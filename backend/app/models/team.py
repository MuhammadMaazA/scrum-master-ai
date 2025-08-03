"""
Team model for organizing users and projects.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Table, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base

# Association table for team members
team_members = Table(
    'team_members',
    Base.metadata,
    Column('team_id', Integer, ForeignKey('teams.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role', String, default='member'),  # member, scrum_master, product_owner
    Column('joined_at', DateTime(timezone=True), server_default=func.now())
)

class Team(Base):
    """Team model for organizing users and managing Scrum activities."""
    
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Team configuration
    is_active = Column(Boolean, default=True)
    team_size = Column(Integer, default=0)
    
    # Scrum configuration
    sprint_length_days = Column(Integer, default=14)  # 2-week sprints by default
    standup_time = Column(String, default="09:00")  # 24h format
    standup_timezone = Column(String, default="UTC")
    standup_days = Column(String, default="1,2,3,4,5")  # Mon-Fri (1=Monday)
    
    # Integration settings
    slack_channel_id = Column(String, nullable=True)
    slack_channel_name = Column(String, nullable=True)
    jira_project_key = Column(String, nullable=True)
    github_repo = Column(String, nullable=True)
    
    # AI preferences
    ai_tone = Column(String, default="professional")  # professional, casual, formal
    ai_detail_level = Column(String, default="medium")  # low, medium, high
    auto_standup_enabled = Column(Boolean, default=True)
    auto_grooming_enabled = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    members = relationship("User", secondary=team_members, back_populates="teams")
    projects = relationship("Project", back_populates="team")
    sprints = relationship("Sprint", back_populates="team")
    standup_summaries = relationship("StandupSummary", back_populates="team")

    def __repr__(self):
        return f"<Team(id={self.id}, name='{self.name}', size={self.team_size})>"

    @property
    def scrum_masters(self):
        """Get all Scrum Masters for this team."""
        return [member for member in self.members if member.is_scrum_master]
    
    @property
    def product_owners(self):
        """Get all Product Owners for this team."""
        return [member for member in self.members if member.is_product_owner]

    def get_member_role(self, user_id: int) -> str:
        """Get the role of a specific member in this team."""
        # This would require a query to the team_members association table
        # Implementation would depend on your specific requirements
        return "member"

    def update_team_size(self):
        """Update the team_size field based on active members."""
        self.team_size = len([m for m in self.members if m.is_active])