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

/* ════════════  DATA  ════════════
   여섯 언어를 한 자리에 — 예전에는 refT5 (en · ko · ja · zh-CN · zh-TW) 로 스페인어가 없었고, 화면과 다른
   사실 (설정 카드 5개, 없는 API · RTSP 입력 칸, 틀린 기본값) 이 많았다. 사실은 코드와 대조했다
   (release audit A-9, 2026-10-02). 값이 언어와 무관하면 문자열 하나, 아니면 { en, ko, ja, 'zh-CN', 'zh-TW', es }. */
function refL(o){
  if(o==null) return '';
  if(typeof o!=='object') return String(o);
  var lang=(window.DXI18n&&DXI18n.lang)||localStorage.getItem('dx-lang')||'en';
  return o[lang]||o.en||'';
}
function _rH4(t){return '<h4>'+refL(t)+'</h4>';}
function _rP(t){return '<p>'+refL(t)+'</p>';}
function _rList(tag,items){return '<'+tag+'>'+items.map(function(i){return '<li>'+refL(i)+'</li>';}).join('')+'</'+tag+'>';}
function _rBox(kind,t){return '<div class="ref-box '+kind+'"><span class="ref-box-icon">'+DXIcon(kind==='warn'?'alert':'info')+'</span><span>'+refL(t)+'</span></div>';}
function _rFlow(steps){return '<div class="ref-flow">'+steps.map(function(s){return '<span class="ref-flow-step">'+refL(s)+'</span>';}).join('<span class="ref-flow-arrow">→</span>')+'</div>';}
function _rTbl(head,rows){
  return '<table class="ref-tbl"><tr>'+head.map(function(h){return '<th>'+refL(h)+'</th>';}).join('')+'</tr>'+
    rows.map(function(r){return '<tr>'+r.map(function(c){return '<td>'+refL(c)+'</td>';}).join('')+'</tr>';}).join('')+'</table>';
}
var _R={  /* 여러 곳에서 쓰는 말 */
  tips:{en:'Tips',ko:'팁',ja:'ヒント','zh-CN':'提示','zh-TW':'提示',es:'Consejos'},
  overview:{en:'Overview',ko:'개요',ja:'概要','zh-CN':'概述','zh-TW':'概述',es:'Descripción general'},
  workflow:{en:'Workflow',ko:'작업 순서',ja:'手順','zh-CN':'操作流程','zh-TW':'操作流程',es:'Flujo de trabajo'},
  step:{en:'Step',ko:'단계',ja:'ステップ','zh-CN':'步骤','zh-TW':'步驟',es:'Paso'},
  what:{en:'What it does',ko:'하는 일',ja:'内容','zh-CN':'作用','zh-TW':'作用',es:'Qué hace'},
  yes:DXIcon('check'),
  no:'—'
};

function buildRefCategories(){return [
  {id:'start',   title:refT5('Getting Started','시작하기','はじめに','快速入门','快速入門','Primeros pasos'),
   desc:refL({en:'From install to first run',ko:'설치부터 첫 실행까지',ja:'インストールから初回実行まで','zh-CN':'从安装到首次运行','zh-TW':'從安裝到首次執行',es:'De la instalación a la primera ejecución'})},
  {id:'core',    title:refL({en:'Core Features',ko:'핵심 기능',ja:'コア機能','zh-CN':'核心功能','zh-TW':'核心功能',es:'Funciones principales'}),
   desc:refL({en:'Models · Run · Benchmark · Compare',ko:'Models · Run · Benchmark · Compare',ja:'モデル · 推論 · ベンチマーク · 比較','zh-CN':'模型 · 推理 · 基准测试 · 对比','zh-TW':'模型 · 推論 · 基準測試 · 對比',es:'Modelos · Inferencia · Benchmark · Comparación'})},
  {id:'advanced',title:refL({en:'Tools & Results',ko:'도구 · 결과',ja:'ツールと結果','zh-CN':'工具与结果','zh-TW':'工具與結果',es:'Herramientas y resultados'}),
   desc:refL({en:'ModelZoo · Outputs · Compiler · Timing chart',ko:'ModelZoo · Outputs · Compiler · 단계별 시간 차트',ja:'ModelZoo · 出力 · Compiler · 時間チャート','zh-CN':'ModelZoo · 输出 · Compiler · 耗时图','zh-TW':'ModelZoo · 輸出 · Compiler · 耗時圖',es:'ModelZoo · Salidas · Compiler · Gráfico de tiempos'})},
  {id:'system',  title:refL({en:'System & Extras',ko:'시스템 · 기타',ja:'システムとその他','zh-CN':'系统与其他','zh-TW':'系統與其他',es:'Sistema y extras'}),
   desc:refL({en:'Shortcuts · Theme & language · Notifications · API',ko:'단축키 · 테마와 언어 · 알림 · API',ja:'ショートカット · テーマと言語 · 通知 · API','zh-CN':'快捷键 · 主题与语言 · 通知 · API','zh-TW':'快捷鍵 · 主題與語言 · 通知 · API',es:'Atajos · Tema e idioma · Notificaciones · API'})}
];}
var _CAT=buildRefCategories();

