# Production release checklist

## Pre-publication checks

1. Update `CHANGELOG.md` and bump version in `.cursor-plugin/plugin.json`.
2. Ensure MCP map/commands are documented and consistent:
   - `README.md` command list includes all tool mappings.
   - `commands/*.md` frontmatter exists and matches MCP tool behavior.
3. Keep production package metadata consistent:
   - `.cursor-plugin/plugin.json` is valid JSON and follows Cursor plugin schema.
   - Use Cursor Marketplace validation during submission.
4. Security defaults are explicit in docs:
   - `CURSOR_ODOO_ALLOW_SHELL=1` only for trusted environments.
   - Absolute path usage for file tools is opt-in via `CURSOR_ODOO_ALLOW_ABSOLUTE_PATHS=1`.
5. Verify no development-only artifacts are shipped in plugin package.
   - Marketplace-relevant files are plugin manifest/rules/agents/skills/commands/mcp/assets/docs.

## Publishing

1. Push the plugin to a public Git repository.
2. Open `https://cursor.com/marketplace/publish`.
3. Submit the repository link.
4. After approval, install through Cursor IDE -> Settings -> Plugins.
