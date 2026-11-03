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
                if (subtabName === 'catalog') targetModId = 'mod-products';
                else if (subtabName === 'studio') targetModId = 'mod-product-editor';
                else if (subtabName === 'curation') {
                    targetModId = 'mod-curation-products';
                    if (typeof initHomeCurationPreviews === 'function') initHomeCurationPreviews();
                }
                else if (subtabName === 'reviews') targetModId = 'mod-reviews';
                else {
                    subtabName = 'catalog';
                    targetModId = 'mod-products';
                }
                if (adminContainer) adminContainer.classList.remove('themes-mode');
            } else if (feature === 'journal') {
                if (subtabName === 'dispatches') targetModId = 'mod-posts';
                else if (subtabName === 'studio') targetModId = 'mod-post-editor';
                else if (subtabName === 'curation') {
                    targetModId = 'mod-curation-posts';
                    if (typeof initHomeCurationPreviews === 'function') initHomeCurationPreviews();
                }
                else if (subtabName === 'comments') targetModId = 'mod-comments';
                else {
                    subtabName = 'dispatches';
                    targetModId = 'mod-posts';
                }
                if (adminContainer) adminContainer.classList.remove('themes-mode');
            } else if (feature === 'orders') {
                targetModId = 'mod-orders';
                if (subtabName === 'pending') {
                    filterAdminOrders('PENDING', document.querySelector('.order-filter-btn[onclick*="PENDING"]'));
                } else {
                    subtabName = 'all';
                    filterAdminOrders('ALL', document.querySelector('.order-filter-btn[onclick*="ALL"]'));
                }
                if (adminContainer) adminContainer.classList.remove('themes-mode');
            } else if (feature === 'system') {
                if (subtabName === 'settings') targetModId = 'mod-settings';
                else if (subtabName === 'seo') {
                    targetModId = 'mod-seo';
                    setTimeout(() => {
                        if (typeof updateSeoLivePreview === 'function') updateSeoLivePreview();
                    }, 50);
                }
                else if (subtabName === 'themes-visual' || subtabName === 'themes') {
                    targetModId = 'mod-themes-visual';
                    if (adminContainer) adminContainer.classList.add('themes-mode');
                    setTimeout(() => {
                        if (typeof applyThemeViewportDimensions === 'function') applyThemeViewportDimensions();
                        if (typeof setupIframeInspectListeners === 'function') setupIframeInspectListeners();
                    }, 60);
                } else if (subtabName === 'themes-text') {
                    targetModId = 'mod-themes-text';
                } else if (subtabName === 'users') targetModId = 'mod-users';
                else if (subtabName === 'audit') targetModId = 'mod-audit';
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
                    const txt = (statusPill ? statusPill.textContent : '').toUpperCase();
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
            if (el) el.classList.add('is-open');
        }

        function closeModal(id) {
            const el = document.getElementById(id);
            if (el) el.classList.remove('is-open');
        }

        // Close any open modal on ESC key or backdrop click
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                document.querySelectorAll('.admin-modal.is-open').forEach(m => m.classList.remove('is-open'));
            }
        });
        document.addEventListener('DOMContentLoaded', function() {
            document.querySelectorAll('.admin-modal').forEach(m => {
                m.addEventListener('click', function(e) {
                    if (e.target === m) m.classList.remove('is-open');
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
