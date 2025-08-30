#!/usr/bin/env python3
"""
Compatibility Test Runner for HoneyHive SDK

Runs all model provider compatibility tests and generates a comprehensive report.
"""

import os
import sys
import subprocess
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class TestResult:
    """Result of a compatibility test."""
    provider: str
    instrumentor: str
    status: str  # "PASSED", "FAILED", "SKIPPED"
    duration: float
    error_message: Optional[str] = None
    notes: Optional[str] = None

class CompatibilityTestRunner:
    """Runs compatibility tests for all model providers."""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.results: List[TestResult] = []
        
        # Map test files to provider info
        self.test_configs = {
            # Direct Provider Support
            "test_openai.py": {
                "provider": "OpenAI",
                "instrumentor": "openinference-instrumentation-openai",
                "required_env": ["OPENAI_API_KEY"]
            },
            "test_azure_openai.py": {
                "provider": "Azure OpenAI",
                "instrumentor": "openinference-instrumentation-openai",
                "required_env": ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_DEPLOYMENT_NAME"]
            },
            "test_anthropic.py": {
                "provider": "Anthropic",
                "instrumentor": "openinference-instrumentation-anthropic", 
                "required_env": ["ANTHROPIC_API_KEY"]
            },
            "test_cohere.py": {
                "provider": "Cohere",
                "instrumentor": "openinference-instrumentation-cohere",
                "required_env": ["COHERE_API_KEY"]
            },
            "test_google_vertexai.py": {
                "provider": "Google Vertex AI",
                "instrumentor": "openinference-instrumentation-vertexai",
                "required_env": ["GCP_PROJECT"]
            },
            "test_google_genai.py": {
                "provider": "Google Generative AI",
                "instrumentor": "openinference-instrumentation-google-generativeai",
                "required_env": ["GOOGLE_API_KEY"]
            },
            
            # AWS Ecosystem
            "test_aws_bedrock.py": {
                "provider": "AWS Bedrock",
                "instrumentor": "openinference-instrumentation-bedrock",
                "required_env": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]
            },
            
            # Framework Integration
            "test_langchain.py": {
                "provider": "LangChain",
                "instrumentor": "openinference-instrumentation-langchain",
                "required_env": ["OPENAI_API_KEY"]  # Uses OpenAI as backend
            },
            "test_llama_index.py": {
                "provider": "LlamaIndex",
                "instrumentor": "openinference-instrumentation-llama-index",
                "required_env": ["OPENAI_API_KEY"]  # Uses OpenAI as backend
            },
            "test_dspy.py": {
                "provider": "DSPy",
                "instrumentor": "openinference-instrumentation-dspy",
                "required_env": ["OPENAI_API_KEY"]  # Uses OpenAI as backend
            },
            
            # Specialized Platforms
            "test_groq.py": {
                "provider": "Groq",
                "instrumentor": "openinference-instrumentation-groq",
                "required_env": ["GROQ_API_KEY"]
            },
            "test_mistralai.py": {
                "provider": "Mistral AI",
                "instrumentor": "openinference-instrumentation-mistralai",
                "required_env": ["MISTRAL_API_KEY"]
            },
            "test_ollama.py": {
                "provider": "Ollama",
                "instrumentor": "openinference-instrumentation-ollama",
                "required_env": []  # Runs locally, no API key needed
            },
            
            # Open Source & Self-Hosted
            "test_huggingface.py": {
                "provider": "Hugging Face",
                "instrumentor": "openinference-instrumentation-huggingface",
                "required_env": []  # Optional: HUGGINGFACE_API_KEY for private models
            },
            "test_litellm.py": {
                "provider": "LiteLLM",
                "instrumentor": "openinference-instrumentation-litellm",
                "required_env": ["OPENAI_API_KEY"]  # Uses OpenAI as proxy backend
            }
        }
    
    def check_base_requirements(self) -> bool:
        """Check if base HoneyHive requirements are met."""
        required_vars = ["HH_API_KEY", "HH_PROJECT"]
        missing = [var for var in required_vars if not os.getenv(var)]
        
        if missing:
            print("❌ Missing base HoneyHive environment variables:")
            for var in missing:
                print(f"   - {var}")
            return False
        
        return True
    
    def check_test_requirements(self, test_file: str) -> Tuple[bool, List[str]]:
        """Check if requirements for a specific test are met."""
        config = self.test_configs.get(test_file, {})
        required_env = config.get("required_env", [])
        
        missing = [var for var in required_env if not os.getenv(var)]
        return len(missing) == 0, missing
    
    def run_test(self, test_file: str) -> TestResult:
        """Run a single compatibility test."""
        config = self.test_configs[test_file]
        provider = config["provider"]
        instrumentor = config["instrumentor"]
        
        print(f"\n🧪 Testing {provider}...")
        print(f"   Instrumentor: {instrumentor}")
        
        # Check requirements
        can_run, missing_env = self.check_test_requirements(test_file)
        
        if not can_run:
            print(f"   ⏭️  Skipping - missing environment variables: {', '.join(missing_env)}")
            return TestResult(
                provider=provider,
                instrumentor=instrumentor,
                status="SKIPPED",
                duration=0.0,
                notes=f"Missing env vars: {', '.join(missing_env)}"
            )
        
        # Run the test
        test_path = self.test_dir / test_file
        start_time = time.time()
        
        try:
            result = subprocess.run(
                [sys.executable, str(test_path)],
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                print(f"   ✅ PASSED ({duration:.1f}s)")
                return TestResult(
                    provider=provider,
                    instrumentor=instrumentor,
                    status="PASSED",
                    duration=duration
                )
            else:
                print(f"   ❌ FAILED ({duration:.1f}s)")
                print(f"   Error: {result.stderr.strip()}")
                return TestResult(
                    provider=provider,
                    instrumentor=instrumentor,
                    status="FAILED",
                    duration=duration,
                    error_message=result.stderr.strip()
                )
                
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"   ⏰ TIMEOUT ({duration:.1f}s)")
            return TestResult(
                provider=provider,
                instrumentor=instrumentor,
                status="FAILED",
                duration=duration,
                error_message="Test timed out after 120 seconds"
            )
            
        except Exception as e:
            duration = time.time() - start_time
            print(f"   💥 ERROR ({duration:.1f}s): {e}")
            return TestResult(
                provider=provider,
                instrumentor=instrumentor,
                status="FAILED",
                duration=duration,
                error_message=str(e)
            )
    
    def run_all_tests(self) -> List[TestResult]:
        """Run all compatibility tests."""
        print("🚀 HoneyHive Model Provider Compatibility Test Suite")
        print("=" * 60)
        
        # Check base requirements
        if not self.check_base_requirements():
            print("\n❌ Cannot run tests - missing base requirements")
            return []
        
        print(f"✓ Base requirements met")
        print(f"✓ Found {len(self.test_configs)} test configurations")
        
        # Run each test
        results = []
        for test_file in sorted(self.test_configs.keys()):
            result = self.run_test(test_file)
            results.append(result)
            self.results.append(result)
        
        return results
    
    def print_summary(self):
        """Print test summary."""
        if not self.results:
            print("\n❌ No test results available")
            return
        
        passed = [r for r in self.results if r.status == "PASSED"]
        failed = [r for r in self.results if r.status == "FAILED"]
        skipped = [r for r in self.results if r.status == "SKIPPED"]
        
        print(f"\n📊 TEST SUMMARY")
        print("=" * 40)
        print(f"Total Tests:    {len(self.results)}")
        print(f"✅ Passed:      {len(passed)}")
        print(f"❌ Failed:      {len(failed)}")
        print(f"⏭️  Skipped:     {len(skipped)}")
        
        if passed:
            print(f"\n✅ PASSED TESTS:")
            for result in passed:
                print(f"   • {result.provider} ({result.duration:.1f}s)")
        
        if failed:
            print(f"\n❌ FAILED TESTS:")
            for result in failed:
                print(f"   • {result.provider}: {result.error_message}")
        
        if skipped:
            print(f"\n⏭️  SKIPPED TESTS:")
            for result in skipped:
                print(f"   • {result.provider}: {result.notes}")
        
        # Overall status
        if failed:
            print(f"\n❌ OVERALL: SOME TESTS FAILED ({len(failed)}/{len(self.results)})")
        elif skipped and not passed:
            print(f"\n⚠️  OVERALL: ALL TESTS SKIPPED")
        else:
            print(f"\n✅ OVERALL: ALL AVAILABLE TESTS PASSED")
    
    def generate_matrix_report(self, output_file: Optional[str] = None):
        """Generate compatibility matrix report."""
        if not self.results:
            print("❌ No results to generate matrix from")
            return
        
        lines = []
        lines.append("# HoneyHive Model Provider Compatibility Matrix")
        lines.append("")
        lines.append("| Provider | Instrumentor | Status | Duration | Notes |")
        lines.append("|----------|-------------|---------|----------|-------|")
        
        for result in self.results:
            status_emoji = {
                "PASSED": "✅",
                "FAILED": "❌", 
                "SKIPPED": "⏭️"
            }.get(result.status, "❓")
            
            duration_str = f"{result.duration:.1f}s" if result.duration > 0 else "N/A"
            notes = result.notes or result.error_message or ""
            if len(notes) > 50:
                notes = notes[:47] + "..."
            
            lines.append(f"| {result.provider} | `{result.instrumentor}` | {status_emoji} {result.status} | {duration_str} | {notes} |")
        
        lines.append("")
        lines.append(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        report_content = "\n".join(lines)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_content)
            print(f"📄 Matrix report saved to: {output_file}")
        else:
            print("\n📄 COMPATIBILITY MATRIX:")
            print(report_content)


def main():
    """Main entry point."""
    runner = CompatibilityTestRunner()
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Run HoneyHive compatibility tests")
    parser.add_argument("--output", "-o", help="Output file for matrix report")
    parser.add_argument("--test", "-t", help="Run specific test file only")
    args = parser.parse_args()
    
    try:
        if args.test:
            # Run specific test
            if args.test not in runner.test_configs:
                print(f"❌ Unknown test: {args.test}")
                print(f"Available tests: {', '.join(runner.test_configs.keys())}")
                sys.exit(1)
            
            result = runner.run_test(args.test)
            runner.results = [result]
        else:
            # Run all tests
            runner.run_all_tests()
        
        # Print summary
        runner.print_summary()
        
        # Generate matrix report
        runner.generate_matrix_report(args.output)
        
        # Exit with appropriate code
        failed_tests = [r for r in runner.results if r.status == "FAILED"]
        sys.exit(len(failed_tests))
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
