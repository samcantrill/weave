# Stage 1 Implementation Plan: Project Config Entrypoint Object

Status: draft
Roadmap stage: `v1`
Planning document: `docs/roadmap/stage-1/planning.md`
Workflow: `.codex/workflows/roadmap-stage-implementation.md`
Target branch: `develop`
Current phase: Phase 3 execution planning complete; implementation pending
Blockers: none

## Summary

- Goal: implement a reusable project-owned config entrypoint object that composes
  explicit commandless config args, preserves structured metadata, and optionally
  instantiates selected trusted values.
- Source functionality-agreement gate: complete in
  `docs/roadmap/stage-1/planning.md`.
- Approved behavior: downstream projects pass explicit `config_args`; Weave does
  not parse project command structure, infer argv boundaries, require command
  tokens, or expose command result fields.
- Source behavior confirmation: complete; command semantics, full-config
  instantiation, implicit `sys.argv` defaulting, global config search, and
  first-party CLI behavior are excluded from Stage 1.
- Key design constraints: domain-neutral APIs, lightweight `import weave`,
  artifact-safe defaults, explicit trusted target execution, no new heavyweight
  runtime dependencies, no workflow/store/scheduler/schema behavior.
- Source design-agreement gate: complete; recorded recommendations define
  `ConfigEntrypoint`, commandless config-args records, generic base resolution,
  separate compose/inspect methods, selected dot-path instantiation, and
  object/metadata separation.
- Future-roadmap impact: Stage 2 can document implemented Stage 1 behavior or
  an explicit deferral; Stage 3 candidates remain outside this contract.
- Reusable interface, adapter, or protocol assumptions: `ConfigBaseRequest`
  carries opaque caller-owned resolver input; `ConfigBaseResolution` returns a
  selected base path plus optional plain-data details; selected-instantiation
  selectors are dot-path strings or caller-name-to-dot-path mappings.
- Examples covered: project-owned parser adapter that passes unparsed config
  args to Weave, fixed base path, generic base resolver, selected target
  instantiation, and migration diagnostics for old command-first invocation
  shapes.
- Public helper/export policy: `compose_config_from_args(...)` and
  `inspect_config_args(...)` are the preferred commandless function-level
  helpers. `ConfigEntrypoint` and these preferred helpers are lazily exported
  from `weave`; detailed parse/result/base-resolution records are exported from
  `weave.api` unless a later reviewed plan change intentionally widens the
  top-level surface. Retained `compose_config_from_argv(...)` and
  `inspect_config_from_argv(...)` do not preserve command-first semantics; they
  raise targeted migration diagnostics for `<command> <base-config> ...`
  shapes or otherwise route to the commandless contract exactly as defined in
  Phase 1.
- Source phase shaping: four confirmed phases in the planning artifact.
- Source plan quality gate: initial implementation-plan review found required
  revisions; those revisions are incorporated here and a follow-up review is
  still required before phase work.
- Out of scope: command semantics, command choices, command-specific resolver
  APIs, first-party executable, argparse ownership, global search, project-root
  discovery, full-config instantiation, workflow execution, persistence policy,
  Stage 3 behavior candidates, domain schemas, and untrusted sandboxing.

## Context

Stage 0 delivered deterministic composition, argv shorthand, recipes,
inspection, artifacts, raw snapshot opt-in, and explicit target instantiation.
The current public argv helper implementation is command-first: `ParsedConfigArgv`,
`ConfigArgvCompositionResult`, `ConfigArgvInspectionResult`,
`compose_config_from_argv(...)`, and `inspect_config_from_argv(...)` all encode
`command` or `command_choices` in some way. Stage 1 intentionally moves the
current public helper contract to commandless config args.

This plan preserves helper availability where retained, not command-first
semantics. Existing tests and docs that treat `<command> <base-config> ...` as
the current shape are expected to change, be replaced, or become targeted
migration-diagnostic coverage.

## Planning Readiness

| Check | Result | Evidence |
| --- | --- | --- |
| Functionality and behavior confirmed | pass | Planning artifact has confirmed FR-1 through FR-7. |
| Design agreement resolved | pass | DAQ-1 through DAQ-9 are confirmed. |
| Design-safety review passed | pass | Reviewer upheld DAQ-7 and found no design blocker. |
| Future-roadmap impact considered | pass | Stage 2 and Stage 3 impacts recorded in planning. |
| Interface/adapter/protocol assumptions explicit | pass | Base resolver and selector shapes are recorded. |
| Validation and phase shaping specific enough | pass | Planning includes examples, validation rows, and four phases. |
| Plan quality gate complete | block | Must be reviewed by `weave_plan_reviewer` before first implementation phase. |

