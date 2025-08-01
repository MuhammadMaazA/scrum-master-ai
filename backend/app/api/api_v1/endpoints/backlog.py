"""
Enhanced backlog management endpoints with AI features.
"""
from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.services.ai_service import ai_service
from app.services.vector_service import vector_service

router = APIRouter()

class BacklogItemResponse(BaseModel):
    id: int
    title: str
    description: str
    acceptance_criteria: Optional[str] = None
    item_type: str
    priority: str
    status: str
    story_points: Optional[int] = None
    jira_key: Optional[str] = None
    
    # AI analysis fields
    ai_suggested_points: Optional[int] = None
    ai_complexity_score: Optional[float] = None
    ai_clarity_score: Optional[float] = None
    ai_suggestions: Optional[str] = None
    duplicate_candidates: Optional[List[int]] = None
    
    # Business fields
    business_value: Optional[int] = None
    effort_estimate: Optional[str] = None
    value_effort_ratio: Optional[float] = None
    
    project_id: int
    sprint_id: Optional[int] = None
    assignee_id: Optional[int] = None
    created_by_id: int
    created_at: str
    updated_at: str

class BacklogItemCreate(BaseModel):
    title: str
    description: str
    acceptance_criteria: Optional[str] = None
    item_type: str = "story"
    priority: str = "medium"
    story_points: Optional[int] = None
    business_value: Optional[int] = None
    assignee_id: Optional[int] = None

class BacklogItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    item_type: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    story_points: Optional[int] = None
    business_value: Optional[int] = None
    assignee_id: Optional[int] = None

@router.get("/projects/{project_id}/items")
async def get_project_backlog(
    project_id: int,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    item_type: Optional[str] = None,
    assignee_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
) -> List[BacklogItemResponse]:
    """Get backlog items for a project with filtering."""
    # TODO: Implement database query with filters
    # For MVP, return mock data that matches the expected structure
    
    mock_items = [
        {
            "id": 1,
            "title": "Implement user authentication",
            "description": "Add OAuth2 authentication for users to securely log into the system",
            "acceptance_criteria": "- Users can sign up with email\n- Users can log in with email/password\n- JWT tokens are issued",
            "item_type": "story",
            "priority": "high",
            "status": "todo",
            "story_points": 8,
            "jira_key": "ECOM-101",
            "ai_suggested_points": 8,
            "ai_complexity_score": 0.7,
            "ai_clarity_score": 0.9,
            "ai_suggestions": '{"improvements": ["Add error handling details", "Specify token expiration"]}',
            "duplicate_candidates": [],
            "business_value": 85,
            "effort_estimate": "L",
            "value_effort_ratio": 10.6,
            "project_id": project_id,
            "sprint_id": None,
            "assignee_id": None,
            "created_by_id": 1,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        },
        {
            "id": 2,
            "title": "Fix payment processing bug",
            "description": "Payment fails when amount is over $1000",
            "acceptance_criteria": None,
            "item_type": "bug",
            "priority": "critical",
            "status": "todo",
            "story_points": 5,
            "jira_key": "ECOM-102",
            "ai_suggested_points": 3,
            "ai_complexity_score": 0.4,
            "ai_clarity_score": 0.6,
            "ai_suggestions": '{"improvements": ["Add steps to reproduce", "Include error messages", "Specify affected payment methods"]}',
            "duplicate_candidates": [],
            "business_value": 95,
            "effort_estimate": "M",
            "value_effort_ratio": 19.0,
            "project_id": project_id,
            "sprint_id": None,
            "assignee_id": 2,
            "created_by_id": 1,
            "created_at": "2024-01-02T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z"
        },
        {
            "id": 3,
            "title": "Add shopping cart",
            "description": "Users need shopping cart",
            "acceptance_criteria": None,
            "item_type": "story",
            "priority": "medium",
            "status": "todo",
            "story_points": None,
            "jira_key": "ECOM-103",
            "ai_suggested_points": 13,
            "ai_complexity_score": 0.8,
            "ai_clarity_score": 0.3,
            "ai_suggestions": '{"improvements": ["Break down into smaller stories", "Add detailed acceptance criteria", "Specify cart persistence requirements"]}',
            "duplicate_candidates": [4],
            "business_value": 70,
            "effort_estimate": "XL",
            "value_effort_ratio": None,
            "project_id": project_id,
            "sprint_id": None,
            "assignee_id": None,
            "created_by_id": 1,
            "created_at": "2024-01-03T00:00:00Z",
            "updated_at": "2024-01-03T00:00:00Z"
        },
        {
            "id": 4,
            "title": "Implement cart functionality",
            "description": "Build cart for user purchases",
            "acceptance_criteria": None,
            "item_type": "story",
            "priority": "medium",
            "status": "todo",
            "story_points": None,
            "jira_key": "ECOM-104",
            "ai_suggested_points": 13,
            "ai_complexity_score": 0.8,
            "ai_clarity_score": 0.4,
            "ai_suggestions": '{"improvements": ["Very similar to ECOM-103", "Consider merging or clarifying differences"]}',
            "duplicate_candidates": [3],
            "business_value": 70,
            "effort_estimate": "XL",
            "value_effort_ratio": None,
            "project_id": project_id,
            "sprint_id": None,
            "assignee_id": None,
            "created_by_id": 1,
            "created_at": "2024-01-04T00:00:00Z",
            "updated_at": "2024-01-04T00:00:00Z"
        }
    ]
    
    # Apply filters
    filtered_items = mock_items
    
    if status:
        filtered_items = [item for item in filtered_items if item["status"] == status]
    if priority:
        filtered_items = [item for item in filtered_items if item["priority"] == priority]
    if item_type:
        filtered_items = [item for item in filtered_items if item["item_type"] == item_type]
    if assignee_id:
        filtered_items = [item for item in filtered_items if item["assignee_id"] == assignee_id]
    if search:
        search_lower = search.lower()
        filtered_items = [
            item for item in filtered_items 
            if search_lower in item["title"].lower() or search_lower in item["description"].lower()
        ]
    
    return filtered_items

