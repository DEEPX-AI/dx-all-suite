window.LabPortal = (function () {
  'use strict';
  var _ready = false;
  var _cardsBound = false;
  var _capabilities = null;
  var _composerOpened = false;
  var _currentManifest = null;
  var _dryRunInFlight = false;
  var _applyInFlight = false;

  function _text(en, ko) {
    return (typeof T === 'function') ? T(en, ko) : en;
  }

  async function _labGet(path) {
    var headers = {};
    if (S.labToken) headers['X-Lab-Token'] = S.labToken;
    var res = await fetch(path, { headers: headers });
    var data = await res.json().catch(function () { return {}; });
    if (!res.ok && !(data && data.error === 'Lab session required')) {
      return { ok: false, error: 'HTTP ' + res.status };
    }
    if (data && data.error === 'Lab session required' && typeof labEnsureSession === 'function') {
      S.labToken = null;
      await labEnsureSession();
      headers = {};
      if (S.labToken) headers['X-Lab-Token'] = S.labToken;
      var retry = await fetch(path, { headers: headers });
      if (!retry.ok) {
        return { ok: false, error: 'HTTP ' + retry.status };
      }
      return await retry.json();
    }
    return data;
  }

  async function _labPost(path, payload) {
    var result = await postJ(path, payload);
    if (result && result.error === 'Lab session required' && typeof labEnsureSession === 'function') {
      S.labToken = null;
      await labEnsureSession();
      result = await postJ(path, payload);
    }
    return result;
  }

  function _setStatus(message, type) {
    var el = document.getElementById('lab-status');
    if (!el) return;
    el.textContent = message;
    el.className = 'lab-status lab-status-' + (type || 'info');
  }

  async function _loadCapabilities() {
    try {
      var data = await _labGet('/api/lab/capabilities');
      if (data && data.ok) {
        _capabilities = data;
        _setStatus(_text('Lab portal ready', 'Lab 포털 준비됨'), 'ok');
        return true;
      }
      _setStatus((data && data.error) || _text('Lab portal unavailable', 'Lab 포털을 사용할 수 없습니다'), 'err');
      return false;
    } catch (err) {
      _setStatus(_text('Lab portal unavailable', 'Lab 포털을 사용할 수 없습니다'), 'err');
      return false;
    }
  }


  function _clear(node) {
    if (node) node.textContent = '';
  }

  function _appendText(parent, tag, className, text) {
    var el = document.createElement(tag);
    if (className) el.className = className;
    el.textContent = text;
    parent.appendChild(el);
    return el;
  }

  function _field(parent, id, label, type) {
    var wrap = document.createElement('div');
    wrap.className = 'fg';
    var lab = document.createElement('label');
    lab.setAttribute('for', id);
    lab.textContent = label;
    var input = document.createElement(type === 'select' ? 'select' : 'input');
    input.id = id;
    if (type && type !== 'select') input.type = type;
    wrap.appendChild(lab);
    wrap.appendChild(input);
    parent.appendChild(wrap);
    return input;
  }

  function _addSelectOption(sel, value, label) {
    var opt = document.createElement('option');
    opt.value = value;
    opt.textContent = label;
    sel.appendChild(opt);
  }


  function canApplyManifest(manifest) {
    return !!manifest && manifest.status === 'ready' && !(manifest.blockers || []).length;
  }

  function _collectConfirmations() {
    var result = {};
    var inputs = document.querySelectorAll('[data-confirmation-key]');
    inputs.forEach(function (inp) {
      result[inp.getAttribute('data-confirmation-key')] = inp.value;
    });
    return result;
  }


  function _describeManifestItem(item) {
    if (!item) return '';
    if (typeof item === 'string') return item;
    return item.message || item.error || item.code || item.path || String(item);
  }

  function _renderManifestSection(root, title, items) {
    if (!items || !items.length) return;
    _appendText(root, 'h4', 'manifest-section-title', _text(title));
    var ul = document.createElement('ul');
    ul.className = 'manifest-' + title.toLowerCase();
    items.forEach(function (item) {
      var li = document.createElement('li');
      li.textContent = _describeManifestItem(item);
      ul.appendChild(li);
    });
    root.appendChild(ul);
  }

  /* The server's summary is English; build the line from the inputs so it reads in the chosen language. */
  function _manifestSummary(m) {
    var i = (m && m.inputs) || {};
    if (m && m.kind === 'add_model' && i.model_name) {
      var cat = (typeof catText === 'function') ? catText(i.category) : i.category;
      return _text('Add {name} to {category}').replace('{name}', i.model_name).replace('{category}', cat) +
        (i.base_model ? ' · ' + _text('Copied from') + ' ' + i.base_model : '');
    }
    if (m && m.kind === 'task_scaffold' && i.task_name) {
      return _text('Create the {name} task skeleton').replace('{name}', i.task_name);
    }
    return (m && (m.summary || m.id)) || '';
  }

  function renderManifestPreview(manifest, onApply, applyButtonClass) {
    var root = document.getElementById('lab-flow-root');
    if (!root) return;
    _clear(root);
    _currentManifest = manifest;

    var applyCb = onApply || function () { applyAddModelManifest(); };
    var btnClass = applyButtonClass || 'btn-apply';

    _appendText(root, 'h3', 'manifest-title',
      (manifest && _manifestSummary(manifest)) || _text('Change preview', '변경 미리보기'));

    if (manifest && manifest.operations) {
      var list = document.createElement('ul');
      list.className = 'manifest-ops';
      manifest.operations.forEach(function (op) {
        var li = document.createElement('li');
        var act = { create: 'New', modify: 'Overwrite', delete: 'Delete' }[op.action];
        li.textContent = '[' + (act ? _text(act) : (op.action || '?')) + '] ' + (op.path || '');
        list.appendChild(li);
      });
      root.appendChild(list);
    }

    if (manifest && manifest.confirmations) {
      var cDiv = document.createElement('div');
      cDiv.className = 'manifest-confirmations';
      manifest.confirmations.forEach(function (c) {
        var wrap = document.createElement('div');
        wrap.className = 'fg';
        var lab = document.createElement('label');
        lab.textContent = (c.label || '') + (c.expected ? ' (' + c.expected + ')' : '');
        var inp = document.createElement('input');
        inp.type = 'text';
        inp.setAttribute('data-confirmation-key', c.key || '');
        wrap.appendChild(lab);
        wrap.appendChild(inp);
        cDiv.appendChild(wrap);
      });
      root.appendChild(cDiv);
    }

    if (manifest && manifest.blockers) {
      _renderManifestSection(root, 'Blockers', manifest.blockers);
    }
    if (manifest && manifest.warnings) {
      _renderManifestSection(root, 'Warnings', manifest.warnings);
    }

    var applyBtn = document.createElement('button');
    applyBtn.className = 'btn ' + btnClass;
    applyBtn.textContent = _text('Apply changes', '변경 적용');
    applyBtn.disabled = !canApplyManifest(manifest);
    applyBtn.addEventListener('click', applyCb);
    root.appendChild(applyBtn);
  }


  function _syncAddModelButtons() {
    var dryBtn = document.querySelector('.btn-dry-run');
    var applyBtn = document.querySelector('.btn-apply');
    var busy = _dryRunInFlight || _applyInFlight;
    if (dryBtn) dryBtn.disabled = busy;
    if (applyBtn) applyBtn.disabled = busy || !canApplyManifest(_currentManifest);
  }


  async function runAddModelDryRun() {
    if (_dryRunInFlight) return;
    _dryRunInFlight = true;
    _syncAddModelButtons();
    var modelName = document.getElementById('wiz-model-name');
    var category = document.getElementById('wiz-category');
    var lang = document.getElementById('wiz-lang');
    var sourcePath = document.getElementById('wiz-source-path');
    var baseModel = document.getElementById('wiz-base-model');
    var payload = {
      model_name: modelName ? modelName.value.trim() : '',
      category: category ? category.value : '',
      task_type: category ? category.value : '',
      lang: lang ? lang.value : 'both',
      source_path: sourcePath ? sourcePath.value.trim() : '',
      base_model: baseModel ? baseModel.value : ''
    };
    _addModelSource = payload.source_path;
    try {
      var result = await _labPost('/api/lab/add_model/dry_run', payload);
      if (result && result.error_code === 'manifest_expired') {
        _currentManifest = null;
        _setStatus(_text('Session expired — please restart the wizard.', '세션이 만료되었습니다. 마법사를 다시 시작하세요.'), 'err');
        renderAddModelWizard();
        return;
      }
      var manifest = result && (result.manifest || result);
      if (manifest && manifest.kind === 'add_model') {
        renderManifestPreview(manifest);
      } else {
        _setStatus(_text('Dry run failed', '드라이 런 실패') + (result && result.error ? ' — ' + result.error : ''), 'err');
      }
    } catch (err) {
      _setStatus(_text('Dry run error', '드라이 런 오류'), 'err');
    } finally {
      _dryRunInFlight = false;
      _syncAddModelButtons();
    }
  }

  async function applyAddModelManifest() {
    if (!canApplyManifest(_currentManifest)) return;
    if (_applyInFlight) return;
    _applyInFlight = true;
    _syncAddModelButtons();
    try {
      var result = await _labPost('/api/lab/add_model/apply', {
        manifest_id: _currentManifest.id,
        confirmations: _collectConfirmations()
      });
      if (result && result.error_code === 'manifest_expired') {
        _currentManifest = null;
        _setStatus(_text('Session expired — please restart the wizard.', '세션이 만료되었습니다. 마법사를 다시 시작하세요.'), 'err');
        renderAddModelWizard();
        return;
      }
      if (result && result.ok) {
        if (_currentManifest) _currentManifest.status = 'applied';
        _setStatus(_text('Apply completed', '적용 완료'), 'ok');
        if (typeof loadModels === 'function') loadModels();
      } else {
        _setStatus(_text('Apply failed', '적용 실패') + (result && result.error ? ' — ' + result.error : ''), 'err');
      }
      _renderAddModelResult(result || {});
    } catch (err) {
      _setStatus(_text('Apply error', '적용 오류'), 'err');
    } finally {
      _applyInFlight = false;
      _syncAddModelButtons();
    }
  }

  /* What Apply did: the folders it created and how to run the Python copy — or the script's reason. */
  function _renderAddModelResult(result) {
    var root = document.getElementById('lab-flow-root');
    if (!root) return;
    var old = document.getElementById('lab-add-model-result');
    if (old) old.remove();
    var box = document.createElement('div');
    box.id = 'lab-add-model-result';
    box.className = 'lab-result' + (result.ok ? ' lab-result-ok' : ' lab-result-err');
    if (result.ok) {
      _appendText(box, 'h4', 'lab-result-title', _text('Created'));
      var ul = document.createElement('ul');
      ul.className = 'lab-result-paths';
      (result.created || []).forEach(function (rel) { _appendText(ul, 'li', '', 'dx_app/' + rel); });
      box.appendChild(ul);
      if (result.reference) {
        _appendText(box, 'p', 'txt-dim txt-sm', _text('Copied from') + ': ' + result.reference);
      }
      var py = (result.created || []).filter(function (rel) { return rel.indexOf('src/python_example/') === 0; })[0];
      if (py) {
        var name = py.split('/').pop();
        _appendText(box, 'p', 'txt-sm', _text('Run the Python copy with your model:'));
        _appendText(box, 'pre', 'code lab-result-cmd',
          'cd dx_app/' + py + '\npython3 ' + name + '_sync.py --model ' + (_addModelSource || '<your-model>.dxnn') + ' --image <image>');
      }
      if ((result.created || []).some(function (rel) { return rel.indexOf('src/cpp_example/') === 0; })) {
        _appendText(box, 'p', 'txt-dim txt-sm', _text('Build the C++ copy with dx_app build.sh.'));
      }
    }
    if (result.output) {
      var det = document.createElement('details');
      _appendText(det, 'summary', '', _text('Script output'));
      _appendText(det, 'pre', 'code lab-result-log', result.output);
      box.appendChild(det);
    }
    root.appendChild(box);
  }


  var _addModelSource = '';

  function _langOptions(sel) {
    _addSelectOption(sel, 'both', _text('Both (C++ & Python)'));
    _addSelectOption(sel, 'cpp', _text('C++ only'));
    _addSelectOption(sel, 'python', _text('Python only'));
  }

  /* Add Model copies an existing example of the category and renames it (add_model.sh --base-model). Only the
     examples that have a factory in every chosen language can be copied, so the list follows category + language. */
  function _referenceChoices(category, lang) {
    var refs = (_capabilities && _capabilities.reference_examples && _capabilities.reference_examples[category]) || [];
    var need = lang === 'both' ? ['python', 'cpp'] : [lang];
    return refs.filter(function (r) { return need.every(function (l) { return (r.langs || []).indexOf(l) !== -1; }); });
  }

  function _fillReferenceSelect() {
    var sel = document.getElementById('wiz-base-model');
    var cat = document.getElementById('wiz-category');
    var lang = document.getElementById('wiz-lang');
    if (!sel || !cat || !lang) return;
    _clear(sel);
    var refs = _referenceChoices(cat.value, lang.value);
    refs.forEach(function (r) { _addSelectOption(sel, r.name, r.family ? r.name + ' · ' + r.family : r.name); });
    if (!refs.length) _addSelectOption(sel, '', _text('No example to copy for this language'));
    sel.disabled = !refs.length;
    var dry = document.querySelector('.btn-dry-run');
    if (dry) dry.disabled = !refs.length || _dryRunInFlight || _applyInFlight;
  }

  function renderAddModelWizard() {
    var root = document.getElementById('lab-flow-root');
    if (!root) return;
    _clear(root);

    _appendText(root, 'h2', 'wizard-title', _text('Add Model Wizard', '모델 추가 마법사'));
    _appendText(root, 'p', 'txt-dim txt-sm',
      _text('Add Model copies an existing example and renames it. Run the copy with your own .dxnn.'));

    var form = document.createElement('div');
    form.className = 'wizard-form';

    var nameInput = _field(form, 'wiz-model-name', _text('Model Name', '모델 이름'), 'text');
    nameInput.placeholder = 'my_detector';
    nameInput.autocomplete = 'off';

    var catSel = _field(form, 'wiz-category', _text('Category', '카테고리'), 'select');
    var refs = (_capabilities && _capabilities.reference_examples) || {};
    if (_capabilities && _capabilities.task_categories) {
      _capabilities.task_categories.forEach(function (cat) {
        var catId = (typeof cat === 'string') ? cat : cat.id;
        if (!catId || !(refs[catId] || []).length) return;
        var label = (typeof catText === 'function') ? catText(catId) : ((cat && cat.label) || catId);
        _addSelectOption(catSel, catId, label);
      });
    }

    var langSel = _field(form, 'wiz-lang', _text('Language', '언어'), 'select');
    _langOptions(langSel);

    _field(form, 'wiz-base-model', _text('Start from'), 'select');

    var src = _field(form, 'wiz-source-path', _text('Your model (.dxnn, optional)'), 'text');
    src.placeholder = 'outputs/my_model.dxnn';
    src.setAttribute('list', 'wiz-dxnn-list');
    var list = document.createElement('datalist');
    list.id = 'wiz-dxnn-list';
    ((_capabilities && _capabilities.experiment_models) || []).forEach(function (m) {
      var opt = document.createElement('option');
      opt.value = m.path;
      opt.label = m.name;
      list.appendChild(opt);
    });
    form.appendChild(list);

    root.appendChild(form);

    var dryBtn = document.createElement('button');
    dryBtn.className = 'btn btn-dry-run';
    dryBtn.textContent = _text('Dry Run', '드라이 런');
    dryBtn.addEventListener('click', function () { runAddModelDryRun(); });
    root.appendChild(dryBtn);

    catSel.addEventListener('change', _fillReferenceSelect);
    langSel.addEventListener('change', _fillReferenceSelect);
    _fillReferenceSelect();
  }


  function _syncTaskButtons() {
    var dryBtn = document.querySelector('.btn-task-dry-run');
    var applyBtn = document.querySelector('.btn-task-apply');
    var busy = _dryRunInFlight || _applyInFlight;
    if (dryBtn) dryBtn.disabled = busy;
    if (applyBtn) applyBtn.disabled = busy || !canApplyManifest(_currentManifest);
  }


  function renderGeneratedFiles(files) {
    var root = document.getElementById('lab-generated-preview');
    if (!root) return;
    _clear(root);
    _appendText(root, 'h4', 'generated-title', _text('Generated Files', '생성된 파일'));
    if (!files || !files.length) {
      _appendText(root, 'p', 'generated-empty', _text('Preview unavailable', '미리보기 없음'));
      return;
    }
    var ul = document.createElement('ul');
    ul.className = 'generated-files';
    files.forEach(function (f) {
      var li = document.createElement('li');
      li.className = 'generated-file';
      var pathSpan = document.createElement('span');
      pathSpan.className = 'generated-path';
      pathSpan.textContent = f.path || '';
      li.appendChild(pathSpan);
      if (f.size != null) {
        var sizeSpan = document.createElement('span');
        sizeSpan.className = 'generated-size';
        sizeSpan.textContent = ' (' + f.size + ' bytes)';
        li.appendChild(sizeSpan);
      }
      if (f.preview) {
        var pre = document.createElement('pre');
        pre.className = 'generated-preview';
        pre.textContent = f.preview;
        li.appendChild(pre);
      }
      ul.appendChild(li);
    });
    root.appendChild(ul);
  }

  async function _loadGeneratedFiles(manifest_id) {
    try {
      var data = await _labGet('/api/lab/generated/' + encodeURIComponent(manifest_id));
      if (data && data.files) {
        renderGeneratedFiles(data.files);
      } else {
        renderGeneratedFiles(null);
      }
    } catch (err) {
      renderGeneratedFiles(null);
    }
  }


  async function runTaskDryRun() {
    if (_dryRunInFlight) return;
    _dryRunInFlight = true;
    _syncTaskButtons();
    var taskName = document.getElementById('wiz-task-name');
    var lang = document.getElementById('wiz-task-lang');
    var scaffoldType = document.getElementById('wiz-scaffold-type');
    var payload = {
      task_name: taskName ? taskName.value : '',
      lang: lang ? lang.value : 'both',
      scaffold_type: scaffoldType ? scaffoldType.value : 'full'
    };
    try {
      var result = await _labPost('/api/lab/task/dry_run', payload);
      if (result && result.error_code === 'manifest_expired') {
        _currentManifest = null;
        _setStatus(_text('Session expired — please restart the wizard.', '세션이 만료되었습니다. 마법사를 다시 시작하세요.'), 'err');
        renderTaskWizard();
        return;
      }
      var manifest = result && (result.manifest || result);
      if (manifest && manifest.kind === 'task_scaffold') {
        _currentManifest = manifest;
        renderManifestPreview(manifest, applyTaskManifest, 'btn-task-apply');

        // Container for the generated file list
        var root = document.getElementById('lab-flow-root');
        if (root) {
          var genDiv = document.createElement('div');
          genDiv.id = 'lab-generated-preview';
          root.appendChild(genDiv);
        }
        if (manifest.id) {
          _loadGeneratedFiles(manifest.id);
        }
      } else {
        _setStatus(_text('Task dry run failed', '태스크 드라이 런 실패'), 'err');
      }
    } catch (err) {
      _setStatus(_text('Task dry run error', '태스크 드라이 런 오류'), 'err');
    } finally {
      _dryRunInFlight = false;
      _syncTaskButtons();
    }
  }

  async function applyTaskManifest() {
    if (!canApplyManifest(_currentManifest)) return;
    if (_applyInFlight) return;
    _applyInFlight = true;
    _syncTaskButtons();
    try {
      var result = await _labPost('/api/lab/task/apply', {
        manifest_id: _currentManifest.id,
        confirmations: _collectConfirmations()
      });
      if (result && result.error_code === 'manifest_expired') {
        _currentManifest = null;
        _setStatus(_text('Session expired — please restart the wizard.', '세션이 만료되었습니다. 마법사를 다시 시작하세요.'), 'err');
        renderTaskWizard();
        return;
      }
      if (result && result.ok) {
        if (_currentManifest) _currentManifest.status = 'applied';
        _setStatus(_text('Apply completed', '적용 완료'), 'ok');
      } else {
        _setStatus(_text('Task apply failed', '태스크 적용 실패'), 'err');
      }
    } catch (err) {
      _setStatus(_text('Task apply error', '태스크 적용 오류'), 'err');
    } finally {
      _applyInFlight = false;
      _syncTaskButtons();
    }
  }


  function renderTaskWizard() {
    var root = document.getElementById('lab-flow-root');
    if (!root) return;
    _clear(root);

    _appendText(root, 'h2', 'wizard-title', _text('Create Task Wizard', '태스크 생성 마법사'));

    var form = document.createElement('div');
    form.className = 'wizard-form';

    _field(form, 'wiz-task-name', _text('Task Name', '태스크 이름'), 'text');

    var langSel = _field(form, 'wiz-task-lang', _text('Language', '언어'), 'select');
    _langOptions(langSel);

    var scaffoldSel = _field(form, 'wiz-scaffold-type', _text('Scaffold Type', '스캐폴드 유형'), 'select');
    _addSelectOption(scaffoldSel, 'full', _text('Full scaffold', '전체 스캐폴드'));
    _addSelectOption(scaffoldSel, 'postprocessor', _text('Postprocessor only', '후처리기만'));

    root.appendChild(form);

    var dryBtn = document.createElement('button');
    dryBtn.className = 'btn btn-task-dry-run';
    dryBtn.textContent = _text('Dry Run', '드라이 런');
    dryBtn.addEventListener('click', function () { runTaskDryRun(); });
    root.appendChild(dryBtn);
  }


  var _currentExperimentRun = null;
  var _experimentInFlight = false;

  function _syncExperimentButtons() {
    var startBtn = document.querySelector('.btn-experiment-start');
    var cancelBtn = document.querySelector('.btn-experiment-cancel');
    var refreshBtn = document.querySelector('.btn-experiment-refresh');
    var terminalStatuses = ['cancelled', 'failed', 'completed'];
    var isTerminal = _currentExperimentRun &&
      terminalStatuses.indexOf(_currentExperimentRun.status) !== -1;
    if (startBtn) startBtn.disabled = _experimentInFlight;
    if (cancelBtn) cancelBtn.disabled = _experimentInFlight || !_currentExperimentRun || isTerminal;
    if (refreshBtn) refreshBtn.disabled = _experimentInFlight || !_currentExperimentRun;
  }

  function renderExperimentLogs(log_tail) {
    var container = document.getElementById('exp-log-block');
    if (!container) return;
    _clear(container);
    _appendText(container, 'h4', 'exp-log-title', _text('Pipeline Logs', '파이프라인 로그'));
    var pre = document.createElement('pre');
    pre.className = 'exp-log-content';
    pre.textContent = Array.isArray(log_tail) ? log_tail.join('\n') : (log_tail || '');
    container.appendChild(pre);
    pre.scrollTop = pre.scrollHeight;
  }

  var _EXPERIMENT_STEP_LABELS = {
    inspect: 'Read the model',
    smoke: 'One inference',
    benchmark: 'Benchmark'
  };
  var _EXPERIMENT_STATUS_LABELS = {
    pending: 'Starting…',
    running: 'Running…',
    completed: 'Completed',
    failed: 'Failed',
    cancelled: 'Cancelled'
  };
  var _experimentPoll = null;

  function _stopExperimentPoll() {
    if (_experimentPoll) { clearTimeout(_experimentPoll); _experimentPoll = null; }
  }

  /* The run advances in a worker on the server; poll it until it ends. */
  function _pollExperiment(runId) {
    _stopExperimentPoll();
    _experimentPoll = setTimeout(async function () {
      _experimentPoll = null;
      if (!_currentExperimentRun || _currentExperimentRun.id !== runId) return;
      var data = await _labGet('/api/lab/experiment/' + encodeURIComponent(runId)).catch(function () { return null; });
      if (!data || !data.id || !_currentExperimentRun || _currentExperimentRun.id !== runId) return;
      _currentExperimentRun = data;
      renderExperimentRun(data);
      _syncExperimentButtons();
    }, 800);
  }

  function renderExperimentRun(run) {
    var root = document.getElementById('exp-run-display');
    if (!root) return;
    _clear(root);
    if (!run) return;

    _appendText(root, 'h4', 'exp-run-status-title', _text('Run Status', '실행 상태'));
    var statusEl = document.createElement('div');
    statusEl.className = 'exp-run-status exp-run-' + (run.status || 'unknown');
    statusEl.textContent = _text(_EXPERIMENT_STATUS_LABELS[run.status] || run.status || 'unknown');
    root.appendChild(statusEl);

    if (run.steps && run.steps.length) {
      var stepperUl = document.createElement('ol');
      stepperUl.className = 'exp-stepper';
      run.steps.forEach(function (step) {
        var li = document.createElement('li');
        li.className = 'exp-step exp-step-' + (step.status || 'pending');
        if (step.id === run.current_step && run.status === 'running') li.className += ' exp-step-active';
        li.textContent = _text(_EXPERIMENT_STEP_LABELS[step.id] || step.id);
        stepperUl.appendChild(li);
      });
      root.appendChild(stepperUl);
    }

    if (run.result && run.result.fps != null) {
      var fps = document.createElement('div');
      fps.className = 'exp-result';
      fps.textContent = _text('Throughput') + ': ' + Number(run.result.fps).toFixed(1) + ' FPS';
      root.appendChild(fps);
    }
    (run.blockers || []).forEach(function (b) {
      _appendText(root, 'p', 'exp-blocker', b.message || b.code || '');
    });

    var logBlock = document.createElement('div');
    logBlock.id = 'exp-log-block';
    root.appendChild(logBlock);
    if (run.log_tail != null) {
      renderExperimentLogs(run.log_tail);
    }
    if (run.status === 'pending' || run.status === 'running') _pollExperiment(run.id);
  }

  function renderExperimentPipeline() {
    var root = document.getElementById('lab-flow-root');
    if (!root) return;
    _clear(root);

    _appendText(root, 'h2', 'experiment-title', _text('Experiment Pipeline', '실험 파이프라인'));
    _appendText(root, 'p', 'txt-dim txt-sm',
      _text('Checks a compiled model on this board: reads the file, runs one inference, then measures throughput.'));

    var form = document.createElement('div');
    form.className = 'experiment-form';

    var pick = _field(form, 'exp-model-pick', _text('Compiled model'), 'select');
    var models = (_capabilities && _capabilities.experiment_models) || [];
    models.forEach(function (m) { _addSelectOption(pick, m.path, m.name); });
    _addSelectOption(pick, '', _text('Other path…'));
    var src = _field(form, 'exp-source-path', _text('Source Path', '소스 경로'), 'text');
    src.placeholder = 'outputs/my_model.dxnn';
    src.value = models.length ? models[0].path : '';
    pick.addEventListener('change', function () {
      src.value = pick.value;
      if (!pick.value) src.focus();
    });

    root.appendChild(form);

    var startBtn = document.createElement('button');
    startBtn.className = 'btn btn-acc btn-experiment-start';
    startBtn.textContent = _text('Start pipeline', '파이프라인 시작');
    startBtn.addEventListener('click', function () { startExperimentPipeline(); });
    root.appendChild(startBtn);

    var cancelBtn = document.createElement('button');
    cancelBtn.className = 'btn btn-experiment-cancel';
    cancelBtn.textContent = _text('Cancel run', '실행 중단');
    cancelBtn.disabled = !_currentExperimentRun;
    cancelBtn.addEventListener('click', function () { cancelExperimentRun(); });
    root.appendChild(cancelBtn);

    var refreshBtn = document.createElement('button');
    refreshBtn.className = 'btn btn-experiment-refresh';
    refreshBtn.textContent = _text('Refresh run', '실행 새로고침');
    refreshBtn.disabled = !_currentExperimentRun;
    refreshBtn.addEventListener('click', function () {
      if (_currentExperimentRun) refreshExperimentRun(_currentExperimentRun.id);
    });
    root.appendChild(refreshBtn);

    var runDisplay = document.createElement('div');
    runDisplay.id = 'exp-run-display';
    root.appendChild(runDisplay);

    if (_currentExperimentRun) {
      renderExperimentRun(_currentExperimentRun);
    }
    _syncExperimentButtons();
  }

  async function startExperimentPipeline() {
    if (_experimentInFlight) return;
    _experimentInFlight = true;
    _syncExperimentButtons();
    var sourceInput = document.getElementById('exp-source-path');
    var pick = document.getElementById('exp-model-pick');
    var source = sourceInput ? sourceInput.value.trim() : '';
    var payload = {
      model_name: source.split('/').pop().replace(/\.dxnn$/, ''),
      source_path: source
    };
    try {
      var result = await _labPost('/api/lab/experiment/start', payload);
      if (result && result.id) {
        _currentExperimentRun = result;
        _setStatus(_text('Pipeline started'), 'ok');
        renderExperimentRun(result);
      } else {
        _setStatus(_text('Pipeline start failed', '파이프라인 시작 실패') + (result && result.error ? ' — ' + result.error : ''), 'err');
      }
    } catch (err) {
      _setStatus(_text('Pipeline start error', '파이프라인 시작 오류'), 'err');
    } finally {
      _experimentInFlight = false;
      _syncExperimentButtons();
    }
  }

  async function refreshExperimentRun(run_id) {
    if (_experimentInFlight) return;
    _experimentInFlight = true;
    _syncExperimentButtons();
    try {
      var data = await _labGet('/api/lab/experiment/' + encodeURIComponent(run_id));
      if (data && data.id) {
        _currentExperimentRun = data;
        renderExperimentRun(data);
      } else {
        _setStatus(_text('Pipeline refresh failed', '파이프라인 새로고침 실패'), 'err');
      }
    } catch (err) {
      _setStatus(_text('Pipeline refresh failed', '파이프라인 새로고침 실패'), 'err');
    } finally {
      _experimentInFlight = false;
      _syncExperimentButtons();
    }
  }

  async function cancelExperimentRun() {
    if (!_currentExperimentRun) return;
    if (_experimentInFlight) return;
    _experimentInFlight = true;
    _syncExperimentButtons();
    try {
      var result = await _labPost('/api/lab/experiment/' + encodeURIComponent(_currentExperimentRun.id) + '/cancel', {});
      if (result && result.id) {
        _currentExperimentRun = result;
        renderExperimentRun(result);
      } else {
        _setStatus(_text('Pipeline cancel failed', '파이프라인 취소 실패'), 'err');
      }
    } catch (err) {
      _setStatus(_text('Pipeline cancel error', '파이프라인 취소 오류'), 'err');
    } finally {
      _experimentInFlight = false;
      _syncExperimentButtons();
    }
  }


  /* Generated Files — shows the generated files of each manifest Lab made
     (/api/lab/manifests, /api/lab/generated/<id>). */
  var _MANIFEST_STATUS_LABELS = { ready: 'Preview', applied: 'Applied', rolled_back: 'Rolled back' };

  function _manifestLine(m) {
    var li = document.createElement('li');
    li.className = 'safety-manifest-item';
    var badge = document.createElement('span');
    badge.className = 'lab-badge lab-badge-' + (m.status || 'ready');
    badge.textContent = _text(_MANIFEST_STATUS_LABELS[m.status] || m.status || '');
    li.appendChild(badge);
    _appendText(li, 'span', 'safety-manifest-summary', ' ' + _manifestSummary(m));
    return li;
  }

  async function renderGeneratedFlow() {
    var root = document.getElementById('lab-flow-root');
    if (!root) return;
    _clear(root);
    _appendText(root, 'h2', 'generated-flow-title', _text('Generated Files', '생성된 파일'));
    var listDiv = document.createElement('div');
    listDiv.className = 'safety-manifests';
    root.appendChild(listDiv);
    var preview = document.createElement('div');
    preview.id = 'lab-generated-preview';
    try {
      var data = await _labGet('/api/lab/manifests');
      var list = ((data && data.manifests) || []).filter(function (m) { return m.status !== 'rolled_back'; });
      if (!list.length) {
        _appendText(listDiv, 'p', 'safety-empty', _text('Nothing generated yet. Add a model or create a task first.', '아직 생성된 파일이 없습니다. 먼저 모델을 추가하거나 태스크를 만드세요.'));
      } else {
        var ul = document.createElement('ul');
        ul.className = 'safety-manifest-list';
        list.forEach(function (m) {
          var li = _manifestLine(m);
          var btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'btn btn-sm';
          btn.textContent = _text('Show files', '파일 보기');
          btn.addEventListener('click', function () { _loadGeneratedFiles(m.id); });
          li.appendChild(btn);
          ul.appendChild(li);
        });
        listDiv.appendChild(ul);
      }
    } catch (err) {
      _appendText(listDiv, 'p', 'safety-error', _text('Failed to load manifests', '매니페스트 로드 실패'));
    }
    root.appendChild(preview);
  }

  /* Safety Center — every Add Model / Create Task change of this session. An applied change that only created
     new files can be rolled back (those files are deleted after a typed confirmation); one that overwrote
     existing files has to be restored by hand. */
  async function renderSafetyCenter() {
    var root = document.getElementById('lab-flow-root');
    if (!root) return;
    _clear(root);

    _appendText(root, 'h2', 'safety-title', _text('Safety Center', '안전 센터'));

    var listDiv = document.createElement('div');
    listDiv.className = 'safety-manifests';
    _appendText(listDiv, 'h3', 'safety-manifests-title', _text('Lab changes'));
    root.appendChild(listDiv);

    try {
      var data = await _labGet('/api/lab/manifests');
      // Rollback and the git plan are about changes that were applied; previews live in Generated Files.
      var changes = ((data && data.manifests) || []).filter(function (m) { return m.status !== 'ready'; });
      if (changes.length) {
        var ul = document.createElement('ul');
        ul.className = 'safety-manifest-list';
        changes.forEach(function (m) {
          var li = _manifestLine(m);
          ul.appendChild(li);

          if (m.change_summary && Object.keys(m.change_summary).length) {
            var summaryDiv = document.createElement('div');
            summaryDiv.className = 'safety-change-summary';
            Object.keys(m.change_summary).forEach(function (r) {
              var sum = m.change_summary[r];
              var span = document.createElement('span');
              span.className = 'safety-root-summary';
              span.textContent = r + ': +' + sum.create + ' ~' + sum.modify + ' -' + sum.delete;
              summaryDiv.appendChild(span);
            });
            li.appendChild(summaryDiv);
          }

          var rb = m.rollback || {};
          if (m.status === 'applied' && rb.supported && rb.confirmation) {
            var conf = document.createElement('input');
            conf.type = 'text';
            conf.className = 'safety-rollback-confirm';
            conf.placeholder = rb.confirmation.expected;
            conf.setAttribute('aria-label', _text('Type to confirm') + ': ' + rb.confirmation.expected);
            li.appendChild(conf);
            var rollbackBtn = document.createElement('button');
            rollbackBtn.className = 'btn btn-red btn-safety-rollback';
            rollbackBtn.textContent = _text('Rollback', '롤백');
            rollbackBtn.disabled = true;
            conf.addEventListener('input', function () { rollbackBtn.disabled = conf.value !== rb.confirmation.expected; });
            rollbackBtn.addEventListener('click', function () { requestRollback(m.id, rb.confirmation, conf.value); });
            li.appendChild(rollbackBtn);
          } else if (m.status === 'applied') {
            _appendText(li, 'p', 'safety-manual txt-dim txt-sm',
              _text('This change overwrote existing files. Restore them by hand.'));
          }

          if (m.status === 'applied') {
            var gitBtn = document.createElement('button');
            gitBtn.className = 'btn btn-safety-git-plan';
            gitBtn.textContent = _text('Commit with git');
            gitBtn.addEventListener('click', function () { requestScopedGitPlan(m.id); });
            li.appendChild(gitBtn);
          }
        });
        listDiv.appendChild(ul);
      } else {
        _appendText(listDiv, 'p', 'safety-empty', _text('No Lab changes yet'));
      }
    } catch (err) {
      _appendText(listDiv, 'p', 'safety-error', _text('Failed to load manifests', '매니페스트 로드 실패'));
    }

    var outputDiv = document.createElement('div');
    outputDiv.id = 'safety-output';
    root.appendChild(outputDiv);
  }

  async function requestRollback(manifestId, confirmation, typed) {
    var output = document.getElementById('safety-output');
    if (!output) return;
    _clear(output);
    var confirmations = {};
    if (confirmation && confirmation.key) confirmations[confirmation.key] = typed || '';
    try {
      var result = await _labPost('/api/lab/rollback', { manifest_id: manifestId, confirmations: confirmations });
      if (result && result.error_code === 'rollback_unsupported') {
        _appendText(output, 'p', 'safety-manual', _text('This change overwrote existing files. Restore them by hand.'));
      } else if (result && result.ok) {
        _appendText(output, 'p', 'safety-ok', _text('Rolled back') + ' — ' + (result.removed || []).join(', '));
        if (typeof loadModels === 'function') loadModels();
        renderSafetyCenter().then(function () {
          var out = document.getElementById('safety-output');
          if (out) _appendText(out, 'p', 'safety-ok', _text('Rolled back') + ' — ' + (result.removed || []).join(', '));
        });
      } else {
        _appendText(output, 'p', 'safety-error', (result && result.error) || _text('Rollback failed', '롤백 실패'));
      }
    } catch (err) {
      _appendText(output, 'p', 'safety-error', _text('Rollback error', '롤백 오류'));
    }
  }

  async function requestScopedGitPlan(manifestId) {
    var output = document.getElementById('safety-output');
    if (!output) return;
    _clear(output);
    try {
      var result = await _labPost('/api/lab/git/plan', { manifest_id: manifestId });
      if (result && result.files) {
        // Studio never runs git in the user's dx_app; it hands over a command that stages only the files this change wrote.
        _appendText(output, 'h4', 'safety-git-title', _text('Files this change wrote'));
        var ul = document.createElement('ul');
        ul.className = 'safety-git-files';
        result.files.forEach(function (f) {
          var li = document.createElement('li');
          li.textContent = f;
          ul.appendChild(li);
        });
        output.appendChild(ul);
        if (result.commands && result.commands.length) {
          _appendText(output, 'p', 'safety-git-note txt-dim txt-sm',
            _text('Studio does not run git for you. Run these in a terminal to commit only these files:'));
          _appendText(output, 'pre', 'safety-git-cmds', result.commands.join('\n'));
        }
      } else {
        _appendText(output, 'p', 'safety-error', (result && result.error) || _text('Git plan failed'));
      }
    } catch (err) {
      _appendText(output, 'p', 'safety-error', _text('Git plan failed'));
    }
  }


  function _bindCards() {
    if (_cardsBound) return;
    _cardsBound = true;
    document.querySelectorAll('[data-lab-flow]').forEach(function (card) {
      card.addEventListener('click', function () {
        var flow = card.getAttribute('data-lab-flow');
        if (flow === 'add-model') {
          renderAddModelWizard();
          return;
        }
        if (flow === 'create-task') {
          renderTaskWizard();
          return;
        }
        if (flow === 'experiment') {
          renderExperimentPipeline();
          return;
        }
        if (flow === 'safety') {
          renderSafetyCenter();
          return;
        }
        if (flow === 'generated') {
          renderGeneratedFlow();
          return;
        }
        if (flow === 'composer') {
          if (window.LabComposer && typeof window.LabComposer.open === 'function') {
            window.LabComposer.open();
          } else {
            var composerRoot = document.getElementById('lab-flow-root');
            if (composerRoot) composerRoot.textContent = _text('Composer module unavailable', 'Composer 모듈을 사용할 수 없습니다.');
          }
          return;
        }
        var root = document.getElementById('lab-flow-root');
        if (root) root.textContent = _text('This flow is planned for the next phase.', '이 흐름은 다음 단계에서 구현됩니다.');
      });
    });
  }

  async function _openComposerByDefault() {
    if (_composerOpened || !window.LabComposer || typeof window.LabComposer.open !== 'function') return;
    await window.LabComposer.open();
    _composerOpened = true;
  }

  async function init() {
    if (_ready) {
      await _openComposerByDefault();
      return;
    }
    _bindCards();
    if (!S.labToken && typeof labEnsureSession === 'function') await labEnsureSession();
    var ok = await _loadCapabilities();
    _ready = !!ok;
    if (_ready) await _openComposerByDefault();
  }

  return {
    init: init,
    canApplyManifest: canApplyManifest,
    request: _labPost,
    get: _labGet,
    capabilities: function () { return _capabilities; }
  };
})();
if (typeof registerLangRefresher === 'function') {
  registerLangRefresher(function refreshLabPortalLanguage() {
    if (document.querySelector('#page-lab.active') && typeof initLabPage === 'function') initLabPage();
  });
}
