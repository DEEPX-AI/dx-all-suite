/**
 * Setup Panel — SDK 설치/샘플 다운로드 대시보드 UI
 */
class SetupPanel {
  constructor() {
    this.panel = document.getElementById('setup-panel');
    this.body = document.getElementById('setup-body');
    this.toggleBtn = document.getElementById('setup-toggle');
    this.status = null;
    this._isCompiling = false;
    this._installing = false;
    this._downloading = false;
    this._sdkCompleted = false;
    this._samplesCompleted = false;
  }

  async init() {
    if (!this.panel) return;
    this.toggleBtn.addEventListener('click', () => this.togglePanel());
    try {
      const res = await fetch('/setup/status');
      this.status = await res.json();
      this._render();
    } catch (e) {
      console.error('[SetupPanel] init error:', e);
    }
  }

  _render() {
    const s = this.status;
    if (!s) return;

    // SDK 상태
    const sdkIcon = document.getElementById('setup-sdk-icon');
    const sdkVersion = document.getElementById('setup-sdk-version');
    const installBtn = document.getElementById('setup-install-btn');

    if (s.dx_com_installed || this._sdkCompleted) {
      sdkIcon.textContent = '✅';
      sdkVersion.textContent = s.dx_com_version ? 'v' + s.dx_com_version : '';
      this._setActionButton(installBtn, '🔄', 'Reinstall');
    } else {
      sdkIcon.textContent = '❌';
      sdkVersion.textContent = '';
      this._setActionButton(installBtn, '📦', 'Install');
    }
    installBtn.onclick = () => this.installSDK();

    // 샘플 + 캘리브레이션 상태
    const samplesIcon = document.getElementById('setup-samples-icon');
    const downloadBtn = document.getElementById('setup-download-btn');
    const allDownloaded = Object.values(s.sample_models).every(m => m.downloaded) &&
                          s.calibration_data.downloaded;

    if (allDownloaded || this._samplesCompleted) {
      samplesIcon.textContent = '✅';
      this._setActionButton(downloadBtn, '🔄', 'Re-download');
    } else {
      samplesIcon.textContent = '❌';
      this._setActionButton(downloadBtn, '⬇️', 'Download');
    }
    downloadBtn.onclick = () => this.downloadSamples();

    // 패널 접기/펼치기 결정 (최초 렌더링 시에만)
    if (!this._initialRenderDone) {
      this._initialRenderDone = true;
      this._expand();
    }

    // 컴파일 폼 비활성화 여부
    if (!s.dx_com_installed) {
      this._disableCompileForm(true);
    } else {
      this._disableCompileForm(false);
    }

    // 샘플 선택 버튼 업데이트
    this._updateSampleSelector();

    // i18n 적용
    if (window.DXI18n && typeof DXI18n.applyLang === 'function') DXI18n.applyLang();
  }

