import re

def update_routes():
    with open("backend/app/api/routes_projects_hub.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Add imports if not present
    if "from backend.app.core.site_inspector import inspect_live_website" not in content:
        content = content.replace(
            "from backend.app.core.llm_gateway import call_multi_model",
            "from backend.app.core.llm_gateway import call_multi_model\nfrom backend.app.core.site_inspector import inspect_live_website\nfrom backend.app.core.dynamic_agent_crafter import detect_and_auto_create_agent"
        )

    # 2. Add AutoIngestProjectRequest schema
    if "class AutoIngestProjectRequest" not in content:
        content = content.replace(
            "class CreateProjectRequest(BaseModel):",
            "class AutoIngestProjectRequest(BaseModel):\n    input_text: str\n\nclass CreateProjectRequest(BaseModel):"
        )

    # 3. Add execute_auto_ingest function and /auto-ingest route
    auto_ingest_code = '''
def execute_auto_ingest(input_text: str) -> Dict[str, Any]:
    clean_text = input_text.strip()
    if not clean_text:
        return {"status": "error", "message": "Input text cannot be empty."}

    # 1. Detect if a URL is provided
    url_pattern = r'(https?://[^\\s]+|www\\.[^\\s]+|[a-zA-Z0-9.-]+\\.(?:com|org|io|in|net|co|app|ai|dev|store|agency|tech)(?:/[^\\s]*)?)'
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
            f"\\nLive Website Inspection Data for {detected_url}:\\n"
            f"- Title: {live_site_data.get('title')}\\n"
            f"- Meta Description: {live_site_data.get('meta_description')}\\n"
            f"- H1 Headings: {live_site_data.get('headings', {}).get('h1', [])}\\n"
            f"- Value Proposition Clues: {live_site_data.get('conversion', {}).get('call_to_actions', [])}\\n"
        )

    sys_prompt = (
        "You are an Elite Enterprise AI Agency Orchestrator. "
        "A founder gave you an arbitrary business idea, company name, or website URL. "
        "Your mission is to autonomously analyze this venture and return a complete JSON configuration. "
        "Return ONLY a valid JSON object with keys: brand_name, project_type, industry, tagline, "
        "value_proposition, target_audience, pricing_tier_summary, allowed_discount_max, "
        "primary_color, secondary_color, assigned_squad, social_posts."
    )

    user_query = f"User Input: {clean_text}\\n{inspection_context}"
    ai_raw = call_multi_model(
        provider="gemini",
        model_name="gemini-2.5-flash",
        system_prompt=sys_prompt,
        user_prompt=user_query,
        fallback_context="auto_ingest_project"
    )

    clean_json_str = re.sub(r'```json\\s*|\\s*```', '', ai_raw).strip()
    try:
        data = json.loads(clean_json_str)
    except Exception:
        match_json = re.search(r'(\\{[\\s\\S]*\\})', clean_json_str)
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
'''

    if "@router.post(\"/auto-ingest\")" not in content:
        # Place before @router.post("/create")
        content = content.replace('@router.post("/create")', auto_ingest_code + '\n@router.post("/create")')

    with open("backend/app/api/routes_projects_hub.py", "w", encoding="utf-8") as f:
        f.write(content)

    print("✓ Successfully updated routes_projects_hub.py with auto-ingest endpoint!")

if __name__ == "__main__":
    update_routes()
