"""Static OCA compliance checks."""

from __future__ import annotations

import ast
import csv
from pathlib import Path
from typing import Any

from .common import error_result, tool_result
from .manifest import validate_manifest

ALLOWED_LICENSES = {"AGPL-3", "LGPL-3", "GPL-3"}


def _load_manifest(path: Path) -> dict[str, Any] | None:
    try:
        value = ast.literal_eval(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None
    return value if isinstance(value, dict) else None


def _python_model_names(root: Path) -> set[str]:
    models: set[str] = set()
    for path in root.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        try:
            tree = ast.parse(content, filename=str(path))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "_name" and isinstance(node.value, ast.Constant):
                        if isinstance(node.value.value, str):
                            models.add(node.value.value)
    return models


def _acl_models(access_csv: Path) -> set[str]:
    models: set[str] = set()
    if not access_csv.exists():
        return models
    with access_csv.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            model_id = row.get("model_id:id") or ""
            if model_id.startswith("model_"):
                models.add(model_id.removeprefix("model_").replace("_", "."))
    return models


def check_oca_compliance(module_path: str) -> dict[str, Any]:
    """Run static OCA-oriented addon checks."""

    root = Path(module_path).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        return error_result("invalid_module_path", f"Module path is not a directory: {module_path}", module_path=str(root))

    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    required_paths = ["__manifest__.py", "__init__.py", "README.md"]
    for relative in required_paths:
        if not (root / relative).exists():
            errors.append({"code": "missing_required_file", "message": f"Missing {relative}", "path": str(root / relative)})

    manifest_path = root / "__manifest__.py"
    manifest: dict[str, Any] | None = None
    if manifest_path.exists():
        manifest_result = validate_manifest(str(manifest_path))
        errors.extend({"file": str(manifest_path), **error} for error in manifest_result["errors"])
        warnings.extend({"file": str(manifest_path), **warning} for warning in manifest_result["warnings"])
        manifest = _load_manifest(manifest_path)

    if manifest:
        license_value = manifest.get("license")
        if license_value not in ALLOWED_LICENSES:
            warnings.append(
                {
                    "code": "oca_license_review",
                    "message": "OCA addons usually use AGPL-3, LGPL-3, or GPL-3.",
                    "value": license_value,
                }
            )
        if "maintainers" not in manifest:
            warnings.append({"code": "missing_maintainers", "message": "OCA modules usually declare maintainers."})
        if "development_status" not in manifest:
            warnings.append({"code": "missing_development_status", "message": "Consider adding development_status metadata."})

    model_names = _python_model_names(root)
    acl_path = root / "security" / "ir.model.access.csv"
    acl_names = _acl_models(acl_path)
    if model_names and not acl_path.exists():
        errors.append({"code": "missing_acl_csv", "message": "Persistent models require security/ir.model.access.csv."})
    for model in sorted(model_names - acl_names):
        warnings.append(
            {
                "code": "missing_acl_for_model",
                "message": "No ACL row found for model; verify whether it is abstract/transient or intentionally internal.",
                "model": model,
            }
        )

    if not (root / "tests").exists():
        warnings.append({"code": "missing_tests_dir", "message": "OCA modules should include focused tests for behavior/security."})

    for path in root.rglob("*"):
        if path.is_file() and "__pycache__" not in path.parts and path.name in {".DS_Store"}:
            warnings.append({"code": "junk_file", "message": "Remove local junk files before publishing.", "path": str(path)})

    return tool_result(
        not errors,
        errors=errors,
        warnings=warnings,
        metadata={"module_path": str(root), "models": sorted(model_names), "acl_models": sorted(acl_names)},
        data={"score": max(0, 100 - len(errors) * 20 - len(warnings) * 5)},
    )
