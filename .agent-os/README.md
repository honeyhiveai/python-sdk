# Agent OS - HoneyHive Python SDK

This directory contains the Agent OS configuration for the HoneyHive Python SDK project. Agent OS provides comprehensive standards, frameworks, and specifications that enable AI coding assistants to work effectively with this codebase while maintaining high quality standards.

## Directory Structure

```
.agent-os/
├── standards/                           # Comprehensive development standards
│   ├── ai-assistant/                   # AI assistant-specific standards
│   │   ├── code-generation/           # Code generation frameworks
│   │   │   ├── tests/                # 🚨 Test Generation Framework (MANDATORY)
│   │   │   │   └── README.md         # Complete test generation hub
│   │   │   ├── production/           # Production code generation framework
│   │   │   ├── linters/              # Tool-specific linting standards
│   │   │   └── shared/               # Shared generation resources
│   │   ├── quality-framework.md      # AI quality requirements
│   │   ├── git-safety-rules.md       # Forbidden git operations
│   │   └── commit-protocols.md       # Structured commit processes
│   ├── coding/                        # Language-specific standards
│   ├── development/                   # Development process standards
│   ├── documentation/                 # Documentation standards
│   ├── testing/                       # Testing methodology and standards
│   ├── security/                      # Security practices
│   ├── tech-stack.md                 # Technology requirements
│   ├── code-style.md                 # Formatting and style standards
│   └── best-practices.md             # Core development practices
├── product/                           # Product documentation
│   ├── overview.md                   # Product vision and architecture
│   ├── audience.md                   # User personas and market segments
│   ├── roadmap.md                    # Development roadmap
│   ├── features.md                   # Feature catalog
│   └── decisions.md                  # Technical decision log
└── specs/                            # Feature specifications (20+ active specs)
    ├── 2025-09-03-ai-assistant-quality-framework/
    ├── 2025-09-06-integration-testing-consolidation/
    ├── 2025-09-05-compatibility-matrix-framework/
    └── [17+ additional specifications]
```

## 🚀 **Quick Start for AI Assistants**

**First Time Here? Follow this discovery path:**

### **Step 1: Understand Your Role** (60-line read)
**📋 [Operating Model](standards/ai-assistant/OPERATING-MODEL.md)** - CRITICAL mental model
- You are the **CODE AUTHOR** (100% implementation)
- Human is the **ORCHESTRATOR** (direction, decisions, approval)
- Read this first to avoid "helper" mode mistakes

### **Step 2: Learn MCP Tools** (90-line read)
**🤖 [MCP Tool Usage Guide](standards/ai-assistant/mcp-tool-usage-guide.md)** - Tool selection reference
- `search_standards` - For process/framework questions
- `start_workflow` - For test/code generation
- Query MCP with: `"mcp tool routing guide"` for detailed usage

### **Step 3: Understand MCP Enforcement** (100-line read)
**🚨 [MCP Enforcement Rules](standards/ai-assistant/mcp-enforcement-rules.md)** - Why MCP exists
- NEVER bypass MCP to read `.agent-os/` directly (except authorship mode)
- MCP provides 90% context reduction (50KB → 5KB)
- Authorship vs consumption distinction

### **Step 4: Start Working**
**Use MCP for everything:**
- Questions? → `mcp_agent-os-rag_search_standards(query="your question")`
- Generate tests? → `mcp_agent-os-rag_start_workflow(type="test_generation_v3", ...)`
- Generate code? → `mcp_agent-os-rag_start_workflow(type="production_code_v2", ...)`

---

## 🚨 **CRITICAL: AI Assistant Entry Points**

### **🧪 For Test Generation (MANDATORY)**
**ALL AI assistants MUST follow the comprehensive test generation framework:**

1. **📋 [Test Generation Framework Hub](standards/ai-assistant/code-generation/tests/README.md)** - **START HERE**
2. **⚡ NEW: [Modular Framework v2](standards/ai-assistant/code-generation/tests/v2/framework-core.md)** - **OPTIMIZED FOR AI CONSUMPTION (68% smaller)**
3. **🚨 Mandatory Acknowledgment Contract** - Required before any test generation
4. **🎯 Quality Targets**: 100% pass rate + 90%+ coverage + 10.0/10 Pylint + 0 MyPy errors
5. **⚡ Natural Discovery Flow**: Framework → Setup → Choose Path (Unit/Integration) → Analysis → Generation → Quality

