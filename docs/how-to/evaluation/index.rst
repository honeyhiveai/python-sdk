Evaluation & Analysis
=====================

Learn how to evaluate LLM outputs, analyze performance, and implement quality assurance for your AI applications.

.. toctree::
   :maxdepth: 2

Overview
--------

Evaluation is critical for maintaining and improving the quality of LLM applications. HoneyHive provides comprehensive evaluation tools for both real-time and batch analysis.

**Key Evaluation Areas**:
- Output quality and accuracy
- Performance and latency
- Cost optimization
- User satisfaction
- A/B testing and experimentation

Quick Reference
---------------

**Key Evaluation Types:**

- **Custom Evaluators**: Domain-specific quality assessment and business logic validation
- **Batch Evaluation**: Large-scale performance analysis and testing workflows
- **Quality Metrics**: Standard quality measurements and scoring systems
- **A/B Testing**: Model and prompt comparison for optimization
- **Performance Analysis**: System performance optimization and monitoring

Getting Started
---------------

**1. Basic Evaluation with Decorators**

.. code-block:: python

   from honeyhive import HoneyHiveTracer, evaluate
   from honeyhive.evaluation.evaluators import ExactMatchEvaluator, LengthEvaluator

   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="evaluation-demo"
   )

   @evaluate(evaluators=["exact_match", "length"])
   def generate_answer(question: str, expected_answer: str) -> str:
       """Generate answer with automatic evaluation."""
       # Your LLM call here
       response = llm_call(question)
       return response

**2. Custom Quality Metrics**

.. code-block:: python

   from honeyhive.evaluation.evaluators import BaseEvaluator, EvaluationResult

   class DomainSpecificEvaluator(BaseEvaluator):
       def __init__(self, domain: str):
           super().__init__(f"domain_{domain}")
           self.domain = domain
       
       def evaluate(self, inputs: dict, outputs: dict, ground_truth: dict = None) -> EvaluationResult:
           score = self._calculate_domain_score(outputs, ground_truth)
           return EvaluationResult(
               score=score,
               metrics={"domain": self.domain, "accuracy": score}
           )

**3. Batch Analysis**

.. code-block:: python

   from honeyhive.evaluation import evaluate_batch

   # Evaluate large dataset
   results = evaluate_batch(
       dataset=[
           ({"prompt": "Q1"}, {"response": "A1"}),
           ({"prompt": "Q2"}, {"response": "A2"}),
           # ... more data
       ],
       evaluators=["quality", "relevance", "accuracy"],
       max_workers=4
   )

Common Evaluation Patterns
--------------------------

**Quality Assurance Pipeline**

.. code-block:: python

   def quality_assurance_pipeline(inputs: list, outputs: list):
       """Comprehensive quality assurance for LLM outputs."""
       
       with tracer.start_span("quality_assurance") as qa_span:
           qa_span.set_attribute("qa.input_count", len(inputs))
           qa_span.set_attribute("qa.pipeline_version", "v2.1")
           
           # Stage 1: Automated evaluation
           with tracer.start_span("automated_evaluation") as auto_span:
               auto_results = evaluate_batch(
                   dataset=list(zip(inputs, outputs)),
                   evaluators=["quality", "safety", "relevance"],
                   max_workers=8
               )
               
               auto_span.set_attribute("eval.passed_count", 
                                     sum(1 for r in auto_results if r.score > 0.8))
               auto_span.set_attribute("eval.avg_score", 
                                     sum(r.score for r in auto_results) / len(auto_results))
           
           # Stage 2: Flag problematic outputs
           with tracer.start_span("quality_filtering") as filter_span:
               flagged_items = []
               for i, result in enumerate(auto_results):
                   if result.score < 0.7:
                       flagged_items.append({
                           "index": i,
                           "score": result.score,
                           "input": inputs[i],
                           "output": outputs[i],
                           "issues": result.metrics
                       })
               
               filter_span.set_attribute("filter.flagged_count", len(flagged_items))
               filter_span.set_attribute("filter.flag_rate", len(flagged_items) / len(outputs))
           
           # Stage 3: Human review queue
           if flagged_items:
               with tracer.start_span("human_review_queue") as review_span:
                   review_queue_id = queue_for_human_review(flagged_items)
                   review_span.set_attribute("review.queue_id", review_queue_id)
                   review_span.set_attribute("review.items_queued", len(flagged_items))
           
           qa_span.set_attribute("qa.quality_score", 
                                sum(r.score for r in auto_results) / len(auto_results))
           qa_span.set_attribute("qa.needs_human_review", len(flagged_items) > 0)
           
           return {
               "automated_results": auto_results,
               "flagged_items": flagged_items,
               "overall_quality": sum(r.score for r in auto_results) / len(auto_results)
           }