## Desired Outcome

A downstream project can write code shaped like this without inventing a command:

```python
entrypoint = ConfigEntrypoint(
    base_config_path="configs/base.yaml",
    recipe_catalog=catalog,
    allow_unparsed=True,
)

result = entrypoint.compose_args([
    "model/=small",
    "seed=123",
])
```

For command-line applications, the recommended adapter shape is that downstream
projects use their own parser for project-owned flags and pass the parser's
remaining/unparsed args to Weave as `config_args`. Weave should then raise
commandless config-arg diagnostics if those leftovers are malformed or include
disallowed passthrough tokens.

The result exposes stable commandless metadata, a `ComposedConfig`, helper-local
warnings, unparsed args from the supplied config-arg sequence, and optional
selected objects. `objects` are returned separately and are not included in
plain-data result exports.

## Non-Goals

- No command token, command choices, command result field, command-specific
  resolver argument, or command-shaped error remediation.
- No implicit read from `sys.argv[1:]`.
- No first-party executable, parser framework, process-exit policy, or terminal
  formatting.
- No global config search, package-level project-root discovery, or default
  config names.
- No default instantiation and no full-config instantiation in Stage 1.
- No persistence of resolved configs, raw source bytes, or instantiated objects
  by default.
- No domain recipes, schemas, datasets, metrics, reports, workflows, schedulers,
  run stores, remote include resolution, plugin include hooks, Hydra bridge, or
  `_copy_` behavior.

## Constraints

- Ordinary `import weave` must remain lightweight and must not import downstream
  project code.
- Authored configs remain trusted project code; this plan does not introduce an
  untrusted sandbox.
- Composition order must remain stable: argv scoped overlays apply before recipe
  expansion; ordinary value overrides apply after recipe expansion.
- Helper-local warnings stay out of normal composed config artifacts.
- Raw source snapshots remain opt-in and metadata-only source artifacts remain
  the default.
- `base_context` is opaque resolver input and is never automatically serialized
  into result metadata.
- New commandless parser diagnostics must use config-args terminology and omit
  command-shaped details or remediation.

## Design Principles

- Make the adapter boundary explicit: projects own argv parsing and pass their
  parser's remaining config args to Weave.
- Prefer distinct commandless records over nullable fields on command-bearing
  records.
- Keep result metadata plain-data friendly, but keep Python object instances out
  of serialized output.
- Reuse existing composition and `instantiate(...)` behavior instead of
  inventing new semantics.
- Keep extension points narrow and path-oriented; do not turn the entrypoint
  into a plugin, search, store, scheduler, or workflow registry.

## Key Design Choices

| Choice | Decision | Rejected alternatives | Revisit trigger |
| --- | --- | --- | --- |
| Public object name | Use `ConfigEntrypoint`. | `ConfigComposer`, because selected instantiation makes the object broader than composition. | Before merge only if maintainers choose a different public name. |
| Result and parse records | Use `ParsedConfigArgs`, `ConfigArgsCompositionResult`, and `ConfigArgsInspectionResult` from `weave.api`; do not add them to the top-level `weave` export surface in Phase 1. | Reusing `ParsedConfigArgv` or command-bearing result records unchanged. | If implementation finds unavoidable duplication that cannot be factored internally. |
| Base resolver | Use `ConfigBaseRequest(base_context=...)` and `ConfigBaseResolution(base_config_path=..., details=...)`. | Resolver receiving command, argparse namespace, full project argv, or search-path registry state. | Real adapters need multiple coordinated base strategies. |
| Method shape | Separate `ConfigEntrypoint.compose_args(...)` and `ConfigEntrypoint.inspect_args(...)` over explicit `config_args=()`, plus preferred function helpers `compose_config_from_args(...)` and `inspect_config_args(...)`. | One mode-flag method, implicit `sys.argv`, full-project-argv scanning. | Usage evidence shows separate methods create real friction. |
| Selected instantiation | Use dot paths or name-to-dot-path mappings; selected values pass to existing `instantiate(...)`. | Default instantiation, full-config instantiation, automatic target discovery, requiring selected values to be `_target_` mappings. | Selected dot paths do not cover common handoff workflows. |
| Plain-data export | Include stable metadata and composed/inspection data; exclude `objects`. | Serializing Python objects or opaque `base_context`. | Downstream adapters need additional stable metadata. |
| Failure semantics | Fail closed with structured, commandless diagnostics. | Best-effort fallback base selection, command-shaped errors, unstructured exceptions. | Existing error types cannot carry required context. |
| Docs/examples | Migrate docs/examples to explicit config args and project-owned adapters. | New examples using command semantics or implying a bundled command. | Stage 1 slips and Stage 2 must record explicit deferral. |

