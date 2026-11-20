import json
import uuid
import random
import re
import urllib.parse
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from backend.app.core.database import query_db, execute_db

router = APIRouter(prefix="/api/leads", tags=["Leads & CRM"])

class LeadCreateRequest(BaseModel):
    full_name: str
    business_name: str
    mobile_number: str
    industry: Optional[str] = "General"
    inquiry_source: Optional[str] = "Direct Lead"
    deal_value: Optional[str] = "₹25,000"
    notes: Optional[str] = "New prospective lead"
    follow_up_date: Optional[str] = None

class PublicInquiryRequest(BaseModel):
    full_name: str
    business_name: str
    mobile_number: str
    service_needed: Optional[str] = "Full Digital Growth Suite"
    budget_range: Optional[str] = "₹25,000 - ₹50,000/mo"
    city: Optional[str] = "India"
    project_details: Optional[str] = None

class LeadStatusUpdateRequest(BaseModel):
    lead_id: str
    status: str
    notes: Optional[str] = None
    follow_up_date: Optional[str] = None

class RescheduleFollowupRequest(BaseModel):
    lead_id: str
    days: int = 2
    notes: Optional[str] = None

class BulkOutreachRequest(BaseModel):
    raw_leads_text: str
    service_pitch_type: Optional[str] = "it_web_mobile_ai" # it_web_mobile_ai, automation_bots, full_marketing
    custom_agency_name: Optional[str] = "Apex AI & IT Solutions"

class ProposalGenerateRequest(BaseModel):
    lead_id: Optional[str] = None
    client_name: str
    business_name: str
    package_type: Optional[str] = "growth_accelerator" # starter, growth_accelerator, enterprise_omnichannel
    custom_budget: Optional[str] = None
    special_notes: Optional[str] = None

class InvoiceGenerateRequest(BaseModel):
    lead_id: Optional[str] = None
    client_name: str
    business_name: str
    service_title: Optional[str] = "Full-Stack Web, Mobile App & AI Automation Suite"
    amount: Optional[str] = "₹45,000"
    tax_percent: Optional[float] = 18.0
    due_days: Optional[int] = 7
    notes: Optional[str] = "Payment terms: 50% advance on milestone start, 50% upon deployment."

class InvoiceMarkPaidRequest(BaseModel):
    invoice_id: str

class AutoProvisionProjectRequest(BaseModel):
    lead_id: Optional[str] = None
    invoice_id: Optional[str] = None
    client_name: str
    business_name: str
    project_title: Optional[str] = "Full-Stack Web App, Mobile App & AI Automation Suite"
    project_tier: Optional[str] = "Growth Accelerator"
    target_days: Optional[int] = 21

class UpdateMilestoneRequest(BaseModel):
    project_id: str
    milestone_index: int
    new_status: str # completed, in_progress, pending
    new_progress: Optional[int] = None

class ClientFeedbackRequest(BaseModel):
    project_id: str
    client_name: Optional[str] = "Client"
    milestone_index: Optional[int] = 1
    feedback_type: str = "general" # 'approval', 'revision', 'general'
    message: str

class ClientAssetUploadRequest(BaseModel):
    project_id: str
    asset_name: str
    asset_type: Optional[str] = "logo" # 'logo', 'content_doc', 'design_reference', 'credentials', 'other'
    asset_url_or_note: str
    uploaded_by: Optional[str] = "Client"

class ClientOnboardingSubmitRequest(BaseModel):
    project_id: str
    brand_name: str
    tagline: Optional[str] = None
    target_audience: Optional[str] = None
    brand_colors: Optional[str] = "#4F46E5, #06B6D4"
    logo_url_or_note: Optional[str] = None
    competitor_websites: Optional[str] = None
    must_have_features: Optional[List[str]] = []
    integrations_needed: Optional[List[str]] = []
    tech_preferences: Optional[str] = "Next.js 14, Tailwind CSS, Python FastAPI, PostgreSQL"
    target_launch_date: Optional[str] = None
    special_requirements: Optional[str] = None

class CodeStarterRequest(BaseModel):
    project_id: str
    component_type: Optional[str] = "landing_page" # 'landing_page', 'ai_lead_bot', 'nextjs_architecture'

class AINegotiateRequest(BaseModel):
    lead_id: Optional[str] = None
    client_name: Optional[str] = "Partner"
    business_name: Optional[str] = "Client Brand"
    incoming_message: str
    objection_category: Optional[str] = "auto" # auto, budget, portfolio, timeline, call_booking

@router.get("/")
def get_leads(
    status: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 150
):
    query_parts = ["SELECT id, full_name, business_name, mobile_number, industry, status, notes, inquiry_source, deal_value, follow_up_date, last_contacted_at, created_at FROM outreach_leads WHERE 1=1"]
    params = []

    if status and status.lower() != 'all':
        query_parts.append("AND status = %s")
        params.append(status.lower())

    if search:
        search_term = f"%{search.strip()}%"
        query_parts.append("AND (full_name ILIKE %s OR business_name ILIKE %s OR mobile_number ILIKE %s OR industry ILIKE %s OR notes ILIKE %s)")
        params.extend([search_term, search_term, search_term, search_term, search_term])

    query_parts.append("ORDER BY follow_up_date ASC, created_at DESC LIMIT %s;")
    params.append(limit)

    full_query = " ".join(query_parts)
    leads = query_db(full_query, tuple(params))

    # Pipeline summary metrics
    stats = query_db("""
        SELECT 
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE status = 'deal_won') as won,
            COUNT(*) FILTER (WHERE status IN ('contacted', 'outreach_sent')) as contacted,
            COUNT(*) FILTER (WHERE status IN ('follow_up', 'in_discussion')) as in_discussion,
            COUNT(*) FILTER (WHERE status IN ('pending', 'new_inquiry', 'new')) as new_inquiries
        FROM outreach_leads;
    """, fetchone=True)

    return {
        "status": "success",
        "count": len(leads),
        "metrics": stats or {},
        "leads": leads
    }

@router.post("/")
def add_lead(lead: LeadCreateRequest):
    f_date = None
    if lead.follow_up_date:
        try:
            f_date = datetime.fromisoformat(lead.follow_up_date.replace("Z", "+00:00"))
        except Exception:
            f_date = datetime.now()
    else:
        f_date = datetime.now()

    execute_db("""
        INSERT INTO outreach_leads (full_name, business_name, mobile_number, whatsapp_number, industry, status, notes, inquiry_source, deal_value, follow_up_date)
        VALUES (%s, %s, %s, %s, %s, 'new_inquiry', %s, %s, %s, %s)
        ON CONFLICT (mobile_number) DO UPDATE
        SET full_name = EXCLUDED.full_name,
            business_name = EXCLUDED.business_name,
            industry = EXCLUDED.industry,
            notes = EXCLUDED.notes,
            deal_value = EXCLUDED.deal_value,
            follow_up_date = EXCLUDED.follow_up_date;
    """, (lead.full_name, lead.business_name, lead.mobile_number, lead.mobile_number, lead.industry, lead.notes, lead.inquiry_source or "Direct Lead", lead.deal_value or "₹25,000", f_date))
    
    return {"status": "success", "message": f"Lead / Client Inquiry for '{lead.business_name}' added successfully."}

@router.post("/update-status")
def update_lead_status(req: LeadStatusUpdateRequest):
    update_parts = ["status = %s", "last_contacted_at = CURRENT_TIMESTAMP"]
    params = [req.status]

    if req.notes is not None:
        update_parts.append("notes = %s")
        params.append(req.notes)

    if req.follow_up_date:
        try:
            f_date = datetime.fromisoformat(req.follow_up_date.replace("Z", "+00:00"))
            update_parts.append("follow_up_date = %s")
            params.append(f_date)
        except Exception:
            pass

    params.append(req.lead_id)
    sql = f"UPDATE outreach_leads SET {', '.join(update_parts)} WHERE id = %s;"
    execute_db(sql, tuple(params))

    return {"status": "success", "message": f"Lead status updated to '{req.status}' successfully."}

