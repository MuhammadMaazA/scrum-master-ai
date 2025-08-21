"""
AI Agents API endpoints for advanced automation workflows.
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.langchain_agents import scrum_master_agent

router = APIRouter()

class AgentRequest(BaseModel):
    """Request model for agent interactions."""
    request: str
    context: Optional[Dict[str, Any]] = None

class WorkflowRequest(BaseModel):
    """Request model for workflow execution."""
    workflow_type: str
    parameters: Optional[Dict[str, Any]] = None

@router.post("/chat")
async def chat_with_agent(
    agent_request: AgentRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Chat with the AI Scrum Master agent.
    
    The agent can understand natural language requests and use available tools
    to perform complex Scrum Master tasks like managing standups, analyzing sprints,
    creating tickets, and providing insights.
    """
    try:
        if not agent_request.request.strip():
            raise HTTPException(status_code=400, detail="Request cannot be empty")
        
        # Process the request with the agent
        response = await scrum_master_agent.process_request(
            agent_request.request,
            agent_request.context
        )
        
        return {
            "success": True,
            "response": response,
            "agent": "scrum_master",
            "timestamp": "2025-01-02T01:45:00Z"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent chat failed: {str(e)}")

@router.post("/workflow/standup")
async def execute_standup_workflow(
    workflow_request: WorkflowRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Execute the complete daily standup workflow.
    
    This workflow:
    1. Collects standup updates from Slack
    2. Analyzes the updates for progress and blockers
    3. Generates a comprehensive summary
    4. Posts the summary back to Slack
    5. Stores insights for future reference
    """
    try:
        channel = workflow_request.parameters.get("channel", "#standup") if workflow_request.parameters else "#standup"
        
        # Run workflow in background for better performance
        background_tasks.add_task(
            scrum_master_agent.daily_standup_workflow,
            channel
        )
        
        return {
            "success": True,
            "message": f"Daily standup workflow started for channel {channel}",
            "workflow": "standup",
            "status": "running"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Standup workflow failed: {str(e)}")

@router.post("/workflow/sprint-health")
async def execute_sprint_health_check(
    workflow_request: WorkflowRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Execute a comprehensive sprint health check.
    
    This workflow:
    1. Analyzes current sprint metrics
    2. Generates burndown analysis
    3. Identifies risks and issues
    4. Searches for similar past patterns
    5. Provides actionable recommendations
    """
    try:
        if not workflow_request.parameters or "sprint_id" not in workflow_request.parameters:
            raise HTTPException(status_code=400, detail="sprint_id is required in parameters")
        
        sprint_id = workflow_request.parameters["sprint_id"]
        
        # Execute health check
        result = await scrum_master_agent.sprint_health_check(sprint_id)
        
        return {
            "success": True,
            "sprint_id": sprint_id,
            "health_check_result": result,
            "workflow": "sprint_health",
            "status": "completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sprint health check failed: {str(e)}")

@router.post("/workflow/create-ticket")
async def execute_intelligent_ticket_creation(
    workflow_request: WorkflowRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Create a ticket using AI analysis and context.
    
    This workflow:
    1. Analyzes the ticket request
    2. Searches for similar past tickets
    3. Determines appropriate metadata (type, priority, story points)
    4. Creates the ticket in Jira
    5. Stores the decision for future reference
    """
    try:
        if not workflow_request.parameters or "ticket_request" not in workflow_request.parameters:
            raise HTTPException(status_code=400, detail="ticket_request is required in parameters")
        
        ticket_request = workflow_request.parameters["ticket_request"]
        project_context = workflow_request.parameters.get("project_context")
        
        # Execute intelligent ticket creation
        result = await scrum_master_agent.intelligent_ticket_creation(
            ticket_request,
            project_context
        )
        
        return {
            "success": True,
            "ticket_request": ticket_request,
            "creation_result": result,
            "workflow": "intelligent_ticket_creation",
            "status": "completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intelligent ticket creation failed: {str(e)}")

@router.post("/auto-standup")
async def trigger_auto_standup(
    channel: str = "#standup",
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Trigger automatic standup collection and summary.
    
    This is a simplified endpoint for scheduling automatic standups.
    """
    try:
        # Execute standup workflow
        if background_tasks:
            background_tasks.add_task(
                scrum_master_agent.daily_standup_workflow,
                channel
            )
            status = "scheduled"
        else:
            result = await scrum_master_agent.daily_standup_workflow(channel)
            status = "completed"
        
        return {
            "success": True,
            "channel": channel,
            "message": f"Auto-standup triggered for {channel}",
            "status": status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto-standup failed: {str(e)}")

@router.get("/capabilities")
async def get_agent_capabilities() -> Dict[str, Any]:
    """
    Get information about the AI agent's capabilities and available tools.
    """
    try:
        capabilities = {
            "agent_type": "AI Scrum Master",
            "model": "GPT-4",
            "tools": [
                {
                    "name": "slack_messenger",
                    "description": "Send messages, collect standup updates, send reminders",
                    "actions": ["send_message", "collect_standup", "send_reminder"]
                },
                {
                    "name": "jira_manager", 
                    "description": "Manage Jira tickets and project data",
                    "actions": ["create_ticket", "update_status", "sync_project", "get_tickets"]
                },
                {
                    "name": "analytics_generator",
                    "description": "Generate sprint analytics and reports",
                    "actions": ["sprint_metrics", "burndown_chart", "velocity_analysis", "sprint_report"]
                },
                {
                    "name": "knowledge_base",
                    "description": "Access and store project knowledge",
                    "actions": ["search", "store", "get_team_context"]
                }
            ],
            "workflows": [
                {
                    "name": "daily_standup",
                    "description": "Complete standup collection and summary workflow",
                    "automated": True
                },
                {
                    "name": "sprint_health_check",
                    "description": "Comprehensive sprint analysis and recommendations",
                    "automated": False
                },
                {
                    "name": "intelligent_ticket_creation",
                    "description": "AI-powered ticket creation with context analysis",
                    "automated": False
                }
            ],
            "features": [
                "Natural language understanding",
                "Multi-tool orchestration", 
                "Decision making with context",
                "Memory and learning",
                "Workflow automation",
                "Human oversight integration"
            ]
        }
        
        return {
            "success": True,
            "capabilities": capabilities
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get capabilities: {str(e)}"
        }

@router.post("/test-tools")
async def test_agent_tools(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Test the agent's tools to verify they're working correctly.
    """
    try:
        test_results = {}
        
        # Test each tool with a simple operation
        test_request = """Test all your tools to verify they're working:
        1. Use slack_messenger to check connection (don't send actual messages)
        2. Use jira_manager to check connection
        3. Use analytics_generator to verify analytics capabilities
        4. Use knowledge_base to test search functionality
        
        Report the status of each tool."""
        
        result = await scrum_master_agent.process_request(test_request)
        
        return {
            "success": True,
            "test_results": result,
            "message": "Tool testing completed"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Tool testing failed: {str(e)}"
        }

@router.post("/schedule-standup")
async def schedule_recurring_standup(
    schedule_config: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Schedule recurring automatic standups.
    
    Expected config:
    {
        "channel": "#standup",
        "time": "09:00",
        "timezone": "UTC",
        "days": ["monday", "tuesday", "wednesday", "thursday", "friday"]
    }
    """
    try:
        # This would integrate with a job scheduler like Celery Beat
        # For now, we'll return a success message
        
        channel = schedule_config.get("channel", "#standup")
        time = schedule_config.get("time", "09:00")
        days = schedule_config.get("days", ["monday", "tuesday", "wednesday", "thursday", "friday"])
        
        return {
            "success": True,
            "message": f"Scheduled automatic standups for {channel} at {time} on {', '.join(days)}",
            "config": schedule_config,
            "note": "Scheduling system integration required for production deployment"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to schedule standup: {str(e)}")

@router.get("/health")
async def agent_health_check() -> Dict[str, Any]:
    """
    Check the health and status of the AI agent system.
    """
    try:
        # Simple health check
        test_response = await scrum_master_agent.process_request("Hello, are you working correctly?")
        
        return {
            "status": "healthy",
            "agent": "scrum_master",
            "tools_count": len(scrum_master_agent.tools),
            "memory_active": bool(scrum_master_agent.memory),
            "test_response": test_response[:100] + "..." if len(test_response) > 100 else test_response
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }