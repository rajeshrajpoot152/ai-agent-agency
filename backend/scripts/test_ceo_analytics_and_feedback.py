import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:8000"

def test_ceo_analytics_and_feedback():
    print("Testing CEO Analytics, Client Feedback & Weekly Progress Digests Suite...")

    # 1. Health check
    req = urllib.request.Request(f"{BASE_URL}/health")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200
        print(" Health Check Passed.")

    # 2. Financial Analytics
    req = urllib.request.Request(f"{BASE_URL}/api/agency/financial-analytics")
    with urllib.request.urlopen(req) as resp:
        fin_res = json.loads(resp.read().decode('utf-8'))
        assert fin_res["status"] == "success"
        s = fin_res["summary"]
        tax = fin_res["tax_compliance"]
        print(f" CEO Financials: Collected={s['total_cash_collected']} ({s['paid_invoices_count']} paid) | Pending={s['pending_receivables']} | Booked={s['total_booked_revenue']} | GST Pool={tax['total_gst_collected']}")
        assert len(fin_res["brand_breakdown"]) == 6
        print(f" 6 Connected Brands Verified in Revenue Distribution: {[b['brand_name'] for b in fin_res['brand_breakdown']]}")

    # 3. Weekly Client Progress Digests
    req = urllib.request.Request(f"{BASE_URL}/api/agency/weekly-progress-digests")
    with urllib.request.urlopen(req) as resp:
        dig_res = json.loads(resp.read().decode('utf-8'))
        assert dig_res["status"] == "success"
        assert dig_res["total_active_projects"] > 0
        first_d = dig_res["digests"][0]
        assert "wa.me" in first_d["whatsapp_link"]
        assert "portal" in first_d["portal_url"]
        print(f" Weekly Monday Digests: {dig_res['total_active_projects']} active project briefs | Sample: {first_d['business_name']} ({first_d['progress_percent']}% sprint)")

    # 4. Dispatch Weekly Digests
    req = urllib.request.Request(
        f"{BASE_URL}/api/agency/dispatch-weekly-digests",
        data=b"{}",
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        disp_res = json.loads(resp.read().decode('utf-8'))
        assert disp_res["status"] == "success"
        print(f" Dispatched Weekly Digests: {disp_res['message']}")

    # 5. Get a project ID for feedback & asset upload testing
    proj_id = first_d["project_id"]

    # Submit Client Feedback (e.g. Revision Request)
    fb_payload = {
        "project_id": proj_id,
        "client_name": first_d["client_name"],
        "milestone_index": 2,
        "feedback_type": "revision",
        "message": "Please adjust hero button color to brand hex #4F46E5 and add dark mode toggle."
    }
    req = urllib.request.Request(
        f"{BASE_URL}/api/leads/projects/submit-feedback",
        data=json.dumps(fb_payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        fb_res = json.loads(resp.read().decode('utf-8'))
        assert fb_res["status"] == "success"
        print(f" Client Feedback Submitted: Phase {fb_payload['milestone_index']} ({fb_payload['feedback_type']}) - Total Feedbacks: {fb_res['total_feedbacks']}")

    # Submit Client Asset Upload
    asset_payload = {
        "project_id": proj_id,
        "asset_name": "Official High-Res Vector Brand Logo",
        "asset_type": "logo",
        "asset_url_or_note": "https://drive.google.com/file/d/sample-brand-logo/view",
        "uploaded_by": first_d["client_name"]
    }
    req = urllib.request.Request(
        f"{BASE_URL}/api/leads/projects/upload-asset",
        data=json.dumps(asset_payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        asset_res = json.loads(resp.read().decode('utf-8'))
        assert asset_res["status"] == "success"
        print(f" Client Asset Uploaded: {asset_payload['asset_name']} ({asset_payload['asset_type']}) - Total Assets: {asset_res['total_assets']}")

    # 6. Verify Project Details Returns Both Feedback & Assets
    req = urllib.request.Request(f"{BASE_URL}/api/leads/projects/{proj_id}")
    with urllib.request.urlopen(req) as resp:
        p_res = json.loads(resp.read().decode('utf-8'))
        assert p_res["status"] == "success"
        p = p_res["project"]
        assert len(p["client_feedback"]) >= 1
        assert len(p["client_assets"]) >= 1
        print(f" Verified Project Portal Data: {len(p['client_feedback'])} feedbacks, {len(p['client_assets'])} assets present.")

    # 7. Verify Team Watercooler Received Live Notifications
    req = urllib.request.Request(f"{BASE_URL}/api/agency/office-pulse")
    with urllib.request.urlopen(req) as resp:
        pulse_res = json.loads(resp.read().decode('utf-8'))
        assert pulse_res["status"] == "success"
        feed = pulse_res["watercooler_feed"]
        top_messages = [m["message"] for m in feed[:5]]
        has_fb_alert = any("CLIENT FEEDBACK" in m for m in top_messages)
        has_asset_alert = any("NEW ASSET ATTACHED" in m for m in top_messages)
        assert has_fb_alert, "Expected client feedback alert in watercooler"
        assert has_asset_alert, "Expected client asset alert in watercooler"
        print(f" Verified Team Watercooler Alerts: Client Feedback & Asset Ingestion active in feed!")

    print("\n ALL CEO ANALYTICS, REVENUE BREAKDOWN & CLIENT PORTAL UPGRADES VERIFIED 100%!")

if __name__ == "__main__":
    test_ceo_analytics_and_feedback()
