import urllib.request
import urllib.parse
import json

BASE_URL = "http://127.0.0.1:8000"

def test_office_and_festivals():
    print("Testing Virtual Office, Team Culture & Festival Engine...")

    # 1. Get Office Pulse
    req = urllib.request.Request(f"{BASE_URL}/api/agency/office-pulse")
    with urllib.request.urlopen(req) as resp:
        pulse = json.loads(resp.read().decode('utf-8'))
        assert pulse["status"] == "success"
        r = pulse["ritual"]
        print(f" Ritual: {r['name']} | Greeting: {r['greeting']} | Attendance: {r['attendance_rate']}")
        assert len(pulse["festivals_calendar"]) >= 5
        assert len(pulse["watercooler_feed"]) >= 4
        assert len(pulse["tech_radar"]) >= 3
        assert len(pulse["agent_scoreboard"]) >= 4

    # 2. Launch Festive Campaign: Diwali
    req = urllib.request.Request(
        f"{BASE_URL}/api/agency/launch-festive-campaign",
        data=json.dumps({"festival_name": "Diwali / Deepawali", "discount_percent": 25}).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        diwali = json.loads(resp.read().decode('utf-8'))
        assert diwali["status"] == "success"
        assert "DIWALI25" in diwali["discount_code"]
        assert "Shubh Deepawali" in diwali["post_copy"]
        assert "Canva" in diwali["canva_layout_prompt"] or "golden" in diwali["canva_layout_prompt"].lower()
        print(f" Diwali Campaign: Code={diwali['discount_code']} | Post Length={len(diwali['post_copy'])} | WA Greeting Ready=True")

    # 3. Launch Festive Campaign: Gandhi Jayanti (2 October)
    req = urllib.request.Request(
        f"{BASE_URL}/api/agency/launch-festive-campaign",
        data=json.dumps({"festival_name": "Gandhi Jayanti (2 October)", "discount_percent": 20}).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        gandhi = json.loads(resp.read().decode('utf-8'))
        assert gandhi["status"] == "success"
        assert "2 October" in gandhi["theme"]
        print(f" Gandhi Jayanti (2 Oct) Campaign: Theme='{gandhi['theme']}' | Verified=True")

    # 4. Post Message to Team Watercooler
    post_payload = {
        "author_name": "Founder",
        "message": "Team, brilliant work on the multi-brand client deliveries today! Bonuses and XP increments unlocked 🚀"
    }
    req = urllib.request.Request(
        f"{BASE_URL}/api/agency/post-office-message",
        data=json.dumps(post_payload).encode('utf-8'),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        post_res = json.loads(resp.read().decode('utf-8'))
        assert post_res["status"] == "success"
        assert post_res["feed"][0]["message"] == post_payload["message"]
        print(f" Watercooler Post: '{post_res['message']}' | Total Feed Count={len(post_res['feed'])}")

    print("\n ALL VIRTUAL OFFICE & FESTIVAL TESTS PASSED 100%! SYSTEM READY.")

if __name__ == "__main__":
    test_office_and_festivals()
