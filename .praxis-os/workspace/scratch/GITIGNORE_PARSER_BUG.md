# Gitignore Parser Bug - Nested Directory Exclusion

**Date**: November 8, 2025  
**Reporter**: Discovered during praxis OS installation on HoneyHive Python SDK  
**Severity**: Medium (causes index bloat, but has workaround)

---

## Summary

The `gitignore-parser` Python library used by praxis OS does not properly exclude nested directories that match `.gitignore` patterns.

**Expected behavior**: `.tox/` in `.gitignore` should exclude `.tox` directories at ANY level  
**Actual behavior**: Only excludes `.tox/` at repository root, misses nested occurrences

---

## Reproduction

### Setup
```bash
# Create test repo
mkdir test-repo && cd test-repo
git init

# Create .gitignore
echo ".tox/" > .gitignore

# Create nested .tox directory
mkdir -p src/module/.tox
touch src/module/.tox/test.py

# Create root .tox directory
mkdir .tox
touch .tox/test.py
```

### Test with gitignore-parser
```python
from gitignore_parser import parse_gitignore

matches = parse_gitignore('.gitignore')

print(matches('./.tox/test.py'))              # True (excluded) ✅
print(matches('src/module/.tox/test.py'))     # False (NOT excluded) ❌
```

### Expected behavior (standard gitignore)
```bash
git check-ignore ./.tox/test.py              # Excluded ✅
git check-ignore src/module/.tox/test.py     # Excluded ✅
```

---

## Impact

### On praxis OS Code Indexing

**Observed in HoneyHive Python SDK**:
- Actual source code: 82 Python files, 32,202 lines
- Indexed (with bug): 1,988 Python files, 621,636 lines
- Extra files: 1,906 files from `src/honeyhive/tracer/.tox/` (old tox artifacts)
- Extra data: 75MB of test dependencies (pylint, mypy, pip internals)

**Performance Impact**:
- Slower index building (10x more files)
- Slower queries (searching through 1,906 extra files)
- Inaccurate code statistics (reported 621k lines vs actual 32k)
- Wasted disk space (75MB of cached vectors for test artifacts)

---

## Root Cause Analysis

### The `gitignore-parser` Library

**Current implementation** (simplified):
```python
# gitignore-parser converts patterns to regex
# but may not properly handle directory patterns with /**/ matching

def parse_gitignore(full_path):
    with open(full_path) as f:
        patterns = f.readlines()
    
    # Converts .tox/ → regex
    # But regex may only match at specific depth
    # Missing: /**/.tox/ pattern expansion
```

### Standard Gitignore Behavior

From Git documentation:
> If there is a separator at the end of the pattern then the pattern will only match directories, otherwise the pattern can match both files and directories.

**Pattern**: `.tox/`  
**Should match**: `.tox/` at ANY directory level (equivalent to `**/.tox/` in glob syntax)

---

## Workaround (Implemented)

### Immediate Fix

Add explicit exclusion patterns in `mcp.yaml`:

```yaml
code:
  source_paths:
    - "../src/"
  languages:
    - "python"
  
  # File Exclusion (3-Tier System)
  respect_gitignore: true  # Tier 1: Doesn't catch nested directories (bug)
  
  exclude_patterns:  # Tier 3: Workaround for nested directories
    - "**/.tox/**"          # Tox test environments
    - "**/__pycache__/**"   # Python bytecode (in case gitignore misses)
    - "**/venv/**"          # Virtual environments
    - "**/node_modules/**"  # Node dependencies
    - "**/.pytest_cache/**" # Pytest cache
```

### Long-term Solution Options

#### Option 1: Replace `gitignore-parser` with `pathspec` ✅ RECOMMENDED

```python
import pathspec

with open('.gitignore') as f:
    spec = pathspec.PathSpec.from_lines('gitwildmatch', f)

# Better gitignore compliance
if spec.match_file('src/module/.tox/test.py'):
    exclude_file()  # Properly excludes nested directories
```

**Pros**:
- Better gitignore spec compliance
- Actively maintained
- Handles nested directories correctly
- Used by other major projects (pre-commit, etc.)

**Cons**:
- Different API (migration needed)
- Slightly different dependency

#### Option 2: Enhance `gitignore-parser` Usage

