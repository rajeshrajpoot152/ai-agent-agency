import re
import json
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.app.core.database import query_db, execute_db
from backend.app.core.llm_gateway import call_multi_model
from backend.app.core.site_inspector import inspect_live_website
from backend.app.core.dynamic_agent_crafter import detect_and_auto_create_agent

router = APIRouter(prefix="/api/projects-hub", tags=["Projects Hub & Virtual Team OS"])

# -------------------------------------------------------------
# Request Schemas
# -------------------------------------------------------------
class AutoIngestProjectRequest(BaseModel):
    input_text: str

class CreateProjectRequest(BaseModel):
    brand_name: str
    project_type: str = "tool_website"  # it_company, tool_website, real_estate, jewelry, custom_crm, other
    industry: str
    tagline: str
    value_proposition: Optional[str] = None
    target_audience: Optional[str] = None
    pricing_tier_summary: Optional[str] = None
    website_url: Optional[str] = None
    primary_color: Optional[str] = "#6366F1"
    secondary_color: Optional[str] = "#06B6D4"

class SmartReplyRequest(BaseModel):
    lead_id: Optional[str] = None
    client_name: Optional[str] = "Client"
    client_message: str
    sentiment_mode: str = "auto"  # positive, negative, auto
    channel: str = "whatsapp"     # whatsapp, email, telegram

class OutreachDispatchRequest(BaseModel):
    lead_id: str
    channel: str = "whatsapp"     # whatsapp, email, telegram
    message_content: str

class GenerateWeekSocialRequest(BaseModel):
    theme: Optional[str] = None

class CreateTeamMemberRequest(BaseModel):
    full_name: str
    email: str
    role: str = "Project Manager"
    assigned_projects: List[str] = []

# -------------------------------------------------------------
# 1. LIST ALL PROJECTS (MASTER PROJECT SWITCHER)
# -------------------------------------------------------------
@router.get("/list")
def list_projects(category: Optional[str] = None, search: Optional[str] = None):
    """
    Returns all projects/tools with isolated KPI metrics, assigned squads, and manager info.
    Supports instant search & category filtering for 200-500 client scale.
    """
    sql = """
        SELECT 
            b.id, b.brand_name, b.project_type, b.industry, 
            b.primary_color, b.secondary_color, b.tagline, b.value_proposition,
            b.target_audience, b.website_url, b.telegram_group_url, b.community_url,
            b.assigned_manager, b.social_autopilot_enabled, b.pricing_tier_summary,
            b.assigned_squad, b.created_at,
            (SELECT COUNT(*) FROM outreach_leads l WHERE l.brand_id = b.id) as leads_count,
            (SELECT COUNT(*) FROM outreach_leads l WHERE l.brand_id = b.id AND l.status = 'in_discussion') as active_deals_count,
            (SELECT COUNT(*) FROM content_schedules c WHERE c.brand_id = b.id) as posts_count
        FROM agency_brands b
    """
    params = []
    conditions = []

    if category and category.lower() != "all":
        conditions.append("b.project_type = %s")
        params.append(category.lower())

    if search and search.strip():
        conditions.append("(b.brand_name ILIKE %s OR b.industry ILIKE %s OR b.tagline ILIKE %s)")
        q = f"%{search.strip()}%"
        params.extend([q, q, q])

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += " ORDER BY (CASE WHEN b.project_type = 'it_company' THEN 1 WHEN b.project_type = 'tool_website' THEN 2 ELSE 3 END), b.created_at ASC;"

    projects = query_db(sql, tuple(params) if params else None)

    # Clean up squad json format if needed
    for p in projects:
        if isinstance(p.get("assigned_squad"), str):
            try:
                p["assigned_squad"] = json.loads(p["assigned_squad"])
            except:
                p["assigned_squad"] = []
        elif not p.get("assigned_squad"):
            p["assigned_squad"] = [
                {"name": "Arjun Sharma", "role": "Lead Architect", "avatar": "/assets/avatars/head_charlie.jpg"},
                {"name": "Neha Patel", "role": "Lead Closer", "avatar": "/assets/avatars/head_maya.jpg"}
            ]

    # Portfolio Stats
    total_projects = len(projects)
    total_leads = sum(p.get("leads_count", 0) for p in projects)
    total_active_deals = sum(p.get("active_deals_count", 0) for p in projects)

    return {
        "status": "success",
        "total_projects": total_projects,
        "metrics": {
            "total_projects": total_projects,
            "total_leads_across_portfolio": total_leads,
            "active_deals_across_portfolio": total_active_deals,
            "system_capacity": "500 Clients (High-Throughput Multi-Tenant Engine)",
            "super_admin": "Founder (You)"
        },
        "projects": projects
    }

