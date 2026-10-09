(function(){
'use strict';

var S = window.DXStream;
if (!S) return;

function _T5(en, ko, ja, zhCN, zhTW, es) {
  var lang = (window.DXI18n && DXI18n.lang) || (S.S && S.S.lang) || document.documentElement.lang || 'en';
  if (lang === 'ko') return ko || en;
  if (lang === 'ja') return ja || en;
  if (lang === 'zh-CN') return zhCN || en;
  if (lang === 'zh-TW') return zhTW || en;
  if (lang === 'es') return es || en;
  return en;
}

/* 여섯 언어를 한 자리에 — 예전에는 _T5 (스페인어 없음) 였고 화면과 다른 사실 (7단계, 데모 11개, MJPEG 기본, 프리셋 5개,
   모델 16개, 요소 26개, 없는 단축키 · API) 이 많았다. 코드와 대조했다 (release audit S-9, 2026-10-02). */
function refL(o) {
  if (o == null) return '';
  if (typeof o !== 'object') return String(o);
  var lang = (window.DXI18n && DXI18n.lang) || (S.S && S.S.lang) || document.documentElement.lang || 'en';
  return o[lang] || o.en || '';
}
function _li(items) { return items.map(function (i) { return '<li>' + refL(i) + '</li>'; }).join(''); }
function _ul(items) { return '<ul>' + _li(items) + '</ul>'; }
function _ol(items) { return '<ol>' + _li(items) + '</ol>'; }
function _p(t) { return '<p>' + refL(t) + '</p>'; }
function _tip(t) { return '<div class="ref-box tip">' + DXIcon('info') + ' ' + refL(t) + '</div>'; }
function _tbl(head, rows) {
  return '<table><thead><tr>' + head.map(function (h) { return '<th>' + refL(h) + '</th>'; }).join('') + '</tr></thead><tbody>' +
    rows.map(function (r) { return '<tr>' + r.map(function (c) { return '<td>' + refL(c) + '</td>'; }).join('') + '</tr>'; }).join('') +
    '</tbody></table>';
}

function buildRefCategories() {
  return [
    { id:'getting-started', icon:'run', title:_T5('Getting Started','시작하기','はじめに','入门指南','入門指南','Primeros pasos'),
      desc:refL({en:'Setup, dashboard and the first demo',ko:'설정, 대시보드, 첫 데모',ja:'セットアップ・ダッシュボード・最初のデモ','zh-CN':'设置、仪表盘和第一个演示','zh-TW':'設定、儀表板與第一個示範',es:'Configuración, panel y primera demo'}) },
    { id:'demo-streaming', icon:'play', title:refL({en:'Demo & Streaming',ko:'데모 · 스트리밍',ja:'デモとストリーミング','zh-CN':'演示与流媒体','zh-TW':'示範與串流',es:'Demos y transmisión'}),
      desc:refL({en:'12 preset demos, WebRTC and MJPEG',ko:'프리셋 데모 12개, WebRTC · MJPEG',ja:'12 のプリセットデモ、WebRTC と MJPEG','zh-CN':'12 个预设演示，WebRTC 与 MJPEG','zh-TW':'12 個預設示範，WebRTC 與 MJPEG',es:'12 demos predefinidas, WebRTC y MJPEG'}) },
    { id:'pipeline', icon:'wrench', title:refL({en:'Pipeline',ko:'파이프라인',ja:'パイプライン','zh-CN':'管道','zh-TW':'管線',es:'Canalización'}),
      desc:refL({en:'Pipeline Builder, connection rules, presets and export',ko:'Pipeline Builder, 연결 규칙, 프리셋, 내보내기',ja:'Pipeline Builder・接続ルール・プリセット・エクスポート','zh-CN':'Pipeline Builder、连接规则、预设与导出','zh-TW':'Pipeline Builder、連接規則、預設與匯出',es:'Pipeline Builder, reglas de conexión, preajustes y exportación'}) },
    { id:'models-elements', icon:'models', title:refL({en:'Models & Elements',ko:'모델 · 요소',ja:'モデルとエレメント','zh-CN':'模型与元素','zh-TW':'模型與元素',es:'Modelos y elementos'}),
      desc:refL({en:'Model catalog, GStreamer elements and custom libraries',ko:'모델 카탈로그, GStreamer 요소, 사용자 라이브러리',ja:'モデルカタログ・GStreamer エレメント・カスタムライブラリ','zh-CN':'模型目录、GStreamer 元素与自定义库','zh-TW':'模型目錄、GStreamer 元素與自訂程式庫',es:'Catálogo de modelos, elementos de GStreamer y bibliotecas propias'}) },
    { id:'system', icon:'bolt', title:refL({en:'System',ko:'시스템',ja:'システム','zh-CN':'系统','zh-TW':'系統',es:'Sistema'}),
      desc:refL({en:'Shortcuts, API, theme and language',ko:'단축키, API, 테마와 언어',ja:'ショートカット・API・テーマと言語','zh-CN':'快捷键、API、主题与语言','zh-TW':'快捷鍵、API、主題與語言',es:'Atajos, API, tema e idioma'}) }
  ];
}

function buildRefTopics() { return [
  { id:'quick-start', cat:'getting-started', icon:'run',
    name:refL({en:'Quick Start',ko:'빠른 시작',ja:'クイックスタート','zh-CN':'快速开始','zh-TW':'快速開始',es:'Inicio rápido'}),
    desc:refL({en:'The basic flow of DX Stream',ko:'DX Stream의 기본 흐름',ja:'DX Stream の基本的な流れ','zh-CN':'DX Stream 的基本流程','zh-TW':'DX Stream 的基本流程',es:'El flujo básico de DX Stream'}),
    tabs:{ overview:
      _p({en:'Recommended order the first time:',ko:'처음에는 이 순서를 권합니다:',ja:'初めての場合はこの順番がおすすめです：','zh-CN':'首次使用时建议按此顺序：','zh-TW':'首次使用時建議依此順序：',es:'Orden recomendado la primera vez:'}) +
      _ol([
        {en:'<b>Setup</b> — finish the six steps (or press <b>Set up the rest</b>).',ko:'<b>Setup</b> — 6단계를 마칩니다(또는 <b>나머지 설정</b>).',ja:'<b>Setup</b> — 6 つのステップを完了します（または<b>残りをセットアップ</b>）。','zh-CN':'<b>Setup</b> — 完成六个步骤（或点击<b>完成其余设置</b>）。','zh-TW':'<b>Setup</b> — 完成六個步驟（或點擊<b>完成其餘設定</b>）。',es:'<b>Setup</b>: complete los seis pasos (o pulse <b>Configurar el resto</b>).'},
        {en:'<b>Dashboard</b> — check the NPU, GStreamer, models, videos and plugin build tiles.',ko:'<b>Dashboard</b> — NPU · GStreamer · 모델 · 영상 · 플러그인 빌드 타일을 확인합니다.',ja:'<b>Dashboard</b> — NPU・GStreamer・モデル・動画・プラグインビルドのタイルを確認します。','zh-CN':'<b>Dashboard</b> — 查看 NPU、GStreamer、模型、视频和插件构建磁贴。','zh-TW':'<b>Dashboard</b> — 查看 NPU、GStreamer、模型、影片與外掛建置磁磚。',es:'<b>Dashboard</b>: revise los mosaicos de NPU, GStreamer, modelos, videos y compilación de plugins.'},
        {en:'<b>Demo Launcher</b> — pick a demo and press Start.',ko:'<b>Demo Launcher</b> — 데모를 고르고 시작을 누릅니다.',ja:'<b>Demo Launcher</b> — デモを選んで開始を押します。','zh-CN':'<b>Demo Launcher</b> — 选择演示并点击开始。','zh-TW':'<b>Demo Launcher</b> — 選擇示範並點擊開始。',es:'<b>Demo Launcher</b>: elija una demo y pulse Iniciar.'},
        {en:'<b>Pipeline Builder</b> — load a demo as a preset and change it, or build your own.',ko:'<b>Pipeline Builder</b> — 데모를 프리셋으로 불러와 고치거나 직접 만듭니다.',ja:'<b>Pipeline Builder</b> — デモをプリセットとして読み込んで変更するか、自分で作ります。','zh-CN':'<b>Pipeline Builder</b> — 将演示作为预设载入后修改，或自行搭建。','zh-TW':'<b>Pipeline Builder</b> — 將示範作為預設載入後修改，或自行建立。',es:'<b>Pipeline Builder</b>: cargue una demo como preajuste y modifíquela, o cree la suya.'}]) +
      _tip({en:'A demo needs its model and sample video; Setup step 5 downloads both.',ko:'데모에는 그 모델과 샘플 영상이 필요하며, Setup 5단계가 둘 다 내려받습니다.',ja:'デモにはそのモデルとサンプル動画が必要で、Setup のステップ 5 が両方をダウンロードします。','zh-CN':'演示需要对应的模型和示例视频；Setup 第 5 步会一并下载。','zh-TW':'示範需要對應的模型與範例影片；Setup 第 5 步會一併下載。',es:'Una demo necesita su modelo y su video de ejemplo; el paso 5 de Setup descarga ambos.'}) }
  },
  { id:'setup-install', cat:'getting-started', icon:'gear',
    name:refL({en:'Setup & Install',ko:'설치 · 설정',ja:'セットアップとインストール','zh-CN':'安装与设置','zh-TW':'安裝與設定',es:'Instalación y configuración'}),
    desc:refL({en:'Six steps, environment check and diagnostics',ko:'6단계 설치, 환경 점검, 진단',ja:'6 ステップ・環境チェック・診断','zh-CN':'六个步骤、环境检查与诊断','zh-TW':'六個步驟、環境檢查與診斷',es:'Seis pasos, comprobación del entorno y diagnóstico'}),
    tabs:{ overview:
      _tbl([{en:'Step',ko:'단계',ja:'ステップ','zh-CN':'步骤','zh-TW':'步驟',es:'Paso'},{en:'What it does',ko:'하는 일',ja:'内容','zh-CN':'作用','zh-TW':'作用',es:'Qué hace'}],[
        ['1. Build Tools & Libraries',{en:'Build tools, GStreamer and libraries (install.sh)',ko:'빌드 도구 · GStreamer · 라이브러리 (install.sh)',ja:'ビルドツール・GStreamer・ライブラリ（install.sh）','zh-CN':'构建工具、GStreamer 与库（install.sh）','zh-TW':'建置工具、GStreamer 與程式庫（install.sh）',es:'Herramientas de compilación, GStreamer y bibliotecas (install.sh)'}],
        ['2. DX-Runtime Dependencies',{en:'DX-RT and dx_engine',ko:'DX-RT와 dx_engine',ja:'DX-RT と dx_engine','zh-CN':'DX-RT 与 dx_engine','zh-TW':'DX-RT 與 dx_engine',es:'DX-RT y dx_engine'}],
        ['3. NPU Linux Driver',{en:'The NPU kernel driver',ko:'NPU 커널 드라이버',ja:'NPU カーネルドライバー','zh-CN':'NPU 内核驱动','zh-TW':'NPU 核心驅動程式',es:'El driver del kernel de la NPU'}],
        ['4. GStreamer Plugin Build',{en:'Builds the DEEPX GStreamer elements (build.sh; Clean Build and Debug Mode options)',ko:'DEEPX GStreamer 요소 빌드 (build.sh, Clean Build · Debug Mode 선택)',ja:'DEEPX GStreamer エレメントをビルド（build.sh、Clean Build・Debug Mode オプション）','zh-CN':'构建 DEEPX GStreamer 元素（build.sh，可选 Clean Build 与 Debug Mode）','zh-TW':'建置 DEEPX GStreamer 元素（build.sh，可選 Clean Build 與 Debug Mode）',es:'Compila los elementos GStreamer de DEEPX (build.sh; opciones Clean Build y Debug Mode)'}],
        ['5. Model & Video Download',{en:'Demo models and sample videos (setup.sh)',ko:'데모 모델과 샘플 영상 (setup.sh)',ja:'デモ用モデルとサンプル動画（setup.sh）','zh-CN':'演示模型与示例视频（setup.sh）','zh-TW':'示範模型與範例影片（setup.sh）',es:'Modelos de las demos y videos de ejemplo (setup.sh)'}],
        ['6. WebRTC Dependencies',{en:'gstreamer1.0-nice and gir1.2-gst-plugins-bad-1.0 for low-latency viewing',ko:'저지연 보기를 위한 gstreamer1.0-nice · gir1.2-gst-plugins-bad-1.0',ja:'低遅延表示用の gstreamer1.0-nice と gir1.2-gst-plugins-bad-1.0','zh-CN':'用于低延迟观看的 gstreamer1.0-nice 与 gir1.2-gst-plugins-bad-1.0','zh-TW':'用於低延遲觀看的 gstreamer1.0-nice 與 gir1.2-gst-plugins-bad-1.0',es:'gstreamer1.0-nice y gir1.2-gst-plugins-bad-1.0 para ver con baja latencia'}]]) +
      _p({en:'<b>Environment Check</b> shows GStreamer, NPU runtime, custom plugins, model files, sample videos and WebRTC at a glance; <b>Deep Diagnostics</b> runs a detailed check.',ko:'<b>Environment Check</b>는 GStreamer · NPU 런타임 · 사용자 플러그인 · 모델 파일 · 샘플 영상 · WebRTC를 한눈에 보여 주고, <b>Deep Diagnostics</b>는 자세히 검사합니다.',ja:'<b>Environment Check</b> は GStreamer・NPU ランタイム・カスタムプラグイン・モデルファイル・サンプル動画・WebRTC を一目で表示し、<b>Deep Diagnostics</b> は詳しくチェックします。','zh-CN':'<b>Environment Check</b> 一览显示 GStreamer、NPU 运行时、自定义插件、模型文件、示例视频与 WebRTC；<b>Deep Diagnostics</b> 会进行详细检查。','zh-TW':'<b>Environment Check</b> 一覽顯示 GStreamer、NPU 執行環境、自訂外掛、模型檔、範例影片與 WebRTC；<b>Deep Diagnostics</b> 會進行詳細檢查。',es:'<b>Environment Check</b> muestra de un vistazo GStreamer, el runtime de la NPU, plugins propios, archivos de modelo, videos de ejemplo y WebRTC; <b>Deep Diagnostics</b> hace una revisión detallada.'}) }
  },
  { id:'dashboard-overview', cat:'getting-started', icon:'dashboard',
    name:refL({en:'Dashboard',ko:'대시보드',ja:'ダッシュボード','zh-CN':'仪表盘','zh-TW':'儀表板',es:'Panel'}),
    desc:refL({en:'Status tiles and quick launch',ko:'상태 타일과 빠른 실행',ja:'ステータスタイルとクイック起動','zh-CN':'状态磁贴与快速启动','zh-TW':'狀態磁磚與快速啟動',es:'Mosaicos de estado e inicio rápido'}),
    tabs:{ overview: _ul([
        {en:'<b>5 tiles</b> — NPU Device, GStreamer, Models (installed / total), Sample Videos, Plugin Build.',ko:'<b>타일 5개</b> — NPU Device, GStreamer, Models(설치 / 전체), Sample Videos, Plugin Build.',ja:'<b>5 つのタイル</b> — NPU Device・GStreamer・Models（インストール済み / 全体）・Sample Videos・Plugin Build。','zh-CN':'<b>5 个磁贴</b> — NPU Device、GStreamer、Models（已安装 / 总数）、Sample Videos、Plugin Build。','zh-TW':'<b>5 個磁磚</b> — NPU Device、GStreamer、Models（已安裝 / 總數）、Sample Videos、Plugin Build。',es:'<b>5 mosaicos</b>: NPU Device, GStreamer, Models (instalados / total), Sample Videos, Plugin Build.'},
        {en:'<b>Quick Launch</b> — Object Detection, Pose Estimation and Segmentation open the Demo Launcher and start that demo.',ko:'<b>Quick Launch</b> — Object Detection · Pose Estimation · Segmentation을 누르면 Demo Launcher가 열리며 그 데모가 시작됩니다.',ja:'<b>Quick Launch</b> — Object Detection・Pose Estimation・Segmentation を押すと Demo Launcher が開き、そのデモが始まります。','zh-CN':'<b>Quick Launch</b> — 点击 Object Detection、Pose Estimation 或 Segmentation 会打开 Demo Launcher 并启动该演示。','zh-TW':'<b>Quick Launch</b> — 點擊 Object Detection、Pose Estimation 或 Segmentation 會開啟 Demo Launcher 並啟動該示範。',es:'<b>Quick Launch</b>: Object Detection, Pose Estimation y Segmentation abren Demo Launcher e inician esa demo.'}]) }
  },
  { id:'demo-launcher', cat:'demo-streaming', icon:'demo',
    name:'Demo Launcher',
    desc:refL({en:'Run the 12 preset demos',ko:'프리셋 데모 12개 실행',ja:'12 のプリセットデモを実行','zh-CN':'运行 12 个预设演示','zh-TW':'執行 12 個預設示範',es:'Ejecute las 12 demos predefinidas'}),
    tabs:{ overview: _ul([
        {en:'The result stage is at the top; the cards below choose which demo it shows. Filter the cards by category.',ko:'결과 무대가 위에 있고, 아래 카드가 무대에 띄울 데모를 고릅니다. 카드는 분류로 거를 수 있습니다.',ja:'上に結果のステージがあり、下のカードでステージに表示するデモを選びます。カードはカテゴリで絞り込めます。','zh-CN':'结果舞台位于上方，下方卡片用于选择要显示的演示，可按类别筛选卡片。','zh-TW':'結果舞台位於上方，下方卡片用於選擇要顯示的示範，可依類別篩選卡片。',es:'El escenario de resultados está arriba; las tarjetas de abajo eligen qué demo muestra. Puede filtrarlas por categoría.'},
        {en:'Choose the view — <b>Local (WebRTC)</b> by default, or <b>Remote (MJPEG)</b> — and press <b>Start</b>; <b>Stop</b> ends the pipeline.',ko:'보기 방식을 고르고(기본 <b>Local (WebRTC)</b>, 또는 <b>Remote (MJPEG)</b>) <b>Start</b>를 누릅니다. <b>Stop</b>은 파이프라인을 끝냅니다.',ja:'表示方式（既定は <b>Local (WebRTC)</b>、または <b>Remote (MJPEG)</b>）を選び <b>Start</b> を押します。<b>Stop</b> でパイプラインを終了します。','zh-CN':'选择观看方式（默认 <b>Local (WebRTC)</b>，或 <b>Remote (MJPEG)</b>），点击 <b>Start</b>；<b>Stop</b> 结束管道。','zh-TW':'選擇觀看方式（預設 <b>Local (WebRTC)</b>，或 <b>Remote (MJPEG)</b>），點擊 <b>Start</b>；<b>Stop</b> 結束管線。',es:'Elija la vista (<b>Local (WebRTC)</b> por defecto, o <b>Remote (MJPEG)</b>) y pulse <b>Start</b>; <b>Stop</b> detiene la canalización.'},
        {en:'The panel shows FPS, resolution and model; the stage can go full screen.',ko:'패널에 FPS · 해상도 · 모델이 나오고, 무대는 전체 화면으로 볼 수 있습니다.',ja:'パネルに FPS・解像度・モデルが表示され、ステージは全画面にできます。','zh-CN':'面板显示 FPS、分辨率和模型；舞台可全屏显示。','zh-TW':'面板顯示 FPS、解析度與模型；舞台可全螢幕顯示。',es:'El panel muestra FPS, resolución y modelo; el escenario puede verse a pantalla completa.'}]) +
      _tip({en:'A card that is not ready says what is missing and links to Setup.',ko:'준비되지 않은 카드는 무엇이 없는지 말하고 Setup으로 이어 줍니다.',ja:'準備ができていないカードは不足しているものを示し、Setup へ案内します。','zh-CN':'未就绪的卡片会说明缺少什么，并链接到 Setup。','zh-TW':'未就緒的卡片會說明缺少什麼，並連結到 Setup。',es:'Una tarjeta que no está lista indica qué falta y enlaza a Setup.'}) }
  },
  { id:'streaming-modes', cat:'demo-streaming', icon:'stream',
    name:'WebRTC / MJPEG',
    desc:refL({en:'Two ways to watch the result',ko:'결과를 보는 두 가지 방식',ja:'結果を見る 2 つの方式','zh-CN':'观看结果的两种方式','zh-TW':'觀看結果的兩種方式',es:'Dos maneras de ver el resultado'}),
    tabs:{ overview:
      _tbl(['','Local (WebRTC)','Remote (MJPEG)'],[
        [{en:'Default',ko:'기본',ja:'既定','zh-CN':'默认','zh-TW':'預設',es:'Predeterminado'},DXIcon('check'),'—'],
        [{en:'Latency',ko:'지연',ja:'遅延','zh-CN':'延迟','zh-TW':'延遲',es:'Latencia'},{en:'Low',ko:'낮음',ja:'低い','zh-CN':'低','zh-TW':'低',es:'Baja'},{en:'Higher',ko:'더 높음',ja:'やや高い','zh-CN':'较高','zh-TW':'較高',es:'Mayor'}],
        [{en:'Needs',ko:'필요',ja:'必要なもの','zh-CN':'需要','zh-TW':'需要',es:'Requiere'},{en:'gstreamer1.0-nice (Setup step 6)',ko:'gstreamer1.0-nice (Setup 6단계)',ja:'gstreamer1.0-nice（Setup のステップ 6）','zh-CN':'gstreamer1.0-nice（Setup 第 6 步）','zh-TW':'gstreamer1.0-nice（Setup 第 6 步）',es:'gstreamer1.0-nice (paso 6 de Setup)'},{en:'Nothing extra; works from another computer',ko:'추가 설치 없음, 다른 컴퓨터에서도 동작',ja:'追加不要。別のコンピューターからも使える','zh-CN':'无需额外安装，可从其他电脑观看','zh-TW':'無需額外安裝，可從其他電腦觀看',es:'Nada adicional; funciona desde otro equipo'}]]) +
      _tip({en:'If WebRTC cannot connect within a few seconds, the view switches to MJPEG by itself.',ko:'WebRTC가 몇 초 안에 연결되지 않으면 보기가 저절로 MJPEG로 바뀝니다.',ja:'WebRTC が数秒以内に接続できない場合、表示は自動的に MJPEG に切り替わります。','zh-CN':'若 WebRTC 在几秒内无法连接，会自动切换为 MJPEG。','zh-TW':'若 WebRTC 在幾秒內無法連線，會自動切換為 MJPEG。',es:'Si WebRTC no conecta en unos segundos, la vista cambia sola a MJPEG.'}) }
  },
  { id:'demo-catalog', cat:'demo-streaming', icon:'clipboard',
    name:refL({en:'Demo Catalog',ko:'데모 목록',ja:'デモ一覧','zh-CN':'演示目录','zh-TW':'示範目錄',es:'Catálogo de demos'}),
    desc:refL({en:'The 12 demos and their models',ko:'데모 12개와 그 모델',ja:'12 のデモとそのモデル','zh-CN':'12 个演示及其模型','zh-TW':'12 個示範及其模型',es:'Las 12 demos y sus modelos'}),
    tabs:{ overview:
      _tbl(['#','Demo',{en:'Model',ko:'모델',ja:'モデル','zh-CN':'模型','zh-TW':'模型',es:'Modelo'}],[
        ['0','Object Detection','YOLO26n'],
        ['1','Object Detection (PPU)','YoloV5S_PPU'],
        ['2','Face Detection','YOLOv5s_Face'],
        ['3','Face Detection (PPU)','SCRFD500M_PPU'],
        ['4','Pose Estimation','YOLO26n-pose'],
        ['5','Pose Estimation (PPU)','YOLOV5Pose_PPU'],
        ['6','Instance Segmentation','YOLO26n-seg'],
        ['7','Multi-Object Tracking','YoloV5S_PPU + OC-SORT'],
        ['8','Multi-Stream','YoloV5S_PPU'],
        ['9','Multi-Stream RTSP','YoloV5S_PPU'],
        ['10','Secondary Inference','YoloV5S_PPU + EfficientNet-Lite0 + SCRFD500M'],
        ['11','Depth Estimation','YOLO26-depth-n']]) }
  },
  { id:'visual-editor', cat:'pipeline', icon:'wrench',
    name:'Pipeline Builder',
    desc:refL({en:'Build a pipeline on a canvas',ko:'캔버스에서 파이프라인 만들기',ja:'キャンバスでパイプラインを組む','zh-CN':'在画布上搭建管道','zh-TW':'在畫布上建立管線',es:'Construya una canalización en un lienzo'}),
    tabs:{ overview: _ul([
        {en:'<b>Palette</b> — elements in 9 categories: source, preprocess, inference, postprocess, tracking, visualization, messaging, output, utility.',ko:'<b>팔레트</b> — 9개 분류의 요소: source, preprocess, inference, postprocess, tracking, visualization, messaging, output, utility.',ja:'<b>パレット</b> — 9 カテゴリのエレメント：source・preprocess・inference・postprocess・tracking・visualization・messaging・output・utility。','zh-CN':'<b>元素面板</b> — 9 个类别的元素：source、preprocess、inference、postprocess、tracking、visualization、messaging、output、utility。','zh-TW':'<b>元素面板</b> — 9 個類別的元素：source、preprocess、inference、postprocess、tracking、visualization、messaging、output、utility。',es:'<b>Paleta</b>: elementos en 9 categorías (source, preprocess, inference, postprocess, tracking, visualization, messaging, output, utility).'},
        {en:'<b>Drag</b> an element onto the canvas, then drag from an output port to an input port to connect.',ko:'요소를 캔버스로 <b>끌어다 놓고</b>, 출력 포트에서 입력 포트로 끌어 연결합니다.',ja:'エレメントをキャンバスに<b>ドラッグ</b>し、出力ポートから入力ポートへドラッグして接続します。','zh-CN':'将元素<b>拖到</b>画布上，再从输出端口拖到输入端口进行连接。','zh-TW':'將元素<b>拖曳</b>到畫布上，再從輸出埠拖曳到輸入埠進行連接。',es:'<b>Arrastre</b> un elemento al lienzo y luego de un puerto de salida a uno de entrada para conectar.'},
        {en:'<b>Right-click</b> a node: Delete, Copy, Properties. On empty canvas: Paste, Select All, Undo, Redo, Fit View, Clear All.',ko:'노드를 <b>오른쪽 클릭</b>: Delete, Copy, Properties. 빈 캔버스: Paste, Select All, Undo, Redo, Fit View, Clear All.',ja:'ノードを<b>右クリック</b>：Delete・Copy・Properties。空のキャンバス：Paste・Select All・Undo・Redo・Fit View・Clear All。','zh-CN':'<b>右键</b>节点：Delete、Copy、Properties。空白画布：Paste、Select All、Undo、Redo、Fit View、Clear All。','zh-TW':'<b>右鍵</b>節點：Delete、Copy、Properties。空白畫布：Paste、Select All、Undo、Redo、Fit View、Clear All。',es:'<b>Clic derecho</b> en un nodo: Delete, Copy, Properties. En el lienzo vacío: Paste, Select All, Undo, Redo, Fit View, Clear All.'},
        {en:'The <b>properties panel</b> edits the selected element; the <b>minimap</b> shows the whole pipeline.',ko:'<b>속성 패널</b>은 고른 요소를 고치고, <b>미니맵</b>은 파이프라인 전체를 보여 줍니다.',ja:'<b>プロパティパネル</b>で選択中のエレメントを編集し、<b>ミニマップ</b>でパイプライン全体を表示します。','zh-CN':'<b>属性面板</b>编辑所选元素；<b>小地图</b>显示整个管道。','zh-TW':'<b>屬性面板</b>編輯所選元素；<b>小地圖</b>顯示整個管線。',es:'El <b>panel de propiedades</b> edita el elemento seleccionado; el <b>minimapa</b> muestra toda la canalización.'},
        {en:'Mouse wheel zooms; drag the empty canvas (or middle-drag) to pan.',ko:'마우스 휠로 확대 · 축소하고, 빈 캔버스를 끌거나 가운데 단추로 끌어 이동합니다.',ja:'マウスホイールで拡大縮小し、空のキャンバスをドラッグ（または中ボタンでドラッグ）して移動します。','zh-CN':'鼠标滚轮缩放；拖动空白画布（或按住中键拖动）可平移。','zh-TW':'滑鼠滾輪縮放；拖曳空白畫布（或按住中鍵拖曳）可平移。',es:'La rueda del ratón hace zoom; arrastre el lienzo vacío (o con el botón central) para desplazarse.'}]) }
  },
  { id:'connection-rules', cat:'pipeline', icon:'external',
    name:refL({en:'Connection Rules',ko:'연결 규칙',ja:'接続ルール','zh-CN':'连接规则','zh-TW':'連接規則',es:'Reglas de conexión'}),
    desc:refL({en:'What the builder checks and fixes',ko:'빌더가 확인하고 고쳐 주는 것',ja:'ビルダーが確認・修正すること','zh-CN':'构建器检查与修正的内容','zh-TW':'建構器檢查與修正的內容',es:'Lo que el constructor comprueba y corrige'}),
    tabs:{ overview: _ul([
        {en:'Each connection is checked by category: allowed, allowed with a warning, or blocked.',ko:'연결마다 분류에 따라 허용 · 경고 후 허용 · 차단으로 판단합니다.',ja:'接続ごとにカテゴリに応じて、許可・警告付きで許可・ブロックを判定します。','zh-CN':'每个连接按类别判定：允许、警告后允许或阻止。','zh-TW':'每個連接依類別判定：允許、警告後允許或阻擋。',es:'Cada conexión se evalúa por categoría: permitida, permitida con aviso o bloqueada.'},
        {en:'From visualization, postprocess or tracking into an encoder or display sink, <code>videoconvert</code> is inserted for you.',ko:'visualization · postprocess · tracking에서 인코더나 화면 sink로 이으면 <code>videoconvert</code>가 자동으로 들어갑니다.',ja:'visualization・postprocess・tracking からエンコーダーや表示用 sink へつなぐと、<code>videoconvert</code> が自動で挿入されます。','zh-CN':'从 visualization、postprocess 或 tracking 连接到编码器或显示 sink 时，会自动插入 <code>videoconvert</code>。','zh-TW':'從 visualization、postprocess 或 tracking 連接到編碼器或顯示 sink 時，會自動插入 <code>videoconvert</code>。',es:'Al conectar visualization, postprocess o tracking con un codificador o un sink de pantalla, se inserta <code>videoconvert</code> automáticamente.'},
        {en:'DxPostprocess gets its <code>inference-id</code> from the DxInfer before it.',ko:'DxPostprocess의 <code>inference-id</code>는 앞의 DxInfer에서 채워집니다.',ja:'DxPostprocess の <code>inference-id</code> は前の DxInfer から設定されます。','zh-CN':'DxPostprocess 的 <code>inference-id</code> 取自其前面的 DxInfer。','zh-TW':'DxPostprocess 的 <code>inference-id</code> 取自其前面的 DxInfer。',es:'DxPostprocess toma su <code>inference-id</code> del DxInfer anterior.'},
        {en:'Warnings: no source, isolated nodes, DxGather or compositor with fewer than 2 inputs, tee with fewer than 2 outputs, DxDeTile without DxTile.',ko:'경고: source 없음, 떨어진 노드, 입력이 2개 미만인 DxGather · compositor, 출력이 2개 미만인 tee, DxTile 없는 DxDeTile.',ja:'警告：source がない・孤立したノード・入力が 2 未満の DxGather / compositor・出力が 2 未満の tee・DxTile のない DxDeTile。','zh-CN':'警告：没有 source、孤立节点、输入少于 2 个的 DxGather 或 compositor、输出少于 2 个的 tee、缺少 DxTile 的 DxDeTile。','zh-TW':'警告：沒有 source、孤立節點、輸入少於 2 個的 DxGather 或 compositor、輸出少於 2 個的 tee、缺少 DxTile 的 DxDeTile。',es:'Avisos: sin source, nodos aislados, DxGather o compositor con menos de 2 entradas, tee con menos de 2 salidas, DxDeTile sin DxTile.'},
        {en:'DxMsgBroker has no output; put DxMsgConv before it.',ko:'DxMsgBroker에는 출력이 없으며, 앞에 DxMsgConv를 두세요.',ja:'DxMsgBroker には出力がありません。前に DxMsgConv を置いてください。','zh-CN':'DxMsgBroker 没有输出端；请在它前面放置 DxMsgConv。','zh-TW':'DxMsgBroker 沒有輸出端；請在它前面放置 DxMsgConv。',es:'DxMsgBroker no tiene salida; coloque DxMsgConv antes.'}]) }
  },
  { id:'preset-export', cat:'pipeline', icon:'download',
    name:refL({en:'Presets & Export',ko:'프리셋 · 내보내기',ja:'プリセットとエクスポート','zh-CN':'预设与导出','zh-TW':'預設與匯出',es:'Preajustes y exportación'}),
    desc:refL({en:'Load a demo, save JSON, see the gst-launch command',ko:'데모 불러오기, JSON 저장, gst-launch 명령 보기',ja:'デモの読み込み・JSON 保存・gst-launch コマンド表示','zh-CN':'载入演示、保存 JSON、查看 gst-launch 命令','zh-TW':'載入示範、儲存 JSON、檢視 gst-launch 指令',es:'Cargar una demo, guardar JSON y ver el comando gst-launch'}),
    tabs:{ overview: _ul([
        {en:'<b>Presets</b> — each demo can be loaded onto the canvas as a starting point.',ko:'<b>프리셋</b> — 데모마다 캔버스로 불러와 출발점으로 쓸 수 있습니다.',ja:'<b>プリセット</b> — 各デモをキャンバスに読み込んで出発点にできます。','zh-CN':'<b>预设</b> — 每个演示都可载入画布作为起点。','zh-TW':'<b>預設</b> — 每個示範都可載入畫布作為起點。',es:'<b>Preajustes</b>: cada demo puede cargarse en el lienzo como punto de partida.'},
        {en:'<b>Export</b> downloads the pipeline as <code>pipeline.json</code>; <b>Import</b> loads such a file.',ko:'<b>Export</b>는 파이프라인을 <code>pipeline.json</code>으로 내려받고, <b>Import</b>는 그 파일을 불러옵니다.',ja:'<b>Export</b> はパイプラインを <code>pipeline.json</code> としてダウンロードし、<b>Import</b> はそのファイルを読み込みます。','zh-CN':'<b>Export</b> 将管道下载为 <code>pipeline.json</code>；<b>Import</b> 载入此类文件。','zh-TW':'<b>Export</b> 將管線下載為 <code>pipeline.json</code>；<b>Import</b> 載入此類檔案。',es:'<b>Export</b> descarga la canalización como <code>pipeline.json</code>; <b>Import</b> carga un archivo así.'},
        {en:'The command preview shows the equivalent <code>gst-launch-1.0</code> line.',ko:'명령 미리보기에 같은 뜻의 <code>gst-launch-1.0</code> 명령이 나옵니다.',ja:'コマンドプレビューに同等の <code>gst-launch-1.0</code> コマンドが表示されます。','zh-CN':'命令预览显示等效的 <code>gst-launch-1.0</code> 命令。','zh-TW':'指令預覽顯示等效的 <code>gst-launch-1.0</code> 指令。',es:'La vista previa del comando muestra la línea <code>gst-launch-1.0</code> equivalente.'},
        {en:'<b>Run</b> and <b>Stop</b> start and end the pipeline; Undo / Redo keeps the last 50 changes.',ko:'<b>Run</b> · <b>Stop</b>으로 파이프라인을 시작 · 종료하고, Undo / Redo는 최근 50개 변경을 기억합니다.',ja:'<b>Run</b>・<b>Stop</b> でパイプラインを開始・終了し、Undo / Redo は直近 50 件の変更を保持します。','zh-CN':'<b>Run</b> 与 <b>Stop</b> 用于启动和结束管道；Undo / Redo 保留最近 50 次更改。','zh-TW':'<b>Run</b> 與 <b>Stop</b> 用於啟動與結束管線；Undo / Redo 保留最近 50 次變更。',es:'<b>Run</b> y <b>Stop</b> inician y detienen la canalización; Deshacer / Rehacer guarda los últimos 50 cambios.'}]) }
  },
  { id:'model-catalog', cat:'models-elements', icon:'models',
    name:refL({en:'Model Catalog',ko:'모델 카탈로그',ja:'モデルカタログ','zh-CN':'模型目录','zh-TW':'模型目錄',es:'Catálogo de modelos'}),
    desc:refL({en:'Demo models: install state and download',ko:'데모 모델의 설치 상태와 다운로드',ja:'デモ用モデルのインストール状態とダウンロード','zh-CN':'演示模型的安装状态与下载','zh-TW':'示範模型的安裝狀態與下載',es:'Modelos de las demos: estado y descarga'}),
    tabs:{ overview: _ul([
        {en:'Cards show the name, description, file, category and whether the model is installed.',ko:'카드에 이름 · 설명 · 파일 · 분류와 설치 여부가 나옵니다.',ja:'カードに名前・説明・ファイル・カテゴリとインストール状態が表示されます。','zh-CN':'卡片显示名称、描述、文件、类别以及是否已安装。','zh-TW':'卡片顯示名稱、說明、檔案、類別以及是否已安裝。',es:'Las tarjetas muestran nombre, descripción, archivo, categoría y si el modelo está instalado.'},
        {en:'<b>Download</b> fetches a missing model; the card updates when it is done.',ko:'<b>Download</b>는 없는 모델을 받고, 끝나면 카드가 바뀝니다.',ja:'<b>Download</b> で足りないモデルを取得し、完了するとカードが更新されます。','zh-CN':'<b>Download</b> 获取缺少的模型，完成后卡片会更新。','zh-TW':'<b>Download</b> 取得缺少的模型，完成後卡片會更新。',es:'<b>Download</b> obtiene un modelo que falta; la tarjeta se actualiza al terminar.'},
        {en:'Open a card for <b>Detail</b> and <b>Metadata</b> tabs.',ko:'카드를 열면 <b>Detail</b> · <b>Metadata</b> 탭이 있습니다.',ja:'カードを開くと <b>Detail</b>・<b>Metadata</b> タブがあります。','zh-CN':'打开卡片可查看 <b>Detail</b> 和 <b>Metadata</b> 标签。','zh-TW':'開啟卡片可查看 <b>Detail</b> 與 <b>Metadata</b> 分頁。',es:'Abra una tarjeta para ver las pestañas <b>Detail</b> y <b>Metadata</b>.'},
        {en:'Search works within the chosen category.',ko:'검색은 고른 분류 안에서 동작합니다.',ja:'検索は選んだカテゴリ内で行われます。','zh-CN':'搜索在所选类别内进行。','zh-TW':'搜尋在所選類別內進行。',es:'La búsqueda funciona dentro de la categoría elegida.'}]) }
  },
  { id:'element-reference', cat:'models-elements', icon:'puzzle',
    name:refL({en:'Element Reference',ko:'요소 레퍼런스',ja:'エレメントリファレンス','zh-CN':'元素参考','zh-TW':'元素參考',es:'Referencia de elementos'}),
    desc:refL({en:'29 GStreamer elements: 17 DEEPX and 12 standard',ko:'GStreamer 요소 29개: DEEPX 17개 · 표준 12개',ja:'29 の GStreamer エレメント：DEEPX 17・標準 12','zh-CN':'29 个 GStreamer 元素：DEEPX 17 个、标准 12 个','zh-TW':'29 個 GStreamer 元素：DEEPX 17 個、標準 12 個',es:'29 elementos de GStreamer: 17 de DEEPX y 12 estándar'}),
    tabs:{ overview: _ul([
        {en:'Elements are grouped in the same 9 categories as the Pipeline Builder palette.',ko:'요소는 Pipeline Builder 팔레트와 같은 9개 분류로 묶입니다.',ja:'エレメントは Pipeline Builder のパレットと同じ 9 カテゴリに分かれています。','zh-CN':'元素按与 Pipeline Builder 元素面板相同的 9 个类别分组。','zh-TW':'元素依與 Pipeline Builder 元素面板相同的 9 個類別分組。',es:'Los elementos se agrupan en las mismas 9 categorías que la paleta de Pipeline Builder.'},
        {en:'The detail panel has the description, key features, a pipeline hint, an example, related elements, properties and pads.',ko:'상세 패널에는 설명 · 주요 기능 · 파이프라인 힌트 · 예시 · 관련 요소 · 속성 · 패드가 있습니다.',ja:'詳細パネルには説明・主な機能・パイプラインのヒント・例・関連エレメント・プロパティ・パッドがあります。','zh-CN':'详情面板包含描述、主要功能、管道提示、示例、相关元素、属性与 pad。','zh-TW':'詳情面板包含說明、主要功能、管線提示、範例、相關元素、屬性與 pad。',es:'El panel de detalle incluye descripción, funciones clave, una pista de canalización, un ejemplo, elementos relacionados, propiedades y pads.'}]) +
      _tip({en:'DxPreprocess, DxInfer and DxPostprocess work together: DxPostprocess must use the <code>inference-id</code> of its DxInfer.',ko:'DxPreprocess · DxInfer · DxPostprocess는 함께 동작하며, DxPostprocess는 자기 DxInfer의 <code>inference-id</code>를 써야 합니다.',ja:'DxPreprocess・DxInfer・DxPostprocess は連携して動きます。DxPostprocess は対応する DxInfer の <code>inference-id</code> を使う必要があります。','zh-CN':'DxPreprocess、DxInfer 与 DxPostprocess 协同工作：DxPostprocess 必须使用其 DxInfer 的 <code>inference-id</code>。','zh-TW':'DxPreprocess、DxInfer 與 DxPostprocess 協同運作：DxPostprocess 必須使用其 DxInfer 的 <code>inference-id</code>。',es:'DxPreprocess, DxInfer y DxPostprocess trabajan juntos: DxPostprocess debe usar el <code>inference-id</code> de su DxInfer.'}) }
  },
  { id:'custom-library', cat:'models-elements', icon:'puzzle',
    name:refL({en:'Custom Library',ko:'사용자 라이브러리',ja:'カスタムライブラリ','zh-CN':'自定义库','zh-TW':'自訂程式庫',es:'Biblioteca propia'}),
    desc:refL({en:'Your own post-processing in C',ko:'C로 만드는 나만의 후처리',ja:'C で書く独自の後処理','zh-CN':'用 C 编写自己的后处理','zh-TW':'用 C 撰寫自己的後處理',es:'Su propio posprocesado en C'}),
    tabs:{ overview: _ul([
        {en:'Upload C sources with a <code>meson.build</code>; the build starts right away.',ko:'C 소스와 <code>meson.build</code>를 올리면 바로 빌드가 시작됩니다.',ja:'C ソースと <code>meson.build</code> をアップロードすると、すぐにビルドが始まります。','zh-CN':'上传 C 源码和 <code>meson.build</code> 后会立即开始构建。','zh-TW':'上傳 C 原始碼與 <code>meson.build</code> 後會立即開始建置。',es:'Suba fuentes en C con un <code>meson.build</code>; la compilación empieza de inmediato.'},
        {en:'Build: <code>meson setup</code> → <code>meson compile</code> → <code>sudo meson install</code>, into <code>/usr/local/share/gstdxstream/lib/</code>; the log updates every second.',ko:'빌드: <code>meson setup</code> → <code>meson compile</code> → <code>sudo meson install</code>, 설치 위치 <code>/usr/local/share/gstdxstream/lib/</code>. 로그는 1초마다 갱신됩니다.',ja:'ビルド：<code>meson setup</code> → <code>meson compile</code> → <code>sudo meson install</code>、インストール先 <code>/usr/local/share/gstdxstream/lib/</code>。ログは 1 秒ごとに更新されます。','zh-CN':'构建：<code>meson setup</code> → <code>meson compile</code> → <code>sudo meson install</code>，安装到 <code>/usr/local/share/gstdxstream/lib/</code>；日志每秒更新。','zh-TW':'建置：<code>meson setup</code> → <code>meson compile</code> → <code>sudo meson install</code>，安裝到 <code>/usr/local/share/gstdxstream/lib/</code>；記錄每秒更新。',es:'Compilación: <code>meson setup</code> → <code>meson compile</code> → <code>sudo meson install</code>, en <code>/usr/local/share/gstdxstream/lib/</code>; el registro se actualiza cada segundo.'},
        {en:'The built <code>.so</code> appears in the DxPostprocess <code>library-file-path</code> list the next time the Pipeline Builder opens.',ko:'빌드된 <code>.so</code>는 다음에 Pipeline Builder를 열 때 DxPostprocess의 <code>library-file-path</code> 목록에 나타납니다.',ja:'ビルドした <code>.so</code> は、次に Pipeline Builder を開いたときに DxPostprocess の <code>library-file-path</code> 一覧に表示されます。','zh-CN':'构建出的 <code>.so</code> 会在下次打开 Pipeline Builder 时出现在 DxPostprocess 的 <code>library-file-path</code> 列表中。','zh-TW':'建置出的 <code>.so</code> 會在下次開啟 Pipeline Builder 時出現在 DxPostprocess 的 <code>library-file-path</code> 清單中。',es:'El <code>.so</code> compilado aparece en la lista <code>library-file-path</code> de DxPostprocess la próxima vez que abra Pipeline Builder.'},
        {en:'The same page also uploads <code>.dxnn</code> model files.',ko:'같은 페이지에서 <code>.dxnn</code> 모델 파일도 올릴 수 있습니다.',ja:'同じページで <code>.dxnn</code> モデルファイルもアップロードできます。','zh-CN':'同一页面也可上传 <code>.dxnn</code> 模型文件。','zh-TW':'同一頁面也可上傳 <code>.dxnn</code> 模型檔案。',es:'La misma página también sube archivos de modelo <code>.dxnn</code>.'}]) +
      _tip({en:'The <code>.so</code> must export the C function named in <code>function-name</code>.',ko:'<code>.so</code>는 <code>function-name</code>에 적은 C 함수를 내보내야 합니다.',ja:'<code>.so</code> は <code>function-name</code> に指定した C 関数をエクスポートする必要があります。','zh-CN':'<code>.so</code> 必须导出 <code>function-name</code> 中指定的 C 函数。','zh-TW':'<code>.so</code> 必須匯出 <code>function-name</code> 中指定的 C 函式。',es:'El <code>.so</code> debe exportar la función C indicada en <code>function-name</code>.'}) }
  },
  { id:'keyboard-shortcuts', cat:'system', icon:'dev',
    name:refL({en:'Keyboard Shortcuts',ko:'키보드 단축키',ja:'キーボードショートカット','zh-CN':'键盘快捷键','zh-TW':'鍵盤快捷鍵',es:'Atajos de teclado'}),
    desc:refL({en:'Pipeline Builder keys',ko:'Pipeline Builder 키',ja:'Pipeline Builder のキー','zh-CN':'Pipeline Builder 按键','zh-TW':'Pipeline Builder 按鍵',es:'Teclas de Pipeline Builder'}),
    tabs:{ overview:
      _tbl([{en:'Key',ko:'키',ja:'キー','zh-CN':'按键','zh-TW':'按鍵',es:'Tecla'},{en:'Action (Pipeline Builder)',ko:'동작 (Pipeline Builder)',ja:'動作（Pipeline Builder）','zh-CN':'作用（Pipeline Builder）','zh-TW':'作用（Pipeline Builder）',es:'Acción (Pipeline Builder)'}],[
        ['<code>Ctrl+Z</code> / <code>Ctrl+Shift+Z</code>',{en:'Undo / Redo',ko:'실행 취소 / 다시 실행',ja:'元に戻す / やり直し','zh-CN':'撤销 / 重做','zh-TW':'復原 / 重做',es:'Deshacer / Rehacer'}],
        ['<code>Ctrl+C</code> / <code>Ctrl+V</code>',{en:'Copy / Paste nodes',ko:'노드 복사 / 붙여넣기',ja:'ノードのコピー / 貼り付け','zh-CN':'复制 / 粘贴节点','zh-TW':'複製 / 貼上節點',es:'Copiar / Pegar nodos'}],
        ['<code>Ctrl+A</code>',{en:'Select all',ko:'모두 선택',ja:'すべて選択','zh-CN':'全选','zh-TW':'全選',es:'Seleccionar todo'}],
        ['<code>Shift</code> + click',{en:'Add to the selection',ko:'선택에 추가',ja:'選択に追加','zh-CN':'加入选择','zh-TW':'加入選取',es:'Añadir a la selección'}],
        ['<code>Delete</code>',{en:'Delete the selected node or connection',ko:'고른 노드나 연결 삭제',ja:'選択中のノードまたは接続を削除','zh-CN':'删除所选节点或连接','zh-TW':'刪除所選節點或連接',es:'Eliminar el nodo o la conexión seleccionados'}],
        ['<code>Esc</code>',{en:'Clear the selection; also closes this detail panel',ko:'선택 해제, 이 상세 패널도 닫음',ja:'選択を解除。この詳細パネルも閉じる','zh-CN':'取消选择；也会关闭此详情面板','zh-TW':'取消選取；也會關閉此詳情面板',es:'Quitar la selección; también cierra este panel'}]]) }
  },
  { id:'api-endpoints', cat:'system', icon:'globe',
    name:'API Endpoints',
    desc:refL({en:'The main HTTP endpoints',ko:'주요 HTTP 엔드포인트',ja:'主な HTTP エンドポイント','zh-CN':'主要 HTTP 端点','zh-TW':'主要 HTTP 端點',es:'Los endpoints HTTP principales'}),
    tabs:{ overview:
      _tbl([{en:'Group',ko:'구분',ja:'グループ','zh-CN':'分组','zh-TW':'分組',es:'Grupo'},'Method','Path'],[
        ['Status','GET','<code>/api/status</code>'],
        ['Demos','GET','<code>/api/demos</code>'],
        ['Demos','POST','<code>/api/demos/:id/start</code> · <code>/api/demos/:id/stop</code>'],
        ['Pipeline','POST','<code>/api/pipeline/run</code> · <code>/api/pipeline/stop</code> · <code>/api/pipeline/validate</code>'],
        ['Pipeline','GET','<code>/api/pipeline/status</code> · <code>/api/pipeline/elements</code>'],
        ['Stream','GET','<code>/api/stream/mjpeg</code> · <code>/api/stream/snapshot</code>'],
        ['WebRTC','POST','<code>/api/webrtc/offer</code> · <code>/api/webrtc/ice</code>'],
        ['Models','GET','<code>/api/models</code> · <code>/api/models/:file/metadata</code>'],
        ['Elements','GET','<code>/api/elements</code>'],
        ['Custom','GET / POST','<code>/api/custom-library</code> · <code>/api/custom-library/upload</code>'],
        ['Setup','GET','<code>/api/setup/status</code> · <code>/api/diagnostics</code>']]) }
  },
  { id:'theme-language', cat:'system', icon:'theme',
    name:refL({en:'Theme & Language',ko:'테마 · 언어',ja:'テーマと言語','zh-CN':'主题与语言','zh-TW':'主題與語言',es:'Tema e idioma'}),
    desc:refL({en:'Dark, light or system; six languages',ko:'어둡게 · 밝게 · 시스템, 6개 언어',ja:'ダーク・ライト・システムと 6 言語','zh-CN':'深色、浅色或跟随系统；六种语言','zh-TW':'深色、淺色或跟隨系統；六種語言',es:'Oscuro, claro o del sistema; seis idiomas'}),
    tabs:{ overview: _ul([
        {en:'The theme button cycles dark → light → system.',ko:'테마 단추는 어둡게 → 밝게 → 시스템 순으로 바뀝니다.',ja:'テーマボタンはダーク → ライト → システムの順に切り替わります。','zh-CN':'主题按钮按深色 → 浅色 → 跟随系统切换。','zh-TW':'主題按鈕依深色 → 淺色 → 跟隨系統切換。',es:'El botón de tema alterna oscuro → claro → del sistema.'},
        {en:'The language menu offers English, 한국어, 日本語, Español, 简体中文 and 繁體中文.',ko:'언어 메뉴에는 English, 한국어, 日本語, Español, 简体中文, 繁體中文이 있습니다.',ja:'言語メニューには English・한국어・日本語・Español・简体中文・繁體中文 があります。','zh-CN':'语言菜单提供 English、한국어、日本語、Español、简体中文 和 繁體中文。','zh-TW':'語言選單提供 English、한국어、日本語、Español、简体中文 與 繁體中文。',es:'El menú de idioma ofrece English, 한국어, 日本語, Español, 简体中文 y 繁體中文.'},
        {en:'Both are remembered in this browser and apply to every module.',ko:'두 설정 모두 이 브라우저에 기억되고 모든 모듈에 적용됩니다.',ja:'どちらもこのブラウザに記憶され、すべてのモジュールに適用されます。','zh-CN':'两项设置都会保存在此浏览器中并应用于所有模块。','zh-TW':'兩項設定都會保存在此瀏覽器中並套用到所有模組。',es:'Ambas preferencias se recuerdan en este navegador y se aplican a todos los módulos.'}]) }
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
      tmp.innerHTML = _refTopicName(t) + ' ' + t.desc;
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
      card.innerHTML = '<span class="ref-section-icon">' + _refIco(topic.icon) + '</span>'
        + '<span class="ref-section-info">'
        + '<span class="ref-section-name">' + _refTopicName(topic) + '</span>'
        + '<span class="ref-section-desc">' + topic.desc + '</span>'
        + '</span>';
      grid.appendChild(card);
    });
    container.appendChild(grid);
  });
}

