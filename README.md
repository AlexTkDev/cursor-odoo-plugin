# Cursor Odoo Developer Plugin

A Cursor plugin to work efficiently with Odoo 16+.

## What it does

- Scaffolds a new Odoo module.
- Validates `__manifest__.py` before commit.
- Validates Odoo XML files (`views`, `data`) for common issues.
- Runs migration checks between Odoo versions.
- Checks against OCA compliance rules.
- Supports PostgreSQL and Odoo test/profiler workflows when environment is configured.

## Cursor commands

- `/odoo-create-module <module_name>`
- `/odoo-validate-manifest <path/to/__manifest__.py>`
- `/odoo-review-xml <path/to/file.xml>`
- `/odoo-migrate-module <module_path> --from 16 --to 17`

## Works out of the box

- Module scaffolding
- Manifest validation
- XML validation
- OCA check
- Quick migration analysis

## Requires project/runtime setup

- PostgreSQL tools: `psycopg` and DSN via `ODOO_DB_DSN` or `DATABASE_URL`.
- Odoo runtime tools (`tests`, `profile`, shell): `odoo-bin` plus one of `database`, `config`, `ODOO_RC`.
- `odoo_shell_eval` is available only when `CURSOR_ODOO_ALLOW_SHELL=1`.

For install and setup details, see `INSTALL.md`.
