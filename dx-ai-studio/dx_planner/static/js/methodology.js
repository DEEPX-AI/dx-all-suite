/**
 * Methodology dialog — explains how EdgeGuide ranks platforms.
 */
const MethodologyDialog = {
  init() {
    this.dialog = document.getElementById('methodologyDialog');
    this.liveSummary = document.getElementById('methodologyLiveSummary');
    document.querySelectorAll('[data-open-methodology]').forEach(btn => {
      btn.addEventListener('click', () => this.open());
    });
    const closeBtn = document.getElementById('methodologyClose');
    if (closeBtn) closeBtn.addEventListener('click', () => this.close());
    if (this.dialog) {
      this.dialog.addEventListener('click', (event) => {
        if (event.target === this.dialog) this.close();
      });
      this.dialog.addEventListener('cancel', (event) => {
        event.preventDefault();
        this.close();
      });
    }
  },

  open() {
    if (!this.dialog) return;
    this._renderLiveSummary();
    if (typeof this.dialog.showModal === 'function') {
      this.dialog.showModal();
    } else {
      this.dialog.setAttribute('open', '');
    }
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) {
      DXI18n.applyLang(this.dialog);
    }
  },

  close() {
    if (!this.dialog) return;
    if (typeof this.dialog.close === 'function') {
      this.dialog.close();
    } else {
      this.dialog.removeAttribute('open');
    }
  },

  _renderLiveSummary() {
    if (!this.liveSummary) return;
    const inputs = typeof WizardController !== 'undefined'
      ? WizardController.getInputs()
      : null;
    const results = typeof window.PlannerRuntime !== 'undefined'
      ? window.PlannerRuntime.getLastResults()
      : null;

    if (!inputs || !results || !results.length) {
      this.liveSummary.hidden = true;
      this.liveSummary.innerHTML = '';
      return;
    }

    const top = results[0];
    const headroomPct = Math.round((inputs.fpsHeadroom != null ? inputs.fpsHeadroom : 0.1) * 100);
    const effective = top.effectiveTargetFps || inputs.targetFps;
    const flag = top.boundaryFlag || 'measured';

    this.liveSummary.hidden = false;
    this.liveSummary.innerHTML =
      '<p class="methodology-live-kicker panel-kicker">' +
        '<span class="ko">현재 세션</span><span class="en">This session</span><span class="ja">このセッション</span>' +
        '<span class="zh-CN">当前会话</span><span class="zh-TW">目前工作階段</span><span class="es">Esta sesión</span>' +
      '</p>' +
      '<ul class="methodology-live-list">' +
        '<li><code>yolo26' + this._esc(inputs.size) + '</code> · ' + this._esc(inputs.task) +
          ' · ' + inputs.cameras + ' ch · ' + inputs.targetFps + ' FPS' +
          ' (+ ' + headroomPct + '% → ' + effective + ' FPS effective)</li>' +
        '<li><span class="ko">1순위</span><span class="en">Top pick</span>: ' +
          this._esc(top.platform.npu.model + ' + ' + top.platform.host.name) +
          ' — max ' + top.maxChannels + ' ch · ' + flag + '</li>' +
      '</ul>';

    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) {
      DXI18n.applyLang(this.liveSummary);
    }
  },

  _esc(value) {
    const div = document.createElement('div');
    div.textContent = value == null ? '' : String(value);
    return div.innerHTML;
  },
};

if (typeof registerPlannerLangRefresher === 'function') {
  registerPlannerLangRefresher(function() {
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
  });
}
