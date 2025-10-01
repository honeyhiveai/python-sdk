# Implementation Plan - Deployment and Rollout Strategy

**Version**: 1.0  
**Date**: 2025-01-27  
**Status**: Implementation Ready  

## 1. Deployment Strategy Overview

### 1.1 Deployment Philosophy

The Universal LLM Discovery Engine deployment follows a **zero-downtime, risk-minimized** approach:

- **Gradual Rollout**: Phased deployment with increasing traffic percentages
- **Feature Flags**: Runtime control over engine selection and behavior
- **Immediate Rollback**: Instant fallback to legacy system if issues arise
- **Comprehensive Monitoring**: Real-time performance and accuracy tracking
- **Production Validation**: Continuous comparison with legacy system

### 1.2 Deployment Phases

```
Phase 1: Infrastructure Setup (Day 1)
├── Backup current implementation
├── Deploy new code with feature flags disabled
├── Initialize monitoring and alerting
└── Validate deployment integrity

Phase 2: Shadow Mode (Days 2-3)
├── Enable comparison mode (0% traffic to new engine)
├── Process all requests with both engines
├── Compare results and performance
└── Tune configuration based on findings

Phase 3: Canary Deployment (Days 4-7)
├── Route 5% traffic to new engine
├── Monitor error rates and performance
├── Gradually increase to 25% if stable
└── Collect production feedback

Phase 4: Progressive Rollout (Days 8-14)
├── Increase to 50% traffic
├── Monitor stability and performance
├── Increase to 75% if metrics are good
└── Prepare for full rollout

Phase 5: Full Deployment (Days 15-21)
├── Route 100% traffic to new engine
├── Disable legacy fallback after validation
├── Remove legacy code after soak period
└── Complete deployment documentation
```

## 2. Infrastructure and Environment Setup

### 2.1 Environment Configuration

