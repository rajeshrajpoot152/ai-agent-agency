from backend.app.core.database import query_db

def inspect_agent_tables():
    for t in ['agents', 'learned_knowledge', 'negative_guardrails', 'autonomous_tasks']:
        cols = query_db(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{t}';")
        print(f"--- Table: {t} ---")
        for c in cols:
            print(f"  {c['column_name']} ({c['data_type']})")
        print()

if __name__ == "__main__":
    inspect_agent_tables()
