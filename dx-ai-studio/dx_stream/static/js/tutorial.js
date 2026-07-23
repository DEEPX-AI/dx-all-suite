(function () {
  'use strict';

  function goPage(p) { if (window.DXStream && DXStream.nav) DXStream.nav(p); }

  function openModelDetailModal() {
    closeModelDetailModal();
    var card = document.querySelector('#models-grid .card');
    if (card) card.click();
    var modal = document.getElementById('model-detail-modal');
    if (!modal) return;
    setTimeout(function () {
      if (modal.open && typeof modal.close === 'function') modal.close();
      modal.classList.add('dxt-tutorial-dialog');
      if (typeof modal.show === 'function') modal.show();
      else modal.setAttribute('open', '');
    }, 80);
  }

  function closeModelDetailModal() {
    var modal = document.getElementById('model-detail-modal');
    if (!modal) return;
    modal.classList.remove('dxt-tutorial-dialog');
    if (modal.open && typeof modal.close === 'function') modal.close();
  }

  function _scrollToTarget(selector) {
    var el = document.querySelector(selector);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }

  function _orderGlobalFirst(list) {
    var idx = list.findIndex(function (s) { return s.id === 'global'; });
    if (idx > 0) {
      var globalSec = list.splice(idx, 1)[0];
      list.unshift(globalSec);
    }
    return list;
  }

  function _mockDemoVideoPreview() {
    var section = document.getElementById('demo-video-section');
    if (section) {
      section.style.display = '';
      section.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    var pipe = document.getElementById('demo-pipeline-info');
    if (pipe) pipe.textContent = 'YOLOv8n · 1920×1080 · filesrc sample.mp4';
    var res = document.getElementById('demo-resolution-info');
    if (res) res.textContent = '1920×1080';
    var model = document.getElementById('demo-model-info');
    if (model) model.textContent = 'YOLOv8n';
    var stats = document.getElementById('webrtc-stats-overlay');
    if (stats) {
      stats.style.display = '';
      stats.textContent = '28.4 FPS | RTT: 18ms | lost: 0';
    }
  }

  function _hideDemoVideoPreview() {
    var section = document.getElementById('demo-video-section');
    if (section) section.style.display = 'none';
  }

  function _mockStreamToast() {
    var c = document.getElementById('toast-container');
    if (!c) return;
    c.innerHTML = '';
    if (window.DXStream && typeof DXStream.toast === 'function') {
      DXStream.toast('Tutorial preview', 'success');
      var toast = c.querySelector('.toast');
      if (toast) toast.id = 'dxt-mock-stream-toast';
      return;
    }
    var el = document.createElement('div');
    el.id = 'dxt-mock-stream-toast';
    el.className = 'toast toast-success show';
    el.textContent = 'Tutorial preview';
    c.appendChild(el);
  }

  function _dismissStreamToast() {
    var c = document.getElementById('toast-container');
    if (c) c.innerHTML = '';
  }

  function _ensureModelsGridDownloadBtn() {
    var btn = document.querySelector('#dxt-stream-mock-download-btn')
      || document.querySelector('.download-model-btn');
    if (btn) {
      if (!btn.id) btn.id = 'dxt-stream-mock-download-btn';
      btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
      return btn;
    }
    var card = document.querySelector('#models-grid .card');
    var host = card || document.getElementById('models-grid');
    if (!host) return null;
    if (!card) {
      host.innerHTML = '<div class="card" style="cursor:pointer"><h3>Tutorial Sample</h3>'
        + '<p class="txt-dim txt-sm"><span class="en">Tutorial preview model</span></p></div>';
      card = host.querySelector('.card');
    }
    var mockBtn = document.createElement('button');
    mockBtn.id = 'dxt-stream-mock-download-btn';
    mockBtn.className = 'btn btn-sm btn-accent download-model-btn';
    mockBtn.type = 'button';
    mockBtn.textContent = '⬇️ Download';
    mockBtn.addEventListener('click', function (e) { e.stopPropagation(); });
    var badge = card.querySelector('.card-badge');
    if (badge) badge.replaceWith(mockBtn);
    else card.appendChild(mockBtn);
    mockBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });
    return mockBtn;
  }

  function _prepModelsGridDownloadDemo() {
    closeModelDetailModal();
    goPage('models');
    return new Promise(function (resolve) {
      var attempts = 0;
      function settle() {
        _ensureModelsGridDownloadBtn();
        setTimeout(function () {
          _ensureModelsGridDownloadBtn();
          resolve();
        }, 450);
      }
      function tick() {
        if (document.querySelector('#models-grid .card') || attempts >= 40) {
          settle();
          return;
        }
        attempts++;
        setTimeout(tick, 100);
      }
      tick();
    });
  }

  function _clearModelsGridDownloadDemo() {
    var mock = document.getElementById('dxt-stream-mock-download-btn');
    if (mock) mock.remove();
    if (window.DXStream && typeof DXStream.modelsInit === 'function') {
      DXStream.modelsInit();
    }
  }

  function _prepPropertyPanel() {
    var panel = document.getElementById('property-panel');
    if (!panel) return;
    panel.classList.remove('hidden');
    panel.style.display = '';
    var empty = panel.querySelector('.prop-empty');
    if (empty) empty.style.display = 'none';
    var content = document.getElementById('prop-content');
    if (content && !content.children.length) {
      content.innerHTML = '<div class="prop-row"><label>name</label><input value="dxinfer" readonly></div>';
    }
    panel.scrollIntoView({ block: 'nearest' });
  }

  // 비동기 DOM 폴링 헬퍼
  function pollFor(selector, cb) {
    var tries = 0;
    (function poll() {
      if (document.querySelector(selector)) return cb && cb();
      if (++tries >= 20) return cb && cb();
      setTimeout(poll, 100);
    })();
  }

  function _prepElementDetail() {
    goPage('elements');
    var card = document.querySelector('#elements-grid .card');
    if (card) card.click();
    else if (window.DXStream && typeof DXStream.showElementDetail === 'function' &&
             window.DXStream._allElements && DXStream._allElements[0]) {
      DXStream.showElementDetail(DXStream._allElements[0].name);
    }
    var detail = document.getElementById('element-detail');
    if (detail) {
      detail.style.display = '';
      setTimeout(function () { detail.scrollIntoView({ behavior: 'smooth', block: 'center' }); }, 150);
    }
  }

  var sections = [

    { id: 'dashboard', icon: '📊',
      title: { ko: '📊 대시보드', en: '📊 Dashboard', ja: '📊 ダッシュボード', 'zh-CN': '📊 仪表板', 'zh-TW': '📊 儀表板', es: '📊 Panel de control' },
      description: { ko: '시스템 상태 및 성능 모니터링', en: 'System status and performance monitoring', ja: 'システム状態とパフォーマンス監視', 'zh-CN': '系统状态和性能监控', 'zh-TW': '系統狀態和效能監控', es: 'Estado del sistema y monitorización del rendimiento' },
      beforeStart: function () { goPage('dashboard'); },
      steps: [
        { target: '#dash-stats', position: 'bottom',
          title: { ko: '시스템 상태 카드', en: 'Status Cards', ja: 'システム状態カード', 'zh-CN': '系统状态卡片', 'zh-TW': '系統狀態卡片', es: 'Tarjetas de estado' },
          content: { ko: '<strong>NPU, GStreamer, 모델, 비디오, 빌드</strong> 5개 상태를 카드로 한눈에 확인합니다. ✅=정상, ⚠️=경고.', en: 'View <strong>NPU, GStreamer, Models, Videos, Build</strong> status at a glance. ✅=OK, ⚠️=warning.', ja: '<strong>NPU, GStreamer, モデル, ビデオ, ビルド</strong>の5つの状態をカードで一目で確認できます。✅=正常, ⚠️=警告。', 'zh-CN': '一目了然地查看<strong>NPU、GStreamer、模型、视频、构建</strong>5个状态卡片。✅=正常, ⚠️=警告。', 'zh-TW': '一目了然地查看<strong>NPU, GStreamer, 模型, 影片, 建構</strong>5個狀態卡片。✅=正常, ⚠️=警告。', es: 'Consulte de un vistazo el estado de <strong>NPU, GStreamer, modelos, vídeos y compilación</strong>. ✅=OK, ⚠️=advertencia.' } },
        { target: '#stat-npu', position: 'bottom',
          title: { ko: 'NPU 상태', en: 'NPU Status', ja: 'NPU状態', 'zh-CN': 'NPU状态', 'zh-TW': 'NPU狀態', es: 'Estado del NPU' },
          content: { ko: 'DeepX NPU 디바이스의 <strong>감지 상태</strong>입니다. ✅이면 정상 동작, ⚠️이면 드라이버 설치가 필요합니다.', en: 'DeepX NPU <strong>detection status</strong>. ✅ = working, ⚠️ = driver installation needed.', ja: 'DeepX NPUデバイスの<strong>検出状態</strong>です。✅=正常動作、⚠️=ドライバーのインストールが必要です。', 'zh-CN': 'DeepX NPU设备的<strong>检测状态</strong>。✅=正常运行，⚠️=需要安装驱动程序。', 'zh-TW': 'DeepX NPU設備的<strong>偵測狀態</strong>。✅=正常運作，⚠️=需要安裝驅動程式。', es: '<strong>Estado de detección</strong> del NPU DeepX. ✅ = operativo, ⚠️ = requiere instalación del controlador.' } },
        { target: '#pipeline-overview', position: 'bottom',
          title: { ko: '파이프라인 개요', en: 'Pipeline Overview', ja: 'パイプライン概要', 'zh-CN': '管道概览', 'zh-TW': '管線概覽', es: 'Resumen del pipeline' },
          content: { ko: '현재 <strong>실행 중인 파이프라인</strong>의 정보(모델명, 해상도, 상태)를 표시합니다.', en: 'Shows information about the <strong>currently running pipeline</strong> (model, resolution, status).', ja: '現在<strong>実行中のパイプライン</strong>の情報(モデル名、解像度、状態)を表示します。', 'zh-CN': '显示当前<strong>运行中管道</strong>的信息（模型名称、分辨率、状态）。', 'zh-TW': '顯示當前<strong>執行中管線</strong>的資訊（模型名稱、解析度、狀態）。', es: 'Muestra información del <strong>pipeline en ejecución</strong> (modelo, resolución, estado).' } },
        { target: '#quick-launch-grid', position: 'bottom',
          title: { ko: '빠른 실행', en: 'Quick Launch', ja: 'クイック起動', 'zh-CN': '快速启动', 'zh-TW': '快速啟動', es: 'Inicio rápido' },
          content: { ko: '<strong>객체 감지, 포즈 추정, 분할</strong> 원클릭 데모를 바로 시작할 수 있습니다.', en: 'One-click demos for <strong>object detection, pose estimation, segmentation</strong>.', ja: '<strong>物体検出、姿勢推定、セグメンテーション</strong>のワンクリックデモを起動できます。', 'zh-CN': '可即时启动<strong>目标检测、姿态估计、分割</strong>一键演示。', 'zh-TW': '可立即啟動<strong>物件偵測、姿態估計、分割</strong>一鍵示範。', es: 'Demos con un clic para <strong>detección de objetos, estimación de pose y segmentación</strong>.' } },
        { target: '#perf-table', position: 'top',
          title: { ko: '성능 지표', en: 'Performance Metrics', ja: 'パフォーマンス指標', 'zh-CN': '性能指标', 'zh-TW': '效能指標', es: 'Métricas de rendimiento' },
          content: { ko: '<strong>FPS, 추론 지연(ms), E2E 지연(ms), NPU 사용률(%)</strong>을 실시간으로 표시합니다.', en: 'Real-time display of <strong>FPS, inference latency, E2E latency, NPU utilization</strong>.', ja: '<strong>FPS、推論レイテンシ(ms)、E2Eレイテンシ(ms)、NPU使用率(%)</strong>をリアルタイムで表示します。', 'zh-CN': '实时显示<strong>FPS、推理延迟(ms)、E2E延迟(ms)、NPU使用率(%)</strong>。', 'zh-TW': '即時顯示<strong>FPS、推論延遲(ms)、E2E延遲(ms)、NPU使用率(%)</strong>。', es: 'Visualización en tiempo real de <strong>FPS, latencia de inferencia, latencia E2E y utilización del NPU</strong>.' } },
        { target: '#chart-fps', position: 'top',
          title: { ko: '스파크라인 차트', en: 'Sparkline Charts', ja: 'スパークラインチャート', 'zh-CN': '迷你折线图', 'zh-TW': '迷你折線圖', es: 'Gráficos sparkline' },
          content: { ko: '<strong>FPS와 NPU 사용률</strong>의 실시간 추이를 소형 차트로 표시합니다.', en: 'Small charts showing real-time trends of <strong>FPS and NPU utilization</strong>.', ja: '<strong>FPSとNPU使用率</strong>のリアルタイム推移を小型チャートで表示します。', 'zh-CN': '小型图表显示<strong>FPS和NPU使用率</strong>的实时趋势。', 'zh-TW': '小型圖表顯示<strong>FPS和NPU使用率</strong>的即時趨勢。', es: 'Gráficos compactos que muestran las tendencias en tiempo real de <strong>FPS y utilización del NPU</strong>.' } },
        { target: '#chart-npu', position: 'top',
          title: { ko: 'NPU 사용률 차트', en: 'NPU Utilization Chart', ja: 'NPU使用率チャート', 'zh-CN': 'NPU使用率图表', 'zh-TW': 'NPU使用率圖表', es: 'Gráfico de utilización del NPU' },
          content: { ko: '<strong>NPU 사용률</strong>의 실시간 추이를 별도 스파크라인으로 표시합니다. FPS 차트와 함께 성능을 모니터링합니다.', en: 'Separate sparkline showing real-time <strong>NPU utilization</strong> trend. Monitor performance alongside FPS chart.', ja: '<strong>NPU使用率</strong>のリアルタイム推移を別のスパークラインで表示します。FPSチャートと合わせてパフォーマンスを監視します。', 'zh-CN': '单独的迷你折线图显示实时<strong>NPU使用率</strong>趋势。与FPS图表一起监控性能。', 'zh-TW': '單獨的迷你折線圖顯示即時<strong>NPU使用率</strong>趨勢。與FPS圖表一起監控效能。', es: 'Sparkline independiente con la tendencia en tiempo real de la <strong>utilización del NPU</strong>. Supervise el rendimiento junto con el gráfico de FPS.' },
          beforeStep: function () {
            var el = document.querySelector('#chart-npu');
            if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
          } },
      ]
    },

    { id: 'demo', icon: '🎬',
      title: { ko: '🎬 데모 런처', en: '🎬 Demo Launcher', ja: '🎬 デモランチャー', 'zh-CN': '🎬 演示启动器', 'zh-TW': '🎬 示範啟動器', es: '🎬 Lanzador de demos' },
      description: { ko: 'AI 데모 실행 및 실시간 영상', en: 'Run AI demos and view real-time video', ja: 'AIデモの実行とリアルタイム映像', 'zh-CN': '运行AI演示并查看实时视频', 'zh-TW': '執行AI示範並查看即時影像', es: 'Ejecute demos de IA y vea vídeo en tiempo real' },
      beforeStart: function () { goPage('demo'); },
      steps: [
        { target: '#playback-mode-bar', position: 'bottom',
          title: { ko: '재생 방식 (로컬 / 원격)', en: 'Playback Mode (Local / Remote)', ja: '再生方式 (ローカル / リモート)', 'zh-CN': '播放方式 (本地 / 远程)', 'zh-TW': '播放方式 (本機 / 遠端)', es: 'Modo de reproducción (Local / Remoto)' },
          content: { ko: '보드와 같은 PC·LAN에서 보면 <strong>로컬 (WebRTC)</strong> — 저지연, 재인코딩 없음. 다른 PC에서 원격 접속하면 <strong>원격 (MJPEG)</strong> — 어디서나 재생됩니다. WebRTC는 브라우저↔보드 직접 연결이라 원격에서는 붙지 않을 수 있어 MJPEG를 씁니다.', en: 'Viewing on the board\'s own PC / same LAN → <strong>Local (WebRTC)</strong> (low latency, no re-encode). Accessing remotely from another PC → <strong>Remote (MJPEG)</strong> (works anywhere). WebRTC needs a direct browser↔board path, so remote viewers use MJPEG.', ja: 'ボードと同じPC・LANで視聴 → <strong>ローカル (WebRTC)</strong>(低遅延・再エンコードなし)。別PCからリモート接続 → <strong>リモート (MJPEG)</strong>(どこでも再生)。WebRTCはブラウザ↔ボード直結が必要なため、リモートではMJPEGを使います。', 'zh-CN': '在开发板本机 / 同一 LAN 观看 → <strong>本地 (WebRTC)</strong>(低延迟, 无重编码)。从其他 PC 远程访问 → <strong>远程 (MJPEG)</strong>(随处播放)。WebRTC 需要浏览器↔开发板直连, 远程时改用 MJPEG。', 'zh-TW': '在開發板本機 / 同一 LAN 觀看 → <strong>本機 (WebRTC)</strong>(低延遲, 無重編碼)。從其他 PC 遠端存取 → <strong>遠端 (MJPEG)</strong>(隨處播放)。WebRTC 需要瀏覽器↔開發板直連, 遠端時改用 MJPEG。', es: 'Viendo en el PC de la placa / misma LAN → <strong>Local (WebRTC)</strong> (baja latencia, sin recodificar). Acceso remoto desde otro PC → <strong>Remoto (MJPEG)</strong> (funciona en cualquier lugar). WebRTC necesita una ruta directa navegador↔placa, por eso los remotos usan MJPEG.' } },
        { target: '#demo-filter-bar', position: 'bottom',
          title: { ko: '카테고리 필터', en: 'Category Filter', ja: 'カテゴリフィルター', 'zh-CN': '类别筛选', 'zh-TW': '類別篩選', es: 'Filtro por categoría' },
          content: { ko: '<strong>감지, 얼굴, 분할, 포즈, 추적, 멀티 스트림, 2차 추론</strong> 카테고리별로 데모를 필터링합니다.', en: 'Filter demos by <strong>detection, face, segmentation, pose, tracking, multi-stream, secondary</strong>.', ja: '<strong>検出、顔、セグメンテーション、ポーズ、追跡、マルチストリーム、2次推論</strong>カテゴリ別にデモをフィルタリングします。', 'zh-CN': '按<strong>检测、人脸、分割、姿态、跟踪、多路流、二次推理</strong>类别筛选演示。', 'zh-TW': '依<strong>偵測、人臉、分割、姿態、追蹤、多路串流、二次推論</strong>類別篩選示範。', es: 'Filtre demos por <strong>detección, rostro, segmentación, pose, seguimiento, multistream y secundaria</strong>.' } },
        { target: '#demo-grid', position: 'bottom',
          title: { ko: '데모 카드', en: 'Demo Cards', ja: 'デモカード', 'zh-CN': '演示卡片', 'zh-TW': '示範卡片', es: 'Tarjetas de demo' },
          content: { ko: '각 카드에 <strong>모델명, 카테고리, 실행 상태 배지</strong>가 표시됩니다. ▶ 버튼으로 데모를 시작합니다. <strong>다중 객체 추적, 멀티 스트림 RTSP, 2차 추론</strong> 데모가 포함됩니다.', en: 'Each card shows <strong>model name, category, status badge</strong>. Click ▶ to start. Includes <strong>Multi-Object Tracking, Multi-Stream RTSP, Secondary Inference</strong>.', ja: '各カードに<strong>モデル名、カテゴリ、実行状態バッジ</strong>が表示されます。▶ボタンでデモを開始します。<strong>複数物体追跡、マルチストリームRTSP、2次推論</strong>を含みます。', 'zh-CN': '每张卡片显示<strong>模型名称、类别、运行状态徽章</strong>。点击▶启动演示。包含<strong>多目标跟踪、多路流RTSP、二次推理</strong>。', 'zh-TW': '每張卡片顯示<strong>模型名稱、類別、執行狀態徽章</strong>。點擊▶啟動示範。包含<strong>多物件追蹤、多路串流RTSP、二次推論</strong>。', es: 'Cada tarjeta muestra <strong>nombre del modelo, categoría e insignia de estado</strong>. Haga clic en ▶ para iniciar. Incluye <strong>seguimiento multiobjeto, RTSP multistream e inferencia secundaria</strong>.' } },
        { target: '#dx-input-modal', position: 'bottom',
          title: { ko: '입력 소스 모달', en: 'Input Source Modal', ja: '入力ソースモーダル', 'zh-CN': '输入源模态框', 'zh-TW': '輸入來源對話框', es: 'Modal de fuente de entrada' },
          content: { ko: '카메라·RTSP URL·파일 경로·sudo 비밀번호 등을 묻는 <strong>접근 가능한 입력 dialog</strong>입니다. 브라우저 <code>prompt()</code> 대신 사용하며, 데모·파이프라인·Setup에서 나타납니다.', en: 'An <strong>accessible input dialog</strong> for camera names, RTSP URLs, file paths, sudo passwords, and more — used instead of browser <code>prompt()</code> in demos, the pipeline builder, and Setup.', ja: 'カメラ名・RTSP URL・ファイルパス・sudoパスワードなどを尋ねる<strong>アクセシブルな入力ダイアログ</strong>です。ブラウザの<code>prompt()</code>の代わりにデモ・パイプライン・Setupで表示されます。', 'zh-CN': '用于询问摄像头名称、RTSP URL、文件路径、sudo 密码等的<strong>无障碍输入对话框</strong>，在演示、管道构建器和 Setup 中替代浏览器 <code>prompt()</code>。', 'zh-TW': '用於詢問攝影機名稱、RTSP URL、檔案路徑、sudo 密碼等的<strong>無障礙輸入對話框</strong>，在示範、管線建構器和 Setup 中替代瀏覽器 <code>prompt()</code>。', es: 'Un <strong>diálogo de entrada accesible</strong> para nombres de cámara, URL RTSP, rutas de archivo, contraseñas sudo y más; sustituye a <code>prompt()</code> del navegador en demos, el constructor de pipelines y Setup.' },
          beforeStep: function () {
            if (window.DXStream && typeof DXStream.inputModal === 'function') {
              DXStream.inputModal('RTSP URL', {
                description: 'Enter an RTSP stream URL (tutorial preview).',
                placeholder: 'rtsp://192.168.1.10/stream',
                defaultValue: '',
              });
            }
          } },
        { target: '#demo-grid [id^="start-demo-"]', position: 'right',
          title: { ko: '데모 시작', en: 'Start Demo', ja: 'デモ開始', 'zh-CN': '启动演示', 'zh-TW': '啟動示範', es: 'Iniciar demo' },
          content: { ko: '▶ 버튼을 클릭하면 파이프라인이 시작됩니다. 실행 중인 카드에는 <strong>초록 테두리 + pulse 애니메이션</strong>이 표시됩니다.', en: 'Click ▶ to start the pipeline. Running cards show a <strong>green border + pulse animation</strong>.', ja: '▶をクリックするとパイプラインが開始します。実行中のカードには<strong>緑枠 + パルスアニメーション</strong>が表示されます。', 'zh-CN': '点击▶启动管道。运行中的卡片显示<strong>绿色边框 + 脉冲动画</strong>。', 'zh-TW': '點擊▶啟動管線。執行中的卡片顯示<strong>綠色邊框 + 脈衝動畫</strong>。', es: 'Haga clic en ▶ para iniciar el pipeline. Las tarjetas en ejecución muestran un <strong>borde verde y animación de pulso</strong>.' },
          beforeStep: function () {
            if (window.DXStream && typeof DXStream._inputModalCancel === 'function') {
              DXStream._inputModalCancel();
            }
            var btn = document.querySelector('#demo-grid [id^="start-demo-"]:not([disabled])');
            if (btn) btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
          } },
        { target: '#demo-video-section', position: 'bottom',
          title: { ko: '비디오 플레이어', en: 'Video Player', ja: 'ビデオプレイヤー', 'zh-CN': '视频播放器', 'zh-TW': '影片播放器', es: 'Reproductor de vídeo' },
          content: { ko: '데모 실행 시 <strong>WebRTC 실시간 영상</strong>이 표시됩니다. AI 추론 결과(바운딩 박스 등)가 오버레이됩니다.', en: 'When a demo runs, <strong>WebRTC real-time video</strong> appears with AI inference overlays (bounding boxes, etc.).', ja: 'デモ実行時に<strong>WebRTCリアルタイム映像</strong>が表示されます。AI推論結果(バウンディングボックスなど)がオーバーレイされます。', 'zh-CN': '演示运行时显示<strong>WebRTC实时视频</strong>，并叠加AI推理结果（边界框等）。', 'zh-TW': '示範執行時顯示<strong>WebRTC即時影像</strong>，並疊加AI推論結果（邊界框等）。', es: 'Al ejecutar una demo, aparece <strong>vídeo WebRTC en tiempo real</strong> con superposiciones de inferencia de IA (cuadros delimitadores, etc.).' },
          beforeStep: function () { _mockDemoVideoPreview(); } },
        { target: '#webrtc-stats-overlay', position: 'bottom',
          title: { ko: '통계 오버레이', en: 'Stats Overlay', ja: '統計オーバーレイ', 'zh-CN': '统计叠加', 'zh-TW': '統計疊加', es: 'Superposición de estadísticas' },
          content: { ko: '영상 위에 <strong>FPS, RTT, 패킷 손실률</strong>이 실시간 표시됩니다. 네트워크 품질을 모니터링할 수 있습니다.', en: '<strong>FPS, RTT, packet loss</strong> are displayed in real-time on the video. Monitor network quality.', ja: '映像上に<strong>FPS、RTT、パケットロス率</strong>がリアルタイム表示されます。ネットワーク品質を監視できます。', 'zh-CN': '视频上实时显示<strong>FPS、RTT、丢包率</strong>。可监控网络质量。', 'zh-TW': '影像上即時顯示<strong>FPS、RTT、封包遺失率</strong>。可監控網路品質。', es: 'Se muestran en tiempo real en el vídeo <strong>FPS, RTT y pérdida de paquetes</strong>. Supervise la calidad de la red.' },
          beforeStep: function () { _mockDemoVideoPreview(); } },
        { target: '#btn-demo-fullscreen', position: 'left',
          title: { ko: '전체화면', en: 'Fullscreen', ja: 'フルスクリーン', 'zh-CN': '全屏', 'zh-TW': '全螢幕', es: 'Pantalla completa' },
          content: { ko: '비디오를 <strong>전체화면</strong>으로 전환합니다. Esc로 나갈 수 있습니다.', en: 'Switch video to <strong>fullscreen</strong>. Press Esc to exit.', ja: 'ビデオを<strong>フルスクリーン</strong>に切り替えます。Escで終了できます。', 'zh-CN': '将视频切换为<strong>全屏</strong>模式。按Esc退出。', 'zh-TW': '將影片切換為<strong>全螢幕</strong>模式。按Esc退出。', es: 'Cambie el vídeo a <strong>pantalla completa</strong>. Pulse Esc para salir.' },
          beforeStep: function () { _mockDemoVideoPreview(); } },
        { target: '#btn-demo-stop', position: 'left',
          title: { ko: '데모 중지', en: 'Stop Demo', ja: 'デモ停止', 'zh-CN': '停止演示', 'zh-TW': '停止示範', es: 'Detener demo' },
          content: { ko: '⏹ 버튼을 클릭하면 실행 중인 <strong>데모를 중지</strong>합니다. 파이프라인이 종료되고 비디오 섹션이 닫힙니다.', en: 'Click ⏹ to <strong>stop the running demo</strong>. The pipeline stops and the video section closes.', ja: '⏹をクリックすると実行中の<strong>デモを停止</strong>します。パイプラインが終了しビデオセクションが閉じます。', 'zh-CN': '点击⏹<strong>停止运行中的演示</strong>。管道停止，视频区域关闭。', 'zh-TW': '點擊⏹<strong>停止執行中的示範</strong>。管線停止，影片區域關閉。', es: 'Haga clic en ⏹ para <strong>detener la demo en ejecución</strong>. El pipeline se detiene y se cierra la sección de vídeo.' },
          beforeStep: function () { _mockDemoVideoPreview(); } },
        { target: '#demo-pipeline-info', position: 'top',
          title: { ko: '파이프라인 정보', en: 'Pipeline Info', ja: 'パイプライン情報', 'zh-CN': '管道信息', 'zh-TW': '管線資訊', es: 'Información del pipeline' },
          content: { ko: '실행 중인 파이프라인의 <strong>모델명, 해상도, 입력 소스</strong> 등의 정보가 하단 바에 표시됩니다.', en: 'Shows <strong>model name, resolution, input source</strong> of the running pipeline in the bottom bar.', ja: '実行中のパイプラインの<strong>モデル名、解像度、入力ソース</strong>などの情報がボトムバーに表示されます。', 'zh-CN': '底部栏显示运行中管道的<strong>模型名称、分辨率、输入源</strong>等信息。', 'zh-TW': '底部欄顯示執行中管線的<strong>模型名稱、解析度、輸入來源</strong>等資訊。', es: 'Muestra en la barra inferior <strong>nombre del modelo, resolución y fuente de entrada</strong> del pipeline en ejecución.' },
          beforeStep: function () {
            _mockDemoVideoPreview();
            var bar = document.querySelector('#demo-video-section .video-info-bar');
            if (bar) bar.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
          },
          afterStep: function () { _hideDemoVideoPreview(); } },
      ]
    },

    { id: 'pipeline', icon: '🔧',
      title: { ko: '🔧 파이프라인 빌더', en: '🔧 Pipeline Builder', ja: '🔧 パイプラインビルダー', 'zh-CN': '🔧 管道构建器', 'zh-TW': '🔧 管線建構器', es: '🔧 Constructor de pipelines' },
      description: { ko: 'GStreamer 파이프라인 시각적 구성', en: 'Visual GStreamer pipeline builder', ja: 'GStreamerパイプラインのビジュアル構成', 'zh-CN': '可视化GStreamer管道构建', 'zh-TW': '視覺化GStreamer管線建構', es: 'Constructor visual de pipelines GStreamer' },
      beforeStart: function () { goPage('pipeline'); },
      steps: [
        { target: '.pipeline-actions', position: 'bottom',
          title: { ko: '파이프라인 툴바', en: 'Pipeline Toolbar', ja: 'パイプラインツールバー', 'zh-CN': '管道工具栏', 'zh-TW': '管線工具列', es: 'Barra de herramientas del pipeline' },
          content: { ko: '<strong>실행, 중지, 내보내기, 가져오기, 프리셋</strong> 버튼이 있습니다.', en: 'Contains <strong>run, stop, export, import, preset</strong> buttons.', ja: '<strong>実行、停止、エクスポート、インポート、プリセット</strong>ボタンがあります。', 'zh-CN': '包含<strong>运行、停止、导出、导入、预设</strong>按钮。', 'zh-TW': '包含<strong>執行、停止、匯出、匯入、預設</strong>按鈕。', es: 'Contiene botones de <strong>ejecutar, detener, exportar, importar y preset</strong>.' } },
        { target: '#btn-pipeline-run', position: 'bottom',
          title: { ko: '실행/중지 버튼', en: 'Run/Stop Buttons', ja: '実行/停止ボタン', 'zh-CN': '运行/停止按钮', 'zh-TW': '執行/停止按鈕', es: 'Botones ejecutar/detener' },
          content: { ko: '<strong>▶ 실행</strong> 버튼으로 파이프라인을 시작하고 <strong>⏹ 중지</strong> 버튼으로 종료합니다. 실행 중에는 상단 바의 상태 배지가 🟢으로 변경됩니다.', en: 'Start the pipeline with <strong>▶ Run</strong> and stop it with <strong>⏹ Stop</strong>. The status badge in the top bar turns 🟢 when running.', ja: '<strong>▶ 実行</strong>ボタンでパイプラインを開始し、<strong>⏹ 停止</strong>ボタンで終了します。実行中はトップバーの状態バッジが🟢に変わります。', 'zh-CN': '使用<strong>▶ 运行</strong>启动管道，使用<strong>⏹ 停止</strong>结束。运行时顶部栏状态徽章变为🟢。', 'zh-TW': '使用<strong>▶ 執行</strong>啟動管線，使用<strong>⏹ 停止</strong>結束。執行中頂部欄狀態徽章變為🟢。', es: 'Inicie el pipeline con <strong>▶ Ejecutar</strong> y deténgalo con <strong>⏹ Detener</strong>. La insignia de estado en la barra superior cambia a 🟢 durante la ejecución.' } },
        { target: '#preset-select', position: 'bottom',
          title: { ko: '프리셋', en: 'Presets', ja: 'プリセット', 'zh-CN': '预设', 'zh-TW': '預設', es: 'Presets' },
          content: { ko: '<strong>11개 데모 프리셋</strong>(0~10번)을 선택하면 미리 구성된 파이프라인이 로드됩니다. 다중 객체 추적(7), 멀티 스트림(8~9), 2차 추론(10)을 포함합니다.', en: 'Select from <strong>11 demo presets</strong> (0–10) to load pre-configured pipelines. Includes Multi-Object Tracking(7), Multi-Stream(8–9), Secondary Inference(10).', ja: '<strong>11個のデモプリセット</strong>(0〜10番)を選択すると、事前設定されたパイプラインが読み込まれます。複数物体追跡(7)、マルチストリーム(8〜9)、2次推論(10)を含みます。', 'zh-CN': '选择<strong>11个演示预设</strong>(0-10)加载预配置管道。包含多目标跟踪(7)、多路流(8-9)、二次推理(10)。', 'zh-TW': '選擇<strong>11個示範預設</strong>(0-10)載入預設管線。包含多物件追蹤(7)、多路串流(8-9)、二次推論(10)。', es: 'Seleccione entre <strong>11 presets de demo</strong> (0–10) para cargar pipelines preconfigurados. Incluye seguimiento multiobjeto (7), multistream (8–9) e inferencia secundaria (10).' } },
        { target: '#palette-panel', position: 'right',
          title: { ko: '요소 팔레트', en: 'Element Palette', ja: 'エレメントパレット', 'zh-CN': '元素面板', 'zh-TW': '元件面板', es: 'Paleta de elementos' },
          content: { ko: '<strong>카테고리별 GStreamer 요소</strong>가 나열됩니다. 검색하거나 드래그하여 캔버스에 배치합니다.', en: '<strong>GStreamer elements by category</strong>. Search or drag to place on canvas.', ja: '<strong>カテゴリ別GStreamerエレメント</strong>が一覧表示されます。検索またはドラッグしてキャンバスに配置します。', 'zh-CN': '按类别列出<strong>GStreamer元素</strong>。搜索或拖拽到画布上放置。', 'zh-TW': '按類別列出<strong>GStreamer元素</strong>。搜尋或拖曳到畫布上放置。', es: '<strong>Elementos GStreamer por categoría</strong>. Busque o arrastre para colocarlos en el lienzo.' } },
        { target: '#palette-search', position: 'right',
          title: { ko: '팔레트 검색', en: 'Palette Search', ja: 'パレット検索', 'zh-CN': '面板搜索', 'zh-TW': '面板搜尋', es: 'Búsqueda en la paleta' },
          content: { ko: '요소 이름으로 <strong>실시간 검색</strong>하여 필터링합니다.', en: '<strong>Real-time search</strong> elements by name.', ja: 'エレメント名で<strong>リアルタイム検索</strong>してフィルタリングします。', 'zh-CN': '按元素名称<strong>实时搜索</strong>并筛选。', 'zh-TW': '按元素名稱<strong>即時搜尋</strong>並篩選。', es: '<strong>Búsqueda en tiempo real</strong> de elementos por nombre.' } },
        { target: '.palette-item', position: 'right',
          title: { ko: '드래그 & 연결', en: 'Drag & Connect', ja: 'ドラッグ＆接続', 'zh-CN': '拖拽与连接', 'zh-TW': '拖曳與連接', es: 'Arrastrar y conectar' },
          content: { ko: '팔레트의 요소를 <strong>드래그</strong>하여 캔버스에 놓고, 노드의 <strong>src/sink 포트</strong>를 이어 파이프라인을 구성합니다. 빈 캔버스 영역을 드래그하면 뷰를 이동할 수 있습니다.', en: '<strong>Drag elements</strong> from the palette onto the canvas, then connect <strong>src/sink ports</strong> between nodes to build the pipeline. Drag empty canvas space to pan the view.', ja: 'パレットのエレメントを<strong>ドラッグ</strong>してキャンバスに配置し、ノードの<strong>src/sinkポート</strong>を接続してパイプラインを構成します。空白キャンバスをドラッグしてビューを移動できます。', 'zh-CN': '从面板<strong>拖拽元素</strong>到画布，连接节点间的<strong>src/sink端口</strong>构建管道。拖拽空白区域可平移视图。', 'zh-TW': '從面板<strong>拖曳元素</strong>到畫布，連接節點間的<strong>src/sink連接埠</strong>建構管線。拖曳空白區域可平移視圖。', es: '<strong>Arrastre elementos</strong> de la paleta al lienzo y conecte los <strong>puertos src/sink</strong> entre nodos para construir el pipeline. Arrastre el espacio vacío del lienzo para desplazar la vista.' },
          beforeStep: function () {
            pollFor('.palette-item', function () {
              var item = document.querySelector('.palette-item');
              if (item) item.scrollIntoView({ behavior: 'smooth', block: 'center' });
            });
          } },
        { target: '#pipeline-canvas', position: 'top',
          title: { ko: '캔버스', en: 'Canvas', ja: 'キャンバス', 'zh-CN': '画布', 'zh-TW': '畫布', es: 'Lienzo' },
          content: { ko: '노드를 <strong>드래그하여 배치</strong>하고, 포트 사이를 연결하여 엣지를 만듭니다. 마우스 휠로 줌, 빈 영역 드래그로 이동합니다.', en: '<strong>Drag nodes</strong> to place them, connect ports to create edges. Mouse wheel to zoom, drag empty area to pan.', ja: 'ノードを<strong>ドラッグして配置</strong>し、ポート間を接続してエッジを作成します。マウスホイールでズーム、空白エリアドラッグで移動します。', 'zh-CN': '<strong>拖拽节点</strong>放置，连接端口创建边。鼠标滚轮缩放，拖拽空白区域平移。', 'zh-TW': '<strong>拖曳節點</strong>放置，連接連接埠建立邊。滑鼠滾輪縮放，拖曳空白區域平移。', es: '<strong>Arrastre nodos</strong> para colocarlos y conecte puertos para crear aristas. Rueda del ratón para zoom; arrastre el área vacía para desplazarse.' } },
        { target: '#canvas-toolbar', position: 'bottom',
          title: { ko: '캔버스 도구', en: 'Canvas Tools', ja: 'キャンバスツール', 'zh-CN': '画布工具', 'zh-TW': '畫布工具', es: 'Herramientas del lienzo' },
          content: { ko: '<strong>확대(+), 축소(-), 전체보기(⊞), 초기화(🗑)</strong> 버튼으로 뷰를 조절합니다.', en: 'Adjust view with <strong>zoom in(+), zoom out(-), fit all(⊞), clear(🗑)</strong> buttons.', ja: '<strong>拡大(+)、縮小(-)、全体表示(⊞)、クリア(🗑)</strong>ボタンでビューを調整します。', 'zh-CN': '使用<strong>放大(+)、缩小(-)、全屏显示(⊞)、清除(🗑)</strong>按钮调整视图。', 'zh-TW': '使用<strong>放大(+)、縮小(-)、全體顯示(⊞)、清除(🗑)</strong>按鈕調整視圖。', es: 'Ajuste la vista con los botones <strong>acercar (+), alejar (-), ajustar todo (⊞) y borrar (🗑)</strong>.' } },
        { target: '#canvas-minimap', position: 'left',
          title: { ko: '미니맵', en: 'Minimap', ja: 'ミニマップ', 'zh-CN': '小地图', 'zh-TW': '小地圖', es: 'Minimapa' },
          content: { ko: '전체 캔버스의 <strong>축소 뷰</strong>와 현재 뷰포트 위치를 보여줍니다. 클릭으로 빠르게 이동할 수 있습니다.', en: 'Shows a <strong>zoomed-out view</strong> of the entire canvas and current viewport. Click to navigate quickly.', ja: 'キャンバス全体の<strong>縮小ビュー</strong>と現在のビューポート位置を表示します。クリックで素早く移動できます。', 'zh-CN': '显示整个画布的<strong>缩小视图</strong>和当前视口位置。点击可快速导航。', 'zh-TW': '顯示整個畫布的<strong>縮小視圖</strong>和當前視口位置。點擊可快速導航。', es: 'Muestra una <strong>vista alejada</strong> de todo el lienzo y la ventana visible actual. Haga clic para navegar rápidamente.' } },
        { target: '#property-panel', position: 'left',
          title: { ko: '속성 패널', en: 'Properties Panel', ja: 'プロパティパネル', 'zh-CN': '属性面板', 'zh-TW': '屬性面板', es: 'Panel de propiedades' },
          content: { ko: '캔버스에서 노드를 선택하면 해당 요소의 <strong>속성을 편집</strong>할 수 있습니다.', en: 'Select a node on canvas to <strong>edit its properties</strong>.', ja: 'キャンバスでノードを選択すると、そのエレメントの<strong>プロパティを編集</strong>できます。', 'zh-CN': '在画布上选择节点后，可<strong>编辑该元素的属性</strong>。', 'zh-TW': '在畫布上選擇節點後，可<strong>編輯該元素的屬性</strong>。', es: 'Seleccione un nodo en el lienzo para <strong>editar sus propiedades</strong>.' },
          beforeStep: function () { _prepPropertyPanel(); } },
        { target: '#pipeline-command-output', position: 'top',
          title: { ko: 'GStreamer 명령어', en: 'GStreamer Command', ja: 'GStreamerコマンド', 'zh-CN': 'GStreamer命令', 'zh-TW': 'GStreamer指令', es: 'Comando GStreamer' },
          content: { ko: '캔버스의 파이프라인 구성에서 <strong>자동 생성된 gst-launch 커맨드</strong>입니다. 복사하여 터미널에서 직접 실행할 수 있습니다.', en: '<strong>Auto-generated gst-launch command</strong> from the canvas pipeline. Copy to run directly in terminal.', ja: 'キャンバスのパイプライン構成から<strong>自動生成されたgst-launchコマンド</strong>です。コピーしてターミナルで直接実行できます。', 'zh-CN': '来自画布管道配置的<strong>自动生成的gst-launch命令</strong>。复制后可直接在终端运行。', 'zh-TW': '來自畫布管線配置的<strong>自動產生的gst-launch指令</strong>。複製後可直接在終端機執行。', es: '<strong>Comando gst-launch generado automáticamente</strong> a partir del pipeline del lienzo. Cópielo para ejecutarlo directamente en la terminal.' } },
        { target: '#canvas-toolbar', position: 'bottom',
          title: { ko: '키보드 단축키', en: 'Keyboard Shortcuts', ja: 'キーボードショートカット', 'zh-CN': '键盘快捷键', 'zh-TW': '鍵盤快捷鍵', es: 'Atajos de teclado' },
          content: { ko: '<strong>Ctrl+Z</strong> 실행취소, <strong>Ctrl+Shift+Z</strong> 다시실행, <strong>Delete</strong> 선택 삭제, <strong>마우스 휠</strong> 줌. 캔버스 도구 바 근처에서 단축키를 사용합니다.', en: '<strong>Ctrl+Z</strong> undo, <strong>Ctrl+Shift+Z</strong> redo, <strong>Delete</strong> remove selected, <strong>mouse wheel</strong> zoom. Use these shortcuts while the canvas is focused.', ja: '<strong>Ctrl+Z</strong> 元に戻す、<strong>Ctrl+Shift+Z</strong> やり直し、<strong>Delete</strong> 選択削除、<strong>マウスホイール</strong> ズーム。キャンバスにフォーカスした状態で使用します。', 'zh-CN': '<strong>Ctrl+Z</strong> 撤销，<strong>Ctrl+Shift+Z</strong> 重做，<strong>Delete</strong> 删除选中，<strong>鼠标滚轮</strong> 缩放。在画布聚焦时使用这些快捷键。', 'zh-TW': '<strong>Ctrl+Z</strong> 復原，<strong>Ctrl+Shift+Z</strong> 重做，<strong>Delete</strong> 刪除選取，<strong>滑鼠滾輪</strong> 縮放。在畫布聚焦時使用這些快捷鍵。', es: '<strong>Ctrl+Z</strong> deshacer, <strong>Ctrl+Shift+Z</strong> rehacer, <strong>Supr</strong> eliminar selección, <strong>rueda del ratón</strong> zoom. Úselos con el lienzo enfocado.' } },
      ]
    },

    { id: 'models', icon: '📦',
      title: { ko: '📦 모델 카탈로그', en: '📦 Model Catalog', ja: '📦 モデルカタログ', 'zh-CN': '📦 模型目录', 'zh-TW': '📦 模型目錄', es: '📦 Catálogo de modelos' },
      description: { ko: '설치된 모델 검색 및 상세 보기', en: 'Search installed models and view details', ja: 'インストール済みモデルの検索と詳細表示', 'zh-CN': '搜索已安装的模型并查看详情', 'zh-TW': '搜尋已安裝的模型並查看詳細資訊', es: 'Busque modelos instalados y consulte detalles' },
      beforeStart: function () { goPage('models'); },
      steps: [
        { target: '#models-filter-bar', position: 'bottom',
          title: { ko: '카테고리 필터', en: 'Category Filter', ja: 'カテゴリフィルター', 'zh-CN': '类别筛选', 'zh-TW': '類別篩選', es: 'Filtro por categoría' },
          content: { ko: '<strong>9개 카테고리 필터 칩</strong>으로 모델을 필터링합니다. OBB 회전 바운딩 박스 모델 필터도 포함됩니다.', en: 'Filter models with <strong>9 category filter chips</strong>. Includes OBB (oriented bounding box) model filter.', ja: '<strong>9つのカテゴリフィルターチップ</strong>でモデルをフィルタリングします。OBB（回転バウンディングボックス）モデルフィルターも含みます。', 'zh-CN': '使用<strong>9个类别筛选标签</strong>筛选模型。包含OBB（定向边界框）模型筛选。', 'zh-TW': '使用<strong>9個類別篩選標籤</strong>篩選模型。包含OBB（定向邊界框）模型篩選。', es: 'Filtre modelos con <strong>9 chips de categoría</strong>. Incluye filtro de modelos OBB (cuadro delimitador orientado).' } },
        { target: '#models-search', position: 'bottom',
          title: { ko: '모델 검색', en: 'Model Search', ja: 'モデル検索', 'zh-CN': '模型搜索', 'zh-TW': '模型搜尋', es: 'Búsqueda de modelos' },
          content: { ko: '이름/카테고리로 <strong>실시간 검색</strong>합니다.', en: '<strong>Real-time search</strong> by name/category.', ja: '名前/カテゴリで<strong>リアルタイム検索</strong>します。', 'zh-CN': '按名称/类别<strong>实时搜索</strong>。', 'zh-TW': '按名稱/類別<strong>即時搜尋</strong>。', es: '<strong>Búsqueda en tiempo real</strong> por nombre/categoría.' } },
        { target: '#models-grid', position: 'bottom',
          title: { ko: '모델 카드', en: 'Model Cards', ja: 'モデルカード', 'zh-CN': '模型卡片', 'zh-TW': '模型卡片', es: 'Tarjetas de modelo' },
          content: { ko: '카드를 클릭하면 <strong>모델 상세 모달</strong>이 열립니다.', en: 'Click a card to open the <strong>model detail modal</strong>.', ja: 'カードをクリックすると<strong>モデル詳細モーダル</strong>が開きます。', 'zh-CN': '点击卡片打开<strong>模型详情弹窗</strong>。', 'zh-TW': '點擊卡片開啟<strong>模型詳情彈窗</strong>。', es: 'Haga clic en una tarjeta para abrir el <strong>modal de detalle del modelo</strong>.' },
          beforeStep: function () { closeModelDetailModal(); } },
        { target: '#model-detail-modal .modal', position: 'right',
          title: { ko: '모델 상세 모달', en: 'Model Detail Modal', ja: 'モデル詳細モーダル', 'zh-CN': '模型详情弹窗', 'zh-TW': '模型詳情彈窗', es: 'Modal de detalle del modelo' },
          content: { ko: '모델 카드를 클릭하면 열리는 <strong>상세 모달</strong>입니다. <strong>이름, 카테고리, 파일 크기, 다운로드 상태, 경로</strong>를 확인하고 상단 탭에서 Detail과 Metadata를 전환합니다.', en: 'The <strong>detail modal</strong> opened from a model card. View <strong>name, category, file size, download status, path</strong> and switch between Detail and Metadata tabs at the top.', ja: 'モデルカードから開く<strong>詳細モーダル</strong>です。<strong>名前、カテゴリ、ファイルサイズ、ダウンロード状態、パス</strong>を確認し、上部タブでDetailとMetadataを切り替えます。', 'zh-CN': '点击模型卡片打开的<strong>详情弹窗</strong>。查看<strong>名称、类别、文件大小、下载状态、路径</strong>，并通过顶部标签在 Detail 和 Metadata 之间切换。', 'zh-TW': '點擊模型卡片開啟的<strong>詳情彈窗</strong>。查看<strong>名稱、類別、檔案大小、下載狀態、路徑</strong>，並透過頂部標籤在 Detail 和 Metadata 之間切換。', es: 'El <strong>modal de detalle</strong> que se abre desde una tarjeta de modelo. Consulte <strong>nombre, categoría, tamaño de archivo, estado de descarga y ruta</strong> y cambie entre las pestañas Detail y Metadata arriba.' },
          beforeStep: function () { openModelDetailModal(); },
          afterStep: function () { closeModelDetailModal(); } },
        { target: '#model-tab-metadata', position: 'top',
          title: { ko: '메타데이터 탭', en: 'Metadata Tab', ja: 'メタデータタブ', 'zh-CN': '元数据选项卡', 'zh-TW': '元資料頁籤', es: 'Pestaña de metadatos' },
          content: { ko: '<strong>메타데이터</strong> 탭을 클릭하면 .dxnn 모델 파일의 <strong>입출력 텐서, 레이어 수, 컴파일 정보</strong>를 확인할 수 있습니다. dx_engine의 parse_model을 내부적으로 실행합니다.', en: 'Click the <strong>Metadata</strong> tab to view the .dxnn model\'s <strong>input/output tensors, layer count, compilation info</strong>. Runs dx_engine parse_model internally.', ja: '<strong>メタデータ</strong>タブをクリックすると.dxnnモデルファイルの<strong>入出力テンソル、レイヤー数、コンパイル情報</strong>を確認できます。内部的にdx_engineのparse_modelを実行します。', 'zh-CN': '点击<strong>元数据</strong>选项卡查看.dxnn模型文件的<strong>输入/输出张量、层数、编译信息</strong>。内部运行dx_engine parse_model。', 'zh-TW': '點擊<strong>元資料</strong>頁籤查看.dxnn模型檔案的<strong>輸入/輸出張量、層數、編譯資訊</strong>。內部執行dx_engine parse_model。', es: 'Haga clic en la pestaña <strong>Metadatos</strong> para ver los <strong>tensores de entrada/salida, número de capas e información de compilación</strong> del modelo .dxnn. Ejecuta internamente dx_engine parse_model.' },
          beforeStep: function () {
            openModelDetailModal();
            var tab = document.querySelector('.modal-tab[data-tab="metadata"]');
            if (tab) tab.click();
          },
          afterStep: function () {
            closeModelDetailModal();
            var tab = document.querySelector('.modal-tab[data-tab="detail"]');
            if (tab) tab.click();
          } },
        { target: '#model-detail-download-btn', position: 'top',
          title: { ko: '모델 다운로드', en: 'Download Model', ja: 'モデルダウンロード', 'zh-CN': '下载模型', 'zh-TW': '下載模型', es: 'Descargar modelo' },
          content: { ko: '상세 모달에서 선택한 모델 파일을 <strong>다운로드</strong>합니다. 이미 설치된 모델은 ✅로 표시됩니다.', en: '<strong>Download</strong> the selected model file from the detail modal. Already installed models show ✅.', ja: '詳細モーダルから選択したモデルファイルを<strong>ダウンロード</strong>します。インストール済みモデルは✅で表示されます。', 'zh-CN': '从详情弹窗<strong>下载</strong>所选模型文件。已安装的模型显示✅。', 'zh-TW': '從詳情彈窗<strong>下載</strong>所選模型檔案。已安裝的模型顯示✅。', es: '<strong>Descargue</strong> el archivo del modelo seleccionado desde el modal de detalle. Los modelos ya instalados muestran ✅.' },
          beforeStep: function () { openModelDetailModal(); },
          afterStep: function () { closeModelDetailModal(); } },
        { target: '#dxt-stream-mock-download-btn', position: 'top',
          title: { ko: '개별 모델 다운로드', en: 'Individual Download', ja: '個別ダウンロード', 'zh-CN': '单个下载', 'zh-TW': '個別下載', es: 'Descarga individual' },
          content: { ko: '모델 카드마다 <strong>⬇️ 다운로드</strong> 버튼이 있습니다. 원하는 모델만 선택적으로 설치할 수 있습니다. 다운로드 중에는 ⏳ 표시, 완료 후 ✅ 배지로 전환됩니다.', en: 'Each model card has an <strong>⬇️ Download</strong> button. Install only the models you need. Shows ⏳ while downloading, then ✅ badge on completion.', ja: '各モデルカードに<strong>⬇️ ダウンロード</strong>ボタンがあります。必要なモデルのみ選択的にインストールできます。ダウンロード中は⏳表示、完了後✅バッジに変わります。', 'zh-CN': '每张模型卡片有<strong>⬇️ Download</strong>按钮。只安装所需的模型。下载中显示⏳，完成后显示✅徽章。', 'zh-TW': '每張模型卡片有<strong>⬇️ 下載</strong>按鈕。只安裝所需的模型。下載中顯示⏳，完成後顯示✅徽章。', es: 'Cada tarjeta de modelo tiene un botón <strong>⬇️ Descargar</strong>. Instale solo los modelos que necesite. Muestra ⏳ durante la descarga y ✅ al completarse.' },
          beforeStep: function () { _prepModelsGridDownloadDemo(); },
          afterStep: function () { _clearModelsGridDownloadDemo(); } },
      ]
    },

    { id: 'elements', icon: '🧩',
      title: { ko: '🧩 요소 레퍼런스', en: '🧩 Element Reference', ja: '🧩 エレメントリファレンス', 'zh-CN': '🧩 元素参考', 'zh-TW': '🧩 元素參考', es: '🧩 Referencia de elementos' },
      description: { ko: 'GStreamer 요소 검색 및 상세', en: 'Search and view GStreamer elements', ja: 'GStreamerエレメントの検索と表示', 'zh-CN': '搜索并查看GStreamer元素', 'zh-TW': '搜尋並查看GStreamer元素', es: 'Busque y consulte elementos GStreamer' },
      beforeStart: function () { goPage('elements'); },
      steps: [
        { target: '#elements-search', position: 'bottom',
          title: { ko: '요소 검색', en: 'Element Search', ja: 'エレメント検索', 'zh-CN': '元素搜索', 'zh-TW': '元素搜尋', es: 'Búsqueda de elementos' },
          content: { ko: '이름/카테고리로 <strong>실시간 검색</strong>합니다.', en: '<strong>Real-time search</strong> by name/category.', ja: '名前/カテゴリで<strong>リアルタイム検索</strong>します。', 'zh-CN': '按名称/类别<strong>实时搜索</strong>。', 'zh-TW': '按名稱/類別<strong>即時搜尋</strong>。', es: '<strong>Búsqueda en tiempo real</strong> por nombre/categoría.' } },
        { target: '#elements-filter-bar', position: 'bottom',
          title: { ko: '카테고리 필터', en: 'Category Filter', ja: 'カテゴリフィルター', 'zh-CN': '类别筛选', 'zh-TW': '類別篩選', es: 'Filtro por categoría' },
          content: { ko: '<strong>10개 카테고리</strong>(전처리, 후처리, 소스, 싱크, 디먹서, 먹서, 파서, 인코더, 디코더, 유틸리티)로 필터링합니다.', en: 'Filter by <strong>10 categories</strong> (preprocessing, postprocessing, source, sink, demuxer, muxer, parser, encoder, decoder, utility).', ja: '<strong>10のカテゴリ</strong>(前処理、後処理、ソース、シンク、デマルチプレクサ、マルチプレクサ、パーサー、エンコーダー、デコーダー、ユーティリティ)でフィルタリングします。', 'zh-CN': '按<strong>10个类别</strong>（预处理、后处理、源、汇（接收端）、解复用器、复用器、解析器、编码器、解码器、工具）筛选。', 'zh-TW': '按<strong>10個類別</strong>（前處理、後處理、來源、接收、解多工器、多工器、解析器、編碼器、解碼器、工具）篩選。', es: 'Filtre por <strong>10 categorías</strong> (preprocesado, postprocesado, fuente, sink, demuxer, muxer, parser, codificador, decodificador y utilidad).' } },
        { target: '#elements-grid', position: 'bottom',
          title: { ko: '요소 카드', en: 'Element Cards', ja: 'エレメントカード', 'zh-CN': '元素卡片', 'zh-TW': '元素卡片', es: 'Tarjetas de elemento' },
          content: { ko: '각 카드에 <strong>이름, 카테고리 배지, 설명, 속성 수</strong>가 표시됩니다. 클릭하면 상세 정보를 볼 수 있습니다.', en: 'Each card shows <strong>name, category badge, description, property count</strong>. Click for details.', ja: '各カードに<strong>名前、カテゴリバッジ、説明、プロパティ数</strong>が表示されます。クリックで詳細情報を見られます。', 'zh-CN': '每张卡片显示<strong>名称、类别徽章、描述、属性数量</strong>。点击查看详情。', 'zh-TW': '每張卡片顯示<strong>名稱、類別徽章、描述、屬性數量</strong>。點擊查看詳情。', es: 'Cada tarjeta muestra <strong>nombre, insignia de categoría, descripción y número de propiedades</strong>. Haga clic para ver detalles.' } },
        { target: '#element-detail', position: 'top',
          title: { ko: '요소 상세', en: 'Element Detail', ja: 'エレメント詳細', 'zh-CN': '元素详情', 'zh-TW': '元素詳情', es: 'Detalle del elemento' },
          content: { ko: '<strong>설명, 속성 테이블, 패드 방향</strong>(src/sink) 정보를 확인합니다. 파이프라인 빌더에서 이 요소를 사용할 때 참고하세요.', en: 'View <strong>description, properties table, pad direction</strong> (src/sink). Reference this when using the element in the pipeline builder.', ja: '<strong>説明、プロパティテーブル、パッド方向</strong>(src/sink)情報を確認します。パイプラインビルダーでこのエレメントを使用する際の参考にしてください。', 'zh-CN': '查看<strong>描述、属性表、端口方向</strong>(src/sink)信息。在管道构建器中使用该元素时作为参考。', 'zh-TW': '查看<strong>描述、屬性表、連接埠方向</strong>(src/sink)資訊。在管線建構器中使用該元素時作為參考。', es: 'Consulte <strong>descripción, tabla de propiedades y dirección de pads</strong> (src/sink). Úselo como referencia al emplear el elemento en el constructor de pipelines.' },
          beforeStep: function () { _prepElementDetail(); } },
        { target: '#palette-panel', position: 'right',
          title: { ko: '요소 활용', en: 'Element Usage', ja: 'エレメント活用', 'zh-CN': '元素使用', 'zh-TW': '元素使用', es: 'Uso del elemento' },
          content: { ko: '요소는 <strong>파이프라인 빌더</strong>의 팔레트에서 드래그하여 캔버스에 배치합니다. 여기서 확인한 속성을 속성 패널에서 설정할 수 있습니다.', en: 'Drag elements from the <strong>pipeline builder</strong> palette onto the canvas. Properties viewed here can be configured in the property panel.', ja: 'エレメントは<strong>パイプラインビルダー</strong>のパレットからドラッグしてキャンバスに配置します。ここで確認したプロパティをプロパティパネルで設定できます。', 'zh-CN': '从<strong>管道构建器</strong>面板拖拽元素到画布上放置。这里查看的属性可在属性面板中配置。', 'zh-TW': '從<strong>管線建構器</strong>面板拖曳元素到畫布上放置。這裡查看的屬性可在屬性面板中設定。', es: 'Arrastre elementos desde la paleta del <strong>constructor de pipelines</strong> al lienzo. Las propiedades consultadas aquí se configuran en el panel de propiedades.' },
          beforeStep: function () { goPage('pipeline'); } },
      ]
    },

    { id: 'setup', icon: '⚙️',
      title: { ko: '⚙️ 설정 & 설치', en: '⚙️ Setup & Install', ja: '⚙️ 設定 & インストール', 'zh-CN': '⚙️ 设置 & 安装', 'zh-TW': '⚙️ 設定 & 安裝', es: '⚙️ Configuración e instalación' },
      description: { ko: '시스템 설정 및 종속성 설치', en: 'System setup and dependency installation', ja: 'システム設定と依存関係のインストール', 'zh-CN': '系统设置和依赖安装', 'zh-TW': '系統設定和相依性安裝', es: 'Configuración del sistema e instalación de dependencias' },
      beforeStart: function () { goPage('setup'); },
      steps: [
        { target: '#setup-info-bar', position: 'bottom',
          title: { ko: '시스템 정보', en: 'System Info', ja: 'システム情報', 'zh-CN': '系统信息', 'zh-TW': '系統資訊', es: 'Información del sistema' },
          content: { ko: '<strong>OS, GStreamer 버전, NPU, Python 버전</strong> 등 현재 시스템 정보를 표시합니다.', en: 'Shows current system info: <strong>OS, GStreamer version, NPU, Python version</strong>.', ja: '現在のシステム情報を表示します：<strong>OS、GStreamerバージョン、NPU、Pythonバージョン</strong>。', 'zh-CN': '显示当前系统信息：<strong>OS、GStreamer版本、NPU、Python版本</strong>。', 'zh-TW': '顯示當前系統資訊：<strong>OS、GStreamer版本、NPU、Python版本</strong>。', es: 'Muestra la información actual del sistema: <strong>SO, versión de GStreamer, NPU y versión de Python</strong>.' } },
        { target: '.setup-grid', position: 'bottom',
          title: { ko: '설치 카드', en: 'Setup Cards', ja: 'セットアップカード', 'zh-CN': '安装卡片', 'zh-TW': '安裝卡片', es: 'Tarjetas de configuración' },
          content: { ko: '<strong>6개 설치/빌드 카드</strong>를 순서대로 실행합니다. 각 카드의 Install/Build 버튼을 클릭하세요.', en: 'Execute <strong>6 install/build cards</strong> in order. Click Install/Build on each card.', ja: '<strong>6つのインストール/ビルドカード</strong>を順番に実行します。各カードのInstall/Buildボタンをクリックしてください。', 'zh-CN': '按顺序执行<strong>6个安装/构建卡片</strong>。点击每张卡片的Install/Build按钮。', 'zh-TW': '按順序執行<strong>6個安裝/建構卡片</strong>。點擊每張卡片的Install/Build按鈕。', es: 'Ejecute <strong>6 tarjetas de instalación/compilación</strong> en orden. Haga clic en Install/Build en cada tarjeta.' } },
        { target: 'button[onclick*="stream-deps"]', position: 'bottom',
          title: { ko: '빌드 도구 설치', en: 'Install Build Tools', ja: 'ビルドツールのインストール', 'zh-CN': '安装构建工具', 'zh-TW': '安裝建置工具', es: 'Instalar herramientas de compilación' },
          content: { ko: '①번 카드입니다. GStreamer 플러그인 빌드에 필요한 <strong>cmake·meson·GStreamer·OpenCV</strong> 등을 install.sh로 설치합니다. <strong>Build(④)보다 먼저</strong> 실행하세요.', en: 'Card ①. Installs <strong>cmake, meson, GStreamer, OpenCV</strong> and other build dependencies via install.sh. Run this <strong>before Build (④)</strong>.', ja: '①番カードです。GStreamerプラグインのビルドに必要な<strong>cmake・meson・GStreamer・OpenCV</strong>などをinstall.shでインストールします。<strong>Build(④)より前に</strong>実行してください。', 'zh-CN': '①号卡片。通过install.sh安装构建GStreamer插件所需的<strong>cmake、meson、GStreamer、OpenCV</strong>等。请在<strong>Build(④)之前</strong>运行。', 'zh-TW': '①號卡片。透過install.sh安裝建置GStreamer外掛程式所需的<strong>cmake、meson、GStreamer、OpenCV</strong>等。請在<strong>Build(④)之前</strong>執行。', es: 'Tarjeta ①. Instala <strong>cmake, meson, GStreamer, OpenCV</strong> y otras dependencias de compilación mediante install.sh. Ejecútelo <strong>antes de Build (④)</strong>.' },
          beforeStep: function () { _scrollToTarget('button[onclick*="stream-deps"]'); } },
        { target: '#setup-badge-runtime', position: 'bottom',
          title: { ko: 'Runtime 상태 배지', en: 'Runtime Status Badge', ja: 'ランタイム状態バッジ', 'zh-CN': '运行时状态徽章', 'zh-TW': '執行時期狀態徽章', es: 'Insignia de estado de runtime' },
          content: { ko: '②번 카드의 <strong>설치 상태 배지</strong>입니다. ✅이면 DX-Runtime 종속성 설치가 완료된 것입니다.', en: 'The <strong>install status badge</strong> on card ②. ✅ means DX-Runtime dependencies are installed.', ja: '②番カードの<strong>インストール状態バッジ</strong>です。✅ならDX-Runtime依存関係のインストールが完了しています。', 'zh-CN': '②号卡片的<strong>安装状态徽章</strong>。✅表示DX-Runtime依赖已安装完成。', 'zh-TW': '②號卡片的<strong>安裝狀態徽章</strong>。✅表示DX-Runtime相依性已安裝完成。', es: 'La <strong>insignia de estado de instalación</strong> de la tarjeta ②. ✅ indica que las dependencias DX-Runtime están instaladas.' },
          beforeStep: function () { _scrollToTarget('#setup-badge-runtime'); } },
        { target: 'button[onclick*="runtime-deps"]', position: 'bottom',
          title: { ko: 'Runtime 설치', en: 'Install Runtime', ja: 'ランタイムインストール', 'zh-CN': '安装运行时', 'zh-TW': '安裝執行時期', es: 'Instalar runtime' },
          content: { ko: '<strong>DX-Runtime 종속성</strong> 패키지를 설치합니다. GStreamer 플러그인 실행에 필요한 기본 패키지입니다.', en: 'Install <strong>DX-Runtime dependency</strong> packages required for GStreamer plugin execution.', ja: 'GStreamerプラグイン実行に必要な<strong>DX-Runtime依存関係</strong>パッケージをインストールします。', 'zh-CN': '安装 GStreamer 插件运行所需的 <strong>DX-Runtime 依赖</strong>包。', 'zh-TW': '安裝 GStreamer 外掛程式執行所需的 <strong>DX-Runtime 相依性</strong>套件。', es: 'Instale los paquetes de <strong>dependencias DX-Runtime</strong> necesarios para ejecutar plugins GStreamer.' },
          beforeStep: function () { _scrollToTarget('button[onclick*="runtime-deps"]'); } },
        { target: '#setup-badge-driver', position: 'bottom',
          title: { ko: 'NPU 드라이버 상태', en: 'NPU Driver Status', ja: 'NPUドライバー状態', 'zh-CN': 'NPU驱动状态', 'zh-TW': 'NPU驅動程式狀態', es: 'Estado del controlador NPU' },
          content: { ko: '③번 카드의 <strong>드라이버 설치 상태</strong> 배지입니다. ✅이면 NPU 드라이버가 준비된 것입니다.', en: 'The <strong>driver install status</strong> badge on card ③. ✅ means the NPU driver is ready.', ja: '③番カードの<strong>ドライバーインストール状態</strong>バッジです。✅ならNPUドライバーの準備が完了しています。', 'zh-CN': '③号卡片的<strong>驱动安装状态</strong>徽章。✅表示NPU驱动已就绪。', 'zh-TW': '③號卡片的<strong>驅動程式安裝狀態</strong>徽章。✅表示NPU驅動程式已就緒。', es: 'La insignia de <strong>estado de instalación del controlador</strong> en la tarjeta ③. ✅ indica que el controlador NPU está listo.' },
          beforeStep: function () { _scrollToTarget('#setup-badge-driver'); } },
        { target: 'button[onclick*="driver"]', position: 'bottom',
          title: { ko: 'NPU 드라이버 설치', en: 'Install NPU Driver', ja: 'NPUドライバーインストール', 'zh-CN': '安装NPU驱动', 'zh-TW': '安裝NPU驅動程式', es: 'Instalar controlador NPU' },
          content: { ko: '리눅스 <strong>NPU 드라이버</strong>를 설치합니다. sudo 비밀번호가 필요할 수 있습니다.', en: 'Install the Linux <strong>NPU driver</strong>. May require a sudo password.', ja: 'Linux <strong>NPUドライバー</strong>をインストールします。sudoパスワードが必要な場合があります。', 'zh-CN': '安装 Linux <strong>NPU 驱动</strong>。可能需要 sudo 密码。', 'zh-TW': '安裝 Linux <strong>NPU 驅動程式</strong>。可能需要 sudo 密碼。', es: 'Instale el <strong>controlador del NPU</strong> en Linux. Puede requerir contraseña sudo.' },
          beforeStep: function () { _scrollToTarget('button[onclick*="driver"]'); } },
        { target: '#setup-badge-build', position: 'bottom',
          title: { ko: '플러그인 빌드 상태', en: 'Plugin Build Status', ja: 'プラグインビルド状態', 'zh-CN': '插件构建状态', 'zh-TW': '外掛程式建構狀態', es: 'Estado de compilación de plugins' },
          content: { ko: '④번 카드의 <strong>빌드 상태</strong> 배지입니다. ✅이면 GStreamer 플러그인 빌드가 완료된 것입니다.', en: 'The <strong>build status</strong> badge on card ④. ✅ means GStreamer plugins are built.', ja: '④番カードの<strong>ビルド状態</strong>バッジです。✅ならGStreamerプラグインのビルドが完了しています。', 'zh-CN': '④号卡片的<strong>构建状态</strong>徽章。✅表示GStreamer插件已构建完成。', 'zh-TW': '④號卡片的<strong>建構狀態</strong>徽章。✅表示GStreamer外掛程式已建構完成。', es: 'La insignia de <strong>estado de compilación</strong> en la tarjeta ④. ✅ indica que los plugins GStreamer están compilados.' },
          beforeStep: function () { _scrollToTarget('#setup-badge-build'); } },
        { target: '#setup-opt-clean', position: 'bottom',
          title: { ko: '빌드 옵션', en: 'Build Options', ja: 'ビルドオプション', 'zh-CN': '构建选项', 'zh-TW': '建構選項', es: 'Opciones de compilación' },
          content: { ko: '<strong>클린 빌드</strong>와 <strong>디버그 모드</strong> 체크박스를 선택할 수 있습니다. 클린 빌드는 이전 빌드를 삭제 후 재빌드, 디버그 모드는 심볼 포함 빌드입니다.', en: 'Select <strong>Clean Build</strong> and <strong>Debug Mode</strong> checkboxes. Clean build removes previous builds; debug mode includes symbols.', ja: '<strong>クリーンビルド</strong>と<strong>デバッグモード</strong>チェックボックスを選択できます。クリーンビルドは以前のビルドを削除後に再ビルド、デバッグモードはシンボルを含むビルドです。', 'zh-CN': '可选择<strong>清理构建</strong>和<strong>调试模式</strong>复选框。清理构建删除之前的构建后重建；调试模式包含符号。', 'zh-TW': '可選擇<strong>清潔建構</strong>和<strong>偵錯模式</strong>核取方塊。清潔建構刪除之前的建構後重建；偵錯模式包含符號。', es: 'Seleccione las casillas <strong>Compilación limpia</strong> y <strong>Modo depuración</strong>. La compilación limpia elimina compilaciones anteriores; el modo depuración incluye símbolos.' },
          beforeStep: function () { _scrollToTarget('#setup-opt-clean'); } },
        { target: 'button[onclick*="build"]', position: 'bottom',
          title: { ko: '플러그인 빌드', en: 'Build Plugins', ja: 'プラグインビルド', 'zh-CN': '构建插件', 'zh-TW': '建構外掛程式', es: 'Compilar plugins' },
          content: { ko: '<strong>GStreamer 플러그인</strong>을 빌드합니다. 위 옵션을 선택한 뒤 Build 버튼을 클릭하세요.', en: 'Build <strong>GStreamer plugins</strong>. Choose options above, then click Build.', ja: '<strong>GStreamerプラグイン</strong>をビルドします。上のオプションを選択してからBuildボタンをクリックしてください。', 'zh-CN': '构建<strong>GStreamer插件</strong>。选择上方选项后点击Build按钮。', 'zh-TW': '建構<strong>GStreamer外掛程式</strong>。選擇上方選項後點擊Build按鈕。', es: 'Compile <strong>plugins GStreamer</strong>. Elija las opciones de arriba y haga clic en Build.' },
          beforeStep: function () { _scrollToTarget('button[onclick*="build"]'); } },
        { target: '#setup-badge-download', position: 'bottom',
          title: { ko: '모델 다운로드 상태', en: 'Model Download Status', ja: 'モデルダウンロード状態', 'zh-CN': '模型下载状态', 'zh-TW': '模型下載狀態', es: 'Estado de descarga de modelos' },
          content: { ko: '⑤번 카드의 <strong>다운로드 상태</strong> 배지입니다. ✅이면 모델과 샘플 비디오가 준비된 것입니다.', en: 'The <strong>download status</strong> badge on card ⑤. ✅ means models and sample videos are ready.', ja: '⑤番カードの<strong>ダウンロード状態</strong>バッジです。✅ならモデルとサンプルビデオの準備が完了しています。', 'zh-CN': '⑤号卡片的<strong>下载状态</strong>徽章。✅表示模型和示例视频已就绪。', 'zh-TW': '⑤號卡片的<strong>下載狀態</strong>徽章。✅表示模型和範例影片已就緒。', es: 'La insignia de <strong>estado de descarga</strong> en la tarjeta ⑤. ✅ indica que modelos y vídeos de muestra están listos.' },
          beforeStep: function () { _scrollToTarget('#setup-badge-download'); } },
        { target: 'button[onclick*="download-models"]', position: 'bottom',
          title: { ko: '모델/비디오 다운로드', en: 'Download Models & Videos', ja: 'モデル/ビデオダウンロード', 'zh-CN': '下载模型和视频', 'zh-TW': '下載模型和影片', es: 'Descargar modelos y vídeos' },
          content: { ko: '추론에 필요한 <strong>모델과 샘플 비디오</strong>를 다운로드합니다.', en: 'Download <strong>models and sample videos</strong> required for inference.', ja: '推論に必要な<strong>モデルとサンプルビデオ</strong>をダウンロードします。', 'zh-CN': '下载推理所需的<strong>模型和示例视频</strong>。', 'zh-TW': '下載推論所需的<strong>模型和範例影片</strong>。', es: 'Descargue <strong>modelos y vídeos de muestra</strong> necesarios para la inferencia.' },
          beforeStep: function () { _scrollToTarget('button[onclick*="download-models"]'); } },
        { target: '#setup-badge-webrtc-deps', position: 'bottom',
          title: { ko: 'WebRTC 상태', en: 'WebRTC Status', ja: 'WebRTC状態', 'zh-CN': 'WebRTC状态', 'zh-TW': 'WebRTC狀態', es: 'Estado de WebRTC' },
          content: { ko: '⑤번 카드의 <strong>WebRTC 의존성 상태</strong> 배지입니다. ✅이면 브라우저 시각화 패키지가 준비된 것입니다.', en: 'The <strong>WebRTC dependency status</strong> badge on card ⑤. ✅ means browser visualization packages are ready.', ja: '⑤番カードの<strong>WebRTC依存関係状態</strong>バッジです。✅ならブラウザ可視化パッケージの準備が完了しています。', 'zh-CN': '⑤号卡片的<strong>WebRTC依赖状态</strong>徽章。✅表示浏览器可视化包已就绪。', 'zh-TW': '⑤號卡片的<strong>WebRTC相依性狀態</strong>徽章。✅表示瀏覽器視覺化套件已就緒。', es: 'La insignia de <strong>estado de dependencias WebRTC</strong> en la tarjeta ⑤. ✅ indica que los paquetes de visualización en el navegador están listos.' },
          beforeStep: function () { _scrollToTarget('#setup-badge-webrtc-deps'); } },
        { target: 'button[onclick*="webrtc-deps"]', position: 'bottom',
          title: { ko: 'WebRTC 의존성 설치', en: 'Install WebRTC Dependencies', ja: 'WebRTC依存関係インストール', 'zh-CN': '安装WebRTC依赖', 'zh-TW': '安裝WebRTC相依性', es: 'Instalar dependencias WebRTC' },
          content: { ko: '브라우저 시각화에 필요한 <strong>GStreamer WebRTC/ICE 패키지</strong>를 설치합니다.', en: 'Install <strong>GStreamer WebRTC/ICE packages</strong> required for browser visualization.', ja: 'ブラウザ可視化に必要な<strong>GStreamer WebRTC/ICEパッケージ</strong>をインストールします。', 'zh-CN': '安装浏览器可视化所需的 <strong>GStreamer WebRTC/ICE 包</strong>。', 'zh-TW': '安裝瀏覽器視覺化所需的 <strong>GStreamer WebRTC/ICE 套件</strong>。', es: 'Instale los <strong>paquetes GStreamer WebRTC/ICE</strong> necesarios para la visualización en el navegador.' },
          beforeStep: function () { _scrollToTarget('button[onclick*="webrtc-deps"]'); } },
        { target: '#setup-env-tbody', position: 'top',
          title: { ko: '환경 점검', en: 'Environment Check', ja: '環境チェック', 'zh-CN': '环境检查', 'zh-TW': '環境檢查', es: 'Comprobación del entorno' },
          content: { ko: '모든 설치가 끝난 뒤 <strong>6개 항목</strong>(NPU, GStreamer, 모델, 비디오, 플러그인, 런타임)의 상태를 확인합니다. 🔄 재점검 버튼으로 최신 상태를 갱신하세요.', en: 'After all installs, check status of <strong>6 items</strong> (NPU, GStreamer, models, videos, plugins, runtime). Click 🔄 to refresh.', ja: 'すべてのインストール後、<strong>6項目</strong>(NPU、GStreamer、モデル、ビデオ、プラグイン、ランタイム)の状態を確認します。🔄 再確認ボタンで最新状態を更新してください。', 'zh-CN': '全部安装完成后，检查<strong>6个项目</strong>（NPU、GStreamer、模型、视频、插件、运行时）的状态。点击🔄刷新。', 'zh-TW': '全部安裝完成後，檢查<strong>6個項目</strong>（NPU、GStreamer、模型、影片、外掛程式、執行時期）的狀態。點擊🔄重新整理。', es: 'Tras todas las instalaciones, compruebe el estado de <strong>6 elementos</strong> (NPU, GStreamer, modelos, vídeos, plugins y runtime). Haga clic en 🔄 para actualizar.' },
          beforeStep: function () { _scrollToTarget('#setup-env-tbody'); } },
      ]
    },

    { id: 'custom', icon: '🔩',
      title: { ko: '🔩 커스텀 라이브러리', en: '🔩 Custom Library', ja: '🔩 カスタムライブラリ', 'zh-CN': '🔩 自定义库', 'zh-TW': '🔩 自訂函式庫', es: '🔩 Biblioteca personalizada' },
      description: { ko: '커스텀 후처리 .so 빌드 및 관리', en: 'Build and manage custom postprocess .so files', ja: 'カスタム後処理.soのビルドと管理', 'zh-CN': '构建和管理自定义后处理.so文件', 'zh-TW': '建構和管理自訂後處理.so檔案', es: 'Compile y gestione archivos .so de postprocesado personalizados' },
      beforeStart: function () { goPage('custom'); },
      steps: [
        { target: '#custom-lib-grid', position: 'right',
          title: { ko: '기존 라이브러리', en: 'Existing Libraries', ja: '既存ライブラリ', 'zh-CN': '现有库', 'zh-TW': '現有函式庫', es: 'Bibliotecas existentes' },
          content: { ko: '<code>/usr/local/share/gstdxstream/lib/</code>에 이미 설치된 <strong>후처리 .so 파일 목록</strong>입니다. 감지, 분류, 포즈, OBB 등 다양한 후처리기가 포함됩니다.', en: 'Lists <strong>postprocess .so files</strong> already installed in <code>/usr/local/share/gstdxstream/lib/</code>. Includes detection, classification, pose, OBB processors.', ja: '<code>/usr/local/share/gstdxstream/lib/</code>に既にインストールされている<strong>後処理.soファイルリスト</strong>です。検出、分類、ポーズ、OBBなど様々なポストプロセッサが含まれます。', 'zh-CN': '列出已安装在<code>/usr/local/share/gstdxstream/lib/</code>中的<strong>后处理.so文件</strong>。包含检测、分类、姿态、OBB等各种后处理器。', 'zh-TW': '列出已安裝在<code>/usr/local/share/gstdxstream/lib/</code>中的<strong>後處理.so檔案</strong>。包含偵測、分類、姿態、OBB等各種後處理器。', es: 'Lista los <strong>archivos .so de postprocesado</strong> ya instalados en <code>/usr/local/share/gstdxstream/lib/</code>. Incluye procesadores de detección, clasificación, pose y OBB.' } },
        { target: '#custom-lib-name', position: 'left',
          title: { ko: '라이브러리 이름', en: 'Library Name', ja: 'ライブラリ名', 'zh-CN': '库名称', 'zh-TW': '函式庫名稱', es: 'Nombre de la biblioteca' },
          content: { ko: '빌드할 <strong>라이브러리 이름</strong>을 입력합니다. 예: <code>my_detector</code>. 빌드 결과물은 <code>libmy_detector.so</code>로 생성됩니다.', en: 'Enter the <strong>library name</strong> to build. E.g. <code>my_detector</code> → output will be <code>libmy_detector.so</code>.', ja: 'ビルドする<strong>ライブラリ名</strong>を入力します。例：<code>my_detector</code>。ビルド結果は<code>libmy_detector.so</code>として生成されます。', 'zh-CN': '输入要构建的<strong>库名称</strong>。例如：<code>my_detector</code>。构建输出为<code>libmy_detector.so</code>。', 'zh-TW': '輸入要建構的<strong>函式庫名稱</strong>。例如：<code>my_detector</code>。建構輸出為<code>libmy_detector.so</code>。', es: 'Introduzca el <strong>nombre de la biblioteca</strong> a compilar. Ej.: <code>my_detector</code> → la salida será <code>libmy_detector.so</code>.' } },
        { target: '#custom-lib-files', position: 'left',
          title: { ko: '파일 업로드', en: 'Upload Files', ja: 'ファイルアップロード', 'zh-CN': '上传文件', 'zh-TW': '上傳檔案', es: 'Subir archivos' },
          content: { ko: '<strong>C 소스 파일(.c)</strong>과 <strong>meson.build</strong>를 함께 선택합니다. SDK 표준 형식의 후처리 함수 시그니처를 따라야 합니다.', en: 'Select your <strong>C source file(.c)</strong> and <strong>meson.build</strong> together. Must follow SDK standard postprocess function signature.', ja: '<strong>Cソースファイル(.c)</strong>と<strong>meson.build</strong>を一緒に選択します。SDK標準形式の後処理関数シグネチャに従う必要があります。', 'zh-CN': '同时选择<strong>C源文件(.c)</strong>和<strong>meson.build</strong>。必须遵循SDK标准格式的后处理函数签名。', 'zh-TW': '同時選擇<strong>C原始碼(.c)</strong>和<strong>meson.build</strong>。必須遵循SDK標準格式的後處理函數簽名。', es: 'Seleccione juntos su <strong>archivo fuente C (.c)</strong> y <strong>meson.build</strong>. Debe seguir la firma estándar del SDK para funciones de postprocesado.' } },
        { target: 'button[onclick*="custom.upload"]', position: 'left',
          title: { ko: '업로드 버튼', en: 'Upload Button', ja: 'アップロードボタン', 'zh-CN': '上传按钮', 'zh-TW': '上傳按鈕', es: 'Botón de subida' },
          content: { ko: '파일 선택 후 <strong>업로드 버튼</strong>을 클릭하면 소스 파일이 서버로 전송되고 자동 빌드가 시작됩니다.', en: 'After selecting files, click <strong>Upload</strong> to send source files to the server and start the build automatically.', ja: 'ファイル選択後、<strong>アップロードボタン</strong>をクリックするとソースファイルがサーバーに送信され、自動ビルドが開始します。', 'zh-CN': '选择文件后，点击<strong>上传按钮</strong>将源文件发送到服务器并自动开始构建。', 'zh-TW': '選擇檔案後，點擊<strong>上傳按鈕</strong>將原始碼傳送到伺服器並自動開始建構。', es: 'Tras seleccionar los archivos, haga clic en <strong>Subir</strong> para enviar los fuentes al servidor e iniciar la compilación automáticamente.' } },
        { target: '#custom-build-log-card', position: 'top',
          title: { ko: '빌드 로그', en: 'Build Log', ja: 'ビルドログ', 'zh-CN': '构建日志', 'zh-TW': '建構日誌', es: 'Registro de compilación' },
          content: { ko: '업로드 후 <strong>빌드 버튼</strong>을 누르면 meson setup → compile → install 과정이 실시간으로 스트리밍됩니다. ✅ 완료 시 데모 실행 시 선택 가능해집니다.', en: 'After upload, click <strong>Build</strong> to stream meson setup → compile → install in real-time. On ✅ completion, the .so becomes selectable in demos.', ja: 'アップロード後、<strong>ビルドボタン</strong>を押すとmeson setup → compile → installの過程がリアルタイムでストリーミングされます。✅ 完了後、デモ実行時に選択可能になります。', 'zh-CN': '上传后，点击<strong>构建按钮</strong>实时流式传输meson setup → compile → install过程。✅完成后，可在演示中选择.so。', 'zh-TW': '上傳後，點擊<strong>建構按鈕</strong>即時串流meson setup → compile → install過程。✅完成後，可在示範中選擇.so。', es: 'Tras la subida, haga clic en <strong>Compilar</strong> para transmitir en tiempo real meson setup → compile → install. Al completarse (✅), el .so queda disponible en las demos.' },
          beforeStep: function () {
            var el = document.getElementById('custom-build-log-card');
            if (el) el.style.display = 'block';
          } },
      ]
    },

    { id: 'global', icon: '🌐',
      title: { ko: '🌐 전역 기능', en: '🌐 Global Features', ja: '🌐 グローバル機能', 'zh-CN': '🌐 全局功能', 'zh-TW': '🌐 全域功能', es: '🌐 Funciones globales' },
      description: { ko: '사이드바, 상단 바, 공유 툴바, 토스트 알림', en: 'Sidebar, top bar, shared toolbar, toast notifications', ja: 'サイドバー、トップバー、共通ツールバー、トースト通知', 'zh-CN': '侧边栏、顶部栏、共享工具栏、Toast通知', 'zh-TW': '側邊欄、頂部欄、共用工具列、Toast通知', es: 'Barra lateral, barra superior, barra compartida y notificaciones toast' },
      beforeStart: function () { goPage('dashboard'); },
      steps: [
        { target: '#sidebar', position: 'right',
          title: { ko: '사이드바', en: 'Sidebar', ja: 'サイドバー', 'zh-CN': '侧边栏', 'zh-TW': '側邊欄', es: 'Barra lateral' },
          content: { ko: '<strong>7개 페이지</strong>로 이동하는 네비게이션입니다. 상단 ☰ 버튼으로 접기/펼치기가 가능합니다.', en: 'Navigate across <strong>7 pages</strong>. Use the ☰ button in the top bar to collapse or expand.', ja: '<strong>7ページ</strong>へのナビゲーションです。上部の☰ボタンで折りたたみ/展開が可能です。', 'zh-CN': '在<strong>7个页面</strong>之间导航。使用顶部栏的☰按钮折叠/展开。', 'zh-TW': '在<strong>7個頁面</strong>之間導航。使用頂部列的☰按鈕折疊/展開。', es: 'Navegue por <strong>7 páginas</strong>. Use el botón ☰ de la barra superior para contraer o expandir.' } },
        { target: '.topbar-left button', position: 'bottom',
          title: { ko: '사이드바 토글 (☰)', en: 'Sidebar Toggle (☰)', ja: 'サイドバートグル (☰)', 'zh-CN': '侧边栏切换 (☰)', 'zh-TW': '側邊欄切換 (☰)', es: 'Alternar barra lateral (☰)' },
          content: { ko: '☰ 버튼을 클릭하면 <strong>사이드바를 접거나 펼칩니다</strong>. 화면 공간이 좁을 때 유용합니다.', en: 'Click ☰ to <strong>collapse or expand the sidebar</strong>. Useful when screen space is limited.', ja: '☰をクリックすると<strong>サイドバーを折りたたみ/展開</strong>します。画面スペースが狭い時に便利です。', 'zh-CN': '点击☰可<strong>折叠或展开侧边栏</strong>。在屏幕空间有限时非常有用。', 'zh-TW': '點擊☰可<strong>折疊或展開側邊欄</strong>。在螢幕空間有限時非常有用。', es: 'Haga clic en ☰ para <strong>contraer o expandir la barra lateral</strong>. Útil cuando el espacio en pantalla es limitado.' } },
        { target: '.nav-item[data-page="dashboard"]', position: 'right',
          title: { ko: '네비게이션 항목', en: 'Nav Items', ja: 'ナビゲーション項目', 'zh-CN': '导航项目', 'zh-TW': '導航項目', es: 'Elementos de navegación' },
          content: { ko: '각 항목을 클릭하면 해당 <strong>페이지로 전환</strong>됩니다. 활성 페이지는 하이라이트 표시됩니다.', en: 'Click each item to <strong>switch to that page</strong>. Active page is highlighted.', ja: '各項目をクリックすると該当<strong>ページに切り替え</strong>ます。アクティブページはハイライト表示されます。', 'zh-CN': '点击每个项目可<strong>切换到对应页面</strong>。当前页面以高亮显示。', 'zh-TW': '點擊每個項目可<strong>切換至對應頁面</strong>。目前頁面以高亮顯示。', es: 'Haga clic en cada elemento para <strong>cambiar a esa página</strong>. La página activa se resalta.' } },
        { target: '.topbar', position: 'bottom',
          title: { ko: '상단 바', en: 'Top Bar', ja: 'トップバー', 'zh-CN': '顶部栏', 'zh-TW': '頂部欄', es: 'Barra superior' },
          content: { ko: '현재 <strong>페이지 제목</strong>과 <strong>파이프라인 실행 상태 배지</strong>가 표시됩니다.', en: 'Shows the current <strong>page title</strong> and <strong>pipeline status badge</strong>.', ja: '現在の<strong>ページタイトル</strong>と<strong>パイプライン実行状態バッジ</strong>が表示されます。', 'zh-CN': '显示当前<strong>页面标题</strong>和<strong>管道运行状态徽章</strong>。', 'zh-TW': '顯示當前<strong>頁面標題</strong>和<strong>管線執行狀態徽章</strong>。', es: 'Muestra el <strong>título de la página</strong> actual y la <strong>insignia de estado del pipeline</strong>.' } },
        { target: '#pipeline-status', position: 'bottom',
          title: { ko: '파이프라인 상태', en: 'Pipeline Status', ja: 'パイプライン状態', 'zh-CN': '管道状态', 'zh-TW': '管線狀態', es: 'Estado del pipeline' },
          content: { ko: '🟡 <strong>대기 중</strong> / 🟢 <strong>실행 중</strong> 상태를 표시합니다. 파이프라인 실행/중지 시 자동 업데이트됩니다.', en: '🟡 <strong>Idle</strong> / 🟢 <strong>Running</strong> status. Auto-updates when pipeline starts/stops.', ja: '🟡 <strong>アイドル</strong> / 🟢 <strong>実行中</strong> 状態を表示します。パイプライン開始/停止時に自動更新されます。', 'zh-CN': '🟡 <strong>空闲</strong> / 🟢 <strong>运行中</strong> 状态。管道启动/停止时自动更新。', 'zh-TW': '🟡 <strong>閒置</strong> / 🟢 <strong>執行中</strong> 狀態。管線啟動/停止時自動更新。', es: 'Estado 🟡 <strong>Inactivo</strong> / 🟢 <strong>En ejecución</strong>. Se actualiza automáticamente al iniciar/detener el pipeline.' } },
        { target: '#dxToolbar', position: 'bottom',
          title: { ko: '공유 툴바', en: 'Shared Toolbar', ja: '共通ツールバー', 'zh-CN': '共享工具栏', 'zh-TW': '共用工具列', es: 'Barra de herramientas compartida' },
          content: { ko: '상단 우측의 <strong>🌏 언어</strong>, <strong>🎓 튜토리얼</strong> 버튼이 모든 페이지에서 동일하게 동작합니다. 언어 메뉴는 튜토리얼 단계마다 자동으로 닫힙니다.', en: 'The <strong>🌏 language</strong> and <strong>🎓 tutorial</strong> buttons in the top-right work the same on every page. The language menu closes automatically during tutorial steps.', ja: '右上の<strong>🌏言語</strong>、<strong>🎓チュートリアル</strong>ボタンは全ページで同じように動作します。言語メニューはチュートリアル中に自動的に閉じます。', 'zh-CN': '右上角的<strong>🌏语言</strong>和<strong>🎓教程</strong>按钮在所有页面中行为一致。教程步骤中语言菜单会自动关闭。', 'zh-TW': '右上角的<strong>🌏語言</strong>和<strong>🎓教學</strong>按鈕在所有頁面中行為一致。教學步驟中語言選單會自動關閉。', es: 'Los botones <strong>🌏 idioma</strong> y <strong>🎓 tutorial</strong> arriba a la derecha funcionan igual en todas las páginas. El menú de idioma se cierra automáticamente durante el tutorial.' },
          beforeStep: function () {
            var el = document.getElementById('dxToolbar') || document.getElementById('langToggle');
            if (el) el.scrollIntoView({ block: 'nearest', inline: 'nearest' });
          } },
        { target: '#dxt-mock-stream-toast', position: 'top',
          title: { ko: '토스트 알림', en: 'Toast Notifications', ja: 'トースト通知', 'zh-CN': 'Toast通知', 'zh-TW': 'Toast通知', es: 'Notificaciones toast' },
          content: { ko: '<strong>info, success, error, warning</strong> 4종류 토스트 알림이 표시됩니다. 4초 후 자동으로 사라집니다.', en: '<strong>info, success, error, warning</strong> toast notifications. Auto-dismiss after 4 seconds.', ja: '<strong>info、success、error、warning</strong>の4種類のトースト通知が表示されます。4秒後に自動的に消えます。', 'zh-CN': '显示<strong>info、success、error、warning</strong>4种Toast通知。4秒后自动消失。', 'zh-TW': '顯示<strong>info、success、error、warning</strong>4種Toast通知。4秒後自動消失。', es: 'Notificaciones toast de <strong>info, success, error y warning</strong>. Se cierran automáticamente a los 4 segundos.' },
          beforeStep: function () { _mockStreamToast(); },
          afterStep: function () { _dismissStreamToast(); } },
      ]
    },

  ];

  _orderGlobalFirst(sections);

  window.DXTutorial.create({
    appId: 'stream',
    sections: sections,
    toolbarSelector: '#dxToolbar',
    skipButtons: true,
    getLang: function () { return localStorage.getItem('dx-lang') || 'en'; },
    onNav: function (p) { goPage(p); },
    onComplete: function (sectionId) {
      var engine = window._dxTutorial;
      if (!engine) return;
      var sec = engine.sections.find(function (s) { return s.id === sectionId; });
      if (sec && window.DXStream && typeof DXStream.toast === 'function') {
        DXStream.toast('✅ "' + engine._t(sec.title) + '" ' + engine._tl('tutorial complete!'), 'success');
      }
    },
    patchNav: function () {}
  });
})();
