# backend/file_analyzer.py
import os
import shutil
import time
from typing import Dict
from database_manager import enhanced_db

class AdvancedFileAnalyzer:
    FILE_CATEGORIES = {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg", ".webp", ".heic"],
        "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt"],
        "Resume": [".pdf", ".docx", ".doc"],  # Resume files (PDFs and Word docs)
        "Docs": [".pdf", ".docx", ".doc", ".txt", ".rtf", ".odt"],  # General documents
        "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
        "Videos": [".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv"],
        "Code": [".py", ".js", ".ts", ".java", ".cpp", ".c", ".html", ".css", ".sql", ".json", ".xml", ".yaml"],
        "Archives": [".zip", ".tar", ".gz", ".rar", ".7z", ".tar.gz"],
        "Spreadsheets": [".xlsx", ".xls", ".csv", ".ods"],
        "Presentations": [".pptx", ".ppt", ".odp"]
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
                
                # Use enhanced categorization
                category = self._categorize_file(file_path)
                
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

        processing_time = time.time() - start_time
        result = {
            "files_processed": files_processed,
            "processing_time": round(processing_time, 2),
            "category_counts": category_counts,
            "category_files": category_files
        }

        session_id = enhanced_db.save_analysis(folder_path, result)
        return {"session_id": session_id, **result}
    
    def _categorize_file(self, file_path: str) -> str:
        """
        Categorize a single file based on extension and content
        """
        ext = os.path.splitext(file_path)[1].lower()
        filename = os.path.basename(file_path).lower()
        
        # First check by extension
        for category, exts in self.FILE_CATEGORIES.items():
            if ext in exts:
                # Additional content-based categorization for certain file types
                if ext in ['.txt', '.md'] and category == 'Documents':
                    # Check if it's actually code
                    if self._is_code_file(file_path):
                        return 'Code'
                    # Check if it's a resume
                    elif self._is_resume_file(file_path, filename):
                        return 'Resume'
                elif ext in ['.pdf', '.docx', '.doc'] and category == 'Documents':
                    # Check if it's a resume
                    if self._is_resume_file(file_path, filename):
                        return 'Resume'
                return category
        
        # Check by filename patterns
        if any(keyword in filename for keyword in ['resume', 'cv', 'curriculum']):
            return 'Resume'
        elif any(keyword in filename for keyword in ['presentation', 'slides', 'ppt']):
            return 'Presentations'
        elif any(keyword in filename for keyword in ['spreadsheet', 'budget', 'expense', 'financial']):
            return 'Spreadsheets'
        
        return 'Others'
    
    def _is_code_file(self, file_path: str) -> bool:
        """Check if a text file contains code"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1000)  # Read first 1000 chars
                # Look for code patterns
                code_patterns = [
                    'def ', 'function ', 'class ', 'import ', 'from ',
                    'console.log', 'document.', 'window.', 'var ', 'let ', 'const ',
                    'public class', 'private ', 'public ', 'static ',
                    '#include', 'int main', 'void ', 'return ',
                    '<?php', '<?xml', '<!DOCTYPE', '<html', '<script'
                ]
                return any(pattern in content for pattern in code_patterns)
        except:
            return False
    
    def _is_resume_file(self, file_path: str, filename: str) -> bool:
        """Check if a document is likely a resume"""
        resume_keywords = [
            'resume', 'cv', 'curriculum', 'vitae', 'profile',
            'experience', 'education', 'skills', 'objective',
            'summary', 'qualifications'
        ]
        
        # Check filename
        if any(keyword in filename for keyword in resume_keywords):
            return True
            
        # Check content for resume-like text
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(2000).lower()  # Read first 2000 chars
                resume_sections = [
                    'work experience', 'employment history', 'professional experience',
                    'education', 'academic background', 'qualifications',
                    'skills', 'technical skills', 'core competencies',
                    'objective', 'summary', 'profile', 'about me',
                    'software engineer', 'developer', 'programmer',
                    'bachelor', 'master', 'degree', 'university',
                    'work experience', 'employment', 'professional',
                    'education', 'academic', 'qualifications',
                    'skills', 'technical', 'competencies',
                    'objective', 'summary', 'profile', 'about',
                    'software', 'engineer', 'developer', 'programmer',
                    'bachelor', 'master', 'degree', 'university'
                ]
                # Count how many resume indicators are present
                indicators = sum(1 for section in resume_sections if section in content)
                return indicators >= 2  # Need at least 2 indicators
        except:
            return False

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
                
                # Use enhanced categorization
                category = self._categorize_file(file_path)
                
                category_counts[category] += 1
                category_files[category].append({
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
