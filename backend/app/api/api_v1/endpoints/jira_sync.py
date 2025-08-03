"""
Jira synchronization API endpoints for data sync and automation.
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.jira_service import jira_service
from app.core.config import settings

router = APIRouter()

@router.post("/sync/backlog/{project_key}")
async def sync_backlog_items(
    project_key: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Sync backlog items from Jira to local database.
    
    This endpoint fetches all issues from the specified Jira project
    and creates or updates corresponding backlog items in the local database.
    """
    try:
        # Validate project key
        if not project_key or len(project_key) < 2:
            raise HTTPException(status_code=400, detail="Invalid project key")
        
        # Check if Jira client is available
        if not jira_service.client:
            raise HTTPException(
                status_code=503, 
                detail="Jira integration not configured. Please check your credentials."
            )
        
        # Run sync in background for large projects
        background_tasks.add_task(jira_service.sync_backlog_items, project_key)
        
        return {
            "success": True,
            "message": f"Backlog sync started for project {project_key}",
            "project_key": project_key
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start backlog sync: {str(e)}")

@router.post("/sync/sprints/{project_key}")
async def sync_sprint_data(
    project_key: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Sync sprint data from Jira to local database.
    
    This endpoint fetches sprint information from the specified Jira project
    and creates or updates corresponding sprints in the local database.
    """
    try:
        # Validate project key
        if not project_key or len(project_key) < 2:
            raise HTTPException(status_code=400, detail="Invalid project key")
        
        # Check if Jira client is available
        if not jira_service.client:
            raise HTTPException(
                status_code=503, 
                detail="Jira integration not configured. Please check your credentials."
            )
        
        # Run sync in background
        background_tasks.add_task(jira_service.sync_sprint_data, project_key)
        
        return {
            "success": True,
            "message": f"Sprint sync started for project {project_key}",
            "project_key": project_key
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start sprint sync: {str(e)}")

@router.post("/sync/auto/{project_key}")
async def auto_sync_project(
    project_key: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Perform complete auto-sync of project data from Jira.
    
    This endpoint synchronizes both backlog items and sprint data
    from the specified Jira project to the local database.
    """
    try:
        # Validate project key
        if not project_key or len(project_key) < 2:
            raise HTTPException(status_code=400, detail="Invalid project key")
        
        # Check if Jira client is available
        if not jira_service.client:
            raise HTTPException(
                status_code=503, 
                detail="Jira integration not configured. Please check your credentials."
            )
        
        # Run complete sync in background
        background_tasks.add_task(jira_service.auto_sync_project_data, project_key)
        
        return {
            "success": True,
            "message": f"Complete auto-sync started for project {project_key}",
            "project_key": project_key,
            "sync_includes": ["backlog_items", "sprints", "project_data"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start auto-sync: {str(e)}")

@router.post("/sync/now/{project_key}")
async def sync_project_now(
    project_key: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Perform immediate synchronization (synchronous).
    
    Use this for smaller projects or when you need immediate results.
    For larger projects, use the async endpoints above.
    """
    try:
        # Validate project key
        if not project_key or len(project_key) < 2:
            raise HTTPException(status_code=400, detail="Invalid project key")
        
        # Check if Jira client is available
        if not jira_service.client:
            raise HTTPException(
                status_code=503, 
                detail="Jira integration not configured. Please check your credentials."
            )
        
        # Perform immediate sync
        sync_results = await jira_service.auto_sync_project_data(project_key)
        
        if "error" in sync_results:
            raise HTTPException(status_code=500, detail=sync_results["error"])
        
        return {
            "success": True,
            "data": sync_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync project: {str(e)}")

@router.post("/create-ticket")
async def create_jira_ticket(
    ticket_data: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Create a new ticket in Jira.
    
    Expected ticket_data format:
    {
        "title": "Ticket title",
        "description": "Ticket description",
        "issue_type": "Story|Task|Bug|Epic",
        "priority": "High|Medium|Low",
        "story_points": 5,
        "project_key": "PROJ" (optional, uses default if not provided)
    }
    """
    try:
        # Check if Jira client is available
        if not jira_service.client:
            raise HTTPException(
                status_code=503, 
                detail="Jira integration not configured. Please check your credentials."
            )
        
        # Validate required fields
        if not ticket_data.get("title"):
            raise HTTPException(status_code=400, detail="Ticket title is required")
        
        # Create ticket in Jira
        ticket_key = await jira_service.create_jira_ticket(ticket_data)
        
        if not ticket_key:
            raise HTTPException(status_code=500, detail="Failed to create ticket in Jira")
        
        return {
            "success": True,
            "ticket_key": ticket_key,
            "message": f"Ticket {ticket_key} created successfully",
            "jira_url": f"{settings.JIRA_URL}/browse/{ticket_key}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create ticket: {str(e)}")

@router.put("/update-ticket-status/{ticket_key}")
async def update_ticket_status(
    ticket_key: str,
    status_data: Dict[str, str],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Update the status of a Jira ticket.
    
    Expected status_data format:
    {
        "status": "To Do|In Progress|Done|etc."
    }
    """
    try:
        # Check if Jira client is available
        if not jira_service.client:
            raise HTTPException(
                status_code=503, 
                detail="Jira integration not configured. Please check your credentials."
            )
        
        # Validate inputs
        if not ticket_key:
            raise HTTPException(status_code=400, detail="Ticket key is required")
        
        new_status = status_data.get("status")
        if not new_status:
            raise HTTPException(status_code=400, detail="New status is required")
        
        # Update ticket status
        success = await jira_service.update_ticket_status(ticket_key, new_status)
        
        if not success:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to update {ticket_key} to status '{new_status}'"
            )
        
        return {
            "success": True,
            "ticket_key": ticket_key,
            "new_status": new_status,
            "message": f"Ticket {ticket_key} status updated to '{new_status}'"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update ticket status: {str(e)}")

@router.get("/projects")
async def get_jira_projects() -> Dict[str, Any]:
    """
    Get list of available Jira projects.
    
    Returns projects that the current user has access to.
    """
    try:
        # Check if Jira client is available
        if not jira_service.client:
            raise HTTPException(
                status_code=503, 
                detail="Jira integration not configured. Please check your credentials."
            )
        
        projects = await jira_service.get_projects()
        
        return {
            "success": True,
            "projects": projects,
            "count": len(projects)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get projects: {str(e)}")

@router.get("/connection-test")
async def test_jira_connection() -> Dict[str, Any]:
    """
    Test the Jira connection and return connection status.
    
    Useful for verifying credentials and configuration.
    """
    try:
        if not jira_service.client:
            return {
                "success": False,
                "connected": False,
                "message": "Jira client not initialized. Check your configuration.",
                "config_status": {
                    "jira_url": bool(settings.JIRA_URL),
                    "jira_username": bool(settings.JIRA_USERNAME),
                    "jira_api_token": bool(settings.JIRA_API_TOKEN),
                    "jira_project_key": bool(settings.JIRA_PROJECT_KEY)
                }
            }
        
        # Test connection
        is_connected = await jira_service.test_connection()
        
        return {
            "success": True,
            "connected": is_connected,
            "message": "Connection successful" if is_connected else "Connection failed",
            "jira_url": settings.JIRA_URL,
            "project_key": settings.JIRA_PROJECT_KEY
        }
        
    except Exception as e:
        return {
            "success": False,
            "connected": False,
            "message": f"Connection test failed: {str(e)}"
        }

@router.get("/sync-status/{project_key}")
async def get_sync_status(
    project_key: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get the synchronization status for a project.
    
    Returns information about the last sync and current data state.
    """
    try:
        from app.models.backlog_item import BacklogItem
        from app.models.sprint import Sprint
        from app.models.project import Project
        
        # Get project info
        project = db.query(Project).filter(Project.jira_project_key == project_key).first()
        if not project:
            raise HTTPException(status_code=404, detail=f"Project {project_key} not found")
        
        # Count synced items
        backlog_count = db.query(BacklogItem).filter(
            BacklogItem.project_id == project.id,
            BacklogItem.jira_key.isnot(None)
        ).count()
        
        sprint_count = db.query(Sprint).filter(
            Sprint.jira_sprint_id.isnot(None)
        ).count()
        
        # Get recent sync info from vector database
        from app.services.vector_service import vector_service
        recent_syncs = await vector_service.get_relevant_context(
            f"sync project {project_key}",
            limit=1,
            document_type="sync_log"
        )
        
        last_sync_info = recent_syncs[0] if recent_syncs else "No recent sync found"
        
        return {
            "success": True,
            "project_key": project_key,
            "project_name": project.name,
            "sync_status": {
                "backlog_items_synced": backlog_count,
                "sprints_synced": sprint_count,
                "last_sync_info": last_sync_info
            },
            "jira_connection": await jira_service.test_connection() if jira_service.client else False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sync status: {str(e)}")