        function openUserModal(u) {
            document.getElementById('user-modal-title').textContent = 'EDIT USER: ' + u.username;
            document.getElementById('user-id').value = u.id;
            document.getElementById('user-username').value = u.username + (u.telegram_handle ? ' (' + u.telegram_handle + ')' : '');
            const isMasterAdmin = (u.id === 1);
            document.getElementById('user-role-display').value = isMasterAdmin ? 'ADMIN' : (u.role || 'CUSTOMER');
            document.getElementById('user-role').value = isMasterAdmin ? 'ADMIN' : (u.role || 'CUSTOMER');
            document.getElementById('user-active').value = u.is_active ? '1' : '0';
            document.getElementById('user-active').disabled = isMasterAdmin;
            document.getElementById('user-new-password').value = '';
            openModal('modal-user');
        }

        function recalculateUserCounts() {
            const rows = document.querySelectorAll('#mod-users table#users-table tbody tr.user-row');
            let total = rows.length;
            let admins = 0, mods = 0, custs = 0, banned = 0;
            rows.forEach(r => {
                const status = (r.getAttribute('data-status') || '').toUpperCase();
                const role = (r.getAttribute('data-role') || '').toUpperCase();
                if (status === 'BANNED') banned++;
                else if (role === 'ADMIN') admins++;
                else if (role === 'MODERATOR') mods++;
                else custs++;
            });
            const filterBtns = document.querySelectorAll('.user-filter-btn');
            filterBtns.forEach(btn => {
                const filter = btn.getAttribute('data-filter');
                const countSpan = btn.querySelector('.user-count');
                if (countSpan) {
                    if (filter === 'ALL') countSpan.textContent = total;
                    else if (filter === 'ADMIN') countSpan.textContent = admins;
                    else if (filter === 'MODERATOR') countSpan.textContent = mods;
                    else if (filter === 'CUSTOMER') countSpan.textContent = custs;
                    else if (filter === 'BANNED') countSpan.textContent = banned;
                }
            });
            executeUsersFilter();
        }

        async function submitUser(e) {
            e.preventDefault();
            const id = document.getElementById('user-id').value;
            const isActive = document.getElementById('user-active').value === '1';
            const newPassword = document.getElementById('user-new-password').value.trim();

            const payload = {
                is_active: isActive
            };
            if (newPassword) payload.new_password = newPassword;

            const res = await fetch('/api/admin/users/' + id, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (data.ok || data.success) {
                closeModal('modal-user');
                const row = document.getElementById('user-row-' + id) || document.querySelector('#users-table tr.user-row[data-user-id="' + id + '"]');
                if (row) {
                    row.setAttribute('data-status', isActive ? 'ACTIVE' : 'BANNED');
                    if (row.cells && row.cells.length > 5) {
                        row.cells[5].innerHTML = isActive
                            ? `<span style="color:var(--admin-accent-green); font-weight:700; font-size:11px; display:inline-flex; align-items:center; gap:5px;"><span style="display:inline-block; width:6px; height:6px; background:#10b981; border-radius:50%; box-shadow:0 0 6px rgba(16,185,129,0.5);"></span>ACTIVE</span>`
                            : `<span class="badge-tag" style="background:rgba(239,68,68,0.18); color:#ef4444; border:1px solid rgba(239,68,68,0.4); font-weight:700; font-size:10px;">BANNED</span>`;
                    }
                    const banBtn = row.querySelector('button[onclick*="toggleUserBan"]');
                    const username = row.querySelector('strong') ? row.querySelector('strong').textContent.trim() : '';
                    if (banBtn) {
                        if (isActive) {
                            banBtn.className = 'btn-admin btn-admin-danger';
                            banBtn.style.background = '';
                            banBtn.style.color = '';
                            banBtn.textContent = 'BAN';
                            banBtn.title = 'Ban user account, device HWID, and IP';
                            banBtn.onclick = () => toggleUserBan(id, username, true);
                        } else {
                            banBtn.className = 'btn-admin';
                            banBtn.style.background = '#10b981';
                            banBtn.style.color = '#000';
                            banBtn.textContent = 'UNBAN';
                            banBtn.title = 'Unban account and restore clearance';
                            banBtn.onclick = () => toggleUserBan(id, username, false);
                        }
                    }
                    let s = row.getAttribute('data-search') || '';
                    s = s.replace(/ACTIVE|BANNED/g, isActive ? 'ACTIVE' : 'BANNED');
                    row.setAttribute('data-search', s);
                }
                recalculateUserCounts();
                showToast(`User #${id} updated successfully.`, 'success');
            } else {
                showToast(data.error || 'User update error', 'error');
            }
        }

        async function deleteUser(id, username) {
            const confirmed = await showConfirmModal({
                title: 'DELETE USER',
                message: `Permanently delete user account "${username}"?`,
                confirmText: 'DELETE USER',
                note: 'WARNING: User account and associated credentials will be permanently removed.'
            });
            if (!confirmed) return;
            const res = await fetch('/api/admin/users/' + id, { method: 'DELETE' });
            const data = await res.json();
            if (data.ok || data.success) {
                const row = document.getElementById('user-row-' + id) || document.querySelector('#users-table tr.user-row[data-user-id="' + id + '"]');
                if (row) row.remove();
                recalculateUserCounts();
                showToast(`User "${username}" permanently deleted.`, 'info');
            } else {
                showToast(data.error || 'Delete error', 'error');
            }
        }

        function openPasswordResetModal(userId, username) {
            document.getElementById('pwd-reset-user-id').value = userId;
            document.getElementById('pwd-reset-username').value = username;
            document.getElementById('pwd-reset-input').value = '';
            openModal('modal-password-reset');
        }

        async function submitPasswordReset(e) {
            e.preventDefault();
            const userId = document.getElementById('pwd-reset-user-id').value;
            const newPassword = document.getElementById('pwd-reset-input').value.trim();
            if (!newPassword || newPassword.length < 6) {
                showToast('Password must be at least 6 characters.', 'error');
                return;
            }
            const res = await fetch('/api/admin/users/' + userId + '/password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: newPassword })
            });
            const data = await res.json();
            if (data.ok) {
                showToast('Password updated successfully for operator #' + userId, 'success');
                closeModal('modal-password-reset');
            } else {
                showToast(data.error || 'Password update failed.', 'error');
            }
        }

        async function toggleUserBan(userId, username, shouldBan) {
            const verb = shouldBan ? 'ban' : 'unban';
            const confirmed = await showConfirmModal({
                title: shouldBan ? 'BAN USER ACCOUNT' : 'UNBAN USER ACCOUNT',
                message: `Are you sure you want to ${verb} "${username}"?`,
                confirmText: shouldBan ? 'BAN USER' : 'UNBAN USER',
                danger: shouldBan,
                note: shouldBan ? 'The user account, device ID, and IP address will be blocked from accessing the store.' : 'The user account will regain access to the store.'
            });
            if (!confirmed) return;
            const res = await fetch('/api/admin/users/' + userId + '/ban', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ban: shouldBan, reason: 'Administrative ban from control center' })
            });
            const data = await res.json();
            if (data.ok) {
                const row = document.getElementById('user-row-' + userId) || document.querySelector('#users-table tr.user-row[data-user-id="' + userId + '"]');
                if (row) {
                    row.setAttribute('data-status', shouldBan ? 'BANNED' : 'ACTIVE');
                    if (row.cells && row.cells.length > 5) {
                        row.cells[5].innerHTML = shouldBan
                            ? `<span class="badge-tag" style="background:rgba(239,68,68,0.18); color:#ef4444; border:1px solid rgba(239,68,68,0.4); font-weight:700; font-size:10px;">BANNED</span>`
                            : `<span style="color:var(--admin-accent-green); font-weight:700; font-size:11px; display:inline-flex; align-items:center; gap:5px;"><span style="display:inline-block; width:6px; height:6px; background:#10b981; border-radius:50%; box-shadow:0 0 6px rgba(16,185,129,0.5);"></span>ACTIVE</span>`;
                    }
                    const banBtn = row.querySelector('button[onclick*="toggleUserBan"]');
                    if (banBtn) {
                        if (shouldBan) {
                            banBtn.className = 'btn-admin';
                            banBtn.style.background = '#10b981';
                            banBtn.style.color = '#000';
                            banBtn.textContent = 'UNBAN';
                            banBtn.title = 'Unban account and restore clearance';
                            banBtn.onclick = () => toggleUserBan(userId, username, false);
                        } else {
                            banBtn.className = 'btn-admin btn-admin-danger';
                            banBtn.style.background = '';
                            banBtn.style.color = '';
                            banBtn.textContent = 'BAN';
                            banBtn.title = 'Ban user account, device HWID, and IP';
                            banBtn.onclick = () => toggleUserBan(userId, username, true);
                        }
                    }
                    let s = row.getAttribute('data-search') || '';
                    s = s.replace(/ACTIVE|BANNED/g, shouldBan ? 'BANNED' : 'ACTIVE');
                    row.setAttribute('data-search', s);
                }
                recalculateUserCounts();
                showToast(`Operator "${username}" ${shouldBan ? 'banned' : 'unbanned'} successfully.`, shouldBan ? 'error' : 'success');
            } else {
                showToast(data.error || 'Ban action failed.', 'error');
            }
        }

        async function toggleUserRole(userId, newRole) {
            const roleName = newRole === 'MODERATOR' ? 'STAFF MODERATOR' : 'CUSTOMER';
            const confirmed = await showConfirmModal({
                title: 'CHANGE ROLE PRIVILEGES',
                message: `Change permission role of user #${userId} to ${roleName}?`,
                confirmText: 'UPDATE ROLE',
                danger: false,
                note: 'User session will be updated with the newly assigned security role permissions.'
            });
            if (!confirmed) return;
            const res = await fetch('/api/admin/users/' + userId + '/role', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ role: newRole })
            });
            const data = await res.json();
            if (data.ok) {
                const row = document.getElementById('user-row-' + userId) || document.querySelector('#users-table tr.user-row[data-user-id="' + userId + '"]');
                if (row) {
                    row.setAttribute('data-role', newRole);
                    if (row.cells && row.cells.length > 3) {
                        if (newRole === 'MODERATOR') {
                            row.cells[3].innerHTML = `<span class="status-pill completed" style="background:#10b981; color:#000; font-weight:800; font-size:10px; padding:2px 7px;">MODERATOR</span>`;
                        } else {
                            row.cells[3].innerHTML = `<span class="badge-tag" style="background:rgba(255,255,255,0.06); color:#a1a1aa; font-size:10px; padding:2px 7px;">CUSTOMER</span>`;
                        }
                    }
                    const roleBtn = row.querySelector('button[onclick*="toggleUserRole"]');
                    if (roleBtn) {
                        if (newRole === 'MODERATOR') {
                            roleBtn.textContent = '- MOD';
                            roleBtn.title = 'Revoke moderator clearance';
                            roleBtn.style.borderColor = 'rgba(245,158,11,0.5)';
                            roleBtn.style.color = '#f59e0b';
                            roleBtn.onclick = () => toggleUserRole(userId, 'CUSTOMER');
                        } else {
                            roleBtn.textContent = '+ MOD';
                            roleBtn.title = 'Promote to Staff Moderator';
                            roleBtn.style.borderColor = 'rgba(16,185,129,0.5)';
                            roleBtn.style.color = '#10b981';
                            roleBtn.onclick = () => toggleUserRole(userId, 'MODERATOR');
                        }
                    }
                    let s = row.getAttribute('data-search') || '';
                    s = s.replace(/CUSTOMER|MODERATOR/g, newRole);
                    row.setAttribute('data-search', s);
                }
                recalculateUserCounts();
                showToast(`User #${userId} clearance updated to ${newRole}.`, 'success');
            } else {
                showToast(data.error || 'Role change failed.', 'error');
            }
        }

        async function unbanIdentifier(banId) {
            const confirmed = await showConfirmModal({
                title: 'UNBAN DEVICE / IP',
                message: 'Remove this device / IP address from the blocklist?',
                confirmText: 'UNBAN',
                danger: false,
                note: 'This device or IP address will be able to access the store again.'
            });
            if (!confirmed) return;
            const res = await fetch('/api/admin/unban-identifier', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: banId })
            });
            const data = await res.json();
            if (data.ok) {
                const row = document.getElementById('ban-row-' + banId) || document.querySelector('button[onclick*="unbanIdentifier(' + banId + ')"]')?.closest('tr');
                if (row) row.remove();
                showToast(`Perimeter block #${banId} revoked successfully.`, 'success');
            } else {
                showToast(data.error || 'Unban failed.', 'error');
            }
        }

        // ==========================================
        // OPERATOR REGISTRY SEARCH & FILTER SUITE
        // ==========================================
        let currentUsersRoleFilter = 'ALL';
        let usersCurrentPage = 1;
        const USERS_PAGE_SIZE = 30;

        function goToUsersPrevPage() {
            if (usersCurrentPage > 1) {
                usersCurrentPage--;
                renderUsersPagination();
                const wrap = document.querySelector('#mod-users .admin-table-wrap');
                if (wrap) wrap.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        }

        function goToUsersNextPage() {
            const matchingRows = getMatchingUsersRows();
            const totalPages = Math.max(1, Math.ceil(matchingRows.length / USERS_PAGE_SIZE));
            if (usersCurrentPage < totalPages) {
                usersCurrentPage++;
                renderUsersPagination();
                const wrap = document.querySelector('#mod-users .admin-table-wrap');
                if (wrap) wrap.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
        }

        function getMatchingUsersRows() {
            const searchInput = document.getElementById('users-search-input');
            const query = (searchInput ? searchInput.value : '').toLowerCase().trim();
            const rows = document.querySelectorAll('#mod-users table#users-table tbody tr.user-row');
            const matching = [];

            rows.forEach(row => {
                const searchData = (row.getAttribute('data-search') || '').toLowerCase();
                const userRole = (row.getAttribute('data-role') || '').toUpperCase();
                const userStatus = (row.getAttribute('data-status') || '').toUpperCase();

                const matchesQuery = !query || searchData.includes(query);
                let matchesRole = true;

                if (currentUsersRoleFilter === 'BANNED') {
                    matchesRole = (userStatus === 'BANNED');
                } else if (currentUsersRoleFilter !== 'ALL') {
                    matchesRole = (userRole === currentUsersRoleFilter);
                }

                if (matchesQuery && matchesRole) {
                    matching.push(row);
                }
            });
            return matching;
        }

        function renderUsersPagination() {
            const allRows = document.querySelectorAll('#mod-users table#users-table tbody tr.user-row');
            const matchingRows = getMatchingUsersRows();
            const total = matchingRows.length;
            const totalPages = Math.max(1, Math.ceil(total / USERS_PAGE_SIZE));

            if (usersCurrentPage > totalPages) usersCurrentPage = totalPages;
            if (usersCurrentPage < 1) usersCurrentPage = 1;

            const startIndex = (usersCurrentPage - 1) * USERS_PAGE_SIZE;
            const endIndex = Math.min(startIndex + USERS_PAGE_SIZE, total);

            allRows.forEach(row => {
                row.style.display = 'none';
            });

            for (let i = startIndex; i < endIndex; i++) {
                matchingRows[i].style.display = '';
            }

            const countEl = document.getElementById('users-search-count');
            if (countEl) {
                countEl.textContent = `SHOWING ${total} OPERATOR${total === 1 ? '' : 'S'} (30 / PAGE)`;
            }

            const noResultsEl = document.getElementById('users-no-results');
            if (noResultsEl) {
                noResultsEl.style.display = (total === 0) ? '' : 'none';
            }

            const pageRangeEl = document.getElementById('users-page-range');
            if (pageRangeEl) {
                pageRangeEl.textContent = total === 0 ? '0–0' : `${startIndex + 1}–${endIndex}`;
            }
            const totalCountEl = document.getElementById('users-total-count');
            if (totalCountEl) totalCountEl.textContent = total;

            const curPageEl = document.getElementById('users-current-page');
            if (curPageEl) curPageEl.textContent = usersCurrentPage;

            const totPagesEl = document.getElementById('users-total-pages');
            if (totPagesEl) totPagesEl.textContent = totalPages;

            const prevBtn = document.getElementById('btn-users-prev');
            if (prevBtn) {
                prevBtn.disabled = (usersCurrentPage <= 1);
                prevBtn.style.opacity = (usersCurrentPage <= 1) ? '0.4' : '1';
                prevBtn.style.cursor = (usersCurrentPage <= 1) ? 'not-allowed' : 'pointer';
            }

            const nextBtn = document.getElementById('btn-users-next');
            if (nextBtn) {
                nextBtn.disabled = (usersCurrentPage >= totalPages);
                nextBtn.style.opacity = (usersCurrentPage >= totalPages) ? '0.4' : '1';
                nextBtn.style.cursor = (usersCurrentPage >= totalPages) ? 'not-allowed' : 'pointer';
            }
        }

        function filterUsersByRole(role, btn) {
            document.querySelectorAll('.user-filter-btn').forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');
            currentUsersRoleFilter = role || 'ALL';
            executeUsersFilter();
        }

        function onUserSearchInput(val) {
            const clearBtn = document.getElementById('users-search-clear-btn');
            if (clearBtn) {
                clearBtn.style.display = (val && val.trim().length > 0) ? 'inline-block' : 'none';
            }
            executeUsersFilter();
        }

        function clearUsersSearch() {
            const input = document.getElementById('users-search-input');
            const clearBtn = document.getElementById('users-search-clear-btn');
            if (input) {
                input.value = '';
                input.focus();
            }
            if (clearBtn) clearBtn.style.display = 'none';
            executeUsersFilter();
        }

        function executeUsersFilter() {
            usersCurrentPage = 1;
            renderUsersPagination();
        }

        // Backward compatibility
        function filterUsersList() {
            executeUsersFilter();
        }

        // Initialize users pagination
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', renderUsersPagination);
        } else {
            renderUsersPagination();
        }

        // ==========================================
        // SETTINGS SAVE
        // ==========================================
