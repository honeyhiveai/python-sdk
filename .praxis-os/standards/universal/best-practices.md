# Development Best Practices - HoneyHive Python SDK

**🎯 MISSION: High-level development guidelines with cross-references to detailed standards**

This document provides an overview of development best practices for the HoneyHive Python SDK. For detailed requirements, see the specialized standards documents linked throughout.

## 🚀 Quick Start for New Contributors

### Essential Setup (5 minutes)
```bash
# 1. Set up development environment
./scripts/setup-dev.sh

# 2. Create virtual environment
python -m venv python-sdk
source python-sdk/bin/activate

# 3. Install in development mode
pip install -e .

# 4. Verify setup
tox -e format && tox -e lint
```

**Detailed Setup**: See **[Environment Setup](development/environment-setup.md)**

### Essential Quality Gates (ALL MUST PASS)
```bash
tox -e format           # Code formatting (Black, isort)
tox -e lint            # Code quality (Pylint ≥8.0/10.0, MyPy)
tox -e unit            # Unit tests (100% pass rate)
tox -e integration     # Integration tests (100% pass rate)
cd docs && make html   # Documentation (zero warnings)
```

## 📋 Core Development Standards

### Code Quality Requirements
- **Type Safety**: Mandatory type hints, no `Any` for domain objects → **[Type Safety Standards](coding/type-safety.md)**
- **Architecture**: Multi-instance support, dependency injection → **[Architecture Patterns](coding/architecture-patterns.md)**
- **Graceful Degradation**: Never crash host application, structured fallbacks → **[Graceful Degradation](coding/graceful-degradation.md)**
- **Error Handling**: Exception hierarchy, logging patterns → **[Error Handling](coding/error-handling.md)**

