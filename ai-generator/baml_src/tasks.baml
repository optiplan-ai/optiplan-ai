client<llm> GemniClient {
  provider google-ai
  options {
    model "gemini-1.5-flash"
    api_key env.GOOGLE_API_KEY
    generationConfig {
      temperature 0.5
    }
  }
}

class Tasks {
  task_id int @description("A unique identifier for the task, used to reference it in dependencies and reports.")
  name string @description("A concise overview of the task.")
  complexity int @assert(in_range, {{ this >= 1 and this <= 10 }}) @description("Estimated complexity of the task on a scale from 1 (easiest) to 10 (most complex).")
  estimated_hours float @description("Realistic time estimate in hours to complete the task.")
  required_skills Skills[] @description("An array of skills required to complete the task.")
  depends_on int[] @description("List of prerequisite task IDs that must be completed before this task can begin.")
}

class Skills {
  name string @description("The name of the skill.")
  category string @description("The category or domain of the skill.")
  preferred_experience float @assert(in_range, {{ this >= 0 and this <= 10 }}) @description("Preferred years of experience for this skill (0 to 10 years).")
  required_proficiency int @assert(in_range, {{ this >= 1 and this <= 10 }}) @description("Required proficiency level for this skill on a scale of 1 (novice) to 10 (expert).")
}

function GenerateRoadmap(raw_text: string) -> Tasks[] {
  client GemniClient
  prompt #"
    Generate a comprehensive and detailed roadmap of tasks to build the following project:
    ---
    {{raw_text}}
    ---

    {{ ctx.output_format }}
  "#
}