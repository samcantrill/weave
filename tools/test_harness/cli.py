"""Run weave test suites and write a compact Markdown summary."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

SUMMARY_OUTPUT = Path("build/test-summary.md")


@dataclass(frozen=True, slots=True)
class Suite:
    name: str
    command: tuple[str, ...]


SUITES: tuple[Suite, ...] = (
    Suite("package", (sys.executable, "-m", "pytest", "tests", "-m", "package", "--ignore=tests/test_examples.py")),
    Suite("unit", (sys.executable, "-m", "pytest", "tests/unit")),
    Suite("contract", (sys.executable, "-m", "pytest", "tests/contracts")),
    Suite("integration", (sys.executable, "-m", "pytest", "tests/integration")),
    Suite("examples", (sys.executable, "-m", "pytest", "tests/test_examples.py")),
)

_COUNT_RE = re.compile(r"(?P<count>\d+) (?P<label>passed|failed|skipped|deselected|xfailed|xpassed|errors?)")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run weave test suites and write a Markdown summary.")
    parser.add_argument("command", choices={"summary"})
    parser.add_argument("--output", default=str(SUMMARY_OUTPUT))
    args = parser.parse_args(argv)

    rows: list[tuple[str, str, float, str]] = []
    failed = False
    for suite in SUITES:
        started = time.monotonic()
        result = subprocess.run(suite.command, check=False, capture_output=True, text=True)
        duration = time.monotonic() - started
        output = "\n".join(part for part in (result.stdout, result.stderr) if part)
        status = "PASS" if result.returncode == 0 else "FAIL"
        failed = failed or result.returncode != 0
        rows.append((suite.name, status, duration, _summarize_counts(output)))

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_render(rows), encoding="utf-8")
    return 1 if failed else 0


def _summarize_counts(output: str) -> str:
    counts: dict[str, int] = {}
    for match in _COUNT_RE.finditer(output):
        label = match.group("label")
        if label == "error":
            label = "errors"
        counts[label] = counts.get(label, 0) + int(match.group("count"))
    if not counts:
        return "no pytest counts found"
    order = ("passed", "failed", "errors", "skipped", "deselected", "xfailed", "xpassed")
    return ", ".join(f"{counts[label]} {label}" for label in order if label in counts)


def _render(rows: list[tuple[str, str, float, str]]) -> str:
    lines = [
        "# Test Summary",
        "",
        "| Suite | Status | Duration | Counts |",
        "| --- | --- | ---: | --- |",
    ]
    for suite, status, duration, counts in rows:
        lines.append(f"| `{suite}` | {status} | {duration:.1f}s | {counts} |")
    lines.append("")
    return "\n".join(lines)


__all__ = ["main"]
