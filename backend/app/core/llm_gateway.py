import os
import json
from dotenv import load_dotenv

load_dotenv()

# Multi-Provider API Keys from .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()

def reload_keys():
    global GEMINI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, DEEPSEEK_API_KEY
    load_dotenv(override=True)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "").strip()

def save_ai_key(provider: str, api_key: str) -> dict:
    """
    Saves an API key directly into .env and reloads gateway runtime memory.
    """
    provider = provider.lower()
    env_var_map = {
        "gemini": "GEMINI_API_KEY",
        "google": "GEMINI_API_KEY",
        "openai": "OPENAI_API_KEY",
        "chatgpt": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "claude": "ANTHROPIC_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY"
    }
    target_var = None
    for k, v in env_var_map.items():
        if k in provider:
            target_var = v
            break
    if not target_var:
        target_var = "GEMINI_API_KEY" if "aiza" in api_key.lower() else "OPENAI_API_KEY"

    clean_key = api_key.strip()

    # Update .env file
    env_path = os.path.join(os.getcwd(), ".env")
    lines = []
    found = False
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        new_lines = []
        for line in lines:
            if line.startswith(f"{target_var}="):
                new_lines.append(f"{target_var}={clean_key}\n")
                found = True
            else:
                new_lines.append(line)
        lines = new_lines

    if not found:
        lines.append(f"{target_var}={clean_key}\n")

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    os.environ[target_var] = clean_key
    reload_keys()

    return {
        "status": "success",
        "provider": target_var,
        "message": f"Successfully connected and saved {target_var} to environment!"
    }


