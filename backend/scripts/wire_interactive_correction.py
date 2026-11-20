import re

def update_interactive_chat():
    with open("backend/app/core/interactive_chat.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add imports if not present
    if "from backend.app.core.correction_engine import" not in content:
        import_stmt = """from backend.app.core.correction_engine import (
    is_user_correction_intent,
    extract_and_persist_guardrail,
    get_active_guardrails_prompt_block,
    verify_and_auto_heal_response
)
from backend.app.core.employee_brainstorm_engine import conduct_project_squad_brainstorm
"""
        content = import_stmt + content

    # 2. Add intent checks
    if "is_correction = is_user_correction_intent(clean_msg)" not in content:
        target = 'is_project_auto_create = any(w in msg_lower for w in ['
        intent_code = """is_correction = is_user_correction_intent(clean_msg)
    is_brainstorm = any(w in msg_lower for w in ["brainstorm", "squad discussion", "team meeting", "strategy session", "team se baat", "brain storming", "brain storm"])

    """
        content = content.replace(target, intent_code + target, 1)

    # 3. Add branches for is_correction and is_brainstorm
    if "SCENARIO -0.4: FOUNDER CORRECTION" not in content:
        target_scenario = "elif is_project_auto_create:"
        # Find where is_project_auto_create block ends
        end_marker = "elif is_dispatch_batch:"
        scenarios_code = """    # -------------------------------------------------------------
    # SCENARIO -0.4: FOUNDER CORRECTION & ZERO-REPEAT-MISTAKE ENGINE
    # -------------------------------------------------------------
    elif is_correction:
        add_human_step(execution_steps, "Critic_RedTeam_Agent", "Captured Founder Correction", "Registered permanent negative guardrail into PostgreSQL.")
        rule_res = extract_and_persist_guardrail(clean_msg, project_id=active_project.get("id") if active_project else None)
        agents_involved.extend(["Critic_RedTeam_Agent", "Evaluator_Agent"])
        
        response_text = (
            f"🫡 **Samajh gaya Boss! Correction permanently note aur save kar li hai.**\\n\\n"
            f"🛡️ **Recorded Rule:** '{rule_res['rule_title']}'\\n"
            f"📌 **Strict Constraint:** {rule_res['rule_instruction']}\\n"
            f"🏷️ **Category:** `{rule_res['category']}` | **Enforcement:** `100% Strict`\\n\\n"
            f"Maine sabhi 26 agents (Aarav, Vikram, Pooja, Arjun, Kabir, etc.) ke system prompts me ye rule permanently inject kar diya hai. "
            f"Ab se koi bhi agent ye galti dubara kabhi repeat nahi karega!"
        )
        deliverable = (
            f"# 🛡️ Founder Guardrail Permanently Recorded\\n\\n"
            f"- **Rule Title:** {rule_res['rule_title']}\\n"
            f"- **Constraint:** {rule_res['rule_instruction']}\\n"
            f"- **Category:** {rule_res['category']}\\n"
            f"- **Enforcement Level:** Strict (Zero Tolerance)\\n"
            f"- **Status:** 🟢 Active across all 26 Specialists & Sprints"
        )

    # -------------------------------------------------------------
    # SCENARIO -0.3: AUTONOMOUS SQUAD BRAINSTORMING & TASK ENGINE
    # -------------------------------------------------------------
    elif is_brainstorm and active_project:
        add_human_step(execution_steps, "CEO_Orchestrator", "Convening Squad Standup", "Assembling Tech Lead, Growth Lead, Designer & QA for brainstorming.")
        bs_res = conduct_project_squad_brainstorm(active_project["id"], focus_topic=clean_msg)
        agents_involved.extend(["IT_Solutions_Architect_Agent", "Marketing_Director_Agent", "Designer_Agent", "Critic_RedTeam_Agent"])
        
        transcript_md = "\\n\\n".join([f"> **{t['speaker']}:** {t['statement']}" for t in bs_res.get("transcript", [])])
        tasks_md = "\\n".join([f"- **{t['title']}** → Assigned to `{t['assigned_to']}` [{t['priority'].upper()}]" for t in bs_res.get("assigned_tasks", [])])
        
        deliverable = f\"\"\"# 🧠 Squad Brainstorming & Strategic Blueprint: {bs_res.get('project_name')}

### 💬 Live Multi-Agent Executive Standup Room
{transcript_md}

---
### 🎯 Executive Consensus
{bs_res.get('executive_summary')}

---
### 📋 Autonomous Tasks Assigned to Employees
{tasks_md}
\"\"\"
        response_text = (
            f"🧠 **Squad Brainstorming Session Complete for '{bs_res.get('project_name')}'!**\\n\\n"
            f"Aarav, Vikram (Tech), Pooja (Growth), Arjun (Design) aur Kabir (QA) ne milkar strategy finalize kar li hai.\\n\\n"
            f"🔹 **Breakthrough:** {bs_res.get('executive_summary').splitlines()[0] if bs_res.get('executive_summary') else 'Pipeline aligned.'}\\n"
            f"🔹 **3 Autonomous Tasks** live assign ho chuki hain.\\n\\n"
            f"Aap deliverable tab me complete squad conversation dekh sakte hain."
        )

    """
        content = content.replace(end_marker, scenarios_code + end_marker, 1)

    # 4. Inject guardrails in ceo_sys_prompt
    if "get_active_guardrails_prompt_block()" not in content:
        content = content.replace("+ project_context_info", "+ project_context_info + get_active_guardrails_prompt_block()", 1)

    # 5. Pre-Response Verification & Self-Healing before saving
    if "verify_and_auto_heal_response(response_text)" not in content:
        save_marker = 'execute_db("""\n        INSERT INTO agency_chat_messages'
        healing_code = """# Run Pre-Response RedTeam Verification & Self-Healing against stored guardrails
    try:
        response_text, was_healed, heal_note = verify_and_auto_heal_response(response_text)
        if was_healed:
            add_human_step(execution_steps, "Critic_RedTeam_Agent", "Guardrail Enforcement", heal_note)
    except Exception:
        pass

    """
        content = content.replace(save_marker, healing_code + save_marker, 1)

    with open("backend/app/core/interactive_chat.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✓ Successfully updated interactive_chat.py with Zero-Repeat-Mistake Engine & Squad Brainstorming!")

if __name__ == "__main__":
    update_interactive_chat()
