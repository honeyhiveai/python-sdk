"""OpenLit Semantic Convention Definition v1.0.0.

Based on official OpenLit semantic conventions from:
https://github.com/openlit/openlit/blob/2f07f37f41ad1834048e27e49e08bb7577502c7c/sdk/python/src/openlit/semcov/__init__.py#L11

This definition contains the complete mapping specification for OpenLit
gen_ai.* attributes to HoneyHive schema, with focus on usage patterns.
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
    "provider": "openlit",
    "version": "1.0.0",
    "source_url": "https://github.com/openlit/openlit/blob/2f07f37f41ad1834048e27e49e08bb7577502c7c/sdk/python/src/openlit/semcov/__init__.py#L11",
    "description": "OpenLit semantic conventions with focus on usage tracking and gen_ai.* attributes",
    # Detection patterns - attributes that identify this convention
    "detection_patterns": {
        "required_prefixes": ["gen_ai."],
        "signature_attributes": [
            "gen_ai.usage.input_tokens",
            "gen_ai.usage.output_tokens",
            "gen_ai.request.model",
        ],
        "unique_attributes": [
            "gen_ai.usage.input_tokens",  # OpenLit uses input_tokens vs prompt_tokens
            "gen_ai.usage.output_tokens",  # OpenLit uses output_tokens vs completion_tokens
        ],
    },
    # Input mapping - how to extract inputs from OpenLit attributes
    "input_mapping": {
        "target_schema": "chat_history",
        "mappings": {
            "gen_ai.request.messages.*": {
                "target": "chat_history",
                "transform": "parse_flattened_messages",
                "description": "Parse message format (generic for any provider)",
            },
            "gen_ai.request.system_prompt": {
                "target": "system_prompt",
                "transform": "direct",
                "description": "System prompt content",
            },
            "gen_ai.request.prompt": {
                "target": "prompt",
                "transform": "direct",
                "description": "User prompt",
            },
            "gen_ai.input.text": {
                "target": "input_text",
                "transform": "direct",
                "description": "Input text content",
            },
            "gen_ai.input.messages": {
                "target": "input_messages",
                "transform": "direct",
                "description": "Input messages",
            },
        },
        "fallback_chat_history": {
            "description": "Create chat_history from available inputs if not structured",
            "sources": [
                "gen_ai.request.system_prompt",
                "gen_ai.request.prompt",
                "gen_ai.input.text",
            ],
        },
    },
    # Output mapping - how to extract outputs from OpenLit attributes
    "output_mapping": {
        "target_schema": "content_finish_reason_role",
        "mappings": {
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
            "gen_ai.output.text": {
                "target": "output_text",
                "transform": "direct",
                "description": "Output text",
            },
        },
        "defaults": {"role": "assistant"},  # Default role for responses
    },
    # Config mapping - how to extract config from OpenLit attributes
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
        },
        "defaults": {"headers": "None", "is_streaming": False},
    },
    # Metadata mapping - how to extract metadata from OpenLit attributes
    "metadata_mapping": {
        "target_schema": "llm_metadata",
        "mappings": {
            "gen_ai.usage.input_tokens": {
                "target": "prompt_tokens",  # Map to standard prompt_tokens
                "transform": "direct",
                "description": "Input token count (mapped to prompt_tokens)",
            },
            "gen_ai.usage.output_tokens": {
                "target": "completion_tokens",  # Map to standard completion_tokens
                "transform": "direct",
                "description": "Output token count (mapped to completion_tokens)",
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
            "gen_ai.system": {
                "target": "system",
                "transform": "direct",
                "description": "System information",
            },
        },
        "computed_fields": {
            "total_tokens": {
                "description": "Compute total if not provided",
                "formula": "gen_ai.usage.input_tokens + gen_ai.usage.output_tokens",
            }
        },
        "defaults": {"llm.request.type": "chat"},
    },
    # Transform functions - how to process attribute values (using generic transforms)
    "transforms": {
        "parse_flattened_messages": {
            "description": "Parse flattened message format (generic for any provider)",
            "implementation": "generic_message_parser.parse_flattened_messages",
        },
        "direct": {
            "description": "Return value as-is (no transformation)",
            "implementation": "generic_transformer.direct",
        },
    },
    # Priority and compatibility
    "priority": 75,  # Medium-high priority for OpenLit
    "compatible_versions": ["0.9.0", "1.0.0", "1.1.0"],
    "deprecated": False,
    # Validation rules
    "validation": {
        "required_for_detection": ["gen_ai.usage.input_tokens", "gen_ai.request.model"],
        "mutually_exclusive": [],
        "dependencies": {},
        "computed_validation": {
            "total_tokens_consistency": "gen_ai.usage.total_tokens == gen_ai.usage.input_tokens + gen_ai.usage.output_tokens"
        },
    },
}
