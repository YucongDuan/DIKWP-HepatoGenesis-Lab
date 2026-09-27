# DIKWP HepatoGenesis Lab

[English](README.md) · [中文](README.zh-CN.md) · [Quick start](GETTING_STARTED.md) · [Releases](https://github.com/YucongDuan/DIKWP-HepatoGenesis-Lab/releases) · [Project page](https://yucongduan.github.io/DIKWP-HepatoGenesis-Lab/)

[![Tests](https://github.com/YucongDuan/DIKWP-HepatoGenesis-Lab/actions/workflows/tests.yml/badge.svg)](https://github.com/YucongDuan/DIKWP-HepatoGenesis-Lab/actions/workflows/tests.yml)

## Executable histories. Competing explanations. Traceable consequences.

**Version 1.0.0 · English edition · Apache-2.0 · Python 3.10+ · standard library only**

A working software companion to **A Brief History of the Liver**, by **Yucong Duan
and Zhongdao Wu**. It turns selected book arguments into executable experiments:
what history changes, which model a measurement can separate, when state
compression destroys a valid action, and how corrections propagate through a
research argument.

This is an independently written research implementation, not a renamed upstream
project, autonomous physician, clinical digital twin, or discovery of a new
physical field. Existing DIKWP projects are credited and examined in
[the source-specific review](docs/UPSTREAM_REVIEW.md).

## Run without installing packages

From the extracted source directory:

```sh
python -m hepatogenesis doctor
python -m hepatogenesis demo --out my-first-run
python -m hepatogenesis verify my-first-run
python -m hepatogenesis serve --port 8766
```

Open `my-first-run/report.html` for the **offline results viewer**, or open
`http://127.0.0.1:8766` for the **live console**. The console invokes real local
Python calculations; it is not the static report pretending to run a model.
Use a new output directory for each complete run. The demo refuses to erase old
experiments. Closing the server with Ctrl+C stops it.

With the supplied executable archive:

```sh
python dist/DIKWP_HepatoGenesis_Lab.pyz doctor
python dist/DIKWP_HepatoGenesis_Lab.pyz demo --out my-second-run
python dist/DIKWP_HepatoGenesis_Lab.pyz serve --port 8766
```

On Windows, `py -3` may replace `python`. `START_WINDOWS.bat` and `START_UNIX.sh`
start the live console from the source directory. Python must already be
installed. Windows/macOS launchers are provided; execution was checked on Linux
with Python 3.13.5, not on those operating systems.

## What runs

| Research question | Implemented computation | Scope of the result |
|---|---|---|
| Can the same visible present conceal different futures? | Segmented RK4 for dynamic, frozen and erased structural history | Three explicit dimensionless teaching models |
| Which explanation earns use on a declared task? | Fit on training trajectories; freeze selection on development trajectories; evaluate once on audit trajectories | Public synthetic fixture; whole trajectories are units |
| Does more complexity always win? | A zero-history negative control | Simpler erased-history model is selected |
| Can an observer implement one valid policy? | Exact finite belief-state dynamic programming with adversarial successors and a budget | Finite model and conservative cost semantics only |
| Which state compression preserves the task? | Observation-only and constraint-aware bisimulation partitions | Declared states, actions, successors, flags and costs |
| Can physical accounting detect a bad explanation? | Conservative 24-zone transport; mass, energy and reaction-direction ledgers | Explicit units; no reserve-to-joules conversion |
| What should be measured to distinguish models? | Finite maximin model separation per measurement cost | Assumed independent noise; not clinical test selection |
| What happens when a source fails? | Append-only SQLite dependency graph and recursive review propagation | Local integrity and declared scope, not guaranteed truth |

The package also contains an **18-chapter English lab map**, a strict synthetic
HepatoScholar V2 file adapter, finite parameter sensitivity, source identities,
checksummed experiment capsules, a browser console, a standalone HTML report,
unit and HTTP tests, and release validation scripts.

## Reproduce the principal experiments

```sh
python -m hepatogenesis compare --scenario high_history --out alternatives.json
python -m hepatogenesis benchmark --out challenge.json
python -m hepatogenesis benchmark --negative-control --out negative.json
python -m hepatogenesis finite --out hidden-state.json
python -m hepatogenesis physics --out physical-ledgers.json
python -m hepatogenesis design --scenario high_history --out observation-design.json
python -m hepatogenesis import-v2 examples/hepatoscholar_v2_synthetic.json --ledger imported.sqlite --out import-report.json
python -m hepatogenesis chapters
python scripts/run_tests.py
```

For a custom finite model:

```sh
python -m hepatogenesis solve examples/hidden_state_game.json --initial A B --horizon 1 --budget 1 --out policy.json
```

For altered numerical parameters, edit `examples/history_scenario.json` and use
`simulate --config ... --out ...`. JSON values are data, never evaluated as code.

## Read the outcome correctly

The public positive fixture is generated by the dynamic-history equations, so its
success is expected and is not unbiased evidence that nature obeys those equations.
The audit mean squared errors in the release run are approximately 0.000004407,
0.008714183 and 0.082682453 for dynamic, frozen and erased history respectively.
In the negative control the three models coincide and the declared complexity
penalty selects erased history. Adverse and tied results remain visible.

The two hidden states in the finite fixture are individually controllable, but
there is no one feasible action when they are observationally indistinguishable.
An additional observation restores feasibility **in that finite fixture**. This
is an exact result about the supplied transition table, not a treatment policy.

The independent RK4 implementation agrees with the supplied book's SciPy model
at six terminal states to about 5.23e-12 in this environment. Agreement between
implementations of the same equations does not validate those equations against
biology. Full records, rather than rounded claims, are in `validation/`.

## Trust and reproducibility

The core makes no outbound network calls and requires no API key. The local web
server binds only to 127.0.0.1 and checks Host, Origin, a session token, payload
size and fixed work limits. Do not expose it through a proxy or to a network.
It is a bounded teaching server, not a production security boundary.

Capsules include source hashes, parameters, both protocols, raw trajectories,
model results, lineage events and an exact file manifest. A retained hash can
detect tampering; it cannot certify scientific truth or protect against an
administrator who rewrites every copy. No patient records are bundled or accepted
by the synthetic benchmark. No external publication, model deployment or
clinical action is implemented.

## Documentation

- [Architecture, models and guarantees](docs/SCIENCE_AND_ARCHITECTURE.md)
- [Source-specific upstream review](docs/UPSTREAM_REVIEW.md)
- [Command line, Python and local HTTP interfaces](docs/INTERFACES.md)
- [Reproduction and result interpretation](docs/REPRODUCIBILITY.md)
- [Security and scientific-use boundaries](SECURITY.md)
- [Chapter-by-chapter English lab guide](docs/BOOK_LABS.md)
- [Extensions and release procedure](CONTRIBUTING.md)
- `docs/HepatoGenesis_Engineering_Guide_EN.docx`: full English engineering guide

The complete source is maintained in [YucongDuan/DIKWP-HepatoGenesis-Lab](https://github.com/YucongDuan/DIKWP-HepatoGenesis-Lab). See [publication records](PUBLICATION.md) and the linked GitHub Actions runs for revision-specific checks. The license does not license the separately supplied book or third-party projects. See `NOTICE` for attribution and AI-assisted authorship disclosure.

## Explore the companion collection

- [Related companion: NEPHROGENESIS-Lab](https://github.com/YucongDuan/NEPHROGENESIS-Lab)
- [Yucong Duan · DIKWP research portfolio](https://github.com/YucongDuan)
- [All projects and research areas](https://github.com/YucongDuan/YucongDuan/blob/main/REPOSITORY_DIRECTORY.md)
