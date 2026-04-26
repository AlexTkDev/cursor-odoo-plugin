"""Migration assistant placeholder."""

from __future__ import annotations

from typing import Any

from .common import not_implemented

SUPPORTED_PAIRS = {("16", "17"), ("17", "18")}


def analyze_migration(module_path: str, source_version: str, target_version: str) -> dict[str, Any]:
    supported = (source_version, target_version) in SUPPORTED_PAIRS
    return not_implemented(
        "analyze_migration",
        "Migration analysis is planned for V2. The API shape is reserved and stable.",
        module_path=module_path,
        source_version=source_version,
        target_version=target_version,
        supported=supported,
    )
