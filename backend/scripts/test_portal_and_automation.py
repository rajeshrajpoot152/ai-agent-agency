import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:8000"

def test_portal_and_automations():
    print("Testing End-to-End Autonomous Pipeline & Client Portal...")

    # 1. AI Sales Negotiator: Budget Objection
    neg_payload = {
        "client_name": "Vikram Sethi",
        "business_name": "Sethi Logistics",
        "incoming_message": "Aapka cost thoda zyada hai, thoda discount milega kya?",
        "objection_category": "auto"
    }
    req = urllib.request.Request(
        f"{BASE_URL}/api/leads/ai-negotiate",
        data=json.dumps(neg_payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        neg_res = json.loads(resp.read().decode('utf-8'))
        assert neg_res["status"] == "success"
        assert neg_res["detected_category"] == "budget"
        print(f" AI Negotiator (Budget): Category={neg_res['detected_category']} | Tactic={neg_res['negotiation_tactic']}")

    # 2. AI Sales Negotiator: Portfolio Objection
    neg_payload2 = {
        "client_name": "Ananya Roy",
        "business_name": "Roy Fashion Boutique",
        "incoming_message": "Aapka purana kaam ya portfolio live link dikhao please.",
        "objection_category": "auto"
    }
    req = urllib.request.Request(
        f"{BASE_URL}/api/leads/ai-negotiate",
        data=json.dumps(neg_payload2).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        neg_res2 = json.loads(resp.read().decode('utf-8'))
        assert neg_res2["status"] == "success"
        assert "QuickApp Studio" in neg_res2["smart_reply"]
        print(f" AI Negotiator (Portfolio): Brand Showcase Verified ({len(neg_res2['smart_reply'])} chars)")

    # 3. 1-Click Client Website & Tech Audit
    audit_payload = {
        "website_url": "royfashion.in",
        "business_name": "Roy Fashion Hub",
        "client_name": "Ananya Roy",
        "client_phone": "9876500000"
    }
    req = urllib.request.Request(
        f"{BASE_URL}/api/agency/audit-website",
        data=json.dumps(audit_payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        audit_res = json.loads(resp.read().decode('utf-8'))
        assert audit_res["status"] == "success"
        assert len(audit_res["critical_flaws"]) == 4
        print(f" 1-Click Website Audit: Overall={audit_res['overall_health_score']} | Flaws={len(audit_res['critical_flaws'])} | WA Hook Ready={bool(audit_res['whatsapp_send_url'])}")

    # 4. Auto-Provision Client Project Portal
    proj_payload = {
        "client_name": "Karan Malhotra",
        "business_name": "Malhotra Luxury Tours",
        "project_title": "Luxury Travel Booking Platform & 24/7 AI Concierge",
        "target_days": 21
    }
    req = urllib.request.Request(
        f"{BASE_URL}/api/leads/auto-provision-project",
        data=json.dumps(proj_payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        proj_res = json.loads(resp.read().decode('utf-8'))
        assert proj_res["status"] == "success"
        proj_id = proj_res["project_id"]
        portal_url = proj_res["portal_url"]
        print(f" Auto-Provisioned Project: {proj_res['business_name']} | ID={proj_id} | Portal={portal_url}")

    # 5. Fetch Client Portal Details & HTML Page
    req = urllib.request.Request(f"{BASE_URL}/portal/{proj_id}")
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8')
        assert "Live Delivery Portal" in html
        assert "Milestones & Deliverables Roadmap" in html
        print(f" Served HTML Project Portal ({len(html)} bytes)")

    # 6. Advance Milestone (Phase 2 completed)
    upd_payload = {
        "project_id": proj_id,
        "milestone_index": 2,
        "new_status": "completed"
    }
    req = urllib.request.Request(
        f"{BASE_URL}/api/leads/projects/update-milestone",
        data=json.dumps(upd_payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        upd_res = json.loads(resp.read().decode('utf-8'))
        assert upd_res["status"] == "success"
        print(f" Updated Milestone: {upd_res['message']} (Progress: {upd_res['progress_percent']}%)")

    # 7. 100% Autonomous Pipeline Test: Invoicing -> Payment -> Auto Project Creation
    inv_payload = {
        "client_name": "Pooja Verma",
        "business_name": "Verma Cloud Diagnostics",
        "service_title": "Diagnostic Patient App & WhatsApp Booking Bot",
        "amount": "₹50,000",
        "tax_percent": 18.0
    }
    req = urllib.request.Request(
        f"{BASE_URL}/api/leads/generate-invoice",
        data=json.dumps(inv_payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        inv_gen = json.loads(resp.read().decode('utf-8'))
        test_inv_id = inv_gen["invoice_id"]
        test_inv_num = inv_gen["invoice_number"]

    # Mark Paid -> Auto provisions project!
    req = urllib.request.Request(
        f"{BASE_URL}/api/leads/invoices/mark-paid",
        data=json.dumps({"invoice_id": test_inv_id}).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        paid_res = json.loads(resp.read().decode('utf-8'))
        assert paid_res["status"] == "success"
        assert bool(paid_res["portal_url"]) is True
        print(f" 100% Autonomous Chain: Invoice {test_inv_num} Paid -> Client Portal Created: {paid_res['portal_url']}")

    print("\n ALL AUTONOMOUS TESTS PASSED 100%! SYSTEM READY FOR COMPLETE SCALE.")

if __name__ == "__main__":
    test_portal_and_automations()
