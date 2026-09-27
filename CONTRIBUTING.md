# Contributing and extending the research kernel

## Preserve a falsifiable change

Start with an issue stating the exact question, current failing example, affected
units and scope, and a proposed discriminating test. A new mechanism should add
an explicit model implementation, a reference or analytic test where available,
a negative control, a declared fitting/selection protocol and a limitation card.
Do not accept a new model merely because its README says it is more intelligent.

Keep test and audit trajectories out of parameter fitting. Use group IDs for
independent experimental units. If moving beyond the supplied synthetic protocol,
create a new reviewed intake contract with provenance, consent, population,
measurement units, missing-data policy and outcome definitions. Do not simply
change the data-kind label to bypass safeguards. Clinical validation, deployment
and human-subject work require processes this software does not provide.

## Interfaces to extend

A fourth dynamic mechanism can be added as a named, reviewed source change to
`dynamics.py`, with output dimensions and explicit assumptions. No uploaded code
execution is supported. To vary observation noise or parameter uncertainty, extend
`experiments.py` and preserve the fixed protocol before audit. To bridge scales,
introduce dimensioned ports and a conservation or approximation test; do not
silently map dimensionless reserve into joules.

For a new field proposal, write a contract identifying degrees of freedom, units,
equation, coupling, independently measurable quantity, null model, distinct
prediction and failure condition. An implemented numerical extension must still
be compared against its null. A successful form validator is not acceptance of
new physics. For finite games, document changes to observation timing, disturbance
semantics and budget accounting before claiming a stronger guarantee.

## Source and publication workflow

Run `python scripts/run_tests.py`, regenerate a new experiment capsule and record
both favorable and unfavorable comparisons. Run the executable archive as well
as source. Check the English interface and report. Review licensing and attribution
before including upstream material. This distribution contains no upstream source.

The root is ready for Git: `git init`, inspect `git status`, add source and intended
documentation, then commit. A maintainer can create a remote repository and push
only after reviewing its contents. No remote URL is invented here and no push is
performed by the delivered application. Do not commit patient records, access
tokens, local ledgers from private work, Python caches or virtual environments.

Prepared CI covers Python 3.10 and 3.13 on Linux plus 3.13 on Windows/macOS. Those
jobs are plans encoded as a workflow, not evidence of completed runs. The local
release audit states the operating system actually exercised. Version changes
must retain old capsules and updated source identities. Semantic or numerical
changes warrant a new version, not editing an old validation record in place.
