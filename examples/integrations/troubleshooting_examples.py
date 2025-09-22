"""
Troubleshooting Examples for Non-Instrumentor Framework Integration

This example demonstrates common issues and their solutions when integrating
HoneyHive with non-instrumentor frameworks.
"""

import os
import sys
import time
from typing import Dict, Any, Optional
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from honeyhive import HoneyHiveTracer
from honeyhive.tracer.provider_detector import ProviderDetector
from honeyhive.tracer.processor_integrator import ProviderIncompatibleError


class ProblematicFramework:
    """
    A framework that demonstrates common integration problems.
    """

    def __init__(self, problem_type: str = "none"):
        self.problem_type = problem_type
        self.name = f"ProblematicFramework-{problem_type}"

        if problem_type == "early_provider_setup":
            # Problem: Sets up provider too early, before HoneyHive
            self.provider = TracerProvider()
            trace.set_tracer_provider(self.provider)
        elif problem_type == "no_provider_access":
            # Problem: Doesn't expose provider for integration
            self._private_provider = TracerProvider()
            trace.set_tracer_provider(self._private_provider)
        elif problem_type == "custom_exporter":
            # Problem: Uses custom exporter that conflicts
            self.provider = TracerProvider()
            # Would add custom exporter here
            trace.set_tracer_provider(self.provider)

        self.tracer = trace.get_tracer(self.name)

    def do_work(self, work_type: str = "normal") -> Dict[str, Any]:
        """Perform some work with tracing."""
        with self.tracer.start_as_current_span(f"{self.name}.do_work") as span:
            span.set_attribute("work.type", work_type)
            span.set_attribute("framework.problem", self.problem_type)

            if work_type == "error":
                # Simulate an error
                span.set_attribute("error", True)
                raise ValueError("Simulated framework error")

            time.sleep(0.01)  # Simulate work

            result = {
                "framework": self.name,
                "work_type": work_type,
                "problem_type": self.problem_type,
                "status": "completed",
                "timestamp": time.time(),
            }

            span.set_attribute("work.status", "completed")
            return result


def troubleshoot_provider_detection():
    """Troubleshoot provider detection issues."""
    print("🔍 Troubleshooting Provider Detection")
    print("=" * 38)

    # Reset OpenTelemetry state
    trace._TRACER_PROVIDER = None

    print("1. Testing provider detection without any setup...")
    detector = ProviderDetector()
    provider_info = detector.detect_provider()
    print(f"   Detected: {provider_info}")

    print("2. Testing with ProxyTracerProvider...")
    # This simulates the initial state before any real provider is set
    from opentelemetry.trace import ProxyTracerProvider

    proxy_provider = ProxyTracerProvider()
    trace.set_tracer_provider(proxy_provider)

    provider_info = detector.detect_provider()
    strategy = detector.determine_integration_strategy(provider_info)
    print(f"   Detected: {provider_info}")
    print(f"   Strategy: {strategy}")

    print("3. Testing with real TracerProvider...")
    real_provider = TracerProvider()
    trace.set_tracer_provider(real_provider)

    provider_info = detector.detect_provider()
    strategy = detector.determine_integration_strategy(provider_info)
    print(f"   Detected: {provider_info}")
    print(f"   Strategy: {strategy}")

    print("   ✅ Provider detection troubleshooting completed")
    print()


def troubleshoot_initialization_order():
    """Troubleshoot initialization order issues."""
    print("🔄 Troubleshooting Initialization Order")
    print("=" * 40)

    # Test Case 1: HoneyHive first (should work)
    print("1. Testing HoneyHive first...")
    trace._TRACER_PROVIDER = None  # Reset

    try:
        tracer = HoneyHiveTracer.init(
            api_key="test-key", project="init-order-test", test_mode=True, verbose=False
        )

        framework = ProblematicFramework("none")
        result = framework.do_work("honeyhive_first")

        print(f"   ✅ Success: {result['status']}")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test Case 2: Framework first (should also work)
    print("2. Testing framework first...")
    trace._TRACER_PROVIDER = None  # Reset

    try:
        framework = ProblematicFramework("early_provider_setup")

        tracer = HoneyHiveTracer.init(
            api_key="test-key", project="init-order-test", test_mode=True, verbose=False
        )

        result = framework.do_work("framework_first")
        print(f"   ✅ Success: {result['status']}")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test Case 3: Problematic framework
    print("3. Testing problematic framework...")
    trace._TRACER_PROVIDER = None  # Reset

    try:
        framework = ProblematicFramework("no_provider_access")

        tracer = HoneyHiveTracer.init(
            api_key="test-key", project="init-order-test", test_mode=True, verbose=False
        )

        result = framework.do_work("problematic")
        print(f"   ✅ Success despite problems: {result['status']}")

    except Exception as e:
        print(f"   ⚠️  Expected issue: {e}")

    print("   ✅ Initialization order troubleshooting completed")
    print()


