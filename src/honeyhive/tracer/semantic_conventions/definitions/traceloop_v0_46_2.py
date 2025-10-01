"""Traceloop Semantic Convention Definition v0.46.2.

Based on official Traceloop semantic conventions from:
https://github.com/traceloop/openllmetry/blob/main/packages/opentelemetry-semantic-conventions-ai/opentelemetry/semconv_ai/__init__.py

This definition contains the complete mapping specification for Traceloop
gen_ai.* attributes to HoneyHive schema, extracted from production analysis.
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
    "provider": "traceloop",
    "version": "0.46.2",
    "source_url": "https://github.com/traceloop/openllmetry/blob/main/packages/opentelemetry-semantic-conventions-ai/opentelemetry/semconv_ai/__init__.py",
    "description": "Traceloop semantic conventions for LLM observability using gen_ai.* attributes",
    # Detection patterns - attributes that identify this convention
    "detection_patterns": {
        "required_prefixes": ["gen_ai.", "llm."],
        "signature_attributes": [
            "llm.request.type",
            "gen_ai.request.model",
            "gen_ai.system",
            "gen_ai.usage.prompt_tokens",
            "gen_ai.usage.completion_tokens",
        ],
        "unique_attributes": [
            "llm.request.type",
            "gen_ai.openai.api_base",
            "gen_ai.request.messages.0.role",
        ],
    },
    # Input mapping - how to extract inputs from Traceloop attributes
    "input_mapping": {
        "target_schema": "chat_history",
        "mappings": {
            "gen_ai.prompt.*": {
                "target": "chat_history",
                "transform": "parse_flattened_messages",
                "description": "Parse Traceloop flattened prompt format (gen_ai.prompt.N.role/content)",
            },
            "gen_ai.request.messages.*": {
                "target": "chat_history",
                "transform": "parse_flattened_messages",
                "description": "Parse Traceloop flattened message format (fallback)",
            },
            "gen_ai.request.system_prompt": {
                "target": "system_prompt",
                "transform": "direct",
                "description": "System prompt content",
            },
            "gen_ai.request.prompt": {
                "target": "prompt",
                "transform": "direct",
                "description": "User prompt for completion-style requests",
            },
        },
    },
    # Output mapping - how to extract outputs from Traceloop attributes
    "output_mapping": {
        "target_schema": "content_finish_reason_role",
        "mappings": {
            "gen_ai.completion.*": {
                "target": "content",
                "transform": "extract_content_from_flattened",
                "description": "Extract content from Traceloop completion attributes",
            },
            "gen_ai.completion.*.role": {
                "target": "role",
                "transform": "extract_role_from_flattened",
                "description": "Extract role from Traceloop completion attributes",
            },
            "gen_ai.completion.*.finish_reason": {
                "target": "finish_reason",
                "transform": "extract_finish_reason_from_json",
                "description": "Extract finish_reason from Traceloop completion attributes",
            },
            "gen_ai.response.messages.*": {
                "target": "content",
                "transform": "extract_content_from_messages",
                "description": "Parse Traceloop response message format (fallback)",
            },
            "gen_ai.response.text": {
                "target": "content",
                "transform": "direct",
                "description": "Response text content",
            },
            "gen_ai.response.content": {
                "target": "content",
                "transform": "direct",
                "description": "Response content",
            },
            "gen_ai.response.finish_reason": {
                "target": "finish_reason",
                "transform": "direct",
                "description": "Completion finish reason",
            },
            "gen_ai.response.id": {
                "target": "id",
                "transform": "direct",
                "description": "Response ID",
            },
            "gen_ai.response.function_calls": {
                "target": "function_calls",
                "transform": "direct",
                "description": "Function calls in response",
            },
            "gen_ai.response.tool_calls": {
                "target": "tool_calls",
                "transform": "direct",
                "description": "Tool calls in response",
            },
        },
    },
    # Config mapping - how to extract config from Traceloop attributes
    "config_mapping": {
        "target_schema": "llm_config",
        "mappings": {
            "gen_ai.request.model": {
                "target": "model",
                "transform": "direct",
                "description": "Model name",
            },
            "gen_ai.system": {
                "target": "provider",
                "transform": "direct",
                "description": "LLM system/provider",
            },
            "gen_ai.request.temperature": {
                "target": "temperature",
                "transform": "direct",
                "description": "Temperature parameter",
            },
            "gen_ai.request.max_tokens": {
                "target": "max_completion_tokens",
                "transform": "direct",
                "description": "Maximum tokens",
            },
            "gen_ai.request.top_p": {
                "target": "top_p",
                "transform": "direct",
                "description": "Top-p parameter",
            },
            "gen_ai.request.frequency_penalty": {
                "target": "frequency_penalty",
                "transform": "direct",
                "description": "Frequency penalty",
            },
            "gen_ai.request.presence_penalty": {
                "target": "presence_penalty",
                "transform": "direct",
                "description": "Presence penalty",
            },
            "gen_ai.request.stop_sequences": {
                "target": "stop",
                "transform": "direct",
                "description": "Stop sequences",
            },
            "gen_ai.request.seed": {
                "target": "seed",
                "transform": "direct",
                "description": "Random seed",
            },
        },
        "defaults": {"headers": "None", "is_streaming": False},
    },
    # Metadata mapping - how to extract metadata from Traceloop attributes
    "metadata_mapping": {
        "target_schema": "llm_metadata",
        "mappings": {
            "gen_ai.usage.prompt_tokens": {
                "target": "prompt_tokens",
                "transform": "direct",
                "description": "Prompt token count",
            },
            "gen_ai.usage.completion_tokens": {
                "target": "completion_tokens",
                "transform": "direct",
                "description": "Completion token count",
            },
            "gen_ai.usage.total_tokens": {
                "target": "total_tokens",
                "transform": "direct",
                "description": "Total token count",
            },
            "gen_ai.response.model": {
                "target": "response_model",
                "transform": "direct",
                "description": "Response model name",
            },
            "gen_ai.openai.api_base": {
                "target": "gen_ai.openai.api_base",
                "transform": "direct",
                "description": "OpenAI API base URL",
            },
            "gen_ai.operation.name": {
                "target": "operation_name",
                "transform": "direct",
                "description": "Operation name",
            },
            "gen_ai.request.type": {
                "target": "llm.request.type",
                "transform": "direct",
                "description": "Request type",
            },
        },
        "defaults": {"llm.request.type": "chat"},
    },
    # Transform functions - how to process attribute values (using generic transforms)
    "transforms": {
        "parse_flattened_messages": {
            "description": "Parse flattened message format (generic for any provider)",
            "implementation": "generic_message_parser.parse_flattened_messages",
        },
        "extract_content_from_flattened": {
            "description": "Extract content from flattened attributes (generic)",
            "implementation": "generic_extractor.extract_content_from_flattened",
        },
        "extract_role_from_flattened": {
            "description": "Extract role from flattened attributes (generic)",
            "implementation": "generic_extractor.extract_role_from_flattened",
        },
        "extract_finish_reason_from_json": {
            "description": "Extract finish_reason from JSON response (generic)",
            "implementation": "generic_extractor.extract_finish_reason_from_json",
        },
        "extract_content_from_messages": {
            "description": "Extract content from message list (generic)",
            "implementation": "generic_extractor.extract_content_from_messages",
        },
    },
    # Priority and compatibility
    "priority": 85,  # High priority for Traceloop (migration support)
    "compatible_versions": ["0.45.0", "0.46.0", "0.46.1", "0.46.2"],
    "deprecated": False,
    # Validation rules
    "validation": {
        "required_for_detection": ["gen_ai.request.model", "gen_ai.system"],
        "mutually_exclusive": [],
        "dependencies": {
            "gen_ai.usage.total_tokens": [
                "gen_ai.usage.prompt_tokens",
                "gen_ai.usage.completion_tokens",
            ]
        },
    },
}
