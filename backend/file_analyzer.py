import os
import time
import hashlib
import mimetypes
import psutil
from multiprocessing import Pool, cpu_count
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from dataclasses import dataclass
from collections import defaultdict

# Try to import optional dependencies for content analysis
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

@dataclass
class AnalysisProgress:
    """Thread-safe progress tracking"""
    def __init__(self):
        self.processed = 0
        self.total = 0
        self.lock = threading.Lock()
    
    def update(self, increment: int = 1):
        with self.lock:
            self.processed += increment
    
    def get_progress(self) -> float:
        with self.lock:
            return (self.processed / self.total * 100) if self.total > 0 else 0

class PerformanceMonitor:
    """Monitor system performance during analysis"""
    
    def __init__(self):
        self.start_time = None
        self.memory_usage = []
        self.cpu_usage = []
        
    def start_monitoring(self):
        self.start_time = time.time()
        self.memory_usage = [psutil.virtual_memory().percent]
        self.cpu_usage = [psutil.cpu_percent()]
    
    def update_metrics(self):
        if self.start_time:
            self.memory_usage.append(psutil.virtual_memory().percent)
            self.cpu_usage.append(psutil.cpu_percent())
    
    def get_summary(self) -> Dict[str, Any]:
        return {
            'duration': time.time() - self.start_time if self.start_time else 0,
            'peak_memory_percent': max(self.memory_usage) if self.memory_usage else 0,
            'avg_cpu_percent': sum(self.cpu_usage) / len(self.cpu_usage) if self.cpu_usage else 0,
            'memory_samples': len(self.memory_usage)
        }

class AdvancedFileAnalyzer:
    """Enhanced file analyzer with advanced detection and performance optimization"""
    
    def __init__(self, num_workers: Optional[int] = None, chunk_size: int = 100):
        self.num_workers = num_workers or min(cpu_count(), 8)  # Cap at 8 for efficiency
        self.chunk_size = chunk_size
        self.progress = AnalysisProgress()
        self.performance_monitor = PerformanceMonitor()
        self.last_analysis = {}
        
        # Advanced file type mappings
        self.file_categories = {
            'Images': {
                'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.heic', '.raw'],
                'mimes': ['image/']
            },
            'Videos': {
                'extensions': ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'],
                'mimes': ['video/']
            },
            'Audio': {
                'extensions': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'],
                'mimes': ['audio/']
            },
            'Documents': {
                'extensions': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.pages'],
                'mimes': ['application/pdf', 'application/msword']
            },
            'Spreadsheets': {
                'extensions': ['.xls', '.xlsx', '.csv', '.ods', '.numbers'],
                'mimes': ['application/vnd.ms-excel']
            },
            'Presentations': {
                'extensions': ['.ppt', '.pptx', '.odp', '.key'],
                'mimes': ['application/vnd.ms-powerpoint']
            },
            'Code': {
                'extensions': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php', '.rb', '.go', '.rs', '.swift'],
                'mimes': ['text/x-python', 'application/javascript']
            },
            'Archives': {
                'extensions': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
                'mimes': ['application/zip', 'application/x-rar']
            },
            'Executables': {
                'extensions': ['.exe', '.dmg', '.app', '.deb', '.rpm'],
                'mimes': ['application/x-executable']
            }
        }
        
        # Content-based keyword patterns
        self.content_patterns = {
            'Financial': ['invoice', 'receipt', 'bill', 'tax', 'statement', 'payment', 'bank', 'transaction'],
            'School': ['homework', 'assignment', 'midterm', 'final', 'quiz', 'essay', 'project', 'study', 'syllabus'],
            'Work': ['meeting', 'presentation', 'report', 'proposal', 'contract', 'deadline', 'budget'],
            'Personal': ['vacation', 'family', 'birthday', 'wedding', 'holiday', 'photo', 'memory']
        }

    def analyze_directory(self, directory_path: str, progress_callback=None) -> Dict[str, Any]:
        """Analyze directory with chunked processing and progress tracking"""
        self.performance_monitor.start_monitoring()
        start_time = time.time()
        
        # Get all files with size-based chunking
        file_paths = self._get_files_with_metadata(directory_path)
        file_chunks = self._create_optimized_chunks(file_paths)
        
        self.progress.total = len(file_paths)
        self.progress.processed = 0
        
        print(f"Analyzing {len(file_paths)} files in {len(file_chunks)} chunks with {self.num_workers} workers...")
        
        # Process chunks in parallel
        all_results = []
        for i, chunk in enumerate(file_chunks):
            chunk_results = self._process_chunk(chunk, i, progress_callback)
            all_results.extend(chunk_results)
            
            # Update performance metrics
            self.performance_monitor.update_metrics()
            
            if progress_callback:
                progress_callback(self.progress.get_progress())
        
        processing_time = time.time() - start_time
        
        # Organize and analyze results
        categorized_files, similarity_groups = self._organize_results(all_results)
        performance_metrics = self._calculate_performance_metrics(processing_time, len(file_paths))
        
        self.last_analysis = {
            'files_processed': len(file_paths),
            'processing_time': processing_time,
            'categories': categorized_files,
            'similarity_groups': similarity_groups,
            'performance_metrics': performance_metrics,
            'system_metrics': self.performance_monitor.get_summary(),
            'worker_efficiency': self._calculate_worker_efficiency(processing_time, len(file_paths))
        }
        
        return self.last_analysis

    # ... all the other existing methods remain unchanged ...

    def analyze_file(self, file_path: str) -> dict:
        """Stub method for compatibility with main.py analysis calls"""
        try:
            size = os.path.getsize(file_path)
        except OSError:
            size = 0
        return {
            "file_path": file_path,
            "category": "Uncategorized",
            "size_bytes": size,
            "status": "stub_analyzed"
        }
