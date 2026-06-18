# Roadmap Stage 1 Planning: Project Config Entrypoint Object

## Metadata

- Roadmap stage: v1
- Source roadmap: [`docs/roadmap.md`](../../roadmap.md)
- Previous version status: Stage 0 complete. The standalone config authoring
  baseline, argv shorthand, recipe catalog, inspection, artifact, and explicit
  target instantiation APIs are treated as locked compatibility inputs.
- Planning artifact status: confirmed
- Current discussion stage: implementation-plan drafting
- Stage gates:
  - Roadmap framing: complete; user agrees with the adapter-oriented framing,
    explicitly does not want Weave to own command semantics, confirms the
    project-owned argv boundary with a configured-base `config_args` style API,
    and later clarified that Stage 1 should remove command reliance from all
    planned helper contracts and migrate away from existing command-first helper
    behavior.
  - Intent discovery: complete; goals, non-goals, done criteria, result shape,
    selected-instantiation priority, and commandless helper constraint are
    confirmed.
  - Capability triage and candidate functional requirements: complete; user
    agrees with the include/defer/out-of-scope split.
  - Functionality agreement review: complete; the queue has no unresolved
    high-impact requirement questions after the commandless helper decision.
  - Functionality and behavior confirmation: complete; user confirmed the
    behavior baseline.
  - Context compaction/reset checkpoint: complete; planning resumed from the
    checkpoint before design-agreement review.
  - Design agreement review: complete; repo-supported recommendations were
    recorded directly and no unresolved high-impact design questions remain.
  - Design safety review: complete; reviewer passed the design with required
    planning revisions, all recorded in this artifact.
  - Examples and validation strategy: complete; coverage obligations are
    recorded and trace to confirmed behavior.
  - Phase shaping: complete; phase boundaries are recorded for implementation
    plan drafting.
  - Implementation readiness: complete; user confirmed the final planning artifact.
  - Handoff: complete; implementation-plan drafting authorized
- Related implementation plan: [implementation-plan.md](implementation-plan.md)
  has been drafted from this confirmed planning artifact and still needs its own plan-quality review.
- Related feature docs:
  - [`project-cli-argv.md`](../../features/project-cli-argv.md)
  - [`config-composition.md`](../../features/config-composition.md)
  - [`example-coverage.md`](../../features/example-coverage.md)
  - Supporting references:
    [`config-behavior-matrix.md`](../../features/config-behavior-matrix.md)
    and [`../../GLOSSARY.md`](../../GLOSSARY.md)
- Blockers:
  - None for roadmap-stage planning; implementation-plan quality review remains pending in `implementation-plan.md`.

## Source Evidence

| Source | Relevant content | Used for | Notes |
| --- | --- | --- | --- |
| `AGENTS.md` | Domain neutrality, minimal imports, deterministic artifact behavior, local checks, and repository layout. | Planning constraints | Stage 1 must not add downstream project imports, heavyweight dependencies, or domain behavior. |
| `.codex/workflows/roadmap-stage-planning.md` | Interactive stage-planning workflow, artifact structure, gates, design-safety review, and implementation-plan handoff rules. | Workflow process | Stage 1 is currently between design agreement and design-safety review. |
| `.codex/templates/roadmap-stage-planning.md` | Required planning artifact sections: metadata gates, stage readbacks, workflow readback, queues, readiness, open questions, and handoff notes. | Artifact shape | Stage 1 planning has been reshaped to this template. |
| `.codex/prompts/roadmap-stage-planning-facilitate.md` | Startup briefing must read roadmap, linked docs, adjacent plans, and architecture before asking behavior or design questions. | Facilitation rules | Prompt names `docs/weave.md` and `docs/structure.md`; those files are absent in this repo. |
| `.codex/prompts/roadmap-stage-functionality-agreement.md` | Functionality queue must be drafted, repo-answerable branches resolved directly, and unresolved high-impact questions asked one at a time. | Functionality agreement process | Completed before the checkpoint. |
| `.codex/prompts/roadmap-stage-design-agreement.md` | Design queue must classify decisions as auto-approved candidates, recorded recommendations, needs discussion, or blocked before user review. | Design agreement process | Used for the resumed design pass. |
| `.codex/prompts/roadmap-stage-design-safety-review.md` | Design-safety review pressure-tests future-roadmap compatibility, interface genericity, and hidden coupling. | Next review gate | Pending after design agreement. |
| `docs/roadmap.md` | Stage 1 outcome is a reusable project config entrypoint object for downstream CLIs and Python applications. | Roadmap scope | Defines constructor options, argv modes, result data, selected instantiation, compatibility wrappers, docs, and examples. |
| `docs/architecture.md` | `weave` owns trusted config authoring, not workflow execution; import boundaries prohibit downstream project imports during ordinary package import. | Architecture constraints | Replaces absent `docs/structure.md` as current architecture source. |
| `docs/roadmap/stage-0/planning.md` | Baseline locks YAML composition, overlays, includes, recipes, interpolation, provenance, artifacts, raw snapshot opt-in, and explicit instantiation. | Compatibility obligations | Stage 1 must layer on top of these contracts. |
| `docs/roadmap/stage-0/implementation-plan.md` | Stage 0 delivered `compose_config_from_argv(...)`, `inspect_config_from_argv(...)`, `ComposedConfig`, artifact records, and examples. | Prior-plan evidence | Confirms existing helpers and boundaries that Stage 1 must preserve. |
| `docs/roadmap/stage-1/implementation-plan.md` | Existing draft plan suggests phases for public contracts, base resolution/argv modes, selected instantiation, docs/examples/hardening. | Draft adjacent evidence | Treated as draft input until planning gates are complete. |
| `docs/roadmap/stage-2/planning.md` | Stage 2 release hardening depends on Stage 1 status and documents a conditional policy for Stage 1 docs/example coverage. | Successor touchpoint | Stage 1 should leave docs, behavior matrix, and examples ready for Stage 2. |
| `docs/roadmap/stage-2/implementation-plan.md` | Release-hardening plan expects Stage 1 either complete or explicitly deferred for docs/example work. | Successor implementation risk | Stage 1 should not push unresolved API behavior into Stage 2. |
| `docs/features/project-cli-argv.md` | Current argv shape is command-first; scoped overlays and helper-local warnings are documented. | Current public behavior to revise | Stage 1 should migrate public helper contracts away from command-first argv rather than rely on that shape. |
| `docs/features/config-composition.md` | Composition is Python-API owned, persistence-free, domain-neutral, artifact-safe by default, and explicit for trusted target instantiation. | Package-level constraints | Stage 1 should not change composition order or persistence policy. |
| `docs/features/example-coverage.md` | Runnable examples must be domain-neutral and avoid promising first-party CLI, workflow execution, remote sources, or implicit persistence. | Example scope | Stage 1 should add adapter-style example coverage only after behavior is confirmed. |
| `docs/features/config-behavior-matrix.md` | Matrix records coverage expectations for argv shorthand, target instantiation, import boundaries, artifacts, and raw snapshot opt-in. | Validation scope | Stage 1 should extend coverage without weakening existing rows. |
| `docs/GLOSSARY.md` | Preferred terms include authored config, composed config, source artifact, raw source snapshot, target, and argv scoped overlay. | Vocabulary | Planning uses glossary terms. |
| `src/weave/__init__.py` | Top-level public symbols are lazily resolved to keep ordinary `import weave` lightweight. | Import-boundary design input | Any new public object must fit the lazy export pattern. |
| `src/weave/api.py` | Defines `ComposedConfig`, argv result dataclasses, `compose_config_from_argv(...)`, `inspect_config_from_argv(...)`, and `instantiate(...)`. | Current public API shape | Stage 1 likely adds a configured object and result type near this API surface. |
| `src/weave/_argv.py` | Currently parses command, base config path, value overrides, scoped overlays, and unparsed args into structured records. | Existing parser implementation to revise or adapt | Stage 1 should reuse parsing logic where useful, but the target helper contract must not require command. |
| `src/weave/instantiate/recursive.py` | `instantiate(...)` recursively constructs trusted `_target_` graphs with explicit runtime injection. | Selected instantiation behavior | Stage 1 should call explicit instantiation only when configured. |
| `tests/unit/config/test_argv.py` | Covers parser classification, scoped overlay candidates, passthrough handling, structured errors, and missing overlay diagnostics. | Compatibility tests | Existing behavior remains locked. |
| `tests/integration/config/test_compose_argv_from_cli.py` | Covers public argv composition result shape, sys.argv defaulting, helper-local warnings, raw snapshots, recipe ordering, and structured errors. | Public compatibility tests | Stage 1 must not regress function-level helpers. |
| `tests/integration/config/test_compose_argv_scoped_overlays.py` | Covers argv scoped overlay composition order, provenance/artifacts, raw snapshot opt-in, and merge errors. | Composition order tests | Configured object should route through the same composition path. |
| `examples/project-cli-argv/README.md` | Shows a project-owned CLI adapter using `compose_config_from_argv(...)`; explicitly states no first-party CLI executable. | Example baseline | Stage 1 can extend this adapter pattern without promising a bundled command. |

## Exploration Coverage

| Area | Files or patterns checked | Findings | Gaps |
| --- | --- | --- | --- |
| Roadmap and architecture docs | `docs/roadmap.md`, `docs/architecture.md`, `docs/roadmap/stage-{0,1,2}/*.md` | Stage 1 is a focused configured-object layer between function-level argv helpers and downstream CLI adapters. | `docs/weave.md` and `docs/structure.md` are absent despite being named by the workflow prompt. |
| Feature docs | `docs/features/project-cli-argv.md`, `docs/features/config-composition.md`, `docs/features/example-coverage.md`, `docs/features/config-behavior-matrix.md`, `docs/GLOSSARY.md` | Existing docs lock argv shape, artifact-safe defaults, no first-party executable, and explicit target instantiation. | Stage 1 entrypoint behavior is not yet documented because the API is not implemented. |
| Source and tests | `src/weave/__init__.py`, `src/weave/api.py`, `src/weave/_argv.py`, `src/weave/instantiate/recursive.py`, `tests/unit/config/test_argv.py`, `tests/integration/config/test_compose_argv_from_cli.py`, `tests/integration/config/test_compose_argv_scoped_overlays.py`, `examples/project-cli-argv/README.md` | Existing argv helpers already return structured metadata and compose through the locked composition path. Public exports are lazy. | No configured entrypoint object or selected-instantiation result model exists yet. |
| Prior or adjacent plans | Stage 0 planning/plan, Stage 1 draft plan, Stage 2 planning/plan | Stage 0 provides prerequisites; Stage 2 depends on Stage 1 docs/example state. | Stage 3 only affects deferral boundaries through the top-level roadmap. |

