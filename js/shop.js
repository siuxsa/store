/**
 * NORTH//FORM — Shop Page Dynamic Filtering, Sorting & URL Query Sync
 */

(function () {
    "use strict";

    const state = {
        category: "ALL",
        gender: "ALL",
        size: "ALL",
        color: "ALL",
        priceRange: "ALL",
        sort: "FEATURED"
    };

    function parseUrlParams() {
        const params = new URLSearchParams(window.location.search);
        const cat = params.get("category");
        const gen = params.get("gender");
        if (cat) state.category = cat;
        if (gen) state.gender = gen;
    }

    function filterAndSortProducts() {
        let list = (window.NORTHFORM_PRODUCTS || []).slice();

        if (state.category !== "ALL") {
            list = list.filter(function (p) {
                return p.category.toLowerCase() === state.category.toLowerCase();
            });
        }

        if (state.gender !== "ALL") {
            list = list.filter(function (p) {
                return p.gender.toLowerCase() === state.gender.toLowerCase();
            });
        }

        if (state.size !== "ALL") {
            list = list.filter(function (p) {
                return p.sizes && p.sizes.includes(state.size);
            });
        }

        if (state.color !== "ALL") {
            list = list.filter(function (p) {
                return (
                    p.color.toLowerCase().includes(state.color.toLowerCase()) ||
                    (p.colors && p.colors.some(function (c) { return c.toLowerCase().includes(state.color.toLowerCase()); }))
                );
            });
        }

        if (state.priceRange === "UNDER_300") {
            list = list.filter(function (p) { return p.price < 300; });
        } else if (state.priceRange === "300_400") {
            list = list.filter(function (p) { return p.price >= 300 && p.price <= 400; });
        } else if (state.priceRange === "OVER_400") {
            list = list.filter(function (p) { return p.price > 400; });
        }

        if (state.sort === "NEWEST") {
            list.sort(function (a, b) { return (b.isNew ? 1 : 0) - (a.isNew ? 1 : 0); });
        } else if (state.sort === "PRICE_ASC") {
            list.sort(function (a, b) { return a.price - b.price; });
        } else if (state.sort === "PRICE_DESC") {
            list.sort(function (a, b) { return b.price - a.price; });
        }

        return list;
    }

    function updateFilterButtonsUI() {
        document.querySelectorAll("[data-filter-type]").forEach(function (btn) {
            const type = btn.getAttribute("data-filter-type");
            const val = btn.getAttribute("data-filter-value");
            if (state[type] && state[type].toLowerCase() === val.toLowerCase()) {
                btn.classList.add("active");
            } else {
                btn.classList.remove("active");
            }
        });

        const headingEl = document.getElementById("shop-page-heading");
        if (headingEl) {
            if (state.category !== "ALL") {
                headingEl.textContent = state.category.toUpperCase();
            } else if (state.gender !== "ALL") {
                headingEl.textContent = "SHOP " + state.gender.toUpperCase();
            } else {
                headingEl.textContent = "SHOP ALL SYSTEMS";
            }
        }
    }

    function renderShopCatalog() {
        const gridEl = document.getElementById("shop-products-grid");
        const countEl = document.getElementById("shop-results-count");
        if (!gridEl) return;

        updateFilterButtonsUI();
        const filtered = filterAndSortProducts();

        if (countEl) {
            countEl.textContent = filtered.length + " TECHNICAL SYSTEM(S)";
        }

        if (filtered.length === 0) {
            gridEl.innerHTML = `
                <div style="grid-column: 1 / -1; padding: 4.5rem 2rem; text-align: center; border: 1px solid var(--border);">
                    <p class="meta-label" style="margin-bottom: 0.75rem;">NO SYSTEMS MATCH CURRENT FILTER CRITERIA</p>
                    <button type="button" class="btn btn-outline-dark" onclick="window.NFShop.resetFilters()">RESET ALL FILTERS</button>
                </div>
            `;
            return;
        }

        gridEl.innerHTML = filtered.map(function (p) {
            return window.createProductCardHTML(p);
        }).join("");
    }

    function setFilter(type, value) {
        if (state[type] === value && value !== "ALL") {
            state[type] = "ALL";
        } else {
            state[type] = value;
        }
        renderShopCatalog();
    }

    function setSort(sortValue) {
        state.sort = sortValue;
        renderShopCatalog();
    }

    function resetFilters() {
        state.category = "ALL";
        state.gender = "ALL";
        state.size = "ALL";
        state.color = "ALL";
        state.priceRange = "ALL";
        state.sort = "FEATURED";
        const sortSelect = document.getElementById("shop-sort-select");
        if (sortSelect) sortSelect.value = "FEATURED";
        renderShopCatalog();
    }

    function toggleMobileSidebar() {
        const sb = document.getElementById("shop-sidebar");
        if (sb) sb.classList.toggle("is-open");
    }

    document.addEventListener("DOMContentLoaded", function () {
        if (!document.getElementById("shop-products-grid")) return;
        parseUrlParams();
        renderShopCatalog();
    });

    window.NFShop = {
        setFilter: setFilter,
        setSort: setSort,
        resetFilters: resetFilters,
        toggleMobileSidebar: toggleMobileSidebar
    };
})();
