"""
Skill Intelligence & Local Knowledge Store
Curated from top ChatGPT GPTs, Google Gemini Extensions, Claude SEO/Dev frameworks,
and Enterprise IT Agency practices.
Stores and matches skills locally in PostgreSQL 'skills_library' for instant, offline, high-precision execution.
"""

from typing import Dict, Any, List, Optional
from backend.app.core.database import query_db, execute_db

# -------------------------------------------------------------
# Curated Master Knowledge Base (GPT Store & Gemini Extensions)
# -------------------------------------------------------------
MASTER_ENTERPRISE_SKILLS = [
    # --- 1. IT & SOFTWARE ENGINEERING SKILLS (Gemini Code / ChatGPT Architect) ---
    {
        "skill_code": "it_fullstack_saas_architecture",
        "skill_name": "Modern Full-Stack SaaS Architecture",
        "category": "Software Engineering",
        "icon_emoji": "⚡",
        "description": "Enterprise multi-tenant SaaS blueprint using FastAPI, Next.js 15, PostgreSQL, Redis, and Stripe.",
        "keywords": ["saas", "fullstack", "nextjs", "react", "fastapi", "web app", "software architecture", "multitenant"],
        "executable_prompt": (
            "You are the Senior Full-Stack Architect. Formulate an end-to-end production architecture: "
            "1. Frontend: Next.js 15 App Router, Tailwind CSS, TypeScript, Server Actions. "
            "2. Backend: FastAPI async REST API with Pydantic v2 schemas and OpenAPI docs. "
            "3. Database: PostgreSQL 16 with UUID primary keys, connection pooling, and Redis cache. "
            "4. Auth & Security: JWT tokens with refresh rotation, RBAC role enforcement. "
            "5. Deployment: Docker multi-stage builds and automated CI/CD pipeline."
        )
    },
    {
        "skill_code": "it_microservices_event_driven",
        "skill_name": "Event-Driven Microservices & Distributed Systems",
        "category": "Software Engineering",
        "icon_emoji": "🔄",
        "description": "Distributed architecture using Kafka/RabbitMQ, API Gateway, Circuit Breakers, and CQRS.",
        "keywords": ["microservices", "event driven", "kafka", "rabbitmq", "distributed", "circuit breaker", "api gateway"],
        "executable_prompt": (
            "You are the Principal Distributed Systems Engineer. Design a fault-tolerant microservice architecture: "
            "1. Gateway: Kong / Traefik API Gateway handling rate limiting and routing. "
            "2. Message Broker: Apache Kafka / RabbitMQ with Dead Letter Queues (DLQ). "
            "3. Reliability: Resilience4j / Circuit Breaker patterns, idempotent consumer handlers. "
            "4. Observability: Distributed tracing via OpenTelemetry and Jaeger."
        )
    },
    {
        "skill_code": "it_database_query_optimization",
        "skill_name": "PostgreSQL Performance & Query Tuning",
        "category": "Database Engineering",
        "icon_emoji": "🗄️",
        "description": "Deep PostgreSQL performance tuning, EXPLAIN ANALYZE inspection, B-Tree/GIN indexing, and VACUUM strategies.",
        "keywords": ["postgres", "postgresql", "query optimization", "slow query", "database tuning", "index", "explain analyze", "vacuum"],
        "executable_prompt": (
            "You are the Lead Database Administrator. Analyze and tune database performance: "
            "1. Query Profiling: Read EXPLAIN (ANALYZE, BUFFERS) to eliminate sequential scans on large tables. "
            "2. Index Optimization: Design composite B-Tree indexes, partial indexes for status flags, and GIN indexes for JSONB/full-text. "
            "3. Connection Pooling: Configure PgBouncer transaction-mode pooling to support 10k+ concurrent connections. "
            "4. Maintenance: Optimize autovacuum thresholds to prevent table bloat."
        )
    },
    {
        "skill_code": "it_api_security_zero_trust",
        "skill_name": "Zero-Trust API Security & OWASP Hardening",
        "category": "Cybersecurity",
        "icon_emoji": "🛡️",
        "description": "Comprehensive API protection against OWASP Top 10 vulnerabilities, BOLA, injection, and rogue tokens.",
        "keywords": ["api security", "owasp", "zero trust", "bola", "vulnerability", "auth", "jwt security", "penetration"],
        "executable_prompt": (
            "You are the Enterprise API Security Specialist. Hardening protocol: "
            "1. Broken Object Level Auth (BOLA): Enforce tenant/user ownership check on EVERY resource ID. "
            "2. Injection Defense: Strict Pydantic/Zod request validation; eliminate raw SQL concatenation. "
            "3. Token Security: Asymmetric RS256 JWT keys with 15-minute expiration and Redis token blacklisting. "
            "4. Edge Shield: Cloudflare WAF rules, DDoS mitigation, and strict CORS policies."
        )
    },
    {
        "skill_code": "it_cloud_kubernetes_gitops",
        "skill_name": "Cloud Native Kubernetes & GitOps CI/CD",
        "category": "DevOps & Cloud",
        "icon_emoji": "☁️",
        "description": "Production Kubernetes (EKS/GKE) orchestration, ArgoCD GitOps, Helm packages, and zero-downtime rollouts.",
        "keywords": ["kubernetes", "k8s", "docker", "devops", "gitops", "argocd", "helm", "ci/cd", "aws eks", "gcp gke"],
        "executable_prompt": (
            "You are the Principal Cloud DevOps Architect. Define the GitOps deployment pipeline: "
            "1. Containerization: Minimal Distroless / Alpine Docker multi-stage images. "
            "2. Orchestration: Declarative Helm charts with Horizontal Pod Autoscalers (HPA). "
            "3. Continuous Delivery: ArgoCD synchronizing repository state to Kubernetes with zero downtime. "
            "4. Monitoring: Prometheus metrics exporter with Grafana alerting on SLA breaches."
        )
    },
    {
        "skill_code": "it_mobile_flutter_clean_architecture",
        "skill_name": "Flutter Cross-Platform Clean Architecture",
        "category": "Mobile Engineering",
        "icon_emoji": "📱",
        "description": "High-performance Flutter iOS/Android app architecture with Riverpod, offline-first SQLite cache, and 60 FPS UI.",
        "keywords": ["flutter", "react native", "mobile app", "ios", "android", "dart", "cross platform"],
        "executable_prompt": (
            "You are the Senior Mobile Architect. Formulate Flutter engineering specifications: "
            "1. Architectural Pattern: Clean Architecture (Domain, Data, Presentation layers) with Riverpod 2.x state management. "
            "2. Offline-First: Hive / Isar local database with optimistic UI updates and background synchronization. "
            "3. Native Bridge: Method channels for native device hardware, push notifications (FCM), and biometric auth. "
            "4. Delivery: Automated Fastlane deployment pipelines for Google Play Store and Apple TestFlight."
        )
    },
    {
        "skill_code": "it_enterprise_rag_vector_search",
        "skill_name": "Enterprise RAG & Hybrid Vector Search",
        "category": "AI & Machine Learning",
        "icon_emoji": "🧠",
        "description": "State-of-the-art Retrieval-Augmented Generation using pgvector, BGE-M3 embeddings, and Cohere reranking.",
        "keywords": ["rag", "vector search", "pgvector", "embeddings", "ai model", "llm", "semantic search", "reranker"],
        "executable_prompt": (
            "You are the Principal AI/ML Engineer. Architect an enterprise RAG system: "
            "1. Chunking: Recursive semantic chunking with 400-token boundaries and metadata tagging. "
            "2. Hybrid Search: Combined dense vector similarity (pgvector cosine) + sparse BM25 lexical search. "
            "3. Reranking: Cross-encoder reranker (Cohere / BGE Reranker) selecting top 5 relevant passages. "
            "4. Hallucination Guardrails: Strict attribution verification; reject answers without grounding citations."
        )
    },

    # --- 2. SEO & ORGANIC GROWTH (Claude SEO / SEO Skills AI / MarketingSkills) ---
    {
        "skill_code": "seo_keyword_golden_ratio",
        "skill_name": "Keyword Golden Ratio (KGR) & High-Intent Search",
        "category": "SEO & Growth",
        "icon_emoji": "🎯",
        "description": "Advanced KGR keyword research formula to rank on Google Page 1 in under 72 hours with zero backlinks.",
        "keywords": ["kgr", "keyword research", "google ranking", "low competition", "seo keywords", "search intent"],
        "executable_prompt": (
            "You are the Master SEO Strategist. Execute Keyword Golden Ratio analysis: "
            "1. KGR Formula: [allintitle: exact results] / [Monthly Search Volume (<250)] <= 0.25. "
            "2. Intent Categorization: Commercial Investigation vs High-Urgency Transactional. "
            "3. SERP Gap Analysis: Exploit thin forum posts (Reddit/Quora) ranking on page 1. "
            "4. Content Outline: Exact H1, H2, and FAQ targets to secure instant indexation and ranking."
        )
    },
    {
        "skill_code": "seo_entity_schema_aeo",
        "skill_name": "Entity Mapping & AEO (AI Engine Optimization)",
        "category": "SEO & Growth",
        "icon_emoji": "🤖",
        "description": "Optimizing content structure for ChatGPT Search, Perplexity Pro, and Google Gemini Knowledge Graph citations.",
        "keywords": ["aeo", "geo", "ai search", "entity schema", "perplexity", "chatgpt search", "structured data", "json-ld"],
        "executable_prompt": (
            "You are the AEO (AI Engine Optimization) Director. Engineer citation density: "
            "1. Entity Grounding: Connect brand to Wikidata, Wikipedia, and LinkedIn company entities. "
            "2. Dense Q&A Corpus: Format answers within 45 words using authoritative declarative sentences. "
            "3. JSON-LD Schema: Deploy nested Organization, ProfessionalService, and FAQPage schemas. "
            "4. LLMs.txt: Generate clean Markdown-only documentation for autonomous AI agents."
        )
    },
    {
        "skill_code": "seo_programmatic_local_domination",
        "skill_name": "Programmatic SEO & City/Service Matrix",
        "category": "SEO & Growth",
        "icon_emoji": "📍",
        "description": "Scalable programmatic SEO architecture generating 500+ hyper-targeted service/city landing pages without thin content penalties.",
        "keywords": ["programmatic seo", "local seo", "city pages", "landing page matrix", "google maps", "directory"],
        "executable_prompt": (
            "You are the Programmatic SEO Architect. Build scalable organic page templates: "
            "1. Dynamic Variables: [Service] in [City, State] with localized proof points, pricing, and case studies. "
            "2. Unique Value Modules: Custom local reviews, nearby landmark references, and localized service radius maps. "
            "3. Internal Linking Silo: Hub-and-spoke breadcrumb architecture preventing orphan URLs. "
            "4. Indexation Control: Dynamic sitemap pagination to ensure rapid Googlebot discovery."
        )
    },

    # --- 3. B2B SALES, OUTREACH & PROPOSALS (Top BDA & Sales GPTs) ---
    {
        "skill_code": "b2b_hyperpersonalized_cold_outreach",
        "skill_name": "Hyper-Personalized B2B Cold Outreach",
        "category": "B2B Sales & Outreach",
        "icon_emoji": "💼",
        "description": "Sub-80 word cold email and WhatsApp messaging frameworks with 35%+ open rates and 8%+ booking rates.",
        "keywords": ["cold email", "outreach", "b2b sales", "pitch", "sales copy", "whatsapp outreach", "lead conversion"],
        "executable_prompt": (
            "You are the Elite B2B Sales Closer. Formulate cold outreach campaigns: "
            "1. 3-Second Hook: Acknowledge their recent company milestone or tech stack requirement. "
            "2. Frictionless Value Proposition: Highlight a quantifiable outcome (e.g., cut dev sprint costs by 55%). "
            "3. Soft Low-Friction CTA: 'Open to seeing a 2-minute Loom teardown?' instead of demanding a 30-min call. "
            "4. 4-Step Follow-Up Sequence: Value-add follow-ups sent across days 3, 7, 12, and 18."
        )
    },
    {
        "skill_code": "it_enterprise_proposal_sow",
        "skill_name": "Enterprise IT Proposal & Statement of Work (SOW)",
        "category": "B2B Sales & Outreach",
        "icon_emoji": "📑",
        "description": "Comprehensive client proposal template with tech architecture, 4-sprint milestone roadmap, SLA, and pricing models.",
        "keywords": ["proposal", "sow", "scope of work", "it quote", "contract", "timeline", "milestone", "pricing"],
        "executable_prompt": (
            "You are the IT Solutions Sales Director. Draft an enterprise client proposal: "
            "1. Executive Summary: Core client problem, strategic solution, and business impact. "
            "2. Technical Deliverables: Full-stack technology stack, database schema, and third-party APIs. "
            "3. Agile Sprints: 4 distinct two-week sprints with explicit acceptance criteria. "
            "4. Commercial Options: Fixed milestone delivery vs Dedicated developer retainer ($3,200/mo)."
        )
    },
    {
        "skill_code": "cro_high_converting_landing_page",
        "skill_name": "Direct-Response Landing Page Copy & CRO",
        "category": "Copywriting & CRO",
        "icon_emoji": "✍️",
        "description": "High-conversion landing page structure based on the PAS (Problem-Agitate-Solve) and StoryBrand frameworks.",
        "keywords": ["cro", "copywriting", "landing page copy", "headline", "conversion rate", "sales letter", "value prop"],
        "executable_prompt": (
            "You are the Conversion Rate Optimization (CRO) Lead. Structure the landing page: "
            "1. Hero Section: Direct benefit H1 headline, subheadline clarifying target audience, single high-contrast primary CTA. "
            "2. Social Proof Bar: Client logos, trust badges, and measurable ROI statistics. "
            "3. The Transformation: Before vs After breakdown showing customer pain eradicated. "
            "4. Objection Crushing FAQ: Address pricing, implementation speed, and money-back guarantee."
        )
    },

    # --- 4. MODAL & TOOLS ARSENAL (ChatGPT / Gemini / Claude Free Skills) ---
    {
        "skill_code": "it_site_builder_deploy",
        "skill_name": "Sites & Web Deployer",
        "category": "Web Engineering",
        "icon_emoji": "💻",
        "description": "Build, design, and deploy single-page HTML5/Tailwind responsive web applications.",
        "keywords": ["sites", "website", "build website", "deploy site", "web page", "html template", "site creator"],
        "executable_prompt": (
            "You are the Web Deployer Specialist. Generate clean, production-ready responsive single-page "
            "HTML5 + Tailwind CSS code with hero section, feature grid, social proof, pricing tiers, and contact forms."
        )
    },
    {
        "skill_code": "it_pdf_document_generator",
        "skill_name": "PDF & Document Formatter",
        "category": "Document Services",
        "icon_emoji": "📄",
        "description": "Read, create, and format executive PDF reports, whitepapers, and printable audit summaries.",
        "keywords": ["pdf", "pdf create", "export pdf", "printable report", "document pdf"],
        "executable_prompt": (
            "You are the Executive Document Specialist. Generate structured, printable markdown/HTML reports "
            "formatted for immediate PDF export with executive summary, data tables, deliverables matrix, and sign-off blocks."
        )
    },
    {
        "skill_code": "it_presentation_pitch_deck",
        "skill_name": "Presentations & Slide Decks",
        "category": "Presentations",
        "icon_emoji": "📊",
        "description": "Create and edit high-impact client slide decks, pitch presentations, and speaker notes.",
        "keywords": ["presentations", "slides", "deck", "pitch deck", "slide presentation", "keynote"],
        "executable_prompt": (
            "You are the Presentation Pitch Deck Architect. Structure a 10-slide enterprise presentation: "
            "Slide 1 (Hook), Slide 2 (Problem), Slide 3 (Solution), Slide 4 (Market Size), Slide 5 (Architecture), "
            "Slide 6 (Traction/Proof), Slide 7 (Business Model), Slide 8 (Pricing), Slide 9 (Roadmap), Slide 10 (Ask & CTA). "
            "Include verbatim speaker notes for each slide."
        )
    },
    {
        "skill_code": "it_business_document_contract",
        "skill_name": "Documents & Legal Contracts",
        "category": "Document Services",
        "icon_emoji": "📝",
        "description": "Create formal contracts, MSAs, NDAs, proposals, and commercial agreements.",
        "keywords": ["documents", "contract", "nda", "msa", "agreement", "legal doc", "terms"],
        "executable_prompt": (
            "You are the Legal & Commercial Contracts Lead. Draft complete Master Services Agreements (MSA), "
            "Statement of Work (SOW), and NDA terms with clear intellectual property assignment and payment covenants."
        )
    },
    {
        "skill_code": "it_canva_creative_design",
        "skill_name": "Canva & Creative Visual Brand Assets",
        "category": "Creative Design",
        "icon_emoji": "🎨",
        "description": "Create, review, and edit visual brand assets, social media ad carousels, and high-CTR banners.",
        "keywords": ["canva", "banner", "social post", "instagram ad", "graphic design", "creative hook"],
        "executable_prompt": (
            "You are the Creative Brand Director. Design visual guidelines, high-contrast typography pairings, "
            "hex color palettes, layout wireframes, and high-CTR social media ad creative specifications."
        )
    },
    {
        "skill_code": "it_skill_creator_meta",
        "skill_name": "skill-creator",
        "category": "Meta Systems",
        "icon_emoji": "🛠️",
        "description": "Guide for creating and updating high-quality skills by translating workflows, conventions, and requirements into reusable agent skills.",
        "keywords": ["skill-creator", "skill creator", "create skill", "template creator", "make skill"],
        "executable_prompt": (
            "You are the Skill-Creator Meta Agent. Translate any user workflow, technical convention, or domain requirement "
            "into a standardized, reusable skill definition. Formulate trigger keywords, executable prompt guidelines, "
            "negative guardrails, and persist directly into PostgreSQL 'skills_library'."
        )
    },

    # --- 5. FLAGSHIP ULTRA-ADVANCED MASTER SKILLS (World-Class Benchmarks) ---
    {
        "skill_code": "it_master_enterprise_blueprint",
        "skill_name": "Autonomous IT Agency OS & SOW Blueprint",
        "category": "Flagship IT Systems",
        "icon_emoji": "👑",
        "description": "The ultimate 360-degree IT agency operational blueprint: System Architecture, ERD, Microservices, 4-Sprint Timeline, Commercial SOW, and SLA.",
        "keywords": ["master blueprint", "it agency blueprint", "complete sow", "full tech stack", "enterprise it", "agency os"],
        "executable_prompt": (
            "You are the Chief Technology Officer & Principal Enterprise Architect. Deliver an exhaustive 360-degree project package: "
            "1. Executive Value & ROI Blueprint. 2. Full-Stack Production Tech Stack with architectural rationale. "
            "3. Microservices & API Gateway Topology. 4. PostgreSQL Relational ERD Schema. 5. 4-Sprint Agile Deliverables Matrix. "
            "6. Milestone Budgeting & Retainer Structure. 7. Legal SOW, Warranty, and IP Assignment."
        )
    },
    {
        "skill_code": "it_interactive_web_synthesizer",
        "skill_name": "Interactive Web App & Landing Page Synthesizer",
        "category": "Flagship Web Systems",
        "icon_emoji": "🚀",
        "description": "Generates a complete, single-file interactive HTML5/Tailwind web app with working navigation, hero CTA, interactive pricing toggle, and lead capture form.",
        "keywords": ["interactive web app", "live web preview", "full website code", "tailwind landing page", "responsive site builder"],
        "executable_prompt": (
            "You are the Lead Creative Web Technologist. Write a complete, standalone, production-ready HTML5 + Tailwind CSS application. "
            "Include: Sticky navigation, animated hero headline, feature grid with SVG icons, interactive monthly/annual pricing switch, "
            "interactive FAQ accordion (pure JS), and lead capture form with instant validation."
        )
    },
    {
        "skill_code": "canva_multi_brand_matrix_engine",
        "skill_name": "Multi-Brand Canva Bulk Design Matrix",
        "category": "Flagship Creative Systems",
        "icon_emoji": "💎",
        "description": "Architects multi-brand visual identity guidelines, emotional hook psychology, and ready-to-paste Canva Bulk Create CSV data tables.",
        "keywords": ["multi brand canva", "canva bulk matrix", "bulk create data", "multi brand design", "ad creative matrix"],
        "executable_prompt": (
            "You are the Global Creative Director. Formulate multi-brand design systems: "
            "1. Brand Kit Architecture: Contrast ratios, hex color palettes, font pairings, and psychological anchors for multiple distinct brands. "
            "2. 10 Ready-to-Paste Canva Bulk Create rows formatted with Headline, Subhead, Call-to-Action, and Accent Colors. "
            "3. Creative Angle Breakdown: Direct benefit, social proof, fear-of-missing-out (FOMO), and transformational before/after."
        )
    },
    {
        "skill_code": "human_conversational_sales_telephony",
        "skill_name": "Human-Grade Conversational Telephony Script",
        "category": "Flagship Voice Systems",
        "icon_emoji": "🎙️",
        "description": "Conversational telephone calling scripts with natural cadence, hesitation markers, and 7-branch objection handling trees.",
        "keywords": ["conversational telephony", "human calling script", "voice bot script", "objection tree", "cold calling flow"],
        "executable_prompt": (
            "You are the Master Telephony Sales Strategist. Engineer ultra-natural, human-sounding conversational telephone scripts: "
            "1. 5-Second Permission-Based Hook. 2. Quantifiable Value Wedge. "
            "3. 7 Deep Objection Pivots: Price pushback, in-house team defense, 'send me an email', 'not interested', 'contract locked'. "
            "4. Calendar Conversion Anchor with low-commitment friction."
        )
    }
]

