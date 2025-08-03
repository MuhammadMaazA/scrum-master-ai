"""
Sprint model for managing sprint cycles and tracking progress.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from typing import Dict, Any

from app.core.database import Base

class Sprint(Base):
    """Sprint model for managing sprint cycles."""
    
    __tablename__ = "sprints"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    goal = Column(Text, nullable=True)
    
    # Sprint timing
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    
    # Sprint status
    status = Column(String, default="planned")  # planned, active, completed, cancelled
    
    # Sprint metrics
    planned_capacity = Column(Float, default=0.0)  # Total story points planned
    actual_velocity = Column(Float, default=0.0)  # Story points completed
    team_capacity_days = Column(Float, default=0.0)  # Total available person-days
    
    # AI insights and notes
    ai_generated_goal = Column(Text, nullable=True)
    ai_insights = Column(Text, nullable=True)  # JSON string with AI analysis
    risk_factors = Column(Text, nullable=True)  # JSON string with identified risks
    
    # Associations
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="sprints")
    team = relationship("Team", back_populates="sprints")
    backlog_items = relationship("BacklogItem", back_populates="sprint")
    standup_summaries = relationship("StandupSummary", back_populates="sprint")

    def __repr__(self):
        return f"<Sprint(id={self.id}, name='{self.name}', status='{self.status}')>"

    @property
    def duration_days(self) -> int:
        """Calculate sprint duration in days."""
        return (self.end_date - self.start_date).days

    @property
    def days_remaining(self) -> int:
        """Calculate days remaining in sprint."""
        if self.status != "active":
            return 0
        remaining = (self.end_date - datetime.now()).days
        return max(0, remaining)

    @property
    def progress_percentage(self) -> float:
        """Calculate sprint progress as percentage."""
        if self.planned_capacity == 0:
            return 0.0
        return min(100.0, (self.actual_velocity / self.planned_capacity) * 100)

    @property
    def burndown_data(self) -> Dict[str, Any]:
        """Generate burndown chart data."""
        # This would be populated by tracking daily progress
        # For now, return basic structure
        return {
            "planned_capacity": self.planned_capacity,
            "actual_velocity": self.actual_velocity,
            "days_remaining": self.days_remaining,
            "ideal_burndown": self._calculate_ideal_burndown(),
            "actual_burndown": self._calculate_actual_burndown()
        }

    def _calculate_ideal_burndown(self) -> list:
        """Calculate ideal burndown line."""
        if self.duration_days == 0:
            return []
        
        daily_burn = self.planned_capacity / self.duration_days
        return [
            {
                "day": i,
                "remaining": self.planned_capacity - (daily_burn * i)
            }
            for i in range(self.duration_days + 1)
        ]

    def _calculate_actual_burndown(self) -> list:
        """Calculate actual burndown based on completed work."""
        # This would query daily snapshots of completed work
        # For now, return simple linear progression
        completed = self.actual_velocity
        remaining = self.planned_capacity - completed
        
        return [
            {"day": 0, "remaining": self.planned_capacity},
            {"day": self.duration_days - self.days_remaining, "remaining": remaining}
        ]

    @property
    def velocity_trend(self) -> str:
        """Analyze velocity trend compared to plan."""
        if self.planned_capacity == 0:
            return "unknown"
        
        progress_rate = self.actual_velocity / self.planned_capacity
        days_elapsed = self.duration_days - self.days_remaining
        expected_progress = days_elapsed / self.duration_days if self.duration_days > 0 else 0
        
        if progress_rate > expected_progress * 1.1:
            return "ahead"
        elif progress_rate < expected_progress * 0.9:
            return "behind"
        else:
            return "on_track"

    def calculate_forecasted_completion(self) -> float:
        """Forecast sprint completion percentage based on current velocity."""
        if self.days_remaining <= 0 or self.planned_capacity == 0:
            return self.progress_percentage
        
        days_elapsed = self.duration_days - self.days_remaining
        if days_elapsed <= 0:
            return 0.0
        
        current_velocity = self.actual_velocity / days_elapsed
        forecasted_total = current_velocity * self.duration_days
        
        return min(100.0, (forecasted_total / self.planned_capacity) * 100)