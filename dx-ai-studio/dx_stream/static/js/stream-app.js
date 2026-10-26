/**
 * DX Stream — main app logic
 */
const DXStream = (() => {
    const S = {
        currentPage: 'dashboard',
        lang: localStorage.getItem('dx-lang') || 'en',
    };

    const $ = id => document.getElementById(id);
    // Detect the proxy prefix: /stream/api/... or /api/...
    const _base = (() => {
        const m = location.pathname.match(/^(\/stream)\/?/);
        return m ? m[1] : '';
    })();
    const api = (url, opts) => fetch(_base + url, opts).then(async r => {
        let payload = null;
        try {
            payload = await r.json();
        } catch (e) {
            if (r.ok) throw e;
        }
        if (r.ok) return payload;

        payload = payload && typeof payload === 'object' ? payload : {};
        return {
            ...payload,
            error: payload.message || payload.detail || payload.error || r.statusText || `HTTP ${r.status}`,
            error_code: payload.error || 'http_error',
            status: r.status,
        };
    }).catch(e => ({ error: e && e.message ? e.message : String(e) }));
    const postJ = (url, body) => api(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });

    function _cleanupTimers() {
        if (DXStream._statusTimer) { clearInterval(DXStream._statusTimer); DXStream._statusTimer = null; }
        if (DXStream._setupPollTimer) { clearInterval(DXStream._setupPollTimer); DXStream._setupPollTimer = null; }
        if (typeof DXStream._setupCleanup === 'function') DXStream._setupCleanup();
        if (DXStream._statsTimer) { clearInterval(DXStream._statsTimer); DXStream._statsTimer = null; }
    }

    function nav(page) {
        _cleanupTimers();
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        const pageEl = $('page-' + page);
        if (pageEl) pageEl.classList.add('active');
        S.currentPage = page;

        // Unified shell: a top tab row instead of a left nav. The active tab is marked with aria-current
        // (dx-shell.css styles that, not class="active").
        const tabs = document.querySelectorAll('.dx-tab');
        tabs.forEach(t => {
            if (t.dataset.page === page) t.setAttribute('aria-current', 'page');
            else t.removeAttribute('aria-current');
        });

        // The header page name reuses the active tab label. Tabs go through the data-i18n dictionary,
        // so a separate language branch in the header would drift from them.
        const label = document.querySelector('.dx-tab[data-page="' + page + '"] span');
        const slot = $('dxShellPage');
        if (slot && label) slot.textContent = label.textContent.trim();

        // If the active tab sat in the overflow menu, bring it back to the row.
        if (window.DXTabs) DXTabs.reflowAll();

        // Call the page's init function
        const initFn = page.replace(/-/g, '') + 'Init';
        if (typeof DXStream[initFn] === 'function') DXStream[initFn]();
    }

    function toggleLang() { if (typeof DXToolbar !== 'undefined') DXToolbar.toggleLang(); }

    function _applyLang() {
        if (typeof DXI18n !== 'undefined') {
            DXI18n.applyLang();
        }
    }

    // The unified shell has no collapsible sidebar; the 56px rail is always visible.
    // Kept as a no-op because external callers may still call it.
    function toggleSidebar() { /* no sidebar in the unified shell */ }

    function toast(msg, type = 'info') {
        const c = $('toast-container');
        if (!c) return;
        // Skip duplicate messages
        var existing = c.querySelectorAll('.toast');
        for (var i = 0; i < existing.length; i++) {
            if (existing[i].textContent === msg) return;
        }
        // Keep at most 5
        while (c.children.length >= 5) c.removeChild(c.firstChild);
        const el = document.createElement('div');
        el.className = 'toast toast-' + type;
        el.textContent = msg;
        c.appendChild(el);
        requestAnimationFrame(() => el.classList.add('show'));
        setTimeout(() => el.remove(), 4000);
    }

    function confirmModal(title, message) {
        return new Promise(resolve => {
            var overlay = $('confirm-modal-overlay');
            if (!overlay) {
                overlay = document.createElement('dialog');
                overlay.id = 'confirm-modal-overlay';
                overlay.className = 'modal-overlay';
                overlay.innerHTML = '<div class="modal confirm-modal">' +
                    '<div class="modal-header"><h3 id="confirm-modal-title"></h3></div>' +
                    '<div class="modal-body"><p id="confirm-modal-msg"></p></div>' +
                    '<div class="modal-footer">' +
                        '<button class="btn btn-ghost btn-sm" id="confirm-modal-cancel">' +
                            '<span data-i18n="Cancel">Cancel</span></button>' +
                        '<button class="btn btn-primary btn-sm" id="confirm-modal-ok">' +
                            '<span data-i18n="OK">OK</span></button>' +
                    '</div></div>';
                document.body.appendChild(overlay);
            }
            $('confirm-modal-title').textContent = title;
            $('confirm-modal-msg').textContent = message;
            overlay.showModal();
            function cleanup(result) {
                overlay.close();
                $('confirm-modal-ok').onclick = null;
                $('confirm-modal-cancel').onclick = null;
                resolve(result);
            }
            $('confirm-modal-ok').onclick = () => cleanup(true);
            $('confirm-modal-cancel').onclick = () => cleanup(false);
            overlay.onclick = e => { if (e.target === overlay) cleanup(false); };
        });
    }

    window.addEventListener('keydown', e => {
        // Ignore Delete/Backspace inside input/textarea
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
        if (S.currentPage === 'pipeline') {
            if (e.key === 'Delete') {
                if (DXStream._pipeState && (DXStream._pipeState.selectedNodes.length > 0 || DXStream._pipeState.selectedNode)) {
                    DXStream._deleteSelectedNode();
                    return;
                }
                if (DXStream._pipeState && DXStream._pipeState.selectedEdge) {
                    DXStream._deleteSelectedEdge();
                    return;
                }
            }
            if (e.key === 'Escape') {
                DXStream._deselectAll();
                return;
            }
            if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
                e.preventDefault();
                DXStream._undo();
                return;
            }
            if ((e.ctrlKey || e.metaKey) && (e.key === 'Z' || (e.key === 'z' && e.shiftKey))) {
                e.preventDefault();
                DXStream._redo();
                return;
            }
            if ((e.ctrlKey || e.metaKey) && e.key === 'c') {
                e.preventDefault();
                DXStream._copyNodes();
                return;
            }
            if ((e.ctrlKey || e.metaKey) && e.key === 'v') {
                e.preventDefault();
                DXStream._pasteNodes();
                return;
            }
            if ((e.ctrlKey || e.metaKey) && e.key === 'a') {
                e.preventDefault();
                // Select all
                if (DXStream._pipeState && DXStream._pipeState.nodes) {
                    DXStream._pipeState.selectedNodes = DXStream._pipeState.nodes.map(function (n) { return n.id; });
                    DXStream._pipeState.selectedNode = DXStream._pipeState.selectedNodes[0] || null;
                }
                if (typeof _refreshCanvas === 'function') _refreshCanvas();   // otherwise the selection does not show
                return;
            }
        }
    });

    // In the launcher, toolbar.js + i18n.js sync theme/lang

    // Initialise on load
    window.addEventListener('DOMContentLoaded', () => {
        _applyLang();
        nav('dashboard');
    });

    function escHtml(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;'); }

    return { S, $, api, postJ, nav, toggleLang, toggleSidebar, toast, confirmModal, _base, escHtml,
        /* One string in the chosen language (ko, en, ja, zh-CN, zh-TW, es). Plain text, not per-language
           <span>s: toasts and confirm dialogs set textContent, so markup would show up raw. */
        _L: function(ko, en, ja, zhCN, zhTW, es) {
            var lang = (window.DXI18n && DXI18n.lang) || S.lang || 'en';
            var v = { ko: ko, en: en, ja: ja, 'zh-CN': zhCN, 'zh-TW': zhTW, es: es }[lang];
            return v || en;
        }
    };
})();

// Expose to window so external scripts (tutorial.js, etc.) can access via window.DXStream
window.DXStream = DXStream;

// What is playing, on every page: keeps the header pill current outside the Dashboard, and tells the
// Demo page when a Pipeline Builder run has replaced its demo on the server.
DXStream._pollPlayback = function () {
    if (document.hidden) return;
    DXStream.api('/api/pipeline/status').then(function (st) {
        if (!st || st.error) return;
        if (typeof DXStream.updatePipelineBadge === 'function') DXStream.updatePipelineBadge(st);
        if (typeof DXStream._demoSyncWithServer === 'function') DXStream._demoSyncWithServer(st);
    });
};
setInterval(DXStream._pollPlayback, 4000);

// Sync with shared i18n — stream-lang-refresh.js owns onLangChange dispatch
DXStream.T = window.T;
if (typeof DXI18n !== 'undefined') {
  DXStream.S.lang = DXI18n.lang;
  // The page reload on a language change is owned by stream-lang-refresh.js (once per change).
}
