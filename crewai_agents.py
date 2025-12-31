from crewai import Agent, Task, Crew, Process
from typing import List, Dict
import google.generativeai as genai
from configs import google_api_key, gemini_model
import json
import re


class GeminiLLM:
    """Wrapper for Gemini models to work with CrewAI."""
    
    def __init__(self, model_name: str = None):
        genai.configure(api_key=google_api_key)
        self.model_name = model_name or gemini_model
        
    def invoke(self, prompt: str, **kwargs):
        """Call Gemini API with the prompt - CrewAI uses invoke method."""
        try:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            # Fallback to 2.5 Pro if 3 Pro fails
            if "3" in self.model_name or "gemini-3" in self.model_name.lower():
                try:
                    fallback_model = "gemini-2.5-pro"  # Stable fallback model
                    model = genai.GenerativeModel(fallback_model)
                    response = model.generate_content(prompt)
                    return response.text
                except Exception as fallback_error:
                    print(f"Fallback model also failed: {fallback_error}")
                    raise e
            raise e
    
    def __call__(self, prompt: str, **kwargs):
        """Also support direct call for compatibility."""
        return self.invoke(prompt, **kwargs)


# Initialize Gemini LLM
gemini_llm = GeminiLLM()


def create_task_generation_crew(project_description: str) -> Crew:
    """Create a CrewAI crew for generating project tasks."""
    
    # Project Analyst Agent
    project_analyst = Agent(
        role="Project Analyst",
        goal="Analyze project requirements and break down the project into logical components",
        backstory="You are an experienced project analyst who specializes in understanding complex project requirements and identifying key components, dependencies, and technical needs.",
        llm=gemini_llm,
        verbose=True,
        allow_delegation=False,
    )
    
    # Task Planner Agent
    task_planner = Agent(
        role="Task Planner",
        goal="Create detailed, actionable tasks with clear requirements and dependencies",
        backstory="You are a meticulous task planner who excels at breaking down project components into specific, measurable tasks with proper sequencing and dependencies.",
        llm=gemini_llm,
        verbose=True,
        allow_delegation=False,
    )
    
    # Roadmap Generator Agent
    roadmap_generator = Agent(
        role="Roadmap Generator",
        goal="Structure tasks into a logical roadmap with proper dependencies and skill requirements",
        backstory="You are a strategic roadmap generator who creates comprehensive project roadmaps with task dependencies, required skills, complexity estimates, and time estimates. You always output valid JSON.",
        llm=gemini_llm,
        verbose=True,
        allow_delegation=False,
    )
    
    # Tasks
    analysis_task = Task(
        description=f"""
        Analyze the following project description and identify:
        1. Main components and features
        2. Technical requirements
        3. Dependencies between components
        4. Key milestones
        
        Project Description: {project_description}
        
        Provide a structured analysis that can be used to create tasks.
        """,
        agent=project_analyst,
        expected_output="A structured analysis document with components, requirements, and dependencies",
    )
    
    planning_task = Task(
        description="""
        Based on the project analysis, create a list of specific, actionable tasks.
        Each task should have:
        - A clear name
        - Description of what needs to be done
        - Dependencies on other tasks (if any)
        - Required technical skills
        
        Format the output as a structured list that can be used to generate the final roadmap.
        """,
        agent=task_planner,
        expected_output="A list of detailed tasks with names, descriptions, dependencies, and skill requirements",
    )
    
    roadmap_task = Task(
        description="""
        Based on the task list, generate a comprehensive roadmap with the following structure:
        
        For each task, provide:
        - task_id: A unique numeric identifier (starting from 1)
        - name: A clear, concise task brief (2-8 words) that describes what will be accomplished. 
          MUST be a descriptive string like "Implement user authentication system" or "Design database schema".
          NEVER use just numbers like "1" or "Task 1" or "1,".
        - description: A detailed markdown-formatted paragraph (2-4 sentences) explaining:
          * What needs to be done
          * Key steps or components involved
          * Expected outcomes or deliverables
          Use markdown formatting with proper sentences and paragraphs.
        - complexity: Estimated complexity (1-10 scale)
        - estimated_hours: Realistic time estimate in hours
        - required_skills: Array of skills with:
          - name: Skill name
          - category: Skill category (e.g., frontend, backend, database, cloud, design, management)
          - preferred_experience: Preferred years of experience (0-10)
          - required_proficiency: Required proficiency level (1-10)
        - depends_on: Array of task IDs that must be completed first (can be empty array [])
        
        CRITICAL REQUIREMENTS:
        1. Return ONLY valid JSON array format - no markdown code blocks, no explanations outside JSON
        2. The "name" field MUST be a descriptive brief (e.g., "Build REST API endpoints" NOT "1" or "Task 1" or "1,")
        3. The "description" field MUST be a markdown paragraph with 2-4 complete sentences
        4. Each task must have all required fields
        5. Task names should be action-oriented and specific (e.g., "Configure CI/CD pipeline" not "CI/CD")
        
        Example format:
        [
          {
            "task_id": 1,
            "name": "Setup project structure and configuration",
            "description": "Create the initial project directory structure following best practices. Configure build tools, package managers, and development environment. Set up version control with proper .gitignore and initial commit structure. Establish coding standards and project documentation framework.",
            "complexity": 3,
            "estimated_hours": 4.0,
            "required_skills": [
              {
                "name": "Project Management",
                "category": "management",
                "preferred_experience": 2.0,
                "required_proficiency": 5
              }
            ],
            "depends_on": []
          }
        ]
        
        Return the JSON array now:
        """,
        agent=roadmap_generator,
        expected_output="A JSON array of task objects with all required fields. Each task must have a descriptive name (not a number) and a markdown paragraph description. Return ONLY valid JSON, no markdown code blocks.",
    )
    
    # Create crew
    crew = Crew(
        agents=[project_analyst, task_planner, roadmap_generator],
        tasks=[analysis_task, planning_task, roadmap_task],
        process=Process.sequential,
        verbose=True,
    )
    
    return crew


