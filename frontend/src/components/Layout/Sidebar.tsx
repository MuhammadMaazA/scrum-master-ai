import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Typography,
  Box,
  Chip,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Assignment as BacklogIcon,
  Timeline as SprintIcon,
  Chat as StandupIcon,
  Analytics as ReportsIcon,
  Settings as SettingsIcon,
  SmartToy as AIIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const DRAWER_WIDTH = 280;

interface SidebarProps {
  open: boolean;
  onClose: () => void;
  variant?: 'permanent' | 'temporary';
}

const menuItems = [
  { 
    text: 'Dashboard', 
    icon: <DashboardIcon />, 
    path: '/',
    description: 'Team overview and metrics'
  },
  { 
    text: 'Daily Standups', 
    icon: <StandupIcon />, 
    path: '/standups',
    description: 'AI-powered standup management',
    badge: 'AI'
  },
  { 
    text: 'Sprint Planning', 
    icon: <SprintIcon />, 
    path: '/sprints',
    description: 'Intelligent sprint planning',
    badge: 'AI'
  },
  { 
    text: 'Backlog', 
    icon: <BacklogIcon />, 
    path: '/backlog',
    description: 'AI-enhanced backlog grooming',
    badge: 'AI'
  },
  { 
    text: 'Teams', 
    icon: <PeopleIcon />, 
    path: '/teams',
    description: 'Team management'
  },
  { 
    text: 'Reports', 
    icon: <ReportsIcon />, 
    path: '/reports',
    description: 'Analytics and insights'
  },
];

const aiItems = [
  { 
    text: 'AI Assistant', 
    icon: <AIIcon />, 
    path: '/ai-assistant',
    description: 'Direct AI interaction'
  },
  { 
    text: 'Settings', 
    icon: <SettingsIcon />, 
    path: '/settings',
    description: 'Configuration'
  },
];

const Sidebar: React.FC<SidebarProps> = ({ open, onClose, variant = 'temporary' }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleNavigation = (path: string) => {
    navigate(path);
    if (variant === 'temporary') {
      onClose();
    }
  };

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(path);
  };

  const DrawerContent = (
    <Box sx={{ width: DRAWER_WIDTH, height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 3, textAlign: 'center', borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h5" component="h1" fontWeight="bold" color="primary">
          🤖 AI Scrum Master
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
          Intelligent Agile Assistant
        </Typography>
      </Box>

      {/* Main Navigation */}
      <Box sx={{ flex: 1, overflowY: 'auto' }}>
        <List sx={{ px: 2, py: 1 }}>
          {menuItems.map((item) => (
            <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                onClick={() => handleNavigation(item.path)}
                selected={isActive(item.path)}
                sx={{
                  borderRadius: 2,
                  '&.Mui-selected': {
                    backgroundColor: 'primary.main',
                    color: 'white',
                    '&:hover': {
                      backgroundColor: 'primary.dark',
                    },
                    '& .MuiListItemIcon-root': {
                      color: 'white',
                    },
                  },
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                }}
              >
                <ListItemIcon sx={{ minWidth: 40 }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText 
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="subtitle2">
                        {item.text}
                      </Typography>
                      {item.badge && (
                        <Chip 
                          label={item.badge} 
                          size="small" 
                          color="secondary"
                          sx={{ height: 20, fontSize: '0.7rem' }}
                        />
                      )}
                    </Box>
                  }
                  secondary={
                    <Typography variant="caption" color="text.secondary">
                      {item.description}
                    </Typography>
                  }
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>

        <Divider sx={{ mx: 2, my: 1 }} />

        {/* AI Tools Section */}
        <List sx={{ px: 2, py: 1 }}>
          <ListItem>
            <Typography variant="overline" color="text.secondary" fontWeight="bold">
              AI Tools
            </Typography>
          </ListItem>
          {aiItems.map((item) => (
            <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                onClick={() => handleNavigation(item.path)}
                selected={isActive(item.path)}
                sx={{
                  borderRadius: 2,
                  '&.Mui-selected': {
                    backgroundColor: 'secondary.main',
                    color: 'white',
                    '&:hover': {
                      backgroundColor: 'secondary.dark',
                    },
                    '& .MuiListItemIcon-root': {
                      color: 'white',
                    },
                  },
                }}
              >
                <ListItemIcon sx={{ minWidth: 40 }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText 
                  primary={
                    <Typography variant="subtitle2">
                      {item.text}
                    </Typography>
                  }
                  secondary={
                    <Typography variant="caption" color="text.secondary">
                      {item.description}
                    </Typography>
                  }
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Box>

      {/* Footer */}
      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider', textAlign: 'center' }}>
        <Typography variant="caption" color="text.secondary">
          v1.0.0 • AI-Powered
        </Typography>
      </Box>
    </Box>
  );

  return (
    <Drawer
      variant={variant}
      open={open}
      onClose={onClose}
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: DRAWER_WIDTH,
          boxSizing: 'border-box',
        },
      }}
    >
      {DrawerContent}
    </Drawer>
  );
};

export default Sidebar;