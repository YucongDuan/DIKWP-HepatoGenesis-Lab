# Source-specific review and concrete advances

## Audit scope

Six repositories were selected for direct relevance: liver literature, liver
workflow, evidence governance, numerical research and energy/history themes.
The review read repository descriptions and the specific source objects listed
below. It did not execute an upstream repository, recursively audit the entire
account, or infer code absence from an archive-only root. Some binary archive
content could not be fetched in the runtime. That limitation is recorded rather
than replaced with conjecture. Git tree and blob hashes identify objects, not
necessarily a branch commit. Date of inspection: 26 September 2026.

## What should be preserved

The preceding projects already establish useful ideas: offline use, explicit
research boundaries, claim-evidence separation, correction and demotion,
permissioned action, comparison against a stronger reference, and reversible
adoption. In particular ASCENT already performs numerical evaluation. A useful
successor must add a new executable problem class rather than pretend that all
previous systems merely organize text.

## 1. YucongDuan/DIKWP-HepatoScholar-OS

**Inspected:** README and recursive root tree. Source: https://github.com/YucongDuan/DIKWP-HepatoScholar-OS/blob/main/README.md

Tree object: `9fe20a90ac47ffe39c6e1749b5ecffd3eb8ae988`. Blob object: `966421268097b8544be5c01fb4468ccce6a6d230`.

**Existing capability.** Research corpus organization, DIKWP literature ledger and gap mining. Runnable distribution is a root ZIP.

**Scoped limitation.** The inspected tree does not expose an installable source root. ZIP internals were not inspected; absence of numerical code inside it is not established.

**Implemented extension.** Flat installable source tree, single-file executable, tests and executable chapter labs.

Upstream runtime tests in this review: **NOT_RUN**.

## 2. YucongDuan/DIKWP-HepatoScholar-Studio-V2

**Inspected:** README, source tree and full analysis CLI. Source: https://github.com/YucongDuan/DIKWP-HepatoScholar-Studio-V2/blob/main/source-distribution/dikwp_hepatoscholar_v2_system_package-2888f5267e/source/cli/hepatoscholar_cli.py

Tree object: `ac7c7303be205937c02301a54dcd15781ee77101`. Blob object: `c67252ea3f4ad8f686137b4b2ed2907841c33275`.

**Existing capability.** closure() subtracts fixed missingness and contradiction penalties from an input quality value. analyze() exports records, roles and seeded claims.

**Scoped limitation.** This inspected numerical score is not calibrated confidence. Nonfinite values are not rejected along the inspected path; isolated NaN expression yields 100. Contradictory evidence is mechanically penalized without assessing study validity.

**Implemented extension.** Strict finite JSON, no truth score, competing executable models, negative controls, a synthetic-record file adapter preserving quality only as an annotation.

Upstream runtime tests in this review: **NOT_RUN**.

## 3. YucongDuan/DIKWP-HepatoCarePath-OS

**Inspected:** README and recursive root tree. Source: https://github.com/YucongDuan/DIKWP-HepatoCarePath-OS/blob/main/README.md

Tree object: `9e19c326671484dd016a06259bcf2121e6c62542`. Blob object: `601171c94db220a3c56914613aed67f47e1a8e26`.

**Existing capability.** Liver workflow, triage routing, preparation and handoff governance; explicitly not diagnosis or prescribing. Source distributed as ZIP.

**Scoped limitation.** Clinical workflow governance is a different problem from a book-based experimental mechanism engine. Archive internals were not inspected.

**Implemented extension.** Separate educational model research from patient workflows; no automated clinical bridge or imported patient records.

Upstream runtime tests in this review: **NOT_RUN**.

## 4. YucongDuan/DIKWP-ASCENT-v0.2.0

**Inspected:** README, module directory and full evaluator.py. Source: https://github.com/YucongDuan/DIKWP-ASCENT-v0.2.0/blob/main/src/dikwp_ascent/evaluator.py

Blob object: `57f9cd466f7df1b2fd27060bd7aa2202dfe9cb68`.

**Existing capability.** Actual numerical evaluation, exact integer-knapsack reference, frozen-model comparisons, per-world nonregression and descriptive paired bootstrap. README documents explicit review and rollback.

**Scoped limitation.** Inspected evaluator handles basis-regression rows and scheduling cases. It is not a history-dependent organ-model evaluator or partial-observation viability solver. Row-level resampling should not be reused blindly for autocorrelated time points.

**Implemented extension.** Equally weighted whole-trajectory losses, train/development/audit separation, mechanism alternatives, finite belief-state game and correction-aware lineage. No claim that ASCENT lacked numerical computation.

Upstream runtime tests in this review: **NOT_RUN**.

## 5. YucongDuan/NEGENESIS-OMEGA

**Inspected:** README and recursive root tree. Source: https://github.com/YucongDuan/NEGENESIS-OMEGA/blob/main/README.md

Tree object: `440cf568f6dc08882752cf1e8446cd6b6a43c06f`. Blob object: `46203875a6ab91b51037725f26d8c6a4c419c956`.

**Existing capability.** Memory, coadaptation and accounting themes; explicit distinction between local order, thermodynamic entropy and moral value. Root ZIP carries distribution.

**Scoped limitation.** README-level conceptual scope cannot establish correctness of a numerical physical implementation; archive internals were not inspected.

**Implemented extension.** Dimensioned finite-volume mass balance, separate energy balance and reaction-direction check, without equating reserve with joules or local order with virtue.

Upstream runtime tests in this review: **NOT_RUN**.

## 6. YucongDuan/DIKWP-ProofLedger-OS

**Inspected:** README only. Source: https://github.com/YucongDuan/DIKWP-ProofLedger-OS/blob/main/README.md



**Existing capability.** Claim-evidence mapping, missing evidence, demotion, correction and reversible review; expressly a local verification scaffold rather than a truth oracle.

**Scoped limitation.** A declared ledger does not by itself show how numerical experiments, source corrections and downstream proposals are connected. Runtime source was not inspected.

**Implemented extension.** Executable SQLite dependency DAG, immutable node versions, typed scopes, recursive correction propagation and externally anchored manifest verification.

Upstream runtime tests in this review: **NOT_RUN**.

## Isolated nonfinite scoring reproduction

The inspected V2 CLI converts a supplied quality value with `float`, subtracts
fixed penalties and clamps with nested `min` and `max`. In the observed Python
semantics, NaN can emerge as a score of 100 along that expression. This was
reproduced as an isolated expression, not by claiming a full installed V2 test.
The included `scripts/reproduce_upstream_edge.py` preserves the result and checks
that this new system rejects nonfinite values. A high annotation is never an
empirical probability in the new ledger.

There is a separate conceptual issue: a study that contradicts a working claim
need not be low quality. Therefore disagreement is retained as a competing
explanation or review condition rather than mechanically penalized as bad
science. This release does not replace one unexplained confidence score with
another. It reports explicit errors, scopes, comparisons and failure cases.

## What is and is not surpassed

The delivered advance is the executable chain from book argument to mechanism,
challenge protocol, observation, counterexample and correction. It is not a
universal performance ranking across unrelated repositories. No head-to-head
clinical study, general intelligence benchmark or full upstream runtime comparison
was carried out. The file adapter is tested against an original synthetic fixture
of the inspected V2 schema; it is not evidence of a live inter-repository API.
Future integration with ASCENT would require a new organ-model task adapter and
reviewed data contract. That integration is not silently claimed as finished.
