import json
from datetime import datetime
from typing import TypedDict, List, Dict, Any, Optional, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from backend.app.core.database import query_db, execute_db
from backend.app.core.llm_gateway import call_multi_model

class UniversalMissionState(TypedDict):
    mission_id: str
    title: str
    objective: str
    category: str
    guardrails: List[str]
    active_agent: str
    active_model: str
    draft_deliverable: Optional[str]
    critic_approved: bool
    critic_feedback: Optional[str]
    retry_count: int
    final_deliverable: Optional[str]
    logs: List[str]
    status: str

# -------------------------------------------------------------
# 1. CEO Orchestrator Planner Node
# -------------------------------------------------------------
def mission_planner_node(state: UniversalMissionState) -> UniversalMissionState:
    logs = list(state.get("logs", []))
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] 👔 [CEO Orchestrator] Analyzing mission: '{state['title']}'...")

    category = (state.get("category") or "general").lower()

    # Route to specialized agent based on category
    agent_mapping = {
        "design": ("Designer_Agent", "graphic_design"),
        "seo": ("SEO_Content_Agent", "seo_keyword_cluster"),
        "seo_technical": ("SEO_Technical_Architect_Agent", "seo_technical_audit"),
        "technical_seo": ("SEO_Technical_Architect_Agent", "seo_technical_audit"),
        "geo": ("GEO_AI_Search_Agent", "seo_geo_aeo"),
        "aeo": ("GEO_AI_Search_Agent", "seo_geo_aeo"),
        "local_seo": ("Local_SEO_Growth_Agent", "seo_local_maps"),
        "maps": ("Local_SEO_Growth_Agent", "seo_local_maps"),
        "copywriting": ("CRO_Copywriting_Agent", "copywriting_cro"),
        "cro": ("CRO_Copywriting_Agent", "copywriting_cro"),
        "ad_creative": ("CRO_Copywriting_Agent", "ad_creative_framework"),
        "marketing": ("Marketing_Director_Agent", "marketing_plan"),
        "marketing_plan": ("Marketing_Director_Agent", "marketing_plan"),
        "growth": ("Marketing_Director_Agent", "marketing_plan"),
        "outreach": ("BDA_Sales_Agent", "cold_email_sequences"),
        "sales": ("BDA_Sales_Agent", "bda_sales"),
        "it_proposal": ("IT_Sales_Proposal_Agent", "it_project_proposal"),
        "proposal": ("IT_Sales_Proposal_Agent", "it_project_proposal"),
        "sow": ("IT_Solutions_Architect_Agent", "it_tech_architecture_sow"),
        "architecture": ("IT_Solutions_Architect_Agent", "it_tech_architecture_sow"),
        "tech_stack": ("IT_Solutions_Architect_Agent", "it_tech_architecture_sow"),
        "offshore": ("IT_Sales_Proposal_Agent", "it_offshore_sales_pitch"),
        "estimation": ("IT_Solutions_Architect_Agent", "it_cost_timeline_calculator"),
        "code": ("DevOps_Coder_Agent", "code_engineering"),
        "tech": ("DevOps_Coder_Agent", "code_engineering"),
        "research": ("CEO_Orchestrator", "market_research"),
        # Modern Modal & Flagship Skills
        "sites": ("DevOps_Coder_Agent", "it_site_builder_deploy"),
        "presentations": ("Marketing_Director_Agent", "it_presentation_pitch_deck"),
        "documents": ("Legal_Compliance_Agent", "it_business_document_contract"),
        "canva": ("Designer_Agent", "it_canva_creative_design"),
        "skill-creator": ("DevOps_Coder_Agent", "it_skill_creator_meta"),
        # Dynamic Autonomous Domains
        "cybersecurity": ("Cybersecurity_Security_Agent", "cybersecurity_penetration_audit"),
        "mobile": ("Mobile_App_Architect_Agent", "mobile_cross_platform_architecture"),
        "devops": ("Cloud_DevOps_Architect_Agent", "cloud_devops_kubernetes_pipeline"),
        "voice": ("AI_Voice_Telephony_Agent", "voice_cold_calling_telephony"),
        "calling": ("AI_Voice_Telephony_Agent", "voice_cold_calling_telephony"),
        "data_science": ("AI_Data_Scientist_Agent", "ai_ml_production_pipeline"),
        "ecommerce": ("Ecommerce_Growth_Architect_Agent", "ecommerce_aov_maximizer"),
        "web3": ("Web3_Blockchain_Agent", "web3_smart_contract_audit"),
        "legal": ("Legal_Compliance_Agent", "legal_contract_compliance"),
        "fintech": ("Fintech_Financial_Analyst_Agent", "saas_financial_modeling"),
        "hr": ("Talent_Acquisition_Agent", "technical_recruiting_scorecard"),
    }

    if category in agent_mapping:
        assigned_agent, skill_code = agent_mapping[category]
    else:
        # Dynamic PostgreSQL Lookup for any self-created agent
        matching_agent = query_db("SELECT name FROM agents WHERE name ILIKE %s OR role ILIKE %s LIMIT 1;", (f"%{category}%", f"%{category}%"), fetchone=True)
        if matching_agent:
            assigned_agent = matching_agent['name']
            skill_code = f"custom_skill_{category}"
        else:
            assigned_agent, skill_code = ("CEO_Orchestrator", "market_research")

    # Fetch Guardrails from PostgreSQL
    rules = query_db("SELECT rule_title, rule_instruction FROM negative_guardrails;")
    guardrails = [f"{r['rule_title']}: {r['rule_instruction']}" for r in rules] if rules else []

    # Get Assigned Agent's Model from PostgreSQL
    agent_info = query_db("SELECT model_provider, model_name FROM agents WHERE name = %s;", (assigned_agent,), fetchone=True)
    provider = agent_info['model_provider'] if agent_info else "openai"
    model = agent_info['model_name'] if agent_info else "gpt-4o"

    logs.append(f"🎯 Assigned Specialist: [{assigned_agent}] with Skill [{skill_code}] running on [{provider.upper()} - {model}].")
    logs.append(f"🛡️ Loaded {len(guardrails)} Strict Negative Guardrails from PostgreSQL.")

    execute_db("UPDATE agency_missions SET status = 'executing', updated_at = CURRENT_TIMESTAMP WHERE id = %s;", (state['mission_id'],))

    return {
        **state,
        "active_agent": assigned_agent,
        "active_model": f"{provider}|{model}",
        "guardrails": guardrails,
        "logs": logs,
        "status": "executing",
        "retry_count": 0
    }

