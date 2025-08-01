"""
Project management endpoints.
"""
from typing import List, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db

router = APIRouter()

class ProjectResponse(BaseModel):
    id: int
    name: str
    key: str
    description: str
    status: str
    jira_project_key: str

@router.get("/")
async def get_projects(db: Session = Depends(get_db)) -> List[ProjectResponse]:
    """Get all projects."""
    return [
        ProjectResponse(
            id=1,
            name="E-commerce Platform",
            key="ECOM",
            description="Main e-commerce platform development",
            status="active",
            jira_project_key="ECOM"
        )
    ]

@router.get("/{project_id}")
async def get_project(project_id: int, db: Session = Depends(get_db)) -> ProjectResponse:
    """Get project by ID."""
    return ProjectResponse(
        id=project_id,
        name="E-commerce Platform",
        key="ECOM", 
        description="Main e-commerce platform development",
        status="active",
        jira_project_key="ECOM"
    )