# Python SDK Release Process

**Ensure consistent, reliable, and secure release process with proper versioning and quality gates for the HoneyHive Python SDK.**

---

## 🚨 TL;DR - Release Process Quick Reference

**Keywords for search**: Python SDK release process, HoneyHive SDK release workflow, semantic versioning MAJOR MINOR PATCH, release checklist pre-release validation, quality gates code coverage testing, backwards compatibility deprecation, migration guide breaking changes, hotfix process emergency release, release automation GitHub Actions, PyPI publish twine, rollback procedures post-release monitoring, version tagging git tag, release candidate RC alpha beta, release validation script

**Core Principle:** Semantic versioning (MAJOR.MINOR.PATCH) with mandatory pre-release validation. Version is managed in `src/honeyhive/__init__.py` only.

**Release Types:**
- **Patch** (x.y.Z): Bug fixes, security patches (fast-track)
- **Minor** (x.Y.0): New features, backwards compatible (standard)
- **Major** (X.0.0): Breaking changes (extended validation + migration guide)
- **Hotfix**: Critical issues (emergency fast-track)

**Mandatory Pre-Release Checks:**
- [ ] All tests pass (`tox -e unit -e integration`)
- [ ] Code coverage ≥80% overall
- [ ] Linting passes (pylint ≥8.0, mypy clean)
- [ ] Security scan passes (`pip-audit`, `safety check`)
- [ ] Documentation builds without warnings
- [ ] Version updated in `src/honeyhive/__init__.py`
- [ ] CHANGELOG.md updated with release notes
- [ ] Migration guide created (if breaking changes)

**Release Execution:**
1. Update `src/honeyhive/__init__.py` and `CHANGELOG.md`
2. Merge to `main` via PR
3. Workflow auto-publishes to PyPI
4. Monitor for issues

**DO NOT update `pyproject.toml` version** - not used for releases.

---

## ❓ Questions This Answers

1. "What is the Python SDK release process?"
2. "How do I create a release for Python SDK?"
3. "What are the release types for Python SDK?"
4. "What is semantic versioning for Python SDK?"
5. "What pre-release validation is required?"
6. "What code coverage is required for releases?"
7. "How do I handle breaking changes in releases?"
8. "What is the hotfix process for Python SDK?"
9. "How do I rollback a release?"
10. "What is the deprecation process?"
11. "How do I create a migration guide?"
12. "What is the release automation workflow?"
13. "How do I publish to PyPI?"
14. "What post-release activities are required?"
15. "How do I create a patch vs minor vs major release?"
16. "What are the quality gates for releases?"
17. "How do I validate a release?"
18. "What security checks are required?"
19. "How do I handle backwards compatibility?"
20. "What is the release communication process?"

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Creating release** | `pos_search_project(action="search_standards", query="Python SDK release process")` |
| **Pre-release validation** | `pos_search_project(action="search_standards", query="Python SDK release checklist validation")` |
| **Breaking changes** | `pos_search_project(action="search_standards", query="Python SDK breaking changes migration guide")` |
| **Hotfix needed** | `pos_search_project(action="search_standards", query="Python SDK hotfix process emergency")` |
| **Semantic versioning** | `pos_search_project(action="search_standards", query="Python SDK semantic versioning MAJOR MINOR PATCH")` |
| **Deprecation** | `pos_search_project(action="search_standards", query="Python SDK deprecation process")` |
| **Rollback** | `pos_search_project(action="search_standards", query="Python SDK rollback release")` |

---

## 🎯 Purpose

Define the complete release process for the HoneyHive Python SDK to ensure consistent, reliable, and secure releases with proper versioning, quality gates, and backwards compatibility.

**Without this standard**: Inconsistent releases, missed quality checks, broken backwards compatibility, unclear versioning, and production issues.

---

## Semantic Versioning

