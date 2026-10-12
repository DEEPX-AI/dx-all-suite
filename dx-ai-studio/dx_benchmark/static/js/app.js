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
    // Tabs are drawn by shared/shell.py and identified by data-page.
    document.querySelectorAll('.dx-tab').forEach(function(btn) {
      btn.addEventListener('click', function() {
        self.switchTab(btn.dataset.page);
      });
    });
    if (window.DXTabs) DXTabs.init({ row: '.dx-shell-tabs' });
  },

  // The header page name reuses the active tab label (one translation path). Tab labels are only
  // translated once a language is applied, so this re-syncs on every language change.
  syncPageTitle: function() {
    var label = document.querySelector('.dx-tab[data-page="' + (this.currentTab || 'dashboard') + '"] span');
    var slot = document.getElementById('dxShellPage');
    if (label && slot) slot.textContent = label.textContent.trim();
  },

  switchTab: function(tabId) {
    this.currentTab = tabId;
    // The active tab is marked with aria-current; dx-shell.css styles it from that.
    document.querySelectorAll('.dx-tab').forEach(function(b) {
      if (b.dataset.page === tabId) b.setAttribute('aria-current', 'page');
      else b.removeAttribute('aria-current');
    });
    document.querySelectorAll('.main-tab-content').forEach(function(c) {
      c.classList.toggle('active', c.id === 'tab-' + tabId);
    });
    this.syncPageTitle();
    // If the active tab was in the overflow menu, bring it back into the row.
    if (window.DXTabs) DXTabs.reflowAll();
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
    BenchApp.syncPageTitle();
  }
  window.addEventListener('dx-lang-applied', function () { BenchApp.syncPageTitle(); });
  if (typeof DXI18n !== 'undefined') {
    DXI18n.onLangChange(refreshBenchmarkModuleLanguage);
  }
});
