import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Chip,
  Grid
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { analyticsAPI } from '../../services/api';

interface BurndownChartProps {
  sprintId: number;
  refreshInterval?: number; // Auto-refresh interval in seconds
}

interface BurndownData {
  sprint_name: string;
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    borderColor: string;
    backgroundColor: string;
    borderDash?: number[];
    tension: number;
  }>;
  metrics: {
    total_points: number;
    completed_points: number;
    completion_percentage: number;
    days_remaining: number;
    is_on_track: boolean;
    predicted_completion: string | null;
  };
}

const BurndownChart: React.FC<BurndownChartProps> = ({ 
  sprintId, 
  refreshInterval = 300 // 5 minutes default
}) => {
  const [burndownData, setBurndownData] = useState<BurndownData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const fetchBurndownData = async () => {
    try {
      setError(null);
      const response = await analyticsAPI.getBurndownChart(sprintId);
      
      if (response.success) {
        setBurndownData(response.data);
        setLastUpdated(new Date());
      } else {
        setError('Failed to load burndown data');
      }
    } catch (err) {
      setError(`Error loading burndown chart: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBurndownData();

    // Set up auto-refresh
    const interval = setInterval(fetchBurndownData, refreshInterval * 1000);
    
    return () => clearInterval(interval);
  }, [sprintId, refreshInterval]);

  const formatChartData = () => {
    if (!burndownData) return [];

    return burndownData.labels.map((date, index) => ({
      date: new Date(date).toLocaleDateString(),
      remaining: burndownData.datasets[0]?.data[index] || 0,
      ideal: burndownData.datasets[1]?.data[index] || 0
    }));
  };

  const getStatusColor = () => {
    if (!burndownData?.metrics) return 'default';
    
    if (burndownData.metrics.is_on_track) {
      return 'success';
    } else if (burndownData.metrics.completion_percentage > 50) {
      return 'warning';
    } else {
      return 'error';
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Box display="flex" justifyContent="center" alignItems="center" minHeight={400}>
            <CircularProgress />
            <Typography variant="body2" sx={{ ml: 2 }}>
              Loading burndown chart...
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent>
          <Alert severity="error">
            {error}
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (!burndownData) {
    return (
      <Card>
        <CardContent>
          <Alert severity="info">
            No burndown data available for this sprint.
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader
        title={
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Typography variant="h6">
              Burndown Chart - {burndownData.sprint_name}
            </Typography>
            <Chip
              label={burndownData.metrics.is_on_track ? 'On Track' : 'At Risk'}
              color={getStatusColor()}
              size="small"
            />
          </Box>
        }
        subheader={
          <Typography variant="caption" color="textSecondary">
            Last updated: {lastUpdated.toLocaleTimeString()}
          </Typography>
        }
      />
      <CardContent>
        <Grid container spacing={3}>
          {/* Metrics Row */}
          <Grid item xs={12}>
            <Grid container spacing={2}>
              <Grid item xs={6} sm={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="primary">
                    {burndownData.metrics.completion_percentage.toFixed(1)}%
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Complete
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Box textAlign="center">
                  <Typography variant="h4" color="secondary">
                    {burndownData.metrics.days_remaining}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Days Left
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Box textAlign="center">
                  <Typography variant="h4">
                    {burndownData.metrics.completed_points}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Points Done
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Box textAlign="center">
                  <Typography variant="h4">
                    {burndownData.metrics.total_points}
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Total Points
                  </Typography>
                </Box>
              </Grid>
            </Grid>
          </Grid>

          {/* Chart */}
          <Grid item xs={12}>
            <Box height={400}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={formatChartData()}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tick={{ fontSize: 12 }}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip 
                    labelFormatter={(label) => `Date: ${label}`}
                    formatter={(value, name) => [
                      `${value} points`,
                      name === 'remaining' ? 'Remaining Work' : 'Ideal Burndown'
                    ]}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="remaining"
                    stroke="#ff6b6b"
                    strokeWidth={3}
                    dot={{ fill: '#ff6b6b', strokeWidth: 2, r: 4 }}
                    name="Actual Burndown"
                  />
                  <Line
                    type="monotone"
                    dataKey="ideal"
                    stroke="#4ecdc4"
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    dot={{ fill: '#4ecdc4', strokeWidth: 2, r: 3 }}
                    name="Ideal Burndown"
                  />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </Grid>

          {/* Prediction */}
          {burndownData.metrics.predicted_completion && (
            <Grid item xs={12}>
              <Alert severity="info">
                <Typography variant="body2">
                  <strong>Predicted Completion:</strong> {' '}
                  {new Date(burndownData.metrics.predicted_completion).toLocaleDateString()}
                  {!burndownData.metrics.is_on_track && (
                    <span style={{ color: '#f44336' }}>
                      {' '}(Behind schedule)
                    </span>
                  )}
                </Typography>
              </Alert>
            </Grid>
          )}
        </Grid>
      </CardContent>
    </Card>
  );
};

export default BurndownChart;