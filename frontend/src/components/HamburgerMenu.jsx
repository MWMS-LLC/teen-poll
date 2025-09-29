import React, { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAudio } from '../contexts/AudioContext.jsx'

const HamburgerMenu = () => {
  const [open, setOpen] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  
  // Use global audio context for theme song state
  const { isThemeSongOn, toggleThemeSong } = useAudio()

  const handleNavigate = (path) => {
    setOpen(false)
    if (location.pathname !== path) {
      navigate(path)
    }
  }

  // Utility function to clear localStorage and start fresh
  const clearLocalStorageAndRefresh = () => {
    try {
      // Clear all localStorage data
      localStorage.clear()
      
      // Show a brief message
      alert('Data cleared! The page will refresh to start fresh.')
      
      // Refresh the page
      window.location.reload()
    } catch (error) {
      console.error('Error clearing localStorage:', error)
      alert('Error clearing data. Please try refreshing the page manually.')
    }
  }

  const handleSoundtrackNavigate = () => {
    setOpen(false)
    navigate('/soundtrack')
  }

  return (
    <div style={styles.container}>
      {/* Hamburger Icon */}
      <button
        style={styles.hamburgerButton}
        onClick={() => setOpen((prev) => !prev)}
        aria-label="Open menu"
      >
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={styles.hamburgerIcon}>
          <line x1="3" y1="6" x2="21" y2="6" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="18" x2="21" y2="18" />
        </svg>
      </button>
      
      {/* Dropdown Menu */}
      {open && (
        <div style={styles.dropdownMenu}>
          <button 
            style={styles.beforeYouBeginItem} 
            onClick={() => handleNavigate('/before-you-begin')}
          >
            Before You Begin
          </button>
          <button 
            style={styles.menuItem} 
            onClick={() => handleNavigate('/')}
          >
            Pick a Bubble
          </button>
          <button 
            style={styles.menuItem} 
            onClick={handleSoundtrackNavigate}
          >
            MyWorld Soundtrack
          </button>
          <button 
            style={styles.menuItem} 
            onClick={() => handleNavigate('/faq')}
          >
            FAQ/About
          </button>
          <button 
            style={styles.menuItem} 
            onClick={() => handleNavigate('/help')}
          >
            Help/Resources
          </button>
          
          {/* Theme Song Toggle */}
          <div style={styles.toggleContainer}>
            <span style={styles.toggleLabel}>Theme Song</span>
            <label style={styles.toggleSwitch}>
              <input 
                type="checkbox" 
                checked={isThemeSongOn} 
                onChange={toggleThemeSong} 
                style={styles.toggleInput} 
              />
              <div style={{
                ...styles.toggleSlider,
                backgroundColor: isThemeSongOn ? '#4ECDC4' : '#95A5A6'
              }}></div>
            </label>
          </div>

        </div>
      )}
    </div>
  )
}

const styles = {
  container: {
    position: 'fixed',
    top: '16px',
    right: '16px',
    zIndex: 50
  },
  
  hamburgerButton: {
    width: '48px',
    height: '48px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: '50%',
    background: 'rgba(255, 255, 255, 0.2)',
    border: 'none',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.3)'
  },
  
  hamburgerIcon: {
    color: 'white'
  },
  
  dropdownMenu: {
    position: 'absolute',
    right: 0,
    top: '100%',
    marginTop: '8px',
    width: '240px',
    background: 'rgba(20, 20, 20, 0.95)',
    backdropFilter: 'blur(15px)',
    color: 'white',
    borderRadius: '20px',
    boxShadow: '0 25px 50px rgba(0, 0, 0, 0.5)',
    padding: '20px 12px',
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
    border: '1px solid rgba(255, 255, 255, 0.15)',
    zIndex: 50
  },
  
  menuItem: {
    textAlign: 'left',
    padding: '12px 16px',
    borderRadius: '12px',
    background: 'transparent',
    color: 'rgba(255, 255, 255, 0.9)',
    border: 'none',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: '500',
    transition: 'all 0.2s ease',
    fontFamily: 'inherit',
    ':hover': {
      background: 'rgba(255, 255, 255, 0.1)',
      color: 'white'
    }
  },

  beforeYouBeginItem: {
    textAlign: 'left',
    padding: '12px 16px',
    borderRadius: '12px',
    background: '#FF8C42', // Warm orange
    color: 'white',
    border: 'none',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: '600',
    transition: 'all 0.2s ease',
    fontFamily: 'inherit',
    boxShadow: '0 4px 12px rgba(255, 140, 66, 0.3)',
    ':hover': {
      background: '#FF7A2E',
      transform: 'translateY(-1px)',
      boxShadow: '0 6px 16px rgba(255, 140, 66, 0.4)'
    }
  },
  
  toggleContainer: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '8px 16px',
    marginTop: '8px',
    borderTop: '1px solid rgba(255, 255, 255, 0.1)',
    paddingTop: '16px'
  },
  
  toggleLabel: {
    fontSize: '14px',
    fontWeight: '500'
  },
  
  toggleSwitch: {
    position: 'relative',
    display: 'inline-flex',
    alignItems: 'center',
    cursor: 'pointer'
  },
  
  toggleInput: {
    position: 'absolute',
    opacity: 0,
    width: 0,
    height: 0
  },
  
  toggleSlider: {
    width: '32px',
    height: '20px',
    borderRadius: '10px',
    transition: 'all 0.2s ease',
    position: 'relative'
  }
}

export default HamburgerMenu
