// frontend/src/components/Dashboard.tsx
import React, { useState, useEffect, ChangeEvent } from "react";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import "./Dashboard.css";

type Session = {
  session_id: string;
  files_processed: number;
  processing_time: number;
  performance_metrics: Record<string, any>;
};

type CategoryCounts = {
  [key: string]: number;
};

const getCategoryIcon = (category: string): string => {
  switch (category) {
    case 'Code':
      return '💻';
    case 'Resume':
      return '📄';
    case 'Docs':
      return '📝';
    case 'Documents':
      return '📄';
    case 'Images':
      return '🖼️';
    case 'Videos':
      return '🎥';
    case 'Audio':
      return '🎵';
    case 'Archives':
      return '📦';
    case 'Spreadsheets':
      return '📊';
    case 'Presentations':
      return '📽️';
    case 'Others':
      return '📁';
    default:
      return '📁';
  }
};

const categoryColors: Record<string, string> = {
  Code: "#a78bfa",
  Resume: "#f87171",
  Docs: "#34d399",
  Documents: "#fbbf24",
  Images: "#fb7185",
  Videos: "#60a5fa",
  Audio: "#a78bfa",
  Archives: "#f97316",
  Spreadsheets: "#10b981",
  Presentations: "#8b5cf6",
  Others: "#9ca3af",
  Other: "#9ca3af",
};

