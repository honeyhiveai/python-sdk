# Agent OS Framework Design Guide

**How to Build Procedural APIs for AI Assistants**

**Version**: 1.0  
**Date**: 2025-09-30  
**Purpose**: Systematic guide for designing deterministic, high-quality AI workflows using Agent OS patterns

---

## 🎯 **Core Concept: Frameworks as Procedural APIs**

Agent OS frameworks are **procedural APIs** for AI assistants, not documentation. This is a paradigm shift from traditional prompt engineering to systematic workflow design.

### **The API Paradigm**

| Traditional Programming API | Agent OS Workflow API |
|-----------------------------|----------------------|
| **Function Definition** | Task file with command sequences |
| **Function Call** | `🎯 NEXT-MANDATORY: [file.md]` navigation |
| **Return Value** | `📊 COUNT-AND-DOCUMENT: result` evidence |
| **Conditional Logic** | `🛑 VALIDATE-GATE: criteria` validation |
| **Error Handling** | `🚨 FRAMEWORK-VIOLATION: condition` detection |
| **Loop/Iteration** | Horizontal file scaling within phase |
| **State Management** | Progress table with `🛑 UPDATE-TABLE` |
| **Type System** | Command language definitions from glossary |

### **Key Insight**

Traditional approach (fails):
```markdown
"Please analyze the codebase and document your findings."
```

API approach (succeeds):
```markdown
🛑 EXECUTE-NOW: grep -n "^class" src/module.py
📊 COUNT-AND-DOCUMENT: Classes found: [NUMBER]
🛑 VALIDATE-GATE: All classes catalogued ✅/❌
🎯 NEXT-MANDATORY: [next-task.md]
```

**Why it works**: Binding commands + explicit navigation + evidence requirements = deterministic execution

---

## 📋 **Framework Design Process**

### **Step 1: Define the Workflow (API Contract)**

**Map your process to a procedural API with clear phases:**

#### **Example: Provider DSL Development**

```python
# Conceptual API contract
def provider_dsl_workflow(provider_name: str) -> ProviderDSL:
    """Complete provider DSL development workflow"""
    
    # Phase 0: Setup
    research_sources = setup_research_environment(provider_name)
    
    # Phase 1: Official Documentation Discovery
    docs = discover_official_documentation(provider_name)
    
    # Phase 2: Instrumentor Verification
    instrumentors = verify_instrumentor_support(provider_name)
    
    # Phase 3: Model & Pricing Collection
    pricing = collect_model_pricing(provider_name, docs)
    
    # Phase 4: Structure Patterns
    patterns = create_detection_patterns(provider_name, instrumentors)
    
    # Phase 5: Navigation Rules
    rules = create_navigation_rules(provider_name, instrumentors)
    
    # Phase 6: Field Mappings
    mappings = create_field_mappings(provider_name, rules)
    
    # Phase 7: Transforms
    transforms = create_transform_functions(provider_name, pricing)
    
    # Phase 8: Compilation & Validation
    bundle = compile_and_validate(patterns, rules, mappings, transforms)
    
    # Phase 9: Documentation
    finalize_documentation(research_sources, bundle)
    
    return bundle
```

#### **Translation to Agent OS Structure**

```
provider-dsl-development/
├── README.md                    # API documentation (Tier 2)
├── entry-point.md              # main() function entry
├── progress-tracking.md        # State management
└── phases/
    ├── 0/  # setup_research_environment()
    ├── 1/  # discover_official_documentation()
    ├── 2/  # verify_instrumentor_support()
    ├── 3/  # collect_model_pricing()
    ├── 4/  # create_detection_patterns()
    ├── 5/  # create_navigation_rules()
    ├── 6/  # create_field_mappings()
    ├── 7/  # create_transform_functions()
    ├── 8/  # compile_and_validate()
    └── 9/  # finalize_documentation()
```

### **Step 2: Design Phase Structure (Modules)**

**Each phase directory is a module containing function definitions:**

#### **Phase as Module Design**

```
phases/2/  # Instrumentor Verification Module
├── shared-analysis.md              # Module entry point / router (≤100 lines)
├── traceloop-verification.md       # verify_traceloop() function
├── openinference-verification.md   # verify_openinference() function
├── openlit-verification.md         # verify_openlit() function
└── evidence-collection.md          # collect_evidence() - returns to caller
```

