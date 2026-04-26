"""OCA compliance placeholder."""

from __future__ import annotations

from typing import Any

from .common import not_implemented


def check_oca_compliance(module_path: str) -> dict[str, Any]:
    return not_implemented(
        "check_oca_compliance",
        "OCA compliance automation is planned for V2.",
        module_path=module_path,
    )
