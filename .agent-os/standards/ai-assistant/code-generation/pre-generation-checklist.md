# Pre-Generation Checklist

## 🎯 **PRE-GENERATION VALIDATION OVERVIEW**

**Purpose**: Ensure all prerequisites are met before beginning any code generation process.

**Scope**: Environment validation, tool availability, configuration verification, and readiness assessment.

---

## 📋 **MANDATORY PRE-GENERATION COMMANDS**

### **Command 1: Environment Validation**
```bash
# AI MUST verify development environment is properly configured
echo "Environment validation: [PYTHON_VERSION, VIRTUAL_ENV, DEPENDENCIES] verified"
```

**Required Output:**
- Python version 3.11+ confirmed
- Virtual environment activated
- Required dependencies installed
- Development tools available

### **Command 2: Tool Availability Check**
```bash
# AI MUST verify all required tools are available and configured
echo "Tool availability: [PYLINT, MYPY, BLACK, TOX] available and configured"
```

**Required Output:**
- Pylint available with correct configuration
- MyPy available with strict settings
- Black formatter available
- Tox testing framework available
- All tools properly configured

### **Command 3: Project Structure Validation**
```bash
# AI MUST verify project structure supports code generation
echo "Project structure: [SRC_DIRECTORY, TEST_DIRECTORY, CONFIG_FILES] validated"
```

**Required Output:**
- Source directory structure confirmed
- Test directory structure confirmed
- Configuration files present and valid
- Import paths working correctly

### **Command 4: Quality Standards Verification**
```bash
# AI MUST verify quality standards are achievable
echo "Quality standards: [PYLINT_CONFIG, MYPY_CONFIG, COVERAGE_CONFIG] verified"
```

**Required Output:**
- Pylint configuration supports 10.0/10 target
- MyPy configuration enables strict typing
- Coverage configuration set for required thresholds
- Quality gates properly configured

---

## 🔍 **ENVIRONMENT VALIDATION CHECKLIST**

### **✅ Python Environment**
- [ ] **Python Version**: 3.11+ installed and active
- [ ] **Virtual Environment**: Activated and named correctly
- [ ] **Package Manager**: pip available and up-to-date
- [ ] **Environment Variables**: Required variables set

```bash
# Validation commands
python --version  # Should be 3.11+
which python     # Should point to virtual environment
pip --version    # Should be latest version
echo $VIRTUAL_ENV # Should show active environment
```

### **✅ Development Dependencies**
- [ ] **Core Dependencies**: All project dependencies installed
- [ ] **Development Tools**: Linting and formatting tools available
- [ ] **Testing Framework**: Testing tools and fixtures ready
- [ ] **Documentation Tools**: Sphinx and related tools available

```bash
# Dependency validation
pip list | grep -E "(pylint|mypy|black|pytest|sphinx)"
tox --version
coverage --version
```

### **✅ Project Configuration**
- [ ] **pyproject.toml**: Present and properly configured
- [ ] **tox.ini**: Testing environments configured
- [ ] **pytest.ini**: Test configuration present
- [ ] **.pylintrc**: Linting rules configured

```bash
# Configuration validation
test -f pyproject.toml && echo "pyproject.toml found"
test -f tox.ini && echo "tox.ini found"
test -f pytest.ini && echo "pytest.ini found"
test -f .pylintrc && echo ".pylintrc found"
```

---

## 🛠️ **TOOL CONFIGURATION VALIDATION**

### **Pylint Configuration Check**
```python
def validate_pylint_config():
    """Validate Pylint configuration for code generation."""
    required_settings = {
        'max-line-length': 88,
        'good-names': ['i', 'j', 'k', 'ex', 'Run', '_'],
        'disable': ['too-few-public-methods'],  # May be overridden per case
    }
    
    # Check pylint configuration file
    config_file = find_pylint_config()
    if not config_file:
        raise ConfigurationError("Pylint configuration file not found")
    
    # Validate configuration settings
    config = parse_pylint_config(config_file)
    for setting, expected_value in required_settings.items():
        if setting not in config:
            raise ConfigurationError(f"Missing Pylint setting: {setting}")
    
    # Test pylint execution
    result = run_pylint_test()
    if result.returncode != 0:
        raise ConfigurationError("Pylint execution test failed")
    
    return True
```

