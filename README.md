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
- `/odoo-check-oca-compliance <module_path>`
- `/odoo-db-list-models [--dsn DSN]`
- `/odoo-db-describe-model <model_name> [--dsn DSN]`
- `/odoo-db-missing-indexes [--dsn DSN] [--min-seq-scan N]`
- `/odoo-run-tests <module_name>`
- `/odoo-profile-module <module_name> [--mode tests|install]`
- `/odoo-shell-eval <python_code>`

## Works out of the box

- Module scaffolding
- Manifest validation
- XML validation
- OCA check
- Quick migration analysis
- DB metadata tools
- Odoo runtime test/profiler helpers

## Agent automation

- Every user goal should map to exactly one MCP tool and follow this pattern:
  - `/odoo-create-module` → `create_module`
  - `/odoo-validate-manifest` → `validate_manifest`
  - `/odoo-review-xml` → `review_xml`
  - `/odoo-migrate-module` → `analyze_migration`
  - `/odoo-check-oca-compliance` → `check_oca_compliance`
  - `/odoo-db-list-models` → `db_list_models`
  - `/odoo-db-describe-model` → `db_describe_model`
  - `/odoo-db-missing-indexes` → `db_missing_indexes`
  - `/odoo-run-tests` → `run_odoo_tests`
  - `/odoo-profile-module` → `profile_module`
  - `/odoo-shell-eval` → `odoo_shell_eval`

## Requires project/runtime setup

- PostgreSQL tools: `psycopg` and DSN via `ODOO_DB_DSN` or `DATABASE_URL`.
- Odoo runtime tools (`tests`, `profile`, shell): `odoo-bin` plus one of `database`, `config`, `ODOO_RC`.
- `odoo_shell_eval` is available only when `CURSOR_ODOO_ALLOW_SHELL=1`.
- File-based tools (`validate_manifest`, `review_xml`) reject absolute paths and `..` traversal by default.
- To allow absolute paths intentionally, set `CURSOR_ODOO_ALLOW_ABSOLUTE_PATHS=1`.

For install and setup details, see `INSTALL.md`.
