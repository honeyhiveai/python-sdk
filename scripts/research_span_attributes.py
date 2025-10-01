#!/usr/bin/env python3
"""
Span Attribute Research Script

Systematically captures real span attributes from different instrumentors,
providers, and scenarios to create a comprehensive reference for transform
development.

Usage:
    python scripts/research_span_attributes.py --instrumentors all --providers all
    python scripts/research_span_attributes.py --instrumentors openinference --providers openai
    python scripts/research_span_attributes.py --scenarios basic,tool_calls
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from honeyhive import HoneyHiveTracer
from benchmark.monitoring.attribute_capture import SpanAttributeCapture
from benchmark.monitoring.span_interceptor import BenchmarkSpanInterceptor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SpanAttributeResearcher:
    """Systematic span attribute research across instrumentors and providers.
    
    Example:
        >>> researcher = SpanAttributeResearcher()
        >>> researcher.run_research(
        ...     instrumentors=["openinference", "traceloop"],
        ...     providers=["openai", "anthropic"],
        ...     scenarios=["basic_chat", "tool_calls"]
        ... )
    """
    
    def __init__(self, output_dir: str = "span_attribute_captures"):
        """Initialize the researcher.
        
        :param output_dir: Directory to save captured data
        :type output_dir: str
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.capture = SpanAttributeCapture(output_dir=str(self.output_dir))
        
        logger.info(f"🔬 Span Attribute Researcher initialized: {self.output_dir}")
    
    def run_research(
        self,
        instrumentors: List[str],
        providers: List[str],
        scenarios: List[str],
        operations_per_scenario: int = 3
    ) -> None:
        """Run systematic span attribute research.
        
        :param instrumentors: List of instrumentors to test
        :type instrumentors: List[str]
        :param providers: List of providers to test
        :type providers: List[str]
        :param scenarios: List of scenarios to test
        :type scenarios: List[str]
        :param operations_per_scenario: Operations per scenario
        :type operations_per_scenario: int
        """
        logger.info(
            f"🔬 Starting research: {len(instrumentors)} instrumentors × "
            f"{len(providers)} providers × {len(scenarios)} scenarios"
        )
        
        total_combinations = len(instrumentors) * len(providers) * len(scenarios)
        current = 0
        
        for instrumentor in instrumentors:
            for provider in providers:
                for scenario in scenarios:
                    current += 1
                    logger.info(
                        f"\n{'='*80}\n"
                        f"[{current}/{total_combinations}] Testing: "
                        f"{instrumentor}/{provider}/{scenario}\n"
                        f"{'='*80}"
                    )
                    
                    try:
                        self._test_combination(
                            instrumentor=instrumentor,
                            provider=provider,
                            scenario=scenario,
                            operations=operations_per_scenario
                        )
                    except Exception as e:
                        logger.error(
                            f"❌ Failed {instrumentor}/{provider}/{scenario}: {e}"
                        )
                        continue
        
        # Save all captures
        logger.info("\n" + "="*80)
        logger.info("💾 Saving captured data...")
        logger.info("="*80)
        
        main_file = self.capture.save_captures()
        logger.info(f"✅ Main file: {main_file}")
        
        category_files = self.capture.save_by_category()
        logger.info(f"✅ Category files: {len(category_files)} saved")
        
        matrix = self.capture.generate_attribute_matrix()
        logger.info(f"✅ Attribute matrix generated")
        
        self.capture.print_summary()
        
        logger.info(f"\n✅ Research complete! Output: {self.output_dir}")
    
    def _test_combination(
        self,
        instrumentor: str,
        provider: str,
        scenario: str,
        operations: int
    ) -> None:
        """Test a single instrumentor/provider/scenario combination.
        
        :param instrumentor: Instrumentor name
        :type instrumentor: str
        :param provider: Provider name
        :type provider: str
        :param scenario: Scenario name
        :type scenario: str
        :param operations: Number of operations to run
        :type operations: int
        """
        # Initialize tracer
        tracer = HoneyHiveTracer.init(
            api_key=os.getenv("HH_API_KEY", "research-key"),
            project=os.getenv("HH_PROJECT", "span-research"),
            source=f"{instrumentor}_{provider}_{scenario}",
            verbose=True
        )
        
        # Add span interceptor
        interceptor = BenchmarkSpanInterceptor()
        tracer.provider.add_span_processor(interceptor)
        interceptor.start_interception()
        
        # Initialize provider and instrumentor
        provider_instance = self._get_provider_instance(
            instrumentor=instrumentor,
            provider=provider,
            tracer=tracer
        )
        
        if not provider_instance:
            logger.warning(f"⚠️  Provider not available: {instrumentor}/{provider}")
            return
        
        # Run scenario
        prompts = self._get_scenario_prompts(scenario, operations)
        
        for i, prompt in enumerate(prompts):
            logger.info(f"  Operation {i+1}/{operations}: {scenario}")
            try:
                response = provider_instance.make_call(prompt, operation_id=i)
                logger.debug(f"    ✓ Success: {len(response.response_text)} chars")
            except Exception as e:
                logger.error(f"    ✗ Failed: {e}")
        
        # Capture spans
        spans, overhead = interceptor.stop_interception()
        logger.info(f"  📸 Captured {len(spans)} spans")
        
        for span in spans:
            self.capture.capture_span(
                span=span,
                instrumentor=instrumentor,
                provider=provider,
                scenario=scenario,
                metadata={
                    "operations_run": operations,
                    "overhead_ms": overhead.get("avg_real_tracer_overhead_ms", 0.0)
                }
            )
        
        # Cleanup
        provider_instance.cleanup_instrumentor()
    
    def _get_provider_instance(
        self,
        instrumentor: str,
        provider: str,
        tracer: any
    ) -> Optional[any]:
        """Get provider instance for instrumentor/provider combination.
        
        :param instrumentor: Instrumentor name
        :type instrumentor: str
        :param provider: Provider name
        :type provider: str
        :param tracer: HoneyHive tracer
        :type tracer: any
        :return: Provider instance or None
        :rtype: Optional[any]
        """
        from benchmark.core.config import BenchmarkConfig
        
        # Create default config
        config = BenchmarkConfig(
            operations=3,
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022"),
            max_tokens=500,
            temperature=0.7,
            timeout=30.0
        )
        
        # Map to provider classes
        if instrumentor == "openinference" and provider == "openai":
            from benchmark.providers.openinference_openai_provider import OpenInferenceOpenAIProvider
            instance = OpenInferenceOpenAIProvider(config, tracer)
        elif instrumentor == "openinference" and provider == "anthropic":
            from benchmark.providers.openinference_anthropic_provider import OpenInferenceAnthropicProvider
            instance = OpenInferenceAnthropicProvider(config, tracer)
        elif instrumentor == "traceloop" and provider == "openai":
            from benchmark.providers.traceloop_openai_provider import TraceloopOpenAIProvider
            instance = TraceloopOpenAIProvider(config, tracer)
        elif instrumentor == "traceloop" and provider == "anthropic":
            from benchmark.providers.traceloop_anthropic_provider import TraceloopAnthropicProvider
            instance = TraceloopAnthropicProvider(config, tracer)
        elif instrumentor == "openlit" and provider == "openai":
            from benchmark.providers.openlit_openai_provider import OpenLitOpenAIProvider
            instance = OpenLitOpenAIProvider(config, tracer)
        else:
            logger.warning(f"⚠️  Unknown combination: {instrumentor}/{provider}")
            return None
        
        # Initialize
        try:
            instance.initialize_client()
            instance.initialize_instrumentor()
            return instance
        except Exception as e:
            logger.error(f"❌ Failed to initialize {instrumentor}/{provider}: {e}")
            return None
    
    def _get_scenario_prompts(self, scenario: str, count: int) -> List[str]:
        """Get prompts for a scenario.
        
        :param scenario: Scenario name
        :type scenario: str
        :param count: Number of prompts needed
        :type count: int
        :return: List of prompts
        :rtype: List[str]
        """
        scenarios = {
            "basic_chat": [
                "Hello! How are you today?",
                "What is the capital of France?",
                "Explain quantum computing in simple terms."
            ],
            "tool_calls": [
                "What's the weather like in San Francisco? Use the weather API.",
                "Calculate 15 * 23 using the calculator tool.",
                "Search for information about Python programming."
            ],
            "multimodal": [
                "Describe what you see in this image: [image_url]",
                "Analyze this audio file: [audio_url]",
                "Process this document: [doc_url]"
            ],
            "complex_chat": [
                "Write a detailed analysis of the Renaissance period, covering art, science, and culture.",
                "Explain the differences between machine learning, deep learning, and artificial intelligence.",
                "Provide a comprehensive guide to setting up a Python web application."
            ],
            "streaming": [
                "Tell me a story about space exploration.",
                "Explain the history of the internet.",
                "Describe the process of photosynthesis."
            ]
        }
        
        prompts = scenarios.get(scenario, scenarios["basic_chat"])
        
        # Repeat if needed
        while len(prompts) < count:
            prompts.extend(prompts)
        
        return prompts[:count]


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Systematically research span attributes across instrumentors/providers"
    )
    
    parser.add_argument(
        "--instrumentors",
        type=str,
        default="all",
        help="Comma-separated instrumentors (openinference,traceloop,openlit) or 'all'"
    )
    
    parser.add_argument(
        "--providers",
        type=str,
        default="all",
        help="Comma-separated providers (openai,anthropic,gemini) or 'all'"
    )
    
    parser.add_argument(
        "--scenarios",
        type=str,
        default="basic_chat,complex_chat",
        help="Comma-separated scenarios or 'all'"
    )
    
    parser.add_argument(
        "--operations",
        type=int,
        default=3,
        help="Operations per scenario (default: 3)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="span_attribute_captures",
        help="Output directory for captured data"
    )
    
    args = parser.parse_args()
    
    # Parse instrumentors
    if args.instrumentors == "all":
        instrumentors = ["openinference", "traceloop", "openlit"]
    else:
        instrumentors = [i.strip() for i in args.instrumentors.split(",")]
    
    # Parse providers
    if args.providers == "all":
        providers = ["openai", "anthropic"]
    else:
        providers = [p.strip() for p in args.providers.split(",")]
    
    # Parse scenarios
    if args.scenarios == "all":
        scenarios = ["basic_chat", "tool_calls", "multimodal", "complex_chat"]
    else:
        scenarios = [s.strip() for s in args.scenarios.split(",")]
    
    # Run research
    researcher = SpanAttributeResearcher(output_dir=args.output_dir)
    researcher.run_research(
        instrumentors=instrumentors,
        providers=providers,
        scenarios=scenarios,
        operations_per_scenario=args.operations
    )


if __name__ == "__main__":
    main()