### **🏗️ For Production Code Generation**
**Follow the production code generation framework:**

1. **📋 [Production Code Framework Hub](standards/ai-assistant/code-generation/production/README.md)** - **START HERE**
2. **⚡ NEW: [Modular Framework v2](standards/ai-assistant/code-generation/production/v2/framework-core.md)** - **OPTIMIZED FOR AI CONSUMPTION**
3. **🔀 Complexity-Based Paths**: Simple Functions → Complex Functions → Classes
4. **🎯 Quality Targets**: 10.0/10 Pylint + 0 MyPy errors + Complete type annotations + Comprehensive docstrings

### **📚 For General Development**
**Reference comprehensive standards:**

1. **🤖 [AI Assistant Standards Hub](standards/ai-assistant/README.md)** - Complete AI guidelines
2. **📋 [Standards Overview](standards/README.md)** - All development standards
3. **🔒 [Compliance Checking](standards/ai-assistant/compliance-checking.md)** - MANDATORY first step
4. **🔐 [Credential File Protection](standards/ai-assistant/credential-file-protection.md)** - **CRITICAL**: Never write to .env files

## 🎯 **Quick Navigation by Task Type**

### **Test Generation Tasks**
```bash
# MANDATORY: Follow comprehensive framework
"Follow the test generation framework in .agent-os/standards/ai-assistant/code-generation/tests/README.md"

# Quality enforcement
"Ensure 100% pass rate, 90%+ coverage, 10.0/10 Pylint, 0 MyPy errors"

# Framework acknowledgment required
"Provide mandatory acknowledgment contract before proceeding"
```

### **Production Code Tasks**
```bash
# Production code generation
"Follow production framework in .agent-os/standards/ai-assistant/code-generation/production/README.md"

# Complexity assessment
"Determine if this is simple function, complex function, or class-based code"

# Quality standards
"Ensure 10.0/10 Pylint, complete type annotations, comprehensive docstrings"
```

### **General Development Tasks**
```bash
# Compliance check (MANDATORY)
"Check .agent-os/standards/ai-assistant/compliance-checking.md first"

# Standards reference
"Follow standards in .agent-os/standards/ for all development"

# Git safety
"Never use dangerous git operations - check .agent-os/standards/ai-assistant/git-safety-rules.md"
```

## 🚨 **CRITICAL PROJECT RULES**

### **🔒 Mandatory AI Assistant Rules**
1. **🧪 Test Generation Framework MANDATORY** - Follow comprehensive framework with acknowledgment contract
2. **🚫 NO MOCKS IN INTEGRATION TESTS** - Integration tests must use real systems only
3. **📋 Compliance Checking FIRST** - Always check existing standards before proceeding
4. **🛡️ Git Safety Rules** - Never use `git commit --no-verify` or dangerous operations
5. **🎯 Quality Targets Non-Negotiable** - 100% pass rate + 90%+ coverage + 10.0/10 Pylint + 0 MyPy errors

### **🔴 Critical Development Rules**
1. **ALWAYS use tox for testing** - Never run pytest directly (`tox -e unit`, `tox -e integration`)
2. **Type hints are MANDATORY** - All functions must have complete type annotations
3. **No code in `__init__.py`** - Only imports allowed
4. **Graceful degradation** - SDK must never crash the host application
5. **EventType enums only** - Never use string literals in documentation examples
6. **Pre-commit hooks cannot be bypassed** - All quality checks must pass

### **🟡 Important Patterns**
1. **Multi-instance support** - No singleton patterns (BYOI architecture)
2. **Unified `@trace` decorator** - Works for both sync and async functions
3. **Environment variables** - Support HH_*, HTTP_*, EXPERIMENT_* patterns
4. **HTTP tracing off by default** - For better performance
5. **Dynamic logic over static patterns** - Analyze content structure, not hardcoded rules

### **🟢 Quality Standards**
1. **90%+ test coverage target** - Minimum 60% per file, 80% project-wide
2. **Black formatting with 88 char lines** - Automatic formatting enforcement
3. **Comprehensive docstrings** - Sphinx-compatible with examples
4. **Structured logging** - Use logging infrastructure, never print statements
5. **Multi-tier CI/CD testing** - Unit, integration, compatibility matrix
6. **Documentation quality control** - Sphinx warnings as errors, link validation
7. **Changelog requirements** - All significant changes must update CHANGELOG.md

