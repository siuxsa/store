/**
 * NORTH//FORM — Global Navigation, Scroll Header, Search Overlay, Mobile Menu & Image Reveal
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
            } else {
                header.classList.remove("is-scrolled");
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
                return (
                    p.name.toLowerCase().includes(q) ||
                    p.category.toLowerCase().includes(q) ||
                    p.subtitle.toLowerCase().includes(q) ||
                    p.description.toLowerCase().includes(q) ||
                    p.color.toLowerCase().includes(q)
                );
            })
            : allProducts.slice(0, 4);

        if (countEl) {
            countEl.textContent = q
                ? matched.length + " SYSTEM(S) MATCHING \"" + query.toUpperCase() + "\""
                : "FEATURED SS26 SYSTEMS";
        }

        if (matched.length === 0) {
            resultsEl.innerHTML = `
                <div style="grid-column: 1 / -1; padding: 3rem 0; color: var(--muted);">
                    <p class="meta-label">NO SYSTEMS FOUND FOR "${query.toUpperCase()}"</p>
                    <p style="font-size: 0.85rem; margin-top: 0.5rem;">Try searching for "Shell", "Parka", "Trouser", "Insulation", or "Dyneema".</p>
                </div>
            `;
            return;
        }

        resultsEl.innerHTML = matched.slice(0, 8).map(function (p) {
            return window.createProductCardHTML(p);
        }).join("");
    }

    // 4. IntersectionObserver for Image & Section Reveal
    function initScrollReveal() {
        const elements = document.querySelectorAll(".reveal-img, .reveal-block");
        if (!elements.length) return;

        if (!("IntersectionObserver" in window)) {
            elements.forEach(function (el) { el.classList.add("is-visible"); });
            return;
        }

        const observer = new IntersectionObserver(function (entries, obs) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    obs.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });

        elements.forEach(function (el) {
            observer.observe(el);
        });
    }

    // 5. Homepage Dynamic Sections Population (if on index.html)
    function initHomepageGrids() {
        const homeGrid = document.getElementById("home-new-systems-grid");
        if (homeGrid && window.NORTHFORM_PRODUCTS) {
            const topEight = window.NORTHFORM_PRODUCTS.slice(0, 8);
            homeGrid.innerHTML = topEight.map(function (p) {
                return window.createProductCardHTML(p);
            }).join("");
        }

        const homeJournalGrid = document.getElementById("home-journal-grid");
        if (homeJournalGrid && window.NORTHFORM_JOURNAL) {
            const topThree = window.NORTHFORM_JOURNAL.slice(0, 3);
            homeJournalGrid.innerHTML = topThree.map(function (article) {
                return `
                <article class="journal-card">
                    <a href="journal.html#${article.id}" class="journal-card-media">
                        <img src="${article.image}" alt="${article.title}" loading="lazy">
                    </a>
                    <div class="journal-card-body">
                        <div style="display: flex; justify-content: space-between;" class="meta-label">
                            <span>${article.category}</span>
                            <span>${article.date}</span>
                        </div>
                        <h3 style="font-size: 1.15rem; font-weight: 600; letter-spacing: -0.01em; text-transform: uppercase;">
                            <a href="journal.html#${article.id}">${article.title}</a>
                        </h3>
                        <p style="font-size: 0.85rem; color: var(--muted); line-height: 1.6;">${article.excerpt}</p>
                        <div style="padding-top: 0.5rem;">
                            <a href="journal.html#${article.id}" class="meta-label link-arrow" style="color: var(--text); font-weight: 600;">
                                READ FIELD NOTE <span class="arrow-icon">→</span>
                            </a>
                        </div>
                    </div>
                </article>
                `;
            }).join("");
        }
    }

    // 6. Newsletter Form Handler
    function initNewsletterForm() {
        const forms = document.querySelectorAll(".js-newsletter-form");
        forms.forEach(function (form) {
            form.addEventListener("submit", function (ev) {
                ev.preventDefault();
                const feedback = form.parentElement.querySelector(".js-newsletter-feedback");
                const input = form.querySelector("input[type='email']");
                if (input) input.value = "";
                if (feedback) {
                    feedback.style.display = "block";
                    feedback.textContent = "THANK YOU FOR SUBSCRIBING.";
                }
            });
        });
    }

    // 7. Global Keyboard Accessibility (ESC closes Search, Cart, Mobile Menu, Lightbox)
    function initKeyboardShortcuts() {
        document.addEventListener("keydown", function (ev) {
            if (ev.key === "Escape") {
                closeSearch();
                closeMobileMenu();
                if (window.NFCart) window.NFCart.close();
                const lightbox = document.getElementById("pdp-lightbox");
                if (lightbox) lightbox.classList.remove("is-open");
            }
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        initHeaderScroll();
        initHomepageGrids();
        initScrollReveal();
        initNewsletterForm();
        initKeyboardShortcuts();

        const searchInput = document.getElementById("search-overlay-input");
        if (searchInput) {
            searchInput.addEventListener("input", function (e) {
                renderSearchResults(e.target.value);
            });
        }
    });

    window.NFUI = {
        openMobileMenu: openMobileMenu,
        closeMobileMenu: closeMobileMenu,
        openSearch: openSearch,
        closeSearch: closeSearch,
        filterSearchTag: function (term) {
            const input = document.getElementById("search-overlay-input");
            if (input) {
                input.value = term;
                renderSearchResults(term);
            }
        }
    };
})();
