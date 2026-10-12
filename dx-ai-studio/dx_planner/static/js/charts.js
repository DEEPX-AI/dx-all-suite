/**
 * Charts — four Canvas 2D charts (BarChart, GaugeChart, GroupBarChart, RadarChart).
 * Driven by theme CSS variables, devicePixelRatio aware, no external libraries.
 */

let _plannerThemeColorCache = null;

function cachePlannerThemeColors() {
  const styles = getComputedStyle(document.documentElement);
  _plannerThemeColorCache = {
    '--accent': styles.getPropertyValue('--accent').trim(),
    '--status-warn': styles.getPropertyValue('--status-warn').trim(),
    '--status-ok': styles.getPropertyValue('--status-ok').trim(),
    '--status-error': styles.getPropertyValue('--status-error').trim(),
    '--border-subtle': styles.getPropertyValue('--border-subtle').trim(),
    '--text-primary': styles.getPropertyValue('--text-primary').trim(),
    '--text-secondary': styles.getPropertyValue('--text-secondary').trim(),
    '--text-muted': styles.getPropertyValue('--text-muted').trim(),
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

// 1. BarChart — Step 2 horizontal bar chart
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
    const warning = getThemeColor('--status-warn');
    const text = getThemeColor('--text-primary');
    const dim = getThemeColor('--text-muted');
    const maxFps = Math.max(...results.map(r => (r.pipelineFps || 0)), 1);
    const barArea = w - pad.left - pad.right;

    results.forEach((r, i) => {
      const y = pad.top + i * (barH + gap);
      const bw = ((r.pipelineFps || 0) / maxFps) * barArea;
      const color = r.meetsRequirement ? accent : warning;
      const label = r.platform.npu.model + ' + ' + r.platform.host.name;

      // Platform name
      ctx.fillStyle = text;
      ctx.font = '12px system-ui, sans-serif';
      ctx.textAlign = 'right';
      ctx.textBaseline = 'middle';
      ctx.fillText(label, pad.left - 8, y + barH / 2);

      // Bar (measured only — no theoretical/estimated bars)
      ctx.fillStyle = color;
      if (ctx.roundRect) {
        ctx.beginPath();
        ctx.roundRect(pad.left, y, bw, barH, 4);
        ctx.fill();
      } else {
        ctx.fillRect(pad.left, y, bw, barH);
      }

      // FPS value
      ctx.fillStyle = dim;
      ctx.textAlign = 'left';
      ctx.fillText(Math.round((r.pipelineFps || 0)) + ' FPS', pad.left + bw + 6, y + barH / 2);
    });

    // Click events (clear the previous handler)
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

// 2. GaugeChart — mini donut gauge (60x60)
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

    const success = getThemeColor('--status-ok') || '#22c55e';
    const warning = getThemeColor('--status-warn') || '#f59e0b';
    const danger = getThemeColor('--status-error') || '#ff453a';
    const border = getThemeColor('--border-subtle') || '#444';

    const ratio = required > 0 ? Math.min(current / required, 1.0) : 1;
    let color;
    if (current >= required) color = success;
    else if (current >= required * 0.5) color = warning;
    else color = danger;

    // Background arc
    ctx.beginPath();
    ctx.arc(cx, cy, radius, startAngle, endAngle);
    ctx.strokeStyle = border;
    ctx.lineWidth = lw;
    ctx.lineCap = 'round';
    ctx.stroke();

    // Value arc
    const fillAngle = startAngle + ratio * Math.PI;
    ctx.beginPath();
    ctx.arc(cx, cy, radius, startAngle, fillAngle);
    ctx.strokeStyle = color;
    ctx.lineWidth = lw;
    ctx.lineCap = 'round';
    ctx.stroke();

    // Text
    const text = getThemeColor('--text-primary') || '#f5f5f7';
    ctx.fillStyle = text;
    ctx.font = 'bold 10px system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    const curStr = boundaryFlag === '+' ? current + '+' : String(current);
    ctx.fillText(curStr + '/' + required, cx, cy + 2);
  }
};

