// Simulate minimal browser DOM environment
global.window = global;
global.sessionStorage = {
    _data: {},
    getItem(k) { return this._data[k] || null; },
    setItem(k, v) { this._data[k] = String(v); },
    removeItem(k) { delete this._data[k]; }
};

class Element {
    constructor(id = '', tag = 'div') {
        this.id = id;
        this.tagName = tag.toUpperCase();
        this.classList = {
            _classes: new Set(),
            add(c) { this._classes.add(c); },
            remove(c) { this._classes.delete(c); },
            contains(c) { return this._classes.has(c); }
        };
        this.style = {};
        this.children = [];
        this._attrs = {};
    }
    getAttribute(k) { return this._attrs[k] || null; }
    setAttribute(k, v) { this._attrs[k] = String(v); }
    querySelectorAll(sel) { return []; }
    querySelector(sel) { return null; }
    appendChild(c) { this.children.push(c); return c; }
    closest() { return null; }
    addEventListener() {}
}

const elementsById = {};
const elementsByClass = {
    'admin-header-btn': [],
    'feature-subtabs': [],
    'subnav-item': [],
    'admin-module': []
};

// Create the modules
const moduleIds = [
    'mod-analytics', 'mod-analytics-matrix', 'mod-products', 'mod-product-editor',
    'mod-curation-products', 'mod-reviews', 'mod-posts', 'mod-post-editor',
    'mod-curation-posts', 'mod-comments', 'mod-orders', 'mod-settings', 'mod-seo',
    'mod-themes-visual', 'mod-themes-text', 'mod-users', 'mod-audit'
];
moduleIds.forEach(id => {
    const el = new Element(id, 'section');
    el.classList.add('admin-module');
    elementsById[id] = el;
    elementsByClass['admin-module'].push(el);
});
elementsById['mod-analytics'].classList.add('active');

const featureIds = ['analytics', 'products', 'journal', 'orders', 'system'];
featureIds.forEach(f => {
    const btn = new Element('', 'button');
    btn.setAttribute('data-feature', f);
    elementsByClass['admin-header-btn'].push(btn);

    const subtabs = new Element(`subtabs-${f}`, 'div');
    elementsById[`subtabs-${f}`] = subtabs;
    elementsByClass['feature-subtabs'].push(subtabs);
});

elementsById['theme-preview-iframe'] = new Element('theme-preview-iframe', 'iframe');

global.document = {
    getElementById(id) { return elementsById[id] || null; },
    querySelectorAll(sel) {
        if (sel === '.admin-header-btn') return elementsByClass['admin-header-btn'];
        if (sel === '.feature-subtabs') return elementsByClass['feature-subtabs'];
        if (sel === '.admin-module') return elementsByClass['admin-module'];
        if (sel.includes('.subnav-item')) return [];
        return [];
    },
    querySelector(sel) {
        if (sel === '.admin-container') return new Element('admin-container');
        return null;
    },
    addEventListener(ev, fn) {}
};

global.location = { reload() {} };
global.window.INITIAL_ANALYTICS_DATA = { kpis: {}, products: [], blogs: [], recent_stream: [] };
global.window.ADMIN_CATALOG_PRODUCTS = [];
global.window.ADMIN_POSTS = [];
global.window.ORIGINAL_THEME_SETTINGS = {};

console.log("Loading scripts in sequence...");
const fs = require('fs');
const scripts = [
    'static/js/admin/admin_core.js',
    'static/js/admin/admin_analytics.js',
    'static/js/admin/admin_orders.js',
    'static/js/admin/admin_products.js',
    'static/js/admin/admin_posts.js',
    'static/js/admin/admin_users.js',
    'static/js/admin/admin_settings.js',
    'static/js/admin/admin_themes.js',
    'static/js/admin/admin_reviews.js',
    'static/js/admin/admin_comments.js',
    'static/js/admin/admin_curation.js'
];

global.window.addEventListener = function() {};
global.window.scrollTo = function() {};

const vm = require('vm');

scripts.forEach(s => {
    try {
        const code = fs.readFileSync(s, 'utf8');
        vm.runInThisContext(code, { filename: s });
        console.log("✓ Loaded: " + s);
    } catch(err) {
        console.error("FAIL on " + s + ":", err);
    }
});

console.log("\nTesting switchFeature calls...");
featureIds.forEach(f => {
    try {
        global.switchFeature(f);
        const activeModules = elementsByClass['admin-module'].filter(m => m.classList.contains('active'));
        console.log(`✓ switchFeature('${f}') -> active module:`, activeModules.map(m => m.id));
    } catch(e) {
        console.error(`FAIL switchFeature('${f}'):`, e);
    }
});

console.log("\nTesting switchSubtab calls...");
const subtabTests = [
    ['analytics', 'overview', 'mod-analytics'],
    ['analytics', 'matrix-full', 'mod-analytics-matrix'],
    ['products', 'catalog', 'mod-products'],
    ['products', 'studio', 'mod-product-editor'],
    ['products', 'curation', 'mod-curation-products'],
    ['products', 'reviews', 'mod-reviews'],
    ['journal', 'dispatches', 'mod-posts'],
    ['journal', 'studio', 'mod-post-editor'],
    ['journal', 'curation', 'mod-curation-posts'],
    ['journal', 'comments', 'mod-comments'],
    ['orders', 'all', 'mod-orders'],
    ['orders', 'pending', 'mod-orders'],
    ['system', 'settings', 'mod-settings'],
    ['system', 'seo', 'mod-seo'],
    ['system', 'themes-visual', 'mod-themes-visual'],
    ['system', 'themes-text', 'mod-themes-text'],
    ['system', 'users', 'mod-users'],
    ['system', 'audit', 'mod-audit']
];

subtabTests.forEach(([feat, sub, expectedMod]) => {
    try {
        global.switchSubtab(feat, sub);
        const activeMods = elementsByClass['admin-module'].filter(m => m.classList.contains('active')).map(m => m.id);
        const ok = activeMods.includes(expectedMod);
        console.log(`${ok ? '✓' : 'FAIL'} switchSubtab('${feat}', '${sub}') -> expected ${expectedMod}, got:`, activeMods);
    } catch(err) {
        console.error(`FAIL switchSubtab('${feat}', '${sub}'):`, err);
    }
});

