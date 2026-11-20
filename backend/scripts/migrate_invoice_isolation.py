from backend.app.core.database import execute_db

def migrate_invoices():
    execute_db("ALTER TABLE client_invoices ADD COLUMN IF NOT EXISTS brand_id UUID REFERENCES agency_brands(id);")
    print("✓ Added brand_id to client_invoices table.")

if __name__ == "__main__":
    migrate_invoices()
