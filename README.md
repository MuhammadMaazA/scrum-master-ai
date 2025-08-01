# AI Scrum Master - Web-Based Virtual Assistant

A comprehensive web application that acts as a virtual AI Scrum Master, automating Scrum Master responsibilities while keeping humans in the loop for oversight.

## 🚀 Features

- **Automated Daily Standups**: AI-powered standup summaries from Slack and Jira
- **Intelligent Backlog Grooming**: Auto-refinement of user stories with duplicate detection
- **Sprint Planning Assistance**: Data-driven sprint recommendations and capacity analysis  
- **Burndown Charts & Velocity Tracking**: Automated progress monitoring and reporting
- **Multi-Tool Integration**: Seamless integration with Jira, Slack, GitHub, and more
- **Human-in-the-Loop**: AI suggestions with human oversight and approval

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI Backend │    │  External APIs  │
│   (TypeScript)   │◄──►│    (Python)      │◄──►│ Jira/Slack/Git │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   AI Engine      │
                    │ GPT-4 + LangChain│
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Vector DB +     │
                    │  PostgreSQL      │
                    └──────────────────┘
```

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy, Celery
- **Frontend**: React, TypeScript, Material-UI
- **AI/LLM**: OpenAI GPT-4, LangChain
- **Database**: PostgreSQL, ChromaDB/Pinecone (Vector DB)
- **Integrations**: Atlassian API, Slack SDK, GitHub API
- **Infrastructure**: Docker, Redis, nginx

## 🚦 Quick Start

### Prerequisites

- Docker & Docker Compose (recommended)
- Python 3.11+ (for local development)
- OpenAI API Key (required)

### Fastest Setup (MVP Ready in 5 minutes!)

1. **Clone and configure**:
```bash
git clone <repository-url>
cd scrum
cp backend/.env.example backend/.env
# Edit backend/.env with your OpenAI API key
```

2. **Start everything with Docker**:
```bash
docker-compose up -d --build
```

3. **Test the MVP**:
```bash
python scripts/test_mvp.py
```

4. **Access the system**:
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - Generate standup summary via API

### Manual Setup (Development)

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# In another terminal - start PostgreSQL and Redis
docker-compose up postgres redis -d
```

### Environment Variables

Create a `.env` file with the following:

```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/scrum_db

# Slack
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_SIGNING_SECRET=your_slack_signing_secret

# Jira
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your_jira_email
JIRA_API_TOKEN=your_jira_api_token

# GitHub (optional)
GITHUB_TOKEN=your_github_token

# Redis
REDIS_URL=redis://localhost:6379
```

## 🏃‍♂️ Development

### Backend Development
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm start
```

### Running Tests
```bash
# Backend tests
cd backend && python -m pytest

# Frontend tests  
cd frontend && npm test
```

## 📋 Development Phases

- [x] **Phase 1**: Project Infrastructure Setup ✅
- [x] **Phase 2**: Core MVP (Basic Standup Summary) ✅
- [ ] **Phase 3**: Backlog Grooming Assistant (API Ready)
- [ ] **Phase 4**: Sprint Planning Automation (Foundation Built)
- [ ] **Phase 5**: Burndown Charts & Reporting
- [ ] **Phase 6**: Advanced Integrations
- [ ] **Phase 7**: UI/UX Enhancements
- [ ] **Phase 8**: Production Deployment

### 🎉 MVP Status: COMPLETE!
The core AI Scrum Master is now functional with:
- ✅ AI-powered standup summary generation
- ✅ Slack & Jira integrations
- ✅ Vector database for context storage
- ✅ Comprehensive API endpoints
- ✅ Docker containerization
- ✅ Automated testing suite

## 🔐 Security & Privacy

- OAuth 2.0 for all third-party integrations
- Encrypted storage of API tokens
- Data anonymization for LLM processing
- Audit logging for all AI actions
- GDPR compliance features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions, please open an issue in the GitHub repository or contact the development team. 