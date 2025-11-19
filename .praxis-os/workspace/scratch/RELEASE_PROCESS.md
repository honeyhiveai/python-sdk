# Release Process

**Date Created:** October 31, 2025  
**Branch:** complete-refactor  
**Automation:** GitHub Actions workflow

---

## Overview

The HoneyHive Python SDK uses an **automated release process** that triggers when the version is updated in the source code and merged to `main`.

**Key Principles:**
- ✅ **Idempotent**: Safe to re-run, won't re-publish existing versions
- ✅ **Automatic**: Merging version bump to main triggers release
- ✅ **Validated**: Checks PyPI before publishing
- ✅ **Complete**: Publishes to PyPI + creates GitHub release

---

## Quick Start - Releasing a New Version

### 1. Update Version

Edit `src/honeyhive/__init__.py`:

```python
# Change this line:
__version__ = "0.1.0rc3"

# To new version:
__version__ = "1.0.0"
```

### 2. Update CHANGELOG

Add entry to `CHANGELOG.md`:

```markdown
## [1.0.0] - 2025-10-31

### Added
- Multi-instance tracer architecture for proper isolation
- Direct OpenTelemetry integration (removed Traceloop dependency)
- Automatic input capture in @trace decorator

### Changed
- evaluate() now supports tracer parameter for enhanced features
- Improved thread safety and context propagation

### Breaking Changes
- Evaluation functions need `tracer` parameter for enrichment features
- See MIGRATION_GUIDE.md for details

[1.0.0]: https://github.com/honeyhiveai/python-sdk/compare/v0.1.0rc3...v1.0.0
```

### 3. Commit and Create PR

```bash
git checkout -b release-v1.0.0
git add src/honeyhive/__init__.py CHANGELOG.md
git commit -m "Release v1.0.0"
git push origin release-v1.0.0

# Create PR to main
gh pr create --title "Release v1.0.0" --body "See CHANGELOG.md for details"
```

### 4. Merge to Main

Once PR is approved and merged to `main`, the workflow **automatically**:

1. ✅ Extracts version from `__init__.py`
2. ✅ Checks if version exists on PyPI
3. ✅ If new: Builds, tests, publishes to PyPI
4. ✅ Creates GitHub release with tag `v1.0.0`
5. ✅ If exists: Exits successfully with message

**That's it!** No manual steps needed.

---

## Workflow Details

### Trigger

**File:** `.github/workflows/sdk-publish.yml`

**Triggers on:**
```yaml
on:
  push:
    branches:
      - main
    paths:
      - 'src/honeyhive/__init__.py'
```

Any push to `main` that changes `src/honeyhive/__init__.py` triggers the workflow.

### What Happens

```
┌─────────────────────────────────────────────────────┐
│ 1. Push to main (with __init__.py change)          │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│ 2. Extract version from __init__.py                 │
│    Example: "1.0.0"                                 │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│ 3. Query PyPI: Does version 1.0.0 exist?           │
└─────────────────┬───────────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
   ┌────────┐         ┌──────────┐
   │ EXISTS │         │ NEW      │
   └────┬───┘         └─────┬────┘
        │                   │
        │                   ▼
        │         ┌─────────────────────┐
        │         │ 4. Build package    │
        │         └──────────┬──────────┘
        │                    │
        │                    ▼
        │         ┌─────────────────────┐
        │         │ 5. Test install     │
        │         └──────────┬──────────┘
        │                    │
        │                    ▼
        │         ┌─────────────────────┐
        │         │ 6. Publish to PyPI  │
        │         └──────────┬──────────┘
        │                    │
        │                    ▼
        │         ┌─────────────────────┐
        │         │ 7. Create GH release│
        │         └──────────┬──────────┘
        │                    │
        ▼                    ▼
   ┌────────────────────────────┐
   │ ✅ Workflow Complete        │
   │                            │
   │ Message: "Already published│
   │ Message: "Published v1.0.0"│
   └────────────────────────────┘
```

