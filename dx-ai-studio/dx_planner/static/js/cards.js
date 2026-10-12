/**
 * CardRenderer — renders the Step 2 recommendation cards.
 * Draws a mini gauge on each card with GaugeChart.draw().
 */
const CardRenderer = {
  _detailCb: null,

  onDetailClick(cb) { this._detailCb = cb; },
  onCompareChange() {},

  render(results, inputs) {
    const container = document.getElementById('recommend-cards');
    if (!container) return;
    container.innerHTML = '';

    // 60fps banner
    const banner = document.getElementById('fps-banner');
    if (banner) {
      banner.style.display = inputs.targetFps >= 60 ? '' : 'none';
    }

    if (results.length === 0) {
      container.innerHTML = this._emptyState();
      this._applyLang();
      return;
    }

    results.forEach((r, i) => {
      container.appendChild(this._buildCard(r, i, inputs));
    });

    // Gauge rendering (after charts.js loads)
    if (typeof GaugeChart !== 'undefined') {
      results.forEach((r, i) => {
        const cv = container.querySelectorAll('.gauge-canvas')[i];
        if (cv) GaugeChart.draw(cv, r.maxChannels, inputs.cameras, r.boundaryFlag);
      });
    }
    this._applyLang();
  },

  _confidenceBadge(flag) {
    const labels = {
      measured: '<span data-i18n="Measured">Measured</span>',
      estimated: '<span data-i18n="Estimated">Estimated</span>',
      '+': '<span data-i18n="Estimated+">Estimated+</span>',
    };
    const key = labels[flag] ? flag : 'measured';
    return '<span class="badge badge-confidence" data-confidence="' + key + '">' + labels[key] + '</span>';
  },

  // The rank is a numbered disc — only first place is gold (medal emoji render differently on each OS).
  _rankBadge(i) {
    return '<span class="rank-disc' + (i === 0 ? ' rank-disc--top' : '') + '">' + (i + 1) + '</span>';
  },

  _ico(name) {
    return (typeof window.DXIcon === 'function') ? window.DXIcon(name) : '';
  },

  _buildCard(r, idx, inputs) {
    const pid = r.platform.id;
    const meets = r.meetsRequirement;
    const confidenceBadge = this._confidenceBadge(r.boundaryFlag);

    const card = document.createElement('div');
    card.className = 'rec-card ' + (meets ? 'card-meets' : 'card-insufficient') +
      (idx === 0 ? ' rec-card--featured' : '');
    card.dataset.platformId = pid;
    card.dataset.index = idx;
    card.tabIndex = 0;
    card.setAttribute('role', 'button');
    card.setAttribute('aria-label', r.platform.npu.model + ' + ' + r.platform.host.name);

    const chVal = this._formatChannels(r.maxChannels, r.boundaryFlag);
    const benchmarkMeta = this._benchmarkMeta(pid);
    const meetsLabel = r.status === 'meets-estimated'
      ? '<span data-i18n="Meets (estimate)">Meets (estimate)</span>'
      : '<span data-i18n="Meets">Meets</span>';
    const statusBadge = meets
      ? '<span class="badge badge-meets">' + this._ico('check') + ' ' + meetsLabel + '</span>'
      : '<span class="badge badge-insufficient">' + this._ico('alert') + ' <span data-i18n="Insufficient">Insufficient</span></span>';
    const featuredBadge = idx === 0
      ? '<span class="badge badge-featured" data-i18n="Top pick">Top pick</span>'
      : '';


    const topoLine = typeof RecommendEngine !== 'undefined'
      ? RecommendEngine._topologyLabel(r.platform)
      : '';

    card.innerHTML =
      '<div class="card-rank">' + this._rankBadge(idx) + '</div>' +
      '<div class="card-header">' +
        '<h3>' + r.platform.npu.model + ' + ' + r.platform.host.name + '</h3>' +
        (topoLine ? '<p class="card-topology txt-dim txt-sm">' + this._escHtml(topoLine) + '</p>' : '') +
        '<div class="card-badges">' + featuredBadge + confidenceBadge + statusBadge + '</div>' +
      '</div>' +
      '<div class="card-metrics">' +
        this._metric(String(Math.round(r.pipelineFps || 0)), 'FPS') +
        this._metric(chVal,
          '<span data-i18n="Ch">Ch</span>') +
        this._metric(r.platform.npu.tdp_w + 'W', 'TDP') +
      '</div>' +
      '<p class="card-why txt-sm txt-dim">' + this._whyHtml(r) + '</p>' +
      benchmarkMeta +
      '<div class="card-gauge"><canvas class="gauge-canvas" width="60" height="60"></canvas></div>' +
      '<div class="card-actions">' +
        '<button class="btn-detail" data-platform-id="' + pid + '">' +
          '<span data-i18n="Details">Details</span>' +
        '</button>' +
      '</div>';

    // Events
    card.querySelector('.card-why')._result = r;
    card.querySelector('.btn-detail').addEventListener('click', () => {
      if (this._detailCb) this._detailCb(pid);
    });

    card.addEventListener('click', (event) => {
      if (event.target.closest('button')) return;
      if (this._detailCb) this._detailCb(pid);
    });

    card.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        if (this._detailCb) this._detailCb(pid);
      }
    });

    // "+" = the estimate stopped at twice the highest tested stream count
    if (r.boundaryFlag === '+') {
      const chMetric = card.querySelectorAll('.metric')[1];
      if (chMetric) chMetric.title = this._t('At least this many — estimates stop at twice the tested stream count');
    }

    return card;
  },

  _t(key) {
    return typeof T === 'function' ? T(key) : key;
  },

  _fill(key, vals) {
    return Object.keys(vals).reduce((out, k) => out.split('{' + k + '}').join(vals[k]), this._t(key));
  },

  /** One line saying why this channel count — the measured point, or the division the estimate comes from. */
  _whyHtml(r) {
    const w = r.why || { kind: 'none' };
    const fps = v => this._formatNumber(v, 1);
    // The quotient is cut, not rounded: 8.95 shown as "9" next to "8 ch" would contradict the floor.
    const quotient = v => this._formatNumber(Math.floor(v * 10) / 10, 1);
    let line;
    if (w.kind === 'measured') {
      line = this._fill('{n} ch held {fps} FPS each ≥ {target} FPS target (measured)',
        { n: w.n, fps: fps(w.atFps), target: w.target });
      if (w.nextN != null) line += ' · ' + this._fill('{n} ch dropped to {fps} FPS', { n: w.nextN, fps: fps(w.nextFps) });
    } else if (w.kind === 'estimated' && w.n > 0) {
      const vals = { total: fps(w.tSat), target: w.target, raw: quotient(w.raw), n: w.n, max: w.maxTested };
      line = w.capped
        ? this._fill('{total} FPS ÷ {target} FPS = {raw} → {n} ch+ (estimates stop at 2 × {max} tested ch)', vals)
        : this._fill('{total} FPS ÷ {target} FPS = {raw} → {n} ch (estimated from the measured total; tested up to {max} ch)', vals);
    } else if (w.kind === 'estimated') {
      line = this._fill('Not even one stream: {total} FPS ÷ {target} FPS = {raw} → 0 ch',
        { total: fps(w.tSat), target: w.target, raw: quotient(w.raw) });
    } else {
      line = this._t('No multi-stream measurement');
    }
    const notes = [];
    if (r.throttled) notes.push(this._t('NPU throttled while measured'));
    const load = Number.isFinite(r.npuPct) ? ' · ' + this._fill('NPU {pct}%', { pct: Math.round(r.npuPct) }) : '';
    if (r.bottleneck === 'npu') notes.push(this._t('Limit: NPU') + load);
    else if (r.bottleneck === 'host') notes.push(this._t('Limit: host (CPU / decode)') + load);
    if (r.meetsLatency === null) notes.push(this._t('Latency not measured'));
    return this._escHtml(line) + notes.map(n => '<span class="card-why-note">' + this._escHtml(n) + '</span>').join('');
  },

  _formatChannels(val, flag) {
    if (flag === '+') return val + '+';
    return String(val);
  },

  _formatNumber(value, digits) {
    return Number(value).toFixed(digits).replace(/\.0+$/, '').replace(/(\.\d*?)0+$/, '$1');
  },

  _escHtml(text) {
    return String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  },

  _benchmarkMeta(pid) {
    const generated = typeof DataLoader !== 'undefined' ? DataLoader.getGeneratedAt() : null;
    const benchmarkDate = typeof DataLoader !== 'undefined' ? DataLoader.getBenchmarkDate(pid) : null;
    const stale = typeof DataLoader !== 'undefined' ? DataLoader.isBenchmarkStale(pid) : false;
    const generatedText = generated ? generated.slice(0, 10) : 'N/A';
    const benchmarkText = benchmarkDate || 'N/A';
    const staleBadge = stale
      ? '<span class="badge badge-stale" data-i18n="Benchmark stale">Benchmark stale</span>'
      : '';
    return '<div class="card-release-meta">' +
      '<span data-i18n="Generated">Generated</span>: ' + generatedText +
      ' · <span data-i18n="Benchmark">Benchmark</span>: ' + benchmarkText +
      staleBadge +
    '</div>';
  },

  _emptyState() {
    return '<div class="empty-state planner-empty-recommendations">' +
      '<strong data-i18n="No matching recommendations">No matching recommendations</strong>' +
      '<p data-i18n="Try relaxing FPS, channel, or model-size requirements.">Try relaxing FPS, channel, or model-size requirements.</p>' +
    '</div>';
  },

  _metric(value, label) {
    return '<div class="metric">' +
      '<span class="metric-value">' + value + '</span>' +
      '<span class="metric-label">' + label + '</span>' +
    '</div>';
  },

  _applyLang() {
    if (typeof DXI18n !== 'undefined' && typeof DXI18n.applyLang === 'function') {
      DXI18n.applyLang();
    }
  },
};
if (typeof registerPlannerLangRefresher === 'function') {
  registerPlannerLangRefresher(function() {
    document.querySelectorAll('.card-why').forEach(el => {
      if (el._result) el.innerHTML = CardRenderer._whyHtml(el._result);
    });
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
  });
}
