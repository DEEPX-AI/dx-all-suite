/**
 * WizardController — EdgeGuide 조건 입력 패널 UI 제어.
 */
const WizardController = {
  _state: {
    task: 'object_detection',
    size: 'n',
    cameras: 4,
    targetFps: 30,
    priority: 'channels',
    ort: true,
    fpsHeadroom: 0.1,
    maxLatencyMs: null,
  },

  _setupStep: 1,
  _setupUnlocked: false,
  _recommendCallback: null,
  _changeCallbacks: [],

  _TASKS: [
    { id: 'object_detection', icon: '🎯', ko: '객체 탐지', en: 'Object Detection' },
    { id: 'pose_estimation', icon: '🏃', ko: '자세 추정', en: 'Pose Estimation' },
    { id: 'segmentation', icon: '🧩', ko: '분할', en: 'Segmentation' },
    { id: 'oriented_bbox', icon: '📐', ko: '회전 박스', en: 'Oriented BBox' },
    { id: 'classification', icon: '🏷️', ko: '분류', en: 'Classification' },
  ],

  _SIZES: [
    { id: 'n', ko: '최고속', en: 'Fastest' },
    { id: 's', ko: '빠름', en: 'Fast' },
    { id: 'm', ko: '균형', en: 'Balanced' },
    { id: 'l', ko: '정확', en: 'Accurate' },
    { id: 'x', ko: '최고정확', en: 'Most Accurate' },
  ],

  _LATENCY_PRESET_MS: [33, 50, 100, 150, 200],

  init() {
    this._bindTaskButtons();
    this._bindSizeButtons();
    this._bindSlider();
    this._bindFpsSelect();
    this._bindPriorityRadio();
    this._bindRecommendButton();
    this._bindSetupNavigation();
    this._bindAdvancedSettings();

    document.querySelectorAll('.ort-btn[data-ort]').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.ort-btn').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        this._state.ort = btn.dataset.ort === 'true';
        this._notifyChange();
      });
    });

    this._syncUI();
    this._syncSetupSteps();
  },

  _bindTaskButtons() {
    document.querySelectorAll('.task-btn[data-task]').forEach(btn => {
      btn.addEventListener('click', () => {
        this._state.task = btn.dataset.task;
        document.querySelectorAll('.task-btn[data-task]').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        this._notifyChange();
      });
    });
  },

  _bindSizeButtons() {
    document.querySelectorAll('.size-btn[data-size]').forEach(btn => {
      btn.addEventListener('click', () => {
        this._state.size = btn.dataset.size;
        document.querySelectorAll('.size-btn[data-size]').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        this._notifyChange();
      });
    });
  },

  _bindSlider() {
    const slider = document.getElementById('channelSlider');
    const display = document.getElementById('channelValue');
    if (!slider || !display) return;
    slider.addEventListener('input', () => {
      this._state.cameras = parseInt(slider.value, 10);
      display.textContent = slider.value;
      this._notifyChange();
    });
  },

  _bindFpsSelect() {
    const select = document.getElementById('targetFps');
    if (!select) return;
    select.addEventListener('change', () => {
      this._state.targetFps = parseInt(select.value, 10);
      this._notifyChange();
    });
  },

  _bindPriorityRadio() {
    document.querySelectorAll('input[name="priority"]').forEach(radio => {
      radio.addEventListener('change', () => {
        if (radio.checked) {
          this._state.priority = radio.value;
          this._notifyChange();
        }
      });
    });
  },

  _bindAdvancedSettings() {
    const headroomSelect = document.getElementById('fpsHeadroom');
    if (headroomSelect) {
      headroomSelect.addEventListener('change', () => {
        this._state.fpsHeadroom = parseFloat(headroomSelect.value);
        this._notifyChange();
      });
    }

    const presetSelect = document.getElementById('maxLatencyPreset');
    if (presetSelect) {
      presetSelect.addEventListener('change', () => {
        this._onMaxLatencyPresetChange(presetSelect.value);
      });
    }

    const latencyInput = document.getElementById('maxLatencyMs');
    if (latencyInput) {
      const onLatencyInput = () => this._onMaxLatencyInputChange();
      latencyInput.addEventListener('input', onLatencyInput);
      latencyInput.addEventListener('change', onLatencyInput);
    }
  },

  _parseLatencyMs(raw) {
    if (raw == null || raw === '') return null;
    const parsed = parseInt(String(raw).trim(), 10);
    return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
  },

  _onMaxLatencyPresetChange(presetValue) {
    const input = document.getElementById('maxLatencyMs');
    if (!presetValue) {
      this._state.maxLatencyMs = null;
      if (input) input.value = '';
    } else {
      const ms = this._parseLatencyMs(presetValue);
      this._state.maxLatencyMs = ms;
      if (input && ms != null) input.value = String(ms);
    }
    this._notifyChange();
  },

  _onMaxLatencyInputChange() {
    const input = document.getElementById('maxLatencyMs');
    const presetSelect = document.getElementById('maxLatencyPreset');
    const raw = input ? input.value.trim() : '';
    const ms = this._parseLatencyMs(raw);
    this._state.maxLatencyMs = ms;

    if (!presetSelect) {
      this._notifyChange();
      return;
    }

    if (ms == null) {
      presetSelect.value = '';
    } else if (this._LATENCY_PRESET_MS.includes(ms)) {
      presetSelect.value = String(ms);
    } else {
      presetSelect.value = '';
    }
    this._notifyChange();
  },

  _syncMaxLatencyControls() {
    const presetSelect = document.getElementById('maxLatencyPreset');
    const input = document.getElementById('maxLatencyMs');
    if (!presetSelect || !input) return;

    const ms = this._state.maxLatencyMs;
    if (ms == null) {
      presetSelect.value = '';
      input.value = '';
      return;
    }

    input.value = String(ms);
    presetSelect.value = this._LATENCY_PRESET_MS.includes(ms) ? String(ms) : '';
  },

  _bindRecommendButton() {
    const btn = document.getElementById('btnRecommend');
    if (!btn) return;
    btn.addEventListener('click', () => {
      if (btn.disabled) return;
      if (this._recommendCallback) this._recommendCallback(this.getInputs());
    });
  },

  _bindSetupNavigation() {
    const nextBtn = document.getElementById('btnSetupNext');
    if (nextBtn) {
      nextBtn.addEventListener('click', () => this.goToSetupStep(2));
    }
    const backBtn = document.getElementById('btnSetupBack');
    if (backBtn) {
      backBtn.addEventListener('click', () => this.goToSetupStep(1));
    }
  },

  goToSetupStep(step) {
    this._setupStep = step === 2 ? 2 : 1;
    this._syncSetupSteps();
    if (step === 2) {
      const firstPriority = document.querySelector('#requirementsStep2 input[name="priority"]');
      if (firstPriority) firstPriority.focus();
    }
  },

  /** Tutorial/help: restore the setup wizard to its first stage without manual DOM patches. */
  resetSetupForTutorial() {
    this._setupStep = 1;
    this._setupUnlocked = false;
    const stage = document.getElementById('requirementsWizardStage');
    if (stage) stage.classList.remove('is-priority-open');
    this._syncSetupSteps();
  },

  unlockSetupSteps() {
    this._setupUnlocked = true;
    this._syncSetupSteps();
  },

  _syncSetupSteps() {
    const stage = document.getElementById('requirementsWizardStage');
    const step2 = document.getElementById('requirementsStep2');
    const nextBtn = document.getElementById('btnSetupNext');
    const backBtn = document.getElementById('btnSetupBack');
    const recommendBtn = document.getElementById('btnRecommend');
    const started = typeof PlannerWorkspace !== 'undefined' && PlannerWorkspace.hasStarted();
    const showBoth = started || this._setupUnlocked;
    const priorityOpen = showBoth || this._setupStep === 2;

    if (stage) stage.classList.toggle('is-priority-open', priorityOpen);
    if (step2) step2.setAttribute('aria-hidden', priorityOpen ? 'false' : 'true');
    if (nextBtn) nextBtn.hidden = showBoth || this._setupStep !== 1;
    if (backBtn) backBtn.hidden = showBoth || this._setupStep !== 2;
    if (recommendBtn) {
      recommendBtn.disabled = !showBoth && this._setupStep !== 2;
      recommendBtn.classList.toggle('is-ready', !recommendBtn.disabled);
    }
  },

  _syncUI() {
    // 초기 task 버튼 활성화
    const taskBtn = document.querySelector(`.task-btn[data-task="${this._state.task}"]`);
    if (taskBtn) taskBtn.classList.add('selected');

    // 초기 size 버튼 활성화
    const sizeBtn = document.querySelector(`.size-btn[data-size="${this._state.size}"]`);
    if (sizeBtn) sizeBtn.classList.add('selected');

    // 슬라이더 초기값
    const slider = document.getElementById('channelSlider');
    const display = document.getElementById('channelValue');
    if (slider) slider.value = this._state.cameras;
    if (display) display.textContent = this._state.cameras;

    // FPS 초기값
    const select = document.getElementById('targetFps');
    if (select) select.value = this._state.targetFps;

    // 우선순위 초기값
    const radio = document.querySelector(`input[name="priority"][value="${this._state.priority}"]`);
    if (radio) radio.checked = true;

    // ORT 초기값
    const ortBtn = document.querySelector(`.ort-btn[data-ort="${this._state.ort}"]`);
    if (ortBtn) ortBtn.classList.add('selected');

    const headroomSelect = document.getElementById('fpsHeadroom');
    if (headroomSelect) headroomSelect.value = String(this._state.fpsHeadroom);

    this._syncMaxLatencyControls();
  },

  getInputs() {
    return { ...this._state };
  },

  setInputs({ task, size, cameras, targetFps, ort, fpsHeadroom, maxLatencyMs, priority }) {
    let changed = false;
    if (priority !== undefined) {
      changed = changed || this._state.priority !== priority;
      this._state.priority = priority;
      document.querySelectorAll('input[name="priority"]').forEach(r => { r.checked = false; });
      const radio = document.querySelector(`input[name="priority"][value="${priority}"]`);
      if (radio) radio.checked = true;
    }
    if (task !== undefined) {
      changed = changed || this._state.task !== task;
      this._state.task = task;
      document.querySelectorAll('.task-btn[data-task]').forEach(b => b.classList.remove('selected'));
      const btn = document.querySelector(`.task-btn[data-task="${task}"]`);
      if (btn) btn.classList.add('selected');
    }
    if (size !== undefined) {
      changed = changed || this._state.size !== size;
      this._state.size = size;
      document.querySelectorAll('.size-btn[data-size]').forEach(b => b.classList.remove('selected'));
      const btn = document.querySelector(`.size-btn[data-size="${size}"]`);
      if (btn) btn.classList.add('selected');
    }
    if (cameras !== undefined && !isNaN(cameras)) {
      changed = changed || this._state.cameras !== cameras;
      this._state.cameras = cameras;
      const sl = document.getElementById('channelSlider');
      const dv = document.getElementById('channelValue');
      if (sl) sl.value = cameras;
      if (dv) dv.textContent = cameras;
    }
    if (targetFps !== undefined && !isNaN(targetFps)) {
      changed = changed || this._state.targetFps !== targetFps;
      this._state.targetFps = targetFps;
      const sel = document.getElementById('targetFps');
      if (sel) sel.value = targetFps;
    }
    if (ort !== undefined) {
      changed = changed || this._state.ort !== ort;
      this._state.ort = ort;
      document.querySelectorAll('.ort-btn').forEach(b => b.classList.remove('selected'));
      const btn = document.querySelector(`.ort-btn[data-ort="${ort}"]`);
      if (btn) btn.classList.add('selected');
    }
    if (fpsHeadroom !== undefined && !isNaN(fpsHeadroom)) {
      changed = changed || this._state.fpsHeadroom !== fpsHeadroom;
      this._state.fpsHeadroom = fpsHeadroom;
      const sel = document.getElementById('fpsHeadroom');
      if (sel) sel.value = String(fpsHeadroom);
    }
    if (maxLatencyMs !== undefined) {
      changed = changed || this._state.maxLatencyMs !== maxLatencyMs;
      this._state.maxLatencyMs = maxLatencyMs;
      this._syncMaxLatencyControls();
    }
    if (changed) this._notifyChange();
  },

  onRecommend(callback) {
    this._recommendCallback = callback;
  },

  onChange(callback) {
    this._changeCallbacks.push(callback);
  },

  _notifyChange() {
    this._changeCallbacks.forEach(cb => cb(this.getInputs()));
  },
};
if (typeof registerPlannerLangRefresher === 'function') {
  registerPlannerLangRefresher(function() {
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
  });
}