#### **Module Responsibilities**

**shared-analysis.md** (Router/Orchestrator):
- Entry point for the phase
- Lists all tasks (functions) to execute
- Routes to first task
- Defines phase completion gate
- Size: ≤100 lines

**Task Files** (Functions):
- Single responsibility (one specific action)
- Explicit commands (🛑 EXECUTE-NOW)
- Evidence documentation (📊 COUNT-AND-DOCUMENT)
- Validation gate (🛑 VALIDATE-GATE)
- Navigation to next (🎯 NEXT-MANDATORY)
- Size: ≤100 lines (≤150 for complex tasks)

**Last Task File** (Phase Return):
- Completes final task
- Phase completion gate
- Evidence summary
- Routes to next phase
- Size: ≤100 lines

### **Step 3: Write Task Files (Function Definitions)**

#### **Standard Task File Template**

```markdown
# Task X.Y: [Function Name]

**🎯 [Brief description of what this function does]**

## 🚨 **ENTRY REQUIREMENTS** (preconditions)

🛑 VALIDATE-GATE: Task Prerequisites
- [ ] Required input X available ✅/❌
- [ ] State Y confirmed ✅/❌
- [ ] Phase X.Y-1 complete ✅/❌

## 🛑 **EXECUTION** (function body)

### **Step 1: [Action Name]**
🛑 EXECUTE-NOW: [Specific command or action]
```bash
# Example command
curl -s https://api.example.com/endpoint | jq '.field'
```
🛑 PASTE-OUTPUT: Complete command results

### **Step 2: [Analysis Name]**
📊 COUNT-AND-DOCUMENT: [Specific metric]: [EXACT VALUE]
📊 QUANTIFY-RESULTS: [Measurement]: [NUMBER or YES/NO]

### **Step 3: [Documentation Name]**
⚠️ EVIDENCE-REQUIRED: [Specific evidence type]
```markdown
# Document findings in specific format
- Field 1: [value]
- Field 2: [value]
```

## 🛑 **VALIDATION GATE** (postconditions)

🛑 VALIDATE-GATE: Task X.Y Complete
- [ ] Command executed with full output ✅/❌
- [ ] Results quantified and documented ✅/❌
- [ ] Evidence meets requirements ✅/❌
- [ ] Quality criteria satisfied ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without complete evidence

## 🎯 **NAVIGATION** (control flow)

🛑 UPDATE-TABLE: Phase X.Y → Complete with evidence
🎯 NEXT-MANDATORY: [next-task-file.md](next-task-file.md)
```

#### **Last Task File Template (Phase Completion)**

```markdown
# Task X.Z: [Final Task Name]

**🎯 [Description - this completes Phase X]**

## 🚨 **ENTRY REQUIREMENTS**
[... standard entry requirements ...]

## 🛑 **EXECUTION**
[... standard execution steps ...]

## 🛑 **VALIDATION GATE**
[... standard validation gate ...]

## 🛤️ **PHASE X COMPLETION GATE**

🛑 UPDATE-TABLE: Phase X → COMPLETE with comprehensive evidence

### **Phase X Summary**
📊 QUANTIFY-RESULTS: Total tasks completed: [X/X]
📊 QUANTIFY-RESULTS: Evidence items documented: [NUMBER]
⚠️ EVIDENCE-REQUIRED: All validation gates passed

### **Handoff to Phase Y Validated**
✅ **Output 1**: [Description] - available for Phase Y
✅ **Output 2**: [Description] - available for Phase Y
✅ **Output 3**: [Description] - available for Phase Y

### **Phase Y Inputs Available and Verified**
✅ Input requirement 1 satisfied
✅ Input requirement 2 satisfied
✅ Input requirement 3 satisfied

## 🎯 **CROSS-PHASE NAVIGATION**

🎯 NEXT-MANDATORY: Phase Y [Description] (only after all validation gates pass)
🚨 FRAMEWORK-VIOLATION: If advancing to Phase Y without Phase X completion
```

### **Step 4: Implement Navigation (Control Flow)**

#### **Within-Phase Navigation (Sequential)**

Standard sequential task chain:

