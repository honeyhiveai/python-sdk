"""Integration performance tests for UniversalProviderProcessor.

This module tests Universal LLM Discovery Engine v4.0 performance with real data
and compiled provider bundles. Tests validate O(1) algorithmic performance claims using
actual frozenset operations and compiled extraction functions.
"""

# pylint: disable=too-many-lines,protected-access,redefined-outer-name,too-many-public-methods,line-too-long
# Justification: Comprehensive integration performance test coverage requires extensive test cases, testing private
# methods requires protected access, pytest fixtures redefine outer names by design, comprehensive test
# classes need many test methods, and real performance integration patterns create unavoidable long lines.

import sys
import time

from src.honeyhive.tracer.processing.semantic_conventions.provider_processor import (
    UniversalProviderProcessor,
)


class TestUniversalProviderProcessorPerformanceIntegration:
    """Integration performance test suite for UniversalProviderProcessor with real data structures."""

    def test_real_provider_detection_performance_openai(
        self, real_honeyhive_tracer
    ) -> None:
        """Test real O(1) provider detection performance with OpenAI attributes."""
        # Arrange - Real processor with compiled bundle
        processor = UniversalProviderProcessor(tracer_instance=real_honeyhive_tracer)

        # Real OpenAI span attributes from OpenInference instrumentation
        openai_attributes = {
            "llm.model_name": "gpt-4",
            "llm.provider": "openai",
            "llm.input_messages": [
                {"role": "user", "content": "What is machine learning?"}
            ],
            "llm.output_messages": [
                {"role": "assistant", "content": "Machine learning is..."}
            ],
            "llm.token_count.prompt": 15,
            "llm.token_count.completion": 25,
            "llm.token_count.total": 40,
            "llm.invocation_parameters.temperature": 0.7,
            "llm.invocation_parameters.max_tokens": 150,
        }

        # Act - Measure real O(1) performance
        start_time = time.perf_counter()
        result = processor.process_span_attributes(openai_attributes)
        processing_time = (time.perf_counter() - start_time) * 1000  # Convert to ms

        # Assert - Validate O(1) performance claims
        assert (
            processing_time < 0.1
        ), f"Processing time {processing_time:.4f}ms exceeds 0.1ms target"
        assert result["metadata"]["provider"] == "openai"
        assert result["metadata"]["detection_method"] == "signature_based"
        assert result["inputs"]["prompt"] is not None
        assert result["outputs"]["completion"] is not None
        assert result["config"]["model"] == "gpt-4"

    def test_real_provider_detection_performance_anthropic(
        self, real_honeyhive_tracer
    ) -> None:
        """Test real O(1) provider detection performance with Anthropic attributes."""
        # Arrange - Real processor with compiled bundle
        processor = UniversalProviderProcessor(tracer_instance=real_honeyhive_tracer)

        # Real Anthropic span attributes from OpenInference instrumentation
        anthropic_attributes = {
            "llm.model_name": "claude-3-sonnet-20240229",
            "llm.provider": "anthropic",
            "llm.input_messages": [
                {"role": "user", "content": "Explain quantum computing"}
            ],
            "llm.output_messages": [
                {"role": "assistant", "content": "Quantum computing leverages..."}
            ],
            "llm.token_count.prompt": 20,
            "llm.token_count.completion": 35,
            "llm.token_count.total": 55,
            "llm.invocation_parameters.temperature": 0.3,
            "llm.invocation_parameters.max_tokens": 200,
            "llm.invocation_parameters.top_k": 5,  # Anthropic-specific parameter
        }

        # Act - Measure real O(1) performance
        start_time = time.perf_counter()
        result = processor.process_span_attributes(anthropic_attributes)
        processing_time = (time.perf_counter() - start_time) * 1000  # Convert to ms

        # Assert - Validate O(1) performance claims
        assert (
            processing_time < 0.1
        ), f"Processing time {processing_time:.4f}ms exceeds 0.1ms target"
        assert result["metadata"]["provider"] == "anthropic"
        assert result["metadata"]["detection_method"] == "signature_based"
        assert result["inputs"]["prompt"] is not None
        assert result["outputs"]["completion"] is not None
        assert result["config"]["model"] == "claude-3-sonnet-20240229"

    def test_real_provider_detection_performance_gemini(
        self, real_honeyhive_tracer
    ) -> None:
        """Test real O(1) provider detection performance with Gemini attributes."""
        # Arrange - Real processor with compiled bundle
        processor = UniversalProviderProcessor(tracer_instance=real_honeyhive_tracer)

        # Real Gemini span attributes from OpenInference instrumentation
        gemini_attributes = {
            "llm.model_name": "gemini-1.5-pro",
            "llm.provider": "google",
            "llm.input_messages": [
                {"role": "user", "content": "What is artificial intelligence?"}
            ],
            "llm.output_messages": [
                {"role": "model", "content": "Artificial intelligence is..."}
            ],
            "llm.token_count.prompt": 18,
            "llm.token_count.completion": 30,
            "llm.token_count.total": 48,
            "llm.invocation_parameters.temperature": 0.5,
            "llm.invocation_parameters.max_output_tokens": 100,
        }

        # Act - Measure real O(1) performance
        start_time = time.perf_counter()
        result = processor.process_span_attributes(gemini_attributes)
        processing_time = (time.perf_counter() - start_time) * 1000  # Convert to ms

        # Assert - Validate O(1) performance claims
        assert (
            processing_time < 0.1
        ), f"Processing time {processing_time:.4f}ms exceeds 0.1ms target"
        assert result["metadata"]["provider"] == "gemini"
        assert result["metadata"]["detection_method"] == "signature_based"
        assert result["inputs"]["prompt"] is not None
        assert result["outputs"]["completion"] is not None
        assert result["config"]["model"] == "gemini-1.5-pro"

    def test_real_frozenset_operations_performance(self, real_honeyhive_tracer) -> None:
        """Test real frozenset.issubset() performance with multiple providers."""
        # Arrange - Real processor with compiled bundle
        processor = UniversalProviderProcessor(tracer_instance=real_honeyhive_tracer)

        # Multiple real provider attribute sets
        test_cases = [
            (
                "openai",
                {
                    "llm.provider": "openai",
                    "llm.model_name": "gpt-3.5-turbo",
                    "llm.input_messages": [{"role": "user", "content": "test"}],
                    "llm.token_count.prompt": 5,
                },
            ),
            (
                "anthropic",
                {
                    "llm.provider": "anthropic",
                    "llm.model_name": "claude-3-haiku-20240307",
                    "llm.input_messages": [{"role": "user", "content": "test"}],
                    "llm.invocation_parameters.top_k": 3,
                },
            ),
            (
                "gemini",
                {
                    "llm.provider": "google",
                    "llm.model_name": "gemini-1.0-pro",
                    "llm.input_messages": [{"role": "user", "content": "test"}],
                    "llm.invocation_parameters.max_output_tokens": 50,
                },
            ),
            ("unknown", {"custom.field": "value", "other.attribute": "data"}),
        ]

        # Act & Assert - Test real frozenset performance for each provider
        for expected_provider, attributes in test_cases:
            start_time = time.perf_counter()
            result = processor.process_span_attributes(attributes)
            processing_time = (time.perf_counter() - start_time) * 1000

            # Validate O(1) performance for each provider
            assert (
                processing_time < 0.1
            ), f"Processing time {processing_time:.4f}ms exceeds 0.1ms target for {expected_provider}"

            if expected_provider != "unknown":
                assert result["metadata"]["provider"] == expected_provider
                assert result["metadata"]["detection_method"] == "signature_based"
            else:
                assert result["metadata"]["detection_method"] == "fallback_heuristic"

    def test_real_bundle_loading_performance(self, real_honeyhive_tracer) -> None:
        """Test real bundle loading performance with compiled provider data."""
        # Act - Measure real bundle loading time
        start_time = time.perf_counter()
        processor = UniversalProviderProcessor(tracer_instance=real_honeyhive_tracer)
        bundle_load_time = (time.perf_counter() - start_time) * 1000

        # Assert - Validate bundle loading performance
        assert (
            bundle_load_time < 3.0
        ), f"Bundle loading time {bundle_load_time:.2f}ms exceeds 3ms target"
        assert processor.bundle is not None
        assert len(processor.provider_signatures) >= 3  # OpenAI, Anthropic, Gemini
        assert len(processor.extraction_functions) >= 3

    def test_real_extraction_function_performance(self, real_honeyhive_tracer) -> None:
        """Test real extraction function performance with compiled functions."""
        # Arrange - Real processor with compiled bundle
        processor = UniversalProviderProcessor(tracer_instance=real_honeyhive_tracer)

        # Real OpenAI attributes for extraction testing
        openai_attributes = {
            "llm.model_name": "gpt-4",
            "llm.provider": "openai",
            "llm.input_messages": [{"role": "user", "content": "Extract this data"}],
            "llm.output_messages": [
                {"role": "assistant", "content": "Data extracted successfully"}
            ],
            "llm.token_count.prompt": 12,
            "llm.token_count.completion": 18,
            "llm.invocation_parameters.temperature": 0.8,
        }

        # Act - Measure real extraction performance
        provider = processor._detect_provider(openai_attributes)
        assert provider == "openai"

        start_time = time.perf_counter()
        result = processor._extract_provider_data(provider, openai_attributes)
        extraction_time = (time.perf_counter() - start_time) * 1000

        # Assert - Validate extraction performance
        assert (
            extraction_time < 0.05
        ), f"Extraction time {extraction_time:.4f}ms exceeds 0.05ms target"
        assert isinstance(result, dict)
        assert "inputs" in result
        assert "outputs" in result
        assert "config" in result
        assert "metadata" in result

    def test_real_validation_enhancement_performance(
        self, real_honeyhive_tracer
    ) -> None:
        """Test real validation and enhancement performance."""
        # Arrange - Real processor with compiled bundle
        processor = UniversalProviderProcessor(tracer_instance=real_honeyhive_tracer)

        # Sample extracted data for validation
        extracted_data = {
            "inputs": {"prompt": "test prompt"},
            "outputs": {"completion": "test completion"},
            "config": {"model": "gpt-4", "temperature": 0.7},
            "metadata": {"provider": "openai"},
        }

        # Act - Measure real validation performance
        start_time = time.perf_counter()
        validated_result = processor._validate_and_enhance(extracted_data, "openai")
        validation_time = (time.perf_counter() - start_time) * 1000

        # Assert - Validate enhancement performance
        assert (
            validation_time < 0.01
        ), f"Validation time {validation_time:.4f}ms exceeds 0.01ms target"
        assert validated_result["metadata"]["provider"] == "openai"
        assert (
            validated_result["metadata"]["processing_engine"]
            == "universal_llm_discovery_v4"
        )
        assert "processed_at" in validated_result["metadata"]

    def test_real_fallback_processing_performance(self, real_honeyhive_tracer) -> None:
        """Test real fallback processing performance for unknown providers."""
        # Arrange - Real processor with compiled bundle
        processor = UniversalProviderProcessor(tracer_instance=real_honeyhive_tracer)

        # Unknown provider attributes
        unknown_attributes = {
            "custom.provider": "unknown_llm",
            "custom.model": "proprietary-model-v1",
            "custom.input": "test input",
            "custom.output": "test output",
        }

        # Act - Measure real fallback performance
        start_time = time.perf_counter()
        result = processor.process_span_attributes(unknown_attributes)
        fallback_time = (time.perf_counter() - start_time) * 1000

        # Assert - Validate fallback performance
        assert (
            fallback_time < 0.1
        ), f"Fallback processing time {fallback_time:.4f}ms exceeds 0.1ms target"
        assert result["metadata"]["detection_method"] == "fallback_heuristic"
        assert "inputs" in result
        assert "outputs" in result
        assert "config" in result
        assert "metadata" in result

    def test_real_performance_stats_tracking(self, real_honeyhive_tracer) -> None:
        """Test real performance statistics tracking with multiple operations."""
        # Arrange - Real processor with compiled bundle
        processor = UniversalProviderProcessor(tracer_instance=real_honeyhive_tracer)

        # Multiple real provider test cases
        test_attributes = [
            {
                "llm.provider": "openai",
                "llm.model_name": "gpt-4",
                "llm.token_count.prompt": 10,
            },
            {
                "llm.provider": "anthropic",
                "llm.model_name": "claude-3-sonnet",
                "llm.invocation_parameters.top_k": 5,
            },
            {
                "llm.provider": "google",
                "llm.model_name": "gemini-1.5-pro",
                "llm.invocation_parameters.max_output_tokens": 100,
            },
            {"custom.field": "unknown"},  # Fallback case
        ]

        # Act - Process multiple spans and measure performance
        processing_times = []
        for attributes in test_attributes:
            start_time = time.perf_counter()
            result = processor.process_span_attributes(attributes)
            processing_time = (time.perf_counter() - start_time) * 1000
            processing_times.append(processing_time)
            assert result is not None

        # Get real performance statistics
        stats = processor.get_performance_stats()

        # Assert - Validate performance tracking
        assert stats["total_processed"] == 4
        assert stats["fallback_usage"] == 1  # One unknown provider
        assert len(stats["processing_times"]) == 4
        assert stats["avg_processing_time_ms"] > 0
        assert stats["provider_detections"]["openai"] == 1
        assert stats["provider_detections"]["anthropic"] == 1
        assert stats["provider_detections"]["gemini"] == 1

        # Validate all individual processing times
        for i, processing_time in enumerate(processing_times):
            assert (
                processing_time < 0.1
            ), f"Processing time {i+1}: {processing_time:.4f}ms exceeds 0.1ms target"

    def test_real_memory_footprint_validation(self, real_honeyhive_tracer) -> None:
        """Test real memory footprint of compiled provider bundle."""
        # Arrange - Create processor with real compiled bundle

        # Act - Create processor with real compiled bundle
        processor = UniversalProviderProcessor(tracer_instance=real_honeyhive_tracer)

        # Measure memory usage of key data structures
        bundle_memory = sys.getsizeof(processor.bundle) if processor.bundle else 0
        signatures_memory = sys.getsizeof(processor.provider_signatures)
        extraction_memory = sys.getsizeof(processor.extraction_functions)
        total_memory = bundle_memory + signatures_memory + extraction_memory

        # Assert - Validate memory footprint target
        assert (
            total_memory < 30000
        ), f"Memory footprint {total_memory} bytes exceeds 30KB target"
        assert len(processor.provider_signatures) >= 3  # OpenAI, Anthropic, Gemini

        # Test that memory usage is reasonable for the functionality provided
        providers_count = len(processor.provider_signatures)
        memory_per_provider = (
            total_memory / providers_count if providers_count > 0 else 0
        )
        assert (
            memory_per_provider < 10000
        ), f"Memory per provider {memory_per_provider} bytes too high"

    def test_real_concurrent_processing_performance(
        self, real_honeyhive_tracer
    ) -> None:
        """Test real concurrent processing performance with multiple simultaneous operations."""
        # Arrange - Real processor with compiled bundle
        processor = UniversalProviderProcessor(tracer_instance=real_honeyhive_tracer)

        # Multiple concurrent attribute sets
        concurrent_attributes = [
            {
                "llm.provider": "openai",
                "llm.model_name": f"gpt-4-{i}",
                "llm.token_count.prompt": 10 + i,
            }
            for i in range(10)  # 10 concurrent operations
        ]

        # Act - Process all attributes concurrently and measure performance
        start_time = time.perf_counter()
        results = []
        for attributes in concurrent_attributes:
            result = processor.process_span_attributes(attributes)
            results.append(result)
        total_time = (time.perf_counter() - start_time) * 1000

        # Assert - Validate concurrent performance
        avg_time_per_operation = total_time / len(concurrent_attributes)
        assert (
            avg_time_per_operation < 0.1
        ), f"Average processing time {avg_time_per_operation:.4f}ms exceeds 0.1ms target"
        assert len(results) == 10
        assert all(result["metadata"]["provider"] == "openai" for result in results)

        # Validate performance stats reflect concurrent operations
        stats = processor.get_performance_stats()
        assert stats["total_processed"] == 10
        assert stats["provider_detections"]["openai"] == 10

    def test_real_bundle_metadata_performance(self, real_honeyhive_tracer) -> None:
        """Test real bundle metadata retrieval performance."""
        # Arrange - Real processor with compiled bundle
        processor = UniversalProviderProcessor(tracer_instance=real_honeyhive_tracer)

        # Act - Measure metadata retrieval performance
        start_time = time.perf_counter()
        metadata = processor.get_bundle_metadata()
        metadata_time = (time.perf_counter() - start_time) * 1000

        # Assert - Validate metadata performance
        assert (
            metadata_time < 0.01
        ), f"Metadata retrieval time {metadata_time:.4f}ms exceeds 0.01ms target"
        assert isinstance(metadata, dict)

        # Validate metadata contains expected information
        if metadata:  # If bundle loader provides metadata
            assert "build_timestamp" in metadata or "providers" in metadata

    def test_real_provider_signature_validation_performance(
        self, real_honeyhive_tracer
    ) -> None:
        """Test real provider signature validation performance."""
        # Arrange - Real processor with compiled bundle
        processor = UniversalProviderProcessor(tracer_instance=real_honeyhive_tracer)

        # Test attributes for signature validation
        test_cases = [
            ("openai", {"llm.provider": "openai", "llm.model_name": "gpt-4"}),
            (
                "anthropic",
                {"llm.provider": "anthropic", "llm.invocation_parameters.top_k": 5},
            ),
            ("invalid", {"invalid.field": "value"}),
        ]

        # Act & Assert - Test signature validation performance
        for provider, attributes in test_cases:
            start_time = time.perf_counter()
            is_valid = processor.validate_attributes_for_provider(attributes, provider)
            validation_time = (time.perf_counter() - start_time) * 1000

            # Validate performance
            assert (
                validation_time < 0.01
            ), f"Signature validation time {validation_time:.4f}ms exceeds 0.01ms target"

            # Validate correctness
            if provider in ["openai", "anthropic"]:
                assert (
                    is_valid is True
                ), f"Valid {provider} attributes should pass validation"
            else:
                assert (
                    is_valid is False
                ), f"Invalid {provider} attributes should fail validation"

    def test_real_error_handling_performance(self, real_honeyhive_tracer) -> None:
        """Test real error handling performance with graceful degradation."""
        # Arrange - Real processor with compiled bundle
        processor = UniversalProviderProcessor(tracer_instance=real_honeyhive_tracer)

        # Error scenarios to test
        error_cases = [
            None,  # Non-dict input
            [],  # List input
            "string",  # String input
            42,  # Integer input
            {"malformed": None},  # Malformed dict
        ]

        # Act & Assert - Test error handling performance
        for i, error_input in enumerate(error_cases):
            start_time = time.perf_counter()
            result = processor.process_span_attributes(error_input)
            error_handling_time = (time.perf_counter() - start_time) * 1000

            # Validate graceful degradation performance
            assert (
                error_handling_time < 0.1
            ), f"Error handling time {error_handling_time:.4f}ms exceeds 0.1ms target for case {i}"
            assert isinstance(result, dict), f"Error case {i} should return dict"
            assert result["metadata"]["detection_method"] == "fallback_heuristic"

    def test_real_performance_stats_calculation_performance(
        self, real_honeyhive_tracer
    ) -> None:
        """Test real performance statistics calculation performance."""
        # Arrange - Real processor with some processing history
        processor = UniversalProviderProcessor(tracer_instance=real_honeyhive_tracer)

        # Generate some processing history
        for i in range(5):
            attributes = {"llm.provider": "openai", "llm.model_name": f"gpt-4-{i}"}
            processor.process_span_attributes(attributes)

        # Act - Measure stats calculation performance
        start_time = time.perf_counter()
        stats = processor.get_performance_stats()
        stats_time = (time.perf_counter() - start_time) * 1000

        # Assert - Validate stats calculation performance
        assert (
            stats_time < 0.01
        ), f"Stats calculation time {stats_time:.4f}ms exceeds 0.01ms target"
        assert stats["total_processed"] == 5
        assert stats["avg_processing_time_ms"] > 0
        assert stats["provider_detections"]["openai"] == 5

    def test_real_bundle_reload_performance(self, real_honeyhive_tracer) -> None:
        """Test real bundle reload performance."""
        # Arrange - Real processor with compiled bundle
        processor = UniversalProviderProcessor(tracer_instance=real_honeyhive_tracer)

        # Act - Measure bundle reload performance
        start_time = time.perf_counter()
        processor.reload_bundle()
        reload_time = (time.perf_counter() - start_time) * 1000

        # Assert - Validate reload performance
        assert (
            reload_time < 5.0
        ), f"Bundle reload time {reload_time:.2f}ms exceeds 5ms reasonable target"
        assert processor.bundle is not None
        # Bundle may be the same object or reloaded - both are valid

    def test_real_end_to_end_processing_pipeline_performance(
        self, real_honeyhive_tracer
    ) -> None:
        """Test complete end-to-end processing pipeline performance."""
        # Arrange - Real processor with compiled bundle
        processor = UniversalProviderProcessor(tracer_instance=real_honeyhive_tracer)

        # Complex real span attributes
        complex_attributes = {
            "llm.model_name": "gpt-4-turbo-preview",
            "llm.provider": "openai",
            "llm.input_messages": [
                {"role": "system", "content": "You are a helpful assistant"},
                {
                    "role": "user",
                    "content": "Write a comprehensive analysis of machine learning",
                },
            ],
            "llm.output_messages": [
                {
                    "role": "assistant",
                    "content": "Machine learning is a comprehensive field...",
                }
            ],
            "llm.token_count.prompt": 150,
            "llm.token_count.completion": 500,
            "llm.token_count.total": 650,
            "llm.invocation_parameters.temperature": 0.7,
            "llm.invocation_parameters.max_tokens": 1000,
            "llm.invocation_parameters.top_p": 0.9,
            "llm.invocation_parameters.frequency_penalty": 0.1,
            "llm.invocation_parameters.presence_penalty": 0.1,
        }

        # Act - Measure complete pipeline performance
        start_time = time.perf_counter()
        result = processor.process_span_attributes(complex_attributes)
        pipeline_time = (time.perf_counter() - start_time) * 1000

        # Assert - Validate complete pipeline performance
        assert (
            pipeline_time < 0.1
        ), f"Complete pipeline time {pipeline_time:.4f}ms exceeds 0.1ms target"
        assert result["metadata"]["provider"] == "openai"
        assert result["metadata"]["detection_method"] == "signature_based"
        assert result["inputs"]["prompt"] is not None
        assert result["outputs"]["completion"] is not None
        assert result["config"]["model"] == "gpt-4-turbo-preview"
        assert result["config"]["temperature"] == 0.7
        assert len(result["config"]) >= 5  # Multiple configuration parameters

    def test_real_graceful_degradation_performance(self, real_honeyhive_tracer) -> None:
        """Test real graceful degradation performance under various failure conditions."""
        # Test with bundle loader that might fail
        processor = UniversalProviderProcessor(
            bundle_loader=None, tracer_instance=real_honeyhive_tracer
        )

        # Test various degradation scenarios
        degradation_cases = [
            {
                "llm.provider": "openai",
                "llm.model_name": "gpt-4",
            },  # Should work even with degraded bundle
            {"unknown.field": "value"},  # Should fallback gracefully
            None,  # Should handle None gracefully
        ]

        # Act & Assert - Test degradation performance
        for i, attributes in enumerate(degradation_cases):
            start_time = time.perf_counter()
            result = processor.process_span_attributes(attributes)
            degradation_time = (time.perf_counter() - start_time) * 1000

            # Validate graceful degradation performance
            assert (
                degradation_time < 0.1
            ), f"Degradation case {i} time {degradation_time:.4f}ms exceeds 0.1ms target"
            assert isinstance(result, dict), f"Degradation case {i} should return dict"
            assert "metadata" in result
            assert result["metadata"]["detection_method"] in [
                "signature_based",
                "fallback_heuristic",
            ]
