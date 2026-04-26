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


def not_implemented(tool: str, message: str, **metadata: Any) -> dict[str, Any]:
    return {
        "ok": False,
        "status": "not_implemented",
        "tool": tool,
        "message": message,
        "metadata": metadata,
    }
