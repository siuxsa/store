        function openReviewModal() {
            document.getElementById('rev-modal-title').textContent = 'ADD VERIFIED REVIEW';
            document.getElementById('rev-id').value = '';
            document.getElementById('rev-product-sku').value = '';
            document.getElementById('rev-rating').value = '5';
            document.getElementById('rev-author-name').value = '';
            document.getElementById('rev-author-role').value = 'Principal Security Architect';
            document.getElementById('rev-author-org').value = 'Enterprise Cyber Operations';
            document.getElementById('rev-verified-badge').value = 'VERIFIED ENTERPRISE DEPLOYMENT · PGP SIGNED';
            document.getElementById('rev-title').value = '';
            document.getElementById('rev-content').value = '';
            if (document.getElementById('rev-featured-manifesto')) document.getElementById('rev-featured-manifesto').checked = false;

            const today = new Date().toISOString().split('T')[0];
            document.getElementById('rev-date').value = today;

            openModal('modal-review');
        }

        function openReviewModalForId(reviewId) {
            const scriptTag = document.getElementById('review-data-' + reviewId);
            if (!scriptTag) return;
            try {
                const data = JSON.parse(scriptTag.textContent);
                document.getElementById('rev-modal-title').textContent = 'EDIT VERIFIED REVIEW #' + reviewId;
                document.getElementById('rev-id').value = data.id || '';
                document.getElementById('rev-product-sku').value = data.product_sku || '';
                document.getElementById('rev-rating').value = String(data.rating || 5);
                document.getElementById('rev-author-name').value = data.author_name || '';
                document.getElementById('rev-author-role').value = data.author_role || '';
                document.getElementById('rev-author-org').value = data.author_org || '';
                document.getElementById('rev-verified-badge').value = data.verified_badge || 'VERIFIED ENTERPRISE DEPLOYMENT · PGP SIGNED';
                document.getElementById('rev-title').value = data.title || '';
                document.getElementById('rev-content').value = data.content || '';
                if (document.getElementById('rev-featured-manifesto')) document.getElementById('rev-featured-manifesto').checked = !!data.featured_manifesto;

                if (data.created_at) {
                    document.getElementById('rev-date').value = data.created_at.substring(0, 10);
                } else {
                    document.getElementById('rev-date').value = new Date().toISOString().split('T')[0];
                }

                openModal('modal-review');
            } catch(e) {
                console.error('Failed to parse review data', e);
            }
        }

        async function submitReviewForm(e) {
            if (e) e.preventDefault();
            const saveBtn = document.getElementById('btn-save-review');
            const originalText = saveBtn ? saveBtn.textContent : 'SAVE VERIFIED REVIEW →';

            const payload = {
                id: document.getElementById('rev-id').value ? parseInt(document.getElementById('rev-id').value) : null,
                product_sku: document.getElementById('rev-product-sku').value,
                rating: parseInt(document.getElementById('rev-rating').value) || 5,
                author_name: document.getElementById('rev-author-name').value.trim(),
                author_role: document.getElementById('rev-author-role').value.trim(),
                author_org: document.getElementById('rev-author-org').value.trim(),
                verified_badge: document.getElementById('rev-verified-badge').value.trim(),
                title: document.getElementById('rev-title').value.trim(),
                content: document.getElementById('rev-content').value.trim(),
                created_at: document.getElementById('rev-date').value ? document.getElementById('rev-date').value + ' 12:00:00' : ''
            };

            if (!payload.author_name || !payload.content) {
                alert('Please enter both Author Name and Assessment Content.');
                return;
            }

            if (saveBtn) {
                saveBtn.disabled = true;
                saveBtn.textContent = 'COMMITTING REVIEW...';
            }

            try {
                const res = await fetch('/api/admin/reviews', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (data.ok || data.success) {
                    try { 
                        sessionStorage.setItem('activeAdminFeature', 'products'); 
                        sessionStorage.setItem('activeSubtab_products', 'reviews'); 
                    } catch(err) {}
                    window.location.reload();
                } else {
                    alert('Error saving review: ' + (data.error || 'Unknown error'));
                    if (saveBtn) {
                        saveBtn.disabled = false;
                        saveBtn.textContent = originalText;
                    }
                }
            } catch(err) {
                alert('Network error while saving review: ' + err.message);
                if (saveBtn) {
                    saveBtn.disabled = false;
                    saveBtn.textContent = originalText;
                }
            }
        }

        async function deleteReview(reviewId, authorName) {
            if (!confirm(`Are you sure you want to permanently delete verified assessment from "${authorName}"? This action cannot be undone.`)) {
                return;
            }

            try {
                const res = await fetch(`/api/admin/reviews/${reviewId}`, {
                    method: 'DELETE'
                });
                const data = await res.json();
                if (data.ok || data.success) {
                    try { 
                        sessionStorage.setItem('activeAdminFeature', 'products'); 
                        sessionStorage.setItem('activeSubtab_products', 'reviews'); 
                    } catch(err) {}
                    window.location.reload();
                } else {
                    alert('Error deleting review: ' + (data.error || 'Unknown error'));
                }
            } catch(err) {
                alert('Network error while deleting review: ' + err.message);
            }
        }

        // ==========================================
        // JOURNAL VERIFICATION LOGS MODERATION
        // ==========================================

        // ==========================================
        // HOMEPAGE CLIENT REVIEWS SHOWCASE CURATION
        // ==========================================
        window.CURATED_REVIEW_IDS = window.CURATED_REVIEW_IDS || [];

        function initHomepageReviewsCuration() {
            const grid = document.getElementById('curate-reviews-slots-grid');
            if (!grid) return;

            const allRevs = window.ADMIN_REVIEWS || [];
            let initialIds = [];

            // 1. Try saved JSON setting
            if (window.ORIGINAL_THEME_SETTINGS && window.ORIGINAL_THEME_SETTINGS.home_featured_reviews_json) {
                try {
                    const parsed = typeof window.ORIGINAL_THEME_SETTINGS.home_featured_reviews_json === 'string'
                        ? JSON.parse(window.ORIGINAL_THEME_SETTINGS.home_featured_reviews_json)
                        : window.ORIGINAL_THEME_SETTINGS.home_featured_reviews_json;
                    if (Array.isArray(parsed) && parsed.length > 0) {
                        initialIds = parsed.map(x => parseInt(x)).filter(x => !isNaN(x) && x > 0);
                    }
                } catch(e) {}
            }

            // 2. Try numbered settings home_featured_review_1..12
            if (!initialIds.length && window.ORIGINAL_THEME_SETTINGS) {
                for (let i = 1; i <= 12; i++) {
                    const v = window.ORIGINAL_THEME_SETTINGS[`home_featured_review_${i}`];
                    if (v && !isNaN(parseInt(v)) && parseInt(v) > 0) {
                        initialIds.push(parseInt(v));
                    }
                }
            }

            // 3. Fallback to reviews marked featured_manifesto in database
            if (!initialIds.length) {
                initialIds = allRevs.filter(r => r.featured_manifesto).map(r => r.id);
            }

            // 4. Default to first 4 reviews if none selected
            if (!initialIds.length) {
                initialIds = allRevs.slice(0, 4).map(r => r.id);
            }

            window.CURATED_REVIEW_IDS = initialIds;
            renderHomepageReviewsSlots();
        }

        function renderHomepageReviewsSlots() {
            const grid = document.getElementById('curate-reviews-slots-grid');
            if (!grid) return;

            const badge = document.getElementById('curate-reviews-count-badge');
            if (badge) badge.textContent = String(window.CURATED_REVIEW_IDS.length);

            const allRevs = window.ADMIN_REVIEWS || [];
            const revMap = {};
            allRevs.forEach(r => { revMap[r.id] = r; });

            grid.innerHTML = '';

            window.CURATED_REVIEW_IDS.forEach((revId, idx) => {
                const slotNum = idx + 1;
                const rev = revMap[revId] || null;
                const isFirst = idx === 0;
                const isLast = idx === window.CURATED_REVIEW_IDS.length - 1;

                const slotCard = document.createElement('div');
                slotCard.className = 'curate-review-slot-box';
                slotCard.style.cssText = 'background:rgba(255,255,255,0.02); border:1px solid var(--admin-border); padding:1rem; border-radius:4px; display:flex; flex-direction:column; gap:0.65rem;';

                // Top bar
                const topBar = document.createElement('div');
                topBar.style.cssText = 'display:flex; justify-content:space-between; align-items:center;';
                topBar.innerHTML = `
                    <span style="background:${isFirst ? '#00e5ff' : 'rgba(255,255,255,0.1)'}; color:${isFirst ? '#000' : '#fff'}; font-family:var(--admin-font-mono); font-size:10px; font-weight:800; padding:2px 7px; border-radius:2px;">
                        SLOT 0${slotNum}${isFirst ? ' · LEAD STREAM' : ''}
                    </span>
                    <div style="display:flex; gap:4px;">
                        <button type="button" class="btn-admin btn-admin-outline" style="padding:2px 6px; font-size:10px; ${isFirst ? 'opacity:0.3; cursor:not-allowed;' : ''}" onclick="moveReviewSlot(${idx}, -1)" ${isFirst ? 'disabled' : ''}>UP</button>
                        <button type="button" class="btn-admin btn-admin-outline" style="padding:2px 6px; font-size:10px; ${isLast ? 'opacity:0.3; cursor:not-allowed;' : ''}" onclick="moveReviewSlot(${idx}, 1)" ${isLast ? 'disabled' : ''}>DOWN</button>
                        <button type="button" class="btn-admin btn-admin-danger" style="padding:2px 6px; font-size:10px;" onclick="removeReviewSlot(${idx})">REMOVE</button>
                    </div>
                `;
                slotCard.appendChild(topBar);

                // Dropdown select
                const selectWrap = document.createElement('div');
                let optionsHtml = `<option value="">-- VACANT / SELECT REVIEW --</option>`;
                allRevs.forEach(r => {
                    const isSel = r.id === revId ? 'selected' : '';
                    const stars = '★'.repeat(r.rating || 5);
                    const skuTag = r.product_sku ? `[${r.product_sku}] ` : '[GLOBAL] ';
                    const shortTitle = (r.title || r.content || '').substring(0, 32);
                    optionsHtml += `<option value="${r.id}" ${isSel}>${stars} ${skuTag}"${shortTitle}..." — ${r.author_name}</option>`;
                });

                selectWrap.innerHTML = `
                    <select class="form-input" style="font-size:12px; padding:0.45rem 0.6rem; width:100%;" onchange="onCurateReviewSlotChange(${idx}, this.value)">
                        ${optionsHtml}
                    </select>
                `;
                slotCard.appendChild(selectWrap);

                // Preview box
                const previewWrap = document.createElement('div');
                if (rev) {
                    const starsStr = '★'.repeat(rev.rating || 5);
                    previewWrap.style.cssText = 'background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.06); padding:8px 10px; border-radius:3px; font-size:11px;';
                    previewWrap.innerHTML = `
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                            <span style="color:#f59e0b; font-weight:700; letter-spacing:2px; font-size:12px;">${starsStr}</span>
                            <span style="color:#00e5ff; font-family:var(--admin-font-mono); font-size:9.5px;">${rev.product_sku || 'ALL CATALOG'}</span>
                        </div>
                        <div style="font-weight:700; color:#fff; font-size:11.5px; margin-bottom:2px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                            ${rev.title || 'Verified Operator Review'}
                        </div>
                        <div style="color:var(--admin-muted); font-size:10.5px; line-height:1.35; margin-bottom:4px; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;">
                            "${rev.content}"
                        </div>
                        <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid rgba(255,255,255,0.06); padding-top:4px; font-size:10px; color:var(--admin-muted);">
                            <span style="color:#fff; font-weight:600;">${rev.author_name}</span>
                            <span style="color:#10b981;">${rev.verified_badge || '● VERIFIED'}</span>
                        </div>
                    `;
                } else {
                    previewWrap.style.cssText = 'padding:14px; background:rgba(255,255,255,0.015); border:1px dashed rgba(0,229,255,0.35); border-radius:3px; font-family:var(--admin-font-mono); font-size:11px; color:#00e5ff; display:flex; align-items:center; justify-content:space-between;';
                    previewWrap.innerHTML = `
                        <span>+ SLOT 0${slotNum} VACANT</span>
                        <span style="font-size:9px; background:rgba(0,229,255,0.1); padding:1px 5px; border-radius:2px;">CHOOSE REVIEW</span>
                    `;
                }
                slotCard.appendChild(previewWrap);

                grid.appendChild(slotCard);
            });

            updateTableShowcaseBadges();
        }

        function updateTableShowcaseBadges() {
            const allRevs = window.ADMIN_REVIEWS || [];
            allRevs.forEach(r => {
                const td = document.getElementById(`review-row-manifesto-${r.id}`);
                if (!td) return;
                const slotIdx = window.CURATED_REVIEW_IDS.indexOf(r.id);
                if (slotIdx !== -1) {
                    td.innerHTML = `
                        <div style="display:flex; flex-direction:column; gap:4px;">
                            <span class="badge-tag" style="background:#10b981; color:#000; font-weight:800; font-size:10px; padding:2px 6px;">
                                ★ SLOT 0${slotIdx + 1}
                            </span>
                            <button type="button" class="btn-admin btn-admin-outline" style="padding:2px 6px; font-size:10px; color:#ef4444; border-color:rgba(239,68,68,0.35);" onclick="toggleReviewInShowcase(${r.id})">
                                REMOVE
                            </button>
                        </div>
                    `;
                } else {
                    td.innerHTML = `
                        <div style="display:flex; flex-direction:column; gap:4px;">
                            <span style="color:var(--admin-muted); font-size:11px;">CATALOG ONLY</span>
                            <button type="button" class="btn-admin btn-admin-outline" style="padding:2px 6px; font-size:10px; color:#00e5ff; border-color:rgba(0,229,255,0.4);" onclick="toggleReviewInShowcase(${r.id})">
                                + ADD TO HOME
                            </button>
                        </div>
                    `;
                }
            });
        }

        function onCurateReviewSlotChange(index, newId) {
            const val = newId ? parseInt(newId) : null;
            window.CURATED_REVIEW_IDS[index] = val;
            renderHomepageReviewsSlots();
        }

        function moveReviewSlot(index, direction) {
            const targetIdx = index + direction;
            if (targetIdx < 0 || targetIdx >= window.CURATED_REVIEW_IDS.length) return;
            const temp = window.CURATED_REVIEW_IDS[index];
            window.CURATED_REVIEW_IDS[index] = window.CURATED_REVIEW_IDS[targetIdx];
            window.CURATED_REVIEW_IDS[targetIdx] = temp;
            renderHomepageReviewsSlots();
        }

        function removeReviewSlot(index) {
            window.CURATED_REVIEW_IDS.splice(index, 1);
            renderHomepageReviewsSlots();
        }

        function addReviewShowcaseSlot(optReviewId) {
            const id = optReviewId ? parseInt(optReviewId) : null;
            window.CURATED_REVIEW_IDS.push(id);
            renderHomepageReviewsSlots();
        }

        function setReviewShowcaseSlotCount(targetCount) {
            const allRevs = window.ADMIN_REVIEWS || [];
            if (window.CURATED_REVIEW_IDS.length > targetCount) {
                window.CURATED_REVIEW_IDS = window.CURATED_REVIEW_IDS.slice(0, targetCount);
            } else {
                while (window.CURATED_REVIEW_IDS.length < targetCount) {
                    const nextUnselected = allRevs.find(r => !window.CURATED_REVIEW_IDS.includes(r.id));
                    window.CURATED_REVIEW_IDS.push(nextUnselected ? nextUnselected.id : null);
                }
            }
            renderHomepageReviewsSlots();
        }

        function toggleReviewInShowcase(reviewId) {
            const id = parseInt(reviewId);
            const existingIdx = window.CURATED_REVIEW_IDS.indexOf(id);
            if (existingIdx !== -1) {
                removeReviewSlot(existingIdx);
            } else {
                const vacantIdx = window.CURATED_REVIEW_IDS.indexOf(null);
                if (vacantIdx !== -1) {
                    window.CURATED_REVIEW_IDS[vacantIdx] = id;
                    renderHomepageReviewsSlots();
                } else {
                    addReviewShowcaseSlot(id);
                }
            }
        }

        async function saveHomepageReviewsShowcase() {
            const statusEl = document.getElementById('curate-reviews-status');
            const validIds = window.CURATED_REVIEW_IDS.filter(id => id && !isNaN(id) && id > 0);

            if (statusEl) {
                statusEl.style.color = '#00e5ff';
                statusEl.textContent = 'COMMITTING HOMEPAGE SHOWCASE TO SYSTEM MATRIX...';
            }

            try {
                const res = await fetch('/api/admin/reviews/curation', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ reviews: validIds })
                });
                const data = await res.json();
                if (data.ok || data.success) {
                    if (statusEl) {
                        statusEl.style.color = '#10b981';
                        statusEl.textContent = `✓ SUCCESS: ${validIds.length} REVIEWS DEPLOYED LIVE TO HOMEPAGE MANIFESTO!`;
                    }
                    if (window.ORIGINAL_THEME_SETTINGS) {
                        window.ORIGINAL_THEME_SETTINGS.home_featured_reviews_json = JSON.stringify(validIds);
                    }
                    if (typeof showThemeToast === 'function') {
                        showThemeToast(`Homepage Reviews Showcase saved (${validIds.length} reviews active).`);
                    }
                    setTimeout(() => {
                        if (statusEl) statusEl.textContent = '';
                    }, 5000);
                } else {
                    if (statusEl) {
                        statusEl.style.color = '#ef4444';
                        statusEl.textContent = 'ERROR: ' + (data.error || 'Failed to save showcase.');
                    }
                }
            } catch(err) {
                if (statusEl) {
                    statusEl.style.color = '#ef4444';
                    statusEl.textContent = 'NETWORK ERROR: ' + err.message;
                }
            }
        }

        document.addEventListener('DOMContentLoaded', () => {
            initHomepageReviewsCuration();
        });
