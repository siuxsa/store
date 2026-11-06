        async function saveSettings(e) {
            e.preventDefault();
            const form = document.getElementById('settings-form');
            const formData = new FormData(form);
            const payload = {};
            formData.forEach((val, key) => { payload[key] = val; });

            const res = await fetch('/api/admin/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (data.ok || data.success) {
                const currentPath = window.location.pathname.replace(/\/+$/, '') || '/admin';
                const newAdminUrl = (data.admin_panel_url || '').replace(/\/+$/, '');
                if (newAdminUrl && newAdminUrl !== currentPath) {
                    showToast(`Admin path updated to ${newAdminUrl}. Redirecting...`, 'success');
                    setTimeout(() => { window.location.href = newAdminUrl; }, 500);
                } else {
                    showToast(data.message || 'System configuration updated successfully.', 'success');
                }
            } else {
                showToast(data.error || 'Settings error', 'error');
            }
        }

        // ========================================================
        // SECURITY, RATE LIMITING & CUSTOM ADMIN PATH HELPERS
        // ========================================================
        function updateAdminPathPreview(rawVal) {
            const cleaned = String(rawVal || '').trim().replace(/^\/+|\/+$/g, '').toLowerCase() || 'admin';
            const dashEl = document.getElementById('preview-admin-dashboard-url');
            const loginEl = document.getElementById('preview-admin-login-url');
            const pillBox = document.getElementById('admin-stealth-status-pill');
            if (dashEl) dashEl.textContent = '/' + cleaned;
            if (loginEl) loginEl.textContent = '/' + cleaned + '/login';
            if (pillBox) {
                if (cleaned !== 'admin') {
                    pillBox.innerHTML = `<span class="status-pill completed" style="background:rgba(16,185,129,0.18); color:#10b981; border:1px solid rgba(16,185,129,0.4); font-size:10px; font-weight:800;">● STEALTH PATH PREVIEW (/${cleaned})</span>`;
                } else {
                    pillBox.innerHTML = `<span class="status-pill" style="background:rgba(245,158,11,0.15); color:#f59e0b; border:1px solid rgba(245,158,11,0.35); font-size:10px; font-weight:800;">● DEFAULT PATH (/admin)</span>`;
                }
            }
        }

        function generateRandomAdminPath() {
            const prefixes = ['cyber-gate', 'ops-console', 'vault-matrix', 'sec-command', 'zero-panel'];
            const prefix = prefixes[Math.floor(Math.random() * prefixes.length)];
            const randHex = Array.from({ length: 4 }, () => Math.floor(Math.random() * 16).toString(16)).join('');
            const slug = `${prefix}-${randHex}`;
            const input = document.getElementById('input-admin-custom-path');
            if (input) {
                input.value = slug;
                updateAdminPathPreview(slug);
                showToast(`Generated stealth admin path: /${slug} (Click Save to activate)`, 'success');
            }
        }

        function resetAdminPathDefault() {
            const input = document.getElementById('input-admin-custom-path');
            if (input) {
                input.value = 'admin';
                updateAdminPathPreview('admin');
            }
        }

        function copyAdminGatewayUrl(kind) {
            const input = document.getElementById('input-admin-custom-path');
            const slug = String((input && input.value) || 'admin').trim().replace(/^\/+|\/+$/g, '').toLowerCase() || 'admin';
            const fullUrl = window.location.origin + '/' + slug + (kind === 'login' ? '/login' : '');
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(fullUrl).then(() => {
                    showToast(`Copied URL: ${fullUrl}`, 'success');
                }).catch(() => {});
            }
        }

        async function refreshSecurityTelemetry() {
            try {
                const res = await fetch('/api/admin/security/telemetry');
                const data = await res.json();
                if (data.ok && data.telemetry) {
                    const t = data.telemetry;
                    const elBlocks = document.getElementById('rl-stat-active-blocks');
                    const elBuckets = document.getElementById('rl-stat-tracked-buckets');
                    const elTotal = document.getElementById('rl-stat-total-throttled');
                    const box = document.getElementById('rl-recent-events-box');
                    if (elBlocks) elBlocks.textContent = String(t.active_blocks_count || 0);
                    if (elBuckets) elBuckets.textContent = String(t.tracked_buckets_count || 0);
                    if (elTotal) elTotal.textContent = String(t.total_throttled || 0);
                    if (box) {
                        if (t.active_blocks && t.active_blocks.length > 0) {
                            const esc = window.escapeHtml || function(s){ return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;'); };
                            let html = '<div style="color:#ef4444; font-weight:700; margin-bottom:0.4rem;">ACTIVE COOLDOWN BLOCKS:</div>';
                            t.active_blocks.forEach(b => {
                                html += `<div style="padding:0.35rem 0; border-bottom:1px solid rgba(255,255,255,0.06); display:flex; justify-content:space-between;">
                                    <span>IP: <strong style="color:#fff;">${esc(b.ip)}</strong> · Scope: <span style="color:#00e5ff;">${esc(b.scope)}</span> · Path: ${esc(b.path)}</span>
                                    <span style="color:#f59e0b;">${esc(b.remaining_seconds)}s remaining</span>
                                </div>`;
                            });
                            box.innerHTML = html;
                        } else {
                            box.innerHTML = '<div>No IP addresses are currently in an active HTTP 429 cooldown block.</div>';
                        }
                    }
                }
            } catch (err) {
                console.error('Failed to refresh security telemetry:', err);
            }
        }

        async function resetActiveRateLimits() {
            try {
                const res = await fetch('/api/admin/security/rate-limit-reset', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({})
                });
                const data = await res.json();
                if (data.ok) {
                    showToast(data.message || 'All active rate limits reset.', 'success');
                    refreshSecurityTelemetry();
                } else {
                    showToast(data.error || 'Failed to reset rate limits.', 'error');
                }
            } catch (err) {
                showToast('Network error: ' + err.message, 'error');
            }
        }

        // ========================================================
        // TELEMETRY & ANALYTICS DATA MANAGEMENT & EXPORT SYSTEM
        // ========================================================
        async function refreshDataStats() {
            try {
                const res = await fetch('/api/admin/data/stats');
                const data = await res.json();
                if (data.ok && data.stats) {
                    const s = data.stats;
                    const elPageviews = document.getElementById('dms-count-pageviews');
                    const elEvents = document.getElementById('dms-count-events');
                    const elVisitors = document.getElementById('dms-count-visitors');
                    const elRevenue = document.getElementById('dms-count-revenue');
                    const elDbSize = document.getElementById('dms-count-dbsize');

                    if (elPageviews) elPageviews.textContent = Number(s.pageviews || 0).toLocaleString();
                    if (elEvents) elEvents.textContent = Number(s.events || 0).toLocaleString();
                    if (elVisitors) elVisitors.textContent = Number(s.unique_visitors || 0).toLocaleString();
                    if (elRevenue) {
                        const revVal = Number(s.pipeline_revenue || 0).toFixed(2);
                        const ordCnt = Number(s.orders || 0);
                        elRevenue.textContent = `$${revVal} (${ordCnt} ord)`;
                    }
                    if (elDbSize) elDbSize.textContent = (s.db_size_kb || 0).toLocaleString() + ' KB';
                }
            } catch(err) {
                console.error('Failed to refresh telemetry stats:', err);
            }
        }

        function exportAnalyticsData(format, type) {
            let url = `/api/admin/analytics/export?format=${encodeURIComponent(format || 'json')}`;
            if (type) {
                url += `&type=${encodeURIComponent(type)}`;
            }
            showDmsBanner(`GENERATING EXPORT FILE (${(type || 'full').toUpperCase()} / ${format.toUpperCase()})...`, false);
            
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', '');
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

            setTimeout(() => {
                showDmsBanner(`✓ ANALYTICS EXPORT DOWNLOAD STARTED (${format.toUpperCase()})`, false);
            }, 800);
        }

        async function purgeDataAction(action, olderThanDays) {
            let confirmPrompt = 'Are you sure you want to clear these analytics records?';
            if (action === 'analytics_all') {
                confirmPrompt = olderThanDays
                    ? `Clear visitor pageviews, ad click events, and orders older than ${olderThanDays} days?\n\n(Products, articles, comments, reviews, and user accounts remain untouched.)`
                    : `This will clear ALL visitor pageviews, ad click events, and order history, resetting revenue metrics to $0.00.\n\n(Products, articles, verified reviews, comments, and user accounts remain untouched.)\n\nProceed with analytics reset?`;
            } else if (action === 'analytics_orders' || action === 'analytics_revenue') {
                confirmPrompt = olderThanDays
                    ? `Clear orders and revenue records older than ${olderThanDays} days?`
                    : `This will delete ALL order records and reset total revenue to $0.00.\n\nProceed with clearing orders?`;
            } else if (action === 'analytics_pageviews') {
                confirmPrompt = olderThanDays
                    ? `Clear visitor pageviews older than ${olderThanDays} days?`
                    : `Clear ALL visitor pageview records? (Orders and store content are unaffected)`;
            } else if (action === 'analytics_events') {
                confirmPrompt = olderThanDays
                    ? `Clear ad click events older than ${olderThanDays} days?`
                    : `Clear ALL ad click event records? (Store content is unaffected)`;
            }

            const confirmed = await showConfirmModal({
                title: 'CONFIRM DATA RESET',
                message: confirmPrompt,
                confirmText: 'CLEAR DATA',
                danger: true,
                note: 'WARNING: Selected analytics logs will be permanently deleted.'
            });
            if (!confirmed) {
                return;
            }

            showDmsBanner('CLEARING ANALYTICS RECORDS & OPTIMIZING DATABASE...', false);

            try {
                const res = await fetch('/api/admin/data/purge', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        action: action,
                        older_than_days: olderThanDays,
                        auto_vacuum: true
                    })
                });
                const data = await res.json();
                if (data.ok) {
                    const msg = `✓ SUCCESS: ${data.message} (Database footprint: ${data.db_size_kb} KB)`;
                    showDmsBanner(msg, false);
                    refreshDataStats();
                    if (typeof showThemeToast === 'function') {
                        showThemeToast(data.message);
                    }
                    // If analytics module exists and is loaded, refresh it too
                    if (typeof loadAnalytics === 'function' && typeof currentDays !== 'undefined') {
                        try { loadAnalytics(currentDays); } catch(e) {}
                    }
                } else {
                    showDmsBanner('PURGE ERROR: ' + (data.error || 'Failed to purge telemetry.'), true);
                }
            } catch(err) {
                showDmsBanner('NETWORK ERROR: ' + err.message, true);
            }
        }

        async function runDatabaseVacuum() {
            const confirmed = await showConfirmModal({
                title: 'OPTIMIZE DATABASE',
                message: 'Optimize and defragment database storage now? (SQLite VACUUM & REINDEX)',
                confirmText: 'OPTIMIZE NOW',
                danger: false,
                note: 'Defragments B-tree index tables and releases unallocated database file pages back to host storage.'
            });
            if (!confirmed) {
                return;
            }
            showDmsBanner('EXECUTING SQLITE VACUUM & REINDEX...', false);
            try {
                const res = await fetch('/api/admin/data/purge', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: 'vacuum' })
                });
                const data = await res.json();
                if (data.ok) {
                    showDmsBanner(`✓ SUCCESS: ${data.message} (Footprint: ${data.db_size_kb} KB)`, false);
                    refreshDataStats();
                    if (typeof showThemeToast === 'function') {
                        showThemeToast('Database optimized successfully.');
                    }
                } else {
                    showDmsBanner('OPTIMIZE ERROR: ' + (data.error || 'Failed to optimize.'), true);
                }
            } catch(err) {
                showDmsBanner('NETWORK ERROR: ' + err.message, true);
            }
        }

        function showDmsBanner(msg, isError) {
            const banner = document.getElementById('dms-status-banner');
            if (!banner) return;
            banner.style.display = 'block';
            if (isError) {
                banner.style.background = 'rgba(239,68,68,0.12)';
                banner.style.border = '1px solid #ef4444';
                banner.style.color = '#ef4444';
            } else {
                banner.style.background = 'rgba(16,185,129,0.12)';
                banner.style.border = '1px solid #10b981';
                banner.style.color = '#10b981';
            }
            banner.textContent = msg;
        }

        async function uploadBrandAsset(fileInput, fieldName) {
            if (!fileInput.files || !fileInput.files[0]) return;
            const file = fileInput.files[0];
            const formData = new FormData();
            formData.append('file', file);

            try {
                const res = await fetch('/api/admin/upload-image', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                if (data.ok && data.url) {
                    const input = document.getElementById('settings-' + fieldName);
                    if (input) {
                        input.value = data.url;
                    }
                    if (fieldName === 'site_logo') {
                        updateLogoLivePreview(data.url);
                    } else if (fieldName === 'site_favicon') {
                        updateFaviconLivePreview(data.url);
                    }
                } else {
                    showToast('Upload failed: ' + (data.error || 'Unknown error'), 'error');
                }
            } catch(err) {
                showToast('Upload error: ' + err.message, 'error');
            }
        }

        function updateLogoLivePreview(url) {
            const img = document.getElementById('settings-logo-preview');
            const empty = document.getElementById('settings-logo-preview-empty');
            if (url && url.trim()) {
                if (img) {
                    img.src = url.trim();
                    img.style.display = 'block';
                }
                if (empty) empty.style.display = 'none';
            } else {
                if (img) img.style.display = 'none';
                if (empty) empty.style.display = 'inline-block';
            }
        }

        function updateFaviconLivePreview(url) {
            const img = document.getElementById('settings-fav-preview');
            const fallback = document.getElementById('settings-fav-fallback');
            if (url && url.trim()) {
                if (img) {
                    img.src = url.trim();
                    img.style.display = 'block';
                }
                if (fallback) fallback.style.display = 'none';
            } else {
                if (img) img.style.display = 'none';
                if (fallback) fallback.style.display = 'block';
            }
        }

        function clearBrandAsset(fieldName) {
            const input = document.getElementById('settings-' + fieldName);
            if (input) input.value = '';
            if (fieldName === 'site_logo') updateLogoLivePreview('');
            if (fieldName === 'site_favicon') updateFaviconLivePreview('');
        }

        // ========================================================
        // SETTINGS SUBTAB SYSTEM & FORM ORCHESTRATION
        // ========================================================
        function switchSettingsTab(tabName, btn) {
            document.querySelectorAll('.settings-subnav-btn').forEach(b => {
                if (b.getAttribute('data-tab') === tabName || b === btn) {
                    b.classList.add('active');
                } else {
                    b.classList.remove('active');
                }
            });

            document.querySelectorAll('.settings-tab-pane').forEach(p => {
                p.style.display = 'none';
            });

            const target = document.getElementById(`settings-pane-${tabName}`);
            if (target) {
                target.style.display = 'block';
            }

            try {
                sessionStorage.setItem('activeSettingsTab', tabName);
            } catch(e) {}
        }

        function submitSettingsForm() {
            const form = document.getElementById('settings-form');
            if (form) {
                if (typeof form.requestSubmit === 'function') {
                    form.requestSubmit();
                } else {
                    form.dispatchEvent(new Event('submit', { cancelable: true }));
                }
            }
        }

        function insertTrackingTemplate(fieldName, type) {
            const textarea = document.querySelector(`textarea[name="${fieldName}"]`);
            if (!textarea) return;

            let snippet = '';
            if (type === 'ga4') {
                snippet = `<!-- Google tag (gtag.js) GA4 -->\n<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"><\/script>\n<script>\n  window.dataLayer = window.dataLayer || [];\n  function gtag(){dataLayer.push(arguments);}\n  gtag('js', new Date());\n  gtag('config', 'G-XXXXXXXXXX');\n<\/script>`;
            } else if (type === 'gtm') {
                snippet = `<!-- Google Tag Manager -->\n<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':\nnew Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],\nj=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=\n'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);\n})(window,document,'script','dataLayer','GTM-XXXXXXX');<\/script>`;
            } else if (type === 'script') {
                snippet = `<script>\n  // Custom tracking logic\n  console.log('Custom JS initialized');\n<\/script>`;
            }

            if (snippet) {
                if (!textarea.value.trim()) {
                    textarea.value = snippet;
                    textarea.focus();
                } else {
                    showConfirmModal({
                        title: 'OVERWRITE SCRIPT FIELD',
                        message: 'Replace existing script in this field with the selected tracking template?',
                        confirmText: 'OVERWRITE SCRIPT',
                        danger: false,
                        note: 'Existing custom JavaScript in this editor block will be overwritten.'
                    }).then(ok => {
                        if (ok) {
                            textarea.value = snippet;
                            textarea.focus();
                        }
                    });
                }
            }
        }

        async function clearTrackingField(fieldName) {
            const textarea = document.querySelector(`textarea[name="${fieldName}"]`);
            if (textarea && textarea.value.trim()) {
                const ok = await showConfirmModal({
                    title: 'CLEAR SCRIPT FIELD',
                    message: 'Clear all custom JavaScript code from this field?',
                    confirmText: 'CLEAR FIELD',
                    danger: true,
                    note: 'Script contents will be blanked out. Remember to click "SAVE SETTINGS" to commit changes.'
                });
                if (ok) {
                    textarea.value = '';
                }
            }
        }

        window.switchSettingsTab = switchSettingsTab;
        window.purgeDataAction = purgeDataAction;
        window.refreshDataStats = refreshDataStats;
        window.insertTrackingTemplate = insertTrackingTemplate;
        window.clearTrackingField = clearTrackingField;
        window.updateAdminPathPreview = updateAdminPathPreview;
        window.generateRandomAdminPath = generateRandomAdminPath;
        window.resetAdminPathDefault = resetAdminPathDefault;
        window.copyAdminGatewayUrl = copyAdminGatewayUrl;
        window.refreshSecurityTelemetry = refreshSecurityTelemetry;
        window.resetActiveRateLimits = resetActiveRateLimits;

        document.addEventListener('DOMContentLoaded', () => {
            refreshDataStats();
            refreshSecurityTelemetry();
            try {
                const savedTab = sessionStorage.getItem('activeSettingsTab');
                if (savedTab && document.getElementById(`settings-pane-${savedTab}`)) {
                    const btn = document.querySelector(`.settings-subnav-btn[data-tab="${savedTab}"]`);
                    switchSettingsTab(savedTab, btn);
                }
            } catch(e) {}
        });

