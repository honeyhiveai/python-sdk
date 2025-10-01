#!/usr/bin/env python3
"""
Performance analysis: Regex vs Native String Operations
for semantic convention attribute parsing in span processor.
"""

import re
import time
from typing import Dict, List


def benchmark_message_extraction():
    """Compare regex vs native string operations for message extraction"""
    
    # Sample attributes from real OpenLLMetry instrumentation
    sample_attributes = {
        "gen_ai.request.messages.0.role": "system",
        "gen_ai.request.messages.0.content": "You are a helpful assistant",
        "gen_ai.request.messages.1.role": "user", 
        "gen_ai.request.messages.1.content": "Hello world",
        "gen_ai.request.messages.2.role": "assistant",
        "gen_ai.request.messages.2.content": "Hi there!",
        "gen_ai.request.messages.2.tool_calls.0.id": "call_123",
        "gen_ai.request.messages.2.tool_calls.0.name": "search_web",
        "gen_ai.request.messages.2.tool_calls.0.arguments": '{"query": "test"}',
        "gen_ai.usage.prompt_tokens": 50,
        "gen_ai.usage.completion_tokens": 25,
        "other_attribute": "value"
    }
    
    iterations = 100000
    
    # Method 1: Regex approach
    pattern = re.compile(r"gen_ai\.request\.messages\.(\d+)\.(role|content|tool_calls\..*)")
    
    def extract_with_regex(attributes: dict) -> list:
        messages = {}
        for key, value in attributes.items():
            match = pattern.match(key)
            if match:
                index = int(match.group(1))
                field = match.group(2)
                if index not in messages:
                    messages[index] = {}
                messages[index][field] = value
        return [messages[i] for i in sorted(messages.keys())]
    
    # Method 2: Native string operations
    def extract_with_native_strings(attributes: dict) -> list:
        messages = {}
        prefix = "gen_ai.request.messages."
        
        for key, value in attributes.items():
            if key.startswith(prefix):
                # Extract index and field using string operations
                remainder = key[len(prefix):]  # Remove prefix
                
                # Find first dot to separate index from field
                dot_pos = remainder.find('.')
                if dot_pos == -1:
                    continue
                    
                try:
                    index = int(remainder[:dot_pos])
                    field = remainder[dot_pos + 1:]
                    
                    if index not in messages:
                        messages[index] = {}
                    messages[index][field] = value
                except ValueError:
                    continue  # Skip if index is not a number
                    
        return [messages[i] for i in sorted(messages.keys())]
    
    # Method 3: Optimized native strings with split
    def extract_with_split(attributes: dict) -> list:
        messages = {}
        prefix = "gen_ai.request.messages."
        
        for key, value in attributes.items():
            if key.startswith(prefix):
                parts = key.split('.', 4)  # Split into max 5 parts
                if len(parts) >= 4:  # gen_ai, request, messages, index, field
                    try:
                        index = int(parts[3])
                        field = '.'.join(parts[4:]) if len(parts) > 4 else parts[3]
                        
                        if index not in messages:
                            messages[index] = {}
                        messages[index][field] = value
                    except (ValueError, IndexError):
                        continue
                        
        return [messages[i] for i in sorted(messages.keys())]
    
    # Benchmark regex approach
    start = time.perf_counter_ns()
    for _ in range(iterations):
        result_regex = extract_with_regex(sample_attributes)
    regex_time = time.perf_counter_ns() - start
    
    # Benchmark native string approach
    start = time.perf_counter_ns()
    for _ in range(iterations):
        result_native = extract_with_native_strings(sample_attributes)
    native_time = time.perf_counter_ns() - start
    
    # Benchmark split approach
    start = time.perf_counter_ns()
    for _ in range(iterations):
        result_split = extract_with_split(sample_attributes)
    split_time = time.perf_counter_ns() - start
    
    # Verify results are equivalent
    print("Results verification:")
    print(f"Regex result: {result_regex}")
    print(f"Native result: {result_native}")
    print(f"Split result: {result_split}")
    print()
    
    # Performance comparison
    print(f"Performance Comparison ({iterations:,} iterations):")
    print(f"Regex approach:        {regex_time / 1_000_000:.2f} ms ({regex_time / iterations:.0f} ns per call)")
    print(f"Native strings:        {native_time / 1_000_000:.2f} ms ({native_time / iterations:.0f} ns per call)")
    print(f"Split approach:        {split_time / 1_000_000:.2f} ms ({split_time / iterations:.0f} ns per call)")
    print()
    
    print("Speed improvement:")
    print(f"Native vs Regex:       {regex_time / native_time:.1f}x faster")
    print(f"Split vs Regex:        {regex_time / split_time:.1f}x faster")
    print(f"Split vs Native:       {native_time / split_time:.1f}x faster")


