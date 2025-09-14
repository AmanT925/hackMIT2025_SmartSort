# backend/main.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import tempfile
import shutil
from concurrent.futures import ProcessPoolExecutor, as_completed
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
        
        # Use parallel processing for 50+ files (lowered threshold for faster demo)
        if file_count >= 50:
            print(f"🚀 PARALLEL processing {file_count} files with {min(cpu_count(), 8)} workers")
            try:
                # Benchmark parallel vs serial for performance comparison
                parallel_start = time.time()
                
                # Split files into chunks for parallel processing
                num_workers = min(cpu_count(), 8)
                chunk_size = max(1, file_count // num_workers)
                chunks = [file_paths[i:i + chunk_size] for i in range(0, len(file_paths), chunk_size)]
                
                all_results = {}
                category_counts = {cat: 0 for cat in analyzer.FILE_CATEGORIES}
                category_files = {cat: [] for cat in analyzer.FILE_CATEGORIES}
                category_files["Others"] = []
                
                # Track worker performance
                worker_times = {}
                
                # Process chunks in parallel using the analyzer
                with ProcessPoolExecutor(max_workers=num_workers) as executor:
                    future_to_chunk = {executor.submit(process_file_chunk, chunk, i): i for i, chunk in enumerate(chunks)}
                    
                    for future in as_completed(future_to_chunk):
                        chunk_id = future_to_chunk[future]
                        try:
                            chunk_result = future.result()
                            worker_times[chunk_id] = chunk_result.get('processing_time', 0)
                            for category, count in chunk_result['category_counts'].items():
                                category_counts[category] += count
                            for category, files in chunk_result['category_files'].items():
                                category_files[category].extend(files)
                        except Exception as exc:
                            print(f'Chunk {chunk_id} generated an exception: {exc}')
                
                parallel_time = time.time() - parallel_start
                
                # Estimate serial time for comparison (simplified calculation)
                # Use average file processing time from workers to estimate serial time
                avg_worker_time = sum(worker_times.values()) / len(worker_times) if worker_times else parallel_time
                estimated_serial_time = avg_worker_time * num_workers  # Rough serial estimate
                
                # Calculate performance metrics
                speedup = estimated_serial_time / parallel_time if parallel_time > 0 else 1
                efficiency = (speedup / num_workers) * 100
                
                result = {
                    'category_counts': category_counts,
                    'category_files': category_files,
                    'files_processed': file_count,
                    'processing_time': parallel_time,
                    'processing_method': 'parallel',
                    'workers_used': num_workers,
                    'performance_analysis': {
                        'parallel_time': round(parallel_time, 3),
                        'estimated_serial_time': round(estimated_serial_time, 3),
                        'speedup': round(speedup, 2),
                        'efficiency': round(efficiency, 1),
                        'throughput': round(file_count / parallel_time, 2),
                        'worker_times': worker_times,
                        'bottleneck_analysis': {
                            'slowest_worker': max(worker_times.values()) if worker_times else 0,
                            'fastest_worker': min(worker_times.values()) if worker_times else 0,
                            'load_balance_ratio': min(worker_times.values()) / max(worker_times.values()) if worker_times and max(worker_times.values()) > 0 else 1
                        }
                    }
                }
            except Exception as e:
                print(f"❌ PARALLEL processing failed: {e}")
                print(f"🔄 Falling back to SERIAL processing")
                # Fall back to serial processing
                result = analyzer.analyze_only(temp_dir)
                result['processing_method'] = 'serial_fallback'
                result['workers_used'] = 1
                result['files_processed'] = file_count
                result['processing_time'] = time.time() - start_time
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
    
    # Create demo files using the utility function
    from utils import create_demo_files
    create_demo_files(demo_dir)
    
    return {
        "message": f"Generated demo files in {demo_folder_name}",
        "demo_path": demo_dir,
        "folder_name": demo_folder_name
    }

@app.post("/generate-large-demo")
async def generate_large_demo_files():
    """
    Generate a medium demo folder with 50-100 files to showcase parallel processing
    """
    import random
    import string
    from datetime import datetime, timedelta
    
    # Generate random gibberish folder name
    random_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    demo_folder_name = f"medium_demo_{random_name}"
    demo_dir = os.path.expanduser(f"~/Desktop/{demo_folder_name}")
    
    # Store the demo folder name for later use in organize function
    generate_demo_files._last_demo_name = demo_folder_name
    
    # Clean up existing demo if it exists
    if os.path.exists(demo_dir):
        shutil.rmtree(demo_dir)
    
    os.makedirs(demo_dir)
    
    # Generate 50-100 files for medium parallel processing demo
    total_files = random.randint(50, 100)
    demo_files = []
    
    print(f"🚀 Generating {total_files} files for medium parallel processing demo...")
    
    # File type pools
    document_names = [
        "report", "document", "budget", "presentation", "notes", "summary", 
        "analysis", "proposal", "contract", "invoice", "receipt", "memo"
    ]
    
    document_suffixes = [
        "_FINAL", "_v2", "_backup", "_copy", "_draft", "_real", "_NEW", 
        "_old", "_temp", "_revised", "_updated", "", "_final_FINAL"
    ]
    
    # Generate files
    for i in range(total_files):
        name = random.choice(document_names)
        suffix = random.choice(document_suffixes)
        ext = random.choice(['.pdf', '.docx', '.txt', '.xlsx', '.pptx', '.csv'])
        filename = f"{name}_{i:03d}{suffix}{ext}"
        
        # Create lightweight content for faster processing
        content_size = random.randint(5, 20)
        content = f"Document {i}: {name}\n" + "Sample content. " * content_size
        
        demo_files.append((filename, content))
    
    # Create all the files
    for filename, content in demo_files:
        file_path = os.path.join(demo_dir, filename)
        
        # Create lightweight files for fast processing
        if filename.endswith(('.pdf', '.docx', '.xlsx', '.pptx')):
            # Create small binary-like files
            with open(file_path, 'wb') as f:
                f.write(b'DEMO_FILE_' + content.encode()[:100])
        else:
            # Create small text files
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content[:200])
    
    return {
        "message": f"Generated {len(demo_files)} files for medium parallel processing demo",
        "demo_path": demo_dir,
        "file_count": len(demo_files),
        "folder_name": demo_folder_name
    }