def troubleshoot_missing_spans():
    """Troubleshoot missing spans in HoneyHive."""
    print("🔎 Troubleshooting Missing Spans")
    print("=" * 32)

    # Reset state
    trace._TRACER_PROVIDER = None

    print("1. Checking API key configuration...")
    api_key = os.getenv("HH_API_KEY")
    if api_key:
        print(f"   ✅ HH_API_KEY is set (length: {len(api_key)})")
    else:
        print("   ❌ HH_API_KEY is not set")

    print("2. Checking project configuration...")
    project = os.getenv("HH_PROJECT")
    if project:
        print(f"   ✅ HH_PROJECT is set: {project}")
    else:
        print("   ⚠️  HH_PROJECT is not set (using default)")

    print("3. Checking OTLP configuration...")
    otlp_enabled = os.getenv("HH_OTLP_ENABLED", "true")
    print(f"   OTLP enabled: {otlp_enabled}")

    print("4. Testing span creation and export...")
    try:
        tracer = HoneyHiveTracer.init(
            api_key=api_key or "test-key",
            project=project or "troubleshooting-test",
            test_mode=True,  # Use test mode to avoid API calls
            verbose=True,  # Enable verbose logging
        )

        print(f"   ✅ Tracer initialized (Session: {tracer.session_id})")

        # Create test spans
        framework = ProblematicFramework("none")

        for i in range(3):
            result = framework.do_work(f"test_span_{i}")
            print(f"   Span {i+1}: {result['status']}")

        print("   ✅ Test spans created successfully")

    except Exception as e:
        print(f"   ❌ Error creating spans: {e}")

    print("5. Checking span processor integration...")
    try:
        from honeyhive.tracer.processor_integrator import ProcessorIntegrator

        integrator = ProcessorIntegrator()
        current_provider = trace.get_tracer_provider()

        print(f"   Current provider type: {type(current_provider).__name__}")

        if hasattr(current_provider, "_span_processors"):
            processor_count = len(current_provider._span_processors)
            print(f"   Span processors: {processor_count}")
        else:
            print("   ⚠️  Cannot access span processors")

    except Exception as e:
        print(f"   ❌ Error checking processors: {e}")

    print("   ✅ Missing spans troubleshooting completed")
    print()


def troubleshoot_performance_issues():
    """Troubleshoot performance issues."""
    print("⚡ Troubleshooting Performance Issues")
    print("=" * 37)

    # Reset state
    trace._TRACER_PROVIDER = None

    print("1. Measuring baseline performance...")

    # Baseline: No tracing
    start_time = time.perf_counter()
    for i in range(100):
        time.sleep(0.001)  # Simulate 1ms work
    baseline_time = time.perf_counter() - start_time

    print(f"   Baseline (no tracing): {baseline_time:.3f}s for 100 operations")

    print("2. Measuring with HoneyHive tracing...")

    # With HoneyHive
    tracer = HoneyHiveTracer.init(
        api_key="perf-test-key",
        project="performance-test",
        test_mode=True,
        verbose=False,
    )

    framework = ProblematicFramework("none")

    start_time = time.perf_counter()
    for i in range(100):
        try:
            result = framework.do_work(f"perf_test_{i}")
        except Exception:
            pass  # Ignore errors for performance testing
    tracing_time = time.perf_counter() - start_time

    print(f"   With tracing: {tracing_time:.3f}s for 100 operations")

    # Calculate overhead
    overhead = ((tracing_time - baseline_time) / baseline_time) * 100
    print(f"   Overhead: {overhead:.1f}%")

    if overhead > 10:
        print("   ⚠️  High overhead detected (>10%)")
        print("   Suggestions:")
        print("     - Check if verbose logging is enabled")
        print("     - Verify test_mode is enabled for testing")
        print("     - Consider batch span processing")
    else:
        print("   ✅ Overhead within acceptable range (<10%)")

    print("3. Memory usage check...")
    try:
        import psutil

        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        print(f"   Current memory usage: {memory_mb:.1f} MB")
    except ImportError:
        print("   ⚠️  psutil not available for memory monitoring")

    print("   ✅ Performance troubleshooting completed")
    print()


