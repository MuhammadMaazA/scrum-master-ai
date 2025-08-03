"""
Analytics API endpoints for burndown charts, velocity tracking, and sprint metrics.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.analytics_service import analytics_service
from app.models.database import Sprint, Team

router = APIRouter()

@router.get("/burndown/{sprint_id}")
async def get_burndown_chart(
    sprint_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get burndown chart data for a specific sprint.
    
    Returns chart data formatted for frontend visualization.
    """
    try:
        # Verify sprint exists
        sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
        if not sprint:
            raise HTTPException(status_code=404, detail="Sprint not found")
        
        chart_data = await analytics_service.get_burndown_chart_data(sprint_id)
        
        if "error" in chart_data:
            raise HTTPException(status_code=500, detail=chart_data["error"])
        
        return {
            "success": True,
            "data": chart_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get burndown chart: {str(e)}")

@router.get("/velocity/{team_id}")
async def get_velocity_chart(
    team_id: int,
    num_sprints: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get velocity chart data for a specific team.
    
    Shows velocity trends over recent sprints.
    """
    try:
        # Verify team exists
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        chart_data = await analytics_service.get_velocity_chart_data(team_id)
        
        if "error" in chart_data:
            raise HTTPException(status_code=500, detail=chart_data["error"])
        
        return {
            "success": True,
            "data": chart_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get velocity chart: {str(e)}")

@router.get("/sprint-metrics/{sprint_id}")
async def get_sprint_metrics(
    sprint_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get comprehensive metrics for a specific sprint.
    
    Includes completion rates, velocity, timeline, and insights.
    """
    try:
        # Verify sprint exists
        sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
        if not sprint:
            raise HTTPException(status_code=404, detail="Sprint not found")
        
        metrics = await analytics_service.get_sprint_metrics(sprint_id)
        
        if not metrics:
            raise HTTPException(status_code=500, detail="Failed to calculate sprint metrics")
        
        return {
            "success": True,
            "data": {
                "sprint_id": metrics.sprint_id,
                "sprint_name": metrics.sprint_name,
                "team_name": metrics.team_name,
                "start_date": metrics.start_date.isoformat(),
                "end_date": metrics.end_date.isoformat(),
                "total_story_points": metrics.total_story_points,
                "completed_story_points": metrics.completed_story_points,
                "remaining_story_points": metrics.remaining_story_points,
                "velocity": round(metrics.velocity, 2),
                "completion_percentage": round(metrics.completion_percentage, 1),
                "days_remaining": metrics.days_remaining,
                "predicted_completion_date": metrics.predicted_completion_date.isoformat() if metrics.predicted_completion_date else None,
                "is_on_track": metrics.is_on_track,
                "burndown_points_count": len(metrics.burndown_data)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sprint metrics: {str(e)}")

@router.get("/sprint-report/{sprint_id}")
async def get_sprint_report(
    sprint_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get a comprehensive sprint report with insights and recommendations.
    
    Includes overview, metrics, velocity comparison, and AI-generated insights.
    """
    try:
        # Verify sprint exists
        sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
        if not sprint:
            raise HTTPException(status_code=404, detail="Sprint not found")
        
        report = await analytics_service.generate_sprint_report(sprint_id)
        
        if "error" in report:
            raise HTTPException(status_code=500, detail=report["error"])
        
        return {
            "success": True,
            "data": report
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate sprint report: {str(e)}")

@router.get("/team-velocity-history/{team_id}")
async def get_team_velocity_history(
    team_id: int,
    num_sprints: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed velocity history for a team.
    
    Returns raw velocity data for analysis and trend identification.
    """
    try:
        # Verify team exists
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        velocity_history = await analytics_service.get_team_velocity_history(team_id, num_sprints)
        
        formatted_history = []
        for v in velocity_history:
            formatted_history.append({
                "sprint_name": v.sprint_name,
                "planned_points": v.planned_points,
                "completed_points": v.completed_points,
                "spillover_points": v.spillover_points,
                "velocity": round(v.velocity, 2),
                "start_date": v.start_date.isoformat(),
                "end_date": v.end_date.isoformat()
            })
        
        return {
            "success": True,
            "data": {
                "team_id": team_id,
                "team_name": team.name,
                "velocity_history": formatted_history,
                "summary": {
                    "sprints_analyzed": len(formatted_history),
                    "average_velocity": round(sum(v.velocity for v in velocity_history) / len(velocity_history), 2) if velocity_history else 0,
                    "average_completion_rate": round(
                        sum(v.completed_points / v.planned_points * 100 for v in velocity_history if v.planned_points > 0) / len(velocity_history), 1
                    ) if velocity_history else 0
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get velocity history: {str(e)}")

@router.get("/dashboard-metrics/{team_id}")
async def get_dashboard_metrics(
    team_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get key metrics for the dashboard overview.
    
    Provides a summary of current sprint status and team performance.
    """
    try:
        # Verify team exists
        team = db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        
        # Get current active sprint
        current_sprint = db.query(Sprint).filter(
            Sprint.team_id == team_id,
            Sprint.status == "Active"
        ).first()
        
        dashboard_data = {
            "team_name": team.name,
            "current_sprint": None,
            "velocity_trend": None
        }
        
        if current_sprint:
            # Get current sprint metrics
            sprint_metrics = await analytics_service.get_sprint_metrics(current_sprint.id)
            
            if sprint_metrics:
                dashboard_data["current_sprint"] = {
                    "sprint_name": sprint_metrics.sprint_name,
                    "completion_percentage": round(sprint_metrics.completion_percentage, 1),
                    "days_remaining": sprint_metrics.days_remaining,
                    "total_points": sprint_metrics.total_story_points,
                    "completed_points": sprint_metrics.completed_story_points,
                    "is_on_track": sprint_metrics.is_on_track,
                    "velocity": round(sprint_metrics.velocity, 2)
                }
        
        # Get velocity trend
        velocity_history = await analytics_service.get_team_velocity_history(team_id, 3)
        if velocity_history:
            velocities = [v.velocity for v in velocity_history]
            avg_velocity = sum(velocities) / len(velocities)
            
            # Determine trend
            if len(velocities) >= 2:
                trend = "improving" if velocities[0] > velocities[-1] else "declining" if velocities[0] < velocities[-1] else "stable"
            else:
                trend = "stable"
            
            dashboard_data["velocity_trend"] = {
                "average_velocity": round(avg_velocity, 2),
                "trend": trend,
                "last_sprint_velocity": round(velocities[0], 2) if velocities else 0
            }
        
        return {
            "success": True,
            "data": dashboard_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard metrics: {str(e)}")

@router.get("/analytics-health")
async def analytics_health_check() -> Dict[str, Any]:
    """
    Health check for analytics service.
    
    Verifies that analytics calculations are working properly.
    """
    try:
        # Simple health check - could be expanded
        return {
            "status": "healthy",
            "service": "analytics",
            "features": [
                "burndown_charts",
                "velocity_tracking", 
                "sprint_metrics",
                "team_performance",
                "dashboard_summary"
            ],
            "timestamp": "2025-01-02T01:45:00Z"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }