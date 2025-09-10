-- Production Database Setup Script
-- Run this in your production database to populate the missing tables

-- First, let's check what we have
SELECT 'Current tables:' as info;
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;

-- Check if options table exists and has data
SELECT 'Options table status:' as info;
SELECT COUNT(*) as options_count FROM options;

-- Check if categories table has data
SELECT 'Categories table status:' as info;
SELECT COUNT(*) as categories_count FROM categories;

-- Check if questions table has data
SELECT 'Questions table status:' as info;
SELECT COUNT(*) as questions_count FROM questions;

-- Check if blocks table has data
SELECT 'Blocks table status:' as info;
SELECT COUNT(*) as blocks_count FROM blocks;

-- If any of these are empty, you'll need to run the import_setup.py script
-- or manually insert the data from the CSV files

-- To manually insert data, you would need to:
-- 1. Copy the CSV files to your production environment
-- 2. Use COPY commands or INSERT statements to populate the tables
-- 3. Ensure all foreign key relationships are maintained

-- For now, let's see what's missing:
SELECT 'Missing data summary:' as info;
SELECT 
    CASE WHEN (SELECT COUNT(*) FROM categories) = 0 THEN 'Categories table is empty' ELSE 'Categories table has data' END as categories_status,
    CASE WHEN (SELECT COUNT(*) FROM blocks) = 0 THEN 'Blocks table is empty' ELSE 'Blocks table has data' END as blocks_status,
    CASE WHEN (SELECT COUNT(*) FROM questions) = 0 THEN 'Questions table is empty' ELSE 'Questions table has data' END as questions_status,
    CASE WHEN (SELECT COUNT(*) FROM options) = 0 THEN 'Options table is empty' ELSE 'Options table has data' END as options_status;