```python
# deployment/config/environment_config.py

"""
Environment-specific configuration for Universal LLM Discovery Engine deployment.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class DeploymentConfig:
    """Configuration for deployment environment."""
    
    # Environment identification
    environment: str  # dev, staging, prod
    deployment_version: str
    rollout_phase: int
    
    # Feature flags
    universal_engine_enabled: bool
    comparison_mode_enabled: bool
    legacy_fallback_enabled: bool
    performance_monitoring_enabled: bool
    
    # Performance thresholds
    max_latency_ms: float
    max_error_rate_percent: float
    min_cache_hit_rate_percent: float
    max_memory_usage_mb: int
    
    # Rollout configuration
    traffic_percentage: int
    rollback_threshold_error_rate: float
    rollback_threshold_latency_ms: float
    
    # Monitoring configuration
    metrics_collection_enabled: bool
    detailed_logging_enabled: bool
    alert_webhook_url: Optional[str]

class EnvironmentManager:
    """Manage environment-specific deployment configuration."""
    
    def __init__(self):
        self.configs = {
            "development": DeploymentConfig(
                environment="development",
                deployment_version="1.0.0-dev",
                rollout_phase=1,
                universal_engine_enabled=True,
                comparison_mode_enabled=True,
                legacy_fallback_enabled=True,
                performance_monitoring_enabled=True,
                max_latency_ms=50.0,  # More lenient for dev
                max_error_rate_percent=5.0,
                min_cache_hit_rate_percent=70.0,
                max_memory_usage_mb=200,
                traffic_percentage=100,  # Full testing in dev
                rollback_threshold_error_rate=10.0,
                rollback_threshold_latency_ms=100.0,
                metrics_collection_enabled=True,
                detailed_logging_enabled=True,
                alert_webhook_url=None
            ),
            "staging": DeploymentConfig(
                environment="staging",
                deployment_version="1.0.0-rc",
                rollout_phase=3,
                universal_engine_enabled=True,
                comparison_mode_enabled=True,
                legacy_fallback_enabled=True,
                performance_monitoring_enabled=True,
                max_latency_ms=20.0,
                max_error_rate_percent=2.0,
                min_cache_hit_rate_percent=85.0,
                max_memory_usage_mb=150,
                traffic_percentage=50,  # Partial rollout in staging
                rollback_threshold_error_rate=5.0,
                rollback_threshold_latency_ms=50.0,
                metrics_collection_enabled=True,
                detailed_logging_enabled=True,
                alert_webhook_url=os.getenv("STAGING_ALERT_WEBHOOK")
            ),
            "production": DeploymentConfig(
                environment="production",
                deployment_version="1.0.0",
                rollout_phase=2,  # Start with shadow mode
                universal_engine_enabled=False,  # Start disabled
                comparison_mode_enabled=True,   # Enable comparison first
                legacy_fallback_enabled=True,
                performance_monitoring_enabled=True,
                max_latency_ms=10.0,  # Strict production requirements
                max_error_rate_percent=0.1,
                min_cache_hit_rate_percent=90.0,
                max_memory_usage_mb=100,
                traffic_percentage=0,  # Start with 0% traffic
                rollback_threshold_error_rate=1.0,
                rollback_threshold_latency_ms=25.0,
                metrics_collection_enabled=True,
                detailed_logging_enabled=False,  # Reduce log volume in prod
                alert_webhook_url=os.getenv("PROD_ALERT_WEBHOOK")
            )
        }
    
    def get_config(self, environment: str) -> DeploymentConfig:
        """Get configuration for specified environment."""
        if environment not in self.configs:
            raise ValueError(f"Unknown environment: {environment}")
        return self.configs[environment]
    
    def update_rollout_phase(self, environment: str, phase: int, traffic_percentage: int) -> None:
        """Update rollout phase and traffic percentage."""
        config = self.get_config(environment)
        config.rollout_phase = phase
        config.traffic_percentage = traffic_percentage
        
        # Adjust feature flags based on phase
        if phase == 1:  # Infrastructure setup
            config.universal_engine_enabled = False
            config.comparison_mode_enabled = False
        elif phase == 2:  # Shadow mode
            config.universal_engine_enabled = False
            config.comparison_mode_enabled = True
        elif phase >= 3:  # Canary and beyond
            config.universal_engine_enabled = True
            config.comparison_mode_enabled = True
        
        if phase >= 5 and traffic_percentage == 100:  # Full deployment
            config.comparison_mode_enabled = False
            config.legacy_fallback_enabled = False
```

### 2.2 Feature Flag Management

