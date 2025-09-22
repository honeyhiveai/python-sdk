# Release Process - HoneyHive Python SDK

**🎯 MISSION: Ensure consistent, reliable, and secure release process with proper versioning and quality gates**

## Version Management

### Semantic Versioning

**Follow [Semantic Versioning 2.0.0](https://semver.org/)**: `MAJOR.MINOR.PATCH`

```bash
# Version format: MAJOR.MINOR.PATCH
0.1.0 - Initial beta release
0.1.1 - Bug fixes (patch)
0.2.0 - New features, backwards compatible (minor)
1.0.0 - First stable release (major)
2.0.0 - Breaking changes (major)
```

### Version Increment Rules

- **MAJOR**: Breaking changes, incompatible API changes
- **MINOR**: New features, backwards compatible additions
- **PATCH**: Bug fixes, backwards compatible fixes

### Pre-release Versions

```bash
# Pre-release suffixes
1.0.0-alpha.1    # Alpha release
1.0.0-beta.1     # Beta release  
1.0.0-rc.1       # Release candidate
```

## Release Checklist

### Pre-Release Validation

**MANDATORY: Complete ALL items before release**

#### Code Quality Gates
- [ ] **All tests pass**: `tox -e unit -e integration`
- [ ] **Code coverage**: Minimum 80% overall, 100% for critical paths
- [ ] **Linting**: Pylint score ≥8.0/10.0, MyPy passes with no errors
- [ ] **Security scan**: `pip-audit` and `safety check` pass
- [ ] **Documentation**: Sphinx builds without warnings

#### Version and Documentation Updates
- [ ] **Version bump**: Update version in `pyproject.toml`
- [ ] **CHANGELOG.md**: Add release notes with breaking changes
- [ ] **docs/changelog.rst**: Update user-facing changelog
- [ ] **Migration guide**: Create if breaking changes exist
- [ ] **API documentation**: Verify all new APIs documented

#### Compatibility and Performance
- [ ] **Backwards compatibility**: Verify existing code still works
- [ ] **Performance**: No significant regressions (>10%)
- [ ] **Dependencies**: All dependencies up to date and secure
- [ ] **Python versions**: Test on all supported Python versions

#### Release Artifacts
- [ ] **Build packages**: `python -m build` succeeds
- [ ] **Package validation**: `twine check dist/*` passes
- [ ] **Installation test**: Fresh install works in clean environment
- [ ] **Example verification**: All examples in documentation work

### Release Execution

#### 1. Prepare Release Branch

```bash
# Create release branch
git checkout main
git pull origin main
git checkout -b release/v1.2.0

# Update version
# Edit pyproject.toml: version = "1.2.0"

# Update changelog
# Edit CHANGELOG.md and docs/changelog.rst

# Commit changes
git add .
git commit -m "chore: prepare v1.2.0 release"
git push origin release/v1.2.0
```

#### 2. Create Release PR

```markdown
# Release PR Template

## Release v1.2.0

### Changes
- [x] Version updated to 1.2.0
- [x] CHANGELOG.md updated
- [x] docs/changelog.rst updated
- [x] All tests passing
- [x] Documentation updated

### Breaking Changes
- List any breaking changes
- Link to migration guide

### New Features
- List new features
- Link to documentation

### Bug Fixes
- List bug fixes
- Reference issue numbers

### Checklist
- [x] All pre-release validation completed
- [x] Migration guide created (if needed)
- [x] Examples updated and tested
- [x] Ready for release
```

#### 3. Tag and Release

```bash
# After PR approval and merge
git checkout main
git pull origin main

# Create and push tag
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin v1.2.0

# Build and publish
python -m build
twine upload dist/*

# Create GitHub release
gh release create v1.2.0 \
  --title "Release v1.2.0" \
  --notes-file RELEASE_NOTES.md \
  --draft=false
```

## Backwards Compatibility

### Deprecation Process

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

### API Versioning

```python
class APIClient:
    """API client with version support."""
    
    def __init__(self, api_version: str = "v2"):
        self.api_version = api_version
        
        if api_version == "v1":
            warnings.warn(
                "API v1 is deprecated and will be removed in v2.0.0",
                DeprecationWarning
            )
    
    def make_request(self, endpoint: str, **kwargs):
        """Make API request with version handling."""
        if self.api_version == "v1":
            return self._handle_v1_request(endpoint, **kwargs)
        else:
            return self._handle_v2_request(endpoint, **kwargs)
```

### Migration Guides

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

### 2. Tracing Decorators

**Old (v1.x)**:
```python
@honeyhive_trace(event_type="model")
def my_function():
    pass
```

**New (v2.0)**:
```python
from honeyhive import trace
from honeyhive.models import EventType

@trace(event_type=EventType.model)
def my_function():
    pass
```

## Automated Migration

Use the migration script to update your code:

```bash
python scripts/migrate_v1_to_v2.py --path src/
```
```

## Release Types

### Patch Releases (Bug Fixes)

**Criteria**:
- Bug fixes only
- No new features
- No breaking changes
- Security patches

**Process**:
- Can be released from main branch
- Minimal testing required
- Fast-track approval process

### Minor Releases (New Features)

**Criteria**:
- New features
- Backwards compatible
- API additions (no removals)
- Performance improvements

**Process**:
- Full testing cycle
- Documentation updates required
- Standard review process

### Major Releases (Breaking Changes)

**Criteria**:
- Breaking API changes
- Major architecture changes
- Removal of deprecated features
- Significant behavior changes

**Process**:
- Extended testing period
- Migration guide required
- Community feedback period
- Deprecation warnings in previous minor releases

## Hotfix Process

### Emergency Releases

For critical security issues or major bugs:

```bash
# Create hotfix branch from latest release tag
git checkout v1.2.0
git checkout -b hotfix/v1.2.1

# Implement minimal fix
# ... make changes ...

# Test thoroughly
tox -e unit -e integration

# Update version and changelog
# Edit pyproject.toml: version = "1.2.1"
# Edit CHANGELOG.md with hotfix details

# Commit and tag
git add .
git commit -m "fix: critical security issue (CVE-2024-XXXX)"
git tag -a v1.2.1 -m "Hotfix release v1.2.1"

# Push and release
git push origin hotfix/v1.2.1
git push origin v1.2.1

# Fast-track release
python -m build
twine upload dist/*

# Merge back to main
git checkout main
git merge hotfix/v1.2.1
git push origin main
```

## Release Automation

### GitHub Actions Release Workflow

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install build twine
      
      - name: Run tests
        run: |
          tox -e unit -e integration
      
      - name: Build package
        run: |
          python -m build
      
      - name: Validate package
        run: |
          twine check dist/*
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
        run: |
          twine upload dist/*
      
      - name: Create GitHub Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          draft: false
          prerelease: false
```

### Release Validation Script

```python
#!/usr/bin/env python3
"""Release validation script."""

import subprocess
import sys
from pathlib import Path

def run_command(cmd: str) -> bool:
    """Run command and return success status."""
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {cmd}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {cmd}")
        print(f"Error: {e.stderr}")
        return False

def validate_release():
    """Validate release readiness."""
    checks = [
        "tox -e unit",
        "tox -e integration", 
        "tox -e lint",
        "python -m build",
        "twine check dist/*",
        "pip-audit",
        "safety check",
    ]
    
    print("🚀 Validating release readiness...")
    
    failed_checks = []
    for check in checks:
        if not run_command(check):
            failed_checks.append(check)
    
    if failed_checks:
        print(f"\n❌ {len(failed_checks)} checks failed:")
        for check in failed_checks:
            print(f"  - {check}")
        sys.exit(1)
    
    print(f"\n✅ All {len(checks)} checks passed! Ready for release.")

if __name__ == "__main__":
    validate_release()
```

## Post-Release Activities

### Release Communication

1. **Update Documentation**:
   - Refresh getting started guides
   - Update API reference
   - Verify all examples work

2. **Community Notification**:
   - GitHub release notes
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

## Rollback Procedures

### Emergency Rollback

If critical issues are discovered post-release:

```bash
# Remove problematic release from PyPI (if possible)
# This is rarely possible due to PyPI policies

# Create immediate hotfix release
git checkout v1.2.0  # Last known good version
git checkout -b hotfix/v1.2.2

# Implement fix or revert problematic changes
# ... make changes ...

# Fast-track release process
# Follow hotfix process above
```

### Communication During Rollback

1. **Immediate notification**: GitHub issue, documentation banner
2. **Workaround guidance**: Temporary solutions for affected users
3. **Timeline communication**: Expected fix timeline
4. **Post-mortem**: Analysis of what went wrong and prevention measures

## References

- **[Git Workflow](git-workflow.md)** - Branching and tagging standards
- **[Testing Standards](testing-standards.md)** - Quality gates for releases
- **[Security Practices](../security/practices.md)** - Security considerations for releases

---

**📝 Next Steps**: Review [Git Workflow](git-workflow.md) for branching and tagging standards.
