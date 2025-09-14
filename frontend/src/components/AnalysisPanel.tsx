import React, { useState, useEffect, ChangeEvent } from "react";
import axios from "axios";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

type Session = {
  session_id: string;
  files_processed: number;
  processing_time: number;
  performance_metrics: string;
  category_counts?: Record<string, number>;
};

const AnalysisPanel: React.FC = () => {
  const [folderPath, setFolderPath] = useState("");
  const [sessions, setSessions] = useState<Session[]>([]);
  const [latestResult, setLatestResult] = useState<Session | null>(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await axios.get("http://127.0.0.1:8000/history");
      setSessions(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleAnalyze = async () => {
    if (!folderPath) return alert("Please enter a folder path");
    try {
      const formData = new FormData();
      formData.append("folder_path", folderPath);
      const res = await axios.post("http://127.0.0.1:8000/analyze", formData);
      setLatestResult(res.data);
      fetchHistory();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Folder Input */}
      <div className="bg-white p-6 rounded shadow space-y-4">
        <h2 className="text-xl font-semibold">Organize Your Folder</h2>
        <input
          type="text"
          placeholder="Enter folder path"
          value={folderPath}
          onChange={(e) => setFolderPath(e.target.value)}
          className="border p-2 rounded w-full"
        />
        <button
          onClick={handleAnalyze}
          className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700"
        >
          Analyze & Organize
        </button>
      </div>

      {/* Latest Result */}
      {latestResult && (
        <div className="bg-white p-6 rounded shadow space-y-4">
          <h2 className="text-xl font-semibold">Latest Analysis</h2>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-green-100 p-4 rounded shadow">
              <h3 className="font-bold">Files Processed</h3>
              <p className="text-2xl">{latestResult.files_processed}</p>
            </div>
            <div className="bg-blue-100 p-4 rounded shadow">
              <h3 className="font-bold">Processing Time</h3>
              <p className="text-2xl">{latestResult.processing_time} sec</p>
            </div>
          </div>
          <div className="mt-4">
            <h3 className="font-bold mb-2">Category Distribution</h3>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart
                data={latestResult.category_counts
                  ? Object.entries(latestResult.category_counts).map(([name, value]) => ({ name, value }))
                  : []}
              >
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#4F46E5" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* History Table */}
      <div className="bg-white p-6 rounded shadow">
        <h2 className="text-xl font-semibold mb-4">Analysis History</h2>
        <table className="table-auto w-full border-collapse border">
          <thead>
            <tr className="bg-gray-200">
              <th className="border p-2">Session ID</th>
              <th className="border p-2">Files Processed</th>
              <th className="border p-2">Processing Time</th>
              <th className="border p-2">Performance Metrics</th>
            </tr>
          </thead>
          <tbody>
            {sessions.map((s) => (
              <tr key={s.session_id}>
                <td className="border p-2">{s.session_id}</td>
                <td className="border p-2">{s.files_processed}</td>
                <td className="border p-2">{s.processing_time.toFixed(2)} sec</td>
                <td className="border p-2">{s.performance_metrics}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AnalysisPanel;
