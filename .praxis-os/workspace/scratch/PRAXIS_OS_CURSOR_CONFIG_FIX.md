# praxis OS - Cursor Installation Issues & Resolutions

This document tracks critical issues found during installation on the HoneyHive Python SDK project.

**Status**: ✅ **BOTH ISSUES RESOLVED** (as of commit `8d41788`)

---

# Issue 1: Cursor MCP Configuration ✅ RESOLVED

## Problem

The Cursor integration guide (`docs/content/how-to-guides/agent-integrations/cursor/index.md`) recommends this MCP configuration:

```json
{
  "mcpServers": {
    "praxis-os": {
      "command": ".praxis-os/venv/bin/python",
      "args": ["-m", "ouroboros", "--transport", "dual"],
      "cwd": ".praxis-os",
      "env": {
        "PYTHONPATH": "."
      }
    }
  }
}
```

**This configuration fails with:** `ModuleNotFoundError: No module named ouroboros`

## Root Causes

1. **Variable Expansion Issue**: The `${workspaceFolder}` variable is **not expanded** in Cursor's MCP configuration. Cursor tries to literally execute a command with that string, resulting in:
   ```
   Error: spawn ${workspaceFolder}/.praxis-os/venv/bin/python ENOENT
   ```

2. **Path Resolution with `cwd`**: When using `cwd` with a relative path and `PYTHONPATH: "."`, the Python module path doesn't resolve correctly relative to the `cwd` setting.

## Working Configuration

Use **absolute paths** for both `command` and `PYTHONPATH`:

```json
{
  "mcpServers": {
    "project-name": {
      "command": "/absolute/path/to/project/.praxis-os/venv/bin/python",
      "args": [
        "-m",
        "ouroboros",
        "--transport",
        "dual"
      ],
      "env": {
        "PYTHONPATH": "/absolute/path/to/project/.praxis-os"
      },
      "autoApprove": [
        "pos_search_project",
        "pos_workflow",
        "pos_browser",
        "pos_filesystem",
        "get_server_info",
        "current_date"
      ]
    }
  }
}
```

**Important:**
- Replace `"project-name"` with your actual project name (e.g., `"python-sdk"`, `"my-api"`, `"frontend"`)
- Replace `/absolute/path/to/project/` with your actual project path
- The server name should match your project to reinforce it as THE authoritative source

## Key Differences

1. **Removed `cwd` setting** - Not needed and causes path resolution issues
2. **Absolute paths everywhere** - `${workspaceFolder}` variables are NOT expanded by Cursor
3. **Absolute PYTHONPATH** - Use `/absolute/path/.praxis-os` instead of relative `.`  
4. **Absolute command path** - Use `/absolute/path/.praxis-os/venv/bin/python` (no variables)
5. **Project-specific server name** - Use just `"project-name"` (e.g., `"python-sdk"`) not generic `"praxis-os"`
6. **Correct tool names** - Updated `autoApprove` to use `pos_*` tools (not `search_standards`)

## Verification

Test that ouroboros can be imported:
```bash
cd /path/to/project
PYTHONPATH=/path/to/project/.praxis-os .praxis-os/venv/bin/python -c "import ouroboros; print('✅ Success')"
```

## Recommendation for Upstream

Update `docs/content/how-to-guides/agent-integrations/cursor/index.md` Step 2 with these critical fixes:

1. **Do NOT use `${workspaceFolder}` variables** - Cursor does not expand them in MCP config
2. **Use absolute paths** for both `command` and `PYTHONPATH`
3. **Remove the `cwd` setting** - It causes path resolution issues
4. **Name the server after the project** - Use the project name (e.g., `"python-sdk"`) NOT generic `"praxis-os"`
   - Server name should be just the project name to reinforce it's THE authoritative source
   - This prevents conflicts when working on multiple projects
   - Makes it clear which project's MCP server is running
   - Pattern: `"<project-name>"` (e.g., `"python-sdk"`, `"my-api"`, `"frontend"`)
5. **Add troubleshooting section** noting:
   - If seeing `spawn ${workspaceFolder}/... ENOENT` error, use absolute paths
   - If seeing `ModuleNotFoundError: No module named ouroboros`, check PYTHONPATH
   - Variables like `${workspaceFolder}` are not expanded in Cursor's MCP configuration
   - Check Cursor logs at `~/Library/Application Support/Cursor/logs/` for actual errors

## Environment Details

- **OS**: macOS 14.6.0
- **Cursor**: Latest version with native MCP support
- **Python**: 3.13.7
- **Project**: HoneyHive Python SDK
- **Installation Method**: Automated `install-praxis-os.py` script

## Related Files

- Installation guide: `/docs/content/how-to-guides/agent-integrations/cursor/index.md`
- Config schema: `/ouroboros/config/schemas/mcp.py`
- Installation script: `/scripts/install-praxis-os.py`

---

