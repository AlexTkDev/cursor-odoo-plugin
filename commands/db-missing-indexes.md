---
name: odoo-db-missing-indexes
description: Find tables with heavy sequential scans for index review.
---

# /odoo-db-missing-indexes

Usage:

```txt
/odoo-db-missing-indexes [--dsn DSN] [--min-seq-scan 1000]
```

Call MCP tool `db_missing_indexes(dsn, min_seq_scan)` and return ranked index candidates.