@router.post("/reschedule-followup")
def reschedule_followup(req: RescheduleFollowupRequest):
    new_date = datetime.now() + timedelta(days=req.days)
    notes_append = f" [Follow-up rescheduled +{req.days}d: {req.notes or 'Routine check-in'}]"
    execute_db("""
        UPDATE outreach_leads
        SET follow_up_date = %s,
            status = 'follow_up_due',
            notes = COALESCE(notes, '') || %s
        WHERE id = %s;
    """, (new_date, notes_append, req.lead_id))
    return {"status": "success", "message": f"Follow-up rescheduled to {new_date.strftime('%d %b %Y')}"}

@router.post("/public-inquiry")
def submit_public_inquiry(req: PublicInquiryRequest):
    # Public Lead Capture from /inquiry landing page
    notes_text = f"Inquiry via Agency Portal. Service: {req.service_needed} | City: {req.city}"
    if req.project_details:
        notes_text += f" | Details: {req.project_details}"

    follow_date = datetime.now()

    execute_db("""
        INSERT INTO outreach_leads (
            full_name, business_name, mobile_number, whatsapp_number, industry,
            status, notes, inquiry_source, deal_value, follow_up_date
        ) VALUES (%s, %s, %s, %s, %s, 'new_inquiry', %s, 'Public Landing Page', %s, %s)
        ON CONFLICT (mobile_number) DO UPDATE
        SET full_name = EXCLUDED.full_name,
            business_name = EXCLUDED.business_name,
            notes = EXCLUDED.notes,
            deal_value = EXCLUDED.deal_value,
            follow_up_date = EXCLUDED.follow_up_date;
    """, (
        req.full_name,
        req.business_name,
        req.mobile_number,
        req.mobile_number,
        req.service_needed,
        notes_text,
        req.budget_range or "₹25,000 - ₹50,000/mo",
        follow_date
    ))

    # Pre-filled WhatsApp response for the user/agency
    clean_phone = "".join(filter(str.isdigit, req.mobile_number))
    intro_message = f"Hello {req.full_name}! 👋 Thank you for reaching out regarding {req.business_name}. We reviewed your inquiry for {req.service_needed}. When is a good time for a quick 10-minute discovery call today?"
    import urllib.parse
    wa_url = f"https://wa.me/{clean_phone}?text={urllib.parse.quote(intro_message)}"

    return {
        "status": "success",
        "message": f"Inquiry for {req.business_name} received! Neha will follow up within 15 minutes.",
        "whatsapp_quick_chat_url": wa_url
    }

@router.post("/generate-proposal")
def generate_client_proposal(req: ProposalGenerateRequest):
    # Professional Agency Proposal Generator
    pkg = req.package_type or "growth_accelerator"
    
    if pkg == "starter":
        pkg_name = "Starter Launch Suite"
        amount = req.custom_budget or "₹15,000 / month"
        deliverables = [
            {"title": "24/7 AI WhatsApp Sales Receptionist", "desc": "Instant automated lead capture, FAQ answers & discovery call booking via WhatsApp."},
            {"title": "12 High-Converting Brand Creatives", "desc": "Custom graphic banners, offer promotions, and product showcases designed for Instagram & Facebook."},
            {"title": "Local SEO & Google Profile Boost", "desc": "Optimization of Google Business profile, citation building, and top-tier local keyword indexing."},
            {"title": "Bi-Weekly Performance Report", "desc": "Transparent growth metrics, lead volume breakdown, and engagement analytics."}
        ]
        scope_summary = f"Complete Starter Digital & AI Setup for {req.business_name} to establish market authority and capture inbound leads autonomously."
    elif pkg == "enterprise_omnichannel":
        pkg_name = "Enterprise Omni-Channel AI Engine"
        amount = req.custom_budget or "₹75,000 / month"
        deliverables = [
            {"title": "Full Autonomous AI Agent Operations", "desc": "Dedicated AI team: Lead Hunter, Closer Neha, Copywriter Kabir, SEO Specialist Arjun, and QA."},
            {"title": "Automated Outbound Voice & AI Telephony", "desc": "Smart voice calling for instant lead qualification, cold outreach, and customer appointment booking."},
            {"title": "Unlimited Multi-Brand Design & Ad Creatives", "desc": "Multi-format reels scripts, high-converting carousels, display ads, and promotional banners."},
            {"title": "Omnichannel Paid Media Funnel", "desc": "High-ROAS Meta Ads & Google Search Ads setup, testing, split-testing, and daily optimization."},
            {"title": "Executive Live CRM & Pipeline Sync", "desc": "Direct integration with CRM, instant WhatsApp/Telegram lead notifications, and real-time deal alerts."},
            {"title": "Dedicated Senior Agency Partner", "desc": "Direct weekly strategy sprints, competitor interception, and bespoke growth advisory."}
        ]
        scope_summary = f"Full-scale Enterprise AI transformation for {req.business_name} delivering aggressive customer acquisition, voice automation, and multi-channel scale."
    else: # growth_accelerator (Default)
        pkg_name = "Growth Accelerator Retainer"
        amount = req.custom_budget or "₹35,000 / month"
        deliverables = [
            {"title": "Targeted Meta & Google Lead Ads Funnel", "desc": "Custom audience targeting, high-converting ad copy, landing page optimization, and daily bid scaling."},
            {"title": "Smart AI Lead Qualification Bot", "desc": "Qualifies incoming inquiries, filters serious buyers, and books calls directly to your calendar."},
            {"title": "20 Branded Social Posts & Carousels", "desc": "Consistent, high-aesthetic brand storytelling with viral hooks, captions, and hashtag strategy."},
            {"title": "Technical SEO & Competitor Interception", "desc": "On-page keyword structuring, backlink architecture, and search visibility expansion."},
            {"title": "Dedicated Growth Strategist", "desc": "Weekly sprint reviews, transparent ROI dashboards, and on-demand campaign adjustments."}
        ]
        scope_summary = f"Comprehensive 360° Growth Accelerator for {req.business_name} designed to 3x qualified inquiries and establish brand dominance within 60 days."

    pricing_breakdown = [
        {"item": "Strategic Onboarding & Asset Setup", "rate": "₹5,000", "status": "Waived (100% OFF for First Month)"},
        {"item": f"{pkg_name} (30-Day Sprint)", "rate": amount, "status": "Active Retainer"},
        {"item": "Autonomous 24/7 AI System Hosting", "rate": "Included", "status": "Free"},
    ]

    valid_until = (datetime.now() + timedelta(days=14)).date()

    # Save to client_proposals table
    proposal_rows = query_db("""
        INSERT INTO client_proposals (
            lead_id, client_name, business_name, package_name, scope_summary,
            deliverables, pricing_breakdown, total_amount, valid_until, status
        ) VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, %s, 'active')
        RETURNING id, created_at;
    """, (
        req.lead_id if req.lead_id else None,
        req.client_name,
        req.business_name,
        pkg_name,
        scope_summary,
        json.dumps(deliverables),
        json.dumps(pricing_breakdown),
        amount,
        valid_until
    ))

    proposal_id = proposal_rows[0]['id'] if proposal_rows else str(uuid.uuid4())

    # If lead_id is present, update lead notes & status
    if req.lead_id:
        execute_db("""
            UPDATE outreach_leads
            SET status = 'in_discussion',
                deal_value = %s,
                notes = COALESCE(notes, '') || %s
            WHERE id = %s;
        """, (amount, f" [Proposal Generated: {pkg_name} ({amount}) on {datetime.now().strftime('%d %b')}]", req.lead_id))

    return {
        "status": "success",
        "proposal_id": proposal_id,
        "proposal_url": f"/proposal/{proposal_id}",
        "package_name": pkg_name,
        "total_amount": amount,
        "valid_until": str(valid_until),
        "deliverables": deliverables,
        "pricing_breakdown": pricing_breakdown,
        "message": f"Proposal for {req.business_name} created successfully!"
    }

