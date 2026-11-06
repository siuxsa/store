        // XSS Defense: Authoritative Global HTML Escaping
        function escapeHtml(str) {
            if (str === null || str === undefined) return '';
            return String(str)
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;')
                .replace(/'/g, '&#39;');
        }
        window.escapeHtml = escapeHtml;

        let currentDays = 14;
        let chartTimelineInstance = null;
        let chartFunnelInstance = null;
        let chartOsInstance = null;
        let chartCategoryInstance = null;

        let currentFeature = 'analytics';
        let currentSubtabs = {
            analytics: 'overview',
            products: 'catalog',
            journal: 'dispatches',
            orders: 'all',
            system: 'settings'
        };

        // Primary Feature Switcher
        function switchFeature(featureName, optSubtab) {
            window.scrollTo(0, 0);
            currentFeature = featureName;
            try { sessionStorage.setItem('activeAdminFeature', featureName); } catch(e) {}

            // Update Primary Header Buttons
            document.querySelectorAll('.admin-header-btn').forEach(btn => {
                if (btn.getAttribute('data-feature') === featureName) {
                    btn.classList.add('active');
                } else {
                    btn.classList.remove('active');
                }
            });

            // Toggle Feature Subtabs Bar
            document.querySelectorAll('.feature-subtabs').forEach(el => {
                el.style.display = 'none';
            });
            const subtabsBar = document.getElementById(`subtabs-${featureName}`);
            if (subtabsBar) {
                subtabsBar.style.display = 'flex';
            }

            // Determine Target Subtab
            const targetSubtab = optSubtab || currentSubtabs[featureName] || getDefaultSubtab(featureName);
            switchSubtab(featureName, targetSubtab);
        }

        function getDefaultSubtab(feature) {
            if (feature === 'analytics') return 'overview';
            if (feature === 'products') return 'catalog';
            if (feature === 'journal') return 'dispatches';
            if (feature === 'orders') return 'all';
            if (feature === 'system') return 'settings';
            return 'overview';
        }

        // Feature-Specific Subtab Switcher
        function switchSubtab(feature, subtabName, btn) {
            window.scrollTo(0, 0);
            currentSubtabs[feature] = subtabName;
            try { sessionStorage.setItem(`activeSubtab_${feature}`, subtabName); } catch(e) {}

            // Update Subtab Pill Active State
            const subtabsBar = document.getElementById(`subtabs-${feature}`);
            if (subtabsBar) {
                subtabsBar.querySelectorAll('.subnav-item').forEach(b => {
                    if (b.getAttribute('data-subtab') === subtabName || b === btn) {
                        b.classList.add('active');
                    } else {
                        b.classList.remove('active');
                    }
                });
            }

            // Hide All Admin Modules
            document.querySelectorAll('.admin-module').forEach(m => m.classList.remove('active'));

            let targetModId = null;
            const adminContainer = document.querySelector('.admin-container');

            if (adminContainer) {
                if (feature === 'analytics' && subtabName === 'matrix-full') {
                    adminContainer.classList.add('matrix-mode');
                } else {
                    adminContainer.classList.remove('matrix-mode');
                }
            }

            if (feature === 'analytics') {
                if (subtabName === 'matrix-full') {
                    targetModId = 'mod-analytics-matrix';
                    if (typeof renderFullMatrixPage === 'function') renderFullMatrixPage();
                    setTimeout(() => {
                        if (typeof renderFullMatrixPage === 'function') renderFullMatrixPage();
                    }, 50);
                } else {
                    subtabName = 'overview';
                    targetModId = 'mod-analytics';
                    setTimeout(() => {
                        if (chartTimelineInstance) chartTimelineInstance.resize();
                        if (chartFunnelInstance) chartFunnelInstance.resize();
                        if (chartOsInstance) chartOsInstance.resize();
                        if (chartCategoryInstance) chartCategoryInstance.resize();
                    }, 50);
                }
                if (adminContainer) adminContainer.classList.remove('themes-mode');
            } else if (feature === 'products') {
                if (subtabName === 'catalog') {
                    targetModId = 'mod-products';
                    if (typeof renderProductsPagination === 'function') renderProductsPagination();
                }
                else if (subtabName === 'studio') targetModId = 'mod-product-editor';
                else if (subtabName === 'curation') {
                    targetModId = 'mod-curation-products';
                    if (typeof initHomeCurationPreviews === 'function') initHomeCurationPreviews();
                }
                else if (subtabName === 'reviews') {
                    targetModId = 'mod-reviews';
                    if (typeof initHomepageReviewsCuration === 'function') initHomepageReviewsCuration();
                    if (typeof renderReviewsPagination === 'function') renderReviewsPagination();
                }
                else {
                    subtabName = 'catalog';
                    targetModId = 'mod-products';
                    if (typeof renderProductsPagination === 'function') renderProductsPagination();
                }
                if (adminContainer) adminContainer.classList.remove('themes-mode');
            } else if (feature === 'journal') {
                if (subtabName === 'dispatches') {
                    targetModId = 'mod-posts';
                    if (typeof renderPostsPagination === 'function') renderPostsPagination();
                }
                else if (subtabName === 'studio') targetModId = 'mod-post-editor';
                else if (subtabName === 'curation') {
                    targetModId = 'mod-curation-posts';
                    if (typeof initHomeCurationPreviews === 'function') initHomeCurationPreviews();
                }
                else if (subtabName === 'comments') {
                    targetModId = 'mod-comments';
                    if (typeof renderCommentsPagination === 'function') renderCommentsPagination();
                }
                else {
                    subtabName = 'dispatches';
                    targetModId = 'mod-posts';
                    if (typeof renderPostsPagination === 'function') renderPostsPagination();
                }
                if (adminContainer) adminContainer.classList.remove('themes-mode');
            } else if (feature === 'orders') {
                if (subtabName === 'pending') {
                    targetModId = 'mod-orders';
                    filterAdminOrders('PENDING', document.querySelector('.order-filter-btn[onclick*="PENDING"]'));
                } else if (subtabName === 'requests') {
                    targetModId = 'mod-tool-requests';
                    if (typeof filterToolRequests === 'function') filterToolRequests('ALL', document.querySelector('.req-filter-btn[onclick*="ALL"]'));
                } else {
                    targetModId = 'mod-orders';
                    subtabName = 'all';
                    filterAdminOrders('ALL', document.querySelector('.order-filter-btn[onclick*="ALL"]'));
                }
                if (adminContainer) adminContainer.classList.remove('themes-mode');
            } else if (feature === 'system') {
                if (subtabName === 'settings') {
                    targetModId = 'mod-settings';
                    if (typeof refreshDataStats === 'function') refreshDataStats();
                }
                else if (subtabName === 'security') {
                    targetModId = 'mod-settings';
                    setTimeout(() => {
                        if (typeof switchSettingsTab === 'function') {
                            const btn = document.querySelector('.settings-subnav-btn[data-tab="security"]');
                            switchSettingsTab('security', btn);
                        }
                        if (typeof refreshSecurityTelemetry === 'function') refreshSecurityTelemetry();
                    }, 30);
                }
                else if (subtabName === 'seo') {
                    targetModId = 'mod-seo';
                    setTimeout(() => {
                        if (typeof updateSeoLivePreview === 'function') updateSeoLivePreview();
                    }, 50);
                }
                else if (subtabName === 'tracking') {
                    subtabName = 'settings';
                    targetModId = 'mod-settings';
                    if (subtabsBar) {
                        const settingsBtn = subtabsBar.querySelector('.subnav-item[data-subtab="settings"]');
                        if (settingsBtn) {
                            subtabsBar.querySelectorAll('.subnav-item').forEach(b => b.classList.remove('active'));
                            settingsBtn.classList.add('active');
                        }
                    }
                    setTimeout(() => {
                        if (typeof switchSettingsTab === 'function') {
                            const btn = document.querySelector('.settings-subnav-btn[data-tab="tracking"]');
                            switchSettingsTab('tracking', btn);
                        }
                    }, 30);
                }
                else if (subtabName === 'themes-visual' || subtabName === 'themes') {
                    targetModId = 'mod-themes-visual';
                    if (adminContainer) adminContainer.classList.add('themes-mode');
                    setTimeout(() => {
                        if (typeof applyThemeViewportDimensions === 'function') applyThemeViewportDimensions();
                        if (typeof setupIframeInspectListeners === 'function') setupIframeInspectListeners();
                    }, 50);
                    setTimeout(() => {
                        if (typeof applyThemeViewportDimensions === 'function') applyThemeViewportDimensions();
                    }, 250);
                } else if (subtabName === 'themes-text') {
                    targetModId = 'mod-themes-text';
                } else if (subtabName === 'users') {
                    targetModId = 'mod-users';
                    if (typeof renderUsersPagination === 'function') renderUsersPagination();
                }
                else if (subtabName === 'audit') {
                    targetModId = 'mod-audit';
                    if (typeof renderAuditPagination === 'function') renderAuditPagination();
                }
                else {
                    subtabName = 'settings';
                    targetModId = 'mod-settings';
                }

                if (subtabName !== 'themes-visual' && subtabName !== 'themes' && adminContainer) {
                    adminContainer.classList.remove('themes-mode');
                }
            }

            if (targetModId) {
                const targetEl = document.getElementById(targetModId);
                if (targetEl) {
                    targetEl.classList.add('active');
                    window.scrollTo(0, 0);
                    const tw = targetEl.querySelector('.admin-table-wrap');
                    if (tw) tw.scrollTop = 0;
                } else {
                    console.error('Target module not found:', targetModId);
                }
            }
        }

        // Orders filter
        function filterAdminOrders(statusFilter, btn) {
            document.querySelectorAll('.order-filter-btn').forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');
            const rows = document.querySelectorAll('#mod-orders tbody tr');
            rows.forEach(row => {
                if (!statusFilter || statusFilter === 'ALL') {
                    row.style.display = '';
                } else {
                    const statusPill = row.querySelector('.status-pill');
                    const selectEl = row.querySelector('select');
                    const txt = ((statusPill ? statusPill.textContent : '') + ' ' + (selectEl ? selectEl.value : '') + ' ' + (row.getAttribute('data-status') || '')).toUpperCase();
                    if (statusFilter === 'PENDING' && (txt.includes('PENDING') || txt.includes('UNFULFILLED'))) {
                        row.style.display = '';
                    } else if (statusFilter === 'COMPLETED' && txt.includes('COMPLETED')) {
                        row.style.display = '';
                    } else if (txt.includes(statusFilter)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                }
            });
        }

        // Backward compatibility bridge for switchAdminTab
        function switchAdminTab(tabName, btn) {
            if (tabName === 'analytics') {
                switchFeature('analytics', 'overview');
            } else if (tabName === 'products') {
                switchFeature('products', 'catalog');
            } else if (tabName === 'product-editor') {
                switchFeature('products', 'studio');
            } else if (tabName === 'curation-products') {
                switchFeature('products', 'curation');
            } else if (tabName === 'reviews') {
                switchFeature('products', 'reviews');
            } else if (tabName === 'posts') {
                switchFeature('journal', 'dispatches');
            } else if (tabName === 'post-editor') {
                switchFeature('journal', 'studio');
            } else if (tabName === 'curation-posts') {
                switchFeature('journal', 'curation');
            } else if (tabName === 'comments') {
                switchFeature('journal', 'comments');
            } else if (tabName === 'orders') {
                switchFeature('orders', 'all');
            } else if (tabName === 'settings') {
                switchFeature('system', 'settings');
            } else if (tabName === 'seo') {
                switchFeature('system', 'seo');
            } else if (tabName === 'themes' || tabName === 'themes-visual') {
                switchFeature('system', 'themes-visual');
            } else if (tabName === 'themes-text') {
                switchFeature('system', 'themes-text');
            } else if (tabName === 'users') {
                switchFeature('system', 'users');
            } else if (tabName === 'audit') {
                switchFeature('system', 'audit');
            } else {
                document.querySelectorAll('.admin-module').forEach(m => m.classList.remove('active'));
                const target = document.getElementById('mod-' + tabName);
                if (target) target.classList.add('active');
            }
        }

        function switchAnalyticsSubTable(subTab, btn) {
            const wrap = btn ? btn.closest('.module-subnav') : document.querySelector('#analytics-tables-anchor .module-subnav');
            if (wrap) {
                wrap.querySelectorAll('.subnav-btn').forEach(el => el.classList.remove('active'));
            }
            if (btn) btn.classList.add('active');
            const p = document.getElementById('subtab-products');
            const b = document.getElementById('subtab-blogs');
            const s = document.getElementById('subtab-stream');
            if (p) p.style.display = (subTab === 'products') ? 'block' : 'none';
            if (b) b.style.display = (subTab === 'blogs') ? 'block' : 'none';
            if (s) s.style.display = (subTab === 'stream') ? 'block' : 'none';
        }

        function openModal(id) {
            const el = document.getElementById(id);
            if (el) {
                el.classList.add('is-open');
                el.style.display = 'flex';
            }
        }

        function closeModal(id) {
            const el = document.getElementById(id);
            if (el) {
                el.classList.remove('is-open');
                el.style.display = 'none';
            }
        }
        window.openModal = openModal;
        window.closeModal = closeModal;

        // Close any open modal on ESC key or backdrop click
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                document.querySelectorAll('.admin-modal.is-open').forEach(m => {
                    if (m.id === 'modal-confirm') return;
                    m.classList.remove('is-open');
                    m.style.display = 'none';
                });
            }
        });
        document.addEventListener('DOMContentLoaded', function() {
            document.querySelectorAll('.admin-modal').forEach(m => {
                m.addEventListener('click', function(e) {
                    if (e.target === m && m.id !== 'modal-confirm') {
                        m.classList.remove('is-open');
                        m.style.display = 'none';
                    }
                });
            });
        });

        // ==========================================
        // CHART.JS INITIALIZATION & DARK THEME SETUP
        // ==========================================


        // INITIAL BOOTSTRAP
        // ==========================================
        document.addEventListener('DOMContentLoaded', () => {
            try {
                if (typeof initHomeCurationPreviews === 'function') initHomeCurationPreviews();
                if (typeof initHomepageReviewsCuration === 'function') initHomepageReviewsCuration();
            } catch(e) {}
            // Restore active admin feature and subtab from session storage (defaults to analytics)
            try {
                let savedFeature = sessionStorage.getItem('activeAdminFeature');
                let savedSubtab = null;
                const legacyTab = sessionStorage.getItem('activeAdminTab');
                if (legacyTab) {
                    if (legacyTab === 'comments') { savedFeature = 'journal'; savedSubtab = 'comments'; }
                    else if (legacyTab === 'reviews') { savedFeature = 'products'; savedSubtab = 'reviews'; }
                    else if (legacyTab === 'posts') { savedFeature = 'journal'; savedSubtab = 'dispatches'; }
                    else if (legacyTab === 'products') { savedFeature = 'products'; savedSubtab = 'catalog'; }
                    else if (legacyTab === 'settings') { savedFeature = 'system'; savedSubtab = 'settings'; }
                    else if (legacyTab === 'seo') { savedFeature = 'system'; savedSubtab = 'seo'; }
                    else if (legacyTab === 'themes-visual' || legacyTab === 'themes') { savedFeature = 'system'; savedSubtab = 'themes-visual'; }
                    else if (legacyTab === 'themes-text') { savedFeature = 'system'; savedSubtab = 'themes-text'; }
                    sessionStorage.removeItem('activeAdminTab');
                }
                if (!savedFeature) savedFeature = 'analytics';
                if (!savedSubtab) savedSubtab = sessionStorage.getItem(`activeSubtab_${savedFeature}`) || getDefaultSubtab(savedFeature);
                switchFeature(savedFeature, savedSubtab);
            } catch(e) {
                switchFeature('analytics', 'overview');
            }

            if (window.INITIAL_ANALYTICS_DATA) {
                try {
                    if (typeof initCharts === 'function') initCharts(window.INITIAL_ANALYTICS_DATA);
                } catch(err) {
                    console.error('Error initializing charts:', err);
                }
                try {
                    if (typeof renderAnalyticsTables === 'function') renderAnalyticsTables(window.INITIAL_ANALYTICS_DATA);
                } catch(err) {
                    console.error('Error rendering analytics tables:', err);
                }
            } else {
                try {
                    if (typeof loadAnalytics === 'function') loadAnalytics(14);
                } catch(err) {
                    console.error('Error loading analytics:', err);
                }
            }

            // Initialize theme viewport scaler
            setTimeout(() => {
                if (typeof applyThemeViewportDimensions === 'function') {
                    applyThemeViewportDimensions();
                }
            }, 100);

            // Periodic background sync every 25s
            setInterval(() => {
                const activeMod = document.querySelector('.admin-module.active');
                if (activeMod && activeMod.id === 'mod-analytics') {
                    loadAnalytics(currentDays);
                }
            }, 25000);
        });

        // Global Smooth Table Side-Scroll Helper
        window.scrollAdminTable = function(tableId, delta) {
            const table = document.getElementById(tableId);
            if (!table) return;
            const wrap = table.closest('.admin-table-wrap');
            if (wrap) {
                wrap.scrollBy({ left: delta, behavior: 'smooth' });
            }
        };

        // ========================================================
        // UNIVERSAL HIGH-TECH CYBERPUNK TOAST NOTIFICATION
        // ========================================================
        window.showToast = function(msg, type) {
            type = type || 'info';
            let container = document.getElementById('global-toast-container');
            if (!container) {
                container = document.createElement('div');
                container.id = 'global-toast-container';
                container.style.cssText = 'position:fixed; bottom:24px; right:24px; z-index:9999999; display:flex; flex-direction:column; gap:10px; pointer-events:none; max-width:440px; width:calc(100vw - 48px);';
                document.body.appendChild(container);
            }
            const toast = document.createElement('div');
            const isErr = type === 'error' || type === 'danger';
            const isSucc = type === 'success';
            const accentColor = isErr ? '#ef4444' : (isSucc ? '#10b981' : '#00e5ff');
            const icon = isErr
                ? '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>'
                : (isSucc
                    ? '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>'
                    : '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#00e5ff" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>');

            toast.style.cssText = `background:#0f1216; border:1px solid ${accentColor}88; border-left:4px solid ${accentColor}; box-shadow:0 12px 40px rgba(0,0,0,0.85); color:#e5e7eb; padding:12px 16px; font-family:var(--admin-font-mono, monospace); font-size:12px; line-height:1.45; border-radius:3px; pointer-events:auto; display:flex; align-items:flex-start; gap:10px; opacity:0; transform:translateY(12px); transition:opacity 0.22s ease, transform 0.22s ease;`;
            toast.innerHTML = `<span style="flex-shrink:0; margin-top:1px;">${icon}</span><span style="flex:1; word-break:break-word;">${msg}</span><button type="button" style="background:none; border:none; color:#888; cursor:pointer; font-size:14px; padding:0 0 0 8px; line-height:1;" onclick="this.parentElement.remove()">✕</button>`;
            container.appendChild(toast);
            requestAnimationFrame(() => {
                toast.style.opacity = '1';
                toast.style.transform = 'translateY(0)';
            });
            setTimeout(() => {
                toast.style.opacity = '0';
                toast.style.transform = 'translateY(12px)';
                setTimeout(() => toast.remove(), 250);
            }, 4500);
        };

        function ensureConfirmModalDOM() {
            let modal = document.getElementById('modal-confirm');
            if (!modal) {
                modal = document.createElement('div');
                modal.id = 'modal-confirm';
                modal.className = 'admin-modal';
                modal.style.cssText = 'display:none; z-index:999999;';
                modal.innerHTML = `
                <div class="admin-modal-box confirm-modal-box">
                    <div class="confirm-modal-header">
                        <div class="confirm-icon-wrap" id="confirm-modal-icon">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                                <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
                            </svg>
                        </div>
                        <div style="flex:1;">
                            <span class="confirm-modal-tag" id="confirm-modal-tag">WARNING</span>
                            <h3 class="confirm-modal-title" id="confirm-modal-title">CONFIRM ACTION</h3>
                        </div>
                        <button type="button" id="confirm-modal-close-x" class="btn-admin btn-admin-outline" style="padding:0.25rem 0.55rem; border-color:transparent; color:var(--admin-muted);" onclick="if (window._confirmReject) window._confirmReject()">✕</button>
                    </div>
                    <div class="confirm-modal-body">
                        <p id="confirm-modal-message" class="confirm-modal-text">Are you sure you want to proceed with this operation?</p>
                        <div id="confirm-modal-input-wrap" style="display:none; margin: 1rem 0;">
                            <input type="text" id="confirm-modal-input" class="admin-input" style="width:100%; box-sizing:border-box; background:#07080a; border:1px solid rgba(0,229,255,0.4); color:#fff; padding:0.6rem 0.85rem; font-family:var(--admin-font-mono, monospace); font-size:12px; border-radius:4px;" autocomplete="off" spellcheck="false">
                        </div>
                        <div class="confirm-modal-note" id="confirm-modal-note">WARNING: This action alters persistent database records and cannot be undone.</div>
                    </div>
                    <div class="confirm-modal-footer">
                        <button type="button" class="btn-admin btn-admin-outline" id="confirm-modal-cancel-btn" style="min-width:90px; padding:0.5rem 1rem;">CANCEL</button>
                        <button type="button" class="btn-admin btn-admin-danger" id="confirm-modal-ok-btn" style="min-width:130px; padding:0.5rem 1.25rem; display:inline-flex; align-items:center; justify-content:center; gap:6px; font-weight:700;">
                            <svg id="confirm-modal-ok-svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><polyline points="20 6 9 17 4 12"/></svg>
                            <span id="confirm-modal-ok-text">DELETE PERMANENTLY</span>
                        </button>
                    </div>
                </div>`;
                document.body.appendChild(modal);
            }
            return modal;
        }

        // ========================================================
        // GLOBAL HIGH-FIDELITY CYBERPUNK CONFIRMATION / PROMPT / ALERT MODAL
        // ========================================================
        window.showConfirmModal = function(options) {
            return new Promise((resolve) => {
                const modal = ensureConfirmModalDOM();

                let msg = typeof options === 'string' ? options : (options && options.message ? options.message : 'Are you sure you want to proceed?');
                let title = (options && options.title) || 'CONFIRM OPERATION';
                let confirmText = (options && options.confirmText) || 'CONFIRM & EXECUTE';
                let cancelText = (options && options.cancelText) || 'CANCEL';
                let isDanger = options && options.danger !== undefined ? options.danger : true;
                let isPrompt = Boolean(options && options.isPrompt);
                let isAlert = Boolean(options && options.isAlert);
                let defaultValue = (options && options.defaultValue) || '';
                let placeholder = (options && options.placeholder) || '';
                let note = (options && options.note) || (isDanger ? 'WARNING: This action alters persistent database records and cannot be undone.' : (isPrompt ? 'INPUT REQUIRED: Specify payload parameters to continue.' : 'System will proceed with the requested configuration change.'));

                const box = modal.querySelector('.admin-modal-box');
                if (box) {
                    if (isDanger) {
                        box.classList.remove('confirm-type-info');
                    } else {
                        box.classList.add('confirm-type-info');
                    }
                }

                const titleEl = document.getElementById('confirm-modal-title');
                const tagEl = document.getElementById('confirm-modal-tag');
                const msgEl = document.getElementById('confirm-modal-message');
                const noteEl = document.getElementById('confirm-modal-note');
                const okBtn = document.getElementById('confirm-modal-ok-btn');
                const okText = document.getElementById('confirm-modal-ok-text');
                const cancelBtn = document.getElementById('confirm-modal-cancel-btn');
                const closeX = document.getElementById('confirm-modal-close-x');
                const iconWrap = document.getElementById('confirm-modal-icon');
                const inputWrap = document.getElementById('confirm-modal-input-wrap');
                const inputEl = document.getElementById('confirm-modal-input');

                if (titleEl) titleEl.textContent = title;
                if (tagEl) {
                    if (isAlert) tagEl.textContent = 'SYSTEM NOTICE';
                    else if (isPrompt) tagEl.textContent = 'INPUT REQUIRED';
                    else tagEl.textContent = isDanger ? 'WARNING' : 'CONFIRMATION';
                }
                if (msgEl) msgEl.textContent = msg;
                if (noteEl) noteEl.textContent = note;
                if (okText) okText.textContent = isAlert ? (options && options.confirmText ? options.confirmText : 'ACKNOWLEDGE') : confirmText;
                if (cancelBtn) {
                    cancelBtn.textContent = cancelText;
                    cancelBtn.style.display = isAlert ? 'none' : 'inline-flex';
                }

                if (inputWrap && inputEl) {
                    if (isPrompt) {
                        inputWrap.style.display = 'block';
                        inputEl.value = defaultValue;
                        inputEl.placeholder = placeholder;
                    } else {
                        inputWrap.style.display = 'none';
                    }
                }

                if (okBtn) {
                    if (isDanger) {
                        okBtn.className = 'btn-admin btn-admin-danger';
                        okBtn.style.background = '';
                        okBtn.style.color = '';
                    } else {
                        okBtn.className = 'btn-admin btn-admin-primary';
                        okBtn.style.background = '#00e5ff';
                        okBtn.style.color = '#000';
                    }
                }

                if (iconWrap) {
                    if (isDanger) {
                        iconWrap.innerHTML = `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`;
                    } else {
                        iconWrap.innerHTML = `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#00e5ff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>`;
                    }
                }

                function cleanup() {
                    modal.classList.remove('is-open');
                    modal.style.display = 'none';
                    document.removeEventListener('keydown', handleKey);
                    if (okBtn) okBtn.onclick = null;
                    if (cancelBtn) cancelBtn.onclick = null;
                    if (closeX) closeX.onclick = null;
                    if (inputEl) inputEl.onkeydown = null;
                    modal.onclick = null;
                    window._confirmReject = null;
                }

                function handleKey(e) {
                    if (e.key === 'Escape') {
                        e.preventDefault();
                        cleanup();
                        resolve(isPrompt ? null : (isAlert ? true : false));
                    } else if (e.key === 'Enter' && !isPrompt) {
                        e.preventDefault();
                        cleanup();
                        resolve(true);
                    }
                }

                window._confirmReject = function() {
                    cleanup();
                    resolve(isPrompt ? null : (isAlert ? true : false));
                };

                document.addEventListener('keydown', handleKey);

                if (okBtn) {
                    okBtn.onclick = function() {
                        const val = inputEl ? inputEl.value : '';
                        cleanup();
                        resolve(isPrompt ? val : true);
                    };
                }
                if (cancelBtn) {
                    cancelBtn.onclick = function() {
                        cleanup();
                        resolve(isPrompt ? null : false);
                    };
                }
                if (closeX) {
                    closeX.onclick = function() {
                        cleanup();
                        resolve(isPrompt ? null : (isAlert ? true : false));
                    };
                }
                modal.onclick = function(e) {
                    if (e.target === modal) {
                        cleanup();
                        resolve(isPrompt ? null : (isAlert ? true : false));
                    }
                };

                if (inputEl && isPrompt) {
                    inputEl.onkeydown = function(e) {
                        if (e.key === 'Enter') {
                            e.preventDefault();
                            const val = inputEl.value;
                            cleanup();
                            resolve(val);
                        }
                    };
                }

                modal.style.display = 'flex';
                modal.classList.add('is-open');
                if (isPrompt && inputEl) {
                    setTimeout(() => { inputEl.focus(); inputEl.select(); }, 40);
                } else if (okBtn) {
                    okBtn.focus();
                }
            });
        };

        window.showAlertModal = function(opts) {
            const defaults = { isAlert: true, danger: false, title: 'SYSTEM NOTICE', confirmText: 'ACKNOWLEDGE' };
            const payload = typeof opts === 'string' ? Object.assign(defaults, { message: opts }) : Object.assign(defaults, opts);
            return window.showConfirmModal(payload);
        };

        window.showPromptModal = function(opts) {
            const defaults = { isPrompt: true, danger: false, title: 'INPUT REQUIRED', confirmText: 'SUBMIT', cancelText: 'CANCEL' };
            const payload = typeof opts === 'string' ? Object.assign(defaults, { message: opts }) : Object.assign(defaults, opts);
            return window.showConfirmModal(payload);
        };

        // ========================================================
        // GLOBAL SAFETY OVERRIDES: ERADICATE CHROME NATIVE POPUPS
        // ========================================================
        window.alert = function(msg) {
            if (typeof window.showToast === 'function') {
                window.showToast(String(msg), 'info');
            } else {
                console.warn('[NATIVE ALERT SUPPRESSED]:', msg);
            }
        };

        window.confirm = function(msg) {
            console.warn('[NATIVE CONFIRM SUPPRESSED — USE await showConfirmModal INSTEAD]:', msg);
            if (typeof window.showConfirmModal === 'function') {
                window.showConfirmModal({ message: String(msg) });
            }
            return false;
        };

        window.prompt = function(msg, defaultValue) {
            console.warn('[NATIVE PROMPT SUPPRESSED — USE await showPromptModal INSTEAD]:', msg);
            if (typeof window.showPromptModal === 'function') {
                window.showPromptModal({ message: String(msg), defaultValue: defaultValue });
            }
            return null;
        };

        // ==========================================
        // AUDIT LOGS PAGINATION & SEARCH (30 / PAGE)
        // ==========================================
        let auditCurrentPage = 1;
        const AUDIT_PAGE_SIZE = 30;

        function goToAuditPrevPage() {
            if (auditCurrentPage > 1) {
                auditCurrentPage--;
                renderAuditPagination();
                const wrap = document.querySelector('#mod-audit .admin-table-wrap');
                if (wrap) wrap.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        }

        function goToAuditNextPage() {
            const matchingRows = getMatchingAuditRows();
            const totalPages = Math.max(1, Math.ceil(matchingRows.length / AUDIT_PAGE_SIZE));
            if (auditCurrentPage < totalPages) {
                auditCurrentPage++;
                renderAuditPagination();
                const wrap = document.querySelector('#mod-audit .admin-table-wrap');
                if (wrap) wrap.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        }

        function onAuditSearchInput(val) {
            const clearBtn = document.getElementById('audit-search-clear-btn');
            if (clearBtn) {
                clearBtn.style.display = (val && val.trim().length > 0) ? 'inline-block' : 'none';
            }
            auditCurrentPage = 1;
            renderAuditPagination();
        }

        function clearAuditSearch() {
            const input = document.getElementById('audit-search-input');
            const clearBtn = document.getElementById('audit-search-clear-btn');
            if (input) {
                input.value = '';
                input.focus();
            }
            if (clearBtn) clearBtn.style.display = 'none';
            auditCurrentPage = 1;
            renderAuditPagination();
        }

        function getMatchingAuditRows() {
            const searchInput = document.getElementById('audit-search-input');
            const query = (searchInput ? searchInput.value : '').toLowerCase().trim();
            const rows = document.querySelectorAll('#mod-audit table#audit-table tbody tr.audit-row');
            const matching = [];

            rows.forEach(row => {
                const searchData = (row.getAttribute('data-search') || row.textContent || '').toLowerCase();
                if (!query || searchData.includes(query)) {
                    matching.push(row);
                }
            });
            return matching;
        }

        function renderAuditPagination() {
            const allRows = document.querySelectorAll('#mod-audit table#audit-table tbody tr.audit-row');
            const matchingRows = getMatchingAuditRows();
            const total = matchingRows.length;
            const totalPages = Math.max(1, Math.ceil(total / AUDIT_PAGE_SIZE));

            if (auditCurrentPage > totalPages) auditCurrentPage = totalPages;
            if (auditCurrentPage < 1) auditCurrentPage = 1;

            const startIndex = (auditCurrentPage - 1) * AUDIT_PAGE_SIZE;
            const endIndex = Math.min(startIndex + AUDIT_PAGE_SIZE, total);

            allRows.forEach(row => {
                row.style.display = 'none';
            });

            for (let i = startIndex; i < endIndex; i++) {
                matchingRows[i].style.display = '';
            }

            const countEl = document.getElementById('audit-search-count');
            if (countEl) {
                countEl.textContent = `SHOWING ${total} EVENT${total === 1 ? '' : 'S'} (30 / PAGE)`;
            }

            const noResultsEl = document.getElementById('audit-no-results');
            if (noResultsEl) {
                noResultsEl.style.display = (total === 0) ? '' : 'none';
            }

            const pageRangeEl = document.getElementById('audit-page-range');
            if (pageRangeEl) {
                pageRangeEl.textContent = total === 0 ? '0–0' : `${startIndex + 1}–${endIndex}`;
            }
            const totalCountEl = document.getElementById('audit-total-count');
            if (totalCountEl) totalCountEl.textContent = total;

            const curPageEl = document.getElementById('audit-current-page');
            if (curPageEl) curPageEl.textContent = auditCurrentPage;

            const totPagesEl = document.getElementById('audit-total-pages');
            if (totPagesEl) totPagesEl.textContent = totalPages;

            const prevBtn = document.getElementById('btn-audit-prev');
            if (prevBtn) {
                prevBtn.disabled = (auditCurrentPage <= 1);
                prevBtn.style.opacity = (auditCurrentPage <= 1) ? '0.4' : '1';
                prevBtn.style.cursor = (auditCurrentPage <= 1) ? 'not-allowed' : 'pointer';
            }

            const nextBtn = document.getElementById('btn-audit-next');
            if (nextBtn) {
                nextBtn.disabled = (auditCurrentPage >= totalPages);
                nextBtn.style.opacity = (auditCurrentPage >= totalPages) ? '0.4' : '1';
                nextBtn.style.cursor = (auditCurrentPage >= totalPages) ? 'not-allowed' : 'pointer';
            }
        }

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', renderAuditPagination);
        } else {
            renderAuditPagination();
        }
