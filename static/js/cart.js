/**
 * NORTH//FORM — Persistent Cart Drawer Engine (Vanilla JS + localStorage)
 */

(function () {
    "use strict";

    const STORAGE_KEY = "northform_cart_v1";

    function getCart() {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            return raw ? JSON.parse(raw) : [];
        } catch (e) {
            return [];
        }
    }

    function saveCart(cart) {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(cart));
        } catch (e) {}
        renderCart();
    }

    function findProduct(productId) {
        const list = window.NORTHFORM_PRODUCTS || [];
        return list.find(function (p) { 
            return p.id === productId || p.id === parseInt(productId, 10) || p.sku === productId || p.code === productId || p.slug === productId; 
        }) || list[0];
    }

    function escapeHtml(str) {
        return String(str == null ? "" : str)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    function addToCart(productId, licenseTier, versionLabel, qty) {
        const product = findProduct(productId);
        if (!product) return;

        const chosenLicense = licenseTier || product.license_duration || "Enterprise License";
        const chosenVersion = versionLabel || product.version || "Latest Build";
        const addQty = Math.max(1, parseInt(qty || 1, 10));

        const cart = getCart();
        const key = String(product.id);

        const existing = cart.find(function (item) {
            return String(item.id) === String(product.id) || item.key === key;
        });
        if (existing) {
            existing.qty += addQty;
            existing.slug = product.slug || existing.slug;
            existing.sku = product.sku || product.code || existing.sku;
            existing.version = chosenVersion;
            existing.license_duration = chosenLicense;
        } else {
            cart.push({
                key: key,
                id: product.id,
                slug: product.slug || product.sku || String(product.id),
                code: product.sku || product.code || ("SYS-" + product.id),
                sku: product.sku || product.code || ("SYS-" + product.id),
                name: product.name,
                price: Number(product.price) || 0,
                version: chosenVersion,
                license_duration: chosenLicense,
                image: product.image || product.image_url || "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=1200&q=85",
                qty: addQty
            });
        }

        saveCart(cart);
        openCart();
    }

    function quickAdd(productId, size, btnEl) {
        const product = findProduct(productId);
        if (!product) return;

        let targetBtn = btnEl;
        if (!targetBtn && typeof window !== "undefined" && window.event && window.event.currentTarget) {
            targetBtn = window.event.currentTarget;
        }

        addToCart(product.id, size || product.license_duration, product.version, 1);

        if (targetBtn && targetBtn.tagName === "BUTTON") {
            const labelEl = targetBtn.querySelector(".qa-label") || targetBtn;
            if (!targetBtn.dataset.origLabel) {
                targetBtn.dataset.origLabel = labelEl.textContent;
            }
            labelEl.textContent = "✓ ADDED TO CART";
            setTimeout(function () {
                if (targetBtn.dataset.origLabel) {
                    labelEl.textContent = targetBtn.dataset.origLabel;
                }
            }, 1300);
        }
    }

    function updateQuantity(itemKey, delta) {
        let cart = getCart();
        const target = cart.find(function (item) { return item.key === itemKey; });
        if (!target) return;

        target.qty += delta;
        if (target.qty <= 0) {
            cart = cart.filter(function (item) { return item.key !== itemKey; });
        }
        saveCart(cart);
    }

    function removeFromCart(itemKey) {
        const cart = getCart().filter(function (item) { return item.key !== itemKey; });
        saveCart(cart);
    }

    function calculateTotal(cart) {
        return cart.reduce(function (sum, item) {
            return sum + item.price * item.qty;
        }, 0);
    }

    function openCart() {
        const drawer = document.getElementById("cart-drawer");
        const backdrop = document.getElementById("cart-backdrop");
        if (drawer && backdrop) {
            drawer.classList.add("is-open");
            backdrop.classList.add("is-open");
            document.body.classList.add("no-scroll");
        }
    }

    function closeCart() {
        const drawer = document.getElementById("cart-drawer");
        const backdrop = document.getElementById("cart-backdrop");
        if (drawer && backdrop) {
            drawer.classList.remove("is-open");
            backdrop.classList.remove("is-open");
            document.body.classList.remove("no-scroll");
        }
    }

    async function handleCheckout() {
        const cart = getCart();
        if (!cart.length) {
            if (window.showToast) window.showToast("Your bag is empty.", "error");
            return;
        }
        const msgEl = document.getElementById("cart-checkout-feedback");
        const tgInput = document.getElementById("cart-buyer-telegram");
        const buyerTg = tgInput ? tgInput.value.trim() : "";

        if (!buyerTg) {
            if (tgInput) {
                tgInput.style.borderColor = "#dc2626";
                tgInput.focus();
                tgInput.addEventListener("input", function () {
                    tgInput.style.borderColor = "var(--border)";
                }, { once: true });
            }
            if (msgEl) {
                msgEl.style.display = "block";
                msgEl.style.color = "#dc2626";
                msgEl.textContent = "PLEASE ENTER YOUR TELEGRAM @USERNAME FOR LICENSE DELIVERY.";
            }
            if (window.showToast) window.showToast("Please enter your Telegram @username to proceed.", "error");
            return;
        }

        if (msgEl) {
            msgEl.style.display = "block";
            msgEl.style.color = "var(--text)";
            msgEl.textContent = "CREATING YOUR ORDER...";
        }

        try {
            const resp = await fetch("/api/checkout", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    buyer_telegram: buyerTg,
                    buyer_note: "Direct website checkout",
                    items: cart.map(function(item) {
                        return {
                            sku: item.sku || item.code || ("SYS-" + item.id),
                            qty: item.qty,
                            price: item.price,
                            name: item.name
                        };
                    })
                })
            });
            const data = await resp.json();
            if (data.success || data.ok) {
                if (msgEl) {
                    msgEl.style.color = "var(--text)";
                    msgEl.innerHTML = `ORDER <strong>#${escapeHtml(data.order_number)}</strong> CREATED.<br><span style="font-size:0.75rem; color:#10b981;">OPENING TELEGRAM TO COMPLETE YOUR ORDER...</span>`;
                }
                saveCart([]);
                setTimeout(function() {
                    if (data.telegram_url) {
                        window.open(data.telegram_url, "_blank");
                    }
                    setTimeout(function() {
                        closeCart();
                    }, 1200);
                }, 1000);
            } else {
                if (msgEl) {
                    msgEl.style.color = "#dc2626";
                    msgEl.textContent = data.error || "Order dispatch error.";
                }
            }
        } catch (err) {
            if (msgEl) {
                msgEl.style.color = "#dc2626";
                msgEl.textContent = "Network error while dispatching order.";
            }
        }
    }

    function renderCart() {
        const cart = getCart();
        const totalCount = cart.reduce(function (sum, item) { return sum + item.qty; }, 0);
        const subtotal = calculateTotal(cart);

        document.querySelectorAll(".js-cart-count").forEach(function (el) {
            el.textContent = totalCount;
        });

        const container = document.getElementById("cart-drawer-items");
        const subtotalEl = document.getElementById("cart-subtotal-amount");
        const shippingNoteEl = document.getElementById("cart-shipping-note");

        if (subtotalEl) {
            subtotalEl.textContent = "$" + subtotal.toLocaleString();
        }

        if (shippingNoteEl) {
            shippingNoteEl.textContent = "INSTANT LICENSE & DOWNLOAD PROVISIONING VIA TELEGRAM & VAULT";
        }

        if (!container) return;

        if (cart.length === 0) {
            container.innerHTML = `
                <div style="padding: 4rem 0; text-align: center; color: var(--muted);">
                    <p class="meta-label" style="margin-bottom: 0.75rem;">YOUR LICENSE CART IS EMPTY</p>
                    <p style="font-size: 0.85rem; margin-bottom: 1.75rem;">Browse verified penetration testing suites, reverse engineering tools &amp; SIEM licenses.</p>
                    <a href="/shop" class="btn btn-outline-dark" onclick="window.NFCart.close()">BROWSE SECURITY TOOLS →</a>
                </div>
            `;
            return;
        }

        container.innerHTML = cart.map(function (item) {
            const matchedProduct = findProduct(item.id);
            const productSlug = item.slug || (matchedProduct && matchedProduct.slug) || item.sku || item.code || item.id;
            const productUrl = "/product/" + encodeURIComponent(productSlug);
            const skuLabel = item.sku || item.code || (matchedProduct && matchedProduct.sku) || ("SYS-" + item.id);
            const tierLabel = item.license_duration || (matchedProduct && matchedProduct.license_duration) || item.version || (matchedProduct && matchedProduct.version) || "Enterprise License";
            const safeKey = escapeHtml(item.key);
            return `
            <div class="cart-item">
                <a href="${productUrl}" onclick="window.NFCart.close()">
                    <img src="${escapeHtml(item.image)}" alt="${escapeHtml(item.name)}" class="cart-item-img">
                </a>
                <div style="display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <div style="display: flex; justify-content: space-between; gap: 0.5rem; align-items: baseline;">
                            <a href="${productUrl}" onclick="window.NFCart.close()" style="font-size: 0.8rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase;">${escapeHtml(item.name)}</a>
                            <span class="meta-mono">$${(Number(item.price) * Number(item.qty)).toLocaleString()}</span>
                        </div>
                        <p class="meta-mono" style="font-size: 0.68rem; color: var(--muted); margin-top: 0.25rem; text-transform: uppercase; letter-spacing: 0.06em;">
                            SKU: ${escapeHtml(skuLabel)} &nbsp;·&nbsp; ${escapeHtml(tierLabel)}
                        </p>
                    </div>
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 0.75rem;">
                        <div class="qty-control">
                            <button type="button" class="qty-btn" onclick="window.NFCart.updateQuantity('${safeKey}', -1)" aria-label="Decrease quantity">−</button>
                            <span class="qty-value">${Number(item.qty)}</span>
                            <button type="button" class="qty-btn" onclick="window.NFCart.updateQuantity('${safeKey}', 1)" aria-label="Increase quantity">+</button>
                        </div>
                        <button type="button" onclick="window.NFCart.removeFromCart('${safeKey}')"
                                style="font-size: 0.68rem; letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted); text-decoration: underline;">
                            REMOVE
                        </button>
                    </div>
                </div>
            </div>
            `;
        }).join("");
    }

    document.addEventListener("DOMContentLoaded", function () {
        renderCart();
    });

    window.NFCart = {
        addToCart: addToCart,
        quickAdd: quickAdd,
        updateQuantity: updateQuantity,
        removeFromCart: removeFromCart,
        renderCart: renderCart,
        open: openCart,
        close: closeCart,
        checkout: handleCheckout
    };
})();
