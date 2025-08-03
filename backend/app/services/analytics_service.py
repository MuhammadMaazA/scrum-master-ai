"""
Analytics Service for Sprint Metrics and Burndown Charts.

This service handles velocity tracking, burndown chart generation,
and sprint analytics for the AI Scrum Master.
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, date
from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.database import get_db
from app.models.sprint import Sprint
from app.models.backlog_item import BacklogItem
from app.models.standup import StandupUpdate
from app.models.team import Team
from app.models.project import Project
from app.services.jira_service import jira_service

logger = logging.getLogger(__name__)

@dataclass
class BurndownPoint:
    """Data point for burndown chart."""
    date: date
    remaining_points: int
    ideal_remaining: int
    completed_points: int

@dataclass
class VelocityData:
    """Velocity tracking data."""
    sprint_name: str
    planned_points: int
    completed_points: int
    spillover_points: int
    velocity: float
    start_date: date
    end_date: date

@dataclass
class SprintMetrics:
    """Complete sprint metrics."""
    sprint_id: int
    sprint_name: str
    team_name: str
    start_date: date
    end_date: date
    total_story_points: int
    completed_story_points: int
    remaining_story_points: int
    velocity: float
    burndown_data: List[BurndownPoint]
    completion_percentage: float
    days_remaining: int
    predicted_completion_date: Optional[date]
    is_on_track: bool

class AnalyticsService:
    """Service for generating sprint analytics and burndown charts."""
    
    def __init__(self):
        self.db = next(get_db())
    
    async def get_sprint_metrics(self, sprint_id: int) -> Optional[SprintMetrics]:
        """Get comprehensive metrics for a sprint."""
        try:
            # Get sprint data
            sprint = self.db.query(Sprint).filter(Sprint.id == sprint_id).first()
            if not sprint:
                logger.error(f"Sprint {sprint_id} not found")
                return None
            
            # Get team data
            team = self.db.query(Team).filter(Team.id == sprint.team_id).first()
            team_name = team.name if team else "Unknown Team"
            
            # Get backlog items in this sprint
            backlog_items = self.db.query(BacklogItem).filter(
                BacklogItem.sprint_id == sprint_id
            ).all()
            
            # Calculate story points
            total_points = sum(item.effort_estimate_numeric or 0 for item in backlog_items)
            completed_points = sum(
                item.effort_estimate_numeric or 0 
                for item in backlog_items 
                if item.status in ['Done', 'Completed', 'Closed']
            )
            remaining_points = total_points - completed_points
            
            # Calculate velocity (completed points over sprint duration)
            sprint_days = (sprint.end_date - sprint.start_date).days + 1
            velocity = completed_points / sprint_days if sprint_days > 0 else 0
            
            # Generate burndown data
            burndown_data = await self._generate_burndown_data(sprint, backlog_items)
            
            # Calculate completion percentage
            completion_pct = (completed_points / total_points * 100) if total_points > 0 else 0
            
            # Calculate days remaining
            today = date.today()
            days_remaining = max(0, (sprint.end_date - today).days)
            
            # Predict completion date based on current velocity
            predicted_completion = await self._predict_completion_date(
                remaining_points, velocity, today
            )
            
            # Determine if sprint is on track
            is_on_track = await self._is_sprint_on_track(
                sprint, completion_pct, days_remaining
            )
            
            return SprintMetrics(
                sprint_id=sprint.id,
                sprint_name=sprint.name,
                team_name=team_name,
                start_date=sprint.start_date,
                end_date=sprint.end_date,
                total_story_points=total_points,
                completed_story_points=completed_points,
                remaining_story_points=remaining_points,
                velocity=velocity,
                burndown_data=burndown_data,
                completion_percentage=completion_pct,
                days_remaining=days_remaining,
                predicted_completion_date=predicted_completion,
                is_on_track=is_on_track
            )
            
        except Exception as e:
            logger.error(f"Failed to get sprint metrics: {e}")
            return None
    
    async def _generate_burndown_data(self, sprint: Sprint, backlog_items: List[BacklogItem]) -> List[BurndownPoint]:
        """Generate burndown chart data points."""
        burndown_points = []
        
        try:
            total_points = sum(item.effort_estimate_numeric or 0 for item in backlog_items)
            sprint_days = (sprint.end_date - sprint.start_date).days + 1
            
            current_date = sprint.start_date
            while current_date <= min(sprint.end_date, date.today()):
                # Calculate ideal remaining (linear burndown)
                days_elapsed = (current_date - sprint.start_date).days
                ideal_remaining = max(0, total_points - (total_points * days_elapsed / sprint_days))
                
                # Calculate actual completed points by this date
                # Note: In a real implementation, you'd track daily completion
                # For now, we'll estimate based on current completion
                if current_date == date.today():
                    completed_by_date = sum(
                        item.effort_estimate_numeric or 0 
                        for item in backlog_items 
                        if item.status in ['Done', 'Completed', 'Closed']
                    )
                else:
                    # Estimate historical completion (linear approximation)
                    total_completed = sum(
                        item.effort_estimate_numeric or 0 
                        for item in backlog_items 
                        if item.status in ['Done', 'Completed', 'Closed']
                    )
                    completion_ratio = min(1.0, days_elapsed / (date.today() - sprint.start_date).days) if (date.today() - sprint.start_date).days > 0 else 0
                    completed_by_date = int(total_completed * completion_ratio)
                
                remaining_points = total_points - completed_by_date
                
                burndown_points.append(BurndownPoint(
                    date=current_date,
                    remaining_points=remaining_points,
                    ideal_remaining=int(ideal_remaining),
                    completed_points=completed_by_date
                ))
                
                current_date += timedelta(days=1)
            
            return burndown_points
            
        except Exception as e:
            logger.error(f"Failed to generate burndown data: {e}")
            return []
    
    async def _predict_completion_date(self, remaining_points: int, current_velocity: float, today: date) -> Optional[date]:
        """Predict sprint completion date based on current velocity."""
        if current_velocity <= 0 or remaining_points <= 0:
            return None
        
        days_needed = remaining_points / current_velocity
        predicted_date = today + timedelta(days=int(days_needed))
        
        return predicted_date
    
    async def _is_sprint_on_track(self, sprint: Sprint, completion_pct: float, days_remaining: int) -> bool:
        """Determine if sprint is on track based on completion vs time remaining."""
        total_days = (sprint.end_date - sprint.start_date).days + 1
        days_elapsed = total_days - days_remaining
        expected_completion = (days_elapsed / total_days) * 100 if total_days > 0 else 0
        
        # Sprint is on track if actual completion is within 10% of expected
        return abs(completion_pct - expected_completion) <= 10
    
    async def get_team_velocity_history(self, team_id: int, num_sprints: int = 5) -> List[VelocityData]:
        """Get velocity history for a team."""
        try:
            # Get recent sprints for the team
            sprints = self.db.query(Sprint).filter(
                Sprint.team_id == team_id,
                Sprint.status.in_(['Completed', 'Closed'])
            ).order_by(Sprint.end_date.desc()).limit(num_sprints).all()
            
            velocity_data = []
            
            for sprint in sprints:
                # Get backlog items for this sprint
                backlog_items = self.db.query(BacklogItem).filter(
                    BacklogItem.sprint_id == sprint.id
                ).all()
                
                planned_points = sum(item.effort_estimate_numeric or 0 for item in backlog_items)
                completed_items = [item for item in backlog_items if item.status in ['Done', 'Completed', 'Closed']]
                completed_points = sum(item.effort_estimate_numeric or 0 for item in completed_items)
                spillover_points = planned_points - completed_points
                
                sprint_days = (sprint.end_date - sprint.start_date).days + 1
                velocity = completed_points / sprint_days if sprint_days > 0 else 0
                
                velocity_data.append(VelocityData(
                    sprint_name=sprint.name,
                    planned_points=planned_points,
                    completed_points=completed_points,
                    spillover_points=spillover_points,
                    velocity=velocity,
                    start_date=sprint.start_date,
                    end_date=sprint.end_date
                ))
            
            return velocity_data
            
        except Exception as e:
            logger.error(f"Failed to get velocity history: {e}")
            return []
    
    async def get_burndown_chart_data(self, sprint_id: int) -> Dict[str, Any]:
        """Get burndown chart data formatted for frontend visualization."""
        try:
            metrics = await self.get_sprint_metrics(sprint_id)
            if not metrics:
                return {"error": "Sprint not found"}
            
            # Format data for Chart.js or similar
            dates = [point.date.isoformat() for point in metrics.burndown_data]
            remaining_points = [point.remaining_points for point in metrics.burndown_data]
            ideal_points = [point.ideal_remaining for point in metrics.burndown_data]
            
            return {
                "sprint_name": metrics.sprint_name,
                "labels": dates,
                "datasets": [
                    {
                        "label": "Remaining Work",
                        "data": remaining_points,
                        "borderColor": "rgb(255, 99, 132)",
                        "backgroundColor": "rgba(255, 99, 132, 0.2)",
                        "tension": 0.1
                    },
                    {
                        "label": "Ideal Burndown",
                        "data": ideal_points,
                        "borderColor": "rgb(54, 162, 235)",
                        "backgroundColor": "rgba(54, 162, 235, 0.2)",
                        "borderDash": [5, 5],
                        "tension": 0.1
                    }
                ],
                "metrics": {
                    "total_points": metrics.total_story_points,
                    "completed_points": metrics.completed_story_points,
                    "completion_percentage": metrics.completion_percentage,
                    "days_remaining": metrics.days_remaining,
                    "is_on_track": metrics.is_on_track,
                    "predicted_completion": metrics.predicted_completion_date.isoformat() if metrics.predicted_completion_date else None
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get burndown chart data: {e}")
            return {"error": str(e)}
    
    async def get_velocity_chart_data(self, team_id: int) -> Dict[str, Any]:
        """Get velocity chart data formatted for frontend visualization."""
        try:
            velocity_history = await self.get_team_velocity_history(team_id)
            
            sprint_names = [v.sprint_name for v in velocity_history]
            planned_points = [v.planned_points for v in velocity_history]
            completed_points = [v.completed_points for v in velocity_history]
            velocities = [v.velocity for v in velocity_history]
            
            # Calculate average velocity
            avg_velocity = sum(velocities) / len(velocities) if velocities else 0
            
            return {
                "labels": sprint_names,
                "datasets": [
                    {
                        "label": "Planned Points",
                        "data": planned_points,
                        "backgroundColor": "rgba(54, 162, 235, 0.5)",
                        "borderColor": "rgb(54, 162, 235)"
                    },
                    {
                        "label": "Completed Points",
                        "data": completed_points,
                        "backgroundColor": "rgba(75, 192, 192, 0.5)",
                        "borderColor": "rgb(75, 192, 192)"
                    }
                ],
                "metrics": {
                    "average_velocity": round(avg_velocity, 2),
                    "sprint_count": len(velocity_history),
                    "trend": "improving" if len(velocities) >= 2 and velocities[0] > velocities[-1] else "stable"
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get velocity chart data: {e}")
            return {"error": str(e)}
    
    async def generate_sprint_report(self, sprint_id: int) -> Dict[str, Any]:
        """Generate a comprehensive sprint report."""
        try:
            metrics = await self.get_sprint_metrics(sprint_id)
            if not metrics:
                return {"error": "Sprint not found"}
            
            # Get team velocity history for context
            team = self.db.query(Team).join(Sprint).filter(Sprint.id == sprint_id).first()
            velocity_history = await self.get_team_velocity_history(team.id, 3) if team else []
            
            report = {
                "sprint_overview": {
                    "name": metrics.sprint_name,
                    "team": metrics.team_name,
                    "duration": f"{metrics.start_date} to {metrics.end_date}",
                    "status": "In Progress" if metrics.days_remaining > 0 else "Completed"
                },
                "story_points": {
                    "planned": metrics.total_story_points,
                    "completed": metrics.completed_story_points,
                    "remaining": metrics.remaining_story_points,
                    "completion_rate": f"{metrics.completion_percentage:.1f}%"
                },
                "velocity": {
                    "current_sprint": round(metrics.velocity, 2),
                    "average_last_3_sprints": round(sum(v.velocity for v in velocity_history) / len(velocity_history), 2) if velocity_history else 0
                },
                "timeline": {
                    "days_remaining": metrics.days_remaining,
                    "on_track": metrics.is_on_track,
                    "predicted_completion": metrics.predicted_completion_date.isoformat() if metrics.predicted_completion_date else None
                },
                "insights": await self._generate_sprint_insights(metrics, velocity_history)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate sprint report: {e}")
            return {"error": str(e)}
    
    async def _generate_sprint_insights(self, metrics: SprintMetrics, velocity_history: List[VelocityData]) -> List[str]:
        """Generate AI insights about sprint performance."""
        insights = []
        
        # Completion rate insights
        if metrics.completion_percentage > 80:
            insights.append("🎯 Sprint is performing well with high completion rate")
        elif metrics.completion_percentage < 50:
            insights.append("⚠️ Sprint completion rate is below expectations")
        
        # Timeline insights
        if not metrics.is_on_track and metrics.days_remaining > 0:
            insights.append("📅 Sprint may miss deadline based on current progress")
        elif metrics.is_on_track:
            insights.append("✅ Sprint is on track to meet its goals")
        
        # Velocity insights
        if velocity_history and len(velocity_history) >= 2:
            current_velocity = metrics.velocity
            avg_historical = sum(v.velocity for v in velocity_history) / len(velocity_history)
            
            if current_velocity > avg_historical * 1.2:
                insights.append("🚀 Team velocity is above historical average")
            elif current_velocity < avg_historical * 0.8:
                insights.append("🐌 Team velocity is below historical average")
        
        # Workload insights
        if metrics.days_remaining > 0:
            daily_required = metrics.remaining_story_points / metrics.days_remaining if metrics.days_remaining > 0 else 0
            if daily_required > metrics.velocity * 1.5:
                insights.append("⚡ Remaining work requires increased daily velocity")
        
        return insights

# Global analytics service instance
analytics_service = AnalyticsService()