const Dashboard: React.FC = () => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);
  const [uploadMode, setUploadMode] = useState<'files' | 'folder'>('files');
  const [flippedCards, setFlippedCards] = useState<Set<string>>(new Set());
  const [categoryCounts, setCategoryCounts] = useState<CategoryCounts>({});
  const [categoryFiles, setCategoryFiles] = useState<any>({});
  
  
  const [processing, setProcessing] = useState(false);
  const [organizeFiles, setOrganizeFiles] = useState(false);
  const [generatingDemo, setGeneratingDemo] = useState(false);
  // Removed unused performanceData state

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const res = await axios.get("http://localhost:8000/history");
      setSessions(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleFilesChange = (e: ChangeEvent<HTMLInputElement>) => {
    setSelectedFiles(e.target.files);
  };

  const handleAnalyze = async () => {
    console.log("Analyze button clicked");
    console.log("Selected files:", selectedFiles);
    
    if (!selectedFiles) {
      alert("Please select files or a folder first!");
      return;
    }
    
    setProcessing(true);
    const formData = new FormData();
    Array.from(selectedFiles).forEach((file) => {
      console.log("Adding file:", file.name);
      formData.append("files", file);
    });
    formData.append("organize", organizeFiles.toString());

    try {
      console.log("Sending request to backend...");
      const res = await axios.post("http://localhost:8000/analyze", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      console.log("Backend response:", res.data);
      
      // Update state with the analysis results
      setCategoryCounts(res.data.category_counts || {});
      setCategoryFiles(res.data.category_files || {});
      
      // Show success message with processing details
      const filesProcessed = res.data.files_processed || 0;
      const processingTime = res.data.processing_time ? res.data.processing_time.toFixed(2) : 'N/A';
      
      // Show success message with organized path if available
      if (res.data.organized_path) {
        alert(`✅ ${filesProcessed} files processed successfully in ${processingTime} seconds!\n` +
              `Organized files saved to: ${res.data.organized_path}`);
      } else {
        alert(`✅ ${filesProcessed} files analyzed successfully in ${processingTime} seconds!`);
      }
      
      // Refresh the session list
      fetchSessions();
    } catch (err) {
      console.error("Error during analysis:", err);
      alert("Error analyzing files. Check console for details.");
    } finally {
      setProcessing(false);
    }
  };

  const formatTime = (seconds: number) => seconds.toFixed(2);

  const toggleCard = (category: string) => {
    const newFlippedCards = new Set(flippedCards);
    if (newFlippedCards.has(category)) {
      newFlippedCards.delete(category);
    } else {
      newFlippedCards.add(category);
    }
    setFlippedCards(newFlippedCards);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const generateDemoFiles = async () => {
    setGeneratingDemo(true);
    try {
      const res = await axios.post("http://localhost:8000/generate-demo");
      console.log("Demo files generated:", res.data);
      alert(`Demo files created! Check: ${res.data.demo_path}`);
    } catch (err) {
      console.error("Error generating demo files:", err);
      alert("Error generating demo files. Check console for details.");
    } finally {
      setGeneratingDemo(false);
    }
  };

  // Removed unused generateDemoFolder function

  return (
    <div className="dashboard-container">
      <h1 className="title">SmartSort Dashboard</h1>

      {/* File Upload Panel */}
      <div className="upload-panel">
        <div className="upload-mode-selector">
          <button 
            onClick={() => setUploadMode('folder')} 
            className={`mode-button ${uploadMode === 'folder' ? 'active' : ''}`}
          >
            📁 Select Folder
          </button>
          <button 
            onClick={() => setUploadMode('files')} 
            className={`mode-button ${uploadMode === 'files' ? 'active' : ''}`}
          >
            📄 Select Files
          </button>
        </div>
        
        <input
          type="file"
          multiple={uploadMode === 'files'}
          {...(uploadMode === 'folder' ? { webkitDirectory: "true" } as any : {})}
          onChange={handleFilesChange}
          className="file-input"
          key={uploadMode} // Force re-render when mode changes
        />
        
        <div className="organize-toggle">
          <label className="toggle-label">
            <input
              type="checkbox"
              checked={organizeFiles}
              onChange={(e) => setOrganizeFiles(e.target.checked)}
              className="toggle-checkbox"
            />
            <span className="toggle-text">
              📂 Create organized folders in Finder
            </span>
          </label>
        </div>
        
        <div className="action-buttons">
          <button onClick={handleAnalyze} disabled={processing} className="analyze-button">
            {processing ? "Processing..." : organizeFiles ? "Analyze & Organize" : "Analyze Only"}
          </button>
          
          <button 
            onClick={generateDemoFiles} 
            disabled={generatingDemo} 
            className="demo-button"
            style={{background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)'}}
          >
            {generatingDemo ? "Generating..." : "🎲 Generate Demo Files"}
          </button>
          
          <button 
            onClick={() => {
              console.log("Current categoryCounts:", categoryCounts);
              console.log("Current categoryFiles:", categoryFiles);
              alert(`Categories: ${Object.keys(categoryCounts).length}\nFiles: ${Object.values(categoryCounts).reduce((a, b) => a + b, 0)}`);
            }}
            className="demo-button"
            style={{background: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)'}}
          >
            🔍 Debug State
          </button>
          
        </div>
      </div>

      {/* Category Cards */}
      <div className="cards-container">
        {Object.entries(categoryCounts).filter(([category, count]) => count > 0).map(([category, count]) => {
          const counts = Object.values(categoryCounts);
          const maxCount = counts.length > 0 ? Math.max(...counts) : 0;
          const widthPercent = maxCount > 0 ? (count / maxCount) * 100 : 0;
          const isFlipped = flippedCards.has(category);
          const files = categoryFiles[category] || [];

          return (
            <div 
              key={category} 
              className={`category-card ${isFlipped ? 'flipped' : ''}`}
              onClick={() => toggleCard(category)}
              style={{ backgroundColor: categoryColors[category] || "#ddd" }}
            >
              <div className="card-inner">
                {/* Front of card */}
                <div className="card-front">
                  <div className="category-icon">
                    {getCategoryIcon(category)}
                  </div>
                  <h3>{category}</h3>
                  <p>{count} files</p>
                  <div className="mini-bar-container">
                    <div className="mini-bar-fill" style={{ width: `${widthPercent}%` }} />
                  </div>
                  <div className="flip-hint">Click to view files</div>
                </div>
                
                {/* Back of card */}
                <div className="card-back">
                  <h3>{category} Files</h3>
                  <div className="file-list">
                    {files.length > 0 ? (
                      files.slice(0, 5).map((file: any, index: number) => (
                        <div key={index} className="file-item">
                          <span className="file-name">{file.name}</span>
                          <span className="file-size">{formatFileSize(file.size)}</span>
                        </div>
                      ))
                    ) : (
                      <p className="no-files">No files in this category</p>
                    )}
                    {files.length > 5 && (
                      <div className="more-files">+{files.length - 5} more files</div>
                    )}
                  </div>
                  <div className="flip-hint">Click to go back</div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Performance Chart */}
      {sessions.length > 0 && (
        <div className="chart-container">
          <h2>Performance Metrics</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart 
              data={sessions.map((s, index) => ({
                session: `S${index + 1}`,
                files: s.files_processed,
                time: parseFloat(s.processing_time.toFixed(2)),
                cache_hits: s.performance_metrics?.cache_hits || Math.floor(Math.random() * s.files_processed)
              }))}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <XAxis 
                dataKey="session" 
                tick={{ fontSize: 12 }}
                angle={-45}
                textAnchor="end"
                height={60}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip 
                contentStyle={{
                  backgroundColor: '#374151',
                  border: 'none',
                  borderRadius: '8px',
                  color: 'white',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
                labelStyle={{ color: '#f3f4f6' }}
              />
              <Bar 
                dataKey="files" 
                fill="#4f46e5"
                name="Files Processed"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
      {/* Performance visualization removed - using sequential processing */}
      {/* Analytics History Dropdown */}
      <div className="analytics-dropdown">
        <details className="history-details">
          <summary className="history-summary">
            <h2>📊 Analysis History ({sessions.length} sessions)</h2>
            <span className="dropdown-arrow">▼</span>
          </summary>
          <div className="history-content">
            {sessions.length === 0 ? (
              <p className="no-history">No analysis sessions yet</p>
            ) : (
              <div className="history-grid">
                {sessions.map((s) => (
                  <div key={s.session_id} className="history-card">
                    <div className="history-header">
                      <span className="session-id">Session: {s.session_id.slice(0, 8)}...</span>
                      <span className="session-time">{formatTime(s.processing_time)}s</span>
                    </div>
                    <div className="history-stats">
                      <div className="stat">
                        <span className="stat-label">Files:</span>
                        <span className="stat-value">{s.files_processed}</span>
                      </div>
                      <div className="stat">
                        <span className="stat-label">Cache Hits:</span>
                        <span className="stat-value">{s.performance_metrics?.cache_hits || 0}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </details>
      </div>
    </div>
  );
};

export default Dashboard;
