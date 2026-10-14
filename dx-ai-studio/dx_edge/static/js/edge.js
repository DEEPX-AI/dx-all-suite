/* DX Edge — Cloud Compile panel. Talks to dx_edge/server.py; AWS calls happen server-side only. */
(function () {
  'use strict';

  var POLL_MS = 15000;
  var $ = function (id) { return document.getElementById(id); };
  var job = null;
  var lastStatus = null;
  var pollTimer = null;

  function api(path, opts) {
    // Relative, so it works standalone (/) and behind the launcher proxy (/edge/).
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
      if (!st.boto3) {
        missing.textContent = T('boto3 is not installed. Install it to compile in the cloud:') + ' ' + st.install_hint;
        return;
      }
      return loadStacks();
    }).catch(function (e) { setMsg(e.message, true); });
  }

  function loadStacks() {
    var f = form();
    var sel = $('edgeStack');
    return api('api/aws/stacks?' + qs({ profile: f.profile, region: f.region })).then(function (res) {
      sel.replaceChildren();
      res.stacks.forEach(function (s) { sel.appendChild(option(s.name, s.name + ' (' + s.bucket + ')')); });
      if (!res.stacks.length) sel.appendChild(option('', T('No compiler stack found in this region')));
    }).catch(function (e) {
      sel.replaceChildren();
      setMsg(e.message, true);
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
  $('edgeProfile').addEventListener('change', loadStacks);
  $('edgeRegion').addEventListener('change', loadStacks);
  $('edgeSave').addEventListener('click', save);
  // Repaint the JS-written text when the language changes (data-i18n covers the markup).
  DXI18n.onLangChange(function () {
    var first = $('edgeProfile').options[0];
    if (first && !first.value) first.textContent = T('Default credentials');
    var stack = $('edgeStack').options[0];
    if (stack && !stack.value) stack.textContent = T('No compiler stack found in this region');
    if (lastStatus) render(lastStatus);
  });
  loadStatus();
})();
