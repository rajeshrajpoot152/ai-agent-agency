import time
from datetime import datetime
from backend.app.core.database import query_db
from backend.app.graph.workflow import agency_graph

def run_outreach_batch():
    """Runs a batch through LangGraph multi-agent workflow."""
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
    config = {"configurable": {"thread_id": f"daemon_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"}}
    result = agency_graph.invoke(initial_state, config=config)
    return result

def run_daemon_loop():
    print("\n" + "="*65)
    print("🚀 [AGENCY DAEMON] 100% Autonomous AI Agency Loop Started!")
    print("="*65)
    print("Watching PostgreSQL DB 'agency_master' in real-time...")
    print("Press Ctrl+C to terminate.\n")

    last_trigger_date = None

    while True:
        try:
            campaign = query_db("SELECT * FROM outreach_campaigns LIMIT 1", fetchone=True)
            if not campaign:
                time.sleep(10)
                continue

            status = campaign['status']
            scheduled_time = campaign['scheduled_time']
            today_str = datetime.now().strftime("%Y-%m-%d")
            now_time = datetime.now().time()

            # Dynamic check on DB status
            if status.lower() in ['paused', 'stopped']:
                time.sleep(10)
                continue

            # Check if scheduled time reached and hasn't run today
            if scheduled_time and (now_time >= scheduled_time) and (last_trigger_date != today_str):
                print(f"\n⏰ [SCHEDULE TRIGGER] Time is {now_time.strftime('%H:%M:%S')}. Triggering LangGraph outreach batch...")
                res = run_outreach_batch()
                print(f"✅ Batch completed. Status: {res.get('workflow_status')}, Processed: {res.get('sent_today', 0)}")
                last_trigger_date = today_str

            time.sleep(30) # Check every 30 seconds
        except KeyboardInterrupt:
            print("\nDaemon loop terminated by user.")
            break
        except Exception as e:
            print(f"[Error in daemon loop]: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_daemon_loop()