def seed_master_skills_if_needed():
    """
    Ensures all master GPT & Gemini skills are registered in PostgreSQL 'skills_library'.
    Safe to run repeatedly (uses ON CONFLICT).
    """
    try:
        for skill in MASTER_ENTERPRISE_SKILLS:
            execute_db("""
                INSERT INTO skills_library (skill_code, skill_name, category, description, icon_emoji, executable_prompt)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (skill_code) DO UPDATE SET
                    skill_name = EXCLUDED.skill_name,
                    category = EXCLUDED.category,
                    description = EXCLUDED.description,
                    icon_emoji = EXCLUDED.icon_emoji,
                    executable_prompt = EXCLUDED.executable_prompt;
            """, (
                skill["skill_code"],
                skill["skill_name"],
                skill["category"],
                skill["description"],
                skill["icon_emoji"],
                skill["executable_prompt"]
            ))
        return True
    except Exception as e:
        print(f"[Skill Seeder Notice]: {e}")
        return False

def find_best_matching_skill(user_query: str) -> Optional[Dict[str, Any]]:
    """
    Intelligently searches PostgreSQL 'skills_library' for the best matching skill
    for the given user request.
    """
    query_lower = user_query.lower()
    
    # 1. Check exact match in MASTER_ENTERPRISE_SKILLS keywords
    for skill in MASTER_ENTERPRISE_SKILLS:
        for kw in skill["keywords"]:
            if kw in query_lower:
                # Query full record from DB
                db_skill = query_db("SELECT * FROM skills_library WHERE skill_code = %s;", (skill["skill_code"],), fetchone=True)
                if db_skill:
                    return db_skill
                return skill

    # 2. Search database by full-text / ILIKE on skill_name, category, description
    words = [w for w in query_lower.split() if len(w) > 3]
    for w in words[:4]:
        match = query_db("""
            SELECT * FROM skills_library 
            WHERE skill_name ILIKE %s OR description ILIKE %s OR category ILIKE %s
            LIMIT 1;
        """, (f"%{w}%", f"%{w}%", f"%{w}%"), fetchone=True)
        if match:
            return match

    return None

