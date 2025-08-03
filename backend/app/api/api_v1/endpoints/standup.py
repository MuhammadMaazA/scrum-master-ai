"""
Standup endpoints for daily standup coordination and AI summaries.
This is the core MVP feature implementing the AI-powered standup workflow.
"""
from typing import List, Any, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.services.ai_service import ai_service
from app.services.slack_service import slack_service
from app.services.jira_service import jira_service
from app.services.vector_service import vector_service

router = APIRouter()

# Pydantic models for API requests/responses
class StandupEntryCreate(BaseModel):
    user_id: int
    yesterday_work: Optional[str] = None
    today_plan: Optional[str] = None
    blockers: Optional[str] = None
    additional_notes: Optional[str] = None

class StandupSummaryResponse(BaseModel):
    id: int
    summary_text: str
    key_achievements: List[str]
    active_blockers: List[dict]
    focus_areas: List[str]
    action_items: List[dict]
    summary_date: datetime
    participants_count: int
    status: str
    posted_to_slack: bool

class GenerateStandupRequest(BaseModel):
    team_id: int
    date: Optional[date] = None
    include_jira_updates: bool = True
    slack_channel_id: Optional[str] = None

@router.get("/teams/{team_id}/summaries")
async def get_team_standup_summaries(
    team_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
) -> List[StandupSummaryResponse]:
    """Get recent standup summaries for a team."""
    # TODO: Implement database query for standup summaries
    # For MVP, return mock data
    return [
        StandupSummaryResponse(
            id=1,
            summary_text="Team completed payment module and fixed critical bugs. Focus today on cart integration.",
            key_achievements=["Payment module completed", "3 critical bugs resolved"],
            active_blockers=[{"description": "Waiting for UX designs", "owner": "Design team"}],
            focus_areas=["Cart integration", "API testing"],
            action_items=[{"action": "Follow up on UX designs", "assignee": "Scrum Master"}],
            summary_date=datetime.now(),
            participants_count=5,
            status="published",
            posted_to_slack=True
        )
    ]

@router.post("/teams/{team_id}/entries")
async def create_standup_entry(
    team_id: int,
    entry: StandupEntryCreate,
    db: Session = Depends(get_db)
) -> Any:
    """Create a new standup entry for a team member."""
    # TODO: Implement database insertion
    # For MVP, store in memory or simple validation
    
    if not any([entry.yesterday_work, entry.today_plan, entry.blockers]):
        raise HTTPException(
            status_code=400,
            detail="At least one standup field must be provided"
        )
    
    # Here you would typically:
    # 1. Validate user belongs to team
    # 2. Store entry in database
    # 3. Potentially trigger summary generation if all team members have submitted
    
    return {
        "message": "Standup entry created successfully",
        "entry_id": 123,  # Mock ID
        "team_id": team_id
    }

