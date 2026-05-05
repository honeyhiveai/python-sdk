"""Test migration scenarios from main branch patterns to complete-refactor.

This module tests real-world migration scenarios to validate backward compatibility
and identify any breaking changes users would encounter.
"""

import asyncio
import os
from unittest.mock import MagicMock, patch

import pytest


class TestMainBranchMigration:
    """Test migration from main branch usage patterns."""

    def setup_method(self):
        """Set up test environment."""
        self.original_env = os.environ.copy()
        os.environ["HH_API_KEY"] = "hh_test_key_12345"
        os.environ["HH_PROJECT"] = "test-project"  # Old pattern
        os.environ["HH_SOURCE"] = "test"

    def teardown_method(self):
        """Clean up environment."""
        os.environ.clear()
        os.environ.update(self.original_env)

    @patch("honeyhive.api.client.HoneyHive")
    def test_main_branch_tracer_init_pattern(self, mock_client):
        """Test main branch HoneyHiveTracer initialization pattern."""
        from honeyhive import HoneyHiveTracer

        # Mock session creation
        mock_session_response = MagicMock()
        mock_session_response.session_id = "test-session-123"
        mock_client.return_value.sessions.start_session.return_value = (
            mock_session_response
        )

        # Main branch pattern (with project parameter)
        tracer = HoneyHiveTracer(
            api_key="hh_test_key_12345",
            project="my-project",  # This was required in main branch
            session_name="test-session",
            source="production",
        )

        # Should work without errors
        assert tracer is not None
        assert hasattr(tracer, "session_id")

    def test_main_branch_imports(self):
        """Test that all main branch imports still work."""
        # These were the main exports in main branch
        try:
            from honeyhive import (
                HoneyHiveTracer,
                aevaluator,
                atrace,
                config,
                enrich_span,
                evaluate,
                evaluator,
                trace,
            )

            # Verify they're all importable
            assert HoneyHiveTracer is not None
            assert trace is not None
            assert atrace is not None
            assert enrich_span is not None
            assert evaluate is not None
            assert evaluator is not None
            assert aevaluator is not None
            assert config is not None

        except ImportError as e:
            pytest.fail(f"Main branch imports failed: {e}")

    def test_main_branch_dotdict_compatibility(self):
        """Test that dotdict (now DotDict) still works."""
        from honeyhive import DotDict

        # Main branch used lowercase 'dotdict', now it's 'DotDict'
        # But the functionality should be the same
        data = DotDict({"nested": {"value": 42}})
        assert data.nested.value == 42

    @patch("honeyhive.api.client.HoneyHive")
    def test_main_branch_decorator_patterns(self, mock_client):
        """Test that decorators work the same as main branch."""
        from honeyhive import atrace, trace

        # Mock session creation for tracer initialization
        mock_session_response = MagicMock()
        mock_session_response.session_id = "test-session-123"
        mock_client.return_value.sessions.start_session.return_value = (
            mock_session_response
        )

        @trace
        def sync_function(x, y):
            return x + y

        @atrace
        async def async_function(x, y):
            await asyncio.sleep(0.001)  # Simulate async work
            return x + y

        # Test sync function
        result = sync_function(1, 2)
        assert result == 3

        # Test async function
        async def run_async_test():
            result = await async_function(3, 4)
            assert result == 7

        asyncio.run(run_async_test())

    def test_main_branch_evaluator_decorator(self):
        """Test that evaluator decorator works like main branch."""
        from honeyhive import evaluator

        @evaluator
        def test_evaluator(output, inputs, ground_truth):
            return {"score": 1.0, "passed": True}

        # Should be callable
        assert callable(test_evaluator)

        # Should work when called
        result = test_evaluator("test output", {"input": "test"}, {"expected": "test"})
        assert result["score"] == 1.0
        assert result["passed"] is True

    def test_environment_variables_compatibility(self):
        """Test that environment variables work as expected."""
        # Main branch relied heavily on environment variables
        assert os.getenv("HH_API_KEY") == "hh_test_key_12345"
        assert os.getenv("HH_PROJECT") == "test-project"
        assert os.getenv("HH_SOURCE") == "test"

    @patch("honeyhive.api.client.HoneyHive")
    def test_main_branch_init_static_method(self, mock_client):
        """Test the legacy HoneyHiveTracer.init() static method."""
        from honeyhive import HoneyHiveTracer

        # Mock session creation
        mock_session_response = MagicMock()
        mock_session_response.session_id = "test-session-123"
        mock_client.return_value.sessions.start_session.return_value = (
            mock_session_response
        )

        # Main branch used HoneyHiveTracer.init() pattern
        tracer = HoneyHiveTracer.init(
            api_key="hh_test_key_12345",
            project="my-project",
            session_name="test-session",
        )

        assert tracer is not None
        assert hasattr(tracer, "session_id")