// 3. GroupBarChart — grouped bars per model size (Step 3)
const GroupBarChart = {
  draw(canvas, platform, task, ort, onBarClick) {
    if (!canvas || !platform) return;
    const sizes = ['n', 's', 'm', 'l', 'x'];
    const pad = { top: 40, right: 20, bottom: 40, left: 50 };
    const w = getCanvasParentContentWidth(canvas, 500);
    const h = 300;
    const ctx = setupCanvas(canvas, w, h);

    const accent = getThemeColor('--accent') || '#2997ff';
    const text = getThemeColor('--text-primary') || '#f5f5f7';
    const dim = getThemeColor('--text-muted') || '#8892A8';
    const gridColor = getThemeColor('--border-subtle') || '#333';

    // Collect data
    const data = sizes.map(sz => {
      const bench = platform.benchmarks.find(
        b => b.size === sz && b.task === task && b.ort === ort
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

    // Grid lines
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

    // Legend
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

    // Draw bars
    const barRects = [];
    data.forEach((d, i) => {
      const gx = pad.left + i * groupW + groupW / 2;

      // X-axis label
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

    // Bar clicks (clear the previous handler)
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

// 4. RadarChart — 5-axis radar/spider chart (Step 3)
const RadarChart = {
  draw(canvas, platforms, currentId, compareId, inputs) {
    if (!canvas || !platforms.length) return;
    const size = Math.max(getCanvasParentContentWidth(canvas, 280), 250);
    const ctx = setupCanvas(canvas, size, size);

    const accent = getThemeColor('--accent') || '#2997ff';
    const success = getThemeColor('--status-ok') || '#30d158';
    const text = getThemeColor('--text-primary') || '#f5f5f7';
    const dim = getThemeColor('--text-muted') || '#8892A8';
    const border = getThemeColor('--border-subtle') || '#333';

    const cx = size / 2;
    const cy = size / 2;
    const radius = size * 0.35;
    const axes = 5;
    const labels = ['FPS', 'Channels', 'TOPS/W', 'Stability', 'TOPS'].map(l => (typeof T === 'function' ? T(l) : l));

    // Compute the 5 axis values for each platform
    function calcMetrics(pid) {
      const p = platforms.find(pl => pl.id === pid);
      if (!p) return null;
      const ort = inputs.ort !== undefined ? inputs.ort : true;
      const bench = p.benchmarks.find(
        b => b.size === inputs.size && b.task === inputs.task && b.ort === ort
      );
      const fps = bench ? bench.throughput_fps : 0;
      const multiAll = p.multi_stream.filter(
        m => m.size === inputs.size && m.task === inputs.task && m.ort === ort
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

    // Maximum values for normalization
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

    // Concentric grid
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

    // Axis lines + labels
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

    // Draw the data area
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

      // Points
      norm.forEach((v, i) => {
        const angle = -Math.PI / 2 + (2 * Math.PI / axes) * i;
        const px = cx + Math.cos(angle) * radius * v;
        const py = cy + Math.sin(angle) * radius * v;
        ctx.beginPath();
        ctx.arc(px, py, 3, 0, 2 * Math.PI);
        ctx.globalAlpha = 1.0;
        if (i === 1 && bf === '+') {
          // Measurement ceiling marker: hollow circle
          ctx.strokeStyle = fillColor;
          ctx.lineWidth = 2;
          ctx.stroke();
        } else {
          ctx.fillStyle = fillColor;
          ctx.fill();
        }
      });
    }

    // Comparison platform (drawn behind)
    if (compareId) {
      const compCalc = calcMetrics(compareId);
      if (compCalc) drawArea(compCalc, success, 0.2);
    }

    // Current platform
    const curCalc = calcMetrics(currentId);
    if (curCalc) drawArea(curCalc, accent, 0.3);
  }
};
