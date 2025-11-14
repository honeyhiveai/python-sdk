# Graph Index WAL Checkpoint Issue

**Date**: November 8, 2025  
**Severity**: High - Graph traversal completely non-functional  
**Status**: Data exists but is inaccessible

---

## Summary

The graph index is successfully building and writing data (220KB), but the data remains in the DuckDB Write-Ahead Log (WAL) and is never checkpointed to the main database file. This makes graph traversal queries (`find_callers`, `find_dependencies`, `find_call_paths`) return empty results.

---

## Evidence

### File Sizes
```bash
$ ls -lh .praxis-os/.cache/indexes/code/graph.*
-rw-r--r--  12K Nov  7 15:57 graph.duckdb       # OLD - schema only
-rw-r--r-- 220K Nov  7 18:15 graph.duckdb.wal   # NEW - actual data!
```

### Query Results
```python
# All graph queries return:
{
  "status": "success",
  "results": [],
  "count": 0,
  "diagnostics": {
    "index_health": "unhealthy",
    "health_message": "Graph index empty or unhealthy"
  }
}
```

### Semantic Search Works
```python
# Vector search works perfectly:
pos_search_project(action="search_code", query="register_tracer")
# ✓ Returns results from code.lance vector index
```

---

## Root Cause

**ACTUAL ISSUE: Foreign Key Constraint Violation During Rebuild**

From MCP logs:
```
18:16:02 - Clearing existing graph data (force rebuild)
18:16:02 - [ERROR] Constraint Error: Violates foreign key constraint 
           because key "parent_id: 17" is still referenced by a foreign 
           key in a different table
18:16:02 - ❌ Failed to build code index: ERROR: rebuild_index(code)
```

**The Bug**:
1. Graph builds successfully (writes to WAL)
2. Health check runs **before WAL is checkpointed**
3. Health check queries main DB (empty) → reports "unhealthy"
4. Triggers automatic rebuild with `force=True`
5. Rebuild tries to `DELETE` existing data
6. **DuckDB foreign key constraint blocks DELETE** (child nodes still reference parents)
7. Rebuild fails, graph stays broken
8. Repeat cycle indefinitely!

**Secondary Issue - DuckDB WAL Mode**: When DuckDB operates in WAL mode, writes go to the `.wal` file first. Data must be **checkpointed** to be visible to new connections.

**Current Behavior**:
1. Graph indexer opens connection to `graph.duckdb`
2. Writes call graph data (writes go to WAL)
3. Connection stays open OR closes without checkpoint
4. Query handler opens NEW connection
5. New connection sees empty database (data still in WAL)

**Why Semantic Search Works**:
- LanceDB doesn't use WAL mode
- All data immediately visible in `code.lance`

---

## DuckDB WAL Behavior

From DuckDB docs:

> "WAL mode allows concurrent readers while a write transaction is in progress. However, readers will only see data that has been checkpointed. A checkpoint merges the WAL into the main database file."

**Checkpoint happens when**:
1. Explicitly called: `PRAGMA wal_checkpoint(FULL)`
2. Connection closes gracefully: `conn.close()`
3. WAL reaches size threshold (default: ~1GB)

**Checkpoint does NOT happen when**:
1. Connection crashes or is killed
2. Connection stays open indefinitely
3. No explicit checkpoint call

---

## Reproduction

```python
# In one process (indexer):
import duckdb
conn = duckdb.connect("graph.duckdb")
conn.execute("CREATE TABLE test (id INT)")
conn.execute("INSERT INTO test VALUES (1)")
# Don't close or checkpoint
# conn.close()  ← MISSING!

# In another process (query):
conn2 = duckdb.connect("graph.duckdb")
result = conn2.execute("SELECT * FROM test").fetchall()
print(result)  # [] - Empty! Data is in WAL
```

---

## Solutions

### Option 1: Fix Foreign Key Cascade on DELETE (CRITICAL FIX)

**The rebuild is failing because of foreign key constraints.** Fix the schema:

```python
# In graph schema creation:
CREATE TABLE relationships (
    id INTEGER PRIMARY KEY,
    parent_id INTEGER,
    child_id INTEGER,
    FOREIGN KEY (parent_id) REFERENCES symbols(id) ON DELETE CASCADE,  ← ADD THIS!
    FOREIGN KEY (child_id) REFERENCES symbols(id) ON DELETE CASCADE    ← ADD THIS!
)
```

