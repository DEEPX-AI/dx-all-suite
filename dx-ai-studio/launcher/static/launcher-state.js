
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
};

window.DXLauncher._SPLASH_MODULES = [
  { name: 'DX App',       angle: 0,    icon: 'app' },
  { name: 'DX Stream',    angle: 45,   icon: 'stream' },
  { name: 'DX Model Zoo', angle: 90,   icon: 'zoo' },
  { name: 'DX Compiler',  angle: 135,  icon: 'compiler' },
  { name: 'DX EdgeGuide', angle: 180,  icon: 'edgeguide' },
  { name: 'DX Benchmark', angle: 225,  icon: 'benchmark' },
  { name: 'DX Monitor',   angle: 270,  icon: 'monitor' },
  { name: 'DX Agent Dev', angle: 315,  icon: 'agent' },
];

window.DXLauncher._DECODE_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
window.DXLauncher._DECODE_FRAME_INTERVAL = 50;
window.DXLauncher._TRACE_LENGTH_CACHE = new Map();
window.DXLauncher._decodeRAF = null;

window.DXLauncher._orbitalResizeTimer = null;

window.DXLauncher.SUPPORTED_LANGS = ['en', 'ja', 'ko', 'es', 'zh-CN', 'zh-TW'];
window.DXLauncher.LANG_SHORT = { en: 'EN', ja: 'JA', ko: 'KO', es: 'ES', 'zh-CN': '简', 'zh-TW': '繁' };
