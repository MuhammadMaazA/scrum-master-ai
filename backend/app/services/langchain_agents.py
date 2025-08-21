"""
LangChain Agents and Tools for advanced AI automation.

This module provides sophisticated AI agents that can make decisions,
use tools, and perform complex workflows for Scrum Master tasks.
"""
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, date

from langchain.agents import Tool, AgentExecutor, create_openai_tools_agent
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.slack_service import slack_service
from app.services.jira_service import jira_service
from app.services.analytics_service import analytics_service
from app.services.vector_service import vector_service

logger = logging.getLogger(__name__)

class SlackTool(BaseTool):
    """Tool for interacting with Slack."""
    
    name: str = "slack_messenger"
    description: str = "Send messages or collect information from Slack channels. Use this to post standup summaries, send reminders, or gather team updates."
    
    def _run(
        self, 
        action: str,
        channel: str = "#standup",
        message: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Execute Slack actions."""
        try:
            if action == "send_message":
                if not message:
                    return "Error: Message content is required for send_message action"
                
                # Send message to Slack
                result = slack_service.post_message(channel, message)
                if result:
                    return f"Successfully sent message to {channel}"
                else:
                    return f"Failed to send message to {channel}"
            
            elif action == "collect_standup":
                # Collect standup updates
                updates = slack_service.collect_standup_updates(channel)
                return f"Collected {len(updates)} standup updates from {channel}"
            
            elif action == "send_reminder":
                reminder_msg = message or "🔔 Friendly reminder: Please post your daily standup update!"
                result = slack_service.post_message(channel, reminder_msg)
                return f"Sent standup reminder to {channel}" if result else "Failed to send reminder"
            
            else:
                return f"Unknown Slack action: {action}. Available actions: send_message, collect_standup, send_reminder"
                
        except Exception as e:
            logger.error(f"Slack tool error: {e}")
            return f"Slack tool error: {str(e)}"

class JiraTool(BaseTool):
    """Tool for interacting with Jira."""
    
    name = "jira_manager"
    description = "Manage Jira tickets and project data. Use this to create tickets, update statuses, sync data, or get project information."
    
    def _run(
        self,
        action: str,
        project_key: str = settings.JIRA_PROJECT_KEY,
        ticket_key: str = "",
        ticket_data: Dict[str, Any] = None,
        status: str = "",
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Execute Jira actions."""
        try:
            if action == "create_ticket":
                if not ticket_data:
                    return "Error: ticket_data is required for create_ticket action"
                
                ticket_key = jira_service.create_jira_ticket(ticket_data)
                if ticket_key:
                    return f"Created Jira ticket: {ticket_key}"
                else:
                    return "Failed to create Jira ticket"
            
            elif action == "update_status":
                if not ticket_key or not status:
                    return "Error: ticket_key and status are required for update_status action"
                
                success = jira_service.update_ticket_status(ticket_key, status)
                return f"Updated {ticket_key} to {status}" if success else f"Failed to update {ticket_key}"
            
            elif action == "sync_project":
                sync_results = jira_service.auto_sync_project_data(project_key)
                if "error" not in sync_results:
                    backlog_count = sync_results.get("backlog_sync", {}).get("total_issues", 0)
                    sprint_count = sync_results.get("sprint_sync", {}).get("total_sprints", 0)
                    return f"Synced project {project_key}: {backlog_count} issues, {sprint_count} sprints"
                else:
                    return f"Sync failed: {sync_results['error']}"
            
            elif action == "get_tickets":
                tickets = jira_service.get_recent_ticket_updates(project_key, hours_back=24)
                return f"Retrieved {len(tickets)} recent tickets from {project_key}"
            
            else:
                return f"Unknown Jira action: {action}. Available actions: create_ticket, update_status, sync_project, get_tickets"
                
        except Exception as e:
            logger.error(f"Jira tool error: {e}")
            return f"Jira tool error: {str(e)}"

class AnalyticsTool(BaseTool):
    """Tool for generating analytics and reports."""
    
    name = "analytics_generator"
    description = "Generate sprint analytics, burndown charts, and performance reports. Use this to analyze team velocity, sprint progress, and generate insights."
    
    def _run(
        self,
        action: str,
        sprint_id: int = None,
        team_id: int = None,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Execute analytics actions."""
        try:
            if action == "sprint_metrics":
                if not sprint_id:
                    return "Error: sprint_id is required for sprint_metrics action"
                
                metrics = analytics_service.get_sprint_metrics(sprint_id)
                if metrics:
                    return f"Sprint {metrics.sprint_name}: {metrics.completion_percentage:.1f}% complete, {metrics.days_remaining} days remaining"
                else:
                    return f"Failed to get metrics for sprint {sprint_id}"
            
            elif action == "burndown_chart":
                if not sprint_id:
                    return "Error: sprint_id is required for burndown_chart action"
                
                chart_data = analytics_service.get_burndown_chart_data(sprint_id)
                if "error" not in chart_data:
                    return f"Generated burndown chart for sprint {chart_data.get('sprint_name', sprint_id)}"
                else:
                    return f"Failed to generate burndown chart: {chart_data['error']}"
            
            elif action == "velocity_analysis":
                if not team_id:
                    return "Error: team_id is required for velocity_analysis action"
                
                velocity_data = analytics_service.get_team_velocity_history(team_id)
                if velocity_data:
                    avg_velocity = sum(v.velocity for v in velocity_data) / len(velocity_data)
                    return f"Team velocity analysis: {len(velocity_data)} sprints analyzed, average velocity {avg_velocity:.2f}"
                else:
                    return f"No velocity data found for team {team_id}"
            
            elif action == "sprint_report":
                if not sprint_id:
                    return "Error: sprint_id is required for sprint_report action"
                
                report = analytics_service.generate_sprint_report(sprint_id)
                if "error" not in report:
                    return f"Generated comprehensive sprint report for {report.get('sprint_overview', {}).get('name', sprint_id)}"
                else:
                    return f"Failed to generate sprint report: {report['error']}"
            
            else:
                return f"Unknown analytics action: {action}. Available actions: sprint_metrics, burndown_chart, velocity_analysis, sprint_report"
                
        except Exception as e:
            logger.error(f"Analytics tool error: {e}")
            return f"Analytics tool error: {str(e)}"

class KnowledgeTool(BaseTool):
    """Tool for accessing and storing project knowledge."""
    
    name = "knowledge_base"
    description = "Access project knowledge, past decisions, and team context. Use this to retrieve relevant information or store new insights."
    
    def _run(
        self,
        action: str,
        query: str = "",
        content: str = "",
        doc_type: str = "general",
        metadata: Dict[str, Any] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Execute knowledge base actions."""
        try:
            if action == "search":
                if not query:
                    return "Error: query is required for search action"
                
                results = vector_service.get_relevant_context(query, limit=5)
                if results:
                    return f"Found {len(results)} relevant knowledge items for query: '{query}'"
                else:
                    return f"No relevant knowledge found for query: '{query}'"
            
            elif action == "store":
                if not content:
                    return "Error: content is required for store action"
                
                doc_id = vector_service.store_context(
                    content, 
                    metadata or {"timestamp": datetime.now().isoformat()}, 
                    doc_type
                )
                return f"Stored knowledge item with ID: {doc_id}"
            
            elif action == "get_team_context":
                team_id = metadata.get("team_id") if metadata else None
                if not team_id:
                    return "Error: team_id is required in metadata for get_team_context action"
                
                context = vector_service.get_team_context(team_id)
                return f"Retrieved team context: {len(context)} items found"
            
            else:
                return f"Unknown knowledge action: {action}. Available actions: search, store, get_team_context"
                
        except Exception as e:
            logger.error(f"Knowledge tool error: {e}")
            return f"Knowledge tool error: {str(e)}"

class ScrumMasterAgent:
    """AI Scrum Master agent with decision-making capabilities."""
    
    def __init__(self):
        """Initialize the Scrum Master agent with tools."""
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        # Initialize tools
        self.tools = [
            SlackTool(),
            JiraTool(),
            AnalyticsTool(),
            KnowledgeTool()
        ]
        
        # Create agent prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Create agent
        self.agent = create_openai_tools_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            max_iterations=5
        )
        
        logger.info("Scrum Master Agent initialized with tools")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the Scrum Master agent."""
        return """You are an AI Scrum Master assistant with advanced capabilities. Your role is to:

1. **Facilitate daily standups**: Collect updates, identify blockers, generate summaries
2. **Manage sprint planning**: Analyze velocity, suggest optimal sprint composition
3. **Monitor progress**: Track burndown, identify risks, provide insights
4. **Automate workflows**: Create tickets, update statuses, send notifications
5. **Maintain knowledge**: Store decisions, retrieve context, learn from history

**Available Tools:**
- slack_messenger: Send messages, collect standup updates, send reminders
- jira_manager: Create/update tickets, sync project data, get ticket information
- analytics_generator: Generate sprint metrics, burndown charts, velocity analysis
- knowledge_base: Search/store project knowledge and team context

**Guidelines:**
- Always be proactive and helpful
- Use tools appropriately to gather information before making recommendations
- Focus on actionable insights and concrete next steps
- Maintain team transparency and communication
- Store important decisions and insights for future reference
- Be concise but thorough in your responses

**Decision Making:**
- When asked to help with standup, collect updates first, then generate summary
- When planning sprints, analyze velocity and capacity before recommending items
- When issues arise, search knowledge base for similar past situations
- Always confirm actions that modify data (creating tickets, updating statuses)

You are operating with human oversight - provide recommendations and execute approved actions."""
    
    async def process_request(self, request: str, context: Dict[str, Any] = None) -> str:
        """Process a request using the agent's tools and reasoning."""
        try:
            # Add context to the request if provided
            if context:
                context_str = f"\nContext: {context}"
                request += context_str
            
            # Execute the agent
            result = await self.agent_executor.ainvoke({
                "input": request
            })
            
            return result["output"]
            
        except Exception as e:
            logger.error(f"Agent processing error: {e}")
            return f"I encountered an error while processing your request: {str(e)}. Please try again or rephrase your request."
    
    async def daily_standup_workflow(self, channel: str = "#standup") -> str:
        """Execute the complete daily standup workflow."""
        try:
            workflow_steps = [
                f"Use slack_messenger to collect_standup from {channel}",
                "Analyze the collected updates for blockers and progress",
                "Generate a comprehensive standup summary",
                f"Use slack_messenger to send_message the summary back to {channel}",
                "Store the summary in knowledge_base for future reference"
            ]
            
            request = f"""Execute the daily standup workflow:
            1. Collect standup updates from {channel}
            2. Analyze updates for progress, blockers, and key insights
            3. Generate a professional standup summary
            4. Post the summary back to the channel
            5. Store important insights for future reference
            
            Please execute these steps and provide a summary of what was accomplished."""
            
            return await self.process_request(request)
            
        except Exception as e:
            logger.error(f"Standup workflow error: {e}")
            return f"Failed to execute standup workflow: {str(e)}"
    
    async def sprint_health_check(self, sprint_id: int) -> str:
        """Perform a comprehensive sprint health check."""
        try:
            request = f"""Perform a sprint health check for sprint ID {sprint_id}:
            1. Use analytics_generator to get sprint_metrics for sprint {sprint_id}
            2. Generate a burndown_chart analysis
            3. Identify any risks or issues with current progress
            4. Search knowledge_base for similar past sprint patterns
            5. Provide actionable recommendations for the team
            
            Please provide a comprehensive health assessment with specific insights and recommendations."""
            
            return await self.process_request(request)
            
        except Exception as e:
            logger.error(f"Sprint health check error: {e}")
            return f"Failed to perform sprint health check: {str(e)}"
    
    async def intelligent_ticket_creation(self, ticket_request: str, project_context: Dict[str, Any] = None) -> str:
        """Create a ticket using AI analysis and context."""
        try:
            context_info = ""
            if project_context:
                context_info = f"\nProject context: {project_context}"
            
            request = f"""Create an intelligent Jira ticket based on this request: "{ticket_request}"{context_info}
            
            Please:
            1. Search knowledge_base for similar past tickets or requirements
            2. Analyze the request to determine appropriate ticket type, priority, and story points
            3. Use jira_manager to create_ticket with well-structured title, description, and metadata
            4. Store the creation decision in knowledge_base for future reference
            
            Provide the ticket key and a summary of the created ticket."""
            
            return await self.process_request(request)
            
        except Exception as e:
            logger.error(f"Intelligent ticket creation error: {e}")
            return f"Failed to create intelligent ticket: {str(e)}"

# Global agent instance
scrum_master_agent = ScrumMasterAgent()