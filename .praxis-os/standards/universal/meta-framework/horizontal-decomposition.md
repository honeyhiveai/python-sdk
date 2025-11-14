# Horizontal Decomposition - Universal Meta-Framework Pattern

**Timeless pattern for breaking complexity into focused modules**

---

## 🎯 TL;DR - Horizontal Decomposition Quick Reference

**Keywords for search**: horizontal decomposition, task decomposition, file size optimization, LLM context management, workflow decomposition, breaking down tasks, modular workflows, AI file size limits

**Core Principle:** Break complex workflows horizontally into small, focused files (≤100 lines) rather than vertically layering abstraction.

**The Problem:** Large monolithic files (2000 lines) → 90%+ context use → <70% attention quality → 60-70% success
**The Solution:** Horizontal decomposition (30 × 65 lines) → 15-25% context use → 95%+ attention quality → 85-95% success

**Decomposition Strategies:**

1. **By Workflow Phase**
   - Break workflow into sequential phases
   - Each phase = one directory with multiple tasks
   - Example: Setup → Analysis → Generation → Validation

2. **By Single Responsibility**
   - One clear purpose per file
   - Task 1: Parse schema (70 lines)
   - Task 2: Generate tests (85 lines)
   - Task 3: Validate output (60 lines)

3. **By Data Type**
   - Decompose by what's being processed
   - Example: users.md, products.md, orders.md

4. **By Complexity**
   - Simple tasks stay together (30 lines)
   - Complex tasks get own file (100 lines)

**Target File Sizes:**
- **Optimal:** ≤100 lines (95%+ attention quality)
- **Acceptable:** 100-170 lines (85-95% attention)
- **Warning:** 170-500 lines (70-85% attention)
- **Failure:** >500 lines (<70% attention)

**Key Pattern:**
```
Large Task (2000 lines)
  ↓ Break into Phases (8 × 250 lines)
  ↓ Break into Tasks (30 × 65 lines)
  ↓ Result: 15-25% context use, 95%+ quality
```

**Horizontal vs Vertical:**
- ❌ **Vertical** - Layered abstractions (models → services → controllers)
- ✅ **Horizontal** - Focused modules by workflow step (task-1 → task-2 → task-3)

**Benefits:**
- 3-4x improvement in success rate
- Minimal context use (15-25% vs 90%+)
- Focused attention per task
- Easier debugging and maintenance
- Parallel execution possible

---

## ❓ Questions This Answers

1. "How do I break down complex AI workflows?"
2. "What is horizontal decomposition?"
3. "Why are my AI tasks failing with large files?"
4. "What file size is optimal for AI?"
5. "How do I prevent AI context overflow?"
6. "What is the difference between horizontal and vertical decomposition?"
7. "How do I structure workflow tasks?"
8. "What decomposition strategies exist?"
9. "How small should task files be?"
10. "How do I improve AI attention quality?"

---

## What Is Horizontal Decomposition?

**Breaking complex workflows across focused, single-responsibility modules** rather than vertically layering abstraction.

**Core Insight**: LLMs have limited context. Break work horizontally into small pieces, not vertically into layers.

---

## What Is the Monolithic Problem?

Large, complex files cause AI attention degradation and execution failures.

```
Large Complex Task (2000 lines)
  ↓
AI reads entire file
  ↓
Context at 90%+ utilization
  ↓
Attention quality <70%
  ↓
Failures, shortcuts, incomplete work
```

**Result**: 60-70% success rate

---

## How Does Decomposition Solve the Problem?

Breaking large tasks into small files optimizes AI attention and dramatically improves success rates.

```
Large Task (2000 lines)
  ↓
Break into Phases (8 × 250 lines)
  ↓
Break into Tasks (30 × 65 lines)
  ↓
Context at 15-25% utilization
  ↓
Attention quality 95%+
  ↓
Consistent, complete execution
```

**Result**: 85-95% success rate

---

## What Decomposition Strategies Should I Use?

Choose the strategy that best matches your workflow's natural structure.

### Strategy 1: By Workflow Phase

```
Test Generation (2000 lines)
  ↓
Phase 0: Setup (200 lines)
Phase 1: Analysis (400 lines)
Phase 2: Generation (800 lines)
Phase 3: Validation (400 lines)
Phase 4: Refinement (200 lines)
```

### Strategy 2: By Single Responsibility

```
Phase 2: Generation (800 lines)
  ↓
Task 1: Setup generation (80 lines)
Task 2: Unit tests (120 lines)
Task 3: Integration tests (100 lines)
Task 4: Edge cases (90 lines)
Task 5: Documentation (85 lines)
```

### Strategy 3: By Execution Context

```
Task: Write Tests (350 lines)
  ↓
Step 1: Analyze function (75 lines)
Step 2: Generate test (65 lines)
Step 3: Validate test (70 lines)
Step 4: Refine test (60 lines)
```

---

## What Are the Target File Sizes?

File size directly impacts AI attention quality. Follow these targets for optimal results.

| Tier | Size | Purpose | Count |
|------|------|---------|-------|
| Entry | 100-150 lines | Framework overview | 1 |
| Phase | 200-300 lines | Phase introduction | 5-8 |
| Task | 60-100 lines | Execution instructions | 20-40 |
| Step | 30-60 lines | Granular actions | Optional |

