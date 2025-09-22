# Integration Test Path

## 🌐 **INTEGRATION TEST PRINCIPLES**

### **Core Philosophy**
- **Real APIs Only**: Use actual endpoints, never mock external services
- **End-to-End Validation**: Complete workflows work in real environment
- **Backend Verification**: Verify backend systems respond correctly
- **NO MOCKS POLICY**: Forbidden - use real credentials and services

### **When to Choose Integration Path**
- Testing end-to-end workflows and real API interactions
- Multi-component integration testing
- Real service validation required
- Target: Functional validation (not coverage percentage)

---

## 📋 **PHASE-SPECIFIC REQUIREMENTS**

### **Phase 1: Method Verification (Integration Focus)**

**🔍 Integration-Specific Analysis:**
- **Workflow entry points** (methods that start end-to-end processes)
- **API interaction methods** (methods that call external services)
- **Data transformation workflows** (methods that process data end-to-end)
- **Configuration-dependent methods** (methods that behave differently based on settings)
- **Multi-step processes** (methods that coordinate multiple operations)

**🚨 Mandatory Commands:**
```bash
grep -n "^class\|^def\|^    def" [PRODUCTION_FILE]
python -c "import ast, inspect; [print(f'{node.name}: {ast.get_docstring(node)}') for node in ast.walk(ast.parse(open('[PRODUCTION_FILE]').read())) if isinstance(node, (ast.FunctionDef, ast.ClassDef))]"
grep -E "^    def [^_]|^def [^_]" [PRODUCTION_FILE]
```

### **Phase 2: Logging Analysis (Real Workflow Validation)**

**🔍 Integration-Specific Analysis:**
- **Workflow progress logging** (verify correct workflow steps executed)
- **Error logging patterns** (validate error handling in real scenarios)
- **Performance logging** (timing and metrics in real environment)
- **API interaction logging** (verify external service calls)
- **Configuration logging** (validate settings applied correctly)

**🚨 Principle:** Validate real logging output, don't mock logging.

**🚨 Mandatory Commands:**
```bash
grep -n "log\." [PRODUCTION_FILE]
grep -n "import.*log\|from.*log\|getLogger\|basicConfig" [PRODUCTION_FILE]
grep -n "safe_log" [PRODUCTION_FILE]
```

### **Phase 3: Dependency Analysis (Real API Focus)**

**🔍 Integration-Specific Analysis:**
- **External API endpoints** (HoneyHive API, third-party services) - Use real APIs
- **Internal service dependencies** (tracer, client, utilities) - Real usage
- **Configuration dependencies** (environment variables, settings) - Real config
- **Network dependencies** (HTTP clients, authentication) - Real connections
- **Data persistence** (backend storage, session management) - Real data

**🚨 Critical Principle:** Use REAL APIs and services, NO MOCKS.

**🚨 Mandatory Commands:**
```bash
grep -E "^import |^from " [PRODUCTION_FILE]
grep -E "requests\.|urllib\.|json\.|os\.|sys\.|time\." [PRODUCTION_FILE]
grep -E "from honeyhive|import honeyhive" [PRODUCTION_FILE]
grep -E "config\.|settings\.|env\.|getenv" [PRODUCTION_FILE]
```

### **Phase 4: Usage Patterns (End-to-End Focus)**

**🔍 Integration-Specific Analysis:**
- **Complete user journeys** (start-to-finish workflows)
- **API interaction sequences** (multi-step API calls)
- **Error handling workflows** (real error responses and recovery)
- **Configuration scenarios** (different environment setups)
- **Performance patterns** (real timing and resource usage)

**🚨 Focus:** Test complete user journeys and real workflows.

**🚨 Mandatory Commands:**
```bash
grep -r "from.*[MODULE_NAME]\|import.*[MODULE_NAME]" src/ --include="*.py"
grep -r "[CLASS_NAME](" src/ --include="*.py" | head -10
grep -r "\.[METHOD_NAME](" src/ --include="*.py" | head -10
```

### **Phase 5: Functionality Analysis (Validation Planning)**

**🔍 Integration-Specific Analysis:**
- **End-to-end workflows** (complete user scenarios)
- **Backend state changes** (data persisted, events triggered)
- **Real API responses** (actual service integration)
- **Error handling** (real error responses from services)
- **Performance validation** (actual network timing)
- **Data integrity** (real data processing and transformation)

**🚨 Success Metric:** Functional correctness, NOT coverage percentage.

**🚨 Mandatory Commands:**
```bash
# No coverage commands - focus on functional validation planning
# Plan real API test scenarios instead
```

### **Phase 6: Pre-Generation Linting (Integration Standards)**

