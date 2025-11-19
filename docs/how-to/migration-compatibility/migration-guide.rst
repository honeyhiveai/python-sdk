=========================================
Migration Guide: v0.1.0+ Architecture
=========================================

.. meta::
   :description: Complete migration guide for upgrading to HoneyHive SDK v0.1.0+ with new modular architecture and hybrid configuration
   :keywords: migration guide, upgrade, v0.1.0, modular architecture, hybrid configuration

Overview
========

This guide helps you migrate from earlier versions of the HoneyHive SDK to v0.1.0+, which introduces a completely rewritten modular architecture and hybrid configuration system.

.. contents:: Table of Contents
   :local:
   :depth: 3

What's New in v0.1.0+
=====================

Major Changes
-------------

1. **🏗️ Modular Tracer Architecture**: Complete rewrite with 35 files across 6 modules
2. **🔧 Hybrid Configuration System**: New Pydantic config objects alongside traditional parameters
3. **🎯 Enhanced Multi-Instance Support**: True multi-instance architecture with independent configurations
4. **🛡️ Improved Error Handling**: Graceful degradation throughout the system
5. **📊 Better Performance**: Optimized connection pooling, caching, and batch processing

.. important::
   **100% Backwards Compatibility Guaranteed**
   
   All existing code continues to work unchanged. This is a **non-breaking upgrade** with enhanced capabilities.

Migration Strategies
====================

Strategy 1: No Migration Required (Recommended)
-----------------------------------------------

**Best for**: Existing applications that work well with current patterns.

**Action**: Simply upgrade to v0.1.0+ - no code changes needed.

.. code-block:: bash

   pip install --upgrade honeyhive

Your existing code continues to work exactly as before:

.. code-block:: python

   # This code works identically in v0.1.0+
   from honeyhive import HoneyHiveTracer, trace
   
   tracer = HoneyHiveTracer.init(
       api_key="hh_1234567890abcdef",
       project="my-project",
       verbose=True
   )
   
   @trace(tracer=tracer)
   def my_function():
       return "Hello, World!"

Strategy 2: Gradual Migration (Recommended for New Features)
------------------------------------------------------------

**Best for**: Applications wanting to adopt new features gradually.

**Action**: Keep existing code, use new patterns for new features.

.. code-block:: python

   # Existing tracer (keep as-is)
   legacy_tracer = HoneyHiveTracer.init(
       api_key="hh_1234567890abcdef",
       project="legacy-project"
   )
   
   # New tracer with modern config (for new features)
   from honeyhive.config.models import TracerConfig
   
   config = TracerConfig(
       api_key="hh_1234567890abcdef",
       project="new-features",
       verbose=True,
       cache_enabled=True
   )
   modern_tracer = HoneyHiveTracer(config=config)

Strategy 3: Full Migration (For Maximum Benefits)
-------------------------------------------------

**Best for**: Applications wanting all new features and enhanced type safety.

**Action**: Migrate to new configuration patterns systematically.

See the detailed migration steps below.

Detailed Migration Steps
========================

Step 1: Update Dependencies
---------------------------

Update to the latest version:

.. code-block:: bash

   pip install --upgrade honeyhive>=0.1.0

Verify the upgrade:

.. code-block:: python

   import honeyhive
   print(f"HoneyHive SDK version: {honeyhive.__version__}")
   # Should show 0.1.0 or higher

Step 2: Assess Current Usage
----------------------------

Identify your current usage patterns:

**Pattern A: Basic Tracer Initialization**

.. code-block:: python

   # Current code (works unchanged)
   tracer = HoneyHiveTracer.init(
       api_key="hh_key",
       project="my-project",
       verbose=True
   )

**Pattern B: Environment Variable Usage**

.. code-block:: python

   # Current code (works unchanged)
   import os
   os.environ["HH_API_KEY"] = "hh_key"
   os.environ["HH_PROJECT"] = "my-project"
   
   tracer = HoneyHiveTracer.init()

**Pattern C: Multiple Tracer Instances**

.. code-block:: python

   # Current code (works unchanged)
   prod_tracer = HoneyHiveTracer.init(api_key="prod_key", project="prod")
   dev_tracer = HoneyHiveTracer.init(api_key="dev_key", project="dev")

Step 3: Choose Migration Approach (Optional)
--------------------------------------------

If you want to adopt the new patterns, choose based on your needs:

**Option A: Keep Traditional .init() Method**

