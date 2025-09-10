

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pg8000
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import os
from urllib.parse import urlparse
import threading
import queue
from contextlib import contextmanager

# Configure logging - force it to be very verbose
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger(__name__)

# Force print statements to flush immediately
import sys
sys.stdout.flush()
sys.stderr.flush()

# Initialize FastAPI app
app = FastAPI(
    title="My World My Say Teen API",
    description="Teen API for teen.myworldmysay.com - Teen Poll System",
    version="1.0.0"
)

# Add startup message
logger.info("🚀 MY WORLD MY SAY TEEN API STARTING UP!")
print("🚀 MY WORLD MY SAY TEEN API STARTING UP!")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://192.168.87.244:5174",
        "http://192.168.87.244:5175",
        "https://myworld-teen-front.s3-website.us-east-2.amazonaws.com",
        "https://teen.myworldmysay.com",
        "https://myworldmysay.com",
        "https://www.myworldmysay.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple connection pool using pg8000
class SimpleConnectionPool:
    def __init__(self, max_connections=5):
        self.max_connections = max_connections
        self.pool = queue.Queue(maxsize=max_connections)
        self.active_connections = 0
        self.lock = threading.Lock()
        self.db_params = None
        
    def _create_connection(self):
        """Create a new database connection"""
        if not self.db_params:
            # Use individual environment variables for AWS App Runner
            host = os.getenv("DB_HOST")
            port = int(os.getenv("DB_PORT", "5432"))
            database = os.getenv("DB_NAME")
            user = os.getenv("DB_USER")
            password = os.getenv("DB_PASSWORD")
            
            print(f"🔍 DEBUG: DB_HOST = {host}")
            logger.info(f"🔍 DEBUG: DB_HOST = {host}")
            
            if not all([host, database, user, password]):
                raise Exception("Database environment variables are not set!")
            
            self.db_params = {
                'host': host,
                'port': port,
                'database': database,
                'user': user,
                'password': password,
                'ssl_context': True
            }
            logger.info(f"Database params initialized for host: {self.db_params['host']}")
        
        return pg8000.connect(**self.db_params)
    
    def get_connection(self):
        """Get a connection from the pool"""
        try:
            # Try to get an existing connection from the pool
            return self.pool.get_nowait()
        except queue.Empty:
            # No connections available, create a new one if under limit
            with self.lock:
                if self.active_connections < self.max_connections:
                    self.active_connections += 1
                    try:
                        conn = self._create_connection()
                        logger.info(f"Created new teen site connection. Active: {self.active_connections}")
                        return conn
                    except Exception as e:
                        self.active_connections -= 1
                        raise e
                else:
                    # Wait for a connection to become available
                    logger.info("Production pool full, waiting for connection...")
                    return self.pool.get(timeout=30)
    
    def return_connection(self, conn):
        """Return a connection to the pool"""
        try:
            # Test if connection is still valid
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            # Connection is good, return to pool
            self.pool.put_nowait(conn)
        except:
            # Connection is bad, close it and decrease counter
            try:
                conn.close()
            except:
                pass
            with self.lock:
                self.active_connections -= 1
            logger.info(f"Closed bad production connection. Active: {self.active_connections}")

# Global connection pool
connection_pool = SimpleConnectionPool(max_connections=5)

@contextmanager
def get_db_connection():
    """Get database connection from the pool"""
    conn = None
    try:
        conn = connection_pool.get_connection()
        yield conn
    finally:
        if conn:
            connection_pool.return_connection(conn)

# Database query execution function with connection pooling
def execute_query(query: str, params: tuple = None, fetch: bool = True):
    """Execute database query using connection pool"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                # Get column names
                columns = [desc[0] for desc in cursor.description]
                # Fetch all rows and convert to list of dicts
                rows = cursor.fetchall()
                results = []
                for row in rows:
                    results.append(dict(zip(columns, row)))
                return results
            else:
                conn.commit()
                return True
                
    except Exception as e:
        logger.error(f"Database operation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database operation failed: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "My World My Say Main API is running", "status": "ok"}

@app.get("/health")
async def health():
    """Health check endpoint that doesn't require database"""
    return {"status": "healthy", "timestamp": str(datetime.now())}

