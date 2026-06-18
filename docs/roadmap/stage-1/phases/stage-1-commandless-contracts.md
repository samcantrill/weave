# Phase 1 Execution Plan: Commandless Public Contracts

## Metadata

- Status: implemented; initial validation passed
- Feature focus: Stage 1 config entrypoint
- PR title: `Stage 1 config entrypoint - Phase 1: Commandless public contracts`
- Branch: `codex/stage-1-commandless-contracts`
- Worktree: `/nas/home/can134/work/weave-worktrees/stage-1-commandless-contracts`
- Phase execution plan path: `docs/roadmap/stage-1/phases/stage-1-commandless-contracts.md`
- Full plan: `docs/roadmap/stage-1/implementation-plan.md`
- Source phase: Phase 1, `stage-1-commandless-contracts`
- Stack predecessor: none
- Base branch: `develop` in the stage plan; local fallback is `main`
- Target branch: `develop` in the stage plan; local fallback is `main`
- Merge eligibility: eligible after focused validation and final PR checks pass, with target branch corrected if `develop` becomes available
- Workflow path: expanded path
- Successor dependency notes: Phase 2 depends on this commandless contract and result shape.
- Plan quality gate: passed in the full implementation plan
- Plan quality gate loop budget: complete before this phase
- Draft pass: completed
- Refine pass: completed in this artifact
- Setup limitations: remote fetch via HTTPS showed only `origin/main`; no `develop` ref is available in this checkout. The current working tree also contains uncommitted roadmap planning artifacts, so implementation proceeds against the available local base while preserving those changes.
- Blockers: none for local Phase 1 implementation; remote PR targeting still needs a valid target branch.

## Objective

Implement the Phase 1 commandless config-args contract: a fixed-base `ConfigEntrypoint`, preferred commandless helper functions, commandless parse/result records without command metadata, and retained argv-helper migration diagnostics.

## Full-Plan Context

This phase replaces the current command-first helper surface with explicit config args while keeping composition, provenance, recipe expansion, helper-local warnings, and raw snapshot behavior intact. Phase 2 owns generic base resolution, Phase 3 owns selected instantiation, and Phase 4 owns public docs/examples, so this phase must not add resolver callbacks, object construction, first-party CLI behavior, or documentation rewrites beyond minimal inline API clarity.

## Stack Context

- Root or stacked phase: root phase
- Current predecessor branch or PR: none
- Why this base branch is correct: Phase 1 is the first implementation phase. The plan names `develop`, but the local and remote refs available in this checkout expose only `main`.
- Retarget/rebase plan after predecessor merge: if `develop` appears before PR creation, rebase or retarget the phase branch to `develop`; otherwise document `main` as the local target limitation.
- Branch cleanup constraints: do not delete or overwrite uncommitted planning artifacts in the original checkout.

## Source Phase Summary

- Goal: establish commandless Stage 1 public contracts and fixed-base compose/inspect behavior.
- Required scope: commandless parser record, `ConfigEntrypoint`, `compose_config_from_args(...)`, `inspect_config_args(...)`, result records, lazy top-level exports, migration diagnostics for old command-first helper shapes.
- Required checkpoints: no implicit `sys.argv`, no command result fields, no resolver callbacks, no selected instantiation, no new runtime dependencies.
- Acceptance criteria: explicit config args compose/inspect against a fixed base; result `to_dict()` omits command fields; retained argv helpers do not preserve command-first semantics.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase: `src/weave/_argv.py` contains command-first parsing and scoped overlay resolution; `src/weave/api.py` contains command-bearing argv result records and helper-local warnings; `src/weave/__init__.py` owns lazy top-level exports.
- Existing tests or harness behavior: `tests/unit/config/test_argv.py`, `tests/integration/config/test_compose_argv_from_cli.py`, `tests/contracts/test_config_composition_inspection_contract.py`, and `tests/test_import.py` cover the current command-first shape and need focused commandless additions or replacements.
- Import-boundary or dependency constraints: `import weave` must stay lightweight, and all heavy composition imports should remain inside API helper bodies.

## In-Scope Work

