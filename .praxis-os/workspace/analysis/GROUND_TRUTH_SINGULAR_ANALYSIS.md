# Ground Truth Singular Everywhere: Impact Analysis

**Date**: November 3, 2025  
**Question**: Should we use `ground_truth` (singular) everywhere instead of `ground_truths` (plural)?  
**Current Status**: SDK is at v0.1.0rc3 (release candidate)

---

## Executive Summary

**Recommendation**: ✅ **YES - Change to singular `ground_truth` everywhere BEFORE v1.0 release**

**Reasoning**:
1. ✅ SDK is still in release candidate (0.1.0rc3) - **best time for breaking changes**
2. ✅ Fixes critical bug where ground truth data is inaccessible to metrics/UI
3. ✅ Aligns with backend's universal `ground_truth` (singular) convention
4. ✅ Simpler mental model - one naming convention, not two
5. ⚠️ Breaking change for early adopters, but manageable with migration guide

---

## Impact Analysis

### Files That Would Change

**Total**: 376 occurrences across 34 files need updating

#### 1. Source Code (10 files)
- `src/honeyhive/experiments/core.py` (30 occurrences)
  - Function parameters
  - Dataset key references
  - Docstrings
  - Internal logic

#### 2. Documentation (12 files - 90+ occurrences)
- `docs/tutorials/05-run-first-experiment.rst` (15 occurrences)
- `docs/how-to/evaluation/creating-evaluators.rst` (35 occurrences)
- `docs/how-to/evaluation/running-experiments.rst` (19 occurrences)
- `docs/how-to/evaluation/dataset-management.rst` (6 occurrences)
- `docs/how-to/integrations/strands.rst` (4 occurrences)
- `docs/how-to/evaluation/server-side-evaluators.rst` (1 occurrence)
- `docs/how-to/evaluation/multi-step-experiments.rst` (1 occurrence)
- `docs/how-to/evaluation/best-practices.rst` (1 occurrence)
- `docs/how-to/evaluation/troubleshooting.rst` (3 occurrences)
- Other documentation files

#### 3. Tests (7 files - 56 occurrences)
- `tests/integration/test_experiments_integration.py` (15 occurrences)
- `tests/unit/test_experiments_immediate_fixes.py` (12 occurrences)
- `tests/integration/test_v1_immediate_ship_requirements.py` (8 occurrences)
- `tests/unit/test_experiments_core.py` (9 occurrences)
- Other test files

#### 4. Examples (2 files)
- `examples/eval_example.py` (2 occurrences)
- Other example files

---

## Breaking Changes for Users

### What Users Need to Change

#### 1. Dataset Format

**BEFORE (plural)**:
```python
dataset = [
    {
        "inputs": {"query": "What is 2+2?"},
        "ground_truths": {"answer": "4"}  # ❌ Plural
    }
]
```

**AFTER (singular)**:
```python
dataset = [
    {
        "inputs": {"query": "What is 2+2?"},
        "ground_truth": {"answer": "4"}  # ✅ Singular
    }
]
```

#### 2. Evaluator Function Signatures

**BEFORE (plural)**:
```python
def my_evaluator(outputs, inputs, ground_truths):  # ❌ Plural
    expected = ground_truths.get("answer", "")
    actual = outputs.get("answer", "")
    return {"score": 1.0 if actual == expected else 0.0}
```

**AFTER (singular)**:
```python
def my_evaluator(outputs, inputs, ground_truth):  # ✅ Singular
    expected = ground_truth.get("answer", "")
    actual = outputs.get("answer", "")
    return {"score": 1.0 if actual == expected else 0.0}
```

#### 3. Legacy Function Signatures (Deprecated Pattern)

**BEFORE (plural)**:
```python
# Old pattern (deprecated but still in docs)
def old_style_function(inputs, ground_truths):
    return process(inputs, ground_truths)
```

**AFTER (singular)**:
```python
# Old pattern (deprecated but still in docs)
def old_style_function(inputs, ground_truth):
    return process(inputs, ground_truth)
```

