"""
User model for authentication and team management.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

class User(Base):
    """User model for team members and Scrum Masters."""
    
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, default="team_member")  # team_member, scrum_master, product_owner, admin
    
    # Authentication
    hashed_password = Column(String, nullable=True)  # OAuth users might not have passwords
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # External IDs for integrations
    slack_user_id = Column(String, nullable=True, unique=True)
    jira_account_id = Column(String, nullable=True)
    github_username = Column(String, nullable=True)
    
    # Profile information
    avatar_url = Column(String, nullable=True)
    timezone = Column(String, default="UTC")
    
    # Preferences
    notification_preferences = Column(Text, nullable=True)  # JSON string
    ai_interaction_preferences = Column(Text, nullable=True)  # JSON string
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    teams = relationship("Team", secondary="team_members", back_populates="members")
    standup_entries = relationship("StandupEntry", back_populates="user")
    assigned_backlog_items = relationship("BacklogItem", foreign_keys="BacklogItem.assignee_id", back_populates="assignee")
    created_backlog_items = relationship("BacklogItem", foreign_keys="BacklogItem.created_by_id", back_populates="created_by")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"

    @property
    def is_scrum_master(self) -> bool:
        """Check if user has Scrum Master role."""
        return self.role in ["scrum_master", "admin"]
    
    @property
    def is_product_owner(self) -> bool:
        """Check if user has Product Owner role."""
        return self.role in ["product_owner", "admin"]
    
    @property
    def can_admin(self) -> bool:
        """Check if user has admin privileges."""
        return self.role == "admin"