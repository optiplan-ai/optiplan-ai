from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from typing import Dict, List
from langchain.schema import Document
import numpy as np
import hashlib
import time
import os
from configs import pinecone_api_key

class PineconeSDK:
    def __init__(self, project_id: str, manager_id: str, index_name: str = "project-embeddings-dev"):
        """
        Initialize the SDK with a specific project identifier.
        Data will be tagged with project_id in the metadata, and queries will filter on that field.
        """
        self.project_id = project_id  # Unique identifier for the project
        self.manager_id = manager_id  # Unique identifier for the project manager

        # Initialize HuggingFace embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-mpnet-base-v2"
        )

        # Text splitter for processing descriptions
        self.text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200
        )

        # Initialize Pinecone
        pc = Pinecone(api_key=pinecone_api_key)

        existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
        if index_name not in existing_indexes:
            pc.create_index(
                name=index_name,
                dimension=768,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                ),
                deletion_protection="disabled"
            )
            while not pc.describe_index(index_name).status["ready"]:
                time.sleep(1)

        index = pc.Index(index_name)
        self.vector_store = PineconeVectorStore(index=index, embedding=self.embeddings)

    def _create_skill_document(self, skill: Dict, user_id: str) -> Document:
        """Create a document for a single user skill with metadata."""
        content = (
            f"Skill: {skill['name']}\n"
            f"Category: {skill['category']}\n"
            f"Experience: {skill.get('experience_years', 'N/A')}y\n"
            f"Proficiency: {skill.get('proficiency_score', 'N/A')}"
        )

        metadata = {
            "skill_name": skill["name"],
            "skill_category": skill["category"],
            "experience": skill.get("experience_years", 0),
            "proficiency": skill.get("proficiency_score", 0),
            "user_id": user_id,
            "project_id": self.project_id,
            "manager_id": self.manager_id
        }

        return Document(page_content=content, metadata=metadata)

    def _create_task_document(self, task: Dict) -> Document:
        """Create a document for a complete task with joined skills."""
        skill_names = [skill["name"] for skill in task["required_skills"]]

        content = (
            f"Task: {task['name']}\n"
            f"Required Skills: {', '.join(skill_names)}\n"
        )

        metadata = {
            "task_id": task["task_id"],
            "task_name": task["name"],
            "required_skills": skill_names,
            "min_complexity": task["complexity"],
            "time_estimate": task["estimated_hours"],
            "project_id": self.project_id,
            "manager_id": self.manager_id
        }

        return Document(page_content=content, metadata=metadata)

    def _get_stable_id(self, entity_id: str, skill_name: str = None, is_user: bool = True) -> str:
        """Generate a deterministic ID for vectors."""
        if is_user:
            base = f"user_{entity_id}_skill_{skill_name}"
        else:
            base = f"task_{entity_id}"
        return hashlib.md5(base.encode()).hexdigest()

    def index_users(self, users: List[Dict]):
        """Index individual skills from users with project_id stored in metadata."""
        all_docs = []
        all_ids = []

        for user in users:
            for skill in user["skills"]:
                doc = self._create_skill_document(skill, user["id"])
                doc.metadata.update({
                    "user_id": user["id"],
                    "user_name": user["name"],
                    "primary_domain": user["primary_domain"],
                    "project_id": self.project_id,
                    "manager_id": self.manager_id,
                })
                all_docs.append(doc)
                all_ids.append(self._get_stable_id(user["id"], skill["name"], True))

        self.vector_store.add_texts(
            texts=[doc.page_content for doc in all_docs],
            metadatas=[doc.metadata for doc in all_docs],
            ids=all_ids,
            namespace="user_skills",
            batch_size=100,
            upsert=True
        )

    def index_tasks(self, tasks: List[Dict]):
        """Index complete tasks with project_id stored in metadata."""
        all_docs = []
        all_ids = []

        for task in tasks:
            doc = self._create_task_document(task)
            all_docs.append(doc)
            all_ids.append(self._get_stable_id(task["task_id"], is_user=False))

        self.vector_store.add_texts(
            texts=[doc.page_content for doc in all_docs],
            metadatas=[doc.metadata for doc in all_docs],
            ids=all_ids,
            namespace="tasks",
            batch_size=100,
            upsert=True
        )

    def find_matching_users(self, task: Dict, users: List[str] = [], top_k: int = 5) -> List[Dict]:
        """Find best matching users for a task within the specified project by filtering on metadata."""
        matches = {}  # user_id -> matching data
        required_skills = set(skill["name"] for skill in task["required_skills"])

        # Create search filter based on the task's requirements and project id
        search_filter = {
            # "availability": {"$gte": task["estimated_hours"] / 20},
            # "max_complexity": {"$gte": task["complexity"] * 0.7},
            "skill_name": {"$in": list(required_skills)},
        }

        if len(users) > 0:
            search_filter["user_id"] = {"$in": users}

        results = self.vector_store.similarity_search_with_score(
            self._create_task_document(task).page_content,
            k=top_k * len(required_skills),  # Get more results to account for multiple skills
            namespace="user_skills",
            filter=search_filter
        )

        for doc, score in results:
            user_id = doc.metadata["user_id"]
            if user_id not in matches:
                matches[user_id] = {
                    "user_id": user_id,
                    "name": doc.metadata["user_name"],
                    "match_scores": [],
                    "matched_skills": set()
                }
            matches[user_id]["match_scores"].append(1 - score)
            matches[user_id]["matched_skills"].add(doc.metadata["skill_name"])

        final_matches = []
        for user_data in matches.values():
            skill_coverage = len(user_data["matched_skills"]) / len(required_skills)
            avg_score = np.mean(user_data["match_scores"])
            user_data["match_score"] = avg_score * skill_coverage
            del user_data["match_scores"]
            del user_data["matched_skills"]
            final_matches.append(user_data)

        return sorted(final_matches, key=lambda x: x["match_score"], reverse=True)[:top_k]

    def find_matching_tasks(self, user: Dict, top_k: int = 5) -> List[Dict]:
        """Find best matching tasks for a user within the specified project by filtering on metadata."""
        user_skills = set(skill["name"] for skill in user["skills"])

        # Create a composite document from user's skills
        skill_docs = [self._create_skill_document(skill, user["id"]) for skill in user["skills"]]
        composite_content = "\n\n".join(doc.page_content for doc in skill_docs)

        # Filter by project_id in tasks
        search_filter = {"project_id": self.project_id}

        results = self.vector_store.similarity_search_with_score(
            composite_content,
            k=top_k,
            namespace="tasks",
            filter=search_filter
        )

        matches = []
        for doc, score in results:
            required_skills = set(doc.metadata["required_skills"])
            skill_coverage = len(required_skills.intersection(user_skills)) / len(required_skills)
            match_data = {
                "task_id": doc.metadata["task_id"],
                "name": doc.metadata["task_name"],
                "match_score": (1 - score) * skill_coverage,
                "min_complexity": doc.metadata["min_complexity"],
                "time_estimate": doc.metadata["time_estimate"],
                "skill_coverage": skill_coverage
            }
            matches.append(match_data)

        return sorted(matches, key=lambda x: x["match_score"], reverse=True)[:top_k]
