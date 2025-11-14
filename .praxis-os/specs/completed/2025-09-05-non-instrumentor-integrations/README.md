# Non-Instrumentor Integration Framework - Overview

**Date**: 2025-09-05  
**Status**: Draft  
**Priority**: High  
**Prototype**: AWS Strands Integration  

## Overview

This specification defines a framework for integrating HoneyHive with systems that use OpenTelemetry machinery directly, rather than through traditional instrumentors. AWS Strands serves as our prototype.

## Problem Solved

Many AI frameworks implement OpenTelemetry integration directly, creating challenges for traditional instrumentor-based integration patterns.

## Solution Delivered

A flexible integration framework that detects existing OpenTelemetry providers and integrates seamlessly regardless of initialization order.

## Current Status

✅ **Prototype Working**: AWS Strands integration demonstrates core concepts  
🔄 **Framework Development**: Generalizing patterns for broader ecosystem  

## Quick Start

```python
from honeyhive import HoneyHiveTracer
from strands import Agent  # Example: AWS Strands

# Works regardless of initialization order
tracer = HoneyHiveTracer.init(api_key="...", project="...")
agent = Agent(model="...", system_prompt="...")
response = agent("Your query")  # Automatically traced
```

## Validation Commands

```bash
# Test AWS Strands integration
python test_strands_simple.py
python test_strands_integration.py
./run_strands_tests.sh
```

## Key Files

- **`srd.md`**: Requirements and success criteria
- **`specs.md`**: Technical specifications and implementation details  
- **`tasks.md`**: Implementation tasks
- **`implementation.md`**: Implementation guide

---

**Next Steps**: Review detailed specifications in `specs.md` and implementation tasks in `tasks.md`.