# -------------------------------------------------------------
# 2. CREATE NEW PROJECT / TOOL / VERTICAL (1-CLICK SETUP)
# -------------------------------------------------------------

def execute_auto_ingest(input_text: str) -> Dict[str, Any]:
    clean_text = input_text.strip()
    if not clean_text:
        return {"status": "error", "message": "Input text cannot be empty."}

    # 1. Detect if a URL is provided
    url_pattern = r'(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.(?:com|org|io|in|net|co|app|ai|dev|store|agency|tech)(?:/[^\s]*)?)'
    match = re.search(url_pattern, clean_text)
    live_site_data = None
    detected_url = None

    if match:
        raw_url = match.group(0)
        detected_url = raw_url if raw_url.startswith("http") else f"https://{raw_url}"
        try:
            audit = inspect_live_website(detected_url)
            if audit.get("status") == "success":
                live_site_data = audit
        except Exception as e:
            print("Site inspection error (ignoring):", e)

    # 2. Call LLM to extract structured project intelligence
    inspection_context = ""
    if live_site_data:
        inspection_context = (
            f"\nLive Website Inspection Data for {detected_url}:\n"
            f"- Title: {live_site_data.get('title')}\n"
            f"- Meta Description: {live_site_data.get('meta_description')}\n"
            f"- H1 Headings: {live_site_data.get('headings', {}).get('h1', [])}\n"
            f"- Value Proposition Clues: {live_site_data.get('conversion', {}).get('call_to_actions', [])}\n"
        )

    sys_prompt = (
        "You are an Elite Enterprise AI Agency Orchestrator. "
        "A founder gave you an arbitrary business idea, company name, or website URL. "
        "Your mission is to autonomously analyze this venture and return a complete JSON configuration. "
        "Return ONLY a valid JSON object with keys: brand_name, project_type, industry, tagline, "
        "value_proposition, target_audience, pricing_tier_summary, allowed_discount_max, "
        "primary_color, secondary_color, assigned_squad, social_posts."
    )

    user_query = f"User Input: {clean_text}\n{inspection_context}"
    ai_raw = call_multi_model(
        provider="gemini",
        model_name="gemini-2.5-flash",
        system_prompt=sys_prompt,
        user_prompt=user_query,
        fallback_context="auto_ingest_project"
    )

    clean_json_str = re.sub(r'```json\s*|\s*```', '', ai_raw).strip()
    try:
        data = json.loads(clean_json_str)
    except Exception:
        match_json = re.search(r'(\{[\s\S]*\})', clean_json_str)
        if match_json:
            data = json.loads(match_json.group(1))
        else:
            raise HTTPException(status_code=500, detail="Could not parse AI response into project JSON")

    brand_name = data.get("brand_name", clean_text[:30])
    project_type = data.get("project_type", "other")
    industry = data.get("industry", "Business Services")
    tagline = data.get("tagline", "Autonomous Enterprise Solutions")
    value_proposition = data.get("value_proposition", "Scalable high-impact execution.")
    target_audience = data.get("target_audience", "Founders & Decision Makers")
    pricing_tier_summary = data.get("pricing_tier_summary", "Custom quote based on scope. Max discount: 10%.")
    allowed_discount_max = data.get("allowed_discount_max", 12)
    primary_color = data.get("primary_color", "#6366F1")
    secondary_color = data.get("secondary_color", "#06B6D4")
    assigned_squad = data.get("assigned_squad", [])
    website_url = detected_url or f"https://{re.sub(r'[^a-zA-Z0-9]', '', brand_name.lower())}.com"

    # 3. Equip specialized agents/skills if needed
    try:
        detect_and_auto_create_agent(f"{industry} {clean_text}")
    except Exception as e:
        print("Skill expansion error (ignoring):", e)

    # 4. Insert into database with UUID primary key
    execute_db("""
        INSERT INTO agency_brands (
            brand_name, project_type, industry, tagline, value_proposition,
            target_audience, pricing_tier_summary, allowed_discount_max,
            website_url, primary_color, secondary_color, assigned_squad
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """, (
        brand_name, project_type, industry, tagline, value_proposition,
        target_audience, pricing_tier_summary, allowed_discount_max,
        website_url, primary_color, secondary_color, json.dumps(assigned_squad)
    ))

    new_project = query_db("SELECT * FROM agency_brands WHERE brand_name = %s ORDER BY created_at DESC LIMIT 1;", (brand_name,), fetchone=True)
    project_id = new_project['id']

    # 5. Seed initial 4 social posts into content_schedules
    posts = data.get("social_posts", [])
    for idx, p in enumerate(posts, start=1):
        try:
            execute_db("""
                INSERT INTO content_schedules (
                    brand_id, platform, post_theme, post_copy, hashtags, canva_prompt, status, day_number
                ) VALUES (%s, %s, %s, %s, %s, %s, 'ready', %s);
            """, (
                project_id,
                p.get("platform", "LinkedIn"),
                p.get("post_theme", "Innovation"),
                p.get("post_copy", ""),
                p.get("hashtags", "#Growth"),
                p.get("canva_prompt", "Clean modern graphic"),
                idx
            ))
        except Exception as e:
            print("Post schedule error:", e)

    return {
        "status": "success",
        "message": f"Project '{brand_name}' autonomously researched, configured & activated!",
        "project": new_project
    }

