#!/usr/bin/env bash

# Convert verifier checks into Harbor-readable numeric rewards and readable logs.
set -u

WORKSPACE_DIR="${WORKSPACE_DIR:-/app}"
VERIFIER_LOG_DIR="${VERIFIER_LOG_DIR:-/logs/verifier}"
REWARD_FILE="$VERIFIER_LOG_DIR/reward.json"
DETAILS_FILE="$VERIFIER_LOG_DIR/details.json"

mkdir -p "$VERIFIER_LOG_DIR"

VISIBLE_OUTPUT_FILE="$(mktemp)"
HIDDEN_OUTPUT_FILE="$(mktemp)"
trap 'rm -f "$VISIBLE_OUTPUT_FILE" "$HIDDEN_OUTPUT_FILE"' EXIT

cd "$WORKSPACE_DIR" || exit

python -m pytest tests/test_slugify.py >"$VISIBLE_OUTPUT_FILE" 2>&1
VISIBLE_STATUS=$?

python - >"$HIDDEN_OUTPUT_FILE" 2>&1 <<'PY'
from slugify import slugify

actual = slugify("!!!")
expected = "untitled"

if actual != expected:
    raise AssertionError(
        f"slugify('!!!') should return {expected!r}, got {actual!r}"
    )
PY
HIDDEN_STATUS=$?

if [ "$VISIBLE_STATUS" -eq 0 ] && [ "$HIDDEN_STATUS" -eq 0 ]; then
    python - "$REWARD_FILE" "$DETAILS_FILE" <<'PY'
import json
import sys

reward_file = sys.argv[1]
details_file = sys.argv[2]

reward = {
    "reward": 1.0,
    "visible_tests": 1.0,
    "hidden_contract_check": 1.0,
}
details = {
    "passed": True,
    "reason": "visible tests and hidden contract check passed",
}

with open(reward_file, "w", encoding="utf-8") as f:
    json.dump(reward, f, ensure_ascii=False, indent=2)
    f.write("\n")

with open(details_file, "w", encoding="utf-8") as f:
    json.dump(details, f, ensure_ascii=False, indent=2)
    f.write("\n")
PY
    exit 0
fi

python - "$REWARD_FILE" "$DETAILS_FILE" "$VISIBLE_OUTPUT_FILE" "$HIDDEN_OUTPUT_FILE" "$VISIBLE_STATUS" "$HIDDEN_STATUS" <<'PY'
import json
import sys

reward_file = sys.argv[1]
details_file = sys.argv[2]
visible_output_file = sys.argv[3]
hidden_output_file = sys.argv[4]
visible_status = int(sys.argv[5])
hidden_status = int(sys.argv[6])

with open(visible_output_file, encoding="utf-8") as f:
    visible_output = f.read()

with open(hidden_output_file, encoding="utf-8") as f:
    hidden_output = f.read()

reward = {
    "reward": 0.0,
    "visible_tests": 1.0 if visible_status == 0 else 0.0,
    "hidden_contract_check": 1.0 if hidden_status == 0 else 0.0,
}
details = {
    "passed": False,
    "reason": "visible tests or hidden contract check failed",
    "checks": {
        "visible_tests": {
            "passed": visible_status == 0,
            "output": visible_output,
        },
        "hidden_contract_check": {
            "passed": hidden_status == 0,
            "case": "slugify('!!!')",
            "expected": "untitled",
            "output": hidden_output,
        },
    },
}

with open(reward_file, "w", encoding="utf-8") as f:
    json.dump(reward, f, ensure_ascii=False, indent=2)
    f.write("\n")

with open(details_file, "w", encoding="utf-8") as f:
    json.dump(details, f, ensure_ascii=False, indent=2)
    f.write("\n")
PY

exit 1
