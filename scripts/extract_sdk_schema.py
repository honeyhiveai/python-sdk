#!/usr/bin/env python3
"""
SDK Schema Extraction Tool

Automatically extracts JSON Schema from official provider SDKs (Python/TypeScript).

Usage:
    python scripts/extract_sdk_schema.py --provider openai
    python scripts/extract_sdk_schema.py --provider anthropic --python-only
    python scripts/extract_sdk_schema.py --provider gemini --typescript-only
"""

import argparse
import ast
import json
import logging
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class FieldInfo:
    """Information about a single field in a type definition."""

    name: str
    type_str: str
    required: bool
    nullable: bool
    nested_type: Optional[str] = None
    constraints: Optional[str] = None
    description: Optional[str] = None
    source: str = ""  # Python or TypeScript


@dataclass
class TypeDefinition:
    """Complete type definition extracted from SDK."""

    name: str
    fields: List[FieldInfo]
    source_file: str
    source_lines: str
    language: str  # "python" or "typescript"
    sdk_version: str
    commit_hash: str


class PydanticModelParser:
    """Parse Pydantic v2 models from Python SDK."""

    def __init__(self, sdk_path: Path):
        self.sdk_path = sdk_path
        self.parsed_types: Dict[str, TypeDefinition] = {}

    def find_type_files(self) -> List[Path]:
        """Find Python files containing Pydantic models."""
        type_files = []

        # Common patterns for type definition locations
        patterns = [
            "**/types/**/*.py",
            "**/models/**/*.py",
            "**/schemas/**/*.py",
        ]

        for pattern in patterns:
            type_files.extend(self.sdk_path.glob(pattern))

        logger.info(f"Found {len(type_files)} potential type files")
        return type_files

    def parse_file(self, file_path: Path) -> List[TypeDefinition]:
        """Parse a single Python file for Pydantic models."""
        try:
            content = file_path.read_text()
            tree = ast.parse(content)

            definitions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it inherits from BaseModel
                    if self._inherits_base_model(node):
                        type_def = self._parse_pydantic_model(node, file_path, content)
                        if type_def:
                            definitions.append(type_def)

            return definitions
        except Exception as e:
            logger.warning(f"Failed to parse {file_path}: {e}")
            return []

    def _inherits_base_model(self, node: ast.ClassDef) -> bool:
        """Check if class inherits from BaseModel."""
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "BaseModel":
                return True
        return False

    def _parse_pydantic_model(
        self,
        node: ast.ClassDef,
        file_path: Path,
        content: str
    ) -> Optional[TypeDefinition]:
        """Parse a Pydantic model class."""
        fields = []

        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                field_info = self._parse_field(item)
                if field_info:
                    fields.append(field_info)

        if not fields:
            return None

        # Get line range
        start_line = node.lineno
        end_line = node.end_lineno or start_line

        return TypeDefinition(
            name=node.name,
            fields=fields,
            source_file=str(file_path.relative_to(self.sdk_path)),
            source_lines=f"{start_line}-{end_line}",
            language="python",
            sdk_version="",  # Will be filled later
            commit_hash=""   # Will be filled later
        )

    def _parse_field(self, node: ast.AnnAssign) -> Optional[FieldInfo]:
        """Parse a single field annotation."""
        field_name = node.target.id
        type_annotation = ast.unparse(node.annotation)

        # Determine if optional
        required = True
        nullable = False

        if node.value is not None:
            required = False

        if "Optional[" in type_annotation:
            required = False
            nullable = True
            # Extract inner type
            type_annotation = re.sub(r"Optional\[(.*)\]", r"\1", type_annotation)

        # Extract nested types
        nested_type = None
        if "List[" in type_annotation or "Sequence[" in type_annotation:
            match = re.search(r"(?:List|Sequence)\[(.*?)\]", type_annotation)
            if match:
                nested_type = match.group(1)

        # Extract constraints
        constraints = None
        if "Literal[" in type_annotation:
            match = re.search(r"Literal\[(.*?)\]", type_annotation)
            if match:
                constraints = f"Literal: {match.group(1)}"

        return FieldInfo(
            name=field_name,
            type_str=self._map_python_type(type_annotation),
            required=required,
            nullable=nullable,
            nested_type=nested_type,
            constraints=constraints,
            source="python"
        )

    def _map_python_type(self, type_str: str) -> str:
        """Map Python types to JSON Schema types."""
        type_map = {
            "str": "string",
            "int": "integer",
            "float": "number",
            "bool": "boolean",
            "List": "array",
            "Dict": "object",
            "dict": "object",
            "Sequence": "array",
        }

        for py_type, json_type in type_map.items():
            if py_type in type_str:
                return json_type

        return type_str


