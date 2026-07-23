/**
 * DX Stream — 메인 앱 로직
 */
const DXStream = (() => {
    const S = {
        currentPage: 'dashboard',
        lang: localStorage.getItem('dx-lang') || 'en',
    };

    const $ = id => document.getElementById(id);
    // 프록시 경로 자동 감지: /stream/api/... 또는 /api/...
    const _base = (() => {
        const m = location.pathname.match(/^(\/stream)\/?/);
        return m ? m[1] : '';
    })();
    const api = (url, opts) => fetch(_base + url, opts).then(r => r.ok ? r.json() : Promise.reject(r.statusText)).catch(e => ({ error: String(e) }));
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
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        const pageEl = $('page-' + page);
        const navEl = document.querySelector(`.nav-item[data-page="${page}"]`);
        if (pageEl) pageEl.classList.add('active');
        if (navEl) navEl.classList.add('active');
        S.currentPage = page;
        const titleLabel = navEl ? navEl.querySelector('.nav-label') : null;
        const title = titleLabel
            ? (titleLabel.querySelector('.' + S.lang) || titleLabel.querySelector('.ko') || titleLabel.querySelector('.en') || titleLabel).textContent.trim()
            : page;
        const titleEl = $('topbar-title');
        if (titleEl && titleLabel) {
            const koSpan = titleLabel.querySelector('.ko');
            const enSpan = titleLabel.querySelector('.en');
            const jaSpan = titleLabel.querySelector('.ja');
            const zhCNSpan = titleLabel.querySelector('.zh-CN');
            const zhTWSpan = titleLabel.querySelector('.zh-TW');
            if (koSpan && enSpan) {
                titleEl.innerHTML = '<span class="ko">' + koSpan.textContent + '</span><span class="en">' + enSpan.textContent + '</span>'
                    + (jaSpan ? '<span class="ja">' + jaSpan.textContent + '</span>' : '')
                    + (zhCNSpan ? '<span class="zh-CN">' + zhCNSpan.textContent + '</span>' : '')
                    + (zhTWSpan ? '<span class="zh-TW">' + zhTWSpan.textContent + '</span>' : '');
            } else {
                titleEl.textContent = title;
            }
        } else if (titleEl) {
            titleEl.textContent = title;
        }
        // 페이지별 init 함수 호출
        const initFn = page.replace(/-/g, '') + 'Init';
        if (typeof DXStream[initFn] === 'function') DXStream[initFn]();
    }

    function toggleLang() { if (typeof DXToolbar !== 'undefined') DXToolbar.toggleLang(); }

    function _applyLang() {
        if (typeof DXI18n !== 'undefined') {
            DXI18n.applyLang();
        }
    }

    function toggleSidebar() {
        $('sidebar').classList.toggle('collapsed');
    }

    function toast(msg, type = 'info') {
        const c = $('toast-container');
        if (!c) return;
        // 중복 메시지 방지
        var existing = c.querySelectorAll('.toast');
        for (var i = 0; i < existing.length; i++) {
            if (existing[i].textContent === msg) return;
        }
        // 최대 5개 제한
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
                            '<span class="ko">취소</span><span class="en">Cancel</span></button>' +
                        '<button class="btn btn-primary btn-sm" id="confirm-modal-ok">' +
                            '<span class="ko">확인</span><span class="en">OK</span></button>' +
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
        // input/textarea 내부에서 Delete/Backspace 는 무시
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
                // 전체 선택
                if (DXStream._pipeState && DXStream._pipeState.nodes) {
                    DXStream._pipeState.selectedNodes = DXStream._pipeState.nodes.map(function (n) { return n.id; });
                    DXStream._pipeState.selectedNode = DXStream._pipeState.selectedNodes[0] || null;
                }
                return;
            }
        }
    });

    // 런처에서 theme/lang 동기화는 toolbar.js + i18n.js가 처리

    // 로드 시 초기화
    window.addEventListener('DOMContentLoaded', () => {
        _applyLang();
        nav('dashboard');
    });

    function escHtml(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;'); }

    return { S, $, api, postJ, nav, toggleLang, toggleSidebar, toast, confirmModal, _base, escHtml,
        _L: function(ko, en, ja, zhCN, zhTW) {
            return '<span class="ko">' + ko + '</span>'
                 + '<span class="en">' + en + '</span>'
                 + '<span class="ja">' + ja + '</span>'
                 + '<span class="zh-CN">' + zhCN + '</span>'
                 + '<span class="zh-TW">' + zhTW + '</span>';
        }
    };
})();

// Expose to window so external scripts (tutorial.js, etc.) can access via window.DXStream
window.DXStream = DXStream;

// Sync with shared i18n — stream-lang-refresh.js owns onLangChange dispatch
DXStream.T = window.T;
if (typeof DXI18n !== 'undefined') {
  DXStream.S.lang = DXI18n.lang;
  if (typeof DXI18n.onLangChange === 'function') {
    DXI18n.onLangChange(function () {
      if (DXStream.S.currentPage && typeof DXStream.nav === 'function') {
        DXStream.nav(DXStream.S.currentPage);
      }
    });
  }
}