// 구역 · 주제 아이콘은 sprite 이름 (아이콘 체계 단계 5). 옛 글자 icon 은 그대로.
/* 화면 이름 주제 (Demo Launcher · Pipeline Builder · API Endpoints) 는 탭과 같은 사전 키라 T() 로 번역한다 */
function _refTopicName(t) { return typeof T === 'function' ? T(t.name) : t.name; }

function _refIco(name) {
  return (/^[a-z0-9_-]+$/.test(name || '') && typeof DXIcon === 'function') ? DXIcon(name) : (name || '');
}

function buildDetailHtml(topic) {
  var tabKeys = Object.keys(topic.tabs);
  var tabLabels = {
    overview: ((typeof DXIcon === 'function') ? DXIcon('clipboard') : '') + ' ' + _T5('Overview','개요','概要','概述','概述','Descripción general'),
    params: ((typeof DXIcon === 'function') ? DXIcon('gear') : '') + ' ' + _T5('Details','상세','詳細','详情','詳情','Detalles'),
    workflow: ((typeof DXIcon === 'function') ? DXIcon('refresh') : '') + ' ' + _T5('Workflow','작업 순서','手順','操作流程','操作流程','Flujo de trabajo'),
    tips: ((typeof DXIcon === 'function') ? DXIcon('info') : '') + ' ' + _T5('Tips','팁','ヒント','提示','提示','Consejos')
  };
  var html = '<div class="ref-detail-hd"><div><div class="ref-detail-kicker">'
    + _T5('Reference','레퍼런스','リファレンス','参考','參考','Referencia') + '</div><h2>'
    + _refIco(topic.icon) + ' ' + _refTopicName(topic) + '</h2><p>' + topic.desc + '</p></div></div>';
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
  closeBtn.innerHTML = ((typeof DXIcon === 'function') ? DXIcon('x') : ''); closeBtn.setAttribute('aria-label', 'Close');
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
  allChip.textContent = _T5('All','전체','すべて','全部','全部','Todo');
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
