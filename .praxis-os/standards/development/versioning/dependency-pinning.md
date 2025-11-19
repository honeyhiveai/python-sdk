# Python SDK Dependency Version Pinning Standards

**Deterministic builds through intelligent dependency versioning**

**Date**: October 4, 2025  
**Status**: Active  
**Scope**: All external dependencies (pip, npm, etc.)

---

## 🚨 TL;DR - Dependency Pinning Quick Reference

**Keywords for search**: Python SDK dependency pinning, HoneyHive SDK version pinning, requirements.txt versioning, pip version specifiers, semver semantic versioning, tilde equals compatible release, exact pin version lock, dependency version ranges, non-deterministic builds forbidden, version justification required, changelog research dependencies, GitHub issues breaking changes, test version upgrades, security vulnerability patching, dependency update strategy

**Core Principle:** "Non-deterministic builds are production incidents waiting to happen." Pin versions to specific, justified ranges.

**Preferred Syntax:**
- `package~=X.Y.0` - **PREFERRED** (patch-level compatibility, e.g., ~=2.5.0 allows 2.5.x)
- `package==X.Y.Z` - Exact pin (rare, for critical stability)
- `package>=X.Y.Z,<X2.0` - Explicit upper bound (when breaking changes expected)
- ❌ `package>=X.Y.Z` - **FORBIDDEN** (unbounded, non-deterministic)

**Research Protocol (Before ANY version spec):**
1. Check package maturity (stable vs experimental)
2. Read changelog for relevant versions
3. Check GitHub issues for breaking changes
4. Test version in isolated environment
5. Write inline justification

**Example (Good):**
```python
# requirements.txt
lancedb~=0.25.0  # Latest stable, 0.24.x had race condition bugs (GitHub #1234)
pytest~=7.4.0  # Mature, stable, follows SemVer strictly
openai>=1.0.0,<2.0.0  # 1.x stable, 2.x is alpha (breaking changes expected)
```

---

## ❓ Questions This Answers

1. "How do I pin dependencies for Python SDK?"
2. "What version specifier should I use?"
3. "When do I use tilde equals (~=)?"
4. "When do I use exact pin (==)?"
5. "When do I use version ranges?"
6. "Why are unbounded ranges forbidden?"
7. "How do I justify a version choice?"
8. "How do I research package maturity?"
9. "How do I update dependencies safely?"
10. "What is the commit message template?"
11. "How do I handle security vulnerabilities?"
12. "How do I handle pre-1.0 libraries?"
13. "What about transitive dependencies?"
14. "What about development vs production deps?"
15. "How do I test version updates?"
16. "What changelog information matters?"
17. "What GitHub issues should I check?"
18. "What are forbidden version patterns?"
19. "When should I update dependencies?"
20. "How do I document dependency changes?"

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Adding dependency** | `pos_search_project(action="search_standards", query="Python SDK dependency pinning version")` |
| **Choosing specifier** | `pos_search_project(action="search_standards", query="Python SDK tilde equals exact pin when to use")` |
| **Justifying version** | `pos_search_project(action="search_standards", query="Python SDK version justification requirements")` |
| **Updating dependency** | `pos_search_project(action="search_standards", query="Python SDK dependency update strategy safe")` |
| **Security patch** | `pos_search_project(action="search_standards", query="Python SDK security vulnerability patching")` |
| **Pre-1.0 library** | `pos_search_project(action="search_standards", query="Python SDK unstable pre-1.0 dependency")` |
| **Forbidden patterns** | `pos_search_project(action="search_standards", query="Python SDK forbidden dependency patterns")` |

---

## 🎯 Core Principle

**"Non-deterministic builds are production incidents waiting to happen."**

**The Problem:**
```python
# requirements.txt
lancedb>=0.3.0  # Allows ANY version from 0.3.0 to 0.999.999

# Developer machine: pip installs lancedb==0.25.1 (latest)
# CI/CD 3 months ago: cached lancedb==0.15.0
# Production: installs lancedb==0.30.0 (future version with breaking change)

# Result: Works on dev, fails in production. "But it worked on my machine!"
```

**The Solution**: Pin versions to specific, justified ranges.

---

## Version Specification Syntax

### Semantic Versioning (SemVer) Recap

```
MAJOR.MINOR.PATCH
  |     |     |
  |     |     └── Bug fixes (backward compatible)
  |     └── New features (backward compatible)
  └── Breaking changes (NOT backward compatible)

Example: 2.5.3
- Major: 2 (API version)
- Minor: 5 (feature set)
- Patch: 3 (bug fix iteration)
```

### Python pip Version Specifiers

| Specifier | Meaning | Use Case | Example |
|-----------|---------|----------|---------|
| `==X.Y.Z` | Exact version | Critical stability (rare) | `lancedb==0.25.1` |
| `~=X.Y.Z` | Compatible release (≥X.Y.Z, <X.(Y+1).0) | **PREFERRED** for stable deps | `lancedb~=0.25.0` → allows 0.25.x |
| `>=X.Y.Z,<X2.0` | Range with upper bound | When breaking changes expected | `package>=1.5.0,<2.0.0` |
| `>=X.Y.Z` | Minimum version (unbounded) | **FORBIDDEN** (non-deterministic) | ❌ Don't use |
| `*` or no version | Latest | **FORBIDDEN** (extremely dangerous) | ❌ Never use |

