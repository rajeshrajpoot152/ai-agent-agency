from backend.app.core.database import query_db

def inspect():
    tables = ['outreach_leads', 'client_invoices', 'agency_brands', 'agency_team_members', 'content_schedules']
    for t in tables:
        cols = query_db(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{t}';")
        print(f"Table: {t}")
        print(" ->", [c['column_name'] for c in cols])

if __name__ == "__main__":
    inspect()
