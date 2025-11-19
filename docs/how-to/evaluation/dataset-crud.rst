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
   
   # Initialize client
   client = HoneyHive(api_key="your-api-key")
   
   # Define dataset
   dataset_data = {
       "name": "qa-test-set-v1",
       "description": "Q&A test cases for v1 evaluation",
       "project": "your-project",
       "datapoints": [
           {
               "inputs": {"question": "What is AI?"},
               "ground_truth": {"answer": "Artificial Intelligence"}
           },
           {
               "inputs": {"question": "What is ML?"},
               "ground_truth": {"answer": "Machine Learning"}
           }
       ]
   }
   
   # Create dataset
   dataset = client.datasets.create_dataset(dataset_data)
   
   print(f"✅ Created dataset: {dataset.dataset_id}")
   print(f"   Name: {dataset.name}")
   print(f"   Datapoints: {len(dataset.datapoints)}")

Create from External Data
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import pandas as pd
   from honeyhive import HoneyHive
   
   # Load data from CSV
   df = pd.read_csv("test_cases.csv")
   
   # Convert to HoneyHive format
   datapoints = []
   for _, row in df.iterrows():
       datapoints.append({
           "inputs": {"question": row["question"]},
           "ground_truth": {"answer": row["answer"]}
       })
   
   # Create dataset
   client = HoneyHive(api_key="your-api-key")
   dataset = client.datasets.create_dataset({
       "name": "imported-from-csv",
       "description": f"Imported {len(datapoints)} test cases",
       "project": "your-project",
       "datapoints": datapoints
   })
   
   print(f"✅ Imported {len(datapoints)} datapoints")

Create from Production Traces
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
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
   
   # Convert to dataset format
   datapoints = []
   for session in sessions:
       datapoints.append({
           "inputs": session.inputs,
           "ground_truth": session.outputs  # Use actual output as ground truth
       })
   
   # Create regression test dataset
   dataset = client.datasets.create_dataset({
       "name": f"regression-tests-{datetime.now().strftime('%Y%m%d')}",
       "description": "Regression test cases from production",
       "project": "your-project",
       "datapoints": datapoints
   })
   
   print(f"✅ Created regression dataset with {len(datapoints)} cases")

Updating Datasets
-----------------

Update Dataset Metadata
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   from honeyhive.sdk.models import DatasetUpdate
   
   client = HoneyHive(api_key="your-api-key")
   
   # Update dataset name and description
   updated = client.datasets.update_dataset(
       dataset_id="dataset_abc123",
       request=DatasetUpdate(
           name="qa-test-set-v2",  # New name
           description="Updated Q&A test cases for v2"
       )
   )
   
   print(f"✅ Updated dataset: {updated.name}")

Add Datapoints to Existing Dataset
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   
   client = HoneyHive(api_key="your-api-key")
   
   # Get current dataset
   dataset = client.datasets.get_dataset("dataset_abc123")
   
   # Add new datapoints
   new_datapoints = [
       {
           "inputs": {"question": "What is DL?"},
           "ground_truth": {"answer": "Deep Learning"}
       }
   ]
   
   # Combine with existing
   all_datapoints = dataset.datapoints + new_datapoints
   
   # Update dataset
   updated = client.datasets.update_dataset_from_dict(
       dataset_id=dataset.dataset_id,
       dataset_data={
           "datapoints": all_datapoints
       }
   )
   
   print(f"✅ Added {len(new_datapoints)} datapoints")
   print(f"   Total: {len(updated.datapoints)} datapoints")

Remove Datapoints
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   
   client = HoneyHive(api_key="your-api-key")
   
   # Get current dataset
   dataset = client.datasets.get_dataset("dataset_abc123")
   
   # Filter out unwanted datapoints
   filtered_datapoints = [
       dp for dp in dataset.datapoints
       if "question" in dp.get("inputs", {})  # Keep only valid ones
   ]
   
   # Update with filtered list
   updated = client.datasets.update_dataset_from_dict(
       dataset_id=dataset.dataset_id,
       dataset_data={"datapoints": filtered_datapoints}
   )
   
   removed_count = len(dataset.datapoints) - len(filtered_datapoints)
   print(f"✅ Removed {removed_count} invalid datapoints")

Deleting Datasets
-----------------

Delete Single Dataset
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   
   client = HoneyHive(api_key="your-api-key")
   
   # Delete dataset
   success = client.datasets.delete_dataset("dataset_abc123")
   
   if success:
       print("✅ Dataset deleted successfully")
   else:
       print("❌ Failed to delete dataset")

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
       success = client.datasets.delete_dataset(dataset_id)
       status = "✅" if success else "❌"
       print(f"{status} {dataset_id}")

