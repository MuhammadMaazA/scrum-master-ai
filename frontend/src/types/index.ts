// Core domain types for the AI Scrum Master frontend

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: 'team_member' | 'scrum_master' | 'product_owner' | 'admin';
  avatar_url?: string;
  slack_user_id?: string;
  teams: Team[];
}

export interface Team {
  id: number;
  name: string;
  description: string;
  team_size: number;
  is_active: boolean;
  slack_channel_name?: string;
  standup_time: string;
  ai_tone: 'professional' | 'casual' | 'formal';
  auto_standup_enabled: boolean;
}

export interface Project {
  id: number;
  name: string;
  key: string;
  description: string;
  status: 'active' | 'on_hold' | 'completed' | 'archived';
  jira_project_key?: string;
  team_id: number;
}

export interface Sprint {
  id: number;
  name: string;
  goal: string;
  start_date: string;
  end_date: string;
  status: 'planned' | 'active' | 'completed' | 'cancelled';
  planned_capacity: number;
  actual_velocity: number;
  team_capacity_days: number;
  project_id: number;
  team_id: number;
}

export interface BacklogItem {
  id: number;
  title: string;
  description: string;
  acceptance_criteria?: string;
  item_type: 'story' | 'bug' | 'task' | 'epic' | 'spike';
  priority: 'critical' | 'high' | 'medium' | 'low';
  status: 'todo' | 'in_progress' | 'review' | 'done' | 'blocked';
  story_points?: number;
  jira_key?: string;
  
  // AI analysis fields
  ai_suggested_points?: number;
  ai_complexity_score?: number;
  ai_clarity_score?: number;
  ai_suggestions?: string;
  duplicate_candidates?: number[];
  
  // Business fields
  business_value?: number;
  effort_estimate?: 'XS' | 'S' | 'M' | 'L' | 'XL' | 'XXL';
  value_effort_ratio?: number;
  
  project_id: number;
  sprint_id?: number;
  assignee_id?: number;
  created_by_id: number;
  created_at: string;
  updated_at: string;
}

export interface StandupEntry {
  id: number;
  yesterday_work?: string;
  today_plan?: string;
  blockers?: string;
  additional_notes?: string;
  entry_date: string;
  source: 'manual' | 'slack' | 'web_form' | 'ai_detected';
  confidence_score: number;
  user_id: number;
  team_id: number;
}

export interface StandupSummary {
  id: number;
  summary_text: string;
  key_achievements: string[];
  active_blockers: BlockerItem[];
  focus_areas: string[];
  action_items: ActionItem[];
  summary_date: string;
  participants_count: number;
  missing_members: string[];
  status: 'generated' | 'reviewed' | 'published' | 'archived';
  posted_to_slack: boolean;
  team_id: number;
  sprint_id?: number;
}

export interface BlockerItem {
  description: string;
  owner?: string;
  since?: string;
}

export interface ActionItem {
  action: string;
  assignee?: string;
  due_date?: string;
  priority?: 'high' | 'medium' | 'low';
}

// AI Analysis types
export interface BacklogAnalysis {
  clarity_score: number;
  suggested_improvements: string[];
  estimated_complexity: 'XS' | 'S' | 'M' | 'L' | 'XL';
  potential_risks: string[];
  acceptance_criteria_suggestions: string[];
}

export interface SprintPlanSuggestion {
  recommended_items: number[];
  total_story_points: number;
  sprint_goal: string;
  risks: string[];
  capacity_utilization: number;
}

// Chart data types
export interface BurndownData {
  day: number;
  remaining: number;
  ideal?: number;
}

export interface VelocityData {
  sprint: string;
  planned: number;
  completed: number;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Form types
export interface StandupEntryForm {
  yesterday_work: string;
  today_plan: string;
  blockers: string;
  additional_notes?: string;
}

export interface BacklogItemForm {
  title: string;
  description: string;
  acceptance_criteria?: string;
  item_type: BacklogItem['item_type'];
  priority: BacklogItem['priority'];
  story_points?: number;
  business_value?: number;
  assignee_id?: number;
}

export interface SprintForm {
  name: string;
  goal: string;
  start_date: string;
  end_date: string;
  planned_capacity: number;
  team_capacity_days: number;
}

// UI State types
export interface DashboardState {
  selectedTeam?: Team;
  selectedProject?: Project;
  activeSprint?: Sprint;
  loading: boolean;
  error?: string;
}

export interface NotificationState {
  open: boolean;
  message: string;
  severity: 'success' | 'error' | 'warning' | 'info';
}

// Filter and sort types
export interface BacklogFilters {
  status?: BacklogItem['status'][];
  priority?: BacklogItem['priority'][];
  item_type?: BacklogItem['item_type'][];
  assignee_id?: number;
  search?: string;
}

export interface SortOption {
  field: string;
  direction: 'asc' | 'desc';
}