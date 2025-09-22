# AI Assistant Standards

**🤖 Comprehensive standards for AI assistant behavior in the HoneyHive Python SDK project**

## 🚨 **CRITICAL: Start Here**

**EVERY AI assistant interaction MUST begin with compliance checking:**

1. **📋 [Compliance Checking](compliance-checking.md)** - MANDATORY first step before any task
2. **🎯 [Quality Framework](quality-framework.md)** - Overall quality requirements and standards
3. **⚡ [Quick Reference](quick-reference.md)** - Fast lookup for common patterns

## 🧪 **MANDATORY: Test Generation Framework**

**🚨 ALL test generation MUST follow the comprehensive framework with acknowledgment contract:**

### **📋 Framework Hub**
- **[Test Generation Framework Hub](code-generation/tests/README.md)** - **START HERE FOR ALL TEST GENERATION**
- **⚡ NEW: [Modular Framework v2](code-generation/tests/v2/framework-core.md)** - **OPTIMIZED FOR AI CONSUMPTION (68% smaller)**
- **🚨 Mandatory Acknowledgment Contract** - Required before proceeding
- **🛡️ Enforcement Patterns** - Violation detection and prevention
- **🎯 Quality Targets**: 100% pass rate + 90%+ coverage + 10.0/10 Pylint + 0 MyPy errors

### **⚡ Natural Discovery Flow**
1. **Framework Setup** → **Pre-Generation Setup** → **Choose Path (Unit/Integration)** 
2. **Analysis Phases 1-6** → **Test Generation** → **Quality Enforcement Phases 7-8**
3. **Mandatory Acknowledgment**: "I acknowledge the critical importance of this framework..."

### **🚨 Framework Violation Detection**
**If AI shows ANY of these behaviors, STOP immediately:**
- ❌ Starts generating code without acknowledgment
- ❌ Says "I'll follow the framework" without showing exact acknowledgment text
- ❌ Skips directly to code generation
- ❌ Says "metrics collected" without showing command output
- ❌ Uses phrases like "based on my understanding" or "I assume"

## 🏗️ **MANDATORY: Production Code Generation Framework**

**🚨 ALL production code generation MUST follow the comprehensive framework:**

### **📋 Framework Hub**
- **[Production Code Framework Hub](code-generation/production/README.md)** - **START HERE FOR PRODUCTION CODE**
- **🔀 Complexity-Based Paths**: Simple Functions → Complex Functions → Classes
- **🎯 Quality Targets**: 10.0/10 Pylint + 0 MyPy errors + Complete type annotations + Comprehensive docstrings

### **⚡ Natural Discovery Flow**
1. **Framework Setup** → **Complexity Assessment** → **Choose Path (Simple/Complex/Class)**
2. **Requirements Analysis** → **Code Generation** → **Quality Enforcement**
3. **Template-Driven Approach** with checkpoint gates

## 📚 **Core Standards**

### **🔧 Code Generation Frameworks (Complete)**
- **📁 [Code Generation Hub](code-generation/README.md)** - Complete code generation framework overview
- **🧪 [Test Generation Framework](code-generation/tests/README.md)** - **MANDATORY** comprehensive test framework
- **🏗️ [Production Code Framework](code-generation/production/README.md)** - Production code generation framework
- **🔍 [Linter Standards](code-generation/linters/README.md)** - Tool-specific compliance rules
- **📋 [Shared Resources](code-generation/shared/)** - Common generation resources
- **🎯 [Quality Gates](code-generation/shared/quality-gates.md)** - Quality requirements
- **📋 [Pre-Generation Checklist](code-generation/shared/pre-generation-checklist.md)** - MANDATORY setup

### **🛡️ Safety & Compliance**
- **🚨 [Git Safety Rules](git-safety-rules.md)** - Prevent destructive git operations
- **📝 [Commit Protocols](commit-protocols.md)** - Structured commit processes
- **✅ [Validation Protocols](validation-protocols.md)** - Verification requirements