@router.get("/items/{item_id}")
async def get_backlog_item(item_id: int, db: Session = Depends(get_db)) -> BacklogItemResponse:
    """Get backlog item by ID."""
    # TODO: Implement database query
    return {
        "id": item_id,
        "title": "Sample Item",
        "description": "Sample description",
        "item_type": "story",
        "priority": "medium",
        "status": "todo",
        "story_points": 5,
        "jira_key": f"ITEM-{item_id}",
        "project_id": 1,
        "created_by_id": 1,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }

@router.post("/projects/{project_id}/items")
async def create_backlog_item(
    project_id: int,
    item: BacklogItemCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> BacklogItemResponse:
    """Create a new backlog item."""
    # TODO: Implement database insertion
    
    # Simulate AI analysis for new items
    if item.description:
        background_tasks.add_task(
            _analyze_item_async,
            item.title,
            item.description,
            item.item_type
        )
    
    # Return mock created item
    return {
        "id": 999,  # Mock ID
        "title": item.title,
        "description": item.description,
        "acceptance_criteria": item.acceptance_criteria,
        "item_type": item.item_type,
        "priority": item.priority,
        "status": "todo",
        "story_points": item.story_points,
        "business_value": item.business_value,
        "project_id": project_id,
        "assignee_id": item.assignee_id,
        "created_by_id": 1,  # TODO: Get from auth
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }

@router.put("/items/{item_id}")
async def update_backlog_item(
    item_id: int,
    item: BacklogItemUpdate,
    db: Session = Depends(get_db)
) -> BacklogItemResponse:
    """Update a backlog item."""
    # TODO: Implement database update
    return {
        "id": item_id,
        "title": item.title or "Updated Item",
        "description": item.description or "Updated description",
        "item_type": item.item_type or "story",
        "priority": item.priority or "medium",
        "status": item.status or "todo",
        "story_points": item.story_points,
        "business_value": item.business_value,
        "project_id": 1,
        "created_by_id": 1,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }

@router.delete("/items/{item_id}")
async def delete_backlog_item(item_id: int, db: Session = Depends(get_db)):
    """Delete a backlog item."""
    # TODO: Implement database deletion
    return {"message": f"Item {item_id} deleted successfully"}

@router.post("/projects/{project_id}/bulk-analyze")
async def bulk_analyze_backlog(
    project_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Any:
    """Run AI analysis on all backlog items in a project."""
    
    # Start background task for bulk analysis
    background_tasks.add_task(_bulk_analyze_project, project_id)
    
    return {
        "message": "Bulk analysis started",
        "project_id": project_id,
        "status": "processing"
    }

@router.post("/items/{item_id}/apply-suggestions")
async def apply_ai_suggestions(
    item_id: int,
    suggestions: dict,
    db: Session = Depends(get_db)
) -> BacklogItemResponse:
    """Apply AI suggestions to a backlog item."""
    # TODO: Implement applying AI suggestions to the item
    
    return {
        "id": item_id,
        "title": suggestions.get("title", "Updated by AI"),
        "description": suggestions.get("description", "Updated by AI"),
        "acceptance_criteria": suggestions.get("acceptance_criteria"),
        "item_type": "story",
        "priority": "medium",
        "status": "todo",
        "story_points": suggestions.get("story_points"),
        "project_id": 1,
        "created_by_id": 1,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }

# Background task functions
async def _analyze_item_async(title: str, description: str, item_type: str):
    """Analyze a single item in the background."""
    try:
        analysis = await ai_service.analyze_backlog_item({
            "title": title,
            "description": description,
            "item_type": item_type
        })
        
        # Store insights in vector database
        insights = f"Backlog analysis: {title} - Clarity: {analysis.clarity_score}, Complexity: {analysis.estimated_complexity}"
        await vector_service.store_backlog_insights(
            insights=insights,
            project_id=1,  # TODO: Get actual project ID
            item_id=999,   # TODO: Get actual item ID
        )
        
        print(f"Analyzed item: {title}")
    except Exception as e:
        print(f"Failed to analyze item {title}: {e}")

async def _bulk_analyze_project(project_id: int):
    """Analyze all items in a project in the background."""
    try:
        # TODO: Get all items from database
        # For now, simulate bulk analysis
        print(f"Starting bulk analysis for project {project_id}")
        
        # Simulate processing time
        import asyncio
        await asyncio.sleep(5)
        
        print(f"Completed bulk analysis for project {project_id}")
    except Exception as e:
        print(f"Failed bulk analysis for project {project_id}: {e}")