Cleanup Old Datasets
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   from datetime import datetime, timedelta
   
   client = HoneyHive(api_key="your-api-key")
   
   # Get all datasets
   datasets = client.datasets.list_datasets(project="your-project")
   
   # Find datasets older than 30 days
   cutoff_date = datetime.now() - timedelta(days=30)
   
   for dataset in datasets:
       # Check if dataset is old (if created_at is available)
       if hasattr(dataset, 'created_at'):
           created = datetime.fromisoformat(dataset.created_at)
           if created < cutoff_date:
               print(f"Deleting old dataset: {dataset.name} (created {created.date()})")
               client.datasets.delete_dataset(dataset.dataset_id)

Listing & Querying Datasets
----------------------------

List All Datasets
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   
   client = HoneyHive(api_key="your-api-key")
   
   # Get all datasets for project
   datasets = client.datasets.list_datasets(project="your-project")
   
   print(f"Found {len(datasets)} datasets:")
   for dataset in datasets:
       print(f"  - {dataset.name} ({len(dataset.datapoints)} datapoints)")

Get Specific Dataset
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   
   client = HoneyHive(api_key="your-api-key")
   
   # Get dataset details
   dataset = client.datasets.get_dataset("dataset_abc123")
   
   print(f"Dataset: {dataset.name}")
   print(f"Description: {dataset.description}")
   print(f"Datapoints: {len(dataset.datapoints)}")
   print(f"Project: {dataset.project}")
   
   # Access datapoints
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
   dataset = client.datasets.list_datasets(
       project="your-project",
       name="qa-dataset-v1"
   )
   
   # Filter by dataset type
   eval_datasets = client.datasets.list_datasets(
       project="your-project",
       dataset_type="evaluation"
   )
   
   # Get specific dataset by ID
   dataset = client.datasets.list_datasets(
       dataset_id="663876ec4611c47f4970f0c3"
   )
   
   # Include datapoints in response (single query)
   dataset_with_data = client.datasets.list_datasets(
       dataset_id="663876ec4611c47f4970f0c3",
       include_datapoints=True
   )[0]

**Client-side filtering (for pattern matching):**

.. code-block:: python

   # For partial matches, fetch and filter client-side
   all_datasets = client.datasets.list_datasets(project="your-project")
   qa_datasets = [ds for ds in all_datasets if "qa-" in ds.name.lower()]
   
   print(f"Found {len(qa_datasets)} Q&A datasets:")
   for dataset in qa_datasets:
       print(f"  - {dataset.name}")

.. note::
   Server-side filtering is more efficient for large projects with 100+ datasets.
   Use ``name`` for exact matches and ``dataset_type`` or ``dataset_id`` for 
   targeted queries.

Advanced Patterns
-----------------

Versioned Datasets
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   from datetime import datetime
   
   client = HoneyHive(api_key="your-api-key")
   
   def create_versioned_dataset(base_name: str, datapoints: list):
       """Create dataset with version timestamp."""
       version = datetime.now().strftime("%Y%m%d_%H%M%S")
       name = f"{base_name}-v{version}"
       
       dataset = client.datasets.create_dataset({
           "name": name,
           "description": f"Version {version} of {base_name}",
           "project": "your-project",
           "datapoints": datapoints
       })
       
       return dataset
   
   # Usage
   dataset = create_versioned_dataset("qa-tests", datapoints)
   print(f"✅ Created: {dataset.name}")

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
       dataset = client.datasets.create_dataset(dataset_data)
   else:
       print("❌ Validation errors:")
       for error in errors:
           print(f"  - {error}")

Sync from External Source
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from honeyhive import HoneyHive
   import requests
   
   def sync_dataset_from_url(dataset_id: str, url: str):
       """Sync dataset from external API."""
       client = HoneyHive(api_key="your-api-key")
       
       # Fetch from external source
       response = requests.get(url)
       external_data = response.json()
       
       # Convert to HoneyHive format
       datapoints = [
           {
               "inputs": item["input"],
               "ground_truth": item["expected_output"]
           }
           for item in external_data
       ]
       
       # Update dataset
       updated = client.datasets.update_dataset_from_dict(
           dataset_id=dataset_id,
           dataset_data={"datapoints": datapoints}
       )
       
       print(f"✅ Synced {len(datapoints)} datapoints from {url}")
   
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
   datasets = client.datasets.list_datasets(project="your-project")
   for ds in datasets:
       print(f"{ds.name}: {ds.dataset_id}")

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

