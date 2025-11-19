#!/usr/bin/env python3
"""
CLI Usage Example

This example demonstrates how to use the HoneyHive CLI for various tasks
including configuration management, monitoring, and API testing.

Prerequisites:
- HoneyHive package installed: pip install honeyhive
- Environment variables set: HH_API_KEY, HH_PROJECT, etc.
- Valid HoneyHive API key (get from https://app.honeyhive.ai)

This script shows CLI usage patterns and can be run alongside CLI commands.
"""

import os
import subprocess
import time
from typing import Any, Dict, List


def sanitize_output(text: str) -> str:
    """Sanitize output to hide sensitive information."""
    import re

    # Replace API keys with placeholder
    text = re.sub(r'"api_key": "hh_[^"]*"', '"api_key": "hh_your_api_key_here"', text)
    text = re.sub(
        r'"api_key": "sk-[^"]*"', '"api_key": "sk_your_openai_key_here"', text
    )
    text = re.sub(r"HH_API_KEY=[^\s]*", "HH_API_KEY=hh_your_api_key_here", text)
    text = re.sub(
        r"OPENAI_API_KEY=[^\s]*", "OPENAI_API_KEY=sk_your_openai_key_here", text
    )

    return text


def run_cli_command(command: List[str]) -> Dict[str, Any]:
    """Run a CLI command and return the result."""
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=30, check=False
        )
        return {
            "success": result.returncode == 0,
            "stdout": sanitize_output(result.stdout.strip()),
            "stderr": sanitize_output(result.stderr.strip()),
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "stderr": "Command timed out",
            "returncode": -1,
        }
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}


def demonstrate_configuration():
    """Demonstrate CLI configuration management."""
    print("🔧 CLI Configuration Management")
    print("=" * 40)

    # Show current configuration
    print("\n1. Show Current Configuration:")
    print("Command: honeyhive config show")
    result = run_cli_command(["honeyhive", "config", "show"])
    if result["success"]:
        print("✓ Configuration loaded successfully")
        print(result["stdout"])
    else:
        print(f"✗ Failed: {result['stderr']}")

    # Show configuration in different formats
    print("\n2. Show Configuration as Environment Variables:")
    print("Command: honeyhive config show --format env")
    result = run_cli_command(["honeyhive", "config", "show", "--format", "env"])
    if result["success"]:
        print("✓ Environment format:")
        print(result["stdout"])
    else:
        print(f"✗ Failed: {result['stderr']}")


def demonstrate_monitoring():
    """Demonstrate CLI monitoring capabilities."""
    print("\n🔍 CLI Monitoring & Status")
    print("=" * 30)

    # Check system status
    print("\n1. System Status Check:")
    print("Command: honeyhive monitor status")
    result = run_cli_command(["honeyhive", "monitor", "status"])
    if result["success"]:
        print("✓ System status:")
        print(result["stdout"])
    else:
        print(f"✗ Failed: {result['stderr']}")


def demonstrate_performance():
    """Demonstrate CLI performance analysis."""
    print("\n⚡ CLI Performance Analysis")
    print("=" * 30)

    # Run benchmarks
    print("\n1. Performance Benchmarks:")
    print("Command: honeyhive performance benchmark --iterations 100 --warmup 10")
    result = run_cli_command(
        [
            "honeyhive",
            "performance",
            "benchmark",
            "--iterations",
            "100",
            "--warmup",
            "10",
        ]
    )
    if result["success"]:
        print("✓ Benchmark results:")
        print(result["stdout"])
    else:
        print(f"✗ Failed: {result['stderr']}")


def demonstrate_api_testing():
    """Demonstrate CLI API testing capabilities."""
    print("\n🌐 CLI API Testing")
    print("=" * 20)

    # Test API connectivity with a simple endpoint
    print("\n1. API Connectivity Test:")
    print(
        "Command: honeyhive api request --method GET --url 'https://api.honeyhive.ai/api/v1/health' --timeout 10"
    )
    result = run_cli_command(
        [
            "honeyhive",
            "api",
            "request",
            "--method",
            "GET",
            "--url",
            "https://api.honeyhive.ai/api/v1/health",
            "--timeout",
            "10",
        ]
    )
    if result["success"]:
        print("✓ API request completed:")
        print(result["stdout"])
    else:
        print(f"✗ API request failed: {result['stderr']}")

    # Test with verbose logging
    print("\n2. API Test with Verbose Logging:")
    print(
        "Command: honeyhive --verbose api request --method GET --url 'https://api.honeyhive.ai/api/v1/health'"
    )
    result = run_cli_command(
        [
            "honeyhive",
            "--verbose",
            "api",
            "request",
            "--method",
            "GET",
            "--url",
            "https://api.honeyhive.ai/api/v1/health",
            "--timeout",
            "5",
        ]
    )
    if result["success"]:
        print("✓ Verbose API request completed:")
        print(result["stdout"])
    else:
        print(f"✗ Verbose API request failed: {result['stderr']}")