function buildRefSections(){
var apiBase=refApiBase();
return [
/* ── Getting Started ── */
{cat:'start',id:'quick-start',icon:'run',
 name:refL({en:'Quick Start Guide',ko:'빠른 시작 가이드',ja:'クイックスタートガイド','zh-CN':'快速入门指南','zh-TW':'快速入門指南',es:'Guía de inicio rápido'}),
 desc:refL({en:'Your first NPU inference in a few minutes',ko:'몇 분 만에 첫 NPU 추론',ja:'数分で最初の NPU 推論','zh-CN':'几分钟内完成首次 NPU 推理','zh-TW':'幾分鐘內完成首次 NPU 推論',es:'Su primera inferencia en la NPU en pocos minutos'}),
 tabs:{
  overview:_rH4(_R.overview)+
   _rP({en:'For first-time DX App users. Follow these steps in order.',ko:'DX App을 처음 쓰는 분을 위한 순서입니다. 차례대로 따라 하세요.',ja:'DX App を初めて使う方向けの手順です。順番に進めてください。','zh-CN':'适合首次使用 DX App 的用户。请按顺序进行。','zh-TW':'適合首次使用 DX App 的使用者。請依序進行。',es:'Para quienes usan DX App por primera vez. Siga estos pasos en orden.'})+
   _rFlow([{en:'1. Set up',ko:'1. 설정',ja:'1. セットアップ','zh-CN':'1. 设置','zh-TW':'1. 設定',es:'1. Configurar'},
           {en:'2. Check models',ko:'2. 모델 확인',ja:'2. モデル確認','zh-CN':'2. 检查模型','zh-TW':'2. 檢查模型',es:'2. Revisar modelos'},
           {en:'3. Run inference',ko:'3. 추론 실행',ja:'3. 推論実行','zh-CN':'3. 运行推理','zh-TW':'3. 執行推論',es:'3. Ejecutar inferencia'},
           {en:'4. See results',ko:'4. 결과 확인',ja:'4. 結果確認','zh-CN':'4. 查看结果','zh-TW':'4. 查看結果',es:'4. Ver resultados'}])+
   _rBox('tip',{en:'On the Setup page, <strong>Set up the rest</strong> runs every step that is not done yet: dependencies, runtime, driver, build and sample assets.',ko:'Setup 페이지의 <strong>나머지 설정</strong>은 아직 끝나지 않은 단계(의존성, 런타임, 드라이버, 빌드, 샘플 에셋)를 차례로 실행합니다.',ja:'Setup ページの<strong>残りをセットアップ</strong>は、まだ終わっていないステップ（依存関係・ランタイム・ドライバー・ビルド・サンプル）を順に実行します。','zh-CN':'Setup 页面的<strong>完成其余设置</strong>会依次运行尚未完成的步骤：依赖、运行时、驱动、构建和示例资源。','zh-TW':'Setup 頁面的<strong>完成其餘設定</strong>會依序執行尚未完成的步驟：相依套件、執行環境、驅動程式、建置與範例資源。',es:'En la página Setup, <strong>Configurar el resto</strong> ejecuta los pasos aún pendientes: dependencias, runtime, driver, compilación y recursos de ejemplo.'}),
  workflow:_rH4(_R.workflow)+
   _rList('ol',[
    {en:'<strong>Setup</strong> — run <strong>Set up the rest</strong>, or each step on its own. Steps that need administrator rights ask for your sudo password.',ko:'<strong>Setup</strong> — <strong>나머지 설정</strong>을 누르거나 단계를 하나씩 실행합니다. 관리자 권한이 필요한 단계는 sudo 비밀번호를 묻습니다.',ja:'<strong>Setup</strong> — <strong>残りをセットアップ</strong>を押すか、ステップを個別に実行します。管理者権限が必要なステップでは sudo パスワードを尋ねます。','zh-CN':'<strong>Setup</strong> — 点击<strong>完成其余设置</strong>，或逐个运行步骤。需要管理员权限的步骤会询问 sudo 密码。','zh-TW':'<strong>Setup</strong> — 點擊<strong>完成其餘設定</strong>，或逐一執行步驟。需要管理員權限的步驟會詢問 sudo 密碼。',es:'<strong>Setup</strong>: pulse <strong>Configurar el resto</strong> o ejecute cada paso por separado. Los pasos que requieren permisos de administrador piden la contraseña de sudo.'},
    {en:'<strong>Models</strong> — check which models are installed; download a missing one from its row or from <strong>ModelZoo</strong>.',ko:'<strong>Models</strong> — 설치된 모델을 확인하고, 없는 모델은 그 줄이나 <strong>ModelZoo</strong>에서 내려받습니다.',ja:'<strong>Models</strong> — インストール済みのモデルを確認し、足りないモデルはその行か <strong>ModelZoo</strong> からダウンロードします。','zh-CN':'<strong>Models</strong> — 查看已安装的模型；缺少的模型可在该行或 <strong>ModelZoo</strong> 中下载。','zh-TW':'<strong>Models</strong> — 查看已安裝的模型；缺少的模型可在該列或 <strong>ModelZoo</strong> 下載。',es:'<strong>Models</strong>: compruebe qué modelos están instalados y descargue los que falten desde su fila o desde <strong>ModelZoo</strong>.'},
    {en:'<strong>Run Inference</strong> → <strong>Single</strong> → choose a model and an image or video → <code>'+DXIcon('play')+' Run</code>.',ko:'<strong>Run Inference</strong> → <strong>Single</strong> → 모델과 이미지 또는 영상 선택 → <code>'+DXIcon('play')+' 실행</code>.',ja:'<strong>Run Inference</strong> → <strong>Single</strong> → モデルと画像または動画を選択 → <code>'+DXIcon('play')+' 実行</code>。','zh-CN':'<strong>Run Inference</strong> → <strong>Single</strong> → 选择模型和图片或视频 → <code>'+DXIcon('play')+' 运行</code>。','zh-TW':'<strong>Run Inference</strong> → <strong>Single</strong> → 選擇模型與圖片或影片 → <code>'+DXIcon('play')+' 執行</code>。',es:'<strong>Run Inference</strong> → <strong>Single</strong> → elija un modelo y una imagen o un video → <code>'+DXIcon('play')+' Ejecutar</code>.'},
    {en:'The result shows boxes, masks or labels. For an image, drag the <strong>Original / Result</strong> slider to compare.',ko:'결과에 박스 · 마스크 · 라벨이 그려집니다. 이미지는 <strong>원본 / 결과</strong> 슬라이더로 비교할 수 있습니다.',ja:'結果にボックス・マスク・ラベルが描かれます。画像では<strong>元画像 / 結果</strong>のスライダーで比較できます。','zh-CN':'结果中会绘制框、掩码或标签。对图片可拖动<strong>原图 / 结果</strong>滑块进行对比。','zh-TW':'結果中會繪製框、遮罩或標籤。對圖片可拖曳<strong>原圖 / 結果</strong>滑桿進行比較。',es:'El resultado muestra cuadros, máscaras o etiquetas. En una imagen, arrastre el control <strong>Original / Resultado</strong> para comparar.'},
    {en:'<strong>Outputs</strong> keeps saved result files.',ko:'저장된 결과 파일은 <strong>Outputs</strong>에 남습니다.',ja:'保存された結果ファイルは <strong>Outputs</strong> に残ります。','zh-CN':'保存的结果文件保留在 <strong>Outputs</strong> 中。','zh-TW':'儲存的結果檔案保留在 <strong>Outputs</strong> 中。',es:'<strong>Outputs</strong> conserva los archivos de resultados guardados.'}])+
   _rBox('warn',{en:'Without the NPU Linux Driver (Setup step 4), inference cannot run on the NPU.',ko:'NPU Linux Driver(Setup 4단계)가 없으면 NPU에서 추론할 수 없습니다.',ja:'NPU Linux Driver（Setup のステップ 4）がないと、NPU で推論できません。','zh-CN':'未安装 NPU Linux Driver（Setup 第 4 步）时，无法在 NPU 上推理。','zh-TW':'未安裝 NPU Linux Driver（Setup 第 4 步）時，無法在 NPU 上推論。',es:'Sin el NPU Linux Driver (paso 4 de Setup) no se puede ejecutar la inferencia en la NPU.'})
}},
{cat:'start',id:'setup-install',icon:'gear',page:'setup',
 name:refL({en:'Setup & Install',ko:'설정 · 설치',ja:'セットアップとインストール','zh-CN':'设置与安装','zh-TW':'設定與安裝',es:'Configuración e instalación'}),
 desc:refL({en:'Six steps: dependencies, runtime, driver, build, sample assets',ko:'6단계: 의존성, 런타임, 드라이버, 빌드, 샘플 에셋',ja:'6 ステップ：依存関係・ランタイム・ドライバー・ビルド・サンプル','zh-CN':'六个步骤：依赖、运行时、驱动、构建、示例资源','zh-TW':'六個步驟：相依套件、執行環境、驅動程式、建置、範例資源',es:'Seis pasos: dependencias, runtime, driver, compilación y recursos de ejemplo'}),
 tabs:{
  overview:_rH4(_R.overview)+
   _rP({en:'The Setup page prepares this PC for DX App in six steps. <strong>Set up the rest</strong> runs the steps that are not done yet, in order; each step can also be run on its own.',ko:'Setup 페이지는 6단계로 이 PC를 DX App에 맞게 준비합니다. <strong>나머지 설정</strong>은 끝나지 않은 단계를 차례로 실행하며, 단계마다 따로 실행할 수도 있습니다.',ja:'Setup ページは 6 つのステップでこの PC を DX App 用に準備します。<strong>残りをセットアップ</strong>は未完了のステップを順に実行します。ステップごとに個別に実行することもできます。','zh-CN':'Setup 页面通过六个步骤为 DX App 准备这台电脑。<strong>完成其余设置</strong>会按顺序运行尚未完成的步骤，也可以单独运行每个步骤。','zh-TW':'Setup 頁面透過六個步驟為 DX App 準備這台電腦。<strong>完成其餘設定</strong>會依序執行尚未完成的步驟，也可以個別執行每個步驟。',es:'La página Setup prepara este equipo para DX App en seis pasos. <strong>Configurar el resto</strong> ejecuta en orden los pasos pendientes; cada paso también puede ejecutarse por separado.'})+
   _rFlow(['1. DX-APP Dependencies','2. DX-Runtime Dependencies','3. DX-Runtime Build','4. NPU Linux Driver','5. DX-APP Build','6. Sample Assets Setup']),
  params:_rH4({en:'Steps',ko:'단계',ja:'ステップ','zh-CN':'步骤','zh-TW':'步驟',es:'Pasos'})+
   _rTbl([_R.step,_R.what,'sudo'],[
    ['1. DX-APP Dependencies',{en:'Build tools and libraries (cmake, gcc, ninja, OpenCV …)',ko:'빌드 도구와 라이브러리 (cmake, gcc, ninja, OpenCV …)',ja:'ビルドツールとライブラリ（cmake、gcc、ninja、OpenCV …）','zh-CN':'构建工具和库（cmake、gcc、ninja、OpenCV …）','zh-TW':'建置工具與程式庫（cmake、gcc、ninja、OpenCV …）',es:'Herramientas y bibliotecas de compilación (cmake, gcc, ninja, OpenCV…)'},_R.yes],
    ['2. DX-Runtime Dependencies',{en:'Libraries DX-RT needs',ko:'DX-RT가 쓰는 라이브러리',ja:'DX-RT が必要とするライブラリ','zh-CN':'DX-RT 所需的库','zh-TW':'DX-RT 所需的程式庫',es:'Bibliotecas que necesita DX-RT'},_R.yes],
    ['3. DX-Runtime Build',{en:'Builds DX-RT and the dx_engine Python package',ko:'DX-RT와 dx_engine Python 패키지 빌드',ja:'DX-RT と dx_engine Python パッケージをビルド','zh-CN':'构建 DX-RT 和 dx_engine Python 包','zh-TW':'建置 DX-RT 與 dx_engine Python 套件',es:'Compila DX-RT y el paquete Python dx_engine'},_R.yes],
    ['4. NPU Linux Driver',{en:'Installs the NPU kernel driver (DKMS); a reboot may be needed',ko:'NPU 커널 드라이버(DKMS) 설치 — 재부팅이 필요할 수 있습니다',ja:'NPU カーネルドライバー（DKMS）をインストール。再起動が必要な場合があります','zh-CN':'安装 NPU 内核驱动（DKMS），可能需要重启','zh-TW':'安裝 NPU 核心驅動程式（DKMS），可能需要重新開機',es:'Instala el driver del kernel de la NPU (DKMS); puede requerir reiniciar'},_R.yes],
    ['5. DX-APP Build',{en:'Builds the C++ examples',ko:'C++ 예제 빌드',ja:'C++ サンプルをビルド','zh-CN':'构建 C++ 示例','zh-TW':'建置 C++ 範例',es:'Compila los ejemplos en C++'},_R.yes],
    ['6. Sample Assets Setup',{en:'Downloads models and sample videos',ko:'모델과 샘플 영상 다운로드',ja:'モデルとサンプル動画をダウンロード','zh-CN':'下载模型和示例视频','zh-TW':'下載模型與範例影片',es:'Descarga modelos y videos de ejemplo'},_R.no]])+
   _rBox('tip',{en:'Finished steps show a check and <strong>Ready</strong>; the header counts how many are ready.',ko:'끝난 단계에는 체크와 <strong>준비됨</strong>이 표시되고, 머리글에 준비된 단계 수가 나옵니다.',ja:'完了したステップにはチェックと<strong>準備完了</strong>が表示され、見出しに準備済みの数が出ます。','zh-CN':'已完成的步骤会显示勾选和<strong>就绪</strong>，标题显示已就绪的数量。','zh-TW':'已完成的步驟會顯示勾選與<strong>就緒</strong>，標題顯示已就緒的數量。',es:'Los pasos terminados muestran una marca y <strong>Listo</strong>; el encabezado cuenta cuántos están listos.'})+
   _rBox('tip',{en:'Compiling an ONNX model to DXNN is done in the <strong>Compiler</strong> module, not on this page.',ko:'ONNX 모델을 DXNN으로 컴파일하는 일은 이 페이지가 아니라 <strong>Compiler</strong> 모듈에서 합니다.',ja:'ONNX モデルの DXNN へのコンパイルは、このページではなく <strong>Compiler</strong> モジュールで行います。','zh-CN':'将 ONNX 模型编译为 DXNN 需在 <strong>Compiler</strong> 模块中进行，而不是在本页面。','zh-TW':'將 ONNX 模型編譯為 DXNN 需在 <strong>Compiler</strong> 模組中進行，而非本頁面。',es:'La compilación de un modelo ONNX a DXNN se hace en el módulo <strong>Compiler</strong>, no en esta página.'}),
  tips:_rH4({en:'Troubleshooting',ko:'문제 해결',ja:'トラブルシューティング','zh-CN':'故障排除','zh-TW':'疑難排解',es:'Solución de problemas'})+
   _rList('ul',[
    {en:'<strong>A step failed</strong> — read its log under the step, fix the cause, and run the step again.',ko:'<strong>단계가 실패하면</strong> — 그 단계 아래의 로그를 보고 원인을 고친 뒤 다시 실행하세요.',ja:'<strong>ステップが失敗したら</strong> — ステップの下のログを確認し、原因を直してから再実行してください。','zh-CN':'<strong>步骤失败时</strong> — 查看该步骤下方的日志，排除原因后重新运行。','zh-TW':'<strong>步驟失敗時</strong> — 查看該步驟下方的記錄，排除原因後重新執行。',es:'<strong>Si un paso falla</strong>, lea su registro, corrija la causa y vuelva a ejecutarlo.'},
    {en:'<strong>Driver not loaded</strong> — check with <code>lsmod | grep -e dxrt_driver -e dx_dma</code> and look for errors in <code>dmesg</code>. Run <strong>Deep Diagnostics</strong> for details.',ko:'<strong>드라이버가 올라오지 않으면</strong> — <code>lsmod | grep -e dxrt_driver -e dx_dma</code>로 확인하고 <code>dmesg</code>에서 오류를 찾으세요. 자세한 것은 <strong>Deep Diagnostics</strong>로 봅니다.',ja:'<strong>ドライバーが読み込まれない</strong> — <code>lsmod | grep -e dxrt_driver -e dx_dma</code> で確認し、<code>dmesg</code> でエラーを探してください。詳細は <strong>Deep Diagnostics</strong> で確認できます。','zh-CN':'<strong>驱动未加载</strong> — 用 <code>lsmod | grep -e dxrt_driver -e dx_dma</code> 检查，并在 <code>dmesg</code> 中查找错误。详情可运行 <strong>Deep Diagnostics</strong>。','zh-TW':'<strong>驅動程式未載入</strong> — 用 <code>lsmod | grep -e dxrt_driver -e dx_dma</code> 檢查，並在 <code>dmesg</code> 中查找錯誤。詳情可執行 <strong>Deep Diagnostics</strong>。',es:'<strong>Driver no cargado</strong>: compruébelo con <code>lsmod | grep -e dxrt_driver -e dx_dma</code> y busque errores en <code>dmesg</code>. Para más detalle, ejecute <strong>Deep Diagnostics</strong>.'},
    {en:'On a <strong>closed network</strong>, prepare the offline packages before you start.',ko:'<strong>폐쇄망</strong>에서는 시작하기 전에 오프라인 패키지를 준비하세요.',ja:'<strong>閉域ネットワーク</strong>では、始める前にオフラインパッケージを用意してください。','zh-CN':'在<strong>封闭网络</strong>中，请在开始前准备好离线安装包。','zh-TW':'在<strong>封閉網路</strong>中，請在開始前準備好離線安裝包。',es:'En una <strong>red aislada</strong>, prepare los paquetes sin conexión antes de empezar.'}])
}},
{cat:'start',id:'deep-diagnostics',icon:'search',page:'setup',
 name:'Deep Diagnostics',
 desc:refL({en:'12 checks of hardware, driver and software',ko:'하드웨어 · 드라이버 · 소프트웨어 12개 검사',ja:'ハードウェア・ドライバー・ソフトウェアの 12 項目チェック','zh-CN':'硬件、驱动和软件的 12 项检查','zh-TW':'硬體、驅動程式與軟體的 12 項檢查',es:'12 comprobaciones de hardware, driver y software'}),
 tabs:{
  overview:_rH4(_R.overview)+
   _rP({en:'<strong>Run Diagnostics</strong> on the Setup page runs 12 checks and shows each as a passed or failed card. A failed card says how to fix it.',ko:'Setup 페이지의 <strong>진단 실행</strong>은 12개 검사를 돌려 통과 · 실패 카드로 보여 줍니다. 실패한 카드에는 고치는 방법이 나옵니다.',ja:'Setup ページの<strong>診断実行</strong>は 12 項目をチェックし、合格・不合格のカードで表示します。不合格のカードには対処方法が出ます。','zh-CN':'Setup 页面的<strong>运行诊断</strong>会执行 12 项检查，并以通过或失败卡片显示。失败的卡片会给出修复方法。','zh-TW':'Setup 頁面的<strong>執行診斷</strong>會進行 12 項檢查，並以通過或失敗卡片顯示。失敗的卡片會提供修正方法。',es:'<strong>Ejecutar diagnóstico</strong> en la página Setup realiza 12 comprobaciones y muestra cada una como tarjeta superada o fallida. Una tarjeta fallida indica cómo corregirlo.'})+
   _rFlow([DXIcon('play')+' Run Diagnostics',{en:'12 checks',ko:'12개 검사',ja:'12 項目','zh-CN':'12 项检查','zh-TW':'12 項檢查',es:'12 comprobaciones'},{en:'Pass / fail cards',ko:'통과 · 실패 카드',ja:'合格・不合格カード','zh-CN':'通过 / 失败卡片','zh-TW':'通過 / 失敗卡片',es:'Tarjetas de resultado'},{en:'Fix',ko:'해결 방법',ja:'対処方法','zh-CN':'修复方法','zh-TW':'修正方法',es:'Corrección'}]),
  params:_rH4({en:'Checks',ko:'검사 항목',ja:'チェック項目','zh-CN':'检查项','zh-TW':'檢查項目',es:'Comprobaciones'})+
   _rTbl(['#',{en:'Check',ko:'검사',ja:'チェック','zh-CN':'检查','zh-TW':'檢查',es:'Comprobación'},{en:'Passes when',ko:'통과 조건',ja:'合格条件','zh-CN':'通过条件','zh-TW':'通過條件',es:'Se supera si'}],[
    ['1','PCIe Link (DeepX)',{en:'A DEEPX NPU is found on the PCIe bus',ko:'PCIe 버스에서 DEEPX NPU가 보임',ja:'PCIe バス上に DEEPX NPU がある','zh-CN':'PCIe 总线上检测到 DEEPX NPU','zh-TW':'PCIe 匯流排上偵測到 DEEPX NPU',es:'Se detecta una NPU de DEEPX en el bus PCIe'}],
    ['2','Device Files',{en:'/dev/dxrt* or /dev/deepx* exists',ko:'/dev/dxrt* 또는 /dev/deepx* 있음',ja:'/dev/dxrt* または /dev/deepx* がある','zh-CN':'存在 /dev/dxrt* 或 /dev/deepx*','zh-TW':'存在 /dev/dxrt* 或 /dev/deepx*',es:'Existe /dev/dxrt* o /dev/deepx*'}],
    ['3','Kernel Module (dxrt_driver)',{en:'Loaded',ko:'로드됨',ja:'ロード済み','zh-CN':'已加载','zh-TW':'已載入',es:'Cargado'}],
    ['4','Kernel Module (dx_dma)',{en:'Loaded',ko:'로드됨',ja:'ロード済み','zh-CN':'已加载','zh-TW':'已載入',es:'Cargado'}],
    ['5','DKMS Driver Status',{en:'The driver is registered in DKMS',ko:'드라이버가 DKMS에 등록됨',ja:'ドライバーが DKMS に登録済み','zh-CN':'驱动已在 DKMS 中注册','zh-TW':'驅動程式已在 DKMS 中註冊',es:'El driver está registrado en DKMS'}],
    ['6','dxrt.service',{en:'The systemd service is active',ko:'systemd 서비스가 실행 중',ja:'systemd サービスが稼働中','zh-CN':'systemd 服务处于运行状态','zh-TW':'systemd 服務正在執行',es:'El servicio systemd está activo'}],
    ['7','CLI Tools',{en:'dxrt-cli, run_model, parse_model and dxtop are available',ko:'dxrt-cli, run_model, parse_model, dxtop 사용 가능',ja:'dxrt-cli・run_model・parse_model・dxtop が使える','zh-CN':'可使用 dxrt-cli、run_model、parse_model、dxtop','zh-TW':'可使用 dxrt-cli、run_model、parse_model、dxtop',es:'dxrt-cli, run_model, parse_model y dxtop están disponibles'}],
    ['8','Python venv (dx_engine)',{en:'dx_engine imports in venv-dx-runtime',ko:'venv-dx-runtime에서 dx_engine import 가능',ja:'venv-dx-runtime で dx_engine を import できる','zh-CN':'在 venv-dx-runtime 中可导入 dx_engine','zh-TW':'在 venv-dx-runtime 中可匯入 dx_engine',es:'dx_engine se importa en venv-dx-runtime'}],
    ['9','Disk Space',{en:'5 GB or more free',ko:'5 GB 이상 남음',ja:'5 GB 以上の空き','zh-CN':'可用空间 5 GB 以上','zh-TW':'可用空間 5 GB 以上',es:'5 GB o más libres'}],
    ['10','Memory',{en:'2 GB or more available',ko:'2 GB 이상 사용 가능',ja:'2 GB 以上利用可能','zh-CN':'可用内存 2 GB 以上','zh-TW':'可用記憶體 2 GB 以上',es:'2 GB o más disponibles'}],
    ['11','Model File Integrity',{en:'No empty (0-byte) .dxnn files in assets/models/',ko:'assets/models/에 0바이트 .dxnn 파일이 없음',ja:'assets/models/ に 0 バイトの .dxnn がない','zh-CN':'assets/models/ 中没有 0 字节的 .dxnn 文件','zh-TW':'assets/models/ 中沒有 0 位元組的 .dxnn 檔',es:'No hay archivos .dxnn vacíos (0 bytes) en assets/models/'}],
    ['12','OpenCV',{en:'cv2 imports',ko:'cv2 import 가능',ja:'cv2 を import できる','zh-CN':'可导入 cv2','zh-TW':'可匯入 cv2',es:'cv2 se importa'}]]),
  tips:_rH4(_R.tips)+
   _rList('ul',[
    {en:'Run it after Setup is complete for the most useful result.',ko:'Setup을 마친 뒤에 실행해야 결과가 가장 쓸모 있습니다.',ja:'Setup を終えてから実行すると最も役に立ちます。','zh-CN':'完成 Setup 后再运行，结果最有参考价值。','zh-TW':'完成 Setup 後再執行，結果最有參考價值。',es:'Ejecútelo después de completar Setup para obtener el resultado más útil.'},
    {en:'Some checks call system tools (lspci, lsmod, dkms, systemctl), so a full run can take several seconds.',ko:'일부 검사는 시스템 도구(lspci, lsmod, dkms, systemctl)를 부르므로 전체 실행에 몇 초가 걸릴 수 있습니다.',ja:'一部のチェックはシステムツール（lspci・lsmod・dkms・systemctl）を呼ぶため、全体で数秒かかることがあります。','zh-CN':'部分检查会调用系统工具（lspci、lsmod、dkms、systemctl），完整运行可能需要几秒钟。','zh-TW':'部分檢查會呼叫系統工具（lspci、lsmod、dkms、systemctl），完整執行可能需要數秒。',es:'Algunas comprobaciones usan herramientas del sistema (lspci, lsmod, dkms, systemctl), así que la ejecución completa puede tardar unos segundos.'}])
}},

/* ── Core ── */
{cat:'core',id:'models',icon:'folder',page:'models',
 name:'Models',
 desc:refL({en:'Every model in the catalog: install state, details, download',ko:'카탈로그의 모든 모델: 설치 상태 · 상세 · 다운로드',ja:'カタログの全モデル：インストール状態・詳細・ダウンロード','zh-CN':'目录中的全部模型：安装状态、详情、下载','zh-TW':'目錄中的全部模型：安裝狀態、詳情、下載',es:'Todos los modelos del catálogo: estado, detalles y descarga'}),
 tabs:{
  overview:_rH4(_R.overview)+
   _rP({en:'The Models page lists models in a table: name, category, C++ and Python examples, run mode, metadata and file.',ko:'Models 페이지는 모델을 표로 보여 줍니다: 이름, 분류, C++ · Python 예제, 실행 모드, 메타데이터, 파일.',ja:'Models ページはモデルを表で表示します：名前・カテゴリ・C++ / Python サンプル・実行モード・メタデータ・ファイル。','zh-CN':'Models 页面以表格列出模型：名称、类别、C++ 与 Python 示例、运行模式、元数据和文件。','zh-TW':'Models 頁面以表格列出模型：名稱、類別、C++ 與 Python 範例、執行模式、中繼資料與檔案。',es:'La página Models muestra los modelos en una tabla: nombre, categoría, ejemplos en C++ y Python, modo de ejecución, metadatos y archivo.'})+
   _rList('ul',[
    {en:'<strong>Category chips and search</strong> narrow the list.',ko:'<strong>분류 칩과 검색</strong>으로 목록을 좁힙니다.',ja:'<strong>カテゴリのチップと検索</strong>で一覧を絞り込みます。','zh-CN':'用<strong>类别标签和搜索</strong>缩小列表。','zh-TW':'用<strong>類別標籤與搜尋</strong>縮小清單。',es:'Los <strong>chips de categoría y la búsqueda</strong> filtran la lista.'},
    {en:'<strong>Detail</strong> opens the model\'s information.',ko:'<strong>Detail</strong>은 모델 정보를 엽니다.',ja:'<strong>Detail</strong> でモデル情報を開きます。','zh-CN':'<strong>Detail</strong> 打开模型信息。','zh-TW':'<strong>Detail</strong> 開啟模型資訊。',es:'<strong>Detail</strong> abre la información del modelo.'},
    {en:'<strong>Download</strong> / <strong>Re-download</strong> fetches the .dxnn file.',ko:'<strong>Download</strong> / <strong>Re-download</strong>로 .dxnn 파일을 받습니다.',ja:'<strong>Download</strong> / <strong>Re-download</strong> で .dxnn ファイルを取得します。','zh-CN':'<strong>Download</strong> / <strong>Re-download</strong> 获取 .dxnn 文件。','zh-TW':'<strong>Download</strong> / <strong>Re-download</strong> 取得 .dxnn 檔案。',es:'<strong>Download</strong> / <strong>Re-download</strong> obtiene el archivo .dxnn.'},
    {en:'<strong>Run</strong> opens Run Inference with that model.',ko:'<strong>Run</strong>은 그 모델로 Run Inference를 엽니다.',ja:'<strong>Run</strong> はそのモデルで Run Inference を開きます。','zh-CN':'<strong>Run</strong> 以该模型打开 Run Inference。','zh-TW':'<strong>Run</strong> 以該模型開啟 Run Inference。',es:'<strong>Run</strong> abre Run Inference con ese modelo.'}]),
  tips:_rH4(_R.tips)+
   _rList('ul',[
    {en:'<strong>Graph</strong> opens the model graph in the Compiler viewer; it is offered for ONNX files.',ko:'<strong>Graph</strong>는 Compiler 뷰어에서 모델 그래프를 엽니다. ONNX 파일에서 쓸 수 있습니다.',ja:'<strong>Graph</strong> は Compiler ビューアでモデルグラフを開きます。ONNX ファイルで使えます。','zh-CN':'<strong>Graph</strong> 在 Compiler 查看器中打开模型图，适用于 ONNX 文件。','zh-TW':'<strong>Graph</strong> 在 Compiler 檢視器中開啟模型圖，適用於 ONNX 檔案。',es:'<strong>Graph</strong> abre el grafo del modelo en el visor de Compiler; está disponible para archivos ONNX.'},
    {en:'To get many models at once, use <strong>ModelZoo</strong>.',ko:'여러 모델을 한꺼번에 받으려면 <strong>ModelZoo</strong>를 쓰세요.',ja:'多くのモデルをまとめて取得するには <strong>ModelZoo</strong> を使います。','zh-CN':'要一次获取多个模型，请使用 <strong>ModelZoo</strong>。','zh-TW':'要一次取得多個模型，請使用 <strong>ModelZoo</strong>。',es:'Para obtener muchos modelos a la vez, use <strong>ModelZoo</strong>.'}])
}},
{cat:'core',id:'run-inference',icon:'play',page:'run',
 name:'Run Inference',
 desc:refL({en:'Single and Continuous runs, thresholds, export',ko:'Single · Continuous 실행, 임계값, 내보내기',ja:'Single / Continuous 実行・しきい値・エクスポート','zh-CN':'Single 与 Continuous 运行、阈值、导出','zh-TW':'Single 與 Continuous 執行、閾值、匯出',es:'Ejecuciones Single y Continuous, umbrales y exportación'}),
 tabs:{
  overview:_rH4(_R.overview)+
   _rList('ul',[
    {en:'<strong>Single</strong> — one image or one video.',ko:'<strong>Single</strong> — 이미지 하나 또는 영상 하나.',ja:'<strong>Single</strong> — 画像 1 枚または動画 1 本。','zh-CN':'<strong>Single</strong> — 一张图片或一个视频。','zh-TW':'<strong>Single</strong> — 一張圖片或一部影片。',es:'<strong>Single</strong>: una imagen o un video.'},
    {en:'<strong>Continuous</strong> — video, camera or RTSP, up to 8 slots at once.',ko:'<strong>Continuous</strong> — 영상 · 카메라 · RTSP, 최대 8개 슬롯 동시 실행.',ja:'<strong>Continuous</strong> — 動画・カメラ・RTSP、最大 8 スロットを同時実行。','zh-CN':'<strong>Continuous</strong> — 视频、摄像头或 RTSP，最多同时 8 个槽位。','zh-TW':'<strong>Continuous</strong> — 影片、攝影機或 RTSP，最多同時 8 個槽位。',es:'<strong>Continuous</strong>: video, cámara o RTSP, hasta 8 ranuras a la vez.'}])+
   _rFlow([{en:'Model',ko:'모델',ja:'モデル','zh-CN':'模型','zh-TW':'模型',es:'Modelo'},{en:'Input',ko:'입력',ja:'入力','zh-CN':'输入','zh-TW':'輸入',es:'Entrada'},{en:'Parameters',ko:'파라미터',ja:'パラメーター','zh-CN':'参数','zh-TW':'參數',es:'Parámetros'},DXIcon('play')+' Run',{en:'Result',ko:'결과',ja:'結果','zh-CN':'结果','zh-TW':'結果',es:'Resultado'}]),
  params:_rH4({en:'Parameters',ko:'파라미터',ja:'パラメーター','zh-CN':'参数','zh-TW':'參數',es:'Parámetros'})+
   _rTbl([{en:'Parameter',ko:'파라미터',ja:'パラメーター','zh-CN':'参数','zh-TW':'參數',es:'Parámetro'},{en:'Range',ko:'범위',ja:'範囲','zh-CN':'范围','zh-TW':'範圍',es:'Rango'},{en:'Default',ko:'기본값',ja:'既定値','zh-CN':'默认值','zh-TW':'預設值',es:'Predeterminado'},{en:'Meaning',ko:'뜻',ja:'意味','zh-CN':'含义','zh-TW':'含義',es:'Significado'}],[
    ['Confidence Threshold','0 – 1','0.25',{en:'Lowest score a detection must have',ko:'남길 검출의 최소 점수',ja:'残す検出の最低スコア','zh-CN':'保留检测结果的最低分数','zh-TW':'保留偵測結果的最低分數',es:'Puntuación mínima de una detección'}],
    ['NMS IoU','0 – 1','0.45',{en:'Overlap above which duplicate boxes are merged',ko:'이보다 많이 겹치는 중복 박스를 합침',ja:'これ以上重なる重複ボックスをまとめる','zh-CN':'重叠超过该值的重复框会被合并','zh-TW':'重疊超過此值的重複框會被合併',es:'Solapamiento a partir del cual se fusionan cuadros duplicados'}],
    ['Objectness','0 – 1','0.25',{en:'Shown for models that use it',ko:'이 값을 쓰는 모델에서만 보임',ja:'この値を使うモデルでのみ表示','zh-CN':'仅在使用该值的模型中显示','zh-TW':'僅在使用此值的模型中顯示',es:'Se muestra en los modelos que lo usan'}],
    ['Top-K','1 – 1000','5',{en:'How many classes a classifier lists',ko:'분류 모델이 보여 줄 클래스 수',ja:'分類モデルが表示するクラス数','zh-CN':'分类模型列出的类别数','zh-TW':'分類模型列出的類別數',es:'Cuántas clases muestra un clasificador'}],
    ['Overlay Alpha','0 – 1','0.6',{en:'Opacity of masks drawn on the image',ko:'이미지에 그리는 마스크의 불투명도',ja:'画像に描くマスクの不透明度','zh-CN':'绘制在图像上的掩码不透明度','zh-TW':'繪製在影像上的遮罩不透明度',es:'Opacidad de las máscaras dibujadas'}]])+
   _rBox('tip',{en:'When a model\'s config.json has its own values, they are filled in.',ko:'모델의 config.json에 값이 있으면 그 값으로 채워집니다.',ja:'モデルの config.json に値があれば、その値が入ります。','zh-CN':'若模型的 config.json 中有自己的值，会自动填入。','zh-TW':'若模型的 config.json 中有自己的值，會自動填入。',es:'Si el config.json del modelo tiene valores propios, se usan esos.'})+
   _rH4({en:'Inputs',ko:'입력',ja:'入力','zh-CN':'输入','zh-TW':'輸入',es:'Entradas'})+
   _rTbl([{en:'Input',ko:'입력',ja:'入力','zh-CN':'输入','zh-TW':'輸入',es:'Entrada'},{en:'Mode',ko:'모드',ja:'モード','zh-CN':'模式','zh-TW':'模式',es:'Modo'}],[
    [{en:'Image',ko:'이미지',ja:'画像','zh-CN':'图片','zh-TW':'圖片',es:'Imagen'},'Single'],
    [{en:'Video file',ko:'영상 파일',ja:'動画ファイル','zh-CN':'视频文件','zh-TW':'影片檔',es:'Archivo de video'},'Single · Continuous'],
    [{en:'Camera (/dev/video*)',ko:'카메라 (/dev/video*)',ja:'カメラ（/dev/video*）','zh-CN':'摄像头（/dev/video*）','zh-TW':'攝影機（/dev/video*）',es:'Cámara (/dev/video*)'},'Continuous'],
    ['RTSP','Continuous']]),
  workflow:_rH4('Single')+
   _rList('ol',[
    {en:'Choose a model and an image or video.',ko:'모델과 이미지 또는 영상을 고릅니다.',ja:'モデルと画像または動画を選びます。','zh-CN':'选择模型以及图片或视频。','zh-TW':'選擇模型以及圖片或影片。',es:'Elija un modelo y una imagen o un video.'},
    {en:'Adjust the parameters if needed and press <code>'+DXIcon('play')+' Run</code>.',ko:'필요하면 파라미터를 바꾸고 <code>'+DXIcon('play')+' 실행</code>을 누릅니다.',ja:'必要ならパラメーターを調整し、<code>'+DXIcon('play')+' 実行</code>を押します。','zh-CN':'如有需要调整参数，然后点击 <code>'+DXIcon('play')+' 运行</code>。','zh-TW':'如有需要調整參數，然後點擊 <code>'+DXIcon('play')+' 執行</code>。',es:'Ajuste los parámetros si hace falta y pulse <code>'+DXIcon('play')+' Ejecutar</code>.'},
    {en:'The result appears with the time per stage. For an image, compare with the <strong>Original / Result</strong> slider.',ko:'결과와 함께 단계별 시간이 나옵니다. 이미지는 <strong>원본 / 결과</strong> 슬라이더로 비교합니다.',ja:'結果とステップごとの時間が表示されます。画像は<strong>元画像 / 結果</strong>のスライダーで比較します。','zh-CN':'结果会连同各阶段耗时一起显示。图片可用<strong>原图 / 结果</strong>滑块对比。','zh-TW':'結果會連同各階段耗時一起顯示。圖片可用<strong>原圖 / 結果</strong>滑桿比較。',es:'El resultado aparece con el tiempo de cada etapa. En una imagen, compare con el control <strong>Original / Resultado</strong>.'}])+
   _rH4('Continuous')+
   _rList('ol',[
    {en:'Open the <strong>Continuous</strong> tab and add slots (up to 8).',ko:'<strong>Continuous</strong> 탭에서 슬롯을 추가합니다(최대 8개).',ja:'<strong>Continuous</strong> タブでスロットを追加します（最大 8）。','zh-CN':'打开 <strong>Continuous</strong> 标签并添加槽位（最多 8 个）。','zh-TW':'開啟 <strong>Continuous</strong> 分頁並新增槽位（最多 8 個）。',es:'Abra la pestaña <strong>Continuous</strong> y añada ranuras (hasta 8).'},
    {en:'Pick a model and an input for each slot, then press <code>'+DXIcon('play')+' Start</code>.',ko:'슬롯마다 모델과 입력을 고르고 <code>'+DXIcon('play')+' 시작</code>을 누릅니다.',ja:'スロットごとにモデルと入力を選び、<code>'+DXIcon('play')+' 開始</code>を押します。','zh-CN':'为每个槽位选择模型和输入，然后点击 <code>'+DXIcon('play')+' 开始</code>。','zh-TW':'為每個槽位選擇模型與輸入，然後點擊 <code>'+DXIcon('play')+' 開始</code>。',es:'Elija un modelo y una entrada para cada ranura y pulse <code>'+DXIcon('play')+' Iniciar</code>.'},
    {en:'Each slot shows the live picture and its FPS; <code>'+DXIcon('stop')+' Stop</code> ends one slot or all.',ko:'슬롯마다 실시간 화면과 FPS가 보이고, <code>'+DXIcon('stop')+' 중지</code>로 하나 또는 전부를 멈춥니다.',ja:'スロットごとにライブ映像と FPS が表示され、<code>'+DXIcon('stop')+' 停止</code>で 1 つまたは全部を止めます。','zh-CN':'每个槽位显示实时画面与 FPS；<code>'+DXIcon('stop')+' 停止</code>可停止单个或全部。','zh-TW':'每個槽位顯示即時畫面與 FPS；<code>'+DXIcon('stop')+' 停止</code>可停止單一或全部。',es:'Cada ranura muestra la imagen en vivo y sus FPS; <code>'+DXIcon('stop')+' Detener</code> termina una ranura o todas.'}])+
   _rBox('warn',{en:'Slots share the NPU, so more slots mean fewer FPS per slot.',ko:'슬롯들은 NPU를 나눠 쓰므로 슬롯이 많을수록 슬롯당 FPS가 줄어듭니다.',ja:'スロットは NPU を共有するため、スロットが多いほど 1 スロットあたりの FPS は下がります。','zh-CN':'各槽位共享 NPU，槽位越多，每个槽位的 FPS 越低。','zh-TW':'各槽位共用 NPU，槽位越多，每個槽位的 FPS 越低。',es:'Las ranuras comparten la NPU: cuantas más ranuras, menos FPS por ranura.'}),
  tips:_rH4(_R.tips)+
   _rList('ul',[
    {en:'<strong>Export Model Package</strong> packs the example source, the model and its config into an archive (C++, Python or both). The archive appears in Outputs.',ko:'<strong>Export Model Package</strong>는 예제 소스 · 모델 · 설정을 압축 파일 하나로 묶습니다(C++, Python 또는 둘 다). 결과는 Outputs에 나타납니다.',ja:'<strong>Export Model Package</strong> はサンプルのソース・モデル・設定を 1 つのアーカイブにまとめます（C++・Python・両方）。アーカイブは Outputs に表示されます。','zh-CN':'<strong>Export Model Package</strong> 会把示例源码、模型和配置打包为一个压缩包（C++、Python 或两者），并显示在 Outputs 中。','zh-TW':'<strong>Export Model Package</strong> 會將範例原始碼、模型與設定打包為一個壓縮檔（C++、Python 或兩者），並顯示在 Outputs 中。',es:'<strong>Export Model Package</strong> empaqueta el código de ejemplo, el modelo y su configuración en un archivo comprimido (C++, Python o ambos), que aparece en Outputs.'},
    {en:'Super-resolution results are larger than the original image.',ko:'초해상도 결과는 원본보다 큰 이미지입니다.',ja:'超解像の結果は元画像より大きくなります。','zh-CN':'超分辨率结果的尺寸大于原图。','zh-TW':'超解析度結果的尺寸大於原圖。',es:'Los resultados de superresolución son mayores que la imagen original.'}])
}},
{cat:'core',id:'rtsp-continuous',icon:'stream',page:'run',
 name:refL({en:'RTSP Input',ko:'RTSP 입력',ja:'RTSP 入力','zh-CN':'RTSP 输入','zh-TW':'RTSP 輸入',es:'Entrada RTSP'}),
 desc:refL({en:'Network cameras in Continuous, Benchmark and A/B Compare',ko:'Continuous · Benchmark · A/B Compare에서 네트워크 카메라 사용',ja:'Continuous・Benchmark・A/B 比較でネットワークカメラを使う','zh-CN':'在 Continuous、Benchmark 和 A/B 对比中使用网络摄像头','zh-TW':'在 Continuous、Benchmark 與 A/B 對比中使用網路攝影機',es:'Cámaras de red en Continuous, Benchmark y Comparación A/B'}),
 tabs:{
  overview:_rH4(_R.overview)+
   _rP({en:'Choose <strong>RTSP</strong> as the input, enter the <strong>RTSP Server</strong> as <code>IP:Port</code> and pick the <strong>Stream</strong> (stream1 – stream16). DX App opens <code>rtsp://IP:Port/streamN</code>.',ko:'입력으로 <strong>RTSP</strong>를 고르고 <strong>RTSP Server</strong>에 <code>IP:Port</code>를 넣은 뒤 <strong>Stream</strong>(stream1 – stream16)을 고릅니다. DX App은 <code>rtsp://IP:Port/streamN</code>을 엽니다.',ja:'入力に <strong>RTSP</strong> を選び、<strong>RTSP Server</strong> に <code>IP:Port</code> を入力して <strong>Stream</strong>（stream1 – stream16）を選びます。DX App は <code>rtsp://IP:Port/streamN</code> を開きます。','zh-CN':'选择 <strong>RTSP</strong> 作为输入，在 <strong>RTSP Server</strong> 中填写 <code>IP:Port</code>，再选择 <strong>Stream</strong>（stream1 – stream16）。DX App 会打开 <code>rtsp://IP:Port/streamN</code>。','zh-TW':'選擇 <strong>RTSP</strong> 作為輸入，在 <strong>RTSP Server</strong> 填寫 <code>IP:Port</code>，再選擇 <strong>Stream</strong>（stream1 – stream16）。DX App 會開啟 <code>rtsp://IP:Port/streamN</code>。',es:'Elija <strong>RTSP</strong> como entrada, escriba el <strong>RTSP Server</strong> como <code>IP:Port</code> y seleccione el <strong>Stream</strong> (stream1 – stream16). DX App abre <code>rtsp://IP:Port/streamN</code>.'})+
   _rFlow(['IP:Port','stream1 – stream16',DXIcon('play')+' Start',{en:'Live result',ko:'실시간 결과',ja:'ライブ結果','zh-CN':'实时结果','zh-TW':'即時結果',es:'Resultado en vivo'}]),
  tips:_rH4(_R.tips)+
   _rList('ul',[
    {en:'Check the stream first: <code>ffprobe rtsp://IP:Port/stream1</code>.',ko:'먼저 스트림을 확인하세요: <code>ffprobe rtsp://IP:Port/stream1</code>.',ja:'まずストリームを確認してください：<code>ffprobe rtsp://IP:Port/stream1</code>。','zh-CN':'先检查流：<code>ffprobe rtsp://IP:Port/stream1</code>。','zh-TW':'先檢查串流：<code>ffprobe rtsp://IP:Port/stream1</code>。',es:'Compruebe primero el flujo: <code>ffprobe rtsp://IP:Port/stream1</code>.'},
    {en:'The server must be reachable from this PC; the stream path must be streamN.',ko:'이 PC에서 서버에 닿아야 하고, 스트림 경로는 streamN 형식이어야 합니다.',ja:'この PC からサーバーに届く必要があり、ストリームのパスは streamN 形式である必要があります。','zh-CN':'这台电脑必须能访问该服务器，且流路径须为 streamN。','zh-TW':'這台電腦必須能連到該伺服器，且串流路徑須為 streamN。',es:'El servidor debe ser accesible desde este equipo y la ruta debe ser streamN.'},
    {en:'Each RTSP slot adds network and NPU load.',ko:'RTSP 슬롯마다 네트워크와 NPU 부하가 늘어납니다.',ja:'RTSP スロットごとにネットワークと NPU の負荷が増えます。','zh-CN':'每个 RTSP 槽位都会增加网络和 NPU 负载。','zh-TW':'每個 RTSP 槽位都會增加網路與 NPU 負載。',es:'Cada ranura RTSP añade carga de red y de NPU.'}])
}},
{cat:'core',id:'benchmark',icon:'clock',page:'bench',
 name:'Benchmark',
 desc:refL({en:'Measure several models in one go',ko:'여러 모델을 한 번에 측정',ja:'複数のモデルをまとめて計測','zh-CN':'一次测量多个模型','zh-TW':'一次測量多個模型',es:'Mida varios modelos de una vez'}),
 tabs:{
  overview:_rH4(_R.overview)+
   _rFlow([{en:'Select models',ko:'모델 선택',ja:'モデル選択','zh-CN':'选择模型','zh-TW':'選擇模型',es:'Elegir modelos'},'Loop Count',DXIcon('play')+' Run',{en:'Chart and table',ko:'차트 · 표',ja:'チャートと表','zh-CN':'图表与表格','zh-TW':'圖表與表格',es:'Gráfico y tabla'},'Export Report']),
  params:_rH4({en:'Parameters and results',ko:'파라미터 · 결과',ja:'パラメーターと結果','zh-CN':'参数与结果','zh-TW':'參數與結果',es:'Parámetros y resultados'})+
   _rTbl([{en:'Item',ko:'항목',ja:'項目','zh-CN':'项目','zh-TW':'項目',es:'Elemento'},{en:'Details',ko:'내용',ja:'内容','zh-CN':'说明','zh-TW':'說明',es:'Detalles'}],[
    ['Loop Count',{en:'1 – 10,000, default 100 (frames for a camera or RTSP input)',ko:'1 – 10,000, 기본 100 (카메라 · RTSP 입력은 프레임 수)',ja:'1 – 10,000、既定 100（カメラ・RTSP 入力ではフレーム数）','zh-CN':'1 – 10,000，默认 100（摄像头或 RTSP 输入时为帧数）','zh-TW':'1 – 10,000，預設 100（攝影機或 RTSP 輸入時為影格數）',es:'1 – 10.000, predeterminado 100 (fotogramas con cámara o RTSP)'}],
    [{en:'Result table',ko:'결과 표',ja:'結果の表','zh-CN':'结果表','zh-TW':'結果表',es:'Tabla de resultados'},{en:'Model, category, status, FPS, latency (ms), detail with the time per stage',ko:'모델, 분류, 상태, FPS, 지연(ms), 단계별 시간이 담긴 상세',ja:'モデル・カテゴリ・状態・FPS・レイテンシ（ms）・ステップごとの時間を含む詳細','zh-CN':'模型、类别、状态、FPS、延迟（ms），以及含各阶段耗时的详情','zh-TW':'模型、類別、狀態、FPS、延遲（ms），以及含各階段耗時的詳情',es:'Modelo, categoría, estado, FPS, latencia (ms) y detalle con el tiempo de cada etapa'}],
    [{en:'Chart',ko:'차트',ja:'チャート','zh-CN':'图表','zh-TW':'圖表',es:'Gráfico'},{en:'FPS of each model as bars',ko:'모델별 FPS 막대',ja:'モデルごとの FPS を棒で表示','zh-CN':'以条形显示各模型的 FPS','zh-TW':'以長條顯示各模型的 FPS',es:'FPS de cada modelo en barras'}]]),
  tips:_rH4(_R.tips)+
   _rList('ul',[
    {en:'A model\'s first run includes warm-up; 100 loops or more give steadier numbers.',ko:'모델의 첫 실행에는 워밍업이 섞이므로 100회 이상이 더 안정적입니다.',ja:'モデルの初回実行にはウォームアップが含まれるため、100 回以上だと数値が安定します。','zh-CN':'模型首次运行包含预热，100 次以上的循环数值更稳定。','zh-TW':'模型首次執行包含暖機，100 次以上的迴圈數值更穩定。',es:'La primera ejecución de un modelo incluye el calentamiento; con 100 vueltas o más las cifras son más estables.'},
    {en:'<strong>'+DXIcon('file')+' Export Report</strong> downloads a self-contained HTML report.',ko:'<strong>'+DXIcon('file')+' Export Report</strong>는 혼자 열리는 HTML 보고서를 내려받습니다.',ja:'<strong>'+DXIcon('file')+' Export Report</strong> は単体で開ける HTML レポートをダウンロードします。','zh-CN':'<strong>'+DXIcon('file')+' Export Report</strong> 会下载一个可独立打开的 HTML 报告。','zh-TW':'<strong>'+DXIcon('file')+' Export Report</strong> 會下載一個可獨立開啟的 HTML 報告。',es:'<strong>'+DXIcon('file')+' Export Report</strong> descarga un informe HTML autónomo.'}])
}},
{cat:'core',id:'compare',icon:'compare',page:'compare',
 name:'A/B Compare',
 desc:refL({en:'2–8 models side by side on the same input',ko:'같은 입력으로 모델 2–8개를 나란히',ja:'同じ入力で 2–8 モデルを並べて比較','zh-CN':'同一输入下并排对比 2–8 个模型','zh-TW':'同一輸入下並排比較 2–8 個模型',es:'De 2 a 8 modelos lado a lado con la misma entrada'}),
 tabs:{
  overview:_rH4(_R.overview)+
   _rList('ul',[
    {en:'<strong>Slots</strong> — 2, 4, 6 or 8; one model per slot.',ko:'<strong>Slots</strong> — 2 · 4 · 6 · 8개, 슬롯마다 모델 하나.',ja:'<strong>Slots</strong> — 2・4・6・8、スロットごとに 1 モデル。','zh-CN':'<strong>Slots</strong> — 2、4、6 或 8 个，每个槽位一个模型。','zh-TW':'<strong>Slots</strong> — 2、4、6 或 8 個，每個槽位一個模型。',es:'<strong>Slots</strong>: 2, 4, 6 u 8, un modelo por ranura.'},
    {en:'<strong>Shared input</strong> — file, camera or RTSP, plus the number of frames (default 30).',ko:'<strong>공유 입력</strong> — 파일 · 카메라 · RTSP와 프레임 수(기본 30).',ja:'<strong>共通の入力</strong> — ファイル・カメラ・RTSP とフレーム数（既定 30）。','zh-CN':'<strong>共享输入</strong> — 文件、摄像头或 RTSP，以及帧数（默认 30）。','zh-TW':'<strong>共用輸入</strong> — 檔案、攝影機或 RTSP，以及影格數（預設 30）。',es:'<strong>Entrada compartida</strong>: archivo, cámara o RTSP, más el número de fotogramas (30 por defecto).'},
    {en:'<strong>Performance Comparison</strong> — slot, model, FPS and latency in one table.',ko:'<strong>Performance Comparison</strong> — 슬롯 · 모델 · FPS · 지연을 한 표로.',ja:'<strong>Performance Comparison</strong> — スロット・モデル・FPS・レイテンシを 1 つの表に。','zh-CN':'<strong>Performance Comparison</strong> — 在一张表中列出槽位、模型、FPS 和延迟。','zh-TW':'<strong>Performance Comparison</strong> — 在一張表中列出槽位、模型、FPS 與延遲。',es:'<strong>Performance Comparison</strong>: ranura, modelo, FPS y latencia en una tabla.'}]),
  workflow:_rH4(_R.workflow)+
   _rList('ol',[
    {en:'Choose the number of slots.',ko:'슬롯 수를 고릅니다.',ja:'スロット数を選びます。','zh-CN':'选择槽位数量。','zh-TW':'選擇槽位數量。',es:'Elija el número de ranuras.'},
    {en:'Assign a model to each slot.',ko:'슬롯마다 모델을 정합니다.',ja:'スロットごとにモデルを割り当てます。','zh-CN':'为每个槽位指定模型。','zh-TW':'為每個槽位指定模型。',es:'Asigne un modelo a cada ranura.'},
    {en:'Pick the shared input and press <code>'+DXIcon('play')+' Run All</code>.',ko:'공유 입력을 고르고 <code>'+DXIcon('play')+' Run All</code>을 누릅니다.',ja:'共通の入力を選び、<code>'+DXIcon('play')+' Run All</code> を押します。','zh-CN':'选择共享输入并点击 <code>'+DXIcon('play')+' Run All</code>。','zh-TW':'選擇共用輸入並點擊 <code>'+DXIcon('play')+' Run All</code>。',es:'Elija la entrada compartida y pulse <code>'+DXIcon('play')+' Run All</code>.'},
    {en:'Compare the results side by side and read the table below them.',ko:'결과를 나란히 비교하고 아래 표를 확인합니다.',ja:'結果を並べて比較し、下の表を確認します。','zh-CN':'并排比较结果并查看下方表格。','zh-TW':'並排比較結果並查看下方表格。',es:'Compare los resultados lado a lado y consulte la tabla inferior.'}]),
  tips:_rH4(_R.tips)+
   _rList('ul',[
    {en:'Models of the same task show accuracy differences at a glance.',ko:'같은 작업의 모델끼리 비교하면 정확도 차이가 한눈에 보입니다.',ja:'同じタスクのモデル同士なら精度の差が一目でわかります。','zh-CN':'同一任务的模型对比时，精度差异一目了然。','zh-TW':'同一任務的模型比較時，精度差異一目了然。',es:'Con modelos de la misma tarea, las diferencias de precisión se ven a simple vista.'},
    {en:'Compare Q-Lite and Q-Pro builds of one model to see the effect of quantization.',ko:'한 모델의 Q-Lite와 Q-Pro를 비교하면 양자화의 영향을 볼 수 있습니다.',ja:'同じモデルの Q-Lite と Q-Pro を比べると量子化の影響がわかります。','zh-CN':'对比同一模型的 Q-Lite 与 Q-Pro，可看出量化的影响。','zh-TW':'比較同一模型的 Q-Lite 與 Q-Pro，可看出量化的影響。',es:'Compare las versiones Q-Lite y Q-Pro de un modelo para ver el efecto de la cuantización.'},
    {en:'Slots share the NPU; use 2 slots for the most precise FPS comparison.',ko:'슬롯들은 NPU를 나눠 쓰므로 FPS를 정확히 비교하려면 2개 슬롯을 쓰세요.',ja:'スロットは NPU を共有するため、FPS を正確に比べるには 2 スロットにしてください。','zh-CN':'各槽位共享 NPU，要精确比较 FPS 请使用 2 个槽位。','zh-TW':'各槽位共用 NPU，要精確比較 FPS 請使用 2 個槽位。',es:'Las ranuras comparten la NPU; use 2 ranuras para comparar FPS con más precisión.'}])
}},

/* ── Tools & Results ── */
{cat:'advanced',id:'modelzoo',icon:'download',page:'modelzoo',
 name:'ModelZoo',
 desc:refL({en:'Download compiled models in batches',ko:'컴파일된 모델을 한꺼번에 내려받기',ja:'コンパイル済みモデルをまとめてダウンロード','zh-CN':'批量下载已编译的模型','zh-TW':'批次下載已編譯的模型',es:'Descargue modelos compilados por lotes'}),
 tabs:{
  overview:_rH4(_R.overview)+
   _rList('ul',[
    {en:'<strong>Source</strong> — Public (default) or Internal (air-gapped).',ko:'<strong>Source</strong> — Public(기본) 또는 Internal(폐쇄망).',ja:'<strong>Source</strong> — Public（既定）または Internal（閉域網）。','zh-CN':'<strong>Source</strong> — Public（默认）或 Internal（离线网络）。','zh-TW':'<strong>Source</strong> — Public（預設）或 Internal（封閉網路）。',es:'<strong>Source</strong>: Public (predeterminado) o Internal (red aislada).'},
    {en:'<strong>Task chips and search</strong> narrow the table.',ko:'<strong>작업 칩과 검색</strong>으로 표를 좁힙니다.',ja:'<strong>タスクのチップと検索</strong>で表を絞り込みます。','zh-CN':'用<strong>任务标签和搜索</strong>缩小表格。','zh-TW':'用<strong>任務標籤與搜尋</strong>縮小表格。',es:'Los <strong>chips de tarea y la búsqueda</strong> filtran la tabla.'},
    {en:'Each row has a checkbox per build — <strong>Q-Lite</strong>, <strong>Q-Pro</strong>, <strong>Q-Master</strong>. Checked builds go to the cart and download together.',ko:'줄마다 빌드별 체크박스(<strong>Q-Lite</strong>, <strong>Q-Pro</strong>, <strong>Q-Master</strong>)가 있고, 체크한 빌드는 장바구니에 모여 한꺼번에 내려받습니다.',ja:'各行にビルドごとのチェックボックス（<strong>Q-Lite</strong>・<strong>Q-Pro</strong>・<strong>Q-Master</strong>）があり、チェックしたビルドはカートに入りまとめてダウンロードされます。','zh-CN':'每行有各构建版本的复选框（<strong>Q-Lite</strong>、<strong>Q-Pro</strong>、<strong>Q-Master</strong>），勾选的版本进入购物车并一起下载。','zh-TW':'每列有各建置版本的核取方塊（<strong>Q-Lite</strong>、<strong>Q-Pro</strong>、<strong>Q-Master</strong>），勾選的版本進入購物車並一起下載。',es:'Cada fila tiene una casilla por versión (<strong>Q-Lite</strong>, <strong>Q-Pro</strong>, <strong>Q-Master</strong>); las marcadas van al carrito y se descargan juntas.'},
    {en:'Shortcuts: Select All, New Only, Q-Lite All, Q-Pro All, Q-Master All, Deselect.',ko:'일괄 선택: Select All, New Only, Q-Lite All, Q-Pro All, Q-Master All, Deselect.',ja:'一括選択：Select All・New Only・Q-Lite All・Q-Pro All・Q-Master All・Deselect。','zh-CN':'批量选择：Select All、New Only、Q-Lite All、Q-Pro All、Q-Master All、Deselect。','zh-TW':'批次選擇：Select All、New Only、Q-Lite All、Q-Pro All、Q-Master All、Deselect。',es:'Selección rápida: Select All, New Only, Q-Lite All, Q-Pro All, Q-Master All, Deselect.'}]),
  params:_rH4({en:'Builds',ko:'빌드 종류',ja:'ビルドの種類','zh-CN':'构建版本','zh-TW':'建置版本',es:'Versiones'})+
   _rTbl([{en:'Build',ko:'빌드',ja:'ビルド','zh-CN':'版本','zh-TW':'版本',es:'Versión'},{en:'Characteristics',ko:'특징',ja:'特徴','zh-CN':'特点','zh-TW':'特點',es:'Características'}],[
    ['Q-Lite',{en:'Lighter quantization — faster, with a small accuracy loss',ko:'가벼운 양자화 — 더 빠르고 정확도는 조금 낮음',ja:'軽い量子化 — より速く、精度はわずかに低い','zh-CN':'轻量量化 — 更快，精度略有下降','zh-TW':'輕量量化 — 更快，精度略有下降',es:'Cuantización ligera: más rápida, con una pequeña pérdida de precisión'}],
    ['Q-Pro',{en:'More precise quantization — higher accuracy',ko:'더 정밀한 양자화 — 더 높은 정확도',ja:'より精密な量子化 — 精度が高い','zh-CN':'更精确的量化 — 精度更高','zh-TW':'更精確的量化 — 精度更高',es:'Cuantización más precisa: mayor exactitud'}],
    ['Q-Master',{en:'Highest-precision build, where one is published',ko:'공개된 경우의 가장 정밀한 빌드',ja:'公開されている場合の最も精密なビルド','zh-CN':'最高精度版本（如有发布）','zh-TW':'最高精度版本（如有發布）',es:'Versión de máxima precisión, cuando se publica'}]]),
  tips:_rH4(_R.tips)+
   _rList('ul',[
    {en:'On a closed network, switch the source to Internal.',ko:'폐쇄망에서는 Source를 Internal로 바꾸세요.',ja:'閉域網では Source を Internal に切り替えてください。','zh-CN':'在封闭网络中，请将 Source 切换为 Internal。','zh-TW':'在封閉網路中，請將 Source 切換為 Internal。',es:'En una red aislada, cambie el origen a Internal.'},
    {en:'Downloaded models appear on the Models page right away.',ko:'내려받은 모델은 바로 Models 페이지에 나타납니다.',ja:'ダウンロードしたモデルはすぐに Models ページに表示されます。','zh-CN':'下载的模型会立即出现在 Models 页面。','zh-TW':'下載的模型會立即出現在 Models 頁面。',es:'Los modelos descargados aparecen al instante en la página Models.'}])
}},
{cat:'advanced',id:'outputs',icon:'folder',page:'outputs',
 name:'Outputs',
 desc:refL({en:'Saved result files: images, videos, archives',ko:'저장된 결과 파일: 이미지 · 영상 · 압축 파일',ja:'保存された結果ファイル：画像・動画・アーカイブ','zh-CN':'保存的结果文件：图片、视频、压缩包','zh-TW':'儲存的結果檔案：圖片、影片、壓縮檔',es:'Archivos de resultados guardados: imágenes, videos y archivos comprimidos'}),
 tabs:{
  overview:_rH4(_R.overview)+
   _rList('ul',[
    {en:'<strong>Grid</strong> or <strong>table</strong> view; filter by All, Images, Videos, Archives or Other.',ko:'<strong>Grid</strong> 또는 <strong>Table</strong> 보기, 전체 · 이미지 · 영상 · 압축 · 기타로 거르기.',ja:'<strong>Grid</strong> または <strong>Table</strong> 表示。すべて・画像・動画・アーカイブ・その他で絞り込み。','zh-CN':'<strong>Grid</strong> 或 <strong>Table</strong> 视图；按全部、图片、视频、压缩包或其他筛选。','zh-TW':'<strong>Grid</strong> 或 <strong>Table</strong> 檢視；依全部、圖片、影片、壓縮檔或其他篩選。',es:'Vista de <strong>cuadrícula</strong> o de <strong>tabla</strong>; filtre por Todo, Imágenes, Videos, Archivos u Otros.'},
    {en:'Click a file to open it in the viewer; results made from a source image can be compared before / after.',ko:'파일을 누르면 뷰어로 열리고, 원본 이미지가 있는 결과는 전 / 후 비교를 할 수 있습니다.',ja:'ファイルをクリックするとビューアで開きます。元画像のある結果は前後比較ができます。','zh-CN':'点击文件在查看器中打开；带有原始图片的结果可进行前后对比。','zh-TW':'點擊檔案在檢視器中開啟；帶有原始圖片的結果可進行前後比較。',es:'Haga clic en un archivo para abrirlo en el visor; los resultados con imagen de origen se pueden comparar antes / después.'},
    {en:'Each file shows its size and time, and can be downloaded or deleted.',ko:'파일마다 크기와 시각이 보이고, 내려받거나 지울 수 있습니다.',ja:'各ファイルにサイズと日時が表示され、ダウンロードや削除ができます。','zh-CN':'每个文件显示大小和时间，可下载或删除。','zh-TW':'每個檔案顯示大小與時間，可下載或刪除。',es:'Cada archivo muestra su tamaño y fecha, y puede descargarse o eliminarse.'}]),
  tips:_rH4(_R.tips)+
   _rList('ul',[
    {en:'Files are kept in <code>outputs/dx_app/</code> inside DX AI Studio.',ko:'파일은 DX AI Studio 안의 <code>outputs/dx_app/</code>에 있습니다.',ja:'ファイルは DX AI Studio 内の <code>outputs/dx_app/</code> に保存されます。','zh-CN':'文件保存在 DX AI Studio 中的 <code>outputs/dx_app/</code>。','zh-TW':'檔案保存在 DX AI Studio 中的 <code>outputs/dx_app/</code>。',es:'Los archivos se guardan en <code>outputs/dx_app/</code> dentro de DX AI Studio.'},
    {en:'Exported model packages appear here; benchmark reports download in the browser instead.',ko:'내보낸 모델 패키지는 여기에 나오고, 벤치마크 보고서는 브라우저로 바로 내려받습니다.',ja:'エクスポートしたモデルパッケージはここに表示され、ベンチマークレポートはブラウザに直接ダウンロードされます。','zh-CN':'导出的模型包会出现在这里；基准测试报告则直接在浏览器中下载。','zh-TW':'匯出的模型包會出現在這裡；基準測試報告則直接在瀏覽器中下載。',es:'Los paquetes de modelo exportados aparecen aquí; los informes de benchmark se descargan en el navegador.'}])
}},
{cat:'advanced',id:'compiler',icon:'compiler',
 name:'Compiler',
 desc:refL({en:'ONNX → DXNN in the Compiler module',ko:'Compiler 모듈에서 ONNX → DXNN',ja:'Compiler モジュールで ONNX → DXNN','zh-CN':'在 Compiler 模块中 ONNX → DXNN','zh-TW':'在 Compiler 模組中 ONNX → DXNN',es:'ONNX → DXNN en el módulo Compiler'}),
 tabs:{
  overview:_rH4(_R.overview)+
   _rP({en:'DX App runs compiled <code>.dxnn</code> models. To compile your own ONNX model, open the <strong>Compiler</strong> module from the left rail: choose the ONNX file and a configuration, compile, and use the resulting <code>.dxnn</code> here.',ko:'DX App은 컴파일된 <code>.dxnn</code> 모델을 실행합니다. 직접 만든 ONNX 모델은 왼쪽 레일의 <strong>Compiler</strong> 모듈에서 ONNX 파일과 설정을 고른 뒤 컴파일하고, 나온 <code>.dxnn</code>을 여기서 쓰세요.',ja:'DX App はコンパイル済みの <code>.dxnn</code> モデルを実行します。独自の ONNX モデルは、左のレールから <strong>Compiler</strong> モジュールを開き、ONNX ファイルと設定を選んでコンパイルし、できた <code>.dxnn</code> をここで使います。','zh-CN':'DX App 运行已编译的 <code>.dxnn</code> 模型。要编译自己的 ONNX 模型，请从左侧栏打开 <strong>Compiler</strong> 模块：选择 ONNX 文件和配置并编译，然后在这里使用生成的 <code>.dxnn</code>。','zh-TW':'DX App 執行已編譯的 <code>.dxnn</code> 模型。要編譯自己的 ONNX 模型，請從左側欄開啟 <strong>Compiler</strong> 模組：選擇 ONNX 檔案與設定並編譯，然後在這裡使用產生的 <code>.dxnn</code>。',es:'DX App ejecuta modelos <code>.dxnn</code> compilados. Para compilar su propio modelo ONNX, abra el módulo <strong>Compiler</strong> desde la barra lateral: elija el archivo ONNX y una configuración, compile y use aquí el <code>.dxnn</code> resultante.'})+
   _rFlow(['ONNX','config',{en:'Compile',ko:'컴파일',ja:'コンパイル','zh-CN':'编译','zh-TW':'編譯',es:'Compilar'},'.dxnn','DX App'])
}},
{cat:'advanced',id:'pipeline',icon:'external',
 name:refL({en:'Timing Chart',ko:'단계별 시간 차트',ja:'時間チャート','zh-CN':'耗时图','zh-TW':'耗時圖',es:'Gráfico de tiempos'}),
 desc:refL({en:'Where the time goes in each run',ko:'실행마다 시간이 어디에 쓰였는지',ja:'各実行で時間がどこにかかったか','zh-CN':'每次运行的时间花在哪里','zh-TW':'每次執行的時間花在哪裡',es:'En qué se va el tiempo de cada ejecución'}),
 tabs:{
  overview:_rH4(_R.overview)+
   _rP({en:'Run Inference, Benchmark and A/B Compare show a bar for each stage of a run: <strong>Read</strong>, <strong>Preprocess</strong>, <strong>Inference</strong>, <strong>Postprocess</strong> and <strong>Display</strong>. Each stage has its own colour, in that order.',ko:'Run Inference · Benchmark · A/B Compare는 실행의 단계마다 막대를 보여 줍니다: <strong>Read</strong>, <strong>Preprocess</strong>, <strong>Inference</strong>, <strong>Postprocess</strong>, <strong>Display</strong>. 단계마다 정해진 순서의 색이 있습니다.',ja:'Run Inference・Benchmark・A/B 比較は、実行の各ステップを棒で表示します：<strong>Read</strong>・<strong>Preprocess</strong>・<strong>Inference</strong>・<strong>Postprocess</strong>・<strong>Display</strong>。各ステップには順番どおりの色があります。','zh-CN':'Run Inference、Benchmark 和 A/B 对比会为运行的每个阶段显示一段条形：<strong>Read</strong>、<strong>Preprocess</strong>、<strong>Inference</strong>、<strong>Postprocess</strong> 和 <strong>Display</strong>，按顺序使用不同颜色。','zh-TW':'Run Inference、Benchmark 與 A/B 對比會為執行的每個階段顯示一段長條：<strong>Read</strong>、<strong>Preprocess</strong>、<strong>Inference</strong>、<strong>Postprocess</strong> 與 <strong>Display</strong>，依序使用不同顏色。',es:'Run Inference, Benchmark y Comparación A/B muestran una barra por etapa: <strong>Read</strong>, <strong>Preprocess</strong>, <strong>Inference</strong>, <strong>Postprocess</strong> y <strong>Display</strong>, cada una con su color en ese orden.'})+
   _rH4({en:'Bottleneck',ko:'병목',ja:'ボトルネック','zh-CN':'瓶颈','zh-TW':'瓶頸',es:'Cuello de botella'})+
   _rP({en:'The longest stage gets diagonal stripes and a <code>bottleneck</code> tag in the legend.',ko:'가장 오래 걸린 단계에는 사선 무늬와 범례의 <code>bottleneck</code> 표시가 붙습니다.',ja:'最も時間のかかったステップには斜線模様と凡例の <code>bottleneck</code> タグが付きます。','zh-CN':'耗时最长的阶段会带有斜纹，并在图例中标记 <code>bottleneck</code>。','zh-TW':'耗時最長的階段會帶有斜紋，並在圖例中標記 <code>bottleneck</code>。',es:'La etapa más larga lleva rayas diagonales y la etiqueta <code>bottleneck</code> en la leyenda.'}),
  tips:_rH4(_R.tips)+
   _rList('ul',[
    {en:'Preprocess is the bottleneck → check the input size and the preprocessing code.',ko:'Preprocess가 병목이면 → 입력 크기와 전처리 코드를 살펴보세요.',ja:'Preprocess がボトルネック → 入力サイズと前処理コードを確認してください。','zh-CN':'Preprocess 是瓶颈 → 检查输入尺寸和预处理代码。','zh-TW':'Preprocess 是瓶頸 → 檢查輸入尺寸與前處理程式碼。',es:'Si el cuello de botella es Preprocess, revise el tamaño de entrada y el código de preprocesado.'},
    {en:'Inference is the bottleneck → try a lighter model or the Q-Lite build.',ko:'Inference가 병목이면 → 더 가벼운 모델이나 Q-Lite 빌드를 써 보세요.',ja:'Inference がボトルネック → より軽いモデルか Q-Lite ビルドを試してください。','zh-CN':'Inference 是瓶颈 → 尝试更轻量的模型或 Q-Lite 版本。','zh-TW':'Inference 是瓶頸 → 嘗試更輕量的模型或 Q-Lite 版本。',es:'Si es Inference, pruebe un modelo más ligero o la versión Q-Lite.'}])
}},

/* ── System ── */
{cat:'system',id:'shortcuts',icon:'dev',
 name:refL({en:'Keyboard Shortcuts',ko:'키보드 단축키',ja:'キーボードショートカット','zh-CN':'键盘快捷键','zh-TW':'鍵盤快捷鍵',es:'Atajos de teclado'}),
 desc:refL({en:'Tutorial and dialog keys',ko:'튜토리얼 · 대화상자 키',ja:'チュートリアルとダイアログのキー','zh-CN':'教程与对话框按键','zh-TW':'教學與對話框按鍵',es:'Teclas del tutorial y de los diálogos'}),
 tabs:{
  overview:_rH4(_R.overview)+
   _rTbl([{en:'Key',ko:'키',ja:'キー','zh-CN':'按键','zh-TW':'按鍵',es:'Tecla'},{en:'Action',ko:'동작',ja:'動作','zh-CN':'作用','zh-TW':'作用',es:'Acción'}],[
    ['<span class="ref-kbd">Esc</span>',{en:'Stop the tutorial, close its index, a dialog or this detail panel',ko:'튜토리얼 끝내기, 목차 · 대화상자 · 이 상세 패널 닫기',ja:'チュートリアルを終了、目次・ダイアログ・この詳細パネルを閉じる','zh-CN':'结束教程，关闭目录、对话框或此详情面板','zh-TW':'結束教學，關閉目錄、對話框或此詳情面板',es:'Detener el tutorial o cerrar su índice, un diálogo o este panel'}],
    ['<span class="ref-kbd">←</span>',{en:'Previous tutorial step',ko:'튜토리얼 이전 단계',ja:'チュートリアルの前のステップ','zh-CN':'教程上一步','zh-TW':'教學上一步',es:'Paso anterior del tutorial'}],
    ['<span class="ref-kbd">→</span> <span class="ref-kbd">Enter</span> <span class="ref-kbd">Space</span>',{en:'Next tutorial step',ko:'튜토리얼 다음 단계',ja:'チュートリアルの次のステップ','zh-CN':'教程下一步','zh-TW':'教學下一步',es:'Paso siguiente del tutorial'}]])
}},
{cat:'system',id:'themes-i18n',icon:'theme',
 name:refL({en:'Theme & Language',ko:'테마 · 언어',ja:'テーマと言語','zh-CN':'主题与语言','zh-TW':'主題與語言',es:'Tema e idioma'}),
 desc:refL({en:'Dark, light or system theme; six languages',ko:'어둡게 · 밝게 · 시스템 테마, 6개 언어',ja:'ダーク・ライト・システムのテーマと 6 言語','zh-CN':'深色、浅色或跟随系统主题；六种语言','zh-TW':'深色、淺色或跟隨系統主題；六種語言',es:'Tema oscuro, claro o del sistema; seis idiomas'}),
 tabs:{
  overview:_rH4(_R.overview)+
   _rList('ul',[
    {en:'The theme button in the top bar cycles '+DXIcon('moon')+' dark → '+DXIcon('sun')+' light → '+DXIcon('theme')+' system.',ko:'위쪽 막대의 테마 단추는 '+DXIcon('moon')+' 어둡게 → '+DXIcon('sun')+' 밝게 → '+DXIcon('theme')+' 시스템 순으로 바뀝니다.',ja:'上部バーのテーマボタンは '+DXIcon('moon')+' ダーク → '+DXIcon('sun')+' ライト → '+DXIcon('theme')+' システムの順に切り替わります。','zh-CN':'顶部栏的主题按钮按 '+DXIcon('moon')+' 深色 → '+DXIcon('sun')+' 浅色 → '+DXIcon('theme')+' 跟随系统 切换。','zh-TW':'頂部列的主題按鈕依 '+DXIcon('moon')+' 深色 → '+DXIcon('sun')+' 淺色 → '+DXIcon('theme')+' 跟隨系統 切換。',es:'El botón de tema de la barra superior alterna '+DXIcon('moon')+' oscuro → '+DXIcon('sun')+' claro → '+DXIcon('theme')+' del sistema.'},
    {en:'The '+DXIcon('globe')+' language menu offers English, 한국어, 日本語, Español, 简体中文 and 繁體中文; it also works from the keyboard.',ko:DXIcon('globe')+' 언어 메뉴에는 English, 한국어, 日本語, Español, 简体中文, 繁體中文이 있고 키보드로도 쓸 수 있습니다.',ja:DXIcon('globe')+' 言語メニューには English・한국어・日本語・Español・简体中文・繁體中文 があり、キーボードでも操作できます。','zh-CN':DXIcon('globe')+' 语言菜单提供 English、한국어、日本語、Español、简体中文 和 繁體中文，也可用键盘操作。','zh-TW':DXIcon('globe')+' 語言選單提供 English、한국어、日本語、Español、简体中文 與 繁體中文，也可用鍵盤操作。',es:'El menú de idioma '+DXIcon('globe')+' ofrece English, 한국어, 日本語, Español, 简体中文 y 繁體中文; también funciona con el teclado.'},
    {en:'Both choices are remembered in this browser and apply to every module.',ko:'두 설정 모두 이 브라우저에 기억되고 모든 모듈에 적용됩니다.',ja:'どちらの設定もこのブラウザに記憶され、すべてのモジュールに適用されます。','zh-CN':'两项设置都会保存在此浏览器中，并应用于所有模块。','zh-TW':'兩項設定都會保存在此瀏覽器中，並套用到所有模組。',es:'Ambas preferencias se recuerdan en este navegador y se aplican a todos los módulos.'}])
}},
{cat:'system',id:'global-features',icon:'wrench',
 name:refL({en:'Notifications & Help',ko:'알림 · 도움말',ja:'通知とヘルプ','zh-CN':'通知与帮助','zh-TW':'通知與說明',es:'Notificaciones y ayuda'}),
 desc:refL({en:'Notices, history, tutorial and assistant',ko:'알림, 기록, 튜토리얼, 도우미',ja:'通知・履歴・チュートリアル・アシスタント','zh-CN':'通知、历史、教程与助手','zh-TW':'通知、記錄、教學與助理',es:'Avisos, historial, tutorial y asistente'}),
 tabs:{
  overview:_rH4(_R.overview)+
   _rList('ul',[
    {en:'Notices appear for a few seconds and can be closed; some carry an action button.',ko:'알림은 몇 초 동안 보이고 닫을 수 있으며, 일부에는 동작 단추가 있습니다.',ja:'通知は数秒間表示され、閉じることもできます。一部には操作ボタンがあります。','zh-CN':'通知会显示几秒钟，可手动关闭；部分通知带有操作按钮。','zh-TW':'通知會顯示幾秒鐘，可手動關閉；部分通知帶有操作按鈕。',es:'Los avisos aparecen unos segundos y se pueden cerrar; algunos tienen un botón de acción.'},
    {en:'The bell keeps the history of notices, with a count of unread ones.',ko:'종 아이콘에 알림 기록이 남고 읽지 않은 수가 표시됩니다.',ja:'ベルに通知の履歴が残り、未読数が表示されます。','zh-CN':'铃铛中保留通知历史，并显示未读数量。','zh-TW':'鈴鐺中保留通知記錄，並顯示未讀數量。',es:'La campana guarda el historial de avisos con el número de no leídos.'},
    {en:'The '+DXIcon('graduation')+' button opens guided tours of each page.',ko:DXIcon('graduation')+' 단추로 페이지별 안내 튜토리얼을 엽니다.',ja:DXIcon('graduation')+' ボタンで各ページのガイドツアーを開きます。','zh-CN':DXIcon('graduation')+' 按钮可打开各页面的引导教程。','zh-TW':DXIcon('graduation')+' 按鈕可開啟各頁面的導覽教學。',es:'El botón '+DXIcon('graduation')+' abre visitas guiadas de cada página.'},
    {en:'The '+DXIcon('chat')+' button opens the DX Assistant for questions about the SDK.',ko:DXIcon('chat')+' 단추로 SDK에 대해 묻는 DX 어시스턴트를 엽니다.',ja:DXIcon('chat')+' ボタンで SDK について質問できる DX アシスタントを開きます。','zh-CN':DXIcon('chat')+' 按钮可打开 DX 助手，询问 SDK 相关问题。','zh-TW':DXIcon('chat')+' 按鈕可開啟 DX 助理，詢問 SDK 相關問題。',es:'El botón '+DXIcon('chat')+' abre el Asistente DX para preguntas sobre el SDK.'}])
}},
{cat:'system',id:'api-endpoints',icon:'globe',
 name:'API Endpoints',
 desc:refL({en:'The HTTP API behind this page',ko:'이 화면이 쓰는 HTTP API',ja:'この画面が使う HTTP API','zh-CN':'此页面使用的 HTTP API','zh-TW':'此頁面使用的 HTTP API',es:'La API HTTP que usa esta página'}),
 tabs:{
  overview:_rH4({en:'Main endpoints',ko:'주요 엔드포인트',ja:'主なエンドポイント','zh-CN':'主要端点','zh-TW':'主要端點',es:'Endpoints principales'})+
   _rTbl(['Method','Endpoint',{en:'Use',ko:'용도',ja:'用途','zh-CN':'用途','zh-TW':'用途',es:'Uso'}],[
    ['<span class="ref-api-method ref-api-get">GET</span>','<span class="mono">/api/models</span>',{en:'Runnable models on this PC',ko:'이 PC에서 실행할 수 있는 모델',ja:'この PC で実行できるモデル','zh-CN':'这台电脑上可运行的模型','zh-TW':'這台電腦上可執行的模型',es:'Modelos ejecutables en este equipo'}],
    ['<span class="ref-api-method ref-api-get">GET</span>','<span class="mono">/api/catalog</span>',{en:'The full model catalog',ko:'전체 모델 카탈로그',ja:'モデルカタログ全体','zh-CN':'完整的模型目录','zh-TW':'完整的模型目錄',es:'Catálogo completo de modelos'}],
    ['<span class="ref-api-method ref-api-post">POST</span>','<span class="mono">/api/run</span>',{en:'Run once and wait for the result',ko:'한 번 실행하고 결과를 기다림',ja:'1 回実行して結果を待つ','zh-CN':'运行一次并等待结果','zh-TW':'執行一次並等待結果',es:'Ejecuta una vez y espera el resultado'}],
    ['<span class="ref-api-method ref-api-post">POST</span>','<span class="mono">/api/run_async</span>',{en:'Start a run; follow it with /api/run_poll and /api/run_result, stop with /api/run_stop',ko:'실행 시작 — /api/run_poll · /api/run_result로 따라가고 /api/run_stop으로 멈춤',ja:'実行を開始し、/api/run_poll・/api/run_result で追跡、/api/run_stop で停止','zh-CN':'开始运行；用 /api/run_poll 和 /api/run_result 跟踪，用 /api/run_stop 停止','zh-TW':'開始執行；用 /api/run_poll 與 /api/run_result 追蹤，用 /api/run_stop 停止',es:'Inicia una ejecución; sígala con /api/run_poll y /api/run_result y deténgala con /api/run_stop'}],
    ['<span class="ref-api-method ref-api-post">POST</span>','<span class="mono">/api/run_multi</span>',{en:'A/B Compare: several models on one input',ko:'A/B Compare: 한 입력에 여러 모델',ja:'A/B 比較：1 つの入力で複数モデル','zh-CN':'A/B 对比：同一输入运行多个模型','zh-TW':'A/B 對比：同一輸入執行多個模型',es:'Comparación A/B: varios modelos con una entrada'}],
    ['<span class="ref-api-method ref-api-post">POST</span>','<span class="mono">/api/run_live</span>',{en:'Continuous slot; /api/live_poll, /api/live_frame (MJPEG), /api/live_stop',ko:'Continuous 슬롯 — /api/live_poll, /api/live_frame(MJPEG), /api/live_stop',ja:'Continuous スロット — /api/live_poll・/api/live_frame（MJPEG）・/api/live_stop','zh-CN':'Continuous 槽位；/api/live_poll、/api/live_frame（MJPEG）、/api/live_stop','zh-TW':'Continuous 槽位；/api/live_poll、/api/live_frame（MJPEG）、/api/live_stop',es:'Ranura Continuous; /api/live_poll, /api/live_frame (MJPEG), /api/live_stop'}],
    ['<span class="ref-api-method ref-api-get">GET</span>','<span class="mono">/api/outputs</span>',{en:'Saved result files (delete: POST /api/outputs/delete)',ko:'저장된 결과 파일 (삭제: POST /api/outputs/delete)',ja:'保存された結果ファイル（削除：POST /api/outputs/delete）','zh-CN':'保存的结果文件（删除：POST /api/outputs/delete）','zh-TW':'儲存的結果檔案（刪除：POST /api/outputs/delete）',es:'Archivos de resultados guardados (eliminar: POST /api/outputs/delete)'}],
    ['<span class="ref-api-method ref-api-get">GET</span>','<span class="mono">/api/setup/status</span>',{en:'Setup state; /api/setup/diagnostics runs the 12 checks',ko:'Setup 상태 — /api/setup/diagnostics는 12개 검사를 실행',ja:'Setup の状態。/api/setup/diagnostics は 12 項目をチェック','zh-CN':'Setup 状态；/api/setup/diagnostics 运行 12 项检查','zh-TW':'Setup 狀態；/api/setup/diagnostics 執行 12 項檢查',es:'Estado de Setup; /api/setup/diagnostics ejecuta las 12 comprobaciones'}]]),
  tips:_rH4(_R.tips)+
   _rBox('tip',{en:'The base URL here is <code>'+apiBase+'</code>. Requests and responses are JSON.',ko:'여기서 기본 URL은 <code>'+apiBase+'</code>이고, 요청과 응답은 JSON입니다.',ja:'ここでのベース URL は <code>'+apiBase+'</code> で、リクエストとレスポンスは JSON です。','zh-CN':'此处的基础 URL 为 <code>'+apiBase+'</code>，请求与响应均为 JSON。','zh-TW':'此處的基礎 URL 為 <code>'+apiBase+'</code>，請求與回應皆為 JSON。',es:'La URL base aquí es <code>'+apiBase+'</code>. Las solicitudes y respuestas son JSON.'})+
   _rList('ul',[
    {en:'From another computer, the API needs a paired browser or the <code>DX_API_TOKEN</code> sent as <code>Authorization: Bearer …</code>.',ko:'다른 컴퓨터에서는 페어링된 브라우저이거나 <code>DX_API_TOKEN</code>을 <code>Authorization: Bearer …</code>로 보내야 합니다.',ja:'別のコンピューターからは、ペアリング済みのブラウザか、<code>DX_API_TOKEN</code> を <code>Authorization: Bearer …</code> で送る必要があります。','zh-CN':'从另一台电脑访问时，需要已配对的浏览器，或以 <code>Authorization: Bearer …</code> 发送 <code>DX_API_TOKEN</code>。','zh-TW':'從另一台電腦存取時，需要已配對的瀏覽器，或以 <code>Authorization: Bearer …</code> 傳送 <code>DX_API_TOKEN</code>。',es:'Desde otro equipo, la API requiere un navegador emparejado o el <code>DX_API_TOKEN</code> enviado como <code>Authorization: Bearer …</code>.'}])
}}
];}
var _SEC=buildRefSections();

