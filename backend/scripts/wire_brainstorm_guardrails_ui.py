import re

def wire_ui():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Add action buttons inside the cockpit-market-spy-bar right side
    if 'triggerSquadBrainstormModal()' not in html:
        target = '<span class="px-2 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-bold">● High Advantage</span>'
        replacement = '''<div class="flex items-center gap-2">
            <span class="px-2 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-bold">● High Advantage</span>
            <button onclick="triggerSquadBrainstormModal()" class="px-3 py-1 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-[11px] flex items-center gap-1 transition shadow-sm">
              <span>🧠</span> Squad Brainstorm
            </button>
            <button onclick="openGuardrailsModal()" class="px-3 py-1 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-bold text-[11px] flex items-center gap-1 transition">
              <span>🛡️</span> Zero-Mistake Rules
            </button>
          </div>'''
        html = html.replace(target, replacement, 1)

    # 2. Add Squad Brainstorm Modal
    brainstorm_modal_html = '''
  <!-- ======================================================== -->
  <!-- MODAL: AUTONOMOUS SQUAD BRAINSTORMING ROOM               -->
  <!-- ======================================================== -->
  <div id="squad-brainstorm-modal" class="hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 max-w-2xl w-full shadow-2xl space-y-4 animate-scaleIn max-h-[85vh] flex flex-col">
      <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
        <div class="flex items-center gap-2.5">
          <span class="text-2xl">🧠</span>
          <div>
            <h3 class="font-bold text-sm text-slate-900 dark:text-white">Autonomous Squad Brainstorming Room</h3>
            <p id="brainstorm-modal-sub" class="text-[11px] text-slate-500 font-mono">Live multi-agent strategic alignment</p>
          </div>
        </div>
        <button onclick="closeSquadBrainstormModal()" class="text-slate-400 hover:text-slate-700 dark:hover:text-white text-base">✕</button>
      </div>

      <div class="overflow-y-auto space-y-4 pr-1 flex-1">
        <!-- Live Dialogue Transcript -->
        <div class="space-y-2">
          <div class="text-[11px] font-mono text-slate-400 uppercase tracking-wider font-bold">Squad Discussion Transcript</div>
          <div id="brainstorm-dialogue-container" class="space-y-2.5 bg-slate-50 dark:bg-slate-950 p-4 rounded-2xl border border-slate-200 dark:border-slate-800">
            <div class="text-center py-6 text-slate-400 text-xs">Assembling squad & initiating brainstorming... ⏳</div>
          </div>
        </div>

        <!-- Consensus & Tasks -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
          <div class="p-3.5 rounded-2xl bg-indigo-50/50 dark:bg-indigo-950/30 border border-indigo-200 dark:border-indigo-800/50 space-y-1.5">
            <div class="text-[10px] font-mono font-bold text-indigo-600 dark:text-indigo-400 uppercase">Executive Consensus</div>
            <div id="brainstorm-consensus-text" class="text-xs text-slate-800 dark:text-slate-200 leading-relaxed font-sans">Strategic alignment in progress...</div>
          </div>
          <div class="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 space-y-1.5">
            <div class="text-[10px] font-mono font-bold text-slate-400 uppercase">Assigned Employee Sprints</div>
            <div id="brainstorm-tasks-container" class="space-y-1 text-xs">
              <!-- Dynamically rendered -->
            </div>
          </div>
        </div>
      </div>

      <div class="pt-2 border-t border-slate-100 dark:border-slate-800 flex justify-end gap-2">
        <button onclick="closeSquadBrainstormModal()" class="px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-bold text-xs hover:bg-slate-200 transition">
          Close
        </button>
        <button onclick="triggerSquadBrainstormModal()" class="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow transition flex items-center gap-1.5">
          <span>🔄</span> Re-Brainstorm Next Sprint
        </button>
      </div>
    </div>
  </div>
'''

    # 3. Add Founder Guardrails & Zero-Mistake Modal
    guardrails_modal_html = '''
  <!-- ======================================================== -->
  <!-- MODAL: FOUNDER GUARDRAILS & ZERO-MISTAKE RULES           -->
  <!-- ======================================================== -->
  <div id="agency-guardrails-modal" class="hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 max-w-xl w-full shadow-2xl space-y-4 animate-scaleIn max-h-[85vh] flex flex-col">
      <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
        <div class="flex items-center gap-2.5">
          <span class="text-2xl">🛡️</span>
          <div>
            <h3 class="font-bold text-sm text-slate-900 dark:text-white">Founder Guardrails & Zero-Mistake Rules</h3>
            <p class="text-[11px] text-emerald-500 font-mono font-bold">● 100% Strict Pre-Response Enforcement Active</p>
          </div>
        </div>
        <button onclick="closeGuardrailsModal()" class="text-slate-400 hover:text-slate-700 dark:hover:text-white text-base">✕</button>
      </div>

      <!-- Add New Correction / Rule Form -->
      <div class="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 space-y-2">
        <label class="block text-[11px] font-bold text-slate-700 dark:text-slate-300">Teach / Correct Agents (Never Repeat This Mistake):</label>
        <div class="flex gap-2">
          <input id="input-new-rule-text" type="text" placeholder="e.g. Invoices me GST hamesha include karo / WhatsApp me English mat use karo" class="flex-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-900 dark:text-white focus:outline-none focus:border-indigo-500" />
          <button onclick="submitNewFounderRule()" class="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs whitespace-nowrap shadow transition">
            + Add Rule
          </button>
        </div>
      </div>

      <!-- Rules List -->
      <div class="overflow-y-auto space-y-2.5 pr-1 flex-1">
        <div class="text-[11px] font-mono text-slate-400 uppercase tracking-wider font-bold">Active Agency Guardrails</div>
        <div id="guardrails-list-container" class="space-y-2">
          <div class="text-center py-6 text-slate-400 text-xs">Loading guardrails... ⏳</div>
        </div>
      </div>

      <div class="pt-2 border-t border-slate-100 dark:border-slate-800 flex justify-end">
        <button onclick="closeGuardrailsModal()" class="px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-bold text-xs hover:bg-slate-200 transition">
          Done
        </button>
      </div>
    </div>
  </div>
'''

    if 'id="squad-brainstorm-modal"' not in html:
        html = html.replace('</body>', brainstorm_modal_html + '\n' + guardrails_modal_html + '\n</body>', 1)

    # 4. Add JS Controllers
    ui_js = '''
    // ========================================================
    // SQUAD BRAINSTORMING & GUARDRAIL JAVASCRIPT CONTROLLERS
    // ========================================================

    // 1. Trigger Squad Brainstorming
    async function triggerSquadBrainstormModal() {
      if (!currentProjectId) {
        alert('Please select an active project first.');
        return;
      }
      const modal = document.getElementById('squad-brainstorm-modal');
      const sub = document.getElementById('brainstorm-modal-sub');
      const diaCont = document.getElementById('brainstorm-dialogue-container');
      const conText = document.getElementById('brainstorm-consensus-text');
      const taskCont = document.getElementById('brainstorm-tasks-container');

      modal.classList.remove('hidden');
      diaCont.innerHTML = '<div class="text-center py-8 text-slate-400 text-xs font-mono">Assembling Tech Lead (Vikram), Growth (Pooja), Design (Arjun) & QA (Kabir)... ⏳</div>';
      conText.textContent = "Synthesizing consensus...";
      taskCont.innerHTML = "";

      try {
        const res = await fetch(`${API_BASE}/api/projects-hub/${currentProjectId}/brainstorm`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({})
        });
        const data = await res.json();
        if (data.status === 'success') {
          sub.textContent = `Venture: ${data.project_name} • Squad Alignment`;
          conText.textContent = data.executive_summary || "Consensus reached on high-velocity pipeline.";

          // Render dialogue
          diaCont.innerHTML = (data.transcript || []).map(t => `
            <div class="p-2.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-xs space-y-1">
              <span class="font-bold text-indigo-600 dark:text-indigo-400 font-mono text-[11px]">${escapeHtml(t.speaker)}</span>
              <p class="text-slate-700 dark:text-slate-300 leading-relaxed">${escapeHtml(t.statement)}</p>
            </div>
          `).join('');

          // Render tasks
          taskCont.innerHTML = (data.assigned_tasks || []).map(t => `
            <div class="p-2 rounded-lg bg-slate-100 dark:bg-slate-900 text-[11px] flex items-center justify-between">
              <div>
                <span class="font-bold text-slate-800 dark:text-slate-200">${escapeHtml(t.title)}</span>
                <span class="text-slate-400 font-mono text-[10px] block">→ ${escapeHtml(t.assigned_to)}</span>
              </div>
              <span class="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-indigo-100 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-300 uppercase">${escapeHtml(t.priority)}</span>
            </div>
          `).join('');
        }
      } catch (e) {
        diaCont.innerHTML = `<div class="text-center py-6 text-rose-500 text-xs">Error conducting brainstorm: ${e.message}</div>`;
      }
    }

    function closeSquadBrainstormModal() {
      document.getElementById('squad-brainstorm-modal').classList.add('hidden');
    }

    // 2. Open & Manage Guardrails
    async function openGuardrailsModal() {
      document.getElementById('agency-guardrails-modal').classList.remove('hidden');
      await loadGuardrailsList();
    }

    function closeGuardrailsModal() {
      document.getElementById('agency-guardrails-modal').classList.add('hidden');
    }

    async function loadGuardrailsList() {
      const cont = document.getElementById('guardrails-list-container');
      cont.innerHTML = '<div class="text-center py-4 text-slate-400 text-xs">Loading active rules... ⏳</div>';
      try {
        const res = await fetch(`${API_BASE}/api/projects-hub/guardrails/list`);
        const data = await res.json();
        if (data.status === 'success' && data.guardrails) {
          if (data.guardrails.length === 0) {
            cont.innerHTML = '<div class="text-center py-6 text-slate-400 text-xs font-mono">No custom guardrails set yet. Add a rule above!</div>';
            return;
          }
          cont.innerHTML = data.guardrails.map(g => `
            <div class="p-3 rounded-2xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 flex items-start justify-between gap-3 text-xs">
              <div class="space-y-1">
                <div class="flex items-center gap-2">
                  <span class="font-bold text-slate-900 dark:text-white">${escapeHtml(g.rule_title)}</span>
                  <span class="px-2 py-0.5 rounded text-[9px] font-mono font-bold bg-emerald-100 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400 uppercase">${escapeHtml(g.enforcement_level || 'STRICT')}</span>
                  <span class="px-1.5 py-0.5 rounded text-[9px] font-mono bg-slate-200 dark:bg-slate-800 text-slate-500">${escapeHtml(g.category || 'WORKFLOW')}</span>
                </div>
                <p class="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed">${escapeHtml(g.rule_instruction)}</p>
              </div>
              <button onclick="deleteGuardrailRule('${g.id}')" class="text-slate-400 hover:text-rose-500 text-xs p-1" title="Delete Rule">✕</button>
            </div>
          `).join('');
        }
      } catch (e) {
        cont.innerHTML = `<div class="text-center py-4 text-rose-500 text-xs">Failed to load rules: ${e.message}</div>`;
      }
    }

    async function submitNewFounderRule() {
      const input = document.getElementById('input-new-rule-text');
      const val = input.value.trim();
      if (!val) return;

      try {
        const res = await fetch(`${API_BASE}/api/projects-hub/guardrails/create`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ rule_text: val })
        });
        const data = await res.json();
        if (data.status === 'success') {
          input.value = '';
          alert('✓ ' + data.message);
          await loadGuardrailsList();
        }
      } catch (e) {
        alert('Error saving rule: ' + e.message);
      }
    }

    async function deleteGuardrailRule(ruleId) {
      if (!confirm('Are you sure you want to remove this rule?')) return;
      try {
        const res = await fetch(`${API_BASE}/api/projects-hub/guardrails/${ruleId}`, {
          method: 'DELETE'
        });
        const data = await res.json();
        if (data.status === 'success') {
          await loadGuardrailsList();
        }
      } catch (e) {
        alert('Error deleting rule: ' + e.message);
      }
    }
'''
    if 'function triggerSquadBrainstormModal' not in html:
        html = html.replace('</script>\n</body>', ui_js + '\n</script>\n</body>', 1)

    with open("frontend/index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("✓ Successfully wired Squad Brainstorming & Zero-Mistake Guardrails UI into index.html!")

if __name__ == "__main__":
    wire_ui()
