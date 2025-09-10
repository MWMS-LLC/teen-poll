#!/usr/bin/env python3
"""
Script to generate 20 users specifically for checkbox_responses table.
This script focuses on creating users and their multi-select responses.
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

def get_checkbox_questions(conn):
    """Get only checkbox questions with their options"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            q.question_code,
            q.question_text,
            q.max_select,
            q.category_id,
            c.category_name,
            q.block_number,
            q.block_text,
            q.version
        FROM questions q
        JOIN categories c ON q.category_id = c.id
        WHERE q.check_box = TRUE
        ORDER BY q.category_id, q.block_number, q.question_number
    """)
    
    questions = []
    for row in cursor.fetchall():
        question = {
            'question_code': row[0],
            'question_text': row[1],
            'max_select': row[2],
            'category_id': row[3],
            'category_name': row[4],
            'block_number': row[5],
            'block_text': row[6],
            'version': row[7]
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

def generate_checkbox_responses(user_uuid, questions):
    """Generate checkbox responses for a user across all checkbox questions"""
    checkbox_responses = []
    
    for question in questions:
        # Generate random creation date within last 30 days
        days_ago = random.randint(0, 30)
        created_at = datetime.now() - timedelta(days=days_ago)
        
        # Multi-select question - select 1 to max_select options
        max_select = question['max_select'] or 1
        num_selections = random.randint(1, min(max_select, len(question['options'])))
        selected_options = random.sample(question['options'], num_selections)
        
        for option in selected_options:
            # Random weight between 0.5 and 1.5 for variety
            weight = round(random.uniform(0.5, 1.5), 2)
            
            checkbox_response = {
                'user_uuid': user_uuid,
                'question_code': question['question_code'],
                'question_text': question['question_text'],
                'question_number': None,  # Will be filled from database
                'category_id': question['category_id'],
                'category_name': question['category_name'],
                'option_id': None,  # Will be filled from database
                'option_select': option['option_select'],
                'option_code': option['option_code'],
                'option_text': option['option_text'],
                'block_number': question['block_number'],
                'weight': weight,
                'created_at': created_at
            }
            checkbox_responses.append(checkbox_response)
    
    return checkbox_responses

def export_to_csv(users, checkbox_responses, output_dir="checkbox_users_data"):
    """Export the generated data to CSV files"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"📁 Creating output directory: {output_dir}")
    
    # Export users
    users_file = os.path.join(output_dir, "checkbox_users.csv")
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
    
    # Export checkbox responses
    checkbox_file = os.path.join(output_dir, "checkbox_responses.csv")
    logger.info(f"📝 Writing {len(checkbox_responses)} checkbox responses to {checkbox_file}")
    
    # Show progress for large files
    if len(checkbox_responses) > 100:
        logger.info("📊 Progress: Writing responses in batches...")
    
    with open(checkbox_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'user_uuid', 'question_code', 'question_text', 'question_number',
            'category_id', 'category_name', 'option_id', 'option_select',
            'option_code', 'option_text', 'block_number', 'weight', 'created_at'
        ])
        
        for i, response in enumerate(checkbox_responses, 1):
            writer.writerow([
                response['user_uuid'], response['question_code'], response['question_text'],
                response['question_number'], response['category_id'], response['category_name'],
                response['option_id'], response['option_select'], response['option_code'],
                response['option_text'], response['block_number'], response['weight'], 
                response['created_at'].isoformat()
            ])
            
            # Show progress every 100 responses
            if i % 100 == 0:
                logger.info(f"   📊 Progress: {i}/{len(checkbox_responses)} responses written...")
    
    logger.info(f"📄 Export complete!")
    logger.info(f"   📊 Users: {users_file}")
    logger.info(f"   ☑️ Checkbox responses: {checkbox_file}")
    
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
    users_file = os.path.join(csv_dir, "checkbox_users.csv")
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
    
    # Upload checkbox responses
    checkbox_file = os.path.join(csv_dir, "checkbox_responses.csv")
    logger.info(f"🗄️ Uploading checkbox responses to database...")
    
    with open(checkbox_file, 'r', encoding='utf-8') as csvfile:
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
                INSERT INTO checkbox_responses (
                    user_uuid, question_code, question_text, question_number,
                    category_id, category_name, option_id, option_select,
                    option_code, option_text, block_number, weight, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['user_uuid'], row['question_code'], row['question_text'],
                question_number, int(row['category_id']), row['category_name'],
                option_id, row['option_select'], row['option_code'],
                row['option_text'], int(row['block_number']), float(row['weight']), 
                row['created_at']
            ))
            
            response_count += 1
            
            # Show progress every 50 responses
            if i % 50 == 0 or i == total_responses:
                logger.info(f"   📊 Progress: {i}/{total_responses} responses uploaded...")
    
    logger.info(f"✅ Uploaded {response_count} checkbox responses successfully")
    
    logger.info("💾 Committing all changes to database...")
    conn.commit()
    cursor.close()
    logger.info("✅ Database transaction committed successfully!")

