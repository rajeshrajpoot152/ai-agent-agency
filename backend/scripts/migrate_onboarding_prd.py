from backend.app.core.database import execute_db

def migrate_onboarding_and_prd():
    print("Migrating client_projects table for Onboarding Wizard, PRD, and Code Starter...")
    execute_db("""
        ALTER TABLE client_projects 
        ADD COLUMN IF NOT EXISTS onboarding_data JSONB DEFAULT '{}'::jsonb,
        ADD COLUMN IF NOT EXISTS prd_document TEXT,
        ADD COLUMN IF NOT EXISTS starter_code JSONB DEFAULT '{}'::jsonb;
    """)
    print(" Successfully updated 'client_projects' table with onboarding_data, prd_document, and starter_code columns.")

if __name__ == "__main__":
    migrate_onboarding_and_prd()
