Dashboard Tour
==============

.. note::
   **Tutorial Goal**: Master the HoneyHive dashboard to effectively monitor, analyze, and improve your LLM applications.

This tutorial provides a comprehensive tour of the HoneyHive dashboard, teaching you how to navigate, interpret data, and take action based on your observability insights.

What You'll Learn
-----------------

- How to navigate the HoneyHive dashboard effectively
- Understanding different views and their purposes
- Interpreting trace data and metrics
- Using filters and search functionality
- Setting up alerts and notifications
- Analyzing trends and performance patterns

Prerequisites
-------------

- Complete :doc:`04-evaluation-basics` tutorial
- Have traces and evaluation data in HoneyHive
- Access to your HoneyHive dashboard at `app.honeyhive.ai <https://app.honeyhive.ai>`_

Dashboard Overview
------------------

The HoneyHive dashboard is organized into several key sections:

**Main Navigation:**
- **Projects**: Overview of all your projects
- **Traces**: Detailed trace exploration
- **Evaluations**: Evaluation results and trends
- **Analytics**: Performance metrics and insights
- **Settings**: Configuration and team management

Let's explore each section in detail.

Projects Overview
-----------------

When you first log in, you'll see the **Projects** page:

**Project Cards Show:**
- Project name and description
- Recent activity (traces, evaluations)
- Key metrics (success rate, average latency)
- Team members with access

**Quick Actions:**
- Click a project to enter its dashboard
- Create new projects with the **+ New Project** button
- Search projects by name or filter by team

**Project Selection Best Practices:**
- Use descriptive project names (e.g., "customer-service-bot", "content-generation")
- Organize by environment (production, staging, development)
- Set up separate projects for different applications

Trace Explorer
--------------

The **Traces** section is where you'll spend most of your time analyzing LLM interactions.

**Trace List View**

The main traces page shows a chronological list of all traces:

.. code-block:: text

   Timestamp    | Function Name      | Status | Duration | Tokens | Model
   2024-01-15   | generate_response  | ✅     | 1.2s     | 150    | gpt-4
   2024-01-15   | analyze_sentiment  | ✅     | 0.8s     | 75     | gpt-3.5
   2024-01-15   | translate_text     | ❌     | 2.1s     | 200    | claude-3

**Key Columns:**
- **Status**: Success (✅), Error (❌), Warning (⚠️)
- **Duration**: Total execution time
- **Tokens**: Token usage (prompt + completion)
- **Model**: LLM model used
- **Cost**: Estimated API costs (if configured)

**Filtering and Search**

Use the powerful filtering system to find specific traces:

**Time Filters:**
- Last hour, day, week, month
- Custom date ranges
- Real-time updates

**Status Filters:**
- Success only
- Errors only
- Specific error types

**Function Filters:**
- Filter by function name
- Filter by event type
- Filter by custom attributes

**Example Searches:**
.. code-block:: text

   # Find all errors in the last 24 hours
   status:error AND timestamp:last_24h
   
   # Find expensive calls (high token usage)
   tokens:>500
   
   # Find specific model usage
   model:"gpt-4" AND customer_tier:"premium"
   
   # Find slow operations
   duration:>5s

**Trace Detail View**

Click any trace to see detailed information:

**Trace Timeline:**
- Visual representation of span hierarchy
- Timing breakdown for each operation
- Parent-child relationships between spans

**Span Details:**
- Input and output data
- Model parameters (temperature, max_tokens)
- Token usage breakdown
- Custom attributes and metadata

**Example Trace Detail:**
.. code-block:: text

   📊 customer_support_response
   ├── 🔍 validate_input (12ms)
   ├── 🤖 openai_completion (1,234ms)
   │   ├── Input: "How do I reset my password?"
   │   ├── Output: "To reset your password, visit..."
   │   ├── Model: gpt-3.5-turbo
   │   ├── Tokens: 45 prompt + 67 completion = 112 total
   │   └── Cost: $0.0002
   └── 📝 log_interaction (5ms)

**Error Analysis:**

For failed traces, you'll see:
- Exception type and message
- Stack trace
- Context leading to the error
- Suggested fixes (when available)

Evaluation Dashboard
--------------------

The **Evaluations** section shows how well your LLM applications are performing:

**Evaluation Overview**

**Key Metrics Dashboard:**
- Overall quality score
- Pass/fail rates by evaluator
- Trend charts over time
- Distribution of scores

**Example Metrics View:**
.. code-block:: text

   📈 Evaluation Summary (Last 7 Days)
   
   Overall Score: 8.2/10 (↗️ +0.3 from last week)
   
   📊 Evaluator Breakdown:
   ├── Factual Accuracy: 9.1/10 (142 evaluations)
   ├── Response Quality: 7.8/10 (142 evaluations)
   ├── Length Check: 8.7/10 (142 evaluations)
   └── Custom Domain: 7.5/10 (89 evaluations)
   
   🎯 Success Rate: 87% (124/142 passed threshold)

