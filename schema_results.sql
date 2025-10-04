-- PostgreSQL schema for Teen Poll MVP results tables
-- This file creates tables for storing user responses and results
-- These tables are denormalized and self-sufficient for data analysis

-- Drop tables if they exist (in reverse dependency order)
-- DROP TABLE IF EXISTS other_responses CASCADE;
-- DROP TABLE IF EXISTS checkbox_responses CASCADE;
-- DROP TABLE IF EXISTS responses CASCADE;
-- DROP TABLE IF EXISTS users CASCADE;

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    user_uuid TEXT UNIQUE NOT NULL,
    year_of_birth INTEGER NOT NULL CHECK (year_of_birth >= 1900 AND year_of_birth <= 2024),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create responses table for single-choice votes
CREATE TABLE responses (
    id SERIAL PRIMARY KEY,
    
    -- Response data
    user_uuid TEXT NOT NULL REFERENCES users(user_uuid) ON DELETE CASCADE,
    
    -- Question data (denormalized)
    question_code VARCHAR(50) NOT NULL,
    question_text TEXT NOT NULL,
    question_number INTEGER,
    
    -- Category data (denormalized) 
    category_id INTEGER,
    category_name VARCHAR(100) NOT NULL,
    category_text TEXT,
    
    -- Option data (denormalized)
    option_id INTEGER,
    option_select VARCHAR(10) NOT NULL,
    option_code VARCHAR(50) NOT NULL,
    option_text TEXT NOT NULL,
    
    -- Block data (denormalized)
    block_number INTEGER,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Prevent duplicate votes from same user on same question
    CONSTRAINT unique_user_question_response UNIQUE (user_uuid, question_code)
);

-- Create checkbox_responses table for multi-select votes
CREATE TABLE checkbox_responses (
    id SERIAL PRIMARY KEY,
    
    -- Response data
    user_uuid TEXT NOT NULL REFERENCES users(user_uuid) ON DELETE CASCADE,
    
    -- Question data (denormalized)
    question_code VARCHAR(50) NOT NULL,
    question_text TEXT NOT NULL,
    question_number INTEGER,
    
    -- Category data (denormalized)
    category_id INTEGER,
    category_name VARCHAR(100) NOT NULL,
    category_text TEXT,
    
    -- Option data (denormalized)
    option_id INTEGER,
    option_select VARCHAR(10) NOT NULL,
    option_code VARCHAR(50) NOT NULL,
    option_text TEXT NOT NULL,
    
    -- Block data (denormalized)
    block_number INTEGER,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    weight REAL DEFAULT 1.0,
    
    -- Prevent duplicate responses
    UNIQUE(user_uuid, question_code, option_select)
);

-- Create other_responses table for free-text responses
CREATE TABLE other_responses (
    id SERIAL PRIMARY KEY,
    
    -- Response data
    user_uuid TEXT NOT NULL REFERENCES users(user_uuid) ON DELETE CASCADE,
    
    -- Question data (denormalized)
    question_code VARCHAR(50) NOT NULL,
    question_text TEXT NOT NULL,
    question_number INTEGER,
    
    -- Category data (denormalized)
    category_id INTEGER,
    category_name VARCHAR(100) NOT NULL,
    category_text TEXT,
    
    -- Block data (denormalized)
    block_number INTEGER,
    
    -- Free text content
    other_text TEXT NOT NULL,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Prevent duplicate other responses from same user on same question
    CONSTRAINT unique_user_question_other UNIQUE (user_uuid, question_code)
);

-- Create indexes for better performance
CREATE INDEX idx_responses_user ON responses(user_uuid);
CREATE INDEX idx_responses_question ON responses(question_code);
CREATE INDEX idx_responses_category ON responses(category_name);
CREATE INDEX idx_responses_created ON responses(created_at);

CREATE INDEX idx_checkbox_responses_user ON checkbox_responses(user_uuid);
CREATE INDEX idx_checkbox_responses_question ON checkbox_responses(question_code);
CREATE INDEX idx_checkbox_responses_category ON checkbox_responses(category_name);
CREATE INDEX idx_checkbox_responses_created ON checkbox_responses(created_at);

CREATE INDEX idx_other_responses_user ON other_responses(user_uuid);
CREATE INDEX idx_other_responses_question ON other_responses(question_code);
CREATE INDEX idx_other_responses_category ON other_responses(category_name);
CREATE INDEX idx_other_responses_created ON other_responses(created_at);

CREATE INDEX idx_users_uuid ON users(user_uuid);
CREATE INDEX idx_users_year ON users(year_of_birth);

