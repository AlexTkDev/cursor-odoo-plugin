"""Static Odoo migration analysis."""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from .common import error_result, tool_result
from .manifest import validate_manifest
from .xml import review_xml

SUPPORTED_PAIRS = {("16", "17"), ("17", "18")}


def _files(root: Path, suffixes: tuple[str, ...]) -> list[Path]:
    ignored = {"__pycache__", ".git", ".pytest_cache", ".ruff_cache"}
    return [
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix in suffixes and not any(part in ignored for part in path.parts)
    ]


def _line(content: str, index: int) -> int:
    return content[:index].count("\n") + 1


def _scan_xml(path: Path, source_version: str, target_version: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    review = review_xml(str(path))
    for error in review["errors"]:
        errors.append({"file": str(path), **error})
    for warning in review["warnings"]:
        warnings.append({"file": str(path), **warning})

    content = path.read_text(encoding="utf-8", errors="ignore")
    if (source_version, target_version) == ("16", "17"):
        for pattern, code, message in [
            (r"\battrs\s*=", "odoo17_attrs_removed", "Odoo 17 removed legacy attrs modifiers; convert to inline expressions."),
            (r"\bstates\s*=", "odoo17_states_removed", "Odoo 17 removed legacy states modifiers; convert to inline expressions."),
            (r"<tree\b", "odoo17_tree_review", "Review tree views for Odoo 17 list view syntax expectations."),
        ]:
            for match in re.finditer(pattern, content):
                warnings.append({"code": code, "message": message, "file": str(path), "line": _line(content, match.start())})

    if (source_version, target_version) == ("17", "18"):
        for match in re.finditer(r"web\.assets_(?:backend|frontend|qweb)", content):
            warnings.append(
                {
                    "code": "odoo18_assets_review",
                    "message": "Review asset bundle compatibility for Odoo 18.",
                    "file": str(path),
                    "line": _line(content, match.start()),
                }
            )
    return errors, warnings


def _scan_python(path: Path, source_version: str, target_version: str) -> list[dict[str, Any]]:
    warnings: list[dict[str, Any]] = []
    content = path.read_text(encoding="utf-8", errors="ignore")

    patterns = [
        (r"@api\.multi\b", "removed_api_multi", "@api.multi is obsolete; remove it and use recordset-aware methods."),
        (r"@api\.one\b", "removed_api_one", "@api.one is obsolete; iterate over self explicitly."),
        (r"\.sudo\(\)", "sudo_review", "Review sudo() use before migration; document the access boundary."),
        (r"\.cr\.execute\(", "raw_sql_review", "Review raw SQL for schema/API changes and parameterization."),
    ]
    if (source_version, target_version) == ("16", "17"):
        patterns.extend(
            [
                (r"\bactive_id\b", "context_active_id_review", "Review context active_id assumptions in Odoo 17 client flows."),
                (r"\bactive_ids\b", "context_active_ids_review", "Review context active_ids assumptions in Odoo 17 client flows."),
            ]
        )

    for pattern, code, message in patterns:
        for match in re.finditer(pattern, content):
            warnings.append({"code": code, "message": message, "file": str(path), "line": _line(content, match.start())})

    try:
        ast.parse(content, filename=str(path))
    except SyntaxError as exc:
        warnings.append({"code": "python_syntax_error", "message": str(exc), "file": str(path), "line": exc.lineno})
    return warnings


def analyze_migration(module_path: str, source_version: str, target_version: str) -> dict[str, Any]:
    """Analyze an addon for known Odoo 16->17 and 17->18 migration risks."""

    pair = (str(source_version), str(target_version))
    if pair not in SUPPORTED_PAIRS:
        return error_result(
            "unsupported_migration_pair",
            "Supported migration pairs are 16->17 and 17->18.",
            source_version=source_version,
            target_version=target_version,
        )

    root = Path(module_path).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        return error_result("invalid_module_path", f"Module path is not a directory: {module_path}", module_path=str(root))

    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    manifest_path = root / "__manifest__.py"
    if manifest_path.exists():
        manifest_result = validate_manifest(str(manifest_path))
        errors.extend({"file": str(manifest_path), **error} for error in manifest_result["errors"])
        warnings.extend({"file": str(manifest_path), **warning} for warning in manifest_result["warnings"])
    else:
        errors.append({"code": "missing_manifest", "message": "Missing __manifest__.py", "file": str(manifest_path)})

    for xml_file in _files(root, (".xml",)):
        xml_errors, xml_warnings = _scan_xml(xml_file, pair[0], pair[1])
        errors.extend(xml_errors)
        warnings.extend(xml_warnings)

    for py_file in _files(root, (".py",)):
        warnings.extend(_scan_python(py_file, pair[0], pair[1]))

    migration_dir = root / "migrations" / f"{target_version}.0.1.0.0"
    if not migration_dir.exists():
        warnings.append(
            {
                "code": "missing_migration_directory",
                "message": "No target-version migration directory found; add one if schema/data changes are required.",
                "expected": str(migration_dir),
            }
        )

    return tool_result(
        not errors,
        errors=errors,
        warnings=warnings,
        metadata={
            "module_path": str(root),
            "source_version": source_version,
            "target_version": target_version,
            "python_files": len(_files(root, (".py",))),
            "xml_files": len(_files(root, (".xml",))),
        },
        data={"risk_count": len(errors) + len(warnings)},
    )