```markdown
# shared-analysis.md routes to first task
🎯 NEXT-MANDATORY: [task-1.md](task-1.md)

# task-1.md routes to task-2
🎯 NEXT-MANDATORY: [task-2.md](task-2.md)

# task-2.md routes to task-3
🎯 NEXT-MANDATORY: [task-3.md](task-3.md)

# task-3.md (last task) routes to next phase
🎯 NEXT-MANDATORY: Phase Y Description
```

**Navigation Chain Example:**

```
shared-analysis.md
    ↓
    🎯 NEXT-MANDATORY
    ↓
task-1-setup.md
    ↓
    🎯 NEXT-MANDATORY
    ↓
task-2-analysis.md
    ↓
    🎯 NEXT-MANDATORY
    ↓
task-3-validation.md
    ↓
    🎯 NEXT-MANDATORY: Phase Y
```

#### **Cross-Phase Navigation**

**Only the LAST task file** in a phase routes to the next phase:

```markdown
# phases/2/evidence-collection.md (last task in Phase 2)

🎯 NEXT-MANDATORY: Phase 3 Model & Pricing Collection (only after all validation gates pass)
```

**NOT in shared-analysis.md or other files** - maintains clear separation of concerns.

#### **Conditional Navigation (Branching)**

For path selection (e.g., unit vs integration tests):

```markdown
# shared-analysis.md

## 🛤️ **PATH SELECTION**

**Choose ONE path based on test type:**

### **Path A: Unit Tests**
- Strategy: Mock everything external
- Coverage target: 90%+ line/branch
- 🎯 NEXT-MANDATORY: [unit-mock-strategy.md](unit-mock-strategy.md)

### **Path B: Integration Tests**
- Strategy: Real API usage
- Coverage target: Functional flow coverage
- 🎯 NEXT-MANDATORY: [integration-real-strategy.md](integration-real-strategy.md)

⚠️ MUST-COMPLETE: Selected path before Phase Y
```

Both paths eventually converge to phase completion:

```
shared-analysis.md
    ├── Path A → unit-mock-strategy.md ──┐
    │                                     ├→ evidence-collection.md → Phase Y
    └── Path B → integration-real-strategy.md ┘
```

### **Step 5: Define Evidence Format (Return Types)**

#### **Standard Evidence Patterns**

**Numerical Evidence:**
```markdown
📊 COUNT-AND-DOCUMENT: Classes found: 15
📊 COUNT-AND-DOCUMENT: Functions analyzed: 42
📊 COUNT-AND-DOCUMENT: Dependencies mapped: 23
```

**Boolean Evidence:**
```markdown
📊 QUANTIFY-RESULTS: Traceloop support verified: YES
📊 QUANTIFY-RESULTS: Compilation successful: YES
📊 QUANTIFY-RESULTS: All tests passing: NO (3 failures)
```

**List Evidence:**
```markdown
⚠️ EVIDENCE-REQUIRED: URLs verified:
- https://docs.provider.com/api
- https://docs.provider.com/models
- https://docs.provider.com/pricing
```

**Structured Evidence:**
```markdown
📊 QUANTIFY-RESULTS: Instrumentor support matrix:
- Traceloop: ✅ VERIFIED (package exists: opentelemetry-instrumentation-provider)
- OpenInference: ✅ VERIFIED (generic LLM support confirmed)
- OpenLit: ❌ NOT SUPPORTED (no provider directory found)
```

**Command Output Evidence:**
```markdown
🛑 PASTE-OUTPUT: AST analysis results
```
CLASS: MyClass (Line 15) - 8 methods
  __init__(self, config) - Line 16 - PUBLIC - Required: 1
  process(self, data) - Line 24 - PUBLIC - Required: 1
  _validate(self, item) - Line 42 - PRIVATE - Required: 1
```
```

#### **Evidence Quality Requirements**

- ✅ **Quantified**: Numbers, not "many" or "several"
- ✅ **Specific**: Exact values, not ranges
- ✅ **Verifiable**: Can be validated by re-running commands
- ✅ **Complete**: All requested evidence provided
- ❌ **Vague**: "Analysis complete", "looks good"
- ❌ **Qualitative**: "high quality", "comprehensive"

### **Step 6: Create Progress Table (State Management)**