@router.post("/auto-ingest")
def auto_ingest_project_endpoint(req: AutoIngestProjectRequest):
    """
    Autonomous Project Builder & Skill Auto-Equipper:
    Accepts any URL, company name, or plain brief.
    Crawls & audits live website, dynamically classifies industry,
    auto-assigns optimal 3D squad, equips skills, seeds social posts,
    and saves to PostgreSQL with 100% strict data isolation.
    """
    return execute_auto_ingest(req.input_text)

@router.post("/create")
def create_project(req: CreateProjectRequest):
    """
    1-Click creates an isolated project (Tool, Real Estate, Jewelry, CRM)
    with automatic 3D specialist squad assignment.
    """
    default_squad = [
        {"name": "Arjun Sharma", "role": "Lead Tech Architect", "avatar": "/assets/avatars/head_charlie.jpg"},
        {"name": "Neha Patel", "role": "Autonomous Lead Specialist", "avatar": "/assets/avatars/head_maya.jpg"},
        {"name": "Priya Nair", "role": "Operations & Strategy Lead", "avatar": "/assets/avatars/head_morgan.jpg"}
    ]

    execute_db("""
        INSERT INTO agency_brands (
            brand_name, project_type, industry, tagline, value_proposition,
            target_audience, pricing_tier_summary, website_url, primary_color,
            secondary_color, assigned_squad
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """, (
        req.brand_name, req.project_type, req.industry, req.tagline,
        req.value_proposition or f"Automated enterprise solution for {req.industry}.",
        req.target_audience or f"Businesses and decision-makers in {req.industry}.",
        req.pricing_tier_summary or "Standard Pricing: Custom quote based on scope. Max discount: 10%.",
        req.website_url or f"https://{re.sub(r'[^a-zA-Z0-9]', '', req.brand_name.lower())}.io",
        req.primary_color or "#6366F1",
        req.secondary_color or "#06B6D4",
        json.dumps(default_squad)
    ))

    new_project = query_db("SELECT * FROM agency_brands WHERE brand_name = %s ORDER BY created_at DESC LIMIT 1;", (req.brand_name,), fetchone=True)
    return {"status": "success", "message": f"Project '{req.brand_name}' created successfully with dedicated 3D squad!", "project": new_project}

