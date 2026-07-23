'use strict';

var BenchApp = {
  currentTab: 'dashboard',
  dataset: null,

  init: function() {
    this.initTabs();
    this.loadDataset();
    Settings.init();
    var egBtn = document.getElementById('edgeguideBtn');
    if (egBtn) egBtn.addEventListener('click', function() { Dashboard.openEdgeGuide(); });
  },

  initTabs: function() {
    var self = this;
    document.querySelectorAll('.main-tab').forEach(function(btn) {
      btn.addEventListener('click', function() {
        self.switchTab(btn.dataset.tab);
      });
    });
  },

  switchTab: function(tabId) {
    this.currentTab = tabId;
    document.querySelectorAll('.main-tab').forEach(function(b) {
      b.classList.toggle('active', b.dataset.tab === tabId);
    });
    document.querySelectorAll('.main-tab-content').forEach(function(c) {
      c.classList.toggle('active', c.id === 'tab-' + tabId);
    });
    if (tabId === 'dashboard' && this.dataset) {
      Dashboard.refresh();
    }
    if (tabId === 'results') {
      Results.refresh();
    }
  },

  loadDataset: function() {
    var self = this;
    fetch('/api/dataset')
      .then(function(r) { return r.json(); })
      .then(function(data) {
        self.dataset = data;
        Dashboard.init(data);
      })
      .catch(function(err) {
        console.warn('Dataset load failed:', err);
        var el = document.getElementById('tab-dashboard');
        if (el) el.innerHTML = '<div class="empty-state"><p>' + _t('No data available') + '</p></div>';
      });
  },
};

document.addEventListener('DOMContentLoaded', function() {
  BenchApp.init();
  window.__benchmarkLangRefreshers = window.__benchmarkLangRefreshers || [];
  window.registerBenchmarkLangRefresher = function (fn) {
    if (typeof fn === 'function') window.__benchmarkLangRefreshers.push(fn);
  };
  function refreshBenchmarkModuleLanguage() {
    if (typeof Settings !== 'undefined' && typeof Settings.init === 'function') Settings.init();
    if (BenchApp.dataset && typeof Dashboard !== 'undefined' && typeof Dashboard.refreshAllCharts === 'function') {
      Dashboard.refreshAllCharts();
    }
    window.__benchmarkLangRefreshers.forEach(function (fn) {
      try { fn(); } catch (e) { console.error('[benchmark-lang-refresh]', e); }
    });
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
  }
  if (typeof DXI18n !== 'undefined') {
    DXI18n.onLangChange(refreshBenchmarkModuleLanguage);
  }
});