class TypeScriptInterfaceParser:
    """Parse TypeScript interfaces from TypeScript SDK."""

    def __init__(self, sdk_path: Path):
        self.sdk_path = sdk_path
        self.parsed_types: Dict[str, TypeDefinition] = {}

    def find_type_files(self) -> List[Path]:
        """Find TypeScript files containing interfaces."""
        type_files = []

        # Common patterns for type definition locations
        patterns = [
            "**/*.ts",
            "**/*.d.ts",
        ]

        for pattern in patterns:
            type_files.extend(self.sdk_path.glob(pattern))

        # Filter out test files, node_modules
        type_files = [
            f for f in type_files
            if "node_modules" not in str(f)
            and ".test." not in str(f)
            and "test/" not in str(f)
        ]

        logger.info(f"Found {len(type_files)} potential TypeScript files")
        return type_files

    def parse_file(self, file_path: Path) -> List[TypeDefinition]:
        """Parse a single TypeScript file for interfaces."""
        try:
            content = file_path.read_text()
            definitions = []

            # Find all interface definitions
            interface_pattern = r"export\s+interface\s+(\w+)\s*{([^}]*)}"
            matches = re.finditer(interface_pattern, content, re.MULTILINE | re.DOTALL)

            for match in matches:
                interface_name = match.group(1)
                interface_body = match.group(2)

                type_def = self._parse_interface(
                    interface_name,
                    interface_body,
                    file_path,
                    content
                )
                if type_def:
                    definitions.append(type_def)

            return definitions
        except Exception as e:
            logger.warning(f"Failed to parse {file_path}: {e}")
            return []

    def _parse_interface(
        self,
        name: str,
        body: str,
        file_path: Path,
        full_content: str
    ) -> Optional[TypeDefinition]:
        """Parse TypeScript interface body."""
        fields = []

        # Parse each field line
        field_pattern = r"(\w+)(\?)?:\s*([^;]+);"
        for match in re.finditer(field_pattern, body):
            field_name = match.group(1)
            optional = match.group(2) == "?"
            type_str = match.group(3).strip()

            field_info = self._parse_field(field_name, type_str, optional)
            if field_info:
                fields.append(field_info)

        if not fields:
            return None

        # Find line numbers (approximate)
        start_line = full_content[:full_content.find(name)].count("\n") + 1

        return TypeDefinition(
            name=name,
            fields=fields,
            source_file=str(file_path.relative_to(self.sdk_path)),
            source_lines=f"{start_line}+",
            language="typescript",
            sdk_version="",
            commit_hash=""
        )

    def _parse_field(
        self,
        field_name: str,
        type_str: str,
        optional: bool
    ) -> FieldInfo:
        """Parse a TypeScript field."""
        # Check for nullable
        nullable = "| null" in type_str or "| undefined" in type_str
        type_str = type_str.replace("| null", "").replace("| undefined", "").strip()

        # Extract nested types
        nested_type = None
        if "Array<" in type_str:
            match = re.search(r"Array<(.*?)>", type_str)
            if match:
                nested_type = match.group(1)

        # Extract constraints (literal types)
        constraints = None
        if "'" in type_str or '"' in type_str:
            constraints = f"Literal: {type_str}"

        return FieldInfo(
            name=field_name,
            type_str=self._map_typescript_type(type_str),
            required=not optional,
            nullable=nullable,
            nested_type=nested_type,
            constraints=constraints,
            source="typescript"
        )

    def _map_typescript_type(self, type_str: str) -> str:
        """Map TypeScript types to JSON Schema types."""
        type_map = {
            "string": "string",
            "number": "number",
            "integer": "integer",
            "boolean": "boolean",
            "Array": "array",
            "object": "object",
        }

        for ts_type, json_type in type_map.items():
            if ts_type in type_str:
                return json_type

        return type_str


