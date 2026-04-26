"""Odoo manifest validation."""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from .common import CheckResult, resolve_existing_file

REQUIRED_KEYS = {
    "name": str,
    "version": str,
    "depends": list,
    "license": str,
    "installable": bool,
    "application": bool,
}

OPTIONAL_TYPED_KEYS = {
    "summary": str,
    "description": str,
    "author": str,
    "website": str,
    "category": str,
    "data": list,
    "demo": list,
    "assets": dict,
    "external_dependencies": dict,
    "auto_install": (bool, list),
}

ODOO_VERSION_RE = re.compile(r"^(?:1[6-8]\.0\.)?\d+\.\d+\.\d+(?:\.\d+)?$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
KNOWN_LICENSES = {
    "LGPL-3",
    "AGPL-3",
    "GPL-3",
    "OEEL-1",
    "OPL-1",
    "Other proprietary",
    "MIT",
    "BSD-3",
}


def _literal_manifest(path: Path) -> dict[str, Any]:
    source = path.read_text(encoding="utf-8")
    try:
        parsed = ast.parse(source, filename=str(path), mode="exec")
    except SyntaxError as exc:
        raise ValueError(f"Manifest has invalid Python syntax: {exc}") from exc

    expression: ast.AST | None = None
    if len(parsed.body) == 1 and isinstance(parsed.body[0], ast.Expr):
        expression = parsed.body[0].value
    elif len(parsed.body) == 1 and isinstance(parsed.body[0], ast.Assign):
        expression = parsed.body[0].value

    if expression is None:
        raise ValueError("Manifest must contain a single literal dict expression")

    value = ast.literal_eval(expression)
    if not isinstance(value, dict):
        raise ValueError("Manifest root must be a dict")
    return value


def validate_manifest(path: str) -> dict[str, Any]:
    """Validate an Odoo ``__manifest__.py`` file."""

    result = CheckResult(metadata={"path": path})
    try:
        manifest_path = resolve_existing_file(path)
        manifest = _literal_manifest(manifest_path)
    except Exception as exc:  # noqa: BLE001 - tool should report structured failures
        result.error("manifest_parse_error", str(exc))
        return result.to_dict()

    result.metadata.update(
        {
            "module": manifest_path.parent.name,
            "keys": sorted(manifest.keys()),
            "name": manifest.get("name"),
            "version": manifest.get("version"),
        }
    )

    for key, expected_type in REQUIRED_KEYS.items():
        if key not in manifest:
            result.error("missing_required_key", f"Missing required manifest key: {key}", key=key)
            continue
        if not isinstance(manifest[key], expected_type):
            result.error(
                "invalid_key_type",
                f"Manifest key {key!r} must be {expected_type.__name__}",
                key=key,
                actual_type=type(manifest[key]).__name__,
            )

    for key, expected_type in OPTIONAL_TYPED_KEYS.items():
        if key in manifest and not isinstance(manifest[key], expected_type):
            expected = (
                ", ".join(t.__name__ for t in expected_type)
                if isinstance(expected_type, tuple)
                else expected_type.__name__
            )
            result.error(
                "invalid_key_type",
                f"Manifest key {key!r} must be {expected}",
                key=key,
                actual_type=type(manifest[key]).__name__,
            )

    name = manifest.get("name")
    if isinstance(name, str) and not name.strip():
        result.error("empty_name", "Manifest name must not be empty", key="name")

    version = manifest.get("version")
    if isinstance(version, str) and not (ODOO_VERSION_RE.match(version) or SEMVER_RE.match(version)):
        result.warning(
            "non_semantic_version",
            "Version should use semantic versioning or Odoo addon versioning, e.g. 16.0.1.0.0",
            key="version",
            value=version,
        )

    depends = manifest.get("depends")
    if isinstance(depends, list):
        if not all(isinstance(item, str) and item for item in depends):
            result.error("invalid_depends", "depends must be a list of non-empty strings", key="depends")
        if len(depends) != len(set(depends)):
            result.warning("duplicate_depends", "depends contains duplicate module names", key="depends")

    license_value = manifest.get("license")
    if isinstance(license_value, str) and license_value not in KNOWN_LICENSES:
        result.warning("unknown_license", "License is not a common Odoo/OCA license", value=license_value)

    assets = manifest.get("assets")
    if isinstance(assets, dict):
        for bundle, entries in assets.items():
            if not isinstance(bundle, str) or not isinstance(entries, list):
                result.error("invalid_assets", "assets must map bundle names to lists", key="assets")
                break
            if not all(isinstance(entry, str) for entry in entries):
                result.error("invalid_asset_entry", "asset entries must be strings", bundle=bundle)

    external = manifest.get("external_dependencies")
    if isinstance(external, dict):
        for section, entries in external.items():
            if section not in {"python", "bin"}:
                result.warning("unknown_external_dependency_section", "Expected external dependency section python or bin", section=section)
            if not isinstance(entries, list) or not all(isinstance(entry, str) for entry in entries):
                result.error("invalid_external_dependencies", "external_dependencies sections must be lists of strings", section=section)

    for sequence_key in ("data", "demo"):
        entries = manifest.get(sequence_key)
        if isinstance(entries, list) and not all(isinstance(entry, str) for entry in entries):
            result.error("invalid_manifest_file_list", f"{sequence_key} must be a list of strings", key=sequence_key)

    return result.to_dict()
