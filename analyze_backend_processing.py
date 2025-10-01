#!/usr/bin/env python3
"""
Analyze why our spans might be getting dropped by the backend.
Compare our span attributes with backend processing logic.
"""

import os
import sys
import json

def analyze_backend_processing():
    """Analyze backend processing logic vs our span attributes."""
    
    print("🔍 Analyzing backend processing logic vs our span attributes...")
    
    # Our test span attributes from verbose logging
    our_span_attributes = {
        "honeyhive.session_id": "4dc9365e-937e-4109-ae0e-ce0cb4ade94a",
        "test.type": "verbose-debug",
        "test.description": "Testing OTLP export with verbose logging",
        "honeyhive_event_type": "tool",
        "honeyhive_inputs.query": "Test query for verbose debugging",
        "honeyhive_outputs.result": "Test result from verbose debug span",
        "honeyhive_config.debug_mode": "true"
    }
    
    print(f"📊 Our span attributes:")
    for key, value in our_span_attributes.items():
        print(f"   {key}: {value}")
    
    print(f"\n🔍 Backend processing analysis:")
    
    # Check session_id extraction (lines 93-94 in backend)
    session_id_found = False
    session_id_sources = [
        "traceloop.association.properties.session_id",
        "honeyhive.session_id"  # Our attribute
    ]
    
    print(f"\n1. 🔍 SESSION ID EXTRACTION:")
    for source in session_id_sources:
        if source in our_span_attributes:
            print(f"   ✅ Found session_id in: {source} = {our_span_attributes[source]}")
            session_id_found = True
        else:
            print(f"   ❌ Not found: {source}")
    
    if not session_id_found:
        print(f"   🚨 CRITICAL: No session_id found! Backend requires session_id to process spans.")
        print(f"   💡 Backend checks: traceloop.association.properties.session_id")
        print(f"   💡 We use: honeyhive.session_id")
        print(f"   🔧 FIX: We need to set 'traceloop.association.properties.session_id' attribute")
        return
    
    # Check project extraction (lines 95-96)
    project_found = False
    project_sources = [
        "traceloop.association.properties.project",
        "honeyhive.project"  # Our potential attribute
    ]
    
    print(f"\n2. 🔍 PROJECT EXTRACTION:")
    for source in project_sources:
        if source in our_span_attributes:
            print(f"   ✅ Found project in: {source} = {our_span_attributes[source]}")
            project_found = True
        else:
            print(f"   ❌ Not found: {source}")
    
    if not project_found:
        print(f"   ⚠️  No project found in span attributes")
        print(f"   💡 Backend checks: traceloop.association.properties.project")
        print(f"   🔧 FIX: We need to set 'traceloop.association.properties.project' attribute")
    
    # Check source extraction (lines 97-98)
    source_found = False
    source_sources = [
        "traceloop.association.properties.source",
        "honeyhive.source"  # Our potential attribute
    ]
    
    print(f"\n3. 🔍 SOURCE EXTRACTION:")
    for source in source_sources:
        if source in our_span_attributes:
            print(f"   ✅ Found source in: {source} = {our_span_attributes[source]}")
            source_found = True
        else:
            print(f"   ❌ Not found: {source}")
    
    if not source_found:
        print(f"   ⚠️  No source found in span attributes")
        print(f"   💡 Backend checks: traceloop.association.properties.source")
        print(f"   🔧 FIX: We need to set 'traceloop.association.properties.source' attribute")
    
    # Check event type determination (lines 66-74)
    print(f"\n4. 🔍 EVENT TYPE DETERMINATION:")
    event_type = None
    
    if "honeyhive_event_type" in our_span_attributes:
        event_type = our_span_attributes["honeyhive_event_type"]
        print(f"   ✅ honeyhive_event_type: {event_type}")
    elif "llm.request.type" in our_span_attributes:
        event_type = "model"
        print(f"   ✅ llm.request.type found -> event_type: model")
    else:
        event_type = "tool"
        print(f"   ✅ Default event_type: tool")
    
    # Check critical condition (line 294)
    print(f"\n5. 🚨 CRITICAL CONDITION CHECK (line 294):")
    print(f"   Backend condition: if (session_id && !skipEvent)")
    
    session_id_check = session_id_found
    skip_event_check = True  # Assume not skipped unless specific conditions
    
    print(f"   session_id check: {session_id_check}")
    print(f"   !skipEvent check: {skip_event_check}")
    
    if session_id_check and skip_event_check:
        print(f"   ✅ SPAN SHOULD BE PROCESSED")
    else:
        print(f"   ❌ SPAN WILL BE DROPPED!")
        if not session_id_check:
            print(f"      Reason: No session_id found")
        if not skip_event_check:
            print(f"      Reason: skipEvent is true")
    
    # Check inputs/outputs processing
    print(f"\n6. 🔍 INPUTS/OUTPUTS PROCESSING:")
    honeyhive_inputs = [k for k in our_span_attributes.keys() if k.startswith("honeyhive_inputs")]
    honeyhive_outputs = [k for k in our_span_attributes.keys() if k.startswith("honeyhive_outputs")]
    honeyhive_config = [k for k in our_span_attributes.keys() if k.startswith("honeyhive_config")]
    
    print(f"   honeyhive_inputs attributes: {len(honeyhive_inputs)}")
    for attr in honeyhive_inputs:
        print(f"      {attr}: {our_span_attributes[attr]}")
    
    print(f"   honeyhive_outputs attributes: {len(honeyhive_outputs)}")
    for attr in honeyhive_outputs:
        print(f"      {attr}: {our_span_attributes[attr]}")
    
    print(f"   honeyhive_config attributes: {len(honeyhive_config)}")
    for attr in honeyhive_config:
        print(f"      {attr}: {our_span_attributes[attr]}")
    
    # Summary and recommendations
    print(f"\n🎯 ANALYSIS SUMMARY:")
    
    issues_found = []
    fixes_needed = []
    
    if not session_id_found:
        issues_found.append("Missing session_id attribute")
        fixes_needed.append("Add 'traceloop.association.properties.session_id' attribute")
    
    if not project_found:
        issues_found.append("Missing project attribute")
        fixes_needed.append("Add 'traceloop.association.properties.project' attribute")
    
    if not source_found:
        issues_found.append("Missing source attribute")
        fixes_needed.append("Add 'traceloop.association.properties.source' attribute")
    
    if issues_found:
        print(f"❌ ISSUES FOUND:")
        for issue in issues_found:
            print(f"   - {issue}")
        
        print(f"\n🔧 FIXES NEEDED:")
        for fix in fixes_needed:
            print(f"   - {fix}")
        
        print(f"\n💡 ROOT CAUSE:")
        print(f"   Our spans use 'honeyhive.*' attributes, but backend expects 'traceloop.association.properties.*'")
        print(f"   The backend was designed for Traceloop format, not our custom format.")
        
        print(f"\n🚀 SOLUTION:")
        print(f"   Update span processor to add Traceloop-compatible attributes:")
        print(f"   - traceloop.association.properties.session_id")
        print(f"   - traceloop.association.properties.project") 
        print(f"   - traceloop.association.properties.source")
        
    else:
        print(f"✅ All required attributes found - spans should be processed correctly")
    
    print(f"\n🔍 Next step: Check if spans have the required Traceloop attributes")

if __name__ == "__main__":
    analyze_backend_processing()
