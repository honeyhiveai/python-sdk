# Test Generation Framework - Hub

## 🚀 **QUICK START (V3 FRAMEWORK - RECOMMENDED)**

**🎯 For AI Assistants: Use the V3 Framework for deterministic, high-quality test generation:**

### **🎯 AI Assistants - Start Here**
**📄 [v3/FRAMEWORK-LAUNCHER.md](v3/FRAMEWORK-LAUNCHER.md)** - Complete AI execution guide with systematic phases

### **🏗️ Human Developers - Start Here**  
**📋 [v3/v3-framework-api-specification.md](v3/v3-framework-api-specification.md)** - Complete methodology and architecture

### **🧠 Future AI Sessions - Start Here**
**🔄 [v3/AI-SESSION-FOUNDATION.md](v3/AI-SESSION-FOUNDATION.md)** - Context foundation and background

### **⚡ Quick Reference**
**📚 [v3/README.md](v3/README.md)** - Framework overview with all entry points

**💡 V3 Benefits**: 
- **80%+ Success Rate** (restored archive parity)
- **Deterministic Quality** (100% pass + 90%+ coverage + 10.0/10 Pylint)
- **AI-Optimized Architecture** (horizontally scaled, <100 lines per instruction file)
- **Automated Validation** (programmatic quality enforcement)

---

## 📚 **FRAMEWORK VERSIONS**

### **🎯 V3 Framework (Current - Recommended)**
**Status**: Production-ready, proven 80%+ success rate
- **[v3/](v3/)** - Complete V3 framework with systematic 8-phase execution
- **Architecture**: Shared Core + Path Extensions, AI constraint-aware
- **Quality**: Automated validation with validate-test-quality.py
- **Paths**: Unit (mock everything) and Integration (real APIs)

### **📋 V2 Framework (Legacy - Archived)**
**Status**: Deprecated due to quality regression (22% success rate)
- **[v2/](v2/)** - Modular framework (archived for reference)
- **Issue**: Lost critical patterns during simplification
- **Replaced by**: V3 framework with restored archive quality

### **📖 Archive Framework (Reference)**
**Status**: Original comprehensive approach (80%+ success rate)
- **[archive/](archive/)** - Original framework files (reference only)
- **Value**: Proven patterns and comprehensive analysis
- **Evolution**: Patterns restored and optimized in V3

---

## 📚 **DETAILED GUIDANCE (LEGACY FRAMEWORK)**

**⚠️ Note**: The sections below represent the original framework. Use the new modular framework above for better efficiency.

## 🚨 **MANDATORY FRAMEWORK ACKNOWLEDGMENT CONTRACT**

**🛑 AI ASSISTANTS: You MUST respond with this EXACT text before proceeding:**

```
I acknowledge the critical importance of this framework and commit to following it completely:

🎯 WHY THIS FRAMEWORK EXISTS:
• The codebase has extensive pre-commit hooks that catch quality violations
• When I generate low-quality code, it creates days of rework cycles for the team
• Surface-level analysis leads to missing conditional branches and exception paths
• Rushing through phases results in 83% coverage instead of 90%+ target
• Each shortcut I take multiplies into hours of debugging and fixing later

🔒 MY BINDING COMMITMENT:
✅ All 9 phases executed systematically with deep analysis (not surface-level)
✅ Progress table updated in chat window after each phase with evidence
✅ All mandatory commands executed with output copy-pasted (no "metrics collected" claims)
✅ All checkpoint gates passed with documented evidence (no assumptions)
✅ Conditional logic analysis for ALL safe_log calls and exception branches
✅ Specific missing branch identification in coverage planning (lines X-Y analysis)
✅ Metrics collection with JSON/summary output shown (actual command execution)
✅ MANDATORY file header with pre-approved pylint disables applied to ALL test files
✅ Quality targets achieved: 100% pass rate, 90%+ coverage, 10.0/10 Pylint, 0 MyPy errors
✅ Framework completion criteria met before marking complete

🚨 I UNDERSTAND THE CONSEQUENCES:
• Skipping deep conditional analysis = missing critical exception paths
• Rushing through phases = failing to achieve 90%+ coverage targets  
• Making assumptions = generating code that fails pre-commit hooks
• Surface-level work = creating rework cycles that waste team time
• Each framework violation directly causes the problems this framework prevents

I commit to systematic, thorough execution over speed, understanding that proper framework execution prevents far more time waste than it creates.
```