## Roadmap Extraction

Baseline roadmap outcome:

- Add a project-owned config entrypoint object that downstream CLIs and Python
  applications can configure once, then use to compose argv shorthand into a
  full `ComposedConfig` without reimplementing base config selection, warning
  handling, passthrough arguments, recipe catalog selection, raw source
  snapshot policy, or optional trusted target instantiation.

Prerequisites:

- Stage 0 composition, inspection, argv shorthand, recipes, artifacts, raw
  snapshot opt-in, and explicit `instantiate(...)` behavior remain stable.
- Existing command-first `compose_config_from_argv(...)` and
  `inspect_config_from_argv(...)` behavior is treated as legacy/current
  behavior to migrate away from or isolate behind compatibility. It is not a
  target dependency for Stage 1 helper contracts.
- Public exports continue to respect lightweight `import weave`.

Primary feature docs:

- `docs/features/project-cli-argv.md`
- `docs/features/config-composition.md`
- `docs/features/example-coverage.md`

Deferred or out-of-scope roadmap work:

- First-party executable, full CLI parser ownership, process exit policy,
  terminal formatting, and command-specific flags.
- Global config guessing, implicit search paths, package-level project-root
  discovery, or default config names.
- Default target instantiation, default resolved snapshot persistence, or
  default raw source persistence.
- Workflow execution, queues, schedulers, run stores, stages, sweeps, reports,
  datasets, metrics, schemas, or domain recipes.
- New argv shorthand syntax beyond the Stage 0 scoped overlay and value
  override behavior.
- Deferred Stage 3 candidates such as remote/plugin include resolution,
  `_copy_`, schema registries, custom include resolvers, broader resolver
  execution, Hydra bridges, and first-party CLI behavior.

Future-roadmap touchpoints:

- Stage 2 needs Stage 1 docs, behavior-matrix rows, and example coverage once
  the entrypoint object is implemented.
- Stage 3 deferred behavior should remain clearly outside the entrypoint
  contract so the configured object does not become an implicit extension host
  for search paths, remote stores, schedulers, or project schemas.
- Future downstream adapters may consume the result object, so public result
  fields and failure semantics should be generic and stable.

Compatibility obligations:

- Remove command reliance from the target helper contracts, including the
  planned configured object and any revised function-level helpers.
- Provide an explicit migration or compatibility story for current command-first
  argv helpers, without using command-bearing behavior in new examples or
  planned APIs.
- Preserve scoped overlay ordering: argv scoped overlays apply before recipe
  expansion; ordinary value overrides apply after recipe expansion.
- Preserve helper-local warnings and keep them out of normal composed config
  artifacts.
- Preserve raw source snapshot opt-in and metadata-only source artifacts by
  default.
- Preserve inert composition: no `_target_` import or object construction
  unless selected instantiation is explicitly requested.
- Preserve lightweight top-level import behavior and avoid importing downstream
  project code during ordinary import or composition.

## Stage Briefing

What this stage is:

- Stage 1 is a public Python API addition for downstream projects that already
  own their CLI or application entrypoint. It should provide one configured
  object that carries project-level defaults such as base config selection,
  passthrough policy, recipe catalog, raw source snapshot policy, and optional
  selected target instantiation. Callers use the object to
  compose argv shorthand into a `ComposedConfig` and associated argv metadata.

Why this stage exists:

- Stage 0 gave projects function-level APIs and a compact argv shorthand, but a
  downstream CLI still has to repeatedly pass or resolve the base config,
  recipe catalog, passthrough policy, and any post-composition instantiation
  behavior. Stage 1 closes that adapter gap without making
  `weave` a CLI framework or workflow engine.

Impacted or linked work:

- The public API surface likely expands in `src/weave/api.py` and lazy exports
  in `src/weave/__init__.py`.
- The existing `_argv.py` parser and argv composition helpers are likely reused
  so compatibility is inherited rather than reimplemented.
- Target instantiation remains the trusted, explicit behavior implemented by
  `instantiate(...)`; Stage 1 may coordinate selected calls but should not
  change target semantics.
- Feature docs and the `project-cli-argv` example will need updates after
  behavior is confirmed.
- Stage 2 release hardening depends on whether Stage 1 docs/example coverage is
  complete or explicitly deferred.

Likely public surfaces and durable artifacts:

- Public Python classes or dataclasses for the configured object and its result.
- Constructor options for fixed `base_config_path`, caller-supplied base
  resolution through generic project-owned context, `allow_unparsed`,
  `RecipeCatalog` or default catalog behavior, raw source snapshot opt-in, and
  selected instantiation policy.
- Methods for composing argv, and possibly inspection-oriented behavior, that
  return `ComposedConfig`, parsed argv metadata, helper-local warnings,
  passthrough/unparsed args, selected object results, and base-resolution
  metadata.
- No new persisted file format is expected. Existing artifact records may be
  referenced through `ComposedConfig`, but the configured object should not
  persist resolved configs, raw sources, or object instances.

Structure rationale:

- The stage is appropriately narrow because it has one primary user-visible
  outcome and one package cluster: a reusable adapter object over existing
  config composition, argv parsing, and optional instantiation behavior.
- The workflow should first confirm the adapter intent and optimization
  priority, then triage capabilities, then lock functional requirements and
  behavior, then review design decisions such as object/result naming,
  base-resolution contract, method shape, and selected-instantiation selector
  shape.
- The implementation plan should remain a later artifact because public
  contract details have not yet been confirmed through functionality agreement,
  behavior confirmation, design agreement, and design-safety review.

Visible assumptions, risks, and constraints:

- Assumption: the entrypoint object should be useful for both CLI adapters and
  Python applications, but it should not own argparse, terminal output, process
  exits, project commands, or project-specific flags.
- Assumption: "automatic start" means configured base selection through a fixed
  path or caller resolver, not package-level config search.
- Assumption: the target Stage 1 contract should be commandless config
  arguments plus explicit base selection. The current command-first argv shape
  is a legacy/current behavior to migrate away from, not a design dependency.
- Risk: selected instantiation could blur the composition/target-construction
  boundary unless the default remains no instantiation and selected/full-config
  modes are explicit.
- Risk: a resolver interface that is too narrow could force redesign for
  project-specific base selection; a resolver interface that is too broad could
  make `weave` own CLI semantics or project policy.
- Risk: public result fields need enough metadata for downstream adapters
  without freezing implementation details that should remain helper-local.
- Constraint: ordinary `import weave` must stay lightweight and must not import
  downstream project modules.
- Constraint: docs and examples must remain domain-neutral and must not imply a
  bundled `weave` command.

User clarification questions and resolved answers:

- User agrees with most of the startup framing and clarified that Weave should
  not own command semantics.
- User wants Stage 1 to shore up the best interaction model for external
  projects: how projects pass the config-relevant argument list, how base config
  selection is separated from project-owned argument parsing, how composed config and
  optional instantiated objects come back, and how unparsed or passthrough items
  are preserved.
- Confirmed: for variable-distance project argv, downstream projects identify
  the config-relevant slice or pass config args separately. Weave parses only
  that supplied list and returns unparsed items from that list. Weave should not
  scan arbitrary project argv to infer command boundaries.
- Confirmed coding-level shape: a configured object should support a
  `compose_args(...)` style entrypoint where the project supplies
  `config_args=[...]` plus configured or explicit base context, and the result
  returns `ComposedConfig`, parsed argv metadata, helper-local warnings,
  passthrough/unparsed items, and optional instantiated objects.
- Intent clarification: Stage 1 should remove command reliance from all helper
  contracts. No planned or revised helper should require command, expose command
  as required metadata, or use command-specific behavior as its base-resolution
  model. Command-like context can be added later only if a concrete use case
  justifies a new design.

## User Intent

Target audience:

- Confirmed for roadmap framing. Primary audience is maintainers of trusted
  downstream projects who want a small project-owned CLI or application adapter
  around `weave` configuration composition.
- User emphasis: external project integration should be straightforward without
  transferring command semantics to Weave.

User-visible outcome:

- Confirmed for roadmap framing. A project configures one object once, then
  calls it with config-relevant args to receive composed config, parsed argv
  metadata, helper-local warnings, passthrough args, and optionally selected
  trusted instantiated objects.
- Confirmed API-boundary direction: Stage 1 should add a configured-base
  `config_args` style entrypoint for project-supplied config argument lists,
  while preserving the current full Weave-shaped argv helpers for compatibility.
- Updated intent: command should not be part of the Stage 1 helper contract.
  Stage 1 should avoid command-shaped parameters, command choices, command
  result fields, and command-specific resolver behavior.

Success criteria:

- Include fixed-base composition with no command required.
- Include caller-resolver base composition using generic project-owned context,
  without command-specific API.
- Include passthrough/unparsed args, helper-local warnings, raw source snapshot
  opt-in, selected instantiation, and one runnable project-owned adapter example.
- Define a migration or compatibility path for existing command-first argv
  helpers without relying on command in new helper behavior.

Non-goals:

- Confirmed defaults: no first-party executable, no command semantics ownership,
  no argparse ownership, no domain flags or schemas, no global search paths, no
  default instantiation, no workflow execution, and no persistence policy.

Constraints:

- Confirmed defaults: preserve domain neutrality, artifact-safe defaults,
  explicit trusted code execution, lightweight imports, and project-owned argv
  boundaries.


## Workflow Stage Readback

Record an explicit narrative readback before or after any context checkpoint so
later passes can resume without rediscovering what was already confirmed.

Roadmap framing locked decisions:

- User agrees with the adapter-oriented framing.
- Locked: Weave must not own command semantics, discover project commands,
  require command tokens, validate command choices, or infer arbitrary project
  argv boundaries.
- Locked: variable-distance project argv is handled by explicit project-owned
  slicing or separate `config_args`; Weave parses only the supplied config arg
  sequence and returns unparsed items from that sequence.
- Locked: Stage 1 should add a configured-base `compose_args(...)` style API
  and revise or isolate existing command-first helper behavior so planned APIs
  do not rely on command.
