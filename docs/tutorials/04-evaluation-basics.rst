Evaluation Basics
=================

.. note::
   **Tutorial Goal**: Learn to evaluate LLM outputs automatically with HoneyHive's evaluation framework.

This tutorial teaches you how to set up automated evaluation of your LLM outputs, creating a feedback loop to improve your applications over time.

What You'll Learn
-----------------

- How to use built-in evaluators for common tasks
- Creating custom evaluators for your specific needs
- Integrating evaluation with your existing tracing
- Understanding evaluation metrics and results
- Setting up evaluation pipelines

Prerequisites
-------------

- Complete :doc:`03-llm-integration` tutorial
- LLM integration working (OpenAI, Anthropic, or Google AI)
- Basic understanding of your evaluation criteria

Why Evaluate LLM Outputs?
-------------------------

LLM applications are probabilistic - the same input can produce different outputs. Evaluation helps you:

- **Measure Quality**: Track how well your LLM performs
- **Detect Regressions**: Catch when changes hurt performance
- **Compare Models**: Decide between different LLM providers or versions
- **Build Confidence**: Provide metrics for stakeholders

Introduction to HoneyHive Evaluation
-------------------------------------

HoneyHive provides both built-in and custom evaluation capabilities:

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace, evaluate
   from honeyhive.evaluation import FactualAccuracyEvaluator
   
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       
   )

**Key Concepts:**

- **Evaluators**: Functions that score LLM outputs
- **Evaluation Context**: Input, output, and expected result
- **Metrics**: Quantitative measures of performance
- **Feedback Loop**: Using evaluation results to improve

Built-in Evaluators
-------------------

HoneyHive provides several built-in evaluators for common use cases:

**Factual Accuracy Evaluator**

.. code-block:: python

   from honeyhive import HoneyHiveTracer, trace
   from honeyhive.evaluation import FactualAccuracyEvaluator
   import openai
   
   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       
   )
   
   # Initialize the evaluator
   fact_evaluator = FactualAccuracyEvaluator()
   
   @trace(tracer=tracer)
   @evaluate(evaluator=fact_evaluator)
   def answer_factual_question(question: str) -> str:
       """Answer a factual question using GPT."""
       client = openai.OpenAI()
       
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[
               {"role": "system", "content": "Provide accurate, factual answers."},
               {"role": "user", "content": question}
           ]
       )
       
       return response.choices[0].message.content
   
   # This call is both traced AND evaluated
   answer = answer_factual_question("What is the capital of France?")
   print(f"Answer: {answer}")

**What gets evaluated:**
- Factual correctness against known data sources
- Claims verification
- Consistency with established facts

**Sentiment Analysis Evaluator**

.. code-block:: python

   from honeyhive.evaluation import SentimentEvaluator
   
   sentiment_evaluator = SentimentEvaluator()
   
   @trace(tracer=tracer)
   @evaluate(evaluator=sentiment_evaluator)
   def analyze_customer_feedback(feedback: str) -> str:
       """Analyze customer feedback sentiment."""
       client = openai.OpenAI()
       
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[
               {"role": "system", "content": "Analyze the sentiment of customer feedback. Respond with positive, negative, or neutral."},
               {"role": "user", "content": f"Customer feedback: {feedback}"}
           ]
       )
       
       return response.choices[0].message.content
   
   # Automatically evaluates sentiment accuracy
   result = analyze_customer_feedback("The product is amazing! I love the new features.")

**Quality Score Evaluator**

.. code-block:: python

   from honeyhive.evaluation import QualityScoreEvaluator
   
   quality_evaluator = QualityScoreEvaluator(
       criteria=["relevance", "clarity", "completeness"]
   )
   
   @trace(tracer=tracer)
   @evaluate(evaluator=quality_evaluator)
   def generate_product_description(product_name: str, features: list) -> str:
       """Generate marketing copy for a product."""
       client = openai.OpenAI()
       
       features_text = ", ".join(features)
       
       response = client.chat.completions.create(
           model="gpt-4",
           messages=[
               {"role": "system", "content": "Write compelling product descriptions."},
               {"role": "user", "content": f"Product: {product_name}, Features: {features_text}"}
           ]
       )
       
       return response.choices[0].message.content

Creating Custom Evaluators
--------------------------