### **MyPy Configuration Check**
```python
def validate_mypy_config():
    """Validate MyPy configuration for strict typing."""
    required_settings = {
        'python_version': '3.11',
        'strict': True,
        'disallow_untyped_defs': True,
        'disallow_incomplete_defs': True,
        'check_untyped_defs': True,
        'disallow_untyped_decorators': True,
        'no_implicit_optional': True,
        'warn_redundant_casts': True,
        'warn_unused_ignores': True,
    }
    
    # Check mypy configuration
    config_file = find_mypy_config()  # mypy.ini or pyproject.toml
    if not config_file:
        raise ConfigurationError("MyPy configuration not found")
    
    # Validate strict typing settings
    config = parse_mypy_config(config_file)
    for setting, expected_value in required_settings.items():
        if config.get(setting) != expected_value:
            raise ConfigurationError(f"MyPy setting '{setting}' should be {expected_value}")
    
    # Test mypy execution
    result = run_mypy_test()
    if result.returncode != 0:
        raise ConfigurationError("MyPy execution test failed")
    
    return True
```

### **Black Configuration Check**
```python
def validate_black_config():
    """Validate Black formatter configuration."""
    required_settings = {
        'line-length': 88,
        'target-version': ['py311'],
        'include': r'\.pyi?$',
        'extend-exclude': r'''
        /(
            \.eggs
          | \.git
          | \.hg
          | \.mypy_cache
          | \.tox
          | \.venv
          | _build
          | buck-out
          | build
          | dist
        )/
        '''
    }
    
    # Check black configuration
    config = find_black_config()  # pyproject.toml [tool.black]
    if not config:
        raise ConfigurationError("Black configuration not found")
    
    # Validate formatting settings
    for setting, expected_value in required_settings.items():
        if setting not in config:
            raise ConfigurationError(f"Missing Black setting: {setting}")
    
    # Test black execution
    result = run_black_test()
    if result.returncode != 0:
        raise ConfigurationError("Black execution test failed")
    
    return True
```

### **Tox Configuration Check**
```python
def validate_tox_config():
    """Validate Tox testing configuration."""
    required_environments = [
        'lint',      # Linting environment
        'mypy',      # Type checking environment
        'format',    # Code formatting environment
        'unit',      # Unit testing environment
        'integration' # Integration testing environment
    ]
    
    # Check tox configuration file
    config_file = Path('tox.ini')
    if not config_file.exists():
        raise ConfigurationError("tox.ini not found")
    
    # Parse tox configuration
    config = parse_tox_config(config_file)
    
    # Validate required environments
    for env in required_environments:
        if env not in config.get('envlist', []):
            raise ConfigurationError(f"Missing tox environment: {env}")
    
    # Validate environment configurations
    for env in required_environments:
        env_config = config.get(f'testenv:{env}', {})
        if not env_config:
            raise ConfigurationError(f"Missing configuration for tox environment: {env}")
    
    # Test tox execution
    result = run_tox_test()
    if result.returncode != 0:
        raise ConfigurationError("Tox execution test failed")
    
    return True
```

---

## 📁 **PROJECT STRUCTURE VALIDATION**

### **Source Directory Structure**
```
src/
├── honeyhive/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── generated.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── logger.py
│   └── api/
│       ├── __init__.py
│       └── client.py
```

### **Test Directory Structure**
```
tests/
├── __init__.py
├── unit/
│   ├── __init__.py
│   ├── test_models/
│   │   ├── __init__.py
│   │   └── test_generated.py
│   └── test_utils/
│       ├── __init__.py
│       ├── test_config.py
│       └── test_logger.py
├── integration/
│   ├── __init__.py
│   └── test_api/
│       ├── __init__.py
│       └── test_client.py
└── fixtures/
    ├── __init__.py
    └── sample_data.py
```

### **Configuration Files Structure**
```
project_root/
├── pyproject.toml      # Project configuration
├── tox.ini            # Testing environments
├── pytest.ini        # Test configuration
├── .pylintrc          # Linting rules
├── mypy.ini           # Type checking config
└── .env.example       # Environment variables template
```

---

## 🎯 **QUALITY STANDARDS VERIFICATION**

