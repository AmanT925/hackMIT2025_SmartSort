# backend/smart_parallel_analyzer.py
import os
import time
import hashlib
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count
import psutil
from typing import Dict, List, Any
from dataclasses import dataclass
from pathlib import Path

@dataclass
class FileResult:
    filepath: str
    category: str
    size: int
    processing_time: float
    worker_id: int = 0

class SmartParallelAnalyzer:
    """
    Smart analyzer that automatically chooses serial vs parallel based on file count
    """
    
    def __init__(self, parallel_threshold: int = 10):
        self.parallel_threshold = parallel_threshold
        self.max_workers = min(cpu_count(), 8)  # Cap at 8 workers
        
    def analyze_files(self, temp_dir: str) -> Dict[str, Any]:
        """
        Main analysis function with automatic serial/parallel switching
        """
        start_time = time.time()
        
        # Get all files
        file_paths = self._get_file_paths(temp_dir)
        file_count = len(file_paths)
        
        # Choose processing method based on file count
        if file_count >= self.parallel_threshold:
            print(f"Using PARALLEL processing for {file_count} files")
            results = self._process_parallel(file_paths)
            method = "parallel"
        else:
            print(f"Using SERIAL processing for {file_count} files")
            results = self._process_serial(file_paths)
            method = "serial"
        
        # Categorize results
        categories = self._categorize_results(results)
        
        total_time = time.time() - start_time
        
        # Calculate performance metrics
        performance_metrics = {
            'processing_method': method,
            'file_count': file_count,
            'processing_time': round(total_time, 3),
            'files_per_second': round(file_count / total_time, 2) if total_time > 0 else 0,
            'workers_used': self.max_workers if method == 'parallel' else 1,
            'memory_usage_mb': round(psutil.Process().memory_info().rss / 1024 / 1024, 2)
        }
        
        return {
            'category_counts': categories,
            'performance_metrics': performance_metrics,
            'files_processed': file_count,
            'processing_time': total_time
        }
    
    def _get_file_paths(self, directory: str) -> List[str]:
        """Get all file paths from directory"""
        file_paths = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_paths.append(os.path.join(root, file))
        return file_paths
    
    def _process_serial(self, file_paths: List[str]) -> List[FileResult]:
        """Serial processing for small file sets"""
        results = []
        for i, filepath in enumerate(file_paths):
            result = self._analyze_single_file(filepath, worker_id=0)
            results.append(result)
        return results
    
    def _process_parallel(self, file_paths: List[str]) -> List[FileResult]:
        """Parallel processing for large file sets"""
        results = []
        
        # Split files into chunks for workers
        chunk_size = max(1, len(file_paths) // self.max_workers)
        chunks = [file_paths[i:i + chunk_size] for i in range(0, len(file_paths), chunk_size)]
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit chunks to workers
            future_to_chunk = {
                executor.submit(process_file_chunk, chunk, worker_id): worker_id 
                for worker_id, chunk in enumerate(chunks)
            }
            
            # Collect results
            for future in as_completed(future_to_chunk):
                worker_id = future_to_chunk[future]
                try:
                    chunk_results = future.result()
                    results.extend(chunk_results)
                except Exception as exc:
                    print(f'Worker {worker_id} generated an exception: {exc}')
        
        return results
    
    def _analyze_single_file(self, filepath: str, worker_id: int = 0) -> FileResult:
        """Analyze a single file"""
        start_time = time.time()
        
        try:
            # Get file info
            stat = os.stat(filepath)
            file_size = stat.st_size
            
            # Determine category
            category = self._get_file_category(filepath)
            
            processing_time = time.time() - start_time
            
            return FileResult(
                filepath=filepath,
                category=category,
                size=file_size,
                processing_time=processing_time,
                worker_id=worker_id
            )
        except Exception as e:
            # Return error result
            return FileResult(
                filepath=filepath,
                category="Error",
                size=0,
                processing_time=time.time() - start_time,
                worker_id=worker_id
            )
    
    def _get_file_category(self, filepath: str) -> str:
        """Determine file category based on extension"""
        ext = Path(filepath).suffix.lower()
        
        categories = {
            'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp', '.heic'],
            'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
            'Spreadsheets': ['.xlsx', '.xls', '.csv', '.ods'],
            'Presentations': ['.pptx', '.ppt', '.odp'],
            'Code': ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.html', '.css', '.sql', '.json'],
            'Archives': ['.zip', '.tar', '.gz', '.rar', '.7z'],
            'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
            'Video': ['.mp4', '.avi', '.mov', '.mkv', '.wmv'],
            'Other': []
        }
        
        for category, extensions in categories.items():
            if ext in extensions:
                return category
        
        return 'Other'
    
    def _categorize_results(self, results: List[FileResult]) -> Dict[str, int]:
        """Count files by category"""
        categories = {}
        for result in results:
            categories[result.category] = categories.get(result.category, 0) + 1
        return categories

def process_file_chunk(file_paths: List[str], worker_id: int) -> List[FileResult]:
    """Worker function for parallel processing"""
    analyzer = SmartParallelAnalyzer()
    results = []
    
    for filepath in file_paths:
        result = analyzer._analyze_single_file(filepath, worker_id)
        results.append(result)
    
    return results