### User Migration Effort

**Estimated effort per user**:
- Small projects (1-5 evaluators): **15-30 minutes**
- Medium projects (5-20 evaluators): **1-2 hours**
- Large projects (20+ evaluators): **2-4 hours**

**Migration steps**:
1. Find-replace `ground_truths` → `ground_truth` in dataset definitions
2. Find-replace `ground_truths` → `ground_truth` in evaluator function signatures
3. Update function bodies to use new parameter name
4. Test evaluators

**Automation potential**: HIGH - Can provide a migration script

---

## Benefits of Singular Convention

### 1. ✅ **Consistency with Backend**

**Current Problem**: SDK uses plural, backend uses singular
- SDK sends: `feedback.ground_truths`
- Backend expects: `feedback.ground_truth`
- Result: Data lost, metrics fail, UI broken

**After Fix**: Perfect alignment
- SDK sends: `feedback.ground_truth`
- Backend expects: `feedback.ground_truth`
- Result: Everything works ✅

### 2. ✅ **Simpler Mental Model**

**Current (confusing)**:
- API models: `ground_truth` (singular)
- Dataset format: `ground_truths` (plural)
- User evaluators: `ground_truths` (plural)
- Built-in evaluators: `ground_truth` (singular)
- Backend storage: `ground_truth` (singular)
- UI display: `ground_truth` (singular)

**After singular everywhere (clear)**:
- Everything: `ground_truth` (singular) ✅

### 3. ✅ **No Conversion Layer Needed**

**Current**: SDK must convert between plural and singular
```python
# Extra conversion logic
if ground_truths is not None:
    update_data["feedback"] = {"ground_truth": ground_truths}  # Convert plural var to singular key
```

**After**: Direct passthrough
```python
# No conversion needed
if ground_truth is not None:
    update_data["feedback"] = {"ground_truth": ground_truth}  # Consistent everywhere
```

### 4. ✅ **Matches Industry Patterns**

Most ML/AI frameworks use singular for "ground truth":
- **Hugging Face**: `ground_truth` parameter
- **LangChain**: `ground_truth` in evaluators
- **OpenAI Evals**: `ideal` (singular concept)
- **Weights & Biases**: `ground_truth` column

### 5. ✅ **Semantically Correct**

"Ground truth" is conceptually singular:
- It's the ONE correct/expected answer for a datapoint
- Even if the answer has multiple fields, it's still ONE ground truth object
- Compare: `"inputs": {...}` is singular even though it has multiple fields

---

## Risks and Mitigation

### Risk 1: Breaking Early Adopters

**Who is affected**:
- Internal Nationwide team (known)
- Any other early 0.1.0rc3 users (likely small number)

**Mitigation**:
1. ✅ **Timing**: We're at RC3, not v1.0 - breaking changes expected
2. ✅ **Migration Guide**: Provide clear, step-by-step guide
3. ✅ **Migration Script**: Automated find-replace tool
4. ✅ **Deprecation Warning**: Add runtime warning for plural form (optional)
5. ✅ **Release Notes**: Prominently document the change

### Risk 2: Documentation Everywhere

**Scope**: 90+ documentation changes needed

**Mitigation**:
1. ✅ **Automated**: Most changes are simple find-replace
2. ✅ **Validation**: Run Sphinx build to catch errors
3. ✅ **Test Code Blocks**: All examples are tested, so changes will be validated
4. ✅ **Examples**: Update all examples to new pattern

### Risk 3: Tests Need Updating

**Scope**: 56 test occurrences to update

**Mitigation**:
1. ✅ **Test Failures**: Will immediately catch any missed updates
2. ✅ **CI/CD**: Pre-commit hooks will validate changes
3. ✅ **Coverage**: Existing tests ensure no regression

---

## Alternative: Backward Compatibility (NOT RECOMMENDED)

### Option: Support Both Plural and Singular

