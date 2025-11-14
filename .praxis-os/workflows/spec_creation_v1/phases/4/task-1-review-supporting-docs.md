# Task 1: Review Supporting Documentation

**Phase:** 4 (Implementation Guidance)  
**Purpose:** Re-read design doc for code examples and patterns  
**Estimated Time:** 5-8 minutes (MOST CRITICAL PHASE FOR RE-READING)

---

## 🎯 Objective

Re-read relevant sections of the supporting documentation to extract ACTUAL code examples and patterns. Do NOT work from memory - actively re-read and COPY concrete implementation details from source.

---

## Prerequisites

🛑 EXECUTE-NOW: Phase 3 must be completed

Supporting docs must be in `supporting-docs/` directory.

---

## Steps

### Step 1: Locate Supporting Documentation

```bash
ls -la supporting-docs/
cat supporting-docs/INDEX.md
```

Identify primary design document(s).

### Step 2: Re-Read Code Examples Sections

⚠️ CRITICAL: COPY code examples, don't paraphrase from memory

**Sections to review:**
- [ ] "Code Examples" or "Implementation" section
- [ ] "Patterns" or "Best Practices" section
- [ ] "Anti-Patterns" or "Pitfalls" section
- [ ] "Configuration" or "Setup" sections
- [ ] "Library Usage" examples (if any)

**Extract and COPY:**
- **Actual code snippets** (preserve syntax exactly)
- Library import statements
- Class/function signatures
- Configuration examples (YAML, JSON)
- Comments explaining WHY
- Anti-pattern examples

**For each code example, note:**
- What library is being used?
- What's the exact method call syntax?
- What parameters are required?
- What does each parameter do?

### Step 3: Search for Specific Library Usage

⚠️ SUPER CRITICAL: Find actual API calls

```bash
# Search for code blocks in design doc
grep -A 10 "```python" supporting-docs/*.md
grep -A 10 "```yaml" supporting-docs/*.md
grep -A 10 "```typescript" supporting-docs/*.md
```

Look for:
- Database connection examples
- API client initialization
- Configuration file structure
- Error handling patterns

### Step 4: Verify Code Understanding

Answer these questions from the source material:
- What's the actual syntax for [critical operation X]?
- What libraries are actually being imported?
- What are the exact parameter names?
- What configuration fields are required?

📊 COUNT-AND-DOCUMENT: Code examples found [number], patterns identified [number]

---

## Completion Criteria

🛑 VALIDATE-GATE: Task Completion

Before proceeding:
- [ ] Primary design doc re-read for ALL code examples ✅/❌
- [ ] Code snippets COPIED (not paraphrased) ✅/❌
- [ ] Library syntax extracted with exact parameters ✅/❌
- [ ] Configuration examples extracted ✅/❌
- [ ] Ready to create implementation.md with REAL code ✅/❌

🚨 FRAMEWORK-VIOLATION: Writing code patterns from memory

Do NOT proceed if you haven't actually re-read and COPIED code examples. Writing patterns from memory creates generic, unusable guidance. Copy actual working syntax from design doc.

**This is the MOST CRITICAL review task - take your time!**

---

## Next Task

🎯 NEXT-MANDATORY: [task-2-code-patterns.md](task-2-code-patterns.md)

Continue to document code patterns using COPIED examples.