### **Quality Targets Validation**
```python
def validate_quality_targets():
    """Validate that quality targets are achievable with current configuration."""
    
    # Test Pylint configuration achieves 10.0/10
    pylint_result = test_pylint_score()
    if pylint_result.score < 10.0:
        raise QualityError(f"Pylint configuration cannot achieve 10.0/10 (current: {pylint_result.score})")
    
    # Test MyPy configuration achieves 0 errors
    mypy_result = test_mypy_errors()
    if mypy_result.error_count > 0:
        raise QualityError(f"MyPy configuration has {mypy_result.error_count} errors")
    
    # Test coverage configuration meets thresholds
    coverage_result = test_coverage_config()
    if coverage_result.threshold < 80:
        raise QualityError(f"Coverage threshold too low: {coverage_result.threshold}%")
    
    # Test documentation generation works
    docs_result = test_documentation_generation()
    if not docs_result.success:
        raise QualityError("Documentation generation failed")
    
    return True
```

### **Import Path Validation**
```python
def validate_import_paths():
    """Validate that import paths work correctly for code generation."""
    
    # Test basic project imports
    try:
        import honeyhive
        from honeyhive.models import generated
        from honeyhive.utils import config, logger
    except ImportError as e:
        raise ImportError(f"Basic project imports failed: {e}")
    
    # Test test imports
    try:
        import tests
        from tests.fixtures import sample_data
    except ImportError as e:
        raise ImportError(f"Test imports failed: {e}")
    
    # Test relative imports work
    test_relative_imports()
    
    return True
```

---

## 📊 **PRE-GENERATION VALIDATION REPORT**

### **Validation Result Structure**
```python
@dataclass
class PreGenerationValidationResult:
    """Pre-generation validation result."""
    
    # Environment validation
    environment_valid: bool
    python_version: str
    virtual_env_active: bool
    dependencies_installed: bool
    
    # Tool validation
    tools_available: bool
    pylint_configured: bool
    mypy_configured: bool
    black_configured: bool
    tox_configured: bool
    
    # Project structure validation
    structure_valid: bool
    source_structure_valid: bool
    test_structure_valid: bool
    config_files_present: bool
    
    # Quality standards validation
    quality_standards_valid: bool
    quality_targets_achievable: bool
    import_paths_working: bool
    
    # Overall readiness
    ready_for_generation: bool
    blocking_issues: List[str]
    warnings: List[str]
    recommendations: List[str]

def generate_pre_generation_report(result: PreGenerationValidationResult) -> str:
    """Generate pre-generation validation report."""
    
    status = "✅ READY" if result.ready_for_generation else "❌ NOT READY"
    
    report = f"""
# Pre-Generation Validation Report

## 🎯 Overall Status: {status}

## 🔧 Environment Validation
- **Python Version**: {result.python_version}
- **Virtual Environment**: {'✅ Active' if result.virtual_env_active else '❌ Inactive'}
- **Dependencies**: {'✅ Installed' if result.dependencies_installed else '❌ Missing'}

## 🛠️ Tool Validation
- **Pylint**: {'✅ Configured' if result.pylint_configured else '❌ Not Configured'}
- **MyPy**: {'✅ Configured' if result.mypy_configured else '❌ Not Configured'}
- **Black**: {'✅ Configured' if result.black_configured else '❌ Not Configured'}
- **Tox**: {'✅ Configured' if result.tox_configured else '❌ Not Configured'}

## 📁 Project Structure
- **Source Structure**: {'✅ Valid' if result.source_structure_valid else '❌ Invalid'}
- **Test Structure**: {'✅ Valid' if result.test_structure_valid else '❌ Invalid'}
- **Config Files**: {'✅ Present' if result.config_files_present else '❌ Missing'}

## 🎯 Quality Standards
- **Standards Valid**: {'✅ Yes' if result.quality_standards_valid else '❌ No'}
- **Targets Achievable**: {'✅ Yes' if result.quality_targets_achievable else '❌ No'}
- **Import Paths**: {'✅ Working' if result.import_paths_working else '❌ Broken'}

## 🚨 Blocking Issues
"""
    
    if result.blocking_issues:
        for issue in result.blocking_issues:
            report += f"- ❌ {issue}\n"
    else:
        report += "- ✅ No blocking issues found\n"
    
    report += "\n## ⚠️ Warnings\n"
    if result.warnings:
        for warning in result.warnings:
            report += f"- ⚠️ {warning}\n"
    else:
        report += "- ✅ No warnings\n"
    
    report += "\n## 💡 Recommendations\n"
    if result.recommendations:
        for recommendation in result.recommendations:
            report += f"- 💡 {recommendation}\n"
    else:
        report += "- ✅ No recommendations\n"
    
    return report
```