- Add `ParsedConfigArgs`, `ConfigArgsCompositionResult`, and `ConfigArgsInspectionResult`.
- Add commandless config-args parsing for value overrides, scoped overlays, and allowed passthrough args.
- Add fixed-base `ConfigEntrypoint.compose_args(...)` and `ConfigEntrypoint.inspect_args(...)`.
- Add `compose_config_from_args(...)` and `inspect_config_args(...)`.
- Convert retained argv helpers to explicit commandless routing or targeted migration diagnostics.
- Update narrow lazy exports for the new preferred top-level helpers and object.

## Out-of-Scope Work

- Base resolver callbacks or resolver result metadata.
- Selected or full-config instantiation.
- Implicit `sys.argv` defaults.
- First-party CLI, project-root discovery, global config search, stores, schedulers, workflows, schemas, or domain examples.
- Public docs and examples beyond minimal test-facing updates.

## Assumptions

- Existing `ArgvValueOverride`, `ArgvScopedOverlay`, and `ArgvUnparsedArg` can remain internal token records for this phase as long as public commandless result records and exports do not expose command-bearing metadata.
- The private argv-scoped overlay composition helper remains the safest way to preserve Stage 0 composition order.
- Retained argv helpers can keep their old parameter names for compatibility while rejecting unsupported command semantics.

## Scope Contract

`ConfigEntrypoint` accepts exactly a fixed `base_config_path` in Phase 1 plus optional `recipe_catalog`, `allow_unparsed`, and `include_raw_source_snapshots` policy. `compose_args(config_args=())` and `inspect_args(config_args=())` require explicit config args and never inspect process argv. Commandless result `to_dict()` payloads include `base_config_path`, `parsed_args`, `value_overrides`, `scoped_overlays`, `unparsed_args`, `warnings`, and the composed or inspection payload; they must not include `command`, `command_choices`, or `parsed_argv`.

## Design Impact

- Maintainability: centralize commandless parsing around existing token classification and composition helpers to avoid a second composition path.
- Extensibility: leave resolver and selected-instantiation extension points to later phases.
- Domain neutrality: keep examples and tests generic config keys and neutral target names.
- Source-tree boundaries: runtime code stays in `src/weave/`; tests stay in focused config and import suites.

## Future Compatibility

Phase 2 can add base resolver strategy selection around `ConfigEntrypoint` without changing Phase 1 commandless parse records. Phase 3 can add an `objects` field to composition results while keeping plain-data exports free of Python objects. Phase 4 can rewrite docs/examples against the preferred helpers introduced here.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Preserve command-first helper behavior in old helpers | The approved Stage 1 plan explicitly rejects command semantics. |
| Reuse `ParsedConfigArgv` in new results | It carries a command field and would make command absence ambiguous. |
| Add resolver support now | Phase 2 owns base resolution and metadata boundaries. |
| Instantiate selected values now | Phase 3 owns object construction and object/result separation. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Existing argv-named internal token records may still be reused internally | Avoids broad duplication while commandless public result records remove command metadata | If these names leak into new top-level APIs or confuse public docs in Phase 4 |

## Reviewability

- Expected PR size and shape: moderate API/test change focused on `_argv.py`, `api.py`, `__init__.py`, and targeted tests.
- Files and areas to inspect: commandless parser errors, result `to_dict()` shape, retained helper diagnostics, lazy exports, scoped overlay ordering.
- Scope-control checks: no resolver callback, no selected instantiation, no implicit process argv, no docs/example rewrite.

## Implementation Steps

1. Add commandless parser record and parsing entrypoint in `_argv.py` with config-args diagnostics.
2. Add commandless result records and fixed-base `ConfigEntrypoint` in `api.py`.
3. Route commandless helpers through the existing scoped-overlay composition inspection path and helper-local warnings.
4. Convert retained argv helpers to reject old command-first shapes or route first-token-as-base commandless sequences.
5. Add lazy top-level exports and focused tests for parser, integration behavior, result shape, migration diagnostics, and import surface.

## Test Plan

### Package Suite

