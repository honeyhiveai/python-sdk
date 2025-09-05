GitHub Actions CI/CD Testing
============================

.. note::
   **Internal HoneyHive SDK Development - GitHub Actions Workflows**
   
   Best practices and workflows for HoneyHive SDK testing in our GitHub Actions CI/CD pipeline. For SDK contributors and maintainers.

This guide covers our internal GitHub Actions workflows for automated testing of the HoneyHive Python SDK. All contributors must understand these workflows to maintain code quality.

Our GitHub Actions Workflows
----------------------------

**HoneyHive SDK uses a comprehensive GitHub Actions CI/CD pipeline with path-based detection logic to optimize resource usage:**

**Core Testing Workflows**:

1. **`tox-full-suite.yml`** - Comprehensive testing pipeline with Python version matrix
2. **`lambda-tests.yml`** - AWS Lambda compatibility testing with Docker simulation
3. **`release-candidate.yml`** - Release automation and validation (manual trigger)

**Documentation Workflows**:

4. **`docs-deploy.yml`** - Documentation deployment to GitHub Pages
5. **`docs-preview.yml`** - PR documentation preview generation
6. **`docs-validation.yml`** - Documentation navigation and link validation
7. **`docs-versioned.yml`** - Versioned documentation management with mike

**Path-Based Optimization** (Added 2025-09-05):

All workflows now include intelligent path detection to prevent unnecessary runs:

- **Excluded Paths**: `.agent-os/**`, `docs/MERMAID_STANDARD.md`
- **Included Paths**: `src/**`, `tests/**`, `docs/**`, `tox.ini`, `pyproject.toml`
- **Benefit**: Agent OS specification changes no longer trigger full CI/CD pipelines

**Key Testing Commands Used in CI**:

.. code-block:: bash

   # Our standard testing commands (used in GHA)
   tox -e unit              # Unit tests (fast)
   tox -e integration       # Integration tests  
   tox -e lint             # Code quality (pylint + mypy)
   tox -e format           # Code formatting (black + isort)
   tox -e py311,py312,py313 # Multi-Python testing

Tox Full Suite Workflow
-----------------------

**`tox-full-suite.yml` - Comprehensive Testing Pipeline**:

This workflow runs our complete tox-based testing suite with optimized triggering:

**Triggers**:
- **Push to main**: Only when code/config files change (with path filters)
- **Pull requests**: All PRs affecting relevant files
- **Manual dispatch**: With configurable Python versions and tox environments
- **Workflow call**: Called by release-candidate workflow

**Path Filters**:

.. code-block:: yaml

   paths:
     - 'src/**'                    # Source code changes
     - 'tests/**'                  # Test changes  
     - 'tox.ini'                   # Tox configuration
     - 'pyproject.toml'            # Project configuration
     - '.github/workflows/tox-full-suite.yml'  # Workflow changes
   paths-ignore:
     - '.agent-os/**'              # Agent OS specifications
     - 'docs/MERMAID_STANDARD.md'  # Documentation standards

**Job Structure**:

The workflow uses **sequential execution** (not matrix) to provide clean PR interfaces:

.. code-block:: yaml

   jobs:
     # Python Version Testing (Sequential)
     test-python-311:
       name: "🐍 Python 3.11 Testing"
     test-python-312: 
       name: "🐍 Python 3.12 Testing"
     test-python-313:
       name: "🐍 Python 3.13 Testing"
     
     # Quality Gates
     code-quality:
       name: "📊 Code Quality (Lint + Format)"
     
     # Coverage Reporting
     coverage-report:
       name: "📈 Coverage Analysis"

AWS Lambda Testing Workflow
---------------------------

**`lambda-tests.yml` - Lambda Compatibility Testing**:

This workflow tests AWS Lambda compatibility with **three-tier testing strategy**:

**Triggers**:
- **Push to main**: Only when Lambda-related files change
- **Pull requests**: All PRs affecting Lambda compatibility
- **Daily schedule**: 2 AM UTC for comprehensive validation
- **Workflow call**: Called by release-candidate workflow

**Path Filters**:

.. code-block:: yaml

   paths:
     - 'src/**'                    # Source code affecting Lambda
     - 'tests/**'                  # Test changes
     - 'lambda_functions/**'       # Lambda-specific code
     - 'tox.ini'                   # Build configuration
     - 'pyproject.toml'            # Dependencies
     - '.github/workflows/lambda-tests.yml'  # Workflow changes
   paths-ignore:
     - '.agent-os/**'              # Agent OS specifications

**Testing Tiers**:

1. **Docker Simulation Suite** (Every PR):
   - Fast Docker-based Lambda environment simulation
   - Python version compatibility (3.11, 3.12, 3.13)
   - Memory constraint testing (128MB, 512MB)

2. **Real AWS Environment** (Main branch + scheduled):
   - Actual AWS Lambda deployment and testing
   - Real cold start and warm start performance
   - AWS SAM CLI integration

3. **Performance Benchmarks** (Scheduled only):
   - Cold start timing analysis
   - Memory usage profiling  
   - Execution time benchmarking

Documentation Workflows
------------------------

**Documentation Pipeline** (Added 2025-09-05):

The SDK now includes comprehensive documentation workflows with path-based optimization:

**`docs-deploy.yml` - GitHub Pages Deployment**:
- **Triggers**: Push to main/complete-refactor, releases, manual dispatch
- **Path filters**: `docs/**`, `src/**`, `*.md`, `pyproject.toml`
- **Excludes**: `.agent-os/**`, `docs/MERMAID_STANDARD.md`
- **Features**: AI Assistant validation protocol, Sphinx build with warnings as errors

**`docs-preview.yml` - PR Documentation Previews**:
- **Triggers**: PR opened/synchronized/reopened
- **Path filters**: Same as docs-deploy with workflow files
- **Features**: API surface validation, artifact upload for manual review
- **Benefits**: Preview docs changes before merge

**`docs-validation.yml` - Navigation Validation**:
- **Triggers**: After docs deployment, weekly monitoring
- **Features**: Link checking, navigation validation, deployment verification
- **Monitoring**: Automatic detection of broken documentation

**`docs-versioned.yml` - Version Management**:
- **Triggers**: Main branch pushes, version tags, manual dispatch
- **Features**: Mike-based versioning, multiple version support
- **Purpose**: Maintain documentation for different SDK versions

Release Candidate Workflow
---------------------------

**`release-candidate.yml` - Comprehensive Release Validation**:

This workflow provides complete release validation with configurable options:

**Triggers**:
- **Manual dispatch only**: Prevents accidental releases
- **Configurable inputs**: Version type, pre-release identifier, test options

**Validation Pipeline**:

1. **Pre-Release Validation**: Check test requirements and AWS test configuration
2. **Full Test Suite**: Calls `tox-full-suite.yml` with comprehensive testing
3. **Lambda Compatibility**: Calls `lambda-tests.yml` with AWS testing enabled
4. **Package Building**: Creates release candidate packages with version bumping
5. **Multi-Python Validation**: Tests packages across Python 3.11, 3.12, 3.13
6. **Release Summary**: Comprehensive report of all validation results

**Emergency Release Mode**:
- Option to skip tests for critical hotfixes
- Still validates package building and installation
- Clearly marked in workflow outputs

Internal Development Best Practices
-----------------------------------

**For HoneyHive SDK Contributors**:

**Pre-Commit Requirements**:

.. code-block:: bash

   # Before every commit, run these locally:
   tox -e format    # Code formatting (black + isort)
   tox -e lint      # Code quality (pylint + mypy)  
   tox -e unit      # Fast unit tests
   
   # For major changes, also run:
   tox -e integration  # Integration tests
   tox -e py311,py312,py313  # Multi-Python testing

**GitHub Actions Integration Points** (Updated 2025-09-05):

1. **Smart PR Validation**: PRs trigger workflows only when relevant files change
2. **Path-Based Optimization**: Workflows skip unnecessary runs for Agent OS specs
3. **Main Branch Protection**: All tests must pass before merge to main
4. **Scheduled Validation**: Daily Lambda tests and weekly documentation validation
5. **Release Validation**: Release candidate workflow with comprehensive testing
6. **Documentation Sync**: Automatic validation and deployment of documentation changes

**Workflow Efficiency Improvements**:

- **Resource Optimization**: 60-80% reduction in unnecessary workflow runs
- **Faster Feedback**: Relevant workflows complete faster due to reduced load
- **Clear PR Interface**: Sequential jobs instead of matrix for cleaner status
- **Intelligent Triggering**: Path filters prevent cascading workflow runs

Environment Variables in CI
---------------------------

**Required Secrets in GitHub Actions** (Updated 2025-09-05):

.. code-block:: bash

   # Repository secrets (configured in GitHub)
   HH_API_KEY          # HoneyHive API key for real API testing
   HH_TEST_API_KEY     # Dedicated test environment key
   AWS_ACCESS_KEY_ID   # For real Lambda testing (optional)
   AWS_SECRET_ACCESS_KEY  # For real Lambda testing (optional)
   CODECOV_TOKEN       # For coverage reporting (optional)