def main():
    """Main function to generate 20 users with checkbox responses"""
    try:
        logger.info("🚀 Starting checkbox users generation...")
        logger.info("=" * 50)
        
        # Step 1: Generate 20 fake users
        logger.info("📋 Step 1/5: Generating 20 fake users...")
        users = generate_fake_users(20)
        logger.info(f"✅ Generated {len(users)} users with birth years 2007-2012")
        
        # Step 2: Connect to database to get checkbox questions
        logger.info("🔗 Step 2/5: Connecting to database...")
        conn = get_database_connection()
        logger.info("✅ Database connection established")
        
        logger.info("📝 Step 3/5: Fetching checkbox questions and options...")
        questions = get_checkbox_questions(conn)
        logger.info(f"✅ Found {len(questions)} checkbox questions")
        
        # Show sample questions for verification
        if questions:
            logger.info("📋 Sample checkbox questions found:")
            for i, q in enumerate(questions[:3], 1):
                logger.info(f"   {i}. {q['question_code']}: {q['question_text'][:60]}...")
            if len(questions) > 3:
                logger.info(f"   ... and {len(questions) - 3} more questions")
        
        # Step 4: Generate checkbox responses for all users
        logger.info("👥 Step 4/5: Generating checkbox responses for all users...")
        all_checkbox_responses = []
        total_responses = 0
        
        for i, user in enumerate(users, 1):
            logger.info(f"👤 User {i:2d}/20: Generating responses for {user['user_uuid'][:8]}...")
            checkbox_responses = generate_checkbox_responses(user['user_uuid'], questions)
            all_checkbox_responses.extend(checkbox_responses)
            total_responses += len(checkbox_responses)
            logger.info(f"   ✅ Generated {len(checkbox_responses)} responses (Total: {total_responses})")
        
        conn.close()
        logger.info(f"✅ Response generation complete: {total_responses} total responses")
        
        # Step 5: Export to CSV
        logger.info("📄 Step 5/5: Exporting data to CSV files...")
        csv_dir = export_to_csv(users, all_checkbox_responses)
        logger.info(f"✅ CSV export complete: {csv_dir}/")
        
        # Step 6: Upload to database
        logger.info("🚀 Bonus Step: Uploading data to database...")
        conn = get_database_connection()
        upload_to_database(conn, csv_dir)
        conn.close()
        
        logger.info("\n" + "=" * 50)
        logger.info("🎉 SUCCESS: Checkbox users generation complete!")
        logger.info("=" * 50)
        logger.info(f"📊 Users created: {len(users)}")
        logger.info(f"☑️ Checkbox responses: {len(all_checkbox_responses)}")
        logger.info(f"📈 Average responses per user: {len(all_checkbox_responses) / len(users):.1f}")
        logger.info(f"📁 CSV files saved in: {csv_dir}/")
        logger.info(f"🗄️ Data uploaded to database successfully!")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
