Managing Datasets in HoneyHive
================================

**Problem:** You need to create, update, or delete datasets in HoneyHive programmatically for automated workflows.

**Solution:** Use the HoneyHive API client to manage datasets through the SDK.

.. contents:: Table of Contents
   :local:
   :depth: 2

Overview
--------

HoneyHive provides API methods for complete dataset lifecycle management:

- **Create**: Upload new datasets programmatically
- **Update**: Modify existing datasets (name, description, datapoints)
- **Delete**: Remove datasets when no longer needed
- **List**: Browse available datasets
- **Get**: Retrieve specific dataset details

When to Use Programmatic Dataset Management
--------------------------------------------

**Use API/SDK** when:

- Automating dataset creation in CI/CD pipelines
- Generating test datasets from production data
- Syncing datasets from external sources
- Batch updating multiple datasets
- Building custom dataset management tools

**Use Dashboard** when:

- Creating one-off test datasets manually
- Exploring and visualizing dataset contents
- Quick edits to individual datapoints
- Team collaboration on test cases

Creating Datasets
-----------------

Upload New Dataset
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   from honeyhive.models import (
       CreateDatasetRequest,
       AddDatapointsToDatasetRequest,
       DatapointMapping,
   )
   
   # Initialize client
   client = HoneyHive(api_key="your-api-key")
   
   # Step 1: Create an empty dataset
   response = client.datasets.create(CreateDatasetRequest(
       name="qa-test-set-v1",
       description="Q&A test cases for v1 evaluation",
   ))
   dataset_id = response.result.insertedId
   print(f"✅ Created dataset: {dataset_id}")
   
   # Step 2: Add datapoints to the dataset
   add_response = client.datasets.add_datapoints(
       dataset_id,
       AddDatapointsToDatasetRequest(
           data=[
               {"question": "What is AI?", "answer": "Artificial Intelligence"},
               {"question": "What is ML?", "answer": "Machine Learning"},
           ],
           mapping=DatapointMapping(
               inputs=["question"],      # Map 'question' field to inputs
               ground_truth=["answer"],  # Map 'answer' field to ground_truth
           )
       )
   )
   print(f"   Added {len(add_response.datapoint_ids)} datapoints")

Create from External Data
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import pandas as pd
   from honeyhive import HoneyHive
   from honeyhive.models import (
       CreateDatasetRequest,
       AddDatapointsToDatasetRequest,
       DatapointMapping,
   )
   
   # Load data from CSV
   df = pd.read_csv("test_cases.csv")
   
   # Convert to list of dicts
   data_rows = df.to_dict(orient="records")
   
   # Create dataset and add datapoints
   client = HoneyHive(api_key="your-api-key")
   
   # Step 1: Create empty dataset
   response = client.datasets.create(CreateDatasetRequest(
       name="imported-from-csv",
       description=f"Imported {len(data_rows)} test cases",
   ))
   dataset_id = response.result.insertedId
   
   # Step 2: Add datapoints with field mapping
   client.datasets.add_datapoints(
       dataset_id,
       AddDatapointsToDatasetRequest(
           data=data_rows,
           mapping=DatapointMapping(
               inputs=["question"],      # CSV column for inputs
               ground_truth=["answer"],  # CSV column for ground_truth
           )
       )
   )
   
   print(f"✅ Imported {len(data_rows)} datapoints to dataset {dataset_id}")

Create from Production Traces
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   from honeyhive.models import (
       CreateDatasetRequest,
       AddDatapointsToDatasetRequest,
       DatapointMapping,
   )
   from datetime import datetime, timedelta
   
   client = HoneyHive(api_key="your-api-key")
   
   # Get production traces from last week
   end_date = datetime.now()
   start_date = end_date - timedelta(days=7)
   
   sessions = client.sessions.get_sessions(
       project="production-app",
       filters={
           "start_time": {"gte": start_date.isoformat()},
           "status": "success"  # Only successful traces
       },
       limit=100
   )
   
   # Convert to data format for add_datapoints
   data_rows = []
   for session in sessions:
       data_rows.append({
           "inputs": session.inputs,
           "outputs": session.outputs  # Use actual output as ground truth
       })
   
   # Create dataset and add datapoints
   response = client.datasets.create(CreateDatasetRequest(
       name=f"regression-tests-{datetime.now().strftime('%Y%m%d')}",
       description="Regression test cases from production",
   ))
   dataset_id = response.result.insertedId
   
   client.datasets.add_datapoints(
       dataset_id,
       AddDatapointsToDatasetRequest(
           data=data_rows,
           mapping=DatapointMapping(
               inputs=["inputs"],
               ground_truth=["outputs"],
           )
       )
   )
   
   print(f"✅ Created regression dataset with {len(data_rows)} cases")

