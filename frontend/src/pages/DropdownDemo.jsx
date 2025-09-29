import React, { useState } from 'react';
import RunSkipDropdown from '../components/RunSkipDropdown';
import './DropdownDemo.css';

const DropdownDemo = () => {
  const [results, setResults] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);

  const addResult = (action, description) => {
    setResults(prev => [...prev, { action, description, timestamp: new Date().toLocaleTimeString() }]);
  };

  const handleRun = (description) => {
    setIsProcessing(true);
    // Simulate some processing time
    setTimeout(() => {
      addResult('Run', description);
      setIsProcessing(false);
    }, 1000);
  };

  const handleSkip = (description) => {
    addResult('Skip', description);
  };

  const clearResults = () => {
    setResults([]);
  };

  return (
    <div className="dropdown-demo">
      <div className="demo-header">
        <h1>Run/Skip Dropdown Demo</h1>
        <p>Click on any dropdown to see the Run/Skip options in action</p>
      </div>

      <div className="demo-section">
        <h2>Basic Usage</h2>
        <div className="demo-row">
          <div className="demo-item">
            <h3>Default Dropdown</h3>
            <RunSkipDropdown
              onRun={() => handleRun('Default dropdown')}
              onSkip={() => handleSkip('Default dropdown')}
            />
          </div>

          <div className="demo-item">
            <h3>Custom Labels</h3>
            <RunSkipDropdown
              onRun={() => handleRun('Custom labels')}
              onSkip={() => handleSkip('Custom labels')}
              runLabel="Execute"
              skipLabel="Pass"
            />
          </div>
        </div>
      </div>

      <div className="demo-section">
        <h2>Different Sizes</h2>
        <div className="demo-row">
          <div className="demo-item">
            <h3>Small</h3>
            <RunSkipDropdown
              onRun={() => handleRun('Small size')}
              onSkip={() => handleSkip('Small size')}
              size="small"
            />
          </div>

          <div className="demo-item">
            <h3>Medium (Default)</h3>
            <RunSkipDropdown
              onRun={() => handleRun('Medium size')}
              onSkip={() => handleSkip('Medium size')}
              size="medium"
            />
          </div>

          <div className="demo-item">
            <h3>Large</h3>
            <RunSkipDropdown
              onRun={() => handleRun('Large size')}
              onSkip={() => handleSkip('Large size')}
              size="large"
            />
          </div>
        </div>
      </div>

      <div className="demo-section">
        <h2>Special States</h2>
        <div className="demo-row">
          <div className="demo-item">
            <h3>Disabled State</h3>
            <RunSkipDropdown
              onRun={() => handleRun('Disabled')}
              onSkip={() => handleSkip('Disabled')}
              disabled={true}
            />
          </div>

          <div className="demo-item">
            <h3>Processing State</h3>
            <RunSkipDropdown
              onRun={() => handleRun('Processing')}
              onSkip={() => handleSkip('Processing')}
              disabled={isProcessing}
              runLabel={isProcessing ? "Processing..." : "Run"}
            />
          </div>
        </div>
      </div>

      <div className="demo-section">
        <h2>Real-world Examples</h2>
        <div className="demo-row">
          <div className="demo-item">
            <h3>Database Import</h3>
            <RunSkipDropdown
              onRun={() => handleRun('Import database schema')}
              onSkip={() => handleSkip('Import database schema')}
              runLabel="Import"
              skipLabel="Skip Import"
            />
          </div>

          <div className="demo-item">
            <h3>User Generation</h3>
            <RunSkipDropdown
              onRun={() => handleRun('Generate fake users')}
              onSkip={() => handleSkip('Generate fake users')}
              runLabel="Generate"
              skipLabel="Skip Generation"
            />
          </div>

          <div className="demo-item">
            <h3>Data Cleanup</h3>
            <RunSkipDropdown
              onRun={() => handleRun('Clean option prefixes')}
              onSkip={() => handleSkip('Clean option prefixes')}
              runLabel="Clean"
              skipLabel="Skip Cleanup"
            />
          </div>
        </div>
      </div>

      <div className="demo-section">
        <h2>Results Log</h2>
        <div className="results-controls">
          <button onClick={clearResults} className="clear-btn">
            Clear Results
          </button>
        </div>
        <div className="results-list">
          {results.length === 0 ? (
            <p className="no-results">No actions performed yet. Try clicking some dropdowns!</p>
          ) : (
            results.map((result, index) => (
              <div key={index} className={`result-item ${result.action.toLowerCase()}`}>
                <span className="result-action">{result.action}</span>
                <span className="result-description">{result.description}</span>
                <span className="result-time">{result.timestamp}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default DropdownDemo;

