/**
 * ExplorerView — 플랫폼 상세 대시보드.
 * RadarChart, GroupBarChart, 벤치마크 테이블, 비교 모드.
 */
const ExplorerView = {
  _modelClickCb: null,
  _sortCol: null,
  _sortAsc: true,
  _taskTabRenderFrame: null,
  _lastOpen: null,

  setOnModelClick(cb) { this._modelClickCb = cb; },

  _lang() {
    return typeof DXI18n !== 'undefined' ? DXI18n.lang : 'en';
  },

  _copyPack(map) {
    return map[this._lang()] || map.en;
  },

  open(platformId, inputs, results) {
    const platform = DataLoader.getPlatformById(platformId);
    if (!platform) return;
    inputs = inputs || {};
    this._lastOpen = { platformId, inputs, results };
    const platforms = DataLoader.getPlatforms();
    const result = (results || []).find(r => r.platform.id === platformId) || null;

    this._renderTitle(platform);
    this._renderFacts(platform, inputs, result);
    this._renderSummary(platform);
    this._renderComparisonSummary(platform, null, inputs, result);
    this._renderRadar(platform, platforms, inputs, result);
    this._renderTaskTabs(platform, inputs);
    this._renderGroupBar(platform, inputs);
    this._renderTable(platform, inputs);
    this._renderMultiStreamEvidence(platform, inputs);
    this._renderCommerce(platform, inputs, result);
    if (typeof PlannerWorkspace !== 'undefined') {
      PlannerWorkspace.markCommerceStepActive(true);
    }
  },

  _renderTitle(platform) {
    const title = document.getElementById('detailTitle');
    if (!title) return;
    const topo = typeof RecommendEngine !== 'undefined'
      ? RecommendEngine._topologyLabel(platform)
      : '';
    title.textContent = platform.npu.model + ' + ' + platform.host.name;
    const subtitle = document.getElementById('detailSubtitle');
    if (subtitle) {
      subtitle.textContent = topo || '';
      subtitle.hidden = !topo;
    }
  },

  _renderFacts(platform, inputs, result) {
    const el = document.getElementById('recommendation-facts');
    if (!el) return;
    const metrics = this._metricsFor(platform, inputs, result);
    const copy = this._factsCopy();
    const runtime = (inputs.ort !== false) ? copy.runtimeOrt : copy.runtimeNative;
    const status = metrics.meetsRequirement ? copy.meets : copy.insufficient;
    el.innerHTML =
      '<div class="fact-grid">' +
        this._factItem(copy.task, inputs.task || '-') +
        this._factItem(copy.modelSize, inputs.size || '-') +
        this._factItem(copy.channelsRequired, inputs.cameras) +
        this._factItem(copy.targetFps, inputs.targetFps) +
        this._factItem(copy.runtime, runtime) +
        this._factItem(copy.maxChannels, this._formatChannels(metrics.maxChannels, metrics.boundaryFlag, copy)) +
        this._factItem(copy.status, status) +
        this._factItem(copy.throughput, this._formatNumber(metrics.throughputFps, 0)) +
        this._factItem(copy.latency, this._formatNumber(metrics.latencyMs, 2)) +
        this._factItem(copy.tdp, platform.npu.tdp_w + 'W') +
        this._factItem(copy.topsPerW, this._formatNumber(metrics.topsPerWatt, 2)) +
        this._factItem(copy.pricing, copy.pricingValue) +
      '</div>';
  },

  _factsCopy() {
    return this._copyPack({
      en: {
        task: 'Task', modelSize: 'Model size', channelsRequired: 'Channels required',
        targetFps: 'Target FPS', runtime: 'Runtime', runtimeOrt: 'ONNX Runtime', runtimeNative: 'Native',
        maxChannels: 'Max channels', status: 'Status', meets: 'Meets', insufficient: 'Insufficient',
        throughput: 'Throughput FPS', latency: 'Latency (ms)', tdp: 'TDP',
        topsPerW: 'TOPS/W', theoretical: 'theoretical',
        pricing: 'Pricing', pricingValue: 'Contact DEEPX for quote',
      },
      ko: {
        task: '작업', modelSize: '모델 크기', channelsRequired: '필요 채널 수',
        targetFps: '목표 FPS', runtime: '런타임', runtimeOrt: 'ONNX Runtime', runtimeNative: 'Native',
        maxChannels: '최대 채널', status: '충족 여부', meets: '충족', insufficient: '부족',
        throughput: '처리량 FPS', latency: '지연 (ms)', tdp: 'TDP',
        topsPerW: 'TOPS/W', theoretical: '이론값',
        pricing: '가격', pricingValue: '가격은 DEEPX에 문의',
      },
      ja: {
        task: 'タスク', modelSize: 'モデルサイズ', channelsRequired: '必要チャンネル数',
        targetFps: '目標FPS', runtime: 'ランタイム', runtimeOrt: 'ONNX Runtime', runtimeNative: 'Native',
        maxChannels: '最大チャンネル', status: '充足状況', meets: '充足', insufficient: '不足',
        throughput: 'スループット FPS', latency: 'レイテンシ (ms)', tdp: 'TDP',
        topsPerW: 'TOPS/W', theoretical: '理論値',
        pricing: '価格', pricingValue: '価格はDEEPXへお問い合わせ',
      },
      'zh-CN': {
        task: '任务', modelSize: '模型大小', channelsRequired: '所需通道数',
        targetFps: '目标 FPS', runtime: '运行时', runtimeOrt: 'ONNX Runtime', runtimeNative: 'Native',
        maxChannels: '最大通道', status: '达标情况', meets: '达标', insufficient: '不足',
        throughput: '吞吐量 FPS', latency: '延迟 (ms)', tdp: 'TDP',
        topsPerW: 'TOPS/W', theoretical: '理论值',
        pricing: '价格', pricingValue: '价格请联系 DEEPX',
      },
      'zh-TW': {
        task: '任務', modelSize: '模型大小', channelsRequired: '所需通道數',
        targetFps: '目標 FPS', runtime: '執行環境', runtimeOrt: 'ONNX Runtime', runtimeNative: 'Native',
        maxChannels: '最大通道', status: '達標情況', meets: '達標', insufficient: '不足',
        throughput: '吞吐量 FPS', latency: '延遲 (ms)', tdp: 'TDP',
        topsPerW: 'TOPS/W', theoretical: '理論值',
        pricing: '價格', pricingValue: '價格請聯絡 DEEPX',
      },
      es: {
        task: 'Tarea', modelSize: 'Tamaño del modelo', channelsRequired: 'Canales requeridos',
        targetFps: 'FPS objetivo', runtime: 'Entorno', runtimeOrt: 'ONNX Runtime', runtimeNative: 'Native',
        maxChannels: 'Canales máx.', status: 'Estado', meets: 'Cumple', insufficient: 'Insuficiente',
        throughput: 'Throughput FPS', latency: 'Latencia (ms)', tdp: 'TDP',
        topsPerW: 'TOPS/W', theoretical: 'teórico',
        pricing: 'Precio', pricingValue: 'Consultar precio a DEEPX',
      },
    });
  },

  _factItem(label, value) {
    return '<div class="fact-item">' +
      '<span class="fact-label">' + this._escHtml(label) + '</span>' +
      '<strong class="fact-value">' + this._escHtml(this._formatValue(value)) + '</strong>' +
    '</div>';
  },

  _renderSummary(p) {
    const el = document.getElementById('platform-summary');
    if (!el) return;
    const topoLabel = typeof RecommendEngine !== 'undefined'
      ? RecommendEngine._topologyLabel(p)
      : '';
    el.innerHTML =
      '<div class="spec-grid">' +
        this._specItem('NPU', p.npu.model) +
        (topoLabel ? this._specItem(
          '<span class="ko">벤치마크 구성</span><span class="en">Benchmark system</span><span class="ja">ベンチ構成</span><span class="zh-CN">基准系统</span><span class="zh-TW">基準系統</span>',
          topoLabel
        ) : '') +
        this._specItem('TOPS', p.npu.tops) +
        this._specItem('TDP', p.npu.tdp_w + 'W') +
        this._specItem('DRAM', p.npu.dram) +
        this._specItem(
          '<span class="ko">호스트</span><span class="en">Host</span><span class="ja">ホスト</span><span class="zh-CN">主机</span><span class="zh-TW">主機</span>',
          p.host.name + ' (' + p.host.cpu + ')'
        ) +
      '</div>';
  },

  _specItem(label, value) {
    return '<div class="spec-item">' +
      '<span class="spec-label">' + label + '</span>' +
      '<span class="spec-value">' + this._escHtml(value) + '</span>' +
    '</div>';
  },

  _renderRadar(platform, platforms, inputs, result) {
    const canvas = document.getElementById('radarChart');
    if (!canvas) return;

    const dd = document.getElementById('compare-dropdown');
    if (!dd) {
      RadarChart.draw(canvas, platforms, platform.id, null, inputs);
      return;
    }

    const previousCompareId = dd.value || null;
    const copy = this._comparisonCopy(this._lang());
    const selectLabel = copy.selectLabel;
    const options = platforms
      .filter(p => p.id !== platform.id)
      .map(p => {
        const name = p.npu.model + ' + ' + p.host.name;
        return '<option value="' + this._escHtml(p.id) + '">' + this._escHtml(name) + '</option>';
      });
    dd.innerHTML = '<option value="">-- ' + selectLabel + ' --</option>' + options.join('');
    if (previousCompareId && platforms.some(p => p.id === previousCompareId && p.id !== platform.id)) {
      dd.value = previousCompareId;
    }

    const drawComparison = () => {
      const compareId = dd.value || null;
      const comparePlatform = compareId ? platforms.find(p => p.id === compareId) || null : null;
      RadarChart.draw(canvas, platforms, platform.id, comparePlatform ? comparePlatform.id : null, inputs);
      this._renderComparisonSummary(platform, comparePlatform, inputs, result);
    };

    dd.onchange = drawComparison;
    drawComparison();
  },

  _renderComparisonSummary(platform, comparePlatform, inputs, result) {
    const el = document.getElementById('comparison-summary');
    if (!el) return;
    const lang = this._lang();
    const copy = this._comparisonCopy(lang);
    const current = this._metricsFor(platform, inputs, result);
    const compare = comparePlatform ? this._metricsFor(comparePlatform, inputs, null) : null;
    const rows = [
      [copy.npu, platform.npu.model, comparePlatform ? comparePlatform.npu.model : null],
      [copy.host, platform.host.name, comparePlatform ? comparePlatform.host.name : null],
      [copy.tops, platform.npu.tops, comparePlatform ? comparePlatform.npu.tops : null],
      [copy.tdp, platform.npu.tdp_w + 'W', comparePlatform ? comparePlatform.npu.tdp_w + 'W' : null],
      [copy.dram, platform.npu.dram, comparePlatform ? comparePlatform.npu.dram : null],
      [copy.throughput, this._formatNumber(current.throughputFps, 0), compare ? this._formatNumber(compare.throughputFps, 0) : null],
      [copy.maxChannels, this._formatChannels(current.maxChannels, current.boundaryFlag, copy), compare ? this._formatChannels(compare.maxChannels, compare.boundaryFlag, copy) : null],
    ];

    let html = '<p class="comparison-summary-head">' + this._escHtml(copy.summaryTitle) + '</p>';
    html += '<table class="comparison-table"><thead><tr><th>' + this._escHtml(copy.metric) + '</th><th>' + this._escHtml(copy.current) + '</th>';
    if (comparePlatform) html += '<th>' + this._escHtml(copy.compare) + '</th>';
    html += '</tr></thead><tbody>';
    rows.forEach(row => {
      html += '<tr><th scope="row">' + this._escHtml(row[0]) + '</th><td>' + this._escHtml(this._formatValue(row[1])) + '</td>';
      if (comparePlatform) html += '<td>' + this._escHtml(this._formatValue(row[2])) + '</td>';
      html += '</tr>';
    });
    html += '</tbody></table>';
    if (!comparePlatform) {
      html += '<p class="comparison-empty">' + this._escHtml(copy.empty) + '</p>';
    }
    el.innerHTML = html;
  },

  _comparisonCopy(lang) {
    const table = {
      en: {
        selectLabel: 'Select comparison',
        summaryTitle: 'Side-by-side summary',
        metric: 'Metric',
        current: 'Selected',
        compare: 'Compare',
        empty: 'Choose another platform in the dropdown to compare.',
        npu: 'NPU', host: 'Host', tops: 'TOPS', tdp: 'TDP', dram: 'DRAM',
        throughput: 'Throughput FPS',
        maxChannels: 'Max channels',
      },
      ko: {
        selectLabel: '비교 대상 선택',
        summaryTitle: '나란히 비교',
        metric: '항목',
        current: '선택',
        compare: '비교',
        empty: '위 드롭다운에서 다른 플랫폼을 선택하면 비교됩니다.',
        npu: 'NPU', host: '호스트', tops: 'TOPS', tdp: 'TDP', dram: 'DRAM',
        throughput: '처리량 FPS',
        maxChannels: '최대 채널',
      },
      ja: {
        selectLabel: '比較対象を選択',
        summaryTitle: '並べて比較',
        metric: '項目',
        current: '選択',
        compare: '比較',
        empty: '上のドロップダウンで別プラットフォームを選ぶと比較できます。',
        npu: 'NPU', host: 'ホスト', tops: 'TOPS', tdp: 'TDP', dram: 'DRAM',
        throughput: 'スループット FPS',
        maxChannels: '最大チャンネル',
      },
      'zh-CN': {
        selectLabel: '选择比较对象',
        summaryTitle: '并排比较',
        metric: '指标',
        current: '当前',
        compare: '对比',
        empty: '在上方下拉框中选择其他平台即可比较。',
        npu: 'NPU', host: '主机', tops: 'TOPS', tdp: 'TDP', dram: 'DRAM',
        throughput: '吞吐量 FPS',
        maxChannels: '最大通道',
      },
      'zh-TW': {
        selectLabel: '選擇比較對象',
        summaryTitle: '並排比較',
        metric: '指標',
        current: '目前',
        compare: '對比',
        empty: '在上方下拉框中選擇其他平台即可比較。',
        npu: 'NPU', host: '主機', tops: 'TOPS', tdp: 'TDP', dram: 'DRAM',
        throughput: '吞吐量 FPS',
        maxChannels: '最大通道',
      },
      es: {
        selectLabel: 'Seleccionar comparación',
        summaryTitle: 'Resumen comparativo',
        metric: 'Métrica',
        current: 'Seleccionado',
        compare: 'Comparar',
        empty: 'Elija otra plataforma en el menú para comparar.',
        npu: 'NPU', host: 'Host', tops: 'TOPS', tdp: 'TDP', dram: 'DRAM',
        throughput: 'Throughput FPS',
        maxChannels: 'Canales máx.',
      },
    };
    return table[lang] || table.en;
  },

  _renderTaskTabs(platform, inputs) {
    const container = document.getElementById('task-tabs');
    if (!container) return;
    const tasks = [
      { key: 'object_detection', ko: '객체 탐지', en: 'Object Detection', ja: '物体検出', 'zh-CN': '目标检测', 'zh-TW': '物件偵測', es: 'Detección de objetos' },
      { key: 'pose_estimation', ko: '포즈', en: 'Pose', ja: 'ポーズ', 'zh-CN': '姿态', 'zh-TW': '姿態', es: 'Pose' },
      { key: 'segmentation', ko: '분할', en: 'Segmentation', ja: 'セグメンテーション', 'zh-CN': '分割', 'zh-TW': '分割', es: 'Segmentación' },
      { key: 'oriented_bbox', ko: 'OBB', en: 'OBB', ja: 'OBB', 'zh-CN': 'OBB', 'zh-TW': 'OBB', es: 'OBB' },
      { key: 'classification', ko: '분류', en: 'Classification', ja: '分類', 'zh-CN': '分类', 'zh-TW': '分類', es: 'Clasificación' }
    ];

    container.innerHTML = '';
    tasks.forEach(t => {
      const btn = document.createElement('button');
      btn.className = 'task-tab' + (t.key === inputs.task ? ' active' : '');
      btn.innerHTML = '<span class="ko">' + t.ko + '</span><span class="en">' + t.en + '</span><span class="ja">' + t.ja + '</span><span class="zh-CN">' + t['zh-CN'] + '</span><span class="zh-TW">' + t['zh-TW'] + '</span><span class="es">' + t.es + '</span>';
      btn.dataset.task = t.key;
      btn.addEventListener('click', () => {
        const nextInputs = { ...inputs, task: t.key };
        container.querySelectorAll('.task-tab').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this._scheduleTaskTabRender(platform, nextInputs, null);
      });
      container.appendChild(btn);
    });
  },

  _scheduleTaskTabRender(platform, inputs, result) {
    if (this._taskTabRenderFrame) cancelAnimationFrame(this._taskTabRenderFrame);
    this._taskTabRenderFrame = requestAnimationFrame(() => {
      this._taskTabRenderFrame = null;
      this._renderFacts(platform, inputs, result);
      this._renderComparisonSummary(platform, null, inputs, result);
      this._renderRadar(platform, DataLoader.getPlatforms(), inputs, result);
      this._renderGroupBar(platform, inputs);
      this._renderTable(platform, inputs);
      this._renderMultiStreamEvidence(platform, inputs);
    });
  },

  _renderGroupBar(platform, inputs) {
    const canvas = document.getElementById('groupBarChart');
    if (!canvas) return;
    const ort = inputs.ort !== undefined ? inputs.ort : true;
    GroupBarChart.draw(canvas, platform, inputs.task, ort, (size) => {
      if (this._modelClickCb) this._modelClickCb({ task: inputs.task, size, ort });
    });
  },

  _renderTable(platform, inputs) {
    const container = document.getElementById('benchmark-table');
    if (!container) return;

    const ort = inputs.ort !== undefined ? inputs.ort : true;
    const rows = platform.benchmarks
      .filter(b => b.task === inputs.task && b.ort === ort)
      .map(b => {
        const multiAll = platform.multi_stream.filter(
          m => m.model === b.model && m.task === b.task && m.ort === ort
        );
        const { maxChannels, boundaryFlag } = RecommendEngine._calcMaxChannels(
          b, multiAll, inputs.targetFps
        );
        return {
          model: b.model,
          task: b.task,
          size: b.size,
          latencyMs: b.latency_ms,
          latencyFps: b.latency_fps,
          throughputFps: b.throughput_fps,
          maxChannels,
          boundaryFlag
        };
      });

    if (this._sortCol) {
      rows.sort((a, b) => {
        const va = a[this._sortCol], vb = b[this._sortCol];
        const cmp = (va < vb ? -1 : va > vb ? 1 : 0);
        return this._sortAsc ? cmp : -cmp;
      });
    }

    const flagBadge = (flag) => {
      const copy = this._factsCopy();
      if (flag === '+') return '+';
      if (flag === 'theoretical') {
        return ' <span class="badge badge-theoretical">' + this._escHtml(copy.theoretical) + '</span>';
      }
      return '';
    };

    const tableCopy = this._benchTableCopy();
    const thSort = (key, label) => {
      const arrow = this._sortCol === key ? (this._sortAsc ? ' ↑' : ' ↓') : '';
      return '<th data-sort="' + key + '" style="cursor:pointer">' + label + arrow + '</th>';
    };

    let html = '<table class="bench-table"><thead><tr>' +
      thSort('model', tableCopy.model) +
      thSort('task', tableCopy.task) +
      thSort('size', tableCopy.size) +
      thSort('latencyMs', tableCopy.latencyMs) +
      thSort('latencyFps', tableCopy.latencyFps) +
      thSort('throughputFps', tableCopy.throughputFps) +
      thSort('maxChannels', tableCopy.maxChannels) +
    '</tr></thead><tbody>';

    rows.forEach(r => {
      const isCurrent = r.task === inputs.task && r.size === inputs.size;
      html += '<tr class="bench-row' + (isCurrent ? ' row-highlight' : '') +
        '" data-task="' + r.task + '" data-size="' + r.size + '">' +
        '<td>' + this._escHtml(r.model) + '</td>' +
        '<td>' + this._escHtml(r.task) + '</td>' +
        '<td>' + this._escHtml(r.size) + '</td>' +
        '<td>' + (r.latencyMs != null ? r.latencyMs.toFixed(2) : '-') + '</td>' +
        '<td>' + (r.latencyFps != null ? Math.round(r.latencyFps) : '-') + '</td>' +
        '<td>' + (r.throughputFps != null ? Math.round(r.throughputFps) : '-') + '</td>' +
        '<td>' + r.maxChannels + flagBadge(r.boundaryFlag) + '</td>' +
      '</tr>';
    });

    html += '</tbody></table>';
    container.innerHTML = html;

    container.querySelectorAll('th[data-sort]').forEach(th => {
      th.addEventListener('click', () => {
        const col = th.dataset.sort;
        if (this._sortCol === col) {
          this._sortAsc = !this._sortAsc;
        } else {
          this._sortCol = col;
          this._sortAsc = true;
        }
        this._renderTable(platform, inputs);
      });
    });

    container.querySelectorAll('.bench-row').forEach(tr => {
      tr.style.cursor = 'pointer';
      tr.addEventListener('click', () => {
        const task = tr.dataset.task;
        const size = tr.dataset.size;
        const ort = inputs.ort !== undefined ? inputs.ort : true;
        if (this._modelClickCb) this._modelClickCb({ task, size, ort });
      });
    });
  },

  _renderMultiStreamEvidence(platform, inputs) {
    const el = document.getElementById('multi-stream-evidence');
    if (!el) return;
    const ort = inputs.ort !== undefined ? inputs.ort : true;
    const modelName = 'yolo26' + inputs.size;
    const rows = platform.multi_stream.filter(
      m => m.model === modelName && m.task === inputs.task && m.ort === ort
    ).sort((a, b) => a.stream_count - b.stream_count);

    if (!rows.length) {
      el.innerHTML = '<div class="empty-state">' + this._escHtml(this._multiStreamCopy().empty) + '</div>';
      return;
    }

    const msCopy = this._multiStreamCopy();
    let html = '<table class="multi-stream-table"><thead><tr>' +
      '<th>' + this._escHtml(msCopy.streams) + '</th>' +
      '<th>' + this._escHtml(msCopy.perChannel) + '</th>' +
      '<th>' + this._escHtml(msCopy.total) + '</th>' +
      '</tr></thead><tbody>';
    rows.forEach(row => {
      html += '<tr>' +
        '<td>' + this._escHtml(row.stream_count) + '</td>' +
        '<td>' + this._escHtml(this._formatNumber(row.per_channel_fps, 1)) + '</td>' +
        '<td>' + this._escHtml(this._formatNumber(row.total_fps, 1)) + '</td>' +
      '</tr>';
    });
    html += '</tbody></table>';
    el.innerHTML = html;
  },

  _selectedBenchmark(platform, inputs) {
    const modelName = 'yolo26' + inputs.size;
    const ort = inputs.ort !== undefined ? inputs.ort : true;
    return platform.benchmarks.find(
      b => b.model === modelName && b.task === inputs.task && b.ort === ort
    ) || null;
  },

  _metricsFor(platform, inputs, result) {
    if (result && result.platform && result.platform.id === platform.id) {
      return {
        throughputFps: result.throughputFps,
        latencyMs: result.latencyMs,
        maxChannels: result.maxChannels,
        boundaryFlag: result.boundaryFlag,
        meetsRequirement: result.meetsRequirement,
        topsPerWatt: result.topsPerWatt,
      };
    }

    const bench = this._selectedBenchmark(platform, inputs);
    const modelName = 'yolo26' + inputs.size;
    const ort = inputs.ort !== undefined ? inputs.ort : true;
    const multiAll = platform.multi_stream.filter(
      m => m.model === modelName && m.task === inputs.task && m.ort === ort
    );
    const channelCalc = bench
      ? RecommendEngine._calcMaxChannels(bench, multiAll, inputs.targetFps, inputs.fpsHeadroom)
      : { maxChannels: 0, boundaryFlag: null };
    const maxChannels = channelCalc.maxChannels || 0;
    const topsPerWatt = platform.npu.tdp_w > 0 ? platform.npu.tops / platform.npu.tdp_w : 0;
    return {
      throughputFps: bench ? bench.throughput_fps || 0 : 0,
      latencyMs: bench ? bench.latency_ms || 0 : 0,
      maxChannels,
      boundaryFlag: channelCalc.boundaryFlag,
      meetsRequirement: maxChannels >= (inputs.cameras || 0),
      topsPerWatt,
    };
  },

  _renderCommerce(platform, inputs, result) {
    const panel = document.getElementById('commercePanel');
    const body = document.getElementById('commerceBody');
    if (!panel || !body) return;

    panel.hidden = false;
    const productName = platform.npu.model + ' + ' + platform.host.name;
    // Real DEEPX purchase + sales pages (was homepage / stale /contact).
    const inquiryUrl = 'https://deepx.ai/contact-us/sales-support/';
    const storeUrl = 'https://deepx.ai/shop_now/';

    body.innerHTML =
      '<p class="commerce-lead">' +
        '<span class="ko"><strong>' + this._escHtml(productName) + '</strong> — 가격은 DEEPX에 문의하세요</span>' +
        '<span class="en"><strong>' + this._escHtml(productName) + '</strong> — contact DEEPX for pricing</span>' +
        '<span class="ja"><strong>' + this._escHtml(productName) + '</strong> — 価格はDEEPXへお問い合わせください</span>' +
        '<span class="zh-CN"><strong>' + this._escHtml(productName) + '</strong> — 价格请联系 DEEPX</span>' +
        '<span class="zh-TW"><strong>' + this._escHtml(productName) + '</strong> — 價格請聯絡 DEEPX</span>' +
        '<span class="es"><strong>' + this._escHtml(productName) + '</strong> — consulte el precio a DEEPX</span>' +
      '</p>' +
      '<p class="commerce-note txt-dim txt-sm">' +
        '<span class="ko">채널·FPS는 해당 벤치마크 구성(호스트+NPU)의 실측값입니다. 양산 견적·최종 가격은 DEEPX에 문의하세요.</span>' +
        '<span class="en">Channels and FPS are measured on that benchmark system (host + NPU). Contact DEEPX for production quotes and final pricing.</span>' +
        '<span class="ja">チャンネル・FPS はそのベンチマーク構成（ホスト+NPU）の実測値です。量産見積・最終価格は DEEPX へお問い合わせください。</span>' +
        '<span class="zh-CN">通道与 FPS 为该 benchmark 构成（主机+NPU）的实测值。量产报价与最终价格请联系 DEEPX。</span>' +
        '<span class="zh-TW">通道與 FPS 為該 benchmark 構成（主機+NPU）的實測值。量產報價與最終價格請聯絡 DEEPX。</span>' +
        '<span class="es">Los canales y FPS son medidos en ese sistema de benchmark (host + NPU). Consulte a DEEPX para cotizaciones y precio final.</span>' +
      '</p>' +
      '<div class="commerce-actions">' +
        '<a class="btn-commerce btn-commerce-primary" href="' + storeUrl + '" target="_blank" rel="noopener noreferrer">' +
          '<span class="ko">제품 정보</span><span class="en">Product info</span><span class="ja">製品情報</span><span class="zh-CN">产品信息</span><span class="zh-TW">產品資訊</span><span class="es">Info del producto</span>' +
        '</a>' +
        '<a class="btn-commerce btn-commerce-secondary" href="' + inquiryUrl + '" target="_blank" rel="noopener noreferrer">' +
          '<span class="ko">견적 문의</span><span class="en">Request quote</span><span class="ja">見積依頼</span><span class="zh-CN">询价</span><span class="zh-TW">詢價</span><span class="es">Solicitar cotización</span>' +
        '</a>' +
      '</div>';

    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) {
      DXI18n.applyLang(panel);
    }
  },

  _benchTableCopy() {
    return this._copyPack({
      en: {
        model: 'Model', task: 'Task', size: 'Size', latencyMs: 'Latency (ms)',
        latencyFps: 'Latency FPS', throughputFps: 'Throughput FPS', maxChannels: 'Max channels',
      },
      ko: {
        model: '모델', task: '작업', size: '크기', latencyMs: '지연 (ms)',
        latencyFps: '지연 FPS', throughputFps: '처리량 FPS', maxChannels: '최대 채널',
      },
      ja: {
        model: 'モデル', task: 'タスク', size: 'サイズ', latencyMs: 'レイテンシ (ms)',
        latencyFps: 'レイテンシ FPS', throughputFps: 'スループット FPS', maxChannels: '最大チャンネル',
      },
      'zh-CN': {
        model: '模型', task: '任务', size: '大小', latencyMs: '延迟 (ms)',
        latencyFps: '延迟 FPS', throughputFps: '吞吐量 FPS', maxChannels: '最大通道',
      },
      'zh-TW': {
        model: '模型', task: '任務', size: '大小', latencyMs: '延遲 (ms)',
        latencyFps: '延遲 FPS', throughputFps: '吞吐量 FPS', maxChannels: '最大通道',
      },
      es: {
        model: 'Modelo', task: 'Tarea', size: 'Tamaño', latencyMs: 'Latencia (ms)',
        latencyFps: 'Latencia FPS', throughputFps: 'Throughput FPS', maxChannels: 'Canales máx.',
      },
    });
  },

  _multiStreamCopy() {
    return this._copyPack({
      en: {
        streams: 'Streams', perChannel: 'Per-channel FPS', total: 'Total FPS',
        empty: 'No multi-stream measurement for this model, task, and runtime.',
      },
      ko: {
        streams: '스트림 수', perChannel: '채널당 FPS', total: '총 FPS',
        empty: '이 모델·작업·런타임에 대한 multi-stream 측정값이 없습니다.',
      },
      ja: {
        streams: 'ストリーム数', perChannel: 'チャンネルあたり FPS', total: '合計 FPS',
        empty: 'このモデル・タスク・ランタイムの multi-stream 測定値がありません。',
      },
      'zh-CN': {
        streams: '流数', perChannel: '每通道 FPS', total: '总 FPS',
        empty: '此模型、任务和运行时没有 multi-stream 测量数据。',
      },
      'zh-TW': {
        streams: '串流數', perChannel: '每通道 FPS', total: '總 FPS',
        empty: '此模型、任務和執行環境沒有 multi-stream 測量資料。',
      },
      es: {
        streams: 'Flujos', perChannel: 'FPS por canal', total: 'FPS total',
        empty: 'No hay medición multi-stream para este modelo, tarea y entorno.',
      },
    });
  },

  _formatChannels(value, flag, copy) {
    if (value == null) return '-';
    const facts = copy || this._factsCopy();
    if (flag === '+') return value + '+';
    if (flag === 'theoretical') return value + ' ' + facts.theoretical;
    return String(value);
  },

  _formatNumber(value, digits) {
    if (value == null || !isFinite(value)) return '-';
    return Number(value).toFixed(digits).replace(/\.0+$/, '').replace(/(\.\d*?)0+$/, '$1');
  },

  _formatValue(value) {
    if (value == null || value === '') return '-';
    return String(value);
  },

  _escHtml(value) {
    return this._formatValue(value)
      .replace(/&/g, '&amp;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  },
};
if (typeof registerPlannerLangRefresher === 'function') {
  registerPlannerLangRefresher(function() {
    if (ExplorerView._lastOpen) {
      const snapshot = ExplorerView._lastOpen;
      ExplorerView.open(snapshot.platformId, snapshot.inputs, snapshot.results);
      return;
    }
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
  });
}
