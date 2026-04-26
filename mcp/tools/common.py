"""Shared helpers for MCP tools."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CheckResult:
    """Structured result used by validators and reviewers."""

    ok: bool = True
    errors: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def error(self, code: str, message: str, **extra: Any) -> None:
        self.ok = False
        self.errors.append({"code": code, "message": message, **extra})

    def warning(self, code: str, message: str, **extra: Any) -> None:
        self.warnings.append({"code": code, "message": message, **extra})

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata,
        }


def resolve_existing_file(path: str) -> Path:
    candidate = Path(path).expanduser()
    if not candidate.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not candidate.is_file():
        raise ValueError(f"Path is not a file: {path}")
    return candidate


def tool_result(
    ok: bool,
    *,
    errors: list[dict[str, Any]] | None = None,
    warnings: list[dict[str, Any]] | None = None,
    metadata: dict[str, Any] | None = None,
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": ok,
        "errors": errors or [],
        "warnings": warnings or [],
        "metadata": metadata or {},
    }
    if data is not None:
        payload["data"] = data
    return payload


def error_result(code: str, message: str, **metadata: Any) -> dict[str, Any]:
    return tool_result(False, errors=[{"code": code, "message": message}], metadata=metadata)


def tail_text(value: str, limit: int = 12000) -> str:
    if len(value) <= limit:
        return value
    return value[-limit:]
