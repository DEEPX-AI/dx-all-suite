// Browse DEEPX ModelZoo, add to cart, download Q-Lite / Q-Pro models

// 티어 목록. 렌더러·카트·일괄선택이 전부 이 위에서 돈다 — 예전에는 세 군데가
// 각각 qlite/qpro 를 손으로 나열해서, Q-Master 를 받을 수 있게 된 뒤에도 화면에서
// 고를 방법이 없었다. 서버 쪽 같은 표: dx_app/core/modelzoo.py 의 _CHIP_DIRS.
var MZ_CHIPS = [
  { key: 'qlite',   label: 'Q-Lite',   col: 'mz-col-ql', chk: 'mz-chk-ql' },
  { key: 'qpro',    label: 'Q-Pro',    col: 'mz-col-qp', chk: 'mz-chk-qp' },
  { key: 'qmaster', label: 'Q-Master', col: 'mz-col-qm', chk: 'mz-chk-qm' },
];

function mzCartIsEmpty(entry) {
  if (!entry) return true;
  for (var i = 0; i < MZ_CHIPS.length; i++) {
    if (entry[MZ_CHIPS[i].key]) return false;
  }
  return true;
}

const MZ = {
  models: [],
  cart: {},           // { "AlexNet-1": { qlite: true, qpro: false, qmaster: false } }
  source: 'public',
  filter: { task: '', search: '' },
  loading: false,
  downloading: false,
  pollTimer: null,
  cartOpen: false,
};

// ── ModelZoo homepage link (follows the selected source) ────────────────────────
// public → developer.deepx.ai (open network); internal → devops publish (air-gapped only).
const MZ_SITE_URLS = {
  public: 'https://developer.deepx.ai/modelzoo/',
  internal: 'https://modelzoo-publish-api.devops.dpx.ai/publish/html',
};
function mzUpdateHomepageLink() {
  var a = $('mz-homepage-link');
  if (!a) return;
  var sel = $('mz-source');
  var src = (sel && sel.value) || MZ.source || 'public';
  a.href = MZ_SITE_URLS[src] || MZ_SITE_URLS.public;
}

async function initModelZoo() {
  mzUpdateHomepageLink();
  if (!MZ.models.length) await mzLoadModels();
  mzRenderTaskChips();
  mzRenderTable();
  mzRenderCart();
}

async function mzLoadModels() {
  MZ.loading = true;
  mzRenderLoading();
  const r = await api('/api/modelzoo/list?source=' + encodeURIComponent(MZ.source));
  MZ.loading = false;
  if (r.ok && r.models) {
    MZ.models = r.models;
  } else {
    MZ.models = [];
    toast(r.error || T('Failed to load ModelZoo'), 'err');
  }
}

function mzSwitchSource() {
  var sel = $('mz-source');
  MZ.source = sel ? sel.value : 'public';
  mzUpdateHomepageLink();
  MZ.models = [];
  with_cache_lock: { _mz_cache_ts = 0; }
  initModelZoo();
}

function mzRenderTaskChips() {
  var tasks = {};
  MZ.models.forEach(function(m) {
    var t = m.task || 'Unknown';
    tasks[t] = (tasks[t] || 0) + 1;
  });
  var keys = Object.keys(tasks).sort();
  var html = '<button class="chip' + (MZ.filter.task === '' ? ' active' : '') + '" onclick="mzFilterTask(\'\')">' + T('All') + ' ' + MZ.models.length + '</button>';
  keys.forEach(function(t) {
    var active = MZ.filter.task === t ? ' active' : '';
    html += '<button class="chip' + active + '" onclick="mzFilterTask(\'' + esc(t) + '\')">' + esc(catText(t)) + ' <span class="txt-dim">' + tasks[t] + '</span></button>';
  });
  var el = $('mz-task-chips');
  if (el) el.innerHTML = html;
}

function mzFilterTask(task) {
  MZ.filter.task = task;
  mzRenderTaskChips();
  mzRenderTable();
}

function mzFiltered() {
  var s = MZ.filter.search.toLowerCase();
  return MZ.models.filter(function(m) {
    if (MZ.filter.task && m.task !== MZ.filter.task) return false;
    if (s && m.name.toLowerCase().indexOf(s) < 0 && (m.class_name || '').toLowerCase().indexOf(s) < 0 && (m.task || '').toLowerCase().indexOf(s) < 0) return false;
    return true;
  });
}

