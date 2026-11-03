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
            alert('Status update failed: ' + (data.error || 'Unknown error'));
        }
    } catch(err) {
        alert('Network error while updating status: ' + err.message);
    }
}

function viewToolRequestDetail(req) {
    const modal = document.getElementById('modal-tool-request-detail');
    if (!modal) return;

    document.getElementById('tr-modal-db-id').value = req.id || '';
    document.getElementById('tr-modal-title').textContent = req.tool_name || 'TOOL SOURCING BRIEF';
    document.getElementById('tr-modal-id').textContent = '#' + (req.request_id || '');
    document.getElementById('tr-modal-date').textContent = req.created_at || '';
    document.getElementById('tr-modal-telegram').textContent = req.contact_telegram || '--';
    document.getElementById('tr-modal-email').textContent = req.contact_email || '--';
    document.getElementById('tr-modal-budget').textContent = (req.budget_range || 'FLEXIBLE').replace(/_/g, ' ');
    document.getElementById('tr-modal-urgency').textContent = req.urgency || 'STANDARD';
    document.getElementById('tr-modal-specs').textContent = req.technical_specs || 'No specific technical instructions provided.';
    document.getElementById('tr-modal-admin-notes').value = req.admin_notes || '';
    document.getElementById('tr-modal-ip').textContent = 'CLIENT IP: ' + (req.ip_address || '127.0.0.1');

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

    if (typeof openModal === 'function') {
        openModal('modal-tool-request-detail');
    }
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
            closeModal('modal-tool-request-detail');
        } else {
            alert('Failed to save notes: ' + (data.error || 'Error'));
        }
    } catch(err) {
        alert('Network error: ' + err.message);
    }
}

async function deleteToolRequest(reqId, refId) {
    if (!confirm(`Permanently remove tool procurement request #${refId} from the intake queue?`)) {
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
            alert('Delete failed: ' + (data.error || 'Unknown error'));
        }
    } catch(err) {
        alert('Network error: ' + err.message);
    }
}
