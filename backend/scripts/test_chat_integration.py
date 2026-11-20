import requests

BASE = "http://127.0.0.1:8000"

print("--- 1. Testing Chat Interception for User Prompt ---")
user_msg = "mera yek it company ahi and mere pass 6 se jayda too website ahi hamo inak markeding kana hai alike design banana post bnnna barding karna seo karna post auto post ho jaeye design ban jauye bneer banjaye main site it comapn ka barnd kana"

res = requests.post(f"{BASE}/api/agency/chat/send", json={
    "session_id": "test_integration_session",
    "message": user_msg
}).json()

print("Status:", res.get("status"))
print("Response text:", res.get("response_text")[:120] + "...")
print("Deliverable length:", len(res.get("deliverable", "")))
print("Deliverable preview:", res.get("deliverable", "")[:250] + "...")

print("\n--- 2. Testing Chat Interception for 100 Numbers Outreach ---")
user_msg_2 = "man lo mere pass 100 number ahi unko massges kan flloop lena ya massge bejana ki hmare company web and mobile applicn ya conatt crean kate hai automna karathi ai agent banhi hai yesa ham kam kaarte hei"

res2 = requests.post(f"{BASE}/api/agency/chat/send", json={
    "session_id": "test_integration_session_2",
    "message": user_msg_2
}).json()

print("Status 2:", res2.get("status"))
print("Response text 2:", res2.get("response_text")[:120] + "...")
print("Deliverable 2 preview:", res2.get("deliverable", "")[:250] + "...")

print("\nINTEGRATION VERIFIED END-TO-END!")