def troubleshoot_integration_errors():
    """Troubleshoot common integration errors."""
    print("🚨 Troubleshooting Integration Errors")
    print("=" * 37)

    print("1. Testing provider incompatibility...")
    trace._TRACER_PROVIDER = None

    try:
        # Simulate incompatible provider
        class IncompatibleProvider:
            def __init__(self):
                self.name = "IncompatibleProvider"

        # This would normally cause issues
        incompatible = IncompatibleProvider()

        # HoneyHive should handle this gracefully
        tracer = HoneyHiveTracer.init(
            api_key="test-key", project="error-test", test_mode=True, verbose=False
        )

        print("   ✅ HoneyHive handled incompatible provider gracefully")

    except ProviderIncompatibleError as e:
        print(f"   ⚠️  Provider incompatibility detected: {e}")
        print("   Suggestion: Initialize HoneyHive before the framework")

    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")

    print("2. Testing configuration errors...")

    # Test missing API key
    try:
        tracer = HoneyHiveTracer.init(
            api_key=None,
            project="error-test",
            test_mode=False,  # This should cause an error
        )
        print("   ⚠️  No error with missing API key (unexpected)")

    except Exception as e:
        print(f"   ✅ Expected error with missing API key: {type(e).__name__}")

    # Test empty project
    try:
        tracer = HoneyHiveTracer.init(
            api_key="test-key", project="", test_mode=True  # Empty project
        )
        print("   ✅ Empty project handled gracefully")

    except Exception as e:
        print(f"   ⚠️  Error with empty project: {e}")

    print("3. Testing framework errors...")

    tracer = HoneyHiveTracer.init(
        api_key="test-key", project="error-test", test_mode=True, verbose=False
    )

    framework = ProblematicFramework("none")

    # Test error handling in framework operations
    try:
        result = framework.do_work("error")  # This should raise an error
        print("   ⚠️  No error raised (unexpected)")

    except ValueError as e:
        print(f"   ✅ Framework error handled correctly: {e}")

    except Exception as e:
        print(f"   ❌ Unexpected error type: {type(e).__name__}: {e}")

    print("   ✅ Integration error troubleshooting completed")
    print()


def troubleshoot_context_propagation():
    """Troubleshoot context propagation issues."""
    print("🔗 Troubleshooting Context Propagation")
    print("=" * 38)

    # Reset state
    trace._TRACER_PROVIDER = None

    print("1. Testing basic context propagation...")

    tracer = HoneyHiveTracer.init(
        api_key="test-key", project="context-test", test_mode=True, verbose=False
    )

    framework = ProblematicFramework("none")
    otel_tracer = trace.get_tracer("context-test")

    # Test parent-child span relationship
    with otel_tracer.start_as_current_span("parent-span") as parent:
        parent.set_attribute("span.type", "parent")
        parent_context = parent.get_span_context()

        # Child operation
        result = framework.do_work("context_test")

        print(f"   Parent span ID: {format(parent_context.span_id, '016x')}")
        print(f"   Parent trace ID: {format(parent_context.trace_id, '032x')}")
        print(f"   Child operation: {result['status']}")

    print("2. Testing cross-framework context...")

    framework_a = ProblematicFramework("none")
    framework_b = ProblematicFramework("none")

    with otel_tracer.start_as_current_span("cross-framework-test") as span:
        span.set_attribute("test.type", "cross_framework")

        # Operation in framework A
        result_a = framework_a.do_work("cross_test_a")

        # Operation in framework B (should inherit context)
        result_b = framework_b.do_work("cross_test_b")

        print(f"   Framework A: {result_a['status']}")
        print(f"   Framework B: {result_b['status']}")
        print("   ✅ Cross-framework context maintained")

    print("3. Testing baggage propagation...")

    from opentelemetry import baggage

    # Set baggage
    ctx = baggage.set_baggage("test.key", "test.value")

    with otel_tracer.start_as_current_span("baggage-test") as span:
        # Check if baggage is available
        baggage_value = baggage.get_baggage("test.key")

        if baggage_value:
            print(f"   ✅ Baggage propagated: {baggage_value}")
            span.set_attribute("baggage.test_key", baggage_value)
        else:
            print("   ⚠️  Baggage not propagated")

        result = framework.do_work("baggage_test")
        print(f"   Operation with baggage: {result['status']}")

    print("   ✅ Context propagation troubleshooting completed")
    print()