**🚨 CRITICAL**: Without this acknowledgment, you are NOT authorized to proceed with test generation.

### **🚨 FRAMEWORK VIOLATION DETECTION**

**If AI shows ANY of these behaviors, STOP immediately:**
- ❌ Starts generating code without acknowledgment
- ❌ Says "I'll follow the framework" without showing the exact acknowledgment text
- ❌ Skips directly to code generation
- ❌ Says "metrics collected" without showing command output
- ❌ Doesn't show progress table in chat window
- ❌ Completes phases 1-5 without progressive table updates after EACH phase
- ❌ Uses phrases like "based on my understanding" or "I assume"
- ❌ Says "found X safe_log calls" without analyzing CONDITIONAL logic
- ❌ Claims "coverage planning complete" without identifying specific missing branches
- ❌ Reports "analysis complete" without showing systematic command execution
- ❌ Rushes through phases without deep conditional/exception analysis
- ❌ Generates test files without mandatory pylint disable header template

**Enforcement Response**: 
> "STOP - You violated the framework contract you committed to. You acknowledged that shortcuts create rework cycles and waste team time. Read the acknowledgment requirements and provide the exact text before proceeding."

---

## 🎯 **FRAMEWORK PURPOSE: PREVENT REWORK CYCLES**

**The Problem**: AI generates low-quality code → Pre-commit hooks catch violations → Days of rework needed
**The Solution**: Framework forces high-quality generation upfront → No rework needed → Commit succeeds immediately

**Quality Targets**: 100% pass rate, 90%+ coverage (unit) / functional validation (integration), 10.0/10 Pylint, 0 MyPy errors.

---

## 🚀 **NATURAL DISCOVERY FLOW**

### **Step 1: Framework Selection** 
**🎯 RECOMMENDED: [V3 Framework](v3/README.md)** - **PRODUCTION READY (80%+ SUCCESS RATE)**
- Complete 8-phase systematic execution
- AI-optimized architecture with quality gates
- Automated validation and enforcement

**⚡ ALTERNATIVE: [V2 Framework](v2/framework-core.md)** - **DEPRECATED (22% SUCCESS RATE)**
- Simplified but lost critical patterns
- Archived for reference only
- Replaced by V3 framework

### **Step 2: V3 Framework Entry Points**
**🤖 FOR AI ASSISTANTS: [Framework Launcher](v3/FRAMEWORK-LAUNCHER.md)** - **START HERE**
- Complete AI execution guide with systematic phases
- Quality gates and automated validation
- Path selection (unit vs integration)

**👨‍💻 FOR HUMAN DEVELOPERS: [API Specification](v3/api-specification.md)** - **COMPREHENSIVE OVERVIEW**
- Complete methodology and architecture
- Framework design principles and patterns
- Implementation guidance and best practices

**🧠 FOR FUTURE AI SESSIONS: [Session Foundation](v3/AI-SESSION-FOUNDATION.md)** - **CONTEXT FOUNDATION**
- Complete background and learnings
- Framework evolution and improvements
- Critical success factors and patterns

---

## 🔀 **STEP 3: CHOOSE YOUR PATH (V3 FRAMEWORK)**

### **🧪 UNIT TEST PATH** (Mock Everything Strategy)
**For testing individual classes/functions in complete isolation:**

**🎯 V3 UNIT PATH: [v3/paths/unit-path.md](v3/paths/unit-path.md)** - **PRODUCTION READY**
- Complete isolation with comprehensive mocking
- 90%+ line and branch coverage targets
- Standard fixtures: `mock_tracer_base`, `mock_safe_log`
- Template: [v3/ai-optimized/templates/unit-test-template.md](v3/ai-optimized/templates/unit-test-template.md)

### **🌐 INTEGRATION TEST PATH** (Real API Strategy)
**For testing end-to-end workflows and real API interactions:**

**🎯 V3 INTEGRATION PATH: [v3/paths/integration-path.md](v3/paths/integration-path.md)** - **PRODUCTION READY**
- Real API usage with backend verification
- End-to-end functional flow validation
- Standard fixtures: `honeyhive_tracer`, `verify_backend_event`
- Template: [v3/ai-optimized/templates/integration-template.md](v3/ai-optimized/templates/integration-template.md)

### **📋 PATH SELECTION GUIDE**
**🎯 PATH DECISION: [v3/paths/README.md](v3/paths/README.md)** - **COMPREHENSIVE GUIDE**
- Decision tree for path selection
- Side-by-side comparison of strategies
- Enforcement mechanisms and quality gates

