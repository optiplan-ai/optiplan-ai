# OptiPlan AI Service

A FastAPI service that provides AI-powered task generation and matching using CrewAI, Gemini AI, and Upstash Vector.

## Features

- **Task Generation**: Generate project roadmap tasks using CrewAI agents with Gemini 3 Pro/2.5 Pro
- **User/Task Indexing**: Index users and tasks using Gemini AI embeddings and Upstash Vector database
- **Smart Matching**: Match tasks to users and users to tasks based on skills and requirements
- **Vector Search**: Powered by Upstash Vector for efficient similarity search

## Setup

### Environment Variables

Create a `.env` file in the ai directory with the following variables:

```bash
# Google API Key for Gemini embeddings and LLM
# Get your API key from: https://ai.google.dev/
GOOGLE_API_KEY=your_google_api_key_here

# Upstash Vector for vector database
# Get your credentials from: https://console.upstash.com/
UPSTASH_VECTOR_REST_URL=your_upstash_vector_url
UPSTASH_VECTOR_REST_TOKEN=your_upstash_vector_token
```

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the service:
```bash
uvicorn main:app --reload
```

## AI Stack

This service uses:

- **CrewAI**: Agent orchestration framework for task generation
- **Gemini 3 Pro/2.5 Pro**: Google's latest language models for task planning
- **Gemini Embeddings**: text-embedding-004 model for vector embeddings
- **Upstash Vector**: Serverless vector database for similarity search

### Task Generation

The service uses a CrewAI crew with three specialized agents:

1. **Project Analyst**: Analyzes project requirements and breaks down components
2. **Task Planner**: Creates detailed, actionable tasks with dependencies
3. **Roadmap Generator**: Structures tasks into a comprehensive roadmap

### Embeddings

This service uses **Gemini AI embeddings** (text-embedding-004) for:

- **Superior Quality**: Google's state-of-the-art embedding model
- **Multilingual Support**: Over 100 languages supported
- **Dynamic Dimensions**: Automatically detects embedding dimensions (768 for text-embedding-004)
- **Task-Specific Optimization**: Uses appropriate task types for document indexing vs query retrieval

## Deployment

### Deploy to Vercel

For serverless deployment with automatic scaling:

1. **Quick Deploy** (via CLI):
```bash
npm install -g vercel
cd ai
vercel
```

2. **Set Environment Variables** in Vercel dashboard:
   - `GOOGLE_API_KEY`: Your Google API key
   - `UPSTASH_VECTOR_REST_URL`: Your Upstash Vector URL
   - `UPSTASH_VECTOR_REST_TOKEN`: Your Upstash Vector token

3. **Access your API** at `https://your-project.vercel.app/`

📖 **Detailed Guide**: See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for complete deployment instructions.

### Local Development

```bash
# Run development server
uvicorn main:app --reload

# API docs available at: http://localhost:8000/docs
```

## API Endpoints

- `GET /` - Root endpoint with service info
- `GET /health-check` - Health check endpoint
- `POST /generate-tasks` - Generate project tasks using CrewAI
- `POST /index-users` - Index user skills in vector database
- `POST /index-tasks` - Index project tasks in vector database
- `POST /match-tasks-for-users` - Find matching tasks for users
- `POST /match-users-for-tasks` - Find matching users for tasks
- `POST /match-tasks-for-user` - Find matching tasks for a single user
- `POST /match-user-for-task` - Find matching users for a single task
- `POST /delete-indexed-users` - Delete user indexes
- `POST /delete-indexed-tasks` - Delete task indexes

## Architecture

The service is built with:

- **FastAPI**: Modern Python web framework
- **CrewAI**: Multi-agent orchestration for complex task generation
- **Upstash Vector**: Serverless vector database
- **Google Gemini**: For both LLM and embeddings
