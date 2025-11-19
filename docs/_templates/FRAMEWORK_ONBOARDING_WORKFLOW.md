# Framework Onboarding Workflow
## Agent OS Standard for Non-Instrumentor Framework Integration

**Version:** 1.0  
**Date:** October 9, 2025  
**Purpose:** Standardized process for fully onboarding agent/AI frameworks to HoneyHive

---

## Overview

This workflow defines the complete process for onboarding a new framework to HoneyHive, from analysis to production-ready integration.

**Scope:** Agent frameworks, orchestration frameworks, and any framework that doesn't use standard auto-instrumentation patterns

**Time Estimate:** 4-8 hours per framework (depending on complexity)

---

## Phase 1: Discovery & Analysis (1-2 hours)

### Step 1.1: Clone and Examine Source Code

**Objective:** Understand the framework's architecture and tracing capabilities

**Tasks:**
```bash
# Clone framework repository
cd /tmp
git clone https://github.com/[org]/[framework].git
cd [framework]

# Search for OpenTelemetry usage
grep -r "opentelemetry" --include="*.py"
grep -r "TracerProvider\|set_tracer_provider" --include="*.py"
grep -r "tracing\|telemetry\|observability" --include="*.py" -i

# Identify key integration points
find . -name "*trace*" -o -name "*telemetry*" -o -name "*instrument*"
```

**Deliverable:** Initial architecture notes

---

### Step 1.2: Classify Framework Pattern

**Objective:** Determine the framework's integration category

**Categories:**

1. **OpenTelemetry TracerProvider Creator**
   - Sets up its own TracerProvider
   - Examples: AWS Strands
   - Integration: Provider coexistence strategy

2. **OpenTelemetry TracerProvider Consumer**
   - Uses `get_tracer_provider()` or accepts provider parameter
   - Examples: Pydantic AI, Semantic Kernel
   - Integration: Initialize HoneyHive first

3. **Custom Tracing System**
   - Has proprietary tracing (not OpenTelemetry)
   - Examples: OpenAI Agents SDK
   - Integration: Manual decoration

4. **No Tracing Built-In**
   - Framework has no tracing capabilities
   - Integration: Full manual decoration

**Deliverable:** Framework classification document

---

### Step 1.3: Document Integration Pattern

**Objective:** Document how HoneyHive will integrate with this framework

**Template:**
```markdown
## [Framework Name] Integration Analysis

**Category:** [Category from 1.2]

**Tracing Architecture:**
- Uses OpenTelemetry: [Yes/No]
- Sets up TracerProvider: [Yes/No]
- Tracing System: [OpenTelemetry/Custom/None]

**Key Integration Points:**
- [List key classes/functions/entry points]

**Recommended Integration Approach:**
- [Specific approach for this framework]

**Complexity:** [Low/Medium/High]
```

**Deliverable:** `FRAMEWORK_ANALYSIS.md` document

---

## Phase 2: Integration Design (1-2 hours)

### Step 2.1: Create Framework Metadata

**Objective:** Define framework compatibility and requirements

**Tasks:**
```bash
# Create framework compatibility YAML
vim docs/_templates/framework_compatibility.yaml
```

**Template:**
```yaml
[framework-key]:
  name: "Framework Display Name"
  category: "agent_framework"  # or orchestration_framework, workflow_framework
  
  python_version_support:
    supported:
      - "3.11"
      - "3.12"
      - "3.13"
    partial: []
    unsupported:
      - "3.10 and below"
  
  framework_version_range:
    minimum: "[framework] >= X.Y.Z"
    recommended: "[framework] >= X.Y.Z"
    tested_versions:
      - "X.Y.Z"
      - "X.Y.Z"
  
  integration_pattern:
    type: "otel_consumer"  # or otel_creator, custom_tracing, manual_only
    requires_init_order: true  # or false
    honeyhive_first: true  # if requires_init_order
    description: "Brief description of integration approach"
  
  tracing_capabilities:
    opentelemetry: true  # or false
    custom_tracing: false  # or true
    span_creation: true
    context_propagation: true
  
  known_limitations:
    - "Limitation 1"
    - "Limitation 2"
  
  example_use_cases:
    - "Use case 1"
    - "Use case 2"
```

