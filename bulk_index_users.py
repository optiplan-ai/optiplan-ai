#!/usr/bin/env python3
"""
Bulk index user profiles from sample_data/user_profiles.json into Upstash Vector.

This script:
1. Reads user profiles from JSON
2. Maps skills to categories intelligently
3. Generates experience_years and proficiency_score based on user data
4. Formats data for the index_users API
5. Indexes all users via the AI service
"""

import json
import os
import sys
import requests
from typing import Dict, List, Any
from pathlib import Path

# Add parent directory to path to import configs
sys.path.insert(0, str(Path(__file__).parent))

from configs import upstash_vector_url, upstash_vector_token

# AI Service URL (default to localhost)
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://localhost:8000")

# Skill category mapping
SKILL_CATEGORIES = {
    # Frontend
    "react": "frontend",
    "vue": "frontend",
    "vue.js": "frontend",
    "angular": "frontend",
    "javascript": "frontend",
    "typescript": "frontend",
    "html": "frontend",
    "css": "frontend",
    "tailwind css": "frontend",
    "next.js": "frontend",
    "nuxt.js": "frontend",
    "svelte": "frontend",
    
    # Backend
    "node.js": "backend",
    "nodejs": "backend",
    "python": "backend",
    "django": "backend",
    "flask": "backend",
    "fastapi": "backend",
    "java": "backend",
    "spring boot": "backend",
    "express": "backend",
    "nest.js": "backend",
    "php": "backend",
    "laravel": "backend",
    "ruby": "backend",
    "ruby on rails": "backend",
    "go": "backend",
    "golang": "backend",
    "rust": "backend",
    "c#": "backend",
    ".net": "backend",
    "kotlin": "backend",
    "scala": "backend",
    "elixir": "backend",
    "phoenix": "backend",
    "perl": "backend",
    
    # Database
    "mysql": "database",
    "postgresql": "database",
    "mongodb": "database",
    "redis": "database",
    "sqlite": "database",
    "oracle": "database",
    "sql server": "database",
    "cassandra": "database",
    "dynamodb": "database",
    "firebase": "database",
    "core data": "database",
    
    # Cloud
    "aws": "cloud",
    "azure": "cloud",
    "gcp": "cloud",
    "google cloud": "cloud",
    "docker": "cloud",
    "kubernetes": "cloud",
    "terraform": "cloud",
    "ansible": "cloud",
    "jenkins": "cloud",
    "ci/cd": "cloud",
    
    # Design
    "figma": "design",
    "sketch": "design",
    "adobe xd": "design",
    "ui/ux": "design",
    "ui design": "design",
    "ux design": "design",
    
    # Management
    "project management": "management",
    "agile": "management",
    "scrum": "management",
    "kanban": "management",
    "product management": "management",
    "team leadership": "management",
    
    # Machine Learning / AI
    "machine learning": "backend",
    "tensorflow": "backend",
    "pytorch": "backend",
    "scikit-learn": "backend",
    "deep learning": "backend",
    "neural networks": "backend",
    "nlp": "backend",
    "computer vision": "backend",
    
    # Other
    "webassembly": "frontend",
    "blockchain": "backend",
    "system administration": "cloud",
    "linux": "cloud",
}


def map_skill_to_category(skill_name: str) -> str:
    """Map a skill name to its category."""
    skill_lower = skill_name.lower().strip()
    
    # Direct match
    if skill_lower in SKILL_CATEGORIES:
        return SKILL_CATEGORIES[skill_lower]
    
    # Partial match
    for key, category in SKILL_CATEGORIES.items():
        if key in skill_lower or skill_lower in key:
            return category
    
    # Default based on common patterns
    if any(word in skill_lower for word in ["react", "vue", "angular", "html", "css", "js", "javascript", "typescript"]):
        return "frontend"
    elif any(word in skill_lower for word in ["python", "java", "node", "django", "flask", "express", "api", "server"]):
        return "backend"
    elif any(word in skill_lower for word in ["sql", "database", "db", "mysql", "postgres", "mongo"]):
        return "database"
    elif any(word in skill_lower for word in ["aws", "azure", "cloud", "docker", "kubernetes", "devops"]):
        return "cloud"
    elif any(word in skill_lower for word in ["design", "ui", "ux", "figma", "sketch"]):
        return "design"
    elif any(word in skill_lower for word in ["management", "agile", "scrum", "leadership"]):
        return "management"
    
    # Default to backend for unknown skills
    return "backend"


