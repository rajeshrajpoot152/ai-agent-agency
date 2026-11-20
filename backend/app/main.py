import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from backend.app.core.config import settings
from backend.app.api.routes_agency import router as agency_router
from backend.app.api.routes_leads import router as leads_router
from backend.app.api.routes_projects_hub import router as projects_hub_router
from backend.app.core.skill_intelligence import seed_master_skills_if_needed

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise LangGraph Multi-Agent Architecture for Autonomous Agency Operations."
)

@app.on_event("startup")
def on_startup():
    # Sync all master GPT & Gemini skills into local PostgreSQL skills_library
    seed_master_skills_if_needed()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(agency_router)
app.include_router(leads_router)
app.include_router(projects_hub_router)

# Accurate Paths to Frontend Pages
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
ASSETS_DIR = os.path.join(BASE_DIR, "frontend", "assets")
if os.path.exists(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

INDEX_FILE = os.path.join(BASE_DIR, "frontend", "index.html")
INQUIRY_FILE = os.path.join(BASE_DIR, "frontend", "inquiry.html")
PROPOSAL_FILE = os.path.join(BASE_DIR, "frontend", "proposal.html")
INVOICE_FILE = os.path.join(BASE_DIR, "frontend", "invoice.html")
PORTAL_FILE = os.path.join(BASE_DIR, "frontend", "portal.html")
ONBOARDING_FILE = os.path.join(BASE_DIR, "frontend", "onboarding.html")

@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>AI Agent Agency API Live</h1><p>Visit <a href='/docs'>/docs</a></p>")

@app.get("/inquiry", response_class=HTMLResponse)
def serve_inquiry():
    if os.path.exists(INQUIRY_FILE):
        with open(INQUIRY_FILE, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Inquiry Page Not Found</h1>", status_code=404)

@app.get("/proposal/{proposal_id}", response_class=HTMLResponse)
def serve_proposal(proposal_id: str):
    if os.path.exists(PROPOSAL_FILE):
        with open(PROPOSAL_FILE, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Proposal Page Not Found</h1>", status_code=404)

@app.get("/invoice/{invoice_id}", response_class=HTMLResponse)
def serve_invoice(invoice_id: str):
    if os.path.exists(INVOICE_FILE):
        with open(INVOICE_FILE, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Invoice Page Not Found</h1>", status_code=404)

@app.get("/portal/{portal_id}", response_class=HTMLResponse)
def serve_portal(portal_id: str):
    if os.path.exists(PORTAL_FILE):
        with open(PORTAL_FILE, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Client Portal Page Not Found</h1>", status_code=404)

@app.get("/onboarding/{portal_id}", response_class=HTMLResponse)
def serve_onboarding(portal_id: str):
    if os.path.exists(ONBOARDING_FILE):
        with open(ONBOARDING_FILE, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Onboarding Page Not Found</h1>", status_code=404)

@app.get("/health")
def health_check():
    return {"status": "healthy", "engine": "LangGraph"}