.. code-block:: python

   # Recommended for existing applications
   tracer = HoneyHiveTracer.init(
       api_key="hh_1234567890abcdef",
       project="my-project",
       verbose=True,
       cache_enabled=True  # New feature available
   )

**Option B: Adopt Modern Config Objects**

.. code-block:: python

   # Recommended for new applications or enhanced type safety
   from honeyhive.config.models import TracerConfig
   
   config = TracerConfig(
       api_key="hh_1234567890abcdef",
       project="my-project",
       verbose=True,
       cache_enabled=True,
       cache_max_size=5000
   )
   
   tracer = HoneyHiveTracer(config=config)

**Option C: Mixed Approach**

.. code-block:: python

   # Use config for base settings, parameters for overrides
   from honeyhive.config.models import TracerConfig
   
   base_config = TracerConfig(
       api_key="hh_1234567890abcdef",
       project="my-project"
   )
   
   # Different tracers with selective overrides
   verbose_tracer = HoneyHiveTracer(config=base_config, verbose=True)
   quiet_tracer = HoneyHiveTracer(config=base_config, verbose=False)

Step 4: Update Advanced Usage (Optional)
----------------------------------------

If you use advanced patterns, consider these enhancements:

**Multi-Instance Management**

.. code-block:: python

   # Before: Manual management
   tracers = {}
   tracers["prod"] = HoneyHiveTracer.init(api_key="prod_key", project="prod")
   tracers["dev"] = HoneyHiveTracer.init(api_key="dev_key", project="dev")
   
   # After: Enhanced with config objects (optional)
   from honeyhive.config.models import TracerConfig
   
   configs = {
       "prod": TracerConfig(api_key="prod_key", project="prod", verbose=False),
       "dev": TracerConfig(api_key="dev_key", project="dev", verbose=True)
   }
   
   tracers = {
       env: HoneyHiveTracer(config=config)
       for env, config in configs.items()
   }

**Environment-Based Configuration**

.. code-block:: python

   # Before: Manual environment handling
   import os
   
   if os.getenv("ENVIRONMENT") == "production":
       tracer = HoneyHiveTracer.init(
           api_key=os.getenv("PROD_API_KEY"),
           project="prod-app",
           verbose=False
       )
   else:
       tracer = HoneyHiveTracer.init(
           api_key=os.getenv("DEV_API_KEY"),
           project="dev-app",
           verbose=True
       )
   
   # After: Enhanced with validation (optional)
   from honeyhive.config.models import TracerConfig
   
   def create_tracer_for_environment():
       env = os.getenv("ENVIRONMENT", "development")
       
       if env == "production":
           config = TracerConfig(
               api_key=os.getenv("PROD_API_KEY"),
               project="prod-app",
               verbose=False,
               cache_enabled=True,
               cache_max_size=10000
           )
       else:
           config = TracerConfig(
               api_key=os.getenv("DEV_API_KEY"),
               project="dev-app",
               verbose=True,
               test_mode=True  # Don't send data in dev
           )
       
       return HoneyHiveTracer(config=config)
   
   tracer = create_tracer_for_environment()

Step 5: Test Your Migration
---------------------------

Verify everything works correctly:

.. code-block:: python

   # Test basic functionality
   @tracer.trace
   def test_function():
       return "Migration successful!"
   
   result = test_function()
   print(f"Test result: {result}")
   
   # Test tracer properties
   print(f"Project: {tracer.project_name}")
   print(f"Source: {tracer.source_environment}")
   print(f"Initialized: {tracer.is_initialized}")

Common Migration Scenarios
==========================

Scenario 1: Simple Application
------------------------------

**Before (works unchanged):**

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   
   tracer = HoneyHiveTracer.init(
       api_key="hh_1234567890abcdef",
       project="simple-app"
   )
   
   @trace(tracer=tracer)
   def process_data(data):
       return data.upper()

**After (optional enhancement):**

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   from honeyhive.config.models import TracerConfig
   
   # Option 1: Keep traditional approach (recommended)
   tracer = HoneyHiveTracer.init(
       api_key="hh_1234567890abcdef",
       project="simple-app",
       cache_enabled=True  # New feature
   )
   
   # Option 2: Modern config approach (optional)
   config = TracerConfig(
       api_key="hh_1234567890abcdef",
       project="simple-app",
       cache_enabled=True,
       verbose=True
   )
   tracer = HoneyHiveTracer(config=config)
   
   @trace(tracer=tracer)
   def process_data(data):
       return data.upper()