## Conflicts And Tradeoffs

- Existing command-first helpers and tests are not treated as the target public
  behavior. This creates migration cost, but it removes a semantic mismatch the
  user explicitly rejected.
- Adding distinct commandless records increases API surface, but avoids carrying
  a misleading nullable `command` field forever.
- Selected instantiation can return plain non-target values because it reuses
  `instantiate(...)`; stricter target-only behavior would be a new product
  choice and is intentionally not introduced here.
- The base resolver remains deliberately narrow. Projects that want search paths
  or global conventions must keep that policy downstream or propose a later
  design.

## Maintainability Assessment

The plan consolidates new behavior around one commandless parser and result
contract. The main maintenance risk is overlap with the current command-first
argv code. Implementation should factor token parsing where useful, but must not
expose command-bearing records through Stage 1 APIs.

Each phase is reviewable in isolation: public commandless contracts, resolver
support, selected instantiation, then docs/examples/hardening.

## Extensibility Assessment

The interfaces are intentionally generic:

- `ConfigBaseRequest` accepts caller-owned context without naming commands or
  CLI frameworks.
- `ConfigBaseResolution` exposes only a selected path and explicit plain-data
  details.
- Selected-instantiation selectors are dot paths, independent of executors,
  stores, schedulers, or schemas.
- Future command context can be designed separately if a concrete need appears.

## Technical Debt Ledger

| Debt | Reason accepted | Revisit trigger | Owner phase |
| --- | --- | --- | --- |
| Existing command-first helper callers need migration. | User confirmed command reliance should be removed from current and planned helper behavior. | Release compatibility requires a separately named legacy command-first helper. | Phase 1 and Phase 4 |
| Public API names create lock-in. | Names are needed for a stable adapter contract and match planning recommendations. | Maintainer chooses different names during plan review. | Phase 1 |
| Selected dot paths may be too narrow. | They satisfy the confirmed selected-instantiation done bar without executor/store coupling. | Real adapters need richer selector behavior. | Phase 3 |

## Implementation Workflow State

- Implementation-plan quality gate: passed
- Review pass: initial `weave_plan_reviewer` review blocked on helper/export policy, Phase 3 ordering, and validation concreteness
- Refinement pass: completed; required revisions incorporated
- Confirmation review: follow-up `weave_plan_reviewer` review passed
- Automatic merge mode: enabled
- Worktree root: `/nas/home/can134/work/weave-worktrees`
- Phase status vocabulary: `pending`, `in_progress`, `pr_open`, `approved`, `merged`, `blocked`

## Phase Index

| Phase | Slug | Status | Branch | PR | Ownership | Goal | Validation | Examples |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `stage-1-commandless-contracts` | merged | `codex/stage-1-commandless-contracts` | https://github.com/samcantrill/weave/pull/1 | `src/weave/api.py`, `src/weave/_argv.py`, `src/weave/__init__.py`, `tests/unit/config/`, `tests/integration/config/`, import tests | Add commandless parser, `ConfigEntrypoint`, preferred commandless helpers, fixed-base compose/inspect, result records, export policy, and migration diagnostics. | `make test-unit`, `make test-integration`, package import tests, commandless result-shape tests. | None yet; docs/examples in Phase 4. |
| 2 | `stage-1-base-resolution` | merged | `codex/stage-1-base-resolution` | https://github.com/samcantrill/weave/pull/2 | `src/weave/api.py`, resolver tests | Add generic base resolver request/resolution and metadata boundaries. | Unit/integration tests for resolver success/failure and serialization boundaries. | Resolver example draft only if useful; final docs in Phase 4. |
| 3 | `stage-1-selected-instantiation` | in_progress | `codex/stage-1-selected-instantiation` | pending | `src/weave/api.py`, instantiation integration tests | Add selected dot-path instantiation and object/result separation. | Unit/integration tests for selectors, runtime injection, non-target values, and no-import default. | Example draft only if useful; final docs in Phase 4. |
| 4 | `stage-1-docs-hardening` | pending | `codex/stage-1-docs-hardening` | pending | `docs/`, `examples/`, example tests, migrated argv docs/tests | Align docs, examples, behavior matrix, README snippets, and migration notes. | Example harness, docs review, focused tests, and `make validate-pr` if available. | Project-owned adapter, resolver, selected instantiation, migration diagnostics. |

