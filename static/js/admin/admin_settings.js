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
                alert('System configuration updated.');
                location.reload();
            } else {
                alert(data.error || 'Settings error');
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
                    const elDbSize = document.getElementById('dms-count-dbsize');

                    if (elPageviews) elPageviews.textContent = Number(s.pageviews || 0).toLocaleString();
                    if (elEvents) elEvents.textContent = Number(s.events || 0).toLocaleString();
                    if (elVisitors) elVisitors.textContent = Number(s.unique_visitors || 0).toLocaleString();
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
                showDmsBanner(`✓ TELEMETRY EXPORT DOWNLOAD INITIATED (${format.toUpperCase()})`, false);
            }, 800);
        }

        async function purgeDataAction(action, olderThanDays) {
            let confirmPrompt = 'Are you sure you want to execute this telemetry purge?';
            if (action === 'analytics_all') {
                confirmPrompt = olderThanDays
                    ? `Purge visitor pageviews and ad tracking events older than ${olderThanDays} days?\n\n(Core store data like reviews, comments, and orders remain 100% safe and untouched.)`
                    : `CRITICAL ACTION: This will purge ALL visitor pageviews, dwell times, and ad tracking events.\n\nNOTE: Verified customer reviews, comments, catalog items, and orders are maintained separately and will NOT be touched.\n\nProceed with complete telemetry reset?`;
            } else if (action === 'analytics_pageviews') {
                confirmPrompt = olderThanDays
                    ? `Purge visitor pageviews older than ${olderThanDays} days?`
                    : `Purge ALL visitor pageview and radar records? (Analytics pageviews will reset to 0; core site content is unaffected)`;
            } else if (action === 'analytics_events') {
                confirmPrompt = olderThanDays
                    ? `Purge ad & conversion tracking events older than ${olderThanDays} days?`
                    : `Purge ALL tracking and ad telemetry event records? (Core site content is unaffected)`;
            }

            if (!confirm(confirmPrompt)) {
                return;
            }

            showDmsBanner('PURGING TELEMETRY RECORDS & RECLAIMING DATABASE PAGES...', false);

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
                } else {
                    showDmsBanner('PURGE ERROR: ' + (data.error || 'Failed to purge telemetry.'), true);
                }
            } catch(err) {
                showDmsBanner('NETWORK ERROR: ' + err.message, true);
            }
        }

        async function runDatabaseVacuum() {
            if (!confirm('Optimize and defragment database storage now? (SQLite VACUUM & REINDEX)')) {
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
                    alert('Upload failed: ' + (data.error || 'Unknown error'));
                }
            } catch(err) {
                alert('Upload error: ' + err.message);
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

        document.addEventListener('DOMContentLoaded', () => {
            refreshDataStats();
        });