@router.get("/proposals/{proposal_id}")
def get_proposal_by_id(proposal_id: str):
    proposal = query_db("""
        SELECT p.id, p.lead_id, p.client_name, p.business_name, p.package_name, p.scope_summary,
               p.deliverables, p.pricing_breakdown, p.total_amount, p.valid_until, p.status, p.created_at,
               l.mobile_number, l.industry
        FROM client_proposals p
        LEFT JOIN outreach_leads l ON p.lead_id = l.id
        WHERE p.id = %s;
    """, (proposal_id,), fetchone=True)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found.")
    return {"status": "success", "proposal": proposal}

@router.get("/proposals")
def list_proposals(limit: int = 20):
    proposals = query_db("""
        SELECT id, client_name, business_name, package_name, total_amount, valid_until, status, created_at
        FROM client_proposals
        ORDER BY created_at DESC LIMIT %s;
    """, (limit,))
    return {"status": "success", "count": len(proposals), "proposals": proposals}

@router.get("/logs")
def get_message_logs(limit: int = 20):
    logs = query_db("""
        SELECT m.id, l.full_name, l.business_name, l.mobile_number, m.message_content, m.sent_channel, m.sent_status, m.sent_at
        FROM outreach_message_logs m
        JOIN outreach_leads l ON m.lead_id = l.id
        ORDER BY m.sent_at DESC LIMIT %s;
    """, (limit,))
    return {"status": "success", "count": len(logs), "logs": logs}

# -------------------------------------------------------------
# BULK 100-CONTACT OUTREACH & FOLLOW-UP DISPATCHER
# -------------------------------------------------------------
@router.post("/bulk-import-outreach")
def bulk_import_outreach(req: BulkOutreachRequest):
    import re
    import urllib.parse

    lines = [line.strip() for line in req.raw_leads_text.strip().split("\n") if line.strip()]
    if not lines:
        raise HTTPException(status_code=400, detail="No phone numbers or contacts provided.")

    agency_name = req.custom_agency_name or "Apex AI & IT Solutions"
    pitch_type = req.service_pitch_type or "it_web_mobile_ai"

    processed_leads = []
    follow_date = datetime.now() + timedelta(days=2)

    for idx, raw_line in enumerate(lines):
        # 1. Parse name, business, and phone
        parts = [p.strip() for p in re.split(r'[,|\t;]', raw_line) if p.strip()]
        
        phone_match = re.search(r'(\+?91[\-\s]?)?[6789]\d{9}', raw_line.replace(" ", ""))
        if not phone_match:
            # Fallback: extract any 10-digit number
            digits = re.sub(r'\D', '', raw_line)
            if len(digits) >= 10:
                raw_phone = digits[-10:]
            else:
                continue
        else:
            raw_phone = phone_match.group(0).replace("+", "").replace("-", "")

        clean_phone = raw_phone
        if len(clean_phone) == 10:
            clean_phone = "91" + clean_phone
        elif not clean_phone.startswith("91") and len(clean_phone) > 10:
            clean_phone = "91" + clean_phone[-10:]

        formatted_display_phone = f"+{clean_phone}"

        # Extract name & business
        name = "Founder"
        business = "Business"
        if len(parts) >= 3:
            name = parts[0]
            business = parts[1]
        elif len(parts) == 2:
            if not any(char.isdigit() for char in parts[0]):
                name = parts[0]
            else:
                business = parts[1]
        elif len(parts) == 1:
            name = f"Prospect #{idx + 1}"
            business = "Commercial Brand"

        # 2. Craft tailored message
        if pitch_type == "automation_bots":
            msg_text = (
                f"Namaste {name}! 👋 Main {agency_name} se bol raha hoon.\n\n"
                f"Hum {business} jaise fast-growing businesses ke liye 24/7 AI WhatsApp Sales Receptionists aur CRM Workflow Automations build karte hain, jisse aapki zero inquiries miss hoti hain aur sales conversion 3x badh jata hai.\n\n"
                f"Kya hum aapko iska ek live working WhatsApp demo dikha sakte hain?"
            )
            industry_val = "Business Automation & AI Bots"
        elif pitch_type == "full_marketing":
            msg_text = (
                f"Namaste {name}! 👋 Main {agency_name} se bol raha hoon.\n\n"
                f"Hum {business} ke liye High-ROAS Performance Ads (Meta & Google), Social Media Brand Creatives, aur Organic SEO handle karte hain jisse qualified high-ticket clients milte hain.\n\n"
                f"Kya aap is mahine ke liye ek customized growth & acquisition strategy discuss karna chahenge?"
            )
            industry_val = "Digital Marketing & Branding"
        else: # it_web_mobile_ai (Default)
            msg_text = (
                f"Namaste {name}! 👋 Main {agency_name} se connect kar raha hoon.\n\n"
                f"Hum modern Web Platforms (Next.js), Mobile Applications (iOS/Android), Business Workflow Automations, aur Autonomous AI Agents develop karte hain jo aapke manual kaam ko autopilot par kar dete hain.\n\n"
                f"Kya aapke brand ({business}) ke liye hum ek short 5-minute portfolio & capability review schedule kar sakte hain?"
            )
            industry_val = "IT Services & AI Engineering"

        # 3. Save / Upsert to PostgreSQL outreach_leads
        lead_rows = query_db("""
            INSERT INTO outreach_leads (
                full_name, business_name, mobile_number, whatsapp_number, industry,
                status, notes, inquiry_source, deal_value, follow_up_date
            ) VALUES (%s, %s, %s, %s, %s, 'new_inquiry', %s, 'IT Services Bulk Blast', '₹35,000', %s)
            ON CONFLICT (mobile_number) DO UPDATE
            SET full_name = EXCLUDED.full_name,
                business_name = EXCLUDED.business_name,
                industry = EXCLUDED.industry,
                follow_up_date = EXCLUDED.follow_up_date,
                deal_value = EXCLUDED.deal_value
            RETURNING id, full_name, business_name, mobile_number, status, follow_up_date;
        """, (
            name,
            business,
            formatted_display_phone,
            formatted_display_phone,
            industry_val,
            f"Bulk outreach queue: {pitch_type} via {agency_name}",
            follow_date
        ))

        lead_id = lead_rows[0]['id'] if lead_rows else f"lead_{idx}"
        wa_url = f"https://wa.me/{clean_phone}?text={urllib.parse.quote(msg_text)}"

        processed_leads.append({
            "lead_id": str(lead_id),
            "name": name,
            "business": business,
            "phone": formatted_display_phone,
            "clean_phone": clean_phone,
            "message": msg_text,
            "whatsapp_url": wa_url,
            "follow_up_date": follow_date.strftime("%d %b %Y"),
            "status": "Ready to Send"
        })

    return {
        "status": "success",
        "total_imported": len(processed_leads),
        "service_pitch": pitch_type,
        "message": f"Successfully ingested {len(processed_leads)} contacts into PostgreSQL! Pitches and 1-Click WhatsApp links generated.",
        "leads": processed_leads
    }