**Key**: Most execution happens in ≤100 line task files

---

## How to Implement Horizontal Decomposition?

Follow this systematic pattern to decompose any complex workflow.

### Pattern 1: Top-Down Breakdown

```
1. Define Framework (150 lines)
   - What problem does this solve?
   - What are the major phases?

2. Break into Phases (8 × 200 lines)
   - Phase 0: Setup
   - Phase 1: Analysis
   - Phase 2: Generation
   - ...

3. Break Phases into Tasks (40 × 70 lines)
   - Phase 1 → Tasks 1-5
   - Phase 2 → Tasks 1-8
   - ...

4. Validate Sizes
   - 95%+ tasks ≤100 lines
```

### Pattern 2: Single Responsibility Test

**Ask**: Does this file do ONE thing?

✅ **Good**: `task-2-generate-unit-tests.md`
- Single responsibility: Generate unit tests
- Clear scope
- No mixing

❌ **Bad**: `task-2-generate-and-validate-tests.md`
- Two responsibilities
- Mixed concerns
- Should be split

---

## What Is Horizontal vs Vertical Decomposition?

Understanding the difference is critical for choosing the right approach for AI workflows.

### ❌ Vertical Decomposition (Abstraction Layers)

```
Layer 1: High-level strategy (abstract)
Layer 2: Mid-level tactics (abstract)
Layer 3: Low-level implementation (concrete)

Problem: AI must understand all layers simultaneously
```

### ✅ Horizontal Decomposition (Sequential Tasks)

```
Task 1: Setup → Task 2: Analysis → Task 3: Generation → Task 4: Validation

Benefit: AI reads ONE task at a time, focused context
```

---

## What Are the Benefits of Horizontal Decomposition?

Horizontal decomposition delivers measurable improvements across all quality metrics.

### Context Efficiency
- **Before**: 75-90% utilization (overflow)
- **After**: 15-25% utilization (optimal)
- **Improvement**: 3-4x better

### Attention Quality
- **Before**: <70% on large files
- **After**: 95%+ on small files
- **Improvement**: 25%+ better

### Maintenance
- **Before**: Edit 500-line monolith
- **After**: Edit 70-line task file
- **Improvement**: Focused, surgical changes

---

## How to Validate Decomposition Quality?

Use these metrics to ensure your decomposition meets prAxIs OS standards.

```bash
# Check task file sizes
find phases/ -name "*.md" -exec sh -c '
  lines=$(wc -l < "$1")
  if [ $lines -gt 100 ]; then
    echo "❌ $lines lines: $1 (split recommended)"
  else
    echo "✅ $lines lines: $1"
  fi
' _ {} \;

# Should see 95%+ ✅
```

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Large file failures** | `pos_search_project(content_type="standards", query="AI failing large files")` |
| **Breaking down workflows** | `pos_search_project(content_type="standards", query="horizontal decomposition")` |
| **Optimal file size** | `pos_search_project(content_type="standards", query="optimal file size AI")` |
| **Context overflow** | `pos_search_project(content_type="standards", query="AI context overflow")` |
| **Task structure** | `pos_search_project(content_type="standards", query="how to structure tasks")` |
| **Decomposition strategies** | `pos_search_project(content_type="standards", query="task decomposition strategies")` |
| **Workflow organization** | `pos_search_project(content_type="standards", query="workflow organization")` |
| **File size limits** | `pos_search_project(content_type="standards", query="AI file size limits")` |

---

## 🔗 Related Standards

**Query workflow for complete decomposition understanding:**

1. **Start with decomposition** → `pos_search_project(content_type="standards", query="horizontal decomposition")` (this document)
2. **Learn framework principles** → `pos_search_project(content_type="standards", query="framework creation principles")` → `standards/meta-workflow/framework-creation-principles.md`
3. **Understand architecture** → `pos_search_project(content_type="standards", query="three-tier architecture")` → `standards/meta-workflow/three-tier-architecture.md`
4. **Apply validation** → `pos_search_project(content_type="standards", query="validation gates")` → `standards/meta-workflow/validation-gates.md`

**By Category:**

**Meta-Framework:**
- `standards/meta-workflow/framework-creation-principles.md` - Core principles → `pos_search_project(content_type="standards", query="framework creation principles")`
- `standards/meta-workflow/three-tier-architecture.md` - README/phase/task structure → `pos_search_project(content_type="standards", query="three-tier architecture")`
- `standards/meta-workflow/command-language.md` - Binding instructions → `pos_search_project(content_type="standards", query="command language")`
- `standards/meta-workflow/validation-gates.md` - Quality checkpoints → `pos_search_project(content_type="standards", query="validation gates")`

**Workflows:**
- `standards/workflows/workflow-construction-standards.md` - Building workflows → `pos_search_project(content_type="standards", query="workflow construction")`

**Architecture:**
- `standards/architecture/solid-principles.md` - Single Responsibility Principle → `pos_search_project(content_type="standards", query="SOLID principles")`
- `standards/architecture/separation-of-concerns.md` - Concern separation → `pos_search_project(content_type="standards", query="separation of concerns")`

---

**Horizontal decomposition is the key to scaling AI workflows. Break work into focused, digestible pieces for consistent results.**
