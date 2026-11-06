        // HOMEPAGE SHOWCASE CURATION LOGIC
        // ==========================================
        function initHomeCurationPreviews() {
            for (let s = 1; s <= 4; s++) {
                updateCurateProdPreview(s);
                updateCuratePostPreview(s);
            }
        }

        function updateCurateProdPreview(slot) {
            const sel = document.getElementById(`curate-prod-slot-${slot}`);
            if (!sel) return;
            const val = String(sel.value || '').trim();
            const box = document.getElementById(`curate-prod-preview-${slot}`);
            const emptyBox = document.getElementById(`curate-prod-empty-${slot}`);
            const prods = window.ADMIN_CATALOG_PRODUCTS || [];
            const prod = prods.find(p => String(p.id) === val || p.sku === val);
            if (prod) {
                if (box) box.style.display = 'flex';
                if (emptyBox) emptyBox.style.display = 'none';
                const img = document.getElementById(`curate-prod-img-${slot}`);
                if (img) img.src = prod.image_url || 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=1200&q=85';
                const nameEl = document.getElementById(`curate-prod-name-${slot}`);
                if (nameEl) nameEl.textContent = prod.name;
                const skuEl = document.getElementById(`curate-prod-sku-${slot}`);
                if (skuEl) skuEl.textContent = prod.sku;
                const priceEl = document.getElementById(`curate-prod-price-${slot}`);
                if (priceEl) priceEl.textContent = `$${parseFloat(prod.price || 0).toFixed(0)}`;
            } else {
                if (box) box.style.display = 'none';
                if (emptyBox) emptyBox.style.display = 'flex';
            }
        }

        function updateCuratePostPreview(slot) {
            const sel = document.getElementById(`curate-post-slot-${slot}`);
            if (!sel) return;
            const val = String(sel.value || '').trim();
            const box = document.getElementById(`curate-post-preview-${slot}`);
            const emptyBox = document.getElementById(`curate-post-empty-${slot}`);
            const posts = window.ADMIN_POSTS || [];
            const post = posts.find(p => String(p.id) === val || p.slug === val);
            if (post) {
                if (box) box.style.display = 'flex';
                if (emptyBox) emptyBox.style.display = 'none';
                const img = document.getElementById(`curate-post-img-${slot}`);
                if (img) img.src = post.image_url || 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1200&q=85';
                const nameEl = document.getElementById(`curate-post-name-${slot}`);
                if (nameEl) nameEl.textContent = post.title;
                const cveEl = document.getElementById(`curate-post-cve-${slot}`);
                if (cveEl) cveEl.textContent = post.cve_id || 'RESEARCH';
                const authorEl = document.getElementById(`curate-post-author-${slot}`);
                if (authorEl) authorEl.textContent = post.author || post.author_name || '';
            } else {
                if (box) box.style.display = 'none';
                if (emptyBox) emptyBox.style.display = 'flex';
            }
        }

        function removeProductSlot(slot) {
            const sel = document.getElementById(`curate-prod-slot-${slot}`);
            if (!sel) return;
            sel.value = '';
            updateCurateProdPreview(slot);
            if (typeof onThemeFieldInput === 'function') {
                onThemeFieldInput(sel.name, '');
            }
            sel.focus();
            sel.style.borderColor = '#00e5ff';
            setTimeout(() => { sel.style.borderColor = ''; }, 2500);
            flashCurationStatus(`Removed product from Serial 0${slot}. Select a new system from the dropdown to assign.`);
        }

        function removePostSlot(slot) {
            const sel = document.getElementById(`curate-post-slot-${slot}`);
            if (!sel) return;
            sel.value = '';
            updateCuratePostPreview(slot);
            if (typeof onThemeFieldInput === 'function') {
                onThemeFieldInput(sel.name, '');
            }
            sel.focus();
            sel.style.borderColor = '#10b981';
            setTimeout(() => { sel.style.borderColor = ''; }, 2500);
            flashCurationStatus(`Removed advisory from Serial 0${slot}. Select a new advisory from the dropdown to assign.`);
        }

        function onCurateProductChange(slot, val) {
            updateCurateProdPreview(slot);
        }

        function onCuratePostChange(slot, val) {
            updateCuratePostPreview(slot);
        }

        function moveProductSlot(fromSlot, direction) {
            const toSlot = fromSlot + direction;
            if (toSlot < 1 || toSlot > 4) return;
            const selA = document.getElementById(`curate-prod-slot-${fromSlot}`);
            const selB = document.getElementById(`curate-prod-slot-${toSlot}`);
            if (!selA || !selB) return;
            const temp = selA.value;
            selA.value = selB.value;
            selB.value = temp;
            updateCurateProdPreview(fromSlot);
            updateCurateProdPreview(toSlot);
            if (typeof onThemeFieldInput === 'function') {
                onThemeFieldInput(selA.name, selA.value);
                onThemeFieldInput(selB.name, selB.value);
            }
            flashCurationStatus(`Swapped Product Serial 0${fromSlot} ⇄ Serial 0${toSlot}`);
        }

        function movePostSlot(fromSlot, direction) {
            const toSlot = fromSlot + direction;
            if (toSlot < 1 || toSlot > 4) return;
            const selA = document.getElementById(`curate-post-slot-${fromSlot}`);
            const selB = document.getElementById(`curate-post-slot-${toSlot}`);
            if (!selA || !selB) return;
            const temp = selA.value;
            selA.value = selB.value;
            selB.value = temp;
            updateCuratePostPreview(fromSlot);
            updateCuratePostPreview(toSlot);
            if (typeof onThemeFieldInput === 'function') {
                onThemeFieldInput(selA.name, selA.value);
                onThemeFieldInput(selB.name, selB.value);
            }
            flashCurationStatus(`Swapped Journal Serial 0${fromSlot} ⇄ Serial 0${toSlot}`);
        }

        function flashCurationStatus(msg) {
            const el = document.getElementById('curate-save-status');
            if (el) {
                el.innerHTML = `<span style="color:#00e5ff;">${msg}</span>`;
                setTimeout(() => { if (el.innerHTML.includes(msg)) el.innerHTML = ''; }, 3500);
            }
        }

        async function saveDirectHomeCuration() {
            const payload = {};
            for (let s = 1; s <= 4; s++) {
                const prodSel = document.getElementById(`curate-prod-slot-${s}`);
                if (prodSel) payload[`home_featured_product_${s}`] = prodSel.value;
                const postSel = document.getElementById(`curate-post-slot-${s}`);
                if (postSel) payload[`home_featured_post_${s}`] = postSel.value;
            }
            const statusEl = document.getElementById('curate-save-status');
            const postStatusEl = document.getElementById('curate-post-save-status');
            const msgSaving = '<span style="color:#00e5ff;">Saving showcase curation...</span>';
            if (statusEl) statusEl.innerHTML = msgSaving;
            if (postStatusEl) postStatusEl.innerHTML = msgSaving;

            try {
                const res = await fetch('/api/admin/home-curation', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (res.ok && data.ok) {
                    const msgSuccess = '<span style="color:#10b981; font-weight:700;">4 PRODUCTS &amp; 4 JOURNALS CURATION SAVED &amp; SYNCED LIVE!</span>';
                    if (statusEl) statusEl.innerHTML = msgSuccess;
                    if (postStatusEl) postStatusEl.innerHTML = msgSuccess;
                    if (typeof showThemeToast === 'function') {
                        showThemeToast('HOMEPAGE CURATION PERSISTED: 4 products & 4 journals updated on homepage.');
                    }
                    const iframe = (typeof getThemeIframe === 'function') ? getThemeIframe() : (typeof previewIframe !== 'undefined' ? previewIframe : document.getElementById('theme-preview-iframe'));
                    if (iframe && iframe.contentWindow) {
                        try { iframe.contentWindow.location.reload(); } catch(e) {}
                    }
                } else {
                    const msgErr = `<span style="color:#ef4444;">Error: ${data.error || 'Failed to save'}</span>`;
                    if (statusEl) statusEl.innerHTML = msgErr;
                    if (postStatusEl) postStatusEl.innerHTML = msgErr;
                }
            } catch (err) {
                const msgNetErr = `<span style="color:#ef4444;">Network error: ${err.message}</span>`;
                if (statusEl) statusEl.innerHTML = msgNetErr;
                if (postStatusEl) postStatusEl.innerHTML = msgNetErr;
            }
        }

        function openHomeCurationModal() {
            if (typeof switchFeature === 'function') {
                switchFeature('products', 'curation');
            } else if (typeof switchAdminTab === 'function') {
                switchAdminTab('products');
            }
        }

        // ==========================================
