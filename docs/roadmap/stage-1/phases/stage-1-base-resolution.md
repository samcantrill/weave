# Phase 2 Execution Plan: Base Resolution And Config-Arg Policies

## Metadata

- Status: refined phase execution plan
- Feature focus: Stage 1 config entrypoint
- PR title: `Stage 1 config entrypoint - Phase 2: Base resolution and metadata boundaries`
- Branch: `codex/stage-1-base-resolution`
- Worktree: `/nas/home/can134/work/weave-worktrees/stage-1-base-resolution`
- Phase execution plan path: `docs/roadmap/stage-1/phases/stage-1-base-resolution.md`
- Full plan: `docs/roadmap/stage-1/implementation-plan.md`
- Source phase: Phase 2, `stage-1-base-resolution`
- Stack predecessor: Phase 1 merged to `develop`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after focused Phase 2 validation, `make validate-pr`, `make test-summary`, PR CI, and workflow metadata updates
- Workflow path: expanded path
- Successor dependency notes: Phase 3 depends on commandless result models and may combine selected instantiation with resolver metadata in tests.
- Plan quality gate: passed in the full implementation plan
- Plan quality gate loop budget: complete before this phase
- Draft pass: completed
- Refine pass: completed in this artifact
- Setup limitations: none; dedicated Phase 2 worktree is clean and based on `develop`.
- Blockers: none for local Phase 2 implementation

## Objective

Add project-owned base resolution to `ConfigEntrypoint` by introducing generic request/resolution records, validating fixed-path versus resolver strategies, invoking the resolver during compose/inspect calls, and serializing only explicit plain-data resolver details.

## Full-Plan Context

Phase 1 established commandless parsing and fixed-base helpers. Phase 2 extends only the configured entrypoint object with a generic base resolver strategy. Preferred function helpers remain fixed-base. Phase 3 selected instantiation and Phase 4 docs/example hardening remain out of scope.

## Stack Context

- Root or stacked phase: root phase after Phase 1 merge
- Current predecessor branch or PR: PR #1 merged into `develop`
- Why this base branch is correct: Phase 2 depends on merged Phase 1 commandless contracts.
- Retarget/rebase plan after predecessor merge: not needed; predecessor is merged.
- Branch cleanup constraints: delete the remote/local Phase 2 branch only after merge and metadata update.

## Source Phase Summary

- Goal: add project-owned base resolution without command semantics or config search behavior.
- Required scope: `ConfigBaseRequest`, `ConfigBaseResolution`, resolver constructor support, resolver invocation, result metadata for explicit details, invalid strategy/return diagnostics.
- Required checkpoints: no command-specific resolver input, no global search, no project-root discovery, no serialization of `base_context`.
- Acceptance criteria: resolver-selected base composes/inspects exactly like fixed base, and `base_context` never appears in `to_dict()` output unless represented by explicit resolver `details`.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase: `src/weave/api.py` owns `ConfigEntrypoint`, commandless result records, helper routing, and result `to_dict()` metadata.
- Existing tests or harness behavior: Phase 1 coverage in `tests/integration/config/test_compose_argv_from_cli.py`, `tests/unit/config/test_argv.py`, `tests/contracts/test_config_composition_inspection_contract.py`, and `tests/test_import.py` should be extended with resolver-specific tests.
- Import-boundary or dependency constraints: `import weave` must stay lazy; resolver records should be exported from `weave.api`, not top-level `weave`, in this phase.

## In-Scope Work

- Add `ConfigBaseRequest(base_context=...)` and `ConfigBaseResolution(base_config_path=..., details=...)` in `weave.api`.
- Add `base_resolver` and `base_context` support to `ConfigEntrypoint` while allowing exactly one base strategy: fixed path or resolver.
- Resolve the base path during `compose_args(...)` and `inspect_args(...)` before calling commandless helpers.
- Add `base_details` metadata to commandless result records, serialized only when resolver details are explicitly returned and validated as plain-data mappings.
- Add structured diagnostics for missing strategy, conflicting strategy, invalid resolver return, invalid details, and resolver exceptions only as needed to preserve context.

## Out-of-Scope Work

- Function-level resolver helpers.
- Command-specific resolver input, command choices, parser framework state, global config search, project-root discovery, default config names, include resolver hooks, selected instantiation, or object persistence.
- Serializing opaque `base_context`.
- Public docs/example rewrite beyond tests and workflow metadata.

## Assumptions

- Resolver is a trusted project callback and can raise normal exceptions; Weave validates its returned object but does not sandbox execution.
- `base_context` is opaque caller input and may be any object.
- Resolver `details` must be absent/`None` or a plain-data mapping.

## Scope Contract