function mzRenderLoading() {
  var tb = $('mz-tbody');
  if (tb) tb.innerHTML = '<tr><td colspan="22" style="text-align:center;padding:40px"><div class="mz-spinner"></div><div class="txt-dim mt8">' + T('Loading ModelZoo page…') + '</div></td></tr>';
}

function mzRenderTable() {
  var list = mzFiltered();
  var tb = $('mz-tbody');
  if (!tb) return;

  if (MZ.loading) { mzRenderLoading(); return; }

  if (!list.length) {
    tb.innerHTML = '<tr><td colspan="26" style="text-align:center;padding:30px;color:var(--text-faint)">' + T('No models found') + '</td></tr>';
    $('mz-count').textContent = '0 / ' + MZ.models.length;
    return;
  }

  tb.innerHTML = list.map(function(m) {
    var cart = MZ.cart[m.name];
    var anyInCart = false;
    var chipCells = '';

    for (var ci = 0; ci < MZ_CHIPS.length; ci++) {
      var chip = MZ_CHIPS[ci];
      var tier = m[chip.key];
      var inCart = !!(cart && cart[chip.key]);
      if (inCart) anyInCart = true;

      var has = !!(tier && tier.dxnn_url);
      var acc = has ? mzNl2br(esc(tier.accuracy || '–')) : '–';
      var dxnn = has ? '<a href="' + esc(tier.dxnn_url) + '" target="_blank" class="txt-link txt-xs">' + DXIcon('models') + ' dxnn</a>' : '–';
      var jsonL = (has && tier.json_url) ? '<a href="' + esc(tier.json_url) + '" target="_blank" class="txt-link txt-xs">' + DXIcon('file') + ' json</a>' : '–';

      var dl = '–';
      if (has) {
        if (tier.exists && !inCart) {
          dl = '<span class="badge b-ok txt-xs" title="' + T('Downloaded') + '">' + DXIcon('check') + '</span>';
        } else {
          dl = '<label class="mz-chk-wrap" title="' + T('Add to cart') + ' — ' + chip.label + '">'
             + '<input type="checkbox" onchange="mzToggleChip(\'' + esc(m.name) + '\',\'' + chip.key + '\')"'
             + (inCart ? ' checked' : '') + '>'
             + '<span class="mz-chk ' + chip.chk + '"></span></label>';
        }
      }

      chipCells += '<td class="' + chip.col + ' txt-xs" style="white-space:normal">' + acc + '</td>'
                 + '<td class="' + chip.col + '">' + dxnn + '</td>'
                 + '<td class="' + chip.col + '">' + jsonL + '</td>'
                 + '<td class="' + chip.col + '">' + dl + '</td>';
    }

    var onnxLink = m.onnx_url ? '<a href="' + esc(m.onnx_url) + '" target="_blank" class="txt-link txt-xs">' + DXIcon('models') + ' onnx</a>' : '–';

    var rowCls = anyInCart ? 'mz-row-selected' : '';

    return '<tr class="' + rowCls + '">'
      + '<td><label class="mz-chk-wrap"><input type="checkbox" onchange="mzToggleCart(\'' + esc(m.name) + '\')"' + (cart ? ' checked' : '') + '><span class="mz-chk"></span></label></td>'
      + '<td><span class="badge b-cat">' + esc(catText(m.task)) + '</span></td>'
      + '<td><strong>' + esc(m.name) + '</strong></td>'
      + '<td class="txt-dim txt-xs">' + esc(m.class_name || '–') + '</td>'
      + '<td class="txt-dim txt-xs">' + esc(m.dataset || '–') + '</td>'
      + '<td class="txt-dim">' + esc(m.input_resolution || '–') + '</td>'
      + '<td class="txt-dim txt-xs">' + esc(m.ops || '–') + '</td>'
      + '<td class="txt-dim txt-xs">' + esc(m.params || '–') + '</td>'
      + '<td class="txt-dim txt-xs">' + esc(m.license || '–') + '</td>'
      + '<td class="txt-dim txt-xs" style="white-space:normal">' + mzNl2br(esc(m.metric || '–')) + '</td>'
      + '<td class="txt-dim txt-xs" style="white-space:normal">' + mzNl2br(esc(m.raw_accuracy || '–')) + '</td>'
      + '<td>' + onnxLink + '</td>'
      /* 티어 그룹 — MZ_CHIPS 순서 */
      + chipCells
      /* Performance */
      + '<td class="txt-dim">' + esc(m.fps || '–') + '</td>'
      + '<td class="txt-dim">' + esc(m.fps_per_watt || '–') + '</td>'
      + '</tr>';
  }).join('');

  $('mz-count').textContent = list.length + ' / ' + MZ.models.length + ' models';
}

