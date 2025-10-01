#!/usr/bin/env python3
"""
Inspect the actual methods available on the HoneyHive client.
"""

import os

def inspect_client():
    """Inspect HoneyHive client methods."""
    
    print("🔍 Inspecting actual HoneyHive client methods...")
    
    try:
        from honeyhive import HoneyHive
        
        # Initialize client
        client = HoneyHive(api_key="dummy-key", test_mode=True)
        
        print(f"✅ HoneyHive client initialized")
        print(f"   Type: {type(client)}")
        
        # Get all attributes and methods
        print(f"\n📋 Available attributes and methods:")
        
        all_attrs = dir(client)
        public_attrs = [attr for attr in all_attrs if not attr.startswith('_')]
        
        for attr in sorted(public_attrs):
            attr_obj = getattr(client, attr)
            attr_type = type(attr_obj).__name__
            
            if callable(attr_obj):
                print(f"   🔧 {attr}() - {attr_type}")
            else:
                print(f"   📦 {attr} - {attr_type}")
        
        # Check specific API modules
        print(f"\n📊 API Modules:")
        api_modules = ['sessions', 'events', 'tools', 'datapoints', 'datasets', 
                      'configurations', 'projects', 'metrics', 'evaluations']
        
        for module_name in api_modules:
            if hasattr(client, module_name):
                module = getattr(client, module_name)
                print(f"   ✅ {module_name}: {type(module).__name__}")
                
                # Get methods of this module
                module_methods = [method for method in dir(module) if not method.startswith('_') and callable(getattr(module, method))]
                for method in sorted(module_methods):
                    print(f"      🔧 {method}()")
            else:
                print(f"   ❌ {module_name}: Not found")
        
        # Test specific methods we need
        print(f"\n🧪 Testing specific methods:")
        
        # Test events API
        if hasattr(client, 'events'):
            events_api = client.events
            print(f"   Events API: {type(events_api).__name__}")
            
            # Check for list_events method
            if hasattr(events_api, 'list_events'):
                print(f"   ✅ events.list_events() exists")
            else:
                print(f"   ❌ events.list_events() not found")
                
                # Show what methods are available
                events_methods = [m for m in dir(events_api) if not m.startswith('_') and callable(getattr(events_api, m))]
                print(f"   Available events methods: {events_methods}")
        
        # Test sessions API
        if hasattr(client, 'sessions'):
            sessions_api = client.sessions
            print(f"   Sessions API: {type(sessions_api).__name__}")
            
            # Check for list_sessions method
            if hasattr(sessions_api, 'list_sessions'):
                print(f"   ✅ sessions.list_sessions() exists")
            else:
                print(f"   ❌ sessions.list_sessions() not found")
                
                # Show what methods are available
                sessions_methods = [m for m in dir(sessions_api) if not m.startswith('_') and callable(getattr(sessions_api, m))]
                print(f"   Available sessions methods: {sessions_methods}")
                
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_client()