Adding Datapoints to Datasets
-----------------------------

Bulk Add Datapoints
~~~~~~~~~~~~~~~~~~~

Use ``add_datapoints`` to add multiple datapoints to an existing dataset. This is the recommended way to populate datasets after creation.

.. code-block:: python

   from honeyhive import HoneyHive
   from honeyhive.models import (
       AddDatapointsToDatasetRequest,
       DatapointMapping,
   )
   
   client = HoneyHive(api_key="your-api-key")
   
   # Add datapoints to an existing dataset
   response = client.datasets.add_datapoints(
       "your-dataset-id",
       AddDatapointsToDatasetRequest(
           data=[
               {"question": "What is AI?", "answer": "Artificial Intelligence"},
               {"question": "What is ML?", "answer": "Machine Learning"},
               {"question": "What is DL?", "answer": "Deep Learning"},
           ],
           mapping=DatapointMapping(
               inputs=["question"],      # Field(s) to map to inputs
               ground_truth=["answer"],  # Field(s) to map to ground_truth
           )
       )
   )
   
   print(f"✅ Added {len(response.datapoint_ids)} datapoints")

Understanding DatapointMapping
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``DatapointMapping`` tells HoneyHive how to transform your raw data into the standard datapoint format (``inputs`` and ``ground_truth``).

.. code-block:: python

   from honeyhive.models import DatapointMapping
   
   # Simple mapping: single field for inputs and ground_truth
   simple_mapping = DatapointMapping(
       inputs=["question"],
       ground_truth=["answer"],
   )
   # Data: {"question": "...", "answer": "..."}
   # Result: {"inputs": {"question": "..."}, "ground_truth": {"answer": "..."}}
   
   # Multiple fields for inputs
   multi_input_mapping = DatapointMapping(
       inputs=["context", "question"],  # Both fields go into inputs
       ground_truth=["answer"],
   )
   # Data: {"context": "...", "question": "...", "answer": "..."}
   # Result: {"inputs": {"context": "...", "question": "..."}, "ground_truth": {"answer": "..."}}

Add Datapoints from CSV
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import pandas as pd
   from honeyhive import HoneyHive
   from honeyhive.models import AddDatapointsToDatasetRequest, DatapointMapping
   
   client = HoneyHive(api_key="your-api-key")
   
   # Load CSV data
   df = pd.read_csv("test_cases.csv")
   # CSV columns: question, context, expected_answer
   
   # Add to existing dataset
   response = client.datasets.add_datapoints(
       "your-dataset-id",
       AddDatapointsToDatasetRequest(
           data=df.to_dict(orient="records"),
           mapping=DatapointMapping(
               inputs=["question", "context"],
               ground_truth=["expected_answer"],
           )
       )
   )
   
   print(f"✅ Imported {len(response.datapoint_ids)} rows from CSV")

Add Datapoints Incrementally
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   from honeyhive.models import AddDatapointsToDatasetRequest, DatapointMapping
   
   client = HoneyHive(api_key="your-api-key")
   dataset_id = "your-dataset-id"
   
   # Add datapoints in batches (useful for large datasets)
   all_data = [...]  # Your large dataset
   batch_size = 100
   
   for i in range(0, len(all_data), batch_size):
       batch = all_data[i:i + batch_size]
       response = client.datasets.add_datapoints(
           dataset_id,
           AddDatapointsToDatasetRequest(
               data=batch,
               mapping=DatapointMapping(
                   inputs=["question"],
                   ground_truth=["answer"],
               )
           )
       )
       print(f"✅ Added batch {i // batch_size + 1}: {len(response.datapoint_ids)} datapoints")

Updating Datasets
-----------------

Update Dataset Metadata
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   from honeyhive.models import UpdateDatasetRequest
   
   client = HoneyHive(api_key="your-api-key")
   
   # Update dataset name and description
   response = client.datasets.update(UpdateDatasetRequest(
       dataset_id="dataset_abc123",
       name="qa-test-set-v2",  # New name
       description="Updated Q&A test cases for v2"
   ))
   
   print(f"✅ Updated dataset")

Add Datapoints to Existing Dataset
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the ``add_datapoints`` method to append new datapoints to an existing dataset:

.. code-block:: python

   from honeyhive import HoneyHive
   from honeyhive.models import AddDatapointsToDatasetRequest, DatapointMapping
   
   client = HoneyHive(api_key="your-api-key")
   
   # Add new datapoints to existing dataset
   response = client.datasets.add_datapoints(
       "dataset_abc123",
       AddDatapointsToDatasetRequest(
           data=[
               {"question": "What is DL?", "answer": "Deep Learning"},
               {"question": "What is NLP?", "answer": "Natural Language Processing"},
           ],
           mapping=DatapointMapping(
               inputs=["question"],
               ground_truth=["answer"],
           )
       )
   )
   
   print(f"✅ Added {len(response.datapoint_ids)} datapoints")