```python
import os
from gitignore_parser import parse_gitignore

# Normalize paths to absolute before checking
matches = parse_gitignore('.gitignore', base_dir=os.getcwd())

# OR: Explicitly add /**/ prefix to directory patterns
def enhance_gitignore_patterns(gitignore_path):
    with open(gitignore_path) as f:
        patterns = f.readlines()
    
    enhanced = []
    for pattern in patterns:
        enhanced.append(pattern)
        if pattern.strip().endswith('/'):
            # Add nested variant
            enhanced.append(f"**/{pattern}")
    
    return enhanced
```

#### Option 3: Document Limitation + Provide Template

Update `mcp.yaml` template with comment:

```yaml
code:
  respect_gitignore: true  
  # ⚠️ Known issue: gitignore-parser doesn't catch nested directories
  #    Add explicit patterns below for common build artifacts:
  exclude_patterns:
    - "**/.tox/**"
    - "**/__pycache__/**"
    - "**/venv/**"
    - "**/node_modules/**"
```

---

## Testing

### Unit Test for Fix

```python
def test_nested_gitignore_exclusion():
    """Test that nested .tox directories are excluded."""
    # Setup
    create_test_repo_with_nested_tox()
    
    # Index with respect_gitignore: true
    index = build_code_index(
        source_paths=["src/"],
        respect_gitignore=True
    )
    
    # Verify
    indexed_files = index.list_files()
    
    # Should NOT include nested .tox
    assert not any('.tox' in f for f in indexed_files), \
        "Nested .tox directories should be excluded by gitignore"
    
    # Should include actual source
    assert any('src/module/main.py' in f for f in indexed_files), \
        "Actual source files should be included"
```

### Integration Test

```bash
# Create repo with nested artifacts
mkdir -p test-repo/src/module/.tox
echo "print('artifact')" > test-repo/src/module/.tox/test.py
echo "print('source')" > test-repo/src/module/main.py
echo ".tox/" > test-repo/.gitignore

# Start praxis OS with respect_gitignore: true
cd test-repo
praxis-os start

# Query indexed files
curl http://localhost:8080/debug/indexed-files | jq '.files'

# Expected: Only main.py, NOT test.py from .tox
```

---

## Recommendation for praxis OS Team

1. **Short-term** (v1.1 - next patch):
   - ✅ Add explicit `exclude_patterns` to `mcp.yaml` template with common artifacts
   - ✅ Document the limitation in README/installation guide
   - ✅ Provide helper script to detect stray build artifacts

2. **Medium-term** (v1.2):
   - Replace `gitignore-parser` with `pathspec` library
   - Add unit tests for nested directory exclusion
   - Add debug logging showing what's being indexed/excluded

3. **Long-term** (v2.0):
   - Consider built-in artifact detection (auto-detect .tox, node_modules, etc.)
   - Provide CLI command to analyze what's being indexed: `praxis-os debug index-contents`

---

## Files Modified

- `mcp.yaml`: Added explicit `exclude_patterns` workaround
- `PRAXIS_OS_CURSOR_CONFIG_FIX.md`: Documented issue #3
- `GITIGNORE_PARSER_BUG.md`: This detailed bug report

---

## Additional Issue: Graph Index WAL Not Checkpointing

**Observed**: Graph database has active WAL file (220KB) but main file is small (12KB), causing graph queries to return "unhealthy" even though data exists.

```
.praxis-os/.cache/indexes/code/graph.duckdb      (12KB - schema only)
.praxis-os/.cache/indexes/code/graph.duckdb.wal  (220KB - actual data!)
```

**Likely Causes**:
1. DuckDB WAL not being checkpointed automatically
2. Server not closing connections properly on query
3. Long-running indexing process preventing checkpoint

**Recommendation**: Add explicit WAL checkpoint after graph building:
```python
# After building graph index
conn.execute("PRAGMA wal_checkpoint(FULL)")
conn.close()
```

---

## References

- Git documentation on gitignore patterns: https://git-scm.com/docs/gitignore
- `gitignore-parser` library: https://github.com/mherrmann/gitignore_parser
- `pathspec` library (alternative): https://github.com/cpburnz/python-pathspec
- DuckDB WAL mode: https://duckdb.org/docs/sql/configuration#write-ahead-log
- Related issue: (to be filed on praxis-os repo)

