# API Documentation

## Overview

This is a FastAPI-based task matching service that uses AI to generate project roadmaps and match users with tasks based on their skills. The service leverages Pinecone vector database for semantic search and matching, and BAML (Boundary AI ML) for AI-powered task generation.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Environment Setup](#environment-setup)
3. [REST API Endpoints](#rest-api-endpoints)
4. [PineconeSDK Class](#pineconesdk-class)
5. [BAML Client](#baml-client)
6. [Data Models](#data-models)
7. [Configuration](#configuration)
8. [Error Handling](#error-handling)
9. [Usage Examples](#usage-examples)

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Optional for BAML clients
ANTHROPIC_API_KEY=your_anthropic_api_key_here  # Optional for BAML clients
```

### Running the Service

```bash
uvicorn main:app --reload
```

The service will be available at `http://localhost:8000`

## Environment Setup

### Dependencies

- **FastAPI**: Web framework for building APIs
- **Pinecone**: Vector database for semantic search
- **BAML**: AI/ML framework for task generation
- **LangChain**: Framework for LLM applications
- **HuggingFace**: Transformers for embeddings
- **Google Generative AI**: For AI-powered task generation

## REST API Endpoints

### Base URL: `http://localhost:8000`

### Health Check

#### `GET /health-check`

Check if the service is running.

**Response:**
```json
{
  "message": "Service is up and running"
}
```

### Task Generation

#### `POST /generate-tasks`

Generate a comprehensive roadmap of tasks for a project using AI.

**Request Body:**
```json
{
  "project_id": "project_123",
  "manager_id": "manager_456",
  "project_description": "Build a scalable AI-powered content management system with React frontend and Python backend"
}
```

**Response:**
```json
{
  "tasks": [
    {
      "task_id": "project_123_1",
      "name": "Set up development environment",
      "complexity": 3,
      "estimated_hours": 8.0,
      "required_skills": [
        {
          "name": "Docker",
          "category": "DevOps",
          "preferred_experience": 2.0,
          "required_proficiency": 6
        }
      ],
      "depends_on": [],
      "project_id": "project_123",
      "manager_id": "manager_456"
    }
  ]
}
```

### User Management

#### `POST /index-users`

Index user profiles and skills in the vector database for matching.

**Request Body:**
```json
{
  "project_id": "project_123",
  "manager_id": "manager_456",
  "users": [
    {
      "id": "user_001",
      "name": "John Doe",
      "primary_domain": "frontend",
      "skills": [
        {
          "name": "React",
          "category": "frontend",
          "experience_years": 3,
          "proficiency_score": 85
        }
      ]
    }
  ]
}
```

**Response:**
```json
{
  "message": "Users indexed successfully"
}
```

#### `POST /delete-indexed-users`

Delete user profiles from the vector database.

**Request Body:**
```json
{
  "project_id": "project_123",
  "manager_id": "manager_456",
  "user_ids": ["user_001", "user_002"]
}
```

**Response:**
```json
{
  "message": "Users Index deleted successfully"
}
```

### Task Management

#### `POST /index-tasks`

Index tasks in the vector database for matching.

**Request Body:**
```json
{
  "project_id": "project_123",
  "manager_id": "manager_456",
  "tasks": [
    {
      "task_id": "task_001",
      "name": "Implement user authentication",
      "complexity": 7,
      "estimated_hours": 24.0,
      "required_skills": [
        {
          "name": "Node.js",
          "category": "backend",
          "preferred_experience": 2.0,
          "required_proficiency": 7
        }
      ]
    }
  ]
}
```

**Response:**
```json
{
  "message": "Tasks indexed successfully"
}
```

#### `POST /delete-indexed-tasks`

Delete tasks from the vector database.

**Request Body:**
```json
{
  "project_id": "project_123",
  "manager_id": "manager_456",
  "task_ids": ["task_001", "task_002"]
}
```

**Response:**
```json
{
  "message": "Tasks Index deleted successfully"
}
```

### Matching Services

#### `POST /match-tasks-for-users`

Find matching tasks for multiple users.

**Request Body:**
```json
{
  "project_id": "project_123",
  "manager_id": "manager_456",
  "users": [
    {
      "id": "user_001",
      "name": "John Doe",
      "primary_domain": "frontend",
      "skills": [...]
    }
  ]
}
```

**Response:**
```json
{
  "users": [
    {
      "id": "user_001",
      "name": "John Doe",
      "primary_domain": "frontend",
      "skills": [...],
      "matched_tasks": [
        {
          "task_id": "task_001",
          "name": "Implement user authentication",
          "match_score": 0.85,
          "min_complexity": 7,
          "time_estimate": 24.0,
          "skill_coverage": 0.75
        }
      ]
    }
  ]
}
```

#### `POST /match-users-for-tasks`

Find matching users for multiple tasks.

**Request Body:**
```json
{
  "project_id": "project_123",
  "manager_id": "manager_456",
  "tasks": [
    {
      "task_id": "task_001",
      "name": "Implement user authentication",
      "complexity": 7,
      "estimated_hours": 24.0,
      "required_skills": [...]
    }
  ]
}
```

**Response:**
```json
{
  "tasks": [
    {
      "task_id": "task_001",
      "name": "Implement user authentication",
      "complexity": 7,
      "estimated_hours": 24.0,
      "required_skills": [...],
      "matched_users": [
        {
          "user_id": "user_001",
          "name": "John Doe",
          "match_score": 0.85,
          "skill_coverage": 0.75
        }
      ]
    }
  ]
}
```

#### `POST /match-tasks-for-user`

Find matching tasks for a single user.

**Request Body:**
```json
{
  "project_id": "project_123",
  "manager_id": "manager_456",
  "user": {
    "id": "user_001",
    "name": "John Doe",
    "primary_domain": "frontend",
    "skills": [...]
  }
}
```

**Response:**
```json
{
  "user": {
    "id": "user_001",
    "name": "John Doe",
    "primary_domain": "frontend",
    "skills": [...]
  },
  "matched_tasks": [
    {
      "task_id": "task_001",
      "name": "Implement user authentication",
      "match_score": 0.85,
      "min_complexity": 7,
      "time_estimate": 24.0,
      "skill_coverage": 0.75
    }
  ]
}
```

#### `POST /match-user-for-task`

Find matching users for a single task.

**Request Body:**
```json
{
  "project_id": "project_123",
  "manager_id": "manager_456",
  "task": {
    "task_id": "task_001",
    "name": "Implement user authentication",
    "complexity": 7,
    "estimated_hours": 24.0,
    "required_skills": [...]
  }
}
```

**Response:**
```json
{
  "task": {
    "task_id": "task_001",
    "name": "Implement user authentication",
    "complexity": 7,
    "estimated_hours": 24.0,
    "required_skills": [...]
  },
  "matched_users": [
    {
      "user_id": "user_001",
      "name": "John Doe",
      "match_score": 0.85,
      "skill_coverage": 0.75
    }
  ]
}
```

## PineconeSDK Class

### Overview

The `PineconeSDK` class provides a comprehensive interface for managing vector embeddings and performing semantic matching between users and tasks using Pinecone vector database.

### Constructor

```python
from PineconeSDK import PineconeSDK

# Initialize with default index names
matcher = PineconeSDK()

# Initialize with custom index names
matcher = PineconeSDK(
    skills_index="custom-skills-index",
    tasks_index="custom-tasks-index"
)
```

### Methods

#### `index_users(users: List[Dict], project_details: Dict[str, str])`

Index user skills in the vector database for semantic search.

**Parameters:**
- `users`: List of user dictionaries containing skills
- `project_details`: Dictionary with `project_id` and `manager_id`

**Example:**
```python
users = [
    {
        "id": "user_001",
        "name": "John Doe",
        "primary_domain": "frontend",
        "skills": [
            {
                "name": "React",
                "category": "frontend",
                "experience_years": 3,
                "proficiency_score": 85
            }
        ]
    }
]

project_details = {
    "project_id": "project_123",
    "manager_id": "manager_456"
}

matcher.index_users(users, project_details)
```

#### `index_tasks(tasks: List[Dict], project_details: Dict[str, str])`

Index tasks in the vector database for semantic search.

**Parameters:**
- `tasks`: List of task dictionaries
- `project_details`: Dictionary with `project_id` and `manager_id`

**Example:**
```python
tasks = [
    {
        "task_id": "task_001",
        "name": "Implement user authentication",
        "complexity": 7,
        "estimated_hours": 24.0,
        "required_skills": [
            {
                "name": "Node.js",
                "category": "backend",
                "preferred_experience": 2.0,
                "required_proficiency": 7
            }
        ]
    }
]

matcher.index_tasks(tasks, project_details)
```

#### `find_matching_users(task: Dict, users: List[str], project_details: Dict[str, str], top_k: int = 5)`

Find users that best match a task's requirements.

**Parameters:**
- `task`: Task dictionary with required skills
- `users`: List of user IDs to search within (empty list for all users)
- `project_details`: Dictionary with `project_id` and `manager_id`
- `top_k`: Maximum number of matches to return

**Returns:**
```python
[
    {
        "user_id": "user_001",
        "name": "John Doe",
        "match_score": 0.85,
        "skill_coverage": 0.75
    }
]
```

#### `find_matching_tasks(user: Dict, project_details: Dict[str, str], top_k: int = 5)`

Find tasks that best match a user's skills.

**Parameters:**
- `user`: User dictionary with skills
- `project_details`: Dictionary with `project_id` and `manager_id`
- `top_k`: Maximum number of matches to return

**Returns:**
```python
[
    {
        "task_id": "task_001",
        "name": "Implement user authentication",
        "match_score": 0.85,
        "min_complexity": 7,
        "time_estimate": 24.0,
        "skill_coverage": 0.75
    }
]
```

#### `delete_user_index(user_id: str, namespace: str = "user_skills")`

Delete all indexed skills for a specific user.

**Parameters:**
- `user_id`: ID of the user to delete
- `namespace`: Vector namespace (default: "user_skills")

#### `delete_task_index(task_id: str, namespace: str = "tasks")`

Delete a specific task from the index.

**Parameters:**
- `task_id`: ID of the task to delete
- `namespace`: Vector namespace (default: "tasks")

#### `delete_users(user_ids: List[str], namespace: str = "user_skills")`

Delete multiple users from the index.

**Parameters:**
- `user_ids`: List of user IDs to delete
- `namespace`: Vector namespace (default: "user_skills")

**Example:**
```python
user_ids = ["user_001", "user_002", "user_003"]
matcher.delete_users(user_ids)
```

#### `delete_tasks(task_ids: List[str], namespace: str = "tasks")`

Delete multiple tasks from the index.

**Parameters:**
- `task_ids`: List of task IDs to delete
- `namespace`: Vector namespace (default: "tasks")

**Example:**
```python
task_ids = ["task_001", "task_002", "task_003"]
matcher.delete_tasks(task_ids)
```

### Private Methods

#### `_calculate_skill_weight(skill: Dict) -> float`

Calculate skill importance weight based on experience and proficiency.

#### `_create_skill_document(skill: Dict, user_id: str, project_details: Dict[str, str])`

Create a document for indexing user skills.

#### `_create_task_document(task: Dict, project_details: Dict[str, str])`

Create a document for indexing tasks.

#### `_get_stable_id(entity_id: str, skill_name: str = None, is_user: bool = True)`

Generate deterministic IDs for vector storage.

#### `_initialize_index(index_name: str, dimensions: int = 1024, metric: str = "cosine")`

Initialize Pinecone index with specified configuration.

## BAML Client

### Overview

BAML (Boundary AI ML) provides AI-powered task generation using large language models. The client is auto-generated from BAML configuration files.

### Usage

```python
import baml_client as client

# Generate tasks from project description
response = client.b.GenerateRoadmap(
    "Build a scalable AI-powered content management system with React frontend and Python backend"
)

# Convert to dictionary format
tasks = to_dict(response)
```

### Available Functions

#### `GenerateRoadmap(raw_text: str) -> List[Tasks]`

Generate a comprehensive roadmap of tasks from a project description.

**Parameters:**
- `raw_text`: Project description text

**Returns:**
List of `Tasks` objects with the following structure:
- `task_id`: Unique identifier
- `name`: Task name
- `complexity`: Complexity level (1-10)
- `estimated_hours`: Time estimate
- `required_skills`: List of required skills
- `depends_on`: List of prerequisite task IDs

### BAML Configuration

The BAML client supports multiple AI providers:

#### Available Clients
- **GeminiClient**: Google Gemini 1.5 Flash
- **CustomGPT4o**: OpenAI GPT-4o
- **CustomGPT4oMini**: OpenAI GPT-4o Mini
- **CustomSonnet**: Anthropic Claude 3.5 Sonnet
- **CustomHaiku**: Anthropic Claude 3 Haiku
- **CustomFast**: Round-robin between GPT-4o Mini and Haiku
- **OpenaiFallback**: Fallback strategy for OpenAI models

#### Retry Policies
- **Constant**: Fixed delay between retries
- **Exponential**: Exponential backoff with configurable parameters

## Data Models

### Pydantic Models (FastAPI)

#### `BaseInput`
```python
class BaseInput(BaseModel):
    project_id: str
    manager_id: str
```

#### `GenTasksInput`
```python
class GenTasksInput(BaseInput):
    project_description: str
```

#### `UsersInput`
```python
class UsersInput(BaseInput):
    users: List[Dict[str, Any]]
```

#### `TasksInput`
```python
class TasksInput(BaseInput):
    tasks: List[Dict[str, Any]]
```

#### `SingleUser`
```python
class SingleUser(BaseInput):
    user: Dict[str, Any]
```

#### `SingleTask`
```python
class SingleTask(BaseInput):
    task: Dict[str, Any]
```

#### `DeleteUsersInput`
```python
class DeleteUsersInput(BaseInput):
    user_ids: List[str]
```

#### `DeleteTasksInput`
```python
class DeleteTasksInput(BaseInput):
    task_ids: List[str]
```

### BAML Generated Models

#### `Tasks`
```python
class Tasks(BaseModel):
    task_id: int
    name: str
    complexity: int  # 1-10 scale
    estimated_hours: float
    required_skills: List[Skills]
    depends_on: List[int]
```

#### `Skills`
```python
class Skills(BaseModel):
    name: str
    category: str
    preferred_experience: float  # 0-10 years
    required_proficiency: int  # 1-10 scale
```

### User Data Structure

```python
user = {
    "id": "user_001",
    "name": "John Doe",
    "primary_domain": "frontend",
    "skills": [
        {
            "name": "React",
            "category": "frontend",
            "experience_years": 3,
            "proficiency_score": 85
        }
    ]
}
```

### Task Data Structure

```python
task = {
    "task_id": "task_001",
    "name": "Implement user authentication",
    "complexity": 7,
    "estimated_hours": 24.0,
    "required_skills": [
        {
            "name": "Node.js",
            "category": "backend",
            "preferred_experience": 2.0,
            "required_proficiency": 7
        }
    ],
    "depends_on": ["task_000"]
}
```

## Utility Functions

### `to_dict(obj)`

Utility function to recursively convert non-subscriptable objects (with `__dict__`) to dictionaries.

**Parameters:**
- `obj`: Object to convert to dictionary

**Returns:**
- Dictionary representation of the object

**Example:**
```python
from main import to_dict

# Convert BAML response to dictionary
response = client.b.GenerateRoadmap("Build a web application")
tasks_dict = to_dict(response)
```

**Implementation:**
```python
def to_dict(obj):
    """Recursively convert non-subscriptable objects (with __dict__) to dicts."""
    if hasattr(obj, "__dict__"):
        return {k: to_dict(v) for k, v in vars(obj).items()}
    return [to_dict(item) for item in obj] if isinstance(obj, list) else obj
```

## Configuration

### Environment Variables

The `configs.py` module handles environment configuration:

```python
from configs import google_api_key, pinecone_api_key

# Required environment variables:
# - GOOGLE_API_KEY: For Google Gemini AI
# - PINECONE_API_KEY: For Pinecone vector database
# - OPENAI_API_KEY: (Optional) For OpenAI models
# - ANTHROPIC_API_KEY: (Optional) For Anthropic models
```

### Pinecone Configuration

Default Pinecone settings:
- **Region**: us-east-1
- **Cloud**: AWS
- **Metric**: Cosine similarity
- **Dimensions**: 768 (for sentence-transformers/all-MiniLM-L6-v2)

### Embedding Model

The service uses HuggingFace's `sentence-transformers/all-MiniLM-L6-v2` model for generating embeddings:
- **Dimensions**: 768
- **Normalization**: Enabled
- **Device**: CPU

## Error Handling

### Common Error Responses

All endpoints return HTTP 500 with error details on failure:

```json
{
  "detail": "Error message description"
}
```

### Exception Handling

The service implements comprehensive exception handling:

1. **Pinecone Connection Errors**: Automatic retry with exponential backoff
2. **AI Model Errors**: Handled by BAML's retry policies
3. **Validation Errors**: Pydantic model validation with detailed error messages
4. **Vector Search Errors**: Graceful degradation with empty results

### Debugging

Enable debug mode for detailed error information:

```python
# Set environment variable
DEBUG=True

# Or modify main.py
app = FastAPI(debug=True)
```

## Usage Examples

### Complete Workflow Example

```python
import requests
import json

base_url = "http://localhost:8000"

# 1. Generate tasks from project description
generate_response = requests.post(f"{base_url}/generate-tasks", json={
    "project_id": "project_123",
    "manager_id": "manager_456",
    "project_description": "Build a scalable AI-powered content management system"
})
tasks = generate_response.json()["tasks"]

# 2. Index users
users_data = {
    "project_id": "project_123",
    "manager_id": "manager_456",
    "users": [
        {
            "id": "user_001",
            "name": "John Doe",
            "primary_domain": "frontend",
            "skills": [
                {
                    "name": "React",
                    "category": "frontend",
                    "experience_years": 3,
                    "proficiency_score": 85
                }
            ]
        }
    ]
}
requests.post(f"{base_url}/index-users", json=users_data)

# 3. Index tasks
tasks_data = {
    "project_id": "project_123",
    "manager_id": "manager_456",
    "tasks": tasks
}
requests.post(f"{base_url}/index-tasks", json=tasks_data)

# 4. Find matching tasks for user
match_response = requests.post(f"{base_url}/match-tasks-for-user", json={
    "project_id": "project_123",
    "manager_id": "manager_456",
    "user": users_data["users"][0]
})
matches = match_response.json()
```

### Python SDK Usage

```python
from PineconeSDK import PineconeSDK
import baml_client as client

# Initialize SDK
matcher = PineconeSDK()

# Generate tasks
tasks = client.b.GenerateRoadmap("Build a web application with React and Node.js")

# Index and match
project_details = {"project_id": "proj_1", "manager_id": "mgr_1"}
matcher.index_tasks(tasks, project_details)
matcher.index_users(users, project_details)

# Find matches
matches = matcher.find_matching_users(tasks[0], [], project_details)
```

### Batch Processing

```python
import asyncio
import aiohttp

async def batch_match_users(users, project_details):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for user in users:
            task = session.post(
                f"{base_url}/match-tasks-for-user",
                json={**project_details, "user": user}
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        return [await resp.json() for resp in responses]

# Usage
matches = await batch_match_users(users, project_details)
```

## Performance Considerations

### Scaling Recommendations

1. **Vector Database**: Use Pinecone's pod-based indexes for high-throughput applications
2. **Embeddings**: Consider using GPU acceleration for large-scale embedding generation
3. **Caching**: Implement Redis caching for frequently accessed matches
4. **Batch Processing**: Use batch operations for indexing large datasets

### Monitoring

Monitor key metrics:
- **Response Time**: API endpoint latency
- **Vector Search Performance**: Pinecone query times
- **AI Model Usage**: BAML function call rates
- **Index Size**: Number of vectors stored

### Security

1. **API Keys**: Store in environment variables or secure key management
2. **Rate Limiting**: Implement rate limiting for production deployments
3. **Input Validation**: All inputs are validated through Pydantic models
4. **CORS**: Configure CORS settings for web applications

## Support and Troubleshooting

### Common Issues

1. **Environment Variables**: Ensure all required API keys are set
2. **Pinecone Limits**: Check index limits and upgrade plan if needed
3. **Model Availability**: Verify AI model availability in your region
4. **Dependencies**: Ensure all requirements are installed with correct versions

### Logging

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Checks

Use the health check endpoint to verify service status:

```bash
curl http://localhost:8000/health-check
```

This documentation provides comprehensive coverage of all public APIs, functions, and components in the codebase. For additional questions or feature requests, please refer to the source code or contact the development team.