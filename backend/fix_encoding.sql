-- Fix UTF-8 encoding issues in setup tables
-- Replace ??? with ' in question text and option text

-- Fix questions table
UPDATE questions 
SET question_text = REPLACE(question_text, '???', '''')
WHERE question_text LIKE '%???%';

-- Fix options table  
UPDATE options
SET option_text = REPLACE(option_text, '???', '''')
WHERE option_text LIKE '%???%';

-- Fix blocks table
UPDATE blocks
SET block_text = REPLACE(block_text, '???', '''')
WHERE block_text LIKE '%???%';

-- Fix categories table
UPDATE categories
SET category_text = REPLACE(category_text, '???', '''')
WHERE category_text LIKE '%???%';

-- Verify the fixes
SELECT 'Questions fixed:' as table_name, COUNT(*) as fixed_count
FROM questions 
WHERE question_text LIKE '%???%'
UNION ALL
SELECT 'Options fixed:', COUNT(*)
FROM options 
WHERE option_text LIKE '%???%'
UNION ALL
SELECT 'Blocks fixed:', COUNT(*)
FROM blocks 
WHERE block_text LIKE '%???%'
UNION ALL
SELECT 'Categories fixed:', COUNT(*)
FROM categories 
WHERE category_text LIKE '%???%';