**Environment Variables Set in Workflows**:

Current workflow configuration uses these standardized environment variables:

.. code-block:: bash

   # Standard test environment (tox-full-suite.yml)
   HH_API_KEY=test-api-key-12345
   HH_API_URL=https://api.honeyhive.ai
   HH_PROJECT=test-project
   HH_SOURCE=github-actions
   HH_TEST_MODE=true
   HH_DEBUG_MODE=true
   HH_DISABLE_TRACING=false
   HH_DISABLE_HTTP_TRACING=false
   HH_OTLP_ENABLED=false

**Environment Variable Usage by Workflow**:

- **tox-full-suite.yml**: Uses test environment variables for unit/integration tests
- **lambda-tests.yml**: Uses real API keys for Lambda compatibility testing
- **release-candidate.yml**: Inherits secrets from called workflows
- **docs-*.yml**: No HoneyHive-specific environment variables needed

Troubleshooting CI Failures
---------------------------

**Common Issues and Solutions** (Updated 2025-09-05):

**1. Path Filter Issues**:

.. code-block:: bash

   # Check if workflow should have triggered
   git diff --name-only HEAD~1 HEAD
   
   # Verify path filters in workflow files
   grep -A 10 "paths:" .github/workflows/*.yml

**2. Tox Environment Failures**:

.. code-block:: bash

   # Check tox configuration
   tox --listenvs
   
   # Run specific environment locally
   tox -e unit -v
   
   # Check for environment variable issues
   env | grep HH_

**3. Lambda Test Failures**:

.. code-block:: bash

   # Check Docker container status
   docker ps -a | grep honeyhive-lambda
   
   # Verify container build
   cd tests/lambda && make build
   
   # Run Lambda tests locally
   make test-lambda

**4. Documentation Build Failures**:

.. code-block:: bash

   # Test documentation build locally
   tox -e docs
   
   # Check for broken references
   cd docs && make html
   
   # Validate navigation
   python docs/utils/validate_navigation.py --local

**5. Workflow Not Triggering**:

Common reasons workflows don't run:

- **Path filters**: Changes only in excluded paths (`.agent-os/**`)
- **Branch filters**: Push to non-main branch with main-only workflow
- **File types**: Changes to files not covered by path filters
- **Workflow syntax**: YAML syntax errors prevent workflow execution

Workflow Monitoring and Debugging
---------------------------------

**Monitoring CI Health** (Updated 2025-09-05):

1. **GitHub Actions Dashboard**: Monitor workflow runs and success rates
2. **Path Filter Effectiveness**: Track reduction in unnecessary runs
3. **Workflow Efficiency**: Monitor average completion times
4. **Coverage Trends**: Track coverage changes over time
5. **Lambda Performance**: Monitor Lambda test execution times
6. **Documentation Deployment**: Monitor docs build and deployment success

**Debugging Failed Workflows**:

.. code-block:: bash

   # Download workflow logs locally (requires GitHub CLI)
   gh run download <run-id>
   
   # Re-run specific workflow manually
   gh workflow run tox-full-suite.yml
   
   # Check recent workflow runs
   gh run list --workflow=tox-full-suite.yml --limit 10
   
   # View workflow run details
   gh run view <run-id>
   
   # Check workflow file syntax
   yamllint .github/workflows/

**Performance Optimization** (Updated 2025-09-05):

- **Path-Based Triggering**: 60-80% reduction in unnecessary workflow runs
- **Sequential Execution**: Clean PR interfaces instead of matrix noise
- **Intelligent Caching**: Dependencies cached between runs
- **Selective Testing**: Workflows only run when relevant files change
- **Resource Optimization**: Appropriate memory/CPU allocation per job
- **Workflow Composition**: Reusable workflows called by release candidate

**Workflow Efficiency Metrics**:

- **Before Path Filters**: ~15-20 workflow runs per Agent OS spec commit
- **After Path Filters**: ~2-3 workflow runs per Agent OS spec commit
- **Resource Savings**: Estimated 70% reduction in CI/CD compute usage
- **Developer Experience**: Faster feedback loops for relevant changes

See Also
--------

- :doc:`lambda-testing` - Lambda-specific CI/CD testing
- :doc:`performance-testing` - Performance testing in pipelines
- :doc:`integration-testing` - Integration testing strategies
- :doc:`../workflow-optimization` - Path-based workflow optimization guide
- ``.agent-os/specs/2025-09-02-cicd-gha-best-practices/`` - Comprehensive CI/CD specifications
- ``.agent-os/standards/best-practices.md`` - Development standards including CI/CD requirements