#!/bin/bash

# AI Scrum Master Setup Script
echo "🚀 Setting up AI Scrum Master..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is required but not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please edit it with your API keys and configuration."
else
    echo "✅ .env file already exists."
fi

# Create data directory
echo "📁 Creating data directories..."
mkdir -p data/chromadb
mkdir -p data/logs

# Build and start services
echo "🐳 Building and starting Docker services..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
echo "🔍 Checking service health..."

# Check PostgreSQL
if docker-compose exec -T postgres pg_isready -U scrum_user -d scrum_db > /dev/null 2>&1; then
    echo "✅ PostgreSQL is ready"
else
    echo "❌ PostgreSQL is not ready"
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is ready"
else
    echo "❌ Redis is not ready"
fi

# Check Backend API
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API is ready"
else
    echo "❌ Backend API is not ready"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file with your API keys:"
echo "   - OPENAI_API_KEY (required for AI features)"
echo "   - SLACK_BOT_TOKEN (for Slack integration)"
echo "   - JIRA_* settings (for Jira integration)"
echo ""
echo "2. Test the MVP functionality:"
echo "   python scripts/test_mvp.py"
echo ""
echo "3. Access the application:"
echo "   - API Documentation: http://localhost:8000/docs"
echo "   - Frontend: http://localhost:3000 (when ready)"
echo "   - API Health: http://localhost:8000/health"
echo ""
echo "4. View logs:"
echo "   docker-compose logs -f backend"
echo ""
echo "5. Stop services:"
echo "   docker-compose down"