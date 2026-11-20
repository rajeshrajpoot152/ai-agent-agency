from backend.app.core.database import query_db, execute_db

def clean_database():
    rows = query_db("SELECT id, brand_name, project_type FROM agency_brands ORDER BY created_at ASC;")
    print("Found", len(rows), "brands:")
    for r in rows:
        print(f" - {r['id']}: {r['brand_name']} ({r['project_type']})")

    # Find the main Flagship IT Agency Hub
    flagship = query_db("SELECT id FROM agency_brands WHERE project_type = 'it_company' LIMIT 1;", fetchone=True)
    if not flagship and rows:
        flagship = rows[0]
        execute_db("UPDATE agency_brands SET project_type = 'it_company', brand_name = 'Apex AI & IT Solutions (Agency Command Hub)' WHERE id = %s;", (flagship['id'],))
        flagship_id = flagship['id']
    elif flagship:
        flagship_id = flagship['id']
        execute_db("UPDATE agency_brands SET brand_name = 'Apex AI & IT Solutions (Agency Command Hub)' WHERE id = %s;", (flagship_id,))
    else:
        flagship_id = None

    print(f"Primary Agency Command Hub ID: {flagship_id}")

    # Remove the dummy test seeds: QuickApp Tool 1..6, dummy realty, dummy jewelry, dummy CRM
    dummy_names = [
        'QuickApp Studio (Tool #1)', 'AutoBot AI (Tool #2)', 'SEO RankJet (Tool #3)',
        'DesignMatrix AI (Tool #4)', 'LeadFlow Engine (Tool #5)', 'VoiceAgent Telephony (Tool #6)',
        'Apex Realty Estates', 'Aura Luxe Jewelry', 'Apex Flow CRM',
        'QuickApp Studio (Product Site #1)', 'AutoBot AI (Product Site #2)',
        'FitLife Elite Gym', 'Artisan Oven Bakery', 'Apex Legal Consulting'
    ]

    for name in dummy_names:
        # Re-assign any leads or logs to flagship so no foreign key error
        b = query_db("SELECT id FROM agency_brands WHERE brand_name = %s;", (name,), fetchone=True)
        if b:
            bid = b['id']
            if bid != flagship_id:
                execute_db("UPDATE outreach_leads SET brand_id = %s WHERE brand_id = %s;", (flagship_id, bid))
                execute_db("UPDATE client_projects SET brand_id = %s WHERE brand_id = %s;", (flagship_id, bid))
                execute_db("DELETE FROM agency_brands WHERE id = %s;", (bid,))
                print(f"Removed dummy test seed: {name}")

    remaining = query_db("SELECT id, brand_name, project_type FROM agency_brands;")
    print("Remaining clean brands:", len(remaining))
    for r in remaining:
        print(f" * {r['brand_name']} ({r['project_type']})")

if __name__ == "__main__":
    clean_database()
