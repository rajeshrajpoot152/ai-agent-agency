from backend.app.core.database import query_db

for tbl in ['outreach_leads', 'clients', 'client_subscriptions']:
    cols = query_db(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{tbl}' ORDER BY ordinal_position;")
    print(f"\n--- {tbl} ---")
    for c in cols:
        print(f"  {c['column_name']} ({c['data_type']})")