/* ════════════  RENDER  ════════════ */
function renderRef(){
  var mainEl=document.getElementById('ref-content');
  if(!mainEl) return;

  /* ── Search placeholder i18n ── */
  var searchEl=document.getElementById('ref-search');
  if(searchEl) searchEl.placeholder=refT5('Search documentation...','문서 검색...','ドキュメント検索...','搜索文档...','搜尋文件...','Buscar en la documentación...');

  /* ── Category chips ── */
  var chipEl=document.getElementById('ref-filter-bar');
  if(chipEl){
    var chipH='<button class="chip active" data-ref-cat-filter="all">'+ refT5('All','전체','すべて','全部','全部','Todo') +'</button>';
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
        '<span class="ref-section-icon">'+_refIco(s.icon)+'</span>'+
        '<span class="ref-section-info"><span class="ref-section-name">'+_refName(s)+'</span><span class="ref-section-desc">'+s.desc+'</span></span>'+
      '</button>';
    });
    mH+='</div>';
  });
  mainEl.innerHTML=mH;
}

/* ════════════  INTERACTIONS  ════════════ */

/* 주제 아이콘은 sprite 이름 (아이콘 체계 단계 5). 옛 글자 icon 은 그대로. */
/* 주제 이름 중 화면 이름 (Models · Outputs · Run Inference …) 은 탭과 같은 사전 키라 T() 로 번역한다.
   예전에는 ja · es 에서도 영어로 보였다 (탭은 번역되는데). */