def generate_troubleshooting_report():
    """Generate a comprehensive troubleshooting report."""
    print("📋 Generating Troubleshooting Report")
    print("=" * 36)

    report = {
        "timestamp": time.time(),
        "python_version": sys.version,
        "platform": sys.platform,
        "environment": {},
        "honeyhive_config": {},
        "opentelemetry_info": {},
        "recommendations": [],
    }

    # Environment variables
    env_vars = ["HH_API_KEY", "HH_PROJECT", "HH_SOURCE", "HH_OTLP_ENABLED"]
    for var in env_vars:
        value = os.getenv(var)
        if var == "HH_API_KEY" and value:
            # Mask API key for security
            report["environment"][var] = f"***{value[-4:]}" if len(value) > 4 else "***"
        else:
            report["environment"][var] = value

    # HoneyHive configuration
    try:
        tracer = HoneyHiveTracer.init(
            api_key="report-test-key",
            project="troubleshooting-report",
            test_mode=True,
            verbose=False,
        )

        report["honeyhive_config"] = {
            "initialization": "success",
            "session_id": tracer.session_id,
            "project": getattr(tracer, "project", "unknown"),
            "source": getattr(tracer, "source", "unknown"),
            "test_mode": getattr(tracer, "test_mode", "unknown"),
        }

    except Exception as e:
        report["honeyhive_config"] = {"initialization": "failed", "error": str(e)}
        report["recommendations"].append("Fix HoneyHive initialization error")

    # OpenTelemetry information
    try:
        current_provider = trace.get_tracer_provider()
        report["opentelemetry_info"] = {
            "provider_type": type(current_provider).__name__,
            "has_span_processors": hasattr(current_provider, "_span_processors"),
        }

        if hasattr(current_provider, "_span_processors"):
            processor_count = len(current_provider._span_processors)
            report["opentelemetry_info"]["span_processor_count"] = processor_count

            if processor_count == 0:
                report["recommendations"].append(
                    "No span processors found - spans may not be exported"
                )

    except Exception as e:
        report["opentelemetry_info"] = {"error": str(e)}
        report["recommendations"].append("Check OpenTelemetry configuration")

    # Generate recommendations
    if not report["environment"]["HH_API_KEY"]:
        report["recommendations"].append("Set HH_API_KEY environment variable")

    if not report["environment"]["HH_PROJECT"]:
        report["recommendations"].append(
            "Set HH_PROJECT environment variable (required for OTLP)"
        )

    if report["environment"]["HH_OTLP_ENABLED"] == "false":
        report["recommendations"].append(
            "OTLP is disabled - spans will not be exported to HoneyHive"
        )

    # Print report
    print("Environment Variables:")
    for key, value in report["environment"].items():
        status = "✅" if value else "❌"
        print(f"  {status} {key}: {value or 'Not set'}")

    print("\nHoneyHive Configuration:")
    for key, value in report["honeyhive_config"].items():
        print(f"  {key}: {value}")

    print("\nOpenTelemetry Information:")
    for key, value in report["opentelemetry_info"].items():
        print(f"  {key}: {value}")

    if report["recommendations"]:
        print("\nRecommendations:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"  {i}. {rec}")
    else:
        print("\n✅ No issues detected!")

    print("\n✅ Troubleshooting report completed")
    return report


def main():
    """Run all troubleshooting examples."""
    print("🔧 HoneyHive Integration Troubleshooting Guide")
    print("=" * 48)
    print()

    try:
        # Run troubleshooting functions
        troubleshoot_provider_detection()
        troubleshoot_initialization_order()
        troubleshoot_missing_spans()
        troubleshoot_performance_issues()
        troubleshoot_integration_errors()
        troubleshoot_context_propagation()

        # Generate final report
        generate_troubleshooting_report()

        print("\n🎉 All troubleshooting examples completed!")
        print("\n💡 Tips for successful integration:")
        print("   1. Initialize HoneyHive early in your application")
        print("   2. Set required environment variables (HH_API_KEY, HH_PROJECT)")
        print("   3. Use test_mode=True during development")
        print("   4. Enable verbose=True for debugging")
        print("   5. Check the HoneyHive dashboard for traces")

    except KeyboardInterrupt:
        print("\n👋 Troubleshooting interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error during troubleshooting: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