function mzSearch() {
  var el = $('mz-search');
  MZ.filter.search = el ? el.value : '';
  mzRenderTable();
}

function mzToggleChip(name, chip) {
  // Toggle a single Q-Lite or Q-Pro chip directly from the table DL column
  if (!MZ.cart[name]) {
    var fresh = {};
    for (var i = 0; i < MZ_CHIPS.length; i++) fresh[MZ_CHIPS[i].key] = (MZ_CHIPS[i].key === chip);
    MZ.cart[name] = fresh;
  } else {
    MZ.cart[name][chip] = !MZ.cart[name][chip];
    if (mzCartIsEmpty(MZ.cart[name])) {
      delete MZ.cart[name];
    }
  }
  mzRenderTable();
  mzRenderCart();
}

function mzToggleCart(name) {
  if (MZ.cart[name]) {
    delete MZ.cart[name];
  } else {
    var m = MZ.models.find(function(x) { return x.name === name; });
    if (m) {
      var entry = {};
      for (var i = 0; i < MZ_CHIPS.length; i++) {
        var t = m[MZ_CHIPS[i].key];
        entry[MZ_CHIPS[i].key] = !!(t && t.dxnn_url && !t.exists);
      }
      // 전부 이미 받아둔 상태면 담을 게 없어 보인다 — 받을 수 있는 첫 티어를 켠다.
      if (mzCartIsEmpty(entry)) {
        for (var j = 0; j < MZ_CHIPS.length; j++) {
          var t2 = m[MZ_CHIPS[j].key];
          if (t2 && t2.dxnn_url) { entry[MZ_CHIPS[j].key] = true; break; }
        }
      }
      MZ.cart[name] = entry;
    }
  }
  mzRenderTable();
  mzRenderCart();
}

function mzCartChipToggle(name, chip) {
  if (!MZ.cart[name]) return;
  MZ.cart[name][chip] = !MZ.cart[name][chip];
  if (mzCartIsEmpty(MZ.cart[name])) {
    delete MZ.cart[name];
    mzRenderTable();
  }
  mzRenderCart();
}

function mzCartRemove(name) {
  delete MZ.cart[name];
  mzRenderTable();
  mzRenderCart();
}

function mzCartClear() {
  MZ.cart = {};
  mzRenderTable();
  mzRenderCart();
}

function mzSelectAllVisible() {
  mzFiltered().forEach(function(m) {
    if (!MZ.cart[m.name]) {
      var e = {};
      for (var i = 0; i < MZ_CHIPS.length; i++) {
        var t = m[MZ_CHIPS[i].key];
        e[MZ_CHIPS[i].key] = !!(t && t.dxnn_url);
      }
      MZ.cart[m.name] = e;
    }
  });
  mzRenderTable();
  mzRenderCart();
}

function mzSelectAllNew() {
  mzFiltered().forEach(function(m) {
    var e = {};
    for (var i = 0; i < MZ_CHIPS.length; i++) {
      var t = m[MZ_CHIPS[i].key];
      e[MZ_CHIPS[i].key] = !!(t && t.dxnn_url && !t.exists);
    }
    if (!mzCartIsEmpty(e)) {
      MZ.cart[m.name] = e;
    }
  });
  mzRenderTable();
  mzRenderCart();
}

function mzDeselectAll() {
  var visible = {};
  mzFiltered().forEach(function(m) { visible[m.name] = true; });
  Object.keys(MZ.cart).forEach(function(name) {
    if (visible[name]) delete MZ.cart[name];
  });
  mzRenderTable();
  mzRenderCart();
}

function mzSelectChipAll(chip) {
  // Select only Q-Lite or Q-Pro for all visible models that have it
  mzFiltered().forEach(function(m) {
    var tier = m[chip];
    if (!tier || !tier.dxnn_url) return;
    if (!MZ.cart[m.name]) {
      var e = {};
      for (var i = 0; i < MZ_CHIPS.length; i++) e[MZ_CHIPS[i].key] = (MZ_CHIPS[i].key === chip);
      MZ.cart[m.name] = e;
    } else {
      MZ.cart[m.name][chip] = true;
    }
  });
  mzRenderTable();
  mzRenderCart();
}

