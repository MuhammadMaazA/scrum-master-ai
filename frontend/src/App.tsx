import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { QueryClient, QueryClientProvider } from 'react-query';
import { ReactQueryDevtools } from 'react-query/devtools';

import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard';
import Standups from './pages/Standups';
import Backlog from './pages/Backlog';
import SprintPlanning from './pages/SprintPlanning';
import AIAssistant from './pages/AIAssistant';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// Create Material-UI theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#9c27b0',
      light: '#ba68c8',
      dark: '#7b1fa2',
    },
    success: {
      main: '#2e7d32',
    },
    warning: {
      main: '#ed6c02',
    },
    error: {
      main: '#d32f2f',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    h1: {
      fontWeight: 600,
    },
    h2: {
      fontWeight: 600,
    },
    h3: {
      fontWeight: 600,
    },
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 6,
        },
      },
    },
  },
});

// Page title mapping
const getPageTitle = (pathname: string): string => {
  switch (pathname) {
    case '/':
      return 'Dashboard';
    case '/standups':
      return 'Daily Standups';
    case '/backlog':
      return 'Product Backlog';
    case '/sprints':
      return 'Sprint Planning';
    case '/ai-assistant':
      return 'AI Assistant';
    case '/teams':
      return 'Teams';
    case '/reports':
      return 'Reports';
    case '/settings':
      return 'Settings';
    default:
      return 'AI Scrum Master';
  }
};

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Routes>
            {/* Main Application Routes */}
            <Route
              path="/"
              element={
                <Layout title={getPageTitle(window.location.pathname)}>
                  <Dashboard />
                </Layout>
              }
            />
            <Route
              path="/standups"
              element={
                <Layout title="Daily Standups">
                  <Standups />
                </Layout>
              }
            />
            <Route
              path="/backlog"
              element={
                <Layout title="Product Backlog">
                  <Backlog />
                </Layout>
              }
            />
            <Route
              path="/sprints"
              element={
                <Layout title="Sprint Planning">
                  <SprintPlanning />
                </Layout>
              }
            />
            <Route
              path="/ai-assistant"
              element={
                <Layout title="AI Assistant">
                  <AIAssistant />
                </Layout>
              }
            />
            
            {/* Placeholder routes for future pages */}
            <Route
              path="/teams"
              element={
                <Layout title="Teams">
                  <div>Teams page coming soon...</div>
                </Layout>
              }
            />
            <Route
              path="/reports"
              element={
                <Layout title="Reports">
                  <div>Reports page coming soon...</div>
                </Layout>
              }
            />
            <Route
              path="/settings"
              element={
                <Layout title="Settings">
                  <div>Settings page coming soon...</div>
                </Layout>
              }
            />

            {/* Catch-all route */}
            <Route
              path="*"
              element={
                <Layout title="Page Not Found">
                  <div>404 - Page not found</div>
                </Layout>
              }
            />
          </Routes>
        </Router>
        
        {/* React Query DevTools (only in development) */}
        {process.env.NODE_ENV === 'development' && (
          <ReactQueryDevtools initialIsOpen={false} />
        )}
      </ThemeProvider>
    </QueryClientProvider>
  );
};

export default App;