For domain-specific evaluation, create custom evaluators:

**Simple Custom Evaluator**

.. code-block:: python

   from honeyhive.evaluation import BaseEvaluator
   
   class LengthEvaluator(BaseEvaluator):
       """Evaluates if response length is appropriate."""
       
       def __init__(self, min_length: int = 50, max_length: int = 500):
           self.min_length = min_length
           self.max_length = max_length
       
       def evaluate(self, input_text: str, output_text: str, context: dict = None) -> dict:
           """Evaluate response length."""
           length = len(output_text)
           
           # Score: 1.0 if within range, penalty for being outside
           if self.min_length <= length <= self.max_length:
               score = 1.0
               feedback = "Length is appropriate"
           elif length < self.min_length:
               score = max(0.0, length / self.min_length)
               feedback = f"Response too short ({length} chars, minimum {self.min_length})"
           else:
               score = max(0.0, self.max_length / length)
               feedback = f"Response too long ({length} chars, maximum {self.max_length})"
           
           return {
               "score": score,
               "feedback": feedback,
               "metrics": {
                   "response_length": length,
                   "min_length": self.min_length,
                   "max_length": self.max_length
               }
           }
   
   # Use the custom evaluator
   length_evaluator = LengthEvaluator(min_length=100, max_length=300)
   
   @trace(tracer=tracer)
   @evaluate(evaluator=length_evaluator)
   def write_summary(article: str) -> str:
       """Write a concise summary of an article."""
       client = openai.OpenAI()
       
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[
               {"role": "system", "content": "Write concise summaries in 100-300 characters."},
               {"role": "user", "content": f"Summarize: {article}"}
           ]
       )
       
       return response.choices[0].message.content

**Advanced Custom Evaluator with LLM**

.. code-block:: python

   class SemanticSimilarityEvaluator(BaseEvaluator):
       """Evaluates semantic similarity to expected output."""
       
       def __init__(self, model: str = "gpt-3.5-turbo"):
           self.model = model
           self.client = openai.OpenAI()
       
       def evaluate(self, input_text: str, output_text: str, context: dict = None) -> dict:
           """Use LLM to evaluate semantic similarity."""
           expected_output = context.get("expected_output", "")
           
           if not expected_output:
               return {"score": 0.0, "feedback": "No expected output provided"}
           
           evaluation_prompt = f"""
           Compare these two responses for semantic similarity on a scale of 0-1:
           
           Expected: {expected_output}
           Actual: {output_text}
           
           Provide a score (0.0-1.0) and brief explanation.
           Format: SCORE: 0.8, EXPLANATION: The responses convey similar meaning...
           """
           
           response = self.client.chat.completions.create(
               model=self.model,
               messages=[{"role": "user", "content": evaluation_prompt}]
           )
           
           result_text = response.choices[0].message.content
           
           # Parse the LLM response (simplified)
           try:
               score_part = result_text.split("SCORE:")[1].split(",")[0].strip()
               score = float(score_part)
               
               explanation_part = result_text.split("EXPLANATION:")[1].strip()
               
               return {
                   "score": score,
                   "feedback": explanation_part,
                   "metrics": {
                       "similarity_score": score,
                       "evaluation_model": self.model
                   }
               }
           except Exception as e:
               return {
                   "score": 0.0,
                   "feedback": f"Evaluation parsing failed: {e}",
                   "raw_response": result_text
               }
   
   # Use with expected output context
   semantic_evaluator = SemanticSimilarityEvaluator()
   
   @trace(tracer=tracer)
   @evaluate(evaluator=semantic_evaluator)
   def translate_text(text: str, target_language: str) -> str:
       """Translate text to target language."""
       client = openai.OpenAI()
       
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[
               {"role": "system", "content": f"Translate to {target_language}"},
               {"role": "user", "content": text}
           ]
       )
       
       return response.choices[0].message.content
   
   # Call with evaluation context
   result = translate_text(
       "Hello, how are you?", 
       "Spanish",
       evaluation_context={"expected_output": "Hola, ¿cómo estás?"}
   )

Multiple Evaluators
-------------------

You can apply multiple evaluators to the same function:

.. code-block:: python

   from honeyhive.evaluation import MultiEvaluator
   
   # Combine multiple evaluators
   multi_evaluator = MultiEvaluator([
       FactualAccuracyEvaluator(),
       LengthEvaluator(min_length=50, max_length=200),
       QualityScoreEvaluator(criteria=["clarity", "helpfulness"])
   ])
   
   @trace(tracer=tracer)
   @evaluate(evaluator=multi_evaluator)
   def answer_support_question(question: str) -> str:
       """Answer a customer support question."""
       client = openai.OpenAI()
       
       response = client.chat.completions.create(
           model="gpt-4",
           messages=[
               {"role": "system", "content": "Provide helpful, accurate support answers."},
               {"role": "user", "content": question}
           ]
       )
       
       return response.choices[0].message.content
   
   # Gets evaluated by all three evaluators
   answer = answer_support_question("How do I reset my password?")

Batch Evaluation
----------------

Evaluate multiple examples at once for comprehensive testing:

.. code-block:: python

   from honeyhive.evaluation import batch_evaluate
   
   def customer_service_bot(question: str) -> str:
       """Customer service bot function to evaluate."""
       client = openai.OpenAI()
       
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[
               {"role": "system", "content": "You are a helpful customer service agent."},
               {"role": "user", "content": question}
           ]
       )
       
       return response.choices[0].message.content
   
   # Test cases for evaluation
   test_cases = [
       {
           "input": "How do I return an item?",
           "expected_output": "To return an item, visit our returns page...",
           "context": {"category": "returns"}
       },
       {
           "input": "What's your refund policy?",
           "expected_output": "Our refund policy allows returns within 30 days...",
           "context": {"category": "policy"}
       },
       {
           "input": "I can't log into my account",
           "expected_output": "For login issues, try resetting your password...",
           "context": {"category": "technical"}
       }
   ]
   
   # Run batch evaluation
   results = batch_evaluate(
       function=customer_service_bot,
       test_cases=test_cases,
       evaluators=[
           SemanticSimilarityEvaluator(),
           QualityScoreEvaluator(),
           LengthEvaluator(min_length=20, max_length=150)
       ],
       
   )
   
   # Analyze results
   print(f"Average score: {results['average_score']:.2f}")
   print(f"Test cases passed: {results['passed']}/{results['total']}")
   
   for i, result in enumerate(results['individual_results']):
       print(f"Test {i+1}: Score {result['score']:.2f} - {result['feedback']}")

Understanding Evaluation Results
---------------------------------

Evaluation results include comprehensive metrics:

.. code-block:: python

   @trace(tracer=tracer)
   @evaluate(evaluator=quality_evaluator)
   def generate_email_response(customer_email: str) -> str:
       """Generate response to customer email."""
       # Your LLM call here
       pass
   
   result = generate_email_response("I'm having trouble with my order...")
   
   # Evaluation results are automatically logged
   # View in HoneyHive dashboard or access programmatically:
   
   evaluation_results = tracer.get_last_evaluation()
   print(f"Overall Score: {evaluation_results['score']}")
   print(f"Feedback: {evaluation_results['feedback']}")
   print(f"Metrics: {evaluation_results['metrics']}")

**Typical Evaluation Result Structure:**

.. code-block:: json

   {
     "score": 0.85,
     "feedback": "Response is clear and helpful but could be more concise",
     "metrics": {
       "factual_accuracy": 0.9,
       "clarity_score": 0.8,
       "length_score": 0.8,
       "response_time_ms": 1234
     },
     "evaluator": "QualityScoreEvaluator",
     "timestamp": "2024-01-15T10:30:00Z"
   }

Setting Up Evaluation Pipelines
---------------------------------

Create automated evaluation workflows:

.. code-block:: python

   import schedule
   import time
   from honeyhive.evaluation import EvaluationPipeline
   
   # Define evaluation pipeline
   pipeline = EvaluationPipeline(
       name="daily_quality_check",
       evaluators=[
           FactualAccuracyEvaluator(),
           QualityScoreEvaluator(),
           LengthEvaluator()
       ]
   )
   
   def run_daily_evaluation():
       """Run daily evaluation of recent LLM interactions."""
       
       # Get recent traces from last 24 hours
       recent_traces = tracer.get_traces(hours=24)
       
       # Run evaluation on subset
       sample_traces = recent_traces[:100]  # Evaluate 100 recent interactions
       
       results = pipeline.evaluate_traces(sample_traces)
       
       # Report results
       if results['average_score'] < 0.7:
           send_alert(f"Quality dropped to {results['average_score']:.2f}")
       
       print(f"Daily evaluation complete. Average score: {results['average_score']:.2f}")
   
   # Schedule daily evaluation
   schedule.every().day.at("09:00").do(run_daily_evaluation)
   
   def send_alert(message: str):
       """Send alert about quality issues."""
       # Integration with your alerting system
       print(f"ALERT: {message}")