# -------------------------------------------------------------
# 3. GET DEDICATED PROJECT COCKPIT (ZERO DATA LEAKAGE)
# -------------------------------------------------------------
@router.get("/{project_id}/dashboard")
def get_project_dashboard(project_id: str):
    """
    Returns complete isolated project data:
    1. Project Profile & Assigned 3D Squad
    2. Cause-and-Effect Impact Radar (Simulated Action Outcomes)
    3. Dedicated Social Media Marketing Calendar
    4. Isolated Leads & Outreach Database (WhatsApp/Email/Telegram)
    """
    brand = query_db("SELECT * FROM agency_brands WHERE id = %s;", (project_id,), fetchone=True)
    if not brand:
        raise HTTPException(status_code=404, detail="Project not found")

    # Parse squad
    squad = brand.get("assigned_squad") or []
    if isinstance(squad, str):
        try:
            squad = json.loads(squad)
        except:
            squad = []

    # 1. Strictly Isolated Leads (Never mix with other projects!)
    leads = query_db("""
        SELECT 
            id, full_name, business_name, mobile_number, whatsapp_number, 
            email_address, telegram_handle, status, deal_value, notes, 
            inquiry_source, last_reply_sentiment, created_at, follow_up_date
        FROM outreach_leads
        WHERE brand_id = %s
        ORDER BY created_at DESC LIMIT 100;
    """, (project_id,))

    # 2. Dedicated Social Posts for this project
    posts = query_db("""
        SELECT 
            id, platform, post_theme, post_copy, hashtags, 
            canva_prompt, status, day_number, scheduled_date
        FROM content_schedules
        WHERE brand_id = %s
        ORDER BY day_number ASC LIMIT 14;
    """, (project_id,))

    # If no posts yet, generate initial 4-platform pack
    if not posts:
        b_name = brand["brand_name"]
        ind = brand.get("industry") or "Technology"
        tag = brand.get("tagline") or "Scale on Autopilot"
        default_posts = [
            {
                "platform": "LinkedIn",
                "theme": "Industry Authority & Problem Teardown",
                "post_copy": f"🚀 In 2026, the biggest differentiator in {ind} is not working more hours—it is automating repetitive bottlenecks.\n\nAt {b_name}, we help teams replace manual effort with intelligent software architectures.\n\n👉 Let's connect for a 15-min discovery sprint.\n\n#{re.sub(r'[^a-zA-Z]', '', ind)} #Automation #Growth2026",
                "hashtags": f"#{re.sub(r'[^a-zA-Z]', '', ind)} #Technology #Scale",
                "canva_prompt": f"Minimalist dark-mode infographic banner showing manual vs automated workflow in {ind} with glowing cyan and indigo accents."
            },
            {
                "platform": "Twitter / X",
                "theme": "Direct Value & Insights",
                "post_copy": f"3 things killing growth in {ind} right now:\n\n1. Slow response times (>10 mins)\n2. Fragmented client communication\n3. Manual spreadsheets\n\nFix these, and your conversion doubles. We ship systems that solve all 3 in under 14 days at {b_name} ⚡",
                "hashtags": f"#{re.sub(r'[^a-zA-Z]', '', ind)} #Productivity",
                "canva_prompt": f"High-contrast stat card with '+210% Conversion' headline on dark slate background."
            },
            {
                "platform": "Instagram",
                "theme": "Behind The Scenes & Framework",
                "post_copy": f"✨ How we engineer high-converting solutions for {ind} clients.\n\nSwipe to explore our 4-stage delivery process 👉\n\nLink in bio to claim your discovery roadmap! 🚀",
                "hashtags": f"#{re.sub(r'[^a-zA-Z]', '', ind)} #Design #Innovation",
                "canva_prompt": f"Elegant multi-slide carousel cover in gold and dark slate displaying '{tag}' with floating 3D device mockups."
            },
            {
                "platform": "Facebook",
                "theme": "Direct Client Offer & Social Proof",
                "post_copy": f"Are manual processes slowing down your business?\n\n{b_name} builds tailored platforms, custom CRM automation, and mobile systems for {ind} leaders.\n\n🎯 100% Code Ownership\n🎯 Fast 14-Day Delivery SLA\n🎯 Dedicated Engineering Partners\n\nDM us or click Learn More to book a consultation!",
                "hashtags": f"#{re.sub(r'[^a-zA-Z]', '', ind)} #BusinessGrowth",
                "canva_prompt": f"Professional corporate social banner showcasing modern digital dashboard and mobile app mockups."
            }
        ]
        for idx, dp in enumerate(default_posts, 1):
            execute_db("""
                INSERT INTO content_schedules (brand_id, platform, post_theme, post_copy, hashtags, canva_prompt, status, day_number)
                VALUES (%s, %s, %s, %s, %s, %s, 'scheduled', %s);
            """, (project_id, dp["platform"], dp["theme"], dp["post_copy"], dp["hashtags"], dp["canva_prompt"], idx))

        posts = query_db("SELECT id, platform, post_theme, post_copy, hashtags, canva_prompt, status, day_number FROM content_schedules WHERE brand_id = %s ORDER BY day_number ASC;", (project_id,))

    # 3. Connected Cause-and-Effect Impact Radar (The User's "What If" Engine!)
    total_leads_count = len(leads)
    in_discussion_count = sum(1 for l in leads if l.get("status") == "in_discussion")
    won_count = sum(1 for l in leads if l.get("status") == "won")

    impact_radar = {
        "current_health_score": "98% Optimal",
        "action_predictions": [
            {
                "trigger_action": "Publish 4 Scheduled Social Posts this week",
                "predicted_reach": "~1,800 - 3,200 Targeted Impressions",
                "inbound_lead_impact": "+6 to +12 Inbound Inquiries",
                "pipeline_impact": "+₹1.5 Lakh potential deal volume"
            },
            {
                "trigger_action": "Send 1-Click WhatsApp Follow-ups to 'In Discussion' leads",
                "predicted_reach": f"{in_discussion_count} Priority Decision Makers",
                "inbound_lead_impact": "40% faster closing velocity",
                "pipeline_impact": "Prevents deal drop-off; secures immediate payment"
            },
            {
                "trigger_action": "Launch Telegram Community VIP Broadcast",
                "predicted_reach": "All connected project subscribers",
                "inbound_lead_impact": "+15% higher retention & repeat business",
                "pipeline_impact": "Continuous brand authority"
            }
        ],
        "kpi_meters": {
            "total_leads": total_leads_count,
            "active_discussions": in_discussion_count,
            "deals_won": won_count,
            "scheduled_social_posts": len(posts),
            "autopilot_status": "🟢 Active (Daily Autonomous Execution)"
        }
    }

    return {
        "status": "success",
        "project": brand,
        "assigned_squad": squad,
        "impact_radar": impact_radar,
        "leads": leads,
        "social_posts": posts
    }

