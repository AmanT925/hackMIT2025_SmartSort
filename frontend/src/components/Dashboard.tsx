// frontend/src/components/Dashboard.tsx
import React, { useState, useEffect, ChangeEvent } from "react";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import "./Dashboard.css"; // we’ll add some custom CSS for nice UI

type Session = {
  session_id: string;
  files_processed: number;
  processing_time: number;
  performance_metrics: Record<string, any>;
};

type CategoryCounts = {
  [key: string]: number;
};

const Dashboard: React.FC = () => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);
  const [categoryCounts, setCategoryCounts] = useState<CategoryCounts>({});
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const res = await axios.get("/history");
      setSessions(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleFilesChange = (e: ChangeEvent<HTMLInputElement>) => {
    setSelectedFiles(e.target.files);
  };

  const handleAnalyze = async () => {
    if (!selectedFiles) return;
    setProcessing(true);
    const formData = new FormData();
    Array.from(selectedFiles).forEach((file) => formData.append("files", file));

    try {
      const res = await axios.post("/analyze", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setCategoryCounts(res.data.category_counts);
      fetchSessions();
    } catch (err) {
      console.error(err);
    } finally {
      setProcessing(false);
    }
  };

  const formatTime = (seconds: number) => seconds.toFixed(2);

  return (
    <div className="dashboard-container">
      <h1 className="title">SmartSort Dashboard</h1>

      {/* Drag & Drop / File Upload */}
      <div className="upload-panel">
        <input
          type="file"
          multiple
          webkitdirectory="true"
          onChange={handleFilesChange}
          className="file-input"
        />
        <button onClick={handleAnalyze} disabled={processing} className="analyze-button">
          {processing ? "Organizing..." : "Analyze & Organize"}
        </button>
      </div>

      {/* Category Cards */}
      <div className="cards-container">
        {Object.entries(categoryCounts).map(([category, count]) => (
          <div key={category} className="category-card">
            <h3>{category}</h3>
            <p>{count} files</p>
          </div>
        ))}
      </div>

      {/* Performance Chart */}
      {sessions.length > 0 && (
        <div className="chart-container">
          <h2>Performance Metrics (Cache Hits)</h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={sessions}>
              <XAxis dataKey="session_id" hide />
              <YAxis />
              <Tooltip />
              <Bar dataKey="performance_metrics.cache_hits" fill="#4f46e5" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Analytics Table */}
      <div className="analytics-table">
        <h2>Analysis History</h2>
        <table>
          <thead>
            <tr>
              <th>Session ID</th>
              <th>Files Processed</th>
              <th>Time (sec)</th>
              <th>Metrics</th>
            </tr>
          </thead>
          <tbody>
            {sessions.map((s) => (
              <tr key={s.session_id}>
                <td>{s.session_id}</td>
                <td>{s.files_processed}</td>
                <td>{formatTime(s.processing_time)}</td>
                <td>{JSON.stringify(s.performance_metrics)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Dashboard;
