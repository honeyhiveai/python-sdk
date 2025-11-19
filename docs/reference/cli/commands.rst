CLI Commands Reference
======================

.. note::
   **Complete reference for HoneyHive CLI commands**
   
   This document provides detailed specifications for all available command-line interface commands in the HoneyHive SDK.

The HoneyHive CLI provides powerful command-line tools for managing projects, analyzing traces, running evaluations, and integrating with CI/CD pipelines.

Installation and Setup
----------------------

**Installation**:

.. code-block:: bash

   # Install with CLI support
   pip install honeyhive[cli]
   
   # Or install with all OpenInference integrations
   pip install honeyhive[all-openinference]

**Authentication**:

.. code-block:: bash

   # Set API key via environment variable
   export HH_API_KEY="your-api-key"
   
   # Or use CLI login command
   honeyhive auth login --api-key your-api-key
   
   # Verify authentication
   honeyhive auth whoami

Global Options
--------------

All commands support these global options:

.. option:: --api-key <key>

   HoneyHive API key for authentication.
   
   **Environment Variable**: ``HH_API_KEY``
   **Example**: ``--api-key hh_abc123...``

.. option:: --base-url <url>

   Base URL for HoneyHive API.
   
   **Default**: ``https://api.honeyhive.ai``
   **Environment Variable**: ``HH_BASE_URL``
   **Example**: ``--base-url https://api-staging.honeyhive.ai``

.. option:: --output <format>

   Output format for results.
   
   **Values**: ``json``, ``yaml``, ``table``, ``csv``
   **Default**: ``table``
   **Example**: ``--output json``

.. option:: --verbose, -v

   Enable verbose output.
   
   **Example**: ``-v`` or ``--verbose``

.. option:: --quiet, -q

   Suppress non-essential output.
   
   **Example**: ``-q`` or ``--quiet``

.. option:: --help, -h

   Show help information.

Authentication Commands
-----------------------

.. program:: honeyhive auth

**honeyhive auth**

Manage authentication credentials.

.. option:: login

   **honeyhive auth login**
   
   Authenticate with HoneyHive.

   .. option:: --api-key <key>

      API key for authentication.
      
      **Required**: Yes
      **Example**: ``honeyhive auth login --api-key hh_abc123...``

   .. option:: --save

      Save credentials to local config file.
      
      **Default**: ``true``
      **Example**: ``honeyhive auth login --api-key key --save``

   **Examples**:

   .. code-block:: bash

      # Basic login
      honeyhive auth login --api-key hh_abc123def456...
      
      # Login without saving
      honeyhive auth login --api-key hh_abc123... --no-save

.. option:: logout

   **honeyhive auth logout**
   
   Remove stored authentication credentials.

   .. option:: --all

      Remove all stored credentials.
      
      **Default**: ``false``

   **Examples**:

   .. code-block:: bash

      # Logout current user
      honeyhive auth logout
      
      # Remove all credentials
      honeyhive auth logout --all

.. option:: whoami

   **honeyhive auth whoami**
   
   Show current authenticated user information.

   **Examples**:

   .. code-block:: bash

      # Show current user
      honeyhive auth whoami
      
      # Output as JSON
      honeyhive auth whoami --output json

Project Commands
----------------

.. program:: honeyhive project

**honeyhive project**

Manage HoneyHive projects.

.. option:: list

   **honeyhive project list**
   
   List all accessible projects.

   .. option:: --limit <number>

      Maximum number of projects to return.
      
      **Default**: ``50``
      **Example**: ``--limit 100``

   .. option:: --offset <number>

      Number of projects to skip.
      
      **Default**: ``0``
      **Example**: ``--offset 20``

   **Examples**:

   .. code-block:: bash

      # List all projects
      honeyhive project list
      
      # List with pagination
      honeyhive project list --limit 10 --offset 20
      
      # Output as JSON
      honeyhive project list --output json

.. option:: create

   **honeyhive project create**
   
   Create a new project.

   .. option:: --name <name>

      Project name.
      
      **Required**: Yes
      **Example**: ``--name my-new-project``

   .. option:: --description <text>

      Project description.
      
      **Example**: ``--description "My LLM application project"``

   .. option:: --settings <json>

      Project settings as JSON.
      
      **Example**: ``--settings '{"retention_days": 90}'``

   **Examples**:

   .. code-block:: bash

      # Create basic project
      honeyhive project create --name my-project
      
      # Create with description
      honeyhive project create \
        --name my-project \
        --description "Production LLM app"

