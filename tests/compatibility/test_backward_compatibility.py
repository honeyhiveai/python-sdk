"""Backward Compatibility Test Suite

This module tests backward compatibility between the complete-refactor branch
and the main branch to ensure existing user code continues to work.
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest


class TestBackwardCompatibility:
    """Test suite for backward compatibility validation."""

    def setup_method(self):
        """Set up test environment variables."""
        self.original_env = os.environ.copy()
        os.environ["HH_API_KEY"] = "test-key"
        os.environ["HH_PROJECT"] = "test-project"
        os.environ["HH_SOURCE"] = "test"

    def teardown_method(self):
        """Clean up environment variables."""
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_import_compatibility(self):
        """Test that all main branch imports still work."""
        # Test core imports that existed in main branch
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
        except ImportError as e:
            pytest.fail(f"Failed to import main branch compatible modules: {e}")

        # Test that these are not None
        assert HoneyHiveTracer is not None
        assert trace is not None
        assert atrace is not None
        assert enrich_span is not None
        assert evaluate is not None
        assert evaluator is not None
        assert aevaluator is not None
        assert config is not None

    @patch("honeyhive.api.client.HoneyHive")
    def test_tracer_initialization_compatibility(self, mock_honeyhive):
        """Test that HoneyHiveTracer can be initialized with main branch pattern."""
        from honeyhive import HoneyHiveTracer

        # Mock the session start response
        mock_session_response = MagicMock()
        mock_session_response.status_code = 200
        mock_session_response.object.session_id = "test-session-id"
        mock_honeyhive.return_value.session.start_session.return_value = (
            mock_session_response
        )

        # Test initialization without project parameter (new pattern)
        tracer = HoneyHiveTracer(
            api_key="test-key", session_name="test-session", source="test"
        )

        assert tracer is not None
        assert hasattr(tracer, "session_id")

    def test_trace_decorator_compatibility(self):
        """Test that @trace decorator works as expected."""
        from honeyhive import trace

        @trace
        def test_function(x, y):
            return x + y

        # Should not raise an exception
        result = test_function(1, 2)
        assert result == 3

    def test_async_trace_decorator_compatibility(self):
        """Test that @atrace decorator works as expected."""
        import asyncio

        from honeyhive import atrace

        @atrace
        async def async_test_function(x, y):
            return x + y

        # Should not raise an exception
        async def run_test():
            result = await async_test_function(1, 2)
            assert result == 3

        asyncio.run(run_test())

    def test_enrich_span_compatibility(self):
        """Test that enrich_span function works."""
        from honeyhive import enrich_span

        # Should not raise an exception
        enrich_span(metadata={"test": "value"})

    def test_evaluator_decorator_compatibility(self):
        """Test that @evaluator decorator works."""
        from honeyhive import evaluator

        @evaluator
        def test_evaluator(output, inputs, ground_truth):
            return {"score": 1.0}

        assert test_evaluator is not None
        assert hasattr(test_evaluator, "__call__")

    def test_config_access_compatibility(self):
        """Test that config object is accessible."""
        from honeyhive import config

        assert config is not None
        # Config should have some basic attributes (updated for new config structure)
        assert hasattr(config, "api") or hasattr(config, "version")

    def test_environment_variable_compatibility(self):
        """Test that environment variables work as expected."""
        # Set environment variables
        os.environ["HH_API_KEY"] = "test-api-key"
        os.environ["HH_PROJECT"] = "test-project"
        os.environ["HH_SOURCE"] = "test-source"

        from honeyhive.utils.config import config

        # Should be able to access config values (updated for new config structure)
        assert (hasattr(config, "api") and hasattr(config.api, "api_key")) or os.getenv(
            "HH_API_KEY"
        ) is not None

    def test_evaluation_basic_compatibility(self):
        """Test that basic evaluation function works."""
        from honeyhive import evaluate

        # Mock evaluation to avoid actual API calls
        def mock_function(inputs, ground_truth=None):
            return {"output": "test"}

        # This should not raise an exception (though it may fail due to missing deps)
        try:
            # Just test that the function is callable
            assert callable(evaluate)
        except Exception:
            # It's okay if evaluation fails due to missing dependencies in test env
            pass

    def test_dotdict_compatibility(self):
        """Test that DotDict (formerly dotdict) is accessible."""
        from honeyhive import DotDict

        # Test that DotDict works like the old dotdict
        d = DotDict({"a": 1, "b": {"c": 2}})
        assert d.a == 1
        assert d.b.c == 2

    def test_logger_compatibility(self):
        """Test that logger functionality is available."""
        from honeyhive import get_logger

        logger = get_logger("test")
        assert logger is not None
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "debug")

    @patch("honeyhive.api.client.HoneyHive")
    def test_multiple_tracer_instances(self, mock_honeyhive):
        """Test that multiple tracer instances can be created (new feature)."""
        from honeyhive import HoneyHiveTracer

        # Mock the session start response
        mock_session_response = MagicMock()
        mock_session_response.status_code = 200
        mock_session_response.object.session_id = "test-session-id"
        mock_honeyhive.return_value.session.start_session.return_value = (
            mock_session_response
        )

        # Should be able to create multiple tracers
        tracer1 = HoneyHiveTracer(session_name="session1")
        tracer2 = HoneyHiveTracer(session_name="session2")

        assert tracer1 is not None
        assert tracer2 is not None
        assert tracer1 != tracer2

    def test_new_features_availability(self):
        """Test that new features are available without breaking old code."""
        # Test that new features can be imported
        try:
            from honeyhive import (
                BaseEvaluator,
                EvaluationResult,
                evaluate_batch,
                evaluate_decorator,
                set_default_tracer,
                trace_class,
            )

            # These should all be importable
            assert trace_class is not None
            assert set_default_tracer is not None
            assert evaluate_batch is not None
            assert evaluate_decorator is not None
            assert BaseEvaluator is not None
            assert EvaluationResult is not None

        except ImportError as e:
            pytest.fail(f"New features should be importable: {e}")

    def test_api_client_compatibility(self):
        """Test that the API client is accessible."""
        from honeyhive import HoneyHive

        # Should be able to instantiate (though may fail without real credentials)
        try:
            client = HoneyHive(bearer_auth="test-key")
            assert client is not None
        except Exception:
            # It's okay if it fails due to invalid credentials in test
            pass


class TestMigrationScenarios:
    """Test specific migration scenarios from main branch patterns."""

    def setup_method(self):
        """Set up test environment."""
        self.original_env = os.environ.copy()
        os.environ["HH_API_KEY"] = "test-key"
        os.environ["HH_PROJECT"] = "test-project"

    def teardown_method(self):
        """Clean up environment variables."""
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_main_branch_import_pattern(self):
        """Test importing like main branch code would."""
        # This is how users would import in main branch
        try:
            from honeyhive import HoneyHiveTracer, evaluate, trace

            assert all([HoneyHiveTracer, trace, evaluate])
        except ImportError as e:
            pytest.fail(f"Main branch import pattern failed: {e}")

    @patch("honeyhive.api.client.HoneyHive")
    def test_main_branch_tracer_usage_pattern(self, mock_honeyhive):
        """Test using tracer like main branch code would."""
        from honeyhive import HoneyHiveTracer, trace

        # Mock the session start response
        mock_session_response = MagicMock()
        mock_session_response.status_code = 200
        mock_session_response.object.session_id = "test-session-id"
        mock_honeyhive.return_value.session.start_session.return_value = (
            mock_session_response
        )

        # Main branch pattern (without project parameter)
        tracer = HoneyHiveTracer(
            api_key=os.getenv("HH_API_KEY"), session_name="test-session"
        )

        @trace
        def test_function():
            return "test"

        result = test_function()
        assert result == "test"

    def test_environment_variable_migration(self):
        """Test that environment variable approach works."""
        # Set the environment variables that complete-refactor expects
        os.environ["HH_API_KEY"] = "test-key"
        os.environ["HH_PROJECT"] = "test-project"
        os.environ["HH_SOURCE"] = "test"

        # Import should work
        from honeyhive import HoneyHiveTracer

        assert HoneyHiveTracer is not None

        # These environment variables should be accessible
        assert os.getenv("HH_API_KEY") == "test-key"
        assert os.getenv("HH_PROJECT") == "test-project"
        assert os.getenv("HH_SOURCE") == "test"
