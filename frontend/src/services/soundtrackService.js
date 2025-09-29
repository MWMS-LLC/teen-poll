// Soundtrack service for managing music data and playlist integration
const API_BASE = import.meta.env.VITE_API_BASE;

class SoundtrackService {
  constructor() {
    this.soundtracks = []
    this.playlists = []
    this.loaded = false
  }

  // Load soundtrack data from backend API
  async loadSoundtracks() {
    try {
      // Fetch soundtracks from backend API
      const response = await fetch(`${API_BASE}/api/soundtracks`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      console.log('Loaded soundtracks from API:', data.soundtracks.length)
      
      // Transform the data to match our component's format
      this.soundtracks = data.soundtracks.map(song => ({
        id: song.song_id,
        title: song.song_title,
        mood: song.mood_tag,
        playlist: song.playlist_tag,
        lyrics: song.lyrics_snippet,
        featured: song.featured,
        featuredOrder: song.featured_order || 0,
        fileUrl: song.file_url
      }))
      
      // Load playlists from API
      await this.loadPlaylists()
      
      this.loaded = true
      return this.soundtracks
    } catch (error) {
      console.error('Error loading soundtracks from API:', error)
      // Fallback to minimal data if API fails
      return this.getFallbackData()
    }
  }
  
  // Load playlists from backend API
  async loadPlaylists() {
    try {
      const response = await fetch(`${API_BASE}/api/soundtracks/playlists`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      this.playlists = [];

      // Normalize: split comma-separated items and trim
      data.playlists.forEach(item => {
        item.split(',').map(p => p.trim()).forEach(playlist => {
          if (!this.playlists.includes(playlist)) {
            this.playlists.push(playlist);
          }
        });
      });

    } catch (error) {
      console.error('Error loading playlists from API:', error);

      // Fallback: extract from soundtracks
      this.playlists = ['All Songs'];
      this.soundtracks.forEach(song => {
        if (song.playlist) {
          const songPlaylists = song.playlist.split(',').map(p => p.trim());
          songPlaylists.forEach(playlist => {
            if (!this.playlists.includes(playlist)) {
              this.playlists.push(playlist);
            }
          });
        }
      });
    }

    // ✅ Keep "All Songs" at the top, sort the rest alphabetically
    const hasAllSongs = this.playlists.includes('All Songs');
    let sorted = this.playlists.filter(p => p !== 'All Songs').sort((a, b) => a.localeCompare(b));
    this.playlists = hasAllSongs ? ['All Songs', ...sorted] : sorted;
  }

  
  // Fallback data if CSV loading fails
  getFallbackData() {
    return [
      {
        id: "STR_01",
        title: "Spark Still Rise (Male Rap)",
        mood: "bitter, believing",
        playlist: "Spiral, Believe, Lowkey",
        lyrics: "You ain't gotta fake the fire. Even sparks can light the sky.",
        featured: true,
        featuredOrder: 1,
        fileUrl: "https://myworld-soundtrack.s3.us-east-2.amazonaws.com/myworld_soundtrack/sparks-still-rise.mp3"
      }
    ]
  }

  // Get all soundtracks
  getSoundtracks() {
    return this.soundtracks
  }

  // Get all playlists
  getPlaylists() {
    return this.playlists
  }

  // Get songs by playlist
  getSongsByPlaylist(playlist) {
    if (playlist === 'All Songs') {
      return this.soundtracks
    }
    return this.soundtracks.filter(song => 
      song.playlist.includes(playlist)
    )
  }

  // Get songs by mood
  getSongsByMood(mood) {
    return this.soundtracks.filter(song => 
      song.mood.toLowerCase().includes(mood.toLowerCase())
    )
  }

  // Get featured songs
  getFeaturedSongs() {
    return this.soundtracks
      .filter(song => song.featured)
      .sort((a, b) => a.featuredOrder - b.featuredOrder)
  }

  // Get song by ID
  getSongById(id) {
    return this.soundtracks.find(song => song.id === id)
  }

  // Search songs by text
  searchSongs(query) {
    const lowerQuery = query.toLowerCase()
    return this.soundtracks.filter(song => 
      song.title.toLowerCase().includes(lowerQuery) ||
      song.lyrics.toLowerCase().includes(lowerQuery) ||
      song.mood.toLowerCase().includes(lowerQuery) ||
      song.playlist.toLowerCase().includes(lowerQuery)
    )
  }

  // Get smart song recommendation based on question text and block code
  getSmartSongRecommendation(questionText, blockCode) {
    if (!this.soundtracks.length) return null
    
    // Simple recommendation logic - can be enhanced later
    const questionLower = questionText.toLowerCase()
    
    // Look for mood matches
    const moodMatches = this.soundtracks.filter(song => 
      song.mood && song.mood.toLowerCase().includes('believing') ||
      song.mood && song.mood.toLowerCase().includes('inspiring')
    )
    
    if (moodMatches.length > 0) {
      // Return a random mood-matching song
      return moodMatches[Math.floor(Math.random() * moodMatches.length)]
    }
    
    // Fallback to a random featured song
    const featuredSongs = this.getFeaturedSongs()
    if (featuredSongs.length > 0) {
      return featuredSongs[0]
    }
    
    // Last resort - return first available song
    return this.soundtracks[0]
  }
}

export default SoundtrackService
