"""HoneyHive span exporter for OpenTelemetry."""

import json
import time
import threading
from typing import Dict, Any, List, Optional
from queue import Queue, Empty

try:
    from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
    from opentelemetry.sdk.trace import ReadableSpan
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    # Create dummy classes for type hints
    class SpanExporter: pass
    class SpanExportResult: pass
    class ReadableSpan: pass

from ..api.client import HoneyHiveClient
from ..api.events import CreateEventRequest


class HoneyHiveSpanExporter(SpanExporter):
    """HoneyHive span exporter that sends spans to the HoneyHive API."""
    
    def __init__(
        self,
        api_key: str,
        project: str,
        source: str = "production",
        test_mode: bool = False,
        batch_size: int = 100,
        batch_timeout: float = 5.0,
        max_queue_size: int = 10000,
    ):
        """Initialize the HoneyHive span exporter.
        
        Args:
            api_key: HoneyHive API key
            project: Project name
            source: Source environment
            test_mode: Whether to run in test mode
            batch_size: Number of spans to batch before sending
            batch_timeout: Timeout for batching in seconds
            max_queue_size: Maximum size of the span queue
        """
        if not OTEL_AVAILABLE:
            raise ImportError("OpenTelemetry is required for HoneyHiveSpanExporter")
        
        self.api_key = api_key
        self.project = project
        self.source = source
        self.test_mode = test_mode
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.max_queue_size = max_queue_size
        
        # Initialize API client
        self.client = HoneyHiveClient(api_key=api_key)
        
        # Span queue and batching
        self.span_queue = Queue(maxsize=max_queue_size)
        self.batch_lock = threading.Lock()
        self.last_batch_time = time.time()
        
        # Start background thread for processing
        self.running = True
        self.worker_thread = threading.Thread(target=self._process_spans, daemon=True)
        self.worker_thread.start()
    
    def export(self, spans: List[ReadableSpan]) -> SpanExportResult:
        """Export spans to HoneyHive API.
        
        Args:
            spans: List of spans to export
            
        Returns:
            Export result
        """
        if not OTEL_AVAILABLE:
            return SpanExportResult.SUCCESS
        
        try:
            # Add spans to queue for background processing
            for span in spans:
                try:
                    self.span_queue.put_nowait(span)
                except:
                    # Queue is full, drop the span
                    if not self.test_mode:
                        print(f"Warning: Span queue full, dropping span {span.name}")
            
            return SpanExportResult.SUCCESS
        
        except Exception as e:
            if not self.test_mode:
                print(f"Error exporting spans: {e}")
            return SpanExportResult.FAILURE
    
    def shutdown(self) -> None:
        """Shutdown the exporter."""
        if not OTEL_AVAILABLE:
            return
        
        try:
            self.running = False
            if self.worker_thread.is_alive():
                self.worker_thread.join(timeout=5.0)
            
            # Process remaining spans
            self._flush_remaining_spans()
            
            # Close client
            self.client.close()
        
        except Exception as e:
            if not self.test_mode:
                print(f"Error shutting down exporter: {e}")
    
    def _process_spans(self):
        """Background thread for processing spans."""
        if not OTEL_AVAILABLE:
            return
        
        batch = []
        last_batch_time = time.time()
        
        while self.running:
            try:
                # Try to get a span from the queue
                try:
                    span = self.span_queue.get(timeout=1.0)
                    batch.append(span)
                except Empty:
                    # No spans available, check if we should flush
                    if batch and (time.time() - last_batch_time) > self.batch_timeout:
                        self._send_batch(batch)
                        batch = []
                        last_batch_time = time.time()
                    continue
                
                # Check if we should send the batch
                if len(batch) >= self.batch_size:
                    self._send_batch(batch)
                    batch = []
                    last_batch_time = time.time()
                
                # Mark task as done
                self.span_queue.task_done()
            
            except Exception as e:
                if not self.test_mode:
                    print(f"Error processing spans: {e}")
                # Clear batch on error to prevent memory leaks
                batch = []
    
    def _send_batch(self, spans: List[ReadableSpan]):
        """Send a batch of spans to the HoneyHive API."""
        if not OTEL_AVAILABLE or not spans:
            return
        
        try:
            # Convert spans to events
            events = []
            for span in spans:
                event = self._span_to_event(span)
                if event:
                    events.append(event)
            
            if not events:
                return
            
            # Send events to API
            from ..api.events import BatchCreateEventRequest
            request = BatchCreateEventRequest(events=events)
            
            if self.test_mode:
                # In test mode, just print the events
                print(f"Test mode: Would send {len(events)} events")
                for event in events:
                    print(f"  Event: {event.event_name} ({event.event_type})")
            else:
                # Send to API
                response = self.client.events.create_event_batch(request)
                if not response.success:
                    print(f"Failed to send batch of {len(events)} events")
        
        except Exception as e:
            if not self.test_mode:
                print(f"Error sending batch: {e}")
    
    def _span_to_event(self, span: ReadableSpan) -> Optional[CreateEventRequest]:
        """Convert a span to a HoneyHive event."""
        if not OTEL_AVAILABLE:
            return None
        
        try:
            # Extract HoneyHive attributes
            attributes = dict(span.attributes)
            
            session_id = attributes.get("honeyhive.session_id")
            project = attributes.get("honeyhive.project", self.project)
            source = attributes.get("honeyhive.source", self.source)
            parent_id = attributes.get("honeyhive.parent_id")
            
            # Skip spans without HoneyHive context
            if not session_id or not project:
                return None
            
            # Create event request
            event = CreateEventRequest(
                project=project,
                source=source,
                event_name=span.name,
                event_type="model",  # Default to model, could be determined from span name
                session_id=session_id,
                parent_id=parent_id,
                start_time=int(span.start_time / 1000000) if span.start_time else None,
                end_time=int(span.end_time / 1000000) if span.end_time else None,
                duration=attributes.get("honeyhive.duration"),
                metadata=attributes,
            )
            
            return event
        
        except Exception as e:
            if not self.test_mode:
                print(f"Error converting span to event: {e}")
            return None
    
    def _flush_remaining_spans(self):
        """Flush any remaining spans in the queue."""
        if not OTEL_AVAILABLE:
            return
        
        try:
            batch = []
            while not self.span_queue.empty():
                try:
                    span = self.span_queue.get_nowait()
                    batch.append(span)
                    
                    if len(batch) >= self.batch_size:
                        self._send_batch(batch)
                        batch = []
                
                except Empty:
                    break
            
            # Send any remaining spans
            if batch:
                self._send_batch(batch)
        
        except Exception as e:
            if not self.test_mode:
                print(f"Error flushing remaining spans: {e}")
    
    def enrich_session(self, enrichment_data: Dict[str, Any]):
        """Enrich a session with additional data.
        
        Args:
            enrichment_data: Session enrichment data
        """
        try:
            if self.test_mode:
                print(f"Test mode: Would enrich session {enrichment_data.get('session_id')}")
                return
            
            # Create enrichment event
            event = CreateEventRequest(
                project=enrichment_data.get("project", self.project),
                source=enrichment_data.get("source", self.source),
                event_name="session_enrichment",
                event_type="session",
                session_id=enrichment_data.get("session_id"),
                metadata=enrichment_data.get("metadata"),
                feedback=enrichment_data.get("feedback"),
                metrics=enrichment_data.get("metrics"),
                config=enrichment_data.get("config"),
                inputs=enrichment_data.get("inputs"),
                outputs=enrichment_data.get("outputs"),
                user_properties=enrichment_data.get("user_properties"),
            )
            
            # Send enrichment event
            response = self.client.events.create_event(event)
            if not response.success:
                print(f"Failed to enrich session {enrichment_data.get('session_id')}")
        
        except Exception as e:
            if not self.test_mode:
                print(f"Error enriching session: {e}")
