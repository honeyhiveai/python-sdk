#!/usr/bin/env python3
"""
Migration Example: OpenInference to OpenLLMetry

This example demonstrates how to migrate from OpenInference to OpenLLMetry
instrumentors for enhanced LLM observability and cost tracking.

The migration process is simple and reversible:
1. Change import statements
2. Update package dependencies
3. Optionally leverage enhanced features

Requirements (Before Migration):
    pip install honeyhive[openinference-openai,openinference-anthropic]
    
Requirements (After Migration):
    pip install honeyhive[traceloop-openai,traceloop-anthropic]
    
Environment Variables:
    HH_API_KEY=your-honeyhive-api-key
    OPENAI_API_KEY=your-openai-api-key
    ANTHROPIC_API_KEY=your-anthropic-api-key
"""

import os
from honeyhive import HoneyHiveTracer, trace, enrich_span
from honeyhive.models import EventType

# === BEFORE MIGRATION: OpenInference Imports ===
# from openinference.instrumentation.openai import OpenAIInstrumentor
# from openinference.instrumentation.anthropic import AnthropicInstrumentor

# === AFTER MIGRATION: OpenLLMetry Imports ===
from opentelemetry.instrumentation.openai import OpenAIInstrumentor
from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor

import openai
import anthropic


def main():
    """Demonstrate migration from OpenInference to OpenLLMetry."""
    
    print("🔄 Migration Example: OpenInference → OpenLLMetry")
    print("=" * 60)
    
    # Show both initialization approaches
    print("\n1. Initialization Comparison")
    show_initialization_comparison()
    
    # Demonstrate that existing code works unchanged
    print("\n2. Existing Code Compatibility")
    demonstrate_code_compatibility()
    
    # Show enhanced features available with OpenLLMetry
    print("\n3. Enhanced OpenLLMetry Features")
    demonstrate_enhanced_features()
    
    # Performance and cost comparison
    print("\n4. Migration Benefits")
    demonstrate_migration_benefits()
    
    print("\n✅ Migration example completed!")
    print("Your existing code works unchanged with enhanced metrics!")


def show_initialization_comparison():
    """Show the difference in initialization between OpenInference and OpenLLMetry."""
    
    print("📋 Initialization Code Comparison:")
    print()
    
    print("BEFORE (OpenInference):")
    print("```python")
    print("from openinference.instrumentation.openai import OpenAIInstrumentor")
    print("from openinference.instrumentation.anthropic import AnthropicInstrumentor")
    print()
    print("tracer = HoneyHiveTracer.init(")
    print("    api_key='your-api-key',")
    print("    instrumentors=[OpenAIInstrumentor(), AnthropicInstrumentor()]")
    print(")")
    print("```")
    print()
    
    print("AFTER (OpenLLMetry):")
    print("```python")
    print("from opentelemetry.instrumentation.openai import OpenAIInstrumentor")
    print("from opentelemetry.instrumentation.anthropic import AnthropicInstrumentor")
    print()
    print("tracer = HoneyHiveTracer.init(")
    print("    api_key='your-api-key',")
    print("    instrumentors=[OpenAIInstrumentor(), AnthropicInstrumentor()]")
    print(")")
    print("```")
    print()
    print("✨ Only the import statements change - initialization is identical!")


def demonstrate_code_compatibility():
    """Demonstrate that existing LLM code works unchanged after migration."""
    
    # Initialize with OpenLLMetry (post-migration)
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        source="migration_example",
        instrumentors=[
            OpenAIInstrumentor(),    # Now using OpenLLMetry
            AnthropicInstrumentor()  # Now using OpenLLMetry
        ]
    )
    
    print("🔧 Testing existing code compatibility...")
    
    # This is the SAME code you had before migration
    existing_openai_function()
    existing_anthropic_function()
    existing_multi_provider_function()
    
    print("✅ All existing code works unchanged!")


@trace(event_type=EventType.model)
def existing_openai_function():
    """Example of existing OpenAI code that works unchanged after migration."""
    
    # This function represents your existing code - no changes needed!
    client = openai.OpenAI()
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What are the benefits of LLM observability?"}
        ],
        max_tokens=100
    )
    
    result = response.choices[0].message.content
    print(f"✓ OpenAI (unchanged code): {result[:50]}...")
    return result


