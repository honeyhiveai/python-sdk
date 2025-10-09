CLI Options Reference
=====================

.. note::
   **Detailed reference for all HoneyHive CLI options and parameters**
   
   This document provides comprehensive details for every option available in the HoneyHive CLI.

This reference covers all command-line options, their accepted values, defaults, and usage patterns across all HoneyHive CLI commands.

Global Options
--------------

These options are available for all commands:

Authentication Options
~~~~~~~~~~~~~~~~~~~~~~

.. option:: --api-key <key>

   **Description**: HoneyHive API key for authentication
   
   **Environment Variable**: ``HH_API_KEY``
   
   **Format**: String starting with ``hh_``
   
   **Required**: Yes (unless set via environment variable or config)
   
   **Example**: ``--api-key hh_1234567890abcdef...``
   
   **Notes**: 
   - Can be obtained from HoneyHive dashboard
   - Should be kept secure and not committed to code

.. option:: --base-url <url>

   **Description**: Base URL for HoneyHive API
   
   **Environment Variable**: ``HH_BASE_URL``
   
   **Default**: ``https://api.honeyhive.ai``
   
   **Format**: Valid URL
   
   **Examples**: 
   - ``--base-url https://api-staging.honeyhive.ai``
   - ``--base-url https://api.honeyhive.ai``
   
   **Use Cases**:
   - Staging environment testing
   - Self-hosted HoneyHive instances
   - Development environments

.. option:: **Description**: Default project name for operations
   
   **Notes**:
   - Used as default when commands require a project
   - Can be overridden by command-specific project options

Output Options
~~~~~~~~~~~~~~

.. option:: --output <format>

   **Description**: Output format for command results
   
   **Environment Variable**: ``HH_OUTPUT_FORMAT``
   
   **Default**: ``table``
   
   **Values**:
   - ``table`` - Human-readable table format
   - ``json`` - JSON format for programmatic use
   - ``yaml`` - YAML format
   - ``csv`` - Comma-separated values
   - ``tsv`` - Tab-separated values
   
   **Examples**:
   
   .. code-block:: bash
   
      # Table output (default)
      honeyhive project list
      
      # JSON output
      honeyhive project list --output json
      
      # CSV output for spreadsheets
      honeyhive event list --output csv

.. option:: --verbose, -v

   **Description**: Enable verbose output
   
   **Default**: ``false``
   
   **Behavior**:
   - Shows additional debugging information
   - Displays API request/response details
   - Includes timing information
   - Shows progress indicators
   
   **Example**: ``honeyhive eval run --evaluators quality -v``

.. option:: --quiet, -q

   **Description**: Suppress non-essential output
   
   **Default**: ``false``
   
   **Behavior**:
   - Only shows critical information and errors
   - Suppresses progress indicators
   - Reduces output verbosity
   - Useful for scripting
   
   **Example**: ``honeyhive event export -q``

.. option:: --no-color

   **Description**: Disable colored output
   
   **Default**: ``false``
   
   **Use Cases**:
   - CI/CD environments
   - File output redirection
   - Terminals without color support
   
   **Example**: ``honeyhive trace analyze --no-color > analysis.txt``

.. option:: --config-file <path>

   **Description**: Path to configuration file
   
   **Environment Variable**: ``HH_CONFIG_FILE``
   
   **Default**: ``~/.honeyhive/config.yaml``
   
   **Formats Supported**: YAML, JSON
   
   **Example**: ``--config-file ./my-config.yaml``

Help and Information
~~~~~~~~~~~~~~~~~~~~

.. option:: --help, -h

   **Description**: Show help information
   
   **Behavior**:
   - Shows command usage
   - Lists available options
   - Provides examples
   
   **Examples**:
   
   .. code-block:: bash
   
      # General help
      honeyhive --help
      
      # Command-specific help
      honeyhive eval run --help

.. option:: --version

   **Description**: Show version information
   
   **Output**: Version number and build information
   
   **Example**: ``honeyhive --version``

