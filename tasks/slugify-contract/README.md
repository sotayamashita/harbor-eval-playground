# slugify-contract

## Overview

This experiment asks an agent to repair a small `slugify(text)` function
according to a written contract. The goal is to observe whether the agent reads
the contract before editing the code.

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

This is expected to fail as a task because `nop` does not modify `slugify.py`.
It should not fail as Harbor wiring.

## Run With Codex Subscription

Run the Codex-agent trial from the repository root:

```bash
CODEX_AUTH_JSON_PATH=/path/to/.codex/auth.json \
uv run --with harbor harbor run \
  -p tasks/slugify-contract \
  -a codex \
  -m gpt-5.5 \
  --ak reasoning_effort=low \
  -n 1 \
  --job-name slugify-codex-auth-json-gpt55 \
  --force-build \
  --yes
```

Expected result:

```text
exceptions: 0
reward: 1.0
visible_tests: 1.0
hidden_contract_check: 1.0
```

`CODEX_AUTH_JSON_PATH` lets Harbor inject Codex CLI auth into the task
container. Treat `auth.json` as a secret and do not commit it. With a ChatGPT
account, use a subscription-supported model such as `gpt-5.5`;
`gpt-5-codex` may require API-key based access and can fail with an
unsupported-model error.

`--ak reasoning_effort=low` passes a Codex-agent kwarg through Harbor. Harbor
converts it to `codex exec -c model_reasoning_effort=low`. Omit it to use
Harbor's current Codex-agent default.

## Reading Results

- Job metrics are in `jobs/slugify-nop-wiring/result.json`.
- Trial rewards are in the trial `result.json`.
- Human-readable verifier evidence is in the trial `verifier/details.json`.
- Agent behavior evidence is in the trial `agent/trajectory.json`.

`reward: 1.0` means the repaired behavior passed the visible tests and hidden
verifier check. It does not by itself prove that the agent read the contract.
To claim that, inspect the trajectory for an explicit read of
`docs/slug-contract.md`, such as:

```text
sed -n '1,220p' docs/slug-contract.md
```

In the first successful Codex trial, the trajectory showed that command and the
contract output before the code edit. That is evidence that the agent observed
the contract, including the hidden `!!! -> untitled` requirement, before
patching `slugify.py`.

## Scope

- This experiment does not measure Codex quality yet.
- This experiment does not compare multiple models.
- This experiment does not design online review or merge gates.
- `Keep`, `Reject`, `Revisit`, and `Experimental` are outside Harbor itself.
