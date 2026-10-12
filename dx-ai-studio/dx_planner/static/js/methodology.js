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
    // In the user's language, in the card's own words — it read "max 8 ch · estimated" with the raw task id in a
    // Korean UI, and the Spanish kicker printed twice (spec addendum 2026-10-12).
    const t = key => (typeof T === 'function' ? T(key) : key);
    const fill = (key, vals) => Object.keys(vals).reduce((out, k) => out.split('{' + k + '}').join(vals[k]), t(key));
    const taskBtn = document.querySelector('.task-btn[data-task="' + inputs.task + '"]');
    const taskName = taskBtn ? taskBtn.textContent.trim() : inputs.task;
    const flag = top.boundaryFlag || 'measured';
    const evidence = t({ measured: 'Measured', estimated: 'Estimated', '+': 'Estimated+' }[flag] || 'Measured');
    const topChannels = fill('{n} ch', { n: top.maxChannels + (flag === '+' ? '+' : '') });

    this.liveSummary.hidden = false;
    this.liveSummary.innerHTML =
      '<p class="methodology-live-kicker panel-kicker">' + this._esc(t('This session')) + '</p>' +
      '<ul class="methodology-live-list">' +
        '<li><code>yolo26' + this._esc(inputs.size) + '</code> · ' + this._esc(taskName) +
          ' · ' + this._esc(fill('{n} ch', { n: inputs.cameras })) + ' · ' + this._esc(inputs.targetFps) + ' FPS</li>' +
        '<li>' + this._esc(t('Top pick')) + ': ' +
          this._esc(top.platform.npu.model + ' + ' + top.platform.host.name) +
          ' — ' + this._esc(topChannels) + ' · ' + this._esc(evidence) + '</li>' +
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