---

## Decision Tree: Which Specifier to Use?

### Step 1: Is this a stable, mature library?

**YES** (e.g., requests, pytest, pydantic)
→ Use `~=X.Y.0` for minor version compatibility

```python
# Allows 2.28.x (patch updates only)
requests~=2.28.0

# Why: Stable libraries follow SemVer strictly
# Patch updates = bug fixes, no breaking changes
```

**NO** (e.g., new library, pre-1.0, known instability)
→ Use `==X.Y.Z` for exact pinning

```python
# Exact version lock
experimental-lib==0.5.2

# Why: Unstable libraries may break SemVer
# Lock to tested version until maturity
```

### Step 2: Has the library broken backward compat recently?

**YES** (check GitHub issues for "breaking change" complaints)
→ Use explicit upper bound

```python
# Allows 1.x but blocks 2.x
library>=1.5.0,<2.0.0

# Why: Library doesn't respect SemVer
# Need to explicitly block known breaking changes
```

**NO** (library is well-maintained, follows SemVer)
→ Use `~=X.Y.0`

```python
# Compatible release (patch updates only)
well-maintained-lib~=3.2.0
```

### Step 3: Is this a transitive dependency?

**YES** (dependency of a dependency)
→ Usually don't specify (let parent control)

```python
# Bad: Over-constraining transitive deps
# If package-a requires requests>=2.20
# and you specify requests==2.25
# You've now created potential conflicts

# Good: Let package-a specify its requests version
# Only pin if you have a specific compatibility issue
```

**Exception**: Pin if security vulnerability or known incompatibility

```python
# Pin transitive dep due to security issue
# In requirements.txt
urllib3~=1.26.0  # CVE-2021-XXXXX in <1.26
```

---

## Justification Requirements

**EVERY version specification must include inline justification:**

### Template:

```python
# requirements.txt

# Package name
package-name~=X.Y.Z  # Justification: [reason for this version/range]
```

### Good Examples:

```python
# Vector database (LanceDB concurrency fixes)
lancedb~=0.25.0  # Latest stable, 0.24.x had race condition bugs (GitHub #1234)

# Local embeddings (performance)
sentence-transformers~=2.2.0  # 2.2.x added M1/M2 optimization, 50% faster

# Testing framework (stability)
pytest~=7.4.0  # Mature, stable, follows SemVer strictly

# OpenAI API (compatibility)
openai>=1.0.0,<2.0.0  # 1.x stable, 2.x is alpha (breaking changes expected)

# Security fix
cryptography==41.0.4  # Exact pin: CVE-2023-XXXXX in <=41.0.3, 41.0.5+ untested
```

### Bad Examples:

```python
# Bad: No justification
lancedb>=0.3.0  # ❌ Why 0.3.0? Why no upper bound?

# Bad: Vague justification
requests>=2.20.0  # ❌ "Latest version" - not specific

# Bad: Unjustified exact pin
pytest==7.4.0  # ❌ Why exact? pytest is stable, use ~=

# Bad: Unbounded range
package>=1.0.0  # ❌ Allows any future version (non-deterministic)
```

---

## Research Protocol

**Before specifying ANY version, research:**

### 1. Check Package Maturity

```bash
# Look at PyPI page
pip show package-name

# Check version history
# - Many releases? Stable cadence? → Mature
# - Few releases? Irregular? 0.x versions? → Unstable
```

### 2. Read Changelog/Release Notes

**Key questions:**
- What changed between versions we're considering?
- Are there breaking changes?
- Are there bug fixes we need?
- Are there features we want?

**Example (lancedb research):**
```
0.25.1 (latest): Bug fixes for vector search edge cases
0.25.0: Stable release, major performance improvements
0.24.x: Had known race condition in concurrent writes (GitHub #789)
0.3.0: Very old, missing many features

Decision: Use ~=0.25.0 (latest stable, avoids 0.24.x bugs)
```

### 3. Check GitHub Issues

**Search for:**
- "breaking change"
- "regression"
- "compatibility"
- "thread safe" / "concurrent" (if relevant)

**Red flags:**
- Many issues about version X breaking things
- Comments like "Don't upgrade past version Y"
- Unresolved critical bugs in recent versions

### 4. Test the Version

**Minimum testing:**
```bash
# Create test environment
python -m venv test_env
source test_env/bin/activate

# Install candidate version
pip install package==X.Y.Z

# Run our tests
pytest tests/

# Run our code
python -m my_module
```

**If tests pass + code works → Safe to use**  
**If tests fail → Research what broke, choose different version**

---

## Special Cases

### Case 1: Pre-1.0 Libraries (Unstable)

```python
# Pre-1.0 doesn't follow SemVer guarantees
# Minor versions CAN have breaking changes

# Strategy: Pin to patch level
experimental-lib~=0.5.0  # Allows 0.5.x, blocks 0.6.x

# Or exact pin if very unstable
experimental-lib==0.5.2
```

