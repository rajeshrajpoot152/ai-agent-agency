import re
import json
from backend.app.core.database import query_db, execute_db
from backend.app.core.llm_gateway import call_multi_model
from backend.app.core.site_inspector import inspect_live_website
from backend.app.core.dynamic_agent_crafter import detect_and_auto_create_agent

def execute_auto_ingest(input_text: str):
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
        "Return ONLY a valid JSON object with these exact keys:\n"
        "{\n"
        '  "brand_name": "Clear, premium brand name",\n'
        '  "project_type": "tool_website | it_company | real_estate | jewelry | custom_crm | ecommerce | local_service | other",\n'
        '  "industry": "Specific industry niche",\n'
        '  "tagline": "Compelling 1-line hook",\n'
        '  "value_proposition": "Unique selling proposition & competitive edge",\n'
        '  "target_audience": "Ideal customer profile (B2B or B2C)",\n'
        '  "pricing_tier_summary": "Realistic pricing model e.g. Starter ₹X, Pro ₹Y or Custom",\n'
        '  "allowed_discount_max": 10 or 15,\n'
        '  "primary_color": "#6366F1",\n'
        '  "secondary_color": "#06B6D4",\n'
        '  "assigned_squad": [\n'
        '     {"name": "Arjun Sharma", "role": "Lead Tech Architect", "avatar": "/assets/avatars/head_charlie.jpg"},\n'
        '     {"name": "Neha Patel", "role": "Autonomous Lead Specialist", "avatar": "/assets/avatars/head_maya.jpg"},\n'
        '     {"name": "Priya Nair", "role": "Operations & Strategy Lead", "avatar": "/assets/avatars/head_morgan.jpg"},\n'
        '     {"name": "Pooja Verma", "role": "Visual Brand Designer", "avatar": "/assets/avatars/head_maya.jpg"}\n'
        '  ],\n'
        '  "social_posts": [\n'
        '     {"platform": "LinkedIn", "post_theme": "Problem & Innovation", "post_copy": "Copy...", "hashtags": "#Tech #Innovation", "canva_prompt": "Minimalist graphic..."},\n'
        '     {"platform": "Twitter / X", "post_theme": "Hot Take & Value", "post_copy": "Tweet...", "hashtags": "#Growth", "canva_prompt": "Clean infographic..."},\n'
        '     {"platform": "Instagram Carousel", "post_theme": "Visual Showcase", "post_copy": "Caption...", "hashtags": "#InstaDaily", "canva_prompt": "3D aesthetic banner..."},\n'
        '     {"platform": "Facebook", "post_theme": "Community & Case Study", "post_copy": "Post...", "hashtags": "#Solutions", "canva_prompt": "Customer result graphic..."}\n'
        '  ]\n'
        "}\n"
        "Do not include markdown fences ```json. Return pure JSON string only."
    )

    user_query = f"User Input: {clean_text}\n{inspection_context}"
    ai_raw = call_multi_model(
        provider="gemini",
        model_name="gemini-2.5-flash",
        system_prompt=sys_prompt,
        user_prompt=user_query,
        fallback_context="auto_ingest_project"
    )

    # Parse JSON
    clean_json_str = re.sub(r'```json\s*|\s*```', '', ai_raw).strip()
    try:
        data = json.loads(clean_json_str)
    except Exception as e:
        print("JSON parse fallback, trying regex search:", e)
        match_json = re.search(r'(\{[\s\S]*\})', clean_json_str)
        if match_json:
            data = json.loads(match_json.group(1))
        else:
            raise ValueError(f"Could not parse AI response into project JSON: {ai_raw}")

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

    # 3. Check and equip specialized agents/skills if needed
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

if __name__ == "__main__":
    res = execute_auto_ingest("Mera ek real estate client hai 'Shree Ram Luxury Villas', Pune me high-end villas sell karte hain ₹2.5 Cr starting.")
    print("Test auto-ingest result:")
    print("Project ID:", res['project']['id'])
    print("Brand Name:", res['project']['brand_name'])
    print("Industry:", res['project']['industry'])
    print("Tagline:", res['project']['tagline'])
    print("Value Prop:", res['project']['value_proposition'])
    print("Assigned Squad:", len(res['project']['assigned_squad']))
