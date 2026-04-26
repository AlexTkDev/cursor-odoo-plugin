# Install

## Local Cursor Plugin

From this repository:

```bash
mkdir -p ~/.cursor/plugins/local
ln -s /Users/alex/Documents/my_project/cursor-odoo-plugin ~/.cursor/plugins/local/cursor-odoo-dev
```

Restart Cursor and enable the local plugin if required.

## MCP Smoke Test

```bash
python3 mcp/server.py
```

The server speaks JSON-RPC over stdio. Cursor launches it through `mcp.json`.

## Runtime Tool Setup

Install Python dependencies:

```bash
python3 -m pip install -r mcp/requirements.txt
```

Database introspection:

```bash
export ODOO_DB_DSN='postgresql://user:password@localhost:5432/dbname'
```

For local use, you can export one of:

- ODOO_DB_DSN
- DATABASE_URL

These credentials are project/environment-specific and should not be committed.

Odoo CLI tools:

```bash
export ODOO_RC=/path/to/odoo.conf
```

For runtime tools, provide one of:

- database
- config
- ODOO_RC

and `odoo-bin` path (defaults to `odoo-bin` in PATH).

Only enable shell evaluation in trusted local environments:

```bash
export CURSOR_ODOO_ALLOW_SHELL=1
```

## Works without extra setup

Cross-project safe:

- Scaffold, manifest validation, XML review, migration risk scan, and OCA checks.
- No project-specific env is required.

Needs project setup:

- PostgreSQL-related tools, tests, profiling, and shell execution.
- Set DSN / `ODOO_RC` / `database` per target project.

## Marketplace Publishing

This plugin follows Cursor's public plugin repository shape: a standalone plugin directory with `.cursor-plugin/plugin.json`, `skills/`, `rules/`, `mcp.json`, `README.md`, `CHANGELOG.md`, and `LICENSE`.

Submit through:

```txt
https://cursor.com/marketplace/publish
```

## Development Checks

```bash
python3 -m py_compile mcp/server.py mcp/tools/*.py
pytest
```

Optional quality tools:

```bash
ruff check .
black --check .
pylint-odoo .
xmllint --noout path/to/file.xml
```
