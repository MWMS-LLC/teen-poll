import React, { useState, useEffect } from 'react'
import { useNavigate, useSearchParams, useLocation } from 'react-router-dom'
import { useAudio } from '../contexts/AudioContext.jsx'
import HamburgerMenu from '../components/HamburgerMenu.jsx'
import Footer from '../components/Footer.jsx'
import SoundtrackService from '../services/soundtrackService.js'

const soundtrackService = new SoundtrackService()

const Soundtrack = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const location = useLocation()

  const [selectedPlaylist, setSelectedPlaylist] = useState('All Songs')
  const [showLyrics, setShowLyrics] = useState(null)
  const [favorites, setFavorites] = useState(new Set(['LRDD_01']))
  
  // Clean back navigation logic
  const getBackNavigation = () => {
    const state = location.state
    const referrer = document.referrer
    
    // Priority 1: Use React Router state if available
    if (state?.from) {
      const isCategory = state.from.includes('/category/')
      const isBlock = state.from.includes('/block/')
      
      return {
        path: state.from,
        label: isCategory ? 'Back to Category' : isBlock ? 'Back to Questions' : 'Back'
      }
    }
    
    // Priority 2: Extract from referrer URL
    const categoryMatch = referrer.match(/\/category\/([^\/\?]+)/)
    const blockMatch = referrer.match(/\/block\/([^\/\?]+)/)
    
    if (categoryMatch) {
      return { path: `/category/${categoryMatch[1]}`, label: 'Back to Category' }
    }
    
    if (blockMatch) {
      return { path: `/block/${blockMatch[1]}`, label: 'Back to Questions' }
    }
    
    // Fallback: Home page
    return { path: '/', label: 'Back to Home' }
  }
  
  const backNavigation = getBackNavigation()
  
  // Use the persistent audio context
  const { 
    audioRef, 
    currentSong, 
    isPlaying, 
    currentTime, 
    duration, 
    volume, 
    playSong, 
    togglePlayPause, 
    setVolumeLevel, 
    seekTo 
  } = useAudio()
  
  // Get soundtrack data from the service
  const [soundtracks, setSoundtracks] = useState([])
  const [playlists, setPlaylists] = useState(['All Songs'])
  
  // Load soundtracks from service on component mount
  useEffect(() => {
    const loadSoundtracks = async () => {
      try {
        await soundtrackService.loadSoundtracks()
        const songs = soundtrackService.getSoundtracks()
        const songPlaylists = soundtrackService.getPlaylists()
        setSoundtracks(songs)
        setPlaylists(songPlaylists)
        
        // Check if playlist parameter is in URL and auto-select it
        const playlistParam = searchParams.get('playlist')
        if (playlistParam && songPlaylists.includes(playlistParam)) {
          setSelectedPlaylist(playlistParam)
        }
      } catch (error) {
        console.error('Error loading soundtracks:', error)
      }
    }
    loadSoundtracks()
  }, [searchParams])

  const filteredSongs = selectedPlaylist === 'All Songs' 
    ? soundtracks 
    : soundtracks.filter(song => song.playlist.includes(selectedPlaylist))



  const handlePlaylistSelect = (playlist) => {
    setSelectedPlaylist(playlist)
  }

  const handleSongSelect = (song) => {
    console.log('Song selected:', song.title, 'File URL:', song.fileUrl)
    // Pass the full playlist so songs can auto-continue
    playSong(song, filteredSongs)
  }

  const toggleFavorite = (songId) => {
    setFavorites(prev => {
      const newFavorites = new Set(prev)
      if (newFavorites.has(songId)) {
        newFavorites.delete(songId)
      } else {
        newFavorites.add(songId)
      }
      return newFavorites
    })
  }



  const handlePrevious = () => {
    if (!currentSong || !filteredSongs.length) return
    playPreviousSong()
  }

  const handleNext = () => {
    if (!currentSong || !filteredSongs.length) return
    playNextSong()
  }

  const formatTime = (time) => {
    if (isNaN(time)) return '0:00'
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  const formatPlaylistName = (playlist) => {
    return playlist
      .replace(/_/g, ' ')  // Replace underscores with spaces
      .replace(/\b\w/g, l => l.toUpperCase())  // Capitalize first letter of each word
  }

  const handleSeek = (e) => {
    if (duration > 0) {
      const rect = e.currentTarget.getBoundingClientRect()
      const percent = (e.clientX - rect.left) / rect.width
      const newTime = percent * duration
      seekTo(newTime)
    }
  }



  return (
    <div style={styles.container}>

      

      
      {/* Hamburger Menu */}
      <HamburgerMenu />
      
      {/* Header Section */}
      <div style={styles.headerSection}>
        <div style={styles.backButton} onClick={() => navigate(backNavigation.path)}>
          ← {backNavigation.label}
        </div>
        <h1 style={styles.pageTitle}>
          {selectedPlaylist === 'All Songs' ? 'All Songs' : `${formatPlaylistName(selectedPlaylist)} Playlist`}
        </h1>
        {searchParams.get('playlist') && (
          <div style={styles.autoSelectMessage}>
            🎵 Auto-selected from category page
          </div>
        )}
      </div>

      {/* Playlists Section */}
      <div style={styles.playlistsSection}>
        <h2 style={styles.playlistsTitle}>Playlists</h2>
        <div style={styles.playlistsContainer}>
          {playlists.map((playlist) => (
            <button
              key={playlist}
              style={{
                ...styles.playlistButton,
                ...(selectedPlaylist === playlist ? styles.selectedPlaylist : {})
              }}
              onClick={() => handlePlaylistSelect(playlist)}
            >
              {formatPlaylistName(playlist)}
            </button>
          ))}
        </div>
      </div>

      {/* Music Player Controls - Positioned at the top for easy access */}
      <div style={styles.playerControls}>
        <div style={styles.timeDisplay}>
          {formatTime(currentTime)}
        </div>
        
        <div style={styles.progressBar} onClick={handleSeek}>
          <div 
            style={{
              ...styles.progressFill,
              width: `${duration > 0 ? (currentTime / duration) * 100 : 0}%`
            }}
          />
        </div>
        
        <div style={styles.timeDisplay}>
          {formatTime(duration)}
        </div>
        
        <div style={styles.controlButtons}>
          <button 
            style={styles.controlButton}
            onClick={handlePrevious}
            disabled={!currentSong}
            title="Previous Song"
          >
            ⏮️
          </button>
          <button 
            style={{
              ...styles.playButton,
              opacity: !currentSong ? 0.5 : 1,
              cursor: !currentSong ? 'not-allowed' : 'pointer'
            }}
            onClick={togglePlayPause}
            disabled={!currentSong}
            title={!currentSong ? "Select a song first" : (isPlaying ? "Pause" : "Play")}
          >
            {isPlaying ? '⏸️' : '▶️'}
          </button>
          <button 
            style={{
              ...styles.controlButton,
              opacity: !currentSong ? 0.5 : 1,
              cursor: !currentSong ? 'not-allowed' : 'pointer'
            }}
            onClick={handleNext}
            disabled={!currentSong}
            title="Next Song"
          >
            ⏭️
          </button>
        </div>
        
        {/* Volume Control */}
        <div style={styles.volumeControl}>
          <span style={styles.volumeIcon}>🔊</span>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={volume}
            onChange={(e) => {
              const newVolume = parseFloat(e.target.value)
              setVolumeLevel(newVolume)
            }}
            style={styles.volumeSlider}
          />
        </div>
      </div>

      {/* Songs List */}
      <div style={styles.songsContainer}>
        {filteredSongs.map((song) => (
          <div 
            key={song.id} 
            style={{
              ...styles.songItem,
              ...(currentSong?.id === song.id ? styles.currentSong : {})
            }}
            onClick={() => handleSongSelect(song)}
            onMouseEnter={() => setShowLyrics(song.id)}
            onMouseLeave={() => setShowLyrics(null)}
          >
            <div style={styles.songInfo}>
              <div style={styles.songTitle}>{song.title}</div>
              <div style={styles.songMood}>{song.mood}</div>
            </div>
            <button 
              style={styles.heartButton}
              onClick={(e) => {
                e.stopPropagation()
                toggleFavorite(song.id)
              }}
            >
              {favorites.has(song.id) ? '❤️' : '🤍'}
            </button>
            
            {/* Lyrics Overlay */}
            {showLyrics === song.id && (
              <div style={styles.lyricsOverlay}>
                {song.lyrics}
              </div>
            )}
          </div>
        ))}
      </div>
      
      {/* Footer */}
      <Footer />
    </div>
  )
}

