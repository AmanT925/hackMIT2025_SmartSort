# backend/performance_benchmarker.py
import time
import psutil
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple
import json
from concurrent.futures import ProcessPoolExecutor
import threading
from dataclasses import dataclass

@dataclass
class BenchmarkResult:
    method: str
    file_count: int
    processing_time: float
    memory_usage: float
    cpu_utilization: float
    throughput: float  # files per second

class PerformanceBenchmarker:
    """
    Benchmarking system to demonstrate parallel computing advantages
    """
    
    def __init__(self):
        self.results = []
        self.monitoring_active = False
        self.system_metrics = {
            'cpu_usage': [],
            'memory_usage': [],
            'timestamps': []
        }
    
    def benchmark_serial_vs_parallel(self, file_paths: List[str]) -> Dict[str, BenchmarkResult]:
        """Compare serial vs parallel processing performance"""
        results = {}
        
        # Test different worker counts
        worker_counts = [1, 2, 4, 8, min(16, psutil.cpu_count())]
        
        for workers in worker_counts:
            method_name = f"parallel_{workers}_workers" if workers > 1 else "serial"
            
            print(f"Benchmarking {method_name}...")
            
            # Start system monitoring
            self._start_monitoring()
            
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            # Run the processing
            if workers == 1:
                self._process_files_serial(file_paths)
            else:
                self._process_files_parallel(file_paths, workers)
            
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            # Stop monitoring
            self._stop_monitoring()
            
            processing_time = end_time - start_time
            memory_usage = end_memory - start_memory
            avg_cpu = np.mean(self.system_metrics['cpu_usage'][-10:]) if self.system_metrics['cpu_usage'] else 0
            
            results[method_name] = BenchmarkResult(
                method=method_name,
                file_count=len(file_paths),
                processing_time=processing_time,
                memory_usage=memory_usage,
                cpu_utilization=avg_cpu,
                throughput=len(file_paths) / processing_time if processing_time > 0 else 0
            )
            
            # Clear metrics for next test
            self.system_metrics = {'cpu_usage': [], 'memory_usage': [], 'timestamps': []}
            
            # Brief pause between tests
            time.sleep(2)
        
        return results
    
    def _process_files_serial(self, file_paths: List[str]):
        """Serial file processing for baseline comparison"""
        from .parallel_file_analyzer import analyze_file_batch
        analyze_file_batch(file_paths, 0)
    
    def _process_files_parallel(self, file_paths: List[str], workers: int):
        """Parallel file processing"""
        from .parallel_file_analyzer import analyze_file_batch
        
        chunk_size = max(1, len(file_paths) // workers)
        chunks = [file_paths[i:i + chunk_size] for i in range(0, len(file_paths), chunk_size)]
        
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(analyze_file_batch, chunk, i) for i, chunk in enumerate(chunks)]
            for future in futures:
                future.result()
    
    def _start_monitoring(self):
        """Start system resource monitoring"""
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_resources)
        self.monitor_thread.start()
    
    def _stop_monitoring(self):
        """Stop system resource monitoring"""
        self.monitoring_active = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join()
    
    def _monitor_resources(self):
        """Monitor CPU and memory usage"""
        while self.monitoring_active:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent
            timestamp = time.time()
            
            self.system_metrics['cpu_usage'].append(cpu_percent)
            self.system_metrics['memory_usage'].append(memory_percent)
            self.system_metrics['timestamps'].append(timestamp)
            
            time.sleep(0.5)
    
    def generate_performance_report(self, results: Dict[str, BenchmarkResult]) -> Dict[str, any]:
        """Generate comprehensive performance analysis"""
        
        # Calculate speedup metrics
        serial_time = results.get('serial', results[list(results.keys())[0]]).processing_time
        
        speedup_data = []
        efficiency_data = []
        
        for method, result in results.items():
            if 'parallel' in method:
                workers = int(method.split('_')[1])
                speedup = serial_time / result.processing_time if result.processing_time > 0 else 0
                efficiency = (speedup / workers) * 100
                
                speedup_data.append({
                    'workers': workers,
                    'speedup': speedup,
                    'efficiency': efficiency,
                    'throughput': result.throughput
                })
        
        # Amdahl's Law analysis
        amdahl_analysis = self._calculate_amdahl_law(speedup_data)
        
        return {
            'benchmark_results': {k: {
                'method': v.method,
                'processing_time': v.processing_time,
                'throughput': v.throughput,
                'memory_usage': v.memory_usage,
                'cpu_utilization': v.cpu_utilization
            } for k, v in results.items()},
            'speedup_analysis': speedup_data,
            'amdahl_analysis': amdahl_analysis,
            'recommendations': self._generate_recommendations(results, speedup_data)
        }
    
    def _calculate_amdahl_law(self, speedup_data: List[Dict]) -> Dict:
        """Calculate theoretical vs actual speedup using Amdahl's Law"""
        if not speedup_data:
            return {}
        
        # Estimate parallel fraction from actual data
        max_speedup = max(item['speedup'] for item in speedup_data)
        estimated_parallel_fraction = 1 - (1 / max_speedup) if max_speedup > 1 else 0.9
        
        theoretical_speedups = []
        for item in speedup_data:
            workers = item['workers']
            theoretical = 1 / ((1 - estimated_parallel_fraction) + (estimated_parallel_fraction / workers))
            theoretical_speedups.append({
                'workers': workers,
                'theoretical_speedup': theoretical,
                'actual_speedup': item['speedup'],
                'efficiency_loss': ((theoretical - item['speedup']) / theoretical) * 100 if theoretical > 0 else 0
            })
        
        return {
            'estimated_parallel_fraction': estimated_parallel_fraction,
            'theoretical_vs_actual': theoretical_speedups
        }
    
    def _generate_recommendations(self, results: Dict[str, BenchmarkResult], speedup_data: List[Dict]) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        if speedup_data:
            best_efficiency = max(speedup_data, key=lambda x: x['efficiency'])
            best_throughput = max(speedup_data, key=lambda x: x['throughput'])
            
            recommendations.append(f"Optimal worker count for efficiency: {best_efficiency['workers']} workers ({best_efficiency['efficiency']:.1f}% efficiency)")
            recommendations.append(f"Optimal worker count for throughput: {best_throughput['workers']} workers ({best_throughput['throughput']:.1f} files/sec)")
            
            # Check for diminishing returns
            sorted_data = sorted(speedup_data, key=lambda x: x['workers'])
            for i in range(1, len(sorted_data)):
                current = sorted_data[i]
                previous = sorted_data[i-1]
                
                if current['efficiency'] < previous['efficiency'] * 0.8:  # 20% efficiency drop
                    recommendations.append(f"Diminishing returns observed beyond {previous['workers']} workers")
                    break
        
        return recommendations

