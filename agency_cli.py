import sys
from datetime import datetime
from core.db import query_db, execute_db
from core.outreach_engine import run_daily_outreach
from core.task_delegator import delegate_task, run_agent_task_worker
from core.self_learning import run_self_training_reflection, auto_create_new_skill

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
        print(f"  Scheduled Time: {campaign['scheduled_time']} (Window: {campaign['time_window_start']} - {campaign['time_window_end']})")
        print(f"  Delay Between:  {campaign['delay_between_messages_seconds']} seconds")
    
    # 2. Leads Stats
    leads_stats = query_db("""
        SELECT 
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE status = 'pending') as pending,
            COUNT(*) FILTER (WHERE status = 'contacted') as contacted
        FROM outreach_leads;
    """, fetchone=True)
    
    # 3. Today's sent count
    today_sent = query_db("""
        SELECT COUNT(*) as sent_today 
        FROM outreach_message_logs 
        WHERE sent_at::date = CURRENT_DATE;
    """, fetchone=True)['sent_today']

    print("\n📊 LEADS & OUTREACH METRICS:")
    print(f"  Total Leads in DB:  {leads_stats['total']}")
    print(f"  Pending Leads:      {leads_stats['pending']}")
    print(f"  Contacted Leads:    {leads_stats['contacted']}")
    print(f"  Sent Today:         {today_sent} / {campaign['daily_quota'] if campaign else 5}")

    # 4. Registered AI Agents
    agents = query_db("SELECT name, role, status FROM agents ORDER BY name;")
    print("\n🤖 AUTONOMOUS AI STAFF (No Humans):")
    for a in agents:
        print(f"  - {a['name']:<20} | Role: {a['role']:<35} | Status: {a['status']}")

    # 5. Learned Knowledge
    knowledge = query_db("SELECT category, insight, confidence_score FROM learned_knowledge ORDER BY created_at DESC LIMIT 3;")
    if knowledge:
        print("\n🧠 RECENT SELF-TRAINED KNOWLEDGE:")
        for k in knowledge:
            print(f"  - [{k['category']}] ({float(k['confidence_score'])*100:.0f}% conf): {k['insight']}")

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
  run-outreach [--force]     Run today's batch of 5 personalized messages
  self-train                 Run Evaluator Agent reflection loop to self-train
  delegate                   Demonstrate Agent A assigning task to Agent B
  work [agent_name]          Run worker loop for an agent (e.g. work Outreach_Agent)
  create-skill "name" "desc" Dynamically create a new skill in database
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
        run_daily_outreach(force=force)
    elif cmd == "self-train":
        run_self_training_reflection()
    elif cmd == "delegate":
        delegate_task(
            assigned_by="CEO_Agent",
            assigned_to="Outreach_Agent",
            title="Analyze Competitor Real-Estate Pricing",
            objective="Inspect top real-estate builders in Noida and provide a 3-bullet competitive advantage summary."
        )
    elif cmd == "work" and len(sys.argv) > 2:
        run_agent_task_worker(sys.argv[2])
    elif cmd == "create-skill" and len(sys.argv) > 3:
        auto_create_new_skill(
            skill_name=sys.argv[2],
            description=sys.argv[3],
            code_or_prompt="Custom prompt/logic synthesized dynamically by AI agent."
        )
    else:
        print_help()
