#!/usr/bin/env python3
"""
Dynamic Integration Complete

This script completes the dynamic OpenAPI integration by:
1. Testing the generated models with dynamic validation
2. Updating the existing SDK to use new models intelligently
3. Running comprehensive integration tests with adaptive strategies
4. Providing rollback capabilities if issues are detected

All operations use dynamic logic principles - no static patterns.
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DynamicIntegrationManager:
    """
    Manages the complete integration using dynamic logic.

    Features:
    - Adaptive testing strategies
    - Intelligent rollback on failures
    - Memory-efficient processing
    - Graceful error handling
    """

    def __init__(self):
        self.project_root = Path.cwd()
        self.backup_dir = None
        self.integration_stats = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "models_validated": 0,
            "errors_handled": 0,
            "processing_time": 0.0,
        }

        # Dynamic thresholds
        self.max_test_time = 300  # 5 minutes max for tests
        self.success_threshold = 0.8  # 80% tests must pass

    def create_backup_dynamically(self) -> bool:
        """Create intelligent backup of current state."""
        logger.info("📦 Creating dynamic backup...")

        try:
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.backup_dir = (
                self.project_root / f"backup_before_dynamic_integration_{timestamp}"
            )

            # Backup critical directories
            backup_targets = [
                "src/honeyhive/models",
                "src/honeyhive/api",
                "openapi.yaml",
            ]

            self.backup_dir.mkdir(exist_ok=True)

            for target in backup_targets:
                target_path = self.project_root / target
                if target_path.exists():
                    if target_path.is_file():
                        shutil.copy2(target_path, self.backup_dir / target_path.name)
                    else:
                        shutil.copytree(target_path, self.backup_dir / target_path.name)
                    logger.debug(f"✅ Backed up: {target}")

            logger.info(f"✅ Backup created: {self.backup_dir}")
            return True

        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            return False

    def validate_generated_models_dynamically(self) -> bool:
        """Dynamically validate generated models with adaptive testing."""
        logger.info("🔍 Validating generated models dynamically...")

        models_dir = self.project_root / "src/honeyhive/models_dynamic"

        if not models_dir.exists():
            logger.error(f"❌ Generated models directory not found: {models_dir}")
            return False

        try:
            # Test 1: Import validation (adaptive approach)
            import_success = self._test_model_imports_dynamically(models_dir)

            # Test 2: Model instantiation (sample-based testing)
            instantiation_success = self._test_model_instantiation_dynamically(
                models_dir
            )

            # Test 3: Compatibility with existing code
            compatibility_success = self._test_backward_compatibility_dynamically()

            # Calculate overall success rate
            tests = [import_success, instantiation_success, compatibility_success]
            success_rate = sum(tests) / len(tests)

            if success_rate >= self.success_threshold:
                logger.info(
                    f"✅ Model validation successful ({success_rate:.1%} success rate)"
                )
                return True
            else:
                logger.error(
                    f"❌ Model validation failed ({success_rate:.1%} success rate)"
                )
                return False

        except Exception as e:
            logger.error(f"❌ Model validation error: {e}")
            return False

    def _test_model_imports_dynamically(self, models_dir: Path) -> bool:
        """Test model imports with adaptive error handling."""
        logger.info("  🔍 Testing model imports...")

        try:
            # Add models directory to path temporarily
            sys.path.insert(0, str(models_dir.parent))

            # Test main import
            exec("from models_dynamic import *")
            logger.debug("    ✅ Main import successful")

            # Test specific model imports (sample-based)
            model_files = [
                f for f in models_dir.glob("*.py") if f.name != "__init__.py"
            ]
            sample_size = min(10, len(model_files))  # Test up to 10 models

            import random

            sample_files = random.sample(model_files, sample_size)

            for model_file in sample_files:
                module_name = model_file.stem
                try:
                    exec(f"from models_dynamic.{module_name} import *")
                    self.integration_stats["models_validated"] += 1
                except Exception as e:
                    logger.debug(f"    ⚠️  Import failed for {module_name}: {e}")
                    self.integration_stats["errors_handled"] += 1

            success_rate = self.integration_stats["models_validated"] / sample_size
            return success_rate >= self.success_threshold

        except Exception as e:
            logger.error(f"    ❌ Import test failed: {e}")
            return False
        finally:
            # Clean up sys.path
            if str(models_dir.parent) in sys.path:
                sys.path.remove(str(models_dir.parent))

    def _test_model_instantiation_dynamically(self, models_dir: Path) -> bool:
        """Test model instantiation with intelligent sampling."""
        logger.info("  🔍 Testing model instantiation...")

        try:
            # Load usage examples for testing
            examples_file = models_dir / "usage_examples.py"

            if not examples_file.exists():
                logger.warning(
                    "    ⚠️  No usage examples found, skipping instantiation test"
                )
                return True  # Not critical

            # Execute examples in controlled environment
            with open(examples_file, "r") as f:
                examples_code = f.read()

            # Create safe execution environment
            safe_globals = {
                "__builtins__": __builtins__,
                "Path": Path,
            }

            # Add models to environment
            sys.path.insert(0, str(models_dir.parent))
            exec("from models_dynamic import *", safe_globals)

            # Execute examples
            exec(examples_code, safe_globals)

            logger.debug("    ✅ Model instantiation successful")
            return True

        except Exception as e:
            logger.warning(f"    ⚠️  Instantiation test failed: {e}")
            return False  # Not critical for overall success
        finally:
            if str(models_dir.parent) in sys.path:
                sys.path.remove(str(models_dir.parent))

    def _test_backward_compatibility_dynamically(self) -> bool:
        """Test backward compatibility with existing SDK."""
        logger.info("  🔍 Testing backward compatibility...")

        try:
            # Test that existing imports still work
            compatibility_tests = [
                "from honeyhive import HoneyHive",
                "from honeyhive.models import EventFilter",
                "from honeyhive.models.generated import Operator, Type",
            ]

            for test in compatibility_tests:
                try:
                    exec(test)
                    logger.debug(f"    ✅ {test}")
                except Exception as e:
                    logger.warning(f"    ⚠️  {test} failed: {e}")
                    return False

            return True

        except Exception as e:
            logger.error(f"    ❌ Compatibility test failed: {e}")
            return False

    def run_integration_tests_dynamically(self) -> bool:
        """Run integration tests with adaptive strategies."""
        logger.info("🧪 Running integration tests dynamically...")

        start_time = time.time()

        try:
            # Test 1: API performance regression tests (critical)
            performance_success = self._run_performance_tests_adaptively()

            # Test 2: Core functionality tests (sample-based)
            functionality_success = self._run_functionality_tests_adaptively()

            # Test 3: EventFilter tests (critical for current issue)
            eventfilter_success = self._run_eventfilter_tests_adaptively()

            # Calculate results
            critical_tests = [performance_success, eventfilter_success]
            optional_tests = [functionality_success]

            # All critical tests must pass
            critical_success = all(critical_tests)

            # Calculate overall success rate
            all_tests = critical_tests + optional_tests
            overall_success_rate = sum(all_tests) / len(all_tests)

            self.integration_stats["processing_time"] = time.time() - start_time

            if critical_success and overall_success_rate >= self.success_threshold:
                logger.info(
                    f"✅ Integration tests successful ({overall_success_rate:.1%} success rate)"
                )
                return True
            else:
                logger.error(
                    f"❌ Integration tests failed (critical: {critical_success}, overall: {overall_success_rate:.1%})"
                )
                return False

        except Exception as e:
            logger.error(f"❌ Integration test error: {e}")
            return False

    def _run_performance_tests_adaptively(self) -> bool:
        """Run performance tests with timeout and adaptive strategies."""
        logger.info("  🚀 Running performance tests...")

        try:
            cmd = [
                sys.executable,
                "-m",
                "pytest",
                "tests/integration/test_api_client_performance_regression.py",
                "-v",
                "--tb=short",
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.max_test_time,
                cwd=self.project_root,
            )

            self.integration_stats["tests_run"] += 1

            if result.returncode == 0:
                self.integration_stats["tests_passed"] += 1
                logger.debug("    ✅ Performance tests passed")
                return True
            else:
                self.integration_stats["tests_failed"] += 1
                logger.warning(f"    ⚠️  Performance tests failed: {result.stdout}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("    ❌ Performance tests timed out")
            return False
        except Exception as e:
            logger.error(f"    ❌ Performance test error: {e}")
            return False

    def _run_functionality_tests_adaptively(self) -> bool:
        """Run core functionality tests with sampling."""
        logger.info("  🔧 Running functionality tests...")

        try:
            # Run a sample of integration tests (not all to save time)
            test_files = [
                "tests/integration/test_simple_integration.py",
                "tests/integration/test_end_to_end_validation.py",
            ]

            passed_tests = 0

            for test_file in test_files:
                test_path = self.project_root / test_file

                if not test_path.exists():
                    logger.debug(f"    ⚠️  Test file not found: {test_file}")
                    continue

                try:
                    cmd = [
                        sys.executable,
                        "-m",
                        "pytest",
                        str(test_path),
                        "-v",
                        "--tb=short",
                        "-x",  # Stop on first failure
                    ]

                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=60,  # 1 minute per test file
                        cwd=self.project_root,
                    )

                    self.integration_stats["tests_run"] += 1

                    if result.returncode == 0:
                        passed_tests += 1
                        self.integration_stats["tests_passed"] += 1
                        logger.debug(f"    ✅ {test_file} passed")
                    else:
                        self.integration_stats["tests_failed"] += 1
                        logger.debug(f"    ⚠️  {test_file} failed")

                except subprocess.TimeoutExpired:
                    logger.debug(f"    ⚠️  {test_file} timed out")
                    self.integration_stats["tests_failed"] += 1
                except Exception as e:
                    logger.debug(f"    ⚠️  {test_file} error: {e}")
                    self.integration_stats["tests_failed"] += 1

            # Success if at least half the tests pass
            success_rate = passed_tests / len(test_files) if test_files else 0
            return success_rate >= 0.5

        except Exception as e:
            logger.error(f"    ❌ Functionality test error: {e}")
            return False

    def _run_eventfilter_tests_adaptively(self) -> bool:
        """Run EventFilter-specific tests (critical for current issue)."""
        logger.info("  🎯 Running EventFilter tests...")

        try:
            # Test EventFilter functionality directly
            test_code = """
