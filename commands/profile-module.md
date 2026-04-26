---
name: odoo-profile-module
description: Profile an Odoo module install/test path with debug SQL output.
---

# /odoo-profile-module

Usage:

```txt
/odoo-profile-module <module_name> [--mode tests|install] [--odoo-bin odoo-bin] [--database DB] [--config PATH] [--addons-path PATH]
```

Call MCP tool `profile_module(module, odoo_bin, database, config, addons_path, mode)` and return profiler output summary.