class TestNewFeatures:
    """Test new features available in complete-refactor that weren't in main."""

    def setup_method(self):
        """Set up test environment."""
        self.original_env = os.environ.copy()
        os.environ["HH_API_KEY"] = "hh_test_key_12345"

    def teardown_method(self):
        """Clean up environment."""
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_new_evaluation_features(self):
        """Test new evaluation features not available in main."""
        from honeyhive import (
            BaseEvaluator,
            EvaluationContext,
            EvaluationResult,
            evaluate_batch,
            evaluate_decorator,
        )

        # These should all be importable (new features)
        assert evaluate_batch is not None
        assert evaluate_decorator is not None
        assert BaseEvaluator is not None
        assert EvaluationResult is not None
        assert EvaluationContext is not None

    def test_new_tracer_features(self):
        """Test new tracer features not available in main."""
        from honeyhive import set_default_tracer, trace_class

        # These are new features
        assert trace_class is not None
        assert set_default_tracer is not None

    def test_enhanced_api_client(self):
        """Test the enhanced HoneyHive API client."""
        from honeyhive import HoneyHive

        # Should be able to instantiate without project parameter
        client = HoneyHive(api_key="hh_test_key_12345")
        assert client is not None

    def test_custom_evaluator_base_class(self):
        """Test creating custom evaluators with BaseEvaluator."""
        from honeyhive import BaseEvaluator

        class CustomEvaluator(BaseEvaluator):
            def evaluate(self, output, inputs, ground_truth, context=None):
                return {"custom_metric": len(str(output))}

        evaluator = CustomEvaluator()
        result = evaluator.evaluate("test output", {}, {})
        assert result["custom_metric"] == len("test output")

    @patch("honeyhive.api.client.HoneyHive")
    def test_multi_instance_tracers(self, mock_client):
        """Test multi-instance tracer support (new feature)."""
        from honeyhive import HoneyHiveTracer

        # Mock session creation
        mock_session_response = MagicMock()
        mock_session_response.session_id = "test-session-123"
        mock_client.return_value.sessions.start_session.return_value = (
            mock_session_response
        )

        # Should be able to create multiple independent tracers
        tracer1 = HoneyHiveTracer(session_name="session1")
        tracer2 = HoneyHiveTracer(session_name="session2")

        assert tracer1 is not None
        assert tracer2 is not None
        assert tracer1 != tracer2


class TestBreakingChanges:
    """Test for potential breaking changes and their workarounds."""

    def setup_method(self):
        """Set up test environment."""
        self.original_env = os.environ.copy()
        os.environ["HH_API_KEY"] = "hh_test_key_12345"

    def teardown_method(self):
        """Clean up environment."""
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_project_parameter_handling(self):
        """Test how project parameter is handled (potential breaking change)."""
        from honeyhive import HoneyHiveTracer

        # Project parameter should be accepted but potentially ignored
        # This tests the backward compatibility
        try:
            tracer = HoneyHiveTracer(
                api_key="hh_test_key_12345",
                project="test-project",  # This might be ignored
                session_name="test",
            )
            # Should not raise an error
            assert tracer is not None
        except Exception as e:
            pytest.fail(f"Project parameter caused error: {e}")

    def test_import_path_changes(self):
        """Test for any import path changes that could break code."""
        # Test that old import patterns still work
        try:
            # These should all work for backward compatibility
            from honeyhive import HoneyHiveTracer, evaluate, trace

            assert all([HoneyHiveTracer, trace, evaluate])
        except ImportError as e:
            pytest.fail(f"Import path changed in breaking way: {e}")

    def test_enrich_session_vs_enrich_span(self):
        """Test the change from enrich_session to enrich_span."""
        from honeyhive import enrich_span

        # enrich_session might not be available anymore
        # But enrich_span should work
        try:
            enrich_span(metadata={"test": "value"})
            # Should not raise an error
        except Exception as e:
            pytest.fail(f"enrich_span failed: {e}")

        # Test if enrich_session is still available for compatibility
        try:
            from honeyhive.tracer import enrich_session

            # If available, it should work
            enrich_session(metadata={"test": "value"})
        except ImportError:
            # It's okay if enrich_session is not available
            # As long as enrich_span works
            pass
        except Exception as e:
            pytest.fail(f"enrich_session compatibility broken: {e}")


class TestPerformanceCompatibility:
    """Test that performance characteristics are maintained or improved."""

    def setup_method(self):
        """Set up test environment."""
        self.original_env = os.environ.copy()
        os.environ["HH_API_KEY"] = "hh_test_key_12345"

    def teardown_method(self):
        """Clean up environment."""
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_tracer_initialization_speed(self):
        """Test that tracer initialization isn't significantly slower."""
        import time

        from honeyhive import HoneyHiveTracer

        start_time = time.time()

        # Initialize tracer
        tracer = HoneyHiveTracer(
            api_key="hh_test_key_12345", test_mode=True  # Avoid actual API calls
        )

        end_time = time.time()
        initialization_time = end_time - start_time

        # Should initialize within reasonable time (< 1 second)
        assert (
            initialization_time < 1.0
        ), f"Initialization took {initialization_time} seconds"
        assert tracer is not None

    def test_decorator_overhead(self):
        """Test that decorator overhead is minimal."""
        import time

        from honeyhive import trace

        @trace
        def test_function():
            return "result"

        # Measure execution time
        start_time = time.time()
        for _ in range(100):
            result = test_function()
        end_time = time.time()

        execution_time = end_time - start_time

        # Should not add significant overhead
        assert (
            execution_time < 1.0
        ), f"100 decorated calls took {execution_time} seconds"
        assert result == "result"