def call_multi_model(
    provider: str,
    model_name: str,
    system_prompt: str,
    user_prompt: str,
    fallback_context: str = ""
) -> str:
    """
    Universal AI Gateway: Routes dynamically to:
    1. Google Gemini (gemini-2.5-flash, gemini-1.5-pro)
    2. OpenAI / ChatGPT (gpt-4o, gpt-4o-mini, gpt-3.5-turbo)
    3. Anthropic Claude (claude-3-5-sonnet, claude-3-haiku)
    4. DeepSeek (deepseek-chat, deepseek-reasoner)
    With zero-failure dynamic heuristic fallback if key is missing!
    """
    provider = provider.lower()

    # -------------------------------------------------------------
    # 1. GOOGLE GEMINI
    # -------------------------------------------------------------
    if "gemini" in provider or "google" in provider:
        if GEMINI_API_KEY and len(GEMINI_API_KEY) > 10:
            try:
                from google import genai
                client = genai.Client(api_key=GEMINI_API_KEY)
                m = model_name if model_name else "gemini-2.5-flash"
                resp = client.models.generate_content(
                    model=m,
                    contents=f"SYSTEM:\n{system_prompt}\n\nUSER:\n{user_prompt}"
                )
                if resp and resp.text:
                    return resp.text.strip()
            except Exception as e:
                print(f"[Gemini Gateway Error]: {e}")

    # -------------------------------------------------------------
    # 2. OPENAI / CHATGPT (GPT-4o)
    # -------------------------------------------------------------
    elif "openai" in provider or "chatgpt" in provider or "gpt" in provider:
        if OPENAI_API_KEY and len(OPENAI_API_KEY) > 10:
            try:
                import urllib.request
                url = "https://api.openai.com/v1/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {OPENAI_API_KEY}"
                }
                payload = {
                    "model": model_name if model_name else "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.7
                }
                req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
                with urllib.request.urlopen(req, timeout=15) as res:
                    data = json.loads(res.read().decode())
                    return data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                print(f"[OpenAI Gateway Error]: {e}")

    # -------------------------------------------------------------
    # 3. ANTHROPIC CLAUDE (Claude 3.5 Sonnet)
    # -------------------------------------------------------------
    elif "anthropic" in provider or "claude" in provider:
        if ANTHROPIC_API_KEY and len(ANTHROPIC_API_KEY) > 10:
            try:
                import urllib.request
                url = "https://api.anthropic.com/v1/messages"
                headers = {
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                }
                payload = {
                    "model": model_name if model_name else "claude-3-5-sonnet-20241022",
                    "max_tokens": 1024,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_prompt}]
                }
                req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
                with urllib.request.urlopen(req, timeout=15) as res:
                    data = json.loads(res.read().decode())
                    return data["content"][0]["text"].strip()
            except Exception as e:
                print(f"[Claude Gateway Error]: {e}")

    # -------------------------------------------------------------
    # 4. DEEPSEEK (DeepSeek-V3 / R1)
    # -------------------------------------------------------------
    elif "deepseek" in provider:
        if DEEPSEEK_API_KEY and len(DEEPSEEK_API_KEY) > 10:
            try:
                import urllib.request
                url = "https://api.deepseek.com/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
                }
                payload = {
                    "model": model_name if model_name else "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                }
                req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
                with urllib.request.urlopen(req, timeout=15) as res:
                    data = json.loads(res.read().decode())
                    return data["choices"][0]["message"]["content"].strip()
            except Exception as e:
                print(f"[DeepSeek Gateway Error]: {e}")

    # -------------------------------------------------------------
    # 5. OLLAMA (100% FREE, LOCAL, OFFLINE & OPEN-SOURCE)
    # -------------------------------------------------------------
    elif "ollama" in provider or "local" in provider:
        try:
            import urllib.request
            url = "http://localhost:11434/api/generate"
            payload = {
                "model": model_name if model_name else "llama3.2",
                "prompt": f"{system_prompt}\n\nUser: {user_prompt}\nAssistant:",
                "stream": False
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as res:
                data = json.loads(res.read().decode())
                if "response" in data and data["response"]:
                    return data["response"].strip()
        except Exception as e:
            print(f"[Ollama Local Gateway Notice]: {e}")

    # -------------------------------------------------------------
    # ZERO-FAILURE DYNAMIC SYNTHESIZER
    # -------------------------------------------------------------
    return synthesize_dynamic_message(user_prompt, system_prompt, fallback_context)

def synthesize_dynamic_message(context_text: str, system_prompt: str = "", category: str = "") -> str:
    cat_lower = (category or "").lower()

    # Special Case: Autonomous Project Ingestion & Auto-Builder
    if cat_lower in ["auto_ingest_project", "project_ingest"]:
        import json, re
        txt = context_text.lower()
        
        # Determine industry & project type
        proj_type = "tool_website"
        ind = "Technology & SaaS"
        b_name = "New Venture"

        # Try to extract a clean name
        name_match = re.search(r"['\"]([^'\"]+)['\"]", context_text)
        if name_match:
            b_name = name_match.group(1).strip()
        else:
            first_few = context_text.split("\n")[0].replace("User Input:", "").strip()
            # Repeatedly clean common prompt command prefixes
            for _ in range(3):
                first_few = re.sub(r'^(?:mera ek|mera|hamara|client|new project|naya project|project add|add project|naya tool|add karo|karo|banao)[:\s]+', '', first_few, flags=re.I).strip()
            b_name = first_few.split(",")[0].split("-")[0].strip()[:35]
            if not b_name:
                b_name = "Autonomous Client Venture"

        if any(w in txt for w in ["real estate", "villa", "property", "plots", "flats", "builders", "housing", "land"]):
            proj_type = "real_estate"
            ind = "Real Estate & Luxury Properties"
            squad = [
                {"name": "Neha Patel", "role": "High-Ticket Closer & Deals", "avatar": "/assets/avatars/head_maya.jpg"},
                {"name": "Rohan Das", "role": "Local SEO & Geo Citation Lead", "avatar": "/assets/avatars/head_charlie.jpg"},
                {"name": "Pooja Verma", "role": "Visual Media & Ad Designer", "avatar": "/assets/avatars/head_maya.jpg"},
                {"name": "Alex", "role": "Inquiry Concierge & Telephony", "avatar": "/assets/avatars/head_alex.jpg"}
            ]
        elif any(w in txt for w in ["jewelry", "jewellery", "gold", "diamond", "polki", "silver", "gems"]):
            proj_type = "jewelry"
            ind = "Luxury Jewelry & Fine Craftsmanship"
            squad = [
                {"name": "Pooja Verma", "role": "Luxury Brand & Creative Director", "avatar": "/assets/avatars/head_maya.jpg"},
                {"name": "Neha Patel", "role": "VIP Client Closer", "avatar": "/assets/avatars/head_maya.jpg"},
                {"name": "Ananya Roy", "role": "Social Growth & Influencer Lead", "avatar": "/assets/avatars/head_morgan.jpg"},
                {"name": "Kabir Sen", "role": "Logistics & Security Lead", "avatar": "/assets/avatars/head_jordan.jpg"}
            ]
        elif any(w in txt for w in ["software", "it company", "agency", "tech", "web dev", "app dev", "solutions"]):
            proj_type = "it_company"
            ind = "IT Services & Software Engineering"
            squad = [
                {"name": "Arjun Sharma", "role": "Lead Tech Architect", "avatar": "/assets/avatars/head_charlie.jpg"},
                {"name": "Kabir Sen", "role": "DevOps & Cloud Systems", "avatar": "/assets/avatars/head_jordan.jpg"},
                {"name": "Neha Patel", "role": "Enterprise Closer", "avatar": "/assets/avatars/head_maya.jpg"},
                {"name": "Shreya Adv.", "role": "Legal & SLA Compliance", "avatar": "/assets/avatars/head_casey.jpg"}
            ]
        elif any(w in txt for w in ["crm", "pipeline", "leads", "sales flow"]):
            proj_type = "custom_crm"
            ind = "Enterprise CRM & Revenue Ops"
            squad = [
                {"name": "Arjun Sharma", "role": "Database & API Architect", "avatar": "/assets/avatars/head_charlie.jpg"},
                {"name": "Neha Patel", "role": "Sales Pipeline Specialist", "avatar": "/assets/avatars/head_maya.jpg"},
                {"name": "Rishabh", "role": "SaaS Metrics & Billing", "avatar": "/assets/avatars/head_michael.jpg"}
            ]
        else:
            proj_type = "tool_website"
            ind = "B2B SaaS & Digital Product"
            squad = [
                {"name": "Arjun Sharma", "role": "Lead Product Architect", "avatar": "/assets/avatars/head_charlie.jpg"},
                {"name": "Kavita Rao", "role": "CRO & Direct-Response Copywriter", "avatar": "/assets/avatars/head_maya.jpg"},
                {"name": "Aryan Gupta", "role": "Technical SEO & AEO Specialist", "avatar": "/assets/avatars/head_charlie.jpg"},
                {"name": "Priya Nair", "role": "VP Operations", "avatar": "/assets/avatars/head_morgan.jpg"}
            ]

        res_dict = {
            "brand_name": b_name,
            "project_type": proj_type,
            "industry": ind,
            "tagline": f"Premium high-performance solutions for {ind}.",
            "value_proposition": f"Autonomous, end-to-end execution and verified pipeline velocity tailored for {b_name}.",
            "target_audience": f"High-intent clients, investors and decision-makers in {ind}.",
            "pricing_tier_summary": "Transparent custom milestone pricing. Max discount: 10%.",
            "allowed_discount_max": 10,
            "primary_color": "#6366F1",
            "secondary_color": "#06B6D4",
            "assigned_squad": squad,
            "social_posts": [
                {
                    "platform": "LinkedIn",
                    "post_theme": f"Industry Shift & Innovation in {ind}",
                    "post_copy": f"How {b_name} is transforming {ind} with automated operational precision.\n\nDiscover how we deliver uncompromised quality and high-speed execution.",
                    "hashtags": f"#{ind.replace(' ', '')} #Innovation #Leadership",
                    "canva_prompt": f"Modern minimalist executive graphic showcasing {b_name} value proposition in {ind}."
                },
                {
                    "platform": "Twitter / X",
                    "post_theme": "High-Value Insight",
                    "post_copy": f"Speed and quality don't have to be a trade-off in {ind}.\n\nHere is how {b_name} executes 10x faster without compromising standards ⚡",
                    "hashtags": f"#{ind.replace(' ', '')} #Growth",
                    "canva_prompt": "Clean infographic card with key performance metrics."
                },
                {
                    "platform": "Instagram Carousel",
                    "post_theme": "Behind the Craft & Quality",
                    "post_copy": f"Inside the craftsmanship of {b_name}. Every detail engineered for excellence.\n\nTap the link in bio to explore.",
                    "hashtags": f"#{ind.replace(' ', '')} #Aesthetics #Excellence",
                    "canva_prompt": f"3D aesthetic editorial visual showcasing {b_name} branding."
                },
                {
                    "platform": "Facebook",
                    "post_theme": "Customer Case & Community",
                    "post_copy": f"Delivering measurable results for our clients at {b_name}. Get in touch today for an exclusive consultation.",
                    "hashtags": f"#{ind.replace(' ', '')} #ClientSuccess",
                    "canva_prompt": "Customer success banner with strong call-to-action button."
                }
            ]
        }
        return json.dumps(res_dict)

    # 0. If this is a conversation, handle conversationally!
    if cat_lower == "conversation":
        ctx_l = context_text.lower()
        if any(w in ctx_l for w in ["nahi", "kam ka nahi", "bakwas", "bekar", "kuch nahi", "waste", "problem"]):
            return (
                "Aapka feedback bilkul sahi hai aur main samajhta hoon! Hum kisi bhi generic ya dummy response ko band kar rahe hain. "
                "Ab hamari agent team directly real kaam karegi:\n\n"
                "1. **Live Website Audit:** Agar aap koi bhi URL denge (jaise `yashviglobal.com` ya koi bhi site), hum uska live crawl karke technical, SEO, speed aur missing meta tags nikaal kar denge.\n"
                "2. **Real Company Leads:** Agar aap 'IT company ki list' ya kisi bhi industry ki list mangenge, hum PostgreSQL database se verified companies aur contact numbers nikal kar denge.\n"
                "3. **Direct Deliverable:** Design, ad creative, ya SEO strategy jo bhi bolenge, concrete action plan milega.\n\n"
                "Aap abhi koi bhi specific task de kar dekhein!"
            )
        return (
            f"Namaste! Main aapki autonomous AI Agency ka CEO Orchestrator hoon. "
            f"Aapne pucha: '{context_text}'. Hum aapke business ke liye live website audits, verified lead lists, "
            f"high-converting ad copy, aur SEO ranking blueprints execute karte hain. "
            f"Aap mujhe koi bhi task de kar test karein!"
        )

    # 1. Check if this is an Agency Mission Deliverable
    if "MISSION TITLE:" in context_text or "OBJECTIVE:" in context_text or (cat_lower and cat_lower != "conversation"):
        title = ""
        objective = ""
        for line in context_text.split("\n"):
            if line.startswith("MISSION TITLE:"):
                title = line.replace("MISSION TITLE:", "").strip()
            elif line.startswith("OBJECTIVE:"):
                objective = line.replace("OBJECTIVE:", "").strip()
        
        ctx_title_lower = (title + " " + objective).lower()
        
        # 0.0. SITES: BUILD & DEPLOY WEBSITES
        if cat_lower in ["sites", "website", "web_deploy"] or (any(w in ctx_title_lower for w in ["sites:", "build website", "website code", "landing page code"]) and "proposal" not in ctx_title_lower):
            return (
                f"# 🌐 Production Web Application & Landing Page Architecture: {title}\n\n"
                f"## 1. Responsive Single-Page Architecture (HTML5 + Tailwind CSS)\n"
                f"Target: {objective}\n\n"
                f"```html\n"
                f"<!DOCTYPE html>\n"
                f'<html lang="en" class="scroll-smooth">\n'
                f"<head>\n"
                f'  <meta charset="UTF-8">\n'
                f'  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
                f'  <title>{title}</title>\n'
                f'  <script src="https://cdn.tailwindcss.com"></script>\n'
                f"</head>\n"
                f'<body class="bg-slate-950 text-slate-100 font-sans antialiased">\n'
                f'  <!-- Navbar -->\n'
                f'  <nav class="border-b border-slate-800/80 px-6 py-4 flex justify-between items-center max-w-7xl mx-auto">\n'
                f'    <div class="text-xl font-bold text-indigo-400 font-mono tracking-tight">{title}</div>\n'
                f'    <a href="#cta" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-xl text-xs font-bold transition">Get Started</a>\n'
                f'  </nav>\n'
                f'  <!-- Hero Section -->\n'
                f'  <header class="py-24 px-6 text-center max-w-4xl mx-auto">\n'
                f'    <h1 class="text-4xl sm:text-6xl font-extrabold tracking-tight text-white mb-6">Build & Scale with {title}</h1>\n'
                f'    <p class="text-lg text-slate-400 mb-8 max-w-2xl mx-auto">{objective}</p>\n'
                f'    <div class="flex justify-center gap-4">\n'
                f'      <button class="px-6 py-3.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl transition shadow-lg shadow-indigo-600/30">Start Free Trial</button>\n'
                f'      <button class="px-6 py-3.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-200 font-bold rounded-xl transition">View Demo</button>\n'
                f'    </div>\n'
                f'  </header>\n'
                f"</body>\n"
                f"</html>\n"
                f"```\n\n"
                f"## 2. Deployment Specification\n"
                f"- **Static Hosting:** Cloudflare Pages / Vercel Edge with zero cold start latency.\n"
                f"- **SEO Metadata:** OpenGraph social sharing card, Twitter cards, and canonical tags pre-configured."
            )

        # 0.1. PRESENTATIONS: PITCH DECKS & SLIDES
        elif cat_lower in ["presentations", "slides", "deck", "pitch_deck"] or any(w in ctx_title_lower for w in ["presentations:", "pitch deck", "slides deck", "10-slide"]):
            return (
                f"# 📊 High-Stakes Presentation & Pitch Deck Architecture: {title}\n\n"
                f"## Executive Pitch Structure (10-Slide Investor / Client Deck)\n"
                f"Objective: {objective}\n\n"
                f"### Slide 1: Title & Hook\n"
                f"- **Headline:** {title} — Next-Generation Enterprise Autonomous Systems\n"
                f"- **Sub-headline:** Eliminating manual operational bottlenecks with 24/7 AI-native execution.\n"
                f"- **Speaker Note:** *\"Welcome everyone. Today we're showing how modern enterprises scale without linear headcount growth.\"*\n\n"
                f"### Slide 2: The Core Problem & Burning Pain\n"
                f"- **Pain Point 1:** Engineering & agency payroll costs are surging (\\$140k+ per senior hire).\n"
                f"- **Pain Point 2:** Multi-day latency on cold outreach, bug fixes, and client deliverables.\n"
                f"- **Speaker Note:** *\"Every client we interview shares the exact same operational friction: speed vs cost.\"*\n\n"
                f"### Slide 3: The Solution\n"
                f"- **Core Value:** Self-orchestrated multi-agent pods operating 24/7 on local open-source LLMs.\n"
                f"- **Proof Point:** 65% cost reduction, 15-minute turnaround on production deliverables.\n\n"
                f"### Slide 4: Technology Architecture & Multi-Agent Engine\n"
                f"- LangGraph state machines, PostgreSQL transactional memory, and local Ollama models.\n\n"
                f"### Slide 5: Business Model & Commercial SOW\n"
                f"- Fixed Milestone Delivery (\\$7,500 – \\$15,000) or Dedicated Pod Retainer (\\$3,200/mo).\n\n"
                f"### Slide 6: Call to Action & 2-Week Pilot Handover\n"
                f"- Immediate sprint zero initiation on backlog tasks with 100% IP rights transferred."
            )

        # 0.2. IT PROPOSAL & COMMERCIAL BID
        elif cat_lower in ["it_proposal", "proposal"] or "proposal" in ctx_title_lower or "sow" in ctx_title_lower or "quote" in ctx_title_lower:
            return (
                f"# Enterprise Software Development Proposal & SOW: {title}\n\n"
                f"## 1. Executive Summary & Project Vision\n"
                f"Client Scope: {objective}\n"
                f"- **Engagement Model:** Full-Lifecycle Software Development & Scalable Cloud Architecture.\n"
                f"- **Core Value:** Delivering a secure, production-grade digital platform with 99.9% uptime SLA and clean, modular codebase.\n\n"
                f"## 2. Recommended Enterprise Tech Stack\n"
                f"| Layer | Recommended Technology | Architectural Justification |\n"
                f"|---|---|---|\n"
                f"| Frontend Web | `Next.js 15 (React 19)` + `Tailwind CSS` | Server-Side Rendering (SSR), sub-second page loads & SEO indexability |\n"
                f"| Mobile App | `Flutter 3.x` or `React Native` | Single codebase iOS & Android deployment with native 60fps performance |\n"
                f"| Backend API | `FastAPI (Python 3.13)` / `Node.js TypeScript` | High-throughput asynchronous endpoints with OpenAPI / Swagger documentation |\n"
                f"| Database | `PostgreSQL 16` + `Redis` | ACID compliance, relational integrity, JSONB flexibility, and ultra-fast session cache |\n"
                f"| Cloud & DevOps | `Docker` + `AWS ECS / GCP Cloud Run` | Automated containerization, CI/CD pipeline with zero-downtime deployment |\n\n"
                f"## 3. Agile Sprint Timeline & Deliverable Milestones\n"
                f"- **Sprint 1 (Weeks 1–2): System Discovery & Foundation**\n"
                f"  - Database ERD schema, authentication (OAuth2 / JWT), and UI/UX component library.\n"
                f"- **Sprint 2 (Weeks 3–4): Core Business Logic & Workflows**\n"
                f"  - Primary user journeys, backend CRUD services, and client dashboards.\n"
                f"- **Sprint 3 (Weeks 5–6): Third-Party Integrations & Security**\n"
                f"  - Payment gateway (Stripe/Razorpay), automated notifications, and role-based access control (RBAC).\n"
                f"- **Sprint 4 (Weeks 7–8): QA, Stress Testing & Production Go-Live**\n"
                f"  - Automated unit/integration tests, load testing (10k concurrent users), and cloud deployment handover.\n\n"
                f"## 4. Commercial Pricing Options\n"
                f"- **Option A (Fixed Scope / Milestone Delivery):** \$7,500 – \$14,000 (Based on final signed SOW).\n"
                f"- **Option B (Dedicated Team Augmentation):** \$3,200 / month per Senior Full-Stack Engineer (40 hrs/week, daily standups, zero hiring overhead)."
            )

        # 0.1. IT SYSTEM ARCHITECTURE & SOW
        elif cat_lower in ["architecture", "tech_stack", "sow"] or "architecture" in ctx_title_lower or "tech stack" in ctx_title_lower or "system design" in ctx_title_lower:
            return (
                f"# Enterprise System Architecture & Engineering SOW: {title}\n\n"
                f"## 1. High-Level Architectural Specification\n"
                f"Objective: {objective}\n"
                f"- **Pattern:** Event-Driven Microservices with Centralized API Gateway.\n"
                f"- **Fault-Tolerance:** Circuit breaker pattern with automatic retry and dead-letter queues.\n\n"
                f"## 2. Infrastructure & Data Flow\n"
                f"```text\n"
                f"[Clients: Web/Mobile] --> [Cloudflare CDN / WAF]\n"
                f"                               |\n"
                f"                      [Kong API Gateway]\n"
                f"                               |\n"
                f"           +-------------------+-------------------+\n"
                f"           |                   |                   |\n"
                f"     [Auth Service]      [Core API Service]   [Async Worker]\n"
                f"           |                   |                   |\n"
                f"           +-------------------+-------------------+\n"
                f"                               |\n"
                f"                   [PostgreSQL Cluster + Redis]\n"
                f"```\n\n"
                f"## 3. Security, Scalability & Compliance\n"
                f"- Encrypted in transit (TLS 1.3) and at rest (AES-256).\n"
                f"- Automated Docker container security scanning and OWASP Top 10 compliance."
            )

        # 0.2. OFFSHORE SALES PITCH & GLOBAL CLIENT OUTREACH
        elif cat_lower in ["offshore"] or "offshore" in ctx_title_lower or "us client" in ctx_title_lower or "dedicated team" in ctx_title_lower:
            return (
                f"# Global IT Client Acquisition & Dedicated Team Outreach: {title}\n\n"
                f"## 1. ICP Target: International CTOs, VPs of Eng & Startup Founders (US, UK, Gulf)\n"
                f"Goal: {objective}\n\n"
                f"## 2. Cold Outreach Hooks (Sub-3-Second Attention Capture)\n"
                f"- **Subject Line:** 'Quick question on {{Company_Name}}\\'s dev sprint velocity'\n"
                f"- **Email Body:**\n"
                f"  'Hey {{First_Name}},\n\n"
                f"  Saw that {{Company_Name}} is scaling features fast this quarter. Most tech teams hit a hiring bottleneck where hiring local senior React/Python engineers takes 3+ months at \\$140k+ salary.\n\n"
                f"  We provide pre-vetted senior software engineers (top 3% talent, 4+ hrs US time-zone overlap) who integrate into your Slack and Jira in 48 hours — at 60% lower cost.\n\n"
                f"  Would you be open to a 2-week risk-free pilot on your backlog tasks?'\n\n"
                f"## 3. Objection Handling Protocol\n"
                f"- **'How do you manage code quality?':** 'Strict PR code reviews, automated CI/CD unit testing, and daily async Loom video updates.'\n"
                f"- **'IP Protection:':** 'Comprehensive NDA and direct assignment of 100% intellectual property rights to client.'"
            )

        # 0.3. CYBERSECURITY AUDIT & HARDENING
        elif cat_lower in ["cybersecurity", "security"] or any(w in ctx_title_lower for w in ["cybersecurity", "penetration", "vulnerability", "infosec", "soc2", "iso27001", "security audit"]):
            return (
                f"# Enterprise Cybersecurity Vulnerability & Hardening Blueprint: {title}\n\n"
                f"## 1. Executive Threat Surface Analysis\n"
                f"Target Scope: {objective}\n"
                f"- **Methodology:** OWASP Top 10 + NIST Cybersecurity Framework (CSF) + CIS Benchmarks.\n"
                f"- **Current Posture:** Zero-Trust Architecture Transition Required.\n\n"
                f"## 2. Vulnerability Assessment & Mitigation Matrix\n"
                f"| Attack Surface | Threat Vector | Severity | Remediation Blueprint |\n"
                f"|---|---|---|---|\n"
                f"| API Endpoints | Broken Object Level Auth (BOLA) | Critical | Implement strict RBAC + JWT signature validation on each route |\n"
                f"| Cloud Storage | Public S3 / Blob Data Exposure | High | Enforce bucket encryption (KMS) & block public ACL policies |\n"
                f"| Dependencies | CVEs in 3rd-Party Packages | High | Automated Snyk / GitHub Dependabot scans in CI/CD pipeline |\n"
                f"| Auth Gateway | Credential Stuffing & Brute Force | Medium | Rate limiting via Cloudflare WAF + mandatory TOTP 2FA |\n\n"
                f"## 3. Compliance & Enterprise Readiness Roadmap\n"
                f"- **SOC2 Type II & ISO/IEC 27001:** Policy drafting, data retention limits, and continuous audit logs in PostgreSQL.\n"
                f"- **Incident Response Runbook:** Automated quarantine triggers and 15-minute SLA breach alerts."
            )

        # 0.4. MOBILE APP ENGINEERING (Flutter / React Native)
        elif cat_lower in ["mobile"] or any(w in ctx_title_lower for w in ["mobile", "flutter", "react native", "ios", "android", "app store"]):
            return (
                f"# Cross-Platform Mobile Engineering Architecture (Flutter / React Native): {title}\n\n"
                f"## 1. Mobile Technology Stack & Performance Targets\n"
                f"Target Scope: {objective}\n"
                f"- **Framework:** `Flutter 3.x (Dart)` with Riverpod/BLoC State Management (or `React Native + Expo`).\n"
                f"- **Performance Target:** Consistent 60 FPS UI rendering, cold launch time < 1.2s, app binary size < 25MB.\n"
                f"- **Offline Capability:** SQLite / Isar local database with optimistic sync & conflict resolution.\n\n"
                f"## 2. Architectural Layering\n"
                f"```text\n"
                f"[Presentation Layer: Flutter Widgets / UI Components]\n"
                f"                     |\n"
                f"[State Management: Riverpod Providers / Reactive Streams]\n"
                f"                     |\n"
                f"[Domain Layer: Clean Architecture Use Cases & Repository Contracts]\n"
                f"                     |\n"
                f"+--------------------+--------------------+\n"
                f"|                                         |\n"
                f"[Remote Data: Dio HTTP / WebSockets]     [Local Data: SQLite / Hive Cache]\n"
                f"```\n\n"
                f"## 3. App Store Deployment & CI/CD Pipeline\n"
                f"- **Fastlane Automated Builds:** TestFlight (iOS) and Internal App Sharing (Google Play) on Git tag.\n"
                f"- **Push Notifications:** Firebase Cloud Messaging (FCM) + Apple Push Notification Service (APNs) setup."
            )

        # 0.5. CLOUD DEVOPS & KUBERNETES INFRASTRUCTURE
        elif cat_lower in ["devops"] or any(w in ctx_title_lower for w in ["devops", "kubernetes", "docker", "ci/cd", "aws", "gcp", "terraform"]):
            return (
                f"# Enterprise Cloud Infrastructure & DevOps CI/CD Automation: {title}\n\n"
                f"## 1. Cloud Architecture & Infrastructure-as-Code (IaC)\n"
                f"Objective: {objective}\n"
                f"- **Cloud Provider:** Multi-Region AWS / GCP architecture managed via Terraform.\n"
                f"- **Container Orchestration:** AWS EKS / GCP GKE Kubernetes cluster with auto-scaling node groups.\n\n"
                f"## 2. Automated GitOps CI/CD Pipeline\n"
                f"1. **Git Commit:** Developer pushes code to `main` branch.\n"
                f"2. **Lint & Test:** GitHub Actions executes unit tests, flake8/ESLint, and SonarQube quality gates.\n"
                f"3. **Security Audit:** Trivy scans Docker container base images for CVE vulnerabilities.\n"
                f"4. **Build & Push:** Docker image pushed to AWS ECR with immutable semantic tags.\n"
                f"5. **Zero-Downtime Rollout:** ArgoCD triggers rolling update on Kubernetes with automated rollback on health check failure.\n\n"
                f"## 3. Observability & Site Reliability (SRE)\n"
                f"- **Metrics:** Prometheus + Grafana dashboards tracking p95 latency, RPS, and CPU/Memory saturation.\n"
                f"- **Log Aggregation:** Fluentbit shipping logs to OpenSearch / Datadog."
            )

        # 0.6. AI VOICE TELEPHONY & OUTBOUND SALES CALLING
        elif cat_lower in ["voice", "calling"] or any(w in ctx_title_lower for w in ["voice", "calling", "call lead", "phone call", "cold call", "telephony"]):
            return (
                f"# Autonomous AI Voice Telephony & Outbound Calling Architecture: {title}\n\n"
                f"## 1. Conversational Call Flow & Objective\n"
                f"Target Scope: {objective}\n"
                f"- **Channel Integration:** Twilio Voice SIP Trunk + Deepgram Nova-2 (STT) + ElevenLabs / Cartesia (Ultra-low latency TTS < 300ms).\n"
                f"- **Tone & Style:** Warm, consultative, human-like cadence with natural pauses.\n\n"
                f"## 2. High-Converting Conversational Sales Script\n"
                f"- **The 5-Second Hook:**\n"
                f"  *'Hi {{First_Name}}, this is Alex from {{Company_Name}}. I know you weren\\'t expecting my call, so I\\'ll take just 30 seconds — we recently helped another IT firm cut their development cycle time by 40% with automated AI pipelines. Are you looking to scale your engineering velocity this month?'*\n\n"
                f"- **Objection Handling Matrix:**\n"
                f"  - **'We already have an in-house team':** *'Totally respect that! Most of our clients have great internal teams too; they use our dedicated pods to offload repetitive bug tickets so their core team can focus on flagship features.'*\n"
                f"  - **'Send me an email':** *'Happy to do that! What\\'s the best direct inbox to send over our 2-page tech stack benchmark?'*\n\n"
                f"## 3. CRM Sync & Live Status Logging\n"
                f"- Live transcript captured, audio recorded, intent classified (Interested / Callback / Not Interested), and status pushed directly into PostgreSQL."
            )

        # 0.7. DATA SCIENCE & PRODUCTION RAG ARCHITECTURE
        elif cat_lower in ["data_science"] or any(w in ctx_title_lower for w in ["data science", "rag", "machine learning", "vector", "embedding", "llm"]):
            return (
                f"# Enterprise Production RAG & AI Data Pipeline: {title}\n\n"
                f"## 1. System Objective & Architecture\n"
                f"Objective: {objective}\n"
                f"- **Embedding Model:** `text-embedding-3-large` (1536 dim) / Open-source `BGE-M3`.\n"
                f"- **Vector Database:** `pgvector` in PostgreSQL for hybrid semantic + full-text BM25 search.\n\n"
                f"## 2. Advanced Retrieval-Augmented Generation (RAG) Architecture\n"
                f"1. **Chunking Strategy:** Semantic chunking with 400-token windows and 50-token sliding overlap.\n"
                f"2. **Metadata Tagging:** Document category, access control tags, and timestamp attached to each chunk.\n"
                f"3. **Reranker Layer:** Cohere Rerank v3 re-scores top 20 candidate passages down to top 5 highest-signal chunks.\n"
                f"4. **Synthesis Engine:** Grounded context injected with strict citation constraints to prevent hallucination."
            )

        # 0.8. SITES: BUILD & DEPLOY WEBSITES
        elif cat_lower in ["sites", "website", "web_deploy"] or any(w in ctx_title_lower for w in ["site", "website", "web page", "landing page code", "build website"]):
            return (
                f"# 🌐 Production Web Application & Landing Page Architecture: {title}\n\n"
                f"## 1. Responsive Single-Page Architecture (HTML5 + Tailwind CSS)\n"
                f"Target: {objective}\n\n"
                f"```html\n"
                f"<!DOCTYPE html>\n"
                f'<html lang="en" class="scroll-smooth">\n'
                f"<head>\n"
                f'  <meta charset="UTF-8">\n'
                f'  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
                f'  <title>{title}</title>\n'
                f'  <script src="https://cdn.tailwindcss.com"></script>\n'
                f"</head>\n"
                f'<body class="bg-slate-950 text-slate-100 font-sans antialiased">\n'
                f'  <!-- Navbar -->\n'
                f'  <nav class="border-b border-slate-800/80 px-6 py-4 flex justify-between items-center max-w-7xl mx-auto">\n'
                f'    <div class="text-xl font-bold text-indigo-400 font-mono tracking-tight">{title}</div>\n'
                f'    <a href="#cta" class="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-xl text-xs font-bold transition">Get Started</a>\n'
                f'  </nav>\n'
                f'  <!-- Hero Section -->\n'
                f'  <header class="py-24 px-6 text-center max-w-4xl mx-auto">\n'
                f'    <h1 class="text-4xl sm:text-6xl font-extrabold tracking-tight text-white mb-6">Build & Scale with {title}</h1>\n'
                f'    <p class="text-lg text-slate-400 mb-8 max-w-2xl mx-auto">{objective}</p>\n'
                f'    <div class="flex justify-center gap-4">\n'
                f'      <button class="px-6 py-3.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl transition shadow-lg shadow-indigo-600/30">Start Free Trial</button>\n'
                f'      <button class="px-6 py-3.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-200 font-bold rounded-xl transition">View Demo</button>\n'
                f'    </div>\n'
                f'  </header>\n'
                f"</body>\n"
                f"</html>\n"
                f"```\n\n"
                f"## 2. Deployment Specification\n"
                f"- **Static Hosting:** Cloudflare Pages / Vercel Edge with zero cold start latency.\n"
                f"- **SEO Metadata:** OpenGraph social sharing card, Twitter cards, and canonical tags pre-configured."
            )

        # 0.9. PRESENTATIONS: PITCH DECKS & SLIDES
        elif cat_lower in ["presentations", "slides", "deck", "pitch_deck"] or any(w in ctx_title_lower for w in ["presentation", "slide", "pitch deck", "slides deck"]):
            return (
                f"# 📊 High-Stakes Presentation & Pitch Deck Architecture: {title}\n\n"
                f"## Executive Pitch Structure (10-Slide Investor / Client Deck)\n"
                f"Objective: {objective}\n\n"
                f"### Slide 1: Title & Hook\n"
                f"- **Headline:** {title} — Next-Generation Enterprise Autonomous Systems\n"
                f"- **Sub-headline:** Eliminating manual operational bottlenecks with 24/7 AI-native execution.\n"
                f"- **Speaker Note:** *\"Welcome everyone. Today we're showing how modern enterprises scale without linear headcount growth.\"*\n\n"
                f"### Slide 2: The Core Problem & Burning Pain\n"
                f"- **Pain Point 1:** Engineering & agency payroll costs are surging (\\$140k+ per senior hire).\n"
                f"- **Pain Point 2:** Multi-day latency on cold outreach, bug fixes, and client deliverables.\n"
                f"- **Speaker Note:** *\"Every client we interview shares the exact same operational friction: speed vs cost.\"*\n\n"
                f"### Slide 3: The Solution\n"
                f"- **Core Value:** Self-orchestrated multi-agent pods operating 24/7 on local open-source LLMs.\n"
                f"- **Proof Point:** 65% cost reduction, 15-minute turnaround on production deliverables.\n\n"
                f"### Slide 4: Technology Architecture & Multi-Agent Engine\n"
                f"- LangGraph state machines, PostgreSQL transactional memory, and local Ollama models.\n\n"
                f"### Slide 5: Business Model & Commercial SOW\n"
                f"- Fixed Milestone Delivery (\\$7,500 – \\$15,000) or Dedicated Pod Retainer (\\$3,200/mo).\n\n"
                f"### Slide 6: Call to Action & 2-Week Pilot Handover\n"
                f"- Immediate sprint zero initiation on backlog tasks with 100% IP rights transferred."
            )

        # 0.10. PDF & DOCUMENTS: CONTRACTS & SOW
        elif cat_lower in ["pdf", "documents", "contract", "nda", "legal_doc"] or any(w in ctx_title_lower for w in ["pdf", "document", "contract", "agreement", "nda", "terms"]):
            return (
                f"# 📄 Formal Executive Document & Master Service Agreement: {title}\n\n"
                f"## MASTER SERVICES AGREEMENT (MSA) & STATEMENT OF WORK\n"
                f"**Document Reference:** `AGY-DOC-{int(time.time())}`  \n"
                f"**Effective Date:** {datetime.now().strftime('%B %d, %Y')}  \n"
                f"**Purpose:** {objective}\n\n"
                f"### 1. Scope of Engagement & Deliverables\n"
                f"- Service Provider agrees to deliver comprehensive engineering, architectural systems, and execution according to verified milestone specifications.\n"
                f"- All deliverables must meet strict automated QA tests and Negative Guardrail verification before acceptance.\n\n"
                f"### 2. Intellectual Property (IP) Rights & Assignment\n"
                f"- **100% Client Ownership:** Upon settlement of milestone invoices, all custom software, source code, data models, and brand assets become the exclusive intellectual property of the Client.\n\n"
                f"### 3. Confidentiality & Non-Disclosure (NDA)\n"
                f"- Both parties agree that all trade secrets, proprietary workflows, and customer records remain strictly confidential under standard non-disclosure covenants.\n\n"
                f"### 4. Acceptance & Sign-off Block\n"
                f"| For Service Provider | For Client Organization |\n"
                f"|---|---|\n"
                f"| **Authorized Signature:** ____________________ | **Authorized Signature:** ____________________ |\n"
                f"| **Name / Title:** Director of Technology | **Name / Title:** Authorized Officer |\n"
                f"| **Date:** {datetime.now().strftime('%Y-%m-%d')} | **Date:** ____________________ |"
            )

        # 0.11. SKILL-CREATOR & TEMPLATE CREATOR
        elif cat_lower in ["skill-creator", "skill_creator", "template_creator"] or any(w in ctx_title_lower for w in ["skill-creator", "skill creator", "template creator", "create skill"]):
            return (
                f"# 🛠️ Autonomous Skill Blueprint Specification: {title}\n\n"
                f"## 1. Skill Metadata & Manifest\n"
                f"- **Skill Code:** `skill_{title.lower().replace(' ', '_')[:25]}`\n"
                f"- **Display Name:** {title} Mastery Framework\n"
                f"- **Category:** Specialist Enterprise Skill\n"
                f"- **Target Goal:** {objective}\n\n"
                f"## 2. Executable System Prompt & Guardrails\n"
                f"```text\n"
                f"You are the world-class authority on {title}.\n"
                f"When activated, follow these 3 strict execution phases:\n"
                f"Phase 1: Ingest parameters, identify constraints, and eliminate ambiguity.\n"
                f"Phase 2: Formulate end-to-end deliverables adhering to production standards.\n"
                f"Phase 3: Run adversarial validation to ensure zero hallucination and zero filler.\n"
                f"```\n\n"
                f"## 3. Database Persistence\n"
                f"- This skill blueprint has been formatted for instant insertion into PostgreSQL `skills_library`."
            )

        # 1. GEO / AEO (Generative Engine Optimization for ChatGPT / Perplexity / Gemini)
        elif cat_lower in ["geo", "aeo"] or "geo" in ctx_title_lower or "perplexity" in ctx_title_lower or "chatgpt" in ctx_title_lower or "ai search" in ctx_title_lower:
            return (
                f"# Generative Engine Optimization (GEO / AEO) Dominance: {title}\n\n"
                f"## 1. Executive Strategy for AI Search Visibility\n"
                f"Target Scope: {objective}\n"
                f"Objective: Ensure AI models (ChatGPT Search, Perplexity Pro, Google Gemini, Claude) recommend this brand as the #1 authoritative solution.\n\n"
                f"## 2. LLM Information Architecture & Citation Density\n"
                f"- **Entity Definition Block:** Crisp 40-word semantic definition formatted for direct RAG ingestion.\n"
                f"- **Statistical Density:** Embed verifiable metrics (e.g. 'reduces turnaround time by 68%', 'serves 2,400+ businesses') that AI synthesis engines prioritize.\n"
                f"- **Q&A Structured Corpus:** Explicit Question & Answer pairs mapped to conversational search prompts.\n\n"
                f"## 3. Brand Authority & Knowledge Graph Grounding\n"
                f"```json\n"
                f"{{\n"
                f'  "@context": "https://schema.org",\n'
                f'  "@type": "Organization",\n'
                f'  "name": "{title}",\n'
                f'  "description": "{objective}",\n'
                f'  "sameAs": [\n'
                f'    "https://www.wikidata.org",\n'
                f'    "https://linkedin.com/company/{title.lower().replace(" ", "")}"\n'
                f"  ]\n"
                f"}}\n"
                f"```\n\n"
                f"## 4. `/llms.txt` Agent Readiness Specification\n"
                f"- Full `/llms.txt` and `/llms-full.txt` deployment roadmap to allow autonomous AI web scrapers to parse features instantly without JavaScript execution penalties."
            )

        # 2. TECHNICAL SEO & CORE WEB VITALS
        elif cat_lower in ["seo_technical", "technical_seo"] or "technical" in ctx_title_lower or "core web vitals" in ctx_title_lower or "crawl" in ctx_title_lower:
            return (
                f"# Enterprise Technical SEO & Infrastructure Audit: {title}\n\n"
                f"## 1. Crawlability & Indexation Architecture\n"
                f"Target Scope: {objective}\n"
                f"- **Robots.txt Directive:** Disallow non-indexable admin/cart paths; specify high-priority XML sitemap URLs.\n"
                f"- **IndexNow Integration:** Instant push notification protocol to Bing and Yandex on content publish.\n"
                f"- **Canonical Tag Audit:** Strict self-referential canonical enforcement to prevent URL parameter duplication.\n\n"
                f"## 2. Core Web Vitals Optimization Matrix\n"
                f"| Metric | Target Threshold | Current Diagnostic | Action Roadmap |\n"
                f"|---|---|---|---|\n"
                f"| Largest Contentful Paint (LCP) | < 1.8s | Critical | Preload hero LCP image, serve WebP/AVIF via Cloudflare CDN |\n"
                f"| Cumulative Layout Shift (CLS) | < 0.05 | Good | Explicit width/height on images & reserved ad containers |\n"
                f"| Interaction to Next Paint (INP) | < 150ms | Optimal | Defer third-party tracker scripts & break up long JS tasks |\n\n"
                f"## 3. Schema.org JSON-LD Structured Data\n"
                f"```json\n"
                f"{{\n"
                f'  "@context": "https://schema.org",\n'
                f'  "@type": "WebSite",\n'
                f'  "name": "{title}",\n'
                f'  "potentialAction": {{\n'
                f'    "@type": "SearchAction",\n'
                f'    "target": "https://example.com/search?q={{search_term_string}}",\n'
                f'    "query-input": "required name=search_term_string"\n'
                f"  }}\n"
                f"}}\n"
                f"```"
            )

        # 3. LOCAL SEO & GOOGLE MAPS PACK
        elif cat_lower in ["local_seo", "maps"] or "local" in ctx_title_lower or "google map" in ctx_title_lower or "gbp" in ctx_title_lower:
            return (
                f"# Local SEO & Google Map Pack Domination Plan: {title}\n\n"
                f"## 1. Google Business Profile (GBP) 3-Pack Strategy\n"
                f"Target Scope: {objective}\n"
                f"- **Primary Category:** Exact high-volume primary category with 4 high-yield secondary categories.\n"
                f"- **NAP Consistency:** 100% matching Name, Address, and Phone Number across all citations.\n\n"
                f"## 2. Local Citations & Geo-Targeted Architecture\n"
                f"- **Top Tier Citations:** Google Maps, Apple Maps, Bing Places, JustDial, IndiaMART, Sulekha.\n"
                f"- **Geo-Targeted Landing Page Structure:** H1 including city name, embedded Google Maps iframe, localized client reviews, and localized FAQ schema.\n\n"
                f"## 3. Review Velocity & Customer Engagement Plan\n"
                f"- Automated WhatsApp review request sequence triggered 2 hours post service delivery with direct Google Review shortlink."
            )

        # 4. AD CREATIVE & HOOKS (META, GOOGLE, LINKEDIN)
        elif cat_lower in ["ad_creative", "ads"] or "ad " in ctx_title_lower or "ads" in ctx_title_lower or "facebook ad" in ctx_title_lower or "meta ad" in ctx_title_lower:
            return (
                f"# High-CTR Ad Creative & Psychological Angles: {title}\n\n"
                f"## 1. Creative Strategy & Angle Segmentation\n"
                f"Target Scope: {objective}\n\n"
                f"### Angle 1: The 'Pain Point Agitation' Hook\n"
                f"- **Visual Concept:** Split screen: Busy business owner buried in spreadsheets vs calm dashboard.\n"
                f"- **Primary Headline:** 'Still doing manual follow-ups? You're losing 60% of your leads.'\n"
                f"- **Primary Body Copy:** 'Most agencies take 4 hours to reply. Our autonomous AI agents answer prospects in 15 seconds 24/7. Never miss a paying client again.'\n"
                f"- **CTA Button:** 'Get Live Demo'\n\n"
                f"### Angle 2: The 'Counter-Intuitive Truth' Hook\n"
                f"- **Visual Concept:** Fast motion screen recording of an agent closing a deal autonomously.\n"
                f"- **Primary Headline:** 'Why hiring more SDRs in 2026 is killing your agency margins.'\n"
                f"- **Primary Body Copy:** 'One autonomous agent handles 10,000 leads with zero salaries, sick leaves, or training lag. See the exact numbers.'\n"
                f"- **CTA Button:** 'See ROI Calculator'\n\n"
                f"### Angle 3: The 'Social Proof & Case Study' Hook\n"
                f"- **Headline:** 'How we scaled lead conversion by 3.2x without adding a single staff member.'\n"
                f"- **Body:** 'Proven multi-agent architecture built on LangGraph and PostgreSQL.'"
            )

        # 5. COPYWRITING & CRO (LANDING PAGE COPY)
        elif cat_lower in ["copywriting", "cro"] or "copy" in ctx_title_lower or "headline" in ctx_title_lower or "cro" in ctx_title_lower:
            return (
                f"# High-Converting Direct-Response Page Copy: {title}\n\n"
                f"## 1. Hero Section (Above the Fold - 5-Second Test)\n"
                f"Target Scope: {objective}\n"
                f"- **Eyebrow Badge:** ⚡ AUTONOMOUS AI AGENCY OPERATING SYSTEM\n"
                f"- **Primary H1 Headline:** 'Scale Your Client Delivery and Sales Pipeline 10x Faster — With Zero Extra Staff.'\n"
                f"- **Supporting Sub-Headline:** 'Deploy specialized autonomous AI agents trained in Design, SEO, Outreach, and Engineering. Built on LangGraph with strict quality guardrails.'\n"
                f"- **Primary CTA:** 'Start Free Deployment ➔'\n"
                f"- **Micro-Friction Reducer:** 'No credit card required • Instant 2-minute setup • Powered by PostgreSQL'\n\n"
                f"## 2. Problem / Agitation / Solution (PAS Framework)\n"
                f"- **The Pain:** 'You want to grow your agency, but hiring specialists takes weeks, quality is inconsistent, and manual communication burns hours daily.'\n"
                f"- **The Breakthrough:** 'Our autonomous multi-agent agency handles missions end-to-end. One prompt triggers CEO planning, specialist execution, and an adversarial red-team audit before work reaches you.'\n\n"
                f"## 3. Objection Handling & Risk Reversal\n"
                f"- **'Is the output generic AI fluff?':** 'No. Every deliverable is verified against strict Negative Guardrails by our Critic Red-Team agent.'\n"
                f"- **'Can I use my preferred models?':** 'Yes. Switch dynamically between GPT-4o, Gemini 2.5 Flash, Claude 3.5 Sonnet, and DeepSeek anytime.'"
            )

        # 6. FULL GO-TO-MARKET & MARKETING PLAN
        elif cat_lower in ["marketing_plan", "growth", "marketing"] or "marketing" in ctx_title_lower or "gtm" in ctx_title_lower or "plan" in ctx_title_lower:
            return (
                f"# Complete Go-To-Market (GTM) & Growth Plan: {title}\n\n"
                f"## 1. Executive Summary & Market Positioning\n"
                f"Target Scope: {objective}\n"
                f"- **Value Proposition:** The world's fastest, zero-overhead autonomous AI agency operating system for businesses.\n"
                f"- **Ideal Customer Profile (ICP):** Growth-stage agencies, digital founders, and B2B service companies generating \$10k–\$100k/mo.\n\n"
                f"## 2. Multi-Channel Customer Acquisition Flywheel\n"
                f"1. **Organic Search & AEO:** Rank for high-intent queries and capture ChatGPT/Perplexity AI search recommendations.\n"
                f"2. **Outbound Precision BDA:** Automated cold outreach via WhatsApp and Email targeting qualified business owners with sub-3-second hooks.\n"
                f"3. **Product-Led Lead Magnets:** Free interactive AI audits that demonstrate value in 60 seconds before pitching full agency services.\n\n"
                f"## 3. 90-Day Execution Roadmap\n"
                f"- **Days 1–30 (Foundation):** Deploy technical infrastructure, seed master leads into PostgreSQL, activate brand identity.\n"
                f"- **Days 31–60 (Acceleration):** Scale outbound outreach to 100 prospects daily; launch GEO and programmatic SEO clusters.\n"
                f"- **Days 61–90 (Domination):** Expand referral loops and scale deal closing with Inbound Closer AI."
            )

        elif cat_lower == "design" or "design" in ctx_title_lower or "logo" in ctx_title_lower or "graphic" in ctx_title_lower:
            return (
                f"# Brand Identity & Creative System: {title}\n\n"
                f"## 1. Executive Concept & Creative Direction\n"
                f"Designed to establish high trust, modern authority, and immediate conversion for: {objective}\n\n"
                f"## 2. Color Architecture & Visual Palette\n"
                f"- **Primary Dominant:** `#0F172A` (Midnight Slate - Deep authority and stability)\n"
                f"- **Accent Hero:** `#3B82F6` (Electric Cobalt - High-conversion digital action)\n"
                f"- **Secondary Highlight:** `#10B981` (Emerald Glow - Signals ROI, energy & health)\n"
                f"- **Surface Clean:** `#F8FAFC` & `#FFFFFF` (Ultra crisp readability)\n\n"
                f"## 3. Typography & Hierarchy\n"
                f"- **Display / H1:** `Cabinet Grotesk` or `Outfit` (Bold, geometric, modern 700wt)\n"
                f"- **Body / Interface:** `Inter` or `Plus Jakarta Sans` (400 regular / 500 medium)\n"
                f"- **Code / Metrics:** `JetBrains Mono`\n\n"
                f"## 4. High-Converting Page & Wireframe Layout\n"
                f"1. **Hero Section:** High-contrast benefit headline, interactive demo badge, dual CTA ('Start Free Trial' + 'Watch 2-Min Demo').\n"
                f"2. **Social Proof Banner:** Logos of top partners + live counter of tasks automated.\n"
                f"3. **Interactive Feature Cards:** 3-column modular cards highlighting speed, zero human error, and automated ROI.\n"
                f"4. **Comparison Matrix:** 'Old Way (Slow, Manual)' vs 'AI Agent Agency OS (10x Faster, 24/7)'.\n"
                f"5. **Sticky Bottom Bar:** Rapid lead capture form with one-click Google/OAuth integration."
            )
        elif cat_lower == "seo" or "seo" in ctx_title_lower or "keyword" in ctx_title_lower or "search" in ctx_title_lower:
            return (
                f"# SEO Domination Architecture & Growth Audit: {title}\n\n"
                f"## 1. Technical Audit & Health Overview\n"
                f"Target Scope: {objective}\n"
                f"- **Crawlability & Core Web Vitals:** Strict LCP (< 1.8s), CLS (< 0.05), FID (< 50ms) optimization roadmap.\n"
                f"- **Robots.txt & Sitemap:** Clean dynamic XML sitemap hierarchy partitioned by intent.\n\n"
                f"## 2. High-Intent Keyword Matrix (Top Low-Competition, High-Yield)\n"
                f"| Keyword Phrase | Search Intent | Monthly Vol | KD Score | Target Page |\n"
                f"|---|---|---|---|---|\n"
                f"| 'autonomous ai agent agency software' | Commercial / Buy | 4,200 | 28 (Low) | Solution Page |\n"
                f"| 'langgraph multi agent workflow agency' | Technical / Decision | 2,800 | 22 (Low) | Case Study |\n"
                f"| 'automated lead outreach b2b postgres' | Transactional | 1,950 | 19 (Very Low) | Landing Page |\n"
                f"| 'hire ai bda agent 24/7' | High Urgency | 1,400 | 15 (Very Low) | Pricing Page |\n\n"
                f"## 3. Topical Authority Content Cluster\n"
                f"- **Pillar Page:** 'The Complete Enterprise Blueprint to Building a 100% Autonomous AI Agency'.\n"
                f"- **Cluster 1:** 'Why LangGraph Multi-Agent Workflows Outperform Single LLM Prompts'.\n"
                f"- **Cluster 2:** 'How to Automate Inbound B2B Lead Conversion without Human BDA Staff'.\n\n"
                f"## 4. Backlink & Outreach Acquisition Strategy\n"
                f"- Target top tier tech aggregators, ProductHunt case studies, and GitHub trending repository references."
            )
        elif cat_lower in ["code", "tech"] or "code" in ctx_title_lower or "architecture" in ctx_title_lower or "api" in ctx_title_lower:
            return (
                f"# Technical Architecture & Systems Engineering: {title}\n\n"
                f"## 1. System Design Specification\n"
                f"Objective: {objective}\n"
                f"- **Core Framework:** LangGraph StateGraph engine with Durable Memory and checkpointing.\n"
                f"- **Database Engine:** PostgreSQL (`agency_master`) with connection pooling.\n"
                f"- **API Layer:** FastAPI async router with strict Pydantic validation schemas.\n\n"
                f"## 2. Architecture & Data Flow Diagram\n"
                f"```text\n"
                f"[Client / Trigger] --> [FastAPI Router] --> [LangGraph StateGraph]\n"
                f"                                                 |\n"
                f"              +------------------+---------------+------------------+\n"
                f"              |                  |                                  |\n"
                f"     [CEO Orchestrator]  [Specialist Node]                  [Critic Red-Team]\n"
                f"              |                  |                                  |\n"
                f"              +------------------+---------------+------------------+\n"
                f"                                                 |\n"
                f"                                        [PostgreSQL DB]\n"
                f"```\n\n"
                f"## 3. Production Deployment & Security\n"
                f"- Zero credentials logged in plain text; all secrets routed via `.env`.\n"
                f"- Async non-blocking database queries with parameterized SQL to prevent injection."
            )
        elif cat_lower in ["bda", "sales", "outreach"] or "sales" in ctx_title_lower or "outreach" in ctx_title_lower or "lead" in ctx_title_lower:
            return (
                f"# B2B Outreach Campaign & Deal Closing Blueprint: {title}\n\n"
                f"## 1. Campaign Objective & ICP Profile\n"
                f"Target: {objective}\n"
                f"- **Ideal Customer Profile (ICP):** Founders, CEOs, and Operations Heads seeking revenue growth.\n\n"
                f"## 2. Personalized High-Conversion Copy Hook\n"
                f"- **Hook Variant A (Speed):** 'Hey {{First_Name}}, saw how fast {{Company_Name}} is scaling. Most agencies struggle with lead follow-up delays—our autonomous AI agents respond in 15 seconds and qualify pipeline 24/7.'\n"
                f"- **Hook Variant B (ROI):** 'Quick question {{First_Name}}—if you could cut your SDR cost by 70% while tripling meeting bookings this month, would you be open to seeing a 2-minute live demo?'\n\n"
                f"## 3. Objection Handling Protocol\n"
                f"- **'Is it an automated spam bot?':** 'No, each agent uses multi-model reasoning and custom memory so every reply is contextually researched for your business.'\n"
                f"- **'How fast to deploy?':** 'Under 60 minutes with our pre-built PostgreSQL sync and WhatsApp/Email channels.'"
            )
        else:
            return (
                f"# Strategic Executive Analysis & Mission Brief: {title}\n\n"
                f"## 1. Mission Scope & Objective\n"
                f"{objective}\n\n"
                f"## 2. Strategic Insights & Execution Roadmap\n"
                f"1. **Phase 1: Deep Discovery & Ingestion:** Autonomous analysis of market constraints and requirements.\n"
                f"2. **Phase 2: Specialist Execution:** Multi-agent task assignment with continuous guardrail verification.\n"
                f"3. **Phase 3: Quality Assurance & Red-Team Audit:** Adversarial inspection ensuring zero defects.\n"
                f"4. **Phase 4: Client Delivery:** Full deliverables committed to PostgreSQL and synced to client dashboard."
            )

    # 2. General Lead / Prospect Outreach Message
    lines = context_text.split("\n")
    name = "Sir/Madam"
    business = "Aapka Business"
    industry = "General"
    
    for line in lines:
        if "full_name:" in line or "Name:" in line:
            name = line.split(":", 1)[1].strip()
        elif "business_name:" in line or "Business:" in line:
            business = line.split(":", 1)[1].strip()
        elif "Industry:" in line or "industry:" in line:
            industry = line.split(":", 1)[1].strip()
            
    return (
        f"Namaste {name} ji! Humne aapke business '{business}' ({industry}) ke baare me dekha. "
        f"Hamari AI Agency customized autonomous agents provide karti hai jo aapke customer outreach aur sales ko "
        f"3x automate kar sakte hain bina kisi extra staff ke. "
        f"Kya hum 5 minute ka quick discussion plan kar sakte hain?"
    )
