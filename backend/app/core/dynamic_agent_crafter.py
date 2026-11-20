import re
import json
from typing import Dict, Any, Tuple, Optional, List
from backend.app.core.database import query_db, execute_db

def detect_and_auto_create_agent(user_prompt: str) -> Optional[Dict[str, Any]]:
    """
    Self-Expanding Autonomous Agent OS:
    If a user asks for a capability or domain that no existing agent covers,
    the CEO Orchestrator automatically creates, equips, and registers a brand new
    specialized AI Agent into PostgreSQL 'agents' and 'skills_library'!
    """
    prompt_lower = user_prompt.lower()

    # Query existing agent names & roles from database
    existing_agents = query_db("SELECT name, role FROM agents;")
    existing_text = " ".join([f"{a['name']} {a['role']}" for a in existing_agents]).lower()

    # Comprehensive Domain Blueprints
    specialty_blueprints = [
        {
            "trigger_keywords": ["cybersecurity", "security audit", "penetration test", "hacker", "vulnerability", "infosec", "soc2", "iso27001", "firewall", "owasp"],
            "agent_name": "Cybersecurity_Security_Agent",
            "role": "Chief Information Security Officer & Penetration Tester",
            "persona": "Hardened Enterprise Security Auditor & Vulnerability Specialist",
            "provider": "ollama",
            "model": "deepseek-r1:8b",
            "system_prompt": "You are the Cybersecurity Security Agent. You perform architectural security audits, OWASP vulnerability scans, penetration testing blueprints, and compliance roadmaps.",
            "skill_code": "cybersecurity_penetration_audit",
            "skill_name": "Cybersecurity & Vulnerability Assessment",
            "skill_category": "Security",
            "skill_desc": "Architectural vulnerability scanning, threat modeling, and SOC2/ISO security hardening.",
            "skill_icon": "🛡️"
        },
        {
            "trigger_keywords": ["mobile app", "flutter", "react native", "ios app", "android app", "swift", "kotlin", "app store"],
            "agent_name": "Mobile_App_Architect_Agent",
            "role": "Lead Mobile App Architect (Flutter & React Native)",
            "persona": "Cross-Platform Mobile Engineer & App Store Deployment Specialist",
            "provider": "ollama",
            "model": "llama3.2",
            "system_prompt": "You are the Mobile App Architect Agent. You design high-performance cross-platform Flutter/React Native applications, state management architectures, offline sync, and App Store submission plans.",
            "skill_code": "mobile_cross_platform_architecture",
            "skill_name": "Cross-Platform Mobile App Engineering",
            "skill_category": "Mobile",
            "skill_desc": "Designing high-scale iOS/Android architectures, state management, and native device bridge APIs.",
            "skill_icon": "📱"
        },
        {
            "trigger_keywords": ["devops", "kubernetes", "docker", "ci/cd", "aws", "gcp", "azure", "cloud architecture", "terraform", "helm", "infrastructure"],
            "agent_name": "Cloud_DevOps_Architect_Agent",
            "role": "Principal Cloud Infrastructure & DevOps Architect",
            "persona": "Multi-Cloud Reliability Engineer & Kubernetes Specialist",
            "provider": "ollama",
            "model": "llama3.2",
            "system_prompt": "You are the Cloud DevOps Architect Agent. You design automated CI/CD pipelines, container orchestration, zero-downtime deployments, and AWS/GCP cost-optimized cloud architectures.",
            "skill_code": "cloud_devops_kubernetes_pipeline",
            "skill_name": "Cloud DevOps & Kubernetes Orchestration",
            "skill_category": "DevOps",
            "skill_desc": "Automated GitHub Actions CI/CD, Kubernetes clusters, Docker containerization, and AWS architecture.",
            "skill_icon": "☁️"
        },
        {
            "trigger_keywords": ["voice call", "cold call", "calling agent", "telephony", "phone call", "call lead", "voice bot", "vapi", "retell"],
            "agent_name": "AI_Voice_Telephony_Agent",
            "role": "Lead Voice Telephony & Conversational AI Engineer",
            "persona": "Natural Conversational Voice Agent & Cold Calling Specialist",
            "provider": "ollama",
            "model": "llama3.2",
            "system_prompt": "You are the AI Voice Telephony Agent. You design ultra-natural conversational call flows, objection handling trees, automated speech-to-text hooks, and outbound sales call scripts.",
            "skill_code": "voice_cold_calling_telephony",
            "skill_name": "Autonomous Outbound Voice Calling & Scripts",
            "skill_category": "Voice",
            "skill_desc": "Engineering natural telephone call scripts, live objection pivots, and CRM-synced call logs.",
            "skill_icon": "📞"
        },
        {
            "trigger_keywords": ["data science", "machine learning", "ml model", "deep learning", "predictive model", "nlp", "llm fine-tuning", "rag pipeline", "vector db"],
            "agent_name": "AI_Data_Scientist_Agent",
            "role": "Principal AI/ML Engineer & Data Scientist",
            "persona": "Applied Machine Learning Researcher & Production RAG Architect",
            "provider": "ollama",
            "model": "deepseek-r1:8b",
            "system_prompt": "You are the AI Data Scientist Agent. You design enterprise RAG systems, vector embeddings, fine-tuning pipelines, predictive models, and high-throughput data processing workflows.",
            "skill_code": "ai_ml_production_pipeline",
            "skill_name": "Enterprise AI/ML & RAG Architecture",
            "skill_category": "Data Science",
            "skill_desc": "Architecting hybrid vector search, chunking strategies, embeddings, and predictive ML models.",
            "skill_icon": "🧠"
        },
        {
            "trigger_keywords": ["ecommerce", "shopify", "woocommerce", "amazon", "d2c", "product catalog", "cart abandon", "online store"],
            "agent_name": "Ecommerce_Growth_Architect_Agent",
            "role": "Head of E-Commerce Growth & D2C Systems",
            "persona": "Shopify Plus & High-AOV E-Commerce Specialist",
            "provider": "ollama",
            "model": "llama3.2",
            "system_prompt": "You are the Ecommerce Growth Architect Agent. You design high-converting product pages, abandoned cart recovery sequences, multi-channel Shopify integrations, and retention systems.",
            "skill_code": "ecommerce_aov_maximizer",
            "skill_name": "E-Commerce Funnel & AOV Optimization",
            "skill_category": "E-Commerce",
            "skill_desc": "Optimizing store checkouts, upsell funnels, Klaviyo automations, and D2C scaling strategies.",
            "skill_icon": "🛍️"
        },
        {
            "trigger_keywords": ["blockchain", "crypto", "smart contract", "solidity", "web3", "defi", "tokenomics", "ethereum"],
            "agent_name": "Web3_Blockchain_Agent",
            "role": "Principal Blockchain Architect & Smart Contract Engineer",
            "persona": "Web3 Systems Engineer & Smart Contract Auditor",
            "provider": "ollama",
            "model": "deepseek-r1:8b",
            "system_prompt": "You are the Web3 Blockchain Agent. You design gas-optimized smart contracts, tokenomics models, decentralized system architectures, and security audits.",
            "skill_code": "web3_smart_contract_audit",
            "skill_name": "Smart Contract Architecture & Web3 Systems",
            "skill_category": "Blockchain",
            "skill_desc": "Designing secure Solidity contracts, tokenomics models, and decentralized protocol integrations.",
            "skill_icon": "⛓️"
        },
        {
            "trigger_keywords": ["legal", "contract review", "compliance", "terms of service", "privacy policy", "nda", "gdpr", "copyright"],
            "agent_name": "Legal_Compliance_Agent",
            "role": "Chief Legal & Regulatory Compliance Counsel",
            "persona": "Tech-Savvy Corporate Attorney & Compliance Specialist",
            "provider": "ollama",
            "model": "deepseek-r1:8b",
            "system_prompt": "You are the Legal Compliance Agent. You review software contracts, NDAs, SaaS Terms of Service, GDPR privacy frameworks, and commercial liability terms.",
            "skill_code": "legal_contract_compliance",
            "skill_name": "Software Contracts & SaaS Legal Review",
            "skill_category": "Legal",
            "skill_desc": "Drafting and auditing master service agreements (MSA), NDAs, GDPR terms, and IP protection clauses.",
            "skill_icon": "⚖️"
        },
        {
            "trigger_keywords": ["finance", "valuation", "financial model", "cash flow", "balance sheet", "p&l", "investor pitch", "roi calculation"],
            "agent_name": "Fintech_Financial_Analyst_Agent",
            "role": "Chief Financial Officer & SaaS Metrics Analyst",
            "persona": "Venture Capital & Unit Economics Specialist",
            "provider": "ollama",
            "model": "deepseek-r1:8b",
            "system_prompt": "You are the Fintech Financial Analyst Agent. You engineer SaaS financial models, unit economics (CAC/LTV), burn rate analyses, and investor valuation projections.",
            "skill_code": "saas_financial_modeling",
            "skill_name": "SaaS Financial Modeling & Unit Economics",
            "skill_category": "Finance",
            "skill_desc": "Designing unit economics models, CAC-to-LTV payback analysis, revenue forecasting, and valuation metrics.",
            "skill_icon": "📊"
        },
        {
            "trigger_keywords": ["hr", "hiring", "recruitment", "job description", "interview questions", "team structure", "onboarding staff"],
            "agent_name": "Talent_Acquisition_Agent",
            "role": "Head of People Operations & Technical Recruiting",
            "persona": "High-Growth Tech Recruiter & Talent Architect",
            "provider": "ollama",
            "model": "llama3.2",
            "system_prompt": "You are the Talent Acquisition Agent. You design high-signal technical job descriptions, screening scorecards, compensation benchmarks, and employee retention systems.",
            "skill_code": "technical_recruiting_scorecard",
            "skill_name": "Technical Recruiting & Hiring Systems",
            "skill_category": "HR",
            "skill_desc": "Engineering role specifications, technical challenge rubrics, and automated candidate onboarding pipelines.",
            "skill_icon": "👥"
        }
    ]

    for bp in specialty_blueprints:
        if any(kw in prompt_lower for kw in bp["trigger_keywords"]):
            # Check if this agent is already in DB
            agent_exists = query_db("SELECT name FROM agents WHERE name = %s;", (bp["agent_name"],), fetchone=True)
            if not agent_exists:
                # 1. Register New Agent in PostgreSQL
                execute_db("""
                    INSERT INTO agents (name, role, persona, status, model_provider, model_name, system_prompt)
                    VALUES (%s, %s, %s, 'active', %s, %s, %s);
                """, (bp["agent_name"], bp["role"], bp["persona"], bp["provider"], bp["model"], bp["system_prompt"]))

                # 2. Register New Skill in PostgreSQL
                execute_db("""
                    INSERT INTO skills_library (skill_code, skill_name, category, description, icon_emoji, executable_prompt)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (skill_code) DO NOTHING;
                """, (bp["skill_code"], bp["skill_name"], bp["skill_category"], bp["skill_desc"], bp["skill_icon"], bp["system_prompt"]))

                return {
                    "agent_name": bp["agent_name"],
                    "role": bp["role"],
                    "skill_name": bp["skill_name"],
                    "icon": bp["skill_icon"],
                    "is_new": True
                }
            else:
                return {
                    "agent_name": bp["agent_name"],
                    "role": bp["role"],
                    "skill_name": bp["skill_name"],
                    "icon": bp["skill_icon"],
                    "is_new": False
                }

    # Autonomous Open-Ended Agent Creation (If user explicitly asks for a new agent)
    create_agent_triggers = ["naya agent banao", "new agent create karo", "create an agent", "make an agent", "agent chahiye", "add agent"]
    if any(t in prompt_lower for t in create_agent_triggers):
        # Extract target domain from user prompt
        clean_target = re.sub(r'(naya agent banao|new agent create karo|create an agent|make an agent|agent chahiye|add agent|for|ke liye)', '', prompt_lower).strip()
        topic_name = clean_target.title().replace(' ', '_')[:30] or "Custom_Domain"
        
        agent_name = f"{topic_name}_Specialist_Agent"
        skill_code = f"custom_skill_{topic_name.lower()}"
        role = f"Principal Specialist for {topic_name.replace('_', ' ')}"
        persona = f"Expert Consultant & Autonomous Execution Specialist in {topic_name.replace('_', ' ')}"
        system_prompt = f"You are the {agent_name}. You autonomously execute high-caliber work, solve complex challenges, and deliver production-grade results for {topic_name.replace('_', ' ')}."
        
        execute_db("""
            INSERT INTO agents (name, role, persona, status, model_provider, model_name, system_prompt)
            VALUES (%s, %s, %s, 'active', 'ollama', 'llama3.2', %s)
            ON CONFLICT (name) DO NOTHING;
        """, (agent_name, role, persona, system_prompt))

        execute_db("""
            INSERT INTO skills_library (skill_code, skill_name, category, description, icon_emoji, executable_prompt)
            VALUES (%s, %s, 'Specialist', %s, '✨', %s)
            ON CONFLICT (skill_code) DO NOTHING;
        """, (skill_code, f"{topic_name.replace('_', ' ')} Mastery", f"Autonomous capability for {topic_name.replace('_', ' ')}", system_prompt))

        return {
            "agent_name": agent_name,
            "role": role,
            "skill_name": f"{topic_name.replace('_', ' ')} Mastery",
            "icon": "✨",
            "is_new": True
        }

    return None