### Testing Requirements
- **Zero Failing Tests**: Never commit failing tests → **[Testing Standards](development/testing-standards.md)**
- **5-Step Debugging**: Systematic test debugging methodology → **[Testing Standards](development/testing-standards.md#systematic-test-debugging-methodology)**
- **Coverage**: Minimum 80% project-wide, 100% for critical paths
- **Test Types**: Unit (fast), Integration (real APIs), Performance (benchmarks)

### Git Workflow
- **Branching**: Feature branches from `main`, squash merge → **[Git Workflow](development/git-workflow.md)**
- **Commits**: Conventional commits format, max 50 chars
- **Reviews**: All changes via PR, automated + manual review

## 🤖 AI Assistant Guidelines

### Critical Requirements
- **Date Usage**: Always use `date +"%Y-%m-%d"` → **[Date Standards](ai-assistant/date-standards.md)**
- **Type Safety**: Never use `Any` for domain objects → **[Type Safety Standards](coding/type-safety.md)**
- **Commit Protocol**: Review before committing → **[Commit Protocols](ai-assistant/commit-protocols.md)**
- **Quality Gates**: All tests must pass → **[Quality Framework](ai-assistant/quality-framework.md)**

### Validation Protocol
```bash
# MANDATORY: Run before generating any code
CURRENT_DATE=$(date +"%Y-%m-%d")
echo "Today is: $CURRENT_DATE"
read_file src/honeyhive/__init__.py  # Check current API
python -m mypy src/ --show-error-codes  # Validate types
```

## 📚 Documentation Standards

### Documentation System
Following the **[Divio Documentation System](https://docs.divio.com/documentation-system/)**:
- **Tutorials**: Learning-oriented, step-by-step guides
- **How-to Guides**: Problem-oriented, specific solutions  
- **Reference**: Information-oriented, technical specifications
- **Explanation**: Understanding-oriented, conceptual background

### Quality Requirements
- **Type Safety**: Use `EventType` enums, never string literals
- **Code Examples**: Complete imports, working syntax, tested execution
- **Cross-References**: Working internal links, proper toctree inclusion

**Detailed Requirements**: See **[Documentation Requirements](documentation/requirements.md)**

## 🔒 Security and Configuration

### Security Practices
- **API Keys**: Never log, support rotation, validate format → **[Security Practices](security/practices.md)**
- **Data Privacy**: Redact PII, configurable filtering
- **Dependencies**: Regular security scans, version pinning

### Configuration Management
- **Environment Variables**: HH_* prefix, multiple fallbacks → **[Configuration Management](security/configuration.md)**
- **Validation**: Type checking, range validation, graceful defaults

## 🚨 Critical Rules Summary

### Never Do This (❌)
- ❌ **Commit failing tests** - Fix tests before committing
- ❌ **Use `Any` for domain objects** - Use proper forward references
- ❌ **Skip pre-commit hooks** - Quality gates are mandatory
- ❌ **Hardcode dates** - Always use `date +"%Y-%m-%d"`
- ❌ **Ignore type errors** - Maintain strict type safety
- ❌ **Break backward compatibility** - Use deprecation warnings
- ❌ **Use regex for simple string operations** - Prefer native Python string methods

### Always Do This (✅)
- ✅ **Run full test suite** before committing
- ✅ **Use TYPE_CHECKING blocks** for forward references
- ✅ **Update documentation** with code changes
- ✅ **Follow conventional commits** format
- ✅ **Maintain type coverage** >95% for new code
- ✅ **Test in fresh environment** for integration changes
- ✅ **Use native string operations** over regex for most text processing

## 🔤 String Processing Standards

### **🎯 PREFER NATIVE PYTHON STRING OPERATIONS OVER REGEX**

**Rule**: Use native Python string methods for most text processing tasks. Reserve regex for complex pattern matching only.

#### **✅ When to Use Native String Operations**
```python
# ✅ PREFERRED - Simple, readable, maintainable
def extract_quality_targets(content: str) -> Dict[str, str]:
    """Extract quality targets using native string operations."""
    targets = {}
    content_lower = content.lower()
    
    if 'quality targets' in content_lower:
        lines = content.split('\n')
        for line in lines:
            if '100%' in line and 'pass rate' in line.lower():
                targets['pass_rate'] = '100'
            
            if '90%' in line and 'coverage' in line.lower():
                targets['coverage'] = '90'
    
    return targets

# ✅ PREFERRED - Context-aware parsing
def parse_config_line(line: str) -> Optional[Tuple[str, str]]:
    """Parse configuration key=value pairs."""
    if '=' not in line or line.strip().startswith('#'):
        return None
    
    key, value = line.split('=', 1)
    return key.strip(), value.strip()

# ✅ PREFERRED - Simple validation
def is_valid_api_key(key: str) -> bool:
    """Validate API key format."""
    return (
        key.startswith('hh_') and 
        len(key) >= 32 and 
        key.replace('hh_', '').replace('_', '').isalnum()
    )
```

#### **❌ When NOT to Use Regex**
```python
# ❌ AVOID - Regex overkill for simple tasks
import re

def extract_quality_targets_bad(content: str) -> Dict[str, str]:
    """DON'T DO THIS - Regex is overkill and error-prone."""
    patterns = {
        'pass_rate': r'(\d+)%\s+pass\s+rate',
        'coverage': r'(\d+)%\+?\s+coverage(?!\s+\+)',  # Complex negative lookahead
        'pylint': r'(\d+\.?\d*)/10\.?0?\s+Pylint',
    }
    
    targets = {}
    for target_type, pattern in patterns.items():
        matches = re.findall(pattern, content, re.IGNORECASE)  # Hard to debug
        if matches:
            targets[target_type] = matches[0]
    
    return targets

# ❌ AVOID - Regex for simple string checks
def is_valid_email_bad(email: str) -> bool:
    """DON'T DO THIS - Overly complex for basic validation."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# ✅ BETTER - Simple string operations
def is_valid_email_good(email: str) -> bool:
    """Simple validation using native string operations."""
    return '@' in email and '.' in email.split('@')[-1]
```

#### **✅ When Regex IS Appropriate**
```python
# ✅ APPROPRIATE - Complex pattern matching
import re

def extract_version_from_changelog(content: str) -> List[str]:
    """Extract version numbers from changelog - regex appropriate here."""
    # Complex pattern that would be difficult with string operations
    pattern = r'##\s+\[?(\d+\.\d+\.\d+(?:-[a-zA-Z0-9]+)?)\]?'
    return re.findall(pattern, content)

def validate_semantic_version(version: str) -> bool:
    """Validate semantic version format - regex appropriate."""
    pattern = r'^\d+\.\d+\.\d+(?:-[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*)?$'
    return re.match(pattern, version) is not None

def parse_log_entries(log_content: str) -> List[Dict[str, str]]:
    """Parse structured log entries - regex appropriate for complex parsing."""
    pattern = r'(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})\s+(\w+)\s+(.+)'
    matches = re.findall(pattern, log_content)
    return [
        {'date': date, 'time': time, 'level': level, 'message': msg}
        for date, time, level, msg in matches
    ]
```

#### **🎯 Decision Matrix**

| Task | Use Native Strings | Use Regex |
|------|-------------------|-----------|
| **Simple substring checks** | ✅ `'error' in text` | ❌ `re.search(r'error', text)` |
| **Basic parsing** | ✅ `line.split('=', 1)` | ❌ `re.match(r'(.+)=(.+)', line)` |
| **Case-insensitive search** | ✅ `keyword in text.lower()` | ❌ `re.search(r'keyword', text, re.I)` |
| **Complex patterns** | ❌ Hard to read | ✅ `re.match(r'^\d{4}-\d{2}-\d{2}$')` |
| **Multiple alternatives** | ❌ Many if/elif | ✅ `re.match(r'(jpg|png|gif)$')` |
| **Structured data extraction** | ❌ Complex parsing | ✅ `re.findall(r'(\w+)=(\w+)')` |

#### **🏆 Benefits of Native String Operations**
- **📖 Readability**: Self-documenting code
- **🐛 Debuggability**: Easy to trace execution
- **⚡ Performance**: Faster for simple operations
- **🧠 Maintainability**: Easier to modify and extend
- **🎯 Context Awareness**: Better handling of edge cases
- **❌ Fewer Bugs**: Less prone to regex gotchas

#### **⚠️ Regex Pitfalls to Avoid**
- **False Positives**: Matching unintended text
- **Performance**: Slow compilation and backtracking
- **Complexity**: Hard to read and maintain
- **Escaping**: Special character handling
- **Debugging**: Difficult to troubleshoot

## 📊 Quality Metrics and Targets

### Code Quality Targets
- **Type Coverage**: >95% for new modules, >80% project-wide
- **Test Coverage**: >80% project-wide, 100% for critical paths
- **Pylint Score**: ≥8.0/10.0 for all modules
- **Performance**: No regression >10% in key operations

### Process Metrics
- **Test Success Rate**: 100% (zero failing tests policy)
- **Review Cycle Time**: <24 hours for standard PRs
- **Documentation Lag**: Updates within 48 hours of code changes
- **Issue Resolution**: Critical issues <4 hours, standard <48 hours

## 🔄 Development Workflow

### Standard Feature Development
1. **Plan**: Create feature branch from `main`
2. **Implement**: Write code with tests and documentation
3. **Validate**: Run all quality gates locally
4. **Review**: Create PR, address feedback
5. **Deploy**: Merge to `main`, monitor metrics

### Refactoring Protocol
1. **Baseline**: Establish quality metrics before changes → **[Refactoring Protocols](coding/refactoring-protocols.md)**
2. **Incremental**: Make small, testable changes
3. **Validate**: Maintain or improve all quality metrics
4. **Document**: Update architecture and API docs

### Release Process
1. **Prepare**: Update version, changelog, documentation → **[Release Process](development/release-process.md)**
2. **Test**: Full test suite, integration validation
3. **Package**: Build and test distribution packages
4. **Deploy**: Tag release, publish to PyPI
5. **Monitor**: Track adoption, gather feedback

## 🔗 Complete Standards Reference

### Development Standards
- **[Environment Setup](development/environment-setup.md)** - Tools, virtual environments, pre-commit hooks
- **[Git Workflow](development/git-workflow.md)** - Branching, commits, pull requests, safety rules
- **[Testing Standards](development/testing-standards.md)** - Unit, integration, coverage, quality gates
- **[Performance Guidelines](development/performance-guidelines.md)** - Optimization, profiling, benchmarks
- **[Release Process](development/release-process.md)** - Versioning, packaging, deployment
- **[Specification Standards](development/specification-standards.md)** - Agent OS spec file structure and requirements

### Coding Standards  
- **[Type Safety Standards](coding/type-safety.md)** - Forward references, MyPy, refactoring protocols
- **[Architecture Patterns](coding/architecture-patterns.md)** - Multi-instance, mixins, dependency injection
- **[Graceful Degradation](coding/graceful-degradation.md)** - **CRITICAL** SDK reliability, never crash host app
- **[Refactoring Protocols](coding/refactoring-protocols.md)** - Safe refactoring, quality preservation
- **[Error Handling](coding/error-handling.md)** - Exception hierarchy, retry logic, context management

### AI Assistant Standards
- **[Quality Framework](ai-assistant/quality-framework.md)** - Autonomous quality gates, validation protocols
- **[Date Standards](ai-assistant/date-standards.md)** - Correct date handling, validation, common errors
- **[Commit Protocols](ai-assistant/commit-protocols.md)** - Review checkpoints, CHANGELOG requirements
- **[Development Process](ai-assistant/development-process.md)** - Validation protocols, escalation procedures

### Documentation Standards
- **[Documentation Requirements](documentation/requirements.md)** - Divio system, quality standards, examples
- **[Documentation Generation](documentation/documentation-generation.md)** - Automated template system
- **[Documentation Templates](documentation/documentation-templates.md)** - Tabbed interface standards
- **[Mermaid Diagrams](documentation/mermaid-diagrams.md)** - Visual diagram standards

### Security Standards
- **[Security Practices](security/practices.md)** - API keys, data privacy, authentication
- **[Configuration Management](security/configuration.md)** - Environment variables, validation, defaults

## 🌳 **AI Assistant Decision Trees**

**Quick decision-making guides for common AI assistant scenarios**

### **When Fixing Tests**
```
Test Failing?
├── ImportError?
│   ├── Module not found? → Check if module moved/renamed → Update import path
│   └── Circular import? → Move import inside function → Use TYPE_CHECKING
├── TypeError?
│   ├── Argument count mismatch? → Check @patch decorators → Add mock parameters
│   └── Type incompatibility? → Check type annotations → Fix type mismatch
├── AttributeError?
│   ├── Config access? → Use nested config pattern → tracer.config.session.inputs
│   └── Mock missing attr? → Configure mock properly → mock.config.attr = value
└── AssertionError?
    ├── Logic error? → Read production code → Understand expected behavior
    └── Value mismatch? → Debug actual values → Update assertion or fix code
```

### **When Writing Code**
```
New Function?
├── Add type annotations? → YES (MANDATORY)
│   ├── Parameters → param: Type
│   ├── Return type → -> ReturnType
│   └── Local variables → var: Type = value
├── Add docstring? → YES (Sphinx format)
│   ├── Brief description
│   ├── :param: and :type: for all parameters
│   ├── :return: and :rtype:
│   └── Working example in .. code-block::
├── Add error handling? → YES (graceful degradation)
│   ├── Specific exceptions first
│   ├── Generic Exception catch
│   └── Use safe_log() utility
└── >3 parameters? → Use keyword-only arguments (*, param)
```

### **When Encountering Errors**
```
Error Occurred?
├── Import/Module Error?
│   ├── Check error-patterns.md → Pattern 1-3
│   └── Run import validation commands
├── Test Execution Error?
│   ├── Check error-patterns.md → Pattern 4-6
│   └── Run test debugging workflow
├── Type Checking Error?
│   ├── Check error-patterns.md → Pattern 7-9
│   └── Add missing type annotations
├── Config/Architecture Error?
│   ├── Check error-patterns.md → Pattern 10-11
│   └── Use nested config access
└── Linting/Formatting Error?
    ├── Check error-patterns.md → Pattern 12-13
    └── Apply formatting fixes or approved disables
```

### **Quality Gate Decision Tree**
```
Code Ready for Commit?
├── Formatting? → Run tox -e format → Must pass 100%
├── Linting? → Run tox -e lint → Must achieve ≥8.0/10.0
├── Type Checking? → Run mypy → Must have 0 errors
├── Unit Tests? → Run tox -e unit → Must pass 100%
├── Integration Tests? → Run tox -e integration → Must pass 100%
└── Documentation? → cd docs && make html → Must have 0 warnings
```

---

**📝 Getting Started**: New contributors should begin with [Environment Setup](development/environment-setup.md) and [Git Workflow](development/git-workflow.md).
