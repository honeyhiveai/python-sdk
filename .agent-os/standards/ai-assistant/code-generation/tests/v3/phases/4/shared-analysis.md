# Phase 4: Usage Pattern Analysis - Shared Analysis

**🎯 Execute all components systematically. Shared analysis provides foundation for path-specific strategies.**

🛑 VALIDATE-GATE: Phase 4 Entry Requirements
- [ ] Phase 3 completed with comprehensive evidence ✅/❌
- [ ] Framework contract acknowledged and binding ✅/❌
- [ ] Test path selected and locked (unit OR integration) ✅/❌
- [ ] Phase 3 progress table updated ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without Phase 3 completion

## 🚨 **ENTRY CHECKPOINT**
- [ ] Phase 3 completed and validated
- [ ] Framework contract acknowledged: [../../core/binding-contract.md](../../core/binding-contract.md)
- [ ] Test path selected: Unit or Integration (determines next steps)
- [ ] Production file confirmed: `src/honeyhive/tracer/instrumentation/initialization.py`

## 📋 **COMPONENTS**

1.  **Function Call Patterns**: [function-call-patterns.md](function-call-patterns.md)
2.  **Control Flow Analysis**: [control-flow-analysis.md](control-flow-analysis.md)
3.  **Error Handling Patterns**: [error-handling-patterns.md](error-handling-patterns.md)
4.  **State Management Analysis**: [state-management-analysis.md](state-management-analysis.md)
5.  **Data Type & Schema Analysis**: [Inline task - see TASK 4.5 below]
6.  **Unit Usage Strategy**: [unit-usage-strategy.md](unit-usage-strategy.md) (Unit path only)
7.  **Integration Usage Strategy**: [integration-usage-strategy.md](integration-usage-strategy.md) (Integration path only)
8.  **Evidence Framework**: [evidence-collection-framework.md](evidence-collection-framework.md)

## 🚨 **EXECUTION GUARDRAILS**

### **Sequential Requirements**
-   **Cannot skip components** - each builds on previous
-   **Shared analysis first** (1-4) before path selection
-   **Path-specific strategy** (5 OR 6) based on test type

### **Evidence Requirements**
-   **Quantified results**: "X patterns found" not "analysis complete"
-   **Command outputs**: Actual grep/Python results pasted
-   **Validation proof**: Quality gates passed with evidence
-   **Progress tracking**: Updated tables with real numbers

## 🛤️ **PATH SELECTION**
-   **Unit**: Execute [unit-usage-strategy.md](unit-usage-strategy.md) (mock usage patterns)
-   **Integration**: Execute [integration-usage-strategy.md](integration-usage-strategy.md) (real usage validation)

## 📋 **INLINE TASKS**

### **TASK 4.5: Data Type & Schema Analysis**
🛑 EXECUTE-NOW: Identify structured data types used in production code
⚠️ MUST-READ: Understand schemas before creating test fixtures

**What to Analyze**:

1. **Pydantic Models (v2)**
   ```bash
   # Find Pydantic v2 models
   grep -r "class.*BaseModel" production_file.py
   grep -r "from pydantic import" production_file.py
   ```
   
   **⚠️ PROJECT CONVENTION**: This project uses Pydantic v2. Use Pydantic models exclusively, NOT dataclasses.

2. **TypedDicts**
   ```bash
   # Find TypedDicts (for type hints, not runtime validation)
   grep -r "class.*TypedDict" production_file.py
   grep -r "from typing import TypedDict" production_file.py
   ```

3. **Custom Types & Schemas**
   ```bash
   # Find custom type imports
   grep -r "from.*types import" production_file.py
   grep -r "import.*_types" production_file.py
   grep -r "from.*bundle_types import" production_file.py
   ```

**Document Schema Requirements**:

For each structured type found:
- [ ] Read the type definition (use `read_file` on the types module)
- [ ] Document required fields and their types
- [ ] Document optional fields and default values
- [ ] Note any validation rules (Pydantic validators, constraints)
- [ ] Understand nested structures (e.g., `Dict[FrozenSet[str], Tuple[str, float]]`)

**Evidence from TASK-014**:
- Pydantic model `CompiledProviderBundle` found
- Schema required `signature_to_provider: Dict[FrozenSet[str], Tuple[str, float]]`
- Test fixture incorrectly used `Dict[FrozenSet[str], str]`
- Result: 17 test errors from Pydantic validation
- Fix: Read `bundle_types.py` and corrected schema to use tuples

**Why This Matters**:
- Test fixtures MUST match production Pydantic v2 schemas
- Pydantic v2 performs strict runtime validation on model instantiation
- Schema violations cause immediate `pydantic_core.ValidationError` exceptions
- Reading schemas upfront prevents fixture validation errors
- Understanding nested types ensures correct mock data structure

**Common Pydantic v2 Schema Issues**:
- Using `str` instead of `Tuple[str, float]` (type mismatch)
- Missing required fields in fixture data (validation error)
- Wrong type for frozenset/set/list collections (type validation)
- Incorrect nesting depth for complex types (structure mismatch)
- Using dataclasses instead of Pydantic models (project convention violation)

📊 COUNT-AND-DOCUMENT: Data types found and documented: [NUMBER]
🛑 UPDATE-TABLE: Task 4.5 complete → Schemas understood and documented

---

**Execute all tasks 4.1-4.8 systematically.**
