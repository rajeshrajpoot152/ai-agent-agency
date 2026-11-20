import datetime
from backend.app.core.database import execute_db, query_db

def migrate_crm():
    execute_db("ALTER TABLE outreach_leads ADD COLUMN IF NOT EXISTS follow_up_date TIMESTAMP;")
    execute_db("ALTER TABLE outreach_leads ADD COLUMN IF NOT EXISTS inquiry_source VARCHAR(100) DEFAULT 'Direct Lead';")
    execute_db("ALTER TABLE outreach_leads ADD COLUMN IF NOT EXISTS deal_value VARCHAR(50) DEFAULT '₹25,000';")
    
    # Populate default follow_up_dates for existing leads if null (e.g. today or upcoming)
    execute_db("""
        UPDATE outreach_leads 
        SET follow_up_date = CURRENT_TIMESTAMP + INTERVAL '1 day'
        WHERE follow_up_date IS NULL;
    """)

    cols = query_db("SELECT column_name FROM information_schema.columns WHERE table_name = 'outreach_leads';")
    print("Updated columns:", [c['column_name'] for c in cols])
    
    # Check count
    cnt = query_db("SELECT count(*) as total FROM outreach_leads;", fetchone=True)
    print("Total leads in DB:", cnt['total'])

if __name__ == '__main__':
    migrate_crm()
