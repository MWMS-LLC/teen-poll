#!/usr/bin/env python3
"""
Script to generate 20 users specifically for responses table (single-choice).
This script focuses on creating users and their single-choice responses.
"""

import os
import random
import uuid
import csv
from datetime import datetime, timedelta
import pg8000
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_fake_users(num_users=20):
    """Generate fake user data"""
    users = []
    for i in range(num_users):
        # Generate random birth year between 2007-2012 (teens)
        birth_year = random.randint(2007, 2012)
        
        # Generate random creation date within last 30 days
        days_ago = random.randint(0, 30)
        created_at = datetime.now() - timedelta(days=days_ago)
        
        user = {
            'user_uuid': str(uuid.uuid4()),
            'year_of_birth': birth_year,
            'created_at': created_at
        }
        users.append(user)
    
    return users

def get_single_choice_questions(conn):
    """Get only single-choice questions with their options"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            q.question_code,
            q.question_text,
            q.category_id,
            c.category_name,
            q.block_number,
            q.block_text,
            q.version
        FROM questions q
        JOIN categories c ON q.category_id = c.id
        WHERE q.check_box = FALSE
        ORDER BY q.category_id, q.block_number, q.question_number
    """)
    
    questions = []
    for row in cursor.fetchall():
        question = {
            'question_code': row[0],
            'question_text': row[1],
            'category_id': row[2],
            'category_name': row[3],
            'block_number': row[4],
            'block_text': row[5],
            'version': row[6]
        }
        
        # Get options for this question
        cursor.execute("""
            SELECT 
                option_select,
                option_code,
                option_text,
                response_message,
                companion_advice,
                tone_tag
            FROM options 
            WHERE question_code = %s 
            ORDER BY option_select
        """, (question['question_code'],))
        
        question['options'] = []
        for opt_row in cursor.fetchall():
            option = {
                'option_select': opt_row[0],
                'option_code': opt_row[1],
                'option_text': opt_row[2],
                'response_message': opt_row[3],
                'companion_advice': opt_row[4],
                'tone_tag': opt_row[5]
            }
            question['options'].append(option)
        
        questions.append(question)
    
    cursor.close()
    return questions

def generate_single_choice_responses(user_uuid, questions):
    """Generate single-choice responses for a user across all single-choice questions"""
    responses = []
    
    for question in questions:
        # Generate random creation date within last 30 days
        days_ago = random.randint(0, 30)
        created_at = datetime.now() - timedelta(days=days_ago)
        
        # Single choice question - select one option
        selected_option = random.choice(question['options'])
        
        response = {
            'user_uuid': user_uuid,
            'question_code': question['question_code'],
            'question_text': question['question_text'],
            'question_number': None,  # Will be filled from database
            'category_id': question['category_id'],
            'category_name': question['category_name'],
            'option_id': None,  # Will be filled from database
            'option_select': selected_option['option_select'],
            'option_code': selected_option['option_code'],
            'option_text': selected_option['option_text'],
            'block_number': question['block_number'],
            'created_at': created_at
        }
        responses.append(response)
    
    return responses

def export_to_csv(users, responses, output_dir="single_choice_users_data"):
    """Export the generated data to CSV files"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"📁 Creating output directory: {output_dir}")
    
    # Export users
    users_file = os.path.join(output_dir, "single_choice_users.csv")
    logger.info(f"📝 Writing {len(users)} users to {users_file}")
    with open(users_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['user_uuid', 'year_of_birth', 'created_at'])
        
        for user in users:
            writer.writerow([
                user['user_uuid'],
                user['year_of_birth'],
                user['created_at'].isoformat()
            ])
    
    # Export single-choice responses
    responses_file = os.path.join(output_dir, "single_choice_responses.csv")
    logger.info(f"📝 Writing {len(responses)} single-choice responses to {responses_file}")
    
    # Show progress for large files
    if len(responses) > 100:
        logger.info("📊 Progress: Writing responses in batches...")
    
    with open(responses_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'user_uuid', 'question_code', 'question_text', 'question_number',
            'category_id', 'category_name', 'option_id', 'option_select',
            'option_code', 'option_text', 'block_number', 'created_at'
        ])
        
        for i, response in enumerate(responses, 1):
            writer.writerow([
                response['user_uuid'], response['question_code'], response['question_text'],
                response['question_number'], response['category_id'], response['category_name'],
                response['option_id'], response['option_select'], response['option_code'],
                response['option_text'], response['block_number'], response['created_at'].isoformat()
            ])
            
            # Show progress every 100 responses
            if i % 100 == 0:
                logger.info(f"   📊 Progress: {i}/{len(responses)} responses written...")
    
    logger.info(f"📄 Export complete!")
    logger.info(f"   📊 Users: {users_file}")
    logger.info(f"   📝 Single-choice responses: {responses_file}")
    
    return output_dir

def get_database_connection():
    """Get database connection using DATABASE_URL"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise Exception("DATABASE_URL environment variable is not set!")
    
    # Parse DATABASE_URL
    parsed = urlparse(database_url)
    db_params = {
        'host': parsed.hostname or "localhost",
        'port': parsed.port or 5432,
        'database': parsed.path.lstrip("/") or "postgres",
        'user': parsed.username or "postgres",
        'password': parsed.password or "",
        'ssl_context': True
    }
    
    logger.info(f"Connecting to database: {db_params['host']}:{db_params['port']}/{db_params['database']}")
    conn = pg8000.connect(**db_params)
    return conn