function mzToggleCartPanel() {
  MZ.cartOpen = !MZ.cartOpen;
  mzRenderCart();
}

function mzCartFileCount() {
  var count = 0;
  Object.keys(MZ.cart).forEach(function(name) {
    var c = MZ.cart[name];
    for (var i = 0; i < MZ_CHIPS.length; i++) {
      if (c[MZ_CHIPS[i].key]) count += 2;  // dxnn + json
    }
  });
  return count;
}

function mzRenderCart() {
  var cartEl = $('mz-cart');
  if (!cartEl) return;

  var names = Object.keys(MZ.cart);
  var fileCount = mzCartFileCount();

  if (!names.length) {
    /* 튜토리얼이 고정해 둔 시연 카트는 지우지 않는다. 카탈로그가 늦게 도착하면
       이 함수가 다시 돌면서 방금 만든 시연을 display:none 으로 덮었다.
       계약: tests/dx_app/test_modelzoo_cart_demo.py */
    if (cartEl.dataset && cartEl.dataset.dxtPinned === '1') return;
    cartEl.style.display = 'none';
    return;
  }
  cartEl.style.display = '';

  var summaryHtml = '<div class="mz-cart-summary">'
    + '<div class="mz-cart-left">'
    + '<span class="mz-cart-icon">' + DXIcon('download') + '</span> '
    + '<strong>' + names.length + '</strong> ' + T('model(s)')
    + ' · <span class="txt-dim">' + fileCount + ' ' + T('files') + '</span>'
    + '</div>'
    + '<div class="mz-cart-right">'
    + '<button class="btn btn-ghost btn-sm" onclick="mzToggleCartPanel()">' + (MZ.cartOpen ? '' + T('Hide') : '' + T('View Cart')) + '</button>'
    + '<button class="btn btn-ghost btn-sm" onclick="mzCartClear()" title="' + T('Clear Cart') + '">' + DXIcon('trash') + '</button>'
    + '<button class="btn btn-acc btn-sm" onclick="mzStartDownload()" ' + (MZ.downloading ? 'disabled' : '') + '>' + DXIcon('download') + ' ' + T('Download All') + ' (' + fileCount + ')</button>'
    + '</div></div>';

  var detailHtml = '';
  if (MZ.cartOpen) {
    detailHtml = '<div class="mz-cart-detail">';
    names.forEach(function(name) {
      var c = MZ.cart[name];
      var m = MZ.models.find(function(x) { return x.name === name; });
      var task = m ? m.task : '';

      detailHtml += '<div class="mz-cart-item">'
        + '<div class="mz-cart-item-info">'
        + '<span class="mz-cart-item-name">' + DXIcon('models') + ' ' + esc(name) + '</span>'
        + '<span class="badge b-cat">' + esc(task) + '</span>'
        + '</div>'
        + '<div class="mz-cart-item-chips">';

      for (var ci = 0; ci < MZ_CHIPS.length; ci++) {
        var chip = MZ_CHIPS[ci];
        var tier = m && m[chip.key];
        if (!tier || !tier.dxnn_url) continue;
        var cls = c[chip.key] ? 'mz-chip-on' : 'mz-chip-off';
        var label = (tier.exists ? DXIcon('check') + ' ' : '') + chip.label;
        detailHtml += '<button class="mz-chip-toggle ' + cls + '" onclick="mzCartChipToggle(\'' + esc(name) + '\',\'' + chip.key + '\')">' + label + '</button>';
      }

      detailHtml += '</div>'
        + '<button class="mz-cart-remove" onclick="mzCartRemove(\'' + esc(name) + '\')" title="'+T('Remove')+'"></button>'
        + '</div>';
    });
    detailHtml += '</div>';
  }

  cartEl.innerHTML = summaryHtml + detailHtml;
}

