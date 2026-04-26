from pathlib import Path

from mcp.server import TOOLS, call_tool, handle_jsonrpc
from mcp.tools.scaffold import create_module


def test_server_registers_v1_and_placeholders() -> None:
    expected = {
        "validate_manifest",
        "review_xml",
        "create_module",
        "db_list_models",
        "analyze_migration",
        "odoo_shell_eval",
        "run_odoo_tests",
        "profile_module",
    }

    assert expected.issubset(TOOLS)


def test_jsonrpc_tools_list() -> None:
    response = handle_jsonrpc({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})

    assert response is not None
    assert response["result"]["tools"]


def test_placeholder_response() -> None:
    result = call_tool("db_list_models", {})

    assert result["status"] == "not_implemented"


def test_create_module_scaffold(tmp_path: Path) -> None:
    result = create_module("demo_addon", target_dir=str(tmp_path), mail_thread=True, website=True)

    module = tmp_path / "demo_addon"
    assert result["ok"] is True
    assert (module / "__manifest__.py").exists()
    assert (module / "models" / "demo_addon.py").exists()
    assert (module / "views" / "demo_addon_views.xml").exists()
    assert (module / "security" / "ir.model.access.csv").exists()
    assert (module / "data" / ".gitkeep").exists()
    assert (module / "demo" / ".gitkeep").exists()
    assert (module / "tests" / ".gitkeep").exists()
