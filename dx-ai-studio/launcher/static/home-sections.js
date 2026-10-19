/* ── Workspace state ──────────────────────────────────────────
 *
 * Fills the two things on the home that are facts rather than layout: what the
 * catalogue holds, and which modules are up.
 *
 * Neither adds a source of truth. The count comes from the catalogue the Model
 * Zoo already serves; the state comes from the health poll `checkHealth()`
 * already runs. A second poller would mean two answers to "is this module up",
 * and they would eventually disagree.
 *
 * The home is a workspace, so it shows only the one number worth seeing from
 * the front door, on the card that opens that module; browsing models belongs
 * in Model Zoo.
 */
(function () {
  'use strict';

  var ns = window.DXLauncher = window.DXLauncher || {};

  /* card data-app → the key checkHealth() files it under */
  var HEALTH_KEY = {
    app: 'app', stream: 'stream', zoo: 'zoo', compiler: 'compiler',
    planner: 'planner', benchmark: 'benchmark', dx_monitor: 'monitor', agent: 'agent',
    edge: 'edge'
  };

  function $(id) { return document.getElementById(id); }
  function _t(key) {
    return (window.DXI18n && window.DXI18n.T) ? window.DXI18n.T(key) : key;
  }

  /* ── the catalogue's size, on the card that opens it ─────── */

  var _models = null;

  /* Each module carries its own number. Eight rows of name + one line of prose do
     not tell apart and read as one block.

     There is no function per module: response shapes differ, so each has its own
     parser (`pick`), but painting happens in one place, _paintFacts.

     compiler and planner have none: they expose no count API, so they keep their
     shipped prose.
     Contract: tests/launcher/test_home_module_facts.py */
  var MODULE_FACTS = [
    { app: 'zoo', url: '/zoo/api/catalog', pick: function (d) {
        var models = (d && d.models) || (Array.isArray(d) ? d : []);
        if (!models.length) return null;
        var tasks = {};
        models.forEach(function (m) { var t = (m.display || {}).task; if (t) tasks[t] = 1; });
        _models = models;
        _paintMeasuredCount(models);
        /* The widgets (home-widgets.js) use this instead of fetching the same catalog again. */
        ns._homeCatalog = models;
        document.dispatchEvent(new CustomEvent('dx-home-catalog', { detail: models }));
        return [[models.length, 'models'], [Object.keys(tasks).length, 'tasks']];
      } },
    { app: 'app', url: '/app/api/demos', pick: function (d) {
        var demos = (d && d.demos) || [];
        if (!demos.length) return null;
        var groups = {};
        demos.forEach(function (x) { if (x.group) groups[x.group] = 1; });
        return [[demos.length, 'demos'], [Object.keys(groups).length, 'groups']];
      } },
    { app: 'stream', url: '/stream/api/demos', pick: function (d) {
        var n = Array.isArray(d) ? d.length : 0;
        return n ? [[n, 'demos']] : null;
      } },
    { app: 'agent', url: '/agent/api/agent/showcases', pick: function (d) {
        var n = ((d && d.showcases) || []).length;
        return n ? [[n, 'showcases']] : null;
      } },
    { app: 'benchmark', url: '/benchmark/api/results', pick: function (d) {
        var rows = Array.isArray(d) ? d : [];
        if (!rows.length) return null;
        var runs = 0;
        rows.forEach(function (r) { runs += ((r && r.runs) || []).length; });
        return [[rows.length, 'platforms'], [runs, 'runs']];
      } },
    { app: 'dx_monitor', url: '/dx_monitor/api/hw_status', pick: function (d) {
        var npu = ((d && d.npus) || [])[0];
        if (!npu) return null;
        var out = [];
        if (npu.cores) out.push([npu.cores, 'cores']);
        var temps = npu.temperatures || [];
        if (temps.length) {
          out.push([Math.round(Math.max.apply(null, temps)) + '\u00B0C', '']);
        }
        return out.length ? out : null;
      } },
  ];

  /* Painted values must be repainted on a language change (written by JS, so data-i18n does not reach them). */
  var _facts = {};

  function _paintFacts() {
    MODULE_FACTS.forEach(function (f) {
      var parts = _facts[f.app];
      if (!parts) return;
      var card = document.querySelector('.orbital-card[data-app="' + f.app + '"] .card-desc');
      if (!card) return;
      card.removeAttribute('data-i18n');   // a live number is not a dictionary key
      card.textContent = parts.map(function (p) {
        return p[1] ? _count(p[0], p[1]) : String(p[0]);
      }).join(' \u00B7 ');
    });
  }

  function _paintCount() { _paintFacts(); }

  /* Number + unit. A unit that starts with a CJK counter word (see the regex) is joined without
     a space, e.g. "28件". Others (models · グループ …) get a space. */
  function _count(n, unitKey) {
    var unit = _t(unitKey);
    return String(n) + (/^[개件個个类類]/.test(unit) ? '' : ' ') + unit;
  }
  ns._countLabel = _count;

  function _fmt(n) {
    return Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  }
  /* One line in the right-hand widget. Speed is shown by Benchmark and Model Zoo; this
     line only says how many models were measured on this device. */
  function _paintMeasuredCount(models) {
    var note = $('measuredCount');
    if (!note) return;
    var measured = 0;
    var tasks = {};
    models.forEach(function (m) {
      var d = m.display || {};
      if (d.task) tasks[d.task] = 1;
      if ((m.performance || {}).fps) measured += 1;
    });
    note.textContent = _count(_fmt(measured), 'measured') + ' · ' + _count(Object.keys(tasks).length, 'tasks');
  }

  function loadCatalogueSize() {
    MODULE_FACTS.forEach(function (f) {
      if (_facts[f.app]) return;            // do not ask again once known
      fetch(f.url).then(function (r) { return r.json(); })
        .then(function (data) {
          var parts = f.pick(data);
          if (!parts || !parts.length) return;
          _facts[f.app] = parts;
          _paintFacts();
        })
        .catch(function () {
          /* That module is not running. The card keeps its shipped description, which is
             true whether or not the server is up. One module failing does not block the rest. */
        });
    });
  }

  /* ── which modules are up ────────────────────────────────── */

  function refreshModuleState() {
    var health = ns._healthStatus;
    if (!health) return;

    var cards = document.querySelectorAll('.orbital-card[data-app]');
    var down = 0;
    cards.forEach(function (card) {
      var key = HEALTH_KEY[card.dataset.app] || card.dataset.app;
      if (!(health[key] && health[key].alive)) down += 1;
    });

    /* Eight "start →" links are eight calls to action, which means none. Status labels
       likewise: when everything runs (the usual case) eight "Running" labels say nothing
       and take space in every row. So speak only for exceptions.
       The dot stays — it shows status without taking a character.
       Contract: tests/launcher/test_home_density_browser.py */
    var exceptional = down > 0;

    cards.forEach(function (card) {
      var key = HEALTH_KEY[card.dataset.app] || card.dataset.app;
      var alive = !!(health[key] && health[key].alive);
      card.classList.toggle('is-up', alive);
      /* Dim only what is confirmed down. Keying on "no is-up" would dim all eight before
         the first health response (up to 5s) (home-stage.css). */
      card.classList.toggle('is-down', !alive);
      var line = card.querySelector('[data-role="state"]');
      if (line) {
        line.textContent = (exceptional && alive) ? _t('Running') : '';
        line.className = 'card-state' + (alive ? ' is-alive' : '');
      }
    });
  }

  /* home stays in the document on every route. Its numbers (including the 2.5 MB zoo catalog) load
     when home is first shown, so users who open /app/ or /compiler/ directly do not fetch the catalog.
     Contract: tests/launcher/test_home_facts_deferred_browser.py */
  function _whenHomeShows(fn) {
    var body = document.body;
    if (body.classList.contains('home-visible')) { fn(); return; }
    var mo = new MutationObserver(function () {
      if (!body.classList.contains('home-visible')) return;
      mo.disconnect();
      fn();
    });
    mo.observe(body, { attributes: true, attributeFilter: ['class'] });
  }

  function init() {
    _whenHomeShows(loadCatalogueSize);
    refreshModuleState();
    /* Piggyback on the health poll's cadence instead of adding one. */
    setInterval(refreshModuleState, 5000);
    /* Both are written in JS, so data-i18n never reaches them: a language
       change has to redraw. The count repaints from the held numbers rather
       than asking the zoo again. */
    if (window.DXI18n && DXI18n.onLangChange) {
      DXI18n.onLangChange(function () {
        _paintCount();
        if (_models) _paintMeasuredCount(_models);
        refreshModuleState();
      });
    }
  }

  ns.refreshModuleState = refreshModuleState;
  /* A card's data-app and its health key differ (dx_monitor → monitor). A contract test
     that copied the mapping by hand would drift silently, so the real one is exported. */
  ns._HEALTH_KEY = HEALTH_KEY;
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
