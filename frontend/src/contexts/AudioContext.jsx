import React, { createContext, useContext, useRef, useState, useEffect, useCallback } from 'react'

const AudioContext = createContext()

export const useAudio = () => {
  const context = useContext(AudioContext)
  if (!context) {
    throw new Error('useAudio must be used within an AudioProvider')
  }
  return context
}

export const AudioProvider = ({ children }) => {
  // ===== THEME SONG SYSTEM (Completely Separate) =====
  const themeAudioRef = useRef(null)
  const [isThemeSongOn, setIsThemeSongOn] = useState(true)
  const [themeSong, setThemeSong] = useState(null)
  const [hasAutoPlayed, setHasAutoPlayed] = useState(false)

  // ===== SOUNDTRACK SYSTEM (Completely Separate) =====
  const soundtrackAudioRef = useRef(null)
  const [currentSong, setCurrentSong] = useState(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolume] = useState(1)
  const [playlist, setPlaylist] = useState([])
  const [currentSongIndex, setCurrentSongIndex] = useState(0)

  // ===== THEME SONG FUNCTIONS (Never touch soundtrack) =====
  
  // Initialize theme song
  useEffect(() => {
    const defaultThemeSong = {
      id: "THM_1",
      title: "Theme Song (Male Inspiring Rap)",
      fileUrl: "https://myworld-soundtrack.s3.us-east-2.amazonaws.com/myworld_soundtrack/Theme+(Male+Inspiring+Rap).mp3"
    }
    setThemeSong(defaultThemeSong)
    
    // Check if theme song was already played this session
    const alreadyPlayed = localStorage.getItem('themeSongPlayed') === 'true'
    setHasAutoPlayed(alreadyPlayed)
    
    console.log('🎵 Theme song system initialized', alreadyPlayed ? '(already played this session)' : '(ready to play)')
  }, [])

  // Clear theme song state when component unmounts (new session)
  useEffect(() => {
    return () => {
      localStorage.removeItem('themeSongPlayed')
    }
  }, [])

  // Auto-play theme song once after user interaction
  useEffect(() => {
    if (isThemeSongOn && themeSong && !hasAutoPlayed) {
      console.log('🎵 Theme song ready to play after user interaction')
    }
  }, [isThemeSongOn, themeSong, hasAutoPlayed])

  // Function to trigger theme song after user interaction (only once per session)
  const triggerThemeSong = useCallback(() => {
    if (isThemeSongOn && themeSong && !hasAutoPlayed) {
      console.log('🎵 Triggering theme song after user interaction')
      playThemeSong()
      setHasAutoPlayed(true)
      // Store in localStorage so it persists across navigation
      localStorage.setItem('themeSongPlayed', 'true')
    }
  }, [isThemeSongOn, themeSong, hasAutoPlayed])

  const playThemeSong = () => {
    if (!themeAudioRef.current || !themeSong) return
    
    console.log('🎵 Playing theme song')
    themeAudioRef.current.src = themeSong.fileUrl
    themeAudioRef.current.load()
    themeAudioRef.current.play().then(() => {
      console.log('🎵 Theme song playing successfully')
    }).catch(error => {
      console.error('❌ Theme song error:', error)
    })
  }

  const stopThemeSong = () => {
    if (themeAudioRef.current) {
      themeAudioRef.current.pause()
      themeAudioRef.current.currentTime = 0
      console.log('🎵 Theme song stopped')
    }
  }

  const toggleThemeSong = () => {
    setIsThemeSongOn(prev => {
      const newState = !prev
      if (newState) {
        console.log('🎵 Theme song turned ON')
        // If turning on and it was already played, allow it to play again
        if (hasAutoPlayed) {
          playThemeSong()
        }
      } else {
        console.log('🎵 Theme song turned OFF')
        stopThemeSong()
      }
      return newState
    })
  }

  // Function to reset theme song state (allow it to play again)
  const resetThemeSong = () => {
    setHasAutoPlayed(false)
    localStorage.removeItem('themeSongPlayed')
    console.log('🎵 Theme song state reset - can play again')
  }

  // ===== SOUNDTRACK FUNCTIONS (Never touch theme song) =====

  const playSong = (song, songList = []) => {
    if (!soundtrackAudioRef.current) return
    
    console.log('🎵 Playing soundtrack:', song.title)
    
    // Stop any current soundtrack
    soundtrackAudioRef.current.pause()
    soundtrackAudioRef.current.currentTime = 0
    
    // Set up new soundtrack
    setCurrentSong(song)
    setIsPlaying(false)
    
    if (songList.length > 0) {
      setPlaylist(songList)
      const songIndex = songList.findIndex(s => s.id === song.id)
      setCurrentSongIndex(songIndex >= 0 ? songIndex : 0)
    }
    
    // Play the soundtrack
    soundtrackAudioRef.current.src = song.fileUrl
    soundtrackAudioRef.current.volume = volume
    soundtrackAudioRef.current.load()
    
    soundtrackAudioRef.current.play().then(() => {
      console.log('✅ Soundtrack started playing')
      setIsPlaying(true)
    }).catch(error => {
      console.error('❌ Soundtrack error:', error)
      setIsPlaying(false)
    })
  }

  const togglePlayPause = () => {
    if (!currentSong || !soundtrackAudioRef.current) return
    
    if (isPlaying) {
      soundtrackAudioRef.current.pause()
      setIsPlaying(false)
    } else {
      soundtrackAudioRef.current.play().then(() => {
        setIsPlaying(true)
      }).catch(error => {
        console.error('Error playing soundtrack:', error)
        setIsPlaying(false)
      })
    }
  }

  const setVolumeLevel = (newVolume) => {
    setVolume(newVolume)
    if (soundtrackAudioRef.current) {
      soundtrackAudioRef.current.volume = newVolume
    }
  }

  const seekTo = (time) => {
    if (soundtrackAudioRef.current && duration > 0) {
      soundtrackAudioRef.current.currentTime = time
      setCurrentTime(time)
    }
  }

  const playNextSong = useCallback(() => {
    if (playlist.length === 0) return
    
    const nextIndex = (currentSongIndex + 1) % playlist.length
    setCurrentSongIndex(nextIndex)
    const nextSong = playlist[nextIndex]
    setCurrentSong(nextSong)
    
    if (soundtrackAudioRef.current) {
      soundtrackAudioRef.current.src = nextSong.fileUrl
      soundtrackAudioRef.current.load()
      soundtrackAudioRef.current.play().then(() => {
        setIsPlaying(true)
        setCurrentTime(0)
      }).catch(error => {
        console.error('Error playing next song:', error)
        setIsPlaying(false)
      })
    }
  }, [playlist, currentSongIndex])

  const playPreviousSong = () => {
    if (playlist.length === 0) return
    
    const prevIndex = currentSongIndex === 0 ? playlist.length - 1 : currentSongIndex - 1
    setCurrentSongIndex(prevIndex)
    const prevSong = playlist[prevIndex]
    setCurrentSong(prevSong)
    
    if (soundtrackAudioRef.current) {
      soundtrackAudioRef.current.src = prevSong.fileUrl
      soundtrackAudioRef.current.load()
      soundtrackAudioRef.current.play().then(() => {
        setIsPlaying(true)
        setCurrentTime(0)
      }).catch(error => {
        console.error('Error playing previous song:', error)
        setIsPlaying(false)
      })
    }
  }

  const setPlaylistSongs = (songs) => {
    setPlaylist(songs)
    setCurrentSongIndex(0)
  }

  // ===== AUDIO EVENT HANDLERS (Separate for each system) =====

  // Theme song audio events
  useEffect(() => {
    const audio = themeAudioRef.current
    if (!audio) return

    const handleEnded = () => {
      console.log('🎵 Theme song ended')
    }
    const handleError = (e) => {
      console.error('🎵 Theme song error:', e)
    }

    audio.addEventListener('ended', handleEnded)
    audio.addEventListener('error', handleError)

    return () => {
      audio.removeEventListener('ended', handleEnded)
      audio.removeEventListener('error', handleError)
    }
  }, [])

  // Soundtrack audio events
  useEffect(() => {
    const audio = soundtrackAudioRef.current
    if (!audio) return

    const handleTimeUpdate = () => setCurrentTime(audio.currentTime)
    const handleLoadedMetadata = () => setDuration(audio.duration)
    const handleEnded = () => {
      setIsPlaying(false)
      setCurrentTime(0)
      setTimeout(() => playNextSong(), 100)
    }
    const handleError = (e) => {
      console.error('Soundtrack error:', e)
      setIsPlaying(false)
    }

    audio.addEventListener('timeupdate', handleTimeUpdate)
    audio.addEventListener('loadedmetadata', handleLoadedMetadata)
    audio.addEventListener('ended', handleEnded)
    audio.addEventListener('error', handleError)

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate)
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata)
      audio.removeEventListener('ended', handleEnded)
      audio.removeEventListener('error', handleError)
    }
  }, [playNextSong])

  const value = {
    // Theme song system
    isThemeSongOn,
    themeSong,
    hasAutoPlayed,
    toggleThemeSong,
    playThemeSong,
    stopThemeSong,
    triggerThemeSong,
    resetThemeSong,
    
    // Soundtrack system
    audioRef: soundtrackAudioRef, // Keep for backward compatibility
    currentSong,
    isPlaying,
    currentTime,
    duration,
    volume,
    playlist,
    currentSongIndex,
    playSong,
    togglePlayPause,
    setVolumeLevel,
    seekTo,
    setPlaylistSongs,
    playNextSong,
    playPreviousSong,
    
    // Backward compatibility functions
    autoPlayThemeSong: () => {
      console.log('🎵 autoPlayThemeSong called (backward compatibility)')
      if (isThemeSongOn && !hasAutoPlayed) {
        playThemeSong()
        setHasAutoPlayed(true)
      }
    }
  }

  return (
    <AudioContext.Provider value={value}>
      {/* TWO COMPLETELY SEPARATE AUDIO ELEMENTS */}
      
      {/* Theme song audio - never interferes with soundtrack */}
      <audio 
        ref={themeAudioRef} 
        preload="metadata" 
        style={{display: 'none'}}
        onLoadStart={() => console.log('🎵 Theme song audio element ready')}
      />
      
      {/* Soundtrack audio - never interferes with theme song */}
      <audio 
        ref={soundtrackAudioRef} 
        preload="metadata" 
        style={{display: 'none'}}
        onLoadStart={() => console.log('🎵 Soundtrack audio element ready')}
      />
      
      {children}
    </AudioContext.Provider>
  )
}