```python
# deployment/feature_flags/flag_manager.py

"""
Feature flag management for Universal LLM Discovery Engine rollout.
"""

import os
import json
import time
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class FeatureFlag:
    """Individual feature flag configuration."""
    
    name: str
    enabled: bool
    rollout_percentage: int  # 0-100
    conditions: Dict[str, Any]
    created_at: float
    updated_at: float
    description: str

class FeatureFlagManager:
    """Manage feature flags for gradual rollout."""
    
    def __init__(self, config_source: str = "environment"):
        self.config_source = config_source
        self.flags: Dict[str, FeatureFlag] = {}
        self.evaluation_cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Initialize default flags
        self._initialize_default_flags()
        
        # Load configuration
        self._load_configuration()
    
    def _initialize_default_flags(self) -> None:
        """Initialize default feature flags for Universal Engine."""
        current_time = time.time()
        
        default_flags = {
            "universal_engine_enabled": FeatureFlag(
                name="universal_engine_enabled",
                enabled=False,
                rollout_percentage=0,
                conditions={},
                created_at=current_time,
                updated_at=current_time,
                description="Enable Universal LLM Discovery Engine"
            ),
            "comparison_mode_enabled": FeatureFlag(
                name="comparison_mode_enabled",
                enabled=False,
                rollout_percentage=0,
                conditions={},
                created_at=current_time,
                updated_at=current_time,
                description="Enable comparison mode between engines"
            ),
            "legacy_fallback_enabled": FeatureFlag(
                name="legacy_fallback_enabled",
                enabled=True,
                rollout_percentage=100,
                conditions={},
                created_at=current_time,
                updated_at=current_time,
                description="Enable fallback to legacy engine on errors"
            ),
            "performance_monitoring_enabled": FeatureFlag(
                name="performance_monitoring_enabled",
                enabled=True,
                rollout_percentage=100,
                conditions={},
                created_at=current_time,
                updated_at=current_time,
                description="Enable detailed performance monitoring"
            ),
            "detailed_logging_enabled": FeatureFlag(
                name="detailed_logging_enabled",
                enabled=False,
                rollout_percentage=0,
                conditions={"environment": ["development", "staging"]},
                created_at=current_time,
                updated_at=current_time,
                description="Enable detailed debug logging"
            )
        }
        
        self.flags.update(default_flags)
    
    def _load_configuration(self) -> None:
        """Load feature flag configuration from source."""
        if self.config_source == "environment":
            self._load_from_environment()
        elif self.config_source == "file":
            self._load_from_file()
        # Could add database, remote config service, etc.
    
    def _load_from_environment(self) -> None:
        """Load feature flags from environment variables."""
        for flag_name in self.flags.keys():
            env_var = f"HONEYHIVE_FEATURE_{flag_name.upper()}"
            env_value = os.getenv(env_var)
            
            if env_value is not None:
                try:
                    # Parse boolean values
                    if env_value.lower() in ("true", "1", "yes", "on"):
                        self.flags[flag_name].enabled = True
                        self.flags[flag_name].rollout_percentage = 100
                    elif env_value.lower() in ("false", "0", "no", "off"):
                        self.flags[flag_name].enabled = False
                        self.flags[flag_name].rollout_percentage = 0
                    else:
                        # Try to parse as percentage
                        percentage = int(env_value)
                        if 0 <= percentage <= 100:
                            self.flags[flag_name].enabled = percentage > 0
                            self.flags[flag_name].rollout_percentage = percentage
                    
                    self.flags[flag_name].updated_at = time.time()
                    
                except (ValueError, TypeError) as e:
                    logger.warning(f"Invalid value for {env_var}: {env_value}, error: {e}")
    
    def is_enabled(self, flag_name: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Check if a feature flag is enabled for given context."""
        if flag_name not in self.flags:
            logger.warning(f"Unknown feature flag: {flag_name}")
            return False
        
        flag = self.flags[flag_name]
        
        # Check basic enabled status
        if not flag.enabled:
            return False
        
        # Check rollout percentage
        if flag.rollout_percentage < 100:
            # Use deterministic hash for consistent rollout
            hash_input = f"{flag_name}:{context.get('user_id', 'anonymous') if context else 'anonymous'}"
            hash_value = hash(hash_input) % 100
            
            if hash_value >= flag.rollout_percentage:
                return False
        
        # Check conditions
        if flag.conditions and context:
            for condition_key, condition_values in flag.conditions.items():
                if condition_key in context:
                    if context[condition_key] not in condition_values:
                        return False
        
        return True
    
    def update_flag(self, flag_name: str, enabled: bool, rollout_percentage: int = None) -> None:
        """Update a feature flag configuration."""
        if flag_name not in self.flags:
            raise ValueError(f"Unknown feature flag: {flag_name}")
        
        flag = self.flags[flag_name]
        flag.enabled = enabled
        
        if rollout_percentage is not None:
            if not 0 <= rollout_percentage <= 100:
                raise ValueError("Rollout percentage must be between 0 and 100")
            flag.rollout_percentage = rollout_percentage
        
        flag.updated_at = time.time()
        
        # Clear evaluation cache
        self.evaluation_cache.clear()
        
        logger.info(f"Updated feature flag {flag_name}: enabled={enabled}, rollout={flag.rollout_percentage}%")
    
    def get_flag_status(self) -> Dict[str, Dict[str, Any]]:
        """Get current status of all feature flags."""
        return {
            name: {
                "enabled": flag.enabled,
                "rollout_percentage": flag.rollout_percentage,
                "conditions": flag.conditions,
                "updated_at": flag.updated_at,
                "description": flag.description
            }
            for name, flag in self.flags.items()
        }
    
    def gradual_rollout(self, flag_name: str, target_percentage: int, step_size: int = 10, 
                       step_duration_minutes: int = 30) -> None:
        """Gradually roll out a feature flag to target percentage."""
        if flag_name not in self.flags:
            raise ValueError(f"Unknown feature flag: {flag_name}")
        
        flag = self.flags[flag_name]
        current_percentage = flag.rollout_percentage
        
        logger.info(f"Starting gradual rollout of {flag_name} from {current_percentage}% to {target_percentage}%")
        
        # This would typically be handled by a background job or external system
        # For now, we'll just update to the target percentage
        self.update_flag(flag_name, target_percentage > 0, target_percentage)
```

