# Pylint Import Rules

**🎯 Import-specific Pylint compliance for AI assistants**

## 🚨 **Critical Import Rules**

### **W0611: Unused import**

**Most common import-related Pylint violation:**

```python
# ❌ VIOLATION - Unused imports
from typing import Dict, List, Optional, Any  # Any unused
from unittest.mock import Mock, patch, MagicMock  # MagicMock unused
import os  # os unused

def test_function() -> None:
    data: Dict[str, str] = {}
    items: List[str] = []
    config: Optional[str] = None
    mock_obj = Mock()
    # Any, MagicMock, os never used

# ✅ CORRECT - Only import what's used
from typing import Dict, List, Optional
from unittest.mock import Mock

def test_function() -> None:
    data: Dict[str, str] = {}
    items: List[str] = []
    config: Optional[str] = None
    mock_obj = Mock()
```

### **C0412: Imports from package not grouped**

```python
# ❌ VIOLATION - Mixed import styles from same package
from typing import Dict
import typing
from typing import List

# ✅ CORRECT - Group imports from same package
from typing import Dict, List
```

### **C0413: Import should be placed at the top of the module**

```python
# ❌ VIOLATION - Import after code
def some_function():
    pass

import logging  # Should be at top

# ✅ CORRECT - Imports at module top
import logging

def some_function():
    pass
```

## 📋 **Import Organization Patterns**

### **Pattern 1: Standard Import Order**

```python
# Future imports (if needed)
from __future__ import annotations

# Standard library - individual imports first
import hashlib
import logging
import os
import time

# Standard library - from imports, grouped and sorted
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, patch

# Third-party - individual imports first
import pytest
import requests

# Third-party - from imports, grouped and sorted
from opentelemetry.trace import Status, StatusCode
from opentelemetry.sdk.trace import ReadableSpan

# Local application - sorted by module depth
from honeyhive.tracer.core.base import HoneyHiveTracer
from honeyhive.tracer.processing.otlp_exporter import HoneyHiveOTLPExporter
from honeyhive.utils.logger import safe_log
```

### **Pattern 2: Test File Imports**

```python
# Standard library
import hashlib
import time
from typing import Any, Dict, List
from unittest.mock import Mock, patch

# Third-party
import pytest

# Local application - test utilities first
from tests.utils import create_test_span, generate_md5_id
from honeyhive.tracer.processing.otlp_exporter import HoneyHiveOTLPExporter
```

### **Pattern 3: Conditional Imports**

```python
# Standard imports at top
import logging
from typing import Optional

# Conditional imports (when necessary)
try:
    import ujson as json
except ImportError:
    import json

# Type checking imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from honeyhive.tracer.core.base import HoneyHiveTracer
```

## 🚨 **Import Violations to Avoid**

### **W0404: Reimported module**

```python
# ❌ VIOLATION - Module imported multiple times
import logging
from typing import Dict
import logging  # Reimported

# ✅ CORRECT - Import once
import logging
from typing import Dict
```

### **W0406: Module import itself**

```python
# ❌ VIOLATION - In file honeyhive/tracer/base.py
from honeyhive.tracer.base import SomeClass

# ✅ CORRECT - Use relative import or direct reference
from .other_module import SomeClass
```

### **C0415: Import outside toplevel**

```python
# ❌ VIOLATION - Import inside function (usually)
def process_data():
    import json  # Should be at module top
    return json.loads(data)

# ✅ CORRECT - Import at module top
import json

def process_data():
    return json.loads(data)

# ✅ ACCEPTABLE - When avoiding circular imports
def get_tracer():
    from honeyhive.tracer.core.base import HoneyHiveTracer
    return HoneyHiveTracer()
```

### **W0401: Wildcard import**

```python
# ❌ VIOLATION - Wildcard import
from honeyhive.models import *

# ✅ CORRECT - Explicit imports
from honeyhive.models import Event, EventType, Span
```

## 📋 **Import Best Practices**

### **Practice 1: Minimize Imports**

```python
# ❌ AVOID - Importing entire modules for single use
import datetime
import os.path

def get_timestamp():
    return datetime.datetime.now()

def get_filename(path):
    return os.path.basename(path)

# ✅ BETTER - Import specific functions
from datetime import datetime
from os.path import basename

def get_timestamp():
    return datetime.now()

def get_filename(path):
    return basename(path)
```

### **Practice 2: Use Aliases Sparingly**

```python
# ❌ AVOID - Unnecessary aliases
import logging as log
from typing import Dict as DictType

# ✅ CORRECT - Only alias when needed
import numpy as np  # Common convention
from honeyhive.tracer.processing.otlp_exporter import HoneyHiveOTLPExporter as OTLPExporter  # Long name
```

### **Practice 3: Group Related Imports**

```python
# ✅ GOOD - Logical grouping
# Core typing imports
from typing import Any, Dict, List, Optional

# Mock testing imports  
from unittest.mock import Mock, patch

# OpenTelemetry imports
from opentelemetry.trace import Status, StatusCode
from opentelemetry.sdk.trace import ReadableSpan

# HoneyHive imports
from honeyhive.tracer.core.base import HoneyHiveTracer
from honeyhive.utils.logger import safe_log
```

## 📋 **Import Planning Checklist**

**Before adding ANY import, verify:**

- [ ] **Import is actually used**: Remove unused imports immediately
- [ ] **Import is at module top**: Unless avoiding circular imports
- [ ] **Imports are grouped**: Standard library, third-party, local
- [ ] **Imports are sorted**: Alphabetically within groups
- [ ] **No wildcard imports**: Use explicit imports
- [ ] **No duplicate imports**: Each module imported once
- [ ] **Appropriate aliases**: Only when necessary for clarity
- [ ] **TYPE_CHECKING imports**: For type hints that cause circular imports

## ⚡ **Quick Import Fixes**

### **Remove Unused Imports**
```python
# Use your IDE's "Optimize Imports" or run:
# isort --remove-unused-imports filename.py
```

### **Fix Import Order**
```python
# Run isort to fix automatically:
# isort filename.py
```

### **Find Circular Imports**
```python
# Use TYPE_CHECKING for type-only imports:
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from honeyhive.tracer.core.base import HoneyHiveTracer
```

---

**🎯 Remember**: Clean imports make code more maintainable and prevent circular dependency issues.