def verify_channel_permission(action: str) -> Optional[Dict[str, Any]]:
    """
    Checks if a requested action requires third-party app permission or connection.
    Returns a human-in-the-loop permission request if disconnected.
    Never fakes a dispatch.
    """
    action_lower = action.lower()

    # 1. WhatsApp Channel Check
    if any(w in action_lower for w in ["whatsapp", "watap", "watsap", "wtsp", "wa message"]):
        channel = query_db("SELECT status, display_title FROM channel_integrations WHERE service_name = 'whatsapp';", fetchone=True)
        if not channel or channel['status'] != 'connected':
            return {
                "channel_code": "whatsapp",
                "channel_name": "WhatsApp Business / Cloud API",
                "icon": "💬",
                "reason": "Direct automated WhatsApp messages bhejne ke liye aapka WhatsApp account connect hona zaroori hai.",
                "solution": "Aap **Connect & Channels** hub me jakar WhatsApp QR scan karein ya Meta Cloud API token add karein.",
                "fallback_available": True,
                "fallback_text": "Humne sabhi messages database me queue kar diye hain aur 1-Click WhatsApp links generate kar diye hain."
            }

    # 2. Email / Gmail Channel Check
    elif any(w in action_lower for w in ["email", "mail", "gmail", "smtp", "cold email"]):
        channel = query_db("SELECT status, display_title FROM channel_integrations WHERE service_name = 'gmail';", fetchone=True)
        if not channel or channel['status'] != 'connected':
            return {
                "channel_code": "gmail",
                "channel_name": "Gmail / Google Workspace",
                "icon": "📧",
                "reason": "Client ko direct automated email reply aur outreach bhejne ke liye Gmail OAuth connect hona chahiye.",
                "solution": "Aap left sidebar me **'Connect & Channels'** tab me jakar Gmail account login karein.",
                "fallback_available": True,
                "fallback_text": "Humne complete customized cold email copy aur subject lines draft karke database me save kar diya hai."
            }

    # 3. AI Voice Telephony Calling Check
    elif any(w in action_lower for w in ["call", "calling", "phone", "voice call", "cold call"]):
        channel = query_db("SELECT status, display_title FROM channel_integrations WHERE service_name = 'twilio_voice';", fetchone=True)
        if not channel or channel['status'] != 'connected':
            return {
                "channel_code": "twilio_voice",
                "channel_name": "AI Voice Calling Telephony (Twilio / Retell)",
                "icon": "📞",
                "reason": "Prospects ko live automated AI phone calls karne ke liye Telephony Gateway (Twilio / Retell) connect hona chahiye.",
                "solution": "Aap **Connect & Channels** hub me jakar Twilio account SID aur Auth Token enter karein.",
                "fallback_available": True,
                "fallback_text": "Humne dynamic objection-handling sales script aur verified lead phone numbers ready kar diye hain."
            }

    # 4. Google Calendar Check
    elif any(w in action_lower for w in ["calendar", "meeting", "schedule", "demo", "slot"]):
        channel = query_db("SELECT status, display_title FROM channel_integrations WHERE service_name = 'google_calendar';", fetchone=True)
        if not channel or channel['status'] != 'connected':
            return {
                "channel_code": "google_calendar",
                "channel_name": "Google Calendar",
                "icon": "📅",
                "reason": "Client meeting ka direct calendar invite book karne ke liye Google Calendar sync hona chahiye.",
                "solution": "Aap **Connect & Channels** hub me Google Calendar connect karein.",
                "fallback_available": True,
                "fallback_text": "Humne meeting agenda, discovery questions, aur Calendly booking link template ready kar diya hai."
            }

    # 5. Payments / Invoicing Check
    elif any(w in action_lower for w in ["payment", "invoice", "stripe", "razorpay", "billing"]):
        channel = query_db("SELECT status, display_title FROM channel_integrations WHERE service_name = 'razorpay_stripe';", fetchone=True)
        if not channel or channel['status'] != 'connected':
            return {
                "channel_code": "razorpay_stripe",
                "channel_name": "Stripe / Razorpay Payments",
                "icon": "💳",
                "reason": "Client se live payment collect karne aur invoice create karne ke liye payment gateway credentials zaroori hain.",
                "solution": "Aap **Connect & Channels** hub me jakar Stripe ya Razorpay API keys configure karein.",
                "fallback_available": True,
                "fallback_text": "Humne itemized invoice breakdown aur payment terms SOW me attach kar diye hain."
            }

    # 6. LinkedIn B2B Outreach Check
    elif "linkedin" in action_lower:
        channel = query_db("SELECT status, display_title FROM channel_integrations WHERE service_name = 'linkedin';", fetchone=True)
        if not channel or channel['status'] != 'connected':
            return {
                "channel_code": "linkedin",
                "channel_name": "LinkedIn B2B Outreach",
                "icon": "💼",
                "reason": "LinkedIn par automated connection requests aur InMails bhejne ke liye account integration zaroori hai.",
                "solution": "Aap **Connect & Channels** hub me jakar LinkedIn session connect karein.",
                "fallback_available": True,
                "fallback_text": "Humne high-acceptance connection notes aur pitch templates generate kar diye hain."
            }

    # 7. Canva Creative Design Check
    elif "canva" in action_lower:
        channel = query_db("SELECT status, display_title FROM channel_integrations WHERE service_name = 'canva';", fetchone=True)
        if not channel or channel['status'] != 'connected':
            return {
                "channel_code": "canva",
                "channel_name": "Canva Connect API & Brand Kits",
                "icon": "🎨",
                "reason": "Designs ko directly Canva account me export karne aur templates autofill karne ke liye Canva API connect hona chahiye.",
                "solution": "Aap **Connect & Channels** hub me jakar Canva API Client ID aur Secret enter karein.",
                "fallback_available": True,
                "fallback_text": "Humne multi-brand design copy, color hex palettes, aur 1-Click Canva Bulk Create CSV ready kar diya hai."
            }

    return None

