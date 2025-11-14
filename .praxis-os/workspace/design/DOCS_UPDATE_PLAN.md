# Documentation Update Plan - V1.0 Experiments

## 🎯 Problem Analysis

### Current Issues

1. **Missing Tutorial**: No getting started tutorial for experiments in `docs/tutorials/`
2. **Outdated Function Signature**: How-to guide shows OLD main branch signature
3. **Missing v1.0 Features**: No documentation for tracer parameter
4. **Incorrect Field Names**: Shows `ground_truth` (singular) instead of `ground_truths` (plural)

### What's Wrong in `how-to/evaluation/running-experiments.rst`

**Line 19 - OUTDATED:**
```python
def my_llm_app(inputs, ground_truths):  # ❌ OLD main branch signature
    # Your application logic
    result = call_llm(inputs["prompt"])
    return {"answer": result}
```

**Line 104 - OUTDATED:**
```python
def my_function(inputs, ground_truths):  # ❌ OLD signature
    """
    Args:
        inputs (dict): From datapoint["inputs"]
        ground_truths (dict): From datapoint["ground_truths"]
    """
```

**Should Be (v1.0):**
```python
def my_llm_app(datapoint: Dict[str, Any]) -> Dict[str, Any]:  # ✅ NEW v1.0
    inputs = datapoint.get("inputs", {})
    ground_truths = datapoint.get("ground_truths")  # Optional
    # Your application logic
    result = call_llm(inputs["prompt"])
    return {"answer": result}

# OR with tracer parameter (v1.0 feature):
def my_llm_app(datapoint: Dict[str, Any], tracer: HoneyHiveTracer) -> Dict[str, Any]:
    inputs = datapoint.get("inputs", {})
    # Can now use tracer.enrich_session(), etc.
    tracer.enrich_session(metadata={"processing": "active"})
    result = call_llm(inputs["prompt"])
    return {"answer": result}
```

---

## 📋 Documentation Standards (from Agent OS)

### Divio Documentation System

1. **TUTORIALS** (`docs/tutorials/`) - Learning-oriented, step-by-step guides (15-20 min max)
   - What user will learn
   - Complete working example
   - Step-by-step instructions
   - Expected outcome

2. **HOW-TO GUIDES** (`docs/how-to/`) - Problem-oriented, specific solutions
   - Question format ("How do I...?")
   - Direct answer
   - Code examples
   - Links to related content

3. **REFERENCE** (`docs/reference/`) - Information-oriented, technical specifications
   - Complete API documentation
   - All parameters documented
   - Type annotations
   - Examples

4. **EXPLANATION** (`docs/explanation/`) - Understanding-oriented, conceptual background
   - Why things work the way they do
   - Architecture decisions
   - Design rationale

### Quality Standards

From `quality-framework.md`:
- [x] **Code Examples**: All examples tested and working (copy-paste executable)
- [x] **Type Safety**: Use type hints in all examples
- [x] **Complete Imports**: All necessary imports included
- [x] **Cross-References**: All internal links verified
- [x] **Sphinx Compliance**: RST format, proper directives, zero build warnings

---

## 🎯 Required Changes

### 1. CREATE: `docs/tutorials/05-run-first-experiment.rst` (NEW)

**Purpose**: Learning-oriented tutorial for experiments  
**Target Audience**: Users new to experiments  
**Time**: 15-20 minutes  
**Format**: Step-by-step with complete working example

**Structure**:
```
Tutorial: Run Your First Experiment
===================================

What You'll Learn
-----------------
- How to run an experiment with evaluate()
- How to structure test data
- How to view results in HoneyHive

What You'll Build
-----------------
A simple question-answering experiment that tests different prompts

Prerequisites
-------------
- Completed Tutorial 01 (Setup First Tracer)
- Python 3.11+
- HoneyHive API key

Step 1: Setup
-------------
[Code: imports, env vars]

Step 2: Define Your Function
-----------------------------
[Code: evaluation function with v1.0 signature]

Step 3: Create Test Dataset
----------------------------
[Code: dataset with inputs/ground_truths]

Step 4: Run Experiment
----------------------
[Code: evaluate() call]

Step 5: View Results
--------------------
[Instructions + screenshot]

What You've Learned
-------------------
[Summary]

Next Steps
----------
[Links to how-to guides]
```

