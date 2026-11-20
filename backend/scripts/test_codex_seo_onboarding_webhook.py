import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:8000"

def test_codex_seo_onboarding_webhook():
    print("Testing Codex SEO Audit, Onboarding Wizard, PRD & WhatsApp Webhook Suite...")

    # 1. Health check
    req = urllib.request.Request(f"{BASE_URL}/health")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        print(" Health Check Passed.")

    # 2. Test Upgraded Codex SEO & GEO Website Audit
    audit_payload = {
        "website_url": "https://malhotratours.com",
        "business_name": "Malhotra Luxury Tours",
        "client_name": "Rohit Malhotra",
        "client_phone": "9876543210"
    }
    req = urllib.request.Request(
        f"{BASE_URL}/api/agency/audit-website",
        data=json.dumps(audit_payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        audit_res = json.loads(resp.read().decode('utf-8'))
        assert audit_res["status"] == "success"
        assert "Codex SEO Suite" in audit_res["engine"]
        s = audit_res["scores"]
        print(f" Codex SEO & GEO Audit Passed: Overall={audit_res['overall_health_score']} | Technical={s['seo_health']} | GEO={s['geo_ai_search']} | E-E-A-T={s['eeat_trust']}")
        assert len(audit_res["critical_flaws"]) == 4
        assert "wa.me" in audit_res["whatsapp_send_url"]
        print(f" 1-Click WhatsApp Pitch Hook Ready: {audit_res['whatsapp_pitch_hook'][:65]}...")

    # 3. Fetch an active project for Onboarding & PRD testing
    req = urllib.request.Request(f"{BASE_URL}/api/leads/projects")
    with urllib.request.urlopen(req) as resp:
        proj_res = json.loads(resp.read().decode('utf-8'))
        assert proj_res["count"] > 0
        test_proj = proj_res["projects"][0]
        proj_id = str(test_proj["id"])
        print(f" Using Active Project for Onboarding: {test_proj['business_name']} (ID: {proj_id})")

    # Verify Onboarding HTML served
    req = urllib.request.Request(f"{BASE_URL}/onboarding/{proj_id}")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        html = resp.read().decode('utf-8')
        assert "Technical Onboarding" in html
        print(" Served HTML Onboarding Wizard Page (200 OK)")

    # Submit Technical Onboarding & Generate PRD
    onboarding_payload = {
        "project_id": proj_id,
        "brand_name": test_proj["business_name"],
        "tagline": "Curated Himalayan & Heritage Luxury Travel Experiences",
        "target_audience": "Affluent travelers and international tourists looking for custom luxury itineraries",
        "brand_colors": "#C29B38, #1E293B",
        "logo_url_or_note": "https://drive.google.com/malhotra-gold-logo.svg",
        "competitor_websites": "abercrombiekent.com, luxurygold.com",
        "must_have_features": [
            "High-Speed Responsive Next.js Web App",
            "24/7 WhatsApp AI Sales Closer Bot",
            "UPI QR & Card Payment Gateway",
            "Codex SEO & AI Search (GEO) Optimization"
        ],
        "tech_preferences": "Next.js 14, Tailwind CSS, Python FastAPI, PostgreSQL",
        "special_requirements": "Interactive booking calendar with instant WhatsApp itinerary generator."
    }
    req = urllib.request.Request(
        f"{BASE_URL}/api/leads/projects/{proj_id}/submit-onboarding",
        data=json.dumps(onboarding_payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        onb_res = json.loads(resp.read().decode('utf-8'))
        assert onb_res["status"] == "success"
        print(f" Technical Onboarding Submitted & PRD Generated: {onb_res['message']}")

    # 4. Verify Project Details Now Contains PRD & Onboarding Data
    req = urllib.request.Request(f"{BASE_URL}/api/leads/projects/{proj_id}")
    with urllib.request.urlopen(req) as resp:
        p_details = json.loads(resp.read().decode('utf-8'))["project"]
        assert p_details.get("prd_document") is not None
        assert "PRODUCT REQUIREMENTS DOCUMENT" in p_details["prd_document"]
        assert p_details["onboarding_data"]["brand_name"] == test_proj["business_name"]
        print(f" Verified PRD in Database: {len(p_details['prd_document'])} characters of specifications.")

    # 5. Generate Autonomous Starter Code
    starter_payload = {
        "project_id": proj_id,
        "component_type": "landing_page"
    }
    req = urllib.request.Request(
        f"{BASE_URL}/api/leads/projects/generate-code-starter",
        data=json.dumps(starter_payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        starter_res = json.loads(resp.read().decode('utf-8'))
        assert starter_res["status"] == "success"
        assert "page.tsx" in starter_res["filename"]
        assert "export default function HomePage" in starter_res["code"]
        print(f" Generated Autonomous Code Starter: {starter_res['filename']} ({len(starter_res['code'])} chars)")

    # 6. Test WhatsApp Inbound Webhook (Verification Challenge + Message Ingestion)
    # Verification GET
    challenge_val = "115599"
    req = urllib.request.Request(
        f"{BASE_URL}/api/leads/webhooks/whatsapp?hub.mode=subscribe&hub.verify_token=apex_agency_webhook_secret_2026&hub.challenge={challenge_val}"
    )
    with urllib.request.urlopen(req) as resp:
        res_val = resp.read().decode('utf-8')
        assert str(challenge_val) in res_val
        print(f" WhatsApp Webhook Verification Challenge Passed: challenge={challenge_val}")

    # Inbound Message POST
    webhook_payload = {
        "from": "919988776655",
        "name": "Vikram Rathore",
        "message": "Hi, what is your budget for developing an e-commerce website with AI automation?"
    }
    req = urllib.request.Request(
        f"{BASE_URL}/api/leads/webhooks/whatsapp",
        data=json.dumps(webhook_payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        hook_res = json.loads(resp.read().decode('utf-8'))
        assert hook_res["status"] == "success"
        assert hook_res["ai_objection_handled"] == "budget"
        assert "Namaste" in hook_res["tactical_reply"]
        print(f" Inbound WhatsApp Handled: Sender={hook_res['sender']} ({hook_res['sender_name']}) | Objection={hook_res['ai_objection_handled']} | Smart Reply: {hook_res['tactical_reply'][:50]}...")

    # 7. Verify Virtual Office Watercooler Caught All Events
    req = urllib.request.Request(f"{BASE_URL}/api/agency/office-pulse")
    with urllib.request.urlopen(req) as resp:
        pulse_res = json.loads(resp.read().decode('utf-8'))
        feed = pulse_res["watercooler_feed"]
        feed_messages = [m["message"] for m in feed[:6]]
        assert any("CLIENT ONBOARDING COMPLETED" in m for m in feed_messages)
        assert any("WHATSAPP INBOUND" in m for m in feed_messages)
        print(" Virtual Office Watercooler Verified: Real-time Onboarding & Inbound WhatsApp alerts logged!")

    print("\n ALL ADVANCED PILLARS (CODEX SEO, ONBOARDING, PRD, CODE SCAFFOLD, WEBHOOK) VERIFIED 100%!")

if __name__ == "__main__":
    test_codex_seo_onboarding_webhook()