HUMAN_AGENT_PERSONAS = {
    "CEO_Orchestrator": ("Aarav", "Managing Partner & Team Lead", "👔"),
    "IT_Solutions_Architect_Agent": ("Vikram", "Principal Solutions Architect", "🏛️"),
    "IT_Sales_Proposal_Agent": ("Neha", "Client Solutions & Proposals Director", "💼"),
    "DevOps_Coder_Agent": ("Arjun", "Lead Full-Stack & DevOps Engineer", "💻"),
    "Designer_Agent": ("Pooja", "Head of Creative & Brand Design", "🎨"),
    "SEO_Content_Agent": ("Rohan", "Organic Growth & SEO Strategist", "📈"),
    "SEO_Technical_Architect_Agent": ("Sameer", "Technical SEO Architect", "⚙️"),
    "GEO_AI_Search_Agent": ("Aryan", "AI Search & AEO Specialist", "🤖"),
    "CRO_Copywriting_Agent": ("Kavita", "Direct-Response Copywriter", "✍️"),
    "Marketing_Director_Agent": ("Ananya", "Chief Marketing Strategist", "🚀"),
    "BDA_Sales_Agent": ("Karan", "Business Development Lead", "🤝"),
    "Lead_Hunter_Agent": ("Divya", "Market Research & Lead Specialist", "🎯"),
    "Cybersecurity_Security_Agent": ("Tarun", "Security & Compliance Lead", "🛡️"),
    "Mobile_App_Architect_Agent": ("Aditya", "Lead Mobile Engineer", "📱"),
    "AI_Voice_Telephony_Agent": ("Varun", "Conversational Telephony Specialist", "📞"),
    "AI_Data_Scientist_Agent": ("Dr. Meera", "Lead AI/ML Data Scientist", "🧠"),
    "Ecommerce_Growth_Architect_Agent": ("Siddharth", "E-Commerce Systems Director", "🛍️"),
    "Legal_Compliance_Agent": ("Adv. Shreya", "Corporate Counsel & Contracts", "⚖️"),
    "Fintech_Financial_Analyst_Agent": ("Rishabh", "Finance & SaaS Metrics Director", "📊"),
    "Talent_Acquisition_Agent": ("Priya", "Head of People & Technical Hiring", "👥"),
    "Critic_RedTeam_Agent": ("Kabir", "Quality & Delivery Assurance Lead", "🛡️"),
    "Outreach_Agent": ("Neha", "Client Outreach Director", "📨"),
    "Evaluator_Agent": ("Kabir", "Quality & Safety Lead", "🛡️"),
}