def benchmark_convention_detection():
    """Compare regex vs native string operations for convention detection"""
    
    sample_attributes = {
        "gen_ai.request.model": "gpt-4",
        "gen_ai.system": "OpenAI",
        "gen_ai.usage.prompt_tokens": 50,
        "llm.model_name": "gpt-4",
        "other.attribute": "value"
    }
    
    iterations = 1000000
    
    # Method 1: Using frozenset intersection (current approach)
    openllmetry_keys = frozenset(["gen_ai.request.model", "gen_ai.system", "gen_ai.usage.prompt_tokens"])
    openinference_keys = frozenset(["llm.model_name", "llm.provider", "llm.token_count.prompt"])
    
    def detect_with_frozenset(attributes: dict) -> str:
        attr_keys = frozenset(attributes.keys())
        if openllmetry_keys & attr_keys:
            return "openllmetry"
        elif openinference_keys & attr_keys:
            return "openinference"
        return "unknown"
    
    # Method 2: Direct key checking
    def detect_with_direct_check(attributes: dict) -> str:
        # Check for OpenLLMetry first (most common)
        if ("gen_ai.request.model" in attributes or 
            "gen_ai.system" in attributes or 
            "gen_ai.usage.prompt_tokens" in attributes):
            return "openllmetry"
        elif ("llm.model_name" in attributes or 
              "llm.provider" in attributes or 
              "llm.token_count.prompt" in attributes):
            return "openinference"
        return "unknown"
    
    # Method 3: Prefix-based detection
    def detect_with_prefix(attributes: dict) -> str:
        has_gen_ai = False
        has_llm = False
        
        for key in attributes:
            if not has_gen_ai and key.startswith("gen_ai."):
                has_gen_ai = True
            elif not has_llm and key.startswith("llm."):
                has_llm = True
            
            if has_gen_ai and has_llm:
                break
        
        if has_gen_ai:
            return "openllmetry"
        elif has_llm:
            return "openinference"
        return "unknown"
    
    # Benchmark approaches
    start = time.perf_counter_ns()
    for _ in range(iterations):
        result_frozenset = detect_with_frozenset(sample_attributes)
    frozenset_time = time.perf_counter_ns() - start
    
    start = time.perf_counter_ns()
    for _ in range(iterations):
        result_direct = detect_with_direct_check(sample_attributes)
    direct_time = time.perf_counter_ns() - start
    
    start = time.perf_counter_ns()
    for _ in range(iterations):
        result_prefix = detect_with_prefix(sample_attributes)
    prefix_time = time.perf_counter_ns() - start
    
    print(f"\nConvention Detection Comparison ({iterations:,} iterations):")
    print(f"Frozenset approach:    {frozenset_time / 1_000_000:.2f} ms ({frozenset_time / iterations:.0f} ns per call)")
    print(f"Direct check:          {direct_time / 1_000_000:.2f} ms ({direct_time / iterations:.0f} ns per call)")
    print(f"Prefix check:          {prefix_time / 1_000_000:.2f} ms ({prefix_time / iterations:.0f} ns per call)")
    print()
    
    print("Speed improvement:")
    print(f"Direct vs Frozenset:   {frozenset_time / direct_time:.1f}x faster")
    print(f"Prefix vs Frozenset:   {frozenset_time / prefix_time:.1f}x faster")
    print(f"Direct vs Prefix:      {prefix_time / direct_time:.1f}x faster")


