"""
HoneyHive OpenTelemetry Span Exporter

This module provides a proper OpenTelemetry span exporter that sends spans
to the HoneyHive API in batches, following OTel best practices.
"""

from typing import Sequence, Optional, Dict, Any
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.sdk.trace import ReadableSpan
import logging
import json
import threading
from concurrent.futures import ThreadPoolExecutor


class HoneyHiveSpanExporter(SpanExporter):
    """
    OpenTelemetry span exporter that sends spans to HoneyHive API.
    
    This follows the proper OTel architecture where:
    1. SpanProcessor collects spans
    2. SpanExporter sends spans to external systems
    3. Batching and retry logic is handled by OTel framework
    """
    
    def __init__(
        self,
        api_key: str,
        server_url: str = "https://api.honeyhive.ai",
        timeout: int = 30,
        max_workers: int = 5,
        test_mode: bool = False,
        verbose: bool = False,
        min_span_duration_ms: float = 1.0,
        max_spans_per_batch: int = 100
    ):
        """
        Initialize HoneyHive span exporter.
        
        Args:
            api_key: HoneyHive API key
            server_url: HoneyHive server URL
            timeout: HTTP request timeout in seconds
            max_workers: Max concurrent HTTP requests
            test_mode: If True, skip actual HTTP calls (for testing)
            verbose: Enable verbose logging
        """
        self.api_key = api_key
        self.server_url = server_url
        self.timeout = timeout
        self.test_mode = test_mode
        self.verbose = verbose
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._logger = logging.getLogger(__name__)
        self._lock = threading.RLock()
        
        # Performance optimization parameters
        self.min_span_duration_ms = min_span_duration_ms
        self.max_spans_per_batch = max_spans_per_batch
        
        # Initialize HoneyHive SDK once (not per request)
        if not test_mode:
            try:
                from honeyhive.sdk import HoneyHive
                self._sdk = HoneyHive(
                    bearer_auth=api_key,
                    server_url=server_url
                )
                if verbose:
                    self._logger.info(f"HoneyHive span exporter initialized with server: {server_url}")
            except Exception as e:
                self._logger.error(f"Failed to initialize HoneyHive SDK: {e}")
                self._sdk = None
        else:
            self._sdk = None
            if verbose:
                self._logger.info("HoneyHive span exporter in test mode - no HTTP calls will be made")
    
    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """
        Export spans to HoneyHive with performance optimizations.
        
        This method is called by OpenTelemetry's BatchSpanProcessor
        with a batch of spans to export.
        
        Args:
            spans: Sequence of spans to export
            
        Returns:
            SpanExportResult indicating success or failure
        """
        if self.test_mode:
            if self.verbose:
                self._logger.debug(f"Test mode: Would export {len(spans)} spans to HoneyHive")
            return SpanExportResult.SUCCESS
        
        if not spans:
            return SpanExportResult.SUCCESS
        
        # Performance optimization: Filter spans based on duration
        filtered_spans = self._filter_spans_by_duration(spans)
        if not filtered_spans:
            if self.verbose:
                self._logger.debug("All spans filtered out due to duration threshold")
            return SpanExportResult.SUCCESS
        
        # Performance optimization: Limit batch size
        if len(filtered_spans) > self.max_spans_per_batch:
            if self.verbose:
                self._logger.debug(f"Limiting batch from {len(filtered_spans)} to {self.max_spans_per_batch} spans")
            filtered_spans = filtered_spans[:self.max_spans_per_batch]
        
        try:
            # Convert OTel spans to HoneyHive events
            events = []
            for span in filtered_spans:
                event = self._span_to_honeyhive_event(span)
                if event:
                    events.append(event)
            
            if not events:
                if self.verbose:
                    self._logger.debug("No HoneyHive events found in span batch")
                return SpanExportResult.SUCCESS
            
            # Send events to HoneyHive (batched)
            success = self._send_events(events)
            
            if self.verbose:
                status = "SUCCESS" if success else "FAILURE"
                self._logger.debug(f"Exported {len(events)} events to HoneyHive: {status}")
            
            return SpanExportResult.SUCCESS if success else SpanExportResult.FAILURE
            
        except Exception as e:
            self._logger.error(f"Failed to export spans to HoneyHive: {e}")
            return SpanExportResult.FAILURE
    
    def _span_to_honeyhive_event(self, span: ReadableSpan) -> Optional[Dict[str, Any]]:
        """
        Convert OpenTelemetry span to HoneyHive event format.
        
        Args:
            span: ReadableSpan to convert
            
        Returns:
            Dictionary representing HoneyHive event, or None if not a HoneyHive span
        """
        try:
            # Extract span attributes
            span_attributes = dict(span.attributes) if span.attributes else {}
            
            # Get session_id from span attributes
            session_id = span_attributes.get("honeyhive.session_id")
            if not session_id:
                # If no session_id, this might not be a HoneyHive span
                return None
            
            # Determine event type from span attributes
            raw_event_type = span_attributes.get("honeyhive_event_type", "tool")
            
            # Map session_start to a valid event type
            if raw_event_type == "session_start":
                event_type = "tool"  # Use 'tool' as the default for session events
            else:
                event_type = raw_event_type
            
            # Calculate duration from span start/end time (timestamps are in nanoseconds)
            duration = None
            if hasattr(span, 'start_time') and hasattr(span, 'end_time'):
                # Convert nanoseconds to milliseconds
                duration = (span.end_time - span.start_time) / 1_000_000
            
            # Extract and structure metadata from span attributes
            metadata = self._extract_attributes_by_prefix(span_attributes, "honeyhive_metadata.")
            inputs = self._extract_attributes_by_prefix(span_attributes, "honeyhive_inputs.")
            outputs = self._extract_attributes_by_prefix(span_attributes, "honeyhive_outputs.")
            feedback = self._extract_attributes_by_prefix(span_attributes, "honeyhive_feedback.")
            metrics = self._extract_attributes_by_prefix(span_attributes, "honeyhive_metrics.")
            config = self._extract_attributes_by_prefix(span_attributes, "honeyhive_config.")
            user_properties = self._extract_attributes_by_prefix(span_attributes, "honeyhive_user_properties.")
            
            # Also check for direct attributes and JSON attributes
            if not metadata:
                if "honeyhive_metadata" in span_attributes:
                    metadata = span_attributes.get("honeyhive_metadata") or {}
                elif "honeyhive_metadata_json" in span_attributes:
                    # Parse JSON metadata
                    try:
                        metadata = json.loads(span_attributes.get("honeyhive_metadata_json", "{}"))
                    except (json.JSONDecodeError, TypeError):
                        metadata = {}
            
            if not inputs:
                if "honeyhive_inputs" in span_attributes:
                    inputs = span_attributes.get("honeyhive_inputs") or {}
                elif "honeyhive_inputs_json" in span_attributes:
                    # Parse JSON inputs
                    try:
                        inputs = json.loads(span_attributes.get("honeyhive_inputs_json", "{}"))
                    except (json.JSONDecodeError, TypeError):
                        inputs = {}
            
            if not outputs and "honeyhive_outputs" in span_attributes:
                outputs = span_attributes.get("honeyhive_outputs") or {}
            
            # Create HoneyHive event
            event = {
                "event_type": event_type,
                "event_name": span.name,
                "session_id": session_id,
                "project": span_attributes.get("honeyhive.project", "unknown"),
                "source": span_attributes.get("honeyhive.source", "unknown"),
                "metadata": metadata,
                "inputs": inputs,
                "outputs": outputs,
                "feedback": feedback,
                "metrics": metrics,
                "config": config,
                "user_properties": user_properties,
                "duration": duration or 0
            }
            
            return event
            
        except Exception as e:
            self._logger.error(f"Failed to convert span to HoneyHive event: {e}")
            return None
    
    def _extract_attributes_by_prefix(self, attributes: Dict[str, Any], prefix: str) -> Dict[str, Any]:
        """
        Extract attributes with a specific prefix and remove the prefix.
        
        Args:
            attributes: Dictionary of span attributes
            prefix: Prefix to filter by
            
        Returns:
            Dictionary with matching attributes (prefix removed from keys)
        """
        result = {}
        for key, value in attributes.items():
            if key.startswith(prefix):
                clean_key = key.replace(prefix, "")
                result[clean_key] = value
        return result
    
    def _send_events(self, events: list) -> bool:
        """
        Send events to HoneyHive API.
        
        Args:
            events: List of HoneyHive event dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        if not self._sdk:
            self._logger.error("HoneyHive SDK not initialized")
            return False
        
        try:
            if len(events) == 1:
                # Single event
                return self._send_single_event(events[0])
            else:
                # Try batch first, fall back to individual events
                if self._send_batch_events(events):
                    return True
                else:
                    # Fallback: send individual events
                    if self.verbose:
                        self._logger.warning("Batch send failed, falling back to individual events")
                    return self._send_individual_events(events)
                    
        except Exception as e:
            self._logger.error(f"Error sending events to HoneyHive: {e}")
            return False
    
    def _send_single_event(self, event: Dict[str, Any]) -> bool:
        """Send a single event to HoneyHive."""
        try:
            from honeyhive.models import operations
            from honeyhive.models.components.createeventrequest import CreateEventRequest
            
            # Create event request
            event_request = operations.CreateEventRequestBody(
                event=CreateEventRequest(**event)
            )
            
            # Send to HoneyHive
            response = self._sdk.events.create_event(request=event_request)
            
            if response.status_code == 200:
                if self.verbose:
                    self._logger.debug(f"Successfully sent event: {event['event_name']}")
                return True
            else:
                self._logger.error(f"Failed to send event: {response.status_code} - {response.raw_response.text}")
                return False
                
        except Exception as e:
            self._logger.error(f"Error sending single event: {e}")
            return False
    
    def _send_batch_events(self, events: list) -> bool:
        """Send multiple events to HoneyHive as a batch."""
        try:
            from honeyhive.models import operations
            from honeyhive.models.components.createeventrequest import CreateEventRequest
            
            # Create batch request
            batch_events = [CreateEventRequest(**event) for event in events]
            batch_request = operations.CreateEventBatchRequestBody(
                events=batch_events
            )
            
            # Send batch to HoneyHive
            response = self._sdk.events.create_event_batch(request=batch_request)
            
            if response.status_code == 200:
                if self.verbose:
                    self._logger.debug(f"Successfully sent batch of {len(events)} events")
                return True
            else:
                self._logger.error(f"Failed to send event batch: {response.status_code} - {response.raw_response.text}")
                return False
                
        except Exception as e:
            self._logger.error(f"Error sending batch events: {e}")
            return False
    
    def _send_individual_events(self, events: list) -> bool:
        """Send events individually as fallback."""
        success_count = 0
        for event in events:
            if self._send_single_event(event):
                success_count += 1
        
        # Consider successful if at least 50% succeeded
        success_rate = success_count / len(events) if events else 0
        return success_rate >= 0.5
    
    def _filter_spans_by_duration(self, spans: Sequence[ReadableSpan]) -> list:
        """
        Filter spans based on duration threshold to improve performance.
        
        Args:
            spans: Sequence of spans to filter
            
        Returns:
            List of spans that meet the duration threshold
        """
        if self.min_span_duration_ms <= 0:
            return list(spans)
        
        filtered_spans = []
        for span in spans:
            try:
                # Calculate span duration in milliseconds
                if hasattr(span, 'start_time') and hasattr(span, 'end_time'):
                    duration_ns = span.end_time - span.start_time
                    duration_ms = duration_ns / 1_000_000  # Convert nanoseconds to milliseconds
                    
                    if duration_ms >= self.min_span_duration_ms:
                        filtered_spans.append(span)
                else:
                    # If we can't determine duration, include the span
                    filtered_spans.append(span)
            except Exception:
                # If there's an error calculating duration, include the span
                filtered_spans.append(span)
        
        if self.verbose and len(filtered_spans) != len(spans):
            self._logger.debug(f"Filtered {len(spans) - len(filtered_spans)} spans below {self.min_span_duration_ms}ms threshold")
        
        return filtered_spans
    
    def shutdown(self) -> None:
        """Shutdown the exporter and clean up resources."""
        if self.verbose:
            self._logger.info("Shutting down HoneyHive span exporter")
        
        with self._lock:
            if hasattr(self, '_executor'):
                self._executor.shutdown(wait=True)
    
    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """
        Force flush any pending spans.
        
        Args:
            timeout_millis: Timeout in milliseconds
            
        Returns:
            True if successful, False otherwise
        """
        # The BatchSpanProcessor will handle this by calling export()
        return True
