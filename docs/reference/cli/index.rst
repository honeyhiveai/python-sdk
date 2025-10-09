CLI Reference
=============

.. note::
   **Complete command-line interface reference for HoneyHive SDK**
   
   Command-line tools for managing projects, evaluating models, and debugging traces.

The HoneyHive SDK includes a comprehensive command-line interface (CLI) for managing projects, running evaluations, and debugging traces without writing code.

Installation and Setup
----------------------

The CLI is included with the HoneyHive SDK installation:

.. code-block:: bash

   pip install honeyhive

Verify installation:

.. code-block:: bash

   honeyhive --version
   # Output: honeyhive 2.1.0

Configuration
~~~~~~~~~~~~~

Configure the CLI with your API key:

.. code-block:: bash

   # Set API key (recommended method)
   export HH_API_KEY="hh_your_api_key_here"
   
   # Alternative: Configure interactively
   honeyhive configure

   # Verify configuration
   honeyhive configure --show

Global Options
--------------

All commands support these global options:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Option
     - Description
   * - ``--api-key TEXT``
     - HoneyHive API key (overrides ``HH_API_KEY`` environment variable)

   * - ``--base-url TEXT``
     - API base URL (default: https://api.honeyhive.ai)
   * - ``--timeout FLOAT``
     - Request timeout in seconds (default: 30.0)
   * - ``--verbose / --quiet``
     - Increase/decrease output verbosity
   * - ``--help``
     - Show help message and exit

Commands Overview
-----------------

.. code-block:: bash

   honeyhive [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]

**Available Commands:**

- ``configure`` - Configure CLI settings
- ``project`` - Project management commands
- ``session`` - Session management commands  
- ``event`` - Event management commands
- ``evaluate`` - Run evaluations
- ``trace`` - Trace debugging and analysis
- ``export`` - Export data
- ``validate`` - Validate configurations and data

Configuration Commands
----------------------

honeyhive configure
~~~~~~~~~~~~~~~~~~~

Configure CLI settings interactively or show current configuration.

**Usage:**

.. code-block:: bash

   honeyhive configure [OPTIONS]

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Option
     - Description
   * - ``--api-key TEXT``
     - Set API key

   * - ``--base-url TEXT``
     - Set API base URL
   * - ``--show``
     - Show current configuration
   * - ``--reset``
     - Reset configuration to defaults

**Examples:**

.. code-block:: bash

   # Interactive configuration
   honeyhive configure
   
   # Set specific values
   honeyhive configure --api-key "hh_your_key" # Show current configuration
   honeyhive configure --show
   
   # Reset to defaults
   honeyhive configure --reset

**Sample Interactive Session:**

.. code-block:: text

   $ honeyhive configure
   HoneyHive CLI Configuration
   ===========================
   
   API Key [current: hh_****...]: hh_your_new_key_here
   Default Project [current: my-old-project]: my-new-project
   Base URL [current: https://api.honeyhive.ai]: 
   
   Configuration saved successfully!

Project Management
------------------

honeyhive project
~~~~~~~~~~~~~~~~~

Manage HoneyHive projects.

**Usage:**

.. code-block:: bash

   honeyhive project SUBCOMMAND [OPTIONS]

**Subcommands:**

- ``list`` - List all projects
- ``create`` - Create a new project
- ``show`` - Show project details
- ``update`` - Update project settings
- ``delete`` - Delete a project

honeyhive project list
~~~~~~~~~~~~~~~~~~~~~~

List all accessible projects.

**Usage:**

.. code-block:: bash

   honeyhive project list [OPTIONS]

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Option
     - Description
   * - ``--limit INTEGER``
     - Maximum number of projects to show (default: 50)
   * - ``--format [table|json|csv]``
     - Output format (default: table)
   * - ``--sort-by [name|created|events]``
     - Sort projects by field (default: name)

**Examples:**

.. code-block:: bash

   # List all projects
   honeyhive project list
   
   # List with JSON output
   honeyhive project list --format json
   
   # List top 10 projects by event count
   honeyhive project list --limit 10 --sort-by events

**Sample Output:**

.. code-block:: text

   $ honeyhive project list
   ┌────────────────────────┬─────────────────────┬────────────┬─────────────┐
   │ Name                   │ Created             │ Events     │ Last Event  │
   ├────────────────────────┼─────────────────────┼────────────┼─────────────┤
   │ customer-support       │ 2024-01-15 10:30:00 │ 15,432     │ 2 hours ago │
   │ content-generation     │ 2024-01-20 14:15:00 │ 8,765      │ 5 min ago   │
   │ data-analysis          │ 2024-02-01 09:00:00 │ 3,201      │ 1 day ago   │
   └────────────────────────┴─────────────────────┴────────────┴─────────────┘

honeyhive project create
~~~~~~~~~~~~~~~~~~~~~~~~

Create a new project.

**Usage:**

.. code-block:: bash

   honeyhive project create [OPTIONS] NAME

**Arguments:**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Argument
     - Description
   * - ``NAME``
     - Project name (required)

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Option
     - Description
   * - ``--description TEXT``
     - Project description
   * - ``--team TEXT``
     - Team or organization name
   * - ``--tags TEXT``
     - Comma-separated tags

**Examples:**

.. code-block:: bash

   # Create basic project
   honeyhive project create "new-llm-app"
   
   # Create with metadata
   honeyhive project create "chatbot-v2" \
     --description "Next generation customer service chatbot" \
     --team "ai-engineering" \
     --tags "chatbot,customer-service,gpt-4"

honeyhive project show
~~~~~~~~~~~~~~~~~~~~~~

Show detailed project information.

**Usage:**

.. code-block:: bash

   honeyhive project show [OPTIONS] [PROJECT_NAME]

**Arguments:**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Argument
     - Description
   * - ``PROJECT_NAME``
     - Project name (optional, uses default if not specified)

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Option
     - Description
   * - ``--format [table|json|yaml]``
     - Output format (default: table)
   * - ``--include-stats``
     - Include detailed statistics

**Examples:**

.. code-block:: bash

   # Show current project
   honeyhive project show
   
   # Show specific project with stats
   honeyhive project show "customer-support" --include-stats
   
   # JSON output for scripting
   honeyhive project show "my-project" --format json

Session Management
------------------

honeyhive session
~~~~~~~~~~~~~~~~~

Manage sessions within projects.

**Usage:**

.. code-block:: bash

   honeyhive session SUBCOMMAND [OPTIONS]

**Subcommands:**

- ``list`` - List sessions
- ``show`` - Show session details
- ``create`` - Create a new session
- ``delete`` - Delete a session

honeyhive session list
~~~~~~~~~~~~~~~~~~~~~~

List sessions in a project.

**Usage:**

.. code-block:: bash

   honeyhive session list [OPTIONS]

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Option
     - Description

   * - ``--limit INTEGER``
     - Maximum sessions to show (default: 50)
   * - ``--since TEXT``
     - Show sessions since date (ISO format)
   * - ``--source TEXT``
     - Filter by source environment

**Examples:**

.. code-block:: bash

   # List recent sessions
   honeyhive session list --limit 20
   
   # List production sessions from last week
   honeyhive session list --source "production" --since "2024-01-15T00:00:00Z"
   
   # List sessions
   honeyhive session list

honeyhive session show
~~~~~~~~~~~~~~~~~~~~~~

Show detailed session information.

**Usage:**

.. code-block:: bash

   honeyhive session show [OPTIONS] SESSION_ID

**Arguments:**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Argument
     - Description
   * - ``SESSION_ID``
     - Session identifier (required)

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Option
     - Description
   * - ``--include-events``
     - Include session events in output
   * - ``--format [table|json|yaml]``
     - Output format (default: table)

**Examples:**

.. code-block:: bash

   # Show session details
   honeyhive session show "session_abc123"
   
   # Show with all events
   honeyhive session show "session_abc123" --include-events

Event Management
----------------

honeyhive event
~~~~~~~~~~~~~~~

Manage events within sessions.

**Usage:**

.. code-block:: bash

   honeyhive event SUBCOMMAND [OPTIONS]

**Subcommands:**

- ``list`` - List events
- ``show`` - Show event details
- ``search`` - Search events

honeyhive event list
~~~~~~~~~~~~~~~~~~~~

List events with filtering options.

**Usage:**

.. code-block:: bash

   honeyhive event list [OPTIONS]

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Option
     - Description

   * - ``--session TEXT``
     - Filter by session ID
   * - ``--event-type TEXT``
     - Filter by event type
   * - ``--since TEXT``
     - Events since date (ISO format)
   * - ``--limit INTEGER``
     - Maximum events to show (default: 50)
   * - ``--errors-only``
     - Show only events with errors

**Examples:**

.. code-block:: bash

   # List recent events
   honeyhive event list --limit 100
   
   # List LLM call events from today
   honeyhive event list --event-type "llm_call" --since "2024-01-22T00:00:00Z"
   
   # List errors from specific session
   honeyhive event list --session "session_xyz789" --errors-only

honeyhive event search
~~~~~~~~~~~~~~~~~~~~~~

Search events by content or attributes.

**Usage:**

.. code-block:: bash

   honeyhive event search [OPTIONS] QUERY

**Arguments:**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Argument
     - Description
   * - ``QUERY``
     - Search query string

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Option
     - Description

   * - ``--field [inputs|outputs|metadata]``
     - Search specific field (default: all)
   * - ``--limit INTEGER``
     - Maximum results (default: 50)
   * - ``--case-sensitive``
     - Case-sensitive search

**Examples:**

.. code-block:: bash

   # Search for events containing "error"
   honeyhive event search "error"
   
   # Search in specific field
   honeyhive event search "gpt-4" --field "metadata"
   
   # Case-sensitive search in project
   honeyhive event search "API_ERROR" --case-sensitive

Evaluation Commands
-------------------

honeyhive evaluate
~~~~~~~~~~~~~~~~~~

Run evaluations on data or individual inputs.

**Usage:**

.. code-block:: bash

   honeyhive evaluate SUBCOMMAND [OPTIONS]

**Subcommands:**

- ``single`` - Evaluate a single input/output pair
- ``batch`` - Evaluate multiple items from file
- ``project`` - Evaluate recent project data
- ``compare`` - Compare evaluation results

honeyhive evaluate single
~~~~~~~~~~~~~~~~~~~~~~~~~

Evaluate a single input/output pair.

**Usage:**

.. code-block:: bash

   honeyhive evaluate single [OPTIONS]

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Option
     - Description
   * - ``--input TEXT``
     - Input text (required)
   * - ``--output TEXT``
     - Output text (required)
   * - ``--evaluator TEXT``
     - Evaluator type (default: quality)
   * - ``--criteria TEXT``
     - Evaluation criteria (comma-separated)
   * - ``--context TEXT``
     - Additional context (JSON format)

**Examples:**

.. code-block:: bash

   # Basic quality evaluation
   honeyhive evaluate single \
     --input "What is machine learning?" \
     --output "Machine learning is a subset of AI that enables computers to learn without explicit programming."
   
   # Custom criteria evaluation
   honeyhive evaluate single \
     --input "Explain quantum computing" \
     --output "Quantum computing uses quantum mechanics principles..." \
     --evaluator "quality" \
     --criteria "accuracy,clarity,completeness"
   
   # With context
   honeyhive evaluate single \
     --input "How do I reset my password?" \
     --output "To reset your password, click the 'Forgot Password' link..." \
     --context '{"domain": "customer_support", "audience": "general"}'

honeyhive evaluate batch
~~~~~~~~~~~~~~~~~~~~~~~~

Evaluate multiple items from a file.

**Usage:**

.. code-block:: bash

   honeyhive evaluate batch [OPTIONS] INPUT_FILE

**Arguments:**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Argument
     - Description
   * - ``INPUT_FILE``
     - Path to input file (JSON, CSV, or JSONL)

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Option
     - Description
   * - ``--output TEXT``
     - Output file path (default: stdout)
   * - ``--evaluator TEXT``
     - Evaluator type (default: quality)
   * - ``--parallel INTEGER``
     - Number of parallel evaluations (default: 5)
   * - ``--format [json|csv|table]``
     - Output format (default: table)

**Input File Format (JSON):**

.. code-block:: json

   [
     {
       "input": "What is the capital of France?",
       "output": "The capital of France is Paris.",
       "context": {"domain": "geography"}
     },
     {
       "input": "Explain photosynthesis",
       "output": "Photosynthesis is the process by which plants convert sunlight into energy...",
       "context": {"domain": "biology", "level": "high_school"}
     }
   ]

**Examples:**

.. code-block:: bash

   # Evaluate test cases
   honeyhive evaluate batch test_cases.json
   
   # Parallel evaluation with output file
   honeyhive evaluate batch large_dataset.jsonl \
     --parallel 10 \
     --output evaluation_results.json
   
   # CSV output for analysis
   honeyhive evaluate batch qa_pairs.csv --format csv

honeyhive evaluate project
~~~~~~~~~~~~~~~~~~~~~~~~~~

Evaluate recent data from a project.

**Usage:**

.. code-block:: bash

   honeyhive evaluate project [OPTIONS] [PROJECT_NAME]

**Arguments:**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Argument
     - Description
   * - ``PROJECT_NAME``
     - Project to evaluate (uses default if not specified)

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Option
     - Description
   * - ``--since TEXT``
     - Evaluate events since date (ISO format)
   * - ``--limit INTEGER``
     - Maximum events to evaluate (default: 100)
   * - ``--event-type TEXT``
     - Filter by event type
   * - ``--evaluator TEXT``
     - Evaluator type (default: quality)
   * - ``--save-results``
     - Save results back to HoneyHive

**Examples:**

.. code-block:: bash

   # Evaluate recent project activity
   honeyhive evaluate project "customer-support" --since "2024-01-20T00:00:00Z"
   
   # Evaluate LLM calls only
   honeyhive evaluate project --event-type "llm_call" --limit 50
   
   # Evaluate and save results
   honeyhive evaluate project "production-bot" --save-results

Trace Analysis
--------------

honeyhive trace
~~~~~~~~~~~~~~~

Analyze and debug traces.

**Usage:**

.. code-block:: bash

   honeyhive trace SUBCOMMAND [OPTIONS]

**Subcommands:**

- ``show`` - Show trace details
- ``search`` - Search traces
- ``analyze`` - Analyze trace patterns
- ``export`` - Export trace data

honeyhive trace show
~~~~~~~~~~~~~~~~~~~~

Show detailed trace information.

**Usage:**

.. code-block:: bash

   honeyhive trace show [OPTIONS] TRACE_ID

**Arguments:**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Argument
     - Description
   * - ``TRACE_ID``
     - Trace identifier (required)

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Option
     - Description
   * - ``--format [tree|json|table]``
     - Display format (default: tree)
   * - ``--include-attributes``
     - Show all span attributes
   * - ``--show-timing``
     - Show detailed timing information

**Examples:**

.. code-block:: bash

   # Show trace as tree
   honeyhive trace show "trace_abc123"
   
   # Show with all attributes
   honeyhive trace show "trace_abc123" --include-attributes
   
   # JSON format for scripting
   honeyhive trace show "trace_abc123" --format json

**Sample Tree Output:**

.. code-block:: text

   $ honeyhive trace show "trace_abc123"
   Trace: trace_abc123 (Duration: 2.34s)
   ├── user_request [2.34s]
   │   ├── validate_input [0.02s] ✓
   │   ├── llm_generation [2.1s]
   │   │   ├── openai_call [1.8s] ✓
   │   │   └── post_processing [0.3s] ✓
   │   └── response_formatting [0.22s] ✓

honeyhive trace analyze
~~~~~~~~~~~~~~~~~~~~~~~

Analyze trace patterns and performance.

**Usage:**

.. code-block:: bash

   honeyhive trace analyze [OPTIONS]

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Option
     - Description

   * - ``--since TEXT``
     - Analyze traces since date
   * - ``--operation TEXT``
     - Focus on specific operation
   * - ``--report [performance|errors|patterns]``
     - Type of analysis report

**Examples:**

.. code-block:: bash

   # Performance analysis
   honeyhive trace analyze --report performance
   
   # Error analysis for last 24 hours
   honeyhive trace analyze --since "2024-01-21T00:00:00Z" --report errors
   
   # Pattern analysis for specific operation
   honeyhive trace analyze --operation "llm_call" --report patterns

Data Export
-----------

honeyhive export
~~~~~~~~~~~~~~~~

Export data for analysis or backup.

**Usage:**

.. code-block:: bash

   honeyhive export SUBCOMMAND [OPTIONS]

**Subcommands:**

- ``events`` - Export events
- ``sessions`` - Export sessions
- ``evaluations`` - Export evaluation results
- ``traces`` - Export trace data

honeyhive export events
~~~~~~~~~~~~~~~~~~~~~~~

Export event data.

**Usage:**

.. code-block:: bash

   honeyhive export events [OPTIONS] OUTPUT_FILE

**Arguments:**

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Argument
     - Description
   * - ``OUTPUT_FILE``
     - Output file path

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Option
     - Description

   * - ``--since TEXT``
     - Export events since date
   * - ``--format [json|csv|parquet]``
     - Output format (default: json)
   * - ``--include [inputs|outputs|metadata|all]``
     - Data to include (default: all)

**Examples:**

.. code-block:: bash

   # Export all events
   honeyhive export events all_events.json # Export recent events as CSV
   honeyhive export events recent_events.csv \
     --since "2024-01-20T00:00:00Z" \
     --format csv
   
   # Export metadata only
   honeyhive export events metadata.json --include metadata

Validation Commands
-------------------

honeyhive validate
~~~~~~~~~~~~~~~~~~

Validate configurations and data.

**Usage:**

.. code-block:: bash

   honeyhive validate SUBCOMMAND [OPTIONS]

**Subcommands:**

- ``config`` - Validate configuration
- ``data`` - Validate data format
- ``api`` - Test API connectivity

honeyhive validate config
~~~~~~~~~~~~~~~~~~~~~~~~~

Validate CLI and SDK configuration.

**Usage:**

.. code-block:: bash

   honeyhive validate config [OPTIONS]

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Option
     - Description
   * - ``--environment TEXT``
     - Validate specific environment config
   * - ``--check-connectivity``
     - Test API connectivity

**Examples:**

.. code-block:: bash

   # Basic configuration validation
   honeyhive validate config
   
   # Validate with connectivity test
   honeyhive validate config --check-connectivity
   
   # Validate production environment
   honeyhive validate config --environment production

honeyhive validate api
~~~~~~~~~~~~~~~~~~~~~~

Test API connectivity and permissions.

**Usage:**

.. code-block:: bash

   honeyhive validate api [OPTIONS]

**Options:**

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Option
     - Description
   * - ``--test-write``
     - Test write permissions (creates test data)
   * - ``--test-project TEXT``
     - Test specific project access

**Examples:**

.. code-block:: bash

   # Test basic API access
   honeyhive validate api
   
   # Test full read/write access
   honeyhive validate api --test-write
   
   # Test specific project access
   honeyhive validate api --test-project "my-project"

Scripting and Automation
------------------------

Output Formats
~~~~~~~~~~~~~~

Most commands support multiple output formats for scripting:

.. code-block:: bash

   # JSON for scripting
   honeyhive project list --format json | jq '.[] | .name'
   
   # CSV for data analysis
   honeyhive event list --format csv | python analyze_events.py
   
   # Table for human reading
   honeyhive session list --format table

Exit Codes
~~~~~~~~~~

The CLI uses standard exit codes:

- ``0`` - Success
- ``1`` - General error
- ``2`` - Invalid arguments
- ``3`` - Authentication error
- ``4`` - Not found error
- ``5`` - Timeout error

**Example Script:**

.. code-block:: bash

   #!/bin/bash
   # Check if project exists
   if honeyhive project show "my-project" --format json > /dev/null 2>&1; then
       echo "Project exists"
       # Export recent data
       honeyhive export events "backup_$(date +%Y%m%d).json" else
       echo "Project not found"
       exit 1
   fi

Configuration Files
~~~~~~~~~~~~~~~~~~~

The CLI supports configuration files for complex setups:

.. code-block:: yaml

   # ~/.honeyhive/config.yaml
   default:
     api_key: "${HH_API_KEY}"
     project: "my-default-project"
     base_url: "https://api.honeyhive.ai"
   
   environments:
     development:
       project: "my-app-dev"
       timeout: 10.0
     
     production:
       project: "my-app-prod"
       timeout: 60.0

Advanced Usage
--------------

Batch Processing
~~~~~~~~~~~~~~~~

Process multiple projects or large datasets:

.. code-block:: bash

   # Process all projects
   for project in $(honeyhive project list --format json | jq -r '.[].name'); do
       echo "Processing $project..."
       honeyhive evaluate project "$project" --since "2024-01-20T00:00:00Z"
   done
   
   # Parallel processing
   honeyhive project list --format json | \
     jq -r '.[].name' | \
     xargs -P 4 -I {} honeyhive evaluate project {}

Integration with CI/CD
~~~~~~~~~~~~~~~~~~~~~~

Use in continuous integration pipelines:

.. code-block:: yaml

   # .github/workflows/evaluation.yml
   name: Model Evaluation
   on:
     schedule:
       - cron: '0 2 * * *'  # Daily at 2 AM
   
   jobs:
     evaluate:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Install HoneyHive CLI
           run: pip install honeyhive
         
         - name: Evaluate Production Model
           env:
             HH_API_KEY: ${{ secrets.HONEYHIVE_API_KEY }}
           run: |
             honeyhive evaluate project "production-model" \
               --since "$(date -d '1 day ago' -I)T00:00:00Z" \
               --save-results
         
         - name: Generate Report
           run: |
             honeyhive trace analyze \
               --since "$(date -d '1 day ago' -I)T00:00:00Z" \
               --report performance > performance_report.txt

Monitoring and Alerting
~~~~~~~~~~~~~~~~~~~~~~~

Create monitoring scripts:

.. code-block:: bash

   #!/bin/bash
   # Monitor error rate
   error_count=$(honeyhive event list \
     \
     --since "$(date -d '1 hour ago' -I)T$(date -d '1 hour ago' +%H):00:00Z" \
     --errors-only \
     --format json | jq length)
   
   if [ "$error_count" -gt 10 ]; then
       echo "High error rate detected: $error_count errors in last hour"
       # Send alert (e.g., Slack, email, PagerDuty)
       curl -X POST -H 'Content-type: application/json' \
         --data "{\"text\":\"🚨 HoneyHive Alert: $error_count errors in production-app\"}" \
         "$SLACK_WEBHOOK_URL"
   fi

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Authentication Errors:**

.. code-block:: bash

   # Check API key format
   honeyhive validate config
   
   # Test API connectivity
   honeyhive validate api

**Network Issues:**

.. code-block:: bash

   # Increase timeout
   honeyhive --timeout 60 project list
   
   # Check proxy settings
   export HTTP_PROXY="http://proxy.company.com:8080"
   honeyhive project list

**Performance Issues:**

.. code-block:: bash

   # Reduce batch size for large exports
   honeyhive export events large_export.json --limit 1000
   
   # Use parallel processing
   honeyhive evaluate batch large_dataset.json --parallel 2

Debug Mode
~~~~~~~~~~

Enable verbose output for debugging:

.. code-block:: bash

   # Enable debug logging
   honeyhive --verbose project list
   
   # Even more verbose
   export HH_LOG_LEVEL=DEBUG
   honeyhive project list

See Also
--------

- :doc:`../configuration/environment-vars` - Environment variable reference
- :doc:`../../tutorials/01-setup-first-tracer` - Getting started tutorial
- :doc:`../../how-to/index` - Troubleshooting guide (see Troubleshooting section)
- :doc:`../../explanation/concepts/llm-observability` - LLM observability concepts