**Follow [Semantic Versioning 2.0.0](https://semver.org/)**: `MAJOR.MINOR.PATCH`

**Format:**
```bash
0.1.0 - Initial beta release
0.1.1 - Bug fixes (patch)
0.2.0 - New features, backwards compatible (minor)
1.0.0 - First stable release (major)
2.0.0 - Breaking changes (major)
```

### Version Increment Rules

- **MAJOR (X.0.0)**: Breaking changes, incompatible API changes
- **MINOR (x.Y.0)**: New features, backwards compatible additions
- **PATCH (x.y.Z)**: Bug fixes, backwards compatible fixes

### Pre-release Versions

```bash
1.0.0alpha1  # Early testing
1.0.0beta1   # Feature complete, testing
1.0.0rc1     # Release candidate
1.0.0        # Stable
```

**See also:** `standards/development/versioning/version-bump-quick-reference.md`

---

## Pre-Release Validation (Mandatory Checklist)

### Code Quality Gates

- [ ] **All tests pass**: `tox -e unit -e integration`
- [ ] **Code coverage**: Minimum 80% overall, 100% for critical paths
- [ ] **Linting**: Pylint score ≥8.0/10.0, MyPy passes with no errors
- [ ] **Security scan**: `pip-audit` and `safety check` pass
- [ ] **Documentation**: Sphinx builds without warnings (`cd docs && make html`)

### Version and Documentation Updates

- [ ] **Version bump**: Update version in `src/honeyhive/__init__.py` (line 6)
- [ ] **CHANGELOG.md**: Add release notes with breaking changes
- [ ] **Migration guide**: Create if breaking changes exist
- [ ] **API documentation**: Verify all new APIs documented
- [ ] **DO NOT update `pyproject.toml`**: Version there is not used

### Compatibility and Performance

- [ ] **Backwards compatibility**: Verify existing code still works
- [ ] **Performance**: No significant regressions (>10%)
- [ ] **Dependencies**: All dependencies up to date and secure
- [ ] **Python versions**: Test on all supported Python versions (3.11, 3.12, 3.13)

### Release Artifacts

- [ ] **Build packages**: `python -m build` succeeds
- [ ] **Package validation**: `twine check dist/*` passes
- [ ] **Installation test**: Fresh install works in clean environment
- [ ] **Example verification**: All examples in documentation work

---

## Release Execution Process

### Step 1: Update Version

**File:** `src/honeyhive/__init__.py` (line 6)

```python
__version__ = "1.2.0"  # Update this line only
```

**DO NOT update `pyproject.toml`** - The release workflow reads from `__init__.py`.

### Step 2: Update CHANGELOG.md

Add release notes at the top:

```markdown
## [1.2.0] - 2025-11-08

### Added
- New features

### Changed
- Updated behavior

### Fixed
- Bug fixes

### Breaking Changes
- Any breaking changes (with migration guide link)

[1.2.0]: https://github.com/honeyhiveai/python-sdk/compare/v1.1.0...v1.2.0
```

### Step 3: Create Release PR

```bash
git checkout -b release/v1.2.0
git add src/honeyhive/__init__.py CHANGELOG.md
git commit -m "release: prepare v1.2.0"
git push origin release/v1.2.0
```

Create PR with checklist:

```markdown
## Release v1.2.0

### Pre-Release Validation
- [x] All tests passing
- [x] Code coverage ≥80%
- [x] Linting passes
- [x] Security scan passes
- [x] Documentation builds
- [x] Version updated in __init__.py
- [x] CHANGELOG.md updated
- [x] Migration guide created (if needed)

### Changes Summary
- New features: [list]
- Bug fixes: [list]
- Breaking changes: [list with migration guide link]

### Ready for Release
- [x] All validation complete
- [x] Ready to merge and publish
```

### Step 4: Merge and Publish

After PR approval:
1. Merge PR to `main`
2. Workflow automatically:
   - Detects version change in `src/honeyhive/__init__.py`
   - Runs tests
   - Builds package
   - Publishes to PyPI
   - Creates GitHub release

**No manual publish required** - workflow handles everything.

---

## Release Types

### Patch Releases (x.y.Z) - Bug Fixes

**Criteria:**
- Bug fixes only
- No new features
- No breaking changes
- Security patches

**Process:**
- Fast-track approval
- Minimal testing (unit + integration)
- Can be released quickly

**Example:** `1.2.3` → `1.2.4`

### Minor Releases (x.Y.0) - New Features

**Criteria:**
- New features
- Backwards compatible
- API additions (no removals)
- Performance improvements

**Process:**
- Full testing cycle
- Documentation updates required
- Standard review process

**Example:** `1.2.4` → `1.3.0`

### Major Releases (X.0.0) - Breaking Changes

**Criteria:**
- Breaking API changes
- Major architecture changes
- Removal of deprecated features
- Significant behavior changes

**Process:**
- Extended testing period
- Migration guide required (mandatory)
- Community feedback period
- Deprecation warnings in previous minor releases

**Example:** `1.3.0` → `2.0.0`

---

## Hotfix Process (Emergency Releases)

For critical security issues or major bugs:

```bash
# 1. Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/v1.2.4

# 2. Implement minimal fix
# ... make changes ...

# 3. Test thoroughly
tox -e unit -e integration

# 4. Update version and changelog
# Edit src/honeyhive/__init__.py: __version__ = "1.2.4"
# Edit CHANGELOG.md with hotfix details

# 5. Commit and push
git add src/honeyhive/__init__.py CHANGELOG.md
git commit -m "fix: critical security issue (CVE-2024-XXXX)"
git push origin hotfix/v1.2.4

# 6. Create PR with "hotfix" label for priority review
# 7. After merge, workflow auto-publishes
```

**Fast-track approval required for hotfixes.**

---

## Backwards Compatibility

### Deprecation Process

When deprecating features:

```python
import warnings
from typing import Optional

def old_method(self) -> str:
    """
    Deprecated method.
    
    .. deprecated:: 1.1.0
       Use :meth:`new_method` instead.
    """
    warnings.warn(
        "old_method is deprecated and will be removed in v2.0.0. "
        "Use new_method instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return self.new_method()

def new_method(self) -> str:
    """New improved method."""
    return "new implementation"
```

**Deprecation Timeline:**
1. **Minor release N**: Add deprecation warning, old method still works
2. **Minor release N+1**: Deprecation warning remains
3. **Major release N+2**: Remove old method

### Migration Guides (Required for Breaking Changes)

Create migration guide for major releases:

```markdown
# Migration Guide: v1.x to v2.0

## Breaking Changes

### 1. API Client Initialization

**Old (v1.x)**:
```python
client = HoneyHiveClient(api_key="key", project="proj")
```

**New (v2.0)**:
```python
tracer = HoneyHiveTracer(api_key="key", project="proj")
```

### 2. Migration Steps

1. Update initialization code
2. Update method calls
3. Test thoroughly
4. Deploy

### 3. Automated Migration

```bash
python scripts/migrate_v1_to_v2.py --path src/
```
```

---

## Post-Release Activities

### Release Communication

1. **Update Documentation**:
   - Refresh getting started guides
   - Update API reference
   - Verify all examples work

2. **Community Notification**:
   - GitHub release notes (automatic)
   - Documentation changelog
   - Social media announcements (if major release)

3. **Monitoring**:
   - Monitor PyPI download stats
   - Watch for issue reports
   - Track adoption metrics

### Release Metrics

Track these metrics for each release:

- **Download count**: PyPI downloads in first week
- **Issue reports**: New issues opened post-release
- **Adoption rate**: Usage in existing projects
- **Performance impact**: Benchmark comparisons
- **Documentation usage**: Most accessed docs pages

---

## Rollback Procedures

### Emergency Rollback

If critical issues are discovered post-release:

```bash
# 1. Create immediate hotfix release
git checkout v1.2.0  # Last known good version
git checkout -b hotfix/v1.2.2

# 2. Implement fix or revert problematic changes
# ... make changes ...

# 3. Fast-track release process (follow hotfix workflow above)
```

**Note:** Cannot remove releases from PyPI once published. Must create new release.

### Communication During Rollback

1. **Immediate notification**: GitHub issue, documentation banner
2. **Workaround guidance**: Temporary solutions for affected users
3. **Timeline communication**: Expected fix timeline
4. **Post-mortem**: Analysis of what went wrong and prevention measures

---

## 🔗 Related Standards

**Query workflow for releases:**

1. **Start with this standard** → `pos_search_project(action="search_standards", query="Python SDK release process")`
2. **Learn version bump** → `pos_search_project(action="search_standards", query="Python SDK version bump")` → `standards/development/versioning/version-bump-quick-reference.md`
3. **Understand git workflow** → `pos_search_project(action="search_standards", query="Python SDK git workflow")` → `standards/development/workflow/git-workflow.md`
4. **Learn testing requirements** → `pos_search_project(action="search_standards", query="Python SDK testing standards")` → `standards/development/testing/testing-standards.md`

**By Category:**

**Versioning:**
- `standards/development/versioning/version-bump-quick-reference.md` → `pos_search_project(action="search_standards", query="Python SDK version bump")`
- `standards/development/versioning/dependency-pinning.md` → `pos_search_project(action="search_standards", query="Python SDK dependency pinning")`

**Workflow:**
- `standards/development/workflow/git-workflow.md` → `pos_search_project(action="search_standards", query="Python SDK git workflow")`

**Testing:**
- `standards/development/testing/testing-standards.md` → `pos_search_project(action="search_standards", query="Python SDK testing")`

**Universal Standards:**
- `standards/universal/workflows/workflow-system-overview.md` → `pos_search_project(action="search_standards", query="workflow system best practices")`

---

## Validation Checklist

Before marking release as complete:

- [ ] Version updated in `src/honeyhive/__init__.py` only (not pyproject.toml)
- [ ] CHANGELOG.md updated with release notes
- [ ] All pre-release validation checks passed
- [ ] Migration guide created (if breaking changes)
- [ ] Documentation updated
- [ ] Release PR approved and merged
- [ ] Workflow published to PyPI successfully
- [ ] GitHub release created
- [ ] Post-release monitoring active
- [ ] Community notified (if major release)

---

**📝 Remember**: Version is managed in `src/honeyhive/__init__.py` only. DO NOT update `pyproject.toml`. The release workflow reads from `__init__.py` and handles PyPI publishing automatically.

