// ==========================================
// ADMIN TOOL REQUESTS & CUSTOM SOURCING PIPELINE
// ==========================================

function filterToolRequests(status, btn) {
    document.querySelectorAll('.req-filter-btn').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');

    const rows = document.querySelectorAll('#tool-requests-table tbody tr.req-row');
    rows.forEach(r => {
        if (status === 'ALL' || r.getAttribute('data-status') === status) {
            r.style.display = '';
        } else {
            r.style.display = 'none';
        }
    });
}

function searchToolRequests(query) {
    const q = (query || '').toLowerCase().trim();
    const rows = document.querySelectorAll('#tool-requests-table tbody tr.req-row');
    rows.forEach(r => {
        const text = (r.getAttribute('data-search') || '').toLowerCase();
        if (!q || text.includes(q)) {
            r.style.display = '';
        } else {
            r.style.display = 'none';
        }
    });
}

async function updateToolRequestStatus(reqId, newStatus) {
    try {
        const res = await fetch(`/api/admin/tool-requests/${reqId}/status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        const data = await res.json();
        if (data.ok) {
            if (typeof showThemeToast === 'function') {
                showThemeToast(`STATUS UPDATED: Sourcing brief #${data.request_id} set to ${newStatus}`);
            }
            // Update row dataset
            const row = document.querySelector(`#tool-requests-table tr.req-row select[onchange*="${reqId}"]`)?.closest('tr');
            if (row) {
                row.setAttribute('data-status', newStatus);
            }
        } else {
            showToast('Status update failed: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch(err) {
        showToast('Network error while updating status: ' + err.message, 'error');
    }
}

function populateAndOpenToolRequestModal(req) {
    const modal = document.getElementById('modal-tool-request-detail');
    if (!modal) return;

    const dbId = document.getElementById('tr-modal-db-id');
    if (dbId) dbId.value = req.id || '';

    const titleEl = document.getElementById('tr-modal-title');
    if (titleEl) titleEl.textContent = req.tool_name || 'TOOL SOURCING BRIEF';

    const idEl = document.getElementById('tr-modal-id');
    if (idEl) idEl.textContent = '#' + (req.request_id || '');

    const dateEl = document.getElementById('tr-modal-date');
    if (dateEl) dateEl.textContent = req.created_at || '';

    const tgEl = document.getElementById('tr-modal-telegram');
    const esc = window.escapeHtml || function(s){ return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;'); };
    if (tgEl) {
        if (req.contact_telegram) {
            const cleanTg = encodeURIComponent(req.contact_telegram.replace('@', '').trim());
            tgEl.innerHTML = `<a href="https://t.me/${cleanTg}" target="_blank" rel="noopener noreferrer" style="color:#00e5ff; font-family:var(--admin-font-mono); font-size:12px; text-decoration:none; font-weight:700; display:inline-flex; align-items:center; gap:5px;">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.3"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
                <span>${esc(req.contact_telegram)}</span>
            </a>`;
        } else {
            tgEl.textContent = '--';
        }
    }

    const emailEl = document.getElementById('tr-modal-email');
    if (emailEl) {
        if (req.contact_email) {
            const cleanEmail = encodeURIComponent(req.contact_email.trim());
            emailEl.innerHTML = `<a href="mailto:${cleanEmail}" style="color:#fff; text-decoration:underline;">${esc(req.contact_email)}</a>`;
        } else {
            emailEl.textContent = '--';
        }
    }

    const budgetEl = document.getElementById('tr-modal-budget');
    if (budgetEl) budgetEl.textContent = (req.budget_range || 'FLEXIBLE').replace(/_/g, ' ');

    const urgencyEl = document.getElementById('tr-modal-urgency');
    if (urgencyEl) {
        urgencyEl.textContent = req.urgency || 'STANDARD';
        if (req.urgency === 'IMMEDIATE') {
            urgencyEl.style.color = '#ef4444';
        } else if (req.urgency === 'HIGH') {
            urgencyEl.style.color = '#f59e0b';
        } else {
            urgencyEl.style.color = '#fff';
        }
    }

    const specsEl = document.getElementById('tr-modal-specs');
    if (specsEl) specsEl.textContent = req.technical_specs || 'No specific technical instructions provided.';

    const notesEl = document.getElementById('tr-modal-admin-notes');
    if (notesEl) notesEl.value = req.admin_notes || '';

    const ipEl = document.getElementById('tr-modal-ip');
    if (ipEl) ipEl.textContent = 'CLIENT IP: ' + (req.ip_address || '127.0.0.1');

    const badge = document.getElementById('tr-modal-status-badge');
    if (badge) {
        badge.textContent = req.status || 'PENDING';
        if (req.status === 'PENDING') {
            badge.style.background = '#00e5ff';
            badge.style.color = '#000';
        } else if (req.status === 'SOURCING') {
            badge.style.background = '#f59e0b';
            badge.style.color = '#000';
        } else if (req.status === 'FULFILLED') {
            badge.style.background = '#10b981';
            badge.style.color = '#000';
        } else {
            badge.style.background = '#ef4444';
            badge.style.color = '#fff';
        }
    }

    modal.classList.add('is-open');
    modal.style.display = 'flex';
}

function viewToolRequestDetail(target) {
    let req = null;
    if (typeof target === 'object' && target !== null) {
        req = target;
    } else if (window.ADMIN_TOOL_REQUESTS && Array.isArray(window.ADMIN_TOOL_REQUESTS)) {
        req = window.ADMIN_TOOL_REQUESTS.find(r => r.id == target || r.request_id == target);
    }

    if (!req) {
        fetch('/api/admin/tool-requests')
            .then(res => res.json())
            .then(data => {
                if (data.ok && data.requests) {
                    window.ADMIN_TOOL_REQUESTS = data.requests;
                    const found = data.requests.find(r => r.id == target || r.request_id == target);
                    if (found) {
                        populateAndOpenToolRequestModal(found);
                    } else {
                        showToast('Could not find procurement record #' + target, 'error');
                    }
                }
            })
            .catch(err => {
                console.error('Failed to fetch tool requests:', err);
                showToast('Failed to load request dossier.', 'error');
            });
        return;
    }

    populateAndOpenToolRequestModal(req);
}

async function saveToolRequestAdminNotes(e) {
    e.preventDefault();
    const reqId = document.getElementById('tr-modal-db-id').value;
    const notes = document.getElementById('tr-modal-admin-notes').value;
    const badge = document.getElementById('tr-modal-status-badge');
    const status = badge ? badge.textContent : 'PENDING';

    try {
        const res = await fetch(`/api/admin/tool-requests/${reqId}/status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: status, admin_notes: notes })
        });
        const data = await res.json();
        if (data.ok) {
            if (typeof showThemeToast === 'function') {
                showThemeToast('INTERNAL NOTES PERSISTED to procurement dossier.');
            }
            if (window.ADMIN_TOOL_REQUESTS) {
                const item = window.ADMIN_TOOL_REQUESTS.find(r => r.id == reqId);
                if (item) item.admin_notes = notes;
            }
            const modal = document.getElementById('modal-tool-request-detail');
            if (modal) {
                modal.classList.remove('is-open');
                modal.style.display = 'none';
            }
            if (typeof closeModal === 'function') {
                closeModal('modal-tool-request-detail');
            }
        } else {
            showToast('Failed to save notes: ' + (data.error || 'Error'), 'error');
        }
    } catch(err) {
        showToast('Network error: ' + err.message, 'error');
    }
}

async function deleteToolRequest(reqId, refId) {
    const confirmed = await showConfirmModal({
        title: 'DELETE CUSTOM REQUEST',
        message: `Permanently delete custom request #${refId}?`,
        confirmText: 'DELETE REQUEST',
        note: 'WARNING: This request and its details will be permanently removed.'
    });
    if (!confirmed) {
        return;
    }

    try {
        const res = await fetch(`/api/admin/tool-requests/${reqId}`, {
            method: 'DELETE'
        });
        const data = await res.json();
        if (data.ok) {
            const row = document.querySelector(`#tool-requests-table tr.req-row select[onchange*="${reqId}"]`)?.closest('tr');
            if (row) row.remove();
            if (typeof showThemeToast === 'function') {
                showThemeToast(`PURGED: Request #${refId} removed permanently.`);
            }
        } else {
            showToast('Delete failed: ' + (data.error || 'Unknown error'), 'error');
        }
    } catch(err) {
        showToast('Network error: ' + err.message, 'error');
    }
}
