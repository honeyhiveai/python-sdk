# Environment Variable Enforcement System

**Date**: 2025-09-12  
**Status**: Active  
**Scope**: Local development and testing  

## Overview

The HoneyHive Python SDK implements programmatic enforcement for detecting and sourcing `.env` files in local development environments, following Agent OS standards. This system ensures that developers always use proper credential management and prevents tests from failing due to missing environment variables.

## 🎯 **Key Features**

### **Automatic .env File Detection**
- Detects local development vs CI/production environments
- Automatically loads `.env` or `.env.integration` files
- Provides clear error messages when files are missing

### **Credential Validation**
- Validates required environment variables are present
- Provides helpful error messages for missing credentials
- Supports both required and optional credentials

### **Agent OS Compliance**
- Follows Agent OS Zero Failing Tests Policy
- Enforces local development standards
- Provides fallback mechanisms for CI/production

## 🔧 **Implementation**

### **Core Module: `tests/utils/env_enforcement.py`**

```python
from tests.utils.env_enforcement import (
    enforce_local_env_file,           # Load .env file in local dev
    enforce_integration_credentials,  # Validate required credentials
    get_llm_credentials,             # Get optional LLM provider keys
    print_env_status,                # Debug environment status
)
```

### **Environment Detection Logic**

The system automatically detects the environment:

- **Local Development**: No CI indicators, requires `.env` files
- **CI/Production**: Has CI environment variables, uses direct env vars

```python
def is_local_development(self) -> bool:
    """Detect if we're running in local development environment."""
    ci_indicators = [
        "CI", "GITHUB_ACTIONS", "GITLAB_CI", "JENKINS_URL", 
        "TRAVIS", "CIRCLECI", "BUILDKITE", "AZURE_PIPELINES"
    ]
    
    # Check CI indicators and HH_SOURCE patterns
    return not any(os.getenv(indicator) for indicator in ci_indicators)
```

### **File Priority Order**

The system looks for environment files in this order:

1. `.env.integration` (integration-specific credentials)
2. `.env` (general project credentials)

## 🚨 **Error Handling**

### **Missing .env File in Local Development**

```
🚨 LOCAL DEVELOPMENT ERROR: No .env file found!

According to Agent OS standards, local development MUST use .env files for credentials.

Expected .env file locations:
  - /path/to/project/.env.integration
  - /path/to/project/.env

To fix this:
1. Copy the example file:
   cp env.integration.example .env.integration

2. Edit .env.integration with your real credentials:
   HH_API_KEY=your_honeyhive_api_key_here
   HH_PROJECT=your_project_name_here
   OPENAI_API_KEY=your_openai_key_here  # (optional, for LLM tests)

3. Never commit .env files to git (they're in .gitignore)
```

### **Missing Required Credentials**

```
🚨 MISSING REQUIRED CREDENTIALS:

The following environment variables are required:
  - HH_API_KEY

Loaded from: /path/to/project/.env

For local development, add these to your .env file:
HH_API_KEY=your_hh_api_key_here

For CI/production, set these environment variables directly.
```

## 📋 **Integration with Test Framework**

### **Updated `tests/conftest.py`**

The enforcement system is integrated into the test framework:

```python
# Load environment variables for real API testing using Agent OS enforcement
try:
    from .utils.env_enforcement import enforce_local_env_file, print_env_status
    
    # Enforce .env file loading in local development (per Agent OS standards)
    enforce_local_env_file()
    
    # Print environment status for debugging (only in debug mode)
    if os.getenv("HH_DEBUG_MODE", "false").lower() == "true":
        print_env_status()
        
except ImportError:
    # Fallback to old method if enforcement module not available
    # ... fallback implementation
```

### **Enhanced Fixtures**

