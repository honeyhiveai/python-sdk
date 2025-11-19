# Configuration Reconciliation Needed

The upgrade process has detected changes to the MCP configuration template.

## Files

- **Current config:** `.praxis-os/config/mcp.yaml`
- **New template:** `.praxis-os/config/mcp.yaml.new`

## Action Required

Please review the differences between your current configuration and the new template.
Merge any new settings or changes that are relevant to your setup.

## Steps

1. Compare the two files:
   ```bash
   diff .praxis-os/config/mcp.yaml .praxis-os/config/mcp.yaml.new
   ```

2. Merge changes manually or use a merge tool

3. Delete the `.new` file when done:
   ```bash
   rm .praxis-os/config/mcp.yaml.new
   ```

4. Delete this prompt file:
   ```bash
   rm .praxis-os/config/CONFIG_RECONCILIATION_NEEDED.md
   ```

## Notes

- Your current configuration has been preserved
- The new template is provided as `.mcp.yaml.new` for reference
- No changes have been made to your active configuration