# -------------------------------------------------------------
# 5. CLIENT TAX INVOICING & UPI ENGINE
# -------------------------------------------------------------
@router.post("/generate-invoice")
def generate_client_invoice(req: InvoiceGenerateRequest):
    # 1. Clean numeric amount
    raw_num = re.sub(r"[^\d]", "", req.amount or "45000")
    subtotal_num = int(raw_num) if raw_num else 45000
    tax_pct = req.tax_percent if req.tax_percent is not None else 18.0
    tax_num = int(round(subtotal_num * (tax_pct / 100.0)))
    total_num = subtotal_num + tax_num

    subtotal_fmt = f"₹{subtotal_num:,}"
    tax_fmt = f"₹{tax_num:,}"
    total_fmt = f"₹{total_num:,}"

    # 2. Unique invoice number
    inv_num = f"INV-2026-{random.randint(1000, 9999)}"
    issue_date = datetime.now().date()
    due_date = issue_date + timedelta(days=req.due_days or 7)

    # 3. Dynamic professional line items
    item1_amt = int(round(subtotal_num * 0.50))
    item2_amt = int(round(subtotal_num * 0.30))
    item3_amt = subtotal_num - item1_amt - item2_amt

    line_items = [
        {
            "description": f"Custom Engineering & UI/UX Architecture ({req.service_title})",
            "quantity": 1,
            "rate": f"₹{item1_amt:,}",
            "amount": f"₹{item1_amt:,}"
        },
        {
            "description": "Multi-Agent AI Automation Workflows, WhatsApp Bot & CRM Pipelines",
            "quantity": 1,
            "rate": f"₹{item2_amt:,}",
            "amount": f"₹{item2_amt:,}"
        },
        {
            "description": "Production Cloud Deployment, SSL Setup, CI/CD & 30-Day Technical Maintenance",
            "quantity": 1,
            "rate": f"₹{item3_amt:,}",
            "amount": f"₹{item3_amt:,}"
        }
    ]

    # 4. Generate UPI VPA payment link and QR URL
    upi_vpa = "agency.growth@upi"
    upi_string = f"upi://pay?pa={upi_vpa}&pn=Apex%20AI%20Agency&am={total_num}&cu=INR&tn={inv_num}"
    upi_qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={urllib.parse.quote(upi_string)}"

    # 5. Validate optional lead_id
    lead_uuid = None
    if req.lead_id:
        try:
            lead_uuid = str(uuid.UUID(req.lead_id))
        except (ValueError, TypeError):
            lead_uuid = None

    # 6. Save in PostgreSQL
    inv_rows = query_db("""
        INSERT INTO client_invoices (
            lead_id, client_name, business_name, invoice_number, issue_date, due_date,
            line_items, subtotal, tax_amount, total_amount, payment_status, upi_vpa, upi_qr_url
        ) VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, 'pending', %s, %s)
        RETURNING *;
    """, (
        lead_uuid,
        req.client_name,
        req.business_name,
        inv_num,
        issue_date,
        due_date,
        json.dumps(line_items),
        subtotal_fmt,
        tax_fmt,
        total_fmt,
        upi_vpa,
        upi_qr_url
    ))

    if not inv_rows:
        raise HTTPException(status_code=500, detail="Failed to persist invoice to PostgreSQL")

    invoice = inv_rows[0]

    # Update lead notes if lead_uuid exists
    if lead_uuid:
        execute_db("""
            UPDATE outreach_leads 
            SET notes = COALESCE(notes, '') || E'\n[Tax Invoice Generated: ' || %s || ' Total: ' || %s || ']'
            WHERE id = %s;
        """, (inv_num, total_fmt, lead_uuid))

    return {
        "status": "success",
        "invoice_id": str(invoice["id"]),
        "invoice_number": invoice["invoice_number"],
        "client_name": invoice["client_name"],
        "business_name": invoice["business_name"],
        "total_amount": invoice["total_amount"],
        "invoice_url": f"/invoice/{invoice['id']}",
        "message": f"Professional Tax Invoice {inv_num} generated with live UPI QR code!"
    }

@router.get("/invoices")
def get_all_invoices(limit: int = 50):
    rows = query_db("""
        SELECT i.*, l.mobile_number, l.whatsapp_number
        FROM client_invoices i
        LEFT JOIN outreach_leads l ON i.lead_id = l.id
        ORDER BY i.created_at DESC
        LIMIT %s;
    """, (limit,))

    for r in rows:
        if r.get("issue_date"):
            r["issue_date_str"] = r["issue_date"].strftime("%d %b %Y")
        if r.get("due_date"):
            r["due_date_str"] = r["due_date"].strftime("%d %b %Y")
        if isinstance(r.get("line_items"), str):
            try:
                r["line_items"] = json.loads(r["line_items"])
            except Exception:
                pass

    return {"status": "success", "count": len(rows), "invoices": rows}

@router.get("/invoices/{invoice_id}")
def get_invoice_details(invoice_id: str):
    is_uuid = False
    try:
        uuid.UUID(invoice_id)
        is_uuid = True
    except (ValueError, TypeError):
        is_uuid = False

    if is_uuid:
        rows = query_db("""
            SELECT i.*, l.mobile_number, l.whatsapp_number, l.industry
            FROM client_invoices i
            LEFT JOIN outreach_leads l ON i.lead_id = l.id
            WHERE i.id::text = %s;
        """, (invoice_id,))
    else:
        rows = query_db("""
            SELECT i.*, l.mobile_number, l.whatsapp_number, l.industry
            FROM client_invoices i
            LEFT JOIN outreach_leads l ON i.lead_id = l.id
            WHERE i.invoice_number = %s;
        """, (invoice_id,))

    if not rows:
        raise HTTPException(status_code=404, detail="Invoice record not found.")

    invoice = rows[0]
    if invoice.get("issue_date"):
        invoice["issue_date_str"] = invoice["issue_date"].strftime("%d %b %Y")
    if invoice.get("due_date"):
        invoice["due_date_str"] = invoice["due_date"].strftime("%d %b %Y")
    if isinstance(invoice.get("line_items"), str):
        try:
            invoice["line_items"] = json.loads(invoice["line_items"])
        except Exception:
            pass

    return {"status": "success", "invoice": invoice}

@router.post("/invoices/mark-paid")
def mark_invoice_as_paid(req: InvoiceMarkPaidRequest):
    is_uuid = False
    try:
        uuid.UUID(req.invoice_id)
        is_uuid = True
    except (ValueError, TypeError):
        is_uuid = False

    if is_uuid:
        row = query_db("""
            UPDATE client_invoices
            SET payment_status = 'paid'
            WHERE id::text = %s
            RETURNING id, lead_id, invoice_number, total_amount, client_name;
        """, (req.invoice_id,), fetchone=True)
    else:
        row = query_db("""
            UPDATE client_invoices
            SET payment_status = 'paid'
            WHERE invoice_number = %s
            RETURNING id, lead_id, invoice_number, total_amount, client_name;
        """, (req.invoice_id,), fetchone=True)

    if not row:
        raise HTTPException(status_code=404, detail="Invoice not found.")

    # If linked to a lead, update lead status to deal_won
    if row.get("lead_id"):
        execute_db("""
            UPDATE outreach_leads 
            SET status = 'deal_won',
                notes = COALESCE(notes, '') || E'\n[Payment Confirmed: Invoice ' || %s || ' Paid]'
            WHERE id = %s;
        """, (row["invoice_number"], row["lead_id"]))

    # 100% Autonomous Provisioning: Create live Client Project Milestone Portal
    existing_proj = query_db("SELECT id FROM client_projects WHERE invoice_id::text = %s;", (str(row['id']),), fetchone=True)
    portal_url = None
    if not existing_proj:
        new_proj = provision_project_internal(
            client_name=row['client_name'],
            business_name=row.get('business_name') or 'Client Partner',
            lead_id=str(row['lead_id']) if row.get('lead_id') else None,
            invoice_id=str(row['id'])
        )
        if new_proj:
            portal_url = f"/portal/{new_proj['id']}"
    else:
        portal_url = f"/portal/{existing_proj['id']}"

    return {
        "status": "success",
        "message": f"Invoice {row['invoice_number']} marked as PAID! Lead converted to 'deal_won' and Client Project Portal auto-provisioned!",
        "invoice": row,
        "portal_url": portal_url
    }

