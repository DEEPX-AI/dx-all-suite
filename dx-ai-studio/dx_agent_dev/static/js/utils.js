/* DX Agent Dev — Utility functions (dx_monitor/static/js/utils.js 미러) */
const $ = id => document.getElementById(id);
const esc = s => { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; };

function api(url, opts) {
  return fetch(url, opts).then(r => r.json()).catch(e => ({ error: e.message }));
}

/* i18n helper — DXI18n(shared/i18n.js)에 위임, 없으면 en 폴백 */
function T(en, ko) {
  if (typeof DXI18n !== 'undefined') return DXI18n.T(en, ko);
  return en;
}

function getLang() {
  return (typeof DXI18n !== 'undefined') ? DXI18n.lang : (localStorage.getItem('dx-lang') || 'en');
}
