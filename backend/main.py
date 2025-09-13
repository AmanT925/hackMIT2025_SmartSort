from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import Dict, Any
from file_analyzer import ParallelFileAnalyzer
from voice_handler import VoiceHandler
from data_cleaner import MessyDataCleaner
from utils import validate_directory, create_demo_files

app = FastAPI(title="SmartSort API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

file_analyzer = ParallelFileAnalyzer()
voice_handler = VoiceHandler()
data_cleaner = MessyDataCleaner()

@app.get("/")
async def root():
    return {"message": "SmartSort API is running!"}

@app.post("/analyze")
async def analyze_directory(request: Dict[str, str]):
    directory_path = request.get("directory_path")
    if not directory_path:
        raise HTTPException(status_code=400, detail="directory_path required")
    
    validation = validate_directory(directory_path)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail=validation["error"])
    
    results = file_analyzer.analyze_directory(directory_path)
    return results

@app.post("/voice-command")
async def process_voice_command(request: Dict[str, str]):
    text = request.get("text", "")
    response = voice_handler.process_command(text, file_analyzer)
    return response

@app.get("/demo/create")
async def create_demo():
    demo_dir = os.path.expanduser("~/Desktop/SmartSort_Demo")
    created_dir = create_demo_files(demo_dir)
    return {"message": "Demo created", "path": created_dir}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
