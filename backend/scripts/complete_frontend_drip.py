import re

def update_frontend():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Add WhatsApp Drip button next to Auto-Hunt button
    if 'id="btn-view-drip"' not in html:
        target = 'id="btn-auto-hunt-leads"'
        btn_drip_html = '''<button id="btn-view-drip" onclick="openDripSequenceModal()" class="px-3.5 py-1.5 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs transition flex items-center gap-1.5 shadow-sm">
              <span>🔁</span> 3-Step Drip
            </button>\n            '''
        html = html.replace('<button id="btn-auto-hunt-leads"', btn_drip_html + '<button id="btn-auto-hunt-leads"', 1)

    # 2. Add Drip Sequence Modal
    drip_modal_html = '''
  <!-- ======================================================== -->
  <!-- MODAL: 3-STEP WHATSAPP DRIP SEQUENCES                   -->
  <!-- ======================================================== -->
  <div id="lead-drip-modal" class="hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 max-w-xl w-full shadow-2xl space-y-4 animate-scaleIn">
      <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
        <div class="flex items-center gap-2">
          <span class="text-2xl">🔁</span>
          <div>
            <h3 class="font-bold text-sm text-slate-900 dark:text-white">Smart 3-Step WhatsApp Drip Machine</h3>
            <p id="drip-modal-project-name" class="text-[11px] text-slate-500 font-mono">Tailored follow-up sequences for higher conversions</p>
          </div>
        </div>
        <button onclick="closeDripSequenceModal()" class="text-slate-400 hover:text-slate-700 dark:hover:text-white text-base">✕</button>
      </div>

      <div id="drip-modal-steps-container" class="space-y-3 max-h-[60vh] overflow-y-auto pr-1">
        <!-- Steps dynamically populated -->
      </div>
    </div>
  </div>
'''
    if 'id="lead-drip-modal"' not in html:
        html = html.replace('</body>', drip_modal_html + '\n</body>', 1)

    # 3. Add JS functions for Drip Modal
    drip_js = '''
    // Open & Load 3-Step Drip Sequences
    async function openDripSequenceModal() {
      if (!currentProjectId) {
        alert('Please select an active project first.');
        return;
      }
      const modal = document.getElementById('lead-drip-modal');
      const container = document.getElementById('drip-modal-steps-container');
      const projLabel = document.getElementById('drip-modal-project-name');
      modal.classList.remove('hidden');
      container.innerHTML = '<div class="text-center py-6 text-slate-400 text-xs">Generating 3-step sequence for this venture... ⏳</div>';

      try {
        const res = await fetch(`${API_BASE}/api/projects-hub/${currentProjectId}/outreach/drip-sequence`);
        const data = await res.json();
        if (data.status === 'success' && data.steps) {
          projLabel.textContent = `Venture: ${data.project_name} • High Conversion Sequence`;
          container.innerHTML = data.steps.map(s => `
            <div class="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 space-y-2">
              <div class="flex items-center justify-between">
                <span class="font-bold text-xs text-indigo-600 dark:text-indigo-400 font-mono">${escapeHtml(s.label)}</span>
                <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400">${escapeHtml(s.timing)}</span>
              </div>
              <div class="text-[11px] font-semibold text-slate-800 dark:text-slate-200">${escapeHtml(s.subject)}</div>
              <p class="text-[11px] text-slate-600 dark:text-slate-400 font-mono bg-white dark:bg-slate-900 p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 leading-relaxed">${escapeHtml(s.body)}</p>
              <div class="flex justify-end pt-1">
                <button onclick="navigator.clipboard.writeText('${escapeAttr(s.body)}'); alert('Sequence copied!');" class="px-2.5 py-1 rounded-lg bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-300 hover:bg-indigo-100 text-[10px] font-bold font-mono transition">
                  📋 Copy Message
                </button>
              </div>
            </div>
          `).join('');
        }
      } catch (e) {
        container.innerHTML = `<div class="text-center py-6 text-rose-500 text-xs">Failed to load drip sequence: ${e.message}</div>`;
      }
    }

    function closeDripSequenceModal() {
      document.getElementById('lead-drip-modal').classList.add('hidden');
    }
'''
    if 'function openDripSequenceModal' not in html:
        html = html.replace('</script>\n</body>', drip_js + '\n</script>\n</body>', 1)

    # 4. Ensure selectProject calls loadMarketSpyIntelligence
    if 'loadMarketSpyIntelligence();' not in html:
        target_select = "renderLeadsHubTab(data);"
        replacement_select = "renderLeadsHubTab(data);\n          loadMarketSpyIntelligence();"
        html = html.replace(target_select, replacement_select, 1)

    with open("frontend/index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("✓ Successfully updated frontend with 3-Step WhatsApp Drip modal and automated Market Spy trigger!")

if __name__ == "__main__":
    update_frontend()
