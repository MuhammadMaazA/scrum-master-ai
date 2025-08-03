"""
Monitoring and Performance Analytics Service.

This service tracks system performance, user behavior, and provides
insights for continuous improvement of the AI Scrum Master system.
"""
import time
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass, asdict
import psutil
import asyncio
from functools import wraps

from app.core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Performance metric data structure."""
    timestamp: datetime
    metric_name: str
    metric_value: float
    metric_unit: str
    context: Dict[str, Any] = None

@dataclass
class APICallMetric:
    """API call performance metric."""
    endpoint: str
    method: str
    status_code: int
    response_time: float
    timestamp: datetime
    user_agent: str = None
    ip_address: str = None

@dataclass
class UserBehaviorMetric:
    """User behavior tracking metric."""
    user_id: str
    action: str
    feature: str
    timestamp: datetime
    success: bool
    metadata: Dict[str, Any] = None

@dataclass
class AIOperationMetric:
    """AI operation performance metric."""
    operation_type: str
    model_used: str
    tokens_used: int
    response_time: float
    timestamp: datetime
    success: bool
    error_type: str = None

class MetricsCollector:
    """Collects and stores various performance metrics."""
    
    def __init__(self):
        self.performance_metrics: List[PerformanceMetric] = []
        self.api_metrics: List[APICallMetric] = []
        self.user_metrics: List[UserBehaviorMetric] = []
        self.ai_metrics: List[AIOperationMetric] = []
        self.max_metrics_per_type = 10000  # Prevent memory issues
    
    def record_performance_metric(self, name: str, value: float, unit: str, context: Dict[str, Any] = None):
        """Record a performance metric."""
        metric = PerformanceMetric(
            timestamp=datetime.now(),
            metric_name=name,
            metric_value=value,
            metric_unit=unit,
            context=context or {}
        )
        
        self.performance_metrics.append(metric)
        self._cleanup_old_metrics('performance')
        
        logger.info(f"METRIC: {name}={value}{unit}")
    
    def record_api_call(self, endpoint: str, method: str, status_code: int, 
                       response_time: float, user_agent: str = None, ip_address: str = None):
        """Record API call metrics."""
        metric = APICallMetric(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            response_time=response_time,
            timestamp=datetime.now(),
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        self.api_metrics.append(metric)
        self._cleanup_old_metrics('api')
        
        if response_time > 5.0:  # Log slow requests
            logger.warning(f"SLOW_REQUEST: {method} {endpoint} took {response_time:.2f}s")
    
    def record_user_behavior(self, user_id: str, action: str, feature: str, 
                           success: bool, metadata: Dict[str, Any] = None):
        """Record user behavior metrics."""
        metric = UserBehaviorMetric(
            user_id=user_id,
            action=action,
            feature=feature,
            timestamp=datetime.now(),
            success=success,
            metadata=metadata or {}
        )
        
        self.user_metrics.append(metric)
        self._cleanup_old_metrics('user')
        
        logger.info(f"USER_ACTION: User={user_id}, Action={action}, Feature={feature}, Success={success}")
    
    def record_ai_operation(self, operation_type: str, model_used: str, tokens_used: int,
                          response_time: float, success: bool, error_type: str = None):
        """Record AI operation metrics."""
        metric = AIOperationMetric(
            operation_type=operation_type,
            model_used=model_used,
            tokens_used=tokens_used,
            response_time=response_time,
            timestamp=datetime.now(),
            success=success,
            error_type=error_type
        )
        
        self.ai_metrics.append(metric)
        self._cleanup_old_metrics('ai')
        
        if not success:
            logger.error(f"AI_OPERATION_FAILED: {operation_type} failed with {error_type}")
    
    def _cleanup_old_metrics(self, metric_type: str):
        """Clean up old metrics to prevent memory issues."""
        if metric_type == 'performance' and len(self.performance_metrics) > self.max_metrics_per_type:
            self.performance_metrics = self.performance_metrics[-self.max_metrics_per_type:]
        elif metric_type == 'api' and len(self.api_metrics) > self.max_metrics_per_type:
            self.api_metrics = self.api_metrics[-self.max_metrics_per_type:]
        elif metric_type == 'user' and len(self.user_metrics) > self.max_metrics_per_type:
            self.user_metrics = self.user_metrics[-self.max_metrics_per_type:]
        elif metric_type == 'ai' and len(self.ai_metrics) > self.max_metrics_per_type:
            self.ai_metrics = self.ai_metrics[-self.max_metrics_per_type:]

class SystemMonitor:
    """Monitors system health and performance."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.monitoring_active = False
    
    async def start_monitoring(self, interval_seconds: int = 60):
        """Start continuous system monitoring."""
        self.monitoring_active = True
        
        while self.monitoring_active:
            try:
                await self.collect_system_metrics()
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"Error in system monitoring: {e}")
                await asyncio.sleep(interval_seconds)
    
    def stop_monitoring(self):
        """Stop system monitoring."""
        self.monitoring_active = False
    
    async def collect_system_metrics(self):
        """Collect system performance metrics."""
        try:
            # CPU Usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics.record_performance_metric("cpu_usage", cpu_percent, "percent")
            
            # Memory Usage
            memory = psutil.virtual_memory()
            self.metrics.record_performance_metric("memory_usage", memory.percent, "percent")
            self.metrics.record_performance_metric("memory_available", memory.available / (1024**3), "GB")
            
            # Disk Usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.metrics.record_performance_metric("disk_usage", disk_percent, "percent")
            
            # Network I/O
            network = psutil.net_io_counters()
            self.metrics.record_performance_metric("network_bytes_sent", network.bytes_sent, "bytes")
            self.metrics.record_performance_metric("network_bytes_recv", network.bytes_recv, "bytes")
            
            # Process Count
            process_count = len(psutil.pids())
            self.metrics.record_performance_metric("process_count", process_count, "count")
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")

