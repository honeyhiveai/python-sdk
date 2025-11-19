# Claude Code Configuration - HoneyHive Python SDK

## Project Context
This is the HoneyHive Python SDK (complete-refactor branch) - a comprehensive observability and evaluation platform for LLM applications.

## Agent OS Integration
The project uses Agent OS for structured development. Key directories:
- Standards: `.agent-os/standards/` - Global coding standards
- Product: `.agent-os/product/` - Product documentation
- Specs: `.agent-os/specs/` - Feature specifications

## Critical Project Rules

### 🔴 MUST FOLLOW
1. **ALWAYS use tox for testing** - Never run pytest directly
   ```bash
   tox -e py311  # Python 3.11 tests
   tox -e unit   # Unit tests only
   ```

2. **Type hints are MANDATORY** - All functions must have type hints
3. **No code in `__init__.py`** - Only imports allowed
4. **Use Black formatting** - Line length 88
5. **Multi-instance tracers** - No singleton pattern

### Key Patterns
- Unified `@trace` decorator works for both sync/async
- HTTP tracing disabled by default for performance
- Graceful degradation - never crash host application
- Environment variables: HH_*, HTTP_*, EXPERIMENT_*

## Quick Commands

### Testing
```bash
tox -e py311        # Test on Python 3.11
tox -e unit         # Run unit tests
tox -e integration  # Run integration tests
tox -e lint         # Run linting
```

### Common Patterns
```python
# Initialize tracer
from honeyhive import HoneyHiveTracer

tracer = HoneyHiveTracer.init(
    api_key="hh_api_...",
    project="my-project"
)

# Use decorators
@trace(event_type="llm_call")
async def my_function():
    return await process()
```

## Development Workflow
1. Check `.agent-os/product/roadmap.md` for current priorities
2. Create specs in `.agent-os/specs/` for new features
3. Follow standards in `.agent-os/standards/`
4. Update `.agent-os/product/decisions.md` for architectural choices

## References
- Product Overview: `.agent-os/product/overview.md`
- Code Style: `.agent-os/standards/code-style.md`
- Best Practices: `.agent-os/standards/best-practices.md`
- Technical Decisions: `.agent-os/product/decisions.md`
