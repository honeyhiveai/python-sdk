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

## 🎯 How-to Guide Content Quality Standards

### Content Completeness Requirements

**MANDATORY: Every how-to guide must cover ALL relevant features in its domain.**

**Validation Process Before Publishing**:
1. **List all features** in the domain by grepping the codebase
2. **Verify each feature** has documentation coverage
3. **Check examples directory** for undocumented patterns
4. **Review recent GitHub issues** for missing topics
5. **Validate compatibility information** where relevant

**Integration Guide Completeness Checklist**:
- [ ] All supported providers/integrations documented
- [ ] Version compatibility matrix included
- [ ] Installation requirements specified (Python version, dependencies)
- [ ] Configuration examples provided (basic and advanced)
- [ ] Error handling patterns shown
- [ ] Known limitations documented explicitly
- [ ] Provider-specific quirks and gotchas covered
- [ ] Performance considerations documented
- [ ] Security best practices included

**Feature Domain Completeness Checklist** (e.g., "Custom Tracing"):
- [ ] All public APIs in domain covered
- [ ] All decorator patterns documented (function-level AND class-level)
- [ ] All enrichment methods explained with examples
- [ ] Async patterns documented if applicable
- [ ] Edge cases and limitations covered
- [ ] Cross-referenced with codebase using grep verification
- [ ] Compared against examples/ directory for coverage gaps

**Troubleshooting Completeness Checklist**:
Source troubleshooting content from these mandatory sources:
- [ ] GitHub issues (review top 20 most common)
- [ ] Support tickets (identify recurring themes)
- [ ] Discord/community questions (FAQ topics)
- [ ] Internal testing pain points
- [ ] Quarterly review: Are we missing common issues?

**Mandatory Troubleshooting Coverage Areas**:
- [ ] Installation and setup issues
- [ ] Network, SSL, and certificate issues
- [ ] Authentication and API key issues  
- [ ] Integration-specific issues
- [ ] Performance and memory issues
- [ ] Configuration and environment variable issues

### Focus and Scope Standards

**MANDATORY: Each how-to guide must address ONE specific problem domain clearly.**

**Domain Specificity Requirements**:
- ✅ **MUST BE**: Specific to SDK's domain (LLM observability, tracing, evaluation)
- ✅ **MUST TARGET**: SDK's actual users (AI engineers building LLM applications)
- ✅ **MUST USE**: Domain terminology (agents, chains, tools, evaluators, spans)
- ❌ **MUST NOT BE**: Generic software advice available elsewhere
- ❌ **MUST NOT BE**: General Python programming patterns
- ❌ **MUST NOT BE**: Random collection of unrelated tips

**How-to Guide Scope Validation**:
- [ ] Single problem domain with clear theme
- [ ] Logical progression (basic → advanced)
- [ ] Coherent content flow (no tangential topics)
- [ ] Related content linked, not duplicated

**Domain-Specific Content Examples**:
- ✅ **GOOD**: "Agent architectures for LLM applications (ReAct, Chain-of-Thought, Tool-use patterns)"
- ✅ **GOOD**: "Evaluating LLM outputs with custom evaluators"
- ✅ **GOOD**: "Tracing multi-step LLM workflows"
- ❌ **BAD**: "Common software design patterns"
- ❌ **BAD**: "General Python best practices"
- ❌ **BAD**: "Generic application monitoring"

### Conciseness Standards

**MANDATORY: How-to guides must be concise and action-oriented.**

**Length Guidelines**:
- **Target**: 5-10 minutes read time (500-1000 words)
- **Code-to-text ratio**: 50-70% code examples, 30-50% explanatory text
- **Maximum**: 1500 words unless complexity justifies more

**Conciseness Enforcement**:
- ✅ **ACTION-ORIENTED** language ("Configure the tracer...", "Add tracing to...")
- ✅ **MINIMAL** background explanation (link to Explanation section for depth)
- ✅ **FOCUSED** on solving the specific problem
- ❌ **NO VERBOSE** academic writing or excessive theory
- ❌ **NO REDUNDANT** content already covered elsewhere

