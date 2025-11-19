#!/usr/bin/env python3
"""
Convert span dumps to test case JSON files.

This script reads span dump files and converts them to the test case format
required for validation.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Set
from collections import defaultdict


class TestCaseGenerator:
    """Generate test cases from span dumps."""
    
    def __init__(self, span_dumps_dir: str = "span_dumps", output_dir: str = "test_cases"):
        self.span_dumps_dir = Path(span_dumps_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Track unique test case schemas to avoid duplicates
        self.seen_schemas: Set[str] = set()
        self.test_case_count = defaultdict(int)
    
    def load_span_dumps(self) -> List[Dict[str, Any]]:
        """Load all span dump files."""
        span_dumps = []
        
        for file in self.span_dumps_dir.glob("*.json"):
            print(f"📂 Loading {file.name}...")
            with open(file, 'r') as f:
                data = json.load(f)
                span_dumps.append({
                    'file': file.name,
                    'data': data
                })
        
        return span_dumps
    
    def extract_instrumentor_provider(self, span: Dict[str, Any], integration_name: str) -> tuple:
        """Extract instrumentor and provider from span."""
        attributes = span.get('attributes', {})
        instrumentation = span.get('instrumentation_info', {})
        scope_name = instrumentation.get('name', '')
        
        # Determine instrumentor from scope
        # We need to capture all framework-specific instrumentation, not just OpenInference
        instrumentor = 'unknown'
        
        if 'openinference.instrumentation.google_adk' in scope_name:
            instrumentor = 'openinference_google_adk'
        elif 'openinference.instrumentation.openai' in scope_name:
            # Check integration name to determine if it's AutoGen, Semantic Kernel, or pure OpenAI
            if integration_name == 'autogen':
                instrumentor = 'autogen_openai'
            elif integration_name == 'semantic_kernel':
                instrumentor = 'semantic_kernel_openai'
            else:
                instrumentor = 'openinference_openai'
        elif 'autogen-core' in scope_name or 'autogen' in scope_name.lower():
            instrumentor = 'autogen_core'
        elif 'semantic_kernel.functions.kernel_function' in scope_name:
            instrumentor = 'semantic_kernel_function'
        elif 'semantic_kernel.connectors.ai.chat_completion_client_base' in scope_name:
            instrumentor = 'semantic_kernel_connector'
        elif 'agent_runtime' in scope_name.lower() and 'inprocessruntime' in scope_name.lower():
            instrumentor = 'semantic_kernel_runtime'
        elif 'semantic_kernel' in scope_name.lower():
            instrumentor = 'semantic_kernel'
        elif 'google' in scope_name.lower() or 'gemini' in attributes.get('llm.model_name', '').lower():
            instrumentor = 'google_adk'
        
        # Determine provider from model name or system
        provider = 'unknown'
        model_name = attributes.get('llm.model_name', attributes.get('gen_ai.request.model', ''))
        system = attributes.get('gen_ai.system', attributes.get('llm.system', ''))
        
        if 'gpt' in model_name.lower() or 'openai' in system.lower():
            provider = 'openai'
        elif 'gemini' in model_name.lower() or 'google' in system.lower():
            provider = 'gemini'
        elif model_name:
            provider = model_name.split('-')[0].split('/')[0]
        elif system:
            provider = system
        
        return instrumentor, provider
    
    def extract_operation(self, span: Dict[str, Any]) -> str:
        """Extract operation type from span."""
        attributes = span.get('attributes', {})
        span_name = span.get('name', '').lower()
        instrumentation = span.get('instrumentation_info', {})
        scope_name = instrumentation.get('name', '').lower()
        
        # Check OpenInference span kind first
        if attributes.get('openinference.span.kind') == 'LLM':
            return 'chat'
        elif attributes.get('openinference.span.kind') == 'CHAIN':
            return 'chain'
        elif attributes.get('openinference.span.kind') == 'AGENT':
            return 'agent'
        elif attributes.get('openinference.span.kind') == 'TOOL':
            return 'tool'
        
        # Framework-specific operation detection
        # AutoGen operations
        if 'autogen' in scope_name:
            if 'run' in span_name:
                return 'run'
            elif 'on_messages' in span_name:
                return 'on_messages'
            elif 'handle_' in span_name:
                return span_name.replace('handle_', '')
        
        # Semantic Kernel operations
        if 'semantic_kernel' in scope_name:
            if 'kernel_function' in scope_name:
                # Extract function name from attributes or span name
                func_name = attributes.get('function.name', span_name.split('.')[-1])
                return f'function_{func_name}'.replace(' ', '_').lower()
            elif 'chat_completion' in scope_name:
                return 'chat_completion'
            elif 'runtime' in scope_name:
                return 'runtime_execution'
        
        # Infer from gen_ai operation name
        operation = attributes.get('gen_ai.operation.name', '')
        if operation:
            return operation.lower().replace(' ', '_')
        
        # Infer from span name patterns
        if 'chat' in span_name:
            return 'chat'
        elif 'completion' in span_name:
            return 'completion'
        elif 'agent' in span_name:
            return 'agent'
        elif 'tool' in span_name or 'function' in span_name:
            return 'tool'
        elif 'run' in span_name:
            return 'run'
        
        # Use the span name as operation if nothing else works
        # Clean it up to be a valid filename
        if span_name:
            clean_name = span_name.replace('.', '_').replace(' ', '_').replace('/', '_').lower()
            # Take last part if it has multiple segments
            parts = clean_name.split('_')
            return '_'.join(parts[-2:]) if len(parts) > 2 else clean_name
        
        return 'unknown'
    
    def map_to_expected_structure(self, span: Dict[str, Any]) -> Dict[str, Any]:
        """Map span attributes to expected HoneyHive event structure."""
        attributes = span.get('attributes', {})
        
        expected = {
            'inputs': {},
            'outputs': {},
            'config': {},
            'metrics': {},
            'metadata': {},
            'session_id': attributes.get('traceloop.association.properties.session_id')
        }
        
        # Extract inputs (prompts/messages)
        chat_history = []
        
        # Try different input formats
        if 'gen_ai.prompt' in attributes:
            expected['inputs']['chat_history'] = attributes['gen_ai.prompt']
        elif 'gen_ai.input.messages' in attributes:
            expected['inputs']['messages'] = attributes['gen_ai.input.messages']
        else:
            # Collect individual input messages
            i = 0
            while f'llm.input_messages.{i}.message.role' in attributes:
                msg = {
                    'role': attributes.get(f'llm.input_messages.{i}.message.role'),
                    'content': attributes.get(f'llm.input_messages.{i}.message.content', '')
                }
                chat_history.append(msg)
                i += 1
            
            if chat_history:
                expected['inputs']['chat_history'] = chat_history
        
        # Try parsing input.value if it's a JSON string
        if not expected['inputs'] and 'input.value' in attributes:
            try:
                parsed = json.loads(attributes['input.value'])
                if isinstance(parsed, dict):
                    if 'messages' in parsed:
                        expected['inputs']['chat_history'] = parsed['messages']
                    else:
                        expected['inputs'] = parsed
            except:
                pass
        
        # Extract outputs (completions/responses)
        if 'gen_ai.completion' in attributes:
            completion = attributes['gen_ai.completion']
            if isinstance(completion, list) and len(completion) > 0:
                expected['outputs']['message'] = completion[0].get('content', '')
            else:
                expected['outputs']['completion'] = completion
        elif 'gen_ai.output.messages' in attributes:
            expected['outputs']['messages'] = attributes['gen_ai.output.messages']
        elif 'llm.output_messages.0.message.content' in attributes:
            expected['outputs']['message'] = attributes['llm.output_messages.0.message.content']
        
        # Try parsing output.value if it's a JSON string
        if not expected['outputs'] and 'output.value' in attributes:
            try:
                parsed = json.loads(attributes['output.value'])
                if isinstance(parsed, dict):
                    if 'content' in parsed:
                        if isinstance(parsed['content'], list) and len(parsed['content']) > 0:
                            expected['outputs']['message'] = parsed['content'][0].get('text', '')
                    else:
                        expected['outputs'] = parsed
                elif isinstance(parsed, str):
                    expected['outputs']['message'] = parsed
            except:
                pass
        
        # Extract config (model parameters)
        config_mappings = {
            'gen_ai.request.model': 'model',
            'llm.model_name': 'model',
            'gen_ai.request.max_tokens': 'max_tokens',
            'gen_ai.request.temperature': 'temperature',
            'gen_ai.request.top_p': 'top_p',
            'gen_ai.request.frequency_penalty': 'frequency_penalty',
            'gen_ai.request.presence_penalty': 'presence_penalty',
        }
        
        for otel_key, config_key in config_mappings.items():
            if otel_key in attributes:
                expected['config'][config_key] = attributes[otel_key]
        
        # Parse llm.invocation_parameters if present
        if 'llm.invocation_parameters' in attributes:
            try:
                params = json.loads(attributes['llm.invocation_parameters'])
                for k, v in params.items():
                    if k not in expected['config']:
                        expected['config'][k] = v
            except:
                pass
        
        # Extract metrics (token counts)
        metrics_mappings = {
            'gen_ai.usage.prompt_tokens': 'prompt_tokens',
            'gen_ai.usage.completion_tokens': 'completion_tokens',
            'gen_ai.usage.cache_read_input_tokens': 'cache_read_input_tokens',
            'gen_ai.usage.reasoning_tokens': 'reasoning_tokens',
            'llm.token_count.prompt': 'prompt_tokens',
            'llm.token_count.completion': 'completion_tokens',
            'llm.token_count.total': 'total_tokens',
        }
        
        for otel_key, metric_key in metrics_mappings.items():
            if otel_key in attributes:
                value = attributes[otel_key]
                expected['metrics'][metric_key] = value
                expected['metadata'][metric_key] = value
        
        # Calculate total tokens if not present
        if 'total_tokens' not in expected['metrics'] and 'prompt_tokens' in expected['metrics'] and 'completion_tokens' in expected['metrics']:
            expected['metrics']['total_tokens'] = expected['metrics']['prompt_tokens'] + expected['metrics']['completion_tokens']
            expected['metadata']['total_tokens'] = expected['metrics']['total_tokens']
        
        # Extract metadata (system info, response details)
        metadata_mappings = {
            'gen_ai.system': 'system',
            'llm.system': 'system',
            'llm.provider': 'provider',
            'gen_ai.response.model': 'response_model',
            'gen_ai.response.id': 'response_id',
            'gen_ai.response.finish_reasons': 'finish_reasons',
            'llm.request.type': 'request_type',
            'llm.is_streaming': 'is_streaming',
            'gen_ai.openai.api_base': 'openai_api_base',
            'traceloop.span.kind': 'span_kind',
            'openinference.span.kind': 'span_kind',
            'gen_ai.operation.name': 'operation_name',
        }
        
        for otel_key, metadata_key in metadata_mappings.items():
            if otel_key in attributes:
                expected['metadata'][metadata_key] = attributes[otel_key]
        
        # Add event type
        event_type = 'model' if attributes.get('openinference.span.kind') == 'LLM' else 'tool'
        expected['metadata']['event_type'] = event_type
        
        return expected
    
    def generate_test_case_schema(self, test_case: Dict[str, Any]) -> str:
        """Generate a schema hash for deduplication based on attribute keys.
        
        We want 1 test case per unique operation name + attribute key fingerprint.
        """
        attributes = test_case['input']['attributes']
        expected = test_case['expected']
        scope_name = test_case['input']['scopeName']
        event_type = test_case['input']['eventType']
        
        # Extract operation name to ensure each operation gets its own test case
        operation_name = attributes.get('gen_ai.operation.name', 'unknown')
        
        # Create a schema representation based on operation + attribute keys
        schema = {
            'scope': scope_name,
            'event_type': event_type,
            'operation': operation_name,  # Include operation name in deduplication
            'attribute_keys': sorted(attributes.keys()),
            'inputs_keys': sorted(expected['inputs'].keys()),
            'outputs_keys': sorted(expected['outputs'].keys()),
            'config_keys': sorted(expected['config'].keys()),
            'metrics_keys': sorted(expected['metrics'].keys()),
        }
        return json.dumps(schema, sort_keys=True)
    
    def create_test_case(self, span: Dict[str, Any], integration_name: str) -> Dict[str, Any]:
        """Create a test case from a span."""
        attributes = span.get('attributes', {})
        instrumentation = span.get('instrumentation_info', {})
        
        # Extract components for naming
        instrumentor, provider = self.extract_instrumentor_provider(span, integration_name)
        operation = self.extract_operation(span)
        
        # Map to expected structure
        expected = self.map_to_expected_structure(span)
        
        # Determine event type based on span kind
        span_kind = attributes.get('openinference.span.kind', '')
        if span_kind == 'LLM':
            event_type = 'model'
        elif span_kind == 'TOOL':
            event_type = 'tool'
        elif span_kind == 'AGENT':
            event_type = 'agent'
        elif span_kind == 'CHAIN':
            event_type = 'chain'
        else:
            # For framework-specific spans without OpenInference kind
            scope_name = instrumentation.get('name', '').lower()
            if 'function' in scope_name or 'tool' in scope_name:
                event_type = 'tool'
            elif 'agent' in scope_name or 'runtime' in scope_name:
                event_type = 'agent'
            elif 'connector' in scope_name or 'completion' in scope_name:
                event_type = 'model'
            else:
                event_type = 'tool'  # Default
        
        # Create test case
        test_case = {
            'name': f"{instrumentor.title().replace('_', ' ')} {provider.title()} {operation.title().replace('_', ' ')}",
            'input': {
                'attributes': attributes,
                'scopeName': instrumentation.get('name', ''),
                'eventType': event_type
            },
            'expected': expected
        }
        
        return test_case, instrumentor, provider, operation
    
    def save_test_case(self, test_case: Dict[str, Any], instrumentor: str, provider: str, operation: str):
        """Save test case to file."""
        # Generate schema hash for deduplication (based on attribute keys)
        schema_hash = self.generate_test_case_schema(test_case)
        
        # Skip if we've seen this schema before
        if schema_hash in self.seen_schemas:
            return False
        
        self.seen_schemas.add(schema_hash)
        
        # Generate filename
        base_name = f"{instrumentor}_{provider}_{operation}"
        self.test_case_count[base_name] += 1
        count = self.test_case_count[base_name]
        filename = f"{base_name}_{count:03d}.json"
        
        # Save to file
        output_path = self.output_dir / filename
        with open(output_path, 'w') as f:
            json.dump(test_case, f, indent=2, default=str)
        
        print(f"  ✅ Created {filename}")
        return True
    
    def process_span_dump(self, dump: Dict[str, Any]):
        """Process a single span dump file."""
        file_name = dump['file']
        data = dump['data']
        
        # Extract integration name from filename (handle multi-word names)
        # Examples: semantic_kernel_20251020_030347.json -> semantic_kernel
        #          autogen_20251020_030511.json -> autogen
        #          google_adk_20251020_030431.json -> google_adk
        base_name = file_name.replace('.json', '')
        parts = base_name.split('_')
        
        # Integration name is everything before the timestamp (YYYYMMDD)
        integration_parts = []
        for part in parts:
            if part.isdigit() and len(part) == 8:  # Found timestamp
                break
            integration_parts.append(part)
        
        integration_name = '_'.join(integration_parts) if integration_parts else parts[0]
        
        print(f"\n🔄 Processing {file_name} ({data['total_spans']} spans)...")
        
        spans = data.get('spans', [])
        created_count = 0
        
        for span in spans:
            # Skip honeyhive decorator spans (those are our test function wrappers)
            instrumentation = span.get('instrumentation_info', {})
            if 'honeyhive' in instrumentation.get('name', '').lower():
                continue
            
            # Create test case for ALL span types (not just LLM)
            # We want to capture all unique JSON key fingerprints
            try:
                test_case, instrumentor, provider, operation = self.create_test_case(span, integration_name)
                
                # Save all unique span fingerprints
                if self.save_test_case(test_case, instrumentor, provider, operation):
                    created_count += 1
            except Exception as e:
                print(f"  ⚠️  Error processing span '{span.get('name', 'unknown')}': {e}")
        
        print(f"  ✅ Created {created_count} unique test cases")
    
    def generate(self):
        """Generate all test cases."""
        print("🚀 Converting span dumps to test cases...")
        print("=" * 60)
        
        # Load span dumps
        span_dumps = self.load_span_dumps()
        
        if not span_dumps:
            print(f"❌ No span dumps found in {self.span_dumps_dir}")
            return
        
        # Process each dump
        for dump in span_dumps:
            self.process_span_dump(dump)
        
        # Summary
        print("\n" + "=" * 60)
        print(f"✅ Test case generation complete!")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📊 Total unique test cases: {len(self.seen_schemas)}")
        print("\nTest cases by provider:")
        for base_name, count in sorted(self.test_case_count.items()):
            print(f"  • {base_name}: {count}")


def main():
    """Main entry point."""
    generator = TestCaseGenerator()
    generator.generate()


if __name__ == "__main__":
    main()

