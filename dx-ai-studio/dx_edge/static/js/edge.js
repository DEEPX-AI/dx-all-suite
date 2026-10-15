/* DX Cloud — step 1 (AWS connection) and DEEPX Compiler Solution / DEEPX Greengrass Solution tabs: subscription, stacks,
   Cloud Compile, and Greengrass devices. The status chips and step states follow the loaded data.
   Both tabs share the same markup with a -<kind> id suffix, so every panel function takes the kind.
   Talks to dx_edge/server.py; AWS calls happen server-side only. */
(function () {
  'use strict';

  var POLL_MS = 15000;
  var STACK_POLL_MS = 10000;
  var KINDS = ['compiler', 'greengrass'];
  var TAB_KEY = 'dx-cloud-tab';
  var $ = function (id) { return document.getElementById(id); };
  var $k = function (id, kind) { return $(id + '-' + kind); };
  var state = {};
  KINDS.forEach(function (k) {
    state[k] = { job: null, lastStatus: null, pollTimer: null, stackJob: null, stackTimer: null, subscribed: false };
  });
  var lastSubs = null;
  var lastStacks = null;
  var lastDevices = null;
  var deleteKind = null;
  var script = null;
  var current = 'compiler';
  var ident = null; // null while checking, then {account, arn} or {error}
  var regionPicked = false; // true once the user picks a region; until then it follows the profile

  function api(path, opts) {
    // Relative, so it works standalone (/) and behind the launcher proxy (/cloud/).
    return fetch(path, opts).then(function (r) {
      return r.json().then(function (body) {
        if (!r.ok) throw new Error(body.error || r.statusText);
        return body;
      });
    });
  }

  function postJson(path, body) {
    return api(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  }

  function account() {
    return { profile: $('edgeProfile').value, region: $('edgeRegion').value };
  }

  function qs(obj) {
    return Object.keys(obj).map(function (k) {
      return encodeURIComponent(k) + '=' + encodeURIComponent(obj[k] || '');
    }).join('&');
  }

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  function option(value, label) {
    var o = el('option', null, label);
    o.value = value;
    return o;
  }

  function link(href, label) {
    var a = el('a', 'btn btn-sm btn-ghost', label);
    a.href = href;
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    return a;
  }

  function showMsg(node, text, isError) {
    node.textContent = text;
    node.classList.toggle('is-error', !!isError);
  }

  function setMsg(kind, text, isError) {
    $k('edgeJob', kind).hidden = false;
    showMsg($k('edgeJobMsg', kind), text, isError);
  }

  function setStackMsg(kind, text, isError) {
    $k('edgeStackJob', kind).hidden = false;
    showMsg($k('edgeStackMsg', kind), text, isError);
  }

  function emptyText(kind) {
    return kind === 'greengrass' ? T('No Greengrass stack found in this region') : T('No compiler stack found in this region');
  }

  // ── Tabs ───────────────────────────────────────────────────────────────

  function selectTab(kind, focus) {
    KINDS.forEach(function (k) {
      var on = k === kind;
      var tab = $k('edgeTab', k);
      tab.setAttribute('aria-selected', on ? 'true' : 'false');
      tab.tabIndex = on ? 0 : -1;
      $k('edgePanel', k).hidden = !on;
    });
    current = kind;
    updateSteps();
    if (focus) $k('edgeTab', kind).focus();
    try { localStorage.setItem(TAB_KEY, kind); } catch (e) { /* storage blocked: the tab is just not remembered */ }
  }

  KINDS.forEach(function (k, i) {
    var tab = $k('edgeTab', k);
    tab.addEventListener('click', function () { selectTab(k); });
    tab.addEventListener('keydown', function (ev) {
      var step = ev.key === 'ArrowRight' ? 1 : ev.key === 'ArrowLeft' ? -1 : 0;
      if (!step) return;
      ev.preventDefault();
      selectTab(KINDS[(i + step + KINDS.length) % KINDS.length], true);
    });
  });

  // ── Account, subscription and stacks ───────────────────────────────────

  // Regions enabled for the account (or the known list); keeps the current pick, else the profile's region.
  function loadRegions(fallback) {
    var sel = $('edgeRegion');
    var want = regionPicked ? sel.value : fallback;
    return api('api/aws/regions?' + qs({ profile: $('edgeProfile').value })).then(function (res) {
      sel.replaceChildren();
      res.regions.forEach(function (r) {
        sel.appendChild(option(r.code, r.name ? r.code + ' · ' + r.name : r.code));
      });
      if (!res.regions.some(function (r) { return r.code === want; })) sel.appendChild(option(want, want));
      if (sel.value !== want) { sel.value = want; loadSetup(); }
    }).catch(function () { /* the server-rendered default stays */ });
  }

  function loadStatus() {
    ident = null;
    showMsg($('edgeIdentity'), T('Checking…'));
    updateSteps();
    return api('api/aws/status?' + qs({ profile: $('edgeProfile').value })).then(function (st) {
      var sel = $('edgeProfile');
      var chosen = sel.value;
      sel.replaceChildren(option('', T('Default credentials')));
      st.profiles.forEach(function (p) { sel.appendChild(option(p, p)); });
      if (st.profiles.indexOf(chosen) >= 0) sel.value = chosen;
      if (!st.profiles.length || st.error || !st.boto3) $('edgeGuide').open = true;
      if (st.boto3) loadRegions(st.default_region);
      var missing = $('edgeBoto3Missing');
      missing.hidden = st.boto3;
      KINDS.forEach(function (k) {
        ['edgeStart', 'edgeStacksReload', 'edgeDeploy', 'edgeSetupReload'].forEach(function (id) {
          $k(id, k).disabled = !st.boto3;
        });
      });
      $('edgeDevReload').disabled = !st.boto3;
      $('edgeRegGen').disabled = !st.boto3;
      $('edgeCheck').disabled = !st.boto3;
      if (!st.boto3) {
        missing.textContent = T('boto3 is not installed. Install it to compile in the cloud:') + ' ' + st.install_hint;
        return noIdentity('');
      }
      if (st.error) { missing.hidden = false; missing.textContent = st.error; return noIdentity(st.error); }
      return loadSetup();
    }).catch(function (e) {
      $('edgeBoto3Missing').hidden = false;
      $('edgeBoto3Missing').textContent = e.message;
      noIdentity(e.message);
    });
  }

  function noIdentity(message) {
    ident = { error: message };
    showMsg($('edgeIdentity'), message, !!message);
    $('edgeGuide').open = true;
    updateSteps();
  }

  // sts get-caller-identity: proves the credentials work and names the account.
  function checkIdentity() {
    ident = null;
    showMsg($('edgeIdentity'), T('Checking…'));
    updateSteps();
    return api('api/aws/identity?' + qs(account())).then(function (res) {
      ident = res;
      showMsg($('edgeIdentity'), T('Connected as') + ' ' + res.arn);
      updateSteps();
    }).catch(function (e) {
      noIdentity(e.message);
    });
  }

  function loadSetup() {
    checkIdentity();
    loadSubscription();
    return loadStacks();
  }

  // ── Status chips and step states ───────────────────────────────────────

  var STEP_TEXT = { done: 'Done', todo: 'Action needed', blocked: 'Waiting', running: 'In progress' };

  function setStep(id, st) {
    var badge = $(id);
    badge.className = 'dx-step-state is-' + st;
    badge.textContent = T(STEP_TEXT[st]);
    badge.closest('.dx-step').dataset.state = st;
  }

  function setChip(id, value, st) {
    $(id + 'Val').textContent = value;
    if (st) $(id).dataset.state = st;
    else delete $(id).dataset.state;
  }

  function readyStacks(kind) {
    return (lastStacks || []).filter(function (s) { return s.kind === kind && s.ready; });
  }

  function updateSteps() {
    var f = account();
    var connected = !!(ident && ident.account);
    setChip('edgeChipProfile', f.profile || T('Default credentials'));
    setChip('edgeChipRegion', f.region || '—');
    setChip('edgeChipAccount', connected ? ident.account : ident ? T('Not connected') : '…',
      connected ? 'ok' : ident ? 'bad' : 'busy');
    setStep('edgeStep1State', connected ? 'done' : ident ? 'todo' : 'running');
    KINDS.forEach(function (k) {
      var sub = (lastSubs || []).filter(function (r) { return r.id === k; })[0];
      var ready = readyStacks(k);
      var busy = (lastStacks || []).some(function (s) { return s.kind === k && /_IN_PROGRESS$/.test(s.status); });
      var job = state[k].lastStatus;
      var s2 = !connected || !sub ? 'blocked' : sub.subscribed ? 'done' : 'todo';
      setStep('edgeStep2State-' + k, s2);
      setStep('edgeStep3State-' + k, ready.length ? 'done' : busy ? 'running' : s2 === 'done' ? 'todo' : 'blocked');
      setStep('edgeStep4State-' + k, job && job.state === 'succeeded' ? 'done'
        : job && job.state !== 'failed' ? 'running' : ready.length ? 'todo' : 'blocked');
      if (k !== current) return;
      setChip('edgeChipSubs', sub ? T(sub.subscribed ? 'Subscribed' : 'Not subscribed') : '—',
        sub ? (sub.subscribed ? 'ok' : 'bad') : null);
      setChip('edgeChipStacks', lastStacks ? String(ready.length) : '—',
        lastStacks ? (ready.length ? 'ok' : 'bad') : null);
    });
    var devices = lastDevices && lastDevices.devices.length;
    setStep('edgeStep5State-greengrass', devices ? 'done' : readyStacks('greengrass').length ? 'todo' : 'blocked');
  }

  function loadSubscription() {
    return api('api/aws/subscription?' + qs(account())).then(function (res) {
      lastSubs = res.templates;
      KINDS.forEach(renderSubs);
      updateSteps();
    }).catch(function (e) {
      KINDS.forEach(function (k) {
        $k('edgeSubs', k).replaceChildren();
        setStackMsg(k, e.message, true);
      });
    });
  }

  function loadStacks() {
    return api('api/aws/stacks?' + qs(account())).then(function (res) {
      lastStacks = res.stacks;
      KINDS.forEach(renderStacks);
      updateSteps();
      loadDevices();
    }).catch(function (e) {
      KINDS.forEach(function (k) {
        $k('edgeStack', k).replaceChildren();
        setMsg(k, e.message, true);
      });
    });
  }

  function renderSubs(kind) {
    var list = $k('edgeSubs', kind);
    list.replaceChildren();
    lastSubs.filter(function (r) { return r.id === kind; }).forEach(function (r) {
      state[kind].subscribed = r.subscribed;
      var li = el('li', 'edge-row');
      li.appendChild(el('strong', null, r.label));
      var badge = el('span', 'badge', r.subscribed ? T('Subscribed') : T('Not subscribed'));
      badge.dataset.state = r.subscribed ? 'ok' : 'bad';
      li.appendChild(badge);
      if (r.ami_id) li.appendChild(el('code', null, r.ami_id));
      li.appendChild(link(r.marketplace, r.subscribed ? T('Open Marketplace listing') : T('Subscribe on Marketplace')));
      list.appendChild(li);
    });
  }

  function renderStacks(kind) {
    var stacks = lastStacks.filter(function (s) { return s.kind === kind; });
    var sel = $k('edgeStack', kind);
    var chosen = sel.value;
    sel.replaceChildren();
    var ready = stacks.filter(function (s) { return s.ready; });
    ready.forEach(function (s) { sel.appendChild(option(s.name, s.name + ' (' + s.bucket + ')')); });
    if (!ready.length) sel.appendChild(option('', emptyText(kind)));
    if (ready.some(function (s) { return s.name === chosen; })) sel.value = chosen;

    var list = $k('edgeStackList', kind);
    list.replaceChildren();
    if (!stacks.length) list.appendChild(el('li', 'edge-row edge-empty', emptyText(kind)));
    stacks.forEach(function (s) {
      var li = el('li', 'edge-row');
      li.appendChild(el('strong', null, s.name));
      var badge = el('span', 'badge', s.status);
      badge.dataset.state = s.ready ? 'ok' : (s.deletable ? 'bad' : 'busy');
      li.appendChild(badge);
      if (s.bucket) li.appendChild(el('code', null, s.bucket));
      li.appendChild(el('span', 'edge-dim', T('Created') + ' ' + new Date(s.created).toLocaleString()));
      if (s.deletable) {
        var del = el('button', 'btn btn-sm btn-danger', T('Delete'));
        del.type = 'button';
        del.addEventListener('click', function () { openDelete(kind, s.name); });
        li.appendChild(del);
      }
      list.appendChild(li);
    });
  }

  function newStackName(kind) {
    var d = new Date();
    var p = function (n) { return String(n).padStart(2, '0'); };
    return (kind === 'greengrass' ? 'dx-gg-' : 'dx-cloud-') + p(d.getFullYear() % 100) + p(d.getMonth() + 1) +
      p(d.getDate()) + p(d.getHours()) + p(d.getMinutes()) + p(d.getSeconds());
  }

  function renderProgress(kind, pr) {
    var badge = $k('edgeStackState', kind);
    badge.textContent = pr.status;
    badge.dataset.state = /_COMPLETE$/.test(pr.status) && !/ROLLBACK/.test(pr.status) ? 'ok'
      : /FAILED|ROLLBACK/.test(pr.status) ? 'bad' : 'busy';
    $k('edgeStackJobName', kind).textContent = pr.name;
    $k('edgeStackJob', kind).hidden = false;
    var ev = $k('edgeStackEvents', kind);
    ev.replaceChildren();
    pr.events.forEach(function (e) {
      ev.appendChild(el('li', null, new Date(e.time).toLocaleTimeString() + '  ' + e.resource + '  ' +
        e.status + (e.reason ? ' — ' + e.reason : '')));
    });
  }

  function pollStack(kind) {
    var s = state[kind];
    clearTimeout(s.stackTimer);
    api('api/aws/stacks/progress?' + qs(s.stackJob)).then(function (pr) {
      renderProgress(kind, pr);
      if (/(_COMPLETE|_FAILED)$/.test(pr.status)) {
        var bad = /ROLLBACK|FAILED/.test(pr.status);
        setStackMsg(kind, bad ? T('The stack did not finish — see the events above.') : T('Done.'), bad);
        loadStacks();
      } else {
        s.stackTimer = setTimeout(function () { pollStack(kind); }, STACK_POLL_MS);
      }
    }).catch(function (e) {
      setStackMsg(kind, e.message, true);
      s.stackTimer = setTimeout(function () { pollStack(kind); }, STACK_POLL_MS);
    });
  }

  function trackStack(kind, name, msg) {
    var f = account();
    state[kind].stackJob = { profile: f.profile, region: f.region, name: name };
    $k('edgeStackEvents', kind).replaceChildren();
    setStackMsg(kind, msg);
    pollStack(kind);
  }

  function deploy(kind, ev) {
    ev.preventDefault();
    var f = account();
    var name = $k('edgeStackName', kind).value.trim();
    if (!state[kind].subscribed || !name) return setStackMsg(kind, T('Choose a subscribed template and a stack name first'), true);
    var btn = $k('edgeDeploy', kind);
    btn.disabled = true;
    postJson('api/aws/stacks', { profile: f.profile, region: f.region, template: kind, name: name }).then(function (res) {
      $k('edgeStackName', kind).value = newStackName(kind);
      trackStack(kind, res.name, T('Creating the stack — this usually takes several minutes.') + ' ' + res.bucket);
      loadStacks();
    }).catch(function (e) {
      setStackMsg(kind, e.message, true);
    }).finally(function () {
      btn.disabled = false;
    });
  }

  function openDelete(kind, name) {
    deleteKind = kind;
    $('edgeDeleteName').textContent = name;
    $('edgeDeleteConfirm').value = '';
    $('edgeDeleteOk').disabled = true;
    $('edgeDeleteDialog').showModal();
    $('edgeDeleteConfirm').focus();
  }

  function submitDelete(ev) {
    ev.preventDefault();
    var f = account();
    var kind = deleteKind;
    var name = $('edgeDeleteName').textContent;
    var typed = $('edgeDeleteConfirm').value;
    if (typed !== name) return;
    $('edgeDeleteOk').disabled = true;
    postJson('api/aws/stacks/delete', { profile: f.profile, region: f.region, name: name, confirm: typed }).then(function (res) {
      $('edgeDeleteDialog').close();
      trackStack(kind, res.name, T('Deleting the stack. The S3 model bucket is kept:') + ' ' + res.bucket);
      loadStacks();
    }).catch(function (e) {
      $('edgeDeleteDialog').close();
      setStackMsg(kind, e.message, true);
    });
  }

  // ── Cloud Compile ──────────────────────────────────────────────────────

  function jobQuery(job) {
    return qs({ profile: job.profile, region: job.region, stack: job.stack, prefix: job.prefix });
  }

  var STATE_MSG = {
    pending: 'Waiting for the compile workflow to start…',
    running: 'Compiling on EC2 — this usually takes several minutes.',
    succeeded: 'Compiled.',
    failed: 'The compile workflow failed — check the CloudWatch logs.'
  };

  function render(kind, st) {
    state[kind].lastStatus = st;
    var badge = $k('edgeJobState', kind);
    badge.textContent = T(st.state);
    badge.dataset.state = st.state;
    setMsg(kind, T(STATE_MSG[st.state]) + (st.dxnn ? ' ' + st.dxnn : ''), st.state === 'failed');
    var done = st.state === 'succeeded';
    $k('edgeDownload', kind).hidden = !done;
    $k('edgeSave', kind).hidden = !done;
    if (done) $k('edgeDownload', kind).href = 'api/aws/compile/download?' + jobQuery(state[kind].job);
    var links = $k('edgeLinks', kind);
    links.replaceChildren();
    var l = st.links || {};
    if (l.execution || l.state_machine) links.appendChild(link(l.execution || l.state_machine, T('Step Functions')));
    if (l.logs) links.appendChild(link(l.logs, T('CloudWatch logs')));
    if (l.s3) links.appendChild(link(l.s3, T('S3 folder')));
    updateSteps();
  }

  // Step Functions state names → what the user sees; unknown states show as-is.
  var LOG_STEPS = {
    ExecutionStarted: 'Workflow started',
    StartEC2Instance: 'Start the compiler EC2 instance',
    SaveInstanceId: 'Record the instance ID',
    WaitForInstanceReady: 'Wait for the instance to boot',
    RunCompilationCommand: 'Send the compile command (SSM)',
    CheckCommandStatus: 'dxcom running — status checks',
    TerminateInstanceAfterSuccess: 'Terminate the instance',
    TerminateInstanceAfterFailure: 'Terminate the instance',
    WorkflowComplete: 'Workflow complete',
    ExecutionSucceeded: 'Workflow complete',
    WorkflowFailed: 'Workflow failed',
    WorkflowFailedBeforeInstance: 'Workflow failed',
    TaskFailed: 'Task failed',
    ExecutionFailed: 'Workflow failed',
    ExecutionTimedOut: 'Workflow failed',
    ExecutionAborted: 'Workflow failed'
  };
  var LOG_POLL_MS = 5000;

  function renderLog(kind, log) {
    state[kind].lastLog = log;
    var steps = $k('edgeLogSteps', kind);
    steps.replaceChildren();
    log.steps.forEach(function (st, i) {
      var li = el('li', st.status === 'failed' ? 'is-failed' : (i === log.steps.length - 1 ? 'is-last' : null));
      var time = el('time', null, new Date(st.time).toLocaleTimeString());
      time.dateTime = st.time;
      li.appendChild(time);
      li.appendChild(el('span', null, LOG_STEPS[st.name] ? T(LOG_STEPS[st.name]) : st.name));
      if (st.count > 1) li.appendChild(el('span', 'edge-dim', '×' + st.count));
      if (st.detail) li.appendChild(el('code', null, st.detail));
      steps.appendChild(li);
    });
    if (!log.steps.length) steps.appendChild(el('li', 'edge-dim', T('Waiting for the compile workflow to start…')));
    var out = $k('edgeLogOut', kind);
    var atEnd = out.scrollTop + out.clientHeight >= out.scrollHeight - 8;
    out.replaceChildren();
    log.lines.forEach(function (line) {
      out.appendChild(el('span', line.stream === 'stderr' ? 'is-err' : null, line.text + '\n'));
    });
    if (atEnd) out.scrollTop = out.scrollHeight;
    $k('edgeLogMeta', kind).textContent = log.instance_id ? log.instance_id : '';
  }

  function pollLog(kind) {
    var s = state[kind];
    clearTimeout(s.logTimer);
    if (!s.job) return;
    var job = s.job;
    var running = true;
    api('api/aws/compile/log?' + jobQuery(job)).then(function (log) {
      if (s.job !== job) return;
      renderLog(kind, log);
      // The .dxnn lands before the workflow terminates its instance; keep reading until the run ends.
      running = !log.execution || log.execution.status === 'RUNNING';
    }).catch(function () { /* the status line already reports AWS errors */ }).then(function () {
      var st = s.lastStatus && s.lastStatus.state;
      if (s.job === job && (!st || st === 'pending' || st === 'running' || running)) {
        s.logTimer = setTimeout(function () { pollLog(kind); }, LOG_POLL_MS);
      }
    });
  }

  function poll(kind) {
    var s = state[kind];
    clearTimeout(s.pollTimer);
    api('api/aws/compile/status?' + jobQuery(s.job)).then(function (st) {
      var wasActive = !s.lastStatus || s.lastStatus.state === 'pending' || s.lastStatus.state === 'running';
      render(kind, st);
      // One last log read when the run ends, so the final lines and steps are shown.
      if (wasActive && (st.state === 'succeeded' || st.state === 'failed')) pollLog(kind);
      if (st.state === 'pending' || st.state === 'running') s.pollTimer = setTimeout(function () { poll(kind); }, POLL_MS);
    }).catch(function (e) {
      setMsg(kind, e.message, true);
      s.pollTimer = setTimeout(function () { poll(kind); }, POLL_MS);
    });
  }

  function start(kind, ev) {
    ev.preventDefault();
    var f = account();
    var stack = $k('edgeStack', kind).value;
    var onnx = $k('edgeOnnx', kind).files[0];
    var cfg = $k('edgeJson', kind).files[0];
    if (!stack || !onnx || !cfg) return setMsg(kind, T('Choose a stack, an .onnx and a .json first'), true);
    var body = new FormData();
    body.append('profile', f.profile);
    body.append('region', f.region);
    body.append('stack', stack);
    body.append('onnx', onnx);
    body.append('json', cfg);
    $k('edgeStart', kind).disabled = true;
    $k('edgeDownload', kind).hidden = true;
    $k('edgeSave', kind).hidden = true;
    $k('edgeLinks', kind).replaceChildren();
    $k('edgeJobPrefix', kind).textContent = '';
    setMsg(kind, T('Uploading…'));
    api('api/aws/compile', { method: 'POST', body: body }).then(function (res) {
      state[kind].job = { profile: f.profile, region: res.region, stack: res.stack, prefix: res.prefix };
      state[kind].lastStatus = null;
      $k('edgeJobPrefix', kind).textContent = res.prefix;
      $k('edgeLogSteps', kind).replaceChildren();
      $k('edgeLogOut', kind).replaceChildren();
      poll(kind);
      pollLog(kind);
    }).catch(function (e) {
      setMsg(kind, e.message, true);
    }).finally(function () {
      $k('edgeStart', kind).disabled = false;
    });
  }

  function save(kind) {
    var btn = $k('edgeSave', kind);
    btn.disabled = true;
    postJson('api/aws/compile/save', state[kind].job).then(function (res) {
      setMsg(kind, T('Saved to') + ' ' + res.path);
    }).catch(function (e) {
      setMsg(kind, e.message, true);
    }).finally(function () {
      btn.disabled = false;
    });
  }

  // ── Greengrass devices (the ready stack picked in the Greengrass compile card) ──

  function devStack() { return $k('edgeStack', 'greengrass').value; }

  function badgeState(status, ok, bad) {
    return ok.indexOf(status) >= 0 ? 'ok' : bad.indexOf(status) >= 0 ? 'bad' : 'busy';
  }

  function loadDevices() {
    var f = account();
    var stack = devStack();
    lastDevices = null;
    updateSteps();
    $('edgeDevStack').textContent = stack || '—';
    $('edgeDevGroup').textContent = '—';
    $('edgeDevDeploy').textContent = '—';
    delete $('edgeDevDeploy').dataset.state;
    $('edgeDevRows').replaceChildren();
    if (!stack) return showMsg($('edgeDevMsg'), T('Choose a ready Greengrass stack first'));
    showMsg($('edgeDevMsg'), T('Loading…'));
    return api('api/aws/greengrass/devices?' + qs({ profile: f.profile, region: f.region, stack: stack })).then(function (res) {
      if (stack !== devStack()) return;
      showMsg($('edgeDevMsg'), '');
      renderDevices(res);
    }).catch(function (e) {
      showMsg($('edgeDevMsg'), e.message, true);
    });
  }

  function renderDevices(res) {
    lastDevices = res;
    updateSteps();
    $('edgeDevGroup').textContent = res.thing_group;
    var dep = $('edgeDevDeploy');
    dep.textContent = res.deployment ? res.deployment.status : '—';
    if (res.deployment) dep.dataset.state = badgeState(res.deployment.status, ['ACTIVE', 'COMPLETED'], ['FAILED', 'CANCELED']);
    dep.title = (res.deployment && res.deployment.error) || '';
    var body = $('edgeDevRows');
    body.replaceChildren();
    if (!res.devices.length) {
      var empty = el('td', 'edge-empty', T('No core device in this Thing Group yet'));
      empty.colSpan = 4;
      body.appendChild(el('tr')).appendChild(empty);
    }
    res.devices.forEach(function (d) {
      var tr = el('tr');
      tr.appendChild(el('td', null, d.name));
      var badge = el('span', 'badge', d.status);
      badge.dataset.state = badgeState(d.status, ['HEALTHY'], ['UNHEALTHY']);
      tr.appendChild(el('td')).appendChild(badge);
      tr.appendChild(el('td', 'edge-dim', d.last_update ? new Date(d.last_update).toLocaleString() : '—'));
      var btn = el('button', 'btn btn-sm btn-ghost', T('Components'));
      btn.type = 'button';
      btn.setAttribute('aria-expanded', 'false');
      btn.addEventListener('click', function () { toggleComponents(d.name, tr, btn); });
      tr.appendChild(el('td')).appendChild(btn);
      body.appendChild(tr);
    });
  }

  function toggleComponents(name, tr, btn) {
    var next = tr.nextElementSibling;
    if (next && next.classList.contains('edge-comp-row')) {
      next.remove();
      btn.setAttribute('aria-expanded', 'false');
      return;
    }
    var row = el('tr', 'edge-comp-row');
    var td = el('td', null, T('Loading…'));
    td.colSpan = 4;
    row.appendChild(td);
    tr.after(row);
    btn.setAttribute('aria-expanded', 'true');
    var f = account();
    api('api/aws/greengrass/components?' + qs({ profile: f.profile, region: f.region, device: name })).then(function (res) {
      td.replaceChildren();
      if (!res.components.length) td.appendChild(el('span', 'edge-empty', T('No DEEPX or Greengrass component installed')));
      var ul = td.appendChild(el('ul', 'edge-comps'));
      res.components.forEach(function (c) {
        var li = ul.appendChild(el('li'));
        li.appendChild(el('code', null, c.name));
        li.appendChild(el('span', 'edge-dim', c.version));
        var badge = li.appendChild(el('span', 'badge', c.state));
        badge.dataset.state = badgeState(c.state, ['RUNNING', 'FINISHED'], ['BROKEN', 'ERRORED']);
      });
    }).catch(function (e) {
      td.replaceChildren(el('span', 'edge-job-msg is-error', e.message));
    });
  }

  function generate(ev) {
    ev.preventDefault();
    var f = account();
    var stack = devStack();
    var thing = $('edgeThing').value.trim();
    if (!stack || !thing) return showMsg($('edgeRegMsg'), T('Choose a ready Greengrass stack and a thing name first'), true);
    $('edgeRegGen').disabled = true;
    postJson('api/aws/greengrass/install-script', { profile: f.profile, region: f.region, stack: stack, thing: thing }).then(function (res) {
      script = res;
      $('edgeScript').textContent = res.script;
      $('edgeRegOut').hidden = false;
      showMsg($('edgeRegMsg'), '');
    }).catch(function (e) {
      showMsg($('edgeRegMsg'), e.message, true);
    }).finally(function () {
      $('edgeRegGen').disabled = false;
    });
  }

  // Clipboard where allowed; otherwise select the text so Ctrl+C copies it.
  function copyText(node, text, done) {
    var fallback = function () {
      var range = document.createRange();
      range.selectNodeContents(node);
      var sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
      done(T('Selected — press Ctrl+C to copy.'));
    };
    if (!navigator.clipboard || !window.isSecureContext) return fallback();
    navigator.clipboard.writeText(text).then(function () { done(T('Copied.')); }, fallback);
  }

  function copyScript() {
    copyText($('edgeScript'), script.script, function (msg) { showMsg($('edgeRegMsg'), msg); });
  }

  // Setup guide commands: the button briefly says what happened instead of "Copy".
  function copyCommand(btn) {
    var code = btn.previousElementSibling;
    var label = btn.querySelector('span');
    copyText(code, code.textContent, function (msg) {
      label.textContent = msg;
      setTimeout(function () { label.textContent = T('Copy'); }, 2000);
    });
  }

  // ── File drop zones (the file input covers the zone, so click, keyboard and drop are native) ──

  function formatSize(bytes) {
    if (bytes >= 1048576) return (bytes / 1048576).toFixed(1) + ' MB';
    return Math.max(1, Math.round(bytes / 1024)) + ' KB';
  }

  function wireDrop(kind, part, ext) {
    var input = $k('edge' + part, kind);
    var zone = $k('edge' + part + 'Drop', kind);
    var label = $k('edge' + part + 'File', kind);
    var over = function (on) { zone.classList.toggle('is-over', on); };
    input.addEventListener('dragenter', function () { over(true); });
    input.addEventListener('dragleave', function () { over(false); });
    input.addEventListener('drop', function () { over(false); });
    input.addEventListener('change', function () {
      var file = input.files[0];
      var ok = !!file && file.name.toLowerCase().endsWith(ext);
      if (file && !ok) input.value = '';
      label.textContent = file ? file.name + (ok ? ' · ' + formatSize(file.size) : '') : '';
      if (file) zone.dataset.state = ok ? 'ready' : 'bad';
      else delete zone.dataset.state;
    });
  }

  function downloadScript() {
    var url = URL.createObjectURL(new Blob([script.script], { type: 'text/x-shellscript' }));
    var a = el('a');
    a.href = url;
    a.download = 'greengrass-install-' + script.thing.replace(/:/g, '_') + '.sh';
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 0);
  }

  // ── Wiring ─────────────────────────────────────────────────────────────

  KINDS.forEach(function (k) {
    $k('edgeCompileForm', k).addEventListener('submit', function (ev) { start(k, ev); });
    $k('edgeStacksReload', k).addEventListener('click', loadStacks);
    $k('edgeSetupReload', k).addEventListener('click', loadSetup);
    $k('edgeDeployForm', k).addEventListener('submit', function (ev) { deploy(k, ev); });
    $k('edgeSave', k).addEventListener('click', function () { save(k); });
    $k('edgeStackName', k).value = newStackName(k);
    wireDrop(k, 'Onnx', '.onnx');
    wireDrop(k, 'Json', '.json');
  });
  $('edgeCheck').addEventListener('click', loadStatus);
  document.querySelectorAll('.edge-copy').forEach(function (btn) {
    btn.addEventListener('click', function () { copyCommand(btn); });
  });
  $k('edgeStack', 'greengrass').addEventListener('change', loadDevices);
  $('edgeProfile').addEventListener('change', loadSetup);
  $('edgeRegion').addEventListener('change', function () { regionPicked = true; loadSetup(); });
  $('edgeProfile').addEventListener('change', function () { if (!regionPicked) loadStatus(); });
  $('edgeDeleteForm').addEventListener('submit', submitDelete);
  $('edgeDeleteCancel').addEventListener('click', function () { $('edgeDeleteDialog').close(); });
  $('edgeDeleteConfirm').addEventListener('input', function () {
    $('edgeDeleteOk').disabled = this.value !== $('edgeDeleteName').textContent;
  });
  $('edgeDevReload').addEventListener('click', loadDevices);
  $('edgeRegForm').addEventListener('submit', generate);
  $('edgeCopy').addEventListener('click', copyScript);
  $('edgeScriptDownload').addEventListener('click', downloadScript);
  // Repaint the JS-written text when the language changes (data-i18n covers the markup).
  DXI18n.onLangChange(function () {
    var first = $('edgeProfile').options[0];
    if (first && !first.value) first.textContent = T('Default credentials');
    KINDS.forEach(function (k) {
      var lastStatus = state[k].lastStatus;
      if (lastStatus) render(k, lastStatus);
      if (state[k].lastLog) renderLog(k, state[k].lastLog);
      if (lastSubs) renderSubs(k);
      if (lastStacks) renderStacks(k);
    });
    if (lastDevices) renderDevices(lastDevices);
    updateSteps();
  });

  var saved = null;
  try { saved = localStorage.getItem(TAB_KEY); } catch (e) { saved = null; }
  selectTab(KINDS.indexOf(saved) >= 0 ? saved : 'compiler');
  loadStatus();
})();
