# Phase 3 Execution Plan: Selected Instantiation And Object Separation

## Metadata

- Status: refined phase execution plan
- Feature focus: Stage 1 config entrypoint
- PR title: `Stage 1 config entrypoint - Phase 3: Selected instantiation and object separation`
- Branch: `codex/stage-1-selected-instantiation`
- Worktree: `/nas/home/can134/work/weave-worktrees/stage-1-selected-instantiation`
- Phase execution plan path: `docs/roadmap/stage-1/phases/stage-1-selected-instantiation.md`
- Full plan: `docs/roadmap/stage-1/implementation-plan.md`
- Source phase: Phase 3, `stage-1-selected-instantiation`
- Stack predecessor: Phase 2 merged to `develop`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after focused Phase 3 validation, `make validate-pr`, `make test-summary`, PR CI, and workflow metadata updates
- Workflow path: expanded path
- Successor dependency notes: Phase 4 depends on the final selected-instantiation API for docs and examples.
- Plan quality gate: passed in the full implementation plan
- Plan quality gate loop budget: complete before this phase
- Draft pass: completed
- Refine pass: completed in this artifact
- Setup limitations: none; dedicated Phase 3 worktree is clean and based on `develop` after Phase 2 merge metadata.
- Blockers: none for local Phase 3 implementation

## Objective

Add opt-in selected instantiation to `ConfigEntrypoint` so callers can instantiate explicitly selected resolved config values while ordinary composition stays inert by default and object values remain separate from plain-data result exports.

## Full-Plan Context

Phases 1 and 2 established commandless composition, fixed and resolver-selected bases, and commandless result records. Phase 3 extends those result records with optional selected object output. Phase 4 documentation and examples remain out of scope until the API is merged.

## Stack Context

- Root or stacked phase: root phase after Phase 2 merge
- Current predecessor branch or PR: PR #2 merged into `develop`
- Why this base branch is correct: Phase 3 depends on merged commandless result models and base-resolution metadata.
- Retarget/rebase plan after predecessor merge: not needed; predecessor is merged and the branch starts from `origin/develop`.
- Branch cleanup constraints: delete the remote/local Phase 3 branch only after merge and metadata update.

## Source Phase Summary

- Goal: selected trusted object construction without changing composition defaults.
- Required scope: selector normalization, selected dot-path lookup, per-selection calls to existing `instantiate(...)`, object mapping on composition results, and serializable selected-object metadata.
- Required checkpoints: no default instantiation, no full-config instantiation, no automatic target discovery, and no object serialization in `to_dict()`.
- Acceptance criteria: selected targets instantiate only when requested, selected non-target values remain plain values, missing paths use structured diagnostics, and object values are returned separately.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase: `src/weave/api.py` owns `ConfigEntrypoint`, commandless result records, `instantiate(...)`, and plain-data result export.
- Existing tests or harness behavior: Phase 1/2 coverage in `tests/integration/config/test_compose_argv_from_cli.py`, `tests/unit/config/test_base_resolution.py`, `tests/contracts/test_config_composition_inspection_contract.py`, and `tests/test_import.py` should be extended with selected-instantiation tests.
- Import-boundary or dependency constraints: ordinary `import weave` must remain lazy; selected instantiation must not import targets unless selectors are supplied and compose is called.

## In-Scope Work

- Add selected-instantiation constructor state to `ConfigEntrypoint` using explicit selectors.
- Accept selector input as a sequence of dot-path strings keyed by path or a mapping of caller-selected object names to dot paths.
- Normalize selectors into stable plain-data metadata and reject invalid selector shapes.
- Look up selected values from `ComposedConfig.resolved` after composition.
- Call existing `instantiate(...)` once per selected value, passing configured runtime injection.
- Add `objects` to composition results while keeping object values out of `to_dict()`.
- Add structured diagnostics for missing selected paths and invalid selectors.

## Out-of-Scope Work

- Default instantiation, full-config instantiation, target discovery, target-only validation, schema behavior, executor hooks, stores, persistence, workflow execution, or first-party CLI behavior.
- Function-level selected-instantiation helpers beyond what is required by `ConfigEntrypoint`.
- Serializing instantiated Python objects.
- Public docs/example rewrites beyond tests and workflow metadata.

## Assumptions

- Selected values are trusted project config values and can be passed to existing `instantiate(...)`.
- Non-target selected values should follow current `instantiate(...)` behavior and therefore remain plain values.
- Runtime injection is configured once on `ConfigEntrypoint` for selected instantiation.
- Selector mappings preserve caller-selected object keys for result `objects` and metadata.

## Scope Contract

`ConfigEntrypoint` remains inert by default. When configured with explicit selected object selectors, `compose_args(...)` composes first, then looks up each dot path in the resolved config and calls `instantiate(value=..., runtime=...)`. `ConfigArgsCompositionResult.objects` maps selected object keys to Python values. `to_dict()` includes selected-object metadata such as object keys and dot paths but never includes actual object values. `inspect_args(...)` remains inspection-only and does not instantiate objects.

