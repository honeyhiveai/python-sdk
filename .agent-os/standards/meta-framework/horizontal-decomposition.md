# Horizontal Decomposition - Universal Meta-Framework Pattern

**Timeless pattern for breaking complexity into focused modules**

## What Is Horizontal Decomposition?

**Breaking complex workflows across focused, single-responsibility modules** rather than vertically layering abstraction.

**Core Insight**: LLMs have limited context. Break work horizontally into small pieces, not vertically into layers.

---

## The Monolithic Problem

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

## The Decomposition Solution

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

## Decomposition Strategies

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

## Target File Sizes

| Tier | Size | Purpose | Count |
|------|------|---------|-------|
| Entry | 100-150 lines | Framework overview | 1 |
| Phase | 200-300 lines | Phase introduction | 5-8 |
| Task | 60-100 lines | Execution instructions | 20-40 |
| Step | 30-60 lines | Granular actions | Optional |

**Key**: Most execution happens in ≤100 line task files

---

## Implementation Pattern

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

## Horizontal vs Vertical

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

## Benefits

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

## Validation

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

## References

- [Framework Creation Principles](framework-creation-principles.md)
- [Three-Tier Architecture](three-tier-architecture.md)

---

**Horizontal decomposition is the key to scaling AI workflows. Break work into focused, digestible pieces for consistent results.**
