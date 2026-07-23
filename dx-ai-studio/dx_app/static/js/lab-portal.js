window.LabPortal = (function () {
  'use strict';
  var _ready = false;
  var _cardsBound = false;
  var _capabilities = null;
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

  function renderManifestPreview(manifest, onApply, applyButtonClass) {
    var root = document.getElementById('lab-flow-root');
    if (!root) return;
    _clear(root);
    _currentManifest = manifest;

    var applyCb = onApply || function () { applyAddModelManifest(); };
    var btnClass = applyButtonClass || 'btn-apply';

    _appendText(root, 'h3', 'manifest-title',
      (manifest && manifest.summary) || _text('Change preview', '변경 미리보기'));

    if (manifest && manifest.operations) {
      var list = document.createElement('ul');
      list.className = 'manifest-ops';
      manifest.operations.forEach(function (op) {
        var li = document.createElement('li');
        li.textContent = '[' + (op.action || 'unknown') + '] ' + (op.path || '');
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
    var postprocessor = document.getElementById('wiz-postprocessor');
    var payload = {
      model_name: modelName ? modelName.value : '',
      category: category ? category.value : '',
      task_type: category ? category.value : '',
      lang: lang ? lang.value : 'cpp',
      source_path: sourcePath ? sourcePath.value : '',
      postprocessor: postprocessor ? postprocessor.value : ''
    };
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
        _setStatus(_text('Dry run failed', '드라이 런 실패'), 'err');
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
      } else {
        _setStatus(_text('Apply failed', '적용 실패'), 'err');
      }
    } catch (err) {
      _setStatus(_text('Apply error', '적용 오류'), 'err');
    } finally {
      _applyInFlight = false;
      _syncAddModelButtons();
    }
  }


  function renderAddModelWizard() {
    var root = document.getElementById('lab-flow-root');
    if (!root) return;
    _clear(root);

    _appendText(root, 'h2', 'wizard-title', _text('Add Model Wizard', '모델 추가 마법사'));

    var form = document.createElement('div');
    form.className = 'wizard-form';

    _field(form, 'wiz-model-name', _text('Model Name', '모델 이름'), 'text');

    var catSel = _field(form, 'wiz-category', _text('Category', '카테고리'), 'select');
    if (_capabilities && _capabilities.task_categories) {
      _capabilities.task_categories.forEach(function (cat) {
        var catId = (typeof cat === 'string') ? cat : cat.id;
        var catLabel = (typeof cat === 'string') ? cat : (cat.label || cat.id);
        if (catId) _addSelectOption(catSel, catId, catLabel || catId);
      });
    }

    var langSel = _field(form, 'wiz-lang', _text('Language', '언어'), 'select');
    _addSelectOption(langSel, 'both', 'both');
    _addSelectOption(langSel, 'cpp', 'cpp');
    _addSelectOption(langSel, 'python', 'python');

    _field(form, 'wiz-source-path', _text('Source Path', '소스 경로'), 'text');

    var ppSel = _field(form, 'wiz-postprocessor', _text('Postprocessor', '후처리기'), 'select');
    if (_capabilities && _capabilities.postprocessors) {
      var cats = Object.keys(_capabilities.postprocessors);
      cats.forEach(function (cat) {
        var pps = _capabilities.postprocessors[cat];
        if (Array.isArray(pps)) {
          pps.forEach(function (pp) { _addSelectOption(ppSel, pp, pp); });
        }
      });
    }

    root.appendChild(form);

    var dryBtn = document.createElement('button');
    dryBtn.className = 'btn btn-dry-run';
    dryBtn.textContent = _text('Dry Run', '드라이 런');
    dryBtn.addEventListener('click', function () { runAddModelDryRun(); });
    root.appendChild(dryBtn);
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

        // 생성된 파일 목록용 컨테이너
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
    _addSelectOption(langSel, 'both', 'both');
    _addSelectOption(langSel, 'cpp', 'cpp');
    _addSelectOption(langSel, 'python', 'python');

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
  }

  function renderExperimentRun(run) {
    var root = document.getElementById('exp-run-display');
    if (!root) return;
    _clear(root);
    if (!run) return;

    _appendText(root, 'h4', 'exp-run-status-title', _text('Run Status', '실행 상태'));
    var statusEl = document.createElement('div');
    statusEl.className = 'exp-run-status';
    statusEl.textContent = (run.status || 'unknown');
    root.appendChild(statusEl);

    _appendText(root, 'h4', 'exp-current-step-title', _text('Current Step', '현재 단계'));
    var stepEl = document.createElement('div');
    stepEl.className = 'exp-current-step';
    stepEl.textContent = run.current_step || '';
    root.appendChild(stepEl);

    if (run.steps && run.steps.length) {
      var stepperUl = document.createElement('ul');
      stepperUl.className = 'exp-stepper';
      run.steps.forEach(function (step) {
        var li = document.createElement('li');
        li.className = 'exp-step';
        if (step.id === run.current_step) li.className += ' exp-step-active';
        li.textContent = step.id;
        stepperUl.appendChild(li);
      });
      root.appendChild(stepperUl);
    }

    var logBlock = document.createElement('div');
    logBlock.id = 'exp-log-block';
    root.appendChild(logBlock);
    if (run.log_tail != null) {
      renderExperimentLogs(run.log_tail);
    }
  }

  function renderExperimentPipeline() {
    var root = document.getElementById('lab-flow-root');
    if (!root) return;
    _clear(root);

    _appendText(root, 'h2', 'experiment-title', _text('Experiment Pipeline', '실험 파이프라인'));

    var form = document.createElement('div');
    form.className = 'experiment-form';

    _field(form, 'exp-model-name', _text('Model Name', '모델 이름'), 'text');
    _field(form, 'exp-source-path', _text('Source Path', '소스 경로'), 'text');

    root.appendChild(form);

    var startBtn = document.createElement('button');
    startBtn.className = 'btn btn-experiment-start';
    startBtn.textContent = _text('Start pipeline', '파이프라인 시작');
    startBtn.addEventListener('click', function () { startExperimentPipeline(); });
    root.appendChild(startBtn);

    var cancelBtn = document.createElement('button');
    cancelBtn.className = 'btn btn-experiment-cancel';
    cancelBtn.textContent = _text('Cancel run', '실행 취소');
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
    var modelInput = document.getElementById('exp-model-name');
    var sourceInput = document.getElementById('exp-source-path');
    var payload = {
      model_name: modelInput ? modelInput.value : '',
      source_path: sourceInput ? sourceInput.value : ''
    };
    try {
      var result = await _labPost('/api/lab/experiment/start', payload);
      if (result && result.id) {
        _currentExperimentRun = result;
        renderExperimentRun(result);
      } else {
        _setStatus(_text('Pipeline start failed', '파이프라인 시작 실패'), 'err');
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


  async function renderSafetyCenter() {
    var root = document.getElementById('lab-flow-root');
    if (!root) return;
    _clear(root);

    _appendText(root, 'h2', 'safety-title', _text('Safety Center', '안전 센터'));

    var listDiv = document.createElement('div');
    listDiv.className = 'safety-manifests';
    _appendText(listDiv, 'h3', 'safety-manifests-title', _text('Pending Manifests', '대기 중 매니페스트'));
    root.appendChild(listDiv);

    try {
      var data = await _labGet('/api/lab/manifests');
      if (data && data.manifests && data.manifests.length) {
        var ul = document.createElement('ul');
        ul.className = 'safety-manifest-list';
        data.manifests.forEach(function (m) {
          var li = document.createElement('li');
          li.className = 'safety-manifest-item';
          li.textContent = (m.kind || '') + ': ' + (m.summary || m.id);
          ul.appendChild(li);

          if (m.change_summary && Object.keys(m.change_summary).length) {
            var summaryDiv = document.createElement('div');
            summaryDiv.className = 'safety-change-summary';
            Object.keys(m.change_summary).forEach(function (r) {
              var s = m.change_summary[r];
              var span = document.createElement('span');
              span.className = 'safety-root-summary';
              span.textContent = r + ': +' + s.create + ' ~' + s.modify + ' -' + s.delete;
              summaryDiv.appendChild(span);
            });
            li.appendChild(summaryDiv);
          }

          var rollbackBtn = document.createElement('button');
          rollbackBtn.className = 'btn btn-safety-rollback';
          rollbackBtn.textContent = _text('Rollback', '롤백');
          rollbackBtn.addEventListener('click', function () { requestRollback(m.id); });
          li.appendChild(rollbackBtn);

          var gitBtn = document.createElement('button');
          gitBtn.className = 'btn btn-safety-git-plan';
          gitBtn.textContent = _text('Git Plan (scoped)', 'Git 계획 (범위 지정)');
          gitBtn.addEventListener('click', function () { requestScopedGitPlan(m.id); });
          li.appendChild(gitBtn);
        });
        listDiv.appendChild(ul);
      } else {
        _appendText(listDiv, 'p', 'safety-empty', _text('No pending manifests', '대기 중 매니페스트 없음'));
      }
    } catch (err) {
      _appendText(listDiv, 'p', 'safety-error', _text('Failed to load manifests', '매니페스트 로드 실패'));
    }

    var outputDiv = document.createElement('div');
    outputDiv.id = 'safety-output';
    root.appendChild(outputDiv);
  }

  async function requestRollback(manifestId) {
    var output = document.getElementById('safety-output');
    if (!output) return;
    _clear(output);
    try {
      var result = await _labPost('/api/lab/rollback', { manifest_id: manifestId });
      if (result && result.error_code === 'rollback_unsupported') {
        _appendText(output, 'p', 'safety-manual', result.message || _text('Manual rollback required', '수동 롤백 필요'));
      } else if (result && result.ok) {
        _appendText(output, 'p', 'safety-ok', result.message || _text('Rollback planned', '롤백 계획됨'));
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
      if (result && result.preview_only && result.files) {
        _appendText(output, 'h4', 'safety-git-title', _text('Scoped Git Plan (preview only)', '범위 지정 Git 계획 (미리보기)'));
        var ul = document.createElement('ul');
        ul.className = 'safety-git-files';
        result.files.forEach(function (f) {
          var li = document.createElement('li');
          li.textContent = f;
          ul.appendChild(li);
        });
        output.appendChild(ul);
      } else {
        _appendText(output, 'p', 'safety-error', (result && result.error) || _text('Git plan failed', 'Git 계획 실패'));
      }
    } catch (err) {
      _appendText(output, 'p', 'safety-error', _text('Git plan error', 'Git 계획 오류'));
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
        var root = document.getElementById('lab-flow-root');
        if (root) root.textContent = _text('This flow is planned for the next phase.', '이 흐름은 다음 단계에서 구현됩니다.');
      });
    });
  }

  async function init() {
    if (_ready) return;
    _bindCards();
    if (!S.labToken && typeof labEnsureSession === 'function') await labEnsureSession();
    var ok = await _loadCapabilities();
    _ready = !!ok;
  }

  return { init: init, canApplyManifest: canApplyManifest };
})();
if (typeof registerLangRefresher === 'function') {
  registerLangRefresher(function refreshLabPortalLanguage() {
    if (document.querySelector('#page-lab.active') && typeof initLabPage === 'function') initLabPage();
  });
}