#### **Progress Table Template**

```markdown
# Progress Tracking Template

## 🛑 **MANDATORY: Copy This Table to Chat Before Execution**

| Phase | Status | Evidence | Commands | Gate |
|-------|--------|----------|----------|------|
| 0. Setup | ⏳ PENDING | 0/3 items | 0/3 | ❌ |
| 1. Discovery | ⏳ PENDING | 0/4 URLs | 0/4 | ❌ |
| 2. Verification | ⏳ PENDING | 0/3 verified | 0/8 | ❌ |
| 3. Collection | ⏳ PENDING | 0 models | 0/6 | ❌ |
| 4. Patterns | ⏳ PENDING | 0 patterns | 0/5 | ❌ |
| 5. Rules | ⏳ PENDING | 0 rules | 0/7 | ❌ |
| 6. Mappings | ⏳ PENDING | 0/4 sections | 0/4 | ❌ |
| 7. Transforms | ⏳ PENDING | 0 transforms | 0/6 | ❌ |
| 8. Validation | ⏳ PENDING | 0% pass | 0/5 | ❌ |
| 9. Documentation | ⏳ PENDING | Incomplete | 0/4 | ❌ |

**Status Legend:**
- ⏳ PENDING - Not started
- 🔄 IN PROGRESS - Currently executing
- ✅ COMPLETE - All validation gates passed
- ❌ BLOCKED - Waiting for dependency

**Gate Legend:**
- ✅ PASSED - All validation criteria met
- ❌ FAILED - Validation criteria not met
- ⏳ PENDING - Not yet validated
```

#### **Table Update Pattern**

After each task:
```markdown
🛑 UPDATE-TABLE: Phase 2.1 → Traceloop verification complete
```

Update to:
```markdown
| 2. Verification | 🔄 IN PROGRESS | 1/3 verified | 3/8 | ⏳ |
```

After phase completion:
```markdown
🛑 UPDATE-TABLE: Phase 2 → COMPLETE with comprehensive evidence
```

Update to:
```markdown
| 2. Verification | ✅ COMPLETE | 3/3 verified | 8/8 | ✅ |
```

---

## 🎨 **Common Design Patterns**

### **Pattern 1: Sequential Pipeline**

**Structure:**
```
Task 1 → Task 2 → Task 3 → Task 4
```

**Use When:**
- Linear workflow with dependencies
- Each task builds on previous results
- No branching or parallelism needed

**Example:**
```
phases/1/
├── shared-analysis.md → task-1-api-docs.md
└── task-1-api-docs.md → task-2-models.md
    └── task-2-models.md → task-3-pricing.md
        └── task-3-pricing.md → task-4-changelog.md
            └── task-4-changelog.md → Phase 2
```

### **Pattern 2: Parallel Tasks with Merge**

**Structure:**
```
        ┌→ Task 2A ┐
Task 1 ─┼→ Task 2B ┼→ Task 3 (merge evidence)
        └→ Task 2C ┘
```

**Use When:**
- Independent tasks can execute in any order
- Results need to be aggregated
- No dependencies between parallel tasks

**Implementation:**
```markdown
# shared-analysis.md

## 🛑 **PARALLEL TASK EXECUTION**

Execute these tasks in any order:

### **Task 2.1: Traceloop Verification**
⚠️ MUST-COMPLETE: [traceloop-verification.md](traceloop-verification.md)

### **Task 2.2: OpenInference Verification**
⚠️ MUST-COMPLETE: [openinference-verification.md](openinference-verification.md)

### **Task 2.3: OpenLit Verification**
⚠️ MUST-COMPLETE: [openlit-verification.md](openlit-verification.md)

🎯 NEXT-MANDATORY: [evidence-collection.md](evidence-collection.md) (after ALL tasks complete)
```

Each parallel task ends with:
```markdown
🎯 NEXT-MANDATORY: Return to [shared-analysis.md](shared-analysis.md) for next task
```

### **Pattern 3: Conditional Branch**

**Structure:**
```
        ┌→ Path A → Task 2A ┐
Task 1 ─┤                    ├→ Task 3
        └→ Path B → Task 2B ┘
```

**Use When:**
- Different strategies based on input
- Path selection affects execution
- Both paths converge to same endpoint