def generate_tasks(project_description: str) -> List[Dict]:
    """Generate tasks using CrewAI."""
    crew = create_task_generation_crew(project_description)
    result = crew.kickoff()
    
    # Parse the result - CrewAI returns text, we need to extract JSON
    result_text = str(result)
    
    # Try to extract JSON from the output
    # Look for JSON array pattern
    json_pattern = r'\[.*?\]'
    json_match = re.search(json_pattern, result_text, re.DOTALL)
    
    if json_match:
        try:
            # Clean the JSON string
            json_str = json_match.group(0)
            # Remove any markdown code blocks if present
            json_str = re.sub(r'```json\s*', '', json_str)
            json_str = re.sub(r'```\s*', '', json_str)
            json_str = json_str.strip()
            
            tasks = json.loads(json_str)
            if isinstance(tasks, list):
                # Validate and fix task data
                for task in tasks:
                    # Ensure name is a proper string, not a number or serial number
                    task_name = task.get("name", "")
                    if isinstance(task_name, (int, float)):
                        task["name"] = f"Task {task.get('task_id', task_name)}"
                    elif not task_name or not isinstance(task_name, str):
                        task["name"] = f"Task {task.get('task_id', len(tasks))}"
                    else:
                        # Clean up names that are just numbers or serial numbers
                        task_name_clean = str(task_name).strip()
                        # Remove trailing commas and numbers
                        if task_name_clean.endswith(',') or task_name_clean.isdigit() or (len(task_name_clean) <= 3 and task_name_clean.replace(',', '').isdigit()):
                            task["name"] = f"Task {task.get('task_id', len(tasks))}"
                        else:
                            # Remove trailing commas and clean up
                            task["name"] = task_name_clean.rstrip(',').strip()
                    
                    # Ensure description exists and is a proper markdown paragraph
                    description = task.get("description", "")
                    if not description or not isinstance(description, str) or len(description.strip()) < 20:
                        # Generate a proper description
                        complexity = task.get('complexity', 5)
                        hours = task.get('estimated_hours', 8)
                        task_name_final = task.get("name", "this task")
                        task["description"] = f"Complete {task_name_final.lower()}. This task has a complexity rating of {complexity}/10 and is estimated to take approximately {hours} hours. The work involves implementing the necessary components and ensuring proper integration with the overall system."
                    else:
                        # Ensure description is properly formatted
                        task["description"] = description.strip()
                    
                    # Ensure all required fields exist
                    task.setdefault("complexity", 5)
                    task.setdefault("estimated_hours", 8.0)
                    task.setdefault("required_skills", [])
                    task.setdefault("depends_on", [])
                
                return tasks
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print(f"JSON string: {json_str[:500]}...")
    
    # If JSON parsing fails, try to parse the text output
    # This is a fallback - the agent should ideally output JSON
    tasks = []
    lines = result_text.split('\n')
    current_task = None
    task_id = 1
    description_lines = []
    in_description = False
    
    for line in lines:
        line_lower = line.lower().strip()
        line_stripped = line.strip()
        
        # Detect task start
        if 'task' in line_lower and ('name' in line_lower or 'id' in line_lower):
            if current_task:
                # Save description if we were collecting it
                if description_lines:
                    desc_text = " ".join(description_lines).strip()
                    # Ensure it's a proper paragraph
                    if len(desc_text) < 20:
                        complexity = current_task.get('complexity', 5)
                        hours = current_task.get('estimated_hours', 8)
                        task_name = current_task.get("name", "this task")
                        current_task["description"] = f"Complete {task_name.lower()}. This task has a complexity rating of {complexity}/10 and is estimated to take approximately {hours} hours. The work involves implementing the necessary components and ensuring proper integration with the overall system."
                    else:
                        current_task["description"] = desc_text
                if not current_task.get("description") or len(current_task.get("description", "")) < 20:
                    complexity = current_task.get('complexity', 5)
                    hours = current_task.get('estimated_hours', 8)
                    task_name = current_task.get("name", "this task")
                    current_task["description"] = f"Complete {task_name.lower()}. This task has a complexity rating of {complexity}/10 and is estimated to take approximately {hours} hours. The work involves implementing the necessary components and ensuring proper integration with the overall system."
                tasks.append(current_task)
            
            # Extract task name - look for patterns like "Task Name:", "Name:", etc.
            task_name = None
            if 'name' in line_lower and ':' in line:
                task_name = line.split(':', 1)[-1].strip()
            elif 'task' in line_lower and any(char.isalpha() for char in line_stripped):
                # Try to extract meaningful name from the line
                parts = re.split(r'[:\-]', line_stripped, 1)
                if len(parts) > 1:
                    task_name = parts[-1].strip()
                else:
                    task_name = line_stripped.replace('task', '').strip()
            
            # Clean task name - remove trailing commas and ensure it's not just a number
            if task_name:
                task_name_clean = task_name.rstrip(',').strip()
                if task_name_clean.isdigit() or (len(task_name_clean) <= 3 and task_name_clean.replace(',', '').isdigit()):
                    task_name_clean = f"Task {task_id}"
            else:
                task_name_clean = f"Task {task_id}"
            
            current_task = {
                "task_id": task_id,
                "name": task_name_clean,
                "description": "",
                "complexity": 5,
                "estimated_hours": 8.0,
                "required_skills": [],
                "depends_on": [],
            }
            description_lines = []
            in_description = False
            task_id += 1
        elif current_task:
            # Check for description field
            if 'description' in line_lower and ':' in line:
                in_description = True
                desc_text = line.split(':', 1)[-1].strip()
                if desc_text:
                    description_lines.append(desc_text)
            elif in_description and line_stripped and not any(keyword in line_lower for keyword in ['complexity', 'hours', 'time', 'estimate', 'skills', 'depends']):
                # Continue collecting description
                description_lines.append(line_stripped)
            elif 'complexity' in line_lower:
                in_description = False
                try:
                    complexity = int(re.search(r'\d+', line).group())
                    current_task["complexity"] = min(max(complexity, 1), 10)
                except:
                    pass
            elif 'hours' in line_lower or 'time' in line_lower or 'estimate' in line_lower:
                in_description = False
                try:
                    hours = float(re.search(r'\d+\.?\d*', line).group())
                    current_task["estimated_hours"] = hours
                except:
                    pass
    
    # Add last task
    if current_task:
        if description_lines:
            desc_text = " ".join(description_lines).strip()
            if len(desc_text) >= 20:
                current_task["description"] = desc_text
        if not current_task.get("description") or len(current_task.get("description", "")) < 20:
            complexity = current_task.get('complexity', 5)
            hours = current_task.get('estimated_hours', 8)
            task_name = current_task.get("name", "this task")
            current_task["description"] = f"Complete {task_name.lower()}. This task has a complexity rating of {complexity}/10 and is estimated to take approximately {hours} hours. The work involves implementing the necessary components and ensuring proper integration with the overall system."
        tasks.append(current_task)
    
    # If we still don't have tasks, create a basic one
    if not tasks:
        tasks = [{
            "task_id": 1,
            "name": "Initial project setup",
            "description": "Set up the initial project structure and configuration",
            "complexity": 3,
            "estimated_hours": 4.0,
            "required_skills": [],
            "depends_on": [],
        }]
    
    return tasks
