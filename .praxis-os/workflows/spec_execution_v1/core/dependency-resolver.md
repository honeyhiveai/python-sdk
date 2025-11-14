# Dependency Resolver - Task Execution Order

**Type:** Tier 2 (Methodology - On-Demand Reading)  
**Purpose:** Validate and resolve task dependencies to determine correct execution order  
**Referenced by:** Phase 0, Task 3

---

## Overview

This document provides methodology for resolving task dependencies extracted from tasks.md, validating dependency relationships, and determining the correct execution order.

---

## Dependency Types

### Type 1: No Dependencies

```markdown
- **Task 1.1**: Create module structure
  - **Dependencies**: None
```

**Execution:** Can execute immediately

### Type 2: Single Dependency

```markdown
- **Task 1.2**: Configure module
  - **Dependencies**: Task 1.1
```

**Execution:** Must wait for Task 1.1 completion

### Type 3: Multiple Dependencies

```markdown
- **Task 2.3**: Integration testing
  - **Dependencies**: Task 2.1, Task 2.2
```

**Execution:** Must wait for ALL listed tasks to complete

### Type 4: Cross-Phase Dependencies

```markdown
- **Task 3.1**: Deploy configuration
  - **Dependencies**: Task 2.5 (from previous phase)
```

**Execution:** Must wait for prior phase task completion

---

## Validation Rules

### Rule 1: No Circular Dependencies

**Invalid:**
```
Task 1.1 depends on Task 1.2
Task 1.2 depends on Task 1.1
```

**Detection:** Build dependency graph, check for cycles

**Action:** Report error, cannot execute

### Rule 2: Forward References Only

**Invalid:**
```
Task 1.1 depends on Task 1.3 (not yet defined)
```

**Valid:**
```
Task 1.3 depends on Task 1.1 (already defined)
```

**Exception:** Cross-phase dependencies (allowed)

### Rule 3: Existing Task References

**Invalid:**
```
Task 2.1 depends on Task 1.5 (Task 1.5 doesn't exist)
```

**Validation:** Verify all referenced task IDs exist in parsed data

---

## Resolution Algorithm

### Step 1: Build Dependency Graph

```python
graph = {
    "1.1": [],  # No dependencies
    "1.2": ["1.1"],  # Depends on 1.1
    "1.3": ["1.1"],  # Depends on 1.1
    "2.1": ["1.2", "1.3"],  # Depends on both
}
```

### Step 2: Topological Sort

Use topological sort to determine execution order:

```python
def resolve_order(graph):
    in_degree = {task: 0 for task in graph}
    
    # Count incoming edges
    for task, deps in graph.items():
        for dep in deps:
            in_degree[task] += 1
    
    # Start with tasks with no dependencies
    queue = [task for task, deg in in_degree.items() if deg == 0]
    order = []
    
    while queue:
        task = queue.pop(0)
        order.append(task)
        
        # Reduce in-degree for dependent tasks
        for other_task, deps in graph.items():
            if task in deps:
                in_degree[other_task] -= 1
                if in_degree[other_task] == 0:
                    queue.append(other_task)
    
    return order
```

### Step 3: Validate Complete Resolution

If not all tasks in order, circular dependency exists.

---

## Execution Order Patterns

### Pattern 1: Sequential (No Dependencies)

```
Task 1.1 → Task 1.2 → Task 1.3
```

Simple sequential execution in definition order.

### Pattern 2: Parallel Potential

```
Task 1.1
  ├→ Task 1.2 (depends on 1.1)
  └→ Task 1.3 (depends on 1.1)
```

Tasks 1.2 and 1.3 can execute in parallel after 1.1.

**Note:** Current workflow uses horizontal scaling (one task at a time), but dependency graph identifies parallelizable tasks for future optimization.

### Pattern 3: Convergence

```
Task 1.1 → Task 1.3
Task 1.2 → Task 1.3
```

Task 1.3 waits for both 1.1 and 1.2 to complete.

---

## Dependency Notation Parsing

### Format 1: Explicit Task ID

```
Dependencies: Task 1.2
```

Parse as: `["1.2"]`

### Format 2: Multiple Tasks

```
Dependencies: Task 1.2, Task 1.3
```

Parse as: `["1.2", "1.3"]`

### Format 3: Implicit Reference

```
Dependencies: Previous task
```

Resolve to: Prior task in sequence

### Format 4: None

```
Dependencies: None
```

Parse as: `[]`

---

## Error Messages

### Circular Dependency Error

```
❌ DEPENDENCY ERROR: Circular dependency detected

Cycle: Task 1.2 → Task 1.3 → Task 1.2

Resolution: Review tasks.md and remove circular dependency.
```

### Missing Task Error

```
❌ DEPENDENCY ERROR: Referenced task does not exist

Task 2.1 depends on Task 1.5 (not found)

Resolution: Verify task IDs in tasks.md are correct.
```

### Cross-Phase Error

```
❌ DEPENDENCY ERROR: Invalid cross-phase dependency

Task 2.1 depends on Task 3.5 (forward reference to later phase)

Resolution: Dependencies must reference prior phases only.
```

---

## Workflow Integration

### In Phase 0

1. Parse all tasks (Task-parser.md)
2. Build dependency graph
3. Validate dependencies
4. Resolve execution order
5. Store for task sequencing

### During Execution

1. Before executing task N.M:
   - Check dependencies
   - Verify all dependencies completed
   - Proceed if clear, wait if blocked

2. Use horizontal scaling:
   - Execute one task at a time
   - Check next task dependencies
   - Skip if blocked, queue for later

---

## References

- Task Parser (task-parser.md): Provides dependency data
- Horizontal Decomposition: One task at a time execution
- Validation Gates (validation-gates.md): Phase-level validation

---

**Proper dependency resolution ensures tasks execute in the correct order, preventing failures from missing prerequisites.**

