# main_parents.py
# Parents version of the main application
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Union
import logging
from datetime import datetime, timezone
import zlib
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import db module and handle errors gracefully
try:
    from db import connection_pool, db_check, db_ssl_status
    logger.info("Successfully imported db module")
except Exception as e:
    logger.error(f"Failed to import db module: {e}")
    raise

app = FastAPI()

# Add startup event to log initialization
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up parents application...")
    try:
        # Test database connection
        db_check()
        logger.info("Parents database connection successful")
    except Exception as e:
        logger.error(f"Parents database connection failed: {e}")
        raise

# ------------------ CORS setup for parents ------------------
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://myworldmysay.com",
    "https://www.myworldmysay.com",
    "https://api.myworldmysay.com",
    "https://teen.myworldmysay.com",
    "https://parents.myworldmysay.com",
    "https://www.parents.myworldmysay.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ DB helper (local to main.py) ------------------
def execute_query(query: str, params: tuple = None, fetch: bool = True):
    """
    Execute a SQL query using the shared connection_pool from db.
    Returns list[dict] when fetch=True, otherwise commits and returns True.
    """
    conn = None
    cursor = None
    try:
        conn = connection_pool.getconn()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        if fetch:
            cols = [d[0] for d in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            return [dict(zip(cols, row)) for row in rows]
        else:
            conn.commit()
            return True
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            connection_pool.putconn(conn)

# ------------------ Data models ------------------
class UserCreate(BaseModel):
    user_uuid: str
    year_of_birth: int

class VoteSubmission(BaseModel):
    user_uuid: str
    question_code: str
    option_select: Optional[str] = None
    option_selects: Optional[List[str]] = None
    other_text: Optional[str] = None

# ------------------ Health check ------------------
@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        db_check()
        return {"status": "healthy", "service": "parents-poll-backend", "timestamp": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

# ------------------ API endpoints ------------------
@app.get("/api/categories")
def get_categories():
    """Get all categories"""
    categories = execute_query("""
        SELECT id, category_name, category_text, day_of_week, description, category_text_long, version, uuid, sort_order
        FROM categories 
        ORDER BY sort_order, id
    """)
    return {"categories": categories}

@app.get("/api/categories/{category_id}/blocks")
def get_blocks(category_id: int):
    """Get blocks for a category"""
    blocks = execute_query("""
        SELECT id, block_number, block_code, block_text, version, uuid, category_name
        FROM blocks 
        WHERE category_id = %s 
        ORDER BY block_number
    """, (category_id,))
    return {"blocks": blocks}

@app.get("/api/blocks/{block_code}/questions")
def get_questions(block_code: str):
    """Get questions for a block"""
    questions = execute_query("""
        SELECT id, question_code, question_number, question_text, check_box, max_select, 
               block_number, block_text, is_start_question, parent_question_id, color_code, version
        FROM questions 
        WHERE block_number = %s 
        ORDER BY question_number
    """, (block_code,))
    return {"questions": questions}

@app.get("/api/questions/{question_code}/options")
def get_options(question_code: str):
    """Get options for a question"""
    options = execute_query("""
        SELECT id, option_select, option_code, option_text, response_message, companion_advice, tone_tag, next_question_id
        FROM options 
        WHERE question_code = %s 
        ORDER BY option_select
    """, (question_code,))
    return {"options": options}

@app.post("/api/users")
def create_user(user: UserCreate):
    """Create a new user"""
    try:
        execute_query("""
            INSERT INTO users (user_uuid, year_of_birth, created_at)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_uuid) DO UPDATE SET
                year_of_birth = EXCLUDED.year_of_birth,
                created_at = EXCLUDED.created_at
        """, (user.user_uuid, user.year_of_birth, datetime.now()), fetch=False)
        
        return {"message": "User created successfully", "user_uuid": user.user_uuid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

# ------------------ Helper function for metadata ------------------
def get_metadata(question_code: str):
    """Get question metadata for vote processing"""
    result = execute_query("""
        SELECT q.question_text, q.question_number, q.category_id, c.category_name, c.category_text, q.block_number
        FROM questions q
        JOIN categories c ON q.category_id = c.id
        WHERE q.question_code = %s
    """, (question_code,))
    
    return result[0] if result else None

# ------------------ Vote submission endpoints ------------------
@app.post("/api/vote/single")
def submit_single_vote(vote: dict):
    """Handle single-choice votes - stores in responses table"""
    user_uuid = vote.get("user_uuid")
    question_code = vote.get("question_code")
    option_select = vote.get("option_select")
    other_text = vote.get("other_text")

    if not user_uuid or not question_code or not option_select:
        raise HTTPException(status_code=400, detail="Missing required fields")

    # Lookup question metadata
    meta = get_metadata(question_code)
    if not meta:
        raise HTTPException(status_code=404, detail="Question not found")

    # Normalize "Other" values
    OTHER_KEY = "OTHER"
    if option_select and isinstance(option_select, str) and option_select.strip().upper() == OTHER_KEY:
        option_select = OTHER_KEY

    if other_text:
        other_text = other_text.strip()

    # Insert single-choice vote
    execute_query(
        """
        INSERT INTO responses
        (user_uuid, question_code, question_text, question_number,
        category_id, category_name, category_text, block_number,
        option_id, option_select, option_code, option_text,
        created_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
        """,
        (
            user_uuid, question_code, meta["question_text"], meta["question_number"],
            meta["category_id"], meta["category_name"], meta["category_text"], meta["block_number"],
            None, option_select, f"{question_code}_{option_select}", option_select
        ),
        fetch=False
    )

    # If user selected OTHER and typed free text, also store it
    if option_select == "OTHER" and other_text:
        execute_query(
            """
            INSERT INTO other_responses
            (user_uuid, question_code, question_text, question_number,
            category_id, category_name, category_text, block_number,
            other_text, created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            """,
            (
                user_uuid, question_code,
                meta["question_text"], meta["question_number"],
                meta["category_id"], meta["category_name"], meta["category_text"], meta["block_number"],
                other_text,
            ),
            fetch=False,
        )

    return {"message": "Single-choice vote recorded", "question_code": question_code}

@app.post("/api/vote/checkbox")
def submit_checkbox_vote(vote: dict):
    """Handle checkbox votes - stores in checkbox_responses table with weights"""
    user_uuid = vote.get("user_uuid")
    question_code = vote.get("question_code")
    option_selects = vote.get("option_selects", [])
    other_text = vote.get("other_text")

    if not user_uuid or not question_code or not option_selects:
        raise HTTPException(status_code=400, detail="Missing required fields")

    if len(option_selects) == 0:
        raise HTTPException(status_code=400, detail="No checkbox options provided")

    # Lookup question metadata
    meta = get_metadata(question_code)
    if not meta:
        raise HTTPException(status_code=404, detail="Question not found")

    # Normalize "Other" values
    OTHER_KEY = "OTHER"
    option_selects = [OTHER_KEY if isinstance(v, str) and v.strip().upper() == OTHER_KEY else v for v in option_selects]

    if other_text:
        other_text = other_text.strip()

    # Calculate weight (each option gets equal weight)
    weight = 1.0 / len(option_selects)

    # Insert each selected option
    for opt in option_selects:
        execute_query(
            """
            INSERT INTO checkbox_responses
            (user_uuid, question_code, question_text, question_number,
            category_id, category_name, category_text, block_number,
            option_id, option_select, option_code, option_text,
            weight, created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            """,
            (
                user_uuid, question_code, meta["question_text"], meta["question_number"],
                meta["category_id"], meta["category_name"], meta["category_text"], meta["block_number"],
                None, opt, f"{question_code}_{opt}", opt, weight
            ),
            fetch=False
        )

        # If "OTHER" was selected and free text exists, also store it
        if opt == "OTHER" and other_text:
            execute_query(
                """
                INSERT INTO other_responses
                (user_uuid, question_code, question_text, question_number,
                category_id, category_name, category_text, block_number,
                other_text, created_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
                """,
                (
                    user_uuid, question_code,
                    meta["question_text"], meta["question_number"],
                    meta["category_id"], meta["category_name"], meta["category_text"], meta["block_number"],
                    other_text,
                ),
                fetch=False,
            )

    return {"message": "Checkbox vote(s) recorded", "question_code": question_code}

@app.post("/api/vote/other")
def submit_other_vote(vote: dict):
    """Handle other text votes - stores in other_responses and creates placeholder in responses"""
    user_uuid = vote.get("user_uuid")
    question_code = vote.get("question_code")
    other_text = vote.get("other_text")

    if not user_uuid or not question_code or not other_text:
        raise HTTPException(status_code=400, detail="Missing required fields")

    other_text = other_text.strip()
    if not other_text:
        raise HTTPException(status_code=400, detail="Other text cannot be empty")

    # Lookup question metadata
    meta = get_metadata(question_code)
    if not meta:
        raise HTTPException(status_code=404, detail="Question not found")

    OTHER_KEY = "OTHER"

    # Store the free text
    execute_query(
        """
        INSERT INTO other_responses
        (user_uuid, question_code, question_text, question_number,
        category_id, category_name, category_text, block_number,
        other_text, created_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
        """,
        (
            user_uuid, question_code,
            meta["question_text"], meta["question_number"],
            meta["category_id"], meta["category_name"], meta["category_text"], meta["block_number"],
            other_text,
        ),
        fetch=False,
    )

    # Create a placeholder in responses so charts show "Other"
    execute_query(
        """
        INSERT INTO responses
        (user_uuid, question_code, question_text, question_number,
        category_id, category_name, category_text, block_number,
        option_id, option_select, option_code, option_text,
        created_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
        """,
        (
            user_uuid, question_code,
            meta["question_text"], meta["question_number"],
            meta["category_id"], meta["category_name"], meta["category_text"], meta["block_number"],
            None, OTHER_KEY, f"{question_code}_{OTHER_KEY}", "Other",
        ),
        fetch=False,
    )

    return {"message": "Other text response recorded", "question_code": question_code}

# ------------------ Results aggregation ------------------
@app.get("/api/results/{question_code}")
def get_results(question_code: str):
    """
    Aggregates results for a question:
      - Single-choice from responses
      - Checkbox from checkbox_responses
      - Total responses reported as integer (number of distinct users)
    """

    # Get all option definitions for the question
    option_rows = execute_query(
        """
        SELECT option_select, option_code, option_text
        FROM options
        WHERE question_code = %s
        ORDER BY option_select
        """,
        (question_code,)
    ) or []

    # Single-choice counts
    single_counts = execute_query(
        """
        SELECT option_select, COUNT(*)::float as votes
        FROM responses
        WHERE question_code = %s
        GROUP BY option_select
        """,
        (question_code,)
    ) or []

    # Checkbox counts (safe cast + handle empty case)
    checkbox_counts = execute_query(
        """
        SELECT option_select, COALESCE(SUM(weight),0)::float as votes
        FROM checkbox_responses
        WHERE question_code = %s
        GROUP BY option_select
        """,
        (question_code,)
    ) or []


    # --- Merge counts into one dict ---
    counts = {}
    for row in single_counts + checkbox_counts:
        sel = row["option_select"]
        counts[sel] = counts.get(sel, 0) + row["votes"]

    # --- Build results array with all options ---
    results = []
    for opt in option_rows:
        votes = counts.get(opt["option_select"], 0)
        results.append({
            "option_select": opt["option_select"],
            "option_code": opt["option_code"],
            "option_text": opt["option_text"],
            "votes": votes
        })

    # --- Total responses as integer (distinct users across both tables) ---
    total_result = execute_query(
        """
        SELECT COUNT(DISTINCT user_uuid) AS n FROM (
            SELECT user_uuid FROM responses WHERE question_code = %s
            UNION
            SELECT user_uuid FROM checkbox_responses WHERE question_code = %s
        ) AS combined_votes
        """,
        (question_code, question_code)
    )
    
    total = int(total_result[0]["n"]) if total_result else 0

    return {
        "question_code": question_code,
        "results": results,
        "total_responses": total
    }

# ------------------ Soundtracks endpoint ------------------
@app.get("/api/soundtracks")
def get_soundtracks():
    """Get all soundtracks"""
    soundtracks = execute_query("""
        SELECT song_id, song_title, mood_tag, playlist_tag, lyrics_snippet, featured, featured_order, file_url
        FROM soundtracks 
        ORDER BY featured DESC, featured_order, song_title
    """)
    return {"soundtracks": soundtracks}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)




