from backend.app.core.database import execute_db, query_db

def migrate_advanced_agency_features():
    print("Migrating database for Proposals, Brands, and Daily Command Center...")
    
    # 1. client_proposals table
    execute_db("""
        CREATE TABLE IF NOT EXISTS client_proposals (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            lead_id UUID REFERENCES outreach_leads(id) ON DELETE SET NULL,
            client_name VARCHAR(255) NOT NULL,
            business_name VARCHAR(255) NOT NULL,
            package_name VARCHAR(255) NOT NULL,
            scope_summary TEXT,
            deliverables JSONB DEFAULT '[]'::jsonb,
            pricing_breakdown JSONB DEFAULT '[]'::jsonb,
            total_amount VARCHAR(50) NOT NULL,
            valid_until DATE,
            status VARCHAR(50) DEFAULT 'active',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)
    print(" Created or verified 'client_proposals' table.")

    # 2. agency_brands table
    execute_db("""
        CREATE TABLE IF NOT EXISTS agency_brands (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            brand_name VARCHAR(255) NOT NULL,
            industry VARCHAR(100),
            primary_color VARCHAR(50) DEFAULT '#4F46E5',
            secondary_color VARCHAR(50) DEFAULT '#06B6D4',
            tagline VARCHAR(255),
            tone_of_voice VARCHAR(100) DEFAULT 'Professional & Modern',
            target_audience TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)
    print(" Created or verified 'agency_brands' table.")

    # Seed sample agency brands if none exist
    existing_brands = query_db("SELECT COUNT(*) as count FROM agency_brands;")
    if existing_brands and existing_brands[0]['count'] == 0:
        execute_db("""
            INSERT INTO agency_brands (brand_name, industry, primary_color, secondary_color, tagline, tone_of_voice, target_audience)
            VALUES 
            ('FitLife Elite Gym', 'Fitness & Wellness', '#EA580C', '#FBBF24', 'Transform Your Body, Elevate Your Life', 'High-energy, Motivating, Direct', 'Working professionals aged 22-45 looking for premium fitness and personal training'),
            ('Artisan Oven Bakery', 'Food & Beverage', '#D97706', '#92400E', 'Handcrafted Sourdough & Pure Butter Pastries', 'Warm, Artisanal, Cozy, Inviting', 'Foodies, families, and dessert lovers seeking gourmet artisan bakes'),
            ('Apex Legal Consulting', 'Legal & Corporate Services', '#1E3A8A', '#3B82F6', 'Strategic Counsel for High-Growth Startups', 'Authoritative, Reassuring, Ultra-Professional', 'Founders, CFOs, and enterprise leaders needing IP and corporate structuring');
        """)
        print(" Seeded 3 diverse sample brand kits into 'agency_brands'.")

    print("Migration complete!")

if __name__ == "__main__":
    migrate_advanced_agency_features()
