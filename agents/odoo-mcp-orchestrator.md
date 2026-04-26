---
name: odoo-mcp-orchestrator
description: Route user intent to a concrete MCP tool and report structured results.
---

# /odoo-mcp-orchestrator

Use this agent when the user requests any action on an Odoo module.

Workflow:

1. Clarify the objective:
- Create/modify module structure.
- Validate code/data correctness.
- Diagnose migration or performance.
- Validate database/model state.

2. Call the matching MCP tool:
- `create_module`
- `validate_manifest`
- `review_xml`
- `analyze_migration`
- `check_oca_compliance`
- `db_list_models` / `db_describe_model` / `db_missing_indexes`
- `run_odoo_tests`
- `profile_module`
- `odoo_shell_eval` (only in permitted safe mode)

3. Return results in structure:
- blocking issues (`errors`) → blocking,
- `warnings` → recommendations,
- `metadata`/`data` → context for next step.

4. Do not run more than one runtime tool until the user confirms continuation.