**Deliverable:** Framework metadata in YAML

---

### Step 2.2: Design Integration Examples

**Objective:** Plan code examples showing integration patterns

**Required Examples:**

1. **Basic Integration** (simple.py)
   - Minimal setup
   - Single agent/workflow
   - Output validation

2. **Multi-Agent/Workflow** (multi_agent.py)
   - Multiple agents or complex workflow
   - Context propagation
   - Handoffs/orchestration

3. **Custom Tools/Functions** (custom_tools.py)
   - Tool decoration
   - Function tracing
   - Error handling

4. **Production Pattern** (production.py)
   - Environment variables
   - Error handling
   - Session management
   - Best practices

**Deliverable:** Example outline document

---

### Step 2.3: Plan Integration Tests

**Objective:** Define test scenarios for compatibility validation

**Required Tests:**

1. **Basic Integration Test**
   ```python
   def test_[framework]_basic_integration():
       # Initialize HoneyHive
       # Initialize framework
       # Execute simple operation
       # Verify traces captured
   ```

2. **Initialization Order Test** (if applicable)
   ```python
   def test_honeyhive_first_[framework]_second():
       # Test HoneyHive → Framework order
       
   def test_[framework]_first_honeyhive_second():
       # Test Framework → HoneyHive order (if supported)
   ```

3. **Context Propagation Test**
   ```python
   def test_context_propagation():
       # Create parent span
       # Execute framework operations
       # Verify nested span hierarchy
   ```

4. **Error Handling Test**
   ```python
   def test_error_handling():
       # Trigger framework error
       # Verify error captured in traces
   ```

**Deliverable:** Test plan document

---

## Phase 3: Implementation (2-3 hours)

### Step 3.1: Create Working Examples

**Objective:** Implement all planned examples

**Location:** `examples/integrations/[framework]_integration.py`

**Requirements:**
- All examples must run without errors
- Include helpful comments
- Add error handling
- Include output examples
- Test with actual framework (if available)

**Template Structure:**
```python
"""
[Framework Name] Integration Example

This example demonstrates how to integrate HoneyHive with [Framework],
[brief description of framework].

[Framework] is a [category], meaning [key characteristic].
"""

import os
from honeyhive import HoneyHiveTracer

# Optional: Only import if framework is available
try:
    from [framework] import [MainClass]
    FRAMEWORK_AVAILABLE = True
except ImportError:
    FRAMEWORK_AVAILABLE = False
    print("⚠️  [Framework] not available. Install with: pip install [framework]")


def main():
    """Main integration example."""
    print("🚀 [Framework] + HoneyHive Integration Example")
    print("=" * 50)
    
    if not FRAMEWORK_AVAILABLE:
        print("❌ [Framework] is not installed. Exiting.")
        return
    
    # Step 1: Initialize HoneyHive
    # [Integration-specific approach]
    
    # Step 2: Initialize framework
    # [Framework-specific setup]
    
    # Step 3: Execute operations
    # [Example operations]
    
    print("✅ Integration example completed!")


if __name__ == "__main__":
    main()
```

**Deliverable:** Working example files

---

### Step 3.2: Create Integration Tests

**Objective:** Implement compatibility matrix tests

**Location:** `tests/compatibility_matrix/test_[framework]_integration.py`

**Requirements:**
- Must use `.env` file for configuration
- Must handle missing dependencies gracefully
- Must include docstrings explaining test purpose
- Must verify trace capture

**Template Structure:**
```python
#!/usr/bin/env python3
"""
[Framework Name] Compatibility Test for HoneyHive SDK

Tests [Framework] integration with HoneyHive's tracing system.
This test validates [specific integration characteristics].
"""

import os
import sys
from pathlib import Path


def load_env_file() -> None:
    """Load environment variables from .env file if it exists."""
    # [Standard env loading code]


def test_[framework]_integration():
    """Test [Framework] integration with HoneyHive."""
    
    # Check required environment variables
    api_key = os.getenv("HH_API_KEY")
    project = os.getenv("HH_PROJECT")
    
    if not all([api_key, project]):
        print("❌ Missing required environment variables")
        return False
    
    # Check if framework is available
    try:
        import [framework]
        print("✓ [Framework] is available")
    except ImportError:
        print("⏭️  [Framework] not available - skipping integration test")
        return True  # Skip, don't fail
    
    try:
        from honeyhive import HoneyHiveTracer
        
        # Test implementation
        # [Test logic]
        
        print("✅ [Framework] integration test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def main():
    """Main test runner."""
    print("🧪 [Framework] + HoneyHive Compatibility Test")
    print("=" * 50)
    
    load_env_file()
    success = test_[framework]_integration()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
```

