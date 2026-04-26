"""Odoo performance profiler placeholder."""

from __future__ import annotations

from typing import Any

from .common import not_implemented


def profile_module(module: str) -> dict[str, Any]:
    return not_implemented(
        "profile_module",
        "Odoo profiling integration is planned for V3.",
        module=module,
    )
