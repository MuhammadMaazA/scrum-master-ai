"""
AI service for LLM interactions and intelligent analysis.
This service handles all AI-powered features like standup summaries,
backlog analysis, and sprint planning assistance.
"""
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta

from langchain_openai import OpenAI, ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import PydanticOutputParser
from langchain.output_parsers import OutputFixingParser
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.vector_service import VectorService

logger = logging.getLogger(__name__)

class StandupSummary(BaseModel):
    """Structured output for standup summaries."""
    summary: str = Field(description="Overall summary of the standup")
    key_achievements: List[str] = Field(description="Key achievements from yesterday")
    today_focus: List[str] = Field(description="Main focus areas for today")
    blockers: List[Dict[str, str]] = Field(description="Active blockers with descriptions")
    action_items: List[Dict[str, str]] = Field(description="Follow-up action items")
    team_sentiment: str = Field(description="Overall team sentiment: positive, neutral, concerned")

class BacklogAnalysis(BaseModel):
    """Structured output for backlog item analysis."""
    clarity_score: float = Field(description="Clarity score from 0.0 to 1.0")
    suggested_improvements: List[str] = Field(description="Suggested improvements")
    estimated_complexity: str = Field(description="Complexity estimate: XS, S, M, L, XL")
    potential_risks: List[str] = Field(description="Potential risks or blockers")
    acceptance_criteria_suggestions: List[str] = Field(description="Suggested acceptance criteria")

class SprintPlanSuggestion(BaseModel):
    """Structured output for sprint planning suggestions."""
    recommended_items: List[int] = Field(description="Recommended backlog item IDs")
    total_story_points: int = Field(description="Total story points of recommended items")
    sprint_goal: str = Field(description="Suggested sprint goal")
    risks: List[str] = Field(description="Identified risks or concerns")
    capacity_utilization: float = Field(description="Percentage of capacity utilized")

