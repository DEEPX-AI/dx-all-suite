const _cs = getComputedStyle(document.documentElement);
const _cv = k => _cs.getPropertyValue(k).trim();
const $ = id => document.getElementById(id);
const esc = s => { const d = document.createElement('div'); d.textContent = s; return d.innerHTML };
function api(url, opts) { return fetch(url, opts).then(r => r.json()).catch(e => ({error: e.message})) }

/* 온도 색상 */
function tempColor(t) { return t < 40 ? _cv('--status-ok') : t < 55 ? _cv('--status-warn') : _cv('--status-error') }

/* 글로벌 상태 */
const S = {
  chartMode: 'temp',
  rtData: [],
  rtView: 'rt',
  accRange: '5m',
  sseSource: null,
  cpuCores: 4,
  thresholds: {},
  isMock: false,
  lastHW: null,
  lastSystemInfo: null,
  lastEvents: [],
  lastEventCount: 0
};

/* 버퍼 상한: 12시간 (1.5초 간격) */
const RT_MAX = 28800;

/* i18n helper */
function T(en, ko) {
  if (typeof DXI18n !== 'undefined') return DXI18n.T(en, ko);
  return en;
}

function getLang() { return (typeof DXI18n !== 'undefined') ? DXI18n.lang : (localStorage.getItem('dx-lang') || 'en'); }
function localeForLang(lang) { var map = { en: 'en-US', ko: 'ko-KR', ja: 'ja-JP', 'zh-CN': 'zh-CN', 'zh-TW': 'zh-TW', es: 'es-ES' }; return map[lang || getLang()] || 'en-US'; }
function formatTime(ts) { var d = ts instanceof Date ? ts : new Date(ts); return d.toLocaleTimeString(localeForLang(), { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }); }

var CHART_LABEL_KEYS = { temp: 'NPU Temp (°C)', volt: 'Voltage (mV)', clock: 'Clock (MHz)', dram: 'NPU DRAM (%)', util: 'NPU Util (%)', ctemp: 'Core Temp (°C)', cpu: 'CPU Load', mem: 'Memory (%)', cpucores: 'CPU Cores (%)' };
function metricLabel(key) { return T(CHART_LABEL_KEYS[key] || key); }
/* 큰 숫자 옆 단위. 차트 제목 괄호 안 단위와 같다. CPU Load 는 load average 라 단위가 없다 (release audit M-2). */
var METRIC_UNITS = { temp: '°C', volt: ' mV', clock: ' MHz', dram: '%', util: '%', ctemp: '°C', mem: '%', cpucores: '%' };
var METRIC_DECIMALS = { cpu: 2, volt: 0, clock: 0 };  /* 상태 카드와 같은 자리수 — "0.7" 옆 카드는 "0.73" 이었다 */
function metricValue(key, v) {
  if (v == null) return T('N/A');
  var d = METRIC_DECIMALS[key] != null ? METRIC_DECIMALS[key] : 1;
  return v.toFixed(d) + (METRIC_UNITS[key] || '');
}
function statusLabel(key) { return T(key); }
function eventCountLabel(count) { var tmpl = T('{count} events'); return tmpl.replace('{count}', count); }

/* 임계치 기반 상태 판정 */
function getStatus(key, value) {
  var th = S.thresholds[key];
  if (!th || th.warn == null || th.crit == null) return 'none';
  if (value >= th.crit) return 'crit';
  if (value >= th.warn) return 'warn';
  return 'ok';
}

/* 상태별 CSS 클래스 */
function statusClass(status) {
  if (status === 'crit') return 'st-crit';
  if (status === 'warn') return 'st-warn';
  if (status === 'ok') return 'st-ok';
  return '';
}

/* 상태별 배지 아이콘 (sprite, 아이콘 체계 단계 5) — 모양 + 색 (색은 st-* 클래스). */
function _mIco(name) {
  return (typeof window !== 'undefined' && typeof window.DXIcon === 'function') ? window.DXIcon(name) : '';
}
/* 아이콘 + 글자. 실제 DOM 이 아니면 (테스트의 가짜 엘리먼트) 글자만. */
function _mLabel(el, name, text) {
  if (typeof window !== 'undefined' && window.DXIcon && window.DXIcon.label && el && el.appendChild && typeof document !== 'undefined' && document.createElementNS) {
    return window.DXIcon.label(el, name, text);
  }
  el.textContent = text;
  return el;
}
function statusIcon(status) {
  if (status === 'crit') return _mIco('x');
  if (status === 'warn') return _mIco('alert');
  if (status === 'ok') return _mIco('check');
  return '';
}

/* NPU 차트 키 목록 */
const NPU_CHART_KEYS = ['temp', 'volt', 'clock', 'dram', 'util', 'ctemp'];
/* System 차트 키 목록 */
const SYS_CHART_KEYS = ['cpu', 'mem', 'cpucores'];

/* 차트 키 → 임계치 키 매핑 */
const CHART_THRESHOLD_MAP = {
  temp: 'npu_temp', ctemp: 'core_temp', dram: 'npu_dram',
  cpu: 'cpu_load', mem: 'memory'
};
