import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Alert,
  CircularProgress,
  LinearProgress,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  TrendingUp,
  Speed,
  Assignment,
  Group,
  Warning,
  CheckCircle,
  Refresh,
  SmartToy,
} from '@mui/icons-material';
import { useQuery } from 'react-query';
import { teamsAPI, sprintsAPI, standupAPI, aiAPI } from '../services/api';
import { Team, Sprint, StandupSummary } from '../types';

const Dashboard: React.FC = () => {
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);

  // Fetch teams
  const { data: teams, isLoading: teamsLoading } = useQuery(
    'teams',
    teamsAPI.getTeams
  );

  // Fetch current sprint for selected team
  const { data: sprints, isLoading: sprintsLoading } = useQuery(
    ['sprints', selectedTeam?.id],
    () => selectedTeam ? sprintsAPI.getTeamSprints(selectedTeam.id) : Promise.resolve([]),
    { enabled: !!selectedTeam }
  );

  // Fetch recent standup summaries
  const { data: standupSummaries, isLoading: standupLoading } = useQuery(
    ['standups', selectedTeam?.id],
    () => selectedTeam ? standupAPI.getTeamStandupSummaries(selectedTeam.id, 5) : Promise.resolve([]),
    { enabled: !!selectedTeam }
  );

  // Fetch AI health
  const { data: aiHealth, isLoading: aiHealthLoading } = useQuery(
    'ai-health',
    aiAPI.healthCheck
  );

  // Set default team
  useEffect(() => {
    if (teams && teams.length > 0 && !selectedTeam) {
      setSelectedTeam(teams[0]);
    }
  }, [teams, selectedTeam]);

  const activeSprint = sprints?.find(sprint => sprint.status === 'active');
  const latestStandup = standupSummaries?.[0];

  if (teamsLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            Team Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            AI-powered insights for your agile team
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<SmartToy />}
          color="secondary"
          onClick={() => window.location.href = '/ai-assistant'}
        >
          Ask AI Assistant
        </Button>
      </Box>

      {/* Team Selector */}
      <Box mb={3}>
        <Typography variant="h6" gutterBottom>
          Select Team
        </Typography>
        <Box display="flex" gap={2} flexWrap="wrap">
          {teams?.map((team) => (
            <Chip
              key={team.id}
              label={team.name}
              onClick={() => setSelectedTeam(team)}
              variant={selectedTeam?.id === team.id ? "filled" : "outlined"}
              color={selectedTeam?.id === team.id ? "primary" : "default"}
              size="medium"
            />
          ))}
        </Box>
      </Box>

      {selectedTeam && (
        <>
          {/* AI Status Alert */}
          <Alert 
            severity={aiHealth?.ai_service === 'operational' ? 'success' : 'warning'}
            action={
              <IconButton size="small" onClick={() => window.location.reload()}>
                <Refresh />
              </IconButton>
            }
            sx={{ mb: 3 }}
          >
            <strong>AI Status:</strong> {aiHealth?.ai_service === 'operational' 
              ? 'All AI services are running smoothly' 
              : 'Some AI services may be limited'}
          </Alert>

          {/* Key Metrics Cards */}
          <Grid container spacing={3} mb={3}>
            {/* Active Sprint */}
            <Grid item xs={12} md={6} lg={3}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <TrendingUp color="primary" sx={{ mr: 1 }} />
                    <Typography variant="h6">Active Sprint</Typography>
                  </Box>
                  {activeSprint ? (
                    <>
                      <Typography variant="h4" fontWeight="bold" color="primary">
                        {activeSprint.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {activeSprint.goal}
                      </Typography>
                      <Box mt={2}>
                        <Typography variant="caption" display="block">
                          Progress: {Math.round((activeSprint.actual_velocity / activeSprint.planned_capacity) * 100)}%
                        </Typography>
                        <LinearProgress 
                          variant="determinate" 
                          value={Math.min((activeSprint.actual_velocity / activeSprint.planned_capacity) * 100, 100)}
                          sx={{ mt: 1 }}
                        />
                      </Box>
                    </>
                  ) : (
                    <Typography color="text.secondary">
                      No active sprint
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* Team Status */}
            <Grid item xs={12} md={6} lg={3}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Group color="success" sx={{ mr: 1 }} />
                    <Typography variant="h6">Team Status</Typography>
                  </Box>
                  <Typography variant="h4" fontWeight="bold" color="success.main">
                    {selectedTeam.team_size}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Active Members
                  </Typography>
                  <Box mt={2}>
                    <Chip 
                      label={selectedTeam.is_active ? "Active" : "Inactive"} 
                      color={selectedTeam.is_active ? "success" : "error"}
                      size="small"
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* AI Automation */}
            <Grid item xs={12} md={6} lg={3}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Speed color="secondary" sx={{ mr: 1 }} />
                    <Typography variant="h6">AI Automation</Typography>
                  </Box>
                  <Typography variant="h4" fontWeight="bold" color="secondary.main">
                    {selectedTeam.auto_standup_enabled ? '✓' : '○'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Auto Standups
                  </Typography>
                  <Box mt={2}>
                    <Chip 
                      label={`Tone: ${selectedTeam.ai_tone}`}
                      variant="outlined"
                      size="small"
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            {/* Latest Standup */}
            <Grid item xs={12} md={6} lg={3}>
              <Card sx={{ height: '100%' }}>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Assignment color="info" sx={{ mr: 1 }} />
                    <Typography variant="h6">Latest Standup</Typography>
                  </Box>
                  {latestStandup ? (
                    <>
                      <Typography variant="body2" fontWeight="bold">
                        {new Date(latestStandup.summary_date).toLocaleDateString()}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" display="block">
                        {latestStandup.participants_count} participants
                      </Typography>
                      <Box mt={1}>
                        <Chip 
                          label={latestStandup.status}
                          color={latestStandup.status === 'published' ? 'success' : 'warning'}
                          size="small"
                        />
                      </Box>
                    </>
                  ) : (
                    <Typography color="text.secondary">
                      No recent standups
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Recent Activity */}
          <Grid container spacing={3}>
            {/* Standup Summary */}
            <Grid item xs={12} lg={8}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="between" alignItems="center" mb={2}>
                    <Typography variant="h6">Latest Standup Summary</Typography>
                    <Button 
                      size="small" 
                      onClick={() => window.location.href = '/standups'}
                    >
                      View All
                    </Button>
                  </Box>
                  {standupLoading ? (
                    <CircularProgress size={24} />
                  ) : latestStandup ? (
                    <Box>
                      <Typography variant="body1" paragraph>
                        {latestStandup.summary_text}
                      </Typography>
                      
                      {latestStandup.key_achievements.length > 0 && (
                        <Box mb={2}>
                          <Typography variant="subtitle2" gutterBottom>
                            🏆 Key Achievements:
                          </Typography>
                          {latestStandup.key_achievements.map((achievement, index) => (
                            <Typography key={index} variant="body2" sx={{ ml: 2 }}>
                              • {achievement}
                            </Typography>
                          ))}
                        </Box>
                      )}

                      {latestStandup.active_blockers.length > 0 && (
                        <Box mb={2}>
                          <Typography variant="subtitle2" gutterBottom>
                            🚫 Active Blockers:
                          </Typography>
                          {latestStandup.active_blockers.map((blocker, index) => (
                            <Typography key={index} variant="body2" sx={{ ml: 2 }}>
                              • {blocker.description}
                            </Typography>
                          ))}
                        </Box>
                      )}

                      <Box display="flex" alignItems="center" gap={1} mt={2}>
                        <Chip 
                          icon={latestStandup.posted_to_slack ? <CheckCircle /> : <Warning />}
                          label={latestStandup.posted_to_slack ? "Posted to Slack" : "Pending"}
                          color={latestStandup.posted_to_slack ? "success" : "warning"}
                          size="small"
                        />
                        <Typography variant="caption" color="text.secondary">
                          Generated by AI • {new Date(latestStandup.summary_date).toLocaleString()}
                        </Typography>
                      </Box>
                    </Box>
                  ) : (
                    <Box textAlign="center" py={4}>
                      <Typography color="text.secondary" gutterBottom>
                        No standup summaries yet
                      </Typography>
                      <Button 
                        variant="outlined" 
                        onClick={() => window.location.href = '/standups'}
                      >
                        Generate First Standup
                      </Button>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>

            {/* Quick Actions */}
            <Grid item xs={12} lg={4}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Quick Actions
                  </Typography>
                  <Box display="flex" flexDirection="column" gap={2}>
                    <Button 
                      variant="outlined" 
                      fullWidth
                      startIcon={<Assignment />}
                      onClick={() => window.location.href = '/standups'}
                    >
                      Generate Standup Summary
                    </Button>
                    <Button 
                      variant="outlined" 
                      fullWidth
                      startIcon={<TrendingUp />}
                      onClick={() => window.location.href = '/sprints'}
                    >
                      Plan Next Sprint
                    </Button>
                    <Button 
                      variant="outlined" 
                      fullWidth
                      startIcon={<Speed />}
                      onClick={() => window.location.href = '/backlog'}
                    >
                      Analyze Backlog
                    </Button>
                    <Button 
                      variant="outlined" 
                      fullWidth
                      startIcon={<SmartToy />}
                      onClick={() => window.location.href = '/ai-assistant'}
                    >
                      Ask AI Assistant
                    </Button>
                  </Box>

                  <Box mt={3}>
                    <Typography variant="subtitle2" gutterBottom>
                      AI Insights
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {activeSprint 
                        ? `Your team is ${activeSprint.actual_velocity >= activeSprint.planned_capacity * 0.8 ? 'on track' : 'falling behind'} this sprint.`
                        : 'Start a new sprint to get AI insights.'}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </>
      )}
    </Box>
  );
};

export default Dashboard;