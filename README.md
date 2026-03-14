<<<<<<< HEAD
# Bureaucracy Navigator Agent

An autonomous AI agent system that helps users complete government procedures by decomposing tasks, retrieving knowledge using RAG, selecting tools through function calling, maintaining memory, and executing multi-step workflows with minimal human intervention.

## Features

1. **Autonomous Task Planning** - LLM-based planner that breaks user requests into subtasks
2. **RAG System** - Knowledge retrieval from government websites and documents
3. **Tool Calling** - Autonomous tool selection for search, scraping, document parsing
4. **Memory System** - Persistent user profile and task history
5. **Workflow Executor** - Step-by-step plan execution
6. **Full-stack Application** - FastAPI backend with Next.js frontend

## Architecture

```
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── agent/          # Core agent components
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Database models
│   │   ├── tools/          # Agent tools
│   │   └── utils/          # Utilities
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── utils/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── docs/                   # Documentation
```

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Demo Procedures

- Income Certificate (Telangana)
- Driving License
- Caste Certificate

## Deployment

- Backend: Render/Railway
- Frontend: Vercel
=======
# Bureaucracy_Navigator
>>>>>>> 918f3656a5122e7dc22409385d081f011650ffd2
