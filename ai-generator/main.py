from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from PineconeSDK import PineconeSDK
import baml_client as client

app = FastAPI()

def to_dict(obj):
    """Recursively convert non-subscriptable objects (with __dict__) to dicts."""
    if hasattr(obj, '__dict__'):
        return {k: to_dict(v) for k, v in vars(obj).items()}
    if isinstance(obj, list):
        return [to_dict(item) for item in obj]
    return obj


# Create a global instance of your Pinecone matcher.
matcher = PineconeSDK(index_name="project-embeddings")


# ======================
# Pydantic Request Models
# ======================

class ProjectDescription(BaseModel):
    project_description: str


class UsersTasks(BaseModel):
    users: List[Dict[str, Any]]
    tasks: List[Dict[str, Any]]


class UsersInput(BaseModel):
    users: List[Dict[str, Any]]


class TasksInput(BaseModel):
    tasks: List[Dict[str, Any]]


class SingleUser(BaseModel):
    user: Dict[str, Any]


class SingleTask(BaseModel):
    task: Dict[str, Any]


# ======================
# API Endpoints
# ======================

@app.post("/generate-tasks")
async def generate_tasks(desc: ProjectDescription):
    """
    Generate tasks from a given project description.
    This endpoint:
      - Invokes the roadmap generator,
      - Converts the response to a dict (list of tasks),
      - Indexes the tasks into Pinecone,
      - Returns the tasks.
    """
    try:
        response = client.b.GenerateRoadmap(desc.project_description)
        tasks = to_dict(response)
        # Optionally index the generated tasks.
        matcher.index_tasks(tasks)
        return {"tasks": tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/index-users-tasks")
async def index_users_tasks(data: UsersTasks):
    """
    Index a given set of users and tasks.
    The request body should contain two keys: 'users' and 'tasks'.
    """
    try:
        matcher.index_users(data.users)
        matcher.index_tasks(data.tasks)
        return {"message": "Users and tasks indexed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/match-tasks-for-users")
async def match_tasks_for_users(data: UsersInput):
    """
    For each user provided in the request body, find the best matching tasks.
    The matched tasks are embedded under the 'matched_tasks' field in the user object.
    """
    try:
        updated_users = []
        for user in data.users:
            matches = matcher.find_matching_tasks(user)
            user["matched_tasks"] = matches
            updated_users.append(user)
        return {"users": updated_users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/match-users-for-tasks")
async def match_users_for_tasks(data: TasksInput):
    """
    For each task provided in the request body, find the best matching users.
    The matched users are embedded under the 'matched_users' field in the task object.
    """
    try:
        updated_tasks = []
        for task in data.tasks:
            matches = matcher.find_matching_users(task)
            task["matched_users"] = matches
            updated_tasks.append(task)
        return {"tasks": updated_tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/match-tasks-for-user")
async def match_tasks_for_user(data: SingleUser):
    """
    Find matching tasks for a single user.
    """
    try:
        user = data.user
        matches = matcher.find_matching_tasks(user)
        return {"user": user, "matched_tasks": matches}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/match-user-for-task")
async def match_user_for_task(data: SingleTask):
    """
    Find matching users for a single task.
    """
    try:
        task = data.task
        matches = matcher.find_matching_users(task)
        return {"task": task, "matched_users": matches}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