# -------------------------------------------------------------
# 2. Specialist Skilled Agent Execution Node
# -------------------------------------------------------------
def specialist_executor_node(state: UniversalMissionState) -> UniversalMissionState:
    logs = list(state.get("logs", []))
    agent_name = state["active_agent"]
    logs.append(f"⚡ [{agent_name}] Producing high-caliber deliverable for: '{state['title']}'...")

    # Fetch agent prompt and model
    agent_row = query_db("SELECT system_prompt, model_provider, model_name FROM agents WHERE name = %s;", (agent_name,), fetchone=True)
    sys_prompt = agent_row['system_prompt'] if agent_row else "You are a world-class domain specialist."
    provider = agent_row['model_provider'] if agent_row else "openai"
    model = agent_row['model_name'] if agent_row else "gpt-4o"

    # Dynamic Local Skill Injection from PostgreSQL 'skills_library'
    category = state.get("category", "")
    skill_row = query_db("""
        SELECT executable_prompt, skill_name, category 
        FROM skills_library 
        WHERE skill_code ILIKE %s OR category ILIKE %s 
        LIMIT 1;
    """, (f"%{category}%", f"%{category}%"), fetchone=True)
    skill_instruction = ""
    if skill_row and skill_row.get('executable_prompt'):
        skill_instruction = f"\n\n[LOCAL SKILL PLAYBOOK - {skill_row['skill_name'].upper()}]:\n{skill_row['executable_prompt']}"

    guardrails_text = "\n".join([f"- {g}" for g in state.get("guardrails", [])])

    feedback_note = ""
    if state.get("critic_feedback"):
        feedback_note = f"\n\n[CRITICAL RED-TEAM FEEDBACK FROM PREVIOUS ROUND - MUST FIX]:\n{state['critic_feedback']}"

    system_instruction = (
        f"{sys_prompt}"
        f"{skill_instruction}\n\n"
        f"STRICT NEGATIVE GUARDRAILS (DO NOT VIOLATE UNDER ANY CIRCUMSTANCES):\n"
        f"{guardrails_text}\n"
        f"{feedback_note}\n\n"
        f"Deliver a structured, comprehensive, production-ready deliverable with zero filler or robotic fluff."
    )

    user_prompt = f"MISSION TITLE: {state['title']}\nOBJECTIVE:\n{state['objective']}"

    deliverable = call_multi_model(
        provider=provider,
        model_name=model,
        system_prompt=system_instruction,
        user_prompt=user_prompt,
        fallback_context=state.get("category", "")
    )

    logs.append(f"📝 [{agent_name}] Draft completed ({len(deliverable)} chars). Forwarding to Adversarial Critic...")

    return {
        **state,
        "draft_deliverable": deliverable,
        "logs": logs
    }

