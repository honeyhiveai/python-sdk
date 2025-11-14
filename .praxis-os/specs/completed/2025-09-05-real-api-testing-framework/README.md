# Real API Testing Framework - Overview

**Date**: 2025-09-05  
**Status**: Implemented  
**Priority**: High  
**Framework**: Comprehensive Real API Integration Testing  

## Overview

This specification defines a comprehensive real API testing framework for the HoneyHive Python SDK that validates integration with real services and catches bugs that mocked tests miss.

## Problem Solved

Traditional mocked tests can miss critical integration issues like:
- ProxyTracerProvider handling failures
- Real OpenTelemetry behavior differences
- API communication problems
- Provider detection and replacement issues
- Initialization order dependencies
- Multi-agent session continuity problems

## Solution Delivered

A multi-layered real API testing framework that includes:

1. **Traditional Real API Tests** - LLM provider integration with real API calls
2. **Non-Instrumentor Integration Tests** - Framework integration (AWS Strands prototype)
3. **OTLP Backend Validation** - End-to-end span capture verification

## Current Status

✅ **Framework Implemented**: Comprehensive testing infrastructure in place  
✅ **AWS Strands Integration**: Working prototype with real API validation  
✅ **Documentation Updated**: Integrated into main testing documentation  
🔄 **Continuous Validation**: Daily CI/CD runs for regression detection  

## Quick Start

```bash
# Run all real API integration tests
tox -e real-api

# Run specific integration test categories
pytest tests/integration/ -m real_api -v

# Run with debug mode
export HH_DEBUG_MODE=true
pytest tests/integration/ -m real_api -v -s

# Run all integration tests (includes real API)
tox -e integration
```

## Key Components

### 1. Real API Test Infrastructure
- **Location**: `tests/integration/`
- **Markers**: `@pytest.mark.real_api`, `@pytest.mark.real_instrumentor`
- **Fixtures**: `real_api_credentials`, `real_honeyhive_tracer`, `fresh_tracer_environment`

### 2. Non-Instrumentor Integration Tests
- **Location**: `tests/integration/test_*_real_api_integration.py`
- **Frameworks**: AWS Strands (prototype), extensible to other non-instrumentor frameworks
- **Scenarios**: Initialization order, concurrent setup, multi-agent sessions
- **Validation**: OTLP export, span capture, backend verification

### 3. Documentation Integration
- **Main Doc**: `docs/development/testing/real-api-testing.rst`
- **Integration**: Embedded in existing testing documentation structure
- **Examples**: Complete test templates and troubleshooting guides

## Validation Commands

```bash
# Prerequisites check
echo $HH_API_KEY
pip list | grep -E "(strands-agents|openinference|opentelemetry)"

# Run comprehensive validation
pytest tests/integration/ -m real_api --tb=short -v

# Run specific framework tests
pytest tests/integration/test_non_instrumentor_real_api_integration.py -v --real-api
pytest tests/integration/test_real_instrumentor_integration.py -v --real-api

# Performance validation
pytest tests/integration/ -m performance -v

# Backend validation (requires credentials)
pytest tests/integration/ -m real_api -k "backend" -v
```

## Key Files

- **`docs/development/testing/real-api-testing.rst`**: Complete documentation
- **`tests/integration/test_non_instrumentor_real_api_integration.py`**: Non-instrumentor framework integration tests (AWS Strands)
- **`tests/integration/conftest.py`**: Real API fixtures and configuration
- **`.github/workflows/tox-full-suite.yml`**: CI/CD integration with real API testing
- **`.praxis-os/specs/2025-09-05-non-instrumentor-integrations/`**: Related framework specs

---

**Next Steps**: The framework is complete and operational. Future work involves expanding to additional non-instrumentor frameworks and enhancing CI/CD integration patterns.