Scenario 2: Multi-Environment Application
-----------------------------------------

**Before (works unchanged):**

.. code-block:: python

   import os
   from honeyhive import HoneyHiveTracer
   
   # Environment-based initialization
   api_key = os.getenv("HH_API_KEY")
   project = os.getenv("HH_PROJECT")
   
   tracer = HoneyHiveTracer.init(
       api_key=api_key,
       project=project,
       verbose=os.getenv("DEBUG") == "true"
   )

**After (optional enhancement):**

.. code-block:: python

   import os
   from honeyhive import HoneyHiveTracer
   from honeyhive.config.models import TracerConfig
   
   # Option 1: Enhanced traditional approach
   tracer = HoneyHiveTracer.init(
       api_key=os.getenv("HH_API_KEY"),
       project=os.getenv("HH_PROJECT"),
       verbose=os.getenv("DEBUG") == "true",
       cache_enabled=os.getenv("CACHE_ENABLED", "true") == "true"
   )
   
   # Option 2: Modern config with environment loading
   config = TracerConfig()  # Automatically loads from HH_* env vars
   tracer = HoneyHiveTracer(config=config)

Scenario 3: LLM Integration Application
---------------------------------------

**Before (works unchanged):**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from openinference.instrumentation.openai import OpenAIInstrumentor
   
   # Initialize tracer
   tracer = HoneyHiveTracer.init(
       api_key="hh_1234567890abcdef",
       project="llm-app"
   )
   
   # Initialize instrumentor
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

**After (optional enhancement):**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   from honeyhive.config.models import TracerConfig
   from openinference.instrumentation.openai import OpenAIInstrumentor
   
   # Option 1: Keep traditional approach (recommended)
   tracer = HoneyHiveTracer.init(
       api_key="hh_1234567890abcdef",
       project="llm-app",
       cache_enabled=True,  # Cache LLM responses
       cache_max_size=1000
   )
   
   # Option 2: Modern config approach (optional)
   config = TracerConfig(
       api_key="hh_1234567890abcdef",
       project="llm-app",
       cache_enabled=True,
       cache_max_size=1000,
       verbose=True
   )
   tracer = HoneyHiveTracer(config=config)
   
   # Instrumentor setup (unchanged)
   instrumentor = OpenAIInstrumentor()
   instrumentor.instrument(tracer_provider=tracer.provider)

New Features Available
======================

Enhanced Configuration Options
------------------------------

New configuration options available in v0.1.0+:

.. code-block:: python

   # Available in both .init() and config objects
   tracer = HoneyHiveTracer.init(
       api_key="hh_1234567890abcdef",
       project="my-project",
       
       # Caching options (new)
       cache_enabled=True,
       cache_max_size=5000,
       cache_ttl=3600,
       cache_cleanup_interval=300,
       
       # Enhanced control (new)
       disable_tracing=False,  # Emergency override
       test_mode=False,        # Don't send data to backend
       
       # Existing options (enhanced)
       verbose=True,
       disable_http_tracing=True,
       disable_batch=False
   )

Multi-Instance Architecture
---------------------------

Enhanced support for multiple independent tracers:

.. code-block:: python

   # Each tracer is completely independent
   data_tracer = HoneyHiveTracer.init(
       api_key="hh_data_key",
       project="data-pipeline",
       cache_enabled=True,
       cache_max_size=10000
   )
   
   llm_tracer = HoneyHiveTracer.init(
       api_key="hh_llm_key",
       project="llm-inference",
       verbose=True,
       cache_enabled=True,
       cache_max_size=5000
   )
   
   # Independent operation
   @data_tracer.trace
   def process_data():
       pass
   
   @llm_tracer.trace
   def generate_response():
       pass

Type Safety and Validation
--------------------------

With modern config objects, get enhanced type safety:

.. code-block:: python

   from honeyhive.config.models import TracerConfig
   
   # Type-safe configuration with validation
   config = TracerConfig(
       api_key="hh_1234567890abcdef",  # Validated format
       project="my-project",           # Required field
       cache_max_size=5000,            # Validated range
       server_url="https://api.honeyhive.ai"  # Validated URL
   )
   
   # IDE autocomplete and type checking
   tracer = HoneyHiveTracer(config=config)

Breaking Changes
================

.. important::
   **No Breaking Changes in v0.1.0+**
   
   This release maintains 100% backwards compatibility. All existing code continues to work unchanged.

