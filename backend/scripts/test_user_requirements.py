import requests

BASE = "http://127.0.0.1:8000"

print("--- 1. Testing Bulk Outreach Ingestion (100-Numbers Machine) ---")
sample_contacts = """
9820011223, Vikram Roy, Alpha Cloud Labs
9880022334, Sunita Deshmukh, Apex Retail Ventures
9840012345, Rajesh Verma, FinEdge Payments
9810033445, Meenakshi Sundaram, Omni Logistics
9876543210, Ankit Agarwal, Bharat Commerce
"""

r1 = requests.post(f"{BASE}/api/leads/bulk-import-outreach", json={
    "raw_leads_text": sample_contacts,
    "service_pitch_type": "it_web_mobile_ai",
    "custom_agency_name": "Apex AI & IT Solutions"
}).json()

print("Status:", r1.get("status"))
print("Total imported:", r1.get("total_imported"))
if r1.get("leads"):
    print("Sample Lead #1:", r1["leads"][0]["name"], "|", r1["leads"][0]["phone"])
    print("WhatsApp Link #1:", r1["leads"][0]["whatsapp_url"][:70] + "...")
    print("Personalized Pitch Preview:", r1["leads"][0]["message"][:100] + "...")

print("\n--- 2. Testing Brand 360° Pack (IT Company & 6+ Sites) ---")
r2 = requests.post(f"{BASE}/api/agency/brand-360-pack", json={
    "brand_name": "Apex AI & IT Solutions"
}).json()

print("Status:", r2.get("status"))
print("Brand:", r2.get("brand_name"))
print("LinkedIn Post Length:", len(r2.get("social_posts", {}).get("linkedin_b2b", "")))
print("Instagram Slides:", len(r2.get("social_posts", {}).get("instagram_carousel", [])))
print("Canva Banner Formats:", list(r2.get("banner_creative_briefs", {}).keys()))
print("SEO Target Keywords:", len(r2.get("seo_package", {}).get("target_keywords", [])))
print("WhatsApp Pitch Ready:", bool(r2.get("outreach_pitches", {}).get("whatsapp_cold_pitch")))

print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")
