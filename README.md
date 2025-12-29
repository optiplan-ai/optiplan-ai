# OptiPlan AI Service

A FastAPI service that provides AI-powered task generation and matching using Gemini AI embeddings.

## Features

- **Task Generation**: Generate project roadmap tasks using BAML
- **User/Task Indexing**: Index users and tasks using Gemini AI embeddings and Pinecone vector database
- **Smart Matching**: Match tasks to users and users to tasks based on skills and requirements
- **Vector Search**: Powered by Pinecone for efficient similarity search

## Setup

### Environment Variables

Create a `.env` file in the ai directory with the following variables:

```bash
# Google API Key for Gemini embeddings
# Get your API key from: https://ai.google.dev/
GOOGLE_API_KEY=your_google_api_key_here

# Pinecone API Key for vector database
# Get your API key from: https://www.pinecone.io/
PINECONE_API_KEY=your_pinecone_api_key_here
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

## Embeddings

This service now uses **Gemini AI embeddings** instead of local models for:

- **Superior Quality**: Google's state-of-the-art text-embedding-004 model
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
   - `PINECONE_API_KEY`: Your Pinecone API key

3. **Access your API** at `https://your-project.vercel.app/`

📖 **Detailed Guide**: See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for complete deployment instructions.

### Local Development

```bash
# Test setup
python test_gemini_embeddings.py

# Run development server
uvicorn main:app --reload

# API docs available at: http://localhost:8000/docs
```

## API Endpoints

- `GET /` - Root endpoint with service info
- `GET /health-check` - Health check endpoint
- `POST /generate-tasks` - Generate project tasks
- `POST /index-users` - Index user skills
- `POST /index-tasks` - Index project tasks
- `POST /match-tasks-for-users` - Find matching tasks for users
- `POST /match-users-for-tasks` - Find matching users for tasks
- `POST /match-tasks-for-user` - Find matching tasks for a single user
- `POST /match-user-for-task` - Find matching users for a single task
- `POST /delete-indexed-users` - Delete user indexes
- `POST /delete-indexed-tasks` - Delete task indexes

## Testing

Verify your setup with the test script:

```bash
python test_gemini_embeddings.py
```

This will test:
- ✅ API key configuration
- ✅ Gemini embeddings functionality
- ✅ Embedding dimensions consistency
- ✅ Ready for production use