# -------------------------------------------------------------
# 4. DEEP PROJECT-CONTEXT SMART REPLY (POSITIVE VS NEGATIVE)
# -------------------------------------------------------------
@router.post("/{project_id}/smart-reply")
def generate_project_aware_smart_reply(project_id: str, req: SmartReplyRequest):
    """
    Generates a reply having 100% DEEP UNDERSTANDING of this specific project:
    - Never leaks or confuses details with another tool
    - Supports Positive Agreement (milestone acceptance, welcome, next steps)
    - Supports Negative / Objection Boundary (firm, polite refusal of impossible terms with smart alternative)
    """
    brand = query_db("SELECT * FROM agency_brands WHERE id = %s;", (project_id,), fetchone=True)
    if not brand:
        raise HTTPException(status_code=404, detail="Project not found")

    lead = None
    if req.lead_id:
        lead = query_db("SELECT * FROM outreach_leads WHERE id = %s AND brand_id = %s;", (req.lead_id, project_id), fetchone=True)

    c_name = req.client_name or (lead.get("full_name") if lead else "Client")
    b_name = brand["brand_name"]
    ind = brand.get("industry") or "Technology"
    pricing = brand.get("pricing_tier_summary") or "Standard scope pricing."
    val_prop = brand.get("value_proposition") or brand.get("tagline") or ""
    allowed_disc = brand.get("allowed_discount_max") or 10

    # System instruction tailored with deep project understanding
    system_prompt = f"""
You are the senior executive partner and lead closer for '{b_name}'.
You have 100% deep understanding of this specific project:
- Industry: {ind}
- Value Proposition: {val_prop}
- Pricing Structure: {pricing}
- Maximum Allowed Discount: {allowed_disc}%
- Strict Rule: You NEVER talk about any other company or service outside of '{b_name}'.

The client sent this message:
"{req.client_message}"

Your Goal:
You must craft an intelligent, natural, high-converting professional Hinglish reply (mix of polite Hindi & English).

MODE: {req.sentiment_mode.upper()}
1. If POSITIVE:
   - Accept the agreement warmly.
   - Outline the clear next steps (milestone, timeline, kickoff call).
   - Reiterate how {b_name} delivers maximum ROI.
2. If NEGATIVE / BOUNDARY:
   - If client demanded an impossible price cut (> {allowed_disc}%), unrealistic 2-day delivery, or out-of-scope demands:
   - Politely and firmly explain WHY that compromises quality/standards.
   - Propose an intelligent win-win counter-offer (e.g. milestone split, Phase 1 MVP rollout, or maximum {allowed_disc}% discount on immediate upfront agreement).
   - Protect company margins while keeping the relationship warm.
3. If AUTO:
   - Detect whether the client is ready to buy (positive) or raising an objection (negative/counter-offer) and answer accordingly.

Keep the response concise, punchy, and ready to send over {req.channel.upper()}.
"""

    reply_text = call_multi_model(
        provider="gemini",
        model_name="gemini-2.5-flash",
        system_prompt=system_prompt,
        user_prompt=f"Client: {c_name}\nClient Message: {req.client_message}\nRequested Mode: {req.sentiment_mode}",
        fallback_context="conversation"
    )

    # Save sentiment tag in lead record if available
    if lead:
        sentiment_tag = "positive" if req.sentiment_mode == "positive" else ("boundary_counter" if req.sentiment_mode == "negative" else "handled")
        execute_db("UPDATE outreach_leads SET last_reply_sentiment = %s WHERE id = %s;", (sentiment_tag, lead["id"]))

    return {
        "status": "success",
        "project_name": b_name,
        "client_name": c_name,
        "sentiment_mode": req.sentiment_mode,
        "channel": req.channel,
        "smart_reply": reply_text
    }

