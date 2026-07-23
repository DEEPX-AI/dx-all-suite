(function(){
'use strict';


function refT5(en, ko, ja, zhCN, zhTW, es){
  var lang=(window.DXI18n&&DXI18n.lang)||localStorage.getItem('dx-lang')||'en';
  if(lang==='ko') return ko || en;
  if(lang==='ja') return ja || en;
  if(lang==='zh-CN') return zhCN || en;
  if(lang==='zh-TW') return zhTW || en;
  if(lang==='es') return es || en;
  return en;
}

function refApiBase(){
  var origin=(window.location&&window.location.origin)||'';
  return origin+'/api/';
}

/* ════════════  DATA  ════════════ */
function buildRefCategories(){return [
  {id:'start',   title:refT5('Getting Started','시작하기','はじめに','快速入门','快速入門'),   desc:refT5('From install to first run','설치부터 첫 실행까지','インストールから初回実行まで','从安装到首次运行','從安裝到首次運行')},
  {id:'core',    title:refT5('Core Features','핵심 기능','コア機能','核心功能','核心功能'),     desc:refT5('Inference · Benchmark · Compare core features','추론 · 벤치마크 · 비교 핵심 기능','推論・ベンチマーク・比較のコア機能','推理·基准测试·对比核心功能','推理·基準測試·對比核心功能')},
  {id:'advanced',title:refT5('Advanced Tools','고급 도구','高度なツール','高级工具','進階工具'),    desc:refT5('Compiler · Pipeline','컴파일러 · 파이프라인','コンパイラ・パイプライン','编译器·流水线','編譯器·流水線')},
  {id:'system',  title:refT5('System & Extras','시스템 & 기타','システム＆その他','系统与其他','系統與其他'),   desc:refT5('Shortcuts · Global features','단축키 · 전역 기능','ショートカット・グローバル機能','快捷键·全局功能','快捷鍵·全域功能')}
];}
var _CAT=buildRefCategories();

function buildRefSections(){
var apiBase=refApiBase();
return [
/* ── Getting Started ── */
{cat:'start',id:'quick-start',icon:'🚀',name:refT5('Quick Start Guide','빠른 시작 가이드','クイックスタートガイド','快速入门指南','快速入門指南'),desc:refT5('Run your first inference in 5 minutes','5분 안에 첫 추론 실행하기','5分で初めての推論を実行','5分钟内运行首次推理','5分鐘內執行首次推理'),page:null,tabs:{
  overview:refT5('<h4>Overview</h4><p>A quick start guide for first-time DX-APP users. Follow the steps below in order and you can run your first NPU inference within 5 minutes.</p>'+
    '<div class="ref-flow"><span class="ref-flow-step">① Run Setup</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">② Check Models</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">③ Run Inference</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">④ Check Results</span></div>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>Click <strong>Run All</strong> on the Setup page to install dependencies → build → download sample assets all at once.</span></div>',
    '<h4>개요</h4><p>DX-APP을 처음 사용하는 분을 위한 빠른 시작 가이드입니다. 아래 단계를 순서대로 따라 하면 5분 이내에 첫 번째 NPU 추론을 실행할 수 있습니다.</p>'+
    '<div class="ref-flow"><span class="ref-flow-step">① Setup 실행</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">② 모델 확인</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">③ Run Inference</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">④ 결과 확인</span></div>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>Setup 페이지에서 <strong>Run All</strong>을 클릭하면 의존성 설치 → 빌드 → 샘플 에셋 다운로드를 한 번에 실행합니다.</span></div>',
    '<h4>概要</h4><p>DX-APPを初めてお使いになる方のためのクイックスタートガイドです。以下の手順に従えば、5分以内に最初のNPU推論を実行できます。</p>'+
    '<div class="ref-flow"><span class="ref-flow-step">① Setup 実行</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">② モデル確認</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">③ Run Inference</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">④ 結果確認</span></div>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>Setup ページで <strong>Run All</strong> をクリックすると、依存関係のインストール→ビルド→サンプルアセットのダウンロードを一括実行します。</span></div>',
    '<h4>概述</h4><p>面向首次使用 DX-APP 用户的快速入门指南。按照以下步骤操作，5分钟内即可运行首次 NPU 推理。</p>'+
    '<div class="ref-flow"><span class="ref-flow-step">① 运行 Setup</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">② 检查模型</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">③ Run Inference</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">④ 查看结果</span></div>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>在 Setup 页面点击 <strong>Run All</strong>，可一次性完成依赖安装→构建→示例资源下载。</span></div>',
    '<h4>概述</h4><p>專為首次使用 DX-APP 的使用者準備的快速入門指南。依照以下步驟操作，5分鐘內即可執行首次 NPU 推理。</p>'+
    '<div class="ref-flow"><span class="ref-flow-step">① 執行 Setup</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">② 確認模型</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">③ Run Inference</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">④ 查看結果</span></div>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>在 Setup 頁面點擊 <strong>Run All</strong>，可一次完成依賴安裝→建構→範例資源下載。</span></div>'),
  workflow:refT5('<h4>Detailed Workflow</h4>'+
    '<ol><li>Go to <strong>Setup page</strong> → Click <code>Run All</code> — DX-APP build, model/video download runs automatically.</li>'+
    '<li>Check deployed <code>.dxnn</code> models on the <strong>Models page</strong>.</li>'+
    '<li><strong>Run page</strong> → Single mode → Select model → Select image/video → <code>▶ Run</code></li>'+
    '<li>Bounding boxes/masks/classes are displayed on the result image.</li>'+
    '<li>Check the full run history on the <strong>Outputs page</strong>.</li></ol>'+
    '<div class="ref-box warn"><span class="ref-box-icon">⚠️</span><span>NPU inference is unavailable if the NPU driver (<code>dx_rt_npu_linux_driver</code>) is not installed. Check step ⑤ in Setup.</span></div>',
    '<h4>상세 워크플로우</h4>'+
    '<ol><li><strong>Setup 페이지</strong>로 이동 → <code>Run All</code> 클릭 — DX-APP 빌드, 모델/비디오 다운로드가 자동 실행됩니다.</li>'+
    '<li><strong>Models 페이지</strong>에서 배포된 <code>.dxnn</code> 모델을 확인합니다.</li>'+
    '<li><strong>Run 페이지</strong> → Single 모드 → 모델 선택 → 이미지/비디오 선택 → <code>▶ Run</code></li>'+
    '<li>결과 이미지에 바운딩 박스/마스크/클래스가 표시됩니다.</li>'+
    '<li><strong>Outputs 페이지</strong>에서 전체 실행 이력을 확인합니다.</li></ol>'+
    '<div class="ref-box warn"><span class="ref-box-icon">⚠️</span><span>NPU 드라이버(<code>dx_rt_npu_linux_driver</code>)가 설치되지 않으면 NPU 추론은 불가합니다. Setup에서 ⑤번을 확인하세요.</span></div>',
    '<h4>詳細ワークフロー</h4>'+
    '<ol><li><strong>Setup ページ</strong>に移動 → <code>Run All</code> をクリック — DX-APP ビルド、モデル/動画のダウンロードが自動実行されます。</li>'+
    '<li><strong>Models ページ</strong>でデプロイ済みの <code>.dxnn</code> モデルを確認します。</li>'+
    '<li><strong>Run ページ</strong> → Single モード → モデル選択 → 画像/動画選択 → <code>▶ Run</code></li>'+
    '<li>結果画像にバウンディングボックス/マスク/クラスが表示されます。</li>'+
    '<li><strong>Outputs ページ</strong>で実行履歴全体を確認します。</li></ol>'+
    '<div class="ref-box warn"><span class="ref-box-icon">⚠️</span><span>NPU ドライバー（<code>dx_rt_npu_linux_driver</code>）がインストールされていない場合、NPU 推論は利用できません。Setup の手順⑤を確認してください。</span></div>',
    '<h4>详细工作流</h4>'+
    '<ol><li>前往 <strong>Setup 页面</strong> → 点击 <code>Run All</code> — DX-APP 构建、模型/视频下载将自动执行。</li>'+
    '<li>在 <strong>Models 页面</strong>查看已部署的 <code>.dxnn</code> 模型。</li>'+
    '<li><strong>Run 页面</strong> → Single 模式 → 选择模型 → 选择图片/视频 → <code>▶ Run</code></li>'+
    '<li>结果图片上显示边界框/掩码/类别。</li>'+
    '<li>在 <strong>Outputs 页面</strong>查看完整运行历史。</li></ol>'+
    '<div class="ref-box warn"><span class="ref-box-icon">⚠️</span><span>若未安装 NPU 驱动程序（<code>dx_rt_npu_linux_driver</code>），则无法使用 NPU 推理。请检查 Setup 步骤⑤。</span></div>',
    '<h4>詳細工作流程</h4>'+
    '<ol><li>前往 <strong>Setup 頁面</strong> → 點擊 <code>Run All</code> — DX-APP 建構、模型/影片下載將自動執行。</li>'+
    '<li>在 <strong>Models 頁面</strong>查看已部署的 <code>.dxnn</code> 模型。</li>'+
    '<li><strong>Run 頁面</strong> → Single 模式 → 選擇模型 → 選擇圖片/影片 → <code>▶ Run</code></li>'+
    '<li>結果圖片上顯示邊界框/遮罩/類別。</li>'+
    '<li>在 <strong>Outputs 頁面</strong>查看完整執行歷史。</li></ol>'+
    '<div class="ref-box warn"><span class="ref-box-icon">⚠️</span><span>若未安裝 NPU 驅動程式（<code>dx_rt_npu_linux_driver</code>），則無法使用 NPU 推理。請檢查 Setup 步驟⑤。</span></div>'),
  tips:refT5('<h4>Useful Tips</h4>'+
    '<ul><li>Each step in Setup can be run individually — you can re-run only the failed step</li>'+
    '<li>If you have no models, download from <strong>ModelZoo</strong></li>'+
    '<li>Real-time inference with camera/RTSP is available in Continuous mode</li>'+
    '<li>Click the top-right <strong>🎓 Tutorial</strong> button to open the interactive guide for the current page</li></ul>',
    '<h4>유용한 팁</h4>'+
    '<ul><li>Setup의 각 단계는 개별 실행할 수 있습니다 — 실패한 단계만 재실행 가능</li>'+
    '<li>모델이 없다면 <strong>ModelZoo</strong>에서 다운로드하세요</li>'+
    '<li>Continuous 모드로 카메라/RTSP 실시간 추론도 가능합니다</li>'+
    '<li>우측 상단 <strong>🎓 튜토리얼</strong> 버튼으로 현재 페이지의 대화형 가이드를 열 수 있습니다</li></ul>',
    '<h4>便利なヒント</h4>'+
    '<ul><li>Setup の各ステップは個別に実行可能です — 失敗したステップだけを再実行できます</li>'+
    '<li>モデルがない場合は <strong>ModelZoo</strong> からダウンロードしてください</li>'+
    '<li>Continuous モードでカメラ/RTSP のリアルタイム推論も可能です</li>'+
    '<li>右上の <strong>🎓 チュートリアル</strong> ボタンで現在のページのガイドを開けます</li></ul>',
    '<h4>实用技巧</h4>'+
    '<ul><li>Setup 中的每个步骤都可以单独运行 — 仅重新运行失败的步骤即可</li>'+
    '<li>如果没有模型，请从 <strong>ModelZoo</strong> 下载</li>'+
    '<li>Continuous 模式下可使用摄像头/RTSP 进行实时推理</li>'+
    '<li>点击右上角的 <strong>🎓 教程</strong> 按钮可打开当前页面的交互式指南</li></ul>',
    '<h4>實用技巧</h4>'+
    '<ul><li>Setup 中的每個步驟都可以單獨執行 — 僅重新執行失敗的步驟即可</li>'+
    '<li>如果沒有模型，請從 <strong>ModelZoo</strong> 下載</li>'+
    '<li>Continuous 模式下可使用攝影機/RTSP 進行即時推理</li>'+
    '<li>點擊右上角的 <strong>🎓 教學</strong> 按鈕可開啟目前頁面的互動式指南</li></ul>',
    '<h4>Consejos útiles</h4>'+
    '<ul><li>Cada paso de Setup puede ejecutarse por separado: puede repetir solo el paso fallido</li>'+
    '<li>Si no tiene modelos, descárguelos desde <strong>ModelZoo</strong></li>'+
    '<li>La inferencia en tiempo real con cámara/RTSP está disponible en modo Continuous</li>'+
    '<li>Haga clic en el botón <strong>🎓 Tutorial</strong> arriba a la derecha para abrir la guía interactiva de la página actual</li></ul>')
}},

{cat:'start',id:'setup-install',icon:'⚙️',name:refT5('Setup & Install','환경 설정 & 설치','セットアップ＆インストール','环境设置与安装','環境設定與安裝'),desc:refT5('Install dependencies, build, download sample assets','의존성 설치, 빌드, 샘플 에셋 다운로드','依存関係のインストール、ビルド、サンプルアセットのダウンロード','安装依赖、构建、下载示例资源','安裝依賴、建構、下載範例資源'),page:'setup',tabs:{
  overview:refT5('<h4>Overview</h4><p>The Setup page configures the DX-APP runtime environment step by step. Five cards run sequentially or individually. ONNX→DXNN compilation moved to the Launcher <strong>Compiler</strong> module.</p>'+
    '<div class="ref-flow"><span class="ref-flow-step">① DX-APP Deps</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">② DX-APP Build</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">③ Sample Assets</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">④ DX-RT Deps</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">⑤ NPU Driver</span></div>',
    '<h4>개요</h4><p>Setup 페이지는 DX-APP 실행 환경을 단계별로 구성합니다. 5개 카드가 순차 또는 개별 실행됩니다. ONNX→DXNN 컴파일은 Launcher <strong>Compiler</strong> 모듈에서 수행합니다.</p>'+
    '<div class="ref-flow"><span class="ref-flow-step">① DX-APP Deps</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">② DX-APP Build</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">③ Sample Assets</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">④ DX-RT Deps</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">⑤ NPU Driver</span></div>',
    '<h4>概要</h4><p>Setup ページは DX-APP の実行環境をステップごとに構成します。5つのカードを順次または個別に実行できます。ONNX→DXNN コンパイルは Launcher の <strong>Compiler</strong> モジュールで行います。</p>'+
    '<div class="ref-flow"><span class="ref-flow-step">① DX-APP Deps</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">② DX-APP Build</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">③ Sample Assets</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">④ DX-RT Deps</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">⑤ NPU Driver</span></div>',
    '<h4>概述</h4><p>Setup 页面逐步配置 DX-APP 运行环境。5张卡片可按顺序或单独执行。ONNX→DXNN 编译已移至 Launcher <strong>Compiler</strong> 模块。</p>'+
    '<div class="ref-flow"><span class="ref-flow-step">① DX-APP Deps</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">② DX-APP Build</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">③ Sample Assets</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">④ DX-RT Deps</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">⑤ NPU Driver</span></div>',
    '<h4>概述</h4><p>Setup 頁面逐步配置 DX-APP 執行環境。5張卡片可依序或單獨執行。ONNX→DXNN 編譯已移至 Launcher <strong>Compiler</strong> 模組。</p>'+
    '<div class="ref-flow"><span class="ref-flow-step">① DX-APP Deps</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">② DX-APP Build</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">③ Sample Assets</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">④ DX-RT Deps</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">⑤ NPU Driver</span></div>'),
  params:refT5('<h4>Step Details</h4>'+
    '<table class="ref-tbl"><tr><th>Step</th><th>Description</th><th>sudo</th><th>Notes</th></tr>'+
    '<tr><td><strong>① DX-APP Dependencies</strong></td><td>Install build tools: cmake, gcc, ninja, OpenCV, etc.</td><td>✅</td><td>apt-based</td></tr>'+
    '<tr><td><strong>② DX-APP Build</strong></td><td>C++ Release build (CMake + Ninja)</td><td>—</td><td>~2 min</td></tr>'+
    '<tr><td><strong>③ Sample Assets</strong></td><td>Download models (.dxnn) + demo videos</td><td>—</td><td>~500MB</td></tr>'+
    '<tr><td><strong>④ DX-Runtime Deps</strong></td><td>Runtime library dependencies</td><td>✅</td><td></td></tr>'+
    '<tr><td><strong>⑤ NPU Driver</strong></td><td>DKMS kernel module installation</td><td>✅</td><td>Reboot recommended</td></tr></table>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>DX-COM ONNX→DXNN compilation is in the Launcher <strong>Compiler</strong> module (not on this Setup page).</span></div>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>Use the <strong>Run All</strong> button to run all steps at once. Already completed steps are shown with <span style="color:#3fb950">✅</span>.</span></div>',
    '<h4>단계별 상세</h4>'+
    '<table class="ref-tbl"><tr><th>단계</th><th>설명</th><th>sudo</th><th>비고</th></tr>'+
    '<tr><td><strong>① DX-APP Dependencies</strong></td><td>cmake, gcc, ninja, OpenCV 등 빌드 도구 설치</td><td>✅</td><td>apt 기반</td></tr>'+
    '<tr><td><strong>② DX-APP Build</strong></td><td>C++ Release 빌드 (CMake + Ninja)</td><td>—</td><td>~2분</td></tr>'+
    '<tr><td><strong>③ Sample Assets</strong></td><td>모델(.dxnn) + 데모 비디오 다운로드</td><td>—</td><td>~500MB</td></tr>'+
    '<tr><td><strong>④ DX-Runtime Deps</strong></td><td>런타임 라이브러리 의존성</td><td>✅</td><td></td></tr>'+
    '<tr><td><strong>⑤ NPU Driver</strong></td><td>DKMS 커널 모듈 설치</td><td>✅</td><td>재부팅 권장</td></tr></table>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>DX-COM ONNX→DXNN 컴파일은 Launcher <strong>Compiler</strong> 모듈에서 수행합니다 (Setup 페이지 아님).</span></div>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span><strong>Run All</strong> 버튼으로 전체 단계를 한 번에 실행할 수 있습니다. 이미 완료된 단계는 <span style="color:#3fb950">✅</span> 상태로 표시됩니다.</span></div>',
    '<h4>ステップ詳細</h4>'+
    '<table class="ref-tbl"><tr><th>ステップ</th><th>説明</th><th>sudo</th><th>備考</th></tr>'+
    '<tr><td><strong>① DX-APP Dependencies</strong></td><td>cmake, gcc, ninja, OpenCV などビルドツールのインストール</td><td>✅</td><td>apt ベース</td></tr>'+
    '<tr><td><strong>② DX-APP Build</strong></td><td>C++ Release ビルド (CMake + Ninja)</td><td>—</td><td>約2分</td></tr>'+
    '<tr><td><strong>③ Sample Assets</strong></td><td>モデル (.dxnn) + デモ動画のダウンロード</td><td>—</td><td>約500MB</td></tr>'+
    '<tr><td><strong>④ DX-Runtime Deps</strong></td><td>ランタイムライブラリの依存関係</td><td>✅</td><td></td></tr>'+
    '<tr><td><strong>⑤ NPU Driver</strong></td><td>DKMS カーネルモジュールのインストール</td><td>✅</td><td>再起動推奨</td></tr></table>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>DX-COM ONNX→DXNN コンパイルは Launcher の <strong>Compiler</strong> モジュールで行います (Setup ページではありません)。</span></div>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span><strong>Run All</strong> ボタンで全ステップを一括実行できます。完了済みのステップは <span style="color:#3fb950">✅</span> で表示されます。</span></div>',
    '<h4>步骤详情</h4>'+
    '<table class="ref-tbl"><tr><th>步骤</th><th>说明</th><th>sudo</th><th>备注</th></tr>'+
    '<tr><td><strong>① DX-APP Dependencies</strong></td><td>安装构建工具：cmake、gcc、ninja、OpenCV 等</td><td>✅</td><td>基于 apt</td></tr>'+
    '<tr><td><strong>② DX-APP Build</strong></td><td>C++ Release 构建 (CMake + Ninja)</td><td>—</td><td>约2分钟</td></tr>'+
    '<tr><td><strong>③ Sample Assets</strong></td><td>下载模型 (.dxnn) + 演示视频</td><td>—</td><td>约500MB</td></tr>'+
    '<tr><td><strong>④ DX-Runtime Deps</strong></td><td>运行时库依赖</td><td>✅</td><td></td></tr>'+
    '<tr><td><strong>⑤ NPU Driver</strong></td><td>DKMS 内核模块安装</td><td>✅</td><td>建议重启</td></tr></table>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>DX-COM ONNX→DXNN 编译在 Launcher <strong>Compiler</strong> 模块中进行（不在 Setup 页面）。</span></div>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>使用 <strong>Run All</strong> 按钮可一次性运行所有步骤。已完成的步骤显示为 <span style="color:#3fb950">✅</span>。</span></div>',
    '<h4>步驟詳情</h4>'+
    '<table class="ref-tbl"><tr><th>步驟</th><th>說明</th><th>sudo</th><th>備註</th></tr>'+
    '<tr><td><strong>① DX-APP Dependencies</strong></td><td>安裝建構工具：cmake、gcc、ninja、OpenCV 等</td><td>✅</td><td>基於 apt</td></tr>'+
    '<tr><td><strong>② DX-APP Build</strong></td><td>C++ Release 建構 (CMake + Ninja)</td><td>—</td><td>約2分鐘</td></tr>'+
    '<tr><td><strong>③ Sample Assets</strong></td><td>下載模型 (.dxnn) + 演示影片</td><td>—</td><td>約500MB</td></tr>'+
    '<tr><td><strong>④ DX-Runtime Deps</strong></td><td>執行時期程式庫依賴</td><td>✅</td><td></td></tr>'+
    '<tr><td><strong>⑤ NPU Driver</strong></td><td>DKMS 核心模組安裝</td><td>✅</td><td>建議重新啟動</td></tr></table>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>DX-COM ONNX→DXNN 編譯在 Launcher <strong>Compiler</strong> 模組中進行（不在 Setup 頁面）。</span></div>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>使用 <strong>Run All</strong> 按鈕可一次執行所有步驟。已完成的步驟顯示為 <span style="color:#3fb950">✅</span>。</span></div>'),
  tips:refT5('<h4>Troubleshooting</h4>'+
    '<ul><li><strong>Build failure</strong> — Try a clean build with <code>build.sh --clean</code></li>'+
    '<li><strong>NPU driver load failure</strong> — Check driver load with <code>lsmod | grep dxnpu</code>, then check errors with <code>dmesg</code></li>'+
    '<li>For <strong>air-gapped networks</strong>, prepare offline packages in advance</li></ul>',
    '<h4>트러블슈팅</h4>'+
    '<ul><li><strong>빌드 실패</strong> — <code>build.sh --clean</code>으로 클린 빌드를 시도하세요</li>'+
    '<li><strong>NPU 드라이버 로드 실패</strong> — <code>lsmod | grep dxnpu</code>로 드라이버 로드 확인 후, <code>dmesg</code>로 에러를 확인하세요</li>'+
    '<li><strong>폐쇄망</strong>에서는 오프라인 패키지를 미리 준비하세요</li></ul>',
    '<h4>トラブルシューティング</h4>'+
    '<ul><li><strong>ビルド失敗</strong> — <code>build.sh --clean</code> でクリーンビルドを試してください</li>'+
    '<li><strong>NPU ドライバーのロード失敗</strong> — <code>lsmod | grep dxnpu</code> でドライバーのロードを確認後、<code>dmesg</code> でエラーを確認してください</li>'+
    '<li><strong>オフライン環境</strong>ではオフラインパッケージを事前に準備してください</li></ul>',
    '<h4>故障排除</h4>'+
    '<ul><li><strong>构建失败</strong> — 使用 <code>build.sh --clean</code> 尝试清理构建</li>'+
    '<li><strong>NPU 驱动加载失败</strong> — 使用 <code>lsmod | grep dxnpu</code> 检查驱动加载，然后用 <code>dmesg</code> 查看错误</li>'+
    '<li>在<strong>离线网络</strong>中请提前准备离线包</li></ul>',
    '<h4>故障排除</h4>'+
    '<ul><li><strong>建構失敗</strong> — 使用 <code>build.sh --clean</code> 嘗試清理建構</li>'+
    '<li><strong>NPU 驅動載入失敗</strong> — 使用 <code>lsmod | grep dxnpu</code> 確認驅動載入，再用 <code>dmesg</code> 查看錯誤</li>'+
    '<li>在<strong>離線網路</strong>中請事先準備離線套件</li></ul>')
}},

{cat:'start',id:'deep-diagnostics',icon:'🔍',name:'Deep Diagnostics',desc:refT5('Comprehensive system health check','시스템 종합 진단','システム総合診断','系统综合诊断','系統綜合診斷'),page:'setup',tabs:{
  overview:refT5('<h4>Overview</h4><p>Deep Diagnostics runs 12 automated checks covering hardware, drivers, software, and resources. Results appear as pass/fail cards with fix suggestions.</p>'+
    '<div class="ref-flow"><span class="ref-flow-step">▶ Run Diagnostics</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">12 Checks</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">Pass/Fail Cards</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">Fix Suggestions</span></div>',
    '<h4>개요</h4><p>Deep Diagnostics는 하드웨어, 드라이버, 소프트웨어, 리소스를 포함한 12개 자동 검사를 실행합니다. 결과는 통과/실패 카드와 수정 제안으로 표시됩니다.</p>'+
    '<div class="ref-flow"><span class="ref-flow-step">▶ 진단 실행</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">12개 검사</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">통과/실패 카드</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">수정 제안</span></div>',
    '<h4>概要</h4><p>Deep Diagnostics はハードウェア、ドライバー、ソフトウェア、リソースを含む12項目の自動チェックを実行します。結果は合格/不合格カードと修正提案で表示されます。</p>'+
    '<div class="ref-flow"><span class="ref-flow-step">▶ 診断実行</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">12項目チェック</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">合格/不合格カード</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">修正提案</span></div>',
    '<h4>概述</h4><p>Deep Diagnostics 运行涵盖硬件、驱动、软件和资源的12项自动检查。结果以通过/失败卡片和修复建议的形式显示。</p>'+
    '<div class="ref-flow"><span class="ref-flow-step">▶ 运行诊断</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">12项检查</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">通过/失败卡片</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">修复建议</span></div>',
    '<h4>概述</h4><p>Deep Diagnostics 執行涵蓋硬體、驅動、軟體和資源的12項自動檢查。結果以通過/失敗卡片和修復建議的形式顯示。</p>'+
    '<div class="ref-flow"><span class="ref-flow-step">▶ 執行診斷</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">12項檢查</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">通過/失敗卡片</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">修復建議</span></div>'),
  params:refT5('<h4>Check Items (12)</h4>'+
    '<table class="ref-tbl"><tr><th>#</th><th>Check</th><th>Description</th></tr>'+
    '<tr><td>1</td><td>PCIe Link</td><td>DeepX NPU detected on PCIe bus (Vendor ID 1ff4)</td></tr>'+
    '<tr><td>2</td><td>Device Files</td><td>/dev/dxrt* or /dev/deepx* present</td></tr>'+
    '<tr><td>3</td><td>Kernel Module (dxrt_driver)</td><td>NPU kernel driver loaded</td></tr>'+
    '<tr><td>4</td><td>Kernel Module (dx_dma)</td><td>DMA module loaded</td></tr>'+
    '<tr><td>5</td><td>DKMS Status</td><td>Driver registered in DKMS</td></tr>'+
    '<tr><td>6</td><td>dxrt.service</td><td>systemd service active</td></tr>'+
    '<tr><td>7</td><td>CLI Tools</td><td>dxrt-cli, run_model, parse_model, dxtop available</td></tr>'+
    '<tr><td>8</td><td>Python venv</td><td>dx_engine importable in venv-dx-runtime</td></tr>'+
    '<tr><td>9</td><td>Disk Space</td><td>≥5GB free</td></tr>'+
    '<tr><td>10</td><td>Memory</td><td>≥2GB available</td></tr>'+
    '<tr><td>11</td><td>Model Integrity</td><td>No zero-byte .dxnn files in assets/models/</td></tr>'+
    '<tr><td>12</td><td>OpenCV</td><td>cv2 importable</td></tr></table>',
    '<h4>검사 항목 (12개)</h4>'+
    '<table class="ref-tbl"><tr><th>#</th><th>검사</th><th>설명</th></tr>'+
    '<tr><td>1</td><td>PCIe Link</td><td>PCIe 버스에서 DeepX NPU 감지 (Vendor ID 1ff4)</td></tr>'+
    '<tr><td>2</td><td>Device Files</td><td>/dev/dxrt* 또는 /dev/deepx* 존재 여부</td></tr>'+
    '<tr><td>3</td><td>Kernel Module (dxrt_driver)</td><td>NPU 커널 드라이버 로드됨</td></tr>'+
    '<tr><td>4</td><td>Kernel Module (dx_dma)</td><td>DMA 모듈 로드됨</td></tr>'+
    '<tr><td>5</td><td>DKMS Status</td><td>드라이버 DKMS 등록 상태</td></tr>'+
    '<tr><td>6</td><td>dxrt.service</td><td>systemd 서비스 활성화 여부</td></tr>'+
    '<tr><td>7</td><td>CLI Tools</td><td>dxrt-cli, run_model, parse_model, dxtop 사용 가능</td></tr>'+
    '<tr><td>8</td><td>Python venv</td><td>venv-dx-runtime에서 dx_engine import 가능</td></tr>'+
    '<tr><td>9</td><td>Disk Space</td><td>5GB 이상 여유 공간</td></tr>'+
    '<tr><td>10</td><td>Memory</td><td>2GB 이상 가용 메모리</td></tr>'+
    '<tr><td>11</td><td>Model Integrity</td><td>assets/models/ 내 0바이트 .dxnn 파일 없음</td></tr>'+
    '<tr><td>12</td><td>OpenCV</td><td>cv2 임포트 가능</td></tr></table>',
    '<h4>チェック項目（12項目）</h4>'+
    '<table class="ref-tbl"><tr><th>#</th><th>チェック</th><th>説明</th></tr>'+
    '<tr><td>1</td><td>PCIe Link</td><td>PCIe バスで DeepX NPU を検出（Vendor ID 1ff4）</td></tr>'+
    '<tr><td>2</td><td>Device Files</td><td>/dev/dxrt* または /dev/deepx* の存在</td></tr>'+
    '<tr><td>3</td><td>Kernel Module (dxrt_driver)</td><td>NPU カーネルドライバーがロード済み</td></tr>'+
    '<tr><td>4</td><td>Kernel Module (dx_dma)</td><td>DMA モジュールがロード済み</td></tr>'+
    '<tr><td>5</td><td>DKMS Status</td><td>ドライバーが DKMS に登録済み</td></tr>'+
    '<tr><td>6</td><td>dxrt.service</td><td>systemd サービスが有効</td></tr>'+
    '<tr><td>7</td><td>CLI Tools</td><td>dxrt-cli, run_model, parse_model, dxtop が利用可能</td></tr>'+
    '<tr><td>8</td><td>Python venv</td><td>venv-dx-runtime で dx_engine がインポート可能</td></tr>'+
    '<tr><td>9</td><td>Disk Space</td><td>5GB 以上の空き容量</td></tr>'+
    '<tr><td>10</td><td>Memory</td><td>2GB 以上の利用可能メモリ</td></tr>'+
    '<tr><td>11</td><td>Model Integrity</td><td>assets/models/ 内に0バイトの .dxnn ファイルなし</td></tr>'+
    '<tr><td>12</td><td>OpenCV</td><td>cv2 がインポート可能</td></tr></table>',
    '<h4>检查项目（12项）</h4>'+
    '<table class="ref-tbl"><tr><th>#</th><th>检查</th><th>说明</th></tr>'+
    '<tr><td>1</td><td>PCIe Link</td><td>在 PCIe 总线上检测到 DeepX NPU（Vendor ID 1ff4）</td></tr>'+
    '<tr><td>2</td><td>Device Files</td><td>/dev/dxrt* 或 /dev/deepx* 是否存在</td></tr>'+
    '<tr><td>3</td><td>Kernel Module (dxrt_driver)</td><td>NPU 内核驱动已加载</td></tr>'+
    '<tr><td>4</td><td>Kernel Module (dx_dma)</td><td>DMA 模块已加载</td></tr>'+
    '<tr><td>5</td><td>DKMS Status</td><td>驱动已在 DKMS 中注册</td></tr>'+
    '<tr><td>6</td><td>dxrt.service</td><td>systemd 服务已激活</td></tr>'+
    '<tr><td>7</td><td>CLI Tools</td><td>dxrt-cli、run_model、parse_model、dxtop 可用</td></tr>'+
    '<tr><td>8</td><td>Python venv</td><td>在 venv-dx-runtime 中可导入 dx_engine</td></tr>'+
    '<tr><td>9</td><td>Disk Space</td><td>≥5GB 可用空间</td></tr>'+
    '<tr><td>10</td><td>Memory</td><td>≥2GB 可用内存</td></tr>'+
    '<tr><td>11</td><td>Model Integrity</td><td>assets/models/ 内无0字节 .dxnn 文件</td></tr>'+
    '<tr><td>12</td><td>OpenCV</td><td>cv2 可导入</td></tr></table>',
    '<h4>檢查項目（12項）</h4>'+
    '<table class="ref-tbl"><tr><th>#</th><th>檢查</th><th>說明</th></tr>'+
    '<tr><td>1</td><td>PCIe Link</td><td>在 PCIe 匯流排上偵測到 DeepX NPU（Vendor ID 1ff4）</td></tr>'+
    '<tr><td>2</td><td>Device Files</td><td>/dev/dxrt* 或 /dev/deepx* 是否存在</td></tr>'+
    '<tr><td>3</td><td>Kernel Module (dxrt_driver)</td><td>NPU 核心驅動已載入</td></tr>'+
    '<tr><td>4</td><td>Kernel Module (dx_dma)</td><td>DMA 模組已載入</td></tr>'+
    '<tr><td>5</td><td>DKMS Status</td><td>驅動已在 DKMS 中註冊</td></tr>'+
    '<tr><td>6</td><td>dxrt.service</td><td>systemd 服務已啟用</td></tr>'+
    '<tr><td>7</td><td>CLI Tools</td><td>dxrt-cli、run_model、parse_model、dxtop 可用</td></tr>'+
    '<tr><td>8</td><td>Python venv</td><td>在 venv-dx-runtime 中可匯入 dx_engine</td></tr>'+
    '<tr><td>9</td><td>Disk Space</td><td>≥5GB 可用空間</td></tr>'+
    '<tr><td>10</td><td>Memory</td><td>≥2GB 可用記憶體</td></tr>'+
    '<tr><td>11</td><td>Model Integrity</td><td>assets/models/ 內無0位元組 .dxnn 檔案</td></tr>'+
    '<tr><td>12</td><td>OpenCV</td><td>cv2 可匯入</td></tr></table>'),
  tips:refT5('<h4>Tips</h4>'+
    '<ul><li>Run diagnostics <strong>after</strong> completing all Setup steps for best results</li>'+
    '<li>Failed items show a 💡 fix suggestion — follow the recommended command</li>'+
    '<li>All checks are Python-native (no shell dependency) and run in under 10 seconds</li></ul>',
    '<h4>팁</h4>'+
    '<ul><li>최적의 결과를 위해 Setup 단계를 모두 완료한 <strong>후</strong> 진단을 실행하세요</li>'+
    '<li>실패한 항목에는 💡 수정 제안이 표시됩니다 — 권장 명령어를 따라하세요</li>'+
    '<li>모든 검사는 Python 네이티브(쉘 의존 없음)이며 10초 이내에 완료됩니다</li></ul>',
    '<h4>ヒント</h4>'+
    '<ul><li>最良の結果を得るために、Setup の全ステップ完了<strong>後</strong>に診断を実行してください</li>'+
    '<li>失敗した項目には💡修正提案が表示されます — 推奨コマンドに従ってください</li>'+
    '<li>すべてのチェックは Python ネイティブ（シェル依存なし）で、10秒以内に完了します</li></ul>',
    '<h4>提示</h4>'+
    '<ul><li>为获得最佳结果，请在完成所有 Setup 步骤<strong>之后</strong>运行诊断</li>'+
    '<li>失败的项目会显示💡修复建议 — 请按照推荐命令操作</li>'+
    '<li>所有检查均为 Python 原生（无 shell 依赖），10秒内完成</li></ul>',
    '<h4>提示</h4>'+
    '<ul><li>為獲得最佳結果，請在完成所有 Setup 步驟<strong>之後</strong>執行診斷</li>'+
    '<li>失敗的項目會顯示💡修復建議 — 請依照建議命令操作</li>'+
    '<li>所有檢查均為 Python 原生（無 shell 依賴），10秒內完成</li></ul>')
}},

/* ── Core Features ── */
{cat:'core',id:'models',icon:'🗂️',name:'Models',desc:refT5('Deployed model list · Details · Graph visualization','배포 모델 목록 · 상세 정보 · 그래프 시각화','デプロイ済みモデル一覧・詳細・グラフ可視化','已部署模型列表·详情·图形可视化','已部署模型列表·詳情·圖形視覺化'),page:'models',tabs:{
  overview:refT5('<h4>Overview</h4><p>The Models page displays deployed <code>.dxnn</code> models on the current system as cards.</p>'+
    '<ul><li><strong>Model Card</strong> — Name, task, Input/Output tensors, model size</li>'+
    '<li><strong>Detail Panel</strong> — Tensor shape, data type, operator info</li>'+
    '<li><strong>📊 Graph</strong> — Opens the model graph in the dx-compiler viewer (ONNX models)</li>'+
    '<li><strong>Search & Filter</strong> — Name search, filter by task type</li></ul>',
    '<h4>개요</h4><p>Models 페이지는 현재 시스템에 배포된 <code>.dxnn</code> 모델 목록을 카드 형태로 표시합니다.</p>'+
    '<ul><li><strong>모델 카드</strong> — 이름, 태스크, Input/Output 텐서, 모델 사이즈</li>'+
    '<li><strong>상세 패널</strong> — 텐서 Shape, 데이터 타입, Operator 정보</li>'+
    '<li><strong>📊 Graph</strong> — dx-compiler 뷰어에서 모델 그래프 보기 (ONNX 모델)</li>'+
    '<li><strong>검색 & 필터</strong> — 이름 검색, 태스크별 필터링</li></ul>',
    '<h4>概要</h4><p>Models ページは現在のシステムにデプロイされた <code>.dxnn</code> モデルをカード形式で表示します。</p>'+
    '<ul><li><strong>モデルカード</strong> — 名前、タスク、入出力テンソル、モデルサイズ</li>'+
    '<li><strong>詳細パネル</strong> — テンソル Shape、データ型、Operator 情報</li>'+
    '<li><strong>📊 Graph</strong> — dx-compiler ビューアでモデルグラフを表示（ONNX モデル）</li>'+
    '<li><strong>検索 & フィルター</strong> — 名前検索、タスク別フィルタリング</li></ul>',
    '<h4>概述</h4><p>Models 页面以卡片形式显示当前系统中已部署的 <code>.dxnn</code> 模型列表。</p>'+
    '<ul><li><strong>模型卡片</strong> — 名称、任务、输入/输出张量、模型大小</li>'+
    '<li><strong>详情面板</strong> — 张量 Shape、数据类型、Operator 信息</li>'+
    '<li><strong>📊 Graph</strong> — 在 dx-compiler 查看器中打开模型图形（ONNX 模型）</li>'+
    '<li><strong>搜索与筛选</strong> — 名称搜索、按任务类型筛选</li></ul>',
    '<h4>概述</h4><p>Models 頁面以卡片形式顯示當前系統中已部署的 <code>.dxnn</code> 模型列表。</p>'+
    '<ul><li><strong>模型卡片</strong> — 名稱、任務、輸入/輸出張量、模型大小</li>'+
    '<li><strong>詳情面板</strong> — 張量 Shape、資料型別、Operator 資訊</li>'+
    '<li><strong>📊 Graph</strong> — 在 dx-compiler 檢視器中開啟模型圖形（ONNX 模型）</li>'+
    '<li><strong>搜尋與篩選</strong> — 名稱搜尋、依任務類型篩選</li></ul>'),
  params:refT5('<h4>Supported Task Types</h4>'+
    '<table class="ref-tbl"><tr><th>Task</th><th>Description</th><th>Output Format</th></tr>'+
    '<tr><td>Classification</td><td>Image classification</td><td>Top-K classes + probabilities</td></tr>'+
    '<tr><td>Detection</td><td>Object detection</td><td>BBox + class + conf</td></tr>'+
    '<tr><td>Segmentation</td><td>Semantic segmentation</td><td>Pixel mask</td></tr>'+
    '<tr><td>Pose Estimation</td><td>Pose estimation</td><td>Keypoint coordinates</td></tr>'+
    '<tr><td>Super Resolution</td><td>Super resolution</td><td>High-resolution image</td></tr>'+
    '<tr><td>Denoising</td><td>Noise removal</td><td>Clean image</td></tr>'+
    '<tr><td>Depth Estimation</td><td>Depth estimation</td><td>Depth Map</td></tr></table>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>The Graph button opens the model graph in the dx-compiler viewer in a new tab (ONNX models).</span></div>',
    '<h4>지원 태스크 유형</h4>'+
    '<table class="ref-tbl"><tr><th>태스크</th><th>설명</th><th>Output 형식</th></tr>'+
    '<tr><td>Classification</td><td>이미지 분류</td><td>Top-K 클래스 + 확률</td></tr>'+
    '<tr><td>Detection</td><td>객체 검출</td><td>BBox + 클래스 + conf</td></tr>'+
    '<tr><td>Segmentation</td><td>의미 분할</td><td>픽셀 마스크</td></tr>'+
    '<tr><td>Pose Estimation</td><td>자세 추정</td><td>Keypoint 좌표</td></tr>'+
    '<tr><td>Super Resolution</td><td>초해상도</td><td>고해상도 이미지</td></tr>'+
    '<tr><td>Denoising</td><td>노이즈 제거</td><td>클린 이미지</td></tr>'+
    '<tr><td>Depth Estimation</td><td>깊이 추정</td><td>Depth Map</td></tr></table>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>Graph 버튼을 클릭하면 새 탭의 dx-compiler 뷰어에서 모델 그래프가 열립니다 (ONNX 모델).</span></div>',
    '<h4>サポートタスクタイプ</h4>'+
    '<table class="ref-tbl"><tr><th>タスク</th><th>説明</th><th>出力形式</th></tr>'+
    '<tr><td>Classification</td><td>画像分類</td><td>Top-K クラス + 確率</td></tr>'+
    '<tr><td>Detection</td><td>オブジェクト検出</td><td>BBox + クラス + conf</td></tr>'+
    '<tr><td>Segmentation</td><td>セマンティックセグメンテーション</td><td>ピクセルマスク</td></tr>'+
    '<tr><td>Pose Estimation</td><td>姿勢推定</td><td>キーポイント座標</td></tr>'+
    '<tr><td>Super Resolution</td><td>超解像</td><td>高解像度画像</td></tr>'+
    '<tr><td>Denoising</td><td>ノイズ除去</td><td>クリーン画像</td></tr>'+
    '<tr><td>Depth Estimation</td><td>深度推定</td><td>Depth Map</td></tr></table>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>Graph ボタンをクリックすると、新しいタブの dx-compiler ビューアにモデルグラフが開きます（ONNX モデル）。</span></div>',
    '<h4>支持的任务类型</h4>'+
    '<table class="ref-tbl"><tr><th>任务</th><th>说明</th><th>输出格式</th></tr>'+
    '<tr><td>Classification</td><td>图像分类</td><td>Top-K 类别 + 概率</td></tr>'+
    '<tr><td>Detection</td><td>目标检测</td><td>BBox + 类别 + conf</td></tr>'+
    '<tr><td>Segmentation</td><td>语义分割</td><td>像素掩码</td></tr>'+
    '<tr><td>Pose Estimation</td><td>姿态估计</td><td>关键点坐标</td></tr>'+
    '<tr><td>Super Resolution</td><td>超分辨率</td><td>高分辨率图像</td></tr>'+
    '<tr><td>Denoising</td><td>降噪</td><td>干净图像</td></tr>'+
    '<tr><td>Depth Estimation</td><td>深度估计</td><td>Depth Map</td></tr></table>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>点击 Graph 按钮可在新标签页的 dx-compiler 查看器中打开模型图形（ONNX 模型）。</span></div>',
    '<h4>支援的任務類型</h4>'+
    '<table class="ref-tbl"><tr><th>任務</th><th>說明</th><th>輸出格式</th></tr>'+
    '<tr><td>Classification</td><td>影像分類</td><td>Top-K 類別 + 機率</td></tr>'+
    '<tr><td>Detection</td><td>物件偵測</td><td>BBox + 類別 + conf</td></tr>'+
    '<tr><td>Segmentation</td><td>語義分割</td><td>像素遮罩</td></tr>'+
    '<tr><td>Pose Estimation</td><td>姿態估計</td><td>關鍵點座標</td></tr>'+
    '<tr><td>Super Resolution</td><td>超解析度</td><td>高解析度影像</td></tr>'+
    '<tr><td>Denoising</td><td>降噪</td><td>乾淨影像</td></tr>'+
    '<tr><td>Depth Estimation</td><td>深度估計</td><td>Depth Map</td></tr></table>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>點擊 Graph 按鈕可在新分頁的 dx-compiler 檢視器中開啟模型圖形（ONNX 模型）。</span></div>'),
  tips:refT5('<h4>Tips</h4>'+
    '<ul><li>Click a model card to open the detail panel with animation</li>'+
    '<li>Task filter buttons are highlighted with <strong>accent color</strong> when active</li>'+
    '<li>If you have no models, download from the <strong>ModelZoo</strong> page</li></ul>',
    '<h4>팁</h4>'+
    '<ul><li>모델 카드를 클릭하면 상세 패널이 애니메이션과 함께 열립니다</li>'+
    '<li>태스크 필터 버튼은 활성 필터가 있을 때 <strong>accent 색상</strong>으로 강조됩니다</li>'+
    '<li>모델이 없다면 <strong>ModelZoo</strong> 페이지에서 다운로드하세요</li></ul>',
    '<h4>ヒント</h4>'+
    '<ul><li>モデルカードをクリックすると、アニメーション付きで詳細パネルが開きます</li>'+
    '<li>タスクフィルターボタンはアクティブ時に<strong>アクセントカラー</strong>で強調されます</li>'+
    '<li>モデルがない場合は <strong>ModelZoo</strong> ページからダウンロードしてください</li></ul>',
    '<h4>提示</h4>'+
    '<ul><li>点击模型卡片可打开带有动画效果的详情面板</li>'+
    '<li>任务筛选按钮在激活时以<strong>强调色</strong>高亮显示</li>'+
    '<li>如果没有模型，请从 <strong>ModelZoo</strong> 页面下载</li></ul>',
    '<h4>提示</h4>'+
    '<ul><li>點擊模型卡片可開啟帶有動畫效果的詳情面板</li>'+
    '<li>任務篩選按鈕在啟用時以<strong>強調色</strong>醒目顯示</li>'+
    '<li>如果沒有模型，請從 <strong>ModelZoo</strong> 頁面下載</li></ul>')
}},

{cat:'core',id:'run-inference',icon:'▶️',name:'Run Inference',desc:refT5('Single · Continuous inference · Parameter settings','Single · Continuous 추론 실행 · 파라미터 설정','Single・Continuous 推論実行・パラメータ設定','Single·Continuous 推理执行·参数设置','Single·Continuous 推理執行·參數設定'),page:'run',tabs:{
  overview:refT5('<h4>Overview</h4><p>The Run page is the core interface for NPU inference. Two modes are supported:</p>'+
    '<ul><li><strong>Single mode</strong> — Select a single image or video for one-shot inference</li>'+
    '<li><strong>Continuous mode</strong> — Continuous real-time inference with video/camera/RTSP sources (up to 8 slots simultaneously)</li></ul>'+
    '<div class="ref-flow"><span class="ref-flow-step">Select Model</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">Select Input</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">Set Parameters</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">▶ Run</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">Check Results</span></div>',
    '<h4>개요</h4><p>Run 페이지는 NPU 추론의 핵심 실행 인터페이스입니다. 두 가지 모드를 지원합니다:</p>'+
    '<ul><li><strong>Single 모드</strong> — 이미지 또는 비디오 1개를 선택하여 단일 추론 실행</li>'+
    '<li><strong>Continuous 모드</strong> — 비디오/카메라/RTSP 소스로 연속 실시간 추론 (최대 8 슬롯 동시)</li></ul>'+
    '<div class="ref-flow"><span class="ref-flow-step">모델 선택</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">입력 선택</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">파라미터 설정</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">▶ Run</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">결과 확인</span></div>',
    '<h4>概要</h4><p>Run ページは NPU 推論のコア実行インターフェースです。2つのモードをサポートしています：</p>'+
    '<ul><li><strong>Single モード</strong> — 画像または動画1つを選択して単発推論を実行</li>'+
    '<li><strong>Continuous モード</strong> — 動画/カメラ/RTSP ソースで連続リアルタイム推論（最大8スロット同時）</li></ul>'+
    '<div class="ref-flow"><span class="ref-flow-step">モデル選択</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">入力選択</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">パラメータ設定</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">▶ Run</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">結果確認</span></div>',
    '<h4>概述</h4><p>Run 页面是 NPU 推理的核心执行界面。支持两种模式：</p>'+
    '<ul><li><strong>Single 模式</strong> — 选择单个图片或视频进行单次推理</li>'+
    '<li><strong>Continuous 模式</strong> — 通过视频/摄像头/RTSP 源进行连续实时推理（最多8个槽位同时运行）</li></ul>'+
    '<div class="ref-flow"><span class="ref-flow-step">选择模型</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">选择输入</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">设置参数</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">▶ Run</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">查看结果</span></div>',
    '<h4>概述</h4><p>Run 頁面是 NPU 推理的核心執行介面。支援兩種模式：</p>'+
    '<ul><li><strong>Single 模式</strong> — 選擇單個圖片或影片進行單次推理</li>'+
    '<li><strong>Continuous 模式</strong> — 透過影片/攝影機/RTSP 來源進行連續即時推理（最多8個插槽同時運行）</li></ul>'+
    '<div class="ref-flow"><span class="ref-flow-step">選擇模型</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">選擇輸入</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">設定參數</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">▶ Run</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">查看結果</span></div>'),
  params:refT5('<h4>Inference Parameters</h4>'+
    '<table class="ref-tbl"><tr><th>Parameter</th><th>Range</th><th>Default</th><th>Description</th></tr>'+
    '<tr><td>Confidence Threshold</td><td>0.0 – 1.0</td><td>0.5</td><td>Detection confidence threshold</td></tr>'+
    '<tr><td>NMS IoU Threshold</td><td>0.0 – 1.0</td><td>0.45</td><td>Non-Maximum Suppression IoU threshold</td></tr>'+
    '<tr><td>Top-K</td><td>1 – 100</td><td>5</td><td>Show top K results for classification</td></tr>'+
    '<tr><td>Alpha (Overlay)</td><td>0.0 – 1.0</td><td>0.5</td><td>Segmentation mask transparency</td></tr></table>'+
    '<h4>Input Source Types</h4>'+
    '<table class="ref-tbl"><tr><th>Type</th><th>Description</th><th>Mode</th></tr>'+
    '<tr><td>Image File</td><td>.jpg, .png, .bmp, etc.</td><td>Single</td></tr>'+
    '<tr><td>Video File</td><td>.mp4, .avi, etc.</td><td>Single / Continuous</td></tr>'+
    '<tr><td>Camera</td><td>USB / CSI camera (/dev/video*)</td><td>Continuous</td></tr>'+
    '<tr><td>RTSP</td><td>rtsp:// stream URL</td><td>Continuous</td></tr></table>',
    '<h4>추론 파라미터</h4>'+
    '<table class="ref-tbl"><tr><th>파라미터</th><th>범위</th><th>기본값</th><th>설명</th></tr>'+
    '<tr><td>Confidence Threshold</td><td>0.0 – 1.0</td><td>0.5</td><td>검출 신뢰도 임계값</td></tr>'+
    '<tr><td>NMS IoU Threshold</td><td>0.0 – 1.0</td><td>0.45</td><td>Non-Maximum Suppression IoU 임계값</td></tr>'+
    '<tr><td>Top-K</td><td>1 – 100</td><td>5</td><td>분류 시 상위 K개 결과 표시</td></tr>'+
    '<tr><td>Alpha (Overlay)</td><td>0.0 – 1.0</td><td>0.5</td><td>분할 마스크 투명도</td></tr></table>'+
    '<h4>입력 소스 유형</h4>'+
    '<table class="ref-tbl"><tr><th>Type</th><th>설명</th><th>모드</th></tr>'+
    '<tr><td>Image File</td><td>.jpg, .png, .bmp 등</td><td>Single</td></tr>'+
    '<tr><td>Video File</td><td>.mp4, .avi 등</td><td>Single / Continuous</td></tr>'+
    '<tr><td>Camera</td><td>USB / CSI 카메라 (/dev/video*)</td><td>Continuous</td></tr>'+
    '<tr><td>RTSP</td><td>rtsp:// 스트림 URL</td><td>Continuous</td></tr></table>',
    '<h4>推論パラメータ</h4>'+
    '<table class="ref-tbl"><tr><th>パラメータ</th><th>範囲</th><th>デフォルト</th><th>説明</th></tr>'+
    '<tr><td>Confidence Threshold</td><td>0.0 – 1.0</td><td>0.5</td><td>検出信頼度しきい値</td></tr>'+
    '<tr><td>NMS IoU Threshold</td><td>0.0 – 1.0</td><td>0.45</td><td>Non-Maximum Suppression IoU しきい値</td></tr>'+
    '<tr><td>Top-K</td><td>1 – 100</td><td>5</td><td>分類時の上位K件の結果を表示</td></tr>'+
    '<tr><td>Alpha (Overlay)</td><td>0.0 – 1.0</td><td>0.5</td><td>セグメンテーションマスクの透明度</td></tr></table>'+
    '<h4>入力ソースタイプ</h4>'+
    '<table class="ref-tbl"><tr><th>タイプ</th><th>説明</th><th>モード</th></tr>'+
    '<tr><td>Image File</td><td>.jpg, .png, .bmp など</td><td>Single</td></tr>'+
    '<tr><td>Video File</td><td>.mp4, .avi など</td><td>Single / Continuous</td></tr>'+
    '<tr><td>Camera</td><td>USB / CSI カメラ (/dev/video*)</td><td>Continuous</td></tr>'+
    '<tr><td>RTSP</td><td>rtsp:// ストリーム URL</td><td>Continuous</td></tr></table>',
    '<h4>推理参数</h4>'+
    '<table class="ref-tbl"><tr><th>参数</th><th>范围</th><th>默认值</th><th>说明</th></tr>'+
    '<tr><td>Confidence Threshold</td><td>0.0 – 1.0</td><td>0.5</td><td>检测置信度阈值</td></tr>'+
    '<tr><td>NMS IoU Threshold</td><td>0.0 – 1.0</td><td>0.45</td><td>Non-Maximum Suppression IoU 阈值</td></tr>'+
    '<tr><td>Top-K</td><td>1 – 100</td><td>5</td><td>分类时显示前K个结果</td></tr>'+
    '<tr><td>Alpha (Overlay)</td><td>0.0 – 1.0</td><td>0.5</td><td>分割掩码透明度</td></tr></table>'+
    '<h4>输入源类型</h4>'+
    '<table class="ref-tbl"><tr><th>类型</th><th>说明</th><th>模式</th></tr>'+
    '<tr><td>Image File</td><td>.jpg, .png, .bmp 等</td><td>Single</td></tr>'+
    '<tr><td>Video File</td><td>.mp4, .avi 等</td><td>Single / Continuous</td></tr>'+
    '<tr><td>Camera</td><td>USB / CSI 摄像头 (/dev/video*)</td><td>Continuous</td></tr>'+
    '<tr><td>RTSP</td><td>rtsp:// 串流 URL</td><td>Continuous</td></tr></table>',
    '<h4>推理參數</h4>'+
    '<table class="ref-tbl"><tr><th>參數</th><th>範圍</th><th>預設值</th><th>說明</th></tr>'+
    '<tr><td>Confidence Threshold</td><td>0.0 – 1.0</td><td>0.5</td><td>偵測信賴度閾值</td></tr>'+
    '<tr><td>NMS IoU Threshold</td><td>0.0 – 1.0</td><td>0.45</td><td>Non-Maximum Suppression IoU 閾值</td></tr>'+
    '<tr><td>Top-K</td><td>1 – 100</td><td>5</td><td>分類時顯示前K個結果</td></tr>'+
    '<tr><td>Alpha (Overlay)</td><td>0.0 – 1.0</td><td>0.5</td><td>分割遮罩透明度</td></tr></table>'+
    '<h4>輸入來源類型</h4>'+
    '<table class="ref-tbl"><tr><th>類型</th><th>說明</th><th>模式</th></tr>'+
    '<tr><td>Image File</td><td>.jpg, .png, .bmp 等</td><td>Single</td></tr>'+
    '<tr><td>Video File</td><td>.mp4, .avi 等</td><td>Single / Continuous</td></tr>'+
    '<tr><td>Camera</td><td>USB / CSI 攝影機 (/dev/video*)</td><td>Continuous</td></tr>'+
    '<tr><td>RTSP</td><td>rtsp:// 串流 URL</td><td>Continuous</td></tr></table>'),
  workflow:refT5('<h4>Single Mode Workflow</h4>'+
    '<ol><li>Select a model from the model cards on the left</li>'+
    '<li>Select an image/video file (thumbnail preview)</li>'+
    '<li>Adjust parameters if needed (Confidence, NMS, etc.)</li>'+
    '<li>Click <code>▶ Run</code> → NPU inference runs</li>'+
    '<li>Bounding boxes / masks / keypoints are overlaid on the result image</li>'+
    '<li>Compare original and result with the <strong>Before / After</strong> slider</li></ol>'+
    '<h4>Continuous Mode Workflow</h4>'+
    '<ol><li>Switch to Continuous tab (top tabs)</li>'+
    '<li>Add slots (up to 8) → assign model/input to each slot</li>'+
    '<li>Click <code>▶ Start</code> → real-time inference begins</li>'+
    '<li>Real-time performance displayed: FPS, latency, etc.</li>'+
    '<li>Stop individual/all with <code>■ Stop</code></li></ol>'+
    '<div class="ref-box warn"><span class="ref-box-icon">⚠️</span><span>In Continuous mode, more slots share NPU resources and may reduce FPS.</span></div>',
    '<h4>Single 모드 워크플로우</h4>'+
    '<ol><li>좌측 모델 카드에서 모델 선택</li>'+
    '<li>이미지/비디오 파일 선택 (썸네일 미리보기)</li>'+
    '<li>필요시 파라미터 조정 (Confidence, NMS 등)</li>'+
    '<li><code>▶ Run</code> 클릭 → NPU 추론 실행</li>'+
    '<li>결과 이미지에 바운딩 박스 / 마스크 / 키포인트가 오버레이됩니다</li>'+
    '<li><strong>Before / After</strong> 슬라이더로 원본과 결과 비교</li></ol>'+
    '<h4>Continuous 모드 워크플로우</h4>'+
    '<ol><li>Continuous 탭으로 전환 (화면 상단 탭)</li>'+
    '<li>슬롯(최대 8개) 추가 → 각 슬롯에 모델/입력 할당</li>'+
    '<li><code>▶ Start</code> 클릭 → 실시간 추론 시작</li>'+
    '<li>FPS, 지연시간 등 실시간 성능 표시</li>'+
    '<li><code>■ Stop</code>으로 개별/전체 중지</li></ol>'+
    '<div class="ref-box warn"><span class="ref-box-icon">⚠️</span><span>Continuous 모드에서 슬롯이 많으면 NPU 자원을 공유하여 FPS가 떨어질 수 있습니다.</span></div>',
    '<h4>Single モードワークフロー</h4>'+
    '<ol><li>左側のモデルカードからモデルを選択</li>'+
    '<li>画像/動画ファイルを選択（サムネイルプレビュー）</li>'+
    '<li>必要に応じてパラメータを調整（Confidence、NMS など）</li>'+
    '<li><code>▶ Run</code> をクリック → NPU 推論を実行</li>'+
    '<li>結果画像にバウンディングボックス/マスク/キーポイントがオーバーレイされます</li>'+
    '<li><strong>Before / After</strong> スライダーで元画像と結果を比較</li></ol>'+
    '<h4>Continuous モードワークフロー</h4>'+
    '<ol><li>Continuous タブに切り替え（画面上部のタブ）</li>'+
    '<li>スロット（最大8つ）を追加 → 各スロットにモデル/入力を割り当て</li>'+
    '<li><code>▶ Start</code> をクリック → リアルタイム推論開始</li>'+
    '<li>FPS、レイテンシなどのリアルタイム性能を表示</li>'+
    '<li><code>■ Stop</code> で個別/全体を停止</li></ol>'+
    '<div class="ref-box warn"><span class="ref-box-icon">⚠️</span><span>Continuous モードではスロットが多いほど NPU リソースを共有し、FPS が低下する場合があります。</span></div>',
    '<h4>Single 模式工作流</h4>'+
    '<ol><li>从左侧模型卡片中选择模型</li>'+
    '<li>选择图片/视频文件（缩略图预览）</li>'+
    '<li>根据需要调整参数（Confidence、NMS 等）</li>'+
    '<li>点击 <code>▶ Run</code> → 执行 NPU 推理</li>'+
    '<li>结果图片上叠加边界框/掩码/关键点</li>'+
    '<li>使用 <strong>Before / After</strong> 滑块对比原图和结果</li></ol>'+
    '<h4>Continuous 模式工作流</h4>'+
    '<ol><li>切换到 Continuous 标签页（顶部标签）</li>'+
    '<li>添加槽位（最多8个）→ 为每个槽位分配模型/输入</li>'+
    '<li>点击 <code>▶ Start</code> → 开始实时推理</li>'+
    '<li>显示 FPS、延迟等实时性能</li>'+
    '<li>使用 <code>■ Stop</code> 单独/全部停止</li></ol>'+
    '<div class="ref-box warn"><span class="ref-box-icon">⚠️</span><span>Continuous 模式下槽位越多，NPU 资源共享越多，FPS 可能降低。</span></div>',
    '<h4>Single 模式工作流程</h4>'+
    '<ol><li>從左側模型卡片中選擇模型</li>'+
    '<li>選擇圖片/影片檔案（縮圖預覽）</li>'+
    '<li>如需調整參數（Confidence、NMS 等）</li>'+
    '<li>點擊 <code>▶ Run</code> → 執行 NPU 推理</li>'+
    '<li>結果圖片上疊加邊界框/遮罩/關鍵點</li>'+
    '<li>使用 <strong>Before / After</strong> 滑桿對比原圖和結果</li></ol>'+
    '<h4>Continuous 模式工作流程</h4>'+
    '<ol><li>切換到 Continuous 分頁（頂部分頁）</li>'+
    '<li>新增插槽（最多8個）→ 為每個插槽指派模型/輸入</li>'+
    '<li>點擊 <code>▶ Start</code> → 開始即時推理</li>'+
    '<li>顯示 FPS、延遲等即時效能</li>'+
    '<li>使用 <code>■ Stop</code> 單獨/全部停止</li></ol>'+
    '<div class="ref-box warn"><span class="ref-box-icon">⚠️</span><span>Continuous 模式下插槽越多，NPU 資源共享越多，FPS 可能降低。</span></div>'),
  tips:refT5('<h4>Tips</h4>'+
    '<ul><li><strong>Export Package</strong> lets you export source code + model + config as a single package</li>'+
    '<li>SR (Super Resolution) results output at higher resolution than the original</li>'+
    '<li>DnCNN denoising learns the noise residual and subtracts it from the original</li></ul>',
    '<h4>팁</h4>'+
    '<li><strong>Export Package</strong>로 소스코드 + 모델 + 설정을 하나의 패키지로 내보낼 수 있습니다</li>'+
    '<li>SR(Super Resolution) 결과는 원본보다 고해상도로 출력됩니다</li>'+
    '<li>DnCNN 노이즈 제거는 noise residual을 학습하여 원본에서 뺍니다</li></ul>',
    '<h4>ヒント</h4>'+
    '<ul><li><strong>Export Package</strong> でソースコード+モデル+設定を1つのパッケージとしてエクスポートできます</li>'+
    '<li>SR（Super Resolution）の結果はオリジナルより高解像度で出力されます</li>'+
    '<li>DnCNN ノイズ除去はノイズ残差を学習し、オリジナルから差し引きます</li></ul>',
    '<h4>提示</h4>'+
    '<ul><li><strong>Export Package</strong> 可将源代码+模型+配置导出为一个包</li>'+
    '<li>SR（Super Resolution）结果以比原图更高的分辨率输出</li>'+
    '<li>DnCNN 降噪学习噪声残差并从原图中减去</li></ul>',
    '<h4>提示</h4>'+
    '<ul><li><strong>Export Package</strong> 可將原始碼+模型+設定匯出為一個套件</li>'+
    '<li>SR（Super Resolution）結果以比原圖更高的解析度輸出</li>'+
    '<li>DnCNN 降噪學習噪聲殘差並從原圖中減去</li></ul>')
}},

{cat:'core',id:'rtsp-continuous',icon:'📡',name:refT5('RTSP Streaming','RTSP 스트리밍','RTSP ストリーミング','RTSP 串流','RTSP 串流'),desc:refT5('RTSP server details for Continuous mode','Continuous 모드의 RTSP 서버 상세','Continuous モードの RTSP サーバー詳細','Continuous 模式的 RTSP 服务器详情','Continuous 模式的 RTSP 伺服器詳情'),page:'run',tabs:{
  overview:refT5('<h4>Overview</h4><p>In Continuous mode, RTSP streaming allows real-time inference on network video streams from IP cameras or media servers.</p>'+
    '<div class="ref-flow"><span class="ref-flow-step">Enter RTSP URL</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">Select Stream</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">▶ Start</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">Live Inference</span></div>',
    '<h4>개요</h4><p>Continuous 모드에서 RTSP 스트리밍은 IP 카메라 또는 미디어 서버의 네트워크 비디오 스트림에 실시간 추론을 수행합니다.</p>'+
    '<div class="ref-flow"><span class="ref-flow-step">RTSP URL 입력</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">스트림 선택</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">▶ 시작</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">실시간 추론</span></div>',
    '<h4>概要</h4><p>Continuous モードでは、RTSP ストリーミングにより IP カメラやメディアサーバーのネットワーク動画ストリームに対してリアルタイム推論を実行します。</p>'+
    '<div class="ref-flow"><span class="ref-flow-step">RTSP URL 入力</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">ストリーム選択</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">▶ 開始</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">リアルタイム推論</span></div>',
    '<h4>概述</h4><p>在 Continuous 模式下，RTSP 串流可对来自 IP 摄像头或媒体服务器的网络视频流进行实时推理。</p>'+
    '<div class="ref-flow"><span class="ref-flow-step">输入 RTSP URL</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">选择串流</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">▶ 开始</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">实时推理</span></div>',
    '<h4>概述</h4><p>在 Continuous 模式下，RTSP 串流可對來自 IP 攝影機或媒體伺服器的網路影片串流進行即時推理。</p>'+
    '<div class="ref-flow"><span class="ref-flow-step">輸入 RTSP URL</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">選擇串流</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">▶ 開始</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">即時推理</span></div>'),
  params:refT5('<h4>RTSP Configuration</h4>'+
    '<table class="ref-tbl"><tr><th>Field</th><th>Format</th><th>Example</th><th>Description</th></tr>'+
    '<tr><td>Server IP</td><td>IP:Port</td><td>192.168.1.100:554</td><td>RTSP server address and port</td></tr>'+
    '<tr><td>Stream Path</td><td>/path</td><td>/live/ch0</td><td>Stream channel path on server</td></tr>'+
    '<tr><td>Full URL</td><td>rtsp://</td><td>rtsp://192.168.1.100:554/live/ch0</td><td>Complete RTSP URL</td></tr>'+
    '<tr><td>Username</td><td>text</td><td>admin</td><td>Auth username (if required)</td></tr>'+
    '<tr><td>Password</td><td>text</td><td>********</td><td>Auth password (if required)</td></tr></table>'+
    '<h4>Supported Protocols</h4>'+
    '<table class="ref-tbl"><tr><th>Protocol</th><th>Port</th><th>Use Case</th></tr>'+
    '<tr><td>RTSP/TCP</td><td>554</td><td>Standard (reliable, higher latency)</td></tr>'+
    '<tr><td>RTSP/UDP</td><td>554</td><td>Low-latency (may drop frames)</td></tr></table>',
    '<h4>RTSP 설정</h4>'+
    '<table class="ref-tbl"><tr><th>필드</th><th>형식</th><th>예시</th><th>설명</th></tr>'+
    '<tr><td>서버 IP</td><td>IP:포트</td><td>192.168.1.100:554</td><td>RTSP 서버 주소 및 포트</td></tr>'+
    '<tr><td>스트림 경로</td><td>/경로</td><td>/live/ch0</td><td>서버 내 스트림 채널 경로</td></tr>'+
    '<tr><td>전체 URL</td><td>rtsp://</td><td>rtsp://192.168.1.100:554/live/ch0</td><td>완전한 RTSP URL</td></tr>'+
    '<tr><td>사용자명</td><td>텍스트</td><td>admin</td><td>인증 사용자명 (필요 시)</td></tr>'+
    '<tr><td>비밀번호</td><td>텍스트</td><td>********</td><td>인증 비밀번호 (필요 시)</td></tr></table>'+
    '<h4>지원 프로토콜</h4>'+
    '<table class="ref-tbl"><tr><th>프로토콜</th><th>포트</th><th>사용 사례</th></tr>'+
    '<tr><td>RTSP/TCP</td><td>554</td><td>표준 (안정적, 높은 지연)</td></tr>'+
    '<tr><td>RTSP/UDP</td><td>554</td><td>저지연 (프레임 드롭 가능)</td></tr></table>',
    '<h4>RTSP 設定</h4>'+
    '<table class="ref-tbl"><tr><th>フィールド</th><th>形式</th><th>例</th><th>説明</th></tr>'+
    '<tr><td>サーバー IP</td><td>IP:ポート</td><td>192.168.1.100:554</td><td>RTSP サーバーアドレスとポート</td></tr>'+
    '<tr><td>ストリームパス</td><td>/パス</td><td>/live/ch0</td><td>サーバー上のストリームチャネルパス</td></tr>'+
    '<tr><td>フル URL</td><td>rtsp://</td><td>rtsp://192.168.1.100:554/live/ch0</td><td>完全な RTSP URL</td></tr>'+
    '<tr><td>ユーザー名</td><td>テキスト</td><td>admin</td><td>認証ユーザー名（必要な場合）</td></tr>'+
    '<tr><td>パスワード</td><td>テキスト</td><td>********</td><td>認証パスワード（必要な場合）</td></tr></table>'+
    '<h4>サポートプロトコル</h4>'+
    '<table class="ref-tbl"><tr><th>プロトコル</th><th>ポート</th><th>用途</th></tr>'+
    '<tr><td>RTSP/TCP</td><td>554</td><td>標準（安定、高レイテンシ）</td></tr>'+
    '<tr><td>RTSP/UDP</td><td>554</td><td>低レイテンシ（フレームドロップの可能性）</td></tr></table>',
    '<h4>RTSP 配置</h4>'+
    '<table class="ref-tbl"><tr><th>字段</th><th>格式</th><th>示例</th><th>说明</th></tr>'+
    '<tr><td>服务器 IP</td><td>IP:端口</td><td>192.168.1.100:554</td><td>RTSP 服务器地址和端口</td></tr>'+
    '<tr><td>串流路径</td><td>/路径</td><td>/live/ch0</td><td>服务器上的串流通道路径</td></tr>'+
    '<tr><td>完整 URL</td><td>rtsp://</td><td>rtsp://192.168.1.100:554/live/ch0</td><td>完整 RTSP URL</td></tr>'+
    '<tr><td>用户名</td><td>文本</td><td>admin</td><td>认证用户名（如需要）</td></tr>'+
    '<tr><td>密码</td><td>文本</td><td>********</td><td>认证密码（如需要）</td></tr></table>'+
    '<h4>支持的协议</h4>'+
    '<table class="ref-tbl"><tr><th>协议</th><th>端口</th><th>使用场景</th></tr>'+
    '<tr><td>RTSP/TCP</td><td>554</td><td>标准（可靠，较高延迟）</td></tr>'+
    '<tr><td>RTSP/UDP</td><td>554</td><td>低延迟（可能丢帧）</td></tr></table>',
    '<h4>RTSP 設定</h4>'+
    '<table class="ref-tbl"><tr><th>欄位</th><th>格式</th><th>範例</th><th>說明</th></tr>'+
    '<tr><td>伺服器 IP</td><td>IP:連接埠</td><td>192.168.1.100:554</td><td>RTSP 伺服器位址和連接埠</td></tr>'+
    '<tr><td>串流路徑</td><td>/路徑</td><td>/live/ch0</td><td>伺服器上的串流頻道路徑</td></tr>'+
    '<tr><td>完整 URL</td><td>rtsp://</td><td>rtsp://192.168.1.100:554/live/ch0</td><td>完整 RTSP URL</td></tr>'+
    '<tr><td>使用者名稱</td><td>文字</td><td>admin</td><td>驗證使用者名稱（如需要）</td></tr>'+
    '<tr><td>密碼</td><td>文字</td><td>********</td><td>驗證密碼（如需要）</td></tr></table>'+
    '<h4>支援的協定</h4>'+
    '<table class="ref-tbl"><tr><th>協定</th><th>連接埠</th><th>使用場景</th></tr>'+
    '<tr><td>RTSP/TCP</td><td>554</td><td>標準（可靠，較高延遲）</td></tr>'+
    '<tr><td>RTSP/UDP</td><td>554</td><td>低延遲（可能掉幀）</td></tr></table>'),
  tips:refT5('<h4>Tips</h4>'+
    '<ul><li>Test RTSP connectivity first: <code>ffprobe rtsp://IP:554/path</code></li>'+
    '<li>For authenticated streams, embed credentials: <code>rtsp://user:pass@IP:554/path</code></li>'+
    '<li>If stream drops frequently, switch from UDP to TCP transport</li>'+
    '<li>Maximum concurrent RTSP slots depends on network bandwidth and NPU capacity</li></ul>',
    '<h4>팁</h4>'+
    '<ul><li>먼저 RTSP 연결을 테스트하세요: <code>ffprobe rtsp://IP:554/path</code></li>'+
    '<li>인증이 필요한 스트림은 URL에 자격증명을 포함: <code>rtsp://user:pass@IP:554/path</code></li>'+
    '<li>스트림이 자주 끊기면 UDP에서 TCP 전송으로 전환하세요</li>'+
    '<li>최대 동시 RTSP 슬롯 수는 네트워크 대역폭과 NPU 용량에 따라 달라집니다</li></ul>',
    '<h4>ヒント</h4>'+
    '<ul><li>まず RTSP 接続をテストしてください: <code>ffprobe rtsp://IP:554/path</code></li>'+
    '<li>認証が必要なストリームは URL に認証情報を埋め込み: <code>rtsp://user:pass@IP:554/path</code></li>'+
    '<li>ストリームが頻繁に切断される場合は、UDP から TCP トランスポートに切り替えてください</li>'+
    '<li>最大同時 RTSP スロット数はネットワーク帯域幅と NPU 容量に依存します</li></ul>',
    '<h4>提示</h4>'+
    '<ul><li>请先测试 RTSP 连接: <code>ffprobe rtsp://IP:554/path</code></li>'+
    '<li>需要认证的串流，在 URL 中嵌入凭据: <code>rtsp://user:pass@IP:554/path</code></li>'+
    '<li>如果串流频繁断开，请从 UDP 切换到 TCP 传输</li>'+
    '<li>最大并发 RTSP 槽位数取决于网络带宽和 NPU 容量</li></ul>',
    '<h4>提示</h4>'+
    '<ul><li>請先測試 RTSP 連線: <code>ffprobe rtsp://IP:554/path</code></li>'+
    '<li>需要驗證的串流，在 URL 中嵌入憑證: <code>rtsp://user:pass@IP:554/path</code></li>'+
    '<li>如果串流頻繁斷開，請從 UDP 切換到 TCP 傳輸</li>'+
    '<li>最大並行 RTSP 插槽數取決於網路頻寬和 NPU 容量</li></ul>')
}},

{cat:'core',id:'benchmark',icon:'⏱️',name:'Benchmark',desc:refT5('Multi-model performance measurement · FPS comparison · Report','다중 모델 성능 측정 · FPS 비교 · 리포트','複数モデル性能測定・FPS 比較・レポート','多模型性能测量·FPS 对比·报告','多模型效能測量·FPS 對比·報告'),page:'bench',tabs:{
  overview:refT5('<h4>Overview</h4><p>The Benchmark page measures and compares NPU inference performance across multiple models.</p>'+
    '<div class="ref-flow"><span class="ref-flow-step">Select Models (multi)</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">Set Loop Count</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">▶ Run Benchmark</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">Result Chart</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">Export Report</span></div>',
    '<h4>개요</h4><p>Benchmark 페이지는 여러 모델의 NPU 추론 성능을 측정하고 비교합니다.</p>'+
    '<div class="ref-flow"><span class="ref-flow-step">모델 선택 (다중)</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">Loop Count 설정</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">▶ Run Benchmark</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">결과 차트</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">Export Report</span></div>',
    '<h4>概要</h4><p>Benchmark ページは複数モデルの NPU 推論性能を測定し比較します。</p>'+
    '<div class="ref-flow"><span class="ref-flow-step">モデル選択（複数）</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">Loop Count 設定</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">▶ Run Benchmark</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">結果チャート</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">Export Report</span></div>',
    '<h4>概述</h4><p>Benchmark 页面测量和比较多个模型的 NPU 推理性能。</p>'+
    '<div class="ref-flow"><span class="ref-flow-step">选择模型（多选）</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">设置 Loop Count</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">▶ Run Benchmark</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">结果图表</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">Export Report</span></div>',
    '<h4>概述</h4><p>Benchmark 頁面測量和比較多個模型的 NPU 推理效能。</p>'+
    '<div class="ref-flow"><span class="ref-flow-step">選擇模型（多選）</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">設定 Loop Count</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">▶ Run Benchmark</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">結果圖表</span><span class="ref-flow-arrow">→</span><span class="ref-flow-step">Export Report</span></div>'),
  params:refT5('<h4>Parameters</h4>'+
    '<table class="ref-tbl"><tr><th>Parameter</th><th>Range</th><th>Default</th><th>Description</th></tr>'+
    '<tr><td>Loop Count</td><td>1 – 10,000</td><td>100</td><td>Inference iteration count (higher = more accurate)</td></tr></table>'+
    '<h4>Result Metrics</h4>'+
    '<table class="ref-tbl"><tr><th>Metric</th><th>Unit</th><th>Description</th></tr>'+
    '<tr><td>FPS</td><td>frames/sec</td><td>Frames processed per second</td></tr>'+
    '<tr><td>Avg Latency</td><td>ms</td><td>Average inference latency</td></tr>'+
    '<tr><td>Min/Max Latency</td><td>ms</td><td>Minimum/maximum latency</td></tr>'+
    '<tr><td>Throughput</td><td>infer/sec</td><td>Inferences per second</td></tr></table>',
    '<h4>파라미터</h4>'+
    '<table class="ref-tbl"><tr><th>파라미터</th><th>범위</th><th>기본값</th><th>설명</th></tr>'+
    '<tr><td>Loop Count</td><td>1 – 10,000</td><td>100</td><td>추론 반복 횟수 (높을수록 정확)</td></tr></table>'+
    '<h4>결과 지표</h4>'+
    '<table class="ref-tbl"><tr><th>지표</th><th>단위</th><th>설명</th></tr>'+
    '<tr><td>FPS</td><td>frames/sec</td><td>초당 처리 프레임 수</td></tr>'+
    '<tr><td>Avg Latency</td><td>ms</td><td>평균 추론 지연시간</td></tr>'+
    '<tr><td>Min/Max Latency</td><td>ms</td><td>최소/최대 지연시간</td></tr>'+
    '<tr><td>Throughput</td><td>infer/sec</td><td>초당 처리량</td></tr></table>',
    '<h4>パラメータ</h4>'+
    '<table class="ref-tbl"><tr><th>パラメータ</th><th>範囲</th><th>デフォルト</th><th>説明</th></tr>'+
    '<tr><td>Loop Count</td><td>1 – 10,000</td><td>100</td><td>推論繰り返し回数（多いほど正確）</td></tr></table>'+
    '<h4>結果指標</h4>'+
    '<table class="ref-tbl"><tr><th>指標</th><th>単位</th><th>説明</th></tr>'+
    '<tr><td>FPS</td><td>frames/sec</td><td>1秒あたりの処理フレーム数</td></tr>'+
    '<tr><td>Avg Latency</td><td>ms</td><td>平均推論レイテンシ</td></tr>'+
    '<tr><td>Min/Max Latency</td><td>ms</td><td>最小/最大レイテンシ</td></tr>'+
    '<tr><td>Throughput</td><td>infer/sec</td><td>1秒あたりのスループット</td></tr></table>',
    '<h4>参数</h4>'+
    '<table class="ref-tbl"><tr><th>参数</th><th>范围</th><th>默认值</th><th>说明</th></tr>'+
    '<tr><td>Loop Count</td><td>1 – 10,000</td><td>100</td><td>推理迭代次数（越高越准确）</td></tr></table>'+
    '<h4>结果指标</h4>'+
    '<table class="ref-tbl"><tr><th>指标</th><th>单位</th><th>说明</th></tr>'+
    '<tr><td>FPS</td><td>frames/sec</td><td>每秒处理帧数</td></tr>'+
    '<tr><td>Avg Latency</td><td>ms</td><td>平均推理延迟</td></tr>'+
    '<tr><td>Min/Max Latency</td><td>ms</td><td>最小/最大延迟</td></tr>'+
    '<tr><td>Throughput</td><td>infer/sec</td><td>每秒吞吐量</td></tr></table>',
    '<h4>參數</h4>'+
    '<table class="ref-tbl"><tr><th>參數</th><th>範圍</th><th>預設值</th><th>說明</th></tr>'+
    '<tr><td>Loop Count</td><td>1 – 10,000</td><td>100</td><td>推理迭代次數（越高越準確）</td></tr></table>'+
    '<h4>結果指標</h4>'+
    '<table class="ref-tbl"><tr><th>指標</th><th>單位</th><th>說明</th></tr>'+
    '<tr><td>FPS</td><td>frames/sec</td><td>每秒處理影格數</td></tr>'+
    '<tr><td>Avg Latency</td><td>ms</td><td>平均推理延遲</td></tr>'+
    '<tr><td>Min/Max Latency</td><td>ms</td><td>最小/最大延遲</td></tr>'+
    '<tr><td>Throughput</td><td>infer/sec</td><td>每秒吞吐量</td></tr></table>'),
  tips:refT5('<h4>Tips</h4>'+
    '<ul><li>First run may be slightly slower due to model warmup — Loop 100+ recommended</li>'+
    '<li>FPS comparison chart provides intuitive comparison via horizontal bar graph</li>'+
    '<li><strong>📄 Export Report</strong> saves the benchmark report as PDF/image</li></ul>',
    '<h4>팁</h4>'+
    '<ul><li>첫 실행은 모델 워밍업으로 약간 느릴 수 있습니다 — Loop 100 이상 권장</li>'+
    '<li>FPS 비교 차트는 수평 막대 그래프로 직관적 비교 가능</li>'+
    '<li><strong>📄 Export Report</strong>로 PDF/이미지 형태의 벤치마크 보고서를 저장합니다</li></ul>',
    '<h4>ヒント</h4>'+
    '<ul><li>初回実行はモデルのウォームアップにより少し遅くなる場合があります — Loop 100以上推奨</li>'+
    '<li>FPS 比較チャートは水平棒グラフで直感的に比較できます</li>'+
    '<li><strong>📄 Export Report</strong> でベンチマークレポートを PDF/画像として保存します</li></ul>',
    '<h4>提示</h4>'+
    '<ul><li>首次运行可能因模型预热略慢 — 建议 Loop 100 以上</li>'+
    '<li>FPS 对比图通过水平柱状图提供直观比较</li>'+
    '<li><strong>📄 Export Report</strong> 可将基准测试报告保存为 PDF/图片</li></ul>',
    '<h4>提示</h4>'+
    '<ul><li>首次執行可能因模型預熱略慢 — 建議 Loop 100 以上</li>'+
    '<li>FPS 對比圖透過水平長條圖提供直觀比較</li>'+
    '<li><strong>📄 Export Report</strong> 可將基準測試報告儲存為 PDF/圖片</li></ul>')
}},

{cat:'core',id:'compare',icon:'🔀',name:'A/B Compare',desc:refT5('2–8 model simultaneous comparison · Performance table','2~8 모델 동시 비교 · 성능 테이블','2〜8モデル同時比較・パフォーマンステーブル','2~8模型同时对比·性能表','2~8模型同時對比·效能表'),page:'compare',tabs:{
  overview:refT5('<h4>Overview</h4><p>The A/B Compare page runs multiple models simultaneously on the same input and compares results side by side.</p>'+
    '<ul><li><strong>Simultaneous comparison</strong> — Assign different models to 2–8 slots</li>'+
    '<li><strong>Shared input</strong> — All slots use the same image/video/camera/RTSP input</li>'+
    '<li><strong>Performance table</strong> — Compare FPS, latency for each model in table format</li></ul>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>Adjust slot count with the <strong>Slot Count</strong> dropdown at the top right (2/4/6/8).</span></div>',
    '<h4>개요</h4><p>A/B Compare 페이지는 동일한 입력에 대해 여러 모델을 동시에 실행하여 결과를 나란히 비교합니다.</p>'+
    '<ul><li><strong>동시 비교</strong> — 2~8개 슬롯에 각각 다른 모델 할당</li>'+
    '<li><strong>입력 공유</strong> — 모든 슬롯이 동일한 이미지/비디오/카메라/RTSP 입력 사용</li>'+
    '<li><strong>성능 테이블</strong> — 각 모델의 FPS, Latency를 표 형태로 비교</li></ul>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>슬롯 수는 우측 상단의 <strong>Slot Count</strong> 드롭다운으로 조절합니다 (2/4/6/8).</span></div>',
    '<h4>概要</h4><p>A/B Compare ページは同じ入力に対して複数のモデルを同時に実行し、結果を並べて比較します。</p>'+
    '<ul><li><strong>同時比較</strong> — 2〜8スロットにそれぞれ異なるモデルを割り当て</li>'+
    '<li><strong>入力共有</strong> — すべてのスロットが同じ画像/動画/カメラ/RTSP 入力を使用</li>'+
    '<li><strong>パフォーマンステーブル</strong> — 各モデルの FPS、レイテンシを表形式で比較</li></ul>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>スロット数は右上の <strong>Slot Count</strong> ドロップダウンで調整します（2/4/6/8）。</span></div>',
    '<h4>概述</h4><p>A/B Compare 页面在相同输入上同时运行多个模型，并排比较结果。</p>'+
    '<ul><li><strong>同时对比</strong> — 在2~8个槽位上分别分配不同模型</li>'+
    '<li><strong>共享输入</strong> — 所有槽位使用相同的图片/视频/摄像头/RTSP 输入</li>'+
    '<li><strong>性能表</strong> — 以表格形式比较各模型的 FPS、延迟</li></ul>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>通过右上角的 <strong>Slot Count</strong> 下拉菜单调整槽位数（2/4/6/8）。</span></div>',
    '<h4>概述</h4><p>A/B Compare 頁面在相同輸入上同時執行多個模型，並排比較結果。</p>'+
    '<ul><li><strong>同時對比</strong> — 在2~8個插槽上分別指派不同模型</li>'+
    '<li><strong>共享輸入</strong> — 所有插槽使用相同的圖片/影片/攝影機/RTSP 輸入</li>'+
    '<li><strong>效能表</strong> — 以表格形式比較各模型的 FPS、延遲</li></ul>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>透過右上角的 <strong>Slot Count</strong> 下拉選單調整插槽數（2/4/6/8）。</span></div>'),
  workflow:refT5('<h4>Workflow</h4>'+
    '<ol><li>Select Slot Count (2–8)</li>'+
    '<li>Assign models to compare in each slot</li>'+
    '<li>Select shared input source (file/camera/RTSP)</li>'+
    '<li><code>▶ Start</code> → All slots run inference simultaneously</li>'+
    '<li>Compare results side by side, check the Performance Comparison table at the bottom</li></ol>',
    '<h4>워크플로우</h4>'+
    '<ol><li>Slot Count 선택 (2~8)</li>'+
    '<li>각 슬롯에 비교할 모델 할당</li>'+
    '<li>공유 입력 소스 선택 (파일/카메라/RTSP)</li>'+
    '<li><code>▶ Start</code> → 모든 슬롯 동시 추론</li>'+
    '<li>결과를 나란히 비교, 하단 Performance Comparison 테이블 확인</li></ol>',
    '<h4>ワークフロー</h4>'+
    '<ol><li>Slot Count を選択（2〜8）</li>'+
    '<li>各スロットに比較するモデルを割り当て</li>'+
    '<li>共有入力ソースを選択（ファイル/カメラ/RTSP）</li>'+
    '<li><code>▶ Start</code> → 全スロット同時推論</li>'+
    '<li>結果を並べて比較、下部の Performance Comparison テーブルを確認</li></ol>',
    '<h4>工作流</h4>'+
    '<ol><li>选择 Slot Count（2~8）</li>'+
    '<li>为每个槽位分配要对比的模型</li>'+
    '<li>选择共享输入源（文件/摄像头/RTSP）</li>'+
    '<li><code>▶ Start</code> → 所有槽位同时推理</li>'+
    '<li>并排比较结果，查看底部 Performance Comparison 表格</li></ol>',
    '<h4>工作流程</h4>'+
    '<ol><li>選擇 Slot Count（2~8）</li>'+
    '<li>為每個插槽指派要對比的模型</li>'+
    '<li>選擇共享輸入來源（檔案/攝影機/RTSP）</li>'+
    '<li><code>▶ Start</code> → 所有插槽同時推理</li>'+
    '<li>並排比較結果，查看底部 Performance Comparison 表格</li></ol>'),
  tips:refT5('<h4>Tips</h4>'+
    '<ul><li>Comparing models with the same task type lets you visually see accuracy differences</li>'+
    '<li>Compare Q-Lite vs Q-Pro to check quantization quality differences</li>'+
    '<li>More slots distribute FPS — 2 slots recommended for precise comparison</li></ul>',
    '<h4>팁</h4>'+
    '<ul><li>같은 태스크의 모델끼리 비교하면 정확도 차이를 직관적으로 볼 수 있습니다</li>'+
    '<li>Q-Lite vs Q-Pro 비교로 양자화 품질 차이를 확인하세요</li>'+
    '<li>슬롯이 많을수록 FPS가 분산됩니다 — 정밀한 비교는 2슬롯 권장</li></ul>',
    '<h4>ヒント</h4>'+
    '<ul><li>同じタスクのモデル同士を比較すると精度の違いを直感的に確認できます</li>'+
    '<li>Q-Lite vs Q-Pro を比較して量子化品質の違いを確認してください</li>'+
    '<li>スロットが多いほど FPS が分散します — 精密な比較には2スロット推奨</li></ul>',
    '<h4>提示</h4>'+
    '<ul><li>比较相同任务类型的模型可以直观地看到精度差异</li>'+
    '<li>对比 Q-Lite vs Q-Pro 以确认量化质量差异</li>'+
    '<li>槽位越多 FPS 越分散 — 精确对比建议使用2个槽位</li></ul>',
    '<h4>提示</h4>'+
    '<ul><li>比較相同任務類型的模型可以直觀地看到精確度差異</li>'+
    '<li>對比 Q-Lite vs Q-Pro 以確認量化品質差異</li>'+
    '<li>插槽越多 FPS 越分散 — 精確對比建議使用2個插槽</li></ul>')
}},

/* ── Advanced Tools ── */
{cat:'advanced',id:'modelzoo',icon:'📥',name:'ModelZoo',desc:refT5('Model download · Internal/Public · Cart','모델 다운로드 · Internal/Public · 장바구니','モデルダウンロード · Internal/Public · カート','模型下载 · Internal/Public · 购物车','模型下載 · Internal/Public · 購物車'),page:'modelzoo',tabs:{
  overview:refT5(
    '<h4>Overview</h4><p>ModelZoo is a page for browsing and downloading pre-compiled <code>.dxnn</code> models.</p>'+
    '<ul><li><strong>Internal</strong> — Internal (on-premise) model repository</li>'+
    '<li><strong>Public</strong> — Public model repository</li>'+
    '<li><strong>Task Filter</strong> — Filter by task: Detection, Classification, SR, etc.</li>'+
    '<li><strong>Cart</strong> — Select multiple models for batch download</li></ul>',
    '<h4>개요</h4><p>ModelZoo는 사전 컴파일된 <code>.dxnn</code> 모델을 검색하고 다운로드하는 페이지입니다.</p>'+
    '<ul><li><strong>Internal</strong> — 폐쇄망(사내) 모델 저장소</li>'+
    '<li><strong>Public</strong> — 외부 공개 모델 저장소</li>'+
    '<li><strong>태스크 필터</strong> — Detection, Classification, SR 등 태스크별 필터</li>'+
    '<li><strong>장바구니</strong> — 여러 모델을 선택하여 일괄 다운로드</li></ul>',
    '<h4>概要</h4><p>ModelZooはコンパイル済みの<code>.dxnn</code>モデルを検索・ダウンロードするページです。</p>'+
    '<ul><li><strong>Internal</strong> — クローズドネットワーク（社内）モデルリポジトリ</li>'+
    '<li><strong>Public</strong> — 外部公開モデルリポジトリ</li>'+
    '<li><strong>タスクフィルター</strong> — Detection、Classification、SR等のタスク別フィルター</li>'+
    '<li><strong>カート</strong> — 複数モデルを選択して一括ダウンロード</li></ul>',
    '<h4>概述</h4><p>ModelZoo 是用于搜索和下载预编译 <code>.dxnn</code> 模型的页面。</p>'+
    '<ul><li><strong>Internal</strong> — 内网（企业内部）模型仓库</li>'+
    '<li><strong>Public</strong> — 外部公开模型仓库</li>'+
    '<li><strong>任务筛选</strong> — 按 Detection、Classification、SR 等任务筛选</li>'+
    '<li><strong>购物车</strong> — 选择多个模型批量下载</li></ul>',
    '<h4>概述</h4><p>ModelZoo 是用於搜尋和下載預編譯 <code>.dxnn</code> 模型的頁面。</p>'+
    '<ul><li><strong>Internal</strong> — 封閉網路（企業內部）模型儲存庫</li>'+
    '<li><strong>Public</strong> — 外部公開模型儲存庫</li>'+
    '<li><strong>任務篩選</strong> — 依 Detection、Classification、SR 等任務篩選</li>'+
    '<li><strong>購物車</strong> — 選擇多個模型批次下載</li></ul>'),
  params:refT5(
    '<h4>Model Variations</h4>'+
    '<table class="ref-tbl"><tr><th>Type</th><th>Quantization</th><th>Characteristics</th></tr>'+
    '<tr><td>Q-Lite</td><td>Light quantization</td><td>Faster speed, slight accuracy loss</td></tr>'+
    '<tr><td>Q-Pro</td><td>Precision quantization</td><td>Higher accuracy, slight speed loss</td></tr></table>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>Click the <strong>Q-Lite</strong> / <strong>Q-Pro</strong> buttons on each model card individually, or add to <strong>Cart (🛒)</strong> for batch download.</span></div>',
    '<h4>모델 바리에이션</h4>'+
    '<table class="ref-tbl"><tr><th>유형</th><th>양자화</th><th>특징</th></tr>'+
    '<tr><td>Q-Lite</td><td>가벼운 양자화</td><td>빠른 속도, 약간의 정확도 감소</td></tr>'+
    '<tr><td>Q-Pro</td><td>정밀 양자화</td><td>높은 정확도, 약간의 속도 감소</td></tr></table>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>각 모델 카드의 <strong>Q-Lite</strong> / <strong>Q-Pro</strong> 버튼을 개별 클릭하거나, <strong>장바구니(🛒)</strong>에 추가하여 일괄 다운로드할 수 있습니다.</span></div>',
    '<h4>モデルバリエーション</h4>'+
    '<table class="ref-tbl"><tr><th>タイプ</th><th>量子化</th><th>特徴</th></tr>'+
    '<tr><td>Q-Lite</td><td>軽量量子化</td><td>高速、わずかな精度低下</td></tr>'+
    '<tr><td>Q-Pro</td><td>精密量子化</td><td>高精度、わずかな速度低下</td></tr></table>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>各モデルカードの<strong>Q-Lite</strong> / <strong>Q-Pro</strong>ボタンを個別にクリックするか、<strong>カート（🛒）</strong>に追加して一括ダウンロードできます。</span></div>',
    '<h4>模型变体</h4>'+
    '<table class="ref-tbl"><tr><th>类型</th><th>量化</th><th>特点</th></tr>'+
    '<tr><td>Q-Lite</td><td>轻量量化</td><td>速度快，精度略有下降</td></tr>'+
    '<tr><td>Q-Pro</td><td>精密量化</td><td>精度高，速度略有下降</td></tr></table>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>点击各模型卡片上的 <strong>Q-Lite</strong> / <strong>Q-Pro</strong> 按钮单独下载，或添加到<strong>购物车（🛒）</strong>批量下载。</span></div>',
    '<h4>模型變體</h4>'+
    '<table class="ref-tbl"><tr><th>類型</th><th>量化</th><th>特點</th></tr>'+
    '<tr><td>Q-Lite</td><td>輕量量化</td><td>速度快，精度略有下降</td></tr>'+
    '<tr><td>Q-Pro</td><td>精密量化</td><td>精度高，速度略有下降</td></tr></table>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>點擊各模型卡片上的 <strong>Q-Lite</strong> / <strong>Q-Pro</strong> 按鈕單獨下載，或加入<strong>購物車（🛒）</strong>批次下載。</span></div>'),
  tips:refT5(
    '<h4>Tips</h4>'+
    '<ul><li>In a closed network, only the <strong>Internal</strong> tab is available</li>'+
    '<li>After download, models appear immediately on the Models page</li>'+
    '<li>The search bar searches model names, task names, and descriptions</li></ul>',
    '<h4>팁</h4>'+
    '<ul><li>폐쇄망에서는 <strong>Internal</strong> 탭만 사용 가능합니다</li>'+
    '<li>다운로드 완료 후 Models 페이지에서 바로 확인됩니다</li>'+
    '<li>검색창은 모델명, 태스크명, 설명 모두 검색합니다</li></ul>',
    '<h4>ヒント</h4>'+
    '<ul><li>クローズドネットワークでは<strong>Internal</strong>タブのみ使用可能です</li>'+
    '<li>ダウンロード完了後、Modelsページですぐに確認できます</li>'+
    '<li>検索バーはモデル名、タスク名、説明をすべて検索します</li></ul>',
    '<h4>提示</h4>'+
    '<ul><li>内网环境下仅可使用 <strong>Internal</strong> 标签</li>'+
    '<li>下载完成后可在 Models 页面立即查看</li>'+
    '<li>搜索栏可搜索模型名、任务名和描述</li></ul>',
    '<h4>提示</h4>'+
    '<ul><li>封閉網路環境下僅可使用 <strong>Internal</strong> 標籤</li>'+
    '<li>下載完成後可在 Models 頁面立即查看</li>'+
    '<li>搜尋欄可搜尋模型名、任務名和描述</li></ul>')
}},

{cat:'advanced',id:'outputs',icon:'📂',name:'Outputs',desc:refT5('Inference result history · Image/Video viewer','추론 결과 이력 · 이미지/비디오 뷰어','推論結果履歴 · 画像/動画ビューア','推理结果历史 · 图像/视频查看器','推論結果歷史 · 圖片/影片檢視器'),page:'outputs',tabs:{
  overview:refT5(
    '<h4>Overview</h4><p>The Outputs page is a file browser for storing and exploring all inference execution results.</p>'+
    '<ul><li><strong>Result Images/Videos</strong> — Thumbnail previews of inference results + click to enlarge</li>'+
    '<li><strong>Metadata</strong> — Displays model used, parameters, and execution time</li>'+
    '<li><strong>Sort/Filter</strong> — Sort and filter by date, model name, or task</li>'+
    '<li><strong>Delete</strong> — Delete unnecessary results</li></ul>',
    '<h4>개요</h4><p>Outputs 페이지는 모든 추론 실행 결과를 저장하고 탐색하는 파일 브라우저입니다.</p>'+
    '<ul><li><strong>결과 이미지/비디오</strong> — 추론 결과물 썸네일 미리보기 + 클릭 시 확대</li>'+
    '<li><strong>메타데이터</strong> — 사용 모델, 파라미터, 실행 시간 표시</li>'+
    '<li><strong>정렬/필터</strong> — 날짜, 모델명, 태스크별 정렬 및 필터링</li>'+
    '<li><strong>삭제</strong> — 불필요한 결과 삭제</li></ul>',
    '<h4>概要</h4><p>Outputsページは、すべての推論実行結果を保存・閲覧するファイルブラウザです。</p>'+
    '<ul><li><strong>結果画像/動画</strong> — 推論結果のサムネイルプレビュー＋クリックで拡大</li>'+
    '<li><strong>メタデータ</strong> — 使用モデル、パラメータ、実行時間を表示</li>'+
    '<li><strong>ソート/フィルター</strong> — 日付、モデル名、タスク別にソート・フィルタリング</li>'+
    '<li><strong>削除</strong> — 不要な結果を削除</li></ul>',
    '<h4>概述</h4><p>Outputs 页面是用于存储和浏览所有推理执行结果的文件浏览器。</p>'+
    '<ul><li><strong>结果图像/视频</strong> — 推理结果缩略图预览 + 点击放大</li>'+
    '<li><strong>元数据</strong> — 显示使用的模型、参数和执行时间</li>'+
    '<li><strong>排序/筛选</strong> — 按日期、模型名、任务排序和筛选</li>'+
    '<li><strong>删除</strong> — 删除不需要的结果</li></ul>',
    '<h4>概述</h4><p>Outputs 頁面是用於儲存和瀏覽所有推論執行結果的檔案瀏覽器。</p>'+
    '<ul><li><strong>結果圖片/影片</strong> — 推論結果縮圖預覽 + 點擊放大</li>'+
    '<li><strong>中繼資料</strong> — 顯示使用的模型、參數和執行時間</li>'+
    '<li><strong>排序/篩選</strong> — 依日期、模型名、任務排序和篩選</li>'+
    '<li><strong>刪除</strong> — 刪除不需要的結果</li></ul>'),
  tips:refT5(
    '<h4>Tips</h4>'+
    '<ul><li>Results are saved in the <code>outputs/</code> directory</li>'+
    '<li>Benchmark reports can also be viewed here</li></ul>',
    '<h4>팁</h4>'+
    '<ul><li>결과물은 <code>outputs/</code> 디렉터리에 저장됩니다</li>'+
    '<li>Benchmark 리포트도 이곳에서 확인 가능합니다</li></ul>',
    '<h4>ヒント</h4>'+
    '<ul><li>結果は<code>outputs/</code>ディレクトリに保存されます</li>'+
    '<li>ベンチマークレポートもここで確認できます</li></ul>',
    '<h4>提示</h4>'+
    '<ul><li>结果保存在 <code>outputs/</code> 目录中</li>'+
    '<li>Benchmark 报告也可在此查看</li></ul>',
    '<h4>提示</h4>'+
    '<ul><li>結果儲存在 <code>outputs/</code> 目錄中</li>'+
    '<li>Benchmark 報告也可在此查看</li></ul>')
}},

{cat:'advanced',id:'pipeline',icon:'🔗',name:'Pipeline (Waterfall)',desc:refT5('Inference pipeline performance analysis · Bottleneck detection','추론 파이프라인 성능 분석 · 병목 감지','推論パイプライン性能分析 · ボトルネック検出','推理流水线性能分析 · 瓶颈检测','推論流水線效能分析 · 瓶頸偵測'),page:null,tabs:{
  overview:refT5(
    '<h4>Overview</h4><p>The <strong>Waterfall Chart</strong> on the Run / Benchmark / Compare pages visually displays the time spent on each stage of the inference pipeline.</p>'+
    '<ul><li><strong>Read</strong> — Read input data <span style="background:var(--info);color:#000;padding:1px 6px;border-radius:3px;font-size:11px">Blue</span></li>'+
    '<li><strong>Preprocess</strong> — Preprocessing (Resize, Normalize, etc.) <span style="background:var(--app-accent);color:#000;padding:1px 6px;border-radius:3px;font-size:11px">Light blue</span></li>'+
    '<li><strong>Inference</strong> — NPU inference execution <span style="background:var(--warning);color:#000;padding:1px 6px;border-radius:3px;font-size:11px">Yellow</span></li>'+
    '<li><strong>Postprocess</strong> — Post-processing (NMS, visualization, etc.) <span style="background:var(--error);color:#000;padding:1px 6px;border-radius:3px;font-size:11px">Red</span></li></ul>',
    '<h4>개요</h4><p>Run / Benchmark / Compare 페이지의 <strong>Waterfall Chart</strong>는 추론 파이프라인의 각 단계별 소요 시간을 시각적으로 표시합니다.</p>'+
    '<ul><li><strong>Read</strong> — 입력 data 읽기 <span style="background:var(--info);color:#000;padding:1px 6px;border-radius:3px;font-size:11px">파란색</span></li>'+
    '<li><strong>Preprocess</strong> — 전처리 (Resize, Normalize 등) <span style="background:var(--app-accent);color:#000;padding:1px 6px;border-radius:3px;font-size:11px">밝은파랑</span></li>'+
    '<li><strong>Inference</strong> — NPU 추론 실행 <span style="background:var(--warning);color:#000;padding:1px 6px;border-radius:3px;font-size:11px">노란색</span></li>'+
    '<li><strong>Postprocess</strong> — 후처리 (NMS, 시각화 등) <span style="background:var(--error);color:#000;padding:1px 6px;border-radius:3px;font-size:11px">빨간색</span></li></ul>',
    '<h4>概要</h4><p>Run / Benchmark / Compareページの<strong>Waterfall Chart</strong>は、推論パイプラインの各ステージの所要時間を視覚的に表示します。</p>'+
    '<ul><li><strong>Read</strong> — 入力データの読み込み <span style="background:var(--info);color:#000;padding:1px 6px;border-radius:3px;font-size:11px">青</span></li>'+
    '<li><strong>Preprocess</strong> — 前処理（Resize、Normalize等） <span style="background:var(--app-accent);color:#000;padding:1px 6px;border-radius:3px;font-size:11px">水色</span></li>'+
    '<li><strong>Inference</strong> — NPU推論実行 <span style="background:var(--warning);color:#000;padding:1px 6px;border-radius:3px;font-size:11px">黄色</span></li>'+
    '<li><strong>Postprocess</strong> — 後処理（NMS、可視化等） <span style="background:var(--error);color:#000;padding:1px 6px;border-radius:3px;font-size:11px">赤</span></li></ul>',
    '<h4>概述</h4><p>Run / Benchmark / Compare 页面的 <strong>Waterfall Chart</strong> 以可视化方式显示推理流水线各阶段的耗时。</p>'+
    '<ul><li><strong>Read</strong> — 读取输入数据 <span style="background:var(--info);color:#000;padding:1px 6px;border-radius:3px;font-size:11px">蓝色</span></li>'+
    '<li><strong>Preprocess</strong> — 预处理（Resize、Normalize 等） <span style="background:var(--app-accent);color:#000;padding:1px 6px;border-radius:3px;font-size:11px">浅蓝</span></li>'+
    '<li><strong>Inference</strong> — NPU 推理执行 <span style="background:var(--warning);color:#000;padding:1px 6px;border-radius:3px;font-size:11px">黄色</span></li>'+
    '<li><strong>Postprocess</strong> — 后处理（NMS、可视化等） <span style="background:var(--error);color:#000;padding:1px 6px;border-radius:3px;font-size:11px">红色</span></li></ul>',
    '<h4>概述</h4><p>Run / Benchmark / Compare 頁面的 <strong>Waterfall Chart</strong> 以視覺化方式顯示推論流水線各階段的耗時。</p>'+
    '<ul><li><strong>Read</strong> — 讀取輸入資料 <span style="background:var(--info);color:#000;padding:1px 6px;border-radius:3px;font-size:11px">藍色</span></li>'+
    '<li><strong>Preprocess</strong> — 前處理（Resize、Normalize 等） <span style="background:var(--app-accent);color:#000;padding:1px 6px;border-radius:3px;font-size:11px">淺藍</span></li>'+
    '<li><strong>Inference</strong> — NPU 推論執行 <span style="background:var(--warning);color:#000;padding:1px 6px;border-radius:3px;font-size:11px">黃色</span></li>'+
    '<li><strong>Postprocess</strong> — 後處理（NMS、視覺化等） <span style="background:var(--error);color:#000;padding:1px 6px;border-radius:3px;font-size:11px">紅色</span></li></ul>'),
  params:refT5(
    '<h4>Bottleneck Indicator</h4>'+
    '<p>The stage with the longest duration is marked with a <strong>diagonal stripe pattern</strong>. A <code>▲ bottleneck</code> tag also appears in the Legend.</p>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>Identifying the bottleneck stage helps determine optimization direction. e.g., Preprocess bottleneck → optimize preprocessing code / Inference bottleneck → consider model lightweighting</span></div>',
    '<h4>병목(Bottleneck) 표시</h4>'+
    '<p>가장 소요 시간이 긴 단계에는 <strong>빗금 패턴(diagonal stripe)</strong>이 표시됩니다. Legend에도 <code>▲ bottleneck</code> 태그가 붙습니다.</p>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>병목 단계를 식별하면 최적화 방향을 결정할 수 있습니다. 예: Preprocess 병목 → 전처리 코드 최적화 / Inference 병목 → 모델 경량화 검토</span></div>',
    '<h4>ボトルネック表示</h4>'+
    '<p>最も所要時間が長いステージには<strong>斜線パターン（diagonal stripe）</strong>が表示されます。Legendにも<code>▲ bottleneck</code>タグが付きます。</p>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>ボトルネックステージを特定すると最適化の方向性を決定できます。例：Preprocessボトルネック → 前処理コードの最適化 / Inferenceボトルネック → モデル軽量化の検討</span></div>',
    '<h4>瓶颈指示</h4>'+
    '<p>耗时最长的阶段会显示<strong>斜线图案（diagonal stripe）</strong>。Legend 中也会标注 <code>▲ bottleneck</code> 标签。</p>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>识别瓶颈阶段有助于确定优化方向。例：Preprocess 瓶颈 → 优化预处理代码 / Inference 瓶颈 → 考虑模型轻量化</span></div>',
    '<h4>瓶頸指示</h4>'+
    '<p>耗時最長的階段會顯示<strong>斜線圖案（diagonal stripe）</strong>。Legend 中也會標註 <code>▲ bottleneck</code> 標籤。</p>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>識別瓶頸階段有助於確定優化方向。例：Preprocess 瓶頸 → 優化前處理程式碼 / Inference 瓶頸 → 考慮模型輕量化</span></div>'),
  tips:refT5(
    '<h4>Tips</h4>'+
    '<ul><li>Colors for each stage are fixed — only the bottleneck is highlighted with a stripe pattern</li>'+
    '<li>Since NPU cores process in parallel, inference time may not scale linearly with batch size</li></ul>',
    '<h4>팁</h4>'+
    '<ul><li>각 단계의 색상은 고정입니다 — 병목만 빗금 패턴으로 강조</li>'+
    '<li>NPU 코어가 병렬 처리하므로 Inference 시간은 배치 크기에 비례하지 않을 수 있습니다</li></ul>',
    '<h4>ヒント</h4>'+
    '<ul><li>各ステージの色は固定です — ボトルネックのみ斜線パターンで強調されます</li>'+
    '<li>NPUコアが並列処理するため、Inference時間はバッチサイズに比例しない場合があります</li></ul>',
    '<h4>提示</h4>'+
    '<ul><li>各阶段的颜色是固定的 — 仅瓶颈以斜线图案高亮显示</li>'+
    '<li>由于 NPU 核心并行处理，Inference 时间可能不与批量大小成正比</li></ul>',
    '<h4>提示</h4>'+
    '<ul><li>各階段的顏色是固定的 — 僅瓶頸以斜線圖案高亮顯示</li>'+
    '<li>由於 NPU 核心並行處理，Inference 時間可能不與批次大小成正比</li></ul>')
}},

/* ── System & Extras ── */
{cat:'system',id:'shortcuts',icon:'⌨️',name:refT5('Keyboard Shortcuts','키보드 단축키','キーボードショートカット','键盘快捷键','鍵盤快捷鍵'),desc:refT5('Global shortcuts · Tutorial controls','전역 단축키 · 튜토리얼 제어','グローバルショートカット · チュートリアル制御','全局快捷键 · 教程控制','全域快捷鍵 · 教學控制'),page:null,tabs:{
  overview:refT5(
    '<h4>Global Shortcuts</h4>'+
    '<table class="ref-tbl"><tr><th>Key</th><th>Action</th><th>Context</th></tr>'+
    '<tr><td><span class="ref-kbd">Esc</span></td><td>Exit tutorial / Close TOC / Close modal</td><td>Global</td></tr>'+
    '<tr><td><span class="ref-kbd">←</span></td><td>Previous step</td><td>During tutorial</td></tr>'+
    '<tr><td><span class="ref-kbd">→</span></td><td>Next step</td><td>During tutorial</td></tr>'+
    '<tr><td><span class="ref-kbd">Enter</span></td><td>Next step / Confirm</td><td>During tutorial</td></tr></table>',
    '<h4>전역 단축키</h4>'+
    '<table class="ref-tbl"><tr><th>키</th><th>동작</th><th>컨텍스트</th></tr>'+
    '<tr><td><span class="ref-kbd">Esc</span></td><td>튜토리얼 종료 / TOC 닫기 / 모달 닫기</td><td>전역</td></tr>'+
    '<tr><td><span class="ref-kbd">←</span></td><td>이전 단계</td><td>튜토리얼 진행 중</td></tr>'+
    '<tr><td><span class="ref-kbd">→</span></td><td>다음 단계</td><td>튜토리얼 진행 중</td></tr>'+
    '<tr><td><span class="ref-kbd">Enter</span></td><td>다음 단계 / 확인</td><td>튜토리얼 진행 중</td></tr></table>',
    '<h4>グローバルショートカット</h4>'+
    '<table class="ref-tbl"><tr><th>キー</th><th>動作</th><th>コンテキスト</th></tr>'+
    '<tr><td><span class="ref-kbd">Esc</span></td><td>チュートリアル終了 / TOC閉じる / モーダル閉じる</td><td>グローバル</td></tr>'+
    '<tr><td><span class="ref-kbd">←</span></td><td>前のステップ</td><td>チュートリアル進行中</td></tr>'+
    '<tr><td><span class="ref-kbd">→</span></td><td>次のステップ</td><td>チュートリアル進行中</td></tr>'+
    '<tr><td><span class="ref-kbd">Enter</span></td><td>次のステップ / 確認</td><td>チュートリアル進行中</td></tr></table>',
    '<h4>全局快捷键</h4>'+
    '<table class="ref-tbl"><tr><th>按键</th><th>操作</th><th>上下文</th></tr>'+
    '<tr><td><span class="ref-kbd">Esc</span></td><td>退出教程 / 关闭目录 / 关闭弹窗</td><td>全局</td></tr>'+
    '<tr><td><span class="ref-kbd">←</span></td><td>上一步</td><td>教程进行中</td></tr>'+
    '<tr><td><span class="ref-kbd">→</span></td><td>下一步</td><td>教程进行中</td></tr>'+
    '<tr><td><span class="ref-kbd">Enter</span></td><td>下一步 / 确认</td><td>教程进行中</td></tr></table>',
    '<h4>全域快捷鍵</h4>'+
    '<table class="ref-tbl"><tr><th>按鍵</th><th>操作</th><th>上下文</th></tr>'+
    '<tr><td><span class="ref-kbd">Esc</span></td><td>結束教學 / 關閉目錄 / 關閉彈窗</td><td>全域</td></tr>'+
    '<tr><td><span class="ref-kbd">←</span></td><td>上一步</td><td>教學進行中</td></tr>'+
    '<tr><td><span class="ref-kbd">→</span></td><td>下一步</td><td>教學進行中</td></tr>'+
    '<tr><td><span class="ref-kbd">Enter</span></td><td>下一步 / 確認</td><td>教學進行中</td></tr></table>'),
  tips:refT5(
    '<h4>Tips</h4>'+
    '<ul><li>Use the TOC (table of contents) button <span class="ref-kbd">☰</span> in the tutorial to view the overall structure</li>'+
    '<li>The <strong>🎓 Tutorial</strong> button opens the guide for the current page</li></ul>',
    '<h4>팁</h4>'+
    '<ul><li>튜토리얼의 TOC(목차) 버튼 <span class="ref-kbd">☰</span>으로 전체 구조를 확인할 수 있습니다</li>'+
    '<li><strong>🎓 튜토리얼</strong> 버튼으로 현재 페이지의 가이드를 열 수 있습니다</li></ul>',
    '<h4>ヒント</h4>'+
    '<ul><li>チュートリアルのTOC（目次）ボタン <span class="ref-kbd">☰</span> で全体構造を確認できます</li>'+
    '<li><strong>🎓 チュートリアル</strong> ボタンで現在のページのガイドを開けます</li></ul>',
    '<h4>提示</h4>'+
    '<ul><li>使用教程中的目录按钮 <span class="ref-kbd">☰</span> 可查看整体结构</li>'+
    '<li><strong>🎓 教程</strong> 按钮会打开当前页面的指南</li></ul>',
    '<h4>提示</h4>'+
    '<ul><li>使用教學中的目錄按鈕 <span class="ref-kbd">☰</span> 可查看整體結構</li>'+
    '<li><strong>🎓 教學</strong> 按鈕會開啟目前頁面的指南</li></ul>',
    '<h4>Consejos</h4>'+
    '<ul><li>Use el botón TOC (tabla de contenidos) <span class="ref-kbd">☰</span> del tutorial para ver la estructura general</li>'+
    '<li>El botón <strong>🎓 Tutorial</strong> abre la guía de la página actual</li></ul>')
}},

{cat:'system',id:'themes-i18n',icon:'🎨',name:refT5('Theme & Language','테마 & 언어','テーマ & 言語','主题与语言','主題與語言'),desc:refT5('Dark/Light theme · Language switching','다크/라이트 테마 · 한국어/영어 전환','ダーク/ライトテーマ · 言語切替','深色/浅色主题 · 语言切换','深色/淺色主題 · 語言切換'),page:null,tabs:{
  overview:refT5(
    '<h4>Theme</h4>'+
    '<p>Toggle between dark/light themes using the 🌙/☀️ icon in the upper right. All components are automatically applied via CSS variables.</p>'+
    '<h4>Internationalization (i18n)</h4>'+
    '<p>Switch languages using the <strong>🌐 KO / EN</strong> toggle in the left sidebar or top bar.</p>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>DX-APP uses the <code>T(en, ko)</code> function.</span></div>',
    '<h4>테마</h4>'+
    '<p>우측 상단 🌙/☀️ 아이콘으로 다크/라이트 테마를 전환합니다. CSS 변수 기반으로 모든 컴포넌트가 자동 적용됩니다.</p>'+
    '<h4>다국어 (i18n)</h4>'+
    '<p>좌측 사이드바 또는 상단 바의 <strong>🌐 KO / EN</strong> 토글로 언어를 전환합니다.</p>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>DX-APP은 <code>T(en, ko)</code> 함수를 사용합니다.</span></div>',
    '<h4>テーマ</h4>'+
    '<p>右上の🌙/☀️アイコンでダーク/ライトテーマを切り替えます。CSS変数ベースですべてのコンポーネントが自動適用されます。</p>'+
    '<h4>多言語対応（i18n）</h4>'+
    '<p>左サイドバーまたはトップバーの<strong>🌐 KO / EN</strong>トグルで言語を切り替えます。</p>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>DX-APPは<code>T(en, ko)</code>関数を使用します。</span></div>',
    '<h4>主题</h4>'+
    '<p>通过右上角的 🌙/☀️ 图标切换深色/浅色主题。基于 CSS 变量，所有组件自动适配。</p>'+
    '<h4>国际化（i18n）</h4>'+
    '<p>通过左侧边栏或顶部栏的 <strong>🌐 KO / EN</strong> 开关切换语言。</p>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>DX-APP 使用 <code>T(en, ko)</code> 函数。</span></div>',
    '<h4>主題</h4>'+
    '<p>透過右上角的 🌙/☀️ 圖示切換深色/淺色主題。基於 CSS 變數，所有元件自動適配。</p>'+
    '<h4>國際化（i18n）</h4>'+
    '<p>透過左側邊欄或頂部列的 <strong>🌐 KO / EN</strong> 開關切換語言。</p>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>DX-APP 使用 <code>T(en, ko)</code> 函式。</span></div>'),
  tips:refT5(
    '<h4>Tips</h4>'+
    '<ul><li>Theme settings are saved in <code>localStorage</code> and persist after refresh</li>'+
    '<li>Not all text may be fully translated</li></ul>',
    '<h4>팁</h4>'+
    '<ul><li>테마 설정은 <code>localStorage</code>에 저장되어 새로고침 후에도 유지됩니다</li>'+
    '<li>모든 텍스트가 완벽히 번역되어 있지는 않을 수 있습니다</li></ul>',
    '<h4>ヒント</h4>'+
    '<ul><li>テーマ設定は<code>localStorage</code>に保存され、リロード後も維持されます</li>'+
    '<li>すべてのテキストが完全に翻訳されているとは限りません</li></ul>',
    '<h4>提示</h4>'+
    '<ul><li>主题设置保存在 <code>localStorage</code> 中，刷新后仍会保留</li>'+
    '<li>并非所有文本都已完全翻译</li></ul>',
    '<h4>提示</h4>'+
    '<ul><li>主題設定儲存在 <code>localStorage</code> 中，重新整理後仍會保留</li>'+
    '<li>並非所有文字都已完全翻譯</li></ul>')
}},

{cat:'system',id:'global-features',icon:'🔧',name:refT5('Global Features','글로벌 기능','グローバル機能','全局功能','全域功能'),desc:refT5('Toast notifications · Navigation · Sidebar','Toast 알림 · 네비게이션 · 사이드바','Toast通知 · ナビゲーション · サイドバー','Toast 通知 · 导航 · 侧边栏','Toast 通知 · 導覽 · 側邊欄'),page:null,tabs:{
  overview:refT5(
    '<h4>Toast Notifications</h4>'+
    '<p>Operation results (success/failure/warning/info) are displayed as Toast messages in the lower right. They disappear automatically and can also be dismissed by clicking.</p>'+
    '<h4>Navigation</h4>'+
    '<ul><li><strong>Left Sidebar</strong> — Icon-based menu, page navigation</li>'+
    '<li><strong>Top Bar</strong> — Current page title, breadcrumbs, theme/language toggle</li>'+
    '<li><strong>SPA Mode</strong> — Smooth page transitions without full page reload</li></ul>'+
    '<h4>Tutorial System</h4>'+
    '<ul><li>Top-right <strong>🎓 Tutorial</strong> button → Start the interactive guide for the current page</li>'+
    '<li>Tutorials guide you step-by-step with highlights and tooltips</li>'+
    '<li>Jump directly to any section via the TOC (table of contents)</li></ul>',
    '<h4>Toast 알림</h4>'+
    '<p>작업 결과(성공/실패/경고/정보)가 우측 하단에 Toast 메시지로 표시됩니다. 자동으로 사라지며, 클릭하여 닫을 수도 있습니다.</p>'+
    '<h4>네비게이션</h4>'+
    '<ul><li><strong>좌측 사이드바</strong> — 아이콘 기반 메뉴, 페이지 전환</li>'+
    '<li><strong>상단 바</strong> — 현재 페이지 제목, 빵크럼, 테마/언어 토글</li>'+
    '<li><strong>SPA 방식</strong> — 페이지 전환 시 새로고침 없이 부드러운 전환</li></ul>'+
    '<h4>튜토리얼 시스템</h4>'+
    '<ul><li>우측 상단 <strong>🎓 튜토리얼</strong> 버튼 → 현재 페이지의 대화형 가이드 시작</li>'+
    '<li>튜토리얼은 하이라이트 + 툴팁으로 단계별 안내</li>'+
    '<li>TOC(목차)에서 원하는 섹션으로 직접 이동 가능</li></ul>',
    '<h4>Toast通知</h4>'+
    '<p>操作結果（成功/失敗/警告/情報）が右下にToastメッセージで表示されます。自動的に消えますが、クリックして閉じることもできます。</p>'+
    '<h4>ナビゲーション</h4>'+
    '<ul><li><strong>左サイドバー</strong> — アイコンベースのメニュー、ページ切替</li>'+
    '<li><strong>トップバー</strong> — 現在のページタイトル、パンくずリスト、テーマ/言語トグル</li>'+
    '<li><strong>SPA方式</strong> — ページ遷移時にリロードなしのスムーズな切替</li></ul>'+
    '<h4>チュートリアルシステム</h4>'+
    '<ul><li>右上の <strong>🎓 チュートリアル</strong> ボタン → 現在のページのガイドを開始</li>'+
    '<li>チュートリアルはハイライト＋ツールチップでステップバイステップで案内</li>'+
    '<li>TOC（目次）から任意のセクションに直接ジャンプ可能</li></ul>',
    '<h4>Toast 通知</h4>'+
    '<p>操作结果（成功/失败/警告/信息）以 Toast 消息形式显示在右下角。会自动消失，也可点击关闭。</p>'+
    '<h4>导航</h4>'+
    '<ul><li><strong>左侧边栏</strong> — 基于图标的菜单，页面切换</li>'+
    '<li><strong>顶部栏</strong> — 当前页面标题、面包屑、主题/语言开关</li>'+
    '<li><strong>SPA 模式</strong> — 页面切换时无需刷新，平滑过渡</li></ul>'+
    '<h4>教程系统</h4>'+
    '<ul><li>右上角 <strong>🎓 教程</strong> 按钮 → 启动当前页面的交互式指南</li>'+
    '<li>教程通过高亮和工具提示逐步引导</li>'+
    '<li>可通过目录直接跳转到任意章节</li></ul>',
    '<h4>Toast 通知</h4>'+
    '<p>操作結果（成功/失敗/警告/資訊）以 Toast 訊息形式顯示在右下角。會自動消失，也可點擊關閉。</p>'+
    '<h4>導覽</h4>'+
    '<ul><li><strong>左側邊欄</strong> — 基於圖示的選單，頁面切換</li>'+
    '<li><strong>頂部列</strong> — 目前頁面標題、麵包屑、主題/語言開關</li>'+
    '<li><strong>SPA 模式</strong> — 頁面切換時無需重新整理，平滑過渡</li></ul>'+
    '<h4>教學系統</h4>'+
    '<ul><li>右上角 <strong>🎓 教學</strong> 按鈕 → 啟動目前頁面的互動式指南</li>'+
    '<li>教學透過高亮和工具提示逐步引導</li>'+
    '<li>可透過目錄直接跳轉到任意章節</li></ul>',
    '<h4>Notificaciones Toast</h4>'+
    '<p>Los resultados de las operaciones (éxito, error, advertencia, información) se muestran como mensajes Toast abajo a la derecha. Desaparecen automáticamente y también se pueden cerrar con un clic.</p>'+
    '<h4>Navegación</h4>'+
    '<ul><li><strong>Barra lateral izquierda</strong> — Menú basado en iconos, cambio de página</li>'+
    '<li><strong>Barra superior</strong> — Título de la página, migas de pan, tema/idioma</li>'+
    '<li><strong>Modo SPA</strong> — Transiciones suaves sin recargar la página</li></ul>'+
    '<h4>Sistema de tutorial</h4>'+
    '<ul><li>Botón <strong>🎓 Tutorial</strong> arriba a la derecha → Inicia la guía interactiva de la página actual</li>'+
    '<li>Los tutoriales guían paso a paso con resaltados y tooltips</li>'+
    '<li>Salte a cualquier sección desde el TOC (tabla de contenidos)</li></ul>'),
  tips:refT5(
    '<h4>Tips</h4>'+
    '<ul><li>All async operations (benchmark, compile, download, etc.) show progress and Toast notifications for status updates</li>'+
    '<li>Click on error Toasts to see detailed information</li></ul>',
    '<h4>팁</h4>'+
    '<ul><li>모든 비동기 작업(벤치마크, 컴파일, 다운로드 등)은 진행률 표시와 Toast 알림으로 상태를 알려줍니다</li>'+
    '<li>에러 발생 시 Toast를 클릭하면 상세 내용을 확인할 수 있습니다</li></ul>',
    '<h4>ヒント</h4>'+
    '<ul><li>すべての非同期操作（ベンチマーク、コンパイル、ダウンロード等）は進捗表示とToast通知でステータスを通知します</li>'+
    '<li>エラー発生時はToastをクリックすると詳細を確認できます</li></ul>',
    '<h4>提示</h4>'+
    '<ul><li>所有异步操作（Benchmark、编译、下载等）都会通过进度条和 Toast 通知显示状态</li>'+
    '<li>发生错误时，点击 Toast 可查看详细信息</li></ul>',
    '<h4>提示</h4>'+
    '<ul><li>所有非同步操作（Benchmark、編譯、下載等）都會透過進度條和 Toast 通知顯示狀態</li>'+
    '<li>發生錯誤時，點擊 Toast 可查看詳細資訊</li></ul>')
}},

{cat:'system',id:'api-endpoints',icon:'🌐',name:'API Endpoints',desc:refT5('Backend REST API reference','Backend REST API 레퍼런스','バックエンド REST API リファレンス','后端 REST API 参考','後端 REST API 參考'),page:null,tabs:{
  overview:refT5(
    '<h4>Key API Endpoints</h4>'+
    '<table class="ref-tbl"><tr><th>Method</th><th>Endpoint</th><th>Description</th></tr>'+
    '<tr><td><span class="ref-api-method ref-api-get">GET</span></td><td class="mono">/api/models</td><td>Returns list of deployed models</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-get">GET</span></td><td class="mono">/api/system</td><td>System information (CPU, Memory, NPU, etc.)</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-post">POST</span></td><td class="mono">/api/inference/single</td><td>Execute single inference</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-post">POST</span></td><td class="mono">/api/inference/continuous</td><td>Start/stop continuous inference</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-post">POST</span></td><td class="mono">/api/benchmark</td><td>Execute benchmark</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-get">GET</span></td><td class="mono">/api/npu/status</td><td>NPU status (temperature, utilization, etc.)</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-post">POST</span></td><td class="mono">/api/compile</td><td>ONNX compile request</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-get">GET</span></td><td class="mono">/api/outputs</td><td>List of inference results</td></tr></table>',
    '<h4>주요 API 엔드포인트</h4>'+
    '<table class="ref-tbl"><tr><th>Method</th><th>Endpoint</th><th>설명</th></tr>'+
    '<tr><td><span class="ref-api-method ref-api-get">GET</span></td><td class="mono">/api/models</td><td>배포된 모델 목록 반환</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-get">GET</span></td><td class="mono">/api/system</td><td>시스템 정보 (CPU, Memory, NPU 등)</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-post">POST</span></td><td class="mono">/api/inference/single</td><td>Single 추론 실행</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-post">POST</span></td><td class="mono">/api/inference/continuous</td><td>Continuous 추론 시작/중지</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-post">POST</span></td><td class="mono">/api/benchmark</td><td>벤치마크 실행</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-get">GET</span></td><td class="mono">/api/npu/status</td><td>NPU 상태 (온도, 사용률 등)</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-post">POST</span></td><td class="mono">/api/compile</td><td>ONNX 컴파일 요청</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-get">GET</span></td><td class="mono">/api/outputs</td><td>추론 결과 목록</td></tr></table>',
    '<h4>主要APIエンドポイント</h4>'+
    '<table class="ref-tbl"><tr><th>Method</th><th>Endpoint</th><th>説明</th></tr>'+
    '<tr><td><span class="ref-api-method ref-api-get">GET</span></td><td class="mono">/api/models</td><td>デプロイ済みモデル一覧を返す</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-get">GET</span></td><td class="mono">/api/system</td><td>システム情報（CPU、メモリ、NPU等）</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-post">POST</span></td><td class="mono">/api/inference/single</td><td>Single推論実行</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-post">POST</span></td><td class="mono">/api/inference/continuous</td><td>Continuous推論の開始/停止</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-post">POST</span></td><td class="mono">/api/benchmark</td><td>ベンチマーク実行</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-get">GET</span></td><td class="mono">/api/npu/status</td><td>NPUステータス（温度、使用率等）</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-post">POST</span></td><td class="mono">/api/compile</td><td>ONNXコンパイルリクエスト</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-get">GET</span></td><td class="mono">/api/outputs</td><td>推論結果一覧</td></tr></table>',
    '<h4>主要 API 端点</h4>'+
    '<table class="ref-tbl"><tr><th>Method</th><th>Endpoint</th><th>说明</th></tr>'+
    '<tr><td><span class="ref-api-method ref-api-get">GET</span></td><td class="mono">/api/models</td><td>返回已部署的模型列表</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-get">GET</span></td><td class="mono">/api/system</td><td>系统信息（CPU、内存、NPU 等）</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-post">POST</span></td><td class="mono">/api/inference/single</td><td>执行 Single 推理</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-post">POST</span></td><td class="mono">/api/inference/continuous</td><td>启动/停止 Continuous 推理</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-post">POST</span></td><td class="mono">/api/benchmark</td><td>执行 Benchmark</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-get">GET</span></td><td class="mono">/api/npu/status</td><td>NPU 状态（温度、使用率等）</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-post">POST</span></td><td class="mono">/api/compile</td><td>ONNX 编译请求</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-get">GET</span></td><td class="mono">/api/outputs</td><td>推理结果列表</td></tr></table>',
    '<h4>主要 API 端點</h4>'+
    '<table class="ref-tbl"><tr><th>Method</th><th>Endpoint</th><th>說明</th></tr>'+
    '<tr><td><span class="ref-api-method ref-api-get">GET</span></td><td class="mono">/api/models</td><td>傳回已部署的模型清單</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-get">GET</span></td><td class="mono">/api/system</td><td>系統資訊（CPU、記憶體、NPU 等）</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-post">POST</span></td><td class="mono">/api/inference/single</td><td>執行 Single 推論</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-post">POST</span></td><td class="mono">/api/inference/continuous</td><td>啟動/停止 Continuous 推論</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-post">POST</span></td><td class="mono">/api/benchmark</td><td>執行 Benchmark</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-get">GET</span></td><td class="mono">/api/npu/status</td><td>NPU 狀態（溫度、使用率等）</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-post">POST</span></td><td class="mono">/api/compile</td><td>ONNX 編譯請求</td></tr>'+
    '<tr><td><span class="ref-api-method ref-api-get">GET</span></td><td class="mono">/api/outputs</td><td>推論結果清單</td></tr></table>'),
  tips:refT5(
    '<h4>Developer Tips</h4>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>All APIs are based on <code>'+apiBase+'</code>. You can call the same endpoints used by the GUI directly with <code>curl</code>, etc.</span></div>'+
    '<ul><li>Responses are in JSON format</li>'+
    '<li>File uploads use <code>multipart/form-data</code> format</li></ul>',
    '<h4>개발자 팁</h4>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>모든 API는 <code>'+apiBase+'</code> 기반입니다. GUI에서 사용하는 것과 동일한 엔드포인트를 <code>curl</code> 등으로 직접 호출할 수 있습니다.</span></div>'+
    '<ul><li>응답은 JSON 형식입니다</li>'+
    '<li>파일 업로드는 <code>multipart/form-data</code> 형식입니다</li></ul>',
    '<h4>開発者向けヒント</h4>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>すべてのAPIは<code>'+apiBase+'</code>ベースです。GUIで使用しているのと同じエンドポイントを<code>curl</code>等で直接呼び出せます。</span></div>'+
    '<ul><li>レスポンスはJSON形式です</li>'+
    '<li>ファイルアップロードは<code>multipart/form-data</code>形式です</li></ul>',
    '<h4>开发者提示</h4>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>所有 API 基于 <code>'+apiBase+'</code>。可以使用 <code>curl</code> 等工具直接调用与 GUI 相同的端点。</span></div>'+
    '<ul><li>响应为 JSON 格式</li>'+
    '<li>文件上传使用 <code>multipart/form-data</code> 格式</li></ul>',
    '<h4>開發者提示</h4>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>所有 API 基於 <code>'+apiBase+'</code>。可以使用 <code>curl</code> 等工具直接呼叫與 GUI 相同的端點。</span></div>'+
    '<ul><li>回應為 JSON 格式</li>'+
    '<li>檔案上傳使用 <code>multipart/form-data</code> 格式</li></ul>',
    '<h4>Consejos para desarrolladores</h4>'+
    '<div class="ref-box tip"><span class="ref-box-icon">💡</span><span>Todas las API usan <code>'+apiBase+'</code> como base. Puede llamar directamente los mismos endpoints que usa la GUI con <code>curl</code>, etc.</span></div>'+
    '<ul><li>Las respuestas están en formato JSON</li>'+
    '<li>Las cargas de archivos usan <code>multipart/form-data</code></li></ul>')
}}
];}
var _SEC=buildRefSections();

/* ════════════  RENDER  ════════════ */
function renderRef(){
  var mainEl=document.getElementById('ref-content');
  if(!mainEl) return;

  /* ── Search placeholder i18n ── */
  var searchEl=document.getElementById('ref-search');
  if(searchEl) searchEl.placeholder=refT5('Search documentation...','문서 검색...','ドキュメント検索...','搜索文档...','搜尋文件...');

  /* ── Category chips ── */
  var chipEl=document.getElementById('ref-filter-bar');
  if(chipEl){
    var chipH='<button class="chip active" data-ref-cat-filter="all">'+ refT5('All','전체','すべて','全部','全部') +'</button>';
    _CAT.forEach(function(c){
      chipH+='<button class="chip" data-ref-cat-filter="'+c.id+'">'+c.title+'</button>';
    });
    chipEl.innerHTML=chipH;
  }

  /* ── Topic cards grouped by category ── */
  var mH='';
  _CAT.forEach(function(c){
    mH+='<div class="ref-cat" id="ref-cat-'+c.id+'" data-ref-cat="'+c.id+'" data-help-id="ref-category-'+c.id+'"><div class="ref-cat-title">'+c.title+'</div><div class="ref-cat-desc">'+c.desc+'</div></div>';
    mH+='<div class="ref-card-row" data-ref-cat="'+c.id+'">';
    _SEC.forEach(function(s){
      if(s.cat!==c.id) return;
      mH+='<button class="ref-topic-card" id="ref-sec-'+s.id+'" data-ref-cat="'+s.cat+'" data-ref-id="'+s.id+'" data-help-id="ref-topic-'+s.id+'">'+
        '<span class="ref-section-icon">'+s.icon+'</span>'+
        '<span class="ref-section-info"><span class="ref-section-name">'+s.name+'</span><span class="ref-section-desc">'+s.desc+'</span></span>'+
      '</button>';
    });
    mH+='</div>';
  });
  mainEl.innerHTML=mH;
}

/* ════════════  INTERACTIONS  ════════════ */

function _refBuildDetail(s){
  var tabKeys=Object.keys(s.tabs);
  var tabLabels={overview:'📋 '+refT5('Overview','개요','概要','概述','概述'),params:'⚙️ '+refT5('Parameters','파라미터','パラメータ','参数','參數'),workflow:'🔄 '+refT5('Workflow','워크플로우','ワークフロー','工作流','工作流程'),tips:'💡 '+refT5('Tips','팁','ヒント','提示','提示')};
  var navLabel=refT5(' → Go to page',' 페이지로 →',' ページへ →',' → 前往页面',' → 前往頁面');
  var goBtn=s.page?'<button class="btn btn-ghost btn-sm" onclick="if(typeof nav===\'function\')nav(\''+s.page+'\')">'+s.name+navLabel+'</button>':'';
  var h='<div class="ref-detail-hd"><div><div class="ref-detail-kicker">'+ refT5('Reference','레퍼런스','リファレンス','参考','參考') +'</div><h2>'+s.icon+' '+s.name+'</h2><p>'+s.desc+'</p></div>'+goBtn+'</div>';
  h+='<div class="ref-tabs" data-ref-tabs="'+s.id+'">';
  tabKeys.forEach(function(k,i){h+='<div class="ref-tab'+(i===0?' active':'')+'" data-ref-tab="'+s.id+'-'+k+'">'+((tabLabels[k])||k)+'</div>';});
  h+='</div>';
  tabKeys.forEach(function(k,i){h+='<div class="ref-tab-content'+(i===0?' active':'')+'" data-ref-panel="'+s.id+'-'+k+'">'+s.tabs[k]+'</div>';});
  return h;
}

function selectRefSection(secId,card){
  var selected=null;
  _SEC.forEach(function(s){if(s.id===secId) selected=s;});
  if(!selected) return;

  /* 같은 카드 다시 클릭 → 닫기 */
  if(card&&card.classList.contains('active')){closeRefDetail();return;}

  /* 기존 확장 패널 제거 */
  var old=document.getElementById('ref-expand');
  if(old) old.remove();

  /* 활성 카드 표시 */
  document.querySelectorAll('.ref-topic-card').forEach(function(c){c.classList.remove('active');});
  if(card) card.classList.add('active');

  /* 확장 패널 생성 */
  var expand=document.createElement('div');
  expand.className='ref-expand';expand.id='ref-expand';

  /* 화살표 */
  var arrow=document.createElement('div');
  arrow.className='ref-expand-arrow';
  var row=card?card.closest('.ref-card-row'):null;
  if(row){
    var rowRect=row.getBoundingClientRect();
    var cardRect=card.getBoundingClientRect();
    arrow.style.left=(cardRect.left-rowRect.left+cardRect.width/2-8)+'px';
  }
  expand.appendChild(arrow);

  /* 닫기 버튼 */
  var closeBtn=document.createElement('button');
  closeBtn.className='ref-expand-close';closeBtn.textContent='✕';
    expand.appendChild(closeBtn);

  /* 상세 내용 */
  var inner=document.createElement('div');
  inner.className='ref-expand-inner';inner.id='ref-detail';
  inner.innerHTML=_refBuildDetail(selected);
  expand.appendChild(inner);

  /* 카드 행 바로 뒤에 삽입 */
  if(row&&row.nextSibling) row.parentNode.insertBefore(expand,row.nextSibling);
  else if(row) row.parentNode.appendChild(expand);

  setTimeout(function(){expand.scrollIntoView({behavior:'smooth',block:'nearest'});},50);
};

/* ── Close expand panel ── */
function closeRefDetail(){
  var ex=document.getElementById('ref-expand');
  if(ex) ex.remove();
  document.querySelectorAll('.ref-topic-card').forEach(function(c){c.classList.remove('active');});
};


/* ── Sub-tab switching ── */
function selectRefTab(el,secId,tabKey){
  var detail=document.getElementById('ref-detail');
  if(!detail) return;
  detail.querySelectorAll('.ref-tab').forEach(function(t){t.classList.remove('active');});
  detail.querySelectorAll('.ref-tab-content').forEach(function(p){p.classList.remove('active');});
  el.classList.add('active');
  var panel=detail.querySelector('[data-ref-panel="'+secId+'-'+tabKey+'"]');
  if(panel) panel.classList.add('active');
};

/* ── Category filter ── */
function filterRefCategory(catId,btn){
  closeRefDetail();
  document.querySelectorAll('#ref-filter-bar .chip').forEach(function(chip){chip.classList.remove('active');});
  if(btn) btn.classList.add('active');
  document.querySelectorAll('.ref-cat,.ref-card-row').forEach(function(el){
    var match=catId==='all'||el.getAttribute('data-ref-cat')===catId||el.id==='ref-cat-'+catId;
    el.style.display=match?'':'none';
  });
  /* 카드 행 내부 카드도 모두 보이게 */
  document.querySelectorAll('.ref-topic-card').forEach(function(c){c.style.display='';});
  var searchInput=document.getElementById('ref-search');
  if(searchInput) searchInput.value='';
};

/* ════════════  EVENT DELEGATION  ════════════ */

function bindEvents(){
  var bar=document.getElementById('ref-filter-bar');
  if(bar&&!bar._dxBound){
    bar._dxBound=true;
    bar.addEventListener('click',function(e){
      var chip=e.target.closest('[data-ref-cat-filter]');
      if(!chip)return;
      filterRefCategory(chip.dataset.refCatFilter,chip);
    });
  }
  var content=document.getElementById('ref-content');
  if(content&&!content._dxBound){
    content._dxBound=true;
    content.addEventListener('click',function(e){
      var card=e.target.closest('[data-ref-id]');
      var tab=e.target.closest('[data-ref-tab]');
      var close=e.target.closest('.ref-expand-close');
      if(close){closeRefDetail();return;}
      if(tab){
        var refTab=tab.dataset.refTab||'';
        var lastHyphen=refTab.lastIndexOf('-');
        if(lastHyphen>0){
          selectRefTab(tab,refTab.slice(0,lastHyphen),refTab.slice(lastHyphen+1));
        }
        return;
      }
      if(card){selectRefSection(card.dataset.refId,card);}
    });
  }
  var searchInput=document.getElementById('ref-search');
  if(searchInput&&!searchInput._dxBound){
    searchInput._dxBound=true;
    searchInput.addEventListener('input',function(){

  closeRefDetail();
  var q=this.value.toLowerCase().trim();
  document.querySelectorAll('#ref-filter-bar .chip').forEach(function(chip){chip.classList.toggle('active',chip.dataset.refCatFilter==='all');});
  document.querySelectorAll('.ref-topic-card').forEach(function(s){
    s.style.display=q&&!s.textContent.toLowerCase().includes(q)?'none':'';
  });
  /* 카드가 없는 카테고리+행 숨기기 */
  document.querySelectorAll('.ref-card-row').forEach(function(row){
    var catId=row.getAttribute('data-ref-cat');
    var hasVisible=false;
    row.querySelectorAll('.ref-topic-card').forEach(function(s){
      if(s.style.display!=='none') hasVisible=true;
    });
    row.style.display=hasVisible?'':'none';
    var catEl=document.getElementById('ref-cat-'+catId);
    if(catEl) catEl.style.display=hasVisible?'':'none';
  });

    });
  }
  if(!document._dxEscBound){
    document._dxEscBound=true;
    document.addEventListener('keydown',function(e){if(e.key==='Escape') closeRefDetail();});
  }
}

function init(){renderRef();bindEvents();}

window.DXAppReference={
  init:init,
  render:renderRef,
  _test:{
    refT5:refT5,
    buildRefCategories:buildRefCategories,
    buildRefSections:buildRefSections
  }
};

if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);
else init();
if(window.DXI18n&&DXI18n.onLangChange){
  DXI18n.onLangChange(function(){
    _CAT=buildRefCategories(); _SEC=buildRefSections();
    closeRefDetail();
    window.DXAppReference.render();
  });
}
})();
