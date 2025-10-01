"""
Universal Semantic Convention Processor for HoneyHive Tracer Integration

Integration layer for Universal LLM Discovery Engine v4.0 with existing HoneyHive tracer.
This replaces the existing semantic convention processing with the new universal engine.
"""

import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional

from .bundle_loader import DevelopmentAwareBundleLoader
from .provider_processor import UniversalProviderProcessor

logger = logging.getLogger(__name__)


class UniversalSemanticConventionProcessor:
    """Integration layer for Universal LLM Discovery Engine with HoneyHive tracer."""

    def __init__(self, cache_manager=None):
        """
        Initialize the universal semantic convention processor.

        Args:
            cache_manager: Optional cache manager for per-tracer caching
        """
        self.cache_manager = cache_manager
        self.processor = None
        self._initialization_time = None
        self._processing_stats = {
            "total_spans_processed": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0,
            "provider_detections": {},
        }

        # Initialize the processor
        self._initialize_processor()

    def _initialize_processor(self):
        """Initialize the universal processor with bundle loading."""

        start_time = time.perf_counter()

        try:
            # Determine bundle and source paths
            current_dir = Path(__file__).parent
            bundle_path = current_dir / "compiled_providers.pkl"
            source_path = (
                current_dir.parent.parent.parent.parent.parent / "config" / "dsl"
            )

            # Create bundle loader (tracer_instance=None for now, can be added later if needed)
            bundle_loader = DevelopmentAwareBundleLoader(
                bundle_path=bundle_path,
                source_path=source_path if source_path.exists() else None,
                tracer_instance=None,
            )

            # Create processor
            self.processor = UniversalProviderProcessor(bundle_loader)

            self._initialization_time = (
                time.perf_counter() - start_time
            ) * 1000  # Convert to ms

            logger.info(
                f"Universal LLM Discovery Engine v4.0 initialized in {self._initialization_time:.2f}ms"
            )
            logger.info(
                f"Supported providers: {self.processor.get_supported_providers()}"
            )

        except Exception as e:
            logger.error(f"Failed to initialize Universal LLM Discovery Engine: {e}")
            raise

    def process_span(self, span_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process span data using Universal LLM Discovery Engine.

        This replaces the existing semantic convention processing with the new universal engine.

        Args:
            span_data: Raw span data from tracer

        Returns:
            Processed span data with HoneyHive schema structure
        """

        if not self.processor:
            logger.error("Universal processor not initialized")
            return span_data

        start_time = time.perf_counter()

        try:
            # Extract attributes from span data
            attributes = span_data.get("attributes", {})

            if not attributes:
                logger.debug("No attributes in span data, returning unchanged")
                return span_data

            # Check cache first
            cache_key = None
            cached_result = None

            if self.cache_manager:
                cache_key = self._generate_cache_key(attributes)
                cached_result = self.cache_manager.get(cache_key)

                if cached_result is not None:
                    self._processing_stats["cache_hits"] += 1
                    logger.debug(f"Cache hit for key: {cache_key}")

                    # Merge cached result with span data
                    processed_span = {**span_data}
                    processed_span.update(cached_result)

                    return processed_span
                else:
                    self._processing_stats["cache_misses"] += 1

            # Process using universal engine
            honeyhive_data = self.processor.process_span_attributes(attributes)

            # Update processing stats
            self._processing_stats["total_spans_processed"] += 1

            # Track provider detections
            provider = honeyhive_data.get("metadata", {}).get("provider", "unknown")
            if provider not in self._processing_stats["provider_detections"]:
                self._processing_stats["provider_detections"][provider] = 0
            self._processing_stats["provider_detections"][provider] += 1

            # Merge with existing span data
            processed_span = {**span_data}
            processed_span.update(honeyhive_data)

            # Add processing metadata
            processing_time = (time.perf_counter() - start_time) * 1000  # Convert to ms
            processed_span.setdefault("metadata", {}).update(
                {
                    "universal_engine_processing_time_ms": processing_time,
                    "universal_engine_version": "4.0",
                }
            )

            # Cache the result if cache manager available
            if self.cache_manager and cache_key:
                self.cache_manager.set(cache_key, honeyhive_data)

            logger.debug(
                f"Processed span using {provider} provider in {processing_time:.4f}ms"
            )

            return processed_span

        except Exception as e:
            self._processing_stats["errors"] += 1
            logger.error(f"Universal processing failed: {e}")

            # Return original span data on error
            return span_data

    def _generate_cache_key(self, attributes: Dict[str, Any]) -> str:
        """Generate cache key for processed data."""

        # Use sorted attribute keys and a hash of values for cache key
        import hashlib
        import json

        # Create a deterministic representation
        sorted_attrs = dict(sorted(attributes.items()))

        try:
            # Create hash of the attributes
            attr_str = json.dumps(sorted_attrs, sort_keys=True, default=str)
            attr_hash = hashlib.md5(attr_str.encode()).hexdigest()[
                :16
            ]  # First 16 chars

            # Include key attribute names for debugging
            key_attrs = sorted(attributes.keys())[:5]  # First 5 keys
            key_suffix = ":".join(key_attrs)

            return f"universal_v4::{attr_hash}::{key_suffix}"

        except Exception as e:
            logger.warning(f"Failed to generate cache key: {e}")
            # Fallback to simple key
            return f"universal_v4::{hash(frozenset(attributes.keys()))}"

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""

        stats = self._processing_stats.copy()

        # Add processor stats if available
        if self.processor:
            processor_stats = self.processor.get_performance_stats()
            stats["processor_stats"] = processor_stats

        # Add initialization time
        if self._initialization_time:
            stats["initialization_time_ms"] = self._initialization_time

        # Calculate cache hit rate
        total_requests = stats["cache_hits"] + stats["cache_misses"]
        if total_requests > 0:
            stats["cache_hit_rate"] = stats["cache_hits"] / total_requests
        else:
            stats["cache_hit_rate"] = 0.0

        return stats

    def reset_stats(self):
        """Reset processing statistics."""

        self._processing_stats = {
            "total_spans_processed": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0,
            "provider_detections": {},
        }

        if self.processor:
            self.processor.reset_performance_stats()

    def get_supported_providers(self) -> list:
        """Get list of supported providers."""

        if self.processor:
            return self.processor.get_supported_providers()
        return []

    def validate_attributes_for_provider(
        self, attributes: Dict[str, Any], provider: str
    ) -> bool:
        """Check if attributes match a specific provider's signatures."""

        if self.processor:
            return self.processor.validate_attributes_for_provider(attributes, provider)
        return False

    def get_bundle_metadata(self) -> Dict[str, Any]:
        """Get bundle build metadata."""

        if self.processor:
            return self.processor.get_bundle_metadata()
        return {}

    def reload_bundle(self):
        """Reload the provider bundle (useful for development)."""

        if self.processor:
            logger.info("Reloading Universal LLM Discovery Engine bundle...")
            self.processor.reload_bundle()
            logger.info("Bundle reloaded successfully")
        else:
            logger.warning("No processor available to reload")

    def health_check(self) -> Dict[str, Any]:
        """Perform health check on the universal processor."""

        health_status = {"healthy": True, "issues": [], "metrics": {}}

        try:
            # Check if processor is initialized
            if not self.processor:
                health_status["healthy"] = False
                health_status["issues"].append("Processor not initialized")
                return health_status

            # Get processing stats
            stats = self.get_processing_stats()
            health_status["metrics"] = stats

            # Check error rate
            total_processed = stats.get("total_spans_processed", 0)
            errors = stats.get("errors", 0)

            if total_processed > 0:
                error_rate = errors / total_processed
                if error_rate > 0.05:  # 5% error threshold
                    health_status["healthy"] = False
                    health_status["issues"].append(f"High error rate: {error_rate:.1%}")

            # Check processor performance
            processor_stats = stats.get("processor_stats", {})
            avg_processing_time = processor_stats.get("avg_processing_time_ms", 0)

            if avg_processing_time > 0.1:  # 0.1ms threshold
                health_status["healthy"] = False
                health_status["issues"].append(
                    f"High processing time: {avg_processing_time:.4f}ms"
                )

            # Check fallback rate
            fallback_rate = processor_stats.get("fallback_rate", 0)
            if fallback_rate > 0.1:  # 10% fallback threshold
                health_status["healthy"] = False
                health_status["issues"].append(
                    f"High fallback rate: {fallback_rate:.1%}"
                )

            # Test basic functionality
            test_attributes = {
                "test.field": "test_value",
                "llm.model_name": "test-model",
            }

            test_start = time.perf_counter()
            test_result = self.processor.process_span_attributes(test_attributes)
            test_time = (time.perf_counter() - test_start) * 1000

            if test_time > 1.0:  # 1ms threshold for test
                health_status["healthy"] = False
                health_status["issues"].append(
                    f"Slow test processing: {test_time:.4f}ms"
                )

            health_status["metrics"]["test_processing_time_ms"] = test_time

        except Exception as e:
            health_status["healthy"] = False
            health_status["issues"].append(f"Health check failed: {e}")

        return health_status


# Factory function for easy integration
def create_universal_processor(
    cache_manager=None,
) -> UniversalSemanticConventionProcessor:
    """
    Factory function to create Universal Semantic Convention Processor.

    Args:
        cache_manager: Optional cache manager for per-tracer caching

    Returns:
        Initialized UniversalSemanticConventionProcessor
    """

    return UniversalSemanticConventionProcessor(cache_manager=cache_manager)
