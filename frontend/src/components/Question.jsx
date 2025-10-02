import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import OptionsList from './OptionsList.jsx'
import ValidationBox from './ValidationBox.jsx'
import ResultsBarChart from './ResultsBarChart.jsx'
import { submitVote, submitCheckboxVote, submitOtherVote } from '../services/apiService.js'
const API_BASE = import.meta.env.VITE_API_BASE;

const Question = ({ question, onAnswered }) => {
  // ===== VOTING COOLDOWN CONFIGURATION =====
  // Adjust these values as needed:
  const VOTING_COOLDOWN_HOURS = 24  // 24 hours cooldown
  //const VOTING_COOLDOWN_MINUTES = 1  // 1 minute cooldown (commented out)
  
  // ===== VOTING COOLDOWN LOGIC =====
  const getVotingCooldownKey = (questionCode) => `voting_cooldown_${questionCode}`
  
  const isVotingOnCooldown = (questionCode) => {
    const cooldownKey = getVotingCooldownKey(questionCode)
    const lastVoteTime = localStorage.getItem(cooldownKey)
    
    if (!lastVoteTime) return false
    
    const now = new Date().getTime()
    const lastVote = parseInt(lastVoteTime)
    const cooldownMs = VOTING_COOLDOWN_HOURS * 60 * 60 * 1000 // Convert hours to milliseconds
    // const cooldownMs = VOTING_COOLDOWN_MINUTES * 60 * 1000 // Convert minutes to milliseconds
    
    return (now - lastVote) < cooldownMs
  }
  
  const setVotingCooldown = (questionCode) => {
    const cooldownKey = getVotingCooldownKey(questionCode)
    localStorage.setItem(cooldownKey, new Date().getTime().toString())
  }
  
  const getCooldownTimeRemaining = (questionCode) => {
    const cooldownKey = getVotingCooldownKey(questionCode)
    const lastVoteTime = localStorage.getItem(cooldownKey)
    
    if (!lastVoteTime) return 0
    
    const now = new Date().getTime()
    const lastVote = parseInt(lastVoteTime)
    const cooldownMs = VOTING_COOLDOWN_HOURS * 60 * 60 * 1000
    // const cooldownMs = VOTING_COOLDOWN_MINUTES * 60 * 1000 // Convert minutes to milliseconds
    
    const timeRemaining = cooldownMs - (now - lastVote)
    return Math.max(0, timeRemaining)
  }
  
  // Define styles at the top to avoid initialization errors
  const styles = {
    questionContainer: {
      border: '1px solid rgba(255, 255, 255, 0.15)',
      borderRadius: '24px',
      padding: '35px',
      backgroundColor: 'transparent',
      marginBottom: '30px',
      boxShadow: 'none',
      backdropFilter: 'none',
      transition: 'all 0.3s ease',
      position: 'relative',
      overflow: 'visible'
    },
    questionHeader: {
      padding: '15px 20px',
      borderRadius: '8px 8px 0 0',
      marginBottom: '20px',
      background: 'linear-gradient(135deg, #4A5568 0%, #2D3748 100%)',
      color: 'white',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      boxShadow: '0 4px 10px rgba(0, 0, 0, 0.1)'
    },
    questionHeaderContent: {
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      width: '100%'
    },
    questionTitle: {
      margin: 0,
      fontSize: '18px',
      fontWeight: 'normal',
      color: 'black',
      lineHeight: '1.6',
      whiteSpace: 'pre-wrap',
      wordWrap: 'break-word',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Helvetica, Arial, sans-serif',
      flex: 1,
      marginRight: '15px'
    },
    optionsContainer: {
      marginBottom: '20px'
    },
    errorContainer: {
      padding: '20px',
      backgroundColor: 'rgba(255, 107, 107, 0.1)',
      border: '1px solid #ff6b6b',
      borderRadius: '8px',
      color: '#ff6b6b',
      textAlign: 'center'
    },
    submitButton: {
      padding: '12px 24px',
      background: '#2D7D7A',
      color: 'white',
      border: 'none',
      borderRadius: '4px',
      cursor: 'pointer',
      fontSize: '16px',
      marginTop: '15px',
      transition: 'background-color 0.3s ease',
      fontWeight: '500'
    },
    resultsContainer: {
      marginTop: '20px'
    },
    loadingContainer: {
      padding: '20px',
      textAlign: 'center',
      color: 'rgba(255, 255, 255, 0.8)'
    },
    errorTitle: {
      fontSize: '20px',
      fontWeight: 'bold',
      marginBottom: '10px',
      color: '#ff6b6b'
    },
    errorText: {
      fontSize: '16px',
      marginBottom: '20px',
      color: '#ff6b6b'
    },
    clearDataButton: {
      padding: '10px 20px',
      background: '#ff6b6b',
      color: 'white',
      border: 'none',
      borderRadius: '4px',
      cursor: 'pointer',
      fontSize: '16px',
      transition: 'background-color 0.3s ease',
      fontWeight: '500'
    },
    playlistTag: {
      fontSize: '14px',
      opacity: 0.8,
      fontStyle: 'italic',
      marginTop: '8px',
      color: 'rgba(255, 255, 255, 0.9)',
      textAlign: 'center'
    },
    playlistToggleButton: {
      background: 'rgba(255, 255, 255, 0.1)',
      border: '1px solid rgba(255, 255, 255, 0.2)',
      borderRadius: '50%',
      width: '40px',
      height: '40px',
      fontSize: '18px',
      color: 'rgba(255, 255, 255, 0.8)',
      cursor: 'pointer',
      transition: 'all 0.2s ease',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      marginLeft: '15px',
      flexShrink: 0
    },
    playlistButtonContainer: {
      padding: '20px 32px',
      background: 'rgba(255, 255, 255, 0.05)',
      borderTop: '1px solid rgba(255, 255, 255, 0.1)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center'
    },
    playlistButton: {
      background: 'linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%)',
      color: 'white',
      border: 'none',
      borderRadius: '25px',
      padding: '12px 24px',
      fontSize: '16px',
      fontWeight: '600',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      boxShadow: '0 4px 15px rgba(78, 205, 196, 0.3)'
    },
    playlistIcon: {
      fontSize: '18px'
    }
  }

  const [options, setOptions] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedOptions, setSelectedOptions] = useState([])
  const [showResults, setShowResults] = useState(false)
  const [results, setResults] = useState(null)
  const [validationMessage, setValidationMessage] = useState('')
  const [companionAdvice, setCompanionAdvice] = useState('')
  const [showCompanion, setShowCompanion] = useState(false)
  const [otherText, setOtherText] = useState('')
  const [showOtherInput, setShowOtherInput] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [votingOnCooldown, setVotingOnCooldown] = useState(false)
  const [cooldownTimeRemaining, setCooldownTimeRemaining] = useState(0)
  const [error, setError] = useState(null)
  const [expandedPlaylist, setExpandedPlaylist] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    console.log('Question useEffect triggered for:', question.question_code)
    fetchOptions()
    
    // Check if user is already on cooldown from a previous vote
    // This is needed to show cooldown message if they refresh the page or return to the question
    const checkExistingCooldown = () => {
      const onCooldown = isVotingOnCooldown(question.question_code)
      if (onCooldown) {
        setVotingOnCooldown(true)
        const remaining = getCooldownTimeRemaining(question.question_code)
        setCooldownTimeRemaining(remaining)
      }
    }
    
    checkExistingCooldown()
    
    // Set up interval to update cooldown countdown only if user is actively on cooldown
    const interval = setInterval(() => {
      if (votingOnCooldown) {
        const remaining = getCooldownTimeRemaining(question.question_code)
        setCooldownTimeRemaining(remaining)
        
        if (remaining <= 0) {
          setVotingOnCooldown(false)
          setCooldownTimeRemaining(0)
        }
      }
    }, 1000) // Update every second
    
    return () => clearInterval(interval)
  }, [question.question_code, votingOnCooldown])

  const fetchOptions = async () => {
    setLoading(true)
    try {
      const response = await axios.get(
        `${API_BASE}/api/questions/${question.question_code}/options`
      )
      setOptions(response.data.options)   // <-- FIXED
    } catch (err) {
      console.error('Error fetching options:', err)
    } finally {
      setLoading(false)
    }
  }


  const handleSingleChoice = async (optionSelect) => {
    // Check if voting is on cooldown from localStorage
    const onCooldown = isVotingOnCooldown(question.question_code)
    if (onCooldown) {
      // Show the cooldown clock when they try to vote again
      setVotingOnCooldown(true)
      const remaining = getCooldownTimeRemaining(question.question_code)
      setCooldownTimeRemaining(remaining)
      console.log('Voting is on cooldown for question:', question.question_code)
      return
    }
    
    try {
      // Show loading state immediately
      setIsSubmitting(true)
      
      // Get user_uuid from localStorage
      const userUuid = localStorage.getItem('user_uuid')
      console.log('Attempting to submit vote with user_uuid:', userUuid)
      console.log('All localStorage items:', Object.keys(localStorage).map(key => ({ key, value: localStorage.getItem(key) })))
      
      if (!userUuid) {
        console.error('No user_uuid found')
        console.log('localStorage contents:', localStorage)
        setIsSubmitting(false)
        return
      }

      const voteData = {
        question_code: question.question_code,
        option_select: optionSelect,
        user_uuid: userUuid
      }
      console.log('Submitting vote data:', voteData)

      // Submit vote using API service
      await submitVote(question.question_code, optionSelect, userUuid)

      // Get results
      const resultsResponse = await axios.get(`${API_BASE}/api/results/${question.question_code}`)
      setResults(resultsResponse.data)
      setShowResults(true)

      // Set validation message
      const selectedOption = options.find(opt => opt.option_select === optionSelect)
      setValidationMessage(selectedOption.response_message)
      setCompanionAdvice(selectedOption.companion_advice)
      setShowCompanion(false)

      // Set voting cooldown for this question (but don't show clock yet)
      setVotingCooldown(question.question_code)
      // Don't set votingOnCooldown to true here - only show clock when they try to vote again

      // Notify parent component that question was answered
      if (onAnswered) {
        onAnswered(question)
      }
    } catch (err) {
      console.error('Error submitting vote:', err)
      setError({ message: 'An error occurred while voting.' })
    } finally {
      // Always hide loading state
      setIsSubmitting(false)
    }
  }

  const handleCheckboxSubmit = async () => {
    if (selectedOptions.length === 0) return;

    // 🚫 Block "Other" with no text
    if (selectedOptions.includes("OTHER") && !otherText.trim()) {
      alert("Please enter text for 'Other' before submitting.");
      return;
    }

    // Cooldown gate
    const onCooldown = isVotingOnCooldown(question.question_code);
    if (onCooldown) {
      setVotingOnCooldown(true);
      const remaining = getCooldownTimeRemaining(question.question_code);
      setCooldownTimeRemaining(remaining);
      return;
    }

    try {
      setIsSubmitting(true);

      const userUuid = localStorage.getItem("user_uuid");
      if (!userUuid) {
        setIsSubmitting(false);
        return;
      }

      console.log('=== CHECKBOX SUBMIT ===')
      console.log('selectedOptions:', selectedOptions)
      console.log('question.check_box:', question.check_box)

      // Submit checkbox vote using API service
      await submitCheckboxVote(
        question.question_code, 
        selectedOptions, 
        userUuid, 
        selectedOptions.includes("OTHER") ? otherText : null
      );

      // Refresh results
      const resultsResponse = await axios.get(
        `${API_BASE}/api/results/${question.question_code}`
      );
      setResults(resultsResponse.data);
      setShowResults(true);

      // Validation messages
      const messages = selectedOptions
        .map((opt) => {
          const o = options.find((x) => x.option_select === opt);
          return o ? o.response_message : "";
        })
        .filter(Boolean);
      setValidationMessage(messages.join("\n\n"));

      // Companion advice
      const advice = selectedOptions
        .map((opt) => {
          const o = options.find((x) => x.option_select === opt);
          return o ? o.companion_advice : "";
        })
        .filter(Boolean);
      setCompanionAdvice(advice.join("\n\n"));
      setShowCompanion(false);

      // Clear state + start cooldown
      setSelectedOptions([]);
      setOtherText("");
      setVotingCooldown(question.question_code);

      if (onAnswered) onAnswered(question);
    } catch (err) {
      console.error("Error submitting checkbox vote:", err);
      setError({ message: "An error occurred while voting." });
    } finally {
      setIsSubmitting(false);
    }
  };


  const handleOtherSubmit = async () => {
    if (!otherText.trim()) return

    try {
      // Show loading state immediately
      setIsSubmitting(true)
      
      // Get user_uuid from localStorage
      const userUuid = localStorage.getItem('user_uuid')
      if (!userUuid) {
        console.error('No user_uuid found')
        setIsSubmitting(false)
        return
      }

      await submitOtherVote(question.question_code, otherText, userUuid)

      // Get results after submitting
      const resultsResponse = await axios.get(`${API_BASE}/api/results/${question.question_code}`)
      setResults(resultsResponse.data)
      setShowResults(true)

      // Set validation message for OTHER response
      setValidationMessage('Thank you for sharing your thoughts!')
      setCompanionAdvice('Your unique perspective adds valuable insight to this poll.')
      setShowCompanion(false)

      // Clear the form
      setOtherText('')
      setShowOtherInput(false)

      // Notify parent component that question was answered
      if (onAnswered) {
        onAnswered(question)
      }
    } catch (err) {
      console.error('Error submitting other response:', err)
      setError({ message: 'An error occurred while submitting your response.' })
    } finally {
      // Always hide loading state
      setIsSubmitting(false)
    }
  }

  const handleOptionChange = (optionSelect, checked) => {
    console.log(`=== CHECKBOX OPTION CHANGE ===`)
    console.log(`Option change: ${optionSelect}, checked: ${checked}`)
    console.log(`Question check_box: ${question.check_box}`)
    console.log(`Current selectedOptions:`, selectedOptions)
    
    if (checked) {
      setSelectedOptions(prev => {
        const newOptions = [...prev, optionSelect]
        console.log('New selected options:', newOptions)
        return newOptions
      })
    } else {
      setSelectedOptions(prev => {
        const newOptions = prev.filter(opt => opt !== optionSelect)
        console.log('New selected options:', newOptions)
        return newOptions
      })
    }
  }

  const handleOtherClick = () => {
    setShowOtherInput(true)
    setSelectedOptions([])
  }

  // Extract playlist from question text if it contains [playlist:name]
  const extractPlaylist = (questionText) => {
    const playlistMatch = questionText.match(/\[playlist:([^\]]+)\]/)
    return playlistMatch ? playlistMatch[1] : null
  }

  const handlePlaylistToggle = (e) => {
    e.stopPropagation()
    setExpandedPlaylist(!expandedPlaylist)
  }

  const handlePlaylistClick = () => {
    const playlist = extractPlaylist(question.question_text)
    if (playlist) {
      navigate(`/soundtrack?playlist=${encodeURIComponent(playlist)}`, {
        state: { from: window.location.pathname }
      })
    }
  }

  const questionPlaylist = extractPlaylist(question.question_text)

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

  if (loading) return <div style={styles.loadingContainer}>Loading options...</div>
  
  // Safety check for question data
  if (!question || !question.question_text) {
    console.error('Invalid question data:', question)
    return (
      <div style={styles.errorContainer}>
        <h3>Error: Invalid question data</h3>
        <p>This question could not be loaded properly.</p>
        <pre>{JSON.stringify(question, null, 2)}</pre>
      </div>
    )
  }

  // Show error display if there's an error
  if (error) {
    return (
      <div style={styles.errorContainer}>
        <div style={styles.errorTitle}>⚠️ Error</div>
        <div style={styles.errorText}>{error.message}</div>
        <button 
          onClick={clearLocalStorageAndRefresh} 
          style={styles.clearDataButton}
        >
          Clear the Error
        </button>
      </div>
    )
  }

  return (
    <div style={{
      ...styles.questionContainer,
      borderColor: question.color_code || '#4A5568',
      boxShadow: `0 8px 25px ${question.color_code ? `${question.color_code}20` : '#4A556820'}`
    }}>
      <div style={{
        ...styles.questionHeader,
        background: question.color_code ? `linear-gradient(135deg, ${question.color_code} 0%, ${question.color_code}CC 100%)` : 'linear-gradient(135deg, #4A5568 0%, #2D3748 100%)'
      }}>
        <div style={styles.questionHeaderContent}>
          {/* Playlist Toggle Button - Only show if question has playlist */}
          {questionPlaylist && (
            <button
              style={styles.playlistToggleButton}
              className="playlist-toggle-hover"
              onClick={handlePlaylistToggle}
              title="Toggle playlist"
            >
              🎵
            </button>
          )}
          
          <h3 style={styles.questionTitle}>
            {question.question_text || 'Question loading...'}
          </h3>
        </div>
        
        {/* Playlist Tag - Removed to prevent mobile overflow */}
      </div>
      
      {/* Playlist Button - Only show when expanded and has playlist */}
      {expandedPlaylist && questionPlaylist && (
        <div style={styles.playlistButtonContainer}>
          <button
            style={styles.playlistButton}
            className="playlist-button-hover"
            onClick={handlePlaylistClick}
          >
            <span style={styles.playlistIcon}>🎵</span>
            Listen to Playlist
          </button>
        </div>
      )}

      {/* Voting Cooldown Message */}
      {votingOnCooldown && (
        <div style={{
          padding: '15px 20px',
          margin: '0 20px 20px 20px',
          backgroundColor: 'rgba(255, 193, 7, 0.1)',
          border: '1px solid #ffc107',
          borderRadius: '8px',
          color: '#856404',
          textAlign: 'center',
          fontSize: '14px'
        }}>
          <strong>⏰ Voting Cooldown Active</strong>
          <br />
          You've already voted on this question. Please wait{' '}
          {Math.floor(cooldownTimeRemaining / (1000 * 60 * 60))}h{' '}
          {Math.floor((cooldownTimeRemaining % (1000 * 60 * 60)) / (1000 * 60))}m{' '}
          {Math.floor((cooldownTimeRemaining % (1000 * 60)) / 1000)}s before voting on this question again.
        </div>
      )}

      {!showResults && (
        <div style={styles.optionsContainer}>
          {options && options.length > 0 ? (
            <OptionsList
              options={options}
              isCheckbox={question.check_box}
              selectedOptions={selectedOptions}
              onOptionChange={handleOptionChange}
              onSingleChoice={handleSingleChoice}
              onOtherClick={handleOtherClick}
              onOtherSubmit={handleOtherSubmit}
              otherText={otherText}
              setOtherText={setOtherText}
              showOtherInput={showOtherInput}
              isSubmitting={isSubmitting}
              maxSelect={question.max_select}
              disabled={votingOnCooldown}
            />
          ) : (
            <div style={styles.errorContainer}>
              <strong>Error:</strong> No options available for this question.
              <br />
              <small>Question code: {question.question_code}</small>
            </div>
          )}
        </div>
      )}

      {question.check_box && !showResults && selectedOptions.length > 0 && (
        <div style={{ marginTop: '15px' }}>
          <button
            onClick={handleCheckboxSubmit}
            disabled={isSubmitting || votingOnCooldown}
            style={{
              ...styles.submitButton,
              background: (isSubmitting || votingOnCooldown) ? '#1a5a57' : '#2D7D7A',
              opacity: (isSubmitting || votingOnCooldown) ? 0.7 : 1,
              cursor: (isSubmitting || votingOnCooldown) ? 'not-allowed' : 'pointer'
            }}
          >
            {isSubmitting ? 'Submitting...' : (votingOnCooldown ? 'Voting Cooldown' : 'Submit')}
          </button>
        </div>
      )}

      {showResults && (
        <div style={styles.resultsContainer}>
          {results ? (
            <ResultsBarChart results={results} questionText={question.question_text} options={options} />
          ) : (
            <div style={styles.errorContainer}>
              <strong>Error:</strong> No results available to display.
            </div>
          )}
          
          <ValidationBox
            message={validationMessage}
            companionAdvice={companionAdvice}
            showCompanion={showCompanion}
            onToggleCompanion={() => setShowCompanion(!showCompanion)}
          />
        </div>
      )}
    </div>
  )
}

export default Question