- Repo-supported default remains to treat Stage 1 as a configured object over
  existing argv composition and optional explicit target instantiation, not as a
  CLI framework, executable, persistence layer, or new config behavior stage.

Intent discovery locked decisions:

- Confirmed: Stage 1 should optimize for straightforward external project
  integration while preserving a minimal, stable API boundary.
- Confirmed: the canonical success case is a project passing `config_args` to a
  configured object and receiving a structured result.
- Confirmed: selected instantiation is part of the done bar, but remains
  opt-in and separate from composition.
- Confirmed: result data should be plain-data friendly for adapter logging or
  JSON where practical, except `objects`, which may contain arbitrary Python
  instances.
- Confirmed: command context is deferred entirely. Stage 1 should not model it
  as a nullable field, label, resolver input, or result field.

Capability triage and candidate-functional-requirement readback:

- Confirmed include: configured object, fixed `base_config_path`, generic
  caller-provided base resolver without command semantics, commandless
  `compose_args(config_args)`, passthrough/unparsed args, helper-local warnings,
  recipe catalog/default catalog behavior, raw source snapshot opt-in,
  structured result object, and selected instantiation.
- Confirmed defer: full-config instantiation unless selected instantiation
  proves insufficient; any command semantics or command-shaped context.
- Confirmed out of scope: first-party CLI, argparse ownership, global config
  search, project-root discovery, domain schemas, workflow execution, and
  persistence policy.

Functionality-agreement readback:

- Confirmed requirement set: commandless configured object, explicit fixed base
  config, generic caller-provided base resolver, explicit project-owned config
  arg sequence, passthrough/unparsed handling, helper-local warnings, recipe
  catalog/default catalog behavior, raw source snapshot opt-in, structured
  result object, and optional selected instantiation.
- Confirmed deferrals: command semantics, command-shaped context, command
  choices, command-specific resolver API, and full-config instantiation unless
  selected instantiation proves insufficient.
- Confirmed out of scope: first-party CLI, argparse ownership, global config
  search, project-root discovery, domain schemas, workflow execution,
  persistence policy, and Stage 3 configuration behavior candidates.
- Design-only follow-ups: final object/result names, resolver context shape,
  selected-instantiation selector model, and exact serializable result metadata.

Functionality and behavior confirmation readback:

- Confirmed behavior baseline: projects pass explicit `config_args`; Weave does
  not parse full project argv.
- Confirmed defaults: no command requirement, command token, command choices,
  command-shaped resolver input, or command result field; no first-party CLI;
  no argparse ownership; no global search; no target instantiation by default;
  no raw source snapshots by default; no resolved config persistence by default.
- Confirmed included behavior: configured object, fixed base, generic resolver,
  project-owned config-arg sequence, passthrough/unparsed args, helper-local
  warnings, recipe catalog/default catalog behavior, raw snapshot opt-in,
  structured result, selected instantiation, and migration/compatibility story
  for current command-first argv helpers.
- Confirmed failure behavior: fail closed on invalid constructor/base selection,
  malformed config args, missing scoped overlays, disallowed unparsed args,
  composition errors, and selected-instantiation failures with structured
  diagnostics.
- Confirmed deferrals and exclusions: command semantics, command-shaped context,
  command choices, command-specific resolver APIs, full-config instantiation,
  first-party CLI, CLI framework ownership, global search, new config syntax,
  workflow execution, persistence policy, Stage 3 behavior candidates, domain
  behavior, and untrusted-config sandboxing.

Design-agreement readback:

- Resumed from checkpoint and completed the design-agreement review without
  reopening functionality or behavior.
- Recorded repo-supported recommendations directly rather than asking the user
  to reconfirm settled constraints.
- Locked design direction: `ConfigEntrypoint`-style public object, commandless
  `config_args`, commandless parser/helper migration, generic base resolver
  request/resolution records, separate `compose_args(...)` and
  `inspect_args(...)`, selected dot-path instantiation, stable result metadata
  with `objects` kept out of plain-data export, lazy exports, fail-closed
  diagnostics, and docs/examples that avoid command semantics.
- No unresolved high-impact design questions remain before design-safety review.

## Stage Readbacks

| Stage | Locked decisions | Defaults | Open questions | Next focus |
| --- | --- | --- | --- | --- |
| Roadmap framing | Adapter-oriented framing accepted; Weave must not own command semantics; project-owned config arg boundary confirmed. | Configured object over existing composition/argv APIs; project owns argv boundaries; no first-party CLI; no default instantiation or persistence. | None for roadmap framing. | Intent discovery: goals, non-goals, done criteria, and constraints. |
| Intent discovery | Goals, non-goals, done criteria, result behavior, selected-instantiation priority, and commandless helper constraint confirmed. | Optimize external project integration while preserving a minimal stable API boundary; command is removed from the Stage 1 helper contract. | None for intent discovery. | Capability triage and candidate functional requirements. |
| Capability triage and candidate functional requirements | Included, deferred, and out-of-scope capability split confirmed. | Include configured object, fixed base, generic resolver, commandless config args, passthrough/warnings, catalog, raw snapshot opt-in, structured result, and selected instantiation. | None for capability triage. | Functionality agreement review. |
| Functionality agreement review | Requirement set confirmed with no unresolved high-impact functionality questions. | Commandless helpers, explicit base selection, project-owned config args, structured results, and selected instantiation are included. | None for functionality agreement. | Functionality and behavior confirmation. |
| Functionality and behavior confirmation | Behavior baseline confirmed by user. | Commandless config args, explicit base selection, structured result, selected instantiation opt-in, and command-first helper migration story. | None for behavior confirmation. | Context checkpoint and reset/resume before design review. |
| Context compaction/reset checkpoint | Checkpoint written and resumed. | Planning artifact is the source of truth for design review. | None. | Design agreement review. |
| Design agreement review | Proposed implementation shape drafted; design queue classified and resolved. | Record repo-supported recommendations directly; ask no settled-command questions. | None. | Design-safety review. |
| Design safety review | Passed with required revisions recorded. | Future-roadmap compatibility and genericity were challenged. | None. | Examples, validation strategy, and phase shaping. |
| Examples and validation strategy | Example and validation rows confirmed. | Examples remain project-owned adapter examples using explicit config args. | None. | Phase shaping. |
| Phase shaping | Four phase boundaries confirmed. | Existing draft implementation-plan stale items must be revised during plan drafting. | None. | Implementation readiness. |
| Implementation readiness | Ready for final planning confirmation. | No unresolved high-impact functionality or design questions remain. | Final planning confirmation. | Handoff. |
| Handoff | Complete; user confirmed final planning and authorized implementation-plan drafting. | Implementation plan should use this artifact as source of truth. | None. | Draft/update implementation plan. |

## Capability Triage

Capability decisions below are confirmed for Stage 1 scope unless a later
functionality or design review explicitly reopens them.

| Capability | Decision | Rationale | Notes |
| --- | --- | --- | --- |
| Configured object with explicit constructor state | include | This is the stage's primary outcome. | Keep configuration explicit and avoid package-global discovery. |
| Fixed base config path | include | Simplest configured-base workflow and required for commandless use. | Must support path-like inputs consistently with existing composition APIs. |
| Caller-provided base resolver without command semantics | include | Some projects may need dynamic base selection, but resolver input should be generic project-owned context rather than command. | Resolver shape moves to design agreement. |
| Passthrough policy without command choices | include | Existing helper supports unparsed args; Stage 1 should preserve passthrough handling while removing command choices from the target contract. | Preserve unparsed arg records without command semantics. |
| Recipe catalog/default catalog behavior | include | Existing compose helpers accept explicit catalogs or default catalog behavior. | Must not import project recipe plugins at ordinary import time. |
| Raw source snapshot opt-in | include | Existing behavior is opt-in and must remain artifact-safe by default. | Constructor or call-level override moves to design agreement. |
| Configured-base config args without base token | include | Stage 1's adapter value is avoiding repeated base path tokens when configured state can supply them. | Must not require a command token. |
| Result object preserving metadata and `ComposedConfig` | include | Downstream adapters need structured records rather than human output. | Boundary between standardized and helper-local metadata moves to design agreement. |
| Optional selected instantiation | include | User confirmed selected instantiation is part of the done bar. | Default remains no instantiation; selector shape moves to design agreement. |
| Full-config instantiation | defer | Higher risk because it can construct broad object graphs and selected instantiation should satisfy the Stage 1 use case first. | Revisit only if selected instantiation proves insufficient. |
| Command semantics or command-shaped context | defer | User explicitly removed command reliance from Stage 1 helper contracts. | Revisit in a later stage only with a concrete need. |
| First-party CLI executable | out of scope | Roadmap and feature docs repeatedly exclude this. | Keep project adapters downstream-owned. |
| Argparse ownership | out of scope | Weave should not own project command-line parsing. | Project adapter responsibility. |
| Global config search or implicit project-root discovery | out of scope | Roadmap explicitly excludes guessing global config names/search paths. | Configured base path or resolver is the supported automatic path. |
| Domain schemas, workflow execution, persistence policy, or Stage 3 config behavior candidates | out of scope | These belong to downstream projects or later roadmap gates. | Avoid mixing `_copy_`, remote includes, schema hooks, workflow execution, or persistence into Stage 1. |

## Functionality Agreement Queue

| ID | Requirement or decision | Depends on | Resolution order | Recommended answer | Why it matters | Why user input is needed | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FRQ-1 | Confirm whether the configured object should optimize primarily for downstream CLI adapters, Python applications, or both. | roadmap framing | 1 | Support both, with CLI adapters as the primary documented example. | This sets result metadata, method naming, examples, and docs emphasis. | User priority is answered: external project interaction and command-boundary clarity matter most. | confirmed |
| FRQ-2 | Lock the configured-base behavior: fixed path and caller resolver supply the base; no global search or command semantics. | FRQ-1 | 2 | Include fixed path and generic resolver; exclude search paths, guessed names, command tokens, command choices, and command-specific resolver APIs. | Base selection is the main new behavior and a public contract. | User explicitly removed command reliance; resolver details move to design agreement. | confirmed |
| FRQ-3 | Lock the argument-boundary model for variable-distance project argv. | FRQ-1, FRQ-2 | 3 | Project owns argv parsing and passes either a config-args slice or separate config args; Weave parses only that supplied sequence and returns unparsed items from it. | This is the core adapter boundary and prevents Weave from owning command semantics. | User confirmed this as the coding-level direction. | confirmed |
| FRQ-4 | Lock selected instantiation scope and defaults. | FRQ-1 | 4 | No instantiation by default; selected instantiation included; full-config instantiation deferred unless selected instantiation proves insufficient. | This protects composition inertness and trusted code execution boundaries. | User agreed selected instantiation is part of the done bar; selector shape moves to design agreement. | confirmed |
| FRQ-5 | Lock result metadata boundary. | FRQ-1, FRQ-2, FRQ-3, FRQ-4 | 5 | Preserve base metadata, parsed config-arg metadata, warnings, unparsed args, `ComposedConfig`, and optional objects; do not include command as a planned result field. | Downstream adapters need structured data without exposing unstable internals. | User agreed result should be plain-data friendly except `objects`; exact metadata shape moves to design agreement. | confirmed |