# Issue 2: Code Indexing Build Artifacts ✅ RESOLVED

**Resolution**: Implemented in commit `8d41788` - "feat(code-index): Implement three-tier file exclusion system with .gitignore support"

---

## Original Problem (Now Fixed)

## Problem

The code indexer **does not respect `.gitignore` patterns** or have default excludes for common build artifacts. This forces users to manually specify subdirectories instead of just pointing to `src/`.

**Current workaround (required):**
```yaml
code:
  source_paths:
    # Must explicitly list subdirectories to avoid .tox/
    - "../src/honeyhive/api/"
    - "../src/honeyhive/cli/"
    - "../src/honeyhive/config/"
    - "../src/honeyhive/evaluation/"
    - "../src/honeyhive/experiments/"
    - "../src/honeyhive/models/"
    - "../src/honeyhive/utils/"
```

**What users want (doesn't work):**
```yaml
code:
  source_paths:
    - "../src/"  # ❌ This indexes .tox/, __pycache__, etc.
```

## Root Cause

When pointing to `../src/`, the indexer processes:
- ✅ `src/honeyhive/api/*.py` (wanted)
- ✅ `src/honeyhive/config/*.py` (wanted)
- ❌ `src/honeyhive/tracer/.tox/py313/lib/python3.13/site-packages/...` (unwanted - thousands of third-party files)
- ❌ `src/**/__pycache__/*.pyc` (unwanted - compiled bytecode)

This causes:
1. **Indexing failures** - Server crashes processing large dependency files (e.g., 10,000+ line files from `.tox/`)
2. **Slow indexing** - Processes thousands of irrelevant files
3. **Poor search quality** - Third-party code pollutes semantic search results
4. **Resource leaks** - Semaphore/multiprocessing warnings from crashes

## What's Gitignored

The project's `.gitignore` already excludes these patterns:
```gitignore
__pycache__/
*.py[cod]
.tox/
.nox/
.coverage
.pytest_cache/
htmlcov/
.mypy_cache/
dist/
build/
*.egg-info/
venv/
.venv/
```

**The indexer should respect these automatically.**

## Attempted Solutions

### Attempt 1: `exclude_patterns` field (FAILED)
Tried adding `exclude_patterns` to `mcp.yaml`:
```yaml
code:
  source_paths:
    - "../src/"
  exclude_patterns:
    - ".tox/**"
    - "__pycache__/**"
    - "*.pyc"
```

**Result:** Schema validation error - `exclude_patterns` is not a supported field in the Pydantic model.

### Attempt 2: Explicit subdirectories (WORKS - but tedious)
List only desired subdirectories:
```yaml
code:
  source_paths:
    - "../src/honeyhive/api/"
    - "../src/honeyhive/cli/"
    # ... etc
```

**Result:** Works, but:
- ❌ Tedious to maintain
- ❌ Easy to miss new directories
- ❌ Doesn't scale across projects
- ❌ User must understand the entire project structure

## Proposed Solutions

### Option 1: Respect `.gitignore` (Recommended)
**Default behavior:** Automatically skip files/directories matching `.gitignore` patterns.

**Benefits:**
- Zero configuration
- Works across all projects automatically
- Aligns with git's file discovery behavior
- Users already maintain `.gitignore` properly

**Implementation:**
```python
# Use gitignore_parser or similar
from gitignore_parser import parse_gitignore

gitignore = parse_gitignore(".gitignore")
if gitignore(file_path):
    continue  # Skip this file
```

**Config opt-out (for edge cases):**
```yaml
code:
  source_paths:
    - "../src/"
  respect_gitignore: true  # Default
```

### Option 2: Built-in Default Excludes
**Fallback:** If no `.gitignore` exists, use sane defaults.

**Default exclusions:**
```python
DEFAULT_EXCLUDES = [
    # Python
    "__pycache__", "*.pyc", "*.pyo", "*.pyd",
    ".tox", ".nox", ".pytest_cache", ".mypy_cache",
    ".coverage", "htmlcov", "*.egg-info", "dist", "build",
    ".venv", "venv", "env",
    
    # JavaScript/Node
    "node_modules", ".next", ".nuxt", "dist", "build",
    
    # General
    ".git", ".svn", ".hg",
    ".DS_Store", "Thumbs.db",
]
```

**Config override:**
```yaml
code:
  source_paths:
    - "../src/"
  exclude_patterns:  # Manual override if needed
    - "custom_pattern/**"
```

### Option 3: Add `exclude_patterns` to Schema
**Quick fix:** Add the field to the Pydantic model.

```python
# ouroboros/config/schemas/indexes.py
class CodeIndexConfig(BaseModel):
    source_paths: List[str]
    languages: List[str]
    exclude_patterns: Optional[List[str]] = None  # ← ADD THIS
    vector: VectorConfig
    # ...
```

**Downside:** Users must manually configure - not zero-config.

## Recommendation for Upstream

**Priority: HIGH** - This blocks simple installation.

1. **Implement Option 1** (respect `.gitignore`) as the default behavior
2. **Implement Option 2** (default excludes) as fallback if no `.gitignore`
3. **Implement Option 3** (manual `exclude_patterns`) for edge cases

This allows users to simply:
```yaml
code:
  source_paths:
    - "../src/"  # ✅ Just works!
```

Instead of:
```yaml
code:
  source_paths:  # ❌ 50+ lines of subdirectory listings
    - "../src/myproject/module1/"
    - "../src/myproject/module2/"
    # ... tedious and error-prone
```

## Impact

**Without this fix:**
- ❌ Installation requires deep project knowledge
- ❌ Users must manually explore directory structure
- ❌ Easy to miss directories (incomplete indexing)
- ❌ Easy to include build artifacts (crashes/poor results)
- ❌ High friction for adoption

**With this fix:**
- ✅ Zero-config for most projects
- ✅ Works like `git status` (familiar behavior)
- ✅ Automatically handles new directories
- ✅ Prevents common indexing pitfalls
- ✅ Low friction for adoption

## Environment Details

- **Project**: HoneyHive Python SDK
- **Affected Files**: ~3,000+ third-party files in `.tox/` directories
- **Error**: Semaphore leaks, indexing crashes at ~81% completion
- **Current Workaround**: 7 explicit subdirectory paths in `mcp.yaml`

## Resolution Implementation

**Commit**: `8d41788` - "feat(code-index): Implement three-tier file exclusion system with .gitignore support"

**Files Changed**:
- ✅ `config/schemas/indexes.py` - Added `respect_gitignore` and `exclude_patterns` fields
- ✅ `subsystems/rag/code/constants.py` - NEW: 246 comprehensive exclusion patterns
- ✅ `subsystems/rag/code/semantic.py` - Implemented three-tier exclusion logic
- ✅ `requirements.txt` - Added `gitignore-parser>=0.1.11` dependency
- ✅ `dist/config/mcp.yaml` - Updated template with exclusion examples
- ✅ `docs/content/reference/config-reference.md` - Documented new fields
- ✅ `tests/subsystems/rag/test_code_index_exclusions.py` - NEW: 15 comprehensive tests

**Three-Tier Exclusion System**:
1. **Tier 1**: Respects `.gitignore` patterns (enabled by default via `respect_gitignore: true`)
2. **Tier 2**: Built-in defaults (246 patterns covering Python, JS, Rust, Go, Java, IDEs, OS files)
3. **Tier 3**: Optional custom `exclude_patterns` in config (additive)

**Results on HoneyHive Python SDK**:
- **Before**: 1,988 files indexed (including 1,906 third-party files in `.tox/`)
- **After**: 82 files indexed (only actual source code)
- **Reduction**: 96% fewer files, no crashes, clean search results

**Configuration Simplified**:
```yaml
# BEFORE (tedious workaround):
code:
  source_paths:
    - "../src/honeyhive/api/"
    - "../src/honeyhive/cli/"
    - "../src/honeyhive/config/"
    - "../src/honeyhive/evaluation/"
    - "../src/honeyhive/experiments/"
    - "../src/honeyhive/models/"
    - "../src/honeyhive/utils/"

# AFTER (zero-config, just works):
code:
  source_paths:
    - "../src/"  # ✅ Automatically excludes .tox/, __pycache__/, etc.
  respect_gitignore: true  # Default
```

---

## Verification Steps

To apply these fixes to an existing installation:

1. **Update praxis-os files**:
   ```bash
   cd /path/to/project/.praxis-os
   git pull  # Get latest praxis-os version with fixes
   ```

2. **Update dependencies**:
   ```bash
   .praxis-os/venv/bin/pip install gitignore-parser
   ```

3. **Simplify mcp.yaml**:
   ```yaml
   code:
     source_paths:
       - "../src/"  # Or your source directory
     respect_gitignore: true  # Default (optional)
   ```

4. **Delete old indexes** (will rebuild with exclusions):
   ```bash
   rm -rf .praxis-os/.cache/indexes/code
   rm -rf .praxis-os/.cache/indexes/standards
   ```

5. **Restart MCP server in Cursor**

6. **Verify exclusion working**:
   ```bash
   # Count source files (excluding build artifacts)
   find src -name "*.py" | grep -v ".tox" | grep -v "__pycache__" | wc -l
   
   # Should match the number of files indexed
   ```

---

## Related Files

- Config schema: `/ouroboros/config/schemas/indexes.py`
- Code indexer: `/ouroboros/subsystems/rag/code/semantic.py`
- Exclusion patterns: `/ouroboros/subsystems/rag/code/constants.py`
- Tests: `/tests/subsystems/rag/test_code_index_exclusions.py`
- Documentation: `/docs/content/reference/config-reference.md`

