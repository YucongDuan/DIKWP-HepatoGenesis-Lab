# GitHub publication · 27 September 2026

Version **1.0.0** of [DIKWP HepatoGenesis Lab](https://github.com/YucongDuan/DIKWP-HepatoGenesis-Lab) publishes the supplied source, examples, documentation and packaged distributions as browsable repository files.

- [Quick start](GETTING_STARTED.md) · [English README](README.md) · [中文说明](README.zh-CN.md)
- [Versioned releases](https://github.com/YucongDuan/DIKWP-HepatoGenesis-Lab/releases) · [Project page](https://yucongduan.github.io/DIKWP-HepatoGenesis-Lab/)
- [Hosted workflow results](https://github.com/YucongDuan/DIKWP-HepatoGenesis-Lab/actions/workflows/tests.yml)

## Local validation at publication

The original uploaded archive manifest was checked against the archive bytes before publication changes. **136 tests passed** on Python 3.12.14 / Linux. The [machine-readable record](validation/PUBLICATION_CHECK_2026-09-27.json) identifies the uploaded archive and its SHA-256; [the log](validation/publication_tests.log) records this run. Earlier validation files remain historical records of the original package.

Publication edits add navigation, quick-start instructions, Chinese entry documentation, repository URLs, a static project page and this record. The numerical and finite-model implementations are retained. Publication CI exposed SQLite handles left open after transaction contexts on Windows; the ledger now commits or rolls back and closes each connection deterministically. The two direct-SQL tampering fixtures also close their handles. All 136 local tests were rerun after this fix. Wheels are rebuilt from this publication source; release manifests are regenerated after the reviewed edits.

Hosted workflow results are separate from the local test result. Follow the Actions link to see the operating system, Python version, commit and conclusion of each run.

## Web and local execution

The project page serves a precomputed HTML example report. Parameter-editable calculations use the local Python server. GitHub Pages does not run the Python backend.

## Attribution

Book: *A Brief History of the Liver*, Yucong Duan and Zhongdao Wu. Software citation and component licensing: [CITATION.cff](CITATION.cff), [LICENSE](LICENSE), [NOTICE](NOTICE).

The macOS run also exposed an operating-system ancestor alias (`/var` to `/private/var`) being mistaken for a capsule payload symlink. Verification now canonicalizes the selected root after rejecting a symlinked root or manifest. Three regression tests cover an allowed ancestor alias, a rejected root symlink, and a rejected symlinked payload directory.
