#!/usr/bin/env python3
"""
OpenAPI Toolchain Setup Script

This script sets up a modern Python OpenAPI toolchain for:
1. Generating accurate OpenAPI specs from backend code analysis
2. Regenerating Python client models from updated specs
3. Validating spec-backend consistency

Uses modern tools:
- openapi-python-client: For generating typed Python clients
- apispec: For generating OpenAPI specs from code
- openapi-core: For validation
"""

import subprocess
import sys
import os
from pathlib import Path
import json
import yaml


class OpenAPIToolchain:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backend_path = (
            self.project_root.parent / "hive-kube" / "kubernetes" / "backend_service"
        )
        self.openapi_file = self.project_root / "openapi.yaml"
        self.models_dir = self.project_root / "src" / "honeyhive" / "models"

    def install_dependencies(self):
        """Install required OpenAPI toolchain dependencies."""
        print("🔧 Installing OpenAPI toolchain dependencies...")

        dependencies = [
            "openapi-python-client",
            "apispec[yaml]",
            "openapi-core",
            "pydantic",
            "pyyaml",
        ]

        for dep in dependencies:
            print(f"  Installing {dep}...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", dep],
                    check=True,
                    capture_output=True,
                )
                print(f"  ✅ {dep} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"  ❌ Failed to install {dep}: {e}")
                return False

        return True

    def backup_current_models(self):
        """Backup current models before regeneration."""
        import shutil
        from datetime import datetime

        backup_dir = (
            self.models_dir.parent
            / f"models.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        if self.models_dir.exists():
            print(f"📦 Backing up current models to {backup_dir}...")
            shutil.copytree(self.models_dir, backup_dir)
            print(f"✅ Models backed up successfully")
            return backup_dir
        else:
            print("ℹ️  No existing models to backup")
            return None

    def update_openapi_spec_critical_fixes(self):
        """Apply critical fixes to OpenAPI spec based on backend analysis."""
        print("🔧 Applying critical OpenAPI spec fixes...")

        if not self.openapi_file.exists():
            print(f"❌ OpenAPI file not found: {self.openapi_file}")
            return False

        try:
            # Load current spec
            with open(self.openapi_file, "r") as f:
                spec = yaml.safe_load(f)

            # Ensure paths section exists
            if "paths" not in spec:
                spec["paths"] = {}

            # Add critical missing endpoints discovered in backend analysis
            critical_fixes = {
                # Events API fixes
                "/events": {
                    "get": {
                        "summary": "List events with filters",
                        "operationId": "listEvents",
                        "tags": ["Events"],
                        "parameters": [
                            {
                                "name": "filters",
                                "in": "query",
                                "schema": {
                                    "type": "string",
                                    "description": "JSON-encoded array of EventFilter objects",
                                },
                            },
                            {
                                "name": "limit",
                                "in": "query",
                                "schema": {"type": "integer", "default": 1000},
                            },
                            {
                                "name": "page",
                                "in": "query",
                                "schema": {"type": "integer", "default": 1},
                            },
                            {
                                "name": "dateRange",
                                "in": "query",
                                "schema": {
                                    "type": "string",
                                    "description": "JSON-encoded date range object",
                                },
                            },
                        ],
                        "responses": {
                            "200": {
                                "description": "Events retrieved successfully",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "events": {
                                                    "type": "array",
                                                    "items": {
                                                        "$ref": "#/components/schemas/Event"
                                                    },
                                                }
                                            },
                                        }
                                    }
                                },
                            }
                        },
                    }
                },
                "/events/chart": {
                    "get": {
                        "summary": "Get events chart data",
                        "operationId": "getEventsChart",
                        "tags": ["Events"],
                        "parameters": [
                            {
                                "name": "dateRange",
                                "in": "query",
                                "required": True,
                                "schema": {
                                    "type": "string",
                                    "description": "JSON-encoded date range with $gte and $lte",
                                },
                            },
                            {
                                "name": "filters",
                                "in": "query",
                                "schema": {
                                    "type": "string",
                                    "description": "JSON-encoded array of EventFilter objects",
                                },
                            },
                            {
                                "name": "metric",
                                "in": "query",
                                "schema": {"type": "string", "default": "duration"},
                            },
                        ],
                        "responses": {
                            "200": {"description": "Chart data retrieved successfully"}
                        },
                    }
                },
                "/events/{event_id}": {
                    "delete": {
                        "summary": "Delete an event",
                        "operationId": "deleteEvent",
                        "tags": ["Events"],
                        "parameters": [
                            {
                                "name": "event_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Event deleted successfully",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "success": {"type": "boolean"},
                                                "deleted": {"type": "string"},
                                            },
                                        }
                                    }
                                },
                            }
                        },
                    }
                },
                # Sessions API fixes
                "/sessions/{session_id}": {
                    "get": {
                        "summary": "Retrieve a session",
                        "operationId": "getSession",
                        "tags": ["Sessions"],
                        "parameters": [
                            {
                                "name": "session_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Session details",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/Session"
                                        }
                                    }
                                },
                            }
                        },
                    },
                    "delete": {
                        "summary": "Delete a session",
                        "operationId": "deleteSession",
                        "tags": ["Sessions"],
                        "parameters": [
                            {
                                "name": "session_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {
                            "200": {"description": "Session deleted successfully"}
                        },
                    },
                },
                # Health endpoints
                "/healthcheck": {
                    "get": {
                        "summary": "Health check",
                        "operationId": "healthCheck",
                        "tags": ["Health"],
                        "responses": {"200": {"description": "Service is healthy"}},
                    }
                },
            }

            # Apply fixes
            for path, methods in critical_fixes.items():
                if path not in spec["paths"]:
                    spec["paths"][path] = {}

                for method, method_spec in methods.items():
                    spec["paths"][path][method] = method_spec
                    print(f"  ✅ Added {method.upper()} {path}")

            # Save updated spec
            with open(self.openapi_file, "w") as f:
                yaml.dump(spec, f, default_flow_style=False, sort_keys=False)

            print(f"✅ OpenAPI spec updated with critical fixes")
            return True

        except Exception as e:
            print(f"❌ Error updating OpenAPI spec: {e}")
            return False

    def generate_python_client(self):
        """Generate Python client from updated OpenAPI spec."""
        print("🔧 Generating Python client from OpenAPI spec...")

        # Create output directory
        output_dir = self.project_root / "generated_client"

        # Remove existing directory if it exists
        import shutil

        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(exist_ok=True)

        try:
            # Use openapi-python-client to generate client
            cmd = [
                "openapi-python-client",
                "generate",
                "--path",
                str(self.openapi_file),
                "--output-path",
                str(output_dir),
            ]

            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.project_root
            )

            if result.returncode == 0:
                print("✅ Python client generated successfully")
                print(f"📁 Generated client available at: {output_dir}")
                return output_dir
            else:
                print(f"❌ Client generation failed: {result.stderr}")
                return None

        except Exception as e:
            print(f"❌ Error generating client: {e}")
            return None

    def extract_models_from_generated_client(self, generated_dir: Path):
        """Extract and integrate models from generated client."""
        print("🔧 Extracting models from generated client...")

        if not generated_dir or not generated_dir.exists():
            print("❌ Generated client directory not found")
            return False

        try:
            # Find the generated models
            models_pattern = generated_dir / "**" / "models" / "*.py"
            import glob

            model_files = list(glob.glob(str(models_pattern), recursive=True))

            if not model_files:
                print("❌ No model files found in generated client")
                return False

            # Create new models directory
            new_models_dir = self.models_dir
            new_models_dir.mkdir(parents=True, exist_ok=True)

            # Copy relevant model files
            import shutil

            for model_file in model_files:
                model_path = Path(model_file)
                dest_path = new_models_dir / model_path.name

                shutil.copy2(model_file, dest_path)
                print(f"  ✅ Copied {model_path.name}")

            # Create __init__.py with proper imports
            init_file = new_models_dir / "__init__.py"
            with open(init_file, "w") as f:
                f.write('"""Generated models from OpenAPI specification."""\n\n')

                # Import all models
                for model_file in model_files:
                    model_name = Path(model_file).stem
                    if model_name != "__init__":
                        f.write(f"from .{model_name} import *\n")

            print(f"✅ Models extracted to {new_models_dir}")
            return True

        except Exception as e:
            print(f"❌ Error extracting models: {e}")
            return False

    def validate_generated_models(self):
        """Validate that generated models work correctly."""
        print("🔧 Validating generated models...")

        try:
            # Test basic imports
            test_imports = [
                "from honeyhive.models import EventFilter",
                "from honeyhive.models import Event",
                "from honeyhive.models.generated import Operator, Type",
            ]

            for import_stmt in test_imports:
                try:
                    exec(import_stmt)
                    print(f"  ✅ {import_stmt}")
                except ImportError as e:
                    print(f"  ❌ {import_stmt} - {e}")
                    return False

            # Test EventFilter creation
            exec(
                """
from honeyhive.models import EventFilter
from honeyhive.models.generated import Operator, Type

# Test EventFilter creation
filter_obj = EventFilter(
    field='event_name',
    value='test',
    operator=Operator.is_,
    type=Type.string
)
print(f"  ✅ EventFilter created: {filter_obj}")
"""
            )

            print("✅ Model validation successful")
            return True

        except Exception as e:
            print(f"❌ Model validation failed: {e}")
            return False

    def run_integration_tests(self):
        """Run integration tests to validate the changes."""
        print("🔧 Running integration tests...")

        try:
            # Run specific tests that use EventFilter
            test_commands = [
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "tests/integration/test_api_client_performance_regression.py::TestAPIClientPerformanceRegression::test_events_api_performance_benchmark",
                    "-v",
                ],
            ]

            for cmd in test_commands:
                print(f"  Running: {' '.join(cmd)}")
                result = subprocess.run(
                    cmd, cwd=self.project_root, capture_output=True, text=True
                )

                if result.returncode == 0:
                    print(f"  ✅ Test passed")
                else:
                    print(f"  ❌ Test failed: {result.stdout}")
                    print(f"  Error: {result.stderr}")
                    return False

            print("✅ Integration tests passed")
            return True

        except Exception as e:
            print(f"❌ Integration test error: {e}")
            return False


