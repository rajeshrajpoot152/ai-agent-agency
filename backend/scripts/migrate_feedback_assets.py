from backend.app.core.database import execute_db

def migrate_feedback_and_assets():
    print("Migrating client_projects table for feedback and asset storage...")
    execute_db("""
        ALTER TABLE client_projects 
        ADD COLUMN IF NOT EXISTS client_feedback JSONB DEFAULT '[]'::jsonb,
        ADD COLUMN IF NOT EXISTS client_assets JSONB DEFAULT '[]'::jsonb;
    """)
    print(" Successfully updated 'client_projects' table with client_feedback and client_assets columns.")

if __name__ == "__main__":
    migrate_feedback_and_assets()
