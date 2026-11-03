import re
import json
import uuid
import html
import urllib.parse
from urllib.parse import quote
from datetime import datetime, timedelta
from flask import request
from markdown_it import MarkdownIt

from database import get_db
from core.config import DEFAULT_SITE_SETTINGS

def log_audit_event(conn, user_id, username, action, details=""):
    ip_addr = request.headers.get("X-Forwarded-For", request.remote_addr or "127.0.0.1")
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("""
    INSERT INTO auth_audit_logs (user_id, username, action, ip_address, details, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, username, action, ip_addr, details, now_str))



def get_settings_dict(conn=None):
    close_after = False
    if conn is None:
        conn = get_db()
        close_after = True
    d = dict(DEFAULT_SITE_SETTINGS)
    rows = conn.execute("SELECT key, value FROM settings").fetchall()
    if close_after:
        conn.close()
    for r in rows:
        d[r["key"]] = r["value"]
    return d


def render_markdown_prose(text):
    if not text:
        return ""
    try:
        md = MarkdownIt("commonmark", {"html": True, "breaks": True}).enable("table")
        html_content = md.render(text)
    except Exception:
        html_content = text

    # Post-process GitHub Alert Callouts: [!WARNING], [!NOTE], [!TIP], [!CAUTION]
    html_content = re.sub(
        r"<blockquote>\s*<p>\s*\[!WARNING\](?:\s*<br\s*/?>)?\s*([\s\S]*?)</p>\s*</blockquote>",
        r'<div class="callout-alert callout-warning"><div class="callout-header">⚠️ WARNING ADVISORY</div><div class="callout-body">\1</div></div>',
        html_content,
        flags=re.IGNORECASE
    )
    html_content = re.sub(
        r"<blockquote>\s*<p>\s*\[!NOTE\](?:\s*<br\s*/?>)?\s*([\s\S]*?)</p>\s*</blockquote>",
        r'<div class="callout-alert callout-note"><div class="callout-header">ℹ️ RESEARCH NOTE</div><div class="callout-body">\1</div></div>',
        html_content,
        flags=re.IGNORECASE
    )
    html_content = re.sub(
        r"<blockquote>\s*<p>\s*\[!TIP\](?:\s*<br\s*/?>)?\s*([\s\S]*?)</p>\s*</blockquote>",
        r'<div class="callout-alert callout-tip"><div class="callout-header">💡 DEFENSIVE TIP</div><div class="callout-body">\1</div></div>',
        html_content,
        flags=re.IGNORECASE
    )
    html_content = re.sub(
        r"<blockquote>\s*<p>\s*\[!CAUTION\](?:\s*<br\s*/?>)?\s*([\s\S]*?)</p>\s*</blockquote>",
        r'<div class="callout-alert callout-caution"><div class="callout-header">⛔ CRITICAL ALERT</div><div class="callout-body">\1</div></div>',
        html_content,
        flags=re.IGNORECASE
    )
    return html_content


def row_to_product(row):
    if not row:
        return None
    d = dict(row)
    try:
        d["specs"] = json.loads(d.get("specs_json") or "[]")
    except Exception:
        d["specs"] = []
    try:
        d["faq"] = json.loads(d.get("faq_json") or "[]")
        if not isinstance(d["faq"], list):
            d["faq"] = []
    except Exception:
        d["faq"] = []
    desc_raw = d.get("description") or ""
    d["description"] = desc_raw
    d["rendered_description"] = render_markdown_prose(desc_raw)
    price = float(d.get("price") or 0)
    retail = float(d.get("retail_price") or 0)
    if retail > price and retail > 0:
        d["discount_pct"] = int(round((1.0 - (price / retail)) * 100))
    else:
        d["discount_pct"] = 0
    return d


def row_to_post(row):
    if not row:
        return None
    d = dict(row)
    skus = [s.strip() for s in (d.get("related_skus") or "").split(",") if s.strip()]
    d["related_sku_list"] = skus
    try:
        d["cvss_score"] = float(d.get("cvss_score") or 0.0)
    except Exception:
        d["cvss_score"] = 0.0
    try:
        d["ad_count"] = int(d.get("ad_count") if d.get("ad_count") is not None else 1)
    except Exception:
        d["ad_count"] = 1
    d["ad_placement"] = (d.get("ad_placement") or "MIDDLE").strip().upper()
    try:
        d["ad_paragraph_interval"] = int(d.get("ad_paragraph_interval") if d.get("ad_paragraph_interval") is not None else 4)
    except Exception:
        d["ad_paragraph_interval"] = 4
    if d.get("summary"):
        d["summary"] = re.sub(r"\[(?:ad|product)(?::[A-Za-z0-9_\-]+)?\]", "", d["summary"], flags=re.IGNORECASE).strip()
    return d


def build_telegram_product_url(product, settings):
    tg_user = settings.get("telegram_user", "ZeroDayMatrixSupport").lstrip("@")
    prefix = settings.get("telegram_msg_prefix", "Hello! I want to purchase:")
    msg = (
        f"{prefix}\n"
        f"• Product: {product['name']} ({product['sku']})\n"
        f"• Version: {product['version']} [{product['license_duration']}]\n"
        f"• Price: ${product['price']:.2f}\n"
        f"Please send payment details for instant activation."
    )
    return f"https://t.me/{tg_user}?text={quote(msg)}"


def render_inline_smart_ad_html(product, settings, post_slug="", candidate_pool=None, initial_index=0, instance_id=None):
    """Renders a simplified, short fixed-space banner ad inside blog post prose with product image background."""
    if not instance_id:
        instance_id = f"smart-ad-{uuid.uuid4().hex[:8]}"

    tg_url = build_telegram_product_url(product, settings)
    ad_headline = (product.get("ad_headline") or "").strip() or product["name"]
    ad_desc = (product.get("ad_description") or "").strip() or (product.get("short_desc") or "").strip()
    ad_badge = (product.get("ad_badge") or "").strip()
    ad_cta = (product.get("ad_cta_text") or "").strip()
    ad_img = (product.get("ad_image_url") or "").strip() or (product.get("image_url") or "").strip() or "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1200&q=85"

    if ad_badge:
        discount_badge = f'<span class="badge-tag" style="background:#dc2626; color:#ffffff; font-weight:700; border:none; padding:0.25rem 0.65rem; font-size:0.7rem; letter-spacing:0.04em;">{html.escape(ad_badge)}</span>'
    elif product["discount_pct"] > 0:
        discount_badge = f'<span class="badge-tag" style="background:#dc2626; color:#ffffff; font-weight:700; border:none; padding:0.25rem 0.65rem; font-size:0.7rem; letter-spacing:0.04em;">SAVE {product["discount_pct"]}% OFF</span>'
    else:
        discount_badge = '<span class="badge-tag" style="background:rgba(255,255,255,0.18); color:#ffffff; font-weight:700; border:1px solid rgba(255,255,255,0.35); padding:0.25rem 0.65rem; font-size:0.7rem;">VERIFIED SYSTEM</span>'

    is_free = product["product_type"] == "FREE_TOOL" or product["price"] <= 0
    price_html = (
        '<span class="meta-mono" style="font-weight:700; font-size:1.15rem; color:#ffffff;">FREE TOOL</span>'
        if is_free
        else (
            f'<span class="meta-mono" style="text-decoration:line-through; color:rgba(255,255,255,0.55); margin-right:0.45rem; font-size:0.85rem;">${product["retail_price"]:.0f}</span>'
            if product.get("retail_price") and product["retail_price"] > product["price"]
            else ''
        ) + f'<span class="meta-mono" style="font-weight:700; font-size:1.2rem; color:#ffffff;">${product["price"]:.0f}</span>'
    )

    if ad_cta:
        cta_label = html.escape(ad_cta)
    elif is_free and product.get("download_url"):
        cta_label = f"DOWNLOAD ({product['version']})"
    else:
        cta_label = "ORDER VIA TELEGRAM →"

    primary_cta = (
        f'<a href="{product["download_url"]}" download '
        f'class="btn" style="background:#ffffff; color:#0c0d0e; padding:0.45rem 1rem; font-size:0.72rem; font-weight:700; border:none; text-decoration:none; display:inline-flex; align-items:center;">{cta_label}</a>'
        if is_free and product.get("download_url") and not ad_cta
        else f'<a href="{tg_url}" target="_blank" rel="noopener" '
             f'class="btn" style="background:#ffffff; color:#0c0d0e; padding:0.45rem 1rem; font-size:0.72rem; font-weight:700; border:none; text-decoration:none; display:inline-flex; align-items:center;">{cta_label}</a>'
    )

    pool_items = []
    has_rotation = False
    if candidate_pool and len(candidate_pool) > 1:
        has_rotation = True
        for p in candidate_pool:
            p_tg = build_telegram_product_url(p, settings)
            p_price = float(p.get("price") or 0)
            p_retail = float(p.get("retail_price") or 0)
            p_disc = int(p.get("discount_pct") or 0)
            p_free = (p.get("product_type") == "FREE_TOOL") or (p_price <= 0)
            p_head = (p.get("ad_headline") or "").strip() or p["name"]
            p_desc_txt = (p.get("ad_description") or "").strip() or (p.get("short_desc") or "").strip()
            p_badge_txt = (p.get("ad_badge") or "").strip()
            p_cta_txt = (p.get("ad_cta_text") or "").strip()
            p_img = (p.get("ad_image_url") or "").strip() or (p.get("image_url") or "").strip() or "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1200&q=85"
            pool_items.append({
                "id": p["id"],
                "sku": p["sku"],
                "name": p_head,
                "slug": p["slug"],
                "short_desc": p_desc_txt,
                "image_url": p_img,
                "ad_badge": p_badge_txt,
                "ad_cta": p_cta_txt,
                "version": p.get("version") or "v1.0",
                "price": p_price,
                "retail_price": p_retail,
                "discount_pct": p_disc,
                "is_free": p_free,
                "download_url": p.get("download_url") or "",
                "tg_url": p_tg,
            })

    rotator_script_html = ""
    progress_bar_html = ""

    if has_rotation:
        progress_bar_html = f'<div id="{instance_id}-pbar" class="smart-ad-pbar" style="position:absolute; top:0; left:0; height:2px; width:0%; background:#00e5ff; opacity:0.85; transition:width 12s linear; z-index:3;"></div>'
        pool_json = json.dumps(pool_items).replace("</", "<\\/")
        rotator_script_html = f"""
<script type="application/json" id="{instance_id}-data">
{pool_json}
</script>
<script>
(function() {{
    const card = document.getElementById('{instance_id}');
    if (!card) return;
    let pool = [];
    try {{
        const raw = document.getElementById('{instance_id}-data');
        if (raw) pool = JSON.parse(raw.textContent);
    }} catch(e) {{
        console.error('Failed to parse smart ad pool', e);
    }}
    if (!pool || pool.length <= 1) return;

    let currentIndex = {initial_index};
    let timer = null;
    let isHovered = false;

    function resetProgressBar() {{
        const bar = card.querySelector('.smart-ad-pbar');
        if (!bar) return;
        bar.style.transition = 'none';
        bar.style.width = '0%';
        void bar.offsetWidth;
        bar.style.transition = 'width 12s linear';
        bar.style.width = '100%';
    }}

    function renderItem(idx) {{
        const item = pool[idx];
        if (!item) return;

        const bgStage = card.querySelector('[data-ad-role="bg-stage"]');
        if (bgStage && item.image_url) {{
            bgStage.style.opacity = '0.45';
            setTimeout(function() {{
                bgStage.style.backgroundImage = 'url(\"' + item.image_url + '\")';
                bgStage.style.opacity = '1';
            }}, 150);
        }}

        const body = card.querySelector('[data-ad-role="content-body"]');
        if (body) body.style.opacity = '0.25';

        setTimeout(function() {{
            const badgeEl = card.querySelector('[data-ad-role="badge"]');
            if (badgeEl) {{
                if (item.ad_badge) {{
                    badgeEl.innerHTML = '<span class=\"badge-tag\" style=\"background:#dc2626; color:#ffffff; font-weight:700; border:none; padding:0.25rem 0.65rem; font-size:0.7rem; letter-spacing:0.04em;\">' + item.ad_badge + '</span>';
                }} else if (item.discount_pct > 0) {{
                    badgeEl.innerHTML = '<span class=\"badge-tag\" style=\"background:#dc2626; color:#ffffff; font-weight:700; border:none; padding:0.25rem 0.65rem; font-size:0.7rem; letter-spacing:0.04em;\">SAVE ' + item.discount_pct + '% OFF</span>';
                }} else {{
                    badgeEl.innerHTML = '<span class=\"badge-tag\" style=\"background:rgba(255,255,255,0.18); color:#ffffff; font-weight:700; border:1px solid rgba(255,255,255,0.35); padding:0.25rem 0.65rem; font-size:0.7rem;\">VERIFIED SYSTEM</span>';
                }}
            }}

            const titleEl = card.querySelector('[data-ad-role="title"]');
            if (titleEl) {{
                titleEl.href = '/arsenal/' + encodeURIComponent(item.slug);
                titleEl.textContent = item.name;
            }}

            const descEl = card.querySelector('[data-ad-role="desc"]');
            if (descEl) {{
                descEl.textContent = item.short_desc;
            }}

            const priceEl = card.querySelector('[data-ad-role="price"]');
            if (priceEl) {{
                if (item.is_free) {{
                    priceEl.innerHTML = '<span class=\"meta-mono\" style=\"font-weight:700; font-size:1.15rem; color:#ffffff;\">FREE TOOL</span>';
                }} else {{
                    let h = '';
                    if (item.retail_price > item.price) {{
                        h += '<span class=\"meta-mono\" style=\"text-decoration:line-through; color:rgba(255,255,255,0.55); margin-right:0.45rem; font-size:0.85rem;\">$' + Math.round(item.retail_price) + '</span>';
                    }}
                    h += '<span class=\"meta-mono\" style=\"font-weight:700; font-size:1.2rem; color:#ffffff;\">$' + Math.round(item.price) + '</span>';
                    priceEl.innerHTML = h;
                }}
            }}

            const actionsEl = card.querySelector('[data-ad-role="actions"]');
            if (actionsEl) {{
                let cta = '';
                const ctaText = item.ad_cta || (item.is_free && item.download_url ? 'DOWNLOAD (' + item.version + ')' : 'ORDER VIA TELEGRAM →');
                if (item.is_free && item.download_url && !item.ad_cta) {{
                    cta = '<a href=\"' + item.download_url + '\" download class=\"btn\" style=\"background:#ffffff; color:#0c0d0e; padding:0.45rem 1rem; font-size:0.72rem; font-weight:700; border:none; text-decoration:none; display:inline-flex; align-items:center;\">' + ctaText + '</a>';
                }} else {{
                    cta = '<a href=\"' + item.tg_url + '\" target=\"_blank\" rel=\"noopener\" class=\"btn\" style=\"background:#ffffff; color:#0c0d0e; padding:0.45rem 1rem; font-size:0.72rem; font-weight:700; border:none; text-decoration:none; display:inline-flex; align-items:center;\">' + ctaText + '</a>';
                }}
                const bag = '<button type=\"button\" onclick=\"window.NFCart && window.NFCart.quickAdd(' + item.id + ')\" class=\"btn\" style=\"background:rgba(0,0,0,0.6); color:#ffffff; border:1px solid rgba(255,255,255,0.6); padding:0.45rem 0.85rem; font-size:0.72rem; font-weight:700; cursor:pointer; backdrop-filter:blur(4px);\">+ BAG</button>';
                actionsEl.innerHTML = cta + ' ' + bag;
            }}

            card.setAttribute('data-smart-ad-sku', item.sku);

            if (body) body.style.opacity = '1';
        }}, 160);
    }}

    function rotateNext() {{
        currentIndex = (currentIndex + 1) % pool.length;
        renderItem(currentIndex);
        restartTimer();
    }}

    function restartTimer() {{
        if (timer) clearInterval(timer);
        resetProgressBar();
        timer = setInterval(function() {{
            if (!isHovered) {{
                rotateNext();
            }}
        }}, 12000);
    }}

    card.addEventListener('mouseenter', function() {{ isHovered = true; }});
    card.addEventListener('mouseleave', function() {{ isHovered = false; }});

    restartTimer();
}})();
</script>
"""

    return f"""
<div id="{instance_id}" class="smart-native-ad-banner" data-smart-ad-sku="{product['sku']}" data-ad-placement="INLINE_AD">
    <div data-ad-role="bg-stage" style="position:absolute; inset:0; z-index:0; background-image:url('{ad_img}'); background-size:cover; background-position:center; filter:brightness(0.72) contrast(1.05); transition:opacity 0.35s ease, filter 0.35s ease;"></div>
    <div style="position:absolute; inset:0; z-index:1; background:linear-gradient(90deg, rgba(8,9,11,0.68) 0%, rgba(8,9,11,0.42) 50%, rgba(8,9,11,0.72) 100%); pointer-events:none;"></div>
    {progress_bar_html}

    <div data-ad-role="content-body" style="position:relative; z-index:2; display:flex; flex-direction:column; justify-content:space-between; height:100%; transition:opacity 0.2s ease;">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">
            <a data-ad-role="title" href="/arsenal/{product['slug']}" style="font-size:clamp(1.15rem, 2.3vw, 1.45rem); font-weight:700; text-transform:uppercase; color:#ffffff; text-decoration:none; display:inline-block; letter-spacing:-0.01em; line-height:1.2; text-shadow:0 1px 4px rgba(0,0,0,0.9), 0 2px 8px rgba(0,0,0,0.85);">
                {html.escape(ad_headline)}
            </a>
            <span data-ad-role="badge">{discount_badge}</span>
        </div>

        <p data-ad-role="desc" style="display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; font-size:0.86rem; line-height:1.45; color:rgba(255,255,255,0.92); margin:0.35rem 0; text-shadow:0 1px 3px rgba(0,0,0,0.95);">
            {html.escape(ad_desc)}
        </p>

        <div class="smart-ad-footer" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.75rem; padding-top:0.5rem; border-top:1px solid rgba(255,255,255,0.2);">
            <div data-ad-role="price" style="display:flex; align-items:baseline; gap:0.45rem; text-shadow:0 1px 3px rgba(0,0,0,0.9);">
                {price_html}
            </div>
            <div data-ad-role="actions" class="smart-ad-actions">
                {primary_cta}
                <button type="button" onclick="window.NFCart && window.NFCart.quickAdd({product['id']})" class="btn" style="background:rgba(0,0,0,0.6); color:#ffffff; border:1px solid rgba(255,255,255,0.6); padding:0.45rem 0.85rem; font-size:0.72rem; font-weight:700; cursor:pointer; backdrop-filter:blur(4px);">+ BAG</button>
            </div>
        </div>
    </div>
</div>
{rotator_script_html}
"""


def process_post_smart_ads(post_dict, products_by_sku, settings, all_prods=None):
    """Parses markdown and replaces [product:SKU] shortcodes or injects native inline smart ads with live rotation."""
    content = post_dict.get("content") or ""
    ad_mode = (post_dict.get("ad_mode") or "ALL").strip().upper()
    ad_count = int(post_dict.get("ad_count") if post_dict.get("ad_count") is not None else 1)
    ad_placement = (post_dict.get("ad_placement") or "MIDDLE").strip().upper()
    ad_interval = max(2, int(post_dict.get("ad_paragraph_interval") if post_dict.get("ad_paragraph_interval") is not None else 4))
    post_slug = post_dict.get("slug") or ""

    # Parse full Markdown into high-fidelity semantic HTML with line breaks enabled
    try:
        md = MarkdownIt("commonmark", {"html": True, "breaks": True}).enable("table")
        html_content = md.render(content)
    except Exception:
        html_content = content

    # Post-process GitHub Alert Callouts: [!WARNING], [!NOTE], [!TIP], [!CAUTION]
    html_content = re.sub(
        r"<blockquote>\s*<p>\s*\[!WARNING\](?:\s*<br\s*/?>)?\s*([\s\S]*?)</p>\s*</blockquote>",
        r'<div class="callout-alert callout-warning"><div class="callout-header">⚠️ WARNING ADVISORY</div><div class="callout-body">\1</div></div>',
        html_content,
        flags=re.IGNORECASE
    )
    html_content = re.sub(
        r"<blockquote>\s*<p>\s*\[!NOTE\](?:\s*<br\s*/?>)?\s*([\s\S]*?)</p>\s*</blockquote>",
        r'<div class="callout-alert callout-note"><div class="callout-header">ℹ️ RESEARCH NOTE</div><div class="callout-body">\1</div></div>',
        html_content,
        flags=re.IGNORECASE
    )
    html_content = re.sub(
        r"<blockquote>\s*<p>\s*\[!TIP\](?:\s*<br\s*/?>)?\s*([\s\S]*?)</p>\s*</blockquote>",
        r'<div class="callout-alert callout-tip"><div class="callout-header">💡 DEFENSIVE TIP</div><div class="callout-body">\1</div></div>',
        html_content,
        flags=re.IGNORECASE
    )
    html_content = re.sub(
        r"<blockquote>\s*<p>\s*\[!CAUTION\](?:\s*<br\s*/?>)?\s*([\s\S]*?)</p>\s*</blockquote>",
        r'<div class="callout-alert callout-caution"><div class="callout-header">⛔ CRITICAL ALERT</div><div class="callout-body">\1</div></div>',
        html_content,
        flags=re.IGNORECASE
    )

    if ad_mode in ("NONE", "SIDEBAR_ONLY"):
        return re.sub(r"(?:<p>\s*)?\[(?:ad|product)(?::([A-Za-z0-9_\-]+))?\](?:\s*</p>)?", "", html_content, flags=re.IGNORECASE)

    if all_prods is None:
        all_prods = list(products_by_sku.values())

    # Build candidate pool for rotating smart ad
    candidate_pool = []
    seen_ids = set()
    for s in post_dict.get("related_sku_list", []):
        p = products_by_sku.get(s.strip().upper())
        if p and p["id"] not in seen_ids:
            candidate_pool.append(p)
            seen_ids.add(p["id"])

    # Expand candidate pool with catalog products if fewer than 8
    for p in all_prods:
        if p["id"] not in seen_ids:
            candidate_pool.append(p)
            seen_ids.add(p["id"])
        if len(candidate_pool) >= 8:
            break

    if not candidate_pool:
        return re.sub(r"(?:<p>\s*)?\[(?:ad|product)(?::([A-Za-z0-9_\-]+))?\](?:\s*</p>)?", "", html_content, flags=re.IGNORECASE)

    manual_rendered_count = 0

    def replace_smart_ad_tag(match):
        nonlocal manual_rendered_count
        param = (match.group(1) or "").strip().upper()
        prod = None
        if param and param not in ("AUTO", "MIDDLE"):
            prod = products_by_sku.get(param)
        if not prod:
            prod = candidate_pool[manual_rendered_count % len(candidate_pool)]
        manual_rendered_count += 1
        inst_id = f"inline-smart-ad-pos{manual_rendered_count}-{uuid.uuid4().hex[:6]}"
        return render_inline_smart_ad_html(
            prod,
            settings,
            post_slug,
            candidate_pool=candidate_pool,
            initial_index=manual_rendered_count % len(candidate_pool),
            instance_id=inst_id
        )

    # 1. Replace all manual shortcodes [ad], [ad:SKU], [ad:auto], [product:SKU] case-insensitively
    ad_tag_regex = re.compile(r"(?:<p>\s*)?\[(?:ad|product)(?::([A-Za-z0-9_\-]+))?\](?:\s*</p>)?", re.IGNORECASE)
    processed = ad_tag_regex.sub(replace_smart_ad_tag, html_content)

    # 3. Automatic in-article placement if more ads needed
    needed_ads = max(0, ad_count - manual_rendered_count)
    if needed_ads > 0 and ad_placement != "MANUAL" and ad_mode in ("ALL", "INLINE_AUTO"):
        paragraphs = processed.split("</p>")
        total_p = len(paragraphs)
        if total_p <= 2:
            prod = candidate_pool[manual_rendered_count % len(candidate_pool)]
            inst_id = f"inline-smart-ad-auto1-{uuid.uuid4().hex[:6]}"
            ad_html = render_inline_smart_ad_html(prod, settings, post_slug, candidate_pool=candidate_pool, initial_index=manual_rendered_count % len(candidate_pool), instance_id=inst_id)
            processed += ad_html
        else:
            insert_indices = []
            if ad_placement == "PARAGRAPH_INTERVAL":
                for i in range(needed_ads):
                    idx = (i + 1) * ad_interval
                    if idx < total_p - 1:
                        insert_indices.append(idx)
            elif ad_placement == "DISTRIBUTED" or needed_ads > 1:
                step = total_p / float(needed_ads + 1)
                for i in range(needed_ads):
                    idx = int(round(step * (i + 1)))
                    if 0 < idx < total_p:
                        insert_indices.append(idx)
            else: # MIDDLE and needed_ads == 1
                insert_indices.append(total_p // 2)

            insert_indices = sorted(list(set(insert_indices)))

            new_parts = []
            ad_inject_idx = 0
            for p_idx, para in enumerate(paragraphs):
                new_parts.append(para)
                if p_idx in insert_indices and ad_inject_idx < needed_ads:
                    cur_idx = (manual_rendered_count + ad_inject_idx) % len(candidate_pool)
                    prod = candidate_pool[cur_idx]
                    inst_id = f"inline-smart-ad-auto{ad_inject_idx + 1}-{uuid.uuid4().hex[:6]}"
                    ad_banner = render_inline_smart_ad_html(prod, settings, post_slug, candidate_pool=candidate_pool, initial_index=cur_idx, instance_id=inst_id)
                    new_parts.append(ad_banner)
                    ad_inject_idx += 1

            processed = "</p>".join(new_parts)

    return processed




def compute_analytics_summary(conn, days=14):
    days = max(1, min(90, int(days)))
    now = datetime.now()
    cutoff_str = (now - timedelta(days=days)).strftime("%Y-%m-%d 00:00:00")
    active_cutoff = (now - timedelta(seconds=90)).strftime("%Y-%m-%d %H:%M:%S")

    kpi_row = conn.execute("""
    SELECT
        COUNT(*) AS total_views,
        COUNT(DISTINCT visitor_id) AS unique_visitors,
        COUNT(DISTINCT session_id) AS total_sessions,
        ROUND(AVG(duration_seconds), 1) AS avg_dwell_seconds,
        ROUND(AVG(max_scroll_pct), 1) AS avg_scroll_pct,
        SUM(CASE WHEN page_type = 'PRODUCT' OR page_type = 'SHOP' THEN 1 ELSE 0 END) AS product_section_views,
        SUM(CASE WHEN page_type = 'BLOG_POST' OR page_type = 'BLOG_INDEX' THEN 1 ELSE 0 END) AS blog_section_views,
        ROUND(AVG(CASE WHEN page_type = 'PRODUCT' THEN duration_seconds END), 1) AS avg_product_dwell,
        ROUND(AVG(CASE WHEN page_type = 'BLOG_POST' THEN duration_seconds END), 1) AS avg_blog_dwell
    FROM analytics_pageviews
    WHERE page_type NOT IN ('ADMIN', 'AUTH') AND created_at >= ?
    """, (cutoff_str,)).fetchone()

    active_now = conn.execute("""
    SELECT COUNT(DISTINCT session_id) FROM analytics_pageviews
    WHERE last_ping_at >= ?
    """, (active_cutoff,)).fetchone()[0]

    ev_rows = conn.execute("""
    SELECT event_type, COUNT(*) AS cnt
    FROM analytics_events
    WHERE created_at >= ?
    GROUP BY event_type
    """, (cutoff_str,)).fetchall()
    ev_counts = {r["event_type"]: r["cnt"] for r in ev_rows}

    ad_impressions = ev_counts.get("SMART_AD_IMPRESSION", 0)
    ad_clicks = ev_counts.get("SMART_AD_CLICK", 0)
    cart_adds = ev_counts.get("ADD_TO_CART", 0)
    tg_clicks = ev_counts.get("TELEGRAM_BUY_CLICK", 0)
    ad_ctr = round((ad_clicks / ad_impressions) * 100, 1) if ad_impressions > 0 else 0.0

    orders_stats = conn.execute("""
    SELECT
        COUNT(*) AS total_orders,
        SUM(CASE WHEN status = 'COMPLETED' THEN total_amount ELSE 0 END) AS completed_revenue,
        SUM(total_amount) AS pipeline_revenue
    FROM orders
    """).fetchone()

    timeline_labels = []
    timeline_product_views = []
    timeline_blog_views = []
    timeline_tg_clicks = []
    timeline_avg_dwell = []

    daily_pv = conn.execute("""
    SELECT
        substr(created_at, 1, 10) AS d,
        SUM(CASE WHEN page_type IN ('PRODUCT', 'SHOP') THEN 1 ELSE 0 END) AS p_views,
        SUM(CASE WHEN page_type IN ('BLOG_POST', 'BLOG_INDEX') THEN 1 ELSE 0 END) AS b_views,
        ROUND(AVG(duration_seconds), 1) AS avg_stay
    FROM analytics_pageviews
    WHERE page_type NOT IN ('ADMIN', 'AUTH') AND created_at >= ?
    GROUP BY substr(created_at, 1, 10)
    """, (cutoff_str,)).fetchall()
    pv_by_day = {r["d"]: r for r in daily_pv}

    daily_ev = conn.execute("""
    SELECT
        substr(created_at, 1, 10) AS d,
        SUM(CASE WHEN event_type IN ('TELEGRAM_BUY_CLICK', 'SMART_AD_CLICK') THEN 1 ELSE 0 END) AS conversions
    FROM analytics_events
    WHERE created_at >= ?
    GROUP BY substr(created_at, 1, 10)
    """, (cutoff_str,)).fetchall()
    ev_by_day = {r["d"]: r["conversions"] for r in daily_ev}

    for i in range(days - 1, -1, -1):
        d_str = (now - timedelta(days=i)).strftime("%Y-%m-%d")
        short_label = (now - timedelta(days=i)).strftime("%b %d")
        timeline_labels.append(short_label)
        row_d = pv_by_day.get(d_str)
        timeline_product_views.append(int(row_d["p_views"] or 0) if row_d else 0)
        timeline_blog_views.append(int(row_d["b_views"] or 0) if row_d else 0)
        timeline_avg_dwell.append(float(row_d["avg_stay"] or 0) if row_d else 0.0)
        timeline_tg_clicks.append(int(ev_by_day.get(d_str, 0)))

    products_list = conn.execute("SELECT sku, name, slug, price, category FROM products ORDER BY id ASC").fetchall()
    product_analytics = []
    for prod in products_list:
        p_stat = conn.execute("""
        SELECT
            COUNT(*) AS views,
            COUNT(DISTINCT visitor_id) AS uniques,
            ROUND(AVG(duration_seconds), 1) AS avg_stay,
            ROUND(AVG(max_scroll_pct), 1) AS avg_scroll
        FROM analytics_pageviews
        WHERE page_type = 'PRODUCT' AND target_slug = ? AND created_at >= ?
        """, (prod["slug"], cutoff_str)).fetchone()

        p_ev = conn.execute("""
        SELECT
            SUM(CASE WHEN event_type = 'SMART_AD_CLICK' THEN 1 ELSE 0 END) AS ad_clicks,
            SUM(CASE WHEN event_type = 'ADD_TO_CART' THEN 1 ELSE 0 END) AS cart_adds,
            SUM(CASE WHEN event_type = 'TELEGRAM_BUY_CLICK' THEN 1 ELSE 0 END) AS tg_buys
        FROM analytics_events
        WHERE target_sku = ? AND created_at >= ?
        """, (prod["sku"], cutoff_str)).fetchone()

        views_cnt = int(p_stat["views"] or 0)
        tg_cnt = int(p_ev["tg_buys"] or 0)
        conv_rate = round((tg_cnt / views_cnt) * 100, 1) if views_cnt > 0 else 0.0

        product_analytics.append({
            "sku": prod["sku"],
            "name": prod["name"],
            "slug": prod["slug"],
            "price": prod["price"],
            "category": prod["category"],
            "views": views_cnt,
            "uniques": int(p_stat["uniques"] or 0),
            "avg_stay_sec": float(p_stat["avg_stay"] or 0.0),
            "avg_scroll_pct": float(p_stat["avg_scroll"] or 0.0),
            "ad_clicks": int(p_ev["ad_clicks"] or 0),
            "cart_adds": int(p_ev["cart_adds"] or 0),
            "tg_buys": tg_cnt,
            "conversion_pct": conv_rate
        })

    posts_list = conn.execute("SELECT title, slug, cve_id, severity, related_skus FROM posts ORDER BY id ASC").fetchall()
    blog_analytics = []
    for post in posts_list:
        b_stat = conn.execute("""
        SELECT
            COUNT(*) AS views,
            COUNT(DISTINCT visitor_id) AS uniques,
            ROUND(AVG(duration_seconds), 1) AS avg_stay,
            ROUND(AVG(max_scroll_pct), 1) AS avg_scroll
        FROM analytics_pageviews
        WHERE page_type = 'BLOG_POST' AND target_slug = ? AND created_at >= ?
        """, (post["slug"], cutoff_str)).fetchone()

        source_path = f"/intel/{post['slug']}"
        b_ev = conn.execute("""
        SELECT
            SUM(CASE WHEN event_type = 'SMART_AD_IMPRESSION' THEN 1 ELSE 0 END) AS impressions,
            SUM(CASE WHEN event_type = 'SMART_AD_CLICK' THEN 1 ELSE 0 END) AS clicks
        FROM analytics_events
        WHERE source_page = ? AND created_at >= ?
        """, (source_path, cutoff_str)).fetchone()

        v_cnt = int(b_stat["views"] or 0)
        imp_cnt = max(v_cnt, int(b_ev["impressions"] or 0))
        clk_cnt = int(b_ev["clicks"] or 0)
        ctr = round((clk_cnt / imp_cnt) * 100, 1) if imp_cnt > 0 else 0.0

        blog_analytics.append({
            "title": post["title"],
            "slug": post["slug"],
            "cve_id": post["cve_id"],
            "severity": post["severity"],
            "related_skus": post["related_skus"],
            "views": v_cnt,
            "uniques": int(b_stat["uniques"] or 0),
            "avg_stay_sec": float(b_stat["avg_stay"] or 0.0),
            "avg_scroll_pct": float(b_stat["avg_scroll"] or 0.0),
            "ad_impressions": imp_cnt,
            "ad_clicks": clk_cnt,
            "ad_ctr_pct": ctr
        })

    os_rows = conn.execute("""
    SELECT os_name, COUNT(*) AS cnt
    FROM analytics_pageviews
    WHERE page_type NOT IN ('ADMIN', 'AUTH') AND created_at >= ?
    GROUP BY os_name
    ORDER BY cnt DESC
    """, (cutoff_str,)).fetchall()

    ref_rows = conn.execute("""
    SELECT referrer, COUNT(*) AS cnt
    FROM analytics_pageviews
    WHERE page_type NOT IN ('ADMIN', 'AUTH') AND created_at >= ?
    GROUP BY referrer
    ORDER BY cnt DESC
    LIMIT 6
    """, (cutoff_str,)).fetchall()

    recent_sessions = [
        dict(r)
        for r in conn.execute("""
        SELECT visit_token, visitor_id, page_type, target_slug, target_title,
               duration_seconds, max_scroll_pct, referrer, device_type, os_name, created_at, last_ping_at
        FROM analytics_pageviews
        WHERE page_type NOT IN ('ADMIN', 'AUTH')
        ORDER BY id DESC
        LIMIT 200
        """).fetchall()
    ]

    return {
        "kpis": {
            "active_visitors_now": max(1, active_now),
            "total_views": int(kpi_row["total_views"] or 0),
            "unique_visitors": int(kpi_row["unique_visitors"] or 0),
            "total_sessions": int(kpi_row["total_sessions"] or 0),
            "avg_dwell_seconds": float(kpi_row["avg_dwell_seconds"] or 0.0),
            "avg_scroll_pct": float(kpi_row["avg_scroll_pct"] or 0.0),
            "product_section_views": int(kpi_row["product_section_views"] or 0),
            "blog_section_views": int(kpi_row["blog_section_views"] or 0),
            "avg_product_dwell": float(kpi_row["avg_product_dwell"] or 0.0),
            "avg_blog_dwell": float(kpi_row["avg_blog_dwell"] or 0.0),
            "smart_ad_impressions": ad_impressions,
            "smart_ad_clicks": ad_clicks,
            "smart_ad_ctr_pct": ad_ctr,
            "cart_adds": cart_adds,
            "telegram_buy_clicks": tg_clicks,
            "total_orders": int(orders_stats["total_orders"] or 0),
            "completed_revenue": float(orders_stats["completed_revenue"] or 0.0),
            "pipeline_revenue": float(orders_stats["pipeline_revenue"] or 0.0)
        },
        "timeline": {
            "labels": timeline_labels,
            "product_views": timeline_product_views,
            "blog_views": timeline_blog_views,
            "telegram_conversions": timeline_tg_clicks,
            "avg_dwell": timeline_avg_dwell
        },
        "products": product_analytics,
        "blogs": blog_analytics,
        "os_breakdown": [{"os": r["os_name"], "count": r["cnt"]} for r in os_rows],
        "referrers": [{"referrer": r["referrer"], "count": r["cnt"]} for r in ref_rows],
        "recent_stream": recent_sessions
    }


def compute_pagination_pages(current_page, total_pages):
    """
    Computes a list of page numbers and ellipsis (None)
    for rendering numbered pagination controls.
    """
    if total_pages <= 7:
        return list(range(1, total_pages + 1))
    pages = []
    if current_page <= 4:
        pages.extend(range(1, 5))
        pages.append(None)
        pages.append(total_pages)
    elif current_page >= total_pages - 3:
        pages.append(1)
        pages.append(None)
        pages.extend(range(total_pages - 3, total_pages + 1))
    else:
        pages.append(1)
        pages.append(None)
        pages.extend([current_page - 1, current_page, current_page + 1])
        pages.append(None)
        pages.append(total_pages)
    return pages



