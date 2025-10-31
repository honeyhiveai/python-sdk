SDK Development
===============

.. note::
   **For HoneyHive SDK Contributors and Maintainers**
   
   This section contains documentation for developers working on the HoneyHive Python SDK itself, not for SDK users. If you're using the SDK in your applications, see the main :doc:`../how-to/index` guides.

This section covers internal development practices, testing strategies, and contribution guidelines for the HoneyHive Python SDK.

**Target Audience:**

- HoneyHive employees working on the SDK
- Open source contributors
- Maintainers and core developers
- Anyone making changes to the SDK codebase

Testing
-------

.. note::
   **For HoneyHive SDK Developers and Contributors**
   
   This guide covers testing practices for developing the HoneyHive Python SDK itself, not for testing applications that use the SDK.

This section provides comprehensive testing standards, practices, and tools used in HoneyHive Python SDK development. All contributors must follow these testing practices to maintain code quality and reliability.

**Current Test Status**:

- **Total Tests**: 2,904 tests (2,735 unit + 169 integration) - 100% success rate ✅
- **Test Coverage**: 94.13% (significantly above 80% requirement ✅)
- **Code Quality**: 10.0/10 Pylint score + 0 MyPy errors ✅
- **Test Types**: Unit, Integration, Lambda, Performance, CLI
- **CI/CD Integration**: GitHub Actions with automated quality gates

**Testing Strategy**:

The HoneyHive SDK employs a **three-tier testing strategy**:

1. **Unit Testing** - Fast, isolated tests with mocking (every commit)
2. **Integration Testing** - Real system tests with live APIs and no mocking (every PR)
3. **Lambda Testing** - AWS deployment and performance validation (daily/release)

.. toctree::
   :maxdepth: 1

   testing/setup-and-commands
   testing/unit-testing
   testing/integration-testing
   testing/integration-testing-strategy
   testing/lambda-testing
   testing/performance-testing
   testing/mocking-strategies
   testing/ci-cd-integration
   testing/troubleshooting-tests
   workflow-optimization

Release Process
---------------

This section covers the automated release and PyPI publishing workflow for SDK maintainers.

.. toctree::
   :maxdepth: 1

   release-process

AI-Assisted Development Infrastructure
--------------------------------------

This section covers the Agent OS MCP/RAG server—our evolution of the Builder Methods Agent OS system into an intelligent Model Context Protocol server with semantic search and phase-gated workflows.

.. toctree::
   :maxdepth: 1

   agent-os-mcp-server

Post-Mortems & Lessons Learned
------------------------------

This section contains detailed post-mortems of significant issues and bugs discovered during SDK development. These documents provide valuable insights into our development processes, testing strategies, and lessons learned.

.. toctree::
   :maxdepth: 1

   post-mortems/2025-09-05-proxy-tracer-provider-bug

**Quick Development Setup:**

.. code-block:: bash

   # Clone and setup development environment
   git clone https://github.com/honeyhiveai/python-sdk.git
   cd python-sdk
   ./scripts/setup-dev.sh
   
   # Run tests to verify setup
   tox -e unit
   tox -e integration

**Development Workflow:**

1. **Setup**: Use ``./scripts/setup-dev.sh`` for consistent environment
2. **Code Quality**: Pre-commit hooks enforce standards automatically
3. **Testing**: Use tox for all testing (never run pytest directly)
4. **Documentation**: Update docs for any API changes
5. **Changelog**: Update CHANGELOG.md for notable changes

**Key Development Principles:**

- **Test-Driven Development**: Write tests before implementing features
- **Type Safety**: Use mypy and maintain 100% type coverage
- **Documentation First**: Document APIs before implementation
- **Backward Compatibility**: Maintain compatibility when possible
- **Performance**: Consider impact on user applications

**Project Structure:**

.. code-block:: text

   python-sdk/
   ├── src/honeyhive/           # Main SDK code
   ├── tests/                   # All test code
   │   ├── unit/               # Fast unit tests
   │   ├── integration/        # Integration tests
   │   └── compatibility_matrix/ # Provider compatibility
   ├── docs/                   # Documentation source
   ├── scripts/               # Development scripts
   └── .agent-os/             # Agent OS standards

**Development Dependencies:**

The SDK uses several tools for development quality:

- **tox**: Test environment management
- **pytest**: Test framework with fixtures
- **black**: Code formatting (runs on save)
- **isort**: Import sorting
- **pylint**: Code quality analysis
- **mypy**: Static type checking
- **yamllint**: YAML file validation
- **pre-commit**: Git hook automation

**Architecture Standards:**

The SDK follows specific architectural patterns:

- **Multi-instance Support**: No global state, independent tracers
- **BYOI Architecture**: Bring Your Own Instrumentor for flexibility
- **OpenTelemetry Native**: Built on OTel standards
- **Graceful Degradation**: Never crash user applications
- **Decorator-First**: Emphasis on ``@trace`` over context managers

Getting Help
------------

**For SDK Development Questions:**

- **Internal Team**: Use HoneyHive development Slack channels
- **Architecture Decisions**: Check ``.agent-os/product/decisions.md``
- **Standards**: Reference ``.agent-os/standards/`` directory
- **Code Review**: Follow established PR review processes

**For External Contributors:**

- **GitHub Issues**: Report bugs or request features
- **GitHub Discussions**: Ask development questions
- **Discord Community**: Get community support
- **Email**: Contact the SDK team directly

**Release Process:**

The SDK uses automated PyPI publishing triggered by version updates in ``src/honeyhive/__init__.py``. The workflow validates versions against PyPI, builds packages, runs integrity checks, and publishes automatically on merge to ``main``. See :doc:`release-process` for complete release procedures and troubleshooting.

Contributing Guidelines
-----------------------

**Before Contributing:**

1. **Read Agent OS Standards**: Check ``.agent-os/standards/``
2. **Review Architecture**: Understand BYOI and multi-instance design
3. **Setup Environment**: Use ``./scripts/setup-dev.sh``
4. **Run Tests**: Ensure your environment works correctly

**Code Contribution Process:**

1. **Fork & Branch**: Create feature branch from ``main``
2. **Implement**: Follow existing patterns and standards
3. **Test**: Add comprehensive tests for new functionality
4. **Document**: Update docs and changelog
5. **PR**: Submit pull request with clear description

**Testing Requirements:**

- **Unit Test Coverage**: Minimum 60% for all new code
- **Integration Tests**: For any external service interactions
- **Type Checking**: Must pass mypy validation
- **Documentation**: All public APIs must be documented
- **Pre-commit**: All hooks must pass

**Review Criteria:**

Pull requests are evaluated on:

- **Functionality**: Does it solve the stated problem?
- **Code Quality**: Follows established patterns and standards
- **Testing**: Comprehensive test coverage
- **Documentation**: Clear docs and changelog updates
- **Performance**: No negative impact on SDK performance
- **Compatibility**: Maintains backward compatibility