def clone_sdk(repo_url: str, version: Optional[str] = None) -> Tuple[Path, str, str]:
    """Clone SDK repository and return path, version, and commit hash."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        clone_path = tmp_path / "sdk"

        logger.info(f"Cloning {repo_url}...")
        subprocess.run(
            ["git", "clone", repo_url, str(clone_path)],
            check=True,
            capture_output=True
        )

        if version:
            logger.info(f"Checking out version {version}...")
            subprocess.run(
                ["git", "checkout", f"tags/{version}"],
                cwd=clone_path,
                check=True,
                capture_output=True
            )

        # Get commit hash
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=clone_path,
            capture_output=True,
            text=True,
            check=True
        )
        commit_hash = result.stdout.strip()

        # Get version (if not specified)
        if not version:
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                cwd=clone_path,
                capture_output=True,
                text=True
            )
            version = result.stdout.strip() if result.returncode == 0 else "unknown"

        logger.info(f"Cloned version {version} (commit: {commit_hash[:8]})")

        # Copy to persistent location
        output_path = Path(f"/tmp/sdk_{commit_hash[:8]}")
        if output_path.exists():
            import shutil
            shutil.rmtree(output_path)
        import shutil
        shutil.copytree(clone_path, output_path)

        return output_path, version, commit_hash


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Extract schemas from provider SDKs")
    parser.add_argument("--provider", required=True, help="Provider name (e.g., openai)")
    parser.add_argument("--python-sdk", help="Python SDK GitHub URL")
    parser.add_argument("--typescript-sdk", help="TypeScript SDK GitHub URL")
    parser.add_argument("--python-only", action="store_true", help="Only process Python SDK")
    parser.add_argument("--typescript-only", action="store_true", help="Only process TypeScript SDK")
    parser.add_argument("--output", help="Output directory", default="provider_response_schemas")

    args = parser.parse_args()

    output_dir = Path(args.output) / args.provider
    output_dir.mkdir(parents=True, exist_ok=True)

    all_types: Dict[str, TypeDefinition] = {}

    # Process Python SDK
    if not args.typescript_only and args.python_sdk:
        logger.info("Processing Python SDK...")
        sdk_path, version, commit = clone_sdk(args.python_sdk)
        parser_obj = PydanticModelParser(sdk_path)

        for file_path in parser_obj.find_type_files():
            definitions = parser_obj.parse_file(file_path)
            for type_def in definitions:
                type_def.sdk_version = version
                type_def.commit_hash = commit
                all_types[f"{type_def.name}_python"] = type_def

        logger.info(f"Extracted {len(all_types)} Python types")

    # Process TypeScript SDK
    if not args.python_only and args.typescript_sdk:
        logger.info("Processing TypeScript SDK...")
        sdk_path, version, commit = clone_sdk(args.typescript_sdk)
        parser_obj = TypeScriptInterfaceParser(sdk_path)

        for file_path in parser_obj.find_type_files():
            definitions = parser_obj.parse_file(file_path)
            for type_def in definitions:
                type_def.sdk_version = version
                type_def.commit_hash = commit
                all_types[f"{type_def.name}_typescript"] = type_def

        logger.info(f"Total types extracted: {len(all_types)}")

    # Generate output
    logger.info(f"Writing output to {output_dir}...")
    # TODO: Generate PARSED_TYPES.md, SDK_SOURCES.md, JSON Schema

    logger.info("✅ Extraction complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
