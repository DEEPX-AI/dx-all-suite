
window.DXLauncher = window.DXLauncher || {};

window.DXLauncher._splashTimers = [];
window.DXLauncher._splashActive = false;
window.DXLauncher._deferredLauncherWorkStarted = false;
window.DXLauncher._launcherCoreStarted = false;
window.DXLauncher._studioReadyPromise = null;
window.DXLauncher._studioReadyResolved = false;

window.DXLauncher.currentApp = null;
window.DXLauncher.APP_PATHS = {
  app: '/app/',
  stream: '/stream/',
  zoo: '/zoo/',
  compiler: '/compiler/',
  planner: '/planner/',
  benchmark: '/benchmark/',
  dx_monitor: '/dx_monitor/',
  agent: '/agent/',
  edge: '/edge/',
};


window.DXLauncher._DECODE_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
window.DXLauncher._DECODE_FRAME_INTERVAL = 50;
window.DXLauncher._TRACE_LENGTH_CACHE = new Map();
window.DXLauncher._decodeRAF = null;

window.DXLauncher.SUPPORTED_LANGS = ['en', 'ja', 'ko', 'es', 'zh-CN', 'zh-TW'];
window.DXLauncher.LANG_SHORT = { en: 'EN', ja: 'JA', ko: 'KO', es: 'ES', 'zh-CN': '简', 'zh-TW': '繁' };
