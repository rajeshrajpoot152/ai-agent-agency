import sys
from datetime import datetime
from backend.app.core.database import query_db, execute_db
from backend.app.graph.workflow import agency_graph

def run_outreach_batch(force: bool = False):
    print("\n🚀 Executing LangGraph Multi-Agent Outreach Batch...")
    initial_state = {
        "campaign_id": "",
        "campaign_name": "",
        "campaign_status": "Active",
        "daily_quota": 5,
        "sent_today": 0,
        "leads_to_process": [],
        "current_lead": None,
        "generated_message": None,
        "qa_approved": False,
        "qa_feedback": None,
        "retry_count": 0,
        "learned_insights": [],
        "workflow_status": "running",
        "logs": []
    }
    config = {"configurable": {"thread_id": f"cli_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"}}
    result = agency_graph.invoke(initial_state, config=config)
    print("\n--- LangGraph Execution Logs ---")
    for log in result.get("logs", []):
        print(f"  {log}")
    print(f"\nFinal Workflow Status: {result.get('workflow_status')}")
    print(f"Total Sent in this Batch: {result.get('sent_today', 0)}")
    return result

def show_status():
    print("\n" + "="*65)
    print("🏢 [AI AGENT AGENCY] Autonomous Master Status Report")
    print("="*65)

    # 1. Outreach Campaign Info
    campaign = query_db("SELECT * FROM outreach_campaigns LIMIT 1", fetchone=True)
    if campaign:
        print("\n📢 CAMPAIGN CONFIGURATION:")
        print(f"  Name:           {campaign['campaign_name']}")
        print(f"  Status:         {campaign['status']}  <-- [Active / Paused / Stopped]")
        print(f"  Daily Quota:    {campaign['daily_quota']} messages / day")
        print(f"  Scheduled Time: {campaign['scheduled_time']} (Window: {campaign.get('time_window_start', '10:00')} - {campaign.get('time_window_end', '18:00')})")
        print(f"  Delay Between:  {campaign.get('delay_between_messages_seconds', 120)} seconds")
    
    # 2. Leads Stats
    leads_stats = query_db("""
        SELECT 
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE status = 'pending') as pending,
            COUNT(*) FILTER (WHERE status = 'contacted') as contacted
        FROM outreach_leads;
    """, fetchone=True)
    
    # 3. Today's sent count
    today_sent_row = query_db("""
        SELECT COUNT(*) as sent_today 
        FROM outreach_message_logs 
        WHERE sent_at::date = CURRENT_DATE;
    """, fetchone=True)
    today_sent = today_sent_row['sent_today'] if today_sent_row else 0

    print("\n📊 LEADS & OUTREACH METRICS:")
    if leads_stats:
        print(f"  Total Leads in DB:  {leads_stats['total']}")
        print(f"  Pending Leads:      {leads_stats['pending']}")
        print(f"  Contacted Leads:    {leads_stats['contacted']}")
    print(f"  Sent Today:         {today_sent} / {campaign['daily_quota'] if campaign else 5}")

    # 4. Registered AI Agents
    try:
        agents = query_db("SELECT name, role, status FROM agents ORDER BY name;")
        if agents:
            print("\n🤖 AUTONOMOUS AI STAFF (No Humans):")
            for a in agents:
                print(f"  - {a['name']:<20} | Role: {a['role']:<35} | Status: {a['status']}")
    except Exception:
        pass

    # 5. Learned Knowledge
    try:
        knowledge = query_db("SELECT category, insight, confidence_score FROM learned_knowledge ORDER BY created_at DESC LIMIT 3;")
        if knowledge:
            print("\n🧠 RECENT SELF-TRAINED KNOWLEDGE:")
            for k in knowledge:
                print(f"  - [{k['category']}] ({float(k['confidence_score'])*100:.0f}% conf): {k['insight']}")
    except Exception:
        pass

    print("\n" + "="*65 + "\n")

def set_campaign_status(status: str):
    execute_db("UPDATE outreach_campaigns SET status = %s, updated_at = CURRENT_TIMESTAMP;", (status,))
    print(f"✅ Campaign status updated to: '{status}'")

def set_campaign_time(time_str: str):
    execute_db("UPDATE outreach_campaigns SET scheduled_time = %s, updated_at = CURRENT_TIMESTAMP;", (time_str,))
    print(f"✅ Campaign scheduled time set to: '{time_str}'")

def set_campaign_quota(quota: int):
    execute_db("UPDATE outreach_campaigns SET daily_quota = %s, updated_at = CURRENT_TIMESTAMP;", (quota,))
    print(f"✅ Daily message quota updated to: {quota}")

def print_help():
    print("""
Usage: python agency_cli.py [COMMAND]

COMMANDS:
  status                     Show complete status (leads, campaign, agents, learning)
  pause                      STOP/PAUSE outreach campaign immediately
  resume                     RESUME/START outreach campaign
  set-time "HH:MM:SS"        Change daily scheduled time (e.g. set-time "11:30:00")
  set-quota [number]         Change daily message quota (e.g. set-quota 5)
  run-outreach               Run today's batch of 5 personalized messages via LangGraph
""")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd == "status":
        show_status()
    elif cmd == "pause":
        set_campaign_status("Paused")
    elif cmd == "resume":
        set_campaign_status("Active")
    elif cmd == "set-time" and len(sys.argv) > 2:
        set_campaign_time(sys.argv[2])
    elif cmd == "set-quota" and len(sys.argv) > 2:
        set_campaign_quota(int(sys.argv[2]))
    elif cmd == "run-outreach":
        force = "--force" in sys.argv
        run_outreach_batch(force=force)
    else:
        print_help()
