import React, { useState, useEffect } from 'react';
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
  Checkbox,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  LinearProgress,
  Stepper,
  Step,
  StepLabel,
  StepContent,
} from '@mui/material';
import {
  PlayArrow as StartIcon,
  SmartToy as AIIcon,
  Timeline as SprintIcon,
  Assignment as TaskIcon,
  TrendingUp as VelocityIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Lightbulb as InsightIcon,
  DragIndicator as DragIcon,
  Add as AddIcon,
  Remove as RemoveIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { teamsAPI, sprintsAPI, backlogAPI, sprintPlanningAPI } from '@/services/api';
import { Team, Sprint, BacklogItem, SprintForm, SprintPlanSuggestion } from '@/types';

const SprintPlanning: React.FC = () => {
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);
  const [activeStep, setActiveStep] = useState(0);
  const [sprintForm, setSprintForm] = useState<SprintForm>({
    name: '',
    goal: '',
    start_date: '',
    end_date: '',
    planned_capacity: 0,
    team_capacity_days: 0,
  });
  const [selectedItems, setSelectedItems] = useState<Set<number>>(new Set());
  const [aiSuggestion, setAiSuggestion] = useState<SprintPlanSuggestion | null>(null);
  const [sprintGoalContext, setSprintGoalContext] = useState('');
  const [showAiDialog, setShowAiDialog] = useState(false);

  const queryClient = useQueryClient();

  // Fetch teams
  const { data: teams } = useQuery('teams', teamsAPI.getTeams);

  // Fetch team sprints
  const { data: sprints } = useQuery(
    ['sprints', selectedTeam?.id],
    () => selectedTeam ? sprintsAPI.getTeamSprints(selectedTeam.id) : Promise.resolve([]),
    { enabled: !!selectedTeam }
  );

  // Fetch backlog items
  const { data: backlogItems, isLoading: backlogLoading } = useQuery(
    ['backlog', selectedTeam?.id],
    () => {
      if (!selectedTeam) return Promise.resolve([]);
      // Assuming we get project from team (simplified for MVP)
      return backlogAPI.getProjectBacklog(1, { status: ['todo'] }); // Use project ID 1 for MVP
    },
    { enabled: !!selectedTeam }
  );

  // Fetch team velocity
  const { data: velocityData } = useQuery(
    ['velocity', selectedTeam?.id],
    () => selectedTeam ? sprintPlanningAPI.getTeamVelocity(selectedTeam.id) : Promise.resolve(null),
    { enabled: !!selectedTeam }
  );

  // Generate AI suggestion mutation
  const generateSuggestionMutation = useMutation(
    ({
      teamId,
      items,
      capacity,
      context,
    }: {
      teamId: number;
      items: BacklogItem[];
      capacity: { velocity: number; days: number };
      context?: string;
    }) => sprintPlanningAPI.suggestSprintPlan(teamId, items, capacity, context),
    {
      onSuccess: (suggestion) => {
        setAiSuggestion(suggestion);
        setSelectedItems(new Set(suggestion.recommended_items));
        setSprintForm(prev => ({
          ...prev,
          goal: suggestion.sprint_goal,
          planned_capacity: suggestion.total_story_points,
        }));
        setShowAiDialog(true);
      },
    }
  );

  // Create sprint mutation
  const createSprintMutation = useMutation(
    ({ teamId, sprint, items }: { teamId: number; sprint: SprintForm; items: number[] }) =>
      sprintPlanningAPI.createSprintFromPlan(teamId, sprint, items),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['sprints', selectedTeam?.id]);
        setActiveStep(0);
        resetForm();
      },
    }
  );

  const resetForm = () => {
    setSprintForm({
      name: '',
      goal: '',
      start_date: '',
      end_date: '',
      planned_capacity: 0,
      team_capacity_days: 0,
    });
    setSelectedItems(new Set());
    setAiSuggestion(null);
    setSprintGoalContext('');
  };

  const handleItemToggle = (itemId: number) => {
    const newSelected = new Set(selectedItems);
    if (newSelected.has(itemId)) {
      newSelected.delete(itemId);
    } else {
      newSelected.add(itemId);
    }
    setSelectedItems(newSelected);
    updateCapacityFromSelection(newSelected);
  };

  const updateCapacityFromSelection = (selected: Set<number>) => {
    const totalPoints = backlogItems
      ?.filter(item => selected.has(item.id))
      .reduce((sum, item) => sum + (item.story_points || 0), 0) || 0;
    
    setSprintForm(prev => ({
      ...prev,
      planned_capacity: totalPoints,
    }));
  };

  const handleGenerateAiSuggestion = () => {
    if (selectedTeam && backlogItems && velocityData) {
      generateSuggestionMutation.mutate({
        teamId: selectedTeam.id,
        items: backlogItems,
        capacity: {
          velocity: velocityData.average_velocity || 20,
          days: sprintForm.team_capacity_days || 10,
        },
        context: sprintGoalContext,
      });
    }
  };

  const handleCreateSprint = () => {
    if (selectedTeam) {
      createSprintMutation.mutate({
        teamId: selectedTeam.id,
        sprint: sprintForm,
        items: Array.from(selectedItems),
      });
    }
  };

  const getCapacityUtilization = () => {
    if (!velocityData?.average_velocity) return 0;
    return (sprintForm.planned_capacity / velocityData.average_velocity) * 100;
  };

  const getCapacityColor = () => {
    const utilization = getCapacityUtilization();
    if (utilization > 100) return 'error';
    if (utilization > 90) return 'warning';
    return 'success';
  };

  // Set default team and sprint dates
  useEffect(() => {
    if (teams && teams.length > 0 && !selectedTeam) {
      setSelectedTeam(teams[0]);
    }
  }, [teams, selectedTeam]);

  useEffect(() => {
    // Set default sprint dates (2 weeks from today)
    const today = new Date();
    const endDate = new Date(today);
    endDate.setDate(today.getDate() + 14);
    
    setSprintForm(prev => ({
      ...prev,
      start_date: today.toISOString().split('T')[0],
      end_date: endDate.toISOString().split('T')[0],
      team_capacity_days: selectedTeam ? selectedTeam.team_size * 10 : 50, // 10 working days per person
    }));
  }, [selectedTeam]);

  const steps = [
    'Setup Sprint Details',
    'Select Backlog Items',
    'Review & Create Sprint',
  ];

  const currentSprint = sprints?.find(sprint => sprint.status === 'active');

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            Sprint Planning
          </Typography>
          <Typography variant="body1" color="text.secondary">
            AI-powered sprint planning and capacity management
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AIIcon />}
          onClick={handleGenerateAiSuggestion}
          disabled={!selectedTeam || !backlogItems || activeStep !== 1}
          color="secondary"
        >
          Get AI Suggestion
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
          {/* Current Sprint Alert */}
          {currentSprint && (
            <Alert severity="info" sx={{ mb: 3 }}>
              <strong>Current Sprint:</strong> {currentSprint.name} is currently active. 
              This planning session will create the next sprint.
            </Alert>
          )}

          {/* Team Velocity Info */}
          {velocityData && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  📊 Team Velocity Insights
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h4" color="primary" fontWeight="bold">
                        {Math.round(velocityData.average_velocity)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Average Velocity (Story Points)
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h4" color="success.main" fontWeight="bold">
                        {velocityData.max_velocity}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Best Sprint
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h4" color="warning.main" fontWeight="bold">
                        {velocityData.min_velocity}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Lowest Sprint
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center">
                      <Typography variant="h4" color="info.main" fontWeight="bold">
                        {velocityData.sprint_count}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Sprints Analyzed
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          )}

          {/* Sprint Planning Stepper */}
          <Card>
            <CardContent>
              <Stepper activeStep={activeStep} orientation="vertical">
                {/* Step 1: Sprint Setup */}
                <Step>
                  <StepLabel>
                    <Typography variant="h6">Setup Sprint Details</Typography>
                  </StepLabel>
                  <StepContent>
                    <Grid container spacing={3}>
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="Sprint Name"
                          value={sprintForm.name}
                          onChange={(e) => setSprintForm({ ...sprintForm, name: e.target.value })}
                          placeholder="e.g., Sprint 16"
                        />
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="Team Capacity (Person-Days)"
                          type="number"
                          value={sprintForm.team_capacity_days}
                          onChange={(e) => setSprintForm({ ...sprintForm, team_capacity_days: parseInt(e.target.value) })}
                        />
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="Start Date"
                          type="date"
                          value={sprintForm.start_date}
                          onChange={(e) => setSprintForm({ ...sprintForm, start_date: e.target.value })}
                          InputLabelProps={{ shrink: true }}
                        />
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label="End Date"
                          type="date"
                          value={sprintForm.end_date}
                          onChange={(e) => setSprintForm({ ...sprintForm, end_date: e.target.value })}
                          InputLabelProps={{ shrink: true }}
                        />
                      </Grid>
                      <Grid item xs={12}>
                        <TextField
                          fullWidth
                          label="Sprint Goal Context (for AI suggestions)"
                          multiline
                          rows={3}
                          value={sprintGoalContext}
                          onChange={(e) => setSprintGoalContext(e.target.value)}
                          placeholder="e.g., Focus on user authentication and payment features"
                        />
                      </Grid>
                    </Grid>
                    <Box mt={2}>
                      <Button
                        variant="contained"
                        onClick={() => setActiveStep(1)}
                        disabled={!sprintForm.name || !sprintForm.start_date || !sprintForm.end_date}
                      >
                        Continue
                      </Button>
                    </Box>
                  </StepContent>
                </Step>

                {/* Step 2: Select Items */}
                <Step>
                  <StepLabel>
                    <Typography variant="h6">Select Backlog Items</Typography>
                  </StepLabel>
                  <StepContent>
                    <Box mb={2}>
                      <Alert severity="info">
                        Current selection: {selectedItems.size} items, {sprintForm.planned_capacity} story points
                        {velocityData && (
                          <Box mt={1}>
                            <LinearProgress 
                              variant="determinate"
                              value={Math.min(getCapacityUtilization(), 100)}
                              color={getCapacityColor()}
                              sx={{ height: 8, borderRadius: 4 }}
                            />
                            <Typography variant="caption" display="block" mt={1}>
                              Capacity utilization: {Math.round(getCapacityUtilization())}% 
                              (Target: 80-90%)
                            </Typography>
                          </Box>
                        )}
                      </Alert>
                    </Box>

                    {backlogLoading ? (
                      <Box textAlign="center" py={4}>
                        <CircularProgress />
                      </Box>
                    ) : backlogItems && backlogItems.length > 0 ? (
                      <List>
                        {backlogItems.map((item) => (
                          <ListItem key={item.id} divider>
                            <ListItemIcon>
                              <Checkbox
                                checked={selectedItems.has(item.id)}
                                onChange={() => handleItemToggle(item.id)}
                              />
                            </ListItemIcon>
                            <ListItemText
                              primary={
                                <Box display="flex" alignItems="center" gap={1}>
                                  <Typography variant="subtitle1" fontWeight="bold">
                                    {item.title}
                                  </Typography>
                                  <Chip 
                                    label={`${item.story_points || '?'} pts`}
                                    size="small"
                                    color="primary"
                                    variant="outlined"
                                  />
                                  <Chip 
                                    label={item.priority}
                                    size="small"
                                    color={
                                      item.priority === 'critical' || item.priority === 'high' ? 'error' :
                                      item.priority === 'medium' ? 'warning' : 'default'
                                    }
                                  />
                                </Box>
                              }
                              secondary={
                                <Typography variant="body2" color="text.secondary" noWrap>
                                  {item.description}
                                </Typography>
                              }
                            />
                          </ListItem>
                        ))}
                      </List>
                    ) : (
                      <Alert severity="warning">
                        No backlog items available. Please add items to the backlog first.
                      </Alert>
                    )}

                    <Box mt={2} display="flex" gap={2}>
                      <Button onClick={() => setActiveStep(0)}>
                        Back
                      </Button>
                      <Button
                        variant="contained"
                        onClick={() => setActiveStep(2)}
                        disabled={selectedItems.size === 0}
                      >
                        Continue
                      </Button>
                      <Button
                        variant="outlined"
                        startIcon={<AIIcon />}
                        onClick={handleGenerateAiSuggestion}
                        disabled={!backlogItems || generateSuggestionMutation.isLoading}
                        color="secondary"
                      >
                        {generateSuggestionMutation.isLoading ? 'Generating...' : 'Get AI Suggestion'}
                      </Button>
                    </Box>
                  </StepContent>
                </Step>

                {/* Step 3: Review & Create */}
                <Step>
                  <StepLabel>
                    <Typography variant="h6">Review & Create Sprint</Typography>
                  </StepLabel>
                  <StepContent>
                    <Grid container spacing={3}>
                      <Grid item xs={12} md={8}>
                        <TextField
                          fullWidth
                          label="Sprint Goal"
                          multiline
                          rows={3}
                          value={sprintForm.goal}
                          onChange={(e) => setSprintForm({ ...sprintForm, goal: e.target.value })}
                          placeholder="Define the sprint goal..."
                        />
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <Card variant="outlined">
                          <CardContent>
                            <Typography variant="h6" gutterBottom>
                              Sprint Summary
                            </Typography>
                            <Typography variant="body2" gutterBottom>
                              <strong>Items:</strong> {selectedItems.size}
                            </Typography>
                            <Typography variant="body2" gutterBottom>
                              <strong>Story Points:</strong> {sprintForm.planned_capacity}
                            </Typography>
                            <Typography variant="body2" gutterBottom>
                              <strong>Duration:</strong> {Math.ceil((new Date(sprintForm.end_date).getTime() - new Date(sprintForm.start_date).getTime()) / (1000 * 60 * 60 * 24))} days
                            </Typography>
                            {velocityData && (
                              <Typography variant="body2" color={getCapacityColor() + '.main'}>
                                <strong>Capacity:</strong> {Math.round(getCapacityUtilization())}%
                              </Typography>
                            )}
                          </CardContent>
                        </Card>
                      </Grid>
                    </Grid>

                    {/* AI Insights */}
                    {aiSuggestion && (
                      <Alert severity="info" sx={{ mt: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          🤖 AI Insights:
                        </Typography>
                        {aiSuggestion.risks.map((risk, index) => (
                          <Typography key={index} variant="body2">
                            • {risk}
                          </Typography>
                        ))}
                      </Alert>
                    )}

                    <Box mt={3} display="flex" gap={2}>
                      <Button onClick={() => setActiveStep(1)}>
                        Back
                      </Button>
                      <Button
                        variant="contained"
                        startIcon={<StartIcon />}
                        onClick={handleCreateSprint}
                        disabled={createSprintMutation.isLoading || !sprintForm.goal || selectedItems.size === 0}
                        color="success"
                        size="large"
                      >
                        {createSprintMutation.isLoading ? 'Creating Sprint...' : 'Create Sprint'}
                      </Button>
                    </Box>
                  </StepContent>
                </Step>
              </Stepper>
            </CardContent>
          </Card>
        </>
      )}

      {/* AI Suggestion Dialog */}
      <Dialog 
        open={showAiDialog} 
        onClose={() => setShowAiDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <AIIcon color="secondary" />
            AI Sprint Planning Suggestion
          </Box>
        </DialogTitle>
        <DialogContent>
          {aiSuggestion && (
            <Box display="flex" flexDirection="column" gap={3} mt={2}>
              <Alert severity="success">
                <Typography variant="subtitle2">
                  ✨ AI has analyzed your backlog and team capacity
                </Typography>
              </Alert>

              <Box>
                <Typography variant="h6" gutterBottom>
                  🎯 Suggested Sprint Goal
                </Typography>
                <Typography variant="body1" sx={{ 
                  p: 2, 
                  bgcolor: 'grey.50', 
                  borderRadius: 1,
                  fontStyle: 'italic' 
                }}>
                  "{aiSuggestion.sprint_goal}"
                </Typography>
              </Box>

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="h6" color="primary">
                    {aiSuggestion.recommended_items.length}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Recommended Items
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="h6" color="success.main">
                    {aiSuggestion.total_story_points}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Story Points
                  </Typography>
                </Grid>
              </Grid>

              <Box>
                <Typography variant="h6" gutterBottom>
                  📊 Capacity Analysis
                </Typography>
                <LinearProgress 
                  variant="determinate"
                  value={aiSuggestion.capacity_utilization}
                  color={aiSuggestion.capacity_utilization > 90 ? 'warning' : 'success'}
                  sx={{ height: 8, borderRadius: 4, mb: 1 }}
                />
                <Typography variant="body2" color="text.secondary">
                  {Math.round(aiSuggestion.capacity_utilization)}% capacity utilization
                </Typography>
              </Box>

              {aiSuggestion.risks.length > 0 && (
                <Box>
                  <Typography variant="h6" gutterBottom color="warning.main">
                    ⚠️ Identified Risks
                  </Typography>
                  {aiSuggestion.risks.map((risk, index) => (
                    <Typography key={index} variant="body2" paragraph>
                      • {risk}
                    </Typography>
                  ))}
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowAiDialog(false)}>
            Dismiss
          </Button>
          <Button 
            variant="contained"
            onClick={() => {
              setShowAiDialog(false);
              setActiveStep(2); // Go to review step
            }}
            color="secondary"
          >
            Accept Suggestion
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SprintPlanning;