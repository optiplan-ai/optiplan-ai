from fastapi import FastAPI, HTTPException
from combined_script import main as run_combined_script
from dotenv import load_dotenv
import os

# Load .env if it exists (useful for local development)
if os.path.exists('.env'):
    load_dotenv()

app = FastAPI()

@app.post("/run-script")
async def run_script():
    try:
        result = run_combined_script()  # Call the function directly
        return {"message": "Script executed successfully", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
