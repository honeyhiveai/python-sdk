#!/usr/bin/env python3
"""
Dynamic OpenAPI Generator

This script uses dynamic logic principles (not static patterns) to generate
comprehensive OpenAPI specifications. It adapts to actual service implementations,
handles errors gracefully, and processes data efficiently.

Key Dynamic Principles:
1. Adaptive endpoint discovery based on actual code analysis
2. Early error detection and graceful degradation
3. Memory-efficient processing of large service codebases
4. Context-aware schema generation
5. Intelligent conflict resolution
"""

import ast
import os
import re
import json
import yaml
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Union, Generator
from dataclasses import dataclass, field
from collections import defaultdict
import logging

# Set up logging for dynamic processing
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EndpointInfo:
    """Dynamic endpoint information with adaptive properties."""

    path: str
    method: str
    service: str
    module: str
    handler_function: Optional[str] = None
    parameters: List[Dict] = field(default_factory=list)
    request_body_schema: Optional[Dict] = None
    response_schema: Optional[Dict] = None
    middleware: List[str] = field(default_factory=list)
    auth_required: bool = True
    tags: List[str] = field(default_factory=list)
    summary: str = ""
    description: str = ""
    deprecated: bool = False
    confidence_score: float = 1.0  # Dynamic confidence in endpoint detection


@dataclass
class ServiceInfo:
    """Dynamic service information with adaptive discovery."""

    name: str
    path: Path
    type: str
    endpoints: List[EndpointInfo] = field(default_factory=list)
    schemas: Dict[str, Dict] = field(default_factory=dict)
    middleware: List[str] = field(default_factory=list)
    auth_schemes: List[str] = field(default_factory=list)
    base_path: str = ""
    version: str = "1.0.0"
    health_check_path: Optional[str] = None


