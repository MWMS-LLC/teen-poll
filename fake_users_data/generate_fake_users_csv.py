#!/usr/bin/env python3
"""
Production script to generate fake users and responses to CSV files first,
then upload them all at once to the remote database.
This approach is more efficient than inserting one by one.
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

def get_questions_with_options(conn):
    """Get all questions with their options and metadata"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            q.question_code,
            q.question_text,
            q.check_box,
            q.max_select,
            q.category_id,
            c.category_name,
            q.block_number,
            q.block_text,
            q.color_code,
            q.version
        FROM questions q
        JOIN categories c ON q.category_id = c.id
        ORDER BY q.category_id, q.block_number, q.question_number
    """)
    
    questions = []
    for row in cursor.fetchall():
        question = {
            'question_code': row[0],
            'question_text': row[1],
            'check_box': row[2],
            'max_select': row[3],
            'category_id': row[4],
            'category_name': row[5],
            'block_number': row[6],
            'block_text': row[7],
            'color_code': row[8],
            'version': row[9]
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

def generate_realistic_responses(user_uuid, questions):
    """Generate realistic responses for a user across all questions"""
    responses = []
    checkbox_responses = []
    
    for question in questions:
        # Generate random creation date within last 30 days
        days_ago = random.randint(0, 30)
        created_at = datetime.now() - timedelta(days=days_ago)
        
        if question['check_box']:
            # Multi-select question
            max_select = question['max_select'] or 1
            num_selections = random.randint(1, min(max_select, len(question['options'])))
            selected_options = random.sample(question['options'], num_selections)
            
            for option in selected_options:
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
                    'weight': 1.0,
                    'created_at': created_at
                }
                checkbox_responses.append(checkbox_response)
        else:
            # Single choice question
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
    
    return responses, checkbox_responses

def export_to_csv(users, responses, checkbox_responses, output_dir="fake_users_data"):
    """Export the generated data to CSV files"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Export users
    users_file = os.path.join(output_dir, "fake_users.csv")
    with open(users_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['user_uuid', 'year_of_birth', 'created_at'])
        
        for user in users:
            writer.writerow([
                user['user_uuid'],
                user['year_of_birth'],
                user['created_at'].isoformat()
            ])
    
    # Export single choice responses
    responses_file = os.path.join(output_dir, "fake_responses.csv")
    with open(responses_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'user_uuid', 'question_code', 'question_text', 'question_number',
            'category_id', 'category_name', 'option_id', 'option_select',
            'option_code', 'option_text', 'block_number', 'created_at'
        ])
        
        for response in responses:
            writer.writerow([
                response['user_uuid'], response['question_code'], response['question_text'],
                response['question_number'], response['category_id'], response['category_name'],
                response['option_id'], response['option_select'], response['option_code'],
                response['option_text'], response['block_number'], response['created_at'].isoformat()
            ])
    
    # Export checkbox responses
    checkbox_file = os.path.join(output_dir, "fake_checkbox_responses.csv")
    with open(checkbox_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'user_uuid', 'question_code', 'question_text', 'question_number',
            'category_id', 'category_name', 'option_id', 'option_select',
            'option_code', 'option_text', 'block_number', 'weight', 'created_at'
        ])
        
        for response in checkbox_responses:
            writer.writerow([
                response['user_uuid'], response['question_code'], response['question_text'],
                response['question_number'], response['category_id'], response['category_name'],
                response['option_id'], response['option_select'], response['option_code'],
                response['option_text'], response['block_number'], response['weight'], 
                response['created_at'].isoformat()
            ])
    
    logger.info(f"📄 Exported data to {output_dir}/")
    logger.info(f"   - Users: {users_file}")
    logger.info(f"   - Responses: {responses_file}")
    logger.info(f"   - Checkbox responses: {checkbox_file}")
    
    return output_dir

def get_production_db_connection():
    """Get database connection for production using DATABASE_URL"""
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
    
    logger.info(f"Connecting to production database: {db_params['host']}:{db_params['port']}/{db_params['database']}")
    conn = pg8000.connect(**db_params)
    return conn

def upload_from_csv(conn, csv_dir):
    """Upload all data from CSV files to the database"""
    cursor = conn.cursor()
    
    # Upload users
    users_file = os.path.join(csv_dir, "fake_users.csv")
    with open(users_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cursor.execute("""
                INSERT INTO users (user_uuid, year_of_birth, created_at)
                VALUES (%s, %s, %s)
            """, (row['user_uuid'], int(row['year_of_birth']), row['created_at']))
    
    logger.info("✅ Uploaded users")
    
    # Upload single choice responses
    responses_file = os.path.join(csv_dir, "fake_responses.csv")
    with open(responses_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
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
    
    logger.info("✅ Uploaded single choice responses")
    
    # Upload checkbox responses
    checkbox_file = os.path.join(csv_dir, "fake_checkbox_responses.csv")
    with open(checkbox_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
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
    
    logger.info("✅ Uploaded checkbox responses")
    
    conn.commit()
    cursor.close()

def main():
    """Main function to generate fake data to CSV and upload to production"""
    try:
        logger.info("🚀 Starting fake data generation to CSV...")
        
        # Step 1: Generate fake data
        logger.info("Generating 20 fake users...")
        users = generate_fake_users(20)
        
        # Step 2: Connect to production database to get questions
        logger.info("Connecting to production database to get questions...")
        conn = get_production_db_connection()
        
        logger.info("Getting all questions with options...")
        questions = get_questions_with_options(conn)
        logger.info(f"📝 Found {len(questions)} questions")
        
        # Step 3: Generate responses for all users
        logger.info("Generating responses for all users...")
        all_responses = []
        all_checkbox_responses = []
        
        for i, user in enumerate(users, 1):
            logger.info(f"👤 Generating responses for user {i}/20 ({user['user_uuid'][:8]}...)")
            responses, checkbox_responses = generate_realistic_responses(user['user_uuid'], questions)
            
            all_responses.extend(responses)
            all_checkbox_responses.extend(checkbox_responses)
        
        conn.close()
        
        # Step 4: Export to CSV
        logger.info("Exporting data to CSV files...")
        csv_dir = export_to_csv(users, all_responses, all_checkbox_responses)
        
        # Step 5: Upload to production database
        logger.info("Uploading data to production database...")
        conn = get_production_db_connection()
        upload_from_csv(conn, csv_dir)
        conn.close()
        
        logger.info("\n🎉 Successfully generated and uploaded fake data!")
        logger.info(f"📊 Users: {len(users)}")
        logger.info(f"📝 Single responses: {len(all_responses)}")
        logger.info(f"☑️ Checkbox responses: {len(all_checkbox_responses)}")
        logger.info(f"🎯 Total responses: {len(all_responses) + len(all_checkbox_responses)}")
        logger.info(f"📈 Average responses per user: {(len(all_responses) + len(all_checkbox_responses)) / len(users):.1f}")
        logger.info(f"📁 CSV files saved in: {csv_dir}/")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
