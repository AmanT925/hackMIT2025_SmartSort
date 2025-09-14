# backend/main.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import tempfile
import shutil
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import cpu_count
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

def analyze_file_batch(file_paths):
    """Process a batch of files in parallel"""
    results = {}
    for filepath in file_paths:
        try:
            # Get file extension and categorize
            ext = os.path.splitext(filepath)[1].lower()
            category = "Other"
            
            for cat, extensions in analyzer.FILE_CATEGORIES.items():
                if ext in extensions:
                    category = cat
                    break
            
            results[filepath] = {
                'category': category,
                'size': os.path.getsize(filepath) if os.path.exists(filepath) else 0
            }
        except Exception:
            results[filepath] = {'category': 'Error', 'size': 0}
    
    return results

@app.post("/analyze")
async def analyze_files(files: List[UploadFile] = File(...), organize: str = Form("false")):
    """
    File analysis with optional organization and parallel processing for 100+ files
    """
    temp_dir = tempfile.mkdtemp()
    should_organize = organize.lower() == "true"
    
    try:
        # Save uploaded files to temp directory
        file_paths = []
        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            file_paths.append(file_path)
        
        file_count = len(file_paths)
        start_time = time.time()
        
        print(f"📋 Received organize parameter: '{organize}' -> should_organize: {should_organize}")
        
        # Use parallel processing for 100+ files
        if file_count >= 100:
            print(f"🚀 PARALLEL processing {file_count} files")
            
            # Split files into chunks for parallel processing
            num_workers = min(cpu_count(), 8)
            chunk_size = max(1, file_count // num_workers)
            chunks = [file_paths[i:i + chunk_size] for i in range(0, len(file_paths), chunk_size)]
            
            all_results = {}
            with ProcessPoolExecutor(max_workers=num_workers) as executor:
                futures = [executor.submit(analyze_file_batch, chunk) for chunk in chunks]
                for future in futures:
                    chunk_results = future.result()
                    all_results.update(chunk_results)
            
            # Count categories and organize file lists
            category_counts = {}
            category_files = {}
            for filepath, file_info in all_results.items():
                category = file_info['category']
                category_counts[category] = category_counts.get(category, 0) + 1
                
                if category not in category_files:
                    category_files[category] = []
                category_files[category].append({
                    'name': os.path.basename(filepath),
                    'size': file_info['size'],
                    'path': filepath
                })
            
            processing_time = time.time() - start_time
            result = {
                'category_counts': category_counts,
                'category_files': category_files,
                'files_processed': file_count,
                'processing_time': processing_time,
                'processing_method': 'parallel',
                'workers_used': num_workers
            }
        else:
            print(f"⚡ SERIAL processing {file_count} files (organize: {should_organize})")
            if should_organize:
                # Use original serial processing with file organization
                print("📂 ORGANIZING files into folders")
                result = analyzer.organize(temp_dir)
            else:
                # Analyze only without moving files
                print("📊 ANALYZING only - no file movement")
                result = analyzer.analyze_only(temp_dir)
            result['processing_method'] = 'serial'
            result['workers_used'] = 1
        
        # Save to database
        session_id = enhanced_db.save_analysis(temp_dir, result)
        result['session_id'] = session_id
        
        # If organizing, copy organized files back to original location or Desktop
        if should_organize and file_count < 100:  # Only for serial processing
            # Get original folder name from the uploaded files
            original_name = "files"
            
            # Store the demo folder name globally when generating demo
            if hasattr(generate_demo_files, '_last_demo_name'):
                original_name = generate_demo_files._last_demo_name
            else:
                # Check file paths for demo folder pattern
                for file in files:
                    if hasattr(file, 'filename') and file.filename:
                        # Extract folder name from file path
                        if '/' in file.filename:
                            folder_name = file.filename.split('/')[0]
                            if folder_name.startswith('messy_files_'):
                                original_name = folder_name
                                break
                        # Check if filename itself has the pattern
                        elif file.filename.startswith('messy_files_'):
                            original_name = file.filename.split('.')[0]
                            break
                
                # If no demo pattern found, use default
                if original_name == "files":
                    original_name = "uploaded_files"
            
            organized_dir = os.path.expanduser(f"~/Desktop/{original_name}_organized")
            if os.path.exists(organized_dir):
                shutil.rmtree(organized_dir)
            shutil.copytree(temp_dir, organized_dir)
            result['organized_path'] = organized_dir
            print(f"📂 Organized files copied to: {organized_dir}")
        
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
    
    # Random file name generators
    def random_gibberish(length=8):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    def random_date():
        start = datetime(2020, 1, 1)
        end = datetime(2024, 12, 31)
        return start + timedelta(days=random.randint(0, (end - start).days))
    
    # File type pools to randomly select from
    document_names = [
        "final_report", "untitled_document", "budget_2024", "presentation_slides", 
        "random_notes", "important_doc", "meeting_notes", "project_summary",
        "quarterly_review", "expense_report", "invoice", "receipt", "contract"
    ]
    
    document_suffixes = [
        "_FINAL", "_v2", "_backup", "_copy", "_draft", "_real", "_NEW", 
        "_old", "_temp", "_revised", "_updated", "", "_final_FINAL"
    ]
    
    image_prefixes = [
        "IMG_", "screenshot_", "photo_", "scan_", "diagram_", "chart_",
        "picture_", "image_", "snap_", "capture_"
    ]
    
    code_names = [
        "main", "script", "styles", "index", "config", "app", "utils", 
        "helper", "test", "backup", "old_version", "new_feature"
    ]
    
    # Randomly generate files with varied counts per category
    demo_files = []
    
    # Random documents (1-12 files)
    doc_count = random.randint(1, 12)
    for _ in range(doc_count):
        name = random.choice(document_names)
        suffix = random.choice(document_suffixes)
        ext = random.choice(['.pdf', '.docx', '.txt', '.xlsx', '.pptx'])
        filename = f"{name}{suffix}{ext}"
        content = f"Random document content for {filename}\n" + "Lorem ipsum " * random.randint(5, 30)
        demo_files.append((filename, content))
    
    # Random images (0-10 files)
    img_count = random.randint(0, 10)
    for _ in range(img_count):
        prefix = random.choice(image_prefixes)
        number = random.randint(1000, 9999)
        date = random_date().strftime("%Y_%m_%d")
        ext = random.choice(['.jpg', '.jpeg', '.png', '.gif'])
        
        if random.choice([True, False]):
            filename = f"{prefix}{number}{ext}"
        else:
            filename = f"{prefix}{date}{ext}"
        
        demo_files.append((filename, ""))
    
    # Random code files (0-8 files)
    code_count = random.randint(0, 8)
    for _ in range(code_count):
        name = random.choice(code_names)
        suffix = random.choice(["_backup", "_old", "_v2", "_copy", ""])
        ext = random.choice(['.py', '.js', '.css', '.html', '.json'])
        filename = f"{name}{suffix}{ext}"
        
        code_content = {
            '.py': f"# {filename}\nprint('Hello World')\n# Random Python code",
            '.js': f"// {filename}\nconsole.log('JavaScript file');\n// Random JS code",
            '.css': f"/* {filename} */\nbody {{ margin: 0; padding: 0; }}\n/* Random CSS */",
            '.html': f"<!-- {filename} -->\n<html><body><h1>Test Page</h1></body></html>",
            '.json': f'{{"name": "{name}", "version": "{random.randint(1,5)}.0"}}'
        }
        
        demo_files.append((filename, code_content.get(ext, f"Content for {filename}")))
    
    # Random media files (0-6 files)
    media_count = random.randint(0, 6)
    for _ in range(media_count):
        media_names = ["audio_recording", "video_tutorial", "music_track", "voice_memo", "screen_record"]
        name = random.choice(media_names)
        suffix = random.choice(["_meeting", "_part1", "_favorite", "_backup", ""])
        ext = random.choice(['.mp3', '.mp4', '.wav', '.mov'])
        filename = f"{name}{suffix}{ext}"
        demo_files.append((filename, ""))
    
    # Random archives (0-2 files)
    for _ in range(random.randint(0, 2)):
        archive_names = ["backup_files", "project_archive", "old_stuff", "documents"]
        name = random.choice(archive_names)
        year = random.randint(2020, 2024)
        ext = random.choice(['.zip', '.tar.gz', '.rar'])
        filename = f"{name}_{year}{ext}"
        demo_files.append((filename, ""))
    
    # Random temp/misc files (1-3 files)
    for _ in range(random.randint(1, 3)):
        misc_names = ["temp_file", "untitled", "new_file", "copy_of_copy"]
        name = random.choice(misc_names)
        suffix = random.choice(["_delete_later", "_backup", "_1", "_final", ""])
        ext = random.choice(['.tmp', '.bak', '.old', '.txt'])
        filename = f"{name}{suffix}{ext}"
        demo_files.append((filename, f"Temporary content for {filename}"))
    
    # Add some completely random gibberish files (1-2 files)
    for _ in range(random.randint(1, 2)):
        filename = f"{random_gibberish()}.{random.choice(['txt', 'dat', 'log'])}"
        demo_files.append((filename, f"Random gibberish file: {random_gibberish(50)}"))
    
    # Create all the files
    for filename, content in demo_files:
        file_path = os.path.join(demo_dir, filename)
        
        # Create realistic file content
        if filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.mp3', '.mp4', '.wav', '.zip', '.tar.gz', '.rar', '.mov')):
            # Create small binary-like files
            with open(file_path, 'wb') as f:
                f.write(b'DEMO_FILE_' + ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(20, 100))).encode())
        else:
            # Create text files
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    return {
        "message": f"Generated {len(demo_files)} random messy files",
        "demo_path": demo_dir,
        "file_count": len(demo_files),
        "folder_name": demo_folder_name
    }

@app.get("/history")
def get_history(limit: int = 20):
    """
    Return last N analysis sessions.
    """
    return enhanced_db.get_history(limit)