**Deliverable:** Integration test files

---

### Step 3.3: Create Documentation

**Objective:** Write comprehensive integration documentation

**Location:** `docs/how-to/integrations/frameworks/[framework].rst`

**Required Sections:**

1. **Title and Overview**
   ```rst
   [Framework Name] Integration
   ============================
   
   Learn how to integrate HoneyHive with [Framework] for [key benefit].
   
   .. contents::
      :local:
      :depth: 2
   ```

2. **Overview**
   - What is the framework
   - Why integrate with HoneyHive
   - Key features

3. **Prerequisites**
   - Python version requirements
   - Framework version requirements
   - Environment setup

4. **Installation**
   ```rst
   Installation
   ------------
   
   .. code-block:: bash
   
      pip install honeyhive [framework]
   ```

5. **Basic Integration**
   - Step-by-step setup
   - Code examples
   - Expected output

6. **Integration Patterns**
   - Pattern 1: [Most common use case]
   - Pattern 2: [Advanced use case]
   - Pattern 3: [Production pattern]

7. **Configuration**
   - Environment variables
   - Code configuration options
   - Best practices

8. **Advanced Usage**
   - Multi-agent/workflow patterns
   - Custom tools
   - Error handling
   - Session management

9. **Troubleshooting**
   - Common issues
   - Debug tips
   - FAQ

10. **See Also**
    - Links to related docs
    - External resources

**Deliverable:** Complete RST documentation file

---

## Phase 4: Validation & Testing (1-2 hours)

### Step 4.1: Run Integration Tests

**Objective:** Validate all tests pass

**Tasks:**
```bash
# Set up test environment
cp env.integration.example .env
# Edit .env with test credentials

# Run framework-specific test
python tests/compatibility_matrix/test_[framework]_integration.py

# Run with tox (if applicable)
tox -e py311 -- tests/compatibility_matrix/test_[framework]_integration.py
```

**Success Criteria:**
- All tests pass
- No errors or warnings
- Traces visible in HoneyHive dashboard

**Deliverable:** Test results

---

### Step 4.2: Validate Examples

**Objective:** Ensure all examples run successfully

**Tasks:**
```bash
# Test each example
python examples/integrations/[framework]_integration.py

# Verify output
# Check HoneyHive dashboard for traces
```

**Success Criteria:**
- Examples run without errors
- Output matches expectations
- Traces captured in HoneyHive

**Deliverable:** Example validation report

---

### Step 4.3: Documentation Review

**Objective:** Ensure documentation is accurate and complete

**Checklist:**
- [ ] All code examples tested
- [ ] Links work correctly
- [ ] RST renders properly
- [ ] No typos or grammar issues
- [ ] Code matches actual implementation
- [ ] Screenshots/diagrams if needed

**Tasks:**
```bash
# Build docs locally
cd docs
make clean html

# Check for warnings
cat build_warnings.log

# Review rendered output
open _build/html/how-to/integrations/frameworks/[framework].html
```

**Deliverable:** Documentation review sign-off

---

## Phase 5: Integration & Deployment (30 mins - 1 hour)

### Step 5.1: Update Navigation

**Objective:** Add framework to documentation navigation

**Files to Update:**

1. **docs/how-to/integrations/index.rst**
   ```rst
   Framework Integrations
   ----------------------
   
   .. toctree::
      :maxdepth: 1
      
      frameworks/pydantic-ai
      frameworks/openai-agents
      frameworks/semantic-kernel
      frameworks/[new-framework]
   ```

2. **docs/how-to/index.rst** (if creating new section)

3. **README.md** (add to supported frameworks list)

**Deliverable:** Updated navigation files

---

### Step 5.2: Update Compatibility Matrix

