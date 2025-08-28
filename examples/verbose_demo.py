#!/usr/bin/env python3
"""Simple demonstration of HoneyHive verbose logging functionality."""

import os
import sys
from honeyhive import HoneyHive

def main():
    """Demonstrate verbose logging functionality."""
    print("HoneyHive Verbose Logging Demo")
    print("=" * 40)
    
    # Method 1: Enable verbose mode via constructor
    print("\n1. Enabling verbose mode via constructor...")
    client = HoneyHive(
        api_key="demo-api-key",  # This will fail, but we'll see the verbose logs
        verbose=True
    )
    
    print(f"✓ Client created with verbose={client.verbose}")
    
    # Method 2: Enable verbose mode via environment variable
    print("\n2. Enabling verbose mode via environment variable...")
    os.environ["HH_VERBOSE"] = "true"
    
    # Reload config to pick up environment variable
    from honeyhive.utils.config import config
    config.reload()
    
    print(f"✓ Environment variable HH_VERBOSE set to: {os.environ.get('HH_VERBOSE')}")
    print(f"✓ Config verbose flag: {config.verbose}")
    
    # Method 3: Show what verbose logging provides
    print("\n3. What verbose logging provides:")
    print("   • Detailed request information (method, URL, headers, body)")
    print("   • Response details (status code, headers, timing)")
    print("   • Error information (error type, message, context)")
    print("   • Retry attempts and delays")
    print("   • All API call metadata")
    
    # Method 4: Show environment variable alternatives
    print("\n4. Environment variable alternatives:")
    print("   export HH_VERBOSE=true")
    print("   export HH_DEBUG_MODE=true")
    print("   export HH_API_KEY=your-api-key")
    print("   export HH_PROJECT=your-project")
    
    print("\n5. Usage in code:")
    print("   # Option A: Constructor parameter")
    print("   client = HoneyHive(api_key='key', verbose=True)")
    print("   ")
    print("   # Option B: Environment variable")
    print("   client = HoneyHive()  # Automatically uses verbose mode")
    
    print("\n✓ Demo completed! Check the logs above for verbose output.")
    print("  When you make actual API calls with verbose=True, you'll see")
    print("  detailed request/response information for debugging.")


if __name__ == "__main__":
    main()