# -------------------------------------------------------------
# 6. AUTONOMOUS CLIENT PROJECT PORTAL & MILESTONE TRACKER
# -------------------------------------------------------------
def provision_project_internal(
    client_name: str,
    business_name: str,
    lead_id: Optional[str] = None,
    invoice_id: Optional[str] = None,
    project_title: Optional[str] = None,
    project_tier: Optional[str] = "Growth Accelerator",
    target_days: int = 21
):
    title = project_title or "Full-Stack Web App, Mobile App & AI Automation Suite"
    slug = re.sub(r"[^a-z0-9]", "", business_name.lower()) or "client"
    staging_url = f"https://preview.apexsolutions.ai/{slug}"
    repo_url = f"https://github.com/apex-ai-agency/{slug}-platform"
    launch_date = datetime.now().date() + timedelta(days=target_days)

    milestones = [
        {
            "id": 1,
            "title": "System Architecture & UI/UX Wireframing",
            "assigned_to": "Kabir - Creative Director",
            "status": "completed",
            "progress": 100,
            "deliverable": "Figma Prototypes, Design Tokens & Database ER Diagram",
            "completion_date": datetime.now().strftime("%d %b %Y")
        },
        {
            "id": 2,
            "title": "Next.js 14 Web Platform & High-Converting UI Engineering",
            "assigned_to": "Arjun - Lead Tech Architect",
            "status": "in_progress",
            "progress": 65,
            "deliverable": "Production Next.js Codebase, Tailwind Responsive Layout & APIs",
            "completion_date": (datetime.now() + timedelta(days=5)).strftime("%d %b %Y")
        },
        {
            "id": 3,
            "title": "Cross-Platform Mobile Application (iOS & Android)",
            "assigned_to": "DevOps & Mobile Squad",
            "status": "pending",
            "progress": 0,
            "deliverable": "React Native / Flutter App Build & Push Notification Setup",
            "completion_date": (datetime.now() + timedelta(days=12)).strftime("%d %b %Y")
        },
        {
            "id": 4,
            "title": "24/7 Autonomous AI Agent & WhatsApp Lead Bot Integration",
            "assigned_to": "Neha - Autonomous Lead Specialist",
            "status": "pending",
            "progress": 0,
            "deliverable": "LangGraph Multi-Agent Workflows & Direct WhatsApp Gateway",
            "completion_date": (datetime.now() + timedelta(days=17)).strftime("%d %b %Y")
        },
        {
            "id": 5,
            "title": "Production Cloud Deployment, SSL, CI/CD & Final Handover",
            "assigned_to": "Arjun - Tech Architect",
            "status": "pending",
            "progress": 0,
            "deliverable": "Live Custom Domain Mapping, High-Availability Cloud Infra & Documentation",
            "completion_date": launch_date.strftime("%d %b %Y")
        }
    ]

    l_uuid = None
    if lead_id:
        try:
            l_uuid = str(uuid.UUID(lead_id))
        except Exception:
            l_uuid = None

    i_uuid = None
    if invoice_id:
        try:
            i_uuid = str(uuid.UUID(invoice_id))
        except Exception:
            i_uuid = None

    rows = query_db("""
        INSERT INTO client_projects (
            lead_id, invoice_id, client_name, business_name, project_title, project_tier,
            progress_percent, status, staging_url, repository_url, milestones, target_launch_date
        ) VALUES (%s, %s, %s, %s, %s, %s, 35, 'in_progress', %s, %s, %s::jsonb, %s)
        RETURNING *;
    """, (
        l_uuid,
        i_uuid,
        client_name,
        business_name,
        title,
        project_tier,
        staging_url,
        repo_url,
        json.dumps(milestones),
        launch_date
    ))

    return rows[0] if rows else None

@router.post("/auto-provision-project")
def auto_provision_project_route(req: AutoProvisionProjectRequest):
    proj = provision_project_internal(
        client_name=req.client_name,
        business_name=req.business_name,
        lead_id=req.lead_id,
        invoice_id=req.invoice_id,
        project_title=req.project_title,
        project_tier=req.project_tier,
        target_days=req.target_days or 21
    )
    if not proj:
        raise HTTPException(status_code=500, detail="Failed to provision client project")

    return {
        "status": "success",
        "project_id": str(proj["id"]),
        "client_name": proj["client_name"],
        "business_name": proj["business_name"],
        "portal_url": f"/portal/{proj['id']}",
        "message": f"Live Milestone Portal auto-provisioned for {proj['business_name']}!"
    }

@router.get("/projects")
def get_all_projects(limit: int = 50):
    rows = query_db("""
        SELECT p.*, l.mobile_number, l.whatsapp_number, l.industry, i.invoice_number, i.total_amount
        FROM client_projects p
        LEFT JOIN outreach_leads l ON p.lead_id = l.id
        LEFT JOIN client_invoices i ON p.invoice_id = i.id
        ORDER BY p.created_at DESC
        LIMIT %s;
    """, (limit,))

    for r in rows:
        if r.get("target_launch_date"):
            r["target_launch_date_str"] = r["target_launch_date"].strftime("%d %b %Y")
        if isinstance(r.get("milestones"), str):
            try:
                r["milestones"] = json.loads(r["milestones"])
            except Exception:
                pass

    return {"status": "success", "count": len(rows), "projects": rows}

@router.get("/projects/{project_id}")
def get_project_details(project_id: str):
    rows = query_db("""
        SELECT p.*, l.mobile_number, l.whatsapp_number, l.industry, i.invoice_number, i.total_amount, i.payment_status
        FROM client_projects p
        LEFT JOIN outreach_leads l ON p.lead_id = l.id
        LEFT JOIN client_invoices i ON p.invoice_id = i.id
        WHERE p.id::text = %s;
    """, (project_id,))

    if not rows:
        raise HTTPException(status_code=404, detail="Project record not found.")

    proj = rows[0]
    if proj.get("target_launch_date"):
        proj["target_launch_date_str"] = proj["target_launch_date"].strftime("%d %b %Y")
    if isinstance(proj.get("milestones"), str):
        try:
            proj["milestones"] = json.loads(proj["milestones"])
        except Exception:
            pass

    if isinstance(proj.get("client_feedback"), str):
        try:
            proj["client_feedback"] = json.loads(proj["client_feedback"])
        except Exception:
            proj["client_feedback"] = []
    elif not proj.get("client_feedback"):
        proj["client_feedback"] = []

    if isinstance(proj.get("client_assets"), str):
        try:
            proj["client_assets"] = json.loads(proj["client_assets"])
        except Exception:
            proj["client_assets"] = []
    elif not proj.get("client_assets"):
        proj["client_assets"] = []

    if isinstance(proj.get("onboarding_data"), str):
        try:
            proj["onboarding_data"] = json.loads(proj["onboarding_data"])
        except Exception:
            proj["onboarding_data"] = {}
    elif not proj.get("onboarding_data"):
        proj["onboarding_data"] = {}

    if isinstance(proj.get("starter_code"), str):
        try:
            proj["starter_code"] = json.loads(proj["starter_code"])
        except Exception:
            proj["starter_code"] = {}
    elif not proj.get("starter_code"):
        proj["starter_code"] = {}

    return {"status": "success", "project": proj}

@router.post("/projects/update-milestone")
def update_project_milestone(req: UpdateMilestoneRequest):
    proj_rows = query_db("SELECT * FROM client_projects WHERE id::text = %s;", (req.project_id,))
    if not proj_rows:
        raise HTTPException(status_code=404, detail="Project not found.")

    proj = proj_rows[0]
    milestones = proj.get("milestones") or []
    if isinstance(milestones, str):
        milestones = json.loads(milestones)

    target_idx = req.milestone_index - 1
    if 0 <= target_idx < len(milestones):
        milestones[target_idx]["status"] = req.new_status
        if req.new_status == "completed":
            milestones[target_idx]["progress"] = 100
        elif req.new_progress is not None:
            milestones[target_idx]["progress"] = req.new_progress

    completed_count = sum(1 for m in milestones if m.get("status") == "completed")
    new_overall_pct = int(round((completed_count / len(milestones)) * 100)) if milestones else 0

    new_status = "completed" if new_overall_pct == 100 else "in_progress"

    execute_db("""
        UPDATE client_projects
        SET milestones = %s::jsonb,
            progress_percent = %s,
            status = %s
        WHERE id::text = %s;
    """, (json.dumps(milestones), new_overall_pct, new_status, req.project_id))

    return {
        "status": "success",
        "progress_percent": new_overall_pct,
        "project_status": new_status,
        "message": f"Milestone {req.milestone_index} updated to {req.new_status}. Overall progress: {new_overall_pct}%"
    }

