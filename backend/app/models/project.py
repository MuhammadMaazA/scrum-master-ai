"""
Project model for organizing sprints and backlog items.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class Project(Base):
    """Project model for organizing sprints and backlog management."""
    
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    key = Column(String, unique=True, nullable=False, index=True)  # Like "PROJ"
    
    # Project status
    is_active = Column(Boolean, default=True)
    status = Column(String, default="active")  # active, on_hold, completed, archived
    
    # Integration identifiers
    jira_project_id = Column(String, nullable=True)
    jira_project_key = Column(String, nullable=True)
    github_repo_name = Column(String, nullable=True)
    
    # Project configuration
    default_story_points = Column(Integer, default=1)
    estimation_scale = Column(String, default="fibonacci")  # fibonacci, linear, t_shirt
    
    # Associations
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    team = relationship("Team", back_populates="projects")
    sprints = relationship("Sprint", back_populates="project")
    backlog_items = relationship("BacklogItem", back_populates="project")

    def __repr__(self):
        return f"<Project(id={self.id}, key='{self.key}', name='{self.name}')>"

    @property
    def active_sprint(self):
        """Get the currently active sprint for this project."""
        return next((sprint for sprint in self.sprints if sprint.status == "active"), None)
    
    @property
    def product_backlog(self):
        """Get all backlog items not assigned to any sprint."""
        return [item for item in self.backlog_items if item.sprint_id is None]
    
    @property
    def total_story_points(self):
        """Calculate total story points across all backlog items."""
        return sum(item.story_points or 0 for item in self.backlog_items)
    
    @property
    def completed_story_points(self):
        """Calculate completed story points."""
        return sum(
            item.story_points or 0 
            for item in self.backlog_items 
            if item.status == "done"
        )