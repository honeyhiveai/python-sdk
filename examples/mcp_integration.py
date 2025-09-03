#!/usr/bin/env python3
"""Example: MCP (Model Context Protocol) integration with HoneyHive.

This example demonstrates:
1. MCP instrumentor integration with HoneyHive SDK
2. Type-safe EventType usage (no string literals)
3. Client-server trace propagation
4. Multi-instrumentor usage patterns
5. Error handling and environment setup
6. Real-world MCP usage patterns

Prerequisites:
- Install MCP support: pip install honeyhive[mcp]
- Set environment variables: HH_API_KEY, HH_PROJECT
- Optional: Set up actual MCP server for real testing

Usage:
    python examples/mcp_integration.py
"""

import asyncio
import os
import sys
from typing import Any, Dict, Optional

# Add src to path for development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from honeyhive import HoneyHiveTracer, trace
from honeyhive.models import EventType


def check_environment_setup() -> Dict[str, str]:
    """Check and display environment configuration.
    
    Returns:
        Dict containing environment configuration
    """
    config = {
        "api_key": os.getenv("HH_API_KEY", "demo-api-key"),
        "project": os.getenv("HH_PROJECT", "mcp-integration-demo"),
        "source": os.getenv("HH_SOURCE", "example-script"),
        "session_name": os.getenv("HH_SESSION_NAME", "mcp-demo-session")
    }
    
    print("🔧 Environment Configuration:")
    for key, value in config.items():
        display_value = value if key != "api_key" else f"{value[:8]}..." if len(value) > 8 else "[short-key]"
        print(f"  {key}: {display_value}")
    
    return config


def get_mcp_instrumentor():
    """Get MCP instrumentor with proper error handling.
    
    Returns:
        MCPInstrumentor instance or None if not available
    """
    try:
        from openinference.instrumentation.mcp import MCPInstrumentor
        print("✅ MCP instrumentor available")
        return MCPInstrumentor()
    except ImportError as e:
        print(f"⚠️  MCP instrumentor not available: {e}")
        print("   Install with: pip install honeyhive[mcp]")
        return None


def setup_multi_instrumentor_tracer(config: Dict[str, str]) -> Optional[HoneyHiveTracer]:
    """Set up HoneyHive tracer with MCP and other instrumentors.
    
    Args:
        config: Environment configuration
        
    Returns:
        Configured HoneyHiveTracer or None if setup fails
    """
    instrumentors = []
    
    # Add MCP instrumentor
    mcp_instrumentor = get_mcp_instrumentor()
    if mcp_instrumentor:
        instrumentors.append(mcp_instrumentor)
        print("🔗 Added MCP instrumentor")
    
    # Optionally add other instrumentors (with graceful handling)
    other_instrumentors = [
        ("openinference.instrumentation.openai", "OpenAIInstrumentor", "OpenAI"),
        ("openinference.instrumentation.anthropic", "AnthropicInstrumentor", "Anthropic"),
    ]
    
    for module_name, class_name, display_name in other_instrumentors:
        try:
            module = __import__(module_name, fromlist=[class_name])
            instrumentor_class = getattr(module, class_name)
            instrumentors.append(instrumentor_class())
            print(f"🔗 Added {display_name} instrumentor")
        except ImportError:
            print(f"ℹ️  {display_name} instrumentor not available (optional)")
    
    if not instrumentors:
        print("⚠️  No instrumentors available - continuing without instrumentation")
    
    try:
        # Initialize HoneyHive tracer with instrumentors
        tracer = HoneyHiveTracer.init(
            api_key=config["api_key"],
            project=config["project"],
            source=config["source"],
            session_name=config["session_name"],
            instrumentors=instrumentors,
            test_mode=config["api_key"] == "demo-api-key"  # Use test mode for demo
        )
        
        print(f"✅ HoneyHive tracer initialized with {len(instrumentors)} instrumentors")
        return tracer
        
    except Exception as e:
        print(f"❌ Failed to initialize tracer: {e}")
        return None


