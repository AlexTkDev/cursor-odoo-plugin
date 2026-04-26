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
