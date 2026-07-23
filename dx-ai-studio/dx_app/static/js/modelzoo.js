// Browse DEEPX ModelZoo, add to cart, download Q-Lite / Q-Pro models

const MZ = {
  models: [],
  cart: {},           // { "AlexNet-1": { qlite: true, qpro: false } }
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
    html += '<button class="chip' + active + '" onclick="mzFilterTask(\'' + esc(t) + '\')">' + esc(t) + ' <span class="txt-dim">' + tasks[t] + '</span></button>';
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
    tb.innerHTML = '<tr><td colspan="22" style="text-align:center;padding:30px;color:var(--text-4)">' + T('No models found') + '</td></tr>';
    $('mz-count').textContent = '0 / ' + MZ.models.length;
    return;
  }

  tb.innerHTML = list.map(function(m) {
    var cart = MZ.cart[m.name];
    var qlInCart = cart && cart.qlite;
    var qpInCart = cart && cart.qpro;

    var hasQL = m.qlite && m.qlite.dxnn_url;
    var qlExists = hasQL && m.qlite.exists;

    var hasQP = m.qpro && m.qpro.dxnn_url;
    var qpExists = hasQP && m.qpro.exists;

    var qlAcc = hasQL ? mzNl2br(esc(m.qlite.accuracy || '–')) : '–';
    var qlDxnn = hasQL ? '<a href="' + esc(m.qlite.dxnn_url) + '" target="_blank" class="txt-link txt-xs">📦 dxnn</a>' : '–';
    var qlJson = (hasQL && m.qlite.json_url) ? '<a href="' + esc(m.qlite.json_url) + '" target="_blank" class="txt-link txt-xs">📄 json</a>' : '–';
    var qlDL = '';
    if (hasQL) {
      if (qlExists && !qlInCart) {
        qlDL = '<span class="badge b-ok txt-xs" title="'+T('Downloaded')+'">✅</span>';
      } else {
        qlDL = '<label class="mz-chk-wrap" title="'+T('Add Q-Lite to cart')+'"><input type="checkbox" onchange="mzToggleChip(\'' + esc(m.name) + '\',\'qlite\')"' + (qlInCart ? ' checked' : '') + '><span class="mz-chk mz-chk-ql"></span></label>';
      }
    } else {
      qlDL = '–';
    }

    var qpAcc = hasQP ? mzNl2br(esc(m.qpro.accuracy || '–')) : '–';
    var qpDxnn = hasQP ? '<a href="' + esc(m.qpro.dxnn_url) + '" target="_blank" class="txt-link txt-xs">📦 dxnn</a>' : '–';
    var qpJson = (hasQP && m.qpro.json_url) ? '<a href="' + esc(m.qpro.json_url) + '" target="_blank" class="txt-link txt-xs">📄 json</a>' : '–';
    var qpDL = '';
    if (hasQP) {
      if (qpExists && !qpInCart) {
        qpDL = '<span class="badge b-ok txt-xs" title="'+T('Downloaded')+'">✅</span>';
      } else {
        qpDL = '<label class="mz-chk-wrap" title="'+T('Add Q-Pro to cart')+'"><input type="checkbox" onchange="mzToggleChip(\'' + esc(m.name) + '\',\'qpro\')"' + (qpInCart ? ' checked' : '') + '><span class="mz-chk mz-chk-qp"></span></label>';
      }
    } else {
      qpDL = '–';
    }

    var onnxLink = m.onnx_url ? '<a href="' + esc(m.onnx_url) + '" target="_blank" class="txt-link txt-xs">📦 onnx</a>' : '–';

    var rowCls = (qlInCart || qpInCart) ? 'mz-row-selected' : '';

    return '<tr class="' + rowCls + '">'
      + '<td><label class="mz-chk-wrap"><input type="checkbox" onchange="mzToggleCart(\'' + esc(m.name) + '\')"' + (cart ? ' checked' : '') + '><span class="mz-chk"></span></label></td>'
      + '<td><span class="badge b-cat">' + esc(m.task) + '</span></td>'
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
      /* Q-Lite group */
      + '<td class="mz-col-ql txt-xs" style="white-space:normal">' + qlAcc + '</td>'
      + '<td class="mz-col-ql">' + qlDxnn + '</td>'
      + '<td class="mz-col-ql">' + qlJson + '</td>'
      + '<td class="mz-col-ql">' + qlDL + '</td>'
      /* Q-Pro group */
      + '<td class="mz-col-qp txt-xs" style="white-space:normal">' + qpAcc + '</td>'
      + '<td class="mz-col-qp">' + qpDxnn + '</td>'
      + '<td class="mz-col-qp">' + qpJson + '</td>'
      + '<td class="mz-col-qp">' + qpDL + '</td>'
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
    MZ.cart[name] = { qlite: chip === 'qlite', qpro: chip === 'qpro' };
  } else {
    MZ.cart[name][chip] = !MZ.cart[name][chip];
    // Remove from cart if nothing selected
    if (!MZ.cart[name].qlite && !MZ.cart[name].qpro) {
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
      MZ.cart[name] = {
        qlite: !!(m.qlite && m.qlite.dxnn_url && !m.qlite.exists),
        qpro: !!(m.qpro && m.qpro.dxnn_url && !m.qpro.exists),
      };
      // If both are false (both downloaded), default enable qlite
      if (!MZ.cart[name].qlite && !MZ.cart[name].qpro) {
        if (m.qlite && m.qlite.dxnn_url) MZ.cart[name].qlite = true;
        else if (m.qpro && m.qpro.dxnn_url) MZ.cart[name].qpro = true;
      }
    }
  }
  mzRenderTable();
  mzRenderCart();
}

