# Changelog

## 1.0.1

- Added CLI command coverage for all MCP tools (`/odoo-check-oca-compliance`, DB tools, runtime test/profile, shell eval).
- Added agent orchestration rule + dedicated MCP orchestration agent and skill for deterministic tool selection.
- Added production-focused path hardening for file input validation via `resolve_existing_file` and release version bump to 1.0.1.
- Removed development tests from plugin package to keep marketplace artifact lightweight.

## 1.0.0

- Production-ready plugin release.
- Added module scaffolding, manifest validation, and XML checks.
- Added migration and OCA compliance checks.
- Added MCP tools for database access, test execution, and profiling.
- Prepared plugin for Cursor Marketplace with local installation support.
