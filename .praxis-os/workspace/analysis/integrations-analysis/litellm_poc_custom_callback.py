#!/usr/bin/env python3
"""
Proof of Concept: HoneyHive LiteLLM Custom Callback

This demonstrates how a custom callback can capture complete LiteLLM metadata.

NOTE: This is a POC/mockup. HoneyHive team would need to:
1. Replace MockHoneyHiveClient with real HoneyHive SDK
2. Adjust trace_data structure to match HoneyHive API
3. Add error handling and retry logic
4. Add async support for async_log_success_event

Usage:
    python litellm_poc_custom_callback.py
"""

from typing import Any, Dict, Optional, Union
from litellm.integrations.custom_logger import CustomLogger
import time
import json


class MockHoneyHiveClient:
    """Mock HoneyHive client for POC purposes."""
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
    
    def log_trace(self, trace_data: Dict[str, Any]):
        """Mock log_trace - in real implementation, this would call HoneyHive API."""
        print("\n" + "="*80)
        print("📊 HoneyHive Trace Logged")
        print("="*80)
        print(json.dumps(trace_data, indent=2, default=str))
        print("="*80 + "\n")


class HoneyHiveLogger(CustomLogger):
    """
    LiteLLM callback for logging to HoneyHive.
    
    Captures complete LiteLLM metadata including:
    - Provider-specific details
    - Router deployment information
    - Proxy virtual key/team tracking
    - Raw requests/responses (optional)
    - Custom metadata
    """
    
    def __init__(
        self,
        api_key: str,
        project: str,
        environment: str = "development",
        api_url: str = "https://api.honeyhive.ai",
        capture_message_content: bool = True,
        capture_raw_request: bool = False,
        debug: bool = False,
    ):
        super().__init__()
        self.api_key = api_key
        self.project = project
        self.environment = environment
        self.api_url = api_url
        self.capture_message_content = capture_message_content
        self.capture_raw_request = capture_raw_request
        self.debug = debug
        
        # Initialize mock client (replace with real HoneyHive SDK)
        self._client = MockHoneyHiveClient(
            api_key=api_key,
            base_url=api_url
        )
    
    def log_success_event(
        self,
        kwargs: Dict[str, Any],
        response_obj: Any,
        start_time: Union[float, None],
        end_time: Union[float, None],
    ):
        """Called after successful LiteLLM completion."""
        try:
            trace_data = self._build_trace_data(
                kwargs=kwargs,
                response_obj=response_obj,
                start_time=start_time,
                end_time=end_time,
                error=None,
            )
            
            self._client.log_trace(trace_data)
        
        except Exception as e:
            if self.debug:
                print(f"[HoneyHive] Error logging trace: {e}")
                import traceback
                traceback.print_exc()
    
    def log_failure_event(
        self,
        kwargs: Dict[str, Any],
        response_obj: Any,
        start_time: Union[float, None],
        end_time: Union[float, None],
    ):
        """Called after failed LiteLLM completion."""
        try:
            trace_data = self._build_trace_data(
                kwargs=kwargs,
                response_obj=None,
                start_time=start_time,
                end_time=end_time,
                error=response_obj,
            )
            
            self._client.log_trace(trace_data)
        
        except Exception as e:
            if self.debug:
                print(f"[HoneyHive] Error logging failure: {e}")
    
    def _build_trace_data(
        self,
        kwargs: Dict[str, Any],
        response_obj: Any,
        start_time: Optional[float],
        end_time: Optional[float],
        error: Optional[Any],
    ) -> Dict[str, Any]:
        """Build complete trace data structure."""
        
        # Extract LiteLLM parameters
        litellm_params = kwargs.get("litellm_params", {})
        metadata = kwargs.get("metadata", {}) or litellm_params.get("metadata", {})
        
        # Core fields
        model = kwargs.get("model", "unknown")
        custom_llm_provider = litellm_params.get("custom_llm_provider", "unknown")
        
        # Build trace
        trace_data = {
            "trace_id": self._generate_trace_id(litellm_params, start_time),
            "project": self.project,
            "environment": self.environment,
            "timestamp": start_time,
            "duration_ms": int((end_time - start_time) * 1000) if start_time and end_time else None,
            
            # LiteLLM metadata
            "provider": custom_llm_provider,
            "model": model,
            "litellm_version": self._get_litellm_version(),
            
            # User metadata
            "metadata": metadata,
            
            # Success/failure
            "success": error is None,
            "error": self._extract_error_info(error) if error else None,
        }
        
        # Input
        if self.capture_message_content:
            trace_data["input"] = {
                "messages": kwargs.get("messages", []),
                "parameters": self._extract_parameters(kwargs),
            }
        
        # Output
        if response_obj and not error:
            trace_data["output"] = self._extract_output(response_obj)
            
            # Usage
            if hasattr(response_obj, "usage"):
                trace_data["usage"] = self._extract_usage(response_obj.usage)
        
        # Router information (if available)
        router_obj = litellm_params.get("router_obj")
        if router_obj:
            trace_data["router"] = {
                "routing_strategy": getattr(router_obj, "routing_strategy", None),
                "deployment_id": kwargs.get("specific_deployment"),
                "model_group": model,
            }
        
        # Proxy information (if available)
        proxy_request = litellm_params.get("proxy_server_request")
        if proxy_request:
            trace_data["proxy"] = {
                "virtual_key_hash": proxy_request.get("api_key_hash"),
                "team_id": proxy_request.get("team_id"),
                "user_id": proxy_request.get("user_id"),
                "request_id": proxy_request.get("request_id"),
            }
        
        return trace_data
    
    def _extract_parameters(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Extract model parameters."""
        param_keys = [
            "temperature", "top_p", "max_tokens", "stream",
            "tools", "tool_choice", "response_format",
        ]
        return {k: kwargs.get(k) for k in param_keys if k in kwargs}
    
    def _extract_output(self, response_obj: Any) -> Dict[str, Any]:
        """Extract response data."""
        output = {}
        if hasattr(response_obj, "choices") and response_obj.choices:
            choice = response_obj.choices[0]
            if hasattr(choice, "message"):
                message = choice.message
                if self.capture_message_content:
                    output["content"] = getattr(message, "content", None)
                    output["tool_calls"] = getattr(message, "tool_calls", None)
                output["finish_reason"] = getattr(choice, "finish_reason", None)
        return output
    
    def _extract_usage(self, usage: Any) -> Dict[str, Any]:
        """Extract usage data."""
        return {
            "prompt_tokens": getattr(usage, "prompt_tokens", None),
            "completion_tokens": getattr(usage, "completion_tokens", None),
            "total_tokens": getattr(usage, "total_tokens", None),
        }
    
    def _extract_error_info(self, error: Any) -> Dict[str, Any]:
        """Extract error information."""
        return {
            "type": type(error).__name__,
            "message": str(error),
            "status_code": getattr(error, "status_code", None),
        }
    
    def _generate_trace_id(self, litellm_params: Dict[str, Any], start_time: Optional[float]) -> str:
        """Generate trace ID."""
        import uuid
        request_id = litellm_params.get("request_id")
        return request_id if request_id else str(uuid.uuid4())
    
    def _get_litellm_version(self) -> str:
        """Get LiteLLM version."""
        try:
            import litellm
            return getattr(litellm, "__version__", "unknown")
        except:
            return "unknown"


# ============================================================================
# POC DEMO
# ============================================================================

if __name__ == "__main__":
    print("\n" + "🚀" * 40)
    print("LiteLLM → HoneyHive Custom Callback POC")
    print("🚀" * 40 + "\n")
    
    import litellm
    import os
    
    # Initialize HoneyHive logger
    logger = HoneyHiveLogger(
        api_key="mock-api-key",  # Replace with real API key
        project="litellm-poc",
        environment="development",
        debug=True,
        capture_message_content=True,
    )
    
    # Register callback
    litellm.callbacks = [logger]
    
    # Test 1: Basic completion
    print("\n📝 Test 1: Basic OpenAI Completion")
    print("-" * 80)
    
    try:
        response = litellm.completion(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello!"}
            ],
            temperature=0.7,
            max_tokens=50,
            metadata={
                "test_id": "test-1",
                "user_id": "user-123",
                "feature": "demo"
            }
        )
        print(f"✅ Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ Error (expected if no API key): {e}")
    
    # Test 2: With custom provider
    print("\n📝 Test 2: Anthropic Completion")
    print("-" * 80)
    
    try:
        response = litellm.completion(
            model="anthropic/claude-3-opus",
            messages=[{"role": "user", "content": "Hello Claude!"}],
            max_tokens=100,
            metadata={"test_id": "test-2"}
        )
        print(f"✅ Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ Error (expected if no API key): {e}")
    
    print("\n" + "✨" * 40)
    print("POC Complete! Check logs above for captured metadata.")
    print("✨" * 40 + "\n")

