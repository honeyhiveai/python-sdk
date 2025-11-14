# Task 1: Generate Test Queries

**Phase**: 3 - Discoverability Testing  
**Purpose**: Generate 5 test queries (one per angle)  
**Depends On**: None  
**Feeds Into**: Task 2

---

## Objective

Generate 5 test queries (one per angle)

---

## Context

📊 **CONTEXT**: Multi-angle testing ensures the standard is discoverable from different query perspectives. Agents approach topics from various angles depending on their current need.

🔍 **MUST-SEARCH**: "query_generation best practices"

---

## Instructions

### Step 1: Generate how-to query

'How do I [task]?'

📖 **DISCOVER-TOOL**: Write content to file

### Step 2: Generate when-to query

'When should I use [concept]?'

📖 **DISCOVER-TOOL**: Write content to file

### Step 3: Generate problem-solving query

'[Problem] not working'

📖 **DISCOVER-TOOL**: Write content to file

### Step 4: Generate decision-making query

'Should I use [X] or [Y]?'

📖 **DISCOVER-TOOL**: Write content to file

### Step 5: Generate tool-discovery query

'What tool for [task]?'

📖 **DISCOVER-TOOL**: Write content to file

---

## Examples

### Example 1: Complete query set for test generation topic

```
[Example content]
```

### Example 2: Complete query set for deployment workflow topic

```
[Example content]
```

---

## Expected Output

**Variables to Capture**:
- `generate_test_queries_complete`: Boolean

---

## Quality Checks

✅ 5 queries generated (one per angle)  
✅ Queries are natural language  
✅ Queries match expected agent patterns  
✅ Queries are specific to topic  

---

## Navigation

🎯 **NEXT-MANDATORY**: task-2-execute-rag-queries.md

↩️ **RETURN-TO**: phase.md