@router.post("/teams/{team_id}/generate-summary")
async def generate_standup_summary(
    team_id: int,
    request: GenerateStandupRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Any:
    """
    Generate AI-powered standup summary for a team.
    This is the core MVP feature that demonstrates the AI Scrum Master capability.
    """
    try:
        # 1. Collect standup entries (from database or Slack)
        standup_entries = await _collect_standup_data(team_id, request.slack_channel_id)
        
        if not standup_entries:
            raise HTTPException(
                status_code=404,
                detail="No standup entries found for today"
            )
        
        # 2. Get Jira updates if requested
        jira_updates = None
        if request.include_jira_updates:
            jira_updates = await _get_jira_updates(team_id)
        
        # 3. Get team context
        team_context = await _get_team_context(team_id)
        
        # 4. Generate AI summary
        ai_summary = await ai_service.generate_standup_summary(
            standup_entries=standup_entries,
            team_context=team_context,
            jira_updates=jira_updates
        )
        
        # 5. Store summary in database
        summary_id = await _store_summary(team_id, ai_summary, len(standup_entries))
        
        # 6. Post to Slack if channel provided
        if request.slack_channel_id:
            background_tasks.add_task(
                _post_summary_to_slack,
                request.slack_channel_id,
                ai_summary.summary,
                summary_id
            )
        
        # 7. Store context in vector database for future reference
        background_tasks.add_task(
            _store_summary_context,
            team_id,
            ai_summary
        )
        
        return {
            "message": "Standup summary generated successfully",
            "summary_id": summary_id,
            "summary": ai_summary.summary,
            "key_achievements": ai_summary.key_achievements,
            "blockers": ai_summary.blockers,
            "action_items": ai_summary.action_items,
            "team_sentiment": ai_summary.team_sentiment,
            "posted_to_slack": bool(request.slack_channel_id)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate standup summary: {str(e)}"
        )

@router.post("/slack/collect/{team_id}")
async def collect_slack_standup_messages(
    team_id: int,
    channel_id: str,
    hours_back: int = 24
) -> Any:
    """
    Collect standup messages from Slack channel and convert to standup entries.
    """
    try:
        # Collect messages from Slack
        messages = await slack_service.collect_standup_messages(
            channel_id=channel_id,
            since_hours=hours_back,
            keywords=["yesterday", "today", "blockers", "standup"]
        )
        
        # Parse messages into standup entries
        entries = []
        for message in messages:
            parsed = await slack_service.parse_standup_from_message(message["message"])
            
            entry = {
                "user_name": message["user_name"],
                "user_id": message["user_id"],
                "yesterday_work": parsed["yesterday_work"],
                "today_plan": parsed["today_plan"],
                "blockers": parsed["blockers"],
                "additional_notes": parsed["additional_notes"],
                "timestamp": message["timestamp"]
            }
            entries.append(entry)
        
        return {
            "message": f"Collected {len(entries)} standup entries from Slack",
            "entries": entries,
            "channel_id": channel_id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to collect Slack messages: {str(e)}"
        )

@router.post("/slack/reminder/{team_id}")
async def send_standup_reminder(
    team_id: int,
    channel_id: str,
    custom_message: Optional[str] = None
) -> Any:
    """Send standup reminder to Slack channel."""
    try:
        message_ts = await slack_service.send_standup_reminder(
            channel_id=channel_id,
            custom_message=custom_message
        )
        
        if message_ts:
            return {
                "message": "Standup reminder sent successfully",
                "slack_timestamp": message_ts,
                "channel_id": channel_id
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to send Slack reminder"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send standup reminder: {str(e)}"
        )

# Helper functions
async def _collect_standup_data(team_id: int, slack_channel_id: Optional[str] = None) -> List[dict]:
    """Collect standup data from database and/or Slack."""
    entries = []
    
    # Try to get from Slack first if channel provided
    if slack_channel_id:
        try:
            slack_messages = await slack_service.collect_standup_messages(
                channel_id=slack_channel_id,
                since_hours=24
            )
            
            for message in slack_messages:
                parsed = await slack_service.parse_standup_from_message(message["message"])
                entries.append({
                    "user": message["user_name"],
                    "yesterday_work": parsed["yesterday_work"],
                    "today_plan": parsed["today_plan"],
                    "blockers": parsed["blockers"],
                    "source": "slack"
                })
        except Exception as e:
            print(f"Failed to collect from Slack: {e}")
    
    # TODO: Also collect from database entries
    # db_entries = get_todays_standup_entries(team_id)
    # entries.extend(db_entries)
    
    # For MVP, provide sample data if nothing found
    if not entries:
        entries = [
            {
                "user": "Alice Smith",
                "yesterday_work": "Completed payment integration API, fixed 2 critical bugs",
                "today_plan": "Working on cart functionality, code review for Bob's PR",
                "blockers": "Waiting for UX designs for checkout flow",
                "source": "sample"
            },
            {
                "user": "Bob Johnson", 
                "yesterday_work": "Finished user authentication module, updated documentation",
                "today_plan": "Starting shopping cart backend, team planning meeting",
                "blockers": "",
                "source": "sample"
            }
        ]
    
    return entries

async def _get_jira_updates(team_id: int) -> List[dict]:
    """Get recent Jira updates for the team."""
    try:
        # TODO: Get project key from team configuration
        project_key = "DEMO"  # For MVP
        
        updates = await jira_service.get_recent_ticket_updates(
            project_key=project_key,
            hours_back=24
        )
        
        return updates
    except Exception as e:
        print(f"Failed to get Jira updates: {e}")
        return []

async def _get_team_context(team_id: int) -> dict:
    """Get team configuration and context."""
    # TODO: Get from database
    return {
        "id": team_id,
        "name": "Development Team",
        "ai_tone": "professional",
        "standup_time": "09:00",
        "timezone": "UTC"
    }

async def _store_summary(team_id: int, ai_summary, participants_count: int) -> int:
    """Store the AI-generated summary in database."""
    # TODO: Implement database storage
    # For MVP, return mock ID
    return 123

async def _post_summary_to_slack(channel_id: str, summary: str, summary_id: int):
    """Post summary to Slack channel."""
    try:
        await slack_service.post_standup_summary(
            channel_id=channel_id,
            summary=summary
        )
        print(f"Posted summary {summary_id} to Slack channel {channel_id}")
    except Exception as e:
        print(f"Failed to post to Slack: {e}")

async def _store_summary_context(team_id: int, ai_summary):
    """Store summary context in vector database."""
    try:
        context_text = f"Standup summary: {ai_summary.summary}"
        if ai_summary.blockers:
            context_text += f" Blockers: {', '.join([b.get('description', '') for b in ai_summary.blockers])}"
        
        await vector_service.store_standup_summary(
            summary=context_text,
            team_id=team_id,
            date=datetime.now()
        )
        print(f"Stored context for team {team_id}")
    except Exception as e:
        print(f"Failed to store context: {e}")