Command-Specific Options
------------------------

Project Commands
~~~~~~~~~~~~~~~~

**honeyhive project list**

.. option:: --limit <number>

   **Description**: Maximum number of projects to return
   
   **Default**: ``50``
   
   **Range**: 1-1000
   
   **Example**: ``--limit 100``

.. option:: --offset <number>

   **Description**: Number of projects to skip (pagination)
   
   **Default**: ``0``
   
   **Range**: 0+
   
   **Example**: ``--offset 20``

.. option:: --sort <field>

   **Description**: Sort projects by field
   
   **Values**: ``name``, ``created_at``, ``updated_at``
   
   **Default**: ``name``
   
   **Example**: ``--sort created_at``

.. option:: --order <direction>

   **Description**: Sort order
   
   **Values**: ``asc``, ``desc``
   
   **Default**: ``asc``
   
   **Example**: ``--order desc``

**honeyhive project create**

.. option:: --name <name>

   **Description**: Project name
   
   **Required**: Yes
   
   **Format**: 1-100 characters, alphanumeric with hyphens/underscores
   
   **Example**: ``--name my-new-project``

.. option:: --description <text>

   **Description**: Project description
   
   **Format**: Up to 500 characters
   
   **Example**: ``--description "Production LLM application for customer support"``

.. option:: --settings <json>

   **Description**: Project settings as JSON
   
   **Format**: Valid JSON object
   
   **Example**: ``--settings '{"retention_days": 90, "auto_eval": true}'``

.. option:: --team <name>

   **Description**: Team to assign project to
   
   **Format**: Team name string
   
   **Example**: ``--team ml-engineering``

Session Commands
~~~~~~~~~~~~~~~~

**honeyhive session list**

.. option:: --start-date <date>

   **Description**: Filter sessions from this date
   
   **Format**: ISO 8601 date (YYYY-MM-DD) or datetime
   
   **Examples**:
   - ``--start-date 2024-01-01``
   - ``--start-date 2024-01-15T10:30:00Z``

.. option:: --end-date <date>

   **Description**: Filter sessions until this date
   
   **Format**: ISO 8601 date (YYYY-MM-DD) or datetime
   
   **Example**: ``--end-date 2024-01-31``

.. option:: --user-id <id>

   **Description**: Filter by user ID
   
   **Format**: User identifier string
   
   **Example**: ``--user-id user_12345``

.. option:: --source <source>

   **Description**: Filter by session source
   
   **Format**: Source identifier string
   
   **Example**: ``--source chat-bot``

.. option:: --status <status>

   **Description**: Filter by session status
   
   **Values**: ``active``, ``completed``, ``error``
   
   **Example**: ``--status completed``

Event Commands
~~~~~~~~~~~~~~

**honeyhive event list**

.. option:: --session-id <id>

   **Description**: Filter events by session ID
   
   **Format**: Session UUID
   
   **Example**: ``--session-id session_abc123def456``

.. option:: --event-type <type>

   **Description**: Filter by event type
   
   **Values**: ``llm``, ``tool``, ``chain``, ``retrieval``, ``embedding``, ``evaluation``, ``custom``
   
   **Example**: ``--event-type llm``

.. option:: --event-name <name>

   **Description**: Filter by event name
   
   **Format**: Event name string
   
   **Example**: ``--event-name openai-chat-completion``

.. option:: --user-id <id>

   **Description**: Filter by user ID
   
   **Example**: ``--user-id user_98765``

.. option:: --model <model>

   **Description**: Filter by LLM model
   
   **Examples**: 
   - ``--model gpt-4``
   - ``--model claude-3-sonnet-20240229``

.. option:: --provider <provider>

   **Description**: Filter by LLM provider
   
   **Values**: ``openai``, ``anthropic``, ``google``, ``azure``, ``local``
   
   **Example**: ``--provider openai``

.. option:: --status <status>

   **Description**: Filter by event status
   
   **Values**: ``success``, ``error``, ``cancelled``, ``timeout``
   
   **Example**: ``--status error``

