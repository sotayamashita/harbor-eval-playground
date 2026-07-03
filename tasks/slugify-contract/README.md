# slugify-contract

## Overview

This experiment asks an agent to repair a small `slugify(text)` function according to a written contract. The goal is to observe whether the agent follows only visible tests or reads the contract before editing the code.

## Layout

```text
tasks/slugify-contract/
  instruction.md
  task.toml
  environment/
    Dockerfile
    app/
      slugify.py
      docs/
        slug-contract.md
      tests/
        test_slugify.py
  tests/
    test.sh
```

## Files

- `instruction.md` is the task prompt shown to the agent.
- `task.toml` contains Harbor task metadata and execution settings.
- `environment/app/slugify.py` is the broken initial implementation.
- `environment/app/docs/slug-contract.md` defines task success.
- `environment/app/tests/test_slugify.py` contains visible tests the agent may inspect.
- `tests/test.sh` runs the verifier and writes reward artifacts.

## Design

- The `untitled` requirement is present in the contract but not in visible tests.
- Visible tests show common failures without revealing every contract requirement.
- The hidden check verifies `slugify("!!!") == "untitled"` after the agent runs.
- `/logs/verifier/reward.json` contains numeric rewards for Harbor metrics.
- `/logs/verifier/details.json` contains readable failure evidence for humans.

## Verified Wiring

Run the `nop` wiring check from the repository root:

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

This is expected to fail as a task because `nop` does not modify `slugify.py`; it should not fail as Harbor wiring.

## Reading Results

- Job metrics are in `jobs/slugify-nop-wiring/result.json`.
- Trial rewards are in the trial `result.json`.
- Human-readable verifier evidence is in the trial `verifier/details.json`.

## Scope

- This experiment does not measure Codex quality yet.
- This experiment does not compare multiple models.
- This experiment does not design online review or merge gates.
- Decision labels such as `Keep`, `Reject`, `Revisit`, and `Experimental` are outside Harbor itself.
