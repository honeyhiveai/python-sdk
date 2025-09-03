Monitoring & Operations
=======================

Learn how to monitor LLM applications in production, set up alerting, and implement operational best practices for reliable AI systems.

.. toctree::
   :maxdepth: 2

Overview
--------

Production LLM applications require comprehensive monitoring to ensure reliability, performance, and cost effectiveness. HoneyHive provides rich observability data that can be used for operational excellence.

**Key Monitoring Areas**:
- Application performance and latency
- LLM provider health and costs
- Quality and accuracy metrics
- User experience indicators
- System reliability patterns

Quick Reference
---------------

**Key Monitoring Areas:**

- **Dashboards**: Visual monitoring and analysis interfaces
- **Alerting**: Proactive issue detection and notification systems
- **Performance Monitoring**: System performance optimization and tracking
- **Cost Tracking**: Cost analysis and optimization strategies
- **Reliability Patterns**: High-availability design patterns and practices

Getting Started
---------------

**1. Basic Health Monitoring**

.. code-block:: python

   from honeyhive import HoneyHiveTracer
   import time

   tracer = HoneyHiveTracer.init(
       api_key="your-api-key",
       project="production-app"
   )

   def health_check_endpoint():
       """Health check with monitoring."""
       
       with tracer.start_span("health_check") as span:
           span.set_attribute("health.endpoint", "/health")
           span.set_attribute("health.timestamp", time.time())
           
           # Check LLM provider health
           llm_healthy = check_llm_provider_health()
           span.set_attribute("health.llm_provider", llm_healthy)
           
           # Check database connectivity
           db_healthy = check_database_health()
           span.set_attribute("health.database", db_healthy)
           
           overall_health = llm_healthy and db_healthy
           span.set_attribute("health.overall", overall_health)
           
           if not overall_health:
               span.set_status("ERROR", "Health check failed")
           
           return {"healthy": overall_health, "timestamp": time.time()}

**2. Performance Metrics Collection**

.. code-block:: python

   class PerformanceMonitor:
       """Collect and track performance metrics."""
       
       def __init__(self, tracer):
           self.tracer = tracer
           self.metrics_buffer = []
       
       def track_llm_call(self, provider: str, model: str, latency_ms: float, 
                         tokens: int, cost_usd: float, quality_score: float):
           """Track individual LLM call metrics."""
           
           with self.tracer.start_span("performance_tracking") as span:
               span.set_attribute("perf.provider", provider)
               span.set_attribute("perf.model", model)
               span.set_attribute("perf.latency_ms", latency_ms)
               span.set_attribute("perf.tokens", tokens)
               span.set_attribute("perf.cost_usd", cost_usd)
               span.set_attribute("perf.quality_score", quality_score)
               span.set_attribute("perf.tokens_per_second", tokens / (latency_ms / 1000))
               span.set_attribute("perf.cost_per_token", cost_usd / tokens if tokens > 0 else 0)
               
               # Store for aggregation
               self.metrics_buffer.append({
                   "provider": provider,
                   "model": model,
                   "latency_ms": latency_ms,
                   "tokens": tokens,
                   "cost_usd": cost_usd,
                   "quality_score": quality_score,
                   "timestamp": time.time()
               })

**3. Alerting Setup**

.. code-block:: python

   class AlertingSystem:
       """Monitor key metrics and trigger alerts."""
       
       def __init__(self, tracer, alert_config: dict):
           self.tracer = tracer
           self.config = alert_config
       
       def check_performance_thresholds(self, metrics: dict):
           """Check if metrics exceed alert thresholds."""
           
           with self.tracer.start_span("alert_threshold_check") as span:
               alerts_triggered = []
               
               # Latency alerts
               if metrics.get("avg_latency_ms", 0) > self.config.get("max_latency_ms", 5000):
                   alert = {
                       "type": "high_latency",
                       "value": metrics["avg_latency_ms"],
                       "threshold": self.config["max_latency_ms"],
                       "severity": "warning"
                   }
                   alerts_triggered.append(alert)
               
               # Quality alerts
               if metrics.get("avg_quality_score", 1.0) < self.config.get("min_quality_score", 0.8):
                   alert = {
                       "type": "low_quality",
                       "value": metrics["avg_quality_score"],
                       "threshold": self.config["min_quality_score"],
                       "severity": "critical"
                   }
                   alerts_triggered.append(alert)
               
               # Cost alerts
               hourly_cost = metrics.get("hourly_cost_usd", 0)
               if hourly_cost > self.config.get("max_hourly_cost_usd", 100):
                   alert = {
                       "type": "high_cost",
                       "value": hourly_cost,
                       "threshold": self.config["max_hourly_cost_usd"],
                       "severity": "warning"
                   }
                   alerts_triggered.append(alert)
               
               span.set_attribute("alerts.triggered_count", len(alerts_triggered))
               span.set_attribute("alerts.types", [a["type"] for a in alerts_triggered])
               
               return alerts_triggered

