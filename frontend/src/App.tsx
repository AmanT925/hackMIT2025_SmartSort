import React, { useState, useRef, useCallback } from 'react';
import { Upload, Mic, MicOff, BarChart3, FolderOpen, Zap, Brain, MessageCircle, FileText, Image, Music, Video, Archive, Code } from 'lucide-react';
import './App.css';

// Mock data for demo
const performanceMetrics = [
  { metric: 'Files Processed', value: '247', color: '#3b82f6' },
  { metric: 'Processing Speed', value: '4x faster', color: '#10b981' },
  { metric: 'Duplicates Found', value: '23', color: '#f59e0b' },
  { metric: 'Categories Created', value: '8', color: '#8b5cf6' },
  { metric: 'Time Elapsed', value: '2.3s', color: '#ef4444' }
];

const categoryData = [
  { name: 'Documents', count: 89, color: '#3b82f6', icon: FileText },
  { name: 'Images', count: 76, color: '#10b981', icon: Image },
  { name: 'Audio', count: 34, color: '#f59e0b', icon: Music },
  { name: 'Videos', count: 28, color: '#ef4444', icon: Video },
  { name: 'Archives', count: 12, color: '#8b5cf6', icon: Archive },
  { name: 'Code', count: 8, color: '#06b6d4', icon: Code }
];