---

## Version Numbering

We follow [Semantic Versioning](https://semver.org/):

### Format: `MAJOR.MINOR.PATCH[PRERELEASE]`

**Examples:**
- `1.0.0` - Stable release
- `1.1.0` - Minor feature addition
- `1.0.1` - Bug fix
- `1.0.0rc1` - Release candidate
- `1.0.0alpha1` - Alpha release
- `1.0.0beta1` - Beta release

### When to Bump

**MAJOR** (`1.0.0` → `2.0.0`):
- Breaking API changes
- Incompatible with previous version
- Requires user code changes

**MINOR** (`1.0.0` → `1.1.0`):
- New features (backward compatible)
- New functionality
- Deprecations (with backward compatibility)

**PATCH** (`1.0.0` → `1.0.1`):
- Bug fixes
- Performance improvements
- Documentation updates
- No API changes

**PRERELEASE** (`1.0.0rc1`, `1.0.0rc2`, ...):
- Testing before stable release
- Release candidates, alphas, betas
- Not guaranteed stable

---

## Release Checklist

### Before Creating PR

- [ ] **Update version** in `src/honeyhive/__init__.py`
- [ ] **Update CHANGELOG.md** with all changes
- [ ] **Run full test suite** locally
  ```bash
  tox -e unit
  tox -e integration
  tox -e lint
  tox -e format
  tox -e docs
  ```
- [ ] **Test package build** locally
  ```bash
  python -m build
  twine check dist/*
  ```
- [ ] **Update documentation** if API changed
- [ ] **Review breaking changes** and update migration guide

### PR Review

- [ ] **All tests passing** in CI
- [ ] **Documentation builds** successfully
- [ ] **CHANGELOG complete** and accurate
- [ ] **Version number appropriate** for changes
- [ ] **No linter errors**

### After Merge

- [ ] **Wait for workflow** to complete (5-10 minutes)
- [ ] **Verify PyPI** publication
  ```bash
  pip index versions honeyhive
  ```
- [ ] **Test installation** from PyPI
  ```bash
  pip install honeyhive==1.0.0
  python -c "import honeyhive; print(honeyhive.__version__)"
  ```
- [ ] **Verify GitHub release** created
- [ ] **Announce release** (if major/minor)

---

## Troubleshooting

### Workflow Skipped Publishing

**Symptom:** Workflow shows "Version already published"

**Cause:** Version exists on PyPI

**Solution:**
1. Check current PyPI version: https://pypi.org/project/honeyhive/
2. Bump version in `__init__.py` to a new version
3. Create new PR and merge

### Workflow Failed on Build

**Symptom:** Build step fails

**Common Causes:**
- Syntax error in Python code
- Missing dependency
- Import error

**Solution:**
1. Test build locally: `python -m build`
2. Fix errors
3. Re-push to main (or re-run workflow)

### Workflow Failed on Publish

**Symptom:** Publish to PyPI fails

**Common Causes:**
- Invalid `PYPI_TOKEN` secret
- Network issue
- PyPI outage

**Solution:**
1. Verify `PYPI_TOKEN` secret is set in GitHub repo settings
2. Check PyPI status: https://status.python.org/
3. Re-run workflow after issue resolved

### GitHub Release Not Created

**Symptom:** Package on PyPI but no GitHub release

**Common Causes:**
- Insufficient permissions
- `GITHUB_TOKEN` issue

**Solution:**
1. Verify workflow has `contents: write` permission
2. Manually create release from GitHub UI if needed
3. Tag should be `v{version}` (e.g., `v1.0.0`)

---

## Manual Release (Emergency)

If automated workflow fails and you need to publish immediately:

### 1. Build Package

```bash
# Ensure version is updated in __init__.py
python -m build
```

### 2. Test Package

```bash
twine check dist/*

# Test installation
python -m venv test-env
source test-env/bin/activate
pip install dist/*.whl
python -c "import honeyhive; print(honeyhive.__version__)"
deactivate
```

### 3. Publish to PyPI

```bash
# Set token
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=<your-pypi-token>

# Upload
twine upload dist/*
```

### 4. Create GitHub Release

```bash
# Create tag
git tag v1.0.0
git push origin v1.0.0

# Create release via GitHub CLI
gh release create v1.0.0 \
  --title "v1.0.0" \
  --notes "See CHANGELOG.md for details"
```

---

## Security

### PyPI Token

**Location:** GitHub repository secrets

**Key:** `PYPI_TOKEN`

**Scope:** Upload to `honeyhive` package only

**Rotation:**
1. Generate new token at https://pypi.org/manage/account/token/
2. Update `PYPI_TOKEN` secret in GitHub repo settings
3. Test with a pre-release version
4. Revoke old token

### GitHub Token

**Automatic:** GitHub provides `GITHUB_TOKEN` automatically

**Permissions:** Set in workflow file (`contents: write`)

---

## Testing New Workflow

To test workflow changes without publishing:

### 1. Test with TestPyPI

Update workflow temporarily:

```yaml
# Change this:
- name: Publish to PyPI
  run: python -m twine upload dist/*

# To this:
- name: Publish to TestPyPI
  run: python -m twine upload --repository testpypi dist/*
```

**Requirements:**
- TestPyPI account: https://test.pypi.org/
- TestPyPI token in `TEST_PYPI_TOKEN` secret

### 2. Use Pre-release Version

Test with version like `1.0.0rc999` that won't conflict with production.

---

## Historical Context

### Previous System (Main Branch)

- Used Speakeasy for SDK generation
- Triggered on `RELEASES.md` changes
- Speakeasy handled publishing

### Current System (Complete-Refactor)

- Hand-written SDK (no Speakeasy)
- Triggered on `__init__.py` version changes
- Native Python build and publish
- Idempotent (safe to re-run)

**Advantages:**
- ✅ Simpler (no external dependencies)
- ✅ More control (we own the build)
- ✅ Safer (version validation)
- ✅ Single source of truth (`__init__.py`)

---

## FAQ

### Q: Can I publish from a branch other than main?

**A:** No. Workflow only triggers on pushes to `main`. This ensures:
- All releases go through PR review
- Main branch always reflects released code
- No accidental releases from feature branches

### Q: What if I need to publish a hotfix urgently?

**A:** 
1. Create hotfix branch from main
2. Make fix and bump PATCH version
3. Create PR with fast-track review
4. Merge to main → automatic release

For true emergencies, use manual release process (see above).

### Q: Can I re-publish the same version?

**A:** No. PyPI doesn't allow replacing published versions. If you need to fix a release:
1. Bump to next PATCH version (e.g., `1.0.0` → `1.0.1`)
2. Yank bad version on PyPI (if critical bug)
3. Publish fixed version

### Q: What if the workflow says "already published" but I updated the version?

**A:** The workflow uses the version from `__init__.py` in the commit that was pushed. Ensure:
1. You actually changed `__init__.py`
2. The change was included in the commit
3. The commit was pushed to main

Check the workflow logs for "Detected version: X.X.X" to see what version it found.

### Q: How do I publish a pre-release?

**A:**
1. Use version like `1.0.0rc1` in `__init__.py`
2. GitHub release will be marked as "pre-release" automatically
3. Users need `pip install honeyhive==1.0.0rc1` (not installed by default)

---

## Support

**For release issues:**
1. Check workflow logs in GitHub Actions
2. Review this document
3. Check PyPI status: https://status.python.org/
4. Contact repository maintainer

---

**Document Version:** 1.0  
**Last Updated:** October 31, 2025  
**Workflow File:** `.github/workflows/sdk-publish.yml`

