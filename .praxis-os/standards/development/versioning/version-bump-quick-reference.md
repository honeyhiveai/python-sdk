# Python SDK Version Bump Quick Reference

**Quick reference for AI assistants to bump SDK version when requested.**

---

## 🚨 TL;DR - Version Bump Quick Reference

**Keywords for search**: Python SDK version bump, HoneyHive SDK increment version, update version number, change version, release version, __version__, src/honeyhive/__init__.py, semantic versioning increment, MAJOR MINOR PATCH bump, how to bump version Python SDK, version string update, prepare release version, pyproject.toml DO NOT CHANGE, CHANGELOG.md update required, honeyhive version file location, semver Python SDK, version bump process HoneyHive

**Core Principle:** Version is defined in ONE file (`src/honeyhive/__init__.py` line 6) and ONLY that file should be changed for version bumps. The release workflow reads version from this file.

**User says: "Bump version to X.Y.Z" or "Increment version"**

**You do:**

1. Edit `src/honeyhive/__init__.py` line 6: `__version__ = "X.Y.Z"`
2. Update `CHANGELOG.md` with release notes
3. Done - workflow handles rest

**DO NOT edit `pyproject.toml` version** - it's not used for releases.

**Verification:**
```bash
python -c "exec(open('src/honeyhive/__init__.py').read()); print(__version__)"
grep "## \[X.Y.Z\]" CHANGELOG.md
```

---

## ❓ Questions This Answers

1. "How do I bump the Python SDK version?"
2. "Where is the Python SDK version defined?"
3. "User asked me to update version to 1.0.0, what files do I change?"
4. "How do I increment MAJOR, MINOR, or PATCH version for Python SDK?"
5. "What's the process for version bump in HoneyHive SDK?"
6. "Where is __version__ located in Python SDK?"
7. "Do I update pyproject.toml version for Python SDK?"
8. "What else needs updating when version changes in Python SDK?"
9. "How does semantic versioning work for this SDK?"
10. "Which version file triggers the release workflow?"
11. "What files should I NOT change when bumping version?"
12. "How do I bump from RC to stable version?"
13. "How do I increment release candidate number?"
14. "What's the CHANGELOG.md format for version bumps?"
15. "How do I verify version was bumped correctly?"
16. "What happens after I bump version and merge to main?"
17. "How do I know if version bump requires MAJOR vs MINOR vs PATCH?"
18. "What are pre-release version formats for Python SDK?"
19. "Where can I find examples of complete version bumps?"
20. "What's the decision tree for version bump requests?"
21. "How does the release workflow detect version changes?"
22. "What's the relationship between __version__ and pyproject.toml?"

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **User requests version bump** | `pos_search_project(action="search_standards", query="how to bump Python SDK version")` |
| **Need version file location** | `pos_search_project(action="search_standards", query="where is Python SDK version defined")` |
| **Increment patch/minor/major** | `pos_search_project(action="search_standards", query="Python SDK increment version semantic versioning")` |
| **Pre-release versions** | `pos_search_project(action="search_standards", query="Python SDK release candidate RC version")` |
| **CHANGELOG update needed** | `pos_search_project(action="search_standards", query="Python SDK CHANGELOG version bump format")` |
| **Verification needed** | `pos_search_project(action="search_standards", query="verify Python SDK version bump")` |
| **pyproject.toml confusion** | `pos_search_project(action="search_standards", query="Python SDK pyproject.toml version DO NOT CHANGE")` |
| **Release workflow integration** | `pos_search_project(action="search_standards", query="Python SDK version bump release workflow")` |

---

## 🎯 Purpose

Define the exact file location and process for version bumps in the HoneyHive Python SDK to enable AI assistants to quickly and correctly update versions when requested.

**Key Principle**: Version is defined in ONE file (`src/honeyhive/__init__.py`) and ONLY that file should be changed for version bumps. The release workflow reads version from this file.

---

## Version File Location - Single Source of Truth

**Single Source of Truth:**

```python
# File: src/honeyhive/__init__.py
# Line: ~6

__version__ = "0.1.0rc3"  # <-- ONLY place to change version
```

**All other code imports from here:**

```python
from honeyhive import __version__
```

**DO NOT touch these files for version bumps:**
- ❌ `pyproject.toml` - Version here is NOT used for releases
- ❌ `docs/conf.py` - Not used
- ❌ Any other file - Only `__init__.py` matters

**Why this matters:** The release workflow (`.github/workflows/sdk-publish.yml`) reads version from `src/honeyhive/__init__.py`, NOT from `pyproject.toml`. Changing the wrong file wastes time and breaks releases.

---

## Version Bump Process - Two Files Only

### Step 1: Update Version String

**File:** `src/honeyhive/__init__.py`  
**Line:** 6  
**Change:** `__version__` string

