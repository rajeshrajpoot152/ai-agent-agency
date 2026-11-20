from backend.app.core.database import execute_db, query_db

def migrate_calendar_and_invoices():
    print("Migrating database for Content Calendar and Invoicing Engine...")

    # 1. content_schedules table
    execute_db("""
        CREATE TABLE IF NOT EXISTS content_schedules (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            brand_id UUID REFERENCES agency_brands(id) ON DELETE CASCADE,
            day_number INT,
            scheduled_date DATE,
            platform VARCHAR(50) NOT NULL,
            post_theme VARCHAR(150),
            post_copy TEXT NOT NULL,
            hashtags TEXT,
            canva_prompt TEXT,
            status VARCHAR(50) DEFAULT 'scheduled',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)
    print(" Created or verified 'content_schedules' table.")

    # 2. client_invoices table
    execute_db("""
        CREATE TABLE IF NOT EXISTS client_invoices (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            lead_id UUID REFERENCES outreach_leads(id) ON DELETE SET NULL,
            client_name VARCHAR(255) NOT NULL,
            business_name VARCHAR(255) NOT NULL,
            invoice_number VARCHAR(100) UNIQUE NOT NULL,
            issue_date DATE NOT NULL,
            due_date DATE NOT NULL,
            line_items JSONB DEFAULT '[]'::jsonb,
            subtotal VARCHAR(50) NOT NULL,
            tax_amount VARCHAR(50) DEFAULT '₹0',
            total_amount VARCHAR(50) NOT NULL,
            payment_status VARCHAR(50) DEFAULT 'pending',
            upi_vpa VARCHAR(100) DEFAULT 'agency.growth@upi',
            upi_qr_url TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)
    print(" Created or verified 'client_invoices' table.")

    print("Migration successful!")

if __name__ == "__main__":
    migrate_calendar_and_invoices()
