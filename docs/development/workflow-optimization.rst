Workflow Path Detection Optimization
====================================

Overview
--------

This document describes the path-based detection logic implemented in GitHub Actions workflows to prevent unnecessary CI/CD runs when only Agent OS specifications or documentation standards are changed.

Problem Statement
-----------------

Previously, workflows would run full test suites and documentation builds even when commits only contained:

- Agent OS specification changes in ``.agent-os/``
- Documentation standard updates like ``docs/MERMAID_STANDARD.md``
- Planning documents that don't affect the actual codebase

This resulted in:

- Wasted CI/CD resources
- Longer feedback cycles
- Unnecessary workflow noise

Solution Implementation
-----------------------

Path-Based Exclusions
~~~~~~~~~~~~~~~~~~~~~

All major workflows now include ``paths-ignore`` filters to exclude:

- ``.agent-os/**`` - Agent OS specifications and planning documents
- ``docs/MERMAID_STANDARD.md`` - Documentation standards that don't affect builds

Affected Workflows
~~~~~~~~~~~~~~~~~~

The following workflows have been updated with path detection:

**tox-full-suite.yml**
  - Excludes Agent OS specs from triggering full test runs
  - Maintains coverage for actual code changes in ``src/`` and ``tests/``

**docs-deploy.yml**
  - Prevents documentation deployment for spec-only changes
  - Still triggers for actual documentation content changes

**docs-preview.yml**
  - Avoids building preview artifacts for non-content changes
  - Focuses on changes that affect user-facing documentation

**docs-validation.yml**
  - Skips validation when no actual documentation changes occur
  - Reduces cascading workflow runs

**lambda-tests.yml**
  - Added comprehensive path filters for Lambda-related changes
  - Prevents Lambda compatibility tests for unrelated changes

Workflow Trigger Logic
----------------------

Each workflow now follows this pattern:

.. code-block:: yaml

   on:
     push:
       branches: [main]
       paths:
         - 'src/**'           # Source code changes
         - 'tests/**'         # Test changes
         - 'docs/**'          # Documentation changes
         - 'tox.ini'          # Build configuration
         - 'pyproject.toml'   # Project configuration
       paths-ignore:
         - '.agent-os/**'     # Agent OS specifications
         - 'docs/MERMAID_STANDARD.md'  # Documentation standards

Benefits
--------

**Resource Efficiency**
  - Reduces unnecessary compute usage
  - Faster feedback for actual code changes
  - Lower CI/CD costs

**Developer Experience**
  - Cleaner workflow status in PRs
  - Faster completion times for relevant changes
  - Less noise in workflow notifications

**Maintenance**
  - Clear separation between planning and implementation
  - Easier to identify when workflows should run
  - Reduced false positives in CI/CD monitoring

Testing the Detection Logic
---------------------------

To verify the path detection works correctly:

1. **Agent OS Spec Changes Only**:
   
   .. code-block:: bash
   
      # Create a commit with only Agent OS changes
      git add .agent-os/
      git commit -m "docs: update agent os specifications"
      
      # Verify workflows don't trigger unnecessarily

2. **Documentation Standards Only**:
   
   .. code-block:: bash
   
      # Update documentation standards
      git add docs/MERMAID_STANDARD.md
      git commit -m "docs: update mermaid standards"
      
      # Verify docs workflows don't trigger

3. **Mixed Changes**:
   
   .. code-block:: bash
   
      # Mix of spec and code changes
      git add .agent-os/ src/honeyhive/
      git commit -m "feat: add feature with specs"
      
      # Verify workflows trigger for code changes

Maintenance Notes
-----------------

When adding new workflow files:

1. **Always include path filters** for relevant file types
2. **Add paths-ignore** for ``.agent-os/**`` and documentation standards
3. **Test the filters** with sample commits before merging
4. **Update this documentation** when adding new exclusion patterns

Future Enhancements
-------------------

Potential improvements to consider:

- **Conditional job execution** within workflows based on changed files
- **Dynamic test selection** based on which modules changed
- **Artifact caching** to speed up workflows when they do run
- **Workflow dependency optimization** to reduce cascading runs

Related Documentation
---------------------

- :doc:`testing/ci-cd-integration` - Comprehensive CI/CD patterns
- ``.agent-os/specs/2025-09-02-cicd-gha-best-practices/`` - Detailed CI/CD specifications
- ``.agent-os/product/decisions.md`` - Architecture decisions including path-based triggers