## 3. Monitoring and Observability

### 3.1 Deployment Monitoring

```python
# deployment/monitoring/deployment_monitor.py

"""
Comprehensive monitoring for Universal LLM Discovery Engine deployment.
"""

import time
import logging
import statistics
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
import threading

logger = logging.getLogger(__name__)

@dataclass
class DeploymentMetrics:
    """Metrics collected during deployment."""
    
    # Request metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # Engine usage metrics
    universal_engine_requests: int = 0
    legacy_engine_requests: int = 0
    fallback_events: int = 0
    
    # Performance metrics
    response_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    universal_response_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    legacy_response_times: deque = field(default_factory=lambda: deque(maxlen=1000))
    
    # Accuracy metrics
    comparison_matches: int = 0
    comparison_mismatches: int = 0
    
    # Resource metrics
    memory_usage_samples: deque = field(default_factory=lambda: deque(maxlen=100))
    cpu_usage_samples: deque = field(default_factory=lambda: deque(maxlen=100))
    
    # Error tracking
    error_types: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    error_messages: deque = field(default_factory=lambda: deque(maxlen=50))
    
    # Timestamps
    start_time: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)

class DeploymentMonitor:
    """Monitor deployment health and performance."""
    
    def __init__(self, alert_callback: Optional[Callable] = None):
        self.metrics = DeploymentMetrics()
        self.alert_callback = alert_callback
        self.monitoring_active = True
        self.alert_thresholds = {
            "error_rate_percent": 1.0,
            "avg_response_time_ms": 25.0,
            "p95_response_time_ms": 50.0,
            "fallback_rate_percent": 5.0,
            "memory_usage_mb": 150,
            "comparison_mismatch_rate_percent": 2.0
        }
        
        # Start background monitoring
        self.monitoring_thread = threading.Thread(target=self._background_monitoring, daemon=True)
        self.monitoring_thread.start()
    
    def record_request(self, engine_type: str, response_time_ms: float, success: bool, 
                      comparison_match: Optional[bool] = None, error: Optional[Exception] = None) -> None:
        """Record metrics for a processed request."""
        self.metrics.total_requests += 1
        self.metrics.last_updated = time.time()
        
        # Record success/failure
        if success:
            self.metrics.successful_requests += 1
        else:
            self.metrics.failed_requests += 1
            
            if error:
                error_type = type(error).__name__
                self.metrics.error_types[error_type] += 1
                self.metrics.error_messages.append(f"{error_type}: {str(error)}")
        
        # Record engine usage
        if engine_type == "universal":
            self.metrics.universal_engine_requests += 1
            self.metrics.universal_response_times.append(response_time_ms)
        elif engine_type == "legacy":
            self.metrics.legacy_engine_requests += 1
            self.metrics.legacy_response_times.append(response_time_ms)
        elif engine_type == "fallback":
            self.metrics.fallback_events += 1
            self.metrics.legacy_response_times.append(response_time_ms)
        
        # Record overall response time
        self.metrics.response_times.append(response_time_ms)
        
        # Record comparison results
        if comparison_match is not None:
            if comparison_match:
                self.metrics.comparison_matches += 1
            else:
                self.metrics.comparison_mismatches += 1
    
    def record_resource_usage(self, memory_mb: float, cpu_percent: float) -> None:
        """Record resource usage metrics."""
        self.metrics.memory_usage_samples.append(memory_mb)
        self.metrics.cpu_usage_samples.append(cpu_percent)
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current deployment metrics."""
        total_requests = self.metrics.total_requests
        
        if total_requests == 0:
            return {"status": "no_data", "total_requests": 0}
        
        # Calculate rates
        error_rate = (self.metrics.failed_requests / total_requests) * 100
        fallback_rate = (self.metrics.fallback_events / total_requests) * 100 if total_requests > 0 else 0
        
        # Calculate response time statistics
        response_times = list(self.metrics.response_times)
        avg_response_time = statistics.mean(response_times) if response_times else 0
        p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else max(response_times) if response_times else 0
        
        # Calculate comparison accuracy
        total_comparisons = self.metrics.comparison_matches + self.metrics.comparison_mismatches
        comparison_accuracy = (self.metrics.comparison_matches / total_comparisons) * 100 if total_comparisons > 0 else 100
        
        # Calculate resource usage
        memory_samples = list(self.metrics.memory_usage_samples)
        avg_memory_usage = statistics.mean(memory_samples) if memory_samples else 0
        max_memory_usage = max(memory_samples) if memory_samples else 0
        
        return {
            "status": "active",
            "total_requests": total_requests,
            "success_rate_percent": (self.metrics.successful_requests / total_requests) * 100,
            "error_rate_percent": error_rate,
            "fallback_rate_percent": fallback_rate,
            "avg_response_time_ms": avg_response_time,
            "p95_response_time_ms": p95_response_time,
            "comparison_accuracy_percent": comparison_accuracy,
            "universal_engine_usage_percent": (self.metrics.universal_engine_requests / total_requests) * 100,
            "avg_memory_usage_mb": avg_memory_usage,
            "max_memory_usage_mb": max_memory_usage,
            "error_types": dict(self.metrics.error_types),
            "uptime_seconds": time.time() - self.metrics.start_time
        }
    
    def check_health(self) -> Dict[str, Any]:
        """Check deployment health against thresholds."""
        metrics = self.get_current_metrics()
        
        if metrics["status"] == "no_data":
            return {"status": "unknown", "issues": ["No data available"]}
        
        issues = []
        warnings = []
        
        # Check error rate
        if metrics["error_rate_percent"] > self.alert_thresholds["error_rate_percent"]:
            issues.append(f"High error rate: {metrics['error_rate_percent']:.2f}%")
        
        # Check response time
        if metrics["avg_response_time_ms"] > self.alert_thresholds["avg_response_time_ms"]:
            issues.append(f"High average response time: {metrics['avg_response_time_ms']:.2f}ms")
        
        if metrics["p95_response_time_ms"] > self.alert_thresholds["p95_response_time_ms"]:
            warnings.append(f"High P95 response time: {metrics['p95_response_time_ms']:.2f}ms")
        
        # Check fallback rate
        if metrics["fallback_rate_percent"] > self.alert_thresholds["fallback_rate_percent"]:
            warnings.append(f"High fallback rate: {metrics['fallback_rate_percent']:.2f}%")
        
        # Check memory usage
        if metrics["max_memory_usage_mb"] > self.alert_thresholds["memory_usage_mb"]:
            warnings.append(f"High memory usage: {metrics['max_memory_usage_mb']:.1f}MB")
        
        # Check comparison accuracy
        if metrics["comparison_accuracy_percent"] < (100 - self.alert_thresholds["comparison_mismatch_rate_percent"]):
            issues.append(f"Low comparison accuracy: {metrics['comparison_accuracy_percent']:.2f}%")
        
        # Determine overall status
        if issues:
            status = "critical"
        elif warnings:
            status = "warning"
        else:
            status = "healthy"
        
        return {
            "status": status,
            "issues": issues,
            "warnings": warnings,
            "metrics": metrics
        }
    
    def _background_monitoring(self) -> None:
        """Background thread for continuous monitoring and alerting."""
        while self.monitoring_active:
            try:
                health_check = self.check_health()
                
                # Send alerts if needed
                if health_check["status"] in ["critical", "warning"] and self.alert_callback:
                    self.alert_callback(health_check)
                
                # Log health status periodically
                if self.metrics.total_requests > 0:
                    logger.info(f"Deployment health: {health_check['status']}, "
                              f"Requests: {health_check['metrics']['total_requests']}, "
                              f"Error rate: {health_check['metrics']['error_rate_percent']:.2f}%, "
                              f"Avg response: {health_check['metrics']['avg_response_time_ms']:.2f}ms")
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Error in background monitoring: {e}")
                time.sleep(60)
    
    def stop_monitoring(self) -> None:
        """Stop background monitoring."""
        self.monitoring_active = False
        if self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
```

