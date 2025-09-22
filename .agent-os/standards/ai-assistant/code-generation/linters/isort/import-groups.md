# isort Import Groups

**🎯 Proper import grouping standards for the HoneyHive Python SDK**

## 🚨 **Critical Import Grouping Rules**

### **Standard Import Group Order**

```python
# 1. FUTURE imports (if any)
from __future__ import annotations

# 2. STANDARD LIBRARY imports
import hashlib
import logging
import os
from typing import Any, Dict, List, Optional

# 3. THIRD-PARTY imports
import pytest
import requests
from opentelemetry.trace import Status

# 4. FIRST-PARTY imports (honeyhive)
from honeyhive.tracer.core.base import HoneyHiveTracer
from honeyhive.utils.logger import safe_log

# 5. LOCAL FOLDER imports (relative imports)
from .utils import helper_function
from ..models import DataModel
```

### **Blank Lines Between Groups**

```python
# ❌ VIOLATION - No separation between groups
import logging
import pytest
from honeyhive.tracer.core.base import HoneyHiveTracer

# ✅ CORRECT - Blank lines separate groups
import logging

import pytest

from honeyhive.tracer.core.base import HoneyHiveTracer
```

## 📋 **Import Group Patterns**

### **Pattern 1: Test File Import Groups**

```python
# Standard library
import hashlib
import time
from typing import Any, Dict, List
from unittest.mock import Mock, patch

# Third-party
import pytest

# First-party (honeyhive)
from honeyhive.tracer.processing.otlp_exporter import HoneyHiveOTLPExporter
from honeyhive.utils.logger import safe_log

# Local (test utilities)
from tests.utils import create_test_span, generate_md5_id
```

### **Pattern 2: Production Code Import Groups**

```python
# Standard library
import logging
import os
from typing import Optional, Union

# Third-party
import requests
from opentelemetry.trace import Tracer
from opentelemetry.sdk.trace import ReadableSpan

# First-party (honeyhive)
from honeyhive.tracer.core.base import HoneyHiveTracer
from honeyhive.tracer.infra.environment import EnvironmentDetector
from honeyhive.utils.logger import safe_log
```

### **Pattern 3: Complex Import Groups**

```python
# Future
from __future__ import annotations

# Standard library - individual imports first
import hashlib
import logging
import os
import time

# Standard library - from imports, grouped by module
from typing import Any, Dict, List, Optional, Union
from unittest.mock import Mock, patch

# Third-party - individual imports first
import pytest
import requests

# Third-party - from imports, grouped by package
from opentelemetry.trace import Status, StatusCode, Tracer
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# First-party - grouped by module depth
from honeyhive.tracer.core.base import HoneyHiveTracer
from honeyhive.tracer.processing.otlp_exporter import HoneyHiveOTLPExporter
from honeyhive.tracer.processing.otlp_session import OTLPSessionConfig
from honeyhive.utils.logger import safe_log

# Local folder - relative imports
from .fixtures import create_mock_span
from ..utils import test_helper
```

## 🚨 **Import Group Violations**

### **Violation 1: Wrong Group Order**

```python
# ❌ VIOLATION - Third-party before standard library
import pytest
import logging
from honeyhive.tracer.core.base import HoneyHiveTracer

# ✅ CORRECT - Proper group order
import logging

import pytest

from honeyhive.tracer.core.base import HoneyHiveTracer
```

### **Violation 2: Mixed Groups**

```python
# ❌ VIOLATION - Standard library mixed with third-party
import logging
import pytest
from typing import Dict
import requests

# ✅ CORRECT - Properly grouped
import logging
from typing import Dict

import pytest
import requests
```

### **Violation 3: Missing Group Separation**

```python
# ❌ VIOLATION - No blank lines between groups
from typing import Dict
import pytest
from honeyhive.tracer.core.base import HoneyHiveTracer

# ✅ CORRECT - Blank lines separate groups
from typing import Dict

import pytest

from honeyhive.tracer.core.base import HoneyHiveTracer
```

## 📋 **HoneyHive-Specific Group Rules**

### **Rule 1: honeyhive Package Classification**

```python
# All honeyhive imports are FIRST-PARTY
from honeyhive.tracer.core.base import HoneyHiveTracer  # First-party
from honeyhive.utils.logger import safe_log  # First-party
from honeyhive.models import Event, EventType  # First-party
```

