# AI Scrum Master Frontend

This is the frontend application for the AI Scrum Master project built with React, TypeScript, and Vite.

## Development

Follow these steps to set up the development environment:

```sh
# Step 1: Navigate to the frontend directory
cd frontend

# Step 2: Install the necessary dependencies.
npm i

# Step 3: Start the development server with auto-reloading and an instant preview.
npm run dev
```

The development server will start at `http://localhost:8080`.

## Available Scripts

- `npm run dev` - Start the development server
- `npm run build` - Build for production
- `npm run lint` - Run ESLint
- `npm run preview` - Preview the production build

## Project Structure

- `src/components/` - React components
- `src/pages/` - Page components
- `src/hooks/` - Custom React hooks
- `src/lib/` - Utility functions
- `src/integrations/` - External service integrations

## Backend Integration

The frontend is configured to connect to the backend API running at:
- Development: `http://localhost:8000`
- The API endpoints are available at `/api/v1/`

## What technologies are used for this project?

This project is built with:

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

## Deployment

Build the project for production using:

```sh
npm run build
```

The built files will be in the `dist/` directory.
