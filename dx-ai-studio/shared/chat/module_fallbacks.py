"""Each module's offline-assistant answers (no API key), in all six languages.

One table keeps every module's answers current and lets a contract test check every language.
Contract: tests/shared/test_module_fallbacks.py

Each rule is (keywords, {lang: answer}); FallbackEngine matches a keyword in the user's message.
"""
from __future__ import annotations

LANGS = ("en", "ko", "ja", "zh-CN", "zh-TW", "es")

_RULES = {
    "dx_app": [
        (["demo", "run", "inference", "detect", "yolo", "face", "pose", "데모", "추론", "실행", "검출", "얼굴",
          "デモ", "推論", "検出", "演示", "推理", "检测", "示範", "推論", "inferencia", "detección"], {
            "en": "Run Demo has ready-made demos for every task — image or video, C++ or Python. To run any model on "
                  "your own input, open Run Inference and pick a category, a model and an input.",
            "ko": "Run Demo에 태스크마다 바로 실행할 수 있는 데모가 있습니다 — 이미지 · 영상, C++ · Python. 원하는 모델을 내 입력으로 "
                  "돌리려면 Run Inference에서 카테고리 · 모델 · 입력을 고르세요.",
            "ja": "Run Demo にはタスクごとにすぐ動かせるデモがあります(画像・動画、C++・Python)。任意のモデルを自分の入力で"
                  "動かすには、Run Inference でカテゴリ・モデル・入力を選んでください。",
            "zh-CN": "Run Demo 为每个任务提供可直接运行的演示(图像或视频，C++ 或 Python)。要用自己的输入运行任意模型，"
                     "请在 Run Inference 中选择类别、模型和输入。",
            "zh-TW": "Run Demo 為每個任務提供可直接執行的示範(影像或影片，C++ 或 Python)。要用自己的輸入執行任意模型，"
                     "請在 Run Inference 中選擇類別、模型與輸入。",
            "es": "Run Demo tiene demos listas para cada tarea (imagen o video, C++ o Python). Para ejecutar cualquier "
                  "modelo con su propia entrada, abra Run Inference y elija una categoría, un modelo y una entrada.",
        }),
        (["sdk", "python", "c++", "api", "code", "example", "코드", "예제", "コード", "サンプル", "代码", "示例",
          "程式碼", "範例", "código", "ejemplo"], {
            "en": "Every model's Python and C++ example is in the DX App SDK (src/python_example, src/cpp_example). "
                  "The Reference tab explains the parameters; Lab can add a model or a task.",
            "ko": "모델마다 Python · C++ 예제가 DX App SDK (src/python_example, src/cpp_example)에 있습니다. Reference 탭이 "
                  "파라미터를 설명하고, Lab에서 모델이나 태스크를 추가할 수 있습니다.",
            "ja": "各モデルの Python と C++ のサンプルは DX App SDK (src/python_example, src/cpp_example) にあります。"
                  "Reference タブでパラメータを説明し、Lab でモデルやタスクを追加できます。",
            "zh-CN": "每个模型的 Python 与 C++ 示例都在 DX App SDK (src/python_example、src/cpp_example) 中。"
                     "Reference 选项卡说明参数，Lab 可添加模型或任务。",
            "zh-TW": "每個模型的 Python 與 C++ 範例都在 DX App SDK (src/python_example、src/cpp_example) 中。"
                     "Reference 分頁說明參數，Lab 可新增模型或任務。",
            "es": "El ejemplo en Python y C++ de cada modelo está en el SDK de DX App (src/python_example, "
                  "src/cpp_example). La pestaña Reference explica los parámetros y Lab añade un modelo o una tarea.",
        }),
    ],
    "dx_stream": [
        (["element", "elements", "엘리먼트", "エレメント", "元素", "elemento", "DxInfer"], {
            "en": "The Element Reference tab lists DX Stream's GStreamer elements with their properties and pads.",
            "ko": "Element Reference 탭에서 DX Stream의 GStreamer 엘리먼트와 속성 · pad를 볼 수 있습니다.",
            "ja": "Element Reference タブで DX Stream の GStreamer エレメントとプロパティ・パッドを確認できます。",
            "zh-CN": "Element Reference 选项卡列出 DX Stream 的 GStreamer 元素及其属性与端口。",
            "zh-TW": "Element Reference 分頁列出 DX Stream 的 GStreamer 元素及其屬性與連接埠。",
            "es": "La pestaña Element Reference muestra los elementos GStreamer de DX Stream con sus propiedades y pads.",
        }),
        (["pipeline", "pipelines", "gstreamer", "파이프라인", "パイプライン", "管道", "管線"], {
            "en": "Build a pipeline with drag & drop in the Pipeline Builder tab, or start from a preset.",
            "ko": "Pipeline Builder 탭에서 드래그 & 드롭으로 파이프라인을 만들거나 preset에서 시작하세요.",
            "ja": "Pipeline Builder タブでドラッグ & ドロップしてパイプラインを作るか、プリセットから始めてください。",
            "zh-CN": "可在 Pipeline Builder 选项卡中拖放构建管道，或从预设开始。",
            "zh-TW": "可在 Pipeline Builder 分頁中拖放建置管線，或從預設開始。",
            "es": "Cree un pipeline arrastrando y soltando en la pestaña Pipeline Builder, o empiece desde un preset.",
        }),
        (["demo", "webrtc", "mjpeg", "streaming", "stream", "데모", "스트리밍", "デモ", "ストリーミング", "演示", "流媒体",
          "示範", "串流", "demostración"], {
            "en": "Open the Demo Launcher, choose a demo and press Start. Use Local (WebRTC) on the board or LAN, "
                  "Remote (MJPEG) from another computer.",
            "ko": "Demo Launcher에서 데모를 고르고 Start를 누르세요. 보드 · 같은 LAN에서는 Local (WebRTC), 다른 컴퓨터에서는 "
                  "Remote (MJPEG)를 쓰세요.",
            "ja": "Demo Launcher でデモを選び Start を押してください。ボードや同じ LAN では Local (WebRTC)、別のコンピューターからは "
                  "Remote (MJPEG) を使います。",
            "zh-CN": "打开 Demo Launcher，选择演示并点击 Start。在开发板或同一局域网使用 Local (WebRTC)，"
                     "从其他计算机使用 Remote (MJPEG)。",
            "zh-TW": "開啟 Demo Launcher，選擇示範並按 Start。在開發板或同一區域網路使用 Local (WebRTC)，"
                     "從其他電腦使用 Remote (MJPEG)。",
            "es": "Abra Demo Launcher, elija una demo y pulse Start. Use Local (WebRTC) en la placa o la LAN y "
                  "Remote (MJPEG) desde otro equipo.",
        }),
    ],
    "dx_modelzoo": [
        # Specific questions (download, inference) come first: the first match wins
        (["download", "다운로드", "설치", "ダウンロード", "下载", "下載", "descargar"], {
            "en": "Download a model (Q-Lite or Q-Pro) from its detail page.",
            "ko": "모델 상세 화면에서 Q-Lite 또는 Q-Pro로 다운로드하세요.",
            "ja": "モデルの詳細画面から Q-Lite または Q-Pro をダウンロードしてください。",
            "zh-CN": "请在模型详情页下载 Q-Lite 或 Q-Pro。",
            "zh-TW": "請在模型詳細頁下載 Q-Lite 或 Q-Pro。",
            "es": "Descargue un modelo (Q-Lite o Q-Pro) desde su página de detalle.",
        }),
        (["inference", "run", "demo", "추론", "실행", "推論", "推理", "inferencia"], {
            "en": "Run Inference on a model's detail page runs it on the NPU through DX App; download the model first.",
            "ko": "모델 상세 화면의 Run Inference가 DX App을 통해 NPU에서 실행합니다. 먼저 모델을 다운로드하세요.",
            "ja": "モデル詳細画面の Run Inference が DX App 経由で NPU 上で実行します。先にモデルをダウンロードしてください。",
            "zh-CN": "模型详情页的 Run Inference 会通过 DX App 在 NPU 上运行；请先下载模型。",
            "zh-TW": "模型詳細頁的 Run Inference 會透過 DX App 在 NPU 上執行；請先下載模型。",
            "es": "Run Inference en la página de detalle lo ejecuta en la NPU mediante DX App; descargue antes el modelo.",
        }),
        (["catalog", "model", "models", "search", "카탈로그", "모델", "검색", "カタログ", "モデル", "目录", "模型",
          "目錄", "catálogo", "modelo"], {
            "en": "The catalog lists nearly 500 DEEPX models by task; search, filter by category and sort at the top.",
            "ko": "카탈로그에 약 500개 DEEPX 모델이 태스크별로 있습니다. 위에서 검색 · 카테고리 필터 · 정렬을 쓰세요.",
            "ja": "カタログには約 500 の DEEPX モデルがタスク別に並んでいます。上部で検索・カテゴリ絞り込み・並べ替えができます。",
            "zh-CN": "目录按任务列出近 500 个 DEEPX 模型；可在顶部搜索、按类别筛选和排序。",
            "zh-TW": "目錄依任務列出近 500 個 DEEPX 模型；可在上方搜尋、依類別篩選與排序。",
            "es": "El catálogo reúne casi 500 modelos DEEPX por tarea; arriba puede buscar, filtrar por categoría y ordenar.",
        }),
    ],
    "dx_compiler": [
        (["compile", "onnx", "dxnn", "컴파일", "コンパイル", "编译", "編譯", "compilar"], {
            "en": "Choose an ONNX model (upload or server path) and a config — or build one with the wizard — then "
                  "click Compile.",
            "ko": "ONNX 모델 (업로드 또는 서버 경로)과 config를 고르세요 — config는 마법사로 만들 수도 있습니다 — 그다음 "
                  "Compile을 누르세요.",
            "ja": "ONNX モデル(アップロードまたはサーバーパス)と config を選び(config はウィザードでも作れます)、"
                  "Compile を押してください。",
            "zh-CN": "选择 ONNX 模型(上传或服务器路径)和 config(也可用向导生成)，然后点击 Compile。",
            "zh-TW": "選擇 ONNX 模型(上傳或伺服器路徑)與 config(也可用精靈產生)，然後按 Compile。",
            "es": "Elija un modelo ONNX (subida o ruta del servidor) y un config —o créelo con el asistente— y pulse "
                  "Compile.",
        }),
        (["graph", "viewer", "그래프", "시각화", "グラフ", "图", "圖", "grafo"], {
            "en": "The graph viewer shows the model and how each compile phase changes it; Ctrl+F searches nodes.",
            "ko": "그래프 뷰어가 모델과 컴파일 단계별 변화를 보여 줍니다. Ctrl+F로 노드를 찾을 수 있습니다.",
            "ja": "グラフビューアはモデルと各コンパイル段階の変化を表示します。Ctrl+F でノードを検索できます。",
            "zh-CN": "图查看器显示模型及每个编译阶段的变化；按 Ctrl+F 搜索节点。",
            "zh-TW": "圖檢視器顯示模型及每個編譯階段的變化；按 Ctrl+F 搜尋節點。",
            "es": "El visor de grafo muestra el modelo y cómo lo cambia cada fase de compilación; Ctrl+F busca nodos.",
        }),
        (["quantization", "quantize", "int8", "dxq", "양자화", "量子化", "量化", "cuantización"], {
            "en": "Pick a DXQ preset (P0–P5) or Auto (Q-PRO) in the quantization settings.",
            "ko": "양자화 설정에서 DXQ preset (P0–P5) 또는 Auto (Q-PRO)를 고르세요.",
            "ja": "量子化設定で DXQ プリセット (P0–P5) または Auto (Q-PRO) を選んでください。",
            "zh-CN": "在量化设置中选择 DXQ 预设 (P0–P5) 或 Auto (Q-PRO)。",
            "zh-TW": "在量化設定中選擇 DXQ 預設 (P0–P5) 或 Auto (Q-PRO)。",
            "es": "Elija un preset DXQ (P0–P5) o Auto (Q-PRO) en los ajustes de cuantización.",
        }),
    ],
    "dx_planner": [
        (["planner", "edgeguide", "recommend", "board", "host", "추천", "보드", "推奨", "ボード", "推荐", "推薦",
          "开发板", "開發板", "recomendar", "placa"], {
            "en": "DX EdgeGuide recommends the DEEPX board and host for your workload from measured YOLO26 "
                  "benchmarks: set the task, model size, channels and FPS, then Get Recommendations.",
            "ko": "DX EdgeGuide는 실측 YOLO26 벤치마크로 워크로드에 맞는 DEEPX 보드와 호스트를 추천합니다. 태스크 · 모델 크기 · "
                  "채널 · FPS를 정하고 Get Recommendations를 누르세요.",
            "ja": "DX EdgeGuide は実測 YOLO26 ベンチマークからワークロードに合う DEEPX ボードとホストを推奨します。タスク・"
                  "モデルサイズ・チャネル・FPS を決めて Get Recommendations を押してください。",
            "zh-CN": "DX EdgeGuide 依据实测 YOLO26 基准为您的工作负载推荐 DEEPX 开发板与主机：设定任务、模型大小、"
                     "通道数和 FPS，然后点击 Get Recommendations。",
            "zh-TW": "DX EdgeGuide 依實測 YOLO26 基準為您的工作負載推薦 DEEPX 開發板與主機：設定任務、模型大小、"
                     "通道數與 FPS，然後按 Get Recommendations。",
            "es": "DX EdgeGuide recomienda la placa y el host DEEPX para su carga a partir de pruebas YOLO26 medidas: "
                  "indique la tarea, el tamaño del modelo, los canales y los FPS y pulse Get Recommendations.",
        }),
        (["price", "cost", "quote", "buy", "가격", "비용", "견적", "구매", "価格", "見積", "价格", "報價", "报价",
          "precio", "presupuesto"], {
            "en": "The Buy step shows product information and a Request quote button; ranking itself is by "
                  "measured performance, not cost.",
            "ko": "Buy 단계에 제품 정보와 Request quote 버튼이 있습니다. 순위는 비용이 아니라 실측 성능으로 정합니다.",
            "ja": "Buy の段階に製品情報と Request quote ボタンがあります。順位はコストではなく実測性能で決まります。",
            "zh-CN": "Buy 步骤提供产品信息和 Request quote 按钮；排名依据实测性能而非成本。",
            "zh-TW": "Buy 步驟提供產品資訊與 Request quote 按鈕；排名依實測效能而非成本。",
            "es": "El paso Buy muestra la información del producto y el botón Request quote; la clasificación se basa "
                  "en el rendimiento medido, no en el coste.",
        }),
        (["dx-m1", "m1", "npu", "deepx"], {
            "en": "DEEPX DX-M1 is an M.2 NPU module rated at 25 TOPS; EdgeGuide compares it on several hosts.",
            "ko": "DEEPX DX-M1은 25 TOPS의 M.2 NPU 모듈입니다. EdgeGuide가 여러 호스트에서 비교합니다.",
            "ja": "DEEPX DX-M1 は 25 TOPS の M.2 NPU モジュールです。EdgeGuide が複数のホストで比較します。",
            "zh-CN": "DEEPX DX-M1 是 25 TOPS 的 M.2 NPU 模块；EdgeGuide 在多种主机上对其进行比较。",
            "zh-TW": "DEEPX DX-M1 是 25 TOPS 的 M.2 NPU 模組；EdgeGuide 在多種主機上進行比較。",
            "es": "DEEPX DX-M1 es un módulo NPU M.2 de 25 TOPS; EdgeGuide lo compara en varios hosts.",
        }),
    ],
    "dx_benchmark": [
        (["benchmark", "run", "벤치마크", "실행", "ベンチマーク", "基准", "基準", "prueba"], {
            "en": "Benchmarks run from the standalone dx-benchmark CLI: `cd dx-benchmark && ./run.sh run`. This page "
                  "shows the results.",
            "ko": "벤치마크는 별도 dx-benchmark CLI로 실행합니다: `cd dx-benchmark && ./run.sh run`. 이 화면은 결과를 보여 줍니다.",
            "ja": "ベンチマークは単体の dx-benchmark CLI で実行します: `cd dx-benchmark && ./run.sh run`。この画面は結果を表示します。",
            "zh-CN": "基准测试通过独立的 dx-benchmark CLI 运行：`cd dx-benchmark && ./run.sh run`。本页面显示结果。",
            "zh-TW": "基準測試透過獨立的 dx-benchmark CLI 執行：`cd dx-benchmark && ./run.sh run`。本頁面顯示結果。",
            "es": "Las pruebas se ejecutan con la CLI independiente dx-benchmark: `cd dx-benchmark && ./run.sh run`. "
                  "Esta página muestra los resultados.",
        }),
        (["result", "report", "dashboard", "결과", "리포트", "대시보드", "結果", "レポート", "结果", "报告", "報告",
          "resultado", "informe"], {
            "en": "The Dashboard tab charts the aggregated results; the Results tab opens each run with its report.",
            "ko": "Dashboard 탭이 모은 결과를 차트로, Results 탭이 실행마다 리포트를 보여 줍니다.",
            "ja": "Dashboard タブは集計結果をグラフで、Results タブは各実行とレポートを表示します。",
            "zh-CN": "Dashboard 选项卡以图表显示汇总结果；Results 选项卡打开每次运行及其报告。",
            "zh-TW": "Dashboard 分頁以圖表顯示彙總結果；Results 分頁開啟每次執行及其報告。",
            "es": "La pestaña Dashboard muestra los resultados agregados; Results abre cada ejecución con su informe.",
        }),
        (["hardware", "board", "device", "하드웨어", "보드", "ハードウェア", "ボード", "硬件", "硬體", "placa"], {
            "en": "Results cover several DEEPX NPU boards on different hosts; the Dashboard lists each platform.",
            "ko": "여러 호스트의 DEEPX NPU 보드 결과가 있습니다. Dashboard에서 플랫폼 목록을 볼 수 있습니다.",
            "ja": "複数のホスト上の DEEPX NPU ボードの結果があります。Dashboard に各プラットフォームが並びます。",
            "zh-CN": "结果涵盖不同主机上的多款 DEEPX NPU 开发板；Dashboard 列出每个平台。",
            "zh-TW": "結果涵蓋不同主機上的多款 DEEPX NPU 開發板；Dashboard 列出每個平台。",
            "es": "Los resultados cubren varias placas NPU DEEPX en distintos hosts; Dashboard muestra cada plataforma.",
        }),
    ],
    "dx_monitor": [
        (["hardware", "monitor", "npu", "temperature", "하드웨어", "모니터", "상태", "온도", "モニター", "温度",
          "监控", "監控", "temperatura"], {
            "en": "DX Monitor shows the NPU's temperature, clock, voltage and utilization, plus CPU and memory, live.",
            "ko": "DX Monitor가 NPU 온도 · 클럭 · 전압 · 사용률과 CPU · 메모리를 실시간으로 보여 줍니다.",
            "ja": "DX Monitor は NPU の温度・クロック・電圧・使用率と CPU・メモリをリアルタイムで表示します。",
            "zh-CN": "DX Monitor 实时显示 NPU 的温度、时钟、电压与利用率，以及 CPU 和内存。",
            "zh-TW": "DX Monitor 即時顯示 NPU 的溫度、時脈、電壓與使用率，以及 CPU 與記憶體。",
            "es": "DX Monitor muestra en vivo la temperatura, el reloj, el voltaje y el uso de la NPU, y la CPU y la "
                  "memoria.",
        }),
        (["event", "events", "log", "로그", "이벤트", "イベント", "ログ", "事件", "日志", "日誌", "evento"], {
            "en": "Runtime Events lists recent NPU and runtime status changes.",
            "ko": "Runtime Events에 최근 NPU · 런타임 상태 변화가 있습니다.",
            "ja": "Runtime Events に最近の NPU とランタイムの状態変化が表示されます。",
            "zh-CN": "Runtime Events 列出最近的 NPU 与运行时状态变化。",
            "zh-TW": "Runtime Events 列出最近的 NPU 與執行階段狀態變化。",
            "es": "Runtime Events muestra los cambios recientes de estado de la NPU y del runtime.",
        }),
    ],
    "dx_agent_dev": [
        (["agent", "console", "build", "app", "에이전트", "콘솔", "빌드", "앱", "エージェント", "コンソール", "代理",
          "智能体", "代理程式", "agente"], {
            "en": "Describe the app you want in the DX Agent Dev console: the coding agent builds it for the NPU and "
                  "streams its progress. You can start the same run from the prompt box on the hub home.",
            "ko": "DX Agent Dev 콘솔에 원하는 앱을 적으세요. 코딩 에이전트가 NPU용으로 만들고 진행을 보여 줍니다. 허브 홈의 "
                  "입력창에서도 같은 실행을 시작할 수 있습니다.",
            "ja": "DX Agent Dev のコンソールに作りたいアプリを書いてください。コーディングエージェントが NPU 向けに作り、"
                  "進行状況を表示します。ハブのホームの入力欄からも同じ実行を始められます。",
            "zh-CN": "在 DX Agent Dev 控制台中描述您想要的应用：编码代理会为 NPU 构建并实时显示进度。"
                     "也可以在中心主页的输入框中启动同样的运行。",
            "zh-TW": "在 DX Agent Dev 主控台中描述您想要的應用程式：程式代理會為 NPU 建置並即時顯示進度。"
                     "也可以在中心首頁的輸入框中啟動同樣的執行。",
            "es": "Describa la app que desea en la consola de DX Agent Dev: el agente de programación la crea para la "
                  "NPU y muestra su progreso. También puede iniciarla desde el cuadro de la página de inicio.",
        }),
    ],
}


def rules(app: str) -> list:
    """The fallback rules for one module, as ChatEngine(fallback_rules=…) expects."""
    return [(list(k), dict(v)) for k, v in _RULES.get(app, [])]


def apps() -> tuple:
    return tuple(_RULES)
