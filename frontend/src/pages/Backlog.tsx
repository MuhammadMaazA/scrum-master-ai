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
  IconButton,
  Tooltip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Add as AddIcon,
  SmartToy as AIIcon,
  Analysis as AnalysisIcon,
  AutoFixHigh as AutoFixIcon,
  ExpandMore as ExpandMoreIcon,
  Refresh as RefreshIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Lightbulb as LightbulbIcon,
  ContentCopy as DuplicateIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { projectsAPI, backlogAPI } from '@/services/api';
import { BacklogItem, BacklogItemForm, BacklogAnalysis, Project, BacklogFilters } from '@/types';

const Backlog: React.FC = () => {
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<BacklogItem | null>(null);
  const [analysisDialogOpen, setAnalysisDialogOpen] = useState(false);
  const [selectedAnalysis, setSelectedAnalysis] = useState<BacklogAnalysis | null>(null);
  const [filters, setFilters] = useState<BacklogFilters>({});
  const [bulkAnalysisRunning, setBulkAnalysisRunning] = useState(false);
  const [newItem, setNewItem] = useState<BacklogItemForm>({
    title: '',
    description: '',
    item_type: 'story',
    priority: 'medium',
    story_points: undefined,
    business_value: undefined,
    assignee_id: undefined,
  });

  const queryClient = useQueryClient();

  // Fetch projects
  const { data: projects } = useQuery('projects', projectsAPI.getProjects);

  // Fetch backlog items for selected project
  const { data: backlogItems, isLoading: itemsLoading } = useQuery(
    ['backlog', selectedProject?.id, filters],
    () => selectedProject ? backlogAPI.getProjectBacklog(selectedProject.id, filters) : Promise.resolve([]),
    { enabled: !!selectedProject }
  );

  // Create item mutation
  const createItemMutation = useMutation(
    ({ projectId, item }: { projectId: number; item: BacklogItemForm }) =>
      backlogAPI.createBacklogItem(projectId, item),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['backlog', selectedProject?.id]);
        setCreateDialogOpen(false);
        resetNewItem();
      },
    }
  );

  // Update item mutation
  const updateItemMutation = useMutation(
    ({ itemId, item }: { itemId: number; item: Partial<BacklogItemForm> }) =>
      backlogAPI.updateBacklogItem(itemId, item),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['backlog', selectedProject?.id]);
        setEditingItem(null);
      },
    }
  );

  // Analyze item mutation
  const analyzeItemMutation = useMutation(
    (item: { title: string; description: string; item_type: string }) =>
      backlogAPI.analyzeBacklogItem(item),
    {
      onSuccess: (analysis) => {
        setSelectedAnalysis(analysis);
        setAnalysisDialogOpen(true);
      },
    }
  );

  // Bulk analyze mutation
  const bulkAnalyzeMutation = useMutation(
    (projectId: number) => backlogAPI.bulkAnalyzeBacklog(projectId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['backlog', selectedProject?.id]);
        setBulkAnalysisRunning(false);
      },
      onError: () => {
        setBulkAnalysisRunning(false);
      },
    }
  );

  // Apply suggestions mutation
  const applySuggestionsMutation = useMutation(
    ({ itemId, suggestions }: { itemId: number; suggestions: any }) =>
      backlogAPI.applyAISuggestions(itemId, suggestions),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['backlog', selectedProject?.id]);
      },
    }
  );

  const resetNewItem = () => {
    setNewItem({
      title: '',
      description: '',
      item_type: 'story',
      priority: 'medium',
      story_points: undefined,
      business_value: undefined,
      assignee_id: undefined,
    });
  };

  const handleCreateItem = () => {
    if (selectedProject) {
      createItemMutation.mutate({
        projectId: selectedProject.id,
        item: newItem,
      });
    }
  };

  const handleAnalyzeItem = (item: BacklogItem) => {
    analyzeItemMutation.mutate({
      title: item.title,
      description: item.description,
      item_type: item.item_type,
    });
  };

  const handleBulkAnalyze = () => {
    if (selectedProject) {
      setBulkAnalysisRunning(true);
      bulkAnalyzeMutation.mutate(selectedProject.id);
    }
  };

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case 'XS': return 'success';
      case 'S': return 'success';
      case 'M': return 'warning';
      case 'L': return 'warning';
      case 'XL': return 'error';
      default: return 'default';
    }
  };

  const getClarityColor = (score: number) => {
    if (score >= 0.8) return 'success';
    if (score >= 0.6) return 'warning';
    return 'error';
  };

  // Set default project
  useEffect(() => {
    if (projects && projects.length > 0 && !selectedProject) {
      setSelectedProject(projects[0]);
    }
  }, [projects, selectedProject]);

  const itemsNeedingAttention = backlogItems?.filter(item => 
    (item.ai_clarity_score && item.ai_clarity_score < 0.6) ||
    (item.duplicate_candidates && item.duplicate_candidates.length > 0) ||
    !item.story_points
  ) || [];

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" fontWeight="bold" gutterBottom>
            Product Backlog
          </Typography>
          <Typography variant="body1" color="text.secondary">
            AI-enhanced backlog grooming and management
          </Typography>
        </Box>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
            disabled={!selectedProject}
          >
            Add Item
          </Button>
          <Button
            variant="contained"
            startIcon={<AnalysisIcon />}
            onClick={handleBulkAnalyze}
            disabled={!selectedProject || bulkAnalysisRunning}
            color="secondary"
          >
            {bulkAnalysisRunning ? 'Analyzing...' : 'Analyze All'}
          </Button>
        </Box>
      </Box>

      {/* Project Selector */}
      <Box mb={3}>
        <Typography variant="h6" gutterBottom>
          Select Project
        </Typography>
        <Box display="flex" gap={2} flexWrap="wrap">
          {projects?.map((project) => (
            <Chip
              key={project.id}
              label={`${project.name} (${project.key})`}
              onClick={() => setSelectedProject(project)}
              variant={selectedProject?.id === project.id ? "filled" : "outlined"}
              color={selectedProject?.id === project.id ? "primary" : "default"}
              size="medium"
            />
          ))}
        </Box>
      </Box>

      {selectedProject && (
        <>
          {/* AI Insights Panel */}
          {itemsNeedingAttention.length > 0 && (
            <Alert severity="warning" sx={{ mb: 3 }}>
              <strong>AI Insights:</strong> {itemsNeedingAttention.length} items need attention - 
              unclear descriptions, potential duplicates, or missing estimates.
            </Alert>
          )}

          {/* Filters and Controls */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Filters & Bulk Actions
              </Typography>
              <Grid container spacing={2} alignItems="center">
                <Grid item xs={12} sm={6} md={3}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Status</InputLabel>
                    <Select
                      value={filters.status?.[0] || ''}
                      onChange={(e) => setFilters({ 
                        ...filters, 
                        status: e.target.value ? [e.target.value as any] : undefined 
                      })}
                    >
                      <MenuItem value="">All</MenuItem>
                      <MenuItem value="todo">To Do</MenuItem>
                      <MenuItem value="in_progress">In Progress</MenuItem>
                      <MenuItem value="review">Review</MenuItem>
                      <MenuItem value="done">Done</MenuItem>
                      <MenuItem value="blocked">Blocked</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Priority</InputLabel>
                    <Select
                      value={filters.priority?.[0] || ''}
                      onChange={(e) => setFilters({ 
                        ...filters, 
                        priority: e.target.value ? [e.target.value as any] : undefined 
                      })}
                    >
                      <MenuItem value="">All</MenuItem>
                      <MenuItem value="critical">Critical</MenuItem>
                      <MenuItem value="high">High</MenuItem>
                      <MenuItem value="medium">Medium</MenuItem>
                      <MenuItem value="low">Low</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <FormControl fullWidth size="small">
                    <InputLabel>Type</InputLabel>
                    <Select
                      value={filters.item_type?.[0] || ''}
                      onChange={(e) => setFilters({ 
                        ...filters, 
                        item_type: e.target.value ? [e.target.value as any] : undefined 
                      })}
                    >
                      <MenuItem value="">All</MenuItem>
                      <MenuItem value="story">Story</MenuItem>
                      <MenuItem value="bug">Bug</MenuItem>
                      <MenuItem value="task">Task</MenuItem>
                      <MenuItem value="epic">Epic</MenuItem>
                      <MenuItem value="spike">Spike</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <TextField
                    fullWidth
                    size="small"
                    label="Search"
                    value={filters.search || ''}
                    onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                  />
                </Grid>
              </Grid>

              {bulkAnalysisRunning && (
                <Box mt={2}>
                  <Typography variant="body2" gutterBottom>
                    AI Analysis in Progress...
                  </Typography>
                  <LinearProgress />
                </Box>
              )}
            </CardContent>
          </Card>

          {/* Backlog Items Table */}
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">
                  Backlog Items ({backlogItems?.length || 0})
                </Typography>
                <IconButton 
                  onClick={() => queryClient.invalidateQueries(['backlog', selectedProject.id])}
                  disabled={itemsLoading}
                >
                  <RefreshIcon />
                </IconButton>
              </Box>

              {itemsLoading ? (
                <Box textAlign="center" py={4}>
                  <CircularProgress />
                </Box>
              ) : backlogItems && backlogItems.length > 0 ? (
                <TableContainer component={Paper} elevation={0}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Title</TableCell>
                        <TableCell>Type</TableCell>
                        <TableCell>Priority</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Points</TableCell>
                        <TableCell>AI Analysis</TableCell>
                        <TableCell>Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {backlogItems.map((item) => (
                        <TableRow key={item.id}>
                          <TableCell>
                            <Box>
                              <Typography variant="subtitle2" fontWeight="bold">
                                {item.title}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {item.jira_key || `#${item.id}`}
                              </Typography>
                              {item.duplicate_candidates && item.duplicate_candidates.length > 0 && (
                                <Tooltip title="Potential duplicates found">
                                  <DuplicateIcon color="warning" fontSize="small" sx={{ ml: 1 }} />
                                </Tooltip>
                              )}
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Chip 
                              label={item.item_type} 
                              size="small" 
                              variant="outlined"
                            />
                          </TableCell>
                          <TableCell>
                            <Chip 
                              label={item.priority}
                              size="small"
                              color={
                                item.priority === 'critical' || item.priority === 'high' ? 'error' :
                                item.priority === 'medium' ? 'warning' : 'default'
                              }
                            />
                          </TableCell>
                          <TableCell>
                            <Chip 
                              label={item.status}
                              size="small"
                              color={
                                item.status === 'done' ? 'success' :
                                item.status === 'blocked' ? 'error' :
                                item.status === 'in_progress' ? 'info' : 'default'
                              }
                            />
                          </TableCell>
                          <TableCell>
                            <Box display="flex" alignItems="center" gap={1}>
                              <Typography variant="body2">
                                {item.story_points || '?'}
                              </Typography>
                              {item.ai_suggested_points && item.ai_suggested_points !== item.story_points && (
                                <Tooltip title={`AI suggests: ${item.ai_suggested_points}`}>
                                  <Chip 
                                    label={`AI: ${item.ai_suggested_points}`}
                                    size="small"
                                    color="info"
                                    variant="outlined"
                                  />
                                </Tooltip>
                              )}
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Box display="flex" gap={1}>
                              {item.ai_clarity_score && (
                                <Chip
                                  label={`${Math.round(item.ai_clarity_score * 100)}%`}
                                  size="small"
                                  color={getClarityColor(item.ai_clarity_score)}
                                  title="Clarity Score"
                                />
                              )}
                              {item.ai_complexity_score && (
                                <Chip
                                  label={item.estimated_complexity || 'M'}
                                  size="small"
                                  color={getComplexityColor(item.estimated_complexity || 'M')}
                                  variant="outlined"
                                  title="AI Complexity"
                                />
                              )}
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Box display="flex" gap={1}>
                              <Tooltip title="Analyze with AI">
                                <IconButton 
                                  size="small"
                                  onClick={() => handleAnalyzeItem(item)}
                                  disabled={analyzeItemMutation.isLoading}
                                >
                                  <AIIcon />
                                </IconButton>
                              </Tooltip>
                              <Tooltip title="Edit item">
                                <IconButton 
                                  size="small"
                                  onClick={() => setEditingItem(item)}
                                >
                                  <EditIcon />
                                </IconButton>
                              </Tooltip>
                            </Box>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Box textAlign="center" py={4}>
                  <Typography color="text.secondary" gutterBottom>
                    No backlog items yet
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    Create your first backlog item to get started
                  </Typography>
                  <Button 
                    variant="outlined" 
                    startIcon={<AddIcon />}
                    onClick={() => setCreateDialogOpen(true)}
                  >
                    Add First Item
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </>
      )}

      {/* Create Item Dialog */}
      <Dialog 
        open={createDialogOpen} 
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Create Backlog Item</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={3} mt={2}>
            <TextField
              label="Title"
              value={newItem.title}
              onChange={(e) => setNewItem({ ...newItem, title: e.target.value })}
              fullWidth
              required
            />
            <TextField
              label="Description"
              multiline
              rows={4}
              value={newItem.description}
              onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
              fullWidth
            />
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel>Type</InputLabel>
                  <Select
                    value={newItem.item_type}
                    onChange={(e) => setNewItem({ ...newItem, item_type: e.target.value as any })}
                  >
                    <MenuItem value="story">User Story</MenuItem>
                    <MenuItem value="bug">Bug</MenuItem>
                    <MenuItem value="task">Task</MenuItem>
                    <MenuItem value="epic">Epic</MenuItem>
                    <MenuItem value="spike">Spike</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel>Priority</InputLabel>
                  <Select
                    value={newItem.priority}
                    onChange={(e) => setNewItem({ ...newItem, priority: e.target.value as any })}
                  >
                    <MenuItem value="critical">Critical</MenuItem>
                    <MenuItem value="high">High</MenuItem>
                    <MenuItem value="medium">Medium</MenuItem>
                    <MenuItem value="low">Low</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField
                  label="Story Points"
                  type="number"
                  value={newItem.story_points || ''}
                  onChange={(e) => setNewItem({ ...newItem, story_points: e.target.value ? parseInt(e.target.value) : undefined })}
                  fullWidth
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  label="Business Value (1-100)"
                  type="number"
                  value={newItem.business_value || ''}
                  onChange={(e) => setNewItem({ ...newItem, business_value: e.target.value ? parseInt(e.target.value) : undefined })}
                  fullWidth
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button 
            onClick={handleCreateItem} 
            variant="contained"
            disabled={createItemMutation.isLoading || !newItem.title}
          >
            {createItemMutation.isLoading ? 'Creating...' : 'Create Item'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* AI Analysis Dialog */}
      <Dialog 
        open={analysisDialogOpen} 
        onClose={() => setAnalysisDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" gap={1}>
            <AIIcon color="secondary" />
            AI Analysis Results
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedAnalysis && (
            <Box display="flex" flexDirection="column" gap={3} mt={2}>
              {/* Clarity Score */}
              <Box>
                <Typography variant="h6" gutterBottom>
                  📊 Clarity Assessment
                </Typography>
                <Box display="flex" alignItems="center" gap={2}>
                  <LinearProgress 
                    variant="determinate" 
                    value={selectedAnalysis.clarity_score * 100}
                    sx={{ flex: 1, height: 8, borderRadius: 4 }}
                    color={getClarityColor(selectedAnalysis.clarity_score)}
                  />
                  <Typography variant="h6" color={getClarityColor(selectedAnalysis.clarity_score) + '.main'}>
                    {Math.round(selectedAnalysis.clarity_score * 100)}%
                  </Typography>
                </Box>
              </Box>

              {/* Complexity Estimate */}
              <Box>
                <Typography variant="h6" gutterBottom>
                  🎯 Complexity Estimate
                </Typography>
                <Chip 
                  label={selectedAnalysis.estimated_complexity}
                  color={getComplexityColor(selectedAnalysis.estimated_complexity)}
                  size="large"
                />
              </Box>

              {/* Suggestions */}
              {selectedAnalysis.suggested_improvements.length > 0 && (
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <LightbulbIcon color="warning" />
                      <Typography variant="h6">
                        Improvement Suggestions ({selectedAnalysis.suggested_improvements.length})
                      </Typography>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    {selectedAnalysis.suggested_improvements.map((suggestion, index) => (
                      <Typography key={index} variant="body2" paragraph>
                        • {suggestion}
                      </Typography>
                    ))}
                  </AccordionDetails>
                </Accordion>
              )}

              {/* Risks */}
              {selectedAnalysis.potential_risks.length > 0 && (
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <WarningIcon color="error" />
                      <Typography variant="h6">
                        Potential Risks ({selectedAnalysis.potential_risks.length})
                      </Typography>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    {selectedAnalysis.potential_risks.map((risk, index) => (
                      <Typography key={index} variant="body2" paragraph>
                        • {risk}
                      </Typography>
                    ))}
                  </AccordionDetails>
                </Accordion>
              )}

              {/* Acceptance Criteria */}
              {selectedAnalysis.acceptance_criteria_suggestions.length > 0 && (
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <CheckCircleIcon color="success" />
                      <Typography variant="h6">
                        Suggested Acceptance Criteria ({selectedAnalysis.acceptance_criteria_suggestions.length})
                      </Typography>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    {selectedAnalysis.acceptance_criteria_suggestions.map((criteria, index) => (
                      <Typography key={index} variant="body2" paragraph>
                        • {criteria}
                      </Typography>
                    ))}
                  </AccordionDetails>
                </Accordion>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAnalysisDialogOpen(false)}>Close</Button>
          <Button 
            variant="contained"
            startIcon={<AutoFixIcon />}
            color="secondary"
            onClick={() => {
              // TODO: Implement apply suggestions
              setAnalysisDialogOpen(false);
            }}
          >
            Apply Suggestions
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Backlog;