Production Monitoring Patterns
------------------------------

**Real-Time Health Dashboard**

.. code-block:: python

   class RealTimeHealthDashboard:
       """Real-time health monitoring for production systems."""
       
       def __init__(self, tracer):
           self.tracer = tracer
           self.health_metrics = {}
           self.update_interval = 30  # seconds
       
       def collect_health_metrics(self):
           """Collect comprehensive health metrics."""
           
           with self.tracer.start_span("health_metrics_collection") as span:
               span.set_attribute("collection.timestamp", time.time())
               
               # System health
               system_health = self._collect_system_health()
               span.set_attribute("health.system_score", system_health["score"])
               
               # LLM provider health
               provider_health = self._collect_provider_health()
               span.set_attribute("health.provider_score", provider_health["score"])
               
               # Application health
               app_health = self._collect_application_health()
               span.set_attribute("health.application_score", app_health["score"])
               
               # Quality health
               quality_health = self._collect_quality_health()
               span.set_attribute("health.quality_score", quality_health["score"])
               
               overall_health = {
                   "timestamp": time.time(),
                   "overall_score": (
                       system_health["score"] + 
                       provider_health["score"] + 
                       app_health["score"] + 
                       quality_health["score"]
                   ) / 4,
                   "components": {
                       "system": system_health,
                       "providers": provider_health,
                       "application": app_health,
                       "quality": quality_health
                   }
               }
               
               span.set_attribute("health.overall_score", overall_health["overall_score"])
               self.health_metrics = overall_health
               
               return overall_health
       
       def _collect_system_health(self):
           """Collect system-level health metrics."""
           
           with self.tracer.start_span("system_health_check") as span:
               import psutil
               
               # CPU usage
               cpu_percent = psutil.cpu_percent(interval=1)
               span.set_attribute("system.cpu_percent", cpu_percent)
               
               # Memory usage
               memory = psutil.virtual_memory()
               memory_percent = memory.percent
               span.set_attribute("system.memory_percent", memory_percent)
               
               # Disk usage
               disk = psutil.disk_usage('/')
               disk_percent = (disk.used / disk.total) * 100
               span.set_attribute("system.disk_percent", disk_percent)
               
               # Calculate health score
               health_score = 1.0
               if cpu_percent > 80:
                   health_score -= 0.3
               if memory_percent > 85:
                   health_score -= 0.4
               if disk_percent > 90:
                   health_score -= 0.3
               
               health_score = max(0, health_score)
               span.set_attribute("system.health_score", health_score)
               
               return {
                   "score": health_score,
                   "cpu_percent": cpu_percent,
                   "memory_percent": memory_percent,
                   "disk_percent": disk_percent
               }
       
       def _collect_provider_health(self):
           """Check LLM provider health and performance."""
           
           with self.tracer.start_span("provider_health_check") as span:
               provider_results = {}
               overall_score = 0
               
               providers = ["openai", "anthropic", "google"]
               
               for provider in providers:
                   with self.tracer.start_span(f"provider_{provider}_check") as provider_span:
                       try:
                           # Simple health check call
                           start_time = time.time()
                           health_response = self._test_provider_health(provider)
                           latency = (time.time() - start_time) * 1000
                           
                           provider_span.set_attribute("provider.name", provider)
                           provider_span.set_attribute("provider.latency_ms", latency)
                           provider_span.set_attribute("provider.healthy", health_response["healthy"])
                           
                           # Score based on latency and availability
                           if health_response["healthy"]:
                               if latency < 1000:
                                   score = 1.0
                               elif latency < 3000:
                                   score = 0.7
                               else:
                                   score = 0.4
                           else:
                               score = 0.0
                           
                           provider_results[provider] = {
                               "healthy": health_response["healthy"],
                               "latency_ms": latency,
                               "score": score
                           }
                           
                           overall_score += score
                           
                       except Exception as e:
                           provider_span.set_attribute("provider.error", str(e))
                           provider_span.set_status("ERROR", str(e))
                           provider_results[provider] = {"healthy": False, "score": 0.0}
               
               overall_score = overall_score / len(providers) if providers else 0
               span.set_attribute("providers.overall_score", overall_score)
               
               return {
                   "score": overall_score,
                   "providers": provider_results
               }

