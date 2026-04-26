# Cursor Odoo Developer Plugin

`cursor-odoo-dev` is a Cursor plugin for Odoo 16+ development.

It provides:

- Odoo Python, XML, security, performance, and OCA rules.
- Module scaffold guidance and MCP-backed addon generation.
- Manifest validation with safe `ast.literal_eval`.
- Static XML review for Odoo views and data files.
- PostgreSQL introspection, migration analysis, OCA checks, Odoo shell bridge, test runner, and profiling tools.

## Commands

- `/odoo-create-module <module_name>`
- `/odoo-validate-manifest <path/to/__manifest__.py>`
- `/odoo-review-xml <path/to/file.xml>`
- `/odoo-create-model <module_name> <model_name>`
- `/odoo-create-wizard <module_name> <wizard_name>`
- `/odoo-create-security <module_name>`
- `/odoo-migrate-module <module_path> --from 16 --to 17`

## MCP Tools

V1:

- `create_module(module_name, target_dir=".", wizard=False, report=False, mail_thread=False, website=False, portal=False)`
- `validate_manifest(path)`
- `review_xml(path)`

V2:

- `db_list_models(dsn=None)`
- `db_describe_model(model, dsn=None)`
- `db_missing_indexes(dsn=None, min_seq_scan=1000)`
- `analyze_migration(module_path, source_version, target_version)`
- `check_oca_compliance(module_path)`

V3:

- `odoo_shell_eval(code, odoo_bin="odoo-bin", database=None, config=None, addons_path=None, timeout=300)`
- `run_odoo_tests(module, odoo_bin="odoo-bin", database=None, config=None, addons_path=None, timeout=1800, extra_args=None)`
- `profile_module(module, odoo_bin="odoo-bin", database=None, config=None, addons_path=None, timeout=1800, mode="tests")`

## Runtime Configuration

PostgreSQL tools require `psycopg` and a DSN through the `dsn` argument, `ODOO_DB_DSN`, or `DATABASE_URL`.

Odoo runtime tools require an `odoo-bin` executable plus either `database`, `config`, or `ODOO_RC`. The shell bridge is disabled by default and only runs when `CURSOR_ODOO_ALLOW_SHELL=1` is set.

All runtime commands use argument lists, timeouts, captured output, and no shell interpolation.

## Compatibility across projects

This plugin is intended to work in different repositories.

Zero-config tools (safe by default):

- `validate_manifest` and `/odoo-validate-manifest`
- `review_xml` and `/odoo-review-xml`
- `create_module` and `/odoo-create-module`
 - `check_oca_compliance`
- `analyze_migration`

Project-bound tools (require explicit environment or arguments):

- PostgreSQL tools: provide `dsn` or set `ODOO_DB_DSN` / `DATABASE_URL`.
- Odoo runtime tools (`odoo_shell_eval`, `run_odoo_tests`, `profile_module`): provide `odoo_bin` and one of `database` / `config` / `ODOO_RC`.
- `odoo_shell_eval` is intentionally disabled until `CURSOR_ODOO_ALLOW_SHELL=1`.

Recommended usage:

1. Use zero-config tools for scaffolding/review tasks immediately after install.
2. Set project runtime env for test/profile/shell/db tasks.
3. Keep credentials only in your local shell/session or secrets manager, never in repository files.

## Project Tree

```txt
.
├── .cursor-plugin/
├── rules/
├── skills/
├── agents/
├── commands/
├── hooks/
├── assets/
├── scripts/
├── mcp/
└── tests/
```

## Migration Notes

This repository started as a local Odoo/Cursor workspace with ignored `.cursor`, `.agent`, `.gemini`, `.vscode`, and `mcp_server` folders. The plugin source now lives in tracked root-level plugin folders. Local machine state and old server logs remain excluded.

The old `mcp_server/server.py` was intentionally not copied directly because it used absolute project paths and unsafe manifest `eval()`. The plugin implements safe modular tools under `mcp/tools/`.
