"""Odoo test runner integration."""

from __future__ import annotations

from typing import Any

from .runtime import build_odoo_command, run_command, validate_runtime_config


def run_odoo_tests(
    module: str,
    odoo_bin: str = "odoo-bin",
    database: str | None = None,
    config: str | None = None,
    addons_path: str | None = None,
    timeout: int = 1800,
    extra_args: list[str] | None = None,
) -> dict[str, Any]:
    """Run Odoo tests for a module through the Odoo CLI."""

    invalid = validate_runtime_config(odoo_bin, database, config)
    if invalid:
        return invalid
    if not module:
        return {
            "ok": False,
            "errors": [{"code": "missing_module", "message": "Provide an Odoo module technical name."}],
            "warnings": [],
            "metadata": {},
        }

    args = [
        "--test-enable",
        "--stop-after-init",
        "-i",
        module,
        "--log-level=test",
    ]
    if extra_args:
        args.extend(extra_args)
    command = build_odoo_command(
        odoo_bin=odoo_bin,
        database=database,
        config=config,
        addons_path=addons_path,
        extra_args=args,
    )
    result = run_command(command, timeout=timeout)
    result["metadata"]["module"] = module
    return result
