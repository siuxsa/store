        function openFulfillModal(id, num, status, info) {
            document.getElementById('fulfill-title').textContent = 'FULFILL ORDER #' + num;
            document.getElementById('fulfill-order-id').value = id;
            document.getElementById('fulfill-status').value = status;
            document.getElementById('fulfill-license-info').value = info || '';
            document.getElementById('modal-fulfill').classList.add('is-open');
        }

        async function submitFulfillment(e) {
            e.preventDefault();
            const id = document.getElementById('fulfill-order-id').value;
            const status = document.getElementById('fulfill-status').value;
            const info = document.getElementById('fulfill-license-info').value;

            const res = await fetch('/api/admin/orders/' + id, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status: status, fulfilled_license_info: info })
            });
            const data = await res.json();
            if (data.ok || data.success) {
                alert('Order fulfillment updated.');
                location.reload();
            } else {
                alert(data.error || 'Fulfillment error');
            }
        }

        async function deleteOrder(id, num) {
            if (!confirm('Permanently delete Order #' + num + '?')) return;
            const res = await fetch('/api/admin/orders/' + id, { method: 'DELETE' });
            const data = await res.json();
            if (data.ok || data.success) location.reload();
            else alert(data.error || 'Delete error');
        }

        // ==========================================
        // DEDICATED PRODUCT STUDIO CONTROLS
        // ==========================================
