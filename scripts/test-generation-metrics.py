#!/usr/bin/env python3
"""Test Generation Metrics Collection System.

This script collects comprehensive metrics for test generation runs to enable
comparison of framework effectiveness and analysis quality over time.

Captures both pre-generation analysis quality and post-generation results.
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import click


class TestGenerationMetrics:
    """Comprehensive test generation metrics collector."""

    def __init__(self, test_file_path: str, production_file_path: str):
        self.test_file_path = Path(test_file_path)
        self.production_file_path = Path(production_file_path)
        self.metrics: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "test_file": str(self.test_file_path),
            "production_file": str(self.production_file_path),
            "pre_generation": {},
            "generation_process": {},
            "post_generation": {},
            "framework_compliance": {},
        }

    def collect_pre_generation_metrics(self) -> Dict[str, Any]:
        """Collect metrics about the analysis quality before generation."""
        click.echo("📊 Collecting pre-generation analysis metrics...")

        pre_metrics = {
            "production_analysis": self._analyze_production_code(),
            "linter_docs_coverage": self._check_linter_docs_coverage(),
            "framework_checklist": self._validate_framework_checklist(),
            "environment_validation": self._validate_environment(),
            "import_planning": self._analyze_import_planning(),
        }

        self.metrics["pre_generation"] = pre_metrics
        return pre_metrics

    def collect_generation_process_metrics(
        self, start_time: float, end_time: float
    ) -> Dict[str, Any]:
        """Collect metrics about the generation process itself."""
        click.echo("⚡ Collecting generation process metrics...")

        process_metrics = {
            "generation_time_seconds": round(end_time - start_time, 2),
            "framework_version": self._get_framework_version(),
            "checklist_completion": self._verify_checklist_completion(),
            "linter_prevention_active": self._check_linter_prevention(),
        }

        self.metrics["generation_process"] = process_metrics
        return process_metrics

    def collect_post_generation_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive metrics about the generated test file."""
        click.echo("🎯 Collecting post-generation quality metrics...")

        if not self.test_file_path.exists():
            return {"error": "Test file does not exist"}

        post_metrics = {
            "test_execution": self._run_test_execution(),
            "coverage_analysis": self._run_coverage_analysis(),
            "linting_analysis": self._run_linting_analysis(),
            "code_quality": self._analyze_code_quality(),
            "test_structure": self._analyze_test_structure(),
        }

        self.metrics["post_generation"] = post_metrics
        return post_metrics

    def collect_framework_compliance_metrics(self) -> Dict[str, Any]:
        """Collect metrics about framework compliance and effectiveness."""
        click.echo("🔍 Collecting framework compliance metrics...")

        compliance_metrics = {
            "checklist_adherence": self._check_checklist_adherence(),
            "linter_docs_usage": self._verify_linter_docs_usage(),
            "quality_targets": self._evaluate_quality_targets(),
            "framework_effectiveness": self._calculate_framework_effectiveness(),
        }

        self.metrics["framework_compliance"] = compliance_metrics
        return compliance_metrics

    def _analyze_production_code(self) -> Dict[str, Any]:
        """Analyze the production code complexity and structure."""
        if not self.production_file_path.exists():
            return {"error": "Production file does not exist"}

        try:
            with open(self.production_file_path, "r", encoding="utf-8") as f:
                content = f.read()

            return {
                "total_lines": len(content.splitlines()),
                "function_count": content.count("def "),
                "class_count": content.count("class "),
                "import_count": content.count("import ") + content.count("from "),
                "complexity_indicators": {
                    "try_except_blocks": content.count("try:"),
                    "if_statements": content.count("if "),
                    "for_loops": content.count("for "),
                    "while_loops": content.count("while "),
                },
                "docstring_coverage": self._estimate_docstring_coverage(content),
            }
        except Exception as e:
            return {"error": f"Failed to analyze production code: {e}"}

    def _check_linter_docs_coverage(self) -> Dict[str, Any]:
        """Check if all relevant linter documentation was discovered."""
        linter_dirs = [
            ".praxis-os/standards/development/code-generation/linters/pylint/",
            ".praxis-os/standards/development/code-generation/linters/black/",
            ".praxis-os/standards/development/code-generation/linters/mypy/",
        ]

        coverage = {}
        for linter_dir in linter_dirs:
            linter_path = Path(linter_dir)
            if linter_path.exists():
                docs = list(linter_path.glob("*.md"))
                coverage[linter_path.name] = {
                    "docs_available": len(docs),
                    "docs_list": [doc.name for doc in docs],
                }
            else:
                coverage[linter_path.name] = {"error": "Directory not found"}

        return coverage

    def _validate_framework_checklist(self) -> Dict[str, Any]:
        """Validate framework checklist completion indicators."""
        checklist_path = Path(
            ".praxis-os/standards/development/code-generation/pre-generation-checklist.md"
        )

        if not checklist_path.exists():
            return {"error": "Pre-generation checklist not found"}

        try:
            with open(checklist_path, "r", encoding="utf-8") as f:
                content = f.read()

            return {
                "checklist_exists": True,
                "checklist_sections": content.count("##"),
                "mandatory_steps": content.count("MANDATORY"),
                "linter_references": content.count("linters/"),
            }
        except Exception as e:
            return {"error": f"Failed to validate checklist: {e}"}

    def _validate_environment(self) -> Dict[str, Any]:
        """Validate the development environment setup."""
        try:
            # Check Python environment
            python_version = subprocess.run(
                ["python", "--version"], capture_output=True, text=True, check=True
            ).stdout.strip()

            # Check if in virtual environment
            venv_active = sys.prefix != sys.base_prefix

            # Check key dependencies
            deps_check = {}
            for dep in ["pytest", "pylint", "black", "mypy"]:
                try:
                    result = subprocess.run(
                        ["python", "-c", f"import {dep}; print({dep}.__version__)"],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    deps_check[dep] = result.stdout.strip()
                except subprocess.CalledProcessError:
                    deps_check[dep] = "not_available"

            return {
                "python_version": python_version,
                "virtual_env_active": venv_active,
                "dependencies": deps_check,
            }
        except Exception as e:
            return {"error": f"Environment validation failed: {e}"}

    def _analyze_import_planning(self) -> Dict[str, Any]:
        """Analyze the quality of import planning in the generated file."""
        if not self.test_file_path.exists():
            return {"error": "Test file does not exist for import analysis"}

        try:
            with open(self.test_file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.splitlines()
            import_section_end = 0

            # Find where imports end
            for i, line in enumerate(lines):
                if line.strip() and not (
                    line.startswith("import ")
                    or line.startswith("from ")
                    or line.startswith("#")
                    or line.strip() == ""
                ):
                    import_section_end = i
                    break

            import_lines = lines[:import_section_end]

            return {
                "total_imports": len(
                    [l for l in import_lines if l.startswith(("import ", "from "))]
                ),
                "import_organization": {
                    "standard_library": len(
                        [l for l in import_lines if self._is_standard_library_import(l)]
                    ),
                    "third_party": len(
                        [l for l in import_lines if self._is_third_party_import(l)]
                    ),
                    "local": len([l for l in import_lines if self._is_local_import(l)]),
                },
                "imports_at_top": import_section_end > 0,
                "unused_imports_likely": content.count("List") == 0
                and "from typing import" in content
                and "List" in content,
            }
        except Exception as e:
            return {"error": f"Import analysis failed: {e}"}

    def _run_test_execution(self) -> Dict[str, Any]:
        """Run the tests and collect execution metrics."""
        try:
            cmd = [
                "python",
                "-m",
                "pytest",
                str(self.test_file_path),
                "-v",
                "--tb=short",
                "--no-header",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            output = result.stdout + result.stderr

            # Parse pytest output
            test_metrics = {
                "exit_code": result.returncode,
                "total_tests": self._extract_test_count(output),
                "passed_tests": output.count(" PASSED"),
                "failed_tests": output.count(" FAILED"),
                "skipped_tests": output.count(" SKIPPED"),
                "execution_time": self._extract_execution_time(output),
                "pass_rate": 0.0,
            }

            if test_metrics["total_tests"] > 0:
                test_metrics["pass_rate"] = round(
                    test_metrics["passed_tests"] / test_metrics["total_tests"] * 100, 2
                )

            return test_metrics

        except subprocess.TimeoutExpired:
            return {"error": "Test execution timed out"}
        except Exception as e:
            return {"error": f"Test execution failed: {e}"}

    def _run_coverage_analysis(self) -> Dict[str, Any]:
        """Run coverage analysis on the generated tests using direct pytest."""
        try:
            # Convert file path to Python module format
            # src/honeyhive/tracer/processing/otlp_session.py -> honeyhive.tracer.processing.otlp_session
            production_path_str = str(self.production_file_path)
            if production_path_str.startswith("src/"):
                production_path_str = production_path_str[4:]  # Remove 'src/' prefix

            # Convert to module format
            if self.production_file_path.name == "__init__.py":
                # For __init__.py files, use the parent directory
                production_module_path = production_path_str.replace(
                    "/__init__.py", ""
                ).replace("/", ".")
            else:
                # For regular files, remove .py extension
                production_module_path = production_path_str.replace(".py", "").replace(
                    "/", "."
                )

            # Use direct pytest for targeted coverage analysis (tox overrides coverage config)
            cmd = [
                "python",
                "-m",
                "pytest",
                str(self.test_file_path),
                f"--cov={production_module_path}",
                "--cov-report=term-missing",
                "--no-header",
                "-q",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            output = result.stdout + result.stderr

            # Extract coverage percentage - handle multiple possible formats
            coverage_percent = 0.0
            missing_lines = []

            # Look for coverage lines in different formats
            for line in output.splitlines():
                if "TOTAL" in line and "%" in line:
                    parts = line.split()
                    for part in parts:
                        if part.endswith("%"):
                            try:
                                coverage_percent = float(part.rstrip("%"))
                                break
                            except ValueError:
                                continue
                    # Look for missing lines in the same line
                    if len(parts) >= 5 and parts[-1] not in ["", "0"]:
                        missing_lines = parts[-1].split(",") if parts[-1] != "" else []
                    break
                # Also check for "Required test coverage" line from tox
                elif "Required test coverage" in line and "reached" in line:
                    # Extract from "Required test coverage of 80.0% reached. Total coverage: 99.81%"
                    if "Total coverage:" in line:
                        coverage_part = line.split("Total coverage:")[-1].strip()
                        if coverage_part.endswith("%"):
                            try:
                                coverage_percent = float(coverage_part.rstrip("%"))
                                break
                            except ValueError:
                                continue
                # Also check for single module coverage lines
                elif (
                    any(
                        module_part in line
                        for module_part in str(self.production_file_path)
                        .replace("src/", "")
                        .replace("/", ".")
                        .replace(".py", "")
                        .split(".")
                    )
                    and "%" in line
                ):
                    parts = line.split()
                    for part in parts:
                        if part.endswith("%"):
                            try:
                                coverage_percent = float(part.rstrip("%"))
                                break
                            except ValueError:
                                continue

            return {
                "coverage_percentage": coverage_percent,
                "missing_lines_count": len(missing_lines),
                "missing_lines": missing_lines[:10],  # First 10 missing lines
                "coverage_target_met": coverage_percent >= 80.0,
            }

        except Exception as e:
            return {"error": f"Coverage analysis failed: {e}"}

    def _run_linting_analysis(self) -> Dict[str, Any]:
        """Run comprehensive linting analysis."""
        linting_results = {}

        # Pylint analysis
        try:
            cmd = ["tox", "-e", "lint", "--", str(self.test_file_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            output = result.stdout + result.stderr

            # Extract pylint score
            score_line = [
                line
                for line in output.splitlines()
                if "Your code has been rated at" in line
            ]
            pylint_score = 0.0
            if score_line:
                import re

                match = re.search(r"rated at ([\d.]+)/10", score_line[0])
                if match:
                    pylint_score = float(match.group(1))

            # Count violation types
            violations = {
                "total_violations": output.count(":"),
                "trailing_whitespace": output.count("trailing-whitespace"),
                "line_too_long": output.count("line-too-long"),
                "import_outside_toplevel": output.count("import-outside-toplevel"),
                "unused_import": output.count("unused-import"),
                "redefined_outer_name": output.count("redefined-outer-name"),
            }

            linting_results["pylint"] = {
                "score": pylint_score,
                "target_met": pylint_score >= 10.0,
                "violations": violations,
            }

        except Exception as e:
            linting_results["pylint"] = {"error": f"Pylint analysis failed: {e}"}

        # Black formatting check
        try:
            cmd = ["python", "-m", "black", str(self.test_file_path), "--check"]
            result = subprocess.run(cmd, capture_output=True, text=True)

            linting_results["black"] = {
                "formatted": result.returncode == 0,
                "needs_formatting": result.returncode != 0,
            }

        except Exception as e:
            linting_results["black"] = {"error": f"Black check failed: {e}"}

        # MyPy type checking
        try:
            cmd = [
                "python",
                "-m",
                "mypy",
                str(self.test_file_path),
                "--ignore-missing-imports",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            output = result.stdout + result.stderr
            error_count = len(
                [line for line in output.splitlines() if ": error:" in line]
            )

            linting_results["mypy"] = {
                "error_count": error_count,
                "clean": error_count == 0,
                "exit_code": result.returncode,
            }

        except Exception as e:
            linting_results["mypy"] = {"error": f"MyPy check failed: {e}"}

        return linting_results

    def _analyze_code_quality(self) -> Dict[str, Any]:
        """Analyze overall code quality metrics."""
        if not self.test_file_path.exists():
            return {"error": "Test file does not exist"}

        try:
            with open(self.test_file_path, "r", encoding="utf-8") as f:
                content = f.read()

            lines = content.splitlines()

            return {
                "total_lines": len(lines),
                "code_lines": len(
                    [l for l in lines if l.strip() and not l.strip().startswith("#")]
                ),
                "comment_lines": len([l for l in lines if l.strip().startswith("#")]),
                "docstring_lines": content.count('"""') * 3,  # Rough estimate
                "blank_lines": len([l for l in lines if not l.strip()]),
                "average_line_length": (
                    sum(len(l) for l in lines) / len(lines) if lines else 0
                ),
                "max_line_length": max(len(l) for l in lines) if lines else 0,
                "complexity_indicators": {
                    "nested_classes": content.count("class "),
                    "test_methods": content.count("def test_"),
                    "assertions": content.count("assert "),
                    "mock_usage": content.count("Mock(") + content.count("@patch"),
                },
            }
        except Exception as e:
            return {"error": f"Code quality analysis failed: {e}"}

    def _analyze_test_structure(self) -> Dict[str, Any]:
        """Analyze the structure and organization of tests."""
        if not self.test_file_path.exists():
            return {"error": "Test file does not exist"}

        try:
            with open(self.test_file_path, "r", encoding="utf-8") as f:
                content = f.read()

            return {
                "test_classes": content.count("class Test"),
                "test_methods": content.count("def test_"),
                "fixtures": content.count("@pytest.fixture"),
                "parametrized_tests": content.count("@pytest.mark.parametrize"),
                "test_organization": {
                    "has_docstrings": '"""' in content,
                    "uses_fixtures": "@pytest.fixture" in content,
                    "uses_mocking": "Mock" in content or "@patch" in content,
                    "has_setup_teardown": "setup" in content.lower()
                    or "teardown" in content.lower(),
                },
                "coverage_patterns": {
                    "happy_path_tests": content.count("test_")
                    - content.count("test_.*error")
                    - content.count("test_.*exception"),
                    "error_handling_tests": content.count("exception")
                    + content.count("error"),
                    "edge_case_tests": content.count("edge")
                    + content.count("boundary"),
                },
            }
        except Exception as e:
            return {"error": f"Test structure analysis failed: {e}"}

    def _get_framework_version(self) -> str:
        """Get the current framework version/identifier."""
        try:
            framework_file = Path(
                ".praxis-os/standards/development/code-generation/comprehensive-analysis-skip-proof.md"
            )
            if framework_file.exists():
                with open(framework_file, "r", encoding="utf-8") as f:
                    content = f.read()
                # Look for version indicators or modification dates
                if "PHASE 0: Pre-Generation Checklist" in content:
                    return "enhanced_v2_directory_discovery"
                elif "Pre-Generation Linting Validation" in content:
                    return "enhanced_v1_linting_validation"
                else:
                    return "original_framework"
            return "unknown"
        except Exception:
            return "error_detecting_version"

    def _verify_checklist_completion(self) -> Dict[str, Any]:
        """Verify that the pre-generation checklist was completed."""
        # This would be enhanced to check for actual completion indicators
        # For now, we check for the existence of key framework components
        checklist_indicators = {
            "checklist_exists": Path(
                ".praxis-os/standards/development/code-generation/pre-generation-checklist.md"
            ).exists(),
            "linter_docs_exist": Path(
                ".praxis-os/standards/development/code-generation/linters/"
            ).exists(),
            "comprehensive_framework_exists": Path(
                ".praxis-os/standards/development/code-generation/comprehensive-analysis-skip-proof.md"
            ).exists(),
        }

        return {
            "completion_indicators": checklist_indicators,
            "likely_completed": all(checklist_indicators.values()),
        }

    def _check_linter_prevention(self) -> Dict[str, Any]:
        """Check if linter prevention mechanisms were active."""
        # Check for evidence of linter prevention in the generated code
        if not self.test_file_path.exists():
            return {"error": "Cannot check linter prevention - file missing"}

        try:
            with open(self.test_file_path, "r", encoding="utf-8") as f:
                content = f.read()

            prevention_indicators = {
                "imports_at_top": not (
                    "import " in content[content.find("def ") :]
                    if "def " in content
                    else False
                ),
                "no_mock_spec_errors": "Mock(spec=" not in content,
                "proper_disable_comments": "# pylint: disable=" in content,
                "type_annotations_present": ") -> " in content,
            }

            return {
                "prevention_indicators": prevention_indicators,
                "prevention_score": sum(prevention_indicators.values())
                / len(prevention_indicators),
            }
        except Exception as e:
            return {"error": f"Linter prevention check failed: {e}"}

    def _check_checklist_adherence(self) -> Dict[str, Any]:
        """Check adherence to the pre-generation checklist."""
        # This would be enhanced with actual checklist tracking
        return {
            "environment_validated": True,  # Placeholder
            "linter_docs_read": True,  # Placeholder
            "production_code_analyzed": True,  # Placeholder
            "import_strategy_planned": True,  # Placeholder
        }

    def _verify_linter_docs_usage(self) -> Dict[str, Any]:
        """Verify that linter documentation was actually used."""
        # Check for evidence that linter docs influenced the generation
        if not self.test_file_path.exists():
            return {"error": "Cannot verify linter docs usage - file missing"}

        try:
            with open(self.test_file_path, "r", encoding="utf-8") as f:
                content = f.read()

            usage_indicators = {
                "pylint_rules_followed": "# pylint: disable=" in content
                and "import-outside-toplevel"
                not in content[200:],  # No imports in functions
                "black_formatting_ready": len(
                    [l for l in content.splitlines() if len(l) > 88]
                )
                == 0,  # No long lines
                "mypy_patterns_used": "Mock(" in content
                and "spec=" not in content,  # Proper mocking
                "import_organization": (
                    content.find("from typing") < content.find("import pytest")
                    if "import pytest" in content
                    else True
                ),
            }

            return {
                "usage_indicators": usage_indicators,
                "usage_score": sum(usage_indicators.values()) / len(usage_indicators),
            }
        except Exception as e:
            return {"error": f"Linter docs usage verification failed: {e}"}

    def _evaluate_quality_targets(self) -> Dict[str, Any]:
        """Evaluate if quality targets were met."""
        post_gen = self.metrics.get("post_generation", {})

        targets = {
            "test_pass_rate": {
                "target": 90.0,
                "actual": post_gen.get("test_execution", {}).get("pass_rate", 0.0),
                "met": False,
            },
            "coverage_percentage": {
                "target": 80.0,
                "actual": post_gen.get("coverage_analysis", {}).get(
                    "coverage_percentage", 0.0
                ),
                "met": False,
            },
            "pylint_score": {
                "target": 10.0,
                "actual": post_gen.get("linting_analysis", {})
                .get("pylint", {})
                .get("score", 0.0),
                "met": False,
            },
            "mypy_errors": {
                "target": 0,
                "actual": post_gen.get("linting_analysis", {})
                .get("mypy", {})
                .get("error_count", 999),
                "met": False,
            },
        }

        # Update met status
        for target_name, target_data in targets.items():
            if target_name == "mypy_errors":
                target_data["met"] = target_data["actual"] <= target_data["target"]
            else:
                target_data["met"] = target_data["actual"] >= target_data["target"]

        return {
            "targets": targets,
            "overall_quality_score": sum(1 for t in targets.values() if t["met"])
            / len(targets),
        }

    def _calculate_framework_effectiveness(self) -> Dict[str, Any]:
        """Calculate overall framework effectiveness score."""
        post_gen = self.metrics.get("post_generation", {})

        # Weight different aspects of effectiveness
        weights = {
            "test_execution": 0.3,
            "code_quality": 0.25,
            "linting_compliance": 0.25,
            "coverage": 0.2,
        }

        scores = {}

        # Test execution score
        test_exec = post_gen.get("test_execution", {})
        scores["test_execution"] = test_exec.get("pass_rate", 0.0) / 100.0

        # Code quality score (based on structure and organization)
        code_qual = post_gen.get("code_quality", {})
        complexity = code_qual.get("complexity_indicators", {})
        test_method_count = complexity.get("test_methods", 0)
        assertion_count = complexity.get("assertions", 0)
        scores["code_quality"] = min(
            1.0, (test_method_count * 0.1 + assertion_count * 0.05)
        )

        # Linting compliance score
        linting = post_gen.get("linting_analysis", {})
        pylint_score = linting.get("pylint", {}).get("score", 0.0) / 10.0
        black_ok = 1.0 if linting.get("black", {}).get("formatted", False) else 0.0
        mypy_ok = 1.0 if linting.get("mypy", {}).get("clean", False) else 0.0
        scores["linting_compliance"] = (pylint_score + black_ok + mypy_ok) / 3.0

        # Coverage score
        coverage = post_gen.get("coverage_analysis", {})
        scores["coverage"] = min(1.0, coverage.get("coverage_percentage", 0.0) / 100.0)

        # Calculate weighted effectiveness score
        effectiveness_score = sum(
            scores[aspect] * weights[aspect] for aspect in weights.keys()
        )

        return {
            "component_scores": scores,
            "weights": weights,
            "overall_effectiveness": round(effectiveness_score, 3),
            "effectiveness_grade": self._score_to_grade(effectiveness_score),
        }

    def _score_to_grade(self, score: float) -> str:
        """Convert effectiveness score to letter grade."""
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"

    # Helper methods for parsing
    def _extract_test_count(self, output: str) -> int:
        """Extract total test count from pytest output."""
        import re

        match = re.search(r"(\d+) passed|(\d+) failed|(\d+) total", output)
        if match:
            return sum(int(g) for g in match.groups() if g)
        return output.count("::test_")

    def _extract_execution_time(self, output: str) -> float:
        """Extract execution time from pytest output."""
        import re

        match = re.search(r"in ([\d.]+)s", output)
        return float(match.group(1)) if match else 0.0

    def _estimate_docstring_coverage(self, content: str) -> float:
        """Estimate docstring coverage percentage."""
        functions = content.count("def ")
        classes = content.count("class ")
        total_items = functions + classes
        docstrings = content.count('"""')

        if total_items == 0:
            return 0.0

        # Rough estimate: assume each docstring covers one item
        return min(100.0, (docstrings / total_items) * 100.0)

    def _is_standard_library_import(self, line: str) -> bool:
        """Check if import line is from standard library."""
        stdlib_modules = [
            "typing",
            "unittest",
            "sys",
            "os",
            "json",
            "time",
            "datetime",
            "pathlib",
        ]
        return any(module in line for module in stdlib_modules)

    def _is_third_party_import(self, line: str) -> bool:
        """Check if import line is from third party."""
        third_party = ["pytest", "pydantic", "requests"]
        return any(module in line for module in third_party)

    def _is_local_import(self, line: str) -> bool:
        """Check if import line is local to the project."""
        return "honeyhive" in line

    def save_metrics(self, output_file: Optional[str] = None) -> str:
        """Save collected metrics to JSON file."""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"test_generation_metrics_{timestamp}.json"

        output_path = Path(output_file)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.metrics, f, indent=2, default=str)

        return str(output_path)

    def generate_summary_report(self) -> str:
        """Generate a human-readable summary report."""
        post_gen = self.metrics.get("post_generation", {})
        framework_compliance = self.metrics.get("framework_compliance", {})

        report = []
        report.append("=" * 60)
        report.append("TEST GENERATION METRICS SUMMARY")
        report.append("=" * 60)
        report.append(f"Timestamp: {self.metrics['timestamp']}")
        report.append(f"Test File: {self.metrics['test_file']}")
        report.append(f"Production File: {self.metrics['production_file']}")
        report.append("")

        # Test Execution Results
        test_exec = post_gen.get("test_execution", {})
        report.append("📊 TEST EXECUTION RESULTS:")
        report.append(f"  Total Tests: {test_exec.get('total_tests', 'N/A')}")
        report.append(f"  Passed: {test_exec.get('passed_tests', 'N/A')}")
        report.append(f"  Failed: {test_exec.get('failed_tests', 'N/A')}")
        report.append(f"  Pass Rate: {test_exec.get('pass_rate', 'N/A')}%")
        report.append("")

        # Coverage Analysis
        coverage = post_gen.get("coverage_analysis", {})
        report.append("📈 COVERAGE ANALYSIS:")
        report.append(f"  Coverage: {coverage.get('coverage_percentage', 'N/A')}%")
        report.append(
            f"  Target Met (80%): {'✅' if coverage.get('coverage_target_met', False) else '❌'}"
        )
        report.append("")

        # Linting Results
        linting = post_gen.get("linting_analysis", {})
        report.append("🔍 LINTING ANALYSIS:")
        pylint_data = linting.get("pylint", {})
        report.append(f"  Pylint Score: {pylint_data.get('score', 'N/A')}/10")
        report.append(
            f"  Black Formatted: {'✅' if linting.get('black', {}).get('formatted', False) else '❌'}"
        )
        report.append(
            f"  MyPy Errors: {linting.get('mypy', {}).get('error_count', 'N/A')}"
        )
        report.append("")

        # Framework Effectiveness
        effectiveness = framework_compliance.get("framework_effectiveness", {})
        report.append("🎯 FRAMEWORK EFFECTIVENESS:")
        report.append(
            f"  Overall Score: {effectiveness.get('overall_effectiveness', 'N/A')}"
        )
        report.append(f"  Grade: {effectiveness.get('effectiveness_grade', 'N/A')}")
        report.append("")

        # Quality Targets
        quality_targets = framework_compliance.get("quality_targets", {})
        report.append("🏆 QUALITY TARGETS:")
        targets = quality_targets.get("targets", {})
        for target_name, target_data in targets.items():
            status = "✅" if target_data.get("met", False) else "❌"
            report.append(
                f"  {target_name}: {target_data.get('actual', 'N/A')} (target: {target_data.get('target', 'N/A')}) {status}"
            )

        return "\n".join(report)


@click.command()
@click.option("--test-file", required=True, help="Path to the test file to analyze")
@click.option(
    "--production-file", required=True, help="Path to the production file being tested"
)
@click.option("--output", help="Output file for metrics JSON (default: auto-generated)")
@click.option(
    "--pre-generation", is_flag=True, help="Collect only pre-generation metrics"
)
@click.option(
    "--post-generation", is_flag=True, help="Collect only post-generation metrics"
)
@click.option("--summary", is_flag=True, help="Display summary report")
def main(
    test_file: str,
    production_file: str,
    output: Optional[str],
    pre_generation: bool,
    post_generation: bool,
    summary: bool,
):
    """Collect comprehensive test generation metrics."""

    collector = TestGenerationMetrics(test_file, production_file)

    if pre_generation or not post_generation:
        click.echo("🔍 Collecting pre-generation metrics...")
        collector.collect_pre_generation_metrics()

    if post_generation or not pre_generation:
        click.echo("📊 Collecting post-generation metrics...")
        start_time = time.time()
        collector.collect_generation_process_metrics(start_time, time.time())
        collector.collect_post_generation_metrics()
        collector.collect_framework_compliance_metrics()

    # Save metrics
    output_file = collector.save_metrics(output)
    click.echo(f"✅ Metrics saved to: {output_file}")

    if summary:
        click.echo("\n" + collector.generate_summary_report())


if __name__ == "__main__":
    main()
