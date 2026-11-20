from backend.app.core.database import execute_db, query_db

def migrate_client_projects():
    print("Migrating database for Autonomous Client Project Portals...")

    execute_db("""
        CREATE TABLE IF NOT EXISTS client_projects (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            lead_id UUID REFERENCES outreach_leads(id) ON DELETE SET NULL,
            invoice_id UUID REFERENCES client_invoices(id) ON DELETE SET NULL,
            client_name VARCHAR(255) NOT NULL,
            business_name VARCHAR(255) NOT NULL,
            project_title VARCHAR(255) NOT NULL,
            project_tier VARCHAR(100) DEFAULT 'Growth Accelerator',
            progress_percent INT DEFAULT 25,
            status VARCHAR(50) DEFAULT 'in_progress',
            staging_url TEXT DEFAULT 'https://staging.apexsolutions.ai/preview',
            repository_url TEXT DEFAULT 'https://github.com/apex-ai-agency/client-build',
            milestones JSONB DEFAULT '[]'::jsonb,
            target_launch_date DATE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)
    print(" Created or verified 'client_projects' table in PostgreSQL.")

if __name__ == "__main__":
    migrate_client_projects()
