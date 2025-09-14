# main.py
from fastapi import FastAPI
from backend.db import connection_pool, db_check, db_ssl_status

app = FastAPI(title="My World My Say API")
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="My World My Say API")

# Allow frontend origins
origins = [
    "http://localhost:5173",   # default Vite
    "http://localhost:5174",   # if Vite bumps port
    "https://youth-poll-frontend.onrender.com",  # deployed frontend
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def execute_query(query: str, params: tuple = None, fetch: bool = True):
    """
    Execute a SQL query using the global connection pool.

    Args:
        query (str): SQL statement to execute.
        params (tuple, optional): Parameters for the SQL statement.
        fetch (bool): If True, fetch results and return as list of dicts.
                      If False, commit changes and return True.

    Returns:
        list[dict] | bool: Query results as list of dicts, or True if committed.
    """
    conn = connection_pool.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        if fetch:
            # Automatically map column names → values
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        else:
            conn.commit()
            return True
    finally:
        connection_pool.return_connection(conn)


@app.get("/health")
def health():
    """
    Health check endpoint.

    Returns:
        dict: Database reachability and SSL status.
    """
    return {
        "database": "ok" if db_check() else "down",
        "ssl": "enabled" if db_ssl_status() else "disabled",
    }


@app.get("/api/categories")
def get_categories():
    """
    Get all categories.
    """
    return {
        "categories": execute_query(
            "SELECT id, category_name, category_text, category_text_long FROM categories ORDER BY id"
        )
    }


@app.get("/api/categories/{category_id}/blocks")
def get_blocks_by_category(category_id: int):
    """
    Get blocks for a given category.

    Args:
        category_id (int): ID of the category.

    Returns:
        dict: A list of blocks for that category.
    """
    return {
        "blocks": execute_query(
            "SELECT id, block_code, block_number, block_text FROM blocks WHERE category_id = %s ORDER BY block_number",
            (category_id,),
        )
    }


@app.get("/api/blocks/{block_code}/questions")
def get_questions(block_code: str):
    """
    Get all questions for a given block.

    Args:
        block_code (str): Code of the block to fetch questions for.

    Returns:
        dict: A list of questions for that block.
    """
    return {"questions": execute_query("SELECT id, question_code, question_text FROM questions WHERE block_code = %s ORDER BY id", (block_code,))}


@app.get("/api/questions/{question_code}/options")
def get_options_by_question(question_code: str):
    """
    Get options for a specific question.

    Args:
        question_code (str): Code of the question.

    Returns:
        dict: A list of options for that question.
    """
    return {
        "options": execute_query(
            "SELECT id, option_code, option_text, option_select FROM options WHERE question_code = %s ORDER BY option_select",
            (question_code,),
        )
    }