class DynamicOpenAPIGenerator:
    """
    Dynamic OpenAPI generator that adapts to actual service implementations.

    Uses dynamic logic principles:
    - Adaptive processing based on actual code structure
    - Early error detection with graceful degradation
    - Memory-efficient streaming for large codebases
    - Context-aware schema inference
    """

    def __init__(
        self, hive_kube_path: str, existing_openapi_path: Optional[str] = None
    ):
        self.hive_kube_path = Path(hive_kube_path)
        self.existing_openapi_path = (
            Path(existing_openapi_path) if existing_openapi_path else None
        )
        self.services: Dict[str, ServiceInfo] = {}
        self.global_schemas: Dict[str, Dict] = {}
        self.processing_stats = {
            "files_processed": 0,
            "endpoints_discovered": 0,
            "schemas_inferred": 0,
            "errors_handled": 0,
            "processing_time": 0.0,
        }

        # Dynamic processing thresholds (adaptive)
        self.max_file_size = 1024 * 1024  # 1MB per file
        self.max_processing_time = 30.0  # 30 seconds per service
        self.confidence_threshold = 0.7  # Minimum confidence for endpoint inclusion

    def discover_services_dynamically(self) -> Dict[str, ServiceInfo]:
        """
        Dynamically discover services using adaptive algorithms.

        Uses dynamic logic:
        - Adapts to different service structures
        - Early termination on errors
        - Memory-efficient processing
        """
        logger.info("🔍 Starting dynamic service discovery...")

        try:
            # Use generator for memory efficiency
            for service_path in self._discover_service_paths():
                try:
                    service = self._analyze_service_dynamically(service_path)
                    if service and len(service.endpoints) > 0:
                        self.services[service.name] = service
                        logger.info(
                            f"✅ Discovered service: {service.name} ({len(service.endpoints)} endpoints)"
                        )

                except Exception as e:
                    self.processing_stats["errors_handled"] += 1
                    logger.warning(f"⚠️  Error analyzing service {service_path}: {e}")
                    # Continue processing other services (graceful degradation)
                    continue

            logger.info(
                f"🎯 Discovery complete: {len(self.services)} services, {sum(len(s.endpoints) for s in self.services.values())} endpoints"
            )
            return self.services

        except Exception as e:
            logger.error(f"❌ Critical error in service discovery: {e}")
            return {}

    def _discover_service_paths(self) -> Generator[Path, None, None]:
        """Generator for memory-efficient service path discovery."""
        if not self.hive_kube_path.exists():
            logger.error(f"❌ hive-kube path not found: {self.hive_kube_path}")
            return

        # Dynamic service discovery patterns (adaptive)
        service_patterns = [
            "kubernetes/*/app/routes",
            "kubernetes/*/routes",
            "kubernetes/*/src/routes",
            "services/*/routes",
            "microservices/*/routes",
        ]

        for pattern in service_patterns:
            try:
                import glob

                full_pattern = str(self.hive_kube_path / pattern)

                for match in glob.glob(full_pattern, recursive=True):
                    match_path = Path(match)
                    if match_path.is_dir():
                        yield match_path

            except Exception as e:
                logger.warning(f"⚠️  Error in pattern {pattern}: {e}")
                continue

    def _analyze_service_dynamically(self, service_path: Path) -> Optional[ServiceInfo]:
        """
        Dynamically analyze a service using adaptive algorithms.

        Key dynamic features:
        - Adapts to different code structures
        - Infers schemas from actual usage
        - Handles errors gracefully
        """
        import time

        start_time = time.time()

        try:
            service_name = self._extract_service_name(service_path)
            service = ServiceInfo(
                name=service_name, path=service_path, type="microservice"
            )

            # Process route files dynamically
            for route_file in self._get_route_files(service_path):
                # Check processing time (early termination)
                if time.time() - start_time > self.max_processing_time:
                    logger.warning(
                        f"⚠️  Processing timeout for {service_name}, using partial results"
                    )
                    break

                # Check file size (memory efficiency)
                if route_file.stat().st_size > self.max_file_size:
                    logger.warning(
                        f"⚠️  Large file skipped: {route_file} ({route_file.stat().st_size} bytes)"
                    )
                    continue

                endpoints = self._analyze_route_file_dynamically(
                    route_file, service_name
                )
                service.endpoints.extend(endpoints)

                self.processing_stats["files_processed"] += 1

            # Dynamic schema inference
            service.schemas = self._infer_schemas_dynamically(service.endpoints)

            # Dynamic service configuration inference
            self._infer_service_config_dynamically(service, service_path)

            self.processing_stats["endpoints_discovered"] += len(service.endpoints)
            self.processing_stats["processing_time"] += time.time() - start_time

            return service

        except Exception as e:
            logger.error(f"❌ Error analyzing service {service_path}: {e}")
            return None

    def _get_route_files(self, service_path: Path) -> Generator[Path, None, None]:
        """Generator for memory-efficient route file discovery."""
        try:
            for file_path in service_path.rglob("*.js"):
                yield file_path
            for file_path in service_path.rglob("*.ts"):
                yield file_path
        except Exception as e:
            logger.warning(f"⚠️  Error discovering route files in {service_path}: {e}")

    def _analyze_route_file_dynamically(
        self, route_file: Path, service_name: str
    ) -> List[EndpointInfo]:
        """
        Dynamically analyze route file using adaptive parsing.

        Key features:
        - Multiple parsing strategies (fallback approach)
        - Context-aware endpoint detection
        - Confidence scoring for results
        """
        endpoints = []

        try:
            with open(route_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Strategy 1: AST parsing (most accurate)
            ast_endpoints = self._parse_with_ast(content, route_file, service_name)
            if ast_endpoints:
                endpoints.extend(ast_endpoints)
                return endpoints  # Early return if AST parsing succeeds

            # Strategy 2: Regex parsing (fallback)
            regex_endpoints = self._parse_with_regex(content, route_file, service_name)
            endpoints.extend(regex_endpoints)

            # Strategy 3: Pattern matching (last resort)
            if not endpoints:
                pattern_endpoints = self._parse_with_patterns(
                    content, route_file, service_name
                )
                endpoints.extend(pattern_endpoints)

            # Dynamic confidence scoring
            for endpoint in endpoints:
                endpoint.confidence_score = self._calculate_confidence_score(
                    endpoint, content
                )

            # Filter by confidence threshold
            high_confidence_endpoints = [
                ep
                for ep in endpoints
                if ep.confidence_score >= self.confidence_threshold
            ]

            if len(high_confidence_endpoints) < len(endpoints):
                logger.info(
                    f"📊 Filtered {len(endpoints) - len(high_confidence_endpoints)} low-confidence endpoints from {route_file.name}"
                )

            return high_confidence_endpoints

        except Exception as e:
            logger.warning(f"⚠️  Error analyzing route file {route_file}: {e}")
            return []

    def _parse_with_ast(
        self, content: str, route_file: Path, service_name: str
    ) -> List[EndpointInfo]:
        """Parse JavaScript/TypeScript using AST (most accurate method)."""
        endpoints = []

        try:
            # For JavaScript/TypeScript, we'd need a JS parser
            # For now, return empty to fall back to regex
            return []

        except Exception as e:
            logger.debug(f"AST parsing failed for {route_file}: {e}")
            return []

    def _parse_with_regex(
        self, content: str, route_file: Path, service_name: str
    ) -> List[EndpointInfo]:
        """Parse using dynamic regex patterns (adaptive approach)."""
        endpoints = []

        # Dynamic regex patterns (adaptive to different frameworks)
        patterns = [
            # Express.js patterns
            (r"\.route\(['\"]([^'\"]+)['\"]\)\.(\w+)\(", "express_route"),
            (r"router\.(\w+)\(['\"]([^'\"]+)['\"]", "express_router"),
            (r"app\.(\w+)\(['\"]([^'\"]+)['\"]", "express_app"),
            # Fastify patterns
            (r"fastify\.(\w+)\(['\"]([^'\"]+)['\"]", "fastify"),
            # Custom patterns
            (r"recordRoutes\.route\(['\"]([^'\"]+)['\"]\)\.(\w+)\(", "custom_route"),
        ]

        for pattern, pattern_type in patterns:
            try:
                matches = re.findall(pattern, content, re.IGNORECASE)

                for match in matches:
                    endpoint = self._create_endpoint_from_match(
                        match, pattern_type, route_file, service_name
                    )
                    if endpoint:
                        endpoints.append(endpoint)

            except Exception as e:
                logger.debug(f"Regex pattern {pattern_type} failed: {e}")
                continue

        return endpoints

    def _parse_with_patterns(
        self, content: str, route_file: Path, service_name: str
    ) -> List[EndpointInfo]:
        """Parse using simple pattern matching (last resort)."""
        endpoints = []

        # Look for common HTTP method keywords
        http_methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        lines = content.split("\n")

        for i, line in enumerate(lines):
            for method in http_methods:
                if method.lower() in line.lower() and (
                    "/" in line or "route" in line.lower()
                ):
                    # Try to extract path from context
                    path = self._extract_path_from_line(line)
                    if path:
                        endpoint = EndpointInfo(
                            path=path,
                            method=method,
                            service=service_name,
                            module=route_file.stem,
                            confidence_score=0.5,  # Lower confidence for pattern matching
                        )
                        endpoints.append(endpoint)

        return endpoints

    def _create_endpoint_from_match(
        self, match: tuple, pattern_type: str, route_file: Path, service_name: str
    ) -> Optional[EndpointInfo]:
        """Dynamically create endpoint from regex match."""
        try:
            if pattern_type in ["express_route", "custom_route"]:
                path, method = match
            elif pattern_type in ["express_router", "express_app", "fastify"]:
                method, path = match
            else:
                return None

            # Normalize method
            method = method.upper()
            if method not in [
                "GET",
                "POST",
                "PUT",
                "DELETE",
                "PATCH",
                "HEAD",
                "OPTIONS",
            ]:
                return None

            # Normalize path
            if not path.startswith("/"):
                path = "/" + path

            endpoint = EndpointInfo(
                path=path,
                method=method,
                service=service_name,
                module=route_file.stem,
                confidence_score=0.8,  # High confidence for regex matches
            )

            # Dynamic tag inference
            endpoint.tags = self._infer_tags_dynamically(endpoint, service_name)

            # Dynamic summary generation
            endpoint.summary = self._generate_summary_dynamically(endpoint)

            return endpoint

        except Exception as e:
            logger.debug(f"Error creating endpoint from match {match}: {e}")
            return None

    def _extract_path_from_line(self, line: str) -> Optional[str]:
        """Dynamically extract path from code line."""
        # Look for quoted strings that look like paths
        path_patterns = [
            r"['\"]([^'\"]*\/[^'\"]*)['\"]",  # Quoted strings with slashes
            r"['\"](\/{1}[^'\"]*)['\"]",  # Strings starting with /
        ]

        for pattern in path_patterns:
            matches = re.findall(pattern, line)
            for match in matches:
                if match.startswith("/") and len(match) > 1:
                    return match

        return None

    def _calculate_confidence_score(
        self, endpoint: EndpointInfo, content: str
    ) -> float:
        """Dynamically calculate confidence score for endpoint."""
        score = endpoint.confidence_score

        # Boost score for well-structured endpoints
        if endpoint.path.count("/") > 1:
            score += 0.1

        # Boost score if handler function is found
        if endpoint.handler_function:
            score += 0.1

        # Boost score if parameters are detected
        if endpoint.parameters:
            score += 0.1

        # Reduce score for very generic paths
        if endpoint.path in ["/", "/health", "/status"]:
            score -= 0.1

        # Boost score if middleware is detected
        if "middleware" in content.lower():
            score += 0.05

        return min(1.0, max(0.0, score))

    def _infer_schemas_dynamically(
        self, endpoints: List[EndpointInfo]
    ) -> Dict[str, Dict]:
        """Dynamically infer schemas from endpoint usage patterns."""
        schemas = {}

        # Group endpoints by path patterns
        path_groups = defaultdict(list)
        for endpoint in endpoints:
            # Extract base path (remove parameters)
            base_path = re.sub(r"\{[^}]+\}", "", endpoint.path).rstrip("/")
            path_groups[base_path].append(endpoint)

        # Infer schemas for each path group
        for base_path, group_endpoints in path_groups.items():
            schema_name = self._generate_schema_name(base_path)

            # Infer schema properties from endpoint patterns
            properties = {}

            # Common properties based on HTTP methods
            if any(ep.method == "GET" for ep in group_endpoints):
                properties.update(self._infer_get_response_schema(group_endpoints))

            if any(ep.method in ["POST", "PUT"] for ep in group_endpoints):
                properties.update(self._infer_request_body_schema(group_endpoints))

            if properties:
                schemas[schema_name] = {
                    "type": "object",
                    "properties": properties,
                    "description": f"Schema for {base_path} endpoints",
                }

        return schemas

    def _generate_schema_name(self, base_path: str) -> str:
        """Generate schema name from path."""
        # Convert /events/export -> EventsExport
        parts = [part.capitalize() for part in base_path.strip("/").split("/") if part]
        return "".join(parts) if parts else "Root"

    def _infer_get_response_schema(
        self, endpoints: List[EndpointInfo]
    ) -> Dict[str, Dict]:
        """Infer GET response schema properties."""
        properties = {}

        # Common response patterns
        if any("list" in ep.path.lower() or ep.path.endswith("s") for ep in endpoints):
            # Array response
            properties["data"] = {
                "type": "array",
                "items": {"type": "object"},
                "description": "List of items",
            }
            properties["total"] = {"type": "integer", "description": "Total count"}
        else:
            # Single object response
            properties["data"] = {"type": "object", "description": "Response data"}

        return properties

    def _infer_request_body_schema(
        self, endpoints: List[EndpointInfo]
    ) -> Dict[str, Dict]:
        """Infer request body schema properties."""
        properties = {}

        # Common request patterns based on path
        for endpoint in endpoints:
            if "create" in endpoint.path.lower() or endpoint.method == "POST":
                properties["name"] = {"type": "string", "description": "Name"}
                properties["description"] = {
                    "type": "string",
                    "description": "Description",
                }

            if "filter" in endpoint.path.lower():
                properties["filters"] = {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "Filter criteria",
                }

        return properties

    def _infer_service_config_dynamically(
        self, service: ServiceInfo, service_path: Path
    ):
        """Dynamically infer service configuration."""
        try:
            # Look for package.json or similar config files
            package_json = service_path.parent / "package.json"
            if package_json.exists():
                with open(package_json, "r") as f:
                    package_data = json.load(f)
                    service.version = package_data.get("version", "1.0.0")

            # Infer base path from service name
            service.base_path = (
                f"/{service.name.replace('_service', '').replace('_', '-')}"
            )

            # Look for health check endpoints
            health_endpoints = [
                ep for ep in service.endpoints if "health" in ep.path.lower()
            ]
            if health_endpoints:
                service.health_check_path = health_endpoints[0].path

        except Exception as e:
            logger.debug(f"Error inferring service config for {service.name}: {e}")

    def _infer_tags_dynamically(
        self, endpoint: EndpointInfo, service_name: str
    ) -> List[str]:
        """Dynamically infer tags for endpoint."""
        tags = []

        # Service-based tag
        tags.append(service_name.replace("_", " ").title())

        # Path-based tags
        path_parts = [
            part
            for part in endpoint.path.split("/")
            if part and not part.startswith("{")
        ]
        if path_parts:
            tags.append(path_parts[0].capitalize())

        return tags

    def _generate_summary_dynamically(self, endpoint: EndpointInfo) -> str:
        """Dynamically generate endpoint summary."""
        method = endpoint.method
        path = endpoint.path

        # Generate summary based on method and path patterns
        if method == "GET":
            if path.endswith("s") or "list" in path.lower():
                return f"List {self._extract_resource_name(path)}"
            elif "{" in path:
                return f"Get {self._extract_resource_name(path)} by ID"
            else:
                return f"Get {self._extract_resource_name(path)}"

        elif method == "POST":
            if "batch" in path.lower():
                return f"Create batch of {self._extract_resource_name(path)}"
            else:
                return f"Create {self._extract_resource_name(path)}"

        elif method == "PUT":
            return f"Update {self._extract_resource_name(path)}"

        elif method == "DELETE":
            return f"Delete {self._extract_resource_name(path)}"

        else:
            return f"{method} {path}"

    def _extract_resource_name(self, path: str) -> str:
        """Extract resource name from path."""
        parts = [part for part in path.split("/") if part and not part.startswith("{")]
        return parts[0] if parts else "resource"

    def _extract_service_name(self, service_path: Path) -> str:
        """Extract service name from path."""
        try:
            # Get relative path from hive-kube root
            rel_path = service_path.relative_to(self.hive_kube_path)
            parts = rel_path.parts

            if "kubernetes" in parts:
                idx = parts.index("kubernetes")
                if idx + 1 < len(parts):
                    return parts[idx + 1]

            return parts[0] if parts else "unknown"

        except ValueError:
            return service_path.parent.name

    def generate_openapi_spec_dynamically(self) -> Dict[str, Any]:
        """
        Generate comprehensive OpenAPI spec using dynamic logic.

        Key features:
        - Merges with existing spec intelligently
        - Adapts to discovered service patterns
        - Handles conflicts gracefully
        """
        logger.info("🔧 Generating OpenAPI specification dynamically...")

        # Start with base spec structure
        spec = {
            "openapi": "3.1.0",
            "info": {
                "title": "HoneyHive Comprehensive API",
                "version": "1.0.0",
                "description": "Complete HoneyHive platform API covering all services",
            },
            "servers": [
                {"url": "https://api.honeyhive.ai", "description": "Production server"}
            ],
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                    }
                },
            },
            "security": [{"BearerAuth": []}],
        }

        # Merge existing OpenAPI spec if available
        if self.existing_openapi_path and self.existing_openapi_path.exists():
            existing_spec = self._load_existing_spec()
            if existing_spec:
                spec = self._merge_specs_dynamically(spec, existing_spec)

        # Add discovered services dynamically
        for service_name, service in self.services.items():
            self._add_service_to_spec_dynamically(spec, service)

        # Dynamic validation and cleanup
        spec = self._validate_and_cleanup_spec(spec)

        logger.info(f"✅ Generated OpenAPI spec with {len(spec['paths'])} paths")
        return spec

    def _load_existing_spec(self) -> Optional[Dict]:
        """Load existing OpenAPI spec with error handling."""
        try:
            with open(self.existing_openapi_path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"⚠️  Could not load existing spec: {e}")
            return None

    def _merge_specs_dynamically(self, new_spec: Dict, existing_spec: Dict) -> Dict:
        """Dynamically merge specifications with conflict resolution."""
        logger.info("🔄 Merging with existing OpenAPI specification...")

        # Preserve existing info if more detailed
        if existing_spec.get("info", {}).get("description"):
            new_spec["info"]["description"] = existing_spec["info"]["description"]

        # Merge paths intelligently
        existing_paths = existing_spec.get("paths", {})
        for path, path_spec in existing_paths.items():
            if path not in new_spec["paths"]:
                new_spec["paths"][path] = path_spec
                logger.debug(f"Preserved existing path: {path}")
            else:
                # Merge methods
                for method, method_spec in path_spec.items():
                    if method not in new_spec["paths"][path]:
                        new_spec["paths"][path][method] = method_spec
                        logger.debug(
                            f"Preserved existing method: {method.upper()} {path}"
                        )

        # Merge schemas
        existing_schemas = existing_spec.get("components", {}).get("schemas", {})
        for schema_name, schema_spec in existing_schemas.items():
            if schema_name not in new_spec["components"]["schemas"]:
                new_spec["components"]["schemas"][schema_name] = schema_spec

        return new_spec

    def _add_service_to_spec_dynamically(self, spec: Dict, service: ServiceInfo):
        """Dynamically add service endpoints to OpenAPI spec."""
        logger.debug(f"Adding service {service.name} to spec...")

        for endpoint in service.endpoints:
            # Skip low-confidence endpoints
            if endpoint.confidence_score < self.confidence_threshold:
                continue

            path = endpoint.path
            method = endpoint.method.lower()

            # Ensure path exists in spec
            if path not in spec["paths"]:
                spec["paths"][path] = {}

            # Skip if method already exists (preserve existing)
            if method in spec["paths"][path]:
                continue

            # Create method specification
            method_spec = {
                "summary": endpoint.summary or f"{endpoint.method} {path}",
                "operationId": f"{method}{self._path_to_operation_id(path)}",
                "tags": endpoint.tags or [service.name.replace("_", " ").title()],
                "responses": {
                    "200": {
                        "description": "Success",
                        "content": {"application/json": {"schema": {"type": "object"}}},
                    }
                },
            }

            # Add parameters for path variables
            if "{" in path:
                method_spec["parameters"] = self._generate_path_parameters(path)

            # Add request body for POST/PUT
            if method in ["post", "put"]:
                method_spec["requestBody"] = {
                    "required": True,
                    "content": {"application/json": {"schema": {"type": "object"}}},
                }

            spec["paths"][path][method] = method_spec

        # Add service schemas
        for schema_name, schema_spec in service.schemas.items():
            full_schema_name = f"{service.name.title()}{schema_name}"
            if full_schema_name not in spec["components"]["schemas"]:
                spec["components"]["schemas"][full_schema_name] = schema_spec

    def _path_to_operation_id(self, path: str) -> str:
        """Convert path to operation ID."""
        # Remove parameters and convert to camelCase
        clean_path = re.sub(r"\{[^}]+\}", "", path)
        parts = [part.capitalize() for part in clean_path.split("/") if part]
        return "".join(parts) if parts else "Root"

    def _generate_path_parameters(self, path: str) -> List[Dict]:
        """Generate path parameters from path variables."""
        parameters = []
        path_vars = re.findall(r"\{(\w+)\}", path)

        for var in path_vars:
            parameters.append(
                {
                    "name": var,
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                    "description": f'{var.replace("_", " ").title()} identifier',
                }
            )

        return parameters

    def _validate_and_cleanup_spec(self, spec: Dict) -> Dict:
        """Validate and cleanup the generated spec."""
        logger.info("🔍 Validating and cleaning up OpenAPI spec...")

        # Remove empty paths
        empty_paths = [path for path, methods in spec["paths"].items() if not methods]
        for path in empty_paths:
            del spec["paths"][path]

        # Ensure all operation IDs are unique
        operation_ids = set()
        for path, methods in spec["paths"].items():
            for method, method_spec in methods.items():
                op_id = method_spec.get("operationId")
                if op_id in operation_ids:
                    # Make unique
                    counter = 1
                    new_op_id = f"{op_id}{counter}"
                    while new_op_id in operation_ids:
                        counter += 1
                        new_op_id = f"{op_id}{counter}"
                    method_spec["operationId"] = new_op_id
                    op_id = new_op_id

                operation_ids.add(op_id)

        return spec

    def save_openapi_spec(self, spec: Dict, output_path: str) -> bool:
        """Save OpenAPI spec to file."""
        try:
            with open(output_path, "w") as f:
                yaml.dump(spec, f, default_flow_style=False, sort_keys=False)

            logger.info(f"✅ OpenAPI spec saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Error saving OpenAPI spec: {e}")
            return False

    def generate_processing_report(self) -> Dict:
        """Generate dynamic processing report."""
        return {
            "services_discovered": len(self.services),
            "total_endpoints": sum(len(s.endpoints) for s in self.services.values()),
            "high_confidence_endpoints": sum(
                len(
                    [
                        ep
                        for ep in s.endpoints
                        if ep.confidence_score >= self.confidence_threshold
                    ]
                )
                for s in self.services.values()
            ),
            "processing_stats": self.processing_stats,
            "service_breakdown": {
                name: {
                    "endpoint_count": len(service.endpoints),
                    "schema_count": len(service.schemas),
                    "avg_confidence": (
                        sum(ep.confidence_score for ep in service.endpoints)
                        / len(service.endpoints)
                        if service.endpoints
                        else 0
                    ),
                }
                for name, service in self.services.items()
            },
        }


