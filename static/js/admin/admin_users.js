        function openUserModal(u) {
            document.getElementById('user-modal-title').textContent = 'EDIT ACCESS: ' + u.username;
            document.getElementById('user-id').value = u.id;
            document.getElementById('user-username').value = u.username + (u.telegram_handle ? ' (' + u.telegram_handle + ')' : '');
            const isMasterAdmin = (u.id === 1);
            document.getElementById('user-role-display').value = isMasterAdmin ? 'IN-BUILT MASTER ADMIN (SYSTEM OPERATOR)' : 'CUSTOMER (VERIFIED CLIENT VAULT)';
            document.getElementById('user-role').value = isMasterAdmin ? 'ADMIN' : 'CUSTOMER';
            document.getElementById('user-active').value = u.is_active ? '1' : '0';
            document.getElementById('user-active').disabled = isMasterAdmin;
            document.getElementById('user-new-password').value = '';
            document.getElementById('modal-user').classList.add('is-open');
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
                location.reload();
            } else {
                alert(data.error || 'User update error');
            }
        }

        async function deleteUser(id, username) {
            if (!confirm('Permanently delete operator account: ' + username + '?')) return;
            const res = await fetch('/api/admin/users/' + id, { method: 'DELETE' });
            const data = await res.json();
            if (data.ok || data.success) location.reload();
            else alert(data.error || 'Delete error');
        }

        function openPasswordResetModal(userId, username) {
            document.getElementById('pwd-reset-user-id').value = userId;
            document.getElementById('pwd-reset-username').value = username;
            document.getElementById('pwd-reset-input').value = '';
            document.getElementById('modal-password-reset').classList.add('is-open');
        }

        async function submitPasswordReset(e) {
            e.preventDefault();
            const userId = document.getElementById('pwd-reset-user-id').value;
            const newPassword = document.getElementById('pwd-reset-input').value.trim();
            if (!newPassword || newPassword.length < 6) {
                alert('Password must be at least 6 characters.');
                return;
            }
            const res = await fetch('/api/admin/users/' + userId + '/password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: newPassword })
            });
            const data = await res.json();
            if (data.ok) {
                alert('Password updated successfully for operator #' + userId);
                closeModal('modal-password-reset');
            } else {
                alert(data.error || 'Password update failed.');
            }
        }

        async function toggleUserBan(userId, username, shouldBan) {
            const verb = shouldBan ? 'BAN & BLACKLIST hardware/network' : 'UNBAN & RESTORE access for';
            if (!confirm(`Are you sure you want to ${verb} ${username}?`)) return;
            const res = await fetch('/api/admin/users/' + userId + '/ban', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ban: shouldBan, reason: 'Administrative ban from control center' })
            });
            const data = await res.json();
            if (data.ok) {
                location.reload();
            } else {
                alert(data.error || 'Ban action failed.');
            }
        }

        async function toggleUserRole(userId, newRole) {
            const roleName = newRole === 'MODERATOR' ? 'STAFF MODERATOR' : 'CUSTOMER';
            if (!confirm(`Change role of user #${userId} to ${roleName}?`)) return;
            const res = await fetch('/api/admin/users/' + userId + '/role', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ role: newRole })
            });
            const data = await res.json();
            if (data.ok) {
                location.reload();
            } else {
                alert(data.error || 'Role change failed.');
            }
        }

        async function unbanIdentifier(banId) {
            if (!confirm('Remove this hardware/IP identifier from blacklist?')) return;
            const res = await fetch('/api/admin/unban-identifier', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: banId })
            });
            const data = await res.json();
            if (data.ok) {
                location.reload();
            } else {
                alert(data.error || 'Unban failed.');
            }
        }

        // ==========================================
        // SETTINGS SAVE
        // ==========================================
