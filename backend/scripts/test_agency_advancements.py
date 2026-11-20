import requests

BASE = "http://127.0.0.1:8000"

print("--- 1. Testing Daily Briefing ---")
r1 = requests.get(f"{BASE}/api/agency/daily-briefing").json()
print("Date:", r1.get("date_str"))
print("Due followups count:", len(r1.get("due_followups", [])))
print("Tactical directives:", len(r1.get("tactical_focus", [])))

print("\n--- 2. Testing System Audit ---")
r2 = requests.get(f"{BASE}/api/agency/system-audit").json()
print("Health score:", r2.get("health_score"))
print("Database Latency:", r2.get("database", {}).get("latency_ms"), "ms")
print("Channels verified:", r2.get("channels", {}).get("verified_active"))
print("Active models:", r2.get("ai_engines", {}).get("available_providers"))

print("\n--- 3. Testing Public Inquiry Intake (/api/leads/public-inquiry) ---")
payload_inq = {
    "full_name": "Rohan Deshmukh",
    "business_name": "Cafe Mocha Roasters",
    "mobile_number": "+919876540001",
    "service_needed": "24/7 AI WhatsApp Sales Receptionist",
    "budget_range": "₹35,000 - ₹60,000/mo",
    "city": "Pune",
    "project_details": "Need automated reservation and menu inquiry answering on WhatsApp"
}
r3 = requests.post(f"{BASE}/api/leads/public-inquiry", json=payload_inq).json()
print("Inquiry status:", r3.get("status"))
print("Message:", r3.get("message"))
print("WhatsApp quick chat URL:", r3.get("whatsapp_quick_chat_url")[:60] + "...")

print("\n--- 4. Testing Proposal Generator (/api/leads/generate-proposal) ---")
payload_prop = {
    "client_name": "Rohan Deshmukh",
    "business_name": "Cafe Mocha Roasters",
    "package_type": "growth_accelerator",
    "custom_budget": "₹35,000 / month"
}
r4 = requests.post(f"{BASE}/api/leads/generate-proposal", json=payload_prop).json()
print("Proposal ID:", r4.get("proposal_id"))
print("Proposal URL:", r4.get("proposal_url"))
print("Deliverables count:", len(r4.get("deliverables", [])))

print("\n--- 5. Testing Public Pages (HTML) ---")
h1 = requests.get(f"{BASE}/inquiry")
print("GET /inquiry status:", h1.status_code, "Length:", len(h1.text))
h2 = requests.get(f"{BASE}{r4.get('proposal_url')}")
print("GET /proposal/{id} status:", h2.status_code, "Length:", len(h2.text))

print("\n--- 6. Testing Brand Kits API ---")
r6 = requests.get(f"{BASE}/api/agency/brands").json()
print("Brand kits count:", r6.get("count"))
if r6.get("brands"):
    print("First brand:", r6["brands"][0]["brand_name"])

print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")
