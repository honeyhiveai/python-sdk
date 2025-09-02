# Agent OS - HoneyHive Python SDK

This directory contains the Agent OS configuration for the HoneyHive Python SDK project. Agent OS helps AI coding assistants understand and work with this codebase effectively.

## Directory Structure

```
.agent-os/
├── standards/              # Global coding standards
│   ├── tech-stack.md      # Technology choices and dependencies
│   ├── code-style.md      # Code formatting and style guide
│   └── best-practices.md  # Development best practices
├── product/               # Product documentation
│   ├── overview.md        # Product vision and architecture
│   ├── audience.md        # User personas and market segments
│   ├── roadmap.md         # Development roadmap
│   ├── features.md        # Feature catalog
│   └── decisions.md       # Technical decision log
└── specs/                 # Feature specifications
    └── 2025-01-15-performance-optimization/
        ├── srd.md         # Spec requirements document
        ├── specs.md       # Technical specifications
        └── tasks.md       # Task breakdown
```

## How to Use Agent OS

### For AI Assistants

When working with AI coding assistants (like Claude, GPT-4, etc.), reference these documents to ensure the AI understands:

1. **Project Context**: Point to `.agent-os/product/overview.md` for understanding the SDK's purpose
2. **Coding Standards**: Reference `.agent-os/standards/` for style and practices
3. **Feature Development**: Use specs in `.agent-os/specs/` as templates for new features

### Common Commands

```bash
# When starting a new feature
"Let's create a new spec following the pattern in .agent-os/specs/"

# When writing code
"Follow the code style defined in .agent-os/standards/code-style.md"

# When making decisions
"Check .agent-os/product/decisions.md for similar decisions"

# When testing
"Use tox as specified in .agent-os/standards/best-practices.md"
```

## Key Project Guidelines

### 🔴 Critical Rules
1. **ALWAYS use tox for testing** - Never run pytest directly
2. **Type hints are MANDATORY** - All functions must have type hints
3. **No code in `__init__.py`** - Only imports allowed
4. **Graceful degradation** - SDK must never crash the host application

### 🟡 Important Patterns
1. **Multi-instance support** - No singleton pattern
2. **Unified `@trace` decorator** - Works for both sync and async
3. **Environment variables** - Support HH_*, HTTP_*, EXPERIMENT_* patterns
4. **HTTP tracing off by default** - For better performance

### 🟢 Best Practices
1. **90% test coverage minimum**
2. **Black formatting with 88 char lines**
3. **Comprehensive docstrings**
4. **Error handling with logging**

## Quick Reference

### Initialize Tracer
```python
from honeyhive import HoneyHiveTracer

tracer = HoneyHiveTracer.init(
    api_key="hh_api_...",
    project="my-project",
    source="production"
)
```

### Use Decorators
```python
@trace(event_type="llm_call")
async def my_function():
    return await llm.complete(prompt)
```

### Run Tests
```bash
# Always use tox
tox -e py311        # Python 3.11 tests
tox -e unit         # Unit tests only
tox -e integration  # Integration tests
tox -e lint         # Linting
```

## Creating New Specs

When adding new features, create a spec following this structure:

```bash
.agent-os/specs/YYYY-MM-DD-feature-name/
├── srd.md    # Business requirements
├── specs.md  # Technical approach
└── tasks.md  # Implementation tasks
```

Use the performance optimization spec as a template.

## Updating Documentation

When making significant changes:
1. Update relevant files in `.agent-os/product/`
2. Add decisions to `decisions.md`
3. Update the roadmap if needed
4. Keep standards current

## Integration with Development

This Agent OS configuration aligns with:
- The complete-refactor branch architecture
- 203+ existing tests
- Production deployment requirements
- OpenTelemetry standards

## For Contributors

If you're contributing to the HoneyHive Python SDK:
1. Read through the standards before coding
2. Follow the patterns in existing specs
3. Update Agent OS docs when adding features
4. Use these docs when working with AI assistants

## Support

For questions about Agent OS or the HoneyHive SDK:
- Check the documentation in this directory
- Review the technical decisions log
- Consult the official HoneyHive docs at https://docs.honeyhive.ai
