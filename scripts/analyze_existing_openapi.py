#!/usr/bin/env python3
"""
Existing OpenAPI Specification Analysis Script

This script thoroughly analyzes the existing OpenAPI spec to catalog all services,
endpoints, models, and components before making any changes. This ensures we don't
lose any manually curated work by the team.
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Set, Any
from collections import defaultdict


class OpenAPIAnalyzer:
    def __init__(self, openapi_file: str):
        self.openapi_file = Path(openapi_file)
        self.spec = None
        self.analysis = {}

    def load_spec(self) -> bool:
        """Load the OpenAPI specification."""
        try:
            with open(self.openapi_file, "r") as f:
                self.spec = yaml.safe_load(f)
            print(f"✅ Loaded OpenAPI spec from {self.openapi_file}")
            return True
        except Exception as e:
            print(f"❌ Error loading OpenAPI spec: {e}")
            return False

    def analyze_info_section(self) -> Dict:
        """Analyze the info section."""
        info = self.spec.get("info", {})
        return {
            "title": info.get("title", "Unknown"),
            "version": info.get("version", "Unknown"),
            "description": info.get("description", ""),
        }

    def analyze_servers(self) -> List[Dict]:
        """Analyze server configurations."""
        servers = self.spec.get("servers", [])
        return [
            {
                "url": server.get("url", ""),
                "description": server.get("description", ""),
            }
            for server in servers
        ]

    def analyze_paths(self) -> Dict:
        """Analyze all paths and endpoints."""
        paths = self.spec.get("paths", {})

        analysis = {
            "total_paths": len(paths),
            "paths_by_service": defaultdict(list),
            "methods_by_service": defaultdict(set),
            "all_endpoints": [],
            "endpoints_by_method": defaultdict(list),
            "deprecated_endpoints": [],
            "endpoints_with_parameters": [],
            "endpoints_with_request_body": [],
            "endpoints_with_responses": [],
        }

        for path, path_spec in paths.items():
            # Determine service from path
            service = self._extract_service_from_path(path)
            analysis["paths_by_service"][service].append(path)

            # Analyze each HTTP method
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
                    endpoint = {
                        "path": path,
                        "method": method.upper(),
                        "service": service,
                        "operation_id": method_spec.get("operationId", ""),
                        "summary": method_spec.get("summary", ""),
                        "description": method_spec.get("description", ""),
                        "tags": method_spec.get("tags", []),
                        "deprecated": method_spec.get("deprecated", False),
                        "parameters": len(method_spec.get("parameters", [])),
                        "has_request_body": "requestBody" in method_spec,
                        "response_codes": list(method_spec.get("responses", {}).keys()),
                    }

                    analysis["all_endpoints"].append(endpoint)
                    analysis["methods_by_service"][service].add(method.upper())
                    analysis["endpoints_by_method"][method.upper()].append(
                        f"{method.upper()} {path}"
                    )

                    if endpoint["deprecated"]:
                        analysis["deprecated_endpoints"].append(endpoint)

                    if endpoint["parameters"] > 0:
                        analysis["endpoints_with_parameters"].append(endpoint)

                    if endpoint["has_request_body"]:
                        analysis["endpoints_with_request_body"].append(endpoint)

                    if endpoint["response_codes"]:
                        analysis["endpoints_with_responses"].append(endpoint)

        # Convert sets to lists for JSON serialization
        for service in analysis["methods_by_service"]:
            analysis["methods_by_service"][service] = list(
                analysis["methods_by_service"][service]
            )

        return analysis

    def _extract_service_from_path(self, path: str) -> str:
        """Extract service name from path."""
        # Remove leading slash and get first segment
        segments = path.strip("/").split("/")
        if not segments or segments[0] == "":
            return "root"

        # Map common patterns
        service_mappings = {
            "session": "sessions",
            "events": "events",
            "metrics": "metrics",
            "datasets": "datasets",
            "datapoints": "datapoints",
            "tools": "tools",
            "projects": "projects",
            "configurations": "configurations",
            "runs": "experiment_runs",
        }

        first_segment = segments[0].lower()
        return service_mappings.get(first_segment, first_segment)

    def analyze_components(self) -> Dict:
        """Analyze components section (schemas, responses, parameters, etc.)."""
        components = self.spec.get("components", {})

        analysis = {
            "schemas": {},
            "responses": {},
            "parameters": {},
            "examples": {},
            "request_bodies": {},
            "headers": {},
            "security_schemes": {},
            "links": {},
            "callbacks": {},
        }

        for component_type in analysis.keys():
            component_data = components.get(component_type, {})
            analysis[component_type] = {
                "count": len(component_data),
                "names": list(component_data.keys()),
            }

            # Special analysis for schemas
            if component_type == "schemas":
                schema_details = {}
                for schema_name, schema_spec in component_data.items():
                    schema_details[schema_name] = {
                        "type": schema_spec.get("type", "unknown"),
                        "properties": len(schema_spec.get("properties", {})),
                        "required": len(schema_spec.get("required", [])),
                        "has_enum": "enum" in schema_spec,
                        "description": schema_spec.get("description", ""),
                    }
                analysis[component_type]["details"] = schema_details

        return analysis

    def analyze_tags(self) -> Dict:
        """Analyze tags used throughout the spec."""
        tags_section = self.spec.get("tags", [])

        # Get tags from tag section
        defined_tags = {}
        for tag in tags_section:
            defined_tags[tag["name"]] = {
                "description": tag.get("description", ""),
                "external_docs": tag.get("externalDocs", {}),
            }

        # Get tags used in paths
        used_tags = set()
        paths = self.spec.get("paths", {})
        for path, path_spec in paths.items():
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
                    tags = method_spec.get("tags", [])
                    used_tags.update(tags)

        return {
            "defined_tags": defined_tags,
            "used_tags": list(used_tags),
            "undefined_tags": list(used_tags - set(defined_tags.keys())),
            "unused_tags": list(set(defined_tags.keys()) - used_tags),
        }

    def analyze_security(self) -> Dict:
        """Analyze security configurations."""
        security = self.spec.get("security", [])
        security_schemes = self.spec.get("components", {}).get("securitySchemes", {})

        return {
            "global_security": security,
            "security_schemes": {
                name: {
                    "type": scheme.get("type", ""),
                    "scheme": scheme.get("scheme", ""),
                    "description": scheme.get("description", ""),
                }
                for name, scheme in security_schemes.items()
            },
        }

    def generate_comprehensive_analysis(self) -> Dict:
        """Generate comprehensive analysis of the OpenAPI spec."""
        if not self.spec:
            return {}

        analysis = {
            "metadata": {
                "file_path": str(self.openapi_file),
                "openapi_version": self.spec.get("openapi", "unknown"),
                "analysis_timestamp": str(Path(__file__).stat().st_mtime),
            },
            "info": self.analyze_info_section(),
            "servers": self.analyze_servers(),
            "paths": self.analyze_paths(),
            "components": self.analyze_components(),
            "tags": self.analyze_tags(),
            "security": self.analyze_security(),
        }

        return analysis

    def generate_service_summary(self) -> Dict:
        """Generate a summary by service."""
        paths_analysis = self.analyze_paths()

        service_summary = {}
        for service, paths in paths_analysis["paths_by_service"].items():
            endpoints = [
                ep for ep in paths_analysis["all_endpoints"] if ep["service"] == service
            ]

            service_summary[service] = {
                "path_count": len(paths),
                "endpoint_count": len(endpoints),
                "methods": list(paths_analysis["methods_by_service"].get(service, [])),
                "paths": paths,
                "endpoints": endpoints,
            }

        return service_summary

    def save_analysis(self, output_file: str):
        """Save analysis to JSON file."""
        analysis = self.generate_comprehensive_analysis()

        with open(output_file, "w") as f:
            json.dump(analysis, f, indent=2, default=str)

        print(f"✅ Analysis saved to {output_file}")
        return analysis

    def print_summary(self):
        """Print a human-readable summary."""
        analysis = self.generate_comprehensive_analysis()
        service_summary = self.generate_service_summary()

        print("\n🔍 EXISTING OPENAPI SPECIFICATION ANALYSIS")
        print("=" * 60)

        # Basic info
        info = analysis["info"]
        print(f"📋 Title: {info['title']}")
        print(f"📋 Version: {info['version']}")
        print(f"📋 OpenAPI Version: {analysis['metadata']['openapi_version']}")

        # Servers
        servers = analysis["servers"]
        print(f"\n🌐 Servers ({len(servers)}):")
        for server in servers:
            print(f"  • {server['url']} - {server['description']}")

        # Paths summary
        paths = analysis["paths"]
        print(f"\n📊 Paths Summary:")
        print(f"  • Total paths: {paths['total_paths']}")
        print(f"  • Total endpoints: {len(paths['all_endpoints'])}")
        print(f"  • Deprecated endpoints: {len(paths['deprecated_endpoints'])}")

        # Services breakdown
        print(f"\n🏗️  Services Breakdown:")
        for service, summary in service_summary.items():
            methods_str = ", ".join(summary["methods"])
            print(
                f"  • {service.upper()}: {summary['endpoint_count']} endpoints ({methods_str})"
            )

        # Components summary
        components = analysis["components"]
        print(f"\n🧩 Components Summary:")
        for comp_type, comp_data in components.items():
            if comp_data["count"] > 0:
                print(f"  • {comp_type}: {comp_data['count']}")

        # Tags summary
        tags = analysis["tags"]
        print(f"\n🏷️  Tags Summary:")
        print(f"  • Defined tags: {len(tags['defined_tags'])}")
        print(f"  • Used tags: {len(tags['used_tags'])}")
        if tags["undefined_tags"]:
            print(f"  • ⚠️  Undefined tags: {', '.join(tags['undefined_tags'])}")

        # Security summary
        security = analysis["security"]
        print(f"\n🔒 Security Summary:")
        print(f"  • Security schemes: {len(security['security_schemes'])}")
        for name, scheme in security["security_schemes"].items():
            print(f"    - {name}: {scheme['type']} ({scheme['scheme']})")

        print(f"\n📁 Detailed Endpoints by Service:")
        print("-" * 40)
        for service, summary in service_summary.items():
            print(f"\n🔧 {service.upper()} SERVICE:")
            for endpoint in summary["endpoints"]:
                tags_str = (
                    f" [{', '.join(endpoint['tags'])}]" if endpoint["tags"] else ""
                )
                print(f"  {endpoint['method']} {endpoint['path']}{tags_str}")
                if endpoint["summary"]:
                    print(f"    └─ {endpoint['summary']}")


def main():
    """Main execution function."""
    print("🔍 Existing OpenAPI Specification Analysis")
    print("=" * 50)

    # Analyze the existing OpenAPI spec
    openapi_file = "openapi.yaml"
    analyzer = OpenAPIAnalyzer(openapi_file)

    if not analyzer.load_spec():
        return 1

    # Generate and save comprehensive analysis
    output_file = "existing_openapi_analysis.json"
    analysis = analyzer.save_analysis(output_file)

    # Print human-readable summary
    analyzer.print_summary()

    # Generate service-specific reports
    service_summary = analyzer.generate_service_summary()

    print(f"\n💾 Files Generated:")
    print(f"  • {output_file} - Complete analysis in JSON format")
    print(f"  • openapi.yaml.backup.* - Backup of original spec")

    print(f"\n🎯 Key Findings:")
    print(f"  • {analysis['paths']['total_paths']} paths defined")
    print(f"  • {len(analysis['paths']['all_endpoints'])} total endpoints")
    print(f"  • {len(service_summary)} services identified")
    print(f"  • {analysis['components']['schemas']['count']} data models")

    if analysis["paths"]["deprecated_endpoints"]:
        print(
            f"  • ⚠️  {len(analysis['paths']['deprecated_endpoints'])} deprecated endpoints"
        )

    print(f"\n📋 Next Steps:")
    print("1. Review the analysis to understand existing API coverage")
    print("2. Compare with backend implementation using analyze_backend_endpoints.py")
    print("3. Create merge strategy to preserve existing work")
    print("4. Update spec incrementally, not wholesale replacement")

    return 0


if __name__ == "__main__":
    exit(main())
