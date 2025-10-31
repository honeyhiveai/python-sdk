Release Process and PyPI Publishing
===================================

.. note::
   **Internal HoneyHive SDK Development - Release Management**
   
   Release process and PyPI publishing workflows for HoneyHive SDK maintainers and contributors. For SDK installation, see :doc:`../tutorials/01-setup-first-tracer`.

This guide covers the automated release process for publishing the HoneyHive Python SDK to PyPI. The SDK uses version-based triggering with automated validation and publishing.

**Current Release Infrastructure**:

- **Trigger**: Push to ``main`` branch with version change in ``src/honeyhive/__init__.py``
- **Validation**: Automatic PyPI version check (idempotent, won't re-publish)
- **Testing**: Full test suite must pass before merge
- **Publishing**: Automatic PyPI upload with GitHub release creation
- **Safety**: Version format validation, package integrity checks, installation testing

Release Workflow Architecture
-----------------------------

**Automated Release Pipeline** (``sdk-publish.yml``):

The SDK uses a version-triggered release workflow that executes on every push to ``main`` that modifies the version file:

.. code-block:: yaml

   # .github/workflows/sdk-publish.yml
   on:
     push:
       branches: [main]
       paths:
         - 'src/honeyhive/__init__.py'

**Workflow Execution Flow**:

1. **Version Extraction**: Parse ``__version__`` from ``src/honeyhive/__init__.py``
2. **PyPI Validation**: Query PyPI API to check if version exists
3. **Conditional Execution**:
   
   - **Version exists**: Exit successfully with "already published" message
   - **Version is new**: Continue to build and publish

4. **Package Build**: Create source distribution and wheel
5. **Integrity Verification**: Run ``twine check`` on built packages
6. **Installation Test**: Test package installation in clean environment
7. **PyPI Publication**: Upload to PyPI using ``PYPI_TOKEN`` secret
8. **GitHub Release**: Create release with version tag
9. **Verification**: Confirm package availability on PyPI

**Idempotent Design**:

The workflow is safe to re-run multiple times. If the version already exists on PyPI, the workflow exits successfully without attempting to re-publish. This prevents errors from accidental re-runs or non-version changes to ``__init__.py``.

Version Management
------------------

**Version Source of Truth**:

The SDK version is defined in a single location:

.. code-block:: python

   # src/honeyhive/__init__.py
   __version__ = "1.0.0"

All SDK modules import version from this file:

.. code-block:: python

   from honeyhive import __version__

**Version Format Requirements**:

The workflow validates version strings against the following pattern:

- **Stable releases**: ``X.Y.Z`` (e.g., ``1.0.0``, ``1.2.3``)
- **Release candidates**: ``X.Y.Zrc#`` (e.g., ``1.0.0rc1``, ``1.0.0rc2``)
- **Alpha releases**: ``X.Y.Zalpha#`` (e.g., ``1.0.0alpha1``)
- **Beta releases**: ``X.Y.Zbeta#`` (e.g., ``1.0.0beta1``)

Invalid version formats will cause the workflow to fail early with a validation error.

**Semantic Versioning**:

The SDK follows `Semantic Versioning <https://semver.org/>`_ (SemVer):

- **MAJOR** (``1.0.0`` → ``2.0.0``): Breaking API changes
- **MINOR** (``1.0.0`` → ``1.1.0``): New features (backward compatible)
- **PATCH** (``1.0.0`` → ``1.0.1``): Bug fixes (backward compatible)

Release Procedure
-----------------

**Standard Release Process**:

1. **Update Version**:

   .. code-block:: bash

      # Edit src/honeyhive/__init__.py
      __version__ = "1.0.0"

2. **Update Changelog**:

   Add release notes to ``CHANGELOG.md``:

   .. code-block:: markdown

      ## [1.0.0] - 2025-10-31

      ### Added
      - Multi-instance tracer architecture
      - Direct OpenTelemetry integration

      ### Changed
      - Improved thread safety and context propagation

      ### Breaking Changes
      - See MIGRATION_GUIDE.md for details

3. **Create Release Branch**:

   .. code-block:: bash

      git checkout -b release-v1.0.0
      git add src/honeyhive/__init__.py CHANGELOG.md
      git commit -m "Release v1.0.0"
      git push origin release-v1.0.0

4. **Create Pull Request**:

   .. code-block:: bash

      gh pr create --title "Release v1.0.0" --body "See CHANGELOG.md"

5. **Review and Merge**:

   - Verify all CI checks pass (tests, linting, documentation)
   - Review changes one final time
   - Merge to ``main`` branch

6. **Automatic Publication**:

   - Workflow triggers on merge to ``main``
   - Package builds, validates, and publishes to PyPI
   - GitHub release created with tag ``v1.0.0``
   - Users can install: ``pip install honeyhive==1.0.0``

**Pre-Release Checklist**:

Before creating the release PR, verify:

- [ ] Full test suite passes locally: ``tox -e unit && tox -e integration``
- [ ] Code quality checks pass: ``tox -e lint && tox -e format``
- [ ] Documentation builds without warnings: ``tox -e docs``
- [ ] Version number follows SemVer conventions
- [ ] ``CHANGELOG.md`` updated with all notable changes
- [ ] Breaking changes documented in migration guide
- [ ] All integration tests pass with real APIs

PyPI Publishing Workflow Details
--------------------------------

**Workflow Configuration**:

The ``sdk-publish.yml`` workflow includes multiple validation steps:

**Version Validation**:

.. code-block:: bash

   # Extract version from source
   version=$(python -c "exec(open('src/honeyhive/__init__.py').read()); print(__version__)")
   
   # Validate format (regex check)
   echo "$version" | grep -E '^[0-9]+\.[0-9]+\.[0-9]+(rc[0-9]+|alpha[0-9]+|beta[0-9]+)?$'

**PyPI Existence Check**:

.. code-block:: bash

   # Query PyPI API
   response=$(curl -s https://pypi.org/pypi/honeyhive/json)
   
   # Check if version exists in releases
   if echo "$response" | python -c "import sys, json; ..."; then
     echo "Version already published - skipping"
     exit 0
   fi

**Package Build and Verification**:

.. code-block:: bash

   # Build distribution packages
   python -m build
   
   # Verify package integrity
   python -m twine check dist/*
   
   # Test installation
   python -m venv test-install
   source test-install/bin/activate
   pip install dist/*.whl
   python -c "import honeyhive; print(honeyhive.__version__)"

**PyPI Publication**:

.. code-block:: bash

   # Publish using PYPI_TOKEN secret
   python -m twine upload dist/*

**GitHub Release Creation**:

.. code-block:: yaml

   - uses: actions/create-release@v1
     with:
       tag_name: v${{ steps.get_version.outputs.version }}
       release_name: v${{ steps.get_version.outputs.version }}
       prerelease: ${{ contains(version, 'rc') || contains(version, 'alpha') }}

**Required Secrets**:

The workflow requires the following GitHub repository secrets:

- ``PYPI_TOKEN``: PyPI API token with upload permissions for ``honeyhive`` package
- ``GITHUB_TOKEN``: Automatically provided by GitHub Actions

Integration with CI/CD Pipeline
-------------------------------

**Release Candidate Workflow**:

Before releasing to PyPI, use the release candidate workflow for comprehensive validation:

.. code-block:: bash

   # Manually trigger release candidate build
   gh workflow run release-candidate.yml \
     --field version_type=minor \
     --field pre_release=rc

The release candidate workflow (see :doc:`testing/ci-cd-integration`) executes:

1. Full test suite across Python 3.11, 3.12, 3.13
2. Integration tests with real APIs
3. Lambda compatibility tests
4. Package building and validation
5. Multi-Python installation testing

Release candidates are uploaded as workflow artifacts but not published to PyPI.

**Main Branch Protection**:

The ``main`` branch is protected and requires:

- All status checks must pass (tests, linting, documentation)
- At least one approval from code owners
- Branch must be up to date with base branch

This ensures only validated code triggers the release workflow.

Troubleshooting Release Issues
------------------------------

**Version Already Published**:

**Symptom**: Workflow shows "Version already published" message

**Cause**: Version string in ``__init__.py`` already exists on PyPI

**Solution**: Update ``__version__`` to a new version number and re-run

.. code-block:: bash

   # Check current PyPI versions
   pip index versions honeyhive
   
   # Update to new version
   __version__ = "1.0.1"  # Increment appropriately

**Build Failures**:

**Symptom**: Package build step fails

**Common Causes**:

- Syntax errors in Python code
- Missing dependencies in ``pyproject.toml``
- Import errors in ``__init__.py``

**Solution**:

.. code-block:: bash

   # Test build locally
   python -m build
   
   # If build fails, check for errors
   python -m pip install -e .
   python -c "import honeyhive"

**Publication Failures**:

**Symptom**: PyPI upload fails

**Common Causes**:

- Invalid or expired ``PYPI_TOKEN``
- Network connectivity issues
- PyPI service outage

**Solution**:

1. Verify ``PYPI_TOKEN`` secret is configured correctly
2. Check PyPI status: https://status.python.org/
3. Re-run workflow after resolving issues

**GitHub Release Not Created**:

**Symptom**: Package published to PyPI but no GitHub release

**Common Causes**:

- Insufficient GitHub Actions permissions
- ``GITHUB_TOKEN`` permission issues

**Solution**:

1. Verify workflow has ``contents: write`` permission
2. Manually create release if needed:

   .. code-block:: bash

      gh release create v1.0.0 \
        --title "v1.0.0" \
        --notes "See CHANGELOG.md for details"

**Version Mismatch**:

**Symptom**: Published package has different version than expected

**Cause**: ``__init__.py`` version doesn't match expected value

**Solution**:

.. code-block:: bash

   # Verify version in source
   python -c "exec(open('src/honeyhive/__init__.py').read()); print(__version__)"
   
   # Ensure this matches intended release version
   # If mismatch, update __init__.py and release again with correct version

Emergency Manual Release
------------------------

If the automated workflow fails and an emergency release is required:

**Manual Release Procedure**:

1. **Verify Version**:

   .. code-block:: bash

      python -c "exec(open('src/honeyhive/__init__.py').read()); print(__version__)"

2. **Build Package**:

   .. code-block:: bash

      python -m build

3. **Verify Package**:

   .. code-block:: bash

      twine check dist/*

4. **Test Installation**:

   .. code-block:: bash

      python -m venv test-env
      source test-env/bin/activate
      pip install dist/*.whl
      python -c "import honeyhive; print(honeyhive.__version__)"
      deactivate

5. **Publish to PyPI**:

   .. code-block:: bash

      # Set credentials
      export TWINE_USERNAME=__token__
      export TWINE_PASSWORD=<pypi-token>
      
      # Upload
      twine upload dist/*

6. **Create GitHub Release**:

   .. code-block:: bash

      git tag v1.0.0
      git push origin v1.0.0
      
      gh release create v1.0.0 \
        --title "v1.0.0" \
        --notes "See CHANGELOG.md for details"

**Post-Manual Release**:

After manual release, update the repository to trigger the automated workflow on the next release. Investigate why the automated workflow failed and fix the root cause.

Release Monitoring
------------------

**Post-Release Verification**:

After workflow completes, verify the release:

1. **Check PyPI**:

   .. code-block:: bash

      pip index versions honeyhive
      # Should show new version

2. **Test Installation**:

   .. code-block:: bash

      pip install honeyhive==1.0.0
      python -c "import honeyhive; print(honeyhive.__version__)"

3. **Verify GitHub Release**:

   .. code-block:: bash

      gh release view v1.0.0

4. **Check Documentation**:

   Verify documentation deployed: https://honeyhiveai.github.io/python-sdk/

**Release Metrics**:

Monitor the following metrics for release health:

- Workflow execution time (target: < 10 minutes)
- Package build success rate (target: 100%)
- PyPI publication success rate (target: 100%)
- GitHub release creation success rate (target: 100%)

Version History and Changelog
-----------------------------

**Changelog Maintenance**:

The ``CHANGELOG.md`` file tracks all notable changes:

.. code-block:: markdown

   # Changelog

   All notable changes to this project will be documented in this file.

   ## [Unreleased]

   ### Added
   - Features in development

   ## [1.0.0] - 2025-10-31

   ### Added
   - Initial stable release

**Changelog Format**:

Follow `Keep a Changelog <https://keepachangelog.com/>`_ format:

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements

**Version Links**:

Include comparison links at the bottom of ``CHANGELOG.md``:

.. code-block:: markdown

   [1.0.0]: https://github.com/honeyhiveai/python-sdk/compare/v0.1.0rc3...v1.0.0
   [Unreleased]: https://github.com/honeyhiveai/python-sdk/compare/v1.0.0...HEAD

Best Practices
--------------

**Release Timing**:

- **Stable releases**: Only from ``main`` branch
- **Pre-releases**: Use ``rc``, ``alpha``, or ``beta`` identifiers
- **Hotfixes**: Patch version increment with minimal changes

**Testing Before Release**:

Always run comprehensive tests before releasing:

.. code-block:: bash

   # Full local validation
   tox -e unit
   tox -e integration
   tox -e lint
   tox -e format
   tox -e docs
   
   # Multi-Python testing
   tox -e py311,py312,py313

**Documentation Updates**:

Ensure documentation is current before release:

- API reference matches implementation
- Migration guides updated for breaking changes
- Examples tested and working
- Changelog complete and accurate

**Communication**:

For major or breaking releases:

- Announce in community channels (Discord, Slack)
- Update documentation with migration guides
- Consider blog post for significant changes
- Notify users of deprecations in advance

See Also
--------

- :doc:`testing/ci-cd-integration` - CI/CD pipeline and GitHub Actions workflows
- :doc:`testing/setup-and-commands` - Development environment setup
- :doc:`../how-to/migration-compatibility/migration-guide` - User migration guides
- ``CHANGELOG.md`` - Complete version history
- ``.github/workflows/sdk-publish.yml`` - Release workflow implementation
- ``.github/workflows/release-candidate.yml`` - Release candidate validation