### Case 2: Internal/First-Party Packages

```python
# Internal packages you control
honeyhive>=0.1.0  # Can use >=, you control breaking changes

# But still prefer ~= for transitive deps
honeyhive~=0.1.0  # Safer
```

### Case 3: Development vs Production

```python
# requirements.txt (production)
pytest~=7.4.0  # Stable, tested version

# requirements-dev.txt (development)
pytest>=7.4.0  # Allow newer versions for dev (but still bounded!)
```

### Case 4: Security Vulnerabilities

```python
# Exact pin when patching security issue
urllib3==1.26.18  # CVE-2023-XXXXX patched, 1.26.19+ untested

# Then: Test 1.26.19+, update to ~=1.26.18 after validation
```

### Case 5: Platform-Specific

```python
# Using platform markers
sentence-transformers~=2.2.0; platform_system != "Darwin"
sentence-transformers~=2.3.0; platform_system == "Darwin"
# Justification: 2.3.0 adds M1/M2 optimization for macOS
```

---

## Update Strategy

### When to Update Dependencies

**Reasons to update:**
- ✅ Security vulnerability patched
- ✅ Bug fix we need
- ✅ Feature we want
- ✅ Performance improvement
- ✅ Deprecation warning (future compatibility)

**NOT reasons to update:**
- ❌ "It's a new version" (if current version works, don't fix it)
- ❌ "Just to be up-to-date" (introduces risk without benefit)

### How to Update Safely

1. **Read the changelog**
   - What changed?
   - Any breaking changes?
   - Any deprecations?

2. **Update in test environment first**
   ```bash
   # Create isolated test env
   python -m venv test_update
   source test_update/bin/activate
   
   # Install new version
   pip install package==X.Y.Z
   
   # Run full test suite
   tox -e unit
   
   # Run integration tests
   tox -e integration
   ```

3. **Update version spec + justification**
   ```python
   # requirements.txt
   # Before:
   package~=1.5.0  # Stable version
   
   # After:
   package~=1.6.0  # Updated for security fix (CVE-2024-XXXXX)
   ```

4. **Commit with evidence**
   ```
   chore(deps): update package 1.5.0 → 1.6.0
   
   **Reason**: Security fix for CVE-2024-XXXXX
   **Testing**: All tests pass (2,904/2,904)
   **Changelog**: https://github.com/package/releases/tag/v1.6.0
   ```

---

## Commit Message Template

```
type(scope): action

**Dependency Changes:**
- Added: package-name~=X.Y.Z
  - Justification: [Why this package? Why this version?]
  - Research: [What did you learn from docs/changelog/issues?]
  - Testing: [How did you validate this works?]

- Updated: package-name X.Y.Z → A.B.C
  - Reason: [Why update? Security? Feature? Bug fix?]
  - Breaking changes: [None | Handled in code changes]
  - Testing: [All tests pass]

- Removed: package-name
  - Reason: [Why removed? No longer needed? Replaced by X?]
```

---

## Forbidden Patterns

### 1. Unbounded Version Ranges

```python
# FORBIDDEN
package>=1.0.0  # Allows ANY future version

# Allowed
package~=1.0.0  # Allows 1.0.x (patch updates only)
```

### 2. No Justification

```python
# FORBIDDEN
package~=2.5.0

# Required
package~=2.5.0  # Latest stable, fixes bug #123
```

### 3. Copy-Paste from Examples

```python
# FORBIDDEN (blindly copying from example)
# Someone's tutorial used lancedb>=0.3.0
lancedb>=0.3.0  # Copied without research

# Required (research + justification)
lancedb~=0.25.0  # Latest stable, researched changelog
```

### 4. "Latest" Without Upper Bound

```python
# FORBIDDEN
package>=2.0.0  # "Get latest 2.x"

# Required
package>=2.0.0,<3.0.0  # Explicit upper bound
# Or better:
package~=2.5.0  # Specific version + patches
```

---

## 🔗 Related Standards

**Query workflow for dependency pinning:**

1. **Start with this standard** → `pos_search_project(action="search_standards", query="Python SDK dependency pinning")`
2. **Learn production checklist** → `pos_search_project(action="search_standards", query="Python SDK production checklist")` → `standards/development/coding/production-checklist.md`
3. **Learn version bumping** → `pos_search_project(action="search_standards", query="Python SDK version bump")` → `standards/development/versioning/version-bump-quick-reference.md`

---

## Validation Checklist

**Before specifying a version:**

- [ ] Researched package maturity (stable vs experimental)
- [ ] Read changelog for relevant versions
- [ ] Checked GitHub issues for problems
- [ ] Tested the version in isolated environment
- [ ] Chose appropriate specifier (~=, ==, or range with upper bound)
- [ ] Wrote inline justification
- [ ] **NEVER used >=X.Y.Z without upper bound**

**If all checked → Version spec is justified**  
**If any unchecked → DO NOT COMMIT**

---

**💡 Key Principle**: 2 minutes of research prevents 2 hours of debugging production version conflicts.