import os
from dotenv import load_dotenv
load_dotenv()

from honeyhive import HoneyHive
from honeyhive.models import EventFilter
from honeyhive.models.generated import Operator, Type

# Test EventFilter creation and usage
api_key = os.getenv("HH_API_KEY")
project = os.getenv("HH_PROJECT", "New Project")

if api_key:
    client = HoneyHive(api_key=api_key)
    
    # Test EventFilter creation
    event_filter = EventFilter(
        field="event_name",
        value="test_event",
        operator=Operator.is_,
        type=Type.string,
    )
    
    # Test API call (should not hang)
    events = client.events.list_events(event_filter, limit=5, project=project)
    print(f"EventFilter test successful: {len(events)} events returned")
else:
    print("EventFilter test skipped: no API key")
"""

            # Execute test in subprocess for isolation
            result = subprocess.run(
                [sys.executable, "-c", test_code],
                capture_output=True,
                text=True,
                timeout=30,  # 30 second timeout
                cwd=self.project_root,
            )

            self.integration_stats["tests_run"] += 1

            if result.returncode == 0 and "successful" in result.stdout:
                self.integration_stats["tests_passed"] += 1
                logger.debug("    ✅ EventFilter test passed")
                return True
            else:
                self.integration_stats["tests_failed"] += 1
                logger.warning(
                    f"    ⚠️  EventFilter test failed: {result.stdout} {result.stderr}"
                )
                return False

        except subprocess.TimeoutExpired:
            logger.error("    ❌ EventFilter test timed out")
            return False
        except Exception as e:
            logger.error(f"    ❌ EventFilter test error: {e}")
            return False

    def integrate_new_models_dynamically(self) -> bool:
        """Integrate new models with existing SDK intelligently."""
        logger.info("🔄 Integrating new models dynamically...")

        try:
            # Strategy: Gradual integration with fallback

            # Step 1: Create integration directory
            integration_dir = self.project_root / "src/honeyhive/models_integrated"
            integration_dir.mkdir(exist_ok=True)

            # Step 2: Copy essential models from dynamic generation
            essential_models = self._identify_essential_models()

            for model_name in essential_models:
                src_file = (
                    self.project_root
                    / "src/honeyhive/models_dynamic"
                    / f"{model_name}.py"
                )
                dst_file = integration_dir / f"{model_name}.py"

                if src_file.exists():
                    shutil.copy2(src_file, dst_file)
                    logger.debug(f"    ✅ Integrated model: {model_name}")

            # Step 3: Create compatibility layer
            self._create_compatibility_layer(integration_dir)

            # Step 4: Update main models __init__.py
            self._update_main_models_init(integration_dir)

            logger.info("✅ Model integration successful")
            return True

        except Exception as e:
            logger.error(f"❌ Model integration failed: {e}")
            return False

    def _identify_essential_models(self) -> List[str]:
        """Identify essential models for integration."""
        # These are the models most likely to be used by existing code
        essential_patterns = [
            "event",
            "session",
            "filter",
            "response",
            "request",
            "error",
        ]

        models_dir = self.project_root / "src/honeyhive/models_dynamic"
        all_models = [
            f.stem for f in models_dir.glob("*.py") if f.name != "__init__.py"
        ]

        essential_models = []

        for model in all_models:
            model_lower = model.lower()
            if any(pattern in model_lower for pattern in essential_patterns):
                essential_models.append(model)

        # Limit to reasonable number
        return essential_models[:20]

    def _create_compatibility_layer(self, integration_dir: Path):
        """Create compatibility layer for smooth transition."""
        compatibility_code = '''"""
