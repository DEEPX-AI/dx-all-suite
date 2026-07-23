/**
 * Charts — Canvas 2D 차트 4종 (BarChart, GaugeChart, GroupBarChart, RadarChart).
 * 테마 CSS 변수 기반, devicePixelRatio 지원, 외부 라이브러리 없음.
 */

let _plannerThemeColorCache = null;

function cachePlannerThemeColors() {
  const styles = getComputedStyle(document.documentElement);
  _plannerThemeColorCache = {
    '--accent': styles.getPropertyValue('--accent').trim(),
    '--warning': styles.getPropertyValue('--warning').trim(),
    '--success': styles.getPropertyValue('--success').trim(),
    '--error': styles.getPropertyValue('--error').trim(),
    '--border': styles.getPropertyValue('--border').trim(),
    '--text-1': styles.getPropertyValue('--text-1').trim(),
    '--text-2': styles.getPropertyValue('--text-2').trim(),
    '--text-3': styles.getPropertyValue('--text-3').trim(),
  };
  return _plannerThemeColorCache;
}

function getThemeColor(varName) {
  return (_plannerThemeColorCache || cachePlannerThemeColors())[varName] || '';
}

function setupCanvas(canvas, w, h) {
  const dpr = window.devicePixelRatio || 1;
  canvas.width = w * dpr;
  canvas.height = h * dpr;
  canvas.style.width = w + 'px';
  canvas.style.height = h + 'px';
  const ctx = canvas.getContext('2d');
  ctx.scale(dpr, dpr);
  return ctx;
}

function getCanvasParentContentWidth(canvas, fallback) {
  const parent = canvas.parentElement;
  if (!parent) return fallback;
  const style = getComputedStyle(parent);
  const paddingX = parseFloat(style.paddingLeft) + parseFloat(style.paddingRight);
  return Math.max(parent.clientWidth - paddingX, 120);
}

// 1. BarChart — Step 2 수평 바 차트
const BarChart = {
  draw(canvas, results, onBarClick) {
    if (!canvas || !results.length) return;
    const pad = { top: 16, right: 60, bottom: 16, left: 120 };
    const barH = 28;
    const gap = 20;
    const w = getCanvasParentContentWidth(canvas, 500);
    const h = results.length * (barH + gap) + pad.top + pad.bottom;
    const ctx = setupCanvas(canvas, w, h);

    const accent = getThemeColor('--accent');
    const warning = getThemeColor('--warning');
    const text = getThemeColor('--text-1');
    const dim = getThemeColor('--text-3');
    const maxFps = Math.max(...results.map(r => r.throughputFps), 1);
    const barArea = w - pad.left - pad.right;

    results.forEach((r, i) => {
      const y = pad.top + i * (barH + gap);
      const bw = (r.throughputFps / maxFps) * barArea;
      const color = r.meetsRequirement ? accent : warning;
      const label = r.platform.npu.model + ' + ' + r.platform.host.name;

      // 플랫폼 이름
      ctx.fillStyle = text;
      ctx.font = '12px system-ui, sans-serif';
      ctx.textAlign = 'right';
      ctx.textBaseline = 'middle';
      ctx.fillText(label, pad.left - 8, y + barH / 2);

      // 바
      ctx.fillStyle = color;
      if (r.boundaryFlag === 'theoretical') {
        ctx.setLineDash([4, 3]);
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.strokeRect(pad.left, y, bw, barH);
        ctx.setLineDash([]);
        ctx.globalAlpha = 0.3;
        ctx.fillRect(pad.left, y, bw, barH);
        ctx.globalAlpha = 1.0;
      } else {
        if (ctx.roundRect) {
          ctx.beginPath();
          ctx.roundRect(pad.left, y, bw, barH, 4);
          ctx.fill();
        } else {
          ctx.fillRect(pad.left, y, bw, barH);
        }
      }

      // FPS 값
      ctx.fillStyle = dim;
      ctx.textAlign = 'left';
      ctx.fillText(Math.round(r.throughputFps) + ' FPS', pad.left + bw + 6, y + barH / 2);
    });

    // 클릭 이벤트 (기존 핸들러 정리)
    canvas.onclick = null;
    canvas.onclick = (e) => {
      const rect = canvas.getBoundingClientRect();
      const y = (e.clientY - rect.top);
      const idx = Math.floor((y - pad.top) / (barH + gap));
      if (idx >= 0 && idx < results.length && (y - pad.top) % (barH + gap) < barH) {
        if (onBarClick) onBarClick(results[idx].platform.id);
      }
    };
  }
};

