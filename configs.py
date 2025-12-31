from dotenv import load_dotenv
import os

# Load .env if it exists (useful for local development)
load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")
upstash_vector_url = os.getenv("UPSTASH_VECTOR_REST_URL")
upstash_vector_token = os.getenv("UPSTASH_VECTOR_REST_TOKEN")

# Gemini model configuration - try 3 Pro first, fallback to 2.5 Pro
def get_gemini_model():
    """Get the best available Gemini model."""
    # Try to detect if Gemini 3 Pro is available
    # For now, default to 2.5 Pro (update when 3 Pro is available)
    model_3_pro = "gemini-3.0-pro"
    model_2_5_pro = "gemini-2.5-pro"  # Stable and widely available model
    
    # You can add logic here to check model availability
    # For now, we'll use 2.5 Pro as default
    return model_2_5_pro

gemini_model = get_gemini_model()
