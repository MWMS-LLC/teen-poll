
import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { fetchCategories } from '../services/apiService';
import { createUser } from '/src/services/apiService.js';
import { useAudio } from '../contexts/AudioContext.jsx'
import HamburgerMenu from '../components/HamburgerMenu.jsx'
import Tooltip from '../components/Tooltip'
import Footer from '../components/Footer.jsx'

console.log("createUser in Landing.jsx:", createUser);

// Safe initialize user data in localStorage
function initializeStorage() {
  let data;

  try {
    data = JSON.parse(localStorage.getItem('myAppData'));
  } catch {
    data = null; // corrupted JSON
  }

  // If missing or invalid, reset with safe defaults
  if (!data || typeof data !== 'object') {
    data = { responses: [], createdAt: Date.now(), version: 1 };
    localStorage.setItem('myAppData', JSON.stringify(data));

    // Force a refresh silently so app restarts clean
    window.location.reload();
  }

  return data;
}


const Landing = () => {
  // Initialize storage safely
  initializeStorage();
  const { triggerThemeSong } = useAudio()
  const navigate = useNavigate()
  
  // Fallback UUID generation function for browsers that don't support crypto.randomUUID
  const generateUUID = () => {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0
      const v = c === 'x' ? r : (r & 0x3 | 0x8)
      return v.toString(16)
    })
  }

  // Utility function to clear app storage and start fresh
  const _clearLocalStorageAndRefresh = () => {
    try {
      // Remove only keys used by your app
      localStorage.removeItem('myAppData');
      localStorage.removeItem('user_uuid');
      localStorage.removeItem('year_of_birth');

      // Immediately reinitialize with safe defaults
      localStorage.setItem('myAppData', JSON.stringify({
        responses: [],
        createdAt: Date.now(),
        version: 1,
      }));

      // Refresh to start clean
      window.location.reload();
    } catch (error) {
      console.error('Error clearing localStorage:', error);
      alert('Error clearing data. Please try refreshing the page manually.');
    }
  };



  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [_error, _setError] = useState('')
  const [showAgeDropdown, setShowAgeDropdown] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState(null)
  const [selectedAge, setSelectedAge] = useState('')
  const [_userCreationError, setUserCreationError] = useState('')
  const [isCreatingUser, setIsCreatingUser] = useState(false)
  const [_retryCount, _setRetryCount] = useState(0)
  
  // Get current day of week (0 = Sunday, 1 = Monday, ..., 6 = Saturday)
  const getCurrentDayOfWeek = () => {
    return new Date().getDay()
  }
  
  // Parse PostgreSQL array format like "{0,1,2,3,4,5,6}" to JavaScript array
  const parseDayOfWeek = (dayOfWeekStr) => {
    if (!dayOfWeekStr) return null
    
    // Handle PostgreSQL array format: "{0,1,2,3,4,5,6}"
    if (typeof dayOfWeekStr === 'string' && dayOfWeekStr.startsWith('{') && dayOfWeekStr.endsWith('}')) {
      const content = dayOfWeekStr.slice(1, -1) // Remove { and }
      return content.split(',').map(day => parseInt(day.trim()))
    }
    
    // Handle already parsed array
    if (Array.isArray(dayOfWeekStr)) {
      return dayOfWeekStr
    }
    
    return null
  }
  
  // Check if category should be active today
  const isCategoryActiveToday = (category) => {
    // If day_of_week is not available yet (old API), always show as active
    if (!category.day_of_week) {
      return true
    }
    
    const dayOfWeekArray = parseDayOfWeek(category.day_of_week)
    
    if (!dayOfWeekArray || dayOfWeekArray.length === 0) {
      // If no day_of_week specified, always show
      return true
    }
    
    return dayOfWeekArray.includes(getCurrentDayOfWeek())
  }

  const [showSharing, setShowSharing] = useState(false)
  const [copySuccess, setCopySuccess] = useState(false)
  const [socialHandles, _setSocialHandles] = useState({})

  useEffect(() => {
    // Fetch categories from API
    fetchCategories()
      .then(data => {
        setCategories(data);
        setLoading(false);   // <-- clear loading here
      })
      .catch(err => {
        console.error("Error fetching categories:", err);
        setLoading(false);   // <-- clear loading even if error
      });
  }, []);   // <-- dependency array + closing parenthesis



  const handleCategoryClick = (category) => {
    // Add small delay to prevent accidental clicks during hover
    setTimeout(() => {
      // Check if user already exists in localStorage
      const existingUserUuid = localStorage.getItem('user_uuid')
      const existingYearOfBirth = localStorage.getItem('year_of_birth')
      
      if (existingUserUuid && existingYearOfBirth) {
        // User exists - trigger theme song and navigate directly to category
        triggerThemeSong()
        navigate(`/category/${category.id}`)
      } else {
        // New user - show age dropdown
        setSelectedCategory(category)
        setShowAgeDropdown(true)
        setSelectedAge('')
        setUserCreationError('') // Clear any previous errors
      }
    }, 150) // 150ms delay
  }

    const handleAgeSubmit = async () => {
    if (!selectedAge) return
    
    // Trigger theme song immediately after user interaction (before any async operations)
    console.log('🎵 User clicked Continue - triggering theme song immediately')
    triggerThemeSong()
    
    let birthYear
    if (selectedAge === 'before2005') {
      navigate('/too-old')
      return
    } else if (selectedAge === 'after2012') {
      navigate('/too-young')
      return
    } else {
      birthYear = parseInt(selectedAge)
      if (birthYear < 2005 || birthYear > 2012) {
        navigate('/too-old')
        return
    }
    }

    try {
      setIsCreatingUser(true)
      setUserCreationError('')
      
      // Generate UUID
      const userUuid = generateUUID()
      console.log('Generated user UUID:', userUuid)
      
      // Create user
      const _userResponse = await createUser(userUuid, birthYear)


      // Store in localStorage
      localStorage.setItem('user_uuid', userUuid)
      localStorage.setItem('year_of_birth', birthYear.toString())
      
      // Verify storage
      const storedUuid = localStorage.getItem('user_uuid')
      const storedYear = localStorage.getItem('year_of_birth')
      console.log('Stored in localStorage:', { user_uuid: storedUuid, year_of_birth: storedYear })

      // Navigate to category page
      navigate(`/category/${selectedCategory.id}`)
    } catch (err) {
      console.error('Error creating user:', err)
      
      // Set user-friendly error message
      let errorMessage = 'Failed to create your account. '
      if (err.response?.status === 400) {
        // These shouldn't happen with the current UI, but handle them gracefully
        if (err.response.data?.detail?.includes('year_of_birth')) {
          errorMessage = 'There was an issue with your age selection. Please try again.'
        } else if (err.response.data?.detail?.includes('user_uuid')) {
          errorMessage = 'There was an issue with your account ID. Please try again.'
        } else {
          errorMessage = 'Please check your information and try again.'
        }
      } else if (err.response?.status === 500) {
        errorMessage = 'Server error. Please try again in a moment.'
      } else if (err.code === 'NETWORK_ERROR') {
        errorMessage = 'Network error. Please check your internet connection and try again.'
      } else if (err.message?.includes('timeout')) {
        errorMessage = 'Request timed out. Please check your connection and try again.'
      } else {
        errorMessage = 'Something went wrong. Please try again.'
      }
      
      setUserCreationError(errorMessage)
      
      // DO NOT continue to voting - user must be created successfully first
      // This prevents the 500 errors that happen when voting without a user in the database
    } finally {
      setIsCreatingUser(false)
    }
  }

  const closeAgeDropdown = () => {
    setShowAgeDropdown(false)
    setSelectedCategory(null)
    setSelectedAge('')
  }

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText('https://myworldmysay.com?ref=1ca99aea-8ae1-4c96-aeaa-a')
      setCopySuccess(true)
      setTimeout(() => setCopySuccess(false), 2000)
    } catch (err) {
      console.error('Failed to copy link:', err)
    }
  }

  const toggleSharing = () => {
    setShowSharing(!showSharing)
  }

  const hasConnectedAccounts = Object.values(socialHandles).some(handle => handle && handle.trim() !== '')

  const handleSocialShare = (platform) => {
    const url = 'https://myworldmysay.com?ref=1ca99aea-8ae1-4c96-aeaa-a'
    const text = 'Check out this poll app - My World My Say!'
    
    switch (platform) {
      case 'Discord':
        window.open(`https://discord.com/channels/@me?content=${encodeURIComponent(text + ' ' + url)}`)
        break
      case 'Instagram':
        // Instagram doesn't support direct link sharing, so copy to clipboard
        navigator.clipboard.writeText(text + ' ' + url)
        setCopySuccess(true)
        setTimeout(() => setCopySuccess(false), 2000)
        break
      case 'Snapchat':
        // Snapchat doesn't support direct link sharing, so copy to clipboard
        navigator.clipboard.writeText(text + ' ' + url)
        setCopySuccess(true)
        setTimeout(() => setCopySuccess(false), 2000)
        break
      case 'Whatsapp':
        window.open(`https://wa.me/?text=${encodeURIComponent(text + ' ' + url)}`)
        break
      case 'Tiktok':
        // TikTok doesn't support direct link sharing, so copy to clipboard
        navigator.clipboard.writeText(text + ' ' + url)
        setCopySuccess(true)
        setTimeout(() => setCopySuccess(false), 2000)
        break
      default:
        break
    }
  }

  // Bold, vibrant category gradients - more masculine and powerful
  const categoryGradients = {
    1: { gradient: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", emoji: "" }, // 1st_Thing_1st - Keep purple
    2: { gradient: "linear-gradient(135deg, #FF6B35 0%, #D63031 100%)", emoji: "" }, // Love - Bold red-orange
    3: { gradient: "linear-gradient(135deg, #E53E3E 0%, #C53030 100%)", emoji: "" }, // Friends - Deep red
    4: { gradient: "linear-gradient(135deg, #00B4D8 0%, #0077B6 100%)", emoji: "" }, // Online_Life - Bold blue
    5: { gradient: "linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%)", emoji: "" }, // Pinky - Bold purple
    6: { gradient: "linear-gradient(135deg, #1E40AF 0%, #1E3A8A 100%)", emoji: "" }, // Lowkey - Deep blue
    7: { gradient: "linear-gradient(135deg, #059669 0%, #047857 100%)", emoji: "" }, // Personal - Deep green
    8: { gradient: "linear-gradient(135deg, #F59E0B 0%, #D97706 100%)", emoji: "" }, // Healing - Bold amber
    9: { gradient: "linear-gradient(135deg, #7C2D12 0%, #991B1B 100%)", emoji: "" }, // Defense - Dark red
    10: { gradient: "linear-gradient(135deg, #DC2626 0%, #B91C1C 100%)", emoji: "" }, // Family - Bold red
    11: { gradient: "linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)", emoji: "" }, // Future - Bold blue
    12: { gradient: "linear-gradient(135deg, #0891B2 0%, #0E7490 100%)", emoji: "" }, // School - Bold cyan
    13: { gradient: "linear-gradient(135deg, #EA580C 0%, #C2410C 100%)", emoji: "" }, // Fun_Stuff - Bold orange
    14: { gradient: "linear-gradient(135deg, #7F1D1D 0%, #991B1B 100%)", emoji: "" }, // Chaos - Dark red
  }
  const getCategoryStyle = (categoryId) => {
    const style = categoryGradients[categoryId] || { 
      gradient: "linear-gradient(135deg, #f0f0f0, #cccccc)", 
      emoji: "✨" 
    }
    return style
  }

  const formatCategoryName = (categoryName) => {
    return categoryName
      .replace(/_/g, ' ')  // Replace underscores with spaces
      .replace(/\b\w/g, l => l.toUpperCase())  // Capitalize first letter of each word
  }

  if (loading) {
    return (
      <div style={styles.loadingContainer}>
        <div style={styles.loadingText}>Loading your world...</div>
        <div style={styles.loadingSpinner}></div>
      </div>
    )
  }

  if (_error) {
    return (
      <div style={styles.errorContainer}>
        <div style={styles.generalErrorText}>Oops! {_error}</div>
      </div>
    )
  }

  return (
    <div style={styles.container}>
      {/* Hamburger Menu */}
      <HamburgerMenu />
      
      {/* Age Verification Modal */}
      {showAgeDropdown && (
        <div style={styles.modalOverlay}>
          <div style={styles.modal}>
            <h2 style={styles.modalTitle}>Welcome to Your World</h2>
            <div style={styles.modalText}>
              We don't collect your name, email, or any personal info. Everything stays on your device.
            </div>
            
            {/* Error Display was deleted*/}
           
            <select
              style={styles.select}
              value={selectedAge}
              onChange={e => setSelectedAge(e.target.value)}
              disabled={isCreatingUser}
            >
              <option value="">Year of Birth</option>
              <option value="before2005">Before 2005</option>
              <option value="2005">2005</option>
              <option value="2006">2006</option>
              <option value="2007">2007</option>
              <option value="2008">2008</option>
              <option value="2009">2009</option>
              <option value="2010">2010</option>
              <option value="2011">2011</option>
              <option value="2012">2012</option>
              <option value="after2012">After 2012</option>
            </select>
            
            {/* Processing indicator */}
            {isCreatingUser && (
              <div style={styles.processingMessage}>
                <div style={styles.spinner}></div>
                Creating your account...
              </div>
            )}
            
            <div style={styles.modalButtons}>
              <button 
                style={isCreatingUser ? styles.submitButtonDisabled : styles.submitButton} 
                onClick={handleAgeSubmit}
                disabled={!selectedAge || isCreatingUser}
              >
                {isCreatingUser ? 'Creating Account...' : 'Continue'}
              </button>
              <button 
                style={styles.cancelButton} 
                onClick={closeAgeDropdown}
                disabled={isCreatingUser}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Logo and Title Section */}
      <div style={styles.titleSection}>
        <div style={styles.logoContainer}>
          <div style={styles.logoText}>My World My Say</div>
          <div style={styles.logoGlow}></div>
        </div>
        
        <div style={styles.taglineContainer}>
          <div style={styles.mainTagline}>Your voice matters.</div>
          <div style={styles.subtitle}>Pick a topic. Click. See what others feel too, anonymously.</div>
        </div>
      </div>

      {/* Social Media Sharing Section */}
      <div style={styles.sharingSection}>
        <div style={styles.sharingHeader}>
          <button 
            style={{
              ...styles.hideLinkButton,
              backgroundColor: showSharing ? '#D97706' : '#2D7D7A'
            }} 
            onClick={toggleSharing}
          >
            {showSharing ? 'Hide Link' : 'Share with your friends'}
          </button>
        </div>
        {showSharing && (
          <>
            <div style={styles.linkContainer}>
              <input 
                type="text" 
                value="https://myworldmysay.com?ref=1ca99aea-8ae1-4c96-aeaa-a" 
                readOnly 
                style={styles.linkInput}
              />
              <button style={styles.copyButton} onClick={handleCopyLink}>
                {copySuccess ? 'Copied!' : 'Copy link'}
              </button>
            </div>
            <div style={styles.followUsText}>Follow Us:</div>
            <div style={styles.socialButtons}>
          <button 
            style={{
              ...styles.socialButton,
              background: hasConnectedAccounts 
                ? 'rgba(147, 51, 234, 0.4)' 
                : 'rgba(147, 51, 234, 0.2)',
              border: hasConnectedAccounts 
                ? '1px solid rgba(196, 181, 253, 0.6)' 
                : '1px dashed rgba(196, 181, 253, 0.4)',
              color: hasConnectedAccounts ? 'white' : 'rgba(255, 255, 255, 0.7)'
            }}
            onMouseEnter={(e) => {
              if (hasConnectedAccounts) {
                e.target.style.background = 'rgba(147, 51, 234, 0.5)'
              } else {
                e.target.style.background = 'rgba(147, 51, 234, 0.3)'
              }
            }}
            onMouseLeave={(e) => {
              if (hasConnectedAccounts) {
                e.target.style.background = 'rgba(147, 51, 234, 0.4)'
              } else {
                e.target.style.background = 'rgba(147, 51, 234, 0.2)'
              }
            }}
            onClick={() => handleSocialShare('Discord')}
          >
            Discord
          </button>
          
          <button 
            style={{
              ...styles.socialButton,
              background: hasConnectedAccounts 
                ? 'rgba(236, 72, 153, 0.4)' 
                : 'rgba(236, 72, 153, 0.2)',
              border: hasConnectedAccounts 
                ? '1px solid rgba(251, 113, 133, 0.6)' 
                : '1px dashed rgba(251, 113, 133, 0.4)',
              color: hasConnectedAccounts ? 'white' : 'rgba(255, 255, 255, 0.7)'
            }}
            onMouseEnter={(e) => {
              if (hasConnectedAccounts) {
                e.target.style.background = 'rgba(236, 72, 153, 0.5)'
              } else {
                e.target.style.background = 'rgba(236, 72, 153, 0.3)'
              }
            }}
            onMouseLeave={(e) => {
              if (hasConnectedAccounts) {
                e.target.style.background = 'rgba(236, 72, 153, 0.4)'
              } else {
                e.target.style.background = 'rgba(236, 72, 153, 0.2)'
              }
            }}
            onClick={() => handleSocialShare('Instagram')}
          >
            Instagram
          </button>
          
          <button 
            style={{
              ...styles.socialButton,
              background: hasConnectedAccounts 
                ? 'rgba(234, 179, 8, 0.4)' 
                : 'rgba(234, 179, 8, 0.2)',
              border: hasConnectedAccounts 
                ? '1px solid rgba(250, 204, 21, 0.6)' 
                : '1px dashed rgba(250, 204, 21, 0.4)',
              color: hasConnectedAccounts ? 'white' : 'rgba(255, 255, 255, 0.7)'
            }}
            onMouseEnter={(e) => {
              if (hasConnectedAccounts) {
                e.target.style.background = 'rgba(234, 179, 8, 0.5)'
              } else {
                e.target.style.background = 'rgba(234, 179, 8, 0.3)'
              }
            }}
            onMouseLeave={(e) => {
              if (hasConnectedAccounts) {
                e.target.style.background = 'rgba(234, 179, 8, 0.4)'
              } else {
                e.target.style.background = 'rgba(234, 179, 8, 0.2)'
              }
            }}
            onClick={() => handleSocialShare('Snapchat')}
          >
            Snapchat
          </button>
          
          <button 
            style={{
              ...styles.socialButton,
              background: hasConnectedAccounts 
                ? 'rgba(34, 197, 94, 0.4)' 
                : 'rgba(34, 197, 94, 0.2)',
              border: hasConnectedAccounts 
                ? '1px solid rgba(74, 222, 128, 0.6)' 
                : '1px dashed rgba(74, 222, 128, 0.4)',
              color: hasConnectedAccounts ? 'white' : 'rgba(255, 255, 255, 0.7)'
            }}
            onMouseEnter={(e) => {
              if (hasConnectedAccounts) {
                e.target.style.background = 'rgba(34, 197, 94, 0.5)'
              } else {
                e.target.style.background = 'rgba(34, 197, 94, 0.3)'
              }
            }}
            onMouseLeave={(e) => {
              if (hasConnectedAccounts) {
                e.target.style.background = 'rgba(34, 197, 94, 0.4)'
              } else {
                e.target.style.background = 'rgba(34, 197, 94, 0.2)'
              }
            }}
            onClick={() => handleSocialShare('Whatsapp')}
          >
            Whatsapp
          </button>
          
          <button 
            className="tiktok-button"
            style={{
              ...styles.socialButton,
              background: hasConnectedAccounts 
                ? 'rgba(55, 65, 81, 0.4)' 
                : 'rgba(55, 65, 81, 0.2)',
              border: hasConnectedAccounts 
                ? '1px solid rgba(156, 163, 175, 0.6)' 
                : '1px dashed rgba(156, 163, 175, 0.4)',
              color: hasConnectedAccounts ? 'white' : 'rgba(255, 255, 255, 0.7)'
            }}
            onMouseEnter={(e) => {
              console.log('TikTok hover enter')
              if (hasConnectedAccounts) {
                e.target.style.background = 'rgba(75, 85, 99, 0.6)'
              } else {
                e.target.style.background = 'rgba(75, 85, 99, 0.4)'
              }
            }}
            onMouseLeave={(e) => {
              console.log('TikTok hover leave')
              if (hasConnectedAccounts) {
                e.target.style.background = 'rgba(55, 65, 81, 0.4)'
              } else {
                e.target.style.background = 'rgba(55, 65, 81, 0.2)'
              }
            }}
            onClick={() => handleSocialShare('Tiktok')}
          >
            Tiktok
          </button>
        </div>
              </>
            )}
        </div>


      {/* Category Topics */}
      <div style={styles.bubblesContainer}>
        <div style={styles.bubblesGrid}>
          {categories.map((category, index) => {
            const categoryStyle = getCategoryStyle(category.id)
            const isActive = isCategoryActiveToday(category)
            const dayOfWeekArray = parseDayOfWeek(category.day_of_week)
            const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            
            return (
              <Tooltip 
                key={category.id}
                content={
                  dayOfWeekArray && dayOfWeekArray.length > 0
                    ? `${category.category_text || category.description || 'Category'}\n\nAvailable: ${dayOfWeekArray.map(day => dayNames[day]).join(', ')}`
                    : (category.category_text || category.description || 'Category')
                }
                position="top"
              >
                <button
                  style={{
                    ...styles.bubble,
                    ...(isActive ? {
                      background: categoryStyle.gradient,
                      opacity: 1,
                      cursor: 'pointer'
                    } : {
                      background: categoryStyle.gradient,
                      opacity: 1,
                      cursor: 'help',
                      position: 'relative'
                    }),
                    animationDelay: `${index * 0.1}s`
                  }}
                  onClick={() => isActive && handleCategoryClick(category)}
                  className={isActive ? "bubble-hover" : ""}
                >
                  <div style={styles.bubbleEmoji}>{categoryStyle.emoji}</div>
                  <div style={{
                    ...styles.bubbleText,
                    color: !isActive ? '#666666' : styles.bubbleText.color
                  }}>
                    {formatCategoryName(category.category_name)}
                    {!isActive && dayOfWeekArray && (
                      <div style={{
                        ...styles.inactiveIndicator,
                        color: '#666666'
                      }}>
                        (Available {dayOfWeekArray.map(day => dayNames[day].slice(0, 3)).join(', ')})
                      </div>
                    )}
                  </div>
                </button>
              </Tooltip>
            )
          })}
        </div>
      </div>
      
      {/* Footer */}
      <Footer />
    </div>
  )
}

// Fun, creative styles
const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    background: 'linear-gradient(135deg, #0A0F2B 0%, #1A1F3B 50%, #2A2F4B 100%)',
    position: 'relative',
    overflowY: 'auto',
    padding: '20px'
  },
  
  loadingContainer: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'linear-gradient(135deg, #0A0F2B 0%, #1A1F3B 100%)',
    gap: '20px'
  },
  
  loadingText: {
    color: 'rgba(255, 255, 255, 0.8)',
    fontSize: '24px',
    fontWeight: '500'
  },
  
  loadingSpinner: {
    width: '40px',
    height: '40px',
    border: '4px solid rgba(255, 255, 255, 0.3)',
    borderTop: '4px solid #4ECDC4',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite'
  },
  
  errorContainer: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'linear-gradient(135deg, #0A0F2B 0%, #1A1F3B 100%)'
  },
  
  generalErrorText: {
    color: '#FF7675',
    fontSize: '20px',
    textAlign: 'center'
  },
  
  modalOverlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
    backdropFilter: 'blur(5px)'
  },
  
  modal: {
    backgroundColor: 'white',
    borderRadius: '20px',
    padding: '30px',
    maxWidth: '400px',
    width: '90%',
    textAlign: 'center',
    boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
    animation: 'modalSlideIn 0.3s ease-out'
  },
  
  modalTitle: {
    fontSize: '24px',
    fontWeight: 'bold',
    marginBottom: '20px',
    color: '#333'
  },
  
  modalText: {
    marginBottom: '20px',
    color: '#666',
    fontSize: '14px',
    lineHeight: '1.5'
  },
  
  select: {
    width: '100%',
    padding: '12px',
    fontSize: '16px',
    border: '2px solid #ddd',
    borderRadius: '10px',
    marginBottom: '20px',
    backgroundColor: 'white'
  },
  
  errorMessage: {
    color: '#FF7675',
    fontSize: '14px',
    marginBottom: '15px',
    padding: '10px',
    backgroundColor: '#FFE6E6',
    borderRadius: '8px',
    border: '1px solid #FFE6E6',
    textAlign: 'left'
  },
  
  modalButtons: {
    display: 'flex',
    gap: '10px',
    justifyContent: 'center'
  },
  
  submitButton: {
    padding: '12px 24px',
    backgroundColor: '#4ECDC4',
    color: 'white',
    border: 'none',
    borderRadius: '10px',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: '600',
    transition: 'all 0.2s ease'
  },
  
  submitButtonDisabled: {
    padding: '12px 24px',
    backgroundColor: '#95A5A6',
    color: 'rgba(255, 255, 255, 0.6)',
    border: 'none',
    borderRadius: '10px',
    cursor: 'not-allowed',
    fontSize: '16px',
    fontWeight: '600',
    transition: 'all 0.2s ease'
  },
  
  cancelButton: {
    padding: '12px 24px',
    backgroundColor: '#95A5A6',
    color: 'white',
    border: 'none',
    borderRadius: '10px',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: '600',
    transition: 'all 0.2s ease'
  },
  
  titleSection: {
    marginTop: '60px',
    marginBottom: '40px',
    textAlign: 'center'
  },
  
  logoContainer: {
    position: 'relative',
    marginBottom: '20px'
  },
  
  logoText: {
    fontSize: '36px',
    fontWeight: 'bold',
    color: '#FFFFFF',
    textShadow: '0 0 20px #2D7D7A, 0 0 40px #2D7D7A, 0 0 60px #2D7D7A, 0 0 80px #2D7D7A, 0 0 100px #2D7D7A',
    animation: 'logoFloat 3s ease-in-out infinite'
  },
  
  logoGlow: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: '100%',
    height: '100%',
    background: 'radial-gradient(circle, rgba(45, 125, 122, 0.1) 0%, transparent 60%)',
    filter: 'blur(10px)',
    zIndex: -1
  },
  
  taglineContainer: {
    maxWidth: '600px',
    margin: '0 auto',
    padding: '0 20px'
  },
  
  tagline: {
    fontSize: '18px',
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: '15px',
    fontStyle: 'italic',
    lineHeight: '1.6'
  },
  
  mainTagline: {
    fontSize: '28px',
    fontWeight: 'bold',
    marginBottom: '20px',
    color: 'white',
    letterSpacing: '1px'
  },
  
  subtitle: {
    fontSize: '18px',
    color: 'rgba(255, 255, 255, 0.9)',
    marginBottom: '15px',
    fontWeight: '500'
  },
  
  description: {
    fontSize: '16px',
    color: 'rgba(255, 255, 255, 0.7)',
    marginBottom: '20px',
    lineHeight: '1.6'
  },
  
  callToAction: {
    fontSize: '16px',
    color: 'rgba(255, 255, 255, 0.9)',
    fontWeight: '500',
    lineHeight: '1.6'
  },
  
  highlight: {
    color: 'rgba(255, 255, 255, 1)',
    fontWeight: '600'
  },
  
  sharingSection: {
    marginTop: '5px',
    marginBottom: '20px',
    padding: '8px',
    background: 'linear-gradient(135deg, #1A1F3B 0%, #2A2F4B 100%)',
    borderRadius: '20px',
    boxShadow: '0 10px 30px rgba(0, 0, 0, 0.3)',
    width: '90%',
    maxWidth: '600px',
    textAlign: 'center'
  },
  
  sharingHeader: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: '10px',
    paddingBottom: '8px',
    borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
  },
  
  sharingTitle: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#2D7D7A'
  },
  
  speechBubble: {
    fontSize: '24px'
  },
  
  hideLinkButton: {
    padding: '8px 15px',
    backgroundColor: '#4ECDC4',
    color: 'white',
    border: 'none',
    borderRadius: '10px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '600',
    transition: 'all 0.2s ease',
    whiteSpace: 'nowrap'
  },
  
  linkContainer: {
    display: 'flex',
    alignItems: 'center',
    background: 'rgba(255, 255, 255, 0.1)',
    borderRadius: '10px',
    padding: '6px 10px',
    marginBottom: '8px',
    border: '1px solid rgba(255, 255, 255, 0.2)'
  },
  
  linkInput: {
    flex: 1,
    background: 'transparent',
    border: 'none',
    color: 'white',
    fontSize: '16px',
    outline: 'none',
    paddingRight: '10px'
  },
  
  copyButton: {
    padding: '8px 15px',
    backgroundColor: '#2D7D7A',
    color: 'white',
    border: 'none',
    borderRadius: '10px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '600',
    transition: 'all 0.2s ease'
  },
  
  socialLabel: {
    fontSize: '18px',
    color: 'rgba(45, 125, 122, 0.9)',
    marginBottom: '15px',
    fontWeight: '500'
  },
  
  followUsText: {
    fontSize: '12px',
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: '6px',
    fontWeight: '500',
    textAlign: 'center'
  },
  
  socialButtons: {
    display: 'flex',
    gap: '8px',
    justifyContent: 'center',
    marginBottom: '0'
  },
  
  socialButton: {
    padding: '10px 20px',
    color: 'white',
    border: 'none',
    borderRadius: '20px',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: '600',
    transition: 'all 0.3s ease',
    boxShadow: '0 5px 15px rgba(0, 0, 0, 0.2)'
  },
  
  
  bubblesContainer: {
    width: '100%',
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center'
  },
  
  bubblesGrid: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '20px',
    width: '100%',
    maxWidth: '300px'
  },
  
  bubble: {
    padding: '20px 24px',
    borderRadius: '50px',
    fontSize: '18px',
    fontWeight: '600',
    color: '#F5E6B3',
    border: 'none',
    cursor: 'pointer',
    width: '240px',
    textAlign: 'center',
    boxShadow: '0 8px 25px rgba(0, 0, 0, 0.3)',
    transition: 'all 0.2s ease',
    animation: 'bubbleFloat 2s ease-in-out infinite',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '8px',
    ':hover': {
      transform: 'scale(1.02)',
      boxShadow: '0 12px 35px rgba(0, 0, 0, 0.4)'
    },
    ':active': {
      transform: 'scale(0.98)',
      transition: 'all 0.1s ease'
    }
  },
  
  bubbleEmoji: {
    fontSize: '24px'
  },
  
  bubbleText: {
    fontSize: '18px',
    lineHeight: '1.3',
    userSelect: 'none',
    WebkitUserSelect: 'none',
    MozUserSelect: 'none',
    msUserSelect: 'none'
  },
  
  inactiveIndicator: {
    fontSize: '12px',
    opacity: 0.7,
    marginTop: '4px',
    fontStyle: 'italic'
  },
  errorTitle: {
    fontSize: '18px',
    fontWeight: 'bold',
    marginBottom: '10px',
    color: '#FF7675'
  },
  errorText: {
    fontSize: '14px',
    color: '#FF7675',
    marginBottom: '15px',
    textAlign: 'left',
    padding: '0 10px',
    lineHeight: '1.4'
  },
  clearDataButton: {
    padding: '8px 15px',
    backgroundColor: '#FF7675',
    color: 'white',
    border: 'none',
    borderRadius: '10px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '600',
    transition: 'all 0.2s ease'
  },
  processingMessage: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    marginTop: '15px',
    color: '#4ECDC4',
    fontSize: '14px',
    fontWeight: '500'
  },
  spinner: {
    border: '4px solid rgba(255, 255, 255, 0.3)',
    borderTop: '4px solid #4ECDC4',
    borderRadius: '50%',
    width: '20px',
    height: '20px'
  }
}

export default Landing
