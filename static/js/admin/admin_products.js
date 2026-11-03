        function updatePseFaqCount() {
            const countEl = document.getElementById('pse-faq-count');
            const rows = document.querySelectorAll('#pse-faq-container .pse-faq-row');
            if (countEl) countEl.textContent = rows.length;
            rows.forEach((row, idx) => {
                const label = row.querySelector('.pse-faq-index-label');
                if (label) label.textContent = `FAQ ACCORDION #${idx + 1}`;
            });
        }

        function addProductStudioFaqRow(q = '', a = '') {
            const container = document.getElementById('pse-faq-container');
            if (!container) return;
            const div = document.createElement('div');
            div.className = 'pse-faq-row';
            div.style.cssText = 'background:#141618; border:1px solid var(--admin-border); border-radius:4px; padding:1.25rem;';
            div.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem; border-bottom:1px solid rgba(255,255,255,0.06); padding-bottom:0.5rem;">
                    <span class="pse-faq-index-label" style="font-family:var(--admin-font-mono); font-size:11px; font-weight:700; color:#10b981;">FAQ ACCORDION</span>
                    <div style="display:flex; gap:0.35rem;">
                        <button type="button" onclick="moveProductStudioFaqRow(this, -1)" class="btn-admin btn-admin-outline" style="padding:0.2rem 0.5rem; font-size:10px;" title="Move Up">↑</button>
                        <button type="button" onclick="moveProductStudioFaqRow(this, 1)" class="btn-admin btn-admin-outline" style="padding:0.2rem 0.5rem; font-size:10px;" title="Move Down">↓</button>
                        <button type="button" onclick="removeProductStudioFaqRow(this)" class="btn-admin btn-admin-danger" style="padding:0.2rem 0.5rem; font-size:10px;" title="Delete">REMOVE</button>
                    </div>
                </div>
                <div class="form-group" style="margin-bottom:0.75rem;">
                    <label class="form-label" style="font-size:11px;">QUESTION / ACCORDION TITLE</label>
                    <input type="text" class="form-input pse-faq-q" placeholder="e.g. Can I run this suite in an airgapped lab?" style="font-weight:600;">
                </div>
                <div class="form-group">
                    <label class="form-label" style="font-size:11px;">ANSWER / ACCORDION CONTENT</label>
                    <textarea rows="3" class="form-textarea pse-faq-a" placeholder="Enter detailed operational or licensing answer for operators..." style="line-height:1.5;"></textarea>
                </div>
            `;
            div.querySelector('.pse-faq-q').value = q || '';
            div.querySelector('.pse-faq-a').value = a || '';
            container.appendChild(div);
            updatePseFaqCount();
        }

        function removeProductStudioFaqRow(btn) {
            const row = btn.closest('.pse-faq-row');
            if (row) {
                row.remove();
                updatePseFaqCount();
            }
        }

        function moveProductStudioFaqRow(btn, direction) {
            const row = btn.closest('.pse-faq-row');
            if (!row) return;
            const container = document.getElementById('pse-faq-container');
            if (direction === -1 && row.previousElementSibling) {
                container.insertBefore(row, row.previousElementSibling);
            } else if (direction === 1 && row.nextElementSibling) {
                container.insertBefore(row.nextElementSibling, row);
            }
            updatePseFaqCount();
        }

        function populateProductStudioFaqs(faqs) {
            const container = document.getElementById('pse-faq-container');
            if (!container) return;
            container.innerHTML = '';
            if (Array.isArray(faqs) && faqs.length > 0) {
                faqs.forEach(item => {
                    addProductStudioFaqRow(item.q || '', item.a || '');
                });
            } else {
                addProductStudioFaqRow('', '');
            }
            updatePseFaqCount();
        }

        // ==========================================
        // PRODUCT STUDIO SPECIFICATIONS (LINE BY LINE)
        // ==========================================
        function updatePseSpecsCount() {
            const countEl = document.getElementById('pse-specs-count');
            const rows = document.querySelectorAll('#pse-specs-container .pse-spec-row');
            if (countEl) countEl.textContent = rows.length;
            rows.forEach((row, idx) => {
                const bullet = row.querySelector('.pse-spec-bullet');
                if (bullet) bullet.textContent = `#${idx + 1}`;
            });
        }

        function addPseSpecRow(text = '') {
            const container = document.getElementById('pse-specs-container');
            if (!container) return;
            const div = document.createElement('div');
            div.className = 'pse-spec-row';
            div.style.cssText = 'display:flex; align-items:center; gap:0.5rem; background:#141618; border:1px solid var(--admin-border); border-radius:4px; padding:0.5rem 0.75rem;';
            div.innerHTML = `
                <span class="pse-spec-bullet" style="color:#00e5ff; font-family:var(--admin-font-mono); font-size:11px; font-weight:700; width:28px;">#</span>
                <input type="text" class="form-input pse-spec-item-input" placeholder="e.g. Automated Active & Passive Web Vulnerability Scanner" style="flex:1; font-weight:600; font-size:12px;">
                <div style="display:flex; gap:0.25rem;">
                    <button type="button" onclick="movePseSpecRow(this, -1)" class="btn-admin btn-admin-outline" style="padding:0.2rem 0.5rem; font-size:10px;" title="Move Up">↑</button>
                    <button type="button" onclick="movePseSpecRow(this, 1)" class="btn-admin btn-admin-outline" style="padding:0.2rem 0.5rem; font-size:10px;" title="Move Down">↓</button>
                    <button type="button" onclick="removePseSpecRow(this)" class="btn-admin btn-admin-danger" style="padding:0.2rem 0.5rem; font-size:10px;" title="Remove">REMOVE</button>
                </div>
            `;
            div.querySelector('.pse-spec-item-input').value = text || '';
            container.appendChild(div);
            updatePseSpecsCount();
        }

        function removePseSpecRow(btn) {
            const row = btn.closest('.pse-spec-row');
            if (row) {
                row.remove();
                updatePseSpecsCount();
            }
        }

        function movePseSpecRow(btn, direction) {
            const row = btn.closest('.pse-spec-row');
            if (!row) return;
            const container = document.getElementById('pse-specs-container');
            if (direction === -1 && row.previousElementSibling) {
                container.insertBefore(row, row.previousElementSibling);
            } else if (direction === 1 && row.nextElementSibling) {
                container.insertBefore(row.nextElementSibling, row);
            }
            updatePseSpecsCount();
        }

        function populatePseSpecs(specsList) {
            const container = document.getElementById('pse-specs-container');
            if (!container) return;
            container.innerHTML = '';
            if (Array.isArray(specsList) && specsList.length > 0) {
                specsList.forEach(item => addPseSpecRow(item));
            } else if (typeof specsList === 'string' && specsList.trim()) {
                specsList.split('\n').filter(s => s.trim()).forEach(item => addPseSpecRow(item));
            } else {
                addPseSpecRow('');
            }
            updatePseSpecsCount();
        }

        // ==========================================
        // PRODUCT STUDIO FULL MARKDOWN MANUAL
        // ==========================================
        function renderProductMarkdownPreviewLive() {
            const text = (document.getElementById('pse-description') ? document.getElementById('pse-description').value : '') || '';
            const preview = document.getElementById('pse-live-markdown-preview');
            if (!preview) return;

            if (!text.trim()) {
                preview.innerHTML = '<p style="color:var(--admin-muted); font-style:italic;">Type markdown content on the left to see instant live rendering here...</p>';
                return;
            }

            let rendered = '';
            if (typeof marked !== 'undefined' && typeof marked.parse === 'function') {
                try {
                    rendered = marked.parse(text, { gfm: true, breaks: true });
                } catch(e) {
                    rendered = text.replace(/\n/g, '<br>');
                }
            } else {
                rendered = text.replace(/\n/g, '<br>');
            }

            // GitHub alert callout styling
            rendered = rendered.replace(/<blockquote>\s*<p>\s*\[!WARNING\](?:\s*<br\s*\/?>)?\s*([\s\S]*?)<\/p>\s*<\/blockquote>/gi,
                '<div style="background:rgba(245,158,11,0.1); border-left:4px solid #f59e0b; padding:10px 14px; margin:14px 0; border-radius:2px;"><strong style="color:#f59e0b; display:flex; align-items:center; gap:6px; margin-bottom:4px; font-size:11px; font-family:var(--admin-font-mono);"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg> WARNING ADVISORY</strong><div style="font-size:12.5px;">$1</div></div>'
            );
            rendered = rendered.replace(/<blockquote>\s*<p>\s*\[!NOTE\](?:\s*<br\s*\/?>)?\s*([\s\S]*?)<\/p>\s*<\/blockquote>/gi,
                '<div style="background:rgba(0,229,255,0.08); border-left:4px solid #00e5ff; padding:10px 14px; margin:14px 0; border-radius:2px;"><strong style="color:#00e5ff; display:flex; align-items:center; gap:6px; margin-bottom:4px; font-size:11px; font-family:var(--admin-font-mono);"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg> RESEARCH NOTE</strong><div style="font-size:12.5px;">$1</div></div>'
            );
            rendered = rendered.replace(/<blockquote>\s*<p>\s*\[!TIP\](?:\s*<br\s*\/?>)?\s*([\s\S]*?)<\/p>\s*<\/blockquote>/gi,
                '<div style="background:rgba(16,185,129,0.1); border-left:4px solid #10b981; padding:10px 14px; margin:14px 0; border-radius:2px;"><strong style="color:#10b981; display:flex; align-items:center; gap:6px; margin-bottom:4px; font-size:11px; font-family:var(--admin-font-mono);"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg> DEFENSIVE TIP</strong><div style="font-size:12.5px;">$1</div></div>'
            );
            rendered = rendered.replace(/<blockquote>\s*<p>\s*\[!CAUTION\](?:\s*<br\s*\/?>)?\s*([\s\S]*?)<\/p>\s*<\/blockquote>/gi,
                '<div style="background:rgba(239,68,68,0.12); border-left:4px solid #ef4444; padding:10px 14px; margin:14px 0; border-radius:2px;"><strong style="color:#ef4444; display:flex; align-items:center; gap:6px; margin-bottom:4px; font-size:11px; font-family:var(--admin-font-mono);"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/></svg> CRITICAL ALERT</strong><div style="font-size:12.5px;">$1</div></div>'
            );

            preview.innerHTML = rendered;
        }

        function updateProductMarkdownStats() {
            const textarea = document.getElementById('pse-description');
            if (!textarea) return;
            const text = textarea.value;
            const words = text.trim() ? (text.trim().match(/\S+/g) || []).length : 0;
            const chars = text.length;
            const lines = text ? text.split('\n').length : 0;

            const wEl = document.getElementById('pse-md-stat-words');
            const cEl = document.getElementById('pse-md-stat-chars');
            const lEl = document.getElementById('pse-md-stat-lines');
            if (wEl) wEl.textContent = words;
            if (cEl) cEl.textContent = chars;
            if (lEl) lEl.textContent = lines;
        }

        function handleProductMarkdownEditorKeydown(e) {
            const textarea = e.target;
            if (e.key === 'Tab') {
                e.preventDefault();
                const start = textarea.selectionStart;
                const end = textarea.selectionEnd;
                textarea.value = textarea.value.substring(0, start) + '  ' + textarea.value.substring(end);
                textarea.selectionStart = textarea.selectionEnd = start + 2;
                renderProductMarkdownPreviewLive();
                updateProductMarkdownStats();
                return;
            }
            if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'b') {
                e.preventDefault();
                formatProductMarkdownSelection('bold');
            } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'i') {
                e.preventDefault();
                formatProductMarkdownSelection('italic');
            } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
                e.preventDefault();
                formatProductMarkdownSelection('link');
            }
        }

        function formatProductMarkdownSelection(type, extra) {
            const textarea = document.getElementById('pse-description');
            if (!textarea) return;
            textarea.focus();
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            const fullText = textarea.value;
            const selected = fullText.substring(start, end);

            let replacement = '';
            let selectRange = null;

            switch(type) {
                case 'bold':
                    replacement = selected ? `**${selected}**` : `**bold text**`;
                    selectRange = selected ? [start + 2, start + 2 + selected.length] : [start + 2, start + 11];
                    break;
                case 'italic':
                    replacement = selected ? `*${selected}*` : `*italic text*`;
                    selectRange = selected ? [start + 1, start + 1 + selected.length] : [start + 1, start + 12];
                    break;
                case 'strike':
                    replacement = selected ? `~~${selected}~~` : `~~strikethrough~~`;
                    selectRange = selected ? [start + 2, start + 2 + selected.length] : [start + 2, start + 15];
                    break;
                case 'code':
                    replacement = selected ? `\`${selected}\`` : `\`code\``;
                    selectRange = selected ? [start + 1, start + 1 + selected.length] : [start + 1, start + 5];
                    break;
                case 'codeblock':
                    replacement = selected ? `\`\`\`bash\n${selected}\n\`\`\`\n` : `\`\`\`bash\n# Terminal execution syntax\n$ ./deploy_tool --airgap --strict\n\`\`\`\n`;
                    selectRange = [start + 8, start + 8 + (selected ? selected.length : 45)];
                    break;
                case 'h1':
                    replacement = selected ? `# ${selected}\n` : `# Heading 1\n`;
                    break;
                case 'h2':
                    replacement = selected ? `## ${selected}\n` : `## Heading 2\n`;
                    break;
                case 'h3':
                    replacement = selected ? `### ${selected}\n` : `### 01 · System Architecture\n`;
                    break;
                case 'quote':
                    replacement = selected ? `> ${selected}\n` : `> Operational quote or security disclosure.\n`;
                    break;
                case 'ul':
                    replacement = selected ? selected.split('\n').map(l => `- ${l}`).join('\n') + '\n' : `- Feature Capability 1\n- Feature Capability 2\n- Feature Capability 3\n`;
                    break;
                case 'ol':
                    replacement = selected ? selected.split('\n').map((l, i) => `${i + 1}. ${l}`).join('\n') + '\n' : `1. Step One\n2. Step Two\n3. Step Three\n`;
                    break;
                case 'table':
                    replacement = `| Component | Specifications | Operational State |\n| :--- | :--- | :--- |\n| Core Runtime | x86_64 / ARM64 | Verified Ready |\n| Airgap Engine | Disconnected | 100% Offline |\n\n`;
                    break;
                case 'link':
                    replacement = selected ? `[${selected}](https://example.com)` : `[Link Text](https://example.com)`;
                    break;
                case 'hr':
                    replacement = `\n---\n\n`;
                    break;
                case 'alert-warning':
                    replacement = `> [!WARNING]\n> ${selected || 'This software is strictly intended for authorized auditing operations.'}\n\n`;
                    break;
                case 'alert-note':
                    replacement = `> [!NOTE]\n> ${selected || 'Requires zero recurring phone-home callbacks or SaaS telemetry check-ins.'}\n\n`;
                    break;
                case 'alert-tip':
                    replacement = `> [!TIP]\n> ${selected || 'Utilize standalone checksum manifests to verify binary integrity.'}\n\n`;
                    break;
                case 'alert-caution':
                    replacement = `> [!CAUTION]\n> ${selected || 'Exercise caution during high-concurrency automated thread execution.'}\n\n`;
                    break;
                default:
                    replacement = selected;
            }

            textarea.value = fullText.substring(0, start) + replacement + fullText.substring(end);
            if (selectRange) {
                textarea.selectionStart = selectRange[0];
                textarea.selectionEnd = selectRange[1];
            } else {
                textarea.selectionStart = textarea.selectionEnd = start + replacement.length;
            }
            renderProductMarkdownPreviewLive();
            updateProductMarkdownStats();
        }

        function loadProductMarkdownTemplate(tmplKey) {
            const textarea = document.getElementById('pse-description');
            if (!textarea) return;
            if (textarea.value.trim() && !confirm('Load template? This will replace your current manual draft.')) return;
            let tmpl = '';
            if (tmplKey === 'arch') {
                tmpl = `### 01 · SYSTEM ARCHITECTURE & SUBSYSTEMS\n\nComprehensive technical architecture overview engineered for security operators and automated pipeline integration.\n\n> [!NOTE]\n> Fully verified for offline airgap isolation with zero external phone-home telemetry.\n\n---\n\n### 02 · MODULE BREAKDOWN & WORKER THREADS\n\n| Subsystem | Capabilities | Throughput Execution |\n| :--- | :--- | :--- |\n| **Core Engine** | High-throughput multi-threaded pipeline | Unthrottled |\n| **Offline Manifest** | Cryptographic SHA-256 signature validation | Instant |\n\n---\n\n### 03 · RUNTIME VERIFICATION EXAMPLE\n\n\`\`\`bash\n# Verify release archive integrity\nsha256sum -c release_checksum.txt\n\`\`\``;
            } else if (tmplKey === 'api') {
                tmpl = `### 01 · REST API & AUTOMATION INTEGRATION\n\nAutomate security auditing routines through the headless CLI pipeline.\n\n\`\`\`bash\n# Dispatch headless audit scan\ncurl -X POST "http://127.0.0.1:1337/api/v1/scan" \\\n  -H "Authorization: Bearer $OPERATOR_KEY" \\\n  -d '{"target": "https://internal.staging.local"}'\n\`\`\`\n\n> [!TIP]\n> API endpoints can be configured to bind exclusively to localhost or internal loopback interfaces.`;
            } else if (tmplKey === 'airgap') {
                tmpl = `### 01 · AIRGAP DEPLOYMENT & DISCONNECTED OPERATIONS\n\n- **100% Offline Safe**: Operates in disconnected network enclaves without SaaS callbacks.\n- **Checksum Validation**: Validate binary signatures before loading onto airgapped jumpboxes.\n\n> [!WARNING]\n> Ensure staging storage media is scanned according to organizational physical media handling protocols.`;
            }
            textarea.value = tmpl;
            renderProductMarkdownPreviewLive();
            updateProductMarkdownStats();
            showThemeToast('LOADED PRODUCT MANUAL TEMPLATE');
        }

        function setProductMarkdownViewMode(mode) {
            const grid = document.getElementById('pse-md-grid');
            const editorCol = document.getElementById('pse-md-editor-col');
            const previewCol = document.getElementById('pse-md-preview-col');
            ['split', 'editor', 'preview'].forEach(m => {
                const b = document.getElementById(`btn-pse-md-mode-${m}`);
                if (b) b.classList.remove('active');
            });
            const activeBtn = document.getElementById(`btn-pse-md-mode-${mode}`);
            if (activeBtn) activeBtn.classList.add('active');

            if (mode === 'split') {
                grid.style.gridTemplateColumns = '1fr 1fr';
                editorCol.style.display = 'flex';
                previewCol.style.display = 'flex';
            } else if (mode === 'editor') {
                grid.style.gridTemplateColumns = '1fr';
                editorCol.style.display = 'flex';
                previewCol.style.display = 'none';
            } else if (mode === 'preview') {
                grid.style.gridTemplateColumns = '1fr';
                editorCol.style.display = 'none';
                previewCol.style.display = 'flex';
                renderProductMarkdownPreviewLive();
            }
        }

        function toggleProductMarkdownFullscreen() {
            const pane = document.getElementById('pse-tab-manual');
            const btn = document.getElementById('btn-pse-md-fullscreen');
            if (!pane) return;
            const isFull = pane.classList.toggle('pse-fullscreen-editor');
            if (isFull) {
                pane.style.cssText = 'position:fixed; inset:0; z-index:99999; background:#0c0d0e; padding:1.5rem; overflow-y:auto; display:flex; flex-direction:column;';
                if (btn) btn.textContent = 'EXIT FULLSCREEN';
                document.body.style.overflow = 'hidden';
            } else {
                pane.style.cssText = 'display:block;';
                if (btn) btn.textContent = 'FULLSCREEN';
                document.body.style.overflow = '';
            }
        }

        function copyProductRenderedHtml() {
            const preview = document.getElementById('pse-live-markdown-preview');
            if (!preview) return;
            navigator.clipboard.writeText(preview.innerHTML).then(() => {
                showThemeToast('RENDERED HTML COPIED TO CLIPBOARD');
            }).catch(() => {
                alert('Copied to clipboard.');
            });
        }

        function openProductStudio() {
            document.getElementById('pse-id').value = '';
            document.getElementById('pse-breadcrumb-title').textContent = 'NEW ARSENAL SYSTEM';
            document.getElementById('pse-heading-title').textContent = 'CREATE NEW ARSENAL SYSTEM';
            document.getElementById('pse-btn-view-live').style.display = 'none';

            // Reset fields
            document.getElementById('pse-sku').value = '';
            document.getElementById('pse-name').value = '';
            document.getElementById('pse-slug').value = '';
            document.getElementById('pse-category').value = 'Web & AppSec Licenses';
            document.getElementById('pse-type').value = 'LICENSE_KEY';
            document.getElementById('pse-price').value = '449';
            document.getElementById('pse-retail').value = '599';
            document.getElementById('pse-version').value = 'v2026.10.1';
            document.getElementById('pse-duration').value = '1-Year Enterprise Key';
            document.getElementById('pse-platform').value = 'Windows / Linux / macOS';
            document.getElementById('pse-badge').value = 'INSTANT DELIVERY';
            if (document.getElementById('pse-featured')) document.getElementById('pse-featured').checked = false;

            document.getElementById('pse-image').value = 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=1200&q=85';
            updateProductCoverPreview('https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=1200&q=85');

            document.getElementById('pse-sha256').value = '';
            document.getElementById('pse-download-url').value = '';
            document.getElementById('pse-desc').value = '';

            // Reset line-by-line specs
            populatePseSpecs([]);

            // Reset full markdown manual
            document.getElementById('pse-description').value = '';
            renderProductMarkdownPreviewLive();
            updateProductMarkdownStats();

            document.getElementById('pse-meta-title').value = '';
            document.getElementById('pse-meta-desc').value = '';
            document.getElementById('pse-meta-keywords').value = '';
            document.getElementById('pse-og-image').value = '';
            updateProductOgPreview('https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=1200&q=85');

            // In-article smart ad campaign
            document.getElementById('pse-ad-headline').value = '';
            document.getElementById('pse-ad-desc').value = '';
            document.getElementById('pse-ad-badge').value = '';
            document.getElementById('pse-ad-cta').value = '';
            document.getElementById('pse-ad-image').value = '';
            updateProductAdPreview();

            // Reset FAQs
            populateProductStudioFaqs([]);

            switchProductStudioTab('specs', document.querySelector('.pse-subnav-btn'));
            calcProductDiscount();
            updateProductPreview();
            updateProductSeoSimulator();

            switchAdminTab('product-editor', null);
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        function openProductStudioForId(id) {
            const el = document.getElementById('product-data-' + id);
            if (!el) {
                console.error('Product raw script not found for ID', id);
                return;
            }
            try {
                const p = JSON.parse(el.textContent);
                editProductStudio(p);
            } catch(err) {
                console.error('Failed to parse product data for ID', id, err);
            }
        }

        function editProductStudio(p) {
            document.getElementById('pse-id').value = p.id;
            document.getElementById('pse-breadcrumb-title').textContent = 'EDIT: ' + p.sku;
            document.getElementById('pse-heading-title').textContent = 'EDIT SYSTEM SPECIFICATIONS — ' + p.name;
            
            const liveBtn = document.getElementById('pse-btn-view-live');
            if (liveBtn) {
                liveBtn.href = '/product/' + (p.slug || p.sku);
                liveBtn.style.display = 'inline-flex';
            }

            document.getElementById('pse-sku').value = p.sku || '';
            document.getElementById('pse-name').value = p.name || '';
            document.getElementById('pse-slug').value = p.slug || '';
            document.getElementById('pse-category').value = p.category || 'Web & AppSec Licenses';
            document.getElementById('pse-type').value = p.product_type || 'LICENSE_KEY';
            document.getElementById('pse-price').value = p.price || 0;
            document.getElementById('pse-retail').value = p.retail_price || 0;
            document.getElementById('pse-version').value = p.version || '';
            document.getElementById('pse-duration').value = p.license_duration || '';
            document.getElementById('pse-platform').value = p.platform || '';
            document.getElementById('pse-badge').value = p.badge_text || 'INSTANT DELIVERY';
            if (document.getElementById('pse-featured')) document.getElementById('pse-featured').checked = !!p.featured;

            const coverUrl = p.image_url || 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=1200&q=85';
            document.getElementById('pse-image').value = coverUrl;
            updateProductCoverPreview(coverUrl);

            document.getElementById('pse-sha256').value = p.sha256_hash || '';
            document.getElementById('pse-download-url').value = p.download_url || '';
            document.getElementById('pse-desc').value = p.short_desc || '';

            // Specifications line by line
            populatePseSpecs(p.specs || []);

            // Full Markdown Manual & Architecture Description
            document.getElementById('pse-description').value = p.description || '';
            renderProductMarkdownPreviewLive();
            updateProductMarkdownStats();

            // Dedicated SEO
            document.getElementById('pse-meta-title').value = p.meta_title || '';
            document.getElementById('pse-meta-desc').value = p.meta_desc || '';
            document.getElementById('pse-meta-keywords').value = p.meta_keywords || '';
            document.getElementById('pse-og-image').value = p.og_image || '';
            updateProductOgPreview(p.og_image || coverUrl);

            // In-article smart ad campaign
            document.getElementById('pse-ad-headline').value = p.ad_headline || '';
            document.getElementById('pse-ad-desc').value = p.ad_description || '';
            document.getElementById('pse-ad-badge').value = p.ad_badge || '';
            document.getElementById('pse-ad-cta').value = p.ad_cta_text || '';
            document.getElementById('pse-ad-image').value = p.ad_image_url || '';
            updateProductAdPreview();

            // Populate per-product FAQs
            populateProductStudioFaqs(p.faq || []);

            switchProductStudioTab('specs', document.querySelector('.pse-subnav-btn'));
            calcProductDiscount();
            updateProductPreview();
            updateProductSeoSimulator();

            switchAdminTab('product-editor', null);
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        function closeProductStudio() {
            switchAdminTab('products', document.querySelector('.admin-nav-item[data-tab="products"]') || document.querySelector('.admin-nav-item[onclick*="products"]'));
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        function switchProductStudioTab(tabKey, btn) {
            document.querySelectorAll('.pse-pane').forEach(el => el.style.display = 'none');
            document.querySelectorAll('.pse-subnav-btn').forEach(el => el.classList.remove('active'));

            const target = document.getElementById('pse-tab-' + tabKey);
            if (target) target.style.display = 'block';
            
            const activeBtn = btn || document.querySelector(`.pse-subnav-btn[onclick*="'${tabKey}'"]`);
            if (activeBtn) activeBtn.classList.add('active');

            if (tabKey === 'preview') updateProductPreview();
            if (tabKey === 'seo') updateProductSeoSimulator();
            if (tabKey === 'ad') updateProductAdPreview();
            if (tabKey === 'manual') {
                renderProductMarkdownPreviewLive();
                updateProductMarkdownStats();
            }
        }

        function calcProductDiscount() {
            const price = parseFloat(document.getElementById('pse-price').value) || 0;
            const retail = parseFloat(document.getElementById('pse-retail').value) || 0;
            const badge = document.getElementById('pse-discount-badge');
            if (badge) {
                if (retail > price && retail > 0) {
                    const pct = Math.round((1.0 - (price / retail)) * 100);
                    badge.textContent = `SAVINGS: ${pct}% OFF`;
                    badge.style.display = 'inline-block';
                } else {
                    badge.style.display = 'none';
                }
            }
        }

        function updateProductCoverPreview(url) {
            const el = document.getElementById('pse-image-preview');
            if (el) el.src = url || 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=1200&q=85';
            const sku = document.getElementById('pse-sku').value.trim();
            const badge = document.getElementById('pse-cover-overlay-badge');
            if (badge) badge.textContent = sku || 'SYSTEM SKU';
        }

        function applyProductCoverPreset(url) {
            const input = document.getElementById('pse-image');
            if (input) input.value = url;
            updateProductCoverPreview(url);
            updateProductPreview();
        }

        function updateProductOgPreview(url) {
            const el = document.getElementById('pse-og-preview');
            if (el) el.src = url || document.getElementById('pse-image').value || 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=1200&q=85';
        }

        function updateProductSeoSimulator() {
            const sku = document.getElementById('pse-sku').value.trim() || 'LIC-SKU';
            const name = document.getElementById('pse-name').value.trim() || 'System Name';
            const slug = document.getElementById('pse-slug').value.trim() || name.toLowerCase().replace(/[^a-z0-9]+/g, '-');
            const customTitle = document.getElementById('pse-meta-title').value.trim();
            const customDesc = document.getElementById('pse-meta-desc').value.trim();
            const shortDesc = document.getElementById('pse-desc').value.trim();

            const serpTitle = document.getElementById('pse-serp-title');
            const serpDesc = document.getElementById('pse-serp-desc');
            const serpUrl = document.getElementById('pse-serp-url');
            const countT = document.getElementById('pse-count-title');
            const countD = document.getElementById('pse-count-desc');

            if (serpUrl) serpUrl.textContent = `https://matrix.security/product/${slug}`;
            if (serpTitle) serpTitle.textContent = customTitle || `${name} (${sku}) — Enterprise License // {{ site_settings.site_name }}`;
            if (serpDesc) serpDesc.textContent = customDesc || shortDesc || 'Commercial security auditing suites, binary analysis frameworks, and verified enterprise seats.';

            if (countT) countT.textContent = customTitle ? `${customTitle.length}/60 chars` : 'AUTO-FALLBACK';
            if (countD) countD.textContent = customDesc ? `${customDesc.length}/160 chars` : 'AUTO-FALLBACK';
        }

        function updateProductPreview() {
            const sku = document.getElementById('pse-sku').value.trim() || 'LIC-BURP-PRO';
            const name = document.getElementById('pse-name').value.trim() || 'Burp Suite Professional';
            const category = document.getElementById('pse-category').value.trim() || 'Web & AppSec';
            const price = document.getElementById('pse-price').value.trim() || '449';
            const retail = document.getElementById('pse-retail').value.trim() || '599';
            const version = document.getElementById('pse-version').value.trim() || 'v2026.10';
            const platform = document.getElementById('pse-platform').value.trim() || 'Windows / Linux / macOS';
            const duration = document.getElementById('pse-duration').value.trim() || '1-Year Enterprise';
            const badge = document.getElementById('pse-badge').value.trim() || 'INSTANT DELIVERY';
            const desc = document.getElementById('pse-desc').value.trim() || 'Enterprise web vulnerability scanner...';
            const img = document.getElementById('pse-image').value.trim() || 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=1200&q=85';

            // Card preview
            const cImg = document.getElementById('prev-card-img'); if (cImg) cImg.src = img;
            const cBadge = document.getElementById('prev-card-badge'); if (cBadge) cBadge.textContent = badge;
            const cSku = document.getElementById('prev-card-sku'); if (cSku) cSku.textContent = sku;
            const cVer = document.getElementById('prev-card-version'); if (cVer) cVer.textContent = version;
            const cName = document.getElementById('prev-card-name'); if (cName) cName.textContent = name;
            const cDesc = document.getElementById('prev-card-desc'); if (cDesc) cDesc.textContent = desc;
            const cPrice = document.getElementById('prev-card-price'); if (cPrice) cPrice.textContent = '$' + price;
            const cRetail = document.getElementById('prev-card-retail'); if (cRetail) cRetail.textContent = '$' + retail;

            // Header preview
            const hSku = document.getElementById('prev-hdr-sku'); if (hSku) hSku.textContent = sku;
            const hName = document.getElementById('prev-hdr-name'); if (hName) hName.textContent = name;
            const hCat = document.getElementById('prev-hdr-category'); if (hCat) hCat.textContent = category;
            const hPlat = document.getElementById('prev-hdr-platform'); if (hPlat) hPlat.textContent = platform;
            const hDur = document.getElementById('prev-hdr-duration'); if (hDur) hDur.textContent = duration;
            const hPrice = document.getElementById('prev-hdr-price'); if (hPrice) hPrice.textContent = '$' + price + '.00';
            const hRetail = document.getElementById('prev-hdr-retail'); if (hRetail) hRetail.textContent = '$' + retail + '.00';
            updateProductAdPreview();
        }

        function updateProductAdPreview() {
            const headline = (document.getElementById('pse-ad-headline') ? document.getElementById('pse-ad-headline').value.trim() : '') || (document.getElementById('pse-name') ? document.getElementById('pse-name').value.trim() : '') || 'BURP SUITE PROFESSIONAL';
            const desc = (document.getElementById('pse-ad-desc') ? document.getElementById('pse-ad-desc').value.trim() : '') || (document.getElementById('pse-desc') ? document.getElementById('pse-desc').value.trim() : '') || 'Enterprise web vulnerability detection and proxy testing framework.';
            const badge = document.getElementById('pse-ad-badge') ? document.getElementById('pse-ad-badge').value.trim() : '';
            const cta = (document.getElementById('pse-ad-cta') ? document.getElementById('pse-ad-cta').value.trim() : '') || 'ORDER VIA TELEGRAM →';
            const img = (document.getElementById('pse-ad-image') ? document.getElementById('pse-ad-image').value.trim() : '') || (document.getElementById('pse-image') ? document.getElementById('pse-image').value.trim() : '') || 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1200&q=85';

            const price = parseFloat(document.getElementById('pse-price') ? document.getElementById('pse-price').value : 0) || 0;
            const retail = parseFloat(document.getElementById('pse-retail') ? document.getElementById('pse-retail').value : 0) || 0;

            const tEl = document.getElementById('pse-sim-ad-title'); if (tEl) tEl.textContent = headline;
            const dEl = document.getElementById('pse-sim-ad-desc'); if (dEl) dEl.textContent = desc;
            const bEl = document.getElementById('pse-sim-ad-badge');
            if (bEl) {
                if (badge) {
                    bEl.textContent = badge;
                    bEl.style.background = '#dc2626';
                    bEl.style.color = '#ffffff';
                    bEl.style.border = 'none';
                } else if (retail > price && retail > 0) {
                    const pct = Math.round((1.0 - (price / retail)) * 100);
                    bEl.textContent = `SAVE ${pct}% OFF`;
                    bEl.style.background = '#dc2626';
                    bEl.style.color = '#ffffff';
                    bEl.style.border = 'none';
                } else {
                    bEl.textContent = 'VERIFIED SYSTEM';
                    bEl.style.background = 'rgba(255,255,255,0.18)';
                    bEl.style.border = '1px solid rgba(255,255,255,0.35)';
                }
            }
            const ctaEl = document.getElementById('pse-sim-ad-cta'); if (ctaEl) ctaEl.textContent = cta;
            const bgEl = document.getElementById('pse-sim-ad-bg'); if (bgEl) bgEl.style.backgroundImage = `url("${img}")`;

            const prEl = document.getElementById('pse-sim-ad-price');
            if (prEl) {
                let h = '';
                if (retail > price) {
                    h += `<span style="font-family:var(--admin-font-mono); text-decoration:line-through; color:rgba(255,255,255,0.55); margin-right:0.45rem; font-size:0.85rem;">$${Math.round(retail)}</span>`;
                }
                h += `<span style="font-family:var(--admin-font-mono); font-weight:700; font-size:1.2rem; color:#ffffff;">$${Math.round(price)}</span>`;
                prEl.innerHTML = h;
            }
        }

        function syncAdFromCatalogFields() {
            const name = document.getElementById('pse-name').value.trim();
            const desc = document.getElementById('pse-desc').value.trim();
            const img = document.getElementById('pse-image').value.trim();
            const price = parseFloat(document.getElementById('pse-price').value) || 0;
            const retail = parseFloat(document.getElementById('pse-retail').value) || 0;

            if (name) document.getElementById('pse-ad-headline').value = name;
            if (desc) document.getElementById('pse-ad-desc').value = desc;
            if (img) document.getElementById('pse-ad-image').value = img;
            if (retail > price && retail > 0) {
                const pct = Math.round((1.0 - (price / retail)) * 100);
                document.getElementById('pse-ad-badge').value = `SAVE ${pct}% OFF`;
            }
            document.getElementById('pse-ad-cta').value = 'ORDER VIA TELEGRAM →';
            updateProductAdPreview();
            showThemeToast('COPIED CURRENT PRODUCT METRICS INTO AD CAMPAIGN');
        }

        function clearAdCustomFields() {
            document.getElementById('pse-ad-headline').value = '';
            document.getElementById('pse-ad-desc').value = '';
            document.getElementById('pse-ad-badge').value = '';
            document.getElementById('pse-ad-cta').value = '';
            document.getElementById('pse-ad-image').value = '';
            updateProductAdPreview();
            showThemeToast('CLEARED AD OVERRIDES — DEFAULTING TO STORE CATALOG');
        }

        async function submitProductStudio(e) {
            e.preventDefault();
            const id = document.getElementById('pse-id').value;
            const saveBtn = document.getElementById('pse-btn-save');
            const origText = saveBtn ? saveBtn.textContent : 'SAVE SYSTEM SPECIFICATIONS →';

            const sku = document.getElementById('pse-sku').value.trim();
            const name = document.getElementById('pse-name').value.trim();
            if (!sku || !name) {
                alert('Please enter both SKU and System Name.');
                switchProductStudioTab('specs', document.querySelector('.pse-subnav-btn'));
                return;
            }

            if (saveBtn) { saveBtn.textContent = 'PERSISTING SPECIFICATIONS...'; saveBtn.disabled = true; }

            const payload = {
                sku: sku,
                name: name,
                slug: document.getElementById('pse-slug').value.trim(),
                category: document.getElementById('pse-category').value.trim(),
                product_type: document.getElementById('pse-type').value,
                price: parseFloat(document.getElementById('pse-price').value) || 0,
                retail_price: parseFloat(document.getElementById('pse-retail').value) || 0,
                version: document.getElementById('pse-version').value.trim(),
                license_duration: document.getElementById('pse-duration').value.trim(),
                platform: document.getElementById('pse-platform').value.trim(),
                badge_text: document.getElementById('pse-badge').value.trim(),
                featured: (document.getElementById('pse-featured') && document.getElementById('pse-featured').checked) ? 1 : 0,
                image_url: document.getElementById('pse-image').value.trim(),
                sha256_hash: document.getElementById('pse-sha256').value.trim(),
                download_url: document.getElementById('pse-download-url').value.trim(),
                short_desc: document.getElementById('pse-desc').value.trim(),
                specs: Array.from(document.querySelectorAll('#pse-specs-container .pse-spec-item-input'))
                    .map(i => i.value.trim())
                    .filter(s => s.length > 0),
                description: (document.getElementById('pse-description') ? document.getElementById('pse-description').value : '').trim(),
                meta_title: document.getElementById('pse-meta-title').value.trim(),
                meta_desc: document.getElementById('pse-meta-desc').value.trim(),
                meta_keywords: document.getElementById('pse-meta-keywords').value.trim(),
                og_image: document.getElementById('pse-og-image').value.trim(),
                ad_headline: document.getElementById('pse-ad-headline') ? document.getElementById('pse-ad-headline').value.trim() : '',
                ad_description: document.getElementById('pse-ad-desc') ? document.getElementById('pse-ad-desc').value.trim() : '',
                ad_badge: document.getElementById('pse-ad-badge') ? document.getElementById('pse-ad-badge').value.trim() : '',
                ad_cta_text: document.getElementById('pse-ad-cta') ? document.getElementById('pse-ad-cta').value.trim() : '',
                ad_image_url: document.getElementById('pse-ad-image') ? document.getElementById('pse-ad-image').value.trim() : ''
            };
            if (id) payload.id = parseInt(id, 10);

            // Collect FAQ Accordions
            const pseFaqs = [];
            document.querySelectorAll('#pse-faq-container .pse-faq-row').forEach(row => {
                const q = (row.querySelector('.pse-faq-q') ? row.querySelector('.pse-faq-q').value : '').trim();
                const a = (row.querySelector('.pse-faq-a') ? row.querySelector('.pse-faq-a').value : '').trim();
                if (q || a) pseFaqs.push({ q, a });
            });
            payload.faq = pseFaqs;

            try {
                const res = await fetch('/api/admin/products', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (data.ok || data.success) {
                    showThemeToast(`SYSTEM SPECIFICATION PERSISTED: ${payload.sku}`);
                    setTimeout(() => location.reload(), 600);
                } else {
                    alert('Error saving system: ' + (data.error || 'Server error'));
                }
            } catch(err) {
                alert('Save error: ' + err.message);
            } finally {
                if (saveBtn) { saveBtn.textContent = origText; saveBtn.disabled = false; }
            }
        }

        // ==========================================
        // DEDICATED THREAT INTEL ADVISORY STUDIO
        // ==========================================
        function togglePlacementIntervalView() {
            const placement = document.getElementById('jse-ad-placement');
            const intervalGroup = document.getElementById('jse-interval-group');
            if (placement && intervalGroup) {
                intervalGroup.style.display = (placement.value === 'PARAGRAPH_INTERVAL') ? 'block' : 'none';
            }
        }

        function insertSmartAdShortcode(customSku) {
            const textarea = document.getElementById('jse-content');
            if (!textarea) return;

            textarea.focus();
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            const fullText = textarea.value;

            let code = '[ad]';
            if (customSku && typeof customSku === 'string') {
                code = `[ad:${customSku.trim().toUpperCase()}]`;
            }

            const before = fullText.substring(0, start);
            const after = fullText.substring(end);
            
            const prefix = before.endsWith('\n\n') ? '' : (before.endsWith('\n') ? '\n' : '\n\n');
            const suffix = after.startsWith('\n\n') ? '' : (after.startsWith('\n') ? '\n' : '\n\n');
            const insertion = prefix + code + suffix;

            textarea.value = before + insertion + after;
            textarea.selectionStart = textarea.selectionEnd = start + insertion.length;

            renderMarkdownPreviewLive();
            updatePostPreview();
            updateMarkdownStats();

            showThemeToast(`IN-ARTICLE SMART AD BANNER SHORTCODE ${code} INSERTED`);
        }



        function updateModalSpecsCount() {
            const rows = document.querySelectorAll('#modal-specs-container .modal-spec-row');
            rows.forEach((row, idx) => {
                const bullet = row.querySelector('.modal-spec-bullet');
                if (bullet) bullet.textContent = `#${idx + 1}`;
            });
        }

        function addModalSpecRow(text = '') {
            const container = document.getElementById('modal-specs-container');
            if (!container) return;
            const div = document.createElement('div');
            div.className = 'modal-spec-row';
            div.style.cssText = 'display:flex; align-items:center; gap:0.5rem; background:#141618; border:1px solid var(--admin-border); border-radius:4px; padding:0.4rem 0.6rem;';
            div.innerHTML = `
                <span class="modal-spec-bullet" style="color:#00e5ff; font-family:var(--admin-font-mono); font-size:10px; font-weight:700; width:26px;">#</span>
                <input type="text" class="form-input modal-spec-input" placeholder="e.g. Memory Analysis Engine" style="flex:1; font-weight:600; font-size:11px;">
                <button type="button" onclick="this.closest('.modal-spec-row').remove(); updateModalSpecsCount();" class="btn-admin btn-admin-danger" style="padding:0.15rem 0.4rem; font-size:9.5px;">REMOVE</button>
            `;
            div.querySelector('.modal-spec-input').value = text || '';
            container.appendChild(div);
            updateModalSpecsCount();
        }

        function populateModalSpecs(specs) {
            const container = document.getElementById('modal-specs-container');
            if (!container) return;
            container.innerHTML = '';
            if (Array.isArray(specs) && specs.length > 0) {
                specs.forEach(s => addModalSpecRow(s || ''));
            } else {
                addModalSpecRow('');
            }
            updateModalSpecsCount();
        }

        function addModalFaqRow(q = '', a = '') {
            const container = document.getElementById('modal-faq-container');
            if (!container) return;
            const div = document.createElement('div');
            div.className = 'modal-faq-row';
            div.style.cssText = 'background:#141618; border:1px solid var(--admin-border); border-radius:4px; padding:0.85rem;';
            div.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
                    <span class="modal-faq-index" style="font-family:var(--admin-font-mono); font-size:10px; color:#10b981; font-weight:700;">FAQ ITEM</span>
                    <button type="button" onclick="this.closest('.modal-faq-row').remove(); updateModalFaqLabels();" class="btn-admin btn-admin-danger" style="padding:0.15rem 0.4rem; font-size:9.5px;">REMOVE</button>
                </div>
                <input type="text" class="form-input modal-faq-q" placeholder="Question / Accordion title..." style="margin-bottom:0.4rem; font-size:11px; font-weight:600;">
                <textarea rows="2" class="form-textarea modal-faq-a" placeholder="Answer..." style="font-size:11px; line-height:1.4;"></textarea>
            `;
            div.querySelector('.modal-faq-q').value = q || '';
            div.querySelector('.modal-faq-a').value = a || '';
            container.appendChild(div);
            updateModalFaqLabels();
        }

        function updateModalFaqLabels() {
            const rows = document.querySelectorAll('#modal-faq-container .modal-faq-row');
            rows.forEach((r, idx) => {
                const label = r.querySelector('.modal-faq-index');
                if (label) label.textContent = `FAQ ITEM #${idx + 1}`;
            });
        }

        function populateModalFaqs(faqs) {
            const container = document.getElementById('modal-faq-container');
            if (!container) return;
            container.innerHTML = '';
            if (Array.isArray(faqs) && faqs.length > 0) {
                faqs.forEach(item => {
                    addModalFaqRow(item.q || '', item.a || '');
                });
            }
            updateModalFaqLabels();
        }

        function openProductModal() {
            document.getElementById('prod-modal-title').textContent = 'CREATE NEW SYSTEM';
            document.getElementById('prod-id').value = '';
            document.getElementById('prod-sku').value = '';
            document.getElementById('prod-name').value = '';
            document.getElementById('prod-category').value = 'Web & AppSec';
            document.getElementById('prod-price').value = '199';
            document.getElementById('prod-retail').value = '499';
            document.getElementById('prod-version').value = 'v2026.1';
            document.getElementById('prod-duration').value = '1-Year Pro Multi-Seat';
            document.getElementById('prod-platform').value = 'Windows / Linux / macOS';
            document.getElementById('prod-image').value = 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=1200&q=85';
            document.getElementById('prod-sha256').value = '';
            document.getElementById('prod-desc').value = '';
            document.getElementById('prod-meta-title').value = '';
            document.getElementById('prod-meta-desc').value = '';
            document.getElementById('prod-meta-keywords').value = '';
            document.getElementById('prod-og-image').value = '';
            document.getElementById('prod-ad-headline').value = '';
            document.getElementById('prod-ad-desc').value = '';
            document.getElementById('prod-ad-badge').value = '';
            document.getElementById('prod-ad-cta').value = '';
            document.getElementById('prod-ad-image').value = '';
            populateModalSpecs([]);
            const descEl = document.getElementById('prod-description');
            if (descEl) descEl.value = '';
            populateModalFaqs([]);
            document.getElementById('modal-product').classList.add('is-open');
        }

        function editProduct(p) {
            document.getElementById('prod-modal-title').textContent = 'EDIT SYSTEM: ' + p.sku;
            document.getElementById('prod-id').value = p.id;
            document.getElementById('prod-sku').value = p.sku;
            document.getElementById('prod-name').value = p.name;
            document.getElementById('prod-category').value = p.category;
            document.getElementById('prod-price').value = p.price;
            document.getElementById('prod-retail').value = p.retail_price;
            document.getElementById('prod-version').value = p.version;
            document.getElementById('prod-duration').value = p.license_duration;
            document.getElementById('prod-platform').value = p.platform;
            document.getElementById('prod-image').value = p.image_url || '';
            document.getElementById('prod-sha256').value = p.sha256_hash || '';
            document.getElementById('prod-desc').value = p.short_desc || '';
            document.getElementById('prod-meta-title').value = p.meta_title || '';
            document.getElementById('prod-meta-desc').value = p.meta_desc || '';
            document.getElementById('prod-meta-keywords').value = p.meta_keywords || '';
            document.getElementById('prod-og-image').value = p.og_image || '';
            document.getElementById('prod-ad-headline').value = p.ad_headline || '';
            document.getElementById('prod-ad-desc').value = p.ad_description || '';
            document.getElementById('prod-ad-badge').value = p.ad_badge || '';
            document.getElementById('prod-ad-cta').value = p.ad_cta_text || '';
            document.getElementById('prod-ad-image').value = p.ad_image_url || '';
            populateModalSpecs(p.specs || []);
            const descEl = document.getElementById('prod-description');
            if (descEl) descEl.value = p.description || '';
            populateModalFaqs(p.faq || []);
            document.getElementById('modal-product').classList.add('is-open');
        }

        async function submitProduct(e) {
            e.preventDefault();
            const id = document.getElementById('prod-id').value;
            const payload = {
                sku: document.getElementById('prod-sku').value.trim(),
                name: document.getElementById('prod-name').value.trim(),
                category: document.getElementById('prod-category').value.trim(),
                price: parseFloat(document.getElementById('prod-price').value) || 0,
                retail_price: parseFloat(document.getElementById('prod-retail').value) || 0,
                version: document.getElementById('prod-version').value.trim(),
                license_duration: document.getElementById('prod-duration').value.trim(),
                platform: document.getElementById('prod-platform').value.trim(),
                image_url: document.getElementById('prod-image').value.trim(),
                sha256_hash: document.getElementById('prod-sha256').value.trim(),
                short_desc: document.getElementById('prod-desc').value.trim(),
                meta_title: document.getElementById('prod-meta-title').value.trim(),
                meta_desc: document.getElementById('prod-meta-desc').value.trim(),
                meta_keywords: document.getElementById('prod-meta-keywords').value.trim(),
                og_image: document.getElementById('prod-og-image').value.trim(),
                ad_headline: document.getElementById('prod-ad-headline') ? document.getElementById('prod-ad-headline').value.trim() : '',
                ad_description: document.getElementById('prod-ad-desc') ? document.getElementById('prod-ad-desc').value.trim() : '',
                ad_badge: document.getElementById('prod-ad-badge') ? document.getElementById('prod-ad-badge').value.trim() : '',
                ad_cta_text: document.getElementById('prod-ad-cta') ? document.getElementById('prod-ad-cta').value.trim() : '',
                ad_image_url: document.getElementById('prod-ad-image') ? document.getElementById('prod-ad-image').value.trim() : ''
            };
            if (id) payload.id = parseInt(id, 10);

            // Collect modal specs
            const modalSpecs = [];
            document.querySelectorAll('#modal-specs-container .modal-spec-row .modal-spec-input').forEach(inp => {
                const val = inp.value.trim();
                if (val) modalSpecs.push(val);
            });
            payload.specs = modalSpecs;

            // Collect modal description
            const descInput = document.getElementById('prod-description');
            payload.description = descInput ? descInput.value : '';

            // Collect modal FAQs
            const modalFaqs = [];
            document.querySelectorAll('#modal-faq-container .modal-faq-row').forEach(row => {
                const q = (row.querySelector('.modal-faq-q') ? row.querySelector('.modal-faq-q').value : '').trim();
                const a = (row.querySelector('.modal-faq-a') ? row.querySelector('.modal-faq-a').value : '').trim();
                if (q || a) modalFaqs.push({ q, a });
            });
            payload.faq = modalFaqs;

            const res = await fetch('/api/admin/products', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (data.ok || data.success) location.reload();
            else alert(data.error || 'Product save error');
        }

        async function deleteProduct(id, name) {
            if (!confirm('Permanently delete ' + name + '?')) return;
            const res = await fetch('/api/admin/products/' + id, { method: 'DELETE' });
            const data = await res.json();
            if (data.ok || data.success) location.reload();
            else alert(data.error || 'Delete error');
        }

        // ==========================================
        // THREAT INTEL CRUD
        // ==========================================
