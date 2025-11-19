#!/usr/bin/env python3
"""
Generate Models and Client

This script generates both Python models AND a complete client from the OpenAPI
specification using dynamic logic. Results are written to a comparison directory
so you can evaluate the full generated SDK against your current implementation.

Key Features:
- Complete SDK generation (models + client + API methods)
- Written to comparison directory
- Preserves existing SDK untouched
- Dynamic generation with intelligent organization
- Comprehensive validation and comparison tools
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
class ClientGenerationStats:
    """Statistics for client generation."""

    models_generated: int = 0
    api_methods_generated: int = 0
    client_classes_generated: int = 0
    errors_handled: int = 0
    processing_time: float = 0.0
    total_files_generated: int = 0
    services_discovered: int = 0


class DynamicModelsAndClientGenerator:
    """
    Generate complete Python SDK (models + client) using dynamic logic.

    This generator creates a full SDK including models, API client classes,
    and method implementations for comparison with your current SDK.
    """

    def __init__(
        self, openapi_spec_path: str, output_base_dir: str = "comparison_output"
    ):
        self.openapi_spec_path = Path(openapi_spec_path)
        self.output_base_dir = Path(output_base_dir)
        self.client_output_dir = self.output_base_dir / "full_sdk"
        self.spec: Optional[Dict] = None
        self.stats = ClientGenerationStats()

        # Ensure output directory exists and is clean
        if self.client_output_dir.exists():
            shutil.rmtree(self.client_output_dir)
        self.client_output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"📁 Full SDK will be generated in: {self.client_output_dir}")

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

    def analyze_spec_for_client_generation(self) -> Dict[str, Any]:
        """Analyze OpenAPI spec to plan client generation."""
        logger.info("🔍 Analyzing spec for client generation...")

        analysis = {
            "services": {},
            "total_endpoints": 0,
            "schemas_count": 0,
            "security_schemes": [],
            "servers": [],
        }

        # Analyze paths to identify services
        paths = self.spec.get("paths", {})
        service_endpoints = {}

        for path, path_spec in paths.items():
            # Extract service from path
            service = self._extract_service_from_path(path)

            if service not in service_endpoints:
                service_endpoints[service] = []

            # Count methods for this path
            methods = [
                method
                for method in path_spec.keys()
                if method.lower() in ["get", "post", "put", "delete", "patch"]
            ]
            service_endpoints[service].extend([(path, method) for method in methods])
            analysis["total_endpoints"] += len(methods)

        analysis["services"] = service_endpoints
        analysis["schemas_count"] = len(
            self.spec.get("components", {}).get("schemas", {})
        )
        analysis["security_schemes"] = list(
            self.spec.get("components", {}).get("securitySchemes", {}).keys()
        )
        analysis["servers"] = self.spec.get("servers", [])

        self.stats.services_discovered = len(service_endpoints)

        logger.info(f"📊 Analysis complete:")
        logger.info(f"  • Services: {len(service_endpoints)}")
        logger.info(f"  • Total endpoints: {analysis['total_endpoints']}")
        logger.info(f"  • Schemas: {analysis['schemas_count']}")

        return analysis

    def _extract_service_from_path(self, path: str) -> str:
        """Extract service name from API path."""
        # Remove leading slash and get first segment
        segments = path.strip("/").split("/")
        if not segments or segments[0] == "":
            return "core"

        # Map to service names
        service_mappings = {
            "events": "events",
            "sessions": "sessions",
            "session": "sessions",
            "metrics": "metrics",
            "tools": "tools",
            "datasets": "datasets",
            "datapoints": "datapoints",
            "projects": "projects",
            "configurations": "configurations",
            "runs": "experiments",
            "healthcheck": "health",
            "health": "health",
        }

        first_segment = segments[0].lower()
        return service_mappings.get(first_segment, first_segment)

    def generate_full_sdk_with_openapi_client(self) -> bool:
        """Generate complete SDK using openapi-python-client."""
        logger.info("🔧 Generating full SDK with openapi-python-client...")

        start_time = time.time()

        try:
            # Create temporary directory for generation
            temp_dir = Path(tempfile.mkdtemp())

            # Run openapi-python-client with full generation
            cmd = [
                "openapi-python-client",
                "generate",
                "--path",
                str(self.openapi_spec_path),
                "--output-path",
                str(temp_dir),
                "--overwrite",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

            if result.returncode != 0:
                logger.error(f"❌ openapi-python-client failed: {result.stderr}")
                return False

            # Process and organize generated SDK
            success = self._process_and_organize_sdk(temp_dir)

            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)

            self.stats.processing_time = time.time() - start_time

            if success:
                logger.info(
                    f"✅ Full SDK generation completed in {self.stats.processing_time:.2f}s"
                )
                return True
            else:
                logger.error("❌ SDK processing failed")
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ openapi-python-client timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Error in SDK generation: {e}")
            return False

    def _process_and_organize_sdk(self, temp_dir: Path) -> bool:
        """Process and organize the generated SDK."""
        logger.info("📦 Processing and organizing generated SDK...")

        try:
            # Find the generated client directory
            client_dirs = list(temp_dir.rglob("*client*"))
            if not client_dirs:
                # Look for any Python package directory
                client_dirs = [
                    d
                    for d in temp_dir.iterdir()
                    if d.is_dir() and not d.name.startswith(".")
                ]

            if not client_dirs:
                logger.error("❌ No generated client directory found")
                return False

            source_dir = client_dirs[0]

            # Create organized structure
            self._create_sdk_structure()

            # Process models
            models_success = self._process_models_section(source_dir)

            # Process API clients
            api_success = self._process_api_section(source_dir)

            # Process client classes
            client_success = self._process_client_section(source_dir)

            # Generate SDK documentation
            self._generate_sdk_documentation()

            # Generate comparison tools
            self._generate_comparison_tools()

            return models_success and api_success and client_success

        except Exception as e:
            logger.error(f"❌ Error processing SDK: {e}")
            return False

    def _create_sdk_structure(self):
        """Create organized SDK directory structure."""
        logger.info("📁 Creating SDK structure...")

        # Create main directories
        directories = [
            "honeyhive_generated",
            "honeyhive_generated/models",
            "honeyhive_generated/api",
            "honeyhive_generated/client",
            "honeyhive_generated/types",
            "docs",
            "examples",
            "tests",
        ]

        for directory in directories:
            (self.client_output_dir / directory).mkdir(parents=True, exist_ok=True)

        # Create __init__.py files
        init_files = [
            "honeyhive_generated/__init__.py",
            "honeyhive_generated/models/__init__.py",
            "honeyhive_generated/api/__init__.py",
            "honeyhive_generated/client/__init__.py",
            "honeyhive_generated/types/__init__.py",
        ]

        for init_file in init_files:
            init_path = self.client_output_dir / init_file
            with open(init_path, "w") as f:
                f.write(f'"""Generated SDK component: {init_file.split("/")[-2]}."""\n')

    def _process_models_section(self, source_dir: Path) -> bool:
        """Process and organize models."""
        logger.info("📝 Processing models section...")

        try:
            # Find models directory
            models_dirs = list(source_dir.rglob("models"))

            if not models_dirs:
                logger.warning("⚠️  No models directory found")
                return True  # Not critical

            source_models_dir = models_dirs[0]
            target_models_dir = self.client_output_dir / "honeyhive_generated/models"

            # Copy and process model files
            for model_file in source_models_dir.glob("*.py"):
                if model_file.name == "__init__.py":
                    continue

                # Process model file
                success = self._process_model_file(model_file, target_models_dir)
                if success:
                    self.stats.models_generated += 1

            # Generate models __init__.py
            self._generate_models_init(target_models_dir)

            logger.info(f"✅ Processed {self.stats.models_generated} models")
            return True

        except Exception as e:
            logger.error(f"❌ Error processing models: {e}")
            return False

    def _process_model_file(self, model_file: Path, target_dir: Path) -> bool:
        """Process individual model file."""
        try:
            with open(model_file, "r") as f:
                content = f.read()

            # Clean and enhance model content
            enhanced_content = self._enhance_model_for_comparison(
                content, model_file.stem
            )

            # Write to target directory
            target_file = target_dir / model_file.name
            with open(target_file, "w") as f:
                f.write(enhanced_content)

            return True

        except Exception as e:
            logger.debug(f"Error processing model {model_file}: {e}")
            return False

    def _enhance_model_for_comparison(self, content: str, model_name: str) -> str:
        """Enhance model content for better comparison."""
        lines = content.split("\n")
        enhanced_lines = []

        # Add comparison header
        enhanced_lines.extend(
            [
                f'"""',
                f"{model_name} - Generated Model for Comparison",
                f"",
                f"This model was generated from the OpenAPI specification.",
                f"Compare with your current implementation in src/honeyhive/models/",
                f"",
                f"Key areas to review:",
                f"- Field definitions and types",
                f"- Required vs optional fields",
                f"- Validation rules",
                f"- Default values",
                f"- Documentation/descriptions",
                f'"""',
                "",
            ]
        )

        # Process existing content
        skip_patterns = [
            "from ..client",
            "from client",
            "import httpx",
        ]

        for line in lines:
            # Skip client-specific imports
            if any(pattern in line for pattern in skip_patterns):
                continue

            enhanced_lines.append(line)

        # Ensure proper imports
        content_str = "\n".join(enhanced_lines)
        if "from typing import" not in content_str:
            import_index = (
                len(
                    [
                        l
                        for l in enhanced_lines
                        if l.startswith('"""') or l.strip() == ""
                    ]
                )
                + 1
            )
            enhanced_lines.insert(
                import_index, "from typing import Any, Dict, List, Optional, Union"
            )
            enhanced_lines.insert(
                import_index + 1, "from pydantic import BaseModel, Field"
            )
            enhanced_lines.insert(import_index + 2, "")

        return "\n".join(enhanced_lines)

    def _process_api_section(self, source_dir: Path) -> bool:
        """Process and organize API client methods."""
        logger.info("🔌 Processing API section...")

        try:
            # Find API directory
            api_dirs = list(source_dir.rglob("api"))

            if not api_dirs:
                logger.warning("⚠️  No API directory found")
                return True  # Not critical

            source_api_dir = api_dirs[0]
            target_api_dir = self.client_output_dir / "honeyhive_generated/api"

            # Process API files by service
            service_apis = {}

            for api_file in source_api_dir.glob("*.py"):
                if api_file.name == "__init__.py":
                    continue

                # Determine service from filename
                service = self._determine_service_from_filename(api_file.stem)

                if service not in service_apis:
                    service_apis[service] = []

                # Process API file
                success = self._process_api_file(api_file, target_api_dir, service)
                if success:
                    service_apis[service].append(api_file.stem)
                    self.stats.api_methods_generated += 1

            # Generate API __init__.py
            self._generate_api_init(target_api_dir, service_apis)

            logger.info(
                f"✅ Processed {self.stats.api_methods_generated} API methods across {len(service_apis)} services"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Error processing API section: {e}")
            return False

    def _determine_service_from_filename(self, filename: str) -> str:
        """Determine service from API filename."""
        filename_lower = filename.lower()

        service_patterns = {
            "events": ["event"],
            "sessions": ["session"],
            "metrics": ["metric"],
            "tools": ["tool"],
            "datasets": ["dataset"],
            "datapoints": ["datapoint"],
            "projects": ["project"],
            "configurations": ["config"],
            "experiments": ["run", "experiment"],
            "health": ["health"],
        }

        for service, patterns in service_patterns.items():
            if any(pattern in filename_lower for pattern in patterns):
                return service

        return "general"

    def _process_api_file(self, api_file: Path, target_dir: Path, service: str) -> bool:
        """Process individual API file."""
        try:
            with open(api_file, "r") as f:
                content = f.read()

            # Enhance API content for comparison
            enhanced_content = self._enhance_api_for_comparison(
                content, api_file.stem, service
            )

            # Write to service-specific file
            target_file = target_dir / f"{service}_{api_file.name}"
            with open(target_file, "w") as f:
                f.write(enhanced_content)

            return True

        except Exception as e:
            logger.debug(f"Error processing API file {api_file}: {e}")
            return False

    def _enhance_api_for_comparison(
        self, content: str, api_name: str, service: str
    ) -> str:
        """Enhance API content for better comparison."""
        lines = content.split("\n")
        enhanced_lines = []

        # Add comparison header
        enhanced_lines.extend(
            [
                f'"""',
                f"{api_name} - Generated API Client for {service.title()} Service",
                f"",
                f"This API client was generated from the OpenAPI specification.",
                f"Compare with your current implementation in src/honeyhive/api/",
                f"",
                f"Key areas to review:",
                f"- Method signatures and parameters",
                f"- Request/response handling",
                f"- Error handling patterns",
                f"- Authentication integration",
                f"- Type hints and documentation",
                f'"""',
                "",
            ]
        )

        # Process existing content
        for line in lines:
            enhanced_lines.append(line)

        return "\n".join(enhanced_lines)

    def _process_client_section(self, source_dir: Path) -> bool:
        """Process main client classes."""
        logger.info("🏗️  Processing client section...")

        try:
            # Find client files
            client_files = []

            # Look for main client files
            for pattern in ["client.py", "*client*.py", "main.py"]:
                client_files.extend(source_dir.rglob(pattern))

            if not client_files:
                logger.warning("⚠️  No client files found")
                return True  # Not critical

            target_client_dir = self.client_output_dir / "honeyhive_generated/client"

            for client_file in client_files:
                success = self._process_client_file(client_file, target_client_dir)
                if success:
                    self.stats.client_classes_generated += 1

            # Generate main client integration
            self._generate_main_client_integration(target_client_dir)

            logger.info(
                f"✅ Processed {self.stats.client_classes_generated} client classes"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Error processing client section: {e}")
            return False

    def _process_client_file(self, client_file: Path, target_dir: Path) -> bool:
        """Process individual client file."""
        try:
            with open(client_file, "r") as f:
                content = f.read()

            # Enhance client content
            enhanced_content = self._enhance_client_for_comparison(
                content, client_file.stem
            )

            # Write to target directory
            target_file = target_dir / client_file.name
            with open(target_file, "w") as f:
                f.write(enhanced_content)

            return True

        except Exception as e:
            logger.debug(f"Error processing client file {client_file}: {e}")
            return False

    def _enhance_client_for_comparison(self, content: str, client_name: str) -> str:
        """Enhance client content for comparison."""
        lines = content.split("\n")
        enhanced_lines = []

        # Add comparison header
        enhanced_lines.extend(
            [
                f'"""',
                f"{client_name} - Generated Client Class",
                f"",
                f"This client class was generated from the OpenAPI specification.",
                f"Compare with your current HoneyHive client implementation.",
                f"",
                f"Key areas to review:",
                f"- Client initialization and configuration",
                f"- Authentication handling",
                f"- Request/response processing",
                f"- Error handling and retries",
                f"- Service integration patterns",
                f'"""',
                "",
            ]
        )

        # Process existing content
        for line in lines:
            enhanced_lines.append(line)

        return "\n".join(enhanced_lines)

    def _generate_models_init(self, models_dir: Path):
        """Generate models __init__.py."""
        model_files = [f for f in models_dir.glob("*.py") if f.name != "__init__.py"]

        init_content = [
            '"""Generated models for comparison."""',
            "",
        ]

        for model_file in sorted(model_files):
            module_name = model_file.stem
            init_content.append(f"from .{module_name} import *")

        init_file = models_dir / "__init__.py"
        with open(init_file, "w") as f:
            f.write("\n".join(init_content))

    def _generate_api_init(self, api_dir: Path, service_apis: Dict[str, List[str]]):
        """Generate API __init__.py."""
        init_content = [
            '"""Generated API clients for comparison."""',
            "",
        ]

        for service, apis in sorted(service_apis.items()):
            init_content.append(f"# {service.title()} Service APIs")
            for api in apis:
                init_content.append(f"from .{service}_{api} import *")
            init_content.append("")

        init_file = api_dir / "__init__.py"
        with open(init_file, "w") as f:
            f.write("\n".join(init_content))

    def _generate_main_client_integration(self, client_dir: Path):
        """Generate main client integration file."""
        integration_content = [
            '"""',
            "Main Client Integration - Generated for Comparison",
            "",
            "This shows how the generated client could be integrated.",
            "Compare with your current HoneyHive client architecture.",
            '"""',
            "",
            "from typing import Optional",
            "",
            "# Import generated components",
            "from ..models import *",
            "from ..api import *",
            "",
            "class HoneyHiveGenerated:",
            '    """Generated HoneyHive client for comparison."""',
            "    ",
            '    def __init__(self, api_key: str, base_url: str = "https://api.honeyhive.ai"):',
            '        """Initialize the generated client."""',
            "        self.api_key = api_key",
            "        self.base_url = base_url",
            "        ",
            "        # Initialize service clients",
            "        # (This would be populated based on generated API clients)",
            "        pass",
            "    ",
            "    # Service properties would be added here based on generated APIs",
            "",
        ]

        integration_file = client_dir / "integration_example.py"
        with open(integration_file, "w") as f:
            f.write("\n".join(integration_content))

    def _generate_sdk_documentation(self):
        """Generate comprehensive SDK documentation."""
        logger.info("📚 Generating SDK documentation...")

        doc_content = [
            "# Generated SDK Documentation",
            "",
            "This directory contains a complete SDK generated from the OpenAPI specification.",
            "",
            "## Purpose",
            "",
            "This SDK is generated for **comparison purposes only**.",
            "Use it to evaluate against your current HoneyHive SDK implementation.",
            "",
            "## Structure",
            "",
            "```",
            "honeyhive_generated/",
            "├── models/          # Data models and schemas",
            "├── api/             # API client methods by service",
            "├── client/          # Main client classes",
            "└── types/           # Type definitions",
            "",
            "docs/                # Documentation",
            "examples/            # Usage examples",
            "tests/               # Generated tests",
            "```",
            "",
            "## Statistics",
            "",
            f"- **Models Generated**: {self.stats.models_generated}",
            f"- **API Methods**: {self.stats.api_methods_generated}",
            f"- **Client Classes**: {self.stats.client_classes_generated}",
            f"- **Services Discovered**: {self.stats.services_discovered}",
            f"- **Total Files**: {self.stats.total_files_generated}",
            f"- **Processing Time**: {self.stats.processing_time:.2f}s",
            "",
            "## Comparison Guide",
            "",
            "### Models Comparison",
            "",
            "1. Compare `honeyhive_generated/models/` with `src/honeyhive/models/`",
            "2. Look for:",
            "   - New model definitions",
            "   - Improved type annotations",
            "   - Additional validation rules",
            "   - Better field documentation",
            "",
            "### API Clients Comparison",
            "",
            "1. Compare `honeyhive_generated/api/` with `src/honeyhive/api/`",
            "2. Look for:",
            "   - New API methods",
            "   - Different parameter handling",
            "   - Improved error handling",
            "   - Better type safety",
            "",
            "### Client Architecture Comparison",
            "",
            "1. Compare `honeyhive_generated/client/` with your main client",
            "2. Look for:",
            "   - Different initialization patterns",
            "   - Service organization approaches",
            "   - Authentication handling",
            "   - Configuration management",
            "",
            "## Usage Example",
            "",
            "```python",
            "# Import generated SDK",
            "from honeyhive_generated import HoneyHiveGenerated",
            "from honeyhive_generated.models import *",
            "",
            "# Compare with your current usage:",
            "# from honeyhive import HoneyHive",
            "# from honeyhive.models import *",
            "",
            'client = HoneyHiveGenerated(api_key="your-key")',
            "```",
            "",
            "## Integration Considerations",
            "",
            "1. **Breaking Changes**: Check for any breaking changes in model definitions",
            "2. **New Features**: Identify new capabilities in the generated SDK",
            "3. **Performance**: Compare performance characteristics",
            "4. **Maintainability**: Evaluate code organization and structure",
            "5. **Testing**: Review generated test patterns",
            "",
            "## Next Steps",
            "",
            "1. Review each component systematically",
            "2. Identify improvements to adopt",
            "3. Plan migration strategy if beneficial",
            "4. Test compatibility with existing code",
            "5. Update documentation and examples",
        ]

        doc_file = self.client_output_dir / "README.md"
        with open(doc_file, "w") as f:
            f.write("\n".join(doc_content))

        logger.info(f"✅ Generated documentation: {doc_file}")

    def _generate_comparison_tools(self):
        """Generate tools to help with comparison."""
        logger.info("🔧 Generating comparison tools...")

        # Create comparison script
        comparison_script = [
            "#!/usr/bin/env python3",
            '"""',
            "SDK Comparison Tool",
            "",
            "This script helps compare the generated SDK with your current implementation.",
            '"""',
            "",
            "import os",
            "import sys",
            "from pathlib import Path",
            "",
            "def compare_models():",
            '    """Compare model definitions."""',
            '    print("🔍 Comparing Models...")',
            "    ",
            '    current_models = Path("src/honeyhive/models")',
            '    generated_models = Path("comparison_output/full_sdk/honeyhive_generated/models")',
            "    ",
            "    if not current_models.exists():",
            '        print("❌ Current models directory not found")',
            "        return",
            "    ",
            "    if not generated_models.exists():",
            '        print("❌ Generated models directory not found")',
            "        return",
            "    ",
            '    current_files = set(f.name for f in current_models.glob("*.py"))',
            '    generated_files = set(f.name for f in generated_models.glob("*.py"))',
            "    ",
            '    print(f"📊 Current models: {len(current_files)}")',
            '    print(f"📊 Generated models: {len(generated_files)}")',
            "    ",
            "    new_models = generated_files - current_files",
            "    if new_models:",
            '        print(f"➕ New models: {sorted(new_models)}")',
            "    ",
            "    missing_models = current_files - generated_files",
            "    if missing_models:",
            '        print(f"❌ Missing in generated: {sorted(missing_models)}")',
            "",
            "def compare_api_clients():",
            '    """Compare API client implementations."""',
            '    print("\\n🔍 Comparing API Clients...")',
            "    ",
            '    current_api = Path("src/honeyhive/api")',
            '    generated_api = Path("comparison_output/full_sdk/honeyhive_generated/api")',
            "    ",
            "    if current_api.exists() and generated_api.exists():",
            '        current_files = set(f.name for f in current_api.glob("*.py"))',
            '        generated_files = set(f.name for f in generated_api.glob("*.py"))',
            "        ",
            '        print(f"📊 Current API files: {len(current_files)}")',
            '        print(f"📊 Generated API files: {len(generated_files)}")',
            "    else:",
            '        print("⚠️  API directories not found for comparison")',
            "",
            "def main():",
            '    """Main comparison function."""',
            '    print("🚀 SDK Comparison Tool")',
            '    print("=" * 50)',
            "    ",
            "    compare_models()",
            "    compare_api_clients()",
            "    ",
            '    print("\\n💡 Next Steps:")',
            '    print("1. Review the detailed comparison above")',
            '    print("2. Examine individual files for differences")',
            '    print("3. Test generated code compatibility")',
            '    print("4. Plan integration strategy")',
            "",
            'if __name__ == "__main__":',
            "    main()",
        ]

        comparison_file = self.client_output_dir / "compare_with_current.py"
        with open(comparison_file, "w") as f:
            f.write("\n".join(comparison_script))

        # Make executable
        comparison_file.chmod(0o755)

        logger.info(f"✅ Generated comparison tool: {comparison_file}")

    def validate_generated_sdk(self) -> bool:
        """Validate the generated SDK."""
        logger.info("🔍 Validating generated SDK...")

        try:
            # Check directory structure
            required_dirs = [
                "honeyhive_generated",
                "honeyhive_generated/models",
                "honeyhive_generated/api",
                "honeyhive_generated/client",
            ]

            for req_dir in required_dirs:
                dir_path = self.client_output_dir / req_dir
                if not dir_path.exists():
                    logger.error(f"❌ Missing required directory: {req_dir}")
                    return False

            # Test basic imports
            sys.path.insert(0, str(self.client_output_dir))

            try:
                exec("from honeyhive_generated.models import *")
                logger.debug("✅ Models import successful")
            except Exception as e:
                logger.warning(f"⚠️  Models import failed: {e}")

            try:
                exec("from honeyhive_generated.api import *")
                logger.debug("✅ API import successful")
            except Exception as e:
                logger.warning(f"⚠️  API import failed: {e}")

            logger.info("✅ SDK validation completed")
            return True

        except Exception as e:
            logger.error(f"❌ SDK validation error: {e}")
            return False
        finally:
            # Clean up sys.path
            if str(self.client_output_dir) in sys.path:
                sys.path.remove(str(self.client_output_dir))

    def count_generated_files(self):
        """Count total generated files."""
        total_files = 0
        for file_path in self.client_output_dir.rglob("*.py"):
            total_files += 1

        self.stats.total_files_generated = total_files

    def generate_comparison_report(self) -> Dict:
        """Generate comprehensive comparison report."""
        self.count_generated_files()

        report = {
            "generation_summary": {
                "models_generated": self.stats.models_generated,
                "api_methods_generated": self.stats.api_methods_generated,
                "client_classes_generated": self.stats.client_classes_generated,
                "services_discovered": self.stats.services_discovered,
                "total_files_generated": self.stats.total_files_generated,
                "errors_handled": self.stats.errors_handled,
                "processing_time": self.stats.processing_time,
            },
            "sdk_structure": {
                "models_dir": "honeyhive_generated/models/",
                "api_dir": "honeyhive_generated/api/",
                "client_dir": "honeyhive_generated/client/",
                "docs_dir": "docs/",
                "examples_dir": "examples/",
            },
            "output_location": str(self.client_output_dir),
            "comparison_tools": [
                "README.md - Complete documentation",
                "compare_with_current.py - Comparison script",
                "honeyhive_generated/ - Generated SDK",
            ],
            "comparison_instructions": [
                "1. Run the comparison script: python compare_with_current.py",
                "2. Compare models: honeyhive_generated/models/ vs src/honeyhive/models/",
                "3. Compare API clients: honeyhive_generated/api/ vs src/honeyhive/api/",
                "4. Review client architecture: honeyhive_generated/client/",
                "5. Test compatibility with your existing code",
                "6. Identify improvements and new features",
                "7. Plan integration strategy",
            ],
        }

        return report


def main():
    """Main execution for full SDK generation."""
    logger.info("🚀 Generate Models and Client")
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
    generator = DynamicModelsAndClientGenerator(
        openapi_spec_path=openapi_spec, output_base_dir="comparison_output"
    )

    # Load OpenAPI spec
    if not generator.load_openapi_spec():
        return 1

    # Analyze spec
    analysis = generator.analyze_spec_for_client_generation()
    if analysis["total_endpoints"] == 0:
        logger.error("❌ No endpoints found for client generation")
        return 1

    # Generate full SDK
    if not generator.generate_full_sdk_with_openapi_client():
        return 1

    # Validate SDK
    if not generator.validate_generated_sdk():
        logger.warning("⚠️  SDK validation had issues, but continuing...")

    # Generate report
    report = generator.generate_comparison_report()

    report_file = "comparison_output/full_sdk_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    summary = report["generation_summary"]

    logger.info(f"\n🎉 Full SDK Generation Complete!")
    logger.info(f"📊 Models generated: {summary['models_generated']}")
    logger.info(f"📊 API methods: {summary['api_methods_generated']}")
    logger.info(f"📊 Client classes: {summary['client_classes_generated']}")
    logger.info(f"📊 Services discovered: {summary['services_discovered']}")
    logger.info(f"📊 Total files: {summary['total_files_generated']}")
    logger.info(f"⏱️  Processing time: {summary['processing_time']:.2f}s")

    logger.info(f"\n📁 Output Location:")
    logger.info(f"  {report['output_location']}")

    logger.info(f"\n💡 Next Steps:")
    for instruction in report["comparison_instructions"]:
        logger.info(f"  {instruction}")

    logger.info(f"\n💾 Files Generated:")
    logger.info(f"  • {report_file}")
    for tool in report["comparison_tools"]:
        logger.info(f"  • {tool}")

    return 0


if __name__ == "__main__":
    exit(main())