.. option:: get

   **honeyhive project get**
   
   Get project details.

   .. option:: <project-name>

      Name of the project to retrieve.
      
      **Required**: Yes
      **Example**: ``honeyhive project get my-project``

   **Examples**:

   .. code-block:: bash

      # Get project details
      honeyhive project get my-project
      
      # Output as JSON
      honeyhive project get my-project --output json

.. option:: update

   **honeyhive project update**
   
   Update project settings.

   .. option:: <project-name>

      Name of the project to update.
      
      **Required**: Yes

   .. option:: --description <text>

      Updated description.

   .. option:: --settings <json>

      Updated settings as JSON.

   **Examples**:

   .. code-block:: bash

      # Update description
      honeyhive project update my-project \
        --description "Updated description"
      
      # Update settings
      honeyhive project update my-project \
        --settings '{"retention_days": 120}'

.. option:: delete

   **honeyhive project delete**
   
   Delete a project.

   .. option:: <project-name>

      Name of the project to delete.
      
      **Required**: Yes

   .. option:: --confirm

      Skip confirmation prompt.
      
      **Default**: ``false``

   **Examples**:

   .. code-block:: bash

      # Delete with confirmation
      honeyhive project delete old-project
      
      # Delete without prompt
      honeyhive project delete old-project --confirm

Session Commands
----------------

.. program:: honeyhive session

**honeyhive session**

Manage tracing sessions.

.. option:: list

   **honeyhive session list**
   
   List sessions in a project.

   .. option:: Project name.
      
      **Required**: Yes

   .. option:: --limit <number>

      Maximum number of sessions to return.
      
      **Default**: ``50``

   .. option:: --start-date <date>

      Start date filter (ISO format).
      
      **Example**: ``--start-date 2024-01-01``

   .. option:: --end-date <date>

      End date filter (ISO format).
      
      **Example**: ``--end-date 2024-01-31``

   **Examples**:

   .. code-block:: bash

      # List recent sessions
      honeyhive session list # List sessions in date range
      honeyhive session list \
        \
        --start-date 2024-01-01 \
        --end-date 2024-01-31

.. option:: get

   **honeyhive session get**
   
   Get session details.

   .. option:: <session-id>

      Session ID to retrieve.
      
      **Required**: Yes

   .. option:: --include-events

      Include events in the session.
      
      **Default**: ``false``

   **Examples**:

   .. code-block:: bash

      # Get session overview
      honeyhive session get session_abc123
      
      # Get session with events
      honeyhive session get session_abc123 --include-events

.. option:: delete

   **honeyhive session delete**
   
   Delete a session.

   .. option:: <session-id>

      Session ID to delete.
      
      **Required**: Yes

   .. option:: --confirm

      Skip confirmation prompt.

   **Examples**:

   .. code-block:: bash

      # Delete session
      honeyhive session delete session_abc123 --confirm

Event Commands
--------------

.. program:: honeyhive event

**honeyhive event**

Manage and analyze events.

.. option:: list

   **honeyhive event list**
   
   List events in a session or project.

   .. option:: Project name.

   .. option:: --session-id <id>

      Session ID to filter by.

   .. option:: --event-type <type>

      Filter by event type.
      
      **Values**: ``llm``, ``tool``, ``chain``, ``evaluation``, etc.

   .. option:: --limit <number>

      Maximum number of events to return.
      
      **Default**: ``100``

   .. option:: --start-time <timestamp>

      Start time filter (ISO format).

   .. option:: --end-time <timestamp>

      End time filter (ISO format).

   **Examples**:

   .. code-block:: bash

      # List recent events
      honeyhive event list # List LLM events in session
      honeyhive event list \
        --session-id session_abc123 \
        --event-type llm
      
      # List events in time range
      honeyhive event list \
        \
        --start-time 2024-01-15T10:00:00Z \
        --end-time 2024-01-15T11:00:00Z

.. option:: get

   **honeyhive event get**
   
   Get event details.

   .. option:: <event-id>

      Event ID to retrieve.
      
      **Required**: Yes

   .. option:: --include-context

      Include parent/child context.
      
      **Default**: ``false``

   **Examples**:

   .. code-block:: bash

      # Get event details
      honeyhive event get evt_abc123
      
      # Get event with context
      honeyhive event get evt_abc123 --include-context

.. option:: search

   **honeyhive event search**
   
   Search events by criteria.

   .. option:: --query <text>

      Search query (supports various filters).
      
      **Example**: ``--query "model:gpt-4 AND status:error"``

   .. option:: Project to search in.

   .. option:: --limit <number>

      Maximum results to return.
      
      **Default**: ``50``

   **Examples**:

   .. code-block:: bash

      # Search for errors
      honeyhive event search \
        \
        --query "status:error"
      
      # Search for specific model
      honeyhive event search \
        \
        --query "model:gpt-4 AND event_type:model"

.. option:: export

   **honeyhive event export**
   
   Export events to file.

   .. option:: Project to export from.
      
      **Required**: Yes

   .. option:: --output-file <path>

      Output file path.
      
      **Required**: Yes

   .. option:: --format <format>

      Export format.
      
      **Values**: ``json``, ``jsonl``, ``csv``, ``parquet``
      **Default**: ``jsonl``

   .. option:: --start-date <date>

      Start date for export.

   .. option:: --end-date <date>

      End date for export.

   .. option:: --event-types <types>

      Comma-separated event types to include.

   **Examples**:

   .. code-block:: bash

      # Export all events
      honeyhive event export \
        \
        --output-file events.jsonl
      
      # Export LLM events as CSV
      honeyhive event export \
        \
        --output-file llm_events.csv \
        --format csv \
        --event-types llm
      
      # Export date range
      honeyhive event export \
        \
        --output-file january_events.jsonl \
        --start-date 2024-01-01 \
        --end-date 2024-01-31

Evaluation Commands
-------------------

.. program:: honeyhive eval

**honeyhive eval**

Run and manage evaluations.

.. option:: run

   **honeyhive eval run**
   
   Run evaluations on events.

   .. option:: --evaluators <list>

      Comma-separated list of evaluators.
      
      **Required**: Yes
      **Example**: ``--evaluators factual_accuracy,relevance,quality``

   .. option:: --target-events <query>

      Query to select target events.
      
      **Example**: ``--target-events "event_type:model AND model:gpt-4"``

   .. option:: Project containing target events.

   .. option:: --config-file <path>

      Path to evaluation configuration file.

   .. option:: --parallel

      Run evaluators in parallel.
      
      **Default**: ``true``

   .. option:: --dry-run

      Show what would be evaluated without running.

   **Examples**:

   .. code-block:: bash

      # Run evaluations on recent LLM events
      honeyhive eval run \
        \
        --evaluators factual_accuracy,quality \
        --target-events "event_type:model AND start_time:>2024-01-15"
      
      # Dry run to see what would be evaluated
      honeyhive eval run \
        \
        --evaluators quality \
        --target-events "session_id:session_abc123" \
        --dry-run
      
      # Run with config file
      honeyhive eval run --config-file evaluation_config.yaml

.. option:: list

   **honeyhive eval list**
   
   List evaluation results.

   .. option:: Project to list evaluations from.

   .. option:: --target-event-id <id>

      Filter by target event ID.

   .. option:: --evaluator <name>

      Filter by evaluator name.

   .. option:: --start-date <date>

      Start date filter.

   .. option:: --end-date <date>

      End date filter.

   **Examples**:

   .. code-block:: bash

      # List recent evaluations
      honeyhive eval list # List evaluations for specific event
      honeyhive eval list \
        \
        --target-event-id evt_abc123
      
      # List quality evaluations
      honeyhive eval list \
        \
        --evaluator quality

.. option:: get

   **honeyhive eval get**
   
   Get evaluation details.

   .. option:: <evaluation-id>

      Evaluation ID to retrieve.
      
      **Required**: Yes

   **Examples**:

   .. code-block:: bash

      # Get evaluation details
      honeyhive eval get eval_abc123

.. option:: compare

   **honeyhive eval compare**
   
   Compare evaluation results.

   .. option:: --evaluations <ids>

      Comma-separated evaluation IDs to compare.
      
      **Required**: Yes

   .. option:: --baseline <id>

      Baseline evaluation ID for comparison.

   **Examples**:

   .. code-block:: bash

      # Compare evaluations
      honeyhive eval compare \
        --evaluations eval_123,eval_456,eval_789
      
      # Compare against baseline
      honeyhive eval compare \
        --evaluations eval_456,eval_789 \
        --baseline eval_123

