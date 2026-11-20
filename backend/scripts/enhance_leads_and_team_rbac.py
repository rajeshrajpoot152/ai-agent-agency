import re

def enhance():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Add "Human Team (RBAC)" button in the Master Project Switcher Bar
    target_switcher_btn = '<button onclick="openCreateProjectModal()"'
    if 'openTeamDelegationModal()' not in html:
        replacement_btn = '''<button onclick="openTeamDelegationModal()" class="px-2.5 py-1.5 rounded-xl bg-purple-50 hover:bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 font-bold text-xs border border-purple-200 dark:border-purple-800 transition flex items-center gap-1 shadow-sm" title="Delegate projects to human managers (RBAC)">
          <span>👥</span> Team Delegation
        </button>
        <button onclick="openCreateProjectModal()"'''
        html = html.replace(target_switcher_btn, replacement_btn, 1)

    # 2. Enhance tab-leads_hub with Search Bar and Status Filters
    old_leads_header = '''        <div class="flex items-center justify-between flex-wrap gap-4 border-b border-slate-200 dark:border-slate-800 pb-4">
          <div>
            <h2 class="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <span>🎯</span> Project Leads & Multi-Channel Outreach
            </h2>
            <p class="text-xs text-slate-500 mt-0.5">Strictly isolated contacts for <strong id="leads-proj-name" class="text-indigo-600 dark:text-indigo-400">Active Project</strong>. Zero data leakage across tools or verticals.</p>
          </div>
          <div class="flex items-center gap-2">
            <button onclick="openAddLeadToProjectModal()" class="px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs transition flex items-center gap-1 shadow-sm">
              <span>➕</span> Add Lead to This Project
            </button>
          </div>
        </div>'''

    new_leads_header = '''        <div class="flex items-center justify-between flex-wrap gap-4 border-b border-slate-200 dark:border-slate-800 pb-4">
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
                <span>🎯</span> Project Leads & Multi-Channel Outreach
              </h2>
              <span class="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold bg-indigo-50 dark:bg-indigo-950 text-indigo-600 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">200–500 Scale Ready</span>
            </div>
            <p class="text-xs text-slate-500 mt-0.5">Strictly isolated contacts for <strong id="leads-proj-name" class="text-indigo-600 dark:text-indigo-400">Active Project</strong>. Zero data leakage across tools or verticals.</p>
          </div>
          <div class="flex items-center gap-2">
            <button onclick="openAddLeadToProjectModal()" class="px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs transition flex items-center gap-1 shadow-sm">
              <span>➕</span> Add Lead to This Project
            </button>
          </div>
        </div>

        <!-- 200–500 Scale High-Speed Search & Filter Bar -->
        <div class="p-3.5 rounded-2xl bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 flex items-center justify-between gap-3 flex-wrap shadow-sm">
          <div class="flex items-center gap-2 flex-1 min-w-[260px]">
            <span class="text-sm">🔍</span>
            <input type="text" id="leads-search-input" oninput="filterProjectLeads()" placeholder="Quick filter among 200–500 clients by name, business, phone or email..." class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-1.5 text-xs text-slate-900 dark:text-white focus:ring-2 focus:ring-indigo-500 font-sans" />
          </div>
          <div class="flex items-center gap-1.5 text-[11px] font-mono">
            <button onclick="setLeadsStatusFilter('all', this)" class="leads-filter-btn px-2.5 py-1 rounded-lg bg-indigo-600 text-white font-bold transition">All Leads</button>
            <button onclick="setLeadsStatusFilter('new', this)" class="leads-filter-btn px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 transition">New</button>
            <button onclick="setLeadsStatusFilter('in_discussion', this)" class="leads-filter-btn px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 transition">In Discussion</button>
            <button onclick="setLeadsStatusFilter('won', this)" class="leads-filter-btn px-2.5 py-1 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 transition">Deal Won</button>
            <span id="leads-count-indicator" class="ml-2 text-slate-400 font-sans text-xs">Loading...</span>
          </div>
        </div>'''

    if old_leads_header in html:
        html = html.replace(old_leads_header, new_leads_header, 1)

    # 3. Add Human Team Delegation Modal
    team_modal_html = '''
  <!-- ======================================================== -->
  <!-- MODAL: HUMAN TEAM DELEGATION & MULTI-MANAGER ACCESS (RBAC) -->
  <!-- ======================================================== -->
  <div id="team-delegation-modal" class="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm hidden flex items-center justify-center p-4">
    <div class="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 max-w-2xl w-full p-6 shadow-2xl space-y-5 animate-scaleIn max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
        <div>
          <h3 class="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <span>👥</span> Human Team & Project Delegation (RBAC)
          </h3>
          <p class="text-xs text-slate-500">Assign specific tools or ventures to human employees/managers. Strict isolation prevents cross-client data access.</p>
        </div>
        <button onclick="closeTeamDelegationModal()" class="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 flex items-center justify-center text-slate-500 font-bold">✕</button>
      </div>

      <!-- Active Team Members List -->
      <div class="space-y-2">
        <h4 class="text-xs font-bold font-mono uppercase text-slate-500 tracking-wider">Active Human Managers & Delegations</h4>
        <div id="team-delegation-list" class="space-y-2 max-h-48 overflow-y-auto pr-1">
          <div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-xs text-slate-400">Loading team members...</div>
        </div>
      </div>

      <!-- Add New Team Member Form -->
      <div class="border-t border-slate-100 dark:border-slate-800 pt-4 space-y-3">
        <h4 class="text-xs font-bold font-mono uppercase text-indigo-600 dark:text-indigo-400 tracking-wider">➕ Delegate New Human Team Member</h4>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="block text-[11px] font-mono text-slate-500 mb-1">Full Name</label>
            <input type="text" id="new-team-name" placeholder="e.g. Vikram Joshi" class="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-900 dark:text-white" />
          </div>
          <div>
            <label class="block text-[11px] font-mono text-slate-500 mb-1">Email Address</label>
            <input type="email" id="new-team-email" placeholder="e.g. vikram@agency.io" class="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-900 dark:text-white" />
          </div>
        </div>
        <div>
          <label class="block text-[11px] font-mono text-slate-500 mb-1">Role / Job Title</label>
          <input type="text" id="new-team-role" placeholder="e.g. Senior Project Manager, Client Lead" class="w-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-900 dark:text-white" />
        </div>
        <div>
          <label class="block text-[11px] font-mono text-slate-500 mb-1">Assigned Projects (Select which ventures this manager can access)</label>
          <div id="new-team-projects-checkboxes" class="grid grid-cols-1 sm:grid-cols-2 gap-2 p-3 rounded-xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 max-h-36 overflow-y-auto">
            <!-- Dynamically populated with active projects -->
          </div>
        </div>

        <div class="flex items-center justify-end gap-2 pt-2">
          <button onclick="closeTeamDelegationModal()" class="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-xs font-semibold">Cancel</button>
          <button id="btn-submit-team-member" onclick="submitAddTeamMemberAction()" class="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-xs shadow-sm transition">Assign Manager & Permissions</button>
        </div>
      </div>
    </div>
  </div>
'''

    if 'id="team-delegation-modal"' not in html:
        # Place before </body>
        html = html.replace('</body>', team_modal_html + '\n</body>', 1)

    # 4. Enhance JavaScript for Leads Filtering and Team Delegation
    js_addon = '''
    // ========================================================
    // 200–500 CLIENT SCALE: LEADS SEARCH & STATUS FILTERING
    // ========================================================
    let currentRawLeads = [];
    let currentLeadStatusFilter = 'all';

    function setLeadsStatusFilter(status, btnEl) {
      currentLeadStatusFilter = status;
      document.querySelectorAll('.leads-filter-btn').forEach(btn => {
        btn.classList.remove('bg-indigo-600', 'text-white', 'font-bold');
        btn.classList.add('bg-slate-100', 'dark:bg-slate-800', 'text-slate-600', 'dark:text-slate-300');
      });
      if (btnEl) {
        btnEl.classList.remove('bg-slate-100', 'dark:bg-slate-800', 'text-slate-600', 'dark:text-slate-300');
        btnEl.classList.add('bg-indigo-600', 'text-white', 'font-bold');
      }
      filterProjectLeads();
    }

    function filterProjectLeads() {
      const query = (document.getElementById('leads-search-input')?.value || '').toLowerCase().trim();
      const filtered = currentRawLeads.filter(l => {
        // Status filter
        if (currentLeadStatusFilter !== 'all') {
          if (l.status !== currentLeadStatusFilter) return false;
        }
        // Query search
        if (!query) return true;
        const nameMatch = (l.full_name || '').toLowerCase().includes(query);
        const bizMatch = (l.business_name || '').toLowerCase().includes(query);
        const phoneMatch = (l.whatsapp_number || l.mobile_number || '').includes(query);
        const emailMatch = (l.email_address || '').toLowerCase().includes(query);
        const noteMatch = (l.notes || '').toLowerCase().includes(query);
        return nameMatch || bizMatch || phoneMatch || emailMatch || noteMatch;
      });

      const countEl = document.getElementById('leads-count-indicator');
      if (countEl) {
        countEl.textContent = `Showing ${filtered.length} of ${currentRawLeads.length} Leads`;
      }

      renderFilteredLeadsTable(filtered);
    }

    function renderFilteredLeadsTable(leads) {
      const tbody = document.getElementById('project-leads-table-body');
      if (!tbody) return;

      if (leads.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center py-10 text-slate-400 text-xs font-mono">No matching leads found for current search/filter.</td></tr>`;
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

    // Wrap renderLeadsHubTab to feed raw leads into filter
    const originalRenderLeadsHubTab = renderLeadsHubTab;
    renderLeadsHubTab = function(data) {
      currentRawLeads = data.leads || [];
      document.getElementById('leads-proj-name').textContent = data.project.brand_name;
      const countEl = document.getElementById('leads-count-indicator');
      if (countEl) countEl.textContent = `Showing ${currentRawLeads.length} of ${currentRawLeads.length} Leads`;
      filterProjectLeads();
    };

    // ========================================================
    // HUMAN TEAM DELEGATION & RBAC CONTROLLER
    // ========================================================
    async function openTeamDelegationModal() {
      const modal = document.getElementById('team-delegation-modal');
      modal.classList.remove('hidden');

      // Populate projects checkboxes
      const container = document.getElementById('new-team-projects-checkboxes');
      if (container && portfolioProjects.length > 0) {
        container.innerHTML = portfolioProjects.map(p => `
          <label class="flex items-center gap-2 p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-900 cursor-pointer text-xs">
            <input type="checkbox" name="team-project-access" value="${p.id}" class="rounded text-indigo-600 focus:ring-indigo-500" />
            <span class="text-slate-800 dark:text-slate-200 font-medium">${escapeHtml(p.brand_name)}</span>
          </label>
        `).join('');
      }

      await loadTeamMembersList();
    }

    function closeTeamDelegationModal() {
      document.getElementById('team-delegation-modal').classList.add('hidden');
    }

    async function loadTeamMembersList() {
      const listEl = document.getElementById('team-delegation-list');
      try {
        const res = await fetch(`${API_BASE}/api/projects-hub/team-members`);
        const data = await res.json();
        const members = data.team_members || [];
        if (members.length === 0) {
          listEl.innerHTML = `<div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-950 text-xs text-slate-400">No human team members added yet. Add one below to delegate projects!</div>`;
          return;
        }

        listEl.innerHTML = members.map(m => {
          let assignedNames = 'None';
          if (m.assigned_projects && m.assigned_projects.length > 0) {
            assignedNames = m.assigned_projects.map(pid => {
              const pr = portfolioProjects.find(p => p.id === pid);
              return pr ? pr.brand_name : 'Project';
            }).join(', ');
          }

          return `
            <div class="p-3 rounded-2xl bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 flex items-center justify-between gap-3">
              <div>
                <div class="font-bold text-xs text-slate-900 dark:text-white flex items-center gap-2">
                  <span>👤 ${escapeHtml(m.full_name)}</span>
                  <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-indigo-50 text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400">${escapeHtml(m.role || 'Manager')}</span>
                </div>
                <div class="text-[11px] text-slate-500 mt-0.5 font-mono">✉️ ${escapeHtml(m.email)}</div>
                <div class="text-[10px] text-emerald-600 dark:text-emerald-400 font-mono mt-1 font-semibold">
                  🔒 Assigned Access: ${escapeHtml(assignedNames)}
                </div>
              </div>
              <span class="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 font-bold">Active</span>
            </div>
          `;
        }).join('');
      } catch (e) {
        listEl.innerHTML = `<div class="p-3 text-xs text-rose-500">Error loading team: ${e.message}</div>`;
      }
    }

    async function submitAddTeamMemberAction() {
      const name = document.getElementById('new-team-name').value.trim();
      const email = document.getElementById('new-team-email').value.trim();
      const role = document.getElementById('new-team-role').value.trim() || 'Project Manager';
      
      const checkedBoxes = Array.from(document.querySelectorAll('input[name="team-project-access"]:checked'));
      const assignedIds = checkedBoxes.map(cb => cb.value);

      if (!name || !email) {
        alert('Please provide manager name and email address.');
        return;
      }

      const btn = document.getElementById('btn-submit-team-member');
      btn.disabled = true;
      btn.textContent = 'Saving Delegation...';

      try {
        const res = await fetch(`${API_BASE}/api/projects-hub/team-members`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            full_name: name,
            email: email,
            role: role,
            assigned_projects: assignedIds
          })
        });
        const data = await res.json();
        alert('✓ ' + (data.message || 'Human team member delegated successfully!'));
        
        document.getElementById('new-team-name').value = '';
        document.getElementById('new-team-email').value = '';
        document.getElementById('new-team-role').value = '';
        checkedBoxes.forEach(cb => cb.checked = false);

        await loadTeamMembersList();
      } catch (e) {
        alert('Error delegating team member: ' + e.message);
      } finally {
        btn.disabled = false;
        btn.textContent = 'Assign Manager & Permissions';
      }
    }
'''

    if 'openTeamDelegationModal' not in html:
        # Insert before </script>
        html = html.replace('</script>\n</body>', js_addon + '\n</script>\n</body>', 1)

    with open("frontend/index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("✓ Successfully enhanced Leads Hub with 200-500 Scale Search/Filter and added Human Team Delegation Modal!")

if __name__ == "__main__":
    enhance()
