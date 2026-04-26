---
name: odoo-shell-eval
description: Execute Python code in Odoo shell (restricted mode).
---

# /odoo-shell-eval

Usage:

```txt
/odoo-shell-eval <code> [--odoo-bin odoo-bin] [--database DB] [--config PATH] [--addons-path PATH]
```

Call MCP tool `odoo_shell_eval(code, odoo_bin, database, config, addons_path)` only when allowed and return stdout/stderr.
