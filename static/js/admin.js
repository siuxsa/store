/**
 * ZERODAY // MATRIX — Admin Command Center & High-Contrast Canvas Analytics Engine
 * Palette:
 *   Deep Indigo: #17153D
 *   Royal Indigo: #2F2B75
 *   Acid Lime: #90E31F
 *   Cyber Volt: #C7FF5E
 *   Ice White: #F2F4FF
 */

(function () {
    "use strict";

    let currentAnalyticsDays = 14;
    let cachedAnalyticsData = null;

    // =========================================================================
    // 1. TAB NAVIGATION
    // =========================================================================
    function switchAdminTab(tabName) {
        const tabs = ["analytics", "blog", "products", "orders", "users", "settings"];
        tabs.forEach(function (t) {
            const panel = document.getElementById("admin-tab-" + t);
            const btn = document.getElementById("admin-btn-" + t);
            if (panel) {
                if (t === tabName) {
                    panel.classList.remove("hidden");
                } else {
                    panel.classList.add("hidden");
                }
            }
            if (btn) {
                if (t === tabName) {
                    btn.classList.add("bg-[#90E31F]", "text-[#17153D]", "border-[#90E31F]");
                    btn.classList.remove("bg-[#2F2B75]", "text-[#F2F4FF]");
                } else {
                    btn.classList.remove("bg-[#90E31F]", "text-[#17153D]", "border-[#90E31F]");
                    btn.classList.add("bg-[#2F2B75]", "text-[#F2F4FF]");
                }
            }
        });

        if (tabName === "analytics") {
            loadAnalyticsDashboard(currentAnalyticsDays);
        }
    }

    // =========================================================================
    // 2. ANALYTICS DASHBOARD & CUSTOM HTML5 CANVAS GRAPHS
    // =========================================================================
    function formatDuration(sec) {
        const s = Math.round(parseFloat(sec || 0));
        if (s < 60) return s + "s";
        const m = Math.floor(s / 60);
        const rem = s % 60;
        return m + "m " + rem + "s";
    }

    async function loadAnalyticsDashboard(days) {
        currentAnalyticsDays = days || 14;
        document.querySelectorAll(".analytics-range-btn").forEach(function (b) {
            const d = parseInt(b.getAttribute("data-days"), 10);
            if (d === currentAnalyticsDays) {
                b.className = "analytics-range-btn px-3 py-1 font-mono text-xs font-bold bg-[#90E31F] text-[#17153D] border border-[#90E31F]";
            } else {
                b.className = "analytics-range-btn px-3 py-1 font-mono text-xs bg-[#17153D] text-[#F2F4FF] border border-[#433E96] hover:border-[#90E31F]";
            }
        });

        try {
            const res = await fetch("/api/admin/analytics/summary?days=" + currentAnalyticsDays);
            const data = await res.json();
            cachedAnalyticsData = data;
            populateKpiCards(data.kpis);
            drawTimelineChart(data.timeline);
            drawProductDwellChart(data.products);
            drawBlogAdConversionChart(data.blogs);
            drawOsAndFunnelPanel(data.kpis, data.os_breakdown, data.referrers);
            populateAnalyticsTables(data.products, data.blogs, data.recent_stream);
        } catch (err) {
            console.error("Failed to load analytics:", err);
        }
    }

    function populateKpiCards(kpis) {
        const setTxt = function (id, val) {
            const el = document.getElementById(id);
            if (el) el.textContent = val;
        };

        setTxt("kpi-active-now", kpis.active_visitors_now);
        setTxt("kpi-total-views", kpis.total_views.toLocaleString());
        setTxt("kpi-unique-visitors", kpis.unique_visitors.toLocaleString() + " unique visitors");
        setTxt("kpi-avg-dwell", formatDuration(kpis.avg_dwell_seconds));
        setTxt("kpi-dwell-split", "Prod: " + formatDuration(kpis.avg_product_dwell) + " // Blog: " + formatDuration(kpis.avg_blog_dwell));

        const totalSec = Math.max(1, kpis.product_section_views + kpis.blog_section_views);
        const prodPct = Math.round((kpis.product_section_views / totalSec) * 100);
        const blogPct = 100 - prodPct;
        setTxt("kpi-traffic-split", prodPct + "% Store / " + blogPct + "% Blog");
        setTxt("kpi-scroll-avg", "Avg Scroll Completion: " + kpis.avg_scroll_pct + "%");

        setTxt("kpi-ad-ctr", kpis.smart_ad_ctr_pct + "% CTR");
        setTxt("kpi-ad-clicks", kpis.smart_ad_clicks + " Ad Clicks / " + kpis.smart_ad_impressions + " Impr");
        setTxt("kpi-tg-clicks", kpis.telegram_buy_clicks);
        setTxt("kpi-revenue", "$" + kpis.completed_revenue.toFixed(0) + " Paid ($" + kpis.pipeline_revenue.toFixed(0) + " Pipe)");
    }

    // Graph 1: Multi-Line Traffic & Conversion Timeline
    function drawTimelineChart(timeline) {
        const canvas = document.getElementById("chart-traffic-timeline");
        if (!canvas || !timeline) return;
        const ctx = canvas.getContext("2d");
        const dpr = window.devicePixelRatio || 1;
        const rect = canvas.parentElement.getBoundingClientRect();
        const width = Math.max(320, rect.width - 16);
        const height = 270;

        canvas.width = width * dpr;
        canvas.height = height * dpr;
        canvas.style.width = width + "px";
        canvas.style.height = height + "px";
        ctx.scale(dpr, dpr);

        ctx.clearRect(0, 0, width, height);

        const padL = 42, padR = 20, padT = 28, padB = 38;
        const plotW = width - padL - padR;
        const plotH = height - padT - padB;

        const labels = timeline.labels || [];
        const pViews = timeline.product_views || [];
        const bViews = timeline.blog_views || [];
        const tgConv = timeline.telegram_conversions || [];

        const maxVal = Math.max(10, ...pViews, ...bViews, ...tgConv);

        // Grid lines
        ctx.strokeStyle = "#433E96";
        ctx.lineWidth = 1;
        ctx.font = "11px 'JetBrains Mono', monospace";
        ctx.fillStyle = "#A5A3C8";

        for (let i = 0; i <= 4; i++) {
            const y = padT + (plotH * i) / 4;
            const val = Math.round(maxVal * (1 - i / 4));
            ctx.beginPath();
            ctx.moveTo(padL, y);
            ctx.lineTo(width - padR, y);
            ctx.stroke();
            ctx.fillText(String(val), 6, y + 4);
        }

        function plotSeries(arr, strokeColor, fillRgba) {
            if (!arr.length) return;
            const stepX = arr.length > 1 ? plotW / (arr.length - 1) : plotW;

            // Area fill
            if (fillRgba) {
                ctx.beginPath();
                arr.forEach(function (v, idx) {
                    const x = padL + idx * stepX;
                    const y = padT + plotH - (v / maxVal) * plotH;
                    if (idx === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                });
                ctx.lineTo(padL + (arr.length - 1) * stepX, padT + plotH);
                ctx.lineTo(padL, padT + plotH);
                ctx.closePath();
                ctx.fillStyle = fillRgba;
                ctx.fill();
            }

            // Line
            ctx.beginPath();
            arr.forEach(function (v, idx) {
                const x = padL + idx * stepX;
                const y = padT + plotH - (v / maxVal) * plotH;
                if (idx === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            });
            ctx.strokeStyle = strokeColor;
            ctx.lineWidth = 2.5;
            ctx.stroke();

            // Points
            arr.forEach(function (v, idx) {
                const x = padL + idx * stepX;
                const y = padT + plotH - (v / maxVal) * plotH;
                ctx.fillStyle = "#17153D";
                ctx.fillRect(x - 3, y - 3, 6, 6);
                ctx.strokeStyle = strokeColor;
                ctx.lineWidth = 2;
                ctx.strokeRect(x - 3, y - 3, 6, 6);
            });
        }

        plotSeries(bViews, "#C7FF5E", "rgba(199, 255, 94, 0.12)");
        plotSeries(pViews, "#90E31F", "rgba(144, 227, 31, 0.16)");
        plotSeries(tgConv, "#F2F4FF", null);

        // X-axis date labels
        const stepX = labels.length > 1 ? plotW / (labels.length - 1) : plotW;
        const skip = Math.max(1, Math.ceil(labels.length / 8));
        ctx.fillStyle = "#F2F4FF";
        labels.forEach(function (lbl, idx) {
            if (idx % skip === 0 || idx === labels.length - 1) {
                const x = padL + idx * stepX;
                ctx.fillText(lbl, Math.max(padL, x - 18), height - 12);
            }
        });
    }

    // Graph 2: Product Views & Stay Time (Dwell Seconds) Bar Chart
    function drawProductDwellChart(products) {
        const canvas = document.getElementById("chart-product-dwell");
        if (!canvas || !products) return;
        const ctx = canvas.getContext("2d");
        const dpr = window.devicePixelRatio || 1;
        const rect = canvas.parentElement.getBoundingClientRect();
        const width = Math.max(320, rect.width - 16);
        const height = 270;

        canvas.width = width * dpr;
        canvas.height = height * dpr;
        canvas.style.width = width + "px";
        canvas.style.height = height + "px";
        ctx.scale(dpr, dpr);
        ctx.clearRect(0, 0, width, height);

        const topProds = products.slice(0, 6);
        const padL = 42, padR = 16, padT = 25, padB = 50;
        const plotW = width - padL - padR;
        const plotH = height - padT - padB;

        const maxMetric = Math.max(
            60,
            ...topProds.map(function (p) { return Math.max(p.views * 3, p.avg_stay_sec); })
        );

        ctx.strokeStyle = "#433E96";
        ctx.font = "10px 'JetBrains Mono', monospace";
        ctx.fillStyle = "#A5A3C8";
        for (let i = 0; i <= 4; i++) {
            const y = padT + (plotH * i) / 4;
            ctx.beginPath();
            ctx.moveTo(padL, y);
            ctx.lineTo(width - padR, y);
            ctx.stroke();
            ctx.fillText(Math.round(maxMetric * (1 - i / 4)) + "s", 4, y + 3);
        }

        const groupW = plotW / Math.max(1, topProds.length);
        const barW = Math.min(24, (groupW - 16) / 2);

        topProds.forEach(function (p, idx) {
            const gx = padL + idx * groupW + 10;

            // Bar 1: Avg Stay Seconds (#90E31F Acid Lime)
            const stayH = (p.avg_stay_sec / maxMetric) * plotH;
            const stayY = padT + plotH - stayH;
            ctx.fillStyle = "#90E31F";
            ctx.fillRect(gx, stayY, barW, stayH);

            // Bar 2: Views scaled (#C7FF5E Cyber Volt)
            const viewScaled = Math.min(maxMetric, p.views * 3);
            const viewH = (viewScaled / maxMetric) * plotH;
            const viewY = padT + plotH - viewH;
            ctx.fillStyle = "#C7FF5E";
            ctx.fillRect(gx + barW + 4, viewY, barW, viewH);

            // Value labels on top of bars
            ctx.fillStyle = "#F2F4FF";
            ctx.font = "10px 'JetBrains Mono', monospace";
            ctx.fillText(Math.round(p.avg_stay_sec) + "s", gx - 2, stayY - 5);
            ctx.fillStyle = "#C7FF5E";
            ctx.fillText(p.views + "v", gx + barW + 4, viewY - 5);

            // SKU label on X axis
            const shortSku = p.sku.replace("LIC-", "").replace("TOOL-", "").replace("FREE-", "");
            ctx.fillStyle = "#F2F4FF";
            ctx.fillText(shortSku.substring(0, 9), gx - 2, height - 20);
        });
    }

    // Graph 3: Blog Post Read Stay-Time, Scroll Depth & Smart Ad Clicks
    function drawBlogAdConversionChart(blogs) {
        const canvas = document.getElementById("chart-blog-conversions");
        if (!canvas || !blogs) return;
        const ctx = canvas.getContext("2d");
        const dpr = window.devicePixelRatio || 1;
        const rect = canvas.parentElement.getBoundingClientRect();
        const width = Math.max(320, rect.width - 16);
        const height = 250;

        canvas.width = width * dpr;
        canvas.height = height * dpr;
        canvas.style.width = width + "px";
        canvas.style.height = height + "px";
        ctx.scale(dpr, dpr);
        ctx.clearRect(0, 0, width, height);

        const topBlogs = blogs.slice(0, 5);
        const padL = 135, padR = 55, padT = 18, padB = 24;
        const plotW = width - padL - padR;
        const plotH = height - padT - padB;
        const rowH = plotH / Math.max(1, topBlogs.length);

        const maxStay = Math.max(120, ...topBlogs.map(function (b) { return b.avg_stay_sec; }));

        topBlogs.forEach(function (b, idx) {
            const y = padT + idx * rowH;
            const label = (b.cve_id ? b.cve_id + " " : "") + b.title.substring(0, 14) + "..";

            ctx.fillStyle = "#F2F4FF";
            ctx.font = "11px 'JetBrains Mono', monospace";
            ctx.fillText(label.substring(0, 19), 6, y + rowH / 2 + 4);

            // Background bar track
            ctx.fillStyle = "#17153D";
            ctx.fillRect(padL, y + 6, plotW, rowH - 14);
            ctx.strokeStyle = "#433E96";
            ctx.strokeRect(padL, y + 6, plotW, rowH - 14);

            // Stay time bar (#90E31F)
            const stayW = Math.max(8, (b.avg_stay_sec / maxStay) * plotW);
            ctx.fillStyle = "#90E31F";
            ctx.fillRect(padL, y + 6, stayW, (rowH - 14) * 0.55);

            // Scroll completion bar (#C7FF5E)
            const scrollW = (Math.min(100, b.avg_scroll_pct) / 100) * plotW;
            ctx.fillStyle = "#C7FF5E";
            ctx.fillRect(padL, y + 6 + (rowH - 14) * 0.55, scrollW, (rowH - 14) * 0.45);

            // Right-hand stats readout
            ctx.fillStyle = "#C7FF5E";
            ctx.fillText(
                formatDuration(b.avg_stay_sec) + " | " + b.ad_clicks + " Ads",
                padL + plotW + 6,
                y + rowH / 2 + 4
            );
        });
    }

    function drawOsAndFunnelPanel(kpis, osList, referrers) {
        const funnelEl = document.getElementById("analytics-funnel-bars");
        if (funnelEl && kpis) {
            const maxF = Math.max(1, kpis.total_views);
            const steps = [
                { label: "1. Total Page Visits", count: kpis.total_views, color: "#90E31F" },
                { label: "2. Smart Ad Impressions in Blog", count: kpis.smart_ad_impressions, color: "#C7FF5E" },
                { label: "3. Smart Ad Clicks -> Product", count: kpis.smart_ad_clicks, color: "#90E31F" },
                { label: "4. Arsenal Cart Additions", count: kpis.cart_adds, color: "#C7FF5E" },
                { label: "5. Telegram Buy & Order Clicks", count: kpis.telegram_buy_clicks, color: "#F2F4FF" }
            ];
            funnelEl.innerHTML = steps.map(function (s) {
                const pct = Math.min(100, Math.max(6, Math.round((s.count / maxF) * 100)));
                return (
                    '<div class="mb-2.5">' +
                        '<div class="flex justify-between font-mono text-xs mb-1">' +
                            '<span class="text-[#F2F4FF]">' + s.label + '</span>' +
                            '<span class="text-[#C7FF5E] font-bold">' + s.count + ' (' + pct + '%)</span>' +
                        '</div>' +
                        '<div class="w-full h-3 bg-[#17153D] border border-[#433E96]">' +
                            '<div class="h-full" style="width:' + pct + '%; background-color:' + s.color + ';"></div>' +
                        '</div>' +
                    '</div>'
                );
            }).join("");
        }

        const osEl = document.getElementById("analytics-os-list");
        if (osEl && osList) {
            const totalOs = Math.max(1, osList.reduce(function (a, b) { return a + b.count; }, 0));
            osEl.innerHTML = osList.map(function (o) {
                const pct = Math.round((o.count / totalOs) * 100);
                return (
                    '<div class="flex items-center justify-between py-1.5 border-b border-[#433E96]/60 font-mono text-xs">' +
                        '<span class="text-[#F2F4FF]">' + o.os + '</span>' +
                        '<div class="flex items-center gap-2">' +
                            '<div class="w-24 h-2 bg-[#17153D] border border-[#433E96]"><div class="h-full bg-[#90E31F]" style="width:' + pct + '%"></div></div>' +
                            '<span class="text-[#C7FF5E] w-14 text-right">' + pct + '% (' + o.count + ')</span>' +
                        '</div>' +
                    '</div>'
                );
            }).join("");
        }
    }

    function populateAnalyticsTables(products, blogs, stream) {
        const prodTbody = document.getElementById("analytics-products-tbody");
        if (prodTbody && products) {
            prodTbody.innerHTML = products.map(function (p) {
                return (
                    '<tr class="border-b border-[#433E96] hover:bg-[#17153D]/60">' +
                        '<td class="p-3 font-mono text-xs text-[#90E31F] font-bold">' + p.sku + '</td>' +
                        '<td class="p-3 text-sm font-bold text-[#F2F4FF]"><a href="/arsenal/' + p.slug + '" class="hover:text-[#C7FF5E]">' + p.name + '</a></td>' +
                        '<td class="p-3 font-mono text-xs text-[#F2F4FF]">' + p.views + ' <span class="text-[#A5A3C8]">(' + p.uniques + ' uniq)</span></td>' +
                        '<td class="p-3 font-mono text-xs text-[#C7FF5E] font-bold">' + formatDuration(p.avg_stay_sec) + '</td>' +
                        '<td class="p-3 font-mono text-xs text-[#F2F4FF]">' + p.avg_scroll_pct + '%</td>' +
                        '<td class="p-3 font-mono text-xs text-[#90E31F]">' + p.ad_clicks + ' from blog</td>' +
                        '<td class="p-3 font-mono text-xs text-[#C7FF5E] font-bold">' + p.tg_buys + ' (' + p.conversion_pct + '%)</td>' +
                    '</tr>'
                );
            }).join("");
        }

        const blogTbody = document.getElementById("analytics-blogs-tbody");
        if (blogTbody && blogs) {
            blogTbody.innerHTML = blogs.map(function (b) {
                return (
                    '<tr class="border-b border-[#433E96] hover:bg-[#17153D]/60">' +
                        '<td class="p-3 font-mono text-xs text-[#C7FF5E]">' + (b.cve_id || b.severity) + '</td>' +
                        '<td class="p-3 text-sm font-bold text-[#F2F4FF]"><a href="/intel/' + b.slug + '" class="hover:text-[#C7FF5E]">' + b.title + '</a></td>' +
                        '<td class="p-3 font-mono text-xs text-[#F2F4FF]">' + b.views + ' <span class="text-[#A5A3C8]">(' + b.uniques + ' uniq)</span></td>' +
                        '<td class="p-3 font-mono text-xs text-[#C7FF5E] font-bold">' + formatDuration(b.avg_stay_sec) + '</td>' +
                        '<td class="p-3 font-mono text-xs text-[#F2F4FF]">' + b.avg_scroll_pct + '% read</td>' +
                        '<td class="p-3 font-mono text-xs text-[#90E31F] font-bold">' + b.ad_clicks + ' / ' + b.ad_impressions + ' (' + b.ad_ctr_pct + '% CTR)</td>' +
                        '<td class="p-3 font-mono text-xs text-[#A5A3C8]">' + (b.related_skus || "Auto") + '</td>' +
                    '</tr>'
                );
            }).join("");
        }

        const streamTbody = document.getElementById("analytics-stream-tbody");
        if (streamTbody && stream) {
            streamTbody.innerHTML = stream.map(function (s) {
                return (
                    '<tr class="border-b border-[#433E96]/60 text-xs font-mono">' +
                        '<td class="p-2.5 text-[#A5A3C8]">' + s.last_ping_at.substring(5) + '</td>' +
                        '<td class="p-2.5 text-[#90E31F]">' + s.visitor_id.substring(0, 10) + '</td>' +
                        '<td class="p-2.5"><span class="px-1.5 py-0.5 bg-[#17153D] border border-[#433E96] text-[#C7FF5E]">' + s.page_type + '</span></td>' +
                        '<td class="p-2.5 text-[#F2F4FF] truncate max-w-[240px]">' + s.target_title + '</td>' +
                        '<td class="p-2.5 text-[#C7FF5E] font-bold">' + formatDuration(s.duration_seconds) + '</td>' +
                        '<td class="p-2.5 text-[#F2F4FF]">' + s.max_scroll_pct + '%</td>' +
                        '<td class="p-2.5 text-[#A5A3C8]">' + s.os_name + ' / ' + s.device_type + '</td>' +
                        '<td class="p-2.5 text-[#90E31F]">' + s.referrer + '</td>' +
                    '</tr>'
                );
            }).join("");
        }
    }

    // =========================================================================
    // 3. CUSTOMIZABLE BLOG STUDIO & SMART PRODUCT AD BUILDER
    // =========================================================================
    function insertBlogSnippet(type) {
        const textarea = document.getElementById("post-form-content");
        if (!textarea) return;

        let snippet = "";
        if (type === "h2") {
            snippet = "\n<h2>Section Heading</h2>\n<p>Write your technical analysis here...</p>\n";
        } else if (type === "code") {
            snippet = "\n<pre><code># Terminal payload or exploit command\nmsf6 > use exploit/multi/handler\n</code></pre>\n";
        } else if (type === "callout") {
            snippet = '\n<div class="cyber-callout">\n<strong>⚡ TACTICAL ADVISORY:</strong> Key zero-day impact or mitigation note.\n</div>\n';
        } else if (type === "smart_ad") {
            const skuSelect = document.getElementById("blog-smart-ad-sku-picker");
            const sku = skuSelect ? skuSelect.value : "LIC-BURP-PRO";
            snippet = "\n[product:" + sku + "]\n";
            // Also append SKU to related_skus input if not already there
            const relInput = document.getElementById("post-form-related-skus");
            if (relInput) {
                const current = relInput.value.split(",").map(function (s) { return s.trim(); }).filter(Boolean);
                if (!current.includes(sku)) {
                    current.push(sku);
                    relInput.value = current.join(",");
                }
            }
        }

        const start = textarea.selectionStart || textarea.value.length;
        const end = textarea.selectionEnd || textarea.value.length;
        textarea.value = textarea.value.substring(0, start) + snippet + textarea.value.substring(end);
        textarea.focus();
    }

    async function previewBlogWithSmartAds() {
        const content = document.getElementById("post-form-content").value;
        const relatedSkus = document.getElementById("post-form-related-skus").value;
        const adMode = document.getElementById("post-form-ad-mode").value;
        const slug = document.getElementById("post-form-slug").value || "preview";

        const res = await fetch("/api/admin/posts/preview", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                content: content,
                related_skus: relatedSkus,
                ad_mode: adMode,
                slug: slug
            })
        });
        const data = await res.json();
        const previewBox = document.getElementById("blog-live-preview-box");
        const previewContainer = document.getElementById("blog-live-preview-wrapper");
        if (previewBox && previewContainer && data.ok) {
            previewBox.innerHTML = data.rendered_html;
            previewContainer.classList.remove("hidden");
            previewContainer.scrollIntoView({ behavior: "smooth" });
        }
    }

    function editPostInStudio(postObj) {
        document.getElementById("post-form-id").value = postObj.id || "";
        document.getElementById("post-form-title").value = postObj.title || "";
        document.getElementById("post-form-slug").value = postObj.slug || "";
        document.getElementById("post-form-category").value = postObj.category || "Zero-Day Advisories";
        document.getElementById("post-form-severity").value = postObj.severity || "CRITICAL";
        document.getElementById("post-form-cve").value = postObj.cve_id || "";
        document.getElementById("post-form-cvss").value = postObj.cvss_score || "";
        document.getElementById("post-form-author").value = postObj.author || "ZERO-DAY UNIT";
        document.getElementById("post-form-read-time").value = postObj.read_time || "6 MIN READ";
        document.getElementById("post-form-summary").value = postObj.summary || "";
        document.getElementById("post-form-content").value = postObj.content || "";
        document.getElementById("post-form-related-skus").value = postObj.related_skus || "";
        document.getElementById("post-form-ad-mode").value = postObj.ad_mode || "ALL";
        document.getElementById("post-form-ad-pitch").value = postObj.ad_custom_pitch || "";
        document.getElementById("post-form-featured").checked = Boolean(postObj.featured);
        document.getElementById("post-studio-heading").textContent = "EDITING ADVISORY #" + postObj.id + ": " + postObj.title;
        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    function resetPostStudio() {
        document.getElementById("post-form-id").value = "";
        document.getElementById("post-form-title").value = "";
        document.getElementById("post-form-slug").value = "";
        document.getElementById("post-form-cve").value = "CVE-2026-";
        document.getElementById("post-form-cvss").value = "9.8";
        document.getElementById("post-form-summary").value = "";
        document.getElementById("post-form-content").value = "";
        document.getElementById("post-form-related-skus").value = "LIC-BURP-PRO";
        document.getElementById("post-form-ad-mode").value = "ALL";
        document.getElementById("post-form-ad-pitch").value = "";
        document.getElementById("post-form-featured").checked = true;
        document.getElementById("post-studio-heading").textContent = "PUBLISH NEW CYBERSECURITY BLOG & SMART PRODUCT AD";
    }

    async function savePostFromStudio(ev) {
        if (ev) ev.preventDefault();
        const payload = {
            id: document.getElementById("post-form-id").value || null,
            title: document.getElementById("post-form-title").value,
            slug: document.getElementById("post-form-slug").value,
            category: document.getElementById("post-form-category").value,
            severity: document.getElementById("post-form-severity").value,
            cve_id: document.getElementById("post-form-cve").value,
            cvss_score: document.getElementById("post-form-cvss").value,
            author: document.getElementById("post-form-author").value,
            read_time: document.getElementById("post-form-read-time").value,
            summary: document.getElementById("post-form-summary").value,
            content: document.getElementById("post-form-content").value,
            related_skus: document.getElementById("post-form-related-skus").value,
            ad_mode: document.getElementById("post-form-ad-mode").value,
            ad_custom_pitch: document.getElementById("post-form-ad-pitch").value,
            featured: document.getElementById("post-form-featured").checked
        };

        const res = await fetch("/api/admin/posts", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (res.ok && data.ok) {
            window.ZDCart.showToast("BLOG POST & SMART ADS SAVED!");
            setTimeout(function () { window.location.reload(); }, 600);
        } else {
            window.ZDCart.showToast(data.error || "Error saving post");
        }
    }

    async function deletePost(postId) {
        const res = await fetch("/api/admin/posts/" + postId, { method: "DELETE" });
        if (res.ok) {
            window.ZDCart.showToast("BLOG POST DELETED");
            setTimeout(function () { window.location.reload(); }, 500);
        }
    }

    // =========================================================================
    // 4. DIGITAL PRODUCTS & LICENSES MANAGER
    // =========================================================================
    function editProductInForm(prodObj) {
        document.getElementById("prod-form-id").value = prodObj.id || "";
        document.getElementById("prod-form-sku").value = prodObj.sku || "";
        document.getElementById("prod-form-name").value = prodObj.name || "";
        document.getElementById("prod-form-slug").value = prodObj.slug || "";
        document.getElementById("prod-form-category").value = prodObj.category || "Web & AppSec Licenses";
        document.getElementById("prod-form-type").value = prodObj.product_type || "LICENSE_KEY";
        document.getElementById("prod-form-price").value = prodObj.price || 0;
        document.getElementById("prod-form-retail").value = prodObj.retail_price || 0;
        document.getElementById("prod-form-version").value = prodObj.version || "";
        document.getElementById("prod-form-duration").value = prodObj.license_duration || "";
        document.getElementById("prod-form-platform").value = prodObj.platform || "";
        document.getElementById("prod-form-badge").value = prodObj.badge_text || "INSTANT DELIVERY";
        document.getElementById("prod-form-short").value = prodObj.short_desc || "";
        document.getElementById("prod-form-specs").value = (prodObj.specs || []).join("\n");
        document.getElementById("prod-form-sha256").value = prodObj.sha256_hash || "";
        document.getElementById("prod-form-download").value = prodObj.download_url || "";
        document.getElementById("prod-form-featured").checked = Boolean(prodObj.featured);
        document.getElementById("prod-studio-heading").textContent = "EDITING PRODUCT: " + prodObj.name + " [" + prodObj.sku + "]";
        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    function resetProductForm() {
        document.getElementById("prod-form-id").value = "";
        document.getElementById("prod-form-sku").value = "LIC-";
        document.getElementById("prod-form-name").value = "";
        document.getElementById("prod-form-slug").value = "";
        document.getElementById("prod-form-price").value = "149";
        document.getElementById("prod-form-retail").value = "1200";
        document.getElementById("prod-form-version").value = "v2026.10 Pro";
        document.getElementById("prod-form-duration").value = "1-Year Pro License";
        document.getElementById("prod-form-platform").value = "Windows / Linux / macOS";
        document.getElementById("prod-form-badge").value = "INSTANT TELEGRAM KEY";
        document.getElementById("prod-form-short").value = "";
        document.getElementById("prod-form-specs").value = "";
        document.getElementById("prod-form-sha256").value = "";
        document.getElementById("prod-form-download").value = "";
        document.getElementById("prod-form-featured").checked = true;
        document.getElementById("prod-studio-heading").textContent = "ADD NEW DIGITAL LICENSE OR DOWNLOADABLE TOOL";
    }

    async function saveProductForm(ev) {
        if (ev) ev.preventDefault();
        const payload = {
            id: document.getElementById("prod-form-id").value || null,
            sku: document.getElementById("prod-form-sku").value,
            name: document.getElementById("prod-form-name").value,
            slug: document.getElementById("prod-form-slug").value,
            category: document.getElementById("prod-form-category").value,
            product_type: document.getElementById("prod-form-type").value,
            price: parseFloat(document.getElementById("prod-form-price").value || 0),
            retail_price: parseFloat(document.getElementById("prod-form-retail").value || 0),
            version: document.getElementById("prod-form-version").value,
            license_duration: document.getElementById("prod-form-duration").value,
            platform: document.getElementById("prod-form-platform").value,
            badge_text: document.getElementById("prod-form-badge").value,
            short_desc: document.getElementById("prod-form-short").value,
            specs: document.getElementById("prod-form-specs").value,
            sha256_hash: document.getElementById("prod-form-sha256").value,
            download_url: document.getElementById("prod-form-download").value,
            featured: document.getElementById("prod-form-featured").checked
        };

        const res = await fetch("/api/admin/products", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (res.ok && data.ok) {
            window.ZDCart.showToast("DIGITAL PRODUCT SAVED!");
            setTimeout(function () { window.location.reload(); }, 600);
        } else {
            window.ZDCart.showToast(data.error || "Error saving product");
        }
    }

    async function deleteProduct(prodId) {
        const res = await fetch("/api/admin/products/" + prodId, { method: "DELETE" });
        if (res.ok) {
            window.ZDCart.showToast("PRODUCT REMOVED");
            setTimeout(function () { window.location.reload(); }, 500);
        }
    }

    // =========================================================================
    // 5. ORDERS & GLOBAL SETTINGS
    // =========================================================================
    async function saveOrderFulfillment(orderId) {
        const statusEl = document.getElementById("order-status-" + orderId);
        const licenseEl = document.getElementById("order-license-" + orderId);
        const res = await fetch("/api/admin/orders/" + orderId, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                status: statusEl ? statusEl.value : "COMPLETED",
                fulfilled_license_info: licenseEl ? licenseEl.value : ""
            })
        });
        if (res.ok) {
            window.ZDCart.showToast("ORDER #" + orderId + " UPDATED & LICENSE UNLOCKED!");
            setTimeout(function () { window.location.reload(); }, 500);
        }
    }

    async function deleteOrder(orderId) {
        const res = await fetch("/api/admin/orders/" + orderId, { method: "DELETE" });
        if (res.ok) {
            window.ZDCart.showToast("ORDER DELETED");
            setTimeout(function () { window.location.reload(); }, 500);
        }
    }

    async function saveGlobalSettings(ev) {
        if (ev) ev.preventDefault();
        const fields = [
            "site_name", "site_tagline", "telegram_user", "telegram_channel",
            "ticker_text", "hero_badge", "hero_title", "hero_subtitle",
            "telegram_msg_prefix", "footer_disclaimer"
        ];
        const payload = {};
        fields.forEach(function (k) {
            const el = document.getElementById("setting-" + k);
            if (el) payload[k] = el.value;
        });

        const res = await fetch("/api/admin/settings", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            window.ZDCart.showToast("GLOBAL SITE & TELEGRAM SETTINGS UPDATED!");
            setTimeout(function () { window.location.reload(); }, 600);
        }
    }

    async function saveUserRbac(userId) {
        const roleEl = document.getElementById("user-role-" + userId);
        const activeEl = document.getElementById("user-active-" + userId);
        const passEl = document.getElementById("user-pass-" + userId);
        const res = await fetch("/api/admin/users/" + userId, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                role: roleEl ? roleEl.value : "CUSTOMER",
                is_active: activeEl ? activeEl.checked : true,
                new_password: passEl ? passEl.value : ""
            })
        });
        if (res.ok) {
            window.ZDCart.showToast("OPERATOR #" + userId + " RBAC & SECURITY UPDATED!");
            setTimeout(function () { window.location.reload(); }, 500);
        }
    }

    document.addEventListener("DOMContentLoaded", function () {
        if (document.getElementById("chart-traffic-timeline")) {
            loadAnalyticsDashboard(14);
            window.addEventListener("resize", function () {
                if (cachedAnalyticsData) {
                    drawTimelineChart(cachedAnalyticsData.timeline);
                    drawProductDwellChart(cachedAnalyticsData.products);
                    drawBlogAdConversionChart(cachedAnalyticsData.blogs);
                }
            });
        }
    });

    window.ZDAdmin = {
        switchTab: switchAdminTab,
        loadAnalytics: loadAnalyticsDashboard,
        insertSnippet: insertBlogSnippet,
        previewBlog: previewBlogWithSmartAds,
        editPost: editPostInStudio,
        resetPost: resetPostStudio,
        savePost: savePostFromStudio,
        deletePost: deletePost,
        editProduct: editProductInForm,
        resetProduct: resetProductForm,
        saveProduct: saveProductForm,
        deleteProduct: deleteProduct,
        saveOrder: saveOrderFulfillment,
        deleteOrder: deleteOrder,
        saveSettings: saveGlobalSettings,
        saveUserRbac: saveUserRbac
    };
})();