function _refName(s){return typeof T==='function'?T(s.name):s.name;}

function _refIco(n){return (/^[a-z0-9_-]+$/.test(n||'')&&typeof DXIcon==='function')?DXIcon(n):(n||'');}

function _refBuildDetail(s){
  var tabKeys=Object.keys(s.tabs);
  var tabLabels={overview:DXIcon('clipboard') + ' '+refT5('Overview','개요','概要','概述','概述','Descripción general'),params:DXIcon('gear') + ' '+refT5('Details','상세','詳細','详情','詳情','Detalles'),workflow:DXIcon('refresh') + ' '+refT5('Workflow','작업 순서','手順','操作流程','操作流程','Flujo de trabajo'),tips:DXIcon('info') + ' '+refT5('Tips','팁','ヒント','提示','提示','Consejos')};
  var navLabel=refT5(' → Go to page',' 페이지로 →',' ページへ →',' → 前往页面',' → 前往頁面',' → Ir a la página');
  var goBtn=s.page?'<button class="btn btn-ghost btn-sm" onclick="if(typeof nav===\'function\')nav(\''+s.page+'\')">'+_refName(s)+navLabel+'</button>':'';
  var h='<div class="ref-detail-hd"><div><div class="ref-detail-kicker">'+ refT5('Reference','레퍼런스','リファレンス','参考','參考','Referencia') +'</div><h2>'+_refIco(s.icon)+' '+_refName(s)+'</h2><p>'+s.desc+'</p></div>'+goBtn+'</div>';
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
  closeBtn.className='ref-expand-close';closeBtn.innerHTML=(typeof DXIcon==='function')?DXIcon('x'):'';closeBtn.setAttribute('aria-label','Close');
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