**Cost Monitoring and Budgeting**

.. code-block:: python

   class CostMonitoringSystem:
       """Monitor and control LLM usage costs."""
       
       def __init__(self, tracer, budget_config: dict):
           self.tracer = tracer
           self.budget_config = budget_config
           self.cost_tracking = {}
       
       def track_usage_cost(self, provider: str, model: str, tokens: int, cost_usd: float):
           """Track individual usage costs."""
           
           with self.tracer.start_span("cost_tracking") as span:
               span.set_attribute("cost.provider", provider)
               span.set_attribute("cost.model", model)
               span.set_attribute("cost.tokens", tokens)
               span.set_attribute("cost.amount_usd", cost_usd)
               span.set_attribute("cost.timestamp", time.time())
               
               # Update tracking
               today = time.strftime("%Y-%m-%d")
               if today not in self.cost_tracking:
                   self.cost_tracking[today] = {"total": 0, "by_provider": {}, "by_model": {}}
               
               self.cost_tracking[today]["total"] += cost_usd
               
               if provider not in self.cost_tracking[today]["by_provider"]:
                   self.cost_tracking[today]["by_provider"][provider] = 0
               self.cost_tracking[today]["by_provider"][provider] += cost_usd
               
               model_key = f"{provider}:{model}"
               if model_key not in self.cost_tracking[today]["by_model"]:
                   self.cost_tracking[today]["by_model"][model_key] = 0
               self.cost_tracking[today]["by_model"][model_key] += cost_usd
               
               # Check budget thresholds
               daily_budget = self.budget_config.get("daily_budget_usd", 1000)
               today_spend = self.cost_tracking[today]["total"]
               budget_utilization = today_spend / daily_budget
               
               span.set_attribute("budget.daily_limit_usd", daily_budget)
               span.set_attribute("budget.today_spend_usd", today_spend)
               span.set_attribute("budget.utilization_percent", budget_utilization * 100)
               
               # Alert if approaching budget
               if budget_utilization > 0.8:
                   span.set_attribute("budget.alert_triggered", True)
                   self._trigger_budget_alert(today_spend, daily_budget, budget_utilization)
               
               return {
                   "daily_spend": today_spend,
                   "budget_utilization": budget_utilization,
                   "alert_triggered": budget_utilization > 0.8
               }
       
       def generate_cost_report(self, days: int = 7):
           """Generate cost analysis report."""
           
           with self.tracer.start_span("cost_report_generation") as span:
               span.set_attribute("report.days", days)
               
               # Collect data for last N days
               report_data = {}
               total_cost = 0
               
               for i in range(days):
                   date = time.strftime("%Y-%m-%d", time.localtime(time.time() - (i * 86400)))
                   if date in self.cost_tracking:
                       report_data[date] = self.cost_tracking[date]
                       total_cost += self.cost_tracking[date]["total"]
               
               # Analysis
               avg_daily_cost = total_cost / days if days > 0 else 0
               projected_monthly_cost = avg_daily_cost * 30
               
               # Find top spending providers and models
               provider_totals = {}
               model_totals = {}
               
               for date_data in report_data.values():
                   for provider, cost in date_data["by_provider"].items():
                       provider_totals[provider] = provider_totals.get(provider, 0) + cost
                   for model, cost in date_data["by_model"].items():
                       model_totals[model] = model_totals.get(model, 0) + cost
               
               top_provider = max(provider_totals.items(), key=lambda x: x[1]) if provider_totals else ("none", 0)
               top_model = max(model_totals.items(), key=lambda x: x[1]) if model_totals else ("none", 0)
               
               span.set_attribute("report.total_cost_usd", total_cost)
               span.set_attribute("report.avg_daily_cost_usd", avg_daily_cost)
               span.set_attribute("report.projected_monthly_cost_usd", projected_monthly_cost)
               span.set_attribute("report.top_provider", top_provider[0])
               span.set_attribute("report.top_model", top_model[0])
               
               return {
                   "period_days": days,
                   "total_cost": total_cost,
                   "avg_daily_cost": avg_daily_cost,
                   "projected_monthly_cost": projected_monthly_cost,
                   "top_provider": top_provider,
                   "top_model": top_model,
                   "daily_breakdown": report_data,
                   "provider_totals": provider_totals,
                   "model_totals": model_totals
               }