### **🎯 Specialized Standards**
- **📅 [Date Standards](date-standards.md)** - Consistent date handling
- **❌ [Error Patterns](error-patterns.md)** - Error handling and recovery
- **🔄 [Code Generation Patterns](code-generation-patterns.md)** - Established patterns
- **🔤 [String Processing](../best-practices.md#string-processing-standards)** - **PREFER native Python over regex**

## 🎯 **Usage Workflow**

### **Phase 1: Compliance Check (MANDATORY)**
```markdown
1. Read [compliance-checking.md](compliance-checking.md)
2. Check existing Agent OS standards for the task
3. Verify project-specific rules in .cursorrules
4. Confirm established patterns before proceeding
```

### **Phase 2: Task Execution**
```markdown
1. Follow relevant standards from this directory
2. Use established templates and patterns
3. Apply quality gates and validation
4. Document compliance status
```

### **Phase 3: Validation**
```markdown
1. Verify all standards were followed
2. Run required quality checks
3. Confirm no violations occurred
4. Update documentation if needed
```

## 📊 **Standards Priority Order**

### **🚨 Critical (Must Follow)**
1. **Compliance Checking** - Always check existing standards first
2. **Git Safety Rules** - Never use dangerous git operations
3. **Quality Framework** - Meet all quality requirements
4. **Code Generation Standards** - Follow established patterns

### **⚡ Important (Should Follow)**
1. **Commit Protocols** - Structured commit processes
2. **Validation Protocols** - Verification requirements
3. **Error Patterns** - Consistent error handling

### **📋 Helpful (Good to Follow)**
1. **Date Standards** - Consistent date formatting
2. **Quick Reference** - Fast pattern lookup
3. **Code Generation Patterns** - Additional patterns

## 🎯 **Real-World Application**

### **Example: Test Execution Task**
```markdown
## Compliance Check ✅
- Reviewed: .agent-os/standards/testing/test-execution-commands.md
- Found: "🚨 MANDATORY: Use Tox - Never Pytest Directly"
- Pattern: Use `tox -e unit` for unit tests

## Task Execution ✅
- Command: `tox -e unit`
- Result: Proper environment, coverage, configuration
- Compliance: 100% - followed established standards
```

### **Example: Code Generation Task**
```markdown
## Compliance Check ✅
- Reviewed: .agent-os/standards/ai-assistant/code-generation/
- Completed: pre-generation-checklist.md
- Pattern: Use established test templates

## Task Execution ✅
- Generated: Following code-generation standards
- Quality: 10.00/10 Pylint, 0 MyPy errors
- Compliance: 100% - followed all standards
```

## 🔍 **Standards Discovery**

### **Find Relevant Standards**
```bash
# Search for topic-specific standards
find .agent-os/standards -name "*.md" | grep -i [topic]

# Find critical requirements
grep -r "CRITICAL\|MANDATORY\|NEVER" .agent-os/standards/

# Check project rules
cat .cursorrules | grep -i [topic]
```

### **Verify Compliance**
```bash
# Check existing patterns
find . -name "*.py" -exec grep -l [pattern] {} \;

# Review recent changes
git log --oneline --grep=[topic] | head -10
```

## 📋 **Standards Maintenance**

### **Adding New Standards**
1. **Check for existing coverage** - avoid duplication
2. **Follow established format** - consistent structure
3. **Include examples** - both correct and incorrect
4. **Update this README** - maintain discoverability

### **Updating Existing Standards**
1. **Maintain backward compatibility** - don't break existing patterns
2. **Document changes** - clear change rationale
3. **Update references** - keep cross-references current
4. **Test compliance** - verify AI assistants can follow updates

## 💡 **Key Principles**

1. **🔍 Check First, Act Second** - Always verify existing standards before proceeding
2. **📋 Standards Compliance by Default** - Follow established patterns, don't invent new ones
3. **🎯 Quality Over Speed** - Better to do it right than do it fast
4. **📚 Documentation Drives Behavior** - Well-documented standards enable consistent behavior

---

**🤖 Remember**: AI assistants are most effective when they consistently follow established standards rather than improvising solutions.

---

## 🔄 **README DRIFT PREVENTION**

**🚨 MANDATORY DRIFT DETECTION**: [See complete enforcement policy](../../README.md#-mandatory-drift-detection-script)

### **📋 Mandatory Update Propagation**
When making changes to AI Assistant standards:

1. **📤 Propagate Upward**: Update references in higher-level READMEs
   - `../README.md` (Standards Overview)  
   - `../../README.md` (Top-level Agent OS)

2. **🔗 Validate Links**: Ensure all internal references work
3. **🎯 Maintain Consistency**: Keep quality targets aligned across all levels
4. **📚 Update Navigation**: Adjust framework references throughout hierarchy

### **🛡️ Drift Prevention Protocol**
**Reference**: See complete drift prevention policy in `../../README.md` (lines 279-312)

**🚨 Remember**: AI Assistant standard changes must be reflected in the entire README hierarchy!
