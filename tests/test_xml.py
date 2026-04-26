from pathlib import Path

from mcp.tools.xml import review_xml


def test_review_xml_ok(tmp_path: Path) -> None:
    xml_file = tmp_path / "views.xml"
    xml_file.write_text(
        "<odoo>\n"
        "  <record id=\"demo_view_form\" model=\"ir.ui.view\">\n"
        "    <field name=\"name\">demo.form</field>\n"
        "    <field name=\"model\">demo.model</field>\n"
        "    <field name=\"arch\" type=\"xml\">\n"
        "      <form><field name=\"name\"/></form>\n"
        "    </field>\n"
        "  </record>\n"
        "</odoo>\n",
        encoding="utf-8",
    )

    result = review_xml(str(xml_file))

    assert result["ok"] is True
    assert result["errors"] == []


def test_review_xml_parse_error(tmp_path: Path) -> None:
    xml_file = tmp_path / "broken.xml"
    xml_file.write_text("<odoo><record></odoo>", encoding="utf-8")

    result = review_xml(str(xml_file))

    assert result["ok"] is False
    assert result["errors"][0]["code"] == "xml_parse_error"


def test_review_xml_duplicate_id_and_deprecated_attrs(tmp_path: Path) -> None:
    xml_file = tmp_path / "bad.xml"
    xml_file.write_text(
        "<odoo>\n"
        "  <record id=\"same\" model=\"ir.ui.view\"/>\n"
        "  <record id=\"same\" model=\"ir.ui.view\">\n"
        "    <field name=\"arch\" type=\"xml\">\n"
        "      <form attrs=\"{'invisible': True}\"/>\n"
        "    </field>\n"
        "  </record>\n"
        "</odoo>\n",
        encoding="utf-8",
    )

    result = review_xml(str(xml_file))

    assert result["ok"] is False
    assert any(error["code"] == "duplicate_xml_id" for error in result["errors"])
    assert any(warning["code"] == "deprecated_modifier" for warning in result["warnings"])