## Functional Requirements

| ID | Requirement | Depends on | What | Why | Scope | User-visible behavior | System behavior | Capability enabled | Validation idea | Decision/status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FR-1 | Configured entrypoint object | none | Provide one public configured object for repeated composition calls. | Reduces downstream adapter boilerplate without adding a first-party CLI. | Constructor state and compose/inspect calls only. | Project code configures the object once and reuses it. | Reuses existing composition and argv helpers. | Fixed-base and default-option tests. | confirmed |
| FR-2 | Explicit base config selection | FR-1 | Support fixed base path and caller-provided resolver with generic project-owned context. | Lets adapters omit repeated base path tokens without package-level guessing or command concepts. | No global search, default names, project-root inference, command tokens, command choices, or command-specific resolver API. | Fixed-base `compose_args(...)` works without a command; resolver-base usage receives generic caller context only if needed. | Produces structured errors for missing/ambiguous base selection. | Fixed-base commandless tests plus resolver success/failure and missing base tests without command. | confirmed |
| FR-3 | Explicit project-owned argument boundary | FR-1, FR-2 | Accept a project-supplied config-args sequence or config-relevant argv slice rather than scanning arbitrary full project argv. | Handles variable-distance config args while keeping command semantics downstream-owned. | Weave parses only the supplied sequence and may return unparsed items from that sequence; project flags outside that sequence are project-owned. | External projects can parse their own argv/options and hand Weave the remaining config args. | Configured object builds the effective parse input from configured base selection plus supplied config args, then routes through existing argv behavior. | Tests for separate config args, explicit argv compatibility, and mixed unparsed items inside the supplied sequence. | confirmed |
| FR-4 | Commandless helper migration and passthrough | FR-1 | Revise planned and function-level helper behavior toward commandless config-argument parsing while preserving passthrough args, scoped overlays, warnings, and carefully scoped migration coverage for legacy command-first helpers. | Removes command reliance from helper contracts while protecting existing users through an explicit migration story. | No new shorthand syntax and no command choices. | New helper behavior is commandless; any retained legacy command-first path is compatibility-only and not used by new examples. | Configured object routes through commandless parser/composition behavior, reusing existing parsing logic where safe. | Commandless helper tests plus migration/compatibility tests for any retained legacy path. | confirmed |
| FR-5 | Recipe catalog and raw snapshot policy | FR-1 | Carry explicit `RecipeCatalog` or default catalog behavior and raw source snapshot opt-in through the object. | Matches existing composition options. | No default raw source bytes or plugin import at ordinary import time. | Callers can set policy once. | Existing artifact-safe defaults remain unchanged. | Catalog and raw snapshot opt-in tests. | confirmed |
| FR-6 | Optional selected instantiation | FR-1 | Optionally instantiate selected target values after composition. | Supports common downstream handoff without making composition execute targets. | No instantiation by default; full-config instantiation deferred. | Result includes selected objects separately from `ComposedConfig`. | Calls `instantiate(...)` with runtime injection only when requested. | Selected path, runtime injection, deferred full-config, and no-import-default tests. | confirmed; selector shape resolved in design agreement |
| FR-7 | Structured result model | FR-1, FR-2, FR-3, FR-4, FR-6 | Return base metadata, parsed config-arg metadata, warnings, passthrough args, `ComposedConfig`, and optional objects; no command field is part of the Stage 1 target. | Downstream adapters need machine-readable results. | Keep persistence caller-owned; `objects` may contain arbitrary Python instances and is not plain-data. | Result can be inspected or converted to plain-data where practical except for instantiated objects. | Mirrors existing argv result validation patterns while allowing commandless configured-base usage. | Result-shape, commandless serialization, and objects-excluded/plain-data tests. | confirmed; exact metadata shape resolved in design agreement |

## Behavior Baseline

Status:

- Confirmed by user.

Included functionality:

- Public configured object for repeated composition calls.
- Fixed-base commandless `compose_args(config_args)` behavior.
- Generic caller-provided base resolver without command semantics.
- Explicit project-owned config-argument sequence; no scanning full project
  argv.
- Passthrough/unparsed args from the supplied config-argument sequence.
- Helper-local warnings that remain outside normal composed config artifacts.
- Recipe catalog/default catalog behavior.
- Raw source snapshot opt-in.
- Structured result with base metadata, parsed config-arg metadata, warnings,
  unparsed args, `ComposedConfig`, and optional `objects`.
- Optional selected instantiation, disabled by default.
- Migration or compatibility story for current command-first argv helpers.

User-visible behavior:

- A project configures the object once and passes only config-relevant args.
- The result always includes the composed config and metadata useful to adapters.
- Unparsed items come only from the supplied config-argument sequence.
- Instantiated objects, when requested, are returned separately from the composed
  config and from plain-data-friendly metadata.

Default behavior:

- No command requirement, command token, command choices, or command result
  field.
- No first-party executable or argparse ownership.
- No global config search or project-root discovery.
- No target instantiation by default.
- No raw source snapshots by default.
- No resolved config persistence by default.

Failure behavior and diagnostics:

- Invalid constructor combinations fail early with structured config validation
  errors.
- Missing, conflicting, or ambiguous base selection fails closed.
- Malformed config args, missing scoped overlay sources, disallowed unparsed
  args, and composition errors preserve structured path/source context.
- Selected instantiation failures use existing trusted target instantiation
  diagnostics.

Explicit deferrals:

- Command semantics, command-shaped context, command choices, and
  command-specific resolver APIs.
- Full-config instantiation unless selected instantiation proves insufficient.
- First-party executable, CLI framework ownership, global search paths, new
  config syntax, workflow execution, persistence policy, and Stage 3 behavior
  candidates.

Out-of-scope behavior:

- Domain-specific flags, schemas, recipes, datasets, metrics, reports, stages,
  queues, schedulers, run stores, or analysis behavior.
- Untrusted config sandboxing or plugin sandboxing.
- Remote include resolution, `_copy_`, schema hooks, Hydra bridges, or broader
  resolver execution.

Context compaction/reset checkpoint:

- Checkpoint status: written; reset/resume required before design review because
  direct context compaction is not available in this session.
- Notes path: `docs/roadmap/stage-1/planning.md`
- Resume instruction: continue Stage 1 roadmap-stage planning from
  `docs/roadmap/stage-1/planning.md` using
  `.codex/workflows/roadmap-stage-planning.md`. Start at design-agreement
  review. Treat functionality and behavior as confirmed. Reload
  `docs/roadmap.md`, `docs/architecture.md`, linked feature docs,
  adjacent stage docs, `.codex/prompts/roadmap-stage-design-agreement.md`, and
  `.codex/prompts/roadmap-stage-design-safety-review.md` before asking design
  questions.
- Functionality and behavior reopened after checkpoint: no

## Proposed Implementation Shape

Likely modules or packages:

- `src/weave/api.py` remains the public API home for the configured object,
  commandless result models, commandless function-level helpers, base-resolution
  records, selected-instantiation coordination, and plain-data exports.
- `src/weave/_argv.py` should extract or add a commandless parser path such as
  `parse_config_args(...)` that returns config-argument records without a
  command field. Existing token record classes for value overrides, scoped
  overlays, and unparsed args can be reused when they do not encode command
  semantics.
- `src/weave/__init__.py` should expose new public symbols through the existing
  lazy export mechanism.
- Documentation, example coverage, behavior-matrix rows, and argv tests should
  be updated to describe commandless config args as the Stage 1 target.

Likely public classes, functions, or protocols:

- `ConfigEntrypoint` as the reusable configured object.
- `ConfigArgsCompositionResult` and `ConfigArgsInspectionResult` as the
  commandless result models for `compose_args(...)` and `inspect_args(...)`.
- `ParsedConfigArgs` as the commandless parse record. It should carry
  `base_config_path`, value overrides, scoped overlays, and unparsed args, but
  no `command` or command-like nullable field.
- `ConfigBaseRequest` and `ConfigBaseResolution` as small resolver boundary
  records. The request carries generic caller-owned `base_context`; the
  resolution carries the selected base path plus optional plain-data details.
- Preferred commandless function-level helpers such as
  `compose_config_from_args(...)` and `inspect_config_args(...)` can mirror the
  configured object for callers that do not need reusable constructor state.
- Existing command-first helper names, if retained at all, should be migrated to
  the commandless contract or kept only as compatibility aliases to the
  commandless helpers. Stage 1 should not retain a public command-first parsing
  path.

Likely internal helpers:

- Commandless token normalization and parsing helpers shared by object and
  function-level APIs.
- Base-resolution validation that enforces exactly one base strategy per
  configured object: fixed `base_config_path` or `base_resolver`.
- A selected-path lookup helper over `ComposedConfig.resolved`.
- A selected-instantiation helper that calls `instantiate(...)` only for
  explicitly requested selections and returns object values separately from
  plain-data metadata.
- Result metadata builders that avoid freezing parser internals not already
  exposed as stable public records.

Data flow:

1. A downstream project parses its own CLI or application inputs and passes an
   explicit `config_args` sequence to `ConfigEntrypoint.compose_args(...)` or
   `inspect_args(...)`.
2. The entrypoint resolves the base config from its fixed constructor path or by
   calling `base_resolver(ConfigBaseRequest(base_context=...))`. The resolver
   does not receive command-specific inputs.
3. The commandless parser classifies only the supplied config args into scoped
   overlays, ordinary value overrides, and unparsed args.
4. Composition routes through the existing inspection path so scoped overlays
   still apply before recipe expansion and ordinary value overrides still apply
   after recipe expansion.
5. Helper-local warnings are computed from the commandless parse record and
   remain outside normal composed config artifacts.
