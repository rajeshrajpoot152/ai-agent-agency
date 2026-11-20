import re

with open("frontend/index.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Modals to add before line 1997:
modals_html = """
  <!-- ======================================================== -->
  <!-- PROJECT-AWARE SMART REPLY MODAL (POSITIVE VS NEGATIVE)    -->
  <!-- ======================================================== -->
  <div id="smart-reply-modal" class="hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 max-w-xl w-full shadow-2xl space-y-4">
      <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
        <div class="flex items-center gap-2.5">
          <span class="text-2xl">🤖</span>
          <div>
            <h3 class="font-bold text-sm text-slate-900 dark:text-white">Project-Aware Smart Reply Engine</h3>
            <p class="text-[11px] text-slate-500">100% deep project understanding with zero cross-tool leakage</p>
          </div>
        </div>
        <button onclick="closeSmartReplyModal()" class="text-slate-400 hover:text-slate-700 dark:hover:text-white text-base">✕</button>
      </div>

      <!-- Project Context Intelligence Banner -->
      <div id="smart-reply-context-banner" class="p-3.5 rounded-2xl bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800 space-y-1 text-xs">
        <div class="flex items-center justify-between">
          <span class="font-bold text-indigo-700 dark:text-indigo-300 font-mono" id="smart-reply-proj-name">Active Project</span>
          <span class="px-2 py-0.5 rounded text-[10px] bg-indigo-600 text-white font-mono font-bold" id="smart-reply-disc-badge">Max 10% Discount</span>
        </div>
        <p class="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed" id="smart-reply-pricing-info">Pricing & Rules loaded from project database.</p>
      </div>

      <!-- Inbound Client Inquiry / Message -->
      <div class="space-y-1.5 text-xs">
        <div class="flex items-center justify-between font-semibold text-slate-700 dark:text-slate-300">
          <span>Client Inquiry / Message:</span>
          <span id="smart-reply-client-name" class="font-bold text-slate-900 dark:text-white font-mono">Client Name</span>
        </div>
        <textarea id="smart-reply-client-msg" rows="3" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-3 text-slate-900 dark:text-white text-xs leading-relaxed" placeholder="Client inquiry, objection, or discount request..."></textarea>
      </div>

      <!-- Sentiment Mode Selector -->
      <div class="space-y-1.5 text-xs">
        <label class="block font-semibold text-slate-700 dark:text-slate-300">Reply Stance & Sentiment Strategy:</label>
        <div class="grid grid-cols-3 gap-2">
          <button type="button" onclick="setReplySentimentMode('positive', this)" class="reply-mode-btn p-2 rounded-xl border border-emerald-500 bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 font-bold text-xs flex flex-col items-center gap-0.5">
            <span>🟢 Positive</span>
            <span class="text-[9px] font-normal opacity-80">Accept & Next Steps</span>
          </button>
          <button type="button" onclick="setReplySentimentMode('negative', this)" class="reply-mode-btn p-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-bold text-xs flex flex-col items-center gap-0.5">
            <span>🔴 Boundary</span>
            <span class="text-[9px] font-normal opacity-80">Refuse & Counter</span>
          </button>
          <button type="button" onclick="setReplySentimentMode('auto', this)" class="reply-mode-btn p-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-bold text-xs flex flex-col items-center gap-0.5">
            <span>⚡ Auto</span>
            <span class="text-[9px] font-normal opacity-80">AI Decision</span>
          </button>
        </div>
      </div>

      <!-- Channel Selector -->
      <div class="flex items-center justify-between text-xs pt-1">
        <span class="font-semibold text-slate-600 dark:text-slate-400">Target Channel:</span>
        <div class="flex gap-2">
          <label class="flex items-center gap-1 cursor-pointer font-medium"><input type="radio" name="reply-channel" value="whatsapp" checked> 📱 WhatsApp</label>
          <label class="flex items-center gap-1 cursor-pointer font-medium"><input type="radio" name="reply-channel" value="email"> ✉️ Email</label>
          <label class="flex items-center gap-1 cursor-pointer font-medium"><input type="radio" name="reply-channel" value="telegram"> ✈️ Telegram</label>
        </div>
      </div>

      <button id="btn-generate-smart-reply" onclick="generateSmartReplyAction()" class="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs shadow-md transition flex items-center justify-center gap-2">
        <span>⚡</span> Generate Context-Aware Professional Reply
      </button>

      <!-- Output Reply Box -->
      <div id="smart-reply-output-box" class="hidden space-y-2 pt-2 border-t border-slate-100 dark:border-slate-800">
        <div class="flex items-center justify-between text-xs">
          <span class="font-bold text-emerald-600 dark:text-emerald-400">Generated Reply (Ready to Send):</span>
          <button onclick="copySmartReplyText()" class="px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-[11px] font-semibold">📋 Copy</button>
        </div>
        <textarea id="smart-reply-result-text" rows="4" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-3 text-slate-900 dark:text-white text-xs leading-relaxed font-sans"></textarea>
        
        <div class="flex items-center justify-between gap-2">
          <a id="smart-reply-send-whatsapp-btn" href="#" target="_blank" class="flex-1 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs text-center shadow-md transition flex items-center justify-center gap-1.5">
            <span>📱</span> Send via WhatsApp Direct
          </a>
          <button onclick="dispatchSmartReplyRecord()" class="py-2 px-4 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-bold text-xs transition">
            Log Contacted
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- ======================================================== -->
  <!-- 1-CLICK CREATE PROJECT / TOOL / VERTICAL MODAL           -->
  <!-- ======================================================== -->
  <div id="create-project-modal" class="hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 max-w-lg w-full shadow-2xl space-y-4">
      <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
        <div class="flex items-center gap-2">
          <span class="text-2xl">✨</span>
          <div>
            <h3 class="font-bold text-sm text-slate-900 dark:text-white">Create New Project or Tool Site</h3>
            <p class="text-[11px] text-slate-500">Add SaaS Tool, Real Estate, Jewelry, or Custom CRM venture</p>
          </div>
        </div>
        <button onclick="closeCreateProjectModal()" class="text-slate-400 hover:text-slate-700 dark:hover:text-white text-base">✕</button>
      </div>

      <div class="space-y-3 text-xs">
        <div>
          <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Project / Brand Name *</label>
          <input id="new-proj-name" type="text" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-slate-900 dark:text-white font-bold" placeholder="e.g. LeadPulse AI, Luxe Gemstones, Urban Estates">
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Project Category *</label>
            <select id="new-proj-type" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-slate-900 dark:text-white font-bold">
              <option value="tool_website">Tool Website (SaaS)</option>
              <option value="it_company">IT Company Website</option>
              <option value="real_estate">Real Estate Platform</option>
              <option value="jewelry">Jewelry Brand</option>
              <option value="custom_crm">Custom CRM Platform</option>
              <option value="other">Other Venture</option>
            </select>
          </div>
          <div>
            <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Industry *</label>
            <input id="new-proj-industry" type="text" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-slate-900 dark:text-white" placeholder="e.g. Luxury Real Estate, AI Marketing">
          </div>
        </div>

        <div>
          <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Tagline / Mission *</label>
          <input id="new-proj-tagline" type="text" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-slate-900 dark:text-white" placeholder="e.g. 24/7 AI Prospecting for High-Growth Startups">
        </div>

        <div>
          <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Pricing & Packaging Structure</label>
          <input id="new-proj-pricing" type="text" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-slate-900 dark:text-white font-mono" placeholder="e.g. Starter: $49/mo, Pro: $199/mo. Max discount: 10%">
        </div>
      </div>

      <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-100 dark:border-slate-800">
        <button onclick="closeCreateProjectModal()" class="px-4 py-2 rounded-xl text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 font-semibold text-xs">Cancel</button>
        <button id="btn-submit-create-project" onclick="submitCreateProjectAction()" class="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs shadow-md transition flex items-center gap-1.5">
          <span>🚀</span> Create Project & Assign 3D Squad
        </button>
      </div>
    </div>
  </div>

  <!-- ======================================================== -->
  <!-- 1-CLICK ADD LEAD TO ACTIVE PROJECT MODAL                 -->
  <!-- ======================================================== -->
  <div id="add-project-lead-modal" class="hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 max-w-md w-full shadow-2xl space-y-4">
      <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
        <div class="flex items-center gap-2">
          <span class="text-2xl">👤</span>
          <div>
            <h3 class="font-bold text-sm text-slate-900 dark:text-white">Add Lead to Project</h3>
            <p class="text-[11px] text-slate-500" id="add-lead-proj-target">Strictly isolated to active project</p>
          </div>
        </div>
        <button onclick="closeAddLeadModal()" class="text-slate-400 hover:text-slate-700 dark:hover:text-white text-base">✕</button>
      </div>

      <div class="space-y-3 text-xs">
        <div>
          <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Full Name *</label>
          <input id="lead-full-name" type="text" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-slate-900 dark:text-white font-bold" placeholder="e.g. Siddharth Rao">
        </div>
        <div>
          <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Business / Brand Name</label>
          <input id="lead-business-name" type="text" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-slate-900 dark:text-white" placeholder="e.g. Rao Global Exports">
        </div>
        <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">WhatsApp / Phone *</label>
            <input id="lead-phone" type="text" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-slate-900 dark:text-white font-mono" placeholder="+919876543210">
          </div>
          <div>
            <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Deal Value</label>
            <input id="lead-deal-val" type="text" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-slate-900 dark:text-white font-mono" placeholder="₹1,50,000">
          </div>
        </div>
        <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Email</label>
            <input id="lead-email" type="email" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-slate-900 dark:text-white font-mono" placeholder="siddharth@rao.com">
          </div>
          <div>
            <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Telegram Handle</label>
            <input id="lead-telegram" type="text" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-slate-900 dark:text-white font-mono" placeholder="@siddharthrao">
          </div>
        </div>
        <div>
          <label class="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Project Scope & Discussion Notes</label>
          <textarea id="lead-notes" rows="2" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-2.5 text-slate-900 dark:text-white text-xs" placeholder="Client requirement, timeline, and current stage..."></textarea>
        </div>
      </div>

      <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-100 dark:border-slate-800">
        <button onclick="closeAddLeadModal()" class="px-4 py-2 rounded-xl text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 font-semibold text-xs">Cancel</button>
        <button id="btn-submit-add-lead" onclick="submitAddLeadAction()" class="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-md transition flex items-center gap-1.5">
          <span>➕</span> Save to Isolated Database
        </button>
      </div>
    </div>
  </div>
"""

# Insert modals right before "  <!-- ======================================================== -->\n  <!-- 3. JAVASCRIPT CONTROLLER -->"
target_marker = "  <!-- ======================================================== -->\n  <!-- 3. JAVASCRIPT CONTROLLER -->"
if target_marker in content:
    content = content.replace(target_marker, modals_html + "\n" + target_marker)
    print("✓ Inserted Smart Reply, Create Project, and Add Lead modals.")
else:
    print("Warning: target_marker not found for modals!")

with open("frontend/index.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Updated frontend/index.html with modals.")
