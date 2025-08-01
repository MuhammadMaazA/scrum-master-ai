import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Add as AddIcon,
  SmartToy as AIIcon,
  Schedule as ScheduleIcon,
  Chat as ChatIcon,
  Send as SendIcon,
  Refresh as RefreshIcon,
  CheckCircle,
  Warning,
  Group,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { teamsAPI, standupAPI } from '../services/api';
import { StandupSummary, StandupEntryForm, Team } from '../types';

const Standups: React.FC = () => {
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);
  const [entryDialogOpen, setEntryDialogOpen] = useState(false);
  const [generateDialogOpen, setGenerateDialogOpen] = useState(false);
  const [slackChannelId, setSlackChannelId] = useState('');
  const [standupEntry, setStandupEntry] = useState<StandupEntryForm>({
    yesterday_work: '',
    today_plan: '',
    blockers: '',
    additional_notes: '',
  });

  const queryClient = useQueryClient();

  // Fetch teams
  const { data: teams } = useQuery('teams', teamsAPI.getTeams);

  // Fetch standup summaries for selected team
  const { data: standupSummaries, isLoading: summariesLoading } = useQuery(
    ['standups', selectedTeam?.id],
    () => selectedTeam ? standupAPI.getTeamStandupSummaries(selectedTeam.id, 10) : Promise.resolve([]),
    { enabled: !!selectedTeam }
  );

  // Create standup entry mutation
  const createEntryMutation = useMutation(
    ({ teamId, entry }: { teamId: number; entry: StandupEntryForm }) =>
      standupAPI.createStandupEntry(teamId, entry),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['standups', selectedTeam?.id]);
        setEntryDialogOpen(false);
        setStandupEntry({
          yesterday_work: '',
          today_plan: '',
          blockers: '',
          additional_notes: '',
        });
      },
    }
  );

  // Generate summary mutation
  const generateSummaryMutation = useMutation(
    ({ teamId, options }: { teamId: number; options: any }) =>
      standupAPI.generateStandupSummary(teamId, options),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['standups', selectedTeam?.id]);
        setGenerateDialogOpen(false);
      },
    }
  );

  // Send reminder mutation
  const sendReminderMutation = useMutation(
    ({ teamId, channelId }: { teamId: number; channelId: string }) =>
      standupAPI.sendStandupReminder(teamId, channelId),
  );

  const handleCreateEntry = () => {
    if (selectedTeam) {
      createEntryMutation.mutate({
        teamId: selectedTeam.id,
        entry: standupEntry,
      });
    }
  };

  const handleGenerateSummary = () => {
    if (selectedTeam) {
      generateSummaryMutation.mutate({
        teamId: selectedTeam.id,
        options: {
          include_jira_updates: true,
          slack_channel_id: slackChannelId || undefined,
        },
      });
    }
  };

  const handleSendReminder = () => {
    if (selectedTeam && slackChannelId) {
      sendReminderMutation.mutate({
        teamId: selectedTeam.id,
        channelId: slackChannelId,
      });
    }
  };

  // Set default team
  React.useEffect(() => {
    if (teams && teams.length > 0 && !selectedTeam) {
      setSelectedTeam(teams[0]);
      setSlackChannelId(teams[0].slack_channel_name || '');
    }
  }, [teams, selectedTeam]);

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            Daily Standups
          </Typography>
          <Typography variant="body1" color="text.secondary">
            AI-powered standup coordination and summaries
          </Typography>
        </Box>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={() => setEntryDialogOpen(true)}
            disabled={!selectedTeam}
          >
            Add Entry
          </Button>
          <Button
            variant="contained"
            startIcon={<AIIcon />}
            onClick={() => setGenerateDialogOpen(true)}
            disabled={!selectedTeam}
          >
            Generate Summary
          </Button>
        </Box>
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
              onClick={() => {
                setSelectedTeam(team);
                setSlackChannelId(team.slack_channel_name || '');
              }}
              variant={selectedTeam?.id === team.id ? "filled" : "outlined"}
              color={selectedTeam?.id === team.id ? "primary" : "default"}
              size="medium"
            />
          ))}
        </Box>
      </Box>

      {selectedTeam && (
        <>
          {/* Team Info */}
          <Alert severity="info" sx={{ mb: 3 }}>
            <strong>{selectedTeam.name}</strong> • 
            Standup time: {selectedTeam.standup_time} • 
            Auto-standup: {selectedTeam.auto_standup_enabled ? 'Enabled' : 'Disabled'} •
            Slack: {selectedTeam.slack_channel_name || 'Not configured'}
          </Alert>

          {/* Quick Actions */}
          <Grid container spacing={2} mb={3}>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <ScheduleIcon color="primary" sx={{ mr: 1 }} />
                    <Typography variant="h6">Send Reminder</Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Send standup reminder to the team
                  </Typography>
                  <Button
                    variant="outlined"
                    fullWidth
                    startIcon={<SendIcon />}
                    onClick={handleSendReminder}
                    disabled={!slackChannelId || sendReminderMutation.isLoading}
{/* loading={sendReminderMutation.isLoading} */}
                  >
                    Send Reminder
                  </Button>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <ChatIcon color="secondary" sx={{ mr: 1 }} />
                    <Typography variant="h6">Collect from Slack</Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Gather standup messages from Slack
                  </Typography>
                  <Button
                    variant="outlined"
                    fullWidth
                    startIcon={<RefreshIcon />}
                    onClick={() => {
                      if (selectedTeam && slackChannelId) {
                        standupAPI.collectSlackMessages(selectedTeam.id, slackChannelId)
                          .then(() => queryClient.invalidateQueries(['standups', selectedTeam.id]));
                      }
                    }}
                    disabled={!slackChannelId}
                  >
                    Collect Messages
                  </Button>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <AIIcon color="success" sx={{ mr: 1 }} />
                    <Typography variant="h6">AI Summary</Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Generate intelligent summary
                  </Typography>
                  <Button
                    variant="contained"
                    fullWidth
                    startIcon={<AIIcon />}
                    onClick={() => setGenerateDialogOpen(true)}
                    color="secondary"
                  >
                    Generate Now
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Standup Summaries */}
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">Recent Standup Summaries</Typography>
                <IconButton 
                  onClick={() => queryClient.invalidateQueries(['standups', selectedTeam.id])}
                  disabled={summariesLoading}
                >
                  <RefreshIcon />
                </IconButton>
              </Box>

              {summariesLoading ? (
                <Box textAlign="center" py={4}>
                  <CircularProgress />
                </Box>
              ) : standupSummaries && standupSummaries.length > 0 ? (
                <List>
                  {standupSummaries.map((summary, index) => (
                    <React.Fragment key={summary.id}>
                      <ListItem alignItems="flex-start">
                        <ListItemIcon>
                          <Box display="flex" flexDirection="column" alignItems="center">
                            {summary.status === 'published' ? (
                              <CheckCircle color="success" />
                            ) : (
                              <Warning color="warning" />
                            )}
                            <Typography variant="caption" color="text.secondary">
                              {new Date(summary.summary_date).toLocaleDateString()}
                            </Typography>
                          </Box>
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Box>
                              <Typography variant="subtitle1" fontWeight="bold">
                                Daily Standup Summary
                              </Typography>
                              <Box display="flex" gap={1} mt={1} mb={2}>
                                <Chip 
                                  label={summary.status}
                                  color={summary.status === 'published' ? 'success' : 'warning'}
                                  size="small"
                                />
                                <Chip 
                                  icon={<Group />}
                                  label={`${summary.participants_count} participants`}
                                  variant="outlined"
                                  size="small"
                                />
                                {summary.posted_to_slack && (
                                  <Chip 
                                    label="Posted to Slack"
                                    color="info"
                                    size="small"
                                  />
                                )}
                              </Box>
                            </Box>
                          }
                          secondary={
                            <Box>
                              <Typography variant="body2" paragraph>
                                {summary.summary_text}
                              </Typography>
                              
                              {summary.key_achievements.length > 0 && (
                                <Box mb={2}>
                                  <Typography variant="subtitle2" gutterBottom>
                                    🏆 Key Achievements:
                                  </Typography>
                                  {summary.key_achievements.map((achievement, idx) => (
                                    <Typography key={idx} variant="body2" sx={{ ml: 2 }}>
                                      • {achievement}
                                    </Typography>
                                  ))}
                                </Box>
                              )}

                              {summary.active_blockers.length > 0 && (
                                <Box mb={2}>
                                  <Typography variant="subtitle2" gutterBottom>
                                    🚫 Active Blockers:
                                  </Typography>
                                  {summary.active_blockers.map((blocker, idx) => (
                                    <Typography key={idx} variant="body2" sx={{ ml: 2 }}>
                                      • {blocker.description}
                                    </Typography>
                                  ))}
                                </Box>
                              )}

                              {summary.focus_areas.length > 0 && (
                                <Box>
                                  <Typography variant="subtitle2" gutterBottom>
                                    🎯 Today's Focus:
                                  </Typography>
                                  {summary.focus_areas.map((focus, idx) => (
                                    <Typography key={idx} variant="body2" sx={{ ml: 2 }}>
                                      • {focus}
                                    </Typography>
                                  ))}
                                </Box>
                              )}
                            </Box>
                          }
                        />
                      </ListItem>
                      {index < standupSummaries.length - 1 && <Divider />}
                    </React.Fragment>
                  ))}
                </List>
              ) : (
                <Box textAlign="center" py={4}>
                  <Typography color="text.secondary" gutterBottom>
                    No standup summaries yet
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Generate your first AI-powered standup summary
                  </Typography>
                  <Button 
                    variant="outlined" 
                    startIcon={<AIIcon />}
                    onClick={() => setGenerateDialogOpen(true)}
                  >
                    Generate Summary
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </>
      )}

      {/* Add Entry Dialog */}
      <Dialog 
        open={entryDialogOpen} 
        onClose={() => setEntryDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Add Standup Entry</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={3} mt={2}>
            <TextField
              label="What did you complete yesterday?"
              multiline
              rows={3}
              value={standupEntry.yesterday_work}
              onChange={(e) => setStandupEntry({ ...standupEntry, yesterday_work: e.target.value })}
              fullWidth
            />
            <TextField
              label="What are you planning to do today?"
              multiline
              rows={3}
              value={standupEntry.today_plan}
              onChange={(e) => setStandupEntry({ ...standupEntry, today_plan: e.target.value })}
              fullWidth
            />
            <TextField
              label="Any blockers or impediments?"
              multiline
              rows={2}
              value={standupEntry.blockers}
              onChange={(e) => setStandupEntry({ ...standupEntry, blockers: e.target.value })}
              fullWidth
            />
            <TextField
              label="Additional notes (optional)"
              multiline
              rows={2}
              value={standupEntry.additional_notes}
              onChange={(e) => setStandupEntry({ ...standupEntry, additional_notes: e.target.value })}
              fullWidth
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEntryDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleCreateEntry} 
            variant="contained"
            disabled={createEntryMutation.isLoading || (!standupEntry.yesterday_work && !standupEntry.today_plan)}
          >
            {createEntryMutation.isLoading ? 'Saving...' : 'Save Entry'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Generate Summary Dialog */}
      <Dialog 
        open={generateDialogOpen} 
        onClose={() => setGenerateDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Generate AI Standup Summary</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={3} mt={2}>
            <Alert severity="info">
              The AI will analyze recent standup entries and Jira updates to create an intelligent summary.
            </Alert>
            <TextField
              label="Slack Channel ID (optional)"
              value={slackChannelId}
              onChange={(e) => setSlackChannelId(e.target.value)}
              fullWidth
              helperText="If provided, the summary will be posted to this Slack channel"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setGenerateDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleGenerateSummary} 
            variant="contained"
            disabled={generateSummaryMutation.isLoading}
            startIcon={<AIIcon />}
          >
            {generateSummaryMutation.isLoading ? 'Generating...' : 'Generate Summary'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Standups;