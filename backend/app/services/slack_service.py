"""
Slack integration service for bot interactions and message handling.
Handles standup coordination, message posting, and team communication.
"""
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.web import SlackResponse

from app.core.config import settings

logger = logging.getLogger(__name__)

class SlackService:
    """
    Slack integration service for AI Scrum Master bot functionality.
    Handles message posting, event processing, and standup coordination.
    """
    
    def __init__(self):
        if not settings.SLACK_BOT_TOKEN:
            logger.warning("Slack bot token not configured")
            self.client = None
        else:
            self.client = WebClient(token=settings.SLACK_BOT_TOKEN)
            
        self.bot_user_id = None
        self._initialize_bot_info()
    
    def _initialize_bot_info(self):
        """Initialize bot information and verify connection."""
        if not self.client:
            return
            
        try:
            response = self.client.auth_test()
            self.bot_user_id = response["user_id"]
            logger.info(f"Slack bot initialized successfully. Bot user ID: {self.bot_user_id}")
        except SlackApiError as e:
            logger.error(f"Failed to initialize Slack bot: {e}")

    async def post_standup_summary(
        self, 
        channel_id: str, 
        summary: str,
        blocks: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[str]:
        """
        Post standup summary to a Slack channel.
        
        Args:
            channel_id: Slack channel ID
            summary: Summary text
            blocks: Optional rich formatting blocks
            
        Returns:
            Message timestamp if successful, None otherwise
        """
        if not self.client:
            logger.error("Slack client not initialized")
            return None
            
        try:
            # Build the message
            message_data = {
                "channel": channel_id,
                "text": f"📋 Daily Standup Summary\n{summary}"
            }
            
            if blocks:
                message_data["blocks"] = blocks
            else:
                # Create default rich formatting
                message_data["blocks"] = self._create_standup_summary_blocks(summary)
            
            # Post message
            response = self.client.chat_postMessage(**message_data)
            
            if response["ok"]:
                logger.info(f"Posted standup summary to channel {channel_id}")
                return response["ts"]  # Message timestamp
            else:
                logger.error(f"Failed to post message: {response.get('error', 'Unknown error')}")
                return None
                
        except SlackApiError as e:
            logger.error(f"Slack API error posting summary: {e}")
            return None

    async def collect_standup_messages(
        self, 
        channel_id: str, 
        since_hours: int = 24,
        keywords: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Collect standup-related messages from a channel.
        
        Args:
            channel_id: Slack channel ID
            since_hours: Look back this many hours
            keywords: Optional keywords to filter messages
            
        Returns:
            List of relevant messages with metadata
        """
        if not self.client:
            logger.error("Slack client not initialized")
            return []
            
        try:
            # Calculate timestamp for lookback
            since_timestamp = (datetime.now() - timedelta(hours=since_hours)).timestamp()
            
            # Get conversation history
            response = self.client.conversations_history(
                channel=channel_id,
                oldest=str(since_timestamp),
                limit=200  # Adjust as needed
            )
            
            if not response["ok"]:
                logger.error(f"Failed to get conversation history: {response.get('error')}")
                return []
            
            messages = response["messages"]
            standup_messages = []
            
            # Process messages
            for message in messages:
                # Skip bot messages (including our own)
                if message.get("bot_id") or message.get("user") == self.bot_user_id:
                    continue
                
                # Filter by keywords if provided
                text = message.get("text", "").lower()
                if keywords:
                    if not any(keyword.lower() in text for keyword in keywords):
                        continue
                
                # Get user info
                user_info = await self._get_user_info(message.get("user"))
                
                standup_entry = {
                    "user_id": message.get("user"),
                    "user_name": user_info.get("real_name", "Unknown User"),
                    "message": message.get("text", ""),
                    "timestamp": datetime.fromtimestamp(float(message.get("ts", 0))),
                    "thread_ts": message.get("thread_ts"),
                    "is_thread_reply": bool(message.get("thread_ts"))
                }
                
                standup_messages.append(standup_entry)
            
            logger.info(f"Collected {len(standup_messages)} standup messages from {channel_id}")
            return standup_messages
            
        except SlackApiError as e:
            logger.error(f"Error collecting standup messages: {e}")
            return []

    async def parse_standup_from_message(self, message: str) -> Dict[str, str]:
        """
        Parse a message to extract standup information.
        Looks for patterns like "Yesterday:", "Today:", "Blockers:" etc.
        
        Args:
            message: Raw message text
            
        Returns:
            Dictionary with parsed standup fields
        """
        standup_data = {
            "yesterday_work": "",
            "today_plan": "",
            "blockers": "",
            "additional_notes": ""
        }
        
        # Common standup patterns
        patterns = {
            "yesterday_work": [
                "yesterday:", "yesterday i", "completed:", "done:", "finished:",
                "worked on:", "yesterday's work:", "what i did:"
            ],
            "today_plan": [
                "today:", "today i", "planning:", "will do:", "going to:",
                "today's plan:", "next:", "working on:"
            ],
            "blockers": [
                "blockers:", "blocked:", "blocker:", "issues:", "problems:",
                "stuck:", "need help:", "impediments:"
            ]
        }
        
        # Split message into lines and process
        lines = message.lower().split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line starts a new section
            section_found = False
            for section, keywords in patterns.items():
                for keyword in keywords:
                    if line.startswith(keyword):
                        current_section = section
                        # Extract content after the keyword
                        content = line[len(keyword):].strip()
                        if content:
                            standup_data[section] = content
                        section_found = True
                        break
                if section_found:
                    break
            
            # If no section keyword found, append to current section
            if not section_found and current_section:
                if standup_data[current_section]:
                    standup_data[current_section] += " " + line
                else:
                    standup_data[current_section] = line
        
        # If no structured format found, treat as general notes
        if not any(standup_data.values()):
            standup_data["additional_notes"] = message
        
        return standup_data

    async def send_standup_reminder(
        self, 
        channel_id: str, 
        custom_message: Optional[str] = None
    ) -> Optional[str]:
        """
        Send a standup reminder to the team.
        
        Args:
            channel_id: Slack channel ID
            custom_message: Optional custom reminder message
            
        Returns:
            Message timestamp if successful
        """
        if not self.client:
            return None
            
        try:
            if custom_message:
                message = custom_message
            else:
                message = "🌅 Good morning team! Time for our daily standup. Please share:\n• What you completed yesterday\n• What you're planning today\n• Any blockers or help needed"
            
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": message
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Submit Standup"
                            },
                            "action_id": "standup_submit",
                            "style": "primary"
                        }
                    ]
                }
            ]
            
            response = self.client.chat_postMessage(
                channel=channel_id,
                text=message,
                blocks=blocks
            )
            
            if response["ok"]:
                logger.info(f"Sent standup reminder to {channel_id}")
                return response["ts"]
            
        except SlackApiError as e:
            logger.error(f"Error sending standup reminder: {e}")
        
        return None

    async def react_to_message(self, channel_id: str, timestamp: str, emoji: str = "white_check_mark"):
        """Add a reaction to a message."""
        if not self.client:
            return False
            
        try:
            response = self.client.reactions_add(
                channel=channel_id,
                timestamp=timestamp,
                name=emoji
            )
            return response["ok"]
        except SlackApiError as e:
            logger.error(f"Error adding reaction: {e}")
            return False

    async def get_channel_members(self, channel_id: str) -> List[Dict[str, Any]]:
        """Get list of channel members."""
        if not self.client:
            return []
            
        try:
            response = self.client.conversations_members(channel=channel_id)
            if not response["ok"]:
                return []
            
            members = []
            for user_id in response["members"]:
                user_info = await self._get_user_info(user_id)
                if user_info and not user_info.get("is_bot", False):
                    members.append({
                        "id": user_id,
                        "name": user_info.get("real_name", "Unknown"),
                        "display_name": user_info.get("display_name", ""),
                        "email": user_info.get("profile", {}).get("email")
                    })
            
            return members
            
        except SlackApiError as e:
            logger.error(f"Error getting channel members: {e}")
            return []

    async def _get_user_info(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information from Slack."""
        if not self.client or not user_id:
            return None
            
        try:
            response = self.client.users_info(user=user_id)
            if response["ok"]:
                return response["user"]
        except SlackApiError as e:
            logger.error(f"Error getting user info for {user_id}: {e}")
        
        return None

    def _create_standup_summary_blocks(self, summary: str) -> List[Dict[str, Any]]:
        """Create rich Slack blocks for standup summary."""
        return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📋 Daily Standup Summary"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": summary
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Generated by AI Scrum Master • {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    }
                ]
            }
        ]

    async def test_connection(self) -> bool:
        """Test Slack connection."""
        if not self.client:
            return False
            
        try:
            response = self.client.auth_test()
            return response["ok"]
        except SlackApiError:
            return False

# Global Slack service instance
slack_service = SlackService()