## Implementation Readiness Blockers

| Blocker | Source | Required resolution | Status |
| --- | --- | --- | --- |
| Implementation-plan review not complete | Plan quality gate | Follow-up `weave_plan_reviewer` review passed after required revisions. | resolved |

## Phase 1: Commandless Public Contracts

Status: merged
Slug: `stage-1-commandless-contracts`
Branch: `codex/stage-1-commandless-contracts`
Worktree: `/nas/home/can134/work/weave-worktrees/stage-1-commandless-contracts`
PR: https://github.com/samcantrill/weave/pull/1
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: establish commandless Stage 1 public contracts and fixed-base compose
  and inspect behavior.
- Files/modules owned: `src/weave/api.py`, `src/weave/_argv.py`,
  `src/weave/__init__.py`, commandless parser tests, fixed-base integration
  tests, import-boundary tests.
- Behavior implemented:
  - `ConfigEntrypoint` with fixed `base_config_path`.
  - `ParsedConfigArgs`, `ConfigArgsCompositionResult`, and
    `ConfigArgsInspectionResult`.
  - `ConfigEntrypoint.compose_args(config_args=())` and
    `ConfigEntrypoint.inspect_args(config_args=())` with no implicit
    `sys.argv` default.
  - `compose_config_from_args(...)` and `inspect_config_args(...)` as preferred
    commandless function-level helpers.
  - Commandless parsing for value overrides, scoped overlays, and unparsed args.
  - Helper-local warnings and raw snapshot policy routed through existing
    composition behavior.
  - Lazy top-level exports for `ConfigEntrypoint`,
    `compose_config_from_args(...)`, and `inspect_config_args(...)`; detailed
    parse/result/base-resolution records remain available from `weave.api`.
  - Retained `compose_config_from_argv(...)` and `inspect_config_from_argv(...)`
    do not preserve command-first semantics. In Phase 1 they must raise
    targeted migration diagnostics for `<command> <base-config> ...` shapes or
    route to the same explicit-base/config-args commandless contract; the exact
    behavior is locked here and must not be decided during code implementation.
- Decisions applied: DAQ-1, DAQ-2, DAQ-4, DAQ-6, DAQ-7, DAQ-8.
- Examples or docs covered: minimal API docstrings if useful; public docs wait
  for Phase 4.
- Out of scope: base resolver callbacks, selected instantiation, full-config
  instantiation, command semantics, `sys.argv` defaulting, docs/example rewrite.
- Dependencies: Stage 0 composition and argv shorthand behavior.

### Tasks

- Add distinct commandless parser records and parsing entrypoint.
- Factor shared parsing helpers from `_argv.py` only where it avoids duplication
  without leaking command fields.
- Add commandless result dataclasses and plain-data export methods.
- Add `ConfigEntrypoint` constructor validation for fixed-base mode.
- Implement `inspect_args(...)` and `compose_args(...)` fixed-base flow through
  existing composition inspection.
- Add `compose_config_from_args(...)` and `inspect_config_args(...)` as the
  preferred commandless function-level helpers.
- Make retained `compose_config_from_argv(...)` and
  `inspect_config_from_argv(...)` raise targeted migration diagnostics for old
  `<command> <base-config> ...` invocation shapes or route to the same
  explicit-base/config-args commandless contract. They must not preserve
  command-first semantics.
- Add lazy top-level exports and `__all__` entries for `ConfigEntrypoint`,
  `compose_config_from_args(...)`, and `inspect_config_args(...)` without
  increasing import side effects.
