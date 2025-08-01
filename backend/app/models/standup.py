"""
Standup models for daily standup entries and AI-generated summaries.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base

class StandupEntry(Base):
    """Individual team member's standup entry."""
    
    __tablename__ = "standup_entries"

    id = Column(Integer, primary_key=True, index=True)
    
    # Standup content
    yesterday_work = Column(Text, nullable=True)
    today_plan = Column(Text, nullable=True)
    blockers = Column(Text, nullable=True)
    additional_notes = Column(Text, nullable=True)
    
    # Entry metadata
    entry_date = Column(DateTime(timezone=True), nullable=False)
    source = Column(String, default="manual")  # manual, slack, web_form, ai_detected
    confidence_score = Column(Integer, default=100)  # AI confidence if auto-generated
    
    # Associations
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="standup_entries")

    def __repr__(self):
        return f"<StandupEntry(id={self.id}, user_id={self.user_id}, date={self.entry_date})>"

    @property
    def has_blockers(self) -> bool:
        """Check if this entry has any blockers."""
        return bool(self.blockers and self.blockers.strip())
    
    @property
    def is_complete(self) -> bool:
        """Check if standup entry has all required fields."""
        return bool(
            self.yesterday_work and self.yesterday_work.strip() and
            self.today_plan and self.today_plan.strip()
        )

class StandupSummary(Base):
    """AI-generated daily standup summary for the team."""
    
    __tablename__ = "standup_summaries"

    id = Column(Integer, primary_key=True, index=True)
    
    # Summary content
    summary_text = Column(Text, nullable=False)
    key_achievements = Column(Text, nullable=True)  # JSON array of achievements
    active_blockers = Column(Text, nullable=True)  # JSON array of blockers
    focus_areas = Column(Text, nullable=True)  # JSON array of today's focus
    action_items = Column(Text, nullable=True)  # JSON array of follow-up actions
    
    # Summary metadata
    summary_date = Column(DateTime(timezone=True), nullable=False)
    participants_count = Column(Integer, default=0)
    missing_members = Column(Text, nullable=True)  # JSON array of user IDs
    
    # AI generation details
    ai_model_used = Column(String, default="gpt-4")
    generation_prompt = Column(Text, nullable=True)
    confidence_score = Column(Integer, default=100)
    human_reviewed = Column(Boolean, default=False)
    human_reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Status and delivery
    status = Column(String, default="generated")  # generated, reviewed, published, archived
    posted_to_slack = Column(Boolean, default=False)
    slack_message_ts = Column(String, nullable=True)
    slack_channel_id = Column(String, nullable=True)
    
    # Associations
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    sprint_id = Column(Integer, ForeignKey("sprints.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    team = relationship("Team", back_populates="standup_summaries")
    sprint = relationship("Sprint", back_populates="standup_summaries")

    def __repr__(self):
        return f"<StandupSummary(id={self.id}, team_id={self.team_id}, date={self.summary_date})>"

    @property
    def is_current(self) -> bool:
        """Check if this summary is for today."""
        return self.summary_date.date() == datetime.now().date()
    
    @property
    def blockers_count(self) -> int:
        """Count active blockers."""
        if not self.active_blockers:
            return 0
        try:
            import json
            blockers = json.loads(self.active_blockers)
            return len(blockers) if isinstance(blockers, list) else 0
        except:
            return 0

    @property
    def action_items_count(self) -> int:
        """Count action items."""
        if not self.action_items:
            return 0
        try:
            import json
            items = json.loads(self.action_items)
            return len(items) if isinstance(items, list) else 0
        except:
            return 0

    def mark_as_published(self):
        """Mark summary as published and set timestamp."""
        self.status = "published"
        self.published_at = datetime.now()

    def mark_slack_posted(self, message_ts: str, channel_id: str):
        """Mark as posted to Slack with message details."""
        self.posted_to_slack = True
        self.slack_message_ts = message_ts
        self.slack_channel_id = channel_id