.. option:: --min-duration <ms>

   **Description**: Filter events with minimum duration
   
   **Format**: Duration in milliseconds
   
   **Example**: ``--min-duration 1000``

.. option:: --max-duration <ms>

   **Description**: Filter events with maximum duration
   
   **Format**: Duration in milliseconds
   
   **Example**: ``--max-duration 5000``

.. option:: --start-time <timestamp>

   **Description**: Filter events from this timestamp
   
   **Format**: ISO 8601 timestamp
   
   **Example**: ``--start-time 2024-01-15T10:30:00Z``

.. option:: --end-time <timestamp>

   **Description**: Filter events until this timestamp
   
   **Format**: ISO 8601 timestamp
   
   **Example**: ``--end-time 2024-01-15T11:30:00Z``

**honeyhive event search**

.. option:: --query <text>

   **Description**: Search query with field filters
   
   **Format**: Lucene-style query syntax
   
   **Field Filters**:
   - ``event_type:model`` - Filter by event type
   - ``model:gpt-4`` - Filter by model
   - ``status:error`` - Filter by status
   - ``user_id:user_123`` - Filter by user
   - ``duration:>1000`` - Duration greater than 1000ms
   - ``start_time:>2024-01-15`` - Events after date
   
   **Operators**:
   - ``AND`` - Both conditions must match
   - ``OR`` - Either condition can match
   - ``NOT`` - Exclude matching conditions
   - ``()`` - Group conditions
   
   **Examples**:
   
   .. code-block:: bash
   
      # Find errors in GPT-4 calls
      --query "model:gpt-4 AND status:error"
      
      # Find slow LLM calls
      --query "event_type:model AND duration:>5000"
      
      # Complex query
      --query "(model:gpt-4 OR model:claude-3) AND status:success AND user_id:user_123"

.. option:: --fields <list>

   **Description**: Comma-separated list of fields to include in results
   
   **Default**: All fields
   
   **Available Fields**: ``event_id``, ``event_type``, ``event_name``, ``model``, ``status``, ``duration_ms``, ``start_time``, ``user_id``
   
   **Example**: ``--fields event_id,model,status,duration_ms``

**honeyhive event export**

.. option:: --format <format>

   **Description**: Export file format
   
   **Values**:
   - ``json`` - Single JSON object with array of events
   - ``jsonl`` - JSON Lines (one event per line)
   - ``csv`` - Comma-separated values
   - ``tsv`` - Tab-separated values
   - ``parquet`` - Apache Parquet format
   - ``excel`` - Excel spreadsheet (.xlsx)
   
   **Default**: ``jsonl``
   
   **Example**: ``--format csv``

.. option:: --output-file <path>

   **Description**: Output file path
   
   **Required**: Yes
   
   **Format**: Valid file path
   
   **Examples**:
   - ``--output-file events.jsonl``
   - ``--output-file /tmp/export/events.csv``

.. option:: --compress

   **Description**: Compress output file
   
   **Default**: ``false``
   
   **Formats**: Automatically detects based on file extension (.gz, .bz2, .xz)
   
   **Example**: ``--output-file events.jsonl.gz --compress``

.. option:: --batch-size <number>

   **Description**: Number of events per batch during export
   
   **Default**: ``1000``
   
   **Range**: 1-10000
   
   **Use Case**: Memory optimization for large exports
   
   **Example**: ``--batch-size 500``

.. option:: --include-metadata

   **Description**: Include event metadata in export
   
   **Default**: ``true``
   
   **Example**: ``--no-include-metadata`` (to exclude)

.. option:: --flatten-json

   **Description**: Flatten nested JSON objects in CSV/TSV exports
   
   **Default**: ``false``
   
   **Example**: ``--flatten-json``

Evaluation Commands
~~~~~~~~~~~~~~~~~~~

**honeyhive eval run**

