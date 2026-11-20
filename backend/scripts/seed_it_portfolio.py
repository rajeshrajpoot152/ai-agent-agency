from backend.app.core.database import execute_db, query_db

def seed_it_agency_portfolio():
    # Insert Primary IT Agency Brand
    execute_db("""
        INSERT INTO agency_brands (brand_name, industry, primary_color, secondary_color, tagline, tone_of_voice, target_audience, website_url)
        VALUES 
        ('Apex AI & IT Solutions (Flagship Company)', 'IT Services & AI Engineering', '#6366F1', '#06B6D4', 'Custom Web Apps, Mobile Engineering, Workflow Automation & Autonomous AI Agents', 'Visionary, High-Tech, Authoritative, High-ROI', 'Founders, SMEs, and Enterprise Leaders needing custom web platforms, mobile apps, operational automation, and autonomous AI agent systems.', 'https://apex-technologies.io'),
        ('QuickApp Studio (Product Site #1)', 'Mobile & Web Development', '#3B82F6', '#10B981', 'Turn Any Business Idea Into A Production Web & Mobile App in 14 Days', 'Agile, High-Velocity, Modern Tech', 'Startups, D2C brands, and local businesses wanting rapid custom web and mobile app launches.', 'https://quickapp.studio'),
        ('AutoBot AI (Product Site #2)', 'Business Automation & AI Bots', '#8B5CF6', '#EC4899', '24/7 AI WhatsApp Sales Receptionists & CRM Automations', 'Innovative, Efficiency-Focused, 24/7 Autopilot', 'E-commerce stores, real estate agencies, clinics, and service businesses losing leads to slow response times.', 'https://autobot-ai.io')
        ON CONFLICT DO NOTHING;
    """)
    print(" Successfully seeded IT Flagship Company and Portfolio Websites into 'agency_brands'!")

if __name__ == "__main__":
    seed_it_agency_portfolio()
