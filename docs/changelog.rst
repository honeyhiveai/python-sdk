Changelog
=========

.. note::
   **Release History and Updates**
   
   This changelog documents all notable changes to the HoneyHive Python SDK. For the complete, up-to-date changelog, see the `CHANGELOG.md file <https://github.com/honeyhiveai/python-sdk/blob/main/CHANGELOG.md>`_ in the repository.

.. important::
   **Format**: This project follows `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_ format and adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

Latest Release Notes
--------------------

**For the complete and always up-to-date changelog, see:** `CHANGELOG.md <https://github.com/honeyhiveai/python-sdk/blob/main/CHANGELOG.md>`_

Current Version Highlights
~~~~~~~~~~~~~~~~~~~~~~~~~~

**v0.1.0rc1 (2025-09-11) - Release Candidate with Performance Improvements**

**🚀 NEW: Performance Optimization Framework**

* **OTLP Performance Tuning**: Configurable batch sizes and flush intervals for production optimization
* **Environment Variables**: ``HH_BATCH_SIZE`` and ``HH_FLUSH_INTERVAL`` for fine-tuned performance control
* **Enhanced Span Processing**: Improved batching performance with configurable parameters
* **API Client Improvements**: Better error handling and configuration management
* **Documentation Navigation**: Comprehensive validation framework with 0 broken links across 69 URLs
* **Integration Testing**: Consolidated two-tier testing strategy with real API validation
* **RST Hierarchy**: Fixed documentation structure across all provider integration guides

**v0.1.0 (Development) - Major Architectural Refactor & Bug Fixes**

**🎯 NEW: Compatibility Matrix Framework (2025-09-05)**

* **Complete Testing Framework**: 13 provider compatibility tests with 100% success rate
* **Python Version Support**: Full validation across Python 3.11, 3.12, and 3.13
* **Dynamic Generation**: Automated maintenance reducing manual work by 75%
* **Official Documentation**: Integrated compatibility matrix in Sphinx docs with optimal UX
* **Systematic Workarounds**: Professional handling of upstream instrumentor bugs
* **Streamlined Architecture**: 25% file count reduction with consolidated documentation

This release represents a comprehensive modernization of the HoneyHive Python SDK with significant architectural improvements and enhanced developer experience.

**🔄 Breaking Changes**

- **Modernized Architecture**: ``HoneyHiveTracer`` now supports multiple independent instances
  
  - ``HoneyHiveTracer.init()`` method maintained for backwards compatibility
  - Direct constructor usage also available: ``HoneyHiveTracer(api_key="key")``
  - Each initialization creates a new independent tracer instance

**✨ Major Additions**

- **Examples Directory Restructure**: Organized provider examples into dedicated integrations/ subdirectory with 39% size reduction, improved navigation, and focused approach eliminating external dependencies

- **CSS-Based Dual-Theme System**: Automatic light/dark theme detection for Mermaid sequence diagrams with targeted styling for optimal readability across all browsers

- **Documentation Quality Prevention System**: Comprehensive error prevention and validation framework
  
  - Zero Build Warnings: Documentation now builds cleanly without any Sphinx warnings  
  - Automated RST Validation: Pre-commit hooks validate structure and formatting
  - Type Safety Enforcement: All code examples use proper ``EventType`` enums
  - Code Example Testing: Automated validation ensures correct syntax and imports

- **Documentation Content Improvements**: Major cleanup and standardization
  
  - Divio Architecture Compliance: Complete reorganization following Divio documentation system
  - Decorator-First Approach: Updated examples to emphasize ``@trace`` decorators
  - Type-Safe Examples: Replaced string literals with ``EventType`` enums
  - Backward Compatibility Documentation: Comprehensive guide for tracer auto-discovery

- **Automatic Tracer Discovery**: Enhanced decorator functionality
  
  - ``@trace`` decorator now works without explicit tracer parameter
  - OpenTelemetry baggage-based tracer discovery mechanism
  - ``set_default_tracer()`` function for global tracer configuration
  - Maintains backward compatibility with existing code

- **Enhanced Decorator Support**: Improved tracing capabilities
  
  - ``@trace_class`` decorator for automatic class-level tracing
  - ``enrich_span()`` utility function for adding context to active spans
  - Unified decorator behavior for both sync and async functions
  - Better error handling and span lifecycle management