@router.post("/projects/submit-feedback")
def submit_project_feedback(req: ClientFeedbackRequest):
    proj_rows = query_db("SELECT * FROM client_projects WHERE id::text = %s;", (req.project_id,))
    if not proj_rows:
        raise HTTPException(status_code=404, detail="Project not found.")

    proj = proj_rows[0]
    feedbacks = proj.get("client_feedback") or []
    if isinstance(feedbacks, str):
        try:
            feedbacks = json.loads(feedbacks)
        except Exception:
            feedbacks = []

    entry = {
        "id": str(uuid.uuid4())[:8],
        "client_name": req.client_name or proj.get("client_name") or "Client",
        "milestone_index": req.milestone_index,
        "feedback_type": req.feedback_type,
        "message": req.message.strip(),
        "created_at": datetime.now().strftime("%d %b %Y, %I:%M %p")
    }
    feedbacks.insert(0, entry)

    execute_db("""
        UPDATE client_projects
        SET client_feedback = %s::jsonb
        WHERE id::text = %s;
    """, (json.dumps(feedbacks), req.project_id))

    # Push live notification to agency team watercooler
    try:
        from backend.app.api.routes_agency import WATERCOOLER_FEED
        alert_emoji = "✅" if req.feedback_type == "approval" else ("⚠️" if req.feedback_type == "revision" else "💬")
        WATERCOOLER_FEED.insert(0, {
            "id": f"msg_fb_{len(WATERCOOLER_FEED) + 1}",
            "author": "Client Success Bot",
            "role": "Autonomous PM",
            "avatar": alert_emoji,
            "time": "Just now",
            "message": f"CLIENT FEEDBACK on Milestone {req.milestone_index} for {proj.get('business_name')} ({req.feedback_type.upper()}): \"{req.message}\" - Assigned to Engineering Squad!"
        })
    except Exception:
        pass

    return {
        "status": "success",
        "feedback_entry": entry,
        "total_feedbacks": len(feedbacks),
        "message": f"Feedback received successfully for Phase {req.milestone_index}."
    }

@router.post("/projects/upload-asset")
def upload_project_asset(req: ClientAssetUploadRequest):
    proj_rows = query_db("SELECT * FROM client_projects WHERE id::text = %s;", (req.project_id,))
    if not proj_rows:
        raise HTTPException(status_code=404, detail="Project not found.")

    proj = proj_rows[0]
    assets = proj.get("client_assets") or []
    if isinstance(assets, str):
        try:
            assets = json.loads(assets)
        except Exception:
            assets = []

    asset_entry = {
        "id": str(uuid.uuid4())[:8],
        "asset_name": req.asset_name.strip(),
        "asset_type": req.asset_type or "logo",
        "asset_url_or_note": req.asset_url_or_note.strip(),
        "uploaded_by": req.uploaded_by or "Client",
        "created_at": datetime.now().strftime("%d %b %Y, %I:%M %p")
    }
    assets.insert(0, asset_entry)

    execute_db("""
        UPDATE client_projects
        SET client_assets = %s::jsonb
        WHERE id::text = %s;
    """, (json.dumps(assets), req.project_id))

    # Push live notification to agency team watercooler
    try:
        from backend.app.api.routes_agency import WATERCOOLER_FEED
        WATERCOOLER_FEED.insert(0, {
            "id": f"msg_asset_{len(WATERCOOLER_FEED) + 1}",
            "author": "Asset Ingestion Bot",
            "role": "DevOps & Storage",
            "avatar": "📂",
            "time": "Just now",
            "message": f"NEW ASSET ATTACHED for {proj.get('business_name')}: \"{req.asset_name}\" ({req.asset_type}) by {req.uploaded_by}."
        })
    except Exception:
        pass

    return {
        "status": "success",
        "asset_entry": asset_entry,
        "total_assets": len(assets),
        "message": f"Asset '{req.asset_name}' uploaded successfully."
    }

# -------------------------------------------------------------
# 7. AUTONOMOUS AI SALES NEGOTIATOR & OBJECTION HANDLER
# -------------------------------------------------------------
@router.post("/ai-negotiate")
def ai_negotiate_reply(req: AINegotiateRequest):
    incoming = req.incoming_message.strip().lower()
    c_name = req.client_name or "Partner"
    b_name = req.business_name or "Client Brand"

    cat = req.objection_category or "auto"
    if cat == "auto":
        if any(w in incoming for w in ["budget", "price", "kam", "discount", "mehenga", "cost", "paisa", "rate"]):
            cat = "budget"
        elif any(w in incoming for w in ["portfolio", "previous", "sample", "pehle", "kaam dikhao", "case study", "link"]):
            cat = "portfolio"
        elif any(w in incoming for w in ["din", "time", "kab tak", "timeline", "duration", "fast", "jaldi"]):
            cat = "timeline"
        elif any(w in incoming for w in ["call", "meet", "baat", "discuss", "phone", "zoom", "google meet"]):
            cat = "call_booking"
        else:
            cat = "value_proposition"

    if cat == "budget":
        tactic = "Milestone Split & ROI Justification"
        reply = (
            f"Namaste {c_name}! 👋 Main samajh sakta hoon ki budget important factor hai.\n\n"
            f"Isliye hum aapke liye upfront pura burden nahi rakhte — hum direct *50% Milestone Advance* aur baki *50% Final Deployment* par split provide karte hain.\n\n"
            f"Plus, {b_name} ke liye hum jo 24/7 AI WhatsApp bot deploy karenge, wo aapki organic leads ka drop-off 0% kar dega, jisse aapka ROI pehle 30 din me recover ho jata hai.\n\n"
            f"Kya hum 5-minute call par aapke budget ke according ek customized sprint plan finalize karein?"
        )
    elif cat == "portfolio":
        tactic = "Live Multi-Brand Case Studies Showcase"
        reply = (
            f"Zaroor {c_name}! 🚀 Ye rahe hamare live deployed tech ecosystems:\n\n"
            f"1. *QuickApp Studio* (Next.js SaaS Platform - 50,000+ Active Users)\n"
            f"2. *AutoBot AI* (24/7 WhatsApp & CRM Autonomous Lead Closing Engine - 3.2x Conversion Boost)\n"
            f"3. *FitLife Elite & Artisan Oven* (Complete E-commerce, Booking & Automation Funnels)\n\n"
            f"Aapke {b_name} ke liye bhi hum same high-performance modern tech stack deploy karenge. Kya aapka project next week start karna chahenge?"
        )
    elif cat == "timeline":
        tactic = "Agile 14-to-21 Day Rapid Deployment Guarantee"
        reply = (
            f"Namaste {c_name}! Hum slow agency model par kaam nahi karte ⚡\n\n"
            f"Hamari dedicated AI specialist team aapke {b_name} project ko *14 se 21 din* ke rapid sprint me complete deliver karti hai:\n"
            f"• Day 1-4: UI/UX Wireframe & Figma Prototype approval\n"
            f"• Day 5-14: Full-Stack Web & Mobile App Engineering\n"
            f"• Day 15-21: AI Agent Workflows, WhatsApp bot integration & Cloud Live Launch\n\n"
            f"Aapko live staging link milegi jahan aap daily progress track kar sakte hain."
        )
    elif cat == "call_booking":
        tactic = "Instant High-Priority Google Meet Scheduling"
        reply = (
            f"Namaste {c_name}! Bilkul, hum aapke convenience par call arrange kar sakte hain 🤝\n\n"
            f"Kya *aaj shaam 4:00 PM* ya *kal subah 11:30 AM* aapke liye comfortable rahega?\n\n"
            f"Main hamare Lead Architect (Arjun) ke sath ek dedicated 15-minute screen-share session set kar deta hoon jisme hum live architecture aur roadmap discuss kar lenge."
        )
    else:
        tactic = "Unfair Technical Advantage & Moat"
        reply = (
            f"Namaste {c_name}! 👋 {b_name} ko market me scale karne ke liye traditional agencies bohot slow hoti hain.\n\n"
            f"Hum aapko custom high-speed web apps, mobile solutions aur autonomous AI workforce provide karte hain jo 24/7 aapka sales lead generation handle karegi.\n\n"
            f"Aap kab start karna chahenge?"
        )

    lead_phone = None
    if req.lead_id:
        l_row = query_db("SELECT mobile_number, whatsapp_number FROM outreach_leads WHERE id::text = %s;", (req.lead_id,), fetchone=True)
        if l_row:
            lead_phone = l_row.get("whatsapp_number") or l_row.get("mobile_number")

    clean_phone = re.sub(r"[^\d]", "", lead_phone or "")
    if clean_phone and len(clean_phone) == 10:
        clean_phone = "91" + clean_phone
    wa_url = f"https://wa.me/{clean_phone}?text={urllib.parse.quote(reply)}" if clean_phone else None

    return {
        "status": "success",
        "detected_category": cat,
        "negotiation_tactic": tactic,
        "smart_reply": reply,
        "whatsapp_url": wa_url
    }