- Keep detailed commandless parse/result/base-resolution records in `weave.api`
  rather than widening the top-level import surface in Phase 1.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` or focused `uv run --group dev python -m pytest tests/unit/config` | Parser classification, malformed config args, unparsed args, commandless remediation. | yes |
| `make test-integration` or focused `uv run --group dev python -m pytest tests/integration/config` | Fixed-base commandless composition, warnings, scoped overlay order, raw snapshot policy, migration diagnostics. | yes |
| `make test-package` or focused import-boundary tests in `tests/` | Lazy exports and import boundary. | yes |
| Commandless result-shape tests in `tests/contracts` or the relevant public API test module | `to_dict()` fields, absence of command fields, top-level export policy, object exclusion placeholder. | yes |

### Acceptance Evidence

- Behavior evidence: fixed-base `compose_args(...)` and `inspect_args(...)` work
  with explicit config args and no command token.
- Design-decision evidence: new result metadata has no `command` field and uses
  distinct commandless records.
- Future-roadmap compatibility evidence: no first-party CLI, search path,
  workflow, store, scheduler, or schema behavior is added.
- Interface, adapter, or protocol reuse evidence: explicit config-args sequence
  works for CLI adapters and Python applications.
- Documentation evidence: temporary docs or test names do not imply command
  semantics; Phase 4 owns final docs and should recommend the project-parser
  leftovers adapter pattern.
- Domain-neutrality evidence: no domain-specific flags, schemas, recipes, or
  examples are introduced.

### Phase Workflow State

- Phase execution plan: completed in `docs/roadmap/stage-1/phases/stage-1-commandless-contracts.md`
- Planning/refinement budget: completed; no additional planning loop used
- Implementation/refinement budget: unused
- PR review budget: unused
- Blocker-resolution budget: 0/3 used
- Pre-submit blocker gate: satisfied for local implementation; PR preparation pending
- Merge record: `docs/roadmap/stage-1/phases/stage-1-commandless-contracts-merge-record.md`

### Risks And Stop Conditions

- Risks: accidental leakage from `ParsedConfigArgv`; compatibility conflict over
  old helper names; stale docs/tests asserting command-first behavior.
- Stop conditions: implementation requires preserving command semantics, adding
  `sys.argv` defaulting, or inventing unplanned parser behavior.
- Assumptions: commandless helper availability can be delivered without a
  separately supported legacy command-first API.

### Completion Summary

- Implementation: completed and merged for commandless parser, fixed-base `ConfigEntrypoint`, preferred helpers, result records, retained-helper migration diagnostics, lazy exports, and focused tests.
- Validation: `make validate-pr` passed; `make test-summary` completed; GitHub `CI/checks` passed on PR #1.
- PR: https://github.com/samcantrill/weave/pull/1.
- Merge: merged into `develop` with merge commit `e4e9221`; metadata update pushed in commit `ca2455a`.
- Follow-up: Phase 2 base resolution is in progress.

## Phase 2: Base Resolution And Config-Arg Policies

Status: merged
Slug: `stage-1-base-resolution`
Branch: `codex/stage-1-base-resolution`
Worktree: `/nas/home/can134/work/weave-worktrees/stage-1-base-resolution`
PR: https://github.com/samcantrill/weave/pull/2
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: add project-owned base resolution without command semantics or config
  search behavior.
- Files/modules owned: `src/weave/api.py`, resolver-specific tests, result
  metadata tests.
- Behavior implemented:
  - `ConfigBaseRequest(base_context=...)`.
  - `ConfigBaseResolution(base_config_path=..., details=...)`.
  - Constructor validation for exactly one base strategy: fixed path or
    resolver.
  - Resolver invocation during compose/inspect calls.
  - Plain-data details in result metadata when returned explicitly.
  - Missing, conflicting, non-callable, and invalid resolver-return diagnostics.
- Decisions applied: DAQ-3, DAQ-6, DAQ-8.
- Examples or docs covered: optional inline examples in tests; final docs wait
  for Phase 4.
- Out of scope: global config search, project-root discovery, default names,
  include resolver hooks, command-specific resolver APIs, serializing opaque
  `base_context`.
- Dependencies: Phase 1 commandless contracts.

### Tasks

- Add base request/resolution dataclasses with validation and plain-data export.
- Add resolver support to `ConfigEntrypoint` constructor and compose/inspect
  flow.
- Add result metadata for base source and explicit resolver details.
- Ensure `base_context` is input-only and never included in `to_dict()` output
  unless represented by explicit resolver details.
- Add failure diagnostics for invalid strategy combinations and resolver output.
- Add tests for fixed path and resolver path parity.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` or focused resolver tests in `tests/unit/config` | Strategy validation, request/resolution validation, invalid returns, opaque context. | yes |
| `make test-integration` or focused resolver tests in `tests/integration/config` | Composition with resolver-selected base plus config args and warnings. | yes |
| Contract/result export tests in `tests/contracts` or relevant API tests | Resolver details serialized only when explicit and plain-data. | yes |
| `make test-package` or focused import-boundary tests in `tests/` | Resolver support adds no import side effects. | yes |