**Verbosity Indicators to Avoid**:
- Long introductory paragraphs before getting to solution
- Repeated explanations of basic concepts
- Excessive background theory (belongs in Explanation section)
- Multi-paragraph descriptions where bullet points suffice

## 🗂️ Content Categorization Rules

### "Getting Started" Section Rules

**CRITICAL: "Getting Started" content varies by Divio category and must NEVER contain migration content.**

**In Tutorials Section**:
- **Purpose**: First learning experience, onboarding new users
- **Content**: Installation → First trace → First integration (complete learning journey)
- **Time**: 5-15 minutes for complete first experience
- **User mindset**: "I want to learn by doing"

**In How-to Section**:
- **Purpose**: Quick wins and first common tasks
- **Content**: Curated links to highest-value how-to guides for common problems
- **Format**: Problem-focused task list with links
- **User mindset**: "What are the first problems I need to solve?"
- ✅ **FOCUS ON**: New capabilities, common first tasks, quick wins
- ❌ **NEVER INCLUDE**: Migration guides, compatibility notes, version comparisons

**Getting Started How-to Examples**:
- ✅ **GOOD**: "Add tracing to your first function"
- ✅ **GOOD**: "Connect your first LLM integration (OpenAI/Anthropic)"
- ✅ **GOOD**: "Set up your development environment"
- ✅ **GOOD**: "View your first traces in the dashboard"
- ❌ **BAD**: "Migrate from v0.0.x to v0.1.0"
- ❌ **BAD**: "Backwards compatibility considerations"
- ❌ **BAD**: "What's new in this version"

### Migration and Compatibility Content Placement

**CRITICAL: Migration guides DO NOT belong in "Getting Started".**

**Proper Placement for Migration Content**:

**Option 1: How-to → Migration & Compatibility Section** (Recommended)
- Create separate section in How-to guides
- Clearly labeled as "Migration & Compatibility"
- Focused on solving upgrade problems
- Step-by-step upgrade processes

**Option 2: Reference Section**
- Version comparison tables
- API changes documentation
- Breaking changes list
- Compatibility matrices

**Option 3: Explanation Section**
- Architectural changes explained
- Design decision rationale
- Migration strategy discussions

**Option 4: Changelog**
- Release notes
- Version history
- Upgrade notes per version

**Migration Content Structure Example**:
```
how-to/
├── Getting Started              ← NEW CAPABILITIES ONLY
│   ├── first-trace
│   ├── first-integration
│   └── view-dashboard
├── [Other how-to sections...]
├── Migration & Compatibility    ← MIGRATION CONTENT HERE
│   ├── migration-guide
│   ├── backwards-compatibility-guide
│   └── version-upgrade-checklist
└── Troubleshooting
```

### Divio Category Decision Tree

**Use this decision tree to categorize documentation content:**

**Is this content explaining what changed between versions?**
- YES → Reference (version comparison) OR Explanation (architectural changes) OR How-to/Migration section
- NO → Continue...

**Is this content teaching a learning path?**
- YES → Tutorial (step-by-step learning journey)
- NO → Continue...

**Is this content solving a specific problem?**
- YES → How-to (problem-focused solution)
- NO → Continue...

**Is this content technical specifications?**
- YES → Reference (API docs, parameters, return values)
- NO → Continue...

**Is this content explaining concepts or design?**
- YES → Explanation (conceptual understanding, architecture, "why")
- NO → Review categorization again

## 🚨 Common Divio Violations to Avoid

### Violation 1: Migration Content in "Getting Started"

**Problem**: Version migration guides in how-to "Getting Started" section  
**Why Wrong**: Migration is about changes, not new user capabilities  
**Customer Impact**: New users confused by migration-focused "getting started"  
**Fix**: Move to "Migration & Compatibility" section or Reference/Explanation

### Violation 2: Incomplete Integration Coverage

**Problem**: Integration guides missing compatibility matrix, version info, or edge cases  
**Why Wrong**: Users hit undocumented issues, lack confidence in SDK  
**Customer Impact**: "LLM Provider Integrations aren't comprehensive enough"  
**Fix**: Use Integration Guide Completeness Checklist before publishing

