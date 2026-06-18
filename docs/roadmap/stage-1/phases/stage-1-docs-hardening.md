# Phase 4 Execution Plan: Docs, Examples, And Hardening

## Metadata

- Status: local implementation and validation complete; PR pending
- Feature focus: Stage 1 config entrypoint
- PR title: `Stage 1 config entrypoint - Phase 4: Docs, examples, and hardening`
- Branch: `codex/stage-1-docs-hardening`
- Worktree: `/nas/home/can134/work/weave-worktrees/stage-1-docs-hardening`
- Phase execution plan path: `docs/roadmap/stage-1/phases/stage-1-docs-hardening.md`
- Full plan: `docs/roadmap/stage-1/implementation-plan.md`
- Source phase: Phase 4, `stage-1-docs-hardening`
- Stack predecessor: Phase 3 merged to `develop`
- Base branch: `develop`
- Target branch: `develop`
- Merge eligibility: eligible after docs/example updates, focused scans, `make validate-pr`, `make test-summary`, PR CI, and workflow metadata updates
- Workflow path: expanded path
- Successor dependency notes: completes Stage 1 implementation documentation for later Stage 2/3 planning.
- Plan quality gate: passed in the full implementation plan
- Plan quality gate loop budget: complete before this phase
- Draft pass: completed
- Refine pass: completed in this artifact
- Setup limitations: original checkout has unrelated dirty docs; Phase 4 work occurs only in this clean worktree.
- Blockers: none for local Phase 4 implementation

## Objective

Align public documentation, runnable examples, and docs coverage records with the implemented Stage 1 commandless `ConfigEntrypoint` surface without adding runtime behavior.

## Full-Plan Context

Phases 1 through 3 merged the commandless helper contract, generic base resolution, and selected instantiation. Phase 4 closes the loop by removing stale command-first recommendations from public docs, adding examples for the project-owned adapter boundary, and recording behavior/coverage matrices that downstream documentation can rely on.

## Stack Context

- Root or stacked phase: root phase after Phase 3 merge
- Current predecessor branch or PR: PR #3 merged into `develop`
- Why this base branch is correct: Phase 4 depends on the complete Stage 1 API surface through Phase 3.
- Retarget/rebase plan after predecessor merge: not needed; predecessor is merged and this branch starts from `origin/develop`.
- Branch cleanup constraints: delete the remote/local Phase 4 branch only after merge and metadata update.

## Source Phase Summary

- Goal: align public docs, examples, behavior matrix, README snippets, and test coverage records with the implemented commandless Stage 1 surface.
- Required scope: docs rewrite for commandless helpers, project-owned adapter examples, resolver and selected-instantiation examples, behavior matrix, example coverage, and focused scans.
- Required checkpoints: no public docs recommend command semantics, first-party CLI ownership, implicit `sys.argv`, or full-config instantiation.
- Acceptance criteria: docs and examples match implemented behavior and validation evidence is recorded.

## Current Source And Harness Findings

- Existing files or modules that constrain this phase: `README.md`, `docs/features/config-composition.md`, `docs/features/project-cli-argv.md`, `examples/project-cli-argv/`, `examples/README.md`, `docs/GLOSSARY.md`, and roadmap docs currently contain the public narrative.
- Existing tests or harness behavior: `tests/test_examples.py` executes examples; focused integration tests already cover commandless helpers, resolver metadata, selected instantiation, and migration diagnostics.
- Import-boundary or dependency constraints: examples must stay domain-neutral and avoid new runtime dependencies or first-party executable claims.

## In-Scope Work

- Rewrite stale command-first docs to describe explicit config args and project-owned argv adapters.
- Update README and feature docs to recommend `ConfigEntrypoint`, `compose_config_from_args(...)`, and `inspect_config_args(...)`.
- Add or update runnable examples for fixed-base adapters, generic base resolvers, selected instantiation, and migration diagnostics.
- Add or update behavior matrix and example coverage docs.
- Update glossary and roadmap snippets where terminology points at old command-first behavior.
- Run focused scans and example/full validation.

## Out-of-Scope Work

- Runtime API changes beyond small test/example support fixes.
- First-party executable docs, command semantics, `command_choices`, implicit `sys.argv`, global config search, or full-config instantiation.
- Domain recipes, schemas, datasets, metrics, reports, workflows, stores, schedulers, or remote/plugin examples.

## Assumptions

- Existing example harness can cover updated examples without new dependencies.
- Stage 1 docs should describe retained argv helper names as migration-compatible helpers, not current command-first recommendations.
- Behavior matrix and example coverage docs are source-controlled documentation artifacts, not generated files.

## Scope Contract

Phase 4 changes documentation and examples only. Public docs should present downstream projects as the owners of CLI parsing and base selection policy. Weave accepts explicit config args, composes deterministic plain-data configs, optionally resolves a base via caller-owned context, and optionally instantiates only explicitly selected dot paths. Result exports must continue to avoid command metadata and Python object serialization.

