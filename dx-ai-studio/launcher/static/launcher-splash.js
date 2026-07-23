
(function() {
  var ns = window.DXLauncher;

  var _MODULE_ICONS = {
    app: '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/><circle cx="14" cy="10" r="1.5"/></svg>',
    stream: '<svg viewBox="0 0 24 24"><circle cx="12" cy="10" r="5"/><circle cx="12" cy="10" r="2"/><path d="M4 18 Q8 14 12 16 Q16 18 20 14"/></svg>',
    zoo: '<svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>',
    compiler: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/><path d="M12 4 V8 M12 16 V20 M4 12 H8 M16 12 H20"/><circle cx="12" cy="12" r="3"/></svg>',
    edgeguide: '<svg viewBox="0 0 24 24"><rect x="6" y="6" width="12" height="12" rx="2"/><line x1="6" y1="2" x2="6" y2="6"/><line x1="18" y1="2" x2="18" y2="6"/><line x1="6" y1="18" x2="6" y2="22"/><line x1="18" y1="18" x2="18" y2="22"/><path d="M20 12 L23 12"/></svg>',
    benchmark: '<svg viewBox="0 0 24 24"><path d="M12 2 A10 10 0 0 1 22 12"/><path d="M12 2 A10 10 0 0 0 2 12"/><line x1="12" y1="12" x2="17" y2="7"/><circle cx="12" cy="12" r="2"/></svg>',
    monitor: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="12" rx="2"/><path d="M8 19h8M12 15v4"/><path d="M7 9l3 3 4-4 3 3"/></svg>',
    agent: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 9l3 3-3 3M13 15h4"/></svg>',
  };
  ns._MODULE_ICONS = _MODULE_ICONS;

  function initSplashV2() {
    if (sessionStorage.getItem('dx-splash-seen')) {
      var ov = document.getElementById('splashOverlay');
      if (ov) ov.remove();
      ns._splashActive = false;
      return false;
    }

    ns._splashActive = true;
    // Conceal (not remove) the gate under the full-screen splash so an early skip can
    // re-show it while the studio is still booting instead of blanking the screen.
    if (typeof ns.hideStudioBootGate === 'function') ns.hideStudioBootGate({ conceal: true });
    var isSmall = window.innerWidth < 400;
    var totalDuration = isSmall ? 8500 : 17500;

    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      ns._splashTimers.push(setTimeout(skipSplash, 2000));
      return true;
    }

    _createCircuitTraces();
    _createParticles(isSmall ? 8 : 15);

    ns._splashTimers.push(setTimeout(function() {
      var scanline = document.querySelector('.splash-scanline');
      if (scanline) scanline.classList.add('visible');
    }, 2500));

    ns._splashTimers.push(setTimeout(function() { _animateLogoGlitch(); }, 500));
    ns._splashTimers.push(setTimeout(function() { _animateLogoStabilize(); }, 1800));
    ns._splashTimers.push(setTimeout(function() { _animateLogoLock(); }, 2400));

    ns._splashTimers.push(setTimeout(function() {
      var sub = document.getElementById('splashSubtitle');
      if (sub) sub.classList.add('typing');
    }, 2800));

    if (!isSmall) {
      var beamSvg = document.getElementById('splashBeams');
      if (beamSvg) beamSvg.setAttribute('viewBox', '0 0 ' + window.innerWidth + ' ' + window.innerHeight);
      ns._SPLASH_MODULES.forEach(function(mod, i) {
        ns._splashTimers.push(setTimeout(function() { _bootModule(mod, i); }, 4000 + i * 500));
      });
    } else {
      var area = document.getElementById('splashModulesArea');
      if (area) {
        ns._SPLASH_MODULES.forEach(function(mod, i) {
          ns._splashTimers.push(setTimeout(function() {
            var el = document.createElement('div');
            el.className = 'splash-hud-frame';
            var name = document.createElement('div');
            name.className = 'splash-module-name';
            name.textContent = mod.name;
            name.style.width = 'auto';
            el.appendChild(name);
            area.appendChild(el);
          }, 4000 + i * 200));
        });
      }
    }

    ns._splashTimers.push(setTimeout(_showEnergyGauge, isSmall ? 4000 : 8200));
    ns._splashTimers.push(setTimeout(_activateCore, isSmall ? 4500 : 11000));
    ns._splashTimers.push(setTimeout(_triggerWarpJump, isSmall ? 6000 : 14000));
    ns._splashTimers.push(setTimeout(_showProceedPrompt, totalDuration));
    return true;
  }

  function skipSplash(manual) {
    if (manual === undefined) manual = false;
    var ov = document.getElementById('splashOverlay');
    if (!ov || ov.classList.contains('fade-out')) return;

    ns._splashTimers.forEach(function(id) { clearTimeout(id); });
    ns._splashTimers.length = 0;
    if (ns._decodeRAF) { cancelAnimationFrame(ns._decodeRAF); ns._decodeRAF = null; }
    if (window._splashParticleCleanup) window._splashParticleCleanup();

    ov.classList.add('fade-out');
    sessionStorage.setItem('dx-splash-seen', '1');
    ns._splashActive = false;

    if (window._dxTutorial && typeof window._dxTutorial.hideTOC === 'function') {
      window._dxTutorial.hideTOC();
    }

    if (typeof ns.completeLauncherBoot === 'function') {
      ns.completeLauncherBoot({ revealAnimation: manual ? 'skip' : 'normal' });
    }

    // If the 8 module servers aren't ready yet, completeLauncherBoot is a no-op and the
    // shell stays boot-pending. Re-show the boot gate (concealed behind the splash until
    // now) so the user sees a "starting up" spinner instead of a blank screen until ready.
    if (!ns._studioReadyResolved && typeof ns.showStudioBootGate === 'function') {
      ns.showStudioBootGate();
    }

    setTimeout(function() {
      ov.remove();
      if (typeof ns.tryCompleteLauncherBoot === 'function') ns.tryCompleteLauncherBoot();
    }, 800);
  }

  function _showProceedPrompt() {
    var ov   = document.getElementById('splashOverlay');
    var skip = ov && ov.querySelector('.splash-skip');
    if (!skip) return;

    ov.setAttribute('onclick', 'skipSplash(false)');

    skip.innerHTML =
      '<span class="splash-skip-key">↵ ENTER</span>' +
      '<span class="splash-skip-sep"> &nbsp;·&nbsp; </span>' +
      '<span class="ko">클릭하여 시작</span>' +
      '<span class="en">CLICK TO ENTER</span>' +
      '<span class="ja">クリックして開始</span>' +
      '<span class="zh-CN">点击进入</span>' +
      '<span class="zh-TW">點擊進入</span>' +
      '<span class="es">HAGA CLIC PARA ENTRAR</span>';
    skip.classList.add('ready');
  }

  function replaySplash() {
    var existing = document.getElementById('splashOverlay');
    if (existing) existing.remove();

    sessionStorage.removeItem('dx-splash-seen');

    var ov = document.createElement('div');
    ov.className = 'splash-overlay';
    ov.id = 'splashOverlay';
    ov.setAttribute('onclick', 'skipSplash(true)');
    ov.innerHTML =
      '<div class="splash-grid"></div>' +
      '<div class="splash-scanline"></div>' +
      '<div class="splash-vignette"></div>' +
      '<div class="splash-ring splash-ring-sm"></div>' +
      '<div class="splash-ring splash-ring-md"></div>' +
      '<div class="splash-ring splash-ring-lg"></div>' +
      '<svg class="splash-circuits" id="splashCircuits" preserveAspectRatio="xMidYMid meet">' +
        '<defs>' +
          '<filter id="glowFilter">' +
            '<feGaussianBlur stdDeviation="3" result="blur"/>' +
            '<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>' +
          '</filter>' +
        '</defs>' +
      '</svg>' +
      '<div class="splash-pulses" id="splashPulses"></div>' +
      '<div class="splash-particles" id="splashParticles"></div>' +
      '<div class="splash-logo-hud" id="splashLogoHud">' +
        '<div class="splash-logo" id="splashLogo">' +
          '<span class="logo-char" data-char="D">D</span><span class="logo-char" data-char="E">E</span><span class="logo-char" data-char="E">E</span><span class="logo-char" data-char="P">P</span><span class="logo-char" data-char="X">X</span>' +
          '<div class="logo-scanline" id="logoScanline"></div>' +
        '</div>' +
        '<div class="splash-subtitle" id="splashSubtitle">AI Studio</div>' +
      '</div>' +
      '<div class="splash-core-text" id="splashCoreText">' +
        '<span class="ko">전체 시스템 가동</span>' +
        '<span class="en">ALL SYSTEMS ONLINE</span>' +
        '<span class="ja">全システム稼働中</span>' +
        '<span class="zh-CN">全部系统已上线</span>' +
        '<span class="zh-TW">全部系統已上線</span>' +
        '<span class="es">TODOS LOS SISTEMAS EN LÍNEA</span>' +
      '</div>' +
      '<svg class="splash-beams" id="splashBeams"></svg>' +
      '<div class="splash-modules-area" id="splashModulesArea"></div>' +
      '<div class="splash-burst" id="splashBurst"></div>' +
      '<div class="splash-skip">' +
        '<span class="ko">클릭하여 건너뛰기</span>' +
        '<span class="en">Click to skip</span>' +
        '<span class="ja">クリックでスキップ</span>' +
        '<span class="zh-CN">点击跳过</span>' +
        '<span class="zh-TW">點擊跳過</span>' +
        '<span class="es">Clic para omitir</span>' +
      '</div>';
    document.body.insertBefore(ov, document.body.firstChild);
    initSplashV2();
  }


  function _createCircuitTraces() {
    var svg = document.getElementById('splashCircuits');
    if (!svg) return;
    var w = window.innerWidth, h = window.innerHeight;
    svg.setAttribute('viewBox', '0 0 ' + w + ' ' + h);
    var cx = w / 2, cy = h / 2;
    var _tracePaths = [];

    var moduleCount = Math.max(1, ns._SPLASH_MODULES.length);
    var step = 360 / moduleCount;
    var mainAngles = ns._SPLASH_MODULES.map(function(_mod, i) {
      return 22.5 + i * step;
    });
    var hudClearance = 80;
    mainAngles.forEach(function(deg, i) {
      var rad = deg * Math.PI / 180;
      var len = Math.min(w, h) * 0.45;
      var sx = cx + hudClearance * Math.cos(rad), sy = cy + hudClearance * Math.sin(rad);
      var ex = cx + len * Math.cos(rad), ey = cy + len * Math.sin(rad);
      var mx = cx + len * 0.4 * Math.cos(rad + 0.1);
      var my = cy + len * 0.4 * Math.sin(rad + 0.1);
      _addTrace(svg, _tracePaths, 'M' + sx + ',' + sy + ' Q' + mx + ',' + my + ' ' + ex + ',' + ey, i * 0.08);

      for (var b = 0; b < 2 + Math.floor(i % 3); b++) {
        var branchStart = 0.3 + b * 0.25;
        var bx = cx + len * branchStart * Math.cos(rad);
        var by = cy + len * branchStart * Math.sin(rad);
        var bAngle = rad + (b % 2 === 0 ? 0.5 : -0.5);
        var bLen = len * 0.2;
        var bex = bx + bLen * Math.cos(bAngle);
        var bey = by + bLen * Math.sin(bAngle);
        _addTrace(svg, _tracePaths, 'M' + bx + ',' + by + ' L' + bex + ',' + bey, i * 0.08 + 0.3 + b * 0.1);
      }
    });

    requestAnimationFrame(function() {
      var pending = [];
      _tracePaths.forEach(function(item) {
        if (!ns._TRACE_LENGTH_CACHE.has(item.d)) pending.push(item);
      });

      function applyTraceStyles() {
        _tracePaths.forEach(function(item) {
          var len = ns._TRACE_LENGTH_CACHE.get(item.d) || 300;
          item.path.style.setProperty('--trace-len', len);
          item.path.style.setProperty('--trace-delay', item.delay + 's');
          item.path.style.strokeDasharray = len;
          item.path.style.strokeDashoffset = len;
        });
      }

      function appendCircuitNodes() {
        var nodeContainer = document.getElementById('splashOverlay');
        if (nodeContainer) {
          var nodeRadius = Math.min(Math.min(w, h) * 0.22, 200);
          var frag = document.createDocumentFragment();
          mainAngles.forEach(function(deg) {
            var rad = deg * Math.PI / 180;
            var nx = cx + nodeRadius * Math.cos(rad);
            var ny = cy + nodeRadius * Math.sin(rad);
            var dot = document.createElement('div');
            dot.className = 'splash-circuit-node';
            dot.style.left = nx + 'px';
            dot.style.top  = ny + 'px';
            frag.appendChild(dot);
          });
          nodeContainer.appendChild(frag);
        }
      }

      if (!pending.length) {
        applyTraceStyles();
        appendCircuitNodes();
        return;
      }

      var idx = 0;
      function measureChunk(deadline) {
        var hasIdleBudget = deadline && typeof deadline.timeRemaining === 'function';
        do {
          var item = pending[idx++];
          ns._TRACE_LENGTH_CACHE.set(item.d, item.path.getTotalLength());
        } while (idx < pending.length && (!hasIdleBudget || deadline.timeRemaining() > 4));

        if (idx < pending.length) {
          _requestIdle(measureChunk);
        } else {
          requestAnimationFrame(function() {
            applyTraceStyles();
            appendCircuitNodes();
          });
        }
      }

      _requestIdle(measureChunk);
    });
  }

  function _requestIdle(fn) {
    if (window.requestIdleCallback) {
      window.requestIdleCallback(fn, { timeout: 120 });
    } else {
      setTimeout(function() { fn({ timeRemaining: function() { return 8; } }); }, 0);
    }
  }

  function _addTrace(svg, collector, d, delay) {
    var path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', d);
    svg.appendChild(path);
    collector.push({ path: path, delay: delay, d: d });
  }


  function _createParticles(count) {
    var container = document.getElementById('splashParticles');
    if (!container) return;

    var canvas = document.createElement('canvas');
    canvas.className = 'splash-particle-canvas';
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    container.appendChild(canvas);

    var ctx = canvas.getContext('2d');
    var particles = [];

    for (var i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        size: 2 + Math.random() * 6,
        baseOpacity: 0.3 + Math.random() * 0.4,
        speed: 0.3 + Math.random() * 0.5,
        dy: -20 - Math.random() * 30,
        dx: -15 + Math.random() * 30,
        phase: Math.random() * Math.PI * 2,
        period: 3 + Math.random() * 2
      });
    }

    var startTime = performance.now();
    var animId;

    function draw(now) {
      var elapsed = (now - startTime) / 1000;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particles.forEach(function(p) {
        var t = (elapsed / p.period + p.phase) % 1;
        var easedT = Math.sin(t * Math.PI * 2) * 0.5 + 0.5;
        var offsetX = p.dx * easedT;
        var offsetY = p.dy * easedT;
        var opacity = p.baseOpacity * (0.5 + 0.5 * Math.sin(elapsed * 1.5 + p.phase));

        ctx.beginPath();
        ctx.arc(p.x + offsetX, p.y + offsetY, p.size / 2, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(99, 140, 255, ' + opacity + ')';
        ctx.fill();
      });

      animId = requestAnimationFrame(draw);
    }

    animId = requestAnimationFrame(draw);

    window._splashParticleCleanup = function() {
      if (animId) cancelAnimationFrame(animId);
    };
  }


  function _animateLogoGlitch() {
    var logo = document.getElementById('splashLogo');
    if (!logo) return;
    var chars = logo.querySelectorAll('.logo-char');
    var scanline = document.getElementById('logoScanline');
    if (!chars.length) return;

    chars.forEach(function(c) { c.classList.add('decoding'); });
    if (scanline) scanline.classList.add('active');

    var total = chars.length;
    var cycleDuration = 1600;
    var lockInterval = cycleDuration / total;
    var startTime = performance.now();
    var lockedCount = 0;
    var lastDecodeUpdate = 0;

    function tick(now) {
      var elapsed = now - startTime;

      var shouldLock = Math.min(total, Math.floor(elapsed / lockInterval));
      while (lockedCount < shouldLock) {
        var c = chars[lockedCount];
        if (c.textContent !== c.dataset.char) c.textContent = c.dataset.char;
        c.classList.remove('decoding');
        c.classList.add('decoded');
        lockedCount++;
      }

      if (now - lastDecodeUpdate >= ns._DECODE_FRAME_INTERVAL) {
        for (var i = lockedCount; i < total; i++) {
          var next = ns._DECODE_CHARS[Math.random() * ns._DECODE_CHARS.length | 0];
          if (chars[i].textContent !== next) chars[i].textContent = next;
        }
        lastDecodeUpdate = now;
      }

      if (lockedCount < total) {
        ns._decodeRAF = requestAnimationFrame(tick);
      } else {
        if (scanline) scanline.classList.remove('active');
      }
    }

    ns._decodeRAF = requestAnimationFrame(tick);
  }

  function _animateLogoStabilize() {
    var logo = document.getElementById('splashLogo');
    if (!logo) return;
    if (ns._decodeRAF) { cancelAnimationFrame(ns._decodeRAF); ns._decodeRAF = null; }
    logo.querySelectorAll('.logo-char').forEach(function(c) {
      c.textContent = c.dataset.char;
      c.classList.remove('decoding');
      c.classList.add('decoded');
    });
    logo.classList.remove('glitch');
    logo.classList.add('stabilize');
  }

  function _animateLogoLock() {
    var logo = document.getElementById('splashLogo');
    var hud  = document.getElementById('splashLogoHud');
    if (logo) { logo.classList.remove('stabilize'); logo.classList.add('locked'); }
    if (hud)  { hud.classList.add('locked'); }
  }


  function _bootModule(mod, index) {
    var area = document.getElementById('splashModulesArea');
    var beamSvg = document.getElementById('splashBeams');
    if (!area || !beamSvg) return;

    var w = window.innerWidth, h = window.innerHeight;
    var cx = w / 2, cy = h / 2;
    var rad = (mod.angle - 90) * Math.PI / 180;
    var radius = Math.max(Math.min(Math.min(w, h) * 0.42, 340), 200);
    var mx = cx + radius * Math.cos(rad);
    var my = cy + radius * Math.sin(rad);

    var hudClearance = 80;
    var bsx = cx + hudClearance * Math.cos(rad);
    var bsy = cy + hudClearance * Math.sin(rad);
    var line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', bsx);
    line.setAttribute('y1', bsy);
    line.setAttribute('x2', mx);
    line.setAttribute('y2', my);
    var beamLen = Math.sqrt(Math.pow(mx - bsx, 2) + Math.pow(my - bsy, 2));
    line.style.setProperty('--beam-len', beamLen);
    line.style.strokeDasharray = beamLen;
    line.style.strokeDashoffset = beamLen;
    beamSvg.appendChild(line);
    requestAnimationFrame(function() { line.classList.add('fire'); });

    ns._splashTimers.push(setTimeout(function() {
      var shock = document.createElement('div');
      shock.className = 'splash-shockwave';
      shock.style.left = (mx - 60) + 'px';
      shock.style.top = (my - 60) + 'px';
      area.appendChild(shock);
      setTimeout(function() { shock.remove(); }, 400);
    }, 150));

    ns._splashTimers.push(setTimeout(function() {
      var frame = document.createElement('div');
      frame.className = 'splash-hud-frame';
      var isMobile = window.innerWidth < 600;
      var halfW = isMobile ? 30 : 55;
      var halfH = isMobile ? 24 : 42;
      frame.style.left = (mx - halfW) + 'px';
      frame.style.top = (my - halfH) + 'px';

      var iconWrap = document.createElement('div');
      iconWrap.className = 'splash-module-icon';
      iconWrap.innerHTML = _MODULE_ICONS[mod.icon] || '';
      frame.appendChild(iconWrap);

      var nameEl = document.createElement('div');
      nameEl.className = 'splash-module-name';
      nameEl.textContent = mod.name;
      nameEl.style.setProperty('--name-len', mod.name.length);
      nameEl.style.setProperty('--name-width', (mod.name.length * 6.5) + 'px');
      frame.appendChild(nameEl);

      var status = document.createElement('div');
      status.className = 'splash-module-status';
      status.textContent = 'ONLINE';
      frame.appendChild(status);

      area.appendChild(frame);
      requestAnimationFrame(function() {
        frame.classList.add('appear');
        iconWrap.classList.add('draw');
      });

      ns._splashTimers.push(setTimeout(function() { nameEl.classList.add('typing'); }, 100));
      ns._splashTimers.push(setTimeout(function() { status.classList.add('online'); }, 250));
    }, 200));
  }


  function _showEnergyGauge() {
    var ov = document.getElementById('splashOverlay');
    if (!ov) return;

    var gauge = document.createElement('div');
    gauge.className = 'energy-gauge';
    gauge.innerHTML =
      '<svg viewBox="0 0 80 80">' +
        '<circle class="gauge-track" cx="40" cy="40" r="34"/>' +
        '<circle class="gauge-fill" cx="40" cy="40" r="34"/>' +
      '</svg>' +
      '<span class="gauge-pct">0%</span>';
    ov.appendChild(gauge);

    var frames = document.querySelectorAll('.splash-hud-frame');
    frames.forEach(function(frame) {
      var dot = document.createElement('div');
      dot.className = 'charge-dot charging';
      frame.appendChild(dot);
    });

    var pctEl = gauge.querySelector('.gauge-pct');
    var startTime = performance.now();
    var duration = 2500;
    function tick(now) {
      var p = Math.min((now - startTime) / duration, 1);
      var val = Math.round(p * 100);
      if (pctEl) pctEl.textContent = val + '%';
      if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }


  function _activateCore() {
    var gauge = document.querySelector('.energy-gauge');
    if (gauge) {
      gauge.classList.add('fired');
      setTimeout(function() { gauge.remove(); }, 400);
    }

    document.querySelectorAll('.charge-dot.charging').forEach(function(dot) {
      dot.classList.remove('charging');
      dot.classList.add('firing');
      setTimeout(function() { dot.remove(); }, 400);
    });

    var textEl = document.getElementById('splashCoreText');
    var beamSvg = document.getElementById('splashBeams');
    if (!textEl) return;

    var w = window.innerWidth, h = window.innerHeight;
    var cy = h / 2;

    var targetX = w - 120;
    var targetY = cy;

    var moduleFrames = document.querySelectorAll('.splash-hud-frame');
    if (beamSvg && moduleFrames.length) {
      moduleFrames.forEach(function(frame) {
        var rect = frame.getBoundingClientRect();
        var fx = rect.left + rect.width / 2;
        var fy = rect.top + rect.height / 2;
        var line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', fx);
        line.setAttribute('y1', fy);
        line.setAttribute('x2', targetX);
        line.setAttribute('y2', targetY);
        line.classList.add('core-laser');
        var len = Math.sqrt(Math.pow(targetX - fx, 2) + Math.pow(targetY - fy, 2));
        var segLen = Math.min(len * 0.15, 40);
        line.style.setProperty('--beam-len', len);
        line.style.strokeDasharray = segLen + ' ' + (len + segLen);
        line.style.strokeDashoffset = len;
        beamSvg.appendChild(line);
      });
      requestAnimationFrame(function() {
        beamSvg.querySelectorAll('.core-laser').forEach(function(l) { l.classList.add('fire'); });
      });
    }

    var _splLang = localStorage.getItem('dx-lang') || 'en';
    var _splTexts = { en: 'ALL SYSTEMS ONLINE', ko: '전체 시스템 가동', ja: '全システム起動', 'zh-CN': '全系统启动', 'zh-TW': '全系統啟動', es: 'TODOS LOS SISTEMAS EN LÍNEA' };
    var fullText = _splTexts[_splLang] || _splTexts.en;
    textEl.innerHTML = '';
    textEl.style.opacity = '1';
    textEl.classList.add('typing');

    var charIdx = 0;
    ns._splashTimers.push(setTimeout(function typeChar() {
      if (charIdx < fullText.length) {
        textEl.textContent = fullText.substring(0, charIdx + 1);
        charIdx++;
        ns._splashTimers.push(setTimeout(typeChar, 100));
      } else {
        ns._splashTimers.push(setTimeout(function() {
          textEl.classList.remove('typing');
          textEl.classList.add('typed');
        }, 400));
      }
    }, 300));
  }

  function _triggerWarpJump() {
    var ov = document.getElementById('splashOverlay');
    if (!ov) return;

    ov.classList.add('warp-compress');

    ns._splashTimers.push(setTimeout(function() {
      ov.classList.add('dissolve-out');
      sessionStorage.setItem('dx-splash-seen', '1');
      ns._splashActive = false;
      if (typeof ns.completeLauncherBoot === 'function') {
        ns.completeLauncherBoot({ revealAnimation: 'normal' });
      }
    }, 700));

    ns._splashTimers.push(setTimeout(function() {
      ov.remove();
      if (typeof ns.tryCompleteLauncherBoot === 'function') ns.tryCompleteLauncherBoot();
    }, 1300));
  }


  function showHeroSplash() {
    var hero = document.getElementById('heroSplash');
    if (!hero) { revealMainContent(); return; }

    window._heroTimer = setTimeout(dismissHeroSplash, 4000);
    setTimeout(function() { var h = document.getElementById('heroSplash'); if (h) { h.remove(); revealMainContent(); } }, 5000);
  }

  function dismissHeroSplash() {
    var hero = document.getElementById('heroSplash');
    if (!hero || hero.classList.contains('hidden')) return;
    clearTimeout(window._heroTimer);
    hero.classList.add('hidden');
    revealMainContent();
    setTimeout(function() { hero.remove(); }, 700);
  }

  function revealMainContent() {
    var main = document.querySelector('.landing-container') || document.querySelector('.top-bar') || document.getElementById('landing');
    if (main && !main.classList.contains('main-content-reveal') && !main.classList.contains('main-content-reveal-skip')) {
      main.classList.add(sessionStorage.getItem('dx-splash-seen') ? 'main-content-reveal-skip' : 'main-content-reveal');
    }
  }

  ns.initSplashV2 = initSplashV2;
  ns.skipSplash = skipSplash;
  ns.replaySplash = replaySplash;
  ns.showHeroSplash = showHeroSplash;
  ns.dismissHeroSplash = dismissHeroSplash;
  ns.revealMainContent = revealMainContent;
})();
if (typeof DXI18n !== 'undefined' && typeof DXI18n.onLangChange === 'function') {
  DXI18n.onLangChange(function() {
    if (typeof DXLauncher !== 'undefined' && typeof DXLauncher.refreshLauncherChrome === 'function') DXLauncher.refreshLauncherChrome();
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
  });
}