def create_performance_visualizations(benchmark_data: Dict) -> Dict[str, str]:
    """Create performance visualization charts"""
    
    # Speedup vs Workers chart
    speedup_data = benchmark_data.get('speedup_analysis', [])
    if speedup_data:
        workers = [item['workers'] for item in speedup_data]
        actual_speedup = [item['speedup'] for item in speedup_data]
        theoretical_speedup = [item['theoretical_speedup'] for item in benchmark_data.get('amdahl_analysis', {}).get('theoretical_vs_actual', [])]
        
        plt.figure(figsize=(12, 8))
        
        # Subplot 1: Speedup comparison
        plt.subplot(2, 2, 1)
        plt.plot(workers, actual_speedup, 'bo-', label='Actual Speedup', linewidth=2, markersize=8)
        if theoretical_speedup:
            plt.plot(workers, theoretical_speedup, 'r--', label='Theoretical (Amdahl\'s Law)', linewidth=2)
        plt.plot(workers, workers, 'g:', label='Linear Speedup', alpha=0.7)
        plt.xlabel('Number of Workers')
        plt.ylabel('Speedup Factor')
        plt.title('Parallel Speedup Analysis')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Subplot 2: Efficiency
        plt.subplot(2, 2, 2)
        efficiency = [item['efficiency'] for item in speedup_data]
        plt.plot(workers, efficiency, 'go-', linewidth=2, markersize=8)
        plt.xlabel('Number of Workers')
        plt.ylabel('Parallel Efficiency (%)')
        plt.title('Parallel Efficiency')
        plt.grid(True, alpha=0.3)
        
        # Subplot 3: Throughput
        plt.subplot(2, 2, 3)
        throughput = [item['throughput'] for item in speedup_data]
        plt.bar(workers, throughput, color='skyblue', alpha=0.7)
        plt.xlabel('Number of Workers')
        plt.ylabel('Files per Second')
        plt.title('Processing Throughput')
        plt.grid(True, alpha=0.3)
        
        # Subplot 4: Processing Time Comparison
        plt.subplot(2, 2, 4)
        benchmark_results = benchmark_data.get('benchmark_results', {})
        methods = list(benchmark_results.keys())
        times = [benchmark_results[method]['processing_time'] for method in methods]
        
        colors = ['red' if 'serial' in method else 'blue' for method in methods]
        plt.bar(range(len(methods)), times, color=colors, alpha=0.7)
        plt.xlabel('Processing Method')
        plt.ylabel('Processing Time (seconds)')
        plt.title('Processing Time Comparison')
        plt.xticks(range(len(methods)), [m.replace('_', ' ').title() for m in methods], rotation=45)
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save the plot
        chart_path = '/tmp/performance_analysis.png'
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return {'performance_chart': chart_path}
    
    return {}