class PerformanceAnalyzer:
    """Analyzes performance metrics and provides insights."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
    
    def analyze_api_performance(self, hours_back: int = 24) -> Dict[str, Any]:
        """Analyze API performance over specified time period."""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        recent_metrics = [m for m in self.metrics.api_metrics if m.timestamp > cutoff_time]
        
        if not recent_metrics:
            return {"error": "No API metrics found for the specified period"}
        
        # Group by endpoint
        endpoint_stats = defaultdict(list)
        for metric in recent_metrics:
            endpoint_stats[f"{metric.method} {metric.endpoint}"].append(metric)
        
        analysis = {
            "total_requests": len(recent_metrics),
            "time_period_hours": hours_back,
            "average_response_time": sum(m.response_time for m in recent_metrics) / len(recent_metrics),
            "slowest_requests": sorted(recent_metrics, key=lambda m: m.response_time, reverse=True)[:5],
            "endpoint_performance": {},
            "status_code_distribution": defaultdict(int),
            "error_rate": 0
        }
        
        # Analyze each endpoint
        for endpoint, metrics in endpoint_stats.items():
            avg_response_time = sum(m.response_time for m in metrics) / len(metrics)
            error_count = sum(1 for m in metrics if m.status_code >= 400)
            
            analysis["endpoint_performance"][endpoint] = {
                "request_count": len(metrics),
                "average_response_time": avg_response_time,
                "error_count": error_count,
                "error_rate": (error_count / len(metrics)) * 100 if metrics else 0
            }
        
        # Status code distribution
        for metric in recent_metrics:
            analysis["status_code_distribution"][metric.status_code] += 1
        
        # Overall error rate
        error_count = sum(1 for m in recent_metrics if m.status_code >= 400)
        analysis["error_rate"] = (error_count / len(recent_metrics)) * 100
        
        return analysis
    
    def analyze_user_behavior(self, hours_back: int = 24) -> Dict[str, Any]:
        """Analyze user behavior patterns."""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        recent_metrics = [m for m in self.metrics.user_metrics if m.timestamp > cutoff_time]
        
        if not recent_metrics:
            return {"error": "No user behavior metrics found"}
        
        # Group by feature and action
        feature_usage = defaultdict(int)
        action_success_rate = defaultdict(lambda: {"total": 0, "success": 0})
        user_activity = defaultdict(int)
        
        for metric in recent_metrics:
            feature_usage[metric.feature] += 1
            action_success_rate[metric.action]["total"] += 1
            if metric.success:
                action_success_rate[metric.action]["success"] += 1
            user_activity[metric.user_id] += 1
        
        # Calculate success rates
        success_rates = {}
        for action, stats in action_success_rate.items():
            success_rates[action] = (stats["success"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        
        return {
            "total_actions": len(recent_metrics),
            "unique_users": len(user_activity),
            "most_used_features": dict(sorted(feature_usage.items(), key=lambda x: x[1], reverse=True)[:10]),
            "action_success_rates": success_rates,
            "most_active_users": dict(sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:5])
        }
    
    def analyze_ai_performance(self, hours_back: int = 24) -> Dict[str, Any]:
        """Analyze AI operation performance."""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        recent_metrics = [m for m in self.metrics.ai_metrics if m.timestamp > cutoff_time]
        
        if not recent_metrics:
            return {"error": "No AI metrics found"}
        
        successful_operations = [m for m in recent_metrics if m.success]
        failed_operations = [m for m in recent_metrics if not m.success]
        
        analysis = {
            "total_operations": len(recent_metrics),
            "success_rate": (len(successful_operations) / len(recent_metrics)) * 100,
            "average_response_time": sum(m.response_time for m in recent_metrics) / len(recent_metrics),
            "total_tokens_used": sum(m.tokens_used for m in recent_metrics),
            "operations_by_type": defaultdict(int),
            "models_used": defaultdict(int),
            "common_errors": defaultdict(int)
        }
        
        for metric in recent_metrics:
            analysis["operations_by_type"][metric.operation_type] += 1
            analysis["models_used"][metric.model_used] += 1
            if metric.error_type:
                analysis["common_errors"][metric.error_type] += 1
        
        # Estimated costs (approximate)
        gpt4_cost_per_1k_tokens = 0.03  # Rough estimate
        estimated_cost = (analysis["total_tokens_used"] / 1000) * gpt4_cost_per_1k_tokens
        analysis["estimated_ai_cost_usd"] = round(estimated_cost, 2)
        
        return analysis
    
    def get_system_health_score(self) -> Dict[str, Any]:
        """Calculate overall system health score."""
        recent_performance = [m for m in self.metrics.performance_metrics 
                            if m.timestamp > datetime.now() - timedelta(minutes=30)]
        
        if not recent_performance:
            return {"health_score": 0, "status": "no_data", "details": "No recent performance data"}
        
        # Get latest metrics for each type
        latest_metrics = {}
        for metric in recent_performance:
            latest_metrics[metric.metric_name] = metric.metric_value
        
        # Calculate health score (0-100)
        health_score = 100
        issues = []
        
        # CPU health (deduct points for high usage)
        cpu_usage = latest_metrics.get("cpu_usage", 0)
        if cpu_usage > 80:
            health_score -= 20
            issues.append(f"High CPU usage: {cpu_usage:.1f}%")
        elif cpu_usage > 60:
            health_score -= 10
            issues.append(f"Moderate CPU usage: {cpu_usage:.1f}%")
        
        # Memory health
        memory_usage = latest_metrics.get("memory_usage", 0)
        if memory_usage > 85:
            health_score -= 25
            issues.append(f"High memory usage: {memory_usage:.1f}%")
        elif memory_usage > 70:
            health_score -= 15
            issues.append(f"Moderate memory usage: {memory_usage:.1f}%")
        
        # Disk health
        disk_usage = latest_metrics.get("disk_usage", 0)
        if disk_usage > 90:
            health_score -= 20
            issues.append(f"High disk usage: {disk_usage:.1f}%")
        elif disk_usage > 80:
            health_score -= 10
            issues.append(f"Moderate disk usage: {disk_usage:.1f}%")
        
        # API performance health
        recent_api_metrics = [m for m in self.metrics.api_metrics 
                            if m.timestamp > datetime.now() - timedelta(minutes=15)]
        
        if recent_api_metrics:
            avg_response_time = sum(m.response_time for m in recent_api_metrics) / len(recent_api_metrics)
            error_rate = (sum(1 for m in recent_api_metrics if m.status_code >= 400) / len(recent_api_metrics)) * 100
            
            if avg_response_time > 5.0:
                health_score -= 15
                issues.append(f"Slow API responses: {avg_response_time:.2f}s average")
            
            if error_rate > 10:
                health_score -= 20
                issues.append(f"High API error rate: {error_rate:.1f}%")
        
        # Determine status
        if health_score >= 90:
            status = "excellent"
        elif health_score >= 70:
            status = "good"
        elif health_score >= 50:
            status = "fair"
        else:
            status = "poor"
        
        return {
            "health_score": max(0, health_score),
            "status": status,
            "issues": issues,
            "last_updated": datetime.now().isoformat(),
            "metrics_summary": latest_metrics
        }

# Performance monitoring decorator
def monitor_performance(operation_type: str = None, track_tokens: bool = False):
    """Decorator to monitor function performance."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            operation_name = operation_type or f"{func.__module__}.{func.__name__}"
            
            try:
                result = await func(*args, **kwargs)
                
                # Record successful operation
                response_time = time.time() - start_time
                metrics_collector.record_performance_metric(
                    f"operation_{operation_name}",
                    response_time,
                    "seconds"
                )
                
                # If this is an AI operation, record AI metrics
                if hasattr(result, 'usage') or track_tokens:
                    tokens_used = getattr(result, 'usage', {}).get('total_tokens', 0)
                    metrics_collector.record_ai_operation(
                        operation_name,
                        "gpt-4",  # Default model
                        tokens_used,
                        response_time,
                        True
                    )
                
                return result
                
            except Exception as e:
                response_time = time.time() - start_time
                
                # Record failed operation
                metrics_collector.record_performance_metric(
                    f"operation_{operation_name}_failed",
                    response_time,
                    "seconds"
                )
                
                if track_tokens:
                    metrics_collector.record_ai_operation(
                        operation_name,
                        "gpt-4",
                        0,
                        response_time,
                        False,
                        str(type(e).__name__)
                    )
                
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            operation_name = operation_type or f"{func.__module__}.{func.__name__}"
            
            try:
                result = func(*args, **kwargs)
                response_time = time.time() - start_time
                
                metrics_collector.record_performance_metric(
                    f"operation_{operation_name}",
                    response_time,
                    "seconds"
                )
                
                return result
                
            except Exception as e:
                response_time = time.time() - start_time
                metrics_collector.record_performance_metric(
                    f"operation_{operation_name}_failed",
                    response_time,
                    "seconds"
                )
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator

# Global instances
metrics_collector = MetricsCollector()
system_monitor = SystemMonitor(metrics_collector)
performance_analyzer = PerformanceAnalyzer(metrics_collector)