# -------------------------------------------------------------
# 8. CLIENT ONBOARDING WIZARD & AI PRD GENERATOR
# -------------------------------------------------------------
@router.get("/projects/{project_id}/onboarding")
def get_project_onboarding(project_id: str):
    rows = query_db("SELECT * FROM client_projects WHERE id::text = %s;", (project_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="Project not found.")
    p = rows[0]
    onboarding = p.get("onboarding_data") or {}
    if isinstance(onboarding, str):
        try:
            onboarding = json.loads(onboarding)
        except Exception:
            onboarding = {}
    return {
        "status": "success",
        "project_id": str(p["id"]),
        "client_name": p["client_name"],
        "business_name": p["business_name"],
        "project_title": p["project_title"],
        "onboarding_data": onboarding,
        "has_prd": bool(p.get("prd_document")),
        "is_completed": bool(onboarding and onboarding.get("brand_name"))
    }

@router.post("/projects/{project_id}/submit-onboarding")
def submit_project_onboarding(project_id: str, req: ClientOnboardingSubmitRequest):
    rows = query_db("SELECT * FROM client_projects WHERE id::text = %s;", (project_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="Project not found.")
    proj = rows[0]

    onboarding_dict = req.dict()
    onboarding_dict["submitted_at"] = datetime.now().strftime("%d %b %Y, %I:%M %p")

    b_name = req.brand_name or proj.get("business_name")
    c_name = proj.get("client_name") or "Founder"
    tagline = req.tagline or "Autonomous IT & Digital Growth Platform"
    audience = req.target_audience or "Enterprise, SME, and digital-first consumers"
    features_list = req.must_have_features or ["High-Converting Responsive UI", "24/7 AI Sales Assistant", "Automated Lead Capture", "SEO & Core Web Vitals Optimization", "Fast Cloud Deployment"]
    features_md = "\n".join([f"- **F{idx+1}: {f}**: Fully responsive, accessible, sub-second latency." for idx, f in enumerate(features_list)])
    integrations = ", ".join(req.integrations_needed) if req.integrations_needed else "WhatsApp Business Cloud API, Stripe/Razorpay UPI, PostgreSQL, Google Gemini AI"

    prd_text = f"""# PRODUCT REQUIREMENTS DOCUMENT (PRD)
## Project: {b_name} — Digital Transformation & Growth Platform
**Client Sponsor:** {c_name} | **Author:** Arjun Sharma (Lead Architect, Apex AI Agency)
**Version:** 1.0 (Architecture Baseline) | **Date:** {datetime.now().strftime('%d %b %Y')}
**Status:** Approved for Sprint Execution 🚀

---

### 1. Executive Summary & Product Vision
{b_name} aims to establish a dominant market presence with: "{tagline}".
The objective is to deploy a high-velocity, modern web and mobile platform that converts organic & paid traffic into qualified sales with 0% dropped leads.

### 2. Target Audience & Core Value Proposition
- **Primary Segment:** {audience}
- **Value Drivers:** Instant response time (<60s inquiry turnaround), seamless mobile experience, trusted security, and transparent real-time delivery milestones.

### 3. System Architecture & Tech Stack Specifications
- **Frontend Layer:** Next.js 14 App Router, React 19, TypeScript, Tailwind CSS, Lucide Icons.
- **Backend & API Layer:** Python 3.13, FastAPI asynchronous microservices.
- **AI & Automation Engine:** LangGraph Multi-Agent State Machine with Google Gemini 2.5 / GPT-4o multimodal models.
- **Database & Persistence:** PostgreSQL with JSONB schema indexing & ACID transaction rollback guards.
- **Hosting & Staging:** Edge CDN with Vercel PPR (Partial Prerendering) + AWS RDS.

### 4. Key Functional Specifications & User Stories
{features_md}

### 5. Third-Party Integrations & Security Protocol
- **Connected Services:** {integrations}
- **Brand Standards:** Primary Hex Palette `{req.brand_colors}`, SSL/TLS v1.3 encryption, GSTR-1 compliant invoice logging.
- **Competitor Benchmarking:** Monitored against `{req.competitor_websites or 'Industry Leaders'}` to maintain 40% faster page speed and higher citation authority.

### 6. Agile Sprint Execution & Acceptance Criteria
- Phase 1: Architecture Sign-Off & Wireframe validation (Complete ✓)
- Phase 2: High-Fidelity UI/UX & Brand Identity lock-in.
- Phase 3: Backend API Integration & AI Bot training.
- Phase 4: Security Audit, Core Web Vitals (LCP < 2.5s, CLS < 0.1) & QA.
- Phase 5: Production Domain Launch & Live Handoff.

*Signed & Authorized by Technical Architecture Squad, Apex AI & IT Solutions.*
"""

    assets = proj.get("client_assets") or []
    if isinstance(assets, str):
        try:
            assets = json.loads(assets)
        except Exception:
            assets = []
    
    assets = [a for a in assets if not a.get("asset_name", "").startswith("Product Requirements Document")]
    assets.insert(0, {
        "id": str(uuid.uuid4())[:8],
        "asset_name": "Product Requirements Document (PRD v1.0)",
        "asset_type": "content_doc",
        "asset_url_or_note": "Viewable in Portal PRD tab",
        "uploaded_by": "Arjun Sharma (Lead Architect)",
        "created_at": datetime.now().strftime("%d %b %Y, %I:%M %p")
    })

    execute_db("""
        UPDATE client_projects
        SET onboarding_data = %s::jsonb,
            prd_document = %s,
            client_assets = %s::jsonb,
            status = 'architecture_ready'
        WHERE id::text = %s;
    """, (json.dumps(onboarding_dict), prd_text, json.dumps(assets), project_id))

    try:
        from backend.app.api.routes_agency import WATERCOOLER_FEED
        WATERCOOLER_FEED.insert(0, {
            "id": f"msg_onb_{len(WATERCOOLER_FEED) + 1}",
            "author": "Arjun Sharma",
            "role": "Lead Tech Architect",
            "avatar": "🚀",
            "time": "Just now",
            "badge": "Onboarding Complete",
            "message": f"CLIENT ONBOARDING COMPLETED: {b_name} has finalized project specifications! Technical PRD v1.0 generated and sprint development initialized."
        })
    except Exception:
        pass

    return {
        "status": "success",
        "project_id": project_id,
        "message": f"Onboarding completed for {b_name}! Technical PRD generated.",
        "prd_preview": prd_text[:300] + "..."
    }

# -------------------------------------------------------------
# 9. AUTONOMOUS CODE & COMPONENT STARTER GENERATOR
# -------------------------------------------------------------
@router.post("/projects/generate-code-starter")
def generate_project_code_starter(req: CodeStarterRequest):
    rows = query_db("SELECT * FROM client_projects WHERE id::text = %s;", (req.project_id,))
    if not rows:
        raise HTTPException(status_code=404, detail="Project not found.")
    proj = rows[0]
    b_name = proj.get("business_name") or "Client Brand"
    onb = proj.get("onboarding_data") or {}
    if isinstance(onb, str):
        try:
            onb = json.loads(onb)
        except Exception:
            onb = {}

    brand_color = onb.get("brand_colors", "#4F46E5").split(",")[0].strip()
    tagline = onb.get("tagline") or "Empowering Growth with Next-Gen Technology"

    ctype = req.component_type or "landing_page"

    if ctype == "landing_page":
        filename = "page.tsx"
        code = f"""// Next.js 14 App Router — High-Converting Landing Page for {b_name}
// Generated by Arjun Sharma (Lead Architect, Apex AI Agency)

import React from 'react';
import Link from 'next/link';

export default function HomePage() {{
  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 selection:bg-indigo-500 selection:text-white font-sans">
      <nav className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between border-b border-slate-800/80">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-[{brand_color}] flex items-center justify-center font-bold text-white text-base">
            {b_name[:2].upper()}
          </div>
          <span className="font-extrabold text-lg tracking-tight text-white">{b_name}</span>
        </div>
        <div className="flex items-center gap-4">
          <Link href="#features" className="text-sm text-slate-300 hover:text-white transition">Features</Link>
          <Link href="#pricing" className="text-sm text-slate-300 hover:text-white transition">Pricing</Link>
          <a href="https://wa.me/919876543210" className="px-4 py-2 rounded-xl bg-[{brand_color}] text-white text-xs font-bold shadow-lg hover:opacity-90 transition">
            Book 5-Min Consultation
          </a>
        </div>
      </nav>

      <section className="max-w-5xl mx-auto px-6 py-20 text-center space-y-6">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs font-mono text-indigo-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          2026 Production Architecture Ready
        </div>
        <h1 className="text-4xl sm:text-6xl font-black text-white tracking-tight leading-tight">
          {tagline}
        </h1>
        <p className="max-w-2xl mx-auto text-base sm:text-lg text-slate-400">
          Engineered for speed, conversion, and effortless automation. Delivered with sub-millisecond edge responses.
        </p>
        <div className="flex flex-wrap items-center justify-center gap-3 pt-4">
          <a href="https://wa.me/919876543210" className="px-6 py-3 rounded-2xl bg-[{brand_color}] text-white font-bold text-sm shadow-xl hover:scale-105 transition">
            Get Started Immediately →
          </a>
          <a href="#demo" className="px-6 py-3 rounded-2xl bg-slate-900 border border-slate-800 text-slate-300 font-semibold text-sm hover:bg-slate-800 transition">
            Explore Staging Demo 🌐
          </a>
        </div>
      </section>
    </main>
  );
}}
"""
    elif ctype == "ai_lead_bot":
        filename = "ai_lead_bot.py"
        code = f"""# 24/7 Autonomous WhatsApp AI Sales Receptionist for {b_name}
# Built with Python 3.13, FastAPI & LangGraph

from fastapi import FastAPI, Request
import re

app = FastAPI(title="{b_name} AI Sales Closer")

@app.post("/webhook/chat")
async def handle_incoming_lead(req: Request):
    payload = await req.json()
    message = payload.get("message", "").lower()
    sender = payload.get("sender_phone", "Anonymous")

    if any(k in message for k in ["price", "cost", "budget", "kam"]):
        reply = "Namaste! For {b_name}, we offer flexible milestone payments (50% upfront, 50% upon launch). Would you like to review our pricing sheet?"
    elif any(k in message for k in ["portfolio", "samples", "work", "pehle"]):
        reply = "Here are live case studies and verified work from {b_name}. You can also explore our staging portal!"
    else:
        reply = "Namaste! Welcome to {b_name}. How can our team assist your requirements today?"

    return {{"status": "delivered", "sender": sender, "reply": reply}}
"""
    else:
        filename = "architecture.json"
        code = json.dumps({
            "project_name": b_name,
            "architecture": "Next.js 14 App Router + FastAPI Microservices",
            "primary_brand_color": brand_color,
            "modules": [
                {"name": "Web Platform", "tech": "React 19 / TypeScript", "status": "scaffolded"},
                {"name": "AI Automation", "tech": "LangGraph State Machine", "status": "active"},
                {"name": "PostgreSQL DB", "tech": "Supabase / AWS RDS", "status": "connected"}
            ]
        }, indent=2)

    starter_dict = {
        "filename": filename,
        "component_type": ctype,
        "code": code,
        "generated_at": datetime.now().strftime("%d %b %Y, %I:%M %p")
    }

    execute_db("""
        UPDATE client_projects
        SET starter_code = %s::jsonb
        WHERE id::text = %s;
    """, (json.dumps(starter_dict), req.project_id))

    return {
        "status": "success",
        "project_id": req.project_id,
        "component_type": ctype,
        "filename": filename,
        "code": code,
        "message": f"Starter code '{filename}' generated for {b_name}!"
    }

# -------------------------------------------------------------
# 10. LIVE WHATSAPP INBOUND WEBHOOK (META CLOUD API)
# -------------------------------------------------------------
@router.get("/webhooks/whatsapp")
def verify_whatsapp_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge")
):
    VERIFY_TOKEN = "apex_agency_webhook_secret_2026"
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge) if hub_challenge and hub_challenge.isdigit() else hub_challenge
    return {"status": "error", "message": "Verification token mismatch or invalid mode"}