6. `inspect_args(...)` returns inspection-oriented metadata. `compose_args(...)`
   converts that inspection to `ComposedConfig` and, only when selections are
   explicit, instantiates selected values from the composed resolved config.
7. The result returns structured metadata, `ComposedConfig` or inspection data,
   passthrough/unparsed args, warnings, and optional `objects` keyed by
   caller-selected names or selected dot paths.

Dependency direction:

- The public object depends only on package-local parsing, composition, recipes,
  artifacts, and explicit instantiation helpers.
- Ordinary `import weave` must not import downstream project modules. A
  base-resolver callable is invoked only during an explicit compose/inspect
  call, and target imports occur only through explicit selected instantiation.
- Stage 1 adds no runtime dependency and no package-global project discovery.

Extension points and flexibility boundaries:

- The supported extension point is base selection through a project-owned
  resolver. The resolver boundary is path-oriented and metadata-oriented, not a
  command, parser, scheduler, store, or workflow extension point.
- Selected instantiation is selector-oriented: callers identify specific dot
  paths and result keys. Stage 1 does not add schema registries, target
  discovery, workflow execution, or object persistence hooks.
- Raw source snapshots, recipe catalog choice, and unparsed-arg policy remain
  explicit constructor or call policies, preserving existing artifact-safe
  defaults.

Generic interface, adapter, or protocol shape:

- `ConfigBaseRequest` should be generic enough for CLI adapters and Python
  applications because it carries caller-owned context without naming commands,
  subcommands, argparse objects, scheduler state, stores, or domain concepts.
  `base_context` is opaque caller-owned input to the resolver and is never
  automatically serialized into result metadata.
- `ConfigBaseResolution` should be plain-data friendly so adapters can log why a
  base config was selected without serializing arbitrary project objects. Only
  explicit plain-data details returned by the resolver are included in
  `to_dict()`-style output.
- Selected-instantiation selectors should be plain strings or mappings of
  caller-selected names to dot paths, keeping the interface independent of any
  future executor or object store.

Future-roadmap impact:

- Stage 2 can document implemented Stage 1 behavior and update the behavior
  matrix without inventing planned APIs.
- Stage 3 candidates remain outside the contract: no remote include resolver,
  schema registry, `_copy_`, Hydra bridge, plugin composition hook, scheduler,
  run store, or first-party CLI behavior is implied by the entrypoint object.
- Future command-shaped context can be added later as a new design if a concrete
  use case justifies it, but Stage 1 does not reserve a nullable command field
  or command metadata slot.

Compatibility constraints:

- The command-first argv path is treated as behavior to migrate away from, not
  as a dependency. If old function names remain, Stage 1 preserves helper
  availability, not command-first semantics: retained names should use the
  commandless contract or provide targeted migration diagnostics for callers
  still passing `<command> <base-config> ...`.
- Existing composition order, structured config errors, helper-local warnings,
  raw source snapshot opt-in, artifact-safe defaults, and lazy package exports
  remain compatibility constraints.

## Design Agreement Queue

| ID | Decision | Depends on | Resolution order | Classification | Recommended answer | Why it matters | Why user input is needed | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DAQ-1 | Public object and result type naming | FR-1, FR-7 | 1 | recorded recommendation | Use `ConfigEntrypoint`, `ConfigArgsCompositionResult`, `ConfigArgsInspectionResult`, `ParsedConfigArgs`, `ConfigBaseRequest`, and `ConfigBaseResolution`. | Names become public API and should describe commandless adapter behavior without implying a first-party CLI. | Not needed; roadmap title, draft implementation source, and confirmed behavior all point to entrypoint plus config-args terminology. | confirmed |
| DAQ-2 | Commandless parser and function-level helper migration | FR-3, FR-4 | 2 | recorded recommendation | Add or extract commandless config-argument parsing; provide preferred commandless helpers such as `compose_config_from_args(...)` and `inspect_config_args(...)`; migrate any retained old helper names to the commandless contract with targeted migration diagnostics, not public command-first compatibility. | This removes command reliance from planned and existing helper behavior while preserving one parse/composition path. | Not needed; user explicitly confirmed command should be removed from all helper contracts and existing behavior. | confirmed |
| DAQ-3 | Base resolver callable contract and metadata | FR-2 | 3 | recorded recommendation | Constructor accepts exactly one base strategy: fixed `base_config_path` or `base_resolver`. The resolver receives `ConfigBaseRequest(base_context=...)` and returns a path or `ConfigBaseResolution`; no command or config-arg scan is part of the resolver contract. | Base selection is the largest reusable adapter boundary and must remain generic. | Not needed; the confirmed behavior requires project-owned context without command semantics. | confirmed |
| DAQ-4 | Method shape and default argument boundary | FR-1, FR-3, FR-7 | 4 | recorded recommendation | Expose separate `compose_args(config_args=(), ...)` and `inspect_args(config_args=(), ...)` methods. Do not default to `sys.argv[1:]`; callers pass explicit config args. Constructor defaults may be overridden only by explicit call policies where the design names the override. | Separate methods mirror existing compose/inspect behavior and protect the project-owned argv boundary. | Not needed; existing API separation and confirmed explicit config-args behavior give a clear default. | confirmed |
| DAQ-5 | Selected-instantiation selector model | FR-6 | 5 | recorded recommendation | Use selected dot paths, with an optional mapping of caller-selected result names to dot paths. A sequence shorthand may key objects by the dot path. Selected values are passed to existing `instantiate(...)`, so non-target plain values remain plain values. No full-config instantiation is included in Stage 1 unless a later requirement reopens it. | Selector shape controls trusted code execution scope and result stability. | Not needed; roadmap and behavior baseline already support selected dot-path instantiation and defer full-config instantiation. | confirmed |
| DAQ-6 | Result metadata standardization boundary | FR-7 | 6 | recorded recommendation | Standardize base resolution, raw `config_args`, `ParsedConfigArgs`, value overrides, scoped overlays, unparsed args, warnings, composed config or inspection, selected-object metadata, and object keys. Keep actual `objects` out of plain-data `to_dict()` output. | Adapters need stable structured records without serializing arbitrary Python objects or freezing internals. | Not needed; user confirmed plain-data-friendly metadata except `objects`. | confirmed |
| DAQ-7 | Lazy public export integration | FR-1 | 7 | auto-approved candidate | Add new symbols to the existing lazy `__init__.py` export pattern. | Preserves import boundaries and current package behavior. | Not needed; repo source already establishes this pattern. | confirmed; safety reviewer should challenge |
| DAQ-8 | Failure semantics and diagnostics | FR-2, FR-3, FR-6, FR-7 | 8 | recorded recommendation | Fail closed with structured `ConfigValidationError` or existing config errors for missing/conflicting base strategy, invalid resolver returns, malformed config args, disallowed unparsed args, missing selected paths, and instantiation failures. Reuse existing path/source context where possible, but new commandless parser diagnostics must not include command-shaped details or remediation. | Implementation-plan drafting needs stable failure boundaries and tests. | Not needed; behavior baseline already confirmed fail-closed diagnostics. | confirmed |
| DAQ-9 | Docs, examples, and behavior matrix placement | FR-4, FR-5, FR-6, FR-7 | 9 | recorded recommendation | Update `project-cli-argv` or successor docs, example coverage, behavior matrix, and project-owned adapter example only after the API lands; examples use explicit config args and never command semantics. | Stage 2 depends on honest docs/example coverage for implemented behavior. | Not needed; adjacent Stage 2 planning and feature docs provide a clear rule. | confirmed |

## Design Decisions

