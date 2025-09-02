# Code Style Standards - HoneyHive Python SDK

## Python Code Organization

### File Structure
```python
"""Module docstring - REQUIRED for all modules."""

# Standard library imports
import os
import sys
from typing import Any, Dict, Optional

# Third-party imports
import httpx
from pydantic import BaseModel

# Local imports (relative imports within package)
from ..utils.config import config
from ..utils.logger import get_logger

# Module-level constants
DEFAULT_TIMEOUT = 30.0
MAX_RETRIES = 3

# NO code in __init__.py files - only imports
```

### Naming Conventions
- **Classes**: PascalCase (e.g., `HoneyHiveTracer`, `SessionAPI`)
- **Functions/Methods**: snake_case (e.g., `start_span`, `create_event`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_TIMEOUT`, `MAX_CONNECTIONS`)
- **Private Members**: Leading underscore (e.g., `_internal_method`)
- **Async Functions**: Prefix with 'a' for dual implementations (e.g., `aevaluator`)
- **Module Files**: snake_case (e.g., `span_processor.py`)

### Type Hints (MANDATORY)
```python
# All functions must have type hints
def process_data(
    input_data: Dict[str, Any],
    timeout: Optional[float] = None,
    retry_count: int = 3
) -> Optional[Dict[str, Any]]:
    """Process data with retries."""
    pass

# Use modern Python 3.11+ syntax
def parse_response(data: str | bytes) -> dict[str, Any] | None:
    """Parse API response."""
    pass

# Class attributes with type hints
class APIClient:
    base_url: str
    api_key: Optional[str]
    timeout: float = 30.0
    _session: Optional[httpx.AsyncClient] = None
```

### Docstrings (REQUIRED)
```python
def create_event(
    self,
    event_type: str,
    inputs: Optional[Dict[str, Any]] = None,
    outputs: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """Create a HoneyHive event.
    
    Args:
        event_type: Type of event to create
        inputs: Input data for the event
        outputs: Output data from the event
        
    Returns:
        Event ID if successful, None otherwise
        
    Raises:
        APIError: If the API call fails
        ValidationError: If input validation fails
    """
    pass
```

### Error Handling
```python
# Specific exception catching
try:
    response = await client.post(url, json=data)
except httpx.TimeoutException as e:
    logger.error(f"Request timeout: {e}")
    raise APITimeoutError(f"Request timed out after {timeout}s") from e
except httpx.HTTPStatusError as e:
    logger.error(f"HTTP error {e.response.status_code}: {e}")
    raise APIError(f"API returned {e.response.status_code}") from e
except Exception as e:
    # Only catch generic Exception as last resort
    logger.error(f"Unexpected error: {e}")
    raise

# Graceful degradation
def enrich_span(self, metadata: Dict[str, Any]) -> bool:
    """Enrich span with metadata, returning success status."""
    try:
        # Attempt enrichment
        return True
    except Exception as e:
        if not self.test_mode:
            logger.warning(f"Failed to enrich span: {e}")
        return False  # Graceful failure
```

### Async/Sync Patterns
```python
# Unified decorator for both sync and async
@trace(event_type="api_call")
def sync_function():
    return "result"

@trace(event_type="api_call")
async def async_function():
    await asyncio.sleep(0.1)
    return "result"

# Dual implementation pattern
def evaluator(func):
    """Sync evaluator decorator."""
    pass

def aevaluator(func):
    """Async evaluator decorator."""
    pass
```

## Testing Style

### Test File Organization
```python
# File naming: test_<module>_<component>.py
# Example: test_api_client.py, test_tracer_decorators.py

import pytest
from unittest.mock import Mock, patch

from honeyhive.api.client import HoneyHive
from honeyhive.utils.config import Config

class TestHoneyHiveClient:
    """Test suite for HoneyHive client."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return HoneyHive(api_key="test-key")
    
    def test_initialization(self, client):
        """Test client initialization."""
        # Arrange-Act-Assert pattern
        assert client.api_key == "test-key"
        assert client.base_url == "https://api.honeyhive.ai"
```

### Test Patterns
```python
# Use tox for all testing - NEVER run pytest directly
# tox -e unit      # Unit tests only
# tox -e integration  # Integration tests
# tox -e py311    # Python 3.11 tests

# Parametrized tests for multiple scenarios
@pytest.mark.parametrize("input_data,expected", [
    ({"key": "value"}, True),
    ({}, False),
    (None, False),
])
def test_validation(input_data, expected):
    """Test input validation."""
    assert validate(input_data) == expected

# Async test support
@pytest.mark.asyncio
async def test_async_operation():
    """Test async operation."""
    result = await async_function()
    assert result == "expected"
```

## Code Formatting Rules

### Black Configuration
- Line length: 88 characters
- Target Python: 3.11, 3.12, 3.13
- String quotes: Double quotes preferred
- Always run on save in editors

### Import Organization (isort)
```python
# Standard library
import json
import os
from typing import Any, Dict, Optional

# Third-party packages
import httpx
from pydantic import BaseModel

# Local imports
from honeyhive.utils import logger
from honeyhive.api.base import BaseAPI
```

### Linting Rules (pylint)
- Maximum line length: 88
- Maximum arguments: 15
- Maximum attributes: 20
- Maximum locals: 25
- Disable specific warnings in pyproject.toml

## Git Workflow

### Branch Naming
- `feature/<description>` - New features
- `fix/<issue-number>-<description>` - Bug fixes
- `refactor/<component>` - Code refactoring
- `docs/<description>` - Documentation updates
- `release/<version>` - Release branches

### Commit Messages
```
<type>(<scope>): <subject>

<body>

<footer>

# Examples:
feat(tracer): add unified @trace decorator
fix(api): handle timeout errors gracefully
docs(readme): update installation instructions
refactor(utils): simplify config loading
```

### Pull Request Standards
- Clear title describing the change
- Link to relevant issues
- Include test coverage
- Update documentation
- Pass all CI checks

## Documentation Standards

### README Structure
1. Project description
2. Key features
3. Installation
4. Quick start
5. Configuration
6. Examples
7. API reference
8. Contributing

### Code Comments
```python
# Use comments sparingly - code should be self-documenting
# Comments explain WHY, not WHAT

# Workaround for OpenTelemetry bug #1234
# TODO: Remove when OTEL 1.21 is released
# FIXME: This is a temporary solution

# Complex logic explanation
# We batch events to reduce API calls while ensuring
# data is sent within the latency window
```

### API Documentation
- OpenAPI 3.0 specification
- Include request/response examples
- Document all error codes
- Provide rate limit information

## Quality Standards

### Code Review Checklist
- [ ] Type hints on all functions
- [ ] Docstrings on all public methods
- [ ] Tests for new functionality
- [ ] No hardcoded values
- [ ] Error handling implemented
- [ ] Documentation updated
- [ ] Black/isort formatting applied
- [ ] Tox tests passing

### Performance Guidelines
- Profile before optimizing
- Avoid premature optimization
- Use generators for large datasets
- Cache expensive computations
- Pool connections
- Batch operations

### Security Practices
- Never log sensitive data
- Validate all inputs
- Use parameterized queries
- Implement rate limiting
- Follow OWASP guidelines