**Quality Monitoring System**

.. code-block:: python

   class QualityMonitoringSystem:
       """Monitor output quality and detect degradation."""
       
       def __init__(self, tracer, quality_config: dict):
           self.tracer = tracer
           self.config = quality_config
           self.quality_history = []
           self.quality_window_size = quality_config.get("window_size", 100)
       
       def track_quality_metrics(self, evaluation_result: dict):
           """Track quality metrics for trend analysis."""
           
           with self.tracer.start_span("quality_tracking") as span:
               quality_entry = {
                   "timestamp": time.time(),
                   "score": evaluation_result.get("score", 0),
                   "metrics": evaluation_result.get("metrics", {}),
                   "evaluator": evaluation_result.get("evaluator", "unknown")
               }
               
               self.quality_history.append(quality_entry)
               
               # Maintain sliding window
               if len(self.quality_history) > self.quality_window_size:
                   self.quality_history.pop(0)
               
               span.set_attribute("quality.current_score", quality_entry["score"])
               span.set_attribute("quality.history_size", len(self.quality_history))
               
               # Calculate trends
               if len(self.quality_history) >= 10:
                   recent_scores = [q["score"] for q in self.quality_history[-10:]]
                   older_scores = [q["score"] for q in self.quality_history[-20:-10]] if len(self.quality_history) >= 20 else []
                   
                   recent_avg = sum(recent_scores) / len(recent_scores)
                   older_avg = sum(older_scores) / len(older_scores) if older_scores else recent_avg
                   
                   trend = "improving" if recent_avg > older_avg else "declining" if recent_avg < older_avg else "stable"
                   trend_magnitude = abs(recent_avg - older_avg)
                   
                   span.set_attribute("quality.trend", trend)
                   span.set_attribute("quality.trend_magnitude", trend_magnitude)
                   span.set_attribute("quality.recent_avg", recent_avg)
                   
                   # Alert on significant quality decline
                   if trend == "declining" and trend_magnitude > self.config.get("decline_threshold", 0.1):
                       span.set_attribute("quality.decline_alert", True)
                       self._trigger_quality_decline_alert(recent_avg, older_avg, trend_magnitude)
               
               return quality_entry
       
       def generate_quality_report(self):
           """Generate comprehensive quality analysis."""
           
           with self.tracer.start_span("quality_report_generation") as span:
               if not self.quality_history:
                   span.set_attribute("report.no_data", True)
                   return {"error": "No quality data available"}
               
               # Overall statistics
               all_scores = [q["score"] for q in self.quality_history]
               avg_score = sum(all_scores) / len(all_scores)
               min_score = min(all_scores)
               max_score = max(all_scores)
               
               # Time-based analysis
               now = time.time()
               last_hour_scores = [q["score"] for q in self.quality_history if now - q["timestamp"] <= 3600]
               last_day_scores = [q["score"] for q in self.quality_history if now - q["timestamp"] <= 86400]
               
               last_hour_avg = sum(last_hour_scores) / len(last_hour_scores) if last_hour_scores else 0
               last_day_avg = sum(last_day_scores) / len(last_day_scores) if last_day_scores else 0
               
               # Quality distribution
               score_buckets = {"high": 0, "medium": 0, "low": 0}
               for score in all_scores:
                   if score >= 0.8:
                       score_buckets["high"] += 1
                   elif score >= 0.6:
                       score_buckets["medium"] += 1
                   else:
                       score_buckets["low"] += 1
               
               span.set_attribute("report.avg_score", avg_score)
               span.set_attribute("report.min_score", min_score)
               span.set_attribute("report.max_score", max_score)
               span.set_attribute("report.last_hour_avg", last_hour_avg)
               span.set_attribute("report.last_day_avg", last_day_avg)
               span.set_attribute("report.high_quality_percent", (score_buckets["high"] / len(all_scores)) * 100)
               
               return {
                   "overall_stats": {
                       "avg_score": avg_score,
                       "min_score": min_score,
                       "max_score": max_score,
                       "total_samples": len(all_scores)
                   },
                   "time_based": {
                       "last_hour_avg": last_hour_avg,
                       "last_day_avg": last_day_avg,
                       "samples_last_hour": len(last_hour_scores),
                       "samples_last_day": len(last_day_scores)
                   },
                   "distribution": score_buckets,
                   "quality_percentage": {
                       "high": (score_buckets["high"] / len(all_scores)) * 100,
                       "medium": (score_buckets["medium"] / len(all_scores)) * 100,
                       "low": (score_buckets["low"] / len(all_scores)) * 100
                   }
               }

