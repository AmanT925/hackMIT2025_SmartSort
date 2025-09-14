import React, { useState, useRef, useCallback } from 'react';
import { Upload, Mic, MicOff, BarChart3, FolderOpen, Zap, Brain, MessageCircle, FileText, Image, Music, Video, Archive, Code } from 'lucide-react';
import './App.css';

// Mock data for demo
const performanceMetrics = {
  filesProcessed: 247,
  processingSpeed: '4x faster',
  duplicatesFound: 23,
  categoriesCreated: 8,
  timeElapsed: '2.3s'
};

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
  const [analysisResults, setAnalysisResults] = useState<{
    totalFiles: number;
    categories: typeof categoryData;
    performance: typeof performanceMetrics;
  } | null>(null);
  const [roastMode, setRoastMode] = useState(false);
  const [roastText, setRoastText] = useState('');
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

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    handleFileAnalysis(files);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    handleFileAnalysis(files);
  };

  // File analysis simulation
  const handleFileAnalysis = async (files: File[]) => {
    setIsAnalyzing(true);
    setProgress(0);
    
    // Simulate progress
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsAnalyzing(false);
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

  // Voice recording handlers
  const toggleRecording = () => {
    setIsRecording(!isRecording);
    if (!isRecording) {
      // Start recording
      setTimeout(() => {
        setVoiceText("Sort this folder and tell me what you found");
        setIsRecording(false);
      }, 3000);
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
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
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
            
            <button
              onClick={() => fileInputRef.current?.click()}
              className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 px-8 py-4 rounded-xl font-semibold transition-all duration-300 transform hover:scale-105"
            >
              Choose Folder
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
                onClick={toggleRecording}
                className={`p-4 rounded-full transition-all duration-300 transform hover:scale-110 ${
                  isRecording 
                    ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
                    : 'bg-blue-600 hover:bg-blue-700'
                }`}
              >
                {isRecording ? <MicOff size={24} /> : <Mic size={24} />}
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
          <div className="mb-12">
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

        {/* Analysis Results */}
        {analysisResults && (
          <div className="mb-12 animate-fade-in">
            <div className="grid md:grid-cols-2 gap-8">
              {/* Performance Metrics */}
              <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-8">
                <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
                  <BarChart3 className="text-green-400" />
                  Performance Metrics
                </h3>
                
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-4 bg-gray-700/30 rounded-xl">
                    <span>Files Processed</span>
                    <span className="font-bold text-blue-400">{performanceMetrics.filesProcessed}</span>
                  </div>
                  <div className="flex justify-between items-center p-4 bg-gray-700/30 rounded-xl">
                    <span>Processing Speed</span>
                    <span className="font-bold text-green-400">{performanceMetrics.processingSpeed}</span>
                  </div>
                  <div className="flex justify-between items-center p-4 bg-gray-700/30 rounded-xl">
                    <span>Duplicates Found</span>
                    <span className="font-bold text-yellow-400">{performanceMetrics.duplicatesFound}</span>
                  </div>
                  <div className="flex justify-between items-center p-4 bg-gray-700/30 rounded-xl">
                    <span>Time Elapsed</span>
                    <span className="font-bold text-purple-400">{performanceMetrics.timeElapsed}</span>
                  </div>
                </div>
              </div>

              {/* File Categories */}
              <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl p-8">
                <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
                  <Brain className="text-purple-400" />
                  AI Categorization
                </h3>
                
                <div className="space-y-3">
                  {categoryData.map((category, index) => {
                    const Icon = category.icon;
                    const percentage = (category.count / performanceMetrics.filesProcessed * 100).toFixed(1);
                    
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
            </div>

            {/* Before/After Comparison */}
            <div className="mt-8 bg-gray-800/50 backdrop-blur-sm rounded-2xl p-8">
              <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
                <FolderOpen className="text-cyan-400" />
                Before vs After
              </h3>
              
              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h4 className="text-xl font-bold mb-4 text-red-400">Before: Chaos 😵</h4>
                  <div className="space-y-2 text-sm bg-gray-700/30 p-4 rounded-xl max-h-40 overflow-y-auto">
                    <div>📄 IMG_001.jpg</div>
                    <div>📄 document (1).pdf</div>
                    <div>📄 IMG_001 - Copy.jpg</div>
                    <div>📄 untitled.mp4</div>
                    <div>📄 New Document.docx</div>
                    <div>📄 aaaaa.zip</div>
                    <div>📄 homework_final_FINAL_v2.pdf</div>
                    <div>📄 random_file.exe</div>
                    <div className="text-gray-500">...and 239 more files!</div>
                  </div>
                </div>
                
                <div>
                  <h4 className="text-xl font-bold mb-4 text-green-400">After: Organized! ✨</h4>
                  <div className="space-y-2 text-sm bg-gray-700/30 p-4 rounded-xl">
                    <div>📁 Documents/ (89 files)</div>
                    <div>📁 Images/ (76 files)</div>
                    <div>📁 Audio/ (34 files)</div>
                    <div>📁 Videos/ (28 files)</div>
                    <div>📁 Archives/ (12 files)</div>
                    <div>📁 Code/ (8 files)</div>
                    <div>📁 Duplicates_Removed/ (23 files)</div>
                  </div>
                </div>
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
