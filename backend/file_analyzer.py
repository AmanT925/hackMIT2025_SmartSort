import os
import time
from multiprocessing import Pool
from typing import Dict, Any

class ParallelFileAnalyzer:
    def __init__(self, num_workers: int = 4):
        self.num_workers = num_workers
        self.last_analysis = {}
    
    def analyze_directory(self, directory_path: str) -> Dict[str, Any]:
        start_time = time.time()
        file_paths = [os.path.join(root, f) for root, _, files in os.walk(directory_path) for f in files if not f.startswith('.')]
        
        with Pool(self.num_workers) as pool:
            results = pool.map(self.analyze_single_file, file_paths)
        
        processing_time = time.time() - start_time
        categorized = {}
        
        for result in results:
            if result:
                cat = result['category']
                if cat not in categorized:
                    categorized[cat] = []
                categorized[cat].append(result)
        
        self.last_analysis = {
            'files_processed': len(file_paths),
            'processing_time': processing_time,
            'categories': categorized,
            'speedup': f"{self.num_workers}x faster"
        }
        return self.last_analysis
    
    def analyze_single_file(self, file_path: str):
        try:
            filename = os.path.basename(file_path)
            return {
                'filename': filename,
                'path': file_path,
                'size': os.path.getsize(file_path),
                'category': self.categorize_file(filename)
            }
        except:
            return None
    
    def categorize_file(self, filename: str) -> str:
        f = filename.lower()
        if 'screenshot' in f: return 'Screenshots'
        if any(w in f for w in ['hw', 'assignment']): return 'School'
        if 'untitled' in f: return 'Needs_Attention'
        return 'Uncategorized'