Remove Datapoints
~~~~~~~~~~~~~~~~~

Use ``remove_datapoint`` to remove individual datapoints from a dataset:

.. code-block:: python

   from honeyhive import HoneyHive
   
   client = HoneyHive(api_key="your-api-key")
   
   # Remove a specific datapoint from a dataset
   response = client.datasets.remove_datapoint(
       dataset_id="dataset_abc123",
       datapoint_id="datapoint_xyz789"
   )
   
   print(f"✅ Removed datapoint from dataset")

Deleting Datasets
-----------------

Delete Single Dataset
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   
   client = HoneyHive(api_key="your-api-key")
   
   # Delete dataset
   response = client.datasets.delete("dataset_abc123")
   
   print("✅ Dataset deleted successfully")

Delete Multiple Datasets
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   
   client = HoneyHive(api_key="your-api-key")
   
   # List of dataset IDs to delete
   datasets_to_delete = [
       "dataset_old_v1",
       "dataset_old_v2",
       "dataset_temp_test"
   ]
   
   # Delete each
   for dataset_id in datasets_to_delete:
       try:
           client.datasets.delete(dataset_id)
           print(f"✅ {dataset_id}")
       except Exception as e:
           print(f"❌ {dataset_id}: {e}")

Cleanup Old Datasets
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   from datetime import datetime, timedelta
   
   client = HoneyHive(api_key="your-api-key")
   
   # Get all datasets
   response = client.datasets.list()
   
   # Find datasets older than 30 days
   cutoff_date = datetime.now() - timedelta(days=30)
   
   for dataset in response.datasets:
       # Check if dataset is old (if created_at is available)
       created_at = getattr(dataset, 'created_at', None)
       if created_at:
           created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
           if created < cutoff_date:
               print(f"Deleting old dataset: {dataset.name} (created {created.date()})")
               client.datasets.delete(dataset.id)

Listing & Querying Datasets
----------------------------

List All Datasets
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   
   client = HoneyHive(api_key="your-api-key")
   
   # Get all datasets
   datasets = client.datasets.list()
   
   print(f"Found {len(datasets.datasets)} datasets:")
   for dataset in datasets.datasets:
       print(f"  - {dataset.name} (ID: {dataset.id})")

Get Specific Dataset
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   
   client = HoneyHive(api_key="your-api-key")
   
   # Get dataset by ID (with datapoints included)
   response = client.datasets.list(
       dataset_id="dataset_abc123",
       include_datapoints=True
   )
   
   if response.datasets:
       dataset = response.datasets[0]
       print(f"Dataset: {dataset.name}")
       print(f"Description: {dataset.description}")
       
       # Access datapoints if included
       if hasattr(dataset, 'datapoints') and dataset.datapoints:
           print(f"Datapoints: {len(dataset.datapoints)}")
           for i, dp in enumerate(dataset.datapoints[:3]):  # First 3
               print(f"\nDatapoint {i+1}:")
               print(f"  Inputs: {dp.get('inputs')}")
               print(f"  Ground Truth: {dp.get('ground_truth')}")

Find Datasets by Name
~~~~~~~~~~~~~~~~~~~~~~

**Server-side filtering (recommended for large projects):**

.. code-block:: python

   from honeyhive import HoneyHive
   
   client = HoneyHive(api_key="your-api-key")
   
   # Filter by exact name (server-side - fast and efficient!)
   datasets = client.datasets.list(name="qa-dataset-v1")
   
   # Get specific dataset by ID
   dataset = client.datasets.list(dataset_id="663876ec4611c47f4970f0c3")
   
   # Include datapoints in response (single query)
   dataset_with_data = client.datasets.list(
       dataset_id="663876ec4611c47f4970f0c3",
       include_datapoints=True
   )

**Client-side filtering (for pattern matching):**

.. code-block:: python

   # For partial matches, fetch and filter client-side
   all_datasets = client.datasets.list()
   qa_datasets = [ds for ds in all_datasets.datasets if "qa-" in ds.name.lower()]
   
   print(f"Found {len(qa_datasets)} Q&A datasets:")
   for dataset in qa_datasets:
       print(f"  - {dataset.name}")

.. note::
   Server-side filtering is more efficient for large projects with 100+ datasets.
   Use ``name`` for exact matches or ``dataset_id`` for targeted queries.

Advanced Patterns
-----------------

