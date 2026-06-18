"""Compose config from project-owned commandless config args."""

from __future__ import annotations

from pathlib import Path
from pprint import pprint

from weave import compose_config_from_args


HERE = Path(__file__).resolve().parent
BASE_CONFIG = HERE / "configs" / "experiment.yaml"


def main() -> None:
    result = compose_config_from_args(
        BASE_CONFIG,
        [
            "data/=data_A",
            "model/=model_B",
            "+runtime/=local",
            "trainer.epochs=5",
            "--dry-run",
        ],
        allow_unparsed=True,
    )

    print("unparsed config args:")
    pprint(result.parsed_args.unparsed_arg_strings)
    print("scoped overlays:")
    pprint(
        [
            {
                "raw": overlay.raw,
                "scope_path": overlay.scope_path,
                "operation": overlay.operation,
                "resolved_path": _relative_to_example(overlay.resolved_path),
            }
            for overlay in result.scoped_overlays
        ],
        sort_dicts=True,
    )
    print("resolved config:")
    pprint(result.composed_config.resolved, sort_dicts=True)

    warning_result = compose_config_from_args(
        BASE_CONFIG,
        [
            "model=model_B",
        ],
    )

    print("helper-local warnings:")
    pprint(
        [
            {
                "code": warning.code,
                "token": warning.token,
                "remediation": warning.remediation,
            }
            for warning in warning_result.warnings
        ],
        sort_dicts=True,
    )


def _relative_to_example(path: str | None) -> str | None:
    if path is None:
        return None
    return str(Path(path).relative_to(HERE))


if __name__ == "__main__":
    main()
