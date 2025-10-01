#!/usr/bin/env python3
"""
OpenAI Schema Validation Script (Phase 5)
Validates JSON Schema syntax and tests all examples against the schema.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import re


def validate_schema_syntax(schema_path: Path) -> Tuple[bool, str, Dict[str, Any]]:
    """Task 1: Validate JSON Schema syntax."""
    try:
        with open(schema_path) as f:
            schema = json.load(f)
        
        # Check required top-level fields
        required_fields = ["$schema", "version", "provider", "schemas"]
        missing = [f for f in required_fields if f not in schema]
        
        if missing:
            return False, f"Missing required fields: {missing}", {}
        
        # Check schemas structure
        schemas = schema.get("schemas", {})
        if not schemas:
            return False, "No schemas defined", {}
        
        # Validate $ref references resolve
        unresolved_refs = check_references(schema, schemas)
        if unresolved_refs:
            return False, f"Unresolved references: {unresolved_refs}", {}
        
        msg = f"✅ Schema valid: {len(schemas)} definitions, version {schema['version']}"
        return True, msg, schema
        
    except json.JSONDecodeError as e:
        return False, f"JSON syntax error: {e}", {}
    except Exception as e:
        return False, f"Validation error: {e}", {}


def check_references(schema: Dict[str, Any], schemas: Dict[str, Any]) -> List[str]:
    """Check that all $ref references resolve correctly."""
    unresolved = []
    
    def find_refs(obj: Any, path: str = ""):
        if isinstance(obj, dict):
            if "$ref" in obj:
                ref = obj["$ref"]
                # Parse #/schemas/SomeName format
                if ref.startswith("#/schemas/"):
                    schema_name = ref.split("/")[-1]
                    if schema_name not in schemas:
                        unresolved.append(f"{path}: {ref}")
            for key, value in obj.items():
                find_refs(value, f"{path}.{key}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                find_refs(item, f"{path}[{i}]")
    
    find_refs(schema)
    return unresolved


def validate_example(example_path: Path, schema: Dict[str, Any]) -> Tuple[bool, str]:
    """Task 2: Validate an example against the schema."""
    try:
        with open(example_path) as f:
            example = json.load(f)
        
        # Basic validation - check if it's the right type of response
        schemas = schema.get("schemas", {})
        
        # Determine example type
        if "object" in example:
            obj_type = example["object"]
            if obj_type == "chat.completion":
                return validate_chat_completion(example, schemas)
            elif obj_type == "chat.completion.chunk":
                return validate_streaming_chunk(example, schemas)
        elif "error" in example:
            return validate_error_response(example, schemas)
        
        return True, "Valid (type not checked)"
        
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except Exception as e:
        return False, f"Validation error: {e}"


def validate_chat_completion(example: Dict[str, Any], schemas: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate a chat completion response."""
    schema = schemas.get("ChatCompletionResponse", {})
    
    # Check required fields
    required = schema.get("required", [])
    missing = [f for f in required if f not in example]
    if missing:
        return False, f"Missing required fields: {missing}"
    
    # Check choices structure
    if "choices" in example and example["choices"]:
        choice = example["choices"][0]
        if "message" not in choice:
            return False, "Missing 'message' in choices[0]"
        
        message = choice["message"]
        
        # Check tool_calls if present
        if "tool_calls" in message:
            if not isinstance(message["tool_calls"], list):
                return False, "tool_calls must be array"
            
            for tc in message["tool_calls"]:
                if "function" in tc:
                    # CRITICAL: arguments should be JSON string
                    args = tc["function"].get("arguments")
                    if args is not None:
                        if not isinstance(args, str):
                            return False, f"tool_calls[].function.arguments must be JSON STRING, got {type(args).__name__}"
                        # Try parsing it as JSON to verify it's valid JSON string
                        try:
                            json.loads(args)
                        except:
                            return False, f"tool_calls[].function.arguments is not valid JSON string: {args}"
        
        # Check audio if present
        if "audio" in message:
            audio = message["audio"]
            if "data" in audio:
                # Should be base64 string
                if not isinstance(audio["data"], str):
                    return False, "audio.data must be base64 string"
    
    return True, "Valid chat completion"


