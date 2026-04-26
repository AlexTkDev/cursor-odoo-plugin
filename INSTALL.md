# Install

## Install the plugin in Cursor

1. Make sure Cursor is installed.
2. Register this repository as a local plugin:

```bash
mkdir -p ~/.cursor/plugins/local
ln -s /Users/alex/Documents/my_project/cursor-odoo-plugin ~/.cursor/plugins/local/cursor-odoo-dev
```

3. Restart Cursor.
4. Enable `cursor-odoo-dev` in plugins list.

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
- Shell is enabled only in trusted setups:

```bash
export CURSOR_ODOO_ALLOW_SHELL=1
```

Keep credentials local. Do not commit secrets to the repository.
