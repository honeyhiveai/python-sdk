# isort Import Sorting Standards

**🎯 Proper import organization using isort for the HoneyHive Python SDK**

## 🚨 **Critical Import Order**

**isort enforces specific import grouping and sorting. Follow this exact pattern:**

### **Standard Import Groups (in order)**

```python
# 1. FUTURE imports (if any)
from __future__ import annotations

# 2. STANDARD LIBRARY imports
import hashlib
import logging
import os
import time
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, patch

# 3. THIRD-PARTY imports  
import pytest
import requests
from opentelemetry.trace import Status, StatusCode

# 4. LOCAL APPLICATION imports
from honeyhive.tracer.core.base import HoneyHiveTracer
from honeyhive.tracer.processing.otlp_exporter import HoneyHiveOTLPExporter
from honeyhive.utils.logger import safe_log
```

## 📋 **isort Configuration (pyproject.toml)**

**The project uses these isort settings:**

```toml
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["honeyhive"]
known_third_party = ["pytest", "requests", "opentelemetry"]
sections = ["FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]
```

## 🔧 **Import Sorting Patterns**

### **Pattern 1: Test File Imports**

```python
# Standard library
import hashlib
import time
from typing import Any, Dict, List
from unittest.mock import Mock, patch

# Third-party
import pytest

# Local application
from honeyhive.tracer.processing.otlp_exporter import HoneyHiveOTLPExporter
from tests.utils import create_test_span
```

### **Pattern 2: Production Code Imports**

```python
# Standard library
import logging
import os
from typing import Optional

# Third-party
import requests
from opentelemetry.trace import Tracer

# Local application
from honeyhive.tracer.core.base import HoneyHiveTracer
from honeyhive.utils.logger import safe_log
```

### **Pattern 3: Complex Import Organization**

```python
# Future (if needed)
from __future__ import annotations

# Standard library - individual imports first
import hashlib
import logging
import os
import time

# Standard library - from imports, sorted alphabetically
from typing import Any, Dict, List, Optional, Union
from unittest.mock import Mock, patch

# Third-party - individual imports first
import pytest
import requests

# Third-party - from imports, sorted by module then by import
from opentelemetry.trace import Status, StatusCode, Tracer
from opentelemetry.sdk.trace import ReadableSpan

# Local application - sorted by module depth, then alphabetically
from honeyhive.tracer.core.base import HoneyHiveTracer
from honeyhive.tracer.processing.otlp_exporter import HoneyHiveOTLPExporter
from honeyhive.utils.logger import safe_log
```

## 🚨 **Common isort Violations**

### **Violation 1: Wrong Import Order**

```python
# ❌ WRONG - Third-party before standard library
import pytest
import logging
from honeyhive.tracer.core.base import HoneyHiveTracer
from typing import Dict

# ✅ CORRECT - Proper grouping and order
import logging
from typing import Dict

import pytest

from honeyhive.tracer.core.base import HoneyHiveTracer
```

### **Violation 2: Missing Blank Lines Between Groups**

```python
# ❌ WRONG - No separation between groups
import logging
import pytest
from honeyhive.tracer.core.base import HoneyHiveTracer

# ✅ CORRECT - Blank lines between groups
import logging

import pytest

from honeyhive.tracer.core.base import HoneyHiveTracer
```

### **Violation 3: Incorrect Alphabetical Order**

```python
# ❌ WRONG - Not alphabetically sorted
from typing import Dict, Any, List
from unittest.mock import patch, Mock

# ✅ CORRECT - Alphabetically sorted
from typing import Any, Dict, List
from unittest.mock import Mock, patch
```

## 📋 **isort Checklist**

**Before generating ANY Python file, ensure:**

- [ ] **Future imports first**: `from __future__ import annotations` if needed
- [ ] **Standard library second**: `import os`, `from typing import ...`
- [ ] **Third-party third**: `import pytest`, `from opentelemetry import ...`
- [ ] **Local application last**: `from honeyhive import ...`
- [ ] **Blank lines between groups**: One blank line separating each group
- [ ] **Alphabetical within groups**: Imports sorted alphabetically within each group
- [ ] **Individual imports before from imports**: `import os` before `from os import path`

## ⚡ **Quick Fixes**

### **Run isort to Auto-Fix**
```bash
# Fix import sorting automatically
isort tests/unit/test_file.py

# Check what would be changed (dry run)
isort --diff tests/unit/test_file.py
```

### **Manual Import Organization**
1. **Group imports** by type (stdlib, third-party, local)
2. **Add blank lines** between groups
3. **Sort alphabetically** within each group
4. **Put individual imports** before from imports

## 🎯 **HoneyHive-Specific Import Patterns**

### **For Test Files**
```python
# Standard library
from typing import Any, Dict, List
from unittest.mock import Mock, patch

# Third-party
import pytest

# Local - test utilities first, then production code
from tests.utils import create_test_span
from honeyhive.tracer.processing.otlp_exporter import HoneyHiveOTLPExporter
```

### **For Production Files**
```python
# Standard library
import logging
from typing import Optional

# Third-party
from opentelemetry.trace import Tracer

# Local - core modules first, then utilities
from honeyhive.tracer.core.base import HoneyHiveTracer
from honeyhive.utils.logger import safe_log
```

---

**🎯 Remember**: isort automatically handles most import organization. Run `isort filename.py` to fix violations.