**Examples:**

```python
# Patch bump: 1.0.0 → 1.0.1
__version__ = "1.0.1"

# Minor bump: 1.0.0 → 1.1.0
__version__ = "1.1.0"

# Major bump: 1.0.0 → 2.0.0
__version__ = "2.0.0"

# Pre-release: 1.0.0rc1 → 1.0.0rc2
__version__ = "1.0.0rc2"

# RC to stable: 1.0.0rc3 → 1.0.0
__version__ = "1.0.0"
```

### Step 2: Update CHANGELOG.md

**File:** `CHANGELOG.md`  
**Location:** Add new version section at top

**Format:**

```markdown
## [1.2.3] - 2025-10-31

### Added
- New feature X
- New feature Y

### Changed
- Updated behavior Z

### Fixed
- Bug fix A
- Bug fix B

### Breaking Changes
- Describe any breaking changes
- Link to migration guide if needed

[1.2.3]: https://github.com/honeyhiveai/python-sdk/compare/v1.2.2...v1.2.3
```

### Step 3: Done

**That's all!** The release workflow handles:
- Building package
- Publishing to PyPI
- Creating GitHub release
- Tagging repository

---

## Semantic Versioning Rules - When to Bump What

**Format:** `MAJOR.MINOR.PATCH`

### When to Bump MAJOR (X.0.0) - Breaking Changes

**Breaking changes - user code needs updates:**

- API method removed
- API method signature changed (incompatible)
- Required parameters added
- Return type changed
- Behavior change that breaks existing code

**Example:** `1.5.2` → `2.0.0`

```python
# Before (1.5.2):
tracer = HoneyHiveTracer.init(api_key, project)

# After (2.0.0) - Breaking change:
tracer = HoneyHiveTracer(api_key=api_key, project=project)
```

### When to Bump MINOR (x.Y.0) - New Features

**New features - backward compatible:**

- New API methods added
- New optional parameters added
- New functionality added
- Deprecation warnings (feature still works)

**Example:** `1.5.2` → `1.6.0`

```python
# Added new method (backward compatible):
tracer.enrich_session_metadata(...)  # New in 1.6.0

# Old code still works unchanged
tracer.enrich_session(...)  # Still works
```

### When to Bump PATCH (x.y.Z) - Bug Fixes

**Bug fixes - backward compatible:**

- Bug fixes
- Performance improvements
- Documentation updates
- Internal refactoring (no API changes)

**Example:** `1.5.2` → `1.5.3`

```python
# Fixed: Context propagation bug in evaluate()
# No API changes, just works correctly now
```

---

## Pre-Release Versions

**Format:** `X.Y.Zrc#`, `X.Y.Zalpha#`, `X.Y.Zbeta#`

### Release Candidates

```python
__version__ = "1.0.0rc1"  # First release candidate
__version__ = "1.0.0rc2"  # Second release candidate
__version__ = "1.0.0"     # Stable release
```

### Alpha/Beta Releases

```python
__version__ = "1.0.0alpha1"  # Early testing
__version__ = "1.0.0beta1"   # Feature complete, testing
__version__ = "1.0.0rc1"     # Release candidate
__version__ = "1.0.0"        # Stable
```

---

## Common User Requests - Decision Tree

### "Bump version to 1.0.0"

```python
# src/honeyhive/__init__.py
__version__ = "1.0.0"
```

Update `CHANGELOG.md`, done.

### "Increment patch version"

```python
# Current: 1.0.0
__version__ = "1.0.1"  # Increment PATCH

# Current: 1.2.5
__version__ = "1.2.6"  # Increment PATCH
```

### "Increment minor version"

```python
# Current: 1.0.0
__version__ = "1.1.0"  # Increment MINOR, reset PATCH

# Current: 1.5.3
__version__ = "1.6.0"  # Increment MINOR, reset PATCH
```

### "Increment major version"

```python
# Current: 1.0.0
__version__ = "2.0.0"  # Increment MAJOR, reset MINOR and PATCH

# Current: 1.5.3
__version__ = "2.0.0"  # Increment MAJOR, reset MINOR and PATCH
```

### "Prepare next RC"

```python
# Current: 1.0.0rc2
__version__ = "1.0.0rc3"  # Increment RC number

# Current: 1.0.0rc3
__version__ = "1.0.0"     # Remove RC for stable release
```

---

## What NOT to Do - Common Mistakes

### ❌ Don't Update pyproject.toml

```toml
# pyproject.toml
[project]
version = "0.1.0rc3"  # ❌ DON'T CHANGE THIS
```

**Why:** Release workflow reads from `__init__.py`, not `pyproject.toml`.

### ❌ Don't Update Multiple Files

**Only update:**
- ✅ `src/honeyhive/__init__.py`
- ✅ `CHANGELOG.md`

