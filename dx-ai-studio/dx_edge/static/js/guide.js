/* DX Cloud — AWS Console guide.
   Renders static/guide/content.<lang>.json: a guide switch, a step TOC with scroll-spy, and steps with a console
   path, instructions, a zoomable screenshot and copyable commands. Content text is only ever set with textContent;
   the inline markup `code`, **strong** and [text](https://…) is turned into elements by inlineInto(). */
(function () {
  'use strict';

  var BASE = '/static/guide/';
  var GUIDE_KEY = 'dx-cloud-guide';
  var main = document.getElementById('guideMain');
  var els = {
    back: document.getElementById('guideBack'),
    title: document.getElementById('guideTitle'),
    lead: document.getElementById('guideLead'),
    sw: document.getElementById('guideSwitch'),
    tocTitle: document.getElementById('guideTocTitle'),
    toc: document.getElementById('guideToc'),
    jump: document.getElementById('guideJump'),
    body: document.getElementById('guideBody'),
    zoom: document.getElementById('guideZoom'),
    zoomImg: document.getElementById('guideZoomImg'),
    zoomCap: document.getElementById('guideZoomCap'),
    zoomClose: document.getElementById('guideZoomClose')
  };
  var cache = {};
  var data = null;
  var current = null;
  var spy = null; // pending animation frame of the scroll-spy

  function lang() {
    return (window.DXI18n && DXI18n.lang) || 'en';
  }

  function load(code) {
    if (cache[code]) return Promise.resolve(cache[code]);
    return fetch(BASE + 'content.' + code + '.json').then(function (r) {
      if (!r.ok) throw new Error(r.status);
      return r.json();
    }).then(function (j) { cache[code] = j; return j; });
  }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function icon(name) {
    return DXIcon.el(name);
  }

  // `code`, **strong** and [text](https://…) only; everything else stays plain text.
  // The pattern is built per call: a shared /g regex would lose its lastIndex in the **strong** recursion.
  var INLINE = '`([^`]+)`|\\*\\*([^*]+)\\*\\*|\\[([^\\]]+)\\]\\((https://[^)\\s]+)\\)';

  function inlineInto(node, text) {
    var re = new RegExp(INLINE, 'g');
    var last = 0;
    var m;
    while ((m = re.exec(text))) {
      if (m.index > last) node.appendChild(document.createTextNode(text.slice(last, m.index)));
      if (m[1] != null) {
        node.appendChild(el('code', null, m[1]));
      } else if (m[2] != null) {
        inlineInto(node.appendChild(el('strong')), m[2]);
      } else {
        var a = el('a', null, m[3]);
        a.href = m[4];
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
        node.appendChild(a);
      }
      last = re.lastIndex;
    }
    if (last < text.length) node.appendChild(document.createTextNode(text.slice(last)));
    return node;
  }

  function anchor(guideId, stepId) {
    return guideId + '-' + stepId;
  }

  function parseHash() {
    var h = decodeURIComponent((location.hash || '').slice(1));
    if (!data || !h) return null;
    for (var i = 0; i < data.guides.length; i++) {
      var g = data.guides[i];
      if (h === g.id) return { guide: g.id, step: null };
      if (h.indexOf(g.id + '-') === 0) return { guide: g.id, step: h };
    }
    return null;
  }

  function storedGuide() {
    try { return localStorage.getItem(GUIDE_KEY); } catch (_) { return null; }
  }

  // execCommand fallback: plain-http hosts have no navigator.clipboard, and writeText can be refused.
  function copyFallback(text) {
    var ta = el('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.className = 'guide-copy-buffer';
    document.body.appendChild(ta);
    ta.select();
    var ok = false;
    try { ok = document.execCommand('copy'); } catch (_) { ok = false; }
    ta.remove();
    return ok ? Promise.resolve() : Promise.reject(new Error('copy'));
  }

  function copyText(text) {
    if (!navigator.clipboard || !window.isSecureContext) return copyFallback(text);
    return navigator.clipboard.writeText(text).catch(function () { return copyFallback(text); });
  }

  function commandBlock(code) {
    var ui = data.ui;
    var box = el('div', 'guide-cmd');
    var pre = el('pre', 'guide-cmd-pre');
    pre.appendChild(el('code', null, code));
    var btn = el('button', 'btn btn-sm btn-ghost guide-copy');
    btn.type = 'button';
    btn.appendChild(icon('copy'));
    var label = btn.appendChild(el('span', null, ui.copy));
    btn.addEventListener('click', function () {
      copyText(code).then(function () { label.textContent = ui.copied; }, function () {
        label.textContent = ui.copyFailed;
      }).then(function () {
        setTimeout(function () { label.textContent = data.ui.copy; }, 1600);
      });
    });
    box.appendChild(btn);
    box.appendChild(pre);
    return box;
  }

  function stepCard(guide, step, n) {
    var ui = data.ui;
    var id = anchor(guide.id, step.id);
    var card = el('section', 'card guide-step');
    card.id = id;
    card.setAttribute('aria-labelledby', id + '-t');

    var head = el('div', 'guide-step-head');
    head.appendChild(el('span', 'guide-step-no', String(n)));
    var h = el('h3', 'guide-step-title', step.title);
    h.id = id + '-t';
    head.appendChild(h);
    var link = el('a', 'guide-step-link', '#');
    link.href = '#' + id;
    link.setAttribute('aria-label', step.title);
    head.appendChild(link);
    card.appendChild(head);

    if (step.path) {
      var path = el('p', 'guide-path');
      path.appendChild(el('span', 'badge guide-path-label', ui.consolePath));
      var trail = el('span', 'guide-crumbs');
      step.path.forEach(function (p, i) {
        if (i) trail.appendChild(el('span', 'guide-crumb-sep', '›'));
        trail.appendChild(el('span', 'guide-crumb', p));
      });
      path.appendChild(trail);
      card.appendChild(path);
    }

    var list = el('ol', 'guide-items');
    step.items.forEach(function (t) { list.appendChild(inlineInto(el('li'), t)); });
    card.appendChild(list);

    if (step.note) {
      var note = el('div', 'guide-note');
      note.appendChild(icon('info'));
      var p = el('p');
      p.appendChild(el('strong', null, ui.note + ' — '));
      inlineInto(p, step.note);
      note.appendChild(p);
      card.appendChild(note);
    }

    (step.commands || []).forEach(function (c) { card.appendChild(commandBlock(c)); });

    if (step.image) {
      var fig = el('figure', 'guide-shot');
      var btn = el('button', 'guide-shot-btn');
      btn.type = 'button';
      btn.title = ui.zoom;
      var img = el('img');
      img.src = BASE + 'img/' + step.image.src;
      img.alt = step.image.alt;
      img.width = step.image.width;
      img.height = step.image.height;
      img.loading = 'lazy';
      img.decoding = 'async';
      btn.appendChild(img);
      btn.addEventListener('click', function () { openZoom(img.src, step.image.alt); });
      fig.appendChild(btn);
      fig.appendChild(el('figcaption', 'guide-shot-cap', step.image.alt));
      card.appendChild(fig);
    }
    return card;
  }

  function openZoom(src, caption) {
    els.zoomImg.src = src;
    els.zoomImg.alt = caption;
    els.zoomCap.textContent = caption;
    if (typeof els.zoom.showModal === 'function') els.zoom.showModal();
  }

  function render(target) {
    var ui = data.ui;
    var guide = data.guides.filter(function (g) { return g.id === target; })[0] || data.guides[0];
    current = guide.id;
    try { localStorage.setItem(GUIDE_KEY, current); } catch (_) { /* storage blocked */ }

    document.title = 'DX Cloud — ' + ui.title;
    els.back.textContent = ui.back;
    els.title.textContent = ui.title;
    els.lead.textContent = ui.lead;
    els.tocTitle.textContent = ui.onThisPage;
    els.zoomClose.setAttribute('aria-label', ui.close);
    els.sw.setAttribute('aria-label', ui.guide);

    els.sw.textContent = '';
    data.guides.forEach(function (g) {
      var b = el('a', 'guide-tab', g.name);
      b.href = '#' + g.id;
      b.setAttribute('role', 'tab');
      b.setAttribute('aria-selected', String(g.id === current));
      b.prepend(icon(g.id === 'compiler' ? 'compiler' : 'cloud'));
      els.sw.appendChild(b);
    });

    els.toc.textContent = '';
    els.jump.textContent = '';
    els.body.textContent = '';
    var intro = el('div', 'guide-intro');
    intro.appendChild(el('h2', 'guide-intro-title', guide.title));
    intro.appendChild(inlineInto(el('p'), guide.intro));
    els.body.appendChild(intro);

    var n = 0;
    guide.sections.forEach(function (sec) {
      var li = el('li', 'guide-toc-sec');
      li.appendChild(el('span', 'guide-toc-sec-title', sec.title));
      var ol = el('ol', 'guide-toc-steps');
      var group = el('optgroup');
      group.label = sec.title;
      var block = el('section', 'guide-sec');
      block.appendChild(el('h2', 'guide-sec-title', sec.title));
      sec.steps.forEach(function (step) {
        n += 1;
        var id = anchor(guide.id, step.id);
        var a = el('a', 'guide-toc-link');
        a.href = '#' + id;
        a.dataset.target = id;
        a.appendChild(el('span', 'guide-toc-no', String(n)));
        a.appendChild(el('span', null, step.title));
        ol.appendChild(el('li')).appendChild(a);
        var opt = el('option', null, n + '. ' + step.title);
        opt.value = id;
        group.appendChild(opt);
        block.appendChild(stepCard(guide, step, n));
      });
      li.appendChild(ol);
      els.toc.appendChild(li);
      els.jump.appendChild(group);
      els.body.appendChild(block);
    });
    spyNow();
  }

  function setActive(id) {
    els.toc.querySelectorAll('.guide-toc-link').forEach(function (a) {
      if (a.dataset.target === id) a.setAttribute('aria-current', 'step');
      else a.removeAttribute('aria-current');
    });
    if (id && els.jump.value !== id) els.jump.value = id;
  }

  // Scroll-spy: the active step is the last one whose top has passed the upper third of the scrolling <main>.
  function spyNow() {
    spy = null;
    var steps = els.body.querySelectorAll('.guide-step');
    if (!steps.length) return;
    var line = main.getBoundingClientRect().top + main.clientHeight / 3;
    var id = steps[0].id;
    for (var i = 0; i < steps.length; i++) {
      if (steps[i].getBoundingClientRect().top > line) break;
      id = steps[i].id;
    }
    setActive(id);
  }

  function goTo(step) {
    var target = step && document.getElementById(step);
    if (target) {
      target.scrollIntoView({ block: 'start' });
      setActive(step);
    } else {
      main.scrollTop = 0;
    }
  }

  function route() {
    var h = parseHash();
    var want = h ? h.guide : (current || storedGuide());
    if (want !== current || !els.body.firstChild) render(want);
    goTo(h && h.step);
  }

  function start() {
    var code = lang();
    var keep = current;
    load(code).catch(function () { return load('en'); }).then(function (j) {
      data = j;
      document.documentElement.lang = j.lang;
      current = null;
      var h = parseHash();
      render(h ? h.guide : (keep || storedGuide()));
      goTo(h && h.step);
    }).catch(function () {
      els.body.textContent = '';
      els.body.appendChild(el('p', 'guide-error', 'The guide could not be loaded.'));
    });
  }

  main.addEventListener('scroll', function () {
    if (!spy) spy = requestAnimationFrame(spyNow);
  }, { passive: true });
  window.addEventListener('hashchange', function () { if (data) route(); });
  els.jump.addEventListener('change', function () { location.hash = els.jump.value; });
  els.zoomClose.addEventListener('click', function () { els.zoom.close(); });
  els.zoom.addEventListener('click', function (e) { if (e.target === els.zoom) els.zoom.close(); });
  if (window.DXI18n) DXI18n.onLangChange(start);
  start();
})();