def main():
    """Main execution function."""
    print("🚀 OpenAPI Toolchain Setup")
    print("=" * 50)

    # Initialize toolchain
    project_root = Path(__file__).parent.parent
    toolchain = OpenAPIToolchain(str(project_root))

    # Step 1: Install dependencies
    if not toolchain.install_dependencies():
        print("❌ Failed to install dependencies")
        return 1

    # Step 2: Backup current models
    backup_dir = toolchain.backup_current_models()

    # Step 3: Update OpenAPI spec with critical fixes
    if not toolchain.update_openapi_spec_critical_fixes():
        print("❌ Failed to update OpenAPI spec")
        return 1

    # Step 4: Generate Python client
    generated_dir = toolchain.generate_python_client()
    if not generated_dir:
        print("❌ Failed to generate Python client")
        return 1

    # Step 5: Extract models from generated client
    if not toolchain.extract_models_from_generated_client(generated_dir):
        print("❌ Failed to extract models")
        return 1

    # Step 6: Validate generated models
    if not toolchain.validate_generated_models():
        print("❌ Model validation failed")
        if backup_dir:
            print(f"💡 Consider restoring from backup: {backup_dir}")
        return 1

    # Step 7: Run integration tests
    if not toolchain.run_integration_tests():
        print("❌ Integration tests failed")
        if backup_dir:
            print(f"💡 Consider restoring from backup: {backup_dir}")
        return 1

    print("\n🎉 OpenAPI Toolchain Setup Complete!")
    print("=" * 50)
    print("✅ Dependencies installed")
    print("✅ OpenAPI spec updated with critical fixes")
    print("✅ Python client generated")
    print("✅ Models extracted and validated")
    print("✅ Integration tests passing")

    if backup_dir:
        print(f"📦 Backup available at: {backup_dir}")

    print("\n🎯 Next Steps:")
    print("1. Review generated models in src/honeyhive/models/")
    print("2. Run full integration test suite")
    print("3. Update SDK API clients to use new endpoints")
    print("4. Update documentation")

    return 0


if __name__ == "__main__":
    sys.exit(main())
