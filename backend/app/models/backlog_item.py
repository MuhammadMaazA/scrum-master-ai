"""
Backlog item model for user stories, bugs, and tasks.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, Any, Optional

from app.core.database import Base

class BacklogItem(Base):
    """Backlog item model for user stories, bugs, and tasks."""
    
    __tablename__ = "backlog_items"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic item information
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    acceptance_criteria = Column(Text, nullable=True)
    
    # Item classification
    item_type = Column(String, default="story")  # story, bug, task, epic, spike
    priority = Column(String, default="medium")  # critical, high, medium, low
    status = Column(String, default="todo")  # todo, in_progress, review, done, blocked
    
    # Estimation and effort
    story_points = Column(Integer, nullable=True)
    estimated_hours = Column(Float, nullable=True)
    actual_hours = Column(Float, nullable=True)
    
    # External system identifiers
    jira_key = Column(String, nullable=True, unique=True, index=True)
    jira_id = Column(String, nullable=True)
    github_issue_number = Column(Integer, nullable=True)
    
    # AI analysis and suggestions
    ai_suggested_points = Column(Integer, nullable=True)
    ai_complexity_score = Column(Float, nullable=True)  # 0.0 to 1.0
    ai_suggestions = Column(Text, nullable=True)  # JSON string with AI recommendations
    ai_clarity_score = Column(Float, nullable=True)  # 0.0 to 1.0, how clear the description is
    duplicate_candidates = Column(Text, nullable=True)  # JSON array of potentially duplicate item IDs
    
    # Workflow tracking
    blocked_reason = Column(Text, nullable=True)
    blocked_since = Column(DateTime(timezone=True), nullable=True)
    
    # Business value and ranking
    business_value = Column(Integer, nullable=True)  # 1-100 scale
    effort_estimate = Column(String, nullable=True)  # XS, S, M, L, XL, XXL
    value_effort_ratio = Column(Float, nullable=True)  # Calculated ratio for prioritization
    
    # Dependencies
    depends_on = Column(Text, nullable=True)  # JSON array of item IDs this depends on
    blocks = Column(Text, nullable=True)  # JSON array of item IDs this blocks
    
    # Associations
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=True)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    project = relationship("Project", back_populates="backlog_items")
    sprint = relationship("Sprint", back_populates="backlog_items")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_backlog_items")
    created_by = relationship("User", foreign_keys=[created_by_id], back_populates="created_backlog_items")

    def __repr__(self):
        return f"<BacklogItem(id={self.id}, title='{self.title[:50]}...', status='{self.status}')>"

    @property
    def is_blocked(self) -> bool:
        """Check if this item is currently blocked."""
        return self.status == "blocked"

    @property
    def is_complete(self) -> bool:
        """Check if this item is completed."""
        return self.status == "done"

    @property
    def is_in_sprint(self) -> bool:
        """Check if this item is assigned to a sprint."""
        return self.sprint_id is not None

    @property
    def age_days(self) -> int:
        """Calculate age of the item in days."""
        return (datetime.now() - self.created_at).days

    @property
    def needs_clarification(self) -> bool:
        """Check if item needs clarification based on AI analysis."""
        if self.ai_clarity_score is None:
            return len(self.description or "") < 50  # Simple heuristic
        return self.ai_clarity_score < 0.6

    @property
    def has_dependencies(self) -> bool:
        """Check if item has dependencies."""
        return bool(self.depends_on and self.depends_on.strip())

    @property
    def is_high_value(self) -> bool:
        """Check if item is considered high business value."""
        if self.business_value is None:
            return False
        return self.business_value >= 80

    def calculate_value_effort_ratio(self) -> Optional[float]:
        """Calculate and update the value-effort ratio for prioritization."""
        if self.business_value is None or self.story_points is None or self.story_points == 0:
            return None
        
        ratio = self.business_value / self.story_points
        self.value_effort_ratio = ratio
        return ratio

    def mark_complete(self):
        """Mark the item as complete and set completion timestamp."""
        self.status = "done"
        self.completed_at = datetime.now()

    def mark_blocked(self, reason: str):
        """Mark the item as blocked with a reason."""
        self.status = "blocked"
        self.blocked_reason = reason
        self.blocked_since = datetime.now()

    def unblock(self):
        """Remove blocked status."""
        if self.status == "blocked":
            self.status = "todo"  # Reset to default
            self.blocked_reason = None
            self.blocked_since = None

    def get_ai_suggestions_dict(self) -> Dict[str, Any]:
        """Parse AI suggestions from JSON string."""
        if not self.ai_suggestions:
            return {}
        try:
            import json
            return json.loads(self.ai_suggestions)
        except:
            return {}

    def set_ai_suggestions(self, suggestions: Dict[str, Any]):
        """Set AI suggestions as JSON string."""
        import json
        self.ai_suggestions = json.dumps(suggestions)

    def get_duplicate_candidates_list(self) -> list:
        """Get list of duplicate candidate IDs."""
        if not self.duplicate_candidates:
            return []
        try:
            import json
            return json.loads(self.duplicate_candidates)
        except:
            return []

    def add_duplicate_candidate(self, item_id: int):
        """Add an item ID to duplicate candidates."""
        candidates = self.get_duplicate_candidates_list()
        if item_id not in candidates:
            candidates.append(item_id)
            import json
            self.duplicate_candidates = json.dumps(candidates)