# Documentation Requirements - HoneyHive Python SDK

**🎯 MISSION: Ensure comprehensive, accurate, and user-friendly documentation following the Divio Documentation System**

## 📚 Divio Documentation System

### Documentation Architecture
Following the **[Divio Documentation System](https://docs.divio.com/documentation-system/)** for all documentation:

#### 1. TUTORIALS (Learning-oriented) - `docs/tutorials/`
- **Purpose**: Help newcomers get started and achieve early success
- **User mindset**: "I want to learn by doing"
- **Structure**: Objective → Prerequisites → Steps → Results → Next Steps
- **Requirements**:
  - Maximum 15-20 minutes per tutorial
  - Step-by-step instructions with working code examples
  - Test with actual beginners (3+ users monthly)
  - Clear expected outcomes at each step

#### 2. HOW-TO GUIDES (Problem-oriented) - `docs/how-to/`
- **Purpose**: Solve specific real-world problems
- **User mindset**: "I want to solve this specific problem"
- **Title format**: "How to [solve specific problem]"
- **Structure**: Problem → Solution → Implementation → Verification
- **Requirements**:
  - Minimal background explanation
  - Clear steps to solution
  - Prerequisites clearly stated
  - Links to reference docs

#### 3. REFERENCE (Information-oriented) - `docs/reference/`
- **Purpose**: Provide comprehensive technical specifications
- **User mindset**: "I need to look up exact details"
- **Requirements**:
  - 100% API coverage with working examples
  - Accurate parameter descriptions and return values
  - Error condition documentation
  - Cross-references between related items
  - Automated testing of all code examples

#### 4. EXPLANATION (Understanding-oriented) - `docs/explanation/`
- **Purpose**: Provide context, background, and design decisions
- **User mindset**: "I want to understand how this works and why"
- **Requirements**:
  - Design decision rationale
  - Architecture overviews
  - Historical context when relevant
  - Comparison with alternatives

## 🎯 Integration Documentation Standards

### **MANDATORY: Tabbed Interface for Integration How-To Docs**
**ALL new instrumentor integration HOW-TO documentation MUST use the interactive tabbed interface pattern** defined in `documentation-templates.md`:

- **SCOPE**: Apply to `docs/how-to/integrations/[provider].rst` only, NOT tutorials
- **3 Required Tabs**: Installation | Basic Setup | Advanced Usage
- **Progressive Disclosure**: Start simple, advance to real-world patterns
- **Consistent UX**: Same pattern across all provider integrations
- **Copy-Paste Ready**: Complete, working examples in each tab

### Template System
- **Generation**: Use `docs/_templates/generate_provider_docs.py --provider [name]`
- **Standards**: See `documentation-generation.md` for complete template system
- **Quality**: All generated content must pass validation checklist

## 🔒 Type Safety in Documentation

### **MANDATORY: Proper Enum Usage**
**ALL documentation examples MUST use proper enum imports:**

```python
# ✅ CORRECT: Always import and use enums
from honeyhive.models import EventType

@trace(event_type=EventType.model)  # Use enum value
def llm_call():
    pass

# ❌ WRONG: Never use string literals
@trace(event_type="model")  # String literal - FORBIDDEN
```

### **MANDATORY: Complete Import Statements**
**Every code example MUST include complete, working imports:**

```python
# ✅ CORRECT: Complete imports
from honeyhive import HoneyHiveTracer, trace
from honeyhive.models import EventType
import openai

# ❌ WRONG: Incomplete imports
# Missing imports - example won't work
@trace(event_type=EventType.model)
```

### Semantic Event Type Mapping
- `EventType.model` → LLM calls, AI model operations
- `EventType.tool` → Individual functions, utilities, data processing
- `EventType.chain` → Multi-step workflows, business logic orchestration
- `EventType.session` → High-level user interactions

## 📊 Quality Standards

### Code Example Requirements
- **Syntax Validation**: All examples must be syntactically correct
- **Import Completeness**: All required imports included
- **Working Examples**: Examples must execute without errors
- **Type Safety**: Pass MyPy type checking
- **Error Handling**: Include appropriate exception handling
- **Security**: No hardcoded credentials, use environment variables

### Documentation Quality Gates
- **Sphinx Build**: Must build without warnings
- **Link Validation**: All internal links must resolve
- **Cross-References**: Proper toctree inclusion
- **Accessibility**: WCAG 2.1 AA compliance
- **Visual Standards**: Use Mermaid diagrams with HoneyHive dual-theme standard

### Content Standards
- **Accuracy**: Technical content must be current and correct
- **Completeness**: Cover all major use cases and edge cases
- **Clarity**: Written for the target audience skill level
- **Consistency**: Follow established terminology and patterns
- **Maintainability**: Easy to update when code changes

## 🎨 Visual Standards

### Mermaid Diagrams
**MANDATORY**: All Mermaid diagrams MUST use HoneyHive dual-theme configuration
- See `mermaid-diagrams.md` for complete standards
- **CRITICAL**: ALL classDef definitions MUST include `color:#ffffff`
- Use HoneyHive professional color palette
- Test in both light and dark themes

### Screenshots and Images
- **Credential Sanitization**: Remove or blur real API keys/tokens
- **Consistent Styling**: Use consistent browser/terminal themes
- **High Resolution**: Minimum 2x resolution for clarity
- **Alt Text**: Descriptive alt text for accessibility

## 🔄 Documentation Maintenance

### Update Requirements
- **Code Changes**: Update documentation within 48 hours of code changes
- **API Changes**: Update reference docs immediately for breaking changes
- **Examples**: Test and update examples with each release
- **Cross-References**: Maintain accurate links between documents

### Review Process
- **Technical Review**: Verify accuracy of all technical content
- **Editorial Review**: Check grammar, clarity, and consistency
- **User Testing**: Test tutorials with actual users
- **Accessibility Review**: Ensure WCAG compliance

### Validation Tools
- **Sphinx Validation**: Use `docs/utils/` scripts for validation
- **Link Checking**: Automated link validation in CI/CD
- **Example Testing**: Automated testing of code examples
- **Style Checking**: Consistent formatting and style

## 🚨 Critical Requirements Summary

### Never Do This (❌)
- ❌ **Use string literals** for EventType - Always use enum imports
- ❌ **Incomplete imports** - All examples must have complete imports
- ❌ **Hardcoded credentials** - Use environment variables
- ❌ **Missing error handling** - Include appropriate exception handling
- ❌ **Broken examples** - All code must be tested and working
- ❌ **Sphinx warnings** - Documentation must build cleanly

### Always Do This (✅)
- ✅ **Import EventType enum** and use proper values
- ✅ **Include complete imports** in all examples
- ✅ **Test all code examples** before committing
- ✅ **Use tabbed interface** for integration how-to guides
- ✅ **Follow Divio system** for document categorization
- ✅ **Maintain cross-references** between related documents

## 📁 File Organization

### Directory Structure
```
docs/
├── tutorials/          # Learning-oriented guides
├── how-to/            # Problem-solving guides
│   └── integrations/  # Provider integration guides (tabbed)
├── reference/         # Technical specifications
├── explanation/       # Conceptual background
├── _templates/        # Documentation generation templates
└── utils/            # Documentation validation tools
```

### Naming Conventions
- **Files**: Use kebab-case: `integration-guide.rst`
- **Sections**: Use sentence case: "Getting started"
- **Code examples**: Use descriptive function names
- **Images**: Include context: `openai-basic-setup-screenshot.png`

## 🔗 Related Standards

- **[Documentation Generation](documentation-generation.md)** - Automated template system
- **[Documentation Templates](documentation-templates.md)** - Tabbed interface standards
- **[Mermaid Diagrams](mermaid-diagrams.md)** - Visual diagram standards
- **[Type Safety Standards](../coding/type-safety.md)** - Type safety in examples
- **[Code Style](../code-style.md)** - Code formatting in documentation

---

**📝 Next Steps**: Review [Documentation Generation](documentation-generation.md) for automated template usage.
