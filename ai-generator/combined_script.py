# @title Structured AI Response Generation using baml
import baml_client as client
import PineconeSDK

def to_dict(obj):
    if hasattr(obj, '__dict__'):
        return {k: to_dict(v) for k, v in vars(obj).items()}
    if isinstance(obj, list):
        return [to_dict(item) for item in obj]
    return obj

sample_users = [
    # Frontend Specialist
    {
        "id": 1,
        "name": "Sarah Frontend",
        "email": "sarah.frontend@example.com",
        "skills": [
            {
                "name": "React",
                "category": "Frontend",
                "experience_years": 5,
                "projects": ["Real-time CMS Dashboard", "Collaborative Editor"],
                "proficiency_score": 0.95
            },
            {
                "name": "WebSockets",
                "category": "Realtime",
                "experience_years": 3,
                "projects": ["Live Collaboration System"],
                "proficiency_score": 0.85
            }
        ],
        "total_experience": 6,
        "primary_domain": "Frontend",
        "availability": 30,
        "learning_speed": 7,
        "complexity_grasp": 9
    },

    # ML Backend Engineer
    {
        "id": 2,
        "name": "Mike PythonML",
        "email": "mike.ml@example.com",
        "skills": [
            {
                "name": "Python",
                "category": "Backend",
                "experience_years": 7,
                "projects": ["Content Categorization Engine"],
                "proficiency_score": 0.98
            },
            {
                "name": "TensorFlow",
                "category": "ML",
                "experience_years": 5,
                "projects": ["NLP Classification System"],
                "proficiency_score": 0.92
            }
        ],
        "total_experience": 8,
        "primary_domain": "Machine Learning",
        "availability": 25,
        "learning_speed": 6,
        "complexity_grasp": 9
    },

    # Cloud/DevOps Expert
    {
        "id": 3,
        "name": "DevOps Dana",
        "email": "dana.cloud@example.com",
        "skills": [
            {
                "name": "Docker",
                "category": "DevOps",
                "experience_years": 4,
                "projects": ["Microservices Orchestration"],
                "proficiency_score": 0.90
            },
            {
                "name": "AWS",
                "category": "Cloud",
                "experience_years": 5,
                "projects": ["Auto-scaling Systems"],
                "proficiency_score": 0.93
            }
        ],
        "total_experience": 6,
        "primary_domain": "Cloud Infrastructure",
        "availability": 20,
        "learning_speed": 8,
        "complexity_grasp": 8
    },

    # Full-Stack GraphQL Developer
    {
        "id": 4,
        "name": "GraphQL Grace",
        "email": "grace.graphql@example.com",
        "skills": [
            {
                "name": "GraphQL",
                "category": "API",
                "experience_years": 4,
                "projects": ["High-performance CMS API"],
                "proficiency_score": 0.91
            },
            {
                "name": "Node.js",
                "category": "Backend",
                "experience_years": 5,
                "projects": ["Real-time Data Layer"],
                "proficiency_score": 0.89
            }
        ],
        "total_experience": 6,
        "primary_domain": "API Development",
        "availability": 35,
        "learning_speed": 9,
        "complexity_grasp": 8
    },

    # Analytics Specialist
    {
        "id": 5,
        "name": "Analytics Alex",
        "email": "alex.data@example.com",
        "skills": [
            {
                "name": "Elasticsearch",
                "category": "Analytics",
                "experience_years": 4,
                "projects": ["Real-time Dashboard System"],
                "proficiency_score": 0.88
            },
            {
                "name": "Kafka",
                "category": "Data Streaming",
                "experience_years": 3,
                "projects": ["Event-driven Analytics"],
                "proficiency_score": 0.85
            }
        ],
        "total_experience": 5,
        "primary_domain": "Data Analytics",
        "availability": 25,
        "learning_speed": 7,
        "complexity_grasp": 8
    }
]

def main():
    # Your script logic here.
    print("Script is running!")

    response = client.b.GenerateRoadmap(project_description)
    tasks = to_dict(response)

    for i in range (0,len(tasks)):
        task = tasks[i]
        print(f'Task Id: {task["task_id"]}')
        print(f'Task Name: {task["name"]}')
        print(f'Complexity: {task["complexity"]}/10')
        print(f'Estimate: {task["estimated_hours"]} hours\n')

    matcher = PineconeSDK(
        index_name="project-embeddings"
    )

    matcher.index_users(sample_users)
    matcher.index_tasks(tasks)

    # Find matches for each task
    print("\n=== Task Assignments ===")
    for task in tasks:
        print(f"\nTask: {task['name']}")
        matches = matcher.find_matching_users(task)
        print("Matched Users:")
        for match in matches:
            print(f"- {match['name']} (Match Score: {match['match_score']:.2f})")

    # Find suitable tasks for each user
    print("\n=== User Task Recommendations ===")
    for user in sample_users:
        print(f"\nUser: {user['name']}")
        matches = matcher.find_matching_tasks(user)
        print("Recommended Tasks:")
        for match in matches:
            print(f"- {match['name']} (Match Score: {match['match_score']:.2f})")

    return "Script completed successfully!"

if __name__ == "__main__":
    main()
