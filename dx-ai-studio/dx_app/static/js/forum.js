/* ═══════════════════════════════════════════════════════════
   forum.js — DX-APP Community Board
   Categories: ask_deepx (DeepX에게 질문) | community (일반토론)
   Features: post list, filter/sort/search, post detail modal,
             comments, like system, new post modal
   ═══════════════════════════════════════════════════════════ */
'use strict';

let _forumSort = 'latest';
let _forumCat  = '';

/* ── User token for like tracking (localStorage, no auth) ── */
function _fTok() {
  let t = localStorage.getItem('dx-ftok');
  if (!t) {
    t = Math.random().toString(36).slice(2) + Date.now().toString(36);
    localStorage.setItem('dx-ftok', t);
  }
  return t;
}

/* ── Timestamp formatting ─────────────────────────────────── */
function _fmtTs(ts) {
  if (!ts) return '';
  const diff = Date.now() / 1000 - ts;
  if (diff < 60)       return T('just now');
  if (diff < 3600)     return `${Math.floor(diff / 60)}${T(' min ago')}`;
  if (diff < 86400)    return `${Math.floor(diff / 3600)}${T(' hours ago')}`;
  if (diff < 86400*30) return `${Math.floor(diff / 86400)}${T(' days ago')}`;
  return fmtDate(ts);
}

/* ── Category badge HTML ──────────────────────────────────── */
function _catBadge(cat) {
  return cat === 'ask_deepx'
    ? '<span class="fcbadge fcbadge-ask">🏢 '+T('Ask DeepX')+'</span>'
    : '<span class="fcbadge fcbadge-comm">💬 '+T('Community')+'</span>';
}

/* ══════════════════════════════════════════════════════════
   LOAD & RENDER LIST
   ══════════════════════════════════════════════════════════ */