**Approach**: Accept both `ground_truths` and `ground_truth`, convert to singular internally

```python
def normalize_ground_truth(datapoint: Dict[str, Any]) -> Dict[str, Any]:
    """Convert plural ground_truths to singular ground_truth."""
    if "ground_truths" in datapoint and "ground_truth" not in datapoint:
        datapoint["ground_truth"] = datapoint.pop("ground_truths")
    return datapoint
```

**Pros**:
- ✅ No breaking change
- ✅ Users can migrate at their own pace

**Cons**:
- ❌ Two ways to do the same thing (violates "one obvious way")
- ❌ Confusing for new users ("which one do I use?")
- ❌ Documentation must explain both patterns
- ❌ More code to maintain
- ❌ Harder to deprecate later
- ❌ Evaluator signatures still need two parameter names: `ground_truth` OR `ground_truths`?

**Recommendation**: ❌ **DON'T DO THIS** - Clean break is better than extended dual-support

---

## Implementation Plan

### Phase 1: SDK Code Changes (Day 1)

1. ✅ **Update core evaluate() function**
   - `src/honeyhive/experiments/core.py`: All plural → singular
   - Internal variable names: `ground_truths` → `ground_truth`
   - Dataset key access: `datapoint.get("ground_truths")` → `datapoint.get("ground_truth")`
   - Function parameters: `ground_truths: Optional[Any]` → `ground_truth: Optional[Any]`

2. ✅ **Update session enrichment**
   - Change: `{"ground_truths": ground_truths}` → `{"ground_truth": ground_truth}`
   - This fixes the critical bug ✅

3. ✅ **Update docstrings**
   - All function/class docstrings mentioning `ground_truths`

### Phase 2: Tests (Day 1)

1. ✅ **Unit tests**: Update all test datasets and evaluators
   - `tests/unit/test_experiments_core.py`
   - `tests/unit/test_experiments_immediate_fixes.py`

2. ✅ **Integration tests**: Update all test datasets
   - `tests/integration/test_experiments_integration.py`
   - `tests/integration/test_v1_immediate_ship_requirements.py`

3. ✅ **Run full test suite**: Verify all passing

### Phase 3: Documentation (Day 1-2)

1. ✅ **Tutorial update**
   - `docs/tutorials/05-run-first-experiment.rst`: All dataset examples

2. ✅ **How-to guides update**
   - `docs/how-to/evaluation/creating-evaluators.rst`: All evaluator signatures
   - `docs/how-to/evaluation/running-experiments.rst`: All examples
   - `docs/how-to/evaluation/dataset-management.rst`: Dataset format examples
   - All other evaluation guides

3. ✅ **Reference docs**: Auto-generated from docstrings (covered in Phase 1)

### Phase 4: Examples (Day 2)

1. ✅ **Update example files**
   - `examples/eval_example.py`
   - Any other evaluation examples

2. ✅ **Test all examples**: Verify they run successfully

### Phase 5: Migration Guide (Day 2)

1. ✅ **Create migration guide**: `MIGRATION_GROUND_TRUTH.md`
   - What changed and why
   - Find-replace steps
   - Before/after code examples
   - Migration script (optional)

2. ✅ **Update CHANGELOG.md**
   - Add prominent breaking change notice
   - Link to migration guide

3. ✅ **Update docs/changelog.rst**
   - User-facing release notes

### Phase 6: Release (Day 3)

1. ✅ **Version bump**: 0.1.0rc3 → 0.1.0rc4 (or 1.0.0 if ready)
2. ✅ **Release notes**: Prominently document breaking change
3. ✅ **Communication**: Notify Nationwide team and any other early adopters
4. ✅ **GitHub release**: Create release with migration guide

---

## Migration Script (Optional Automation)

