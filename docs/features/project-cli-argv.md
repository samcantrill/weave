# Project CLI Argv Shorthand

`compose_config_from_argv(...)` helps project-specific CLIs accept compact config
shorthand without making `weave` own a command-line executable.

The argv shape is:

```text
<command> <base-config> <config-shorthand-or-command-arg>...
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
