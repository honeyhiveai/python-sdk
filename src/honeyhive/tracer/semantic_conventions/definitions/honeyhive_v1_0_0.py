"""HoneyHive Native Semantic Convention Definition v1.0.0.

This definition contains the complete mapping specification for HoneyHive
native honeyhive_* attributes to HoneyHive schema, based on main branch
compatibility analysis and production usage patterns.
"""

# pylint: disable=line-too-long
# Justification: DSL configuration files contain long descriptive strings and URLs
# that should not be broken for readability and maintainability

# pylint: disable=unused-import
# Justification: Type imports are used for static type checking and IDE support
# even if not used at runtime in configuration files

from typing import Any, Dict, List

# Convention metadata
CONVENTION_DEFINITION = {
    "provider": "honeyhive",
    "version": "1.0.0",
    "source_url": "https://github.com/honeyhiveai/python-sdk",
    "description": "HoneyHive native semantic conventions using honeyhive_* attributes",
    # Detection patterns - attributes that identify this convention
    "detection_patterns": {
        "required_prefixes": ["honeyhive_", "honeyhive."],
        "signature_attributes": [
            "honeyhive_event_type",
            "honeyhive_session_id",
            "honeyhive.session_id",
        ],
        "unique_attributes": [
            "honeyhive_inputs",
            "honeyhive_outputs",
            "honeyhive_config",
            "honeyhive_metadata",
        ],
    },
    # Input mapping - how to extract inputs from HoneyHive attributes
    "input_mapping": {
        "target_schema": "flexible",
        "mappings": {
            "honeyhive_inputs": {
                "target": "*",
                "transform": "parse_json_or_direct",
                "description": "Direct honeyhive inputs (JSON or dict)",
            },
            "honeyhive_inputs.*": {
                "target": "*",
                "transform": "nested_attribute_extraction",
                "description": "Nested honeyhive input attributes",
            },
            "honeyhive_inputs._params_.*": {
                "target": "parameters.*",
                "transform": "parameter_extraction",
                "description": "Main branch @trace decorator parameters",
            },
        },
    },
    # Output mapping - how to extract outputs from HoneyHive attributes
    "output_mapping": {
        "target_schema": "flexible",
        "mappings": {
            "honeyhive_outputs": {
                "target": "*",
                "transform": "parse_json_or_direct",
                "description": "Direct honeyhive outputs (JSON or dict)",
            },
            "honeyhive_outputs.*": {
                "target": "*",
                "transform": "nested_attribute_extraction",
                "description": "Nested honeyhive output attributes",
            },
        },
    },
    # Config mapping - how to extract config from HoneyHive attributes
    "config_mapping": {
        "target_schema": "flexible",
        "mappings": {
            "honeyhive_config": {
                "target": "*",
                "transform": "parse_json_or_direct",
                "description": "Direct honeyhive config (JSON or dict)",
            },
            "honeyhive_model": {
                "target": "model",
                "transform": "direct",
                "description": "Model name",
            },
            "honeyhive_provider": {
                "target": "provider",
                "transform": "direct",
                "description": "Provider name",
            },
            "honeyhive_temperature": {
                "target": "temperature",
                "transform": "direct",
                "description": "Temperature parameter",
            },
            "honeyhive_max_tokens": {
                "target": "max_completion_tokens",
                "transform": "direct",
                "description": "Maximum tokens",
            },
            "honeyhive_top_p": {
                "target": "top_p",
                "transform": "direct",
                "description": "Top-p parameter",
            },
            "honeyhive_frequency_penalty": {
                "target": "frequency_penalty",
                "transform": "direct",
                "description": "Frequency penalty",
            },
            "honeyhive_presence_penalty": {
                "target": "presence_penalty",
                "transform": "direct",
                "description": "Presence penalty",
            },
            "honeyhive_stop": {
                "target": "stop",
                "transform": "direct",
                "description": "Stop sequences",
            },
            "honeyhive_seed": {
                "target": "seed",
                "transform": "direct",
                "description": "Random seed",
            },
            "honeyhive_best_of": {
                "target": "best_of",
                "transform": "direct",
                "description": "Best of parameter",
            },
            "honeyhive_logit_bias": {
                "target": "logit_bias",
                "transform": "direct",
                "description": "Logit bias",
            },
            "honeyhive_user": {
                "target": "user",
                "transform": "direct",
                "description": "User identifier",
            },
        },
        "exclusions": [
            "honeyhive_prompt_tokens",
            "honeyhive_completion_tokens",
            "honeyhive_total_tokens",
        ],
    },
    # Metadata mapping - how to extract metadata from HoneyHive attributes
    "metadata_mapping": {
        "target_schema": "flexible",
        "mappings": {
            "honeyhive_metadata": {
                "target": "*",
                "transform": "parse_json_or_direct",
                "description": "Direct honeyhive metadata (JSON or dict)",
            },
            "honeyhive_metrics": {
                "target": "metrics",
                "transform": "parse_json_or_direct",
                "description": "Metrics data",
            },
            "honeyhive_feedback": {
                "target": "feedback",
                "transform": "parse_json_or_direct",
                "description": "Feedback data",
            },
            "honeyhive_error": {
                "target": "error",
                "transform": "error_message_extraction",
                "description": "Error information",
            },
            "honeyhive_prompt_tokens": {
                "target": "usage.prompt_tokens",
                "transform": "direct",
                "description": "Prompt token count",
            },
            "honeyhive_completion_tokens": {
                "target": "usage.completion_tokens",
                "transform": "direct",
                "description": "Completion token count",
            },
            "honeyhive_total_tokens": {
                "target": "usage.total_tokens",
                "transform": "direct",
                "description": "Total token count",
            },
            "honeyhive_metadata.*": {
                "target": "*",
                "transform": "nested_attribute_extraction",
                "description": "Nested metadata attributes",
            },
        },
    },
    # Context mapping - special HoneyHive context attributes
    "context_mapping": {
        "honeyhive_session_id": {
            "target": "session_id",
            "dual_mapping": [
                "honeyhive.session_id",
                "traceloop.association.properties.session_id",
            ],
            "description": "Session ID with dual mapping for backend compatibility",
        },
        "honeyhive.session_id": {
            "target": "session_id",
            "dual_mapping": [
                "honeyhive.session_id",
                "traceloop.association.properties.session_id",
            ],
            "description": "Session ID from span attributes",
        },
        "honeyhive_project": {
            "target": "project",
            "dual_mapping": [
                "honeyhive.project",
                "traceloop.association.properties.project",
            ],
            "description": "Project name with dual mapping",
        },
        "honeyhive.project": {
            "target": "project",
            "dual_mapping": [
                "honeyhive.project",
                "traceloop.association.properties.project",
            ],
            "description": "Project from span attributes",
        },
        "honeyhive_source": {
            "target": "source",
            "dual_mapping": [
                "honeyhive.source",
                "traceloop.association.properties.source",
            ],
            "description": "Source with dual mapping",
        },
        "honeyhive.source": {
            "target": "source",
            "dual_mapping": [
                "honeyhive.source",
                "traceloop.association.properties.source",
            ],
            "description": "Source from span attributes",
        },
        "honeyhive_parent_id": {
            "target": "parent_id",
            "dual_mapping": [
                "honeyhive.parent_id",
                "traceloop.association.properties.parent_id",
            ],
            "description": "Parent ID with dual mapping",
        },
        "honeyhive.parent_id": {
            "target": "parent_id",
            "dual_mapping": [
                "honeyhive.parent_id",
                "traceloop.association.properties.parent_id",
            ],
            "description": "Parent ID from span attributes",
        },
    },
    # Transform functions - how to process attribute values
    "transforms": {
        "parse_json_or_direct": {
            "description": "Parse JSON string or use direct value",
            "implementation": "json_or_direct_parser",
        },
        "nested_attribute_extraction": {
            "description": "Extract nested attribute values",
            "implementation": "nested_extractor",
        },
        "parameter_extraction": {
            "description": "Extract @trace decorator parameters",
            "implementation": "parameter_extractor",
        },
        "error_message_extraction": {
            "description": "Extract error message from various formats",
            "implementation": "error_extractor",
        },
    },
    # Enrichment capability - HoneyHive native can enrich other conventions
    "enrichment": {
        "enabled": True,
        "description": "HoneyHive native processing enriches data from other conventions",
        "supported_conventions": ["openinference", "traceloop", "openlit"],
        "enrichment_strategy": "honeyhive_first",
        "precedence": "honeyhive_values_take_priority",
    },
    # Priority and compatibility
    "priority": 100,  # Highest priority - HoneyHive native always processes first
    "compatible_versions": ["1.0.0"],
    "deprecated": False,
    # Validation rules
    "validation": {
        "required_for_detection": ["honeyhive_event_type"],
        "mutually_exclusive": [],
        "dependencies": {},
        "dual_mapping_validation": {
            "description": "Ensure dual mapping attributes are set correctly",
            "required_mappings": [
                "honeyhive.session_id -> traceloop.association.properties.session_id",
                "honeyhive.project -> traceloop.association.properties.project",
                "honeyhive.source -> traceloop.association.properties.source",
                "honeyhive.parent_id -> traceloop.association.properties.parent_id",
            ],
        },
    },
}
