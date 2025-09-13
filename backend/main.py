from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import tempfile
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Import your enhanced modules
from file_analyzer import AdvancedFileAnalyzer
from voice_handler import VoiceHandler
from data_cleaner import AdvancedDataCleaner
from utils import (
    validate_directory, create_demo_files, performance_test_suite, 
    analysis_db, get_system_info, export_analysis_results
)

app = FastAPI(
    title="SmartSort Enhanced API", 
    version="2.0.0",
    description="AI-powered file organizer with advanced parallel processing and intelligent categorization"
)

# Enhanced CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize enhanced components
advanced_analyzer = AdvancedFileAnalyzer(num_workers=4)
voice_handler = VoiceHandler()
data_cleaner = AdvancedDataCleaner()

# Thread pool for CPU-intensive tasks
executor = ThreadPoolExecutor(max_workers=2)

# Progress tracking for long operations
active_analyses = {}

class AnalysisProgress:
    def __init__(self, analysis_id: str):
        self.analysis_id = analysis_id
        self.progress = 0.0
        self.status = "starting"
        self.start_time = datetime.now()
        self.results = None
        self.error = None

@app.get("/")
async def root():
    return {
        "message": "SmartSort Enhanced API is running!",
        "version": "2.0.0",
        "features": [
            "Advanced parallel processing",
            "Content-based file analysis",
            "Intelligent duplicate detection",
            "Performance benchmarking",
            "Analysis caching and history"
        ]
    }

@app.get("/system-info")
async def get_system_information():
    """Get system information for performance context"""
    try:
        system_info = get_system_info()
        return {
            "system_info": system_info,
            "analyzer_config": {
                "workers": advanced_analyzer.num_workers,
                "chunk_size": advanced_analyzer.chunk_size
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_directory(request: Dict[str, Any]):
    """Enhanced directory analysis with progress tracking"""
    directory_path = request.get("directory_path")
    enable_caching = request.get("enable_caching", True)
    
    if not directory_path:
        raise HTTPException(status_code=400, detail="directory_path is required")
    
    # Validate directory
    validation = validate_directory(directory_path)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail=validation["error"])
    
    try:
        # Check for cached results if enabled
        if enable_caching:
            cached_results = analysis_db.get_analysis_history(directory_path, limit=1)
            if cached_results:
                latest = cached_results[0]
                cache_age_hours = (datetime.now() - datetime.fromisoformat(latest['timestamp'])).total_seconds() / 3600
                if cache_age_hours < 1:  # Use cache if less than 1 hour old
                    return {
                        "cached": True,
                        "cache_age_hours": cache_age_hours,
                        **latest
                    }
        
        # Run enhanced analysis
        results = advanced_analyzer.analyze_directory(directory_path)
        
        # Comprehensive issue detection
        all_files = []
        for category_files in results.get('categories', {}).values():
            all_files.extend(category_files)
        
        issues = data_cleaner.detect_comprehensive_issues(all_files)
        recommendations = data_cleaner.generate_cleanup_recommendations(issues)
        
        # Enhanced response
        enhanced_results = {
            **results,
            'issues_detected': issues,
            'cleanup_recommendations': recommendations,
            'directory_stats': validation.get('statistics', {}),
            'analysis_timestamp': datetime.now().isoformat(),
            'cached': False
        }
        
        # Save to database
        if enable_caching:
            analysis_db.save_analysis(directory_path, enhanced_results)
        
        return enhanced_results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-async")
async def analyze_directory_async(request: Dict[str, Any], background_tasks: BackgroundTasks):
    """Start asynchronous analysis for large directories"""
    directory_path = request.get("directory_path")
    analysis_id = f"analysis_{datetime.now().timestamp()}"
    
    if not directory_path:
        raise HTTPException(status_code=400, detail="directory_path is required")
    
    validation = validate_directory(directory_path)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail=validation["error"])
    
    # Estimate if this needs async processing
    file_count = validation.get('statistics', {}).get('total_files', 0)
    if file_count < 100:
        raise HTTPException(status_code=400, detail="Use /analyze for smaller directories")
    
    # Initialize progress tracking
    progress = AnalysisProgress(analysis_id)
    active_analyses[analysis_id] = progress
    
    # Start background analysis
    background_tasks.add_task(run_background_analysis, analysis_id, directory_path)
    
    return {
        "analysis_id": analysis_id,
        "estimated_duration_minutes": file_count / 1000 * 2,  # Rough estimate
        "status": "started",
        "check_progress_url": f"/analysis-progress/{analysis_id}"
    }

async def run_background_analysis(analysis_id: str, directory_path: str):
    """Run analysis in background with progress updates"""
    progress = active_analyses.get(analysis_id)
    if not progress:
        return
    
    try:
        progress.status = "analyzing"
        
        def progress_callback(percent: float):
            progress.progress = percent
        
        # Run analysis in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            executor, 
            lambda: advanced_analyzer.analyze_directory(directory_path, progress_callback)
        )
        
        # Process results
        all_files = []
        for category_files in results.get('categories', {}).values():
            all_files.extend(category_files)
        
        issues = data_cleaner.detect_comprehensive_issues(all_files)
        recommendations = data_cleaner.generate_cleanup_recommendations(issues)
        
        progress.results = {
            **results,
            'issues_detected': issues,
            'cleanup_recommendations': recommendations,
            'analysis_timestamp': datetime.now().isoformat()
        }
        progress.status = "completed"
        progress.progress = 100.0
        
        # Save to database
        analysis_db.save_analysis(directory_path, progress.results)
        
    except Exception as e:
        progress.status = "error"
        progress.error = str(e)