## 🚀 **Quick Reference**

### **🧪 Test Generation (MANDATORY FRAMEWORK)**
```bash
# STEP 1: Read framework hub (choose optimized or legacy)
"Follow .agent-os/standards/ai-assistant/code-generation/tests/README.md"
"OR use NEW modular v2: .agent-os/standards/ai-assistant/code-generation/tests/v2/framework-core.md"

# STEP 2: Provide acknowledgment contract (REQUIRED)
"I acknowledge the critical importance of this framework and commit to following it completely..."

# STEP 3: Follow natural discovery flow
# Framework → Setup → Choose Path (Unit/Integration) → Analysis → Generation → Quality
```

### **🏗️ Production Code Generation**
```bash
# STEP 1: Read production framework
"Follow .agent-os/standards/ai-assistant/code-generation/production/README.md"

# STEP 2: Assess complexity
"Determine: Simple Function / Complex Function / Class-based"

# STEP 3: Follow appropriate path with quality enforcement
```

### **💻 Initialize Tracer (Current API)**
```python
from honeyhive import HoneyHiveTracer
from honeyhive.models import EventType

tracer = HoneyHiveTracer.init(
    api_key="hh_api_...",
    project="my-project",
    source="production"
)
```

### **🎯 Use Decorators (EventType Required)**
```python
@trace(event_type=EventType.LLM)  # Use enum, not string
async def my_function():
    return await llm.complete(prompt)
```

### **🧪 Run Tests (Always Use Tox)**
```bash
# Quality enforcement commands
tox -e unit         # Unit tests only (fast, mocked)
tox -e integration  # Integration tests (real APIs, no mocks)
tox -e lint         # Linting (pylint + mypy)
tox -e format       # Code formatting checks

# Python version matrix
tox -e py311        # Python 3.11 full test suite
tox -e py312        # Python 3.12 full test suite  
tox -e py313        # Python 3.13 full test suite

# Specialized testing
tox -e compatibility        # Compatibility matrix testing
tox -e docs                # Documentation build with warnings as errors
```

## 📋 **Creating New Specifications**

When adding new features, create a spec following this structure:

```bash
.agent-os/specs/YYYY-MM-DD-feature-name/
├── README.md         # Quick overview and status
├── srd.md           # Business requirements and goals
├── specs.md         # Technical specifications
├── tasks.md         # Implementation task breakdown
└── implementation.md # Detailed implementation guidance
```

**🚨 Critical Active Specs**:
- **`2025-09-03-ai-assistant-quality-framework/`** - AI quality requirements and autonomous testing
- **`2025-09-06-integration-testing-consolidation/`** - No-mock integration testing (RELEASE BLOCKING)
- **`2025-09-05-compatibility-matrix-framework/`** - Multi-provider testing framework
- **`2025-09-03-commit-message-standards/`** - Structured commit message validation

## 🔄 **Documentation Maintenance**

### **When Making Changes**:
1. **Update Agent OS standards** - Keep `.agent-os/standards/` current
2. **Add technical decisions** - Document in `.agent-os/product/decisions.md`
3. **Update roadmap** - Reflect progress in `.agent-os/product/roadmap.md`
4. **Maintain README hierarchy** - Prevent drift between levels

### **Quality Gates for Documentation**:
- **Sphinx warnings as errors** - Documentation must build cleanly
- **Link validation** - All internal references must work
- **Example testing** - All code examples must be tested
- **CHANGELOG updates** - Required for all significant changes

## 🏗️ **Current Architecture Integration**

This Agent OS configuration supports:
- **950+ comprehensive tests** - 831 unit + 119 integration tests
- **Multi-tier CI/CD strategy** - Unit, integration, compatibility matrix
- **Python 3.11-3.13 support** - Full version compatibility matrix
- **BYOI architecture** - Bring Your Own Instrumentor pattern
- **OpenTelemetry standards** - Complete tracing and instrumentation
- **AWS Lambda compatibility** - Production deployment support
- **Performance benchmarking** - Statistical significance validation

## 👥 **For Contributors**

