/* DX Cloud — AWS Compiler / AWS Greengrass tabs: stack setup, Cloud Compile, and Greengrass devices.
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
    return { profile: $('edgeProfile').value, region: $('edgeRegion').value.trim() };
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

  function loadStatus() {
    return api('api/aws/status').then(function (st) {
      var sel = $('edgeProfile');
      sel.replaceChildren(option('', T('Default credentials')));
      st.profiles.forEach(function (p) { sel.appendChild(option(p, p)); });
      if (!$('edgeRegion').value) $('edgeRegion').value = st.default_region;
      var missing = $('edgeBoto3Missing');
      missing.hidden = st.boto3;
      KINDS.forEach(function (k) {
        ['edgeStart', 'edgeStacksReload', 'edgeDeploy', 'edgeSetupReload'].forEach(function (id) {
          $k(id, k).disabled = !st.boto3;
        });
      });
      $('edgeDevReload').disabled = !st.boto3;
      $('edgeRegGen').disabled = !st.boto3;
      if (!st.boto3) {
        missing.textContent = T('boto3 is not installed. Install it to compile in the cloud:') + ' ' + st.install_hint;
        return;
      }
      if (st.error) { missing.hidden = false; missing.textContent = st.error; return; }
      return loadSetup();
    }).catch(function (e) {
      $('edgeBoto3Missing').hidden = false;
      $('edgeBoto3Missing').textContent = e.message;
    });
  }

  function loadSetup() {
    loadSubscription();
    return loadStacks();
  }

  function loadSubscription() {
    return api('api/aws/subscription?' + qs(account())).then(function (res) {
      lastSubs = res.templates;
      KINDS.forEach(renderSubs);
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
  }

  function poll(kind) {
    var s = state[kind];
    clearTimeout(s.pollTimer);
    api('api/aws/compile/status?' + jobQuery(s.job)).then(function (st) {
      render(kind, st);
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
      $k('edgeJobPrefix', kind).textContent = res.prefix;
      poll(kind);
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

  function copyScript() {
    var fallback = function () {
      var range = document.createRange();
      range.selectNodeContents($('edgeScript'));
      var sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
      showMsg($('edgeRegMsg'), T('Selected — press Ctrl+C to copy.'));
    };
    if (!navigator.clipboard || !window.isSecureContext) return fallback();
    navigator.clipboard.writeText(script.script).then(function () {
      showMsg($('edgeRegMsg'), T('Copied.'));
    }, fallback);
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
  });
  $k('edgeStack', 'greengrass').addEventListener('change', loadDevices);
  $('edgeProfile').addEventListener('change', loadSetup);
  $('edgeRegion').addEventListener('change', loadSetup);
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
      if (lastSubs) renderSubs(k);
      if (lastStacks) renderStacks(k);
    });
    if (lastDevices) renderDevices(lastDevices);
  });

  var saved = null;
  try { saved = localStorage.getItem(TAB_KEY); } catch (e) { saved = null; }
  selectTab(KINDS.indexOf(saved) >= 0 ? saved : 'compiler');
  loadStatus();
})();
