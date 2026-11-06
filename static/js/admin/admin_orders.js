        window._activeFulfillOrderObj = null;

        function getOrderDataById(id) {
            const el = document.getElementById('order-data-' + id);
            if (!el) return null;
            try {
                return JSON.parse(el.textContent);
            } catch (e) {
                console.error('Failed to parse order JSON for ID', id, e);
                return null;
            }
        }

        function updateFulfillLinksLabels() {
            const rows = document.querySelectorAll('#fulfill-links-container .fulfill-link-row');
            rows.forEach((row, idx) => {
                const badge = row.querySelector('.fulfill-dl-index');
                if (badge) badge.textContent = `LINK #${idx + 1}`;
            });
        }

        function addFulfillLinkRow(label = '', url = '') {
            const container = document.getElementById('fulfill-links-container');
            if (!container) return;
            const row = document.createElement('div');
            row.className = 'fulfill-link-row';
            row.style.cssText = 'display:grid; grid-template-columns: 58px 175px 1fr auto; gap:0.45rem; align-items:center; background:#141618; border:1px solid var(--admin-border); padding:0.45rem 0.6rem; border-radius:4px;';
            row.innerHTML = `
                <span class="fulfill-dl-index" style="font-family:var(--admin-font-mono); font-size:10px; font-weight:700; color:#10b981;">LINK #1</span>
                <input type="text" class="form-input fulfill-dl-label" placeholder="Link Name (e.g. Main File)" style="font-size:11px; padding:0.35rem 0.55rem;">
                <input type="text" class="form-input fulfill-dl-url" placeholder="https://..." style="font-family:var(--admin-font-mono); font-size:11px; padding:0.35rem 0.55rem;">
                <button type="button" class="btn-admin btn-admin-danger" style="padding:0.3rem 0.55rem; font-size:9.5px;" onclick="this.closest('.fulfill-link-row').remove(); updateFulfillLinksLabels();">
                    REMOVE
                </button>
            `;
            row.querySelector('.fulfill-dl-label').value = label || '';
            row.querySelector('.fulfill-dl-url').value = url || '';
            container.appendChild(row);
            updateFulfillLinksLabels();
        }

        function populateFulfillLinks(links) {
            const container = document.getElementById('fulfill-links-container');
            if (!container) return;
            container.innerHTML = '';
            if (Array.isArray(links) && links.length > 0) {
                links.forEach(lk => {
                    if (typeof lk === 'object' && lk !== null) {
                        addFulfillLinkRow(lk.label || '', lk.url || '');
                    } else if (typeof lk === 'string' && lk.trim()) {
                        addFulfillLinkRow('Download Link', lk.trim());
                    }
                });
            } else {
                addFulfillLinkRow('', '');
            }
            updateFulfillLinksLabels();
        }

        function loadOrderProductDefaults() {
            const ord = window._activeFulfillOrderObj;
            if (!ord) return;
            const defLinks = Array.isArray(ord.default_delivery_links) ? ord.default_delivery_links : [];
            const defMsg = ord.default_delivery_message || '';
            populateFulfillLinks(defLinks);
            const msgEl = document.getElementById('fulfill-delivery-message');
            if (msgEl) msgEl.value = defMsg;
            if (typeof showToast === 'function') {
                showToast('Loaded default download links and message from product settings.', 'success');
            }
        }

        function openFulfillModalById(id, forceStatus = null) {
            const ord = getOrderDataById(id);
            if (!ord) return;
            window._activeFulfillOrderObj = ord;

            document.getElementById('fulfill-title').textContent = 'FULFILL ORDER #' + ord.order_number;
            document.getElementById('fulfill-order-id').value = ord.id;
            document.getElementById('fulfill-status').value = forceStatus || ord.status || 'PENDING_TELEGRAM';
            document.getElementById('fulfill-license-info').value = ord.fulfilled_license_info || '';

            const summaryEl = document.getElementById('fulfill-items-summary');
            if (summaryEl) {
                const itemNames = (ord.items || []).map(it => `${it.name} (${it.sku}) x${it.qty || 1}`).join(' · ');
                summaryEl.textContent = `Customer: ${ord.owner_username ? ord.owner_username + ' (' + ord.buyer_telegram + ')' : ord.buyer_telegram} — ${itemNames}`;
            }

            const userSelect = document.getElementById('fulfill-user-id');
            if (userSelect) {
                userSelect.value = ord.owner_user_id ? String(ord.owner_user_id) : '';
            }

            const initialLinks = (Array.isArray(ord.delivery_links) && ord.delivery_links.length > 0)
                ? ord.delivery_links
                : (Array.isArray(ord.default_delivery_links) ? ord.default_delivery_links : []);
            populateFulfillLinks(initialLinks);

            const initialMsg = (ord.delivery_message && ord.delivery_message.trim())
                ? ord.delivery_message
                : (ord.default_delivery_message || '');
            const msgEl = document.getElementById('fulfill-delivery-message');
            if (msgEl) msgEl.value = initialMsg;

            openModal('modal-fulfill');
        }

        function openFulfillModal(id, num, status, info) {
            const ord = getOrderDataById(id);
            if (ord) {
                openFulfillModalById(id);
                return;
            }
            document.getElementById('fulfill-title').textContent = 'FULFILL ORDER #' + num;
            document.getElementById('fulfill-order-id').value = id;
            document.getElementById('fulfill-status').value = status;
            document.getElementById('fulfill-license-info').value = info || '';
            populateFulfillLinks([]);
            openModal('modal-fulfill');
        }

        async function onOrderRowStatusChange(id, newStatus, selectEl) {
            const prevStatus = selectEl ? (selectEl.getAttribute('data-prev-status') || 'PENDING_TELEGRAM') : 'PENDING_TELEGRAM';
            const ord = getOrderDataById(id);
            const orderNum = ord ? ord.order_number : id;

            if (newStatus === 'COMPLETED') {
                const links = (ord && Array.isArray(ord.delivery_links) && ord.delivery_links.length > 0)
                    ? ord.delivery_links
                    : (ord && Array.isArray(ord.default_delivery_links) ? ord.default_delivery_links : []);
                const msg = (ord && ord.delivery_message && ord.delivery_message.trim())
                    ? ord.delivery_message
                    : (ord && ord.default_delivery_message ? ord.default_delivery_message : '');
                const targetCustomer = (ord && ord.owner_username) ? `${ord.owner_username} (${ord.buyer_telegram})` : (ord ? ord.buyer_telegram : 'the customer');

                const sendNow = await showConfirmModal({
                    title: `COMPLETE ORDER #${orderNum} & SEND PACKAGE?`,
                    message: `You are changing Order #${orderNum} to COMPLETED for ${targetCustomer}.\n\nConfigured package ready to send automatically:\n• Download Links: ${links.length} link(s)\n• Message: ${msg ? '"' + (msg.length > 90 ? msg.substring(0, 90) + '...' : msg) + '"' : '(No message set)'}\n\nCan we send this package to the user now, or do you want to edit/change anything first?`,
                    confirmText: 'SEND & COMPLETE NOW',
                    cancelText: 'EDIT LINKS / MESSAGE',
                    danger: false,
                    note: 'Only this authenticated customer account will have access to these download links and message in their Vault.'
                });

                if (!sendNow) {
                    if (selectEl) selectEl.value = prevStatus;
                    openFulfillModalById(id, 'COMPLETED');
                    return;
                }

                const res = await fetch('/api/admin/orders/' + id, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        status: 'COMPLETED',
                        use_product_defaults: true
                    })
                });
                const data = await res.json();
                if (data.ok || data.success) {
                    updateOrderRowInPlace(id, 'COMPLETED');
                    showToast(`Order #${orderNum} completed and delivery package sent to customer.`, 'success');
                } else {
                    if (selectEl) selectEl.value = prevStatus;
                    showToast(data.error || 'Failed to update order', 'error');
                }
            } else {
                const confirmed = await showConfirmModal({
                    title: 'CHANGE ORDER STATUS',
                    message: `Change Order #${orderNum} status to ${newStatus}?`,
                    confirmText: 'UPDATE STATUS',
                    cancelText: 'CANCEL',
                    danger: newStatus === 'CANCELLED'
                });
                if (!confirmed) {
                    if (selectEl) selectEl.value = prevStatus;
                    return;
                }
                const res = await fetch('/api/admin/orders/' + id, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status: newStatus })
                });
                const data = await res.json();
                if (data.ok || data.success) {
                    updateOrderRowInPlace(id, newStatus);
                    showToast(`Order #${orderNum} status updated to ${newStatus}.`, 'success');
                } else {
                    if (selectEl) selectEl.value = prevStatus;
                    showToast(data.error || 'Failed to update order', 'error');
                }
            }
        }

        function updateOrderRowInPlace(id, newStatus, deliveryLinks, deliveryMessage, fulfilledLicenseInfo) {
            const row = document.getElementById('order-row-' + id) || document.getElementById('order-data-' + id)?.closest('tr');
            if (!row) return;

            row.setAttribute('data-status', newStatus);

            // Update status select
            const selectEl = row.querySelector('select');
            if (selectEl) {
                selectEl.value = newStatus;
                selectEl.setAttribute('data-prev-status', newStatus);
                if (newStatus === 'COMPLETED') {
                    selectEl.style.borderColor = '#10b981';
                    selectEl.style.color = '#10b981';
                } else if (newStatus === 'PENDING_TELEGRAM') {
                    selectEl.style.borderColor = '#f59e0b';
                    selectEl.style.color = '#f59e0b';
                } else {
                    selectEl.style.borderColor = '#ef4444';
                    selectEl.style.color = '#ef4444';
                }
            }

            // Update script JSON object
            const scriptEl = document.getElementById('order-data-' + id);
            let ordObj = null;
            if (scriptEl) {
                try {
                    ordObj = JSON.parse(scriptEl.textContent);
                    ordObj.status = newStatus;
                    if (deliveryLinks !== undefined) ordObj.delivery_links = deliveryLinks;
                    if (deliveryMessage !== undefined) ordObj.delivery_message = deliveryMessage;
                    if (fulfilledLicenseInfo !== undefined) ordObj.fulfilled_license_info = fulfilledLicenseInfo;
                    scriptEl.textContent = JSON.stringify(ordObj);
                } catch(e) {}
            }

            const links = (deliveryLinks !== undefined)
                ? deliveryLinks
                : ((ordObj && Array.isArray(ordObj.delivery_links) && ordObj.delivery_links.length > 0)
                    ? ordObj.delivery_links
                    : (ordObj && Array.isArray(ordObj.default_delivery_links) ? ordObj.default_delivery_links : []));
            const msg = (deliveryMessage !== undefined)
                ? deliveryMessage
                : ((ordObj && ordObj.delivery_message) ? ordObj.delivery_message : (ordObj ? (ordObj.default_delivery_message || ordObj.fulfilled_license_info || '') : ''));

            if (row.cells && row.cells.length > 6) {
                const safeMsg = (msg || '').replace(/</g, '&lt;').replace(/>/g, '&gt;');
                if (newStatus === 'COMPLETED') {
                    row.cells[6].innerHTML = `
                        <div style="color:#10b981; font-weight:700;">SENT (${links.length} link${links.length === 1 ? '' : 's'})</div>
                        <div style="color:var(--admin-muted); font-size:10px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
                            ${safeMsg || 'Delivered to user vault'}
                        </div>
                    `;
                } else {
                    row.cells[6].innerHTML = `
                        <div style="color:#00e5ff; font-size:10.5px;">READY (${links.length} product link${links.length === 1 ? '' : 's'})</div>
                        <div style="color:var(--admin-muted); font-size:10px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">
                            ${safeMsg || 'Default product package ready'}
                        </div>
                    `;
                }
            }

            recalculateOrderCounts();
        }

        function recalculateOrderCounts() {
            const rows = document.querySelectorAll('#mod-orders tbody tr[id^="order-row-"], #mod-orders tbody tr[data-status]');
            let total = rows.length;
            let pending = 0, completed = 0;
            rows.forEach(r => {
                const st = (r.getAttribute('data-status') || r.querySelector('select')?.value || '').toUpperCase();
                if (st === 'COMPLETED') completed++;
                else if (st.includes('PENDING')) pending++;
            });
            const allBtn = document.querySelector('.order-filter-btn[onclick*="ALL"]');
            if (allBtn) allBtn.textContent = `ALL (${total})`;
            const pendingBtn = document.querySelector('.order-filter-btn[onclick*="PENDING"]');
            if (pendingBtn) pendingBtn.textContent = `PENDING (${pending})`;
            const completedBtn = document.querySelector('.order-filter-btn[onclick*="COMPLETED"]');
            if (completedBtn) completedBtn.textContent = `COMPLETED (${completed})`;
            renderOrdersPagination();
        }

        async function submitFulfillment(e) {
            e.preventDefault();
            const id = document.getElementById('fulfill-order-id').value;
            const status = document.getElementById('fulfill-status').value;
            const info = document.getElementById('fulfill-license-info').value.trim();
            const message = document.getElementById('fulfill-delivery-message')
                ? document.getElementById('fulfill-delivery-message').value.trim()
                : '';
            const userIdVal = document.getElementById('fulfill-user-id')
                ? document.getElementById('fulfill-user-id').value
                : '';

            const deliveryLinks = [];
            document.querySelectorAll('#fulfill-links-container .fulfill-link-row').forEach(row => {
                const l = (row.querySelector('.fulfill-dl-label') ? row.querySelector('.fulfill-dl-label').value : '').trim();
                const u = (row.querySelector('.fulfill-dl-url') ? row.querySelector('.fulfill-dl-url').value : '').trim();
                if (u) {
                    deliveryLinks.push({ label: l || 'Download Package', url: u });
                }
            });

            if (status === 'COMPLETED') {
                const confirmed = await showConfirmModal({
                    title: 'CONFIRM DELIVERY TO CUSTOMER',
                    message: `Ready to mark this order as COMPLETED and send ${deliveryLinks.length} download link(s) and your message to the customer?\n\nClick "SEND & COMPLETE" to deliver now, or "BACK TO EDIT" if you need to change anything.`,
                    confirmText: 'SEND & COMPLETE',
                    cancelText: 'BACK TO EDIT',
                    danger: false,
                    note: 'The download link(s) and message will be unlocked exclusively in this authenticated user\'s Vault.'
                });
                if (!confirmed) return;
            }

            const payload = {
                status: status,
                fulfilled_license_info: info,
                delivery_links: deliveryLinks,
                delivery_message: message
            };
            if (userIdVal !== '') {
                payload.user_id = parseInt(userIdVal, 10);
            }

            const res = await fetch('/api/admin/orders/' + id, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (data.ok || data.success) {
                closeModal('modal-fulfill');
                updateOrderRowInPlace(id, status, deliveryLinks, message, info);
                showToast(status === 'COMPLETED' ? 'Order completed and sent to customer vault!' : 'Order fulfillment updated.', 'success');
            } else {
                showToast(data.error || 'Fulfillment error', 'error');
            }
        }

        async function deleteOrder(id, num) {
            const confirmed = await showConfirmModal({
                title: 'DELETE ORDER',
                message: `Are you sure you want to permanently delete Order #${num}?`,
                confirmText: 'DELETE ORDER',
                note: 'WARNING: Order details and fulfilled license keys for this transaction will be permanently removed.'
            });
            if (!confirmed) return;
            const res = await fetch('/api/admin/orders/' + id, { method: 'DELETE' });
            const data = await res.json();
            if (data.ok || data.success) {
                const row = document.getElementById('order-row-' + id) || document.getElementById('order-data-' + id)?.closest('tr');
                if (row) row.remove();
                recalculateOrderCounts();
                showToast(`Order #${num} permanently deleted.`, 'info');
            } else {
                showToast(data.error || 'Delete error', 'error');
            }
        }

        // ==========================================
        // ORDERS PAGINATION & SEARCH (30 / PAGE)
        // ==========================================
        let ordersCurrentPage = 1;
        const ORDERS_PAGE_SIZE = 30;
        let currentOrdersStatusFilter = 'ALL';

        function goToOrdersPrevPage() {
            if (ordersCurrentPage > 1) {
                ordersCurrentPage--;
                renderOrdersPagination();
                const wrap = document.querySelector('#mod-orders .admin-table-wrap');
                if (wrap) wrap.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        }

        function goToOrdersNextPage() {
            const matchingRows = getMatchingOrdersRows();
            const totalPages = Math.max(1, Math.ceil(matchingRows.length / ORDERS_PAGE_SIZE));
            if (ordersCurrentPage < totalPages) {
                ordersCurrentPage++;
                renderOrdersPagination();
                const wrap = document.querySelector('#mod-orders .admin-table-wrap');
                if (wrap) wrap.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        }

        function filterAdminOrders(statusFilter, btn) {
            document.querySelectorAll('.order-filter-btn').forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');
            currentOrdersStatusFilter = statusFilter || 'ALL';
            ordersCurrentPage = 1;
            renderOrdersPagination();
        }
        window.filterAdminOrders = filterAdminOrders;

        function onOrderSearchInput(val) {
            const clearBtn = document.getElementById('orders-search-clear-btn');
            if (clearBtn) {
                clearBtn.style.display = (val && val.trim().length > 0) ? 'inline-block' : 'none';
            }
            ordersCurrentPage = 1;
            renderOrdersPagination();
        }

        function clearOrderSearch() {
            const input = document.getElementById('orders-search-input');
            const clearBtn = document.getElementById('orders-search-clear-btn');
            if (input) {
                input.value = '';
                input.focus();
            }
            if (clearBtn) clearBtn.style.display = 'none';
            ordersCurrentPage = 1;
            renderOrdersPagination();
        }

        function getMatchingOrdersRows() {
            const searchInput = document.getElementById('orders-search-input');
            const query = (searchInput ? searchInput.value : '').toLowerCase().trim();
            const rows = document.querySelectorAll('#mod-orders table#orders-table tbody tr.order-row');
            const matching = [];

            rows.forEach(row => {
                const searchData = (row.getAttribute('data-search') || row.textContent || '').toLowerCase();
                const rowStatus = (row.getAttribute('data-status') || row.querySelector('select')?.value || '').toUpperCase();

                const matchesQuery = !query || searchData.includes(query);
                let matchesStatus = true;

                if (currentOrdersStatusFilter === 'PENDING') {
                    matchesStatus = rowStatus.includes('PENDING');
                } else if (currentOrdersStatusFilter === 'COMPLETED') {
                    matchesStatus = rowStatus.includes('COMPLETED');
                } else if (currentOrdersStatusFilter !== 'ALL') {
                    matchesStatus = rowStatus.includes(currentOrdersStatusFilter);
                }

                if (matchesQuery && matchesStatus) {
                    matching.push(row);
                }
            });
            return matching;
        }

        function renderOrdersPagination() {
            const allRows = document.querySelectorAll('#mod-orders table#orders-table tbody tr.order-row');
            const matchingRows = getMatchingOrdersRows();
            const total = matchingRows.length;
            const totalPages = Math.max(1, Math.ceil(total / ORDERS_PAGE_SIZE));

            if (ordersCurrentPage > totalPages) ordersCurrentPage = totalPages;
            if (ordersCurrentPage < 1) ordersCurrentPage = 1;

            const startIndex = (ordersCurrentPage - 1) * ORDERS_PAGE_SIZE;
            const endIndex = Math.min(startIndex + ORDERS_PAGE_SIZE, total);

            allRows.forEach(row => {
                row.style.display = 'none';
            });

            for (let i = startIndex; i < endIndex; i++) {
                matchingRows[i].style.display = '';
            }

            const countEl = document.getElementById('orders-search-count');
            if (countEl) {
                countEl.textContent = `SHOWING ${total} ORDER${total === 1 ? '' : 'S'} (30 / PAGE)`;
            }

            const noResultsEl = document.getElementById('orders-no-results');
            if (noResultsEl) {
                noResultsEl.style.display = (total === 0) ? '' : 'none';
            }

            const pageRangeEl = document.getElementById('orders-page-range');
            if (pageRangeEl) {
                pageRangeEl.textContent = total === 0 ? '0–0' : `${startIndex + 1}–${endIndex}`;
            }
            const totalCountEl = document.getElementById('orders-total-count');
            if (totalCountEl) totalCountEl.textContent = total;

            const curPageEl = document.getElementById('orders-current-page');
            if (curPageEl) curPageEl.textContent = ordersCurrentPage;

            const totPagesEl = document.getElementById('orders-total-pages');
            if (totPagesEl) totPagesEl.textContent = totalPages;

            const prevBtn = document.getElementById('btn-orders-prev');
            if (prevBtn) {
                prevBtn.disabled = (ordersCurrentPage <= 1);
                prevBtn.style.opacity = (ordersCurrentPage <= 1) ? '0.4' : '1';
                prevBtn.style.cursor = (ordersCurrentPage <= 1) ? 'not-allowed' : 'pointer';
            }

            const nextBtn = document.getElementById('btn-orders-next');
            if (nextBtn) {
                nextBtn.disabled = (ordersCurrentPage >= totalPages);
                nextBtn.style.opacity = (ordersCurrentPage >= totalPages) ? '0.4' : '1';
                nextBtn.style.cursor = (ordersCurrentPage >= totalPages) ? 'not-allowed' : 'pointer';
            }
        }

        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', renderOrdersPagination);
        } else {
            renderOrdersPagination();
        }

        // ==========================================
        // DEDICATED PRODUCT STUDIO CONTROLS
        // ==========================================