`ConfigEntrypoint` accepts either `base_config_path=...` or `base_resolver=...`, never both and never neither. During `compose_args(...)` and `inspect_args(...)`, a resolver receives `ConfigBaseRequest(base_context=...)` and must return `ConfigBaseResolution`. Commandless result objects expose `base_details` as a tuple of resolver detail mappings or an empty tuple, and `to_dict()` serializes `base_details`; it never serializes `base_context`.

## Design Impact

- Maintainability: keep resolver policy contained in `ConfigEntrypoint`, not the parser or composition internals.
- Extensibility: typed request/resolution records leave room for later adapter policies without adding command semantics.
- Domain neutrality: records use generic base/context/details names only.
- Source-tree boundaries: runtime changes stay in `src/weave/api.py`; tests stay in focused config/import/contract suites.

## Future Compatibility

Phase 3 can add selected instantiation to composition results without changing resolver request shape. Phase 4 can document resolver adapters with neutral examples. Future command semantics, if ever needed, should use a separate design rather than overloading `base_context`.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Resolver receives command or argv state | Stage 1 explicitly rejects command semantics. |
| Resolver returns arbitrary metadata objects | Result exports must stay plain-data friendly and deterministic. |
| Add global search/default base names | Out of Phase 2 scope and would create project policy in Weave. |
| Add function-level resolver helpers now | Phase 2 only requires resolver support on the configured entrypoint object. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Result `base_details` is generic and minimal | Satisfies Stage 1 metadata boundary without designing a broader base-source model | Downstream adapters need multiple named resolver strategies or richer base metadata |

## Reviewability

- Expected PR size and shape: small-to-moderate API/test change focused on `api.py`, resolver tests, and metadata artifacts.
- Files and areas to inspect: strategy validation, resolver invocation, result `to_dict()` shape, import surface, error context.
- Scope-control checks: no command input, no search paths, no selected instantiation, no serialization of arbitrary context.

## Implementation Steps

1. Add base request/resolution records and resolver type handling in `api.py`.
2. Extend commandless result records with validated `base_details` metadata.
3. Add resolver strategy support to `ConfigEntrypoint` compose/inspect flow.
4. Add focused unit/integration/contract/import tests for resolver success, failures, serialization boundaries, and fixed-path parity.
5. Update workflow metadata and run required validation.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/test_import.py`
- Required assertions or deferral reason: `ConfigBaseRequest` and `ConfigBaseResolution` are available from `weave.api` but not top-level `weave`; lazy exports remain unchanged for resolver records.

### Unit Suite

- Status: required
- Expected paths: resolver-focused tests in `tests/unit/config/`
- Required assertions or deferral reason: request/resolution validation, strategy validation, invalid resolver returns, invalid details, and base-context opacity.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_config_composition_inspection_contract.py` or focused API contract tests
- Required assertions or deferral reason: resolver details serialize only when explicit and plain-data; `base_context` is absent from result payloads.

### Integration Suite

- Status: required
- Expected paths: `tests/integration/config/test_compose_argv_from_cli.py` or resolver-specific integration file
- Required assertions or deferral reason: resolver-selected base composes and inspects with config args, warnings, and fixed-path parity.

### E2E Suite

- Status: deferred
- Expected paths: none
- Required assertions or deferral reason: no first-party executable or external workflow is added.

### Opt-In Suites

- Status: deferred
- Markers affected: none beyond existing contract marker use
- Required assertions or deferral reason: no new optional dependency behavior is introduced.

## Risks

- Accidentally serializing opaque `base_context`.
- Letting resolver support become a search path or command adapter API.
- Adding resolver metadata to artifacts rather than helper-local result metadata.

## Validation Commands

Targeted development commands:

```sh
uv run --group dev python -m pytest tests/unit/config/test_base_resolution.py
uv run --group dev python -m pytest tests/integration/config/test_compose_argv_from_cli.py
uv run --group dev python -m pytest tests/test_import.py
uv run --group dev python -m pytest tests/contracts/test_config_composition_inspection_contract.py
```

Final PR-preparation commands:

```sh
make validate-pr
make test-summary
```

## Handoff Notes For `weave_phase_executor`

- Safe implementation slices: records/results first, entrypoint resolver flow second, tests third.
- Tests to run with each slice: unit resolver tests after record/validation edits, integration tests after entrypoint flow, import/contract tests after export/result shape edits.
- Decisions the executor must not revisit: no command context, no global search, no function-level resolver helper, no selected instantiation.
- Conditions that require stopping for the manager: resolver support requires serializing arbitrary `base_context`, preserving command semantics, or adding project search policy.

## Refinement And Review Budget Status

- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed in `docs/roadmap/stage-1/phases/stage-1-base-resolution.md`
- Final phase execution plan: completed in this artifact
- Implementation summary: pending
- Implementation validation: pending
- Refinement summary: pending
- Blocker-resolution summary: pending
- PR preparation: pending
- Stack maintenance: pending
- Remaining blockers: none
