#!/usr/bin/env python3
"""Validate the plugin package shape expected by Cursor Marketplace."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"^[a-z0-9]([a-z0-9.-]*[a-z0-9])?$")
REQUIRED_PLUGIN_KEYS = {"name"}
ALLOWED_PLUGIN_KEYS = {
    "name",
    "displayName",
    "description",
    "version",
    "author",
    "publisher",
    "homepage",
    "repository",
    "license",
    "logo",
    "keywords",
    "category",
    "tags",
    "commands",
    "agents",
    "skills",
    "rules",
    "hooks",
    "mcpServers",
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(relative: str) -> dict:
    path = ROOT / relative
    if not path.exists():
        fail(f"Missing {relative}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON in {relative}: {exc}")


def assert_relative_path(value: str, *, allow_file: bool = True) -> None:
    if value.startswith("/") or ".." in Path(value).parts:
        fail(f"Path must be relative and must not contain '..': {value}")
    path = ROOT / value
    if allow_file:
        exists = path.exists()
    else:
        exists = path.is_dir()
    if not exists:
        fail(f"Referenced path does not exist: {value}")


def validate_frontmatter(path: Path, required: set[str]) -> None:
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        fail(f"Missing YAML frontmatter: {path.relative_to(ROOT)}")
    end = content.find("\n---", 4)
    if end == -1:
        fail(f"Unclosed YAML frontmatter: {path.relative_to(ROOT)}")
    frontmatter = content[4:end]
    keys = {line.split(":", 1)[0].strip() for line in frontmatter.splitlines() if ":" in line}
    missing = required - keys
    if missing:
        fail(f"Missing frontmatter keys {sorted(missing)} in {path.relative_to(ROOT)}")


def validate_plugin_manifest() -> None:
    manifest = load_json(".cursor-plugin/plugin.json")
    missing = REQUIRED_PLUGIN_KEYS - set(manifest)
    if missing:
        fail(f"plugin.json missing required keys: {sorted(missing)}")
    unknown = set(manifest) - ALLOWED_PLUGIN_KEYS
    if unknown:
        fail(f"plugin.json contains unsupported keys: {sorted(unknown)}")
    if not NAME_RE.match(manifest["name"]):
        fail("plugin name must be lowercase kebab-case/dot-case and start/end alphanumeric")

    for key in ("rules", "agents", "skills", "commands"):
        value = manifest.get(key)
        if isinstance(value, str):
            assert_relative_path(value, allow_file=False)
        elif isinstance(value, list):
            for item in value:
                assert_relative_path(item)

    if "hooks" in manifest and isinstance(manifest["hooks"], str):
        assert_relative_path(manifest["hooks"])
    if "mcpServers" in manifest and isinstance(manifest["mcpServers"], str):
        assert_relative_path(manifest["mcpServers"])
    if "logo" in manifest and not manifest["logo"].startswith(("http://", "https://")):
        assert_relative_path(manifest["logo"])


def validate_marketplace() -> None:
    marketplace = load_json(".cursor-plugin/marketplace.json")
    if not NAME_RE.match(marketplace.get("name", "")):
        fail("marketplace name must be kebab-case")
    if "owner" not in marketplace or "name" not in marketplace["owner"]:
        fail("marketplace owner.name is required")
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        fail("marketplace plugins must be a non-empty array")
    names = set()
    for plugin in plugins:
        name = plugin.get("name", "")
        source = plugin.get("source")
        if not NAME_RE.match(name):
            fail(f"Invalid marketplace plugin name: {name}")
        if name in names:
            fail(f"Duplicate marketplace plugin name: {name}")
        names.add(name)
        if not isinstance(source, str):
            fail(f"Marketplace source must be a string for {name}")
        assert_relative_path(source, allow_file=False)


def validate_components() -> None:
    for rule in (ROOT / "rules").glob("*.mdc"):
        validate_frontmatter(rule, {"description", "alwaysApply"})
    for skill in (ROOT / "skills").glob("*/SKILL.md"):
        validate_frontmatter(skill, {"name", "description"})
    for agent in (ROOT / "agents").glob("*.md"):
        validate_frontmatter(agent, {"name", "description"})
    for command in (ROOT / "commands").glob("*"):
        if command.suffix in {".md", ".mdc", ".markdown", ".txt"}:
            validate_frontmatter(command, {"name", "description"})
    hooks = load_json("hooks/hooks.json")
    if "hooks" not in hooks or not isinstance(hooks["hooks"], dict):
        fail("hooks/hooks.json must contain a hooks object")
    mcp = load_json("mcp.json")
    if "mcpServers" not in mcp or "cursor-odoo-dev" not in mcp["mcpServers"]:
        fail("mcp.json must define mcpServers.cursor-odoo-dev")


def validate_no_build_artifacts() -> None:
    forbidden = [path for path in ROOT.rglob("*") if path.name == "__pycache__" or path.suffix == ".pyc"]
    if forbidden:
        fail("Build artifacts found: " + ", ".join(str(path.relative_to(ROOT)) for path in forbidden[:10]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--mcp", action="store_true")
    parser.parse_args()

    validate_plugin_manifest()
    validate_marketplace()
    validate_components()
    validate_no_build_artifacts()
    print("cursor-odoo-dev plugin validation ok")


if __name__ == "__main__":
    main()
