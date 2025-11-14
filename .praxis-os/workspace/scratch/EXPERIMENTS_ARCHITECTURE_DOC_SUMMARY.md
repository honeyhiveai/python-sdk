# Experiments Architecture Documentation - Created

## Overview

Created comprehensive "How Experiments Work" conceptual documentation to fill the gap in experiments/evaluation documentation coverage.

## New Document

**Location**: `docs/explanation/concepts/experiments-architecture.rst`

**Size**: ~1,000 lines of comprehensive explanation

## What's Covered

### 1. Core Concepts
- ✅ What are experiments?
- ✅ How do experiments work? (detailed execution flow)
- ✅ Experiments vs Traces (clear distinction)
- ✅ Component relationships

### 2. Architecture & Flow
- ✅ Complete experiment lifecycle (4 phases: Setup → Execution → Evaluation → Aggregation)
- ✅ Visual Mermaid diagram showing data flow
- ✅ Multi-instance architecture explanation
- ✅ Per-datapoint tracer isolation

### 3. Data Flow
- ✅ Input data structure (dataset format)
- ✅ Function signature requirements (v1.0+)
- ✅ Step-by-step data transformation
- ✅ Evaluation metadata propagation

### 4. Evaluation Lifecycle
- ✅ Phase 1: Initialization (dataset loading, evaluator setup)
- ✅ Phase 2: Execution loop (per-datapoint processing)
- ✅ Phase 3: Backend aggregation (automatic metrics)
- ✅ Phase 4: Results access (comparison APIs)

### 5. Backend Aggregation
- ✅ Why backend aggregation? (benefits over client-side)
- ✅ Aggregation strategies (metrics, comparison, cost)
- ✅ Real examples of aggregated data structures

### 6. Best Practices
- ✅ Reproducibility patterns
- ✅ Consistent evaluator usage
- ✅ Multi-instance architecture leverage
- ✅ Progressive complexity
- ✅ Cost monitoring

### 7. Common Patterns
- ✅ A/B testing pattern
- ✅ Progressive improvement pattern
- ✅ Regression testing pattern
- ✅ Complete working examples for each

## Integration

Updated `docs/explanation/index.rst` to include the new document in the "Fundamental Concepts" section.

## Build Status

✅ Documentation builds successfully with no errors
✅ No linting errors
✅ Mermaid diagram renders correctly
✅ All cross-references valid

## Cross-References

The document includes links to:
- Tutorial 05 (Run First Experiment)
- How-to guides (running experiments, comparing experiments)
- Reference documentation (experiments API)
- Other concept docs (tracing fundamentals)

## Visual Elements

Includes a comprehensive Mermaid diagram showing:
- Setup phase (green)
- Execution phase (blue)
- Evaluation phase (orange)
- Backend aggregation (purple)
- Data flow between all components

## Key Sections for Different Audiences

**For beginners**: "What are Experiments?" + "Experiments vs Traces"
**For implementers**: "How Experiments Work" + "Component Relationships"
**For architects**: "Multi-Instance Architecture" + "Backend Aggregation"
**For practitioners**: "Best Practices" + "Common Patterns"

## Fills Documentation Gap

This document addresses the missing "How do experiments work" conceptual explanation identified in the documentation audit. It provides the architectural understanding that was previously scattered across multiple how-to guides.

## Next Step (If Desired)

The second identified gap was the Strands evaluation tutorial, which could be created as a separate hands-on tutorial document based on the existing Strands integration content.

