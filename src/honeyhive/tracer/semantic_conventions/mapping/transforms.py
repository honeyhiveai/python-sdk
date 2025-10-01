"""Transform functions for semantic convention mapping.

This module contains all data transformation functions used by the rule engine
to convert raw OpenTelemetry attributes into the HoneyHive event schema format.
"""

# pylint: disable=unused-argument  # Arguments needed for consistent interface

import json
from typing import Any, Dict, List, Optional, Tuple

from ....utils.logger import safe_log


class TransformRegistry:  # pylint: disable=too-few-public-methods
    """Registry of transform functions for semantic convention mapping.

    This class provides a centralized location for all transform functions,
    using O(1) dictionary lookups instead of O(n) elif chains for scalability.
    """

    def __init__(self) -> None:
        """Initialize the transform registry with O(1) dictionary lookup.

        All transforms are generic and reusable across providers.
        Provider-specific logic is handled through DSL configuration.
        """
        self._transforms = {
            # Core transforms
            "direct": self._direct,
            # Message parsing (generic)
            "parse_messages": self._parse_messages,
            "parse_prompts": self._parse_messages,  # Same logic
            "parse_json_messages": self._parse_json_messages,
            "parse_flattened_messages": self._parse_flattened_messages,
            # Content extraction (generic)
            "extract_content_from_messages": self._extract_content_from_messages,
            "extract_role_from_messages": self._extract_role_from_messages,
            "extract_content_from_flattened": self._extract_content_from_flattened,
            "extract_role_from_flattened": self._extract_role_from_flattened,
            "extract_content_from_json": self._extract_content_from_json,
            "extract_role_from_json": self._extract_role_from_json,
            "extract_finish_reason_from_json": self._extract_finish_reason_from_json,
            # Role setting
            "set_assistant_role": self._set_assistant_role,
            "set_user_role": self._set_user_role,
            "set_system_role": self._set_system_role,
            # Message creation
            "create_system_message": self._create_system_message,
            "create_user_message": self._create_user_message,
            "create_assistant_message": self._create_assistant_message,
            # JSON utilities
            "parse_json_or_direct": self._parse_json_or_direct,
            "serialize_to_json": self._serialize_to_json,
            # HoneyHive native transforms
            "nested_attribute_extraction": self._nested_attribute_extraction,
            "parameter_extraction": self._parameter_extraction,
            "error_message_extraction": self._error_message_extraction,
        }

    def apply_transform(
        self, transform: str, value: Any, attributes: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Apply a transformation function to a value using O(1) dictionary lookup.

        Args:
            transform: Name of the transformation function
            value: Value to transform
            attributes: All span attributes for context (optional)

        Returns:
            Transformed value
        """
        if attributes is None:
            attributes = {}

        try:
            # O(1) dictionary lookup instead of O(n) elif chain
            transform_func = self._transforms.get(transform)
            if transform_func:
                # Handle methods that don't accept attributes parameter
                try:
                    return transform_func(value, attributes)
                except TypeError:
                    # Fallback for methods with old signature
                    return transform_func(value)
            else:
                safe_log(None, "warning", f"Unknown transform function: {transform}")
                return value

        except Exception as e:
            safe_log(None, "warning", f"Transform {transform} failed: {e}")
            return value

    # === CORE TRANSFORMS ===

    def _direct(self, value: Any, attributes: Optional[Dict[str, Any]] = None) -> Any:
        """Return value as-is (no transformation)."""
        return value

    # === MESSAGE PARSING (GENERIC) ===

    def _parse_messages(
        self, value: Any, attributes: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, str]]:
        """Parse message data into chat_history format (generic for all providers)."""
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return [
                        self._normalize_message(msg)
                        for msg in parsed
                        if isinstance(msg, dict)
                    ]
                if isinstance(parsed, dict):
                    return [self._normalize_message(parsed)]
            except (json.JSONDecodeError, TypeError):
                return [{"role": "user", "content": str(value)}]
        elif isinstance(value, list):
            return [
                self._normalize_message(msg) for msg in value if isinstance(msg, dict)
            ]
        elif isinstance(value, dict):
            return [self._normalize_message(value)]
        return [{"role": "user", "content": str(value)}] if value is not None else []

    def _normalize_message(self, msg: Dict[str, Any]) -> Dict[str, str]:
        """Normalize message format to handle both direct and nested formats."""
        # Handle OpenInference format:
        # {"message.role": "user", "message.content": "..."}
        if "message.role" in msg and "message.content" in msg:
            return {
                "role": str(msg.get("message.role", "user")),
                "content": str(msg.get("message.content", "")),
            }
        # Handle standard format: {"role": "user", "content": "..."}
        return {
            "role": str(msg.get("role", "user")),
            "content": str(msg.get("content", "")),
        }

    def _parse_json_messages(
        self, value: Any, attributes: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, str]]:
        """Parse JSON string containing messages."""
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                return self._parse_messages(parsed, attributes)
            except (json.JSONDecodeError, TypeError):
                return [{"role": "user", "content": str(value)}]
        return self._parse_messages(value, attributes)

    def _parse_flattened_messages(
        self,
        flattened_attrs: Dict[str, Any],
        attributes: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, str]]:
        """Parse flattened message attributes to chat history format (generic)."""
        messages: Dict[int, Dict[str, str]] = {}

        for key, value in flattened_attrs.items():
            index, field = self._extract_index_and_field(key)
            if index is not None and field in ["role", "content"]:
                if index not in messages:
                    messages[index] = {}
                messages[index][field] = value

        return [messages[i] for i in sorted(messages.keys())]

    def _extract_index_and_field(self, key: str) -> Tuple[Optional[int], Optional[str]]:
        """Extract numeric index and field from flattened attribute key."""
        # Extract index and field from patterns like:
        # - "messages.0.role" or "prompt.1.content" (Traceloop format)
        # - "llm.input_messages.0.message.role" (OpenInference format)
        parts = key.split(".")
        if len(parts) < 3:
            return None, None

        try:
            # Find the numeric index
            for i, part in enumerate(parts):
                if part.isdigit():
                    index = int(part)
                    field = self._find_field_in_remaining_parts(parts[i + 1 :])
                    return index, field
        except ValueError:
            pass

        return None, None

    def _find_field_in_remaining_parts(
        self, remaining_parts: List[str]
    ) -> Optional[str]:
        """Find role/content field in remaining parts of the key."""
        # Look for role/content in remaining parts
        for remaining_part in remaining_parts:
            if remaining_part in ["role", "content"]:
                return remaining_part

        # Also check for message.role/message.content pattern (OpenInference)
        if len(remaining_parts) >= 2:
            if remaining_parts[0] == "message" and remaining_parts[1] in [
                "role",
                "content",
            ]:
                return remaining_parts[1]

        return None

    # === CONTENT EXTRACTION (GENERIC) ===

    def _extract_content_from_messages(
        self, value: Any, attributes: Optional[Dict[str, Any]] = None
    ) -> str:
        """Extract content from message list (works with any provider format)."""
        messages = self._parse_messages(value, attributes)
        for msg in messages:
            if msg.get("role") == "assistant" and msg.get("content"):
                return str(msg["content"])
        # Fallback: return content from first message
        if messages and messages[0].get("content"):
            return str(messages[0]["content"])
        return ""

    def _extract_role_from_messages(
        self, value: Any, attributes: Optional[Dict[str, Any]] = None
    ) -> str:
        """Extract role from message list (works with any provider format)."""
        messages = self._parse_messages(value, attributes)
        if messages and messages[0].get("role"):
            return str(messages[0]["role"])
        return "assistant"

    def _extract_content_from_flattened(
        self,
        flattened_attrs: Dict[str, Any],
        attributes: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Extract content from flattened attributes (generic)."""
        for key, value in flattened_attrs.items():
            if key.endswith(".content"):
                return str(value)
        return ""

    def _extract_role_from_flattened(
        self,
        flattened_attrs: Dict[str, Any],
        attributes: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Extract role from flattened attributes (generic)."""
        for key, value in flattened_attrs.items():
            if key.endswith(".role"):
                return str(value)
        return "assistant"

    def _extract_content_from_json(
        self, value: Any, attributes: Optional[Dict[str, Any]] = None
    ) -> str:
        """Extract content from JSON response (generic)."""
        if isinstance(value, str):
            try:
                response = json.loads(value)
                if isinstance(response, dict):
                    # Try OpenAI format
                    if (
                        "choices" in response
                        and isinstance(response["choices"], list)
                        and response["choices"]
                    ):
                        message = response["choices"][0].get("message", {})
                        return str(message.get("content", ""))
                    # Try direct content
                    if "content" in response:
                        return str(response["content"])
            except (json.JSONDecodeError, KeyError, IndexError):
                pass
        return str(value) if value else ""

    def _extract_role_from_json(
        self, value: Any, attributes: Optional[Dict[str, Any]] = None
    ) -> str:
        """Extract role from JSON response (generic)."""
        if isinstance(value, str):
            try:
                response = json.loads(value)
                if isinstance(response, dict):
                    # Try OpenAI format
                    if (
                        "choices" in response
                        and isinstance(response["choices"], list)
                        and response["choices"]
                    ):
                        message = response["choices"][0].get("message", {})
                        return str(message.get("role", "assistant"))
                    # Try direct role
                    if "role" in response:
                        return str(response["role"])
            except (json.JSONDecodeError, KeyError, IndexError):
                pass
        return "assistant"

    def _extract_finish_reason_from_json(
        self, value: Any, attributes: Optional[Dict[str, Any]] = None
    ) -> str:
        """Extract finish_reason from JSON response (generic)."""
        if isinstance(value, str):
            try:
                response = json.loads(value)
                if isinstance(response, dict):
                    # Try OpenAI format
                    if (
                        "choices" in response
                        and isinstance(response["choices"], list)
                        and response["choices"]
                    ):
                        return str(response["choices"][0].get("finish_reason", "stop"))
                    # Try direct finish_reason
                    if "finish_reason" in response:
                        return str(response["finish_reason"])
            except (json.JSONDecodeError, KeyError, IndexError):
                pass
        return "stop"

    # === ROLE SETTING ===

    def _set_assistant_role(
        self, value: Any, attributes: Optional[Dict[str, Any]] = None
    ) -> str:
        """Return 'assistant' role."""
        return "assistant"

    def _set_user_role(
        self, value: Any, attributes: Optional[Dict[str, Any]] = None
    ) -> str:
        """Return 'user' role."""
        return "user"

    def _set_system_role(
        self, value: Any, attributes: Optional[Dict[str, Any]] = None
    ) -> str:
        """Return 'system' role."""
        return "system"

    # === MESSAGE CREATION ===

    def _create_system_message(
        self, value: Any, attributes: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, str]]:
        """Create a system message."""
        return [{"role": "system", "content": str(value)}]

    def _create_user_message(
        self, value: Any, attributes: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, str]]:
        """Create a user message."""
        return [{"role": "user", "content": str(value)}]

    def _create_assistant_message(
        self, value: Any, attributes: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, str]]:
        """Create an assistant message."""
        return [{"role": "assistant", "content": str(value)}]

    # === JSON UTILITIES ===

    def _parse_json_or_direct(
        self, value: Any, attributes: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Parse JSON string or return value directly."""
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        return value

    def _serialize_to_json(
        self, value: Any, attributes: Optional[Dict[str, Any]] = None
    ) -> str:
        """Serialize value to JSON string."""
        try:
            return json.dumps(value)
        except (TypeError, ValueError):
            return str(value)

    # === HONEYHIVE NATIVE TRANSFORMS ===

    def _nested_attribute_extraction(
        self, value: Any, attributes: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Extract nested attribute values (HoneyHive native)."""
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return {"value": value}
        return {"value": str(value)}

    def _parameter_extraction(
        self, value: Any, attributes: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Extract parameter values from @trace decorator (HoneyHive native)."""
        if isinstance(value, dict):
            # Extract parameters from nested structure
            return {k.replace("_params_", ""): v for k, v in value.items()}
        return value

    def _error_message_extraction(
        self, value: Any, attributes: Optional[Dict[str, Any]] = None
    ) -> str:
        """Extract error message from various error formats (HoneyHive native)."""
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            # Try common error message fields
            for field in ["message", "error", "description", "detail"]:
                if field in value:
                    return str(value[field])
            return str(value)
        if hasattr(value, "message"):
            return str(value.message)
        return str(value)

# No global instance - each tracer instance creates its own for multi-instance
# architecture
