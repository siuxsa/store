        function updateJseStatusPill(val) {
            const pill = document.getElementById('jse-status-pill');
            if (!pill) return;
            const isDraft = (val || '').toUpperCase() === 'DRAFT';
            pill.textContent = isDraft ? 'DRAFT' : 'PUBLISHED';
            pill.style.background = isDraft ? '#f59e0b' : '#10b981';
            pill.style.color = '#000';
        }

        async function togglePostStatusQuick(postId, btn) {
            if (btn) btn.disabled = true;
            try {
                const res = await fetch(`/api/admin/posts/${postId}/toggle-status`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                const data = await res.json();
                if (data.ok) {
                    showThemeToast(`ADVISORY STATUS UPDATED: ${data.new_status}`);
                    setTimeout(() => location.reload(), 450);
                } else {
                    alert('Error changing status: ' + (data.error || 'Server error'));
                    if (btn) btn.disabled = false;
                }
            } catch(err) {
                alert('Request failed: ' + err.message);
                if (btn) btn.disabled = false;
            }
        }

        function openPostStudio() {
            document.getElementById('jse-id').value = '';
            document.getElementById('jse-slug').value = '';
            document.getElementById('jse-breadcrumb-title').textContent = 'DRAFT ADVISORY';
            document.getElementById('jse-heading-title').textContent = 'DRAFT THREAT INTEL ADVISORY';
            document.getElementById('jse-btn-view-live').style.display = 'none';

            if (document.getElementById('jse-status')) {
                document.getElementById('jse-status').value = 'PUBLISHED';
                updateJseStatusPill('PUBLISHED');
            }

            // Reset fields
            document.getElementById('jse-title').value = '';
            document.getElementById('jse-cve').value = 'CVE-2026-';
            document.getElementById('jse-cvss').value = '9.8';
            document.getElementById('jse-severity').value = 'CRITICAL';
            document.getElementById('jse-category').value = 'Zero-Day Advisories';
            document.getElementById('jse-author').value = 'ZERO//FORM RESEARCH LAB';
            document.getElementById('jse-read-time').value = '8 MIN READ';
            if (document.getElementById('jse-featured')) document.getElementById('jse-featured').checked = false;

            const bannerUrl = 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1600&q=85';
            document.getElementById('jse-image').value = bannerUrl;
            updatePostCoverPreview(bannerUrl);

            document.getElementById('jse-summary').value = '';
            document.getElementById('jse-content').value = "### 01 · Technical Breakdown\n\nOur offensive security lab audited the subsystem...\n\n[ad]\n\n```bash\n# Proof of concept verification\n./exploit --target kernel-6.13\n```\n\n> **NOTICE:** Patch advisory committed in upstream kernel tree.";
            renderMarkdownPreviewLive();

            document.getElementById('jse-skus').value = 'LIC-BURP-PRO,LIC-MSF-PRO';
            document.getElementById('jse-ad-mode').value = 'ALL';
            document.getElementById('jse-ad-count').value = '1';
            document.getElementById('jse-ad-placement').value = 'MIDDLE';
            document.getElementById('jse-ad-interval').value = '4';
            togglePlacementIntervalView();
            document.getElementById('jse-ad-pitch').value = 'Audit your perimeter against this zero-day with verified commercial licenses.';

            document.getElementById('jse-meta-title').value = '';
            document.getElementById('jse-meta-desc').value = '';
            document.getElementById('jse-meta-keywords').value = '';
            document.getElementById('jse-og-image').value = '';
            updatePostOgPreview(bannerUrl);

            switchPostStudioTab('markdown', document.querySelector('.jse-subnav-btn[onclick*="markdown"]') || document.querySelector('.jse-subnav-btn'));
            updatePostPreview();
            updatePostSeoSimulator();

            switchAdminTab('post-editor', null);
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        function openPostStudioForId(id) {
            const el = document.getElementById('post-data-' + id);
            if (!el) {
                console.error('Post raw script not found for ID', id);
                alert('Could not find post data for ID: ' + id);
                return;
            }
            try {
                const p = JSON.parse(el.textContent);
                editPostStudio(p);
            } catch(err) {
                console.error('Failed to parse post data for ID', id, err);
                alert('Failed to parse post data for ID ' + id + ': ' + err.message);
            }
        }

        function editPostStudio(p) {
            try {
                if (!p || typeof p !== 'object') {
                    console.error('Invalid post object passed to editPostStudio', p);
                    return;
                }
                document.getElementById('jse-id').value = p.id || '';
                document.getElementById('jse-slug').value = p.slug || '';
                document.getElementById('jse-breadcrumb-title').textContent = 'EDIT: ' + (p.cve_id || p.title || ('POST #' + p.id));
                document.getElementById('jse-heading-title').textContent = 'EDIT RESEARCH ADVISORY — ' + (p.title || '');

                const liveBtn = document.getElementById('jse-btn-view-live');
                if (liveBtn) {
                    liveBtn.href = '/intel/' + (p.slug || p.id);
                    liveBtn.style.display = 'inline-flex';
                }

                document.getElementById('jse-title').value = p.title || '';
                document.getElementById('jse-cve').value = p.cve_id || '';
                document.getElementById('jse-cvss').value = (p.cvss_score !== undefined && p.cvss_score !== null) ? String(p.cvss_score) : '9.8';
                document.getElementById('jse-severity').value = p.severity || 'CRITICAL';
                document.getElementById('jse-category').value = p.category || 'Zero-Day Advisories';
                document.getElementById('jse-author').value = p.author || 'ZERO//FORM RESEARCH LAB';
                document.getElementById('jse-read-time').value = p.read_time || '8 MIN READ';
                if (document.getElementById('jse-featured')) document.getElementById('jse-featured').checked = !!p.featured;
                if (document.getElementById('jse-status')) {
                    document.getElementById('jse-status').value = p.status || 'PUBLISHED';
                    updateJseStatusPill(p.status || 'PUBLISHED');
                }

                const bannerUrl = p.image_url || 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1600&q=85';
                document.getElementById('jse-image').value = bannerUrl;
                updatePostCoverPreview(bannerUrl);

                document.getElementById('jse-summary').value = p.summary || '';
                document.getElementById('jse-content').value = p.content || '';

                document.getElementById('jse-skus').value = p.related_skus || '';
                document.getElementById('jse-ad-mode').value = p.ad_mode || 'ALL';
                document.getElementById('jse-ad-count').value = (p.ad_count !== undefined && p.ad_count !== null ? String(p.ad_count) : '1');
                document.getElementById('jse-ad-placement').value = (p.ad_placement || 'MIDDLE');
                document.getElementById('jse-ad-interval').value = (p.ad_paragraph_interval !== undefined && p.ad_paragraph_interval !== null ? String(p.ad_paragraph_interval) : '4');
                togglePlacementIntervalView();
                document.getElementById('jse-ad-pitch').value = p.ad_custom_pitch || '';

                document.getElementById('jse-meta-title').value = p.meta_title || '';
                document.getElementById('jse-meta-desc').value = p.meta_desc || '';
                document.getElementById('jse-meta-keywords').value = p.meta_keywords || '';
                document.getElementById('jse-og-image').value = p.og_image || '';
                updatePostOgPreview(p.og_image || bannerUrl);

                renderMarkdownPreviewLive();
                updatePostPreview();
                updatePostSeoSimulator();
                updateMarkdownStats();

                // Open Markdown Studio directly so user sees the editor & live preview immediately!
                switchPostStudioTab('markdown', document.querySelector('.jse-subnav-btn[onclick*="markdown"]') || document.querySelector('.jse-subnav-btn'));

                switchAdminTab('post-editor', null);
                window.scrollTo({ top: 0, behavior: 'smooth' });
            } catch(err) {
                console.error('Failed to load post in Post Studio:', err);
                alert('Failed to load post in Post Studio: ' + err.message);
            }
        }

        function closePostStudio() {
            switchAdminTab('posts', document.querySelector('.admin-nav-item[data-tab="posts"]') || document.querySelector('.admin-nav-item[onclick*="posts"]'));
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        function switchPostStudioTab(tabKey, btn) {
            document.querySelectorAll('.jse-pane').forEach(el => el.style.display = 'none');
            document.querySelectorAll('.jse-subnav-btn').forEach(el => el.classList.remove('active'));

            const target = document.getElementById('jse-tab-' + tabKey);
            if (target) target.style.display = 'block';
            
            const activeBtn = btn || document.querySelector(`.jse-subnav-btn[onclick*="'${tabKey}'"]`);
            if (activeBtn) activeBtn.classList.add('active');

            if (tabKey === 'preview') updatePostPreview();
            if (tabKey === 'seo') updatePostSeoSimulator();
            if (tabKey === 'markdown') renderMarkdownPreviewLive();
        }

        function updatePostCoverPreview(url) {
            const el = document.getElementById('jse-image-preview');
            if (el) el.src = url || 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1600&q=85';
            const cve = document.getElementById('jse-cve').value.trim();
            const badge = document.getElementById('jse-cover-overlay-cve');
            if (badge) badge.textContent = cve || 'CVE-2026-XXXX';
        }

        function applyPostCoverPreset(url) {
            const input = document.getElementById('jse-image');
            if (input) input.value = url;
            updatePostCoverPreview(url);
            updatePostPreview();
        }

        function updatePostOgPreview(url) {
            const el = document.getElementById('jse-og-preview');
            if (el) el.src = url || document.getElementById('jse-image').value || 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1600&q=85';
        }

        function insertMarkdownSnippet(snippet) {
            formatMarkdownSelection('raw', snippet);
        }

        function getLineBounds(text, start, end) {
            let lineStart = text.lastIndexOf('\n', start - 1);
            lineStart = (lineStart === -1) ? 0 : lineStart + 1;
            let lineEnd = text.indexOf('\n', end);
            lineEnd = (lineEnd === -1) ? text.length : lineEnd;
            return { lineStart, lineEnd };
        }

        function applyLinePrefix(text, start, end, prefix) {
            const { lineStart, lineEnd } = getLineBounds(text, start, end);
            const lines = text.substring(lineStart, lineEnd).split('\n');
            let idx = 1;
            const modified = lines.map(line => {
                if (prefix.startsWith('#')) {
                    const clean = line.replace(/^#+\s*/, '');
                    return prefix + clean;
                }
                if (prefix === 'ol') {
                    const clean = line.replace(/^\d+\.\s*/, '');
                    return `${idx++}. ${clean}`;
                }
                if (prefix === 'quote') {
                    return `> ${line}`;
                }
                return prefix + line;
            });
            return modified.join('\n');
        }

        function formatMarkdownSelection(type, extra) {
            const textarea = document.getElementById('jse-content');
            if (!textarea) return;

            textarea.focus();
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            const fullText = textarea.value;
            const selected = fullText.substring(start, end);

            let replacement = '';
            let selectRange = null;

            switch(type) {
                case 'raw':
                    replacement = extra || '';
                    break;
                case 'bold':
                    if (selected) {
                        replacement = `**${selected}**`;
                        selectRange = [start + 2, start + 2 + selected.length];
                    } else {
                        replacement = `**bold text**`;
                        selectRange = [start + 2, start + 11];
                    }
                    break;
                case 'italic':
                    if (selected) {
                        replacement = `*${selected}*`;
                        selectRange = [start + 1, start + 1 + selected.length];
                    } else {
                        replacement = `*italic text*`;
                        selectRange = [start + 1, start + 12];
                    }
                    break;
                case 'strike':
                    if (selected) {
                        replacement = `~~${selected}~~`;
                        selectRange = [start + 2, start + 2 + selected.length];
                    } else {
                        replacement = `~~strikethrough text~~`;
                        selectRange = [start + 2, start + 20];
                    }
                    break;
                case 'code':
                    if (selected) {
                        replacement = `\`${selected}\``;
                        selectRange = [start + 1, start + 1 + selected.length];
                    } else {
                        replacement = `\`command_or_symbol\``;
                        selectRange = [start + 1, start + 18];
                    }
                    break;
                case 'codeblock':
                    const lang = extra || 'bash';
                    const code = selected || '# Terminal command execution\n./exploit --target localhost --port 8080';
                    replacement = `\n\`\`\`${lang}\n${code}\n\`\`\`\n`;
                    selectRange = [start + 4 + lang.length, start + 4 + lang.length + code.length];
                    break;
                case 'h1':
                    replacement = applyLinePrefix(fullText, start, end, '# ');
                    break;
                case 'h2':
                    replacement = applyLinePrefix(fullText, start, end, '## ');
                    break;
                case 'h3':
                    replacement = applyLinePrefix(fullText, start, end, '### ');
                    break;
                case 'h4':
                    replacement = applyLinePrefix(fullText, start, end, '#### ');
                    break;
                case 'quote':
                    replacement = applyLinePrefix(fullText, start, end, 'quote');
                    break;
                case 'ul':
                    replacement = applyLinePrefix(fullText, start, end, '- ');
                    break;
                case 'ol':
                    replacement = applyLinePrefix(fullText, start, end, 'ol');
                    break;
                case 'task':
                    replacement = applyLinePrefix(fullText, start, end, '- [ ] ');
                    break;
                case 'link':
                    const linkUrl = prompt('Enter Hyperlink Target URL:', 'https://');
                    if (linkUrl === null) return;
                    const linkText = selected || 'Technical Specification';
                    replacement = `[${linkText}](${linkUrl || 'https://'})`;
                    selectRange = [start + 1, start + 1 + linkText.length];
                    break;
                case 'image':
                    const imgUrl = prompt('Enter Image Asset URL:', 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1200&q=85');
                    if (imgUrl === null) return;
                    const altText = selected || 'Architecture & Attack Surface Diagram';
                    replacement = `\n![${altText}](${imgUrl})\n`;
                    break;
                case 'table':
                    replacement = `\n| TECHNICAL VECTOR | AFFECTED SUBSYSTEM | CVSS BASE |\n| :--- | :--- | :--- |\n| CVE-2026-3199 | Linux Kernel eBPF Verifier | CRITICAL (9.8) |\n| Memory Tamper | ring-0 Ring Execution Engine | HIGH (8.8) |\n| Token Smuggle | Enterprise Gateway Ingress | HIGH (8.4) |\n\n`;
                    break;
                case 'hr':
                    replacement = `\n\n---\n\n`;
                    break;
                case 'alert-warning':
                    replacement = `\n> [!WARNING]\n> ${selected || 'CRITICAL: Exploitation vector actively observed in the wild. Enforce immediate isolation patches.'}\n\n`;
                    break;
                case 'alert-note':
                    replacement = `\n> [!NOTE]\n> ${selected || 'Advisory research verified on hardened hypervisor testbed running Linux Kernel 6.13-rc7.'}\n\n`;
                    break;
                case 'alert-tip':
                    replacement = `\n> [!TIP]\n> ${selected || 'Deploy runtime eBPF tracepoint assertions to detect ring-0 privilege escalation attempts.'}\n\n`;
                    break;
                case 'pill':
                    replacement = `<span class="status-pill completed">${selected || 'CRITICAL 9.8'}</span>`;
                    break;
                case 'clear':
                    if (selected) {
                        replacement = selected
                            .replace(/^#+\s+/gm, '')
                            .replace(/^\>\s+/gm, '')
                            .replace(/^[\-\*\+]\s+/gm, '')
                            .replace(/^\d+\.\s+/gm, '')
                            .replace(/\*\*(.*?)\*\*/g, '$1')
                            .replace(/\*(.*?)\*/g, '$1')
                            .replace(/~~(.*?)~~/g, '$1')
                            .replace(/`([^`]+)`/g, '$1')
                            .replace(/\[(.*?)\]\(.*?\)/g, '$1');
                    }
                    break;
                default:
                    replacement = selected;
            }

            if (replacement !== '') {
                if (['h1', 'h2', 'h3', 'h4', 'quote', 'ul', 'ol', 'task'].includes(type)) {
                    const lineInfo = getLineBounds(fullText, start, end);
                    textarea.value = fullText.substring(0, lineInfo.lineStart) + replacement + fullText.substring(lineInfo.lineEnd);
                    textarea.selectionStart = lineInfo.lineStart;
                    textarea.selectionEnd = lineInfo.lineStart + replacement.length;
                } else {
                    textarea.value = fullText.substring(0, start) + replacement + fullText.substring(end);
                    if (selectRange) {
                        textarea.selectionStart = selectRange[0];
                        textarea.selectionEnd = selectRange[1];
                    } else {
                        textarea.selectionStart = textarea.selectionEnd = start + replacement.length;
                    }
                }
            }

            renderMarkdownPreviewLive();
            updatePostPreview();
            updateMarkdownStats();
        }

        function handleMarkdownEditorKeydown(e) {
            const textarea = e.target;
            // Tab key support: indent / outdent 2 spaces
            if (e.key === 'Tab') {
                e.preventDefault();
                const start = textarea.selectionStart;
                const end = textarea.selectionEnd;
                const value = textarea.value;

                if (!e.shiftKey) {
                    // Indent
                    if (start === end) {
                        textarea.value = value.substring(0, start) + '  ' + value.substring(end);
                        textarea.selectionStart = textarea.selectionEnd = start + 2;
                    } else {
                        const { lineStart, lineEnd } = getLineBounds(value, start, end);
                        const lines = value.substring(lineStart, lineEnd).split('\n');
                        const indented = lines.map(l => '  ' + l).join('\n');
                        textarea.value = value.substring(0, lineStart) + indented + value.substring(lineEnd);
                        textarea.selectionStart = lineStart;
                        textarea.selectionEnd = lineStart + indented.length;
                    }
                } else {
                    // Shift+Tab: Outdent
                    const { lineStart, lineEnd } = getLineBounds(value, start, end);
                    const lines = value.substring(lineStart, lineEnd).split('\n');
                    const outdented = lines.map(l => l.startsWith('  ') ? l.substring(2) : (l.startsWith(' ') ? l.substring(1) : l)).join('\n');
                    textarea.value = value.substring(0, lineStart) + outdented + value.substring(lineEnd);
                    textarea.selectionStart = lineStart;
                    textarea.selectionEnd = lineStart + outdented.length;
                }
                renderMarkdownPreviewLive();
                updateMarkdownStats();
                return;
            }

            // Keyboard Shortcuts: Ctrl+B, Ctrl+I, Ctrl+K
            if (e.ctrlKey || e.metaKey) {
                if (e.key === 'b' || e.key === 'B') {
                    e.preventDefault();
                    formatMarkdownSelection('bold');
                } else if (e.key === 'i' || e.key === 'I') {
                    e.preventDefault();
                    formatMarkdownSelection('italic');
                } else if (e.key === 'k' || e.key === 'K') {
                    e.preventDefault();
                    formatMarkdownSelection('link');
                }
            }
        }

        function updateMarkdownStats() {
            const text = (document.getElementById('jse-content') ? document.getElementById('jse-content').value : '') || '';
            const words = text.trim() ? (text.trim().match(/\S+/g) || []).length : 0;
            const chars = text.length;
            const lines = text ? text.split('\n').length : 0;
            const readTimeMin = Math.max(1, Math.ceil(words / 180));

            const wEl = document.getElementById('md-stat-words');
            const cEl = document.getElementById('md-stat-chars');
            const lEl = document.getElementById('md-stat-lines');
            const rEl = document.getElementById('md-stat-readtime');

            if (wEl) wEl.textContent = words.toLocaleString();
            if (cEl) cEl.textContent = chars.toLocaleString();
            if (lEl) lEl.textContent = lines.toLocaleString();
            if (rEl) rEl.textContent = `${readTimeMin} MIN READ`;

            // Auto sync with jse-read-time if empty or default
            const rtInput = document.getElementById('jse-read-time');
            if (rtInput && (!rtInput.value || rtInput.value.includes('MIN'))) {
                rtInput.value = `${readTimeMin} MIN READ`;
            }
        }

        function updateSummaryCharCount() {
            const sum = (document.getElementById('jse-summary') ? document.getElementById('jse-summary').value : '') || '';
            const cEl = document.getElementById('jse-summary-count');
            if (cEl) cEl.textContent = `${sum.length} CHARS`;
        }

        function setMarkdownViewMode(mode) {
            const grid = document.getElementById('jse-md-grid');
            const editorCol = document.getElementById('jse-md-editor-col');
            const previewCol = document.getElementById('jse-md-preview-col');
            const btnSplit = document.getElementById('btn-md-mode-split');
            const btnEditor = document.getElementById('btn-md-mode-editor');
            const btnPreview = document.getElementById('btn-md-mode-preview');

            [btnSplit, btnEditor, btnPreview].forEach(b => { if (b) b.classList.remove('active'); });

            if (mode === 'split') {
                if (btnSplit) btnSplit.classList.add('active');
                if (grid) grid.style.gridTemplateColumns = '1fr 1fr';
                if (editorCol) editorCol.style.display = 'flex';
                if (previewCol) previewCol.style.display = 'flex';
            } else if (mode === 'editor') {
                if (btnEditor) btnEditor.classList.add('active');
                if (grid) grid.style.gridTemplateColumns = '1fr';
                if (editorCol) editorCol.style.display = 'flex';
                if (previewCol) previewCol.style.display = 'none';
            } else if (mode === 'preview') {
                if (btnPreview) btnPreview.classList.add('active');
                if (grid) grid.style.gridTemplateColumns = '1fr';
                if (editorCol) editorCol.style.display = 'none';
                if (previewCol) previewCol.style.display = 'flex';
            }
        }

        function toggleMarkdownFullscreen() {
            const box = document.getElementById('jse-md-studio-box');
            const btn = document.getElementById('btn-md-fullscreen');
            const textarea = document.getElementById('jse-content');
            const previewCol = document.getElementById('jse-md-preview-col');

            if (!box) return;

            const isFull = box.classList.toggle('zen-fullscreen');
            if (isFull) {
                box.style.position = 'fixed';
                box.style.top = '0';
                box.style.left = '0';
                box.style.width = '100vw';
                box.style.height = '100vh';
                box.style.zIndex = '99999';
                box.style.background = '#0a0b0d';
                box.style.padding = '2rem';
                box.style.overflowY = 'auto';
                if (btn) btn.textContent = 'EXIT FULLSCREEN';
                if (textarea) textarea.style.height = 'calc(100vh - 230px)';
                if (previewCol) previewCol.style.height = 'calc(100vh - 200px)';
            } else {
                box.style.position = 'static';
                box.style.width = 'auto';
                box.style.height = 'auto';
                box.style.zIndex = 'auto';
                box.style.background = 'var(--admin-surface)';
                box.style.padding = '1.25rem';
                if (btn) btn.textContent = 'FULLSCREEN';
                if (textarea) textarea.style.height = '520px';
                if (previewCol) previewCol.style.height = '560px';
            }
        }

        function loadMarkdownTemplate(tmplKey) {
            const textarea = document.getElementById('jse-content');
            if (!textarea) return;

            if (textarea.value.trim().length > 30) {
                if (!confirm('Replace current markdown draft with the selected structured template?')) return;
            }

            const cve = (document.getElementById('jse-cve') ? document.getElementById('jse-cve').value.trim() : '') || 'CVE-2026-3199';
            const title = (document.getElementById('jse-title') ? document.getElementById('jse-title').value.trim() : '') || 'Linux Kernel Privilege Escalation Vector';

            let tmpl = '';
            if (tmplKey === 'cve') {
                tmpl = `### 01 · EXECUTIVE DISCLOSURE & CVSS BASE\nCritical vulnerability identified in enterprise infrastructure allowing unauthenticated remote code execution with ring-0 privileges.\n\n> [!WARNING]\n> Operational vulnerability verified under lab conditions. Ensure perimeter ingress gateways are patched immediately.\n\n---\n\n### 02 · TECHNICAL ATTACK SURFACE & ROOT CAUSE\nAuditing identified an integer overflow condition leading to improper boundary checks in memory allocation routines:\n\n\`\`\`bash\n# Verify vulnerability signature\ncurl -s -X POST https://matrix.security/api/v1/audit --data-binary @probe.bin\n\`\`\`\n\n| VECTOR IDENTIFIER | TARGET COMPONENT | CVSS 3.1 BASE |\n| :--- | :--- | :--- |\n| ${cve} | Kernel eBPF Memory Verifier | 9.8 CRITICAL |\n| Ring-0 Escalation | Hypervisor Dispatch Table | 9.1 CRITICAL |\n\n---\n\n### 03 · EXPLOITATION TIMELINE & AUDIT TRAIL\n1. Initial unauthenticated handshake dispatched across the public edge.\n2. Malformed token triggers out-of-bounds pointer decrement.\n3. Arbitrary shellcode executed under root context.\n\n---\n\n### 04 · REMEDIATION & DETECTION SIGNATURES\n- Deploy vendor security patch release **v2026.10.4** immediately.\n- Implement strict runtime eBPF tracepoints to log anomalous privilege escalation.\n- Isolate management interfaces from public networks.`;
            } else if (tmplKey === 're') {
                tmpl = `### 01 · TARGET BINARY MANIFEST\n- **Architecture**: x86_64 ELF & PE32+ (Dual Artifact)\n- **Compiler Suite**: Clang 19 with OLLVM Control Flow Flattening\n- **Cryptographic Hash (SHA-256)**: \`8f4e2b91a04d3c90e5fa3b82c61099238e83b1dc3a2b1c902348a\`\n\n---\n\n### 02 · REVERSE ENGINEERING & DISASSEMBLY ANALYSIS\nAnalysis reveals dynamic API resolution via PEB export directory hashing:\n\n\`\`\`c\n// Decompiled symbol resolution engine\nFARPROC ResolveApiHash(DWORD dwModuleHash, DWORD dwFunctionHash) {\n    PPEB pPeb = (PPEB)__readgsqword(0x60);\n    // Export table walking loop\n    return pTargetFunction;\n}\n\`\`\`\n\n> [!NOTE]\n> Dynamic strings are encrypted using an AES-256-GCM envelope with an embedded hardware-derived key.\n\n---\n\n### 03 · MITRE ATT&CK EVALUATION\n- **T1055**: Process Injection via Hollow Process Staging\n- **T1027**: Obfuscated Files and Encrypted Payloads\n- **T1140**: Deobfuscate / Decode Files or Memory`;
            } else if (tmplKey === 'incident') {
                tmpl = `### 01 · INCIDENT OVERVIEW & THREAT SEVERITY\n- **Incident Token**: INC-2026-ALPHA\n- **Threat Level**: <span class="status-pill completed">CRITICAL 9.8</span>\n- **Affected Cluster**: Production Hypervisor Mesh (Region: EU-West-1)\n\n> [!WARNING]\n> Active persistence mechanism detected within scheduled hypervisor jobs.\n\n---\n\n### 02 · CONTAINMENT TIMELINE\n- **02:14 UTC**: Anomalous lateral movement detected via SIEM telemetry.\n- **02:28 UTC**: Compromised worker nodes isolated into quarantine VLAN.\n- **03:05 UTC**: Root credentials rotated and revoked across the identity mesh.\n\n---\n\n### 03 · ROOT CAUSE & POST-MORTEM ACTION ITEMS\n- [x] Rotate all master API tokens and SSH keys\n- [x] Revoke unauthenticated API ingress endpoints\n- [ ] Deploy zero-trust microsegmentation across worker pools\n- [ ] Complete forensic memory dump analysis`;
            }

            textarea.value = tmpl;
            renderMarkdownPreviewLive();
            updatePostPreview();
            updateMarkdownStats();
        }

        function copyRenderedHtml() {
            const preview = document.getElementById('jse-live-markdown-preview');
            if (!preview) return;
            navigator.clipboard.writeText(preview.innerHTML).then(() => {
                alert('Rendered HTML copied to clipboard.');
            }).catch(() => {
                alert('Copied to clipboard.');
            });
        }

        function renderMarkdownPreviewLive() {
            const text = (document.getElementById('jse-content') ? document.getElementById('jse-content').value : '') || '';
            const preview = document.getElementById('jse-live-markdown-preview');
            if (!preview) return;

            if (!text.trim()) {
                preview.innerHTML = '<p style="color:var(--admin-muted); font-style:italic;">Type or select markdown content on the left to see instant live rendering here...</p>';
                return;
            }

            let rendered = '';

            // Use marked.js if available
            if (typeof marked !== 'undefined' && typeof marked.parse === 'function') {
                try {
                    rendered = marked.parse(text, { gfm: true, breaks: true });
                } catch(e) {
                    rendered = '';
                }
            }

            // Fallback high-fidelity parser if marked not loaded
            if (!rendered) {
                rendered = text
                    .replace(/^### (.*$)/gim, '<h3 style="font-size:16px; font-weight:700; color:#fff; margin-top:1.25rem; margin-bottom:0.4rem; border-left:3px solid #00e5ff; padding-left:8px;">$1</h3>')
                    .replace(/^## (.*$)/gim, '<h2 style="font-size:19px; font-weight:700; color:#00e5ff; margin-top:1.5rem; margin-bottom:0.5rem; letter-spacing:-0.02em;">$1</h2>')
                    .replace(/^# (.*$)/gim, '<h1 style="font-size:23px; font-weight:800; color:#fff; margin-top:1.75rem; margin-bottom:0.75rem; letter-spacing:-0.02em;">$1</h1>')
                    .replace(/\*\*(.*?)\*\*/gim, '<strong style="color:#fff; font-weight:700;">$1</strong>')
                    .replace(/\*(.*?)\*/gim, '<em style="color:#d1d5db;">$1</em>')
                    .replace(/~~(.*?)~~/gim, '<del style="color:#6b7280;">$1</del>')
                    .replace(/```(\w*)\n([\s\S]*?)```/gim, '<pre style="background:#121417; border:1px solid rgba(255,255,255,0.12); padding:1rem; border-radius:4px; font-family:var(--admin-font-mono); font-size:11.5px; line-height:1.6; overflow-x:auto; margin:1rem 0; color:#10b981;"><code>$2</code></pre>')
                    .replace(/`([^`]+)`/gim, '<code style="background:rgba(255,255,255,0.08); padding:2px 6px; font-family:var(--admin-font-mono); font-size:11px; color:#00e5ff; border-radius:2px;">$1</code>')
                    .replace(/^-\s+\[ \]\s+(.*$)/gim, '<div style="display:flex; align-items:center; gap:8px; margin:4px 0;"><input type="checkbox" disabled style="accent-color:#00e5ff;"> <span>$1</span></div>')
                    .replace(/^-\s+\[x\]\s+(.*$)/gim, '<div style="display:flex; align-items:center; gap:8px; margin:4px 0;"><input type="checkbox" checked disabled style="accent-color:#00e5ff;"> <span style="text-decoration:line-through; color:var(--admin-muted);">$1</span></div>')
                    .replace(/^-\s+(.*$)/gim, '<li style="margin-left:1.25rem; list-style-type:square; color:#e5e7eb;">$1</li>')
                    .replace(/^\d+\.\s+(.*$)/gim, '<li style="margin-left:1.25rem; list-style-type:decimal; color:#e5e7eb;">$1</li>')
                    .replace(/^>\s+(.*$)/gim, '<blockquote style="border-left:3px solid #00e5ff; padding:0.6rem 1rem; background:rgba(0,229,255,0.04); margin:0.85rem 0; font-style:italic; color:#e2e8f0;">$1</blockquote>')
                    .replace(/\[(.*?)\]\((.*?)\)/gim, '<a href="$2" target="_blank" style="color:#00e5ff; text-decoration:underline;">$1 ↗</a>')
                    .replace(/\n\n/gim, '<br><br>');
            }

            // Post-process GitHub Alert Callouts: [!WARNING], [!NOTE], [!TIP], [!CAUTION]
            rendered = rendered
                .replace(/<blockquote>\s*<p>\s*\[!WARNING\]\s*([\s\S]*?)<\/p>\s*<\/blockquote>/gim, 
                    '<div style="background:rgba(245,158,11,0.08); border-left:4px solid #f59e0b; padding:0.85rem 1.15rem; margin:1rem 0; border-radius:0 4px 4px 0;"><div style="font-family:var(--admin-font-mono); font-size:11px; font-weight:700; color:#f59e0b; margin-bottom:4px; display:flex; align-items:center; gap:6px;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg> WARNING ADVISORY</div><div style="color:#fef3c7; font-size:12.5px; line-height:1.6;">$1</div></div>')
                .replace(/<blockquote>\s*<p>\s*\[!NOTE\]\s*([\s\S]*?)<\/p>\s*<\/blockquote>/gim, 
                    '<div style="background:rgba(0,229,255,0.07); border-left:4px solid #00e5ff; padding:0.85rem 1.15rem; margin:1rem 0; border-radius:0 4px 4px 0;"><div style="font-family:var(--admin-font-mono); font-size:11px; font-weight:700; color:#00e5ff; margin-bottom:4px; display:flex; align-items:center; gap:6px;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg> RESEARCH NOTE</div><div style="color:#e0f2fe; font-size:12.5px; line-height:1.6;">$1</div></div>')
                .replace(/<blockquote>\s*<p>\s*\[!TIP\]\s*([\s\S]*?)<\/p>\s*<\/blockquote>/gim, 
                    '<div style="background:rgba(16,185,129,0.08); border-left:4px solid #10b981; padding:0.85rem 1.15rem; margin:1rem 0; border-radius:0 4px 4px 0;"><div style="font-family:var(--admin-font-mono); font-size:11px; font-weight:700; color:#10b981; margin-bottom:4px; display:flex; align-items:center; gap:6px;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg> DEFENSIVE TIP</div><div style="color:#d1fae5; font-size:12.5px; line-height:1.6;">$1</div></div>')
                .replace(/<blockquote>\s*<p>\s*\[!CAUTION\]\s*([\s\S]*?)<\/p>\s*<\/blockquote>/gim, 
                    '<div style="background:rgba(239,68,68,0.08); border-left:4px solid #ef4444; padding:0.85rem 1.15rem; margin:1rem 0; border-radius:0 4px 4px 0;"><div style="font-family:var(--admin-font-mono); font-size:11px; font-weight:700; color:#ef4444; margin-bottom:4px; display:flex; align-items:center; gap:6px;"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/></svg> CRITICAL ALERT</div><div style="color:#fee2e2; font-size:12.5px; line-height:1.6;">$1</div></div>');

            // Style HTML tables rendered by marked.js
            rendered = rendered.replace(/<table>/gim, '<table style="width:100%; border-collapse:collapse; margin:1.25rem 0; font-family:var(--admin-font-mono); font-size:11px; background:#101214; border:1px solid rgba(255,255,255,0.1);">');
            rendered = rendered.replace(/<th>/gim, '<th style="border:1px solid rgba(255,255,255,0.15); padding:8px 12px; background:rgba(255,255,255,0.05); color:#fff; text-align:left; font-weight:700;">');
            rendered = rendered.replace(/<td>/gim, '<td style="border:1px solid rgba(255,255,255,0.08); padding:8px 12px; color:#e5e7eb;">');

            // Process Smart Ad shortcodes [ad], [ad:SKU], [product:SKU] in live markdown preview
            const prods = (window.ADMIN_CATALOG_PRODUCTS && Array.isArray(window.ADMIN_CATALOG_PRODUCTS)) ? window.ADMIN_CATALOG_PRODUCTS : [];
            let adPreviewIndex = 0;

            const adRegex = /(?:<p>\s*)?\[(?:ad|product)(?::([A-Za-z0-9_\-]+))?\](?:\s*<\/p>)?/gi;
            rendered = rendered.replace(adRegex, function(match, skuParam) {
                adPreviewIndex++;
                let prod = null;
                if (skuParam && skuParam.toUpperCase() !== 'AUTO' && skuParam.toUpperCase() !== 'MIDDLE') {
                    prod = prods.find(p => p.sku && p.sku.toUpperCase() === skuParam.toUpperCase());
                }
                if (!prod) {
                    prod = prods[(adPreviewIndex - 1) % (prods.length || 1)] || {
                        name: 'BURP SUITE PROFESSIONAL v2026.1',
                        sku: 'LIC-BURP-PRO',
                        price: 199,
                        retail_price: 499,
                        image_url: 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=1200&q=85',
                        ad_headline: 'BURP SUITE PROFESSIONAL v2026.1',
                        ad_description: 'Instant license delivery with unlimited scanner threads and verified SHA-256 hashes.',
                        ad_badge: 'SAVE 60% OFF',
                        ad_cta_text: 'ORDER SYSTEM →'
                    };
                }

                const headline = prod.ad_headline || prod.name || 'COMMERCIAL SECURITY SYSTEM';
                const desc = prod.ad_description || prod.short_desc || 'Verified commercial security software and binary licenses ready for deployment.';
                const badge = prod.ad_badge || (prod.discount_pct ? `SAVE ${prod.discount_pct}% OFF` : 'VERIFIED INVENTORY');
                const ctaText = prod.ad_cta_text || 'ORDER SYSTEM →';
                const img = prod.ad_image_url || prod.image_url || 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=1200&q=85';
                const price = prod.price || 199;
                const retail = prod.retail_price || 0;

                return `
                <div class="smart-ad-markdown-preview-card" style="position:relative; overflow:hidden; border-radius:4px; padding:1.15rem 1.35rem; margin:1.5rem 0; background:#0c0d0e; border:1px solid #00e5ff; box-shadow:0 6px 20px rgba(0,229,255,0.15); font-family:var(--admin-font-mono);">
                    <div style="position:absolute; inset:0; z-index:0; background-image:url('${img}'); background-size:cover; background-position:center; filter:brightness(0.68) contrast(1.05);"></div>
                    <div style="position:absolute; inset:0; z-index:1; background:linear-gradient(90deg, rgba(8,9,11,0.72) 0%, rgba(8,9,11,0.45) 50%, rgba(8,9,11,0.75) 100%); pointer-events:none;"></div>
                    
                    <div style="position:relative; z-index:2; display:flex; flex-direction:column; gap:0.45rem;">
                        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
                            <div style="display:flex; align-items:center; gap:6px;">
                                <span style="background:#00e5ff; color:#0c0d0e; font-size:9.5px; font-weight:800; padding:2px 6px; border-radius:2px; letter-spacing:0.06em;">LIVE SMART AD BANNER #${adPreviewIndex}</span>
                                <span style="font-size:11.5px; color:#ffffff; font-weight:700; text-shadow:0 1px 3px rgba(0,0,0,0.9);">${headline}</span>
                            </div>
                            <span style="background:rgba(0,0,0,0.8); color:#00e5ff; border:1px solid #00e5ff; padding:2px 7px; font-size:9.5px; font-weight:800; border-radius:2px;">${badge}</span>
                        </div>
                        <p style="margin:0.25rem 0; font-size:11.5px; line-height:1.4; color:rgba(255,255,255,0.92); display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; text-shadow:0 1px 3px rgba(0,0,0,0.95);">
                            ${desc}
                        </p>
                        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem; padding-top:0.4rem; border-top:1px solid rgba(255,255,255,0.2);">
                            <div style="display:flex; align-items:baseline; gap:6px;">
                                <span style="font-size:14px; font-weight:800; color:#ffffff;">$${price}</span>
                                ${retail > price ? `<span style="font-size:11px; text-decoration:line-through; color:rgba(255,255,255,0.5);">$${retail}</span>` : ''}
                            </div>
                            <span style="background:#ffffff; color:#0c0d0e; padding:3px 8px; font-size:10px; font-weight:800; border-radius:2px;">${ctaText}</span>
                        </div>
                    </div>
                </div>
                `;
            });

            preview.innerHTML = rendered;
        }

        function toggleLinkedSku(sku) {
            const input = document.getElementById('jse-skus');
            if (!input) return;
            const current = input.value.split(',').map(s => s.trim().toUpperCase()).filter(s => s.length > 0);
            const index = current.indexOf(sku.toUpperCase());
            if (index > -1) {
                current.splice(index, 1);
            } else {
                current.push(sku.toUpperCase());
            }
            input.value = current.join(',');
            updatePostPreview();
        }

        function updatePostSeoSimulator() {
            const cve = document.getElementById('jse-cve').value.trim() || 'CVE-2026-XXXX';
            const title = document.getElementById('jse-title').value.trim() || 'Advisory Title';
            const slug = document.getElementById('jse-slug').value.trim() || title.toLowerCase().replace(/[^a-z0-9]+/g, '-');
            const customTitle = document.getElementById('jse-meta-title').value.trim();
            const customDesc = document.getElementById('jse-meta-desc').value.trim();
            const summary = document.getElementById('jse-summary').value.trim();

            const serpTitle = document.getElementById('jse-serp-title');
            const serpDesc = document.getElementById('jse-serp-desc');
            const serpUrl = document.getElementById('jse-serp-url');
            const countT = document.getElementById('jse-count-title');
            const countD = document.getElementById('jse-count-desc');

            if (serpUrl) serpUrl.textContent = `https://matrix.security/journal/${slug}`;
            if (serpTitle) serpTitle.textContent = customTitle || `${title} [${cve}] // {{ site_settings.site_name }} Threat Research`;
            if (serpDesc) serpDesc.textContent = customDesc || summary || 'Brief technical vulnerability analysis and PoC exploit mitigation details...';

            if (countT) countT.textContent = customTitle ? `${customTitle.length}/60 chars` : 'AUTO-FALLBACK';
            if (countD) countD.textContent = customDesc ? `${customDesc.length}/160 chars` : 'AUTO-FALLBACK';
        }

        function updatePostPreview() {
            const cve = document.getElementById('jse-cve').value.trim() || 'CVE-2026-XXXX';
            const title = document.getElementById('jse-title').value.trim() || 'Vulnerability Analysis Title';
            const cvss = document.getElementById('jse-cvss').value.trim() || '9.8';
            const category = document.getElementById('jse-category').value.trim() || 'Zero-Day Advisories';
            const summary = document.getElementById('jse-summary').value.trim() || 'Executive summary of this security advisory...';
            const banner = document.getElementById('jse-image').value.trim() || 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1600&q=85';
            const pitch = document.getElementById('jse-ad-pitch').value.trim() || 'Audit your perimeter with verified commercial licenses.';

            const pBanner = document.getElementById('prev-art-banner'); if (pBanner) pBanner.src = banner;
            const pCve = document.getElementById('prev-art-cve'); if (pCve) pCve.textContent = cve;
            const pCvss = document.getElementById('prev-art-cvss'); if (pCvss) pCvss.textContent = 'CVSS ' + cvss;
            const pCat = document.getElementById('prev-art-category'); if (pCat) pCat.textContent = category.toUpperCase();
            const pTitle = document.getElementById('prev-art-title'); if (pTitle) pTitle.textContent = title;
            const pSumm = document.getElementById('prev-art-summary'); if (pSumm) pSumm.textContent = summary;
            const pPitch = document.getElementById('prev-art-ad-pitch'); if (pPitch) pPitch.textContent = pitch;
        }

        async function submitPostStudio(e, targetStatus = null) {
            if (e && e.preventDefault) e.preventDefault();
            const id = document.getElementById('jse-id').value;
            const saveBtn = document.getElementById('jse-btn-save');
            const draftBtn = document.getElementById('jse-btn-draft');
            const origText = saveBtn ? saveBtn.textContent : 'PUBLISH / SAVE ADVISORY →';

            const title = document.getElementById('jse-title').value.trim();
            if (!title) {
                alert('Please enter an Advisory Title.');
                switchPostStudioTab('specs', document.querySelector('.jse-subnav-btn'));
                return;
            }

            let finalStatus = targetStatus;
            if (!finalStatus) {
                finalStatus = (document.getElementById('jse-status') ? document.getElementById('jse-status').value : 'PUBLISHED');
            }
            if (document.getElementById('jse-status')) {
                document.getElementById('jse-status').value = finalStatus;
                updateJseStatusPill(finalStatus);
            }

            if (saveBtn) { saveBtn.textContent = 'PERSISTING ADVISORY...'; saveBtn.disabled = true; }
            if (draftBtn) { draftBtn.disabled = true; }

            const payload = {
                title: title,
                slug: document.getElementById('jse-slug').value.trim(),
                cve_id: document.getElementById('jse-cve').value.trim(),
                cvss_score: document.getElementById('jse-cvss').value.trim(),
                severity: document.getElementById('jse-severity').value,
                category: document.getElementById('jse-category').value.trim(),
                status: finalStatus,
                author: document.getElementById('jse-author').value.trim() || 'ZERO//FORM RESEARCH LAB',
                read_time: document.getElementById('jse-read-time').value.trim() || '8 MIN READ',
                image_url: document.getElementById('jse-image').value.trim(),
                summary: document.getElementById('jse-summary').value.trim(),
                content: document.getElementById('jse-content').value.trim(),
                related_skus: document.getElementById('jse-skus').value.trim(),
                ad_mode: document.getElementById('jse-ad-mode').value,
                ad_count: parseInt(document.getElementById('jse-ad-count').value, 10) || 0,
                ad_placement: document.getElementById('jse-ad-placement').value,
                ad_paragraph_interval: parseInt(document.getElementById('jse-ad-interval').value, 10) || 4,
                ad_custom_pitch: document.getElementById('jse-ad-pitch').value.trim(),
                meta_title: document.getElementById('jse-meta-title').value.trim(),
                meta_desc: document.getElementById('jse-meta-desc').value.trim(),
                meta_keywords: document.getElementById('jse-meta-keywords').value.trim(),
                og_image: document.getElementById('jse-og-image').value.trim()
            };
            if (id) payload.id = parseInt(id, 10);

            try {
                const res = await fetch('/api/admin/posts', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (data.ok || data.success) {
                    try { sessionStorage.setItem('activeAdminTab', 'posts'); } catch(e) {}
                    const statusMsg = payload.status === 'DRAFT' ? 'SAVED AS DRAFT' : 'PUBLISHED & ARCHIVED';
                    showThemeToast(`ADVISORY ${statusMsg}: ${payload.title.substring(0, 30)}...`);

                    const liveBtn = document.getElementById('jse-btn-view-live');
                    if (liveBtn) {
                        const finalSlug = data.slug || payload.slug || id;
                        liveBtn.href = '/intel/' + finalSlug;
                        liveBtn.style.display = 'inline-flex';
                    }
                    if (data.id) {
                        document.getElementById('jse-id').value = data.id;
                    }
                    setTimeout(() => location.reload(), 700);
                } else {
                    alert('Error saving advisory: ' + (data.error || 'Server error'));
                }
            } catch(err) {
                alert('Save error: ' + err.message);
            } finally {
                if (saveBtn) { saveBtn.textContent = origText; saveBtn.disabled = false; }
                if (draftBtn) { draftBtn.disabled = false; }
            }
        }

        // ==========================================
        // PRODUCTS CATALOG CRUD (MODAL FALLBACK)
        // ==========================================


        function openPostModal() {
            document.getElementById('post-modal-title').textContent = 'DRAFT THREAT ADVISORY';
            document.getElementById('post-id').value = '';
            document.getElementById('post-slug').value = '';
            document.getElementById('post-title').value = '';
            document.getElementById('post-cve').value = 'CVE-2026-';
            document.getElementById('post-cvss').value = '9.8';
            document.getElementById('post-severity').value = 'CRITICAL';
            document.getElementById('post-category').value = 'Cloud Infrastructure';
            document.getElementById('post-image').value = 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1600&q=85';
            document.getElementById('post-skus').value = 'LIC-BURP-PRO,LIC-MSF-PRO';
            document.getElementById('post-read-time').value = '7 MIN READ';
            document.getElementById('post-ad-count').value = '1';
            document.getElementById('post-ad-placement').value = 'MIDDLE';
            document.getElementById('post-ad-interval').value = '4';
            document.getElementById('post-ad-pitch').value = '';
            document.getElementById('post-summary').value = '';
            document.getElementById('post-content').value = '';
            document.getElementById('post-meta-title').value = '';
            document.getElementById('post-meta-desc').value = '';
            document.getElementById('post-meta-keywords').value = '';
            document.getElementById('post-og-image').value = '';
            document.getElementById('modal-post').classList.add('is-open');
        }

        function editPost(p) {
            document.getElementById('post-modal-title').textContent = 'EDIT ADVISORY: ' + (p.cve_id || p.title);
            document.getElementById('post-id').value = p.id;
            document.getElementById('post-slug').value = p.slug || '';
            document.getElementById('post-title').value = p.title;
            document.getElementById('post-cve').value = p.cve_id;
            document.getElementById('post-cvss').value = p.cvss_score;
            document.getElementById('post-severity').value = p.severity;
            document.getElementById('post-category').value = p.category;
            document.getElementById('post-image').value = p.image_url || '';
            document.getElementById('post-skus').value = p.related_skus || '';
            document.getElementById('post-read-time').value = p.read_time || '6 MIN READ';
            document.getElementById('post-ad-count').value = (p.ad_count !== undefined && p.ad_count !== null ? String(p.ad_count) : '1');
            document.getElementById('post-ad-placement').value = (p.ad_placement || 'MIDDLE');
            document.getElementById('post-ad-interval').value = (p.ad_paragraph_interval !== undefined && p.ad_paragraph_interval !== null ? String(p.ad_paragraph_interval) : '4');
            document.getElementById('post-ad-pitch').value = p.ad_custom_pitch || '';
            document.getElementById('post-summary').value = p.summary;
            document.getElementById('post-content').value = p.content;
            document.getElementById('post-meta-title').value = p.meta_title || '';
            document.getElementById('post-meta-desc').value = p.meta_desc || '';
            document.getElementById('post-meta-keywords').value = p.meta_keywords || '';
            document.getElementById('post-og-image').value = p.og_image || '';
            document.getElementById('modal-post').classList.add('is-open');
        }

        async function submitPost(e) {
            e.preventDefault();
            const id = document.getElementById('post-id').value;
            const payload = {
                title: document.getElementById('post-title').value.trim(),
                slug: document.getElementById('post-slug').value.trim(),
                cve_id: document.getElementById('post-cve').value.trim(),
                cvss_score: document.getElementById('post-cvss').value.trim(),
                severity: document.getElementById('post-severity').value,
                category: document.getElementById('post-category').value.trim(),
                image_url: document.getElementById('post-image').value.trim(),
                related_skus: document.getElementById('post-skus').value.trim(),
                read_time: document.getElementById('post-read-time').value.trim() || '6 MIN READ',
                ad_count: parseInt(document.getElementById('post-ad-count').value, 10) || 0,
                ad_placement: document.getElementById('post-ad-placement').value,
                ad_paragraph_interval: parseInt(document.getElementById('post-ad-interval').value, 10) || 4,
                ad_custom_pitch: document.getElementById('post-ad-pitch').value.trim(),
                summary: document.getElementById('post-summary').value.trim(),
                content: document.getElementById('post-content').value.trim(),
                meta_title: document.getElementById('post-meta-title').value.trim(),
                meta_desc: document.getElementById('post-meta-desc').value.trim(),
                meta_keywords: document.getElementById('post-meta-keywords').value.trim(),
                og_image: document.getElementById('post-og-image').value.trim(),
                author: 'ZERO//FORM RESEARCH LAB'
            };
            if (id) payload.id = parseInt(id, 10);

            const res = await fetch('/api/admin/posts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (data.ok || data.success) location.reload();
            else alert(data.error || 'Post save error');
        }

        async function deletePost(id, title) {
            if (!confirm('Permanently delete advisory: ' + title + '?')) return;
            try { sessionStorage.setItem('activeAdminTab', 'posts'); } catch(e) {}
            const res = await fetch('/api/admin/posts/' + id, { method: 'DELETE' });
            const data = await res.json();
            if (data.ok || data.success) location.reload();
            else alert(data.error || 'Delete error');
        }

        // ==========================================
        // USER RBAC & IDENTITY MANAGEMENT
        // ==========================================
