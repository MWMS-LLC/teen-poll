# main.py
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.db import connection_pool, db_check, db_ssl_status

# Initialize FastAPI app
app = FastAPI(
    title="My World My Say API",
    description="Backend API for My World My Say app",
    version="1.0.0"
)

# CORS setup
origins = [
    "http://localhost:5173",
    "https://myworldmysay.com",
    "https://www.myworldmysay.com",
    "https://api.myworldmysay.com",
    "https://teen.myworldmysay.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database query execution function
def execute_query(query: str, params: tuple = None, fetch: bool = True):
    try:
        conn = connection_pool.getconn()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        if fetch:
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            results = [dict(zip(columns, row)) for row in rows]
            return results
        else:
            conn.commit()
            return True
    except Exception as e:
        logging.error(f"Database operation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database operation failed: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            connection_pool.putconn(conn)

# ------------------ Root ------------------
@app.get("/")
def root():
    return {"message": "MWMS API running"}

# ------------------ Health ------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/db-check")
def database_check():
    return db_check()

@app.get("/db-ssl-status")
def database_ssl_status():
    return db_ssl_status()

# ------------------ Categories ------------------
@app.get("/api/categories")
def get_categories():
    query = "SELECT id, name, description FROM categories ORDER BY id"
    return {"categories": execute_query(query)}

# ------------------ Blocks ------------------
@app.get("/api/categories/{category_id}/blocks")
def get_blocks(category_id: int):
    query = """
        SELECT id, block_code, block_number, block_text
        FROM blocks
        WHERE category_id = %s
        ORDER BY block_number
    """
    return {"blocks": execute_query(query, (category_id,))}

# ------------------ Questions ------------------
@app.get("/api/blocks/{block_code}/questions")
def get_questions(block_code: str):
    query = """
        SELECT id, question_code, question_number, question_text
        FROM questions
        WHERE block_code = %s
        ORDER BY question_number
    """
    return {"questions": execute_query(query, (block_code,))}

# ------------------ Options ------------------
@app.get("/api/questions/{question_code}/options")
def get_options(question_code: str):
    query = """
        SELECT id, option_code, option_number, option_text
        FROM options
        WHERE question_code = %s
        ORDER BY option_number
    """
    return {"options": execute_query(query, (question_code,))}

# ------------------ Users ------------------
@app.post("/api/users")
def create_user(user_uuid: str, year_of_birth: int):
    query = "INSERT INTO users (user_uuid, year_of_birth) VALUES (%s, %s) ON CONFLICT DO NOTHING"
    execute_query(query, (user_uuid, year_of_birth), fetch=False)
    return {"message": "User created or already exists"}

@app.post("/api/debug/ensure_user")
def ensure_user(user_uuid: str, year_of_birth: int):
    query = "INSERT INTO users (user_uuid, year_of_birth) VALUES (%s, %s) ON CONFLICT DO NOTHING"
    execute_query(query, (user_uuid, year_of_birth), fetch=False)
    return {"message": "User ensured"}

# ------------------ Responses ------------------
@app.post("/api/vote")
def record_vote(user_uuid: str, question_code: str, question_text: str, question_number: int,
               category_name: str, block_number: int,
               option_id: int, option_code: str, option_text: str,
               setup_question_code: str = None, setup_option_id: int = None):
    query = """
        INSERT INTO responses (
            user_uuid, question_code, question_text, question_number,
            category_name, option_id, option_code, option_text, block_number,
            setup_question_code, setup_option_id
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    execute_query(query, (user_uuid, question_code, question_text, question_number,
                         category_name, option_id, option_code, option_text,
                         block_number, setup_question_code, setup_option_id), fetch=False)
    return {"message": "Vote recorded"}

@app.post("/api/checkbox_vote")
def record_checkbox_vote(user_uuid: str, question_code: str, question_text: str, question_number: int,
                        category_name: str, block_number: int,
                        option_id: int, option_code: str, option_text: str, weight: float = 1.0,
                        setup_question_code: str = None, setup_option_id: int = None):
    query = """
        INSERT INTO checkbox_responses (
            user_uuid, question_code, question_text, question_number,
            category_name, option_id, option_code, option_text, block_number, weight,
            setup_question_code, setup_option_id
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    execute_query(query, (user_uuid, question_code, question_text, question_number,
                         category_name, option_id, option_code, option_text, block_number,
                         weight, setup_question_code, setup_option_id), fetch=False)
    return {"message": "Checkbox vote recorded"}

@app.post("/api/other")
def record_other_response(user_uuid: str, question_code: str, question_text: str, question_number: int,
                         category_name: str, block_number: int, other_text: str,
                         setup_question_code: str = None):
    query = """
        INSERT INTO other_responses (
            user_uuid, question_code, question_text, question_number,
            category_name, block_number, other_text, setup_question_code
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """
    execute_query(query, (user_uuid, question_code, question_text, question_number,
                         category_name, block_number, other_text, setup_question_code), fetch=False)
    return {"message": "Other response recorded"}

# ------------------ Results ------------------
@app.get("/api/results/{question_code}")
def get_results(question_code: str):
    query = """
        SELECT option_code, option_text, COUNT(*) as votes
        FROM responses
        WHERE question_code = %s
        GROUP BY option_code, option_text
        ORDER BY votes DESC
    """
    return {"results": execute_query(query, (question_code,))}

# ------------------ Soundtracks ------------------
@app.get("/api/soundtracks")
def get_soundtracks():
    query = "SELECT * FROM soundtracks ORDER BY id"
    return {"soundtracks": execute_query(query)}

@app.get("/api/soundtracks/playlists")
def get_playlists():
    query = "SELECT DISTINCT playlist FROM soundtracks ORDER BY playlist"
    return {"playlists": execute_query(query)}