**Example: Unit vs Integration Tests**
```markdown
# shared-analysis.md

## 🛤️ **PATH SELECTION**

### **Path A: Unit Tests**
🎯 NEXT-MANDATORY: [unit-mock-strategy.md](unit-mock-strategy.md)

### **Path B: Integration Tests**
🎯 NEXT-MANDATORY: [integration-real-strategy.md](integration-real-strategy.md)
```

Both paths end with:
```markdown
🎯 NEXT-MANDATORY: [evidence-collection.md](evidence-collection.md)
```

### **Pattern 4: Validation Loop with Retry**

**Structure:**
```
Task 1 → Validate → [Pass] → Task 2
              ↓
           [Fail] → Fix Instructions → Task 1
```

**Use When:**
- Quality gates with potential failures
- Iterative improvement needed
- Can't proceed without validation

**Implementation:**
```markdown
# task-validation.md

## 🛑 **VALIDATION GATE**

🛑 VALIDATE-GATE: Quality Criteria
- [ ] Criterion 1 met ✅/❌
- [ ] Criterion 2 met ✅/❌

### **If ALL ✅:**
🎯 NEXT-MANDATORY: [next-task.md](next-task.md)

### **If ANY ❌:**
🚨 FRAMEWORK-VIOLATION: Quality criteria not met

**Fix Instructions:**
1. Review failed criterion
2. Re-execute [task-X.md](task-X.md)
3. Return to this validation

🎯 NEXT-MANDATORY: [task-X.md](task-X.md) (for rework)
```

### **Pattern 5: Horizontal Scaling (Extensible Module)**

**Structure:**
```
phases/2/
├── shared-analysis.md
├── task-1.md
├── task-2.md
├── task-3.md
└── [easy to add task-4.md, task-5.md, etc.]
```

**Use When:**
- Framework may grow over time
- Don't know all requirements upfront
- Want to avoid refactoring when adding features

**Benefits:**
- Add new file → update navigation → done!
- No file size bloat
- Each file stays ≤100 lines
- Easy maintenance

**Example: Adding New Instrumentor**
```bash
# Original:
phases/2/
├── traceloop-verification.md
├── openinference-verification.md
└── openlit-verification.md

# Add new instrumentor - just create new file:
phases/2/
├── traceloop-verification.md
├── openinference-verification.md
├── openlit-verification.md
└── llamaindex-verification.md  # NEW!
```

Update navigation:
```markdown
# openlit-verification.md
🎯 NEXT-MANDATORY: [llamaindex-verification.md](llamaindex-verification.md)

# llamaindex-verification.md
🎯 NEXT-MANDATORY: [evidence-collection.md](evidence-collection.md)
```

---

## 📏 **File Size Guidelines (Context Optimization)**

### **Size Constraints by Tier**

| File Type | Tier | Target Size | Practical Limit | Purpose |
|-----------|------|-------------|-----------------|---------|
| **Hub README** | 2 | 300-400 lines | 500 lines | Overview & discovery |
| **Entry Point** | 1 | 50-75 lines | 100 lines | Framework initialization |
| **Phase Reference** | 2 | 200-300 lines | 400 lines | Optional detailed guide |
| **shared-analysis.md** | 1 | 50-75 lines | 100 lines | Phase router |
| **Task Files** | 1 | 60-80 lines | 100 lines | Specific execution |
| **Complex Tasks** | 1 | 100-120 lines | 150 lines | Multi-step tasks |
| **Progress Table** | 1 | 50-75 lines | 100 lines | State tracking |

### **Why These Limits?**

**From LLM Workflow Engineering Methodology:**

| Context Utilization | Attention Quality | Execution Consistency | File Size |
|---------------------|------------------|----------------------|-----------|
| **15-25%** (Optimal) | 95%+ | 85%+ | ≤100 lines |
| **50-75%** (Degraded) | 70-85% | 60-75% | 200-500 lines |
| **75%+** (Failure) | <70% | <50% | 500+ lines |

**Rule of Thumb:**
- Tier 1 (execution): ≤100 lines → 15-25% context → 85%+ consistency
- Tier 2 (reference): 200-500 lines → 40-60% context → one-time consumption
- Tier 3 (output): Unlimited → never re-consumed by AI

