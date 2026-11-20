import re

def update_interactive_chat():
    with open("backend/app/core/interactive_chat.py", "r", encoding="utf-8") as f:
        chat_code = f.read()

    # Add project auto create detection
    target_check = 'is_followup_query = any(w in msg_lower for w in ["follow up", "followup", "follow-up", "kisko message karna", "aaj ka follow up", "pending leads", "inquiry status", "pipeline", "client status", "leads status"])'
    
    new_check = '''is_followup_query = any(w in msg_lower for w in ["follow up", "followup", "follow-up", "kisko message karna", "aaj ka follow up", "pending leads", "inquiry status", "pipeline", "client status", "leads status"])

    is_project_auto_create = any(w in msg_lower for w in [
        "naya project", "new project", "project add", "naya client", "new client",
        "add client", "naya tool", "new tool", "project build", "build project"
    ])'''

    if "is_project_auto_create =" not in chat_code:
        chat_code = chat_code.replace(target_check, new_check, 1)

    # Add execution branch in handle_user_chat
    target_branch = '# SCENARIO 0: DIRECT API KEY SUBMISSION'
    new_branch = '''# SCENARIO -1: AUTONOMOUS PROJECT / CLIENT CREATION & INGESTION
    if is_project_auto_create:
        add_human_step(execution_steps, "CEO_Orchestrator", "Project Ingestion", "Autonomous project analysis, skill equipping, and squad assignment.")
        try:
            from backend.app.api.routes_projects_hub import execute_auto_ingest
            ingest_res = execute_auto_ingest(clean_msg)
            if ingest_res.get("status") == "success":
                p = ingest_res["project"]
                squad = p.get("assigned_squad", [])
                if isinstance(squad, str):
                    import json
                    try: squad = json.loads(squad)
                    except: squad = []
                squad_str = ", ".join([f"{m.get('name', 'Specialist')} ({m.get('role', 'Lead')})" for m in squad])
                
                response_text = (
                    f"✅ **Project '{p.get('brand_name')}' Autonomously Built & Activated!**\\n\\n"
                    f"🔹 **Industry:** {p.get('industry')}\\n"
                    f"🔹 **Tagline:** {p.get('tagline')}\\n"
                    f"🔹 **Assigned 3D Squad:** {squad_str}\\n"
                    f"🔹 **Social Autopilot:** 4 multi-platform posts ready in queue.\\n"
                    f"🔹 **Data Isolation:** Enforced 100% (Zero cross-client leakage).\\n\\n"
                    f"Aap top project selector me **{p.get('brand_name')}** par switch kar sakte hain. Bataiye, abhi iske liye pehle kya execute karein?"
                )
                deliverable = (
                    f"# 🚀 Project Blueprint: {p.get('brand_name')}\\n\\n"
                    f"- **Vertical:** {p.get('project_type')}\\n"
                    f"- **Industry:** {p.get('industry')}\\n"
                    f"- **Website:** {p.get('website_url')}\\n"
                    f"- **Value Proposition:** {p.get('value_proposition')}\\n"
                    f"- **Pricing Model:** {p.get('pricing_tier_summary')}\\n"
                    f"- **Max Allowed Discount:** {p.get('allowed_discount_max')}%"
                )
            else:
                response_text = f"Error creating project: {ingest_res.get('message')}"
        except Exception as e:
            response_text = f"Technical Error building project: {str(e)}"

    elif ''' + target_branch

    if "SCENARIO -1: AUTONOMOUS PROJECT" not in chat_code:
        chat_code = chat_code.replace(target_branch, new_branch, 1)

    with open("backend/app/core/interactive_chat.py", "w", encoding="utf-8") as f:
        f.write(chat_code)

    print("✓ Updated interactive_chat.py with autonomous project builder.")

