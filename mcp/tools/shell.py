"""Odoo shell bridge."""

from __future__ import annotations

import os
from typing import Any

from .common import error_result
from .runtime import build_odoo_command, run_command, validate_runtime_config


def odoo_shell_eval(
    code: str,
    odoo_bin: str = "odoo-bin",
    database: str | None = None,
    config: str | None = None,
    addons_path: str | None = None,
    timeout: int = 300,
) -> dict[str, Any]:
    """Evaluate code through ``odoo-bin shell`` with explicit opt-in."""

    if os.environ.get("CURSOR_ODOO_ALLOW_SHELL") != "1":
        return error_result(
            "shell_disabled",
            "Set CURSOR_ODOO_ALLOW_SHELL=1 to enable odoo_shell_eval. This tool executes code in an Odoo environment.",
        )
    if not code.strip():
        return error_result("empty_code", "Provide Python code to evaluate.")

    invalid = validate_runtime_config(odoo_bin, database, config)
    if invalid:
        return invalid

    command = build_odoo_command(
        odoo_bin=odoo_bin,
        database=database,
        config=config,
        addons_path=addons_path,
        extra_args=["shell"],
    )
    result = run_command(command, timeout=timeout, input_text=code)
    result["metadata"]["code_preview"] = code[:160]
    return result
