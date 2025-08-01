// API service for communicating with the AI Scrum Master backend

import axios, { AxiosResponse } from 'axios';
import {
  User,
  Team,
  Project,
  Sprint,
  BacklogItem,
  StandupEntry,
  StandupSummary,
  BacklogAnalysis,
  SprintPlanSuggestion,
  StandupEntryForm,
  BacklogItemForm,
  SprintForm,
  BacklogFilters,
} from '@/types';

// Configure axios defaults
const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth tokens
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  login: async (username: string, password: string): Promise<any> => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
  
  logout: async (): Promise<void> => {
    await api.post('/auth/logout');
    localStorage.removeItem('auth_token');
  },
  
  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// Teams API
export const teamsAPI = {
  getTeams: async (): Promise<Team[]> => {
    const response = await api.get('/teams/');
    return response.data;
  },
  
  getTeam: async (teamId: number): Promise<Team> => {
    const response = await api.get(`/teams/${teamId}`);
    return response.data;
  },
  
  getTeamMembers: async (teamId: number): Promise<User[]> => {
    const response = await api.get(`/teams/${teamId}/members`);
    return response.data;
  },
};

// Projects API
export const projectsAPI = {
  getProjects: async (): Promise<Project[]> => {
    const response = await api.get('/projects/');
    return response.data;
  },
  
  getProject: async (projectId: number): Promise<Project> => {
    const response = await api.get(`/projects/${projectId}`);
    return response.data;
  },
};

// Sprints API
export const sprintsAPI = {
  getTeamSprints: async (teamId: number): Promise<Sprint[]> => {
    const response = await api.get(`/sprints/teams/${teamId}/sprints`);
    return response.data;
  },
  
  getSprint: async (sprintId: number): Promise<Sprint> => {
    const response = await api.get(`/sprints/${sprintId}`);
    return response.data;
  },
  
  createSprint: async (teamId: number, sprint: SprintForm): Promise<Sprint> => {
    const response = await api.post(`/sprints/teams/${teamId}/sprints`, sprint);
    return response.data;
  },
  
  updateSprint: async (sprintId: number, sprint: Partial<SprintForm>): Promise<Sprint> => {
    const response = await api.put(`/sprints/${sprintId}`, sprint);
    return response.data;
  },
  
  getSprintBurndown: async (sprintId: number): Promise<any> => {
    const response = await api.get(`/sprints/${sprintId}/burndown`);
    return response.data;
  },
};

// Backlog API
export const backlogAPI = {
  getProjectBacklog: async (projectId: number, filters?: BacklogFilters): Promise<BacklogItem[]> => {
    const response = await api.get(`/backlog/projects/${projectId}/items`, {
      params: filters,
    });
    return response.data;
  },
  
  getBacklogItem: async (itemId: number): Promise<BacklogItem> => {
    const response = await api.get(`/backlog/items/${itemId}`);
    return response.data;
  },
  
  createBacklogItem: async (projectId: number, item: BacklogItemForm): Promise<BacklogItem> => {
    const response = await api.post(`/backlog/projects/${projectId}/items`, item);
    return response.data;
  },
  
  updateBacklogItem: async (itemId: number, item: Partial<BacklogItemForm>): Promise<BacklogItem> => {
    const response = await api.put(`/backlog/items/${itemId}`, item);
    return response.data;
  },
  
  deleteBacklogItem: async (itemId: number): Promise<void> => {
    await api.delete(`/backlog/items/${itemId}`);
  },
  
  analyzeBacklogItem: async (item: { title: string; description: string; item_type: string }): Promise<BacklogAnalysis> => {
    const response = await api.post('/ai/analyze-backlog', item);
    return response.data;
  },
  
  bulkAnalyzeBacklog: async (projectId: number): Promise<any> => {
    const response = await api.post(`/backlog/projects/${projectId}/bulk-analyze`);
    return response.data;
  },
  
  applyAISuggestions: async (itemId: number, suggestions: any): Promise<BacklogItem> => {
    const response = await api.post(`/backlog/items/${itemId}/apply-suggestions`, suggestions);
    return response.data;
  },
};

// Standup API
export const standupAPI = {
  getTeamStandupSummaries: async (teamId: number, limit: number = 10): Promise<StandupSummary[]> => {
    const response = await api.get(`/standup/teams/${teamId}/summaries`, {
      params: { limit },
    });
    return response.data;
  },
  
  createStandupEntry: async (teamId: number, entry: StandupEntryForm): Promise<any> => {
    const response = await api.post(`/standup/teams/${teamId}/entries`, {
      ...entry,
      user_id: 1, // TODO: Get from auth context
    });
    return response.data;
  },
  
  generateStandupSummary: async (teamId: number, options: {
    include_jira_updates?: boolean;
    slack_channel_id?: string;
  } = {}): Promise<any> => {
    const response = await api.post(`/standup/teams/${teamId}/generate-summary`, {
      team_id: teamId,
      ...options,
    });
    return response.data;
  },
  
  collectSlackMessages: async (teamId: number, channelId: string, hoursBack: number = 24): Promise<any> => {
    const response = await api.post(`/standup/slack/collect/${teamId}`, null, {
      params: { channel_id: channelId, hours_back: hoursBack },
    });
    return response.data;
  },
  
  sendStandupReminder: async (teamId: number, channelId: string, customMessage?: string): Promise<any> => {
    const response = await api.post(`/standup/slack/reminder/${teamId}`, null, {
      params: { channel_id: channelId, custom_message: customMessage },
    });
    return response.data;
  },
};

// Sprint Planning API
export const sprintPlanningAPI = {
  suggestSprintPlan: async (
    teamId: number,
    backlogItems: BacklogItem[],
    capacity: { velocity: number; days: number },
    context?: string
  ): Promise<SprintPlanSuggestion> => {
    const response = await api.post('/ai/suggest-sprint-plan', {
      team_id: teamId,
      backlog_items: backlogItems,
      team_velocity: capacity.velocity,
      capacity_days: capacity.days,
      sprint_goal_context: context,
    });
    return response.data;
  },
  
  createSprintFromPlan: async (
    teamId: number,
    sprintData: SprintForm,
    selectedItems: number[]
  ): Promise<Sprint> => {
    const response = await api.post(`/sprints/teams/${teamId}/create-from-plan`, {
      sprint: sprintData,
      selected_items: selectedItems,
    });
    return response.data;
  },
  
  getTeamVelocity: async (teamId: number, sprintCount: number = 5): Promise<any> => {
    const response = await api.get(`/sprints/teams/${teamId}/velocity`, {
      params: { sprint_count: sprintCount },
    });
    return response.data;
  },
};

// AI Services API
export const aiAPI = {
  testStandupSummary: async (entries: any[], teamContext: any): Promise<any> => {
    const response = await api.post('/ai/test-standup-summary', {
      entries,
      team_context: teamContext,
    });
    return response.data;
  },
  
  getVectorStats: async (): Promise<any> => {
    const response = await api.get('/ai/vector-stats');
    return response.data;
  },
  
  healthCheck: async (): Promise<any> => {
    const response = await api.post('/ai/health-check');
    return response.data;
  },
};

// Utility functions
export const apiUtils = {
  handleApiError: (error: any): string => {
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }
    if (error.message) {
      return error.message;
    }
    return 'An unexpected error occurred';
  },
  
  isApiError: (error: any): boolean => {
    return error.response && error.response.status;
  },
};

export default api;