Operational Best Practices
--------------------------

**1. Monitoring Hierarchy**

.. code-block:: python

   # Good: Layered monitoring approach
   monitoring_layers = {
       "infrastructure": ["cpu", "memory", "disk", "network"],
       "application": ["response_time", "error_rate", "throughput"],
       "business": ["user_satisfaction", "conversion_rate", "quality_score"],
       "cost": ["token_usage", "api_costs", "budget_utilization"]
   }

**2. Alert Fatigue Prevention**

.. code-block:: python

   class SmartAlertingSystem:
       """Prevent alert fatigue with intelligent alerting."""
       
       def __init__(self, tracer):
           self.tracer = tracer
           self.alert_history = {}
           self.suppression_windows = {
               "low": 300,     # 5 minutes
               "medium": 900,  # 15 minutes
               "high": 1800,   # 30 minutes
               "critical": 0   # Never suppress
           }
       
       def should_send_alert(self, alert_type: str, severity: str) -> bool:
           """Determine if alert should be sent based on history."""
           
           with self.tracer.start_span("alert_suppression_check") as span:
               span.set_attribute("alert.type", alert_type)
               span.set_attribute("alert.severity", severity)
               
               now = time.time()
               last_sent = self.alert_history.get(alert_type, 0)
               suppression_window = self.suppression_windows.get(severity, 300)
               
               should_send = (now - last_sent) > suppression_window
               
               span.set_attribute("alert.last_sent_ago", now - last_sent)
               span.set_attribute("alert.suppression_window", suppression_window)
               span.set_attribute("alert.should_send", should_send)
               
               if should_send:
                   self.alert_history[alert_type] = now
               
               return should_send

**3. Performance Baselines**

.. code-block:: python

   # Establish and maintain performance baselines
   def establish_performance_baseline(historical_data: list):
       """Establish performance baselines from historical data."""
       
       baselines = {}
       
       for metric in ["latency_ms", "quality_score", "cost_per_request"]:
           values = [d.get(metric, 0) for d in historical_data if metric in d]
           
           if values:
               baselines[metric] = {
                   "p50": sorted(values)[len(values) // 2],
                   "p95": sorted(values)[int(len(values) * 0.95)],
                   "p99": sorted(values)[int(len(values) * 0.99)],
                   "avg": sum(values) / len(values),
                   "samples": len(values)
               }
       
       return baselines

See Also
--------

- :doc:`../evaluation/index` - Evaluation and quality analysis
- :doc:`../advanced-tracing/custom-spans` - Advanced tracing techniques
- :doc:`../integrations/multi-provider` - Multi-provider reliability
- :doc:`../../reference/api/tracer` - HoneyHiveTracer API reference
