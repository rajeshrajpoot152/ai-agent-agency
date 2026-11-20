from backend.app.core.database import query_db

cols = query_db("SELECT column_name, is_nullable, data_type FROM information_schema.columns WHERE table_name = 'outreach_message_logs' ORDER BY ordinal_position;")
for c in cols:
    print(dict(c))