.. option:: --evaluators <list>

   **Description**: Comma-separated list of evaluators to run
   
   **Required**: Yes
   
   **Available Evaluators**:
   - ``quality`` - Overall response quality
   - ``factual_accuracy`` - Factual correctness
   - ``relevance`` - Query relevance
   - ``toxicity`` - Content safety
   - ``length`` - Response length appropriateness
   - ``coherence`` - Response coherence
   - ``custom_evaluator_name`` - Custom evaluators
   
   **Example**: ``--evaluators quality,factual_accuracy,relevance``

.. option:: --target-events <query>

   **Description**: Query to select target events for evaluation
   
   **Format**: Same syntax as event search query
   
   **Examples**:
   
   .. code-block:: bash
   
      # Evaluate recent LLM events
      --target-events "event_type:model AND start_time:>2024-01-15"
      
      # Evaluate specific session
      --target-events "session_id:session_abc123"
      
      # Evaluate GPT-4 events with errors
      --target-events "model:gpt-4 AND status:error"

.. option:: --max-events <number>

   **Description**: Maximum number of events to evaluate
   
   **Default**: ``1000``
   
   **Range**: 1-10000
   
   **Example**: ``--max-events 500``

.. option:: --parallel

   **Description**: Run evaluators in parallel
   
   **Default**: ``true``
   
   **Example**: ``--no-parallel`` (to disable)

.. option:: --max-workers <number>

   **Description**: Maximum number of parallel workers
   
   **Default**: ``4``
   
   **Range**: 1-20
   
   **Example**: ``--max-workers 8``

.. option:: --timeout <seconds>

   **Description**: Timeout for individual evaluations
   
   **Default**: ``30``
   
   **Range**: 1-300
   
   **Example**: ``--timeout 60``

.. option:: --retry-failed

   **Description**: Retry failed evaluations
   
   **Default**: ``false``
   
   **Example**: ``--retry-failed``

.. option:: --max-retries <number>

   **Description**: Maximum number of retries for failed evaluations
   
   **Default**: ``3``
   
   **Range**: 1-10
   
   **Example**: ``--max-retries 5``

.. option:: --dry-run

   **Description**: Show what would be evaluated without actually running
   
   **Default**: ``false``
   
   **Use Case**: Testing evaluation queries
   
   **Example**: ``--dry-run``

.. option:: --save-results

   **Description**: Save evaluation results to HoneyHive
   
   **Default**: ``true``
   
   **Example**: ``--no-save-results`` (for testing)

.. option:: --output-file <path>

   **Description**: Save evaluation results to local file
   
   **Format**: JSON or CSV based on file extension
   
   **Example**: ``--output-file evaluation_results.json``

**honeyhive eval list**

.. option:: --evaluator <name>

   **Description**: Filter by evaluator name
   
   **Example**: ``--evaluator quality``

.. option:: --target-event-id <id>

   **Description**: Filter by target event ID
   
   **Example**: ``--target-event-id evt_abc123``

.. option:: --min-score <score>

   **Description**: Filter by minimum score
   
   **Format**: Numeric value (depends on evaluator scale)
   
   **Example**: ``--min-score 0.8``

.. option:: --max-score <score>

   **Description**: Filter by maximum score
   
   **Example**: ``--max-score 0.5``

.. option:: --status <status>

   **Description**: Filter by evaluation status
   
   **Values**: ``completed``, ``failed``, ``pending``, ``skipped``
   
   **Example**: ``--status completed``

Trace Analysis Commands
~~~~~~~~~~~~~~~~~~~~~~~

**honeyhive trace analyze**

.. option:: --time-window <window>

   **Description**: Time window for analysis
   
   **Values**:
   - ``1h`` - Last 1 hour
   - ``6h`` - Last 6 hours
   - ``24h`` - Last 24 hours
   - ``7d`` - Last 7 days
   - ``30d`` - Last 30 days
   - ``custom`` - Use start-time/end-time
   
   **Default**: ``24h``
   
   **Example**: ``--time-window 7d``

.. option:: --start-time <timestamp>

   **Description**: Custom start time for analysis
   
   **Format**: ISO 8601 timestamp
   
   **Example**: ``--start-time 2024-01-01T00:00:00Z``