def calculate_proficiency_score(
    experience_years: float,
    learning_speed: int,
    complexity_grasp: int
) -> int:
    """
    Calculate proficiency score (1-10) based on experience, learning speed, and complexity grasp.
    
    Formula:
    - Base: experience_years / 2 (capped at 5)
    - Learning speed multiplier: learning_speed / 10
    - Complexity grasp multiplier: complexity_grasp / 10
    - Final: (base * 0.4) + (learning_speed * 0.3) + (complexity_grasp * 0.3)
    """
    # Base score from experience (max 5 points)
    experience_score = min(experience_years / 2, 5.0)
    
    # Normalize learning_speed and complexity_grasp (assuming they're 1-10 scale)
    learning_score = (learning_speed / 10.0) * 5.0  # Max 5 points
    complexity_score = (complexity_grasp / 10.0) * 5.0  # Max 5 points
    
    # Weighted combination
    proficiency = (experience_score * 0.4) + (learning_score * 0.3) + (complexity_score * 0.3)
    
    # Scale to 1-10 and round
    proficiency = max(1, min(10, int(round(proficiency * 2))))
    
    return proficiency


def transform_user_profile(user: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform a user profile from the JSON format to the format expected by index_users.
    
    Input format:
    {
        "id": 1,
        "name": "Alice Johnson",
        "email": "alice.johnson@example.com",
        "skills": ["React", "JavaScript", "Node.js"],
        "experience": 5,
        "availability": 20,
        "learning_speed": 8,
        "complexity_grasp": 7
    }
    
    Output format:
    {
        "id": "1",
        "name": "Alice Johnson",
        "skills": [
            {
                "name": "React",
                "category": "frontend",
                "experience_years": 4.0,
                "proficiency_score": 7
            },
            ...
        ]
    }
    """
    user_id = str(user["id"])
    experience_years = float(user.get("experience", 0))
    learning_speed = user.get("learning_speed", 5)
    complexity_grasp = user.get("complexity_grasp", 5)
    
    # Transform skills
    transformed_skills = []
    for skill_name in user.get("skills", []):
        category = map_skill_to_category(skill_name)
        
        # Calculate experience years for this specific skill
        # Assume user has been using this skill for a portion of their total experience
        # More experienced users likely have more years per skill
        skill_experience = min(experience_years * 0.8, experience_years - 1) if experience_years > 1 else experience_years
        
        # Calculate proficiency score
        proficiency = calculate_proficiency_score(
            skill_experience,
            learning_speed,
            complexity_grasp
        )
        
        transformed_skills.append({
            "name": skill_name,
            "category": category,
            "experience_years": round(skill_experience, 1),
            "proficiency_score": proficiency
        })
    
    return {
        "id": user_id,
        "name": user.get("name", f"User {user_id}"),
        "primary_domain": None,  # Can be set later if needed
        "skills": transformed_skills
    }


def load_user_profiles(file_path: str) -> List[Dict[str, Any]]:
    """Load user profiles from JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def index_users_bulk(
    users: List[Dict[str, Any]],
    project_id: str = "bulk-index-project",
    manager_id: str = "bulk-index-manager"
) -> bool:
    """Index users via the AI service."""
    url = f"{AI_SERVICE_URL}/index-users"
    
    payload = {
        "users": users,
        "project_id": project_id,
        "manager_id": manager_id
    }
    
    try:
        response = requests.post(url, json=payload, timeout=300)
        response.raise_for_status()
        result = response.json()
        print(f"[SUCCESS] {result.get('message', 'Users indexed successfully')}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Error indexing users: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"   Details: {error_detail}")
            except:
                print(f"   Response: {e.response.text}")
        return False


def main():
    """Main function to bulk index users."""
    # Get file path
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    user_profiles_path = project_root / "sample_data" / "user_profiles.json"
    
    if not user_profiles_path.exists():
        print(f"[ERROR] User profiles file not found at {user_profiles_path}")
        sys.exit(1)
    
    print(f"Loading user profiles from {user_profiles_path}...")
    raw_users = load_user_profiles(str(user_profiles_path))
    print(f"   Found {len(raw_users)} users")
    
    print("\nTransforming user profiles...")
    transformed_users = []
    for user in raw_users:
        transformed = transform_user_profile(user)
        transformed_users.append(transformed)
        print(f"   [OK] {transformed['name']}: {len(transformed['skills'])} skills")
    
    print(f"\nSummary:")
    print(f"   Total users: {len(transformed_users)}")
    total_skills = sum(len(u['skills']) for u in transformed_users)
    print(f"   Total skills: {total_skills}")
    
    # Show skill distribution
    categories = {}
    for user in transformed_users:
        for skill in user['skills']:
            cat = skill['category']
            categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\nSkill distribution by category:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"   {cat}: {count} skills")
    
    print(f"\nIndexing users to Upstash Vector...")
    print(f"   AI Service URL: {AI_SERVICE_URL}")
    
    success = index_users_bulk(transformed_users)
    
    if success:
        print(f"\n[SUCCESS] Successfully indexed {len(transformed_users)} users!")
        print(f"   You can now use these users for task matching.")
    else:
        print(f"\n[ERROR] Failed to index users. Please check the error messages above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

