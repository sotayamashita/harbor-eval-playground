# Harbor Eval Playground

## Overview

This repository collects small Harbor experiments for evaluating local coding
agents through reproducible offline eval tasks. The first experiment checks
whether Harbor can run a task, start an agent, execute a verifier, and write
readable job artifacts.

## Prerequisites

- Docker is installed and running.
- `uv` is available.
- Harbor runs via `uv run --with harbor harbor`.
- Codex CLI is installed and authenticated for Codex-agent experiments.
- The local task schema is generated from Harbor `0.17.0`.

## Quick Start

Run the wiring check with the `nop` agent:

```bash
uv run --with harbor harbor run \
  -p tasks/slugify-contract \
  -a nop \
  -m nop \
  -n 1 \
  --job-name slugify-nop-wiring \
  --force-build \
  --yes
```

Expected result:

```text
exceptions: 0
reward: 0.0
visible_tests: 0.0
hidden_contract_check: 0.0
```

## Experiments

- [`slugify-contract`](tasks/slugify-contract/README.md)
  - Status: Wiring verified with `nop`; Codex trial passed with `reward: 1.0`.
  - Purpose: Small Python repair task with visible tests and a hidden contract check.

## Design Notes

- `environment/app/` becomes `/app` inside the task container.
- `tests/test.sh` is copied by Harbor to `/tests/test.sh` and run as the verifier.
- Visible tests are available to the agent; hidden checks live in the verifier.
- Harbor rewards must be numeric; readable failure details go to verifier logs.
- Harbor's Docker build context is the task `environment/` directory.

## Troubleshooting

- If Docker cannot find `app/`, make sure task files live under `environment/app/`.
- If Harbor reports missing rewards, make sure the verifier writes `/logs/verifier/reward.json`.
- If local Docker works but Harbor fails, check Harbor's `environment/` context.

## References

- [Harbor task structure](https://www.harborframework.com/docs/tasks)
- [Harbor task tutorial](https://www.harborframework.com/docs/tasks/task-tutorial)
- [Harbor GitHub repository](https://github.com/harbor-framework/harbor)
