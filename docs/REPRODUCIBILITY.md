# Reproduction and verification

## Three different forms of agreement

1. **Same program and runtime.** Two fresh demo directories should contain
identical payloads, including the SQLite demonstration ledger. Their complete
manifest can be compared. This release was actually run twice with 24 sensitivity
samples; all 23 payload file digests agreed.
2. **Different numerical implementation.** The new fixed-step RK4 was compared
with the supplied book's SciPy adaptive implementation on six scenarios and 200
vector-field inputs. `validation/book_crosscheck.json` records endpoint and
clearance differences and the supplied source digest. The book's program is not
relicensed or redistributed in this software source.
3. **Independent scientific data.** Neither of the above is a comparison against
independent wet-lab or clinical observations. That form of validation is absent.

## Run the complete bundle

```sh
python -m hepatogenesis demo --out experiment-001 --samples 24
python -m hepatogenesis verify experiment-001
python -m hepatogenesis demo --out experiment-002 --samples 24
```

Compare the two `manifest.json` files using any text comparison tool. On another
Python version, platform or floating-point implementation, recomputation can
produce slightly different low-order values. Compare numerical tolerances and
full environment metadata; do not promise bitwise portability across platforms.
No timestamp is mixed into the scientific run identity. Source identity includes
runtime modules and embedded assets, so changing the UI also changes that identity.

A capsule contains trajectories, both declared protocols, numerical summaries,
finite model outcomes, physical ledgers, measurement designs, sensitivity rows,
lineage events and database, runtime/source records and an offline report. It is
first written to a temporary directory and moved into a previously absent output
path. The manifest specifies the exact expected file set. Extra, missing,
modified and symlinked payloads are rejected. Keep a manifest digest outside the
bundle to detect an attacker who edits both a payload and its manifest.

## Reproduce tests and releases

```sh
python scripts/run_tests.py
python scripts/reproduce_upstream_edge.py
python scripts/build_zipapp.py --out dist/DIKWP_HepatoGenesis_Lab.pyz
python dist/DIKWP_HepatoGenesis_Lab.pyz doctor
python dist/DIKWP_HepatoGenesis_Lab.pyz demo --out zipapp-run --samples 0
python dist/DIKWP_HepatoGenesis_Lab.pyz verify zipapp-run
```

The test report states actual test count, failures, errors, skips, Python and
platform. A prepared GitHub Actions file is not a completed GitHub Actions run.
The Windows and macOS entries remain unexecuted until that workflow is run.
The archive uses an ordinary Python zip application. It includes the package and
its assets, not a private Python interpreter. Python 3.10 or newer must exist on
the destination machine. A wheel is also supplied for ordinary installation.

## Interpreting the release numbers

The positive synthetic fixture gives the dynamic model an audit MSE about
4.4071e-6, frozen history about 8.7142e-3 and erased history about 8.2682e-2. The
negative control gives all three approximately 4.4071e-6 and chooses erased history
with the predeclared penalty. These differences demonstrate code behavior under
a known generator, not superior diagnosis. The training/development/audit counts
are 3/2/3 complete trajectories. Times within a trajectory are correlated and are
not called independent replicates.

The 24-cell mass ledger closes within about 2.03e-13 mmol in the release run.
This is a discrete bookkeeping residual. It does not bound anatomical modeling
error. The finite hidden-state result is exact for its finite table and cost
semantics; the sampled continuous path check is not exact. Separating these
claims is part of the research design.

The release source includes no external calls that silently fetch newer data.
A later citation correction or data update must create a new immutable evidence
version, invalidate affected descendants, rerun experiments and preserve the old
capsule. Never overwrite an unfavorable experiment solely because its result is
inconvenient. The zero-sensitivity mode emits a header-only CSV, not old samples.
