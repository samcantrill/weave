# Project-Owned Config Args

This example shows how a project-owned CLI adapter can pass explicit config args
to `weave` without giving `weave` ownership of project commands or process
behavior.

The adapter chooses the base config, keeps command-specific flags as project
state, and passes only config shorthand to `compose_config_from_args(...)` or
`ConfigEntrypoint.compose_args(...)`.

It demonstrates:

- commandless config args such as `data/=data_A` and `trainer.epochs=5`;
- trailing-slash scoped overlays and `+scope/=` creation for missing sections;
- command-specific passthrough args returned with `allow_unparsed=True`;
- helper-local warnings for likely missing scoped-overlay slashes;
- generic base resolution with plain-data resolver details;
- selected instantiation of an explicit trusted config path;
- migration diagnostics for old `<command> <base-config> ...` helper input.

## Run

Run from the repository root:

```sh
uv run python examples/project-cli-argv/project_cli_argv.py
```
