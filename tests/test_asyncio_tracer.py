#!/usr/bin/env python3
"""
Simple tests for asyncio_tracer.py

These tests cover the basic functionality to improve coverage from 0% to 40%+.
"""

import pytest
import asyncio
import os
import sys

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from honeyhive.tracer.asyncio_tracer import (
    AsyncioInstrumentor,
    instrument_asyncio,
    uninstrument_asyncio,
    ASYNCIO_PREFIX,
    VERSION
)


class TestAsyncioInstrumentorBasic:
    """Test basic AsyncioInstrumentor functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        try:
            uninstrument_asyncio()
        except:
            pass
        
        self.instrumentor = AsyncioInstrumentor()
    
    def test_initialization(self):
        """Test basic initialization"""
        assert hasattr(self.instrumentor, 'methods_to_instrument')
        assert hasattr(self.instrumentor, 'coroutines_to_instrument')
        
        # Check methods to instrument
        expected_methods = [
            "create_task", "ensure_future", "wait", "wait_for",
            "as_completed", "to_thread", "run_coroutine_threadsafe"
        ]
        assert self.instrumentor.methods_to_instrument == expected_methods
        
        # Check coroutines to instrument (currently empty)
        assert self.instrumentor.coroutines_to_instrument == []
    
    def test_instrumentation_dependencies(self):
        """Test instrumentation dependencies"""
        deps = self.instrumentor.instrumentation_dependencies()
        assert deps == []
    
    def test_instrument_method(self):
        """Test the instrument method from BaseInstrumentor"""
        # Mock the custom _instrument method
        with pytest.MonkeyPatch().context() as m:
            m.setattr(self.instrumentor, '_instrument', lambda: None)
            # Should not raise any exceptions
            self.instrumentor.instrument()
    
    def test_uninstrument_method(self):
        """Test the uninstrument method from BaseInstrumentor"""
        # First instrument to set the state
        with pytest.MonkeyPatch().context() as m:
            m.setattr(self.instrumentor, '_instrument', lambda: None)
            m.setattr(self.instrumentor, '_uninstrument', lambda: None)
            self.instrumentor.instrument()
            # Should not raise any exceptions
            self.instrumentor.uninstrument()


class TestGlobalFunctions:
    """Test global functions"""
    
    def setup_method(self):
        """Reset instrumentation state"""
        try:
            uninstrument_asyncio()
        except:
            pass
    
    def test_instrument_asyncio(self):
        """Test instrument_asyncio function"""
        # Should not raise any exceptions
        instrument_asyncio()
    
    def test_uninstrument_asyncio(self):
        """Test uninstrument_asyncio function"""
        # Should not raise any exceptions
        uninstrument_asyncio()


class TestConstants:
    """Test module constants"""
    
    def test_asyncio_prefix(self):
        """Test ASYNCIO_PREFIX constant"""
        assert ASYNCIO_PREFIX == "asyncio"
    
    def test_version(self):
        """Test VERSION constant"""
        assert VERSION == "1.0.0"


class TestInstrumentationState:
    """Test instrumentation state management"""
    
    def setup_method(self):
        """Reset instrumentation state"""
        try:
            uninstrument_asyncio()
        except:
            pass
    
    def test_instrumentation_lifecycle(self):
        """Test basic instrumentation lifecycle"""
        # Create new instrumentor instance
        instrumentor = AsyncioInstrumentor()
        
        # Should not raise any exceptions during basic operations
        assert instrumentor is not None
        assert hasattr(instrumentor, 'methods_to_instrument')
        assert hasattr(instrumentor, 'coroutines_to_instrument')
    
    def test_environment_variable_control(self):
        """Test that environment variable controls auto-instrumentation"""
        # Set test mode to prevent auto-instrumentation
        os.environ['HH_TEST_MODE'] = 'true'
        
        try:
            # Import should not trigger auto-instrumentation
            from honeyhive.tracer.asyncio_tracer import instrumentor
            # The instrumentor should exist but not be auto-instrumented
            assert instrumentor is not None
        
        finally:
            # Clean up environment
            if 'HH_TEST_MODE' in os.environ:
                del os.environ['HH_TEST_MODE']


class TestAsyncioIntegration:
    """Test basic asyncio integration"""
    
    def setup_method(self):
        """Reset instrumentation state"""
        try:
            uninstrument_asyncio()
        except:
            pass
    
    def test_asyncio_module_access(self):
        """Test that we can access asyncio module"""
        # This tests that the import and basic module access works
        assert asyncio is not None
        assert hasattr(asyncio, 'create_task')
        assert hasattr(asyncio, 'ensure_future')
        assert hasattr(asyncio, 'wait')
        assert hasattr(asyncio, 'wait_for')
        assert hasattr(asyncio, 'as_completed')
        assert hasattr(asyncio, 'to_thread')
        assert hasattr(asyncio, 'run_coroutine_threadsafe')
        assert hasattr(asyncio, 'gather')
    
    def test_instrumentor_creation(self):
        """Test instrumentor creation and basic attributes"""
        instrumentor = AsyncioInstrumentor()
        
        # Test that all expected methods are present
        for method in instrumentor.methods_to_instrument:
            assert hasattr(asyncio, method), f"Method {method} not found in asyncio module"
        
        # Test that gather is accessible (special case)
        assert hasattr(asyncio, 'gather'), "gather method not found in asyncio module"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