---

## 🚨 **PRE-GENERATION GATE CRITERIA**

### **✅ READY FOR GENERATION WHEN:**

#### **Environment Requirements (25%)**
- [ ] Python 3.11+ installed and active
- [ ] Virtual environment activated
- [ ] All dependencies installed
- [ ] Environment variables configured

#### **Tool Requirements (25%)**
- [ ] Pylint available and configured for 10.0/10
- [ ] MyPy available and configured for strict typing
- [ ] Black available and configured for formatting
- [ ] Tox available with all required environments

#### **Project Structure Requirements (25%)**
- [ ] Source directory structure valid
- [ ] Test directory structure valid
- [ ] Configuration files present and valid
- [ ] Import paths working correctly

#### **Quality Standards Requirements (25%)**
- [ ] Quality targets achievable with current configuration
- [ ] All quality gates properly configured
- [ ] Documentation generation working
- [ ] No blocking configuration issues

### **❌ NOT READY FOR GENERATION IF:**
- Python version below 3.11
- Virtual environment not activated
- Required tools missing or misconfigured
- Project structure invalid or incomplete
- Quality targets not achievable
- Import paths broken
- Blocking configuration issues present

---

## 🔄 **AUTOMATED PRE-GENERATION VALIDATION**

### **Validation Script**
```python
#!/usr/bin/env python3
"""
Automated Pre-Generation Validation Script

This script performs comprehensive validation of the development
environment before beginning code generation.
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Tuple

def run_pre_generation_validation() -> PreGenerationValidationResult:
    """Run complete pre-generation validation."""
    print("🔍 Starting pre-generation validation...")
    
    # Environment validation
    env_result = validate_environment()
    
    # Tool validation
    tool_result = validate_tools()
    
    # Project structure validation
    structure_result = validate_project_structure()
    
    # Quality standards validation
    quality_result = validate_quality_standards()
    
    # Compile results
    result = PreGenerationValidationResult(
        environment_valid=env_result.valid,
        python_version=env_result.python_version,
        virtual_env_active=env_result.venv_active,
        dependencies_installed=env_result.deps_installed,
        tools_available=tool_result.valid,
        pylint_configured=tool_result.pylint_ok,
        mypy_configured=tool_result.mypy_ok,
        black_configured=tool_result.black_ok,
        tox_configured=tool_result.tox_ok,
        structure_valid=structure_result.valid,
        source_structure_valid=structure_result.source_ok,
        test_structure_valid=structure_result.test_ok,
        config_files_present=structure_result.config_ok,
        quality_standards_valid=quality_result.valid,
        quality_targets_achievable=quality_result.targets_ok,
        import_paths_working=quality_result.imports_ok,
        ready_for_generation=all([
            env_result.valid,
            tool_result.valid,
            structure_result.valid,
            quality_result.valid
        ]),
        blocking_issues=collect_blocking_issues(env_result, tool_result, structure_result, quality_result),
        warnings=collect_warnings(env_result, tool_result, structure_result, quality_result),
        recommendations=generate_recommendations(env_result, tool_result, structure_result, quality_result)
    )
    
    # Generate and save report
    report = generate_pre_generation_report(result)
    report_path = Path("pre_generation_validation_report.md")
    report_path.write_text(report)
    
    print(f"✅ Validation complete. Ready: {result.ready_for_generation}")
    print(f"📋 Report saved to: {report_path}")
    
    if not result.ready_for_generation:
        print("❌ Environment not ready for code generation")
        print("🔧 Please address blocking issues before proceeding")
        sys.exit(1)
    
    return result

if __name__ == "__main__":
    run_pre_generation_validation()
```

---

**💡 Key Principle**: Pre-generation validation ensures that the development environment is properly configured and ready for high-quality code generation, preventing issues and ensuring consistent results.
