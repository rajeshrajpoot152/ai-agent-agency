import json
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from backend.app.core.database import query_db, execute_db
from backend.app.core.llm_gateway import call_multi_model

# -----------------------------------------------------------------
# 1. AUTONOMOUS CORRECTION & RULE EXTRACTION ENGINE
# -----------------------------------------------------------------

CORRECTION_TRIGGER_PATTERNS = [
    r'\b(?:ye|yeh|yehi)\s+(?:galti|mistake|wrong|galat)\b',
    r'\b(?:aage\s+se|dobara|again|next\s+time)\s+(?:mat|nahi|never|not)\b',
    r'\b(?:mat\s+karna|nahi\s+karna|never\s+do|don\'t\s+do|stop\s+doing)\b',
    r'\b(?:always|hamesha|har\s+baar|strictly)\s+(?:use|rakhna|karna|prefer)\b',
    r'\b(?:correction|rule|rule\s+add|guardrail|instruction)\b',
    r'\b(?:galat\s+hai|wrong\s+approach|sahi\s+nahi\s+hai|change\s+this)\b',
    r'\b(?:yad\s+rakhna|yaad\s+rakhna|remember\s+this|note\s+this)\b'
]

def is_user_correction_intent(message: str) -> bool:
    """Checks if the user prompt is instructing the AI to correct a mistake or set a strict rule."""
    msg_lower = message.lower()
    for pattern in CORRECTION_TRIGGER_PATTERNS:
        if re.search(pattern, msg_lower):
            return True
    return False


def extract_and_persist_guardrail(
    user_instruction: str,
    project_id: Optional[str] = None,
    created_by: str = "Founder / Boss"
) -> Dict[str, Any]:
    """
    Extracts structured rule title, instruction constraint, and category from
    natural user feedback/correction and persists it into PostgreSQL negative_guardrails.
    """
    sys_prompt = """
You are the Chief Quality Officer & Guardrails Architect (Kabir).
The founder/boss just gave a correction or strict rule for the AI Agency.

Analyze the user's feedback and extract:
1. rule_title: Short, high-impact title (3-6 words, e.g. 'Short Bullet Summaries Only', 'No English In WhatsApp Drips', 'Max 10% Discount Rule')
2. rule_instruction: Clear, imperative, unambiguous constraint (e.g. 'Never output long multi-paragraph essays. Always format executive summaries in 3-4 bullet points maximum.')
3. category: One of ['tone', 'pricing', 'formatting', 'accuracy', 'communication', 'workflow']
4. affected_agents: Array of agent names affected (or ['All_Agents'])

Return ONLY valid JSON:
{
  "rule_title": "string",
  "rule_instruction": "string",
  "category": "string",
  "affected_agents": ["All_Agents"]
}
Do not use markdown codeblocks. Return pure JSON.
"""

    raw_ai = call_multi_model(
        provider="gemini",
        model_name="gemini-2.5-flash",
        system_prompt=sys_prompt,
        user_prompt=f"Founder's Correction: '{user_instruction}'",
        fallback_context="evaluation"
    )

    clean_json = re.sub(r'```json\s*|\s*```', '', raw_ai).strip()
    try:
        rule_data = json.loads(clean_json)
    except Exception:
        # Fallback rule extraction
        rule_data = {
            "rule_title": "Founder Direct Correction",
            "rule_instruction": user_instruction.strip(),
            "category": "workflow",
            "affected_agents": ["All_Agents"]
        }

    title = rule_data.get("rule_title", "Founder Directive")
    instruction = rule_data.get("rule_instruction", user_instruction)
    category = rule_data.get("category", "workflow")

    # Persist in negative_guardrails
    execute_db("""
        INSERT INTO negative_guardrails (rule_title, rule_instruction, category, enforcement_level)
        VALUES (%s, %s, %s, 'strict');
    """, (title, instruction, category))

    # Also record in learned_knowledge
    execute_db("""
        INSERT INTO learned_knowledge (agent_role, category, insight, confidence_score)
        VALUES ('All_Agents', %s, %s, 1.0);
    """, (category, f"Founder Rule [{title}]: {instruction}"))

    return {
        "status": "success",
        "rule_title": title,
        "rule_instruction": instruction,
        "category": category,
        "enforcement_level": "strict",
        "message": f"Rule '{title}' permanently recorded. All 26 agency agents will enforce it immediately."
    }


# -----------------------------------------------------------------
# 2. UNIVERSAL SYSTEM PROMPT GUARDRAIL INJECTOR
# -----------------------------------------------------------------

def get_active_guardrails_prompt_block() -> str:
    """
    Retrieves all active guardrails and returns a fortified prompt block
    to be prepended/appended to any agent or chat session.
    """
    try:
        rules = query_db("SELECT rule_title, rule_instruction FROM negative_guardrails ORDER BY created_at ASC;")
    except Exception:
        rules = []

    if not rules:
        return ""

    block = "\n\n### 🛡️ STRICT FOUNDER GUARDRAILS & ZERO-MISTAKE RULES (MANDATORY ENFORCEMENT):\n"
    block += "The founder has explicitly corrected the agency on the following rules. You MUST STRICTLY OBEY them. Never violate:\n"
    for idx, r in enumerate(rules, 1):
        block += f"{idx}. **{r['rule_title']}**: {r['rule_instruction']}\n"
    block += "⚠️ VIOLATING ANY RULE ABOVE IS A ZERO-TOLERANCE FAILURE.\n\n"
    return block


# -----------------------------------------------------------------
# 3. PRE-RESPONSE REDTEAM COMPLIANCE CHECK & AUTO-HEALING
# -----------------------------------------------------------------

def verify_and_auto_heal_response(
    original_response: str,
    active_guardrails: Optional[List[Dict[str, Any]]] = None
) -> Tuple[str, bool, Optional[str]]:
    """
    Critic_RedTeam_Agent (Kabir) audits the generated text against guardrails.
    If a violation is detected, it auto-corrects and rewrites the content.
    Returns (final_text, was_healed, violation_summary).
    """
    if not active_guardrails:
        try:
            active_guardrails = query_db("SELECT rule_title, rule_instruction FROM negative_guardrails;")
        except Exception:
            active_guardrails = []

    if not active_guardrails or len(original_response.strip()) < 20:
        return (original_response, False, None)

    # Fast heuristic check for common rules (e.g. length, greeting, jargon)
    rules_text = "\n".join([f"- {r['rule_title']}: {r['rule_instruction']}" for r in active_guardrails])
    
    audit_prompt = f"""
You are Kabir, Chief Quality Officer & RedTeam Auditor.
Check if the generated response violates ANY of these strict founder rules:
{rules_text}

Response to audit:
\"\"\"
{original_response[:2000]}
\"\"\"

If it passes all rules with 100% compliance, return ONLY: PASS
If it violates any rule, return REWRITE followed by the corrected version that fixes the violation.
Format:
REWRITE
<corrected response here>
"""

    audit_res = call_multi_model(
        provider="gemini",
        model_name="gemini-2.5-flash",
        system_prompt="You are a strict, no-compromise QA auditor. Ensure 100% compliance with founder guardrails.",
        user_prompt=audit_prompt,
        fallback_context="evaluation"
    ).strip()

    if audit_res.startswith("REWRITE"):
        healed_text = audit_res.replace("REWRITE", "", 1).strip()
        if len(healed_text) > 10:
            return (healed_text, True, "Self-healed response to strictly comply with founder guardrails.")

    return (original_response, False, None)
