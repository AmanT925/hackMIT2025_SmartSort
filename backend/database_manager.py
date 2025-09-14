# database_manager.py
import sqlite3
import json
import hashlib
import os
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import contextmanager

class EnhancedAnalysisDatabase:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.path.expanduser("~/smartsort_enhanced.db")
        self._init_schema()
    
    def _init_schema(self):
        with self._get_connection() as conn:
            # Analysis session metadata
            conn.execute('''
                CREATE TABLE IF NOT EXISTS analysis_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    directory_path TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    files_processed INTEGER,
                    processing_time REAL,
                    performance_metrics TEXT
                )
            ''')
            # Per-file caching table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS file_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filepath TEXT NOT NULL,
                    filehash TEXT NOT NULL,
                    result TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES analysis_sessions(session_id)
                )
            ''')
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    # ----------- Session Management -----------
    def save_analysis(self, directory_path: str, results: Dict[str, Any]) -> str:
        session_id = f"session_{datetime.now().timestamp()}"
        with self._get_connection() as conn:
            conn.execute('''
                INSERT INTO analysis_sessions 
                (session_id, directory_path, files_processed, processing_time, performance_metrics)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                session_id,
                directory_path,
                results.get('files_processed', 0),
                results.get('processing_time', 0),
                json.dumps(results.get('performance_metrics', {}))
            ))
            conn.commit()
        return session_id

    def get_history(self, limit: int = 20):
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM analysis_sessions ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            ).fetchall()
            return [dict(r) for r in rows]

    def get_session_files(self, session_id: str):
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM file_cache WHERE session_id=? ORDER BY timestamp DESC",
                (session_id,)
            ).fetchall()
            return [dict(r) for r in rows]
    
    # ----------- File Cache Management -----------
    def _file_hash(self, filepath: str) -> str:
        """Generate a hash based on file metadata (mtime + size)."""
        stat = os.stat(filepath)
        h = hashlib.sha256()
        h.update(str(stat.st_mtime).encode())
        h.update(str(stat.st_size).encode())
        return h.hexdigest()
    
    def get_cached_file(self, filepath: str) -> Optional[Dict[str, Any]]:
        filehash = self._file_hash(filepath)
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT result FROM file_cache WHERE filepath=? AND filehash=? ORDER BY timestamp DESC LIMIT 1",
                (filepath, filehash)
            ).fetchone()
            return json.loads(row["result"]) if row else None

    def save_file_result(self, filepath: str, result: Dict[str, Any], session_id: str):
        filehash = self._file_hash(filepath)
        with self._get_connection() as conn:
            conn.execute('''
                INSERT INTO file_cache (filepath, filehash, result, session_id)
                VALUES (?, ?, ?, ?)
            ''', (filepath, filehash, json.dumps(result), session_id))
            conn.commit()

# Singleton instance
enhanced_db = EnhancedAnalysisDatabase()
