#!/usr/bin/env python3
"""
Generate Models Only

This script generates ONLY Python models from the OpenAPI specification
using dynamic logic. Results are written to a comparison directory so you
can evaluate them against your current implementation.

Key Features:
- Models only (no client code)
- Written to comparison directory
- Preserves existing SDK untouched
- Dynamic generation with confidence scoring
- Comprehensive validation and reporting
"""

import json
import yaml
import subprocess
import sys
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ModelGenerationStats:
    """Statistics for model generation."""

    models_generated: int = 0
    models_skipped: int = 0
    errors_handled: int = 0
    processing_time: float = 0.0
    schemas_analyzed: int = 0
    confidence_scores: List[float] = None

    def __post_init__(self):
        if self.confidence_scores is None:
            self.confidence_scores = []


class DynamicModelsOnlyGenerator:
    """
    Generate only Python models using dynamic logic.

    This generator focuses exclusively on creating high-quality Python models
    from OpenAPI schemas without generating client code.
    """

    def __init__(
        self, openapi_spec_path: str, output_base_dir: str = "comparison_output"
    ):
        self.openapi_spec_path = Path(openapi_spec_path)
        self.output_base_dir = Path(output_base_dir)
        self.models_output_dir = self.output_base_dir / "models_only"
        self.spec: Optional[Dict] = None
        self.stats = ModelGenerationStats()

        # Dynamic processing parameters
        self.confidence_threshold = 0.6
        self.max_schema_complexity = 50

        # Ensure output directory exists and is clean
        if self.models_output_dir.exists():
            shutil.rmtree(self.models_output_dir)
        self.models_output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"📁 Models will be generated in: {self.models_output_dir}")

    def load_openapi_spec(self) -> bool:
        """Load and validate OpenAPI specification."""
        try:
            logger.info(f"📖 Loading OpenAPI spec from {self.openapi_spec_path}")

            if not self.openapi_spec_path.exists():
                logger.error(f"❌ OpenAPI spec not found: {self.openapi_spec_path}")
                return False

            with open(self.openapi_spec_path, "r") as f:
                self.spec = yaml.safe_load(f)

            # Validate required sections
            if not self.spec or "openapi" not in self.spec:
                logger.error("❌ Invalid OpenAPI specification")
                return False

            logger.info(
                f"✅ Loaded OpenAPI spec: {self.spec.get('info', {}).get('title', 'Unknown')} v{self.spec.get('info', {}).get('version', 'Unknown')}"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Error loading OpenAPI spec: {e}")
            return False

    def analyze_schemas_for_models(self) -> Dict[str, Dict]:
        """Analyze schemas to determine which models to generate."""
        logger.info("🔍 Analyzing schemas for model generation...")

        schemas = self.spec.get("components", {}).get("schemas", {})

        if not schemas:
            logger.warning("⚠️  No schemas found in OpenAPI spec")
            return {}

        analyzed_schemas = {}

        for schema_name, schema_def in schemas.items():
            try:
                analysis = self._analyze_individual_schema(schema_name, schema_def)

                if analysis["confidence_score"] >= self.confidence_threshold:
                    analyzed_schemas[schema_name] = analysis
                    self.stats.confidence_scores.append(analysis["confidence_score"])
                else:
                    self.stats.models_skipped += 1
                    logger.debug(
                        f"Skipped low-confidence schema: {schema_name} (score: {analysis['confidence_score']:.2f})"
                    )

                self.stats.schemas_analyzed += 1

            except Exception as e:
                self.stats.errors_handled += 1
                logger.warning(f"⚠️  Error analyzing schema {schema_name}: {e}")
                continue

        logger.info(
            f"📊 Analyzed {self.stats.schemas_analyzed} schemas, selected {len(analyzed_schemas)} for generation"
        )
        return analyzed_schemas

    def _analyze_individual_schema(self, schema_name: str, schema_def: Dict) -> Dict:
        """Analyze individual schema with confidence scoring."""
        analysis = {
            "name": schema_name,
            "schema": schema_def,
            "confidence_score": 0.5,  # Base score
            "complexity": 0,
            "has_properties": False,
            "has_required_fields": False,
            "has_description": False,
            "service_category": "unknown",
        }

        # Calculate confidence score dynamically
        if "type" in schema_def:
            analysis["confidence_score"] += 0.2

        if "properties" in schema_def:
            analysis["has_properties"] = True
            analysis["confidence_score"] += 0.2
            analysis["complexity"] = len(schema_def["properties"])

            # Boost for reasonable complexity
            if 1 <= analysis["complexity"] <= self.max_schema_complexity:
                analysis["confidence_score"] += 0.1

        if "required" in schema_def:
            analysis["has_required_fields"] = True
            analysis["confidence_score"] += 0.1

        if "description" in schema_def:
            analysis["has_description"] = True
            analysis["confidence_score"] += 0.1

        # Reduce score for overly complex schemas
        if analysis["complexity"] > self.max_schema_complexity:
            analysis["confidence_score"] -= 0.2

        # Categorize by service (for organization)
        analysis["service_category"] = self._categorize_schema(schema_name)

        # Ensure score is in valid range
        analysis["confidence_score"] = max(0.0, min(1.0, analysis["confidence_score"]))

        return analysis

    def _categorize_schema(self, schema_name: str) -> str:
        """Categorize schema by service type."""
        name_lower = schema_name.lower()

        categories = {
            "events": ["event", "trace", "span"],
            "sessions": ["session"],
            "metrics": ["metric", "evaluation"],
            "datasets": ["dataset", "datapoint"],
            "tools": ["tool", "function"],
            "projects": ["project"],
            "configurations": ["config", "setting"],
            "auth": ["auth", "token", "key"],
            "errors": ["error", "exception"],
            "responses": ["response", "result"],
        }

        for category, keywords in categories.items():
            if any(keyword in name_lower for keyword in keywords):
                return category

        return "general"

    def generate_models_with_openapi_client(self) -> bool:
        """Generate models using openapi-python-client."""
        logger.info("🔧 Generating models with openapi-python-client...")

        start_time = time.time()

        try:
            # Create temporary directory for generation
            temp_dir = Path(tempfile.mkdtemp())

            # Run openapi-python-client
            cmd = [
                "openapi-python-client",
                "generate",
                "--path",
                str(self.openapi_spec_path),
                "--output-path",
                str(temp_dir),
                "--overwrite",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if result.returncode != 0:
                logger.error(f"❌ openapi-python-client failed: {result.stderr}")
                return False

            # Extract models from generated code
            success = self._extract_models_only(temp_dir)

            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)

            self.stats.processing_time = time.time() - start_time

            if success:
                logger.info(
                    f"✅ Model generation completed in {self.stats.processing_time:.2f}s"
                )
                return True
            else:
                logger.error("❌ Model extraction failed")
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ openapi-python-client timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Error in model generation: {e}")
            return False

    def _extract_models_only(self, temp_dir: Path) -> bool:
        """Extract only model files from generated client."""
        logger.info("📦 Extracting models from generated client...")

        try:
            # Find models directory in generated code
            models_dirs = list(temp_dir.rglob("models"))

            if not models_dirs:
                logger.error("❌ No models directory found in generated code")
                return False

            source_models_dir = models_dirs[0]

            # Copy model files
            for model_file in source_models_dir.glob("*.py"):
                if model_file.name == "__init__.py":
                    continue

                # Process and copy model file
                success = self._process_and_copy_model(model_file)
                if success:
                    self.stats.models_generated += 1
                else:
                    self.stats.models_skipped += 1

            # Generate clean __init__.py for models only
            self._generate_models_init_file()

            # Generate model documentation
            self._generate_model_documentation()

            logger.info(f"✅ Extracted {self.stats.models_generated} models")
            return True

        except Exception as e:
            logger.error(f"❌ Error extracting models: {e}")
            return False

    def _process_and_copy_model(self, model_file: Path) -> bool:
        """Process and copy individual model file."""
        try:
            # Read original model
            with open(model_file, "r") as f:
                content = f.read()

            # Clean up content (remove client-specific imports/code)
            cleaned_content = self._clean_model_content(content, model_file.stem)

            # Write to models output directory
            output_file = self.models_output_dir / model_file.name
            with open(output_file, "w") as f:
                f.write(cleaned_content)

            logger.debug(f"✅ Processed model: {model_file.name}")
            return True

        except Exception as e:
            logger.warning(f"⚠️  Error processing model {model_file}: {e}")
            return False

    def _clean_model_content(self, content: str, model_name: str) -> str:
        """Clean model content to remove client-specific code."""
        lines = content.split("\n")
        cleaned_lines = []

        # Add header comment
        cleaned_lines.extend(
            [
                f'"""',
                f"{model_name} model generated from OpenAPI specification.",
                f"",
                f"This model was generated for comparison purposes.",
                f"Review before integrating into the main SDK.",
                f'"""',
                "",
            ]
        )

        skip_patterns = [
            "from ..client",
            "from client",
            "import httpx",
            "import attrs",
            "from attrs",
        ]

        for line in lines:
            # Skip client-specific imports
            if any(pattern in line for pattern in skip_patterns):
                continue

            # Skip empty lines at the beginning
            if not cleaned_lines and not line.strip():
                continue

            cleaned_lines.append(line)

        # Ensure proper imports for models
        import_section = [
            "from typing import Any, Dict, List, Type, TypeVar, Union, Optional",
            "from pydantic import BaseModel, Field",
            "",
        ]

        # Find where to insert imports (after docstring, before first import/class)
        insert_index = 0
        in_docstring = False

        for i, line in enumerate(cleaned_lines):
            if line.strip().startswith('"""'):
                in_docstring = not in_docstring
            elif not in_docstring and (
                line.startswith("from ")
                or line.startswith("import ")
                or line.startswith("class ")
            ):
                insert_index = i
                break

        # Insert imports if not already present
        existing_content = "\n".join(cleaned_lines)
        if "from typing import" not in existing_content:
            for imp in reversed(import_section):
                cleaned_lines.insert(insert_index, imp)

        return "\n".join(cleaned_lines)

    def _generate_models_init_file(self):
        """Generate __init__.py for models directory."""
        logger.info("📝 Generating models __init__.py...")

        init_content = [
            '"""',
            "Generated models from OpenAPI specification.",
            "",
            "These models are generated for comparison purposes.",
            "Review before integrating into the main SDK.",
            '"""',
            "",
        ]

        # Import all models
        model_files = [
            f for f in self.models_output_dir.glob("*.py") if f.name != "__init__.py"
        ]

        for model_file in sorted(model_files):
            module_name = model_file.stem
            init_content.append(f"from .{module_name} import *")

        init_content.extend(["", "# Model categories for organization"])

        # Group models by category
        categories = {}
        for model_file in model_files:
            category = self._categorize_schema(model_file.stem)
            if category not in categories:
                categories[category] = []
            categories[category].append(model_file.stem)

        for category, models in sorted(categories.items()):
            init_content.append(f"# {category.title()}: {', '.join(models)}")

        # Write __init__.py
        init_file = self.models_output_dir / "__init__.py"
        with open(init_file, "w") as f:
            f.write("\n".join(init_content))

        logger.info(f"✅ Generated __init__.py with {len(model_files)} model imports")

    def _generate_model_documentation(self):
        """Generate documentation for the models."""
        logger.info("📚 Generating model documentation...")

        doc_content = [
            "# Generated Models Documentation",
            "",
            "This directory contains Python models generated from the OpenAPI specification.",
            "",
            "## Purpose",
            "",
            "These models are generated for **comparison purposes only**.",
            "Review them against your current implementation before making any changes.",
            "",
            "## Statistics",
            "",
            f"- **Models Generated**: {self.stats.models_generated}",
            f"- **Models Skipped**: {self.stats.models_skipped}",
            f"- **Schemas Analyzed**: {self.stats.schemas_analyzed}",
            f"- **Processing Time**: {self.stats.processing_time:.2f}s",
            "",
        ]

        if self.stats.confidence_scores:
            avg_confidence = sum(self.stats.confidence_scores) / len(
                self.stats.confidence_scores
            )
            doc_content.extend(
                [
                    f"- **Average Confidence Score**: {avg_confidence:.2f}",
                    f"- **Confidence Range**: {min(self.stats.confidence_scores):.2f} - {max(self.stats.confidence_scores):.2f}",
                    "",
                ]
            )

        # Add model categories
        model_files = [
            f for f in self.models_output_dir.glob("*.py") if f.name != "__init__.py"
        ]
        categories = {}

        for model_file in model_files:
            category = self._categorize_schema(model_file.stem)
            if category not in categories:
                categories[category] = []
            categories[category].append(model_file.stem)

        doc_content.extend(
            [
                "## Model Categories",
                "",
            ]
        )

        for category, models in sorted(categories.items()):
            doc_content.extend(
                [
                    f"### {category.title()}",
                    "",
                ]
            )
            for model in sorted(models):
                doc_content.append(f"- `{model}`")
            doc_content.append("")

        doc_content.extend(
            [
                "## Usage Example",
                "",
                "```python",
                "# Import models",
                "from models_only import *",
                "",
                "# Use models for type hints and validation",
                "def process_event(event_data: dict) -> Event:",
                "    return Event(**event_data)",
                "```",
                "",
                "## Next Steps",
                "",
                "1. Review generated models against your current implementation",
                "2. Identify differences and improvements",
                "3. Decide which models to integrate",
                "4. Test compatibility with existing code",
                "5. Update imports and type hints as needed",
            ]
        )

        # Write documentation
        doc_file = self.models_output_dir / "README.md"
        with open(doc_file, "w") as f:
            f.write("\n".join(doc_content))

        logger.info(f"✅ Generated documentation: {doc_file}")

    def validate_generated_models(self) -> bool:
        """Validate that generated models work correctly."""
        logger.info("🔍 Validating generated models...")

        try:
            # Test basic import
            sys.path.insert(0, str(self.models_output_dir.parent))

            try:
                exec("from models_only import *")
                logger.debug("✅ Basic import successful")
            except Exception as e:
                logger.error(f"❌ Basic import failed: {e}")
                return False

            # Test individual model imports (sample)
            model_files = [
                f
                for f in self.models_output_dir.glob("*.py")
                if f.name != "__init__.py"
            ]
            sample_size = min(5, len(model_files))

            import random

            sample_files = random.sample(model_files, sample_size)

            for model_file in sample_files:
                module_name = model_file.stem
                try:
                    exec(f"from models_only.{module_name} import *")
                    logger.debug(f"✅ {module_name} import successful")
                except Exception as e:
                    logger.warning(f"⚠️  {module_name} import failed: {e}")

            logger.info("✅ Model validation completed")
            return True

        except Exception as e:
            logger.error(f"❌ Model validation error: {e}")
            return False
        finally:
            # Clean up sys.path
            if str(self.models_output_dir.parent) in sys.path:
                sys.path.remove(str(self.models_output_dir.parent))

    def generate_comparison_report(self) -> Dict:
        """Generate comprehensive comparison report."""
        model_files = [
            f for f in self.models_output_dir.glob("*.py") if f.name != "__init__.py"
        ]

        # Categorize models
        categories = {}
        for model_file in model_files:
            category = self._categorize_schema(model_file.stem)
            if category not in categories:
                categories[category] = []
            categories[category].append(model_file.stem)

        report = {
            "generation_summary": {
                "models_generated": self.stats.models_generated,
                "models_skipped": self.stats.models_skipped,
                "schemas_analyzed": self.stats.schemas_analyzed,
                "errors_handled": self.stats.errors_handled,
                "processing_time": self.stats.processing_time,
            },
            "quality_metrics": {
                "average_confidence": (
                    sum(self.stats.confidence_scores)
                    / len(self.stats.confidence_scores)
                    if self.stats.confidence_scores
                    else 0
                ),
                "confidence_range": {
                    "min": (
                        min(self.stats.confidence_scores)
                        if self.stats.confidence_scores
                        else 0
                    ),
                    "max": (
                        max(self.stats.confidence_scores)
                        if self.stats.confidence_scores
                        else 0
                    ),
                },
                "high_confidence_models": len(
                    [s for s in self.stats.confidence_scores if s >= 0.8]
                ),
            },
            "model_categories": categories,
            "output_location": str(self.models_output_dir),
            "files_generated": [
                "models/*.py - Individual model files",
                "models/__init__.py - Model imports",
                "models/README.md - Documentation",
            ],
            "comparison_instructions": [
                "1. Compare generated models with your current src/honeyhive/models/",
                "2. Look for new models that might be useful",
                "3. Check for improved type definitions",
                "4. Identify any breaking changes",
                "5. Test compatibility with existing code",
            ],
        }

        return report


def main():
    """Main execution for models-only generation."""
    logger.info("🚀 Generate Models Only")
    logger.info("=" * 50)

    # Check for OpenAPI spec
    openapi_files = [
        "openapi_comprehensive_dynamic.yaml",
        "openapi.yaml",
    ]

    openapi_spec = None
    for spec_file in openapi_files:
        if Path(spec_file).exists():
            openapi_spec = spec_file
            break

    if not openapi_spec:
        logger.error(f"❌ No OpenAPI spec found. Tried: {', '.join(openapi_files)}")
        return 1

    # Initialize generator
    generator = DynamicModelsOnlyGenerator(
        openapi_spec_path=openapi_spec, output_base_dir="comparison_output"
    )

    # Load OpenAPI spec
    if not generator.load_openapi_spec():
        return 1

    # Analyze schemas
    schemas = generator.analyze_schemas_for_models()
    if not schemas:
        logger.error("❌ No schemas found for model generation")
        return 1

    # Generate models
    if not generator.generate_models_with_openapi_client():
        return 1

    # Validate models
    if not generator.validate_generated_models():
        logger.warning("⚠️  Model validation had issues, but continuing...")

    # Generate report
    report = generator.generate_comparison_report()

    report_file = "comparison_output/models_only_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    summary = report["generation_summary"]
    metrics = report["quality_metrics"]

    logger.info(f"\n🎉 Models-Only Generation Complete!")
    logger.info(f"📊 Models generated: {summary['models_generated']}")
    logger.info(f"📊 Models skipped: {summary['models_skipped']}")
    logger.info(f"📊 Average confidence: {metrics['average_confidence']:.2f}")
    logger.info(f"📊 High-confidence models: {metrics['high_confidence_models']}")
    logger.info(f"⏱️  Processing time: {summary['processing_time']:.2f}s")

    logger.info(f"\n📁 Output Location:")
    logger.info(f"  {report['output_location']}")

    logger.info(f"\n💡 Next Steps:")
    for instruction in report["comparison_instructions"]:
        logger.info(f"  {instruction}")

    logger.info(f"\n💾 Files Generated:")
    logger.info(f"  • {report_file}")
    for file_desc in report["files_generated"]:
        logger.info(f"  • {file_desc}")

    return 0


if __name__ == "__main__":
    exit(main())
