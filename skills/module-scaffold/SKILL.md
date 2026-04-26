---
name: module-scaffold
description: Create production-ready Odoo 16+ addon skeletons with manifest, models, views, security, data, demo, tests, and README.
metadata:
  tags:
    - odoo
    - scaffold
    - module
---

# Module Scaffold Skill

Use when the user asks to create a new Odoo addon or run `/odoo-create-module`.

## Inputs

- `module_name`: required lowercase snake_case technical module name.
- Optional features: `wizard`, `report`, `mail.thread`, `website`, `portal`.

## Workflow

1. Validate the module name before creating files.
2. Generate the standard Odoo addon tree:
   `__manifest__.py`, `__init__.py`, `models/`, `views/`, `security/`, `data/`, `demo/`, `tests/`, `README.md`.
3. Include `security/ir.model.access.csv` for persistent models.
4. Add dependencies only when requested by features:
   `mail` for `mail.thread`, `website` for website, `portal` for portal.
5. Keep generated code simple and migration-friendly.

## Acceptance

- The addon imports cleanly.
- Manifest validates with `validate_manifest`.
- XML validates with `review_xml`.