function mzCartChipToggle(name, chip) {
  if (!MZ.cart[name]) return;
  MZ.cart[name][chip] = !MZ.cart[name][chip];
  // Remove from cart if nothing selected
  if (!MZ.cart[name].qlite && !MZ.cart[name].qpro) {
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
      MZ.cart[m.name] = {
        qlite: !!(m.qlite && m.qlite.dxnn_url),
        qpro: !!(m.qpro && m.qpro.dxnn_url),
      };
    }
  });
  mzRenderTable();
  mzRenderCart();
}

function mzSelectAllNew() {
  mzFiltered().forEach(function(m) {
    var ql = !!(m.qlite && m.qlite.dxnn_url && !m.qlite.exists);
    var qp = !!(m.qpro && m.qpro.dxnn_url && !m.qpro.exists);
    if (ql || qp) {
      MZ.cart[m.name] = { qlite: ql, qpro: qp };
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
    var has = chip === 'qlite'
      ? (m.qlite && m.qlite.dxnn_url)
      : (m.qpro && m.qpro.dxnn_url);
    if (!has) return;
    if (!MZ.cart[m.name]) {
      MZ.cart[m.name] = { qlite: chip === 'qlite', qpro: chip === 'qpro' };
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
    if (c.qlite) count += 2;  // dxnn + json
    if (c.qpro) count += 2;
  });
  return count;
}

function mzRenderCart() {
  var cartEl = $('mz-cart');
  if (!cartEl) return;

  var names = Object.keys(MZ.cart);
  var fileCount = mzCartFileCount();

  if (!names.length) {
    cartEl.style.display = 'none';
    return;
  }
  cartEl.style.display = '';

  var summaryHtml = '<div class="mz-cart-summary">'
    + '<div class="mz-cart-left">'
    + '<span class="mz-cart-icon">🛒</span> '
    + '<strong>' + names.length + '</strong> ' + T('model(s)')
    + ' · <span class="txt-dim">' + fileCount + ' ' + T('files') + '</span>'
    + '</div>'
    + '<div class="mz-cart-right">'
    + '<button class="btn btn-ghost btn-sm" onclick="mzToggleCartPanel()">' + (MZ.cartOpen ? '▼ ' + T('Hide') : '▲ ' + T('View Cart')) + '</button>'
    + '<button class="btn btn-ghost btn-sm" onclick="mzCartClear()" title="' + T('Clear Cart') + '">🗑️</button>'
    + '<button class="btn btn-acc btn-sm" onclick="mzStartDownload()" ' + (MZ.downloading ? 'disabled' : '') + '>📥 ' + T('Download All') + ' (' + fileCount + ')</button>'
    + '</div></div>';

  var detailHtml = '';
  if (MZ.cartOpen) {
    detailHtml = '<div class="mz-cart-detail">';
    names.forEach(function(name) {
      var c = MZ.cart[name];
      var m = MZ.models.find(function(x) { return x.name === name; });
      var task = m ? m.task : '';
      var hasQL = m && m.qlite && m.qlite.dxnn_url;
      var hasQP = m && m.qpro && m.qpro.dxnn_url;

      detailHtml += '<div class="mz-cart-item">'
        + '<div class="mz-cart-item-info">'
        + '<span class="mz-cart-item-name">📦 ' + esc(name) + '</span>'
        + '<span class="badge b-cat">' + esc(task) + '</span>'
        + '</div>'
        + '<div class="mz-cart-item-chips">';

      if (hasQL) {
        var qlCls = c.qlite ? 'mz-chip-on' : 'mz-chip-off';
        var qlLabel = m.qlite.exists ? '✅ Q-Lite' : 'Q-Lite';
        detailHtml += '<button class="mz-chip-toggle ' + qlCls + '" onclick="mzCartChipToggle(\'' + esc(name) + '\',\'qlite\')">' + qlLabel + '</button>';
      }
      if (hasQP) {
        var qpCls = c.qpro ? 'mz-chip-on' : 'mz-chip-off';
        var qpLabel = m.qpro.exists ? '✅ Q-Pro' : 'Q-Pro';
        detailHtml += '<button class="mz-chip-toggle ' + qpCls + '" onclick="mzCartChipToggle(\'' + esc(name) + '\',\'qpro\')">' + qpLabel + '</button>';
      }

      detailHtml += '</div>'
        + '<button class="mz-cart-remove" onclick="mzCartRemove(\'' + esc(name) + '\')" title="'+T('Remove')+'">✕</button>'
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

    if (c.qlite && m.qlite && m.qlite.dxnn_url) {
      items.push({ name: name, chip: 'qlite', dxnn_url: m.qlite.dxnn_url, json_url: m.qlite.json_url || null });
    }
    if (c.qpro && m.qpro && m.qpro.dxnn_url) {
      items.push({ name: name, chip: 'qpro', dxnn_url: m.qpro.dxnn_url, json_url: m.qpro.json_url || null });
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
      toast('⚠️ ' + T('Downloaded') + ' ' + okCount + ', ' + T('errors') + ' ' + errCount, 'err');
    } else {
      toast('✅ ' + T('Download complete —') + ' ' + okCount + ' ' + T('files'), 'ok');
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
    + (st.running ? '<button class="btn btn-ghost btn-sm" onclick="mzStopDownload()">⏹ ' + T('Stop') + '</button>' : '')
    + '</div>';

  if (st.current && st.running) {
    html += '<div class="mz-prog-current">⏳ ' + esc(st.current) + '</div>';
  }

  if (st.results && st.results.length) {
    html += '<div class="mz-prog-log">';
    st.results.forEach(function(r) {
      var icon = r.status === 'ok' ? '✅' : r.status === 'cancelled' ? '⏹' : '❌';
      var sizeStr = r.size ? mzFmtSize(r.size) : '';
      var detail = r.error ? '<span class="txt-dim"> — ' + esc(r.error) + '</span>' : '';
      html += '<div class="mz-prog-item">' + icon + ' ' + esc(r.file || '') + (r.chip ? ' <span class="badge b-blue">' + r.chip + '</span>' : '') + ' ' + sizeStr + detail + '</div>';
    });
    html += '</div>';
  }

  if (st.finished) {
    html += '<div class="mt8 txt-sm" style="color:var(--success)">' + T('✅ All done!') + '</div>';
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