@app.on_event("startup")
async def startup_event():
    """Initialize database connection pool on startup"""
    # The original code had db_pool, but it's removed.
    # This function is kept as it was not explicitly removed by the new_code.
    # However, the new_code removed the db_pool logic.
    # This function will now effectively do nothing if db_pool is removed.
    pass

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection pool on shutdown"""
    # The original code had db_pool, but it's removed.
    # This function is kept as it was not explicitly removed by the new_code.
    # However, the new_code removed the db_pool logic.
    # This function will now effectively do nothing if db_pool is removed.
    pass

# Request validation functions (replacing pydantic)
def validate_user_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate user creation request"""
    if not isinstance(data.get('user_uuid'), str):
        raise HTTPException(status_code=400, detail="user_uuid must be a string")
    if not isinstance(data.get('year_of_birth'), int):
        raise HTTPException(status_code=400, detail="year_of_birth must be an integer")
    return data

def validate_vote_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate vote request"""
    if not isinstance(data.get('question_code'), str):
        raise HTTPException(status_code=400, detail="question_code must be a string")
    if not isinstance(data.get('option_select'), str):
        raise HTTPException(status_code=400, detail="option_select must be a string")
    if not isinstance(data.get('user_uuid'), str):
        raise HTTPException(status_code=400, detail="user_uuid must be a string")
    return data

def validate_checkbox_vote_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate checkbox vote request"""
    if not isinstance(data.get('question_code'), str):
        raise HTTPException(status_code=400, detail="question_code must be a string")
    if not isinstance(data.get('option_selects'), list):
        raise HTTPException(status_code=400, detail="option_selects must be a list")
    if not isinstance(data.get('user_uuid'), str):
        raise HTTPException(status_code=400, detail="user_uuid must be a string")
    return data