### 2. UPDATE: `docs/how-to/evaluation/running-experiments.rst`

**Changes Required**:

1. **Update all function signatures** to v1.0 format
2. **Add section for tracer parameter** (v1.0 feature)
3. **Update ground_truth → ground_truths** (plural everywhere)
4. **Add backward compatibility note**
5. **Add type hints to all examples**

**New Sections to Add**:
```
How do I use the tracer inside my evaluation function? (NEW)
------------------------------------------------------------
[v1.0 feature with tracer parameter]

How do I migrate from main branch to v1.0?
------------------------------------------
[Backward compatibility guide]
```

### 3. UPDATE: `docs/tutorials/index.rst`

**Add to Getting Started Path**:
```rst
.. toctree::
   :maxdepth: 1
   :numbered:

   01-setup-first-tracer
   02-add-llm-tracing-5min
   03-enable-span-enrichment
   04-configure-multi-instance
   05-run-first-experiment  # NEW
```

### 4. UPDATE: `docs/how-to/evaluation/index.rst`

**Add tip about new v1.0 features**:
```rst
.. tip::
   **Using v1.0?** Check out the new tracer parameter feature
   in :doc:`running-experiments` for advanced session enrichment.
```

---

## 🎯 Detailed Changes

### `running-experiments.rst` - Line-by-Line Updates

#### Section: "What's the simplest way to run an experiment?"

**BEFORE (lines 14-42):**
```python
def my_llm_app(inputs, ground_truths):  # ❌ OLD
    # Your application logic
    result = call_llm(inputs["prompt"])
    return {"answer": result}
```

**AFTER:**
```python
from typing import Any, Dict

def my_llm_app(datapoint: Dict[str, Any]) -> Dict[str, Any]:  # ✅ v1.0
    """Process a single datapoint in your experiment.
    
    Args:
        datapoint: Contains 'inputs' and optionally 'ground_truths'
    
    Returns:
        Dictionary with your function's outputs
    """
    inputs = datapoint.get("inputs", {})
    # ground_truths available but typically not used here
    # (used by evaluators)
    
    result = call_llm(inputs["prompt"])
    return {"answer": result}
```

#### Section: "What signature must my function have?" (lines 95-130)

**REPLACE ENTIRE SECTION WITH:**

```rst
What signature should my evaluation function have?
--------------------------------------------------

**V1.0 Signature (Recommended)**

Your function receives a ``datapoint`` dictionary:

.. code-block:: python

   from typing import Any, Dict
   
   def my_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
       """
       Args:
           datapoint: Dictionary containing:
               - "inputs": Your input parameters
               - "ground_truths": Expected outputs (optional)
       
       Returns:
           dict: Your function's output
       """
       # Extract inputs
       inputs = datapoint.get("inputs", {})
       ground_truths = datapoint.get("ground_truths")  # Optional
       
       # Your logic
       user_query = inputs.get("question")
       result = process_query(user_query)
       
       # Return dict
       return {"answer": result, "metadata": {...}}

.. important::
   - Parameter is **positional** - must be first parameter
   - ``datapoint`` contains both ``inputs`` and ``ground_truths``
   - ``ground_truths`` is optional in datapoint
   - Return value should be a **dictionary**
   - Use **type hints** for better IDE support

**Backward Compatibility Note**

If you're migrating from main branch (pre-v1.0), your old signature will NOT work:

.. code-block:: python

   # ❌ OLD main branch signature - NO LONGER SUPPORTED
   def my_function(inputs, ground_truths):
       pass
   
   # ✅ NEW v1.0 signature - USE THIS
   def my_function(datapoint: Dict[str, Any]) -> Dict[str, Any]:
       inputs = datapoint.get("inputs", {})
       ground_truths = datapoint.get("ground_truths")
       pass

See :doc:`../migration-compatibility/migration-guide` for full migration details.
```

#### NEW Section to ADD (after line 211):

