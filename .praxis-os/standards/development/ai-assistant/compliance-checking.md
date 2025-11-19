# AI Assistant Compliance Checking

**🎯 Mandatory compliance verification before attempting any alternative approaches**

## 🚨 **CRITICAL: Check Existing Standards FIRST**

Before attempting any task, AI assistants MUST:

1. **Check existing praxis OS standards** for established patterns
2. **Verify project-specific rules** in `.cursorrules` and repo documentation
3. **Follow established patterns** rather than inventing alternatives
4. **Reference existing documentation** before creating new approaches

## 📋 **Pre-Task Compliance Checklist**

### **Before Any Code Generation**
- [ ] Read relevant praxis OS standards in `.agent-os/standards/`
- [ ] Check project-specific rules in `.cursorrules`
- [ ] Verify established patterns in existing codebase
- [ ] Confirm no existing solutions before creating new ones

### **Before Any Test Execution**
- [ ] Check `.agent-os/standards/testing/test-execution-commands.md`
- [ ] Verify tox configuration in `tox.ini`
- [ ] Use established test commands (tox) not manual alternatives
- [ ] Follow project-specific test patterns

### **Before Any Tool Usage**
- [ ] Check if tool usage is documented in praxis OS standards
- [ ] Verify tool is in approved tech stack (`.agent-os/standards/tech-stack.md`)
- [ ] Follow established tool usage patterns
- [ ] Use project-configured tool settings

## 🔍 **Compliance Verification Process**

### **Step 1: Standards Discovery**
```bash
# Check for existing standards
find .agent-os/standards -name "*.md" | grep -i [topic]
grep -r "CRITICAL\|MANDATORY\|NEVER" .agent-os/standards/
```

### **Step 2: Project Rules Verification**
```bash
# Check project-specific rules
cat .cursorrules | grep -i [topic]
grep -r "always\|never\|must" README.md pyproject.toml tox.ini
```

### **Step 3: Pattern Confirmation**
```bash
# Look for established patterns in codebase
find . -name "*.py" -exec grep -l [pattern] {} \;
git log --oneline --grep=[topic] | head -10
```

## 🚨 **Common Compliance Failures**

### **Test Execution Violations**
❌ **WRONG**: Running `pytest` directly
❌ **WRONG**: Manual coverage collection
❌ **WRONG**: Custom test environments

✅ **CORRECT**: Using `tox -e unit` for unit tests
✅ **CORRECT**: Using `tox -e integration` for integration tests
✅ **CORRECT**: Following established tox environments

### **Code Generation Violations**
❌ **WRONG**: Ignoring existing code generation standards
❌ **WRONG**: Creating new patterns without checking existing ones
❌ **WRONG**: Skipping pre-generation checklists

✅ **CORRECT**: Following `.agent-os/standards/ai-assistant/code-generation/`
✅ **CORRECT**: Using established templates and patterns
✅ **CORRECT**: Completing pre-generation checklists

### **Tool Usage Violations**
❌ **WRONG**: Using tools not in approved tech stack
❌ **WRONG**: Ignoring project-configured tool settings
❌ **WRONG**: Creating custom tool configurations

✅ **CORRECT**: Using approved tools from tech stack
✅ **CORRECT**: Following project tool configurations
✅ **CORRECT**: Respecting established tool usage patterns

## 📊 **Compliance Tracking**

### **Compliance Score Calculation**
- **100%**: Perfect compliance, followed all existing standards
- **80-99%**: Good compliance, minor deviations with justification
- **60-79%**: Moderate compliance, some standards ignored
- **<60%**: Poor compliance, major violations of established patterns

### **Compliance Reporting**
When deviating from standards, AI assistants MUST:
1. **Explicitly acknowledge** the deviation
2. **Provide justification** for why deviation is necessary
3. **Reference specific standards** being deviated from
4. **Propose updates** to standards if pattern should change

## 🎯 **Real-World Example: Test Execution**

### **Compliance Failure Example**
```bash
# ❌ VIOLATION: Manual coverage attempt
coverage run --source=src/honeyhive temp_coverage_test.py
```

**Problems**:
- Ignored existing test execution standards
- Attempted manual approach despite clear "NEVER pytest directly" rule
- Created temporary files instead of using established patterns

### **Compliance Success Example**
```bash
# ✅ CORRECT: Following established standards
tox -e unit  # Uses proper environment, coverage, and configuration
```

**Benefits**:
- Follows established `.agent-os/standards/testing/test-execution-commands.md`
- Uses proper environment configuration from `tox.ini`
- Generates accurate coverage data through established pipeline

## 🛠️ **Implementation Guidelines**

### **For AI Assistants**
1. **Always check standards first** before attempting any task
2. **Reference specific documentation** when following patterns
3. **Acknowledge when following established patterns**
4. **Report compliance status** in task execution

### **For Standards Maintenance**
1. **Keep standards up-to-date** with current project practices
2. **Make standards easily discoverable** through clear organization
3. **Provide clear examples** of correct and incorrect approaches
4. **Regular compliance audits** of AI assistant behavior

## 📋 **Compliance Verification Template**

```markdown
## Compliance Check: [Task Name]

### Standards Reviewed:
- [ ] `.agent-os/standards/[relevant-standard].md`
- [ ] Project rules in `.cursorrules`
- [ ] Existing patterns in codebase

### Compliance Status:
- **Score**: [0-100]%
- **Standards Followed**: [list]
- **Deviations**: [list with justifications]
- **Pattern Used**: [established/new/modified]

### Execution Approach:
[Describe approach and how it follows established standards]
```

---

**💡 Key Principle**: AI assistants must be **standards-compliant by default**, not standards-violating by default. Check first, then act.