def demonstrate_tracing():
    """Demonstrate CLI tracing capabilities."""
    print("\n📊 CLI Tracing Management")
    print("=" * 27)

    print("\n1. Interactive Span Creation:")
    print("Command: honeyhive trace start --name 'cli_demo_span'")
    print("Note: This would start an interactive span (skipped in demo)")
    print("✓ In interactive mode, you would press Enter to end the span")

    print("\n2. Session Enrichment:")
    print(
        "Command: honeyhive trace enrich --session-id 'demo_session' --metadata '{\"demo\": true}'"
    )
    result = run_cli_command(
        [
            "honeyhive",
            "trace",
            "enrich",
            "--session-id",
            "demo_session",
            "--metadata",
            '{"demo": true, "source": "cli_example"}',
        ]
    )
    if result["success"]:
        print("✓ Session enrichment:")
        print(result["stdout"])
    else:
        print(f"✗ Failed: {result['stderr']}")


def demonstrate_cleanup():
    """Demonstrate CLI resource cleanup."""
    print("\n🧹 CLI Resource Cleanup")
    print("=" * 25)

    print("\n1. Clean Up Resources:")
    print("Command: honeyhive cleanup")
    result = run_cli_command(["honeyhive", "cleanup"])
    if result["success"]:
        print("✓ Cleanup completed:")
        print(result["stdout"])
    else:
        print(f"✗ Failed: {result['stderr']}")


def demonstrate_help_system():
    """Demonstrate CLI help system."""
    print("\n❓ CLI Help System")
    print("=" * 18)

    # Main help
    print("\n1. Main CLI Help:")
    print("Command: honeyhive --help")
    result = run_cli_command(["honeyhive", "--help"])
    if result["success"]:
        print("✓ Main help available")
        # Show just the first few lines
        lines = result["stdout"].split("\n")[:10]
        print("\n".join(lines))
        print("... (truncated)")
    else:
        print(f"✗ Failed: {result['stderr']}")

    # Command-specific help
    print("\n2. Command-Specific Help:")
    print("Command: honeyhive config --help")
    result = run_cli_command(["honeyhive", "config", "--help"])
    if result["success"]:
        print("✓ Config command help available")
        # Show just the first few lines
        lines = result["stdout"].split("\n")[:8]
        print("\n".join(lines))
        print("... (truncated)")
    else:
        print(f"✗ Failed: {result['stderr']}")


def check_prerequisites():
    """Check if prerequisites are met."""
    print("🔍 Checking Prerequisites")
    print("=" * 25)

    # Check if honeyhive CLI is available
    result = run_cli_command(["honeyhive", "--version"])
    if result["success"]:
        print("✓ HoneyHive CLI is installed and accessible")
    else:
        print("✗ HoneyHive CLI not found. Install with: pip install honeyhive")
        return False

    # Check for API key
    api_key = os.environ.get("HH_API_KEY")
    if api_key:
        print("✓ HH_API_KEY environment variable is set")
    else:
        print("⚠️  HH_API_KEY not set. Some features may not work.")

    # Check for project
    project = os.environ.get("HH_PROJECT")
    if project:
        print(f"✓ HH_PROJECT is set to: {project}")
    else:
        print("⚠️  HH_PROJECT not set. Using default project.")

    return True


def main():
    """Main demonstration function."""
    print("🚀 HoneyHive CLI Usage Example")
    print("This example demonstrates various CLI capabilities")
    print("and shows how to integrate CLI commands into workflows.\n")

    # Check prerequisites
    if not check_prerequisites():
        print(
            "\n❌ Prerequisites not met. Please install HoneyHive and set environment variables."
        )
        return

    # Run demonstrations
    try:
        demonstrate_configuration()
        demonstrate_monitoring()
        demonstrate_performance()
        demonstrate_api_testing()
        demonstrate_tracing()
        demonstrate_cleanup()
        demonstrate_help_system()

        print("\n🎉 CLI Example Completed Successfully!")
        print("\nKey CLI capabilities demonstrated:")
        print("✅ Configuration management (show, set)")
        print("✅ System monitoring and status checks")
        print("✅ Performance benchmarking")
        print("✅ API connectivity testing")
        print("✅ Tracing and session management")
        print("✅ Resource cleanup")
        print("✅ Comprehensive help system")

        print("\nNext steps:")
        print("• Set up your environment variables (HH_API_KEY, HH_PROJECT)")
        print("• Try interactive commands like 'honeyhive trace start'")
        print("• Use 'honeyhive monitor watch' for real-time monitoring")
        print("• Explore 'honeyhive --help' for all available commands")

    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")


if __name__ == "__main__":
    main()
