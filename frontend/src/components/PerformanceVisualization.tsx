// frontend/src/components/PerformanceVisualization.tsx
import React from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from "recharts";

interface PerformanceData {
  performance_analysis?: {
    parallel_time: number;
    estimated_serial_time: number;
    speedup: number;
    efficiency: number;
    throughput: number;
    worker_times: Record<string, number>;
    bottleneck_analysis: {
      slowest_worker: number;
      fastest_worker: number;
      load_balance_ratio: number;
    };
  };
  workers_used?: number;
  files_processed?: number;
  processing_method?: string;
}

interface Props {
  data: PerformanceData;
}

const PerformanceVisualization: React.FC<Props> = ({ data }) => {
  if (!data.performance_analysis) {
    return null;
  }

  const perf = data.performance_analysis;
  
  // Speedup comparison data
  const speedupData = [
    { method: 'Serial', time: perf.estimated_serial_time, speedup: 1 },
    { method: 'Parallel', time: perf.parallel_time, speedup: perf.speedup }
  ];

  // Worker performance data
  const workerTimes = Object.values(perf.worker_times);
  const fastestWorkerTime = Math.min(...workerTimes);
  const workerData = Object.entries(perf.worker_times).map(([worker, time]) => ({
    worker: `Worker ${parseInt(worker) + 1}`,
    time: parseFloat(time.toFixed(3)),
    efficiency: ((fastestWorkerTime / time) * 100).toFixed(1)
  }));

  // Efficiency metrics
  const efficiencyData = [
    { name: 'Parallel Efficiency', value: perf.efficiency, color: '#10b981' },
    { name: 'Overhead', value: 100 - perf.efficiency, color: '#ef4444' }
  ];

  // Theoretical vs Actual speedup
  const theoreticalSpeedup = data.workers_used || 1;
  const scalabilityData = Array.from({ length: theoreticalSpeedup }, (_, i) => {
    const workers = i + 1;
    const theoretical = workers;
    const actual = workers === data.workers_used ? perf.speedup : (perf.speedup * workers) / (data.workers_used || 1);
    return {
      workers,
      theoretical,
      actual: Math.min(actual, theoretical * 0.9) // Account for overhead
    };
  });

  return (
    <div className="performance-visualization">
      <div className="performance-header">
        <h2>🚀 Parallel Computing Performance Analysis</h2>
        <div className="key-metrics">
          <div className="metric-card">
            <div className="metric-value">{perf.speedup}x</div>
            <div className="metric-label">Speedup</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{perf.efficiency}%</div>
            <div className="metric-label">Efficiency</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{perf.throughput}</div>
            <div className="metric-label">Files/sec</div>
          </div>
          <div className="metric-card">
            <div className="metric-value">{data.workers_used}</div>
            <div className="metric-label">Workers</div>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        {/* Speedup Comparison */}
        <div className="chart-section">
          <h3>⚡ Serial vs Parallel Performance</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={speedupData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="method" />
              <YAxis />
              <Tooltip 
                formatter={(value, name) => [
                  name === 'time' ? `${value}s` : `${value}x`,
                  name === 'time' ? 'Processing Time' : 'Speedup Factor'
                ]}
              />
              <Bar dataKey="time" fill="#4f46e5" name="time" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Worker Load Distribution */}
        <div className="chart-section">
          <h3>👥 Worker Load Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={workerData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="worker" />
              <YAxis />
              <Tooltip formatter={(value, name) => [
                name === 'time' ? `${value}s` : `${value}%`,
                name === 'time' ? 'Processing Time' : 'Efficiency'
              ]} />
              <Bar dataKey="time" fill="#10b981" name="time" />
            </BarChart>
          </ResponsiveContainer>
          <div className="load-balance-info">
            Load Balance Ratio: {Math.round(perf.bottleneck_analysis.load_balance_ratio * 100)}%
          </div>
        </div>

        {/* Efficiency Breakdown */}
        <div className="chart-section">
          <h3>📊 Parallel Efficiency</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={efficiencyData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}%`}
              >
                {efficiencyData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Scalability Analysis */}
        <div className="chart-section">
          <h3>📈 Scalability Analysis (Amdahl's Law)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={scalabilityData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="workers" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="theoretical" 
                stroke="#ef4444" 
                strokeDasharray="5 5"
                name="Theoretical Speedup"
              />
              <Line 
                type="monotone" 
                dataKey="actual" 
                stroke="#10b981" 
                strokeWidth={3}
                name="Actual Speedup"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Technical Analysis */}
      <div className="technical-analysis">
        <h3>🔬 Technical Analysis</h3>
        <div className="analysis-grid">
          <div className="analysis-card">
            <h4>Computational Strategy</h4>
            <p>
              <strong>Parallelization Approach:</strong> Data parallelism with process-based workers<br/>
              <strong>Load Balancing:</strong> Static chunk distribution across {data.workers_used} workers<br/>
              <strong>Communication Overhead:</strong> {(100 - perf.efficiency).toFixed(1)}% of total time
            </p>
          </div>
          
          <div className="analysis-card">
            <h4>Bottleneck Analysis</h4>
            <p>
              <strong>Slowest Worker:</strong> {perf.bottleneck_analysis.slowest_worker.toFixed(3)}s<br/>
              <strong>Fastest Worker:</strong> {perf.bottleneck_analysis.fastest_worker.toFixed(3)}s<br/>
              <strong>Load Imbalance:</strong> {((1 - perf.bottleneck_analysis.load_balance_ratio) * 100).toFixed(1)}%
            </p>
          </div>

          <div className="analysis-card">
            <h4>Performance Insights</h4>
            <p>
              {perf.efficiency > 80 && "✅ Excellent parallel efficiency - minimal overhead"}
              {perf.efficiency > 60 && perf.efficiency <= 80 && "⚠️ Good efficiency - some optimization possible"}
              {perf.efficiency <= 60 && "🔴 Low efficiency - significant overhead detected"}
              <br/>
              <strong>Recommended:</strong> {
                perf.bottleneck_analysis.load_balance_ratio < 0.8 
                  ? "Improve load balancing with dynamic work stealing"
                  : "Current load distribution is well-balanced"
              }
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceVisualization;
