"""Test verbose logging functionality for the HoneyHive client."""

import pytest
import logging
import os
from unittest.mock import patch, MagicMock
from honeyhive.api.client import HoneyHive
from honeyhive.utils.config import config


class TestVerboseLogging:
    """Test verbose logging functionality."""
    
    def test_verbose_flag_in_client_init(self):
        """Test that verbose flag is properly set in client initialization."""
        # Test with verbose=True
        client = HoneyHive(api_key="test-key", verbose=True)
        assert client.verbose is True
        
        # Test with verbose=False
        client = HoneyHive(api_key="test-key", verbose=False)
        assert client.verbose is False
        
        # Test default from config
        config.verbose = True
        client = HoneyHive(api_key="test-key")
        assert client.verbose is True
        
        # Reset config
        config.verbose = False
    
    def test_verbose_logger_level(self):
        """Test that verbose mode sets logger to DEBUG level."""
        # Test verbose=True - should create logger with DEBUG level
        with patch('honeyhive.api.client.get_logger') as mock_get_logger:
            mock_logger = MagicMock()
            mock_get_logger.return_value = mock_logger
            
            # Create client after patching get_logger
            client = HoneyHive(api_key="test-key", verbose=True)
            
            # Verify that get_logger was called with DEBUG level for verbose mode
            mock_get_logger.assert_called_with("honeyhive.client", level="DEBUG")
            
            # Test verbose=False - should create logger without level specification
            mock_get_logger.reset_mock()
            client = HoneyHive(api_key="test-key", verbose=False)
            mock_get_logger.assert_called_with("honeyhive.client")
    
    def test_verbose_environment_variable(self):
        """Test that HH_VERBOSE environment variable is respected."""
        # Set environment variable
        os.environ["HH_VERBOSE"] = "true"
        
        # Reload config to pick up environment variable
        config.reload()
        
        # Test that config.verbose is True
        assert config.verbose is True
        
        # Clean up
        del os.environ["HH_VERBOSE"]
        config.reload()
        assert config.verbose is False
    
    def test_verbose_logging_in_request(self):
        """Test that verbose logging is used in request methods."""
        # Create a client with verbose mode
        client = HoneyHive(api_key="test-key", verbose=True)
        
        # Mock the logger to capture calls
        original_logger = client.logger
        mock_logger = MagicMock()
        client.logger = mock_logger
        
        # Mock the HTTP client to avoid real requests
        with patch('httpx.Client') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {"Content-Type": "application/json"}
            mock_response.elapsed = MagicMock()
            mock_response.elapsed.total_seconds.return_value = 0.1
            mock_client.request.return_value = mock_response
            
            # Mock retry config
            client.retry_config.should_retry = MagicMock(return_value=False)
            
            # Make a request
            client.request("GET", "/test")
            
            # Verify that verbose logging was called for both request and response
            assert mock_logger.info.call_count >= 2  # Request and response logs
            
            # Check that request details were logged
            request_log_calls = [call for call in mock_logger.info.call_args_list 
                               if "API Request Details" in str(call)]
            assert len(request_log_calls) > 0
            
            # Check that response details were logged
            response_log_calls = [call for call in mock_logger.info.call_args_list 
                                if "API Response Details" in str(call)]
            assert len(response_log_calls) > 0
        
        # Restore original logger
        client.logger = original_logger
    
    def test_verbose_logging_in_async_request(self):
        """Test that verbose logging is used in async request methods."""
        # Create a client with verbose mode
        client = HoneyHive(api_key="test-key", verbose=True)
        
        # Mock the logger to capture calls
        original_logger = client.logger
        mock_logger = MagicMock()
        client.logger = mock_logger
        
        # Mock the async HTTP client
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {"Content-Type": "application/json"}
            mock_response.elapsed = MagicMock()
            mock_response.elapsed.total_seconds.return_value = 0.1
            
            # Make the mock client.request return an awaitable
            async def mock_request(*args, **kwargs):
                return mock_response
            
            mock_client.request = mock_request
            
            # Mock retry config
            client.retry_config.should_retry = MagicMock(return_value=False)
            
            # Make an async request
            import asyncio
            asyncio.run(client.request_async("GET", "/test"))
            
            # Verify that verbose logging was called for both request and response
            assert mock_logger.info.call_count >= 2  # Request and response logs
            
            # Check that request details were logged
            request_log_calls = [call for call in mock_logger.info.call_args_list 
                               if "API Request Details" in str(call)]
            assert len(request_log_calls) > 0
            
            # Check that response details were logged
            response_log_calls = [call for call in mock_logger.info.call_args_list 
                                if "API Async Response Details" in str(call)]
            assert len(response_log_calls) > 0
        
        # Restore original logger
        client.logger = original_logger
    
    def test_verbose_logging_in_error_handling(self):
        """Test that verbose logging is used in error handling."""
        # Create a client with verbose mode
        client = HoneyHive(api_key="test-key", verbose=True)
        
        # Mock the logger to capture calls
        original_logger = client.logger
        mock_logger = MagicMock()
        client.logger = mock_logger
        
        # Mock the HTTP client to raise an exception
        with patch('httpx.Client') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_client.request.side_effect = Exception("Test error")
            
            # Mock retry config
            client.retry_config.should_retry_exception = MagicMock(return_value=False)
            
            # Make a request that will fail
            with pytest.raises(Exception):
                client.request("GET", "/test")
            
            # Verify that verbose error logging was called
            mock_logger.error.assert_called_once()
            error_call = mock_logger.error.call_args
            assert "API Request Failed" in error_call[0][0]
            assert "honeyhive_data" in error_call[1]
        
        # Restore original logger
        client.logger = original_logger
    
    def test_client_initialization_log_includes_verbose(self):
        """Test that client initialization log includes verbose flag."""
        # Create a client with verbose mode
        client = HoneyHive(api_key="test-key", verbose=True)
        
        # Mock the logger to capture calls
        original_logger = client.logger
        mock_logger = MagicMock()
        client.logger = mock_logger
        
        # Re-initialize to trigger the log message
        client.logger.info("HoneyHive client initialized", honeyhive_data={
            "base_url": client.base_url,
            "test_mode": client.test_mode,
            "verbose": client.verbose
        })
        
        # Verify that the initialization log includes verbose flag
        mock_logger.info.assert_called_once()
        init_call = mock_logger.info.call_args
        assert "HoneyHive client initialized" in init_call[0][0]
        assert init_call[1]["honeyhive_data"]["verbose"] is True
        
        # Restore original logger
        client.logger = original_logger
