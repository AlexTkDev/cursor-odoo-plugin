#!/usr/bin/env python3
"""MCP stdio server for cursor-odoo-dev."""

from __future__ import annotations

import json
import logging
import sys
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

try:
    from .tools import (
        analyze_migration,
        check_oca_compliance,
        create_module,
        db_describe_model,
        db_list_models,
        db_missing_indexes,
        odoo_shell_eval,
        profile_module,
        review_xml,
        run_odoo_tests,
        validate_manifest,
    )
except ImportError:  # pragma: no cover - used when executed as python mcp/server.py
    from tools import (  # type: ignore[no-redef]
        analyze_migration,
        check_oca_compliance,
        create_module,
        db_describe_model,
        db_list_models,
        db_missing_indexes,
        odoo_shell_eval,
        profile_module,
        review_xml,
        run_odoo_tests,
        validate_manifest,
    )

LOGGER = logging.getLogger("cursor_odoo_dev.mcp")


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    input_schema: dict[str, Any]
    handler: Callable[..., dict[str, Any]]

    def descriptor(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
        }


def object_schema(properties: dict[str, Any], required: list[str] | None = None) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": properties,
        "required": required or [],
        "additionalProperties": False,
    }


TOOLS: dict[str, Tool] = {
    "validate_manifest": Tool(
        "validate_manifest",
        "Validate an Odoo __manifest__.py file.",
        object_schema({"path": {"type": "string"}}, ["path"]),
        validate_manifest,
    ),
    "review_xml": Tool(
        "review_xml",
        "Review an Odoo XML file with static checks.",
        object_schema({"path": {"type": "string"}}, ["path"]),
        review_xml,
    ),
    "create_module": Tool(
        "create_module",
        "Create an Odoo 16+ addon skeleton.",
        object_schema(
            {
                "module_name": {"type": "string"},
                "target_dir": {"type": "string", "default": "."},
                "wizard": {"type": "boolean", "default": False},
                "report": {"type": "boolean", "default": False},
                "mail_thread": {"type": "boolean", "default": False},
                "website": {"type": "boolean", "default": False},
                "portal": {"type": "boolean", "default": False},
            },
            ["module_name"],
        ),
        create_module,
    ),
    "db_list_models": Tool("db_list_models", "V2 placeholder: list Odoo models from PostgreSQL.", object_schema({}), db_list_models),
    "db_describe_model": Tool(
        "db_describe_model",
        "V2 placeholder: describe a model from PostgreSQL.",
        object_schema({"model": {"type": "string"}}, ["model"]),
        db_describe_model,
    ),
    "db_missing_indexes": Tool("db_missing_indexes", "V2 placeholder: find missing PostgreSQL indexes.", object_schema({}), db_missing_indexes),
    "analyze_migration": Tool(
        "analyze_migration",
        "V2 placeholder: analyze Odoo 16->17 or 17->18 migration.",
        object_schema(
            {
                "module_path": {"type": "string"},
                "source_version": {"type": "string"},
                "target_version": {"type": "string"},
            },
            ["module_path", "source_version", "target_version"],
        ),
        analyze_migration,
    ),
    "check_oca_compliance": Tool(
        "check_oca_compliance",
        "V2 placeholder: check OCA compliance.",
        object_schema({"module_path": {"type": "string"}}, ["module_path"]),
        check_oca_compliance,
    ),
    "odoo_shell_eval": Tool(
        "odoo_shell_eval",
        "V3 placeholder: evaluate code in an Odoo shell.",
        object_schema({"code": {"type": "string"}}, ["code"]),
        odoo_shell_eval,
    ),
    "run_odoo_tests": Tool(
        "run_odoo_tests",
        "V3 placeholder: run Odoo tests for a module.",
        object_schema({"module": {"type": "string"}}, ["module"]),
        run_odoo_tests,
    ),
    "profile_module": Tool(
        "profile_module",
        "V3 placeholder: profile an Odoo module.",
        object_schema({"module": {"type": "string"}}, ["module"]),
        profile_module,
    ),
}


def list_tools() -> dict[str, Any]:
    return {"tools": [tool.descriptor() for tool in TOOLS.values()]}


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    tool = TOOLS.get(name)
    if tool is None:
        return {"ok": False, "errors": [{"code": "unknown_tool", "message": f"Unknown tool: {name}"}], "warnings": [], "metadata": {}}
    try:
        return tool.handler(**arguments)
    except TypeError as exc:
        return {"ok": False, "errors": [{"code": "invalid_arguments", "message": str(exc)}], "warnings": [], "metadata": {"tool": name}}
    except Exception as exc:  # noqa: BLE001 - MCP must return structured errors
        LOGGER.exception("Tool failed: %s", name)
        return {"ok": False, "errors": [{"code": "tool_exception", "message": str(exc)}], "warnings": [], "metadata": {"tool": name}}


def handle_jsonrpc(request: dict[str, Any]) -> dict[str, Any] | None:
    request_id = request.get("id")
    method = request.get("method")
    params = request.get("params") or {}

    if request_id is None and str(method).startswith("notifications/"):
        return None

    try:
        if method == "initialize":
            result: dict[str, Any] = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "cursor-odoo-dev", "version": "1.0.0"},
            }
        elif method == "tools/list":
            result = list_tools()
        elif method == "tools/call":
            payload = call_tool(params.get("name", ""), params.get("arguments") or {})
            result = {"content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False, indent=2)}]}
        elif method in {"resources/list", "prompts/list"}:
            result = {"resources": []} if method == "resources/list" else {"prompts": []}
        else:
            return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}
    except Exception as exc:  # noqa: BLE001
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32603, "message": str(exc)}}

    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def main() -> None:
    logging.basicConfig(stream=sys.stderr, level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_jsonrpc(request)
        except json.JSONDecodeError as exc:
            response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": f"Parse error: {exc}"}}
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
