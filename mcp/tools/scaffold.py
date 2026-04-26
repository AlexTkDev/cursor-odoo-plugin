"""Odoo module scaffold generator."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

MODULE_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def _model_name(module_name: str) -> str:
    return module_name.replace("_", ".")


def _class_name(module_name: str) -> str:
    return "".join(part.capitalize() for part in module_name.split("_"))


def create_module(
    module_name: str,
    target_dir: str = ".",
    wizard: bool = False,
    report: bool = False,
    mail_thread: bool = False,
    website: bool = False,
    portal: bool = False,
) -> dict[str, Any]:
    """Create an Odoo addon skeleton."""

    if not MODULE_RE.match(module_name):
        return {
            "ok": False,
            "errors": [
                {
                    "code": "invalid_module_name",
                    "message": "Module name must be lowercase snake_case and start with a letter.",
                }
            ],
            "warnings": [],
            "metadata": {"module": module_name},
        }

    root = Path(target_dir).expanduser().resolve() / module_name
    if root.exists():
        return {
            "ok": False,
            "errors": [{"code": "module_exists", "message": f"Target module already exists: {root}"}],
            "warnings": [],
            "metadata": {"path": str(root)},
        }

    depends = ["base"]
    if mail_thread:
        depends.append("mail")
    if website:
        depends.append("website")
    if portal:
        depends.append("portal")

    model = _model_name(module_name)
    cls = _class_name(module_name)
    created: list[str] = []

    def write(relative: str, content: str = "") -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        created.append(str(path))

    root.mkdir(parents=True)

    manifest_data = [
        "security/ir.model.access.csv",
        f"views/{module_name}_views.xml",
    ]
    write(
        "__manifest__.py",
        "{\n"
        f"    'name': '{cls}',\n"
        f"    'version': '16.0.1.0.0',\n"
        f"    'summary': 'Odoo addon for {module_name}',\n"
        "    'license': 'LGPL-3',\n"
        f"    'depends': {depends!r},\n"
        f"    'data': {manifest_data!r},\n"
        "    'demo': [],\n"
        "    'installable': True,\n"
        "    'application': False,\n"
        "}\n",
    )
    write("__init__.py", "from . import models\n")
    write("models/__init__.py", f"from . import {module_name}\n")

    model_content = (
        "from odoo import fields, models\n\n\n"
        f"class {cls}(models.Model):\n"
        f"    _name = '{model}'\n"
        f"    _description = '{cls}'\n\n"
        "    name = fields.Char(required=True)\n"
    )
    if mail_thread:
        model_content = (
            "from odoo import fields, models\n\n\n"
            f"class {cls}(models.Model):\n"
            f"    _name = '{model}'\n"
            f"    _description = '{cls}'\n"
            f"    _inherit = ['mail.thread', 'mail.activity.mixin']\n\n"
            "    name = fields.Char(required=True, tracking=True)\n"
        )
    write(f"models/{module_name}.py", model_content)

    write(
        f"views/{module_name}_views.xml",
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        "<odoo>\n"
        f"    <record id=\"{module_name}_view_tree\" model=\"ir.ui.view\">\n"
        f"        <field name=\"name\">{model}.tree</field>\n"
        f"        <field name=\"model\">{model}</field>\n"
        "        <field name=\"arch\" type=\"xml\">\n"
        "            <tree>\n"
        "                <field name=\"name\"/>\n"
        "            </tree>\n"
        "        </field>\n"
        "    </record>\n\n"
        f"    <record id=\"{module_name}_view_form\" model=\"ir.ui.view\">\n"
        f"        <field name=\"name\">{model}.form</field>\n"
        f"        <field name=\"model\">{model}</field>\n"
        "        <field name=\"arch\" type=\"xml\">\n"
        "            <form>\n"
        "                <sheet>\n"
        "                    <group>\n"
        "                        <field name=\"name\"/>\n"
        "                    </group>\n"
        "                </sheet>\n"
        "            </form>\n"
        "        </field>\n"
        "    </record>\n\n"
        f"    <record id=\"{module_name}_action\" model=\"ir.actions.act_window\">\n"
        f"        <field name=\"name\">{cls}</field>\n"
        f"        <field name=\"res_model\">{model}</field>\n"
        "        <field name=\"view_mode\">tree,form</field>\n"
        "    </record>\n\n"
        f"    <menuitem id=\"{module_name}_menu_root\" name=\"{cls}\"/>\n"
        f"    <menuitem id=\"{module_name}_menu\" name=\"{cls}\" parent=\"{module_name}_menu_root\" action=\"{module_name}_action\"/>\n"
        "</odoo>\n",
    )
    write(
        "security/ir.model.access.csv",
        "id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink\n"
        f"access_{module_name}_user,{module_name} user,model_{module_name},base.group_user,1,1,1,0\n",
    )
    write("README.md", f"# {cls}\n\nOdoo 16+ addon scaffold generated by cursor-odoo-dev.\n")
    write("data/.gitkeep")
    write("demo/.gitkeep")
    write("tests/.gitkeep")

    if wizard:
        write("wizards/.gitkeep")
    if report:
        write("reports/.gitkeep")

    return {
        "ok": True,
        "errors": [],
        "warnings": [],
        "metadata": {
            "module": module_name,
            "path": str(root),
            "features": {
                "wizard": wizard,
                "report": report,
                "mail_thread": mail_thread,
                "website": website,
                "portal": portal,
            },
            "created": created,
        },
    }