.. option:: --end-time <timestamp>

   **Description**: Custom end time for analysis
   
   **Format**: ISO 8601 timestamp
   
   **Example**: ``--end-time 2024-01-31T23:59:59Z``

.. option:: --include-metrics

   **Description**: Include detailed performance metrics
   
   **Default**: ``false``
   
   **Example**: ``--include-metrics``

.. option:: --groupby <field>

   **Description**: Group analysis results by field
   
   **Values**: ``model``, ``provider``, ``event_type``, ``user_id``, ``session_id``, ``status``
   
   **Example**: ``--groupby model``

.. option:: --output-file <path>

   **Description**: Save analysis results to file
   
   **Formats**: JSON, YAML, CSV based on extension
   
   **Example**: ``--output-file analysis_results.json``

**honeyhive trace performance**

.. option:: --percentiles <list>

   **Description**: Comma-separated percentiles to calculate
   
   **Default**: ``50,90,95,99``
   
   **Format**: Numbers between 0-100
   
   **Example**: ``--percentiles 25,50,75,90,95,99``

.. option:: --metrics <list>

   **Description**: Performance metrics to analyze
   
   **Values**: ``latency``, ``tokens_per_second``, ``cost``, ``error_rate``, ``throughput``
   
   **Default**: All metrics
   
   **Example**: ``--metrics latency,error_rate``

Configuration Options
~~~~~~~~~~~~~~~~~~~~~

**honeyhive config set**

.. option:: <key> <value>

   **Description**: Configuration key-value pair
   
   **Available Keys**:
   - ``api_key`` - Default API key
   - ``base_url`` - Default base URL
   - ``default_project`` - Default project name
   - ``output_format`` - Default output format
   - ``verbose`` - Default verbose setting
   - ``timeout`` - Default timeout in seconds
   
   **Examples**:
   
   .. code-block:: bash
   
      # Set default project
      honeyhive config set default_project my-project
      
      # Set output format
      honeyhive config set output_format json
      
      # Set timeout
      honeyhive config set timeout 60

Advanced Options
----------------

Filtering and Search
~~~~~~~~~~~~~~~~~~~~

**Date/Time Formats**:

The CLI accepts various date and time formats:

- **ISO 8601**: ``2024-01-15T10:30:45Z``
- **ISO Date**: ``2024-01-15``
- **Relative**: ``-1h``, ``-24h``, ``-7d``, ``-30d``
- **Unix Timestamp**: ``1642253445``

**Examples**:

.. code-block:: bash

   # ISO 8601 format
   --start-time 2024-01-15T10:30:45Z
   
   # Simple date
   --start-date 2024-01-15
   
   # Relative time
   --start-time -24h

**Query Syntax**:

Advanced query syntax for filtering:

- **Field Filters**: ``field:value``
- **Range Queries**: ``field:>value``, ``field:<value``, ``field:>=value``, ``field:<=value``
- **Wildcard**: ``field:pattern*``
- **Regex**: ``field:/pattern/``
- **Arrays**: ``field:[value1,value2]``
- **Null Checks**: ``field:null``, ``field:!null``

**Examples**:

.. code-block:: bash

   # Range query
   --query "duration:>1000 AND duration:<5000"
   
   # Wildcard search
   --query "model:gpt* AND status:success"
   
   # Array filter
   --query "event_type:[model,tool]"
   
   # Null check
   --query "error:null"

Output Formatting
~~~~~~~~~~~~~~~~~

**Table Format Options**:

.. option:: --table-style <style>

   **Description**: Table display style
   
   **Values**: ``grid``, ``simple``, ``plain``, ``markdown``
   
   **Default**: ``grid``

.. option:: --max-width <width>

   **Description**: Maximum table width
   
   **Default**: Terminal width
   
   **Example**: ``--max-width 120``

.. option:: --truncate

   **Description**: Truncate long values in table cells
   
   **Default**: ``true``