**Objective:** Add framework to compatibility tracking

**Files to Update:**

1. **tests/compatibility_matrix/README.md**
   - Add framework to list
   - Update framework count
   - Add any special notes

2. **tests/compatibility_matrix/requirements.txt** (if needed)
   ```txt
   # Framework (optional dependency for testing)
   [framework]>=X.Y.Z
   ```

**Deliverable:** Updated compatibility documentation

---

### Step 5.3: Create Pull Request Checklist

**Objective:** Ensure all deliverables are included

**PR Checklist:**
```markdown
## Framework Onboarding: [Framework Name]

### Phase 1: Discovery & Analysis
- [ ] Framework source code analyzed
- [ ] Integration pattern classified
- [ ] FRAMEWORK_ANALYSIS.md created

### Phase 2: Integration Design
- [ ] framework_compatibility.yaml entry added
- [ ] Example designs documented
- [ ] Test plan documented

### Phase 3: Implementation
- [ ] Working examples created in `examples/integrations/`
- [ ] Integration tests created in `tests/compatibility_matrix/`
- [ ] Documentation created in `docs/how-to/integrations/frameworks/`

### Phase 4: Validation
- [ ] All integration tests pass
- [ ] All examples run successfully
- [ ] Documentation reviewed and accurate

### Phase 5: Integration
- [ ] Navigation updated
- [ ] Compatibility matrix updated
- [ ] README updated (if applicable)

### Testing
- [ ] Tested with Python 3.11
- [ ] Tested with Python 3.12
- [ ] Tested with Python 3.13
- [ ] Tested with real API credentials
- [ ] Traces verified in HoneyHive dashboard

### Documentation
- [ ] RST builds without warnings
- [ ] All code examples tested
- [ ] Links verified
- [ ] Screenshots/diagrams added (if needed)
```

**Deliverable:** Complete PR with checklist

---

## Phase 6: Post-Deployment (Ongoing)

### Step 6.1: Monitor Usage

**Objective:** Track framework adoption and issues

**Metrics:**
- Documentation page views
- GitHub issues related to framework
- User feedback
- Integration test stability

---

### Step 6.2: Maintain Compatibility

**Objective:** Keep integration up-to-date with framework changes

**Tasks:**
- Monitor framework releases
- Update version compatibility
- Fix breaking changes
- Update documentation

---

## Success Criteria

A framework is considered **fully onboarded** when:

✅ **Documentation**
- Complete RST documentation page
- All code examples tested and working
- Troubleshooting guide included

✅ **Examples**
- Basic integration example
- Advanced/multi-agent example
- Production pattern example
- All examples run without errors

✅ **Testing**
- Integration test suite implemented
- Tests pass on all supported Python versions
- Tests handle missing dependencies gracefully

✅ **Metadata**
- Framework compatibility YAML complete
- Navigation updated
- Compatibility matrix updated

✅ **Validation**
- Traces successfully captured in HoneyHive
- Integration patterns verified
- Documentation builds without warnings

---

## Quick Reference

### File Checklist

```
Required Files:
├── docs/_templates/
│   └── framework_compatibility.yaml (add entry)
├── docs/how-to/integrations/frameworks/
│   └── [framework].rst (NEW)
├── examples/integrations/
│   └── [framework]_integration.py (NEW)
├── tests/compatibility_matrix/
│   └── test_[framework]_integration.py (NEW)
└── docs/how-to/integrations/index.rst (UPDATE)
```

### Time Estimates

- **Simple Framework** (e.g., basic OpenTelemetry consumer): 4-5 hours
- **Medium Framework** (e.g., with custom patterns): 6-7 hours  
- **Complex Framework** (e.g., custom tracing system): 8-10 hours

### Key Decision Points

1. **Integration Pattern** (Phase 1.2) → Determines all subsequent work
2. **Example Complexity** (Phase 2.2) → Affects implementation time
3. **Test Coverage** (Phase 2.3) → Balances thoroughness vs. time

---

## Templates Location

All templates referenced in this workflow are stored in:
- `docs/_templates/` - Documentation templates
- This workflow serves as the meta-template for the entire process

---

**Version History:**
- 1.0 (2025-10-09): Initial framework onboarding workflow

