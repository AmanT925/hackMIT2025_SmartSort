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

    def _get_files_with_metadata(self, directory_path: str) -> List[Tuple[str, int]]:
        """Get files with size metadata for better chunking"""
        file_data = []
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        file_data.append((file_path, size))
                    except OSError:
                        file_data.append((file_path, 0))
        
        # Sort by size for better load balancing
        return sorted(file_data, key=lambda x: x[1], reverse=True)

    def _create_optimized_chunks(self, file_data: List[Tuple[str, int]]) -> List[List[str]]:
        """Create balanced chunks based on file sizes"""
        if len(file_data) <= self.chunk_size:
            return [[fp for fp, _ in file_data]]
        
        chunks = []
        current_chunk = []
        current_size = 0
        size_threshold = sum(size for _, size in file_data) / (len(file_data) // self.chunk_size + 1)
        
        for file_path, size in file_data:
            if len(current_chunk) >= self.chunk_size or current_size >= size_threshold:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = [file_path]
                current_size = size
            else:
                current_chunk.append(file_path)
                current_size += size
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks

    def _process_chunk(self, file_chunk: List[str], chunk_id: int, progress_callback=None) -> List[Dict[str, Any]]:
        """Process a chunk of files with a thread pool"""
        with ThreadPoolExecutor(max_workers=min(4, len(file_chunk))) as executor:
            future_to_file = {
                executor.submit(self.analyze_single_file_advanced, file_path): file_path 
                for file_path in file_chunk
            }
            
            results = []
            for future in as_completed(future_to_file):
                result = future.result()
                if result:
                    results.append(result)
                
                self.progress.update()
                
                if progress_callback and self.progress.processed % 10 == 0:
                    progress_callback(self.progress.get_progress())
        
        return results

    def analyze_single_file_advanced(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Advanced single file analysis with content inspection"""
        try:
            file_info = os.stat(file_path)
            filename = os.path.basename(file_path)
            extension = Path(file_path).suffix.lower()
            
            # Basic metadata
            result = {
                'path': file_path,
                'filename': filename,
                'size': file_info.st_size,
                'created': file_info.st_ctime,
                'modified': file_info.st_mtime,
                'extension': extension,
                'status': 'analyzed'
            }
            
            # Advanced type detection
            result.update(self._detect_file_type_advanced(file_path, extension))
            
            # Content-based analysis
            result.update(self._analyze_file_content(file_path, extension))
            
            # File similarity hash
            result['similarity_hash'] = self._generate_similarity_hash(file_path, file_info.st_size)
            
            # Performance classification
            result['category'] = self._classify_file_advanced(filename, extension, result.get('content_text', ''))
            
            return result
            
        except Exception as e:
            return {
                'path': file_path,
                'filename': os.path.basename(file_path),
                'status': 'error',
                'error': str(e),
                'category': 'Errors'
            }

    def _detect_file_type_advanced(self, file_path: str, extension: str) -> Dict[str, Any]:
        """Advanced file type detection using multiple methods"""
        type_info = {
            'detected_type': 'Unknown',
            'mime_type': 'unknown',
            'type_confidence': 0.0
        }
        
        # Method 1: Extension-based detection
        for category, patterns in self.file_categories.items():
            if extension in patterns['extensions']:
                type_info['detected_type'] = category
                type_info['type_confidence'] = 0.8
                break
        
        # Method 2: MIME type detection
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            type_info['mime_type'] = mime_type
            for category, patterns in self.file_categories.items():
                if any(mime_pattern in mime_type for mime_pattern in patterns['mimes']):
                    if type_info['detected_type'] == 'Unknown':
                        type_info['detected_type'] = category
                        type_info['type_confidence'] = 0.6
                    else:
                        type_info['type_confidence'] = 0.9  # Confirmed by both methods
        
        # Method 3: Magic number detection (if available)
        if MAGIC_AVAILABLE:
            try:
                detected_mime = magic.from_file(file_path, mime=True)
                if detected_mime != type_info['mime_type']:
                    type_info['magic_mime'] = detected_mime
                    type_info['type_confidence'] = max(type_info['type_confidence'], 0.95)
            except Exception:
                pass
        
        return type_info

    def _analyze_file_content(self, file_path: str, extension: str) -> Dict[str, Any]:
        """Analyze file content for additional insights"""
        content_info = {
            'content_analyzed': False,
            'content_text': '',
            'metadata': {}
        }
        
        try:
            # Image metadata analysis
            if extension in ['.jpg', '.jpeg', '.png', '.tiff'] and PIL_AVAILABLE:
                content_info.update(self._analyze_image_content(file_path))
            
            # PDF text extraction
            elif extension == '.pdf' and PDF_AVAILABLE:
                content_info.update(self._analyze_pdf_content(file_path))
            
            # Text file analysis
            elif extension in ['.txt', '.md', '.py', '.js', '.html', '.css']:
                content_info.update(self._analyze_text_content(file_path))
        
        except Exception as e:
            content_info['content_error'] = str(e)
        
        return content_info

    def _analyze_image_content(self, file_path: str) -> Dict[str, Any]:
        """Extract image metadata and properties"""
        try:
            with Image.open(file_path) as img:
                metadata = {
                    'content_analyzed': True,
                    'metadata': {
                        'dimensions': f"{img.width}x{img.height}",
                        'format': img.format,
                        'mode': img.mode
                    }
                }
                
                # Extract EXIF data
                if hasattr(img, '_getexif') and img._getexif():
                    exif = {TAGS.get(tag, tag): value for tag, value in img._getexif().items()}
                    metadata['metadata']['exif'] = {
                        k: str(v) for k, v in exif.items() 
                        if k in ['DateTime', 'Camera', 'Software', 'GPS']
                    }
                
                return metadata
        except Exception:
            return {'content_analyzed': False}

    def _analyze_pdf_content(self, file_path: str) -> Dict[str, Any]:
        """Extract PDF text content"""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages[:3]:  # Limit to first 3 pages for performance
                    text += page.extract_text()
                
                return {
                    'content_analyzed': True,
                    'content_text': text[:500],  # First 500 characters
                    'metadata': {
                        'pages': len(reader.pages),
                        'text_length': len(text)
                    }
                }
        except Exception:
            return {'content_analyzed': False}

    def _analyze_text_content(self, file_path: str) -> Dict[str, Any]:
        """Analyze text file content"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read(1000)  # First 1000 characters
                
                return {
                    'content_analyzed': True,
                    'content_text': content,
                    'metadata': {
                        'encoding': 'utf-8',
                        'lines': content.count('\n'),
                        'words': len(content.split())
                    }
                }
        except Exception:
            return {'content_analyzed': False}

    def _generate_similarity_hash(self, file_path: str, file_size: int) -> str:
        """Generate hash for duplicate detection"""
        try:
            # For small files, use full content hash
            if file_size < 1024 * 1024:  # 1MB
                with open(file_path, 'rb') as f:
                    return hashlib.md5(f.read()).hexdigest()
            else:
                # For large files, use size + first/last chunks
                with open(file_path, 'rb') as f:
                    first_chunk = f.read(8192)
                    f.seek(-8192, 2)
                    last_chunk = f.read(8192)
                    combined = f"{file_size}:{first_chunk.hex()}:{last_chunk.hex()}"
                    return hashlib.md5(combined.encode()).hexdigest()
        except Exception:
            return hashlib.md5(f"{file_path}:{file_size}".encode()).hexdigest()

    def _classify_file_advanced(self, filename: str, extension: str, content: str) -> str:
        """Advanced file classification using multiple signals"""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        # Content-based classification
        for category, keywords in self.content_patterns.items():
            if any(keyword in filename_lower or keyword in content_lower for keyword in keywords):
                return category
        
        # Pattern-based classification
        if 'screenshot' in filename_lower or 'screen shot' in filename_lower:
            return 'Screenshots'
        elif 'untitled' in filename_lower:
            return 'Needs_Attention'
        elif any(word in filename_lower for word in ['backup', 'old', 'temp', 'tmp']):
            return 'Archive'
        
        # Fallback to type-based classification
        for category, patterns in self.file_categories.items():
            if extension in patterns['extensions']:
                return category
        
        return 'Uncategorized'

    def _organize_results(self, results: List[Dict[str, Any]]) -> Tuple[Dict[str, List], Dict[str, List]]:
        """Organize results and detect similarity groups"""
        categorized_files = defaultdict(list)
        similarity_groups = defaultdict(list)
        
        for result in results:
            if result:
                category = result.get('category', 'Uncategorized')
                categorized_files[category].append(result)
                
                # Group by similarity hash for duplicate detection
                sim_hash = result.get('similarity_hash', '')
                if sim_hash:
                    similarity_groups[sim_hash].append(result)
        
        # Filter similarity groups to only those with duplicates
        duplicate_groups = {
            hash_val: files for hash_val, files in similarity_groups.items() 
            if len(files) > 1
        }
        
        return dict(categorized_files), duplicate_groups

    def _calculate_performance_metrics(self, processing_time: float, file_count: int) -> Dict[str, Any]:
        """Calculate detailed performance metrics"""
        return {
            'files_per_second': file_count / processing_time if processing_time > 0 else 0,
            'avg_time_per_file': processing_time / file_count if file_count > 0 else 0,
            'estimated_sequential_time': processing_time * self.num_workers,
            'parallel_speedup': f"{self.num_workers}x theoretical",
            'actual_speedup': f"{min(self.num_workers, file_count)}x practical",
            'worker_utilization': min(100, (file_count / self.num_workers) * 100)
        }

    def _calculate_worker_efficiency(self, processing_time: float, file_count: int) -> Dict[str, Any]:
        """Calculate worker efficiency metrics"""
        ideal_time_per_worker = processing_time / self.num_workers
        actual_files_per_worker = file_count / self.num_workers
        
        return {
            'workers_used': self.num_workers,
            'files_per_worker': actual_files_per_worker,
            'time_per_worker': ideal_time_per_worker,
            'efficiency_score': min(100, (actual_files_per_worker / max(1, self.chunk_size)) * 100)
        }

    def benchmark_performance(self, test_directory: str, worker_counts: List[int] = None) -> Dict[str, Any]:
        """Benchmark performance with different worker counts"""
        if worker_counts is None:
            worker_counts = [1, 2, 4, cpu_count(), cpu_count() * 2]
        
        benchmark_results = {}
        original_workers = self.num_workers
        
        for workers in worker_counts:
            if workers <= cpu_count() * 2:  # Reasonable upper limit
                self.num_workers = workers
                print(f"Benchmarking with {workers} workers...")
                
                start_time = time.time()
                results = self.analyze_directory(test_directory)
                duration = time.time() - start_time
                
                benchmark_results[f"{workers}_workers"] = {
                    'duration': duration,
                    'files_processed': results['files_processed'],
                    'files_per_second': results['performance_metrics']['files_per_second'],
                    'memory_peak': results['system_metrics']['peak_memory_percent']
                }
        
        self.num_workers = original_workers
        return benchmark_results