---

## 📚 **SUPPORTING RESOURCES (V3 FRAMEWORK)**

### **Quick Reference**
- **🚀 [V3 Framework Launcher](v3/FRAMEWORK-LAUNCHER.md)** - AI execution guide with systematic phases
- **📋 [V3 Phase System](v3/phases/README.md)** - Complete 8-phase breakdown with evidence requirements
- **🎯 [V3 Templates](v3/ai-optimized/templates/README.md)** - Code generation templates and patterns
- **🛡️ [V3 Enforcement](v3/enforcement/README.md)** - Quality gates and automated validation

### **Legacy Reference (Archived)**
- **⚡ [V2 Phase Checklist](v2/phase-checklist.md)** - Deprecated (22% success rate)
- **⚡ [V2 Evidence Templates](v2/evidence-templates.md)** - Replaced by V3 system

---

## 📋 **FRAMEWORK COMPONENTS**

### **🎯 Test Type Frameworks**
| Document | Purpose | When to Use |
|----------|---------|-------------|
| **🎯 [V3 Unit Path](v3/paths/unit-path.md)** | **PRODUCTION READY** unit test guidance (80%+ success) | **RECOMMENDED** for unit tests |
| **🎯 [V3 Integration Path](v3/paths/integration-path.md)** | **PRODUCTION READY** integration test guidance (80%+ success) | **RECOMMENDED** for integration tests |
| **⚡ [V2 Unit Path](v2/paths/unit-path.md)** | Deprecated unit test guidance (22% success) | Legacy reference only |
| **⚡ [V2 Integration Path](v2/paths/integration-path.md)** | Deprecated integration test guidance (22% success) | Legacy reference only |

### **🔍 Decision Support**
| Document | Purpose | When to Use |
|----------|---------|-------------|
| **🎯 [V3 Framework Launcher](v3/FRAMEWORK-LAUNCHER.md)** | **PRODUCTION READY** AI execution guide | **RECOMMENDED** for AI assistants |
| **🎯 [V3 Path Selection](v3/paths/README.md)** | **PRODUCTION READY** path decision guide | **RECOMMENDED** for path selection |
| **⚡ [V2 Phase Checklist](v2/phase-checklist.md)** | Deprecated step-by-step execution | Legacy reference only |

---

## 🚨 **MANDATORY PROCESS OVERVIEW**

### **Phase 0: Pre-Generation Setup**
1. **Environment Validation** - Python venv, tox availability
2. **Metrics Collection** - Baseline measurement
3. **Target Validation** - Reject inappropriate files (`__init__.py`, `conftest.py`)

### **Test Type Classification**
- **Single Module + Business Logic** → **Unit Test Path**
- **Multi-Component Integration** → **Integration Test Path**
- **Invalid Target** → **Reject + Suggest Alternatives**

### **Phase 1-6: Comprehensive Analysis**
- Method verification, logging analysis, dependency mapping
- Usage patterns, coverage planning, linting validation

### **Test Generation**
- **Unit Tests**: Comprehensive mocks, test isolation
- **Integration Tests**: Real APIs, environment setup

### **Phase 7-8: Quality Assurance**
- **Metrics Collection**: Quality measurement
- **Quality Enforcement**: Mandatory fixes until perfect

---

## 🎯 **QUALITY TARGETS MATRIX**

| Test Type | Pass Rate | Coverage | Pylint | MyPy | Mock Strategy |
|-----------|-----------|----------|--------|------|---------------|
| **Unit Tests** | 100% | 90%+ | 10.0/10 | 0 errors | Required (all external deps) |
| **Integration Tests** | 100% | 80%+ | 10.0/10 | 0 errors | Forbidden (real APIs only) |

---

## 🔧 **COMMON WORKFLOWS**

### **Unit Test Generation Workflow**
```
1. Validate single module target
2. Apply unit test naming: test_[module]_[file].py
3. Complete analysis phases 1-6
4. Generate tests with comprehensive mocks
5. Enforce quality until 100% pass, 90%+ coverage, 10.0/10 Pylint
```

### **Integration Test Generation Workflow**
```
1. Validate multi-component target
2. Apply integration naming: test_[feature]_integration.py
3. Complete analysis phases 1-6
4. Generate tests with real APIs (no mocks)
5. Enforce quality until 100% pass, 80%+ coverage, 10.0/10 Pylint
```