### Acceptance Evidence

- Behavior evidence: resolver-selected base composition works without command
  input.
- Design-decision evidence: `base_context` does not appear in result plain-data
  export.
- Future-roadmap compatibility evidence: no search path, plugin, store,
  scheduler, or workflow extension point is introduced.
- Interface, adapter, or protocol reuse evidence: resolver request/resolution
  records are generic and domain-neutral.
- Documentation evidence: Phase 4 notes updated if APIs need docs coverage.
- Domain-neutrality evidence: resolver examples use neutral project context.

### Phase Workflow State

- Phase execution plan: completed in `docs/roadmap/stage-1/phases/stage-1-base-resolution.md`
- Planning/refinement budget: completed; no additional planning loop used during implementation
- Implementation/refinement budget: unused
- PR review budget: unused
- Blocker-resolution budget: 0/3 used
- Pre-submit blocker gate: satisfied locally; PR #2 merged into `develop` after CI passed
- Merge record: `docs/roadmap/stage-1/phases/stage-1-base-resolution-merge-record.md`

### Risks And Stop Conditions

- Risks: resolver contract becomes too broad; result metadata leaks arbitrary
  project context.
- Stop conditions: implementation requires global search, command-specific
  context, or serialization of arbitrary caller objects.
- Assumptions: one resolver callback is enough for Stage 1 adapter workflows.

### Completion Summary

- Implementation: completed locally for resolver request/resolution records, exact-one base strategy validation, resolver compose/inspect flow, commandless `base_details` result metadata, structured diagnostics, detailed API export policy, and focused tests.
- Validation: focused Phase 2 tests passed; `make validate-pr` passed; `make test-summary` completed with package 28, unit 285, contract 32, integration 93, and examples 9 passing.
- PR: https://github.com/samcantrill/weave/pull/2 targeting `develop`.
- Merge: merged into `develop` with merge commit `fa3ace8` after GitHub `CI/checks` passed.
- Follow-up: Phase 3 selected instantiation remains pending after Phase 2 merge.

## Phase 3: Optional Selected Instantiation

Status: in_progress
Slug: `stage-1-selected-instantiation`
Branch: `codex/stage-1-selected-instantiation`
Worktree: `/nas/home/can134/work/weave-worktrees/stage-1-selected-instantiation`
PR: pending
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: add explicit selected trusted object construction while keeping
  composition inert by default.
- Files/modules owned: `src/weave/api.py`, selected-instantiation tests,
  import-boundary tests.
- Behavior implemented:
  - Selector normalization for dot-path sequences and name-to-dot-path mappings.
  - Lookup from `ComposedConfig.resolved`.
  - Per-selection call to existing `instantiate(...)` with runtime injection.
  - `objects` mapping on composition results.
  - Plain-data selected-object metadata without serializing objects.
  - Selected non-target values remain plain values through existing
    `instantiate(...)` semantics.
- Decisions applied: DAQ-5, DAQ-6, DAQ-8.
- Examples or docs covered: final docs wait for Phase 4.
- Out of scope: default instantiation, full-config instantiation, automatic
  target discovery, target schema validation, executor hooks, stores,
  persistence, workflow execution.
- Dependencies: Phase 1 commandless result models; Phase 2 if selected
  instantiation uses resolver metadata in combined tests.

### Tasks

