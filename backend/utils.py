import os
import shutil
from typing import Dict, Any

def validate_directory(directory_path: str) -> Dict[str, Any]:
    try:
        if not os.path.exists(directory_path):
            return {"valid": False, "error": "Directory does not exist"}
        
        if not os.path.isdir(directory_path):
            return {"valid": False, "error": "Path is not a directory"}
        
        if not os.access(directory_path, os.R_OK):
            return {"valid": False, "error": "Directory is not readable"}
        
        # Count files
        file_count = 0
        for root, dirs, files in os.walk(directory_path):
            file_count += len([f for f in files if not f.startswith('.')])
        
        return {
            "valid": True, 
            "file_count": file_count,
            "path": os.path.abspath(directory_path)
        }
        
    except Exception as e:
        return {"valid": False, "error": str(e)}

def create_demo_files(demo_dir: str) -> str:
    if os.path.exists(demo_dir):
        shutil.rmtree(demo_dir)
    
    os.makedirs(demo_dir)
    
    # Create sample messy files for demo
    demo_files = [
        # School files
        "Physics_HW_3_final.pdf",
        "Math_midterm_study_guide.docx", 
        "Essay_draft_final_FINAL.txt",
        "Untitled.docx",
        "Untitled (1).docx",
        
        # Financial
        "Phone_bill_March_2024.pdf",
        "grocery_receipt_042324.jpg",
        
        # Screenshots
        "Screenshot 2024-03-15 at 2.30.45 PM.png",
        "Screen Shot 2024-04-01 at 10.15.23 AM.png",
        
        # Random downloads
        "download (1).pdf",
        "document.pdf", 
        "IMG_1234.HEIC",
        
        # Code files
        "main.py",
        "script.js",
        "index.html"
    ]
    
    for filename in demo_files:
        file_path = os.path.join(demo_dir, filename)
        with open(file_path, 'w') as f:
            f.write(f"Demo content for {filename}")
    
    return demo_dir

def format_file_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"
