from backend.app.core.database import query_db

def inspect_all():
    rows = query_db("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name;")
    for r in rows:
        t = r['table_name']
        cols = query_db(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{t}';")
        print(f"Table: {t} ({len(cols)} cols)")

if __name__ == "__main__":
    inspect_all()