## 4. Rollback and Recovery Procedures

### 4.1 Automated Rollback System

```python
# deployment/rollback/rollback_manager.py

"""
Automated rollback system for Universal LLM Discovery Engine deployment.
"""

import time
import logging
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class RollbackTrigger(Enum):
    """Types of rollback triggers."""
    HIGH_ERROR_RATE = "high_error_rate"
    HIGH_LATENCY = "high_latency"
    HIGH_MEMORY_USAGE = "high_memory_usage"
    LOW_ACCURACY = "low_accuracy"
    MANUAL = "manual"
    HEALTH_CHECK_FAILURE = "health_check_failure"

@dataclass
class RollbackEvent:
    """Record of a rollback event."""
    trigger: RollbackTrigger
    timestamp: float
    metrics_snapshot: Dict[str, Any]
    reason: str
    success: bool
    duration_seconds: float = 0.0

class RollbackManager:
    """Manage automated rollback procedures."""
    
    def __init__(self, feature_flag_manager, deployment_monitor):
        self.feature_flag_manager = feature_flag_manager
        self.deployment_monitor = deployment_monitor
        self.rollback_history: List[RollbackEvent] = []
        
        # Rollback thresholds
        self.rollback_thresholds = {
            "error_rate_percent": 2.0,
            "avg_response_time_ms": 30.0,
            "p95_response_time_ms": 60.0,
            "memory_usage_mb": 200,
            "comparison_accuracy_percent": 95.0
        }
        
        # Rollback configuration
        self.auto_rollback_enabled = True
        self.rollback_cooldown_minutes = 30
        self.max_rollbacks_per_hour = 3
        
        # State tracking
        self.last_rollback_time = 0
        self.rollbacks_in_last_hour = 0
    
    def check_rollback_conditions(self) -> Optional[RollbackTrigger]:
        """Check if rollback conditions are met."""
        if not self.auto_rollback_enabled:
            return None
        
        # Check cooldown period
        if time.time() - self.last_rollback_time < (self.rollback_cooldown_minutes * 60):
            return None
        
        # Check rollback frequency limit
        recent_rollbacks = [
            event for event in self.rollback_history
            if time.time() - event.timestamp < 3600  # Last hour
        ]
        
        if len(recent_rollbacks) >= self.max_rollbacks_per_hour:
            logger.warning("Rollback frequency limit reached, skipping automatic rollback")
            return None
        
        # Get current metrics
        health_check = self.deployment_monitor.check_health()
        
        if health_check["status"] == "no_data":
            return None
        
        metrics = health_check["metrics"]
        
        # Check error rate
        if metrics["error_rate_percent"] > self.rollback_thresholds["error_rate_percent"]:
            return RollbackTrigger.HIGH_ERROR_RATE
        
        # Check response time
        if metrics["avg_response_time_ms"] > self.rollback_thresholds["avg_response_time_ms"]:
            return RollbackTrigger.HIGH_LATENCY
        
        # Check memory usage
        if metrics["max_memory_usage_mb"] > self.rollback_thresholds["memory_usage_mb"]:
            return RollbackTrigger.HIGH_MEMORY_USAGE
        
        # Check comparison accuracy
        if metrics["comparison_accuracy_percent"] < self.rollback_thresholds["comparison_accuracy_percent"]:
            return RollbackTrigger.LOW_ACCURACY
        
        # Check overall health
        if health_check["status"] == "critical":
            return RollbackTrigger.HEALTH_CHECK_FAILURE
        
        return None
    
    def execute_rollback(self, trigger: RollbackTrigger, reason: str = "") -> RollbackEvent:
        """Execute rollback procedure."""
        start_time = time.time()
        
        logger.warning(f"Executing rollback due to {trigger.value}: {reason}")
        
        # Capture metrics snapshot
        metrics_snapshot = self.deployment_monitor.get_current_metrics()
        
        try:
            # Step 1: Disable universal engine
            self.feature_flag_manager.update_flag("universal_engine_enabled", False, 0)
            logger.info("Disabled universal engine")
            
            # Step 2: Ensure legacy fallback is enabled
            self.feature_flag_manager.update_flag("legacy_fallback_enabled", True, 100)
            logger.info("Enabled legacy fallback")
            
            # Step 3: Disable comparison mode to reduce overhead
            self.feature_flag_manager.update_flag("comparison_mode_enabled", False, 0)
            logger.info("Disabled comparison mode")
            
            # Step 4: Enable detailed logging for debugging
            self.feature_flag_manager.update_flag("detailed_logging_enabled", True, 100)
            logger.info("Enabled detailed logging")
            
            # Wait a moment for changes to propagate
            time.sleep(5)
            
            # Verify rollback success
            time.sleep(10)  # Allow time for metrics to update
            post_rollback_health = self.deployment_monitor.check_health()
            
            success = post_rollback_health["status"] != "critical"
            duration = time.time() - start_time
            
            rollback_event = RollbackEvent(
                trigger=trigger,
                timestamp=start_time,
                metrics_snapshot=metrics_snapshot,
                reason=reason,
                success=success,
                duration_seconds=duration
            )
            
            self.rollback_history.append(rollback_event)
            self.last_rollback_time = start_time
            
            if success:
                logger.info(f"Rollback completed successfully in {duration:.2f} seconds")
            else:
                logger.error(f"Rollback completed but system still unhealthy after {duration:.2f} seconds")
            
            return rollback_event
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Rollback failed after {duration:.2f} seconds: {e}")
            
            rollback_event = RollbackEvent(
                trigger=trigger,
                timestamp=start_time,
                metrics_snapshot=metrics_snapshot,
                reason=f"Rollback failed: {str(e)}",
                success=False,
                duration_seconds=duration
            )
            
            self.rollback_history.append(rollback_event)
            return rollback_event
    
    def manual_rollback(self, reason: str) -> RollbackEvent:
        """Execute manual rollback."""
        return self.execute_rollback(RollbackTrigger.MANUAL, reason)
    
    def get_rollback_status(self) -> Dict[str, Any]:
        """Get current rollback system status."""
        recent_rollbacks = [
            event for event in self.rollback_history
            if time.time() - event.timestamp < 3600
        ]
        
        return {
            "auto_rollback_enabled": self.auto_rollback_enabled,
            "total_rollbacks": len(self.rollback_history),
            "recent_rollbacks": len(recent_rollbacks),
            "last_rollback_time": self.last_rollback_time,
            "cooldown_remaining_minutes": max(0, (self.rollback_cooldown_minutes * 60 - (time.time() - self.last_rollback_time)) / 60),
            "rollback_thresholds": self.rollback_thresholds,
            "recent_rollback_events": [
                {
                    "trigger": event.trigger.value,
                    "timestamp": event.timestamp,
                    "reason": event.reason,
                    "success": event.success,
                    "duration_seconds": event.duration_seconds
                }
                for event in recent_rollbacks
            ]
        }
```

