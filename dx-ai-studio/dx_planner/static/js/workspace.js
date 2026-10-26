const PlannerWorkspace = {
  _state: 'empty',
  _selectedPlatformId: null,

  init() {
    this.root = document.getElementById('plannerWorkspace');
    this.recommendationsPanel = document.getElementById('recommendationsPanel');
    this.detailPanel = document.getElementById('detailPanel');
    this.detailEmpty = document.getElementById('detailEmpty');
    this.detailContent = document.getElementById('detailContent');
    this.autoRefreshNote = document.getElementById('autoRefreshNote');
    this.conditionSummary = document.getElementById('conditionSummary');
    this.recommendSummary = document.getElementById('recommendSummary');
    this.recommendationVerdict = document.getElementById('recommendationVerdict');
    this.workflowSteps = document.getElementById('workflowSteps');
    this.scopeBannerMeta = document.getElementById('scopeBannerMeta');
    this.setState('empty');
  },

  hasStarted() {
    return this._state !== 'empty';
  },

  getSelectedPlatformId() {
    return this._selectedPlatformId;
  },

  getComparePlatformId() {
    const dropdown = document.getElementById('compare-dropdown');
    return dropdown && dropdown.value ? dropdown.value : null;
  },

  clearCompareSelection() {
    const dropdown = document.getElementById('compare-dropdown');
    if (dropdown) dropdown.value = '';
  },

  setState(state) {
    this._state = state;
    if (!this.root) return;
    this.root.dataset.state = state;
    this.root.classList.remove('workspace-state-empty', 'workspace-state-recommended', 'workspace-state-detailed');
    this.root.classList.add('workspace-state-' + state);
    if (this.recommendationsPanel) this.recommendationsPanel.hidden = state === 'empty';
    if (this.detailPanel) this.detailPanel.hidden = state !== 'detailed';
    if (this.autoRefreshNote) this.autoRefreshNote.hidden = state === 'empty';
    this._updateWorkflowSteps(state);
  },

  showRecommendations() {
    this.setState('recommended');
  },

  showDetail(platformId) {
    this._selectedPlatformId = platformId;
    this.setState('detailed');
    if (this.detailEmpty) this.detailEmpty.hidden = true;
    if (this.detailContent) this.detailContent.hidden = false;
    this.markSelectedCard(platformId);
  },

  showDetailEmpty() {
    this._selectedPlatformId = null;
    if (this.detailEmpty) this.detailEmpty.hidden = false;
    if (this.detailContent) this.detailContent.hidden = true;
    this.markSelectedCard(null);
  },

  markSelectedCard(platformId) {
    document.querySelectorAll('#recommend-cards .rec-card').forEach(card => {
      card.classList.toggle('selected', Boolean(platformId) && card.dataset.platformId === platformId);
    });
  },

  renderRecommendationSummary(inputs, results) {
    if (this.conditionSummary) {
      const runtime = inputs.ort ? 'ONNX Runtime' : 'Native';
      this.conditionSummary.innerHTML = [
        this._summaryChip('Task', plannerTaskLabel(inputs.task)),
        this._summaryChip('Model', 'yolo26' + inputs.size),
        this._summaryChip('Channels', inputs.cameras),
        this._summaryChip('FPS', inputs.targetFps),
        this._summaryChip('Runtime', runtime),
      ].join('');
    }

    if (this.recommendSummary) {
      const meets = results.filter(r => r.meetsRequirement).length;
      const insufficient = Math.max(results.length - meets, 0);
      this.recommendSummary.innerHTML = [
        this._summaryChip('Meets', meets),
        this._summaryChip('Insufficient', insufficient),
      ].join('');
    }

    this._renderRecommendationVerdict(inputs, results);
  },

  renderScopeBannerMeta() {
    if (!this.scopeBannerMeta || typeof DataLoader === 'undefined') return;
    const meta = DataLoader.getMeta();
    const platformCount = meta.platform_count != null ? meta.platform_count : DataLoader.getPlatforms().length;
    const generated = DataLoader.getGeneratedAt();
    const generatedText = generated ? generated.slice(0, 10) : 'N/A';
    const tpl = (typeof T === 'function') ? T('{n} platforms · YOLO26 benchmark · updated {date}')
      : '{n} platforms · YOLO26 benchmark · updated {date}';
    this.scopeBannerMeta.textContent = tpl.replace('{n}', platformCount).replace('{date}', generatedText);
    if (!this._metaLangHooked && typeof DXI18n !== 'undefined' && DXI18n.onLangChange) {
      this._metaLangHooked = true;   // re-render on language change
      DXI18n.onLangChange(() => this.renderScopeBannerMeta());
    }
  },

  _renderRecommendationVerdict(inputs, results) {
    const el = this.recommendationVerdict;
    if (!el) return;

    if (!results || results.length === 0) {
      el.hidden = true;
      el.innerHTML = '';
      el.classList.remove('verdict-meets', 'verdict-insufficient', 'verdict-empty');
      return;
    }

    const top = results[0];
    const name = top.platform.npu.model + ' + ' + top.platform.host.name;
    const channels = this._formatChannels(top.maxChannels, top.boundaryFlag);
    const meets = top.meetsRequirement;
    // Measured at a tested stream count, or estimated from the measured total FPS.
    const evidence = {
      estimated: '<span data-i18n="(estimated)">(estimated)</span>',
      '+': '<span data-i18n="(estimated, at least)">(estimated, at least)</span>',
    }[top.boundaryFlag] || '<span data-i18n="(measured)">(measured)</span>';
    const throttleNote = top.throttled
      ? ' · <span data-i18n="NPU throttled while measured">NPU throttled while measured</span>'
      : '';
    el.hidden = false;
    el.classList.remove('verdict-meets', 'verdict-insufficient', 'verdict-empty');
    el.classList.add(meets ? 'verdict-meets' : 'verdict-insufficient');

    if (meets) {
      el.innerHTML =
        '<p class="verdict-line">' +
          '<strong data-i18n="Top pick">Top pick</strong>: ' +
          this._escHtml(name) + ' — ' +
          '<span class="ko">' + inputs.cameras + '채널 · ' + inputs.targetFps + ' FPS 조건 충족</span>' +
          '<span class="en">' + inputs.cameras + ' channels · ' + inputs.targetFps + ' FPS requirement met</span>' +
          '<span class="ja">' + inputs.cameras + 'ch · ' + inputs.targetFps + ' FPS を満たします</span>' +
          '<span class="zh-CN">满足 ' + inputs.cameras + ' 路 · ' + inputs.targetFps + ' FPS</span>' +
          '<span class="zh-TW">滿足 ' + inputs.cameras + ' 路 · ' + inputs.targetFps + ' FPS</span>' +
          '<span class="es">Cumple ' + inputs.cameras + ' canales · ' + inputs.targetFps + ' FPS</span>' +
          ' <span class="verdict-evidence">' + evidence + '</span>' +
        '</p>' +
        '<p class="verdict-sub txt-dim txt-sm">' +
          '<span class="ko">목표 ' + inputs.targetFps + ' FPS · 최대 ' + channels + '채널</span>' +
          '<span class="en">Target ' + inputs.targetFps + ' FPS · up to ' + channels + ' ch</span>' +
          '<span class="ja">目標 ' + inputs.targetFps + ' FPS · 最大 ' + channels + 'ch</span>' +
          '<span class="zh-CN">目标 ' + inputs.targetFps + ' FPS · 最多 ' + channels + ' 路</span>' +
          '<span class="zh-TW">目標 ' + inputs.targetFps + ' FPS · 最多 ' + channels + ' 路</span>' +
          '<span class="es">Objetivo ' + inputs.targetFps + ' FPS · hasta ' + channels + ' ch</span>' +
          throttleNote +
        '</p>';
    } else {
      el.innerHTML =
        '<p class="verdict-line">' +
          '<strong data-i18n="No exact match">No exact match</strong>: ' +
          this._escHtml(name) + ' — ' +
          '<span class="ko">최대 ' + channels + '채널 (요청 ' + inputs.cameras + '채널)</span>' +
          '<span class="en">max ' + channels + ' ch (requested ' + inputs.cameras + ')</span>' +
          '<span class="ja">最大 ' + channels + 'ch（要求 ' + inputs.cameras + 'ch）</span>' +
          '<span class="zh-CN">最多 ' + channels + ' 路（需要 ' + inputs.cameras + ' 路）</span>' +
          '<span class="zh-TW">最多 ' + channels + ' 路（需要 ' + inputs.cameras + ' 路）</span>' +
          '<span class="es">máx. ' + channels + ' canales (solicitados ' + inputs.cameras + ')</span>' +
          ' <span class="verdict-evidence">' + evidence + '</span>' +
        '</p>' +
        '<p class="verdict-sub txt-dim txt-sm">' +
          '<span class="ko">FPS·채널·모델 크기를 낮추거나 아래 카드에서 근접 옵션을 확인하세요.</span>' +
          '<span class="en">Lower FPS, channels, or model size — or review near matches below.</span>' +
          '<span class="ja">FPS・チャンネル・モデルサイズを下げるか、下のカードで近似候補を確認してください。</span>' +
          '<span class="zh-CN">降低 FPS、路数或模型大小，或查看下方近似选项。</span>' +
          '<span class="zh-TW">降低 FPS、路數或模型大小，或查看下方近似選項。</span>' +
          '<span class="es">Reduzca FPS, canales o tamaño del modelo, o revise opciones cercanas abajo.</span>' +
        '</p>';
    }

    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) {
      DXI18n.applyLang(el);
    }
  },

  _updateWorkflowSteps(state) {
    if (!this.workflowSteps) return;
    const activeStep = state === 'detailed' ? 'details' : (state === 'recommended' ? 'recommendations' : 'requirements');
    this.workflowSteps.querySelectorAll('.workflow-step').forEach(step => {
      const stepName = step.dataset.step;
      step.classList.toggle('is-active', stepName === activeStep);
      step.classList.toggle('is-done', this._isWorkflowStepDone(stepName, state));
    });
  },

  markCommerceStepActive(active) {
    if (!this.workflowSteps) return;
    const commerce = this.workflowSteps.querySelector('.workflow-step[data-step="commerce"]');
    if (commerce) commerce.classList.toggle('is-active', Boolean(active));
  },

  _isWorkflowStepDone(stepName, state) {
    if (stepName === 'requirements') return state !== 'empty';
    if (stepName === 'recommendations') return state === 'detailed';
    if (stepName === 'details') return false;
    if (stepName === 'commerce') return false;
    return false;
  },

  _formatChannels(val, flag) {
    if (flag === '+') return val + '+';
    return String(val);
  },

  _summaryChip(label, value) {
    const text = typeof T === 'function' ? T(label) : label;
    return '<span class="summary-chip"><strong>' + this._escHtml(text) + '</strong>' +
      '<span>' + this._escHtml(value) + '</span></span>';
  },

  _escHtml(value) {
    return String(value == null ? '' : value)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  },
};
