        const escHtml = window.escapeHtml || function(str) {
            if (str === null || str === undefined) return '';
            return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
        };

        function initCharts(data) {
            if (typeof Chart === 'undefined') {
                console.warn('Chart.js not loaded');
                return;
            }

            Chart.defaults.color = '#8c9096';
            Chart.defaults.font.family = "'JetBrains Mono', monospace";
            Chart.defaults.font.size = 11;
            Chart.defaults.plugins.tooltip.backgroundColor = '#1c1f22';
            Chart.defaults.plugins.tooltip.borderColor = 'rgba(255, 255, 255, 0.15)';
            Chart.defaults.plugins.tooltip.borderWidth = 1;
            Chart.defaults.plugins.tooltip.titleColor = '#ffffff';
            Chart.defaults.plugins.tooltip.bodyColor = '#f0f0f2';
            Chart.defaults.plugins.tooltip.padding = 10;
            Chart.defaults.plugins.legend.labels.usePointStyle = true;
            Chart.defaults.plugins.legend.labels.boxWidth = 8;
            Chart.defaults.plugins.legend.labels.color = '#f0f0f2';

            const timeline = data.timeline || {};
            const kpis = data.kpis || {};

            // 1. TIMELINE MULTI-AXIS CHART
            const ctxTimeline = document.getElementById('chart-timeline');
            if (ctxTimeline) {
                if (chartTimelineInstance) chartTimelineInstance.destroy();
                chartTimelineInstance = new Chart(ctxTimeline, {
                    type: 'line',
                    data: {
                        labels: timeline.labels || [],
                        datasets: [
                            {
                                label: 'PRODUCT CATALOG VIEWS',
                                data: timeline.product_views || [],
                                borderColor: '#38bdf8',
                                backgroundColor: 'rgba(56, 189, 248, 0.12)',
                                fill: true,
                                tension: 0.35,
                                borderWidth: 2,
                                yAxisID: 'y'
                            },
                            {
                                label: 'THREAT INTEL READS',
                                data: timeline.blog_views || [],
                                borderColor: '#a855f7',
                                backgroundColor: 'rgba(168, 85, 247, 0.12)',
                                fill: true,
                                tension: 0.35,
                                borderWidth: 2,
                                yAxisID: 'y'
                            },
                            {
                                label: 'AVG DWELL TIME (SEC)',
                                data: timeline.avg_dwell || [],
                                borderColor: '#ffffff',
                                borderDash: [4, 4],
                                fill: false,
                                tension: 0.2,
                                borderWidth: 1.5,
                                yAxisID: 'y1'
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: { mode: 'index', intersect: false },
                        scales: {
                            x: {
                                grid: { color: 'rgba(255, 255, 255, 0.05)' }
                            },
                            y: {
                                type: 'linear',
                                display: true,
                                position: 'left',
                                grid: { color: 'rgba(255, 255, 255, 0.05)' },
                                title: { display: true, text: 'PAGE VIEWS', color: '#8c9096', font: { size: 10 } }
                            },
                            y1: {
                                type: 'linear',
                                display: true,
                                position: 'right',
                                grid: { drawOnChartArea: false },
                                title: { display: true, text: 'DWELL SECONDS', color: '#ffffff', font: { size: 10 } }
                            }
                        }
                    }
                });
            }

            // 2. CONVERSION FUNNEL BAR CHART
            const ctxFunnel = document.getElementById('chart-funnel');
            if (ctxFunnel) {
                if (chartFunnelInstance) chartFunnelInstance.destroy();
                chartFunnelInstance = new Chart(ctxFunnel, {
                    type: 'bar',
                    data: {
                        labels: ['SMART AD IMPRESSIONS', 'NATIVE AD CLICKS', 'CART ADDITIONS', 'TELEGRAM BUY INTENT'],
                        datasets: [{
                            label: 'TOTAL CONVERSION EVENTS',
                            data: [
                                kpis.smart_ad_impressions || 0,
                                kpis.smart_ad_clicks || 0,
                                kpis.cart_adds || 0,
                                kpis.telegram_buy_clicks || 0
                            ],
                            backgroundColor: [
                                'rgba(255, 255, 255, 0.25)',
                                '#38bdf8',
                                '#f59e0b',
                                '#22c55e'
                            ],
                            borderColor: [
                                'rgba(255, 255, 255, 0.5)',
                                '#38bdf8',
                                '#f59e0b',
                                '#22c55e'
                            ],
                            borderWidth: 1,
                            borderRadius: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                            y: { grid: { color: 'rgba(255, 255, 255, 0.05)' } }
                        }
                    }
                });
            }

            // 3. CLIENT BROWSER & USER AGENT ARCHITECTURE DOUGHNUT
            const ctxOs = document.getElementById('chart-os');
            if (ctxOs) {
                if (chartOsInstance) chartOsInstance.destroy();
                const browserList = data.browser_breakdown || [];
                let labels = [];
                let counts = [];
                if (browserList.length > 0) {
                    labels = browserList.map(b => b.browser);
                    counts = browserList.map(b => b.count);
                } else {
                    const osBreakdown = data.os_breakdown || [];
                    labels = osBreakdown.map(o => o.os);
                    counts = osBreakdown.map(o => o.count);
                }
                chartOsInstance = new Chart(ctxOs, {
                    type: 'doughnut',
                    data: {
                        labels: labels.length ? labels : ['Chrome', 'Firefox', 'Safari', 'Edge', 'Other'],
                        datasets: [{
                            data: counts.length ? counts : [55, 25, 10, 6, 4],
                            backgroundColor: ['#00e5ff', '#10b981', '#f59e0b', '#38bdf8', '#a855f7', '#64748b'],
                            borderColor: '#141618',
                            borderWidth: 3
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { position: 'right' }
                        },
                        cutout: '65%'
                    }
                });
            }

            // 4. ATTACK SURFACE CATEGORIES
            const ctxCategory = document.getElementById('chart-category');
            if (ctxCategory) {
                if (chartCategoryInstance) chartCategoryInstance.destroy();
                const blogs = data.blogs || [];
                const catCounts = {};
                blogs.forEach(b => {
                    const tag = b.cve_id ? b.cve_id.split('-')[0] + ' (' + (b.severity || 'CRIT') + ')' : 'Advisory';
                    catCounts[b.title.substring(0, 22) + '...'] = b.views || 10;
                });

                chartCategoryInstance = new Chart(ctxCategory, {
                    type: 'polarArea',
                    data: {
                        labels: Object.keys(catCounts).length ? Object.keys(catCounts) : ['Kernel eBPF', 'OAuth2 Smuggle', 'PKINIT Kerberos', 'K8s Lua RCE'],
                        datasets: [{
                            data: Object.values(catCounts).length ? Object.values(catCounts) : [45, 38, 28, 42],
                            backgroundColor: [
                                'rgba(56, 189, 248, 0.65)',
                                'rgba(168, 85, 247, 0.65)',
                                'rgba(34, 197, 94, 0.65)',
                                'rgba(245, 158, 11, 0.65)'
                            ],
                            borderColor: '#141618',
                            borderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { position: 'right' }
                        },
                        scales: {
                            r: {
                                grid: { color: 'rgba(255, 255, 255, 0.08)' },
                                angleLines: { color: 'rgba(255, 255, 255, 0.08)' },
                                ticks: { backdropColor: 'transparent', color: '#8c9096' }
                            }
                        }
                    }
                });
            }
        }

        // ==========================================
        // RENDER DETAILED PERFORMANCE TABLES
        // ==========================================
        window.CURRENT_ANALYTICS_DATA = null;
        let matrixActiveTable = 'products';
        let matrixCurrentPage = 1;
        const MATRIX_PAGE_SIZE = 20;

        function renderAnalyticsTables(data) {
            window.CURRENT_ANALYTICS_DATA = data;

            // 1. Products Table (LAST 10 PREVIEW)
            const tbodyProds = document.getElementById('tbody-products-analytics');
            if (tbodyProds) {
                const prods = (data.products || []).slice(0, 10);
                tbodyProds.innerHTML = prods.map(p => `
                    <tr>
                        <td style="font-weight:700;">${escHtml(p.sku)}</td>
                        <td style="font-weight:600; color:#fff;">${escHtml(p.name)}</td>
                        <td>$${Math.round(p.price || 0)}</td>
                        <td><strong>${escHtml(p.views)}</strong></td>
                        <td style="color:var(--admin-muted);">${escHtml(p.uniques)}</td>
                        <td>${escHtml(p.avg_stay_sec)}s</td>
                        <td>${escHtml(p.avg_scroll_pct)}%</td>
                        <td>${escHtml(p.cart_adds)}</td>
                        <td style="color:var(--admin-accent-green); font-weight:700;">${escHtml(p.tg_buys)}</td>
                        <td>
                            <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:${Math.min(100, (p.conversion_pct || 0) * 3)}%;"></div></div>
                            ${escHtml(p.conversion_pct)}%
                        </td>
                    </tr>
                `).join('') || '<tr><td colspan="10" style="text-align:center; color:var(--admin-muted);">No product telemetry captured.</td></tr>';
            }

            // 2. Blogs Table (LAST 10 PREVIEW)
            const tbodyBlogs = document.getElementById('tbody-blogs-analytics');
            if (tbodyBlogs) {
                const blogs = (data.blogs || []).slice(0, 10);
                tbodyBlogs.innerHTML = blogs.map(b => `
                    <tr>
                        <td style="font-weight:700;"><span class="status-pill">${escHtml(b.cve_id || 'ADVISORY')}</span></td>
                        <td style="font-weight:600; color:#fff;">${escHtml(b.title)}</td>
                        <td><span class="status-pill ${b.severity === 'CRITICAL' ? 'critical' : ''}">${escHtml(b.severity)}</span></td>
                        <td><strong>${escHtml(b.views)}</strong></td>
                        <td style="color:var(--admin-muted);">${escHtml(b.uniques)}</td>
                        <td>${escHtml(b.avg_stay_sec)}s</td>
                        <td>${escHtml(b.avg_scroll_pct)}%</td>
                        <td>${escHtml(b.ad_impressions)}</td>
                        <td>${escHtml(b.ad_clicks)}</td>
                        <td style="color:var(--admin-accent-cyan); font-weight:700;">${escHtml(b.ad_ctr_pct)}%</td>
                    </tr>
                `).join('') || '<tr><td colspan="10" style="text-align:center; color:var(--admin-muted);">No advisory telemetry captured.</td></tr>';
            }

            // 3. Live Stream Table (LAST 10 PREVIEW)
            const tbodyStream = document.getElementById('tbody-stream-analytics');
            if (tbodyStream) {
                const stream = (data.recent_stream || []).slice(0, 10);
                tbodyStream.innerHTML = stream.map(s => {
                    const rawUa = s.user_agent || (s.device_type + ' / ' + s.os_name);
                    const shortUa = rawUa.length > 38 ? rawUa.substring(0, 35) + '...' : rawUa;
                    const ipAddr = s.ip_address || '127.0.0.1';
                    const targetLabel = s.target_title || s.target_slug || '';
                    return `
                    <tr>
                        <td style="color:var(--admin-muted); font-family:var(--admin-font-mono);">${escHtml(s.visit_token)}</td>
                        <td><span class="status-pill">${escHtml(s.page_type)}</span></td>
                        <td style="font-weight:600; max-width:200px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
                            ${escHtml(targetLabel)}
                        </td>
                        <td title="${escHtml(rawUa)}" style="max-width:220px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:#00e5ff; font-family:var(--admin-font-mono); font-size:10.5px;">
                            ${escHtml(shortUa)}
                        </td>
                        <td style="font-family:var(--admin-font-mono); color:#10b981; font-weight:700;">${escHtml(ipAddr)}</td>
                        <td>${escHtml(s.duration_seconds)}s</td>
                        <td>${escHtml(s.max_scroll_pct)}%</td>
                        <td style="color:var(--admin-muted);">${escHtml(s.referrer || 'Direct')}</td>
                        <td style="color:var(--admin-muted);">${escHtml(s.created_at)}</td>
                    </tr>
                `;
                }).join('') || '<tr><td colspan="9" style="text-align:center; color:var(--admin-muted);">No recent stream events.</td></tr>';
            }

            // Also update the full matrix paginated table if active
            if (typeof renderFullMatrixPage === 'function') {
                renderFullMatrixPage();
            }
        }

        // DEDICATED FULL MATRIX LOGIC (20 PER PAGE WITH NEXT/PREV)
        // ========================================================
        function switchFullMatrixTable(tableType, btn) {
            matrixActiveTable = tableType;
            matrixCurrentPage = 1;
            document.querySelectorAll('#mod-analytics-matrix .subnav-btn').forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');

            const p = document.getElementById('full-matrix-products');
            const b = document.getElementById('full-matrix-blogs');
            const s = document.getElementById('full-matrix-stream');
            if (p) p.style.display = (tableType === 'products') ? 'block' : 'none';
            if (b) b.style.display = (tableType === 'blogs') ? 'block' : 'none';
            if (s) s.style.display = (tableType === 'stream') ? 'block' : 'none';

            renderFullMatrixPage();
        }

        function renderFullMatrixPage() {
            try {
                const data = window.CURRENT_ANALYTICS_DATA || window.INITIAL_ANALYTICS_DATA || {};
                let list = [];
                if (matrixActiveTable === 'products') list = data.products || [];
                else if (matrixActiveTable === 'blogs') list = data.blogs || [];
                else if (matrixActiveTable === 'stream') list = data.recent_stream || [];

                const totalCount = list.length;
                const totalPages = Math.max(1, Math.ceil(totalCount / MATRIX_PAGE_SIZE));
                if (matrixCurrentPage > totalPages) matrixCurrentPage = totalPages;
                if (matrixCurrentPage < 1) matrixCurrentPage = 1;

                const startIdx = (matrixCurrentPage - 1) * MATRIX_PAGE_SIZE;
                const endIdx = Math.min(startIdx + MATRIX_PAGE_SIZE, totalCount);
                const pageItems = list.slice(startIdx, endIdx);

                // Update pagination indicator
                const rangeEl = document.getElementById('matrix-page-range');
                const countEl = document.getElementById('matrix-total-count');
                const pageEl = document.getElementById('matrix-current-page');
                const totalPagesEl = document.getElementById('matrix-total-pages');
                const prevBtn = document.getElementById('btn-matrix-prev');
                const nextBtn = document.getElementById('btn-matrix-next');

                if (rangeEl) rangeEl.textContent = totalCount ? `${startIdx + 1}–${endIdx}` : '0–0';
                if (countEl) countEl.textContent = totalCount;
                if (pageEl) pageEl.textContent = matrixCurrentPage;
                if (totalPagesEl) totalPagesEl.textContent = totalPages;
                if (prevBtn) prevBtn.disabled = (matrixCurrentPage <= 1);
                if (nextBtn) nextBtn.disabled = (matrixCurrentPage >= totalPages);

                // Reset scroll position on active table viewport so new page starts at top
                const activeVp = document.getElementById(
                    matrixActiveTable === 'products' ? 'full-matrix-products' :
                    matrixActiveTable === 'blogs' ? 'full-matrix-blogs' : 'full-matrix-stream'
                );
                if (activeVp) activeVp.scrollTop = 0;

                // Render active table
                if (matrixActiveTable === 'products') {
                    const tbody = document.getElementById('tbody-products-full');
                    if (tbody) {
                        tbody.innerHTML = pageItems.map(p => `
                            <tr>
                                <td style="font-weight:700;">${escHtml(p.sku)}</td>
                                <td style="font-weight:600; color:#fff;">${escHtml(p.name)}</td>
                                <td>$${Math.round(p.price || 0)}</td>
                                <td><strong>${escHtml(p.views)}</strong></td>
                                <td style="color:var(--admin-muted);">${escHtml(p.uniques)}</td>
                                <td>${escHtml(p.avg_stay_sec)}s</td>
                                <td>${escHtml(p.avg_scroll_pct)}%</td>
                                <td>${escHtml(p.cart_adds)}</td>
                                <td style="color:var(--admin-accent-green); font-weight:700;">${escHtml(p.tg_buys)}</td>
                                <td>
                                    <div class="progress-bar-bg"><div class="progress-bar-fill" style="width:${Math.min(100, (p.conversion_pct || 0) * 3)}%;"></div></div>
                                    ${escHtml(p.conversion_pct)}%
                                </td>
                            </tr>
                        `).join('') || '<tr><td colspan="10" style="text-align:center; color:var(--admin-muted);">No product records on this page.</td></tr>';
                    }
                } else if (matrixActiveTable === 'blogs') {
                    const tbody = document.getElementById('tbody-blogs-full');
                    if (tbody) {
                        tbody.innerHTML = pageItems.map(b => `
                            <tr>
                                <td style="font-weight:700;"><span class="status-pill">${escHtml(b.cve_id || 'ADVISORY')}</span></td>
                                <td style="font-weight:600; color:#fff;">${escHtml(b.title)}</td>
                                <td><span class="status-pill ${b.severity === 'CRITICAL' ? 'critical' : ''}">${escHtml(b.severity)}</span></td>
                                <td><strong>${escHtml(b.views)}</strong></td>
                                <td style="color:var(--admin-muted);">${escHtml(b.uniques)}</td>
                                <td>${escHtml(b.avg_stay_sec)}s</td>
                                <td>${escHtml(b.avg_scroll_pct)}%</td>
                                <td>${escHtml(b.ad_impressions)}</td>
                                <td>${escHtml(b.ad_clicks)}</td>
                                <td style="color:var(--admin-accent-cyan); font-weight:700;">${escHtml(b.ad_ctr_pct)}%</td>
                            </tr>
                        `).join('') || '<tr><td colspan="10" style="text-align:center; color:var(--admin-muted);">No advisory records on this page.</td></tr>';
                    }
                } else if (matrixActiveTable === 'stream') {
                    const tbody = document.getElementById('tbody-stream-full');
                    if (tbody) {
                        tbody.innerHTML = pageItems.map(s => {
                            const rawUa = s.user_agent || (s.device_type + ' / ' + s.os_name);
                            const shortUa = rawUa.length > 40 ? rawUa.substring(0, 37) + '...' : rawUa;
                            const ipAddr = s.ip_address || '127.0.0.1';
                            const targetLabel = s.target_title || s.target_slug || '';
                            return `
                            <tr>
                                <td style="color:var(--admin-muted); font-family:var(--admin-font-mono);">${escHtml(s.visit_token)}</td>
                                <td><span class="status-pill">${escHtml(s.page_type)}</span></td>
                                <td style="font-weight:600; max-width:200px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
                                    ${escHtml(targetLabel)}
                                </td>
                                <td title="${escHtml(rawUa)}" style="max-width:220px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:#00e5ff; font-family:var(--admin-font-mono); font-size:10.5px;">
                                    ${escHtml(shortUa)}
                                </td>
                                <td style="font-family:var(--admin-font-mono); color:#10b981; font-weight:700;">${escHtml(ipAddr)}</td>
                                <td>${escHtml(s.duration_seconds)}s</td>
                                <td>${escHtml(s.max_scroll_pct)}%</td>
                                <td style="color:var(--admin-muted);">${escHtml(s.referrer || 'Direct')}</td>
                                <td style="color:var(--admin-muted);">${escHtml(s.created_at)}</td>
                            </tr>
                        `;
                        }).join('') || '<tr><td colspan="9" style="text-align:center; color:var(--admin-muted);">No stream events on this page.</td></tr>';
                    }
                }
            } catch(e) {
                console.error('Error rendering full matrix page:', e);
            }
        }

        function goToMatrixPrevPage() {
            if (matrixCurrentPage > 1) {
                matrixCurrentPage--;
                renderFullMatrixPage();
            }
        }

        function goToMatrixNextPage() {
            matrixCurrentPage++;
            renderFullMatrixPage();
        }

        // ==========================================
        // DYNAMIC TIMEFRAME ANALYTICS FETCHER
        // ==========================================
        async function loadAnalytics(days, btnElement) {
            currentDays = days;
            if (btnElement) {
                document.querySelectorAll('.btn-range').forEach(b => b.classList.remove('active'));
                btnElement.classList.add('active');
            }

            try {
                const res = await fetch('/api/admin/analytics/summary?days=' + days);
                const data = await res.json();

                // Update KPIs
                const k = data.kpis || {};
                document.getElementById('kpi-total-views').textContent = k.total_views || 0;
                document.getElementById('kpi-uniques-note').textContent = (k.unique_visitors || 0) + ' Unique Hardware Fingerprints';
                document.getElementById('kpi-active-now').textContent = k.active_visitors_now || 1;
                document.getElementById('kpi-avg-dwell').textContent = (k.avg_dwell_seconds || 0) + 's';
                document.getElementById('kpi-scroll-note').textContent = (k.avg_scroll_pct || 0) + '% Average Page Scroll Depth';
                document.getElementById('kpi-smart-ctr').textContent = (k.smart_ad_ctr_pct || 0) + '%';
                document.getElementById('kpi-ad-clicks-note').textContent = (k.smart_ad_clicks || 0) + ' Clicks / ' + (k.smart_ad_impressions || 0) + ' Ad Views';
                document.getElementById('kpi-tg-clicks').textContent = k.telegram_buy_clicks || 0;
                document.getElementById('kpi-cart-adds-note').textContent = (k.cart_adds || 0) + ' Bags Created Across Arsenal';
                if (k.pipeline_revenue !== undefined) {
                    document.getElementById('kpi-pipeline-rev').textContent = '$' + Number(k.pipeline_revenue).toFixed(2);
                }

                // Re-render charts & tables
                initCharts(data);
                renderAnalyticsTables(data);
            } catch (err) {
                console.error('Error fetching analytics:', err);
            }
        }

        // ==========================================
        // ORDERS FULFILLMENT LOGIC
        // ==========================================