## Design Impact

- Maintainability: consolidate Stage 1 guidance around one current commandless adapter model.
- Extensibility: keep future command support, richer selectors, and full-config instantiation documented as deferred rather than implied.
- Domain neutrality: examples use generic service/model/data names only and no domain-specific pipelines.
- Source-tree boundaries: docs/examples/harness updates only unless validation exposes a small support issue.

## Future Compatibility

Stage 2 can reference implemented Stage 1 docs directly. Stage 3 candidates remain deferred unless a later design introduces richer execution, storage, or workflow behavior.

## Alternatives Rejected

| Alternative | Reason rejected |
| --- | --- |
| Keep `project-cli-argv` as command-first docs | The implemented helper contract is commandless and old command-shaped input is a migration diagnostic path. |
| Add a first-party CLI example | Stage 1 explicitly keeps parser ownership downstream. |
| Document full-config instantiation | Stage 1 only supports selected explicit instantiation. |

## Debt Introduced

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| Compatibility wording for retained argv helper names | Names remain available but no longer describe the preferred helper contract. | Release docs require a separately named legacy command-first API. |

## Reviewability

- Expected PR size and shape: docs/example-focused change with no runtime behavior changes.
- Files and areas to inspect: README snippets, feature docs, example code/README, behavior matrix, example coverage, roadmap metadata.
- Scope-control checks: no command-owned examples, no implicit argv defaulting, no full-config instantiation, no domain-specific behavior.

## Implementation Steps

1. Update README, glossary, roadmap snippets, and feature docs to describe commandless config args and adapter ownership.
2. Update or add runnable examples for fixed-base adapters, resolver base selection, selected instantiation, and migration diagnostics.
3. Add behavior matrix and example coverage docs that record implemented and deferred Stage 1 behavior.
4. Run focused scans and example validation, then full `make validate-pr` and `make test-summary`.
5. Update workflow metadata and open the Phase 4 PR against `develop`.

## Test Plan

### Package Suite

- Status: required through `make validate-pr`
- Expected paths: `tests/test_import.py` and package-marked tests
- Required assertions or deferral reason: docs/example updates do not change import boundaries.

### Unit Suite

- Status: required through `make validate-pr`
- Expected paths: existing unit suite
- Required assertions or deferral reason: no runtime changes expected; existing API coverage should remain green.

### Contract Suite

- Status: required through `make validate-pr`
- Expected paths: existing contract suite
- Required assertions or deferral reason: docs/examples must not alter artifact contracts.

### Integration Suite

- Status: required through `make validate-pr`
- Expected paths: existing integration suite plus examples where applicable
- Required assertions or deferral reason: commandless helpers, resolver metadata, selected instantiation, and migration diagnostics remain green.

### E2E Suite

- Status: required through example harness
- Expected paths: `tests/test_examples.py`, `examples/`
- Required assertions or deferral reason: runnable examples demonstrate current Stage 1 behavior.

### Opt-In Suites

- Status: deferred
- Markers affected: none
- Required assertions or deferral reason: no new optional dependency behavior is introduced.

## Risks

- Docs overpromise unimplemented behavior.
- Stale command-first recommendations remain discoverable.
- Example changes accidentally imply a first-party executable or domain-specific workflow.

## Validation Commands

Targeted development commands:

```sh
make test-examples
rg -n "compose_config_from_argv|inspect_config_from_argv|command_choices|sys\.argv|<command>|full-config instantiation" README.md docs examples tests
```

Final PR-preparation commands:

```sh
make validate-pr
make test-summary
```

## Handoff Notes For `weave_phase_executor`

- Safe implementation slices: public docs first, runnable examples second, matrix/coverage docs third, validation and metadata last.
- Tests to run with each slice: `make test-examples` after example edits; focused `rg` scans after docs edits; full validation before PR.
- Decisions the executor must not revisit: no first-party CLI, no command semantics, no implicit `sys.argv`, no full-config instantiation, no domain-specific examples.
- Conditions that require stopping for the manager: documentation requires behavior not merged in Phases 1-3 or would need runtime API changes outside small support fixes.

## Refinement And Review Budget Status

- Phase implementation refinement: unused
- PR review: unused
- Blocker resolution: 0/3 used

## Completion Notes

- Draft plan: completed in this artifact
- Final phase execution plan: completed in this artifact
- Implementation summary: aligned README, feature docs, glossary, roadmap, behavior matrix, example coverage, and the project-owned adapter example with Stage 1 behavior.
- Implementation validation: `make test-examples`, focused docs scans, `make validate-pr`, and `make test-summary` passed.
- Refinement summary: no additional refinement loop used
- Blocker-resolution summary: none
- PR preparation: pending; local validation complete
- Stack maintenance: Phase 3 merged before branch creation
- Remaining blockers: none
