import urllib.request
import urllib.parse
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    print("Testing Invoices and Content Calendar Endpoints...")

    # 1. Health check
    req = urllib.request.Request(f"{BASE_URL}/health")
    with urllib.request.urlopen(req) as resp:
        health_data = json.loads(resp.read().decode('utf-8'))
        print(f" Health check: {health_data}")
        assert resp.status == 200

    # 2. Generate Invoice
    inv_payload = {
        "client_name": "Rohan Deshmukh",
        "business_name": "Skyline Logistics Corp",
        "service_title": "Enterprise Next.js Web Portal & AI WhatsApp Fleet Bot",
        "amount": "₹60,000",
        "tax_percent": 18.0,
        "due_days": 7
    }
    req = urllib.request.Request(
        f"{BASE_URL}/api/leads/generate-invoice",
        data=json.dumps(inv_payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        inv_res = json.loads(resp.read().decode('utf-8'))
        print(f" Invoice Generated: {inv_res['invoice_number']} | Total: {inv_res['total_amount']} | URL: {inv_res['invoice_url']}")
        assert inv_res["status"] == "success"
        inv_id = inv_res["invoice_id"]
        inv_num = inv_res["invoice_number"]

    # 3. Fetch Invoice Details
    req = urllib.request.Request(f"{BASE_URL}/api/leads/invoices/{inv_id}")
    with urllib.request.urlopen(req) as resp:
        inv_details = json.loads(resp.read().decode('utf-8'))
        assert inv_details["status"] == "success"
        inv = inv_details["invoice"]
        print(f" Fetched Details: Subtotal={inv['subtotal']} | Tax={inv['tax_amount']} | Items Count={len(inv['line_items'])} | QR Present={bool(inv['upi_qr_url'])}")

    # 4. Fetch HTML Invoice Page
    req = urllib.request.Request(f"{BASE_URL}/invoice/{inv_id}")
    with urllib.request.urlopen(req) as resp:
        html_content = resp.read().decode('utf-8')
        assert "GST Tax Invoice" in html_content
        assert "Scan with Any UPI App" in html_content
        print(f" HTML Invoice Page Served ({len(html_content)} bytes)")

    # 5. Mark Invoice as Paid
    pay_payload = {"invoice_id": inv_id}
    req = urllib.request.Request(
        f"{BASE_URL}/api/leads/invoices/mark-paid",
        data=json.dumps(pay_payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        paid_res = json.loads(resp.read().decode('utf-8'))
        assert paid_res["status"] == "success"
        print(f" Mark Paid: {paid_res['message']}")

    # 6. Content Calendar Generation
    cal_payload = {"days": 30}
    req = urllib.request.Request(
        f"{BASE_URL}/api/agency/content-calendar/generate",
        data=json.dumps(cal_payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        cal_res = json.loads(resp.read().decode('utf-8'))
        assert cal_res["status"] == "success"
        print(f" Content Calendar: {cal_res['message']} ({cal_res['days_scheduled']} days)")

    # 7. Get Content Calendar
    req = urllib.request.Request(f"{BASE_URL}/api/agency/content-calendar")
    with urllib.request.urlopen(req) as resp:
        cal_list = json.loads(resp.read().decode('utf-8'))
        assert cal_list["status"] == "success"
        first_post = cal_list["calendar"][0]
        print(f" Calendar item 1: Day {first_post['day_number']} | {first_post['platform']} | Theme: {first_post['post_theme']}")

    # 8. Update post status
    update_payload = {"schedule_id": str(first_post['id']), "status": "published"}
    req = urllib.request.Request(
        f"{BASE_URL}/api/agency/content-calendar/update-status",
        data=json.dumps(update_payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        update_res = json.loads(resp.read().decode('utf-8'))
        assert update_res["status"] == "success"
        print(f" Status Update: {update_res['message']}")

    print("\n ALL VERIFICATIONS PASSED 100%! SYSTEM READY.")

if __name__ == "__main__":
    test_api()