Versioned Datasets
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   from honeyhive.models import (
       CreateDatasetRequest,
       AddDatapointsToDatasetRequest,
       DatapointMapping,
   )
   from datetime import datetime
   
   client = HoneyHive(api_key="your-api-key")
   
   def create_versioned_dataset(base_name: str, data: list, mapping: DatapointMapping):
       """Create dataset with version timestamp."""
       version = datetime.now().strftime("%Y%m%d_%H%M%S")
       name = f"{base_name}-v{version}"
       
       # Create dataset
       response = client.datasets.create(CreateDatasetRequest(
           name=name,
           description=f"Version {version} of {base_name}",
       ))
       dataset_id = response.result.insertedId
       
       # Add datapoints
       client.datasets.add_datapoints(
           dataset_id,
           AddDatapointsToDatasetRequest(data=data, mapping=mapping)
       )
       
       return dataset_id, name
   
   # Usage
   dataset_id, name = create_versioned_dataset(
       "qa-tests",
       data=[{"question": "What is AI?", "answer": "Artificial Intelligence"}],
       mapping=DatapointMapping(inputs=["question"], ground_truth=["answer"])
   )
   print(f"✅ Created: {name} ({dataset_id})")

Dataset Validation
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def validate_dataset(datapoints: list) -> tuple[bool, list]:
       """Validate dataset format before upload."""
       errors = []
       
       for i, dp in enumerate(datapoints):
           # Check required fields
           if "inputs" not in dp:
               errors.append(f"Datapoint {i}: missing 'inputs'")
           
           if "ground_truth" not in dp:
               errors.append(f"Datapoint {i}: missing 'ground_truth'")
           
           # Check inputs is dict
           if not isinstance(dp.get("inputs"), dict):
               errors.append(f"Datapoint {i}: 'inputs' must be dict")
       
       is_valid = len(errors) == 0
       return is_valid, errors
   
   # Usage
   is_valid, errors = validate_dataset(datapoints)
   if is_valid:
       response = client.datasets.create(CreateDatasetRequest(name="validated-dataset"))
       # Then add datapoints...
   else:
       print("❌ Validation errors:")
       for error in errors:
           print(f"  - {error}")

Sync from External Source
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   from honeyhive.models import AddDatapointsToDatasetRequest, DatapointMapping
   import requests
   
   def sync_dataset_from_url(dataset_id: str, url: str):
       """Sync dataset from external API."""
       client = HoneyHive(api_key="your-api-key")
       
       # Fetch from external source
       response = requests.get(url)
       external_data = response.json()
       
       # Add datapoints to dataset
       add_response = client.datasets.add_datapoints(
           dataset_id,
           AddDatapointsToDatasetRequest(
               data=external_data,
               mapping=DatapointMapping(
                   inputs=["input"],
                   ground_truth=["expected_output"],
               )
           )
       )
       
       print(f"✅ Synced {len(add_response.datapoint_ids)} datapoints from {url}")
   
   # Usage
   sync_dataset_from_url(
       "dataset_abc123",
       "https://api.example.com/test-cases"
   )

Best Practices
--------------

**Naming Conventions:**

- Use descriptive names: ``qa-customer-support-v1``
- Include version numbers: ``regression-tests-20240120``
- Use prefixes for categorization: ``prod-``, ``test-``, ``dev-``

**Dataset Size:**

- Keep datasets focused (50-500 datapoints ideal)
- Split large datasets into categories
- Use pagination when listing many datasets

**Validation:**

- Always validate datapoints before upload
- Check for required fields (``inputs``, ``ground_truth``)
- Verify data types match expectations

**Version Control:**

- Create new datasets for major changes
- Use timestamps or version numbers in names
- Keep old versions for comparison

**Cleanup:**

- Regularly delete unused datasets
- Archive old versions
- Document dataset purposes in descriptions

Troubleshooting
---------------

**"Dataset not found" error:**

Verify the dataset_id:

.. code-block:: python

   # List all datasets to find correct ID
   datasets = client.datasets.list()
   for ds in datasets.datasets:
       print(f"{ds.name}: {ds.id}")

**Update fails with validation error:**

Ensure datapoints are properly formatted:

.. code-block:: python

   # Each datapoint must have inputs and ground_truth
   datapoint = {
       "inputs": {"key": "value"},        # Required
       "ground_truth": {"expected": "value"}  # Required
   }

**Delete fails:**

Check if dataset is being used in active experiments:

.. code-block:: python

   # Datasets used in experiments may be protected
   # Check experiment references before deleting

Next Steps
----------

- :doc:`running-experiments` - Use datasets in experiments
- :doc:`dataset-management` - UI-based dataset management

**Key Takeaway:** Programmatic dataset management enables automated testing workflows, data syncing, and CI/CD integration. Use the SDK for automation and the dashboard for manual exploration. ✨

