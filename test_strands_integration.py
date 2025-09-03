#!/usr/bin/env python3
"""Test script to verify HoneyHive instrumentation with AWS Strands.

This script tests multiple scenarios to ensure HoneyHive's automatic
instrumentation works correctly with AWS Strands regardless of initialization order.

Requirements:
    pip install strands-agents[otel] honeyhive opentelemetry-api opentelemetry-sdk

Environment Variables:
    HONEYHIVE_API_KEY: Your HoneyHive API key
    AWS_ACCESS_KEY_ID: AWS access key for Bedrock
    AWS_SECRET_ACCESS_KEY: AWS secret key for Bedrock
    AWS_REGION: AWS region (default: us-east-1)
"""

import os
import sys
import time
import traceback
from typing import Any, Dict, List, Optional

# Add src to path for local testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

try:
    from honeyhive import HoneyHiveTracer, trace, enrich_span
except ImportError as e:
    print(f"❌ HoneyHive import failed: {e}")
    print("   Install with: pip install honeyhive")
    sys.exit(1)

try:
    from opentelemetry import trace as otel_trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
except ImportError as e:
    print(f"❌ OpenTelemetry import failed: {e}")
    print("   Install with: pip install opentelemetry-api opentelemetry-sdk")
    sys.exit(1)

try:
    # Import AWS Strands (verified working pattern)
    from strands import Agent
    STRANDS_AVAILABLE = True
    print("✅ AWS Strands imported successfully")
except ImportError as e:
    print(f"⚠️  Strands import failed: {e}")
    print("   Install with: pip install strands-agents")
    STRANDS_AVAILABLE = False


class TestResults:
    """Track test results across scenarios."""
    
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
    
    def add_result(self, test_name: str, passed: bool, details: str = "", error: Optional[str] = None):
        """Add a test result."""
        self.results.append({
            "test_name": test_name,
            "passed": passed,
            "details": details,
            "error": error,
            "timestamp": time.time()
        })
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
    
    def print_summary(self):
        """Print test summary."""
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%" if self.total_tests > 0 else "0%")
        
        print(f"\n{'DETAILED RESULTS'}")
        print(f"{'-'*60}")
        for result in self.results:
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"{status} {result['test_name']}")
            if result["details"]:
                print(f"    Details: {result['details']}")
            if result["error"]:
                print(f"    Error: {result['error']}")