## 5. Production Deployment Checklist

### 5.1 Pre-Deployment Checklist

```markdown
# Universal LLM Discovery Engine - Production Deployment Checklist

## Phase 1: Infrastructure Setup

### Code Deployment
- [ ] Backup current production implementation
- [ ] Deploy new code with feature flags disabled
- [ ] Verify all dependencies are installed
- [ ] Confirm DSL configuration files are present
- [ ] Validate environment variables are set correctly

### Monitoring Setup
- [ ] Configure deployment monitoring dashboard
- [ ] Set up alerting webhooks and notifications
- [ ] Verify log aggregation is working
- [ ] Test performance monitoring collection
- [ ] Configure rollback automation

### Testing Validation
- [ ] Run full test suite in production environment
- [ ] Execute performance benchmarks
- [ ] Validate O(1) compliance tests pass
- [ ] Confirm integration tests succeed
- [ ] Verify backward compatibility tests pass

### Infrastructure Validation
- [ ] Confirm adequate memory allocation (>150MB per instance)
- [ ] Verify CPU resources are sufficient
- [ ] Test cache system connectivity and performance
- [ ] Validate network connectivity to all dependencies
- [ ] Confirm load balancer health checks work

## Phase 2: Shadow Mode Deployment

### Feature Flag Configuration
- [ ] Enable comparison mode (comparison_mode_enabled = true)
- [ ] Keep universal engine disabled (universal_engine_enabled = false)
- [ ] Ensure legacy fallback enabled (legacy_fallback_enabled = true)
- [ ] Enable performance monitoring (performance_monitoring_enabled = true)

### Monitoring Validation
- [ ] Verify both engines are processing requests
- [ ] Confirm comparison results are being collected
- [ ] Check performance metrics are within thresholds
- [ ] Validate memory usage remains stable
- [ ] Monitor error rates and alert thresholds

### Data Collection
- [ ] Collect 24 hours of comparison data
- [ ] Analyze accuracy rates (target >98%)
- [ ] Review performance differences
- [ ] Identify any systematic issues
- [ ] Document findings and optimizations needed

## Phase 3: Canary Deployment

### Gradual Traffic Increase
- [ ] Enable universal engine (universal_engine_enabled = true)
- [ ] Set initial traffic to 5% (traffic_percentage = 5)
- [ ] Monitor for 4 hours with stable metrics
- [ ] Increase to 10% if stable
- [ ] Increase to 25% if metrics remain good

### Performance Validation
- [ ] Error rate remains <0.5%
- [ ] Average response time <15ms
- [ ] P95 response time <30ms
- [ ] Memory usage <120MB per instance
- [ ] Cache hit rate >85%

### Issue Response
- [ ] Rollback procedures tested and ready
- [ ] On-call team notified and available
- [ ] Escalation procedures documented
- [ ] Communication plan for stakeholders ready

## Phase 4: Progressive Rollout

### Traffic Scaling
- [ ] Increase to 50% traffic
- [ ] Monitor for 12 hours
- [ ] Increase to 75% traffic
- [ ] Monitor for 24 hours
- [ ] Prepare for full rollout

### Stability Validation
- [ ] No critical issues in 48 hours
- [ ] Performance metrics stable
- [ ] Error rates within acceptable limits
- [ ] No memory leaks detected
- [ ] Customer impact assessment complete

## Phase 5: Full Deployment

### Complete Migration
- [ ] Route 100% traffic to universal engine
- [ ] Monitor for 72 hours
- [ ] Disable comparison mode (comparison_mode_enabled = false)
- [ ] Reduce logging verbosity for production
- [ ] Update documentation

### Legacy Cleanup
- [ ] Keep legacy fallback for 1 week
- [ ] Disable legacy fallback after validation
- [ ] Archive legacy code (do not delete immediately)
- [ ] Update monitoring dashboards
- [ ] Complete deployment documentation

### Post-Deployment
- [ ] Conduct deployment retrospective
- [ ] Update runbooks and procedures
- [ ] Train support team on new system
- [ ] Plan for future optimizations
- [ ] Schedule performance review in 30 days
```

This comprehensive deployment strategy ensures:

1. **Zero-Downtime Deployment**: Gradual rollout with immediate fallback capability
2. **Risk Mitigation**: Multiple validation checkpoints and automated rollback
3. **Comprehensive Monitoring**: Real-time performance and health tracking
4. **Production Readiness**: Thorough testing and validation at each phase
5. **Operational Excellence**: Clear procedures, monitoring, and recovery plans

The deployment approach minimizes risk while ensuring the Universal LLM Discovery Engine can be safely deployed to production with confidence.
