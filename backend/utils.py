import os
import shutil
import sqlite3
import json
import time
import random
import string
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime, timedelta
import hashlib
from contextlib import contextmanager

class PerformanceTestSuite:
    """Generate test datasets and benchmark performance"""
    
    def __init__(self, base_test_dir: str = None):
        self.base_test_dir = base_test_dir or os.path.expanduser("~/Desktop/SmartSort_Performance_Tests")
    
    def create_large_test_dataset(self, 
                                  file_count: int = 1000, 
                                  duplicate_ratio: float = 0.2,
                                  similarity_ratio: float = 0.15) -> str:
        """Create a large test dataset with controlled characteristics"""
        test_dir = os.path.join(self.base_test_dir, f"large_dataset_{file_count}")
        
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        os.makedirs(test_dir)
        
        print(f"Creating test dataset with {file_count} files...")
        
        # Calculate file distribution
        num_duplicates = int(file_count * duplicate_ratio)
        num_similar = int(file_count * similarity_ratio)
        num_unique = file_count - num_duplicates - num_similar
        
        file_templates = self._generate_file_templates()
        created_files = []
        
        # Create unique files
        for i in range(num_unique):
            template = random.choice(file_templates)
            filename = self._generate_filename(template, i)
            file_path = os.path.join(test_dir, filename)
            content = self._generate_file_content(template, i)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            created_files.append(file_path)
        
        # Create duplicate files
        base_files = random.sample(created_files, min(len(created_files), num_duplicates // 2))
        for i, base_file in enumerate(base_files):
            for j in range(2):  # Create 2 duplicates of each base file
                dup_filename = f"duplicate_{i}_{j}_{os.path.basename(base_file)}"
                dup_path = os.path.join(test_dir, dup_filename)
                shutil.copy2(base_file, dup_path)
        
        # Create similar files
        similar_base_files = random.sample(created_files, min(len(created_files), num_similar // 3))
        for i, base_file in enumerate(similar_base_files):
            for j in range(3):  # Create 3 similar versions
                similar_filename = self._create_similar_filename(os.path.basename(base_file), j)
                similar_path = os.path.join(test_dir, similar_filename)
                self._create_similar_file(base_file, similar_path, j)
        
        print(f"Created test dataset at: {test_dir}")
        return test_dir
    
    def _generate_file_templates(self) -> List[Dict[str, Any]]:
        """Generate file templates for different categories"""
        return [
            {'category': 'school', 'extensions': ['.pdf', '.docx', '.txt'], 
             'prefixes': ['homework', 'assignment', 'essay', 'notes', 'study_guide']},
            {'category': 'financial', 'extensions': ['.pdf', '.jpg'], 
             'prefixes': ['invoice', 'receipt', 'statement', 'tax_doc']},
            {'category': 'images', 'extensions': ['.jpg', '.png', '.gif'], 
             'prefixes': ['IMG', 'photo', 'picture', 'screenshot']},
            {'category': 'code', 'extensions': ['.py', '.js', '.html', '.css'], 
             'prefixes': ['main', 'script', 'index', 'app', 'component']},
            {'category': 'documents', 'extensions': ['.pdf', '.docx', '.txt'], 
             'prefixes': ['document', 'report', 'memo', 'letter']},
            {'category': 'media', 'extensions': ['.mp4', '.mp3', '.avi'], 
             'prefixes': ['video', 'audio', 'recording', 'clip']}
        ]
    
    def _generate_filename(self, template: Dict[str, Any], index: int) -> str:
        """Generate a filename based on template"""
        prefix = random.choice(template['prefixes'])
        extension = random.choice(template['extensions'])
        
        # Add some randomness
        if random.random() < 0.3:  # 30% chance of generic name
            return f"Untitled_{index}{extension}"
        elif random.random() < 0.2:  # 20% chance of version indicator
            version = random.choice(['_v1', '_v2', '_final', '_copy', '_(1)'])
            return f"{prefix}_{index}{version}{extension}"
        else:
            return f"{prefix}_{index}{extension}"
    
    def _generate_file_content(self, template: Dict[str, Any], index: int) -> str:
        """Generate appropriate content for file type"""
        category = template['category']
        
        if category == 'school':
            return f"""Assignment {index}
            
This is homework assignment number {index}.
Topics covered: {random.choice(['Math', 'Science', 'History', 'English'])}
Due date: {datetime.now() + timedelta(days=random.randint(1, 30))}

Content: {'Lorem ipsum dolor sit amet ' * random.randint(10, 50)}
"""
        elif category == 'financial':
            return f"""Invoice #{index}
Amount: ${random.randint(10, 1000)}.{random.randint(10, 99)}
Date: {datetime.now() - timedelta(days=random.randint(1, 365))}
Vendor: {random.choice(['Amazon', 'Walmart', 'Target', 'Best Buy'])}
"""
        elif category == 'code':
            return f"""# File {index}
def function_{index}():
    '''Generated function for testing'''
    return {random.randint(1, 100)}

if __name__ == "__main__":
    result = function_{index}()
    print(f"Result: {{result}}")
"""
        else:
            return f"Test content for file {index}\n" + "Sample data " * random.randint(5, 20)
    
    def _create_similar_filename(self, base_filename: str, variant: int) -> str:
        """Create similar filename variants"""
        name, ext = os.path.splitext(base_filename)
        
        variants = [
            f"{name}_copy{ext}",
            f"{name}_v{variant + 2}{ext}",
            f"{name}_final{ext}",
            f"Copy of {base_filename}",
            f"{name}_{variant + 1}{ext}"
        ]
        
        return variants[variant % len(variants)]
    
    def _create_similar_file(self, base_file: str, target_path: str, variant: int):
        """Create a similar file with slight modifications"""
        try:
            with open(base_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Make slight modifications
            if variant == 0:
                content += f"\n\n# Modified version {variant}"
            elif variant == 1:
                content = content.replace("Lorem", "Lorem Modified")
            else:
                content = f"# Variant {variant}\n" + content
            
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception:
            # Fallback: just copy the file
            shutil.copy2(base_file, target_path)

class AnalysisDatabase:
    """SQLite database for storing analysis history and caching"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.path.expanduser("~/smartsort_analysis.db")
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema"""
        with self._get_connection() as conn:
            # Analysis history table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS analysis_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    directory_path TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    files_processed INTEGER,
                    processing_time REAL,
                    worker_count INTEGER,
                    performance_metrics TEXT,
                    categories TEXT,
                    issues_found TEXT
                )
            ''')
            
            # File cache table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS file_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    file_hash TEXT,
                    size INTEGER,
                    modified_time REAL,
                    analysis_result TEXT,
                    cached_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Performance benchmarks table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS benchmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_name TEXT,
                    worker_count INTEGER,
                    file_count INTEGER,
                    duration REAL,
                    files_per_second REAL,
                    memory_usage REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with proper cleanup"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def save_analysis(self, directory_path: str, analysis_results: Dict[str, Any]):
        """Save analysis results to database"""
        with self._get_connection() as conn:
            conn.execute('''
                INSERT INTO analysis_history 
                (directory_path, timestamp, files_processed, processing_time, 
                 worker_count, performance_metrics, categories, issues_found)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                directory_path,
                datetime.now(),
                analysis_results.get('files_processed', 0),
                analysis_results.get('processing_time', 0),
                analysis_results.get('worker_count', 0),
                json.dumps(analysis_results.get('performance_metrics', {})),
                json.dumps(analysis_results.get('categories', {})),
                json.dumps(analysis_results.get('issues', {}))
            ))
            conn.commit()
    
    def get_analysis_history(self, directory_path: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get analysis history"""
        with self._get_connection() as conn:
            if directory_path:
                cursor = conn.execute('''
                    SELECT * FROM analysis_history 
                    WHERE directory_path = ? 
                    ORDER BY timestamp DESC LIMIT ?
                ''', (directory_path, limit))
            else:
                cursor = conn.execute('''
                    SELECT * FROM analysis_history 
                    ORDER BY timestamp DESC LIMIT ?
                ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def cache_file_analysis(self, file_path: str, analysis_result: Dict[str, Any]):
        """Cache individual file analysis result"""
        try:
            file_stat = os.stat(file_path)
            file_hash = hashlib.md5(f"{file_path}:{file_stat.st_size}:{file_stat.st_mtime}".encode()).hexdigest()
            
            with self._get_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO file_cache 
                    (file_path, file_hash, size, modified_time, analysis_result)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    file_path,
                    file_hash,
                    file_stat.st_size,
                    file_stat.st_mtime,
                    json.dumps(analysis_result)
                ))
                conn.commit()
        except Exception as e:
            print(f"Failed to cache file analysis: {e}")
    
    def get_cached_analysis(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get cached analysis if file hasn't changed"""
        try:
            file_stat = os.stat(file_path)
            current_hash = hashlib.md5(f"{file_path}:{file_stat.st_size}:{file_stat.st_mtime}".encode()).hexdigest()
            
            with self._get_connection() as conn:
                cursor = conn.execute('''
                    SELECT analysis_result FROM file_cache 
                    WHERE file_path = ? AND file_hash = ?
                ''', (file_path, current_hash))
                
                row = cursor.fetchone()
                if row:
                    return json.loads(row['analysis_result'])
        except Exception:
            pass
        
        return None
    
    def save_benchmark(self, test_name: str, worker_count: int, file_count: int, 
                      duration: float, files_per_second: float, memory_usage: float):
        """Save benchmark results"""
        with self._get_connection() as conn:
            conn.execute('''
                INSERT INTO benchmarks 
                (test_name, worker_count, file_count, duration, files_per_second, memory_usage)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (test_name, worker_count, file_count, duration, files_per_second, memory_usage))
            conn.commit()
    
    def get_benchmark_history(self, test_name: str = None) -> List[Dict[str, Any]]:
        """Get benchmark history"""
        with self._get_connection() as conn:
            if test_name:
                cursor = conn.execute('''
                    SELECT * FROM benchmarks 
                    WHERE test_name = ? 
                    ORDER BY timestamp DESC
                ''', (test_name,))
            else:
                cursor = conn.execute('''
                    SELECT * FROM benchmarks 
                    ORDER BY timestamp DESC
                ''')
            
            return [dict(row) for row in cursor.fetchall()]
    
    def cleanup_old_cache(self, days_old: int = 30):
        """Clean up old cache entries"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        with self._get_connection() as conn:
            conn.execute('''
                DELETE FROM file_cache 
                WHERE cached_at < ?
            ''', (cutoff_date,))
            conn.commit()

def validate_directory(directory_path: str) -> Dict[str, Any]:
    """Enhanced directory validation with detailed info"""
    try:
        if not os.path.exists(directory_path):
            return {"valid": False, "error": "Directory does not exist"}
        
        if not os.path.isdir(directory_path):
            return {"valid": False, "error": "Path is not a directory"}
        
        if not os.access(directory_path, os.R_OK):
            return {"valid": False, "error": "Directory is not readable"}
        
        # Gather detailed statistics
        stats = {
            'total_files': 0,
            'total_size': 0,
            'file_types': {},
            'depth_analysis': {'max_depth': 0, 'avg_depth': 0},
            'size_distribution': {'small': 0, 'medium': 0, 'large': 0, 'empty': 0}
        }
        
        depth_sum = 0
        depth_count = 0
        
        for root, dirs, files in os.walk(directory_path):
            depth = len(Path(root).parts) - len(Path(directory_path).parts)
            stats['depth_analysis']['max_depth'] = max(stats['depth_analysis']['max_depth'], depth)
            
            for file in files:
                if not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    try:
                        file_size = os.path.getsize(file_path)
                        stats['total_files'] += 1
                        stats['total_size'] += file_size
                        depth_sum += depth
                        depth_count += 1
                        
                        # File type counting
                        ext = Path(file).suffix.lower()
                        stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1
                        
                        # Size distribution
                        if file_size == 0:
                            stats['size_distribution']['empty'] += 1
                        elif file_size < 1024 * 1024:  # < 1MB
                            stats['size_distribution']['small'] += 1
                        elif file_size < 100 * 1024 * 1024:  # < 100MB
                            stats['size_distribution']['medium'] += 1
                        else:
                            stats['size_distribution']['large'] += 1
                            
                    except OSError:
                        continue
        
        if depth_count > 0:
            stats['depth_analysis']['avg_depth'] = depth_sum / depth_count
        
        return {
            "valid": True,
            "path": os.path.abspath(directory_path),
            "statistics": stats,
            "estimated_processing_time": estimate_processing_time(stats['total_files'])
        }
        
    except Exception as e:
        return {"valid": False, "error": str(e)}

def estimate_processing_time(file_count: int, workers: int = 4) -> Dict[str, float]:
    """Estimate processing time based on file count and system"""
    # Base processing rate: files per second per worker
    base_rate = 10  # Conservative estimate
    
    sequential_time = file_count / base_rate
    parallel_time = file_count / (base_rate * workers)
    
    return {
        'sequential_seconds': sequential_time,
        'parallel_seconds': parallel_time,
        'estimated_speedup': sequential_time / parallel_time if parallel_time > 0 else 1
    }

def create_demo_files(demo_dir: str) -> str:
    """Create comprehensive demo files for testing"""
    if os.path.exists(demo_dir):
        shutil.rmtree(demo_dir)
    
    os.makedirs(demo_dir)
    
    # Enhanced demo files with realistic scenarios
    demo_files = [
        # School files with version conflicts
        ("Physics_HW_3_final.pdf", "Physics homework assignment on thermodynamics"),
        ("Physics_HW_3_final_v2.pdf", "Physics homework assignment on thermodynamics - revised"),
        ("Math_midterm_study_guide.docx", "Study guide for calculus midterm exam"),
        ("Essay_draft_final_FINAL.txt", "English essay on Shakespeare - final version"),
        
        # Generic/problematic names
        ("Untitled.docx", "Generic document with no clear purpose"),
        ("Untitled (1).docx", "Another generic document"),
        ("document.pdf", "Generic document name"),
        ("New folder/Untitled.txt", "Nested generic file"),
        
        # Financial documents
        ("Phone_bill_March_2024.pdf", "Monthly phone bill - $89.99"),
        ("grocery_receipt_042324.jpg", "Receipt from grocery store - $127.45"),
        ("tax_documents_2023.pdf", "Tax filing documents for 2023"),
        ("bank_statement_april.pdf", "Bank statement for April 2024"),
        
        # Screenshots and images
        ("Screenshot 2024-03-15 at 2.30.45 PM.png", "Screenshot content"),
        ("Screen Shot 2024-04-01 at 10.15.23 AM.png", "Another screenshot"),
        ("IMG_1234.HEIC", "Photo from iPhone camera"),
        ("IMG_1235.HEIC", "Similar photo from iPhone camera"),
        ("photo_vacation_2024.jpg", "Vacation photo from summer trip"),
        
        # Work-related files
        ("meeting_notes_q2_review.txt", "Notes from Q2 performance review meeting"),
        ("presentation_draft.pptx", "Draft presentation for client meeting"),
        ("budget_proposal_2024.xlsx", "Annual budget proposal spreadsheet"),
        
        # Downloads and temporary files
        ("download.pdf", "Generic downloaded file"),
        ("download (1).pdf", "Another generic downloaded file"),
        ("temp_file.tmp", "Temporary file that should be cleaned"),
        (".DS_Store", "System file that should be ignored"),
        
        # Code files
        ("main.py", "Python main application file"),
        ("script.js", "JavaScript utility script"),
        ("index.html", "HTML homepage file"),
        ("styles.css", "CSS stylesheet"),
        
        # Media files
        ("video_call_recording.mp4", "Recorded video call"),
        ("audio_note.mp3", "Voice memo recording"),
        
        # Duplicate content (same content, different names)
        ("important_document.pdf", "This is important content for testing"),
        ("copy_of_important_document.pdf", "This is important content for testing"),
        ("important_document_backup.pdf", "This is important content for testing"),
    ]
    
    for file_path, content in demo_files:
        full_path = os.path.join(demo_dir, file_path)
        
        # Create subdirectories if needed
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Create file with realistic content
        with open(full_path, 'w', encoding='utf-8') as f:
            if file_path.endswith('.py'):
                f.write(f'#!/usr/bin/env python3\n"""{content}"""\n\ndef main():\n    print("Hello, World!")\n\nif __name__ == "__main__":\n    main()\n')
            elif file_path.endswith('.js'):
                f.write(f'// {content}\nconsole.log("Hello, World!");\n')
            elif file_path.endswith('.html'):
                f.write(f'<!DOCTYPE html>\n<html>\n<head><title>{content}</title></head>\n<body><h1>Hello, World!</h1></body>\n</html>\n')
            elif file_path.endswith('.css'):
                f.write(f'/* {content} */\nbody {{ font-family: Arial, sans-serif; }}\n')
            else:
                f.write(f"{content}\n\nGenerated on: {datetime.now()}\nFile size: {len(content)} characters\n")
    
    print(f"Created {len(demo_files)} demo files in {demo_dir}")
    return demo_dir

def format_file_size(size_bytes: int) -> str:
    """Convert bytes to human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"

def format_duration(seconds: float) -> str:
    """Format duration in human readable format"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:.0f}m {secs:.0f}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours:.0f}h {minutes:.0f}m"

def export_analysis_results(results: Dict[str, Any], output_path: str) -> Dict[str, Any]:
    """Export analysis results to JSON file with enhanced metadata"""
    try:
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'analysis_results': results,
            'metadata': {
                'version': '2.0',
                'export_format': 'smartsort_analysis',
                'file_count': results.get('files_processed', 0),
                'processing_time': results.get('processing_time', 0),
                'categories_found': len(results.get('categories', {}))
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        file_size = os.path.getsize(output_path)
        return {
            'success': True,
            'path': output_path,
            'file_size': file_size,
            'formatted_size': format_file_size(file_size)
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_system_info() -> Dict[str, Any]:
    """Get detailed system information for performance context"""
    import platform
    import psutil
    
    return {
        'platform': platform.system(),
        'platform_release': platform.release(),
        'platform_version': platform.version(),
        'architecture': platform.machine(),
        'processor': platform.processor(),
        'cpu_count_physical': psutil.cpu_count(logical=False),
        'cpu_count_logical': psutil.cpu_count(logical=True),
        'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
        'memory_available_gb': round(psutil.virtual_memory().available / (1024**3), 2),
        'python_version': platform.python_version(),
        'disk_usage': {
            'total_gb': round(psutil.disk_usage('/').total / (1024**3), 2),
            'free_gb': round(psutil.disk_usage('/').free / (1024**3), 2)
        }
    }

def simulate_file_operations(structure: Dict[str, List[str]], base_path: str, dry_run: bool = True) -> Dict[str, Any]:
    """Simulate or execute file organization operations"""
    operations = []
    total_size_moved = 0
    
    for folder, files in structure.items():
        target_dir = os.path.join(base_path, folder)
        
        if not dry_run:
            os.makedirs(target_dir, exist_ok=True)
        
        operations.append({
            "action": "create_directory",
            "path": target_dir,
            "file_count": len(files),
            "executed": not dry_run
        })
        
        for filename in files:
            source_path = os.path.join(base_path, filename)
            destination_path = os.path.join(target_dir, filename)
            
            file_size = 0
            if os.path.exists(source_path):
                try:
                    file_size = os.path.getsize(source_path)
                    total_size_moved += file_size
                    
                    if not dry_run:
                        shutil.move(source_path, destination_path)
                except Exception as e:
                    operations.append({
                        "action": "move_file_error",
                        "source": source_path,
                        "destination": destination_path,
                        "error": str(e),
                        "executed": False
                    })
                    continue
            
            operations.append({
                "action": "move_file",
                "source": source_path,
                "destination": destination_path,
                "size": file_size,
                "executed": not dry_run
            })
    
    summary = {
        "total_operations": len(operations),
        "directories_created": len([op for op in operations if op["action"] == "create_directory"]),
        "files_moved": len([op for op in operations if op["action"] == "move_file"]),
        "total_size_moved": total_size_moved,
        "formatted_size_moved": format_file_size(total_size_moved),
        "operations": operations[:20],  # Show first 20 operations
        "dry_run": dry_run,
        "note": "This is a simulation - no files were actually moved" if dry_run else "Files were actually moved"
    }
    
    return summary

# Initialize global instances
performance_test_suite = PerformanceTestSuite()
analysis_db = AnalysisDatabase()