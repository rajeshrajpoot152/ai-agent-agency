import os
import psycopg2
from psycopg2.extras import RealDictCursor
from backend.app.core.config import settings

def migrate_strict_project_isolation():
    print("Starting Strict Project Isolation & Multi-Tenant Migration...")
    conn = psycopg2.connect(
        dbname=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        cursor_factory=RealDictCursor
    )
    conn.autocommit = True
    cur = conn.cursor()

    # 1. Enhance agency_brands for complete project isolation & metadata
    print("1. Updating agency_brands table schema...")
    cur.execute("""
        ALTER TABLE agency_brands 
        ADD COLUMN IF NOT EXISTS project_type VARCHAR(50) DEFAULT 'tool_website',
        ADD COLUMN IF NOT EXISTS assigned_squad JSONB DEFAULT '[]'::jsonb,
        ADD COLUMN IF NOT EXISTS social_autopilot_enabled BOOLEAN DEFAULT true,
        ADD COLUMN IF NOT EXISTS telegram_group_url VARCHAR(255),
        ADD COLUMN IF NOT EXISTS community_url VARCHAR(255),
        ADD COLUMN IF NOT EXISTS assigned_manager VARCHAR(100) DEFAULT 'Founder (You)',
        ADD COLUMN IF NOT EXISTS pricing_tier_summary TEXT,
        ADD COLUMN IF NOT EXISTS value_proposition TEXT,
        ADD COLUMN IF NOT EXISTS allowed_discount_max INTEGER DEFAULT 10;
    """)

    # 2. Human Team Members Delegation Table (Future Multi-Manager Access)
    print("2. Ensuring agency_team_members table exists...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS agency_team_members (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            full_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE,
            role VARCHAR(100) DEFAULT 'Project Manager',
            assigned_projects JSONB DEFAULT '[]'::jsonb,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)

    # 3. Enhance outreach_leads for multi-tenant project isolation & channels
    print("3. Updating outreach_leads table schema...")
    cur.execute("""
        ALTER TABLE outreach_leads 
        ADD COLUMN IF NOT EXISTS brand_id UUID REFERENCES agency_brands(id),
        ADD COLUMN IF NOT EXISTS telegram_handle VARCHAR(100),
        ADD COLUMN IF NOT EXISTS email_address VARCHAR(255),
        ADD COLUMN IF NOT EXISTS community_member BOOLEAN DEFAULT false,
        ADD COLUMN IF NOT EXISTS last_reply_sentiment VARCHAR(50),
        ADD COLUMN IF NOT EXISTS project_notes TEXT;
    """)

    # 4. Enhance client_projects for brand association
    print("4. Updating client_projects table schema...")
    cur.execute("""
        ALTER TABLE client_projects 
        ADD COLUMN IF NOT EXISTS brand_id UUID REFERENCES agency_brands(id);
    """)

    # 5. Populate / Standardize the Portfolio:
    # 1 Flagship IT Agency + 6 Tool Websites + 1 Real Estate + 1 Jewelry + 1 Custom CRM
    print("5. Seeding / Standardizing the Portfolio (1 IT Company + 6 Tools + 3 Verticals)...")

    # Define standard portfolio
    portfolio = [
        {
            "brand_name": "Apex AI & IT Solutions (Flagship Company)",
            "project_type": "it_company",
            "industry": "IT Services & Enterprise AI Engineering",
            "primary_color": "#6366F1",
            "secondary_color": "#06B6D4",
            "tagline": "Custom Web Apps, Mobile Engineering, Workflow Automation & Autonomous AI Agents",
            "value_proposition": "End-to-end bespoke technology partner for founders, SMEs, and enterprises scaling with high velocity.",
            "target_audience": "Founders, CTOs, and Business Owners needing custom software and automated AI systems.",
            "website_url": "https://apex-technologies.io",
            "telegram_group_url": "https://t.me/ApexEnterpriseHQ",
            "community_url": "https://discord.gg/apextech",
            "pricing_tier_summary": "Standard Sprints: $3,000 - $12,000 / milestone. Max discount allowed: 10%.",
            "assigned_squad": [
                {"name": "Arjun Sharma", "role": "Lead Tech Architect", "avatar": "/assets/avatars/head_charlie.jpg"},
                {"name": "Kabir Sen", "role": "VP Tech Operations & DevOps", "avatar": "/assets/avatars/head_jordan.jpg"},
                {"name": "Neha Patel", "role": "Autonomous Lead Specialist", "avatar": "/assets/avatars/head_maya.jpg"},
                {"name": "Priya Nair", "role": "VP Operations & Strategy", "avatar": "/assets/avatars/head_morgan.jpg"}
            ]
        },
        {
            "brand_name": "QuickApp Studio (Tool #1)",
            "project_type": "tool_website",
            "industry": "Rapid Mobile & Web App Builder",
            "primary_color": "#0EA5E9",
            "secondary_color": "#38BDF8",
            "tagline": "Turn Spreadsheets and APIs into Native Mobile Apps in 48 Hours",
            "value_proposition": "Low-code to production code app generator for fast-moving startups.",
            "target_audience": "Indie hackers, agencies, and small businesses needing swift app launches.",
            "website_url": "https://quickappstudio.io",
            "telegram_group_url": "https://t.me/QuickAppCreators",
            "community_url": "https://discord.gg/quickapp",
            "pricing_tier_summary": "Starter: $49/mo, Agency: $199/mo, Lifetime: $499.",
            "assigned_squad": [
                {"name": "Arjun Sharma", "role": "Full-Stack Engineer", "avatar": "/assets/avatars/head_charlie.jpg"},
                {"name": "Alex", "role": "Customer Success Lead", "avatar": "/assets/avatars/head_alex.jpg"},
                {"name": "Neha Patel", "role": "Growth Closer", "avatar": "/assets/avatars/head_maya.jpg"}
            ]
        },
        {
            "brand_name": "AutoBot AI (Tool #2)",
            "project_type": "tool_website",
            "industry": "Autonomous Business Automation Bots",
            "primary_color": "#8B5CF6",
            "secondary_color": "#A78BFA",
            "tagline": "24/7 AI Receptionist & WhatsApp Autonomous Booking Agent",
            "value_proposition": "Automates lead capture, objection answering, and calendaring over WhatsApp and Web.",
            "target_audience": "Clinics, consultancies, realtors, and retail businesses.",
            "website_url": "https://autobotai.cloud",
            "telegram_group_url": "https://t.me/AutoBotUsers",
            "community_url": "https://discord.gg/autobotai",
            "pricing_tier_summary": "Pro: $79/mo, Enterprise: $299/mo.",
            "assigned_squad": [
                {"name": "Kabir Sen", "role": "DevOps & Integration Architect", "avatar": "/assets/avatars/head_jordan.jpg"},
                {"name": "Neha Patel", "role": "Lead Closer", "avatar": "/assets/avatars/head_maya.jpg"}
            ]
        },
        {
            "brand_name": "SEO RankJet (Tool #3)",
            "project_type": "tool_website",
            "industry": "AI Search (GEO / AEO) & Codex SEO Optimizer",
            "primary_color": "#10B981",
            "secondary_color": "#34D399",
            "tagline": "Dominate Google Search, Perplexity and ChatGPT AI Overviews",
            "value_proposition": "Automated technical crawl, JSON-LD schema builder, and passage citability engine.",
            "target_audience": "Content creators, e-commerce stores, and digital marketing agencies.",
            "website_url": "https://rankjet.io",
            "telegram_group_url": "https://t.me/RankJetSEO",
            "community_url": "https://discord.gg/rankjet",
            "pricing_tier_summary": "Pro: $99/mo, Scale: $249/mo.",
            "assigned_squad": [
                {"name": "Arjun Sharma", "role": "SEO Architect", "avatar": "/assets/avatars/head_charlie.jpg"},
                {"name": "Sameer", "role": "Technical Crawler", "avatar": "/assets/avatars/head_sam.jpg"}
            ]
        },
        {
            "brand_name": "DesignMatrix AI (Tool #4)",
            "project_type": "tool_website",
            "industry": "Canva Multi-Brand Ad & Banner Bulk Generator",
            "primary_color": "#EC4899",
            "secondary_color": "#F472B6",
            "tagline": "Generate 50 Production-Ready Social Creatives in 1 Click",
            "value_proposition": "Bulk creative creation engine formatted for Canva, Meta Ads and LinkedIn carousels.",
            "target_audience": "Social media managers, D2C brands, and growth marketers.",
            "website_url": "https://designmatrix.ai",
            "telegram_group_url": "https://t.me/DesignMatrixAI",
            "community_url": "https://discord.gg/designmatrix",
            "pricing_tier_summary": "Creator: $39/mo, Agency: $149/mo.",
            "assigned_squad": [
                {"name": "Pooja Verma", "role": "Creative Design Lead", "avatar": "/assets/avatars/agent_5.jpg"},
                {"name": "Kabir Sen", "role": "Design Director", "avatar": "/assets/avatars/head_jordan.jpg"}
            ]
        },
        {
            "brand_name": "LeadFlow Engine (Tool #5)",
            "project_type": "tool_website",
            "industry": "B2B Prospecting & Multi-Channel Outreach Machine",
            "primary_color": "#F59E0B",
            "secondary_color": "#FBBF24",
            "tagline": "Verified B2B Decision Makers + Automated Personalized Outreach",
            "value_proposition": "Scrapes and enriches verified business contacts with 1-click WhatsApp and email pipelines.",
            "target_audience": "B2B sales teams, agency owners, and recruiters.",
            "website_url": "https://leadflowengine.io",
            "telegram_group_url": "https://t.me/LeadFlowVIP",
            "community_url": "https://discord.gg/leadflow",
            "pricing_tier_summary": "Standard: $89/mo, Unlimited: $279/mo.",
            "assigned_squad": [
                {"name": "Neha Patel", "role": "Lead Prospector", "avatar": "/assets/avatars/head_maya.jpg"},
                {"name": "Karan Malhotra", "role": "BDA Closer", "avatar": "/assets/avatars/agent_11.jpg"}
            ]
        },
        {
            "brand_name": "VoiceAgent Telephony (Tool #6)",
            "project_type": "tool_website",
            "industry": "AI Voice Calling & Inbound Concierge",
            "primary_color": "#6366F1",
            "secondary_color": "#818CF8",
            "tagline": "Ultra-Low Latency Conversational AI Phone Call Agents",
            "value_proposition": "Handles appointment scheduling, customer inquiries, and qualification calls smoothly.",
            "target_audience": "Healthcare clinics, real estate brokers, and insurance agencies.",
            "website_url": "https://voiceagenttelephony.io",
            "telegram_group_url": "https://t.me/VoiceAgentHQ",
            "community_url": "https://discord.gg/voiceagent",
            "pricing_tier_summary": "Pay-as-you-go: $0.12/minute or Enterprise Unlimited.",
            "assigned_squad": [
                {"name": "Varun", "role": "Telephony Specialist", "avatar": "/assets/avatars/agent_15.jpg"},
                {"name": "Alex", "role": "Success Lead", "avatar": "/assets/avatars/head_alex.jpg"}
            ]
        },
        {
            "brand_name": "Apex Realty Estates",
            "project_type": "real_estate",
            "industry": "Luxury Real Estate & Villa Developments",
            "primary_color": "#B45309",
            "secondary_color": "#D97706",
            "tagline": "Exclusive High-Yield Luxury Properties, Plots & Commercial Spaces",
            "value_proposition": "Curated luxury real estate portfolios with 3D virtual walkthroughs and AI client matching.",
            "target_audience": "High-net-worth investors, luxury home buyers, and commercial developers.",
            "website_url": "https://apexrealtyestates.com",
            "telegram_group_url": "https://t.me/ApexRealtyVIP",
            "community_url": "https://discord.gg/apexrealty",
            "pricing_tier_summary": "Prime Villas: ₹1.8 Cr - ₹12 Cr. Commercial: ₹3.5 Cr+.",
            "assigned_squad": [
                {"name": "Priya Nair", "role": "Strategy & Valuation Lead", "avatar": "/assets/avatars/head_morgan.jpg"},
                {"name": "Kabir Sen", "role": "Visual Experience Director", "avatar": "/assets/avatars/head_jordan.jpg"},
                {"name": "Neha Patel", "role": "High-Ticket Client Closer", "avatar": "/assets/avatars/head_maya.jpg"}
            ]
        },
        {
            "brand_name": "Aura Luxe Jewelry",
            "project_type": "jewelry",
            "industry": "Fine Diamond & Bespoke Bridal Jewelry",
            "primary_color": "#BE185D",
            "secondary_color": "#F43F5E",
            "tagline": "Ethically Sourced Solitaires, Heritage Polki & Modern Luxury Craftsmanship",
            "value_proposition": "Custom artisan jewelry crafted with GIA-certified diamonds and heritage gold artistry.",
            "target_audience": "Bridal shoppers, luxury gift seekers, and gemstone collectors.",
            "website_url": "https://auraluxejewelry.store",
            "telegram_group_url": "https://t.me/AuraLuxeJewels",
            "community_url": "https://discord.gg/auraluxe",
            "pricing_tier_summary": "Custom Rings & Sets: ₹85,000 - ₹25 Lakhs.",
            "assigned_squad": [
                {"name": "Pooja Verma", "role": "Creative Brand Designer", "avatar": "/assets/avatars/agent_5.jpg"},
                {"name": "Alex", "role": "VIP Client Concierge", "avatar": "/assets/avatars/head_alex.jpg"},
                {"name": "Neha Patel", "role": "Bespoke Sales Consultant", "avatar": "/assets/avatars/head_maya.jpg"}
            ]
        },
        {
            "brand_name": "Apex Flow CRM",
            "project_type": "custom_crm",
            "industry": "Custom Enterprise CRM & Lead Pipeline Automation",
            "primary_color": "#059669",
            "secondary_color": "#10B981",
            "tagline": "Lightweight High-Speed CRM for Teams Managing 500+ Deals",
            "value_proposition": "Custom pipelines, automated WhatsApp triggers, and zero-clutter client management.",
            "target_audience": "Growing agencies, real estate firms, and B2B enterprises.",
            "website_url": "https://apexflowcrm.com",
            "telegram_group_url": "https://t.me/ApexFlowCRM",
            "community_url": "https://discord.gg/apexflow",
            "pricing_tier_summary": "Team: $120/mo, Enterprise: $350/mo.",
            "assigned_squad": [
                {"name": "Arjun Sharma", "role": "Lead Architect", "avatar": "/assets/avatars/head_charlie.jpg"},
                {"name": "Rishabh", "role": "FinTech & Pipeline Analyst", "avatar": "/assets/avatars/head_michael.jpg"}
            ]
        }
    ]

    import json
    for p in portfolio:
        existing = cur.execute("SELECT id FROM agency_brands WHERE brand_name = %s;", (p["brand_name"],))
        row = cur.fetchone()
        if row:
            cur.execute("""
                UPDATE agency_brands SET
                    project_type = %s,
                    industry = %s,
                    primary_color = %s,
                    secondary_color = %s,
                    tagline = %s,
                    value_proposition = %s,
                    target_audience = %s,
                    website_url = %s,
                    telegram_group_url = %s,
                    community_url = %s,
                    pricing_tier_summary = %s,
                    assigned_squad = %s
                WHERE id = %s;
            """, (
                p["project_type"], p["industry"], p["primary_color"], p["secondary_color"],
                p["tagline"], p["value_proposition"], p["target_audience"], p["website_url"],
                p["telegram_group_url"], p["community_url"], p["pricing_tier_summary"],
                json.dumps(p["assigned_squad"]), row["id"]
            ))
            print(f"  ✓ Updated existing project: {p['brand_name']}")
        else:
            cur.execute("""
                INSERT INTO agency_brands (
                    brand_name, project_type, industry, primary_color, secondary_color,
                    tagline, value_proposition, target_audience, website_url,
                    telegram_group_url, community_url, pricing_tier_summary, assigned_squad
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (
                p["brand_name"], p["project_type"], p["industry"], p["primary_color"], p["secondary_color"],
                p["tagline"], p["value_proposition"], p["target_audience"], p["website_url"],
                p["telegram_group_url"], p["community_url"], p["pricing_tier_summary"],
                json.dumps(p["assigned_squad"])
            ))
            print(f"  + Created new project: {p['brand_name']}")

    # 6. Backfill existing leads without brand_id to Flagship IT Agency
    flagship = cur.execute("SELECT id FROM agency_brands WHERE brand_name ILIKE '%Flagship%' LIMIT 1;")
    flagship_row = cur.fetchone()
    if flagship_row:
        f_id = flagship_row["id"]
        cur.execute("UPDATE outreach_leads SET brand_id = %s WHERE brand_id IS NULL;", (f_id,))
        cur.execute("UPDATE client_projects SET brand_id = %s WHERE brand_id IS NULL;", (f_id,))
        print(f"6. Backfilled unassigned leads and client projects to Flagship ID: {f_id}")

    # 7. Seed sample isolated leads for Real Estate and Jewelry to demonstrate zero data leakage
    realty = cur.execute("SELECT id FROM agency_brands WHERE project_type = 'real_estate' LIMIT 1;")
    realty_row = cur.fetchone()
    if realty_row:
        r_id = realty_row["id"]
        cur.execute("SELECT count(*) as count FROM outreach_leads WHERE brand_id = %s;", (r_id,))
        if cur.fetchone()["count"] == 0:
            cur.execute("""
                INSERT INTO outreach_leads (brand_id, full_name, business_name, mobile_number, whatsapp_number, email_address, telegram_handle, status, deal_value, notes)
                VALUES 
                (%s, 'Sanjay Singhania', 'Singhania Capital', '+919811223344', '+919811223344', 'sanjay@singhaniacap.com', '@sanjaysinghania', 'in_discussion', '₹4.5 Cr', 'Interested in 4BHK Golf Course Villa. Follow-up on payment structure scheduled.'),
                (%s, 'Rituja Deshmukh', 'Deshmukh Architects', '+919822334455', '+919822334455', 'rituja@deshmukharch.in', '@ritujadeshmukh', 'new', '₹2.8 Cr', 'Inquired for luxury weekend plot near Lonavala.');
            """, (r_id, r_id))
            print("  + Seeded 2 verified leads for Apex Realty Estates")

    jewelry = cur.execute("SELECT id FROM agency_brands WHERE project_type = 'jewelry' LIMIT 1;")
    jewelry_row = cur.fetchone()
    if jewelry_row:
        j_id = jewelry_row["id"]
        cur.execute("SELECT count(*) as count FROM outreach_leads WHERE brand_id = %s;", (j_id,))
        if cur.fetchone()["count"] == 0:
            cur.execute("""
                INSERT INTO outreach_leads (brand_id, full_name, business_name, mobile_number, whatsapp_number, email_address, telegram_handle, status, deal_value, notes)
                VALUES 
                (%s, 'Ananya Mehra', 'Mehra Bridal Studio', '+919833445566', '+919833445566', 'ananya@mehrabridal.com', '@ananyamehra', 'in_discussion', '₹6.2 Lakh', 'Custom uncut diamond polki necklace set for destination wedding in Udaipur.'),
                (%s, 'Kunal Kapoor', 'Kapoor Jewels Boutique', '+919844556677', '+919844556677', 'kunal@kapoorboutique.com', '@kunalkapoor', 'new', '₹3.5 Lakh', 'Solitaire engagement ring 1.5 carat oval cut.');
            """, (j_id, j_id))
            print("  + Seeded 2 verified leads for Aura Luxe Jewelry")

    print("\n✅ Strict Project Isolation & Multi-Tenant Migration Completed Successfully!")
    cur.close()
    conn.close()

if __name__ == "__main__":
    migrate_strict_project_isolation()
