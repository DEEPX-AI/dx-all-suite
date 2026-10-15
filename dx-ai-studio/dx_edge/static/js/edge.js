/* DX Cloud — stack setup and Cloud Compile panels. Talks to dx_edge/server.py; AWS calls happen server-side only. */
(function () {
  'use strict';

  var POLL_MS = 15000;
  var STACK_POLL_MS = 10000;
  var $ = function (id) { return document.getElementById(id); };
  var job = null;
  var lastStatus = null;
  var pollTimer = null;
  var lastSubs = null;
  var lastStacks = null;
  var lastProgress = null;
  var stackJob = null;
  var stackTimer = null;

  function api(path, opts) {
    // Relative, so it works standalone (/) and behind the launcher proxy (/cloud/).
    return fetch(path, opts).then(function (r) {
      return r.json().then(function (body) {
        if (!r.ok) throw new Error(body.error || r.statusText);
        return body;
      });
    });
  }

  function form() {
    return { profile: $('edgeProfile').value, region: $('edgeRegion').value.trim(), stack: $('edgeStack').value };
  }

  function qs(obj) {
    return Object.keys(obj).map(function (k) {
      return encodeURIComponent(k) + '=' + encodeURIComponent(obj[k] || '');
    }).join('&');
  }

  function setMsg(text, isError) {
    var el = $('edgeJobMsg');
    $('edgeJob').hidden = false;
    el.textContent = text;
    el.classList.toggle('is-error', !!isError);
  }

  function option(value, label) {
    var o = document.createElement('option');
    o.value = value;
    o.textContent = label;
    return o;
  }

  function loadStatus() {
    return api('api/aws/status').then(function (st) {
      var sel = $('edgeProfile');
      sel.replaceChildren(option('', T('Default credentials')));
      st.profiles.forEach(function (p) { sel.appendChild(option(p, p)); });
      if (!$('edgeRegion').value) $('edgeRegion').value = st.default_region;
      var missing = $('edgeBoto3Missing');
      missing.hidden = st.boto3;
      $('edgeStart').disabled = !st.boto3;
      $('edgeStacksReload').disabled = !st.boto3;
      $('edgeDeploy').disabled = !st.boto3;
      $('edgeSetupReload').disabled = !st.boto3;
      if (!st.boto3) {
        missing.textContent = T('boto3 is not installed. Install it to compile in the cloud:') + ' ' + st.install_hint;
        return;
      }
      if (st.error) { setMsg(st.error, true); return; }
      return loadSetup();
    }).catch(function (e) { setMsg(e.message, true); });
  }

  function loadStacks() {
    var f = form();
    var sel = $('edgeStack');
    return api('api/aws/stacks?' + qs({ profile: f.profile, region: f.region })).then(function (res) {
      sel.replaceChildren();
      var ready = res.stacks.filter(function (s) { return s.ready; });
      ready.forEach(function (s) { sel.appendChild(option(s.name, s.name + ' (' + s.bucket + ')')); });
      if (!ready.length) sel.appendChild(option('', T('No compiler stack found in this region')));
      renderStackList(res.stacks);
    }).catch(function (e) {
      sel.replaceChildren();
      setMsg(e.message, true);
    });
  }

  // ── Stack setup ────────────────────────────────────────────────────────

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  function setStackMsg(text, isError) {
    $('edgeStackJob').hidden = false;
    var m = $('edgeStackMsg');
    m.textContent = text;
    m.classList.toggle('is-error', !!isError);
  }

  function loadSetup() {
    loadSubscription();
    return loadStacks();
  }

  function loadSubscription() {
    var f = form();
    return api('api/aws/subscription?' + qs({ profile: f.profile, region: f.region })).then(function (res) {
      renderSubs(res.templates);
    }).catch(function (e) {
      $('edgeSubs').replaceChildren();
      setStackMsg(e.message, true);
    });
  }

  function renderSubs(rows) {
    lastSubs = rows;
    var list = $('edgeSubs');
    var sel = $('edgeTemplate');
    var chosen = sel.value;
    list.replaceChildren();
    sel.replaceChildren();
    rows.forEach(function (r) {
      var li = el('li', 'edge-row');
      li.appendChild(el('strong', null, r.label));
      var badge = el('span', 'badge', r.subscribed ? T('Subscribed') : T('Not subscribed'));
      badge.dataset.state = r.subscribed ? 'ok' : 'bad';
      li.appendChild(badge);
      if (r.ami_id) li.appendChild(el('code', null, r.ami_id));
      li.appendChild(link(r.marketplace, r.subscribed ? T('Open Marketplace listing') : T('Subscribe on Marketplace')));
      list.appendChild(li);
      var o = option(r.id, r.label + (r.subscribed ? '' : ' — ' + T('Not subscribed')));
      o.disabled = !r.subscribed;
      sel.appendChild(o);
    });
    if (chosen) sel.value = chosen;
    if (sel.selectedOptions.length && sel.selectedOptions[0].disabled) {
      var first = rows.filter(function (r) { return r.subscribed; })[0];
      sel.value = first ? first.id : '';
    }
  }

  function renderStackList(stacks) {
    lastStacks = stacks;
    var list = $('edgeStackList');
    list.replaceChildren();
    if (!stacks.length) list.appendChild(el('li', 'edge-row edge-empty', T('No compiler stack found in this region')));
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
        del.addEventListener('click', function () { openDelete(s.name); });
        li.appendChild(del);
      }
      list.appendChild(li);
    });
  }

  function newStackName() {
    var d = new Date();
    var p = function (n) { return String(n).padStart(2, '0'); };
    return 'dx-cloud-' + p(d.getFullYear() % 100) + p(d.getMonth() + 1) + p(d.getDate()) +
      p(d.getHours()) + p(d.getMinutes()) + p(d.getSeconds());
  }

  function renderProgress(pr) {
    lastProgress = pr;
    var badge = $('edgeStackState');
    badge.textContent = pr.status;
    badge.dataset.state = /_COMPLETE$/.test(pr.status) && !/ROLLBACK/.test(pr.status) ? 'ok'
      : /FAILED|ROLLBACK/.test(pr.status) ? 'bad' : 'busy';
    $('edgeStackJobName').textContent = pr.name;
    $('edgeStackJob').hidden = false;
    var ev = $('edgeStackEvents');
    ev.replaceChildren();
    pr.events.forEach(function (e) {
      ev.appendChild(el('li', null, new Date(e.time).toLocaleTimeString() + '  ' + e.resource + '  ' +
        e.status + (e.reason ? ' — ' + e.reason : '')));
    });
  }

  function pollStack() {
    clearTimeout(stackTimer);
    api('api/aws/stacks/progress?' + qs(stackJob)).then(function (pr) {
      renderProgress(pr);
      if (/(_COMPLETE|_FAILED)$/.test(pr.status)) {
        setStackMsg(/ROLLBACK|FAILED/.test(pr.status) ? T('The stack did not finish — see the events above.') : T('Done.'),
          /ROLLBACK|FAILED/.test(pr.status));
        loadStacks();
      } else {
        stackTimer = setTimeout(pollStack, STACK_POLL_MS);
      }
    }).catch(function (e) {
      setStackMsg(e.message, true);
      stackTimer = setTimeout(pollStack, STACK_POLL_MS);
    });
  }

  function trackStack(name, msg) {
    var f = form();
    stackJob = { profile: f.profile, region: f.region, name: name };
    $('edgeStackEvents').replaceChildren();
    setStackMsg(msg);
    pollStack();
  }

  function deploy(ev) {
    ev.preventDefault();
    var f = form();
    var name = $('edgeStackName').value.trim();
    var template = $('edgeTemplate').value;
    if (!template || !name) return setStackMsg(T('Choose a subscribed template and a stack name first'), true);
    $('edgeDeploy').disabled = true;
    api('api/aws/stacks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ profile: f.profile, region: f.region, template: template, name: name })
    }).then(function (res) {
      $('edgeStackName').value = newStackName();
      trackStack(res.name, T('Creating the stack — this usually takes several minutes.') + ' ' + res.bucket);
      loadStacks();
    }).catch(function (e) {
      setStackMsg(e.message, true);
    }).finally(function () {
      $('edgeDeploy').disabled = false;
    });
  }

  function openDelete(name) {
    $('edgeDeleteName').textContent = name;
    $('edgeDeleteConfirm').value = '';
    $('edgeDeleteOk').disabled = true;
    $('edgeDeleteDialog').showModal();
    $('edgeDeleteConfirm').focus();
  }

  function submitDelete(ev) {
    ev.preventDefault();
    var f = form();
    var name = $('edgeDeleteName').textContent;
    var typed = $('edgeDeleteConfirm').value;
    if (typed !== name) return;
    $('edgeDeleteOk').disabled = true;
    api('api/aws/stacks/delete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ profile: f.profile, region: f.region, name: name, confirm: typed })
    }).then(function (res) {
      $('edgeDeleteDialog').close();
      trackStack(res.name, T('Deleting the stack. The S3 model bucket is kept:') + ' ' + res.bucket);
      loadStacks();
    }).catch(function (e) {
      $('edgeDeleteDialog').close();
      setStackMsg(e.message, true);
    });
  }

  function jobQuery() {
    return qs({ profile: job.profile, region: job.region, stack: job.stack, prefix: job.prefix });
  }

  function link(href, label) {
    var a = document.createElement('a');
    a.className = 'btn btn-sm btn-ghost';
    a.href = href;
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    a.textContent = label;
    return a;
  }

  var STATE_MSG = {
    pending: 'Waiting for the compile workflow to start…',
    running: 'Compiling on EC2 — this usually takes several minutes.',
    succeeded: 'Compiled.',
    failed: 'The compile workflow failed — check the CloudWatch logs.'
  };

  function render(st) {
    lastStatus = st;
    var badge = $('edgeJobState');
    badge.textContent = T(st.state);
    badge.dataset.state = st.state;
    setMsg(T(STATE_MSG[st.state]) + (st.dxnn ? ' ' + st.dxnn : ''), st.state === 'failed');
    var done = st.state === 'succeeded';
    $('edgeDownload').hidden = !done;
    $('edgeSave').hidden = !done;
    if (done) $('edgeDownload').href = 'api/aws/compile/download?' + jobQuery();
    var links = $('edgeLinks');
    links.replaceChildren();
    var l = st.links || {};
    if (l.execution || l.state_machine) links.appendChild(link(l.execution || l.state_machine, T('Step Functions')));
    if (l.logs) links.appendChild(link(l.logs, T('CloudWatch logs')));
    if (l.s3) links.appendChild(link(l.s3, T('S3 folder')));
  }

  function poll() {
    clearTimeout(pollTimer);
    api('api/aws/compile/status?' + jobQuery()).then(function (st) {
      render(st);
      if (st.state === 'pending' || st.state === 'running') pollTimer = setTimeout(poll, POLL_MS);
    }).catch(function (e) {
      setMsg(e.message, true);
      pollTimer = setTimeout(poll, POLL_MS);
    });
  }

  function start(ev) {
    ev.preventDefault();
    var f = form();
    var onnx = $('edgeOnnx').files[0];
    var cfg = $('edgeJson').files[0];
    if (!f.stack || !onnx || !cfg) return setMsg(T('Choose a stack, an .onnx and a .json first'), true);
    var body = new FormData();
    body.append('profile', f.profile);
    body.append('region', f.region);
    body.append('stack', f.stack);
    body.append('onnx', onnx);
    body.append('json', cfg);
    $('edgeStart').disabled = true;
    $('edgeDownload').hidden = true;
    $('edgeSave').hidden = true;
    $('edgeLinks').replaceChildren();
    $('edgeJobPrefix').textContent = '';
    setMsg(T('Uploading…'));
    api('api/aws/compile', { method: 'POST', body: body }).then(function (res) {
      job = { profile: f.profile, region: res.region, stack: res.stack, prefix: res.prefix };
      $('edgeJobPrefix').textContent = res.prefix;
      poll();
    }).catch(function (e) {
      setMsg(e.message, true);
    }).finally(function () {
      $('edgeStart').disabled = false;
    });
  }

  function save() {
    $('edgeSave').disabled = true;
    api('api/aws/compile/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(job)
    }).then(function (res) {
      setMsg(T('Saved to') + ' ' + res.path);
    }).catch(function (e) {
      setMsg(e.message, true);
    }).finally(function () {
      $('edgeSave').disabled = false;
    });
  }

  $('edgeCompileForm').addEventListener('submit', start);
  $('edgeStacksReload').addEventListener('click', loadStacks);
  $('edgeProfile').addEventListener('change', loadSetup);
  $('edgeRegion').addEventListener('change', loadSetup);
  $('edgeSetupReload').addEventListener('click', loadSetup);
  $('edgeDeployForm').addEventListener('submit', deploy);
  $('edgeDeleteForm').addEventListener('submit', submitDelete);
  $('edgeDeleteCancel').addEventListener('click', function () { $('edgeDeleteDialog').close(); });
  $('edgeDeleteConfirm').addEventListener('input', function () {
    $('edgeDeleteOk').disabled = this.value !== $('edgeDeleteName').textContent;
  });
  $('edgeStackName').value = newStackName();
  $('edgeSave').addEventListener('click', save);
  // Repaint the JS-written text when the language changes (data-i18n covers the markup).
  DXI18n.onLangChange(function () {
    var first = $('edgeProfile').options[0];
    if (first && !first.value) first.textContent = T('Default credentials');
    var stack = $('edgeStack').options[0];
    if (stack && !stack.value) stack.textContent = T('No compiler stack found in this region');
    if (lastStatus) render(lastStatus);
    if (lastSubs) renderSubs(lastSubs);
    if (lastStacks) renderStackList(lastStacks);
  });
  loadStatus();
})();