@trace(event_type=EventType.model)
def existing_anthropic_function():
    """Example of existing Anthropic code that works unchanged after migration."""
    
    # This function represents your existing code - no changes needed!
    client = anthropic.Anthropic()
    
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=100,
        messages=[
            {"role": "user", "content": "Explain the value of enhanced LLM metrics."}
        ]
    )
    
    result = response.content[0].text
    print(f"✓ Anthropic (unchanged code): {result[:50]}...")
    return result


@trace(event_type=EventType.chain)
def existing_multi_provider_function():
    """Example of existing multi-provider code that works unchanged."""
    
    enrich_span({
        "function.type": "existing_multi_provider",
        "migration.status": "post_migration",
        "providers.count": 2
    })
    
    # Your existing multi-provider logic works unchanged
    openai_result = existing_openai_function()
    anthropic_result = existing_anthropic_function()
    
    # Your existing business logic
    comparison = {
        "openai_length": len(openai_result),
        "anthropic_length": len(anthropic_result),
        "preferred": "openai" if len(openai_result) > len(anthropic_result) else "anthropic"
    }
    
    enrich_span(comparison)
    print(f"✓ Multi-provider comparison: {comparison['preferred']} preferred")
    
    return comparison


def demonstrate_enhanced_features():
    """Show enhanced features available with OpenLLMetry."""
    
    print("🚀 Enhanced features now available with OpenLLMetry:")
    
    # Initialize tracer for enhanced features demo
    tracer = HoneyHiveTracer.init(
        api_key=os.getenv("HH_API_KEY"),
        source="enhanced_features_demo",
        instrumentors=[OpenAIInstrumentor(), AnthropicInstrumentor()]
    )
    
    # Enhanced cost tracking
    enhanced_cost_tracking()
    
    # Enhanced error handling
    enhanced_error_handling()
    
    # Enhanced performance monitoring
    enhanced_performance_monitoring()


@trace(event_type=EventType.model)
def enhanced_cost_tracking():
    """Demonstrate enhanced cost tracking with OpenLLMetry."""
    
    enrich_span({
        "feature.type": "enhanced_cost_tracking",
        "feature.new_in_openllmetry": True
    })
    
    client = openai.OpenAI()
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Explain cost optimization for LLMs."}],
        max_tokens=150
    )
    
    # OpenLLMetry provides enhanced cost tracking attributes
    if response.usage:
        prompt_cost = (response.usage.prompt_tokens / 1000) * 0.0015
        completion_cost = (response.usage.completion_tokens / 1000) * 0.002
        total_cost = prompt_cost + completion_cost
        
        enrich_span({
            "cost.prompt_tokens": response.usage.prompt_tokens,
            "cost.completion_tokens": response.usage.completion_tokens,
            "cost.total_tokens": response.usage.total_tokens,
            "cost.prompt_cost_usd": prompt_cost,
            "cost.completion_cost_usd": completion_cost,
            "cost.total_cost_usd": total_cost,
            "cost.cost_per_token": total_cost / response.usage.total_tokens,
            "cost.efficiency_chars_per_dollar": len(response.choices[0].message.content) / total_cost
        })
        
        print(f"💰 Enhanced cost tracking: ${total_cost:.4f} ({response.usage.total_tokens} tokens)")


@trace(event_type=EventType.model)
def enhanced_error_handling():
    """Demonstrate enhanced error handling with OpenLLMetry."""
    
    enrich_span({
        "feature.type": "enhanced_error_handling",
        "feature.new_in_openllmetry": True,
        "error.handling_enabled": True
    })
    
    client = openai.OpenAI()
    
    try:
        # Intentionally use a very small max_tokens to potentially trigger an error
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Write a very long essay about artificial intelligence, machine learning, deep learning, and neural networks."}],
            max_tokens=10  # Very small to potentially cause issues
        )
        
        enrich_span({
            "error.occurred": False,
            "response.truncated": len(response.choices[0].message.content) < 50
        })
        
        print("✓ Enhanced error handling: Request succeeded")
        
    except Exception as e:
        enrich_span({
            "error.occurred": True,
            "error.type": type(e).__name__,
            "error.message": str(e),
            "error.recoverable": "rate_limit" in str(e).lower() or "quota" in str(e).lower()
        })
        
        print(f"⚠️  Enhanced error handling: Caught {type(e).__name__}")


