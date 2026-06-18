"""Compose config from project-owned commandless config args."""

from __future__ import annotations

from pathlib import Path
from pprint import pprint
from typing import cast

from weave import (
    ConfigEntrypoint,
    compose_config_from_args,
    compose_config_from_argv,
)
from weave.api import ConfigBaseRequest, ConfigBaseResolution
from weave.errors import ConfigValidationError

from services import AdapterService


HERE = Path(__file__).resolve().parent
BASE_CONFIG = HERE / "configs" / "experiment.yaml"


def main() -> None:
    config_args = [
        "data/=data_A",
        "model/=model_B",
        "+runtime/=local",
        "trainer.epochs=5",
        "--dry-run",
    ]
    result = compose_config_from_args(
        BASE_CONFIG,
        config_args,
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

    entrypoint = ConfigEntrypoint(
        base_resolver=_resolve_base,
        base_context={"profile": "adapter-demo"},
        selected_objects={"service": "service"},
    )
    selected_result = entrypoint.compose_args(
        [
            "service.name=selected-service",
            "service.retries=3",
        ]
    )

    print("base resolver details:")
    pprint(selected_result.base_details, sort_dicts=True)
    service = cast(AdapterService, selected_result.objects["service"])
    print("selected service:")
    pprint(service, sort_dicts=True)
    print("serialized selected-object metadata:")
    pprint(selected_result.to_dict()["selected_objects"], sort_dicts=True)

    try:
        compose_config_from_argv(["run", str(BASE_CONFIG), "trainer.epochs=5"])
    except ConfigValidationError as exc:
        print("migration diagnostic:")
        context = exc.context
        if context is None:
            pprint({"type": type(exc).__name__, "message": str(exc)})
        else:
            pprint(
                {
                    "code": context.code,
                    "details": context.details,
                    "remediation": context.remediation,
                },
                sort_dicts=True,
            )


def _resolve_base(request: ConfigBaseRequest) -> ConfigBaseResolution:
    context = request.base_context
    profile = context["profile"] if isinstance(context, dict) else "default"
    return ConfigBaseResolution(
        base_config_path=BASE_CONFIG,
        details={"profile": profile},
    )


def _relative_to_example(path: str | None) -> str | None:
    if path is None:
        return None
    return str(Path(path).relative_to(HERE))


if __name__ == "__main__":
    main()
