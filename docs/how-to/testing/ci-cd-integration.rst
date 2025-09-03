CI/CD Integration Testing
=========================

.. note::
   **Problem-solving guide for integrating HoneyHive testing into CI/CD pipelines**
   
   Practical solutions for automating HoneyHive SDK testing in continuous integration and deployment workflows.

Integrating testing into CI/CD pipelines ensures consistent quality and catches issues before they reach production.

Quick Start
-----------

**Problem**: I need to add HoneyHive SDK testing to my CI/CD pipeline quickly.

**Solution**:

.. code-block:: yaml

   # .github/workflows/test.yml
   name: HoneyHive SDK Tests
   
   on: [push, pull_request]
   
   jobs:
     test:
       runs-on: ubuntu-latest
       
       steps:
       - uses: actions/checkout@v4
       - uses: actions/setup-python@v4
         with:
           python-version: '3.11'
       
       - name: Install dependencies
         run: |
           pip install -e .
           pip install pytest pytest-cov
       
       - name: Run HoneyHive SDK tests
         env:
           HH_API_KEY: ${{ secrets.HH_TEST_API_KEY }}
           HH_TEST_MODE: "true"
         run: |
           pytest tests/ \
             --cov=honeyhive \
             --cov-fail-under=70 \
             -v

GitHub Actions Integration
--------------------------

**Problem**: Set up comprehensive GitHub Actions workflow for HoneyHive testing.

**Solution - Complete GitHub Actions Workflow**:

.. code-block:: yaml

   # .github/workflows/honeyhive-tests.yml
   name: HoneyHive SDK Testing Suite
   
   on:
     push:
       branches: [ main, develop ]
     pull_request:
       branches: [ main ]
     schedule:
       - cron: '0 2 * * *'  # Daily at 2 AM UTC
   
   env:
     HH_TEST_MODE: "true"
     HH_PROJECT: "ci-test-project"
     HH_SOURCE: "github-actions"
   
   jobs:
     # Unit and Integration Tests
     test-matrix:
       name: Test Python ${{ matrix.python-version }}
       runs-on: ubuntu-latest
       strategy:
         matrix:
           python-version: ['3.11', '3.12', '3.13']
       
       steps:
       - name: Checkout code
         uses: actions/checkout@v4
       
       - name: Set up Python ${{ matrix.python-version }}
         uses: actions/setup-python@v4
         with:
           python-version: ${{ matrix.python-version }}
       
       - name: Cache dependencies
         uses: actions/cache@v3
         with:
           path: ~/.cache/pip
           key: ${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml') }}
           restore-keys: |
             ${{ runner.os }}-pip-
       
       - name: Install dependencies
         run: |
           python -m pip install --upgrade pip
           pip install tox tox-gh-actions
       
       - name: Run tests with tox
         env:
           HH_API_KEY: ${{ secrets.HH_TEST_API_KEY }}
         run: tox
       
       - name: Upload coverage to Codecov
         if: matrix.python-version == '3.11'
         uses: codecov/codecov-action@v4
         with:
           file: ./coverage.xml
           flags: unittests
           name: codecov-umbrella
   
     # Lambda Testing
     lambda-tests:
       name: Lambda Tests (Memory ${{ matrix.memory }}MB)
       runs-on: ubuntu-latest
       strategy:
         matrix:
           memory: [256, 512, 1024]
       
       steps:
       - name: Checkout code
         uses: actions/checkout@v4
       
       - name: Set up Python
         uses: actions/setup-python@v4
         with:
           python-version: '3.11'
       
       - name: Install Docker Compose
         run: |
           sudo apt-get update
           sudo apt-get install docker-compose
       
       - name: Build Lambda test containers
         run: |
           cd tests/lambda
           make build
       
       - name: Run Lambda compatibility tests
         env:
           HH_API_KEY: ${{ secrets.HH_TEST_API_KEY }}
           AWS_LAMBDA_FUNCTION_MEMORY_SIZE: ${{ matrix.memory }}
         run: |
           cd tests/lambda
           make test-lambda
       
       - name: Run Lambda performance tests
         env:
           HH_API_KEY: ${{ secrets.HH_TEST_API_KEY }}
           AWS_LAMBDA_FUNCTION_MEMORY_SIZE: ${{ matrix.memory }}
         run: |
           cd tests/lambda
           make test-performance
       
       - name: Upload Lambda performance results
         uses: actions/upload-artifact@v4
         with:
           name: lambda-performance-${{ matrix.memory }}mb
           path: tests/lambda/performance-results.json
   
     # Performance Regression Testing
     performance-check:
       name: Performance Regression Check
       runs-on: ubuntu-latest
       needs: [test-matrix]
       
       steps:
       - name: Checkout code
         uses: actions/checkout@v4
       
       - name: Set up Python
         uses: actions/setup-python@v4
         with:
           python-version: '3.11'
       
       - name: Install dependencies
         run: |
           pip install -e .
           pip install pytest pytest-benchmark
       
       - name: Run performance benchmarks
         env:
           HH_API_KEY: ${{ secrets.HH_TEST_API_KEY }}
         run: |
           pytest tests/performance/ \
             --benchmark-json=benchmark-results.json \
             --benchmark-compare-fail=min:5% \
             --benchmark-compare-fail=max:20%
       
       - name: Upload benchmark results
         uses: actions/upload-artifact@v4
         with:
           name: benchmark-results
           path: benchmark-results.json
   
     # Security Testing
     security-scan:
       name: Security Scan
       runs-on: ubuntu-latest
       
       steps:
       - name: Checkout code
         uses: actions/checkout@v4
       
       - name: Run Bandit security scan
         run: |
           pip install bandit[toml]
           bandit -r src/ -f json -o bandit-results.json
       
       - name: Upload security scan results
         uses: actions/upload-artifact@v4
         with:
           name: security-scan-results
           path: bandit-results.json
   
     # Code Quality Gates
     quality-gates:
       name: Quality Gates
       runs-on: ubuntu-latest
       needs: [test-matrix, lambda-tests, performance-check]
       
       steps:
       - name: Download test artifacts
         uses: actions/download-artifact@v4
         with:
           pattern: '*'
           merge-multiple: true
       
       - name: Check coverage threshold
         run: |
           # Extract coverage from artifacts and check threshold
           python scripts/check-coverage-threshold.py coverage.xml 70
       
       - name: Check performance regression
         run: |
           # Check if performance regression exceeds threshold
           python scripts/check-performance-regression.py benchmark-results.json 20
       
       - name: Generate test report
         run: |
           python scripts/generate-test-report.py \
             --coverage coverage.xml \
             --performance benchmark-results.json \
             --lambda-results tests/lambda/performance-results.json \
             --output test-report.html
       
       - name: Upload test report
         uses: actions/upload-artifact@v4
         with:
           name: test-report
           path: test-report.html

**Advanced GitHub Actions Features**:

.. code-block:: yaml

   # Advanced features for GitHub Actions
   
   # Conditional job execution
   integration-tests:
     if: github.event_name == 'push' || github.event.pull_request.draft == false
     
   # Parallel job execution with dependencies
   deploy-staging:
     needs: [test-matrix, lambda-tests, quality-gates]
     if: github.ref == 'refs/heads/develop'
     
   # Environment-specific testing
   test-environments:
     strategy:
       matrix:
         environment: [development, staging, production]
     env:
       HH_ENVIRONMENT: ${{ matrix.environment }}
       HH_API_KEY: ${{ secrets[format('HH_{0}_API_KEY', matrix.environment)] }}
     
   # Workflow dispatch for manual testing
   manual-testing:
     if: github.event_name == 'workflow_dispatch'
     steps:
     - name: Run extended test suite
       run: |
         pytest tests/ \
           --runslow \
           --run-integration \
           --run-performance \
           -v

GitLab CI Integration
---------------------

**Problem**: Set up GitLab CI pipeline for HoneyHive testing.

**Solution - GitLab CI Configuration**:

.. code-block:: yaml

   # .gitlab-ci.yml
   stages:
     - test
     - performance
     - security
     - quality-gates
   
   variables:
     HH_TEST_MODE: "true"
     HH_PROJECT: "gitlab-ci-test"
     HH_SOURCE: "gitlab-ci"
     PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"
   
   cache:
     paths:
       - .cache/pip
       - .tox/
   
   # Unit and Integration Tests
   test:unit:
     stage: test
     image: python:3.11
     parallel:
       matrix:
         - PYTHON_VERSION: ["3.11", "3.12", "3.13"]
     script:
       - pip install tox
       - tox -e py${PYTHON_VERSION//./}
     coverage: '/TOTAL\s+\d+\s+\d+\s+(\d+%)/'
     artifacts:
       reports:
         coverage_report:
           coverage_format: cobertura
           path: coverage.xml
       paths:
         - htmlcov/
       expire_in: 1 week
   
   test:integration:
     stage: test
     image: python:3.11
     services:
       - docker:dind
     variables:
       DOCKER_DRIVER: overlay2
       DOCKER_TLS_CERTDIR: ""
     script:
       - pip install tox docker
       - tox -e integration
     artifacts:
       paths:
         - integration-test-results.xml
       expire_in: 1 week
   
   # Lambda Testing
   test:lambda:
     stage: test
     image: docker:latest
     services:
       - docker:dind
     parallel:
       matrix:
         - MEMORY_SIZE: [256, 512, 1024]
     script:
       - cd tests/lambda
       - make build
       - AWS_LAMBDA_FUNCTION_MEMORY_SIZE=$MEMORY_SIZE make test-lambda
       - AWS_LAMBDA_FUNCTION_MEMORY_SIZE=$MEMORY_SIZE make test-performance
     artifacts:
       paths:
         - tests/lambda/performance-results-${MEMORY_SIZE}mb.json
       expire_in: 1 week
   
   # Performance Testing
   performance:benchmarks:
     stage: performance
     image: python:3.11
     script:
       - pip install -e .
       - pip install pytest pytest-benchmark
       - pytest tests/performance/ --benchmark-json=benchmark-results.json
     artifacts:
       paths:
         - benchmark-results.json
       expire_in: 1 week
   
   performance:regression:
     stage: performance
     image: python:3.11
     script:
       - python scripts/check-performance-regression.py benchmark-results.json
     dependencies:
       - performance:benchmarks
     allow_failure: true
   
   # Security Scanning
   security:bandit:
     stage: security
     image: python:3.11
     script:
       - pip install bandit[toml]
       - bandit -r src/ -f json -o bandit-results.json
     artifacts:
       paths:
         - bandit-results.json
       expire_in: 1 week
   
   security:safety:
     stage: security
     image: python:3.11
     script:
       - pip install safety
       - safety check --json --output safety-results.json
     artifacts:
       paths:
         - safety-results.json
       expire_in: 1 week
   
   # Quality Gates
   quality:coverage:
     stage: quality-gates
     image: python:3.11
     script:
       - python scripts/check-coverage-threshold.py coverage.xml 70
     dependencies:
       - test:unit
   
   quality:report:
     stage: quality-gates
     image: python:3.11
     script:
       - python scripts/generate-quality-report.py
     dependencies:
       - test:unit
       - test:integration
       - test:lambda
       - performance:benchmarks
       - security:bandit
       - security:safety
     artifacts:
       paths:
         - quality-report.html
       expire_in: 1 month

Jenkins Pipeline Integration
----------------------------

**Problem**: Set up Jenkins pipeline for HoneyHive testing.

**Solution - Jenkins Pipeline**:

.. code-block:: groovy

   // Jenkinsfile
   pipeline {
       agent any
       
       environment {
           HH_TEST_MODE = 'true'
           HH_PROJECT = 'jenkins-ci-test'
           HH_SOURCE = 'jenkins'
           HH_API_KEY = credentials('honeyhive-test-api-key')
       }
       
       options {
           timeout(time: 1, unit: 'HOURS')
           retry(2)
           parallelsAlwaysFailFast()
       }
       
       stages {
           stage('Setup') {
               steps {
                   script {
                       // Set up Python environment
                       sh '''
                           python -m venv venv
                           . venv/bin/activate
                           pip install --upgrade pip
                           pip install tox pytest
                       '''
                   }
               }
           }
           
           stage('Test Matrix') {
               parallel {
                   stage('Python 3.11') {
                       steps {
                           script {
                               sh '''
                                   . venv/bin/activate
                                   tox -e py311
                               '''
                           }
                       }
                       post {
                           always {
                               publishTestResults testResultsPattern: 'test-results-py311.xml'
                           }
                       }
                   }
                   
                   stage('Python 3.12') {
                       steps {
                           script {
                               sh '''
                                   . venv/bin/activate
                                   tox -e py312
                               '''
                           }
                       }
                       post {
                           always {
                               publishTestResults testResultsPattern: 'test-results-py312.xml'
                           }
                       }
                   }
                   
                   stage('Python 3.13') {
                       steps {
                           script {
                               sh '''
                                   . venv/bin/activate
                                   tox -e py313
                               '''
                           }
                       }
                       post {
                           always {
                               publishTestResults testResultsPattern: 'test-results-py313.xml'
                           }
                       }
                   }
               }
           }
           
           stage('Integration Tests') {
               when {
                   anyOf {
                       branch 'main'
                       branch 'develop'
                       changeRequest()
                   }
               }
               steps {
                   script {
                       sh '''
                           . venv/bin/activate
                           tox -e integration
                       '''
                   }
               }
               post {
                   always {
                       publishTestResults testResultsPattern: 'integration-test-results.xml'
                   }
               }
           }
           
           stage('Lambda Tests') {
               when {
                   anyOf {
                       branch 'main'
                       expression { env.CHANGE_TARGET == 'main' }
                   }
               }
               parallel {
                   stage('Lambda 256MB') {
                       steps {
                           script {
                               sh '''
                                   cd tests/lambda
                                   AWS_LAMBDA_FUNCTION_MEMORY_SIZE=256 make test-lambda
                               '''
                           }
                       }
                   }
                   
                   stage('Lambda 512MB') {
                       steps {
                           script {
                               sh '''
                                   cd tests/lambda
                                   AWS_LAMBDA_FUNCTION_MEMORY_SIZE=512 make test-lambda
                               '''
                           }
                       }
                   }
                   
                   stage('Lambda 1024MB') {
                       steps {
                           script {
                               sh '''
                                   cd tests/lambda
                                   AWS_LAMBDA_FUNCTION_MEMORY_SIZE=1024 make test-lambda
                               '''
                           }
                       }
                   }
               }
           }
           
           stage('Performance Tests') {
               steps {
                   script {
                       sh '''
                           . venv/bin/activate
                           pytest tests/performance/ \
                               --benchmark-json=benchmark-results.json \
                               --benchmark-compare-fail=min:5% \
                               --benchmark-compare-fail=max:20%
                       '''
                   }
               }
               post {
                   always {
                       archiveArtifacts artifacts: 'benchmark-results.json'
                   }
               }
           }
           
           stage('Quality Gates') {
               parallel {
                   stage('Coverage Check') {
                       steps {
                           script {
                               sh '''
                                   . venv/bin/activate
                                   python scripts/check-coverage-threshold.py coverage.xml 70
                               '''
                           }
                       }
                   }
                   
                   stage('Security Scan') {
                       steps {
                           script {
                               sh '''
                                   . venv/bin/activate
                                   pip install bandit safety
                                   bandit -r src/ -f json -o bandit-results.json
                                   safety check --json --output safety-results.json
                               '''
                           }
                       }
                       post {
                           always {
                               archiveArtifacts artifacts: 'bandit-results.json,safety-results.json'
                           }
                       }
                   }
               }
           }
       }
       
       post {
           always {
               publishCoverage adapters: [
                   coberturaAdapter('coverage.xml')
               ]
               
               archiveArtifacts artifacts: '''
                   htmlcov/**,
                   test-results-*.xml,
                   coverage.xml,
                   benchmark-results.json
               '''
           }
           
           success {
               emailext (
                   subject: "HoneyHive SDK Tests Passed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                   body: "All tests passed successfully.",
                   to: "${env.CHANGE_AUTHOR_EMAIL}"
               )
           }
           
           failure {
               emailext (
                   subject: "HoneyHive SDK Tests Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                   body: "Tests failed. Please check the build logs.",
                   to: "${env.CHANGE_AUTHOR_EMAIL}"
               )
           }
       }
   }

Azure DevOps Integration
------------------------

**Problem**: Set up Azure DevOps pipeline for HoneyHive testing.

**Solution - Azure Pipeline**:

.. code-block:: yaml

   # azure-pipelines.yml
   trigger:
     branches:
       include:
         - main
         - develop
     paths:
       exclude:
         - docs/*
         - README.md
   
   pr:
     branches:
       include:
         - main
         - develop
   
   variables:
     HH_TEST_MODE: 'true'
     HH_PROJECT: 'azure-devops-test'
     HH_SOURCE: 'azure-devops'
   
   stages:
   - stage: Test
     displayName: 'Test Stage'
     jobs:
     - job: TestMatrix
       displayName: 'Test Matrix'
       strategy:
         matrix:
           Python311:
             pythonVersion: '3.11'
           Python312:
             pythonVersion: '3.12'
           Python313:
             pythonVersion: '3.13'
       
       pool:
         vmImage: 'ubuntu-latest'
       
       steps:
       - task: UsePythonVersion@0
         inputs:
           versionSpec: '$(pythonVersion)'
         displayName: 'Use Python $(pythonVersion)'
       
       - script: |
           python -m pip install --upgrade pip
           pip install tox
         displayName: 'Install dependencies'
       
       - script: |
           tox -e py$(echo $(pythonVersion) | tr -d '.')
         env:
           HH_API_KEY: $(HH_TEST_API_KEY)
         displayName: 'Run tests'
       
       - task: PublishTestResults@2
         inputs:
           testResultsFiles: 'test-results.xml'
           testRunTitle: 'Python $(pythonVersion) Tests'
         condition: succeededOrFailed()
       
       - task: PublishCodeCoverageResults@1
         inputs:
           codeCoverageTool: 'cobertura'
           summaryFileLocation: 'coverage.xml'
           reportDirectory: 'htmlcov'
         condition: succeededOrFailed()
   
   - stage: Integration
     displayName: 'Integration Tests'
     dependsOn: Test
     condition: succeeded()
     jobs:
     - job: IntegrationTests
       displayName: 'Integration Tests'
       pool:
         vmImage: 'ubuntu-latest'
       
       steps:
       - task: UsePythonVersion@0
         inputs:
           versionSpec: '3.11'
       
       - script: |
           pip install tox docker
           tox -e integration
         env:
           HH_API_KEY: $(HH_TEST_API_KEY)
         displayName: 'Run integration tests'
   
   - stage: Lambda
     displayName: 'Lambda Tests'
     dependsOn: Test
     condition: succeeded()
     jobs:
     - job: LambdaTests
       displayName: 'Lambda Tests'
       strategy:
         matrix:
           Memory256:
             memorySize: '256'
           Memory512:
             memorySize: '512'
           Memory1024:
             memorySize: '1024'
       
       pool:
         vmImage: 'ubuntu-latest'
       
       steps:
       - script: |
           cd tests/lambda
           make build
           AWS_LAMBDA_FUNCTION_MEMORY_SIZE=$(memorySize) make test-lambda
         env:
           HH_API_KEY: $(HH_TEST_API_KEY)
         displayName: 'Run Lambda tests'
       
       - task: PublishBuildArtifacts@1
         inputs:
           pathToPublish: 'tests/lambda/performance-results.json'
           artifactName: 'lambda-performance-$(memorySize)mb'

Environment-Specific Testing
----------------------------

**Problem**: Test HoneyHive SDK across different environments.

**Solution - Environment Matrix Testing**:

.. code-block:: yaml

   # Environment-specific testing configuration
   name: Environment Testing
   
   on:
     push:
       branches: [ main ]
     schedule:
       - cron: '0 */6 * * *'  # Every 6 hours
   
   jobs:
     environment-tests:
       name: Test ${{ matrix.environment }}
       runs-on: ubuntu-latest
       strategy:
         matrix:
           environment:
             - development
             - staging
             - production
         fail-fast: false
       
       env:
         HH_ENVIRONMENT: ${{ matrix.environment }}
         HH_PROJECT: ci-${{ matrix.environment }}-test
         HH_SOURCE: github-actions-${{ matrix.environment }}
       
       steps:
       - uses: actions/checkout@v4
       - uses: actions/setup-python@v4
         with:
           python-version: '3.11'
       
       - name: Configure environment
         run: |
           case "${{ matrix.environment }}" in
             development)
               echo "HH_TEST_MODE=true" >> $GITHUB_ENV
               echo "HH_BASE_URL=https://api-dev.honeyhive.ai" >> $GITHUB_ENV
               ;;
             staging)
               echo "HH_TEST_MODE=false" >> $GITHUB_ENV
               echo "HH_BASE_URL=https://api-staging.honeyhive.ai" >> $GITHUB_ENV
               ;;
             production)
               echo "HH_TEST_MODE=false" >> $GITHUB_ENV
               echo "HH_BASE_URL=https://api.honeyhive.ai" >> $GITHUB_ENV
               ;;
           esac
       
       - name: Run environment-specific tests
         env:
           HH_API_KEY: ${{ secrets[format('HH_{0}_API_KEY', matrix.environment)] }}
         run: |
           pip install -e .
           pytest tests/integration/ \
             -m "not slow" \
             --environment=${{ matrix.environment }} \
             -v

