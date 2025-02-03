from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from typing import Dict, List
from langchain.schema import Document
import numpy as np
import hashlib
import time
from configs import pinecone_api_key


class PineconeSDK:
    def __init__(
        self,
        skills_index: str = "skills-embeddings",
        tasks_index: str = "tasks-embeddings",
    ):
        """
        Initialize SDK with separate vector spaces for skills and tasks.
        """
        self.pc = Pinecone(api_key=pinecone_api_key)

        # Specialized embeddings for skills (optimized for technical terms and expertise)
        self.skills_embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-large-en",
            model_kwargs={"device": "cpu"},
            encode_kwargs={
                "normalize_embeddings": True,
                "instruction": "Represent this professional skill for matching with job requirements:",
            },
        )

        # Specialized embeddings for tasks (optimized for project requirements)
        self.tasks_embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-large-en",
            model_kwargs={"device": "cpu"},
            encode_kwargs={
                "normalize_embeddings": True,
                "instruction": "Represent this project task for matching with professional skills:",
            },
        )

        # Initialize Pinecone indexes for skills and tasks
        skills_index = self._initialize_index(skills_index)
        tasks_index = self._initialize_index(tasks_index)

        # Create separate vector stores
        self.skills_store = PineconeVectorStore(
            index=self.pc.Index(skills_index), embedding=self.skills_embeddings
        )

        self.tasks_store = PineconeVectorStore(
            index=self.pc.Index(tasks_index), embedding=self.tasks_embeddings
        )

    def _initialize_index(
        self,
        index_name: str,
        dimensions: int = 1024,
        metric: str = "cosine",
        spec: ServerlessSpec = None,
    ) -> str:
        """Initialize a new index with the specified name."""
        existing_indexes = [index_info["name"] for index_info in self.pc.list_indexes()]
        if index_name not in existing_indexes:
            self.pc.create_index(
                name=index_name,
                dimension=768,
                metric=metric,
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                deletion_protection="disabled",
            )
            while not self.pc.describe_index(index_name).status["ready"]:
                time.sleep(1)
        return index_name

    def _calculate_skill_weight(self, skill: Dict) -> float:
        """Calculate skill importance weight based on multiple factors."""
        # Base weights
        experience_weight = min(
            skill.get("experience_years", 0) / 10.0, 1.0
        )  # Cap at 10 years
        proficiency_weight = skill.get("proficiency_score", 0) / 100.0

        # Category importance multipliers
        category_multipliers = {
            "frontend": 1.1,
            "backend": 1.1,
            "database": 1.15,
            "cloud": 1.15,
            "design": 1.1,
            "management": 1.0,
        }

        category_multiplier = category_multipliers.get(
            skill["skill_category"].lower(), 1.0
        )

        # Combine weights
        return (
            0.4 * experience_weight + 0.6 * proficiency_weight
        ) * category_multiplier

    def _create_skill_document(
        self, skill: Dict, user_id: str, project_details: Dict[str, str]
    ) -> Document:
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
            "project_id": project_details["project_id"],
            "manager_id": project_details["manager_id"],
            # Store the content as well for later retrieval
            "page_content": content,
        }

        return Document(page_content=content, metadata=metadata)

    def _create_task_document(
        self, task: Dict, project_details: Dict[str, str]
    ) -> Document:
        """Create a document for a complete task with joined skills."""
        skill_names = [skill["name"] for skill in task["required_skills"]]
        content = f"Task: {task['name']}\n" f"Required Skills: {', '.join(skill_names)}"

        metadata = {
            "task_id": task["task_id"],
            "task_name": task["name"],
            "required_skills": skill_names,
            "min_complexity": task["complexity"],
            "time_estimate": task["estimated_hours"],
            "project_id": project_details["project_id"],
            "manager_id": project_details["manager_id"],
            # Store the content as well for later retrieval
            "page_content": content,
        }

        return Document(page_content=content, metadata=metadata)

    def _get_stable_id(
        self, entity_id: str, skill_name: str = None, is_user: bool = True
    ) -> str:
        """Generate a deterministic ID for vectors."""
        if is_user:
            base = f"user_{entity_id}_skill_{skill_name}"
        else:
            base = f"task_{entity_id}"
        return hashlib.md5(base.encode()).hexdigest()

    def index_users(self, users: List[Dict], project_details: Dict[str, str]):
        """Index user skills in the skills vector space."""
        all_docs = []
        all_ids = []

        for user in users:
            for skill in user["skills"]:
                doc = self._create_skill_document(skill, user["id"], project_details)
                doc.metadata.update(
                    {
                        "user_id": user["id"],
                        "user_name": user["name"],
                        "primary_domain": user["primary_domain"],
                        "project_id": project_details["project_id"],
                        "manager_id": project_details["manager_id"],
                    }
                )
                all_docs.append(doc)
                all_ids.append(self._get_stable_id(user["id"], skill["name"]))

        self.skills_store.add_texts(
            texts=[doc.page_content for doc in all_docs],
            metadatas=[doc.metadata for doc in all_docs],
            ids=all_ids,
            namespace="user_skills",
            batch_size=100,
            upsert=True,
        )

    def index_tasks(self, tasks: List[Dict], project_details: Dict[str, str]):
        """Index tasks in the tasks vector space."""
        all_docs = []
        all_ids = []

        for task in tasks:
            doc = self._create_task_document(task, project_details)
            all_docs.append(doc)
            all_ids.append(self._get_stable_id(task["task_id"], is_user=False))

        self.tasks_store.add_texts(
            texts=[doc.page_content for doc in all_docs],
            metadatas=[doc.metadata for doc in all_docs],
            ids=all_ids,
            namespace="tasks",
            batch_size=100,
            upsert=True,
        )

    def find_matching_users(
        self,
        task: Dict,
        users: List[str],
        project_details: Dict[str, str],
        top_k: int = 5,
    ) -> List[Dict]:
        """Find matching users by querying the skills space with task requirements."""
        matches = {}
        required_skills = set(skill["name"] for skill in task["required_skills"])

        # Create task embedding query
        task_doc = self._create_task_document(task, project_details)

        # Search in skills space
        search_filter = {
            # "availability": {"$gte": task["estimated_hours"] / 20},
            # "max_complexity": {"$gte": task["complexity"] * 0.7},
            # "skill_name": {"$in": list(required_skills)},
            "project_id": project_details["project_id"],
            "manager_id": project_details["manager_id"],
        }

        if users:
            search_filter["user_id"] = {"$in": users}

        results = self.skills_store.similarity_search_with_score(
            task_doc.page_content, k=top_k * len(required_skills), filter=search_filter
        )

        # Enhanced scoring with skill space specific metrics
        for doc, score in results:
            user_id = doc.metadata["user_id"]
            if user_id not in matches:
                matches[user_id] = {
                    "user_id": user_id,
                    "name": doc.metadata["user_name"],
                    "match_scores": [],
                    "matched_skills": set(),
                    "skill_weights": [],
                }

            skill_weight = self._calculate_skill_weight(doc.metadata)
            matches[user_id]["match_scores"].append(1 - score)
            matches[user_id]["matched_skills"].add(doc.metadata["skill_name"])
            matches[user_id]["skill_weights"].append(skill_weight)

        # Final ranking with specialized scoring for skills space
        final_matches = []
        for user_data in matches.values():
            skill_coverage = len(user_data["matched_skills"]) / len(required_skills)
            avg_score = np.mean(user_data["match_scores"])
            avg_weight = np.mean(user_data["skill_weights"])

            final_score = avg_score * 0.4 + skill_coverage * 0.4 + avg_weight * 0.2

            final_matches.append(
                {
                    "user_id": user_data["user_id"],
                    "name": user_data["name"],
                    "match_score": final_score,
                    "skill_coverage": skill_coverage,
                }
            )

        return sorted(final_matches, key=lambda x: x["match_score"], reverse=True)[
            :top_k
        ]

    def find_matching_tasks(
        self, user: Dict, project_details: Dict[str, str], top_k: int = 5
    ) -> List[Dict]:
        """Find matching tasks by querying the tasks space with user skills."""
        user_skills = set(skill["name"] for skill in user["skills"])

        # Create composite skill document for querying
        skill_docs = [
            self._create_skill_document(skill, user["id"], project_details)
            for skill in user["skills"]
        ]
        composite_content = "\n\n".join(doc.page_content for doc in skill_docs)

        # Search in tasks space
        search_filter = {
            "project_id": project_details["project_id"],
            "manager_id": project_details["manager_id"],
        }

        results = self.tasks_store.similarity_search_with_score(
            composite_content, k=top_k, filter=search_filter
        )

        # Enhanced scoring with task space specific metrics
        matches = []
        for doc, score in results:
            required_skills = set(doc.metadata["required_skills"])
            skill_coverage = (
                len(required_skills.intersection(user_skills)) / len(required_skills)
                if required_skills
                else 0
            )

            match_data = {
                "task_id": doc.metadata["task_id"],
                "name": doc.metadata["task_name"],
                "match_score": (1 - score) * skill_coverage,
                "min_complexity": doc.metadata["min_complexity"],
                "time_estimate": doc.metadata["time_estimate"],
                "skill_coverage": skill_coverage,
            }
            matches.append(match_data)

        return sorted(matches, key=lambda x: x["match_score"], reverse=True)[:top_k]
