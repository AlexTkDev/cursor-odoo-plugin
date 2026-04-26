---
name: migration-assistant
description: Static Odoo 16 to 17 and 17 to 18 migration analysis.
metadata:
  tags:
    - odoo
    - migration
---

# Migration Assistant Skill

Use for migration planning. Call MCP tool `analyze_migration(module_path, source_version, target_version)` to detect manifest, XML, Python, and migration-directory risks.

Supported target pairs are `16->17` and `17->18`.
