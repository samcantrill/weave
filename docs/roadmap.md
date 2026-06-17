# Roadmap

## Completed Baseline

- Establish `weave` as a standalone configuration authoring package.
- Package-local tests and runnable examples.
- Config composition, includes, overlays, replacement, overrides, recipes,
  target instantiation, redaction, provenance, source artifacts, raw source
  snapshots, and artifact-safe fingerprints.
- Project-CLI argv shorthand through `compose_config_from_argv(...)`.

## Near-Term Items

- Add CI for `make validate-pr` and `make test-summary`.
- Add publication documentation when the repository is ready to release.

## Deferred Non-Goals

No first-party CLI executable, Hydra bridge, untrusted config sandboxing, domain
recipe catalog, workflow execution engine, scheduler, run store, or queueing
system is planned for this package.
