#!/usr/bin/env python3
"""
Comprehensive Service Discovery Script

This script scans the entire hive-kube repository to discover ALL services and their endpoints,
not just the backend_service. This ensures we capture the complete API surface area for
comprehensive OpenAPI spec generation.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
import json
import subprocess
import yaml


class ComprehensiveServiceDiscovery:
    def __init__(self, hive_kube_path: str):
        self.hive_kube_path = Path(hive_kube_path)
        self.services = {}
        self.all_endpoints = {}

    def discover_all_services(self) -> Dict[str, Dict]:
        """Discover all services in the hive-kube repository."""
        print("🔍 Discovering all services in hive-kube repository...")

        if not self.hive_kube_path.exists():
            print(f"❌ hive-kube path not found: {self.hive_kube_path}")
            return {}

        services = {}

        # Scan for different service patterns
        service_patterns = [
            "kubernetes/*/app/routes",  # Main backend services
            "kubernetes/*/routes",  # Alternative route structure
            "kubernetes/*/src/routes",  # Source-based structure
            "services/*/routes",  # Services directory
            "microservices/*/routes",  # Microservices
            "apps/*/routes",  # Apps directory
            "*/app.js",  # Express apps
            "*/server.js",  # Server files
            "*/index.js",  # Index files with routes
            "*/main.ts",  # TypeScript main files
            "*/app.ts",  # TypeScript app files
        ]

        for pattern in service_patterns:
            services.update(self._scan_pattern(pattern))

        # Also scan for Docker services
        docker_services = self._discover_docker_services()
        services.update(docker_services)

        # Scan for serverless functions
        serverless_services = self._discover_serverless_functions()
        services.update(serverless_services)

        self.services = services
        return services

    def _scan_pattern(self, pattern: str) -> Dict[str, Dict]:
        """Scan for services matching a specific pattern."""
        services = {}

        try:
            # Use glob to find matching paths
            import glob

            full_pattern = str(self.hive_kube_path / pattern)
            matches = glob.glob(full_pattern, recursive=True)

            for match in matches:
                match_path = Path(match)

                if match_path.is_dir():
                    # It's a routes directory
                    service_name = self._extract_service_name_from_path(match_path)
                    endpoints = self._analyze_routes_directory(match_path)

                    if endpoints:
                        services[service_name] = {
                            "type": "routes_directory",
                            "path": str(match_path),
                            "endpoints": endpoints,
                        }
                        print(
                            f"  📁 Found routes directory: {service_name} ({len(endpoints)} endpoints)"
                        )

                elif match_path.is_file():
                    # It's a server/app file
                    service_name = self._extract_service_name_from_path(
                        match_path.parent
                    )
                    endpoints = self._analyze_server_file(match_path)

                    if endpoints:
                        services[service_name] = {
                            "type": "server_file",
                            "path": str(match_path),
                            "endpoints": endpoints,
                        }
                        print(
                            f"  📄 Found server file: {service_name} ({len(endpoints)} endpoints)"
                        )

        except Exception as e:
            print(f"  ⚠️  Error scanning pattern {pattern}: {e}")

        return services

    def _extract_service_name_from_path(self, path: Path) -> str:
        """Extract service name from file path."""
        # Get relative path from hive-kube root
        try:
            rel_path = path.relative_to(self.hive_kube_path)
            parts = rel_path.parts

            # Common service name extraction patterns
            if "kubernetes" in parts:
                # kubernetes/service_name/...
                idx = parts.index("kubernetes")
                if idx + 1 < len(parts):
                    return parts[idx + 1]

            elif "services" in parts:
                # services/service_name/...
                idx = parts.index("services")
                if idx + 1 < len(parts):
                    return parts[idx + 1]

            elif "microservices" in parts:
                # microservices/service_name/...
                idx = parts.index("microservices")
                if idx + 1 < len(parts):
                    return parts[idx + 1]

            elif "apps" in parts:
                # apps/service_name/...
                idx = parts.index("apps")
                if idx + 1 < len(parts):
                    return parts[idx + 1]

            # Fallback: use first directory name
            return parts[0] if parts else "unknown"

        except ValueError:
            return path.name

    def _analyze_routes_directory(self, routes_dir: Path) -> Dict[str, List[str]]:
        """Analyze a routes directory for endpoints."""
        endpoints = {}

        try:
            for route_file in routes_dir.iterdir():
                if route_file.is_file() and route_file.suffix in [".js", ".ts"]:
                    file_endpoints = self._analyze_route_file(route_file)

                    if file_endpoints:
                        # Use filename as module name
                        module_name = route_file.stem
                        endpoints[module_name] = file_endpoints

        except Exception as e:
            print(f"    ⚠️  Error analyzing routes directory {routes_dir}: {e}")

        return endpoints

    def _analyze_server_file(self, server_file: Path) -> Dict[str, List[str]]:
        """Analyze a server file for endpoints."""
        try:
            endpoints = self._analyze_route_file(server_file)
            if endpoints:
                return {"main": endpoints}
            return {}
        except Exception as e:
            print(f"    ⚠️  Error analyzing server file {server_file}: {e}")
            return {}

    def _analyze_route_file(self, route_file: Path) -> Dict[str, List[str]]:
        """Analyze a single route file for endpoints."""
        endpoints = {}

        try:
            with open(route_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Multiple patterns for different frameworks and styles
            route_patterns = [
                # Express.js patterns
                r"\.route\(['\"]([^'\"]+)['\"]\)\.(\w+)\(",
                r"router\.(\w+)\(['\"]([^'\"]+)['\"]",
                r"app\.(\w+)\(['\"]([^'\"]+)['\"]",
                # Fastify patterns
                r"fastify\.(\w+)\(['\"]([^'\"]+)['\"]",
                r"server\.(\w+)\(['\"]([^'\"]+)['\"]",
                # Koa patterns
                r"router\.(\w+)\(['\"]([^'\"]+)['\"]",
                # NestJS patterns
                r"@(\w+)\(['\"]([^'\"]+)['\"]\)",
                # Custom patterns
                r"recordRoutes\.route\(['\"]([^'\"]+)['\"]\)\.(\w+)\(",
                # OpenAPI/Swagger annotations
                r"@swagger\.(\w+)\(['\"]([^'\"]+)['\"]",
                # GraphQL patterns (just to identify them)
                r"type\s+(\w+)\s*\{",
                r"Query\s*\{",
                r"Mutation\s*\{",
            ]

            for pattern in route_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)

                for match in matches:
                    if len(match) == 2:
                        # Determine which is method and which is path
                        if pattern.startswith(r"\.route") or pattern.startswith(
                            r"recordRoutes"
                        ):
                            path, method = match
                        elif pattern.startswith(r"@"):
                            method, path = match
                        else:
                            method, path = match

                        # Normalize method
                        method = method.lower()
                        if method in [
                            "get",
                            "post",
                            "put",
                            "delete",
                            "patch",
                            "head",
                            "options",
                        ]:
                            if path not in endpoints:
                                endpoints[path] = []
                            endpoints[path].append(method.upper())

            # Also look for route mounting patterns
            mount_patterns = [
                r"app\.use\(['\"]([^'\"]+)['\"],\s*(\w+)",
                r"router\.use\(['\"]([^'\"]+)['\"],\s*(\w+)",
                r"server\.register\((\w+),\s*\{\s*prefix:\s*['\"]([^'\"]+)['\"]",
            ]

            for pattern in mount_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if len(match) == 2:
                        prefix, router_name = match
                        # Note: This would require deeper analysis to get actual endpoints
                        endpoints[f"{prefix}/*"] = ["MOUNT"]

        except Exception as e:
            print(f"      ⚠️  Error reading file {route_file}: {e}")

        return endpoints

    def _discover_docker_services(self) -> Dict[str, Dict]:
        """Discover services from Docker configurations."""
        services = {}

        try:
            # Look for docker-compose files
            compose_patterns = [
                "docker-compose*.yml",
                "docker-compose*.yaml",
                "compose*.yml",
                "compose*.yaml",
            ]

            for pattern in compose_patterns:
                compose_files = list(self.hive_kube_path.rglob(pattern))

                for compose_file in compose_files:
                    docker_services = self._analyze_docker_compose(compose_file)
                    services.update(docker_services)

            # Look for individual Dockerfiles
            dockerfiles = list(self.hive_kube_path.rglob("Dockerfile*"))
            for dockerfile in dockerfiles:
                service_name = self._extract_service_name_from_path(dockerfile.parent)

                # Try to find associated server files
                server_files = []
                for pattern in ["app.js", "server.js", "main.ts", "app.ts", "index.js"]:
                    server_file = dockerfile.parent / pattern
                    if server_file.exists():
                        server_files.append(server_file)

                if server_files:
                    endpoints = {}
                    for server_file in server_files:
                        file_endpoints = self._analyze_server_file(server_file)
                        endpoints.update(file_endpoints)

                    if endpoints:
                        services[f"{service_name}_docker"] = {
                            "type": "docker_service",
                            "path": str(dockerfile.parent),
                            "dockerfile": str(dockerfile),
                            "endpoints": endpoints,
                        }
                        print(f"  🐳 Found Docker service: {service_name}_docker")

        except Exception as e:
            print(f"  ⚠️  Error discovering Docker services: {e}")

        return services

    def _analyze_docker_compose(self, compose_file: Path) -> Dict[str, Dict]:
        """Analyze a docker-compose file for services."""
        services = {}

        try:
            with open(compose_file, "r") as f:
                compose_data = yaml.safe_load(f)

            compose_services = compose_data.get("services", {})

            for service_name, service_config in compose_services.items():
                # Look for port mappings to identify web services
                ports = service_config.get("ports", [])

                if ports:
                    # This is likely a web service
                    build_context = service_config.get("build", {})
                    if isinstance(build_context, str):
                        service_path = compose_file.parent / build_context
                    elif isinstance(build_context, dict):
                        context = build_context.get("context", ".")
                        service_path = compose_file.parent / context
                    else:
                        service_path = compose_file.parent

                    # Try to find endpoints in the service
                    endpoints = {}
                    if service_path.exists():
                        # Look for common server files
                        for pattern in ["app/routes", "routes", "src/routes"]:
                            routes_dir = service_path / pattern
                            if routes_dir.exists():
                                endpoints.update(
                                    self._analyze_routes_directory(routes_dir)
                                )

                    if endpoints:
                        services[f"{service_name}_compose"] = {
                            "type": "docker_compose_service",
                            "path": str(service_path),
                            "compose_file": str(compose_file),
                            "ports": ports,
                            "endpoints": endpoints,
                        }
                        print(f"  🐳 Found compose service: {service_name}_compose")

        except Exception as e:
            print(f"    ⚠️  Error analyzing compose file {compose_file}: {e}")

        return services

    def _discover_serverless_functions(self) -> Dict[str, Dict]:
        """Discover serverless functions (Lambda, etc.)."""
        services = {}

        try:
            # Look for serverless configurations
            serverless_patterns = [
                "serverless.yml",
                "serverless.yaml",
                "template.yml",
                "template.yaml",
                "sam.yml",
                "sam.yaml",
            ]

            for pattern in serverless_patterns:
                config_files = list(self.hive_kube_path.rglob(pattern))

                for config_file in config_files:
                    serverless_services = self._analyze_serverless_config(config_file)
                    services.update(serverless_services)

        except Exception as e:
            print(f"  ⚠️  Error discovering serverless functions: {e}")

        return services

    def _analyze_serverless_config(self, config_file: Path) -> Dict[str, Dict]:
        """Analyze serverless configuration for functions."""
        services = {}

        try:
            with open(config_file, "r") as f:
                config_data = yaml.safe_load(f)

            # Serverless Framework format
            if "functions" in config_data:
                functions = config_data["functions"]

                for func_name, func_config in functions.items():
                    events = func_config.get("events", [])
                    endpoints = {}

                    for event in events:
                        if "http" in event:
                            http_config = event["http"]
                            method = http_config.get("method", "GET").upper()
                            path = http_config.get("path", "/")

                            if path not in endpoints:
                                endpoints[path] = []
                            endpoints[path].append(method)

                    if endpoints:
                        services[f"{func_name}_serverless"] = {
                            "type": "serverless_function",
                            "path": str(config_file.parent),
                            "config_file": str(config_file),
                            "endpoints": {"main": endpoints},
                        }
                        print(f"  ⚡ Found serverless function: {func_name}_serverless")

            # AWS SAM format
            elif "Resources" in config_data:
                resources = config_data["Resources"]

                for resource_name, resource_config in resources.items():
                    if resource_config.get("Type") == "AWS::Serverless::Function":
                        properties = resource_config.get("Properties", {})
                        events = properties.get("Events", {})
                        endpoints = {}

                        for event_name, event_config in events.items():
                            if event_config.get("Type") == "Api":
                                api_properties = event_config.get("Properties", {})
                                method = api_properties.get("Method", "GET").upper()
                                path = api_properties.get("Path", "/")

                                if path not in endpoints:
                                    endpoints[path] = []
                                endpoints[path].append(method)

                        if endpoints:
                            services[f"{resource_name}_sam"] = {
                                "type": "sam_function",
                                "path": str(config_file.parent),
                                "config_file": str(config_file),
                                "endpoints": {"main": endpoints},
                            }
                            print(f"  ⚡ Found SAM function: {resource_name}_sam")

        except Exception as e:
            print(f"    ⚠️  Error analyzing serverless config {config_file}: {e}")

        return services

    def generate_comprehensive_report(self) -> Dict:
        """Generate comprehensive service discovery report."""
        # Flatten all endpoints
        all_endpoints = {}
        service_summary = {}

        for service_name, service_data in self.services.items():
            endpoints = service_data.get("endpoints", {})
            endpoint_count = 0

            for module, module_endpoints in endpoints.items():
                if isinstance(module_endpoints, dict):
                    for path, methods in module_endpoints.items():
                        endpoint_count += (
                            len(methods) if isinstance(methods, list) else 1
                        )

                        # Add to all_endpoints
                        full_path = (
                            f"/{service_name}{path}"
                            if not path.startswith("/")
                            else path
                        )
                        if full_path not in all_endpoints:
                            all_endpoints[full_path] = {}

                        if isinstance(methods, list):
                            for method in methods:
                                all_endpoints[full_path][method.lower()] = {
                                    "service": service_name,
                                    "module": module,
                                    "type": service_data["type"],
                                }
                else:
                    endpoint_count += (
                        len(module_endpoints)
                        if isinstance(module_endpoints, list)
                        else 1
                    )

            service_summary[service_name] = {
                "type": service_data["type"],
                "path": service_data["path"],
                "endpoint_count": endpoint_count,
                "modules": list(endpoints.keys()),
            }

        return {
            "services": service_summary,
            "all_endpoints": all_endpoints,
            "total_services": len(self.services),
            "total_endpoints": len(all_endpoints),
        }

    def save_discovery_report(self, output_file: str):
        """Save comprehensive discovery report."""
        report = self.generate_comprehensive_report()

        # Add detailed service data
        report["detailed_services"] = self.services

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        print(f"✅ Comprehensive service discovery report saved to {output_file}")
        return report

    def print_discovery_summary(self):
        """Print human-readable discovery summary."""
        report = self.generate_comprehensive_report()

        print(f"\n🔍 COMPREHENSIVE SERVICE DISCOVERY REPORT")
        print("=" * 60)
        print(f"📊 Total services discovered: {report['total_services']}")
        print(f"📊 Total endpoints discovered: {report['total_endpoints']}")

        print(f"\n🏗️  Services by Type:")
        type_counts = {}
        for service_name, service_data in report["services"].items():
            service_type = service_data["type"]
            type_counts[service_type] = type_counts.get(service_type, 0) + 1

        for service_type, count in type_counts.items():
            print(f"  • {service_type}: {count} services")

        print(f"\n📋 Service Details:")
        for service_name, service_data in report["services"].items():
            print(f"\n🔧 {service_name.upper()}:")
            print(f"  Type: {service_data['type']}")
            print(f"  Path: {service_data['path']}")
            print(f"  Endpoints: {service_data['endpoint_count']}")
            print(f"  Modules: {', '.join(service_data['modules'])}")


def main():
    """Main execution function."""
    print("🔍 Comprehensive Service Discovery")
    print("=" * 50)

    # Path to hive-kube repository
    hive_kube_path = "../hive-kube"

    if not Path(hive_kube_path).exists():
        print(f"❌ hive-kube repository not found at {hive_kube_path}")
        print("Please ensure the hive-kube repository is cloned alongside python-sdk")
        return 1

    # Initialize discovery
    discovery = ComprehensiveServiceDiscovery(hive_kube_path)

    # Discover all services
    services = discovery.discover_all_services()

    if not services:
        print("❌ No services discovered")
        return 1

    # Generate and save report
    output_file = "comprehensive_service_discovery.json"
    report = discovery.save_discovery_report(output_file)

    # Print summary
    discovery.print_discovery_summary()

    print(f"\n💾 Files Generated:")
    print(f"  • {output_file} - Complete service discovery report")

    print(f"\n🎯 Next Steps:")
    print("1. Review discovered services and endpoints")
    print("2. Use this data to generate comprehensive OpenAPI spec")
    print("3. Validate against actual service implementations")
    print("4. Generate unified Python SDK client")

    return 0


if __name__ == "__main__":
    exit(main())