| ID | Decision | Selected approach | User feedback | Alternatives rejected | Rationale | Maintainability impact | Extensibility, flexibility, and expansion impact | Future-roadmap impact | Interface, adapter, or protocol impact | Validation/documentation obligation | Debt and revisit trigger | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DAQ-1 | Public object and result type naming | `ConfigEntrypoint`, `ConfigArgsCompositionResult`, `ConfigArgsInspectionResult`, `ParsedConfigArgs`, `ConfigBaseRequest`, and `ConfigBaseResolution`. | User previously confirmed the configured-base `config_args` style and commandless target. | `ConfigComposer` was rejected because selected instantiation makes the object broader than composition. Command or argv-named result types were rejected for the new target because they imply the old command-first shape. | Matches the roadmap's stage title and keeps config-argument terminology visible. | Clear names reduce duplicate wrappers and make docs easier to align. | Names leave room for downstream CLI and Python application adapters without encoding argparse or commands. | Does not reserve command fields for future work; future command support would need an explicit new design. | Public API names become stable and should be exported lazily. | API docs, import tests, result-shape tests, glossary/doc consistency. | Revisit only before implementation if maintainers choose different public names. | confirmed |
| DAQ-2 | Commandless parser and function-level helper migration | Add commandless parser/helper path and migrate retained function-level helper names to commandless behavior; do not keep public command-first compatibility as a Stage 1 target. | User explicitly asked to remove command reliance from planned and existing behavior. | Keeping `command_choices`, command result fields, nullable command metadata, or public command-first compatibility was rejected. | Avoids two semantic models and prevents new examples from relying on command-owned behavior. | Requires coordinated test/docs migration but leaves the package with one current helper contract. | Future command support can be added later as a separate API instead of being baked into every result. | Stage 2 docs can describe one supported commandless surface; Stage 3 remains unaffected. | Public function helpers become config-args oriented. | Migration diagnostics, old-doc cleanup, commandless unit/integration tests, and docs explaining the compatibility break if old invocations are no longer supported. | Accepted debt: old callers may need migration. Revisit only if release compatibility requires a separately named legacy helper. | confirmed |
| DAQ-3 | Base resolver callable contract and metadata | Exactly one constructor base strategy: fixed path or resolver. Resolver receives `ConfigBaseRequest(base_context=...)` and returns path or `ConfigBaseResolution`. | User confirmed base selection should be separate from command semantics. | Global search, project-root discovery, command choices, resolver(command=...), and resolver scanning arbitrary argv were rejected. | Keeps base selection explicit and project-owned. | A small resolver record is easier to test than broad parser integration. | Generic request/resolution records can grow later without naming commands, stores, schedulers, or schemas. | Does not block future search/path policy work because Stage 1 does not claim it. | Establishes the main adapter protocol for base selection. | Constructor validation tests, resolver success/failure tests, invalid return tests, metadata export tests. | Revisit if real adapters need multiple coordinated base strategies in one object. | confirmed |
| DAQ-4 | Method shape and default argument boundary | Separate `compose_args(...)` and `inspect_args(...)` methods over an explicit `config_args` sequence; no `sys.argv` default. | User confirmed projects pass explicit config args and Weave does not parse full project argv. | One method with mode flags, implicit `sys.argv[1:]`, and full-project-argv scanning were rejected. | Mirrors existing compose/inspect separation and protects caller-owned argv boundaries. | Keeps call paths understandable and testable. | Works for both CLI adapters and Python applications; adapters can choose how to slice args before calling Weave. | Future first-party CLI work, if any, would sit outside this object. | Public method contract is explicit and commandless. | Method-shape docs, default-empty args tests, no-sys-argv-default tests. | Revisit only if usage evidence shows separate inspect/compose methods create meaningful duplication. | confirmed |
| DAQ-5 | Selected-instantiation selector model | Mapping of caller-selected object names to dot paths, with sequence shorthand keyed by dot path; instantiate selected values only by passing them through existing `instantiate(...)`. Non-target plain values remain plain values. | User confirmed selected instantiation is in scope and full-config instantiation is deferred. | Default instantiation, full-config instantiation, automatic target discovery, target-only selected values, and schema-driven selectors were rejected. | Selected paths are the narrowest useful trusted execution boundary, and existing `instantiate(...)` semantics avoid inventing new target checks. | Keeps object construction isolated from composition internals. | Selector mapping can support future adapters without binding to an executor or object store. | Avoids pulling Stage 3 execution/storage behavior into Stage 1. | Adds a small selector interface over composed resolved config. | Selected path lookup tests, non-target selected value tests, runtime injection tests, no-instantiation-default import tests. | Revisit if selected paths cannot cover common handoff workflows. | confirmed |
| DAQ-6 | Result metadata standardization boundary | Stable result fields for base resolution, config args, parsed records, warnings, unparsed args, composed config or inspection, selected-object metadata, and object keys; actual `objects` excluded from plain-data export. | User confirmed results should be plain-data friendly except objects. | Serializing arbitrary object instances or exposing command fields/parser internals was rejected. | Gives adapters enough structured data while keeping Python instances separate. | Reduces accidental API lock-in around internal parser details. | Plain-data metadata can feed logs, tests, and docs without imposing persistence policy. | Stage 2 can document stable records; future stores remain downstream-owned. | Result models become the main adapter data contract. | Result `to_dict()` tests, object-exclusion tests, metadata shape docs. | Revisit if downstream adapters need additional stable metadata; add fields deliberately. | confirmed |
| DAQ-7 | Lazy public export integration | Follow existing `__init__.py` lazy optional symbol resolution. | None needed. | Eager imports and new package import side effects were rejected. | The current package already uses this pattern to preserve lightweight import. | Low implementation risk. | New symbols do not change project import boundaries. | Supports Stage 2 import-boundary checks. | Public export mechanism only. | Import-boundary tests and `__all__` checks. | Safety reviewer may overturn if new symbols require heavy imports. | auto-approved candidate |
| DAQ-8 | Failure semantics and diagnostics | Fail closed with structured diagnostics for invalid construction, base resolution, config args, unparsed args, composition, selected path lookup, and instantiation. New commandless parser errors include no command-shaped context or remediation. | User confirmed fail-closed behavior baseline. | Best-effort partial composition, silent fallback base selection, command-shaped errors, and unstructured exceptions were rejected. | Existing package behavior favors structured config errors and source/path context. | Clear failure boundaries make phase planning and tests tractable. | Diagnostics stay generic and do not encode CLI exit behavior. | Does not constrain future terminal presentation or process-exit policy. | Error shape is part of the adapter contract. | Unit/integration failure tests and docs examples for common errors. | Revisit if implementation finds an existing error type cannot carry required context. | confirmed |
| DAQ-9 | Docs, examples, and behavior matrix placement | Update feature docs, example coverage, behavior matrix, and project-owned adapter examples after implementation; no examples use command semantics. | User confirmed commandless target. | Documenting planned APIs as released behavior, first-party executable examples, and command-shaped adapter examples were rejected. | Keeps Stage 2 release docs honest and avoids stale command-first docs. | Concentrates docs migration in the hardening phase. | Examples remain domain-neutral and project-owned. | Stage 2 can include or defer Stage 1 docs based on implementation status. | Documentation contract for downstream adapters. | Example harness, behavior matrix update, feature-doc consistency review. | Revisit if Stage 1 slips and Stage 2 must record explicit deferrals. | confirmed |

## Design Agreement Triage

| Decision ID | Final classification | Reviewer challenge considered | Traceability | Manager action | Status |
| --- | --- | --- | --- | --- | --- |
| DAQ-1 | recorded recommendation | Public names could lock the wrong abstraction; `ConfigEntrypoint` remains closest to the roadmap title and confirmed adapter behavior. | FR-1, FR-7 | Safety reviewer checked; naming does not overpromise CLI ownership. | confirmed |
| DAQ-2 | recorded recommendation | Compatibility break may be costly; user explicitly confirmed removing command reliance from existing helper behavior. | FR-3, FR-4 | Safety reviewer challenged this; no discussion blocker, but a separately named legacy helper is the revisit trigger if release compatibility requires it. | confirmed |
| DAQ-3 | recorded recommendation | Resolver could become too narrow; generic request/resolution records avoid command coupling while leaving caller context open. | FR-2 | Safety reviewer verified the generic boundary with the added opaque `base_context` serialization rule. | confirmed |
| DAQ-4 | recorded recommendation | Explicit args may be more verbose; it is required by the confirmed project-owned boundary and avoids ambiguous sys.argv behavior. | FR-1, FR-3, FR-7 | Safety reviewer upheld the explicit `compose_args(...)`/`inspect_args(...)` method shape for CLI adapters and Python applications. | confirmed |
| DAQ-5 | recorded recommendation | Selected dot paths may be too narrow; they satisfy the current done bar and avoid premature executor/store behavior. | FR-6 | Safety reviewer upheld selected dot paths with the added non-target value behavior clarification. | confirmed |
| DAQ-6 | recorded recommendation | Too much metadata could freeze internals; selected stable fields map directly to confirmed result needs. | FR-7 | Safety reviewer upheld plain-data export and `objects` separation. | confirmed |
| DAQ-7 | auto-approved candidate | Existing lazy export pattern is low risk but import boundaries are non-negotiable. | FR-1 | Safety reviewer upheld lazy export integration. | confirmed |
| DAQ-8 | recorded recommendation | Failure coverage can be incomplete if not named now; behavior baseline already names fail-closed categories. | FR-2, FR-3, FR-6, FR-7 | Safety reviewer upheld fail-closed diagnostics with the added commandless error-context rule. | confirmed |
| DAQ-9 | recorded recommendation | Docs could promise behavior before implementation; Stage 2 already warns against this. | FR-4, FR-5, FR-6, FR-7 | Safety reviewer upheld docs/example phase boundaries. | confirmed |

## Design Safety Review

| Finding | Affected decision or requirement | Future-roadmap or compatibility risk | Interface, adapter, or protocol reuse risk | Recommended planning revision | Status |
| --- | --- | --- | --- | --- | --- |
| Design-safety reviewer passed the design gate. | All design decisions | No blocker found; remaining risk is migration cost from current command-first helpers. | Generic interface shape is acceptable if commandless records are distinct from current `ParsedConfigArgv` and result types. | Continue with validation strategy and phase shaping after recording reviewer revisions. | accepted |
| Preserve helper availability, not command-first semantics. | DAQ-2, FR-4 | Existing tests/docs currently encode `command`, `command_choices`, and command metadata. Treating those as compatibility requirements would contradict confirmed behavior. | New APIs need distinct commandless records such as `ParsedConfigArgs` and `ConfigArgsCompositionResult`; do not wrap existing command-bearing records unchanged. | Planning and phase shaping must require commandless records and targeted migration diagnostics for old invocation shapes. | recorded |
| `base_context` must stay opaque. | DAQ-3, FR-2, FR-7 | Serializing caller context could leak project objects or freeze project policy into result records. | Resolver context remains input-only; only explicit plain-data `ConfigBaseResolution.details` may appear in result metadata. | Record serialization boundary and validation coverage. | recorded |
| Selected non-target values should reuse `instantiate(...)` semantics. | DAQ-5, FR-6 | Requiring `_target_` mappings would invent stricter behavior and need maintainer discussion. | Passing selected values through `instantiate(...)` keeps non-target plain values plain and target mappings constructible. | Record selected-value behavior and validation coverage. | recorded |
| Commandless parser diagnostics must be commandless. | DAQ-8, FR-3, FR-4 | Reusing old parser context could leak command-shaped remediation into the new contract. | Parser errors should use config-args terminology and omit command details. | Add validation obligation for commandless error context/remediation. | recorded |
| Existing draft implementation plan has stale optional items. | Phase shaping | Draft text mentions optional `sys.argv[1:]` defaulting and optional full-config instantiation; confirmed planning rejects both for Stage 1. | Implementation-plan drafting must revise those draft inputs rather than carrying them forward. | Record in phase sketch and handoff notes. | recorded |

Gate result:

- Status: passed
- Reviewer: `weave_design_safety_reviewer`
- Blockers: none from design-safety review
- Auto-approved decisions upheld: DAQ-7 lazy public export integration
- Auto-approved decisions overturned: none
- Recorded recommendations: DAQ-1 through DAQ-6 and DAQ-8 through DAQ-9 upheld
  with the revisions above
- Future-roadmap impact summary: Stage 2 remains unblocked if docs/examples are
  implemented or explicitly deferred; Stage 3 remains protected because base
  resolution is path-oriented and not a general include resolver, search path
  registry, plugin loader, scheduler hook, store hook, schema hook, or workflow
  extension point.
- Generic interface, adapter, and protocol assessment: `ConfigBaseRequest`,
  `ConfigBaseResolution`, selected dot-path mappings, commandless parse/result
  records, and object/metadata separation are generic enough for CLI adapters
  and Python applications when the recorded boundaries are preserved.
- Planning revisions required: completed in this artifact.
- Accepted risks: public API naming lock-in and command-first helper migration
  cost.
- Revisit triggers: release compatibility requires a separately named legacy
  command-first helper; real adapters need multiple coordinated base strategies;
  selected dot paths cannot cover common handoff workflows; command semantics
  get a concrete future use case.

