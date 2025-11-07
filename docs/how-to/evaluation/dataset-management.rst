Using Datasets in Experiments
==============================

How do I manage test datasets for experiments?
----------------------------------------------

Use datasets created in HoneyHive UI or define them in code.

How do I use a dataset I created in the HoneyHive UI?
-----------------------------------------------------

**Pass dataset_id Instead of dataset List**

.. code-block:: python

   from honeyhive.experiments import evaluate
   
   # Use dataset from UI (by ID)
   result = evaluate(
       function=my_function,
       dataset_id="dataset_abc123",  # From HoneyHive UI
       evaluators=[my_evaluator],
       api_key="your-api-key",
       project="your-project"
   )

**Finding Your Dataset ID:**

1. Go to HoneyHive dashboard
2. Navigate to Datasets section
3. Click on your dataset
4. Copy the dataset ID from the URL or details page

When should I define datasets in code vs UI?
--------------------------------------------

**Choose Based on Use Case**

**Use Code-Defined** when:
- Iterating quickly during development
- Generating test data programmatically
- Dataset changes frequently
- Dataset is small (<100 items)

.. code-block:: python

   # Code-defined dataset
   dataset = [
       {"inputs": {...}, "ground_truth": {...}},
      {"inputs": {...}, "ground_truth": {...}}
  ]
  
  result = evaluate(function=my_function, dataset=dataset)  # ...more args

**Use UI-Managed** when:
- Dataset is large (>100 items)
- Multiple team members need access
- You want version control via UI
- Dataset is stable/standardized

.. code-block:: python

  # UI-managed dataset
  result = evaluate(function=my_function, dataset_id="dataset_123")  # ...more args

What are EXT- prefixed IDs?
---------------------------

**Automatically Generated for Code Datasets**

When you pass a ``dataset`` list (not ``dataset_id``), HoneyHive generates an external ID:

.. code-block:: python

  dataset = [{"inputs": {...}, "ground_truth": {...}}]
  
  result = evaluate(function=my_function, dataset=dataset)  # ...more args
  
  print(result.dataset_id)  # "EXT-abc123def456..."

The EXT- ID is deterministic - same dataset content = same ID.

This allows comparing runs on the same code-defined dataset.

How do I create a dataset in the HoneyHive UI?
----------------------------------------------

**Use the Datasets Interface**

1. **Navigate**: Go to Datasets in HoneyHive dashboard
2. **Create**: Click "New Dataset"
3. **Add Data**: 
   - Upload CSV/JSON file, or
   - Add datapoints manually, or
   - Curate from existing traces
4. **Save**: Give it a name and description
5. **Use**: Copy the dataset ID for your code

**CSV Format:**

.. code-block:: text

   inputs.question,inputs.context,ground_truth.answer
   "What is AI?","AI is...", "Artificial Intelligence..."
   "What is ML?","ML is...", "Machine Learning..."

**JSON Format:**

.. code-block:: json

   [
       {
           "inputs": {"question": "What is AI?", "context": "..."},
           "ground_truth": {"answer": "Artificial Intelligence..."}
       },
       {
           "inputs": {"question": "What is ML?", "context": "..."},
           "ground_truth": {"answer": "Machine Learning..."}
       }
   ]

How do I create a dataset from production traces?
-------------------------------------------------

**Use Trace Curation in UI**

1. Go to Traces in dashboard
2. Filter for good/interesting examples
3. Select traces you want
4. Click "Add to Dataset"
5. Choose existing dataset or create new one
6. Inputs and outputs automatically extracted

This is great for:
- Creating regression tests from production
- Building golden datasets
- Finding edge cases

How do I version my datasets?
-----------------------------

**Use Naming Conventions**

.. code-block:: python

   # Version in name
   result = evaluate(
       function=my_function,
       dataset_id="qa-dataset-v1",
       name="experiment-on-v1-dataset",
       api_key="your-api-key",
       project="your-project"
   )
   
   # Later, test on new version
   result = evaluate(
       function=my_function,
       dataset_id="qa-dataset-v2",
       name="experiment-on-v2-dataset",
       api_key="your-api-key",
       project="your-project"
   )

See Also
--------

- :doc:`running-experiments` - Use datasets in experiments
- :doc:`comparing-experiments` - Ensure same dataset for comparison
- :doc:`../../reference/experiments/utilities` - Dataset utility functions