**Don't update:**
- ❌ `pyproject.toml`
- ❌ `docs/conf.py`
- ❌ Any other files

### ❌ Don't Forget CHANGELOG

Version bump without CHANGELOG update = incomplete release.

Always update `CHANGELOG.md` with release notes.

---

## Verification - How to Check Version Bump

**After version bump, verify:**

```bash
# 1. Check version string
python -c "exec(open('src/honeyhive/__init__.py').read()); print(__version__)"
# Should show: 1.0.0 (or whatever you set)

# 2. Check CHANGELOG has entry
grep "## \[1.0.0\]" CHANGELOG.md
# Should show: ## [1.0.0] - 2025-10-31

# 3. That's it - ready to commit
```

---

## Integration with Release Workflow

**After version bump and merge to main:**

1. Workflow triggers on `src/honeyhive/__init__.py` change
2. Extracts version: `1.0.0`
3. Checks PyPI: Does `honeyhive==1.0.0` exist?
4. If NO: Builds, tests, publishes to PyPI
5. If YES: Exits with "already published" (safe)
6. Creates GitHub release: `v1.0.0`

**Workflow file:** `.github/workflows/sdk-publish.yml`

---

## Complete Example - Version Bump from Start to Finish

**User request:** "Bump version to 1.0.0"

**Step 1 - Update version:**

```python
# src/honeyhive/__init__.py (line 6)
__version__ = "1.0.0"  # Changed from "0.1.0rc3"
```

**Step 2 - Update CHANGELOG:**

```markdown
# CHANGELOG.md (add at top)

## [1.0.0] - 2025-10-31

### Added
- Multi-instance tracer architecture for proper isolation
- Direct OpenTelemetry integration (removed Traceloop dependency)
- Automatic input capture in @trace decorator

### Changed
- evaluate() now supports tracer parameter for enhanced features
- Improved thread safety and context propagation

### Breaking Changes
- Evaluation functions need `tracer` parameter for enrichment
- See MIGRATION_GUIDE.md for details

[1.0.0]: https://github.com/honeyhiveai/python-sdk/compare/v0.1.0rc3...v1.0.0
```

**Step 3 - Commit:**

```bash
git add src/honeyhive/__init__.py CHANGELOG.md
git commit -m "release: v1.0.0"
```

**Done!** Workflow handles rest on merge to main.

---

## Quick Reference Commands

```bash
# Check current version
python -c "exec(open('src/honeyhive/__init__.py').read()); print(__version__)"

# Verify CHANGELOG has new version
grep -A 5 "## \[" CHANGELOG.md | head -10

# Files to update for version bump
# 1. src/honeyhive/__init__.py (line 6)
# 2. CHANGELOG.md (add new section at top)

# Files to NOT update
# ❌ pyproject.toml
# ❌ docs/conf.py
# ❌ Any other files
```

---

## 🔗 Related Standards

**Query workflow for version management:**

1. **Start with this standard** → `pos_search_project(action="search_standards", query="Python SDK version bump")`
2. **Learn release process** → `pos_search_project(action="search_standards", query="Python SDK release process")` → `standards/development/workflow/release-process.md`
3. **Understand git workflow** → `pos_search_project(action="search_standards", query="Python SDK git workflow")` → `standards/development/workflow/git-workflow.md`
4. **Learn dependency pinning** → `pos_search_project(action="search_standards", query="Python SDK dependency pinning")` → `standards/development/versioning/dependency-pinning.md`

**By Category:**

**Versioning:**
- `standards/development/versioning/dependency-pinning.md` → `pos_search_project(action="search_standards", query="Python SDK dependency pinning")`

**Workflow:**
- `standards/development/workflow/release-process.md` → `pos_search_project(action="search_standards", query="Python SDK release process")`
- `standards/development/workflow/git-workflow.md` → `pos_search_project(action="search_standards", query="Python SDK git workflow")`

**Universal Standards:**
- `standards/universal/workflows/workflow-system-overview.md` → `pos_search_project(action="search_standards", query="workflow system best practices")`

---

## Validation Checklist

Before marking version bump as complete:

- [ ] `src/honeyhive/__init__.py` line 6 updated to new version
- [ ] `CHANGELOG.md` has new version section at top
- [ ] CHANGELOG includes date in format `YYYY-MM-DD`
- [ ] CHANGELOG includes compare link at bottom
- [ ] Version string matches semantic versioning format
- [ ] Did NOT change `pyproject.toml` version
- [ ] Verification command shows correct version
- [ ] CHANGELOG grep finds new version entry
- [ ] Ready to commit with message `release: vX.Y.Z`

---

**📝 Remember**: Only `src/honeyhive/__init__.py` line 6 + `CHANGELOG.md` need updating. That's it!

