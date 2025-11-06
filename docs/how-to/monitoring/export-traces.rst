How to Export Traces
=====================

**Problem:** You need to export trace data from HoneyHive for analysis, backup, or integration with other tools.

**Solution:** Use the HoneyHive CLI or API to export traces in multiple formats.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

HoneyHive provides multiple ways to export trace data:

- **CLI Export**: Quick command-line exports for ad-hoc analysis
- **API Export**: Programmatic access for automated pipelines
- **Multiple Formats**: JSON, JSONL, CSV, Parquet for different use cases
- **Flexible Filtering**: Time ranges, operations, status filters

When to Export Traces
---------------------

**Common Use Cases:**

- **Data Analysis**: Export for Jupyter notebooks, pandas analysis
- **Backup & Archival**: Long-term storage of trace data
- **Compliance**: Audit trail requirements
- **ML Training**: Export traces for model training datasets
- **Debugging**: Detailed offline analysis of specific issues
- **Cost Analysis**: Export for billing and usage analytics

Export Methods
--------------

CLI Export (Recommended for Ad-Hoc)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Basic Export:**

.. code-block:: bash

   # Export all traces from last 24 hours
   honeyhive export traces traces.jsonl
   
   # Export as CSV
   honeyhive export traces traces.csv --format csv
   
   # Export with time range
   honeyhive export traces traces.jsonl \
     --since "2024-01-20T00:00:00Z" \
     --until "2024-01-21T00:00:00Z"

**Filtered Exports:**

.. code-block:: bash

   # Export only error traces
   honeyhive trace search --query "status:error" --format json > errors.json
   
   # Export specific operations
   honeyhive trace search \
     --query "operation:llm_call" \
     --format jsonl > llm_calls.jsonl
   
   # Export with metadata
   honeyhive export traces full_traces.jsonl --include all

.. note::
   **CLI Installation Required**
   
   Install the HoneyHive CLI: ``pip install honeyhive[cli]``

API Export (Recommended for Automation)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Using Python SDK:**

.. code-block:: python

   from honeyhive import HoneyHive
   import json
   from datetime import datetime, timedelta
   
   # Initialize client
   client = HoneyHive(api_key="your-api-key")
   
   # Query traces from last 7 days
   end_date = datetime.now()
   start_date = end_date - timedelta(days=7)
   
   # Get sessions (traces) with filtering
   sessions = client.sessions.get_sessions(
       project="your-project",
       filters={
           "start_time": {
               "gte": start_date.isoformat(),
               "lte": end_date.isoformat()
           },
           "source": "production"
       },
       limit=1000  # Adjust as needed
   )
   
   # Export to file
   with open("traces_export.jsonl", "w") as f:
       for session in sessions:
           f.write(json.dumps(session.model_dump()) + "\n")
   
   print(f"✅ Exported {len(sessions)} traces")

**Paginated Export (Large Datasets):**

.. code-block:: python

   from honeyhive import HoneyHive
   import json
   
   client = HoneyHive(api_key="your-api-key")
   
   def export_all_traces(project: str, output_file: str):
       """Export all traces with pagination."""
       page = 0
       page_size = 100
       total_exported = 0
       
       with open(output_file, "w") as f:
           while True:
               # Get page of sessions
               sessions = client.sessions.get_sessions(
                   project=project,
                   offset=page * page_size,
                   limit=page_size
               )
               
               if not sessions:
                   break  # No more data
               
               # Write to file
               for session in sessions:
                   f.write(json.dumps(session.model_dump()) + "\n")
                   total_exported += 1
               
               print(f"Exported page {page + 1} ({total_exported} traces so far)")
               page += 1
       
       print(f"✅ Total exported: {total_exported} traces")
   
   # Run export
   export_all_traces("your-project", "all_traces.jsonl")

Export Formats
--------------

JSONL (Recommended)
~~~~~~~~~~~~~~~~~~~

**Best for:**

- Large datasets
- Streaming processing
- Line-by-line parsing

.. code-block:: bash

   honeyhive export traces traces.jsonl --format jsonl

**Advantages:**

- One trace per line
- Easy to stream/process incrementally
- Standard format for data pipelines

JSON
~~~~

**Best for:**

- Small datasets
- Pretty printing
- Direct API integration

.. code-block:: bash

   honeyhive export traces traces.json --format json

**Structure:**

.. code-block:: javascript

   {
     "traces": [
       {
         "session_id": "session_123",
         "start_time": "2024-01-20T10:30:00Z",
         "spans": []  // Array of span objects
       }
     ]
   }

CSV
~~~

**Best for:**

- Excel analysis
- Spreadsheet tools
- Business intelligence

.. code-block:: bash

   honeyhive export traces traces.csv --format csv

