from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from UpstashVectorStore import UpstashVectorStore
from crewai_agents import generate_tasks

app = FastAPI(
    title="OptiPlan AI Service",
    description="AI-powered task generation and matching using CrewAI and Gemini embeddings",
    version="2.0.0"
)

# Initialize matcher lazily to avoid cold start issues
_matcher = None

def get_matcher() -> UpstashVectorStore:
    """Get or create the UpstashVectorStore instance."""
    global _matcher
    if _matcher is None:
        _matcher = UpstashVectorStore()
    return _matcher


# ======================
# Pydantic Request Models
# ======================


class BaseInput(BaseModel):
    project_id: str
    manager_id: str


class GenTasksInput(BaseInput):
    project_description: str


class UsersInput(BaseInput):
    users: List[Dict[str, Any]]


class TasksInput(BaseInput):
    tasks: List[Dict[str, Any]]


class SingleUser(BaseInput):
    user: Dict[str, Any]


class SingleTask(BaseInput):
    task: Dict[str, Any]


class DeleteUsersInput(BaseInput):
    user_ids: List[str]


class DeleteTasksInput(BaseInput):
    task_ids: List[str]


# ======================
# API Endpoints
# ======================


@app.get("/")
async def root():
    return {"message": "OptiPlan AI Service - Powered by CrewAI and Gemini AI", "status": "healthy"}


@app.get("/health-check")
async def health_check():
    return {"message": "Service is up and running"}

    
@app.post("/generate-tasks")
async def generate_tasks_endpoint(data: GenTasksInput):
    try:
        # Use CrewAI to generate tasks
        tasks = generate_tasks(data.project_description)
        
        # Process tasks to add project and manager IDs
        for task in tasks:
            task["task_id"] = f'{data.project_id}_{task.get("task_id", len(tasks))}'
            task["project_id"] = data.project_id
            task["manager_id"] = data.manager_id
            if "depends_on" in task:
                task["depends_on"] = [
                    f'{data.project_id}_{dep}' for dep in task["depends_on"]
                ]
        return {"tasks": tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/index-users")
async def index_users(data: UsersInput):
    try:
        matcher = get_matcher()
        project_details = {"project_id": data.project_id, "manager_id": data.manager_id}
        matcher.index_users(data.users, project_details)
        return {"message": "Users indexed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/index-tasks")
async def index_tasks(data: TasksInput):
    try:
        matcher = get_matcher()
        project_details = {"project_id": data.project_id, "manager_id": data.manager_id}
        matcher.index_tasks(data.tasks, project_details)
        return {"message": "Tasks indexed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/match-tasks-for-users")
async def match_tasks_for_users(data: UsersInput):
    try:
        matcher = get_matcher()
        updated_users = []
        project_details = {"project_id": data.project_id, "manager_id": data.manager_id}
        for user in data.users:
            matches = matcher.find_matching_tasks(user, project_details)
            user["matched_tasks"] = matches
            updated_users.append(user)
        return {"users": updated_users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/match-users-for-tasks")
async def match_users_for_tasks(data: TasksInput):
    try:
        matcher = get_matcher()
        updated_tasks = []
        project_details = {"project_id": data.project_id, "manager_id": data.manager_id}
        for task in data.tasks:
            matches = matcher.find_matching_users(task, [], project_details)
            task["matched_users"] = matches
            updated_tasks.append(task)
        return {"tasks": updated_tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/match-tasks-for-user")
async def match_tasks_for_user(data: SingleUser):
    try:
        matcher = get_matcher()
        user = data.user
        project_details = {"project_id": data.project_id, "manager_id": data.manager_id}
        matches = matcher.find_matching_tasks(user, project_details)
        return {"user": user, "matched_tasks": matches}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/match-user-for-task")
async def match_user_for_task(data: SingleTask):
    try:
        matcher = get_matcher()
        task = data.task
        project_details = {"project_id": data.project_id, "manager_id": data.manager_id}
        matches = matcher.find_matching_users(task, [], project_details)
        return {"task": task, "matched_users": matches}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/delete-indexed-users")
async def delete_indexed_users(data: DeleteUsersInput):
    try:
        matcher = get_matcher()
        matcher.delete_users(data.user_ids)
        return {"message": "Users Index deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/delete-indexed-tasks")
async def delete_indexed_tasks(data: DeleteTasksInput):
    try:
        matcher = get_matcher()
        matcher.delete_tasks(data.task_ids)
        return {"message": "Tasks Index deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# Vercel handler
def handler(request, response):
    return app(request, response)
