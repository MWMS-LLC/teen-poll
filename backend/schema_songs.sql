CREATE TABLE IF NOT EXISTS soundtracks (
    id SERIAL PRIMARY KEY,
    song_id TEXT UNIQUE,
    song_title TEXT,
    mood_tag TEXT,
    playlist_tag TEXT,
    lyrics_snippet TEXT,
    featured BOOLEAN,
    featured_order INT,
    file_url TEXT,
    created_at TIMESTAMP DEFAULT now()
);