**Non-Breaking Enhancements:**

1. **New Configuration Options**: Additional parameters available but not required
2. **Enhanced Error Handling**: Better error messages and graceful degradation
3. **Improved Performance**: Optimizations that don't affect existing APIs
4. **New Import Paths**: Additional import paths available (existing paths still work)

Troubleshooting
===============

Common Issues and Solutions
---------------------------

**Issue 1: Import Errors**

.. code-block:: python

   # If you see import errors for new features
   from honeyhive.config.models import TracerConfig  # New import
   
   # Solution: Make sure you're on v0.1.0+
   # pip install --upgrade honeyhive>=0.1.0

**Issue 2: Configuration Validation Errors**

.. code-block:: python

   # If using config objects and getting validation errors
   from honeyhive.config.models import TracerConfig
   
   try:
       config = TracerConfig(
           api_key="invalid_key",  # Missing 'hh_' prefix
           project="my-project"
       )
   except ValueError as e:
       print(f"Configuration error: {e}")
       
       # Solution: Fix the configuration
       config = TracerConfig(
           api_key="hh_1234567890abcdef",  # Correct format
           project="my-project"
       )

**Issue 3: Performance Differences**

.. code-block:: python

   # If you notice performance changes
   tracer = HoneyHiveTracer.init(
       api_key="hh_1234567890abcdef",
       project="my-project",
       
       # Tune performance settings
       cache_enabled=True,      # Enable caching
       cache_max_size=10000,    # Increase cache size
       disable_batch=False      # Use batching
   )

**Issue 4: Multiple Tracer Conflicts**

.. code-block:: python

   # If multiple tracers interfere with each other
   
   # Each tracer is now completely independent
   tracer1 = HoneyHiveTracer.init(
       api_key="hh_key1",
       project="project1"
   )
   
   tracer2 = HoneyHiveTracer.init(
       api_key="hh_key2", 
       project="project2"
   )
   
   # No conflicts - each has independent state

Getting Help
============

If you encounter issues during migration:

1. **Check the Documentation**:
   
   - :doc:`../../reference/configuration/hybrid-config-approach` - Configuration guide
   - :doc:`../../reference/api/config-models` - Configuration API reference
   - :doc:`../../reference/api/tracer-architecture` - Architecture overview

2. **Review Examples**:
   
   - Check ``examples/basic_usage.py`` for updated patterns
   - Review ``examples/integrations/`` for LLM integration examples

3. **Test Incrementally**:
   
   - Start with no changes (backwards compatibility)
   - Add new features gradually
   - Test each change thoroughly

4. **Contact Support**:
   
   - Join our `Discord community <https://discord.gg/honeyhive>`_
   - Email support@honeyhive.ai
   - Create an issue on GitHub

Migration Checklist
===================

Use this checklist to track your migration progress:

**Pre-Migration**

- [ ] Backup your current code
- [ ] Review current HoneyHive usage patterns
- [ ] Test current functionality
- [ ] Plan migration strategy

**Migration**

- [ ] Upgrade to HoneyHive SDK v0.1.0+
- [ ] Verify existing code still works
- [ ] Choose migration approach (none/gradual/full)
- [ ] Update configuration patterns (optional)
- [ ] Add new features as needed (optional)

**Post-Migration**

- [ ] Test all functionality thoroughly
- [ ] Verify tracer initialization
- [ ] Check trace data in HoneyHive dashboard
- [ ] Monitor performance and adjust settings
- [ ] Update team documentation

**Validation**

- [ ] All existing traces still work
- [ ] New features work as expected
- [ ] Performance is acceptable
- [ ] Error handling works correctly
- [ ] Multi-instance setup (if applicable)

Conclusion
==========

The HoneyHive SDK v0.1.0+ provides significant architectural improvements while maintaining complete backwards compatibility. You can:

1. **Upgrade immediately** with no code changes
2. **Adopt new features gradually** as needed
3. **Migrate fully** for maximum benefits

The modular architecture, hybrid configuration system, and enhanced multi-instance support provide a solid foundation for scaling your LLM observability as your applications grow.

**Next Steps:**

- Review the :doc:`../../tutorials/advanced-configuration` tutorial
- Explore the :doc:`../../reference/api/tracer-architecture` documentation
- Try the enhanced examples in ``examples/``

Welcome to HoneyHive SDK v0.1.0+! 🚀