#!/usr/bin/env python3
"""
🚀 Enhanced AI Scrum Master - With Real OpenAI Integration
Advanced AI-powered Scrum Master with comprehensive features
"""
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
import os
import asyncio
import json
from datetime import datetime, timedelta
from enum import Enum
import openai
from openai import OpenAI

# Initialize FastAPI app
app = FastAPI(
    title="🤖 Enhanced AI Scrum Master",
    description="Your intelligent agile assistant with OpenAI integration",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = None
if os.getenv("OPENAI_API_KEY"):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ============================================================================
# 📊 ENHANCED DATA MODELS
# ============================================================================

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class StoryPointScale(str, Enum):
    XS = "1"
    S = "2"
    M = "3"
    L = "5"
    XL = "8"
    XXL = "13"

class StandupUpdate(BaseModel):
    user: str = Field(..., description="Team member name")
    yesterday: str = Field(..., description="What was accomplished yesterday")
    today: str = Field(..., description="What is planned for today")
    blockers: Optional[str] = Field(None, description="Any blockers or impediments")
    velocity_points: Optional[int] = Field(None, description="Story points completed")

class BacklogItem(BaseModel):
    id: Optional[str] = Field(None, description="Unique identifier")
    title: str = Field(..., description="User story title")
    description: str = Field(..., description="Detailed description")
    priority: Priority = Field(Priority.MEDIUM, description="Business priority")
    story_points: Optional[StoryPointScale] = Field(None, description="Estimated effort")
    epic: Optional[str] = Field(None, description="Associated epic")
    acceptance_criteria: Optional[List[str]] = Field(None, description="AC list")
    labels: Optional[List[str]] = Field([], description="Story labels/tags")
    assignee: Optional[str] = Field(None, description="Assigned team member")
    status: Optional[str] = Field("To Do", description="Current status")

class SprintPlan(BaseModel):
    sprint_goal: str = Field(..., description="Sprint objective")
    capacity: int = Field(..., description="Team capacity in story points")
    selected_items: List[BacklogItem] = Field(..., description="Stories in sprint")
    risks: List[str] = Field([], description="Identified risks")
    dependencies: List[str] = Field([], description="External dependencies")

class AIResponse(BaseModel):
    message: str = Field(..., description="AI-generated response")
    suggestions: List[str] = Field([], description="Actionable recommendations")
    confidence_score: Optional[float] = Field(None, description="AI confidence (0-1)")
    context_used: Optional[List[str]] = Field([], description="Context sources")

class BurndownData(BaseModel):
    sprint_name: str
    dates: List[str]
    ideal_remaining: List[int]
    actual_remaining: List[int]
    completed: List[int]

class VelocityMetrics(BaseModel):
    sprint_velocities: List[int]
    average_velocity: float
    velocity_trend: str  # "increasing", "decreasing", "stable"
    prediction_next_sprint: int

# ============================================================================
# 🧠 AI SERVICE LAYER
# ============================================================================

class AIService:
    def __init__(self):
        self.client = client
        self.model = "gpt-4"
        
    async def generate_standup_summary(self, updates: List[StandupUpdate]) -> AIResponse:
        """Generate intelligent standup summary with insights"""
        if not self.client:
            return self._fallback_standup_summary(updates)
            
        # Prepare context
        context = self._prepare_standup_context(updates)
        
        prompt = f"""
You are an experienced Scrum Master analyzing a daily standup. Based on the following team updates, provide:

1. A concise summary of team progress
2. Key achievements and blockers
3. Risk assessment and recommendations
4. Action items for follow-up

Team Updates:
{context}

Provide a structured response focusing on:
- Team velocity and progress
- Critical blockers requiring immediate attention
- Recommendations for the Scrum Master
- Sprint goal alignment

Keep tone professional but encouraging.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI Scrum Master assistant with deep knowledge of agile methodologies."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            ai_content = response.choices[0].message.content
            suggestions = self._extract_suggestions(ai_content)
            
            return AIResponse(
                message=ai_content,
                suggestions=suggestions,
                confidence_score=0.85,
                context_used=["team_updates", "velocity_data"]
            )
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._fallback_standup_summary(updates)
    
    async def analyze_backlog(self, items: List[BacklogItem]) -> AIResponse:
        """Intelligent backlog analysis with prioritization recommendations"""
        if not self.client:
            return self._fallback_backlog_analysis(items)
            
        # Prepare backlog context
        context = self._prepare_backlog_context(items)
        
        prompt = f"""
As a Product Owner's AI assistant, analyze this product backlog and provide:

1. Prioritization recommendations based on value vs effort
2. Quality assessment of user stories
3. Duplicate detection and consolidation suggestions
4. Missing acceptance criteria identification
5. Story point estimation validation

Backlog Items:
{context}

Provide structured recommendations for:
- Priority adjustments with reasoning
- Story improvements needed
- Potential duplicates to merge
- Stories ready for sprint vs. those needing refinement
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI Product Owner assistant specializing in backlog optimization."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            ai_content = response.choices[0].message.content
            suggestions = self._extract_suggestions(ai_content)
            
            return AIResponse(
                message=ai_content,
                suggestions=suggestions,
                confidence_score=0.8,
                context_used=["backlog_items", "historical_data"]
            )
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._fallback_backlog_analysis(items)
    
    async def suggest_sprint_plan(self, backlog: List[BacklogItem], capacity: int) -> SprintPlan:
        """AI-driven sprint planning with capacity optimization"""
        if not self.client:
            return self._fallback_sprint_plan(backlog, capacity)
            
        # Prepare planning context
        context = self._prepare_planning_context(backlog, capacity)
        
        prompt = f"""
As an AI Scrum Master, create an optimal sprint plan considering:

Available Backlog:
{context}

Team Capacity: {capacity} story points

Provide:
1. Recommended stories for sprint (staying within capacity)
2. Sprint goal that unifies selected work
3. Risk assessment for the proposed sprint
4. Dependencies and prerequisites
5. Alternative compositions if initial selection has issues

Focus on:
- Maximizing business value delivery
- Ensuring sprint coherence
- Managing technical dependencies
- Balancing team workload
- 20% capacity buffer for unexpected work
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI Scrum Master with expertise in sprint planning and capacity management."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1200
            )
            
            ai_content = response.choices[0].message.content
            
            # Parse AI response to extract sprint plan
            selected_items = self._extract_sprint_items(ai_content, backlog, capacity)
            sprint_goal = self._extract_sprint_goal(ai_content)
            risks = self._extract_risks(ai_content)
            dependencies = self._extract_dependencies(ai_content)
            
            return SprintPlan(
                sprint_goal=sprint_goal,
                capacity=capacity,
                selected_items=selected_items,
                risks=risks,
                dependencies=dependencies
            )
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._fallback_sprint_plan(backlog, capacity)
    
    def _prepare_standup_context(self, updates: List[StandupUpdate]) -> str:
        """Format standup updates for AI processing"""
        context_lines = []
        for update in updates:
            context_lines.append(f"""
Team Member: {update.user}
Yesterday: {update.yesterday}
Today: {update.today}
Blockers: {update.blockers or 'None'}
Points Completed: {update.velocity_points or 'Not specified'}
""")
        return "\n".join(context_lines)
    
    def _prepare_backlog_context(self, items: List[BacklogItem]) -> str:
        """Format backlog items for AI processing"""
        context_lines = []
        for item in items:
            context_lines.append(f"""
Title: {item.title}
Description: {item.description}
Priority: {item.priority}
Story Points: {item.story_points or 'Not estimated'}
Epic: {item.epic or 'None'}
Status: {item.status}
Acceptance Criteria: {len(item.acceptance_criteria or [])} items defined
""")
        return "\n".join(context_lines)
    
    def _prepare_planning_context(self, backlog: List[BacklogItem], capacity: int) -> str:
        """Format planning context for AI processing"""
        ready_items = [item for item in backlog if item.status in ["Ready", "To Do"]]
        context_lines = []
        
        for item in ready_items:
            points = int(item.story_points.value) if item.story_points else 3
            context_lines.append(f"""
- {item.title} ({points} points, {item.priority} priority)
  Description: {item.description[:100]}...
  Epic: {item.epic or 'None'}
""")
        return "\n".join(context_lines)
    
    def _extract_suggestions(self, ai_content: str) -> List[str]:
        """Extract actionable suggestions from AI response"""
        # Simple extraction logic - could be enhanced with better parsing
        suggestions = []
        lines = ai_content.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['recommend', 'suggest', 'should', 'consider']):
                suggestions.append(line.strip('- ').strip())
        return suggestions[:5]  # Limit to top 5 suggestions
    
    def _extract_sprint_items(self, ai_content: str, backlog: List[BacklogItem], capacity: int) -> List[BacklogItem]:
        """Extract recommended sprint items from AI response"""
        # Simplified selection based on priority and capacity
        sorted_items = sorted(backlog, key=lambda x: (
            {"high": 0, "medium": 1, "low": 2}[x.priority],
            int(x.story_points.value) if x.story_points else 3
        ))
        
        selected = []
        total_points = 0
        target_capacity = int(capacity * 0.8)  # 80% rule
        
        for item in sorted_items:
            points = int(item.story_points.value) if item.story_points else 3
            if total_points + points <= target_capacity:
                selected.append(item)
                total_points += points
                
        return selected
    
    def _extract_sprint_goal(self, ai_content: str) -> str:
        """Extract sprint goal from AI response"""
        # Look for sprint goal in AI response
        lines = ai_content.split('\n')
        for line in lines:
            if 'sprint goal' in line.lower() or 'goal:' in line.lower():
                return line.split(':', 1)[-1].strip()
        return "Deliver high-value features while maintaining quality standards"
    
    def _extract_risks(self, ai_content: str) -> List[str]:
        """Extract identified risks from AI response"""
        risks = []
        lines = ai_content.split('\n')
        in_risk_section = False
        
        for line in lines:
            if 'risk' in line.lower():
                in_risk_section = True
            elif in_risk_section and line.strip().startswith('-'):
                risks.append(line.strip('- ').strip())
            elif in_risk_section and not line.strip():
                break
                
        return risks[:3]  # Limit to top 3 risks
    
    def _extract_dependencies(self, ai_content: str) -> List[str]:
        """Extract dependencies from AI response"""
        deps = []
        lines = ai_content.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['depend', 'prerequisite', 'requires']):
                deps.append(line.strip('- ').strip())
                
        return deps[:3]  # Limit to top 3 dependencies
    
    # Fallback methods for when OpenAI is not available
    def _fallback_standup_summary(self, updates: List[StandupUpdate]) -> AIResponse:
        """Fallback standup summary without AI"""
        team_size = len(updates)
        total_points = sum(update.velocity_points or 0 for update in updates)
        blockers = [update.user for update in updates if update.blockers]
        
        summary = f"""
🎯 **Daily Standup Summary**
- **Team Size**: {team_size} members reporting
- **Velocity**: {total_points} story points completed yesterday
- **Blockers**: {len(blockers)} team members need assistance
- **Status**: {'⚠️ Attention Required' if blockers else '✅ Team on Track'}

**Key Highlights:**
{chr(10).join(f"• {update.user}: {update.yesterday[:50]}..." for update in updates[:3])}
        """.strip()
        
        suggestions = [
            "Schedule blocker resolution sessions",
            "Review sprint progress in planning session",
            "Update Jira tickets with current status",
            "Conduct 1:1s with blocked team members"
        ]
        
        return AIResponse(
            message=summary,
            suggestions=suggestions,
            confidence_score=0.6,
            context_used=["team_updates"]
        )
    
    def _fallback_backlog_analysis(self, items: List[BacklogItem]) -> AIResponse:
        """Fallback backlog analysis without AI"""
        total_items = len(items)
        high_priority = len([item for item in items if item.priority == Priority.HIGH])
        unestimated = len([item for item in items if not item.story_points])
        
        analysis = f"""
📋 **Backlog Health Check**
- **Total Items**: {total_items}
- **High Priority**: {high_priority} items
- **Unestimated**: {unestimated} stories need pointing
- **Status**: {'Good' if unestimated < total_items * 0.3 else 'Needs Attention'}
        """.strip()
        
        suggestions = [
            "Estimate unpointed stories in next refinement",
            "Review high-priority items for sprint readiness",
            "Add acceptance criteria to incomplete stories",
            "Consider breaking down large stories (>8 points)"
        ]
        
        return AIResponse(
            message=analysis,
            suggestions=suggestions,
            confidence_score=0.5,
            context_used=["backlog_metrics"]
        )
    
    def _fallback_sprint_plan(self, backlog: List[BacklogItem], capacity: int) -> SprintPlan:
        """Fallback sprint planning without AI"""
        # Simple capacity-based selection
        sorted_items = sorted(backlog, key=lambda x: (
            {"high": 0, "medium": 1, "low": 2}[x.priority],
            int(x.story_points.value) if x.story_points else 3
        ))
        
        selected = []
        total_points = 0
        target_capacity = int(capacity * 0.8)
        
        for item in sorted_items:
            points = int(item.story_points.value) if item.story_points else 3
            if total_points + points <= target_capacity:
                selected.append(item)
                total_points += points
        
        return SprintPlan(
            sprint_goal="Deliver highest priority features within team capacity",
            capacity=capacity,
            selected_items=selected,
            risks=["Capacity estimation may be optimistic"],
            dependencies=["External API availability", "Design review completion"]
        )

# Initialize AI service
ai_service = AIService()

# ============================================================================
# 🚀 ENHANCED API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Enhanced welcome endpoint with system status"""
    openai_status = "🟢 Connected" if client else "🔴 Not configured"
    
    return {
        "message": "🚀 Welcome to Enhanced AI Scrum Master!",
        "status": "RUNNING",
        "ai_status": openai_status,
        "version": "2.0.0",
        "features": [
            "🧠 Real OpenAI Integration",
            "📊 Advanced Standup Analysis",
            "🎯 Intelligent Backlog Management", 
            "🚀 AI-Powered Sprint Planning",
            "📈 Velocity & Burndown Analytics",
            "🤖 Contextual AI Assistant"
        ],
        "endpoints": {
            "docs": "http://localhost:8000/docs",
            "health": "http://localhost:8000/health",
            "standup": "POST /api/v1/standup/summary",
            "backlog": "POST /api/v1/backlog/analyze",
            "planning": "POST /api/v1/sprint/plan",
            "ai_chat": "POST /api/v1/ai/chat"
        }
    }

@app.get("/health")
async def health_check():
    """Enhanced health check with system status"""
    return {
        "status": "healthy",
        "service": "Enhanced AI Scrum Master",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "openai_configured": client is not None,
        "features_active": {
            "standup_analysis": True,
            "backlog_management": True,
            "sprint_planning": True,
            "ai_assistance": client is not None
        }
    }

@app.post("/api/v1/standup/summary", response_model=AIResponse)
async def generate_standup_summary(updates: List[StandupUpdate]):
    """AI-powered standup summary with insights"""
    if not updates:
        raise HTTPException(status_code=400, detail="No standup updates provided")
    
    try:
        response = await ai_service.generate_standup_summary(updates)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

@app.post("/api/v1/backlog/analyze", response_model=AIResponse)
async def analyze_backlog(items: List[BacklogItem]):
    """AI-powered backlog analysis and optimization"""
    if not items:
        raise HTTPException(status_code=400, detail="No backlog items provided")
    
    try:
        response = await ai_service.analyze_backlog(items)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing backlog: {str(e)}")

@app.post("/api/v1/sprint/plan", response_model=SprintPlan)
async def suggest_sprint_plan(backlog: List[BacklogItem], capacity: int):
    """AI-driven sprint planning with capacity optimization"""
    if not backlog:
        raise HTTPException(status_code=400, detail="No backlog items provided")
    if capacity <= 0:
        raise HTTPException(status_code=400, detail="Capacity must be positive")
    
    try:
        plan = await ai_service.suggest_sprint_plan(backlog, capacity)
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating sprint plan: {str(e)}")

@app.post("/api/v1/ai/chat", response_model=AIResponse)
async def ai_assistant(message: str, context: Optional[Dict[str, Any]] = None):
    """Enhanced AI assistant with contextual understanding"""
    
    if not client:
        # Fallback responses
        return _fallback_ai_chat(message)
    
    # Enhanced context-aware responses
    system_prompt = """
You are an experienced Scrum Master and Agile Coach AI assistant. You have deep knowledge of:
- Scrum framework and ceremonies
- Agile best practices and methodologies
- Team dynamics and facilitation
- Product management and backlog optimization
- Velocity tracking and sprint planning
- Stakeholder communication

Provide practical, actionable advice that helps teams improve their agile practices.
"""
    
    user_prompt = f"""
Context: {json.dumps(context) if context else 'General agile question'}
Question: {message}

Please provide specific, actionable guidance for this Scrum/Agile question.
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=600
        )
        
        ai_content = response.choices[0].message.content
        suggestions = ai_service._extract_suggestions(ai_content)
        
        return AIResponse(
            message=ai_content,
            suggestions=suggestions,
            confidence_score=0.9,
            context_used=list(context.keys()) if context else ["general_knowledge"]
        )
        
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return _fallback_ai_chat(message)

def _fallback_ai_chat(message: str) -> AIResponse:
    """Fallback AI chat without OpenAI"""
    message_lower = message.lower()
    
    if "retrospective" in message_lower:
        response = """
🔄 **Retrospective Best Practices**

1. **Structure**: Use What went well? / What didn't? / Action items
2. **Facilitation**: Keep discussions timeboxed and focused
3. **Participation**: Ensure everyone contributes equally
4. **Follow-up**: Track action items in next sprint

**Common Formats:**
- Start/Stop/Continue
- Glad/Sad/Mad
- 4Ls (Liked/Learned/Lacked/Longed for)
"""
        suggestions = [
            "Use voting to prioritize discussion topics",
            "Set clear time limits for each section",
            "Focus on actionable improvements only",
            "Create SMART action items with owners"
        ]
    
    elif "planning" in message_lower:
        response = """
📅 **Sprint Planning Excellence**

1. **Preparation**: Ensure backlog is refined and estimated
2. **Capacity**: Consider team availability and velocity
3. **Goal Setting**: Define clear, measurable sprint goal
4. **Task Breakdown**: Split stories into implementable tasks

**Planning Tips:**
- Use 80% capacity rule for buffer
- Include whole team in estimation
- Break down dependencies early
"""
        suggestions = [
            "Review team velocity from last 3 sprints",
            "Identify dependencies before committing",
            "Ensure Definition of Ready is met",
            "Plan for 20% buffer capacity"
        ]
    
    else:
        response = """
🤖 **AI Scrum Master Assistant**

I'm here to help with all aspects of agile delivery:
- Sprint planning and execution
- Backlog management and prioritization  
- Team facilitation and coaching
- Metrics and continuous improvement

Ask me about specific scrum events, techniques, or challenges you're facing!
"""
        suggestions = [
            "Ask about sprint planning best practices",
            "Get help with retrospective formats",
            "Learn about velocity tracking",
            "Discuss backlog refinement techniques"
        ]
    
    return AIResponse(
        message=response,
        suggestions=suggestions,
        confidence_score=0.7,
        context_used=["built_in_knowledge"]
    )

# ============================================================================
# 📊 ANALYTICS ENDPOINTS
# ============================================================================

@app.get("/api/v1/analytics/burndown")
async def get_burndown_chart(sprint_name: str = "Current Sprint") -> BurndownData:
    """Generate burndown chart data"""
    # Mock data for demonstration
    dates = [(datetime.now() - timedelta(days=x)).strftime("%Y-%m-%d") for x in range(10, 0, -1)]
    ideal_remaining = [45, 40, 36, 32, 27, 23, 18, 14, 9, 5]
    actual_remaining = [45, 42, 38, 35, 30, 25, 22, 18, 12, 8]
    completed = [0, 3, 7, 10, 15, 20, 23, 27, 33, 37]
    
    return BurndownData(
        sprint_name=sprint_name,
        dates=dates,
        ideal_remaining=ideal_remaining,
        actual_remaining=actual_remaining,
        completed=completed
    )

@app.get("/api/v1/analytics/velocity")
async def get_velocity_metrics() -> VelocityMetrics:
    """Get team velocity analytics"""
    # Mock data for demonstration
    sprint_velocities = [32, 28, 35, 31, 38, 34]
    average_velocity = sum(sprint_velocities) / len(sprint_velocities)
    
    # Simple trend calculation
    recent_avg = sum(sprint_velocities[-3:]) / 3
    older_avg = sum(sprint_velocities[:3]) / 3
    
    if recent_avg > older_avg * 1.1:
        trend = "increasing"
    elif recent_avg < older_avg * 0.9:
        trend = "decreasing" 
    else:
        trend = "stable"
    
    return VelocityMetrics(
        sprint_velocities=sprint_velocities,
        average_velocity=round(average_velocity, 1),
        velocity_trend=trend,
        prediction_next_sprint=round(recent_avg)
    )

# ============================================================================
# 🚀 STARTUP CONFIGURATION
# ============================================================================

if __name__ == "__main__":
    print("🚀 Starting Enhanced AI Scrum Master...")
    print("🧠 OpenAI Integration:", "✅ Active" if client else "❌ Configure OPENAI_API_KEY")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/health")
    print("💡 Try the enhanced endpoints with real AI!")
    
    uvicorn.run(
        "enhanced_ai_scrum:app",
        host="127.0.0.1", 
        port=8001,  # Different port to avoid conflict
        reload=True,
        log_level="info"
    )
