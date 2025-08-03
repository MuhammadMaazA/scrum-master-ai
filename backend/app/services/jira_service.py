"""
Jira integration service for issue tracking and project management.
Handles ticket retrieval, updates, and sprint management.
"""
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from atlassian import Jira
from atlassian.errors import ApiError

from app.core.config import settings

logger = logging.getLogger(__name__)

class JiraService:
    """
    Jira integration service for AI Scrum Master functionality.
    Handles ticket operations, sprint management, and project data retrieval.
    """
    
    def __init__(self):
        if not all([settings.JIRA_URL, settings.JIRA_USERNAME, settings.JIRA_API_TOKEN]):
            logger.warning("Jira credentials not fully configured")
            self.client = None
        else:
            try:
                self.client = Jira(
                    url=settings.JIRA_URL,
                    username=settings.JIRA_USERNAME,
                    password=settings.JIRA_API_TOKEN,
                    cloud=True
                )
                logger.info("Jira client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Jira client: {e}")
                self.client = None

    async def get_recent_ticket_updates(
        self, 
        project_key: str, 
        hours_back: int = 24,
        assignee: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get tickets updated in the last N hours.
        
        Args:
            project_key: Jira project key (e.g., "PROJ")
            hours_back: Look back this many hours
            assignee: Optional filter by assignee
            
        Returns:
            List of ticket updates with metadata
        """
        if not self.client:
            logger.error("Jira client not initialized")
            return []
            
        try:
            # Calculate cutoff time
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            cutoff_str = cutoff_time.strftime("%Y-%m-%d %H:%M")
            
            # Build JQL query
            jql_parts = [
                f"project = {project_key}",
                f"updated >= '{cutoff_str}'"
            ]
            
            if assignee:
                jql_parts.append(f"assignee = '{assignee}'")
            
            jql = " AND ".join(jql_parts)
            
            # Execute search
            issues = self.client.jql(
                jql,
                fields=['key', 'summary', 'status', 'assignee', 'updated', 'description', 'issuetype']
            )
            
            # Process results
            updates = []
            for issue in issues.get('issues', []):
                fields = issue.get('fields', {})
                
                update_info = {
                    'key': issue.get('key'),
                    'summary': fields.get('summary', ''),
                    'status': fields.get('status', {}).get('name', 'Unknown'),
                    'assignee': self._extract_user_name(fields.get('assignee')),
                    'updated': fields.get('updated'),
                    'issue_type': fields.get('issuetype', {}).get('name', 'Unknown'),
                    'url': f"{settings.JIRA_URL}/browse/{issue.get('key')}"
                }
                
                updates.append(update_info)
            
            logger.info(f"Retrieved {len(updates)} recent ticket updates from {project_key}")
            return updates
            
        except ApiError as e:
            logger.error(f"Jira API error getting recent updates: {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting recent ticket updates: {e}")
            return []

    async def get_sprint_issues(
        self, 
        board_id: int, 
        sprint_id: Optional[int] = None,
        state: str = "active"
    ) -> List[Dict[str, Any]]:
        """
        Get issues from a specific sprint or active sprint.
        
        Args:
            board_id: Jira board ID
            sprint_id: Optional specific sprint ID
            state: Sprint state (active, closed, future)
            
        Returns:
            List of sprint issues
        """
        if not self.client:
            return []
            
        try:
            # Get sprint if not provided
            if not sprint_id:
                sprints = self.client.sprints(board_id, state=state)
                if not sprints:
                    logger.warning(f"No {state} sprints found for board {board_id}")
                    return []
                sprint_id = sprints[0]['id']
            
            # Get sprint issues
            issues = self.client.sprint_issues(sprint_id, fields=[
                'key', 'summary', 'status', 'assignee', 'storyPoints', 
                'description', 'issuetype', 'priority', 'updated'
            ])
            
            # Process issues
            sprint_issues = []
            for issue in issues.get('issues', []):
                fields = issue.get('fields', {})
                
                issue_info = {
                    'key': issue.get('key'),
                    'summary': fields.get('summary', ''),
                    'status': fields.get('status', {}).get('name', 'Unknown'),
                    'assignee': self._extract_user_name(fields.get('assignee')),
                    'story_points': fields.get(self._get_story_points_field_id(), 0),
                    'issue_type': fields.get('issuetype', {}).get('name', 'Unknown'),
                    'priority': fields.get('priority', {}).get('name', 'Medium'),
                    'description': fields.get('description', ''),
                    'updated': fields.get('updated'),
                    'url': f"{settings.JIRA_URL}/browse/{issue.get('key')}"
                }
                
                sprint_issues.append(issue_info)
            
            logger.info(f"Retrieved {len(sprint_issues)} issues from sprint {sprint_id}")
            return sprint_issues
            
        except ApiError as e:
            logger.error(f"Jira API error getting sprint issues: {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting sprint issues: {e}")
            return []

    async def get_backlog_issues(
        self, 
        project_key: str, 
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get product backlog issues (not in any sprint).
        
        Args:
            project_key: Jira project key
            max_results: Maximum number of results
            
        Returns:
            List of backlog issues
        """
        if not self.client:
            return []
            
        try:
            # JQL for backlog items (not in sprint, not done)
            jql = f'project = {project_key} AND sprint is EMPTY AND status != Done ORDER BY priority DESC, created ASC'
            
            issues = self.client.jql(
                jql,
                fields=[
                    'key', 'summary', 'status', 'assignee', 'storyPoints',
                    'description', 'issuetype', 'priority', 'created', 'updated'
                ],
                limit=max_results
            )
            
            # Process backlog issues
            backlog_issues = []
            for issue in issues.get('issues', []):
                fields = issue.get('fields', {})
                
                issue_info = {
                    'key': issue.get('key'),
                    'summary': fields.get('summary', ''),
                    'status': fields.get('status', {}).get('name', 'Unknown'),
                    'assignee': self._extract_user_name(fields.get('assignee')),
                    'story_points': fields.get(self._get_story_points_field_id()),
                    'issue_type': fields.get('issuetype', {}).get('name', 'Unknown'),
                    'priority': fields.get('priority', {}).get('name', 'Medium'),
                    'description': fields.get('description', ''),
                    'created': fields.get('created'),
                    'updated': fields.get('updated'),
                    'url': f"{settings.JIRA_URL}/browse/{issue.get('key')}"
                }
                
                backlog_issues.append(issue_info)
            
            logger.info(f"Retrieved {len(backlog_issues)} backlog issues from {project_key}")
            return backlog_issues
            
        except ApiError as e:
            logger.error(f"Jira API error getting backlog: {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting backlog issues: {e}")
            return []

    async def update_issue_description(
        self, 
        issue_key: str, 
        new_description: str
    ) -> bool:
        """
        Update an issue's description.
        
        Args:
            issue_key: Jira issue key (e.g., "PROJ-123")
            new_description: New description text
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            return False
            
        try:
            self.client.issue_update(
                issue_key,
                fields={'description': new_description}
            )
            
            logger.info(f"Updated description for issue {issue_key}")
            return True
            
        except ApiError as e:
            logger.error(f"Jira API error updating issue {issue_key}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error updating issue {issue_key}: {e}")
            return False

    async def create_issue(
        self, 
        project_key: str, 
        summary: str, 
        description: str,
        issue_type: str = "Story",
        priority: str = "Medium",
        assignee: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a new Jira issue.
        
        Args:
            project_key: Jira project key
            summary: Issue summary/title
            description: Issue description
            issue_type: Issue type (Story, Bug, Task, etc.)
            priority: Priority level
            assignee: Optional assignee username
            
        Returns:
            Issue key if successful, None otherwise
        """
        if not self.client:
            return None
            
        try:
            fields = {
                'project': {'key': project_key},
                'summary': summary,
                'description': description,
                'issuetype': {'name': issue_type},
                'priority': {'name': priority}
            }
            
            if assignee:
                fields['assignee'] = {'name': assignee}
            
            response = self.client.issue_create(fields=fields)
            issue_key = response.get('key')
            
            if issue_key:
                logger.info(f"Created new issue: {issue_key}")
                return issue_key
            
        except ApiError as e:
            logger.error(f"Jira API error creating issue: {e}")
        except Exception as e:
            logger.error(f"Error creating issue: {e}")
        
        return None

    async def get_project_velocity(
        self, 
        board_id: int, 
        sprint_count: int = 5
    ) -> Dict[str, Any]:
        """
        Calculate team velocity based on recent sprints.
        
        Args:
            board_id: Jira board ID
            sprint_count: Number of recent sprints to analyze
            
        Returns:
            Velocity statistics
        """
        if not self.client:
            return {}
            
        try:
            # Get recent completed sprints
            sprints = self.client.sprints(board_id, state='closed')
            recent_sprints = sprints[:sprint_count] if sprints else []
            
            velocities = []
            sprint_details = []
            
            for sprint in recent_sprints:
                sprint_id = sprint['id']
                issues = self.client.sprint_issues(sprint_id, fields=['storyPoints'])
                
                # Calculate completed story points
                total_points = 0
                completed_issues = 0
                
                for issue in issues.get('issues', []):
                    fields = issue.get('fields', {})
                    story_points = fields.get(self._get_story_points_field_id(), 0)
                    
                    if story_points:
                        total_points += story_points
                        completed_issues += 1
                
                velocities.append(total_points)
                sprint_details.append({
                    'name': sprint.get('name', ''),
                    'points': total_points,
                    'issues': completed_issues
                })
            
            # Calculate statistics
            if velocities:
                avg_velocity = sum(velocities) / len(velocities)
                max_velocity = max(velocities)
                min_velocity = min(velocities)
            else:
                avg_velocity = max_velocity = min_velocity = 0
            
            return {
                'average_velocity': avg_velocity,
                'max_velocity': max_velocity,
                'min_velocity': min_velocity,
                'sprint_count': len(velocities),
                'recent_sprints': sprint_details
            }
            
        except ApiError as e:
            logger.error(f"Jira API error calculating velocity: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error calculating velocity: {e}")
            return {}

    def _extract_user_name(self, user_obj: Optional[Dict[str, Any]]) -> Optional[str]:
        """Extract user name from Jira user object."""
        if not user_obj:
            return None
        return user_obj.get('displayName') or user_obj.get('name', 'Unknown User')

    def _get_story_points_field_id(self) -> str:
        """Get the field ID for story points (varies by Jira setup)."""
        # This is typically a custom field in Jira
        # Common field IDs for story points: customfield_10002, customfield_10016
        # You may need to adjust this based on your Jira configuration
        return 'customfield_10002'

    async def test_connection(self) -> bool:
        """Test Jira connection."""
        if not self.client:
            return False
            
        try:
            # Try to get current user info
            user = self.client.myself()
            logger.info(f"Jira connection test successful. User: {user.get('displayName', 'Unknown')}")
            return True
        except Exception as e:
            logger.error(f"Jira connection test failed: {e}")
            return False

    async def get_projects(self) -> List[Dict[str, Any]]:
        """Get list of available projects."""
        if not self.client:
            return []
            
        try:
            projects = self.client.projects()
            return [
                {
                    'key': project.get('key'),
                    'name': project.get('name'),
                    'id': project.get('id')
                }
                for project in projects
            ]
        except Exception as e:
            logger.error(f"Error getting projects: {e}")
            return []

# Global Jira service instance
jira_service = JiraService()