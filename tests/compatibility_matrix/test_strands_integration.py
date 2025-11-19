#!/usr/bin/env python3
"""
AWS Strands Compatibility Test for HoneyHive SDK

Tests AWS Strands integration with HoneyHive's OpenTelemetry provider coexistence.
This test validates that HoneyHive and Strands can work together without conflicts,
testing various initialization orders and concurrent scenarios.
"""

import os
import sys
import threading
import time
from pathlib import Path
from typing import Optional


def load_env_file() -> None:
    """Load environment variables from .env file if it exists."""
    # Look for .env file in project root
    env_file = Path(__file__).parent.parent.parent / ".env"

    if env_file.exists():
        print(f"📄 Loading environment variables from {env_file}")
        with open(env_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Parse KEY=VALUE format (handle export statements)
                if "=" in line:
                    # Remove 'export ' prefix if present
                    if line.startswith("export "):
                        line = line[7:]  # Remove 'export '

                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()

                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    # Only set if not already in environment
                    if key and not os.getenv(key):
                        os.environ[key] = value
                else:
                    print(
                        f"⚠️  Warning: Invalid line format in .env file (line {line_num}): {line}"
                    )
    else:
        print(f"ℹ️  No .env file found at {env_file}")
        print(
            "   Set environment variables manually or create .env file from env.example"
        )


def test_strands_integration():
    """Test AWS Strands integration with HoneyHive via OpenTelemetry coexistence."""

    # Check required environment variables
    api_key = os.getenv("HH_API_KEY")
    project = os.getenv("HH_PROJECT")

    if not all([api_key, project]):
        print("❌ Missing required environment variables:")
        print("   - HH_API_KEY (HoneyHive API key)")
        print("   - HH_PROJECT (HoneyHive project)")
        return False

    # Check if AWS Strands is available (optional dependency)
    try:
        import strands
        from strands import Agent

        print("✓ AWS Strands is available")
    except ImportError:
        print("⏭️  AWS Strands not available - skipping integration test")
        print("   Install with: pip install strands-agents")
        return True  # Skip, don't fail

    try:
        from honeyhive import HoneyHiveTracer
        from honeyhive.tracer.provider_detector import (
            IntegrationStrategy,
            ProviderDetector,
        )

        print("🔧 Setting up AWS Strands with HoneyHive integration...")

        # Test 1: HoneyHive first, then Strands
        print("\n📋 Test 1: HoneyHive → Strands initialization order")
        success_1 = test_honeyhive_first_strands_second(api_key, project)

        # Test 2: Strands first, then HoneyHive
        print("\n📋 Test 2: Strands → HoneyHive initialization order")
        success_2 = test_strands_first_honeyhive_second(api_key, project)

        # Test 3: Concurrent initialization
        print("\n📋 Test 3: Concurrent initialization")
        success_3 = test_concurrent_initialization(api_key, project)

        # Overall success
        all_success = success_1 and success_2 and success_3

        if all_success:
            print("\n✅ All AWS Strands integration tests passed!")
            print("   • Provider coexistence: ✓")
            print("   • Initialization order independence: ✓")
            print("   • Concurrent initialization: ✓")
        else:
            print("\n❌ Some AWS Strands integration tests failed")

        return all_success

    except ImportError as e:
        print(f"❌ Missing required dependencies: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during Strands integration test: {e}")
        return False


def test_honeyhive_first_strands_second(api_key: str, project: str) -> bool:
    """Test HoneyHive initializing first, then AWS Strands."""
    try:
        from honeyhive import HoneyHiveTracer
        from honeyhive.tracer.provider_detector import (
            IntegrationStrategy,
            ProviderDetector,
        )

        # Initialize HoneyHive tracer first
        tracer = HoneyHiveTracer.init(
            api_key=api_key,
            project=project,
            source="strands-compatibility-test",
            session_name="honeyhive_first_test",
            test_mode=False,
        )
        print("   ✓ HoneyHive tracer initialized first")

        # Get provider info before Strands
        detector = ProviderDetector()
        pre_strands_info = detector.get_provider_info()

        # Import and initialize Strands (should use existing provider)
        import strands
        from strands import Agent

        agent = Agent(
            name="test-agent",
            model="claude-3-haiku-20240307",
            system_prompt="You are a helpful test assistant.",
        )
        print("   ✓ AWS Strands agent initialized")

        # Get provider info after Strands
        post_strands_info = detector.get_provider_info()

        # Verify provider consistency
        provider_consistent = (
            pre_strands_info["provider_class_name"]
            == post_strands_info["provider_class_name"]
        )

        if provider_consistent and tracer.is_main_provider:
            print("   ✓ Provider coexistence successful")
            return True
        else:
            print("   ❌ Provider coexistence failed")
            return False

    except Exception as e:
        print(f"   ❌ Error in HoneyHive→Strands test: {e}")
        return False


def test_strands_first_honeyhive_second(api_key: str, project: str) -> bool:
    """Test AWS Strands initializing first, then HoneyHive."""
    try:
        # Import and initialize Strands first
        import strands
        from strands import Agent

        from honeyhive import HoneyHiveTracer
        from honeyhive.tracer.provider_detector import (
            IntegrationStrategy,
            ProviderDetector,
        )

        agent = Agent(
            name="test-agent-2",
            model="claude-3-haiku-20240307",
            system_prompt="You are a helpful test assistant.",
        )
        print("   ✓ AWS Strands agent initialized first")

        # Get provider info after Strands initialization
        detector = ProviderDetector()
        pre_honeyhive_info = detector.get_provider_info()

        # Initialize HoneyHive tracer (should integrate with existing provider)
        tracer = HoneyHiveTracer.init(
            api_key=api_key,
            project=project,
            source="strands-compatibility-test",
            session_name="strands_first_test",
            test_mode=False,
        )
        print("   ✓ HoneyHive tracer initialized")

        # Get provider info after HoneyHive
        post_honeyhive_info = detector.get_provider_info()

        # Verify integration strategy
        integration_successful = (
            pre_honeyhive_info["integration_strategy"]
            == IntegrationStrategy.MAIN_PROVIDER
            or post_honeyhive_info["integration_strategy"]
            == IntegrationStrategy.SPAN_PROCESSOR_ONLY
        )

        if integration_successful:
            print("   ✓ Integration strategy successful")
            return True
        else:
            print("   ❌ Integration strategy failed")
            return False

    except Exception as e:
        print(f"   ❌ Error in Strands→HoneyHive test: {e}")
        return False


def test_concurrent_initialization(api_key: str, project: str) -> bool:
    """Test concurrent initialization of HoneyHive and Strands."""
    try:
        from honeyhive import HoneyHiveTracer

        results = []
        errors = []

        def init_honeyhive():
            """Initialize HoneyHive in thread."""
            try:
                tracer = HoneyHiveTracer.init(
                    api_key=api_key,
                    project=project,
                    source="concurrent-test",
                    session_name="concurrent_honeyhive",
                    test_mode=False,
                )
                results.append(("honeyhive", tracer.is_main_provider, tracer))
            except Exception as e:
                errors.append(("honeyhive", str(e)))

        def init_strands():
            """Initialize Strands in thread."""
            try:
                # Small delay to create race condition
                time.sleep(0.05)

                import strands
                from strands import Agent

                agent = Agent(
                    name="concurrent-agent",
                    model="claude-3-haiku-20240307",
                    system_prompt="You are a concurrent test assistant.",
                )
                results.append(("strands", "initialized", "success"))
            except Exception as e:
                errors.append(("strands", str(e)))

        # Start concurrent initialization
        threads = [
            threading.Thread(target=init_honeyhive),
            threading.Thread(target=init_strands),
        ]

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join(timeout=30)  # 30 second timeout

        # Verify both initialized successfully
        if len(errors) == 0 and len(results) == 2:
            print("   ✓ Concurrent initialization successful")
            return True
        else:
            print(f"   ❌ Concurrent initialization failed - errors: {errors}")
            return False

    except Exception as e:
        print(f"   ❌ Error in concurrent initialization test: {e}")
        return False


def main():
    """Main test runner for compatibility testing."""
    print("🧪 AWS Strands + HoneyHive Compatibility Test")
    print("=" * 50)

    # Load environment variables from .env file
    load_env_file()

    success = test_strands_integration()

    if success:
        print("\n🎉 AWS Strands compatibility test completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 AWS Strands compatibility test failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
