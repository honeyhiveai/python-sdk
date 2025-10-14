# Phase 1: Method Verification

**Phase Number:** 1  
**Purpose:** CRITICAL - AST-based deep analysis to prevent 22% failure rate  
**Estimated Time:** 15-20 minutes  
**Total Tasks:** 7

---

## 🚨 Why This Phase is Critical

**V2's 22% failure rate traced directly to incomplete Phase 1 analysis:**
- Missing mock attributes → AttributeError failures
- Wrong function signatures → TypeError failures  
- Incomplete mocking → Integration leaks

**V3 prevents failures through systematic AST-based analysis**

---

## 🎯 Phase Objective

Comprehensively analyze production code using AST parsing to extract all functions, methods, attributes, and dependencies. This deep analysis prevents the failures that plagued V2.

---

## Tasks in This Phase

### Task 1: AST Method Analysis
**File:** [task-1-ast-method-analysis.md](task-1-ast-method-analysis.md)  
**Purpose:** Deep AST parsing for complete method signature extraction  
**Time:** 3 minutes

### Task 2: Attribute Pattern Detection  
**File:** [task-2-attribute-detection.md](task-2-attribute-detection.md)  
**Purpose:** Find ALL attribute access patterns for mock completeness  
**Time:** 2 minutes

### Task 3: Import Dependency Mapping
**File:** [task-3-import-mapping.md](task-3-import-mapping.md)  
**Purpose:** Map all imports to identify external vs internal dependencies  
**Time:** 2 minutes

### Task 4: Function Call Analysis
**File:** [task-4-function-calls.md](task-4-function-calls.md)  
**Purpose:** Analyze all function calls for signature matching  
**Time:** 2 minutes

### Task 5: Mock Completeness Validation (Unit Path)
**File:** [task-5-mock-completeness.md](task-5-mock-completeness.md)  
**Purpose:** Document ALL required mock attributes and patches  
**Time:** 3 minutes  
**Path:** Unit tests only

### Task 6: Real API Requirements (Integration Path)
**File:** [task-6-real-api-requirements.md](task-6-real-api-requirements.md)  
**Purpose:** Document real API endpoints and credentials needed  
**Time:** 3 minutes  
**Path:** Integration tests only

### Task 7: Evidence Collection
**File:** [task-7-evidence-collection.md](task-7-evidence-collection.md)  
**Purpose:** Consolidate all Phase 1 findings with quantified evidence  
**Time:** 2 minutes

---

## Execution Approach

🛑 EXECUTE-NOW: Complete tasks 1-4 (common to all paths)

Then based on path selection from Phase 0:
- **Unit path:** Complete task 5 (mock completeness)
- **Integration path:** Complete task 6 (real API requirements)

Finally: Complete task 7 (evidence collection)

---

## Phase Deliverables

Upon completion, you will have:
- ✅ Complete AST analysis with all function signatures
- ✅ All attribute access patterns identified
- ✅ All imports mapped (external vs internal)
- ✅ All function calls analyzed
- ✅ Mock completeness requirements (unit) OR API requirements (integration)
- ✅ Quantified evidence documented

---

## Validation Gate

🛑 VALIDATE-GATE: Phase 1 Checkpoint

Before advancing to Phase 2:
- [ ] AST parsing completed successfully ✅/❌
- [ ] All function signatures extracted ✅/❌
- [ ] All attributes detected (config, is_main_provider, etc) ✅/❌
- [ ] All imports mapped ✅/❌
- [ ] Function calls analyzed ✅/❌
- [ ] Path-specific requirements complete ✅/❌
- [ ] Progress table updated with evidence ✅/❌

🚨 FRAMEWORK-VIOLATION: Missing attributes = 22% failure

**Incomplete Phase 1 = Test Generation Failure**

---

## Start Phase 1

🎯 NEXT-MANDATORY: [task-1-ast-method-analysis.md](task-1-ast-method-analysis.md)

Begin with AST analysis - this is the foundation that prevents failures.