const SmartSortApp = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [voiceText, setVoiceText] = useState('');
  const [analysisResults, setAnalysisResults] = useState<any>(null);
  const [roastMode, setRoastMode] = useState(false);
  const [roastText, setRoastText] = useState('');
  const [loadingMessage, setLoadingMessage] = useState('');
  const [showMetricsModal, setShowMetricsModal] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const voiceCommands = [
    "Sort this folder",
    "Tell me what you found",
    "Roast my organization",
    "Find duplicates",
    "Show me file stats"
  ];

  // Drag and drop handlers
  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    setSelectedFiles(files);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setSelectedFiles(files);
  };

  // Humorous loading messages
  const loadingMessages = [
    "Damn, you're really messy huh? 🤦‍♂️",
    "You should be on Hoarders 📺",
    "Did a tornado hit your computer? 🌪️",
    "This is worse than my teenager's room 😱",
    "I've seen cleaner dumpsters 🗑️",
    "Your files are having an identity crisis 🤔",
    "Even chaos theory can't explain this mess 🧠",
    "I need therapy after seeing this 💭",
    "Are you collecting digital dust bunnies? 🐰",
    "This folder structure defies physics 🚀",
    "I'm calling Marie Kondo 📞",
    "Your organization skills need CPR 🚑"
  ];

  // File analysis simulation
  const handleFileAnalysis = async (files: File[]) => {
    setIsAnalyzing(true);
    setProgress(0);
    setLoadingMessage(loadingMessages[Math.floor(Math.random() * loadingMessages.length)]);
    
    // Auto-scroll to progress bar after a short delay
    setTimeout(() => {
      const progressElement = document.getElementById('progress-section');
      if (progressElement) {
        progressElement.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'center' 
        });
      }
    }, 300);
    
    // Change loading message every 2 seconds
    const messageInterval = setInterval(() => {
      setLoadingMessage(loadingMessages[Math.floor(Math.random() * loadingMessages.length)]);
    }, 2000);
    
    // Simulate progress
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          clearInterval(messageInterval);
          setIsAnalyzing(false);
          setLoadingMessage('');
          setAnalysisResults({
            totalFiles: files.length,
            categories: categoryData,
            performance: performanceMetrics
          });
          return 100;
        }
        return prev + Math.random() * 15;
      });
    }, 200);

    // Mock API call
    try {
      const formData = new FormData();
      files.forEach((file: File) => formData.append('files', file));
      // await fetch('http://localhost:8000/analyze', { method: 'POST', body: formData });
    } catch (error) {
      console.log('Demo mode - API call simulated');
    }
  };

  // Push-to-talk handlers
  const handleMouseDown = () => {
    setIsRecording(true);
    setVoiceText("Listening...");
  };

  const handleMouseUp = () => {
    if (isRecording) {
      setIsRecording(false);
      // Simulate voice recognition result
      setTimeout(() => {
        setVoiceText("Sort this folder and tell me what you found");
      }, 500);
    }
  };

  const handleVoiceCommand = async (command: string) => {
    try {
      if (command.includes('roast')) {
        setRoastMode(true);
        setRoastText("Wow, your files are more scattered than my thoughts on a Monday morning! 📁💀 You've got 23 duplicates just chilling like they're at a family reunion, and your naming convention looks like it was created by a caffeinated squirrel. But hey, at least you're consistent... consistently chaotic! 😅");
      } else {
        setVoiceText(`Processing: "${command}"`);
        // await fetch('http://localhost:8000/voice-command', {
        //   method: 'POST',
        //   headers: { 'Content-Type': 'application/json' },
        //   body: JSON.stringify({ text: command })
        // });
      }
    } catch (error) {
      console.log('Demo mode - voice command simulated');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
      {/* Header */}
      <div className="container mx-auto px-6 py-8">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold mb-4">
            SmartSort AI
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Intelligent file organization with parallel processing, voice commands, and AI-powered insights
          </p>
        </div>

        {/* Main Upload Area */}
        <div className="mb-12">
          <div
            className={`relative border-2 border-dashed rounded-3xl p-12 text-center transition-all duration-300 ${
              isDragging 
                ? 'border-blue-400 bg-blue-400/10 scale-105' 
                : 'border-gray-600 hover:border-gray-500'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              {...({ webkitdirectory: "" } as any)}
              onChange={handleFileSelect}
              className="hidden"
              aria-label="Select folder for file organization"
            />
            
            <Upload className="mx-auto mb-6 text-blue-400" size={80} />
            <h3 className="text-2xl font-bold mb-4">Drop your messy folder here</h3>
            <p className="text-gray-400 mb-6">Or click to select a folder for AI-powered organization</p>
            {selectedFiles.length > 0 && (
              <p className="text-green-400 mb-4">✅ {selectedFiles.length} file(s) selected - Click a button below to proceed</p>
            )}
            
            <button
              onClick={() => fileInputRef.current?.click()}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 px-8 py-4 rounded-xl font-semibold transition-all duration-300 transform hover:scale-105"
            >
              Choose Folder
            </button>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="mb-8">
          <div className="flex flex-wrap justify-center gap-3">
            <button
              onClick={() => {
                // Trigger file analysis with selected files
                if (selectedFiles.length > 0) {
                  handleFileAnalysis(selectedFiles);
                } else {
                  alert('Please select or drop files first!');
                }
              }}
              className="bg-gradient-to-r from-purple-800 to-purple-900 hover:from-purple-900 hover:to-purple-950 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 transform hover:scale-105 flex items-center gap-2"
            >
              🔍 Analyze & Organize
            </button>
            
            <button
              onClick={() => {
                // Generate demo files simulation
                handleFileAnalysis(Array(25).fill(null).map((_, i) => new File([''], `demo_file_${i}.txt`)));
              }}
              className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 transform hover:scale-105 flex items-center gap-2"
            >
              📁 Generate Demo
            </button>
            
            <button
              onClick={() => {
                // Medium demo simulation
                handleFileAnalysis(Array(75).fill(null).map((_, i) => new File([''], `medium_demo_${i}.txt`)));
              }}
              className="bg-gradient-to-r from-yellow-600 to-amber-600 hover:from-yellow-700 hover:to-amber-700 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 transform hover:scale-105 flex items-center gap-2"
            >
              📊 Medium Demo
            </button>
            
            <button
              onClick={() => {
                // XL demo simulation
                handleFileAnalysis(Array(150).fill(null).map((_, i) => new File([''], `xl_demo_${i}.txt`)));
              }}
              className="bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-700 hover:to-indigo-800 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 transform hover:scale-105 flex items-center gap-2"
            >
              🚀 XL Demo
            </button>
            
            <button
              onClick={() => {
                // Debug state - show current state in console
                console.log('Debug State:', {
                  isDragging,
                  isAnalyzing,
                  progress,
                  isRecording,
                  voiceText,
                  analysisResults,
                  roastMode,
                  loadingMessage,
                  showMetricsModal
                });
                alert('Debug state logged to console (F12)');
              }}
              className="bg-gradient-to-r from-slate-600 to-slate-700 hover:from-slate-700 hover:to-slate-800 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 transform hover:scale-105 flex items-center gap-2"
            >
              🐛 Debug
            </button>
          </div>
        </div>

        {/* Voice Interface */}
        <div className="mb-12">
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-8">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold flex items-center gap-3">
                <MessageCircle className="text-purple-400" />
                Voice Commands
              </h3>
              
              <button
                onMouseDown={handleMouseDown}
                onMouseUp={handleMouseUp}
                onMouseLeave={handleMouseUp}
                className={`p-4 rounded-full transition-all duration-300 transform hover:scale-110 select-none flex items-center justify-center ${
                  isRecording 
                    ? 'bg-red-500 hover:bg-red-600 animate-pulse shadow-lg shadow-red-500/50' 
                    : 'bg-blue-600 hover:bg-blue-700'
                }`}
              >
                <Mic size={24} />
                <span className="sr-only">Push to talk</span>
              </button>
            </div>

            {voiceText && (
              <div className="mb-6 p-4 bg-gray-700/50 rounded-xl">
                <p className="text-blue-300">💬 "{voiceText}"</p>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
              {voiceCommands.map((command, index) => (
                <button
                  key={index}
                  onClick={() => handleVoiceCommand(command)}
                  className="px-4 py-2 bg-gray-700/50 hover:bg-gray-600/50 rounded-lg text-sm transition-all duration-300 transform hover:scale-105"
                >
                  "{command}"
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Roast Mode */}
        {roastMode && (
          <div className="mb-12 animate-fade-in">
            <div className="bg-gradient-to-r from-orange-900/50 to-red-900/50 backdrop-blur-sm rounded-2xl p-8 border border-orange-500/30">
              <h3 className="text-2xl font-bold mb-4 text-orange-300">🔥 Roast Mode Activated!</h3>
              <p className="text-lg leading-relaxed">{roastText}</p>
              <button
                onClick={() => setRoastMode(false)}
                className="mt-4 px-6 py-2 bg-orange-600 hover:bg-orange-700 rounded-lg transition-colors"
              >
                I can take it, give me more! 😤
              </button>
            </div>
          </div>
        )}

        {/* Progress Bar */}
        {isAnalyzing && (
          <div id="progress-section" className="mb-12">
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-8">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold flex items-center gap-3">
                  <Zap className="text-yellow-400" />
                  Processing Files (Parallel Mode)
                </h3>
                <span className="text-2xl font-bold text-blue-400">{Math.round(progress)}%</span>
              </div>
              
              <div className="w-full bg-gray-700 rounded-full h-4 mb-4">
                <div 
                  className="bg-gradient-to-r from-blue-500 to-purple-500 h-4 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
              
              {/* Humorous Loading Message */}
              {loadingMessage && (
                <div className="mt-4 p-3 bg-gray-700/30 rounded-lg border-l-4 border-orange-400">
                  <p className="text-orange-300 font-medium italic">{loadingMessage}</p>
                </div>
              )}
              
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
                <div>Files: {Math.round(progress * 2.47)}/247</div>
                <div>Speed: 4x faster</div>
                <div>Duplicates: {Math.round(progress * 0.23)}</div>
                <div>Categories: {Math.round(progress * 0.08)}</div>
                <div>Time: {(progress * 0.023).toFixed(1)}s</div>
              </div>
            </div>
          </div>
        )}

        {/* See Metrics Button - Always Visible */}
        <div className="text-center mb-8">
          <button
            onClick={() => {
              setShowMetricsModal(true);
              // Auto-scroll to modal after a short delay
              setTimeout(() => {
                const modalElement = document.querySelector('[data-modal="metrics"]');
                if (modalElement) {
                  modalElement.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'center' 
                  });
                }
              }, 100);
            }}
            className="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 px-8 py-4 rounded-xl font-semibold transition-all duration-300 transform hover:scale-105 flex items-center gap-3 mx-auto"
          >
            <BarChart3 size={20} />
            See Metrics?
          </button>
        </div>

        {/* Analysis Results */}
        {analysisResults && (
          <div className="mb-12 animate-fade-in">
            {/* File Categories */}
            <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-8 mb-8">
              <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
                <Brain className="text-purple-400" />
                AI Categorization
              </h3>
              
              <div className="space-y-3">
                {categoryData.map((category, index) => {
                  const Icon = category.icon;
                  const percentage = (category.count / 247 * 100).toFixed(1);
                  
                  return (
                    <div key={index} className="p-4 bg-gray-700/30 rounded-xl">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-3">
                          <Icon size={20} style={{ color: category.color }} />
                          <span className="font-semibold">{category.name}</span>
                        </div>
                        <span className="font-bold" style={{ color: category.color }}>
                          {category.count} ({percentage}%)
                        </span>
                      </div>
                      <div className="w-full bg-gray-600 rounded-full h-2">
                        <div 
                          className="h-2 rounded-full transition-all duration-1000"
                          style={{ 
                            width: `${percentage}%`,
                            backgroundColor: category.color
                          }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Before/After Comparison */}
            <div className="mt-8">
              <h3 className="text-xl font-bold mb-4 flex items-center justify-center gap-3">
                <FolderOpen className="text-cyan-400" />
                Before vs After
              </h3>
              
              <div className="grid grid-cols-2 gap-4">
                {/* Before Box */}
                <div style={{backgroundColor: 'rgba(127, 29, 29, 0.6)', borderColor: '#ef4444', borderWidth: '2px'}} className="backdrop-blur-sm rounded-lg p-3 shadow-lg">
                  <h4 className="text-sm font-bold mb-2 flex items-center gap-1" style={{color: '#fca5a5'}}>
                    <span>Before: Chaos</span> 😵
                  </h4>
                  <div className="space-y-1 text-xs p-2 rounded-lg max-h-24 overflow-y-auto" style={{backgroundColor: 'rgba(153, 27, 27, 0.5)', borderColor: '#dc2626', borderWidth: '1px'}}>
                    <div>📄 IMG_001.jpg</div>
                    <div>📄 document (1).pdf</div>
                    <div>📄 IMG_001 - Copy.jpg</div>
                    <div>📄 untitled.mp4</div>
                    <div className="text-red-300/70">...+239 more!</div>
                  </div>
                </div>
                
                {/* After Box */}
                <div style={{backgroundColor: 'rgba(20, 83, 45, 0.6)', borderColor: '#22c55e', borderWidth: '2px'}} className="backdrop-blur-sm rounded-lg p-3 shadow-lg">
                  <h4 className="text-sm font-bold mb-2 flex items-center gap-1" style={{color: '#86efac'}}>
                    <span>After: Organized!</span> ✨
                  </h4>
                  <div className="space-y-1 text-xs p-2 rounded-lg" style={{backgroundColor: 'rgba(21, 128, 61, 0.5)', borderColor: '#16a34a', borderWidth: '1px'}}>
                    <div>📁 Documents/ (89)</div>
                    <div>📁 Images/ (76)</div>
                    <div>📁 Audio/ (34)</div>
                    <div>📁 Videos/ (28)</div>
                    <div>📁 Archives/ (12)</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Metrics Modal */}
        {showMetricsModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div data-modal="metrics" className="bg-gray-800 rounded-2xl p-8 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold flex items-center gap-3">
                  <BarChart3 className="text-green-400" />
                  Performance Metrics
                </h3>
                <button
                  onClick={() => setShowMetricsModal(false)}
                  className="p-2 hover:bg-gray-700 rounded-lg transition-colors ml-4"
                >
                  ✕
                </button>
              </div>
              
              <div className="space-y-4">
                {performanceMetrics.map((metric, index) => (
                  <div key={index} className="flex justify-between items-center p-4 bg-gray-700/30 rounded-xl">
                    <span>{metric.metric}</span>
                    <span className="font-bold" style={{ color: metric.color }}>{metric.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="text-center py-8 border-t border-gray-700">
          <p className="text-gray-400">
            SmartSort AI - Addressing HackMIT challenges: Voloridge (Parallel Processing) • Rox (Messy Data) • Wispr (Voice Interface) • Demo (Clean UI)
          </p>
        </div>
      </div>
    </div>
  );
};

export default SmartSortApp;
