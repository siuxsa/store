/**
 * NORTH//FORM — Product Detail Page Controller (Gallery, Lightbox, Size/Color, Accordions)
 */

(function () {
    "use strict";

    let currentProduct = null;
    let currentImageIdx = 0;
    let selectedSize = "L";
    let selectedColor = "";

    function loadProductFromUrl() {
        const params = new URLSearchParams(window.location.search);
        const pid = params.get("id") || "storm-shell-jacket";
        const all = window.NORTHFORM_PRODUCTS || [];
        currentProduct = all.find(function (p) { return p.id === pid; }) || all[0];
        if (!currentProduct) return;

        selectedSize = (currentProduct.sizes && currentProduct.sizes.includes("L"))
            ? "L"
            : (currentProduct.sizes[0] || "M");
        selectedColor = currentProduct.color;
        currentImageIdx = 0;

        document.title = currentProduct.name.toUpperCase() + " — NORTH//FORM";

        const setTxt = function (id, val) {
            const el = document.getElementById(id);
            if (el) el.textContent = val;
        };

        setTxt("pdp-breadcrumb-cat", currentProduct.category);
        setTxt("pdp-breadcrumb-name", currentProduct.name);
        setTxt("pdp-code", "SYSTEM " + currentProduct.code + " // " + currentProduct.category.toUpperCase());
        setTxt("pdp-title", currentProduct.name);
        setTxt("pdp-price", "$" + currentProduct.price);
        setTxt("pdp-description", currentProduct.description);
        setTxt("pdp-selected-color-label", selectedColor);
        setTxt("pdp-acc-details", currentProduct.details);
        setTxt("pdp-acc-materials", currentProduct.materials);
        setTxt("pdp-acc-tech", currentProduct.technology);

        const featuresList = document.getElementById("pdp-features-list");
        if (featuresList && currentProduct.features) {
            featuresList.innerHTML = currentProduct.features.map(function (f) {
                return `<li style="padding: 0.35rem 0; border-bottom: 1px solid var(--border); font-size: 0.84rem;">— ${f}</li>`;
            }).join("");
        }

        renderGallery();
        renderColorSwatches();
        renderSizePills();
        renderRelatedProducts();
    }

    function renderGallery() {
        if (!currentProduct) return;
        const imgs = currentProduct.images && currentProduct.images.length
            ? currentProduct.images
            : [currentProduct.image, currentProduct.image2 || currentProduct.image];

        const mainImg = document.getElementById("pdp-main-image");
        if (mainImg) {
            mainImg.src = imgs[currentImageIdx];
            mainImg.alt = currentProduct.name + " view " + (currentImageIdx + 1);
        }

        const thumbsContainer = document.getElementById("pdp-thumbnails");
        if (thumbsContainer) {
            thumbsContainer.innerHTML = imgs.map(function (url, idx) {
                const activeClass = idx === currentImageIdx ? "active" : "";
                return `
                <button type="button" class="pdp-thumb ${activeClass}" onclick="window.NFPDP.selectImage(${idx})" aria-label="View image ${idx + 1}">
                    <img src="${url}" alt="${currentProduct.name} thumbnail ${idx + 1}">
                </button>
                `;
            }).join("");
        }
    }

    function selectImage(idx) {
        if (!currentProduct) return;
        const imgs = currentProduct.images || [currentProduct.image];
        currentImageIdx = (idx + imgs.length) % imgs.length;
        renderGallery();
    }

    function stepImage(delta) {
        selectImage(currentImageIdx + delta);
    }

    function openLightbox() {
        const modal = document.getElementById("pdp-lightbox");
        const lbImg = document.getElementById("pdp-lightbox-img");
        if (!modal || !lbImg || !currentProduct) return;
        const imgs = currentProduct.images || [currentProduct.image];
        lbImg.src = imgs[currentImageIdx];
        modal.classList.add("is-open");
    }

    function closeLightbox() {
        const modal = document.getElementById("pdp-lightbox");
        if (modal) modal.classList.remove("is-open");
    }

    function renderColorSwatches() {
        const wrap = document.getElementById("pdp-color-swatches");
        if (!wrap || !currentProduct) return;
        const colors = currentProduct.colors || [currentProduct.color];
        wrap.innerHTML = colors.map(function (c) {
            const active = c === selectedColor ? "active" : "";
            return `<button type="button" class="color-swatch-btn ${active}" onclick="window.NFPDP.selectColor('${c}')">${c}</button>`;
        }).join("");
    }

    function selectColor(colorName) {
        selectedColor = colorName;
        const lbl = document.getElementById("pdp-selected-color-label");
        if (lbl) lbl.textContent = selectedColor;
        renderColorSwatches();
    }

    function renderSizePills() {
        const wrap = document.getElementById("pdp-size-pills");
        if (!wrap || !currentProduct) return;
        const sizes = currentProduct.sizes || ["XS", "S", "M", "L", "XL"];
        wrap.innerHTML = sizes.map(function (s) {
            const active = s === selectedSize ? "active" : "";
            return `<button type="button" class="size-pill ${active}" onclick="window.NFPDP.selectSize('${s}')">${s}</button>`;
        }).join("");
    }

    function selectSize(sz) {
        selectedSize = sz;
        renderSizePills();
    }

    function addCurrentToCart(buyNow) {
        if (!currentProduct || !window.NFCart) return;
        window.NFCart.addToCart(currentProduct.id, selectedSize, selectedColor, 1);

        const addBtn = document.getElementById("pdp-add-btn");
        if (addBtn && !buyNow) {
            const orig = addBtn.innerHTML;
            addBtn.innerHTML = "✓ ADDED TO CART";
            setTimeout(function () { addBtn.innerHTML = orig; }, 1400);
        }
    }

    function toggleAccordion(btnEl) {
        const item = btnEl.closest(".accordion-item");
        if (!item) return;
        const content = item.querySelector(".accordion-content");
        const icon = btnEl.querySelector(".acc-icon");
        const isOpen = content.style.maxHeight && content.style.maxHeight !== "0px";

        if (isOpen) {
            content.style.maxHeight = "0px";
            if (icon) icon.textContent = "+";
        } else {
            content.style.maxHeight = content.scrollHeight + "px";
            if (icon) icon.textContent = "−";
        }
    }

    function renderRelatedProducts() {
        const grid = document.getElementById("pdp-related-grid");
        if (!grid || !currentProduct) return;
        const all = window.NORTHFORM_PRODUCTS || [];
        const related = all.filter(function (p) { return p.id !== currentProduct.id; }).slice(0, 4);
        grid.innerHTML = related.map(function (p) {
            return window.createProductCardHTML(p);
        }).join("");
    }

    document.addEventListener("DOMContentLoaded", function () {
        if (!document.getElementById("pdp-main-image")) return;
        loadProductFromUrl();

        // Open first accordion by default
        const firstAcc = document.querySelector(".accordion-trigger");
        if (firstAcc) toggleAccordion(firstAcc);
    });

    window.NFPDP = {
        selectImage: selectImage,
        stepImage: stepImage,
        openLightbox: openLightbox,
        closeLightbox: closeLightbox,
        selectColor: selectColor,
        selectSize: selectSize,
        addToCart: addCurrentToCart,
        toggleAccordion: toggleAccordion
    };
})();
