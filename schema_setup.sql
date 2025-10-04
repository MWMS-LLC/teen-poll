-- PostgreSQL schema for Teen Poll MVP setup tables
-- This file creates the core structure for categories, blocks, questions, and options

-- Drop tables if they exist (in reverse dependency order)
DROP TABLE IF EXISTS options CASCADE;
DROP TABLE IF EXISTS questions CASCADE;
DROP TABLE IF EXISTS blocks CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS soundtracks CASCADE;

-- Create categories table (matches your CSV exactly)
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    category_text TEXT,
    day_of_week INTEGER[],
    description TEXT,
    category_text_long TEXT,
    version VARCHAR(20),
    uuid TEXT UNIQUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create blocks table (matches your CSV exactly)
CREATE TABLE blocks (
    id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    block_number INTEGER NOT NULL,
    block_code VARCHAR(50) UNIQUE NOT NULL,
    block_text TEXT NOT NULL,
    version VARCHAR(20),
    uuid TEXT UNIQUE,
    category_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_block_per_category UNIQUE (category_id, block_number)
);

-- Create questions table (matches your CSV exactly)
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    question_code VARCHAR(50) UNIQUE NOT NULL,
    question_number INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    check_box BOOLEAN DEFAULT FALSE,
    max_select INTEGER DEFAULT 1,
    block_number INTEGER NOT NULL,
    block_text TEXT,
    is_start_question BOOLEAN DEFAULT FALSE,
    parent_question_id INTEGER,
    color_code TEXT,
    version VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_question_per_block UNIQUE (category_id, block_number, question_number)
);

-- Create options table (matches your CSV exactly)
CREATE TABLE options (
    id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    question_code VARCHAR(50) NOT NULL,
    question_number INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    check_box BOOLEAN DEFAULT FALSE,
    block_number INTEGER NOT NULL,
    block_text TEXT NOT NULL,
    option_select VARCHAR(10) NOT NULL,
    option_code VARCHAR(50) NOT NULL,
    option_text TEXT NOT NULL,
    response_message TEXT,
    companion_advice TEXT,
    tone_tag TEXT,
    next_question_id INTEGER,
    version VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_option_per_question UNIQUE (question_code, option_select)
);

-- Create indexes for better performance
CREATE INDEX idx_categories_sort ON categories(sort_order);
CREATE INDEX idx_blocks_category ON blocks(category_id);
CREATE INDEX idx_blocks_code ON blocks(block_code);
CREATE INDEX idx_questions_category ON questions(category_id);
CREATE INDEX idx_questions_block ON questions(block_number);
CREATE INDEX idx_questions_code ON questions(question_code);
CREATE INDEX idx_options_category ON options(category_id);
CREATE INDEX idx_options_question ON options(question_code);
CREATE INDEX idx_options_select ON options(option_select);

-- Create soundtracks table for music playlist functionality
CREATE TABLE soundtracks (
    id SERIAL PRIMARY KEY,
    song_id VARCHAR(50) UNIQUE NOT NULL,
    song_title VARCHAR(255) NOT NULL,
    mood_tag TEXT,
    playlist_tag TEXT,
    lyrics_snippet TEXT,
    featured BOOLEAN DEFAULT FALSE,
    featured_order INTEGER DEFAULT 0,
    file_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for soundtracks
CREATE INDEX idx_soundtracks_featured ON soundtracks(featured, featured_order);
CREATE INDEX idx_soundtracks_playlist ON soundtracks USING GIN(to_tsvector('english', playlist_tag));
CREATE INDEX idx_soundtracks_mood ON soundtracks USING GIN(to_tsvector('english', mood_tag));

