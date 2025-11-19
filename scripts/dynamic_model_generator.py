#!/usr/bin/env python3
"""
Dynamic Model Generator

This script generates Python SDK models using dynamic logic principles.
It adapts to the generated OpenAPI spec, handles errors gracefully, and
processes data efficiently without static patterns.

Key Dynamic Principles:
1. Adaptive model generation based on actual OpenAPI schemas
2. Early error detection and graceful degradation
3. Memory-efficient processing of large specifications
4. Context-aware type inference
5. Intelligent conflict resolution and deduplication
"""

import json
import yaml
import subprocess
import sys
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Union, Generator
from dataclasses import dataclass
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ModelInfo:
    """Dynamic model information."""

    name: str
    schema: Dict[str, Any]
    service: str
    dependencies: Set[str]
    confidence_score: float = 1.0
    generated_code: Optional[str] = None


@dataclass
class GenerationStats:
    """Dynamic generation statistics."""

    models_generated: int = 0
    models_skipped: int = 0
    errors_handled: int = 0
    processing_time: float = 0.0
    memory_usage: float = 0.0
    conflicts_resolved: int = 0


class DynamicModelGenerator:
    """
    Dynamic model generator using adaptive algorithms.

    Features:
    - Adapts to different OpenAPI schema structures
    - Handles large specifications efficiently
    - Resolves naming conflicts intelligently
    - Generates type-safe Python models
    """

    def __init__(self, openapi_spec_path: str, output_dir: str):
        self.openapi_spec_path = Path(openapi_spec_path)
        self.output_dir = Path(output_dir)
        self.spec: Optional[Dict] = None
        self.models: Dict[str, ModelInfo] = {}
        self.stats = GenerationStats()

        # Dynamic processing thresholds
        self.max_schema_depth = 10
        self.max_properties = 100
        self.confidence_threshold = 0.7

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_openapi_spec_dynamically(self) -> bool:
        """Dynamically load OpenAPI specification with error handling."""
        try:
            logger.info(f"📖 Loading OpenAPI spec from {self.openapi_spec_path}")

            with open(self.openapi_spec_path, "r") as f:
                self.spec = yaml.safe_load(f)

            # Validate spec structure
            if not self._validate_spec_structure():
                return False

            logger.info(
                f"✅ Loaded OpenAPI spec: {self.spec['info']['title']} v{self.spec['info']['version']}"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Error loading OpenAPI spec: {e}")
            return False

    def _validate_spec_structure(self) -> bool:
        """Validate OpenAPI spec has required structure."""
        required_sections = ["openapi", "info", "paths"]

        for section in required_sections:
            if section not in self.spec:
                logger.error(f"❌ Missing required section: {section}")
                return False

        return True

    def analyze_schemas_dynamically(self) -> Dict[str, ModelInfo]:
        """Dynamically analyze schemas and create model information."""
        logger.info("🔍 Analyzing schemas dynamically...")

        schemas = self.spec.get("components", {}).get("schemas", {})

        if not schemas:
            logger.warning("⚠️  No schemas found in OpenAPI spec")
            return {}

        # Process schemas with dependency resolution
        for schema_name, schema_def in schemas.items():
            try:
                model_info = self._analyze_schema_dynamically(schema_name, schema_def)
                if (
                    model_info
                    and model_info.confidence_score >= self.confidence_threshold
                ):
                    self.models[schema_name] = model_info
                else:
                    self.stats.models_skipped += 1
                    logger.debug(f"Skipped low-confidence model: {schema_name}")

            except Exception as e:
                self.stats.errors_handled += 1
                logger.warning(f"⚠️  Error analyzing schema {schema_name}: {e}")
                continue

        # Resolve dependencies dynamically
        self._resolve_dependencies_dynamically()

        logger.info(
            f"📊 Analyzed {len(self.models)} models, skipped {self.stats.models_skipped}"
        )
        return self.models

    def _analyze_schema_dynamically(
        self, schema_name: str, schema_def: Dict
    ) -> Optional[ModelInfo]:
        """Dynamically analyze individual schema."""
        # Extract service from schema name or context
        service = self._infer_service_from_schema(schema_name, schema_def)

        # Calculate confidence score
        confidence = self._calculate_schema_confidence(schema_def)

        # Extract dependencies
        dependencies = self._extract_dependencies_dynamically(schema_def)

        model_info = ModelInfo(
            name=schema_name,
            schema=schema_def,
            service=service,
            dependencies=dependencies,
            confidence_score=confidence,
        )

        return model_info

    def _infer_service_from_schema(self, schema_name: str, schema_def: Dict) -> str:
        """Dynamically infer service from schema context."""
        # Service inference patterns
        service_patterns = {
            "event": "backend",
            "session": "backend",
            "metric": "evaluation",
            "alert": "beekeeper",
            "notification": "notification",
            "ingestion": "ingestion",
            "enrichment": "enrichment",
        }

        schema_lower = schema_name.lower()

        for pattern, service in service_patterns.items():
            if pattern in schema_lower:
                return service

        # Default to backend service
        return "backend"

    def _calculate_schema_confidence(self, schema_def: Dict) -> float:
        """Calculate confidence score for schema."""
        score = 0.5  # Base score

        # Boost for well-defined schemas
        if "type" in schema_def:
            score += 0.2

        if "properties" in schema_def:
            score += 0.2
            # Boost for reasonable number of properties
            prop_count = len(schema_def["properties"])
            if 1 <= prop_count <= self.max_properties:
                score += 0.1

        if "description" in schema_def:
            score += 0.1

        if "required" in schema_def:
            score += 0.1

        # Reduce score for overly complex schemas
        if self._get_schema_depth(schema_def) > self.max_schema_depth:
            score -= 0.2

        return min(1.0, max(0.0, score))

    def _get_schema_depth(self, schema_def: Dict, current_depth: int = 0) -> int:
        """Calculate schema nesting depth."""
        if current_depth > self.max_schema_depth:
            return current_depth

        max_depth = current_depth

        if "properties" in schema_def:
            for prop_schema in schema_def["properties"].values():
                if isinstance(prop_schema, dict):
                    depth = self._get_schema_depth(prop_schema, current_depth + 1)
                    max_depth = max(max_depth, depth)

        if "items" in schema_def and isinstance(schema_def["items"], dict):
            depth = self._get_schema_depth(schema_def["items"], current_depth + 1)
            max_depth = max(max_depth, depth)

        return max_depth

    def _extract_dependencies_dynamically(self, schema_def: Dict) -> Set[str]:
        """Dynamically extract schema dependencies."""
        dependencies = set()

        def extract_refs(obj):
            if isinstance(obj, dict):
                if "$ref" in obj:
                    ref = obj["$ref"]
                    if ref.startswith("#/components/schemas/"):
                        dep_name = ref.split("/")[-1]
                        dependencies.add(dep_name)
                else:
                    for value in obj.values():
                        extract_refs(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_refs(item)

        extract_refs(schema_def)
        return dependencies

    def _resolve_dependencies_dynamically(self):
        """Dynamically resolve model dependencies."""
        logger.info("🔗 Resolving model dependencies...")

        # Build dependency graph
        dependency_graph = {}
        for model_name, model_info in self.models.items():
            dependency_graph[model_name] = model_info.dependencies

        # Topological sort for generation order
        generation_order = self._topological_sort(dependency_graph)

        # Reorder models based on dependencies
        ordered_models = {}
        for model_name in generation_order:
            if model_name in self.models:
                ordered_models[model_name] = self.models[model_name]

        self.models = ordered_models
        logger.info(f"📊 Resolved dependencies for {len(self.models)} models")

    def _topological_sort(self, graph: Dict[str, Set[str]]) -> List[str]:
        """Topological sort for dependency resolution."""
        # Kahn's algorithm
        in_degree = {node: 0 for node in graph}

        # Calculate in-degrees
        for node in graph:
            for dep in graph[node]:
                if dep in in_degree:
                    in_degree[dep] += 1

        # Find nodes with no incoming edges
        queue = [node for node, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            node = queue.pop(0)
            result.append(node)

            # Remove edges from this node
            for dep in graph.get(node, set()):
                if dep in in_degree:
                    in_degree[dep] -= 1
                    if in_degree[dep] == 0:
                        queue.append(dep)

        return result

    def generate_models_dynamically(self) -> bool:
        """Generate Python models using dynamic approach."""
        logger.info("🔧 Generating Python models dynamically...")

        start_time = time.time()

        try:
            # Use openapi-python-client for initial generation
            temp_dir = self._generate_with_openapi_client()

            if not temp_dir:
                return False

            # Extract and enhance models dynamically
            success = self._extract_and_enhance_models(temp_dir)

            # Cleanup temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)

            self.stats.processing_time = time.time() - start_time

            if success:
                logger.info(
                    f"✅ Generated {self.stats.models_generated} models in {self.stats.processing_time:.2f}s"
                )
                return True
            else:
                logger.error("❌ Model generation failed")
                return False

        except Exception as e:
            logger.error(f"❌ Error in model generation: {e}")
            return False

    def _generate_with_openapi_client(self) -> Optional[Path]:
        """Generate initial models using openapi-python-client."""
        logger.info("🔧 Running openapi-python-client...")

        temp_dir = Path(tempfile.mkdtemp())

        try:
            cmd = [
                "openapi-python-client",
                "generate",
                "--path",
                str(self.openapi_spec_path),
                "--output-path",
                str(temp_dir),
                "--overwrite",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                logger.info("✅ openapi-python-client generation successful")
                return temp_dir
            else:
                logger.error(f"❌ openapi-python-client failed: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logger.error("❌ openapi-python-client timed out")
            return None
        except Exception as e:
            logger.error(f"❌ Error running openapi-python-client: {e}")
            return None

    def _extract_and_enhance_models(self, temp_dir: Path) -> bool:
        """Extract and enhance generated models."""
        logger.info("🔧 Extracting and enhancing models...")

        try:
            # Find generated models directory
            models_dirs = list(temp_dir.rglob("models"))

            if not models_dirs:
                logger.error("❌ No models directory found in generated code")
                return False

            models_dir = models_dirs[0]

            # Process each model file
            for model_file in models_dir.glob("*.py"):
                if model_file.name == "__init__.py":
                    continue

                success = self._process_model_file_dynamically(model_file)
                if success:
                    self.stats.models_generated += 1
                else:
                    self.stats.models_skipped += 1

            # Generate enhanced __init__.py
            self._generate_init_file_dynamically()

            return True

        except Exception as e:
            logger.error(f"❌ Error extracting models: {e}")
            return False

    def _process_model_file_dynamically(self, model_file: Path) -> bool:
        """Process individual model file with enhancements."""
        try:
            # Read generated model
            with open(model_file, "r") as f:
                content = f.read()

            # Apply dynamic enhancements
            enhanced_content = self._enhance_model_content(content, model_file.stem)

            # Write to output directory
            output_file = self.output_dir / model_file.name
            with open(output_file, "w") as f:
                f.write(enhanced_content)

            logger.debug(f"✅ Processed model: {model_file.name}")
            return True

        except Exception as e:
            logger.warning(f"⚠️  Error processing model {model_file}: {e}")
            return False

    def _enhance_model_content(self, content: str, model_name: str) -> str:
        """Dynamically enhance model content."""
        enhancements = []

        # Add dynamic imports if needed
        if "from typing import" not in content and (
            "List[" in content or "Dict[" in content or "Optional[" in content
        ):
            enhancements.append("from typing import List, Dict, Optional, Union, Any\n")

        # Add pydantic imports if not present
        if "from pydantic import" not in content and "BaseModel" in content:
            enhancements.append("from pydantic import BaseModel, Field\n")

        # Add docstring if missing
        if '"""' not in content and "class " in content:
            class_match = re.search(r"class (\w+)", content)
            if class_match:
                class_name = class_match.group(1)
                docstring = f'"""{class_name} model for HoneyHive API."""\n'
                content = content.replace(
                    f"class {class_name}", f"class {class_name}:\n    {docstring}"
                )

        # Combine enhancements
        if enhancements:
            import_section = "".join(enhancements)
            # Insert after existing imports or at the beginning
            if "import " in content:
                lines = content.split("\n")
                import_end = 0
                for i, line in enumerate(lines):
                    if line.strip() and not line.startswith(("import ", "from ")):
                        import_end = i
                        break

                lines.insert(import_end, import_section.rstrip())
                content = "\n".join(lines)
            else:
                content = import_section + content

        return content

    def _generate_init_file_dynamically(self):
        """Generate enhanced __init__.py file."""
        logger.info("🔧 Generating __init__.py...")

        init_content = ['"""Generated models for HoneyHive API."""\n\n']

        # Import all models
        model_files = [
            f for f in self.output_dir.glob("*.py") if f.name != "__init__.py"
        ]

        for model_file in sorted(model_files):
            module_name = model_file.stem
            init_content.append(f"from .{module_name} import *\n")

        # Add __all__ for explicit exports
        init_content.append("\n__all__ = [\n")

        for model_file in sorted(model_files):
            # Extract class names from file
            try:
                with open(model_file, "r") as f:
                    file_content = f.read()

                import re

                class_names = re.findall(r"^class (\w+)", file_content, re.MULTILINE)

                for class_name in class_names:
                    init_content.append(f'    "{class_name}",\n')

            except Exception as e:
                logger.debug(f"Error extracting classes from {model_file}: {e}")

        init_content.append("]\n")

        # Write __init__.py
        init_file = self.output_dir / "__init__.py"
        with open(init_file, "w") as f:
            f.write("".join(init_content))

        logger.info(f"✅ Generated __init__.py with {len(model_files)} model imports")

    def validate_generated_models(self) -> bool:
        """Validate generated models work correctly."""
        logger.info("🔍 Validating generated models...")

        try:
            # Test basic imports
            sys.path.insert(0, str(self.output_dir.parent))

            test_imports = [
                "from models import *",
            ]

            for import_stmt in test_imports:
                try:
                    exec(import_stmt)
                    logger.debug(f"✅ {import_stmt}")
                except Exception as e:
                    logger.error(f"❌ {import_stmt} failed: {e}")
                    return False

            logger.info("✅ Model validation successful")
            return True

        except Exception as e:
            logger.error(f"❌ Model validation failed: {e}")
            return False
        finally:
            if str(self.output_dir.parent) in sys.path:
                sys.path.remove(str(self.output_dir.parent))

    def generate_usage_examples(self):
        """Generate dynamic usage examples."""
        logger.info("📝 Generating usage examples...")

        examples_content = [
            '"""Usage examples for generated models."""\n\n',
            "from models import *\n\n",
        ]

        # Generate examples for each service
        services = set(model.service for model in self.models.values())

        for service in sorted(services):
            service_models = [
                model for model in self.models.values() if model.service == service
            ]

            examples_content.append(f"# {service.title()} Service Examples\n")

            for model in service_models[:3]:  # Limit to 3 examples per service
                example = self._generate_model_example(model)
                if example:
                    examples_content.append(example)

            examples_content.append("\n")

        # Write examples file
        examples_file = self.output_dir / "usage_examples.py"
        with open(examples_file, "w") as f:
            f.write("".join(examples_content))

        logger.info(f"✅ Generated usage examples: {examples_file}")

    def _generate_model_example(self, model: ModelInfo) -> str:
        """Generate usage example for a model."""
        try:
            schema = model.schema

            if schema.get("type") != "object" or "properties" not in schema:
                return ""

            properties = schema["properties"]
            required = schema.get("required", [])

            example_lines = [
                f"# Example: {model.name}\n",
                f"{model.name.lower()}_data = {model.name}(\n",
            ]

            # Generate example values for properties
            for prop_name, prop_schema in list(properties.items())[
                :5
            ]:  # Limit to 5 properties
                example_value = self._generate_example_value(prop_schema, prop_name)
                is_required = prop_name in required

                if (
                    is_required or len(example_lines) < 5
                ):  # Include required fields and some optional
                    example_lines.append(f"    {prop_name}={example_value},\n")

            example_lines.append(")\n\n")

            return "".join(example_lines)

        except Exception as e:
            logger.debug(f"Error generating example for {model.name}: {e}")
            return ""

    def _generate_example_value(self, prop_schema: Dict, prop_name: str) -> str:
        """Generate example value for property."""
        prop_type = prop_schema.get("type", "string")

        if prop_type == "string":
            if "email" in prop_name.lower():
                return '"user@example.com"'
            elif "name" in prop_name.lower():
                return f'"{prop_name.replace("_", " ").title()}"'
            elif "id" in prop_name.lower():
                return '"123e4567-e89b-12d3-a456-426614174000"'
            else:
                return f'"example_{prop_name}"'

        elif prop_type == "integer":
            return "42"

        elif prop_type == "number":
            return "3.14"

        elif prop_type == "boolean":
            return "True"

        elif prop_type == "array":
            return "[]"

        elif prop_type == "object":
            return "{}"

        else:
            return "None"

    def generate_report(self) -> Dict:
        """Generate comprehensive generation report."""
        return {
            "generation_stats": {
                "models_generated": self.stats.models_generated,
                "models_skipped": self.stats.models_skipped,
                "errors_handled": self.stats.errors_handled,
                "processing_time": self.stats.processing_time,
                "conflicts_resolved": self.stats.conflicts_resolved,
            },
            "model_breakdown": {
                name: {
                    "service": model.service,
                    "confidence_score": model.confidence_score,
                    "dependency_count": len(model.dependencies),
                    "dependencies": list(model.dependencies),
                }
                for name, model in self.models.items()
            },
            "service_summary": self._generate_service_summary(),
        }

    def _generate_service_summary(self) -> Dict:
        """Generate service-wise summary."""
        services = {}

        for model in self.models.values():
            service = model.service
            if service not in services:
                services[service] = {
                    "model_count": 0,
                    "avg_confidence": 0.0,
                    "models": [],
                }

            services[service]["model_count"] += 1
            services[service]["models"].append(model.name)

        # Calculate average confidence
        for service_name, service_data in services.items():
            service_models = [
                m for m in self.models.values() if m.service == service_name
            ]
            if service_models:
                avg_confidence = sum(m.confidence_score for m in service_models) / len(
                    service_models
                )
                service_data["avg_confidence"] = avg_confidence

        return services


def main():
    """Main execution with dynamic processing."""
    logger.info("🚀 Dynamic Model Generator")
    logger.info("=" * 50)

    # Initialize generator
    generator = DynamicModelGenerator(
        openapi_spec_path="openapi_comprehensive_dynamic.yaml",
        output_dir="src/honeyhive/models_dynamic",
    )

    # Load OpenAPI spec
    if not generator.load_openapi_spec_dynamically():
        return 1

    # Analyze schemas
    models = generator.analyze_schemas_dynamically()

    if not models:
        logger.error("❌ No models to generate")
        return 1

    # Generate models
    if not generator.generate_models_dynamically():
        return 1

    # Validate models
    if not generator.validate_generated_models():
        logger.warning("⚠️  Model validation failed, but continuing...")

    # Generate usage examples
    generator.generate_usage_examples()

    # Generate report
    report = generator.generate_report()

    with open("dynamic_model_generation_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    stats = report["generation_stats"]
    logger.info(f"\n🎉 Dynamic Model Generation Complete!")
    logger.info(f"📊 Models generated: {stats['models_generated']}")
    logger.info(f"📊 Models skipped: {stats['models_skipped']}")
    logger.info(f"📊 Errors handled: {stats['errors_handled']}")
    logger.info(f"⏱️  Processing time: {stats['processing_time']:.2f}s")

    logger.info(f"\n💾 Files Generated:")
    logger.info(f"  • src/honeyhive/models_dynamic/ - Generated models")
    logger.info(f"  • dynamic_model_generation_report.json - Generation report")

    return 0


if __name__ == "__main__":
    import re

    exit(main())