// Premium styling - copied from running site
const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    background: 'linear-gradient(135deg, #1A1A2E 0%, #16213E 50%, #0F3460 100%)',
    position: 'relative',
    overflowY: 'auto',
    padding: '20px'
  },
  

  
  headerSection: {
    marginTop: '20px',
    marginBottom: '20px',
    width: '100%',
    maxWidth: '800px',
    position: 'relative'
  },
  
  backButton: {
    color: 'rgba(255, 255, 255, 0.7)',
    fontSize: '14px',
    cursor: 'pointer',
    marginBottom: '15px',
    transition: 'all 0.2s ease',
    display: 'inline-block',
    padding: '6px 12px',
    borderRadius: '15px',
    background: 'rgba(255, 255, 255, 0.1)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    alignSelf: 'flex-start',
    marginLeft: '20px'
  },
  
  pageTitle: {
    fontSize: '36px',
    fontWeight: 'bold',
    color: 'white',
    marginBottom: '15px',
    textShadow: '0 0 20px rgba(255, 255, 255, 0.3)',
    textAlign: 'center',
    marginTop: '10px'
  },
  
  autoSelectMessage: {
    fontSize: '14px',
    color: 'rgba(78, 205, 196, 0.8)',
    textAlign: 'center',
    fontStyle: 'italic',
    marginBottom: '10px'
  },
  
  playlistsSection: {
    width: '100%',
    maxWidth: '800px',
    marginBottom: '30px',
    textAlign: 'center'
  },
  
  playlistsTitle: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: 'white',
    marginBottom: '20px',
    textShadow: '0 0 15px rgba(255, 255, 255, 0.2)'
  },
  
  playlistsContainer: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '15px',
    justifyContent: 'center'
  },
  
  playlistButton: {
    padding: '12px 24px',
    fontSize: '16px',
    fontWeight: '600',
    color: 'rgba(255, 255, 255, 0.8)',
    background: 'rgba(255, 255, 255, 0.1)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '25px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    backdropFilter: 'blur(10px)'
  },
  
  selectedPlaylist: {
    background: 'rgba(78, 205, 196, 0.3)',
    border: '1px solid rgba(78, 205, 196, 0.5)',
    boxShadow: '0 0 15px rgba(78, 205, 196, 0.3)'
  },

  playerControls: {
    width: '100%',
    maxWidth: '1400px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '25px 30px',
    background: 'rgba(20, 20, 30, 0.95)',
    borderRadius: '25px 25px 0 0',
    border: '2px solid rgba(78, 205, 196, 0.4)',
    borderBottom: 'none',
    marginTop: '30px',
    marginBottom: '0px',
    boxShadow: '0 15px 40px rgba(0, 0, 0, 0.5), 0 0 30px rgba(78, 205, 196, 0.2)',
    backdropFilter: 'blur(15px)',
    position: 'fixed',
    bottom: '0px',
    left: '50%',
    transform: 'translateX(-50%)',
    zIndex: 1000
  },

  timeDisplay: {
    fontSize: '16px',
    color: 'rgba(255, 255, 255, 0.9)',
    textShadow: '0 0 5px rgba(255, 255, 255, 0.1)',
    fontWeight: '500',
    minWidth: '45px'
  },

  progressBar: {
    flex: 1,
    height: '10px',
    background: 'rgba(255, 255, 255, 0.15)',
    borderRadius: '5px',
    margin: '0 20px',
    cursor: 'pointer',
    position: 'relative',
    overflow: 'hidden'
  },

  progressFill: {
    height: '100%',
    background: 'linear-gradient(90deg, #4ECDC4 0%, #44A08D 100%)',
    borderRadius: '5px',
    transition: 'width 0.1s linear',
    boxShadow: '0 0 10px rgba(78, 205, 196, 0.5)'
  },

  controlButtons: {
    display: 'flex',
    gap: '20px',
    alignItems: 'center'
  },

  controlButton: {
    background: 'rgba(255, 255, 255, 0.1)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    borderRadius: '50%',
    width: '50px',
    height: '50px',
    fontSize: '20px',
    color: 'rgba(255, 255, 255, 0.9)',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    boxShadow: '0 4px 15px rgba(0, 0, 0, 0.3)'
  },

  playButton: {
    background: 'rgba(78, 205, 196, 0.2)',
    border: '2px solid #4ECDC4',
    borderRadius: '50%',
    width: '60px',
    height: '60px',
    fontSize: '24px',
    color: '#4ECDC4',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    boxShadow: '0 0 20px rgba(78, 205, 196, 0.3)'
  },

  volumeControl: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    marginLeft: '20px'
  },

  volumeIcon: {
    fontSize: '18px',
    color: 'rgba(255, 255, 255, 0.8)'
  },

  volumeSlider: {
    width: '80px',
    height: '6px',
    background: 'rgba(255, 255, 255, 0.2)',
    borderRadius: '3px',
    outline: 'none',
    cursor: 'pointer',
    WebkitAppearance: 'none',
    appearance: 'none'
  },

  songsContainer: {
    width: '100%',
    maxWidth: '1400px',
    marginBottom: '30px',
    borderRadius: '20px',
    overflow: 'hidden',
    boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    background: 'rgba(30, 30, 50, 0.7)'
  },

  songItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '15px 20px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
    background: 'rgba(40, 40, 60, 0.5)',
    position: 'relative'
  },

  currentSong: {
    background: 'rgba(78, 205, 196, 0.15)',
    borderLeft: '5px solid #4ECDC4',
    boxShadow: '0 0 20px rgba(78, 205, 196, 0.2)'
  },

  songInfo: {
    flex: 1,
    marginRight: '15px'
  },

  songTitle: {
    fontSize: '18px',
    fontWeight: 'bold',
    color: 'white',
    marginBottom: '5px',
    textShadow: '0 0 10px rgba(255, 255, 255, 0.2)'
  },

  songMood: {
    fontSize: '14px',
    color: 'rgba(255, 255, 255, 0.7)',
    textShadow: '0 0 5px rgba(255, 255, 255, 0.1)'
  },

  heartButton: {
    background: 'none',
    border: 'none',
    color: 'rgba(255, 255, 255, 0.7)',
    fontSize: '24px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    padding: '5px'
  },

  lyricsOverlay: {
    position: 'absolute',
    top: '100%',
    left: '50%',
    transform: 'translateX(-50%)',
    background: 'rgba(0, 0, 0, 0.9)',
    color: 'white',
    padding: '15px',
    borderRadius: '10px',
    fontSize: '14px',
    lineHeight: '1.5',
    maxWidth: '80%',
    whiteSpace: 'pre-wrap',
    zIndex: 10,
    boxShadow: '0 10px 25px rgba(0, 0, 0, 0.7)',
    border: '1px solid rgba(78, 205, 196, 0.3)'
  }
}

export default Soundtrack