### **When to Split Files**

**Split if:**
- ✅ File exceeds 100 lines for Tier 1
- ✅ Single task has 3+ distinct sub-tasks
- ✅ File has multiple responsibilities
- ✅ Navigation becomes unclear

**Don't split if:**
- ❌ Creates files <30 lines (too fragmented)
- ❌ Breaks logical cohesion
- ❌ Makes navigation overly complex

---

## ✅ **Quality Checklist for Framework Design**

### **Completeness**

- [ ] Every task file has `🎯 NEXT-MANDATORY` navigation
- [ ] Every phase has completion gate in last task
- [ ] Every command produces documented evidence
- [ ] Progress table covers all phases
- [ ] All phases have entry requirements
- [ ] All phases have validation gates
- [ ] Hub README provides complete overview
- [ ] Entry point routes to Phase 0

### **Determinism**

- [ ] Commands use binding language (🛑, 📊, 🎯, ⚠️)
- [ ] Navigation is explicit with file paths
- [ ] Validation gates have measurable criteria
- [ ] No ambiguous natural language instructions
- [ ] Evidence requirements are quantified
- [ ] All conditionals are explicit
- [ ] Command glossary is referenced
- [ ] Framework violations are detected

### **Maintainability**

- [ ] Horizontal scaling enabled (directories per phase)
- [ ] Each Tier 1 file ≤100-150 lines
- [ ] Consistent patterns across all phases
- [ ] Reusable templates applied
- [ ] Clear separation of concerns
- [ ] Modular design allows updates
- [ ] Documentation is co-located
- [ ] Navigation chains are unbroken

### **Discoverability**

- [ ] Entry point clearly identified
- [ ] Hub README provides workflow overview
- [ ] Progress table shows full structure
- [ ] Navigation chain is complete
- [ ] Phase purposes are documented
- [ ] Task responsibilities are clear
- [ ] Command language glossary linked
- [ ] Examples provided where helpful

### **Context Optimization**

- [ ] Tier 1 files in optimal range (≤100 lines)
- [ ] Tier 2 files for reference only (200-500 lines)
- [ ] Command language reduces token usage
- [ ] Evidence format is compact
- [ ] Minimal redundancy across files
- [ ] Clear boundaries between tiers
- [ ] No unnecessary verbose language
- [ ] Focus on execution efficiency

---

## 🚀 **Quick Start: Building Your First Framework**

### **Example: API Documentation Generation Framework**

**Goal:** Systematic generation of API documentation from codebase

#### **Step 1: Define API Contract**

```python
def api_documentation_workflow(source_dir: str) -> Documentation:
    # Phase 0: Load codebase context
    context = load_codebase_context(source_dir)
    
    # Phase 1: Analyze codebase structure
    structure = analyze_codebase_structure(context)
    
    # Phase 2: Extract public APIs
    apis = extract_public_apis(structure)
    
    # Phase 3: Generate usage examples
    examples = generate_usage_examples(apis)
    
    # Phase 4: Build documentation
    docs = build_documentation(apis, examples)
    
    # Phase 5: Validate links and references
    validate_documentation(docs)
    
    return docs
```

#### **Step 2: Create Directory Structure**

```bash
api-documentation-framework/
├── README.md
├── entry-point.md
├── progress-tracking.md
└── phases/
    ├── 0/
    │   ├── shared-analysis.md
    │   └── load-context.md
    ├── 1/
    │   ├── shared-analysis.md
    │   ├── analyze-structure.md
    │   └── inventory-modules.md
    ├── 2/
    │   ├── shared-analysis.md
    │   ├── extract-classes.md
    │   ├── extract-functions.md
    │   └── extract-parameters.md
    ├── 3/
    │   ├── shared-analysis.md
    │   ├── generate-class-examples.md
    │   └── generate-function-examples.md
    ├── 4/
    │   ├── shared-analysis.md
    │   ├── build-reference.md
    │   └── build-guides.md
    └── 5/
        ├── shared-analysis.md
        ├── validate-links.md
        └── validate-examples.md
```

#### **Step 3: Write Entry Point**

