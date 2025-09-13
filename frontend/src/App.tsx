import React, { useState } from 'react';
import './App.css';

function App() {
  const [directoryPath, setDirectoryPath] = useState('');
  const [results, setResults] = useState<any>(null);
  const [voiceCommand, setVoiceCommand] = useState('');
  const [response, setResponse] = useState('');

  const createDemo = async () => {
    const res = await fetch('http://localhost:8000/demo/create');
    const data = await res.json();
    alert(`Demo created at: ${data.path}`);
    setDirectoryPath(data.path);
  };

  const analyzeFiles = async () => {
    const res = await fetch('http://localhost:8000/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ directory_path: directoryPath })
    });
    const data = await res.json();
    setResults(data);
  };

  const sendVoiceCommand = async () => {
    const res = await fetch('http://localhost:8000/voice-command', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: voiceCommand })
    });
    const data = await res.json();
    setResponse(data.response);
  };

  return (
    <div className="App" style={{ padding: '20px' }}>
      <h1>SmartSort - AI File Organizer</h1>
      
      <button onClick={createDemo}>Create Demo Files</button>
      
      <div>
        <input 
          value={directoryPath}
          onChange={(e) => setDirectoryPath(e.target.value)}
          placeholder="Directory path"
          style={{ width: '300px', margin: '10px' }}
        />
        <button onClick={analyzeFiles}>Analyze</button>
      </div>
      
      {results && (
        <div style={{ background: '#f0f0f0', padding: '10px', margin: '10px' }}>
          <h3>Results:</h3>
          <p>Files: {results.files_processed}</p>
          <p>Time: {results.processing_time?.toFixed(2)}s</p>
          <p>Categories: {Object.keys(results.categories || {}).length}</p>
        </div>
      )}
      
      <div>
        <input
          value={voiceCommand}
          onChange={(e) => setVoiceCommand(e.target.value)}
          placeholder="Try: 'roast my organization'"
          style={{ width: '300px', margin: '10px' }}
        />
        <button onClick={sendVoiceCommand}>Send Voice Command</button>
      </div>
      
      {response && <p style={{ background: '#e0e0e0', padding: '10px' }}>{response}</p>}
    </div>
  );
}

export default App;
