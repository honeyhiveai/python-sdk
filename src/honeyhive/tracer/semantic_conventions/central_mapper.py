"""Centralized HoneyHive Event Mapping System.

This module provides a unified mapping system that all semantic convention
extractors use to ensure consistent output format. Based on analysis of 196
production events from Deep Research Prod.

All extractors (HoneyHive Native, OpenInference, Traceloop, OpenLit) use this
centralized system to produce events that conform to the canonical schema.
"""

from typing import Any, Dict, List, Optional

from ...utils.logger import safe_log
from .discovery import ConventionDefinition, get_discovery_instance
from .mapping import RuleApplier, RuleEngine
from .schema import EventType, HoneyHiveEventSchema


class CentralEventMapper:
    """Centralized event mapping system.

    This class provides standardized methods for mapping semantic convention
    data to the canonical HoneyHive event schema. All extractors use this
    system to ensure consistent output format.
    """

    def __init__(self) -> None:
        """Initialize the central mapper."""
        self.discovery = get_discovery_instance()
        self.rule_engine = RuleEngine()
        self.rule_applier = RuleApplier()

        self.schema_stats: Dict[str, Any] = {
            "events_mapped": 0,
            "validation_errors": 0,
            "schema_types_used": {},
        }

    def map_attributes_to_schema(
        self, attributes: Dict[str, Any], event_type: str = "model"
    ) -> Dict[str, Any]:
        """Map OpenTelemetry attributes to HoneyHive event schema.

        This method replaces ConfigDrivenMapper.map_to_honeyhive_schema() and provides
        the main interface for dynamic semantic convention processing.

        Args:
            attributes: Source span attributes from OpenTelemetry
            event_type: Target event type (model, chain, tool, session)

        Returns:
            Mapped data in HoneyHive event schema format
        """
        try:
            # 1. Detect semantic convention using our detection logic
            detected_convention = self._detect_convention(attributes)

            safe_log(
                None,
                "debug",
                f"🔍 SEMANTIC CONVENTIONS: Detected {detected_convention} for "
                f"event_type {event_type} with {len(attributes)} attributes",
            )

            if not detected_convention or detected_convention == "unknown":
                # Return empty structure if no convention detected
                return {"inputs": {}, "outputs": {}, "config": {}, "metadata": {}}

            # 2. Get convention definition and create rules
            definition = self._get_definition_for_provider(detected_convention)
            if not definition:
                safe_log(
                    None,
                    "warning",
                    f"No definition found for detected convention: "
                    f"{detected_convention}",
                )
                return {"inputs": {}, "outputs": {}, "config": {}, "metadata": {}}

            # 3. Create mapping rules dynamically from definition
            rules = self.rule_engine.create_rules(definition)

            # 4. Apply rules to transform attributes
            mapped_data = self.rule_applier.apply_rules(attributes, rules, event_type)

            # 5. Update statistics
            self.schema_stats["events_mapped"] += 1
            self.schema_stats["schema_types_used"][event_type] = (
                self.schema_stats["schema_types_used"].get(event_type, 0) + 1
            )

            safe_log(
                None,
                "info",
                (
                    f"✅ SEMANTIC CONVENTIONS: Processed {detected_convention} "
                    f"event_type {event_type} - "
                    f"inputs: {len(mapped_data.get('inputs', {}))}, "
                    f"outputs: {len(mapped_data.get('outputs', {}))}"
                ),
            )

            return mapped_data

        except Exception as e:
            safe_log(
                None,
                "error",
                f"Semantic convention mapping failed for event_type {event_type}: {e}",
            )
            self.schema_stats["validation_errors"] += 1
            # Return empty structure on error
            return {"inputs": {}, "outputs": {}, "config": {}, "metadata": {}}

    def detect_convention(self, attributes: Dict[str, Any]) -> str:
        """Detect semantic convention from attributes (compatibility method).

        Args:
            attributes: Source span attributes

        Returns:
            Detected convention name or "unknown"
        """
        return self._detect_convention(attributes)

    def _detect_convention(self, attributes: Dict[str, Any]) -> str:
        """Detect semantic convention from span attributes.

        Args:
            attributes: Span attributes to analyze

        Returns:
            Provider name of detected convention or "unknown"
        """
        try:
            # Get all discovered definitions
            definitions = self.discovery.definitions

            # First pass: Check for unique attributes (most specific)
            for definition in definitions.values():
                if self._has_unique_attributes(attributes, definition):
                    safe_log(
                        None,
                        "debug",
                        f"🎯 Matched convention by unique attributes: "
                        f"{definition.provider} v{definition.version_string}",
                    )
                    return definition.provider

            # Second pass: Check general patterns (less specific)
            for definition in definitions.values():
                if self._matches_definition(attributes, definition):
                    safe_log(
                        None,
                        "debug",
                        f"🔍 Matched convention by patterns: "
                        f"{definition.provider} v{definition.version_string}",
                    )
                    return definition.provider

            safe_log(
                None,
                "debug",
                f"🔍 No convention matched for {len(attributes)} attributes",
            )
            return "unknown"

        except Exception as e:
            safe_log(None, "error", f"Convention detection failed: {e}")
            return "unknown"

    def _has_unique_attributes(
        self, attributes: Dict[str, Any], definition: ConventionDefinition
    ) -> bool:
        """Check if attributes contain unique attributes for a specific convention.

        Args:
            attributes: Span attributes to check
            definition: Convention definition to check unique attributes for

        Returns:
            True if any unique attributes are found
        """
        try:
            if not definition.definition_data:
                return False
            detection_patterns = definition.definition_data.get(
                "detection_patterns", {}
            )
            unique_attrs = detection_patterns.get("unique_attributes", [])

            if not unique_attrs:
                return False

            # Check if any unique attribute is present
            for unique_attr in unique_attrs:
                if unique_attr in attributes:
                    safe_log(
                        None,
                        "debug",
                        f"🎯 Found unique attribute '{unique_attr}' for "
                        f"{definition.provider}",
                    )
                    return True

            return False

        except Exception as e:
            safe_log(
                None,
                "warning",
                f"Error checking unique attributes for {definition.provider}: {e}",
            )
            return False

    def _matches_definition(
        self, attributes: Dict[str, Any], definition: ConventionDefinition
    ) -> bool:
        """Check if attributes match a convention definition's detection patterns.

        Args:
            attributes: Span attributes to check
            definition: Convention definition to match against

        Returns:
            True if attributes match the definition's patterns
        """
        try:
            if not definition.definition_data:
                return False
            detection_patterns = definition.definition_data.get(
                "detection_patterns", {}
            )

            # Check required attributes
            required_attrs = detection_patterns.get("required_attributes", [])
            for required_attr in required_attrs:
                if required_attr not in attributes:
                    return False

            # Check signature attributes (at least one must be present)
            signature_attrs = detection_patterns.get("signature_attributes", [])
            if signature_attrs:
                has_signature = any(attr in attributes for attr in signature_attrs)
                if not has_signature:
                    return False

            # Check attribute patterns (at least one pattern must match)
            attribute_patterns = detection_patterns.get("attribute_patterns", [])
            if attribute_patterns:
                has_pattern_match = False
                for pattern in attribute_patterns:
                    if pattern.endswith("*"):
                        prefix = pattern[:-1]
                        if any(attr.startswith(prefix) for attr in attributes):
                            has_pattern_match = True
                            break
                    else:
                        if pattern in attributes:
                            has_pattern_match = True
                            break

                if not has_pattern_match:
                    return False

            return True

        except Exception as e:
            safe_log(
                None, "warning", f"Error matching definition {definition.provider}: {e}"
            )
            return False

    def _get_definition_for_provider(
        self, provider: str
    ) -> Optional[ConventionDefinition]:
        """Get the latest definition for a provider.

        Args:
            provider: Provider name (e.g., "traceloop", "openinference")

        Returns:
            Latest ConventionDefinition for the provider or None
        """
        try:
            # Get all definitions and find the latest for this provider
            definitions = self.discovery.definitions

            provider_definitions = [
                definition
                for definition in definitions.values()
                if definition.provider == provider
            ]

            if not provider_definitions:
                return None

            # Return the latest version (definitions are sorted by version desc)
            latest_definition = max(provider_definitions, key=lambda d: d.version)

            safe_log(
                None,
                "debug",
                f"🔍 Found definition: {provider} v{latest_definition.version_string}",
            )

            return latest_definition

        except Exception as e:
            safe_log(None, "error", f"Error getting definition for {provider}: {e}")
            return None

    def create_base_event(
        self, event_name: str, event_type: EventType, source: str = "python-sdk"
    ) -> Dict[str, Any]:
        """Create base event structure with all required fields.

        Args:
            event_name: Name of the event
            event_type: Type of event (model, chain, tool, session)
            source: Source of the event

        Returns:
            Base event dictionary with all required fields initialized
        """
        return {
            "event_name": event_name,
            "event_type": event_type.value,
            "source": source,
            "inputs": {},
            "outputs": {},
            "config": {},
            "metadata": {},
            # Additional fields (will be populated by span processor)
            "project_id": None,
            "event_id": None,
            "session_id": None,
            "parent_id": None,
            "children_ids": [],
            "error": None,
            "start_time": None,
            "end_time": None,
            "duration": None,
            "feedback": {},
            "metrics": {},
            "user_properties": {},
        }

    def map_llm_inputs(
        self,
        messages: Optional[List[Dict[str, Any]]] = None,
        prompts: Optional[List[Dict[str, Any]]] = None,
        system_message: Optional[str] = None,
        functions: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Map LLM inputs to standard chat_history format.

        Based on production analysis showing chat_history is the primary
        input format for successful LLM events (43 events).

        Args:
            messages: List of chat messages
            prompts: List of prompts (alternative format)
            system_message: System message to prepend
            functions: Function definitions for tool calls

        Returns:
            Standardized inputs dictionary
        """
        inputs = {}

        # Build chat_history from various input formats
        chat_history = []

        # Add system message if provided
        if system_message:
            chat_history.append({"role": "system", "content": system_message})

        # Process messages (primary format)
        if messages:
            for msg in messages:
                if isinstance(msg, dict):
                    # Normalize message format
                    normalized_msg = {
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", msg.get("text", "")),
                    }

                    # Preserve additional fields
                    for key, value in msg.items():
                        if key not in ["role", "content", "text"]:
                            normalized_msg[key] = value

                    chat_history.append(normalized_msg)

        # Process prompts (alternative format)
        elif prompts:
            for prompt in prompts:
                if isinstance(prompt, dict):
                    chat_history.append(
                        {
                            "role": prompt.get("role", "user"),
                            "content": prompt.get("content", str(prompt)),
                        }
                    )
                else:
                    chat_history.append({"role": "user", "content": str(prompt)})

        # Set chat_history if we have messages
        if chat_history:
            inputs["chat_history"] = chat_history

        # Add functions if provided (for tool calls)
        if functions:
            inputs["functions"] = functions

        return inputs

    def map_llm_outputs(
        self,
        content: Optional[str] = None,
        role: Optional[str] = None,
        *,
        finish_reason: Optional[str] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        response_id: Optional[str] = None,
        messages: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Map LLM outputs to standard format.

        Based on production analysis showing content|finish_reason|role
        is the primary output format for successful LLM events (49 events).

        Args:
            content: Response content
            role: Response role (usually "assistant")
            finish_reason: Completion reason ("stop", "tool_calls", etc.)
            tool_calls: Tool calls made by the model
            response_id: Response ID
            messages: Alternative message format

        Returns:
            Standardized outputs dictionary
        """
        outputs = {}

        # Extract content from messages if not provided directly
        if not content and messages:
            for msg in messages:
                if isinstance(msg, dict) and msg.get("role") == "assistant":
                    content = msg.get("content", "")
                    break

        # Set primary output fields (based on 49 successful events)
        if content is not None:
            outputs["content"] = content

        if role:
            outputs["role"] = role
        elif content is not None:
            outputs["role"] = "assistant"  # Default for LLM responses

        if finish_reason:
            outputs["finish_reason"] = finish_reason

        # Handle tool calls (13 events with tool calls)
        if tool_calls:
            for i, tool_call in enumerate(tool_calls):
                if isinstance(tool_call, dict):
                    outputs[f"tool_calls.{i}.id"] = str(tool_call.get("id", ""))
                    outputs[f"tool_calls.{i}.name"] = tool_call.get(
                        "name", tool_call.get("function", {}).get("name")
                    )
                    outputs[f"tool_calls.{i}.arguments"] = tool_call.get(
                        "arguments", tool_call.get("function", {}).get("arguments")
                    )

        # Add response ID if provided
        if response_id:
            outputs["id"] = response_id

        return outputs

    def map_llm_config(
        self,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        *,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        headers: Optional[str] = None,
        is_streaming: Optional[bool] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Map LLM configuration to standard format.

        Based on production analysis showing provider|model|headers|is_streaming
        is the standard config format for LLM events (62 events).

        Args:
            model: Model name
            provider: Provider name
            temperature: Temperature setting
            max_tokens: Maximum tokens
            headers: Request headers
            is_streaming: Whether streaming is enabled
            **kwargs: Additional configuration parameters

        Returns:
            Standardized config dictionary
        """
        config: Dict[str, Any] = {}

        # Core LLM config fields (based on 62 successful events)
        if provider:
            config["provider"] = provider

        if model:
            config["model"] = model

        if headers is not None:
            config["headers"] = headers
        elif provider:  # Default headers for LLM events
            config["headers"] = "None"

        if is_streaming is not None:
            config["is_streaming"] = is_streaming
        elif provider:  # Default streaming for LLM events
            config["is_streaming"] = False

        # Additional parameters
        if temperature is not None:
            config["temperature"] = temperature

        if max_tokens is not None:
            config["max_completion_tokens"] = max_tokens

        # Add any additional config parameters
        for key, value in kwargs.items():
            if key not in config and value is not None:
                config[key] = value

        return config

    def map_llm_metadata(
        self,
        scope: Optional[Dict[str, str]] = None,
        request_type: Optional[str] = None,
        *,
        api_base: Optional[str] = None,
        response_model: Optional[str] = None,
        system_fingerprint: Optional[str] = None,
        total_tokens: Optional[int] = None,
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Map LLM metadata to standard format.

        Based on production analysis of LLM metadata fields.

        Args:
            scope: Instrumentation scope information
            request_type: Type of LLM request ("chat", "completion", etc.)
            api_base: API base URL
            response_model: Response model name
            system_fingerprint: System fingerprint
            total_tokens: Total token count
            prompt_tokens: Prompt token count
            completion_tokens: Completion token count
            **kwargs: Additional metadata fields

        Returns:
            Standardized metadata dictionary
        """
        metadata: Dict[str, Any] = {}

        # Core metadata fields
        if scope:
            metadata["scope"] = scope

        if request_type:
            metadata["llm.request.type"] = request_type

        if api_base:
            metadata["gen_ai.openai.api_base"] = api_base

        if response_model:
            metadata["response_model"] = response_model

        if system_fingerprint:
            metadata["system_fingerprint"] = system_fingerprint

        # Token usage (critical for LLM events)
        if any([total_tokens, prompt_tokens, completion_tokens]):
            if total_tokens is not None:
                metadata["total_tokens"] = total_tokens
            if prompt_tokens is not None:
                metadata["prompt_tokens"] = prompt_tokens
            if completion_tokens is not None:
                metadata["completion_tokens"] = completion_tokens

        # Add additional metadata
        for key, value in kwargs.items():
            if key not in metadata and value is not None:
                metadata[key] = value

        return metadata

    def create_llm_event(
        self,
        event_name: str,
        source: str,
        *,
        messages: Optional[List[Dict[str, Any]]] = None,
        content: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Create a complete LLM event using centralized mapping.

        This is the primary method that extractors should use to create
        LLM events that conform to the canonical schema.

        Args:
            event_name: Name of the event
            source: Source of the event
            messages: Input messages
            content: Response content
            model: Model name
            provider: Provider name
            **kwargs: Additional parameters for inputs, outputs, config, metadata

        Returns:
            Complete event dictionary conforming to canonical schema
        """
        try:
            # Create base event
            event = self.create_base_event(event_name, EventType.MODEL, source)

            # Map inputs
            event["inputs"] = self.map_llm_inputs(
                messages=messages,
                prompts=kwargs.get("prompts"),
                system_message=kwargs.get("system_message"),
                functions=kwargs.get("functions"),
            )

            # Map outputs
            event["outputs"] = self.map_llm_outputs(
                content=content,
                role=kwargs.get("role"),
                finish_reason=kwargs.get("finish_reason"),
                tool_calls=kwargs.get("tool_calls"),
                response_id=kwargs.get("response_id"),
                messages=kwargs.get("output_messages"),
            )

            # Map config
            event["config"] = self.map_llm_config(
                model=model,
                provider=provider,
                temperature=kwargs.get("temperature"),
                max_tokens=kwargs.get("max_tokens"),
                headers=kwargs.get("headers"),
                is_streaming=kwargs.get("is_streaming"),
            )

            # Map metadata
            event["metadata"] = self.map_llm_metadata(
                scope=kwargs.get("scope"),
                request_type=kwargs.get("request_type", "chat"),
                api_base=kwargs.get("api_base"),
                response_model=kwargs.get("response_model"),
                system_fingerprint=kwargs.get("system_fingerprint"),
                total_tokens=kwargs.get("total_tokens"),
                prompt_tokens=kwargs.get("prompt_tokens"),
                completion_tokens=kwargs.get("completion_tokens"),
            )

            # Validate the event using Pydantic
            try:
                validated_event = HoneyHiveEventSchema(**event)
                # Convert back to dict for compatibility
                event = validated_event.model_dump()
            except Exception as validation_error:
                safe_log(
                    None, "warning", f"Pydantic validation error: {validation_error}"
                )
                self.schema_stats["validation_errors"] += 1
                # Continue with unvalidated event for graceful degradation

            self.schema_stats["events_mapped"] += 1
            self.schema_stats["schema_types_used"]["llm"] = (
                self.schema_stats["schema_types_used"].get("llm", 0) + 1
            )

            return event

        except Exception as e:
            safe_log(None, "error", f"Failed to create LLM event: {e}")
            # Return minimal valid event structure for graceful degradation
            return self.create_base_event(event_name, EventType.MODEL, source)

    def get_mapping_stats(self) -> Dict[str, Any]:
        """Get statistics about the mapping operations.

        Returns:
            Dictionary containing mapping statistics
        """
        return self.schema_stats.copy()


def get_central_mapper(
    cache_manager: Optional[Any] = None,
) -> Optional[CentralEventMapper]:
    """Get a central mapper instance for the given cache manager.

    This follows the multi-instance architecture pattern where each tracer instance
    has its own semantic convention processing components.

    Args:
        cache_manager: Cache manager from the tracer instance (for
            multi-instance isolation)

    Returns:
        CentralEventMapper instance or None if initialization fails
    """
    try:
        # Create a new instance for each tracer (multi-instance architecture)
        mapper = CentralEventMapper()
        safe_log(
            None,
            "debug",
            f"🔍 CENTRAL MAPPER: Created instance for tracer "
            f"{id(cache_manager) if cache_manager else 'unknown'}",
        )
        return mapper
    except Exception as e:
        safe_log(None, "error", f"Failed to create central mapper: {e}")
        return None
