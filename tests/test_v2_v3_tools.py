from pathlib import Path

from mcp.tools.migration import analyze_migration
from mcp.tools.oca import check_oca_compliance
from mcp.tools.profiler import profile_module
from mcp.tools.shell import odoo_shell_eval
from mcp.tools.tests import run_odoo_tests


def _write_minimal_module(root: Path) -> Path:
    module = root / "demo_addon"
    (module / "models").mkdir(parents=True)
    (module / "views").mkdir()
    (module / "security").mkdir()
    (module / "tests").mkdir()
    (module / "__init__.py").write_text("from . import models\n", encoding="utf-8")
    (module / "models" / "__init__.py").write_text("from . import demo\n", encoding="utf-8")
    (module / "models" / "demo.py").write_text(
        "from odoo import fields, models\n\n"
        "class Demo(models.Model):\n"
        "    _name = 'demo.addon'\n"
        "    _description = 'Demo Addon'\n"
        "    name = fields.Char(required=True)\n",
        encoding="utf-8",
    )
    (module / "__manifest__.py").write_text(
        "{\n"
        "    'name': 'Demo Addon',\n"
        "    'version': '16.0.1.0.0',\n"
        "    'depends': ['base'],\n"
        "    'license': 'LGPL-3',\n"
        "    'installable': True,\n"
        "    'application': False,\n"
        "    'data': ['security/ir.model.access.csv', 'views/demo_views.xml'],\n"
        "}\n",
        encoding="utf-8",
    )
    (module / "security" / "ir.model.access.csv").write_text(
        "id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink\n"
        "access_demo_addon_user,demo user,model_demo_addon,base.group_user,1,1,1,0\n",
        encoding="utf-8",
    )
    (module / "views" / "demo_views.xml").write_text(
        "<odoo><record id=\"demo_view\" model=\"ir.ui.view\"><field name=\"arch\" type=\"xml\"><tree attrs=\"{}\"/></field></record></odoo>",
        encoding="utf-8",
    )
    return module


def test_analyze_migration_static_warnings(tmp_path: Path) -> None:
    module = _write_minimal_module(tmp_path)

    result = analyze_migration(str(module), "16", "17")

    assert result["ok"] is True
    assert any(warning["code"] == "odoo17_attrs_removed" for warning in result["warnings"])


def test_check_oca_compliance_scores_module(tmp_path: Path) -> None:
    module = _write_minimal_module(tmp_path)
    (module / "README.md").write_text("# Demo\n", encoding="utf-8")

    result = check_oca_compliance(str(module))

    assert result["ok"] is True
    assert "score" in result["data"]


def test_shell_is_disabled_by_default() -> None:
    result = odoo_shell_eval("print(env)")

    assert result["ok"] is False
    assert result["errors"][0]["code"] == "shell_disabled"


def test_runtime_tools_require_target() -> None:
    test_result = run_odoo_tests("demo_addon")
    profile_result = profile_module("demo_addon")

    assert test_result["errors"][0]["code"] == "missing_runtime_target"
    assert profile_result["errors"][0]["code"] == "missing_runtime_target"