- Add selected-instantiation constructor or call policy using explicit selectors.
- Add selector validation and normalized selected-object metadata.
- Implement dot-path lookup with structured missing-path diagnostics.
- Call `instantiate(...)` only for selected values and pass runtime injection.
- Keep `objects` separate from `to_dict()` and other plain-data exports.
- Add tests proving no target import or construction occurs by default.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-unit` or focused selected-instantiation tests in `tests/unit/config` | Sequence and mapping normalization, duplicate keys, invalid selectors, missing paths. | yes |
| `make test-integration` or focused selected-instantiation tests in `tests/integration/config` | Target construction, nested target behavior, runtime injection. | yes |
| Focused selected-value tests in the selected-instantiation test module | Existing `instantiate(...)` semantics leave plain values plain. | yes |
| `make test-package` or focused import-boundary tests in `tests/` | Composition without selection stays inert by default. | yes |
| Contract/result export tests in `tests/contracts` or relevant API tests | Objects are excluded from plain-data export and metadata remains serializable. | yes |

### Acceptance Evidence

- Behavior evidence: selected values instantiate only when requested.
- Design-decision evidence: no full-config instantiation API is introduced.
- Future-roadmap compatibility evidence: no executor/store/workflow persistence
  behavior is added.
- Interface, adapter, or protocol reuse evidence: selectors are plain strings or
  name-to-path mappings.
- Documentation evidence: Phase 4 notes updated for selected-instantiation docs.
- Domain-neutrality evidence: tests use neutral target fixtures.

### Phase Workflow State

- Phase execution plan: completed in `docs/roadmap/stage-1/phases/stage-1-selected-instantiation.md`
- Planning/refinement budget: completed; no additional planning loop used
- Implementation/refinement budget: unused
- PR review budget: unused
- Blocker-resolution budget: 0/3 used
- Pre-submit blocker gate: Phase 1 and Phase 2 merged
- Merge record: pending

### Risks And Stop Conditions

- Risks: selector model proves too narrow; accidental object serialization;
  implicit instantiation slips into compose path.
- Stop conditions: implementation requires full-config instantiation, automatic
  target discovery, or object persistence.
- Assumptions: selected dot paths cover the Stage 1 handoff workflow.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Phase 4: Docs, Examples, And Hardening

Status: pending
Slug: `stage-1-docs-hardening`
Branch: `codex/stage-1-docs-hardening`
Worktree: `/nas/home/can134/work/weave-worktrees/stage-1-docs-hardening`
PR: https://github.com/samcantrill/weave/pull/1
Base branch: `develop`
Target branch: `develop`
Workflow path: expanded path

### Scope

- Goal: align public docs, examples, behavior matrix, README snippets, and test
  coverage records with the implemented commandless Stage 1 surface.
- Files/modules owned: `docs/features/project-cli-argv.md` or successor docs,
  `docs/features/config-composition.md`, `docs/features/example-coverage.md`,
  `docs/features/config-behavior-matrix.md`, `docs/GLOSSARY.md` if terminology
  changes, `README.md`, `examples/`, `tests/test_examples.py`, migrated docs
  and example tests.
- Behavior implemented: documentation and examples only; no new runtime behavior
  unless a small test/doc support fix is required.
- Decisions applied: DAQ-2, DAQ-9 and all validation obligations from planning.
- Examples or docs covered:
  - Fixed-base project-owned parser adapter that passes unparsed config args to
    Weave.
  - Generic base resolver.
  - Selected target instantiation.
  - Migration diagnostics for old command-first invocation shapes.
- Out of scope: first-party executable docs, future command semantics, domain
  examples, schemas, workflows, stores, schedulers, remote/plugin examples.
- Dependencies: Phases 1 through 3 merged.

### Tasks

- Rewrite command-first feature docs to describe the commandless Stage 1 public
  surface and any retained migration diagnostics.
- Update README public API snippets if the old command-first helper is no longer
  a recommended import.
- Add or update runnable examples and example harness coverage.
- Update behavior matrix rows for commandless parsing, configured entrypoint,
  resolver metadata, selected instantiation, import boundaries, artifact-safe
  defaults, and migration diagnostics.
- Update example coverage docs.
- Remove stale references to optional `sys.argv[1:]` defaulting or optional
  full-config instantiation from Stage 1 docs/plans.
- Run focused docs/example validation and broad pre-PR checks as practical.

### Validation

| Command/check | Purpose | Required before phase complete |
| --- | --- | --- |
| `make test-examples` | Runnable examples stay valid. | yes |
| Focused docs scan with `rg` over `README.md docs examples tests` | No Stage 1 helper docs require command or imply first-party executable behavior. | yes |
| Behavior matrix and example coverage review in `docs/features/` | Coverage rows match implemented public behavior and deferrals. | yes |
| `make validate-pr` | Full repository validation before final Stage 1 PR completion. | yes, unless unavailable and documented |
| `make test-summary` | Required before PR body or release-style summary. | when preparing PR body |

### Acceptance Evidence

- Behavior evidence: docs and examples reflect implemented behavior.
- Design-decision evidence: no examples or public docs use command semantics for
  Stage 1 helpers.
- Future-roadmap compatibility evidence: Stage 2 can consume implemented docs or
  explicit deferrals; Stage 3 candidates remain deferred.
- Interface, adapter, or protocol reuse evidence: examples demonstrate project
  adapters and Python applications without CLI ownership by Weave.
- Documentation evidence: feature docs, behavior matrix, example coverage, and
  README snippets are aligned.
- Domain-neutrality evidence: examples avoid project-specific schemas, stages,
  datasets, metrics, reports, schedulers, and stores.

### Phase Workflow State

- Phase execution plan: pending
- Planning/refinement budget: pending
- Implementation/refinement budget: pending
- PR review budget: pending
- Blocker-resolution budget: pending
- Pre-submit blocker gate: Phases 1 through 3 merged
- Merge record: pending

### Risks And Stop Conditions

- Risks: docs overpromise unimplemented behavior; old command-first examples
  remain discoverable as current recommendations.
- Stop conditions: docs require behavior not implemented in prior phases or
  introduce first-party CLI claims.
- Assumptions: example harness can cover at least one project-owned adapter flow
  without adding new runtime dependencies.

### Completion Summary

- Implementation: pending
- Validation: pending
- PR: pending
- Merge: pending
- Follow-up: pending

## Cross-Phase Validation

- Full relevant test command: `make validate-pr` before preparing a PR.
- PR-body evidence command: `make test-summary` before writing a PR body.
- Focused commands:
  - parser/unit tests for commandless config args;
  - integration tests for fixed base, resolver base, warnings, raw snapshots,
    selected instantiation, and migration diagnostics;
  - package import-boundary tests;
  - example harness tests.
- Docs/template checks: behavior matrix, example coverage, feature docs,
  README snippets, roadmap Stage 1 plan/implementation consistency.
- Domain-neutrality checks: no domain recipes, schemas, metrics, datasets,
  reports, workflows, run stores, schedulers, or first-party CLI claims.
- Example/demo checks: runnable examples use explicit config args and project
  adapters.
- Manual review focus: commandless public contract, migration diagnostics,
  base-context serialization boundary, selected-instantiation object separation,
  absence of implicit `sys.argv` and full-config instantiation.

## Implementation Plan Review

| Finding | Severity | Resolution | Status |
| --- | --- | --- | --- |
| Initial plan left public helper/export policy to implementation. | blocker | Resolved by locking `compose_config_from_args(...)`, `inspect_config_args(...)`, retained old-helper migration diagnostics/commandless routing, and top-level export policy. | resolved; follow-up review passed |
| Initial plan allowed Phase 3 before Phase 2 in fixed-base-only cases. | concern | Resolved by requiring Phase 1 and Phase 2 merged before Phase 3. | resolved; follow-up review passed |
| Initial validation rows included placeholder checks. | note | Resolved by naming Make targets and suite locations for focused validation. | resolved; follow-up review passed |

Gate result:

- Status: passed
- Review evidence: initial `weave_plan_reviewer` review blocked; required revisions were incorporated; follow-up `weave_plan_reviewer` review passed with no remaining blocker
- Accepted risks:
  - Public API naming lock-in.
  - Command-first helper migration cost.
  - Selected dot-path ergonomics may need later refinement.
- Revisit triggers:
  - Release compatibility requires a separately named legacy command-first
    helper.
  - Real adapters need multiple coordinated base strategies.
  - Selected dot paths cannot cover common handoff workflows.
  - A concrete future command-semantics use case appears.

## Plan Quality Gate

Before the first phase starts:

- `weave_plan_reviewer` reviewed this implementation plan.
- Initial blocker findings were resolved in this document.
- Phase execution planning must use this implementation plan plus the confirmed
  roadmap-stage planning artifact as sources of truth.

## Final Approval

- Approval status: approved for Phase 1 execution planning
- Approved scope: four-phase Stage 1 implementation plan with Phase 1 commandless public contracts first
- Accepted risks: public naming lock-in, command-first migration cost, selected
  dot-path ergonomics revisit trigger
- Deferred items: command semantics, first-party CLI, implicit `sys.argv`,
  full-config instantiation, global search, workflow execution, persistence,
  Stage 3 behavior candidates, and domain-specific behavior
