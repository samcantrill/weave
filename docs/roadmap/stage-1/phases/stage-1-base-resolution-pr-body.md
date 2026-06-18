## Summary

Implements Stage 1 Phase 2 base resolution for `ConfigEntrypoint`. Projects can now provide either a fixed `base_config_path` or a generic `base_resolver` callback that receives `ConfigBaseRequest(base_context=...)` and returns `ConfigBaseResolution(base_config_path=..., details=...)`.

The resolver contract stays commandless and domain-neutral: no command tokens, argv parser state, project-root search, global config discovery, or opaque `base_context` serialization is added. Explicit resolver `details` are validated as plain data and exposed only through commandless result metadata.

## Acceptance Criteria

- [x] `ConfigEntrypoint` accepts exactly one base strategy: fixed path or resolver.
- [x] Resolver-selected bases compose and inspect through the existing commandless config-args path.
- [x] `ConfigBaseRequest` and `ConfigBaseResolution` are available from `weave.api` without widening top-level `weave` exports.
- [x] `base_context` remains opaque input and is absent from `to_dict()` payloads unless a project explicitly mirrors values in resolver `details`.
- [x] No command-specific resolver input, global search, project-root discovery, selected instantiation, store, scheduler, workflow, or schema behavior was added.

## Implementation Notes

`ConfigEntrypoint` now validates base strategy selection at construction. Fixed-base entrypoints keep the Phase 1 behavior; resolver entrypoints invoke the callback during `compose_args(...)` and `inspect_args(...)`, then route the selected path through `inspect_config_args(...)`.

`ConfigArgsCompositionResult` and `ConfigArgsInspectionResult` now carry `base_details`, serialized as a list in `to_dict()`. Fixed-base helpers and resolver calls without details serialize this as an empty list. The older command-bearing `ConfigArgv*` records were left unchanged.

New tests implemented:

- Unit coverage for request/resolution validation, strategy errors, invalid resolver returns, non-callable resolvers, and opaque context delivery.
- Integration coverage for fixed-base empty details, resolver-selected base composition and inspection, and absence of opaque context in result payloads.
- Contract coverage proving resolver details are helper result metadata, not normal composition artifacts.
- Package import coverage for detailed API exports without top-level export expansion.

## Tests And Validation

| Check | Result | Evidence |
| --- | --- | --- |
| `make validate-pr` | PASS | Ruff, pyright, package, unit, contract, integration, examples, and build all completed successfully. |
| `make test-summary` | PASS | Refreshed `build/test-summary.md`. |
| GitHub checks | Pending | To run after PR opens. |

### Test Suite Summary

| Suite | Status | Duration | Counts |
| --- | --- | ---: | --- |
| `package` | PASS | 1.3s | 28 passed, 820 deselected |
| `unit` | PASS | 1.0s | 285 passed |
| `contract` | PASS | 0.7s | 32 passed |
| `integration` | PASS | 1.0s | 93 passed |
| `examples` | PASS | 2.9s | 9 passed |

## Risks / Follow-Ups

- Phase 3 still owns selected instantiation and object/result separation.
- Phase 4 still owns final docs and example hardening for resolver adapters.
