(function(){
'use strict';

var S = window.DXStream;
if (!S) return;

function _T5(en, ko, ja, zhCN, zhTW) {
  var lang = (window.DXI18n && DXI18n.lang) || (S.S && S.S.lang) || document.documentElement.lang || 'en';
  if (lang === 'ko') return ko || en;
  if (lang === 'ja') return ja || en;
  if (lang === 'zh-CN') return zhCN || en;
  if (lang === 'zh-TW') return zhTW || en;
  return en;
}

function buildRefCategories() {
  return [
    { id:'getting-started', icon:'🚀', title:_T5('Getting Started','시작하기','はじめに','入门指南','入門指南'), desc:_T5('Setup, dashboard, and first demo flow','설정, 대시보드, 첫 데모 실행 흐름','セットアップ、ダッシュボード、初回デモの流れ','设置、仪表盘和首次演示流程','設定、儀表板與首次示範流程') },
    { id:'demo-streaming', icon:'▶️', title:_T5('Demo & Streaming','데모 & 스트리밍','デモ & ストリーミング','演示与流媒体','示範與串流'), desc:_T5('Preset demos, MJPEG/WebRTC','프리셋 데모, MJPEG/WebRTC','プリセットデモ、MJPEG/WebRTC','预设演示、MJPEG/WebRTC','預設示範、MJPEG/WebRTC') },
    { id:'pipeline', icon:'🔧', title:_T5('Pipeline','파이프라인','パイプライン','管道','管線'), desc:_T5('Pipeline builder, validation, presets, and export','파이프라인 빌더, 검증, 프리셋, 내보내기','パイプラインビルダー、検証、プリセット、エクスポート','管道构建器、验证、预设和导出','管線建置器、驗證、預設與匯出') },
    { id:'models-elements', icon:'📦', title:_T5('Models & Elements','모델 & 요소','モデル & エレメント','模型与元素','模型與元素'), desc:_T5('Model catalog, GStreamer elements, and custom libraries','모델 카탈로그, GStreamer 요소, 커스텀 라이브러리','モデルカタログ、GStreamerエレメント、カスタムライブラリ','模型目录、GStreamer 元素和自定义库','模型目錄、GStreamer 元素與自訂函式庫') },
    { id:'system', icon:'⚡', title:_T5('System','시스템','システム','系统','系統'), desc:_T5('Monitoring, APIs, keyboard shortcuts, and troubleshooting','모니터링, API, 단축키, 문제 해결','モニタリング、API、ショートカット、トラブルシューティング','监控、API、快捷键和故障排除','監控、API、快捷鍵與疑難排解') }
  ];
}

function buildRefTopics() { return [
  {
    id:'quick-start', cat:'getting-started', icon:'🏁',
    name: _T5('Quick Start','빠른 시작','クイックスタート','快速开始','快速開始'),
    desc: _T5('Learn the basic workflow of DX Stream','DX Stream의 기본 사용 흐름을 알아봅니다','DX Streamの基本的なワークフローを学びます','了解DX Stream的基本工作流程','了解DX Stream的基本工作流程'),
    tabs: { overview: _T5(
      '<p>Recommended steps when using DX Stream for the first time:</p><ol><li>Check prerequisites on the <b>Setup</b> page (NPU device, GStreamer, Models)</li><li>Confirm system status on the <b>Dashboard</b></li><li>Run your first AI inference demo in the <b>Demo Launcher</b></li><li>Build custom pipelines in the <b>Pipeline Builder</b></li><li>Browse available AI models in the <b>Model Catalog</b></li></ol><div class="ref-box tip">💡 Complete all 6 steps on the Setup page before running demos for the best experience.</div>',
      '<p>DX Stream을 처음 사용할 때 권장하는 순서입니다:</p><ol><li><b>설정 페이지</b>에서 사전 요구사항 확인 (NPU 장치, GStreamer, 모델)</li><li><b>대시보드</b>에서 시스템 상태 확인</li><li><b>데모 실행기</b>에서 첫 번째 AI 추론 데모 실행</li><li><b>파이프라인 빌더</b>에서 커스텀 파이프라인 구성</li><li><b>모델 카탈로그</b>에서 사용 가능한 AI 모델 확인</li></ol><div class="ref-box tip">💡 설정 페이지의 6단계를 모두 완료한 후 데모를 실행하면 가장 좋습니다.</div>',
      '<p>DX Streamを初めて使用する際の推奨手順：</p><ol><li><b>セットアップ</b>ページで前提条件を確認（NPUデバイス、GStreamer、モデル）</li><li><b>ダッシュボード</b>でシステム状態を確認</li><li><b>デモランチャー</b>で最初のAI推論デモを実行</li><li><b>パイプラインビルダー</b>でカスタムパイプラインを構築</li><li><b>モデルカタログ</b>で利用可能なAIモデルを確認</li></ol><div class="ref-box tip">💡 デモを実行する前にセットアップページの6つのステップをすべて完了することをお勧めします。</div>',
      '<p>首次使用DX Stream时的推荐步骤：</p><ol><li>在<b>设置</b>页面检查前提条件（NPU设备、GStreamer、模型）</li><li>在<b>仪表盘</b>确认系统状态</li><li>在<b>演示启动器</b>中运行首个AI推理演示</li><li>在<b>管道构建器</b>中构建自定义管道</li><li>在<b>模型目录</b>中浏览可用的AI模型</li></ol><div class="ref-box tip">💡 在运行演示之前完成设置页面的所有6个步骤可获得最佳体验。</div>',
      '<p>首次使用DX Stream時的建議步驟：</p><ol><li>在<b>設定</b>頁面檢查前提條件（NPU裝置、GStreamer、模型）</li><li>在<b>儀表板</b>確認系統狀態</li><li>在<b>示範啟動器</b>中執行首個AI推論示範</li><li>在<b>管線建置器</b>中建置自訂管線</li><li>在<b>模型目錄</b>中瀏覽可用的AI模型</li></ol><div class="ref-box tip">💡 在執行示範之前完成設定頁面的所有6個步驟可獲得最佳體驗。</div>'
    ) }
  },
  {
    id:'setup-install', cat:'getting-started', icon:'⚙️',
    name: _T5('Setup & Install','설치 및 설정','セットアップとインストール','安装与设置','安裝與設定'),
    desc: _T5('7-step installation and environment check','6단계 설치 과정과 환경 점검','7ステップのインストールと環境チェック','7步安装和环境检查','7步安裝與環境檢查'),
    tabs: { overview: _T5(
      '<p>Complete the 6 steps in order on the Setup page:</p><table><thead><tr><th>Step</th><th>Description</th><th>Required</th></tr></thead><tbody><tr><td>1</td><td><b>Build Tools & Libraries</b> — cmake, meson, GStreamer, OpenCV</td><td>✅</td></tr><tr><td>2</td><td><b>Runtime SDK</b> — Install DEEPX SDK</td><td>✅</td></tr><tr><td>3</td><td><b>Driver</b> — DX NPU kernel driver</td><td>✅</td></tr><tr><td>4</td><td><b>Build Plugins</b> — Compile GStreamer DX elements</td><td>✅</td></tr><tr><td>5</td><td><b>Download AI Models</b> — Choose from 16 models</td><td>✅</td></tr><tr><td>6</td><td><b>WebRTC Support</b> — Low-latency streaming (gstreamer1.0-nice)</td><td>Optional</td></tr></tbody></table><p>Each step has an install button with real-time progress polling. Environment Check and Deep Diagnostics show NPU, GStreamer, and model status at a glance.</p>',
      '<p>설정 페이지에서 6단계를 순서대로 진행합니다:</p><table><thead><tr><th>단계</th><th>내용</th><th>필수</th></tr></thead><tbody><tr><td>1</td><td><b>빌드 도구 & 라이브러리</b> — cmake, meson, GStreamer, OpenCV</td><td>✅</td></tr><tr><td>2</td><td><b>런타임 SDK</b> — DEEPX SDK 설치</td><td>✅</td></tr><tr><td>3</td><td><b>드라이버</b> — DX NPU 커널 드라이버</td><td>✅</td></tr><tr><td>4</td><td><b>플러그인 빌드</b> — GStreamer DX 요소 컴파일</td><td>✅</td></tr><tr><td>5</td><td><b>AI 모델 다운로드</b> — 16개 모델 중 선택</td><td>✅</td></tr><tr><td>6</td><td><b>WebRTC 지원</b> — 저지연 스트리밍 (gstreamer1.0-nice)</td><td>선택</td></tr></tbody></table><p>각 단계는 설치 버튼이 있으며, 진행률을 실시간 폴링합니다.</p>',
      '<p>セットアップページで6つのステップを順番に進めます：</p><table><thead><tr><th>ステップ</th><th>内容</th><th>必須</th></tr></thead><tbody><tr><td>1</td><td><b>ビルドツール & ライブラリ</b> — cmake, meson, GStreamer, OpenCV</td><td>✅</td></tr><tr><td>2</td><td><b>ランタイムSDK</b> — DEEPX SDKのインストール</td><td>✅</td></tr><tr><td>3</td><td><b>ドライバー</b> — DX NPUカーネルドライバー</td><td>✅</td></tr><tr><td>4</td><td><b>プラグインビルド</b> — GStreamer DXエレメントのコンパイル</td><td>✅</td></tr><tr><td>5</td><td><b>AIモデルダウンロード</b> — 16モデルから選択</td><td>✅</td></tr><tr><td>6</td><td><b>WebRTCサポート</b> — 低遅延ストリーミング</td><td>任意</td></tr></tbody></table>',
      '<p>在设置页面按顺序完成6个步骤：</p><table><thead><tr><th>步骤</th><th>说明</th><th>必需</th></tr></thead><tbody><tr><td>1</td><td><b>构建工具和库</b> — cmake、meson、GStreamer、OpenCV</td><td>✅</td></tr><tr><td>2</td><td><b>运行时SDK</b> — 安装DEEPX SDK</td><td>✅</td></tr><tr><td>3</td><td><b>驱动程序</b> — DX NPU内核驱动</td><td>✅</td></tr><tr><td>4</td><td><b>构建插件</b> — 编译GStreamer DX元素</td><td>✅</td></tr><tr><td>5</td><td><b>下载AI模型</b> — 从16个模型中选择</td><td>✅</td></tr><tr><td>6</td><td><b>WebRTC支持</b> — 低延迟流媒体</td><td>可选</td></tr></tbody></table>',
      '<p>在設定頁面按順序完成6個步驟：</p><table><thead><tr><th>步驟</th><th>說明</th><th>必需</th></tr></thead><tbody><tr><td>1</td><td><b>建置工具與函式庫</b> — cmake、meson、GStreamer、OpenCV</td><td>✅</td></tr><tr><td>2</td><td><b>執行時SDK</b> — 安裝DEEPX SDK</td><td>✅</td></tr><tr><td>3</td><td><b>驅動程式</b> — DX NPU核心驅動</td><td>✅</td></tr><tr><td>4</td><td><b>建置外掛</b> — 編譯GStreamer DX元素</td><td>✅</td></tr><tr><td>5</td><td><b>下載AI模型</b> — 從16個模型中選擇</td><td>✅</td></tr><tr><td>6</td><td><b>WebRTC支援</b> — 低延遲串流</td><td>可選</td></tr></tbody></table>'
    ) }
  },
  {
    id:'dashboard-overview', cat:'getting-started', icon:'📊',
    name: _T5('Dashboard Overview','대시보드 개요','ダッシュボード概要','仪表盘概述','儀表板概述'),
    desc: _T5('System status, metrics, quick launch','시스템 상태, 성능 지표, 빠른 실행','システム状態、メトリクス、クイック起動','系统状态、指标、快速启动','系統狀態、指標、快速啟動'),
    tabs: { overview: _T5(
      '<p>The Dashboard provides a system overview at a glance:</p><ul><li><b>5 stat tiles</b> — NPU Device, GStreamer, Models (installed/total), Sample Videos, Plugin Build</li><li><b>Pipeline Status</b> — Active pipeline info (model, FPS when running)</li><li><b>Quick Launch</b> — 3 presets: Object Detection, Pose Estimation, Segmentation</li><li><b>Performance Metrics table</b> — FPS, Inference Latency, E2E Latency, NPU Utilization (current/avg/max)</li><li><b>Sparkline charts</b> — Real-time FPS and NPU utilization graphs (Chart.js)</li></ul>',
      '<p>대시보드는 시스템 상태를 한눈에 보여줍니다:</p><ul><li><b>5개 상태 타일</b> — NPU 장치, GStreamer, 모델, 샘플 비디오, 플러그인 빌드</li><li><b>파이프라인 상태</b> — 활성 파이프라인 정보</li><li><b>빠른 실행</b> — 객체 감지, 포즈 추정, 의미론적 분할 3개 프리셋</li><li><b>성능 지표 테이블</b> — FPS, 추론 지연, E2E 지연, NPU 사용률</li><li><b>스파크라인 차트</b> — FPS와 NPU 사용률의 실시간 그래프</li></ul>',
      '<p>ダッシュボードはシステム状態を一目で表示します：</p><ul><li><b>5つのステータスタイル</b> — NPUデバイス、GStreamer、モデル、サンプルビデオ、プラグインビルド</li><li><b>パイプライン状態</b> — アクティブなパイプライン情報</li><li><b>クイック起動</b> — 物体検出、姿勢推定、セグメンテーション</li><li><b>パフォーマンス指標テーブル</b> — FPS、推論レイテンシ、NPU使用率</li><li><b>スパークラインチャート</b> — リアルタイムグラフ</li></ul>',
      '<p>仪表盘提供系统状态的一览视图：</p><ul><li><b>5个状态磁贴</b> — NPU设备、GStreamer、模型、示例视频、插件构建</li><li><b>管道状态</b> — 活动管道信息</li><li><b>快速启动</b> — 3个预设</li><li><b>性能指标表</b> — FPS、推理延迟、NPU利用率</li><li><b>迷你图表</b> — 实时图表</li></ul>',
      '<p>儀表板提供系統狀態的一覽視圖：</p><ul><li><b>5個狀態磁磚</b> — NPU裝置、GStreamer、模型、範例影片、外掛建置</li><li><b>管線狀態</b> — 活動管線資訊</li><li><b>快速啟動</b> — 3個預設</li><li><b>效能指標表</b> — FPS、推論延遲、NPU使用率</li><li><b>迷你圖表</b> — 即時圖表</li></ul>'
    ) }
  },
  {
    id:'demo-launcher', cat:'demo-streaming', icon:'🎬',
    name: _T5('Demo Launcher','데모 실행기','デモランチャー','演示启动器','示範啟動器'),
    desc: _T5('Run 11 preset demos and view results','11개 프리셋 데모 실행 및 결과 확인','11個のプリセットデモを実行し結果を確認','运行11个预设演示并查看结果','執行11個預設示範並查看結果'),
    tabs: { overview: _T5(
      '<p>Run 11 preset AI inference demos:</p><ul><li>Category filter bar for quick type selection</li><li>Click demo card → auto-build pipeline → start video streaming</li><li>Choose MJPEG (default) or WebRTC output mode</li><li>Real-time FPS and latency overlay on video</li><li>Stop button to terminate pipeline</li><li>Fullscreen mode supported</li></ul><div class="ref-box tip">💡 The required model must be installed before running a demo. Download from Model Catalog.</div>',
      '<p>11개의 프리셋 AI 추론 데모를 실행할 수 있습니다:</p><ul><li>카테고리 필터 바로 빠르게 원하는 유형 찾기</li><li>데모 카드 클릭 → 파이프라인 자동 빌드 → 비디오 스트리밍 시작</li><li>MJPEG(기본) 또는 WebRTC 출력 모드 선택</li><li>실시간 FPS, 지연 시간 오버레이 표시</li><li>중지 버튼으로 파이프라인 종료</li><li>전체화면 모드 지원</li></ul><div class="ref-box tip">💡 데모를 실행하려면 해당 모델이 먼저 설치되어 있어야 합니다.</div>',
      '<p>11個のプリセットAI推論デモを実行できます：</p><ul><li>カテゴリフィルターバーで素早くタイプを選択</li><li>デモカードをクリック → パイプライン自動構築 → ストリーミング開始</li><li>MJPEG（デフォルト）またはWebRTC出力モード選択</li><li>リアルタイムFPSとレイテンシのオーバーレイ表示</li><li>停止ボタンでパイプライン終了</li></ul><div class="ref-box tip">💡 デモを実行するには対応するモデルが事前にインストールされている必要があります。</div>',
      '<p>可运行11个预设AI推理演示：</p><ul><li>类别过滤栏快速选择类型</li><li>点击卡片 → 自动构建管道 → 开始视频流</li><li>选择MJPEG或WebRTC输出模式</li><li>实时FPS和延迟叠加显示</li><li>停止按钮终止管道</li></ul><div class="ref-box tip">💡 运行演示前需先安装相应模型。</div>',
      '<p>可執行11個預設AI推論示範：</p><ul><li>類別篩選列快速選擇類型</li><li>點擊卡片 → 自動建置管線 → 開始視訊串流</li><li>選擇MJPEG或WebRTC輸出模式</li><li>即時FPS和延遲疊加顯示</li><li>停止按鈕終止管線</li></ul><div class="ref-box tip">💡 執行示範前需先安裝相應模型。</div>'
    ) }
  },
  {
    id:'streaming-modes', cat:'demo-streaming', icon:'📡',
    name: _T5('MJPEG / WebRTC Streaming','MJPEG / WebRTC 스트리밍','MJPEG / WebRTCストリーミング','MJPEG / WebRTC流媒体','MJPEG / WebRTC串流'),
    desc: _T5('Compare two video output modes','두 가지 비디오 출력 모드 비교','2つのビデオ出力モードの比較','两种视频输出模式比较','兩種視訊輸出模式比較'),
    tabs: { overview: _T5(
      '<table><thead><tr><th>Feature</th><th>MJPEG</th><th>WebRTC</th></tr></thead><tbody><tr><td>Default</td><td>✅ Default</td><td>Manual switch</td></tr><tr><td>Transport</td><td><code>multipart/x-mixed-replace</code></td><td>RTCPeerConnection (SDP/ICE)</td></tr><tr><td>Latency</td><td>High (200–500ms)</td><td>Low (&lt;100ms)</td></tr><tr><td>Compatibility</td><td>All browsers</td><td>Requires <code>gstreamer1.0-nice</code></td></tr></tbody></table><div class="ref-box tip">💡 Use MJPEG for reliability, WebRTC for low latency.</div>',
      '<table><thead><tr><th>항목</th><th>MJPEG</th><th>WebRTC</th></tr></thead><tbody><tr><td>기본 모드</td><td>✅ 기본값</td><td>수동 전환</td></tr><tr><td>전송 방식</td><td><code>multipart/x-mixed-replace</code></td><td>RTCPeerConnection</td></tr><tr><td>지연 시간</td><td>높음 (200–500ms)</td><td>낮음 (&lt;100ms)</td></tr><tr><td>호환성</td><td>모든 브라우저</td><td><code>gstreamer1.0-nice</code> 필요</td></tr></tbody></table><div class="ref-box tip">💡 안정성이 중요하면 MJPEG, 지연 시간이 중요하면 WebRTC를 사용하세요.</div>',
      '<table><thead><tr><th>項目</th><th>MJPEG</th><th>WebRTC</th></tr></thead><tbody><tr><td>デフォルト</td><td>✅</td><td>手動切替</td></tr><tr><td>転送方式</td><td><code>multipart/x-mixed-replace</code></td><td>RTCPeerConnection</td></tr><tr><td>レイテンシ</td><td>高い</td><td>低い</td></tr><tr><td>互換性</td><td>全ブラウザ</td><td><code>gstreamer1.0-nice</code>が必要</td></tr></tbody></table><div class="ref-box tip">💡 安定性ならMJPEG、低遅延ならWebRTC。</div>',
      '<table><thead><tr><th>项目</th><th>MJPEG</th><th>WebRTC</th></tr></thead><tbody><tr><td>默认</td><td>✅</td><td>手动切换</td></tr><tr><td>传输</td><td><code>multipart/x-mixed-replace</code></td><td>RTCPeerConnection</td></tr><tr><td>延迟</td><td>高</td><td>低</td></tr><tr><td>兼容性</td><td>所有浏览器</td><td>需要<code>gstreamer1.0-nice</code></td></tr></tbody></table><div class="ref-box tip">💡 注重稳定性用MJPEG，注重低延迟用WebRTC。</div>',
      '<table><thead><tr><th>項目</th><th>MJPEG</th><th>WebRTC</th></tr></thead><tbody><tr><td>預設</td><td>✅</td><td>手動切換</td></tr><tr><td>傳輸</td><td><code>multipart/x-mixed-replace</code></td><td>RTCPeerConnection</td></tr><tr><td>延遲</td><td>高</td><td>低</td></tr><tr><td>相容性</td><td>所有瀏覽器</td><td>需要<code>gstreamer1.0-nice</code></td></tr></tbody></table><div class="ref-box tip">💡 注重穩定性用MJPEG，注重低延遲用WebRTC。</div>'
    ) }
  },
  {
    id:'demo-catalog', cat:'demo-streaming', icon:'📋',
    name: _T5('Demo Catalog','데모 카탈로그','デモカタログ','演示目录','示範目錄'),
    desc: _T5('Detailed description of 11 demo scenarios','11개 데모 시나리오 상세 설명','11個のデモシナリオの詳細説明','11个演示场景详细说明','11個示範場景詳細說明'),
    tabs: { overview: _T5(
      '<table><thead><tr><th>#</th><th>Demo</th><th>Model</th><th>Category</th></tr></thead><tbody><tr><td>0</td><td>Object Detection</td><td>YOLOv26n</td><td>object_detection</td></tr><tr><td>1</td><td>Object Detection (PPU)</td><td>YoloV5S_PPU</td><td>object_detection</td></tr><tr><td>2</td><td>Face Detection</td><td>YOLOv5s_Face</td><td>face_detection</td></tr><tr><td>3</td><td>Face Detection PPU</td><td>SCRFD500M_PPU</td><td>face_detection</td></tr><tr><td>4</td><td>Pose Estimation</td><td>YOLOv26n_Pose</td><td>pose_estimation</td></tr><tr><td>5</td><td>Pose Estimation PPU</td><td>YOLOV5Pose_PPU</td><td>pose_estimation</td></tr><tr><td>6</td><td>Semantic Segmentation</td><td>YOLOv26n_Seg</td><td>segmentation</td></tr><tr><td>7</td><td>Multi-Object Tracking</td><td>YoloV5S_PPU + DxTracker</td><td>tracking</td></tr><tr><td>8</td><td>Multi-Stream</td><td>YoloV5S_PPU</td><td>multi_stream</td></tr><tr><td>9</td><td>Multi-Stream RTSP</td><td>YoloV5S_PPU</td><td>multi_stream</td></tr><tr><td>10</td><td>Secondary Inference</td><td>Detection + Classification + Face</td><td>secondary</td></tr></tbody></table>',
      '<table><thead><tr><th>#</th><th>데모</th><th>모델</th><th>카테고리</th></tr></thead><tbody><tr><td>0</td><td>객체 감지</td><td>YOLOv26n</td><td>object_detection</td></tr><tr><td>1</td><td>객체 감지 (PPU)</td><td>YoloV5S_PPU</td><td>object_detection</td></tr><tr><td>2</td><td>얼굴 감지</td><td>YOLOv5s_Face</td><td>face_detection</td></tr><tr><td>3</td><td>얼굴 감지 PPU</td><td>SCRFD500M_PPU</td><td>face_detection</td></tr><tr><td>4</td><td>포즈 추정</td><td>YOLOv26n_Pose</td><td>pose_estimation</td></tr><tr><td>5</td><td>포즈 추정 PPU</td><td>YOLOV5Pose_PPU</td><td>pose_estimation</td></tr><tr><td>6</td><td>의미론적 분할</td><td>YOLOv26n_Seg</td><td>segmentation</td></tr><tr><td>7</td><td>다중 객체 추적</td><td>YoloV5S_PPU + DxTracker</td><td>tracking</td></tr><tr><td>8</td><td>멀티스트림</td><td>YoloV5S_PPU</td><td>multi_stream</td></tr><tr><td>9</td><td>멀티스트림 RTSP</td><td>YoloV5S_PPU</td><td>multi_stream</td></tr><tr><td>10</td><td>2차 추론</td><td>Detection + Classification + Face</td><td>secondary</td></tr></tbody></table>',
      '<table><thead><tr><th>#</th><th>デモ</th><th>モデル</th><th>カテゴリ</th></tr></thead><tbody><tr><td>0</td><td>物体検出</td><td>YOLOv26n</td><td>object_detection</td></tr><tr><td>1</td><td>物体検出 PPU</td><td>YoloV5S_PPU</td><td>object_detection</td></tr><tr><td>2</td><td>顔検出</td><td>YOLOv5s_Face</td><td>face_detection</td></tr><tr><td>3</td><td>顔検出 PPU</td><td>SCRFD500M_PPU</td><td>face_detection</td></tr><tr><td>4</td><td>姿勢推定</td><td>YOLOv26n_Pose</td><td>pose_estimation</td></tr><tr><td>5</td><td>姿勢推定 PPU</td><td>YOLOV5Pose_PPU</td><td>pose_estimation</td></tr><tr><td>6</td><td>セマンティックセグメンテーション</td><td>YOLOv26n_Seg</td><td>segmentation</td></tr><tr><td>7</td><td>複数物体追跡</td><td>YoloV5S_PPU + DxTracker</td><td>tracking</td></tr><tr><td>8</td><td>マルチストリーム</td><td>YoloV5S_PPU</td><td>multi_stream</td></tr><tr><td>9</td><td>マルチストリーム RTSP</td><td>YoloV5S_PPU</td><td>multi_stream</td></tr><tr><td>10</td><td>二次推論</td><td>Detection + Classification + Face</td><td>secondary</td></tr></tbody></table>',
      '<table><thead><tr><th>#</th><th>演示</th><th>模型</th><th>类别</th></tr></thead><tbody><tr><td>0</td><td>目标检测</td><td>YOLOv26n</td><td>object_detection</td></tr><tr><td>1</td><td>目标检测 PPU</td><td>YoloV5S_PPU</td><td>object_detection</td></tr><tr><td>2</td><td>人脸检测</td><td>YOLOv5s_Face</td><td>face_detection</td></tr><tr><td>3</td><td>人脸检测 PPU</td><td>SCRFD500M_PPU</td><td>face_detection</td></tr><tr><td>4</td><td>姿态估计</td><td>YOLOv26n_Pose</td><td>pose_estimation</td></tr><tr><td>5</td><td>姿态估计 PPU</td><td>YOLOV5Pose_PPU</td><td>pose_estimation</td></tr><tr><td>6</td><td>语义分割</td><td>YOLOv26n_Seg</td><td>segmentation</td></tr><tr><td>7</td><td>多目标跟踪</td><td>YoloV5S_PPU + DxTracker</td><td>tracking</td></tr><tr><td>8</td><td>多路流</td><td>YoloV5S_PPU</td><td>multi_stream</td></tr><tr><td>9</td><td>多路流 RTSP</td><td>YoloV5S_PPU</td><td>multi_stream</td></tr><tr><td>10</td><td>二次推理</td><td>Detection + Classification + Face</td><td>secondary</td></tr></tbody></table>',
      '<table><thead><tr><th>#</th><th>示範</th><th>模型</th><th>類別</th></tr></thead><tbody><tr><td>0</td><td>物件偵測</td><td>YOLOv26n</td><td>object_detection</td></tr><tr><td>1</td><td>物件偵測 PPU</td><td>YoloV5S_PPU</td><td>object_detection</td></tr><tr><td>2</td><td>人臉偵測</td><td>YOLOv5s_Face</td><td>face_detection</td></tr><tr><td>3</td><td>人臉偵測 PPU</td><td>SCRFD500M_PPU</td><td>face_detection</td></tr><tr><td>4</td><td>姿態估計</td><td>YOLOv26n_Pose</td><td>pose_estimation</td></tr><tr><td>5</td><td>姿態估計 PPU</td><td>YOLOV5Pose_PPU</td><td>pose_estimation</td></tr><tr><td>6</td><td>語義分割</td><td>YOLOv26n_Seg</td><td>segmentation</td></tr><tr><td>7</td><td>多物件追蹤</td><td>YoloV5S_PPU + DxTracker</td><td>tracking</td></tr><tr><td>8</td><td>多路串流</td><td>YoloV5S_PPU</td><td>multi_stream</td></tr><tr><td>9</td><td>多路串流 RTSP</td><td>YoloV5S_PPU</td><td>multi_stream</td></tr><tr><td>10</td><td>二次推論</td><td>Detection + Classification + Face</td><td>secondary</td></tr></tbody></table>'
    ) }
  },
  {
    id:'visual-editor', cat:'pipeline', icon:'🎨',
    name: _T5('Visual Editor','비주얼 에디터','ビジュアルエディタ','可视化编辑器','視覺化編輯器'),
    desc: _T5('Canvas-based pipeline node editor','캔버스 기반 파이프라인 노드 에디터','キャンバスベースのパイプラインノードエディタ','基于画布的管道节点编辑器','基於畫布的管線節點編輯器'),
    tabs: { overview: _T5(
      '<p>A visual pipeline editor based on HTML5 Canvas 2D:</p><ul><li><b>Left sidebar</b> — Element palette with 9 categories</li><li><b>Drag & Drop</b> — Place elements on canvas to create nodes with input/output pads</li><li><b>Connect</b> — Drag from output pad to input pad to link elements</li><li><b>Right-click menu</b> — Delete, Duplicate, Disconnect</li><li><b>Property panel</b> — Edit selected element properties on the right</li><li><b>Minimap</b> — Canvas overview in bottom-right corner</li><li><b>Mouse wheel</b> — Zoom in/out; middle-click drag — Pan</li></ul>',
      '<p>HTML5 Canvas 2D 기반의 비주얼 파이프라인 에디터입니다:</p><ul><li><b>왼쪽 사이드바</b> — 9개 카테고리의 요소 팔레트</li><li><b>드래그 & 드롭</b> — 요소를 캔버스에 배치하면 입출력 패드가 있는 노드 생성</li><li><b>연결</b> — 출력 패드에서 입력 패드로 드래그</li><li><b>우클릭 메뉴</b> — 삭제, 복제, 연결 해제</li><li><b>속성 패널</b> — 오른쪽에서 선택된 요소의 속성 편집</li><li><b>미니맵</b> — 우측 하단 코너에 캔버스 개요</li><li><b>마우스 휠</b> — 줌 인/아웃</li></ul>',
      '<p>HTML5 Canvas 2Dベースのビジュアルパイプラインエディタ：</p><ul><li><b>左サイドバー</b> — 9カテゴリのエレメントパレット</li><li><b>ドラッグ＆ドロップ</b> — エレメントをキャンバスに配置</li><li><b>接続</b> — 出力パッドから入力パッドへドラッグ</li><li><b>右クリックメニュー</b> — 削除、複製、切断</li><li><b>プロパティパネル</b> — 右側で編集</li><li><b>ミニマップ</b> — 右下にキャンバス概要</li></ul>',
      '<p>基于HTML5 Canvas 2D的可视化管道编辑器：</p><ul><li><b>左侧边栏</b> — 9个类别的元素面板</li><li><b>拖放</b> — 将元素放到画布上</li><li><b>连接</b> — 从输出焊盘拖到输入焊盘</li><li><b>右键菜单</b> — 删除、复制、断开</li><li><b>属性面板</b> — 右侧编辑</li><li><b>小地图</b> — 右下角概览</li></ul>',
      '<p>基於HTML5 Canvas 2D的視覺化管線編輯器：</p><ul><li><b>左側邊欄</b> — 9個類別的元素面板</li><li><b>拖放</b> — 將元素放到畫布上</li><li><b>連接</b> — 從輸出接墊拖到輸入接墊</li><li><b>右鍵選單</b> — 刪除、複製、中斷</li><li><b>屬性面板</b> — 右側編輯</li><li><b>小地圖</b> — 右下角概覽</li></ul>'
    ) }
  },
  {
    id:'connection-rules', cat:'pipeline', icon:'🔗',
    name: _T5('Connection Rules','연결 규칙','接続ルール','连接规则','連接規則'),
    desc: _T5('Pad compatibility, validation, auto-insert','패드 호환성, 검증, 자동 삽입','パッド互換性、検証、自動挿入','焊盘兼容性、验证、自动插入','接墊相容性、驗證、自動插入'),
    tabs: { overview: _T5(
      '<p>Connection validation rules in Pipeline Builder:</p><ul><li><b>ID Matching</b> — DxPreprocess and DxInfer must have matching <code>preprocess-id</code></li><li><b>Auto-insert</b> — When connecting incompatible pads, suggests inserting <code>videoconvert</code> or <code>queue</code></li><li><b>Multi-input</b> — DxGather, compositor require 2+ inputs</li><li><b>Multi-output</b> — tee requires 2+ outputs</li><li><b>Terminal</b> — DxMsgBroker has no output pad (must be last)</li><li><b>Validation</b> — Warns about missing source/sink, unconnected pads, ID mismatches</li></ul>',
      '<p>파이프라인 빌더의 연결 검증 규칙:</p><ul><li><b>ID 매칭</b> — DxPreprocess와 DxInfer는 <code>preprocess-id</code>가 일치해야 함</li><li><b>자동 삽입</b> — 호환되지 않는 패드 연결 시 <code>videoconvert</code> 또는 <code>queue</code> 삽입 제안</li><li><b>다중 입력</b> — DxGather, compositor는 2개 이상의 입력 필요</li><li><b>다중 출력</b> — tee는 2개 이상의 출력 필요</li><li><b>종단 요소</b> — DxMsgBroker는 출력 패드 없음</li><li><b>검증</b> — 소스/싱크 누락, 미연결 패드, ID 불일치 경고</li></ul>',
      '<p>パイプラインビルダーの接続検証ルール：</p><ul><li><b>IDマッチング</b> — DxPreprocessとDxInferは<code>preprocess-id</code>が一致する必要あり</li><li><b>自動挿入</b> — 互換性のないパッド接続時に自動挿入を提案</li><li><b>複数入力</b> — DxGather、compositorは2つ以上の入力が必要</li><li><b>複数出力</b> — teeは2つ以上の出力が必要</li><li><b>終端エレメント</b> — DxMsgBrokerは出力パッドなし</li><li><b>検証</b> — ソース/シンク不足、未接続パッド、IDミスマッチを警告</li></ul>',
      '<p>管道构建器的连接验证规则：</p><ul><li><b>ID匹配</b> — DxPreprocess和DxInfer的<code>preprocess-id</code>必须匹配</li><li><b>自动插入</b> — 不兼容时建议插入<code>videoconvert</code>或<code>queue</code></li><li><b>多输入</b> — DxGather、compositor需要2+输入</li><li><b>多输出</b> — tee需要2+输出</li><li><b>终端元素</b> — DxMsgBroker没有输出焊盘</li><li><b>验证</b> — 警告缺少源/汇、未连接焊盘</li></ul>',
      '<p>管線建置器的連接驗證規則：</p><ul><li><b>ID匹配</b> — DxPreprocess和DxInfer的<code>preprocess-id</code>必須匹配</li><li><b>自動插入</b> — 不相容時建議插入<code>videoconvert</code>或<code>queue</code></li><li><b>多輸入</b> — DxGather、compositor需要2+輸入</li><li><b>多輸出</b> — tee需要2+輸出</li><li><b>終端元素</b> — DxMsgBroker沒有輸出接墊</li><li><b>驗證</b> — 警告缺少源/匯、未連接接墊</li></ul>'
    ) }
  },
  {
    id:'preset-export', cat:'pipeline', icon:'💾',
    name: _T5('Preset & Export','프리셋 & 내보내기','プリセット & エクスポート','预设与导出','預設與匯出'),
    desc: _T5('Save, load, GStreamer command preview','파이프라인 저장, 불러오기, GStreamer 명령 미리보기','パイプラインの保存・読込・コマンドプレビュー','管道保存、加载、命令预览','管線儲存、載入、命令預覽'),
    tabs: { overview: _T5(
      '<p>Pipeline Builder save and export features:</p><ul><li><b>5 built-in presets</b> — Standard, Config, PPU, Tracking, Multi-stream</li><li><b>Load preset</b> — auto-builds pipeline on canvas</li><li><b>Save as JSON</b> — exports full pipeline state</li><li><b>Import JSON</b> — restore previously saved pipelines</li><li><b>GStreamer Command Preview</b> — shows equivalent <code>gst-launch-1.0</code> command</li><li><b>Run button</b> — sends pipeline to server for execution</li><li><b>Undo/Redo</b> — <code>Ctrl+Z</code> / <code>Ctrl+Shift+Z</code></li></ul>',
      '<p>파이프라인 빌더의 저장 및 내보내기 기능:</p><ul><li><b>5개 내장 프리셋</b> — Standard, Config, PPU, Tracking, Multi-stream</li><li><b>프리셋 로드</b> → 캔버스에 자동으로 파이프라인 구성</li><li><b>JSON 저장</b> — 전체 파이프라인 상태 내보내기</li><li><b>JSON 불러오기</b> — 이전에 저장한 파이프라인 복원</li><li><b>GStreamer 명령 미리보기</b> — <code>gst-launch-1.0</code> 명령 표시</li><li><b>실행 버튼</b> — 파이프라인을 서버로 전송하여 실행</li><li><b>Undo/Redo</b> — <code>Ctrl+Z</code> / <code>Ctrl+Shift+Z</code></li></ul>',
      '<p>パイプラインビルダーの保存・エクスポート機能：</p><ul><li><b>5つの内蔵プリセット</b></li><li><b>プリセットロード</b> → キャンバスに自動構築</li><li><b>JSON保存</b> — パイプライン全状態をエクスポート</li><li><b>JSONインポート</b> — 復元</li><li><b>GStreamerコマンドプレビュー</b></li><li><b>実行ボタン</b></li><li><b>Undo/Redo</b></li></ul>',
      '<p>管道构建器的保存和导出功能：</p><ul><li><b>5个内置预设</b></li><li><b>加载预设</b> → 自动构建</li><li><b>保存为JSON</b></li><li><b>导入JSON</b></li><li><b>GStreamer命令预览</b></li><li><b>运行按钮</b></li><li><b>撤销/重做</b></li></ul>',
      '<p>管線建置器的儲存和匯出功能：</p><ul><li><b>5個內建預設</b></li><li><b>載入預設</b> → 自動建置</li><li><b>儲存為JSON</b></li><li><b>匯入JSON</b></li><li><b>GStreamer命令預覽</b></li><li><b>執行按鈕</b></li><li><b>復原/重做</b></li></ul>'
    ) }
  },
  {
    id:'model-catalog', cat:'models-elements', icon:'🧠',
    name: _T5('Model Catalog','모델 카탈로그','モデルカタログ','模型目录','模型目錄'),
    desc: _T5('Search, download, and inspect 16 AI models','16개 AI 모델 검색, 다운로드, 메타데이터 확인','16個のAIモデル検索・ダウンロード・メタデータ確認','搜索、下载和查看16个AI模型','搜尋、下載和查看16個AI模型'),
    tabs: { overview: _T5(
      '<p>Manage 16 DEEPX <code>.dxnn</code> AI models:</p><ul><li><b>5 categories</b> — Object Detection(8), Face Detection(3), Pose Estimation(3), Segmentation(1), Classification(1)</li><li><b>Model cards</b> — name, bilingual description, filename, category badge, install status</li><li><b>Download</b> — click button → poll progress → auto-refresh on completion</li><li><b>Detail modal</b> — General tab + Metadata tab</li><li><b>Search + category filter</b> — work independently</li></ul>',
      '<p>16개의 DEEPX <code>.dxnn</code> AI 모델을 관리합니다:</p><ul><li><b>5개 카테고리</b> — 객체 감지(8), 얼굴 감지(3), 포즈 추정(3), 분할(1), 분류(1)</li><li><b>모델 카드</b> — 이름, 이중 언어 설명, 파일명, 카테고리 배지, 설치 상태</li><li><b>다운로드</b> — 클릭 → 진행률 폴링 → 완료 시 자동 새로고침</li><li><b>상세 모달</b> — 일반 탭 + 메타데이터 탭</li><li><b>검색 + 카테고리 필터</b> — 독립적으로 동작</li></ul>',
      '<p>16個のDEEPX <code>.dxnn</code> AIモデルを管理：</p><ul><li><b>5カテゴリ</b></li><li><b>モデルカード</b> — 名前、説明、ファイル名、カテゴリバッジ、状態</li><li><b>ダウンロード</b> — 進捗ポーリング → 完了時に自動更新</li><li><b>詳細モーダル</b> — 一般タブ + メタデータタブ</li><li><b>検索 + フィルター</b></li></ul>',
      '<p>管理16个DEEPX <code>.dxnn</code> AI模型：</p><ul><li><b>5个类别</b></li><li><b>模型卡片</b></li><li><b>下载</b> — 轮询进度 → 完成自动刷新</li><li><b>详细模态框</b></li><li><b>搜索 + 类别过滤</b></li></ul>',
      '<p>管理16個DEEPX <code>.dxnn</code> AI模型：</p><ul><li><b>5個類別</b></li><li><b>模型卡片</b></li><li><b>下載</b> — 輪詢進度 → 完成自動重新整理</li><li><b>詳細模態框</b></li><li><b>搜尋 + 類別篩選</b></li></ul>'
    ) }
  },
  {
    id:'element-reference', cat:'models-elements', icon:'🧩',
    name: _T5('Element Reference','요소 레퍼런스','エレメントリファレンス','元素参考','元素參考'),
    desc: _T5('Properties, pads, and examples for 26 elements','26개 GStreamer 요소 속성, 패드, 예제','26個のエレメントの属性・パッド・例','26个元素的属性、焊盘和示例','26個元素的屬性、接墊與範例'),
    tabs: { overview: _T5(
      '<p>13 DEEPX custom + 13 standard GStreamer elements:</p><ul><li><b>10 categories</b> — Preprocess, Inference, Postprocess, Visualization, Tracking, Messaging, Source, Output, Utility</li><li><b>Element cards</b> — name, category badge, bilingual description, property count</li><li><b>Detail panel</b> — long description, key features, pipeline hint, example config</li><li><b>Properties table</b> — name, type, default, description</li></ul><div class="ref-box tip">💡 Key rules: DxPreprocess/DxInfer must match <code>preprocess-id</code>; DxInfer/DxPostprocess must match <code>inference-id</code></div>',
      '<p>13개 DEEPX 커스텀 + 13개 표준 GStreamer 요소:</p><ul><li><b>10개 카테고리</b></li><li><b>요소 카드</b> — 이름, 카테고리 배지, 설명, 속성 수</li><li><b>상세 패널</b> — 긴 설명, 주요 기능, 파이프라인 힌트, 예제</li><li><b>속성 테이블</b> — 이름, 타입, 기본값, 설명</li></ul><div class="ref-box tip">💡 DxPreprocess/DxInfer는 <code>preprocess-id</code> 일치 필수</div>',
      '<p>13個のDEEPXカスタム + 13個の標準GStreamerエレメント：</p><ul><li><b>10カテゴリ</b></li><li><b>エレメントカード</b></li><li><b>詳細パネル</b></li><li><b>プロパティテーブル</b></li></ul><div class="ref-box tip">💡 DxPreprocess/DxInferは<code>preprocess-id</code>一致必須</div>',
      '<p>13个DEEPX自定义 + 13个标准GStreamer元素：</p><ul><li><b>10个类别</b></li><li><b>元素卡片</b></li><li><b>详细面板</b></li><li><b>属性表</b></li></ul><div class="ref-box tip">💡 DxPreprocess/DxInfer的<code>preprocess-id</code>必须匹配</div>',
      '<p>13個DEEPX自訂 + 13個標準GStreamer元素：</p><ul><li><b>10個類別</b></li><li><b>元素卡片</b></li><li><b>詳細面板</b></li><li><b>屬性表</b></li></ul><div class="ref-box tip">💡 DxPreprocess/DxInfer的<code>preprocess-id</code>必須匹配</div>'
    ) }
  },
  {
    id:'custom-library', cat:'models-elements', icon:'🔩',
    name: _T5('Custom Library','커스텀 라이브러리','カスタムライブラリ','自定义库','自訂函式庫'),
    desc: _T5('Upload C source, meson build, .so install','C 소스 업로드, meson 빌드, .so 설치','Cソースアップロード、mesonビルド、.soインストール','C源码上传、meson构建、.so安装','C原始碼上傳、meson建置、.so安裝'),
    tabs: { overview: _T5(
      '<p>Manage C libraries for custom post-processing logic:</p><ul><li><b>Upload</b> — C source files + <code>meson.build</code></li><li><b>Build process</b> — meson setup → meson compile → sudo meson install</li><li><b>Install path</b> — <code>/usr/local/share/gstdxstream/lib/</code></li><li><b>Pipeline Builder integration</b> — built <code>.so</code> auto-appears in DxPostprocess dropdown</li><li><b>Real-time build log</b> — 1-second polling interval</li></ul><div class="ref-box tip">💡 The <code>.so</code> must export a C function matching <code>function-name</code> (default: <code>PostProcess</code>).</div>',
      '<p>커스텀 후처리 로직을 위한 C 라이브러리 관리:</p><ul><li><b>업로드</b> — C 소스 파일 + <code>meson.build</code></li><li><b>빌드 프로세스</b> — meson setup → meson compile → sudo meson install</li><li><b>설치 경로</b> — <code>/usr/local/share/gstdxstream/lib/</code></li><li><b>파이프라인 빌더 연동</b> — 빌드된 <code>.so</code>가 드롭다운에 자동 표시</li><li><b>실시간 빌드 로그</b> — 1초 간격 폴링</li></ul><div class="ref-box tip">💡 <code>.so</code> 파일은 <code>function-name</code>과 일치하는 C 함수를 export해야 합니다.</div>',
      '<p>カスタム後処理ロジック用のCライブラリ管理：</p><ul><li><b>アップロード</b> — Cソースファイル + <code>meson.build</code></li><li><b>ビルドプロセス</b> — meson setup → compile → install</li><li><b>インストールパス</b> — <code>/usr/local/share/gstdxstream/lib/</code></li><li><b>パイプラインビルダー連携</b> — <code>.so</code>が自動表示</li></ul><div class="ref-box tip">💡 <code>.so</code>は<code>function-name</code>と一致するC関数をエクスポートする必要があります。</div>',
      '<p>管理自定义后处理逻辑的C库：</p><ul><li><b>上传</b> — C源文件 + <code>meson.build</code></li><li><b>构建过程</b> — meson setup → compile → install</li><li><b>安装路径</b> — <code>/usr/local/share/gstdxstream/lib/</code></li><li><b>管道构建器集成</b> — <code>.so</code>自动出现</li></ul><div class="ref-box tip">💡 <code>.so</code>必须导出与<code>function-name</code>匹配的C函数。</div>',
      '<p>管理自訂後處理邏輯的C函式庫：</p><ul><li><b>上傳</b> — C原始碼檔案 + <code>meson.build</code></li><li><b>建置過程</b> — meson setup → compile → install</li><li><b>安裝路徑</b> — <code>/usr/local/share/gstdxstream/lib/</code></li><li><b>管線建置器整合</b> — <code>.so</code>自動出現</li></ul><div class="ref-box tip">💡 <code>.so</code>必須匯出與<code>function-name</code>匹配的C函式。</div>'
    ) }
  },
  {
    id:'keyboard-shortcuts', cat:'system', icon:'⌨️',
    name: _T5('Keyboard Shortcuts','키보드 단축키','キーボードショートカット','键盘快捷键','鍵盤快捷鍵'),
    desc: _T5('Pipeline Builder and general shortcuts','파이프라인 빌더 및 일반 단축키','パイプラインビルダーと一般ショートカット','管道构建器和通用快捷键','管線建置器與一般快捷鍵'),
    tabs: { overview: _T5(
      '<table><thead><tr><th>Shortcut</th><th>Action</th><th>Scope</th></tr></thead><tbody><tr><td><code>Ctrl+Z</code></td><td>Undo</td><td>Pipeline Builder</td></tr><tr><td><code>Ctrl+Shift+Z</code></td><td>Redo</td><td>Pipeline Builder</td></tr><tr><td><code>Delete</code> / <code>Backspace</code></td><td>Delete selected node</td><td>Pipeline Builder</td></tr><tr><td><code>Escape</code></td><td>Deselect / Close panel</td><td>Global</td></tr><tr><td><code>Ctrl+K</code></td><td>Open chat widget</td><td>Global</td></tr><tr><td>Mouse wheel</td><td>Canvas zoom</td><td>Pipeline Builder</td></tr><tr><td>Middle-click drag</td><td>Canvas pan</td><td>Pipeline Builder</td></tr></tbody></table>',
      '<table><thead><tr><th>단축키</th><th>기능</th><th>범위</th></tr></thead><tbody><tr><td><code>Ctrl+Z</code></td><td>실행 취소</td><td>파이프라인 빌더</td></tr><tr><td><code>Ctrl+Shift+Z</code></td><td>다시 실행</td><td>파이프라인 빌더</td></tr><tr><td><code>Delete</code> / <code>Backspace</code></td><td>선택한 노드 삭제</td><td>파이프라인 빌더</td></tr><tr><td><code>Escape</code></td><td>선택 해제 / 패널 닫기</td><td>전체</td></tr><tr><td><code>Ctrl+K</code></td><td>채팅 위젯 열기</td><td>전체</td></tr><tr><td>마우스 휠</td><td>캔버스 줌</td><td>파이프라인 빌더</td></tr><tr><td>중간 클릭 드래그</td><td>캔버스 패닝</td><td>파이프라인 빌더</td></tr></tbody></table>',
      '<table><thead><tr><th>ショートカット</th><th>機能</th><th>範囲</th></tr></thead><tbody><tr><td><code>Ctrl+Z</code></td><td>元に戻す</td><td>パイプラインビルダー</td></tr><tr><td><code>Ctrl+Shift+Z</code></td><td>やり直し</td><td>パイプラインビルダー</td></tr><tr><td><code>Delete</code></td><td>選択ノード削除</td><td>パイプラインビルダー</td></tr><tr><td><code>Escape</code></td><td>選択解除/パネル閉じ</td><td>全体</td></tr><tr><td><code>Ctrl+K</code></td><td>チャットウィジェット</td><td>全体</td></tr></tbody></table>',
      '<table><thead><tr><th>快捷键</th><th>功能</th><th>范围</th></tr></thead><tbody><tr><td><code>Ctrl+Z</code></td><td>撤销</td><td>管道构建器</td></tr><tr><td><code>Ctrl+Shift+Z</code></td><td>重做</td><td>管道构建器</td></tr><tr><td><code>Delete</code></td><td>删除选中节点</td><td>管道构建器</td></tr><tr><td><code>Escape</code></td><td>取消选择/关闭面板</td><td>全局</td></tr><tr><td><code>Ctrl+K</code></td><td>打开聊天</td><td>全局</td></tr></tbody></table>',
      '<table><thead><tr><th>快捷鍵</th><th>功能</th><th>範圍</th></tr></thead><tbody><tr><td><code>Ctrl+Z</code></td><td>復原</td><td>管線建置器</td></tr><tr><td><code>Ctrl+Shift+Z</code></td><td>重做</td><td>管線建置器</td></tr><tr><td><code>Delete</code></td><td>刪除選取節點</td><td>管線建置器</td></tr><tr><td><code>Escape</code></td><td>取消選取/關閉面板</td><td>全域</td></tr><tr><td><code>Ctrl+K</code></td><td>開啟聊天</td><td>全域</td></tr></tbody></table>'
    ) }
  },
  {
    id:'api-endpoints', cat:'system', icon:'🌐',
    name: _T5('API Endpoints','API 엔드포인트','APIエンドポイント','API端点','API端點'),
    desc: _T5('Complete REST API list and usage','REST API 전체 목록 및 사용법','REST API全リストと使い方','REST API完整列表和用法','REST API完整列表與用法'),
    tabs: { overview: _T5(
      '<table><thead><tr><th>Group</th><th>Method</th><th>Path</th></tr></thead><tbody><tr><td>Status</td><td>GET</td><td><code>/api/status</code></td></tr><tr><td>Pipeline</td><td>POST</td><td><code>/api/pipeline/run</code></td></tr><tr><td>Pipeline</td><td>POST</td><td><code>/api/pipeline/stop</code></td></tr><tr><td>Pipeline</td><td>GET</td><td><code>/api/pipeline/status</code></td></tr><tr><td>Pipeline</td><td>POST</td><td><code>/api/pipeline/validate</code></td></tr><tr><td>Stream</td><td>GET</td><td><code>/api/stream/mjpeg</code></td></tr><tr><td>Stream</td><td>POST</td><td><code>/api/stream/webrtc/offer</code></td></tr><tr><td>Demo</td><td>GET</td><td><code>/api/demos</code></td></tr><tr><td>Demo</td><td>POST</td><td><code>/api/demo/run/:id</code></td></tr><tr><td>Models</td><td>GET</td><td><code>/api/models</code></td></tr><tr><td>Elements</td><td>GET</td><td><code>/api/elements</code></td></tr><tr><td>Custom</td><td>GET</td><td><code>/api/custom-library</code></td></tr><tr><td>Custom</td><td>POST</td><td><code>/api/custom-library/upload</code></td></tr></tbody></table>',
      '<table><thead><tr><th>분류</th><th>메서드</th><th>경로</th></tr></thead><tbody><tr><td>상태</td><td>GET</td><td><code>/api/status</code></td></tr><tr><td>파이프라인</td><td>POST</td><td><code>/api/pipeline/run</code></td></tr><tr><td>파이프라인</td><td>POST</td><td><code>/api/pipeline/stop</code></td></tr><tr><td>파이프라인</td><td>GET</td><td><code>/api/pipeline/status</code></td></tr><tr><td>파이프라인</td><td>POST</td><td><code>/api/pipeline/validate</code></td></tr><tr><td>스트림</td><td>GET</td><td><code>/api/stream/mjpeg</code></td></tr><tr><td>스트림</td><td>POST</td><td><code>/api/stream/webrtc/offer</code></td></tr><tr><td>데모</td><td>GET</td><td><code>/api/demos</code></td></tr><tr><td>데모</td><td>POST</td><td><code>/api/demo/run/:id</code></td></tr><tr><td>모델</td><td>GET</td><td><code>/api/models</code></td></tr><tr><td>요소</td><td>GET</td><td><code>/api/elements</code></td></tr><tr><td>커스텀</td><td>GET</td><td><code>/api/custom-library</code></td></tr><tr><td>커스텀</td><td>POST</td><td><code>/api/custom-library/upload</code></td></tr></tbody></table>',
      '<table><thead><tr><th>分類</th><th>メソッド</th><th>パス</th></tr></thead><tbody><tr><td>ステータス</td><td>GET</td><td><code>/api/status</code></td></tr><tr><td>パイプライン</td><td>POST</td><td><code>/api/pipeline/run</code></td></tr><tr><td>パイプライン</td><td>POST</td><td><code>/api/pipeline/stop</code></td></tr><tr><td>ストリーム</td><td>GET</td><td><code>/api/stream/mjpeg</code></td></tr><tr><td>デモ</td><td>GET</td><td><code>/api/demos</code></td></tr><tr><td>モデル</td><td>GET</td><td><code>/api/models</code></td></tr><tr><td>エレメント</td><td>GET</td><td><code>/api/elements</code></td></tr></tbody></table>',
      '<table><thead><tr><th>分类</th><th>方法</th><th>路径</th></tr></thead><tbody><tr><td>状态</td><td>GET</td><td><code>/api/status</code></td></tr><tr><td>管道</td><td>POST</td><td><code>/api/pipeline/run</code></td></tr><tr><td>管道</td><td>POST</td><td><code>/api/pipeline/stop</code></td></tr><tr><td>流</td><td>GET</td><td><code>/api/stream/mjpeg</code></td></tr><tr><td>演示</td><td>GET</td><td><code>/api/demos</code></td></tr><tr><td>模型</td><td>GET</td><td><code>/api/models</code></td></tr><tr><td>元素</td><td>GET</td><td><code>/api/elements</code></td></tr></tbody></table>',
      '<table><thead><tr><th>分類</th><th>方法</th><th>路徑</th></tr></thead><tbody><tr><td>狀態</td><td>GET</td><td><code>/api/status</code></td></tr><tr><td>管線</td><td>POST</td><td><code>/api/pipeline/run</code></td></tr><tr><td>管線</td><td>POST</td><td><code>/api/pipeline/stop</code></td></tr><tr><td>串流</td><td>GET</td><td><code>/api/stream/mjpeg</code></td></tr><tr><td>示範</td><td>GET</td><td><code>/api/demos</code></td></tr><tr><td>模型</td><td>GET</td><td><code>/api/models</code></td></tr><tr><td>元素</td><td>GET</td><td><code>/api/elements</code></td></tr></tbody></table>'
    ) }
  },
  {
    id:'theme-language', cat:'system', icon:'🎨',
    name: _T5('Theme & Language','테마 & 언어','テーマ & 言語','主题与语言','主題與語言'),
    desc: _T5('Dark/light theme, 5 language switching','다크/라이트 테마, 5개 국어 전환','ダーク/ライトテーマ、5言語切替','深色/浅色主题、5种语言','深色/淺色主題、5種語言'),
    tabs: { overview: _T5(
      '<ul><li><b>Theme</b> — Toggle via toolbar icon, persisted in <code>localStorage</code></li><li><b>Languages (5)</b> — Korean(ko), English(en), Japanese(ja), Simplified Chinese(zh-CN), Traditional Chinese(zh-TW)</li><li><b>Switch</b> — Toolbar language button dropdown</li><li><b>Storage</b> — <code>localStorage(\'dx-lang\')</code></li><li><b>Scope</b> — All page UI text updates instantly</li></ul>',
      '<ul><li><b>테마</b> — 툴바 아이콘으로 전환, <code>localStorage</code>에 저장</li><li><b>언어 (5개)</b> — 한국어(ko), English(en), 日本語(ja), 简体中文(zh-CN), 繁體中文(zh-TW)</li><li><b>전환 방법</b> — 툴바 언어 버튼 → 드롭다운</li><li><b>저장</b> — <code>localStorage(\'dx-lang\')</code></li><li><b>적용 범위</b> — 모든 페이지의 UI 텍스트가 즉시 업데이트</li></ul>',
      '<ul><li><b>テーマ</b> — ツールバーアイコンで切替、<code>localStorage</code>に保存</li><li><b>言語（5つ）</b> — 韓国語、英語、日本語、簡体中国語、繁体中国語</li><li><b>切替方法</b> — ツールバー言語ボタン → ドロップダウン</li><li><b>保存</b> — <code>localStorage(\'dx-lang\')</code></li><li><b>適用範囲</b> — 全ページのUIテキストが即座に更新</li></ul>',
      '<ul><li><b>主题</b> — 工具栏图标切换，<code>localStorage</code>保存</li><li><b>语言（5种）</b> — 韩语、英语、日语、简体中文、繁体中文</li><li><b>切换</b> — 工具栏语言下拉</li><li><b>存储</b> — <code>localStorage(\'dx-lang\')</code></li><li><b>范围</b> — 即时更新所有UI文本</li></ul>',
      '<ul><li><b>主題</b> — 工具列圖示切換，<code>localStorage</code>儲存</li><li><b>語言（5種）</b> — 韓語、英語、日語、簡體中文、繁體中文</li><li><b>切換</b> — 工具列語言下拉</li><li><b>儲存</b> — <code>localStorage(\'dx-lang\')</code></li><li><b>範圍</b> — 即時更新所有UI文字</li></ul>'
    ) }
  }
]; }

var _currentFilter = 'all';
var _expandedId = null;
var _bound = false;

function renderRefContent(filter, search) {
  var container = document.getElementById('ref-content');
  if (!container) return;
  container.innerHTML = '';
  _expandedId = null;

  var categories = buildRefCategories();
  var filtered = buildRefTopics().filter(function(t) {
    if (filter && filter !== 'all' && t.cat !== filter) return false;
    if (search) {
      var tmp = document.createElement('div');
      tmp.innerHTML = t.name + ' ' + t.desc;
      var text = tmp.textContent.toLowerCase();
      if (text.indexOf(search.toLowerCase()) < 0) return false;
    }
    return true;
  });

  var cats = {};
  filtered.forEach(function(t) {
    if (!cats[t.cat]) cats[t.cat] = [];
    cats[t.cat].push(t);
  });

  categories.forEach(function(cat) {
    if (!cats[cat.id]) return;
    var header = document.createElement('div');
    header.className = 'ref-cat';
    header.id = 'ref-cat-' + cat.id;
    header.setAttribute('data-ref-cat', cat.id);

    var title = document.createElement('div');
    title.className = 'ref-cat-title';
    title.textContent = cat.title;
    header.appendChild(title);

    var desc = document.createElement('div');
    desc.className = 'ref-cat-desc';
    desc.textContent = cat.desc;
    header.appendChild(desc);
    container.appendChild(header);

    var grid = document.createElement('div');
    grid.className = 'ref-card-row';
    grid.setAttribute('data-ref-cat', cat.id);
    cats[cat.id].forEach(function(topic) {
      var card = document.createElement('button');
      card.className = 'ref-topic-card';
      card.setAttribute('data-ref-id', topic.id);
      card.setAttribute('data-ref-cat', topic.cat);
      card.innerHTML = '<span class="ref-section-icon">' + topic.icon + '</span>'
        + '<span class="ref-section-info">'
        + '<span class="ref-section-name">' + topic.name + '</span>'
        + '<span class="ref-section-desc">' + topic.desc + '</span>'
        + '</span>';
      grid.appendChild(card);
    });
    container.appendChild(grid);
  });
}

function buildDetailHtml(topic) {
  var tabKeys = Object.keys(topic.tabs);
  var tabLabels = {
    overview: '📋 ' + _T5('Overview','개요','概要','概述','概述'),
    params: '⚙️ ' + _T5('Parameters','파라미터','パラメータ','参数','參數'),
    workflow: '🔄 ' + _T5('Workflow','워크플로우','ワークフロー','工作流','工作流程'),
    tips: '💡 ' + _T5('Tips','팁','ヒント','提示','提示')
  };
  var html = '<div class="ref-detail-hd"><div><div class="ref-detail-kicker">'
    + _T5('Reference','레퍼런스','リファレンス','参考','參考') + '</div><h2>'
    + topic.icon + ' ' + topic.name + '</h2><p>' + topic.desc + '</p></div></div>';
  html += '<div class="ref-tabs">';
  tabKeys.forEach(function(key, i) {
    html += '<div class="ref-tab' + (i === 0 ? ' active' : '') + '" data-tab="' + key + '" tabindex="0">'
      + (tabLabels[key] || key) + '</div>';
  });
  html += '</div>';
  tabKeys.forEach(function(key, i) {
    html += '<div class="ref-tab-content' + (i === 0 ? ' active' : '') + '" data-tab="' + key + '">'
      + topic.tabs[key] + '</div>';
  });
  return html;
}

function showDetail(topicId, cardEl) {
  var wasExpanded = _expandedId;
  closeDetail();
  if (wasExpanded === topicId) return;

  var topic = buildRefTopics().find(function(t) { return t.id === topicId; });
  if (!topic) return;
  _expandedId = topicId;
  cardEl.classList.add('active');

  var gridEl = cardEl.parentNode;
  var cardRect = cardEl.getBoundingClientRect();
  var gridRect = gridEl.getBoundingClientRect();
  var arrowLeft = cardRect.left - gridRect.left + cardRect.width / 2 - 8;

  var expand = document.createElement('div');
  expand.className = 'ref-expand';
  expand.id = 'ref-expand';

  var arrow = document.createElement('div');
  arrow.className = 'ref-expand-arrow';
  arrow.style.left = arrowLeft + 'px';
  expand.appendChild(arrow);

  var closeBtn = document.createElement('button');
  closeBtn.className = 'ref-expand-close';
  closeBtn.textContent = '✕';
  expand.appendChild(closeBtn);

  var inner = document.createElement('div');
  inner.className = 'ref-expand-inner';
  inner.id = 'ref-detail';
  inner.innerHTML = buildDetailHtml(topic);
  expand.appendChild(inner);

  gridEl.parentNode.insertBefore(expand, gridEl.nextSibling);
  expand.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function closeDetail() {
  var el = document.querySelector('.ref-expand');
  if (el) el.remove();
  document.querySelectorAll('.ref-topic-card.active').forEach(function(c) { c.classList.remove('active'); });
  _expandedId = null;
}

function activateRefTab(tab) {
  var expandInner = tab.closest('.ref-expand-inner');
  if (!expandInner) return;
  expandInner.querySelectorAll('.ref-tab').forEach(function(t) { t.classList.remove('active'); });
  expandInner.querySelectorAll('.ref-tab-content').forEach(function(tc) { tc.classList.remove('active'); });
  tab.classList.add('active');
  var tc = expandInner.querySelector('.ref-tab-content[data-tab="' + tab.getAttribute('data-tab') + '"]');
  if (tc) tc.classList.add('active');
}

function renderFilterChips() {
  var bar = document.getElementById('ref-filter-bar');
  if (!bar) return;
  bar.innerHTML = '';
  var categories = buildRefCategories();

  var allChip = document.createElement('button');
  allChip.className = 'chip active';
  allChip.setAttribute('data-ref-cat-filter', 'all');
  allChip.textContent = _T5('All','전체','すべて','全部','全部');
  bar.appendChild(allChip);

  categories.forEach(function(cat) {
    var chip = document.createElement('button');
    chip.className = 'chip';
    chip.setAttribute('data-ref-cat-filter', cat.id);
    chip.textContent = cat.title;
    bar.appendChild(chip);
  });
}

S.referenceInit = function() {
  renderFilterChips();
  renderRefContent('all', '');

  var searchEl = document.getElementById('ref-search');
  if (_bound) return;
  _bound = true;

  var bar = document.getElementById('ref-filter-bar');
  if (bar) {
    bar.addEventListener('click', function(e) {
      var chip = e.target.closest('[data-ref-cat-filter]');
      if (!chip) return;
      _currentFilter = chip.getAttribute('data-ref-cat-filter');
      bar.querySelectorAll('.chip').forEach(function(c) { c.classList.remove('active'); });
      chip.classList.add('active');
      var search = (document.getElementById('ref-search') || {}).value || '';
      renderRefContent(_currentFilter, search);
    });
  }

  var content = document.getElementById('ref-content');
  if (content) {
    content.addEventListener('click', function(e) {
      var closeBtn = e.target.closest('.ref-expand-close');
      if (closeBtn) { closeDetail(); return; }

      var tab = e.target.closest('.ref-tab');
      if (tab) {
        activateRefTab(tab);
        return;
      }

      var card = e.target.closest('.ref-topic-card');
      if (card) {
        showDetail(card.getAttribute('data-ref-id'), card);
      }
    });

    content.addEventListener('keydown', function(e) {
      var tab = e.target.closest('.ref-tab');
      if (!tab) return;
      if (e.key !== 'Enter' && e.key !== ' ') return;
      e.preventDefault();
      activateRefTab(tab);
    });
  }

  if (searchEl) {
    searchEl.addEventListener('input', function() {
      renderRefContent(_currentFilter, this.value);
    });
  }

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && _expandedId) closeDetail();
  });
};

})();
if (typeof registerStreamLangRefresher === 'function') {
  registerStreamLangRefresher(function() {
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
    if (typeof DXStream !== 'undefined' && DXStream.S && DXStream.S.currentPage && typeof DXStream.nav === 'function') {
      DXStream.nav(DXStream.S.currentPage);
    }
  });
}