.. option:: export

   **honeyhive eval export**
   
   Export evaluation results.

   .. option:: Project to export from.

   .. option:: --output-file <path>

      Output file path.

   .. option:: --format <format>

      Export format.
      
      **Values**: ``json``, ``csv``, ``excel``

   .. option:: --evaluator <name>

      Filter by evaluator name.

   **Examples**:

   .. code-block:: bash

      # Export all evaluations
      honeyhive eval export \
        \
        --output-file evaluations.csv \
        --format csv
      
      # Export specific evaluator results
      honeyhive eval export \
        \
        --output-file quality_evals.json \
        --evaluator quality

Trace Analysis Commands
-----------------------

.. program:: honeyhive trace

**honeyhive trace**

Analyze traces and spans.

.. option:: analyze

   **honeyhive trace analyze**
   
   Analyze trace patterns and performance.

   .. option:: Project to analyze.

   .. option:: --time-window <window>

      Time window for analysis.
      
      **Values**: ``1h``, ``24h``, ``7d``, ``30d``
      **Default**: ``24h``

   .. option:: --output-file <path>

      Save analysis results to file.

   .. option:: --include-metrics

      Include detailed metrics in analysis.

   **Examples**:

   .. code-block:: bash

      # Analyze recent traces
      honeyhive trace analyze # Analyze last week with metrics
      honeyhive trace analyze \
        \
        --time-window 7d \
        --include-metrics \
        --output-file trace_analysis.json

.. option:: performance

   **honeyhive trace performance**
   
   Analyze trace performance metrics.

   .. option:: Project to analyze.

   .. option:: --groupby <field>

      Group results by field.
      
      **Values**: ``model``, ``event_type``, ``user_id``, ``session_id``

   .. option:: --percentiles <list>

      Comma-separated percentiles to calculate.
      
      **Default**: ``50,90,95,99``

   **Examples**:

   .. code-block:: bash

      # Performance analysis by model
      honeyhive trace performance \
        \
        --groupby model
      
      # Custom percentiles
      honeyhive trace performance \
        \
        --percentiles 50,75,90,95,99

.. option:: errors

   **honeyhive trace errors**
   
   Analyze error patterns in traces.

   .. option:: Project to analyze.

   .. option:: --time-window <window>

      Time window for analysis.

   .. option:: --groupby <field>

      Group errors by field.

   **Examples**:

   .. code-block:: bash

      # Analyze recent errors
      honeyhive trace errors # Group errors by model
      honeyhive trace errors \
        \
        --groupby model

Configuration Commands
----------------------

.. program:: honeyhive config

**honeyhive config**

Manage CLI configuration.

.. option:: get

   **honeyhive config get**
   
   Get configuration value.

   .. option:: <key>

      Configuration key to retrieve.
      
      **Example**: ``honeyhive config get api_key``

.. option:: set

   **honeyhive config set**
   
   Set configuration value.

   .. option:: <key> <value>

      Configuration key and value.
      
      **Example**: ``honeyhive config set default_project my-project``

.. option:: list

   **honeyhive config list**
   
   List all configuration values.

   **Examples**:

   .. code-block:: bash

      # List all config
      honeyhive config list
      
      # List as JSON
      honeyhive config list --output json

.. option:: reset

   **honeyhive config reset**
   
   Reset configuration to defaults.

   .. option:: --confirm

      Skip confirmation prompt.

   **Examples**:

   .. code-block:: bash

      # Reset config
      honeyhive config reset --confirm

Utility Commands
----------------

.. program:: honeyhive

**honeyhive validate**

Validate data and configurations.

.. option:: --config-file <path>

   Configuration file to validate.

.. option:: --data-file <path>

   Data file to validate.

.. option:: --schema <type>

   Schema type for validation.
   
   **Values**: ``event``, ``evaluation``, ``config``

**Examples**:

.. code-block:: bash

   # Validate config file
   honeyhive validate --config-file config.yaml
   
   # Validate event data
   honeyhive validate --data-file events.jsonl --schema event

**honeyhive version**

Show version information.

**Examples**:

