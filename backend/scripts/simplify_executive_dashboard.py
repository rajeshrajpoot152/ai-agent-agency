import re

def simplify():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Clean Top Header: Replace 9 cluttered buttons with sleek, compact controls & dropdown
    old_header_btns = '''      <div class="flex items-center gap-3">
        <!-- Theme Toggle (Light / Dark Mode) -->
        <button id="theme-toggle-btn" onclick="toggleTheme()" class="py-1.5 px-3 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-xs font-medium transition flex items-center gap-1.5" title="Switch between Light & Dark mode">
          <span id="theme-icon">☀️</span>
          <span id="theme-label" class="hidden sm:inline">Light Mode</span>
        </button>

        <!-- Voice Speaker Toggle -->
        <button id="tts-toggle-btn" onclick="toggleAutoTTS()" class="py-1.5 px-3 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-xs font-mono transition flex items-center gap-1.5" title="Auto-read assistant responses aloud">
          <span id="tts-icon">🔊</span>
          <span id="tts-label" class="hidden sm:inline">Voice: OFF</span>
        </button>

        <!-- Public Lead Intake Page Link -->
        <a href="/inquiry" target="_blank" class="py-1.5 px-3 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-xs font-medium transition flex items-center gap-1.5 shadow-sm" title="Open Public Client Intake Form (/inquiry)">
          <span>🌐</span>
          <span class="hidden md:inline">Client Intake Form</span>
        </a>

        <!-- Fast GST Tax Invoice Creator -->
        <button onclick="openInvoiceModal('', '', '', '₹45,000')" class="py-1.5 px-3 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-xs font-medium transition flex items-center gap-1.5 shadow-sm" title="Create 1-Click GST Invoice & UPI QR">
          <span>💳</span>
          <span class="hidden md:inline">Invoice & QR</span>
        </button>

        <!-- 1-Click Client Website & Tech Audit Hook -->
        <button onclick="openWebsiteAuditModal()" class="py-1.5 px-3 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-xs font-medium transition flex items-center gap-1.5 shadow-sm" title="Run 1-Click Client Website & SEO Tech Audit">
          <span>🔍</span>
          <span class="hidden md:inline">Web Audit</span>
        </button>

        <!-- System Health Audit -->
        <button onclick="openAuditModal()" class="py-1.5 px-3 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-xs font-medium transition flex items-center gap-1.5 shadow-sm" title="Run System Health & Diagnostic Audit">
          <span>🩺</span>
          <span class="hidden md:inline">Audit</span>
        </button>

        <!-- Connect AI Brain Modal Trigger -->
        <button onclick="openAIKeyModal()" class="py-1.5 px-3 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-xs font-medium transition flex items-center gap-1.5 shadow-sm" title="Connect Google Gemini (Free) or ChatGPT API Key">
          <span>🧠</span>
          <span class="hidden sm:inline">Connect AI Brain</span>
        </button>

        <!-- Fast Mission Cockpit -->
        <button onclick="switchTab('missions')" class="py-1.5 px-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-xs shadow-sm transition flex items-center gap-1.5">
          <span>🚀</span> Projects Cockpit
        </button>

        <button onclick="refreshUniversalData()" class="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 transition text-xs" title="Refresh">
          🔄
        </button>
      </div>'''

    new_header_btns = '''      <div class="flex items-center gap-2.5">
        <!-- Theme Toggle -->
        <button id="theme-toggle-btn" onclick="toggleTheme()" class="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-xs transition" title="Toggle Theme">
          <span id="theme-icon">☀️</span>
        </button>

        <!-- Connect AI Brain -->
        <button onclick="openAIKeyModal()" class="py-1.5 px-3 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-xs font-semibold transition flex items-center gap-1.5 shadow-sm" title="Connect Gemini or ChatGPT">
          <span>🧠</span>
          <span class="hidden sm:inline">AI Brain</span>
        </button>

        <!-- Quick Utilities Dropdown (Invoice, Audit, Intake) -->
        <div class="relative inline-block text-left">
          <button id="quick-tools-btn" onclick="toggleQuickToolsMenu()" class="py-1.5 px-3 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-xs font-semibold transition flex items-center gap-1 shadow-sm">
            <span>⚡ Tools</span>
            <span class="text-[10px]">▼</span>
          </button>
          <div id="quick-tools-dropdown" class="hidden absolute right-0 mt-2 w-52 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xl py-2 z-50 text-xs">
            <a href="/inquiry" target="_blank" class="flex items-center gap-2 px-3.5 py-2 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300">
              <span>🌐</span> Public Client Intake
            </a>
            <button onclick="openInvoiceModal('', '', '', '₹45,000'); toggleQuickToolsMenu();" class="w-full text-left flex items-center gap-2 px-3.5 py-2 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300">
              <span>💳</span> GST Invoice & UPI QR
            </button>
            <button onclick="openWebsiteAuditModal(); toggleQuickToolsMenu();" class="w-full text-left flex items-center gap-2 px-3.5 py-2 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300">
              <span>🔍</span> Web & SEO Audit
            </button>
            <button onclick="openAuditModal(); toggleQuickToolsMenu();" class="w-full text-left flex items-center gap-2 px-3.5 py-2 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300">
              <span>🩺</span> System Diagnostic
            </button>
          </div>
        </div>

        <button onclick="refreshUniversalData()" class="p-2 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 transition text-xs" title="Refresh">
          🔄
        </button>
      </div>'''

    if old_header_btns in html:
        html = html.replace(old_header_btns, new_header_btns, 1)

    # 2. Compact, Short & Strong Cockpit (`tab-cockpit`)
    old_cockpit_markup = re.search(r'(<div id="tab-cockpit"[\s\S]*?</div>\s*<!-- ======================================================\s*-->\s*<!-- TAB: SOCIAL MARKETING AUTOPILOT)', html)
    if old_cockpit_markup:
        new_cockpit_markup = '''<div id="tab-cockpit" class="tab-content flex-1 overflow-y-auto p-5 md:p-6 space-y-4">
        
        <!-- 1. Sleek Compact Venture Bar (Short & Direct) -->
        <div class="p-3.5 md:p-4 rounded-2xl bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 shadow-sm flex items-center justify-between gap-3 flex-wrap">
          <div class="flex items-center gap-3 min-w-[260px]">
            <div class="w-10 h-10 rounded-xl bg-indigo-600/10 text-indigo-600 dark:text-indigo-400 flex items-center justify-center font-bold text-lg">⚡</div>
            <div>
              <div class="flex items-center gap-2 flex-wrap">
                <h2 id="cockpit-proj-name" class="font-black text-sm md:text-base text-slate-900 dark:text-white">Apex AI & IT Solutions</h2>
                <span id="cockpit-proj-type-badge" class="px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase bg-indigo-50 text-indigo-600 dark:bg-indigo-950 dark:text-indigo-300">IT Services</span>
                <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-50 text-emerald-600 dark:bg-emerald-950 dark:text-emerald-400 font-bold">● Isolated</span>
              </div>
              <p id="cockpit-proj-tagline" class="text-[11px] text-slate-500 truncate max-w-lg mt-0.5">High-velocity systems & automation</p>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <a id="cockpit-proj-site-link" href="#" target="_blank" class="px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-semibold transition">🌐 Site</a>
            <button onclick="switchTab('chat')" class="px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs shadow-sm transition flex items-center gap-1.5">
              <span>💬</span> Instruct Squad
            </button>
          </div>
        </div>

        <!-- 2. Compact 4-KPI Row (Short Numbers, Zero Fluff) -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div class="p-3.5 rounded-2xl bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 flex items-center gap-3 shadow-sm">
            <div class="w-8 h-8 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 flex items-center justify-center text-sm">🎯</div>
            <div>
              <div class="text-[10px] font-mono text-slate-400 uppercase">Leads</div>
              <div id="cockpit-stat-leads" class="text-base font-black text-slate-900 dark:text-white font-mono">0</div>
            </div>
          </div>
          <div class="p-3.5 rounded-2xl bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 flex items-center gap-3 shadow-sm">
            <div class="w-8 h-8 rounded-xl bg-sky-50 dark:bg-sky-950/60 flex items-center justify-center text-sm">💼</div>
            <div>
              <div class="text-[10px] font-mono text-slate-400 uppercase">In Discussion</div>
              <div id="cockpit-stat-discussions" class="text-base font-black text-indigo-600 dark:text-indigo-400 font-mono">0</div>
            </div>
          </div>
          <div class="p-3.5 rounded-2xl bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 flex items-center gap-3 shadow-sm">
            <div class="w-8 h-8 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 flex items-center justify-center text-sm">🏆</div>
            <div>
              <div class="text-[10px] font-mono text-slate-400 uppercase">Won</div>
              <div id="cockpit-stat-won" class="text-base font-black text-emerald-600 dark:text-emerald-400 font-mono">0</div>
            </div>
          </div>
          <div class="p-3.5 rounded-2xl bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 flex items-center gap-3 shadow-sm">
            <div class="w-8 h-8 rounded-xl bg-purple-50 dark:bg-purple-950/60 flex items-center justify-center text-sm">📢</div>
            <div>
              <div class="text-[10px] font-mono text-slate-400 uppercase">Autopilot</div>
              <div id="cockpit-stat-autopilot" class="text-xs font-black text-emerald-600 dark:text-emerald-400 font-mono">Active (4)</div>
            </div>
          </div>
        </div>

        <!-- 3. Short 2-Column Command Grid: 3D Squad + Impact Radar -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-3.5">
          <!-- Compact 3D Specialist Squad (5 Cols) -->
          <div class="lg:col-span-5 p-4 rounded-2xl bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 space-y-2.5 shadow-sm">
            <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800/80 pb-2">
              <h3 class="font-bold text-xs text-slate-900 dark:text-white flex items-center gap-1.5">
                <span>👥</span> Assigned 3D Squad
              </h3>
              <span class="text-[10px] font-mono text-emerald-500 font-bold">● Active Duty</span>
            </div>
            <div id="cockpit-squad-container" class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <!-- Compact horizontal squad chips -->
            </div>
          </div>

          <!-- Compact Cause-and-Effect Impact Radar (7 Cols) -->
          <div class="lg:col-span-7 p-4 rounded-2xl bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 space-y-2.5 shadow-sm">
            <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800/80 pb-2">
              <h3 class="font-bold text-xs text-slate-900 dark:text-white flex items-center gap-1.5">
                <span>🎯</span> Cause-and-Effect Radar
              </h3>
              <span class="text-[10px] font-mono text-indigo-500 font-bold">Predicted Impact</span>
            </div>
            <div id="cockpit-impact-radar-container" class="space-y-2">
              <!-- Compact 1-line prediction bars -->
            </div>
          </div>
        </div>

      </div>

      <!-- ====================================================== -->
      <!-- TAB: SOCIAL MARKETING AUTOPILOT'''
        html = html[:old_cockpit_markup.start()] + new_cockpit_markup + html[old_cockpit_markup.end()-len('<!-- TAB: SOCIAL MARKETING AUTOPILOT'):]

    # 3. Update JavaScript renderCockpitTab to render compact squad chips and compact impact radar
    old_render_cockpit = '''      // Render Assigned 3D Squad
      const squadContainer = document.getElementById('cockpit-squad-container');
      const squad = data.assigned_squad || [];
      if (squadContainer) {
        if (squad.length === 0) {
          squadContainer.innerHTML = `<div class="p-4 rounded-2xl bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-xs text-slate-400">Defaulting to Core Executive Squad.</div>`;
        } else {
          squadContainer.innerHTML = squad.map(member => `
            <div class="p-3.5 rounded-2xl bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 flex items-center justify-between shadow-sm hover:border-indigo-500/40 transition">
              <div class="flex items-center gap-3">
                <img src="${member.avatar || '/assets/avatars/head_charlie.jpg'}" class="w-11 h-11 rounded-full object-cover border-2 border-indigo-500 shadow" alt="${escapeAttr(member.name)}" onerror="this.src='/assets/avatars/agent_1.jpg'" />
                <div>
                  <h4 class="font-bold text-xs text-slate-900 dark:text-white">${escapeHtml(member.name)}</h4>
                  <p class="text-[10px] text-indigo-600 dark:text-indigo-400 font-mono">${escapeHtml(member.role)}</p>
                </div>
              </div>
              <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-50 text-emerald-600 dark:bg-emerald-950/60 dark:text-emerald-400 font-bold">● Active Duty</span>
            </div>
          `).join('');
        }
      }

      // Render Cause-and-Effect Impact Radar Simulation Cards
      const radarContainer = document.getElementById('cockpit-impact-radar-container');
      const predictions = radar.action_predictions || [];
      if (radarContainer) {
        radarContainer.innerHTML = predictions.map(act => `
          <div class="p-4 rounded-2xl bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 space-y-2 shadow-sm hover:border-indigo-500/40 transition">
            <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800/80 pb-2">
              <div class="flex items-center gap-2">
                <span class="text-base">⚡</span>
                <span class="font-bold text-xs text-slate-900 dark:text-white">${escapeHtml(act.trigger_action)}</span>
              </div>
              <span class="text-[10px] font-mono text-indigo-600 dark:text-indigo-400 font-bold">Predicted Outcome ➔</span>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-1 text-[11px] font-mono">
              <div class="p-2 rounded-xl bg-slate-50 dark:bg-slate-900/60">
                <span class="text-[9px] text-slate-400 uppercase block">Expected Reach</span>
                <span class="font-bold text-slate-800 dark:text-slate-200">${escapeHtml(act.predicted_reach)}</span>
              </div>
              <div class="p-2 rounded-xl bg-indigo-50/60 dark:bg-indigo-950/40 border border-indigo-100 dark:border-indigo-900/40">
                <span class="text-[9px] text-indigo-500 uppercase block">Inbound Lead Velocity</span>
                <span class="font-bold text-indigo-700 dark:text-indigo-300">${escapeHtml(act.inbound_lead_impact)}</span>
              </div>
              <div class="p-2 rounded-xl bg-emerald-50/60 dark:bg-emerald-950/40 border border-emerald-100 dark:border-emerald-900/40">
                <span class="text-[9px] text-emerald-600 uppercase block">Direct Pipeline Impact</span>
                <span class="font-bold text-emerald-700 dark:text-emerald-300">${escapeHtml(act.pipeline_impact)}</span>
              </div>
            </div>
          </div>
        `).join('');
      }'''

    new_render_cockpit = '''      // Render Assigned 3D Squad (Compact, Short Chips)
      const squadContainer = document.getElementById('cockpit-squad-container');
      const squad = data.assigned_squad || [];
      if (squadContainer) {
        if (squad.length === 0) {
          squadContainer.innerHTML = `<div class="p-2 text-xs text-slate-400 font-mono">Executive Squad Active.</div>`;
        } else {
          squadContainer.innerHTML = squad.map(member => `
            <div class="p-2 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 flex items-center gap-2.5 shadow-sm">
              <img src="${member.avatar || '/assets/avatars/head_charlie.jpg'}" class="w-8 h-8 rounded-full object-cover border border-indigo-500 flex-shrink-0" alt="${escapeAttr(member.name)}" onerror="this.src='/assets/avatars/agent_1.jpg'" />
              <div class="min-w-0">
                <h4 class="font-bold text-[11px] text-slate-900 dark:text-white truncate">${escapeHtml(member.name)}</h4>
                <p class="text-[9px] text-indigo-600 dark:text-indigo-400 font-mono truncate">${escapeHtml(member.role)}</p>
              </div>
            </div>
          `).join('');
        }
      }

      // Render Cause-and-Effect Impact Radar (Compact 1-Line Predictive Bars)
      const radarContainer = document.getElementById('cockpit-impact-radar-container');
      const predictions = radar.action_predictions || [];
      if (radarContainer) {
        radarContainer.innerHTML = predictions.map(act => `
          <div class="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200/80 dark:border-slate-800 flex items-center justify-between gap-2 shadow-sm text-xs">
            <div class="flex items-center gap-2 min-w-0">
              <span class="text-indigo-500 flex-shrink-0 font-bold">⚡</span>
              <span class="font-bold text-slate-800 dark:text-slate-200 truncate">${escapeHtml(act.trigger_action)}</span>
            </div>
            <div class="flex items-center gap-1.5 flex-shrink-0 font-mono text-[10px]">
              <span class="px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300 font-bold">${escapeHtml(act.inbound_lead_impact)}</span>
              <span class="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 font-bold">${escapeHtml(act.pipeline_impact)}</span>
            </div>
          </div>
        `).join('');
      }'''

    if old_render_cockpit in html:
        html = html.replace(old_render_cockpit, new_render_cockpit, 1)

    # 4. Helper for Quick Tools dropdown
    dropdown_helper_js = '''
    function toggleQuickToolsMenu() {
      const menu = document.getElementById('quick-tools-dropdown');
      if (menu) menu.classList.toggle('hidden');
    }
    document.addEventListener('click', function(e) {
      const btn = document.getElementById('quick-tools-btn');
      const menu = document.getElementById('quick-tools-dropdown');
      if (btn && menu && !btn.contains(e.target) && !menu.contains(e.target)) {
        menu.classList.add('hidden');
      }
    });
'''
    if 'function toggleQuickToolsMenu' not in html:
        html = html.replace('</script>\n</body>', dropdown_helper_js + '\n</script>\n</body>', 1)

    with open("frontend/index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("✓ Successfully simplified executive dashboard!")

if __name__ == "__main__":
    simplify()