```rst
How do I use enrich_session inside my evaluation function?
----------------------------------------------------------

**Use the tracer Parameter (V1.0 Feature)**

.. versionadded:: 1.0
   The ``tracer`` parameter enables session enrichment within evaluation functions.

Pass a ``tracer`` parameter to your function to access tracer instance methods:

.. code-block:: python

   from typing import Any, Dict
   from honeyhive import HoneyHiveTracer
   
   def my_function(
       datapoint: Dict[str, Any],
       tracer: HoneyHiveTracer  # V1.0 feature
   ) -> Dict[str, Any]:
       """Evaluation function with tracer access.
       
       Args:
           datapoint: Input data and ground truths
           tracer: HoneyHive tracer instance for this datapoint
       
       Returns:
           Function outputs
       """
       inputs = datapoint.get("inputs", {})
       
       # Use tracer instance methods
       tracer.enrich_session(
           metadata={"processing_stage": "evaluation"},
           metrics={"complexity": len(inputs.get("text", ""))}
       )
       
       # Your logic
       result = process(inputs)
       
       # Enrich again after processing
       tracer.enrich_session(
           metadata={"status": "completed"}
       )
       
       return {"result": result}

**How It Works:**

1. ``evaluate()`` detects the ``tracer`` parameter using ``inspect.signature()``
2. Each datapoint gets its own tracer instance
3. Your function receives the correct tracer for that datapoint
4. Use ``tracer.enrich_session()``, ``tracer.enrich_span()``, etc.

.. important::
   **Backward Compatibility**: Functions WITHOUT the ``tracer`` parameter still work!
   The ``tracer`` parameter is **optional**. Only add it if you need to enrich sessions.

.. code-block:: python

   # ✅ Both signatures work:
   
   # Without tracer (main branch compatible)
   def func1(datapoint: Dict[str, Any]) -> Dict[str, Any]:
       return {"result": "test"}
   
   # With tracer (v1.0 feature)
   def func2(datapoint: Dict[str, Any], tracer: HoneyHiveTracer) -> Dict[str, Any]:
       tracer.enrich_session(metadata={"status": "processing"})
       return {"result": "test"}
   
   # Both work with evaluate()
   evaluate(function=func1, dataset=dataset, ...)  # ✅
   evaluate(function=func2, dataset=dataset, ...)  # ✅
```

---

## 📝 New Tutorial Content

### `docs/tutorials/05-run-first-experiment.rst`

