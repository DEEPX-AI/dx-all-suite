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
 * This used to render a five-across model row in a Models section. The section
 * is gone — the home is a workspace, and 348 models belong in the module that
 * exists to browse them. What survives is the one number worth seeing from the
 * front door, on the card that opens that module.
 */
(function () {
  'use strict';

  var ns = window.DXLauncher = window.DXLauncher || {};

  /* card data-app → the key checkHealth() files it under */
  var HEALTH_KEY = {
    app: 'app', stream: 'stream', zoo: 'zoo', compiler: 'compiler',
    planner: 'planner', benchmark: 'benchmark', dx_monitor: 'monitor', agent: 'agent'
  };

  function $(id) { return document.getElementById(id); }
  function _t(key) {
    return (window.DXI18n && window.DXI18n.T) ? window.DXI18n.T(key) : key;
  }

  /* ── the catalogue's size, on the card that opens it ─────── */

  var _models = null;

  /* 각 모듈이 자기 숫자를 든다. 여덟 행이 이름 + 산문 한 줄로만 되어 있으면 서로
     구별되지 않아 목록이 한 덩어리로 읽힌다.

     모듈마다 함수를 한 벌씩 두지 않는다 — 다음 모듈이 생길 때 또 한 벌이 늘고,
     그건 이 저장소에서 이미 두 번 고친 모양이다. 응답 모양은 제각각이라 파싱은
     각자 갖되(`pick`), 그리는 일은 _paintFacts 한 곳에서 한다.

     compiler 와 planner 는 없다. 셀 API 가 없고(각각 listdir/mkdir, hb 뿐),
     숫자를 붙이자고 엔드포인트를 만드는 것은 이 작업이 아니다. 그 둘은 출하 시
     산문을 유지한다 — 비대칭을 그대로 두는 편이 정직하다.
     계약: tests/launcher/test_home_module_facts.py */
  var MODULE_FACTS = [
    { app: 'zoo', url: '/zoo/api/catalog', pick: function (d) {
        var models = (d && d.models) || (Array.isArray(d) ? d : []);
        if (!models.length) return null;
        var tasks = {};
        models.forEach(function (m) { var t = (m.display || {}).task; if (t) tasks[t] = 1; });
        _models = models;
        _paintMeasuredCount(models);
        /* 위젯 (home-widgets.js) 은 같은 카탈로그를 다시 받지 않고 이것을 쓴다. */
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

  /* 그린 값은 언어가 바뀌면 다시 그려야 한다 (JS 로 쓰므로 data-i18n 이 닿지 않는다). */
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

  /* 숫자 + 단위. 단위가 수량사 (개 · 件 · 個 · 个 · 類 · 类) 로 시작하면 붙여 쓴다 — "354개", "28件" (release audit
     L-12 · L-28). 그 밖 (models · グループ …) 은 띄운다. */
  function _count(n, unitKey) {
    var unit = _t(unitKey);
    return String(n) + (/^[개件個个类類]/.test(unit) ? '' : ' ') + unit;
  }
  ns._countLabel = _count;

  function _fmt(n) {
    return Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  }
  /* 오른쪽 위젯의 한 줄. 표는 home 을 떠났다 (spec §5.6) — 무엇이 얼마나 빠른지는
     Benchmark 와 Model Zoo 가 보여준다. 여기는 이 장치에서 몇 개를 쟀는지만 말한다. */
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
      if (_facts[f.app]) return;            // 이미 알고 있으면 다시 묻지 않는다
      fetch(f.url).then(function (r) { return r.json(); })
        .then(function (data) {
          var parts = f.pick(data);
          if (!parts || !parts.length) return;
          _facts[f.app] = parts;
          _paintFacts();
        })
        .catch(function () {
          /* 그 모듈이 돌지 않는다. 카드는 출하 시 설명을 유지한다 — 서버가 떠
             있든 아니든 참인 문장이다. 한 모듈의 실패가 나머지를 막지 않는다. */
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

    /* "start →" 여덟 개는 행동 유도가 여덟 개라는 뜻이고, 그러면 아무것도 행동
       유도가 아니다. 상태 라벨도 같다 — 전부 돌 때(평상시) "Running" 여덟 개는
       아무것도 말하지 않으면서 칸마다 같은 폭을 차지한다. 그러니 예외가 있을 때만
       말한다.
       점은 그대로 둔다 — 점은 한 글자도 차지하지 않으면서 상태를 말한다.
       계약: tests/launcher/test_home_density_browser.py */
    var exceptional = down > 0;

    cards.forEach(function (card) {
      var key = HEALTH_KEY[card.dataset.app] || card.dataset.app;
      var alive = !!(health[key] && health[key].alive);
      card.classList.toggle('is-up', alive);
      /* 꺼졌다고 확인된 것만 흐리게 한다. 'is-up 이 없으면' 으로 쓰면 첫 health 응답
         전 (최대 5초) 에 여덟 개가 모두 흐리다 (home-stage.css, spec 2026-09-23 §5.3). */
      card.classList.toggle('is-down', !alive);
      var line = card.querySelector('[data-role="state"]');
      if (line) {
        line.textContent = (exceptional && alive) ? _t('Running') : '';
        line.className = 'card-state' + (alive ? ' is-alive' : '');
      }
    });
  }

  /* home 은 모든 경로에서 문서에 남아 있다. 그 숫자 (zoo catalog 2.5 MB 포함) 는 home 이 처음 보일 때 받는다 —
     /app/ · /compiler/ 로 바로 연 사용자는 home 을 보지 않았는데 화면마다 catalog 를 받았다 (2026-10-11 성능 감사).
     계약: tests/launcher/test_home_facts_deferred_browser.py */
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
  /* 카드의 data-app 과 health 키가 다르다(dx_monitor → monitor). 계약 테스트가
     그 매핑을 손으로 베끼면 조용히 어긋나므로, 진짜를 내보낸다. */
  ns._HEALTH_KEY = HEALTH_KEY;
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
