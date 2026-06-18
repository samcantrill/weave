"""Neutral service target used by the project-owned adapter example."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AdapterService:
    name: str
    retries: int = 1
