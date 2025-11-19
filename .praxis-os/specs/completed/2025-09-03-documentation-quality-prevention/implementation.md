# Documentation Quality Prevention - Implementation Guide

## Quick Start: Immediate Prevention Measures

### 1. Enhanced Pre-commit Hook Setup

```bash
# Add to .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: rst-lint
        name: RST Syntax Check
        entry: python scripts/check-rst-quality.py
        language: python
        files: '\.rst$'
        
      - id: doc-code-test
        name: Test Documentation Code Examples
        entry: python scripts/test-doc-examples.py
        language: python
        files: '\.rst$'
        
      - id: type-safety-check
        name: Documentation Type Safety
        entry: python scripts/check-doc-types.py
        language: python
        files: '\.rst$'
```

### 2. Validation Script Templates

#### RST Quality Checker (`scripts/check-rst-quality.py`)

```python
#!/usr/bin/env python3
"""
RST Quality Checker - Prevents common documentation errors
"""
import re
import sys
from pathlib import Path
from typing import List, Tuple

class RSTQualityChecker:
    def __init__(self):
        self.errors = []
        
    def check_file(self, filepath: Path) -> List[str]:
        """Check a single RST file for quality issues."""
        content = filepath.read_text()
        lines = content.splitlines()
        
        # Check title underlines
        self._check_title_underlines(lines, filepath)
        
        # Check blank lines
        self._check_blank_lines(lines, filepath)
        
        # Check code block structure
        self._check_code_blocks(lines, filepath)
        
        # Check table formatting
        self._check_tables(lines, filepath)
        
        return self.errors
        
    def _check_title_underlines(self, lines: List[str], filepath: Path):
        """Ensure title underlines match title length."""
        for i, line in enumerate(lines[:-1]):
            next_line = lines[i + 1]
            if re.match(r'^[=-]{3,}$', next_line):
                if len(line.strip()) != len(next_line.strip()):
                    self.errors.append(
                        f"{filepath}:{i+2}: Title underline length mismatch"
                    )
                    
    def _check_blank_lines(self, lines: List[str], filepath: Path):
        """Check for required blank lines."""
        for i, line in enumerate(lines[:-1]):
            # Check blank line after headers
            if line.startswith('**') and line.endswith('**:'):
                next_line = lines[i + 1] if i + 1 < len(lines) else ""
                if next_line.strip() and not next_line.startswith('.. '):
                    self.errors.append(
                        f"{filepath}:{i+2}: Missing blank line after header"
                    )
                    
    def _check_code_blocks(self, lines: List[str], filepath: Path):
        """Validate code block structure."""
        in_code_block = False
        for i, line in enumerate(lines):
            if line.strip().startswith('.. code-block::'):
                in_code_block = True
                # Check for blank line after directive
                if i + 1 < len(lines) and lines[i + 1].strip():
                    self.errors.append(
                        f"{filepath}:{i+2}: Missing blank line after code-block directive"
                    )
            elif in_code_block and line and not line.startswith('   '):
                in_code_block = False
                
    def _check_tables(self, lines: List[str], filepath: Path):
        """Validate table formatting."""
        for i, line in enumerate(lines):
            if re.match(r'^[=+-]{3,}$', line):
                # Simple table border check
                if i > 0 and i < len(lines) - 1:
                    prev_line = lines[i - 1]
                    next_line = lines[i + 1]
                    if '|' in prev_line or '|' in next_line:
                        # More complex table validation needed
                        pass

def main():
    if len(sys.argv) < 2:
        print("Usage: check-rst-quality.py <file1.rst> [file2.rst] ...")
        sys.exit(1)
        
    checker = RSTQualityChecker()
    all_errors = []
    
    for filepath in sys.argv[1:]:
        path = Path(filepath)
        if path.exists():
            errors = checker.check_file(path)
            all_errors.extend(errors)
            
    if all_errors:
        print("RST Quality Issues Found:")
        for error in all_errors:
            print(f"  ❌ {error}")
        sys.exit(1)
    else:
        print("✅ All RST files pass quality checks")

if __name__ == "__main__":
    main()
```

#### Type Safety Checker (`scripts/check-doc-types.py`)

```python
#!/usr/bin/env python3
"""
Documentation Type Safety Checker
"""
import re
import sys
from pathlib import Path
from typing import List

def check_type_safety(filepath: Path) -> List[str]:
    """Check for type safety violations in documentation."""
    content = filepath.read_text()
    errors = []
    
    # Check for string literals in event_type parameters
    string_literal_pattern = r'event_type\s*=\s*["\'](\w+)["\']'
    matches = re.finditer(string_literal_pattern, content)
    
    for match in matches:
        line_num = content[:match.start()].count('\n') + 1
        event_type = match.group(1)
        errors.append(
            f"{filepath}:{line_num}: Use EventType.{event_type} instead of '{event_type}'"
        )
    
    # Check for missing imports when EventType is used
    if 'EventType.' in content:
        if 'from honeyhive.models import EventType' not in content:
            errors.append(f"{filepath}: Missing 'from honeyhive.models import EventType'")
    
    return errors

def main():
    if len(sys.argv) < 2:
        print("Usage: check-doc-types.py <file1.rst> [file2.rst] ...")
        sys.exit(1)
        
    all_errors = []
    
    for filepath in sys.argv[1:]:
        path = Path(filepath)
        if path.exists():
            errors = check_type_safety(path)
            all_errors.extend(errors)
            
    if all_errors:
        print("Type Safety Issues Found:")
        for error in all_errors:
            print(f"  ❌ {error}")
        sys.exit(1)
    else:
        print("✅ All documentation passes type safety checks")

if __name__ == "__main__":
    main()
```