# -------------------------------------------------------------
# 5. DISPATCH OUTREACH (WHATSAPP / EMAIL / TELEGRAM)
# -------------------------------------------------------------
@router.post("/{project_id}/outreach/dispatch")
def dispatch_project_outreach(project_id: str, req: OutreachDispatchRequest):
    """
    Dispatches or formats an outreach message for WhatsApp, Email, or Telegram
    strictly isolated to this project.
    """
    lead = query_db("SELECT * FROM outreach_leads WHERE id = %s AND brand_id = %s;", (req.lead_id, project_id), fetchone=True)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found in this project")

    brand = query_db("SELECT brand_name FROM agency_brands WHERE id = %s;", (project_id,), fetchone=True)

    # Record message log
    execute_db("""
        INSERT INTO outreach_message_logs (lead_id, channel, message_content, message_body, status)
        VALUES (%s, %s, %s, %s, 'sent');
    """, (req.lead_id, req.channel, req.message_content, req.message_content))

    # Update lead status
    execute_db("""
        UPDATE outreach_leads 
        SET status = 'in_discussion', last_contacted_at = NOW()
        WHERE id = %s;
    """, (req.lead_id,))

    # Format quick action URL
    whatsapp_url = None
    phone = lead.get("whatsapp_number") or lead.get("mobile_number") or ""
    clean_phone = re.sub(r'[^0-9]', '', phone)
    if clean_phone:
        import urllib.parse
        encoded_msg = urllib.parse.quote(req.message_content)
        whatsapp_url = f"https://wa.me/{clean_phone}?text={encoded_msg}"

    return {
        "status": "success",
        "message": f"Outreach recorded for {lead.get('full_name')} via {req.channel.upper()}",
        "whatsapp_direct_url": whatsapp_url,
        "lead_status": "in_discussion"
    }