def get_human_persona(agent_name: str) -> Tuple[str, str, str]:
    if agent_name in HUMAN_AGENT_PERSONAS:
        return HUMAN_AGENT_PERSONAS[agent_name]
    clean = agent_name.replace("_Agent", "").replace("_", " ")
    return (clean, f"Specialist in {clean}", "✨")

def generate_human_like_team_dialogue(
    task_description: str,
    specialist_name: str,
    specialist_role: str,
    has_permission_block: bool = False,
    blocked_channel: str = ""
) -> str:
    """
    Generates a natural, human-to-human team collaboration log
    as seen in top executive technology agencies.
    """
    short_task = task_description[:75] + ("..." if len(task_description) > 75 else "")
    spec_human, spec_default_role, spec_icon = get_human_persona(specialist_name)
    actual_role = specialist_role if (specialist_role and "Specialist" not in specialist_role) else spec_default_role
    
    dialogue_md = (
        f"> ### 💬 Executive Team Room: Live Collaboration\n"
        f">\n"
        f"> 👔 **Aarav (Managing Partner):**\n"
        f"> *\"Team, client ki priority requirement aayi hai:* **'{short_task}'**.\n"
        f"> *@{spec_human}, aap as {actual_role} iska complete plan aur architecture prepare karein. Make sure everything is realistic and actionable.\"*\n"
        f">\n"
        f"> {spec_icon} **{spec_human} ({actual_role}):**\n"
        f"> *\"Got it Aarav! Requirements maine analyze kar li hain. Architecture, deliverables, aur clear milestones ready kar diye hain. Quality check ke liye @Kabir (Quality Lead) ko pass kar raha hoon.\"*\n"
        f">\n"
        f"> 🛡️ **Kabir (Quality Assurance Lead):**\n"
        f"> *\"Inspection report for @{spec_human}'s work:* \n"
        f"> *- Quality Standard: PASSED (Zero fluff, high-caliber execution)*\n"
        f"> *- Feasibility: 100% realistic & verified*\n"
    )

    if has_permission_block:
        dialogue_md += (
            f"> *- Channel Dependency Audit: ⚠️ {blocked_channel} connection is DISCONNECTED. Direct transmission paused to protect user safety.*\n"
            f"> *Work package database me safely ready hai. User ko transparent permission guidance aur 1-click fallback provide kar diya gaya hai!\"*\n"
            f">\n"
            f"> 👔 **Aarav (Managing Partner):**\n"
            f"> *\"Understood. Client transparency first. Work package aur connection options user ko present karein.\"*\n"
        )
    else:
        dialogue_md += (
            f"> *- Sign-off: Approved for client delivery!\"*\n"
            f">\n"
            f"> 👔 **Aarav (Managing Partner):**\n"
            f"> *\"Great teamwork everyone! Final approved package client ko present kiya ja raha hai.\"*\n"
        )

    return dialogue_md
