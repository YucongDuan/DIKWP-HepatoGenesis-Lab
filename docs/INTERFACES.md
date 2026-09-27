# Interfaces and schemas

## Command line

Run all commands from the repository root, or replace `python -m hepatogenesis`
with `python DIKWP_HepatoGenesis_Lab.pyz`. Exit status zero means the requested
computation completed; status two indicates invalid input or a local I/O error.
Completion does not mean a scientific hypothesis passed.

| Command | Inputs | Output |
|---|---|---|
| doctor | None | Python/version/dependency/source identity JSON |
| chapters | None | 18 English chapter objects with exercise and command |
| demo | --out NEWDIR, --samples 0..128 | Complete experiment capsule and report |
| verify | DIRECTORY, optional --manifest-sha256 HASH | File-set and content verification |
| simulate | --scenario NAME or --config JSON; --model MODE; --out JSON | Full numerical trajectory and metrics |
| compare | --scenario or --config; --out JSON | All three mechanism hypotheses |
| design | --scenario or default-parameter config; --out JSON | Candidate measurements and maximin selection |
| benchmark | optional --protocol JSON OR --negative-control; --out JSON | Frozen model selection and audit losses |
| finite | --out JSON | Common-policy and abstraction counterexamples |
| physics | --out JSON | Spatial transport, reaction and energy ledgers |
| information | --out JSON | Binary information/decoder counterexample |
| solve | MODEL.json --initial STATES --horizon N --budget N --out JSON | Exact finite policy result and partition |
| import-v2 | INPUT.json --ledger NEW.sqlite --out JSON | Synthetic V2 record intake report |
| serve | --port PORT | Loopback interactive console; Ctrl+C stops it |

## Numeric scenario JSON

`examples/history_scenario.json` contains `scenario` and optional `parameters`.
The scenario includes a name, initial memory/capacity/reserve, pulse interval and
height, repair interval and multiplier, support and horizon. Unknown keys are
rejected. Defaults are dataclass defaults. There are no expressions, native code,
file references or executable plugins in the contract. JSON rejects duplicate
keys, NaN, infinities, overflowing floating literals and payloads above 2 MB.
Numeric validation rejects booleans even though Python treats bool as a subclass
of int. Model names are a finite allowlist.

## Synthetic benchmark JSON

See `examples/benchmark_protocol.json`. The top level names the generator,
parameters, q grid, complexity penalty, noise assumption and trajectory groups.
Each group has a unique ID, one split, a scenario and strictly increasing C/R
observations. A generating scenario may not cross splits under another name.
The protocol accepts synthetic data only. Relabeling patient records as synthetic
is not an acceptable data-intake workflow and is not prevented by scientific
validation alone. There is no file upload endpoint in the browser.

## Finite transition model

See `examples/hidden_state_game.json`. Required fields are `states`, `actions`,
`observation`, `transitions`, `costs`, `safe` and `goal`. Each enabled action has a
nonempty list of possible successors and a nonnegative integer cost. Missing
actions are disabled, not automatically zero cost. Goal states must be safe.
Transitions are declarative; they cannot call Python functions.

## Python examples

```python
from pathlib import Path
from hepatogenesis.dynamics import Scenario, simulate
from hepatogenesis.finite import hidden_state_fixture, solve_belief
from hepatogenesis.evidence import Ledger

run = simulate(Scenario(name="custom", memory=1.2, horizon=40))
print(run.metrics())
result = solve_belief(hidden_state_fixture(), ["A", "B"], 1, 1)
assert result["feasible"] is False
ledger = Ledger(Path("new_research.sqlite"))
print(ledger.verify())
```

The Python interfaces have the same validation contracts as the CLI. For a field
proposal, call `physics.field_contract(packet)`; an accepted proposal remains a
hypothesis. There is no evaluator of arbitrary symbolic field equations.

## Local HTTP

GET `/` returns the English console and its per-server random token. GET
`/api/catalog` returns the fixed model and scenario catalog. POST `/api/simulate`
accepts `{scenario, model, memory?, repair_multiplier?}` with stricter UI limits.
POST `/api/lab` accepts `{name}` from `finite`, `physics`, `information`,
`benchmark`, `negative_control`, `design`. All POST requests require exact Host,
Origin, JSON content type, one Content-Length, one X-Hepato-Token and a payload
of at most 16,384 bytes. There are no CORS grants, remote controls or path fields.
The browser code performs these calls; a third-party site cannot use its own
Origin with the token interface. Same-user malware is outside the trust boundary.

A synthetic V2 adapter is implemented as a file interface, not an upstream
service call. It follows the inspected scenario/records structure. All records
are prevalidated; imported quality is retained as an uncalibrated annotation.
The CLI requires a new dedicated ledger. API callers importing into a shared
ledger should note that a whole multi-record import is not one database
transaction, although each append is transactional. No live ASCENT, CarePath or
ProofLedger integration is claimed.