def validate_other_request(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate other text request"""
    if not isinstance(data.get('question_code'), str):
        raise HTTPException(status_code=400, detail="question_code must be a string")
    if not isinstance(data.get('user_uuid'), str):
        raise HTTPException(status_code=400, detail="user_uuid must be a string")
    if not isinstance(data.get('other_text'), str):
        raise HTTPException(status_code=400, detail="other_text must be a string")
    return data

# API endpoints
@app.get("/test")
async def test():
    """Test endpoint to verify code is running"""
    print("🔍 PRINT: Test endpoint called!")
    logger.info("🔍 Test endpoint called - debug logging is working!")
    logger.error("🔍 ERROR: Test endpoint called - error logging test!")
    logger.debug("🔍 DEBUG: Test endpoint called - debug logging test!")
    return {"message": "Test endpoint working", "timestamp": str(datetime.now())}

@app.get("/api/categories")
async def get_categories():
    """Get all categories - Updated to use correct database with 14 categories"""
    print("🔍 PRINT: Categories endpoint called!")
    logger.info("🔍 LOG: Categories endpoint called!")
    
    try:
        print("🔍 PRINT: About to execute database query")
        logger.info("🔍 LOG: About to execute database query")
        
        query = "SELECT * FROM categories ORDER BY id"
        results = execute_query(query)
        
        print(f"🔍 PRINT: Query successful, got {len(results)} results")
        logger.info(f"🔍 LOG: Query successful, got {len(results)} results")
        
        return results
    except Exception as e:
        print(f"🔍 PRINT: Error in categories endpoint: {e}")
        logger.error(f"🔍 LOG: Error in categories endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch categories")

@app.get("/api/categories/{category_id}/blocks")
async def get_blocks_by_category(category_id: int):
    """Get blocks for a specific category"""
    query = "SELECT * FROM blocks WHERE category_id = %s ORDER BY block_number"
    results = execute_query(query, (category_id,))
    return results

@app.get("/api/blocks/{block_code}/questions")
async def get_questions_by_block(block_code: str):
    """Get questions for a specific block"""
    # Extract category_id and block_number from block_code (e.g., "1_1" -> category_id=1, block_number=1)
    try:
        parts = block_code.split('_')
        if len(parts) == 2:
            category_id = int(parts[0])
            block_number = int(parts[1])
        else:
            raise ValueError("Invalid block_code format")
    except (ValueError, IndexError):
        raise HTTPException(status_code=400, detail="Invalid block_code format. Expected format: category_block (e.g., 1_1)")
    
    query = "SELECT * FROM questions WHERE category_id = %s AND block_number = %s ORDER BY question_number"
    results = execute_query(query, (category_id, block_number))
    return results

@app.get("/api/questions/{question_code}/options")
async def get_options_by_question(question_code: str):
    """Get options for a specific question"""
    query = "SELECT * FROM options WHERE question_code = %s ORDER BY option_select"
    results = execute_query(query, (question_code,))
    return results

@app.post("/api/users")
async def create_user(user: Dict[str, Any]):
    """Create a new user with age validation"""
    try:
        validated_data = validate_user_request(user)
        
        # Validate age (2005-2012)
        if validated_data['year_of_birth'] < 2005 or validated_data['year_of_birth'] > 2012:
            raise HTTPException(status_code=400, detail="Invalid year of birth. Must be between 2005-2012.")
        
        query = """
            INSERT INTO users (user_uuid, year_of_birth, created_at)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_uuid) DO NOTHING
        """
        execute_query(query, (validated_data['user_uuid'], validated_data['year_of_birth'], datetime.now()), fetch=False)
        return {"message": "User created successfully", "user_uuid": validated_data['user_uuid']}
    except Exception as e:
        logger.error(f"User creation failed: {e}")
        raise HTTPException(status_code=500, detail="User creation failed")

@app.get("/api/users")
async def get_users():
    """Get all users (for debugging)"""
    query = "SELECT user_uuid, year_of_birth, created_at FROM users"
    results = execute_query(query)
    return {"users": results}

@app.post("/api/debug/ensure_user")
async def debug_ensure_user(user_data: Dict[str, Any]):
    """Debug endpoint to manually ensure a user exists"""
    try:
        user_uuid = user_data.get('user_uuid')
        if not user_uuid:
            raise HTTPException(status_code=400, detail="user_uuid is required")
        
        # Check current status
        check_query = "SELECT user_uuid, year_of_birth, created_at FROM users WHERE user_uuid = %s"
        existing_user = execute_query(check_query, (user_uuid,))
        
        if existing_user:
            return {
                "message": "User already exists",
                "user": existing_user[0],
                "action": "none"
            }
        else:
            # Create the user
            # This function is no longer used, so we'll just return an error
            # if ensure_user_exists is removed.
            raise HTTPException(status_code=500, detail="User creation is not supported via this endpoint.")
            
    except Exception as e:
        logger.error(f"Debug ensure_user failed: {e}")
        raise HTTPException(status_code=500, detail=f"Debug operation failed: {str(e)}")

@app.post("/api/vote")
async def vote(vote_data: Dict[str, Any]):
    """Record a single-choice vote"""
    try:
        logger.info(f"Received vote request: {vote_data}")
        
        # Validate vote data
        validated_data = validate_vote_request(vote_data)
        
        # Get question and category details for denormalization
        question_query = """
            SELECT q.question_text, q.question_number, c.category_name, c.id as category_id, q.block_number
            FROM questions q
            JOIN categories c ON q.category_id = c.id
            WHERE q.question_code = %s
        """
        question_info = execute_query(question_query, (vote_data['question_code'],))
        
        if not question_info:
            logger.error(f"Question not found: {vote_data['question_code']}")
            raise HTTPException(status_code=404, detail="Question not found")
        
        question = question_info[0]
        logger.info(f"Question info: {question}")
        
        # Get option details
        option_query = """
            SELECT option_text, option_code
            FROM options
            WHERE question_code = %s AND option_select = %s
        """
        option_info = execute_query(option_query, (vote_data['question_code'], vote_data['option_select']))
        
        if not option_info:
            logger.error(f"Option not found: question_code={vote_data['question_code']}, option_select={vote_data['option_select']}")
            raise HTTPException(status_code=404, detail="Option not found")
        
        option = option_info[0]
        logger.info(f"Option info: {option}")
        
        # Insert vote with denormalized data
        insert_query = """
            INSERT INTO responses (
                question_code, option_select, option_code, option_text, user_uuid,
                question_text, question_number, category_name, category_id, block_number, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        execute_query(insert_query, (
            vote_data['question_code'], vote_data['option_select'], option['option_code'], option['option_text'],
            vote_data['user_uuid'], question['question_text'], question['question_number'],
            question['category_name'], question['category_id'], question['block_number'], datetime.now()
        ), fetch=False)
        
        logger.info(f"Vote recorded successfully for user {vote_data['user_uuid']}")
        return {"message": "Vote recorded successfully"}
        
    except Exception as e:
        logger.error(f"Vote recording failed: {e}")
        logger.error(f"Exception type: {type(e)}")
        logger.error(f"Exception details: {str(e)}")
        raise HTTPException(status_code=500, detail="Vote recording failed")

@app.post("/api/checkbox_vote")
async def checkbox_vote(vote_data: Dict[str, Any]):
    """Record a checkbox vote with weights"""
    try:
        # Validate vote data
        validated_data = validate_checkbox_vote_request(vote_data)
        
        # Get question and category details for denormalization
        question_query = """
            SELECT q.question_text, q.question_number, c.category_name, c.id as category_id, q.block_number, q.max_select
            FROM questions q
            JOIN categories c ON q.category_id = c.id
            WHERE q.question_code = %s
        """
        question_info = execute_query(question_query, (vote_data['question_code'],))
        
        if not question_info:
            raise HTTPException(status_code=404, detail="Question not found")
        
        question = question_info[0]
        
        # Validate max_select limit
        if question['max_select'] and len(vote_data['option_selects']) > question['max_select']:
            raise HTTPException(
                status_code=400, 
                detail=f"Too many options selected. Maximum allowed: {question['max_select']}"
            )
        
        # Calculate weight for each option
        weight = 1.0 / len(vote_data['option_selects'])
        
        # Insert votes for each selected option
        for option_select in vote_data['option_selects']:
            # Handle "OTHER" option specially for checkbox questions
            if option_select == "OTHER":
                # For "OTHER" in checkbox questions, we need to get the actual text
                # This should come from the frontend as a separate field
                other_text = vote_data.get('other_text', 'OTHER')
                
                # Insert "OTHER" as a checkbox response with proper weight
                insert_query = """
                    INSERT INTO checkbox_responses (
                        question_code, option_select, option_code, option_text, user_uuid,
                        question_text, question_number, category_name, category_id, block_number, weight, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                execute_query(insert_query, (
                    vote_data['question_code'], "OTHER", "OTHER", other_text,
                    vote_data['user_uuid'], question['question_text'], question['question_number'],
                    question['category_name'], question['category_id'], question['block_number'], weight, datetime.now()
                ), fetch=False)
            else:
                # Get option details for regular options
                option_query = """
                    SELECT option_text, option_code
                    FROM options
                    WHERE question_code = %s AND option_select = %s
                """
                option_info = execute_query(option_query, (vote_data['question_code'], option_select))
                
                if not option_info:
                    continue  # Skip invalid options
                
                option = option_info[0]
                
                # Insert checkbox vote with denormalized data
                insert_query = """
                    INSERT INTO checkbox_responses (
                        question_code, option_select, option_code, option_text, user_uuid,
                        question_text, question_number, category_name, category_id, block_number, weight, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                execute_query(insert_query, (
                    vote_data['question_code'], option_select, option['option_code'], option['option_text'],
                    vote_data['user_uuid'], question['question_text'], question['question_number'],
                    question['category_name'], question['category_id'], question['block_number'], weight, datetime.now()
                ), fetch=False)
        
        return {"message": "Checkbox vote recorded successfully"}
        
    except Exception as e:
        logger.error(f"Checkbox vote recording failed: {e}")
        raise HTTPException(status_code=500, detail="Checkbox vote recording failed")

@app.post("/api/other")
async def submit_other(other_data: Dict[str, Any]):
    """Record a free-text response"""
    try:
        # Validate other data
        validated_data = validate_other_request(other_data)
        
        # Get question and category details for denormalization
        question_query = """
            SELECT q.question_text, q.question_number, c.category_name, c.id as category_id, q.block_number
            FROM questions q
            JOIN categories c ON q.category_id = c.id
            WHERE q.question_code = %s
        """
        question_info = execute_query(question_query, (other_data['question_code'],))
        
        if not question_info:
            raise HTTPException(status_code=404, detail="Question not found")
        
        question = question_info[0]
        
        # Insert other response with denormalized data
        insert_query = """
            INSERT INTO other_responses (
                question_code, user_uuid, other_text, question_text, question_number,
                category_name, category_id, block_number, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        execute_query(insert_query, (
            other_data['question_code'], other_data['user_uuid'], other_data['other_text'],
            question['question_text'], question['question_number'], question['category_name'],
            question['category_id'], question['block_number'], datetime.now()
        ), fetch=False)
        
        return {"message": "Other response recorded successfully"}
        
    except Exception as e:
        logger.error(f"Other response recording failed: {e}")
        raise HTTPException(status_code=500, detail="Other response recording failed")

@app.get("/api/soundtracks")
async def get_soundtracks():
    """Get all soundtracks"""
    try:
        query = """
        SELECT song_id, song_title, mood_tag, playlist_tag, lyrics_snippet, 
               featured, featured_order, file_url
        FROM soundtracks 
        ORDER BY featured_order, song_title
        """
        results = execute_query(query)
        logger.info(f"Retrieved {len(results)} soundtracks")
        return {"soundtracks": results}
    except Exception as e:
        logger.error(f"Error retrieving soundtracks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve soundtracks: {str(e)}")

@app.get("/api/soundtracks/playlists")
async def get_playlists():
    """Get all unique playlists"""
    try:
        query = """
        SELECT DISTINCT unnest(string_to_array(playlist_tag, ', ')) as playlist
        FROM soundtracks 
        WHERE playlist_tag IS NOT NULL AND playlist_tag != ''
        ORDER BY playlist
        """
        results = execute_query(query)
        playlists = ['All Songs'] + [r['playlist'] for r in results]
        logger.info(f"Retrieved {len(playlists)} playlists")
        return {"playlists": playlists}
    except Exception as e:
        logger.error(f"Error retrieving playlists: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve playlists: {str(e)}")

@app.get("/api/results/{question_code}")
async def get_results(question_code: str):
    """Get results for a specific question"""
    try:
        # Check if it's a checkbox question by looking at the question type
        question_query = "SELECT * FROM questions WHERE question_code = %s"
        question_info = execute_query(question_query, (question_code,))
        
        if not question_info:
            raise HTTPException(status_code=404, detail="Question not found")
        
        question = question_info[0]
        
        # For now, assume all questions can have both types of responses
        # Get single-choice responses
        single_query = """
            SELECT option_select, COUNT(*) as count
            FROM responses
            WHERE question_code = %s
            GROUP BY option_select
            ORDER BY option_select
        """
        single_results = execute_query(single_query, (question_code,))
        
        # Get checkbox responses (sum of weights)
        checkbox_query = """
            SELECT option_select, SUM(weight) as count
            FROM checkbox_responses
            WHERE question_code = %s
            GROUP BY option_select
            ORDER BY option_select
        """
        checkbox_results = execute_query(checkbox_query, (question_code,))
        
        # Get OTHER responses with proper weighting
        other_query = """
            SELECT COUNT(*) as count
            FROM other_responses
            WHERE question_code = %s
        """
        other_results = execute_query(other_query, (question_code,))
        
        # Combine results
        all_results = {}
        
        # Add single-choice results
        for result in single_results:
            option = result['option_select']
            if option in all_results:
                all_results[option]['count'] += result['count']
            else:
                all_results[option] = {'option_select': option, 'count': result['count']}
        
        # Add checkbox results
        for result in checkbox_results:
            option = result['option_select']
            if option in all_results:
                all_results[option]['count'] += result['count']
            else:
                all_results[option] = {'option_select': option, 'count': result['count']}
        
        # Add OTHER responses with proper weighting
        if other_results and other_results[0]['count'] > 0:
            other_count = other_results[0]['count']
            # For OTHER responses, we need to check if they came from checkbox questions
            # and apply the same weighting logic
            if 'OTHER' in all_results:
                # If OTHER already exists from checkbox votes, don't double-count
                # The checkbox_responses already includes the properly weighted OTHER votes
                pass
            else:
                # If OTHER only exists from "other" responses, treat as single choice (full vote)
                all_results['OTHER'] = {'option_select': 'OTHER', 'count': other_count}
        
        # Convert to list and sort
        final_results = list(all_results.values())
        final_results.sort(key=lambda x: x['option_select'])
        
        return {
            "question_code": question_code,
            "results": final_results
        }
        
    except Exception as e:
        logger.error(f"Error fetching results: {e}")
        raise HTTPException(status_code=500, detail="Error fetching results")

@app.post("/api/import_data")
async def import_data():
    """Import CSV data to the current database"""
    try:
        logger.info("🔄 Starting data import...")
        
        # Import the import_to_render function
        from import_to_render import import_to_render
        
        # Run the import
        import_to_render()
        
        return {"message": "Data import completed successfully"}
        
    except Exception as e:
        logger.error(f"❌ Import error: {e}")
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

@app.post("/api/setup")
async def setup_database():
    """Setup database with initial data (categories, blocks, questions, options)"""
    try:
        logger.info("🔄 Starting database setup...")
        
        # Import CSV data
        import csv
        import os
        from datetime import datetime
        
        def clean_csv_value(value):
            """Clean CSV values and handle multi-line content"""
            if value is None:
                return None
            value = str(value).strip().replace('\ufeff', '')
            if '\n' in value:
                value = value.replace('\n', ' ')
            return value
        
        # Get database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Import categories
            logger.info("📁 Importing categories...")
            with open('data/categories.csv', 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cursor.execute("""
                        INSERT INTO categories (category_name, category_text, sort_order, created_at)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (category_name) DO NOTHING
                    """, (
                        clean_csv_value(row['category_name']),
                        clean_csv_value(row.get('category_text', '')),
                        int(row.get('sort_order', 0)),
                        datetime.now()
                    ))
            logger.info("✅ Categories imported")
            
            # Import blocks
            logger.info("📁 Importing blocks...")
            with open('data/blocks.csv', 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cursor.execute("""
                        INSERT INTO blocks (category_id, block_number, block_code, block_text, version, uuid, category_name, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (block_code) DO NOTHING
                    """, (
                        int(row['category_id']),
                        int(row['block_number']),
                        clean_csv_value(row['block_code']),
                        clean_csv_value(row['block_text']),
                        clean_csv_value(row.get('version', '')),
                        clean_csv_value(row.get('uuid', '')),
                        clean_csv_value(row.get('category_name', '')),
                        datetime.now()
                    ))
            logger.info("✅ Blocks imported")
            
            # Import questions
            logger.info("📁 Importing questions...")
            with open('data/questions.csv', 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cursor.execute("""
                        INSERT INTO questions (category_id, question_code, question_number, question_text, check_box, max_select, block_number, block_text, is_start_question, parent_question_id, color_code, version, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (question_code) DO NOTHING
                    """, (
                        int(row['category_id']),
                        clean_csv_value(row['question_code']),
                        int(row['question_number']),
                        clean_csv_value(row['question_text']),
                        row.get('check_box', 'false').lower() == 'true',
                        int(row.get('max_select', 10)) if row.get('max_select') and row.get('max_select').strip() and row.get('max_select') != '' else (10 if row.get('check_box', 'false').lower() == 'true' else 1),
                        int(row['block_number']),
                        clean_csv_value(row['block_text']),
                        row.get('is_start_question', 'false').lower() == 'true',
                        int(row['parent_question_id']) if row.get('parent_question_id') and row.get('parent_question_id').strip() else None,
                        clean_csv_value(row.get('color_code', '')),
                        clean_csv_value(row.get('version', '')),
                        datetime.now()
                    ))
            logger.info("✅ Questions imported")
            
            # Import options
            logger.info("📁 Importing options...")
            with open('data/options.csv', 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cursor.execute("""
                        INSERT INTO options (question_code, option_select, option_text, sort_order, weight, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (question_code, option_select) DO NOTHING
                    """, (
                        clean_csv_value(row['question_code']),
                        clean_csv_value(row['option_select']),
                        clean_csv_value(row['option_text']),
                        int(row.get('sort_order', 0)),
                        float(row.get('weight', 1.0)),
                        datetime.now()
                    ))
            logger.info("✅ Options imported")
            
            # Import soundtracks
            logger.info("📁 Importing soundtracks...")
            with open('data/soundtracks.csv', 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cursor.execute("""
                        INSERT INTO soundtracks (title, artist, playlist, mood, energy, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (title, artist) DO NOTHING
                    """, (
                        clean_csv_value(row['title']),
                        clean_csv_value(row['artist']),
                        clean_csv_value(row['playlist']),
                        clean_csv_value(row['mood']),
                        clean_csv_value(row['energy']),
                        datetime.now()
                    ))
            logger.info("✅ Soundtracks imported")
            
            # Commit all changes
            conn.commit()
            logger.info("🎉 Database setup completed successfully!")
            
            return {
                "message": "Database setup completed successfully",
                "details": {
                    "categories": "imported",
                    "blocks": "imported", 
                    "questions": "imported",
                    "options": "imported",
                    "soundtracks": "imported"
                }
            }
            
        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Error during import: {e}")
            raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"❌ Setup endpoint error: {e}")
        raise HTTPException(status_code=500, detail=f"Setup failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
