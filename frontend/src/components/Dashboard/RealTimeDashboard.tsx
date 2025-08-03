import React, { useState, useEffect, useCallback } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Alert,
  Button,
  Badge,
  LinearProgress,
  Tooltip,
  IconButton,
  Snackbar
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Timeline as TimelineIcon,
  Group as GroupIcon,
  Assignment as AssignmentIcon,
  Speed as SpeedIcon,
  Notifications as NotificationsIcon
} from '@mui/icons-material';
import { analyticsAPI, agentsAPI } from '../../services/api';
import BurndownChart from '../Analytics/BurndownChart';

interface DashboardMetrics {
  team_name: string;
  current_sprint: {
    sprint_name: string;
    completion_percentage: number;
    days_remaining: number;
    total_points: number;
    completed_points: number;
    is_on_track: boolean;
    velocity: number;
  } | null;
  velocity_trend: {
    average_velocity: number;
    trend: 'improving' | 'declining' | 'stable';
    last_sprint_velocity: number;
  } | null;
}

interface LiveUpdate {
  id: string;
  type: 'success' | 'warning' | 'error' | 'info';
  message: string;
  timestamp: Date;
  action?: string;
}

const RealTimeDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [liveUpdates, setLiveUpdates] = useState<LiveUpdate[]>([]);
  const [showNotification, setShowNotification] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState('');

  const fetchDashboardMetrics = useCallback(async (teamId: number = 1) => {
    try {
      setError(null);
      const response = await analyticsAPI.getDashboardMetrics(teamId);
      
      if (response.success) {
        const newMetrics = response.data;
        
        // Check for significant changes
        if (metrics?.current_sprint && newMetrics.current_sprint) {
          const oldCompletion = metrics.current_sprint.completion_percentage;
          const newCompletion = newMetrics.current_sprint.completion_percentage;
          
          if (Math.abs(newCompletion - oldCompletion) >= 5) {
            addLiveUpdate({
              type: newCompletion > oldCompletion ? 'success' : 'warning',
              message: `Sprint completion updated: ${newCompletion.toFixed(1)}% (${newCompletion > oldCompletion ? '+' : ''}${(newCompletion - oldCompletion).toFixed(1)}%)`,
              action: 'completion_change'
            });
          }
        }
        
        setMetrics(newMetrics);
        setLastUpdated(new Date());
      } else {
        setError('Failed to load dashboard metrics');
      }
    } catch (err) {
      setError(`Error loading dashboard: ${err}`);
    } finally {
      setLoading(false);
    }
  }, [metrics]);

  const addLiveUpdate = (update: Omit<LiveUpdate, 'id' | 'timestamp'>) => {
    const newUpdate: LiveUpdate = {
      ...update,
      id: Date.now().toString(),
      timestamp: new Date()
    };
    
    setLiveUpdates(prev => [newUpdate, ...prev.slice(0, 9)]); // Keep last 10 updates
    
    // Show notification for important updates
    if (update.type === 'success' || update.type === 'warning') {
      setNotificationMessage(update.message);
      setShowNotification(true);
    }
  };

  const handleRefresh = () => {
    setLoading(true);
    fetchDashboardMetrics();
    addLiveUpdate({
      type: 'info',
      message: 'Dashboard refreshed manually',
      action: 'manual_refresh'
    });
  };

  const triggerAutoStandup = async () => {
    try {
      addLiveUpdate({
        type: 'info',
        message: 'Triggering automatic standup...',
        action: 'standup_trigger'
      });

      const response = await agentsAPI.triggerAutoStandup('#standup');
      
      if (response.success) {
        addLiveUpdate({
          type: 'success',
          message: 'Automatic standup initiated successfully',
          action: 'standup_success'
        });
      } else {
        addLiveUpdate({
          type: 'error',
          message: 'Failed to trigger automatic standup',
          action: 'standup_error'
        });
      }
    } catch (err) {
      addLiveUpdate({
        type: 'error',
        message: `Standup trigger failed: ${err}`,
        action: 'standup_error'
      });
    }
  };

  useEffect(() => {
    fetchDashboardMetrics();

    // Set up auto-refresh
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(() => {
        fetchDashboardMetrics();
      }, 60000); // Refresh every minute
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh, fetchDashboardMetrics]);

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving':
        return <TrendingUpIcon color="success" />;
      case 'declining':
        return <TrendingDownIcon color="error" />;
      default:
        return <TimelineIcon color="info" />;
    }
  };

  const getStatusColor = (isOnTrack: boolean) => {
    return isOnTrack ? 'success' : 'warning';
  };

  if (loading && !metrics) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
        <LinearProgress sx={{ width: '50%' }} />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" action={
        <Button color="inherit" size="small" onClick={handleRefresh}>
          Retry
        </Button>
      }>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" gutterBottom>
          AI Scrum Master Dashboard
        </Typography>
        <Box display="flex" alignItems="center" gap={2}>
          <Tooltip title="Auto-refresh enabled">
            <Chip
              icon={<RefreshIcon />}
              label={autoRefresh ? 'Live' : 'Manual'}
              color={autoRefresh ? 'success' : 'default'}
              size="small"
              onClick={() => setAutoRefresh(!autoRefresh)}
            />
          </Tooltip>
          <Tooltip title="Refresh now">
            <IconButton onClick={handleRefresh} disabled={loading}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Typography variant="caption" color="textSecondary">
            Updated: {lastUpdated.toLocaleTimeString()}
          </Typography>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Team Overview */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6" display="flex" alignItems="center">
                  <GroupIcon sx={{ mr: 1 }} />
                  {metrics?.team_name || 'Team Dashboard'}
                </Typography>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<AssignmentIcon />}
                  onClick={triggerAutoStandup}
                >
                  Auto Standup
                </Button>
              </Box>

              {metrics?.current_sprint ? (
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center" p={2}>
                      <Typography variant="h3" color="primary">
                        {metrics.current_sprint.completion_percentage.toFixed(1)}%
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Sprint Complete
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={metrics.current_sprint.completion_percentage}
                        sx={{ mt: 1 }}
                      />
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center" p={2}>
                      <Typography variant="h3" color="secondary">
                        {metrics.current_sprint.days_remaining}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Days Remaining
                      </Typography>
                      <Chip
                        label={metrics.current_sprint.is_on_track ? 'On Track' : 'At Risk'}
                        color={getStatusColor(metrics.current_sprint.is_on_track)}
                        size="small"
                        sx={{ mt: 1 }}
                      />
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center" p={2}>
                      <Typography variant="h3">
                        {metrics.current_sprint.completed_points}/{metrics.current_sprint.total_points}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Story Points
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Box textAlign="center" p={2} display="flex" flexDirection="column" alignItems="center">
                      <Typography variant="h3" display="flex" alignItems="center">
                        {metrics.current_sprint.velocity.toFixed(1)}
                        {metrics.velocity_trend && (
                          <Box ml={1}>
                            {getTrendIcon(metrics.velocity_trend.trend)}
                          </Box>
                        )}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Current Velocity
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              ) : (
                <Alert severity="info">
                  No active sprint found. Create a sprint to see dashboard metrics.
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Live Updates */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Badge badgeContent={liveUpdates.length} color="primary">
                  <NotificationsIcon />
                </Badge>
                <Typography variant="h6" sx={{ ml: 1 }}>
                  Live Updates
                </Typography>
              </Box>
              
              <Box maxHeight={300} overflow="auto">
                {liveUpdates.length === 0 ? (
                  <Typography variant="body2" color="textSecondary">
                    No recent updates
                  </Typography>
                ) : (
                  liveUpdates.map((update) => (
                    <Alert
                      key={update.id}
                      severity={update.type}
                      sx={{ mb: 1, fontSize: '0.75rem' }}
                    >
                      <Typography variant="caption" display="block">
                        {update.message}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        {update.timestamp.toLocaleTimeString()}
                      </Typography>
                    </Alert>
                  ))
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Burndown Chart */}
        {metrics?.current_sprint && (
          <Grid item xs={12}>
            <BurndownChart 
              sprintId={1} // This should come from current sprint data
              refreshInterval={300}
            />
          </Grid>
        )}

        {/* Velocity Trend */}
        {metrics?.velocity_trend && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" display="flex" alignItems="center" mb={2}>
                  <SpeedIcon sx={{ mr: 1 }} />
                  Team Velocity Trend
                </Typography>
                
                <Grid container spacing={2}>
                  <Grid item xs={4}>
                    <Box textAlign="center">
                      <Typography variant="h4" color="primary">
                        {metrics.velocity_trend.average_velocity.toFixed(1)}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        Average Velocity
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={4}>
                    <Box textAlign="center">
                      <Typography variant="h4">
                        {metrics.velocity_trend.last_sprint_velocity.toFixed(1)}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        Last Sprint
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={4}>
                    <Box textAlign="center" display="flex" flexDirection="column" alignItems="center">
                      {getTrendIcon(metrics.velocity_trend.trend)}
                      <Typography variant="caption" color="textSecondary" sx={{ mt: 1 }}>
                        {metrics.velocity_trend.trend.charAt(0).toUpperCase() + metrics.velocity_trend.trend.slice(1)}
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>

      {/* Notifications */}
      <Snackbar
        open={showNotification}
        autoHideDuration={4000}
        onClose={() => setShowNotification(false)}
        message={notificationMessage}
      />
    </Box>
  );
};

export default RealTimeDashboard;