## Summary

Implements Stage 1 Phase 1 commandless config contracts. This adds a fixed-base `ConfigEntrypoint`, preferred `compose_config_from_args(...)` and `inspect_config_args(...)` helpers, commandless parse/result records, lazy top-level exports, and retained argv-helper migration diagnostics for old command-first invocation shapes.

The implementation preserves existing composition behavior for value overrides, scoped overlays, helper-local warnings, raw source snapshot opt-in, and artifact-safe defaults while avoiding resolver callbacks, selected instantiation, implicit `sys.argv`, and first-party CLI behavior.

## Acceptance Criteria

- [x] Fixed-base `ConfigEntrypoint.compose_args(...)` and `inspect_args(...)` work with explicit config args and no command token.
- [x] Commandless result payloads use distinct records and omit command fields.
- [x] Retained argv helpers no longer preserve command-first semantics and raise targeted migration diagnostics.
- [x] Lazy top-level exports include only `ConfigEntrypoint`, `compose_config_from_args(...)`, and `inspect_config_args(...)` from the new surface.
- [x] No resolver, selected-instantiation, first-party CLI, workflow, store, scheduler, schema, or domain-specific behavior was added.

## Implementation Notes

Commandless parsing lives beside the legacy internal argv parser and reuses existing value override and scoped-overlay mechanics without exposing command metadata. Public commandless results serialize `parsed_args`, `base_config_path`, overrides, scoped overlays, unparsed args, warnings, and composed/inspection data, with no `command`, `parsed_argv`, or `objects` fields.

The retained `compose_config_from_argv(...)` and `inspect_config_from_argv(...)` now require explicit argv input, route base-first sequences to the commandless contract, and reject old `<command> <base-config> ...` shapes with structured migration diagnostics.

New tests implemented:

- Unit coverage for commandless token parsing, errors, scoped overlays, and unparsed args.
- Integration coverage for fixed-base composition, `ConfigEntrypoint`, retained-helper routing, warnings, raw snapshots, and migration diagnostics.
- Contract coverage for result shape and structured error context.
- Package import coverage for lazy top-level export policy.

## Tests And Validation

| Check | Result | Evidence |
| --- | --- | --- |
| `make validate-pr` | PASS | Ruff, pyright, package, unit, contract, integration, examples, and build all completed successfully. |
| `make test-summary` | PASS | Refreshed `build/test-summary.md`. |
| GitHub checks | Pending | To be populated after PR creation. |

### Test Suite Summary

| Suite | Status | Duration | Counts |
| --- | --- | ---: | --- |
| `package` | PASS | 1.1s | 28 passed, 800 deselected |
| `unit` | PASS | 0.9s | 278 passed |
| `contract` | PASS | 0.7s | 31 passed |
| `integration` | PASS | 1.0s | 91 passed |
| `examples` | PASS | 2.7s | 9 passed |

## Risks / Follow-Ups

- Phase 2 still owns generic base resolver support.
- Phase 3 still owns selected instantiation and object/result separation.
- Phase 4 should complete the public docs and examples migration from command-first wording to the new commandless adapter pattern.
