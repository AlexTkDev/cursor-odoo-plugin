---
name: xml-review
description: Review Odoo XML files for parse errors, duplicate IDs, inheritance problems, xpaths, deprecated attrs/states, and malformed arch.
metadata:
  tags:
    - odoo
    - xml
    - views
---

# XML Review Skill

Use when the user asks to inspect Odoo XML or runs `/odoo-review-xml`.

## Workflow

1. Locate the target XML file or module XML files.
2. Call MCP tool `review_xml(path)`.
3. Separate definite errors from static-analysis warnings.
4. For `inherit_id`, fields, and xpath issues, note whether the check is static best-effort or registry-backed.

## Checks

- XML parse.
- Duplicate XML IDs.
- Suspicious or broken `inherit_id`.
- Bad xpath syntax and missing `position`.
- Obsolete `attrs` and `states`.
- Missing fields where statically visible.
- Malformed `arch`.