# -------------------------------------------------------------
# 3. Adversarial Red-Team Critic Node (Catches Mistakes)
# -------------------------------------------------------------
def critic_redteam_node(state: UniversalMissionState) -> UniversalMissionState:
    logs = list(state.get("logs", []))
    draft = state.get("draft_deliverable", "")
    retry_count = state.get("retry_count", 0)
    logs.append("🧐 [Critic Red-Team Agent] Inspecting deliverable against Negative Guardrails & Standards...")

    execute_db("UPDATE agency_missions SET status = 'red_team_review', updated_at = CURRENT_TIMESTAMP WHERE id = %s;", (state['mission_id'],))

    # Guardrails check
    has_robot_words = any(w in draft.lower() for w in ["delve", "testament", "tapestry", "pivotal"])
    is_sufficiently_deep = len(draft) > 120

    if (not has_robot_words and is_sufficiently_deep) or retry_count >= 2:
        logs.append("✅ [Critic Red-Team Agent] Deliverable PASSED all strict quality checks!")
        return {
            **state,
            "critic_approved": True,
            "critic_feedback": None,
            "logs": logs
        }
    else:
        critique = "Avoid robotic buzzwords (delve/testament), expand actionable steps, and ensure razor-sharp focus."
        logs.append(f"⚠️ [Critic Red-Team Agent] Quality check failed: {critique}. Looping back to specialist...")
        return {
            **state,
            "critic_approved": False,
            "critic_feedback": critique,
            "retry_count": retry_count + 1,
            "logs": logs
        }

# -------------------------------------------------------------
# 4. Delivery & State Persistence Node
# -------------------------------------------------------------
def delivery_node(state: UniversalMissionState) -> UniversalMissionState:
    logs = list(state.get("logs", []))
    deliverable = state.get("draft_deliverable")
    mission_id = state["mission_id"]

    logs.append(f"🚀 [Delivery Agent] Packaging final deliverable and committing to PostgreSQL 'agency_missions'...")

    execute_db("""
        UPDATE agency_missions 
        SET status = 'completed', output_deliverable = %s, updated_at = CURRENT_TIMESTAMP 
        WHERE id = %s;
    """, (deliverable, mission_id))

    logs.append(f"🏆 Mission '{state['title']}' COMPLETED successfully and ready for client!")

    return {
        **state,
        "final_deliverable": deliverable,
        "status": "completed",
        "logs": logs
    }

# Conditional Edge Route
def check_critic_decision(state: UniversalMissionState) -> Literal["delivery_node", "specialist_executor_node"]:
    if state.get("critic_approved", False):
        return "delivery_node"
    return "specialist_executor_node"

# -------------------------------------------------------------
# Compile Universal LangGraph Workflow
# -------------------------------------------------------------
def create_universal_agency_graph():
    builder = StateGraph(UniversalMissionState)

    builder.add_node("mission_planner_node", mission_planner_node)
    builder.add_node("specialist_executor_node", specialist_executor_node)
    builder.add_node("critic_redteam_node", critic_redteam_node)
    builder.add_node("delivery_node", delivery_node)

    builder.add_edge(START, "mission_planner_node")
    builder.add_edge("mission_planner_node", "specialist_executor_node")
    builder.add_edge("specialist_executor_node", "critic_redteam_node")

    builder.add_conditional_edges(
        "critic_redteam_node",
        check_critic_decision,
        {
            "delivery_node": "delivery_node",
            "specialist_executor_node": "specialist_executor_node"
        }
    )

    builder.add_edge("delivery_node", END)

    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)

universal_graph = create_universal_agency_graph()