**🔍 Integration-Specific Planning:**
- **Real environment setup** (load .env file, real credentials)
- **Backend verification utilities** (use existing verification functions)
- **Error handling** (test real error responses from services)
- **Performance considerations** (real network timing)
- **Minimal Pylint disables** (only essential for integration patterns)

---

## 🔗 **INTEGRATION TEST GENERATION PATTERNS**

### **Standard Integration Test Structure**
```python
# File header with minimal pylint disables
# pylint: disable=too-many-lines
# Justification: Comprehensive integration test scenarios require extensive test cases

import os
import pytest
from dotenv import load_dotenv
from tests.utils import (
    verify_backend_event,
    verify_tracer_span,
    verify_span_export,
    generate_test_id,
)

load_dotenv()  # Load real test credentials

def test_end_to_end_workflow(integration_tracer, integration_client, real_project) -> None:
    """Test complete workflow with real backend verification."""
    # Arrange: Set up real environment and unique identifiers
    # Act: Execute real workflow with actual APIs
    # Assert: Verify backend state changes and real responses
```

### **Real Environment Setup**
```python
# ✅ CORRECT: Real environment setup
import os
from dotenv import load_dotenv

load_dotenv()  # Load real test credentials
api_key = os.getenv('HH_API_KEY')  # Real API key
base_url = os.getenv('HH_BASE_URL', 'https://api.honeyhive.ai')  # Real endpoint
```

### **Backend Verification Patterns**
```python
# ✅ PROVEN FIXTURES: Use existing backend verification utilities
from tests.utils import (
    verify_backend_event,      # Core backend verification
    verify_tracer_span,        # Complete workflow: create → export → verify
    verify_span_export,        # Standardized span export verification
    generate_test_id,          # Unique test identifiers
)

# ✅ STANDARD PATTERN: Complete workflow verification
verified_event = verify_tracer_span(
    tracer=integration_tracer,
    client=integration_client,
    project=real_project,
    span_name="backend_verification_test",
    unique_identifier=unique_id,
    span_attributes={
        "test.backend_verification": "true",
        "test.verification_type": "integration_test",
        "honeyhive.project": real_project,
    },
)

# ✅ BACKEND STATE VALIDATION: Verify data persistence
session_response = client.create_session("test_session")
retrieved_session = client.get_session(session_response.session_id)
assert retrieved_session.name == "test_session"  # Backend actually stored data
```

### **Standard Integration Test Fixtures**
- `integration_tracer`: Real HoneyHive tracer with live backend
- `integration_client`: Real HoneyHive client with live API
- `real_project`: Actual project for backend verification
- `unique_test_id`: Generated unique identifier for test isolation

---

## 🎯 **INTEGRATION TEST QUALITY ENFORCEMENT**

### **Success Metrics (NOT Coverage)**
- **Backend Validation**: Verify backend systems are actually working and responding correctly
- **Functional Validation**: Complete workflows work end-to-end
- **Real API Responses**: Verify actual service integration and data processing
- **Error Handling**: Real error responses from services (validate backend error handling)
- **Performance**: Actual network timing and latency
- **Data Integrity**: Real data processing and transformation
- **State Changes**: Verify backend state changes (data persisted, events triggered)

### **Quality Targets**
- **Test Pass Rate**: 100% (all integration tests must pass)
- **Functional Validation**: All workflows complete successfully
- **Pylint Score**: 10.0/10 (perfect)
- **MyPy Errors**: 0 (no type issues)
- **Black Formatting**: Clean (proper formatting)
- **Backend Verification**: All backend interactions verified

### **Approved Pylint Disables (Minimal)**
```python
# pylint: disable=too-many-lines
# Justification: Comprehensive integration test scenarios require extensive test cases

# Only add others if absolutely necessary for integration patterns
```

### **Quality Enforcement Loop (Enhanced)**
1. Generate integration tests with real APIs
2. Execute tests against real backend
3. Verify all backend interactions successful
4. Fix any functional issues or API problems
5. **Execute automated validation**: `python .agent-os/scripts/validate-test-quality.py --test-file [FILE]`
6. **Continue fixing until exit code 0** - No exceptions, no bypasses
7. Achieve 100% pass rate with real backend validation
8. Document functional validation achievement with automated validation evidence

### **🚨 MANDATORY AUTOMATED VALIDATION**
**Phase 8 cannot be completed without:**
```bash
# REQUIRED: Must return exit code 0
python .agent-os/scripts/validate-test-quality.py --test-file [GENERATED_FILE]
echo "Exit code: $?"  # Must be 0
```

**Quality Gate Rules (Integration Focus):**
- **100% test pass rate** confirmed by script (real backend validation)
- **10.0/10 Pylint score** confirmed by script  
- **0 MyPy errors** confirmed by script
- **Black formatting** confirmed by script
- **Functional validation** achieved (end-to-end workflows work)
- **No framework completion** without exit code 0
