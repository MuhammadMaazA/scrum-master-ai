"""
Main API router that includes all endpoint routers.
"""
from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, teams, projects, sprints, standup, backlog, ai, analytics, jira_sync, agents, security, monitoring

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
api_router.include_router(jira_sync.router, prefix="/jira", tags=["jira-sync"])
api_router.include_router(agents.router, prefix="/agents", tags=["ai-agents"])
api_router.include_router(security.router, prefix="/security", tags=["security"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])