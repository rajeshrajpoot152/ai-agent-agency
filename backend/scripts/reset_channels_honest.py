from backend.app.core.database import execute_db, query_db

def reset_honest():
    execute_db("""
        UPDATE channel_integrations
        SET status = 'disconnected',
            auth_credentials = '{}',
            last_synced_at = NULL;
    """)
    rows = query_db("SELECT service_name, display_title, status FROM channel_integrations ORDER BY id;")
    print("Channel Integrations Reset to Honest Status:")
    for r in rows:
        print(f" - {r['display_title']} ({r['service_name']}): {r['status']}")

if __name__ == '__main__':
    reset_honest()
