from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import os
from datetime import datetime
from file_analyzer import AdvancedFileAnalyzer
from database_manager import enhanced_db
from utils import validate_directory, create_demo_files, get_system_info, export_analysis_results

app = FastAPI(
    title="SmartSort Enhanced API",
    version="2.0.0",
    description="AI-powered file organizer with advanced parallel processing and intelligent categorization"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzer
advanced_analyzer = AdvancedFileAnalyzer(num_workers=4)

@app.get("/")
async def root():
    return {"message": "SmartSort Enhanced API is running!", "version": "2.0.0"}

@app.post("/analyze")
async def analyze_directory(request: Dict[str, Any]):
    directory_path = request.get("directory_path")
    enable_caching = request.get("enable_caching", True)

    if not directory_path:
        raise HTTPException(status_code=400, detail="directory_path is required")

    validation = validate_directory(directory_path)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail=validation["error"])

    try:
        session_id = enhanced_db.save_analysis(directory_path, {"files_processed": 0, "processing_time": 0})
        results = []

        for root, _, files in os.walk(directory_path):
            for f in files:
                file_path = os.path.join(root, f)
                cached_result = enhanced_db.get_cached_file(file_path) if enable_caching else None

                if cached_result:
                    results.append({"file": file_path, "result": cached_result, "cached": True})
                else:
                    analysis_result = advanced_analyzer.analyze_file(file_path)
                    if enable_caching:
                        enhanced_db.save_file_result(file_path, analysis_result, session_id)
                    results.append({"file": file_path, "result": analysis_result, "cached": False})

        enhanced_db.save_analysis(directory_path, {"files_processed": len(results)})

        return {"session_id": session_id, "results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
async def get_analysis_history(limit: int = 10):
    try:
        history = enhanced_db.get_history(limit)
        return {"history": history, "total_entries": len(history)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history/{session_id}")
async def get_session_files(session_id: str):
    try:
        files = enhanced_db.get_session_files(session_id)
        return {"files": files, "total_files": len(files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/cache/clear")
async def clear_analysis_cache():
    try:
        with enhanced_db._get_connection() as conn:
            conn.execute("DELETE FROM file_cache")
            conn.commit()
        return {"message": "Analysis cache cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system-info")
async def get_system_information():
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

@app.get("/demo/create")
async def create_demo():
    try:
        demo_dir = os.path.expanduser("~/Desktop/SmartSort_Enhanced_Demo")
        created_dir = create_demo_files(demo_dir)
        stats = validate_directory(created_dir)
        return {"message": "Enhanced demo files created", "path": created_dir, "statistics": stats.get('statistics', {})}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export-results")
async def export_results(request: Dict[str, Any]):
    analysis_data = request.get("analysis_data")
    output_format = request.get("format", "json")

    if not analysis_data:
        raise HTTPException(status_code=400, detail="analysis_data is required")

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"/tmp/smartsort_export_{timestamp}.{output_format}"
        export_result = export_analysis_results(analysis_data, output_path)

        if export_result["success"]:
            return {"export_path": export_result["path"], "file_size": export_result["formatted_size"], "format": output_format}
        else:
            raise HTTPException(status_code=500, detail=export_result["error"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