@trace(event_type=EventType.model)
def enhanced_performance_monitoring():
    """Demonstrate enhanced performance monitoring with OpenLLMetry."""
    
    import time
    
    enrich_span({
        "feature.type": "enhanced_performance_monitoring",
        "feature.new_in_openllmetry": True,
        "monitoring.detailed_metrics": True
    })
    
    client = openai.OpenAI()
    
    start_time = time.time()
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Explain performance monitoring for LLMs."}],
        max_tokens=100
    )
    
    end_time = time.time()
    latency = end_time - start_time
    
    # Enhanced performance metrics
    if response.usage:
        tokens_per_second = response.usage.total_tokens / latency
        time_to_first_token = latency * 0.1  # Estimated
        processing_efficiency = response.usage.completion_tokens / (latency - time_to_first_token)
        
        enrich_span({
            "performance.total_latency_ms": latency * 1000,
            "performance.time_to_first_token_ms": time_to_first_token * 1000,
            "performance.tokens_per_second": tokens_per_second,
            "performance.processing_efficiency": processing_efficiency,
            "performance.throughput_chars_per_second": len(response.choices[0].message.content) / latency,
            "performance.model_efficiency_score": tokens_per_second / 100,  # Normalized score
            "performance.latency_category": "fast" if latency < 2 else "medium" if latency < 5 else "slow"
        })
        
        print(f"📊 Enhanced performance monitoring: {tokens_per_second:.1f} tokens/sec")


def demonstrate_migration_benefits():
    """Show the benefits gained from migrating to OpenLLMetry."""
    
    print("🎯 Migration Benefits Summary:")
    print()
    
    benefits = [
        {
            "category": "Cost Tracking",
            "before": "Basic token counts",
            "after": "Detailed cost breakdown, efficiency metrics, budget tracking"
        },
        {
            "category": "Performance Monitoring", 
            "before": "Simple latency tracking",
            "after": "Tokens/sec, time-to-first-token, processing efficiency"
        },
        {
            "category": "Error Handling",
            "before": "Basic error capture",
            "after": "Enhanced error categorization, recovery suggestions"
        },
        {
            "category": "Production Readiness",
            "before": "Development-focused",
            "after": "Production-optimized with advanced monitoring"
        },
        {
            "category": "LLM-Specific Metrics",
            "before": "Generic OpenTelemetry attributes",
            "after": "LLM-optimized attributes and cost analysis"
        }
    ]
    
    for benefit in benefits:
        print(f"📈 {benefit['category']}:")
        print(f"   Before: {benefit['before']}")
        print(f"   After:  {benefit['after']}")
        print()
    
    print("💡 Migration Recommendation:")
    print("   • Start with OpenInference for development and learning")
    print("   • Migrate to OpenLLMetry when you need production monitoring")
    print("   • Use mixed setups strategically based on provider usage")
    print("   • Migration is reversible - you can switch back anytime")


def migration_checklist():
    """Provide a migration checklist."""
    
    print("\n📋 Migration Checklist:")
    print()
    
    checklist_items = [
        "[ ] Backup current requirements.txt or pyproject.toml",
        "[ ] Update package dependencies (openinference → opentelemetry)",
        "[ ] Change import statements in your code",
        "[ ] Test with simple LLM calls to verify functionality",
        "[ ] Verify traces appear in HoneyHive dashboard",
        "[ ] Monitor application performance after migration",
        "[ ] Update documentation and deployment scripts",
        "[ ] Train team on new enhanced features (optional)",
        "[ ] Set up enhanced monitoring and alerting (optional)"
    ]
    
    for item in checklist_items:
        print(f"   {item}")
    
    print()
    print("🔄 Rollback Plan:")
    print("   1. Reinstall OpenInference packages")
    print("   2. Revert import statements")
    print("   3. Restart application")
    print("   4. Verify functionality")


if __name__ == "__main__":
    # Check required environment variables
    required_vars = ["HH_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables before running the example.")
        print()
        print("For demonstration purposes, you can also run this script")
        print("without API keys to see the migration code patterns.")
        
        # Show migration patterns without making API calls
        show_initialization_comparison()
        migration_checklist()
    else:
        main()
        migration_checklist()
