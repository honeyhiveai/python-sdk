#!/usr/bin/env python3
"""
Proof of Concept: LiteLLM Router with HoneyHive

Demonstrates how the custom callback captures Router-specific metadata:
- Deployment selection
- Routing strategy
- Fallback information
- Load balancing decisions

Usage:
    python litellm_poc_router_example.py
"""

import litellm
from litellm import Router
import os
from litellm_poc_custom_callback import HoneyHiveLogger


def setup_router():
    """Set up a Router with multiple deployments."""
    
    model_list = [
        # OpenAI GPT-4 - Deployment 1
        {
            "model_name": "gpt-4",
            "litellm_params": {
                "model": "gpt-4",
                "api_key": os.getenv("OPENAI_API_KEY", "mock-key-1"),
            },
            "model_info": {
                "id": "openai-gpt4-primary"
            }
        },
        # OpenAI GPT-4 - Deployment 2 (fallback)
        {
            "model_name": "gpt-4",
            "litellm_params": {
                "model": "gpt-4",
                "api_key": os.getenv("OPENAI_API_KEY_2", "mock-key-2"),
            },
            "model_info": {
                "id": "openai-gpt4-secondary"
            }
        },
        # Azure GPT-4 - Deployment 3
        {
            "model_name": "gpt-4",
            "litellm_params": {
                "model": "azure/gpt-4-deployment",
                "api_key": os.getenv("AZURE_API_KEY", "mock-azure-key"),
                "api_base": "https://my-endpoint.openai.azure.com",
            },
            "model_info": {
                "id": "azure-gpt4"
            }
        },
    ]
    
    router = Router(
        model_list=model_list,
        routing_strategy="lowest-latency",  # or "least-busy", "lowest-cost"
        fallbacks=[
            {
                "gpt-4": ["openai-gpt4-secondary", "azure-gpt4"]
            }
        ],
        num_retries=2,
        timeout=30,
        debug_level="INFO",
    )
    
    return router


if __name__ == "__main__":
    print("\n" + "🔀" * 40)
    print("LiteLLM Router → HoneyHive Integration POC")
    print("🔀" * 40 + "\n")
    
    # Set up HoneyHive logging
    logger = HoneyHiveLogger(
        api_key="mock-api-key",
        project="litellm-router-poc",
        environment="development",
        debug=True,
    )
    litellm.callbacks = [logger]
    
    # Create router
    print("📋 Setting up Router with 3 deployments...")
    router = setup_router()
    
    # Test 1: Normal routing
    print("\n📝 Test 1: Router Call (will show routing decision)")
    print("-" * 80)
    
    try:
        response = router.completion(
            model="gpt-4",
            messages=[
                {"role": "user", "content": "Explain routing in one sentence."}
            ],
            metadata={
                "test_id": "router-test-1",
                "user_id": "user-456"
            }
        )
        print(f"✅ Response: {response.choices[0].message.content}")
        print(f"📊 Model used: {response.model}")
    except Exception as e:
        print(f"❌ Error (expected without real API keys): {e}")
        print("💡 In real scenario, HoneyHive would capture:")
        print("   - Selected deployment ID")
        print("   - Routing strategy used")
        print("   - Latency of selected deployment")
        print("   - Available vs selected deployments")
    
    # Test 2: With specific deployment
    print("\n📝 Test 2: Specific Deployment Selection")
    print("-" * 80)
    
    try:
        response = router.completion(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello"}],
            specific_deployment="azure-gpt4",  # Force Azure
            metadata={"test_id": "router-test-2"}
        )
        print(f"✅ Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ Error (expected without real API keys): {e}")
        print("💡 In real scenario, HoneyHive would capture:")
        print("   - Forced deployment: azure-gpt4")
        print("   - Routing strategy: overridden")
    
    print("\n" + "✨" * 40)
    print("Router POC Complete!")
    print("Note: Real implementation would show deployment selection,")
    print("      fallback chains, and load balancing decisions.")
    print("✨" * 40 + "\n")

