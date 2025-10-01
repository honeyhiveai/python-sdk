#!/usr/bin/env python3
"""
Provider Template Generator for Universal LLM Discovery Engine v4.0

Generates consistent provider templates with the 4-file structure:
- structure_patterns.yaml (Provider signature detection)
- navigation_rules.yaml (Field extraction paths)
- field_mappings.yaml (HoneyHive schema mapping)
- transforms.yaml (Data transformation functions)
"""

import yaml
import argparse
import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class ProviderTemplateGenerator:
    """Generate template files for new providers."""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize template generator."""
        self.base_dir = base_dir or Path(__file__).parent.parent
        self.providers_dir = self.base_dir / "config" / "dsl" / "providers"
        self.schema_dir = self.base_dir / "provider_response_schemas"
        
    def generate_provider_files(
        self, 
        provider_name: str, 
        schema_path: Optional[Path] = None
    ) -> None:
        """Generate all 4 provider files from templates or schema.
        
        Args:
            provider_name: Name of the provider (e.g., 'openai')
            schema_path: Optional path to JSON Schema file for schema-driven generation
        """
        
        logger.info(f"Generating provider files for: {provider_name}")
        if schema_path:
            logger.info(f"Using schema: {schema_path}")
        else:
            logger.info("Using template-based generation (no schema provided)")
        
        provider_dir = self.providers_dir / provider_name
        provider_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate all 4 required files
        self._generate_structure_patterns(provider_dir, provider_name)
        self._generate_navigation_rules(provider_dir, provider_name, schema_path)
        self._generate_field_mappings(provider_dir, provider_name, schema_path)
        self._generate_transforms(provider_dir, provider_name, schema_path)
        
        logger.info(f"Successfully generated files for provider: {provider_name}")
        logger.info(f"Provider directory: {provider_dir}")
        logger.info("Files created:")
        for file_path in provider_dir.glob("*.yaml"):
            logger.info(f"  - {file_path.name}")
    
    def _generate_structure_patterns(self, provider_dir: Path, provider_name: str):
        """Generate structure_patterns.yaml template."""
        
        template = {
            "version": "1.0",
            "provider": provider_name,
            "dsl_type": "provider_structure_patterns",
            "patterns": {
                f"{provider_name}_primary": {
                    "signature_fields": ["field1", "field2", "field3"],
                    "optional_fields": ["optional1", "optional2"],
                    "confidence_weight": 0.95,
                    "description": f"Primary {provider_name} detection pattern"
                },
                f"{provider_name}_secondary": {
                    "signature_fields": ["alt_field1", "alt_field2"],
                    "optional_fields": ["alt_optional1"],
                    "confidence_weight": 0.85,
                    "description": f"Secondary {provider_name} detection pattern"
                }
            },
            "validation": {
                "minimum_signature_fields": 2,
                "maximum_patterns": 5,
                "confidence_threshold": 0.80
            }
        }
        
        file_path = provider_dir / "structure_patterns.yaml"
        with open(file_path, 'w') as f:
            yaml.dump(template, f, default_flow_style=False, sort_keys=False, indent=2)
        
        logger.debug(f"Generated: {file_path}")
    
    # ========== SCHEMA PROCESSING METHODS ==========
    
    def _load_provider_schema(self, schema_path: Path) -> Dict[str, Any]:
        """Load JSON Schema from provider_response_schemas.
        
        Args:
            schema_path: Path to JSON Schema file
            
        Returns:
            Parsed JSON Schema dictionary
        """
        logger.info(f"Loading schema from: {schema_path}")
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        with open(schema_path) as f:
            schema = json.load(f)
        
        logger.debug(f"Loaded schema with {len(schema.get('definitions', {}))} definitions")
        return schema
    
    def _extract_schema_fields(self, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recursively extract all fields from JSON Schema.
        
        Args:
            schema: JSON Schema dictionary
            
        Returns:
            List of field definitions with paths, types, and metadata
        """
        fields = []
        
        # Walk through schema definitions (check both 'definitions' and 'schemas')
        definitions = schema.get("definitions", schema.get("schemas", {}))
        
        for def_name, definition in definitions.items():
            if def_name == "ChatCompletionResponse":
                # Start from the main response object
                fields.extend(self._walk_schema_object(definition, "", schema))
                break
        
        logger.info(f"Extracted {len(fields)} fields from schema")
        return fields
    
    def _resolve_ref(self, ref_path: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve a $ref reference to its definition.
        
        Args:
            ref_path: Reference path (e.g., "#/schemas/ChatCompletionChoice")
            schema: Full schema dictionary
            
        Returns:
            Resolved schema object
        """
        # Remove leading #/ and split path
        if ref_path.startswith("#/"):
            ref_path = ref_path[2:]
        
        parts = ref_path.split("/")
        
        # Resolve reference
        ref_obj = schema
        for part in parts:
            ref_obj = ref_obj.get(part, {})
        
        return ref_obj
    
    def _walk_schema_object(
        self, 
        obj: Dict[str, Any], 
        path_prefix: str,
        schema: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Recursively walk schema object to extract fields.
        
        Args:
            obj: Schema object definition
            path_prefix: Current path prefix (e.g., "choices[].message")
            schema: Full schema for $ref resolution
            
        Returns:
            List of field definitions
        """
        fields = []
        
        # Handle $ref references
        if "$ref" in obj and schema:
            ref_path = obj["$ref"]
            resolved_obj = self._resolve_ref(ref_path, schema)
            
            # If resolved to a simple type, add it as a field
            if resolved_obj.get("type") in ["string", "integer", "number", "boolean"]:
                return [{
                    "path": path_prefix,
                    "type": resolved_obj.get("type"),
                    "format": resolved_obj.get("format"),
                    "nullable": "null" in resolved_obj.get("type", []) if isinstance(resolved_obj.get("type"), list) else resolved_obj.get("nullable", False),
                    "description": resolved_obj.get("description", "")
                }]
            
            # Otherwise recurse
            return self._walk_schema_object(resolved_obj, path_prefix, schema)
        
        if obj.get("type") == "object":
            for prop_name, prop_def in obj.get("properties", {}).items():
                field_path = f"{path_prefix}.{prop_name}" if path_prefix else prop_name
                
                # Skip metadata fields that aren't in the response
                if prop_name in ["id", "object", "created", "model", "system_fingerprint", "service_tier", "usage"]:
                    # Add these as top-level fields
                    fields.append({
                        "path": field_path,
                        "type": prop_def.get("type"),
                        "format": prop_def.get("format"),
                        "nullable": "null" in prop_def.get("type", []) if isinstance(prop_def.get("type"), list) else prop_def.get("nullable", False),
                        "description": prop_def.get("description", "")
                    })
                
                # Handle $ref references (resolve and recurse)
                if "$ref" in prop_def and schema:
                    fields.extend(self._walk_schema_object(prop_def, field_path, schema))
                
                # Recurse into nested objects
                elif prop_def.get("type") == "object":
                    fields.extend(self._walk_schema_object(prop_def, field_path, schema))
                
                # Handle arrays
                elif prop_def.get("type") == "array":
                    items = prop_def.get("items", {})
                    array_path = f"{field_path}[]"
                    
                    # Mark as array field
                    fields.append({
                        "path": field_path,
                        "type": "array",
                        "format": prop_def.get("format"),
                        "nullable": False,
                        "description": prop_def.get("description", ""),
                        "items_type": items.get("type")
                    })
                    
                    # Recurse into array items (will handle $ref if present)
                    fields.extend(self._walk_schema_object(items, array_path, schema))
                
                # Simple fields
                elif prop_name not in ["id", "object", "created", "model", "system_fingerprint", "service_tier", "usage"]:
                    fields.append({
                        "path": field_path,
                        "type": prop_def.get("type"),
                        "format": prop_def.get("format"),
                        "nullable": "null" in prop_def.get("type", []) if isinstance(prop_def.get("type"), list) else prop_def.get("nullable", False),
                        "description": prop_def.get("description", "")
                    })
        
        return fields
    
    def _map_to_instrumentor_pattern(self, field_path: str, instrumentor: str) -> str:
        """Map schema field path to instrumentor attribute pattern.
        
        Args:
            field_path: Schema field path (e.g., "choices[].message.content")
            instrumentor: Instrumentor name ("openinference", "traceloop", "openlit")
            
        Returns:
            Instrumentor-specific attribute pattern
        """
        # Convert array notation
        instrumented_path = field_path.replace("[]", ".0")
        
        if instrumentor == "openinference":
            # OpenInference uses llm.* namespace
            return f"llm.{instrumented_path}"
        
        elif instrumentor in ["traceloop", "openlit"]:
            # Traceloop/OpenLit use gen_ai.* namespace
            # Map common patterns
            if "choices" in instrumented_path:
                instrumented_path = instrumented_path.replace("choices.0", "completion.0")
            return f"gen_ai.{instrumented_path}"
        
        return instrumented_path
    
    def _determine_extraction_method(self, field: Dict[str, Any]) -> str:
        """Determine extraction method based on field type.
        
        Args:
            field: Field definition dictionary
            
        Returns:
            Extraction method name
        """
        # Array reconstruction needed
        if "[]" in field['path'] or field.get('type') == 'array':
            return "array_reconstruction"
        
        # JSON string preservation
        elif field.get("format") == "json-string":
            return "preserve_json_string"
        
        # Direct copy
        else:
            return "direct_copy"
    
    def _determine_fallback(self, field: Dict[str, Any]) -> Any:
        """Determine fallback value based on field type.
        
        Args:
            field: Field definition dictionary
            
        Returns:
            Appropriate fallback value
        """
        if field.get("nullable"):
            return None
        
        field_type = field.get("type")
        
        if field_type == "string":
            return ""
        elif field_type in ["integer", "number"]:
            return 0
        elif field_type == "boolean":
            return False
        elif field_type == "array":
            return []
        elif field_type == "object":
            return {}
        else:
            return None
    
    def _determine_honeyhive_section(self, field: Dict[str, Any]) -> str:
        """Determine which HoneyHive section a field belongs to.
        
        Args:
            field: Field definition dictionary
            
        Returns:
            Section name: "inputs", "outputs", "config", or "metadata"
        """
        path = field['path'].lower()
        
        # Metadata patterns (id, timestamps, usage, etc.)
        if any(x in path for x in ["id", "created", "service_tier", "usage", "system_fingerprint"]):
            return "metadata"
        
        # Output patterns (in choices[].message)
        elif "choices" in path or "message" in path:
            return "outputs"
        
        # Model identifier goes to config
        elif path == "model":
            return "config"
        
        # Default to metadata
        else:
            return "metadata"
    
    def _extract_field_name(self, field_path: str) -> str:
        """Extract simple field name from path.
        
        Args:
            field_path: Full field path (e.g., "choices[].message.content")
            
        Returns:
            Simple field name (e.g., "content")
        """
        # Remove array notation
        clean_path = field_path.replace("[]", "")
        # Get last component
        parts = clean_path.split(".")
        return parts[-1]
    
    def _find_json_string_fields(self, schema: Dict[str, Any], base_path: str) -> List[str]:
        """Find fields with json-string format in schema.
        
        Args:
            schema: JSON Schema dictionary
            base_path: Base path to search within
            
        Returns:
            List of field paths with json-string format
        """
        json_string_fields = []
        
        # For tool_calls, we know arguments is a JSON string
        if "tool_calls" in base_path:
            json_string_fields.append("function.arguments")
        
        return json_string_fields
    
    # ========== SCHEMA-DRIVEN GENERATION METHODS ==========
    
    def _generate_navigation_rules(
        self, 
        provider_dir: Path, 
        provider_name: str,
        schema_path: Optional[Path] = None
    ):
        """Generate navigation_rules.yaml from schema or template."""
        
        if schema_path and schema_path.exists():
            # SCHEMA-DRIVEN GENERATION
            logger.info("Generating navigation rules from schema...")
            schema = self._load_provider_schema(schema_path)
            fields = self._extract_schema_fields(schema)
            
            navigation_rules = {}
            
            # Generate rules for ALL instrumentors (OpenInference, Traceloop, OpenLit)
            instrumentors = ["openinference", "traceloop", "openlit"]
            
            for field in fields:
                # Skip some fields that don't need navigation rules
                if field['path'] == "object":
                    continue
                
                rule_base_name = field['path'].replace("[]", "_array").replace(".", "_")
                
                # Generate rule for each instrumentor
                for instrumentor in instrumentors:
                    rule_name = f"{instrumentor}_{rule_base_name}"
                    navigation_rules[rule_name] = {
                        "source_field": self._map_to_instrumentor_pattern(field['path'], instrumentor),
                        "extraction_method": self._determine_extraction_method(field),
                        "nullable": field.get("nullable", False),
                        "fallback_value": self._determine_fallback(field),
                        "description": f"Extract {field['path']} from {instrumentor}"
                    }
            
            template = {
                "version": "1.0",
                "provider": provider_name,
                "dsl_type": "provider_navigation_rules",
                "navigation_rules": navigation_rules
            }
        else:
            # TEMPLATE-BASED GENERATION (fallback)
            logger.info("Generating navigation rules from template...")
            template = {
                "version": "1.0",
                "provider": provider_name,
                "dsl_type": "provider_navigation_rules",
                "navigation_rules": {
                    "extract_input_messages": {
                        "source_field": "llm.input_messages",
                        "extraction_method": "direct_copy",
                        "fallback_value": [],
                        "validation": "array_of_objects",
                        "description": "Extract input message array"
                    },
                    "extract_output_messages": {
                        "source_field": "llm.output_messages", 
                        "extraction_method": "direct_copy",
                        "fallback_value": [],
                        "validation": "array_of_objects",
                        "description": "Extract output message array"
                    },
                    "extract_model_name": {
                        "source_field": "llm.model_name",
                        "extraction_method": "direct_copy",
                        "fallback_value": "unknown",
                        "validation": "non_empty_string",
                        "description": "Extract model name"
                    },
                    "extract_prompt_tokens": {
                        "source_field": "llm.token_count_prompt",
                        "extraction_method": "direct_copy",
                        "fallback_value": 0,
                        "validation": "positive_number",
                        "description": "Extract prompt token count"
                    },
                    "extract_completion_tokens": {
                        "source_field": "llm.token_count_completion",
                        "extraction_method": "direct_copy",
                        "fallback_value": 0,
                        "validation": "positive_number",
                        "description": "Extract completion token count"
                    }
                },
                "extraction_methods": {
                    "direct_copy": "Copy field value directly",
                    "array_flatten": "Flatten nested arrays",
                    "object_merge": "Merge multiple objects",
                    "string_concat": "Concatenate string values",
                    "first_non_null": "Return first non-null value from array"
                },
                "validation_rules": {
                    "non_empty_string": "Ensure string is not empty",
                    "positive_number": "Ensure number is positive",
                    "array_of_objects": "Ensure array contains only objects",
                    "array_of_strings": "Ensure array contains only strings",
                    "non_null": "Ensure value is not null"
                }
            }
        
        file_path = provider_dir / "navigation_rules.yaml"
        with open(file_path, 'w') as f:
            yaml.dump(template, f, default_flow_style=False, sort_keys=False, indent=2)
        
        logger.info(f"Generated: {file_path} ({len(template.get('navigation_rules', {}))} rules)")
    
    def _generate_field_mappings(
        self,
        provider_dir: Path,
        provider_name: str,
        schema_path: Optional[Path] = None
    ):
        """Generate field_mappings.yaml from schema or template."""
        
        if schema_path and schema_path.exists():
            # SCHEMA-DRIVEN GENERATION
            logger.info("Generating field mappings from schema...")
            schema = self._load_provider_schema(schema_path)
            fields = self._extract_schema_fields(schema)
            
            mappings = {
                "inputs": {},
                "outputs": {},
                "config": {},
                "metadata": {}
            }
            
            for field in fields:
                # Skip object type marker
                if field['path'] == "object":
                    continue
                
                section = self._determine_honeyhive_section(field)
                field_name = self._extract_field_name(field['path'])
                rule_name = f"traceloop_{field['path'].replace('[]', '_array').replace('.', '_')}"
                
                # Avoid duplicate field names in same section
                if field_name in mappings[section]:
                    field_name = f"{field_name}_{field['path'].replace('[]', '').replace('.', '_')}"
                
                mappings[section][field_name] = {
                    "source_rule": rule_name,
                    "required": not field.get("nullable", False),
                    "description": field.get("description", f"Extract {field['path']}")
                }
            
            template = {
                "version": "1.0",
                "provider": provider_name,
                "dsl_type": "provider_field_mappings",
                "field_mappings": mappings
            }
        else:
            # TEMPLATE-BASED GENERATION (fallback)
            logger.info("Generating field mappings from template...")
            template = {
                "version": "1.0",
                "provider": provider_name,
                "dsl_type": "provider_field_mappings",
                "field_mappings": {
                    "inputs": {
                        "chat_history": {
                            "source_rule": "extract_input_messages",
                            "required": False,
                            "description": f"{provider_name} input message array"
                        },
                        "prompt": {
                            "source_rule": "extract_user_prompt",
                            "required": False,
                            "description": "User prompt text"
                        },
                        "context": {
                            "source_rule": "extract_context_data",
                            "required": False,
                            "description": "Additional context information"
                        }
                    },
                    "outputs": {
                        "response": {
                            "source_rule": "extract_output_messages",
                            "required": False,
                            "description": f"{provider_name} response message array"
                        },
                        "completion": {
                            "source_rule": "extract_completion_text",
                            "required": False,
                            "description": "Completion text content"
                        },
                        "tool_calls": {
                            "source_rule": "extract_tool_calls",
                            "required": False,
                            "description": "Function/tool call results"
                        }
                    },
                    "config": {
                        "model": {
                            "source_rule": "extract_model_name",
                            "required": True,
                            "description": f"{provider_name} model identifier"
                        },
                        "temperature": {
                            "source_rule": "extract_temperature",
                            "required": False,
                            "description": "Model temperature setting"
                        },
                        "max_tokens": {
                            "source_rule": "extract_max_tokens",
                            "required": False,
                            "description": "Maximum token limit"
                        }
                    },
                    "metadata": {
                        "provider": {
                            "source_rule": f"static_{provider_name}",
                            "required": True,
                            "description": "Provider identifier"
                        },
                        "prompt_tokens": {
                            "source_rule": "extract_prompt_tokens",
                            "required": False,
                            "description": "Input token count"
                        },
                        "completion_tokens": {
                            "source_rule": "extract_completion_tokens",
                            "required": False,
                            "description": "Output token count"
                        },
                        "total_tokens": {
                            "source_rule": "calculate_total_tokens",
                            "required": False,
                            "description": "Total token usage"
                        },
                        "instrumentor": {
                            "source_rule": "detect_instrumentor",
                            "required": False,
                            "description": "Instrumentor framework used"
                        }
                    }
                },
                "schema_validation": {
                    "inputs": {
                        "allow_empty": True,
                        "max_fields": 20
                    },
                    "outputs": {
                        "allow_empty": True,
                        "max_fields": 20
                    },
                    "config": {
                        "require_model": True,
                        "allow_empty": False
                    },
                    "metadata": {
                        "require_provider": True,
                        "allow_empty": False
                    }
                }
            }
        
        file_path = provider_dir / "field_mappings.yaml"
        with open(file_path, 'w') as f:
            yaml.dump(template, f, default_flow_style=False, sort_keys=False, indent=2)
        
        logger.info(f"Generated: {file_path}")
    
    def _generate_transforms(
        self,
        provider_dir: Path, 
        provider_name: str,
        schema_path: Optional[Path] = None
    ):
        """Generate transforms.yaml from schema or template."""
        
        if schema_path and schema_path.exists():
            # SCHEMA-DRIVEN GENERATION
            logger.info("Generating transforms from schema...")
            schema = self._load_provider_schema(schema_path)
            fields = self._extract_schema_fields(schema)
            
            transforms = {}
            
            for field in fields:
                # Only create transforms for complex fields
                if field.get('type') == 'array' and '[]' in field['path']:
                    # Array reconstruction transform
                    transform_name = f"extract_{field['path'].replace('[]', '_array').replace('.', '_')}"
                    
                    transforms[transform_name] = {
                        "function_type": "array_reconstruction",
                        "implementation": "reconstruct_array_from_flattened",
                        "parameters": {
                            "prefix": field['path'].replace("[]", ""),
                            "preserve_json_strings": self._find_json_string_fields(schema, field['path'])
                        },
                        "description": f"Reconstruct {field['path']} from flattened attributes"
                    }
                
                elif field.get("format") == "json-string":
                    # JSON string preservation transform
                    transform_name = f"extract_{field['path'].replace('.', '_')}"
                    
                    transforms[transform_name] = {
                        "function_type": "string_extraction",
                        "implementation": "extract_first_non_empty",
                        "parameters": {
                            "preserve_as_json": True
                        },
                        "description": f"Extract {field['path']} as JSON string"
                    }
            
            template = {
                "version": "1.0",
                "provider": provider_name,
                "dsl_type": "provider_transforms",
                "transforms": transforms
            }
        else:
            # TEMPLATE-BASED GENERATION (fallback)
            logger.info("Generating transforms from template...")
            template = {
            "version": "1.0",
            "provider": provider_name,
            "dsl_type": "provider_transforms",
            "transforms": {
                "extract_user_prompt": {
                    "function_type": "string_extraction",
                    "implementation": "extract_user_message_content",
                    "parameters": {
                        "role_filter": "user",
                        "content_field": "content",
                        "join_multiple": True,
                        "separator": "\n\n"
                    },
                    "description": f"Extract user prompt from {provider_name} messages"
                },
                "extract_completion_text": {
                    "function_type": "string_extraction",
                    "implementation": "extract_assistant_message_content",
                    "parameters": {
                        "role_filter": "assistant",
                        "content_field": "content",
                        "join_multiple": True,
                        "separator": "\n"
                    },
                    "description": f"Extract completion text from {provider_name} response"
                },
                "calculate_total_tokens": {
                    "function_type": "numeric_calculation",
                    "implementation": "sum_fields",
                    "parameters": {
                        "source_fields": ["prompt_tokens", "completion_tokens"],
                        "fallback_value": 0
                    },
                    "description": f"Calculate total {provider_name} token usage"
                },
                "extract_tool_calls": {
                    "function_type": "array_transformation",
                    "implementation": "extract_field_values",
                    "parameters": {
                        "source_array": "tool_calls",
                        "extract_field": "function",
                        "preserve_structure": True
                    },
                    "description": "Extract tool call information"
                },
                "detect_instrumentor": {
                    "function_type": "string_extraction",
                    "implementation": "detect_instrumentor_framework",
                    "parameters": {
                        "attribute_patterns": {
                            "openinference": ["llm.input_messages", "llm.output_messages"],
                            "traceloop": ["gen_ai.request.model", "gen_ai.completion"],
                            "direct": [f"{provider_name}.model", f"{provider_name}.messages"]
                        }
                    },
                    "description": "Detect which instrumentor framework is being used"
                }
            },
            "function_registry": {
                "string_extraction": [
                    "extract_user_message_content",
                    "extract_assistant_message_content",
                    "extract_system_message_content",
                    "extract_first_non_empty"
                ],
                "array_transformation": [
                    "flatten_and_join",
                    "filter_by_role",
                    "extract_field_values",
                    "deduplicate_array"
                ],
                "numeric_calculation": [
                    "sum_fields",
                    "average_fields",
                    "max_fields",
                    "min_fields"
                ],
                "object_transformation": [
                    "merge_objects",
                    "filter_object_fields",
                    "rename_object_keys",
                    "flatten_nested_object"
                ]
            },
            "validation": {
                "max_transforms_per_provider": 20,
                "required_parameters": ["function_type", "implementation"],
                "allowed_function_types": [
                    "string_extraction",
                    "array_transformation", 
                    "numeric_calculation",
                    "object_transformation"
                ]
            }
        }
        
        file_path = provider_dir / "transforms.yaml"
        with open(file_path, 'w') as f:
            yaml.dump(template, f, default_flow_style=False, sort_keys=False, indent=2)
        
        logger.debug(f"Generated: {file_path}")

def main():
    """Main entry point for provider template generation."""
    
    parser = argparse.ArgumentParser(
        description="Generate provider template files for Universal LLM Discovery Engine v4.0"
    )
    parser.add_argument(
        "--provider",
        required=True,
        help="Provider name (e.g., openai, anthropic, gemini)"
    )
    parser.add_argument(
        "--schema",
        type=Path,
        help="Path to provider JSON Schema for schema-driven generation (e.g., provider_response_schemas/openai/v2025-01-30.json)"
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        help="Base directory for the project (default: parent of script directory)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        generator = ProviderTemplateGenerator(args.base_dir)
        generator.generate_provider_files(args.provider, args.schema)
        
        print(f"\n✅ Successfully generated template files for provider: {args.provider}")
        print(f"📁 Provider directory: {generator.providers_dir / args.provider}")
        print("\n📝 Next steps:")
        print("1. Edit the generated YAML files to match your provider's specific patterns")
        print("2. Update signature_fields in structure_patterns.yaml")
        print("3. Configure field extraction rules in navigation_rules.yaml")
        print("4. Map fields to HoneyHive schema in field_mappings.yaml")
        print("5. Define transformation functions in transforms.yaml")
        print("6. Test provider detection with: python scripts/test_provider_detection.py")
        
    except Exception as e:
        logger.error(f"Failed to generate provider template: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
