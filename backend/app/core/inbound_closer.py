import json
from backend.app.core.database import query_db, execute_db
from backend.app.core.llm_gateway import call_multi_model

def handle_inbound_message(lead_id: str, incoming_text: str) -> dict:
    """
    Inbound Sales Closer Agent:
    Handles incoming client messages, overcomes objections, and closes deals!
    """
    lead = query_db("SELECT * FROM outreach_leads WHERE id = %s", (lead_id,), fetchone=True)
    if not lead:
        return {"error": "Lead not found"}

    name = lead['full_name'] or 'Sir/Madam'
    biz = lead['business_name'] or 'Business'
    industry = lead['industry'] or 'General'

    # Fetch agent configuration from DB
    agent = query_db("SELECT * FROM agents WHERE name = 'Inbound_Closer_Agent'", fetchone=True)
    provider = agent['model_provider'] if agent else "openai"
    model = agent['model_name'] if agent else "gpt-4o"
    sys_prompt = agent['system_prompt'] if agent else "You are an expert sales closer."

    # Past chat history
    history = query_db("""
        SELECT sender, message_text FROM lead_conversations 
        WHERE lead_id = %s ORDER BY created_at ASC LIMIT 6;
    """, (lead_id,))

    history_str = "\n".join([f"{h['sender'].upper()}: {h['message_text']}" for h in history])

    system_instruction = (
        f"{sys_prompt}\n"
        f"Prospect Name: {name}\n"
        f"Business: {biz} (Industry: {industry})\n"
        f"Goal: Guide the prospect politely, explain how our autonomous AI agents save 20+ hours/week, "
        f"answer any questions about pricing or process, and encourage booking a 15-minute onboarding call or starting with a pilot."
    )

    user_prompt = f"PREVIOUS CHAT:\n{history_str}\n\nLATEST CLIENT MESSAGE: \"{incoming_text}\"\n\nWrite your persuasive, warm, and concise WhatsApp reply:"

    ai_reply = call_multi_model(
        provider=provider,
        model_name=model,
        system_prompt=system_instruction,
        user_prompt=user_prompt
    )

    # Determine deal stage dynamically
    deal_stage = "inquiry"
    txt = (incoming_text + " " + ai_reply).lower()
    if "price" in txt or "cost" in txt or "charges" in txt:
        deal_stage = "pricing"
    elif "call" in txt or "meeting" in txt or "time" in txt or "demo" in txt:
        deal_stage = "meeting_booked"
    elif "ready" in txt or "start" in txt or "onboard" in txt:
        deal_stage = "closed_won"

    # 1. Log Client's incoming message
    execute_db("""
        INSERT INTO lead_conversations (lead_id, sender, message_text, deal_stage)
        VALUES (%s, 'lead', %s, %s);
    """, (lead_id, incoming_text, deal_stage))

    # 2. Log AI Closer's reply
    execute_db("""
        INSERT INTO lead_conversations (lead_id, sender, message_text, deal_stage)
        VALUES (%s, 'ai_closer', %s, %s);
    """, (lead_id, ai_reply, deal_stage))

    # 3. Update lead status in DB
    execute_db("""
        UPDATE outreach_leads 
        SET status = 'replied', notes = %s 
        WHERE id = %s;
    """, (f"Deal Stage: {deal_stage.upper()}", lead_id))

    return {
        "lead_id": lead_id,
        "lead_name": name,
        "business": biz,
        "client_message": incoming_text,
        "ai_closer_reply": ai_reply,
        "deal_stage": deal_stage
    }
