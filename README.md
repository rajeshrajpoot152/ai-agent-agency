# 🏢 AI Agent Agency Master (LangGraph Enterprise Edition)

A 100% autonomous, dynamic multi-agent system powered by **LangGraph**, **FastAPI**, and **PostgreSQL (`agency_master`)**. Zero hardcoded/static mock data.

---

## 🌟 Key Features

1. **Stateful LangGraph Architecture**:
   - `Orchestrator Node` (CEO Agent)
   - `Outreach Agent Node` (Copywriting & Personalization Specialist)
   - `QA Evaluator Node` (Quality Control & Cyclic Review Loop)
   - `Dispatcher Node` (Tool Execution & WhatsApp Dispatch)
   - `Self-Learning Node` (Continuous Autonomous Self-Training)

2. **Full Dynamic Control**:
   - **Pause / Resume Switch**: Stop or resume outreach anytime.
   - **Schedule Time Picker**: Set exact execution time (e.g., `10:30:00`).
   - **Daily Quota**: Set daily batch size (e.g., 5 messages/day).
   - **Safe Interval**: Built-in delays to prevent spam or bans.

3. **Modern Real-Time Web Dashboard**:
   - Live KPI metrics (Total, Pending, Contacted, Today's quota).
   - Interactive control panel.
   - Live stream terminal showing LangGraph node execution in real time.
   - Master Leads table with 100 contacts.

4. **Client Ready (Delivery & Hand-off)**:
   - Includes `docker-compose.yml` for 1-click client deployments.
   - Pluggable tools for messaging (Console Mock, Twilio, WhatsApp Cloud API).

---

## 📁 Project Structure

```
ai-agent-agency/
├── backend/
│   ├── app/
│   │   ├── api/                  # FastAPI REST Endpoints
│   │   │   ├── routes_agency.py  # Status, Pause, Resume, Schedule, Quota, Run-Batch
│   │   │   └── routes_leads.py   # Lead CRUD & Message Logs
│   │   ├── core/
│   │   │   ├── config.py         # Pydantic Settings & Environment Variables
│   │   │   └── database.py       # PostgreSQL Connection Pool
│   │   ├── graph/                # LangGraph State Machine
│   │   │   ├── state.py          # AgencyState TypedDict
│   │   │   ├── nodes.py          # Agent Execution Nodes
│   │   │   ├── edges.py          # Conditional & Cyclic Edges
│   │   │   └── workflow.py       # Compiled StateGraph with Checkpointing
│   │   ├── tools/
│   │   │   └── whatsapp_tool.py  # Pluggable Messaging Tool
│   │   └── main.py               # FastAPI App & Dashboard Static Mounter
├── database/
│   ├── schema.sql                # Complete PostgreSQL Master Schema
│   └── seed_data.sql             # Default Agents & Initial Campaign
├── frontend/
│   └── index.html                # Modern Tailwind CSS Dashboard
├── docker-compose.yml            # 1-Click Container Deployment
├── Dockerfile                    # Container build file
├── run_server.py                 # Starts Web Dashboard & FastAPI Server
├── run_langgraph_test.py         # Direct LangGraph Terminal Test
├── start-agency.bat              # Windows One-Click Auto Starter
└── .env                          # PostgreSQL & API Credentials
```

---

## 🚀 How to Run

### Method 1: Local Server (Windows / Mac / Linux)
```bash
# 1. Start Web Dashboard & API Server
python run_server.py
```
Open your browser and navigate to:
- **Control Dashboard**: `http://127.0.0.1:8000/`
- **Interactive Swagger API Docs**: `http://127.0.0.1:8000/docs`

### Method 2: Client Delivery via Docker
Give this folder to your client and run:
```bash
docker-compose up -d
```
All services (PostgreSQL, LangGraph Backend, and UI) will automatically spin up!

---

## 🛠️ How to Customize

- **Add a New Agent Node**: Define a new function in `backend/app/graph/nodes.py` and register it in `backend/app/graph/workflow.py`.
- **Add a New Tool**: Add your API logic under `backend/app/tools/` and import it into the dispatcher node.
- **Change Model**: Configure your `GEMINI_API_KEY` in `.env`.
