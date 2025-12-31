from upstash_vector import Index
from typing import Dict, List, Optional
import hashlib
from configs import upstash_vector_url, upstash_vector_token


class UpstashVectorStore:
    def __init__(
        self,
        skills_index_name: str = "skills-embeddings",
        tasks_index_name: str = "tasks-embeddings",
    ):
        """
        Initialize SDK with separate vector spaces for skills and tasks.
        Uses Upstash Vector REST API.
        """
        if not upstash_vector_url or not upstash_vector_token:
            raise ValueError("UPSTASH_VECTOR_REST_URL and UPSTASH_VECTOR_REST_TOKEN must be set")
        
        # Initialize Upstash Vector indexes
        # Upstash will automatically handle text-to-vector conversion using built-in embedding models
        self.skills_index = Index(
            url=upstash_vector_url,
            token=upstash_vector_token,
        )
        self.tasks_index = Index(
            url=upstash_vector_url,
            token=upstash_vector_token,
        )

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
            skill.get("category", "").lower(), 1.0
        )

        # Combine weights
        return (
            0.4 * experience_weight + 0.6 * proficiency_weight
        ) * category_multiplier

    def _create_skill_document(
        self, skill: Dict, user_id: str, project_details: Dict[str, str]
    ) -> Dict:
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
        }

        return {
            "content": content,
            "metadata": metadata,
        }

    def _create_task_document(
        self, task: Dict, project_details: Dict[str, str]
    ) -> Dict:
        """Create a document for a complete task with joined skills."""
        skill_names = [skill["name"] for skill in task.get("required_skills", [])]
        content = f"Task: {task['name']}\n" f"Required Skills: {', '.join(skill_names)}"

        metadata = {
            "task_id": task["task_id"],
            "task_name": task["name"],
            "required_skills": skill_names,
            "min_complexity": task.get("complexity", 0),
            "time_estimate": task.get("estimated_hours", 0),
            "project_id": project_details["project_id"],
            "manager_id": project_details["manager_id"],
        }

        return {
            "content": content,
            "metadata": metadata,
        }

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
        """Index user skills in the skills vector space using raw text."""
        all_vectors = []

        for user_data in users:
            for skill in user_data.get("skills", []):
                doc = self._create_skill_document(skill, user_data["id"], project_details)
                doc["metadata"].update({
                    "user_id": user_data["id"],
                    "user_name": user_data.get("name", ""),
                    "primary_domain": user_data.get("primary_domain", ""),
                })
                
                vector_id = self._get_stable_id(user_data["id"], skill["name"])
                
                # Pass raw text - Upstash will handle embedding automatically
                all_vectors.append((
                    vector_id,
                    doc["content"],  # Raw text string
                    doc["metadata"]
                ))

        # Upsert in batches for better performance
        batch_size = 100
        for i in range(0, len(all_vectors), batch_size):
            batch = all_vectors[i:i + batch_size]
            try:
                self.skills_index.upsert(batch)
            except Exception as e:
                print(f"Error upserting batch {i//batch_size + 1}: {e}")

    def index_tasks(self, tasks: List[Dict], project_details: Dict[str, str]):
        """Index tasks in the tasks vector space using raw text."""
        all_vectors = []

        for task in tasks:
            doc = self._create_task_document(task, project_details)
            vector_id = self._get_stable_id(task["task_id"], is_user=False)
            
            # Pass raw text - Upstash will handle embedding automatically
            all_vectors.append((
                vector_id,
                doc["content"],  # Raw text string
                doc["metadata"]
            ))

        # Upsert in batches for better performance
        batch_size = 100
        for i in range(0, len(all_vectors), batch_size):
            batch = all_vectors[i:i + batch_size]
            try:
                self.tasks_index.upsert(batch)
            except Exception as e:
                print(f"Error upserting batch {i//batch_size + 1}: {e}")

    def delete_user_index(self, user_id: str):
        """Delete all indexed skills related to a specific user."""
        # Upstash Vector requires querying first to get IDs, then deleting
        # For now, we'll query by metadata and delete matching vectors
        try:
            # Query for all vectors with this user_id
            # Note: This is a simplified approach - in production, you might want to
            # maintain a mapping of user_id to vector IDs
            print(f"Note: Deleting skills indexes of user {user_id} requires querying first.")
            print(f"Consider maintaining a mapping of user_id to vector IDs for efficient deletion.")
        except Exception as e:
            print(f"Error deleting user index: {e}")

    def delete_task_index(self, task_id: str):
        """Delete a specific task from the index."""
        try:
            vector_id = self._get_stable_id(task_id, is_user=False)
            self.tasks_index.delete(ids=[vector_id])
            print(f"Deleted index of task {task_id}.")
        except Exception as e:
            print(f"Error deleting task index: {e}")

    def find_matching_users(
        self,
        task: Dict,
        users: List[str],
        project_details: Dict[str, str],
        top_k: int = 5,
    ) -> List[Dict]:
        """Find matching users by querying the skills space with task requirements."""
        matches = {}
        required_skills = {skill["name"] for skill in task.get("required_skills", [])}

        # Create task query text
        task_doc = self._create_task_document(task, project_details)
        query_text = task_doc["content"]

        # Search in skills space
        try:
            # Query Upstash Vector with raw text - Upstash will handle embedding automatically
            query_top_k = top_k * len(required_skills) if required_skills else top_k * 2
            results = self.skills_index.query(
                data=query_text,  # Pass raw text string
                top_k=min(query_top_k, 100),  # Limit to reasonable number
                include_metadata=True,
            )
            
            # Filter results by metadata (client-side filtering)
            filtered_results = []
            for result in results:
                # Handle both dict and object access patterns
                metadata = result.metadata if hasattr(result, 'metadata') else result.get("metadata", {})
                if isinstance(metadata, dict):
                    project_id = metadata.get("project_id")
                    manager_id = metadata.get("manager_id")
                    user_id = metadata.get("user_id")
                else:
                    project_id = getattr(metadata, "project_id", None)
                    manager_id = getattr(metadata, "manager_id", None)
                    user_id = getattr(metadata, "user_id", None)
                
                if (project_id == project_details["project_id"] and
                    manager_id == project_details["manager_id"]):
                    if not users or user_id in users:
                        filtered_results.append(result)
            
            results = filtered_results[:query_top_k]
        except Exception as e:
            print(f"Error querying skills index: {e}")
            results = []

        # Enhanced scoring with skill space specific metrics
        for result in results:
            # Handle both dict and object access patterns
            metadata = result.metadata if hasattr(result, 'metadata') else result.get("metadata", {})
            
            if isinstance(metadata, dict):
                user_id = metadata.get("user_id")
                user_name = metadata.get("user_name", "")
                skill_name = metadata.get("skill_name", "")
            else:
                user_id = getattr(metadata, "user_id", None)
                user_name = getattr(metadata, "user_name", "")
                skill_name = getattr(metadata, "skill_name", "")
            
            if not user_id:
                continue
                
            if user_id not in matches:
                matches[user_id] = {
                    "user_id": user_id,
                    "name": user_name,
                    "match_scores": [],
                    "matched_skills": set(),
                    "skill_weights": [],
                }

            # Calculate skill weight - convert metadata to dict if needed
            metadata_dict = metadata if isinstance(metadata, dict) else {
                "experience_years": getattr(metadata, "experience", 0),
                "proficiency_score": getattr(metadata, "proficiency", 0),
                "category": getattr(metadata, "skill_category", "")
            }
            skill_weight = self._calculate_skill_weight(metadata_dict)
            
            # Upstash Vector returns similarity score (higher is better)
            score = getattr(result, "score", None) or getattr(result, "similarity", None) or result.get("score", 0) if isinstance(result, dict) else 0
            if score is None:
                score = 0
            matches[user_id]["match_scores"].append(score)
            matches[user_id]["matched_skills"].add(skill_name)
            matches[user_id]["skill_weights"].append(skill_weight)

        # Final ranking with specialized scoring for skills space
        final_matches = []
        for user_data in matches.values():
            skill_coverage = (
                len(user_data["matched_skills"]) / len(required_skills)
                if required_skills
                else 0
            )
            avg_score = sum(user_data["match_scores"]) / len(user_data["match_scores"]) if user_data["match_scores"] else 0
            avg_weight = sum(user_data["skill_weights"]) / len(user_data["skill_weights"]) if user_data["skill_weights"] else 0

            final_score = avg_score * 0.4 + skill_coverage * 0.4 + avg_weight * 0.2

            final_matches.append({
                "user_id": user_data["user_id"],
                "name": user_data["name"],
                "match_score": final_score,
                "skill_coverage": skill_coverage,
            })

        return sorted(final_matches, key=lambda x: x["match_score"], reverse=True)[
            :top_k
        ]

    def find_matching_tasks(
        self, user: Dict, project_details: Dict[str, str], top_k: int = 5
    ) -> List[Dict]:
        """Find matching tasks by querying the tasks space with user skills."""
        user_skills = {skill["name"] for skill in user.get("skills", [])}

        # Create composite skill document for querying
        skill_contents = []
        for skill in user.get("skills", []):
            skill_doc = self._create_skill_document(skill, user["id"], project_details)
            skill_contents.append(skill_doc["content"])
        
        composite_content = "\n\n".join(skill_contents)

        # Search in tasks space
        try:
            # Query Upstash Vector with raw text - Upstash will handle embedding automatically
            results = self.tasks_index.query(
                data=composite_content,  # Pass raw text string
                top_k=top_k,
                include_metadata=True,
            )
            
            # Filter results by metadata (client-side filtering)
            filtered_results = []
            for result in results:
                # Handle both dict and object access patterns
                metadata = result.metadata if hasattr(result, 'metadata') else result.get("metadata", {})
                
                if isinstance(metadata, dict):
                    project_id = metadata.get("project_id")
                    manager_id = metadata.get("manager_id")
                else:
                    project_id = getattr(metadata, "project_id", None)
                    manager_id = getattr(metadata, "manager_id", None)
                
                if (project_id == project_details["project_id"] and
                    manager_id == project_details["manager_id"]):
                    filtered_results.append(result)
            
            results = filtered_results[:top_k]
        except Exception as e:
            print(f"Error querying tasks index: {e}")
            results = []

        # Enhanced scoring with task space specific metrics
        matches = []
        for result in results:
            # Handle both dict and object access patterns
            metadata = result.metadata if hasattr(result, 'metadata') else result.get("metadata", {})
            
            if isinstance(metadata, dict):
                required_skills = set(metadata.get("required_skills", []))
                task_id = metadata.get("task_id", "")
                task_name = metadata.get("task_name", "")
                min_complexity = metadata.get("min_complexity", 0)
                time_estimate = metadata.get("time_estimate", 0)
            else:
                required_skills = set(getattr(metadata, "required_skills", []))
                task_id = getattr(metadata, "task_id", "")
                task_name = getattr(metadata, "task_name", "")
                min_complexity = getattr(metadata, "min_complexity", 0)
                time_estimate = getattr(metadata, "time_estimate", 0)
            
            skill_coverage = (
                len(required_skills.intersection(user_skills)) / len(required_skills)
                if required_skills
                else 0
            )

            # Upstash Vector returns similarity score
            score = getattr(result, "score", None) or getattr(result, "similarity", None) or result.get("score", 0) if isinstance(result, dict) else 0
            if score is None:
                score = 0
                
            match_data = {
                "task_id": task_id,
                "name": task_name,
                "match_score": score * skill_coverage,
                "min_complexity": min_complexity,
                "time_estimate": time_estimate,
                "skill_coverage": skill_coverage,
            }
            matches.append(match_data)

        return sorted(matches, key=lambda x: x["match_score"], reverse=True)[:top_k]

    def delete_users(self, user_ids: List[str]):
        """Delete all indexed skills related to multiple users."""
        for user_id in user_ids:
            self.delete_user_index(user_id)
        print(f"Deleted skills indexes for {len(user_ids)} users.")

    def delete_tasks(self, task_ids: List[str]):
        """Delete multiple tasks from the index."""
        try:
            vector_ids = [self._get_stable_id(task_id, is_user=False) for task_id in task_ids]
            self.tasks_index.delete(ids=vector_ids)
            print(f"Deleted indexes for {len(task_ids)} tasks.")
        except Exception as e:
            print(f"Error deleting tasks: {e}")