**Model Comparison Framework**

.. code-block:: python

   def compare_models(test_dataset: list, models: dict):
       """Compare multiple models on the same dataset."""
       
       with tracer.start_span("model_comparison") as comparison_span:
           comparison_span.set_attribute("comparison.dataset_size", len(test_dataset))
           comparison_span.set_attribute("comparison.models_count", len(models))
           comparison_span.set_attribute("comparison.models", list(models.keys()))
           
           model_results = {}
           
           for model_name, model_config in models.items():
               with tracer.start_span(f"model_{model_name}") as model_span:
                   model_span.set_attribute("model.name", model_name)
                   model_span.set_attribute("model.provider", model_config.get("provider"))
                   model_span.set_attribute("model.version", model_config.get("version"))
                   
                   # Generate outputs for this model
                   outputs = []
                   for test_item in test_dataset:
                       output = generate_with_model(model_config, test_item["input"])
                       outputs.append(output)
                   
                   # Evaluate this model's outputs
                   evaluation_results = evaluate_batch(
                       dataset=[(item["input"], output) for item, output in zip(test_dataset, outputs)],
                       evaluators=["quality", "accuracy", "relevance", "safety"],
                       context={"model": model_name}
                   )
                   
                   # Calculate model metrics
                   avg_score = sum(r.score for r in evaluation_results) / len(evaluation_results)
                   avg_latency = sum(r.metrics.get("latency", 0) for r in evaluation_results) / len(evaluation_results)
                   
                   model_span.set_attribute("model.avg_score", avg_score)
                   model_span.set_attribute("model.avg_latency_ms", avg_latency)
                   model_span.set_attribute("model.outputs_count", len(outputs))
                   
                   model_results[model_name] = {
                       "outputs": outputs,
                       "evaluations": evaluation_results,
                       "avg_score": avg_score,
                       "avg_latency": avg_latency
                   }
           
           # Find best performing model
           best_model = max(model_results.items(), key=lambda x: x[1]["avg_score"])
           comparison_span.set_attribute("comparison.best_model", best_model[0])
           comparison_span.set_attribute("comparison.best_score", best_model[1]["avg_score"])
           
           return model_results

**Continuous Evaluation System**

