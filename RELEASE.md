# Production release checklist

## Pre-publication checks

1. Update `CHANGELOG.md` and bump version in `.cursor-plugin/plugin.json`.
2. Ensure MCP map/commands are documented and consistent:
   - `README.md` command list includes all tool mappings.
   - `commands/*.md` frontmatter exists and matches MCP tool behavior.
3. Keep production package metadata consistent:
   - `scripts/validate-plugin.py --quick` (or Marketplace validation flow) succeeds.
4. Security defaults are explicit in docs:
   - `CURSOR_ODOO_ALLOW_SHELL=1` only for trusted environments.
   - Absolute path usage for file tools is opt-in via `CURSOR_ODOO_ALLOW_ABSOLUTE_PATHS=1`.
5. Verify no development-only test artifacts are shipped in plugin package.
   - Marketplace-relevant files are plugin manifest/rules/agents/skills/commands/hooks/mcp/docs.

## Publishing command

1. Run plugin validation from repository root:

```bash
python3 scripts/validate-plugin.py --quick
```

2. Review diff and publish artifact according to your internal release process.
