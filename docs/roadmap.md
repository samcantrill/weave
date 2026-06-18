# Roadmap

## Completed Baseline

- Establish `weave` as a standalone configuration authoring package.
- Package-local tests, CI, and runnable examples.
- Config composition, includes, overlays, replacement, overrides, recipes,
  target instantiation, redaction, provenance, source artifacts, raw source
  snapshots, and artifact-safe fingerprints.
- Project-owned config-arg adapters through `ConfigEntrypoint` and
  `compose_config_from_args(...)`, including generic base resolution and
  selected-object instantiation.
- Retained argv helper names with commandless behavior and migration diagnostics
  for old command-first invocation shapes.

## Near-Term Items

- Add publication documentation when the repository is ready to release.
- Use Stage 2 planning to decide whether richer docs or migration guides are
  needed for downstream adopters.

## Deferred Non-Goals

No first-party CLI executable, command semantics, implicit `sys.argv` parsing,
Hydra bridge, untrusted config sandboxing, domain recipe catalog, workflow
execution engine, scheduler, run store, or queueing system is planned for this
package.