  async installSDK() {
    if (this._installing || this._isCompiling) {
      if (this._isCompiling) alert(this._t('Compilation in progress. Cannot modify setup.'));
      return;
    }
    this._installing = true;
    const btn = document.getElementById('setup-install-btn');
    const progressDiv = document.getElementById('setup-install-progress');
    const bar = document.getElementById('setup-install-bar');
    const text = document.getElementById('setup-install-text');

    btn.disabled = true;
    progressDiv.style.display = 'block';

    try {
      const res = await fetch('/setup/install-sdk', { method: 'POST' });
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let installSucceeded = false;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          try {
            const event = JSON.parse(line.slice(6));
            if (event.progress !== undefined) {
              bar.style.width = event.progress + '%';
            }
            if (event.message) {
              text.textContent = event.message;
            }
            if (event.type === 'complete') {
              installSucceeded = true;
              this._markSdkInstalled();
            }
            if (event.type === 'complete' || event.type === 'error') {
              if (event.type === 'error') {
                bar.classList.add('error');
              }
            }
          } catch (e) { /* skip */ }
        }
      }
    } catch (e) {
      text.textContent = this._t('Error') + ': ' + e.message;
      bar.classList.add('error');
    }

    btn.disabled = false;
    this._installing = false;
    if (installSucceeded) this._markSdkInstalled();
    await this._refreshStatus();
  }

  async downloadSamples() {
    if (this._downloading || this._isCompiling) {
      if (this._isCompiling) alert(this._t('Compilation in progress. Cannot modify setup.'));
      return;
    }
    this._downloading = true;
    const btn = document.getElementById('setup-download-btn');
    const progressDiv = document.getElementById('setup-download-progress');
    const bar = document.getElementById('setup-download-bar');
    const text = document.getElementById('setup-download-text');

    btn.disabled = true;
    progressDiv.style.display = 'block';

    try {
      const res = await fetch('/setup/download-samples', { method: 'POST' });
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let downloadSucceeded = false;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop();

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue;
          try {
            const event = JSON.parse(line.slice(6));
            if (event.progress !== undefined) {
              bar.style.width = event.progress + '%';
            }
            if (event.message) {
              text.textContent = event.message;
            }
            if (event.type === 'complete') {
              downloadSucceeded = true;
              this._markSamplesDownloaded();
            }
            if (event.type === 'error') {
              bar.classList.add('error');
            }
          } catch (e) { /* skip */ }
        }
      }
    } catch (e) {
      text.textContent = this._t('Error') + ': ' + e.message;
      bar.classList.add('error');
    }

    btn.disabled = false;
    this._downloading = false;
    if (downloadSucceeded) this._markSamplesDownloaded();
    await this._refreshStatus();
  }

  selectSample(modelName) {
    if (!this.status) return;
    const model = this.status.sample_models[modelName];
    if (!model || !model.downloaded) return;

    const modelPath = document.getElementById('model_path');
    const configPath = document.getElementById('config_path');
    if (modelPath) modelPath.value = model.onnx_path;
    if (configPath) configPath.value = model.config_path;

    // 드롭존 숨기기 (서버 경로 모드)
    const modelServerPath = document.getElementById('model_server_path');
    const configServerPath = document.getElementById('config_server_path');
    if (modelServerPath && !modelServerPath.checked) modelServerPath.click();
    if (configServerPath && !configServerPath.checked) configServerPath.click();
  }

  togglePanel() {
    if (this.body.style.display === 'none') {
      this._expand();
    } else {
      this._collapse();
    }
  }

  setCompiling(isCompiling) {
    this._isCompiling = isCompiling;
  }

  _t(key) {
    return typeof T === 'function' ? T(key) : key;
  }

  _setActionButton(btn, icon, key) {
    if (!btn) return;
    let iconEl = btn.querySelector('.setup-action-icon');
    let labelEl = btn.querySelector('.setup-action-label');
    if (!iconEl || !labelEl) {
      btn.innerHTML = '<span class="setup-action-icon"></span><span class="setup-action-label"></span>';
      iconEl = btn.querySelector('.setup-action-icon');
      labelEl = btn.querySelector('.setup-action-label');
    }
    iconEl.textContent = icon;
    labelEl.textContent = this._t(key);
    btn.setAttribute('aria-label', this._t(key));
  }

  _markSdkInstalled() {
    this._sdkCompleted = true;
    if (this.status) this.status.dx_com_installed = true;
    const sdkIcon = document.getElementById('setup-sdk-icon');
    const installBtn = document.getElementById('setup-install-btn');
    if (sdkIcon) sdkIcon.textContent = '✅';
    this._setActionButton(installBtn, '🔄', 'Reinstall');
    this._disableCompileForm(false);
  }

  _markSamplesDownloaded() {
    this._samplesCompleted = true;
    if (this.status) {
      Object.values(this.status.sample_models || {}).forEach(m => { m.downloaded = true; });
      if (this.status.calibration_data) this.status.calibration_data.downloaded = true;
    }
    const samplesIcon = document.getElementById('setup-samples-icon');
    const downloadBtn = document.getElementById('setup-download-btn');
    if (samplesIcon) samplesIcon.textContent = '✅';
    this._setActionButton(downloadBtn, '🔄', 'Re-download');
    this._updateSampleSelector();
  }

  refreshLanguage() {
    if (this.status) this._render();
  }


  _expand() {
    this.body.style.display = 'block';
    this.toggleBtn.textContent = '▲';
  }

  _collapse() {
    this.body.style.display = 'none';
    this.toggleBtn.textContent = '▼';
  }

  _disableCompileForm(disabled) {
    const compileBtn = document.querySelector('.compile-btn');
    if (compileBtn) compileBtn.disabled = disabled;
    const form = document.getElementById('compile-form');
    if (form) {
      form.style.opacity = disabled ? '0.5' : '1';
    }
  }

  _updateSampleSelector() {
    const container = document.getElementById('sample-select-container');
    if (!container || !this.status) return;

    const models = this.status.sample_models;
    const hasAny = Object.values(models).some(m => m.downloaded);
    container.style.display = hasAny ? 'inline-block' : 'none';

    // 드롭다운 항목 생성
    const dropdown = document.getElementById('sample-dropdown');
    if (!dropdown) return;
    dropdown.innerHTML = '';
    Object.entries(models).forEach(([name, info]) => {
      const item = document.createElement('div');
      item.className = 'sample-dropdown-item' + (info.downloaded ? '' : ' disabled');
      item.textContent = name;
      if (!info.downloaded) {
        const note = document.createElement('span');
        note.className = 'sample-note';
        note.textContent = '(' + this._t('Download required') + ')';
        item.appendChild(note);
      } else {
        item.addEventListener('click', () => {
          this.selectSample(name);
          dropdown.classList.remove('open');
        });
      }
      dropdown.appendChild(item);
    });
  }

  async _refreshStatus() {
    try {
      const res = await fetch('/setup/status');
      this.status = await res.json();
      this._render();
    } catch (e) {
      console.error('[SetupPanel] refresh error:', e);
    }
  }
}

// 전역 인스턴스 + 자동 초기화
window.setupPanel = new SetupPanel();
document.addEventListener('DOMContentLoaded', function () {
  if (!window.setupPanel || !document.getElementById('setup-panel')) return;
  setupPanel.init();

  if (window.DXI18n && typeof DXI18n.onLangChange === 'function') {
    DXI18n.onLangChange(function () {
      if (window.setupPanel && typeof setupPanel.refreshLanguage === 'function') {
        setupPanel.refreshLanguage();
      }
    });
  }

  // 📦 샘플 선택 드롭다운 토글 (position: fixed — form-panel overflow 회피)
  var sampleBtn = document.getElementById('sample-select-btn');
  var sampleDD = document.getElementById('sample-dropdown');
  if (sampleBtn) {
    sampleBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = sampleDD.classList.toggle('open');
      if (open) {
        var r = sampleBtn.getBoundingClientRect();
        sampleDD.style.top = (r.bottom + 4) + 'px';
        sampleDD.style.left = Math.max(8, r.right - sampleDD.offsetWidth) + 'px';
      }
    });
    document.addEventListener('click', function () {
      sampleDD.classList.remove('open');
    });
  }
});
