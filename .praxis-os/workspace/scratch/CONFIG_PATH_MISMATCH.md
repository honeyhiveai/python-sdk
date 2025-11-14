# Config Path Mismatch - DuckDB Graph Database

**Date**: November 8, 2025  
**Issue**: Graph index showing as "unhealthy" due to config path mismatch

---

## Problem

The `mcp.yaml` config specifies:
```yaml
duckdb_path: ".cache/code.duckdb"
```

But the server actually creates the database at:
```
.cache/indexes/code/graph.duckdb
```

## Impact

- Graph traversal queries (`find_callers`, `find_dependencies`, `find_call_paths`) return empty results
- Health check reports "graph: Graph index empty or unhealthy"
- Data exists (220KB in WAL file) but queries can't access it

## Root Cause

Either:
1. **Config is ignored**: Server has hardcoded path that overrides config
2. **Path resolution issue**: Config path is relative to wrong base directory
3. **Template error**: Default config has wrong path

## Verification

```bash
# Config says:
grep duckdb_path .praxis-os/config/mcp.yaml
# Output: duckdb_path: ".cache/code.duckdb"

# Actual location:
find .praxis-os -name "*.duckdb"
# Output: .praxis-os/.cache/indexes/code/graph.duckdb

# File has data (in WAL):
ls -lh .praxis-os/.cache/indexes/code/
# graph.duckdb (12KB) + graph.duckdb.wal (220KB)
```

## Solution

**Option 1**: Comment out `duckdb_path` and let server use default
```yaml
# duckdb_path: ".cache/code.duckdb"  # Let server use default path
```

**Option 2**: Fix config to match actual path
```yaml
duckdb_path: ".cache/indexes/code/graph.duckdb"
```

**Option 3**: Update server code to respect config path (if it's being ignored)

## Recommendation for Upstream

1. **Verify path resolution logic** in server code
2. **Remove `duckdb_path` from template** if it's not being used
3. **Add validation** that warns if config path doesn't match actual path
4. **Document** actual path conventions in comments

---

## Related Issues

- WAL checkpoint issue (220KB data in .wal file, not accessible)
- Gitignore parser nested directory exclusion
- See: `GITIGNORE_PARSER_BUG.md`, `PRAXIS_OS_CURSOR_CONFIG_FIX.md`