async function loadForum() {
  const area = $('forum-list-area');
  if (!area) return;
  area.innerHTML = '<div class="forum-state">'+T('⏳ Loading…')+'</div>';

  const params = new URLSearchParams({ sort: _forumSort });
  if (_forumCat) params.set('category', _forumCat);
  const q = $('forum-search')?.value?.trim();
  if (q) params.set('q', q);

  try {
    const data = await api(`/api/forum/posts?${params}`);
    const posts = Array.isArray(data.posts) ? data.posts : [];

    if (!posts.length) {
      area.innerHTML = `
        <div class="forum-state" style="padding:60px 20px">
          <div style="font-size:40px;margin-bottom:12px">📭</div>
          <div style="font-weight:700;color:var(--text-1);margin-bottom:6px">${T('No posts yet')}</div>
          <div style="font-size:12px">${T('Write the first post!')}</div>
        </div>`;
      return;
    }

    area.innerHTML = posts.map(p => `
      <div class="forum-item" onclick="openForumPost('${p.id}')">
        <div class="forum-item-top">
          ${_catBadge(p.category)}
          <span class="forum-item-date">${_fmtTs(p.created_at)}</span>
        </div>
        <div class="forum-item-title">${esc(p.title)}</div>
        ${p.body_preview ? `<div class="forum-item-preview">${esc(p.body_preview)}${p.body_preview.length >= 150 ? '…' : ''}</div>` : ''}
        <div class="forum-item-footer">
          <span class="forum-meta-chip">👤 ${esc(p.author)}</span>
          <span class="forum-meta-chip">👍 ${p.likes}</span>
          <span class="forum-meta-chip">💬 ${p.comment_count}</span>
          ${(p.tags || []).map(t => `<span class="forum-tag-pill">#${esc(t)}</span>`).join('')}
        </div>
      </div>`).join('');
  } catch (e) {
    area.innerHTML = '<div class="forum-state" style="color:var(--error)">'+T('⚠️ Failed to load. Please check the server.')+'</div>';
  }
}

/* ── Sort / Category / Search controls ───────────────────── */
function forumSort(s) {
  _forumSort = s;
  document.querySelectorAll('.forum-sort-btn').forEach(b =>
    b.classList.toggle('active', b.dataset.s === s));
  loadForum();
}

function forumCat(c) {
  _forumCat = c;
  document.querySelectorAll('.forum-cat-btn').forEach(b =>
    b.classList.toggle('active', b.dataset.c === c));
  loadForum();
}

/* ══════════════════════════════════════════════════════════
   POST DETAIL MODAL
   ══════════════════════════════════════════════════════════ */
async function openForumPost(id) {
  _ensureFModal();
  const bd = $('fmodal').querySelector('.fmodal-bd');
  bd.innerHTML = '<div class="forum-state" style="padding:60px 0">'+T('⏳ Loading…')+'</div>';
  openModal('fmodal');

  const post = await api(`/api/forum/posts/${id}`);
  if (post.error) { toast(post.error, 'err'); $('fmodal').close(); return; }
  _renderFModal(post);
}

function _ensureFModal() {
  if ($('fmodal')) return;
  const d = document.createElement('dialog');
  d.id = 'fmodal';
  d.className = 'modal-overlay';
  d.innerHTML = `
    <div class="modal" style="width:740px;max-width:96vw;max-height:92vh;overflow:hidden;display:flex;flex-direction:column">
      <div class="modal-hd" style="flex-shrink:0">
        <span id="fmodal-ttl" style="display:flex;align-items:center;gap:8px;flex-wrap:wrap"></span>
        <button class="modal-x" onclick="$('fmodal').close()">✕</button>
      </div>
      <div class="fmodal-bd" style="flex:1;overflow-y:auto;padding:0"></div>
    </div>`;
  document.body.appendChild(d);
}

function _renderFModal(p) {
  const tok = _fTok();
  const liked = (p.likes || []).includes(tok);

  $('fmodal-ttl').innerHTML = `${_catBadge(p.category)}<span>${esc(p.title)}</span>`;

  $('fmodal').querySelector('.fmodal-bd').innerHTML = `
    <div style="padding:16px 20px;border-bottom:1px solid var(--border)">
      <div class="forum-item-footer" style="margin-bottom:10px">
        <span class="forum-meta-chip">👤 ${esc(p.author)}</span>
        <span class="forum-meta-chip">🕐 ${_fmtTs(p.created_at)}</span>
        ${(p.tags || []).map(t => `<span class="forum-tag-pill">#${esc(t)}</span>`).join('')}
      </div>
      <div class="forum-body-txt">${esc(p.body || '').replace(/\n/g, '<br>')}</div>
      <div style="margin-top:14px">
        <button id="flike-btn" class="btn ${liked ? 'btn-acc' : 'btn-ghost'} btn-sm"
          onclick="forumLikePost('${p.id}')">
          ${T('👍 Recommend')} <span id="flike-cnt">${(p.likes || []).length}</span>
        </button>
      </div>
    </div>
    <div style="padding:16px 20px">
      <div class="forum-cmt-hdr">${T('💬 Comments')} <span id="fmodal-cmt-cnt">${(p.comments || []).length}</span>${T('comment count suffix')}</div>
      <div id="fmodal-cmts">
        ${(p.comments || []).map(c => _renderCmt(c, p.id)).join('')}
      </div>
      <div style="margin-top:14px;border-top:1px solid var(--border);padding-top:12px">
        <div style="display:flex;gap:8px;align-items:flex-start;margin-bottom:8px">
          <input type="text" id="fcmt-nick" class="input"
            placeholder="${T('Nickname (optional)')}" style="width:130px;flex-shrink:0;height:34px">
          <textarea id="fcmt-body" class="input" rows="2"
            placeholder="${T('Enter a comment…')}"
            style="flex:1;resize:vertical;font-family:inherit;min-height:34px"></textarea>
        </div>
        <button class="btn btn-acc btn-sm" onclick="forumAddCmt('${p.id}')">${T('Post Comment')}</button>
      </div>
    </div>`;
}

function _renderCmt(c, postId) {
  const liked = (c.likes || []).includes(_fTok());
  return `
    <div class="forum-cmt" id="fcmt-${c.id}">
      <div class="forum-cmt-meta">
        <span>👤 ${esc(c.author)}</span>
        <span>·</span>
        <span>${_fmtTs(c.created_at)}</span>
      </div>
      <div class="forum-cmt-body">${esc(c.body).replace(/\n/g, '<br>')}</div>
      <button class="btn ${liked ? 'btn-acc' : 'btn-ghost'} forum-cmt-like-btn"
        onclick="forumLikeCmt('${postId}','${c.id}',this)">
        👍 <span>${(c.likes || []).length}</span>
      </button>
    </div>`;
}

/* ── Like post ────────────────────────────────────────────── */
async function forumLikePost(postId) {
  const d = await api(`/api/forum/posts/${postId}/like`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_token: _fTok() })
  });
  if (d.error) { toast(d.error, 'err'); return; }
  const cnt = $('flike-cnt');
  if (cnt) cnt.textContent = d.likes;
  const btn = $('flike-btn');
  if (btn) btn.className = `btn ${d.liked ? 'btn-acc' : 'btn-ghost'} btn-sm`;
}

/* ── Like comment ─────────────────────────────────────────── */
async function forumLikeCmt(postId, cmtId, btn) {
  const d = await api(`/api/forum/posts/${postId}/comments/${cmtId}/like`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_token: _fTok() })
  });
  if (d.error) { toast(d.error, 'err'); return; }
  btn.querySelector('span').textContent = d.likes;
  btn.className = `btn ${d.liked ? 'btn-acc' : 'btn-ghost'} forum-cmt-like-btn`;
}

/* ── Add comment ──────────────────────────────────────────── */
async function forumAddCmt(postId) {
  const body   = $('fcmt-body')?.value?.trim();
  const author = $('fcmt-nick')?.value?.trim() || 'Anonymous';
  if (!body) { toast(T('Please enter comment content'), 'warn'); return; }

  const d = await api(`/api/forum/posts/${postId}/comments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ body, author })
  });
  if (d.error) { toast(d.error, 'err'); return; }

  $('fmodal-cmts').insertAdjacentHTML('beforeend', _renderCmt(d, postId));
  const cntEl = $('fmodal-cmt-cnt');
  if (cntEl) cntEl.textContent = parseInt(cntEl.textContent || '0') + 1;
  $('fcmt-body').value = '';
  toast(T('Comment posted 🎉'), 'ok');
}