Compatibility layer for dynamic model integration.

This module provides backward compatibility while transitioning to new models.
"""

# Re-export existing models for compatibility
try:
    from ..models.generated import *
except ImportError:
    pass

# Import new dynamic models
try:
    from . import *
except ImportError:
    pass

# Compatibility aliases (add as needed)
# Example: OldModelName = NewModelName
'''

        compatibility_file = integration_dir / "compatibility.py"
        with open(compatibility_file, "w") as f:
            f.write(compatibility_code)

    def _update_main_models_init(self, integration_dir: Path):
        """Update main models __init__.py to include new models."""
        main_init = self.project_root / "src/honeyhive/models/__init__.py"

        if main_init.exists():
            # Read existing content
            with open(main_init, "r") as f:
                content = f.read()

            # Add import for integrated models
            integration_import = "\n# Dynamic model integration\ntry:\n    from .models_integrated.compatibility import *\nexcept ImportError:\n    pass\n"

            if "Dynamic model integration" not in content:
                content += integration_import

                with open(main_init, "w") as f:
                    f.write(content)

                logger.debug("    ✅ Updated main models __init__.py")

    def rollback_on_failure(self) -> bool:
        """Rollback changes if integration fails."""
        if not self.backup_dir or not self.backup_dir.exists():
            logger.error("❌ No backup available for rollback")
            return False

        logger.info("🔄 Rolling back changes...")

        try:
            # Restore backed up files
            for backup_item in self.backup_dir.iterdir():
                target_path = self.project_root / backup_item.name

                # Remove current version
                if target_path.exists():
                    if target_path.is_file():
                        target_path.unlink()
                    else:
                        shutil.rmtree(target_path)

                # Restore backup
                if backup_item.is_file():
                    shutil.copy2(backup_item, target_path)
                else:
                    shutil.copytree(backup_item, target_path)

                logger.debug(f"    ✅ Restored: {backup_item.name}")

            logger.info("✅ Rollback successful")
            return True

        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            return False

    def generate_integration_report(self) -> Dict:
        """Generate comprehensive integration report."""
        return {
            "integration_stats": self.integration_stats,
            "backup_location": str(self.backup_dir) if self.backup_dir else None,
            "success_metrics": {
                "test_success_rate": (
                    self.integration_stats["tests_passed"]
                    / max(1, self.integration_stats["tests_run"])
                ),
                "models_validated": self.integration_stats["models_validated"],
                "errors_handled": self.integration_stats["errors_handled"],
            },
            "recommendations": self._generate_recommendations(),
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on integration results."""
        recommendations = []

        success_rate = self.integration_stats["tests_passed"] / max(
            1, self.integration_stats["tests_run"]
        )

        if success_rate >= 0.9:
            recommendations.append(
                "✅ Integration highly successful - proceed with confidence"
            )
        elif success_rate >= 0.7:
            recommendations.append(
                "⚠️  Integration mostly successful - monitor for issues"
            )
        else:
            recommendations.append("❌ Integration has issues - consider rollback")

        if self.integration_stats["errors_handled"] > 0:
            recommendations.append(
                f"🔍 {self.integration_stats['errors_handled']} errors handled - review logs"
            )

        if self.integration_stats["processing_time"] > 180:
            recommendations.append(
                "⏱️  Integration took longer than expected - optimize for future"
            )

        return recommendations


