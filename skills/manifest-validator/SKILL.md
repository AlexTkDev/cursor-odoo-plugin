---
name: manifest-validator
description: Validate Odoo 16+ __manifest__.py files for required keys, versioning, dependencies, assets, and external dependencies.
metadata:
  tags:
    - odoo
    - manifest
    - validation
---

# Manifest Validator Skill

Use when the user asks to validate or review an Odoo manifest or runs `/odoo-validate-manifest`.

## Workflow

1. Locate `__manifest__.py`.
2. Call MCP tool `validate_manifest(path)`.
3. Report blocking errors first, then warnings.
4. Recommend minimal manifest changes that preserve module intent.

## Checks

- Required keys and value types.
- `name`, `version`, `depends`, `license`, `installable`, `application`.
- `assets` and `external_dependencies` structure.
- Odoo/OCA-style semantic versioning.