**🔧 Improvements**

- **Testing Infrastructure**: Comprehensive test coverage improvements
  
  - Unit tests for registry and tracer discovery mechanisms
  - Integration tests for backward compatibility scenarios  
  - Performance testing for multi-instance scenarios
  - Mocking strategies for reliable test isolation

- **Developer Experience**: Enhanced tooling and workflows
  
  - Pre-commit hooks for code quality and documentation validation
  - Strict changelog enforcement for high-frequency development environments
  - Feature synchronization verification
  - Enhanced error messages and debugging information

**🐛 Fixes**

- **API Endpoint Corrections**: Fixed incorrect health check endpoints
- **Documentation Warnings**: Resolved 23+ Sphinx build warnings
- **Import Issues**: Fixed pylint ungrouped-imports warnings
- **Cross-Reference Links**: Corrected broken internal documentation links

.. note::
   **Staying Updated**
   
   - **GitHub Releases**: Watch the `releases page <https://github.com/honeyhiveai/python-sdk/releases>`_ for notifications
   - **PyPI Updates**: Monitor `honeyhive on PyPI <https://pypi.org/project/honeyhive/>`_ for new versions
   - **Breaking Changes**: Major version bumps indicate breaking changes - review the changelog carefully before upgrading

Version Upgrade Guide
---------------------

**Upgrading to Latest Version**

.. code-block:: bash

   # Upgrade to latest version
   pip install --upgrade honeyhive
   
   # Or specify a specific version
   pip install honeyhive==X.Y.Z

**Breaking Changes Checklist**

When upgrading across major versions, review:

1. **API Changes**: Check for deprecated or removed methods
2. **Configuration Changes**: Verify environment variable names and formats
3. **Dependency Updates**: Update any instrumentor packages if needed
4. **Import Changes**: Update import statements if package structure changed
5. **Behavior Changes**: Test critical paths for any behavioral differences

**Migration Support**

If you need help migrating between versions:

- **Migration Guides**: Check the :doc:`how-to/index` section for version-specific migration guides
- **GitHub Discussions**: Ask questions in `GitHub Discussions <https://github.com/honeyhiveai/python-sdk/discussions>`_
- **Discord Community**: Get help in our `Discord server <https://discord.gg/honeyhive>`_
- **Support Email**: Contact support@honeyhive.ai for enterprise migration assistance

Contributing to the Changelog
------------------------------

**For Contributors**

When submitting pull requests, update the "Unreleased" section in `CHANGELOG.md`:

.. code-block:: markdown

   ## [Unreleased]
   
   ### Added
   - New feature description
   
   ### Changed
   - Changed behavior description
   
   ### Deprecated
   - Deprecated feature notice
   
   ### Removed
   - Removed feature description
   
   ### Fixed
   - Bug fix description
   
   ### Security
   - Security improvement description

**Change Categories**

- **Added**: New features
- **Changed**: Changes in existing functionality  
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements

**Writing Good Changelog Entries**

- **Be specific**: "Fixed trace span duration calculation" vs "Fixed bug"
- **Include impact**: "Breaking Change: Removed deprecated `trace_event()` method"
- **Add context**: "Improved performance by 40% for large trace batches"
- **Reference issues**: "Fixed #123: Memory leak in async tracing"

Release Process
---------------

**For Maintainers**

The release process follows these steps:

1. **Update Version**: Bump version in `pyproject.toml`
2. **Update Changelog**: Move "Unreleased" items to new version section
3. **Create Release**: Tag and create GitHub release
4. **Publish Package**: Automated publishing to PyPI
5. **Update Documentation**: Deploy updated docs with new version

**Release Schedule**

- **Major Releases**: Quarterly (breaking changes, major features)
- **Minor Releases**: Monthly (new features, improvements)
- **Patch Releases**: As needed (bug fixes, security updates)
- **Pre-releases**: Beta versions for testing major changes

**Version Numbering**

Following Semantic Versioning:

- **Major**: Breaking changes (1.0.0 → 2.0.0)
- **Minor**: New features, backwards compatible (1.0.0 → 1.1.0)  
- **Patch**: Bug fixes, backwards compatible (1.0.0 → 1.0.1)
- **Pre-release**: Beta versions (1.1.0-beta.1)