/* ══════════════════════════════════════════════════════════
   NEW POST MODAL
   ══════════════════════════════════════════════════════════ */
function openNewPost() {
  if (!$('fpost-modal')) {
    const d = document.createElement('dialog');
    d.id = 'fpost-modal';
    d.className = 'modal-overlay';
    d.innerHTML = `
      <div class="modal" style="width:580px;max-width:96vw">
        <div class="modal-hd">
          <span>${T('✏️ New Post')}</span>
          <button class="modal-x" onclick="$('fpost-modal').close()">✕</button>
        </div>
        <div class="modal-bd" style="gap:12px;padding:20px">
          <div class="fg">
            <label>${T('Category')}</label>
            <select id="fnp-cat" class="input" style="margin-top:5px">
              <option value="ask_deepx">🏢 ${T('Ask DeepX')}</option>
              <option value="community" selected>💬 ${T('Community Discussion')}</option>
            </select>
          </div>
          <div class="fg">
            <label>${T('Nickname')} <span style="color:var(--text-3);font-size:11px">${T('(Anonymous if empty)')}</span></label>
            <input type="text" id="fnp-nick" class="input" placeholder="${T('Nickname')}" maxlength="30" style="margin-top:5px">
          </div>
          <div class="fg">
            <label>${T('Title')} <span style="color:var(--error)">*</span></label>
            <input type="text" id="fnp-title" class="input" placeholder="${T('Enter a title')}" maxlength="100" style="margin-top:5px">
          </div>
          <div class="fg">
            <label>${T('Content')} <span style="color:var(--error)">*</span></label>
            <textarea id="fnp-body" class="input" rows="7"
              placeholder="${T('Enter content…')}"
              style="margin-top:5px;resize:vertical;font-family:inherit"></textarea>
          </div>
          <div class="fg">
            <label>${T('Tags')} <span style="color:var(--text-3);font-size:11px">${T('(comma separated, max 5)')}</span></label>
            <input type="text" id="fnp-tags" class="input"
              placeholder="${T('DX-M1, YOLOv8, optimization…')}" style="margin-top:5px">
          </div>
          <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:4px">
            <button class="btn btn-ghost" onclick="$('fpost-modal').close()">${T('Cancel')}</button>
            <button class="btn btn-acc" onclick="forumSubmitPost()">${T('✅ Submit')}</button>
          </div>
        </div>
      </div>`;
    document.body.appendChild(d);
  }
  ['fnp-nick','fnp-title','fnp-body','fnp-tags'].forEach(id => {
    const el = $(id); if (el) el.value = '';
  });
  openModal('fpost-modal');
}

async function forumSubmitPost() {
  const title  = $('fnp-title')?.value?.trim();
  const body   = $('fnp-body')?.value?.trim();
  const author = $('fnp-nick')?.value?.trim() || 'Anonymous';
  const cat    = $('fnp-cat')?.value || 'community';
  const tags   = ($('fnp-tags')?.value || '').split(',').map(t => t.trim()).filter(Boolean);

  if (!title) { toast(T('Please enter a title'), 'warn'); return; }
  if (!body)  { toast(T('Please enter content'), 'warn'); return; }

  const d = await api('/api/forum/posts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, body, category: cat, author, tags })
  });
  if (d.error) { toast(d.error, 'err'); return; }

  $('fpost-modal').close();
  toast(T('Post published 🎉'), 'ok');
  loadForum();
}
if (typeof registerLangRefresher === 'function') {
  registerLangRefresher(function refreshForumLanguage() {
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
  });
}
