---
name: migration-assistant
description: Placeholder skill for Odoo 16 to 17 and 17 to 18 migration analysis.
metadata:
  tags:
    - odoo
    - migration
---

# Migration Assistant Skill

Use for migration planning. V1 registers the MCP placeholder `analyze_migration(module_path, source_version, target_version)` and returns a stable `not_implemented` payload.

Current supported target pairs for planning are `16->17` and `17->18`.