#### Code Example Tester (`scripts/test-doc-examples.py`)

```python
#!/usr/bin/env python3
"""
Test all Python code examples in documentation
"""
import ast
import re
import sys
import tempfile
from pathlib import Path
from typing import List, Tuple

def extract_python_code_blocks(content: str) -> List[Tuple[int, str]]:
    """Extract Python code blocks from RST content."""
    code_blocks = []
    lines = content.splitlines()
    
    in_python_block = False
    current_block = []
    block_start = 0
    
    for i, line in enumerate(lines):
        if line.strip().startswith('.. code-block:: python'):
            in_python_block = True
            block_start = i + 1
            current_block = []
        elif in_python_block:
            if line and not line.startswith('   '):
                # End of code block
                if current_block:
                    code_blocks.append((block_start, '\n'.join(current_block)))
                in_python_block = False
                current_block = []
            elif line.startswith('   '):
                # Remove 3-space indentation
                current_block.append(line[3:])
            elif not line.strip():
                # Empty line in code block
                current_block.append('')
    
    # Handle case where file ends with code block
    if in_python_block and current_block:
        code_blocks.append((block_start, '\n'.join(current_block)))
    
    return code_blocks

def test_code_block(code: str) -> List[str]:
    """Test a single code block for syntax and imports."""
    errors = []
    
    # Test syntax
    try:
        ast.parse(code)
    except SyntaxError as e:
        errors.append(f"Syntax error: {e}")
        
    # Check for common issues
    if '@trace(' in code and 'from honeyhive' not in code:
        errors.append("Missing honeyhive import for @trace decorator")
        
    if 'EventType.' in code and 'from honeyhive.models import EventType' not in code:
        errors.append("Missing EventType import")
        
    return errors

def test_rst_file(filepath: Path) -> List[str]:
    """Test all code blocks in an RST file."""
    content = filepath.read_text()
    code_blocks = extract_python_code_blocks(content)
    all_errors = []
    
    for line_num, code in code_blocks:
        errors = test_code_block(code)
        for error in errors:
            all_errors.append(f"{filepath}:{line_num}: {error}")
    
    return all_errors

def main():
    if len(sys.argv) < 2:
        print("Usage: test-doc-examples.py <file1.rst> [file2.rst] ...")
        sys.exit(1)
        
    all_errors = []
    
    for filepath in sys.argv[1:]:
        path = Path(filepath)
        if path.exists():
            errors = test_rst_file(path)
            all_errors.extend(errors)
            
    if all_errors:
        print("Code Example Issues Found:")
        for error in all_errors:
            print(f"  ❌ {error}")
        sys.exit(1)
    else:
        print("✅ All code examples pass validation")

if __name__ == "__main__":
    main()
```

### 3. GitHub Actions Integration

```yaml
# .github/workflows/documentation-quality.yml
name: Documentation Quality Assurance

on:
  push:
    paths: ['docs/**', '.praxis-os/**']
  pull_request:
    paths: ['docs/**', '.praxis-os/**']

jobs:
  documentation-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          pip install sphinx sphinx-rtd-theme
          pip install -e .
          
      - name: RST Quality Check
        run: |
          python scripts/check-rst-quality.py docs/**/*.rst
          
      - name: Type Safety Check
        run: |
          python scripts/check-doc-types.py docs/**/*.rst
          
      - name: Test Code Examples
        run: |
          python scripts/test-doc-examples.py docs/**/*.rst
          
      - name: Build Documentation (No Warnings)
        run: |
          cd docs
          python -m sphinx -b html . _build/html -W -q
          
      - name: Check Documentation Coverage
        run: |
          python scripts/check-doc-coverage.py
```

### 4. Makefile Integration

```makefile
# Add to docs/Makefile
.PHONY: quality-check
quality-check:
	@echo "Running documentation quality checks..."
	@python ../scripts/check-rst-quality.py **/*.rst
	@python ../scripts/check-doc-types.py **/*.rst  
	@python ../scripts/test-doc-examples.py **/*.rst
	@echo "✅ All quality checks passed"

.PHONY: build-strict
build-strict: quality-check
	@echo "Building documentation with strict warnings..."
	python -m sphinx -b html . _build/html -W

.PHONY: fix-common-issues
fix-common-issues:
	@echo "Auto-fixing common documentation issues..."
	python ../scripts/auto-fix-rst.py **/*.rst
```

## Implementation Timeline

### Week 1: Foundation Setup
- [ ] Create validation scripts
- [ ] Add pre-commit hooks
- [ ] Test on current documentation

### Week 2: CI/CD Integration  
- [ ] Add GitHub Actions workflow
- [ ] Create quality dashboards
- [ ] Document new processes

### Week 3: Monitoring & Automation
- [ ] Deploy automated fixes
- [ ] Setup alerting
- [ ] Train team on new workflow

### Week 4: Optimization
- [ ] Analyze effectiveness
- [ ] Refine validation rules
- [ ] Create long-term maintenance plan

## Success Metrics

1. **Zero Build Failures**: 100% documentation builds succeed
2. **Fast Feedback**: Validation errors caught in < 30 seconds
3. **High Coverage**: 100% of documentation files validated
4. **Type Safety**: 100% enum usage compliance
5. **Developer Satisfaction**: Reduced frustration with documentation errors

This implementation guide provides practical, actionable steps to prevent the documentation quality issues we encountered, ensuring they never happen again through automation and validation.
