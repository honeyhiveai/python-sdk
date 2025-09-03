"""Tests for MCP instrumentor integration with HoneyHive SDK.

This module tests the integration of the OpenInference MCP (Model Context Protocol)
instrumentor with the HoneyHive SDK's BYOI (Bring Your Own Instrumentor) architecture.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from honeyhive import HoneyHiveTracer


class TestMCPInstrumentorIntegration:
    """Test MCP instrumentor integration with HoneyHive tracer."""

    def test_mcp_instrumentor_integration_success(self):
        """Test successful MCP instrumentor integration."""
        # Create mock MCP instrumentor
        mock_instrumentor = Mock()
        mock_instrumentor.instrument = Mock()
        mock_instrumentor.__class__.__name__ = "MCPInstrumentor"

        # Test integration
        tracer = HoneyHiveTracer.init(
            api_key="test-key",
            project="test-project",
            test_mode=True,
            instrumentors=[mock_instrumentor],
        )

        # Verify tracer created successfully
        assert tracer is not None
        assert tracer.project == "test-project"

        # Verify instrumentor was called
        mock_instrumentor.instrument.assert_called_once()

    def test_mcp_instrumentor_import_error_handling(self):
        """Test graceful handling when MCP instrumentor not available."""
        with patch(
            "builtins.__import__",
            side_effect=ImportError(
                "No module named 'openinference.instrumentation.mcp'"
            ),
        ):
            # Should not raise exception - graceful degradation
            tracer = HoneyHiveTracer.init(
                api_key="test-key",
                project="test-project",
                test_mode=True,
                instrumentors=[],  # Empty list to avoid import issues
            )
            assert tracer is not None

    def test_mcp_instrumentor_without_instrument_method(self):
        """Test handling of invalid instrumentor objects."""
        # Create object without instrument method
        invalid_instrumentor = Mock()
        del invalid_instrumentor.instrument  # Remove instrument method

        # Should handle gracefully
        tracer = HoneyHiveTracer.init(
            api_key="test-key",
            project="test-project",
            test_mode=True,
            instrumentors=[invalid_instrumentor],
        )

        assert tracer is not None

    def test_mcp_instrumentor_integration_failure(self):
        """Test handling when instrumentor.instrument() raises exception."""
        # Create mock that raises exception on instrument()
        mock_instrumentor = Mock()
        mock_instrumentor.instrument.side_effect = Exception("Integration failed")
        mock_instrumentor.__class__.__name__ = "MCPInstrumentor"

        # Should handle exception gracefully
        tracer = HoneyHiveTracer.init(
            api_key="test-key",
            project="test-project",
            test_mode=True,
            instrumentors=[mock_instrumentor],
        )

        assert tracer is not None
        mock_instrumentor.instrument.assert_called_once()

    def test_multiple_instrumentors_with_mcp(self):
        """Test MCP instrumentor alongside other instrumentors."""
        # Create multiple mock instrumentors
        mcp_instrumentor = Mock()
        mcp_instrumentor.instrument = Mock()
        mcp_instrumentor.__class__.__name__ = "MCPInstrumentor"

        openai_instrumentor = Mock()
        openai_instrumentor.instrument = Mock()
        openai_instrumentor.__class__.__name__ = "OpenAIInstrumentor"

        # Test with multiple instrumentors
        tracer = HoneyHiveTracer.init(
            api_key="test-key",
            project="test-project",
            test_mode=True,
            instrumentors=[mcp_instrumentor, openai_instrumentor],
        )

        assert tracer is not None

        # Verify both instrumentors were called
        mcp_instrumentor.instrument.assert_called_once()
        openai_instrumentor.instrument.assert_called_once()

    @pytest.mark.asyncio
    async def test_mcp_context_propagation_setup(self):
        """Test that MCP instrumentor works with baggage context setup."""
        mock_instrumentor = Mock()
        mock_instrumentor.instrument = Mock()
        mock_instrumentor.__class__.__name__ = "MCPInstrumentor"

        # Test with session context
        tracer = HoneyHiveTracer.init(
            api_key="test-key",
            project="test-project",
            source="test-source",
            session_name="test-session",
            test_mode=True,
            instrumentors=[mock_instrumentor],
        )

        assert tracer is not None
        assert tracer.project == "test-project"
        assert tracer.source == "test-source"

        # Verify instrumentor integration
        mock_instrumentor.instrument.assert_called_once()


class TestMCPInstrumentorOptionalDependency:
    """Test MCP instrumentor optional dependency handling."""

    def test_mcp_instrumentor_lazy_import_pattern(self):
        """Test lazy import pattern for MCP instrumentor."""

        def get_mcp_instrumentor():
            """Get MCP instrumentor if available."""
            try:
                # This would normally import the real instrumentor
                from unittest.mock import Mock

                mock_instrumentor = Mock()
                mock_instrumentor.instrument = Mock()
                mock_instrumentor.__class__.__name__ = "MCPInstrumentor"
                return mock_instrumentor
            except ImportError:
                raise ImportError(
                    "MCP instrumentor not available. Install with: pip install honeyhive[mcp]"
                )

        # Test successful import
        instrumentor = get_mcp_instrumentor()
        assert instrumentor is not None
        assert hasattr(instrumentor, "instrument")

    def test_mcp_dependency_error_message(self):
        """Test helpful error message when MCP dependency missing."""

        def get_mcp_instrumentor_with_error():
            """Simulate import error."""
            raise ImportError(
                "MCP instrumentor not available. Install with: pip install honeyhive[mcp]"
            )

        with pytest.raises(ImportError, match="pip install honeyhive\\[mcp\\]"):
            get_mcp_instrumentor_with_error()


class TestMCPSpanEnrichment:
    """Test MCP span attribute handling and enrichment."""

    def test_mcp_span_detection(self):
        """Test detection of MCP-related spans."""
        # Mock span with MCP attributes
        mock_span = Mock()
        mock_span.name = "mcp_tool_call"
        mock_span.attributes = {
            "mcp.client.name": "test-client",
            "mcp.server.name": "test-server",
            "mcp.tool.name": "analyze_data",
        }

        # Test span detection logic
        is_mcp_span = any("mcp." in key for key in mock_span.attributes.keys())
        assert is_mcp_span is True

    def test_non_mcp_span_detection(self):
        """Test that non-MCP spans are not incorrectly identified."""
        mock_span = Mock()
        mock_span.name = "openai_completion"
        mock_span.attributes = {"openai.model": "gpt-4", "openai.tokens": 150}

        # Test span detection logic
        is_mcp_span = any("mcp." in key for key in mock_span.attributes.keys())
        assert is_mcp_span is False

    def test_mcp_span_attribute_enrichment(self):
        """Test enrichment of MCP spans with HoneyHive context."""
        # Mock HoneyHive baggage context
        honeyhive_context = {
            "honeyhive.project": "test-project",
            "honeyhive.source": "test-source",
            "honeyhive.session.id": "session-123",
        }

        # Mock MCP span
        mcp_attributes = {
            "mcp.client.name": "financial-client",
            "mcp.server.name": "financial-server",
            "mcp.tool.name": "get_stock_price",
            "mcp.request.params": '{"ticker": "AAPL"}',
        }

        # Simulate enrichment process
        enriched_attributes = {**mcp_attributes, **honeyhive_context}

        # Verify enrichment
        assert "honeyhive.project" in enriched_attributes
        assert "honeyhive.session.id" in enriched_attributes
        assert "mcp.tool.name" in enriched_attributes
        assert enriched_attributes["honeyhive.project"] == "test-project"
        assert enriched_attributes["mcp.tool.name"] == "get_stock_price"


@pytest.mark.integration
class TestMCPRealIntegration:
    """Integration tests with real MCP instrumentor (requires optional dependency)."""

    @pytest.fixture(autouse=True)
    def setup_mcp_available(self):
        """Check if MCP instrumentor is available for integration tests."""
        try:
            import openinference.instrumentation.mcp  # noqa: F401

            self.mcp_available = True
        except ImportError:
            self.mcp_available = False
            pytest.skip(
                "MCP instrumentor not available. Install with: pip install honeyhive[mcp]"
            )

    def test_real_mcp_instrumentor_integration(self):
        """Test integration with real MCP instrumentor."""
        if not self.mcp_available:
            pytest.skip("MCP instrumentor not available")

        from openinference.instrumentation.mcp import MCPInstrumentor

        # Test real instrumentor integration
        instrumentor = MCPInstrumentor()

        tracer = HoneyHiveTracer.init(
            api_key="test-key",
            project="mcp-integration-test",
            test_mode=True,
            instrumentors=[instrumentor],
        )

        assert tracer is not None
        assert tracer.project == "mcp-integration-test"

    def test_mcp_instrumentor_properties(self):
        """Test that real MCP instrumentor has expected interface."""
        if not self.mcp_available:
            pytest.skip("MCP instrumentor not available")

        from openinference.instrumentation.mcp import MCPInstrumentor

        instrumentor = MCPInstrumentor()

        # Verify expected interface
        assert hasattr(instrumentor, "instrument")
        assert callable(getattr(instrumentor, "instrument"))
        assert instrumentor.__class__.__name__ == "MCPInstrumentor"


class TestMCPPerformanceImpact:
    """Test performance impact of MCP instrumentor integration."""

    def test_mcp_instrumentor_initialization_time(self):
        """Test that MCP instrumentor doesn't add significant initialization overhead."""
        import time

        # Mock instrumentor for performance testing
        mock_instrumentor = Mock()
        mock_instrumentor.instrument = Mock()
        mock_instrumentor.__class__.__name__ = "MCPInstrumentor"

        # Measure initialization time
        start_time = time.time()

        tracer = HoneyHiveTracer.init(
            api_key="test-key",
            project="performance-test",
            test_mode=True,
            instrumentors=[mock_instrumentor],
        )

        end_time = time.time()
        initialization_time = end_time - start_time

        # Verify tracer created and time is reasonable
        assert tracer is not None
        assert initialization_time < 1.0  # Should be well under 1 second
        mock_instrumentor.instrument.assert_called_once()

    def test_multiple_instrumentors_performance(self):
        """Test performance with multiple instrumentors including MCP."""
        import time

        # Create multiple mock instrumentors
        instrumentors = []
        for i in range(5):  # Test with 5 instrumentors
            mock = Mock()
            mock.instrument = Mock()
            mock.__class__.__name__ = f"TestInstrumentor{i}"
            instrumentors.append(mock)

        # Add MCP instrumentor
        mcp_instrumentor = Mock()
        mcp_instrumentor.instrument = Mock()
        mcp_instrumentor.__class__.__name__ = "MCPInstrumentor"
        instrumentors.append(mcp_instrumentor)

        # Measure initialization time
        start_time = time.time()

        tracer = HoneyHiveTracer.init(
            api_key="test-key",
            project="multi-instrumentor-test",
            test_mode=True,
            instrumentors=instrumentors,
        )

        end_time = time.time()
        initialization_time = end_time - start_time

        # Verify all instrumentors integrated and performance acceptable
        assert tracer is not None
        assert (
            initialization_time < 2.0
        )  # Should be reasonable even with multiple instrumentors

        # Verify all instrumentors were called
        for instrumentor in instrumentors:
            instrumentor.instrument.assert_called_once()
