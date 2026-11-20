import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "agency_master")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Rajesh@123")

def run_sql_file(conn, file_path):
    print(f"Executing: {file_path} ...")
    with open(file_path, "r", encoding="utf-8") as f:
        sql = f.read()
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    print(f"Success: {file_path}")

def init_database():
    print(f"Connecting to PostgreSQL database '{DB_NAME}' on {DB_HOST}:{DB_PORT} as {DB_USER}...")
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    try:
        run_sql_file(conn, "schema.sql")
        run_sql_file(conn, "seed_data.sql")
        print("\nAll tables & initial agents created successfully in 'agency_master'!")
        
        # Verify tables created
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            tables = [row[0] for row in cur.fetchall()]
            print("\nCreated Tables in agency_master:")
            for t in tables:
                print(f"  - {t}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_database()
