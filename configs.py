from dotenv import load_dotenv
import os

# Load .env if it exists (useful for local development)
load_dotenv()

google_api_key = os.getenv("GOOGLE_API_KEY")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
