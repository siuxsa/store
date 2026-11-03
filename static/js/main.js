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
                return name.includes(q) || sku.includes(q) || cat.includes(q) || version.includes(q);
            })
            : allProducts.slice(0, 4);

        if (countEl) {
            countEl.textContent = q
                ? matched.length + " SYSTEM(S) MATCHING \"" + query.toUpperCase() + "\""
                : "FEATURED SECURITY ARSENAL";
        }

        if (matched.length === 0) {
            resultsEl.innerHTML = `
                <div style="grid-column: 1 / -1; padding: 3rem 0; color: var(--muted); text-align: center;">
                    <p class="meta-label">NO SYSTEMS FOUND FOR "${query.toUpperCase()}"</p>
                    <p style="font-size: 0.85rem; margin-top: 0.5rem;">Try searching for "Burp", "Metasploit", "Splunk", "IDA", or "CVE".</p>
                </div>
            `;
            return;
        }

        resultsEl.innerHTML = matched.slice(0, 8).map(function (p) {
            const img = p.image || p.image_url || "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=1200&q=85";
            const desc = p.short_desc || (p.specs && p.specs.length ? p.specs.join(" · ") : "Commercial security license package.");
            const specs = (p.version || "v2026.1") + " · " + (p.platform || "Windows / Linux / macOS");
            return `
            <div class="product-card">
                <a href="/arsenal/${p.slug || p.id}" class="product-card-image-wrap">
                    <img src="${img}" alt="${p.name}" class="product-card-img" loading="lazy">
                    <span class="product-badge">${p.badge_text || 'VERIFIED'}</span>
                </a>
                <div class="product-meta">
                    <div class="product-meta-header">
                        <span class="meta-label">${p.category}</span>
                        <span class="meta-mono">$${p.price}</span>
                    </div>
                    <h3 class="product-title">
                        <a href="/arsenal/${p.slug || p.id}">${p.name}</a>
                    </h3>
                    <p class="product-desc">${desc}</p>
                    <div class="product-specs-line">${specs}</div>
                    <div class="product-actions">
                        <button type="button" class="btn btn-outline-dark" style="flex:1; padding:0.45rem 0.5rem; font-size:0.68rem;" onclick="window.NFCart && window.NFCart.quickAdd(${p.id})">+ ADD</button>
                        <a href="/arsenal/${p.slug || p.id}" class="btn btn-dark" style="padding:0.45rem 0.75rem; font-size:0.68rem;">VIEW →</a>
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

    document.addEventListener("DOMContentLoaded", function () {
        initHeaderScroll();
        initKeyboardShortcuts();
    });

    window.NFUI = {
        openMobileMenu: openMobileMenu,
        closeMobileMenu: closeMobileMenu,
        openSearch: openSearch,
        closeSearch: closeSearch,
        filterSearchTag: filterSearchTag
    };
})();
