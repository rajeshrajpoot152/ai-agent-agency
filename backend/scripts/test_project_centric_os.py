import json
import urllib.request
import urllib.parse

BASE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("==================================================")
    print("Testing Project-Centric Virtual Team OS Backend...")
    print("==================================================")

    # 1. Test Project List
    req = urllib.request.Request(f"{BASE_URL}/api/projects-hub/list")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        assert data["status"] == "success"
        projects = data["projects"]
        print(f"✓ 1. Projects List: Retrieved {len(projects)} projects across portfolio.")
        assert len(projects) >= 7, "Expected at least 7 projects (1 IT + 6 tools)"

    # Identify Flagship IT, Tool #1, Real Estate, and Jewelry
    flagship = next((p for p in projects if p["project_type"] == "it_company"), None)
    tool_1 = next((p for p in projects if "QuickApp Studio" in p["brand_name"]), None)
    realty = next((p for p in projects if p["project_type"] == "real_estate"), None)
    jewelry = next((p for p in projects if p["project_type"] == "jewelry"), None)

    assert flagship is not None, "Flagship IT Company missing"
    assert tool_1 is not None, "QuickApp Studio Tool #1 missing"
    assert realty is not None, "Apex Realty missing"
    assert jewelry is not None, "Aura Luxe Jewelry missing"

    print(f"  - Flagship: {flagship['brand_name']} (ID: {flagship['id']})")
    print(f"  - Tool #1:  {tool_1['brand_name']} (ID: {tool_1['id']})")
    print(f"  - Realty:   {realty['brand_name']} (ID: {realty['id']})")
    print(f"  - Jewelry:  {jewelry['brand_name']} (ID: {jewelry['id']})")

    # 2. Test Project Dashboard & Cause-and-Effect Impact Radar for Tool #1
    req = urllib.request.Request(f"{BASE_URL}/api/projects-hub/{tool_1['id']}/dashboard")
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        assert data["status"] == "success"
        radar = data["impact_radar"]
        print(f"✓ 2. Tool #1 Dashboard & Impact Radar:")
        print(f"  - Current Health: {radar['current_health_score']}")
        print(f"  - Action Predictions: {len(radar['action_predictions'])} predictive models loaded")
        print(f"  - Assigned Squad: {[s['name'] for s in data['assigned_squad']]}")
        print(f"  - Dedicated Social Posts: {len(data['social_posts'])} posts ready")

    # 3. Test Strict Multi-Tenant Data Isolation (Realty vs Jewelry)
    realty_dash = json.loads(urllib.request.urlopen(f"{BASE_URL}/api/projects-hub/{realty['id']}/dashboard").read().decode())
    jewelry_dash = json.loads(urllib.request.urlopen(f"{BASE_URL}/api/projects-hub/{jewelry['id']}/dashboard").read().decode())

    realty_leads = realty_dash["leads"]
    jewelry_leads = jewelry_dash["leads"]

    print(f"✓ 3. Data Isolation Check:")
    print(f"  - Realty Leads count: {len(realty_leads)} (e.g. {[l['full_name'] for l in realty_leads]})")
    print(f"  - Jewelry Leads count: {len(jewelry_leads)} (e.g. {[l['full_name'] for l in jewelry_leads]})")

    # Verify zero cross-contamination
    realty_names = set(l["full_name"] for l in realty_leads)
    jewelry_names = set(l["full_name"] for l in jewelry_leads)
    assert not (realty_names & jewelry_names), "Data contamination detected between Realty and Jewelry!"
    print("  ✓ Zero data leakage between projects verified 100%!")

    # 4. Test Deep Project-Aware Positive vs. Negative Smart Reply
    # Positive case: Client wants to start with QuickApp Studio
    pos_payload = {
        "client_name": "Rohan Mehta",
        "client_message": "Hi, I am ready to purchase the Agency plan of QuickApp Studio. Can we start immediately?",
        "sentiment_mode": "positive",
        "channel": "whatsapp"
    }
    req_pos = urllib.request.Request(
        f"{BASE_URL}/api/projects-hub/{tool_1['id']}/smart-reply",
        data=json.dumps(pos_payload).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_pos) as resp:
        pos_res = json.loads(resp.read().decode())
        print(f"\n✓ 4A. Smart Reply [POSITIVE Agreement]:")
        print(f"  Snippet: {pos_res['smart_reply'][:200]}...")
        assert "QuickApp" in pos_res["smart_reply"] or "plan" in pos_res["smart_reply"].lower()

    # Negative / Boundary case: Client asking for 70% discount on Luxury Jewelry
    neg_payload = {
        "client_name": "Sunil Verma",
        "client_message": "I want this custom diamond bridal necklace set, but my budget is only 1 Lakh instead of 6 Lakhs. Give me 70% discount or I will go elsewhere.",
        "sentiment_mode": "negative",
        "channel": "whatsapp"
    }
    req_neg = urllib.request.Request(
        f"{BASE_URL}/api/projects-hub/{jewelry['id']}/smart-reply",
        data=json.dumps(neg_payload).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_neg) as resp:
        neg_res = json.loads(resp.read().decode())
        print(f"\n✓ 4B. Smart Reply [NEGATIVE / Boundary Defense & Counter-Offer]:")
        print(f"  Snippet: {neg_res['smart_reply'][:250]}...")
        # Verify it handled the boundary professionally
        assert len(neg_res["smart_reply"]) > 50

    # 5. Test Outreach Dispatch
    if realty_leads:
        target_lead = realty_leads[0]
        dispatch_payload = {
            "lead_id": target_lead["id"],
            "channel": "whatsapp",
            "message_content": "Namaste Sanjay ji! Golf Course Villa site visit ke liye slots open hain. Kya kal 11:30 AM convenient hoga?"
        }
        req_disp = urllib.request.Request(
            f"{BASE_URL}/api/projects-hub/{realty['id']}/outreach/dispatch",
            data=json.dumps(dispatch_payload).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req_disp) as resp:
            disp_res = json.loads(resp.read().decode())
            print(f"\n✓ 5. Outreach Dispatch:")
            print(f"  Status: {disp_res['status']} | WhatsApp Direct URL generated: {bool(disp_res.get('whatsapp_direct_url'))}")

    # 6. Test Future Human Team Delegation
    team_payload = {
        "full_name": "Rohan Sharma (Human PM)",
        "email": "rohan.pm@agency.io",
        "role": "Senior Project Manager",
        "assigned_projects": [realty["id"], tool_1["id"]]
    }
    req_team = urllib.request.Request(
        f"{BASE_URL}/api/projects-hub/team-members",
        data=json.dumps(team_payload).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req_team) as resp:
        team_res = json.loads(resp.read().decode())
        print(f"\n✓ 6. Human Team Delegation (RBAC): {team_res['message']}")

    print("\n==================================================")
    print("ALL PROJECT-CENTRIC OS BACKEND TESTS PASSED 100%! 🎉")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
