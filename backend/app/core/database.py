import psycopg2
from psycopg2.extras import RealDictCursor
from backend.app.core.config import settings

def get_db_connection():
    return psycopg2.connect(
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        cursor_factory=RealDictCursor
    )

def query_db(query: str, params=None, fetchone: bool = False):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            res = cur.fetchone() if fetchone else cur.fetchall()
            conn.commit()
            return res
    finally:
        conn.close()

def execute_db(query: str, params=None):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            conn.commit()
            return cur.rowcount
    finally:
        conn.close()
