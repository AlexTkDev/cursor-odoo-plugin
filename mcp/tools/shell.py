"""Odoo shell bridge placeholder."""

from __future__ import annotations

from typing import Any

from .common import not_implemented


def odoo_shell_eval(code: str) -> dict[str, Any]:
    return not_implemented(
        "odoo_shell_eval",
        "Odoo shell bridge is planned for V3 and will require explicit sandbox and database policy.",
        code_preview=code[:120],
    )