def upload_to_database(conn, csv_dir):
    """Upload all data from CSV files to the database"""
    cursor = conn.cursor()
    
    # Upload users
    users_file = os.path.join(csv_dir, "single_choice_users.csv")
    logger.info(f"🗄️ Uploading {len(list(csv.DictReader(open(users_file, 'r', encoding='utf-8'))))} users to database...")
    
    with open(users_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        user_count = 0
        for row in reader:
            cursor.execute("""
                INSERT INTO users (user_uuid, year_of_birth, created_at)
                VALUES (%s, %s, %s)
            """, (row['user_uuid'], int(row['year_of_birth']), row['created_at']))
            user_count += 1
    
    logger.info(f"✅ Uploaded {user_count} users successfully")
    
    # Upload single-choice responses
    responses_file = os.path.join(csv_dir, "single_choice_responses.csv")
    logger.info(f"🗄️ Uploading single-choice responses to database...")
    
    with open(responses_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        response_count = 0
        
        # Count total responses first
        all_rows = list(reader)
        total_responses = len(all_rows)
        logger.info(f"📊 Found {total_responses} responses to upload")
        
        # Reset file pointer and upload
        csvfile.seek(0)
        next(csvfile)  # Skip header
        
        for i, row in enumerate(all_rows, 1):
            # Get question_number and option_id from database
            cursor.execute("""
                SELECT question_number FROM questions WHERE question_code = %s
            """, (row['question_code'],))
            question_number_result = cursor.fetchone()
            question_number = question_number_result[0] if question_number_result else None
            
            cursor.execute("""
                SELECT id FROM options WHERE question_code = %s AND option_select = %s
            """, (row['question_code'], row['option_select']))
            option_id_result = cursor.fetchone()
            option_id = option_id_result[0] if option_id_result else None
            
            cursor.execute("""
                INSERT INTO responses (
                    user_uuid, question_code, question_text, question_number,
                    category_id, category_name, option_id, option_select,
                    option_code, option_text, block_number, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['user_uuid'], row['question_code'], row['question_text'],
                question_number, int(row['category_id']), row['category_name'],
                option_id, row['option_select'], row['option_code'],
                row['option_text'], int(row['block_number']), row['created_at']
            ))
            
            response_count += 1
            
            # Show progress every 50 responses
            if i % 50 == 0 or i == total_responses:
                logger.info(f"   📊 Progress: {i}/{total_responses} responses uploaded...")
    
    logger.info(f"✅ Uploaded {response_count} single-choice responses successfully")
    
    logger.info("💾 Committing all changes to database...")
    conn.commit()
    cursor.close()
    logger.info("✅ Database transaction committed successfully!")

def main():
    """Main function to generate 20 users with single-choice responses"""
    try:
        logger.info("🚀 Starting single-choice users generation...")
        logger.info("=" * 50)
        
        # Step 1: Generate 20 fake users
        logger.info("📋 Step 1/5: Generating 20 fake users...")
        users = generate_fake_users(20)
        logger.info(f"✅ Generated {len(users)} users with birth years 2007-2012")
        
        # Step 2: Connect to database to get single-choice questions
        logger.info("🔗 Step 2/5: Connecting to database...")
        conn = get_database_connection()
        logger.info("✅ Database connection established")
        
        logger.info("📝 Step 3/5: Fetching single-choice questions and options...")
        questions = get_single_choice_questions(conn)
        logger.info(f"✅ Found {len(questions)} single-choice questions")
        
        # Show sample questions for verification
        if questions:
            logger.info("📋 Sample single-choice questions found:")
            for i, q in enumerate(questions[:3], 1):
                logger.info(f"   {i}. {q['question_code']}: {q['question_text'][:60]}...")
            if len(questions) > 3:
                logger.info(f"   ... and {len(questions) - 3} more questions")
        
        # Step 4: Generate single-choice responses for all users
        logger.info("👥 Step 4/5: Generating single-choice responses for all users...")
        all_responses = []
        total_responses = 0
        
        for i, user in enumerate(users, 1):
            logger.info(f"👤 User {i:2d}/20: Generating responses for {user['user_uuid'][:8]}...")
            responses = generate_single_choice_responses(user['user_uuid'], questions)
            all_responses.extend(responses)
            total_responses += len(responses)
            logger.info(f"   ✅ Generated {len(responses)} responses (Total: {total_responses})")
        
        conn.close()
        logger.info(f"✅ Response generation complete: {total_responses} total responses")
        
        # Step 5: Export to CSV
        logger.info("📄 Step 5/5: Exporting data to CSV files...")
        csv_dir = export_to_csv(users, all_responses)
        logger.info(f"✅ CSV export complete: {csv_dir}/")
        
        # Step 6: Upload to database
        logger.info("🚀 Bonus Step: Uploading data to database...")
        conn = get_database_connection()
        upload_to_database(conn, csv_dir)
        conn.close()
        
        logger.info("\n" + "=" * 50)
        logger.info("🎉 SUCCESS: Single-choice users generation complete!")
        logger.info("=" * 50)
        logger.info(f"📊 Users created: {len(users)}")
        logger.info(f"📝 Single-choice responses: {len(all_responses)}")
        logger.info(f"📈 Average responses per user: {len(all_responses) / len(users):.1f}")
        logger.info(f"📁 CSV files saved in: {csv_dir}/")
        logger.info(f"🗄️ Data uploaded to database successfully!")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

