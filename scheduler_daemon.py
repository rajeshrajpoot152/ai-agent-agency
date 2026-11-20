import time
from datetime import datetime
from core.db import query_db
from core.outreach_engine import run_daily_outreach
from core.self_learning import run_self_training_reflection

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
                # Agent is sleeping/paused
                time.sleep(10)
                continue

            # Check if scheduled time reached and hasn't run today
            if scheduled_time and (now_time >= scheduled_time) and (last_trigger_date != today_str):
                print(f"\n⏰ [SCHEDULE TRIGGER] Time is {now_time.strftime('%H:%M:%S')}. Triggering daily outreach batch...")
                run_daily_outreach(force=False)
                last_trigger_date = today_str
                
                # Run autonomous self-training loop after outreach
                run_self_training_reflection()

            time.sleep(30) # Check every 30 seconds
        except KeyboardInterrupt:
            print("\nDaemon loop terminated by user.")
            break
        except Exception as e:
            print(f"[Error in daemon loop]: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_daemon_loop()