.. code-block:: bash

   # Show version
   honeyhive version
   
   # Detailed version info
   honeyhive version --verbose

**honeyhive help**

Show help information.

.. option:: <command>

   Show help for specific command.

**Examples**:

.. code-block:: bash

   # General help
   honeyhive help
   
   # Command-specific help
   honeyhive help eval run

Configuration File Format
-------------------------

**YAML Configuration**:

.. code-block:: yaml

   # honeyhive.yaml
   api_key: "hh_your_api_key"
   base_url: "https://api.honeyhive.ai"
   default_project: "my-project"
   
   output:
     format: "table"
     verbose: false
   
   evaluation:
     parallel: true
     timeout_ms: 30000
     default_evaluators:
       - "quality"
       - "relevance"
   
   trace:
     default_time_window: "24h"
     performance_percentiles: [50, 90, 95, 99]

**JSON Configuration**:

.. code-block:: json

   {
     "api_key": "hh_your_api_key",
     "base_url": "https://api.honeyhive.ai",
     "default_project": "my-project",
     "output": {
       "format": "table",
       "verbose": false
     },
     "evaluation": {
       "parallel": true,
       "timeout_ms": 30000,
       "default_evaluators": ["quality", "relevance"]
     }
   }

Environment Variables
---------------------

The CLI respects these environment variables:

.. envvar:: HH_API_KEY

   HoneyHive API key for authentication.

.. envvar:: HH_BASE_URL

   Base URL for HoneyHive API.
   
   **Default**: ``https://api.honeyhive.ai``

.. envvar:: HH_PROJECT

   Default project name for operations. Required field that must match your HoneyHive project.

.. envvar:: HH_CONFIG_FILE

   Path to configuration file.
   
   **Default**: ``~/.honeyhive/config.yaml``

.. envvar:: HH_OUTPUT_FORMAT

   Default output format.
   
   **Values**: ``json``, ``yaml``, ``table``, ``csv``
   **Default**: ``table``

Exit Codes
----------

The CLI uses these exit codes:

- ``0``: Success
- ``1``: General error
- ``2``: Invalid command usage
- ``3``: Authentication error
- ``4``: Network/API error
- ``5``: Data validation error
- ``6``: Permission error

Examples and Use Cases
----------------------

**Daily Monitoring**:

.. code-block:: bash

   #!/bin/bash
   # Daily monitoring script
   
   PROJECT="production-llm-app"
   DATE=$(date -d "yesterday" +%Y-%m-%d)
   
   # Check for errors
   honeyhive trace errors \
     \
     --time-window 24h \
     --output json > daily_errors.json
   
   # Performance analysis
   honeyhive trace performance \
     \
     --time-window 24h \
     --groupby model > daily_performance.txt
   
   # Run evaluations on recent events
   honeyhive eval run \
     \
     --evaluators quality,factual_accuracy \
     --target-events "start_time:>$DATE"

**CI/CD Integration**:

.. code-block:: bash

   #!/bin/bash
   # CI/CD evaluation script
   
   # Export test session events
   honeyhive event export \
     \
     --session-id $TEST_SESSION_ID \
     --output-file test_events.jsonl
   
   # Run evaluations
   honeyhive eval run \
     --evaluators quality,accuracy \
     --target-events "session_id:$TEST_SESSION_ID" \
     --output json > evaluation_results.json
   
   # Check if evaluations pass threshold
   python check_evaluation_thresholds.py evaluation_results.json

**Data Export for Analysis**:

.. code-block:: bash

   #!/bin/bash
   # Export data for ML analysis
   
   PROJECT="ml-training-data"
   START_DATE="2024-01-01"
   END_DATE="2024-01-31"
   
   # Export events
   honeyhive event export \
     \
     --start-date $START_DATE \
     --end-date $END_DATE \
     --format parquet \
     --output-file events_jan2024.parquet
   
   # Export evaluations
   honeyhive eval export \
     \
     --format csv \
     --output-file evaluations_jan2024.csv

See Also
--------

- :doc:`options` - Detailed CLI options reference
- :doc:`../configuration/environment-vars` - Environment variable configuration
- :doc:`../../tutorials/01-setup-first-tracer` - Getting started with HoneyHive
- :doc:`../../development/testing/ci-cd-integration` - CI/CD integration patterns
