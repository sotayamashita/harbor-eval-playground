"""Harbor verifier for the slugify-contract task.

Runs the visible pytest suite and a hidden contract check, then writes
Harbor-readable reward.json and details.json.
"""

import importlib.util
import json
import subprocess
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path

# Fixed container paths. WORKSPACE mirrors `workdir` in task.toml.
WORKSPACE = Path("/app")
LOG_DIR = Path("/logs/verifier")
REWARD_FILE = LOG_DIR / "reward.json"
DETAILS_FILE = LOG_DIR / "details.json"


@dataclass(frozen=True)
class CheckResult:
    name: str
    passed: bool
    score: float
    details: dict


def run_visible_tests() -> CheckResult:
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_slugify.py"],
        cwd=WORKSPACE,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    passed = completed.returncode == 0
    score = 0.0

    if passed:
        score = 1.0

    return CheckResult(
        name="visible_tests",
        passed=passed,
        score=score,
        details={"passed": passed, "output": completed.stdout},
    )


def load_slugify():
    slugify_path = WORKSPACE / "slugify.py"
    spec = importlib.util.spec_from_file_location("slugify", slugify_path)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {slugify_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module.slugify


def run_hidden_contract_check() -> CheckResult:
    try:
        slugify = load_slugify()

        actual = slugify("!!!")
        expected = "untitled"

        if actual != expected:
            raise AssertionError(
                f"slugify('!!!') should return {expected!r}, got {actual!r}"
            )

        return CheckResult(
            name="hidden_contract_check",
            passed=True,
            score=1.0,
            details={
                "passed": True,
                "case": "slugify('!!!')",
                "expected": expected,
                "actual": actual,
            },
        )

    except Exception:
        return CheckResult(
            name="hidden_contract_check",
            passed=False,
            score=0.0,
            details={
                "passed": False,
                "case": "slugify('!!!')",
                "expected": "untitled",
                "output": traceback.format_exc(),
            },
        )


def write_json(path: Path, data: object) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    checks = [run_visible_tests(), run_hidden_contract_check()]
    passed = all(check.passed for check in checks)

    reward_score = 0.0
    if passed:
        reward_score = 1.0

    reward = {"reward": reward_score}
    for check in checks:
        reward[check.name] = check.score

    if passed:
        reason = "all verifier checks passed"
    else:
        reason = "one or more verifier checks failed"

    check_details = {}
    for check in checks:
        check_details[check.name] = check.details

    details = {
        "passed": passed,
        "reason": reason,
        "checks": check_details,
    }

    write_json(REWARD_FILE, reward)
    write_json(DETAILS_FILE, details)

    if passed:
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
