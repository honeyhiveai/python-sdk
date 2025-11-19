# Task 1: Analyze Chunk Sizes

**Phase**: 4 - Semantic Validation  
**Purpose**: Analyze chunk sizes (after semantic chunking)  
**Depends On**: None  
**Feeds Into**: Task 2

---

## Objective

Analyze chunk sizes (after semantic chunking)

---

## Context

📊 **CONTEXT**: Chunk size impacts RAG retrieval quality. Too small = insufficient context. Too large = imprecise matching.

🔍 **MUST-SEARCH**: "semantic_chunking best practices"

---

## Instructions

### Step 1: Parse standard into semantic chunks

Parse standard into semantic chunks

📖 **DISCOVER-TOOL**: Read file contents

### Step 2: Count tokens per chunk

Count tokens per chunk

### Step 3: Calculate min, max, average chunk size

Calculate min, max, average chunk size

### Step 4: Identify chunks outside 100-500 token range

Identify chunks outside 100-500 token range

---

## Examples

### Example 1: Chunk size analysis results

```
[Example content]
```

---

## Expected Output

**Variables to Capture**:
- `analyze_chunk_sizes_complete`: Boolean

---

## Quality Checks

✅ All chunks 100-500 tokens  
✅ Average chunk size 200-400 tokens  
✅ No chunks too small or too large  

---

## Navigation

🎯 **NEXT-MANDATORY**: task-2-verify-semantic-completeness.md

↩️ **RETURN-TO**: phase.md

