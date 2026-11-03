        async function updateCommentStatus(commentId, newStatus) {
            try {
                const res = await fetch(`/api/admin/comments/${commentId}/status`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ status: newStatus })
                });
                const data = await res.json();
                if (data.ok || data.success) {
                    try { 
                        sessionStorage.setItem('activeAdminFeature', 'journal'); 
                        sessionStorage.setItem('activeSubtab_journal', 'comments'); 
                    } catch(err) {}
                    window.location.reload();
                } else {
                    alert('Error updating comment status: ' + (data.error || 'Unknown error'));
                }
            } catch(err) {
                alert('Network error while updating comment status: ' + err.message);
            }
        }

        async function deleteComment(commentId) {
            if (!confirm('Permanently delete this verification log entry from the database? This cannot be undone.')) {
                return;
            }

            try {
                const res = await fetch(`/api/admin/comments/${commentId}`, {
                    method: 'DELETE'
                });
                const data = await res.json();
                if (data.ok || data.success) {
                    try { 
                        sessionStorage.setItem('activeAdminFeature', 'journal'); 
                        sessionStorage.setItem('activeSubtab_journal', 'comments'); 
                    } catch(err) {}
                    window.location.reload();
                } else {
                    alert('Error deleting comment: ' + (data.error || 'Unknown error'));
                }
            } catch(err) {
                alert('Network error while deleting comment: ' + err.message);
            }
        }

        // ==========================================