- Status: required
- Expected paths: `tests/test_import.py`
- Required assertions or deferral reason: lazy top-level exports include only `ConfigEntrypoint`, `compose_config_from_args`, and `inspect_config_args` from the new surface; detailed commandless records stay in `weave.api`.

### Unit Suite

- Status: required
- Expected paths: `tests/unit/config/test_argv.py`
- Required assertions or deferral reason: commandless token classification, scoped overlay resolution, malformed token diagnostics, disallowed and allowed unparsed args, no command details in error contexts.

### Contract Suite

- Status: required
- Expected paths: `tests/contracts/test_config_composition_inspection_contract.py` or a focused public API contract test
- Required assertions or deferral reason: commandless `to_dict()` result shape omits command fields and object fields.

### Integration Suite

- Status: required
- Expected paths: `tests/integration/config/test_compose_argv_from_cli.py` or successor commandless helper tests
- Required assertions or deferral reason: fixed-base compose/inspect, warnings, scoped overlay order, raw snapshot opt-in, retained helper migration diagnostics.

### E2E Suite

- Status: deferred
- Expected paths: none
- Required assertions or deferral reason: Phase 1 does not add a first-party executable or user-facing workflow.

### Opt-In Suites

- Status: deferred
- Markers affected: contract tests only if existing contract markers are used
- Required assertions or deferral reason: no new optional dependency or slow suite is introduced.

## Risks

- Accidentally retaining command fields in new result exports.
- Breaking Stage 0 scoped overlay ordering while refactoring parser code.
- Old helper compatibility expectations may remain in tests or docs; Phase 4 owns public docs cleanup.

## Validation Commands

Targeted development commands:

```sh
uv run --group dev python -m pytest tests/unit/config/test_argv.py
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

- Safe implementation slices: parser first, API/result records second, export surface third, focused tests last.
- Tests to run with each slice: unit parser tests after `_argv.py`, integration helper tests after `api.py`, import tests after `__init__.py`.
- Decisions the executor must not revisit: commandless helpers do not infer commands, do not default to `sys.argv`, do not add resolver or instantiation behavior.
- Conditions that require stopping for the manager: implementation requires command semantics, a process argv default, or a base resolver to satisfy fixed-base behavior.

## Refinement And Review Budget Status

- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed in `docs/roadmap/stage-1/phases/stage-1-commandless-contracts.md`
- Final phase execution plan: completed in this artifact
- Implementation summary: added commandless config-args parser records, fixed-base `ConfigEntrypoint`, `compose_config_from_args(...)`, `inspect_config_args(...)`, commandless result records, retained-helper migration diagnostics, lazy top-level exports, focused tests, and a minimal example-code compatibility update for validation.
- Scope control: resolver callbacks, selected instantiation, full-config instantiation, implicit `sys.argv`, first-party CLI behavior, and broad docs rewrites were not implemented.
- Tests added or updated: unit parser coverage in `tests/unit/config/test_argv.py`; integration helper coverage in `tests/integration/config/test_compose_argv_from_cli.py`; import-boundary coverage in `tests/test_import.py`; contract result/error coverage in `tests/contracts/test_config_composition_inspection_contract.py` and `tests/contracts/test_config_error_contract.py`.
- Implementation validation: `uv run --group dev python -m pytest tests/unit/config/test_argv.py tests/integration/config/test_compose_argv_from_cli.py tests/test_import.py tests/contracts/test_config_composition_inspection_contract.py tests/contracts/test_config_error_contract.py` passed with 59 tests; `make test-unit` passed with 278 tests; `make test-integration` passed with 91 tests; `make test-package` passed with 28 selected tests; `uv run --group dev python -m pytest tests/contracts` passed with 31 tests; `make validate-pr` passed; `make test-summary` completed.
- Refinement summary: not run; implementation refinement budget remains unused.
- Blocker-resolution summary: 0/3 used.
- PR preparation: not performed in this pass; no PR opened.
- Stack maintenance: no branch/worktree cleanup performed because the implementation ran in the current checkout due the recorded local setup limitations.
- Remaining blockers: remote target branch mismatch remains unresolved for PR targeting; original checkout still contains unrelated pre-existing roadmap/docs changes.