```markdown
# API Documentation Framework - Entry Point

⚠️ MUST-READ: [../command-language-glossary.md](../command-language-glossary.md)

## 🛑 **MANDATORY STEPS**

### **Step 1: Acknowledge Framework**
🛑 EXECUTE-NOW: State acknowledgment
```
✅ I acknowledge the API Documentation Framework contract:
- I will analyze the codebase systematically
- I will extract ALL public APIs with complete signatures
- I will generate working examples for each API
- I will validate all documentation links
```

### **Step 2: Initialize Progress Table**
🛑 UPDATE-TABLE: Copy table to chat
⚠️ MUST-READ: [progress-tracking.md](progress-tracking.md)
🛑 PASTE-OUTPUT: Complete table in chat

### **Step 3: Execute Framework Phases**
🎯 NEXT-MANDATORY: [phases/0/shared-analysis.md](phases/0/shared-analysis.md)
```

#### **Step 4: Write First Phase Task**

```markdown
# Phase 0: Load Codebase Context

## 🚨 **ENTRY REQUIREMENTS**
🛑 VALIDATE-GATE: Prerequisites
- [ ] Source directory confirmed ✅/❌
- [ ] Framework acknowledgment complete ✅/❌

## 🛑 **EXECUTION**

🛑 EXECUTE-NOW: List all Python source files
```bash
find src/ -name "*.py" -type f | sort
```
🛑 PASTE-OUTPUT: Complete file list

📊 COUNT-AND-DOCUMENT: Python files found: [NUMBER]

## 🛑 **VALIDATION GATE**
🛑 VALIDATE-GATE: Context Loading Complete
- [ ] All files catalogued ✅/❌
- [ ] File count documented ✅/❌

## 🎯 **NAVIGATION**
🛑 UPDATE-TABLE: Phase 0 → Complete
🎯 NEXT-MANDATORY: Phase 1 Codebase Analysis
```

#### **Step 5: Test and Iterate**

1. Execute framework with real input
2. Measure consistency across runs
3. Identify navigation gaps
4. Add validation gates where needed
5. Refine evidence requirements
6. Iterate until 80%+ success rate

---

## 🎯 **Success Metrics**

A well-designed framework should achieve:

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Execution Consistency** | 80-95% | Success rate across 10+ runs |
| **Instruction Compliance** | 85-95% | % of commands executed correctly |
| **Context Efficiency** | 15-25% per phase | Token utilization measurement |
| **Navigation Drift** | <5% | % of incorrect next-step selections |
| **Evidence Completeness** | 95%+ | % of required evidence provided |
| **Quality Gate Pass** | 90%+ | % of validation gates passed first time |

### **Measurement Commands**

**Test consistency:**
```bash
for i in {1..10}; do
    run_framework_test.sh > "run_$i.log"
done
diff run_*.log  # Should be minimal differences
```

**Measure context efficiency:**
```python
import tiktoken

def measure_context(file_path):
    with open(file_path) as f:
        content = f.read()
    tokens = len(tiktoken.encoding_for_model("gpt-4").encode(content))
    max_tokens = 8192  # GPT-4 context window
    utilization = (tokens / max_tokens) * 100
    print(f"{file_path}: {tokens} tokens ({utilization:.1f}%)")
```

---

## 📚 **Additional Resources**

- **Command Language Glossary**: [command-language-glossary.md](command-language-glossary.md)
- **Design Patterns Library**: [framework-design-patterns.md](framework-design-patterns.md)
- **LLM Workflow Methodology**: [LLM-WORKFLOW-ENGINEERING-METHODOLOGY.md](LLM-WORKFLOW-ENGINEERING-METHODOLOGY.md)
- **V3 Test Framework**: [code-generation/tests/v3/](code-generation/tests/v3/) (reference implementation)
- **Provider DSL Framework**: [provider-dsl-development/](provider-dsl-development/) (reference implementation)

---

## 🎓 **Learning Path**

1. **Read**: Command Language Glossary (understand the API)
2. **Study**: V3 Test Framework structure (see patterns in action)
3. **Practice**: Build simple 3-phase framework
4. **Apply**: Design your own framework following this guide
5. **Refine**: Measure and iterate based on success metrics
6. **Contribute**: Share patterns back to this guide

---

**Remember: You're not writing documentation, you're designing a procedural API for AI execution!**