// 2. GaugeChart — 미니 도넛 게이지 (60x60)
const GaugeChart = {
  draw(canvas, current, required, boundaryFlag) {
    if (!canvas) return;
    const size = 60;
    const ctx = setupCanvas(canvas, size, size);
    const cx = size / 2;
    const cy = size / 2 + 6;
    const radius = 22;
    const lw = 3;
    const startAngle = Math.PI;
    const endAngle = 2 * Math.PI;

    const success = getThemeColor('--success') || '#22c55e';
    const warning = getThemeColor('--warning') || '#f59e0b';
    const danger = getThemeColor('--error') || '#F85149';
    const border = getThemeColor('--border') || '#444';

    const ratio = required > 0 ? Math.min(current / required, 1.0) : 1;
    let color;
    if (current >= required) color = success;
    else if (current >= required * 0.5) color = warning;
    else color = danger;

    // 배경 아크
    ctx.beginPath();
    ctx.arc(cx, cy, radius, startAngle, endAngle);
    ctx.strokeStyle = border;
    ctx.lineWidth = lw;
    ctx.lineCap = 'round';
    ctx.stroke();

    // 값 아크
    const fillAngle = startAngle + ratio * Math.PI;
    ctx.beginPath();
    ctx.arc(cx, cy, radius, startAngle, fillAngle);
    ctx.strokeStyle = color;
    ctx.lineWidth = lw;
    ctx.lineCap = 'round';
    ctx.stroke();

    // 텍스트
    const text = getThemeColor('--text-1') || '#E2E8F0';
    ctx.fillStyle = text;
    ctx.font = 'bold 10px system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    const curStr = boundaryFlag === '+' ? current + '+' : String(current);
    ctx.fillText(curStr + '/' + required, cx, cy + 2);
  }
};