@app.post("/generate-xl-demo")
async def generate_xl_demo_files():
    """
    Generate an extra large demo folder with 100-200 files to showcase high-scale parallel processing
    """
    import random
    import string
    from datetime import datetime, timedelta
    
    # Generate random gibberish folder name
    random_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    demo_folder_name = f"xl_demo_{random_name}"
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
        "report", "document", "budget", "presentation", "notes", "summary", 
        "analysis", "proposal", "contract", "invoice", "receipt", "memo",
        "specification", "manual", "guide", "tutorial", "readme", "changelog"
    ]
    
    document_suffixes = [
        "_FINAL", "_v2", "_backup", "_copy", "_draft", "_real", "_NEW", 
        "_old", "_temp", "_revised", "_updated", "", "_final_FINAL", "_v3"
    ]
    
    # Generate 100-200 files for extra large parallel processing demo
    total_files = random.randint(100, 200)
    demo_files = []
    
    print(f"🚀 Generating {total_files} files for parallel processing demo...")
    
    # Generate mostly documents to show processing time
    for i in range(total_files):
        name = random.choice(document_names)
        suffix = random.choice(document_suffixes)
        ext = random.choice(['.pdf', '.docx', '.txt', '.xlsx', '.pptx', '.csv'])
        filename = f"{name}_{i:03d}{suffix}{ext}"
        
        # Create lightweight content for faster processing
        content_size = random.randint(5, 20)
        content = f"Document {i}: {name}\n" + "Sample content. " * content_size
        
        demo_files.append((filename, content))
    
    # Create all the files
    for filename, content in demo_files:
        file_path = os.path.join(demo_dir, filename)
        
        # Create lightweight files for fast processing
        if filename.endswith(('.pdf', '.docx', '.xlsx', '.pptx')):
            # Create small binary-like files
            with open(file_path, 'wb') as f:
                f.write(b'DEMO_FILE_' + content.encode()[:100])  # Much smaller
        else:
            # Create small text files
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content[:200])  # Limit text size
    
    return {
        "message": f"Generated {len(demo_files)} files for parallel processing demo",
        "demo_path": demo_dir,
        "file_count": len(demo_files),
        "folder_name": demo_folder_name
    }

def process_file_chunk(file_paths, worker_id):
    """
    Worker function to process a chunk of files in parallel
    """
    import time
    from file_analyzer import AdvancedFileAnalyzer
    
    start_time = time.time()
    analyzer = AdvancedFileAnalyzer()
    
    category_counts = {}
    category_files = {}
    
    for file_path in file_paths:
        try:
            # Get file category
            category = analyzer._categorize_file(file_path)
            
            # Count categories
            if category not in category_counts:
                category_counts[category] = 0
                category_files[category] = []
            
            category_counts[category] += 1
            
            # Add file info
            file_info = {
                'name': os.path.basename(file_path),
                'size': os.path.getsize(file_path),
                'path': file_path
            }
            category_files[category].append(file_info)
            
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            continue
    
    processing_time = time.time() - start_time
    
    return {
        'category_counts': category_counts,
        'category_files': category_files,
        'processing_time': processing_time,
        'worker_id': worker_id
    }

@app.get("/history")
def get_history(limit: int = 20):
    """
    Return last N analysis sessions.
    """
    return enhanced_db.get_history(limit)