**Or use correct delete order**:
```python
def clear_graph_data():
    # Delete in reverse dependency order
    conn.execute("DELETE FROM relationships")  # Children first
    conn.execute("DELETE FROM symbols")         # Parents second
    conn.execute("DELETE FROM ast_nodes")       # Root last
```

### Option 2: Explicit Checkpoint After Indexing (ALSO NEEDED)

Add checkpoint call after graph is built:

```python
# In graph index builder
def build_graph_index():
    conn = duckdb.connect(graph_db_path)
    
    try:
        # Build graph...
        for file in source_files:
            extract_and_insert_calls(conn, file)
        
        # CRITICAL: Checkpoint before closing
        conn.execute("PRAGMA wal_checkpoint(FULL)")
        
    finally:
        conn.close()  # Ensures WAL is flushed
```

### Option 2: Use Single Shared Connection

Keep one persistent connection for both writes and reads:

```python
# Singleton pattern
class GraphIndex:
    _conn = None
    
    @classmethod
    def get_connection(cls):
        if cls._conn is None:
            cls._conn = duckdb.connect(graph_db_path)
        return cls._conn
    
    @classmethod
    def shutdown(cls):
        if cls._conn:
            cls._conn.execute("PRAGMA wal_checkpoint(FULL)")
            cls._conn.close()
            cls._conn = None
```

### Option 3: Fix Health Check Timing

Health check should wait for checkpoint:
```python
def check_graph_health():
    # Force checkpoint before checking
    conn.execute("PRAGMA wal_checkpoint(FULL)")
    
    # Now check if data exists
    result = conn.execute("SELECT COUNT(*) FROM symbols").fetchone()
    return result[0] > 0
```

### Option 4: Disable WAL Mode

Force immediate writes to main file (slower but simpler):

```python
conn = duckdb.connect(graph_db_path)
conn.execute("PRAGMA disable_checkpoint_on_shutdown")
conn.execute("PRAGMA wal_autocheckpoint=1")  # Checkpoint after every transaction
```

---

## Testing

### Verify Checkpoint Works

```bash
# Before fix:
$ ls -lh graph.*
graph.duckdb      12K
graph.duckdb.wal 220K  ← Data stuck here

# After fix (with checkpoint):
$ ls -lh graph.*
graph.duckdb     232K  ← Data merged!
graph.duckdb.wal   0K  ← WAL empty or deleted
```

### Verify Graph Queries Work

```python
# Should return actual call relationships:
result = pos_search_project(
    action="find_callers",
    query="register_tracer",
    max_depth=3
)

# Expected: Non-empty results showing functions that call register_tracer
assert result["count"] > 0
assert result["diagnostics"]["index_health"] == "healthy"
```

---

## Current Workaround

**None available.** Graph traversal is completely non-functional until checkpointing is fixed.

**Semantic search works** as a partial workaround for finding code, but call graph analysis is unavailable.

---

## Related Issues

- `CONFIG_PATH_MISMATCH.md` - Config path didn't match actual path (minor issue)
- `GITIGNORE_PARSER_BUG.md` - Nested directory exclusion (unrelated)
- `PRAXIS_OS_CURSOR_CONFIG_FIX.md` - Cursor MCP config (unrelated)

---

## Recommendation for Upstream

1. **Immediate Fix**: Add `PRAGMA wal_checkpoint(FULL)` after graph index building
2. **Better Fix**: Use connection pooling with proper lifecycle management
3. **Best Fix**: Investigate why connection isn't being closed properly
4. **Testing**: Add integration test that verifies graph queries work after indexing
5. **Monitoring**: Add health check that verifies WAL file size vs main file size

---

## Impact

**Severity**: High  
**Affected Features**: All graph traversal (`find_callers`, `find_dependencies`, `find_call_paths`)  
**Workaround**: None  
**User Impact**: Major feature completely non-functional

This is likely affecting **all users** who try to use graph traversal features.

---

## References

- DuckDB WAL mode: https://duckdb.org/docs/sql/configuration#write-ahead-log
- DuckDB checkpoint: https://duckdb.org/docs/sql/pragmas#wal-checkpoint
- SQLite WAL (similar concept): https://www.sqlite.org/wal.html