**JSON Format Options**:

.. option:: --pretty

   **Description**: Pretty-print JSON output
   
   **Default**: ``true``

.. option:: --compact

   **Description**: Compact JSON output (no formatting)
   
   **Default**: ``false``

**CSV Format Options**:

.. option:: --delimiter <char>

   **Description**: CSV delimiter character
   
   **Default**: ``,``
   
   **Example**: ``--delimiter "|"``

.. option:: --quote-char <char>

   **Description**: CSV quote character
   
   **Default**: ``"``

.. option:: --escape-char <char>

   **Description**: CSV escape character
   
   **Default**: ``\``

.. option:: --no-header

   **Description**: Omit header row in CSV output
   
   **Default**: ``false``

Pagination Options
~~~~~~~~~~~~~~~~~~

.. option:: --page-size <number>

   **Description**: Number of items per page
   
   **Default**: ``50``
   
   **Range**: 1-1000

.. option:: --page <number>

   **Description**: Page number (1-based)
   
   **Default**: ``1``

.. option:: --all-pages

   **Description**: Fetch all pages automatically
   
   **Default**: ``false``
   
   **Warning**: Use with caution for large datasets

Performance Options
~~~~~~~~~~~~~~~~~~~

.. option:: --batch-size <number>

   **Description**: Batch size for bulk operations
   
   **Default**: Varies by command
   
   **Range**: 1-10000

.. option:: --rate-limit <number>

   **Description**: Rate limit (requests per second)
   
   **Default**: ``10``
   
   **Range**: 1-100

.. option:: --max-concurrent <number>

   **Description**: Maximum concurrent operations
   
   **Default**: ``4``
   
   **Range**: 1-20

.. option:: --timeout <seconds>

   **Description**: Request timeout
   
   **Default**: ``30``
   
   **Range**: 1-300

Debug Options
~~~~~~~~~~~~~

.. option:: --debug

   **Description**: Enable debug mode
   
   **Default**: ``false``
   
   **Behavior**:
   - Shows detailed API requests/responses
   - Includes stack traces for errors
   - Logs internal operations

.. option:: --trace-requests

   **Description**: Trace HTTP requests
   
   **Default**: ``false``
   
   **Use Case**: Debugging API issues

.. option:: --log-level <level>

   **Description**: Set log level
   
   **Values**: ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``, ``CRITICAL``
   
   **Default**: ``INFO``

.. option:: --log-file <path>

   **Description**: Write logs to file
   
   **Example**: ``--log-file honeyhive.log``

Option Precedence
-----------------

Options are resolved in this order (highest to lowest precedence):

1. **Command-line arguments** - Explicitly provided options
2. **Environment variables** - ``HH_*`` variables
3. **Configuration file** - ``~/.honeyhive/config.yaml``
4. **Default values** - Built-in defaults

**Example**:

.. code-block:: bash

   # Environment variable
   
   # Config file contains: default_project: "config-project"
   
   # Command line overrides both
   honeyhive event list # Uses: "cli-project"

Validation Rules
----------------

**API Key Format**:
- Must start with ``hh_``
- Must be 32+ characters
- Alphanumeric characters only

**Project Names**:
- 1-100 characters
- Alphanumeric, hyphens, underscores only
- Cannot start or end with hyphen/underscore

**Date/Time Values**:
- Must be valid ISO 8601 format
- Or relative format (``-1h``, ``-7d``)
- Future dates are allowed

**Numeric Ranges**:
- Positive integers for limits/offsets
- 0.0-1.0 for scores/percentiles
- Reasonable ranges for timeouts/batch sizes

**File Paths**:
- Must be valid for the operating system
- Directories must exist (for output files)
- Read permissions required (for input files)

See Also
--------

- :doc:`commands` - Complete command reference
- :doc:`../configuration/environment-vars` - Environment variable details
- :doc:`../../development/testing/ci-cd-integration` - CI/CD usage patterns
- :doc:`../../tutorials/01-setup-first-tracer` - Getting started guide
