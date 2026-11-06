        function recalculateCommentStats() {
            const rows = document.querySelectorAll('#mod-comments tbody tr.comment-row');
            let total = rows.length;
            let pending = 0, approved = 0, rejected = 0;
            rows.forEach(r => {
                const status = (r.getAttribute('data-status') || '').toUpperCase();
                if (status === 'APPROVED') approved++;
                else if (status === 'PENDING') pending++;
                else if (status === 'REJECTED') rejected++;
            });

            const totalEl = document.getElementById('comment-stat-total');
            if (totalEl) totalEl.textContent = total;
            const pendingEl = document.getElementById('comment-stat-pending');
            if (pendingEl) pendingEl.textContent = pending;
            const approvedEl = document.getElementById('comment-stat-approved');
            if (approvedEl) approvedEl.textContent = approved;
            const rejectedEl = document.getElementById('comment-stat-rejected');
            if (rejectedEl) rejectedEl.textContent = rejected;
        }

        async function updateCommentStatus(commentId, newStatus) {
            try {
                const res = await fetch(`/api/admin/comments/${commentId}/status`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status: newStatus })
                });
                const data = await res.json();
                if (data.ok || data.success) {
                    const row = document.getElementById('comment-row-' + commentId);
                    if (row) {
                        row.style.background = (newStatus === 'PENDING') ? 'rgba(245,158,11,0.04)' : '';
                        row.setAttribute('data-status', newStatus);
                        let s = row.getAttribute('data-search') || '';
                        s = s.replace(/APPROVED|PENDING|REJECTED/g, newStatus);
                        row.setAttribute('data-search', s);
                        if (row.cells && row.cells.length > 0) {
                            if (newStatus === 'APPROVED') {
                                row.cells[0].innerHTML = `<span class="status-pill completed" style="font-size:10px; background:rgba(16,185,129,0.15); color:#10b981; border:1px solid #10b981;">APPROVED</span>`;
                            } else if (newStatus === 'PENDING') {
                                row.cells[0].innerHTML = `<span class="status-pill pending" style="font-size:10px; background:rgba(245,158,11,0.18); color:#f59e0b; border:1px solid #f59e0b; font-weight:700;">PENDING REVIEW</span>`;
                            } else {
                                row.cells[0].innerHTML = `<span class="status-pill cancelled" style="font-size:10px; background:rgba(239,68,68,0.15); color:#ef4444; border:1px solid #ef4444;">REJECTED</span>`;
                            }
                        }
                        const actionCell = row.cells[row.cells.length - 1];
                        if (actionCell) {
                            let btns = '';
                            if (newStatus !== 'APPROVED') {
                                btns += `<button type="button" class="btn-admin btn-admin-primary" style="padding:0.35rem 0.65rem; background:#10b981; border-color:#10b981; color:#000; font-weight:700;" onclick="updateCommentStatus(${commentId}, 'APPROVED')">APPROVE</button> `;
                            }
                            if (newStatus !== 'REJECTED') {
                                btns += `<button type="button" class="btn-admin btn-admin-outline" style="padding:0.35rem 0.65rem; color:#f59e0b; border-color:rgba(245,158,11,0.4); margin-left:4px;" onclick="updateCommentStatus(${commentId}, 'REJECTED')">REJECT</button> `;
                            }
                            btns += `<button type="button" class="btn-admin btn-admin-danger" style="padding:0.35rem 0.65rem; margin-left:4px;" onclick="deleteComment(${commentId})">DELETE</button>`;
                            actionCell.innerHTML = btns;
                        }
                    }
                    recalculateCommentStats();
                    if (typeof renderCommentsPagination === 'function') renderCommentsPagination();
                    showToast(`Comment #${commentId} status updated to ${newStatus}.`, 'success');
                } else {
                    showToast('Error updating comment status: ' + (data.error || 'Unknown error'), 'error');
                }
            } catch(err) {
                showToast('Network error while updating comment status: ' + err.message, 'error');
            }
        }

        async function deleteComment(commentId) {
            const confirmed = await showConfirmModal({
                title: 'DELETE COMMENT',
                message: 'Permanently delete this comment?',
                confirmText: 'DELETE COMMENT',
                note: 'WARNING: This comment will be permanently removed from the article.'
            });
            if (!confirmed) {
                return;
            }

            try {
                const res = await fetch(`/api/admin/comments/${commentId}`, {
                    method: 'DELETE'
                });
                const data = await res.json();
                if (data.ok || data.success) {
                    const row = document.getElementById('comment-row-' + commentId);
                    if (row) row.remove();
                    recalculateCommentStats();
                    if (typeof renderCommentsPagination === 'function') renderCommentsPagination();
                    showToast(`Comment #${commentId} permanently deleted.`, 'info');
                } else {
                    showToast('Error deleting comment: ' + (data.error || 'Unknown error'), 'error');
                }
            } catch(err) {
                showToast('Network error while deleting comment: ' + err.message, 'error');
            }
        }

        // ==========================================
        // ARTICLE COMMENTS PAGINATION & SEARCH SUITE
        // ==========================================
        let commentsCurrentPage = 1;
        let currentCommentsStatusFilter = 'ALL';
        const COMMENTS_PAGE_SIZE = 20;

        function filterCommentsByStatus(status, btn) {
            document.querySelectorAll('.comment-filter-btn').forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');
            currentCommentsStatusFilter = status || 'ALL';
            commentsCurrentPage = 1;
            renderCommentsPagination();
        }

        function goToCommentsPrevPage() {
            if (commentsCurrentPage > 1) {
                commentsCurrentPage--;
                renderCommentsPagination();
                const wrap = document.querySelector('#mod-comments .admin-table-wrap');
                if (wrap) wrap.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        }

        function goToCommentsNextPage() {
            const matchingRows = getMatchingCommentsRows();
            const totalPages = Math.max(1, Math.ceil(matchingRows.length / COMMENTS_PAGE_SIZE));
            if (commentsCurrentPage < totalPages) {
                commentsCurrentPage++;
                renderCommentsPagination();
                const wrap = document.querySelector('#mod-comments .admin-table-wrap');
                if (wrap) wrap.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        }

        function getMatchingCommentsRows() {
            const searchInput = document.getElementById('comments-search-input');
            const query = (searchInput ? searchInput.value : '').toLowerCase().trim();
            const rows = document.querySelectorAll('#mod-comments table tbody tr.comment-row');
            const matching = [];

            rows.forEach(row => {
                const searchData = (row.getAttribute('data-search') || row.textContent || '').toLowerCase();
                const status = (row.getAttribute('data-status') || '').toUpperCase();

                const matchesQuery = !query || searchData.includes(query);
                const matchesFilter = (currentCommentsStatusFilter === 'ALL' || status === currentCommentsStatusFilter);

                if (matchesQuery && matchesFilter) {
                    matching.push(row);
                }
            });
            return matching;
        }

        function renderCommentsPagination() {
            const allRows = document.querySelectorAll('#mod-comments table tbody tr.comment-row');
            const matchingRows = getMatchingCommentsRows();
            const total = matchingRows.length;
            const totalPages = Math.max(1, Math.ceil(total / COMMENTS_PAGE_SIZE));

            if (commentsCurrentPage > totalPages) commentsCurrentPage = totalPages;
            if (commentsCurrentPage < 1) commentsCurrentPage = 1;

            const startIndex = (commentsCurrentPage - 1) * COMMENTS_PAGE_SIZE;
            const endIndex = Math.min(startIndex + COMMENTS_PAGE_SIZE, total);

            allRows.forEach(row => {
                row.style.display = 'none';
            });

            for (let i = startIndex; i < endIndex; i++) {
                matchingRows[i].style.display = '';
            }

            const countEl = document.getElementById('comments-search-count');
            if (countEl) {
                countEl.textContent = `SHOWING ${total} COMMENT${total === 1 ? '' : 'S'} (20 / PAGE)`;
            }

            const noResultsEl = document.getElementById('comments-no-results');
            if (noResultsEl) {
                noResultsEl.style.display = (total === 0) ? '' : 'none';
            }

            const pageRangeEl = document.getElementById('comments-page-range');
            if (pageRangeEl) {
                pageRangeEl.textContent = total === 0 ? '0–0' : `${startIndex + 1}–${endIndex}`;
            }
            const totalCountEl = document.getElementById('comments-total-count');
            if (totalCountEl) totalCountEl.textContent = total;

            const curPageEl = document.getElementById('comments-current-page');
            if (curPageEl) curPageEl.textContent = commentsCurrentPage;

            const totPagesEl = document.getElementById('comments-total-pages');
            if (totPagesEl) totPagesEl.textContent = totalPages;

            const prevBtn = document.getElementById('btn-comments-prev');
            if (prevBtn) {
                prevBtn.disabled = (commentsCurrentPage <= 1);
                prevBtn.style.opacity = (commentsCurrentPage <= 1) ? '0.4' : '1';
                prevBtn.style.cursor = (commentsCurrentPage <= 1) ? 'not-allowed' : 'pointer';
            }

            const nextBtn = document.getElementById('btn-comments-next');
            if (nextBtn) {
                nextBtn.disabled = (commentsCurrentPage >= totalPages);
                nextBtn.style.opacity = (commentsCurrentPage >= totalPages) ? '0.4' : '1';
                nextBtn.style.cursor = (commentsCurrentPage >= totalPages) ? 'not-allowed' : 'pointer';
            }
        }

        function onCommentSearchInput(val) {
            const clearBtn = document.getElementById('comments-search-clear-btn');
            if (clearBtn) {
                clearBtn.style.display = (val && val.trim().length > 0) ? 'inline-block' : 'none';
            }
            commentsCurrentPage = 1;
            renderCommentsPagination();
        }

        function clearCommentSearch() {
            const input = document.getElementById('comments-search-input');
            const clearBtn = document.getElementById('comments-search-clear-btn');
            if (input) {
                input.value = '';
                input.focus();
            }
            if (clearBtn) clearBtn.style.display = 'none';
            commentsCurrentPage = 1;
            renderCommentsPagination();
        }

        document.addEventListener('DOMContentLoaded', () => {
            renderCommentsPagination();
        });