// 3. GroupBarChart — 모델 사이즈별 그룹 바 (Step 3)
const GroupBarChart = {
  draw(canvas, platform, task, ort, onBarClick) {
    if (!canvas || !platform) return;
    const sizes = ['n', 's', 'm', 'l', 'x'];
    const pad = { top: 40, right: 20, bottom: 40, left: 50 };
    const w = getCanvasParentContentWidth(canvas, 500);
    const h = 300;
    const ctx = setupCanvas(canvas, w, h);

    const accent = getThemeColor('--accent') || '#638CFF';
    const text = getThemeColor('--text-1') || '#E2E8F0';
    const dim = getThemeColor('--text-3') || '#8892A8';
    const gridColor = getThemeColor('--border') || '#333';

    // 데이터 수집
    const data = sizes.map(sz => {
      const modelName = 'yolo26' + sz;
      const bench = platform.benchmarks.find(
        b => b.model === modelName && b.task === task && b.ort === ort
      );
      return {
        size: sz,
        latencyFps: bench ? bench.latency_fps : null,
        throughputFps: bench ? bench.throughput_fps : null
      };
    });

    const allVals = data.flatMap(d => [d.latencyFps, d.throughputFps]).filter(v => v != null);
    const maxVal = allVals.length ? Math.max(...allVals) * 1.1 : 100;
    const chartW = w - pad.left - pad.right;
    const chartH = h - pad.top - pad.bottom;
    const groupW = chartW / sizes.length;
    const barW = groupW * 0.3;

    // 그리드라인
    ctx.strokeStyle = gridColor;
    ctx.lineWidth = 0.5;
    ctx.setLineDash([3, 3]);
    for (let i = 0; i <= 4; i++) {
      const y = pad.top + chartH - (i / 4) * chartH;
      ctx.beginPath();
      ctx.moveTo(pad.left, y);
      ctx.lineTo(w - pad.right, y);
      ctx.stroke();
      ctx.fillStyle = dim;
      ctx.font = '10px system-ui, sans-serif';
      ctx.textAlign = 'right';
      ctx.textBaseline = 'middle';
      ctx.fillText(Math.round((maxVal * i) / 4), pad.left - 6, y);
    }
    ctx.setLineDash([]);

    // 범례
    const accentLight = accent + '88';
    ctx.fillStyle = accentLight;
    ctx.fillRect(w - pad.right - 140, pad.top - 30, 12, 12);
    ctx.fillStyle = dim;
    ctx.font = '10px system-ui, sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText('Latency FPS', w - pad.right - 124, pad.top - 20);
    ctx.fillStyle = accent;
    ctx.fillRect(w - pad.right - 140, pad.top - 14, 12, 12);
    ctx.fillStyle = dim;
    ctx.fillText('Throughput FPS', w - pad.right - 124, pad.top - 4);

    // 바 그리기
    const barRects = [];
    data.forEach((d, i) => {
      const gx = pad.left + i * groupW + groupW / 2;

      // X축 라벨
      ctx.fillStyle = text;
      ctx.font = '12px system-ui, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(d.size, gx, h - pad.bottom + 20);

      if (d.latencyFps != null) {
        const bh = (d.latencyFps / maxVal) * chartH;
        const bx = gx - barW - 1;
        const by = pad.top + chartH - bh;
        ctx.fillStyle = accentLight;
        ctx.fillRect(bx, by, barW, bh);
        barRects.push({ x: bx, y: by, w: barW, h: bh, size: d.size });
      }

      if (d.throughputFps != null) {
        const bh = (d.throughputFps / maxVal) * chartH;
        const bx = gx + 1;
        const by = pad.top + chartH - bh;
        ctx.fillStyle = accent;
        ctx.fillRect(bx, by, barW, bh);
        barRects.push({ x: bx, y: by, w: barW, h: bh, size: d.size });
      }

      if (d.latencyFps == null && d.throughputFps == null) {
        ctx.fillStyle = gridColor;
        ctx.font = '10px system-ui, sans-serif';
        ctx.fillText('N/A', gx, pad.top + chartH - 10);
      }
    });

    // 바 클릭 (기존 핸들러 정리)
    canvas.onclick = null;
    if (onBarClick) {
      canvas.onclick = (e) => {
        const rect = canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;
        for (const br of barRects) {
          if (mx >= br.x && mx <= br.x + br.w && my >= br.y && my <= br.y + br.h) {
            onBarClick(br.size);
            return;
          }
        }
      };
    }
  }
};

