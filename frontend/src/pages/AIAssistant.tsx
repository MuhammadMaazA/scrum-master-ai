import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Grid,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Chip,
  Divider,
  Paper,
  IconButton,
} from '@mui/material';
import {
  SmartToy as AIIcon,
  Send as SendIcon,
  Lightbulb as InsightIcon,
  Timeline as TrendIcon,
  Assignment as TaskIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';
import { useQuery, useMutation } from 'react-query';
import { aiAPI } from '../services/api';

interface ChatMessage {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  category?: 'general' | 'standup' | 'backlog' | 'sprint';
}

const AIAssistant: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: '1',
      type: 'ai',
      content: 'Hello! I\'m your AI Scrum Master assistant. I can help you with standup summaries, backlog analysis, sprint planning, and general agile questions. What would you like to know?',
      timestamp: new Date(),
      category: 'general',
    },
  ]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  // Fetch AI health status
  const { data: aiHealth } = useQuery('ai-health', aiAPI.healthCheck);

  // Sample quick actions
  const quickActions = [
    {
      title: 'Analyze Team Velocity',
      description: 'Get insights about your team\'s sprint velocity trends',
      prompt: 'Can you analyze our team\'s velocity trends and suggest improvements?',
      category: 'sprint' as const,
      icon: <TrendIcon />,
    },
    {
      title: 'Backlog Health Check',
      description: 'Review backlog quality and suggest improvements',
      prompt: 'Please review our product backlog and identify items that need attention',
      category: 'backlog' as const,
      icon: <TaskIcon />,
    },
    {
      title: 'Standup Insights',
      description: 'Get insights from recent standup summaries',
      prompt: 'What patterns do you see in our recent standups? Any recommendations?',
      category: 'standup' as const,
      icon: <InsightIcon />,
    },
    {
      title: 'Sprint Planning Tips',
      description: 'Get advice for upcoming sprint planning',
      prompt: 'What should we consider for our next sprint planning session?',
      category: 'sprint' as const,
      icon: <AIIcon />,
    },
  ];

  const handleSendMessage = async () => {
    if (!currentMessage.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: currentMessage,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsProcessing(true);

    try {
      // Simulate AI response (in real implementation, this would call your AI API)
      const aiResponse = await simulateAIResponse(currentMessage);
      
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: aiResponse,
        timestamp: new Date(),
        category: detectCategory(currentMessage),
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: 'I apologize, but I encountered an error processing your request. Please try again or contact support if the issue persists.',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  const simulateAIResponse = async (message: string): Promise<string> => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1500));

    // Simple keyword-based responses for demo
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('velocity') || lowerMessage.includes('sprint performance')) {
      return `Based on your team's recent sprint data, I can see some interesting patterns:

**Velocity Analysis:**
• Your average velocity is 23 story points per sprint
• You've maintained consistent performance over the last 5 sprints
• Best sprint: 28 points (Sprint 14)
• There's a slight dip in velocity when taking on technical debt stories

**Recommendations:**
• Consider dedicating 20% of each sprint to technical debt
• Your velocity is stable - you can confidently plan for 22-25 points
• The team performs better with 8-10 smaller stories vs 4-5 large ones

Would you like me to analyze any specific sprint or create a capacity plan for your next sprint?`;
    }

    if (lowerMessage.includes('backlog') || lowerMessage.includes('user stories')) {
      return `I've analyzed your product backlog and here's what I found:

**Backlog Health Score: 78/100** 📊

**Issues Found:**
• 12 stories lack clear acceptance criteria
• 5 potential duplicate stories detected
• 8 stories are too large (>13 points) and should be split
• 3 stories have unclear business value

**Recommendations:**
• Prioritize refining stories in the "Ready for Sprint" state
• Consider a backlog grooming session to address large stories
• Update acceptance criteria for high-priority items
• Remove or archive 4 low-value stories that haven't moved in 6 months

Would you like me to suggest specific improvements for any of these stories?`;
    }

    if (lowerMessage.includes('standup') || lowerMessage.includes('daily')) {
      return `Based on your recent standup patterns, here are my insights:

**Standup Analysis:**
• Average participation: 92% (excellent!)
• Most common blocker: External dependencies (40% of blockers)
• Team sentiment trend: Positive and stable
• Average standup duration: 12 minutes (within target)

**Key Patterns:**
• Blockers are typically resolved within 1.5 days
• Stories tend to stay "in progress" longer than estimated
• Best collaboration happens on UI/frontend tasks

**Suggestions:**
• Create a "dependency tracking board" for external blockers
• Consider pair programming for backend API tasks
• Daily async check-ins work well for your team

Would you like me to generate a custom standup format for your team?`;
    }

    if (lowerMessage.includes('planning') || lowerMessage.includes('next sprint')) {
      return `Here's what to consider for your upcoming sprint planning:

**Preparation Checklist:**
✅ Backlog refined and stories estimated
✅ Team availability confirmed (4 members, 10 days each)
✅ Previous sprint retrospective actions identified

**Capacity Recommendation:**
• Target: 24-26 story points (based on your 23-point average)
• Reserve 15% buffer for unexpected work
• Include 1-2 technical improvement tasks

**Focus Areas:**
• Complete the user authentication feature (8 points remaining)
• Address 2 critical bugs from production
• Start payment integration (plan for 2-sprint epic)

**Risks to Consider:**
• Holiday schedule may reduce capacity by 10%
• New team member still ramping up
• External API dependency for payment feature

Would you like me to suggest a specific set of stories for the sprint?`;
    }

    // Default response
    return `I understand you're asking about "${message}". 

As your AI Scrum Master assistant, I can help you with:
• **Sprint Planning** - Capacity analysis and story selection
• **Backlog Management** - Story refinement and prioritization  
• **Standup Insights** - Team patterns and improvement suggestions
• **Velocity Tracking** - Performance trends and forecasting
• **Process Improvement** - Agile best practices and team optimization

Could you be more specific about what aspect you'd like help with? For example:
- "Analyze our team's velocity trends"
- "Review our current backlog for issues"
- "Suggest improvements for our standups"
- "Help plan our next sprint"`;
  };

  const detectCategory = (message: string): ChatMessage['category'] => {
    const lowerMessage = message.toLowerCase();
    if (lowerMessage.includes('standup') || lowerMessage.includes('daily')) return 'standup';
    if (lowerMessage.includes('backlog') || lowerMessage.includes('story')) return 'backlog';
    if (lowerMessage.includes('sprint') || lowerMessage.includes('planning')) return 'sprint';
    return 'general';
  };

  const handleQuickAction = (prompt: string) => {
    setCurrentMessage(prompt);
  };

  const clearConversation = () => {
    setMessages([messages[0]]); // Keep the welcome message
  };

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            AI Assistant
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Your intelligent Scrum Master companion
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<ClearIcon />}
          onClick={clearConversation}
          disabled={messages.length <= 1}
        >
          Clear Chat
        </Button>
      </Box>

      {/* AI Status */}
      <Alert 
        severity={aiHealth?.ai_service === 'operational' ? 'success' : 'warning'}
        sx={{ mb: 3 }}
      >
        <strong>AI Status:</strong> {aiHealth?.ai_service === 'operational' 
          ? 'All AI services running smoothly' 
          : 'Some AI features may be limited'}
      </Alert>

      <Grid container spacing={3}>
        {/* Chat Interface */}
        <Grid item xs={12} lg={8}>
          <Card sx={{ height: 600, display: 'flex', flexDirection: 'column' }}>
            {/* Chat Messages */}
            <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
              <List>
                {messages.map((message) => (
                  <ListItem 
                    key={message.id} 
                    sx={{ 
                      flexDirection: 'column',
                      alignItems: message.type === 'user' ? 'flex-end' : 'flex-start',
                      mb: 1
                    }}
                  >
                    <Paper
                      elevation={1}
                      sx={{
                        p: 2,
                        maxWidth: '80%',
                        bgcolor: message.type === 'user' ? 'primary.main' : 'grey.100',
                        color: message.type === 'user' ? 'white' : 'text.primary',
                        borderRadius: 2,
                      }}
                    >
                      <Box display="flex" alignItems="center" gap={1} mb={1}>
                        {message.type === 'ai' && <AIIcon fontSize="small" />}
                        <Typography variant="caption" color="inherit" sx={{ opacity: 0.8 }}>
                          {message.type === 'user' ? 'You' : 'AI Assistant'}
                        </Typography>
                        {message.category && (
                          <Chip 
                            label={message.category} 
                            size="small" 
                            variant="outlined"
                            sx={{ 
                              color: 'inherit', 
                              borderColor: 'currentColor',
                              opacity: 0.7 
                            }}
                          />
                        )}
                      </Box>
                      <Typography 
                        variant="body2" 
                        sx={{ whiteSpace: 'pre-line' }}
                      >
                        {message.content}
                      </Typography>
                      <Typography 
                        variant="caption" 
                        color="inherit" 
                        opacity={0.6}
                        display="block"
                        mt={1}
                      >
                        {message.timestamp.toLocaleTimeString()}
                      </Typography>
                    </Paper>
                  </ListItem>
                ))}
                {isProcessing && (
                  <ListItem sx={{ justifyContent: 'flex-start' }}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <CircularProgress size={16} />
                      <Typography variant="body2" color="text.secondary">
                        AI is thinking...
                      </Typography>
                    </Box>
                  </ListItem>
                )}
              </List>
            </Box>

            {/* Input Area */}
            <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
              <Box display="flex" gap={1}>
                <TextField
                  fullWidth
                  multiline
                  maxRows={3}
                  placeholder="Ask me anything about your agile process..."
                  value={currentMessage}
                  onChange={(e) => setCurrentMessage(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      handleSendMessage();
                    }
                  }}
                />
                <Button
                  variant="contained"
                  endIcon={<SendIcon />}
                  onClick={handleSendMessage}
                  disabled={!currentMessage.trim() || isProcessing}
                  sx={{ minWidth: 'auto', px: 3 }}
                >
                  Send
                </Button>
              </Box>
            </Box>
          </Card>
        </Grid>

        {/* Quick Actions & Suggestions */}
        <Grid item xs={12} lg={4}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Get instant insights with these common requests
              </Typography>
              
              <Box display="flex" flexDirection="column" gap={1}>
                {quickActions.map((action, index) => (
                  <Button
                    key={index}
                    variant="outlined"
                    fullWidth
                    startIcon={action.icon}
                    onClick={() => handleQuickAction(action.prompt)}
                    sx={{ 
                      justifyContent: 'flex-start', 
                      textAlign: 'left',
                      p: 2,
                      height: 'auto'
                    }}
                  >
                    <Box>
                      <Typography variant="subtitle2" fontWeight="bold">
                        {action.title}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {action.description}
                      </Typography>
                    </Box>
                  </Button>
                ))}
              </Box>
            </CardContent>
          </Card>

          {/* AI Capabilities */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                AI Capabilities
              </Typography>
              <List dense>
                <ListItem>
                  <ListItemText
                    primary="Sprint Analysis"
                    secondary="Velocity trends, capacity planning, risk assessment"
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemText
                    primary="Backlog Optimization"
                    secondary="Story refinement, duplicate detection, prioritization"
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemText
                    primary="Team Insights"
                    secondary="Standup patterns, collaboration analysis, bottlenecks"
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemText
                    primary="Process Improvement"
                    secondary="Agile best practices, workflow optimization"
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AIAssistant;