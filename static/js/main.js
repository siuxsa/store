/**
 * ZERO//FORM — Global Navigation, Scroll Header, Search Overlay, Mobile Menu & Keyboard Shortcuts
 */

(function () {
    "use strict";

    // 1. Sticky Header Scroll Transition
    function initHeaderScroll() {
        const header = document.getElementById("site-header");
        if (!header) return;

        function onScroll() {
            if (window.scrollY > 44) {
                header.classList.add("is-scrolled");
                if (header.classList.contains("header-transparent")) {
                    header.classList.remove("header-transparent");
                    header.setAttribute("data-was-transparent", "true");
                }
            } else {
                header.classList.remove("is-scrolled");
                if (header.getAttribute("data-was-transparent") === "true") {
                    header.classList.add("header-transparent");
                }
            }
        }

        window.addEventListener("scroll", onScroll, { passive: true });
        onScroll();
    }

    // 2. Fullscreen Mobile Menu
    function openMobileMenu() {
        const menu = document.getElementById("mobile-menu");
        if (!menu) return;
        menu.classList.add("is-open");
        document.body.classList.add("no-scroll");
    }

    function closeMobileMenu() {
        const menu = document.getElementById("mobile-menu");
        if (!menu) return;
        menu.classList.remove("is-open");
        document.body.classList.remove("no-scroll");
    }

    // 3. Fullscreen Real-Time Search Overlay
    function openSearch() {
        const overlay = document.getElementById("search-overlay");
        const input = document.getElementById("search-overlay-input");
        if (!overlay) return;
        closeMobileMenu();
        overlay.classList.add("is-open");
        document.body.classList.add("no-scroll");
        renderSearchResults("");
        if (input) {
            input.value = "";
            setTimeout(function () { input.focus(); }, 120);
        }
    }

    function closeSearch() {
        const overlay = document.getElementById("search-overlay");
        if (!overlay) return;
        overlay.classList.remove("is-open");
        document.body.classList.remove("no-scroll");
    }

    function escapeHtml(str) {
        return String(str == null ? "" : str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function renderSearchResults(query) {
        const resultsEl = document.getElementById("search-results-grid");
        const countEl = document.getElementById("search-results-count");
        if (!resultsEl) return;

        const q = (query || "").trim().toLowerCase();
        const allProducts = window.NORTHFORM_PRODUCTS || [];

        const matched = q
            ? allProducts.filter(function (p) {
                const name = (p.name || "").toLowerCase();
                const sku = (p.sku || "").toLowerCase();
                const cat = (p.category || "").toLowerCase();
                const version = (p.version || "").toLowerCase();
                const shortDesc = (p.short_desc || "").toLowerCase();
                return name.includes(q) || sku.includes(q) || cat.includes(q) || version.includes(q) || shortDesc.includes(q);
            })
            : allProducts.slice(0, 4);

        if (countEl) {
            countEl.textContent = q
                ? matched.length + " SECURITY TOOL(S) MATCHING \"" + query.toUpperCase() + "\""
                : "FEATURED SECURITY TOOLS";
        }

        if (matched.length === 0) {
            resultsEl.innerHTML = `
                <div style="grid-column: 1 / -1; padding: 3rem 0; color: var(--muted); text-align: center;">
                    <p class="meta-label">NO SECURITY TOOLS FOUND FOR "${escapeHtml(query.toUpperCase())}"</p>
                    <p style="font-size: 0.85rem; margin-top: 0.5rem;">Try searching for "Burp", "Metasploit", "Splunk", "IDA", or "Cobalt".</p>
                </div>
            `;
            return;
        }

        resultsEl.innerHTML = matched.slice(0, 8).map(function (p) {
            const img = escapeHtml(p.image || p.image_url || "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=1200&q=85");
            const desc = escapeHtml(p.short_desc || (p.specs && p.specs.length ? p.specs.join(" · ") : "Commercial security license package."));
            const specs = escapeHtml((p.version || "v2026.1") + " · " + (p.platform || "Windows / Linux / macOS"));
            const discPct = p.discount_pct || (p.retail_price && p.price && p.retail_price > p.price ? Math.round(((p.retail_price - p.price) / p.retail_price) * 100) : 0);
            const discountBadgeHtml = discPct > 0 ? `<span class="product-discount-badge"><span class="discount-label">DISCOUNT</span><span class="discount-val">-${discPct}%</span></span>` : '';
            const retailHtml = (p.retail_price && p.price && p.retail_price > p.price) ? `<span class="product-price-retail">$${Math.round(p.retail_price)}</span>` : '';
            const prodUrl = "/product/" + encodeURIComponent(p.slug || p.sku || p.id);
            return `
            <div class="product-card">
                <a href="${prodUrl}" class="product-card-image-wrap">
                    <img src="${img}" alt="${escapeHtml(p.name)}" class="product-card-img" loading="lazy">
                    <span class="product-badge">${escapeHtml(p.badge_text || 'VERIFIED')}</span>
                    ${discountBadgeHtml}
                </a>
                <div class="product-meta">
                    <div class="product-meta-header">
                        <span class="meta-label">${escapeHtml(p.category)}</span>
                        <div class="product-price-wrap">
                            ${retailHtml}
                            <span class="product-price-current">$${Math.round(p.price)}</span>
                        </div>
                    </div>
                    <h3 class="product-title">
                        <a href="${prodUrl}">${escapeHtml(p.name)}</a>
                    </h3>
                    <p class="product-desc">${desc}</p>
                    <div class="product-specs-line">${specs}</div>
                    <div class="product-actions">
                        <button type="button" class="btn btn-outline-dark" style="flex:1; padding:0.45rem 0.5rem; font-size:0.68rem;" onclick="window.NFUI && window.NFUI.closeSearch(); window.NFCart && window.NFCart.quickAdd(${Number(p.id)}, null, this)">+ ADD</button>
                        <a href="${prodUrl}" class="btn btn-dark" style="padding:0.45rem 0.75rem; font-size:0.68rem;">VIEW →</a>
                    </div>
                </div>
            </div>
            `;
        }).join("");
    }

    function filterSearchTag(tag) {
        const input = document.getElementById("search-overlay-input");
        if (input) {
            input.value = tag;
            renderSearchResults(tag);
        }
    }

    function initKeyboardShortcuts() {
        document.addEventListener("keydown", function (e) {
            if (e.key === "Escape") {
                closeSearch();
                closeMobileMenu();
                if (window.NFCart && window.NFCart.close) {
                    window.NFCart.close();
                }
            }
            if (e.key === "/" && !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)) {
                e.preventDefault();
                openSearch();
            }
        });

        const searchInput = document.getElementById("search-overlay-input");
        if (searchInput) {
            let debounceTimer;
            searchInput.addEventListener("input", function (e) {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(function () {
                    renderSearchResults(e.target.value);
                }, 100);
            });
        }
    }

    // 4. Smart Dynamic Sticky Sidebars (Product Studio PDP & Threat Journal Detail)
    // Ensures sidebar data finishes scrolling cleanly into view, locks at viewport bottom/top,
    // and naturally scrolls away only when the long content column finishes.
    function initSmartStickySidebars() {
        const sidebarConfigs = [
            { el: document.querySelector('.journal-sidebar-column'), layout: document.querySelector('.journal-detail-layout') },
            { el: document.querySelector('.pdp-info-panel'), layout: document.querySelector('.pdp-layout') },
            { el: document.querySelector('.shop-sidebar'), layout: document.querySelector('.shop-layout') }
        ];

        function calculateSticky() {
            // On mobile / tablet screens, disable custom top overrides so items stack naturally
            if (window.innerWidth <= 1024) {
                sidebarConfigs.forEach(cfg => {
                    if (cfg.el) cfg.el.style.top = '';
                });
                return;
            }

            const vh = window.innerHeight;
            const headerEl = document.getElementById('site-header');
            const headerH = headerEl ? headerEl.offsetHeight : 66;
            const topMargin = headerH + 20; // 20px below header
            const bottomMargin = 28;        // 28px breathing room above viewport bottom

            sidebarConfigs.forEach(cfg => {
                if (!cfg.el || !cfg.layout) return;
                const h = cfg.el.offsetHeight;
                if (h <= 0) return;

                // Ensure parent layout allows sticky positioning
                cfg.el.style.position = 'sticky';
                cfg.el.style.alignSelf = 'start';

                // If sidebar height fits within viewport: stick nicely to top offset
                if (h + topMargin + bottomMargin <= vh) {
                    cfg.el.style.top = topMargin + 'px';
                } else {
                    // If sidebar is taller than viewport:
                    // User scrolls naturally through the sidebar data until its bottom is reached ("after finish right side data"),
                    // then it locks into position so the entire sidebar remains visible.
                    // When the long column finishes and next section comes, it naturally scrolls up with the page.
                    cfg.el.style.top = (vh - h - bottomMargin) + 'px';
                }
            });
        }

        window.addEventListener('resize', calculateSticky, { passive: true });
        window.addEventListener('scroll', calculateSticky, { passive: true });

        if (window.ResizeObserver) {
            const ro = new ResizeObserver(() => calculateSticky());
            sidebarConfigs.forEach(cfg => {
                if (cfg.el) ro.observe(cfg.el);
                if (cfg.layout) ro.observe(cfg.layout);
            });
        }

        calculateSticky();
        setTimeout(calculateSticky, 200);
        setTimeout(calculateSticky, 800);
    }

    document.addEventListener("DOMContentLoaded", function () {
        initHeaderScroll();
        initKeyboardShortcuts();
        initSmartStickySidebars();
    });

    // ========================================================
    // STOREFRONT HIGH-TECH CYBERPUNK TOAST NOTIFICATION
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

        toast.style.cssText = `background:#0f1216; border:1px solid ${accentColor}88; border-left:4px solid ${accentColor}; box-shadow:0 12px 40px rgba(0,0,0,0.85); color:#e5e7eb; padding:12px 16px; font-family:'JetBrains Mono', monospace; font-size:12px; line-height:1.45; border-radius:3px; pointer-events:auto; display:flex; align-items:flex-start; gap:10px; opacity:0; transform:translateY(12px); transition:opacity 0.22s ease, transform 0.22s ease;`;
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
                    <button type="button" id="confirm-modal-close-x" class="btn-admin btn-admin-outline" style="padding:0.25rem 0.55rem; border-color:transparent; color:#9ca3af;" onclick="if (window._confirmReject) window._confirmReject()">✕</button>
                </div>
                <div class="confirm-modal-body">
                    <p id="confirm-modal-message" class="confirm-modal-text">Are you sure you want to proceed with this operation?</p>
                    <div id="confirm-modal-input-wrap" style="display:none; margin: 1rem 0;">
                        <input type="text" id="confirm-modal-input" style="width:100%; box-sizing:border-box; background:#07080a; border:1px solid rgba(0,229,255,0.4); color:#fff; padding:0.6rem 0.85rem; font-family:'JetBrains Mono', monospace; font-size:12px; border-radius:4px;" autocomplete="off" spellcheck="false">
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
    // STOREFRONT CONFIRMATION / PROMPT / ALERT MODAL
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

            const box = modal.querySelector('.confirm-modal-box');
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

    /* ==========================================================================
       SHARE ADVISORY POPUP MODAL HANDLERS (MINIMAL BRAND-MATCHED)
       ========================================================================== */
    window.openShareModal = function (title, customUrl) {
        const modal = document.getElementById('modal-share-advisory');
        if (!modal) return;

        const postTitle = (title && typeof title === 'string') ? title.trim() : (document.title || 'Security Advisory');
        const postUrl = (customUrl && typeof customUrl === 'string') ? customUrl.trim() : window.location.href;

        window._currentShareData = { title: postTitle, url: postUrl };

        // Attach social handlers
        const fbBtn = document.getElementById('share-btn-fb');
        if (fbBtn) {
            fbBtn.onclick = function (e) {
                e.preventDefault();
                const shareUrl = 'https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(postUrl);
                window.open(shareUrl, '_blank', 'noopener,noreferrer');
            };
        }

        const xBtn = document.getElementById('share-btn-x');
        if (xBtn) {
            xBtn.onclick = function (e) {
                e.preventDefault();
                const shareUrl = 'https://twitter.com/intent/tweet?url=' + encodeURIComponent(postUrl) + '&text=' + encodeURIComponent(postTitle);
                window.open(shareUrl, '_blank', 'noopener,noreferrer');
            };
        }

        const gmailBtn = document.getElementById('share-btn-gmail');
        if (gmailBtn) {
            gmailBtn.onclick = function (e) {
                e.preventDefault();
                const shareUrl = 'https://mail.google.com/mail/?view=cm&fs=1&su=' + encodeURIComponent(postTitle) + '&body=' + encodeURIComponent(postUrl);
                window.open(shareUrl, '_blank', 'noopener,noreferrer');
            };
        }

        modal.classList.add('is-open');
        modal.style.display = 'flex';
        document.body.classList.add('modal-open');
    };

    window.closeShareModal = function () {
        const modal = document.getElementById('modal-share-advisory');
        if (modal) {
            modal.classList.remove('is-open');
            modal.style.display = 'none';
            document.body.classList.remove('modal-open');
        }
    };

    window.copyShareUrl = function () {
        const url = (window._currentShareData && window._currentShareData.url) || window.location.href;
        
        function onCopiedSuccess() {
            if (typeof window.showToast === 'function') {
                window.showToast('Link copied to clipboard.', 'success');
            }
            const copyBtn = document.getElementById('share-btn-copy');
            const copyLabel = document.getElementById('share-copy-label');

            if (copyBtn) {
                copyBtn.classList.add('copied');
            }
            if (copyLabel) {
                const orig = copyLabel.textContent;
                copyLabel.textContent = 'Copied!';
                setTimeout(function () {
                    copyLabel.textContent = orig;
                    if (copyBtn) copyBtn.classList.remove('copied');
                }, 2000);
            }
        }

        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(url).then(onCopiedSuccess).catch(function () {
                fallbackCopy(url);
            });
        } else {
            fallbackCopy(url);
        }

        function fallbackCopy(text) {
            const ta = document.createElement('textarea');
            ta.value = text;
            ta.style.position = 'fixed';
            ta.style.opacity = '0';
            document.body.appendChild(ta);
            ta.select();
            try {
                document.execCommand('copy');
                onCopiedSuccess();
            } catch (e) {
                if (typeof window.showToast === 'function') {
                    window.showToast('Failed to copy link.', 'error');
                }
            }
            document.body.removeChild(ta);
        }
    };

    // Close on click outside and escape
    document.addEventListener('click', function (e) {
        const modal = document.getElementById('modal-share-advisory');
        if (modal && modal.classList.contains('is-open')) {
            if (e.target === modal) {
                closeShareModal();
            }
        }
    });

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            const modal = document.getElementById('modal-share-advisory');
            if (modal && modal.classList.contains('is-open')) {
                closeShareModal();
            }
        }
    });

    /* ==========================================================================
       AUTOMATIC GEOLOCATION & BROWSER GOOGLE TRANSLATE ENGINE
       ========================================================================== */
    var TIMEZONE_TO_LANG = {
        'Asia/Dhaka': 'bn',
        'Asia/Kolkata': 'hi',
        'Asia/Calcutta': 'hi',
        'Asia/Karachi': 'ur',
        'Asia/Colombo': 'si',
        'Asia/Kathmandu': 'ne',
        'Asia/Tokyo': 'ja',
        'Asia/Seoul': 'ko',
        'Asia/Shanghai': 'zh-CN',
        'Asia/Hong_Kong': 'zh-TW',
        'Asia/Taipei': 'zh-TW',
        'Asia/Singapore': 'zh-CN',
        'Asia/Jakarta': 'id',
        'Asia/Bangkok': 'th',
        'Asia/Ho_Chi_Minh': 'vi',
        'Asia/Manila': 'tl',
        'Asia/Dubai': 'ar',
        'Asia/Riyadh': 'ar',
        'Asia/Baghdad': 'ar',
        'Asia/Beirut': 'ar',
        'Asia/Amman': 'ar',
        'Africa/Cairo': 'ar',
        'Europe/Paris': 'fr',
        'Europe/Berlin': 'de',
        'Europe/Madrid': 'es',
        'Europe/Rome': 'it',
        'Europe/Moscow': 'ru',
        'Europe/Kyiv': 'uk',
        'Europe/Istanbul': 'tr',
        'Europe/Amsterdam': 'nl',
        'Europe/Warsaw': 'pl',
        'Europe/Stockholm': 'sv',
        'Europe/Oslo': 'no',
        'Europe/Helsinki': 'fi',
        'Europe/Copenhagen': 'da',
        'Europe/Lisbon': 'pt',
        'Europe/Athens': 'el',
        'America/Sao_Paulo': 'pt',
        'America/Mexico_City': 'es',
        'America/Bogota': 'es',
        'America/Buenos_Aires': 'es',
        'America/Santiago': 'es',
        'America/Lima': 'es',
        'America/Caracas': 'es'
    };

    var COUNTRY_TO_LANG = {
        'BD': 'bn', 'IN': 'hi', 'PK': 'ur', 'SA': 'ar', 'AE': 'ar', 'EG': 'ar',
        'FR': 'fr', 'DE': 'de', 'ES': 'es', 'IT': 'it', 'RU': 'ru', 'TR': 'tr',
        'JP': 'ja', 'CN': 'zh-CN', 'KR': 'ko', 'BR': 'pt', 'PT': 'pt', 'ID': 'id',
        'TH': 'th', 'VN': 'vi', 'MX': 'es', 'AR': 'es', 'NL': 'nl', 'PL': 'pl',
        'SE': 'sv', 'NO': 'no', 'FI': 'fi', 'DK': 'da', 'GR': 'el', 'UA': 'uk'
    };

    var LANG_NAMES = {
        'bn': 'বাংলা',
        'es': 'Español',
        'fr': 'Français',
        'de': 'Deutsch',
        'ar': 'العربية',
        'ru': 'Русский',
        'zh-CN': '简体中文',
        'zh-TW': '繁體中文',
        'ja': '日本語',
        'ko': '한국어',
        'hi': 'हिन्दी',
        'ur': 'اردو',
        'pt': 'Português',
        'it': 'Italiano',
        'tr': 'Türkçe',
        'id': 'Bahasa Indonesia',
        'vi': 'Tiếng Việt',
        'th': 'ไทย',
        'nl': 'Nederlands',
        'pl': 'Polski',
        'sv': 'Svenska'
    };

    function getCookie(name) {
        var v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
        return v ? decodeURIComponent(v[2]) : null;
    }

    function getCurrentLanguage() {
        var transCookie = getCookie('googtrans');
        if (transCookie) {
            var parts = transCookie.split('/');
            if (parts.length >= 3 && parts[2] && parts[2] !== 'en') {
                return parts[2];
            }
        }
        return 'en';
    }

    function detectUserLanguage() {
        // 1. Saved target language
        var saved = localStorage.getItem('nf_detected_lang');
        if (saved && saved !== 'en') return saved;

        // 2. Browser navigator language (e.g. bn-BD, bn, fr, de, es)
        var navLang = (navigator.language || (navigator.languages && navigator.languages[0]) || '').toLowerCase();
        if (navLang) {
            var code = navLang.split('-')[0];
            if (code !== 'en' && code.length === 2) {
                return code;
            }
        }

        // 3. User geographic timezone
        try {
            var tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
            if (tz && TIMEZONE_TO_LANG[tz]) {
                return TIMEZONE_TO_LANG[tz];
            }
        } catch (e) {}

        // 4. Default target language: Bangla ('bn')
        return 'bn';
    }

    function setGoogleTransCookie(langCode) {
        var hostname = window.location.hostname;
        var past = 'Thu, 01 Jan 1970 00:00:00 UTC;';
        if (!langCode || langCode === 'en') {
            document.cookie = 'googtrans=; expires=' + past + ' path=/;';
            document.cookie = 'googtrans=; expires=' + past + ' path=/; domain=' + hostname + ';';
            if (hostname.indexOf('.') !== -1) {
                document.cookie = 'googtrans=; expires=' + past + ' path=/; domain=.' + hostname + ';';
            }
            localStorage.removeItem('nf_trans_active');
        } else {
            var cookieVal = '/en/' + langCode;
            document.cookie = 'googtrans=' + cookieVal + '; path=/;';
            document.cookie = 'googtrans=' + cookieVal + '; path=/; domain=' + hostname + ';';
            if (hostname.indexOf('.') !== -1) {
                document.cookie = 'googtrans=' + cookieVal + '; path=/; domain=.' + hostname + ';';
            }
            localStorage.setItem('nf_trans_active', langCode);
        }
    }

    function updateLanguageUI() {
        var current = getCurrentLanguage();
        var isTranslated = (current !== 'en');
        var buttons = document.querySelectorAll('.header-lang-btn, .js-lang-btn');
        var labels = document.querySelectorAll('.js-lang-label');

        labels.forEach(function(el) {
            if (isTranslated) {
                el.textContent = 'EN';
            } else {
                var target = detectUserLanguage();
                var code = (target || 'bn').split('-')[0].toUpperCase();
                el.textContent = code;
            }
        });

        buttons.forEach(function(btn) {
            if (isTranslated) {
                btn.classList.add('is-active');
                btn.setAttribute('title', 'Click to restore original English');
            } else {
                btn.classList.remove('is-active');
                btn.setAttribute('title', 'Auto-detect location and translate website');
            }
        });
    }

    function toggleLanguage() {
        var current = getCurrentLanguage();
        if (current !== 'en') {
            // Revert back to English
            setGoogleTransCookie('en');
            if (window.showToast) {
                window.showToast('Restored website to original English.', 'info');
            }
            updateLanguageUI();
            setTimeout(function() {
                window.location.reload();
            }, 300);
        } else {
            // Translate to detected language
            var target = detectUserLanguage();
            localStorage.setItem('nf_detected_lang', target);
            setGoogleTransCookie(target);

            var name = LANG_NAMES[target] || target.toUpperCase();
            if (window.showToast) {
                window.showToast('Location detected: Translating to ' + name + '...', 'info');
            }

            var combo = document.querySelector('.goog-te-combo');
            if (combo) {
                combo.value = target;
                combo.dispatchEvent(new Event('change'));
                updateLanguageUI();
            } else {
                setTimeout(function() {
                    window.location.reload();
                }, 350);
            }
        }
    }

    // Background lightweight geo lookup for edge cases
    if (!localStorage.getItem('nf_detected_lang')) {
        try {
            fetch('https://api.country.is/')
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    if (data && data.country && COUNTRY_TO_LANG[data.country]) {
                        var detected = COUNTRY_TO_LANG[data.country];
                        localStorage.setItem('nf_detected_lang', detected);
                        updateLanguageUI();
                    }
                })
                .catch(function() {});
        } catch(e) {}
    }

    document.addEventListener('DOMContentLoaded', function() {
        updateLanguageUI();
    });

    window.NFLang = {
        toggle: toggleLanguage,
        detect: detectUserLanguage,
        getCurrent: getCurrentLanguage,
        updateUI: updateLanguageUI
    };

    window.NFUI = {
        openMobileMenu: openMobileMenu,
        closeMobileMenu: closeMobileMenu,
        openSearch: openSearch,
        closeSearch: closeSearch,
        filterSearchTag: filterSearchTag
    };
})();
