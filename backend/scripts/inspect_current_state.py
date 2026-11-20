from backend.app.core.database import query_db

for table in ['agency_brands', 'client_projects', 'outreach_leads', 'content_schedules']:
    cols = query_db("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s;", (table,))
    print(f"\n--- {table} Columns ---")
    for c in cols:
        print(f"  {c['column_name']} ({c['data_type']})")

print("\n--- Current Projects Sample ---")
projects = query_db("SELECT * FROM client_projects LIMIT 2;")
for p in projects:
    print(dict(p))