### **🚨 MANDATORY SETUP**
```bash
# Required first step for all contributors
./scripts/setup-dev.sh
```

### **📋 Development Requirements**
1. **Follow AI Assistant Standards** - Use frameworks in `.agent-os/standards/ai-assistant/`
2. **Pre-commit compliance** - Cannot bypass quality enforcement
3. **Test generation framework** - Mandatory for all test creation
4. **Quality targets** - 100% pass rate + 90%+ coverage + 10.0/10 Pylint + 0 MyPy errors
5. **Documentation updates** - CHANGELOG.md required for significant changes
6. **Real integration testing** - No mocks in integration tests

### **🛡️ Quality Standards (Automatically Enforced)**
- **Black formatting** (88-character lines)
- **Import sorting** (isort with black profile)  
- **Static analysis** (pylint + mypy with strict settings)
- **YAML validation** (yamllint with 120-character lines)
- **Documentation quality** (Sphinx warnings as errors)
- **Test coverage** (minimum thresholds enforced)

## 📞 **Support & Resources**

### **Documentation Hierarchy**
1. **Start here**: `.agent-os/README.md` (this file)
2. **Standards overview**: `.agent-os/standards/README.md`
3. **AI assistant hub**: `.agent-os/standards/ai-assistant/README.md`
4. **Test framework**: `.agent-os/standards/ai-assistant/code-generation/tests/README.md`

### **External Resources**
- **Official HoneyHive Documentation**: https://docs.honeyhive.ai
- **Technical Decisions Log**: `.agent-os/product/decisions.md`
- **Product Roadmap**: `.agent-os/product/roadmap.md`

## 🔄 **README Maintenance Protocol**

### **🛡️ Preventing Future Drift**
**To maintain consistency across the README hierarchy:**

1. **📋 Update Propagation Rule**: When updating deep-level READMEs, propagate key changes upward
2. **🔗 Link Validation**: Verify all internal links work after structural changes
3. **🎯 Quality Target Consistency**: Ensure quality targets remain consistent across all levels
4. **📚 Framework Reference Updates**: Update framework references when frameworks evolve

### **🚨 MANDATORY DRIFT DETECTION SCRIPT**

**🛑 STOP: BEFORE CONTINUING - RUN DRIFT DETECTION**

**CRITICAL: After ANY README changes, you MUST immediately run:**

```bash
# MANDATORY: Run drift detection script after README changes
python .agent-os/scripts/validate-readme-hierarchy.py
```

**❌ DO NOT PROCEED until exit code 0**
**❌ DO NOT make additional changes until validated**
**❌ DO NOT commit changes until drift detection passes**

**🚨 ENFORCEMENT TRIGGERS:**
- Modified any `.md` file in `.agent-os/`? → **RUN SCRIPT NOW**
- Updated framework references? → **RUN SCRIPT NOW**  
- Changed navigation links? → **RUN SCRIPT NOW**
- Modified `.cursorrules`? → **RUN SCRIPT NOW**

**🛑 BLOCKING REQUIREMENT**: 
- Script MUST pass (exit code 0) before changes are considered complete
- Fix ALL issues identified by the script
- Re-run script until zero issues remain
- **NO EXCEPTIONS**: This step cannot be skipped or deferred

**📋 Script Validates:**
- **README hierarchy consistency** - All internal links work
- **Quality target alignment** - Consistent targets across all levels  
- **Framework references** - Current framework links throughout
- **⚙️ .cursorrules integration** - Agent OS references and modular framework links

### **🚨 Mandatory Review Points**
**Review README hierarchy when:**
- Adding new frameworks or standards
- Changing directory structure
- Updating quality requirements
- Modifying AI assistant guidelines
- Creating new specifications

### **📊 Monthly Maintenance Checklist**
- [ ] Validate all internal links work correctly
- [ ] Verify directory structure listings match reality
- [ ] Check quality targets are consistent across levels
- [ ] Ensure framework references are current
- [ ] Update navigation paths if needed

### **🎯 Success Metrics**
- **Zero broken internal links** across README hierarchy
- **Consistent quality targets** at all levels
- **Accurate directory listings** in all READMEs
- **Current framework references** throughout

---

**🎯 Remember**: Agent OS provides the comprehensive frameworks and standards that enable consistent, high-quality development. Always start with the appropriate framework hub for your task type!
