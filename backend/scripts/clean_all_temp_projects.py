from backend.app.core.database import query_db, execute_db

def clean():
    execute_db("DELETE FROM content_schedules WHERE brand_id IN (SELECT id FROM agency_brands WHERE brand_name != 'Apex AI & IT Solutions (Agency Command Hub)');")
    execute_db("DELETE FROM agency_brands WHERE brand_name != 'Apex AI & IT Solutions (Agency Command Hub)';")
    brands = query_db("SELECT id, brand_name, project_type FROM agency_brands;")
    print("Clean brands remaining:", len(brands))
    for b in brands:
        print(f" - {b['brand_name']} ({b['project_type']})")

if __name__ == "__main__":
    clean()
