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
            document.getElementById('rev-featured-manifesto').checked = true;

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
                document.getElementById('rev-featured-manifesto').checked = !!data.featured_manifesto;

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
                featured_manifesto: document.getElementById('rev-featured-manifesto').checked,
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
