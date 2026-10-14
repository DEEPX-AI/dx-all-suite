/* DX App — Graph Composer event list: the events of a run once or a Live, filtered by node, event, track id and
   time; a row shows its frame in the result video of its stream (when there is one) and selects its node on the
   canvas; the --events file is offered for download. Events: {seq, frame, time, stream, node, event, track_id, data}
   (dx_app/core/graph_events.py); track_id -1 with data.track_ids ("3,7") is an event of several tracks. Frames count
   per stream, so an event is sought in its stream's video at frame / that video's fps. A component: its owner (graph-run.js, graph-live.js) calls render() after a language
   change. Contract: tests/dx_app/test_graph_logic_browser.py */
window.GraphEvents = (function () {
  'use strict';
  var KEEP = 2000, SHOW = 300;

  function create(host, c, opts) {
    var o = opts || {};
    var st = { events: [], total: 0, truncated: false, partial: false, url: null, videos: [],
      f: { node: '', event: '', track: '', from: '', to: '' } };
    var els = {};

    function uniq(key) {
      var seen = {};
      st.events.forEach(function (e) { if (e[key] != null) seen[e[key]] = true; });
      return Object.keys(seen).sort();
    }

    function matches(e) {
      var f = st.f;
      if (f.node && e.node !== f.node) return false;
      if (f.event && e.event !== f.event) return false;
      if (f.track !== '' && trackIds(e).indexOf(String(Number(f.track))) === -1) return false;
      if (f.from !== '' && !(e.time != null && e.time >= Number(f.from))) return false;
      if (f.to !== '' && !(e.time != null && e.time <= Number(f.to))) return false;
      return true;
    }

    /* The track ids of an event: its track_id, or those of data.track_ids when it is -1 (several tracks). */
    function trackIds(e) {
      if (e.track_id != null && e.track_id >= 0) return [String(e.track_id)];
      var many = e.data && e.data.track_ids;
      if (many == null || many === '') return [];
      return String(many).split(',').map(function (x) { return x.trim(); }).filter(Boolean);
    }

    /* The result video an event is in: the only one, else the one of its stream. */
    function videoOf(e) {
      if (st.videos.length === 1) return st.videos[0];
      for (var i = 0; i < st.videos.length; i++) if (st.videos[i].stream === e.stream) return st.videos[i];
      return null;
    }

    /* Where an event's frame is in its video: the middle of the frame at the video's fps, else the stream time. */
    function frameTime(e) {
      var v = videoOf(e);
      if (!v) return null;
      if (e.frame != null && v.fps) return (e.frame + 0.5) / v.fps;
      return e.time != null ? e.time : null;
    }

    function jump(e) {
      if (o.onSelectNode) o.onSelectNode(e.node);
      var v = videoOf(e), t = frameTime(e);
      if (!v || t == null) return;
      v.video.pause();
      v.video.currentTime = Math.max(0, t);
      v.video.focus();
    }

    function select(id, label, values, key) {
      var sel = c.h('select', { class: 'input', id: id }, [c.h('option', { value: '', text: T('All') })]
        .concat(values.map(function (v) { return c.h('option', { value: v, text: v }); })));
      sel.value = values.indexOf(st.f[key]) === -1 ? '' : st.f[key];
      st.f[key] = sel.value;
      sel.addEventListener('change', function () { st.f[key] = sel.value; renderRows(); });
      return c.h('div', { class: 'fg gc-fg' }, [c.h('label', { for: id, text: label }), sel]);
    }

    function numberFilter(id, label, key, attrs) {
      var el = c.h('input', Object.assign({ type: 'number', class: 'input', id: id, value: st.f[key] }, attrs || {}));
      el.addEventListener('input', function () { st.f[key] = el.value; renderRows(); });
      return c.h('div', { class: 'fg gc-fg' }, [c.h('label', { for: id, text: label }), el]);
    }

    function dataText(d) {
      var keys = Object.keys(d || {});
      return keys.map(function (k) { return k + '=' + (typeof d[k] === 'object' ? JSON.stringify(d[k]) : d[k]); }).join(' ');
    }

    function renderRows() {
      var shown = st.events.filter(matches), rows = shown.slice(-SHOW);
      els.summary.textContent = c.fmt(T('{shown} of {total} events'), { shown: shown.length, total: st.total })
        + (st.truncated || shown.length > SHOW ? ' · ' + T('the list shows the latest; the file has all of them') : '')
        + (st.partial ? ' · ' + T('Only the end of the log was read: the total and the counts are partial.') : '');
      els.tbody.textContent = '';
      rows.forEach(function (e) {
        var t = frameTime(e), canJump = t != null, ids = trackIds(e);
        var go = c.h('button', { type: 'button', class: 'btn btn-ghost btn-sm',
          'aria-label': c.fmt(canJump ? T('Show event {n} in the video') : T('Select node {node}'), { n: e.seq, node: e.node }) },
          [c.icon(canJump ? 'play' : 'graph')]);
        go.addEventListener('click', function () { jump(e); });
        els.tbody.appendChild(c.h('tr', {}, [
          c.h('td', { class: 'gc-num', text: e.time != null ? e.time.toFixed(2) : '-' }),
          c.h('td', { class: 'gc-num', text: e.frame != null ? String(e.frame) : '-' }),
          c.h('td', { text: e.node }), c.h('td', { text: e.event }),
          c.h('td', { class: 'gc-num', text: ids.length ? ids.join(',') : '-' }),
          c.h('td', { class: 'gc-ev-data', text: dataText(e.data) }),
          c.h('td', {}, [go])]));
      });
      els.empty.hidden = rows.length > 0;
    }

    function render() {
      host.textContent = '';
      if (!st.total && !st.events.length) {
        host.hidden = !o.alwaysShow;
        if (o.alwaysShow) host.appendChild(c.h('p', { class: 'gc-help', text: T('No events yet.') }));
        return;
      }
      host.hidden = false;
      var pre = o.idPrefix || 'gc-ev';
      els.summary = c.h('p', { class: 'gc-help gc-ev-summary', role: 'status' });
      var tools = [select(pre + '-node', T('Node'), uniq('node'), 'node'), select(pre + '-event', T('Event'), uniq('event'), 'event'),
        numberFilter(pre + '-track', T('Track id'), 'track', { min: '0', step: '1' }),
        numberFilter(pre + '-from', T('From (s)'), 'from', { min: '0', step: '0.1' }),
        numberFilter(pre + '-to', T('To (s)'), 'to', { min: '0', step: '0.1' })];
      if (st.url) {
        tools.push(c.h('a', { class: 'btn btn-ghost btn-sm gc-ev-download', href: st.url, download: 'events.jsonl' },
          [c.icon('download'), c.h('span', { text: ' ' + T('Download events (JSONL)') })]));
      }
      els.tbody = c.h('tbody');
      els.empty = c.h('p', { class: 'gc-help', text: T('No event matches the filters.') });
      host.appendChild(c.h('h3', { class: 'gc-section-title', text: T('Events') }));
      host.appendChild(c.h('div', { class: 'gc-ev-tools' }, tools));
      host.appendChild(els.summary);
      host.appendChild(c.h('div', { class: 'gc-ev-scroll' }, [c.h('table', { class: 'gc-run-table gc-ev-table' }, [
        c.h('thead', {}, [c.h('tr', {}, [c.h('th', { text: T('Time (s)') }), c.h('th', { text: T('Frame') }),
          c.h('th', { text: T('Node') }), c.h('th', { text: T('Event') }), c.h('th', { text: T('Track id') }),
          c.h('th', { text: T('Details') }), c.h('th', {}, [c.h('span', { class: 'dx-sr-only', text: T('Show') })])])]),
        els.tbody])]));
      host.appendChild(els.empty);
      renderRows();
    }

    var api = {
      /* A finished run: its listing and, for a video result, the videos to seek: [{video, fps, stream}] (stream null
         when the run had one). meta.partial: the events of the log's end only. */
      set: function (events, meta) {
        st.events = (events || []).slice(-KEEP);
        st.total = (meta && meta.total) || st.events.length;
        st.truncated = !!(meta && meta.truncated);
        st.partial = !!(meta && meta.partial);
        st.url = (meta && meta.url) || null;
        st.videos = (meta && meta.videos) || [];
        render();
      },
      /* New events of a running job (poll). */
      append: function (events, total) {
        if (!events || !events.length) { if (total != null && total !== st.total) { st.total = total; if (els.summary) renderRows(); } return; }
        var refill = !st.events.length;
        st.events = st.events.concat(events).slice(-KEEP);
        st.total = total != null ? total : st.events.length;
        if (refill || !els.tbody || !host.contains(els.tbody)) render(); else renderRows();
      },
      lastSeq: function () { return st.events.length ? st.events[st.events.length - 1].seq || 0 : 0; },
      clear: function () {
        st.events = []; st.total = 0; st.url = null; st.videos = []; st.truncated = false; st.partial = false; render();
      },
      /* Draw into another element (the owner rebuilt its panel). */
      attach: function (el) { host = el; render(); },
      state: function () { return st; },
      render: render
    };
    return api;
  }

  return { create: create };
})();
