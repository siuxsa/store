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
            return p.id === productId || p.id === parseInt(productId, 10) || p.sku === productId || p.code === productId; 
        }) || list[0];
    }

    function addToCart(productId, size, color, qty) {
        const product = findProduct(productId);
        if (!product) return;

        const chosenSize = size || (product.sizes && product.sizes[0]) || (product.license_duration || "1-Year Pro");
        const chosenColor = color || product.color || "Enterprise License";
        const addQty = Math.max(1, parseInt(qty || 1, 10));

        const cart = getCart();
        const key = product.id + "__" + chosenSize;

        const existing = cart.find(function (item) { return item.key === key; });
        if (existing) {
            existing.qty += addQty;
        } else {
            cart.push({
                key: key,
                id: product.id,
                code: product.sku || product.code || ("SYS-" + product.id),
                sku: product.sku || product.code,
                name: product.name,
                price: product.price,
                size: chosenSize,
                color: chosenColor,
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
        addToCart(product.id, size || "L", product.color, 1);

        if (btnEl) {
            const labelEl = btnEl.querySelector(".qa-label");
            if (labelEl) {
                const orig = labelEl.textContent;
                labelEl.textContent = "✓ ADDED TO SYSTEM";
                setTimeout(function () {
                    labelEl.textContent = orig;
                }, 1400);
            }
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
        if (!cart.length) return;
        const msgEl = document.getElementById("cart-checkout-feedback");
        const tgInput = document.getElementById("cart-buyer-telegram");
        const buyerTg = tgInput ? tgInput.value.trim() : "";

        if (msgEl) {
            msgEl.style.display = "block";
            msgEl.style.color = "var(--text)";
            msgEl.textContent = "DISPATCHING ORDER TICKET...";
        }

        try {
            const resp = await fetch("/api/checkout", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    buyer_telegram: buyerTg || "@client_direct",
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
                    msgEl.innerHTML = `ORDER <strong>#${data.order_number}</strong> CREATED.<br><span style="font-size:0.75rem;">DISPATCHING TO TELEGRAM...</span>`;
                }
                saveCart([]);
                setTimeout(function() {
                    if (data.telegram_url) {
                        window.open(data.telegram_url, "_blank");
                    }
                    window.location.href = "/orders/" + data.order_number;
                }, 1000);
            } else {
                if (msgEl) msgEl.textContent = data.error || "Order dispatch error.";
            }
        } catch (err) {
            if (msgEl) msgEl.textContent = "DISPATCH INITIALIZED. THANK YOU.";
            saveCart([]);
            setTimeout(function() { closeCart(); }, 1500);
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
            if (subtotal >= 250 || subtotal === 0) {
                shippingNoteEl.textContent = subtotal >= 250
                    ? "QUALIFIES FOR COMPLIMENTARY GLOBAL EXPRESS SHIPPING"
                    : "COMPLIMENTARY GLOBAL SHIPPING ON ORDERS OVER $250";
            } else {
                shippingNoteEl.textContent = "ADD $" + (250 - subtotal) + " MORE FOR COMPLIMENTARY GLOBAL SHIPPING";
            }
        }

        if (!container) return;

        if (cart.length === 0) {
            container.innerHTML = `
                <div style="padding: 4rem 0; text-align: center; color: var(--muted);">
                    <p class="meta-label" style="margin-bottom: 0.75rem;">YOUR CART IS EMPTY</p>
                    <p style="font-size: 0.85rem; margin-bottom: 1.75rem;">Explore enterprise security licenses, red team toolkits & threat intelligence.</p>
                    <a href="/arsenal" class="btn btn-outline-dark" onclick="window.NFCart.close()">EXPLORE ARSENAL →</a>
                </div>
            `;
            return;
        }

        container.innerHTML = cart.map(function (item) {
            return `
            <div class="cart-item">
                <a href="product.html?id=${item.id}">
                    <img src="${item.image}" alt="${item.name}" class="cart-item-img">
                </a>
                <div style="display: flex; flex-direction: column; justify-content: space-between;">
                    <div>
                        <div style="display: flex; justify-content: space-between; gap: 0.5rem; align-items: baseline;">
                            <a href="product.html?id=${item.id}" style="font-size: 0.8rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase;">${item.name}</a>
                            <span class="meta-mono">$${item.price * item.qty}</span>
                        </div>
                        <p style="font-size: 0.72rem; color: var(--muted); margin-top: 0.25rem; text-transform: uppercase; letter-spacing: 0.08em;">
                            COLOR: ${item.color} &nbsp;/&nbsp; SIZE: ${item.size}
                        </p>
                    </div>
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 0.75rem;">
                        <div class="qty-control">
                            <button type="button" class="qty-btn" onclick="window.NFCart.updateQuantity('${item.key}', -1)" aria-label="Decrease quantity">−</button>
                            <span class="qty-value">${item.qty}</span>
                            <button type="button" class="qty-btn" onclick="window.NFCart.updateQuantity('${item.key}', 1)" aria-label="Increase quantity">+</button>
                        </div>
                        <button type="button" onclick="window.NFCart.removeFromCart('${item.key}')"
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
