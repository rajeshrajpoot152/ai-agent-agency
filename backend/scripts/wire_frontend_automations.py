import re

def enhance_frontend():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Add Auto-Hunt button in Leads Hub header
    target_leads_hdr_btn = '<button onclick="openAddLeadToProjectModal()"'
    new_leads_hdr_btn = '''<button id="btn-auto-hunt-leads" onclick="autoHuntLeadsForActiveProject()" class="px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs transition flex items-center gap-1.5 shadow-sm">
              <span>⚡</span> Auto-Hunt 5 Leads
            </button>
            <button onclick="openAddLeadToProjectModal()"'''

    if 'id="btn-auto-hunt-leads"' not in html:
        html = html.replace(target_leads_hdr_btn, new_leads_hdr_btn, 1)

    # 2. Add Market Spy Strip to Cockpit
    target_cockpit_strip = '<!-- 3. Short 2-Column Command Grid: 3D Squad + Impact Radar -->'
    market_spy_html = '''<!-- 2.5 Market & Competitor Spy Intelligence Bar -->
        <div id="cockpit-market-spy-bar" class="p-3 rounded-2xl bg-gradient-to-r from-slate-900 to-indigo-950 border border-indigo-500/30 text-white shadow-sm flex items-center justify-between gap-3 flex-wrap text-xs font-mono">
          <div class="flex items-center gap-2.5">
            <span class="text-base">🕵️</span>
            <div>
              <span class="font-bold text-indigo-300">Market & Competitor Spy:</span>
              <span id="cockpit-market-spy-text" class="text-slate-300 ml-1">Analyzing competitor pricing & search volume...</span>
            </div>
          </div>
          <span class="px-2 py-0.5 rounded text-[10px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-bold">● High Advantage</span>
        </div>

        <!-- 3. Short 2-Column Command Grid: 3D Squad + Impact Radar -->'''

    if 'id="cockpit-market-spy-bar"' not in html:
        html = html.replace(target_cockpit_strip, market_spy_html, 1)

    # 3. Add Invoice & UPI QR Modal
    invoice_qr_modal = '''
  <!-- ======================================================== -->
  <!-- MODAL: 1-CLICK GST INVOICE & UPI QR PAYMENT MACHINE       -->
  <!-- ======================================================== -->
  <div id="lead-invoice-qr-modal" class="hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 max-w-md w-full shadow-2xl space-y-4 animate-scaleIn">
      <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
        <div class="flex items-center gap-2">
          <span class="text-2xl">💳</span>
          <div>
            <h3 class="font-bold text-sm text-slate-900 dark:text-white">GST Invoice & UPI QR Machine</h3>
            <p id="inv-modal-client-name" class="text-[11px] text-slate-500">Generating invoice for Client</p>
          </div>
        </div>
        <button onclick="closeInvoiceQRModal()" class="text-slate-400 hover:text-slate-700 dark:hover:text-white text-base">✕</button>
      </div>

      <div class="space-y-3 text-xs">
        <div class="p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <div>
            <div class="text-[10px] font-mono text-slate-400">INVOICE NUMBER</div>
            <div id="inv-modal-number" class="font-bold text-slate-900 dark:text-white font-mono text-xs">INV-2026-XXXX</div>
          </div>
          <div class="text-right">
            <div class="text-[10px] font-mono text-slate-400">TOTAL PAYABLE (18% GST)</div>
            <div id="inv-modal-total" class="font-black text-emerald-600 dark:text-emerald-400 font-mono text-sm">₹0</div>
          </div>
        </div>

        <div class="flex flex-col items-center justify-center p-4 rounded-2xl bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 shadow-inner space-y-2">
          <img id="inv-modal-qr-img" src="" class="w-44 h-44 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm" alt="UPI QR Code" />
          <span class="text-[10px] font-mono text-slate-400">Scan using PhonePe / Google Pay / Paytm / UPI</span>
        </div>

        <div>
          <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">WhatsApp Payment Message</label>
          <textarea id="inv-modal-wa-text" rows="3" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-slate-900 dark:text-white text-[11px] font-mono leading-relaxed" readonly></textarea>
        </div>

        <div class="flex items-center gap-2 pt-2">
          <a id="inv-modal-wa-btn" href="#" target="_blank" class="flex-1 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs text-center shadow transition flex items-center justify-center gap-1.5">
            <span>📱</span> Send via WhatsApp
          </a>
          <button onclick="navigator.clipboard.writeText(document.getElementById('inv-modal-wa-text').value); alert('Payment message copied!');" class="px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-300 font-semibold text-xs transition">
            📋 Copy
          </button>
        </div>
      </div>
    </div>
  </div>
'''

    if 'id="lead-invoice-qr-modal"' not in html:
        html = html.replace('</body>', invoice_qr_modal + '\n</body>', 1)

    # 4. Enhance JavaScript
    js_automations = '''
    // ========================================================
    // AUTOMATIONS JAVASCRIPT CONTROLLERS
    // ========================================================
    
    // 1. Auto-Hunt 5 Verified Leads for Active Project
    async function autoHuntLeadsForActiveProject() {
      if (!currentProjectId) {
        alert('Please select an active project first.');
        return;
      }
      const btn = document.getElementById('btn-auto-hunt-leads');
      btn.disabled = true;
      btn.innerHTML = `<span>Hunting verified prospects...</span> <span class="animate-spin">⏳</span>`;

      try {
        const res = await fetch(`${API_BASE}/api/projects-hub/${currentProjectId}/leads/auto-hunt`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ count: 5, location: "India / Global" })
        });
        const data = await res.json();
        btn.disabled = false;
        btn.innerHTML = `<span>⚡</span> Auto-Hunt 5 Leads`;

        if (data.status === 'success') {
          alert('✓ ' + data.message);
          await selectProject(currentProjectId);
        } else {
          alert('Error: ' + data.message);
        }
      } catch (e) {
        btn.disabled = false;
        btn.innerHTML = `<span>⚡</span> Auto-Hunt 5 Leads`;
        alert('Auto-hunt error: ' + e.message);
      }
    }

    // 2. Open 1-Click Invoice & UPI QR Modal for any Lead
    async function openInvoiceQRForLead(leadId, clientName, dealValue) {
      if (!currentProjectId) return;
      document.getElementById('inv-modal-client-name').textContent = `Client: ${clientName}`;
      document.getElementById('lead-invoice-qr-modal').classList.remove('hidden');

      // Parse deal value amount
      let amt = 45000.0;
      if (dealValue) {
        const num = parseFloat(dealValue.replace(/[^0-9.]/g, ''));
        if (num && !isNaN(num)) amt = num;
      }

      try {
        const res = await fetch(`${API_BASE}/api/projects-hub/${currentProjectId}/leads/${leadId}/generate-invoice`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ amount: amt })
        });
        const data = await res.json();
        if (data.status === 'success') {
          document.getElementById('inv-modal-number').textContent = data.invoice_number;
          document.getElementById('inv-modal-total').textContent = `₹${data.total_amount.toLocaleString()}`;
          document.getElementById('inv-modal-qr-img').src = data.upi_qr_url;
          document.getElementById('inv-modal-wa-text').value = data.whatsapp_message;
          const waBtn = document.getElementById('inv-modal-wa-btn');
          if (data.whatsapp_direct_url) {
            waBtn.href = data.whatsapp_direct_url;
            waBtn.classList.remove('hidden');
          } else {
            waBtn.classList.add('hidden');
          }
        }
      } catch (e) {
        alert('Error generating invoice: ' + e.message);
      }
    }

    function closeInvoiceQRModal() {
      document.getElementById('lead-invoice-qr-modal').classList.add('hidden');
    }

    // 3. Load Market & Competitor Spy
    async function loadMarketSpyIntelligence() {
      if (!currentProjectId) return;
      const textEl = document.getElementById('cockpit-market-spy-text');
      if (!textEl) return;
      try {
        const res = await fetch(`${API_BASE}/api/projects-hub/${currentProjectId}/market-spy`);
        const data = await res.json();
        if (data.status === 'success' && data.alerts && data.alerts.length > 0) {
          textEl.textContent = data.alerts[0];
        }
      } catch (e) {
        console.error("Market spy error:", e);
      }
    }

    // Update renderFilteredLeadsTable to include Invoice & QR button
    const origRenderFilteredLeadsTable = renderFilteredLeadsTable;
    renderFilteredLeadsTable = function(leads) {
      const tbody = document.getElementById('project-leads-table-body');
      if (!tbody) return;

      if (leads.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center py-10 text-slate-400 text-xs font-mono">No matching leads found. Click 'Auto-Hunt 5 Leads' above!</td></tr>`;
        return;
      }

      tbody.innerHTML = leads.map(l => {
        const phone = l.whatsapp_number || l.mobile_number || '';
        const cleanPhone = phone.replace(/[^0-9]/g, '');
        const waUrl = cleanPhone ? `https://wa.me/${cleanPhone}` : '#';
        const mailUrl = l.email_address ? `mailto:${l.email_address}` : '#';
        const tgUrl = l.telegram_handle ? `https://t.me/${l.telegram_handle.replace('@', '')}` : '#';

        let statusBadge = '<span class="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">NEW</span>';
        if (l.status === 'in_discussion') {
          statusBadge = '<span class="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">IN DISCUSSION</span>';
        } else if (l.status === 'won') {
          statusBadge = '<span class="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-50 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">DEAL WON</span>';
        }

        return `
          <tr class="hover:bg-slate-50 dark:hover:bg-slate-900/40 transition">
            <td class="py-3 px-4">
              <div class="font-bold text-slate-900 dark:text-white">${escapeHtml(l.full_name)}</div>
              <div class="text-[11px] text-slate-400 font-mono">${escapeHtml(l.business_name || 'Individual Client')}</div>
            </td>
            <td class="py-3 px-4">
              <div>${statusBadge}</div>
              <div class="text-[11px] font-mono font-bold text-slate-700 dark:text-slate-300 mt-1">${escapeHtml(l.deal_value || 'Flexible')}</div>
            </td>
            <td class="py-3 px-4">
              <div class="flex items-center gap-1.5 flex-wrap">
                ${cleanPhone ? `<a href="${waUrl}" target="_blank" class="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 text-[10px] font-mono font-bold hover:underline">📱 WhatsApp</a>` : ''}
                ${l.email_address ? `<a href="${mailUrl}" class="px-2 py-0.5 rounded bg-sky-50 text-sky-700 dark:bg-sky-950 dark:text-sky-300 text-[10px] font-mono font-bold hover:underline">✉️ Email</a>` : ''}
                ${l.telegram_handle ? `<a href="${tgUrl}" target="_blank" class="px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300 text-[10px] font-mono font-bold hover:underline">✈️ Telegram</a>` : ''}
              </div>
            </td>
            <td class="py-3 px-4 max-w-xs">
              <p class="text-[11px] text-slate-600 dark:text-slate-400 line-clamp-2 leading-relaxed">${escapeHtml(l.notes || 'No notes added yet.')}</p>
            </td>
            <td class="py-3 px-4 text-right">
              <div class="flex items-center justify-end gap-1.5">
                <button onclick="openSmartReplyModal('${l.id}', '${escapeAttr(l.full_name)}', '${escapeAttr(l.notes || '')}')" class="px-2.5 py-1.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:opacity-95 text-white font-bold text-xs shadow-sm transition inline-flex items-center gap-1" title="Deep Project-Aware Reply">
                  <span>🤖</span> Reply
                </button>
                <button onclick="openInvoiceQRForLead('${l.id}', '${escapeAttr(l.full_name)}', '${escapeAttr(l.deal_value || '₹45,000')}')" class="px-2.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-sm transition inline-flex items-center gap-1" title="Generate GST Invoice & UPI QR">
                  <span>💳</span> Invoice
                </button>
              </div>
            </td>
          </tr>
        `;
      }).join('');
    };
'''

    if 'function autoHuntLeadsForActiveProject' not in html:
        html = html.replace('</script>\n</body>', js_automations + '\n</script>\n</body>', 1)

    with open("frontend/index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("✓ Successfully enhanced frontend with all 4 automations UI!")

if __name__ == "__main__":
    enhance_frontend()