## Design Impact

- Maintainability: keep selected-instantiation coordination in `api.py` around result construction and reuse existing `instantiate(...)` semantics.
- Extensibility: selector metadata can grow deliberately without binding Stage 1 to executors or stores.
- Domain neutrality: selectors are generic dot paths and caller-owned names only.
- Source-tree boundaries: runtime changes stay in `src/weave/api.py`; tests stay in focused config/import/contract suites.

## Future Compatibility

Phase 4 can document selected instantiation with project-owned examples. Future executor, store, workflow, or full-config instantiation work should use a separate design rather than overloading Stage 1 selectors.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Instantiate by default | Stage 1 must preserve inert composition unless selected instantiation is explicitly requested. |
| Instantiate the full config | Full-config instantiation is deferred and has a larger trusted-execution blast radius. |
| Require selected values to be `_target_` mappings | Existing `instantiate(...)` semantics intentionally leave non-target plain values plain. |
| Serialize object values in `to_dict()` | Result exports must stay plain-data friendly and deterministic. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Selector model is limited to dot paths and caller names | Matches the confirmed done bar while avoiding executor/store coupling | Downstream adapters need richer selection semantics |

## Reviewability

- Expected PR size and shape: moderate API/test change focused on result shape and explicit selected-instantiation flow.
- Files and areas to inspect: selector normalization, path lookup diagnostics, object/result separation, no-instantiation default, and runtime injection.
- Scope-control checks: no default/full-config instantiation, no target discovery, no persistence, no docs/example expansion beyond metadata.

## Implementation Steps

1. Add selector normalization records/helpers and structured selected-path diagnostics in `api.py`.
2. Extend commandless composition results with `objects` and selected-object metadata while keeping `to_dict()` plain-data only.
3. Add `ConfigEntrypoint` constructor options for selected object selectors and runtime injection, and instantiate only in `compose_args(...)`.
4. Add focused unit/integration/contract/import tests for selectors, missing paths, runtime injection, non-target selected values, no-import default, and object exclusion.
5. Update workflow metadata and run required validation.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/test_import.py`
- Required assertions or deferral reason: ordinary `import weave` and unselected composition do not import target modules; no extra top-level detailed selected records are exported unless intentionally selected.

### Unit Suite

- Status: required
- Expected paths: selected-instantiation tests in `tests/unit/config/`
- Required assertions or deferral reason: selector normalization, invalid selectors, duplicate keys, selected path lookup, missing path diagnostics, non-target value behavior, and object-exclusion export.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_config_composition_inspection_contract.py` or focused API contract tests
- Required assertions or deferral reason: `objects` are absent from result `to_dict()` and selected-object metadata is serializable.

### Integration Suite

- Status: required
- Expected paths: `tests/integration/config/test_compose_argv_from_cli.py` or a selected-instantiation integration file
- Required assertions or deferral reason: selected target instantiation works with runtime injection and resolver/fixed-base composition remains inert when no selectors are configured.

### E2E Suite

- Status: deferred
- Expected paths: none
- Required assertions or deferral reason: runnable selected-instantiation examples are owned by Phase 4.

### Opt-In Suites

- Status: deferred
- Markers affected: none beyond existing package/unit/contract/integration markers
- Required assertions or deferral reason: no new optional dependency behavior is introduced.

## Risks

- Accidentally constructing targets during inspect or unselected compose.
- Accidentally serializing Python objects in `to_dict()`.
- Losing path context when selected lookup or instantiation fails.

## Validation Commands

Targeted development commands:

```sh
uv run --group dev python -m pytest tests/unit/config/test_selected_instantiation.py
uv run --group dev python -m pytest tests/integration/config/test_compose_selected_instantiation.py
uv run --group dev python -m pytest tests/test_import.py
uv run --group dev python -m pytest tests/contracts/test_config_composition_inspection_contract.py
```

Final PR-preparation commands:

```sh
make validate-pr
make test-summary
```

## Handoff Notes For `weave_phase_executor`

- Safe implementation slices: selector helpers first, result object separation second, entrypoint compose flow third, tests fourth.
- Tests to run with each slice: unit selected-instantiation tests after helper edits, integration tests after compose flow, import/contract tests after result export edits.
- Decisions the executor must not revisit: no default instantiation, no full-config instantiation, no target discovery, no object serialization.
- Conditions that require stopping for the manager: selected instantiation requires serializing objects, importing targets during inspect/unselected compose, or adding executor/store/workflow behavior.

## Refinement And Review Budget Status

- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed in `docs/roadmap/stage-1/phases/stage-1-selected-instantiation.md`
- Final phase execution plan: completed in this artifact
- Implementation summary: pending
- Implementation validation: pending
- Refinement summary: pending
- Blocker-resolution summary: pending
- PR preparation: pending
- Stack maintenance: branch is based on `develop`; no successor branches exist yet.
- Remaining blockers: none
