'use strict';

var Settings = {
  init: function() {
    var container = document.getElementById('tab-settings');
    if (!container) return;
    container.innerHTML = this._buildHTML();
    this.load();
  },

  _buildHTML: function() {
    return '<div class="settings-panel">' +
      '<h2 data-i18n="Settings">' + _t('Settings') + '</h2>' +
      '<div class="settings-group">' +
        '<h3 data-i18n="Path Settings">' + _t('Path Settings') + '</h3>' +
        '<p class="settings-notice">' +
          _t('Paths are configured at deployment and cannot be changed at runtime.') +
        '</p>' +
        '<div class="setting-row">' +
          '<label data-i18n="Model Directory">' + _t('Model Directory') + '</label>' +
          '<input type="text" id="settModelDir" readonly class="setting-input">' +
        '</div>' +
        '<div class="setting-row">' +
          '<label data-i18n="Video Directory">' + _t('Video Directory') + '</label>' +
          '<input type="text" id="settVideoDir" readonly class="setting-input">' +
        '</div>' +
        '<div class="setting-row">' +
          '<label data-i18n="Results Directory">' + _t('Results Directory') + '</label>' +
          '<input type="text" id="settResultsDir" readonly class="setting-input">' +
        '</div>' +
      '</div>' +
      '<div class="settings-group">' +
        '<h3 data-i18n="Thermal Settings">' + _t('Thermal Settings') + '</h3>' +
        '<p class="settings-notice">' +
          _t('Thermal and benchmark parameters are deployment-fixed. Adjust via configuration files before starting the server.') +
        '</p>' +
        '<div class="setting-row">' +
          '<label>Cooldown Threshold (°C)</label>' +
          '<input type="number" id="settCooldownTemp" value="55" readonly class="setting-input">' +
        '</div>' +
        '<div class="setting-row">' +
          '<label>Wait Interval (s)</label>' +
          '<input type="number" id="settWaitInterval" value="10" readonly class="setting-input">' +
        '</div>' +
      '</div>' +
      '<div class="settings-group">' +
        '<h3 data-i18n="Benchmark Parameters">' + _t('Benchmark Parameters') + '</h3>' +
        '<div class="setting-row">' +
          '<label data-i18n="Iterations">' + _t('Iterations') + '</label>' +
          '<input type="number" id="settIterations" value="100" readonly class="setting-input">' +
        '</div>' +
        '<div class="setting-row">' +
          '<label data-i18n="Warmup Runs">' + _t('Warmup Runs') + '</label>' +
          '<input type="number" id="settWarmup" value="10" readonly class="setting-input">' +
        '</div>' +
        '<div class="setting-row">' +
          '<label data-i18n="FPS Threshold">' + _t('FPS Threshold') + '</label>' +
          '<input type="number" id="settFpsThreshold" value="0" step="0.1" readonly class="setting-input">' +
        '</div>' +
      '</div>' +
    '</div>';
  },

  load: function() {
    fetch('/api/config')
      .then(function(r) { return r.json(); })
      .then(function(data) {
        if (data.model_dir) document.getElementById('settModelDir').value = data.model_dir;
        if (data.video_dir) document.getElementById('settVideoDir').value = data.video_dir;
        if (data.results_dir) document.getElementById('settResultsDir').value = data.results_dir;
        if (data.cooldown_temp != null) document.getElementById('settCooldownTemp').value = data.cooldown_temp;
        if (data.wait_interval != null) document.getElementById('settWaitInterval').value = data.wait_interval;
        if (data.iterations != null) document.getElementById('settIterations').value = data.iterations;
        if (data.warmup != null) document.getElementById('settWarmup').value = data.warmup;
        if (data.fps_threshold != null) document.getElementById('settFpsThreshold').value = data.fps_threshold;
      })
      .catch(function() {});
  },
};