---

## 🚨 **CRITICAL DECISION POINTS**

### **Target Validation Decision Tree**
```
Is target __init__.py or conftest.py? → REJECT
Does target have >50 lines business logic? → If NO: REJECT
Is target single module or multi-component? → Route to Unit/Integration
```

### **Quality Enforcement Loop**
```
Generate Tests → Check Quality → Fix Issues → Re-check → Repeat until Perfect
```

---

## 📚 **INTEGRATION WITH PROJECT STANDARDS**

### **Links to Current Standards**
- **🎯 [V3 Unit Test Path](v3/paths/unit-path.md)** - **PRODUCTION READY** unit test requirements (80%+ success)
- **🎯 [V3 Integration Test Path](v3/paths/integration-path.md)** - **PRODUCTION READY** integration test requirements (80%+ success)
- **🎯 [V3 Quality Standards](v3/enforcement/README.md)** - Comprehensive quality gates and automated validation

### **Legacy Standards (Archived)**
- **⚡ [V2 Unit Test Path](v2/paths/unit-path.md)** - Deprecated (22% success rate)
- **⚡ [V2 Integration Test Path](v2/paths/integration-path.md)** - Deprecated (22% success rate)

### **Framework Integration**
- **Pre-commit Hooks**: Enforce no mocks in integration tests
- **Tox Environments**: Use `tox -e unit` and `tox -e integration`
- **Metrics Collection**: Automated quality measurement
- **Quality Gates**: Cannot bypass quality enforcement

---

## 🎯 **SUCCESS METRICS**

**Framework Proven Across 10+ Experiments:**
- **100% Grade A Achievement** - All experiments achieve Grade A effectiveness
- **Consistent Quality** - 90%+ coverage, 10.0/10 Pylint scores achieved
- **Error Prevention** - Proactive validation prevents common issues
- **Scalability** - Works on files from 600-1200+ lines

---

## 🔄 **FRAMEWORK EVOLUTION**

**Current Version**: V3 Framework (AI-Optimized + Quality Gates)  
**Last Updated**: 2025-09-21  
**Status**: Production-ready, 80%+ success rate achieved

**V3 Key Improvements:**
- **Restored Archive Quality**: 80%+ success rate (vs V2's 22% failure)
- **AI-Optimized Architecture**: <100 lines per instruction file for optimal AI consumption
- **Automated Quality Gates**: Programmatic validation with exit codes
- **Systematic Enforcement**: Prevents framework shortcuts and quality regression
- **Comprehensive Templates**: Unit and integration path-specific code generation

**Version History:**
- **V3 (Current)**: Production-ready, systematic execution, 80%+ success rate
- **V2 (Deprecated)**: Simplified but lost critical patterns, 22% success rate
- **Archive (Reference)**: Original comprehensive approach, 80%+ success rate

---

**🎯 Start Here**: [V3 Framework](v3/README.md) for production-ready test generation with systematic quality assurance!

---

## 🔄 **README DRIFT PREVENTION**

**🚨 MANDATORY DRIFT DETECTION**: [See complete enforcement policy](../../../../README.md#-mandatory-drift-detection-script)

### **📋 Mandatory Update Propagation**
When making changes to this test generation framework:

1. **📤 Propagate Upward**: Update references in higher-level READMEs
   - `../../README.md` (AI Assistant Standards)
   - `../../../README.md` (Standards Overview)  
   - `../../../../README.md` (Top-level Agent OS)

2. **🔗 Validate Links**: Ensure all internal references work
3. **🎯 Maintain Consistency**: Keep quality targets aligned across all levels
4. **📚 Update Navigation**: Adjust framework references throughout hierarchy

### **🛡️ Drift Prevention Protocol**
**Reference**: See complete drift prevention policy in `../../../../README.md` (lines 279-312)

**🚨 MANDATORY DRIFT DETECTION SCRIPT:**
```bash
# REQUIRED: Run after ANY changes to this README
python ../../../../.agent-os/scripts/validate-readme-hierarchy.py
```

**Key Requirements:**
- Update propagation rule when changing deep-level READMEs
- Link validation after structural changes  
- Quality target consistency across all levels
- Framework reference updates when frameworks evolve
- **🛑 BLOCKING**: Script must pass (exit code 0) before changes complete

**🚨 Remember**: This prevents the framework changes from being isolated to this level only!
