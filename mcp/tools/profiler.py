"""Odoo performance profiler integration."""

from __future__ import annotations

from typing import Any

from .runtime import build_odoo_command, run_command, validate_runtime_config


def profile_module(
    module: str,
    odoo_bin: str = "odoo-bin",
    database: str | None = None,
    config: str | None = None,
    addons_path: str | None = None,
    timeout: int = 1800,
    mode: str = "tests",
) -> dict[str, Any]:
    """Run a repeatable Odoo CLI profile pass and return timing/log output."""

    invalid = validate_runtime_config(odoo_bin, database, config)
    if invalid:
        return invalid
    if mode not in {"tests", "install"}:
        return {
            "ok": False,
            "errors": [{"code": "invalid_profile_mode", "message": "mode must be 'tests' or 'install'"}],
            "warnings": [],
            "metadata": {"mode": mode},
        }

    args = ["--stop-after-init", "-i", module, "--log-level=debug_sql"]
    if mode == "tests":
        args.insert(0, "--test-enable")
    command = build_odoo_command(
        odoo_bin=odoo_bin,
        database=database,
        config=config,
        addons_path=addons_path,
        extra_args=args,
    )
    result = run_command(command, timeout=timeout)
    result["metadata"].update({"module": module, "mode": mode, "profile_kind": "cli_wall_time_and_debug_sql"})
    result["warnings"].append(
        {
            "code": "profiler_scope",
            "message": "This profiler captures CLI duration and Odoo debug_sql output. Use database/runtime profilers for deeper production traces.",
        }
    )
    return result
