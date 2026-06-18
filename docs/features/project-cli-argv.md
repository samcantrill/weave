# Project-Owned Config Args

Project-specific CLIs can accept compact config shorthand without making `weave`
own a command-line executable. The project parser owns commands and
command-specific flags, chooses the base config, and passes the remaining config
args to `weave`.

Preferred helpers are `compose_config_from_args(...)`, `inspect_config_args(...)`,
and `ConfigEntrypoint.compose_args(...)`.

## Shape

The current Stage 1 shape is commandless:

```text
<config-shorthand-or-project-passthrough>...
```

The base config is supplied separately by the project:

```python
from weave import ConfigEntrypoint

entrypoint = ConfigEntrypoint(base_config_path="configs/base.yaml")
result = entrypoint.compose_args(["model/=model_B", "trainer.epochs=5"])
```

No-slash left-hand sides are ordinary value overrides:

```text
run.seed=123
+vars.learning_rate=0.0003
output_dir=results/model_B.yaml
```

Trailing-slash left-hand sides are scoped overlays:

```text
data/=data_A
model/=model_B
model/pipeline/=pipeline_A
+runtime/=local
```

Scoped overlays apply after authored includes and before recipe expansion. Value
overrides apply after recipe expansion and win over scoped overlay content.
Warnings are helper-local result data and are not persisted into normal composed
config artifacts.

## Base Selection

Projects can keep base selection fixed:

```python
entrypoint = ConfigEntrypoint(base_config_path="configs/base.yaml")
```

or provide a narrow resolver that receives opaque project-owned context:

```python
from weave import ConfigEntrypoint
from weave.api import ConfigBaseRequest, ConfigBaseResolution

def resolve_base(request: ConfigBaseRequest) -> ConfigBaseResolution:
    profile = request.base_context["profile"]
    return ConfigBaseResolution(
        base_config_path=f"configs/{profile}.yaml",
        details={"profile": profile},
    )

entrypoint = ConfigEntrypoint(
    base_resolver=resolve_base,
    base_context={"profile": "dev"},
)
```

`base_context` is never serialized automatically. Resolver `details` must be
plain data and are exposed as result metadata.

## Selected Instantiation

Selected instantiation is opt-in and path-oriented. Composition remains inert
unless selectors are configured.

```python
entrypoint = ConfigEntrypoint(
    base_config_path="configs/base.yaml",
    selected_objects={"service": "service"},
)
result = entrypoint.compose_args(["service.retries=3"])
service = result.objects["service"]
```

`result.to_dict()` includes selected-object metadata but never serializes Python
objects.

## Retained Argv Helper Names

`compose_config_from_argv(...)` and `inspect_config_from_argv(...)` remain
available for compatibility with explicit argv vectors where the first token is
the base config. They are not command-first helpers. Old
`<command> <base-config> ...` shapes raise structured migration diagnostics, and
`command_choices` is not part of the Stage 1 contract.

See [`examples/project-cli-argv/`](../../examples/project-cli-argv/) for a
runnable project-owned adapter example.