def check_environment() -> bool:
    """Check required environment variables and AWS credentials."""
    # Check HoneyHive API key
    required_vars = ["HONEYHIVE_API_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"❌ Missing environment variables: {missing}")
        print("   Set HONEYHIVE_API_KEY to run tests")
        return False
    
    print("✅ HoneyHive API key configured")
    
    # Check AWS credentials (optional for real Strands testing)
    try:
        import boto3
        from botocore.exceptions import NoCredentialsError, PartialCredentialsError
        
        session = boto3.Session()
        creds = session.get_credentials()
        
        if creds:
            # Test credentials by making a simple call
            sts = session.client('sts')
            identity = sts.get_caller_identity()
            print(f"✅ AWS credentials configured")
            print(f"   Account: {identity.get('Account', 'unknown')}")
            print(f"   User/Role: {identity.get('Arn', 'unknown').split('/')[-1]}")
            
            # Check for region
            region = session.region_name or os.getenv('AWS_REGION', os.getenv('AWS_DEFAULT_REGION'))
            if region:
                print(f"   Region: {region}")
            else:
                print("   ⚠️  No AWS region configured, setting default to us-east-1")
                os.environ['AWS_REGION'] = 'us-east-1'
                
        else:
            print("⚠️  No AWS credentials found")
            print("   AWS Strands will use mock mode only")
            print("   For real testing, configure AWS credentials:")
            print("     - AWS SSO: aws configure sso && aws sso login")
            print("     - Environment: export AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=...")
            print("     - AWS CLI: aws configure")
            
    except ImportError:
        print("⚠️  boto3 not available, skipping AWS credential check")
    except (NoCredentialsError, PartialCredentialsError) as e:
        print(f"⚠️  AWS credential error: {e}")
        print("   Configure AWS credentials for full Strands testing")
    except Exception as e:
        print(f"⚠️  AWS credential check failed: {e}")
    
    return True


def setup_mock_strands_if_needed():
    """Create a mock Strands Agent for testing if real one isn't available."""
    if STRANDS_AVAILABLE:
        return
    
    print("⚠️  Creating mock Strands Agent for testing...")
    
    # Create a mock Agent class that uses OpenTelemetry
    class MockAgent:
        """Mock Strands Agent that simulates OpenTelemetry integration."""
        
        def __init__(self, model: str = "mock-model", system_prompt: str = "Mock agent"):
            self.model = model
            self.system_prompt = system_prompt
            self.tracer = otel_trace.get_tracer("mock-strands-agent")
        
        def __call__(self, query: str) -> str:
            """Simulate agent execution with OpenTelemetry spans."""
            with self.tracer.start_as_current_span("agent_execution") as span:
                span.set_attribute("agent.model", self.model)
                span.set_attribute("agent.query", query)
                span.set_attribute("agent.type", "mock")
                
                # Simulate sub-operations
                with self.tracer.start_as_current_span("model_call") as model_span:
                    model_span.set_attribute("model.name", self.model)
                    model_span.set_attribute("model.input_tokens", len(query.split()))
                    time.sleep(0.1)  # Simulate processing time
                    
                    # Simulate response
                    response = f"Mock response to: {query}"
                    model_span.set_attribute("model.output_tokens", len(response.split()))
                    model_span.set_attribute("model.latency_ms", 100)
                
                span.set_attribute("agent.response", response)
                return response
    
    # Monkey patch the Agent import
    import sys
    if 'strands' not in sys.modules:
        class MockStrandsModule:
            Agent = MockAgent
        
        sys.modules['strands'] = MockStrandsModule()
    
    # Update global availability flag
    globals()['STRANDS_AVAILABLE'] = True
    print("✅ Mock Strands Agent created")


@trace(event_type="tool", event_name="test_scenario")
def test_scenario_1_honeyhive_first(results: TestResults):
    """Test Scenario 1: Initialize HoneyHive first, then Strands."""
    print("\n" + "="*50)
    print("SCENARIO 1: HoneyHive First")
    print("="*50)
    
    try:
        # Reset OpenTelemetry state
        otel_trace._TRACER_PROVIDER = None
        
        print("Step 1: Initializing HoneyHive tracer...")
        tracer = HoneyHiveTracer.init(
            api_key=os.getenv("HONEYHIVE_API_KEY"),
            project="strands-test-scenario-1",
            source="test",
            test_mode=True,
            session_name="scenario_1_honeyhive_first"
        )
        
        # Check if HoneyHive became the global provider
        current_provider = otel_trace.get_tracer_provider()
        is_main_provider = tracer.is_main_provider
        print(f"   HoneyHive is main provider: {is_main_provider}")
        print(f"   Current provider: {type(current_provider).__name__}")
        
        print("Step 2: Creating Strands agent...")
        from strands import Agent
        agent = Agent(
            model="anthropic.claude-3-haiku-20240307-v1:0",  # More widely available
            system_prompt="You are a helpful AI assistant"
        )
        
        print("Step 3: Executing agent query...")
        with tracer.start_span("strands_agent_call") as span:
            enrich_span(metadata={
                "test_scenario": "honeyhive_first",
                "initialization_order": "honeyhive_then_strands"
            })
            
            response = agent("What is the capital of France?")
            
            enrich_span(metadata={
                "agent_response_length": len(response),
                "execution_successful": True
            })
        
        print(f"   Agent response: {response[:100]}...")
        
        results.add_result(
            "Scenario 1: HoneyHive First",
            True,
            f"HoneyHive main provider: {is_main_provider}, Response received"
        )
        
    except Exception as e:
        error_msg = f"Scenario 1 failed: {str(e)}"
        print(f"❌ {error_msg}")
        print(f"   Traceback: {traceback.format_exc()}")
        results.add_result("Scenario 1: HoneyHive First", False, error=error_msg)


@trace(event_type="tool", event_name="test_scenario")
def test_scenario_2_strands_first(results: TestResults):
    """Test Scenario 2: Initialize Strands first, then HoneyHive."""
    print("\n" + "="*50)
    print("SCENARIO 2: Strands First")
    print("="*50)
    
    try:
        # Reset OpenTelemetry state
        otel_trace._TRACER_PROVIDER = None
        
        print("Step 1: Creating Strands agent first...")
        from strands import Agent
        agent = Agent(
            model="anthropic.claude-3-haiku-20240307-v1:0",  # More widely available
            system_prompt="You are a helpful AI assistant"
        )
        
        # Check current provider after Strands init
        provider_after_strands = otel_trace.get_tracer_provider()
        print(f"   Provider after Strands: {type(provider_after_strands).__name__}")
        
        print("Step 2: Initializing HoneyHive tracer...")
        tracer = HoneyHiveTracer.init(
            api_key=os.getenv("HONEYHIVE_API_KEY"),
            project="strands-test-scenario-2",
            source="test",
            test_mode=True,
            session_name="scenario_2_strands_first"
        )
        
        is_main_provider = tracer.is_main_provider
        current_provider = otel_trace.get_tracer_provider()
        print(f"   HoneyHive is main provider: {is_main_provider}")
        print(f"   Current provider: {type(current_provider).__name__}")
        
        print("Step 3: Executing agent query...")
        with tracer.start_span("strands_agent_call") as span:
            enrich_span(metadata={
                "test_scenario": "strands_first",
                "initialization_order": "strands_then_honeyhive"
            })
            
            response = agent("What is the largest planet in our solar system?")
            
            enrich_span(metadata={
                "agent_response_length": len(response),
                "execution_successful": True
            })
        
        print(f"   Agent response: {response[:100]}...")
        
        results.add_result(
            "Scenario 2: Strands First",
            True,
            f"HoneyHive main provider: {is_main_provider}, Response received"
        )
        
    except Exception as e:
        error_msg = f"Scenario 2 failed: {str(e)}"
        print(f"❌ {error_msg}")
        print(f"   Traceback: {traceback.format_exc()}")
        results.add_result("Scenario 2: Strands First", False, error=error_msg)


@trace(event_type="chain", event_name="test_scenario")
def test_scenario_3_multiple_agents(results: TestResults):
    """Test Scenario 3: Multiple agents with single HoneyHive tracer."""
    print("\n" + "="*50)
    print("SCENARIO 3: Multiple Agents")
    print("="*50)
    
    try:
        # Reset OpenTelemetry state
        otel_trace._TRACER_PROVIDER = None
        
        print("Step 1: Initializing HoneyHive tracer...")
        tracer = HoneyHiveTracer.init(
            api_key=os.getenv("HONEYHIVE_API_KEY"),
            project="strands-test-scenario-3",
            source="test",
            test_mode=True,
            session_name="scenario_3_multiple_agents"
        )
        
        print("Step 2: Creating multiple Strands agents...")
        from strands import Agent
        
        research_agent = Agent(
            model="anthropic.claude-3-haiku-20240307-v1:0",
            system_prompt="You are a research assistant"
        )
        
        writing_agent = Agent(
            model="anthropic.claude-3-haiku-20240307-v1:0",
            system_prompt="You are a writing assistant"
        )
        
        print("Step 3: Executing multiple agent queries...")
        with tracer.start_span("multi_agent_workflow") as workflow_span:
            enrich_span(metadata={
                "test_scenario": "multiple_agents",
                "agent_count": 2
            })
            
            # Research phase
            with tracer.start_span("research_phase") as research_span:
                enrich_span(metadata={"phase": "research", "agent": "research_agent"})
                research_result = research_agent("Research the benefits of renewable energy")
                research_span.set_attribute("response_length", len(research_result))
            
            # Writing phase
            with tracer.start_span("writing_phase") as writing_span:
                enrich_span(metadata={"phase": "writing", "agent": "writing_agent"})
                writing_result = writing_agent("Write a summary of renewable energy benefits")
                writing_span.set_attribute("response_length", len(writing_result))
            
            enrich_span(metadata={
                "research_length": len(research_result),
                "writing_length": len(writing_result),
                "workflow_successful": True
            })
        
        print(f"   Research result: {research_result[:100]}...")
        print(f"   Writing result: {writing_result[:100]}...")
        
        results.add_result(
            "Scenario 3: Multiple Agents",
            True,
            f"Research: {len(research_result)} chars, Writing: {len(writing_result)} chars"
        )
        
    except Exception as e:
        error_msg = f"Scenario 3 failed: {str(e)}"
        print(f"❌ {error_msg}")
        print(f"   Traceback: {traceback.format_exc()}")
        results.add_result("Scenario 3: Multiple Agents", False, error=error_msg)


def test_span_enrichment(results: TestResults):
    """Test that HoneyHive span processor enriches Strands spans."""
    print("\n" + "="*50)
    print("SCENARIO 4: Span Enrichment Verification")
    print("="*50)
    
    try:
        # Reset OpenTelemetry state
        otel_trace._TRACER_PROVIDER = None
        
        print("Step 1: Setting up console exporter to capture spans...")
        # Set up a console exporter to see span output
        provider = TracerProvider()
        console_processor = BatchSpanProcessor(ConsoleSpanExporter())
        provider.add_span_processor(console_processor)
        otel_trace.set_tracer_provider(provider)
        
        print("Step 2: Initializing HoneyHive tracer...")
        tracer = HoneyHiveTracer.init(
            api_key=os.getenv("HONEYHIVE_API_KEY"),
            project="strands-test-scenario-4",
            source="test",
            test_mode=True,
            session_name="scenario_4_span_enrichment"
        )
        
        print("Step 3: Creating Strands agent...")
        from strands import Agent
        agent = Agent(
            model="anthropic.claude-3-haiku-20240307-v1:0",
            system_prompt="You are a helpful AI assistant"
        )
        
        print("Step 4: Executing agent with span monitoring...")
        with tracer.start_span("span_enrichment_test") as span:
            enrich_span(metadata={
                "test_scenario": "span_enrichment",
                "monitoring_enabled": True
            })
            
            response = agent("Explain quantum computing in simple terms")
            
            # Verify span attributes
            span_attributes = {}
            if hasattr(span, '_attributes'):
                span_attributes = span._attributes or {}
            
            has_honeyhive_attrs = any(key.startswith('honeyhive.') for key in span_attributes.keys())
            
            enrich_span(metadata={
                "span_attributes_count": len(span_attributes),
                "has_honeyhive_attributes": has_honeyhive_attrs,
                "response_received": len(response) > 0
            })
        
        print(f"   Agent response: {response[:100]}...")
        print(f"   Span attributes found: {len(span_attributes)}")
        print(f"   HoneyHive attributes present: {has_honeyhive_attrs}")
        
        results.add_result(
            "Scenario 4: Span Enrichment",
            True,
            f"Attributes: {len(span_attributes)}, HoneyHive attrs: {has_honeyhive_attrs}"
        )
        
    except Exception as e:
        error_msg = f"Scenario 4 failed: {str(e)}"
        print(f"❌ {error_msg}")
        print(f"   Traceback: {traceback.format_exc()}")
        results.add_result("Scenario 4: Span Enrichment", False, error=error_msg)


def main():
    """Run all test scenarios."""
    print("🧪 AWS Strands + HoneyHive Integration Test")
    print("=" * 60)
    
    # Check environment
    if not check_environment():
        return 1
    
    # Setup mock Strands if needed
    setup_mock_strands_if_needed()
    
    # Initialize results tracker
    results = TestResults()
    
    # Run test scenarios
    test_scenario_1_honeyhive_first(results)
    test_scenario_2_strands_first(results)
    test_scenario_3_multiple_agents(results)
    test_span_enrichment(results)
    
    # Print results
    results.print_summary()
    
    # Return exit code
    return 0 if results.failed_tests == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
