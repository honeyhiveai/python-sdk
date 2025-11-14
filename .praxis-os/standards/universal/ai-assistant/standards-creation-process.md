# Standards Creation Process

**Standard for creating, structuring, and maintaining standards in prAxIs OS.**

---

## 🎯 TL;DR - Standards Creation Quick Reference

**Keywords for search**: standards creation, creating standards, standards process, how to write standards, standards structure, standards template, standards quality, maintaining standards

**Core Principle:** Standards define "how to work" guidelines that shape AI agent behavior and code quality. Create them when you need reusable, consistent processes.

**When to Create a Standard:**
- ✅ Process/methodology needs consistency
- ✅ Quality criteria needs definition
- ✅ Best practices need documentation
- ✅ Constraints/rules need enforcement
- ❌ NOT for one-time tasks or feature designs (use specs)

**Standard Structure (Required Sections):**
1. **Purpose** - Why this standard exists (2-3 sentences)
2. **The Problem** - What happens WITHOUT this standard
3. **The Standard** - The actual rules/guidelines (specific, actionable)
4. **Checklist** - Quick validation checklist
5. **Examples** - Real-world applications
6. **Anti-Patterns** - Common mistakes to avoid

**Quality Standards:**
- Specific & actionable (not vague advice)
- Measurable (can verify compliance)
- Justified (explains WHY, not just WHAT)
- Testable (can validate with examples)
- Discoverable (RAG-optimized with TL;DR, query hooks)

**Creation Workflow:**
```
1. Query existing standards → Identify gap
2. Write Problem → Validate need
3. Draft Standard → Get feedback
4. Add examples → Demonstrate application
5. RAG optimize → Query for optimization guidance (see Step 5 below)
6. Test queries → Validate findability (test for pollution)
```

**Common Mistakes:**
- ❌ Too vague ("write good code" instead of specific checklist)
- ❌ No examples (abstract rules without demonstrations)
- ❌ Not RAG-optimized (hidden, undiscoverable content)
- ❌ No justification (rules without reasoning)