class AIService:
    """
    AI service for intelligent Scrum Master assistance.
    Handles all LLM interactions and structured output parsing.
    """
    
    def __init__(self):
        # Only initialize OpenAI if API key is provided
        if settings.OPENAI_API_KEY:
            self.chat_model = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS,
                openai_api_key=settings.OPENAI_API_KEY
            )
        else:
            self.chat_model = None
            logger.warning("OpenAI API key not provided. AI features will be disabled.")
        
        self.vector_service = VectorService()
        
        # Output parsers for structured responses
        self.standup_parser = PydanticOutputParser(pydantic_object=StandupSummary)
        self.backlog_parser = PydanticOutputParser(pydantic_object=BacklogAnalysis)
        self.sprint_parser = PydanticOutputParser(pydantic_object=SprintPlanSuggestion)
        
        # Add fixing parsers to handle malformed outputs (only if chat model is available)
        if self.chat_model:
            self.standup_parser = OutputFixingParser.from_llm(
                parser=self.standup_parser, llm=self.chat_model
            )
            self.backlog_parser = OutputFixingParser.from_llm(
                parser=self.backlog_parser, llm=self.chat_model
            )
            self.sprint_parser = OutputFixingParser.from_llm(
                parser=self.sprint_parser, llm=self.chat_model
            )

    async def generate_standup_summary(
        self, 
        standup_entries: List[Dict[str, Any]], 
        team_context: Dict[str, Any],
        jira_updates: Optional[List[Dict[str, Any]]] = None
    ) -> StandupSummary:
        """
        Generate an AI-powered standup summary from team entries and Jira data.
        
        Args:
            standup_entries: List of individual standup entries
            team_context: Team information and preferences
            jira_updates: Optional Jira ticket updates from yesterday
            
        Returns:
            Structured standup summary
        """
        try:
            # Get relevant context from vector store
            context = await self.vector_service.get_relevant_context(
                f"standup team {team_context.get('name', '')} blockers progress",
                limit=3
            )
            
            # Build the prompt
            system_prompt = self._get_standup_system_prompt(team_context)
            human_prompt = self._build_standup_human_prompt(
                standup_entries, jira_updates, context
            )
            
            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", human_prompt)
            ])
            
            # Format the prompt
            formatted_prompt = prompt.format_prompt(
                format_instructions=self.standup_parser.get_format_instructions()
            )
            
            # Generate response
            response = await self.chat_model.agenerate([formatted_prompt.to_messages()])
            output = response.generations[0][0].text
            
            # Parse structured output
            parsed_summary = self.standup_parser.parse(output)
            
            logger.info(f"Generated standup summary for team {team_context.get('name')}")
            return parsed_summary
            
        except Exception as e:
            logger.error(f"Failed to generate standup summary: {e}")
            # Return fallback summary
            return StandupSummary(
                summary="Failed to generate AI summary. Please review standup entries manually.",
                key_achievements=[],
                today_focus=[],
                blockers=[],
                action_items=[],
                team_sentiment="neutral"
            )

    async def analyze_backlog_item(
        self, 
        item: Dict[str, Any],
        similar_items: Optional[List[Dict[str, Any]]] = None
    ) -> BacklogAnalysis:
        """
        Analyze a backlog item for clarity, complexity, and improvements.
        
        Args:
            item: Backlog item data
            similar_items: Similar items for context
            
        Returns:
            Structured analysis of the backlog item
        """
        try:
            # Get relevant context from vector store
            context = await self.vector_service.get_relevant_context(
                f"user story {item.get('title', '')} {item.get('description', '')}",
                limit=2
            )
            
            system_prompt = self._get_backlog_analysis_system_prompt()
            human_prompt = self._build_backlog_analysis_human_prompt(item, similar_items, context)
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", human_prompt)
            ])
            
            formatted_prompt = prompt.format_prompt(
                format_instructions=self.backlog_parser.get_format_instructions()
            )
            
            response = await self.chat_model.agenerate([formatted_prompt.to_messages()])
            output = response.generations[0][0].text
            
            parsed_analysis = self.backlog_parser.parse(output)
            
            logger.info(f"Analyzed backlog item: {item.get('title', 'Unknown')}")
            return parsed_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze backlog item: {e}")
            return BacklogAnalysis(
                clarity_score=0.5,
                suggested_improvements=["Unable to analyze - please review manually"],
                estimated_complexity="M",
                potential_risks=["Analysis failed"],
                acceptance_criteria_suggestions=[]
            )

    async def suggest_sprint_plan(
        self,
        backlog_items: List[Dict[str, Any]],
        team_velocity: float,
        capacity_days: float,
        sprint_goal_context: Optional[str] = None
    ) -> SprintPlanSuggestion:
        """
        Suggest optimal sprint plan based on backlog and team capacity.
        
        Args:
            backlog_items: Available backlog items for selection
            team_velocity: Team's average velocity in story points
            capacity_days: Available person-days for the sprint
            sprint_goal_context: Optional context for sprint goal
            
        Returns:
            Structured sprint plan suggestion
        """
        try:
            # Get relevant context about past sprints
            context = await self.vector_service.get_relevant_context(
                f"sprint planning velocity {team_velocity} capacity",
                limit=3
            )
            
            system_prompt = self._get_sprint_planning_system_prompt()
            human_prompt = self._build_sprint_planning_human_prompt(
                backlog_items, team_velocity, capacity_days, sprint_goal_context, context
            )
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", human_prompt)
            ])
            
            formatted_prompt = prompt.format_prompt(
                format_instructions=self.sprint_parser.get_format_instructions()
            )
            
            response = await self.chat_model.agenerate([formatted_prompt.to_messages()])
            output = response.generations[0][0].text
            
            parsed_suggestion = self.sprint_parser.parse(output)
            
            logger.info(f"Generated sprint plan suggestion with {len(parsed_suggestion.recommended_items)} items")
            return parsed_suggestion
            
        except Exception as e:
            logger.error(f"Failed to generate sprint plan: {e}")
            return SprintPlanSuggestion(
                recommended_items=[],
                total_story_points=0,
                sprint_goal="Unable to generate sprint goal",
                risks=["Planning analysis failed"],
                capacity_utilization=0.0
            )

    def _get_standup_system_prompt(self, team_context: Dict[str, Any]) -> str:
        """Build system prompt for standup summaries."""
        tone = team_context.get('ai_tone', 'professional')
        team_name = team_context.get('name', 'the team')
        
        return f"""You are an AI Scrum Master assistant helping {team_name}. 
        Your role is to create concise, actionable daily standup summaries.
        
        Guidelines:
        - Use a {tone} tone
        - Focus on progress, blockers, and next steps
        - Identify potential risks or dependencies
        - Suggest concrete action items where helpful
        - Maintain team anonymity unless specifically needed
        - Be objective and supportive
        
        The summary will be shared with the team and stakeholders, so ensure it's clear and actionable."""

    def _build_standup_human_prompt(
        self, 
        entries: List[Dict[str, Any]], 
        jira_updates: Optional[List[Dict[str, Any]]], 
        context: List[str]
    ) -> str:
        """Build human prompt with standup data."""
        prompt_parts = []
        
        # Add context if available
        if context:
            prompt_parts.append("Relevant context from previous standups:")
            for ctx in context:
                prompt_parts.append(f"- {ctx}")
            prompt_parts.append("")
        
        # Add standup entries
        prompt_parts.append("Today's standup entries:")
        for entry in entries:
            user = entry.get('user', 'Team member')
            prompt_parts.append(f"\n**{user}:**")
            if entry.get('yesterday_work'):
                prompt_parts.append(f"Yesterday: {entry['yesterday_work']}")
            if entry.get('today_plan'):
                prompt_parts.append(f"Today: {entry['today_plan']}")
            if entry.get('blockers'):
                prompt_parts.append(f"Blockers: {entry['blockers']}")
        
        # Add Jira updates if available
        if jira_updates:
            prompt_parts.append("\nJira ticket updates from yesterday:")
            for update in jira_updates:
                prompt_parts.append(f"- {update.get('key', 'Unknown')}: {update.get('summary', 'No summary')}")
        
        prompt_parts.append("\nGenerate a comprehensive standup summary following the specified format.")
        prompt_parts.append("{format_instructions}")
        
        return "\n".join(prompt_parts)

    def _get_backlog_analysis_system_prompt(self) -> str:
        """Build system prompt for backlog analysis."""
        return """You are an expert agile coach analyzing user stories and backlog items.
        Your role is to assess clarity, identify improvements, and estimate complexity.
        
        Guidelines:
        - Evaluate description clarity and completeness
        - Suggest specific improvements for unclear items
        - Estimate complexity based on scope and technical requirements
        - Identify potential risks or dependencies
        - Suggest concrete acceptance criteria
        - Use standard estimation scale: XS, S, M, L, XL
        
        Be constructive and specific in your feedback."""

    def _build_backlog_analysis_human_prompt(
        self, 
        item: Dict[str, Any], 
        similar_items: Optional[List[Dict[str, Any]]], 
        context: List[str]
    ) -> str:
        """Build human prompt for backlog item analysis."""
        prompt_parts = []
        
        # Add context
        if context:
            prompt_parts.append("Relevant context from similar items:")
            for ctx in context:
                prompt_parts.append(f"- {ctx}")
            prompt_parts.append("")
        
        # Add item details
        prompt_parts.append("Backlog item to analyze:")
        prompt_parts.append(f"Title: {item.get('title', 'No title')}")
        prompt_parts.append(f"Description: {item.get('description', 'No description')}")
        
        if item.get('acceptance_criteria'):
            prompt_parts.append(f"Acceptance Criteria: {item['acceptance_criteria']}")
        
        if item.get('story_points'):
            prompt_parts.append(f"Current Story Points: {item['story_points']}")
        
        # Add similar items for reference
        if similar_items:
            prompt_parts.append("\nSimilar items for reference:")
            for similar in similar_items[:3]:  # Limit to 3 for brevity
                prompt_parts.append(f"- {similar.get('title', 'Unknown')}: {similar.get('story_points', 'No points')} points")
        
        prompt_parts.append("\nAnalyze this item following the specified format.")
        prompt_parts.append("{format_instructions}")
        
        return "\n".join(prompt_parts)

    def _get_sprint_planning_system_prompt(self) -> str:
        """Build system prompt for sprint planning."""
        return """You are an expert Scrum Master helping with sprint planning.
        Your role is to recommend optimal backlog items for the sprint based on capacity and priorities.
        
        Guidelines:
        - Consider team velocity and capacity constraints
        - Prioritize high-value, well-defined items
        - Ensure sprint goal coherence
        - Identify risks and dependencies
        - Aim for 80-90% capacity utilization for sustainable pace
        - Consider item complexity and team skills
        
        Provide realistic recommendations that promote team success."""

    def _build_sprint_planning_human_prompt(
        self,
        backlog_items: List[Dict[str, Any]],
        team_velocity: float,
        capacity_days: float,
        sprint_goal_context: Optional[str],
        context: List[str]
    ) -> str:
        """Build human prompt for sprint planning."""
        prompt_parts = []
        
        # Add context
        if context:
            prompt_parts.append("Context from previous sprints:")
            for ctx in context:
                prompt_parts.append(f"- {ctx}")
            prompt_parts.append("")
        
        # Add team capacity info
        prompt_parts.append("Team capacity information:")
        prompt_parts.append(f"- Average velocity: {team_velocity} story points")
        prompt_parts.append(f"- Available capacity: {capacity_days} person-days")
        
        if sprint_goal_context:
            prompt_parts.append(f"- Sprint goal context: {sprint_goal_context}")
        
        # Add backlog items
        prompt_parts.append("\nAvailable backlog items (ordered by priority):")
        for i, item in enumerate(backlog_items, 1):
            points = item.get('story_points', 'No estimate')
            priority = item.get('priority', 'medium')
            prompt_parts.append(
                f"{i}. [{item.get('id')}] {item.get('title', 'No title')} "
                f"({points} points, {priority} priority)"
            )
            if item.get('description'):
                # Truncate long descriptions
                desc = item['description'][:100] + "..." if len(item['description']) > 100 else item['description']
                prompt_parts.append(f"   Description: {desc}")
        
        prompt_parts.append("\nRecommend items for the sprint following the specified format.")
        prompt_parts.append("{format_instructions}")
        
        return "\n".join(prompt_parts)

# Global AI service instance
ai_service = AIService()