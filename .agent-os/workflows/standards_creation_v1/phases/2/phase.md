# Phase 2: RAG Optimization

**Purpose:** Optimize content for RAG semantic search discovery  
**Deliverable:** RAG-optimized standard with keyword density, query hooks, descriptive headers, and semantic chunking

---

## Overview

Optimize content for RAG semantic search discovery

We systematically:

1. **Optimize keyword density**
2. **Add query hooks throughout content**
3. **Optimize headers for keywords**
4. **Ensure semantic chunking**

**Status**: ⬜ Not Started | 🟡 In Progress | ✅ Complete

---

## Tasks

| # | Task | File | Status |
|---|------|------|--------|
| 1 | Optimize Keyword Density | task-1-optimize-keyword-density.md | ⬜ |
| 2 | Add Query Hooks | task-2-add-query-hooks.md | ⬜ |
| 3 | Optimize Headers | task-3-optimize-headers.md | ⬜ |
| 4 | Ensure Semantic Chunking | task-4-ensure-semantic-chunking.md | ⬜ |

---

## Validation Gate

🚨 **CRITICAL**: Phase 2 MUST complete successfully before proceeding.

**Evidence Required**:

| Evidence | Type | Validator | Description |
|----------|------|-----------|-------------|
| `keyword_density_tldr` | string | equals_high | TL;DR keyword density classification |
| `keyword_density_body` | string | equals_natural | Body keyword density classification |
| `query_hooks_count` | integer | greater_than_or_equal_5 | Number of query hooks |
| `headers_descriptive` | boolean | is_true | Headers are descriptive and keyword-rich |
| `semantic_chunks_valid` | boolean | is_true | Chunks are 100-500 tokens and complete |

**Human Approval**: False

---

## Navigation

**Start Here**: 🎯 NEXT-MANDATORY: task-1-optimize-keyword-density.md

**After Phase 2 Complete**: 🎯 NEXT-MANDATORY: ../3/phase.md
