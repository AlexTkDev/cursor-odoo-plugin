---
name: odoo-run-tests
description: Run Odoo module tests through odoo-bin.
---

# /odoo-run-tests

Usage:

```txt
/odoo-run-tests <module_name> [--odoo-bin odoo-bin] [--database DB] [--config PATH] [--addons-path PATH]
```

Call MCP tool `run_odoo_tests(module, odoo_bin, database, config, addons_path)` and return execution result.