.. code-block:: python

   class ContinuousEvaluationSystem:
       """System for ongoing evaluation of production LLM outputs."""
       
       def __init__(self, tracer, evaluation_config: dict):
           self.tracer = tracer
           self.config = evaluation_config
           self.evaluation_buffer = []
           self.buffer_size = config.get("buffer_size", 100)
       
       def evaluate_production_output(self, input_data: dict, output_data: dict, user_feedback: dict = None):
           """Evaluate a single production output."""
           
           with self.tracer.start_span("production_evaluation") as span:
               span.set_attribute("eval.production", True)
               span.set_attribute("eval.has_user_feedback", user_feedback is not None)
               
               # Add to evaluation buffer
               evaluation_item = {
                   "input": input_data,
                   "output": output_data,
                   "user_feedback": user_feedback,
                   "timestamp": time.time()
               }
               
               self.evaluation_buffer.append(evaluation_item)
               span.set_attribute("eval.buffer_size", len(self.evaluation_buffer))
               
               # Real-time quality check
               if self.config.get("real_time_evaluation", True):
                   with self.tracer.start_span("real_time_quality_check") as rt_span:
                       quality_score = self._quick_quality_check(input_data, output_data)
                       rt_span.set_attribute("quality.score", quality_score)
                       rt_span.set_attribute("quality.threshold", self.config.get("quality_threshold", 0.7))
                       
                       if quality_score < self.config.get("quality_threshold", 0.7):
                           rt_span.set_attribute("quality.alert_triggered", True)
                           self._trigger_quality_alert(evaluation_item, quality_score)
               
               # Trigger batch evaluation if buffer is full
               if len(self.evaluation_buffer) >= self.buffer_size:
                   span.set_attribute("eval.triggering_batch", True)
                   self._trigger_batch_evaluation()
               
               return quality_score if 'quality_score' in locals() else None
       
       def _trigger_batch_evaluation(self):
           """Process accumulated evaluation buffer."""
           
           with self.tracer.start_span("batch_evaluation_trigger") as batch_span:
               batch_span.set_attribute("batch.size", len(self.evaluation_buffer))
               
               # Prepare dataset for evaluation
               dataset = [(item["input"], item["output"]) for item in self.evaluation_buffer]
               
               # Run comprehensive evaluation
               results = evaluate_batch(
                   dataset=dataset,
                   evaluators=self.config.get("evaluators", ["quality", "safety", "relevance"]),
                   max_workers=self.config.get("max_workers", 4),
                   context={"batch_type": "production_monitoring"}
               )
               
               # Analyze results for trends
               avg_score = sum(r.score for r in results) / len(results)
               declining_quality = self._detect_quality_decline(results)
               
               batch_span.set_attribute("batch.avg_score", avg_score)
               batch_span.set_attribute("batch.declining_quality", declining_quality)
               
               if declining_quality:
                   self._trigger_quality_decline_alert(results)
               
               # Store results for historical analysis
               self._store_evaluation_results(results)
               
               # Clear buffer
               self.evaluation_buffer.clear()
               batch_span.set_attribute("batch.buffer_cleared", True)

Performance Analysis Tools
--------------------------

**Token Usage Analysis**

.. code-block:: python

   def analyze_token_usage(evaluation_results: list):
       """Analyze token usage patterns and costs."""
       
       with tracer.start_span("token_usage_analysis") as analysis_span:
           token_data = []
           
           for result in evaluation_results:
               if "tokens" in result.metrics:
                   tokens = result.metrics["tokens"]
                   token_data.append({
                       "input_tokens": tokens.get("input", 0),
                       "output_tokens": tokens.get("output", 0),
                       "total_tokens": tokens.get("total", 0),
                       "cost": tokens.get("cost", 0),
                       "quality_score": result.score
                   })
           
           if token_data:
               # Calculate statistics
               total_tokens = sum(item["total_tokens"] for item in token_data)
               total_cost = sum(item["cost"] for item in token_data)
               avg_tokens_per_request = total_tokens / len(token_data)
               avg_cost_per_request = total_cost / len(token_data)
               
               # Quality vs cost analysis
               high_quality_items = [item for item in token_data if item["quality_score"] > 0.8]
               if high_quality_items:
                   avg_cost_high_quality = sum(item["cost"] for item in high_quality_items) / len(high_quality_items)
                   cost_efficiency = avg_cost_high_quality / avg_cost_per_request if avg_cost_per_request > 0 else 0
               else:
                   cost_efficiency = 0
               
               analysis_span.set_attribute("tokens.total", total_tokens)
               analysis_span.set_attribute("tokens.avg_per_request", avg_tokens_per_request)
               analysis_span.set_attribute("cost.total_usd", total_cost)
               analysis_span.set_attribute("cost.avg_per_request_usd", avg_cost_per_request)
               analysis_span.set_attribute("efficiency.cost_quality_ratio", cost_efficiency)
               
               return {
                   "total_tokens": total_tokens,
                   "avg_tokens_per_request": avg_tokens_per_request,
                   "total_cost": total_cost,
                   "avg_cost_per_request": avg_cost_per_request,
                   "cost_efficiency": cost_efficiency,
                   "token_distribution": analyze_token_distribution(token_data)
               }

