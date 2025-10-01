"""OpenInference Semantic Convention Definition v0.1.31.

Based on official OpenInference semantic conventions from:
https://github.com/Arize-ai/openinference/blob/main/python/openinference-semantic-conventions/src/openinference/semconv/trace/__init__.py

This definition contains the complete mapping specification for OpenInference
attributes to HoneyHive schema, extracted from production analysis.
"""

# pylint: disable=line-too-long,duplicate-code
# Justification: DSL configuration files contain long descriptive strings and URLs
# that should not be broken for readability and maintainability

# pylint: disable=unused-import
# Justification: Type imports are used for static type checking and IDE support
# even if not used at runtime in configuration files

from typing import Any, Dict, List

# Convention metadata
CONVENTION_DEFINITION = {
    "provider": "openinference",
    "version": "0.1.31",
    "source_url": "https://github.com/Arize-ai/openinference/blob/main/python/openinference-semantic-conventions/src/openinference/semconv/trace/__init__.py",
    "description": "OpenInference semantic conventions for LLM observability",
    # Detection patterns - attributes that identify this convention
    "detection_patterns": {
        "required_prefixes": ["llm."],
        "signature_attributes": [
            "llm.input_messages",
            "llm.output_messages",
            "llm.model_name",
            "llm.provider",
            "openinference.span.kind",
        ],
        "unique_attributes": ["openinference.span.kind", "llm.invocation_parameters"],
    },
    # Input mapping - how to extract inputs from OpenInference attributes
    "input_mapping": {
        "target_schema": "chat_history",
        "mappings": {
            "llm.input_messages.*": {
                "target": "chat_history",
                "transform": "parse_flattened_messages",
                "description": "Parse flattened OpenInference message attributes to chat_history",
            },
            "llm.prompts": {
                "target": "prompts",
                "transform": "parse_json_or_direct",
                "description": "Alternative prompt format",
            },
            "llm.system_message": {
                "target": "system_message",
                "transform": "direct",
                "description": "System message content",
            },
            "llm.retrieved_documents": {
                "target": "retrieved_documents",
                "transform": "direct",
                "description": "Retrieved documents for RAG",
            },
        },
    },
    # Output mapping - how to extract outputs from OpenInference attributes
    "output_mapping": {
        "target_schema": "content_finish_reason_role",
        "mappings": {
            # Separate rules for each target field (following Traceloop pattern)
            "llm.output_messages": {
                "target": "content",
                "transform": "extract_content_from_messages",
                "description": "Extract content from OpenInference output messages",
            },
            "llm.output_messages.role": {
                "target": "role",
                "transform": "extract_role_from_messages",
                "description": "Extract role from OpenInference output messages",
            },
            "llm.output_messages.*.content": {
                "target": "content",
                "transform": "extract_content_from_flattened",
                "description": "Extract content from flattened OpenInference output message attributes",
            },
            "llm.output_messages.*.role": {
                "target": "role",
                "transform": "extract_role_from_flattened",
                "description": "Extract role from flattened OpenInference output message attributes",
            },
            "output.value": {
                "target": "content",
                "transform": "extract_content_from_json",
                "description": "Extract content from OpenAI response JSON",
            },
            "output.value.role": {
                "target": "role",
                "transform": "extract_role_from_json",
                "description": "Extract role from OpenAI response JSON",
            },
            "output.value.finish_reason": {
                "target": "finish_reason",
                "transform": "extract_finish_reason_from_json",
                "description": "Extract finish_reason from OpenAI response JSON",
            },
            "llm.response.finish_reasons": {
                "target": "finish_reason",
                "transform": "direct",
                "description": "Extract first finish reason",
            },
            "llm.function_calls": {
                "target": "function_calls",
                "transform": "direct",
                "description": "Function calls made by model",
            },
            "llm.tool_calls": {
                "target": "tool_calls",
                "transform": "direct",
                "description": "Tool calls made by model",
            },
        },
    },
    # Config mapping - how to extract config from OpenInference attributes
    "config_mapping": {
        "target_schema": "llm_config",
        "mappings": {
            "llm.model_name": {
                "target": "model",
                "transform": "direct",
                "description": "Model name",
            },
            "llm.provider": {
                "target": "provider",
                "transform": "direct",
                "description": "LLM provider",
            },
            "llm.invocation_parameters": {
                "target": "invocation_parameters",
                "transform": "parse_json_or_direct",
                "description": "Extract parameters from JSON",
            },
            "llm.temperature": {
                "target": "temperature",
                "transform": "direct",
                "description": "Temperature parameter",
            },
            "llm.max_tokens": {
                "target": "max_completion_tokens",
                "transform": "direct",
                "description": "Maximum tokens",
            },
        },
        "defaults": {"headers": "None", "is_streaming": False},
    },
    # Metadata mapping - how to extract metadata from OpenInference attributes
    "metadata_mapping": {
        "target_schema": "llm_metadata",
        "mappings": {
            "llm.token_count.total": {
                "target": "total_tokens",
                "transform": "direct",
                "description": "Total token count",
            },
            "llm.token_count.prompt": {
                "target": "prompt_tokens",
                "transform": "direct",
                "description": "Prompt token count",
            },
            "llm.token_count.completion": {
                "target": "completion_tokens",
                "transform": "direct",
                "description": "Completion token count",
            },
            "llm.response.model": {
                "target": "response_model",
                "transform": "direct",
                "description": "Response model name",
            },
            "openinference.span.kind": {
                "target": "span_kind",
                "transform": "direct",
                "description": "OpenInference span kind",
            },
        },
        "defaults": {"llm.request.type": "chat"},
    },
    # Transform functions - how to process attribute values (using generic transforms)
    "transforms": {
        "parse_messages": {
            "description": "Parse message format to standardized chat_history (generic)",
            "implementation": "generic_message_parser.parse_messages",
        },
        "parse_flattened_messages": {
            "description": "Parse flattened message format (generic for any provider)",
            "implementation": "generic_message_parser.parse_flattened_messages",
        },
        "extract_content_from_messages": {
            "description": "Extract content from message list (generic)",
            "implementation": "generic_extractor.extract_content_from_messages",
        },
        "extract_role_from_messages": {
            "description": "Extract role from message list (generic)",
            "implementation": "generic_extractor.extract_role_from_messages",
        },
        "extract_content_from_flattened": {
            "description": "Extract content from flattened attributes (generic)",
            "implementation": "generic_extractor.extract_content_from_flattened",
        },
        "extract_role_from_flattened": {
            "description": "Extract role from flattened attributes (generic)",
            "implementation": "generic_extractor.extract_role_from_flattened",
        },
        "extract_content_from_json": {
            "description": "Extract content from JSON response (generic)",
            "implementation": "generic_extractor.extract_content_from_json",
        },
        "extract_role_from_json": {
            "description": "Extract role from JSON response (generic)",
            "implementation": "generic_extractor.extract_role_from_json",
        },
        "extract_finish_reason_from_json": {
            "description": "Extract finish_reason from JSON response (generic)",
            "implementation": "generic_extractor.extract_finish_reason_from_json",
        },
        "parse_json_or_direct": {
            "description": "Parse JSON string or return value directly (generic)",
            "implementation": "generic_json_parser.parse_json_or_direct",
        },
    },
    # Priority and compatibility
    "priority": 80,  # High priority for OpenInference
    "compatible_versions": ["0.1.30", "0.1.31", "0.1.32"],
    "deprecated": False,
    # Validation rules
    "validation": {
        "required_for_detection": ["llm.input_messages", "llm.model_name"],
        "mutually_exclusive": [],
        "dependencies": {
            "llm.token_count.total": [
                "llm.token_count.prompt",
                "llm.token_count.completion",
            ]
        },
    },
}
