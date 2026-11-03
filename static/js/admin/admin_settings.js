        async function saveSettings(e) {
            e.preventDefault();
            const form = document.getElementById('settings-form');
            const formData = new FormData(form);
            const payload = {};
            formData.forEach((val, key) => { payload[key] = val; });

            const res = await fetch('/api/admin/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (data.ok || data.success) {
                alert('System configuration updated.');
                location.reload();
            } else {
                alert(data.error || 'Settings error');
            }
        }

        // ==========================================
        // VISUAL THEMES STUDIO LOGIC & PREVIEW SYNC
        // ==========================================
        window.THEME_CURRENT_PAGE = 'home';
        window.THEME_CURRENT_URL = '/';
        window.ORIGINAL_THEME_SETTINGS = window.ORIGINAL_THEME_SETTINGS || {};
        const previewIframe = document.getElementById('theme-preview-iframe');

