"""HoneyHive span processor for OpenTelemetry."""

import time
from typing import Optional, Dict, Any
from threading import Lock

try:
    from opentelemetry import context, baggage
    from opentelemetry.sdk.trace import ReadableSpan, SpanProcessor
    from opentelemetry.context import Context
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    # Create dummy classes for type hints
    class Context: pass
    class ReadableSpan: pass
    class SpanProcessor: pass


class HoneyHiveSpanProcessor(SpanProcessor):
    """HoneyHive span processor with optimized attribute setting and reduced overhead."""
    
    def __init__(self):
        """Initialize with performance optimizations."""
        if not OTEL_AVAILABLE:
            raise ImportError("OpenTelemetry is required for HoneyHiveSpanProcessor")
        
        self._context_cache = {}  # Cache context lookups
        self._cache_ttl = 1000    # Cache TTL in operations
        self._operation_count = 0
        self._lock = Lock()
    
    def on_start(self, span: ReadableSpan, parent_context: Optional[Context] = None) -> None:
        """Called when a span starts - optimized attribute setting with conditional processing."""
        if not OTEL_AVAILABLE:
            return
        
        try:
            # DEBUG: Display span information before processing
            span_name = getattr(span, 'name', 'Unknown')
            span_kind = getattr(span, 'kind', 'Unknown')
            span_attributes = getattr(span, 'attributes', {})
            print(f"🔍 SPAN INTERCEPTED: {span_name} (kind: {span_kind})")
            print(f"   Attributes: {span_attributes}")
            print(f"   Parent context: {parent_context}")
            
            # Increment operation counter for cache management
            with self._lock:
                self._operation_count += 1
            
            # Get current context (use parent_context if provided, otherwise get_current)
            ctx = parent_context if parent_context is not None else context.get_current()
            if not ctx:
                print("   ❌ No context available")
                return
            
            print(f"   Context: {ctx}")
            
            # Check if we have cached attributes for this context
            ctx_id = id(ctx)
            if ctx_id in self._context_cache:
                cached_attrs = self._context_cache[ctx_id]
                print(f"   ✅ Using cached attributes: {cached_attrs}")
                # Apply cached attributes directly
                for key, value in cached_attrs.items():
                    span.set_attribute(key, value)
                return
            
            # Cache miss - compute attributes with early exit optimization
            attributes_to_set = {}
            
            # Try to get session_id from baggage first
            session_id = baggage.get_baggage('session_id', ctx)
            print(f"   Session ID from baggage: {session_id}")
            
            # If no session_id in baggage, try to get it from the span name or attributes
            # This helps catch OpenInference spans that might not have explicit baggage
            if not session_id:
                # Check if this is an OpenAI-related span (OpenInference creates these)
                if any(keyword in span_name.lower() for keyword in ['openai', 'chat', 'completion', 'gpt']):
                    print(f"   🔍 This looks like an OpenInference span: {span_name}")
                    # This is likely an OpenInference span, try to get session context from global state
                    try:
                        from honeyhive.tracer.otel_tracer import HoneyHiveTracer
                        if HoneyHiveTracer._is_initialized and HoneyHiveTracer._instance:
                            session_id = HoneyHiveTracer._instance.session_id
                            if session_id:
                                # Add session context to this span
                                attributes_to_set["honeyhive.session_id"] = session_id
                                attributes_to_set["honeyhive.project"] = HoneyHiveTracer._instance.project
                                attributes_to_set["honeyhive.source"] = HoneyHiveTracer._instance.source
                                print(f"   ✅ OpenInference span enriched with session context: {span_name}")
                                print(f"   ✅ Added attributes: {attributes_to_set}")
                            else:
                                print(f"   ❌ No session ID available from HoneyHiveTracer")
                        else:
                            print(f"   ❌ HoneyHiveTracer not initialized")
                    except Exception as e:
                        print(f"   ❌ Error getting HoneyHiveTracer: {e}")
                else:
                    print(f"   ℹ️  Not an OpenInference span")
            
            # Always process association_properties for legacy support
            # This ensures backward compatibility regardless of session_id status
            try:
                # Check if context has association_properties (legacy support)
                if hasattr(ctx, 'get') and callable(getattr(ctx, 'get', None)):
                    association_properties = ctx.get('association_properties')
                    if association_properties and isinstance(association_properties, dict):
                        print(f"   🔍 Found association_properties: {association_properties}")
                        for key, value in association_properties.items():
                            if value is not None and not baggage.get_baggage(key, ctx):
                                # Always set traceloop.association.properties.* format for backend compatibility
                                attributes_to_set[f"traceloop.association.properties.{key}"] = str(value)
                                print(f"   ✅ Set traceloop.association.properties.{key} = {value}")
            except Exception as e:
                print(f"   ❌ Error checking association_properties: {e}")
            
            # If we have session_id from baggage, process normally
            if session_id:
                # Set honeyhive.* attributes (primary format)
                attributes_to_set["honeyhive.session_id"] = session_id
                
                # Add project from baggage - early exit if missing
                project = baggage.get_baggage('project', ctx)
                if not project:
                    # No project means no HoneyHive context, skip processing
                    print(f"   ❌ No project in baggage, skipping processing")
                    return
                    
                attributes_to_set["honeyhive.project"] = project
                
                # Add source from baggage
                source = baggage.get_baggage('source', ctx)
                if source:
                    attributes_to_set["honeyhive.source"] = source
                
                # Add parent_id from baggage
                parent_id = baggage.get_baggage('parent_id', ctx)
                if parent_id:
                    attributes_to_set["honeyhive.parent_id"] = parent_id
                
                # Add experiment harness information from configuration
                try:
                    from honeyhive.utils.config import config
                    
                    if config.experiment_id:
                        attributes_to_set["honeyhive.experiment_id"] = config.experiment_id
                        print(f"   ✅ Added experiment ID: {config.experiment_id}")
                    
                    if config.experiment_name:
                        attributes_to_set["honeyhive.experiment_name"] = config.experiment_name
                        print(f"   ✅ Added experiment name: {config.experiment_name}")
                    
                    if config.experiment_variant:
                        attributes_to_set["honeyhive.experiment_variant"] = config.experiment_variant
                        print(f"   ✅ Added experiment variant: {config.experiment_variant}")
                    
                    if config.experiment_group:
                        attributes_to_set["honeyhive.experiment_group"] = config.experiment_group
                        print(f"   ✅ Added experiment group: {config.experiment_group}")
                    
                    if config.experiment_metadata:
                        # Add experiment metadata as individual attributes for better observability
                        for key, value in config.experiment_metadata.items():
                            attr_key = f"honeyhive.experiment_metadata.{key}"
                            attributes_to_set[attr_key] = str(value)
                        print(f"   ✅ Added experiment metadata: {len(config.experiment_metadata)} items")
                        
                except Exception as e:
                    print(f"   ⚠️  Error adding experiment attributes: {e}")
                
                # Set traceloop.association.properties.* attributes for backend compatibility
                # BUT avoid duplicates with what's already set from association_properties
                attributes_to_set["traceloop.association.properties.session_id"] = session_id
                attributes_to_set["traceloop.association.properties.project"] = project
                if source:
                    attributes_to_set["traceloop.association.properties.source"] = source
                if parent_id:
                    attributes_to_set["traceloop.association.properties.parent_id"] = parent_id
                
                print(f"   ✅ Set both honeyhive.* and traceloop.association.properties.* attributes for backend compatibility")
            else:
                # No session_id, but we might have association_properties
                print(f"   ℹ️  No session_id in baggage, only processing association_properties")
                
                # Even without session_id, we can still add experiment attributes
                try:
                    from honeyhive.utils.config import config
                    
                    if config.experiment_id:
                        attributes_to_set["honeyhive.experiment_id"] = config.experiment_id
                        print(f"   ✅ Added experiment ID (no session): {config.experiment_id}")
                    
                    if config.experiment_name:
                        attributes_to_set["honeyhive.experiment_name"] = config.experiment_name
                        print(f"   ✅ Added experiment name (no session): {config.experiment_name}")
                    
                    if config.experiment_variant:
                        attributes_to_set["honeyhive.experiment_variant"] = config.experiment_variant
                        print(f"   ✅ Added experiment variant (no session): {config.experiment_variant}")
                    
                    if config.experiment_group:
                        attributes_to_set["honeyhive.experiment_group"] = config.experiment_group
                        print(f"   ✅ Added experiment group (no session): {config.experiment_group}")
                    
                    if config.experiment_metadata:
                        # Add experiment metadata as individual attributes for better observability
                        for key, value in config.experiment_metadata.items():
                            attr_key = f"honeyhive.experiment_metadata.{key}"
                            attributes_to_set[attr_key] = str(value)
                        print(f"   ✅ Added experiment metadata (no session): {len(config.experiment_metadata)} items")
                        
                except Exception as e:
                    print(f"   ⚠️  Error adding experiment attributes (no session): {e}")
            
            print(f"   📝 Final attributes to set: {attributes_to_set}")
            
            # Set all attributes at once (more efficient)
            for key, value in attributes_to_set.items():
                span.set_attribute(key, value)
            
            # Cache the attributes for future use
            if len(attributes_to_set) > 0:
                with self._lock:
                    self._context_cache[ctx_id] = attributes_to_set
                    
                    # Clean up cache if it gets too large
                    if len(self._context_cache) > 1000:
                        self._cleanup_cache()
            
            print(f"   ✅ Span processing complete")
        
        except Exception as e:
            # Silently fail to avoid breaking the application
            print(f"   ❌ Error in span processor: {e}")
            pass
    
    def on_end(self, span: ReadableSpan) -> None:
        """Called when a span ends."""
        if not OTEL_AVAILABLE:
            return
        
        try:
            # Add end time if not already set
            if not span.attributes.get("honeyhive.end_time"):
                span.set_attribute("honeyhive.end_time", int(time.time() * 1000))
            
            # Add duration if start time is available
            start_time = span.attributes.get("honeyhive.start_time")
            if start_time:
                end_time = span.attributes.get("honeyhive.end_time", int(time.time() * 1000))
                duration = end_time - start_time
                span.set_attribute("honeyhive.duration", duration)
        
        except Exception as e:
            # Silently fail to avoid breaking the application
            pass
    
    def shutdown(self) -> None:
        """Shutdown the span processor."""
        if not OTEL_AVAILABLE:
            return
        
        try:
            with self._lock:
                self._context_cache.clear()
        except Exception as e:
            # Silently fail to avoid breaking the application
            pass
    
    def force_flush(self, timeout_millis: float = 30000) -> bool:
        """Force flush any pending spans."""
        if not OTEL_AVAILABLE:
            return True
        
        try:
            # No pending spans to flush in this processor
            return True
        except Exception as e:
            return False
    
    def _cleanup_cache(self):
        """Clean up the context cache to prevent memory leaks."""
        if not OTEL_AVAILABLE:
            return
        
        try:
            # Simple cleanup: remove oldest entries
            cache_size = len(self._context_cache)
            if cache_size > 1000:
                # Remove oldest 20% of entries
                items_to_remove = cache_size // 5
                keys_to_remove = list(self._context_cache.keys())[:items_to_remove]
                for key in keys_to_remove:
                    del self._context_cache[key]
        except Exception as e:
            # Silently fail to avoid breaking the application
            pass
