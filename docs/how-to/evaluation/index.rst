Evaluation & Analysis Guides
=============================

**Problem-solving guides** for running experiments and evaluating LLM outputs in HoneyHive.

.. tip::
   **New to experiments?** Start with the :doc:`../../tutorials/04-evaluation-basics` tutorial first.

.. toctree::
   :maxdepth: 2
   :caption: Experiments & Evaluation

   running-experiments
   creating-evaluators
   comparing-experiments
   dataset-management
   server-side-evaluators
   multi-step-experiments
   result-analysis
   best-practices
   troubleshooting

Overview
--------

Experiments in HoneyHive help you systematically test and improve AI applications. These guides show you how to solve specific evaluation challenges.

**What You Can Do:**

- Run experiments with the ``evaluate()`` function
- Create custom metrics with evaluators
- Compare runs to track improvements
- Manage datasets in UI and code
- Analyze results programmatically

Quick Links
-----------

**Getting Started:**

- :doc:`running-experiments` - Core ``evaluate()`` workflow and patterns
- :doc:`creating-evaluators` - Build custom metrics with ``@evaluator``
- :doc:`dataset-management` - Work with datasets

**Comparing & Analyzing:**

- :doc:`comparing-experiments` - Compare runs and identify improvements
- :doc:`result-analysis` - Access and export experiment data

**Advanced Patterns:**

- :doc:`multi-step-experiments` - Evaluate complex multi-step pipelines
- :doc:`server-side-evaluators` - Use evaluators configured in UI
- :doc:`best-practices` - Design effective evaluation strategies

**Need Help?**

- :doc:`troubleshooting` - Fix common experiment issues

Common Use Cases
----------------

**"How do I test if my prompt change improved quality?"**
   See :doc:`running-experiments` for basic workflow, then :doc:`comparing-experiments` to compare results.

**"How do I create custom quality metrics?"**
   See :doc:`creating-evaluators` for decorator-based evaluator patterns.

**"How do I evaluate a RAG pipeline with multiple steps?"**
   See :doc:`multi-step-experiments` for component-level evaluation.

**"How do I use datasets I created in the HoneyHive UI?"**
   See :doc:`dataset-management` for managed dataset workflows.

**"My experiments are too slow, how do I speed them up?"**
   See :doc:`troubleshooting` for parallel execution and optimization tips.

See Also
--------

- :doc:`../../tutorials/04-evaluation-basics` - Learn experiments basics
- :doc:`../../reference/experiments/experiments` - Complete API reference
- :doc:`../monitoring/index` - Monitor experiments in production
