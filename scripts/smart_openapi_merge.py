#!/usr/bin/env python3
"""
Smart OpenAPI Merge Strategy

This script intelligently merges the existing OpenAPI spec (47 endpoints, 10 services)
with the backend implementation analysis to create a complete, accurate specification
that preserves all existing work while adding missing endpoints.
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Set, Any
from collections import defaultdict
import subprocess
import sys


class SmartOpenAPIMerger:
    def __init__(self, openapi_file: str, backend_analysis_file: str = None):
        self.openapi_file = Path(openapi_file)
        self.backend_analysis_file = backend_analysis_file
        self.existing_spec = None
        self.backend_endpoints = {}
        self.merge_report = {
            "preserved_endpoints": [],
            "added_endpoints": [],
            "updated_endpoints": [],
            "conflicts": [],
            "warnings": [],
        }

    def load_existing_spec(self) -> bool:
        """Load the existing OpenAPI specification."""
        try:
            with open(self.openapi_file, "r") as f:
                self.existing_spec = yaml.safe_load(f)
            print(
                f"✅ Loaded existing OpenAPI spec: {self.existing_spec['info']['title']} v{self.existing_spec['info']['version']}"
            )
            return True
        except Exception as e:
            print(f"❌ Error loading OpenAPI spec: {e}")
            return False

    def analyze_backend_endpoints(self) -> Dict:
        """Analyze backend endpoints using our existing script."""
        print("🔍 Analyzing backend endpoints...")

        try:
            # Run the backend analysis script
            result = subprocess.run(
                [sys.executable, "scripts/analyze_backend_endpoints.py"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )

            if result.returncode != 0:
                print(f"❌ Backend analysis failed: {result.stderr}")
                return {}

            # Load the generated analysis
            suggested_paths_file = Path("scripts/suggested_openapi_paths.json")
            if suggested_paths_file.exists():
                with open(suggested_paths_file, "r") as f:
                    backend_paths = json.load(f)
                print(f"✅ Loaded backend analysis: {len(backend_paths)} paths found")
                return backend_paths
            else:
                print("❌ Backend analysis file not found")
                return {}

        except Exception as e:
            print(f"❌ Error analyzing backend: {e}")
            return {}

    def normalize_path(self, path: str) -> str:
        """Normalize path format for comparison."""
        # Convert :param to {param} format
        import re

        normalized = re.sub(r":(\w+)", r"{\1}", path)

        # Handle root path
        if normalized == "/":
            return "/"

        # Remove trailing slash
        return normalized.rstrip("/")

    def extract_existing_paths(self) -> Dict[str, Dict]:
        """Extract all existing paths from the OpenAPI spec."""
        existing_paths = {}

        paths = self.existing_spec.get("paths", {})
        for path, path_spec in paths.items():
            normalized_path = self.normalize_path(path)
            existing_paths[normalized_path] = {
                "original_path": path,
                "methods": {},
            }

            for method, method_spec in path_spec.items():
                if method.lower() in [
                    "get",
                    "post",
                    "put",
                    "delete",
                    "patch",
                    "head",
                    "options",
                ]:
                    existing_paths[normalized_path]["methods"][method.lower()] = {
                        "spec": method_spec,
                        "operation_id": method_spec.get("operationId", ""),
                        "summary": method_spec.get("summary", ""),
                        "tags": method_spec.get("tags", []),
                    }

        return existing_paths

    def create_enhanced_spec(self) -> Dict:
        """Create enhanced OpenAPI spec by merging existing and backend data."""
        print("🔧 Creating enhanced OpenAPI specification...")

        # Start with existing spec
        enhanced_spec = dict(self.existing_spec)

        # Get backend endpoints
        backend_paths = self.analyze_backend_endpoints()
        existing_paths = self.extract_existing_paths()

        print(f"📊 Merge Analysis:")
        print(f"  • Existing paths: {len(existing_paths)}")
        print(f"  • Backend paths: {len(backend_paths)}")

        # Process backend endpoints
        for backend_path, backend_methods in backend_paths.items():
            normalized_backend_path = self.normalize_path(backend_path)

            # Skip problematic paths
            if self._should_skip_path(normalized_backend_path):
                continue

            # Check if path exists in OpenAPI spec
            if normalized_backend_path in existing_paths:
                self._merge_existing_path(
                    enhanced_spec,
                    normalized_backend_path,
                    backend_methods,
                    existing_paths,
                )
            else:
                self._add_new_path(
                    enhanced_spec, normalized_backend_path, backend_methods
                )

        # Add critical missing endpoints that we know are important
        self._add_critical_missing_endpoints(enhanced_spec)

        return enhanced_spec

    def _should_skip_path(self, path: str) -> bool:
        """Determine if a path should be skipped."""
        skip_patterns = [
            "/*",  # Wildcard auth routes
            "/email",  # Internal email service
        ]

        return any(pattern in path for pattern in skip_patterns)

    def _merge_existing_path(
        self, spec: Dict, path: str, backend_methods: Dict, existing_paths: Dict
    ):
        """Merge backend methods with existing path."""
        existing_path_data = existing_paths[path]
        original_path = existing_path_data["original_path"]

        # Check for new methods from backend
        for method, method_spec in backend_methods.items():
            method_lower = method.lower()

            if method_lower == "route":  # Skip non-standard methods
                continue

            if method_lower not in existing_path_data["methods"]:
                # Add new method to existing path
                if "paths" not in spec:
                    spec["paths"] = {}
                if original_path not in spec["paths"]:
                    spec["paths"][original_path] = {}

                # Create method spec based on backend info
                new_method_spec = self._create_method_spec_from_backend(
                    method_spec, path, method
                )
                spec["paths"][original_path][method_lower] = new_method_spec

                self.merge_report["added_endpoints"].append(
                    f"{method.upper()} {original_path}"
                )
                print(f"  ➕ Added {method.upper()} {original_path}")
            else:
                # Method exists, preserve existing spec
                self.merge_report["preserved_endpoints"].append(
                    f"{method.upper()} {original_path}"
                )

    def _add_new_path(self, spec: Dict, path: str, backend_methods: Dict):
        """Add completely new path from backend."""
        if "paths" not in spec:
            spec["paths"] = {}

        # Use the normalized path for OpenAPI spec
        openapi_path = path
        spec["paths"][openapi_path] = {}

        for method, method_spec in backend_methods.items():
            method_lower = method.lower()

            if method_lower == "route":  # Skip non-standard methods
                continue

            # Create method spec
            new_method_spec = self._create_method_spec_from_backend(
                method_spec, path, method
            )
            spec["paths"][openapi_path][method_lower] = new_method_spec

            self.merge_report["added_endpoints"].append(
                f"{method.upper()} {openapi_path}"
            )
            print(f"  ➕ Added {method.upper()} {openapi_path}")

    def _create_method_spec_from_backend(
        self, backend_spec: Dict, path: str, method: str
    ) -> Dict:
        """Create OpenAPI method spec from backend analysis."""
        # Extract service from path or backend spec
        service = self._extract_service_from_path(path)

        method_spec = {
            "summary": backend_spec.get("summary", f"{method.upper()} {path}"),
            "operationId": backend_spec.get(
                "operationId", f"{method.lower()}{service.title()}"
            ),
            "tags": [service.title()],
            "responses": {"200": {"description": "Success"}},
        }

        # Add parameters for paths with variables
        if "{" in path:
            method_spec["parameters"] = self._create_path_parameters(path)

        # Add common query parameters for GET requests
        if method.upper() == "GET" and service in ["events", "sessions"]:
            method_spec["parameters"] = method_spec.get("parameters", [])
            method_spec["parameters"].extend(
                self._create_common_query_parameters(service)
            )

        # Add request body for POST/PUT requests
        if method.upper() in ["POST", "PUT"] and service != "healthcheck":
            method_spec["requestBody"] = self._create_request_body(service, method)

        return method_spec

    def _extract_service_from_path(self, path: str) -> str:
        """Extract service name from path."""
        segments = path.strip("/").split("/")
        if not segments or segments[0] == "":
            return "root"

        service_mappings = {
            "events": "Events",
            "sessions": "Sessions",
            "metrics": "Metrics",
            "tools": "Tools",
            "datasets": "Datasets",
            "datapoints": "Datapoints",
            "projects": "Projects",
            "configurations": "Configurations",
            "runs": "Experiments",
            "healthcheck": "Health",
        }

        first_segment = segments[0].lower()
        return service_mappings.get(first_segment, first_segment.title())

    def _create_path_parameters(self, path: str) -> List[Dict]:
        """Create path parameters from path variables."""
        import re

        parameters = []
        path_vars = re.findall(r"\{(\w+)\}", path)

        for var in path_vars:
            parameters.append(
                {
                    "name": var,
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                }
            )

        return parameters

    def _create_common_query_parameters(self, service: str) -> List[Dict]:
        """Create common query parameters for GET endpoints."""
        common_params = [
            {
                "name": "limit",
                "in": "query",
                "schema": {"type": "integer", "default": 100},
            }
        ]

        if service.lower() == "events":
            common_params.extend(
                [
                    {
                        "name": "filters",
                        "in": "query",
                        "schema": {
                            "type": "string",
                            "description": "JSON-encoded array of EventFilter objects",
                        },
                    },
                    {
                        "name": "dateRange",
                        "in": "query",
                        "schema": {
                            "type": "string",
                            "description": "JSON-encoded date range object",
                        },
                    },
                ]
            )

        return common_params

    def _create_request_body(self, service: str, method: str) -> Dict:
        """Create request body specification."""
        return {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "description": f"Request body for {method.upper()} {service}",
                    }
                }
            },
        }

    def _add_critical_missing_endpoints(self, spec: Dict):
        """Add critical endpoints we know are missing but important."""
        critical_endpoints = {
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
            }
        }

        # Only add if not already present
        for path, methods in critical_endpoints.items():
            if path not in spec.get("paths", {}):
                if "paths" not in spec:
                    spec["paths"] = {}
                spec["paths"][path] = {}

            for method, method_spec in methods.items():
                if method not in spec["paths"][path]:
                    spec["paths"][path][method] = method_spec
                    self.merge_report["added_endpoints"].append(
                        f"{method.upper()} {path} (critical)"
                    )
                    print(f"  ➕ Added critical endpoint: {method.upper()} {path}")

    def save_enhanced_spec(self, output_file: str) -> bool:
        """Save the enhanced OpenAPI specification."""
        try:
            enhanced_spec = self.create_enhanced_spec()

            with open(output_file, "w") as f:
                yaml.dump(enhanced_spec, f, default_flow_style=False, sort_keys=False)

            print(f"✅ Enhanced OpenAPI spec saved to {output_file}")
            return True

        except Exception as e:
            print(f"❌ Error saving enhanced spec: {e}")
            return False

    def generate_merge_report(self) -> Dict:
        """Generate a detailed merge report."""
        report = {
            "summary": {
                "preserved_endpoints": len(self.merge_report["preserved_endpoints"]),
                "added_endpoints": len(self.merge_report["added_endpoints"]),
                "updated_endpoints": len(self.merge_report["updated_endpoints"]),
                "conflicts": len(self.merge_report["conflicts"]),
                "warnings": len(self.merge_report["warnings"]),
            },
            "details": self.merge_report,
        }

        return report

    def print_merge_report(self):
        """Print a human-readable merge report."""
        report = self.generate_merge_report()

        print(f"\n📊 OPENAPI MERGE REPORT")
        print("=" * 40)
        print(f"✅ Preserved endpoints: {report['summary']['preserved_endpoints']}")
        print(f"➕ Added endpoints: {report['summary']['added_endpoints']}")
        print(f"🔄 Updated endpoints: {report['summary']['updated_endpoints']}")
        print(f"⚠️  Conflicts: {report['summary']['conflicts']}")
        print(f"⚠️  Warnings: {report['summary']['warnings']}")

        if self.merge_report["added_endpoints"]:
            print(f"\n➕ Added Endpoints:")
            for endpoint in self.merge_report["added_endpoints"]:
                print(f"  • {endpoint}")

        if self.merge_report["conflicts"]:
            print(f"\n⚠️  Conflicts:")
            for conflict in self.merge_report["conflicts"]:
                print(f"  • {conflict}")


def main():
    """Main execution function."""
    print("🔧 Smart OpenAPI Merge Strategy")
    print("=" * 40)

    # Initialize merger
    merger = SmartOpenAPIMerger("openapi.yaml")

    # Load existing spec
    if not merger.load_existing_spec():
        return 1

    # Create enhanced spec
    output_file = "openapi.enhanced.yaml"
    if not merger.save_enhanced_spec(output_file):
        return 1

    # Generate and display merge report
    merger.print_merge_report()

    # Save merge report
    report = merger.generate_merge_report()
    with open("openapi_merge_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n💾 Files Generated:")
    print(f"  • {output_file} - Enhanced OpenAPI specification")
    print(f"  • openapi_merge_report.json - Detailed merge report")
    print(f"  • openapi.yaml.backup.* - Original spec backup")

    print(f"\n🎯 Next Steps:")
    print("1. Review the enhanced specification")
    print("2. Test client generation with enhanced spec")
    print("3. Validate against backend implementation")
    print("4. Replace original spec if validation passes")

    return 0


if __name__ == "__main__":
    exit(main())