```rst
Tutorial 5: Run Your First Experiment
======================================

.. note::
   **Tutorial** (15-20 minutes)
   
   This is a hands-on tutorial that takes you step-by-step through running
   your first experiment with HoneyHive. You'll create a working example
   and see results in the dashboard.

What You'll Learn
-----------------

By the end of this tutorial, you'll know how to:

- Run an experiment with ``evaluate()``
- Structure test data with inputs and ground truths
- **Create evaluators to automatically score outputs**
- **View metrics and scores in HoneyHive dashboard**
- Compare different versions of your function

What You'll Build
-----------------

A complete question-answering experiment with automated evaluation. You'll:

1. Create a baseline QA function
2. Test it against a dataset
3. **Add evaluators to automatically score outputs**
4. **Compare baseline vs improved version using metrics**
5. View results and metrics in HoneyHive dashboard

Prerequisites
-------------

Before starting this tutorial, you should:

- Complete :doc:`01-setup-first-tracer`
- Have Python 3.11 or higher installed
- Have a HoneyHive API key
- Basic familiarity with Python dictionaries

If you haven't set up the SDK yet, go back to Tutorial 1.

Step 1: Install and Setup
--------------------------

First, create a new Python file for this tutorial:

.. code-block:: bash

   touch my_first_experiment.py

Add the necessary imports and setup:

.. code-block:: python

   # my_first_experiment.py
   import os
   from typing import Any, Dict
   from honeyhive.experiments import evaluate
   
   # Set your API key
   os.environ["HH_API_KEY"] = "your-api-key-here"
   os.environ["HH_PROJECT"] = "experiments-tutorial"

.. tip::
   Store your API key in a ``.env`` file instead of hardcoding it.
   See :doc:`../how-to/deployment/production` for production best practices.

Step 2: Define Your Function
-----------------------------

Create a simple function that answers questions. This will be the function
we test in our experiment:

.. code-block:: python

   def answer_question(datapoint: Dict[str, Any]) -> Dict[str, Any]:
       """Answer a trivia question.
       
       This is the function we'll test in our experiment.
       
       Args:
           datapoint: Contains 'inputs' with the question
       
       Returns:
           Dictionary with the answer
       """
       inputs = datapoint.get("inputs", {})
       question = inputs.get("question", "")
       
       # Simple logic: check for keywords
       # (In real use, you'd call an LLM here)
       if "capital" in question.lower() and "france" in question.lower():
           answer = "Paris"
       elif "2+2" in question:
           answer = "4"
       elif "color" in question.lower() and "sky" in question.lower():
           answer = "blue"
       else:
           answer = "I don't know"
       
       return {
           "answer": answer,
           "confidence": "high" if answer != "I don't know" else "low"
       }

.. note::
   This example uses simple logic for demonstration. In a real experiment,
   you'd call an LLM API (OpenAI, Anthropic, etc.) inside this function.

Step 3: Create Your Test Dataset
---------------------------------

Define a dataset with questions and expected answers:

.. code-block:: python

   dataset = [
       {
           "inputs": {
               "question": "What is the capital of France?"
           },
           "ground_truths": {
               "answer": "Paris",
               "category": "geography"
           }
       },
       {
           "inputs": {
               "question": "What is 2+2?"
           },
           "ground_truths": {
               "answer": "4",
               "category": "math"
           }
       },
       {
           "inputs": {
               "question": "What color is the sky?"
           },
           "ground_truths": {
               "answer": "blue",
               "category": "science"
           }
       }
   ]

**Understanding the Structure:**

- ``inputs``: What your function receives
- ``ground_truths``: The expected correct answers (used for evaluation)

Step 4: Run Your Experiment
----------------------------

Now run the experiment:

.. code-block:: python

   result = evaluate(
       function=answer_question,
       dataset=dataset,
       name="qa-baseline-v1",
       verbose=True  # Show progress
   )
   
   print(f"\\n✅ Experiment complete!")
   print(f"📊 Run ID: {result.run_id}")
   print(f"📈 Status: {result.status}")

**Run it:**

.. code-block:: bash

   python my_first_experiment.py

**Expected Output:**

.. code-block:: text

   Processing datapoint 1/3...
   Processing datapoint 2/3...
   Processing datapoint 3/3...
   
   ✅ Experiment complete!
   📊 Run ID: run_abc123...
   📈 Status: completed

Step 5: View Results in Dashboard
----------------------------------

1. Go to `HoneyHive Dashboard <https://app.honeyhive.ai>`_
2. Navigate to your project: ``experiments-tutorial``
3. Click on "Experiments" tab
4. Find your run: ``qa-baseline-v1``
5. Click to view:
   - Session traces for each question
   - Function outputs
   - Ground truths
   - Session metadata

**What You'll See:**

- 3 sessions (one per datapoint)
- Each session shows inputs and outputs
- Ground truths displayed for comparison
- Session names include your experiment name

Step 6: Add Evaluators for Automated Scoring
---------------------------------------------

Viewing results manually is helpful, but let's add **evaluators** to automatically
score our function's outputs:

.. code-block:: python

   def exact_match_evaluator(
       outputs: Dict[str, Any],
       inputs: Dict[str, Any],
       ground_truths: Dict[str, Any]
   ) -> float:
       """Check if answer exactly matches ground truth.
       
       Args:
           outputs: Function's output (from answer_question)
           inputs: Original inputs (not used here)
           ground_truths: Expected outputs
       
       Returns:
           1.0 if exact match, 0.0 otherwise
       """
       actual_answer = outputs.get("answer", "").lower().strip()
       expected_answer = ground_truths.get("answer", "").lower().strip()
       
       return 1.0 if actual_answer == expected_answer else 0.0

   def confidence_evaluator(
       outputs: Dict[str, Any],
       inputs: Dict[str, Any],
       ground_truths: Dict[str, Any]
   ) -> float:
       """Check if confidence is appropriate.
       
       Returns:
           1.0 if high confidence, 0.5 if low confidence
       """
       confidence = outputs.get("confidence", "low")
       return 1.0 if confidence == "high" else 0.5

**Understanding Evaluators:**