def main():
    """Main execution with dynamic processing."""
    import time

    start_time = time.time()

    logger.info("🚀 Dynamic OpenAPI Generator")
    logger.info("=" * 50)

    # Initialize generator
    generator = DynamicOpenAPIGenerator(
        hive_kube_path="../hive-kube", existing_openapi_path="openapi.yaml"
    )

    # Dynamic service discovery
    services = generator.discover_services_dynamically()

    if not services:
        logger.error("❌ No services discovered")
        return 1

    # Generate comprehensive OpenAPI spec
    spec = generator.generate_openapi_spec_dynamically()

    # Save spec
    output_path = "openapi_comprehensive_dynamic.yaml"
    if not generator.save_openapi_spec(spec, output_path):
        return 1

    # Generate report
    report = generator.generate_processing_report()

    with open("dynamic_generation_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    elapsed_time = time.time() - start_time
    logger.info(f"\n🎉 Dynamic OpenAPI Generation Complete!")
    logger.info(f"⏱️  Processing time: {elapsed_time:.2f}s")
    logger.info(f"📊 Services: {report['services_discovered']}")
    logger.info(f"📊 Endpoints: {report['total_endpoints']}")
    logger.info(f"📊 High-confidence endpoints: {report['high_confidence_endpoints']}")
    logger.info(f"📊 Files processed: {report['processing_stats']['files_processed']}")
    logger.info(f"📊 Errors handled: {report['processing_stats']['errors_handled']}")

    logger.info(f"\n💾 Files Generated:")
    logger.info(f"  • {output_path} - Comprehensive OpenAPI specification")
    logger.info(f"  • dynamic_generation_report.json - Processing report")

    return 0


if __name__ == "__main__":
    exit(main())