Best Practices for Evaluation
------------------------------

**1. Start Simple**

.. code-block:: python

   # Begin with basic evaluators
   @evaluate(evaluator=LengthEvaluator())
   def simple_function():
       pass

**2. Use Multiple Metrics**

.. code-block:: python

   # Combine different evaluation perspectives
   evaluators = [
       FactualAccuracyEvaluator(),  # Correctness
       QualityScoreEvaluator(),     # Quality
       LengthEvaluator()            # Format
   ]

**3. Include Domain Knowledge**

.. code-block:: python

   class MedicalAccuracyEvaluator(BaseEvaluator):
       """Custom evaluator for medical domain."""
       def evaluate(self, input_text, output_text, context=None):
           # Domain-specific evaluation logic
           pass

**4. Monitor Evaluation Performance**

.. code-block:: python

   # Track evaluation metrics over time
   def track_evaluation_trends():
       results = get_recent_evaluations(days=7)
       trend = calculate_score_trend(results)
       
       if trend < -0.1:  # 10% decline
           alert_team("Evaluation scores declining")

**5. Use Evaluation for Model Selection**

.. code-block:: python

   def compare_models():
       """Compare different models using same evaluation criteria."""
       
       models = ["gpt-3.5-turbo", "gpt-4", "claude-3-sonnet"]
       evaluator = QualityScoreEvaluator()
       
       results = {}
       for model in models:
           # Test each model with same inputs
           model_results = evaluate_model(model, test_cases, evaluator)
           results[model] = model_results
       
       best_model = max(results.keys(), key=lambda k: results[k]['average_score'])
       print(f"Best performing model: {best_model}")

Troubleshooting Evaluation
---------------------------

**Common Issues:**

**Evaluation Taking Too Long**

.. code-block:: python

   # Use async evaluation for better performance
   @trace(tracer=tracer)
   @evaluate(evaluator=quality_evaluator, async_eval=True)
   def fast_function():
       pass

**Inconsistent Evaluation Results**

.. code-block:: python

   # Set random seed for LLM-based evaluators
   evaluator = SemanticSimilarityEvaluator(
       model="gpt-3.5-turbo",
       temperature=0.0  # Reduce randomness
   )

**Evaluation Errors**

.. code-block:: python

   # Add error handling to custom evaluators
   class RobustEvaluator(BaseEvaluator):
       def evaluate(self, input_text, output_text, context=None):
           try:
               # Evaluation logic
               return {"score": score, "feedback": feedback}
           except Exception as e:
               return {
                   "score": 0.0,
                   "feedback": f"Evaluation failed: {e}",
                   "error": True
               }

Viewing Results in HoneyHive Dashboard
---------------------------------------

Once you've set up evaluation:

1. **Navigate to your project** in the HoneyHive dashboard
2. **View Evaluation Tab** to see aggregated results
3. **Filter by evaluator** to focus on specific metrics
4. **Track trends over time** to monitor improvement
5. **Set up alerts** for quality thresholds

What's Next?
------------

You now have comprehensive evaluation set up! Next steps:

- :doc:`05-trace-enrichment` - Learn to enrich traces with metrics, feedback, and custom data
- :doc:`../how-to/evaluation/index` - Advanced evaluation patterns
- :doc:`../development/testing/ci-cd-integration` - Testing in CI/CD pipelines

Key Takeaways
-------------

- **Start with built-in evaluators** for common use cases
- **Create custom evaluators** for domain-specific needs
- **Use multiple evaluators** for comprehensive assessment
- **Set up automated pipelines** for continuous monitoring
- **Track trends over time** to measure improvement
- **Use evaluation results** to make data-driven decisions

.. tip::
   Evaluation is most valuable when integrated into your development workflow. Start simple, then expand your evaluation coverage as you learn what metrics matter most for your use case!
