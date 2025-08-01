"""
Enhanced sprint management endpoints with AI planning features.
"""
from typing import List, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.services.ai_service import ai_service

router = APIRouter()

class SprintResponse(BaseModel):
    id: int
    name: str
    goal: str
    status: str
    start_date: str
    end_date: str
    planned_capacity: float
    actual_velocity: float
    team_capacity_days: float
    project_id: int
    team_id: int

class SprintCreate(BaseModel):
    name: str
    goal: str
    start_date: str
    end_date: str
    planned_capacity: float
    team_capacity_days: float

class VelocityResponse(BaseModel):
    average_velocity: float
    max_velocity: float
    min_velocity: float
    sprint_count: int
    recent_sprints: List[dict]

@router.get("/teams/{team_id}/sprints")
async def get_team_sprints(team_id: int, db: Session = Depends(get_db)) -> List[SprintResponse]:
    """Get sprints for a team."""
    # TODO: Implement database query
    # Return mock data for MVP
    current_date = datetime.now()
    
    return [
        {
            "id": 1,
            "name": "Sprint 15",
            "goal": "Implement payment integration and fix critical bugs",
            "status": "active",
            "start_date": (current_date - timedelta(days=7)).isoformat(),
            "end_date": (current_date + timedelta(days=7)).isoformat(),
            "planned_capacity": 40.0,
            "actual_velocity": 25.0,
            "team_capacity_days": 50.0,
            "project_id": 1,
            "team_id": team_id
        },
        {
            "id": 2,
            "name": "Sprint 14",
            "goal": "User authentication and profile management",
            "status": "completed",
            "start_date": (current_date - timedelta(days=21)).isoformat(),
            "end_date": (current_date - timedelta(days=7)).isoformat(),
            "planned_capacity": 35.0,
            "actual_velocity": 33.0,
            "team_capacity_days": 50.0,
            "project_id": 1,
            "team_id": team_id
        },
        {
            "id": 3,
            "name": "Sprint 13",
            "goal": "Database optimization and API improvements",
            "status": "completed",
            "start_date": (current_date - timedelta(days=35)).isoformat(),
            "end_date": (current_date - timedelta(days=21)).isoformat(),
            "planned_capacity": 32.0,
            "actual_velocity": 28.0,
            "team_capacity_days": 45.0,
            "project_id": 1,
            "team_id": team_id
        }
    ]

@router.get("/{sprint_id}")
async def get_sprint(sprint_id: int, db: Session = Depends(get_db)) -> SprintResponse:
    """Get sprint by ID."""
    # TODO: Implement database query
    current_date = datetime.now()
    
    return {
        "id": sprint_id,
        "name": f"Sprint {sprint_id}",
        "goal": "Sample sprint goal for development",
        "status": "active" if sprint_id == 1 else "completed",
        "start_date": (current_date - timedelta(days=7)).isoformat(),
        "end_date": (current_date + timedelta(days=7)).isoformat(),
        "planned_capacity": 40.0,
        "actual_velocity": 25.0,
        "team_capacity_days": 50.0,
        "project_id": 1,
        "team_id": 1
    }

@router.post("/teams/{team_id}/sprints")
async def create_sprint(
    team_id: int,
    sprint: SprintCreate,
    db: Session = Depends(get_db)
) -> SprintResponse:
    """Create a new sprint."""
    # TODO: Implement database insertion
    
    return {
        "id": 999,  # Mock ID
        "name": sprint.name,
        "goal": sprint.goal,
        "status": "planned",
        "start_date": sprint.start_date,
        "end_date": sprint.end_date,
        "planned_capacity": sprint.planned_capacity,
        "actual_velocity": 0.0,
        "team_capacity_days": sprint.team_capacity_days,
        "project_id": 1,  # TODO: Get from team
        "team_id": team_id
    }

@router.post("/teams/{team_id}/create-from-plan")
async def create_sprint_from_plan(
    team_id: int,
    request: dict,
    db: Session = Depends(get_db)
) -> SprintResponse:
    """Create a sprint from AI planning recommendations."""
    sprint_data = request.get("sprint")
    selected_items = request.get("selected_items", [])
    
    # TODO: Implement creating sprint and assigning items
    
    return {
        "id": 999,
        "name": sprint_data["name"],
        "goal": sprint_data["goal"],
        "status": "planned",
        "start_date": sprint_data["start_date"],
        "end_date": sprint_data["end_date"],
        "planned_capacity": sprint_data["planned_capacity"],
        "actual_velocity": 0.0,
        "team_capacity_days": sprint_data["team_capacity_days"],
        "project_id": 1,
        "team_id": team_id
    }

@router.get("/teams/{team_id}/velocity")
async def get_team_velocity(
    team_id: int,
    sprint_count: int = 5,
    db: Session = Depends(get_db)
) -> VelocityResponse:
    """Get team velocity statistics."""
    # TODO: Implement actual velocity calculation from database
    
    # Mock velocity data for MVP
    recent_sprints = [
        {"name": "Sprint 15", "points": 25, "issues": 8},
        {"name": "Sprint 14", "points": 33, "issues": 12},
        {"name": "Sprint 13", "points": 28, "issues": 10},
        {"name": "Sprint 12", "points": 30, "issues": 11},
        {"name": "Sprint 11", "points": 22, "issues": 9},
    ]
    
    velocities = [sprint["points"] for sprint in recent_sprints]
    
    return {
        "average_velocity": sum(velocities) / len(velocities),
        "max_velocity": max(velocities),
        "min_velocity": min(velocities),
        "sprint_count": len(velocities),
        "recent_sprints": recent_sprints
    }

@router.get("/{sprint_id}/burndown")
async def get_sprint_burndown(sprint_id: int, db: Session = Depends(get_db)) -> dict:
    """Get burndown chart data for a sprint."""
    # TODO: Implement actual burndown calculation
    
    # Mock burndown data
    return {
        "sprint_id": sprint_id,
        "planned_capacity": 40,
        "actual_velocity": 25,
        "days_remaining": 7,
        "ideal_burndown": [
            {"day": 0, "remaining": 40},
            {"day": 1, "remaining": 36},
            {"day": 2, "remaining": 32},
            {"day": 3, "remaining": 28},
            {"day": 4, "remaining": 24},
            {"day": 5, "remaining": 20},
            {"day": 6, "remaining": 16},
            {"day": 7, "remaining": 12},
            {"day": 8, "remaining": 8},
            {"day": 9, "remaining": 4},
            {"day": 10, "remaining": 0}
        ],
        "actual_burndown": [
            {"day": 0, "remaining": 40},
            {"day": 1, "remaining": 38},
            {"day": 2, "remaining": 35},
            {"day": 3, "remaining": 30},
            {"day": 4, "remaining": 25},
            {"day": 5, "remaining": 22},
            {"day": 6, "remaining": 18},
            {"day": 7, "remaining": 15}
        ]
    }