# Example MCP-style functions with proper tracing
@trace(event_type=EventType.tool)
def analyze_financial_data(ticker: str, period: str = "1y") -> Dict[str, Any]:
    """Analyze financial data for a given ticker.
    
    This function simulates an MCP tool that would be called by an agent
    to analyze financial data. In a real scenario, this would be traced
    automatically by the MCP instrumentor.
    
    Args:
        ticker: Stock ticker symbol
        period: Analysis period
        
    Returns:
        Analysis results dictionary
    """
    print(f"📊 Analyzing financial data for {ticker} (period: {period})")
    
    # Simulate financial analysis
    analysis_result = {
        "ticker": ticker,
        "period": period,
        "analysis": {
            "trend": "bullish",
            "risk_level": "moderate",
            "recommendation": "buy",
            "confidence": 0.85
        },
        "metrics": {
            "pe_ratio": 15.2,
            "market_cap": "2.5T",
            "dividend_yield": 0.5
        }
    }
    
    print(f"✅ Analysis complete for {ticker}")
    return analysis_result


@trace(event_type=EventType.tool)
def fetch_market_news(ticker: str, limit: int = 5) -> Dict[str, Any]:
    """Fetch market news for a given ticker.
    
    Another example MCP tool function that would be traced automatically.
    
    Args:
        ticker: Stock ticker symbol
        limit: Number of news articles to fetch
        
    Returns:
        News articles dictionary
    """
    print(f"📰 Fetching market news for {ticker} (limit: {limit})")
    
    # Simulate news fetching
    news_result = {
        "ticker": ticker,
        "articles": [
            {
                "title": f"{ticker} Reports Strong Q4 Earnings",
                "summary": "Company exceeds expectations with strong revenue growth",
                "sentiment": "positive",
                "relevance": 0.9
            },
            {
                "title": f"Market Analysis: {ticker} Outlook",
                "summary": "Analysts remain optimistic about future prospects",
                "sentiment": "positive", 
                "relevance": 0.8
            }
        ],
        "overall_sentiment": "positive"
    }
    
    print(f"✅ Fetched {len(news_result['articles'])} news articles for {ticker}")
    return news_result


@trace(event_type=EventType.chain)
def comprehensive_stock_analysis(ticker: str) -> Dict[str, Any]:
    """Perform comprehensive stock analysis using multiple tools.
    
    This function demonstrates a chain of operations that would typically
    be orchestrated by an MCP client calling multiple MCP tools.
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Comprehensive analysis results
    """
    print(f"🔍 Starting comprehensive analysis for {ticker}")
    
    try:
        # Step 1: Analyze financial data
        financial_data = analyze_financial_data(ticker, "1y")
        
        # Step 2: Fetch market news
        news_data = fetch_market_news(ticker, 3)
        
        # Step 3: Combine results
        comprehensive_result = {
            "ticker": ticker,
            "timestamp": "2025-09-03T10:00:00Z",
            "financial_analysis": financial_data["analysis"],
            "key_metrics": financial_data["metrics"],
            "market_sentiment": news_data["overall_sentiment"],
            "news_summary": len(news_data["articles"]),
            "overall_score": 8.5,
            "recommendation": "Strong Buy"
        }
        
        print(f"✅ Comprehensive analysis complete for {ticker}")
        return comprehensive_result
        
    except Exception as e:
        print(f"❌ Analysis failed for {ticker}: {e}")
        raise