### **Rule 2: Test Utilities Classification**

```python
# Test utilities are LOCAL imports
from tests.utils import create_test_span  # Local
from tests.fixtures import mock_tracer  # Local
from tests.mocks import MockExporter  # Local
```

### **Rule 3: OpenTelemetry Classification**

```python
# OpenTelemetry imports are THIRD-PARTY
from opentelemetry.trace import Status  # Third-party
from opentelemetry.sdk.trace import ReadableSpan  # Third-party
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter  # Third-party
```

## 📋 **Import Group Organization**

### **Within Each Group: Alphabetical Order**

```python
# Standard library - alphabetical
import hashlib
import logging
import os
import time

# Standard library from imports - alphabetical by module, then by import
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, patch

# Third-party - alphabetical
import pytest
import requests

# Third-party from imports - alphabetical by package
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.trace import Status, StatusCode
```

### **Individual vs From Imports**

```python
# Within each group: individual imports first, then from imports
import logging
import os

from typing import Any, Dict
from unittest.mock import Mock
```

### **Submodule Organization**

```python
# First-party imports - organized by module depth
from honeyhive.tracer.core.base import HoneyHiveTracer
from honeyhive.tracer.processing.otlp_exporter import HoneyHiveOTLPExporter
from honeyhive.tracer.processing.otlp_session import OTLPSessionConfig
from honeyhive.utils.logger import safe_log
```

## 📋 **isort Configuration for Groups**

### **Project Configuration (pyproject.toml)**

```toml
[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["honeyhive"]
known_third_party = ["pytest", "requests", "opentelemetry"]
sections = ["FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
```

### **Custom Group Configuration**

```toml
[tool.isort]
# Custom sections for specific needs
sections = [
    "FUTURE",
    "STDLIB", 
    "THIRDPARTY",
    "FIRSTPARTY",
    "LOCALFOLDER"
]

# Known packages
known_first_party = ["honeyhive"]
known_third_party = [
    "pytest",
    "requests", 
    "opentelemetry",
    "pydantic"
]

# Test-specific configuration
known_local_folder = ["tests"]
```

## 📋 **Group-Specific Best Practices**

### **Practice 1: Minimize Groups**

```python
# ✅ GOOD - Only necessary groups
import logging
from typing import Dict

import pytest

from honeyhive.tracer.core.base import HoneyHiveTracer

# ❌ AVOID - Too many single-import groups
import logging

from typing import Dict

import pytest

from honeyhive.tracer.core.base import HoneyHiveTracer
```

### **Practice 2: Logical Grouping Within Sections**

```python
# ✅ GOOD - Related imports together
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, patch

from opentelemetry.trace import Status, StatusCode
from opentelemetry.sdk.trace import ReadableSpan

# ❌ AVOID - Scattered related imports
from typing import Dict
from unittest.mock import Mock
from typing import List
from unittest.mock import patch
```

### **Practice 3: Consistent Test Import Patterns**

```python
# Standard pattern for test files
from typing import Any, Dict, List
from unittest.mock import Mock, patch

import pytest

from honeyhive.tracer.processing.otlp_exporter import HoneyHiveOTLPExporter
from tests.utils import create_test_span
```

## 📋 **Import Group Checklist**

**Before finalizing imports:**

- [ ] **Correct group order**: FUTURE → STDLIB → THIRDPARTY → FIRSTPARTY → LOCALFOLDER
- [ ] **Blank lines between groups**: One blank line separating each group
- [ ] **Alphabetical within groups**: Imports sorted alphabetically
- [ ] **Individual before from**: `import x` before `from x import y`
- [ ] **Consistent honeyhive classification**: All honeyhive imports as first-party
- [ ] **Proper test utilities**: Test imports as local folder
- [ ] **No mixed groups**: Each group contains only its type of imports

## ⚡ **Quick Group Fixes**

### **Auto-fix Import Groups**
```bash
isort tests/unit/test_file.py
```

### **Check Import Groups**
```bash
isort --check-only --diff tests/unit/test_file.py
```

### **Manual Group Organization**
1. **Identify import types**: Standard library, third-party, first-party, local
2. **Group by type**: Put similar imports together
3. **Add blank lines**: Separate each group with blank line
4. **Sort within groups**: Alphabetical order within each group

---

**🎯 Remember**: Proper import grouping makes code more readable and maintainable. Use isort to automate this process.