@router.post("/webhooks/whatsapp")
def receive_whatsapp_webhook(payload: Dict[str, Any]):
    sender = None
    sender_name = "WhatsApp Lead"
    message_text = "Namaste"

    if "entry" in payload:
        try:
            val = payload["entry"][0]["changes"][0]["value"]
            if "messages" in val and val["messages"]:
                msg_obj = val["messages"][0]
                sender = msg_obj.get("from")
                message_text = msg_obj.get("text", {}).get("body", "")
            if "contacts" in val and val["contacts"]:
                sender_name = val["contacts"][0].get("profile", {}).get("name", "Prospect")
        except Exception:
            pass

    if not sender:
        sender = str(payload.get("from") or payload.get("sender_number") or payload.get("phone") or "919876543210")
        sender_name = str(payload.get("name") or payload.get("client_name") or "Direct Inquirer")
        message_text = str(payload.get("text") or payload.get("message") or "Hi, looking for web and AI services.")

    clean_num = re.sub(r"[^\d]", "", sender)
    if len(clean_num) == 10:
        clean_num = "91" + clean_num

    lead_rows = query_db("SELECT * FROM outreach_leads WHERE mobile_number = %s OR whatsapp_number = %s;", (clean_num, clean_num))
    if not lead_rows:
        execute_db("""
            INSERT INTO outreach_leads (full_name, business_name, mobile_number, whatsapp_number, industry, status, notes, inquiry_source)
            VALUES (%s, %s, %s, %s, 'Direct Inquiry', 'in_discussion', %s, 'WhatsApp Inbound Webhook')
            ON CONFLICT (mobile_number) DO UPDATE
            SET status = 'in_discussion';
        """, (sender_name, f"{sender_name}'s Business", clean_num, clean_num, f"Latest Message: {message_text}"))
    else:
        execute_db("UPDATE outreach_leads SET status = 'in_discussion', notes = %s WHERE id = %s;", (f"Latest Message: {message_text}", lead_rows[0]["id"]))

    neg_res = ai_negotiate_reply(AINegotiateRequest(
        client_name=sender_name,
        business_name=f"{sender_name}'s Brand",
        incoming_message=message_text
    ))

    try:
        from backend.app.api.routes_agency import WATERCOOLER_FEED
        WATERCOOLER_FEED.insert(0, {
            "id": f"msg_wa_{len(WATERCOOLER_FEED) + 1}",
            "author": "WhatsApp Inbound Bot",
            "role": "Autonomous Receptionist",
            "avatar": "📲",
            "time": "Just now",
            "badge": "Inbound Message",
            "message": f"WHATSAPP INBOUND from {sender_name} ({clean_num}): \"{message_text}\" - AI Negotiator replied: \"{neg_res['smart_reply'][:60]}...\""
        })
    except Exception:
        pass

    return {
        "status": "success",
        "sender": clean_num,
        "sender_name": sender_name,
        "incoming_message": message_text,
        "ai_objection_handled": neg_res["detected_category"],
        "tactical_reply": neg_res["smart_reply"]
    }