// 4. RadarChart — 5축 레이더/스파이더 차트 (Step 3)
const RadarChart = {
  draw(canvas, platforms, currentId, compareId, inputs) {
    if (!canvas || !platforms.length) return;
    const size = Math.max(getCanvasParentContentWidth(canvas, 280), 250);
    const ctx = setupCanvas(canvas, size, size);

    const accent = getThemeColor('--accent') || '#638CFF';
    const success = getThemeColor('--success') || '#3FB950';
    const text = getThemeColor('--text-1') || '#E2E8F0';
    const dim = getThemeColor('--text-3') || '#8892A8';
    const border = getThemeColor('--border') || '#333';

    const cx = size / 2;
    const cy = size / 2;
    const radius = size * 0.35;
    const axes = 5;
    const labels = ['FPS', 'Channels', 'TOPS/W', 'Stability', 'TOPS'];

    // 각 플랫폼에 대해 5축 값 계산
    function calcMetrics(pid) {
      const p = platforms.find(pl => pl.id === pid);
      if (!p) return null;
      const modelName = 'yolo26' + inputs.size;
      const ort = inputs.ort !== undefined ? inputs.ort : true;
      const bench = p.benchmarks.find(
        b => b.model === modelName && b.task === inputs.task && b.ort === ort
      );
      const fps = bench ? bench.throughput_fps : 0;
      const multiAll = p.multi_stream.filter(
        m => m.model === modelName && m.task === inputs.task && m.ort === ort
      );
      const { maxChannels, boundaryFlag: bf } = RecommendEngine._calcMaxChannels(
        bench || { throughput_fps: 0 }, multiAll, inputs.targetFps
      );
      const topsW = p.npu.tdp_w > 0 ? p.npu.tops / p.npu.tdp_w : 0;
      const stability = (typeof RecommendEngine !== 'undefined' && RecommendEngine._stabilityScore)
        ? multiAll.reduce((best, m) => {
            const s = RecommendEngine._stabilityScore(m);
            return s > best ? s : best;
          }, 0)
        : 0;
      return { metrics: [fps, maxChannels, topsW, stability, p.npu.tops], boundaryFlag: bf };
    }

    // 정규화를 위한 최대값 계산
    const allCalc = platforms.map(p => calcMetrics(p.id)).filter(Boolean);
    const allMetrics = allCalc.map(c => c.metrics);
    const maxVals = [0, 0, 0, 0, 0];
    allMetrics.forEach(m => {
      m.forEach((v, i) => { if (v > maxVals[i]) maxVals[i] = v; });
    });
    maxVals.forEach((v, i) => { if (v === 0) maxVals[i] = 1; });

    function normalize(metrics) {
      return metrics.map((v, i) => v / maxVals[i]);
    }

    // 동심원 그리드
    const rings = [0.33, 0.66, 1.0];
    rings.forEach(scale => {
      ctx.beginPath();
      for (let i = 0; i <= axes; i++) {
        const angle = -Math.PI / 2 + (2 * Math.PI / axes) * i;
        const px = cx + Math.cos(angle) * radius * scale;
        const py = cy + Math.sin(angle) * radius * scale;
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      }
      ctx.closePath();
      ctx.strokeStyle = border;
      ctx.lineWidth = 0.5;
      ctx.stroke();
    });

    // 축 라인 + 라벨
    for (let i = 0; i < axes; i++) {
      const angle = -Math.PI / 2 + (2 * Math.PI / axes) * i;
      const ex = cx + Math.cos(angle) * radius;
      const ey = cy + Math.sin(angle) * radius;
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(ex, ey);
      ctx.strokeStyle = border;
      ctx.lineWidth = 0.5;
      ctx.stroke();

      const lx = cx + Math.cos(angle) * (radius + 18);
      const ly = cy + Math.sin(angle) * (radius + 18);
      ctx.fillStyle = dim;
      ctx.font = '11px system-ui, sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(labels[i], lx, ly);
    }

    // 데이터 영역 그리기
    function drawArea(calc, fillColor, alpha) {
      const norm = normalize(calc.metrics);
      const bf = calc.boundaryFlag;
      ctx.beginPath();
      norm.forEach((v, i) => {
        const angle = -Math.PI / 2 + (2 * Math.PI / axes) * i;
        const px = cx + Math.cos(angle) * radius * v;
        const py = cy + Math.sin(angle) * radius * v;
        if (i === 0) ctx.moveTo(px, py);
        else ctx.lineTo(px, py);
      });
      ctx.closePath();
      ctx.strokeStyle = fillColor;
      ctx.lineWidth = 2;
      ctx.stroke();
      ctx.globalAlpha = alpha;
      ctx.fillStyle = fillColor;
      ctx.fill();
      ctx.globalAlpha = 1.0;

      // 점
      norm.forEach((v, i) => {
        const angle = -Math.PI / 2 + (2 * Math.PI / axes) * i;
        const px = cx + Math.cos(angle) * radius * v;
        const py = cy + Math.sin(angle) * radius * v;
        ctx.beginPath();
        ctx.arc(px, py, 3, 0, 2 * Math.PI);
        ctx.globalAlpha = 1.0;
        if (i === 1 && bf === '+') {
          // 측정 상한 표시: 빈 원
          ctx.strokeStyle = fillColor;
          ctx.lineWidth = 2;
          ctx.stroke();
        } else {
          ctx.fillStyle = fillColor;
          ctx.fill();
        }
      });
    }

    // 비교 플랫폼 (뒤에 그림)
    if (compareId) {
      const compCalc = calcMetrics(compareId);
      if (compCalc) drawArea(compCalc, success, 0.2);
    }

    // 현재 플랫폼
    const curCalc = calcMetrics(currentId);
    if (curCalc) drawArea(curCalc, accent, 0.3);
  }
};