### Violation 3: Incomplete Feature Coverage

**Problem**: Feature guides missing APIs, patterns, or small details  
**Why Wrong**: Users discover undocumented features, documentation loses trust  
**Customer Impact**: "Custom Tracing section is missing enrichment stuff + class decorators + a lot of small things"  
**Fix**: Use Feature Domain Completeness Checklist and grep codebase for coverage

### Violation 4: Random Unfocused Content

**Problem**: How-to guide covering random unrelated topics  
**Why Wrong**: Violates "one problem domain" principle  
**Customer Impact**: "Testing Your Application is pretty random"  
**Fix**: Use Focus and Scope Standards to ensure single coherent theme

### Violation 5: Verbose Content

**Problem**: How-to guide with excessive explanation, low code-to-text ratio  
**Why Wrong**: Violates conciseness principle, slows users down  
**Customer Impact**: "Monitor In Production has potential but it's too verbose"  
**Fix**: Use Conciseness Standards - 50-70% code, link to Explanation for depth

### Violation 6: Generic Not Domain-Specific

**Problem**: How-to guide covering generic software patterns instead of domain-specific  
**Why Wrong**: Violates domain specificity requirement  
**Customer Impact**: "Common Application Patterns is not focused enough on different agent architectures"  
**Fix**: Use Domain Specificity Requirements - LLM/AI focus, not generic software

### Violation 7: Incomplete Troubleshooting

**Problem**: Troubleshooting section missing common issues  
**Why Wrong**: Users can't find solutions to known problems  
**Customer Impact**: "Troubleshooting doesn't have the SSL stuff anymore"  
**Fix**: Use Troubleshooting Completeness Checklist and source from issues/support

## 📋 Pre-Publish Documentation Review Checklist

**MANDATORY: Run this checklist before publishing any how-to documentation.**

### Content Quality Validation
- [ ] **Completeness**: All features in domain covered? (grep codebase)
- [ ] **Focus**: Single problem domain, not random collection?
- [ ] **Domain-specific**: LLM/AI focused, not generic software?
- [ ] **Concise**: 50-70% code examples, 30-50% text?
- [ ] **Comprehensive**: Checked examples/ for undocumented patterns?
- [ ] **Current**: Reviewed recent issues for missing topics?

### Categorization Validation
- [ ] **Right Divio category**: Tutorial/How-to/Reference/Explanation correct?
- [ ] **Getting Started correct**: Capabilities-focused, not migration?
- [ ] **Migration placement**: NOT in Getting Started?
- [ ] **Problem-focused**: How-to solves specific problem?
- [ ] **Learning-focused**: Tutorial teaches concepts?

### Integration/Feature Specific
- [ ] **Provider coverage**: All supported providers documented?
- [ ] **Compatibility matrix**: Version compatibility included?
- [ ] **All APIs covered**: Grepped for public methods?
- [ ] **All patterns covered**: Function AND class decorators?
- [ ] **Edge cases**: Known limitations documented?

### Troubleshooting Specific
- [ ] **Common issues**: Sourced from GitHub/support/community?
- [ ] **Mandatory areas**: SSL, auth, installation, integration covered?
- [ ] **Quarterly review**: Scheduled for missing issue check?

### Quality Gates
- [ ] **Code examples run**: All examples tested?
- [ ] **Links valid**: Internal and external links work?
- [ ] **Sphinx builds**: No warnings or errors?
- [ ] **Navigation works**: Toctree and cross-references correct?

## 🔗 Related Standards

- **[Documentation Generation](documentation-generation.md)** - Automated template system
- **[Documentation Templates](documentation-templates.md)** - Tabbed interface standards
- **[Mermaid Diagrams](mermaid-diagrams.md)** - Visual diagram standards
- **[Type Safety Standards](../coding/type-safety.md)** - Type safety in examples
- **[Code Style](../code-style.md)** - Code formatting in documentation

---

**📝 Next Steps**: Review [Documentation Generation](documentation-generation.md) for automated template usage.