**Quality Trend Analysis**

.. code-block:: python

   def analyze_quality_trends(historical_results: list, time_window_hours: int = 24):
       """Analyze quality trends over time."""
       
       with tracer.start_span("quality_trend_analysis") as trend_span:
           trend_span.set_attribute("analysis.time_window_hours", time_window_hours)
           trend_span.set_attribute("analysis.data_points", len(historical_results))
           
           # Group results by time buckets
           current_time = time.time()
           time_buckets = {}
           
           for result in historical_results:
               timestamp = result.get("timestamp", current_time)
               hours_ago = int((current_time - timestamp) / 3600)
               
               if hours_ago <= time_window_hours:
                   if hours_ago not in time_buckets:
                       time_buckets[hours_ago] = []
                   time_buckets[hours_ago].append(result["score"])
           
           # Calculate trends
           trend_data = []
           for hour in sorted(time_buckets.keys()):
               scores = time_buckets[hour]
               avg_score = sum(scores) / len(scores)
               trend_data.append({
                   "hours_ago": hour,
                   "avg_score": avg_score,
                   "sample_count": len(scores),
                   "min_score": min(scores),
                   "max_score": max(scores)
               })
           
           # Detect trends
           if len(trend_data) >= 2:
               recent_avg = sum(item["avg_score"] for item in trend_data[:3]) / min(3, len(trend_data))
               older_avg = sum(item["avg_score"] for item in trend_data[-3:]) / min(3, len(trend_data))
               trend_direction = "improving" if recent_avg > older_avg else "declining"
               trend_magnitude = abs(recent_avg - older_avg)
           else:
               trend_direction = "insufficient_data"
               trend_magnitude = 0
           
           trend_span.set_attribute("trend.direction", trend_direction)
           trend_span.set_attribute("trend.magnitude", trend_magnitude)
           trend_span.set_attribute("trend.buckets_analyzed", len(time_buckets))
           
           return {
               "trend_direction": trend_direction,
               "trend_magnitude": trend_magnitude,
               "time_series_data": trend_data,
               "summary": {
                   "total_samples": sum(item["sample_count"] for item in trend_data),
                   "overall_avg": sum(item["avg_score"] * item["sample_count"] for item in trend_data) / 
                                 sum(item["sample_count"] for item in trend_data) if trend_data else 0
               }
           }

Best Practices
--------------

**1. Evaluation Strategy**

.. code-block:: python

   # Good: Multi-layered evaluation
   evaluation_pipeline = [
       "automated_quality_check",    # Fast, automated
       "safety_evaluation",          # Critical for production
       "domain_specific_metrics",    # Business-relevant
       "user_feedback_integration",  # Real-world validation
       "periodic_human_review"       # Quality assurance
   ]

**2. Performance Monitoring**

.. code-block:: python

   # Monitor evaluation performance itself
   @evaluate(evaluators=["quality"])
   def monitored_llm_call(prompt: str):
       with tracer.start_span("llm_call_with_monitoring") as span:
           start_time = time.time()
           response = llm_call(prompt)
           span.set_attribute("llm.response_time_ms", (time.time() - start_time) * 1000)
           return response

**3. Cost-Aware Evaluation**

.. code-block:: python

   # Balance evaluation depth with cost
   def cost_aware_evaluation(data: dict, priority: str = "normal"):
       if priority == "high":
           evaluators = ["quality", "safety", "accuracy", "relevance", "custom_domain"]
       elif priority == "normal":
           evaluators = ["quality", "safety"]
       else:  # low priority
           evaluators = ["basic_quality"]
       
       return evaluate(data, evaluators=evaluators)

See Also
--------

- :doc:`../integrations/index` - LLM provider integrations
- :doc:`../advanced-tracing/custom-spans` - Custom tracing patterns
- :doc:`../monitoring/index` - System monitoring and alerting
- :doc:`../../reference/evaluation/evaluators` - Evaluator API reference
