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
    // 통합 shell(Option A): 탭은 shared/shell.py 가 그리고 data-page 로 식별한다.
    document.querySelectorAll('.dx-tab').forEach(function(btn) {
      btn.addEventListener('click', function() {
        self.switchTab(btn.dataset.page);
      });
    });
    if (window.DXTabs) DXTabs.init({ row: '.dx-shell-tabs' });
  },

  // 헤더 페이지명은 활성 탭 라벨을 그대로 쓴다 (번역 경로를 하나로 유지). 탭 라벨은 언어가 적용된 뒤에야
  // 번역되므로, 언어 적용 때마다 다시 맞춘다 — 예전에는 탭을 누르기 전까지 "Dashboard" 영어였다.
  syncPageTitle: function() {
    var label = document.querySelector('.dx-tab[data-page="' + (this.currentTab || 'dashboard') + '"] span');
    var slot = document.getElementById('dxShellPage');
    if (label && slot) slot.textContent = label.textContent.trim();
  },

  switchTab: function(tabId) {
    this.currentTab = tabId;
    // 활성 표시는 aria-current — dx-shell.css 가 그걸로 스타일을 건다.
    document.querySelectorAll('.dx-tab').forEach(function(b) {
      if (b.dataset.page === tabId) b.setAttribute('aria-current', 'page');
      else b.removeAttribute('aria-current');
    });
    document.querySelectorAll('.main-tab-content').forEach(function(c) {
      c.classList.toggle('active', c.id === 'tab-' + tabId);
    });
    this.syncPageTitle();
    // 활성 탭이 오버플로 메뉴에 있었다면 행으로 되돌린다.
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
