#!/usr/bin/env python3
"""
Backend Endpoint Analysis Script

This script analyzes the backend route files to extract all available endpoints
and compare them against the current OpenAPI specification.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import json


class BackendEndpointAnalyzer:
    def __init__(self, backend_path: str):
        self.backend_path = Path(backend_path)
        self.routes_path = self.backend_path / "app" / "routes"
        self.endpoints = {}

    def analyze_js_routes(self, file_path: Path) -> Dict[str, List[str]]:
        """Analyze JavaScript route files for endpoints."""
        endpoints = {}

        try:
            with open(file_path, "r") as f:
                content = f.read()

            # Find route definitions like .route('/path').get(), .post(), etc.
            route_patterns = [
                r"\.route\(['\"]([^'\"]+)['\"]\)\.(\w+)\(",
                r"router\.(\w+)\(['\"]([^'\"]+)['\"]",
                r"recordRoutes\.route\(['\"]([^'\"]+)['\"]\)\.(\w+)\(",
            ]

            for pattern in route_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if len(match) == 2:
                        if pattern.startswith(r"router\."):
                            method, path = match
                        else:
                            path, method = match

                        if path not in endpoints:
                            endpoints[path] = []
                        endpoints[path].append(method.upper())

            return endpoints

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return {}

    def analyze_ts_routes(self, file_path: Path) -> Dict[str, List[str]]:
        """Analyze TypeScript route files for endpoints."""
        endpoints = {}

        try:
            with open(file_path, "r") as f:
                content = f.read()

            # Find route definitions in TypeScript
            route_patterns = [
                r"router\.(\w+)\(['\"]([^'\"]+)['\"]",
                r"\.route\(['\"]([^'\"]+)['\"]\)\.(\w+)\(",
            ]

            for pattern in route_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if len(match) == 2:
                        if pattern.startswith(r"router\."):
                            method, path = match
                        else:
                            path, method = match

                        if path not in endpoints:
                            endpoints[path] = []
                        endpoints[path].append(method.upper())

            return endpoints

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return {}

    def analyze_all_routes(self) -> Dict[str, Dict[str, List[str]]]:
        """Analyze all route files in the backend."""
        all_endpoints = {}

        if not self.routes_path.exists():
            print(f"Routes path not found: {self.routes_path}")
            return all_endpoints

        for route_file in self.routes_path.iterdir():
            if route_file.is_file():
                file_name = route_file.name

                if file_name.endswith(".js"):
                    endpoints = self.analyze_js_routes(route_file)
                elif file_name.endswith(".ts"):
                    endpoints = self.analyze_ts_routes(route_file)
                else:
                    continue

                if endpoints:
                    # Extract module name from filename
                    module_name = (
                        file_name.replace(".route.ts", "")
                        .replace(".route.js", "")
                        .replace(".js", "")
                        .replace(".ts", "")
                    )
                    all_endpoints[module_name] = endpoints

        return all_endpoints

    def generate_openapi_paths(
        self, endpoints: Dict[str, Dict[str, List[str]]]
    ) -> Dict:
        """Generate OpenAPI paths section from discovered endpoints."""
        paths = {}

        for module, module_endpoints in endpoints.items():
            for path, methods in module_endpoints.items():
                # Convert path parameters from :param to {param}
                openapi_path = re.sub(r":(\w+)", r"{\1}", path)

                if openapi_path not in paths:
                    paths[openapi_path] = {}

                for method in methods:
                    method_lower = method.lower()
                    paths[openapi_path][method_lower] = {
                        "summary": f"{method} {openapi_path}",
                        "operationId": f"{method_lower}{module.title()}",
                        "tags": [module.title()],
                        "responses": {"200": {"description": "Success"}},
                    }

        return paths

    def compare_with_openapi(self, openapi_file: str) -> Dict:
        """Compare discovered endpoints with existing OpenAPI spec."""
        comparison = {
            "backend_only": {},
            "openapi_only": {},
            "matching": {},
            "method_mismatches": {},
        }

        # Load existing OpenAPI spec
        try:
            import yaml

            with open(openapi_file, "r") as f:
                openapi_spec = yaml.safe_load(f)

            openapi_paths = openapi_spec.get("paths", {})
        except Exception as e:
            print(f"Error loading OpenAPI spec: {e}")
            openapi_paths = {}

        # Get backend endpoints
        backend_endpoints = self.analyze_all_routes()

        # Flatten backend endpoints for comparison
        backend_flat = {}
        for module, module_endpoints in backend_endpoints.items():
            for path, methods in module_endpoints.items():
                openapi_path = re.sub(r":(\w+)", r"{\1}", path)
                backend_flat[openapi_path] = set(m.lower() for m in methods)

        # Flatten OpenAPI endpoints
        openapi_flat = {}
        for path, path_spec in openapi_paths.items():
            openapi_flat[path] = set(path_spec.keys())

        # Compare
        backend_paths = set(backend_flat.keys())
        openapi_paths_set = set(openapi_flat.keys())

        comparison["backend_only"] = {
            path: list(backend_flat[path]) for path in backend_paths - openapi_paths_set
        }

        comparison["openapi_only"] = {
            path: list(openapi_flat[path]) for path in openapi_paths_set - backend_paths
        }

        comparison["matching"] = {
            path: {
                "backend": list(backend_flat[path]),
                "openapi": list(openapi_flat[path]),
            }
            for path in backend_paths & openapi_paths_set
        }

        return comparison


def main():
    # Paths
    backend_path = "../../hive-kube/kubernetes/backend_service"
    openapi_file = "../openapi.yaml"

    analyzer = BackendEndpointAnalyzer(backend_path)

    print("🔍 Analyzing Backend Endpoints...")
    print("=" * 50)

    # Analyze all routes
    endpoints = analyzer.analyze_all_routes()

    print(f"📊 Found {len(endpoints)} route modules:")
    for module, module_endpoints in endpoints.items():
        total_endpoints = sum(len(methods) for methods in module_endpoints.values())
        print(
            f"  • {module}: {len(module_endpoints)} paths, {total_endpoints} endpoints"
        )

    print("\n🔍 Detailed Endpoint Analysis:")
    print("=" * 50)

    for module, module_endpoints in endpoints.items():
        print(f"\n📁 {module.upper()} MODULE:")
        for path, methods in module_endpoints.items():
            methods_str = ", ".join(methods)
            print(f"  {methods_str} {path}")

    # Compare with OpenAPI spec
    if os.path.exists(openapi_file):
        print(f"\n🔍 Comparing with {openapi_file}...")
        print("=" * 50)

        comparison = analyzer.compare_with_openapi(openapi_file)

        print(f"\n❌ Backend-only endpoints ({len(comparison['backend_only'])} paths):")
        for path, methods in comparison["backend_only"].items():
            methods_str = ", ".join(methods)
            print(f"  {methods_str} {path}")

        print(f"\n❌ OpenAPI-only endpoints ({len(comparison['openapi_only'])} paths):")
        for path, methods in comparison["openapi_only"].items():
            methods_str = ", ".join(methods)
            print(f"  {methods_str} {path}")

        print(f"\n✅ Matching endpoints ({len(comparison['matching'])} paths):")
        for path, path_data in comparison["matching"].items():
            backend_methods = set(path_data["backend"])
            openapi_methods = set(path_data["openapi"])

            if backend_methods == openapi_methods:
                methods_str = ", ".join(sorted(backend_methods))
                print(f"  ✅ {methods_str} {path}")
            else:
                print(f"  ⚠️  {path}")
                print(f"     Backend: {', '.join(sorted(backend_methods))}")
                print(f"     OpenAPI: {', '.join(sorted(openapi_methods))}")

    # Generate suggested OpenAPI paths
    print(f"\n📝 Generating OpenAPI paths for missing endpoints...")
    suggested_paths = analyzer.generate_openapi_paths(endpoints)

    # Save to file
    output_file = "suggested_openapi_paths.json"
    with open(output_file, "w") as f:
        json.dump(suggested_paths, f, indent=2)

    print(f"💾 Suggested OpenAPI paths saved to: {output_file}")


if __name__ == "__main__":
    main()
