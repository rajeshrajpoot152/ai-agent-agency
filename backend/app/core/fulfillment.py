import json
from datetime import datetime
from backend.app.core.database import query_db, execute_db
from backend.app.core.llm_gateway import call_multi_model

def auto_fulfill_deal(lead_id: str) -> dict:
    """
    Fulfillment Agent:
    Once a deal is agreed upon, this agent immediately synthesizes the custom AI deliverable
    and commits it into PostgreSQL 'content_deliverables'.
    """
    lead = query_db("SELECT * FROM outreach_leads WHERE id = %s", (lead_id,), fetchone=True)
    if not lead:
        return {"error": "Lead not found"}

    name = lead['full_name'] or "Client"
    biz = lead['business_name'] or "Company"
    industry = lead['industry'] or "General"

    system_instruction = (
        "You are the Service_Fulfillment_Agent of an elite AI agency. "
        "Create a comprehensive 4-point customized AI Automation Roadmap for this client. "
        "Include: 1) WhatsApp AI Bot Setup, 2) Lead Scraper Strategy, 3) 24/7 Auto CRM, 4) Expected ROI."
    )

    user_prompt = f"CLIENT: {name}\nBUSINESS: {biz} ({industry})"

    deliverable_text = call_multi_model(
        provider="claude",
        model_name="claude-3-5-sonnet-20241022",
        system_prompt=system_instruction,
        user_prompt=user_prompt
    )

    # Save to content_deliverables table
    execute_db("""
        INSERT INTO content_deliverables (client_id, platform_name, content_text, status, published_at)
        VALUES (NULL, 'whatsapp_package', %s, 'approved', CURRENT_TIMESTAMP);
    """, (deliverable_text,))

    # Update lead status to 'closed_won'
    execute_db("""
        UPDATE outreach_leads 
        SET status = 'deal_won', notes = 'Closed Won - Deliverable Generated & Ready to Ship' 
        WHERE id = %s;
    """, (lead_id,))

    return {
        "status": "success",
        "client": name,
        "business": biz,
        "deliverable_summary": deliverable_text[:300] + "..."
    }
