"""
Main API router that includes all endpoint routers.
"""
from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, teams, projects, sprints, standup, backlog, ai, analytics

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(sprints.router, prefix="/sprints", tags=["sprints"])
api_router.include_router(standup.router, prefix="/standup", tags=["standup"])
api_router.include_router(backlog.router, prefix="/backlog", tags=["backlog"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])