```python
@pytest.fixture(scope="session")
def real_api_credentials():
    """Get real API credentials for integration tests with Agent OS enforcement."""
    try:
        from .utils.env_enforcement import enforce_integration_credentials
        
        # Use Agent OS enforcement to validate credentials
        validated_creds = enforce_integration_credentials()
        
        return {
            "api_key": validated_creds["HH_API_KEY"],
            "source": os.environ.get("HH_SOURCE", "pytest-integration"),
            "api_url": os.environ.get("HH_API_URL", "https://api.honeyhive.ai"),
            "project": os.environ.get("HH_PROJECT", "test-project"),
        }
        
    except ImportError:
        # Fallback implementation
        # ...
```

## 🛠️ **Developer Tools**

### **Setup Script: `scripts/setup-local-env.py`**

Helps developers create their local `.env` file:

```bash
python scripts/setup-local-env.py
```

### **Environment Status Debugging**

```bash
# Test the enforcement system
python tests/utils/env_enforcement.py

# Run tests with debug output
HH_DEBUG_MODE=true pytest tests/integration/test_example.py -v -s
```

## 📊 **Environment Variables**

### **Required for Integration Tests**
- `HH_API_KEY`: HoneyHive API key (required)

### **Optional Configuration**
- `HH_PROJECT`: Project name (derived from API key if not set)
- `HH_SOURCE`: Source identifier (defaults to "pytest-integration")
- `HH_API_URL`: API endpoint (defaults to "https://api.honeyhive.ai")

### **Optional LLM Provider Keys**
- `OPENAI_API_KEY`: For OpenAI instrumentor tests
- `ANTHROPIC_API_KEY`: For Anthropic instrumentor tests
- `GOOGLE_API_KEY`: For Google AI instrumentor tests
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`: For AWS Bedrock tests
- `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`: For Azure OpenAI tests

## 🔄 **Workflow Integration**

### **Local Development Workflow**

1. **First Time Setup**:
   ```bash
   # Copy example file
   cp env.integration.example .env
   
   # Edit with real credentials
   vim .env
   
   # Run tests
   tox -e integration
   ```

2. **Daily Development**:
   - Tests automatically load `.env` file
   - Clear error messages if credentials missing
   - Debug output available with `HH_DEBUG_MODE=true`

### **CI/Production Workflow**

1. **Environment Variables**: Set directly in CI/production environment
2. **No .env Files**: System detects CI environment and skips .env loading
3. **Same Validation**: Same credential validation applies

## 🎯 **Benefits**

### **For Developers**
- ✅ **No More Missing Credentials**: Clear error messages guide setup
- ✅ **Automatic Detection**: No manual environment switching
- ✅ **Secure by Default**: Credentials never committed to git
- ✅ **Debug Support**: Easy troubleshooting with status output

### **For CI/Production**
- ✅ **Environment Agnostic**: Works with direct environment variables
- ✅ **No File Dependencies**: Doesn't require .env files in deployment
- ✅ **Same Validation**: Consistent credential checking everywhere

### **For Agent OS Compliance**
- ✅ **Zero Failing Tests**: Prevents test failures due to missing credentials
- ✅ **Local Development Standards**: Enforces .env file usage
- ✅ **Clear Error Messages**: Guides developers to correct setup

## 🔍 **Testing the System**

### **Test Missing .env File**
```bash
# Move .env file temporarily
mv .env .env.backup

# Test enforcement (should show clear error)
python tests/utils/env_enforcement.py

# Restore file
mv .env.backup .env
```

### **Test Integration**
```bash
# Test with debug output
HH_DEBUG_MODE=true pytest tests/integration/test_tracer_integration.py::TestTracerIntegration::test_tracer_event_creation_integration -v -s
```

## 📚 **Related Documentation**

- **Agent OS Standards**: `.agent-os/standards/best-practices.md`
- **Environment Variables**: `ENVIRONMENT_VARIABLES.md`
- **Integration Testing**: `docs/development/testing/`
- **Zero Failing Tests Policy**: `.agent-os/standards/best-practices.md`

---

**Compliance**: This enforcement system is MANDATORY for all local development in the HoneyHive Python SDK project and follows Agent OS standards for credential management.
