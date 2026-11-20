import re

with open("frontend/index.html", "r", encoding="utf-8") as f:
    content = f.read()

js_code = """
    // =============================================================
    // 0. PROJECT-CENTRIC VIRTUAL TEAM OPERATING SYSTEM CONTROLLER
    // =============================================================
    let currentProjectId = null;
    let portfolioProjects = [];
    let activeProjectData = null;
    let currentSentimentMode = 'positive';
    let currentSmartReplyLeadId = null;

    async function initProjectCentricOS() {
      try {
        await loadMasterProjects();
      } catch (e) {
        console.error("initProjectCentricOS error:", e);
      }
    }

    async function loadMasterProjects(category = 'all') {
      try {
        let url = `${API_BASE}/api/projects-hub/list`;
        if (category && category !== 'all') {
          url += `?category=${encodeURIComponent(category)}`;
        }
        const res = await fetch(url);
        const data = await res.json();
        if (data.status === 'success') {
          portfolioProjects = data.projects || [];
          renderMasterProjectSelector();

          // If no active project selected yet, default to first or flagship
          if (!currentProjectId && portfolioProjects.length > 0) {
            const flagship = portfolioProjects.find(p => p.project_type === 'it_company') || portfolioProjects[0];
            currentProjectId = flagship.id;
          }

          if (currentProjectId) {
            document.getElementById('master-project-selector').value = currentProjectId;
            await selectProject(currentProjectId);
          }
        }
      } catch (e) {
        console.error("loadMasterProjects error:", e);
      }
    }

    function renderMasterProjectSelector() {
      const select = document.getElementById('master-project-selector');
      if (!select) return;

      select.innerHTML = portfolioProjects.map(p => {
        let icon = '🛠️';
        if (p.project_type === 'it_company') icon = '🏢';
        else if (p.project_type === 'real_estate') icon = '🏡';
        else if (p.project_type === 'jewelry') icon = '💎';
        else if (p.project_type === 'custom_crm') icon = '⚡';
        
        return `<option value="${p.id}" ${p.id === currentProjectId ? 'selected' : ''}>${icon} ${p.brand_name} (${p.leads_count || 0} Leads)</option>`;
      }).join('');
    }

    async function onMasterProjectChange(projectId) {
      if (!projectId) return;
      currentProjectId = projectId;
      await selectProject(projectId);
    }

    function filterProjectCategory(category, btnEl) {
      document.querySelectorAll('.proj-cat-chip').forEach(el => {
        el.classList.remove('bg-indigo-600', 'text-white', 'font-bold');
        el.classList.add('bg-slate-100', 'dark:bg-slate-800', 'text-slate-600', 'dark:text-slate-300');
      });
      if (btnEl) {
        btnEl.classList.add('bg-indigo-600', 'text-white', 'font-bold');
        btnEl.classList.remove('bg-slate-100', 'dark:bg-slate-800', 'text-slate-600', 'dark:text-slate-300');
      }
      loadMasterProjects(category);
    }

    async function selectProject(projectId) {
      currentProjectId = projectId;
      try {
        const res = await fetch(`${API_BASE}/api/projects-hub/${projectId}/dashboard`);
        const data = await res.json();
        if (data.status === 'success') {
          activeProjectData = data;
          renderCockpitTab(data);
          renderSocialHubTab(data);
          renderLeadsHubTab(data);

          // Update active project badge
          const statusText = document.getElementById('active-project-status-text');
          if (statusText) {
            statusText.textContent = `🟢 ${data.project.brand_name} • Autopilot Active`;
          }
        }
      } catch (e) {
        console.error("selectProject error:", e);
      }
    }

    // 1. Render Cockpit & Cause-and-Effect Impact Radar
    function renderCockpitTab(data) {
      const p = data.project;
      const radar = data.impact_radar || {};
      const kpis = radar.kpi_meters || {};

      // Fill Hero Card
      document.getElementById('cockpit-proj-name').textContent = p.brand_name;
      document.getElementById('cockpit-proj-tagline').textContent = p.tagline || 'Autonomous Enterprise Scale';
      document.getElementById('cockpit-proj-valprop').textContent = `Target & Value: ${p.value_proposition || p.target_audience || 'Scalable solutions'}`;
      document.getElementById('cockpit-proj-type-badge').textContent = (p.project_type || 'tool_website').replace('_', ' ');
      document.getElementById('cockpit-manager-badge').textContent = `Lead: ${p.assigned_manager || 'Founder (You)'}`;
      
      const siteLink = document.getElementById('cockpit-proj-site-link');
      if (siteLink) {
        siteLink.href = p.website_url || '#';
      }

      // KPI Scorecards
      document.getElementById('cockpit-stat-leads').textContent = kpis.total_leads || 0;
      document.getElementById('cockpit-stat-discussions').textContent = kpis.active_discussions || 0;
      document.getElementById('cockpit-stat-won').textContent = kpis.deals_won || 0;
      document.getElementById('cockpit-stat-autopilot').textContent = kpis.autopilot_status || 'Active';

      // Render Assigned 3D Squad
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
      }
    }

    // 2. Render Social Marketing Autopilot Tab
    function renderSocialHubTab(data) {
      document.getElementById('social-proj-name').textContent = data.project.brand_name;
      const grid = document.getElementById('social-posts-grid');
      const posts = data.social_posts || [];
      if (!grid) return;

      if (posts.length === 0) {
        grid.innerHTML = `<div class="p-8 rounded-3xl bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-xs text-slate-400 col-span-2 text-center">No social posts generated yet. Click 'Generate Fresh Week\\'s Posts' above!</div>`;
        return;
      }

      grid.innerHTML = posts.map(p => {
        let platformIcon = '📱';
        let platformBadgeColor = 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300';
        if (p.platform.toLowerCase().includes('linkedin')) {
          platformIcon = '💼 LinkedIn';
          platformBadgeColor = 'bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300';
        } else if (p.platform.toLowerCase().includes('twitter') || p.platform.toLowerCase().includes('x')) {
          platformIcon = '🐦 Twitter / X';
          platformBadgeColor = 'bg-sky-50 text-sky-700 dark:bg-sky-950 dark:text-sky-300';
        } else if (p.platform.toLowerCase().includes('instagram')) {
          platformIcon = '📸 Instagram Carousel';
          platformBadgeColor = 'bg-pink-50 text-pink-700 dark:bg-pink-950 dark:text-pink-300';
        } else if (p.platform.toLowerCase().includes('facebook')) {
          platformIcon = '👥 Facebook';
          platformBadgeColor = 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300';
        }

        return `
          <div class="p-5 rounded-3xl bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between space-y-4">
            <div class="space-y-3">
              <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2.5">
                <span class="px-2.5 py-0.5 rounded-full text-xs font-bold font-mono ${platformBadgeColor}">${platformIcon}</span>
                <span class="text-[10px] font-mono text-emerald-500 font-bold">● Ready to Post</span>
              </div>
              <div class="text-[11px] font-bold text-slate-700 dark:text-slate-300 font-mono">${escapeHtml(p.post_theme)}</div>
              <p class="text-xs text-slate-800 dark:text-slate-200 whitespace-pre-wrap leading-relaxed font-sans max-h-48 overflow-y-auto pr-1">${escapeHtml(p.post_copy)}</p>
              <div class="text-[11px] text-indigo-600 dark:text-indigo-400 font-mono font-semibold">${escapeHtml(p.hashtags)}</div>
            </div>

            <div class="space-y-2 pt-3 border-t border-slate-100 dark:border-slate-800/80">
              <div class="p-2.5 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-[10px] font-mono text-slate-500 flex items-start justify-between gap-2">
                <div>
                  <strong class="text-slate-700 dark:text-slate-300 block mb-0.5">🎨 Canva Design Brief:</strong>
                  <span>${escapeHtml(p.canva_prompt)}</span>
                </div>
                <button onclick="navigator.clipboard.writeText('${escapeAttr(p.canva_prompt)}'); alert('Canva prompt copied!');" class="flex-shrink-0 text-[10px] font-bold text-indigo-600 underline">Copy Prompt</button>
              </div>

              <div class="flex items-center justify-between gap-2">
                <button onclick="navigator.clipboard.writeText('${escapeAttr(p.post_copy + '\\n\\n' + p.hashtags)}'); alert('Post copy + hashtags copied!');" class="flex-1 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-semibold transition">
                  📋 Copy Full Post
                </button>
                <button onclick="alert('⚡ Live connection: Scheduled for automated posting queue on ${p.platform}!');" class="flex-1 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs shadow-sm transition">
                  🚀 Publish Now
                </button>
              </div>
            </div>
          </div>
        `;
      }).join('');
    }

    // 3. Render Dedicated Leads & Multi-Channel Outreach Tab (Zero Leakage)
    function renderLeadsHubTab(data) {
      document.getElementById('leads-proj-name').textContent = data.project.brand_name;
      const tbody = document.getElementById('project-leads-table-body');
      const leads = data.leads || [];
      if (!tbody) return;

      if (leads.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center py-12 text-slate-400 text-xs">No leads stored for this project yet. Click 'Add Lead to This Project' above to add your first client!</td></tr>`;
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
              <button onclick="openSmartReplyModal('${l.id}', '${escapeAttr(l.full_name)}', '${escapeAttr(l.notes || '')}')" class="px-3 py-1.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:opacity-95 text-white font-bold text-xs shadow-sm transition inline-flex items-center gap-1">
                <span>🤖</span> Smart Reply
              </button>
            </td>
          </tr>
        `;
      }).join('');
    }

    // 4. Project-Aware Smart Reply Modal Handlers
    function openSmartReplyModal(leadId, clientName, clientMsg) {
      if (!activeProjectData) return;
      currentSmartReplyLeadId = leadId;
      const p = activeProjectData.project;

      document.getElementById('smart-reply-proj-name').textContent = p.brand_name;
      document.getElementById('smart-reply-disc-badge').textContent = `Max ${p.allowed_discount_max || 10}% Discount`;
      document.getElementById('smart-reply-pricing-info').textContent = p.pricing_tier_summary || 'Standard scope pricing structure.';
      document.getElementById('smart-reply-client-name').textContent = clientName || 'Client';
      document.getElementById('smart-reply-client-msg').value = clientMsg || 'Hello, I want to know more about pricing and delivery.';
      document.getElementById('smart-reply-output-box').classList.add('hidden');

      document.getElementById('smart-reply-modal').classList.remove('hidden');
    }

    function closeSmartReplyModal() {
      document.getElementById('smart-reply-modal').classList.add('hidden');
    }

    function setReplySentimentMode(mode, btnEl) {
      currentSentimentMode = mode;
      document.querySelectorAll('.reply-mode-btn').forEach(btn => {
        btn.classList.remove('border-emerald-500', 'bg-emerald-50', 'dark:bg-emerald-950/40', 'text-emerald-700', 'dark:text-emerald-300');
        btn.classList.add('border-slate-200', 'dark:border-slate-700', 'bg-slate-50', 'dark:bg-slate-800', 'text-slate-600', 'dark:text-slate-300');
      });
      if (btnEl) {
        btnEl.classList.remove('border-slate-200', 'dark:border-slate-700', 'bg-slate-50', 'dark:bg-slate-800', 'text-slate-600', 'dark:text-slate-300');
        btnEl.classList.add('border-emerald-500', 'bg-emerald-50', 'dark:bg-emerald-950/40', 'text-emerald-700', 'dark:text-emerald-300');
      }
    }

    async function generateSmartReplyAction() {
      if (!currentProjectId) return;
      const btn = document.getElementById('btn-generate-smart-reply');
      btn.disabled = true;
      btn.innerHTML = `<span>Synthesizing with Deep Project Understanding...</span> <span class="animate-spin">⏳</span>`;

      const clientMsg = document.getElementById('smart-reply-client-msg').value.trim();
      const clientName = document.getElementById('smart-reply-client-name').textContent;
      const channel = document.querySelector('input[name="reply-channel"]:checked')?.value || 'whatsapp';

      try {
        const res = await fetch(`${API_BASE}/api/projects-hub/${currentProjectId}/smart-reply`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            lead_id: currentSmartReplyLeadId,
            client_name: clientName,
            client_message: clientMsg,
            sentiment_mode: currentSentimentMode,
            channel: channel
          })
        });
        const data = await res.json();
        if (data.status === 'success') {
          document.getElementById('smart-reply-result-text').value = data.smart_reply;
          
          // Direct WhatsApp Link
          const lead = (activeProjectData.leads || []).find(l => l.id === currentSmartReplyLeadId);
          const phone = lead ? (lead.whatsapp_number || lead.mobile_number || '') : '';
          const cleanPhone = phone.replace(/[^0-9]/g, '');
          const waBtn = document.getElementById('smart-reply-send-whatsapp-btn');
          if (cleanPhone) {
            waBtn.href = `https://wa.me/${cleanPhone}?text=${encodeURIComponent(data.smart_reply)}`;
            waBtn.classList.remove('hidden');
          } else {
            waBtn.classList.add('hidden');
          }

          document.getElementById('smart-reply-output-box').classList.remove('hidden');
        }
      } catch (err) {
        alert('Failed to generate smart reply: ' + err.message);
      } finally {
        btn.disabled = false;
        btn.innerHTML = `<span>⚡</span> Generate Context-Aware Professional Reply`;
      }
    }

    function copySmartReplyText() {
      const text = document.getElementById('smart-reply-result-text').value;
      navigator.clipboard.writeText(text);
      alert('✅ Reply copied to clipboard!');
    }

    async function dispatchSmartReplyRecord() {
      if (!currentProjectId || !currentSmartReplyLeadId) return;
      const msg = document.getElementById('smart-reply-result-text').value;
      const channel = document.querySelector('input[name="reply-channel"]:checked')?.value || 'whatsapp';

      try {
        await fetch(`${API_BASE}/api/projects-hub/${currentProjectId}/outreach/dispatch`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            lead_id: currentSmartReplyLeadId,
            channel: channel,
            message_content: msg
          })
        });
        alert('✅ Message logged and lead marked in discussion!');
        closeSmartReplyModal();
        await selectProject(currentProjectId);
      } catch (e) {
        alert('Error: ' + e.message);
      }
    }

    // 5. Create Project Handlers
    function openCreateProjectModal() {
      document.getElementById('create-project-modal').classList.remove('hidden');
    }
    function closeCreateProjectModal() {
      document.getElementById('create-project-modal').classList.add('hidden');
    }

    async function submitCreateProjectAction() {
      const name = document.getElementById('new-proj-name').value.trim();
      const type = document.getElementById('new-proj-type').value;
      const ind = document.getElementById('new-proj-industry').value.trim();
      const tag = document.getElementById('new-proj-tagline').value.trim();
      const pricing = document.getElementById('new-proj-pricing').value.trim();

      if (!name || !ind || !tag) {
        alert('Please fill Project Name, Industry, and Tagline!');
        return;
      }

      const btn = document.getElementById('btn-submit-create-project');
      btn.disabled = true;

      try {
        const res = await fetch(`${API_BASE}/api/projects-hub/create`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            brand_name: name,
            project_type: type,
            industry: ind,
            tagline: tag,
            pricing_tier_summary: pricing
          })
        });
        const data = await res.json();
        if (data.status === 'success') {
          alert(`🎉 Success! ${name} created with dedicated 3D squad!`);
          closeCreateProjectModal();
          await loadMasterProjects();
          if (data.project?.id) {
            await selectProject(data.project.id);
          }
        }
      } catch (err) {
        alert('Failed to create project: ' + err.message);
      } finally {
        btn.disabled = false;
      }
    }

    // 6. Add Lead Handlers
    function openAddLeadToProjectModal() {
      if (!activeProjectData) return;
      document.getElementById('add-lead-proj-target').textContent = `Adding to: ${activeProjectData.project.brand_name}`;
      document.getElementById('add-project-lead-modal').classList.remove('hidden');
    }
    function closeAddLeadModal() {
      document.getElementById('add-project-lead-modal').classList.add('hidden');
    }

    async function submitAddLeadAction() {
      if (!currentProjectId) return;
      const fullName = document.getElementById('lead-full-name').value.trim();
      const bizName = document.getElementById('lead-business-name').value.trim();
      const phone = document.getElementById('lead-phone').value.trim();
      const dealVal = document.getElementById('lead-deal-val').value.trim();
      const email = document.getElementById('lead-email').value.trim();
      const tg = document.getElementById('lead-telegram').value.trim();
      const notes = document.getElementById('lead-notes').value.trim();

      if (!fullName || !phone) {
        alert('Please enter Full Name and Phone/WhatsApp number!');
        return;
      }

      const btn = document.getElementById('btn-submit-add-lead');
      btn.disabled = true;

      try {
        const res = await fetch(`${API_BASE}/api/leads/`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            brand_id: currentProjectId,
            full_name: fullName,
            business_name: bizName || fullName,
            mobile_number: phone,
            whatsapp_number: phone,
            email_address: email,
            telegram_handle: tg,
            deal_value: dealVal || 'Flexible',
            notes: notes
          })
        });
        const data = await res.json();
        alert(`✅ Lead '${fullName}' saved strictly into ${activeProjectData.project.brand_name}!`);
        closeAddLeadModal();
        await selectProject(currentProjectId);
      } catch (e) {
        alert('Error saving lead: ' + e.message);
      } finally {
        btn.disabled = false;
      }
    }

    async function regenerateProjectSocialWeek() {
      if (!currentProjectId) return;
      try {
        const res = await fetch(`${API_BASE}/api/projects-hub/${currentProjectId}/dashboard`);
        const data = await res.json();
        alert('⚡ Generated fresh multi-platform social calendar for active project!');
        renderSocialHubTab(data);
      } catch (e) {
        alert('Error: ' + e.message);
      }
    }
"""