@app.get("/analysis-progress/{analysis_id}")
async def get_analysis_progress(analysis_id: str):
    """Get progress of background analysis"""
    progress = active_analyses.get(analysis_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    response = {
        "analysis_id": analysis_id,
        "status": progress.status,
        "progress_percent": progress.progress,
        "duration_seconds": (datetime.now() - progress.start_time).total_seconds()
    }
    
    if progress.status == "completed" and progress.results:
        response["results"] = progress.results
    elif progress.status == "error":
        response["error"] = progress.error
    
    return response

@app.post("/benchmark-performance")
async def benchmark_performance(request: Dict[str, Any]):
    """Benchmark performance with different configurations"""
    test_file_count = request.get("file_count", 500)
    worker_counts = request.get("worker_counts", [1, 2, 4, 8])
    
    try:
        # Create test dataset
        test_dir = performance_test_suite.create_large_test_dataset(
            file_count=test_file_count,
            duplicate_ratio=0.2,
            similarity_ratio=0.1
        )
        
        # Run benchmarks
        benchmark_results = advanced_analyzer.benchmark_performance(test_dir, worker_counts)
        
        # Save benchmark results
        for config, metrics in benchmark_results.items():
            worker_count = int(config.split('_')[0])
            analysis_db.save_benchmark(
                test_name=f"benchmark_{test_file_count}_files",
                worker_count=worker_count,
                file_count=test_file_count,
                duration=metrics['duration'],
                files_per_second=metrics['files_per_second'],
                memory_usage=metrics.get('memory_peak', 0)
            )
        
        return {
            "test_directory": test_dir,
            "file_count": test_file_count,
            "benchmark_results": benchmark_results,
            "recommendation": recommend_optimal_workers(benchmark_results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def recommend_optimal_workers(benchmark_results: Dict[str, Any]) -> Dict[str, Any]:
    """Recommend optimal worker count based on benchmark results"""
    best_config = None
    best_performance = 0
    
    for config, metrics in benchmark_results.items():
        # Score based on files per second with memory penalty
        score = metrics['files_per_second'] - (metrics.get('memory_peak', 0) * 0.1)
        if score > best_performance:
            best_performance = score
            best_config = config
    
    return {
        "recommended_workers": int(best_config.split('_')[0]) if best_config else 4,
        "performance_score": best_performance,
        "reasoning": "Optimized for speed while managing memory usage"
    }

@app.get("/analysis-history")
async def get_analysis_history(directory_path: Optional[str] = None, limit: int = 10):
    """Get analysis history from database"""
    try:
        history = analysis_db.get_analysis_history(directory_path, limit)
        return {
            "history": history,
            "total_entries": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice-command")
async def process_voice_command(request: Dict[str, str]):
    """Enhanced voice command processing"""
    command_text = request.get("text", "")
    
    if not command_text:
        raise HTTPException(status_code=400, detail="text is required")
    
    try:
        response = voice_handler.process_command(command_text, advanced_analyzer)
        
        # Add context-aware suggestions
        if response.get("action") == "help":
            response["suggestions"] = [
                "Try: 'analyze my downloads folder'",
                "Try: 'find duplicates in my documents'",
                "Try: 'roast my file organization'",
                "Try: 'benchmark my system performance'"
            ]
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/demo/create")
async def create_demo():
    """Create enhanced demo files for testing"""
    try:
        demo_dir = os.path.expanduser("~/Desktop/SmartSort_Enhanced_Demo")
        created_dir = create_demo_files(demo_dir)
        
        # Quick analysis for demo stats
        stats = validate_directory(created_dir)
        
        return {
            "message": "Enhanced demo files created successfully",
            "path": created_dir,
            "statistics": stats.get('statistics', {}),
            "demo_features": [
                "Exact duplicates for testing",
                "Similar files with version conflicts",
                "Various file types and categories",
                "Problematic naming patterns",
                "Realistic file sizes and content"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export-results")
async def export_analysis_results(request: Dict[str, Any]):
    """Export analysis results to file"""
    analysis_data = request.get("analysis_data")
    output_format = request.get("format", "json")
    
    if not analysis_data:
        raise HTTPException(status_code=400, detail="analysis_data is required")
    
    try:
        # Create export file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"/tmp/smartsort_export_{timestamp}.{output_format}"
        
        export_result = export_analysis_results(analysis_data, output_path)
        
        if export_result["success"]:
            return {
                "export_path": export_result["path"],
                "file_size": export_result["formatted_size"],
                "format": output_format,
                "timestamp": timestamp
            }
        else:
            raise HTTPException(status_code=500, detail=export_result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cleanup-recommendations/{analysis_id}")
async def get_cleanup_recommendations(analysis_id: str):
    """Get detailed cleanup recommendations for an analysis"""
    # This could be expanded to store recommendations by ID
    raise HTTPException(status_code=501, detail="Feature coming soon")

@app.delete("/cache/clear")
async def clear_analysis_cache():
    """Clear analysis cache"""
    try:
        analysis_db.cleanup_old_cache(days_old=0)  # Clear all cache
        return {"message": "Analysis cache cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)