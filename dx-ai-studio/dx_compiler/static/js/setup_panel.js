/**
 * Setup Panel — SDK 설치/샘플 다운로드 대시보드 UI
 *
 * 공용 단계 목록의 압축형 (shared/static/dx-steps.js · 아이콘 체계 단계 2c). 여기서는 상태만 알린다
 * (DXSteps.set) — 뱃지 · 다음 단계 · 막대 · 모두 끝났을 때의 한 줄 접힘은 부품이 칠한다.
 * Compile 버튼의 잠금은 이 파일 한 곳이 정한다: SDK 가 없거나 /feature-check 가 컴파일 불가라고
 * 하면 잠그고, 그 이유를 버튼 옆에 적는다 (_disableCompileForm).
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
    this._sdkFailed = false;
    this._samplesFailed = false;
    this._featureBlocked = false;
  }

  async init() {
    if (!this.panel) return;
    this.toggleBtn.addEventListener('click', () => this.togglePanel());
    try {
      const res = await fetch('/setup/status');
      this.status = await res.json();
      this._render();
    } catch (e) {
      this.panel.removeAttribute('aria-busy');
      console.error('[SetupPanel] init error:', e);
    }
  }

  _render() {
    const s = this.status;
    if (!s) return;
    // 첫 상태가 오기 전에는 두 단계가 모두 todo 라 전체가 펼쳐졌다가 한 줄로 접히며 폼을 밀었다.
    this.panel.removeAttribute('aria-busy');

    // SDK 상태
    const sdkVersion = document.getElementById('setup-sdk-version');
    const installBtn = document.getElementById('setup-install-btn');

    const sdkOk = !!(s.dx_com_installed || this._sdkCompleted);
    if (sdkOk) {
      sdkVersion.textContent = s.dx_com_version ? 'v' + s.dx_com_version : '';
      this._setActionButton(installBtn, 'refresh', 'Reinstall');
    } else {
      sdkVersion.textContent = '';
      this._setActionButton(installBtn, 'download', 'Install');
    }
    if (!this._installing) this._step('sdk', sdkOk ? 'done' : (this._sdkFailed ? 'failed' : 'todo'));
    installBtn.onclick = () => this.installSDK();

    // 샘플 + 캘리브레이션 상태
    const downloadBtn = document.getElementById('setup-download-btn');
    const allDownloaded = Object.values(s.sample_models || {}).every(m => m.downloaded) &&
                          (s.calibration_data && s.calibration_data.downloaded);

    const samplesOk = !!(allDownloaded || this._samplesCompleted);
    if (samplesOk) {
      this._setActionButton(downloadBtn, 'refresh', 'Re-download');
    } else {
      this._setActionButton(downloadBtn, 'download', 'Download');
    }
    const samplesCount = document.getElementById('setup-samples-count');
    if (samplesCount) samplesCount.textContent = samplesOk ? this._sampleCountText() : '';
    if (!this._downloading) this._step('samples', samplesOk ? 'done' : (this._samplesFailed ? 'failed' : 'todo'));
    this._updateSummary();
    downloadBtn.onclick = () => this.downloadSamples();

    // 패널 접기/펼치기 결정 (최초 렌더링 시에만)
    if (!this._initialRenderDone) {
      this._initialRenderDone = true;
      this._expand();
    }

    // 컴파일 버튼 잠금 여부 (이유는 버튼 옆에)
    this._applyCompileGate();

    // 샘플 선택 버튼 업데이트
    this._updateSampleSelector();

    // i18n 적용
    if (window.DXI18n && typeof DXI18n.applyLang === 'function') DXI18n.applyLang();
  }

  async installSDK(password, authFailed) {
    if (this._installing || this._isCompiling) {
      if (this._isCompiling) alert(this._t('Compilation in progress. Cannot modify setup.'));
      return;
    }

    // dx_app Setup pattern: collect sudo before POST when install.sh is required (no local wheel).
    // Avoids relying on a single-chunk SSE need_sudo event after the Install click finishes.
    if (!password && this.status && this.status.install_requires_sudo) {
      const pw = await this._promptSudoPassword(!!authFailed);
      if (!pw) return;
      return this.installSDK(pw, false);
    }

    const btn = document.getElementById('setup-install-btn');
    const progressDiv = document.getElementById('setup-install-progress');
    const bar = document.getElementById('setup-install-bar');
    const text = document.getElementById('setup-install-text');
    // Guard: if the panel DOM isn't present, bail WITHOUT latching _installing — otherwise a
    // throw here would leave _installing=true and block every future Install click.
    if (!btn || !progressDiv || !bar || !text) return;

    this._installing = true;
    this._sdkFailed = false;
    this._step('sdk', 'running');
    btn.disabled = true;
    progressDiv.style.display = 'block';
    bar.classList.remove('error');

    let installSucceeded = false;
    try {
      const res = await fetch('/setup/install-sdk', {
        method: 'POST',
        headers: password ? { 'Content-Type': 'application/json' } : {},
        body: password ? JSON.stringify({ password: password }) : undefined,
      });
      let sudoNeeded = false;
      let sudoMsg = '';
      const logEl = document.getElementById('setup-install-log');
      if (logEl) { logEl.textContent = ''; logEl.style.display = 'none'; }

      // Stream events LIVE so the install.sh output scrolls in real time (minutes-long).
      await this._readSseEvents(res.body, (event) => {
        if (event.progress !== undefined) {
          bar.style.width = event.progress + '%';
        }
        if (event.message) {
          text.textContent = event.message;
          this._appendInstallLog(event.message);
        }
        if (event.type === 'need_sudo' || event.type === 'sudo_auth') {
          sudoNeeded = true;
          sudoMsg = event.message || '';
        }
        if (event.type === 'complete') {
          installSucceeded = true;
          this._markSdkInstalled();
        }
        if (event.type === 'error') {
          bar.classList.add('error');
          this._sdkFailed = true;
        }
      });

      if (sudoNeeded) {
        this._installing = false;
        btn.disabled = false;
        const pw = await this._promptSudoPassword(true);
        if (pw) return this.installSDK(pw, true);
        text.textContent = this._t('Installation cancelled');
        bar.classList.add('error');
        this._step('sdk', 'todo');
        return;
      }
    } catch (e) {
      text.textContent = this._t('Error') + ': ' + e.message;
      bar.classList.add('error');
      this._sdkFailed = true;
    }

    btn.disabled = false;
    this._installing = false;
    if (installSucceeded) this._markSdkInstalled();
    await this._refreshStatus();
  }

  /** Parse SSE stream from fetch body. Calls onEvent(ev) LIVE as each event arrives (so the
   *  install log streams in real time, like the compile/stream-setup panels), handles the
   *  final chunk when done=true, and also returns all events for post-processing. */
  async _readSseEvents(body, onEvent) {
    const reader = body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    const events = [];
    const emit = (jsonStr) => {
      try {
        const ev = JSON.parse(jsonStr);
        events.push(ev);
        if (onEvent) { try { onEvent(ev); } catch (e) { /* UI cb error — keep reading */ } }
      } catch (e) { /* skip partial / non-JSON */ }
    };

    while (true) {
      const { done, value } = await reader.read();
      if (value) {
        buffer += decoder.decode(value, { stream: true });
      }
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const raw of lines) {
        const line = raw.trim();
        if (line.startsWith('data: ')) emit(line.slice(6));
      }
      if (done) break;
    }

    const tail = buffer.trim();
    if (tail.startsWith('data: ')) emit(tail.slice(6));
    return events;
  }

  _appendInstallLog(line) {
    const log = document.getElementById('setup-install-log');
    if (!log) return;
    log.style.display = 'block';
    log.textContent += (log.textContent ? '\n' : '') + line;
    log.scrollTop = log.scrollHeight;
  }

  _promptSudoPassword(authFailed) {
    const t = (k) => this._t(k);
    return new Promise((resolve) => {
      document.getElementById('setup-sudo-modal')?.remove();
      const root = document.documentElement || document.body;
      const overlay = document.createElement('div');
      overlay.id = 'setup-sudo-modal';
      overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,.55);display:flex;' +
        'align-items:center;justify-content:center;z-index:100001;padding:20px';
      const box = document.createElement('div');
      box.style.cssText = 'width:min(460px,92vw);background:var(--surface-panel,var(--control-bg));' +
        'border:1px solid var(--border-subtle);border-radius:12px;padding:20px;' +
        'box-shadow:0 20px 60px rgba(0,0,0,.35)';
      box.innerHTML =
        '<h3 style="margin:0 0 8px">' + this._ico('lock') + ' ' + t('Administrator (sudo) Authentication') + '</h3>' +
        (authFailed ? '<p style="margin:0 0 8px;color:var(--status-error,#e5484d);font-size:13px">' +
          t('Incorrect password. Please try again.') + '</p>' : '') +
        '<p class="txt-dim" style="margin:0 0 12px;font-size:13px;line-height:1.45">' +
          t('Enter your sudo password to download and install the DX Compiler SDK.') + '</p>' +
        '<input id="_sudo-pw" type="password" autocomplete="current-password" ' +
          'style="width:100%;box-sizing:border-box;padding:9px 11px;border-radius:8px;' +
          'border:1px solid var(--border-subtle);background:var(--surface-page);color:var(--text-primary)" ' +
          'placeholder="' + t('Enter password') + '">' +
        '<div style="display:flex;justify-content:flex-end;gap:8px;margin-top:14px">' +
          '<button id="_sudo-cancel" class="fp-btn" type="button">' + t('Cancel') + '</button>' +
          '<button id="_sudo-ok" class="fp-btn fp-select" type="button">' + t('OK') + '</button>' +
        '</div>';
      overlay.appendChild(box);
      root.appendChild(overlay);
      const input = box.querySelector('#_sudo-pw');
      const done = (v) => { overlay.remove(); resolve(v || null); };
      box.querySelector('#_sudo-cancel').onclick = () => done(null);
      box.querySelector('#_sudo-ok').onclick = () => done(input.value);
      input.onkeydown = (e) => {
        if (e.key === 'Enter') { e.preventDefault(); done(input.value); }
        else if (e.key === 'Escape') { e.preventDefault(); done(null); }
      };
      // Ignore the Install-button click that may still be bubbling when the modal opens.
      let backdropReady = false;
      setTimeout(() => { backdropReady = true; }, 350);
      overlay.onclick = (e) => {
        if (backdropReady && e.target === overlay) done(null);
      };
      setTimeout(() => input.focus(), 0);
    });
  }

  async downloadSamples() {
    if (this._downloading || this._isCompiling) {
      if (this._isCompiling) alert(this._t('Compilation in progress. Cannot modify setup.'));
      return;
    }
    const btn = document.getElementById('setup-download-btn');
    const progressDiv = document.getElementById('setup-download-progress');
    const bar = document.getElementById('setup-download-bar');
    const text = document.getElementById('setup-download-text');
    // Guard: bail WITHOUT latching _downloading if the DOM isn't present — otherwise a throw
    // here leaves _downloading=true and blocks every future Download click.
    if (!btn || !progressDiv || !bar || !text) return;

    this._downloading = true;
    this._samplesFailed = false;
    this._step('samples', 'running');
    btn.disabled = true;
    progressDiv.style.display = 'block';
    bar.classList.remove('error');

    let downloadSucceeded = false;
    try {
      const res = await fetch('/setup/download-samples', { method: 'POST' });
      // Stream events LIVE (like install) so download progress updates in real time.
      await this._readSseEvents(res.body, (event) => {
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
          this._samplesFailed = true;
        }
      });
    } catch (e) {
      text.textContent = this._t('Error') + ': ' + e.message;
      bar.classList.add('error');
      this._samplesFailed = true;
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

    // 값만 바꾸면 change 가 오지 않아 그래프가 그려지지 않았다 — 직접 입력할 때와 같은 길로 (2026-10-11 audit)
    if (modelPath) modelPath.dispatchEvent(new Event('change', { bubbles: true }));
    if (configPath) configPath.dispatchEvent(new Event('change', { bubbles: true }));
  }

  togglePanel() {
    // 모두 끝나 한 줄에서 펼친 상태면, 접기는 다시 그 한 줄로.
    if (this.panel.classList.contains('is-complete') && this.panel.classList.contains('is-expanded')) {
      this.panel.classList.remove('is-expanded');
      return;
    }
    if (this.body.style.display === 'none') {
      this._expand();
    } else {
      this._collapse();
    }
  }

  setCompiling(isCompiling) {
    this._isCompiling = isCompiling;
  }

  /** /feature-check 의 결과 (index.html). 버튼을 직접 만지지 않고 여기로 알린다 — 잠금은 한 곳에서. */
  setFeatureCompile(available) {
    this._featureBlocked = !available;
    this._applyCompileGate();
  }

  /** 튜토리얼이 접힌 칸 안의 버튼을 가리키기 전에 — 한 줄 요약도, 접힌 단계도 편다. */
  revealForTour() {
    if (!this.panel) return;
    this.panel.classList.add('is-expanded');
    this._expand();
    if (window.DXSteps) { DXSteps.open(this.panel, 'sdk'); DXSteps.open(this.panel, 'samples'); }
  }

  _ico(name) {
    return typeof window.DXIcon === 'function' ? window.DXIcon(name) : '';
  }

  _step(id, state) {
    if (this.panel && window.DXSteps) DXSteps.set(this.panel, id, state);
  }

  _sampleCountText() {
    const n = Object.values((this.status && this.status.sample_models) || {}).filter(m => m.downloaded).length;
    return this._t('{n} sample models').split('{n}').join(String(n));
  }

  /* 모두 끝났을 때의 한 줄: "Setup ready · SDK v… · 샘플 N개". */
  _updateSummary() {
    const facts = document.getElementById('setup-summary-facts');
    if (!facts || !this.status) return;
    const parts = [];
    if (this.status.dx_com_version) parts.push('SDK v' + this.status.dx_com_version);
    parts.push(this._sampleCountText());
    facts.textContent = '· ' + parts.join(' · ');
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
    iconEl.innerHTML = this._ico(icon);
    labelEl.textContent = this._t(key);
    btn.setAttribute('aria-label', this._t(key));
  }

  _markSdkInstalled() {
    this._sdkCompleted = true;
    if (this.status) this.status.dx_com_installed = true;
    this._sdkFailed = false;
    const installBtn = document.getElementById('setup-install-btn');
    this._step('sdk', 'done');
    this._setActionButton(installBtn, 'refresh', 'Reinstall');
    this._applyCompileGate();
  }

  _markSamplesDownloaded() {
    this._samplesCompleted = true;
    if (this.status) {
      Object.values(this.status.sample_models || {}).forEach(m => { m.downloaded = true; });
      if (this.status.calibration_data) this.status.calibration_data.downloaded = true;
    }
    this._samplesFailed = false;
    const downloadBtn = document.getElementById('setup-download-btn');
    this._step('samples', 'done');
    this._setActionButton(downloadBtn, 'refresh', 'Re-download');
    const samplesCount = document.getElementById('setup-samples-count');
    if (samplesCount) samplesCount.textContent = this._sampleCountText();
    this._updateSummary();
    this._updateSampleSelector();
  }

  refreshLanguage() {
    if (this.status) this._render();
  }


  _expand() {
    this.body.style.display = 'block';
    this.toggleBtn.setAttribute('aria-expanded', 'true');
  }

  _collapse() {
    this.body.style.display = 'none';
    this.toggleBtn.setAttribute('aria-expanded', 'false');
  }

  _applyCompileGate() {
    const sdkOk = !!(this.status && (this.status.dx_com_installed || this._sdkCompleted));
    if (!this.status && !this._featureBlocked) return;
    const reason = !sdkOk && this.status ? 'Install the SDK first'
      : (this._featureBlocked ? 'Compile unavailable: dx_com not installed on server.' : '');
    this._disableCompileForm(!!reason, reason);
  }

  _disableCompileForm(disabled, reason) {
    // Only gate the submit action — never disable/grey the input fields. Grey-ing the whole
    // form made the compiler read as "Input UI unusable" whenever the venv probe disagreed
    // with in-process dx_com. Users must still be able to fill model/config/options; if
    // dx_com is truly missing, the disabled compile button + Setup banner convey that.
    const compileBtn = document.querySelector('.compile-btn');
    if (compileBtn) {
      compileBtn.disabled = disabled;
      if (disabled) compileBtn.setAttribute('aria-describedby', 'compile-gate-reason');
      else compileBtn.removeAttribute('aria-describedby');
    }
    // 잠긴 버튼만 보이면 왜 못 누르는지 모른다 — 이유를 옆에 적는다.
    const why = document.getElementById('compile-gate-reason');
    if (why) {
      why.hidden = !disabled;
      why.innerHTML = disabled ? this._ico('lock') + '<span>' + this._t(reason || 'Install the SDK first') + '</span>' : '';
    }
    const form = document.getElementById('compile-form');
    if (form) form.style.opacity = '1';
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

  // 샘플 선택 드롭다운 토글 (position: fixed — form-panel overflow 회피)
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