# -------------------------------------------------------------
# 6. HUMAN TEAM DELEGATION (MULTI-MANAGER ACCESS)
# -------------------------------------------------------------
@router.get("/team-members")
def list_team_members():
    """
    Lists human team members/managers who can be assigned specific projects.
    """
    members = query_db("SELECT * FROM agency_team_members ORDER BY created_at DESC;")
    return {"status": "success", "team_members": members}

@router.post("/team-members")
def add_team_member(req: CreateTeamMemberRequest):
    """
    Adds a human employee/manager and assigns them to specific projects.
    """
    execute_db("""
        INSERT INTO agency_team_members (full_name, email, role, assigned_projects)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (email) DO UPDATE 
        SET full_name = EXCLUDED.full_name,
            role = EXCLUDED.role,
            assigned_projects = EXCLUDED.assigned_projects;
    """, (req.full_name, req.email, req.role, json.dumps(req.assigned_projects)))

    return {"status": "success", "message": f"Team member {req.full_name} added and delegated successfully!"}


# -------------------------------------------------------------
# 7. AUTOMATION 1: AUTO-LEAD PROSPECTING ENGINE
# -------------------------------------------------------------
class AutoHuntLeadsRequest(BaseModel):
    count: int = 5
    location: Optional[str] = "India / Global"

@router.post("/{project_id}/leads/auto-hunt")
def auto_hunt_leads_endpoint(project_id: str, req: AutoHuntLeadsRequest):
    """
    Autonomously hunts, qualifies & inserts verified B2B/B2C leads
    strictly into the active project database container (Zero Leakage).
    """
    from backend.app.core.automations_engine import auto_hunt_leads_for_project
    return auto_hunt_leads_for_project(project_id, count=req.count, location=req.location or "")

# -------------------------------------------------------------
# 8. AUTOMATION 2: 3-STEP SMART DRIP SEQUENCES
# -------------------------------------------------------------
@router.get("/{project_id}/outreach/drip-sequence")
def get_drip_sequence_endpoint(project_id: str, client_name: str = "Client"):
    """
    Generates tailored 3-step high-converting follow-up sequence
    (Day 1 Intro, Day 3 Proof, Day 7 Breakup) for the active project.
    """
    from backend.app.core.automations_engine import generate_drip_sequence
    return generate_drip_sequence(project_id, client_name=client_name)

# -------------------------------------------------------------
# 9. AUTOMATION 3: 1-CLICK GST INVOICE & UPI QR CODE GENERATOR
# -------------------------------------------------------------
class GenerateInvoiceRequest(BaseModel):
    amount: float = 45000.0

@router.post("/{project_id}/leads/{lead_id}/generate-invoice")
def generate_invoice_endpoint(project_id: str, lead_id: str, req: GenerateInvoiceRequest):
    """
    Generates official GST invoice, dynamic UPI QR code,
    and ready-to-send WhatsApp payment link for the client.
    """
    from backend.app.core.automations_engine import generate_invoice_for_lead
    return generate_invoice_for_lead(project_id, lead_id, amount=req.amount)

# -------------------------------------------------------------
# 10. AUTOMATION 4: WEEKLY MARKET & COMPETITOR SPY
# -------------------------------------------------------------
@router.get("/{project_id}/market-spy")
def get_market_spy_endpoint(project_id: str):
    """
    Returns weekly market intelligence, competitor pricing shifts,
    and ranking signals for the active project.
    """
    from backend.app.core.automations_engine import get_market_spy_intelligence
    return get_market_spy_intelligence(project_id)