```python
#!/usr/bin/env python3
"""
Migrate ground_truths (plural) to ground_truth (singular) in evaluation code.

Usage:
    python migrate_ground_truth.py <directory>
"""

import re
import sys
from pathlib import Path

def migrate_file(file_path: Path) -> bool:
    """Migrate a single file. Returns True if changes were made."""
    content = file_path.read_text()
    original = content
    
    # 1. Dataset keys: "ground_truths" → "ground_truth"
    content = re.sub(
        r'"ground_truths"(\s*:)',
        r'"ground_truth"\1',
        content
    )
    
    # 2. Function parameters: ground_truths → ground_truth
    content = re.sub(
        r'\bground_truths\b',
        'ground_truth',
        content
    )
    
    if content != original:
        file_path.write_text(content)
        return True
    return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python migrate_ground_truth.py <directory>")
        sys.exit(1)
    
    directory = Path(sys.argv[1])
    if not directory.is_dir():
        print(f"Error: {directory} is not a directory")
        sys.exit(1)
    
    changed_files = []
    for py_file in directory.rglob("*.py"):
        if migrate_file(py_file):
            changed_files.append(py_file)
    
    print(f"\nMigrated {len(changed_files)} files:")
    for f in changed_files:
        print(f"  ✅ {f}")
    
    print("\n⚠️  IMPORTANT: Review changes and run your tests!")

if __name__ == "__main__":
    main()
```

---

## Comparison: Plural vs Singular

| Aspect | Plural (`ground_truths`) | Singular (`ground_truth`) |
|--------|-------------------------|---------------------------|
| **User DX** | Slightly more intuitive ("expected answers") | Industry standard, semantically correct |
| **Backend Match** | ❌ Mismatch causes bugs | ✅ Perfect alignment |
| **Conversion Layer** | ❌ Required | ✅ Not needed |
| **Built-in Evaluators** | ❌ Mismatch with user evaluators | ✅ Consistent everywhere |
| **Documentation** | ❌ Confusing (two patterns) | ✅ One clear pattern |
| **Mental Model** | ❌ Complex (plural in SDK, singular in backend) | ✅ Simple (singular everywhere) |
| **Breaking Change** | ✅ No (keep current) | ⚠️ Yes (but manageable at RC stage) |
| **Long-term Maintenance** | ❌ Higher (conversion logic forever) | ✅ Lower (no conversion) |

**Score**: Plural: 1/8 ✅, Singular: 7/8 ✅

---

## Decision Matrix

| Scenario | Use Singular? | Rationale |
|----------|---------------|-----------|
| **Pre-1.0 (current)** | ✅ **YES** | Best time for breaking change, fixes critical bug |
| **Post-1.0** | ⚠️ **Maybe** | Would need longer deprecation period, more communication |
| **Post-1.5** | ❌ **NO** | Too disruptive, would need dual-support forever |

**Current status**: 0.1.0rc3 → ✅ **PERFECT TIME TO CHANGE**

---

## Recommended Decision

### ✅ **YES - Change to singular `ground_truth` everywhere**

**Why now**:
1. Still in release candidate phase (0.1.0rc3)
2. Fixes critical bug blocking metrics and UI
3. Limited user base affected (early adopters)
4. Clean break better than perpetual dual-support
5. Aligns with backend and industry standards

**Action items**:
1. Implement all changes in one PR
2. Create comprehensive migration guide
3. Update all tests, docs, examples
4. Release as 0.1.0rc4 or 1.0.0
5. Communicate prominently to early adopters

**Timeline**: 2-3 days of focused work

---

## Conclusion

**Bottom line**: While changing to singular `ground_truth` is a breaking change, it's the **right decision** at this stage:

1. ✅ **Fixes critical bug** - Ground truth data actually works
2. ✅ **Perfect timing** - RC phase is for breaking changes
3. ✅ **Simpler long-term** - One convention, not two
4. ✅ **Manageable migration** - Clear steps, automation available
5. ✅ **Industry alignment** - Matches backend and ML frameworks

**Recommendation**: **Proceed with singular `ground_truth` everywhere before v1.0 release.**

---

**Next steps**: If approved, begin implementation immediately. Target completion: 2-3 days.