## Practical Design Notes

Public Python API surface:

- Planned public surface is `ConfigEntrypoint`, commandless config-args result
  and parse records, base resolver request/resolution records, and preferred
  commandless function-level helpers. Exact implementation details should be finalized during
  implementation-plan drafting from this confirmed planning source.

CLI surface:

- No first-party executable is planned. Downstream project adapters remain the
  CLI owner and pass explicit config args to Weave.

Persisted records and file layout:

- No new persistence is planned. Existing `ComposedConfig` artifact records
  remain caller-owned, and `objects` are not serialized by result `to_dict()`
  output.

Import boundaries and dependencies:

- Must preserve lightweight `import weave` and avoid downstream project imports
  except through explicit trusted recipe loading, caller-invoked base resolver
  callbacks, or selected target instantiation. No new runtime dependency is
  planned.

Failure modes and diagnostics:

- Fail closed for invalid constructor combinations, base resolution failures,
  malformed config args, disallowed unparsed args, composition errors, missing
  selected paths, and instantiation errors. Diagnostics should stay structured
  and commandless.

Extension points and flexibility boundaries:

- Base resolution is the only Stage 1 adapter extension point. It resolves a
  path from caller-owned context and optional plain-data metadata; it is not a
  parser, command, search, scheduler, store, or workflow hook.

Generic interfaces, adapters, and protocols:

- `ConfigBaseRequest`/`ConfigBaseResolution` and selected dot-path mappings are
  the reusable interface shapes. They intentionally avoid project command,
  executor, run-store, schema, and domain concepts.

Future-roadmap compatibility:

- Stage 1 must not absorb Stage 3 behavior candidates or make Stage 2 document
  unsupported behavior. Future command support, if needed, should be a new
  design rather than a hidden nullable command field in Stage 1 results.

Maintainability assessment:

- The design consolidates around one commandless parser/helper contract but
  accepts migration cost for existing command-first helper callers.

Extensibility assessment:

- The resolver and selected-instantiation shapes leave room for project-owned
  adapters without committing Weave to a CLI framework, executor, store, or
  schema registry.

Flexibility and expansion assessment:

- Callers can vary base selection through resolver context and vary selected
  objects through explicit dot-path mappings while composition remains inert by
  default.

Scalability and future compatibility:

- No new global search, persistence, or registry behavior is introduced; future
  expansion should add explicit APIs rather than widening Stage 1 semantics.

Accepted debt:

| Debt | Reason accepted | Revisit trigger |
| --- | --- | --- |
| None yet | Not applicable | Not applicable |

## Examples And Demonstrations

| Example | Behavior demonstrated | Weave context | Required docs/tests | Status |
| --- | --- | --- | --- | --- |
| Project-owned CLI adapter with configured base path | Configure entrypoint object once, compose explicit config args without repeated base token, preserve warnings/unparsed args. | Extends current `project-cli-argv` example pattern without first-party executable or command semantics. | Feature docs, example README, example harness, public integration tests. | confirmed |
| Generic base resolver example | Resolve base config from caller-provided project context without command semantics; `base_context` is input-only and not serialized unless the resolver returns explicit plain-data details. | Shows explicit project-owned base selection. | Feature docs and tests for resolver success/failure and metadata boundaries. | confirmed |
| Selected target instantiation example | Compose config, instantiate selected trusted target path, return object separately; selected non-target values remain plain values through existing `instantiate(...)` semantics. | Demonstrates explicit trusted target construction after composition. | Example coverage decision and no-import-default tests. | confirmed |
| Migration diagnostics example | Show old command-first invocation shape receiving targeted commandless migration diagnostics, if retained helper names would otherwise be ambiguous. | Makes the commandless break understandable without documenting command-first behavior as current. | Feature docs and error tests. | confirmed |

## Validation Strategy

| Area | Behavior validated | Required coverage | Test/check type | Command or location | Status |
| --- | --- | --- | --- | --- | --- |
| Import boundary | New public symbols do not make ordinary `import weave` import heavy modules or downstream project code. | Lazy export and import-boundary tests. | Package/unit | `tests/test_import.py` plus new coverage as needed | confirmed |
| Commandless parser and records | Config args parse without command tokens, command choices, command result fields, or command-shaped diagnostics. | Unit parser tests for overrides, scoped overlays, unparsed args, malformed tokens, and remediation text. | Unit | `tests/unit/config/test_argv.py` or successor commandless parser tests | confirmed |
| Configured base path | Object composes explicit config args using configured base path and existing scoped overlay/value override behavior. | Unit and integration tests. | Unit/integration | New Stage 1 tests | confirmed |
| Generic base resolver | Resolver success, failure, missing base, ambiguous base, invalid return, input-only `base_context`, and explicit plain-data resolution details. | Unit and integration tests. | Unit/integration | New Stage 1 tests | confirmed |
| Existing helper migration | Current command-first `compose_config_from_argv(...)` and `inspect_config_from_argv(...)` behavior migrates to the commandless contract, with targeted diagnostics for old command-first invocation shapes. | Regression tests for commandless helpers and migration diagnostics; update or replace old command-first expectations. | Unit/integration | Existing and new argv suites | confirmed |
| No implicit project argv | `compose_args(...)` and `inspect_args(...)` default to an empty config-arg sequence and never read `sys.argv[1:]`. | Tests that monkeypatch `sys.argv` and observe no implicit use. | Unit/integration | New Stage 1 tests | confirmed |
| Passthrough and warnings | Helper-local warnings and unparsed args are preserved in result data and not persisted to artifacts. | Public integration tests. | Integration | New Stage 1 tests and existing argv tests migrated to commandless records | confirmed |
| Raw snapshot opt-in | Raw source snapshots remain disabled by default and enabled only by explicit policy. | Integration tests. | Integration | New Stage 1 tests | confirmed |
| Selected instantiation | No instantiation by default; selected targets instantiate only when requested; runtime injection passes through; selected non-target values remain plain. | Unit/integration tests. | Unit/integration | New Stage 1 tests and existing instantiate tests | confirmed |
| No full-config instantiation | Stage 1 does not expose full-config instantiation unless a later requirement reopens it. | Absence/invalid-option tests and docs review. | Unit/docs | New Stage 1 tests and feature docs | confirmed |
| Docs and examples | Adapter examples stay domain-neutral, use explicit config args, avoid first-party executable claims, and migrate away from command-first helper examples. | Example harness and docs review. | Example/docs | `tests/test_examples.py`, feature docs | confirmed |

## Phase Sketch

### Phase 1 - Commandless Public Contracts

Goal:

- Add the configured object, commandless parser/records, constructor validation,
  fixed-base `compose_args(...)` and `inspect_args(...)`, and lazy public
  exports without selected instantiation.

Scope:

- Public `ConfigEntrypoint` object.
- `ParsedConfigArgs`, `ConfigArgsCompositionResult`, and
  `ConfigArgsInspectionResult`.
- Preferred commandless function-level helpers if retained function-level access
  is needed.
- Fixed `base_config_path`, `allow_unparsed`, recipe catalog/default catalog,
  and raw source snapshot policy.
- Commandless diagnostics and migration diagnostics for old command-first
  invocation shapes.

Out of scope:

- Base resolver callbacks.
- Selected or full-config instantiation.
- `sys.argv` defaulting.
- Command tokens, command choices, command result fields, or command-shaped
  error context.

Acceptance criteria:

- Fixed-base composition works with explicit config args and no command.
- Public result metadata contains no command field.
- New parser records are distinct from command-bearing `ParsedConfigArgv`.
- Old command-first invocation shapes fail with targeted migration diagnostics
  or are routed through a documented commandless compatibility path without
  preserving command semantics.

Test expectations:

- Package: lazy export/import-boundary checks.
- Unit: constructor validation, parser classification, commandless diagnostics,
  result `to_dict()` object exclusion.
- Contract: public result field shape.
- Integration: fixed-base composition with scoped overlays, value overrides,
  warnings, unparsed args, and raw snapshot policy.
- E2E: none beyond runnable examples in Phase 4.
- Opt-in: none.

Design impact:

- Establishes the current public contract and separates it from legacy
  command-first records.

Future compatibility:

- Future command semantics require a separate design and cannot reuse hidden
  nullable command slots.

Alternatives rejected:

- Wrapping existing `ParsedConfigArgv` unchanged.
- Keeping `command_choices` or command result metadata.
- Reading `sys.argv[1:]` implicitly.

Debt introduced:

- Migration work for callers and tests that rely on command-first helpers.

Reviewability:

- Phase can be reviewed around API shape, parser records, and fixed-base
  behavior without resolver or instantiation complexity.

### Phase 2 - Base Resolution And Config-Arg Policies

Goal:

- Add project-owned base resolution and finish commandless config-arg policy
  behavior without widening Weave into CLI parsing or search.

Scope:

- `ConfigBaseRequest` and `ConfigBaseResolution`.
- Exactly one base strategy per entrypoint: fixed path or resolver.
- Resolver invocation with opaque `base_context`.
- Explicit plain-data resolver details in result metadata.
- Missing, conflicting, ambiguous, and invalid base-resolution diagnostics.
- Call-level overrides only where explicitly named and validated by the
  implementation plan.

Out of scope:

- Global config search, project-root discovery, default config names, include
  resolver hooks, plugin loaders, workflow hooks, stores, schedulers, and
  command-specific resolver APIs.

Acceptance criteria:

- Resolver-base composition works without command context.
- `base_context` is not serialized into result metadata automatically.
- Resolver details are serialized only when returned as plain data in
  `ConfigBaseResolution`.
- Failure modes are structured and commandless.

Test expectations:

- Package: no new import side effects from resolver support.
- Unit: base strategy validation, resolver return validation, metadata
  serialization boundaries.
- Contract: `ConfigBaseResolution.to_dict()` or equivalent plain-data export.
- Integration: resolver success/failure with config args, warnings, raw snapshot
  policy, and unparsed args.
- E2E: optional example-level coverage in Phase 4.
- Opt-in: none.

Design impact:

- Establishes the only Stage 1 adapter extension point.

Future compatibility:

- Keeps Stage 3 search/resolver/plugin candidates deferred and separable.

Alternatives rejected:

- Resolver receives command, argparse namespace, or full project argv.
- Resolver doubles as config search path registry or include resolver.

Debt introduced:

- None beyond documenting resolver metadata boundaries.

Reviewability:

