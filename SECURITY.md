# Security and scientific-use boundaries

## Threat model

This release trusts the local operating-system user, installed Python interpreter,
source files and local filesystem. It does not isolate hostile native code,
protect against a malicious administrator, authenticate a scientist's civil
identity or guarantee source truth. Hash chains and manifests support integrity
checks relative to an independently retained digest.

Inputs are JSON data, not executable expressions. No eval, exec, pickle loading,
shell launching, arbitrary Python plugin, remote model call, subprocess action,
automatic publication or clinical control exists in the runtime package. Runtime
code is separated from release/testing scripts. CSV text fields that could be
spreadsheet formulas are prefixed. JSON output is validated before atomic writes.
Existing complete run directories are never silently reset.

The optional server binds only to 127.0.0.1. It uses an exact Host check, exact
same-Origin check for POST, per-session token, payload limit, fixed routes,
content security policy and bounded computations. It uses a serial standard
library server and is not production infrastructure. A slow local connection may
delay it until the timeout; other same-user applications remain trusted. Do not
bind it to all interfaces, tunnel it, put it behind a public reverse proxy, or use
it as hospital infrastructure. Do not enter real patient data. Browser status
messages do not establish formal safety or completion of external work.

## Reporting a problem

Use the repository's security-reporting channel after the maintainer publishes
this source and enables one. No fictitious security email address is supplied.
For a local copy, preserve the failing JSON, software version, expected behavior
and a minimal reproduction without personal data. Avoid publishing private
records or credentials. This delivered package has not yet been published to a
new remote repository, so it does not claim an active hosted reporting service.

## Scientific boundaries

Only synthetic benchmark records are accepted by that interface. No diagnosis,
prognosis, dose, treatment selection, organ-allocation decision or patient-specific
viability judgment is implemented. These statements describe intended and tested
capability, not a field-of-use amendment to Apache-2.0.

A novel-field form is never labeled empirical confirmation. The program does not
simulate Planck-scale physics, the origin of the universe, evolution of an entire
liver lineage or conscious experience. It provides named mathematical examples
that connect to those book questions without pretending to have solved them.
There is no autonomous model deployment. A ledger's review label is not permission
to act on patients or a replacement for independent professional review.