def update_frontend():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Remove hardcoded category filter chips from Master Project Switcher bar
    old_cat_chips = '''      <!-- Quick Category Filter Chips -->
      <div class="flex items-center gap-1.5 overflow-x-auto text-[11px] font-medium py-0.5">
        <button onclick="filterProjectCategory('all', this)" class="proj-cat-chip px-2.5 py-1 rounded-lg bg-indigo-600 text-white font-bold transition">All</button>
        <button onclick="filterProjectCategory('it_company', this)" class="proj-cat-chip px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 transition">IT Flagship</button>
        <button onclick="filterProjectCategory('tool_website', this)" class="proj-cat-chip px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 transition">6 Tools</button>
        <button onclick="filterProjectCategory('real_estate', this)" class="proj-cat-chip px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 transition">Real Estate</button>
        <button onclick="filterProjectCategory('jewelry', this)" class="proj-cat-chip px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 transition">Jewelry</button>
        <button onclick="filterProjectCategory('custom_crm', this)" class="proj-cat-chip px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 transition">CRM</button>
      </div>'''

    if old_cat_chips in html:
        html = html.replace(old_cat_chips, '', 1)

    # 2. Update New Project Modal to 1-Click Autonomous Auto-Builder
    old_modal = re.search(r'(<div id="create-project-modal"[\s\S]*?</div>\s*</div>\s*</div>\s*</div>)', html)
    
    new_modal_html = '''  <!-- ======================================================== -->
  <!-- MODAL: AUTONOMOUS 1-CLICK PROJECT BUILDER (ZERO EFFORT)   -->
  <!-- ======================================================== -->
  <div id="create-project-modal" class="hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 max-w-lg w-full shadow-2xl space-y-4">
      <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
        <div class="flex items-center gap-2">
          <span class="text-2xl">⚡</span>
          <div>
            <h3 class="font-bold text-sm text-slate-900 dark:text-white">Auto-Build Any Project or Client</h3>
            <p class="text-[11px] text-slate-500">Autonomous crawler, squad assignment, and skill auto-configuration</p>
          </div>
        </div>
        <button onclick="closeCreateProjectModal()" class="text-slate-400 hover:text-slate-700 dark:hover:text-white text-base">✕</button>
      </div>

      <div class="space-y-3 text-xs">
        <div>
          <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Website URL, Company Name, or Brief *</label>
          <textarea id="auto-ingest-input" rows="3" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-slate-900 dark:text-white font-medium text-xs focus:ring-2 focus:ring-indigo-500 leading-relaxed" placeholder="Enter URL (e.g. https://example.com) OR brief (e.g. Shree Ram Developers, luxury residential villas in Pune, or a new SaaS tool)..."></textarea>
          <p class="text-[10px] text-slate-400 mt-1 font-mono">💡 AI automatically crawls the site, detects industry, assigns the optimal 3D squad, and seeds marketing.</p>
        </div>

        <div id="auto-build-loading" class="hidden p-3 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800 text-indigo-700 dark:text-indigo-300 text-xs flex items-center gap-2">
          <span class="animate-spin text-base">⏳</span>
          <span class="font-semibold">Crawling website, auto-equipping skills, and configuring 3D squad...</span>
        </div>

        <div class="flex items-center justify-end gap-2 pt-2">
          <button onclick="closeCreateProjectModal()" class="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-semibold">Cancel</button>
          <button id="btn-auto-build-proj" onclick="submitAutoBuildProjectAction()" class="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs shadow-sm transition flex items-center gap-1.5">
            <span>🚀</span> Build & Launch Project
          </button>
        </div>
      </div>
    </div>
  </div>'''

    # Replace modal in html
    if 'id="auto-ingest-input"' not in html:
        # Search for create-project-modal
        m_start = html.find('<div id="create-project-modal"')
        if m_start != -1:
            m_end = html.find('<!-- ======================================================== -->\n  <!-- MODAL: ADD LEAD TO ACTIVE PROJECT', m_start)
            if m_end != -1:
                html = html[:m_start] + new_modal_html + '\n\n  ' + html[m_end:]

    # 3. Add JS function submitAutoBuildProjectAction
    js_func = '''
    async function submitAutoBuildProjectAction() {
      const input = document.getElementById('auto-ingest-input').value.trim();
      if (!input) {
        alert('Please enter a website URL, company name, or project description.');
        return;
      }

      const btn = document.getElementById('btn-auto-build-proj');
      const loader = document.getElementById('auto-build-loading');
      btn.disabled = true;
      loader.classList.remove('hidden');

      try {
        const res = await fetch(`${API_BASE}/api/projects-hub/auto-ingest`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ input_text: input })
        });
        const data = await res.json();
        loader.classList.add('hidden');
        btn.disabled = false;

        if (data.status === 'success') {
          alert('✓ ' + data.message);
          closeCreateProjectModal();
          document.getElementById('auto-ingest-input').value = '';
          currentProjectId = data.project.id;
          await loadMasterProjects();
          await selectProject(data.project.id);
        } else {
          alert('Error: ' + (data.message || 'Could not build project'));
        }
      } catch (e) {
        loader.classList.add('hidden');
        btn.disabled = false;
        alert('Network/Build error: ' + e.message);
      }
    }
'''

    if 'function submitAutoBuildProjectAction' not in html:
        html = html.replace('</script>\n</body>', js_func + '\n</script>\n</body>', 1)

    with open("frontend/index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("✓ Updated frontend with 1-click autonomous project builder & removed static category pills.")

if __name__ == "__main__":
    update_interactive_chat()
    update_frontend()