def main():
    """Main integration execution."""
    logger.info("🚀 Dynamic Integration Complete")
    logger.info("=" * 50)

    manager = DynamicIntegrationManager()

    # Step 1: Create backup
    if not manager.create_backup_dynamically():
        logger.error("❌ Cannot proceed without backup")
        return 1

    # Step 2: Validate generated models
    if not manager.validate_generated_models_dynamically():
        logger.error("❌ Model validation failed")
        return 1

    # Step 3: Run integration tests
    if not manager.run_integration_tests_dynamically():
        logger.warning("⚠️  Integration tests failed - attempting rollback")
        manager.rollback_on_failure()
        return 1

    # Step 4: Integrate new models
    if not manager.integrate_new_models_dynamically():
        logger.warning("⚠️  Model integration failed - attempting rollback")
        manager.rollback_on_failure()
        return 1

    # Step 5: Generate report
    report = manager.generate_integration_report()

    with open("dynamic_integration_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    stats = report["integration_stats"]
    metrics = report["success_metrics"]

    logger.info(f"\n🎉 Dynamic Integration Complete!")
    logger.info(f"📊 Tests run: {stats['tests_run']}")
    logger.info(f"📊 Tests passed: {stats['tests_passed']}")
    logger.info(f"📊 Success rate: {metrics['test_success_rate']:.1%}")
    logger.info(f"📊 Models validated: {metrics['models_validated']}")
    logger.info(f"⏱️  Processing time: {stats['processing_time']:.2f}s")

    logger.info(f"\n💡 Recommendations:")
    for rec in report["recommendations"]:
        logger.info(f"  {rec}")

    logger.info(f"\n💾 Files Generated:")
    logger.info(f"  • dynamic_integration_report.json - Integration report")
    if report["backup_location"]:
        logger.info(f"  • {report['backup_location']} - Backup location")

    return 0


if __name__ == "__main__":
    exit(main())