**Evaluation Trends**

Track how your LLM performance changes over time:

- **Daily/Weekly/Monthly** views
- **Score trends** for each evaluator
- **Volume trends** (number of evaluations)
- **Correlation analysis** between different metrics

**Evaluation Detail View**

Click any evaluation to see:
- Original input and output
- Score breakdown by criteria
- Detailed feedback from evaluators
- Comparison with similar evaluations
- Improvement suggestions

**Example Evaluation Detail:**

.. code-block:: json

   {
     "input": "Explain quantum computing to a 10-year-old",
     "output": "Quantum computing is like having a magical computer...",
     "evaluations": {
       "clarity": {
         "score": 8.5,
         "feedback": "Explanation is clear and age-appropriate"
       },
       "accuracy": {
         "score": 9.0,
         "feedback": "Scientifically accurate while remaining simple"
       },
       "engagement": {
         "score": 7.5,
         "feedback": "Good use of analogy, could be more interactive"
       }
     },
     "overall_score": 8.3,
     "suggestions": [
       "Consider adding a simple example or activity",
       "Use more concrete analogies for abstract concepts"
     ]
   }

Analytics and Insights
----------------------

The **Analytics** section provides high-level insights into your LLM application performance:

**Performance Analytics**

**Latency Analysis:**
- Average response times by model
- P95/P99 latency percentiles
- Geographic performance variations
- Time-of-day patterns

**Token Usage Analytics:**
- Token consumption trends
- Cost analysis by model
- Efficiency metrics (tokens per request)
- Budget tracking and projections

**Model Comparison:**
- Side-by-side model performance
- Cost vs. quality trade-offs
- Success rates by model
- User satisfaction correlation

**Usage Analytics**

**Request Volume:**
- Requests per hour/day/week
- Peak usage times
- Seasonal patterns
- Growth trends

**User Behavior:**
- Most common request types
- User journey analysis
- Feature adoption rates
- Error patterns by user segment

**Custom Dashboards**

Create custom dashboards for your specific needs:

**Business Metrics Dashboard:**
.. code-block:: text

   📊 Customer Support Bot Performance
   
   🎯 Resolution Rate: 94% (↗️ +2%)
   ⏱️ Avg Response Time: 1.2s (↙️ -0.1s)
   💰 Cost per Interaction: $0.003 (↙️ -15%)
   😊 Customer Satisfaction: 4.2/5 (↗️ +0.1)

**Technical Performance Dashboard:**
.. code-block:: text

   ⚡ System Performance
   
   🚀 Throughput: 450 req/min
   🎯 Success Rate: 99.2%
   ⏱️ P95 Latency: 2.1s
   💾 Memory Usage: 68%

Setting Up Alerts
-----------------

Stay informed about issues with intelligent alerting:

**Alert Types:**

**Performance Alerts:**
- Latency exceeds threshold
- Error rate spike
- Token usage budget exceeded
- Success rate drops below threshold

**Quality Alerts:**
- Evaluation scores drop below threshold
- Specific evaluator failures
- Trend degradation over time
- Custom metric violations

**Alert Configuration Example:**

.. code-block:: json

   {
     "name": "High Error Rate Alert",
     "condition": "error_rate > 5% over 10 minutes",
     "channels": ["email", "slack"],
     "severity": "critical",
     "actions": [
       "notify_on_call_engineer",
       "create_incident_ticket"
     ]
   }

**Alert Channels:**
- Email notifications
- Slack integration
- Webhook endpoints
- PagerDuty integration
- Custom notification systems

Advanced Dashboard Features
----------------------------

**Comparative Analysis**

Compare different time periods or configurations:

.. code-block:: text

   📊 Before/After Comparison
   
   Model Change: gpt-3.5-turbo → gpt-4
   
   Metric          | Before | After | Change
   Quality Score   | 7.2    | 8.7   | +21%
   Avg Latency     | 0.8s   | 1.4s  | +75%
   Cost per Call   | $0.001 | $0.004| +300%
   Success Rate    | 92%    | 97%   | +5%

**Cohort Analysis**

Track user groups over time:

.. code-block:: text

   👥 User Cohort Performance
   
   Cohort         | Week 1 | Week 2 | Week 3 | Week 4
   New Users      | 8.1    | 8.3    | 8.5    | 8.7
   Power Users    | 9.2    | 9.1    | 9.3    | 9.4
   Enterprise     | 8.8    | 9.0    | 9.1    | 9.2

**Custom Queries**

Use SQL-like queries for advanced analysis:

.. code-block:: sql

   SELECT 
     model,
     AVG(duration) as avg_latency,
     COUNT(*) as request_count,
     AVG(evaluation_score) as avg_quality
   FROM traces 
   WHERE timestamp > '2024-01-01'
     AND customer_tier = 'premium'
   GROUP BY model
   ORDER BY avg_quality DESC

Dashboard Best Practices
------------------------

**Daily Monitoring Routine:**

1. **Check Overview Metrics** (5 minutes)
   - Overall system health
   - Key performance indicators
   - Any active alerts

2. **Review Recent Errors** (10 minutes)
   - Investigate new error patterns
   - Check if errors are recurring
   - Identify root causes

3. **Analyze Performance Trends** (10 minutes)
   - Look for degradation patterns
   - Check evaluation score trends
   - Monitor cost and usage

**Weekly Deep Dive:**

1. **Quality Analysis** (30 minutes)
   - Review evaluation trends
   - Identify improvement opportunities
   - Compare different models/prompts

2. **Performance Optimization** (30 minutes)
   - Analyze latency patterns
   - Review token usage efficiency
   - Cost optimization opportunities

3. **User Experience Review** (20 minutes)
   - User satisfaction metrics
   - Feature adoption analysis
   - Support ticket correlation

**Monthly Strategic Review:**

1. **ROI Analysis**
   - Cost vs. value delivered
   - Efficiency improvements
   - Business impact metrics

2. **Technology Planning**
   - Model performance comparison
   - New feature evaluation
   - Scaling requirements

Troubleshooting Common Issues
------------------------------

**Missing Traces**

If you don't see expected traces:

1. **Check Project Selection**: Ensure you're in the right project
2. **Verify Time Range**: Expand the time filter
3. **Check Filters**: Clear any active filters
4. **Validate SDK Setup**: Ensure tracer is properly initialized

**Performance Issues**

If dashboard is slow:

1. **Narrow Time Range**: Use shorter time periods
2. **Add Filters**: Reduce data volume with specific filters
3. **Use Sampling**: Enable trace sampling for high-volume applications
4. **Check Network**: Verify internet connection stability

**Data Discrepancies**

If numbers don't match expectations:

1. **Check Timezone**: Ensure consistent timezone settings
2. **Verify Aggregation**: Understand how metrics are calculated
3. **Review Sampling**: Account for any sampling rates
4. **Time Lag**: Allow for data processing delays

Mobile Dashboard
----------------

Access insights on the go with the mobile-optimized dashboard:

**Mobile Features:**
- Responsive design for phones and tablets
- Key metrics at a glance
- Push notifications for critical alerts
- Offline viewing of cached data

**Mobile Best Practices:**
- Set up critical alerts for mobile notifications
- Use bookmark shortcuts for frequent views
- Configure simplified dashboards for mobile

Integration with Development Workflow
--------------------------------------

**CI/CD Integration:**

Connect dashboard insights with your development process:

.. code-block:: yaml

   # GitHub Actions example
   - name: Check LLM Quality
     run: |
       # Query HoneyHive API for recent evaluation scores
       quality_score=$(curl -H "Authorization: Bearer $HH_API_KEY" \
         "https://api.honeyhive.ai/evaluations/average?hours=1")
       
       if (( $(echo "$quality_score < 0.8" | bc -l) )); then
         echo "Quality score $quality_score below threshold"
         exit 1
       fi

**Code Review Integration:**

.. code-block:: python

   # Add dashboard links to pull requests
   @trace(tracer=tracer, metadata={"pr_number": "123"})
   def new_feature():
       pass
   
   # Dashboard automatically shows traces for this PR

Team Collaboration
------------------

**Sharing Insights:**

1. **Shareable Links**: Create links to specific dashboard views
2. **Scheduled Reports**: Automatically email dashboard summaries
3. **Embedded Dashboards**: Integrate key metrics into other tools
4. **Export Data**: Download data for external analysis

**Role-Based Access:**

- **Developers**: Full access to traces and technical metrics
- **Product Managers**: Focus on business metrics and user experience
- **Executives**: High-level dashboards with KPI summaries
- **Support Team**: Access to error traces and customer interactions

What's Next?
------------

You now know how to effectively use the HoneyHive dashboard! Next steps:

- :doc:`../how-to/monitoring/index` - Set up advanced monitoring
- :doc:`../how-to/testing/ci-cd-integration` - Integrate with your development workflow
- :doc:`../explanation/concepts/llm-observability` - Understand observability concepts

Key Takeaways
-------------

- **Start with the overview** to understand system health
- **Use filters effectively** to focus on relevant data
- **Set up meaningful alerts** to catch issues early
- **Regular monitoring routines** help maintain quality
- **Share insights** with your team for better collaboration
- **Integrate with development** workflow for continuous improvement

.. tip::
   The dashboard is most powerful when used consistently. Establish daily and weekly routines to review your LLM application performance, and use the insights to drive continuous improvement!
