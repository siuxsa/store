        function switchThemeInspector(page, url, btn) {
            window.THEME_CURRENT_PAGE = page;
            window.THEME_CURRENT_URL = url;
            
            // Subnav buttons
            document.querySelectorAll('#mod-themes .subnav-btn').forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');

            // Hide/show panels
            document.querySelectorAll('.theme-subpanel').forEach(p => p.style.display = 'none');
            const targetPanel = document.getElementById('theme-panel-' + page);
            if (targetPanel) targetPanel.style.display = 'block';

            // Update status indicator
            const ind = document.getElementById('theme-active-indicator');
            if (ind) {
                if (page === 'seo') {
                    ind.textContent = 'ACTIVE: SEO & SOCIAL METADATA';
                } else {
                    ind.textContent = 'ACTIVE: ' + page.toUpperCase() + (page === 'global' ? ' SHELL' : ' PAGE');
                }
            }

            if (page === 'seo') {
                updateSeoLivePreview();
            }

            // Update preview url labels & links
            const urlLabel = document.getElementById('theme-preview-url-label');
            if (urlLabel) urlLabel.textContent = url + ' (' + page.toUpperCase() + ')';
            const extLink = document.getElementById('theme-open-external-btn');
            if (extLink) extLink.href = url;

            // Navigate iframe if needed
            if (previewIframe && previewIframe.contentWindow) {
                try {
                    const curPath = previewIframe.contentWindow.location.pathname;
                    if (curPath !== url) {
                        previewIframe.src = url;
                    }
                } catch(e) {
                    previewIframe.src = url;
                }
            }
        }

        let currentThemeDevice = 'desktop';
        let currentThemeScaleMode = 'fit';

        function applyThemeViewportDimensions() {
            const scaler = document.getElementById('theme-frame-scaler');
            const container = document.getElementById('theme-frame-container');
            const canvas = document.getElementById('theme-stage-canvas');
            if (!scaler || !container || !canvas) return;

            let targetWidth = 1280;
            let targetHeight = 740;

            if (currentThemeDevice === 'tablet') {
                targetWidth = 768;
                targetHeight = 840;
            } else if (currentThemeDevice === 'mobile') {
                targetWidth = 390;
                targetHeight = 740;
            }

            // Determine scale factor
            const availableWidth = Math.max(300, canvas.clientWidth - 48);
            let scale = 1.0;

            if (currentThemeDevice === 'desktop') {
                if (currentThemeScaleMode === 'fit') {
                    scale = Math.min(1.0, availableWidth / 1280);
                } else if (currentThemeScaleMode === '80') {
                    scale = 0.80;
                } else if (currentThemeScaleMode === '100') {
                    scale = 1.0;
                }
            } else if (currentThemeDevice === 'tablet') {
                scale = Math.min(1.0, availableWidth / 768);
            } else {
                scale = 1.0;
            }

            container.style.width = targetWidth + 'px';
            container.style.height = targetHeight + 'px';
            container.style.transform = `scale(${scale})`;
            container.style.transformOrigin = 'top center';

            scaler.style.width = Math.round(targetWidth * scale) + 'px';
            scaler.style.height = Math.round(targetHeight * scale) + 'px';
        }

        function setThemeDevice(mode, btn) {
            currentThemeDevice = mode;
            document.querySelectorAll('.theme-device-btn').forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');

            const container = document.getElementById('theme-frame-container');
            if (container) {
                container.className = 'theme-viewport-frame device-' + mode;
            }

            const scaleControls = document.getElementById('theme-scale-controls');
            if (scaleControls) {
                scaleControls.style.display = (mode === 'desktop') ? 'inline-flex' : 'none';
            }

            applyThemeViewportDimensions();
        }

        function setThemeScale(scaleMode, btn) {
            currentThemeScaleMode = scaleMode;
            document.querySelectorAll('.theme-scale-btn').forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');
            applyThemeViewportDimensions();
        }

        window.addEventListener('resize', () => {
            const activeMod = document.querySelector('.admin-module.active');
            if (activeMod && activeMod.id === 'mod-themes') {
                applyThemeViewportDimensions();
            }
        });

        function onThemeFieldInput(name, value) {
            // Update preview image box if applicable
            const previewImg = document.getElementById('preview-' + name);
            if (previewImg) {
                previewImg.src = value;
            }

            // Sync directly to embedded preview iframe DOM
            syncFieldToIframe(name, value);
        }

        function onColorControlSync(name, value) {
            // Synchronize all input representations of this color
            const picker = document.getElementById('picker-' + name);
            const text = document.getElementById('text-' + name);
            const quick = document.getElementById('quick-' + name);

            if (picker && picker.value !== value) picker.value = value;
            if (text && text.value !== value) text.value = value;
            if (quick && quick.value !== value) quick.value = value;

            onThemeFieldInput(name, value);
        }

        function applyColorPalettePreset(bg, text, dark, cyan, green, amber) {
            onColorControlSync('theme_bg_color', bg);
            onColorControlSync('theme_text_color', text);
            onColorControlSync('theme_dark_color', dark);
            onColorControlSync('accent_cyan_color', cyan);
            onColorControlSync('accent_green_color', green);
            onColorControlSync('accent_amber_color', amber);
        }

        function applyThemePreset(fieldName, url) {
            const input = document.querySelector(`.theme-field[name="${fieldName}"]`);
            if (input) {
                input.value = url;
                onThemeFieldInput(fieldName, url);
            }
        }

        function syncFieldToIframe(name, value) {
            if (name.startsWith('hero_cta_')) {
                updateHeroLiveButtons();
            }
            if (!previewIframe || !previewIframe.contentDocument) return;
            try {
                const doc = previewIframe.contentDocument;

                // Sync Theme CSS Variables directly to preview document :root
                if (name === 'theme_bg_color') {
                    doc.documentElement.style.setProperty('--bg', value);
                    if (doc.body) doc.body.style.backgroundColor = value;
                } else if (name === 'theme_text_color') {
                    doc.documentElement.style.setProperty('--text', value);
                    if (doc.body) doc.body.style.color = value;
                } else if (name === 'theme_dark_color') {
                    doc.documentElement.style.setProperty('--dark', value);
                } else if (name === 'accent_cyan_color') {
                    doc.documentElement.style.setProperty('--cyan', value);
                    doc.documentElement.style.setProperty('--accent-cyan', value);
                } else if (name === 'accent_green_color') {
                    doc.documentElement.style.setProperty('--green', value);
                    doc.documentElement.style.setProperty('--accent-green', value);
                } else if (name === 'accent_amber_color') {
                    doc.documentElement.style.setProperty('--amber', value);
                    doc.documentElement.style.setProperty('--accent-amber', value);
                } else if (name === 'font_family_sans') {
                    doc.documentElement.style.setProperty('--font-sans', value);
                } else if (name === 'font_family_mono') {
                    doc.documentElement.style.setProperty('--font-mono', value);
                } else if (name === 'custom_css_overrides') {
                    let customStyle = doc.getElementById('dynamic-custom-css-preview');
                    if (!customStyle) {
                        customStyle = doc.createElement('style');
                        customStyle.id = 'dynamic-custom-css-preview';
                        doc.head.appendChild(customStyle);
                    }
                    customStyle.textContent = value;
                }

                const targets = doc.querySelectorAll(`[data-theme-bind="${name}"]`);
                targets.forEach(el => {
                    if (el.tagName === 'IMG') {
                        el.src = value;
                    } else if (el.dataset.themeFormat === 'multiline') {
                        el.innerHTML = value.replace(/\n/g, '<br>');
                    } else {
                        el.textContent = value;
                    }
                });

                const hrefTargets = doc.querySelectorAll(`[data-theme-bind-href="${name}"]`);
                hrefTargets.forEach(el => {
                    el.href = value;
                });
            } catch(e) {
                // Cross-frame or loading state, ignore safely
            }
        }

        function updateHeroLiveButtons() {
            const pField = document.getElementById('field-hero_cta_primary');
            const pUrlField = document.getElementById('field-hero_cta_primary_url');
            const sField = document.getElementById('field-hero_cta_secondary');
            const sUrlField = document.getElementById('field-hero_cta_secondary_url');

            const pText = (pField ? pField.value.trim() : '') || 'EXPLORE ARSENAL';
            const pUrl = (pUrlField ? pUrlField.value.trim() : '') || '/shop';
            const sText = (sField ? sField.value.trim() : '') || 'THREAT JOURNAL';
            const sUrl = (sUrlField ? sUrlField.value.trim() : '') || '/journal';

            const pTextEl = document.getElementById('sim-hero-primary-text');
            const pBtnEl = document.getElementById('sim-hero-primary-btn');
            const sTextEl = document.getElementById('sim-hero-secondary-text');
            const sBtnEl = document.getElementById('sim-hero-secondary-btn');

            if (pTextEl) pTextEl.textContent = pText.replace(/→/g, '').trim();
            if (pBtnEl) pBtnEl.href = pUrl;
            if (sTextEl) sTextEl.textContent = sText.replace(/→/g, '').trim();
            if (sBtnEl) sBtnEl.href = sUrl;
        }

        function onThemeIframeLoaded() {
            // Apply all current input states into the newly loaded iframe
            document.querySelectorAll('.theme-field').forEach(field => {
                if (field.name && field.value !== undefined) {
                    syncFieldToIframe(field.name, field.value);
                }
            });
            // Also sync quick visual color pickers
            ['theme_bg_color', 'theme_text_color', 'theme_dark_color', 'accent_cyan_color', 'accent_green_color', 'accent_amber_color'].forEach(colorName => {
                const el = document.getElementById('text-' + colorName) || document.getElementById('picker-' + colorName) || document.getElementById('quick-' + colorName);
                if (el && el.value) {
                    syncFieldToIframe(colorName, el.value);
                }
            });
            setupIframeInspectListeners();
        }

        function refreshThemePreview() {
            if (previewIframe && previewIframe.contentWindow) {
                try {
                    previewIframe.contentWindow.location.reload();
                } catch(e) {
                    previewIframe.src = window.THEME_CURRENT_URL || '/';
                }
            }
        }

        // ==========================================
        // POINT & CLICK VISUAL INSPECTOR & POPUP
        // ==========================================
        window.THEME_INSPECT_MODE = true;
        let inspectorCollapsed = false;

        const THEME_FIELD_META = {
            // Header & Navigation
            site_name: { label: "Site Brand Callsign", page: "global", type: "text" },
            site_tagline: { label: "Site Tagline", page: "global", type: "text" },
            ticker_text: { label: "Announcement Ticker Text", page: "global", type: "multiline" },
            ticker_subtext: { label: "Ticker Dispatch Notice", page: "global", type: "text" },
            nav_shop_label: { label: "Nav 'Arsenal' Label", page: "global", type: "text" },
            nav_blog_label: { label: "Nav 'Threat Intel' Label", page: "global", type: "text" },
            nav_orders_label: { label: "Nav 'Order Lookup' Label", page: "global", type: "text" },
            nav_about_label: { label: "Nav 'About' Label", page: "global", type: "text" },
            telegram_user: { label: "Telegram Concierge Handle", page: "global", type: "text" },
            telegram_channel: { label: "Telegram Channel Link", page: "global", type: "text" },
            telegram_msg_prefix: { label: "Telegram Order Message Prefix", page: "global", type: "multiline" },

            // Home Page
            hero_badge: { label: "Hero Eyebrow Badge", page: "home", type: "text" },
            hero_title: { label: "Hero Main Headline", page: "home", type: "multiline" },
            hero_subtitle: { label: "Hero Elevator Subtitle", page: "home", type: "multiline" },
            hero_cta_primary: { label: "Hero Primary CTA Button Label", page: "home", type: "text" },
            hero_cta_primary_url: { label: "Hero Primary CTA Target URL", page: "home", type: "text" },
            hero_cta_secondary: { label: "Hero Sub-Button CTA Label", page: "home", type: "text" },
            hero_cta_secondary_url: { label: "Hero Sub-Button Target URL", page: "home", type: "text" },
            hero_image: { label: "Hero Cover Key Art Image", page: "home", type: "image" },
            manifesto_eyebrow: { label: "Manifesto Section Eyebrow", page: "home", type: "text" },
            manifesto_sublabel: { label: "Manifesto Sublabel / Year", page: "home", type: "text" },
            manifesto_title: { label: "Manifesto Section Headline", page: "home", type: "multiline" },
            manifesto_lead: { label: "Manifesto Lead Paragraph", page: "home", type: "multiline" },
            featured_eyebrow: { label: "Featured Section Eyebrow", page: "home", type: "text" },
            featured_title: { label: "Featured Section Title", page: "home", type: "text" },
            featured_cta: { label: "Featured View All Button", page: "home", type: "text" },

            // Category Strip One-Line Text
            category_strip_text: { label: "Category Strip One-Line Text", page: "home", type: "text" },

            // Homepage Showcase Curation (4 Products & 4 Journals)
            home_featured_product_1: { label: "Homepage Product Slot 1", page: "home", type: "text" },
            home_featured_product_2: { label: "Homepage Product Slot 2", page: "home", type: "text" },
            home_featured_product_3: { label: "Homepage Product Slot 3", page: "home", type: "text" },
            home_featured_product_4: { label: "Homepage Product Slot 4", page: "home", type: "text" },
            home_featured_post_1: { label: "Homepage Journal Slot 1", page: "home", type: "text" },
            home_featured_post_2: { label: "Homepage Journal Slot 2", page: "home", type: "text" },
            home_featured_post_3: { label: "Homepage Journal Slot 3", page: "home", type: "text" },
            home_featured_post_4: { label: "Homepage Journal Slot 4", page: "home", type: "text" },

            showcase_eyebrow: { label: "Showcase Section Eyebrow", page: "home", type: "text" },
            showcase_title: { label: "Showcase Section Headline", page: "home", type: "multiline" },
            showcase_desc: { label: "Showcase Description", page: "home", type: "multiline" },
            showcase_stat1_val: { label: "Metric 01 Value", page: "home", type: "text" },
            showcase_stat1_label: { label: "Metric 01 Subtitle", page: "home", type: "text" },
            showcase_stat2_val: { label: "Metric 02 Value", page: "home", type: "text" },
            showcase_stat2_label: { label: "Metric 02 Subtitle", page: "home", type: "text" },
            showcase_stat3_val: { label: "Metric 03 Value", page: "home", type: "text" },
            showcase_stat3_label: { label: "Metric 03 Subtitle", page: "home", type: "text" },
            journal_section_eyebrow: { label: "Home Journal Eyebrow", page: "home", type: "text" },
            journal_section_title: { label: "Home Journal Title", page: "home", type: "text" },
            journal_section_cta: { label: "Home Journal View Button", page: "home", type: "text" },

            // About Page
            about_eyebrow: { label: "About Page Eyebrow", page: "about", type: "text" },
            about_title: { label: "About Page Main Headline", page: "about", type: "multiline" },
            about_desc: { label: "About Page Elevator Description", page: "about", type: "multiline" },
            about_banner_image: { label: "About Page Key Art Banner", page: "about", type: "image" },
            about_banner_badge: { label: "About Banner Badge Tag", page: "about", type: "text" },
            about_banner_title: { label: "About Banner Headline", page: "about", type: "text" },
            about_banner_meta: { label: "About Key Art Sublabel", page: "about", type: "text" },
            about_tenet1_eyebrow: { label: "Tenet 01 Eyebrow", page: "about", type: "text" },
            about_tenet1_title: { label: "Tenet 01 Title", page: "about", type: "text" },
            about_tenet1_desc: { label: "Tenet 01 Description", page: "about", type: "multiline" },
            about_tenet1_tag: { label: "Tenet 01 Footer Tag", page: "about", type: "text" },
            about_tenet2_eyebrow: { label: "Tenet 02 Eyebrow", page: "about", type: "text" },
            about_tenet2_title: { label: "Tenet 02 Title", page: "about", type: "text" },
            about_tenet2_desc: { label: "Tenet 02 Description", page: "about", type: "multiline" },
            about_tenet2_tag: { label: "Tenet 02 Footer Tag", page: "about", type: "text" },
            about_tenet3_eyebrow: { label: "Tenet 03 Eyebrow", page: "about", type: "text" },
            about_tenet3_title: { label: "Tenet 03 Title", page: "about", type: "text" },
            about_tenet3_desc: { label: "Tenet 03 Description", page: "about", type: "multiline" },
            about_tenet3_tag: { label: "Tenet 03 Footer Tag", page: "about", type: "text" },
            about_metrics_eyebrow: { label: "About Metrics Eyebrow", page: "about", type: "text" },
            about_metric1_val: { label: "About Metric 01 Value", page: "about", type: "text" },
            about_metric1_title: { label: "About Metric 01 Title", page: "about", type: "text" },
            about_metric1_desc: { label: "About Metric 01 Description", page: "about", type: "multiline" },
            about_metric2_val: { label: "About Metric 02 Value", page: "about", type: "text" },
            about_metric2_title: { label: "About Metric 02 Title", page: "about", type: "text" },
            about_metric2_desc: { label: "About Metric 02 Description", page: "about", type: "multiline" },
            about_metric3_val: { label: "About Metric 03 Value", page: "about", type: "text" },
            about_metric3_title: { label: "About Metric 03 Title", page: "about", type: "text" },
            about_metric3_desc: { label: "About Metric 03 Description", page: "about", type: "multiline" },
            about_metric4_val: { label: "About Metric 04 Value", page: "about", type: "text" },
            about_metric4_title: { label: "About Metric 04 Title", page: "about", type: "text" },
            about_metric4_desc: { label: "About Metric 04 Description", page: "about", type: "multiline" },
            about_cta_eyebrow: { label: "About Bottom CTA Eyebrow", page: "about", type: "text" },
            about_cta_title: { label: "About Bottom CTA Headline", page: "about", type: "text" },
            about_cta_desc: { label: "About Bottom CTA Description", page: "about", type: "multiline" },
            about_cta_btn1: { label: "About Primary CTA Button", page: "about", type: "text" },
            about_cta_btn2: { label: "About Secondary CTA Button", page: "about", type: "text" },

            // Catalog & Journal Pages
            shop_eyebrow: { label: "Arsenal Catalog Eyebrow", page: "shop", type: "text" },
            shop_title: { label: "Arsenal Catalog Headline", page: "shop", type: "text" },
            shop_subtitle: { label: "Arsenal Catalog Subtitle", page: "shop", type: "multiline" },
            journal_eyebrow: { label: "Threat Journal Eyebrow", page: "journal", type: "text" },
            journal_title: { label: "Threat Journal Headline", page: "journal", type: "text" },
            journal_subtitle: { label: "Threat Journal Subtitle", page: "journal", type: "multiline" },

            // Global Footer
            footer_desc: { label: "Footer Brand Description", page: "global", type: "multiline" },
            footer_disclaimer: { label: "Footer Compliance Disclaimer", page: "global", type: "multiline" },
            footer_motto: { label: "Footer Edition & Motto", page: "global", type: "multiline" },
            footer_col1_title: { label: "Footer Column 01 Title", page: "global", type: "text" },
            footer_col2_title: { label: "Footer Column 02 Title", page: "global", type: "text" },
            footer_col3_title: { label: "Footer Column 03 Title", page: "global", type: "text" },
            footer_telegram_desc: { label: "Footer Concierge Description", page: "global", type: "multiline" },
            footer_badge: { label: "Footer Security Badge", page: "global", type: "text" },

            // Dedicated SEO & Social Metadata
            seo_meta_title: { label: "Global SEO Meta Title", page: "seo", type: "text" },
            seo_meta_description: { label: "Global SEO Meta Description", page: "seo", type: "multiline" },
            seo_meta_keywords: { label: "Global SEO Search Keywords", page: "seo", type: "text" },
            seo_og_image: { label: "Global Social Share / OG Image", page: "seo", type: "image" },

            seo_home_title: { label: "Home Page SEO Title", page: "seo", type: "text" },
            seo_home_desc: { label: "Home Page SEO Description", page: "seo", type: "multiline" },
            seo_home_keywords: { label: "Home Page SEO Keywords", page: "seo", type: "text" },
            seo_home_image: { label: "Home Page Social OG Image", page: "seo", type: "image" },

            seo_about_title: { label: "About Page SEO Title", page: "seo", type: "text" },
            seo_about_desc: { label: "About Page SEO Description", page: "seo", type: "multiline" },
            seo_about_keywords: { label: "About Page SEO Keywords", page: "seo", type: "text" },
            seo_about_image: { label: "About Page Social OG Image", page: "seo", type: "image" },

            seo_shop_title: { label: "Arsenal Catalog SEO Title", page: "seo", type: "text" },
            seo_shop_desc: { label: "Arsenal Catalog SEO Description", page: "seo", type: "multiline" },
            seo_shop_keywords: { label: "Arsenal Catalog SEO Keywords", page: "seo", type: "text" },
            seo_shop_image: { label: "Arsenal Catalog Social OG Image", page: "seo", type: "image" },

            seo_journal_title: { label: "Threat Journal SEO Title", page: "seo", type: "text" },
            seo_journal_desc: { label: "Threat Journal SEO Description", page: "seo", type: "multiline" },
            seo_journal_keywords: { label: "Threat Journal SEO Keywords", page: "seo", type: "text" },
            seo_journal_image: { label: "Threat Journal Social OG Image", page: "seo", type: "image" }
        };

        function toggleInspectorPane() {
            inspectorCollapsed = !inspectorCollapsed;
            const grid = document.querySelector('.theme-studio-grid');
            const showBtn = document.getElementById('btn-show-inspector');
            if (grid) {
                if (inspectorCollapsed) {
                    grid.classList.add('inspector-collapsed');
                    if (showBtn) showBtn.style.display = 'inline-flex';
                } else {
                    grid.classList.remove('inspector-collapsed');
                    if (showBtn) showBtn.style.display = 'none';
                }
            }
            setTimeout(applyThemeViewportDimensions, 260);
        }

        function toggleInspectMode() {
            window.THEME_INSPECT_MODE = !window.THEME_INSPECT_MODE;
            const btn = document.getElementById('btn-inspect-mode');
            const txt = document.getElementById('inspect-mode-text');
            if (btn && txt) {
                if (window.THEME_INSPECT_MODE) {
                    btn.classList.remove('off');
                    txt.textContent = 'INSPECT & EDIT: ON';
                } else {
                    btn.classList.add('off');
                    txt.textContent = 'INSPECT & EDIT: OFF';
                }
            }
            setupIframeInspectListeners();
        }

        function setupIframeInspectListeners() {
            if (!previewIframe) return;
            let doc = null;
            try {
                doc = previewIframe.contentDocument || (previewIframe.contentWindow ? previewIframe.contentWindow.document : null);
            } catch(e) {
                console.warn('Iframe doc access error:', e);
                return;
            }
            if (!doc || !doc.body) {
                setTimeout(setupIframeInspectListeners, 100);
                return;
            }

            try {
                // Ensure inspect stylesheet is injected
                let styleTag = doc.getElementById('theme-inspect-style');
                if (!styleTag) {
                    styleTag = doc.createElement('style');
                    styleTag.id = 'theme-inspect-style';
                    styleTag.textContent = `
                        body.inspect-mode-active [data-theme-bind] {
                            cursor: pointer !important;
                        }
                        body.inspect-mode-active .hero-overlay {
                            pointer-events: none !important;
                        }
                        .theme-inspectable-hover {
                            outline: 2px dashed #00e5ff !important;
                            outline-offset: 3px !important;
                            background-color: rgba(0, 229, 255, 0.12) !important;
                            cursor: pointer !important;
                            transition: outline 0.12s ease !important;
                        }
                        #theme-inspect-floating-pill {
                            position: absolute;
                            z-index: 2147483647;
                            background: #00e5ff;
                            color: #050608;
                            font-family: 'JetBrains Mono', monospace, -apple-system, sans-serif;
                            font-size: 11px;
                            font-weight: 800;
                            padding: 3px 8px;
                            border-radius: 2px;
                            pointer-events: none;
                            letter-spacing: 0.05em;
                            box-shadow: 0 4px 14px rgba(0,0,0,0.75), 0 0 10px rgba(0,229,255,0.4);
                            display: none;
                            text-transform: uppercase;
                            white-space: nowrap;
                        }
                    `;
                    doc.head.appendChild(styleTag);
                }

                // Ensure floating pill exists in doc.body
                let pill = doc.getElementById('theme-inspect-floating-pill');
                if (!pill) {
                    pill = doc.createElement('div');
                    pill.id = 'theme-inspect-floating-pill';
                    doc.body.appendChild(pill);
                }

                // Toggle inspect-mode-active on iframe body
                if (window.THEME_INSPECT_MODE) {
                    doc.body.classList.add('inspect-mode-active');
                } else {
                    doc.body.classList.remove('inspect-mode-active');
                    doc.querySelectorAll('.theme-inspectable-hover').forEach(el => el.classList.remove('theme-inspectable-hover'));
                    if (pill) pill.style.display = 'none';
                }

                // Attach capturing event listeners once per document instance
                if (!doc.__inspectListenersAttached) {
                    doc.__inspectListenersAttached = true;

                    let currentHoveredEl = null;

                    function findInspectableTarget(target) {
                        if (!target || target === doc.body || target === doc.documentElement) return null;
                        let found = target.closest('[data-theme-bind]');
                        if (!found) {
                            if (target.closest('.hero-media') || target.classList.contains('hero-section')) {
                                if (!target.closest('.hero-content') && !target.closest('.hero-actions')) {
                                    found = doc.querySelector('[data-theme-bind="hero_image"]');
                                }
                            } else if (target.closest('.about-banner-container')) {
                                if (!target.closest('.about-banner-glass')) {
                                    found = doc.querySelector('[data-theme-bind="about_banner_image"]');
                                }
                            }
                        }
                        return found;
                    }

                    // Capturing click listener
                    doc.addEventListener('click', function(e) {
                        if (!window.THEME_INSPECT_MODE) return;

                        const target = findInspectableTarget(e.target);
                        if (target) {
                            e.preventDefault();
                            e.stopPropagation();
                            e.stopImmediatePropagation();

                            const key = target.getAttribute('data-theme-bind');
                            if (key) {
                                target.classList.remove('theme-inspectable-hover');
                                if (pill) pill.style.display = 'none';
                                currentHoveredEl = null;
                                openQuickEditModal(key);
                            }
                        }
                    }, true);

                    // Capturing mouseover listener
                    doc.addEventListener('mouseover', function(e) {
                        if (!window.THEME_INSPECT_MODE) return;

                        const target = findInspectableTarget(e.target);
                        if (target === currentHoveredEl) return;

                        if (currentHoveredEl && currentHoveredEl !== target) {
                            currentHoveredEl.classList.remove('theme-inspectable-hover');
                            currentHoveredEl = null;
                        }

                        if (target) {
                            currentHoveredEl = target;
                            target.classList.add('theme-inspectable-hover');
                            const key = target.getAttribute('data-theme-bind');
                            const meta = THEME_FIELD_META[key] || { label: key };

                            pill.textContent = 'EDIT: ' + (meta.label || key).toUpperCase();
                            pill.style.display = 'block';

                            const rect = target.getBoundingClientRect();
                            const scrollX = doc.defaultView.pageXOffset || doc.documentElement.scrollLeft || 0;
                            const scrollY = doc.defaultView.pageYOffset || doc.documentElement.scrollTop || 0;

                            let topPos = rect.top + scrollY - 26;
                            if (topPos < 5) topPos = rect.bottom + scrollY + 6;
                            let leftPos = Math.max(10, rect.left + scrollX);

                            pill.style.top = topPos + 'px';
                            pill.style.left = leftPos + 'px';
                        } else {
                            if (pill) pill.style.display = 'none';
                        }
                    }, true);

                    // Capturing mouseout listener
                    doc.addEventListener('mouseout', function(e) {
                        if (!window.THEME_INSPECT_MODE) return;
                        if (currentHoveredEl && (!e.relatedTarget || !currentHoveredEl.contains(e.relatedTarget))) {
                            currentHoveredEl.classList.remove('theme-inspectable-hover');
                            currentHoveredEl = null;
                            if (pill) pill.style.display = 'none';
                        }
                    }, true);
                }
            } catch(err) {
                console.warn('Inspect listener setup warning:', err);
            }
        }

        function openQuickEditModal(key) {
            console.log('Visual Inspector: Opening quick edit modal for:', key);
            const meta = THEME_FIELD_META[key] || { label: key, page: 'theme', type: 'text' };
            const inputField = document.querySelector(`.theme-field[name="${key}"]`);
            
            let currentVal = '';
            if (inputField && inputField.value !== undefined) {
                currentVal = inputField.value;
            } else if (window.ORIGINAL_THEME_SETTINGS && window.ORIGINAL_THEME_SETTINGS[key] !== undefined) {
                currentVal = window.ORIGINAL_THEME_SETTINGS[key];
            } else if (previewIframe && previewIframe.contentDocument) {
                const el = previewIframe.contentDocument.querySelector(`[data-theme-bind="${key}"]`);
                if (el) {
                    currentVal = el.tagName === 'IMG' ? el.src : (el.innerText || el.textContent || '').trim();
                }
            }

            const keyInput = document.getElementById('quick-edit-field-key');
            const typeInput = document.getElementById('quick-edit-field-type');
            const contextEl = document.getElementById('quick-edit-context');
            const titleEl = document.getElementById('quick-edit-title');

            if (keyInput) keyInput.value = key;
            if (typeInput) typeInput.value = meta.type;
            if (contextEl) contextEl.innerHTML = `<span class="live-pulse" style="background:#00e5ff; box-shadow:0 0 8px #00e5ff;"></span> INSPECT &amp; EDIT // ${(meta.page || 'THEME').toUpperCase()}`;
            if (titleEl) titleEl.textContent = meta.label || key;

            // Hide all input wrappers initially
            const inWrap = document.getElementById('quick-edit-input-wrap');
            const txtWrap = document.getElementById('quick-edit-textarea-wrap');
            const imgWrap = document.getElementById('quick-edit-image-wrap');

            if (inWrap) inWrap.style.display = 'none';
            if (txtWrap) txtWrap.style.display = 'none';
            if (imgWrap) imgWrap.style.display = 'none';

            if (meta.type === 'image') {
                const imgInput = document.getElementById('quick-edit-image-url');
                const imgPreview = document.getElementById('quick-edit-img-preview');
                const imgLabel = document.getElementById('quick-edit-image-label');
                if (imgLabel) imgLabel.textContent = `${(meta.label || 'IMAGE').toUpperCase()} URL`;
                if (imgInput) imgInput.value = currentVal;
                if (imgPreview) imgPreview.src = currentVal;
                if (imgWrap) imgWrap.style.display = 'block';
                if (imgInput) setTimeout(() => imgInput.focus(), 50);
            } else if (meta.type === 'multiline') {
                const textArea = document.getElementById('quick-edit-textarea');
                const textLabel = document.getElementById('quick-edit-textarea-label');
                if (textLabel) textLabel.textContent = (meta.label || 'CONTENT').toUpperCase();
                if (textArea) textArea.value = currentVal;
                if (txtWrap) txtWrap.style.display = 'block';
                if (textArea) setTimeout(() => textArea.focus(), 50);
            } else {
                const singleInput = document.getElementById('quick-edit-input');
                const singleLabel = document.getElementById('quick-edit-input-label');
                if (singleLabel) singleLabel.textContent = (meta.label || 'LABEL').toUpperCase();
                if (singleInput) singleInput.value = currentVal;
                if (inWrap) inWrap.style.display = 'block';
                if (singleInput) setTimeout(() => singleInput.focus(), 50);
            }

            openModal('modal-theme-element');
        }
        window.openQuickEditModal = openQuickEditModal;

        function onQuickEditFieldInput(val) {
            const key = document.getElementById('quick-edit-field-key').value;
            if (!key) return;

            // Update in left inspector pane
            const inputField = document.querySelector(`.theme-field[name="${key}"]`);
            if (inputField) inputField.value = val;

            // Live sync to preview iframe
            syncFieldToIframe(key, val);
        }

        function onQuickEditImageInput(url) {
            const key = document.getElementById('quick-edit-field-key').value;
            const imgPreview = document.getElementById('quick-edit-img-preview');
            if (imgPreview) imgPreview.src = url;

            const inputField = document.querySelector(`.theme-field[name="${key}"]`);
            if (inputField) inputField.value = url;

            const inspectorPreview = document.getElementById('preview-' + key);
            if (inspectorPreview) inspectorPreview.src = url;

            syncFieldToIframe(key, url);
        }

        function applyQuickEditPreset(url) {
            const imgInput = document.getElementById('quick-edit-image-url');
            if (imgInput) imgInput.value = url;
            onQuickEditImageInput(url);
        }

        async function handleImageFileUpload(fileInput, targetMode, targetId) {
            if (!fileInput.files || !fileInput.files[0]) return;
            const file = fileInput.files[0];
            const formData = new FormData();
            formData.append('file', file);

            const statusEl = document.getElementById('quick-edit-upload-status');
            const btnText = document.getElementById('quick-edit-upload-text');
            const origBtnText = btnText ? btnText.textContent : 'UPLOAD FILE';

            if (statusEl) statusEl.style.display = 'inline-block';
            if (btnText) btnText.textContent = 'UPLOADING...';

            try {
                const res = await fetch('/api/admin/upload-image', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json();
                if (data.ok && data.url) {
                    if (targetMode === 'quick-edit') {
                        const urlInput = document.getElementById('quick-edit-image-url');
                        if (urlInput) urlInput.value = data.url;
                        onQuickEditImageInput(data.url);
                    } else if (targetMode === 'field') {
                        const input = document.querySelector(`.theme-field[name="${targetId}"]`);
                        if (input) {
                            input.value = data.url;
                            onThemeFieldInput(targetId, data.url);
                        }
                        const preview = document.getElementById('preview-' + targetId);
                        if (preview) preview.src = data.url;
                    } else if (targetMode === 'product') {
                        const prodImg = document.getElementById('prod-image');
                        if (prodImg) prodImg.value = data.url;
                    } else if (targetMode === 'product-og') {
                        const prodOg = document.getElementById('prod-og-image');
                        if (prodOg) prodOg.value = data.url;
                    } else if (targetMode === 'post') {
                        const postImg = document.getElementById('post-image');
                        if (postImg) postImg.value = data.url;
                    } else if (targetMode === 'post-og') {
                        const postOg = document.getElementById('post-og-image');
                        if (postOg) postOg.value = data.url;
                    } else if (targetMode === 'settings-seo') {
                        const sInput = document.getElementById('settings-seo_og_image');
                        if (sInput) sInput.value = data.url;
                        const sPrev = document.getElementById('settings-preview-seo_og_image');
                        if (sPrev) sPrev.src = data.url;
                    } else if (targetMode === 'pse-cover') {
                        const inEl = document.getElementById('pse-image');
                        if (inEl) { inEl.value = data.url; updateProductCoverPreview(data.url); updateProductPreview(); }
                    } else if (targetMode === 'pse-seo-og') {
                        const inEl = document.getElementById('pse-og-image');
                        if (inEl) { inEl.value = data.url; updateProductOgPreview(data.url); }
                    } else if (targetMode === 'jse-banner') {
                        const inEl = document.getElementById('jse-image');
                        if (inEl) { inEl.value = data.url; updatePostCoverPreview(data.url); updatePostPreview(); }
                    } else if (targetMode === 'jse-seo-og') {
                        const inEl = document.getElementById('jse-og-image');
                        if (inEl) { inEl.value = data.url; updatePostOgPreview(data.url); }
                    } else if (targetMode === 'pse-ad-bg') {
                        const inEl = document.getElementById('pse-ad-image');
                        if (inEl) { inEl.value = data.url; updateProductAdPreview(); }
                    } else if (targetMode === 'product-ad-bg') {
                        const inEl = document.getElementById('prod-ad-image');
                        if (inEl) inEl.value = data.url;
                    }
                    showThemeToast(`UPLOAD COMPLETE: ${data.filename} applied.`);
                } else {
                    alert('Upload failed: ' + (data.error || 'Server error'));
                }
            } catch(err) {
                alert('Upload error: ' + err.message);
            } finally {
                if (statusEl) statusEl.style.display = 'none';
                if (btnText) btnText.textContent = origBtnText;
                fileInput.value = '';
            }
        }

        window.CURRENT_SEO_PANE = 'global';

        function switchSeoPageTab(paneKey, btn) {
            window.CURRENT_SEO_PANE = paneKey;
            document.querySelectorAll('.seo-page-pane').forEach(el => el.style.display = 'none');
            document.querySelectorAll('.seo-page-subnav-btn').forEach(el => el.classList.remove('active'));

            const target = document.getElementById('seo-pane-' + paneKey);
            if (target) target.style.display = 'block';
            if (btn) btn.classList.add('active');

            const badge = document.getElementById('serp-preview-badge');
            const urlEl = document.getElementById('serp-preview-url');

            const pageUrls = {
                'global': 'https://matrix.security/',
                'home': 'https://matrix.security/',
                'about': 'https://matrix.security/about',
                'shop': 'https://matrix.security/shop',
                'journal': 'https://matrix.security/journal'
            };

            if (badge) badge.textContent = paneKey.toUpperCase() + (paneKey === 'global' ? ' FALLBACK' : ' PAGE');
            if (urlEl) urlEl.textContent = pageUrls[paneKey] || 'https://matrix.security/';

            updateSeoLivePreview();
        }

        function updateSeoLivePreview() {
            const pane = window.CURRENT_SEO_PANE || 'global';
            let titleName = 'seo_meta_title';
            let descName = 'seo_meta_description';

            if (pane !== 'global') {
                titleName = `seo_${pane}_title`;
                descName = `seo_${pane}_desc`;
            }

            const titleInput = document.querySelector(`.theme-field[name="${titleName}"]`);
            const descInput = document.querySelector(`.theme-field[name="${descName}"]`);
            const globalTitleInput = document.querySelector('.theme-field[name="seo_meta_title"]');
            const globalDescInput = document.querySelector('.theme-field[name="seo_meta_description"]');

            const serpTitle = document.getElementById('serp-preview-title');
            const serpDesc = document.getElementById('serp-preview-desc');

            let titleVal = (titleInput ? titleInput.value.trim() : '') || (globalTitleInput ? globalTitleInput.value.trim() : '') || '{{ site_settings.site_name }} // Security Systems';
            let descVal = (descInput ? descInput.value.trim() : '') || (globalDescInput ? globalDescInput.value.trim() : '') || '{{ site_settings.site_tagline }}';

            if (serpTitle) serpTitle.textContent = titleVal;
            if (serpDesc) serpDesc.textContent = descVal;

            // Update character count badges across all inputs
            ['global', 'home', 'about', 'shop', 'journal'].forEach(p => {
                const tName = p === 'global' ? 'seo_meta_title' : `seo_${p}_title`;
                const dName = p === 'global' ? 'seo_meta_description' : `seo_${p}_desc`;
                const tIn = document.querySelector(`.theme-field[name="${tName}"]`);
                const dIn = document.querySelector(`.theme-field[name="${dName}"]`);
                const cT = document.getElementById(`count-${p}-title`);
                const cD = document.getElementById(`count-${p}-desc`);

                if (tIn && cT) {
                    const len = tIn.value.trim().length;
                    cT.textContent = len ? `${len}/60 chars` : 'AUTO-FALLBACK';
                }
                if (dIn && cD) {
                    const len = dIn.value.trim().length;
                    cD.textContent = len ? `${len}/160 chars` : 'AUTO-FALLBACK';
                }
            });
        }

        async function submitQuickEdit(e) {
            e.preventDefault();
            const key = document.getElementById('quick-edit-field-key').value;
            const type = document.getElementById('quick-edit-field-type').value;
            const meta = THEME_FIELD_META[key] || { label: key };
            const saveBtn = document.getElementById('btn-quick-edit-save');
            const origText = saveBtn ? saveBtn.textContent : 'APPLY & SAVE →';

            let val = '';
            if (type === 'image') {
                val = document.getElementById('quick-edit-image-url').value;
            } else if (type === 'multiline') {
                val = document.getElementById('quick-edit-textarea').value;
            } else {
                val = document.getElementById('quick-edit-input').value;
            }

            if (saveBtn) {
                saveBtn.textContent = 'SAVING...';
                saveBtn.disabled = true;
            }

            try {
                const res = await fetch('/api/admin/theme', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ [key]: val })
                });
                const data = await res.json();
                if (data.ok || data.success) {
                    if (window.ORIGINAL_THEME_SETTINGS) {
                        window.ORIGINAL_THEME_SETTINGS[key] = val;
                    }
                    const inputField = document.querySelector(`.theme-field[name="${key}"]`);
                    if (inputField) inputField.value = val;
                    syncFieldToIframe(key, val);

                    closeModal('modal-theme-element');
                    showThemeToast(`UPDATED: ${meta.label || key} saved live to database.`);
                } else {
                    alert('Save failed: ' + (data.error || data.message || 'Error'));
                }
            } catch(err) {
                alert('Save error: ' + err.message);
            } finally {
                if (saveBtn) {
                    saveBtn.textContent = origText;
                    saveBtn.disabled = false;
                }
            }
        }

        function showThemeToast(msg) {
            const toast = document.getElementById('theme-toast');
            if (!toast) return;
            const iconSvg = '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="vertical-align:-1px; margin-right:6px;"><polyline points="20 6 9 17 4 12"/></svg>';
            toast.innerHTML = iconSvg + (msg || 'THEME CONFIGURATION PERSISTED TO RUNTIME DATABASE');
            toast.style.display = 'inline-flex';
            toast.style.alignItems = 'center';
            setTimeout(() => {
                toast.style.display = 'none';
            }, 3800);
        }

        async function saveThemeStudio() {
            const saveBtn = document.getElementById('btn-save-theme');
            const quickSaveBtn = document.getElementById('btn-save-colors-quick');
            const originalText = saveBtn ? saveBtn.textContent : 'SAVE ALL THEME CHANGES →';
            if (saveBtn) {
                saveBtn.textContent = 'PERSISTING CHANGES...';
                saveBtn.disabled = true;
            }
            if (quickSaveBtn) {
                quickSaveBtn.textContent = 'SAVING...';
                quickSaveBtn.disabled = true;
            }

            const payload = {};
            document.querySelectorAll('.theme-field').forEach(input => {
                if (input.name) {
                    payload[input.name] = input.value;
                }
            });
            // Ensure all color settings are captured
            ['theme_bg_color', 'theme_text_color', 'theme_dark_color', 'accent_cyan_color', 'accent_green_color', 'accent_amber_color'].forEach(colorName => {
                const el = document.getElementById('text-' + colorName) || document.getElementById('quick-' + colorName) || document.getElementById('picker-' + colorName);
                if (el && el.value) {
                    payload[colorName] = el.value;
                }
            });

            try {
                const res = await fetch('/api/admin/theme', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (data.ok || data.success) {
                    window.ORIGINAL_THEME_SETTINGS = { ...window.ORIGINAL_THEME_SETTINGS, ...payload };
                    showThemeToast('THEME PERSISTED: All changes saved to database & live across all client sessions.');
                    refreshThemePreview();
                    if (saveBtn) saveBtn.textContent = 'SAVED SUCCESSFULLY';
                    if (quickSaveBtn) quickSaveBtn.textContent = 'SAVED ✓';
                    setTimeout(() => {
                        if (saveBtn) {
                            saveBtn.textContent = originalText;
                            saveBtn.disabled = false;
                        }
                        if (quickSaveBtn) {
                            quickSaveBtn.textContent = 'SAVE COLORS';
                            quickSaveBtn.disabled = false;
                        }
                    }, 2200);
                } else {
                    alert('Theme save failed: ' + (data.error || data.message || 'Unknown error'));
                    if (saveBtn) {
                        saveBtn.textContent = originalText;
                        saveBtn.disabled = false;
                    }
                    if (quickSaveBtn) {
                        quickSaveBtn.textContent = 'SAVE COLORS';
                        quickSaveBtn.disabled = false;
                    }
                }
            } catch(err) {
                alert('Network error while saving theme: ' + err.message);
                if (saveBtn) {
                    saveBtn.textContent = originalText;
                    saveBtn.disabled = false;
                }
                if (quickSaveBtn) {
                    quickSaveBtn.textContent = 'SAVE COLORS';
                    quickSaveBtn.disabled = false;
                }
            }
        }

        function resetThemeStudio() {
            if (!confirm('Revert all unsaved theme changes to the latest saved database state?')) return;
            if (!window.ORIGINAL_THEME_SETTINGS) return;

            document.querySelectorAll('.theme-field').forEach(input => {
                if (input.name && window.ORIGINAL_THEME_SETTINGS[input.name] !== undefined) {
                    input.value = window.ORIGINAL_THEME_SETTINGS[input.name];
                    const previewImg = document.getElementById('preview-' + input.name);
                    if (previewImg) previewImg.src = input.value;
                }
            });

            onThemeIframeLoaded();
            showThemeToast('REVERTED: Inspector fields reset to saved database values.');
        }

        function switchVisualCanvasPage(page, url, btn) {
            document.querySelectorAll('#mod-themes-visual .subnav-btn').forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');
            const urlLabel = document.getElementById('theme-preview-url-label');
            if (urlLabel) urlLabel.textContent = url + ' (' + page.toUpperCase() + ')';
            const extLink = document.getElementById('theme-open-external-btn');
            if (extLink) extLink.href = url;
            const iframe = document.getElementById('theme-preview-iframe');
            if (iframe) iframe.src = url;
        }

        function switchThemeTextTab(paneKey, btn) {
            document.querySelectorAll('.theme-text-subnav-btn').forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');
            document.querySelectorAll('.theme-text-pane').forEach(p => p.style.display = 'none');
            const target = document.getElementById('theme-text-pane-' + paneKey);
            if (target) target.style.display = 'block';
        }

        async function saveSeoStudio() {
            const saveBtn = document.getElementById('btn-save-seo');
            const originalText = saveBtn ? saveBtn.textContent : 'SAVE ALL SEO & METADATA';
            if (saveBtn) {
                saveBtn.textContent = 'PERSISTING SEO...';
                saveBtn.disabled = true;
            }

            const payload = {};
            document.querySelectorAll('#mod-seo .theme-field').forEach(input => {
                if (input.name) {
                    payload[input.name] = input.value;
                }
            });

            try {
                const res = await fetch('/api/admin/theme', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (data.ok || data.success) {
                    if (typeof showThemeToast === 'function') {
                        showThemeToast('SEO PERSISTED: SERP snippets & Social metadata updated live.');
                    }
                    if (saveBtn) saveBtn.textContent = 'SAVED SUCCESSFULLY';
                    setTimeout(() => {
                        if (saveBtn) {
                            saveBtn.textContent = originalText;
                            saveBtn.disabled = false;
                        }
                    }, 2200);
                } else {
                    alert('SEO save failed: ' + (data.error || 'Unknown error'));
                    if (saveBtn) {
                        saveBtn.textContent = originalText;
                        saveBtn.disabled = false;
                    }
                }
            } catch(err) {
                alert('Network error while saving SEO: ' + err.message);
                if (saveBtn) {
                    saveBtn.textContent = originalText;
                    saveBtn.disabled = false;
                }
            }
        }

        // ==========================================
        // VERIFIED REVIEWS MATRIX MANAGEMENT
        // ==========================================
