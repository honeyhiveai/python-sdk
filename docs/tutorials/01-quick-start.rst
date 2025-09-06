Quick Start: Your First HoneyHive Project
=========================================

.. note::
   **Tutorial Goal**: In 5 minutes, you'll have HoneyHive installed, configured, and tracing your first function.

Welcome! This tutorial will get you up and running with the HoneyHive Python SDK in just a few minutes. By the end, you'll have a working LLM observability setup.

What You'll Build
-----------------

You'll create a simple Python script that:

1. Installs and configures the HoneyHive SDK
2. Traces a simple function with the ``@trace`` decorator
3. Sends trace data to your HoneyHive dashboard

Prerequisites
-------------

- Python 3.11 or higher installed
- A HoneyHive account (free at `honeyhive.ai <https://honeyhive.ai>`_)
- Your HoneyHive API key (found in your dashboard settings)

Step 1: Install HoneyHive
-------------------------

Install the SDK using pip:

.. code-block:: bash

   pip install honeyhive

That's it! The HoneyHive SDK is designed with minimal dependencies to avoid conflicts with your existing setup.

Step 2: Get Your API Key
------------------------

1. Log into your HoneyHive dashboard at `app.honeyhive.ai <https://app.honeyhive.ai>`_
2. Go to **Settings** → **API Keys**
3. Copy your API key (it starts with ``hh_``)

.. important::
   Keep your API key secure! Never commit it to version control.

.. warning::
   **OTLP Tracing Requirement**: You **must** specify a project name when using OTLP tracing due to backend compatibility requirements. Set the ``HH_PROJECT`` environment variable or pass the ``project`` parameter to ``HoneyHiveTracer.init()``.

Step 3: Create Your First Traced Function
-----------------------------------------

Create a new file called ``hello_honeyhive.py``:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   
   # Initialize the tracer with required project parameter
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key-here",  # Replace with your actual API key
       project="My First Project",   # Required for OTLP tracing
       source="tutorial"
   )
   
   # You can also use environment variables (recommended):
   # export HH_API_KEY="your-api-key-here"
   # export HH_PROJECT="My First Project"
   # tracer = HoneyHiveTracer.init(source="tutorial")
   
   # Use the @trace decorator to automatically trace this function
   @trace(tracer=tracer)
   def greet_user(name: str, language: str = "en") -> str:
       """A simple function that greets users in different languages."""
       
       greetings = {
           "en": f"Hello, {name}!",
           "es": f"¡Hola, {name}!",
           "fr": f"Bonjour, {name}!",
           "de": f"Hallo, {name}!"
       }
       
       greeting = greetings.get(language, greetings["en"])
       print(greeting)
       return greeting
   
   if __name__ == "__main__":
       # Call your traced function
       result = greet_user("Alice", "es")
       print(f"✅ Function returned: {result}")
       print("🎉 Check your HoneyHive dashboard to see the trace!")

Step 4: Run Your Script
-----------------------

Run your script:

.. code-block:: bash

   python hello_honeyhive.py

You should see output like:

.. code-block:: text

   ¡Hola, Alice!
   ✅ Function returned: ¡Hola, Alice!
   🎉 Check your HoneyHive dashboard to see the trace!

Step 5: View Your Trace
-----------------------

1. Open your HoneyHive dashboard at `app.honeyhive.ai <https://app.honeyhive.ai>`_
2. Navigate to **Projects** → **[your project name]**
3. You should see your trace with:
   - Function name: ``greet_user``
   - Input parameters: ``name="Alice"``, ``language="es"``
   - Output: ``"¡Hola, Alice!"``
   - Execution time and metadata

🎉 **Congratulations!** You've successfully:

- ✅ Installed the HoneyHive SDK
- ✅ Created your first traced function
- ✅ Sent trace data to HoneyHive
- ✅ Viewed the trace in your dashboard

Understanding What Happened
---------------------------

Let's break down what you just did:

1. **HoneyHiveTracer.init()**: Created a tracer instance for your project
2. **@trace decorator**: Automatically captured:
   - Function inputs and outputs
   - Execution time
   - Function name and metadata
3. **Automatic sending**: The SDK automatically sent trace data to HoneyHive

The Magic of ``@trace``
-----------------------

The ``@trace`` decorator is the easiest way to add observability to your functions. It:

- Captures all function arguments and return values
- Measures execution time
- Handles errors gracefully
- Works with both synchronous and asynchronous functions
- Automatically sends data to HoneyHive

.. tip::
   You can add ``@trace`` to any function in your codebase - even existing functions!

Environment Variables (Optional)
--------------------------------

Instead of hardcoding your API key, you can use environment variables:

.. code-block:: bash

   export HH_API_KEY="your-api-key-here"
   export HH_SOURCE="tutorial"

Then update your code:

.. code-block:: python

   # This will automatically use your environment variables
   tracer = HoneyHiveTracer.init()

What's Next?
------------

Now that you have basic tracing working, you're ready to:

- :doc:`02-basic-tracing` - Learn more tracing patterns and best practices
- :doc:`03-llm-integration` - Add LLM provider integration (OpenAI, Anthropic, etc.)
- :doc:`04-evaluation-basics` - Start evaluating your LLM outputs

Troubleshooting
---------------

**Not seeing traces in your dashboard?**

1. Check that your API key is correct
2. Verify your internet connection
3. Ensure you're looking at the right project in the dashboard

**Getting import errors?**

1. Make sure you installed with ``pip install honeyhive``
2. Check that you're using Python 3.11 or higher: ``python --version``

**Need more help?**

- Check our :doc:`../how-to/index` guide (Troubleshooting section)
- Join our `Discord community <https://discord.gg/honeyhive>`_
- Email support@honeyhive.ai

.. note::
   **Security Tip**: For production applications, always use environment variables or secure secret management for your API keys, never hardcode them in your source code.
