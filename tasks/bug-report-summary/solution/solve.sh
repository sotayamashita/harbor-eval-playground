#!/usr/bin/env bash
set -euo pipefail

cat >/app/summary.md <<'EOF'
# Bug Summary

CSV export fails in the Admin Dashboard when filtered User Activity results
include emoji. To reproduce, open Reports > User Activity, set the search filter
to `feedback 😀`, and click Export CSV. The expected behavior is a downloaded CSV
with the filtered rows, but the button stays on `Preparing...` and then shows
`Something went wrong` with no file downloaded. This blocks team admins from
exporting weekly activity reports for feedback containing emoji.
EOF