Performance Regression Tracking
-------------------------------

**Problem**: Track and alert on performance regressions in CI.

**Solution - Performance Monitoring**:

.. code-block:: yaml

   # Performance regression tracking
   performance-monitoring:
     name: Performance Monitoring
     runs-on: ubuntu-latest
     
     steps:
     - uses: actions/checkout@v4
       with:
         fetch-depth: 0  # Full history for comparison
     
     - uses: actions/setup-python@v4
       with:
         python-version: '3.11'
     
     - name: Install dependencies
       run: |
         pip install -e .
         pip install pytest pytest-benchmark
     
     - name: Run performance benchmarks
       run: |
         pytest tests/performance/ \
           --benchmark-json=current-benchmark.json \
           --benchmark-histogram=benchmark-histogram
     
     - name: Download baseline benchmarks
       uses: actions/download-artifact@v4
       with:
         name: baseline-benchmarks
         path: baseline/
       continue-on-error: true
     
     - name: Compare with baseline
       run: |
         python scripts/compare-benchmarks.py \
           --current current-benchmark.json \
           --baseline baseline/benchmark.json \
           --threshold 15 \
           --output comparison-report.json
     
     - name: Upload current benchmarks as baseline
       if: github.ref == 'refs/heads/main'
       uses: actions/upload-artifact@v4
       with:
         name: baseline-benchmarks
         path: current-benchmark.json
     
     - name: Create performance report
       if: github.event_name == 'pull_request'
       uses: actions/github-script@v7
       with:
         script: |
           const fs = require('fs');
           const comparison = JSON.parse(fs.readFileSync('comparison-report.json'));
           
           let reportBody = '## 📊 Performance Report\n\n';
           
           if (comparison.regressions.length > 0) {
             reportBody += '### ⚠️ Performance Regressions Detected\n\n';
             comparison.regressions.forEach(reg => {
               reportBody += `- **${reg.benchmark}**: ${reg.change}% slower\n`;
             });
           } else {
             reportBody += '### ✅ No Performance Regressions\n\n';
           }
           
           if (comparison.improvements.length > 0) {
             reportBody += '### 🚀 Performance Improvements\n\n';
             comparison.improvements.forEach(imp => {
               reportBody += `- **${imp.benchmark}**: ${imp.change}% faster\n`;
             });
           }
           
           github.rest.issues.createComment({
             issue_number: context.issue.number,
             owner: context.repo.owner,
             repo: context.repo.repo,
             body: reportBody
           });

Testing Documentation and Reports
---------------------------------

**Problem**: Generate comprehensive test reports for stakeholders.

**Solution - Test Reporting**:

.. code-block:: yaml

   # Test reporting and documentation
   test-reporting:
     name: Generate Test Reports
     runs-on: ubuntu-latest
     needs: [test-matrix, lambda-tests, performance-check]
     
     steps:
     - uses: actions/checkout@v4
     
     - name: Download all artifacts
       uses: actions/download-artifact@v4
       with:
         pattern: '*'
         merge-multiple: true
     
     - name: Generate comprehensive test report
       run: |
         python scripts/generate-test-report.py \
           --coverage coverage.xml \
           --unit-tests test-results-*.xml \
           --integration-tests integration-test-results.xml \
           --lambda-tests tests/lambda/performance-results-*.json \
           --performance benchmark-results.json \
           --security bandit-results.json \
           --output comprehensive-test-report.html
     
     - name: Generate badges
       run: |
         python scripts/generate-badges.py \
           --coverage coverage.xml \
           --tests test-results-*.xml \
           --output badges/
     
     - name: Deploy report to GitHub Pages
       if: github.ref == 'refs/heads/main'
       uses: peaceiris/actions-gh-pages@v3
       with:
         github_token: ${{ secrets.GITHUB_TOKEN }}
         publish_dir: ./reports
         destination_dir: test-reports
     
     - name: Upload test report
       uses: actions/upload-artifact@v4
       with:
         name: comprehensive-test-report
         path: comprehensive-test-report.html

