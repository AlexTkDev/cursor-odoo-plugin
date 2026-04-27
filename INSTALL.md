# Install

## Install from Cursor Marketplace

After publication, install through Cursor IDE:

1. Open Cursor.
2. Go to Settings.
3. Open Plugins.
4. Search for `Cursor Odoo Developer Plugin`.
5. Install and enable it.

## Local development install

For local testing before marketplace approval:

```bash
mkdir -p ~/.cursor/plugins/local
ln -s /Users/alex/Documents/my_project/cursor-odoo-plugin ~/.cursor/plugins/local/cursor-odoo-dev
```

Restart Cursor and enable `cursor-odoo-dev` in Settings -> Plugins.

## Install dependencies

```bash
python3 -m pip install -r mcp/requirements.txt
```

## Recommended environment variables

- For database tools:
  - `ODOO_DB_DSN='postgresql://user:password@localhost:5432/dbname'`
  - or `DATABASE_URL`
- For Odoo runtime tools:
  - `ODOO_RC=/path/to/odoo.conf` or `config`
  - `database`
  - `odoo-bin` in `PATH` (or full path to binary)
- For hardened file validation in manifest/XML tools:
  - `CURSOR_ODOO_ALLOW_ABSOLUTE_PATHS=1` to accept absolute paths.
  - Default behavior is safer: relative paths only, no path traversal with `..`.
- Shell is enabled only in trusted setups:

```bash
export CURSOR_ODOO_ALLOW_SHELL=1
```

Keep credentials local. Do not commit secrets to the repository.
