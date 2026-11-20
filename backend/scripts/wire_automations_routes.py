import re

def update_routes():
    with open("backend/app/api/routes_projects_hub.py", "r", encoding="utf-8") as f:
        code = f.read()

    new_endpoints = '''
# -------------------------------------------------------------
# 7. AUTOMATION 1: AUTO-LEAD PROSPECTING ENGINE
# -------------------------------------------------------------
class AutoHuntLeadsRequest(BaseModel):
    count: int = 5
    location: Optional[str] = "India / Global"

@router.post("/{project_id}/leads/auto-hunt")
def auto_hunt_leads_endpoint(project_id: str, req: AutoHuntLeadsRequest):
    """
    Autonomously hunts, qualifies & inserts verified B2B/B2C leads
    strictly into the active project database container (Zero Leakage).
    """
    from backend.scripts.test_automations import auto_hunt_leads_for_project
    return auto_hunt_leads_for_project(project_id, count=req.count, location=req.location or "")

# -------------------------------------------------------------
# 8. AUTOMATION 2: 3-STEP SMART DRIP SEQUENCES
# -------------------------------------------------------------
@router.get("/{project_id}/outreach/drip-sequence")
def get_drip_sequence_endpoint(project_id: str, client_name: str = "Client"):
    """
    Generates tailored 3-step high-converting follow-up sequence
    (Day 1 Intro, Day 3 Proof, Day 7 Breakup) for the active project.
    """
    from backend.scripts.test_automations import generate_drip_sequence
    return generate_drip_sequence(project_id, client_name=client_name)

# -------------------------------------------------------------
# 9. AUTOMATION 3: 1-CLICK GST INVOICE & UPI QR CODE GENERATOR
# -------------------------------------------------------------
class GenerateInvoiceRequest(BaseModel):
    amount: float = 45000.0

@router.post("/{project_id}/leads/{lead_id}/generate-invoice")
def generate_invoice_endpoint(project_id: str, lead_id: str, req: GenerateInvoiceRequest):
    """
    Generates official GST invoice, dynamic UPI QR code,
    and ready-to-send WhatsApp payment link for the client.
    """
    from backend.scripts.test_automations import generate_invoice_for_lead
    return generate_invoice_for_lead(project_id, lead_id, amount=req.amount)

# -------------------------------------------------------------
# 10. AUTOMATION 4: WEEKLY MARKET & COMPETITOR SPY
# -------------------------------------------------------------
@router.get("/{project_id}/market-spy")
def get_market_spy_endpoint(project_id: str):
    """
    Returns weekly market intelligence, competitor pricing shifts,
    and ranking signals for the active project.
    """
    from backend.scripts.test_automations import get_market_spy_intelligence
    return get_market_spy_intelligence(project_id)
'''

    if "@router.post(\"/{project_id}/leads/auto-hunt\")" not in code:
        code = code + "\n" + new_endpoints

    with open("backend/app/api/routes_projects_hub.py", "w", encoding="utf-8") as f:
        f.write(code)

    print("✓ Successfully wired all 4 automations into routes_projects_hub.py!")

if __name__ == "__main__":
    update_routes()
