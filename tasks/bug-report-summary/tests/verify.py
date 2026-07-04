"""Harbor verifier for the bug-report-summary task.

Checks that summary.md exists, then uses an LLM judge to evaluate its content.
"""

import json
import os
import traceback
from dataclasses import dataclass
from pathlib import Path

from anthropic import Anthropic, transform_schema
from pydantic import BaseModel, Field

WORKSPACE = Path("/app")
LOG_DIR = Path("/logs/verifier")
REWARD_FILE = LOG_DIR / "reward.json"
DETAILS_FILE = LOG_DIR / "details.json"
JUDGE_FILE = LOG_DIR / "judge_response.json"
SUMMARY_FILE = WORKSPACE / "summary.md"
BUG_REPORT_FILE = WORKSPACE / "bug-report.md"
PASS_THRESHOLD = 0.8


class JudgeResponse(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0)
    reason: str
    missing: list[str] = Field(default_factory=list)


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    score: float
    details: dict


def write_json(path: Path, data: object) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def check_summary_exists() -> CheckResult:
    exists = SUMMARY_FILE.is_file()
    score = 0.0

    if exists:
        score = 1.0

    return CheckResult(
        name="summary_exists",
        passed=exists,
        score=score,
        details={
            "passed": exists,
            "path": str(SUMMARY_FILE),
        },
    )


def build_judge_prompt(bug_report: str, summary: str) -> str:
    return f"""Evaluate whether the summary is useful for bug triage.

Rubric:
- It states the observed behavior.
- It states the expected behavior.
- It includes concrete reproduction steps.
- It states the impact or severity.
- It stays factual and does not invent details.

Score from 0.0 to 1.0.
Use 0.8 or higher only if the summary satisfies all important rubric items.

Bug report:
{bug_report}

Summary:
{summary}
"""


def run_llm_judge() -> CheckResult:
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        model_name = os.getenv("MODEL_NAME", "claude-haiku-4-5")

        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")

        bug_report = BUG_REPORT_FILE.read_text(encoding="utf-8")
        summary = SUMMARY_FILE.read_text(encoding="utf-8")
        schema = transform_schema(JudgeResponse.model_json_schema())
        client = Anthropic(api_key=api_key)

        response = client.messages.create(
            model=model_name,
            max_tokens=1024,
            output_config={"format": {"type": "json_schema", "schema": schema}},
            messages=[
                {
                    "role": "user",
                    "content": build_judge_prompt(bug_report, summary),
                }
            ],
        )

        result = JudgeResponse.model_validate_json(response.content[0].text)
        write_json(JUDGE_FILE, result.model_dump())
        passed = result.score >= PASS_THRESHOLD
        score = 0.0

        if passed:
            score = 1.0

        return CheckResult(
            name="content_judge",
            passed=passed,
            score=score,
            details={
                "passed": passed,
                "score": result.score,
                "threshold": PASS_THRESHOLD,
                "reason": result.reason,
                "missing": result.missing,
                "model": model_name,
            },
        )

    except Exception:
        return CheckResult(
            name="content_judge",
            passed=False,
            score=0.0,
            details={
                "passed": False,
                "score": 0.0,
                "threshold": PASS_THRESHOLD,
                "output": traceback.format_exc(),
            },
        )


def skipped_content_judge(reason: str) -> CheckResult:
    return CheckResult(
        name="content_judge",
        passed=False,
        score=0.0,
        details={
            "passed": False,
            "score": 0.0,
            "threshold": PASS_THRESHOLD,
            "reason": reason,
        },
    )


def build_reward(checks: list[CheckResult], content_score: float) -> dict:
    passed = True
    for check in checks:
        if not check.passed:
            passed = False

    reward_score = 0.0
    if passed:
        reward_score = 1.0

    reward = {
        "reward": reward_score,
        "content_score": content_score,
    }

    for check in checks:
        reward[check.name] = check.score

    return reward


def build_details(checks: list[CheckResult]) -> dict:
    passed = True
    for check in checks:
        if not check.passed:
            passed = False

    if passed:
        reason = "all verifier checks passed"
    else:
        reason = "one or more verifier checks failed"

    check_details = {}
    for check in checks:
        check_details[check.name] = check.details

    return {
        "passed": passed,
        "reason": reason,
        "checks": check_details,
    }


def main() -> int:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    summary_exists = check_summary_exists()
    checks = [summary_exists]
    content_score = 0.0

    if summary_exists.passed:
        content_judge = run_llm_judge()
    else:
        content_judge = skipped_content_judge("summary.md does not exist")

    checks.append(content_judge)
    content_score = content_judge.details.get("score", 0.0)

    reward = build_reward(checks, content_score)
    details = build_details(checks)

    write_json(REWARD_FILE, reward)
    write_json(DETAILS_FILE, details)

    for check in checks:
        if not check.passed:
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
