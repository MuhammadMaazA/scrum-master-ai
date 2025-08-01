#!/usr/bin/env python3
"""
🚀 Simple AI Scrum Master - Working Demo
A minimal working version of your AI Scrum Master!
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os

# Initialize FastAPI app
app = FastAPI(
    title="🤖 AI Scrum Master",
    description="Your intelligent agile assistant - WORKING DEMO!",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple data models
class StandupUpdate(BaseModel):
    user: str
    yesterday: str
    today: str
    blockers: Optional[str] = None

class BacklogItem(BaseModel):
    title: str
    description: str
    priority: str = "medium"

class AIResponse(BaseModel):
    message: str
    suggestions: List[str] = []

# ============================================================================
# 🎯 WORKING API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Welcome to your AI Scrum Master!"""
    return {
        "message": "🚀 Welcome to your AI Scrum Master!",
        "status": "WORKING!",
        "features": [
            "📊 Standup Summaries",
            "🎯 Backlog Analysis", 
            "🚀 Sprint Planning",
            "🤖 AI Assistance"
        ],
        "urls": {
            "docs": "http://localhost:8000/docs",
            "health": "http://localhost:8000/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "AI Scrum Master", "version": "1.0.0"}

@app.post("/api/v1/standup/summary", response_model=AIResponse)
async def generate_standup_summary(updates: List[StandupUpdate]):
    """Generate AI-powered standup summary"""
    if not updates:
        raise HTTPException(status_code=400, detail="No standup updates provided")
    
    # Mock AI analysis
    team_size = len(updates)
    total_tasks = sum(len(update.today.split(',')) for update in updates)
    blockers = [update.user for update in updates if update.blockers]
    
    summary = f"""
🎯 **Daily Standup Summary**
- **Team Size**: {team_size} members
- **Tasks Planned**: {total_tasks} items
- **Blockers**: {len(blockers)} team members need help
- **Overall Status**: {'⚠️ Attention Needed' if blockers else '✅ On Track'}
    """.strip()
    
    suggestions = [
        "Consider pair programming for blocked tasks",
        "Schedule 1:1s with team members facing blockers",
        "Review sprint capacity vs. planned work",
        "Update Jira tickets with progress"
    ]
    
    return AIResponse(message=summary, suggestions=suggestions)

@app.post("/api/v1/backlog/analyze", response_model=AIResponse)
async def analyze_backlog(items: List[BacklogItem]):
    """AI backlog analysis and recommendations"""
    if not items:
        raise HTTPException(status_code=400, detail="No backlog items provided")
    
    high_priority = len([item for item in items if item.priority == "high"])
    
    analysis = f"""
📋 **Backlog Analysis**
- **Total Items**: {len(items)}
- **High Priority**: {high_priority}
- **Recommendation**: {'Focus on high-priority items first' if high_priority > 3 else 'Well-balanced backlog'}
    """.strip()
    
    suggestions = [
        "Break down large stories into smaller tasks",
        "Add acceptance criteria to unclear items",
        "Estimate story points for planning",
        "Consider technical debt items"
    ]
    
    return AIResponse(message=analysis, suggestions=suggestions)

@app.post("/api/v1/ai/chat", response_model=AIResponse)
async def ai_assistant(message: str):
    """General AI assistant for Scrum questions"""
    
    # Mock AI responses based on keywords
    if "retrospective" in message.lower():
        response = """
🔄 **Retrospective Best Practices**
- What went well?
- What could be improved?
- Action items for next sprint
        """.strip()
        suggestions = ["Use voting for prioritization", "Time-box discussions", "Focus on actionable items"]
    
    elif "planning" in message.lower():
        response = """
📅 **Sprint Planning Tips**
- Review velocity from last sprint
- Ensure stories are properly estimated
- Consider team capacity and holidays
        """.strip()
        suggestions = ["Include the whole team", "Break down large stories", "Plan for ~80% capacity"]
    
    else:
        response = "I'm your AI Scrum Master assistant. Ask me about standups, planning, retrospectives, or agile best practices!"
        suggestions = ["Try asking about sprint planning", "Ask about retrospective formats", "Need help with backlog grooming?"]
    
    return AIResponse(message=response, suggestions=suggestions)

# ============================================================================
# 🚀 START THE SERVER
# ============================================================================

if __name__ == "__main__":
    print("🚀 Starting AI Scrum Master...")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health")
    print("✨ Frontend will run on: http://localhost:3000")
    
    uvicorn.run(
        "simple_ai_scrum:app", 
        host="127.0.0.1", 
        port=8000, 
        reload=True,
        log_level="info"
    )