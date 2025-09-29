import React, { useState } from 'react';
import './RunSkipDropdown.css';

const RunSkipDropdown = ({ 
  onRun, 
  onSkip, 
  runLabel = "Run", 
  skipLabel = "Skip",
  disabled = false,
  className = "",
  size = "medium" // small, medium, large
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const handleRun = () => {
    onRun();
    setIsOpen(false);
  };

  const handleSkip = () => {
    onSkip();
    setIsOpen(false);
  };

  const toggleDropdown = () => {
    if (!disabled) {
      setIsOpen(!isOpen);
    }
  };

  return (
    <div className={`run-skip-dropdown ${className} ${size}`}>
      <button
        className={`dropdown-toggle ${disabled ? 'disabled' : ''}`}
        onClick={toggleDropdown}
        disabled={disabled}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        <span>Actions</span>
        <svg 
          className={`dropdown-arrow ${isOpen ? 'open' : ''}`} 
          width="12" 
          height="12" 
          viewBox="0 0 12 12"
        >
          <path d="M2 4l4 4 4-4" stroke="currentColor" strokeWidth="2" fill="none"/>
        </svg>
      </button>
      
      {isOpen && (
        <div className="dropdown-menu">
          <button 
            className="dropdown-item run-option"
            onClick={handleRun}
          >
            <span className="icon">▶</span>
            {runLabel}
          </button>
          <button 
            className="dropdown-item skip-option"
            onClick={handleSkip}
          >
            <span className="icon">⏭</span>
            {skipLabel}
          </button>
        </div>
      )}
    </div>
  );
};

export default RunSkipDropdown;

