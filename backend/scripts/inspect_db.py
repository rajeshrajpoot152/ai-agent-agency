from backend.app.core.database import query_db

tables = query_db("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;")
print("Tables in PostgreSQL:", [t['table_name'] for t in tables])
