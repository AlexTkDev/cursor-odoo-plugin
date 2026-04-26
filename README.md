# Cursor Odoo Developer Plugin

`cursor-odoo-dev` is a Cursor plugin for Odoo 16+ development.

It provides:

- Odoo Python, XML, security, performance, and OCA rules.
- Module scaffold guidance and MCP-backed addon generation.
- Manifest validation with safe `ast.literal_eval`.
- Static XML review for Odoo views and data files.
- V2/V3 MCP placeholders for database introspection, migrations, OCA review, shell, tests, and profiling.

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

V2 placeholders:

- `db_list_models()`
- `db_describe_model(model)`
- `db_missing_indexes()`
- `analyze_migration(module_path, source_version, target_version)`
- `check_oca_compliance(module_path)`

V3 placeholders:

- `odoo_shell_eval(code)`
- `run_odoo_tests(module)`
- `profile_module(module)`

## Project Tree

```txt
.
├── .cursor-plugin/
├── rules/
├── skills/
├── commands/
├── hooks/
├── mcp/
└── tests/
```

## Migration Notes

This repository started as a local Odoo/Cursor workspace with ignored `.cursor`, `.agent`, `.gemini`, `.vscode`, and `mcp_server` folders. The plugin source now lives in tracked root-level plugin folders. Local machine state and old server logs remain excluded.

The old `mcp_server/server.py` was intentionally not copied directly because it used absolute project paths and unsafe manifest `eval()`. V1 implements safe modular tools under `mcp/tools/`.
