---
name: odoo-mcp-orchestrator
description: Always choose MCP-first execution path for Odoo tooling tasks.
---

# Odoo MCP Orchestrator Skill

Use when user asks for any Odoo operation and the expected path is deterministic.

Rules:

1. Call one MCP tool per intent and avoid speculative tool calls.
2. Return blocking errors before non-blocking warnings.
3. Ask for confirmation before risky runtime actions:
- DB writes
- `odoo_shell_eval` (requires `CURSOR_ODOO_ALLOW_SHELL=1`).
