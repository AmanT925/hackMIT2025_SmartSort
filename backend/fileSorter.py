"""
File sorting and organization utilities
"""
import os
import shutil
from typing import List, Dict, Any
from pathlib import Path

# Global variable to track last operation for undo functionality
last_operation = None

def sortFiles(directory_path: str = None) -> Dict[str, Any]:
    """
    Sort files in the given directory into organized folders
    """
    global last_operation
    
    if not directory_path:
        directory_path = os.getcwd()
    
    try:
        # Create organized folder structure
        categories = {
            'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
            'Videos': ['.mp4', '.avi', '.mov', '.mkv', '.wmv'],
            'Audio': ['.mp3', '.wav', '.flac', '.aac'],
            'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'Code': ['.py', '.js', '.html', '.css', '.java', '.cpp']
        }
        
        moved_files = []
        
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            
            if os.path.isfile(file_path):
                file_ext = Path(filename).suffix.lower()
                
                # Find appropriate category
                target_category = 'Other'
                for category, extensions in categories.items():
                    if file_ext in extensions:
                        target_category = category
                        break
                
                # Create category folder if it doesn't exist
                category_path = os.path.join(directory_path, target_category)
                os.makedirs(category_path, exist_ok=True)
                
                # Move file
                target_path = os.path.join(category_path, filename)
                shutil.move(file_path, target_path)
                moved_files.append({
                    'original': file_path,
                    'new': target_path,
                    'category': target_category
                })
        
        last_operation = {
            'type': 'sort',
            'files': moved_files,
            'directory': directory_path
        }
        
        return {
            'success': True,
            'files_moved': len(moved_files),
            'categories_created': len(set(f['category'] for f in moved_files))
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def findFiles(topic: str, directory_path: str = None) -> List[Dict[str, Any]]:
    """
    Find files related to a specific topic
    """
    if not directory_path:
        directory_path = os.getcwd()
    
    matching_files = []
    topic_lower = topic.lower()
    
    try:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if topic_lower in file.lower():
                    file_path = os.path.join(root, file)
                    matching_files.append({
                        'filename': file,
                        'path': file_path,
                        'size': os.path.getsize(file_path),
                        'modified': os.path.getmtime(file_path)
                    })
    except Exception as e:
        print(f"Error searching files: {e}")
    
    return matching_files

def showDuplicates(directory_path: str = None) -> List[List[Dict[str, Any]]]:
    """
    Find and show duplicate files
    """
    if not directory_path:
        directory_path = os.getcwd()
    
    import hashlib
    from collections import defaultdict
    
    file_hashes = defaultdict(list)
    
    try:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read()).hexdigest()
                    
                    file_hashes[file_hash].append({
                        'filename': file,
                        'path': file_path,
                        'size': os.path.getsize(file_path)
                    })
                except (IOError, OSError):
                    continue
        
        # Return only groups with duplicates
        duplicates = [files for files in file_hashes.values() if len(files) > 1]
        return duplicates
        
    except Exception as e:
        print(f"Error finding duplicates: {e}")
        return []

def undoLast() -> Dict[str, Any]:
    """
    Undo the last file operation
    """
    global last_operation
    
    if not last_operation:
        return {'success': False, 'error': 'No operation to undo'}
    
    try:
        if last_operation['type'] == 'sort':
            # Move files back to original locations
            for file_info in last_operation['files']:
                if os.path.exists(file_info['new']):
                    shutil.move(file_info['new'], file_info['original'])
            
            # Remove empty category folders
            directory_path = last_operation['directory']
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                if os.path.isdir(item_path) and not os.listdir(item_path):
                    os.rmdir(item_path)
            
            files_restored = len(last_operation['files'])
            last_operation = None
            
            return {
                'success': True,
                'files_restored': files_restored,
                'message': 'Successfully undid last sort operation'
            }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}
    
    return {'success': False, 'error': 'Could not undo operation'}