@trace(event_type=EventType.session)
async def simulate_mcp_agent_session() -> Dict[str, Any]:
    """Simulate an MCP agent session with multiple operations.
    
    This async function simulates how an MCP agent would interact with
    multiple tools in a session, with proper trace context propagation.
    
    Returns:
        Session results dictionary
    """
    print("🤖 Starting MCP agent simulation session")
    
    session_results = {
        "session_id": "mcp-demo-session-001",
        "operations": [],
        "total_tools_used": 0,
        "success_rate": 0.0
    }
    
    # Simulate multiple stock analyses
    tickers = ["AAPL", "GOOGL", "MSFT"]
    successful_operations = 0
    
    for ticker in tickers:
        try:
            print(f"\n📈 Processing {ticker}...")
            
            # Simulate async delay (real MCP operations might have network delays)
            await asyncio.sleep(0.1)
            
            # Perform comprehensive analysis
            result = comprehensive_stock_analysis(ticker)
            
            session_results["operations"].append({
                "ticker": ticker,
                "status": "success",
                "recommendation": result["recommendation"],
                "score": result["overall_score"]
            })
            
            successful_operations += 1
            session_results["total_tools_used"] += 2  # financial + news tools
            
        except Exception as e:
            print(f"❌ Failed to process {ticker}: {e}")
            session_results["operations"].append({
                "ticker": ticker,
                "status": "failed",
                "error": str(e)
            })
    
    session_results["success_rate"] = successful_operations / len(tickers)
    
    print(f"\n✅ Session complete: {successful_operations}/{len(tickers)} successful")
    return session_results


def demonstrate_error_handling():
    """Demonstrate error handling in MCP integration."""
    print("\n🔧 Demonstrating error handling scenarios")
    
    @trace(event_type=EventType.tool)
    def failing_tool(should_fail: bool = True) -> str:
        """Tool that can be configured to fail."""
        if should_fail:
            raise ValueError("Simulated tool failure")
        return "success"
    
    # Test graceful error handling
    try:
        result = failing_tool(should_fail=True)
        print(f"Unexpected success: {result}")
    except ValueError as e:
        print(f"✅ Error handled gracefully: {e}")
    
    # Test successful operation
    try:
        result = failing_tool(should_fail=False)
        print(f"✅ Tool succeeded: {result}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


async def main() -> int:
    """Main example function.
    
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print("🚀 HoneyHive MCP Integration Example")
    print("=" * 50)
    
    try:
        # Check environment setup
        config = check_environment_setup()
        
        # Set up tracer with MCP instrumentor
        tracer = setup_multi_instrumentor_tracer(config)
        if not tracer:
            print("❌ Failed to set up tracer")
            return 1
        
        print("\n" + "=" * 50)
        print("📊 Running MCP Integration Examples")
        print("=" * 50)
        
        # Example 1: Simple tool usage
        print("\n1️⃣ Simple MCP Tool Usage:")
        financial_result = analyze_financial_data("AAPL", "6m")
        print(f"   Result: {financial_result['analysis']['recommendation']}")
        
        # Example 2: Chain of operations
        print("\n2️⃣ Chain of MCP Operations:")
        comprehensive_result = comprehensive_stock_analysis("GOOGL")
        print(f"   Overall recommendation: {comprehensive_result['recommendation']}")
        
        # Example 3: Async session simulation
        print("\n3️⃣ Async MCP Agent Session:")
        session_result = await simulate_mcp_agent_session()
        print(f"   Session success rate: {session_result['success_rate']:.1%}")
        
        # Example 4: Error handling
        print("\n4️⃣ Error Handling:")
        demonstrate_error_handling()
        
        # Force flush traces before exit
        if hasattr(tracer, 'force_flush'):
            print("\n📤 Flushing traces...")
            tracer.force_flush()
        
        print("\n" + "=" * 50)
        print("✅ MCP Integration Example Complete!")
        print("=" * 50)
        
        if config["api_key"] == "demo-api-key":
            print("\n💡 To see traces in HoneyHive dashboard:")
            print("   1. Set HH_API_KEY environment variable")
            print("   2. Set HH_PROJECT to your project name")
            print("   3. Re-run this example")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Example failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    """Entry point for the example script."""
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Example interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