Best Practices for CI/CD Testing
--------------------------------

**CI/CD Testing Guidelines**:

1. **Fail Fast**: Run quick tests first, expensive tests later
2. **Parallel Execution**: Use matrix strategies for faster feedback
3. **Environment Parity**: Test in environments similar to production
4. **Artifact Management**: Save test results and reports for analysis
5. **Quality Gates**: Set clear criteria for pipeline success/failure
6. **Performance Monitoring**: Track performance trends over time
7. **Security Integration**: Include security scans in the pipeline
8. **Notification Strategy**: Alert the right people at the right time

**Pipeline Optimization**:

.. code-block:: yaml

   # Optimized pipeline structure
   stages:
     - lint-and-format     # Fast feedback (< 2 minutes)
     - unit-tests         # Core functionality (< 5 minutes)
     - integration-tests  # Component interaction (< 10 minutes)
     - performance-tests  # Performance validation (< 15 minutes)
     - security-scans     # Security validation (< 10 minutes)
     - deployment-tests   # End-to-end validation (< 30 minutes)

**Environment Variables**:

.. code-block:: bash

   # Required environment variables for CI/CD
   HH_TEST_MODE=true
   HH_API_KEY=<test-api-key>
   HH_PROJECT=<ci-project-name>
   HH_SOURCE=<ci-system-name>
   HH_BASE_URL=<test-environment-url>
   
   # Optional optimization variables
   HH_DISABLE_HTTP_TRACING=true
   HH_BATCH_SIZE=100
   HH_FLUSH_TIMEOUT=5000

See Also
--------

- :doc:`lambda-testing` - Lambda-specific CI/CD testing
- :doc:`performance-testing` - Performance testing in pipelines
- :doc:`integration-testing` - Integration testing strategies
- :doc:`../../tutorials/advanced-setup` - Advanced CI/CD configuration
- :doc:`../../reference/configuration/environment-vars` - CI/CD environment settings
