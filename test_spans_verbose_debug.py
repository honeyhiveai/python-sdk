#!/usr/bin/env python3
"""
Test script with verbose debug logging to trace OTLP export pipeline.
"""

import os
import sys
import time
import logging

# Set up detailed logging to see everything
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable all HoneyHive debug logging
os.environ['HH_DEBUG'] = 'true'
os.environ['HH_LOG_LEVEL'] = 'DEBUG'

def test_spans_verbose_debug():
    """Test sending spans with full verbose debug logging."""
    
    print("🔍 Testing spans with VERBOSE DEBUG logging...")
    
    # Check for required environment variables
    api_key = os.getenv('HH_API_KEY')
    if not api_key:
        print("❌ ERROR: HH_API_KEY environment variable not set!")
        sys.exit(1)
    
    project = os.getenv('HH_PROJECT', 'verbose-debug-test')
    
    try:
        from honeyhive import HoneyHiveTracer
        
        print(f"✅ Initializing HoneyHive tracer with VERBOSE=True...")
        print(f"   Project: {project}")
        print(f"   API Key: {api_key[:8]}..." if api_key else "None")
        
        # Initialize tracer with VERBOSE=True for debug logs
        tracer = HoneyHiveTracer.init(
            project=project,
            source="verbose-debug",
            test_mode=False,  # Production mode for real export
            otlp_enabled=True,
            disable_batch=True,  # Immediate export
            verbose=True  # ← ENABLE VERBOSE DEBUG LOGGING
        )
        
        print(f"✅ Tracer initialized with verbose logging!")
        print(f"   Session ID: {tracer.session_id}")
        
        # Create a simple test span with verbose logging
        print(f"\n📝 Creating test span with verbose logging...")
        
        with tracer.start_span("verbose-debug-test-span") as span:
            span.set_attribute("honeyhive.session_id", tracer.session_id)
            span.set_attribute("test.type", "verbose-debug")
            span.set_attribute("test.description", "Testing OTLP export with verbose logging")
            span.set_attribute("honeyhive_event_type", "tool")
            
            # Add some test data
            span.set_attribute("honeyhive_inputs.query", "Test query for verbose debugging")
            span.set_attribute("honeyhive_outputs.result", "Test result from verbose debug span")
            span.set_attribute("honeyhive_config.debug_mode", "true")
            
            print(f"   ✅ Test span created with attributes")
        
        print(f"\n⏳ Waiting for span processing and export...")
        time.sleep(2)  # Give time for processing
        
        print(f"🔄 Force flushing tracer to ensure span export...")
        tracer.provider.force_flush()
        time.sleep(3)  # Give more time for export with verbose logging
        
        print(f"\n🎯 VERBOSE DEBUG TEST COMPLETE!")
        print(f"📊 Summary:")
        print(f"   Project: {project}")
        print(f"   Session ID: {tracer.session_id}")
        print(f"   Test Span: verbose-debug-test-span")
        print(f"   Verbose Logging: ENABLED")
        
        print(f"\n🔍 Check the verbose logs above for:")
        print(f"   1. Span processor on_end calls")
        print(f"   2. OTLP exporter export calls")
        print(f"   3. HTTP requests to HoneyHive backend")
        print(f"   4. Any errors in the export pipeline")
        
        print(f"\n✅ If verbose logs show successful export, check HoneyHive UI:")
        print(f"   - Project: {project}")
        print(f"   - Session: {tracer.session_id}")
        print(f"   - Look for: verbose-debug-test-span")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_spans_verbose_debug()
