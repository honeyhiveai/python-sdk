#!/usr/bin/env python3
"""
V3 Framework Test Generator

Main orchestrator for the V3 test generation framework.
Executes all 8 phases systematically and generates high-quality test files.
"""

import sys
import os
import argparse
import subprocess
import json
from pathlib import Path
from datetime import datetime
import tempfile


class V3FrameworkExecutor:
    def __init__(self, production_file: str, test_type: str, output_dir: str = None):
        self.production_file = Path(production_file)
        self.test_type = test_type.lower()
        self.output_dir = (
            Path(output_dir) if output_dir else self._determine_output_dir()
        )
        self.analysis_results = {}
        self.generated_test_file = None
        self.framework_root = Path(
            ".praxis-os/standards/development/code-generation/tests/v3"
        )

        if self.test_type not in ["unit", "integration"]:
            raise ValueError("Test type must be 'unit' or 'integration'")

    def _determine_output_dir(self) -> Path:
        """Determine output directory based on test type."""
        if self.test_type == "unit":
            return Path("tests/unit")
        else:
            return Path("tests/integration")

    def _generate_test_filename(self) -> str:
        """Generate test file name from production file."""
        prod_name = self.production_file.stem
        if self.test_type == "integration":
            return f"test_{prod_name}_integration.py"
        else:
            return f"test_{prod_name}.py"

    def execute_phase_1_through_5(self) -> dict:
        """Execute analysis phases 1-5 and collect results."""
        print("🔍 Executing Analysis Phases 1-5...")

        # Phase 1: Method Verification
        print("Phase 1: Method Verification", end=" ")
        phase1_result = self._analyze_methods()
        print("✅" if phase1_result["success"] else "❌")

        # Phase 2: Logging Analysis
        print("Phase 2: Logging Analysis", end=" ")
        phase2_result = self._analyze_logging()
        print("✅" if phase2_result["success"] else "❌")

        # Phase 3: Dependency Analysis
        print("Phase 3: Dependency Analysis", end=" ")
        phase3_result = self._analyze_dependencies()
        print("✅" if phase3_result["success"] else "❌")

        # Phase 4: Usage Pattern Analysis
        print("Phase 4: Usage Pattern Analysis", end=" ")
        phase4_result = self._analyze_usage_patterns()
        print("✅" if phase4_result["success"] else "❌")

        # Phase 5: Coverage Analysis
        print("Phase 5: Coverage Analysis", end=" ")
        phase5_result = self._analyze_coverage()
        print("✅" if phase5_result["success"] else "❌")

        return {
            "phase1": phase1_result,
            "phase2": phase2_result,
            "phase3": phase3_result,
            "phase4": phase4_result,
            "phase5": phase5_result,
        }

    def _analyze_methods(self) -> dict:
        """Execute Phase 1: Method Verification."""
        try:
            # Use AST to analyze methods
            import ast

            with open(self.production_file, "r") as f:
                tree = ast.parse(f.read())

            functions = []
            classes = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.col_offset == 0:
                    functions.append(
                        {
                            "name": node.name,
                            "line": node.lineno,
                            "args": [arg.arg for arg in node.args.args],
                            "is_private": node.name.startswith("_"),
                        }
                    )
                elif isinstance(node, ast.ClassDef):
                    class_methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_methods.append(
                                {
                                    "name": item.name,
                                    "line": item.lineno,
                                    "args": [arg.arg for arg in item.args.args],
                                    "is_private": item.name.startswith("_"),
                                }
                            )
                    classes.append(
                        {
                            "name": node.name,
                            "line": node.lineno,
                            "methods": class_methods,
                        }
                    )

            return {
                "success": True,
                "functions": functions,
                "classes": classes,
                "total_functions": len(functions),
                "total_methods": sum(len(cls["methods"]) for cls in classes),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _analyze_logging(self) -> dict:
        """Execute Phase 2: Logging Analysis."""
        try:
            with open(self.production_file, "r") as f:
                content = f.read()

            # Count logging patterns
            import re

            log_calls = len(re.findall(r"log\.", content))
            safe_log_calls = len(re.findall(r"safe_log", content))
            logging_imports = len(re.findall(r"import.*log|from.*log", content))

            return {
                "success": True,
                "log_calls": log_calls,
                "safe_log_calls": safe_log_calls,
                "logging_imports": logging_imports,
                "total_logging": log_calls + safe_log_calls,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _analyze_dependencies(self) -> dict:
        """Execute Phase 3: Dependency Analysis."""
        try:
            with open(self.production_file, "r") as f:
                content = f.read()

            import re

            # Find all imports
            import_lines = re.findall(
                r"^(import|from.*import).*$", content, re.MULTILINE
            )
            external_deps = [
                line
                for line in import_lines
                if any(
                    lib in line for lib in ["requests", "opentelemetry", "os", "sys"]
                )
            ]
            internal_deps = [line for line in import_lines if "honeyhive" in line]

            return {
                "success": True,
                "total_imports": len(import_lines),
                "external_dependencies": len(external_deps),
                "internal_dependencies": len(internal_deps),
                "import_lines": import_lines,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _analyze_usage_patterns(self) -> dict:
        """Execute Phase 4: Usage Pattern Analysis."""
        try:
            with open(self.production_file, "r") as f:
                content = f.read()

            import re

            # Analyze control flow and patterns
            if_statements = len(re.findall(r"^\s*if\s+", content, re.MULTILINE))
            try_blocks = len(re.findall(r"^\s*try:", content, re.MULTILINE))
            function_calls = len(re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*\(", content))

            return {
                "success": True,
                "if_statements": if_statements,
                "try_blocks": try_blocks,
                "function_calls": function_calls,
                "complexity_score": if_statements + try_blocks + (function_calls // 10),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _analyze_coverage(self) -> dict:
        """Execute Phase 5: Coverage Analysis."""
        try:
            with open(self.production_file, "r") as f:
                lines = f.readlines()

            # Count executable lines (non-comment, non-blank)
            executable_lines = len(
                [
                    line
                    for line in lines
                    if line.strip() and not line.strip().startswith("#")
                ]
            )

            coverage_target = (
                90.0 if self.test_type == "unit" else 0.0
            )  # Integration focuses on functionality

            return {
                "success": True,
                "total_lines": len(lines),
                "executable_lines": executable_lines,
                "coverage_target": coverage_target,
                "test_type": self.test_type,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_phase_6_validation(self) -> bool:
        """Execute Phase 6: Pre-Generation Validation."""
        print("Phase 6: Pre-Generation Validation", end=" ")

        # Check prerequisites
        prerequisites = [
            self.production_file.exists(),
            self.output_dir.exists()
            or self.output_dir.mkdir(parents=True, exist_ok=True),
            self.framework_root.exists(),
        ]

        success = all(prerequisites)
        print("✅" if success else "❌")
        return success

    def generate_test_file(self) -> Path:
        """Generate the actual test file using templates and analysis."""
        print("🔧 Generating test file...")

        test_filename = self._generate_test_filename()
        self.generated_test_file = self.output_dir / test_filename

        # Generate test content based on analysis and templates
        test_content = self._build_test_content()

        # Write test file
        with open(self.generated_test_file, "w") as f:
            f.write(test_content)

        print(f"📝 Generated: {self.generated_test_file}")
        return self.generated_test_file

    def _build_test_content(self) -> str:
        """Build test file content from templates and analysis."""
        # Get analysis results
        phase1 = self.analysis_results.get("phase1", {})
        phase2 = self.analysis_results.get("phase2", {})
        phase3 = self.analysis_results.get("phase3", {})

        # Build imports
        imports = self._build_imports()

        # Build test class
        class_name = f"Test{self.production_file.stem.title().replace('_', '')}"
        if self.test_type == "integration":
            class_name += "Integration"

        # Build test methods
        test_methods = self._build_test_methods()

        # Combine into full test file
        content = f'''"""
Test file for {self.production_file.name}

Generated by V3 Framework - {self.test_type.title()} Tests
"""

{imports}


class {class_name}:
    """Test class for {self.production_file.stem} functionality."""

{test_methods}
'''

        return content

    def _build_imports(self) -> str:
        """Build import section based on test type."""
        if self.test_type == "unit":
            return """import pytest
from unittest.mock import Mock, patch, PropertyMock
from honeyhive.tracer.instrumentation.initialization import *"""
        else:
            return """import pytest
import os
from honeyhive.tracer.instrumentation.initialization import *
from honeyhive.tracer.base import HoneyHiveTracer"""

    def _build_test_methods(self) -> str:
        """Build test methods based on analysis."""
        methods = []

        # Get functions from analysis
        phase1 = self.analysis_results.get("phase1", {})
        functions = phase1.get("functions", [])

        for func in functions:
            if not func["is_private"]:  # Only test public functions
                method_name = f"test_{func['name']}"
                if self.test_type == "unit":
                    method_content = self._build_unit_test_method(func)
                else:
                    method_content = self._build_integration_test_method(func)

                methods.append(f"    def {method_name}(self{method_content}):")

        return (
            "\n\n".join(methods)
            if methods
            else '    def test_placeholder(self):\n        """Placeholder test."""\n        assert True'
        )

    def _build_unit_test_method(self, func: dict) -> str:
        """Build unit test method with mocks."""
        fixture_params = (
            ",\n        mock_tracer_base: Mock,\n        mock_safe_log: Mock"
        )
        method_body = f"""
        \"\"\"Test {func['name']} function.\"\"\"
        # Arrange
        mock_tracer_base.config.api_key = "test-key"
        
        # Act
        result = {func['name']}(mock_tracer_base)
        
        # Assert
        assert result is not None
        mock_safe_log.assert_called()"""

        return fixture_params + "\n    ) -> None:" + method_body

    def _build_integration_test_method(self, func: dict) -> str:
        """Build integration test method with real fixtures."""
        fixture_params = ",\n        honeyhive_tracer: HoneyHiveTracer,\n        verify_backend_event"
        method_body = f"""
        \"\"\"Test {func['name']} integration.\"\"\"
        # Arrange
        honeyhive_tracer.project_name = "integration-test"
        
        # Act
        result = {func['name']}(honeyhive_tracer)
        
        # Assert
        assert result is not None
        verify_backend_event(
            tracer=honeyhive_tracer,
            expected_event_type="function_call",
            expected_data={{"function": "{func['name']}"}}
        )"""

        return fixture_params + "\n    ) -> None:" + method_body

    def execute_phase_7_metrics(self) -> dict:
        """Execute Phase 7: Post-Generation Metrics."""
        print("Phase 7: Post-Generation Metrics", end=" ")

        if not self.generated_test_file or not self.generated_test_file.exists():
            print("❌")
            return {"success": False, "error": "No test file to analyze"}

        try:
            # Run tests to get metrics
            result = subprocess.run(
                ["pytest", str(self.generated_test_file), "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=120,
            )

            # Parse results
            import re

            passed_match = re.search(r"(\d+) passed", result.stdout)
            failed_match = re.search(r"(\d+) failed", result.stdout)

            passed_count = int(passed_match.group(1)) if passed_match else 0
            failed_count = int(failed_match.group(1)) if failed_match else 0
            total_count = passed_count + failed_count

            pass_rate = (passed_count / total_count * 100) if total_count > 0 else 0

            metrics = {
                "success": True,
                "total_tests": total_count,
                "passed_tests": passed_count,
                "failed_tests": failed_count,
                "pass_rate": pass_rate,
            }

            print(
                f"✅ ({passed_count}/{total_count} tests, {pass_rate:.1f}% pass rate)"
            )
            return metrics

        except Exception as e:
            print("❌")
            return {"success": False, "error": str(e)}

    def execute_phase_8_enforcement(self) -> dict:
        """Execute Phase 8: Quality Enforcement."""
        print("Phase 8: Quality Enforcement", end=" ")

        if not self.generated_test_file:
            print("❌")
            return {"success": False, "error": "No test file to validate"}

        try:
            # Run quality validation script
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/validate-test-quality.py",
                    str(self.generated_test_file),
                ],
                capture_output=True,
                text=True,
            )

            success = result.returncode == 0
            print("✅" if success else "❌")

            return {
                "success": success,
                "exit_code": result.returncode,
                "output": result.stdout,
                "errors": result.stderr,
            }

        except Exception as e:
            print("❌")
            return {"success": False, "error": str(e)}

    def execute_full_framework(self) -> dict:
        """Execute the complete V3 framework."""
        print("🚀 V3 FRAMEWORK EXECUTION STARTED")
        print(f"📁 Production file: {self.production_file}")
        print(f"🎯 Test type: {self.test_type}")
        print()

        try:
            # Execute phases 1-5
            self.analysis_results = self.execute_phase_1_through_5()

            # Execute phase 6
            if not self.execute_phase_6_validation():
                return {"success": False, "error": "Phase 6 validation failed"}

            # Generate test file
            self.generate_test_file()

            # Execute phase 7
            metrics = self.execute_phase_7_metrics()

            # Execute phase 8
            quality_results = self.execute_phase_8_enforcement()

            print()
            if quality_results["success"]:
                print("✅ FRAMEWORK EXECUTION COMPLETE")
                print(f"🎉 Test file ready: {self.generated_test_file}")
            else:
                print("❌ FRAMEWORK EXECUTION FAILED")
                print("🔧 Quality gates not met - see output above")

            return {
                "success": quality_results["success"],
                "generated_file": str(self.generated_test_file),
                "analysis_results": self.analysis_results,
                "metrics": metrics,
                "quality_results": quality_results,
            }

        except Exception as e:
            print(f"❌ FRAMEWORK EXECUTION ERROR: {e}")
            return {"success": False, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="V3 Framework Test Generator")
    parser.add_argument("--file", required=True, help="Production file path")
    parser.add_argument(
        "--type", required=True, choices=["unit", "integration"], help="Test type"
    )
    parser.add_argument(
        "--output", help="Output directory (default: tests/unit or tests/integration)"
    )

    args = parser.parse_args()

    try:
        executor = V3FrameworkExecutor(args.file, args.type, args.output)
        result = executor.execute_full_framework()

        if result["success"]:
            sys.exit(0)
        else:
            sys.exit(1)

    except Exception as e:
        print(f"❌ ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