def validate_streaming_chunk(example: Dict[str, Any], schemas: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate a streaming chunk response."""
    # Streaming chunks have different structure
    if "choices" not in example:
        return False, "Missing 'choices' in streaming chunk"
    
    if example["choices"]:
        choice = example["choices"][0]
        if "delta" not in choice:
            return False, "Missing 'delta' in streaming choice"
    
    return True, "Valid streaming chunk"


def validate_error_response(example: Dict[str, Any], schemas: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate an error response."""
    error = example.get("error", {})
    if "message" not in error:
        return False, "Missing 'message' in error"
    if "type" not in error:
        return False, "Missing 'type' in error"
    
    return True, "Valid error response"


def check_completeness(schema: Dict[str, Any], examples_dir: Path) -> Tuple[bool, List[str]]:
    """Task 3: Check completeness of schema coverage."""
    issues = []
    schemas = schema.get("schemas", {})
    
    # Check critical schemas exist
    critical_schemas = [
        "ChatCompletionResponse",
        "ChatCompletionChoice",
        "ChatCompletionMessage",
        "UsageInfo"
    ]
    
    for schema_name in critical_schemas:
        if schema_name not in schemas:
            issues.append(f"Missing critical schema: {schema_name}")
    
    # Check tool calls support
    if "ToolCall" in schemas:
        tool_call = schemas["ToolCall"]
        if "properties" in tool_call and "function" in tool_call["properties"]:
            func = tool_call["properties"]["function"]
            if "$ref" in func:
                func_schema_name = func["$ref"].split("/")[-1]
                if func_schema_name in schemas:
                    func_schema = schemas[func_schema_name]
                    if "properties" in func_schema and "arguments" in func_schema["properties"]:
                        args_def = func_schema["properties"]["arguments"]
                        # CRITICAL: Should be string type (JSON string)
                        if args_def.get("type") != "string":
                            issues.append(f"⚠️  ToolCall.function.arguments should be type 'string' (JSON string), got: {args_def.get('type')}")
                        # Check for json-string format hint
                        if args_def.get("format") != "json-string":
                            issues.append(f"⚠️  ToolCall.function.arguments should have format 'json-string', got: {args_def.get('format')}")
    
    # Check examples coverage
    examples = list(examples_dir.glob("*.json"))
    if len(examples) < 5:
        issues.append(f"Insufficient examples: {len(examples)} (recommended: 10+)")
    
    return len(issues) == 0, issues


def main():
    """Run all Phase 5 validation tasks."""
    print("=" * 60)
    print("OpenAI Schema Validation (Phase 5)")
    print("=" * 60)
    print()
    
    base_dir = Path(__file__).parent
    schema_path = base_dir / "v2025-01-30.json"
    examples_dir = base_dir / "examples"
    
    results = {
        "task_1_syntax": False,
        "task_2_examples": False,
        "task_3_completeness": False,
    }
    
    # Task 1: Validate Schema Syntax
    print("Task 1: Validate Schema Syntax")
    print("-" * 60)
    
    valid, msg, schema = validate_schema_syntax(schema_path)
    results["task_1_syntax"] = valid
    print(msg)
    print()
    
    if not valid:
        print("❌ Schema validation failed. Fix syntax errors first.")
        sys.exit(1)
    
    # Task 2: Test Examples
    print("Task 2: Test Examples Against Schema")
    print("-" * 60)
    
    examples = list(examples_dir.glob("*.json"))
    passed = 0
    failed = 0
    
    for example_path in sorted(examples):
        valid, msg = validate_example(example_path, schema)
        status = "✅" if valid else "❌"
        print(f"{status} {example_path.name}: {msg}")
        if valid:
            passed += 1
        else:
            failed += 1
    
    results["task_2_examples"] = failed == 0
    print()
    print(f"Examples: {passed} passed, {failed} failed out of {len(examples)} total")
    print()
    
    # Task 3: Check Completeness
    print("Task 3: Check Schema Completeness")
    print("-" * 60)
    
    complete, issues = check_completeness(schema, examples_dir)
    results["task_3_completeness"] = complete
    
    if complete:
        print("✅ Schema is complete")
    else:
        print("⚠️  Schema completeness issues:")
        for issue in issues:
            print(f"   - {issue}")
    print()
    
    # Summary
    print("=" * 60)
    print("Phase 5 Validation Summary")
    print("=" * 60)
    print()
    print(f"Task 1 (Syntax):      {'✅ PASS' if results['task_1_syntax'] else '❌ FAIL'}")
    print(f"Task 2 (Examples):    {'✅ PASS' if results['task_2_examples'] else '❌ FAIL'}")
    print(f"Task 3 (Completeness): {'✅ PASS' if results['task_3_completeness'] else '⚠️  ISSUES'}")
    print()
    
    all_pass = all(results.values())
    if all_pass:
        print("🎉 Phase 5 (Validation) COMPLETE!")
        print()
        print("Next: Phase 6 (Documentation)")
        sys.exit(0)
    else:
        print("❌ Phase 5 validation incomplete. Address issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

