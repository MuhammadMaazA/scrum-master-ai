"""
Monitoring and Analytics API endpoints.
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.monitoring_service import (
    metrics_collector, 
    performance_analyzer, 
    system_monitor
)
from app.api.api_v1.endpoints.security import get_current_active_user, UserInDB

router = APIRouter()

@router.get("/health")
async def get_system_health() -> Dict[str, Any]:
    """
    Get overall system health score and status.
    
    Returns a comprehensive health assessment including:
    - Overall health score (0-100)
    - System status (excellent/good/fair/poor)
    - Current performance metrics
    - Identified issues and recommendations
    """
    try:
        health_data = performance_analyzer.get_system_health_score()
        return {
            "success": True,
            "data": health_data
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get system health: {str(e)}"
        }

@router.get("/performance/api")
async def get_api_performance(
    hours_back: int = Query(default=24, ge=1, le=168),
    current_user: UserInDB = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get API performance analytics.
    
    Provides detailed analysis of API endpoint performance including:
    - Response times by endpoint
    - Error rates and status code distribution
    - Slowest requests identification
    - Request volume trends
    """
    try:
        analysis = performance_analyzer.analyze_api_performance(hours_back)
        
        # Format slowest requests for better readability
        if "slowest_requests" in analysis:
            for request in analysis["slowest_requests"]:
                request.response_time = round(request.response_time, 3)
        
        return {
            "success": True,
            "data": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze API performance: {str(e)}")

@router.get("/performance/user-behavior")
async def get_user_behavior_analytics(
    hours_back: int = Query(default=24, ge=1, le=168),
    current_user: UserInDB = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get user behavior analytics.
    
    Analyzes user interaction patterns including:
    - Feature usage statistics
    - Action success rates
    - Most active users
    - User engagement trends
    """
    try:
        analysis = performance_analyzer.analyze_user_behavior(hours_back)
        return {
            "success": True,
            "data": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze user behavior: {str(e)}")

@router.get("/performance/ai-operations")
async def get_ai_performance_analytics(
    hours_back: int = Query(default=24, ge=1, le=168),
    current_user: UserInDB = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get AI operations performance analytics.
    
    Provides insights into AI system performance including:
    - Operation success rates
    - Response times by operation type
    - Token usage and estimated costs
    - Error patterns and model performance
    """
    try:
        analysis = performance_analyzer.analyze_ai_performance(hours_back)
        return {
            "success": True,
            "data": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze AI performance: {str(e)}")

@router.get("/metrics/system")
async def get_system_metrics(
    current_user: UserInDB = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get current system resource metrics.
    
    Returns real-time system performance data including:
    - CPU usage
    - Memory usage 
    - Disk usage
    - Network I/O
    - Process count
    """
    try:
        # Collect fresh system metrics
        await system_monitor.collect_system_metrics()
        
        # Get recent performance metrics
        from datetime import datetime, timedelta
        recent_metrics = [
            m for m in metrics_collector.performance_metrics 
            if m.timestamp > datetime.now() - timedelta(minutes=5)
        ]
        
        # Format metrics by type
        current_metrics = {}
        for metric in recent_metrics:
            current_metrics[metric.metric_name] = {
                "value": metric.metric_value,
                "unit": metric.metric_unit,
                "timestamp": metric.timestamp.isoformat()
            }
        
        return {
            "success": True,
            "data": {
                "current_metrics": current_metrics,
                "collection_time": datetime.now().isoformat(),
                "metrics_count": len(recent_metrics)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system metrics: {str(e)}")

@router.post("/metrics/record-user-action")
async def record_user_action(
    action_data: Dict[str, Any],
    current_user: UserInDB = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Record a user action for analytics.
    
    Expected action_data format:
    {
        "action": "sprint_created",
        "feature": "sprint_planning",
        "success": true,
        "metadata": {"sprint_id": 123, "items_count": 15}
    }
    """
    try:
        # Validate required fields
        required_fields = ["action", "feature", "success"]
        for field in required_fields:
            if field not in action_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Record the user action
        metrics_collector.record_user_behavior(
            user_id=current_user.username,
            action=action_data["action"],
            feature=action_data["feature"],
            success=action_data["success"],
            metadata=action_data.get("metadata", {})
        )
        
        return {
            "success": True,
            "message": "User action recorded successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record user action: {str(e)}")

@router.get("/dashboard")
async def get_monitoring_dashboard(
    current_user: UserInDB = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get comprehensive monitoring dashboard data.
    
    Combines multiple analytics into a single dashboard view:
    - System health summary
    - Recent performance trends
    - User activity overview
    - AI operations summary
    """
    try:
        # Get health score
        health_data = performance_analyzer.get_system_health_score()
        
        # Get recent analytics (last 6 hours for dashboard)
        api_perf = performance_analyzer.analyze_api_performance(6)
        user_behavior = performance_analyzer.analyze_user_behavior(6)
        ai_perf = performance_analyzer.analyze_ai_performance(6)
        
        # Get current system metrics
        await system_monitor.collect_system_metrics()
        from datetime import datetime, timedelta
        recent_system_metrics = [
            m for m in metrics_collector.performance_metrics 
            if m.timestamp > datetime.now() - timedelta(minutes=5)
        ]
        
        current_system = {}
        for metric in recent_system_metrics:
            current_system[metric.metric_name] = metric.metric_value
        
        dashboard_data = {
            "system_health": {
                "score": health_data.get("health_score", 0),
                "status": health_data.get("status", "unknown"),
                "issues_count": len(health_data.get("issues", []))
            },
            "api_performance": {
                "total_requests": api_perf.get("total_requests", 0),
                "average_response_time": round(api_perf.get("average_response_time", 0), 3),
                "error_rate": round(api_perf.get("error_rate", 0), 2)
            },
            "user_activity": {
                "total_actions": user_behavior.get("total_actions", 0),
                "unique_users": user_behavior.get("unique_users", 0),
                "top_feature": max(user_behavior.get("most_used_features", {"unknown": 0}).items(), 
                                 key=lambda x: x[1], default=("unknown", 0))[0]
            },
            "ai_operations": {
                "total_operations": ai_perf.get("total_operations", 0),
                "success_rate": round(ai_perf.get("success_rate", 0), 2),
                "tokens_used": ai_perf.get("total_tokens_used", 0),
                "estimated_cost": ai_perf.get("estimated_ai_cost_usd", 0)
            },
            "system_resources": {
                "cpu_usage": current_system.get("cpu_usage", 0),
                "memory_usage": current_system.get("memory_usage", 0),
                "disk_usage": current_system.get("disk_usage", 0)
            },
            "last_updated": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "data": dashboard_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")

@router.get("/alerts")
async def get_system_alerts(
    current_user: UserInDB = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get current system alerts and warnings.
    
    Returns actionable alerts based on system performance,
    error rates, and other monitored metrics.
    """
    try:
        health_data = performance_analyzer.get_system_health_score()
        api_perf = performance_analyzer.analyze_api_performance(1)  # Last hour
        
        alerts = []
        
        # Health-based alerts
        if health_data.get("health_score", 100) < 70:
            alerts.append({
                "type": "warning",
                "category": "system_health",
                "message": f"System health score is {health_data.get('health_score', 0)}/100",
                "details": health_data.get("issues", []),
                "severity": "medium" if health_data.get("health_score", 0) > 50 else "high"
            })
        
        # API performance alerts
        if api_perf.get("error_rate", 0) > 10:
            alerts.append({
                "type": "error",
                "category": "api_performance", 
                "message": f"High API error rate: {api_perf.get('error_rate', 0):.1f}%",
                "severity": "high"
            })
        
        if api_perf.get("average_response_time", 0) > 3.0:
            alerts.append({
                "type": "warning",
                "category": "api_performance",
                "message": f"Slow API responses: {api_perf.get('average_response_time', 0):.2f}s average",
                "severity": "medium"
            })
        
        # AI operations alerts
        ai_perf = performance_analyzer.analyze_ai_performance(1)
        if ai_perf.get("success_rate", 100) < 90:
            alerts.append({
                "type": "warning",
                "category": "ai_operations",
                "message": f"AI operation success rate: {ai_perf.get('success_rate', 0):.1f}%",
                "severity": "medium"
            })
        
        # Resource usage alerts
        from datetime import datetime, timedelta
        recent_metrics = [
            m for m in metrics_collector.performance_metrics 
            if m.timestamp > datetime.now() - timedelta(minutes=5)
        ]
        
        for metric in recent_metrics:
            if metric.metric_name == "memory_usage" and metric.metric_value > 85:
                alerts.append({
                    "type": "warning",
                    "category": "resource_usage",
                    "message": f"High memory usage: {metric.metric_value:.1f}%",
                    "severity": "high"
                })
            elif metric.metric_name == "cpu_usage" and metric.metric_value > 80:
                alerts.append({
                    "type": "warning", 
                    "category": "resource_usage",
                    "message": f"High CPU usage: {metric.metric_value:.1f}%",
                    "severity": "medium"
                })
        
        # Sort alerts by severity
        severity_order = {"high": 0, "medium": 1, "low": 2}
        alerts.sort(key=lambda x: severity_order.get(x.get("severity", "low"), 2))
        
        return {
            "success": True,
            "data": {
                "alerts": alerts,
                "total_alerts": len(alerts),
                "high_severity_count": len([a for a in alerts if a.get("severity") == "high"]),
                "generated_at": datetime.now().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")

@router.post("/start-monitoring")
async def start_system_monitoring(
    current_user: UserInDB = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Start continuous system monitoring.
    
    Admin endpoint to start background system monitoring.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        if not system_monitor.monitoring_active:
            # Start monitoring in background (in production, use proper task queue)
            import asyncio
            asyncio.create_task(system_monitor.start_monitoring(60))  # 60 second intervals
            
            return {
                "success": True,
                "message": "System monitoring started",
                "interval_seconds": 60
            }
        else:
            return {
                "success": True,
                "message": "System monitoring already active"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring: {str(e)}")

@router.post("/stop-monitoring")
async def stop_system_monitoring(
    current_user: UserInDB = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Stop continuous system monitoring.
    
    Admin endpoint to stop background system monitoring.
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        system_monitor.stop_monitoring()
        return {
            "success": True,
            "message": "System monitoring stopped"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop monitoring: {str(e)}")

@router.get("/stats")
async def get_monitoring_stats() -> Dict[str, Any]:
    """
    Get monitoring system statistics.
    
    Returns information about the monitoring system itself.
    """
    try:
        return {
            "success": True,
            "data": {
                "monitoring_active": system_monitor.monitoring_active,
                "metrics_collected": {
                    "performance_metrics": len(metrics_collector.performance_metrics),
                    "api_metrics": len(metrics_collector.api_metrics),
                    "user_metrics": len(metrics_collector.user_metrics),
                    "ai_metrics": len(metrics_collector.ai_metrics)
                },
                "monitoring_features": [
                    "system_resource_monitoring",
                    "api_performance_tracking",
                    "user_behavior_analytics",
                    "ai_operation_monitoring",
                    "real_time_health_scoring",
                    "automated_alerting"
                ]
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get monitoring stats: {str(e)}"
        }