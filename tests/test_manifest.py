from pathlib import Path

from mcp.tools.manifest import validate_manifest


def test_validate_manifest_ok(tmp_path: Path) -> None:
    manifest = tmp_path / "__manifest__.py"
    manifest.write_text(
        "{\n"
        "    'name': 'Demo',\n"
        "    'version': '16.0.1.0.0',\n"
        "    'depends': ['base'],\n"
        "    'license': 'LGPL-3',\n"
        "    'installable': True,\n"
        "    'application': False,\n"
        "    'assets': {'web.assets_backend': ['demo/static/src/js/demo.js']},\n"
        "    'external_dependencies': {'python': ['requests']},\n"
        "}\n",
        encoding="utf-8",
    )

    result = validate_manifest(str(manifest))

    assert result["ok"] is True
    assert result["errors"] == []


def test_validate_manifest_missing_required_key(tmp_path: Path) -> None:
    manifest = tmp_path / "__manifest__.py"
    manifest.write_text("{'name': 'Demo'}\n", encoding="utf-8")

    result = validate_manifest(str(manifest))

    assert result["ok"] is False
    assert any(error["code"] == "missing_required_key" for error in result["errors"])


def test_validate_manifest_rejects_non_literal(tmp_path: Path) -> None:
    manifest = tmp_path / "__manifest__.py"
    manifest.write_text("__import__('os').system('echo nope')\n", encoding="utf-8")

    result = validate_manifest(str(manifest))

    assert result["ok"] is False
    assert result["errors"][0]["code"] == "manifest_parse_error"