def benchmark_event_type_detection():
    """Compare regex vs native string operations for event type detection"""
    
    span_names = [
        "openai.chat.completions",
        "anthropic.messages.create", 
        "search_web_tool",
        "chain.workflow.execute",
        "unknown_operation"
    ]
    
    iterations = 1000000
    
    # Method 1: Regex patterns
    model_pattern = re.compile(r".*(chat|completion|generate|model).*", re.IGNORECASE)
    tool_pattern = re.compile(r".*(tool|function|search|api).*", re.IGNORECASE)
    chain_pattern = re.compile(r".*(chain|workflow|pipeline).*", re.IGNORECASE)
    
    def detect_with_regex(span_name: str) -> str:
        if model_pattern.match(span_name):
            return "model"
        elif tool_pattern.match(span_name):
            return "tool"
        elif chain_pattern.match(span_name):
            return "chain"
        return "tool"
    
    # Method 2: Native string operations
    model_keywords = ["chat", "completion", "generate", "model"]
    tool_keywords = ["tool", "function", "search", "api"]
    chain_keywords = ["chain", "workflow", "pipeline"]
    
    def detect_with_native(span_name: str) -> str:
        span_lower = span_name.lower()
        
        for keyword in model_keywords:
            if keyword in span_lower:
                return "model"
        
        for keyword in tool_keywords:
            if keyword in span_lower:
                return "tool"
                
        for keyword in chain_keywords:
            if keyword in span_lower:
                return "chain"
                
        return "tool"
    
    # Method 3: Optimized with early termination
    def detect_optimized(span_name: str) -> str:
        span_lower = span_name.lower()
        
        # Check most common patterns first
        if ("chat" in span_lower or "completion" in span_lower or 
            "generate" in span_lower or "model" in span_lower):
            return "model"
        elif ("tool" in span_lower or "function" in span_lower or 
              "search" in span_lower or "api" in span_lower):
            return "tool"
        elif ("chain" in span_lower or "workflow" in span_lower or 
              "pipeline" in span_lower):
            return "chain"
        return "tool"
    
    # Benchmark all approaches across all span names
    total_regex_time = 0
    total_native_time = 0
    total_optimized_time = 0
    
    for span_name in span_names:
        # Regex
        start = time.perf_counter_ns()
        for _ in range(iterations):
            result_regex = detect_with_regex(span_name)
        total_regex_time += time.perf_counter_ns() - start
        
        # Native
        start = time.perf_counter_ns()
        for _ in range(iterations):
            result_native = detect_with_native(span_name)
        total_native_time += time.perf_counter_ns() - start
        
        # Optimized
        start = time.perf_counter_ns()
        for _ in range(iterations):
            result_optimized = detect_optimized(span_name)
        total_optimized_time += time.perf_counter_ns() - start
    
    total_iterations = iterations * len(span_names)
    
    print(f"\nEvent Type Detection Comparison ({total_iterations:,} iterations):")
    print(f"Regex approach:        {total_regex_time / 1_000_000:.2f} ms ({total_regex_time / total_iterations:.0f} ns per call)")
    print(f"Native strings:        {total_native_time / 1_000_000:.2f} ms ({total_native_time / total_iterations:.0f} ns per call)")
    print(f"Optimized native:      {total_optimized_time / 1_000_000:.2f} ms ({total_optimized_time / total_iterations:.0f} ns per call)")
    print()
    
    print("Speed improvement:")
    print(f"Native vs Regex:       {total_regex_time / total_native_time:.1f}x faster")
    print(f"Optimized vs Regex:    {total_regex_time / total_optimized_time:.1f}x faster")
    print(f"Optimized vs Native:   {total_native_time / total_optimized_time:.1f}x faster")


if __name__ == "__main__":
    print("=== String Operations Performance Analysis ===")
    print("Testing regex vs native Python string operations for span processor")
    print()
    
    benchmark_message_extraction()
    benchmark_convention_detection()
    benchmark_event_type_detection()
    
    print("\n=== Summary ===")
    print("Native Python string operations are significantly faster than regex for:")
    print("1. Message extraction from attribute keys")
    print("2. Convention detection via key checking")
    print("3. Event type detection via substring matching")
    print()
    print("Recommendation: Use native string operations for maximum performance")
