# backend/main.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import tempfile
import shutil
import time
from file_analyzer import AdvancedFileAnalyzer
from database_manager import enhanced_db

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Initialize analyzer
analyzer = AdvancedFileAnalyzer()

@app.post("/analyze")
async def analyze_files(files: List[UploadFile] = File(...), organize: str = Form("false")):
    """
    File analysis with optional organization (sequential processing only)
    """
    temp_dir = tempfile.mkdtemp()
    should_organize = organize.lower() == "true"
    
    try:
        # Save uploaded files to temp directory
        file_paths = []
        for file in files:
            # Create directory structure if file has subdirectories
            file_path = os.path.join(temp_dir, file.filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save file content
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            file_paths.append(file_path)
        
        file_count = len(file_paths)
        start_time = time.time()
        
        print(f"📋 Received {file_count} files, organize={organize} (should_organize={should_organize})")
        print(f"📁 Temp directory: {temp_dir}")
        
        # Process files
        print(f"⚡ Processing {file_count} files (organize: {should_organize})")
        
        if should_organize:
            print("📂 ORGANIZING files into folders")
            result = analyzer.organize(temp_dir)
        else:
            print("📊 ANALYZING only - no file movement")
            result = analyzer.analyze_only(temp_dir)
            
        result['processing_method'] = 'serial'
        result['workers_used'] = 1
        
        # Save to database
        session_id = enhanced_db.save_analysis(temp_dir, result)
        result['session_id'] = session_id
        
        # If organizing, copy organized files to Desktop
        if should_organize:
            # Create organized directory on Desktop
            desktop = os.path.expanduser("~/Desktop")
            organized_dir = os.path.join(desktop, "organized_files")
            
            # Add timestamp to make directory name unique
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            organized_dir = f"{organized_dir}_{timestamp}"
            
            # Remove if exists and copy files
            if os.path.exists(organized_dir):
                shutil.rmtree(organized_dir)
                
            # Copy the entire directory structure
            shutil.copytree(temp_dir, organized_dir)
            
            # Store the path in the result
            result['organized_path'] = organized_dir
            print(f"✅ Organized files saved to: {organized_dir}")
        
        return result
    
    finally:
        # Only clean up temp directory if we're NOT organizing files
        if not should_organize:
            shutil.rmtree(temp_dir, ignore_errors=True)
        else:
            print(f"📁 Organized files saved in: {temp_dir}")

@app.post("/generate-demo")
async def generate_demo_files():
    """
    Generate a random messy demo folder with various file types for testing
    """
    import random
    import string
    from datetime import datetime, timedelta
    
    # Generate random gibberish folder name
    random_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    demo_folder_name = f"messy_files_{random_name}"
    demo_dir = os.path.expanduser(f"~/Desktop/{demo_folder_name}")
    
    # Store the demo folder name for later use in organize function
    generate_demo_files._last_demo_name = demo_folder_name
    
    # Clean up existing demo if it exists
    if os.path.exists(demo_dir):
        shutil.rmtree(demo_dir)
    
    os.makedirs(demo_dir)
    
    # Create demo files using the utility function
    from utils import create_demo_files
    create_demo_files(demo_dir)
    
    return {
        "message": f"Generated demo files in {demo_folder_name}",
        "demo_path": demo_dir,
        "folder_name": demo_folder_name
    }


@app.get("/history")
def get_history(limit: int = 20):
    """
    Return last N analysis sessions.
    """
    return enhanced_db.get_history(limit)