**Note**: Complex nested data is flattened or JSON-encoded in CSV format.

Parquet
~~~~~~~

**Best for:**

- Data lakes
- Big data processing
- Columnar analytics

.. code-block:: bash

   honeyhive export traces traces.parquet --format parquet

**Advantages:**

- Efficient compression
- Fast columnar queries
- Industry standard for analytics

Advanced Export Patterns
-------------------------

Filtered Export by Status
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Export only successful traces
   sessions = client.sessions.get_sessions(
       project="your-project",
       filters={"status": "success"},
       limit=1000
   )

Export with Span Details
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   import json
   
   client = HoneyHive(api_key="your-api-key")
   
   def export_with_events(project: str, session_id: str):
       """Export session with all events (spans)."""
       # Get session details
       session = client.sessions.get_session(session_id)
       
       # Get all events for this session
       events = client.events.get_events(
           project=project,
           filters={"session_id": session_id}
       )
       
       # Combine data
       export_data = {
           "session": session.model_dump(),
           "events": [event.model_dump() for event in events]
       }
       
       with open(f"session_{session_id}.json", "w") as f:
           json.dump(export_data, f, indent=2)
       
       return export_data
   
   # Export specific session with all spans
   export_with_events("your-project", "session_abc123")

Scheduled Exports
~~~~~~~~~~~~~~~~~

**Daily Export Script:**

.. code-block:: python

   #!/usr/bin/env python3
   """Daily trace export for archival."""
   from honeyhive import HoneyHive
   import json
   from datetime import datetime, timedelta
   
   def daily_export():
       client = HoneyHive(api_key="your-api-key")
       
       # Export yesterday's data
       yesterday = datetime.now() - timedelta(days=1)
       start = yesterday.replace(hour=0, minute=0, second=0)
       end = yesterday.replace(hour=23, minute=59, second=59)
       
       sessions = client.sessions.get_sessions(
           project="production-app",
           filters={
               "start_time": {
                   "gte": start.isoformat(),
                   "lte": end.isoformat()
               }
           }
       )
       
       # Save to dated file
       filename = f"traces_{yesterday.strftime('%Y%m%d')}.jsonl"
       with open(filename, "w") as f:
           for session in sessions:
               f.write(json.dumps(session.model_dump()) + "\n")
       
       print(f"✅ Exported {len(sessions)} traces to {filename}")
   
   if __name__ == "__main__":
       daily_export()

**Cron Schedule:**

.. code-block:: bash

   # Run daily at 1 AM
   0 1 * * * /path/to/venv/bin/python /path/to/daily_export.py

Export Performance Tips
-----------------------

**For Large Datasets:**

1. **Use Pagination**: Process in chunks of 100-1000 traces
2. **Use JSONL**: Faster than JSON for large datasets
3. **Filter by Time**: Export specific time ranges
4. **Use Compression**: Gzip output files for storage

.. code-block:: python

   import gzip
   import json
   
   # Export with compression
   with gzip.open("traces.jsonl.gz", "wt") as f:
       for session in sessions:
           f.write(json.dumps(session.model_dump()) + "\n")

**For Real-Time Export:**

.. code-block:: python

   import time
   from honeyhive import HoneyHive
   
   client = HoneyHive(api_key="your-api-key")
   last_export_time = datetime.now()
   
   while True:
       # Export new traces every 5 minutes
       time.sleep(300)
       
       now = datetime.now()
       sessions = client.sessions.get_sessions(
           project="your-project",
           filters={
               "start_time": {"gte": last_export_time.isoformat()}
           }
       )
       
       # Process new sessions...
       last_export_time = now

Troubleshooting
---------------

**Export Fails with "Too Many Results":**

Use pagination:

.. code-block:: python

   # Bad: Trying to get everything at once
   sessions = client.sessions.get_sessions(limit=100000)  # ❌ Too large
   
   # Good: Use pagination
   for page in range(0, 1000, 100):
       sessions = client.sessions.get_sessions(offset=page, limit=100)

**Missing Span Data:**

Ensure you're exporting both sessions and events:

.. code-block:: python

   # Export sessions (traces)
   sessions = client.sessions.get_sessions(project="your-project")
   
   # Also export events (spans) for each session
   for session in sessions:
       events = client.events.get_events(
           project="your-project",
           filters={"session_id": session.session_id}
       )

**Slow Exports:**

1. Reduce time range
2. Use filters to limit results
3. Export during off-peak hours
4. Use JSONL instead of JSON

Next Steps
----------

- :doc:`../advanced-tracing/index` - Advanced tracing patterns
- :doc:`/reference/cli/index` - Complete CLI reference

**Key Takeaway:** HoneyHive provides flexible export options for any use case - from ad-hoc CLI exports to automated production pipelines. Choose the right format and method based on your needs. ✨

