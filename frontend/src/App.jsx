import { useState } from 'react';
import ScanForm from './components/ScanForm';
import ScanStatus from './components/ScanStatus';
import './App.css';

function App() {
  const [taskId, setTaskId] = useState(null);
  const [result, setResult] = useState(null);

  const handleTaskStarted = (id) => {
    setTaskId(id);
    setResult(null);
  };

  const handleResult = (data) => {
    setResult(data);
  };

  return (
    <div className="app-container">
      <h1>VulTure Security Scanner</h1>
      <ScanForm onTaskStarted={handleTaskStarted} />
      {taskId && <ScanStatus taskId={taskId} onResult={handleResult} />}
      {result && (
        <pre className="result-json">{JSON.stringify(result, null, 2)}</pre>
      )}
    </div>
  );
}

export default App;
