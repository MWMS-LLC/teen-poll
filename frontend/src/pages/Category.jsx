import React, { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import { fetchBlocks } from '../services/apiService';
import HamburgerMenu from '../components/HamburgerMenu'
import Footer from '../components/Footer.jsx'
import { useAudio } from '../contexts/AudioContext.jsx'


const Category = () => {
  const [blocks, setBlocks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [expandedBlock, setExpandedBlock] = useState(null)
  const { categoryId } = useParams()
  const navigate = useNavigate()
  const location = useLocation()
  
  // Use global audio context for theme song auto-play
  const { autoPlayThemeSong } = useAudio()
  
  const loadBlocks = useCallback(async () => {
    try {
      setLoading(true);

      const rawBlocks = await fetchBlocks(categoryId); //  from apiService
      console.log('Fetched blocks:', rawBlocks);

      const blocksWithPlaylists = rawBlocks.map(block => {
        const playlistMatch = block.block_text.match(/🎵\[playlist:([^\]]+)\]/);
        if (playlistMatch) {
          return { ...block, playlist: playlistMatch[1] };
        }
        return block;
      });

      setBlocks(blocksWithPlaylists);
    } catch (err) {
      setError('Failed to fetch blocks');
      console.error('Error fetching blocks:', err);
    } finally {
      setLoading(false);
    }
  }, [categoryId]);

  useEffect(() => {
    const userUuid = localStorage.getItem('user_uuid');
    if (!userUuid) {
      console.log('No user UUID found, redirecting to landing page');
      navigate('/');
      return;
    }

    console.log('User UUID found:', userUuid);
    loadBlocks();          //  wrapper that calls fetchBlocks
    autoPlayThemeSong();
  }, [categoryId]);

  const handleBlockClick = (block) => {
    // Always navigate to block page
    navigate(`/block/${block.block_code}`)
  }

  const handlePlaylistToggle = (block, e) => {
    // Stop event propagation so it doesn't trigger block navigation
    e.stopPropagation()
    console.log('Playlist toggle clicked for block:', block.id, 'Current expanded:', expandedBlock)
    setExpandedBlock(expandedBlock === block.id ? null : block.id)
  }

  const handlePlaylistClick = (block) => {
    // Navigate to soundtrack page with playlist parameter and current location as state
    navigate(`/soundtrack?playlist=${encodeURIComponent(block.playlist)}`, {
      state: { from: location.pathname }
    })
  }

  if (loading) {
    return (
      <div style={styles.loadingContainer}>
        <div style={styles.loadingText}>Loading blocks...</div>
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
      {/* Hamburger Menu */}
      <HamburgerMenu />
      
      {/* Header Section */}
      <div style={styles.headerSection}>
        <div style={styles.backButton} onClick={() => navigate('/')}>
          ← Back to Categories
        </div>
        <h1 style={styles.pageTitle}>Choose a Block</h1>
        <div style={styles.pageSubtitle}>
          Pick the topic that speaks to you right now
        </div>
      </div>

      {/* Blocks Grid */}
      <div style={styles.blocksContainer}>
        <div style={styles.blocksGrid}>
          {blocks.map((block, index) => (
            <div
              key={block.id}
              style={{
                ...styles.blockContainer,
                background: getBlockGradient(index),
                animationDelay: `${index * 0.1}s`
              }}
            >
              <div 
                style={styles.blockButton}
                onClick={() => handleBlockClick(block)}
                className="block-hover"
              >
                {/* Playlist Toggle Button - Only show if block has playlist */}
                {block.playlist && (
                  <button
                    style={styles.playlistToggleButton}
                    className="playlist-toggle-hover"
                    onClick={(e) => handlePlaylistToggle(block, e)}
                    title="Toggle playlist"
                  >
                    🎵
                  </button>
                )}
                
                <div style={styles.blockContent}>
                  <div style={styles.blockTitle}>{block.block_text}</div>
                  {block.playlist && (
                    <div style={styles.playlistTag}>[playlist:{block.playlist}]</div>
                  )}
                </div>
              </div>
              
              {/* Playlist Button - Only show when expanded and has playlist */}
              {expandedBlock === block.id && block.playlist && (
                <div style={styles.playlistButtonContainer}>
                  <button
                    style={styles.playlistButton}
                    className="playlist-button-hover"
                    onClick={() => handlePlaylistClick(block)}
                  >
                    <span style={styles.playlistIcon}>🎵</span>
                    Listen to Playlist
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
      
      {/* Footer */}
      <Footer />
      

    </div>
  )
}

// Beautiful, subtle block gradients - more neutral and appealing to everyone
const getBlockGradient = (index) => {
  const gradients = [
    "linear-gradient(135deg, #4A5568 0%, #2D3748 100%)", // Subtle gray
    "linear-gradient(135deg, #2C7A7B 0%, #234E52 100%)", // Muted teal
    "linear-gradient(135deg, #553C9A 0%, #44318E 100%)", // Deep purple
    "linear-gradient(135deg, #C53030 0%, #9B2C2C 100%)", // Muted red
    "linear-gradient(135deg, #D69E2E 0%, #B7791F 100%)", // Warm gold
    "linear-gradient(135deg, #38A169 0%, #2F855A 100%)", // Forest green
    "linear-gradient(135deg, #3182CE 0%, #2C5282 100%)", // Navy blue
    "linear-gradient(135deg, #805AD5 0%, #6B46C1 100%)", // Royal purple
    "linear-gradient(135deg, #E53E3E 0%, #C53030 100%)", // Deep red
    "linear-gradient(135deg, #DD6B20 0%, #C05621 100%)", // Burnt orange
    "linear-gradient(135deg, #319795 0%, #2C7A7B 100%)", // Dark teal
    "linear-gradient(135deg, #5A67D8 0%, #4C51BF 100%)"  // Indigo
  ]
  return gradients[index % gradients.length]
}

// Premium styling
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
  
  errorText: {
    color: '#FF7675',
    fontSize: '20px',
    textAlign: 'center'
  },
  
  headerSection: {
    marginTop: '60px',
    marginBottom: '40px',
    textAlign: 'center',
    width: '100%',
    maxWidth: '800px'
  },
  
  backButton: {
    color: 'rgba(255, 255, 255, 0.7)',
    fontSize: '16px',
    cursor: 'pointer',
    marginBottom: '20px',
    transition: 'all 0.2s ease',
    display: 'inline-block',
    padding: '8px 16px',
    borderRadius: '20px',
    background: 'rgba(255, 255, 255, 0.1)',
    border: '1px solid rgba(255, 255, 255, 0.2)'
  },
  
  pageTitle: {
    fontSize: '36px',
    fontWeight: 'bold',
    color: 'white',
    marginBottom: '15px',
    textShadow: '0 0 20px rgba(255, 255, 255, 0.3)'
  },
  
  pageSubtitle: {
    fontSize: '18px',
    color: 'rgba(255, 255, 255, 0.8)',
    lineHeight: '1.6'
  },
  
  blocksContainer: {
    width: '100%',
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'flex-start'
  },
  
  blocksGrid: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '20px',
    width: '100%',
    maxWidth: '800px'
  },
  
  blockContainer: {
    width: '100%',
    borderRadius: '20px',
    overflow: 'hidden',
    boxShadow: '0 8px 25px rgba(0, 0, 0, 0.3)',
    animation: 'blockSlideIn 0.5s ease-out forwards',
    opacity: 0,
    transform: 'translateY(20px)'
  },
  
  blockButton: {
    padding: '24px 32px',
    fontSize: '16px',
    fontWeight: '600',
    color: 'white',
    border: 'none',
    cursor: 'pointer',
    width: '100%',
    textAlign: 'center',
    transition: 'all 0.3s ease',
    minHeight: '120px',
    display: 'flex',
    alignItems: 'center',
    background: 'transparent'
  },
  
  blockContent: {
    position: 'relative',
    zIndex: 2,
    flex: 1
  },
  
  blockTitle: {
    fontSize: '18px',
    fontWeight: 'bold',
    marginBottom: '8px',
    textShadow: '0 2px 4px rgba(0, 0, 0, 0.3)',
    lineHeight: '1.3'
  },
  
  blockDescription: {
    fontSize: '16px',
    opacity: 0.9,
    lineHeight: '1.4',
    textShadow: '0 1px 2px rgba(0, 0, 0, 0.3)',
    marginTop: '8px'
  },
  
  playlistTag: {
    fontSize: '14px',
    opacity: 0.8,
    fontStyle: 'italic',
    marginTop: '8px',
    color: 'rgba(255, 255, 255, 0.9)'
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
    background: 'rgba(0, 0, 0, 0.2)',
    borderTop: '1px solid rgba(255, 255, 255, 0.1)',
    display: 'flex',
    justifyContent: 'center'
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

export default Category