- **Input**: Receives ``(outputs, inputs, ground_truths)``
- **Output**: Returns a score (typically 0.0 to 1.0)
- **Purpose**: Automated quality assessment
- **Runs**: After function executes, for each datapoint

Step 7: Run Experiment with Evaluators
---------------------------------------

Now run the experiment with evaluators:

.. code-block:: python

   result = evaluate(
       function=answer_question,
       dataset=dataset,
       evaluators=[exact_match_evaluator, confidence_evaluator],  # Added!
       name="qa-baseline-with-metrics-v1",
       verbose=True
   )
   
   print(f"\\n✅ Experiment complete!")
   print(f"📊 Run ID: {result.run_id}")
   print(f"📈 Status: {result.status}")
   
   # Access metrics
   if result.metrics:
       print(f"\\n📊 Aggregated Metrics:")
       # Metrics stored in model_extra for Pydantic v2
       extra_fields = getattr(result.metrics, "model_extra", {})
       for metric_name, metric_value in extra_fields.items():
           print(f"   {metric_name}: {metric_value:.2f}")

**Expected Output:**

.. code-block:: text

   Processing datapoint 1/3...
   Processing datapoint 2/3...
   Processing datapoint 3/3...
   Running evaluators...
   
   ✅ Experiment complete!
   📊 Run ID: run_xyz789...
   📈 Status: completed
   
   📊 Aggregated Metrics:
      exact_match_evaluator: 1.00
      confidence_evaluator: 1.00

Step 8: View Metrics in Dashboard
----------------------------------

Go back to the HoneyHive dashboard:

1. Find your new run: ``qa-baseline-with-metrics-v1``
2. Click to view details
3. You'll now see:
   - **Metrics tab**: Aggregated scores
   - **Per-datapoint metrics**: Individual scores
   - **Metric trends**: Compare across runs

**What You'll See:**

- Exact match score: 100% (3/3 correct)
- Confidence score: 100% (all high confidence)
- Metrics visualized as charts
- Per-session metrics in session details

Step 9: Test an Improvement
----------------------------

Let's test an improved version WITH evaluators:

.. code-block:: python

   def answer_question_improved(datapoint: Dict[str, Any]) -> Dict[str, Any]:
       """Improved version with better logic."""
       inputs = datapoint.get("inputs", {})
       question = inputs.get("question", "").lower()
       
       # More sophisticated keyword matching
       answers = {
           "capital of france": "Paris",
           "2+2": "4", 
           "color of the sky": "blue",
           "color is the sky": "blue"
       }
       
       # Check each pattern
       for pattern, ans in answers.items():
           if all(word in question for word in pattern.split()):
               return {"answer": ans, "confidence": "high"}
       
       return {"answer": "I don't know", "confidence": "low"}
   
   # Run improved version WITH EVALUATORS
   result_v2 = evaluate(
       function=answer_question_improved,
       dataset=dataset,
       evaluators=[exact_match_evaluator, confidence_evaluator],  # Same evaluators!
       name="qa-improved-with-metrics-v1",
       verbose=True
   )
   
   print(f"\\n✅ Improved version complete!")
   print(f"📊 Run ID: {result_v2.run_id}")
   
   # Compare metrics
   if result_v2.metrics:
       print(f"\\n📊 Metrics:")
       extra_fields = getattr(result_v2.metrics, "model_extra", {})
       for metric_name, metric_value in extra_fields.items():
           print(f"   {metric_name}: {metric_value:.2f}")

Now you have TWO runs to compare in the dashboard!

What You've Learned
-------------------

Congratulations! You've:

✅ Created your first evaluation function  
✅ Structured test data with inputs and ground truths  
✅ **Created evaluators to automatically score outputs**  
✅ Run experiments with ``evaluate()`` and evaluators  
✅ Viewed results and metrics in HoneyHive dashboard  
✅ Compared different versions with automated scoring  

**Key Concepts:**

- **Evaluation Function**: Your application logic under test
- **Dataset**: Test cases with inputs and ground truths
- **Evaluators**: Automated scoring functions
- **Metrics**: Quantitative measurements of quality  

Next Steps
----------

Now that you understand the basics:

- :doc:`../how-to/evaluation/creating-evaluators` - Add automated scoring
- :doc:`../how-to/evaluation/comparing-experiments` - Compare runs statistically
- :doc:`../how-to/evaluation/dataset-management` - Use datasets from HoneyHive UI
- :doc:`../how-to/evaluation/best-practices` - Production experiment patterns

Complete Code
-------------

Here's the complete code from this tutorial:

.. code-block:: python

   # my_first_experiment.py
   import os
   from typing import Any, Dict
   from honeyhive.experiments import evaluate
   
   os.environ["HH_API_KEY"] = "your-api-key-here"
   os.environ["HH_PROJECT"] = "experiments-tutorial"
   
   def answer_question(datapoint: Dict[str, Any]) -> Dict[str, Any]:
       """Answer a trivia question."""
       inputs = datapoint.get("inputs", {})
       question = inputs.get("question", "")
       
       if "capital" in question.lower() and "france" in question.lower():
           answer = "Paris"
       elif "2+2" in question:
           answer = "4"
       elif "color" in question.lower() and "sky" in question.lower():
           answer = "blue"
       else:
           answer = "I don't know"
       
       return {"answer": answer}
   
   dataset = [
       {
           "inputs": {"question": "What is the capital of France?"},
           "ground_truths": {"answer": "Paris"}
       },
       {
           "inputs": {"question": "What is 2+2?"},
           "ground_truths": {"answer": "4"}
       },
       {
           "inputs": {"question": "What color is the sky?"},
           "ground_truths": {"answer": "blue"}
       }
   ]
   
   # Define evaluators
   def exact_match_evaluator(
       outputs: Dict[str, Any],
       inputs: Dict[str, Any],
       ground_truths: Dict[str, Any]
   ) -> float:
       """Check if answer exactly matches ground truth."""
       actual = outputs.get("answer", "").lower().strip()
       expected = ground_truths.get("answer", "").lower().strip()
       return 1.0 if actual == expected else 0.0
   
   def confidence_evaluator(
       outputs: Dict[str, Any],
       inputs: Dict[str, Any],
       ground_truths: Dict[str, Any]
   ) -> float:
       """Check if confidence is appropriate."""
       confidence = outputs.get("confidence", "low")
       return 1.0 if confidence == "high" else 0.5
   
   # Run experiment with evaluators
   result = evaluate(
       function=answer_question,
       dataset=dataset,
       evaluators=[exact_match_evaluator, confidence_evaluator],
       name="qa-baseline-with-metrics-v1",
       verbose=True
   )
   
   print(f"\\n✅ Experiment complete! Run ID: {result.run_id}")
   
   # Print metrics
   if result.metrics:
       print(f"\\n📊 Metrics:")
       extra_fields = getattr(result.metrics, "model_extra", {})
       for metric_name, metric_value in extra_fields.items():
           print(f"   {metric_name}: {metric_value:.2f}")
```

---

## ✅ Implementation Checklist

### Phase 1: Create New Tutorial
- [ ] Create `docs/tutorials/05-run-first-experiment.rst`
- [ ] Update `docs/tutorials/index.rst` to include new tutorial
- [ ] Build docs and verify zero warnings
- [ ] Test all code examples

### Phase 2: Update How-To Guide
- [ ] Update function signatures in `running-experiments.rst`
- [ ] Change `ground_truth` → `ground_truths` throughout
- [ ] Add tracer parameter section
- [ ] Add backward compatibility note
- [ ] Add type hints to all examples
- [ ] Update complete example at end

### Phase 3: Quality Checks
- [ ] Run `make html` - zero warnings
- [ ] All code examples copy-paste executable
- [ ] All cross-references working
- [ ] Backward compatibility clearly explained
- [ ] v1.0 features highlighted with `.. versionadded::`

---

## 🎯 Success Criteria

Documentation is ready when:

1. ✅ New tutorial exists and is linked from index
2. ✅ All function signatures show v1.0 format
3. ✅ `ground_truths` (plural) used throughout
4. ✅ Tracer parameter documented with examples
5. ✅ Backward compatibility clearly explained
6. ✅ Zero Sphinx build warnings
7. ✅ All code examples tested and working
8. ✅ Type hints in all examples

---

**Ready to implement? Let's start with Phase 1!** 🚀

