"""Runtime helpers for Odoo CLI-backed tools."""

from __future__ import annotations

import os
import shlex
import subprocess
import time
from pathlib import Path
from typing import Any

from .common import error_result, tail_text, tool_result


def build_odoo_command(
    *,
    odoo_bin: str = "odoo-bin",
    database: str | None = None,
    config: str | None = None,
    addons_path: str | None = None,
    extra_args: list[str] | None = None,
) -> list[str]:
    command = [odoo_bin]
    if config:
        command.extend(["-c", config])
    if database:
        command.extend(["-d", database])
    if addons_path:
        command.extend(["--addons-path", addons_path])
    if extra_args:
        command.extend(extra_args)
    return command


def validate_runtime_config(odoo_bin: str, database: str | None, config: str | None) -> dict[str, Any] | None:
    if not odoo_bin:
        return error_result("missing_odoo_bin", "Provide odoo_bin or use the default executable name.")
    if "/" in odoo_bin or odoo_bin.startswith("."):
        candidate = Path(odoo_bin).expanduser()
        if not candidate.exists():
            return error_result("odoo_bin_not_found", f"odoo_bin does not exist: {odoo_bin}", odoo_bin=odoo_bin)
    if config:
        candidate = Path(config).expanduser()
        if not candidate.exists():
            return error_result("config_not_found", f"Odoo config file does not exist: {config}", config=config)
    if not database and not config and not os.environ.get("ODOO_RC"):
        return error_result(
            "missing_runtime_target",
            "Provide database, config, or ODOO_RC so Odoo knows which environment to use.",
        )
    return None


def run_command(command: list[str], *, timeout: int = 1800, input_text: str | None = None, cwd: str | None = None) -> dict[str, Any]:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            input=input_text,
            text=True,
            capture_output=True,
            timeout=timeout,
            cwd=cwd,
            check=False,
        )
    except FileNotFoundError as exc:
        return error_result("executable_not_found", str(exc), command=command)
    except subprocess.TimeoutExpired as exc:
        return tool_result(
            False,
            errors=[{"code": "timeout", "message": f"Command timed out after {timeout}s"}],
            metadata={"command": command, "timeout": timeout},
            data={"stdout": tail_text(exc.stdout or ""), "stderr": tail_text(exc.stderr or "")},
        )

    duration = round(time.monotonic() - started, 3)
    return tool_result(
        completed.returncode == 0,
        errors=[] if completed.returncode == 0 else [{"code": "command_failed", "message": f"Command exited with {completed.returncode}"}],
        metadata={"command": command, "command_display": shlex.join(command), "returncode": completed.returncode, "duration_seconds": duration},
        data={"stdout": tail_text(completed.stdout), "stderr": tail_text(completed.stderr)},
    )
