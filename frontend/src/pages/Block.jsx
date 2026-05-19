import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { fetchQuestions, fetchBlocks } from '../services/apiService';
import Question from '../components/Question'
import HamburgerMenu from '../components/HamburgerMenu'
import Footer from '../components/Footer.jsx'
import SoundtrackService from '../services/soundtrackService'

const Block = () => {
  const [questions, setQuestions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [answeredQuestions, setAnsweredQuestions] = useState(0)
  const [showMusicSuggestion, setShowMusicSuggestion] = useState(false)
  const [musicSuggestion, setMusicSuggestion] = useState(null)
  const [_allBlocks, setAllBlocks] = useState([])
  const [isLastBlock, setIsLastBlock] = useState(false)
  const [_allBlocksCompleted, setAllBlocksCompleted] = useState(false)
  const { blockCode } = useParams()
  const navigate = useNavigate()

  const soundtrackService = new SoundtrackService()

  const handleBackToBlocks = () => {
    const categoryId = blockCode.split("_")[0]
    navigate(`/category/${categoryId}`)
  }

  const loadSoundtracks = async () => {
    await soundtrackService.loadSoundtracks()
  }

  const loadQuestions = async () => {
    try {
      setLoading(true)
      const rawQuestions = await fetchQuestions(blockCode)
      setQuestions(rawQuestions)
    } catch (err) {
      setError("Failed to fetch questions")
      console.error("Error fetching questions:", err)
    } finally {
      setLoading(false)
    }
  }

  const loadBlocksForCategory = async () => {
    try {
      const categoryId = blockCode.split("_")[0]
      const blocks = await fetchBlocks(categoryId)
      setAllBlocks(blocks)
      
      // Check if this is the last block
      const isLast = blocks[blocks.length - 1]?.block_code === blockCode
      setIsLastBlock(isLast)
      
      // Check if all blocks are completed
      const userUuid = localStorage.getItem('user_uuid')
      const completedBlocks = JSON.parse(localStorage.getItem(`completed_blocks_${userUuid}`) || '[]')
      
      const allCompleted = blocks.every(block => 
        completedBlocks.includes(block.block_code) || block.block_code === blockCode
      )
      setAllBlocksCompleted(allCompleted)
    } catch (err) {
      console.error("Error loading blocks:", err)
    }
  }

  const markBlockAsCompleted = () => {
    const userUuid = localStorage.getItem('user_uuid')
    const completedBlocks = JSON.parse(localStorage.getItem(`completed_blocks_${userUuid}`) || '[]')
    
    if (!completedBlocks.includes(blockCode)) {
      completedBlocks.push(blockCode)
      localStorage.setItem(`completed_blocks_${userUuid}`, JSON.stringify(completedBlocks))
      console.log('Block marked as completed:', blockCode)
    }
  }

  useEffect(() => {
    const userUuid = localStorage.getItem('user_uuid')
    if (!userUuid) {
      console.log('No user UUID found, redirecting to landing page')
      navigate('/')
      return
    }

    console.log('User UUID found:', userUuid)

    loadQuestions()
    loadSoundtracks()
    loadBlocksForCategory()
  }, [blockCode, navigate])

  const handleQuestionAnswered = (questionData) => {
    const newCount = answeredQuestions + 1
    setAnsweredQuestions(newCount)

    // Track total questions answered in this category (across all blocks)
    const categoryId = blockCode.split("_")[0]
    const userUuid = localStorage.getItem('user_uuid')
    const categoryAnswersKey = `category_${categoryId}_answers_${userUuid}`
    const currentTotal = parseInt(localStorage.getItem(categoryAnswersKey) || '0')
    localStorage.setItem(categoryAnswersKey, (currentTotal + 1).toString())

    // Mark block as completed when all questions are answered
    if (newCount === questions.length) {
      markBlockAsCompleted()
    }

    if (newCount >= Math.min(3, questions.length) && !showMusicSuggestion) {
      setShowMusicSuggestion(true)
      generateMusicSuggestion(questionData)
    }
  }

  // Kept for future use - can be re-enabled by changing button onClick to use this function
  const _handleViewSummary = () => {
    // Check if user has answered at least 2 questions in this category
    const categoryId = blockCode.split("_")[0]
    const userUuid = localStorage.getItem('user_uuid')
    const categoryAnswersKey = `category_${categoryId}_answers_${userUuid}`
    const totalAnswered = parseInt(localStorage.getItem(categoryAnswersKey) || '0')

    if (totalAnswered < 2) {
      alert(`You need to answer at least 2 questions in this category to see your summary.\n\nYou've answered ${totalAnswered} so far.`)
      return
    }

    navigate(`/summary/${categoryId}`)
  }

  const generateMusicSuggestion = (questionData) => {
    if (!questionData || !questionData.question_text) return

    const smartSong = soundtrackService.getSmartSongRecommendation(
      questionData.question_text,
      blockCode
    )
    if (smartSong) {
      setMusicSuggestion(smartSong)
    }
  }

  const handleListenToPlaylist = () => {
    navigate('/soundtrack')
  }

  const handleNextBlock = () => {
    const categoryId = blockCode.split("_")[0]
    navigate(`/category/${categoryId}`)
  }

  if (loading) {
    return (
      <div style={styles.loadingContainer}>
        <div style={styles.loadingText}>Loading questions...</div>
        <div style={styles.loadingSpinner}></div>
      </div>
    )
  }

  if (error) {
    return (
      <div style={styles.errorContainer}>
        <div style={styles.errorText}>Oops! {error}</div>
      </div>
    )
  }

  return (
    <div style={styles.container}>
      <HamburgerMenu />

      <div style={styles.headerSection}>
        <div style={styles.backButton} onClick={handleBackToBlocks}>
          ← Back to Blocks
        </div>
        <h1 style={styles.pageTitle}>Questions</h1>
      </div>

      <div style={styles.questionsContainer}>
        <div style={styles.questionsList}>
          {questions.map((question, index) => (
            <div
              key={question.question_code}
              style={{
                ...styles.questionCard,
                animationDelay: `${index * 0.1}s`
              }}
              className="question-card"
            >
              <Question
                question={question}
                onAnswered={handleQuestionAnswered}
              />
            </div>
          ))}
        </div>
      </div>

      {showMusicSuggestion && musicSuggestion && (
        <div style={styles.musicSuggestionContainer}>
          <div style={styles.musicSuggestionCard}>
            <div style={styles.musicIcon}>🎵</div>
            <h3 style={styles.musicSuggestionTitle}>
              Hey, listen to a song to expand your thoughts
            </h3>
            <div style={styles.songSuggestion}>
              <div style={styles.songTitle}>{musicSuggestion.title}</div>
              <div style={styles.songLyrics}>"{musicSuggestion.lyrics}"</div>
            </div>
            <div style={styles.musicButtons}>
              <button
                style={styles.listenButton}
                onClick={handleListenToPlaylist}
              >
                Listen to Playlist
              </button>
              <button
                style={styles.skipButton}
                onClick={() => setShowMusicSuggestion(false)}
              >
                Maybe Later
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Navigation Buttons */}
      <div style={styles.backToBlocksContainer}>
        {isLastBlock ? (
          /* Final block: Back to Categories button */
          <button
            style={styles.backToCategoriesButton}
            onClick={handleNextBlock}
            className="back-to-categories-hover"
          >
            ← Back to Categories
          </button>
        ) : (
          /* Regular blocks: Back to Blocks button */
          <button
            style={styles.backToBlocksButton}
            onClick={handleNextBlock}
            className="back-to-blocks-hover"
          >
            Back to Blocks
          </button>
        )}
      </div>

      <Footer />
    </div>
  )
}

// Full styles preserved
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
    fontSize: '16px',
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

  errorText: {
    color: '#FF7675',
    fontSize: '20px',
    textAlign: 'center'
  },

  questionsContainer: {
    width: '100%',
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    marginTop: '40px'
  },

  questionsList: {
    width: '100%',
    maxWidth: '800px',
    display: 'flex',
    flexDirection: 'column',
    gap: '30px'
  },

  questionCard: {
    background: 'transparent',
    borderRadius: '0',
    padding: '0',
    border: 'none',
    boxShadow: 'none',
    backdropFilter: 'none',
    transition: 'all 0.4s ease',
    animation: 'questionSlideIn 0.6s ease-out forwards',
    opacity: 0,
    transform: 'translateY(30px)',
    position: 'relative',
    overflow: 'visible'
  },

  musicSuggestionContainer: {
    width: '100%',
    maxWidth: '800px',
    marginTop: '40px',
    padding: '20px',
    background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)',
    borderRadius: '20px',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
    backdropFilter: 'blur(10px)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center'
  },

  musicSuggestionCard: {
    background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%)',
    borderRadius: '15px',
    padding: '25px',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    boxShadow: '0 10px 20px rgba(0, 0, 0, 0.2)',
    backdropFilter: 'blur(10px)',
    textAlign: 'center',
    width: '100%',
    maxWidth: '600px'
  },

  musicIcon: {
    fontSize: '40px',
    marginBottom: '15px',
    color: '#4ECDC4'
  },

  musicSuggestionTitle: {
    fontSize: '18px',
    fontWeight: 'bold',
    color: 'white',
    marginBottom: '10px',
    textShadow: '0 0 15px rgba(255, 255, 255, 0.3)'
  },

  musicSuggestionText: {
    fontSize: '16px',
    color: 'rgba(255, 255, 255, 0.8)',
    marginBottom: '20px',
    lineHeight: '1.5'
  },


  songSuggestion: {
    background: 'rgba(255, 255, 255, 0.08)',
    borderRadius: '10px',
    padding: '15px',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    marginBottom: '20px',
    textAlign: 'left'
  },

  songTitle: {
    fontSize: '20px',
    fontWeight: 'bold',
    color: 'white',
    marginBottom: '5px'
  },

  songLyrics: {
    fontSize: '14px',
    color: 'rgba(255, 255, 255, 0.7)',
    fontStyle: 'italic'
  },

  musicButtons: {
    display: 'flex',
    justifyContent: 'space-around',
    gap: '15px'
  },

  listenButton: {
    background: '#4ECDC4',
    color: 'white',
    padding: '12px 25px',
    borderRadius: '25px',
    border: 'none',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: 'bold',
    transition: 'all 0.3s ease',
    boxShadow: '0 5px 15px rgba(78, 205, 196, 0.4)'
  },

  skipButton: {
    background: 'rgba(255, 255, 255, 0.1)',
    color: 'rgba(255, 255, 255, 0.7)',
    padding: '12px 25px',
    borderRadius: '25px',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: 'bold',
    transition: 'all 0.3s ease'
  },

  headerSection: {
    width: '100%',
    maxWidth: '800px',
    marginTop: '40px',
    textAlign: 'center',
    color: 'white',
    padding: '20px',
    borderRadius: '15px',
    background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
    backdropFilter: 'blur(10px)'
  },

  backButton: {
    fontSize: '16px',
    color: 'rgba(255, 255, 255, 0.7)',
    cursor: 'pointer',
    marginBottom: '15px',
    transition: 'color 0.3s ease'
  },

  pageTitle: {
    fontSize: '36px',
    fontWeight: 'bold',
    marginBottom: '10px',
    textShadow: '0 0 15px rgba(255, 255, 255, 0.3)'
  },

  pageSubtitle: {
    fontSize: '18px',
    color: 'rgba(255, 255, 255, 0.7)',
    textShadow: '0 0 10px rgba(255, 255, 255, 0.2)'
  },

  backToBlocksContainer: {
    width: '100%',
    maxWidth: '800px',
    display: 'flex',
    flexDirection: 'column',
    gap: '15px',
    alignItems: 'center',
    marginTop: '40px',
    marginBottom: '20px'
  },

  backToBlocksButton: {
    padding: '15px 30px',
    fontSize: '16px',
    fontWeight: '600',
    color: 'white',
    backgroundColor: '#2D7D7A',
    border: '2px solid #2D7D7A',
    borderRadius: '25px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    boxShadow: '0 4px 15px rgba(45, 125, 122, 0.3)',
    textTransform: 'none',
    letterSpacing: '0.5px'
  },

  backToCategoriesButton: {
    padding: '12px 30px',
    fontSize: '16px',
    fontWeight: '600',
    color: 'rgba(255, 255, 255, 0.9)',
    background: 'rgba(255, 255, 255, 0.1)',
    border: '2px solid rgba(255, 255, 255, 0.3)',
    borderRadius: '25px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    minWidth: '250px'
  },

  summaryButton: {
    padding: '18px 35px',
    fontSize: '18px',
    fontWeight: '700',
    color: '#0A0F2B',
    background: 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)',
    border: '2px solid rgba(255, 215, 0, 0.5)',
    borderRadius: '30px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    boxShadow: '0 8px 25px rgba(255, 215, 0, 0.4)',
    textTransform: 'none',
    letterSpacing: '0.5px',
    animation: 'sparkle 2s ease-in-out infinite'
  }
}

export default Block

