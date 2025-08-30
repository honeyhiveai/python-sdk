#!/usr/bin/env python3
"""
Script to generate dataclass models from OpenAPI specification.
This provides an alternative to datamodel-codegen for generating dataclass-based models.
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import argparse


def get_python_type(schema: Dict[str, Any], field_name: str = "") -> str:
    """Convert OpenAPI schema type to Python type annotation."""

    # Handle references
    if "$ref" in schema:
        ref_name = schema["$ref"].split("/")[-1]
        return ref_name

    # Handle enums
    if "enum" in schema:
        return "str"  # We'll handle enums separately

    # Handle basic types
    schema_type = schema.get("type", "string")

    if schema_type == "string":
        if "format" in schema:
            if schema["format"] == "date-time":
                return "datetime"
            elif schema["format"] == "uuid":
                return "UUID"
        return "str"
    elif schema_type == "integer":
        return "int"
    elif schema_type == "number":
        return "float"
    elif schema_type == "boolean":
        return "bool"
    elif schema_type == "array":
        items_schema = schema.get("items", {})
        item_type = get_python_type(items_schema, field_name)
        return f"List[{item_type}]"
    elif schema_type == "object":
        if "additionalProperties" in schema:
            additional_props = schema["additionalProperties"]
            if isinstance(additional_props, dict):
                value_type = get_python_type(additional_props, field_name)
                return f"Dict[str, {value_type}]"
            else:
                return "Dict[str, Any]"
        else:
            return "Dict[str, Any]"

    return "Any"


def generate_enum(schema: Dict[str, Any], name: str) -> str:
    """Generate enum class from OpenAPI schema."""
    if "enum" not in schema:
        return ""

    lines = [f"class {name}(Enum):"]
    for value in schema["enum"]:
        # Convert value to valid Python identifier
        if isinstance(value, str):
            identifier = value.replace("-", "_").replace(" ", "_")
            lines.append(f'    {identifier} = "{value}"')
        else:
            lines.append(f"    {value} = {value}")

    return "\n".join(lines)


def generate_dataclass(
    schema: Dict[str, Any], name: str, required_fields: List[str]
) -> str:
    """Generate dataclass from OpenAPI schema."""

    lines = [f"@dataclass"]
    lines.append(f"class {name}:")

    # Add description as docstring if available
    if "description" in schema:
        lines.append(f'    """{schema["description"]}"""')

    # Generate fields
    properties = schema.get("properties", {})
    for field_name, field_schema in properties.items():
        field_type = get_python_type(field_schema, field_name)

        # Check if field is required
        is_required = field_name in required_fields

        if is_required:
            lines.append(f"    {field_name}: {field_type}")
        else:
            # Add default value for optional fields
            if field_type == "List[Any]":
                lines.append(
                    f"    {field_name}: {field_type} = field(default_factory=list)"
                )
            elif field_type == "Dict[str, Any]":
                lines.append(
                    f"    {field_name}: {field_type} = field(default_factory=dict)"
                )
            else:
                lines.append(f"    {field_name}: Optional[{field_type}] = None")

    # Add serialization methods
    lines.append("")
    lines.append("    def to_dict(self) -> Dict[str, Any]:")
    lines.append('        """Convert to dictionary for JSON serialization."""')
    lines.append("        result = asdict(self)")
    lines.append("        # Handle enum serialization")
    lines.append("        for key, value in result.items():")
    lines.append("            if isinstance(value, Enum):")
    lines.append("                result[key] = value.value")
    lines.append("        return {k: v for k, v in result.items() if v is not None}")

    lines.append("")
    lines.append("    def to_json(self) -> str:")
    lines.append('        """Convert to JSON string."""')
    lines.append("        return json.dumps(self.to_dict(), indent=2)")

    lines.append("")
    lines.append("    @classmethod")
    lines.append(f'    def from_dict(cls, data: Dict[str, Any]) -> "{name}":')
    lines.append('        """Create instance from dictionary."""')
    lines.append("        # Handle enum deserialization")
    lines.append("        for key, value in data.items():")
    lines.append("            if key in cls.__dataclass_fields__:")
    lines.append("                field_info = cls.__dataclass_fields__[key]")
    lines.append(
        '                if hasattr(field_info.type, "__origin__") and field_info.type.__origin__ is type:'
    )
    lines.append("                    if field_info.type == Enum:")
    lines.append("                        # Find the actual enum class")
    lines.append("                        for base in cls.__mro__:")
    lines.append('                            if hasattr(base, "__annotations__"):')
    lines.append("                                if key in base.__annotations__:")
    lines.append(
        "                                    enum_class = base.__annotations__[key]"
    )
    lines.append(
        '                                    if hasattr(enum_class, "__origin__") and enum_class.__origin__ is Union:'
    )
    lines.append(
        "                                        enum_class = next((t for t in enum_class.__args__ if t != type(None)), None)"
    )
    lines.append(
        "                                    if enum_class and hasattr(enum_class, value):"
    )
    lines.append(
        "                                        data[key] = enum_class(value)"
    )
    lines.append("        return cls(**data)")

    lines.append("")
    lines.append("    @classmethod")
    lines.append(f'    def from_json(cls, json_str: str) -> "{name}":')
    lines.append('        """Create instance from JSON string."""')
    lines.append("        data = json.loads(json_str)")
    lines.append("        return cls.from_dict(data)")

    return "\n".join(lines)


def generate_models(
    openapi_path: str, output_path: str, include_validation: bool = False
):
    """Generate dataclass models from OpenAPI specification."""

    # Read OpenAPI spec
    with open(openapi_path) as f:
        if openapi_path.endswith(".yaml") or openapi_path.endswith(".yml"):
            spec = yaml.safe_load(f)
        else:
            spec = json.load(f)

    # Generate file header
    lines = [
        "# Generated from OpenAPI specification using custom dataclass generator",
        "# This file provides dataclass alternatives to Pydantic models",
        "",
        "from dataclasses import dataclass, field, asdict",
        "from typing import Optional, Dict, Any, List, Union",
        "from datetime import datetime",
        "from enum import Enum",
        "import json",
        "",
        "# ============================================================================",
        "# Generated Models",
        "# ============================================================================",
        "",
    ]

    # Generate enums first
    schemas = spec.get("components", {}).get("schemas", {})
    enums = []

    for name, schema in schemas.items():
        if "enum" in schema:
            enum_code = generate_enum(schema, name)
            if enum_code:
                enums.append((name, enum_code))

    # Sort enums by name for consistent output
    enums.sort(key=lambda x: x[0])

    for name, enum_code in enums:
        lines.append(enum_code)
        lines.append("")

    # Generate dataclasses
    dataclasses = []

    for name, schema in schemas.items():
        if schema.get("type") == "object" and "enum" not in schema:
            required_fields = schema.get("required", [])
            dataclass_code = generate_dataclass(schema, name, required_fields)
            dataclasses.append((name, dataclass_code))

    # Sort dataclasses by name for consistent output
    dataclasses.sort(key=lambda x: x[0])

    for name, dataclass_code in dataclasses:
        lines.append(dataclass_code)
        lines.append("")

    # Add validation utilities if requested
    if include_validation:
        lines.extend(
            [
                "# ============================================================================",
                "# Validation Utilities",
                "# ============================================================================",
                "",
                "class DataclassValidator:",
                '    """Utility class for validating dataclass instances."""',
                "    ",
                "    @staticmethod",
                "    def validate_required_fields(instance: Any) -> List[str]:",
                '        """Validate that required fields are not None."""',
                "        errors = []",
                "        for field_name, field_value in instance.__dict__.items():",
                "            field_info = instance.__class__.__dataclass_fields__[field_name]",
                "            if not field_info.default and not field_info.default_factory and field_value is None:",
                "                errors.append(f\"Field '{field_name}' is required but is None\")",
                "        return errors",
                "    ",
                "    @staticmethod",
                "    def validate_types(instance: Any) -> List[str]:",
                '        """Basic type validation for dataclass instances."""',
                "        errors = []",
                "        for field_name, field_value in instance.__dict__.items():",
                "            field_info = instance.__class__.__dataclass_fields__[field_name]",
                "            expected_type = field_info.type",
                "            ",
                "            # Handle Optional types",
                "            if hasattr(expected_type, '__origin__') and expected_type.__origin__ is Union:",
                "                if type(None) in expected_type.__args__:",
                "                    if field_value is not None:",
                "                        expected_type = next(t for t in expected_type.__args__ if t is not type(None))",
                "                    else:",
                "                        continue",
                "            ",
                "            if field_value is not None and not isinstance(field_value, expected_type):",
                "                errors.append(f\"Field '{field_name}' expected {expected_type}, got {type(field_value)}\")",
                "        ",
                "        return errors",
                "",
            ]
        )

    # Write output file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(lines))

    print(f"Generated {len(dataclasses)} dataclasses and {len(enums)} enums")
    print(f"Output written to: {output_file.absolute()}")


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Generate dataclass models from OpenAPI specification"
    )
    parser.add_argument(
        "input", help="Path to OpenAPI specification file (YAML or JSON)"
    )
    parser.add_argument("output", help="Output path for generated Python file")
    parser.add_argument(
        "--validation", action="store_true", help="Include validation utilities"
    )

    args = parser.parse_args()

    try:
        generate_models(args.input, args.output, args.validation)
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
