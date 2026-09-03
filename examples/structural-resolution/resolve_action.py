"""Resolve runtime structure after composition, then instantiate targets."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import cast

from weave import (
    StructuralResolutionRequest,
    StructuralResolverDefinition,
    StructuralResolverRejected,
    compose_config,
    instantiate,
    resolve_structural,
)


HERE = Path(__file__).resolve().parent


def main() -> None:
    workspace_roots = {"primary": "/runtime/workspaces/run-001"}

    def runtime_resolver(request: StructuralResolutionRequest) -> str:
        kind = request.arguments.get("kind")
        workspace_name = request.arguments.get("workspace_name")
        if kind != "workspace" or not isinstance(workspace_name, str):
            raise StructuralResolverRejected(
                "unsupported_runtime_authority",
                details={"kind": kind if isinstance(kind, str) else None},
            )
        try:
            return workspace_roots[workspace_name]
        except KeyError:
            raise StructuralResolverRejected(
                "unknown_workspace",
                details={"workspace_name": workspace_name},
            ) from None

    composed = compose_config(HERE / "config.yaml")
    action = composed.resolved["action"]
    authored_before = deepcopy(action)
    fingerprint_before = composed.fingerprint

    resolution = resolve_structural(
        action,
        resolvers={
            "example.runtime": StructuralResolverDefinition(
                version=1,
                handler=runtime_resolver,
            )
        },
    )

    assert action == authored_before
    assert composed.fingerprint == fingerprint_before
    objects = cast(dict[str, object], instantiate(resolution.value))

    print(json.dumps([record.to_dict() for record in resolution.records]))
    print(cast(dict[str, str], objects["summary"])["status"])


if __name__ == "__main__":
    main()
