'use strict';

function _escHtml(s) {
  var d = document.createElement('div');
  d.textContent = s == null ? '' : String(s);
  return d.innerHTML;
}

function _escAttr(s) {
  return _escHtml(s).replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

var Results = {
  currentHw: null,
  currentRun: null,
  data: null,

  refresh: function() {
    var container = document.getElementById('tab-results');
    if (!container) return;
    container.innerHTML = this._buildShellHTML(
      '<div class="loading">' + _t('Loading...') + '</div>',
      '<div class="empty-state small"><p>' + _t('Select Hardware') + '</p></div>',
      '<div class="empty-state"><p>' + _t('Select Hardware') + ' / ' + _t('Select Run') + '</p></div>'
    );
    var self = this;
    fetch('/api/results')
      .then(function(r) { return r.json(); })
      .then(function(data) {
        self.data = data;
        self.renderHwList(container);
      })
      .catch(function(err) {
        container.innerHTML = self._buildShellHTML(
          '<div class="empty-state small"><p>' + _t('No data available') + '</p></div>',
          '<div class="empty-state small"><p>' + _t('Select Hardware') + '</p></div>',
          '<p class="error">' + _escHtml(err.message) + '</p>'
        );
      });
  },

  _buildShellHTML: function(hwCardContent, hwDetailContent, runDetailContent) {
    return '<div class="results-panel results-workspace">' +
      '<aside class="results-rail" id="resultsHwRail">' +
        '<section class="results-rail-section">' +
          '<h2 data-i18n="Select Hardware">' + _t('Select Hardware') + '</h2>' +
          '<div id="hwCardGrid" class="hw-card-grid">' + hwCardContent + '</div>' +
        '</section>' +
        '<section class="results-rail-section" id="hwDetail">' + hwDetailContent + '</section>' +
      '</aside>' +
      '<section class="results-detail" id="runDetail">' + runDetailContent + '</section>' +
    '</div>';
  },

  renderHwList: function(container) {
    if (!this.data || this.data.length === 0) {
      container.innerHTML = this._buildShellHTML(
        '<div class="empty-state small"><p>' + _t('No data available') + '</p></div>',
        '<div class="empty-state small"><p>' + _t('Select Hardware') + '</p></div>',
        '<div class="empty-state"><p>' + _t('No data available') + '</p></div>'
      );
      return;
    }
    var cardsHtml = '';
    this.data.forEach(function(hw) {
      cardsHtml += '<div class="hw-card" role="button" tabindex="0" data-hw-id="' + _escAttr(hw.hw_id) + '">' +
      '<div class="hw-card-icon">🖥️</div>' +
      '<div class="hw-card-name">' + _escHtml(hw.hw_id) + '</div>' +
      '<div class="hw-card-runs">' + (hw.runs || []).length + ' runs</div>' +
      '</div>';
    });
    container.innerHTML = this._buildShellHTML(
      cardsHtml,
      '<div class="empty-state small"><p>' + _t('Select Hardware') + '</p></div>',
      '<div class="empty-state"><p>' + _t('Select Hardware') + ' / ' + _t('Select Run') + '</p></div>'
    );
    container.querySelectorAll('.hw-card[data-hw-id]').forEach(function(card) {
      var select = function() { Results.selectHw(card.dataset.hwId); };
      card.addEventListener('click', select);
      card.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); select(); }
      });
    });
  },

  selectHw: function(hwId) {
    this.currentHw = hwId;
    var hw = this.data.find(function(h) { return h.hw_id === hwId; });
    if (!hw) return;
    var detailEl = document.getElementById('hwDetail');
    if (!detailEl) return;
    document.querySelectorAll('.hw-card[data-hw-id]').forEach(function(card) {
      card.classList.toggle('active', card.dataset.hwId === hwId);
    });
    var html = '<h3>' + _escHtml(hwId) + ' — ' + _t('Select Run') + '</h3><div class="run-list">';
    hw.runs.forEach(function(run) {
      html += '<div class="run-item" role="button" tabindex="0" data-hw-id="' + _escAttr(hwId) + '" data-run-id="' + _escAttr(run.run_id) + '">' +
        '<span class="run-id">' + _escHtml(run.run_id) + '</span>' +
        (run.has_report ? '<span class="badge badge-ok">📋</span>' : '') +
      '</div>';
    });
    html += '</div>';
    detailEl.innerHTML = html;
    detailEl.querySelectorAll('.run-item[data-run-id]').forEach(function(item) {
      var select = function() { Results.selectRun(item.dataset.hwId, item.dataset.runId); };
      item.addEventListener('click', select);
      item.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); select(); }
      });
    });
    var runDetailEl = document.getElementById('runDetail');
    if (runDetailEl) {
      runDetailEl.innerHTML = '<div class="empty-state"><p>' + _t('Select Run') + '</p></div>';
    }
  },

  selectRun: function(hwId, runId) {
    this.currentRun = runId;
    var runDetailEl = document.getElementById('runDetail');
    if (!runDetailEl) return;
    runDetailEl.innerHTML = '<div class="loading">' + _t('Loading...') + '</div>';

    var self = this;
    var hwSegment = encodeURIComponent(hwId);
    var runSegment = encodeURIComponent(runId);
    Promise.all([
      fetch('/api/results/' + hwSegment + '/' + runSegment).then(function(r) { return r.json(); }),
      fetch('/api/results/' + hwSegment + '/' + runSegment + '/report').then(function(r) { return r.json(); }).catch(function() { return null; }),
    ]).then(function(results) {
      var detail = results[0];
      var report = results[1];
      self.renderRunDetail(runDetailEl, detail, report);
    }).catch(function(err) {
      runDetailEl.innerHTML = '<p class="error">' + _escHtml(err.message) + '</p>';
    });
  },

  renderRunDetail: function(container, detail, report) {
    var html = '<div class="run-detail">';

    if (report && report.markdown) {
      html += '<section class="result-section result-section--report" data-help-id="bench-result-report"><h2>' + _t('View Report') + '</h2>';
      html += '<div class="report-content">';
      if (typeof marked !== 'undefined' && marked.parse) {
        html += marked.parse(report.markdown);
      } else {
        html += '<pre>' + _escHtml(report.markdown) + '</pre>';
      }
      html += '</div></section>';
    }

    html += '<section class="result-section result-section--raw" data-help-id="bench-result-raw"><h2>' + _t('Raw Data') + '</h2>';
    var sections = ['environment', 'model_results', 'pipeline_results', 'multi_stream_results'];
    sections.forEach(function(section) {
      var data = detail[section];
      if (!data) return;
      html += '<details class="result-section"><summary>' + section.replace(/_/g, ' ') + '</summary>';
      html += '<pre class="json-view">' + _escHtml(JSON.stringify(data, null, 2)) + '</pre>';
      html += '</details>';
    });
    html += '</section>';

    html += '</div>';
    container.innerHTML = html;
  },
};
if (typeof registerBenchmarkLangRefresher === 'function') {
  registerBenchmarkLangRefresher(function() {
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
    if (typeof Dashboard !== 'undefined' && typeof Dashboard.refreshAllCharts === 'function') Dashboard.refreshAllCharts();
  });
}