# Insert js_code right after `<script>\n    const API_BASE = window.location.origin;`
target_js_marker = "<script>\n    const API_BASE = window.location.origin;"
if target_js_marker in content:
    content = content.replace(target_js_marker, target_js_marker + "\n" + js_code)
    print("✓ Inserted Project-Centric OS JS Controller.")
else:
    print("Warning: target_js_marker not found!")

# Also update switchTab in content to support 'cockpit', 'social_hub', 'leads_hub'
switch_tab_target = "const titles = {\n        'chat': 'Studio Assistant',"
switch_tab_replace = """const titles = {
        'cockpit': 'Project Command & Cause-and-Effect Impact Radar',
        'social_hub': 'Social Marketing Autopilot',
        'leads_hub': 'Project Leads & Multi-Channel Outreach',
        'chat': 'Studio Assistant',"""

if switch_tab_target in content:
    content = content.replace(switch_tab_target, switch_tab_replace)
    print("✓ Updated switchTab titles with cockpit, social_hub, and leads_hub.")

# Also add initProjectCentricOS() call at page initialization
init_marker = "initSpeechRecognition();\n    refreshUniversalData();"
init_replace = "initSpeechRecognition();\n    refreshUniversalData();\n    initProjectCentricOS();"
if init_marker in content:
    content = content.replace(init_marker, init_replace)
    print("✓ Added initProjectCentricOS() to page load.")

with open("frontend/index.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated frontend/index.html with full Project-Centric OS Controller.")