- Phase can be reviewed around one clear interface and its diagnostics.

### Phase 3 - Optional Selected Instantiation

Goal:

- Let callers explicitly instantiate selected trusted values while keeping
  composition inert by default.

Scope:

- Selected dot-path strings and optional name-to-dot-path mapping.
- Sequence shorthand keyed by selected dot path.
- Lookup from `ComposedConfig.resolved`.
- Per-selection calls to existing `instantiate(...)` with runtime injection.
- Object mapping on composition results and plain-data selected-object metadata.
- Selected non-target values pass through existing `instantiate(...)` semantics
  and therefore remain plain values.

Out of scope:

- Default instantiation.
- Full-config instantiation.
- Automatic target discovery.
- Target schema validation, executor hooks, stores, persistence, or workflow
  execution.

Acceptance criteria:

- No target imports occur unless selected instantiation is requested.
- Selected target mappings instantiate through existing recursive behavior.
- Selected non-target values remain plain values.
- Missing selected paths and instantiation errors are structured and preserve
  path context.
- `objects` are returned separately and omitted from plain-data result export.

Test expectations:

- Package: no-import-default checks.
- Unit: selector normalization, path lookup, missing path errors,
  object-exclusion export.
- Contract: result object/metadata separation.
- Integration: selected target instantiation with runtime injection.
- E2E: selected target example in Phase 4.
- Opt-in: selected instantiation tests are explicit opt-in behavior.

Design impact:

- Adds trusted target construction coordination without changing composition or
  instantiate semantics.

Future compatibility:

- Avoids Stage 3 executor/store coupling by returning Python objects only to the
  caller.

Alternatives rejected:

- Full-config instantiation in Stage 1.
- Requiring selected values to be `_target_` mappings.
- Persisting or serializing instantiated objects.

Debt introduced:

- Revisit selected path ergonomics if common adapters need richer selectors.

Reviewability:

- Phase is isolated to selector normalization, lookup, and object result shape.

### Phase 4 - Docs, Examples, And Hardening

Goal:

- Align docs, examples, behavior matrix, and migration notes with the
  commandless Stage 1 public contract.

Scope:

- Feature docs for commandless config args and configured entrypoint usage.
- Runnable project-owned adapter example using explicit config args.
- Generic base resolver example.
- Selected instantiation example.
- Migration notes for old command-first invocation shapes.
- Behavior matrix and example coverage updates.
- Removal or rewrite of examples that imply command-first Stage 1 behavior.

Out of scope:

- First-party executable docs.
- Domain-specific examples, schemas, workflows, run stores, schedulers, or
  remote/plugin integration examples.
- Documentation for unimplemented future command semantics.

Acceptance criteria:

- Docs do not describe command as part of any Stage 1 helper contract.
- Examples use explicit config args and remain domain-neutral.
- Behavior matrix has rows for configured base path, resolver base selection,
  commandless helper migration, selected instantiation, import boundaries, and
  artifact-safe defaults.
- Existing draft implementation-plan text that mentions optional `sys.argv[1:]`
  defaulting or optional full-config instantiation is revised before final plan
  approval.

Test expectations:

- Package: docs import examples do not break lazy imports.
- Unit: no additional unit-only expectations beyond previous phases.
- Contract: docs and behavior matrix align with public result contracts.
- Integration: example harness covers the runnable adapter example.
- E2E: `tests/test_examples.py` or existing harness path.
- Opt-in: none.

Design impact:

- Turns the API design into supported public documentation without promising
  unimplemented behavior.

Future compatibility:

- Lets Stage 2 either consume implemented Stage 1 coverage or record explicit
  deferral if Stage 1 is not complete.

Alternatives rejected:

- Leaving `project-cli-argv` docs command-first without migration notes.
- Documenting planned future command support.

Debt introduced:

- Existing docs/tests using command-first helper examples must be updated.

Reviewability:

- Phase is docs/test cleanup and can be reviewed against the behavior matrix.

## Implementation Readiness

| Check | Evidence | Result | Required action |
| --- | --- | --- | --- |
| Roadmap-to-requirement traceability | Confirmed FRs map to the revised Stage 1 roadmap entry and commandless helper scope. | pass | None. |
| Requirement-to-design traceability | Design queue is classified and each decision traces to confirmed FRs. | pass | None. |
| Design-safety review completed | Reviewer passed the design and required revisions are recorded. | pass | None. |
| Future-roadmap impact considered | Stage 2 and Stage 3 touchpoints are recorded in design decisions and safety review. | pass | None. |
| Generic interface, adapter, and protocol flexibility considered | Resolver, result, and selector contracts are recorded as generic interface shapes and reviewed. | pass | None. |
| Example-to-validation traceability | Examples and validation rows trace to commandless configured-base, resolver, migration, and selected-instantiation behavior. | pass | None. |
| Phase-shaping readiness | Phase boundaries are recorded and account for stale draft-plan items. | pass | None. |
| Unresolved blocked or needs-discussion functionality or design decisions | Functionality, design, and design-safety queues have no unresolved high-impact questions. | pass | None. |
| Final planning confirmation | User confirmed the final planning artifact and authorized implementation-plan drafting. | pass | None. |

Readiness result:

- Status: confirmed and handed off to implementation-plan drafting
- Implementation-plan drafting blockers:
  - None from roadmap-stage planning. The implementation plan records its own quality-review gate before phase execution.
- Accepted risks:
  - Public API naming lock-in.
  - Migration cost for existing command-first helper callers and tests.
- Assumptions to carry forward:
  - Stage 1 stays domain-neutral and adapter-oriented.
  - Existing command-first argv helper behavior migrates to the commandless
    contract; helper availability may be retained, but public command-first
    semantics should not be preserved as Stage 1 behavior.
  - Optional trusted target instantiation remains explicit, selected, and
    disabled by default.
  - `base_context` is input-only resolver context unless the resolver returns
    explicit plain-data details.
  - Full-config instantiation and implicit `sys.argv` defaulting are out of
    Stage 1.

## Open Questions

| Question | Affects | Current default | Status |
| --- | --- | --- | --- |
| Does the user have clarifying questions about the Stage 1 briefing before intent discovery begins? | Roadmap framing | User asked for coding-level shape; answered and recorded. | resolved |
| What should Stage 1 optimize for: lowest downstream CLI boilerplate, strictest API minimalism, richest structured metadata for adapters, or another priority? | Roadmap framing and intent discovery | Balance CLI boilerplate reduction with minimal, stable public contracts. | resolved; external project interaction and command-boundary clarity are priority |
| Should the documented target audience emphasize downstream CLI adapters, Python application entrypoints, or both equally? | Roadmap framing and intent discovery | Support both, document adapter integration first because the current gap is project-owned argument handoff. | resolved |
| Should variable-distance project argv be handled by requiring the project to pass a config-args slice or separate config args, rather than Weave scanning full project argv? | Functionality and behavior | Yes. Project owns argv parsing; Weave parses only supplied config args and returns unparsed items from that supplied sequence. | resolved |
| Should selected instantiation be part of the core done bar? | Intent discovery | Yes, but it remains explicit, opt-in, and separately returned. | resolved |
| Should result data be plain-data friendly except for instantiated objects? | Intent discovery and design | Yes. `objects` may contain arbitrary Python instances and should be separated from plain-data result metadata. | resolved |
| Should Stage 1 remove command reliance from all helper contracts, including planned and current command-first helpers? | Intent discovery and design | Yes. Command-specific behavior is deferred until a concrete future need justifies it. | resolved |
| What selector shape should selected instantiation use? | Functionality and design | Dot paths with optional caller-selected result names; sequence shorthand keys by path. Selected values pass through existing `instantiate(...)` semantics. | resolved in design agreement and safety review |
| How much parsed/base-resolution metadata should be standardized in the result? | Functionality and design | Standardize base resolution, raw config args, parsed records, warnings, unparsed args, selected-object metadata, and object keys; keep object values and opaque `base_context` out of plain-data export. | resolved in design agreement and safety review |
| Should the object expose separate compose and inspect methods, or one method with explicit mode options? | Design | Separate `compose_args(...)` and `inspect_args(...)`; no implicit `sys.argv` default. | resolved in design agreement |
| What final public names should the object and result types use? | Design | `ConfigEntrypoint`, `ConfigArgsCompositionResult`, `ConfigArgsInspectionResult`, `ParsedConfigArgs`, `ConfigBaseRequest`, and `ConfigBaseResolution`. | resolved in design agreement |
| Does the user confirm this final roadmap-stage planning artifact and authorize implementation-plan drafting next? | Handoff | Confirm planning artifact, then revise/draft `implementation-plan.md` from it. | resolved; user confirmed |

## Handoff Notes

Implementation-plan draft inputs:

- User confirmed final planning and authorized implementation-plan drafting.
- The existing `implementation-plan.md` is draft evidence and must be revised
  during implementation-plan drafting to remove stale optional `sys.argv[1:]`
  defaulting and optional full-config instantiation references.
- Implementation-plan drafting should use this planning artifact as source of
  truth, especially the commandless helper migration, opaque `base_context`,
  selected non-target value behavior, and commandless diagnostics requirements.

Design-safety review result:

- Passed with required planning revisions, all recorded here.
- No design decisions need user discussion under the confirmed behavior
  baseline.

Validation and phase-shaping inputs:

- Examples, validation strategy, and four implementation phases are recorded and
  trace to requirements and design decisions.
- Validation must cover commandless parsing and diagnostics, helper migration,
  resolver metadata boundaries, no implicit `sys.argv`, no full-config
  instantiation, selected non-target values, import boundaries, docs, and
  examples.

Plan-quality-gate risks:

- Release compatibility may require a separately named legacy command-first
  helper; that would need an explicit reopened decision because it conflicts
  with the confirmed Stage 1 target.
- Public name lock-in remains accepted pending final confirmation.
- Selected dot-path ergonomics should be revisited only if implementation or
  real adapter usage shows the selector model is insufficient.

Assumptions to carry forward:

- Stage 1 is a configured-object layer over existing composition behavior and a
  new commandless config-args parser/helper contract.
- Existing artifact-safe defaults, explicit trusted code execution, and import
  boundaries remain non-negotiable unless an intentional compatibility break is
  documented.
- Stage 1 does not add command semantics, first-party CLI behavior, config
  search, workflow execution, persistence policy, schema registries, executor or
  store hooks, remote/plugin include resolution, or Stage 3 behavior candidates.
