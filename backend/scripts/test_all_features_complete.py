import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:8000"

def test_all_features_complete():
    print("Testing All Advanced Features & Automation Suite...")

    # 1. Health check
    req = urllib.request.Request(f"{BASE_URL}/health")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        print(" Health Check Passed.")

    # 2. Festive Blast Queue (100 Leads WhatsApp Engine)
    blast_payload = {
        "festival_name": "Diwali / Deepawali",
        "discount_percent": 25
    }
    req = urllib.request.Request(
        f"{BASE_URL}/api/agency/festive-blast-queue",
        data=json.dumps(blast_payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        blast_res = json.loads(resp.read().decode('utf-8'))
        assert blast_res["status"] == "success"
        assert blast_res["total_queued"] > 0
        first_lead = blast_res["queue"][0]
        assert "DIWALI25" in first_lead["coupon_code"]
        assert "wa.me" in first_lead["whatsapp_url"]
        print(f" Festive Blast Queue: {blast_res['total_queued']} leads queued | Sample: {first_lead['client_name']} ({first_lead['business_name']}) | Code: {first_lead['coupon_code']}")

    # 3. Trigger Team Standup Banter
    req = urllib.request.Request(
        f"{BASE_URL}/api/agency/trigger-team-standup",
        data=b"{}",
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        standup_res = json.loads(resp.read().decode('utf-8'))
        assert standup_res["status"] == "success"
        print(f" Team Standup Triggered: {standup_res['message']} | Total Messages in Room: {len(standup_res['feed'])}")

    # 4. Award Agent Increment & Promotion
    inc_payload = {
        "agent_name": "Arjun Sharma",
        "bonus_amount": "₹35,000",
        "new_title": "Executive Principal Architect & Partner",
        "reason": "Outstanding technical velocity, sub-50ms latency & flawless milestone delivery"
    }
    req = urllib.request.Request(
        f"{BASE_URL}/api/agency/award-agent-increment",
        data=json.dumps(inc_payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        inc_res = json.loads(resp.read().decode('utf-8'))
        assert inc_res["status"] == "success"
        print(f" Agent Increment Awarded: {inc_res['message']}")

    # 5. Full Agency Data Export & Backup
    req = urllib.request.Request(f"{BASE_URL}/api/agency/export-data")
    with urllib.request.urlopen(req) as resp:
        export_res = json.loads(resp.read().decode('utf-8'))
        assert export_res["status"] == "success"
        s = export_res["summary"]
        print(f" Full Agency Backup: Leads={s['total_leads']}, Invoices={s['total_invoices']}, Projects={s['total_projects']}, Schedules={s['scheduled_posts']}, Brands={s['connected_brands']}")

    # 6. Verify Office Pulse Reflects All Changes
    req = urllib.request.Request(f"{BASE_URL}/api/agency/office-pulse")
    with urllib.request.urlopen(req) as resp:
        pulse_res = json.loads(resp.read().decode('utf-8'))
        assert pulse_res["status"] == "success"
        top_msg = pulse_res["watercooler_feed"][0]
        assert "CONGRATULATIONS" in top_msg["message"]
        print(f" Verified Office Watercooler Top Feed: '{top_msg['message'][:60]}...'")

    print("\n ALL ADVANCED FEATURES & AUTOMATIONS VERIFIED 100%! SYSTEM READY.")

if __name__ == "__main__":
    test_all_features_complete()