**Maintenance:**
- Review quarterly or when issues arise
- Update based on dogfooding feedback
- Archive obsolete standards (don't delete)
- Version changes that impact behavior

---

## ❓ Questions This Answers

1. "How do I create a new standard?"
2. "When should I create a standard?"
3. "What structure should standards follow?"
4. "What makes a good standard?"
5. "How do I maintain standards?"
6. "What are standards creation anti-patterns?"
7. "How do I ensure standards are discoverable?"
8. "What's the difference between standards and specs?"
9. "How do I validate standard quality?"
10. "What examples exist of good standards?"

---

## 🎯 Purpose

Define how to create new standards, when to create them, and how to structure them for maximum effectiveness. Standards are the "how to work" guidelines that shape agent behavior and code quality.

**Key Distinction**: Standards vs Specs
- **Standards**: Guidelines for HOW to work (this is a standard)
- **Specs**: Design docs for WHAT to build (features/implementations)

---

## When Should I Create a Standard?

Create a standard when you need reusable, consistent guidelines for recurring processes or behaviors.

Create a standard when you need to define:
- ✅ **Process/methodology** - How to do something consistently
- ✅ **Quality criteria** - What "good" looks like
- ✅ **Best practices** - Patterns that work well
- ✅ **Constraints/rules** - Things that must/must not be done
- ✅ **Behavioral patterns** - How agents should act

**Examples of standards:**
- Production code checklist
- Testing standards  
- RAG content authoring
- Git safety rules
- Documentation patterns

Do NOT create a standard for:
- ❌ Feature designs (use specs)
- ❌ One-time tasks (just do them)
- ❌ Project-specific details (document in project README)

---

## What Structure Should Standards Follow?

All standards must follow this RAG-optimized template structure for consistency and discoverability.

```markdown
# [Standard Name]

**[One sentence describing what this standard defines]**

---

## 🎯 TL;DR - [Standard Name] Quick Reference

**Keywords for search**: [primary keyword], [synonym 1], [synonym 2], [natural query phrase 1], [natural query phrase 2], [how to X], [what is X], [when to use X]

**Core Principle:** [The key insight this standard embodies - one clear sentence]

**[The Core Pattern/Process - 3-5 key points]:**
1. **[First key point]** - [Brief explanation]
2. **[Second key point]** - [Brief explanation]
3. **[Third key point]** - [Brief explanation]

**[Main Checklist Name]:**
- [ ] [Most critical criterion 1]
- [ ] [Most critical criterion 2]
- [ ] [Most critical criterion 3]
- [ ] [Most critical criterion 4]

**Common Anti-Patterns:**
- ❌ [Anti-pattern 1]
- ❌ [Anti-pattern 2]
- ❌ [Anti-pattern 3]

**When to Query This Standard:**
- [Scenario 1] → `pos_search_project(content_type="standards", query="[query phrase 1]")`
- [Scenario 2] → `pos_search_project(content_type="standards", query="[query phrase 2]")`
- [Scenario 3] → `pos_search_project(content_type="standards", query="[query phrase 3]")`

---

## ❓ Questions This Answers

1. "[Question phrased as agent would ask it]"
2. "[Another natural language question]"
3. "[How to do X?]"
4. "[What is Y?]"
5. "[When should I Z?]"
6. "[Why does W matter?]"
7. "[What are X anti-patterns?]"
8. "[How to validate X?]"
9. "[What examples exist for X?]"
10. "[How to avoid common mistakes in X?]"

---

## 🎯 Purpose

[2-3 sentences explaining why this standard exists and what problem it solves]

**Core Principle**: [The key insight this standard embodies]

---

## Why [Standard Topic] Matters - The Problem

[Describe what happens WITHOUT this standard]

**Example of the problem:**
[Concrete scenario showing the pain point]

**Impact:**
- ❌ [Negative outcome 1]
- ❌ [Negative outcome 2]
- ❌ [Negative outcome 3]

---

## What Is [The Standard]?

### [Principle/Rule 1 - Phrased as Question]

**What to do:**
[Clear, actionable guidance]

**Why:**
[Rationale for this principle]

**Example:**
```
[Code/text showing correct application]
```

**Anti-pattern:**
```
[Code/text showing what NOT to do]
```

### [Principle/Rule 2 - Phrased as Question]

[Repeat structure]

---

## What Is the [Standard Topic] Checklist?

When [doing the thing this standard covers]:

- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]
- [ ] [Criterion 4]

---

## What Are [Standard Topic] Examples?

### Example 1: [Scenario]

**Context**: [Situation]

**❌ Bad** (violates standard):
```
[Example of violation]
```

**✅ Good** (follows standard):
```
[Example of compliance]
```

**Why it matters**: [Impact of following vs not following]

---

## What Are [Standard Topic] Anti-Patterns?

### Anti-Pattern 1: [Common mistake]

**Wrong:**
```
[What people do wrong]
```

**Right:**
```
[Correct approach]
```

**Why it fails:** [Explanation of the problem]

---

## ❓ Frequently Asked Questions

**[Common question 1]?**
→ [Answer]

**[Common question 2]?**
→ [Answer]

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **[Scenario 1]** | `pos_search_project(content_type="standards", query="[natural query 1]")` |
| **[Scenario 2]** | `pos_search_project(content_type="standards", query="[natural query 2]")` |
| **[Scenario 3]** | `pos_search_project(content_type="standards", query="[natural query 3]")` |

---

## 🔗 Related Standards

**Query workflow for [topic] mastery:**

1. **Start with [this standard]** → `pos_search_project(content_type="standards", query="[topic]")` (this document)
2. **Learn [related topic 1]** → `pos_search_project(content_type="standards", query="[related topic 1]")` → `standards/[path]/[file].md`
3. **Understand [related topic 2]** → `pos_search_project(content_type="standards", query="[related topic 2]")` → `standards/[path]/[file].md`

**By Category:**

**[Category 1]:**
- `standards/[path]/[file].md` - [Description] → `pos_search_project(content_type="standards", query="[query]")`

**[Category 2]:**
- `standards/[path]/[file].md` - [Description] → `pos_search_project(content_type="standards", query="[query]")`

---

**Related Standards (Legacy format - update to above):**
- [Related standard 1]
- [Related standard 2]

**Query anytime:**
```python
pos_search_project(content_type="standards", query="[natural language query]")
```

---

**Remember**: [Key takeaway for this standard]
```

---

## How to Create a New Standard (Step-by-Step)?

Complete workflow from identifying a gap through validation and publication.

### Step 1: Identify the Gap

**Trigger**: You experience a problem or inconsistency that needs a standard.

**Questions to ask:**
- Is this a repeating pattern that needs consistency?
- Would a guideline prevent quality/safety issues?
- Is this knowledge that agents need to query?

**Example**: 
- "Agents keep breaking out of prAxIs OS patterns"
- "Content isn't discoverable through RAG"
- "Code quality is inconsistent"

### Step 2: Research Existing Standards

**Before creating**, query to see if standard already exists:

```python
pos_search_project(content_type="standards", query="[topic] standards")
pos_search_project(content_type="standards", query="how to [do the thing]")
pos_search_project(content_type="standards", query="[related concept] guidelines")
```

**If exists**: Update existing standard, don't create duplicate.

### Step 3: Draft the Standard

**Use the template above.**

**Key requirements:**
- Clear, actionable principles
- Examples showing good vs bad
- Checklist for compliance
- Anti-patterns documented
- RAG-optimized for discoverability (complete Step 5 before finalizing)

### Step 4: Add Examples

**Add concrete examples showing good vs bad applications.**

This step ensures your standard has practical demonstrations that agents can learn from.

### Step 5: RAG Optimize → Ensure Discoverability

**Critical:** Your standard is only useful if agents can find it through natural queries.

**Query for content optimization (how to write):**
```python
pos_search_project(content_type="standards", query="how to make content discoverable for agents")
pos_search_project(content_type="standards", query="RAG content authoring keywords query hooks")
pos_search_project(content_type="standards", query="avoid generic terms keyword pollution")
pos_search_project(content_type="standards", query="front-load critical information TL;DR")
```

**Query for query patterns (how agents search):**
```python
pos_search_project(content_type="standards", query="query construction content-specific phrases")
pos_search_project(content_type="standards", query="semantic search patterns effectiveness")
pos_search_project(content_type="standards", query="avoid generic questions use unique values")
```

**Why query BOTH perspectives:**
- **Content side:** Learn how to structure discoverable content
- **Query side:** Understand how agents will search for it
- **Together:** Avoid keyword pollution, use content-specific phrases

**Apply what you discover:**

1. **Add keyword line** with content-specific terms (not generic)
   - ✅ "three phase development, conversational design, spec implementation"
   - ❌ "workflow, process, development" (too generic, pollutes results)

2. **Include query hooks** (20+ natural questions your standard answers)

3. **Front-load TL;DR** with high keyword density

4. **Use specific headers** that match how agents think
   - ✅ "How to Build Features in prAxIs OS"
   - ❌ "Usage" or "Examples"

5. **Test from multiple angles** (Step 6)

**Validation:**
- [ ] Queried for RAG content optimization guidance
- [ ] Queried for query construction patterns
- [ ] Understand both how to write AND how agents search
- [ ] Keywords are content-specific (won't pollute other standards)
- [ ] Headers match natural agent queries
- [ ] TL;DR section has high keyword density
- [ ] Query hooks section included (20+ questions)

### Step 6: Test Queries → Validate Findability

**Test that your standard returns for the RIGHT queries and doesn't pollute others:**

**Should return your standard (top 3 results):**
```python
# Test 5+ natural queries agents would use for YOUR content
pos_search_project(content_type="standards", query="[your content-specific phrase 1]")
pos_search_project(content_type="standards", query="[your content-specific phrase 2]")
pos_search_project(content_type="standards", query="[natural question from your query hooks]")
pos_search_project(content_type="standards", query="[domain-specific term unique to your topic]")
pos_search_project(content_type="standards", query="[problem your standard solves]")
```

**Should NOT return your standard:**
```python
# Test that generic terms don't cause pollution
pos_search_project(content_type="standards", query="workflow")  # Should return workflow standards, not yours
pos_search_project(content_type="standards", query="testing")   # Should return test standards, not yours
pos_search_project(content_type="standards", query="process")   # Should return process standards, not yours
```

**If your standard returns for generic queries it shouldn't:**
→ You're polluting other standards' results
→ Remove generic keywords from your keyword line
→ Use more content-specific phrases
→ Refine Step 5 and retest

**CRITICAL: Test from 5+ different perspectives to ensure comprehensive discoverability**

```python
# Test multi-angle discovery (thorough, systematic approach)

# Angle 1: Direct "how to" query
pos_search_project(content_type="standards", query="how to [do what standard covers]")

# Angle 2: "What is" conceptual query  
pos_search_project(content_type="standards", query="what is [main concept]")

# Angle 3: Best practices query
pos_search_project(content_type="standards", query="[topic] best practices")

# Angle 4: Problem-solving query
pos_search_project(content_type="standards", query="when should I [use this]")

# Angle 5: Anti-pattern query
pos_search_project(content_type="standards", query="[topic] anti-patterns")

# Should return your new standard in top 3 results for ALL angles
```

**If not discoverable from ALL angles:**
- Add more query hooks covering missing angles
- Increase keyword density for underperforming queries
- Add explicit "Questions This Answers" entries for missing angles
- Update headers to include missing query phrasings

**Validation criteria:** Content MUST return in top 3 for minimum 5 different natural query phrasings.

### Step 7: Place in Correct Directory

**Standards location**: `universal/standards/[category]/[standard-name].md`

**Categories:**
- `ai-assistant/` - How AI agents should work
- `ai-safety/` - Safety constraints and rules
- `architecture/` - Architectural patterns
- `concurrency/` - Concurrency standards
- `database/` - Database patterns
- `documentation/` - Documentation standards
- `failure-modes/` - Error handling patterns
- `installation/` - Installation/upgrade procedures
- `meta-workflow/` - Framework creation/maintenance
- `performance/` - Performance optimization
- `security/` - Security patterns
- `testing/` - Testing standards
- `workflows/` - Workflow system standards

**Create new category** if none fit (but query first to see if it should merge with existing).

### Step 8: Test with Real Usage

**Dogfooding**: Use the standard yourself immediately.

**Check:**
- Can you follow the standard easily?
- Does it solve the problem it intended to solve?
- Are the examples clear?
- Is it discoverable through natural queries?

**Iterate** based on actual usage.

### Step 9: Ship to `universal/`

Commit to `universal/standards/[category]/[name].md`.

File watcher will detect and reindex within 30 seconds.

Verify it's indexed:
```python
pos_search_project(content_type="standards", query="[your standard topic]")
```

---

## What Makes a Good Standard?

Quality standards ensure standards are effective, usable, and discoverable.

A good standard must:

- [ ] **Solve a real problem** - Based on actual experience, not theoretical
- [ ] **Be actionable** - Clear what to do, not vague philosophy
- [ ] **Include examples** - Show good vs bad concretely
- [ ] **Be RAG-optimized** - Returns in top 3 for natural queries from 5+ angles:
  - [ ] Has TL;DR section first with high keyword density
  - [ ] Has "Questions This Answers" section (10+ questions)
  - [ ] Uses query-oriented headers ("How to X?" not "Usage")
  - [ ] Has "When to Query This Standard" table with example queries
  - [ ] Has "Keywords for search" line with explicit search terms
  - [ ] Has cross-references with query patterns, not just file links
  - [ ] Tested and discoverable from minimum 5 different query phrasings
- [ ] **Have checklist** - Concrete compliance criteria
- [ ] **Document anti-patterns** - Show common mistakes
- [ ] **Link to related standards** - Part of coherent system with query workflows
- [ ] **Be maintainable** - Single source of truth, no duplication
- [ ] **Be testable** - Can verify compliance programmatically

---

## What Standards Creation Anti-Patterns Should I Avoid?

These common mistakes reduce standard effectiveness. Recognize and avoid them.

### Anti-Pattern 1: Vague Philosophy

**Wrong:**
```markdown
# Excellence Standard

Always strive for excellence in your code.
Be thoughtful and careful.
```

**Right:**
```markdown
# Production Code Checklist

Code must:
- [ ] Have Sphinx-style docstrings
- [ ] Include type hints for all parameters
- [ ] Handle errors with specific exception types
[...concrete, checkable criteria]
```

---

### Anti-Pattern 2: Creating Specs When You Need Standards

**Wrong thinking**: "I need to design a new testing approach" → Create spec

**Right thinking**: "I need to define how we test" → Create standard

**Test**: Does this define HOW to work (standard) or WHAT to build (spec)?

---

### Anti-Pattern 3: Duplicating Existing Standards

**Wrong**: Creating `python-testing-best-practices.md` when `testing/test-pyramid.md` already exists

**Right**: Update existing standard or link to it

**Always query first**:
```python
pos_search_project(content_type="standards", query="[topic you're covering]")
```

---

### Anti-Pattern 4: Not RAG-Optimizing

**Wrong**: Writing for human readers who will read top-to-bottom

```markdown
# My Standard

## Introduction
[Long introduction...]

## Background
[Historical context...]

## The Actual Content
[Useful stuff buried on line 300]
```

**Why it fails:**
- AI queries won't return relevant chunks
- Critical info buried too deep
- No query hooks for discovery
- Generic headers don't rank
- Not testable for discoverability

**Right**: Writing for AI agents with RAG optimization

```markdown
# My Standard

## 🎯 TL;DR - My Standard Quick Reference

**Keywords for search**: [topic], [how to X], [what is Y]

**Core Principle:** [One sentence]

**[Key Points]:**
1. Point 1
2. Point 2

---

## ❓ Questions This Answers

1. "How to do X?"
2. "What is Y?"
...

---

## 🎯 Purpose

[Content continues with query-oriented headers...]

## What Is [Topic]?
## How to [Action]?
## What Are [Topic] Examples?
```

**Requirements (ALL must be met):**
- [ ] **TL;DR section first** - High keyword density, front-loaded critical info
- [ ] **"Questions This Answers" section** - 10+ natural language questions
- [ ] **Query-oriented headers** - "How to X?" not "Usage", "What is Y?" not "Overview"
- [ ] **"When to Query This Standard" table** - Scenarios with example queries
- [ ] **Cross-references with queries** - `pos_search_project(content_type="standards", query="[topic]")` not just file links
- [ ] **Keywords for search line** - Explicit list of search terms
- [ ] **Multi-angle tested** - Verified discoverable from 5+ different query phrasings

**Follow**: `standards/ai-assistant/rag-content-authoring.md`

**Test with:**
```python
# Test 5+ different angles
pos_search_project(content_type="standards", query="how to [primary approach]")
pos_search_project(content_type="standards", query="what is [main concept]")
pos_search_project(content_type="standards", query="[action] best practices")
pos_search_project(content_type="standards", query="when should I [scenario]")
pos_search_project(content_type="standards", query="[topic] anti-patterns")
```

**If content doesn't return in top 3 for ALL test queries → Not properly optimized**

---

## What Examples of Good Standards Exist?

Learn from these exemplar prAxIs OS standards that demonstrate best practices.

Study these as templates:

- `standards/ai-safety/production-code-checklist.md` - Comprehensive checklist format
- `standards/testing/test-pyramid.md` - Clear principles with examples
- `standards/workflows/workflow-construction-standards.md` - Structural guidelines
- `standards/documentation/rag-content-authoring.md` - RAG optimization

---

## How to Maintain Standards?

Standards require ongoing maintenance to remain effective and relevant.

### When to Update Standards

Update when:
- Technology/tools change (e.g., new testing framework)
- Pattern proves insufficient through usage
- Better approach discovered through dogfooding
- Discoverability issues found (agents can't find it)

### How to Update Standards

1. **Test current discoverability**:
   ```python
   pos_search_project(content_type="standards", query="[topic]")
   ```

2. **Make updates**:
   - Preserve core principles
   - Update examples/tools/syntax
   - Add new anti-patterns discovered
   - Improve query hooks if needed

3. **Test new discoverability**:
   Same queries should still return the standard

4. **Commit to `universal/`**:
   File watcher reindexes automatically

### Deprecating Standards

If standard is obsolete:
- **Don't delete immediately** - May break existing queries
- **Add deprecation notice** at top:
  ```markdown
  ## ⚠️ DEPRECATED
  
  This standard is superseded by [new-standard.md].
  
  Use pos_search_project(content_type="standards", query="[new topic]") for current guidance.
  ```
- **Keep for 3+ months** to allow transition
- **Then archive** to `deprecated/` directory

---

## How to Measure Standard Effectiveness?

Track these metrics to measure standard adoption and effectiveness.

Track effectiveness:

- **Discoverability**: Do natural queries return this standard?
- **Usage**: Do agents follow this standard in practice?
- **Quality impact**: Does code/work improve measurably?
- **Maintenance**: How often does it need updates?

**Good standard indicators:**
- Returns in top 3-5 for relevant queries
- Agents naturally follow it without prompting
- Quality metrics improve (test coverage, linter scores, etc.)
- Rarely needs updates (principles are stable)

---

## 📞 Questions?

**How do I know if something should be a standard vs a spec?**
→ Ask: "Is this HOW to work (standard) or WHAT to build (spec)?"

**Can I create a standard without formal approval?**
→ Yes! prAxIs OS is dogfooded. Experience a need → Create standard → Test it → Ship it.

**What if my standard conflicts with an existing standard?**
→ Query to find existing: `pos_search_project(content_type="standards", query="[topic]")`. Update existing or document why new one is needed.

**How do I test if my standard is being followed?**
→ Review code/work for compliance. Add linter rules or automated checks if possible.

**What if my standard becomes obsolete?**
→ Add deprecation notice, point to replacement, keep for 3 months, then archive.

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Creating standard** | `pos_search_project(content_type="standards", query="how to create standard")` |
| **Standard structure** | `pos_search_project(content_type="standards", query="standard structure template")` |
| **Quality criteria** | `pos_search_project(content_type="standards", query="what makes good standard")` |
| **When to create** | `pos_search_project(content_type="standards", query="when to write standard")` |
| **Standards vs specs** | `pos_search_project(content_type="standards", query="standard vs spec")` |
| **Maintenance** | `pos_search_project(content_type="standards", query="maintain standards")` |
| **Anti-patterns** | `pos_search_project(content_type="standards", query="standards creation mistakes")` |
| **Examples** | `pos_search_project(content_type="standards", query="good standard examples")` |

---

## 🔗 Related Standards

**Query workflow for creating standards:**

1. **Start with creation process** → `pos_search_project(content_type="standards", query="how to create standard")` (this document)
2. **Learn RAG optimization** → `pos_search_project(content_type="standards", query="RAG content authoring")` → `standards/documentation/rag-content-authoring.md`
3. **Understand specs** → `pos_search_project(content_type="standards", query="creating specs")` → `usage/creating-specs.md`
4. **Learn command language** → `pos_search_project(content_type="standards", query="command language")` → `standards/meta-workflow/command-language.md`

**By Category:**

**Documentation:**
- `standards/documentation/rag-content-authoring.md` - RAG optimization → `pos_search_project(content_type="standards", query="RAG content authoring")`
- `standards/documentation/readme-templates.md` - README patterns → `pos_search_project(content_type="standards", query="README templates")`
- `standards/documentation/code-comments.md` - Comment guidelines → `pos_search_project(content_type="standards", query="code comments")`

**Meta-Framework:**
- `standards/meta-workflow/command-language.md` - Command symbols → `pos_search_project(content_type="standards", query="command language")`
- `standards/meta-workflow/three-tier-architecture.md` - Content organization → `pos_search_project(content_type="standards", query="three tier architecture")`
- `standards/meta-workflow/validation-gates.md` - Quality gates → `pos_search_project(content_type="standards", query="validation gates")`

**Usage:**
- `usage/creating-specs.md` - Spec creation guide → `pos_search_project(content_type="standards", query="creating specs")`
- `usage/operating-model.md` - prAxIs OS principles → `pos_search_project(content_type="standards", query="operating model")`

---

**Remember**: Standards emerge from real experience. If you hit a problem that needs consistency, create the standard. Don't wait for permission. Dogfood it. Ship it.