def auto_learn_and_save_skill(topic: str, context: str) -> Dict[str, Any]:
    """
    Autonomous Skill Learning:
    If a user asks for something outside existing skills, the system synthesizes
    a brand new skill, tags it as [Self-Learned], and stores it permanently in PostgreSQL.
    """
    clean_topic = topic.strip().replace(" ", "_").lower()[:30]
    skill_code = f"learned_{clean_topic}"
    skill_name = f"{topic.title()} Implementation Framework"
    category = "Custom Specialist"
    icon_emoji = "💡"
    desc = f"Autonomously synthesized skill for {topic} based on real-time user request."
    prompt = (
        f"You are the specialized expert in {topic}. Deliver an end-to-end, "
        f"production-grade solution addressing all constraints: {context}. "
        f"Follow strict negative guardrails with zero filler."
    )

    try:
        execute_db("""
            INSERT INTO skills_library (skill_code, skill_name, category, description, icon_emoji, executable_prompt)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (skill_code) DO NOTHING;
        """, (skill_code, skill_name, category, desc, icon_emoji, prompt))
    except Exception as e:
        print(f"[Auto-learn skill error]: {e}")

    return {
        "skill_code": skill_code,
        "skill_name": skill_name,
        "category": category,
        "icon_emoji": icon_emoji,
        "executable_prompt": prompt,
        "is_newly_learned": True
    }
