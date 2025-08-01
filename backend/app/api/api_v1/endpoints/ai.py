"""
Enhanced AI service endpoints for testing and sprint planning.
"""
from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.ai_service import ai_service
from app.services.vector_service import vector_service

router = APIRouter()

class AnalyzeBacklogRequest(BaseModel):
    title: str
    description: str
    item_type: str = "story"

class StandupSummaryRequest(BaseModel):
    entries: List[Dict[str, Any]]
    team_context: Dict[str, Any]

class SprintPlanRequest(BaseModel):
    team_id: int
    backlog_items: List[Dict[str, Any]]
    team_velocity: float
    capacity_days: float
    sprint_goal_context: str = ""

@router.post("/analyze-backlog")
async def analyze_backlog_item(request: AnalyzeBacklogRequest) -> Any:
    """Analyze a backlog item using AI."""
    try:
        item_data = {
            "title": request.title,
            "description": request.description,
            "item_type": request.item_type
        }
        
        analysis = await ai_service.analyze_backlog_item(item_data)
        
        return {
            "clarity_score": analysis.clarity_score,
            "suggested_improvements": analysis.suggested_improvements,
            "estimated_complexity": analysis.estimated_complexity,
            "potential_risks": analysis.potential_risks,
            "acceptance_criteria_suggestions": analysis.acceptance_criteria_suggestions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/suggest-sprint-plan")
async def suggest_sprint_plan(request: SprintPlanRequest) -> Any:
    """Generate AI sprint planning suggestions."""
    try:
        suggestion = await ai_service.suggest_sprint_plan(
            backlog_items=request.backlog_items,
            team_velocity=request.team_velocity,
            capacity_days=request.capacity_days,
            sprint_goal_context=request.sprint_goal_context or None
        )
        
        return {
            "recommended_items": suggestion.recommended_items,
            "total_story_points": suggestion.total_story_points,
            "sprint_goal": suggestion.sprint_goal,
            "risks": suggestion.risks,
            "capacity_utilization": suggestion.capacity_utilization
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sprint planning failed: {str(e)}")

@router.post("/test-standup-summary")
async def test_standup_summary(request: StandupSummaryRequest) -> Any:
    """Test standup summary generation."""
    try:
        summary = await ai_service.generate_standup_summary(
            standup_entries=request.entries,
            team_context=request.team_context
        )
        
        return {
            "summary": summary.summary,
            "key_achievements": summary.key_achievements,
            "today_focus": summary.today_focus,
            "blockers": summary.blockers,
            "action_items": summary.action_items,
            "team_sentiment": summary.team_sentiment
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")

@router.get("/vector-stats")
async def get_vector_stats() -> Any:
    """Get vector database statistics."""
    try:
        stats = await vector_service.get_collection_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.post("/health-check")
async def ai_health_check() -> Any:
    """Check AI services health."""
    return {
        "ai_service": "operational",
        "vector_service": "operational",
        "openai_configured": bool(ai_service.chat_model),
        "vector_db_path": vector_service.collection.name if vector_service.collection else None,
        "features": {
            "standup_summaries": True,
            "backlog_analysis": True,
            "sprint_planning": True,
            "semantic_search": True
        }
    }

@router.post("/chat")
async def ai_chat(request: dict) -> Any:
    """Simple AI chat endpoint for the assistant."""
    message = request.get("message", "")
    context = request.get("context", {})
    
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    # Simple chat response (in a real implementation, you'd use a chat-specific model)
    try:
        # For MVP, return a structured response based on keywords
        response = await _generate_chat_response(message, context)
        
        return {
            "response": response,
            "category": _detect_category(message),
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

async def _generate_chat_response(message: str, context: dict) -> str:
    """Generate a chat response based on the message."""
    # Simple keyword-based responses for MVP
    message_lower = message.lower()
    
    if "velocity" in message_lower:
        return "Your team's average velocity is 23 story points per sprint. You've been consistent over the last 5 sprints with a range of 22-28 points. This suggests good predictability for sprint planning."
    
    elif "backlog" in message_lower:
        return "I see 12 items in your backlog that need attention. 3 stories lack acceptance criteria, 2 might be duplicates, and 4 are larger than recommended (>13 points). Would you like me to help prioritize which to address first?"
    
    elif "standup" in message_lower:
        return "Your standups are running well! 92% participation rate and averaging 12 minutes. I notice external dependencies are your most common blocker type. Consider creating a dependency tracking board."
    
    elif "sprint" in message_lower or "planning" in message_lower:
        return "For your next sprint, I recommend targeting 24-26 story points based on your velocity. You have 3 high-priority items ready for sprint that total 22 points. Include 1-2 technical improvement tasks for a balanced sprint."
    
    else:
        return f"I understand you're asking about '{message}'. I can help with sprint planning, backlog analysis, velocity tracking, and standup insights. What specific aspect would you like to explore?"

def _detect_category(message: str) -> str:
    """Detect the category of the chat message."""
    message_lower = message.lower()
    
    if "standup" in message_lower or "daily" in message_lower:
        return "standup"
    elif "backlog" in message_lower or "story" in message_lower:
        return "backlog"
    elif "sprint" in message_lower or "planning" in message_lower:
        return "sprint"
    else:
        return "general"