# backend/file_analyzer.py
import os
import shutil
import time
from typing import Dict
from database_manager import enhanced_db

class AdvancedFileAnalyzer:
    FILE_CATEGORIES = {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
        "Documents": [".pdf", ".docx", ".txt", ".xlsx", ".pptx"],
        "Music": [".mp3", ".wav", ".flac"],
        "Videos": [".mp4", ".mov", ".avi"],
        "Code": [".py", ".js", ".ts", ".java", ".cpp", ".c", ".html", ".css"],
        "Archives": [".zip", ".tar", ".gz", ".rar"]
    }

    def __init__(self):
        pass

    def organize(self, folder_path: str) -> Dict:
        start_time = time.time()
        files_processed = 0
        category_counts = {cat: 0 for cat in self.FILE_CATEGORIES}
        category_files = {cat: [] for cat in self.FILE_CATEGORIES}
        category_files["Others"] = []

        for root, dirs, files in os.walk(folder_path):
            for file in files:
                files_processed += 1
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                ext = os.path.splitext(file)[1].lower()
                moved = False
                
                for category, exts in self.FILE_CATEGORIES.items():
                    if ext in exts:
                        # Create category folder and move file
                        target_dir = os.path.join(folder_path, category)
                        os.makedirs(target_dir, exist_ok=True)
                        shutil.move(file_path, os.path.join(target_dir, file))
                        
                        category_counts[category] += 1
                        category_files[category].append({
                            'name': file,
                            'size': file_size,
                            'path': os.path.join(target_dir, file)
                        })
                        moved = True
                        break
                        
                if not moved:
                    # Create Others folder and move file
                    target_dir = os.path.join(folder_path, "Others")
                    os.makedirs(target_dir, exist_ok=True)
                    shutil.move(file_path, os.path.join(target_dir, file))
                    
                    category_counts.setdefault("Others", 0)
                    category_counts["Others"] += 1
                    category_files["Others"].append({
                        'name': file,
                        'size': file_size,
                        'path': os.path.join(target_dir, file)
                    })

        processing_time = time.time() - start_time
        result = {
            "files_processed": files_processed,
            "processing_time": round(processing_time, 2),
            "category_counts": category_counts,
            "category_files": category_files
        }

        session_id = enhanced_db.save_analysis(folder_path, result)
        return {"session_id": session_id, **result}
    
    def analyze_only(self, folder_path: str) -> Dict:
        """
        Analyze files without moving them - just categorize and return data
        """
        start_time = time.time()
        files_processed = 0
        category_counts = {cat: 0 for cat in self.FILE_CATEGORIES}
        category_files = {cat: [] for cat in self.FILE_CATEGORIES}
        category_files["Others"] = []

        for root, dirs, files in os.walk(folder_path):
            for file in files:
                files_processed += 1
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                ext = os.path.splitext(file)[1].lower()
                moved = False
                
                for category, exts in self.FILE_CATEGORIES.items():
                    if ext in exts:
                        category_counts[category] += 1
                        category_files[category].append({
                            'name': file,
                            'size': file_size,
                            'path': file_path
                        })
                        moved = True
                        break
                        
                if not moved:
                    category_counts.setdefault("Others", 0)
                    category_counts["Others"] += 1
                    category_files["Others"].append({
                        'name': file,
                        'size': file_size,
                        'path': file_path
                    })

        processing_time = time.time() - start_time
        result = {
            "files_processed": files_processed,
            "processing_time": round(processing_time, 2),
            "category_counts": category_counts,
            "category_files": category_files
        }

        session_id = enhanced_db.save_analysis(folder_path, result)
        return {"session_id": session_id, **result}
