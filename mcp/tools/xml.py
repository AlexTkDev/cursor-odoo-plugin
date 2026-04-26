"""Static Odoo XML review."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any

from .common import CheckResult, resolve_existing_file

ID_ATTRS = {"id"}
DEPRECATED_ATTRS = {"attrs", "states"}


def _line_for(content: str, needle: str) -> int | None:
    index = content.find(needle)
    if index < 0:
        return None
    return content[:index].count("\n") + 1


def _safe_xpath_check(expr: str) -> tuple[bool, str | None]:
    normalized = expr.strip()
    if not normalized:
        return False, "empty xpath expression"
    if normalized.startswith("//"):
        normalized = "." + normalized
    try:
        ET.Element("root").findall(normalized)
    except SyntaxError as exc:
        return False, str(exc)
    return True, None


def _review_tree(root: ET.Element, content: str, result: CheckResult) -> None:
    ids: list[str] = []
    for element in root.iter():
        for attr in ID_ATTRS:
            value = element.attrib.get(attr)
            if value:
                ids.append(value)

        for deprecated in DEPRECATED_ATTRS:
            if deprecated in element.attrib:
                result.warning(
                    "deprecated_modifier",
                    f"Legacy XML modifier {deprecated!r} should be reviewed for Odoo 16+ migration readiness",
                    tag=element.tag,
                    attribute=deprecated,
                    line=_line_for(content, deprecated),
                )

        if element.tag == "xpath":
            expr = element.attrib.get("expr", "")
            ok, error = _safe_xpath_check(expr)
            if not ok:
                result.error("bad_xpath", f"Invalid xpath expression: {error}", expr=expr, line=_line_for(content, expr))
            if "position" not in element.attrib:
                result.warning("xpath_missing_position", "xpath nodes should declare position explicitly", expr=expr)

        if element.tag == "field" and element.attrib.get("name") == "inherit_id":
            ref = element.attrib.get("ref")
            if not ref:
                result.warning("inherit_id_without_ref", "inherit_id field should use a ref attribute where possible")
            elif "." not in ref and ref not in ids:
                result.warning(
                    "inherit_id_best_effort",
                    "inherit_id reference is not defined earlier in this file; validate against addon dependencies",
                    ref=ref,
                )

        if element.tag == "field" and element.attrib.get("name") == "arch" and element.text:
            arch_text = element.text.strip()
            if arch_text.startswith("<"):
                try:
                    ET.fromstring(arch_text)
                except ET.ParseError as exc:
                    result.error("malformed_arch", f"Malformed arch XML: {exc}", line=_line_for(content, arch_text[:40]))

    counts = Counter(ids)
    for xml_id, count in counts.items():
        if count > 1:
            result.error("duplicate_xml_id", f"Duplicate XML id: {xml_id}", id=xml_id, count=count)

    for match in re.finditer(r"<field\s+[^>]*name=[\"']([A-Za-z_][\w.]*)[\"'][^>]*/?>", content):
        field_name = match.group(1)
        if field_name in {"name", "model", "arch", "inherit_id", "type", "binding_model_id"}:
            continue
        if field_name.startswith("x_"):
            result.warning(
                "custom_field_best_effort",
                "Custom field reference found; validate that the field exists on the target model",
                field=field_name,
                line=content[: match.start()].count("\n") + 1,
            )


def review_xml(path: str) -> dict[str, Any]:
    """Review an Odoo XML file with static checks."""

    result = CheckResult(metadata={"path": path})
    try:
        xml_path = resolve_existing_file(path)
        content = Path(xml_path).read_text(encoding="utf-8")
        root = ET.fromstring(content)
    except ET.ParseError as exc:
        result.error("xml_parse_error", f"XML parse error: {exc}")
        return result.to_dict()
    except Exception as exc:  # noqa: BLE001 - tool should report structured failures
        result.error("xml_read_error", str(exc))
        return result.to_dict()

    result.metadata.update({"root": root.tag, "ids": 0})
    if root.tag != "odoo":
        result.warning("unexpected_root", "Odoo XML files usually use <odoo> as root", root=root.tag)

    _review_tree(root, content, result)
    result.metadata["ids"] = len([element.attrib["id"] for element in root.iter() if "id" in element.attrib])
    result.metadata["records"] = len([element for element in root.iter() if element.tag == "record"])
    return result.to_dict()