async function mzStartDownload() {
  if (MZ.downloading) return;

  var items = [];
  Object.keys(MZ.cart).forEach(function(name) {
    var c = MZ.cart[name];
    var m = MZ.models.find(function(x) { return x.name === name; });
    if (!m) return;

    for (var i = 0; i < MZ_CHIPS.length; i++) {
      var key = MZ_CHIPS[i].key;
      var tier = m[key];
      if (c[key] && tier && tier.dxnn_url) {
        items.push({ name: name, chip: key, dxnn_url: tier.dxnn_url, json_url: tier.json_url || null });
      }
    }
  });

  if (!items.length) {
    toast(T('No files selected for download'), 'err');
    return;
  }

  MZ.downloading = true;
  mzRenderCart();
  mzRenderProgress({ running: true, total: items.length * 2, done: 0, current: T('Starting…'), results: [], finished: false });
  $('mz-progress').style.display = '';

  var r = await postJ('/api/modelzoo/download', { items: items, source: MZ.source });
  if (!r.ok) {
    MZ.downloading = false;
    toast(r.error || T('Download failed'), 'err');
    mzRenderCart();
    return;
  }

  if (MZ.pollTimer) clearInterval(MZ.pollTimer);
  MZ.pollTimer = setInterval(mzPollProgress, 1500);
}

async function mzPollProgress() {
  var r = await api('/api/modelzoo/status');
  mzRenderProgress(r);

  if (r.finished) {
    clearInterval(MZ.pollTimer);
    MZ.pollTimer = null;
    MZ.downloading = false;

    var okCount = (r.results || []).filter(function(x) { return x.status === 'ok'; }).length;
    var errCount = (r.results || []).filter(function(x) { return x.status === 'error'; }).length;

    if (errCount > 0) {
      toast(T('Downloaded') + ' ' + okCount + ', ' + T('errors') + ' ' + errCount, 'err');
    } else {
      toast(T('Download complete —') + ' ' + okCount + ' ' + T('files'), 'ok');
    }

    // Refresh model list (exists flags)
    MZ.models = [];
    await mzLoadModels();
    MZ.cart = {};
    mzRenderTaskChips();
    mzRenderTable();
    mzRenderCart();

    // Refresh main Models page data too
    if (typeof loadModels === 'function') loadModels();
  }
}

async function mzStopDownload() {
  await postJ('/api/modelzoo/stop', {});
  toast(T('Cancelling download…'), 'info');
}

function mzRenderProgress(st) {
  var el = $('mz-progress');
  if (!el) return;
  if (!st || (!st.running && !st.finished)) { el.style.display = 'none'; return; }
  el.style.display = '';

  var pct = st.total > 0 ? Math.round(st.done / st.total * 100) : 0;
  var barW = pct + '%';

  var html = '<div class="mz-prog-header">'
    + '<div class="mz-prog-bar-wrap"><div class="mz-prog-bar" style="width:' + barW + '"></div></div>'
    + '<span class="mz-prog-pct">' + pct + '% (' + st.done + '/' + st.total + ')</span>'
    + (st.running ? '<button class="btn btn-ghost btn-sm" onclick="mzStopDownload()">' + DXIcon('stop') + ' ' + T('Stop') + '</button>' : '')
    + '</div>';

  if (st.current && st.running) {
    html += '<div class="mz-prog-current">' + DXIcon('spinner') + ' ' + esc(st.current) + '</div>';
  }

  if (st.results && st.results.length) {
    html += '<div class="mz-prog-log">';
    st.results.forEach(function(r) {
      var icon = r.status === 'ok' ? DXIcon('check') : r.status === 'cancelled' ? DXIcon('stop') : DXIcon('x');
      var sizeStr = r.size ? mzFmtSize(r.size) : '';
      var detail = r.error ? '<span class="txt-dim"> — ' + esc(r.error) + '</span>' : '';
      html += '<div class="mz-prog-item">' + icon + ' ' + esc(r.file || '') + (r.chip ? ' <span class="badge b-blue">' + r.chip + '</span>' : '') + ' ' + sizeStr + detail + '</div>';
    });
    html += '</div>';
  }

  if (st.finished) {
    html += '<div class="mt8 txt-sm" style="color:var(--status-ok)">' + DXIcon('check')+' '+T('All done!') + '</div>';
  }

  el.innerHTML = html;
}

function mzFmtSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / 1048576).toFixed(1) + ' MB';
}

function mzNl2br(s) {
  // Convert escaped newlines (\n) to <br> for multi-line metric/accuracy display
  return s.replace(/\n/g, '<br>');
}

async function mzRefresh() {
  MZ.models = [];
  await initModelZoo();
  toast(T('ModelZoo refreshed'), 'ok');
}
if (typeof registerLangRefresher === 'function') {
  registerLangRefresher(function refreshModelZooPageLanguage() {
    if (document.querySelector('#page-modelzoo.active') && typeof initModelZoo === 'function') initModelZoo();
  });
}
