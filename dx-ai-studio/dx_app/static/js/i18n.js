/* ============================================================
   i18n.js — DX-APP i18n Data Module
   Exports dictionaries & callbacks for shared/i18n.js core.
   ============================================================ */
'use strict';

/* ─── Translation Dictionary (English → Korean) ─── */
window._DX_I18N_DICT = {
  /* ==== Sidebar ==== */
  'Setup': {
    ko: '설치', ja: 'セットアップ',
    'zh-CN': '安装', 'zh-TW': '安裝',
    es: 'Instalación',
  },
  'Dashboard': {
    ko: '대시보드', ja: 'ダッシュボード',
    'zh-CN': '仪表盘', 'zh-TW': '儀表板',
    es: 'Panel de control',
  },
  'Models': {
    ko: '모델', ja: 'モデル',
    'zh-CN': '模型', 'zh-TW': '模型',
    es: 'Modelos',
  },
  'Benchmark': {
    ko: '벤치마크', ja: 'ベンチマーク',
    'zh-CN': '基准测试', 'zh-TW': '基準測試',
    es: 'Evaluación de rendimiento',
  },
  'A/B Compare': {
    ko: 'A/B 비교', ja: 'A/B 比較',
    'zh-CN': 'A/B 对比', 'zh-TW': 'A/B 比較',
    es: 'Comparación A/B',
  },
  'Compiler': {
    ko: '컴파일러', ja: 'コンパイラ',
    'zh-CN': '编译器', 'zh-TW': '編譯器',
    es: 'Compilador',
  },
  'Graph view is available for ONNX models only': {
    ko: '그래프 보기는 ONNX 모델만 지원합니다',
    ja: 'グラフ表示は ONNX モデルのみ対応します',
    'zh-CN': '图形视图仅支持 ONNX 模型',
    'zh-TW': '圖形檢視僅支援 ONNX 模型',
    es: 'La vista de grafo solo está disponible para modelos ONNX',
  },
  'Outputs': {
    ko: '출력물', ja: '出力',
    'zh-CN': '输出', 'zh-TW': '輸出',
    es: 'Salidas',
  },
  'EdgeGuide': {
    ko: 'EdgeGuide', ja: 'EdgeGuide',
    'zh-CN': 'EdgeGuide', 'zh-TW': 'EdgeGuide',
    es: 'EdgeGuide',
  },
  'Reference': {
    ko: '레퍼런스', ja: 'リファレンス',
    'zh-CN': '参考', 'zh-TW': '參考',
    es: 'Referencia',
  },
  'Developer': {
    ko: '개발자', ja: '開発者',
    'zh-CN': '开发者', 'zh-TW': '開發者',
    es: 'Desarrollador',
  },

  /* ==== Page titles ==== */
  'Setup & Install': {
    ko: '설치', ja: 'セットアップ & インストール',
    'zh-CN': '安装', 'zh-TW': '安裝',
    es: 'Instalación',
  },
  'API Endpoints': {
    ko: 'API 엔드포인트', ja: 'API エンドポイント',
    'zh-CN': 'API 端点', 'zh-TW': 'API 端點',
    es: 'Endpoints de la API',
  },
  'Run Inference': {
    ko: '추론 실행', ja: '推論実行',
    'zh-CN': '运行推理', 'zh-TW': '執行推論',
    es: 'Ejecutar inferencia',
  },
  'DX-COM Compiler': {
    ko: 'DX-COM 컴파일러', ja: 'DX-COM コンパイラ',
    'zh-CN': 'DX-COM 编译器', 'zh-TW': 'DX-COM 編譯器',
    es: 'Compilador DX-COM',
  },
  'DX EdgeGuide': {
    ko: 'DX EdgeGuide', ja: 'DX EdgeGuide',
    'zh-CN': 'DX EdgeGuide', 'zh-TW': 'DX EdgeGuide',
    es: 'DX EdgeGuide',
  },

  /* ==== Setup page ==== */
  'DX-APP Dependencies': {
    ko: 'DX-APP 종속성', ja: 'DX-APP 依存関係',
    'zh-CN': 'DX-APP 依赖项', 'zh-TW': 'DX-APP 相依套件',
    es: 'Dependencias de DX-APP',
  },
  'DX-APP Build': {
    ko: 'DX-APP 빌드', ja: 'DX-APP ビルド',
    'zh-CN': 'DX-APP 构建', 'zh-TW': 'DX-APP 建置',
    es: 'Compilación DX-APP',
  },
  'Sample Assets Setup': {
    ko: '샘플 에셋 설정', ja: 'サンプルアセットのセットアップ',
    'zh-CN': '示例资源设置', 'zh-TW': '範例資源設定',
    es: 'Configuración de activos de muestra',
  },
  'DX-Runtime Dependencies': {
    ko: 'DX-Runtime 종속성', ja: 'DX-Runtime 依存関係',
    'zh-CN': 'DX-Runtime 依赖项', 'zh-TW': 'DX-Runtime 相依套件',
    es: 'Dependencias de DX-Runtime',
  },
  'NPU Linux Driver': {
    ko: 'NPU 리눅스 드라이버', ja: 'NPU Linux ドライバー',
    'zh-CN': 'NPU Linux 驱动程序', 'zh-TW': 'NPU Linux 驅動程式',
    es: 'Controlador Linux NPU',
  },
  'Install': {
    ko: '설치', ja: 'インストール',
    'zh-CN': '安装', 'zh-TW': '安裝',
    es: 'Instalar',
  },
  'Build': {
    ko: '빌드', ja: 'ビルド',
    'zh-CN': '构建', 'zh-TW': '建置',
    es: 'Compilar',
  },
  'Execution Log': {
    ko: '실행 로그', ja: '実行ログ',
    'zh-CN': '执行日志', 'zh-TW': '執行日誌',
    es: 'Registro de ejecución',
  },
  'Manual Input': {
    ko: '수동 입력', ja: '手動入力',
    'zh-CN': '手动输入', 'zh-TW': '手動輸入',
    es: 'Entrada manual',
  },
  'Refresh Status': {
    ko: '상태 새로고침', ja: '状態を更新',
    'zh-CN': '刷新状态', 'zh-TW': '重新整理狀態',
    es: 'Actualizar estado',
  },
  'Send': {
    ko: '전송', ja: '送信',
    'zh-CN': '发送', 'zh-TW': '傳送',
    es: 'Enviar',
  },
  'Cancel': {
    ko: '취소', ja: 'キャンセル',
    'zh-CN': '取消', 'zh-TW': '取消',
    es: 'Cancelar',
  },
  'Start Install': {
    ko: '설치 시작', ja: 'インストール開始',
    'zh-CN': '启动安装', 'zh-TW': '啟動安裝',
    es: 'Iniciar instalación',
  },
  'DEEPX Developers Portal Account': {
    ko: 'DEEPX 개발자 포털 계정', ja: 'DEEPX 開発者ポータルアカウント',
    'zh-CN': 'DEEPX 开发者门户账户', 'zh-TW': 'DEEPX 開發者入口網站帳戶',
    es: 'Cuenta del portal de desarrolladores DEEPX',
  },
  'Select an item to run — logs will appear here.': {
    ko: '실행할 항목을 선택하세요 — 로그가 여기에 표시됩니다.', ja: '実行する項目を選択してください — ログがここに表示されます。',
    'zh-CN': '选择要运行的项目 — 日志将在此显示。', 'zh-TW': '選擇要執行的項目 — 日誌將在此顯示。',
    es: 'Seleccione un elemento para ejecutar — los registros aparecerán aquí.',
  },
  /* ==== Dashboard ==== */
  'NPU Topology': {
    ko: 'NPU 토폴로지', ja: 'NPU トポロジー',
    'zh-CN': 'NPU 拓扑', 'zh-TW': 'NPU 拓樸',
    es: 'Topología NPU',
  },
  'Realtime Monitor': {
    ko: '실시간 모니터', ja: 'リアルタイムモニター',
    'zh-CN': '实时监控', 'zh-TW': '即時監控',
    es: 'Monitor en tiempo real',
  },
  'System Resources': {
    ko: '시스템 자원', ja: 'システムリソース',
    'zh-CN': '系统资源', 'zh-TW': '系統資源',
    es: 'Recursos del sistema',
  },
  'CPU Load': {
    ko: 'CPU 부하', ja: 'CPU 負荷',
    'zh-CN': 'CPU 负载', 'zh-TW': 'CPU 負載',
    es: 'Carga de CPU',
  },
  'Memory': {
    ko: '메모리', ja: 'メモリ',
    'zh-CN': '内存', 'zh-TW': '記憶體',
    es: 'Memoria',
  },
  'NPU Temp': {
    ko: 'NPU 온도', ja: 'NPU 温度',
    'zh-CN': 'NPU 温度', 'zh-TW': 'NPU 溫度',
    es: 'Temp. NPU',
  },
  'Disk': {
    ko: '디스크', ja: 'ディスク',
    'zh-CN': '磁盘', 'zh-TW': '磁碟',
    es: 'Disco',
  },
  'System Information': {
    ko: '시스템 정보', ja: 'システム情報',
    'zh-CN': '系统信息', 'zh-TW': '系統資訊',
    es: 'Información del sistema',
  },
  'Property': {
    ko: '속성', ja: 'プロパティ',
    'zh-CN': '属性', 'zh-TW': '屬性',
    es: 'Propiedad',
  },
  'Value': {
    ko: '값', ja: '値',
    'zh-CN': '值', 'zh-TW': '值',
    es: 'Valor',
  },
  'Recent Runs': {
    ko: '최근 실행', ja: '最近の実行',
    'zh-CN': '最近运行', 'zh-TW': '最近執行',
    es: 'Ejecuciones recientes',
  },
  'Model': {
    ko: '모델', ja: 'モデル',
    'zh-CN': '模型', 'zh-TW': '模型',
    es: 'Modelo',
  },
  'Category': {
    ko: '카테고리', ja: 'カテゴリ',
    'zh-CN': '类别', 'zh-TW': '類別',
    es: 'Categoría',
  },
  'Lang': {
    ko: '언어', ja: '言語',
    'zh-CN': '语言', 'zh-TW': '語言',
    es: 'Idioma',
  },
  'FPS': {
    ko: 'FPS', ja: 'FPS',
    'zh-CN': 'FPS', 'zh-TW': 'FPS',
    es: 'FPS',
  },
  'Live source': {
    ko: '실시간 입력', ja: 'ライブ入力',
    'zh-CN': '实时输入', 'zh-TW': '即時輸入',
    es: 'Fuente en vivo',
  },
  'Exit code:': {
    ko: '종료 코드:', ja: '終了コード:',
    'zh-CN': '退出码：', 'zh-TW': '結束代碼：',
    es: 'Código de salida:',
  },
  'Latency': {
    ko: '지연시간', ja: 'レイテンシ',
    'zh-CN': '延迟', 'zh-TW': '延遲',
    es: 'Latencia',
  },
  'Status': {
    ko: '상태', ja: 'ステータス',
    'zh-CN': '状态', 'zh-TW': '狀態',
    es: 'Estado',
  },
  'FPS per Watt': {
    ko: '와트당 FPS', ja: 'ワットあたりFPS',
    'zh-CN': '每瓦FPS', 'zh-TW': '每瓦FPS',
    es: 'FPS por vatio',
  },
  'Total Models': {
    ko: '전체 모델', ja: 'モデル合計',
    'zh-CN': '模型总数', 'zh-TW': '總計模型',
    es: 'Total de modelos',
  },
  'C++ Models': {
    ko: 'C++ 모델', ja: 'C++ モデル',
    'zh-CN': 'C++ 模型', 'zh-TW': 'C++ 模型',
    es: 'Modelos C++',
  },
  'Python Models': {
    ko: 'Python 모델', ja: 'Python モデル',
    'zh-CN': 'Python 模型', 'zh-TW': 'Python 模型',
    es: 'Modelos Python',
  },
  'NPU Devices': {
    ko: 'NPU 디바이스', ja: 'NPU デバイス',
    'zh-CN': 'NPU 设备', 'zh-TW': 'NPU 裝置',
    es: 'Dispositivos NPU',
  },
  'No NPU detected': {
    ko: 'NPU가 감지되지 않음', ja: 'NPU が検出されません',
    'zh-CN': '未检测到 NPU', 'zh-TW': '未偵測到 NPU',
    es: 'No se detectó NPU',
  },
  'No runs yet': {
    ko: '실행 기록 없음', ja: 'まだ実行記録がありません',
    'zh-CN': '暂无运行记录', 'zh-TW': '尚無執行記錄',
    es: 'Aún no hay ejecuciones',
  },

  /* RT Monitor buttons */
  'Volt': {
    ko: '전압', ja: '電圧',
    'zh-CN': '电压', 'zh-TW': '電壓',
    es: 'Voltaje',
  },
  'Clock': {
    ko: '클럭', ja: 'クロック',
    'zh-CN': '时钟', 'zh-TW': '時脈',
    es: 'Reloj',
  },
  'Core Temp': {
    ko: '코어 온도', ja: 'コア温度',
    'zh-CN': '核心温度', 'zh-TW': '核心溫度',
    es: 'Temp. del núcleo',
  },
  'NPU DRAM': {
    ko: 'NPU DRAM', ja: 'NPU DRAM',
    'zh-CN': 'NPU DRAM', 'zh-TW': 'NPU DRAM',
    es: 'DRAM NPU',
  },
  'NPU Util': {
    ko: 'NPU 사용률', ja: 'NPU 使用率',
    'zh-CN': 'NPU 利用率', 'zh-TW': 'NPU 使用率',
    es: 'Util. NPU',
  },
  'View All': {
    ko: '전체 보기', ja: 'すべて表示',
    'zh-CN': '查看全部', 'zh-TW': '檢視全部',
    es: 'Ver todo',
  },

  /* Sysinfo table keys */
  'OS': {
    ko: 'OS', ja: 'OS',
    'zh-CN': 'OS', 'zh-TW': 'OS',
    es: 'SO',
  },
  'Hostname': {
    ko: '호스트명', ja: 'ホスト名',
    'zh-CN': '主机名', 'zh-TW': '主機名稱',
    es: 'Nombre de host',
  },
  'CPU': {
    ko: 'CPU', ja: 'CPU',
    'zh-CN': 'CPU', 'zh-TW': 'CPU',
    es: 'CPU',
  },
  'CPU Cores': {
    ko: 'CPU 코어', ja: 'CPU コア数',
    'zh-CN': 'CPU 核心数', 'zh-TW': 'CPU 核心數',
    es: 'Núcleos de CPU',
  },
  'Python': {
    ko: 'Python', ja: 'Python',
    'zh-CN': 'Python', 'zh-TW': 'Python',
    es: 'Python',
  },
  'OpenCV': {
    ko: 'OpenCV', ja: 'OpenCV',
    'zh-CN': 'OpenCV', 'zh-TW': 'OpenCV',
    es: 'OpenCV',
  },
  'DX-RT': {
    ko: 'DX-RT', ja: 'DX-RT',
    'zh-CN': 'DX-RT', 'zh-TW': 'DX-RT',
    es: 'DX-RT',
  },
  'DX-APP': {
    ko: 'DX-APP', ja: 'DX-APP',
    'zh-CN': 'DX-APP', 'zh-TW': 'DX-APP',
    es: 'DX-APP',
  },
  'NPU Count': {
    ko: 'NPU 수', ja: 'NPU 数',
    'zh-CN': 'NPU 数量', 'zh-TW': 'NPU 數量',
    es: 'Conteo de NPU',
  },
  'NPU PCI': {
    ko: 'NPU PCI', ja: 'NPU PCI',
    'zh-CN': 'NPU PCI', 'zh-TW': 'NPU PCI',
    es: 'PCI NPU',
  },
  'DX Engine': {
    ko: 'DX 엔진', ja: 'DX エンジン',
    'zh-CN': 'DX 引擎', 'zh-TW': 'DX 引擎',
    es: 'Motor DX',
  },

  /* ==== Models ==== */
  'Mode': {
    ko: '모드', ja: 'モード',
    'zh-CN': '模式', 'zh-TW': '模式',
    es: 'Modo',
  },
  'Meta': {
    ko: '메타', ja: 'メタ',
    'zh-CN': '元数据', 'zh-TW': '中繼資料',
    es: 'Metadatos',
  },
  'File': {
    ko: '파일', ja: 'ファイル',
    'zh-CN': '文件', 'zh-TW': '檔案',
    es: 'Archivo',
  },
  /* ==== Run Inference ==== */
  'Single': {
    ko: '단일', ja: '単一',
    'zh-CN': '单次', 'zh-TW': '單次',
    es: 'Individual',
  },
  'Continuous': {
    ko: '연속', ja: '連続',
    'zh-CN': '连续', 'zh-TW': '連續',
    es: 'Continuo',
  },
  'Language': {
    ko: '언어', ja: '言語',
    'zh-CN': '语言', 'zh-TW': '語言',
    es: 'Idioma',
  },
  'Input Type': {
    ko: '입력 유형', ja: '入力タイプ',
    'zh-CN': '输入类型', 'zh-TW': '輸入類型',
    es: 'Tipo de entrada',
  },
  'Image': {
    ko: '이미지', ja: '画像',
    'zh-CN': '图像', 'zh-TW': '影像',
    es: 'Imagen',
  },
  'Video': {
    ko: '동영상', ja: '動画',
    'zh-CN': '视频', 'zh-TW': '影片',
    es: 'Video',
  },
  'Sample Image': {
    ko: '샘플 이미지', ja: 'サンプル画像',
    'zh-CN': '示例图像', 'zh-TW': '範例影像',
    es: 'Imagen de muestra',
  },
  'Video File': {
    ko: '동영상 파일', ja: '動画ファイル',
    'zh-CN': '视频文件', 'zh-TW': '影片檔案',
    es: 'Archivo de video',
  },
  'Device ID': {
    ko: '디바이스 ID', ja: 'デバイス ID',
    'zh-CN': '设备 ID', 'zh-TW': '裝置 ID',
    es: 'ID de dispositivo',
  },
  'Confidence Threshold': {
    ko: '신뢰도 임계값', ja: '信頼度しきい値',
    'zh-CN': '置信度阈值', 'zh-TW': '信賴度閾值',
    es: 'Umbral de confianza',
  },
  'NMS IoU Threshold': {
    ko: 'NMS IoU 임계값', ja: 'NMS IoU しきい値',
    'zh-CN': 'NMS IoU 阈值', 'zh-TW': 'NMS IoU 閾值',
    es: 'Umbral IoU de NMS',
  },
  'Top-K Results': {
    ko: 'Top-K 결과', ja: 'Top-K 結果',
    'zh-CN': 'Top-K 结果', 'zh-TW': 'Top-K 結果',
    es: 'Resultados Top-K',
  },
  'Overlay Alpha': {
    ko: '오버레이 알파', ja: 'オーバーレイアルファ',
    'zh-CN': '叠加透明度', 'zh-TW': '疊加透明度',
    es: 'Alfa de superposición',
  },
  'Export Model Package': {
    ko: '모델 패키지 내보내기', ja: 'モデルパッケージのエクスポート',
    'zh-CN': '导出模型包', 'zh-TW': '匯出模型套件',
    es: 'Exportar paquete de modelo',
  },
  'Export': {
    ko: '내보내기', ja: 'エクスポート',
    'zh-CN': '导出', 'zh-TW': '匯出',
    es: 'Exportar',
  },
  'Sync': {
    ko: '동기', ja: '同期',
    'zh-CN': '同步', 'zh-TW': '同步',
    es: 'Síncrono',
  },
  'Async': {
    ko: '비동기', ja: '非同期',
    'zh-CN': '异步', 'zh-TW': '非同步',
    es: 'Asíncrono',
  },
  'Select a model and click Run.': {
    ko: '모델을 선택하고 실행을 클릭하세요.', ja: 'モデルを選択して実行をクリックしてください。',
    'zh-CN': '选择模型并点击运行。', 'zh-TW': '選擇模型並點擊執行。',
    es: 'Seleccione un modelo y haga clic en Ejecutar.',
  },
  'No additional parameters required for this task.': {
    ko: '이 작업에는 추가 매개변수가 필요하지 않습니다.', ja: 'このタスクに追加パラメータは不要です。',
    'zh-CN': '此任务无需额外参数。', 'zh-TW': '此任務無需額外參數。',
    es: 'No se requieren parámetros adicionales para esta tarea.',
  },
  'Continuous Config': {
    ko: '연속 구성', ja: '連続構成',
    'zh-CN': '连续配置', 'zh-TW': '連續組態',
    es: 'Configuración continua',
  },
  'Model Slots': {
    ko: '모델 슬롯', ja: 'モデルスロット',
    'zh-CN': '模型槽位', 'zh-TW': '模型插槽',
    es: 'Ranuras de modelo',
  },
  'Start Continuous': {
    ko: '연속 시작', ja: '連続開始',
    'zh-CN': '开始连续', 'zh-TW': '開始連續',
    es: 'Iniciar continuo',
  },
  'Stop': {
    ko: '중지', ja: '停止',
    'zh-CN': '停止', 'zh-TW': '停止',
    es: 'Detener',
  },
  'Live Display': {
    ko: '라이브 디스플레이', ja: 'ライブ表示',
    'zh-CN': '实时显示', 'zh-TW': '即時顯示',
    es: 'Pantalla en vivo',
  },

  /* ==== Benchmark ==== */
  'C++ (Compiled)': {
    ko: 'C++ (컴파일됨)', ja: 'C++ (コンパイル済み)',
    'zh-CN': 'C++ (已编译)', 'zh-TW': 'C++ (已編譯)',
    es: 'C++ (Compilado)',
  },
  'Select All': {
    ko: '전체 선택', ja: 'すべて選択',
    'zh-CN': '全选', 'zh-TW': '全選',
    es: 'Seleccionar todo',
  },
  'Deselect': {
    ko: '선택 해제', ja: '選択解除',
    'zh-CN': '取消选择', 'zh-TW': '取消選擇',
    es: 'Deseleccionar',
  },
  /* ==== A/B Compare ==== */
  'Panels:': {
    ko: '패널:', ja: 'パネル:',
    'zh-CN': '面板:', 'zh-TW': '面板:',
    es: 'Paneles:',
  },
  '2-split': {
    ko: '2분할', ja: '2分割',
    'zh-CN': '2分屏', 'zh-TW': '2分割',
    es: '2 divisiones',
  },
  '3-split': {
    ko: '3분할', ja: '3分割',
    'zh-CN': '3分屏', 'zh-TW': '3分割',
    es: '3 divisiones',
  },
  '4-split': {
    ko: '4분할', ja: '4分割',
    'zh-CN': '4分屏', 'zh-TW': '4分割',
    es: '4 divisiones',
  },
  'Shared Image': {
    ko: '공유 이미지', ja: '共有画像',
    'zh-CN': '共享图像', 'zh-TW': '共用影像',
    es: 'Imagen compartida',
  },
  // ── Setup step list ──
  'Install system packages required for C++ build (cmake, gcc, ninja, OpenCV, …)': {
    ko: 'C++ 빌드에 필요한 시스템 패키지 설치 (cmake, gcc, ninja, OpenCV, …)',
    ja: 'C++ ビルドに必要なシステムパッケージをインストール (cmake, gcc, ninja, OpenCV, …)',
    'zh-CN': '安装 C++ 构建所需的系统软件包 (cmake, gcc, ninja, OpenCV, …)',
    'zh-TW': '安裝 C++ 建置所需的系統套件 (cmake, gcc, ninja, OpenCV, …)',
    es: 'Instale los paquetes del sistema requeridos para la compilación C++ (cmake, gcc, ninja, OpenCV, …)',
  },
  'Install packages required for NPU runtime (cmake, ONNX Runtime, …)': {
    ko: 'NPU 런타임에 필요한 패키지 설치 (cmake, ONNX Runtime, …)',
    ja: 'NPU ランタイムに必要なパッケージをインストール (cmake, ONNX Runtime, …)',
    'zh-CN': '安装 NPU 运行时所需的软件包 (cmake, ONNX Runtime, …)',
    'zh-TW': '安裝 NPU 執行階段所需的套件 (cmake, ONNX Runtime, …)',
    es: 'Instale los paquetes requeridos para el runtime NPU (cmake, ONNX Runtime, …)',
  },
  'Build the DX-RT runtime and install the dx_engine Python API into venv-dx-runtime': {
    ko: 'DX-RT 런타임을 빌드하고 dx_engine Python API를 venv-dx-runtime에 설치',
    ja: 'DX-RT ランタイムをビルドし、dx_engine Python API を venv-dx-runtime にインストール',
    'zh-CN': '构建 DX-RT 运行时并将 dx_engine Python API 安装到 venv-dx-runtime',
    'zh-TW': '建置 DX-RT 執行環境並將 dx_engine Python API 安裝到 venv-dx-runtime',
    es: 'Compile el runtime DX-RT e instale la API de Python dx_engine en venv-dx-runtime',
  },
  'Install DEEPX NPU kernel driver (requires sudo)': {
    ko: 'DEEPX NPU 커널 드라이버 설치 (sudo 필요)',
    ja: 'DEEPX NPU カーネルドライバーをインストール (sudo 必要)',
    'zh-CN': '安装 DEEPX NPU 内核驱动程序 (需要 sudo)',
    'zh-TW': '安裝 DEEPX NPU 核心驅動程式 (需要 sudo)',
    es: 'Instale el controlador del kernel del NPU DEEPX (requiere sudo)',
  },
  'Compile C++ demo binaries (cmake)': {
    ko: 'C++ 데모 바이너리 컴파일 (cmake)',
    ja: 'C++ デモバイナリをコンパイル (cmake)',
    'zh-CN': '编译 C++ 演示二进制文件 (cmake)',
    'zh-TW': '編譯 C++ 演示二進位檔案 (cmake)',
    es: 'Compile binarios de demo C++ (cmake)',
  },
  'Download sample models & videos for Run / Benchmark demos': {
    ko: 'Run / Benchmark 데모용 샘플 모델 및 비디오 다운로드',
    ja: 'Run / Benchmark デモ用のサンプルモデルと動画をダウンロード',
    'zh-CN': '下载 Run / Benchmark 演示用的示例模型和视频',
    'zh-TW': '下載 Run / Benchmark 示範用的範例模型和影片',
    es: 'Descargue modelos y videos de ejemplo para demos de Ejecución / Benchmark',
  },
  // Run Demo card task names; the same words as the Model Zoo CATEGORIES labels.
  // New demos of the dx_app per-model layout, also matching the Model Zoo CATEGORIES labels.
  'Image Matting': { ko: '이미지 매팅', ja: '画像マッティング', 'zh-CN': '图像抠图', 'zh-TW': '影像去背', es: 'Matting de imagen' },
  'Image Retrieval': { ko: '이미지 검색', ja: '画像検索', 'zh-CN': '图像检索', 'zh-TW': '影像檢索', es: 'Recuperación de imágenes' },
  'Visual Place Recognition': { ko: '장소 인식', ja: '視覚的場所認識', 'zh-CN': '视觉地点识别', 'zh-TW': '視覺地點辨識', es: 'Reconocimiento visual de lugares' },
  'Retrieval & Matting': { ko: '검색 · 매팅', ja: '検索 · マッティング', 'zh-CN': '检索 · 抠图', 'zh-TW': '檢索 · 去背', es: 'Recuperación y matting' },
  '3D Object Detection': { ko: '3D 객체 탐지', ja: '3D物体検出', 'zh-CN': '3D目标检测', 'zh-TW': '3D物件偵測', es: 'Detección de objetos 3D' },
  'Attribute Recognition': { ko: '속성 인식', ja: '属性認識', 'zh-CN': '属性识别', 'zh-TW': '屬性辨識', es: 'Reconocimiento de atributos' },
  'Classification': { ko: '분류', ja: '分類', 'zh-CN': '分类', 'zh-TW': '分類', es: 'Clasificación' },
  // Run Demo group (filter) names: the groups of /api/demos
  'Detection': { ko: '탐지', ja: '検出', 'zh-CN': '检测', 'zh-TW': '偵測', es: 'Detección' },
  'Segmentation': { ko: '분할', ja: 'セグメンテーション', 'zh-CN': '分割', 'zh-TW': '分割', es: 'Segmentación' },
  'Keypoint & Pose': { ko: '키포인트 · 자세', ja: 'キーポイント · 姿勢', 'zh-CN': '关键点 · 姿态', 'zh-TW': '關鍵點 · 姿態', es: 'Puntos clave y pose' },
  'Pose & Landmark': { ko: '자세 · 랜드마크', ja: '姿勢 · ランドマーク', 'zh-CN': '姿态 · 关键点', 'zh-TW': '姿態 · 關鍵點', es: 'Pose y puntos de referencia' },
  'Driving & 3D': { ko: '주행 · 3D', ja: '運転 · 3D', 'zh-CN': '驾驶 · 3D', 'zh-TW': '駕駛 · 3D', es: 'Conducción y 3D' },
  'Image Restoration': { ko: '이미지 복원', ja: '画像復元', 'zh-CN': '图像复原', 'zh-TW': '影像復原', es: 'Restauración de imagen' },
  'Recognition': { ko: '인식', ja: '認識', 'zh-CN': '识别', 'zh-TW': '辨識', es: 'Reconocimiento' },
  'Depth Estimation': { ko: '깊이 추정', ja: '深度推定', 'zh-CN': '深度估计', 'zh-TW': '深度估計', es: 'Estimación de profundidad' },
  'Embedding': { ko: '임베딩', ja: '埋め込み', 'zh-CN': '嵌入', 'zh-TW': '嵌入', es: 'Embedding' },
  'Face Alignment': { ko: '얼굴 정렬', ja: '顔アライメント', 'zh-CN': '人脸对齐', 'zh-TW': '人臉對齊', es: 'Alineación facial' },
  'Face Detection': { ko: '얼굴 탐지', ja: '顔検出', 'zh-CN': '人脸检测', 'zh-TW': '人臉偵測', es: 'Detección de rostros' },
  'Hand Detection': { ko: '손 탐지', ja: '手検出', 'zh-CN': '手部检测', 'zh-TW': '手部偵測', es: 'Detección de manos' },
  'Hand Landmark': { ko: '손 랜드마크', ja: '手のランドマーク', 'zh-CN': '手部关键点', 'zh-TW': '手部關鍵點', es: 'Puntos de la mano' },
  'Image Denoising': { ko: '이미지 노이즈 제거', ja: '画像ノイズ除去', 'zh-CN': '图像去噪', 'zh-TW': '影像去噪', es: 'Eliminación de ruido de imagen' },
  'Image Enhancement': { ko: '이미지 향상', ja: '画像強調', 'zh-CN': '图像增强', 'zh-TW': '影像增強', es: 'Mejora de imagen' },
  'Instance Segmentation': { ko: '인스턴스 분할', ja: 'インスタンスセグメンテーション', 'zh-CN': '实例分割', 'zh-TW': '實例分割', es: 'Segmentación de instancias' },
  'Keypoint Detection': { ko: '키포인트 탐지', ja: 'キーポイント検出', 'zh-CN': '关键点检测', 'zh-TW': '關鍵點偵測', es: 'Detección de puntos clave' },
  'OBB Detection': { ko: 'OBB 탐지', ja: 'OBB検出', 'zh-CN': 'OBB检测', 'zh-TW': 'OBB偵測', es: 'Detección OBB' },
  'Object Detection': { ko: '객체 탐지', ja: '物体検出', 'zh-CN': '目标检测', 'zh-TW': '物件偵測', es: 'Detección de objetos' },
  'Object Pose Estimation': { ko: '객체 자세 추정', ja: '物体姿勢推定', 'zh-CN': '物体姿态估计', 'zh-TW': '物件姿態估計', es: 'Estimación de pose de objetos' },
  'PPU Pipeline': { ko: 'PPU 파이프라인', ja: 'PPU パイプライン', 'zh-CN': 'PPU 流水线', 'zh-TW': 'PPU 管線', es: 'Canalización PPU' },
  'Panoptic Driving': { ko: '파놉틱 주행 인식', ja: 'パノプティック走行認識', 'zh-CN': '全景驾驶感知', 'zh-TW': '全景駕駛感知', es: 'Percepción panóptica de conducción' },
  'Person Re-ID': { ko: '사람 재식별', ja: '人物再識別', 'zh-CN': '行人重识别', 'zh-TW': '行人重新識別', es: 'Re-ID de personas' },
  'Pose Estimation': { ko: '자세 추정', ja: '姿勢推定', 'zh-CN': '姿态估计', 'zh-TW': '姿態估計', es: 'Estimación de pose' },
  'Semantic Segmentation': { ko: '시맨틱 분할', ja: 'セマンティックセグメンテーション', 'zh-CN': '语义分割', 'zh-TW': '語意分割', es: 'Segmentación semántica' },
  'Super Resolution': { ko: '초해상도', ja: '超解像', 'zh-CN': '超分辨率', 'zh-TW': '超解析度', es: 'Superresolución' },
  'Set up the rest': {
    ko: '나머지 설치', ja: '残りをセットアップ',
    'zh-CN': '安装其余项', 'zh-TW': '安裝其餘項目',
    es: 'Instalar el resto',
  },
  'Six steps get DX App running on this PC. What is done stays done.': {
    ko: '여섯 단계면 이 PC에서 DX App이 돌아갑니다. 끝난 단계는 그대로 둡니다.',
    ja: '6 つのステップでこの PC で DX App が動きます。終わったステップはそのままです。',
    'zh-CN': '六个步骤即可让 DX App 在这台电脑上运行。已完成的步骤会保留。',
    'zh-TW': '六個步驟即可讓 DX App 在這台電腦上執行。已完成的步驟會保留。',
    es: 'Seis pasos para que DX App funcione en este PC. Lo que ya está hecho se queda hecho.',
  },
  'Run All': {
    ko: '전체 실행', ja: 'すべて実行',
    'zh-CN': '全部运行', 'zh-TW': '全部執行',
    es: 'Ejecutar todo',
  },
  'Performance Comparison': {
    ko: '성능 비교', ja: 'パフォーマンス比較',
    'zh-CN': '性能对比', 'zh-TW': '效能比較',
    es: 'Comparación de rendimiento',
  },
  'Slot': {
    ko: '슬롯', ja: 'スロット',
    'zh-CN': '槽位', 'zh-TW': '插槽',
    es: 'Ranura',
  },

  /* ==== Pipeline ==== */
  'Input Image': {
    ko: '입력 이미지', ja: '入力画像',
    'zh-CN': '输入图像', 'zh-TW': '輸入影像',
    es: 'Imagen de entrada',
  },
  'Input Video': {
    ko: '입력 동영상', ja: '入力動画',
    'zh-CN': '输入视频', 'zh-TW': '輸入影片',
    es: 'Video de entrada',
  },
  'Pipeline Mode': {
    ko: '파이프라인 모드', ja: 'パイプラインモード',
    'zh-CN': '流水线模式', 'zh-TW': '管線模式',
    es: 'Modo de pipeline',
  },
  'Add Step': {
    ko: '단계 추가', ja: 'ステップ追加',
    'zh-CN': '添加步骤', 'zh-TW': '新增步驟',
    es: 'Agregar paso',
  },
  'Run Pipeline': {
    ko: '파이프라인 실행', ja: 'パイプライン実行',
    'zh-CN': '运行流水线', 'zh-TW': '執行管線',
    es: 'Ejecutar pipeline',
  },
  'Chain (sequential pass-through)': {
    ko: '체인 (순차 통과)', ja: 'チェーン (順次パススルー)',
    'zh-CN': '链式 (顺序传递)', 'zh-TW': '鏈式 (順序傳遞)',
    es: 'Cadena (paso secuencial)',
  },
  'Cascade (stage-1 → cropped regions → stage-2)': {
    ko: '캐스케이드 (단계1 → 잘린 영역 → 단계2)', ja: 'カスケード (ステージ1 → トリミング領域 → ステージ2)',
    'zh-CN': '级联 (阶段1 → 裁剪区域 → 阶段2)', 'zh-TW': '級聯 (階段1 → 裁剪區域 → 階段2)',
    es: 'Cascada (etapa-1 → regiones recortadas → etapa-2)',
  },

  /* ==== Compiler ==== */
  'Presets': {
    ko: '프리셋', ja: 'プリセット',
    'zh-CN': '预设', 'zh-TW': '預設',
    es: 'Preajustes',
  },
  'ONNX Model': {
    ko: 'ONNX 모델', ja: 'ONNX モデル',
    'zh-CN': 'ONNX 模型', 'zh-TW': 'ONNX 模型',
    es: 'Modelo ONNX',
  },
  'Load JSON Config': {
    ko: 'JSON 구성 로드', ja: 'JSON 設定を読み込む',
    'zh-CN': '加载 JSON 配置', 'zh-TW': '載入 JSON 設定',
    es: 'Cargar configuración JSON',
  },
  'Local File': {
    ko: '로컬 파일', ja: 'ローカルファイル',
    'zh-CN': '本地文件', 'zh-TW': '本機檔案',
    es: 'Archivo local',
  },
  'Browse Server': {
    ko: '서버 찾아보기', ja: 'サーバーを参照',
    'zh-CN': '浏览服务器', 'zh-TW': '瀏覽伺服器',
    es: 'Explorar servidor',
  },
  'Compile Settings': {
    ko: '컴파일 설정', ja: 'コンパイル設定',
    'zh-CN': '编译设置', 'zh-TW': '編譯設定',
    es: 'Configuración de compilación',
  },
  'Input Name': {
    ko: '입력 이름', ja: '入力名',
    'zh-CN': '输入名称', 'zh-TW': '輸入名稱',
    es: 'Nombre de entrada',
  },
  'Input Shape (N,C,H,W)': {
    ko: '입력 형상 (N,C,H,W)', ja: '入力 Shape (N,C,H,W)',
    'zh-CN': '输入 Shape (N,C,H,W)', 'zh-TW': '輸入 Shape (N,C,H,W)',
    es: 'Forma de entrada (N,C,H,W)',
  },
  'Calibration Method': {
    ko: '보정 방법', ja: 'キャリブレーション方式',
    'zh-CN': '校准方法', 'zh-TW': '校準方法',
    es: 'Método de calibración',
  },
  'EMA (recommended)': {
    ko: 'EMA (권장)', ja: 'EMA (推奨)',
    'zh-CN': 'EMA (推荐)', 'zh-TW': 'EMA (建議)',
    es: 'EMA (recomendado)',
  },
  'MinMax': {
    ko: 'MinMax', ja: 'MinMax',
    'zh-CN': 'MinMax', 'zh-TW': 'MinMax',
    es: 'MínMáx',
  },
  'Calibration Samples': {
    ko: '보정 샘플', ja: 'キャリブレーションサンプル',
    'zh-CN': '校准样本', 'zh-TW': '校準樣本',
    es: 'Muestras de calibración',
  },
  'Optimization Level': {
    ko: '최적화 수준', ja: '最適化レベル',
    'zh-CN': '优化级别', 'zh-TW': '最佳化等級',
    es: 'Nivel de optimización',
  },
  'DXQ Enhanced Scheme': {
    ko: 'DXQ 향상 스키마', ja: 'DXQ 拡張スキーム',
    'zh-CN': 'DXQ 增强方案', 'zh-TW': 'DXQ 增強方案',
    es: 'Esquema mejorado DXQ',
  },
  'None (default)': {
    ko: '없음 (기본)', ja: 'なし (デフォルト)',
    'zh-CN': '无 (默认)', 'zh-TW': '無 (預設)',
    es: 'Ninguno (por defecto)',
  },
  'Quantization Device': {
    ko: '양자화 디바이스', ja: '量子化デバイス',
    'zh-CN': '量化设备', 'zh-TW': '量化裝置',
    es: 'Dispositivo de cuantización',
  },
  'Default (CPU)': {
    ko: '기본 (CPU)', ja: 'デフォルト (CPU)',
    'zh-CN': '默认 (CPU)', 'zh-TW': '預設 (CPU)',
    es: 'Por defecto (CPU)',
  },
  'CUDA (GPU)': {
    ko: 'CUDA (GPU)', ja: 'CUDA (GPU)',
    'zh-CN': 'CUDA (GPU)', 'zh-TW': 'CUDA (GPU)',
    es: 'CUDA (GPU)',
  },
  'Aggressive Partitioning': {
    ko: '공격적 파티셔닝', ja: 'アグレッシブパーティショニング',
    'zh-CN': '激进分区', 'zh-TW': '積極分區',
    es: 'Particionamiento agresivo',
  },
  'Generate compile log': {
    ko: '컴파일 로그 생성', ja: 'コンパイルログを生成',
    'zh-CN': '生成编译日志', 'zh-TW': '產生編譯日誌',
    es: 'Generar registro de compilación',
  },
  'Calibration Dataset': {
    ko: '보정 데이터셋', ja: 'キャリブレーションデータセット',
    'zh-CN': '校准数据集', 'zh-TW': '校準資料集',
    es: 'Conjunto de datos de calibración',
  },
  'Dataset path': {
    ko: '데이터셋 경로', ja: 'データセットパス',
    'zh-CN': '数据集路径', 'zh-TW': '資料集路徑',
    es: 'Ruta del conjunto de datos',
  },
  'File extension': {
    ko: '파일 확장자', ja: 'ファイル拡張子',
    'zh-CN': '文件扩展名', 'zh-TW': '檔案副檔名',
    es: 'Extensión de archivo',
  },
  'Preprocessing Pipeline': {
    ko: '전처리 파이프라인', ja: '前処理パイプライン',
    'zh-CN': '预处理流水线', 'zh-TW': '前處理管線',
    es: 'Pipeline de pre-procesamiento',
  },
  'Output Settings': {
    ko: '출력 설정', ja: '出力設定',
    'zh-CN': '输出设置', 'zh-TW': '輸出設定',
    es: 'Configuración de salida',
  },
  'Output Directory': {
    ko: '출력 디렉토리', ja: '出力ディレクトリ',
    'zh-CN': '输出目录', 'zh-TW': '輸出目錄',
    es: 'Directorio de salida',
  },
  'Start Compile': {
    ko: '컴파일 시작', ja: 'コンパイル開始',
    'zh-CN': '启动编译', 'zh-TW': '啟動編譯',
    es: 'Iniciar compilación',
  },
  'Export JSON': {
    ko: 'JSON 내보내기', ja: 'JSON エクスポート',
    'zh-CN': '导出 JSON', 'zh-TW': '匯出 JSON',
    es: 'Exportar JSON',
  },
  'Compile Log': {
    ko: '컴파일 로그', ja: 'コンパイルログ',
    'zh-CN': '编译日志', 'zh-TW': '編譯日誌',
    es: 'Registro de compilación',
  },
  'Compile Result': {
    ko: '컴파일 결과', ja: 'コンパイル結果',
    'zh-CN': '编译结果', 'zh-TW': '編譯結果',
    es: 'Resultado de compilación',
  },
  'Model Visualization': {
    ko: '모델 시각화', ja: 'モデル可視化',
    'zh-CN': '模型可视化', 'zh-TW': '模型視覺化',
    es: 'Visualización del modelo',
  },
  'Compile History': {
    ko: '컴파일 이력', ja: 'コンパイル履歴',
    'zh-CN': '编译历史', 'zh-TW': '編譯歷史',
    es: 'Historial de compilación',
  },
  'Time': {
    ko: '시간', ja: '時間',
    'zh-CN': '时间', 'zh-TW': '時間',
    es: 'Tiempo',
  },
  'No compile history yet.': {
    ko: '컴파일 이력이 없습니다.', ja: 'コンパイル履歴がまだありません。',
    'zh-CN': '暂无编译历史。', 'zh-TW': '尚無編譯歷史。',
    es: 'Aún no hay historial de compilación.',
  },
  'Logs will appear here once compiling starts.': {
    ko: '컴파일이 시작되면 로그가 여기에 표시됩니다.', ja: 'コンパイルが開始されるとログがここに表示されます。',
    'zh-CN': '编译开始后日志将显示在此处。', 'zh-TW': '編譯開始後日誌將顯示在此處。',
    es: 'Los registros aparecerán aquí cuando comience la compilación.',
  },
  'PPU Settings (Object Detection only)': {
    ko: 'PPU 설정 (객체 검출 전용)', ja: 'PPU 設定 (物体検出専用)',
    'zh-CN': 'PPU 设置 (仅目标检测)', 'zh-TW': 'PPU 設定 (僅物件偵測)',
    es: 'Configuración de PPU (solo detección de objetos)',
  },
  'Enable PPU': {
    ko: 'PPU 활성화', ja: 'PPU 有効化',
    'zh-CN': '启用 PPU', 'zh-TW': '啟用 PPU',
    es: 'Habilitar PPU',
  },
  'Type': {
    ko: '유형', ja: 'タイプ',
    'zh-CN': '类型', 'zh-TW': '類型',
    es: 'Tipo',
  },
  'Num Classes': {
    ko: '클래스 수', ja: 'クラス数',
    'zh-CN': '类别数', 'zh-TW': '類別數',
    es: 'Núm. de clases',
  },
  'Layer Config (JSON)': {
    ko: '레이어 구성 (JSON)', ja: 'レイヤー設定 (JSON)',
    'zh-CN': '层配置 (JSON)', 'zh-TW': '層設定 (JSON)',
    es: 'Configuración de capa (JSON)',
  },

  /* Compiler tips/descriptions */
  'Maximize NPU utilization (improves performance on some models)': {
    ko: 'NPU 활용도 극대화 (일부 모델 성능 향상)', ja: 'NPU 使用率を最大化 (一部のモデルでパフォーマンスが向上します)',
    'zh-CN': '最大化NPU利用率 (可提升部分模型的性能)', 'zh-TW': '最大化NPU利用率 (可提升部分模型的效能)',
    es: 'Maximice la utilización del NPU (mejora el rendimiento en algunos modelos)',
  },
  'Improves quantization accuracy. P0=faster, P5=more accurate (DX-COM v2.1+)': {
    ko: '양자화 정확도 향상. P0=빠름, P5=정확도 높음 (DX-COM v2.1+)', ja: '量子化精度を向上させます。P0=高速、P5=高精度 (DX-COM v2.1+)',
    'zh-CN': '提升量化精度。P0=更快，P5=更精确 (DX-COM v2.1+)', 'zh-TW': '提升量化精度。P0=更快，P5=更精確 (DX-COM v2.1+)',
    es: 'Mejora la precisión de cuantización. P0=más rápido, P5=más preciso (DX-COM v2.1+)',
  },
  'Calibration device — select CUDA for faster calibration if a GPU is available': {
    ko: '보정 디바이스 — GPU가 있으면 CUDA를 선택하여 빠른 보정', ja: 'キャリブレーションデバイス — GPUが利用可能な場合はCUDAを選択すると高速化されます',
    'zh-CN': '校准设备 — 如有GPU可用，选择CUDA以加快校准速度', 'zh-TW': '校準裝置 — 如有GPU可用，選擇CUDA以加快校準速度',
    es: 'Dispositivo de calibración — seleccione CUDA para calibración más rápida si hay GPU disponible',
  },
  'Click or drag to upload an ONNX file': {
    ko: '클릭 또는 드래그하여 ONNX 파일 업로드', ja: 'クリックまたはドラッグしてONNXファイルをアップロード',
    'zh-CN': '点击或拖拽上传ONNX文件', 'zh-TW': '點擊或拖曳上傳ONNX檔案',
    es: 'Haga clic o arrastre para subir un archivo ONNX',
  },
  'Or enter a server path below': {
    ko: '또는 아래에 서버 경로 입력', ja: 'または下にサーバーパスを入力',
    'zh-CN': '或在下方输入服务器路径', 'zh-TW': '或在下方輸入伺服器路徑',
    es: 'O introduzca una ruta del servidor abajo',
  },
  'Upload an ONNX file to inspect the model graph': {
    ko: 'ONNX 파일을 업로드하여 모델 그래프 검사', ja: 'ONNXファイルをアップロードしてモデルグラフを検査',
    'zh-CN': '上传ONNX文件以检查模型图', 'zh-TW': '上傳ONNX檔案以檢查模型圖',
    es: 'Suba un archivo ONNX para inspeccionar el gráfico del modelo',
  },

  /* ==== Outputs ==== */
  'Size': {
    ko: '크기', ja: 'サイズ',
    'zh-CN': '大小', 'zh-TW': '大小',
    es: 'Tamaño',
  },
  'Modified': {
    ko: '수정일', ja: '更新日時',
    'zh-CN': '修改日期', 'zh-TW': '修改日期',
    es: 'Modificado',
  },
  'No output files yet.': {
    ko: '아직 출력 파일이 없습니다.', ja: '出力ファイルはまだありません。',
    'zh-CN': '尚无输出文件。', 'zh-TW': '尚無輸出檔案。',
    es: 'Sin archivos de salida aún.',
  },

  /* ==== Planner ==== */
  'Configuration': {
    ko: '구성', ja: '構成',
    'zh-CN': '配置', 'zh-TW': '組態',
    es: 'Configuración',
  },
  'Workload Tasks': {
    ko: '워크로드 작업', ja: 'ワークロードタスク',
    'zh-CN': '工作负载任务', 'zh-TW': '工作負載任務',
    es: 'Tareas de carga de trabajo',
  },
  'Target FPS (per channel)': {
    ko: '목표 FPS (채널당)', ja: '目標FPS (チャンネルあたり)',
    'zh-CN': '目标FPS (每通道)', 'zh-TW': '目標FPS (每通道)',
    es: 'FPS objetivo (por canal)',
  },
  'Operating Hours': {
    ko: '운영 시간', ja: '稼働時間',
    'zh-CN': '运营时间', 'zh-TW': '營運時間',
    es: 'Horas de operación',
  },
  'TCO Period': {
    ko: 'TCO 기간', ja: 'TCO 期間',
    'zh-CN': 'TCO 周期', 'zh-TW': 'TCO 期間',
    es: 'Período de TCO',
  },
  'Currency / Region': {
    ko: '통화 / 지역', ja: '通貨 / 地域',
    'zh-CN': '货币 / 地区', 'zh-TW': '貨幣 / 地區',
    es: 'Moneda / Región',
  },
  'Electricity Rate': {
    ko: '전기 요금', ja: '電気料金',
    'zh-CN': '电费费率', 'zh-TW': '電費費率',
    es: 'Tarifa de electricidad',
  },
  'Response Latency': {
    ko: '응답 지연시간', ja: '応答レイテンシ',
    'zh-CN': '响应延迟', 'zh-TW': '回應延遲',
    es: 'Latencia de respuesta',
  },
  'Hardware Sizing & Cost': {
    ko: '하드웨어 규모 산정 & 비용', ja: 'ハードウェア規模算定 & コスト',
    'zh-CN': '硬件规模估算 & 成本', 'zh-TW': '硬體規模估算 & 成本',
    es: 'Dimensionamiento y costo de hardware',
  },
  'TCO Comparison': {
    ko: 'TCO 비교', ja: 'TCO 比較',
    'zh-CN': 'TCO 比较', 'zh-TW': 'TCO 比較',
    es: 'Comparación de TCO',
  },
  'Break-Even Timeline': {
    ko: '손익분기 타임라인', ja: '損益分岐タイムライン',
    'zh-CN': '盈亏平衡时间线', 'zh-TW': '損益平衡時間線',
    es: 'Línea de tiempo del punto de equilibrio',
  },
  'Scaling Curve': {
    ko: '스케일링 곡선', ja: 'スケーリング曲線',
    'zh-CN': '扩展曲线', 'zh-TW': '擴展曲線',
    es: 'Curva de escalado',
  },
  '1 Year': {
    ko: '1년', ja: '1年',
    'zh-CN': '1年', 'zh-TW': '1年',
    es: '1 año',
  },
  '3 Years': {
    ko: '3년', ja: '3年',
    'zh-CN': '3年', 'zh-TW': '3年',
    es: '3 años',
  },
  '5 Years': {
    ko: '5년', ja: '5年',
    'zh-CN': '5年', 'zh-TW': '5年',
    es: '5 años',
  },
  'Business (12h)': {
    ko: '업무시간 (12시간)', ja: '営業時間 (12時間)',
    'zh-CN': '工作时间 (12小时)', 'zh-TW': '工作時間 (12小時)',
    es: 'Horario laboral (12 h)',
  },
  '24/7': {
    ko: '24/7', ja: '24/7',
    'zh-CN': '24/7', 'zh-TW': '24/7',
    es: '24/7',
  },
  'Cloud AI Cost (simulated)': {
    ko: '클라우드 AI 비용 (시뮬레이션)', ja: 'クラウドAIコスト (シミュレーション)',
    'zh-CN': '云端AI成本 (模拟)', 'zh-TW': '雲端AI成本 (模擬)',
    es: 'Costo de IA en la nube (simulado)',
  },
  'DEEPX Electricity Cost': {
    ko: 'DEEPX 전기 비용', ja: 'DEEPX 電気コスト',
    'zh-CN': 'DEEPX 电力成本', 'zh-TW': 'DEEPX 電力成本',
    es: 'Costo de electricidad DEEPX',
  },
  'Based on GPT-4o Vision API pricing (simulated)': {
    ko: 'GPT-4o 비전 API 요금 기반 (시뮬레이션)', ja: 'GPT-4o Vision API 料金に基づく (シミュレーション)',
    'zh-CN': '基于GPT-4o Vision API定价 (模拟)', 'zh-TW': '基於GPT-4o Vision API定價 (模擬)',
    es: 'Basado en precios de GPT-4o Vision API (simulado)',
  },
  'DX-M1 @ 3W TDP actual power cost': {
    ko: 'DX-M1 @ 3W TDP 실제 전력 비용', ja: 'DX-M1 @ 3W TDP 実際の消費電力コスト',
    'zh-CN': 'DX-M1 @ 3W TDP 实际功耗成本', 'zh-TW': 'DX-M1 @ 3W TDP 實際功耗成本',
    es: 'DX-M1 @ 3W TDP costo real de potencia',
  },
  'Inference + Network Round-Trip': {
    ko: '추론 + 네트워크 왕복 시간', ja: '推論 + ネットワーク往復時間',
    'zh-CN': '推理 + 网络往返时间', 'zh-TW': '推論 + 網路往返時間',
    es: 'Inferencia + viaje de ida y vuelta de red',
  },
  'Monthly cumulative cost vs. Cloud': {
    ko: '월간 누적 비용 vs. 클라우드', ja: '月間累計コスト vs. クラウド',
    'zh-CN': '月度累计成本 vs. 云端', 'zh-TW': '每月累計成本 vs. 雲端',
    es: 'Costo acumulado mensual vs. Cloud',
  },
  'Cost curve as camera count scales': {
    ko: '카메라 수 증가에 따른 비용 곡선', ja: 'カメラ台数増加に伴うコスト曲線',
    'zh-CN': '随摄像头数量增加的成本曲线', 'zh-TW': '隨攝影機數量增加的成本曲線',
    es: 'Curva de costo al escalar la cantidad de cámaras',
  },
  'Smart Factory': {
    ko: '스마트 팩토리', ja: 'スマートファクトリー',
    'zh-CN': '智能工厂', 'zh-TW': '智慧工廠',
    es: 'Fábrica inteligente',
  },
  'Unmanned Store': {
    ko: '무인 매장', ja: '無人店舗',
    'zh-CN': '无人商店', 'zh-TW': '無人商店',
    es: 'Tienda autónoma',
  },
  'Intelligent CCTV': {
    ko: '지능형 CCTV', ja: 'インテリジェント CCTV',
    'zh-CN': '智能 CCTV', 'zh-TW': '智慧 CCTV',
    es: 'CCTV inteligente',
  },
  'Autonomous Robot': {
    ko: '자율 로봇', ja: '自律ロボット',
    'zh-CN': '自主机器人', 'zh-TW': '自主機器人',
    es: 'Robot autónomo',
  },
  'Smart Farm': {
    ko: '스마트 팜', ja: 'スマートファーム',
    'zh-CN': '智慧农场', 'zh-TW': '智慧農場',
    es: 'Granja inteligente',
  },
  'Add Task': {
    ko: '작업 추가', ja: 'タスク追加',
    'zh-CN': '添加任务', 'zh-TW': '新增任務',
    es: 'Agregar tarea',
  },

  /* Planner warning badges */
  'GDPR/Privacy law: Cloud unsuitable — cross-border video transfer restricted': {
    ko: 'GDPR/개인정보보호법: 클라우드 부적합 — 국경 간 영상 전송 제한',
    ja: 'GDPR/プライバシー法: クラウドは不適 — 国境を越えた映像転送が制限されます',
    'zh-CN': 'GDPR/隐私法：云端不适用——跨境视频传输受限',
    'zh-TW': 'GDPR/隱私法：雲端不適用——跨境影像傳輸受限',
    es: 'Ley GDPR/de privacidad: la nube no es adecuada: transferencia de video transfronteriza restringida',
  },
  'Edge AI: offline operation supported — works even without internet': {
    ko: '엣지 AI: 오프라인 운영 지원 — 인터넷 없이도 동작',
    ja: 'エッジAI: オフライン動作に対応 — インターネットなしでも動作します',
    'zh-CN': '边缘 AI：支持离线运行——无需联网也能工作',
    'zh-TW': '邊緣 AI：支援離線運行——無需連網也能運作',
    es: 'IA en el borde: funcionamiento sin conexión — funciona incluso sin internet',
  },

  /* Planner summary stats */
  'CAPEX': {
    ko: 'CAPEX (초기비용)', ja: 'CAPEX',
    'zh-CN': 'CAPEX', 'zh-TW': 'CAPEX',
    es: 'CAPEX',
  },
  'Electricity': {
    ko: '전기 비용', ja: '電気代',
    'zh-CN': '电费', 'zh-TW': '電費',
    es: 'Electricidad',
  },
  'Maintenance': {
    ko: '유지보수', ja: 'メンテナンス',
    'zh-CN': '维护', 'zh-TW': '維護',
    es: 'Mantenimiento',
  },
  'Savings vs Cloud': {
    ko: '클라우드 대비 절감액', ja: 'クラウドと比較した節約額',
    'zh-CN': '相比云端节省', 'zh-TW': '相比雲端節省',
    es: 'Ahorro vs Nube',
  },
  'Break-Even': {
    ko: '손익분기점', ja: '損益分岐点',
    'zh-CN': '盈亏平衡点', 'zh-TW': '損益平衡點',
    es: 'Punto de equilibrio',
  },
  'CO₂ Saved': {
    ko: 'CO₂ 절감량', ja: 'CO₂ 削減量',
    'zh-CN': 'CO₂ 减排量', 'zh-TW': 'CO₂ 減碳量',
    es: 'CO₂ ahorrado',
  },
  'months': {
    ko: '개월', ja: 'ヶ月',
    'zh-CN': '个月', 'zh-TW': '個月',
    es: 'meses',
  },
  'year': {
    ko: '년', ja: '年',
    'zh-CN': '年', 'zh-TW': '年',
    es: 'año',
  },

  /* Planner chart labels */
  'CapEx (Hardware)': {
    ko: 'CapEx (하드웨어)', ja: 'CapEx (ハードウェア)',
    'zh-CN': 'CapEx (硬件)', 'zh-TW': 'CapEx (硬體)',
    es: 'CapEx (hardware)',
  },
  'OpEx (Electricity)': {
    ko: 'OpEx (전기 비용)', ja: 'OpEx (電気代)',
    'zh-CN': 'OpEx (电费)', 'zh-TW': 'OpEx (電費)',
    es: 'OpEx (Electricidad)',
  },
  'OpEx (Cloud Svc)': {
    ko: 'OpEx (클라우드 서비스)', ja: 'OpEx (クラウドサービス)',
    'zh-CN': 'OpEx (云服务)', 'zh-TW': 'OpEx (雲端服務)',
    es: 'OpEx (Servicio en la nube)',
  },
  'Bandwidth (line)': {
    ko: '대역폭 (회선)', ja: '帯域幅 (回線)',
    'zh-CN': '带宽 (线路)', 'zh-TW': '頻寬 (線路)',
    es: 'Ancho de banda (línea)',
  },
  'BEST': {
    ko: '최적', ja: '最適',
    'zh-CN': '最佳', 'zh-TW': '最佳',
    es: 'MEJOR',
  },

  /* ==== Developer modal ==== */
  'Developer Mode': {
    ko: '개발자 모드', ja: '開発者モード',
    'zh-CN': '开发者模式', 'zh-TW': '開發者模式',
    es: 'Modo de desarrollador',
  },
  'Authenticate': {
    ko: '인증', ja: '認証',
    'zh-CN': '认证', 'zh-TW': '驗證',
    es: 'Autenticar',
  },
  'Add Model': {
    ko: '모델 추가', ja: 'モデルを追加',
    'zh-CN': '添加模型', 'zh-TW': '新增模型',
    es: 'Agregar modelo',
  },
  'Delete Model': {
    ko: '모델 삭제', ja: 'モデルを削除',
    'zh-CN': '删除模型', 'zh-TW': '刪除模型',
    es: 'Eliminar modelo',
  },
  'Skeleton': {
    ko: '스켈레톤', ja: 'スケルトン',
    'zh-CN': '骨架', 'zh-TW': '骨架',
    es: 'Esqueleto',
  },
  'Git Commit': {
    ko: 'Git 커밋', ja: 'Git コミット',
    'zh-CN': 'Git 提交', 'zh-TW': 'Git 提交',
    es: 'Commit de Git',
  },
  'Extract Pkg': {
    ko: '패키지 추출', ja: 'パッケージ抽出',
    'zh-CN': '提取包', 'zh-TW': '擷取套件',
    es: 'Extraer paquete',
  },
  'Model Name': {
    ko: '모델 이름', ja: 'モデル名',
    'zh-CN': '模型名称', 'zh-TW': '模型名稱',
    es: 'Nombre del modelo',
  },
  'Task Type': {
    ko: '작업 유형', ja: 'タスクタイプ',
    'zh-CN': '任务类型', 'zh-TW': '任務類型',
    es: 'Tipo de tarea',
  },
  'Postprocessor': {
    ko: '후처리기', ja: '後処理',
    'zh-CN': '后处理器', 'zh-TW': '後處理器',
    es: 'Post-procesador',
  },
  'Sync only': {
    ko: '동기 전용', ja: '同期のみ',
    'zh-CN': '仅同步', 'zh-TW': '僅同步',
    es: 'Solo síncrono',
  },
  'Task Name': {
    ko: '작업 이름', ja: 'タスク名',
    'zh-CN': '任务名称', 'zh-TW': '任務名稱',
    es: 'Nombre de tarea',
  },
  'Create Skeleton': {
    ko: '스켈레톤 생성', ja: 'スケルトン作成',
    'zh-CN': '创建骨架', 'zh-TW': '建立骨架',
    es: 'Crear esqueleto',
  },
  'Commit Message': {
    ko: '커밋 메시지', ja: 'コミットメッセージ',
    'zh-CN': '提交信息', 'zh-TW': '提交訊息',
    es: 'Mensaje de commit',
  },
  'Push after commit': {
    ko: '커밋 후 푸시', ja: 'コミット後にプッシュ',
    'zh-CN': '提交后推送', 'zh-TW': '提交後推送',
    es: 'Push después de confirmar',
  },
  'Commit': {
    ko: '커밋', ja: 'コミット',
    'zh-CN': '提交', 'zh-TW': '提交',
    es: 'Confirmar',
  },
  'Extract Package': {
    ko: '패키지 추출', ja: 'パッケージ抽出',
    'zh-CN': '提取包', 'zh-TW': '擷取套件',
    es: 'Extraer paquete',
  },
  'Select Model': {
    ko: '모델 선택', ja: 'モデルを選択',
    'zh-CN': '选择模型', 'zh-TW': '選擇模型',
    es: 'Seleccionar modelo',
  },
  'Search': {
    ko: '검색', ja: '検索',
    'zh-CN': '搜索', 'zh-TW': '搜尋',
    es: 'Buscar',
  },

  /* ==== ROI modal ==== */
  'Select Region of Interest': {
    ko: '관심 영역 선택', ja: '関心領域を選択',
    'zh-CN': '选择感兴趣区域', 'zh-TW': '選擇感興趣區域',
    es: 'Seleccionar región de interés',
  },
  'Drag to select region': {
    ko: '드래그하여 영역 선택', ja: 'ドラッグして領域を選択',
    'zh-CN': '拖动选择区域', 'zh-TW': '拖曳選擇區域',
    es: 'Arrastre para seleccionar región',
  },
  'Apply ROI': {
    ko: 'ROI 적용', ja: 'ROIを適用',
    'zh-CN': '应用 ROI', 'zh-TW': '套用 ROI',
    es: 'Aplicar ROI',
  },
  /* ==== File browser ==== */
  'Select File': {
    ko: '파일 선택', ja: 'ファイルを選択',
    'zh-CN': '选择文件', 'zh-TW': '選擇檔案',
    es: 'Seleccionar archivo',
  },
  'Select': {
    ko: '선택', ja: '選択',
    'zh-CN': '选择', 'zh-TW': '選擇',
    es: 'Seleccionar',
  },

  /* ==== NPU Monitor float ==== */
  'NPU Monitor': {
    ko: 'NPU 모니터', ja: 'NPU モニター',
    'zh-CN': 'NPU 监控', 'zh-TW': 'NPU 監控',
    es: 'Monitor NPU',
  },
  'Avg Temp': {
    ko: '평균 온도', ja: '平均温度',
    'zh-CN': '平均温度', 'zh-TW': '平均溫度',
    es: 'Temp. promedio',
  },
  'Voltage': {
    ko: '전압', ja: '電圧',
    'zh-CN': '电压', 'zh-TW': '電壓',
    es: 'Voltaje',
  },

  /* ==== Compile test modal ==== */
  'Test Run — Select Pipeline': {
    ko: '테스트 실행 — 파이프라인 선택', ja: 'テスト実行 — パイプライン選択',
    'zh-CN': '测试运行 — 选择流水线', 'zh-TW': '測試執行 — 選擇管線',
    es: 'Ejecución de prueba — Seleccionar pipeline',
  },
  'Preprocessor': {
    ko: '전처리기', ja: '前処理',
    'zh-CN': '预处理器', 'zh-TW': '前處理器',
    es: 'Pre-procesador',
  },
  'Visualizer': {
    ko: '시각화기', ja: 'ビジュアライザ',
    'zh-CN': '可视化器', 'zh-TW': '視覺化器',
    es: 'Visualizador',
  },
  'Recommended Pipelines by Category': {
    ko: '카테고리별 권장 파이프라인', ja: 'カテゴリ別の推奨パイプライン',
    'zh-CN': '按类别推荐的流水线', 'zh-TW': '依類別推薦的管線',
    es: 'Pipelines recomendados por categoría',
  },
  'Deploy?': {
    ko: '배포?', ja: 'デプロイしますか？',
    'zh-CN': '是否部署？', 'zh-TW': '是否部署？',
    es: '¿Desplegar?',
  },
  'Reconfigure': {
    ko: '재구성', ja: '再構成',
    'zh-CN': '重新配置', 'zh-TW': '重新組態',
    es: 'Reconfigurar',
  },
  'Confirm Deploy': {
    ko: '배포 확인', ja: 'デプロイを確認',
    'zh-CN': '确认部署', 'zh-TW': '確認部署',
    es: 'Confirmar despliegue',
  },
  'Select Sample Image': {
    ko: '샘플 이미지 선택', ja: 'サンプル画像を選択',
    'zh-CN': '选择示例图像', 'zh-TW': '選擇範例影像',
    es: 'Seleccionar imagen de muestra',
  },

  /* ==== Buttons with emoji ==== */
  '＋ Add Model': {
    ko: '＋ 모델 추가', ja: '＋ モデル追加',
    'zh-CN': '＋ 添加模型', 'zh-TW': '＋ 新增模型',
    es: '＋ Agregar modelo',
  },
  '↩ Reconfigure': {
    ko: '↩ 재구성', ja: '↩ 再設定',
    'zh-CN': '↩ 重新配置', 'zh-TW': '↩ 重新設定',
    es: '↩ Reconfigurar',
  },
  '+ Add Task': {
    ko: '+ 작업 추가', ja: '+ タスク追加',
    'zh-CN': '+ 添加任务', 'zh-TW': '+ 新增任務',
    es: '+ Agregar tarea',
  },

  /* ==== Setup titles with emoji ==== */


  /* ==== Dashboard sections with emoji ==== */

  /* ==== Topbar page titles (with emoji) ==== */

  /* ==== Misc ==== */
  'MEM': {
    ko: '메모리', ja: 'メモリ',
    'zh-CN': '内存', 'zh-TW': '記憶體',
    es: 'MEM',
  },
  'NPU Dashboard v2.0': {
    ko: 'NPU 대시보드 v2.0', ja: 'NPU ダッシュボード v2.0',
    'zh-CN': 'NPU 仪表板 v2.0', 'zh-TW': 'NPU 儀表板 v2.0',
    es: 'Panel de control NPU v2.0',
  },
  'PASS': {
    ko: '통과', ja: '合格',
    'zh-CN': '通过', 'zh-TW': '通過',
    es: 'APROBADO',
  },
  'FAIL': {
    ko: '실패', ja: '失敗',
    'zh-CN': '失败', 'zh-TW': '失敗',
    es: 'FALLO',
  },
  'Inspect': {
    ko: '검사', ja: '検査',
    'zh-CN': '检查', 'zh-TW': '檢查',
    es: 'Inspeccionar',
  },
  'Netron ↗': {
    ko: 'Netron ↗', ja: 'Netron ↗',
    'zh-CN': 'Netron ↗', 'zh-TW': 'Netron ↗',
    es: 'Netron ↗',
  },
  'Both (C++ & Python)': {
    ko: '모두 (C++ & Python)', ja: '両方 (C++ & Python)',
    'zh-CN': '两者 (C++ & Python)', 'zh-TW': '兩者 (C++ & Python)',
    es: 'Ambos (C++ y Python)',
  },
  'Both': {
    ko: '모두', ja: '両方',
    'zh-CN': '两者', 'zh-TW': '兩者',
    es: 'Ambos',
  },
  'C++ only': {
    ko: 'C++ 전용', ja: 'C++ のみ',
    'zh-CN': '仅 C++', 'zh-TW': '僅 C++',
    es: 'Solo C++',
  },
  'Python only': {
    ko: 'Python 전용', ja: 'Python のみ',
    'zh-CN': '仅 Python', 'zh-TW': '僅 Python',
    es: 'Solo Python',
  },
  'vs': {
    ko: 'vs', ja: 'vs',
    'zh-CN': 'vs', 'zh-TW': 'vs',
    es: 'vs',
  },
  'Cores': {
    ko: '코어', ja: 'コア',
    'zh-CN': '核心', 'zh-TW': '核心',
    es: 'Núcleos',
  },
  'Available': {
    ko: '사용 가능', ja: '利用可能',
    'zh-CN': '可用', 'zh-TW': '可用',
    es: 'Disponible',
  },

  /* ==== Benchmark ==== */
  'All Categories': {
    ko: '전체 카테고리', ja: 'すべてのカテゴリ',
    'zh-CN': '全部类别', 'zh-TW': '全部類別',
    es: 'Todas las categorías',
  },
  'Default (built-in)': {
    ko: '기본 (내장)', ja: 'デフォルト (内蔵)',
    'zh-CN': '默认 (内置)', 'zh-TW': '預設 (內建)',
    es: 'Por defecto (incorporado)',
  },
  'Select models to benchmark': {
    ko: '벤치마크할 모델을 선택하세요', ja: 'ベンチマークするモデルを選択してください',
    'zh-CN': '选择要进行基准测试的模型', 'zh-TW': '選擇要進行基準測試的模型',
    es: 'Seleccione modelos para benchmark',
  },
  'Running...': {
    ko: '실행 중...', ja: '実行中...',
    'zh-CN': '运行中...', 'zh-TW': '執行中...',
    es: 'Ejecutando...',
  },
  'Start Benchmark': {
    ko: '벤치마크 시작', ja: 'ベンチマーク開始',
    'zh-CN': '开始基准测试', 'zh-TW': '開始基準測試',
    es: 'Iniciar benchmark',
  },
  'Benchmark complete': {
    ko: '벤치마크 완료', ja: 'ベンチマーク完了',
    'zh-CN': '基准测试完成', 'zh-TW': '基準測試完成',
    es: 'Benchmark completo',
  },
  'No data — run benchmark first': {
    ko: '데이터 없음 — 벤치마크를 먼저 실행하세요', ja: 'データなし — まずベンチマークを実行してください',
    'zh-CN': '无数据 — 请先运行基准测试', 'zh-TW': '無資料 — 請先執行基準測試',
    es: 'Sin datos — ejecute benchmark primero',
  },
  'No benchmark results to export': {
    ko: '내보낼 벤치마크 결과가 없습니다', ja: 'エクスポートするベンチマーク結果がありません',
    'zh-CN': '没有可导出的基准测试结果', 'zh-TW': '沒有可匯出的基準測試結果',
    es: 'Sin resultados de benchmark para exportar',
  },
  'Benchmark report downloaded': {
    ko: '벤치마크 리포트가 다운로드되었습니다', ja: 'ベンチマークレポートがダウンロードされました',
    'zh-CN': '基准测试报告已下载', 'zh-TW': '基準測試報告已下載',
    es: 'Informe de benchmark descargado',
  },
  'Frame Count': {
    ko: '프레임 수', ja: 'フレーム数',
    'zh-CN': '帧数', 'zh-TW': '幀數',
    es: 'Conteo de cuadros',
  },
  'Loop Count': {
    ko: '반복 횟수', ja: 'ループ回数',
    'zh-CN': '循环次数', 'zh-TW': '迴圈次數',
    es: 'Conteo de bucles',
  },
  'Results': {
    ko: '결과', ja: '結果',
    'zh-CN': '结果', 'zh-TW': '結果',
    es: 'Resultados',
  },
  'click row for detail': {
    ko: '상세 보기는 행을 클릭하세요', ja: '行をクリックして詳細を表示',
    'zh-CN': '点击行查看详情', 'zh-TW': '點擊列查看詳細資訊',
    es: 'haga clic en la fila para detalles',
  },
  'FPS Comparison': {
    ko: 'FPS 비교', ja: 'FPS 比較',
    'zh-CN': 'FPS 对比', 'zh-TW': 'FPS 比較',
    es: 'Comparación de FPS',
  },
  'Original': {
    ko: '원본', ja: 'オリジナル',
    'zh-CN': '原始', 'zh-TW': '原始',
    es: 'Original',
  },
  'Result': {
    ko: '결과', ja: '結果',
    'zh-CN': '结果', 'zh-TW': '結果',
    es: 'Resultado',
  },
  'Comparison disabled: original and result use different aspect ratios.': {
    ko: '원본과 결과의 가로세로 비율이 달라 비교를 비활성화했습니다.', ja: '元画像と結果画像の縦横比が異なるため、比較を無効にしました。',
    'zh-CN': '原始图像和结果图像的宽高比不同，已禁用对比。', 'zh-TW': '原始影像和結果影像的長寬比不同，已停用比較。',
    es: 'La comparación se desactivó porque la imagen original y el resultado tienen relaciones de aspecto diferentes.',
  },
  'Comparison unavailable: result image could not be decoded.': {
    ko: '결과 이미지를 디코딩할 수 없어 비교할 수 없습니다.', ja: '結果画像をデコードできないため、比較できません。',
    'zh-CN': '无法解码结果图像，无法进行对比。', 'zh-TW': '無法解碼結果影像，無法進行比較。',
    es: 'La comparación no está disponible porque no se pudo decodificar la imagen del resultado.',
  },
  'Total': {
    ko: '합계', ja: '合計',
    'zh-CN': '总计', 'zh-TW': '總計',
    es: 'Total',
  },
  'HW State After Run': {
    ko: '실행 후 HW 상태', ja: '実行後のHW状態',
    'zh-CN': '运行后硬件状态', 'zh-TW': '執行後硬體狀態',
    es: 'Estado de HW después de ejecución',
  },
  'Full Output': {
    ko: '전체 출력', ja: '全出力',
    'zh-CN': '完整输出', 'zh-TW': '完整輸出',
    es: 'Salida completa',
  },
  'Benchmark Detail': {
    ko: '벤치마크 상세', ja: 'ベンチマーク詳細',
    'zh-CN': '基准测试详情', 'zh-TW': '基準測試詳情',
    es: 'Detalle del benchmark',
  },
  'Export Report': {
    ko: '리포트 내보내기', ja: 'レポートをエクスポート',
    'zh-CN': '导出报告', 'zh-TW': '匯出報告',
    es: 'Exportar informe',
  },
  'auto-selected': {
    ko: '자동 선택됨', ja: '自動選択済み',
    'zh-CN': '已自动选择', 'zh-TW': '已自動選擇',
    es: 'auto-seleccionado',
  },
  'not found in model list': {
    ko: '모델 목록에 없음', ja: 'モデルリストに見つかりません',
    'zh-CN': '在模型列表中未找到', 'zh-TW': '在模型列表中未找到',
    es: 'no encontrado en la lista de modelos',
  },

  /* ==== Compiler (toast/UI) ==== */
  'JSON config loaded': {
    ko: 'JSON 설정 로드됨', ja: 'JSON 設定が読み込まれました',
    'zh-CN': 'JSON 配置已加载', 'zh-TW': 'JSON 設定已載入',
    es: 'Configuración JSON cargada',
  },
  'Invalid JSON': {
    ko: '잘못된 JSON', ja: '無効な JSON',
    'zh-CN': '无效的 JSON', 'zh-TW': '無效的 JSON',
    es: 'JSON inválido',
  },
  'Please drop a .json file': {
    ko: '.json 파일을 드롭하세요', ja: '.json ファイルをドロップしてください',
    'zh-CN': '请拖放 .json 文件', 'zh-TW': '請拖放 .json 檔案',
    es: 'Por favor suelte un archivo .json',
  },
  'Use the path input or browse button to select a server folder': {
    ko: '서버 폴더를 선택하려면 경로 입력 또는 찾아보기 사용', ja: 'パス入力または参照ボタンを使用してサーバーフォルダを選択してください',
    'zh-CN': '使用路径输入或浏览按钮选择服务器文件夹', 'zh-TW': '使用路徑輸入或瀏覽按鈕選擇伺服器資料夾',
    es: 'Use la entrada de ruta o el botón explorar para seleccionar una carpeta del servidor',
  },
  'Run install.sh to install': {
    ko: 'install.sh을 실행하여 설치하세요', ja: 'install.sh を実行してインストールしてください',
    'zh-CN': '运行 install.sh 进行安装', 'zh-TW': '執行 install.sh 進行安裝',
    es: 'Ejecute install.sh para instalar',
  },
  'dx-compiler directory not found': {
    ko: 'dx-compiler 디렉터리를 찾을 수 없음', ja: 'dx-compiler ディレクトリが見つかりません',
    'zh-CN': '未找到 dx-compiler 目录', 'zh-TW': '未找到 dx-compiler 目錄',
    es: 'Directorio dx-compiler no encontrado',
  },
  'Status check failed': {
    ko: '상태 확인 실패', ja: 'ステータス確認失敗',
    'zh-CN': '状态检查失败', 'zh-TW': '狀態檢查失敗',
    es: 'Error en la verificación del estado',
  },
  'Uploading: ': {
    ko: '업로드 중: ', ja: 'アップロード中: ',
    'zh-CN': '上传中: ', 'zh-TW': '上傳中: ',
    es: 'Subiendo: ',
  },
  'Click to select a different file': {
    ko: '다른 파일을 선택하려면 클릭', ja: 'クリックして別のファイルを選択',
    'zh-CN': '点击选择其他文件', 'zh-TW': '點擊選擇其他檔案',
    es: 'Haga clic para seleccionar un archivo diferente',
  },
  'Please enter an ONNX path': {
    ko: 'ONNX 경로를 입력해주세요', ja: 'ONNXパスを入力してください',
    'zh-CN': '请输入ONNX路径', 'zh-TW': '請輸入ONNX路徑',
    es: 'Por favor introduzca una ruta ONNX',
  },
  'No ONNX info': {
    ko: 'ONNX 정보 없음', ja: 'ONNX 情報なし',
    'zh-CN': '无ONNX信息', 'zh-TW': '無ONNX資訊',
    es: 'Sin información ONNX',
  },
  'Please specify an ONNX file first': {
    ko: 'ONNX 파일을 먼저 지정하세요', ja: '先にONNXファイルを指定してください',
    'zh-CN': '请先指定ONNX文件', 'zh-TW': '請先指定ONNX檔案',
    es: 'Por favor especifique un archivo ONNX primero',
  },
  'No preprocessing steps. Add one below.': {
    ko: '전처리 단계가 없습니다. 아래에서 추가하세요.', ja: '前処理ステップがありません。下から追加してください。',
    'zh-CN': '无预处理步骤。请在下方添加。', 'zh-TW': '無前處理步驟。請在下方新增。',
    es: 'No hay pasos de preprocesamiento. Agregue uno a continuación.',
  },
  'Preset applied: ': {
    ko: '프리셋 적용됨: ', ja: 'プリセット適用: ',
    'zh-CN': '预设已应用: ', 'zh-TW': '預設已套用: ',
    es: 'Preset aplicado: ',
  },
  'JSON config loaded from server': {
    ko: '서버에서 JSON 설정 로드됨', ja: 'サーバーからJSON設定が読み込まれました',
    'zh-CN': '已从服务器加载JSON配置', 'zh-TW': '已從伺服器載入JSON設定',
    es: 'Configuración JSON cargada del servidor',
  },
  'JSON config applied: ': {
    ko: 'JSON 설정 적용됨: ', ja: 'JSON 設定適用: ',
    'zh-CN': 'JSON 配置已应用: ', 'zh-TW': 'JSON 設定已套用: ',
    es: 'Configuración JSON aplicada: ',
  },
  'JSON config file downloaded': {
    ko: 'JSON 설정 파일 다운로드됨', ja: 'JSON設定ファイルがダウンロードされました',
    'zh-CN': 'JSON配置文件已下载', 'zh-TW': 'JSON設定檔已下載',
    es: 'Archivo de configuración JSON descargado',
  },
  'Compilation already in progress': {
    ko: '컴파일이 이미 진행 중입니다', ja: 'コンパイルは既に実行中です',
    'zh-CN': '编译已在进行中', 'zh-TW': '編譯已在進行中',
    es: 'Compilación ya en progreso',
  },
  'Please enter the calibration dataset path': {
    ko: '보정 데이터셋 경로를 입력하세요', ja: 'キャリブレーションデータセットのパスを入力してください',
    'zh-CN': '请输入校准数据集路径', 'zh-TW': '請輸入校準資料集路徑',
    es: 'Por favor introduzca la ruta del dataset de calibración',
  },
  'Compilation succeeded!': {
    ko: '컴파일 성공!', ja: 'コンパイル成功！',
    'zh-CN': '编译成功！', 'zh-TW': '編譯成功！',
    es: '¡Compilación exitosa!',
  },
  'Compilation failed': {
    ko: '컴파일 실패', ja: 'コンパイル失敗',
    'zh-CN': '编译失败', 'zh-TW': '編譯失敗',
    es: 'Compilación fallida',
  },
  'Compilation succeeded': {
    ko: '컴파일 성공', ja: 'コンパイル成功',
    'zh-CN': '编译成功', 'zh-TW': '編譯成功',
    es: 'Compilación exitosa',
  },
  'Duration': {
    ko: '소요시간', ja: '所要時間',
    'zh-CN': '持续时间', 'zh-TW': '持續時間',
    es: 'Duración',
  },
  'Output file': {
    ko: '출력 파일', ja: '出力ファイル',
    'zh-CN': '输出文件', 'zh-TW': '輸出檔案',
    es: 'Archivo de salida',
  },
  'File size': {
    ko: '파일 크기', ja: 'ファイルサイズ',
    'zh-CN': '文件大小', 'zh-TW': '檔案大小',
    es: 'Tamaño de archivo',
  },
  'Output path': {
    ko: '출력 경로', ja: '出力パス',
    'zh-CN': '输出路径', 'zh-TW': '輸出路徑',
    es: 'Ruta de salida',
  },
  'Enter a name for the deployed model:': {
    ko: '배포할 모델 이름을 입력하세요:', ja: 'デプロイするモデルの名前を入力してください:',
    'zh-CN': '请输入部署模型的名称:', 'zh-TW': '請輸入部署模型的名稱:',
    es: 'Introduzca un nombre para el modelo desplegado:',
  },
  'deployed to assets/models/!': {
    ko: 'assets/models/에 배포됨!', ja: 'assets/models/ にデプロイされました！',
    'zh-CN': '已部署到 assets/models/！', 'zh-TW': '已部署到 assets/models/！',
    es: '¡desplegado en assets/models/!',
  },
  'Deployment failed: ': {
    ko: '배포 실패: ', ja: 'デプロイ失敗: ',
    'zh-CN': '部署失败: ', 'zh-TW': '部署失敗: ',
    es: 'Error en el despliegue: ',
  },
  'Navigating to Benchmark': {
    ko: '벤치마크로 이동 중', ja: 'ベンチマークに移動中',
    'zh-CN': '正在导航至基准测试', 'zh-TW': '前往基準測試',
    es: 'Navegando al benchmark',
  },
  'will be auto-selected': {
    ko: '자동 선택됩니다', ja: '自動選択されます',
    'zh-CN': '将被自动选择', 'zh-TW': '將被自動選擇',
    es: 'se seleccionará automáticamente',
  },
  'Deploying…': {
    ko: '배포 중…', ja: 'デプロイ中…',
    'zh-CN': '部署中…', 'zh-TW': '部署中…',
    es: 'Desplegando…',
  },
  'Deployment complete': {
    ko: '배포 완료', ja: 'デプロイ完了',
    'zh-CN': '部署完成', 'zh-TW': '部署完成',
    es: 'Despliegue completo',
  },
  'navigating to Run page…': {
    ko: '실행 페이지로 이동 중…', ja: '実行ページに移動中…',
    'zh-CN': '正在导航到运行页面…', 'zh-TW': '前往執行頁面…',
    es: 'navegando a la página de ejecución…',
  },
  'Running test…': {
    ko: '테스트 실행 중…', ja: 'テスト実行中…',
    'zh-CN': '测试运行中…', 'zh-TW': '測試執行中…',
    es: 'Ejecutando prueba…',
  },
  'Show output': {
    ko: '출력 보기', ja: '出力を表示',
    'zh-CN': '显示输出', 'zh-TW': '顯示輸出',
    es: 'Mostrar salida',
  },
  'Navigated to Run Inference page. Select the deployed model and run inference.': {
    ko: '추론 실행 페이지로 이동했습니다. 배포된 모델을 선택하고 추론을 실행하세요.', ja: '推論実行ページに移動しました。デプロイされたモデルを選択して推論を実行してください。',
    'zh-CN': '已导航至运行推理页面。请选择已部署的模型并运行推理。', 'zh-TW': '切換到執行推論頁面。請選擇已部署的模型並執行推論。',
    es: 'Se navegó a la página de Ejecutar inferencia. Seleccione el modelo desplegado y ejecute la inferencia.',
  },
  'No dxnn file info': {
    ko: 'DXNN 파일 정보 없음', ja: 'DXNN ファイル情報なし',
    'zh-CN': '无 DXNN 文件信息', 'zh-TW': '無 DXNN 檔案資訊',
    es: 'Sin información de archivo dxnn',
  },
  'No DXNN file available': {
    ko: 'DXNN 파일이 없습니다', ja: '利用可能なDXNNファイルがありません',
    'zh-CN': '无可用的DXNN文件', 'zh-TW': '無可用的DXNN檔案',
    es: 'No hay archivo DXNN disponible',
  },
  'Upload an ONNX file and compile it first': {
    ko: 'ONNX 파일을 업로드하고 먼저 컴파일하세요', ja: 'ONNXファイルをアップロードして先にコンパイルしてください',
    'zh-CN': '请先上传ONNX文件并进行编译', 'zh-TW': '請先上傳ONNX檔案並進行編譯',
    es: 'Suba un archivo ONNX y compílelo primero',
  },
  'No ONNX file — only DXNN side available': {
    ko: 'ONNX 파일 없음 — DXNN만 표시 가능', ja: 'ONNXファイルなし — DXNN側のみ利用可能',
    'zh-CN': '无ONNX文件 — 仅DXNN侧可用', 'zh-TW': '無ONNX檔案 — 僅DXNN側可用',
    es: 'Sin archivo ONNX — solo disponible el lado DXNN',
  },
  'No DXNN file — compile first to enable side-by-side': {
    ko: 'DXNN 파일 없음 — 나란히 보기 위해 먼저 컴파일하세요', ja: 'DXNNファイルなし — 並列表示にはまずコンパイルしてください',
    'zh-CN': '无DXNN文件 — 请先编译以启用并排视图', 'zh-TW': '無DXNN檔案 — 請先編譯以啟用並排檢視',
    es: 'Sin archivo DXNN — compile primero para habilitar vista lado a lado',
  },
  'Loading side-by-side view…': {
    ko: '나란히 보기 로드 중…', ja: '並列ビューを読み込み中…',
    'zh-CN': '加载并排视图中…', 'zh-TW': '載入並排檢視中…',
    es: 'Cargando vista lado a lado…',
  },
  'Model file path not found': {
    ko: '모델 파일 경로를 찾을 수 없음', ja: 'モデルファイルパスが見つかりません',
    'zh-CN': '未找到模型文件路径', 'zh-TW': '未找到模型檔案路徑',
    es: 'Ruta de archivo de modelo no encontrada',
  },
  'Failed to send input: ': {
    ko: '입력 전송 실패: ', ja: '入力の送信に失敗: ',
    'zh-CN': '发送输入失败: ', 'zh-TW': '傳送輸入失敗: ',
    es: 'Error al enviar entrada: ',
  },
  'No videos': {
    ko: '비디오 없음', ja: '動画なし',
    'zh-CN': '无视频', 'zh-TW': '無影片',
    es: 'Sin videos',
  },

  /* ==== Inference ==== */
  'Press Run to start inference.': {
    ko: '실행을 눌러 추론을 시작하세요.', ja: '実行を押して推論を開始してください。',
    'zh-CN': '按运行以开始推理。', 'zh-TW': '按執行以開始推論。',
    es: 'Presione Ejecutar para iniciar la inferencia.',
  },
  'Please select an image first': {
    ko: '이미지를 먼저 선택하세요', ja: '先に画像を選択してください',
    'zh-CN': '请先选择图像', 'zh-TW': '請先選擇影像',
    es: 'Por favor seleccione una imagen primero',
  },
  'ROI selected': {
    ko: 'ROI 선택됨', ja: 'ROI が選択されました',
    'zh-CN': 'ROI 已选择', 'zh-TW': 'ROI 已選擇',
    es: 'ROI seleccionado',
  },
  'ROI cleared': {
    ko: 'ROI 해제됨', ja: 'ROI がクリアされました',
    'zh-CN': 'ROI 已清除', 'zh-TW': 'ROI 已清除',
    es: 'ROI limpiado',
  },
  'Select a model': {
    ko: '모델을 선택하세요', ja: 'モデルを選択してください',
    'zh-CN': '请选择模型', 'zh-TW': '請選擇模型',
    es: 'Seleccione un modelo',
  },
  'Model not found': {
    ko: '모델을 찾을 수 없음', ja: 'モデルが見つかりません',
    'zh-CN': '未找到模型', 'zh-TW': '找不到模型',
    es: 'Modelo no encontrado',
  },
  'Stopped': {
    ko: '중지됨', ja: '停止済み',
    'zh-CN': '已停止', 'zh-TW': '已停止',
    es: 'Detenido',
  },
  'Please select a model first': {
    ko: '모델을 먼저 선택하세요', ja: '先にモデルを選択してください',
    'zh-CN': '请先选择模型', 'zh-TW': '請先選擇模型',
    es: 'Por favor seleccione un modelo primero',
  },
  'Extracting...': {
    ko: '추출 중...', ja: '抽出中...',
    'zh-CN': '提取中...', 'zh-TW': '提取中...',
    es: 'Extrayendo...',
  },
  'Extracting package: ': {
    ko: '패키지 추출 중: ', ja: 'パッケージ抽出中: ',
    'zh-CN': '提取包中: ', 'zh-TW': '提取套件中: ',
    es: 'Extrayendo paquete: ',
  },
  'Package saved to the outputs/ folder': {
    ko: '패키지가 outputs/ 폴더에 저장됨', ja: 'パッケージが outputs/ フォルダに保存されました',
    'zh-CN': '包已保存到 outputs/ 文件夹', 'zh-TW': '套件已儲存到 outputs/ 資料夾',
    es: 'Paquete guardado en la carpeta outputs/',
  },
  'Extraction failed': {
    ko: '추출 실패', ja: '抽出失敗',
    'zh-CN': '提取失败', 'zh-TW': '提取失敗',
    es: 'Error en la extracción',
  },
  'You can add up to 8 models': {
    ko: '모델은 최대 8개까지 추가할 수 있습니다', ja: '最大8つのモデルを追加できます',
    'zh-CN': '最多可添加8个模型', 'zh-TW': '最多可新增8個模型',
    es: 'Puede agregar hasta 8 modelos',
  },
  'Please select Category and Model for all slots': {
    ko: '모든 슬롯에서 카테고리와 모델을 선택하세요', ja: 'すべてのスロットでカテゴリとモデルを選択してください',
    'zh-CN': '请为所有槽位选择类别和模型', 'zh-TW': '請為所有插槽選擇類別和模型',
    es: 'Por favor seleccione Categoría y Modelo para todas las ranuras',
  },
  'Please select a video': {
    ko: '비디오를 선택하세요', ja: '動画を選択してください',
    'zh-CN': '请选择视频', 'zh-TW': '請選擇影片',
    es: 'Por favor seleccione un video',
  },
  'Model file not configured: ': {
    ko: '모델 파일 미설정: ', ja: 'モデルファイル未設定: ',
    'zh-CN': '模型文件未配置: ', 'zh-TW': '模型檔案未設定: ',
    es: 'Archivo de modelo no configurado: ',
  },
  'Model file not found: ': {
    ko: '모델 파일 미발견: ', ja: 'モデルファイルが見つかりません: ',
    'zh-CN': '未找到模型文件: ', 'zh-TW': '未找到模型檔案: ',
    es: 'Archivo de modelo no encontrado: ',
  },
  'no_model_file': {
    ko: '모델 파일이 설정되지 않았습니다', ja: 'モデルファイルが設定されていません',
    'zh-CN': '未配置模型文件', 'zh-TW': '未設定模型檔案',
    es: 'Archivo de modelo no configurado',
  },
  // .dxnn files DX-RT cannot read (Model Zoo 2_5_0 = container v9)
  'needs_dxrt': {
    en: 'This model needs DX-RT 3.5.0 or later (.dxnn container v9). The installed DX-RT reads up to v8.',
    ko: '이 모델은 DX-RT 3.5.0 이상이 필요합니다 (.dxnn container v9). 설치된 DX-RT는 v8까지 읽습니다.',
    ja: 'このモデルには DX-RT 3.5.0 以降が必要です (.dxnn container v9)。インストール済みの DX-RT は v8 までです。',
    'zh-CN': '此模型需要 DX-RT 3.5.0 或更高版本 (.dxnn container v9)。已安装的 DX-RT 仅支持到 v8。',
    'zh-TW': '此模型需要 DX-RT 3.5.0 或更新版本 (.dxnn container v9)。已安裝的 DX-RT 僅支援到 v8。',
    es: 'Este modelo requiere DX-RT 3.5.0 o posterior (.dxnn container v9). El DX-RT instalado lee hasta v8.',
  },
  'model_not_found': {
    ko: '모델 파일을 찾을 수 없습니다', ja: 'モデルファイルが見つかりません',
    'zh-CN': '未找到模型文件', 'zh-TW': '找不到模型檔案',
    es: 'Archivo de modelo no encontrado',
  },
  'input_not_found': {
    ko: '입력 파일을 찾을 수 없습니다', ja: '入力ファイルが見つかりません',
    'zh-CN': '未找到输入文件', 'zh-TW': '找不到輸入檔案',
    es: 'Archivo de entrada no encontrado',
  },
  'path_outside_allowed_roots': {
    ko: '허용된 경로 밖의 입력입니다', ja: '許可されたパス外の入力です',
    'zh-CN': '输入路径超出允许范围', 'zh-TW': '輸入路徑超出允許範圍',
    es: 'La ruta está fuera de las carpetas permitidas',
  },
  'file_extension_not_allowed': {
    ko: '허용되지 않은 파일 확장자입니다', ja: '許可されていないファイル拡張子です',
    'zh-CN': '文件扩展名不被允许', 'zh-TW': '不允許的檔案副檔名',
    es: 'La extensión del archivo no está permitida',
  },
  'binary_not_found': {
    ko: '실행 바이너리를 찾을 수 없습니다', ja: '実行バイナリが見つかりません',
    'zh-CN': '未找到可执行二进制文件', 'zh-TW': '找不到可執行二進位檔',
    es: 'Binario ejecutable no encontrado',
  },
  'script_not_found': {
    ko: '실행 스크립트를 찾을 수 없습니다', ja: '実行スクリプトが見つかりません',
    'zh-CN': '未找到执行脚本', 'zh-TW': '找不到執行腳本',
    es: 'Script de ejecución no encontrado',
  },
  'process_exit': {
    ko: '프로세스가 0이 아닌 코드로 종료되었습니다', ja: 'プロセスがゼロ以外のコードで終了しました',
    'zh-CN': '进程以非零代码退出', 'zh-TW': '程序以非零代碼結束',
    es: 'El proceso terminó con un código distinto de cero',
  },
  'inference_timeout': {
    ko: '추론 시간이 초과되었습니다', ja: '推論がタイムアウトしました',
    'zh-CN': '推理超时', 'zh-TW': '推論逾時',
    es: 'La inferencia agotó el tiempo de espera',
  },
  'inference_exception': {
    ko: '추론 중 예외가 발생했습니다', ja: '推論中に例外が発生しました',
    'zh-CN': '推理过程中发生异常', 'zh-TW': '推論期間發生例外',
    es: 'Se produjo una excepción durante la inferencia',
  },
  'invalid_payload': {
    ko: '요청 형식이 올바르지 않습니다', ja: 'リクエスト形式が正しくありません',
    'zh-CN': '请求格式无效', 'zh-TW': '請求格式無效',
    es: 'Formato de solicitud no válido',
  },
  'image_base64_too_large': {
    ko: '이미지 업로드가 너무 큽니다', ja: '画像アップロードが大きすぎます',
    'zh-CN': '图像上传过大', 'zh-TW': '影像上傳過大',
    es: 'La imagen cargada es demasiado grande',
  },
  'invalid_image_base64': {
    ko: '이미지 업로드 데이터가 올바르지 않습니다', ja: '画像アップロードデータが無効です',
    'zh-CN': '图像上传数据无效', 'zh-TW': '影像上傳資料無效',
    es: 'Datos de imagen no válidos',
  },
  'camera_not_found': {
    ko: '카메라 장치를 찾을 수 없습니다', ja: 'カメラデバイスが見つかりません',
    'zh-CN': '未找到摄像头设备', 'zh-TW': '找不到攝影機裝置',
    es: 'Dispositivo de cámara no encontrado',
  },
  'rtsp_required': {
    ko: 'RTSP URL이 필요합니다', ja: 'RTSP URL が必要です',
    'zh-CN': '需要 RTSP URL', 'zh-TW': '需要 RTSP URL',
    es: 'Se requiere una URL RTSP',
  },
  'failed_camera_mux': {
    ko: '카메라 멀티플렉서를 시작하지 못했습니다', ja: 'カメラマルチプレクサを開始できませんでした',
    'zh-CN': '无法启动摄像头复用器', 'zh-TW': '無法啟動攝影機多工器',
    es: 'No se pudo iniciar el multiplexor de cámara',
  },
  'live_mode_unsupported': {
    ko: '라이브 모드는 camera/rtsp만 지원합니다', ja: 'ライブモードは camera/rtsp のみ対応しています',
    'zh-CN': '实时模式仅支持 camera/rtsp', 'zh-TW': '即時模式僅支援 camera/rtsp',
    es: 'El modo en vivo solo admite camera/rtsp',
  },
  'live_image_only': {
    ko: '정지 이미지 전용 모델 — 라이브 불가', ja: '静止画専用モデル — ライブ不可',
    'zh-CN': '仅支持静态图像 — 无法实时运行', 'zh-TW': '僅支援靜態影像 — 無法即時執行',
    es: 'Solo admite imágenes fijas',
  },
  'Compare': {
    ko: '비교', ja: '比較', 'zh-CN': '对比', 'zh-TW': '比較', es: 'Comparar',
  },
  'Nothing generated yet. Add a model or create a task first.': { ko: '아직 생성된 파일이 없습니다. 먼저 모델을 추가하거나 태스크를 만드세요.', ja: 'まだ生成されたファイルはありません。先にモデルを追加するかタスクを作成してください。', 'zh-CN': '尚无生成的文件。请先添加模型或创建任务。', 'zh-TW': '尚無產生的檔案。請先新增模型或建立任務。', es: 'Aún no hay archivos generados. Primero añada un modelo o cree una tarea.' },
  'Show files': { ko: '파일 보기', ja: 'ファイルを表示', 'zh-CN': '查看文件', 'zh-TW': '檢視檔案', es: 'Ver archivos' },
  'Details': { ko: '상세 정보', ja: '詳細', 'zh-CN': '详情', 'zh-TW': '詳情', es: 'Detalles' },
  'View Graph': { ko: '그래프 보기', ja: 'グラフを表示', 'zh-CN': '查看图', 'zh-TW': '檢視圖', es: 'Ver grafo' },
  'Graph': { ko: '그래프', ja: 'グラフ', 'zh-CN': '图', 'zh-TW': '圖', es: 'Grafo' },
  'Delete {name}?': {
    ko: '{name} 파일을 삭제할까요?', ja: '{name} を削除しますか？',
    'zh-CN': '删除 {name}？', 'zh-TW': '刪除 {name}？', es: '¿Eliminar {name}?',
  },
  'Deleted {name}': {
    ko: '{name} 파일을 삭제했습니다', ja: '{name} を削除しました',
    'zh-CN': '已删除 {name}', 'zh-TW': '已刪除 {name}', es: 'Se eliminó {name}',
  },
  'No files': {
    ko: '파일이 없습니다', ja: 'ファイルがありません', 'zh-CN': '没有文件', 'zh-TW': '沒有檔案', es: 'No hay archivos',
  },
  'No files matching filter.': {
    ko: '이 필터에 맞는 파일이 없습니다.', ja: 'このフィルターに一致するファイルはありません。',
    'zh-CN': '没有符合筛选条件的文件。', 'zh-TW': '沒有符合篩選條件的檔案。', es: 'Ningún archivo coincide con el filtro.',
  },
  'Preview': {
    ko: '미리 보기', ja: 'プレビュー', 'zh-CN': '预览', 'zh-TW': '預覽', es: 'Vista previa',
  },
  'Delete': {
    ko: '삭제', ja: '削除', 'zh-CN': '删除', 'zh-TW': '刪除', es: 'Eliminar',
  },
  'runner_error': {
    ko: '예제가 오류를 보고했습니다 — 결과가 정확하지 않습니다', ja: 'サンプルがエラーを報告したため結果は信頼できません',
    'zh-CN': '示例报告了错误，结果不可信', 'zh-TW': '範例回報了錯誤，結果不可信',
    es: 'El ejemplo informó de un error; el resultado no es fiable',
  },
  'live_deps_missing': {
    ko: '라이브 실행에 필요한 패키지가 없습니다', ja: 'ライブ実行に必要なパッケージがありません',
    'zh-CN': '缺少实时运行所需的软件包', 'zh-TW': '缺少即時執行所需的套件',
    es: 'Faltan paquetes necesarios para la ejecución en vivo',
  },
  'live_runner_failed': {
    ko: '예제가 스스로 끝났습니다', ja: 'サンプルが自ら終了しました',
    'zh-CN': '示例自行退出', 'zh-TW': '範例自行結束',
    es: 'El ejemplo terminó por sí solo',
  },
  'live_cpp_only': {
    ko: '라이브 모드는 현재 C++만 지원합니다', ja: 'ライブモードは現在 C++ のみ対応しています',
    'zh-CN': '实时模式目前仅支持 C++', 'zh-TW': '即時模式目前僅支援 C++',
    es: 'El modo en vivo actualmente solo admite C++',
  },
  'Processing...': {
    ko: '처리 중...', ja: '処理中...',
    'zh-CN': '处理中...', 'zh-TW': '處理中...',
    es: 'Procesando...',
  },
  'Error': {
    ko: '오류', ja: 'エラー',
    'zh-CN': '错误', 'zh-TW': '錯誤',
    es: 'Error',
  },
  'Continuous inference complete': {
    ko: '연속 추론 완료', ja: '連続推論完了',
    'zh-CN': '连续推理完成', 'zh-TW': '連續推論完成',
    es: 'Inferencia continua completa',
  },
  'Continuous inference stopped': {
    ko: '연속 추론 중지됨', ja: '連続推論が停止されました',
    'zh-CN': '连续推理已停止', 'zh-TW': '連續推論已停止',
    es: 'Inferencia continua detenida',
  },
  'Stopping inference…': {
    ko: '추론 중지 중…', ja: '推論を停止中…',
    'zh-CN': '正在停止推理…', 'zh-TW': '正在停止推論…',
    es: 'Deteniendo inferencia…',
  },
  'Live inference complete': {
    ko: '라이브 추론 완료', ja: 'ライブ推論完了',
    'zh-CN': '实时推理完成', 'zh-TW': '即時推論完成',
    es: 'Inferencia en vivo completa',
  },

  /* ==== Pipeline ==== */
  'Select input': {
    ko: '입력을 선택하세요', ja: '入力を選択',
    'zh-CN': '选择输入', 'zh-TW': '選擇輸入',
    es: 'Seleccionar entrada',
  },
  'Queued': {
    ko: '대기 중', ja: 'キュー待ち',
    'zh-CN': '已排队', 'zh-TW': '已排隊',
    es: 'En cola',
  },
  'Add pipeline steps': {
    ko: '파이프라인 단계를 추가하세요', ja: 'パイプラインステップを追加してください',
    'zh-CN': '添加流水线步骤', 'zh-TW': '新增管線步驟',
    es: 'Agregar pasos de pipeline',
  },

  /* ==== Compare ==== */
  'Select an image or video': {
    ko: '이미지 또는 비디오를 선택하세요', ja: '画像または動画を選択してください',
    'zh-CN': '请选择图像或视频', 'zh-TW': '請選擇影像或影片',
    es: 'Seleccione una imagen o video',
  },
  'Select at least one model': {
    ko: '최소 하나의 모델을 선택하세요', ja: '少なくとも1つのモデルを選択してください',
    'zh-CN': '请至少选择一个模型', 'zh-TW': '請至少選擇一個模型',
    es: 'Seleccione al menos un modelo',
  },

  /* ==== File Browser ==== */
  'Select Folder': {
    ko: '폴더 선택', ja: 'フォルダ選択',
    'zh-CN': '选择文件夹', 'zh-TW': '選擇資料夾',
    es: 'Seleccionar carpeta',
  },
  'File browser error': {
    ko: '파일 브라우저 오류', ja: 'ファイルブラウザエラー',
    'zh-CN': '文件浏览器错误', 'zh-TW': '檔案瀏覽器錯誤',
    es: 'Error del explorador de archivos',
  },
  'No item selected': {
    ko: '선택된 항목 없음', ja: '項目が選択されていません',
    'zh-CN': '未选择项目', 'zh-TW': '未選擇項目',
    es: 'Ningún elemento seleccionado',
  },
  'Failed to read file: ': {
    ko: '파일 읽기 실패: ', ja: 'ファイル読み取り失敗: ',
    'zh-CN': '文件读取失败: ', 'zh-TW': '檔案讀取失敗: ',
    es: 'Error al leer archivo: ',
  },

  /* ==== Models ==== */
  'File not found': {
    ko: '파일을 찾을 수 없음', ja: 'ファイルが見つかりません',
    'zh-CN': '未找到文件', 'zh-TW': '未找到檔案',
    es: 'Archivo no encontrado',
  },

  /* ==== Inference (dynamic fragments) ==== */
  'Deployed model ': {
    ko: '배포된 모델 ', ja: 'デプロイ済みモデル ',
    'zh-CN': '已部署模型 ', 'zh-TW': '已部署模型 ',
    es: 'Modelo desplegado ',
  },
  ' selected. Press Run to start inference.': {
    ko: ' 선택됨. Run을 눌러 추론을 시작하세요.', ja: ' が選択されました。実行を押して推論を開始してください。',
    'zh-CN': ' 已选择。按运行以开始推理。', 'zh-TW': ' 已選擇。按執行以開始推論。',
    es: ' seleccionado(s). Presione Ejecutar para iniciar la inferencia.',
  },
  'ROI applied: ': {
    ko: 'ROI 적용: ', ja: 'ROI 適用: ',
    'zh-CN': 'ROI 已应用: ', 'zh-TW': 'ROI 已套用: ',
    es: 'ROI aplicado: ',
  },
  'px — only this region will be cropped for inference': {
    ko: 'px — 이 영역만 잘려서 추론에 사용됩니다', ja: 'px — この領域のみが切り取られて推論に使用されます',
    'zh-CN': 'px — 仅此区域将被裁剪用于推理', 'zh-TW': 'px — 僅此區域將被裁剪用於推論',
    es: 'px — solo esta región se recortará para la inferencia',
  },
  'Model file not configured for ': {
    ko: '모델 파일이 설정되지 않음:', ja: 'モデルファイル未設定:',
    'zh-CN': '模型文件未配置:', 'zh-TW': '模型檔案未設定:',
    es: 'Archivo de modelo no configurado para',
  },
  'Model file missing: ': {
    ko: '모델 파일 누락:', ja: 'モデルファイル欠落:',
    'zh-CN': '模型文件缺失:', 'zh-TW': '模型檔案遺失:',
    es: 'Archivo de modelo faltante:',
  },
  'C++ binary not built for ': {
    ko: 'C++ 바이너리가 빌드되지 않음:', ja: 'C++ バイナリ未ビルド:',
    'zh-CN': 'C++ 二进制文件未构建:', 'zh-TW': 'C++ 二進位檔未建置:',
    es: 'Binario C++ no compilado para',
  },
  'Python app not found for ': {
    ko: 'Python 앱을 찾을 수 없음:', ja: 'Python アプリが見つかりません:',
    'zh-CN': '未找到 Python 应用:', 'zh-TW': '未找到 Python 應用:',
    es: 'Aplicación Python no encontrada para',
  },
  'Please select an image': {
    ko: '이미지를 선택해주세요', ja: '画像を選択してください',
    'zh-CN': '请选择图像', 'zh-TW': '請選擇影像',
    es: 'Por favor seleccione una imagen',
  },
  'Model not found: ': {
    ko: '모델을 찾을 수 없음: ', ja: 'モデルが見つかりません: ',
    'zh-CN': '未找到模型: ', 'zh-TW': '找不到模型: ',
    es: 'Modelo no encontrado: ',
  },
  'Slot ': {
    ko: '슬롯 ', ja: 'スロット ',
    'zh-CN': '插槽 ', 'zh-TW': '插槽 ',
    es: 'Ranura ',
  },
  ': Model not found': {
    ko: ': 모델을 찾을 수 없음', ja: ': モデルが見つかりません',
    'zh-CN': ': 未找到模型', 'zh-TW': ': 找不到模型',
    es: ': Modelo no encontrado',
  },
  'No ROI': {
    ko: 'ROI 없음', ja: 'ROI なし',
    'zh-CN': '无 ROI', 'zh-TW': '無 ROI',
    es: 'Sin ROI',
  },
  'ROI set': {
    ko: 'ROI 설정됨', ja: 'ROI 設定済み',
    'zh-CN': 'ROI 已设置', 'zh-TW': 'ROI 已設定',
    es: 'ROI establecido',
  },
  'Too small — try again': {
    ko: '너무 작음 — 다시 시도', ja: '小さすぎます — もう一度お試しください',
    'zh-CN': '太小 — 请重试', 'zh-TW': '太小 — 請重試',
    es: 'Demasiado pequeño — intente de nuevo',
  },

  /* ==== Compiler (extra) ==== */
  'Starting compilation…\n': {
    ko: '컴파일 시작 중…\n', ja: 'コンパイルを開始しています…\n',
    es: 'Iniciando compilación…\n',
    'zh-CN': '正在启动编译…\n', 'zh-TW': '正在啟動編譯…\n'
  },
  'DX-COM installed': {
    ko: 'DX-COM 설치됨', ja: 'DX-COM インストール済み',
    'zh-CN': 'DX-COM 已安装', 'zh-TW': 'DX-COM 已安裝',
    es: 'DX-COM instalado',
  },
  'DX-COM not installed': {
    ko: 'DX-COM 미설치', ja: 'DX-COM 未インストール',
    'zh-CN': 'DX-COM 未安装', 'zh-TW': 'DX-COM 未安裝',
    es: 'DX-COM no instalado',
  },
  'DX-COM not installed (install.sh present)': {
    ko: 'DX-COM 미설치 (install.sh 존재)', ja: 'DX-COM 未インストール (install.sh あり)',
    'zh-CN': 'DX-COM 未安装 (install.sh 存在)', 'zh-TW': 'DX-COM 未安裝 (install.sh 存在)',
    es: 'DX-COM no instalado (install.sh presente)',
  },
  'Top-K: shows the top-K class predictions': {
    ko: 'Top-K: 상위 K개 클래스 예측을 표시합니다', ja: 'Top-K: 上位Kクラスの予測を表示します',
    'zh-CN': 'Top-K: 显示前K个类别预测', 'zh-TW': 'Top-K: 顯示前K個類別預測',
    es: 'Top-K: muestra las top-K predicciones de clase',
  },
  'Semantic segmentation: predicts per-pixel class labels': {
    ko: '의미론적 분할: 픽셀별 클래스 레이블을 예측합니다', ja: 'セマンティックセグメンテーション: ピクセルごとのクラスラベルを予測します',
    'zh-CN': '语义分割: 预测每个像素的类别标签', 'zh-TW': '語意分割: 預測每個像素的類別標籤',
    es: 'Segmentación semántica: predice etiquetas de clase por píxel',
  },

  /* ==== Benchmark (extra) ==== */
  'choose comparison models and start benchmark': {
    ko: '비교 모델을 선택하고 벤치마크를 시작하세요', ja: '比較モデルを選択してベンチマークを開始してください',
    'zh-CN': '选择比较模型并开始基准测试', 'zh-TW': '選擇比較模型並開始基準測試',
    es: 'elija modelos de comparación e inicie el benchmark',
  },
  'models': {
    ko: '모델', ja: 'モデル',
    'zh-CN': '模型', 'zh-TW': '模型',
    es: 'modelos',
  },

  /* ==== Dashboard ==== */
  'Mock Data': {
    ko: '모의 데이터', ja: 'モックデータ',
    'zh-CN': '模拟数据', 'zh-TW': '模擬資料',
    es: 'Datos simulados',
  },
  ' NPU(s)': {
    ko: ' NPU', ja: ' NPU',
    'zh-CN': ' 个NPU', 'zh-TW': ' 個NPU',
    es: ' NPU(s)',
  },

  /* ==== Compiler (extra 2) ==== */
  'Only .onnx files can be uploaded': {
    ko: '.onnx 파일만 업로드할 수 있습니다', ja: '.onnx ファイルのみアップロード可能です',
    'zh-CN': '只能上传 .onnx 文件', 'zh-TW': '只能上傳 .onnx 檔案',
    es: 'Solo se pueden subir archivos .onnx',
  },
  'ONNX file uploaded successfully': {
    ko: 'ONNX 파일 업로드 성공', ja: 'ONNX ファイルのアップロード成功',
    'zh-CN': 'ONNX 文件上传成功', 'zh-TW': 'ONNX 檔案上傳成功',
    es: 'Archivo ONNX subido exitosamente',
  },
  'Upload failed: ': {
    ko: '업로드 실패: ', ja: 'アップロード失敗: ',
    'zh-CN': '上传失败: ', 'zh-TW': '上傳失敗: ',
    es: 'Error al subir: ',
  },
  'JSON load failed: ': {
    ko: 'JSON 로드 실패: ', ja: 'JSON 読み込み失敗: ',
    'zh-CN': 'JSON 加载失败: ', 'zh-TW': 'JSON 載入失敗: ',
    es: 'Error al cargar JSON: ',
  },
  'JSON parse error: ': {
    ko: 'JSON 파싱 오류: ', ja: 'JSON 解析エラー: ',
    'zh-CN': 'JSON 解析错误: ', 'zh-TW': 'JSON 解析錯誤: ',
    es: 'Error de análisis JSON: ',
  },
  'Failed to start compilation: ': {
    ko: '컴파일 시작 실패: ', ja: 'コンパイル開始失敗: ',
    'zh-CN': '编译启动失败: ', 'zh-TW': '編譯啟動失敗: ',
    es: 'Error al iniciar compilación: ',
  },
  'No compilation result available': {
    ko: '컴파일 결과 없음', ja: 'コンパイル結果がありません',
    'zh-CN': '无可用编译结果', 'zh-TW': '無可用編譯結果',
    es: 'Sin resultado de compilación disponible',
  },
  ' deployed to assets/models/!': {
    ko: ' assets/models/에 배포됨!', ja: ' が assets/models/ にデプロイされました！',
    'zh-CN': ' 已部署到 assets/models/！', 'zh-TW': ' 已部署到 assets/models/！',
    es: ' ¡desplegado en assets/models/!',
  },
  'Deployment complete → navigating to Run page…': {
    ko: '배포 완료 → 실행 페이지로 이동 중…', ja: 'デプロイ完了 → 実行ページに移動中…',
    'zh-CN': '部署完成 → 正在导航到运行页面…', 'zh-TW': '部署完成 → 前往執行頁面…',
    es: 'Despliegue completo → navegando a la página de Ejecución…',
  },
  'Enter a model name': {
    ko: '모델 이름을 입력하세요', ja: 'モデル名を入力',
    es: 'Ingrese nombre del modelo',
    'zh-CN': '输入模型名称', 'zh-TW': '輸入模型名稱'
  },
  'Deploy complete!': {
    ko: '배포 완료!', ja: 'デプロイ完了！',
    'zh-CN': '部署完成！', 'zh-TW': '部署完成！',
    es: '¡Despliegue completo!',
  },
  'Error: ': {
    ko: '오류: ', ja: 'エラー: ',
    'zh-CN': '错误: ', 'zh-TW': '錯誤: ',
    es: 'Error: ',
  },

  /* ==== Notifications ==== */
  'Notifications': {
    ko: '알림', ja: '通知',
    'zh-CN': '通知', 'zh-TW': '通知',
    es: 'Notificaciones',
  },
  'No notifications yet': {
    ko: '알림이 없습니다', ja: '通知はまだありません',
    'zh-CN': '暂无通知', 'zh-TW': '暫無通知',
    es: 'Aún no hay notificaciones',
  },
  'Clear': {
    ko: '지우기', ja: 'クリア',
    'zh-CN': '清除', 'zh-TW': '清除',
    es: 'Limpiar',
  },
  'Cleared': {
    ko: '비움', ja: 'クリア済み',
    'zh-CN': '已清除', 'zh-TW': '已清除',
    es: 'Limpiado',
  },

  /* ==== Profiler ==== */
  'What is this?': {
    ko: '이것이 뭐예요?', ja: 'これは何ですか？',
    'zh-CN': '这是什么？', 'zh-TW': '這是什麼？',
    es: '¿Qué es esto?',
  },
  'profiler-help-desc': {
    en: 'This Gantt chart shows the time each hardware/software component spent during a single inference pass. Each row (lane) represents a processing stage — NPU compute, input I/O, pre/post processing, PCIe transfer, etc. Longer bars = more time = potential bottleneck. Use this to identify which stages slow inference.',
    ko: '이 Gantt 차트는 단일 추론 실행 동안 각 HW/SW 구성 요소가 소비한 시간을 보여줍니다. 각 행(lane)은 NPU 연산, 입력 I/O, 전/후처리, PCIe 전송 등의 처리 단계를 나타냅니다. 바가 길수록 = 시간이 오래 걸림 = 병목 지점. 어떤 단계가 추론을 느리게 하는지 확인하세요.',
    ja: 'このGanttチャートは単一の推論実行中に各HW/SWコンポーネントが消費した時間を表示します。各行(レーン)はNPU演算、入力I/O、前後処理、PCIe転送などの処理段階を示します。バーが長いほど時間がかかりボトルネックとなります。どの段階が推論を遅くしているか確認してください。',
    'zh-CN': '此Gantt图显示单次推理运行期间各HW/SW组件消耗的时间。每行(通道)表示NPU运算、输入I/O、前后处理、PCIe传输等处理阶段。条越长=耗时越久=瓶颈所在。请查看哪个阶段拖慢了推理速度。',
    'zh-TW': '此Gantt圖顯示單次推理執行期間各HW/SW元件消耗的時間。每列(通道)表示NPU運算、輸入I/O、前後處理、PCIe傳輸等處理階段。長條越長=耗時越久=瓶頸所在。請查看哪個階段拖慢了推理速度。',
    es: 'Este diagrama de Gantt muestra el tiempo que consumió cada componente de hardware/software durante una pasada de inferencia. Cada fila (carril) representa una etapa de procesamiento — cómputo NPU, E/S de entrada, pre/postprocesado, transferencia PCIe, etc. Barras más largas = más tiempo = posible cuello de botella. Use esto para identificar qué etapas ralentizan la inferencia.',
  },
  'prof-scroll-hint': {
    en: 'Scroll to zoom • Drag to pan',
    ko: '스크롤로 줌 • 드래그로 패닝',
    ja: 'スクロールでズーム・ドラッグでパン',
    'zh-CN': '滚轮缩放 • 拖拽平移',
    'zh-TW': '滾輪縮放 • 拖曳平移',
    es: 'Desplazamiento para zoom • Arrastre para desplazar',
  },

    /* ==== Relative time ==== */
  'just now': {
    ko: '방금 전', ja: 'たった今',
    'zh-CN': '刚刚', 'zh-TW': '剛剛',
    es: 'ahora mismo',
  },
/* ==== Community page buttons ==== */
  'All': {
    ko: '전체', ja: 'すべて',
    'zh-CN': '全部', 'zh-TW': '全部',
    es: 'Todo',
  },
  'Latest': {
    ko: '최신순', ja: '最新',
    'zh-CN': '最新', 'zh-TW': '最新',
    es: 'Más reciente',
  },
  'Most Liked': {
    ko: '추천순', ja: '人気順',
    'zh-CN': '最多点赞', 'zh-TW': '最多按讚',
    es: 'Más gustados',
  },
  'Most Comments': {
    ko: '댓글순', ja: 'コメント順',
    'zh-CN': '最多评论', 'zh-TW': '最多留言',
    es: 'Más comentarios',
  },
  'New Post': {
    ko: '새 글 작성', ja: '新規投稿',
    'zh-CN': '新帖子', 'zh-TW': '新貼文',
    es: 'Nueva publicación',
  },

  /* ==== Model source option ==== */

  /* ==== Page descriptions ==== */
  'Detailed guides, parameters, workflows, and tips for each DX-APP feature — all in one place.': {
    ko: 'DX-APP 기능별 상세 가이드 · 파라미터 · 워크플로우 · 팁을 한 곳에서 확인하세요.', ja: 'DX-APP の各機能の詳細ガイド・パラメータ・ワークフロー・ヒントをすべて一か所で確認できます。',
    'zh-CN': 'DX-APP 各功能的详细指南、参数、工作流和提示 — 一站式查阅。', 'zh-TW': 'DX-APP 各功能的詳細指南、參數、工作流程和提示 — 一站式查閱。',
    es: 'Guías detalladas, parámetros, flujos de trabajo y consejos para cada característica de DX-APP — todo en un solo lugar.',
  },

  /* ==== Inference (extra) ==== */
  'Confidence Trend': {
    ko: 'Confidence 추이', ja: '信頼度の推移',
    'zh-CN': 'Confidence 趋势', 'zh-TW': 'Confidence 趨勢',
    es: 'Tendencia de confianza',
  },


  /* ─── Additional i18n entries ─── */
  'Model Demo Runner': { ko: '모델 예제 실행', ja: 'モデルデモランナー', 'zh-CN': '模型演示运行器', 'zh-TW': '模型展示執行器',es:'Ejecutor de demo de modelo'},
  'ModelZoo': { ko: '모델 저장소', ja: 'ModelZoo', 'zh-CN': 'ModelZoo', 'zh-TW': 'ModelZoo',es:'ModelZoo'},
  'Install dependencies and build each component from this page. Run top-to-bottom, left-to-right.': {
    ko: '이 페이지에서 종속성을 설치하고 각 구성 요소를 빌드하세요. 위에서 아래로, 왼쪽에서 오른쪽으로 실행합니다.',
    ja: 'このページから依存関係をインストールし、各コンポーネントをビルドします。上から下、左から右に実行してください。',
    'zh-CN': '从此页面安装依赖并构建各组件。从上到下、从左到右执行。',
    'zh-TW': '從此頁面安裝相依套件並建置各元件。由上至下、由左至右執行。',
    es: 'Instale dependencias y compile cada componente desde esta página. Ejecute de arriba a abajo, de izquierda a derecha.',
  },
  'Install system packages required for C++ build (cmake, gcc, ninja, OpenCV, …) →': {
    ko: 'C++ 빌드에 필요한 시스템 패키지 설치 (cmake, gcc, ninja, OpenCV, …) →',
    ja: 'C++ ビルドに必要なシステムパッケージをインストール (cmake, gcc, ninja, OpenCV, …) →',
    'zh-CN': '安装 C++ 构建所需的系统软件包 (cmake, gcc, ninja, OpenCV, …) →',
    'zh-TW': '安裝 C++ 建置所需的系統套件 (cmake, gcc, ninja, OpenCV, …) →',
    es: 'Instale los paquetes del sistema requeridos para la compilación C++ (cmake, gcc, ninja, OpenCV, …) →',
  },
  'Compile C++ demo binaries (cmake) →': {
    ko: 'C++ 데모 바이너리 컴파일 (cmake) →',
    ja: 'C++ デモバイナリをコンパイル (cmake) →',
    'zh-CN': '编译 C++ 演示二进制文件 (cmake) →',
    'zh-TW': '編譯 C++ 演示二進位檔案 (cmake) →',
    es: 'Compile binarios de demo C++ (cmake) →',
  },
  'Download sample models & videos for Run / Benchmark demos →': {
    ko: 'Run / Benchmark 데모용 샘플 모델 및 비디오 다운로드 →',
    ja: 'Run / Benchmark デモ用のサンプルモデルと動画をダウンロード →',
    'zh-CN': '下载 Run / Benchmark 演示用的示例模型和视频 →',
    'zh-TW': '下載 Run / Benchmark 示範用的範例模型和影片 →',
    es: 'Descargue modelos y videos de ejemplo para demos de Ejecución / Benchmark →',
  },
  'Install packages required for NPU runtime (cmake, ONNX Runtime, …) →': {
    ko: 'NPU 런타임에 필요한 패키지 설치 (cmake, ONNX Runtime, …) →',
    ja: 'NPU ランタイムに必要なパッケージをインストール (cmake, ONNX Runtime, …) →',
    'zh-CN': '安装 NPU 运行时所需的软件包 (cmake, ONNX Runtime, …) →',
    'zh-TW': '安裝 NPU 執行階段所需的套件 (cmake, ONNX Runtime, …) →',
    es: 'Instale los paquetes requeridos para el runtime NPU (cmake, ONNX Runtime, …) →',
  },
  'Install DEEPX NPU kernel driver (requires sudo) →': {
    ko: 'DEEPX NPU 커널 드라이버 설치 (sudo 필요) →',
    ja: 'DEEPX NPU カーネルドライバーをインストール (sudo 必要) →',
    'zh-CN': '安装 DEEPX NPU 内核驱动程序 (需要 sudo) →',
    'zh-TW': '安裝 DEEPX NPU 核心驅動程式 (需要 sudo) →',
    es: 'Instale el controlador del kernel del NPU DEEPX (requiere sudo) →',
  },
  'ONNX→.dxnn converter. Requires DEEPX Developers Portal account →': {
    ko: 'ONNX→.dxnn 변환기. DEEPX 개발자 포털 계정 필요 →',
    ja: 'ONNX→.dxnn コンバーター。DEEPX 開発者ポータルアカウントが必要 →',
    'zh-CN': 'ONNX→.dxnn 转换器。需要 DEEPX 开发者门户账户 →',
    'zh-TW': 'ONNX→.dxnn 轉換器。需要 DEEPX 開發者入口網站帳號 →',
    es: 'Conversor ONNX→.dxnn. Requiere cuenta de DEEPX Developers Portal →',
  },
  'Deep Diagnostics': { ko: '심층 진단', ja: '詳細診断', 'zh-CN': '深度诊断', 'zh-TW': '深度診斷',es:'Diagnóstico profundo'},
  'Run Diagnostics': { ko: '진단 실행', ja: '診断実行', 'zh-CN': '运行诊断', 'zh-TW': '執行診斷',es:'Ejecutar diagnóstico'},
  'Comprehensive system health check: PCIe link, kernel modules, DKMS, services, CLI tools, Python venv, disk, memory, model integrity.': {
    ko: '시스템 종합 진단: PCIe 링크, 커널 모듈, DKMS, 서비스, CLI 도구, Python 가상환경, 디스크, 메모리, 모델 무결성.',
    ja: 'システム総合診断: PCIe リンク、カーネルモジュール、DKMS、サービス、CLI ツール、Python 仮想環境、ディスク、メモリ、モデル整合性。',
    'zh-CN': '系统综合健康检查：PCIe 链路、内核模块、DKMS、服务、CLI 工具、Python 虚拟环境、磁盘、内存、模型完整性。',
    'zh-TW': '系統綜合健康檢查：PCIe 連結、核心模組、DKMS、服務、CLI 工具、Python 虛擬環境、磁碟、記憶體、模型完整性。',
    es: 'Verificación integral del estado del sistema: enlace PCIe, módulos del kernel, DKMS, servicios, herramientas CLI, Python venv, disco, memoria, integridad del modelo.',
  },
  'Actions': { ko: '작업', ja: '操作', 'zh-CN': '操作', 'zh-TW': '操作',es:'Acciones'},
  'Passed to the model\'s config.json as score_threshold / nms_threshold': {
    ko: '모델의 config.json에 score_threshold / nms_threshold로 전달됩니다',
    ja: 'モデルの config.json に score_threshold / nms_threshold として渡されます',
    es: 'Se pasa al config.json del modelo como score_threshold / nms_threshold',
    'zh-CN': '作为 score_threshold / nms_threshold 传递到模型的 config.json',
    'zh-TW': '作為 score_threshold / nms_threshold 傳遞至模型的 config.json'
  },
  'Profiler': { ko: '프로파일러', ja: 'プロファイラー', 'zh-CN': '性能分析器', 'zh-TW': '分析器',es:'Perfilador'},
  'Profiler Timeline': { ko: '프로파일러 타임라인', ja: 'プロファイラー タイムライン', 'zh-CN': '性能分析器时间轴', 'zh-TW': '分析器時間軸',es:'Línea de tiempo del perfilador'},
  'Reset Zoom': { ko: '줌 초기화', ja: 'ズームをリセット', 'zh-CN': '重置缩放', 'zh-TW': '重設縮放',es:'Restablecer zoom'},
  'Extract the selected model\'s source code, config, and model file as a package. Available for download on the Outputs page.': {
    ko: '선택한 모델의 소스 코드, 설정, 모델 파일을 패키지로 추출합니다. Outputs 페이지에서 다운로드할 수 있습니다.',
    ja: '選択したモデルのソースコード、設定、モデルファイルをパッケージとして抽出します。Outputs ページからダウンロードできます。',
    'zh-CN': '将所选模型的源代码、配置和模型文件提取为软件包。可在 Outputs 页面下载。',
    'zh-TW': '將所選模型的原始碼、組態和模型檔案擷取為套件。可在 Outputs 頁面下載。',
    es: 'Extraiga el código fuente, configuración y archivo de modelo del modelo seleccionado como paquete. Disponible para descarga en la página de Salidas.',
  },
  'Camera Device': { ko: '카메라 장치', ja: 'カメラデバイス', 'zh-CN': '摄像头设备', 'zh-TW': '攝影機裝置',es:'Dispositivo de cámara'},
  'RTSP address': { ko: 'RTSP 주소', ja: 'RTSP アドレス', 'zh-CN': 'RTSP 地址', 'zh-TW': 'RTSP 位址', es: 'Dirección RTSP' },
  'Enter the RTSP address (rtsp://… or IP:Port)': {
    ko: 'RTSP 주소를 입력하세요 (rtsp://… 또는 IP:포트)', ja: 'RTSP アドレスを入力してください (rtsp://… または IP:ポート)',
    'zh-CN': '请输入 RTSP 地址（rtsp://… 或 IP:端口）', 'zh-TW': '請輸入 RTSP 位址（rtsp://… 或 IP:連接埠）',
    es: 'Introduzca la dirección RTSP (rtsp://… o IP:Puerto)',
  },
  'RTSP Server': { ko: 'RTSP 서버', ja: 'RTSP サーバー', 'zh-CN': 'RTSP 服务器', 'zh-TW': 'RTSP 伺服器',es:'Servidor RTSP'},
  'Stream': { ko: '스트림', ja: 'ストリーム', 'zh-CN': '流', 'zh-TW': '串流',es:'Stream'},
  'Settings': { ko: '설정', ja: '設定', 'zh-CN': '设置', 'zh-TW': '設定',es:'Configuración'},
  'None': { ko: '해제', ja: 'なし', 'zh-CN': '无', 'zh-TW': '無',es:'Ninguno'},
  'Latency(ms)': { ko: '지연시간(ms)', ja: 'レイテンシ(ms)', 'zh-CN': '延迟(ms)', 'zh-TW': '延遲(ms)',es:'Latencia (ms)'},
  'Slots:': { ko: '슬롯:', ja: 'スロット:', 'zh-CN': '槽位:', 'zh-TW': '插槽:',es:'Ranuras:'},
  'Shared Input (Image / Video)': { ko: '공유 입력 (이미지 / 동영상)', ja: '共有入力 (画像 / 動画)', 'zh-CN': '共享输入 (图像 / 视频)', 'zh-TW': '共用輸入 (影像 / 影片)',es:'Entrada compartida (Imagen / Video)'},
  'Camera': { ko: '카메라', ja: 'カメラ', 'zh-CN': '摄像头', 'zh-TW': '攝影機',es:'Cámara'},
  'Browse the DEEPX ModelZoo — select models and download Q-Lite / Q-Pro / Q-Master DXNN files directly.': {
    ko: 'DEEPX 모델 저장소를 탐색하세요 — 모델을 선택하고 Q-Lite / Q-Pro / Q-Master DXNN 파일을 직접 다운로드합니다.',
    ja: 'DEEPX ModelZoo を閲覧 — モデルを選択し、Q-Lite / Q-Pro / Q-Master DXNN ファイルを直接ダウンロードします。',
    'zh-CN': '浏览 DEEPX ModelZoo — 选择模型并直接下载 Q-Lite / Q-Pro / Q-Master DXNN 文件。',
    'zh-TW': '瀏覽 DEEPX ModelZoo — 選擇模型並直接下載 Q-Lite / Q-Pro / Q-Master DXNN 檔案。',
    es: 'Explore el DEEPX ModelZoo — seleccione modelos y descargue archivos DXNN Q-Lite / Q-Pro / Q-Master directamente.',
  },
  'ModelZoo Homepage': { ko: 'ModelZoo 홈페이지', ja: 'ModelZoo ホームページ', 'zh-CN': 'ModelZoo 主页', 'zh-TW': 'ModelZoo 首頁',es:'Página principal de ModelZoo'},
  'Source': { ko: '소스', ja: 'ソース', 'zh-CN': '来源', 'zh-TW': '來源',es:'Fuente'},
  'New Only': { ko: '새 항목만', ja: '新規のみ', 'zh-CN': '仅新增项', 'zh-TW': '僅新增項',es:'Solo nuevos'},
  'Q-Lite All': { ko: 'Q-Lite 전체', ja: 'Q-Lite すべて', 'zh-CN': 'Q-Lite 全部', 'zh-TW': 'Q-Lite 全部',es:'Todo Q-Lite'},
  'Q-Pro All': { ko: 'Q-Pro 전체', ja: 'Q-Pro すべて', 'zh-CN': 'Q-Pro 全部', 'zh-TW': 'Q-Pro 全部',es:'Todo Q-Pro'},
  'Q-Master All': { ko: 'Q-Master 전체', ja: 'Q-Master すべて', 'zh-CN': 'Q-Master 全部', 'zh-TW': 'Q-Master 全部', es: 'Todo Q-Master' },
  'Add to cart': { ko: '장바구니에 담기', ja: 'カートに追加', 'zh-CN': '加入购物车', 'zh-TW': '加入購物車', es: 'Añadir al carrito' },
  'Task': { ko: '작업', ja: 'タスク', 'zh-CN': '任务', 'zh-TW': '任務',es:'Tarea'},
  'Name': { ko: '이름', ja: '名前', 'zh-CN': '名称', 'zh-TW': '名稱',es:'Nombre'},
  'Dataset': { ko: '데이터셋', ja: 'データセット', 'zh-CN': '数据集', 'zh-TW': '資料集',es:'Conjunto de datos'},
  'Input': { ko: '입력', ja: '入力', 'zh-CN': '输入', 'zh-TW': '輸入',es:'Entrada'},
  'License': { ko: '라이선스', ja: 'ライセンス', 'zh-CN': '许可证', 'zh-TW': '授權條款',es:'Licencia'},
  'Metric': { ko: '메트릭', ja: 'メトリック', 'zh-CN': '指标', 'zh-TW': '指標',es:'Métrica'},
  'Accuracy': { ko: '정확도', ja: '精度', 'zh-CN': '准确率', 'zh-TW': '準確率',es:'Precisión'},
  'Convert an ONNX model to a DEEPX NPU .dxnn binary. Upload → configure → compile → deploy in one place.': {
    ko: 'ONNX 모델을 DEEPX NPU .dxnn 바이너리로 변환합니다. 업로드 → 설정 → 컴파일 → 배포를 한 곳에서.',
    ja: 'ONNX モデルを DEEPX NPU .dxnn バイナリに変換します。アップロード → 設定 → コンパイル → デプロイを一箇所で。',
    'zh-CN': '将 ONNX 模型转换为 DEEPX NPU .dxnn 二进制文件。上传 → 配置 → 编译 → 部署一站式完成。',
    'zh-TW': '將 ONNX 模型轉換為 DEEPX NPU .dxnn 二進位檔。上傳 → 設定 → 編譯 → 部署一站式完成。',
    es: 'Convierta un modelo ONNX a binario .dxnn de DEEPX NPU. Suba → configure → compile → despliegue en un solo lugar.',
  },
  'Click or drag ONNX file': { ko: '클릭 또는 ONNX 파일 드래그', ja: 'クリックまたは ONNX ファイルをドラッグ', 'zh-CN': '点击或拖拽 ONNX 文件', 'zh-TW': '點擊或拖曳 ONNX 檔案',es:'Haga clic o arrastre archivo ONNX'},
  'Or enter server path below': { ko: '또는 아래에 서버 경로 입력', ja: 'または下にサーバーパスを入力', 'zh-CN': '或在下方输入服务器路径', 'zh-TW': '或在下方輸入伺服器路徑',es:'O introduzca la ruta del servidor abajo'},
  'Server ONNX path': { ko: '서버 ONNX 경로', ja: 'サーバー ONNX パス', 'zh-CN': '服务器 ONNX 路径', 'zh-TW': '伺服器 ONNX 路徑',es:'Ruta ONNX del servidor'},
  'Click or drag JSON config': { ko: '클릭 또는 JSON 설정 드래그', ja: 'クリックまたは JSON 設定をドラッグ', 'zh-CN': '点击或拖拽 JSON 配置文件', 'zh-TW': '點擊或拖曳 JSON 設定檔',es:'Haga clic o arrastre configuración JSON'},
  'Auto-fill all compile fields': { ko: '모든 컴파일 필드 자동 채우기', ja: 'すべてのコンパイルフィールドを自動入力', 'zh-CN': '自动填充所有编译字段', 'zh-TW': '自動填入所有編譯欄位',es:'Auto-completar todos los campos de compilación'},
  'Server JSON path': { ko: '서버 JSON 경로', ja: 'サーバー JSON パス', 'zh-CN': '服务器 JSON 路径', 'zh-TW': '伺服器 JSON 路徑',es:'Ruta JSON del servidor'},
  'Load': { ko: '로드', ja: '読み込み', 'zh-CN': '加载', 'zh-TW': '載入',es:'Cargar'},
  'Click to browse folder': { ko: '클릭하여 폴더 탐색', ja: 'クリックしてフォルダを参照', 'zh-CN': '点击浏览文件夹', 'zh-TW': '點擊瀏覽資料夾',es:'Haga clic para explorar carpeta'},
  'Or drag images / enter path': { ko: '또는 이미지 드래그 / 경로 입력', ja: 'または画像をドラッグ / パスを入力', 'zh-CN': '或拖拽图片 / 输入路径', 'zh-TW': '或拖曳影像 / 輸入路徑',es:'O arrastre imágenes / introduzca ruta'},
  'fast compile': { ko: '빠른 컴파일', ja: '高速コンパイル', 'zh-CN': '快速编译', 'zh-TW': '快速編譯',es:'compilación rápida'},
  'optimal performance': { ko: '최적 성능', ja: '最適パフォーマンス', 'zh-CN': '最优性能', 'zh-TW': '最佳效能',es:'rendimiento óptimo'},
  'Add': { ko: '추가', ja: '追加', 'zh-CN': '添加', 'zh-TW': '新增',es:'Agregar'},
  'Password:': { ko: '비밀번호:', ja: 'パスワード:', 'zh-CN': '密码:', 'zh-TW': '密碼:',es:'Contraseña:'},
  'ONNX Graph': { ko: 'ONNX 그래프', ja: 'ONNX グラフ', 'zh-CN': 'ONNX 图', 'zh-TW': 'ONNX 圖',es:'Gráfico ONNX'},
  'DXNN Graph': { ko: 'DXNN 그래프', ja: 'DXNN グラフ', 'zh-CN': 'DXNN 图', 'zh-TW': 'DXNN 圖',es:'Gráfico DXNN'},
  'Side-by-Side': { ko: '나란히 보기', ja: '並べて表示', 'zh-CN': '并排对比', 'zh-TW': '並排對比',es:'Lado a lado'},
  'Upload an ONNX file or compile a model, then view the graph structure below': {
    ko: 'ONNX 파일을 업로드하거나 모델을 컴파일한 후 아래에서 그래프 구조를 확인하세요',
    ja: 'ONNX ファイルをアップロードするかモデルをコンパイルし、下のグラフ構造を確認してください',
    'zh-CN': '上传 ONNX 文件或编译模型，然后在下方查看图结构',
    'zh-TW': '上傳 ONNX 檔案或編譯模型，然後在下方查看圖結構',
    es: 'Suba un archivo ONNX o compile un modelo, luego vea la estructura del gráfico a continuación',
  },
  'Click "ONNX Graph" or "DXNN Graph" above to visualize': {
    ko: '"ONNX Graph" 또는 "DXNN Graph"를 클릭하여 시각화',
    ja: '上の「ONNX Graph」または「DXNN Graph」をクリックして視覚化',
    'zh-CN': '点击上方 "ONNX Graph" 或 "DXNN Graph" 进行可视化',
    'zh-TW': '點擊上方 "ONNX Graph" 或 "DXNN Graph" 進行視覺化',
    es: 'Haga clic en "ONNX Graph" o "DXNN Graph" arriba para visualizar',
  },
  'Download': { ko: '다운로드', ja: 'ダウンロード', 'zh-CN': '下载', 'zh-TW': '下載',es:'Descargar'},
  'Before': { ko: '이전', ja: '変更前', 'zh-CN': '变更前', 'zh-TW': '變更前',es:'Antes'},
  'After': { ko: '이후', ja: '変更後', 'zh-CN': '变更后', 'zh-TW': '變更後',es:'Después'},
  'Detail': { ko: '상세', ja: '詳細', 'zh-CN': '详情', 'zh-TW': '詳細資訊',es:'Detalle'},
  'Run': { ko: '실행', ja: '実行', 'zh-CN': '运行', 'zh-TW': '執行', es: 'Ejecutar'},
  'Re-download': { ko: '다시 다운로드', ja: '再ダウンロード', 'zh-CN': '重新下载', 'zh-TW': '重新下載', es: 'Volver a descargar'},
  'Loading catalog…': { ko: '카탈로그 불러오는 중…', ja: 'カタログを読み込み中…', 'zh-CN': '正在加载目录…', 'zh-TW': '正在載入目錄…', es: 'Cargando catálogo…'},
  'Download the Q-Lite .dxnn from ModelZoo': { ko: 'ModelZoo에서 Q-Lite .dxnn 다운로드', ja: 'ModelZoo から Q-Lite .dxnn をダウンロード', 'zh-CN': '从 ModelZoo 下载 Q-Lite .dxnn', 'zh-TW': '從 ModelZoo 下載 Q-Lite .dxnn', es: 'Descargar el .dxnn Q-Lite desde ModelZoo'},
  'Re-download the Q-Lite .dxnn from ModelZoo': { ko: 'ModelZoo에서 Q-Lite .dxnn 다시 다운로드', ja: 'ModelZoo から Q-Lite .dxnn を再ダウンロード', 'zh-CN': '从 ModelZoo 重新下载 Q-Lite .dxnn', 'zh-TW': '從 ModelZoo 重新下載 Q-Lite .dxnn', es: 'Volver a descargar el .dxnn Q-Lite desde ModelZoo'},
  'Downloading': { ko: '다운로드 중', ja: 'ダウンロード中', 'zh-CN': '下载中', 'zh-TW': '下載中', es: 'Descargando'},
  'Download complete': { ko: '다운로드 완료', ja: 'ダウンロード完了', 'zh-CN': '下载完成', 'zh-TW': '下載完成', es: 'Descarga completada'},
  'Download finished with errors': { ko: '다운로드가 오류와 함께 완료됨', ja: 'エラーがある状態でダウンロードが完了しました', 'zh-CN': '下载完成但有错误', 'zh-TW': '下載完成但有錯誤', es: 'Descarga finalizada con errores'},
  'Download failed to start': { ko: '다운로드를 시작하지 못했습니다', ja: 'ダウンロードを開始できませんでした', 'zh-CN': '下载启动失败', 'zh-TW': '下載啟動失敗', es: 'No se pudo iniciar la descarga'},
  'A model download is already in progress.': { ko: '이미 모델 다운로드가 진행 중입니다.', ja: 'すでにモデルのダウンロードが進行中です。', 'zh-CN': '已有模型正在下载中。', 'zh-TW': '已有模型正在下載中。', es: 'Ya hay una descarga de modelo en curso.'},
  'async_empty_video': {
    ko: '이 async 예제는 영상 프레임을 저장하지 못했습니다 — 일부 async 러너의 알려진 제한이며 업데이트 예정입니다. Sync 모드로 전환하면 동일한 주석 영상이 나옵니다. 정확한 동작은 터미널에서 run_demo.sh로 직접 실행해 확인하세요.',
    en: 'This async example produced no video frames — a known limitation of some async runners, fix planned in a future update. Switch to Sync mode for the identical annotated video. To verify the real behavior, run it directly in a terminal via run_demo.sh.',
    ja: 'この async 例は映像フレームを保存できませんでした — 一部の async ランナーの既知の制限で、今後のアップデートで対応予定です。Sync モードに切り替えると同一の注釈付き映像が得られます。実際の動作はターミナルで run_demo.sh を直接実行して確認してください。',
    'zh-CN': '此 async 示例未生成视频帧 — 这是部分 async 运行器的已知限制，计划在后续更新中修复。切换到 Sync 模式可得到相同的标注视频。如需验证真实行为，请在终端通过 run_demo.sh 直接运行。',
    'zh-TW': '此 async 範例未產生影格 — 這是部分 async 執行器的已知限制，計畫於後續更新中修復。切換到 Sync 模式可獲得相同的標註影片。如需驗證實際行為，請在終端機透過 run_demo.sh 直接執行。',
    es: 'Este ejemplo async no generó fotogramas de video — una limitación conocida de algunos runners async, con corrección prevista en una futura actualización. Cambie al modo Sync para el mismo video anotado. Para verificar el comportamiento real, ejecútelo directamente en una terminal con run_demo.sh.',
  },
  'async_video_stalled': {
    ko: 'async 예제가 영상 처리 중 멈췄습니다 — 일부 async 러너의 알려진 제한이며 업데이트 예정입니다. Sync 모드를 사용하세요. 정확한 동작은 터미널에서 run_demo.sh로 직접 실행해 확인하세요.',
    en: 'The async example stalled while processing video — a known limitation of some async runners, fix planned in a future update. Please use Sync mode. To verify the real behavior, run it directly in a terminal via run_demo.sh.',
    ja: 'async 例が映像処理中に停止しました — 一部の async ランナーの既知の制限で、今後のアップデートで対応予定です。Sync モードをご使用ください。実際の動作はターミナルで run_demo.sh を直接実行して確認してください。',
    'zh-CN': 'async 示例在处理视频时卡住 — 这是部分 async 运行器的已知限制，计划在后续更新中修复。请使用 Sync 模式。如需验证真实行为，请在终端通过 run_demo.sh 直接运行。',
    'zh-TW': 'async 範例在處理影片時卡住 — 這是部分 async 執行器的已知限制，計畫於後續更新中修復。請使用 Sync 模式。如需驗證實際行為，請在終端機透過 run_demo.sh 直接執行。',
    es: 'El ejemplo async se bloqueó al procesar video — una limitación conocida de algunos runners async, con corrección prevista en una futura actualización. Use el modo Sync. Para verificar el comportamiento real, ejecútelo directamente en una terminal con run_demo.sh.',
  },
  'This will permanently delete model source files from disk.': {
    ko: '디스크에서 모델 소스 파일이 영구적으로 삭제됩니다.',
    ja: 'ディスクからモデルソースファイルが完全に削除されます。',
    'zh-CN': '这将从磁盘永久删除模型源文件。',
    'zh-TW': '這將從磁碟永久刪除模型原始檔案。',
    es: 'Esto eliminará permanentemente los archivos fuente del modelo del disco.',
  },
  'Auto-generate skeleton code (Factory, Postprocessor, Visualizer, Runner) for a new task type.To add a model to an existing task, use the Add Model tab.': {
    ko: '새 작업 유형에 대한 스켈레톤 코드 (Factory, Postprocessor, Visualizer, Runner)를 자동 생성합니다.기존 작업에 모델을 추가하려면 모델 추가 탭을 사용하세요.',
    ja: '新しいタスクタイプ用のスケルトンコード (Factory, Postprocessor, Visualizer, Runner) を自動生成します。既存タスクにモデルを追加するには「モデル追加」タブを使用してください。',
    'zh-CN': '为新任务类型自动生成骨架代码 (Factory, Postprocessor, Visualizer, Runner)。要向已有任务添加模型，请使用「添加模型」标签页。',
    'zh-TW': '為新任務類型自動產生骨架程式碼 (Factory, Postprocessor, Visualizer, Runner)。要向既有任務新增模型，請使用「新增模型」分頁。',
    es: 'Auto-generar código esqueleto (Factory, Postprocessor, Visualizer, Runner) para un nuevo tipo de tarea. Para agregar un modelo a una tarea existente, use la pestaña Agregar modelo.',
  },
  'Files to generate: Factory interface, Postprocessor, Visualizer, Sync/Async Runner (C++), Postprocessor/Visualizer (Python)': {
    ko: '생성할 파일: Factory 인터페이스, Postprocessor, Visualizer, Sync/Async Runner (C++), Postprocessor/Visualizer (Python)',
    ja: '生成するファイル: Factory インターフェース、Postprocessor、Visualizer、Sync/Async Runner (C++)、Postprocessor/Visualizer (Python)',
    'zh-CN': '要生成的文件：Factory 接口、Postprocessor、Visualizer、Sync/Async Runner (C++)、Postprocessor/Visualizer (Python)',
    'zh-TW': '要產生的檔案：Factory 介面、Postprocessor、Visualizer、Sync/Async Runner (C++)、Postprocessor/Visualizer (Python)',
    es: 'Archivos a generar: interfaz Factory, Postprocessor, Visualizer, Runner Sync/Async (C++), Postprocessor/Visualizer (Python)',
  },
  'Packages are saved to outputs/ directory. Use the Outputs page to download.': {
    ko: '패키지는 outputs/ 디렉토리에 저장됩니다. Outputs 페이지에서 다운로드하세요.',
    ja: 'パッケージは outputs/ ディレクトリに保存されます。Outputs ページからダウンロードしてください。',
    'zh-CN': '包已保存至 outputs/ 目录。请在 Outputs 页面下载。',
    'zh-TW': '套件已儲存至 outputs/ 目錄。請在 Outputs 頁面下載。',
    es: 'Los paquetes se guardan en el directorio outputs/. Use la página de Salidas para descargar.',
  },
  'Undo': {
    ko: '실행 취소', ja: '元に戻す', 'zh-CN': '撤销', 'zh-TW': '復原', es: 'Deshacer',
  },
  'Redo': {
    ko: '다시 실행', ja: 'やり直す', 'zh-CN': '重做', 'zh-TW': '重做', es: 'Rehacer',
  },
  'Inspector': {
    ko: 'Inspector', ja: 'インスペクター', 'zh-CN': '检查器', 'zh-TW': '檢查器', es: 'Inspector',
  },
  'Fit view': {
    ko: '화면에 맞추기', ja: '画面に合わせる', 'zh-CN': '适应视图', 'zh-TW': '適應檢視', es: 'Ajustar vista',
  },
  'Zoom in': {
    ko: '확대', ja: '拡大', 'zh-CN': '放大', 'zh-TW': '放大', es: 'Acercar',
  },
  'Zoom out': {
    ko: '축소', ja: '縮小', 'zh-CN': '缩小', 'zh-TW': '縮小', es: 'Alejar',
  },
  'Minimap': {
    ko: '미니맵', ja: 'ミニマップ', 'zh-CN': '小地图', 'zh-TW': '小地圖', es: 'Minimapa',
  },
  'Blocked': { ko: '차단됨', ja: 'ブロック済み', 'zh-CN': '已阻止', 'zh-TW': '已封鎖', es: 'Bloqueado' },
  'Plugin scaffold preview': { ko: 'Plugin scaffold 미리보기', ja: 'Plugin scaffold プレビュー', 'zh-CN': 'Plugin scaffold 预览', 'zh-TW': 'Plugin scaffold 預覽', es: 'Vista previa del scaffold de plugin' },
  'Workflow Preview': { ko: '워크플로우 미리보기', ja: 'ワークフロープレビュー', 'zh-CN': '工作流预览', 'zh-TW': '工作流程預覽', es: 'Vista previa del flujo de trabajo' },
  'Running inference…': { ko: '추론 실행 중…', ja: '推論実行中…', 'zh-CN': '正在运行推理…', 'zh-TW': '正在執行推論…', es: 'Ejecutando inferencia…' },
  'frames': { ko: '프레임', ja: 'フレーム', 'zh-CN': '帧', 'zh-TW': '影格', es: 'fotogramas' },
  // ── Entries moved from the markup lang-spans ──
  'Advanced Tools': {
    ko: '고급 도구',
    ja: '高度なツール',
    'zh-CN': '高级工具',
    'zh-TW': '進階工具',
    es: 'Herramientas avanzadas',
  },
  'Auto-generate skeleton code (Factory, Postprocessor, Visualizer, Runner) for a new task type.<br>To add a model to an existing task, use the <strong>Add Model</strong> tab.': {
    ko: '새 작업 유형에 대한 스켈레톤 코드 (Factory, Postprocessor, Visualizer, Runner)를 자동 생성합니다.<br>기존 작업에 모델을 추가하려면 <strong>모델 추가</strong> 탭을 사용하세요.',
    ja: '新しいタスクタイプのスケルトンコード (Factory, Postprocessor, Visualizer, Runner) を自動生成します。<br>既存タスクにモデルを追加するには<strong>モデル追加</strong>タブを使用してください。',
    'zh-CN': '为新任务类型自动生成骨架代码 (Factory, Postprocessor, Visualizer, Runner)。<br>要向现有任务添加模型，请使用<strong>添加模型</strong>选项卡。',
    'zh-TW': '為新任務類型自動產生骨架程式碼 (Factory, Postprocessor, Visualizer, Runner)。<br>要將模型新增至現有任務，請使用<strong>新增模型</strong>分頁。',
    es: 'Generación automática de código esqueleto (Factory, Postprocessor, Visualizer, Runner) para un nuevo tipo de tarea.<br>Para añadir un modelo a una tarea existente, use la pestaña <strong>Añadir modelo</strong>.',
  },
  'Build the DX-RT runtime and install the dx_engine Python API into venv-dx-runtime →': {
    ko: 'DX-RT 런타임을 빌드하고 dx_engine Python API를 venv-dx-runtime에 설치 →',
    ja: 'DX-RT ランタイムをビルドし、dx_engine Python API を venv-dx-runtime にインストール →',
    'zh-CN': '构建 DX-RT 运行时并将 dx_engine Python API 安装到 venv-dx-runtime →',
    'zh-TW': '建置 DX-RT 執行環境並將 dx_engine Python API 安裝到 venv-dx-runtime →',
    es: 'Compile el runtime DX-RT e instale la API de Python dx_engine en venv-dx-runtime →',
  },
  'Choose a pre-configured demo scenario and see the results instantly.': {
    ko: '사전 구성된 데모 시나리오를 선택하고 실행 결과를 바로 확인하세요.',
    ja: '事前設定済みのデモシナリオを選択し、実行結果をすぐに確認できます。',
    'zh-CN': '选择预配置的演示场景，立即查看运行结果。',
    'zh-TW': '選擇預先設定的示範情境，立即查看執行結果。',
    es: 'Elija un escenario de demostración preconfigurado y vea los resultados al instante.',
  },
  'Class': {
    ko: '클래스',
    ja: 'クラス',
    'zh-CN': '类别',
    'zh-TW': '類別',
    es: 'Clase',
  },
  'Code Language': {
    ko: '코드 언어',
    ja: 'コード言語',
    'zh-CN': '代码语言',
    'zh-TW': '程式語言',
    es: 'Lenguaje de código',
  },
  'Create Task': {
    ko: '작업 생성',
    ja: 'タスク作成',
    'zh-CN': '创建任务',
    'zh-TW': '建立任務',
    es: 'Crear tarea',
  },
  'DX-Runtime Build': {
    ko: 'DX-Runtime 빌드',
    ja: 'DX-Runtime ビルド',
    'zh-CN': 'DX-Runtime 构建',
    'zh-TW': 'DX-Runtime 建置',
    es: 'Compilación de DX-Runtime',
  },
  'Demo Quick Start': {
    ko: '데모만 빠르게 시작',
    ja: 'デモ クイックスタート',
    'zh-CN': '演示快速开始',
    'zh-TW': '示範快速開始',
    es: 'Inicio rápido de la demo',
  },
  'Experiment': {
    ko: '실험 실행',
    ja: '実験',
    'zh-CN': '实验',
    'zh-TW': '實驗',
    es: 'Experimento',
  },
  'Frames': {
    ko: '프레임',
    ja: 'フレーム',
    'zh-CN': '帧',
    'zh-TW': '影格',
    es: 'Cuadros',
  },
  'Generate a new task skeleton': {
    ko: '새 작업 유형 스켈레톤 생성',
    ja: '新しいタスクスケルトンを生成',
    'zh-CN': '生成新的任务骨架',
    'zh-TW': '產生新的任務骨架',
    es: 'Generar un esqueleto de tarea nuevo',
  },
  'Generated Files': {
    ko: '생성 파일',
    ja: '生成ファイル',
    'zh-CN': '生成的文件',
    'zh-TW': '產生的檔案',
    es: 'Archivos generados',
  },
  'Inspect change plans and rollback guidance': {
    ko: '변경 계획과 롤백 안내 확인',
    ja: '変更計画とロールバックガイドを確認',
    'zh-CN': '检查变更计划和回滚指引',
    'zh-TW': '檢查變更計畫和復原指引',
    es: 'Inspeccione planes de cambio y guía de reversión',
  },
  'Install only what the demo needs, in one go — downloads only the required models and skips steps already done': {
    ko: '데모에 필요한 것만 한 번에 설치 — 필요한 모델만 다운로드, 이미 된 단계는 건너뜀',
    ja: 'デモに必要なものだけを一度にインストール — 必要なモデルのみダウンロードし、完了済みの手順はスキップします',
    'zh-CN': '一次性只安装演示所需内容 — 仅下载所需模型，跳过已完成的步骤',
    'zh-TW': '一次只安裝示範所需內容 — 僅下載所需模型，略過已完成的步驟',
    es: 'Instale solo lo que la demo necesita, de una vez — descarga solo los modelos necesarios y omite los pasos ya completados',
  },
  'Lab': {
    ko: '실험실',
    ja: 'ラボ',
    'zh-CN': '实验室',
    'zh-TW': '實驗室',
    es: 'Laboratorio',
  },
  'Manage model/task extensions, experiments, and safe change previews in one place.': {
    ko: '모델·작업 확장, 실험 실행, 안전한 변경 미리보기를 한 곳에서 관리합니다.',
    ja: 'モデル・タスク拡張、実験、安全な変更プレビューを一か所で管理します。',
    'zh-CN': '在一处管理模型/任务扩展、实验和安全变更预览。',
    'zh-TW': '在一處管理模型/任務擴充、實驗和安全變更預覽。',
    es: 'Gestione extensiones de modelos y tareas, experimentos y vistas previas seguras de cambios en un solo lugar.',
  },
  'Objectness Threshold': {
    ko: 'Objectness 임계값',
    ja: 'Objectness しきい値',
    'zh-CN': 'Objectness 阈值',
    'zh-TW': 'Objectness 閾值',
    es: 'Umbral de objectness',
  },
  'Output Language': {
    ko: '출력 언어',
    ja: '出力言語',
    'zh-CN': '输出语言',
    'zh-TW': '輸出語言',
    es: 'Idioma de salida',
  },
  'Packages are saved to <code>outputs/</code> directory. Use the Outputs page to download.': {
    ko: '패키지는 <code>outputs/</code> 디렉토리에 저장됩니다. Outputs 페이지에서 다운로드하세요.',
    ja: 'パッケージは <code>outputs/</code> ディレクトリに保存されます。Outputs ページからダウンロードしてください。',
    'zh-CN': '包保存在 <code>outputs/</code> 目录中。请使用 Outputs 页面下载。',
    'zh-TW': '套件儲存在 <code>outputs/</code> 目錄中。請使用 Outputs 頁面下載。',
    es: 'Los paquetes se guardan en el directorio <code>outputs/</code>. Use la página Salidas para descargarlos.',
  },
  'Preparing Lab session': {
    ko: 'Lab 세션 준비 중',
    ja: 'Lab セッション準備中',
    'zh-CN': '正在准备 Lab 会话',
    'zh-TW': '正在準備 Lab 工作階段',
    es: 'Preparando sesión de laboratorio',
  },
  'Preview manifest before applying': {
    ko: '매니페스트 미리보기 후 적용',
    ja: '適用前にマニフェストをプレビュー',
    'zh-CN': '应用前预览清单',
    'zh-TW': '套用前預覽資訊清單',
    es: 'Vista previa del manifiesto antes de aplicar',
  },
  'Review generated artifacts': {
    ko: '생성된 산출물 확인',
    ja: '生成された成果物を確認',
    'zh-CN': '查看生成的产物',
    'zh-TW': '檢閱產生的產出物',
    es: 'Revisar artefactos generados',
  },
  'Run DXNN experiment pipeline': {
    ko: 'DXNN 실험 파이프라인 실행',
    ja: 'DXNN 実験パイプラインを実行',
    'zh-CN': '运行 DXNN 实验流水线',
    'zh-TW': '執行 DXNN 實驗管線',
    es: 'Ejecutar pipeline de experimentos DXNN',
  },
  'Run Demo': {
    ko: '데모 실행',
    ja: 'デモ実行',
    'zh-CN': '运行演示',
    'zh-TW': '執行示範',
    es: 'Ejecutar demo',
  },
  'Safety Center': {
    ko: '안전 센터',
    ja: '安全センター',
    'zh-CN': '安全中心',
    'zh-TW': '安全中心',
    es: 'Centro de seguridad',
  },
  'Start Demo Setup': {
    ko: '데모 설정 시작',
    ja: 'デモ設定を開始',
    'zh-CN': '开始演示设置',
    'zh-TW': '開始示範設定',
    es: 'Iniciar configuración de demo',
  },
  'Try demo': {
    ko: '데모 사용해보기',
    ja: 'デモを試す',
    'zh-CN': '试用演示',
    'zh-TW': '試用示範',
    es: 'Probar demo',
  },
  'Type input to send to the process (press Enter)': {
    ko: '프로세스에 보낼 입력을 입력하세요 (Enter 키)',
    ja: 'プロセスに送信する入力を入力してください (Enter キー)',
    'zh-CN': '输入要发送到进程的内容 (按 Enter)',
    'zh-TW': '輸入要傳送至程序的內容 (按 Enter)',
    es: 'Escriba la entrada para enviar al proceso (presione Enter)',
  },
  'Upload image': {
    ko: '이미지 업로드',
    ja: '画像アップロード',
    'zh-CN': '上传图像',
    'zh-TW': '上傳影像',
    es: 'Subir imagen',
  },
  'Version Info': {
    ko: '버전 정보',
    ja: 'バージョン情報',
    'zh-CN': '版本信息',
    'zh-TW': '版本資訊',
    es: 'Información de versión',
  },
  'No models are installed yet': {
    ko: '설치된 모델이 없습니다', ja: 'インストール済みのモデルがありません',
    'zh-CN': '尚未安装任何模型', 'zh-TW': '尚未安裝任何模型',
    es: 'Aún no hay modelos instalados',
  },
  'Download one from ModelZoo to run inference.': {
    ko: 'ModelZoo에서 모델을 내려받으면 추론을 실행할 수 있습니다.',
    ja: 'ModelZoo からモデルをダウンロードすると推論を実行できます。',
    'zh-CN': '从 ModelZoo 下载模型后即可运行推理。',
    'zh-TW': '從 ModelZoo 下載模型後即可執行推論。',
    es: 'Descargue uno desde ModelZoo para ejecutar inferencia.',
  },
  'Open ModelZoo': {
    ko: 'ModelZoo 열기', ja: 'ModelZoo を開く',
    'zh-CN': '打开 ModelZoo', 'zh-TW': '開啟 ModelZoo',
    es: 'Abrir ModelZoo',
  },
  /* Lab — Add Model copies an existing example */
  'Start from': {
    ko: '복사할 예제', ja: 'コピー元の例',
    'zh-CN': '起始示例', 'zh-TW': '起始範例',
    es: 'Partir de',
  },
  /* ==== Graph Composer (graph-*.js, shared/static/dx-graph-canvas.js, templates #page-graph) ==== */
  'Graph Composer': {
    ko: '그래프 Composer', ja: 'グラフコンポーザー',
    'zh-CN': '图编排器', 'zh-TW': '圖編排器',
    es: 'Compositor de grafos',
  },
  'Connect several models into one pipeline, check it, and run it on the NPU.': {
    ko: '여러 모델을 하나의 파이프라인으로 연결하고, 검사한 뒤 NPU에서 실행합니다.', ja: '複数のモデルを一つのパイプラインにつなぎ、検証して NPU で実行します。',
    'zh-CN': '将多个模型连接成一条流水线，检查后在 NPU 上运行。', 'zh-TW': '將多個模型連接成一條管線，檢查後在 NPU 上執行。',
    es: 'Conecte varios modelos en una canalización, compruébela y ejecútela en la NPU.',
  },
  'New graph': {
    ko: '새 그래프', ja: '新しいグラフ',
    'zh-CN': '新建图', 'zh-TW': '新增圖',
    es: 'Nuevo grafo',
  },
  'Project name': {
    ko: '프로젝트 이름', ja: 'プロジェクト名',
    'zh-CN': '项目名称', 'zh-TW': '專案名稱',
    es: 'Nombre del proyecto',
  },
  'Open project': {
    ko: '프로젝트 열기', ja: 'プロジェクトを開く',
    'zh-CN': '打开项目', 'zh-TW': '開啟專案',
    es: 'Abrir proyecto',
  },
  'Version': {
    ko: '버전', ja: 'バージョン',
    'zh-CN': '版本', 'zh-TW': '版本',
    es: 'Versión',
  },
  'Save': {
    ko: '저장', ja: '保存',
    'zh-CN': '保存', 'zh-TW': '儲存',
    es: 'Guardar',
  },
  'Import JSON': {
    ko: 'JSON 가져오기', ja: 'JSON をインポート',
    'zh-CN': '导入 JSON', 'zh-TW': '匯入 JSON',
    es: 'Importar JSON',
  },
  'Validate': {
    ko: '검사', ja: '検証',
    'zh-CN': '验证', 'zh-TW': '驗證',
    es: 'Validar',
  },
  'Palette': {
    ko: '팔레트', ja: 'パレット',
    'zh-CN': '组件面板', 'zh-TW': '元件面板',
    es: 'Paleta',
  },
  'Search models…': {
    ko: '모델 검색…', ja: 'モデルを検索…',
    'zh-CN': '搜索模型…', 'zh-TW': '搜尋模型…',
    es: 'Buscar modelos…',
  },
  'Search models': {
    ko: '모델 검색', ja: 'モデルを検索',
    'zh-CN': '搜索模型', 'zh-TW': '搜尋模型',
    es: 'Buscar modelos',
  },
  'Checking the graph…': {
    ko: '그래프를 검사하는 중…', ja: 'グラフを検証しています…',
    'zh-CN': '正在检查图…', 'zh-TW': '正在檢查圖…',
    es: 'Comprobando el grafo…',
  },
  'The graph runner is not built. Build dx_app (./build.sh) to use the Graph Composer.': {
    ko: '그래프 실행 파일이 빌드되지 않았습니다. Graph Composer를 쓰려면 dx_app을 빌드하세요 (./build.sh).', ja: 'グラフ実行ファイルがビルドされていません。Graph Composer を使うには dx_app をビルドしてください (./build.sh)。',
    'zh-CN': '图运行程序尚未构建。要使用图编排器，请构建 dx_app (./build.sh)。', 'zh-TW': '圖執行程式尚未建置。要使用圖編排器，請建置 dx_app (./build.sh)。',
    es: 'El ejecutor de grafos no está compilado. Compile dx_app (./build.sh) para usar el compositor de grafos.',
  },
  'Empty graph': {
    ko: '빈 그래프', ja: '空のグラフ',
    'zh-CN': '空图', 'zh-TW': '空白圖',
    es: 'Grafo vacío',
  },
  'Could not check the graph': {
    ko: '그래프를 검사하지 못했습니다', ja: 'グラフを検証できませんでした',
    'zh-CN': '无法检查该图', 'zh-TW': '無法檢查該圖',
    es: 'No se pudo comprobar el grafo',
  },
  '{n} problems to fix': {
    ko: '고칠 문제 {n}개', ja: '修正が必要な問題: {n} 件',
    'zh-CN': '有 {n} 个问题需要修复', 'zh-TW': '有 {n} 個問題需要修正',
    es: '{n} problemas por corregir',
  },
  '{n} models are not installed': {
    ko: '설치되지 않은 모델 {n}개', ja: '未インストールのモデル: {n} 件',
    'zh-CN': '有 {n} 个模型未安装', 'zh-TW': '有 {n} 個模型未安裝',
    es: '{n} modelos no están instalados',
  },
  'Over the NPU memory budget': {
    ko: 'NPU 메모리 한도를 넘습니다', ja: 'NPU メモリの上限を超えています',
    'zh-CN': '超出 NPU 内存预算', 'zh-TW': '超出 NPU 記憶體預算',
    es: 'Supera la memoria disponible de la NPU',
  },
  'Ready to run': {
    ko: '실행 준비 완료', ja: '実行できます',
    'zh-CN': '可以运行', 'zh-TW': '可以執行',
    es: 'Listo para ejecutar',
  },
  'Unsaved changes': {
    ko: '저장하지 않은 변경 사항', ja: '未保存の変更',
    'zh-CN': '有未保存的更改', 'zh-TW': '有未儲存的變更',
    es: 'Cambios sin guardar',
  },
  'Share one engine between {nodes} ({model}): saves {saves}': {
    ko: '{nodes}가 엔진 하나를 공유 ({model}): {saves} 절약', ja: '{nodes} で 1 つのエンジンを共有 ({model}): {saves} 削減',
    'zh-CN': '让 {nodes} 共用一个引擎 ({model})：节省 {saves}', 'zh-TW': '讓 {nodes} 共用一個引擎 ({model})：節省 {saves}',
    es: 'Compartir un motor entre {nodes} ({model}): ahorra {saves}',
  },
  'Use {n} buffers on {nodes}: saves {saves}': {
    ko: '{nodes}에서 buffer {n}개 사용: {saves} 절약', ja: '{nodes} でバッファーを {n} 個に: {saves} 削減',
    'zh-CN': '在 {nodes} 上使用 {n} 个缓冲区：节省 {saves}', 'zh-TW': '在 {nodes} 上使用 {n} 個緩衝區：節省 {saves}',
    es: 'Usar {n} búferes en {nodes}: ahorra {saves}',
  },
  'NPU memory': {
    ko: 'NPU 메모리', ja: 'NPU メモリ',
    'zh-CN': 'NPU 内存', 'zh-TW': 'NPU 記憶體',
    es: 'Memoria de la NPU',
  },
  '{used} of {free} free': {
    ko: '여유 {free} 중 {used}', ja: '空き {free} のうち {used}',
    'zh-CN': '可用 {free} 中的 {used}', 'zh-TW': '可用 {free} 中的 {used}',
    es: '{used} de {free} libres',
  },
  'Not counted (model file missing): {models}': {
    ko: '계산에서 빠짐 (모델 파일 없음): {models}', ja: '集計外 (モデルファイルなし): {models}',
    'zh-CN': '未计入（缺少模型文件）：{models}', 'zh-TW': '未計入（缺少模型檔案）：{models}',
    es: 'Sin contar (falta el archivo del modelo): {models}',
  },
  'This dx_app build does not apply engine options yet; the estimate shows what they will save.': {
    ko: '이 dx_app 빌드는 아직 engine 옵션을 적용하지 않습니다. 추정치는 적용되었을 때 절약되는 양을 보여 줍니다.', ja: 'この dx_app ビルドはまだ engine オプションを適用しません。見積もりは適用後に削減される量を示します。',
    'zh-CN': '此 dx_app 版本尚未应用 engine 选项；估算显示应用后可节省的量。', 'zh-TW': '此 dx_app 版本尚未套用 engine 選項；估算顯示套用後可節省的量。',
    es: 'Esta compilación de dx_app aún no aplica las opciones de engine; la estimación muestra lo que ahorrarán.',
  },
  'Ways to fit': {
    ko: '맞추는 방법', ja: '収める方法',
    'zh-CN': '缩减方法', 'zh-TW': '縮減方法',
    es: 'Cómo hacer que quepa',
  },
  'Apply': {
    ko: '적용', ja: '適用',
    'zh-CN': '应用', 'zh-TW': '套用',
    es: 'Aplicar',
  },
  'Discard the unsaved changes to this graph?': {
    ko: '이 그래프의 저장하지 않은 변경 사항을 버릴까요?', ja: 'このグラフの未保存の変更を破棄しますか?',
    'zh-CN': '放弃此图未保存的更改？', 'zh-TW': '放棄此圖未儲存的變更？',
    es: '¿Descartar los cambios sin guardar de este grafo?',
  },
  'Open project…': {
    ko: '프로젝트 열기…', ja: 'プロジェクトを開く…',
    'zh-CN': '打开项目…', 'zh-TW': '開啟專案…',
    es: 'Abrir proyecto…',
  },
  'No versions': {
    ko: '버전 없음', ja: 'バージョンなし',
    'zh-CN': '无版本', 'zh-TW': '無版本',
    es: 'Sin versiones',
  },
  'Version {n}': {
    ko: '버전 {n}', ja: 'バージョン {n}',
    'zh-CN': '版本 {n}', 'zh-TW': '版本 {n}',
    es: 'Versión {n}',
  },
  'This file is not a Graph Composer project.': {
    ko: 'Graph Composer 프로젝트 파일이 아닙니다.', ja: 'Graph Composer のプロジェクトファイルではありません。',
    'zh-CN': '该文件不是图编排器项目。', 'zh-TW': '該檔案不是圖編排器專案。',
    es: 'Este archivo no es un proyecto del compositor de grafos.',
  },
  'Add a node before saving.': {
    ko: '저장하기 전에 노드를 추가하세요.', ja: '保存する前にノードを追加してください。',
    'zh-CN': '保存前请先添加节点。', 'zh-TW': '儲存前請先新增節點。',
    es: 'Añada un nodo antes de guardar.',
  },
  'Untitled graph': {
    ko: '제목 없는 그래프', ja: '無題のグラフ',
    'zh-CN': '未命名图', 'zh-TW': '未命名圖',
    es: 'Grafo sin título',
  },
  'Saved {name}, version {n}': {
    ko: '{name} 저장됨 (버전 {n})', ja: '{name} を保存しました (バージョン {n})',
    'zh-CN': '已保存 {name}（版本 {n}）', 'zh-TW': '已儲存 {name}（版本 {n}）',
    es: 'Se guardó {name}, versión {n}',
  },
  'Delete the project {name} and all its versions?': {
    ko: '프로젝트 {name}와 모든 버전을 삭제할까요?', ja: 'プロジェクト {name} とすべてのバージョンを削除しますか?',
    'zh-CN': '删除项目 {name} 及其所有版本？', 'zh-TW': '刪除專案 {name} 及其所有版本？',
    es: '¿Eliminar el proyecto {name} y todas sus versiones?',
  },
  'Installed': {
    ko: '설치됨', ja: 'インストール済み',
    'zh-CN': '已安装', 'zh-TW': '已安裝',
    es: 'Instalado',
  },
  'Not installed': {
    ko: '설치 안 됨', ja: '未インストール',
    'zh-CN': '未安装', 'zh-TW': '未安裝',
    es: 'No instalado',
  },
  'Broken file': {
    ko: '손상된 파일', ja: '壊れたファイル',
    'zh-CN': '文件损坏', 'zh-TW': '檔案損壞',
    es: 'Archivo dañado',
  },
  'Needs a newer DX-RT': {
    ko: '더 새로운 DX-RT 필요', ja: '新しい DX-RT が必要',
    'zh-CN': '需要更新的 DX-RT', 'zh-TW': '需要更新的 DX-RT',
    es: 'Requiere un DX-RT más reciente',
  },
  'Not graph-ready': {
    ko: '그래프에서 사용 불가', ja: 'グラフでは使えません',
    'zh-CN': '不可用于图', 'zh-TW': '不可用於圖',
    es: 'No disponible en grafos',
  },
  'Add to the graph': {
    ko: '그래프에 추가', ja: 'グラフに追加',
    'zh-CN': '添加到图', 'zh-TW': '新增到圖',
    es: 'Añadir al grafo',
  },
  'Add {name} to the graph': {
    ko: '{name}을(를) 그래프에 추가', ja: '{name} をグラフに追加',
    'zh-CN': '将 {name} 添加到图', 'zh-TW': '將 {name} 新增到圖',
    es: 'Añadir {name} al grafo',
  },
  'Needs DX-RT {version} or later': {
    ko: 'DX-RT {version} 이상 필요', ja: 'DX-RT {version} 以降が必要',
    'zh-CN': '需要 DX-RT {version} 或更高版本', 'zh-TW': '需要 DX-RT {version} 或更新版本',
    es: 'Requiere DX-RT {version} o posterior',
  },
  'frame or crop': {
    ko: '프레임 또는 crop', ja: 'フレームまたはクロップ',
    'zh-CN': '整帧或裁剪', 'zh-TW': '整幀或裁切',
    es: 'fotograma o recorte',
  },
  'full frame': {
    ko: '전체 프레임', ja: 'フレーム全体',
    'zh-CN': '整帧', 'zh-TW': '整幀',
    es: 'fotograma completo',
  },
  'Open': {
    ko: '열기', ja: '開く',
    'zh-CN': '打开', 'zh-TW': '開啟',
    es: 'Abrir',
  },
  'Open the example {name}': {
    ko: '예제 {name} 열기', ja: 'サンプル {name} を開く',
    'zh-CN': '打开示例 {name}', 'zh-TW': '開啟範例 {name}',
    es: 'Abrir el ejemplo {name}',
  },
  'Examples': {
    ko: '예제', ja: 'サンプル',
    'zh-CN': '示例', 'zh-TW': '範例',
    es: 'Ejemplos',
  },
  'Sources': {
    ko: '소스', ja: 'ソース',
    'zh-CN': '源', 'zh-TW': '來源',
    es: 'Fuentes',
  },
  'Image or video': {
    ko: '이미지 또는 비디오', ja: '画像または動画',
    'zh-CN': '图片或视频', 'zh-TW': '圖片或影片',
    es: 'Imagen o vídeo',
  },
  'CPU ops': {
    ko: 'CPU 연산', ja: 'CPU 演算',
    'zh-CN': 'CPU 运算', 'zh-TW': 'CPU 運算',
    es: 'Operaciones de CPU',
  },
  'takes {inputs}': {
    ko: '입력: {inputs}', ja: '入力: {inputs}',
    'zh-CN': '输入：{inputs}', 'zh-TW': '輸入：{inputs}',
    es: 'recibe {inputs}',
  },
  'Problems': {
    ko: '문제', ja: '問題',
    'zh-CN': '问题', 'zh-TW': '問題',
    es: 'Problemas',
  },
  'Remove {name}': {
    ko: '{name} 제거', ja: '{name} を削除',
    'zh-CN': '移除 {name}', 'zh-TW': '移除 {name}',
    es: 'Quitar {name}',
  },
  'name, e.g. score_threshold': {
    ko: '이름 (예: score_threshold)', ja: '名前 (例: score_threshold)',
    'zh-CN': '名称，例如 score_threshold', 'zh-TW': '名稱，例如 score_threshold',
    es: 'nombre, p. ej. score_threshold',
  },
  'Parameter name': {
    ko: '파라미터 이름', ja: 'パラメーター名',
    'zh-CN': '参数名称', 'zh-TW': '參數名稱',
    es: 'Nombre del parámetro',
  },
  'value': {
    ko: '값', ja: '値',
    'zh-CN': '值', 'zh-TW': '值',
    es: 'valor',
  },
  'Parameter value': {
    ko: '파라미터 값', ja: 'パラメーター値',
    'zh-CN': '参数值', 'zh-TW': '參數值',
    es: 'Valor del parámetro',
  },
  'Parameters': {
    ko: '파라미터', ja: 'パラメーター',
    'zh-CN': '参数', 'zh-TW': '參數',
    es: 'Parámetros',
  },
  'Overrides the model config.json for this node. Lists such as class_names are comma separated.': {
    ko: '이 노드에서만 모델의 config.json 값을 덮어씁니다. class_names 같은 목록은 쉼표로 구분합니다.', ja: 'このノードだけモデルの config.json を上書きします。class_names などのリストはカンマ区切りです。',
    'zh-CN': '仅对此节点覆盖模型的 config.json。class_names 等列表用逗号分隔。', 'zh-TW': '僅對此節點覆寫模型的 config.json。class_names 等清單以逗號分隔。',
    es: 'Sustituye el config.json del modelo solo en este nodo. Las listas como class_names van separadas por comas.',
  },
  '"base" and "events" are reserved: dx_app names its layer files after them. Pick another name.': {
    ko: '"base"와 "events"는 예약된 이름입니다. dx_app이 레이어 파일 이름에 사용합니다. 다른 이름을 고르세요.',
    ja: '"base" と "events" は予約済みの名前です。dx_app がレイヤーファイルの名前に使います。別の名前を選んでください。',
    'zh-CN': '"base" 和 "events" 是保留名称，dx_app 用它们命名图层文件。请换一个名称。',
    'zh-TW': '"base" 和 "events" 是保留名稱，dx_app 用它們命名圖層檔案。請換一個名稱。',
    es: '"base" y "events" están reservados: dx_app nombra con ellos sus archivos de capa. Elija otro nombre.',
  },
  'Use letters, digits, _ or -, starting with a letter.': {
    ko: '영문자, 숫자, _ 또는 -만 쓰고 영문자로 시작하세요.', ja: '英字、数字、_ または - を使い、英字で始めてください。',
    'zh-CN': '请使用字母、数字、_ 或 -，并以字母开头。', 'zh-TW': '請使用字母、數字、_ 或 -，並以字母開頭。',
    es: 'Use letras, dígitos, _ o -, empezando por una letra.',
  },
  'Another node already has this name.': {
    ko: '같은 이름의 노드가 이미 있습니다.', ja: '同じ名前のノードがすでにあります。',
    'zh-CN': '已有同名节点。', 'zh-TW': '已有同名節點。',
    es: 'Otro nodo ya tiene este nombre.',
  },
  'Node name': {
    ko: '노드 이름', ja: 'ノード名',
    'zh-CN': '节点名称', 'zh-TW': '節點名稱',
    es: 'Nombre del nodo',
  },
  'Connect to…': {
    ko: '연결할 노드…', ja: '接続先…',
    'zh-CN': '连接到…', 'zh-TW': '連接到…',
    es: 'Conectar con…',
  },
  'Connect to': {
    ko: '연결', ja: '接続先',
    'zh-CN': '连接到', 'zh-TW': '連接到',
    es: 'Conectar con',
  },
  'The keyboard way to draw an edge from this node.': {
    ko: '키보드로 이 노드에서 연결선을 그립니다.', ja: 'キーボードでこのノードから接続を引きます。',
    'zh-CN': '用键盘从此节点画一条连接。', 'zh-TW': '用鍵盤從此節點畫一條連接。',
    es: 'La forma de trazar una conexión desde este nodo con el teclado.',
  },
  '{mb} on the NPU': {
    ko: 'NPU에서 {mb}', ja: 'NPU 上で {mb}',
    'zh-CN': '在 NPU 上占用 {mb}', 'zh-TW': '在 NPU 上佔用 {mb}',
    es: '{mb} en la NPU',
  },
  'Uses the engine of {nodes}': {
    ko: '{nodes}의 엔진을 함께 사용', ja: '{nodes} のエンジンを共用',
    'zh-CN': '共用 {nodes} 的引擎', 'zh-TW': '共用 {nodes} 的引擎',
    es: 'Usa el motor de {nodes}',
  },
  '{shape} · {frames} frames · {items} results · {crops} crops': {
    ko: '{shape} · 프레임 {frames} · 결과 {items} · crop {crops}', ja: '{shape} · {frames} フレーム · 結果 {items} · クロップ {crops}',
    'zh-CN': '{shape} · {frames} 帧 · {items} 个结果 · {crops} 个裁剪', 'zh-TW': '{shape} · {frames} 幀 · {items} 個結果 · {crops} 個裁切',
    es: '{shape} · {frames} fotogramas · {items} resultados · {crops} recortes',
  },
  '{ms} ms per frame': {
    ko: '프레임당 {ms} ms', ja: '1 フレームあたり {ms} ms',
    'zh-CN': '每帧 {ms} ms', 'zh-TW': '每幀 {ms} ms',
    es: '{ms} ms por fotograma',
  },
  'Last run': {
    ko: '마지막 실행', ja: '前回の実行',
    'zh-CN': '上次运行', 'zh-TW': '上次執行',
    es: 'Última ejecución',
  },
  'An image or video under the dx_app folder, camera:0 or rtsp://… (Run once takes images and videos).': {
    ko: 'dx_app 폴더 아래의 이미지나 비디오, camera:0 또는 rtsp://… (한 번 실행은 이미지와 비디오만 받습니다).', ja: 'dx_app フォルダー内の画像や動画、camera:0 または rtsp://… (1 回実行は画像と動画のみ)。',
    'zh-CN': 'dx_app 文件夹下的图片或视频、camera:0 或 rtsp://…（单次运行只接受图片和视频）。', 'zh-TW': 'dx_app 資料夾下的圖片或影片、camera:0 或 rtsp://…（單次執行只接受圖片和影片）。',
    es: 'Una imagen o un vídeo dentro de la carpeta de dx_app, camera:0 o rtsp://… (Ejecutar una vez admite imágenes y vídeos).',
  },
  '{task} · produces {produces} · takes {consumes}': {
    ko: '{task} · 출력 {produces} · 입력 {consumes}', ja: '{task} · 出力 {produces} · 入力 {consumes}',
    'zh-CN': '{task} · 输出 {produces} · 输入 {consumes}', 'zh-TW': '{task} · 輸出 {produces} · 輸入 {consumes}',
    es: '{task} · produce {produces} · recibe {consumes}',
  },
  'Track objects across frames (IoU tracker)': {
    ko: '프레임 사이에서 객체 추적 (IoU tracker)', ja: 'フレーム間でオブジェクトを追跡 (IoU トラッカー)',
    'zh-CN': '跨帧跟踪目标（IoU 跟踪器）', 'zh-TW': '跨幀追蹤目標（IoU 追蹤器）',
    es: 'Seguir objetos entre fotogramas (rastreador IoU)',
  },
  'Overlap to keep a track (IoU)': {
    ko: '추적을 유지할 겹침 (IoU)', ja: '追跡を続ける重なり (IoU)',
    'zh-CN': '保持跟踪所需的重叠（IoU）', 'zh-TW': '保持追蹤所需的重疊（IoU）',
    es: 'Solapamiento para mantener un seguimiento (IoU)',
  },
  'Frames a lost track survives': {
    ko: '놓친 추적이 유지되는 프레임 수', ja: '見失った追跡を保つフレーム数',
    'zh-CN': '丢失的轨迹保留的帧数', 'zh-TW': '遺失的軌跡保留的幀數',
    es: 'Fotogramas que sobrevive un seguimiento perdido',
  },
  'Tracking': {
    ko: '추적', ja: '追跡',
    'zh-CN': '跟踪', 'zh-TW': '追蹤',
    es: 'Seguimiento',
  },
  'Default (6)': {
    ko: '기본값 (6)', ja: '既定 (6)',
    'zh-CN': '默认 (6)', 'zh-TW': '預設 (6)',
    es: 'Predeterminado (6)',
  },
  'NPU engine': {
    ko: 'NPU 엔진', ja: 'NPU エンジン',
    'zh-CN': 'NPU 引擎', 'zh-TW': 'NPU 引擎',
    es: 'Motor de la NPU',
  },
  'Buffers': {
    ko: 'Buffer', ja: 'バッファー',
    'zh-CN': '缓冲区', 'zh-TW': '緩衝區',
    es: 'Búferes',
  },
  'Fewer buffers use less NPU memory and may lower throughput.': {
    ko: 'buffer가 적을수록 NPU 메모리를 덜 쓰지만 처리량이 줄 수 있습니다.', ja: 'バッファーを減らすと NPU メモリは減りますが、スループットが下がることがあります。',
    'zh-CN': '缓冲区越少，占用的 NPU 内存越少，但吞吐量可能降低。', 'zh-TW': '緩衝區越少，佔用的 NPU 記憶體越少，但輸送量可能降低。',
    es: 'Menos búferes usan menos memoria de la NPU y pueden reducir el rendimiento.',
  },
  'Share one engine with other nodes of this model': {
    ko: '이 모델의 다른 노드와 엔진 하나를 공유', ja: 'このモデルの他のノードと 1 つのエンジンを共有',
    'zh-CN': '与此模型的其他节点共用一个引擎', 'zh-TW': '與此模型的其他節點共用一個引擎',
    es: 'Compartir un motor con otros nodos de este modelo',
  },
  'Takes the results of: {inputs}': {
    ko: '받는 결과: {inputs}', ja: '受け取る結果: {inputs}',
    'zh-CN': '接收的结果：{inputs}', 'zh-TW': '接收的結果：{inputs}',
    es: 'Recibe los resultados de: {inputs}',
  },
  'CPU op': {
    ko: 'CPU 연산', ja: 'CPU 演算',
    'zh-CN': 'CPU 运算', 'zh-TW': 'CPU 運算',
    es: 'Operación de CPU',
  },
  'Delete node': {
    ko: '노드 삭제', ja: 'ノードを削除',
    'zh-CN': '删除节点', 'zh-TW': '刪除節點',
    es: 'Eliminar nodo',
  },
  'Whole frame': {
    ko: '전체 프레임', ja: 'フレーム全体',
    'zh-CN': '整帧', 'zh-TW': '整幀',
    es: 'Fotograma completo',
  },
  'One run per box (ROI crop)': {
    ko: '박스마다 한 번 실행 (ROI crop)', ja: 'ボックスごとに 1 回実行 (ROI クロップ)',
    'zh-CN': '每个框运行一次（ROI 裁剪）', 'zh-TW': '每個框執行一次（ROI 裁切）',
    es: 'Una ejecución por caja (recorte ROI)',
  },
  'Results to a CPU op': {
    ko: '결과를 CPU 연산으로', ja: '結果を CPU 演算へ',
    'zh-CN': '将结果传给 CPU 运算', 'zh-TW': '將結果傳給 CPU 運算',
    es: 'Resultados a una operación de CPU',
  },
  'Connection': {
    ko: '연결', ja: '接続',
    'zh-CN': '连接', 'zh-TW': '連接',
    es: 'Conexión',
  },
  'Crops': {
    ko: 'Crop', ja: 'クロップ',
    'zh-CN': '裁剪', 'zh-TW': '裁切',
    es: 'Recortes',
  },
  'Comma separated, e.g. person, car. Empty: every box.': {
    ko: '쉼표로 구분 (예: person, car). 비우면 모든 박스.', ja: 'カンマ区切り (例: person, car)。空欄ならすべてのボックス。',
    'zh-CN': '用逗号分隔，例如 person, car。留空表示所有框。', 'zh-TW': '以逗號分隔，例如 person, car。留空表示所有框。',
    es: 'Separadas por comas, p. ej. person, car. Vacío: todas las cajas.',
  },
  'Minimum score': {
    ko: '최소 점수', ja: '最小スコア',
    'zh-CN': '最低分数', 'zh-TW': '最低分數',
    es: 'Puntuación mínima',
  },
  'Minimum area (px²)': {
    ko: '최소 면적 (px²)', ja: '最小面積 (px²)',
    'zh-CN': '最小面积（px²）', 'zh-TW': '最小面積（px²）',
    es: 'Área mínima (px²)',
  },
  'Padding (share of the box per side)': {
    ko: '여백 (변마다 박스 크기 대비 비율)', ja: '余白 (各辺のボックスに対する割合)',
    'zh-CN': '外扩（每边占框尺寸的比例）', 'zh-TW': '外擴（每邊占框尺寸的比例）',
    es: 'Margen (fracción de la caja por lado)',
  },
  'At most this many boxes': {
    ko: '최대 박스 수', ja: '最大ボックス数',
    'zh-CN': '最多框数', 'zh-TW': '最多框數',
    es: 'Como máximo este número de cajas',
  },
  'Alignment': {
    ko: '정렬', ja: '位置合わせ',
    'zh-CN': '对齐', 'zh-TW': '對齊',
    es: 'Alineación',
  },
  'Five face landmarks (face5)': {
    ko: '얼굴 랜드마크 5개 (face5)', ja: '顔のランドマーク 5 点 (face5)',
    'zh-CN': '五个面部关键点（face5）', 'zh-TW': '五個臉部關鍵點（face5）',
    es: 'Cinco puntos faciales (face5)',
  },
  'Primary output': {
    ko: '기본 출력', ja: '主出力',
    'zh-CN': '主输出', 'zh-TW': '主要輸出',
    es: 'Salida principal',
  },
  'Delete connection': {
    ko: '연결 삭제', ja: '接続を削除',
    'zh-CN': '删除连接', 'zh-TW': '刪除連接',
    es: 'Eliminar conexión',
  },
  'Select a node or a connection to edit it.': {
    ko: '편집할 노드나 연결을 선택하세요.', ja: '編集するノードまたは接続を選択してください。',
    'zh-CN': '选择要编辑的节点或连接。', 'zh-TW': '選擇要編輯的節點或連接。',
    es: 'Seleccione un nodo o una conexión para editarlo.',
  },
  'Start from an example in the palette, or add a source and a model.': {
    ko: '팔레트의 예제로 시작하거나 소스와 모델을 추가하세요.', ja: 'パレットのサンプルから始めるか、ソースとモデルを追加してください。',
    'zh-CN': '从组件面板中的示例开始，或添加一个源和一个模型。', 'zh-TW': '從元件面板中的範例開始，或新增一個來源和一個模型。',
    es: 'Empiece con un ejemplo de la paleta o añada una fuente y un modelo.',
  },
  '{n} nodes selected': {
    ko: '노드 {n}개 선택됨', ja: '{n} 個のノードを選択中',
    'zh-CN': '已选择 {n} 个节点', 'zh-TW': '已選擇 {n} 個節點',
    es: '{n} nodos seleccionados',
  },
  'Run once takes images and videos. Camera and RTSP sources come with Live.': {
    ko: '한 번 실행은 이미지와 비디오만 받습니다. 카메라와 RTSP 소스는 Live에서 지원됩니다.', ja: '1 回実行は画像と動画のみです。カメラと RTSP のソースは Live で対応します。',
    'zh-CN': '单次运行只接受图片和视频。摄像头和 RTSP 源将在 Live 中支持。', 'zh-TW': '單次執行只接受圖片和影片。攝影機和 RTSP 來源將在 Live 中支援。',
    es: 'Ejecutar una vez admite imágenes y vídeos. Las fuentes de cámara y RTSP llegan con Live.',
  },
  'This input does not exist or is outside the dx_app, sample and outputs folders.': {
    ko: '이 입력이 없거나 dx_app, sample, outputs 폴더 밖에 있습니다.', ja: 'この入力は存在しないか、dx_app・sample・outputs フォルダーの外にあります。',
    'zh-CN': '此输入不存在，或不在 dx_app、sample、outputs 文件夹中。', 'zh-TW': '此輸入不存在，或不在 dx_app、sample、outputs 資料夾中。',
    es: 'Esta entrada no existe o está fuera de las carpetas dx_app, sample y outputs.',
  },
  'A graph run is already running.': {
    ko: '그래프 실행이 이미 진행 중입니다.', ja: 'グラフの実行がすでに進行中です。',
    'zh-CN': '已有图正在运行。', 'zh-TW': '已有圖正在執行。',
    es: 'Ya hay una ejecución de grafo en curso.',
  },
  'The run failed.': {
    ko: '실행에 실패했습니다.', ja: '実行に失敗しました。',
    'zh-CN': '运行失败。', 'zh-TW': '執行失敗。',
    es: 'La ejecución falló.',
  },
  'Add a source to run the graph.': {
    ko: '그래프를 실행하려면 소스를 추가하세요.', ja: 'グラフを実行するにはソースを追加してください。',
    'zh-CN': '要运行图，请添加一个源。', 'zh-TW': '要執行圖，請新增一個來源。',
    es: 'Añada una fuente para ejecutar el grafo.',
  },
  'As in the graph: {uri}': {
    ko: '그래프 설정대로: {uri}', ja: 'グラフの設定どおり: {uri}',
    'zh-CN': '按图中设置：{uri}', 'zh-TW': '依圖中設定：{uri}',
    es: 'Como en el grafo: {uri}',
  },
  'Upload an image…': {
    ko: '이미지 업로드…', ja: '画像をアップロード…',
    'zh-CN': '上传图片…', 'zh-TW': '上傳圖片…',
    es: 'Subir una imagen…',
  },
  'Input for {source}': {
    ko: '{source}의 입력', ja: '{source} の入力',
    'zh-CN': '{source} 的输入', 'zh-TW': '{source} 的輸入',
    es: 'Entrada de {source}',
  },
  'Sync (one stage at a time)': {
    ko: 'Sync (한 번에 한 단계)', ja: 'Sync (1 段ずつ)',
    'zh-CN': 'Sync（一次一个阶段）', 'zh-TW': 'Sync（一次一個階段）',
    es: 'Sync (una etapa a la vez)',
  },
  'Async (stages overlap)': {
    ko: 'Async (단계가 겹쳐 실행)', ja: 'Async (段が重なって実行)',
    'zh-CN': 'Async（阶段重叠执行）', 'zh-TW': 'Async（階段重疊執行）',
    es: 'Async (las etapas se solapan)',
  },
  'all': {
    ko: '전체', ja: 'すべて',
    'zh-CN': '全部', 'zh-TW': '全部',
    es: 'todos',
  },
  'Run once': {
    ko: '한 번 실행', ja: '1 回実行',
    'zh-CN': '运行一次', 'zh-TW': '執行一次',
    es: 'Ejecutar una vez',
  },
  'Frames in flight': {
    ko: '동시에 처리할 프레임', ja: '同時処理フレーム数',
    'zh-CN': '同时处理的帧数', 'zh-TW': '同時處理的幀數',
    es: 'Fotogramas en curso',
  },
  'Stop after frames': {
    ko: '이 프레임 수 후 중지', ja: 'このフレーム数で停止',
    'zh-CN': '处理到此帧数后停止', 'zh-TW': '處理到此幀數後停止',
    es: 'Detener tras estos fotogramas',
  },
  '{frames} frames': {
    ko: '{frames} 프레임', ja: '{frames} フレーム',
    'zh-CN': '{frames} 帧', 'zh-TW': '{frames} 幀',
    es: '{frames} fotogramas',
  },
  '{fps} FPS (average {avg})': {
    ko: '{fps} FPS (평균 {avg})', ja: '{fps} FPS (平均 {avg})',
    'zh-CN': '{fps} FPS（平均 {avg}）', 'zh-TW': '{fps} FPS（平均 {avg}）',
    es: '{fps} FPS (media {avg})',
  },
  '{s} s': {
    ko: '{s}초', ja: '{s} 秒',
    'zh-CN': '{s} 秒', 'zh-TW': '{s} 秒',
    es: '{s} s',
  },
  'Done: {frames} frames in {s} s': {
    ko: '완료: {s}초 동안 {frames} 프레임', ja: '完了: {s} 秒で {frames} フレーム',
    'zh-CN': '完成：{s} 秒处理 {frames} 帧', 'zh-TW': '完成：{s} 秒處理 {frames} 幀',
    es: 'Terminado: {frames} fotogramas en {s} s',
  },
  'The run stopped with exit code {code}': {
    ko: '실행이 종료 코드 {code}로 멈췄습니다', ja: '実行は終了コード {code} で停止しました',
    'zh-CN': '运行以退出码 {code} 停止', 'zh-TW': '執行以結束代碼 {code} 停止',
    es: 'La ejecución terminó con el código de salida {code}',
  },
  'Result of {name}': {
    ko: '{name}의 결과', ja: '{name} の結果',
    'zh-CN': '{name} 的结果', 'zh-TW': '{name} 的結果',
    es: 'Resultado de {name}',
  },
  'Node': {
    ko: '노드', ja: 'ノード',
    'zh-CN': '节点', 'zh-TW': '節點',
    es: 'Nodo',
  },
  'ms per frame': {
    ko: '프레임당 ms', ja: '1 フレームあたり ms',
    'zh-CN': '每帧 ms', 'zh-TW': '每幀 ms',
    es: 'ms por fotograma',
  },
  'Graph canvas. Tab moves between nodes, [ and ] between their connections, arrow keys move the selection, Delete removes it, Ctrl+Z undoes.': {
    ko: '그래프 캔버스. Tab으로 노드 사이를, [ 와 ]로 연결 사이를 이동하고, 화살표 키로 선택 항목을 옮기며, Delete로 지우고, Ctrl+Z로 되돌립니다.', ja: 'グラフキャンバス。Tab でノード間を、[ と ] で接続間を移動し、矢印キーで選択を動かし、Delete で削除、Ctrl+Z で元に戻します。',
    'zh-CN': '图画布。Tab 在节点间移动，[ 和 ] 在连接间移动，方向键移动所选项，Delete 删除，Ctrl+Z 撤销。', 'zh-TW': '圖畫布。Tab 在節點間移動，[ 和 ] 在連接間移動，方向鍵移動所選項目，Delete 刪除，Ctrl+Z 復原。',
    es: 'Lienzo del grafo. Tab cambia de nodo, [ y ] recorren sus conexiones, las flechas mueven la selección, Supr la elimina y Ctrl+Z deshace.',
  },
  'Edge {from} to {to}': {
    ko: '{from}에서 {to}(으)로 가는 연결', ja: '{from} から {to} への接続',
    'zh-CN': '从 {from} 到 {to} 的连接', 'zh-TW': '從 {from} 到 {to} 的連接',
    es: 'Conexión de {from} a {to}',
  },
  'No connections': {
    ko: '연결 없음', ja: '接続なし',
    'zh-CN': '没有连接', 'zh-TW': '沒有連接',
    es: 'Sin conexiones',
  },
  'Align left': {
    ko: '왼쪽 맞춤', ja: '左揃え',
    'zh-CN': '左对齐', 'zh-TW': '靠左對齊',
    es: 'Alinear a la izquierda',
  },
  'Align center': {
    ko: '가운데 맞춤', ja: '中央揃え',
    'zh-CN': '水平居中', 'zh-TW': '水平置中',
    es: 'Centrar horizontalmente',
  },
  'Align top': {
    ko: '위쪽 맞춤', ja: '上揃え',
    'zh-CN': '顶端对齐', 'zh-TW': '靠上對齊',
    es: 'Alinear arriba',
  },
  'Align middle': {
    ko: '세로 가운데 맞춤', ja: '上下中央揃え',
    'zh-CN': '垂直居中', 'zh-TW': '垂直置中',
    es: 'Centrar verticalmente',
  },
  'Distribute horizontally': {
    ko: '가로 간격 균등', ja: '左右に均等配置',
    'zh-CN': '水平均匀分布', 'zh-TW': '水平均勻分布',
    es: 'Distribuir horizontalmente',
  },
  'Distribute vertically': {
    ko: '세로 간격 균등', ja: '上下に均等配置',
    'zh-CN': '垂直均匀分布', 'zh-TW': '垂直均勻分布',
    es: 'Distribuir verticalmente',
  },
  'Graph canvas tools': {
    ko: '그래프 캔버스 도구', ja: 'グラフキャンバスのツール',
    'zh-CN': '图画布工具', 'zh-TW': '圖畫布工具',
    es: 'Herramientas del lienzo',
  },
  'Auto layout': {
    ko: '자동 배치', ja: '自動レイアウト',
    'zh-CN': '自动布局', 'zh-TW': '自動配置',
    es: 'Distribución automática',
  },
  'Copy': {
    ko: '복사', ja: 'コピー',
    'zh-CN': '复制', 'zh-TW': '複製',
    es: 'Copiar',
  },
  'Paste': {
    ko: '붙여넣기', ja: '貼り付け',
    'zh-CN': '粘贴', 'zh-TW': '貼上',
    es: 'Pegar',
  },
  'Duplicate': {
    ko: '복제', ja: '複製',
    'zh-CN': '创建副本', 'zh-TW': '建立副本',
    es: 'Duplicar',
  },
  'Select all': {
    ko: '모두 선택', ja: 'すべて選択',
    'zh-CN': '全选', 'zh-TW': '全選',
    es: 'Seleccionar todo',
  },
  'Drag items from the palette, or select one and press Enter': {
    ko: '팔레트에서 항목을 끌어오거나, 하나를 선택하고 Enter를 누르세요', ja: 'パレットから項目をドラッグするか、選択して Enter を押してください',
    'zh-CN': '从组件面板拖入项目，或选中一个后按 Enter', 'zh-TW': '從元件面板拖入項目，或選取一個後按 Enter',
    es: 'Arrastre elementos desde la paleta o seleccione uno y pulse Intro',
  },
  'Selected {label}': {
    ko: '{label} 선택됨', ja: '{label} を選択',
    'zh-CN': '已选择 {label}', 'zh-TW': '已選擇 {label}',
    es: 'Seleccionado: {label}',
  },
  'Connected {from} to {to}': {
    ko: '{from}을(를) {to}에 연결함', ja: '{from} を {to} に接続しました',
    'zh-CN': '已将 {from} 连接到 {to}', 'zh-TW': '已將 {from} 連接到 {to}',
    es: 'Se conectó {from} con {to}',
  },
  'Cannot connect: {reason}': {
    ko: '연결할 수 없음: {reason}', ja: '接続できません: {reason}',
    'zh-CN': '无法连接：{reason}', 'zh-TW': '無法連接：{reason}',
    es: 'No se puede conectar: {reason}',
  },
  'This would create a cycle': {
    ko: '순환이 생깁니다', ja: '循環ができてしまいます',
    'zh-CN': '这会形成环', 'zh-TW': '這會形成循環',
    es: 'Esto crearía un ciclo',
  },
  'These nodes are already connected': {
    ko: '이미 연결된 노드입니다', ja: 'これらのノードはすでに接続されています',
    'zh-CN': '这些节点已经连接', 'zh-TW': '這些節點已經連接',
    es: 'Estos nodos ya están conectados',
  },
  'Deleted {n}': {
    ko: '{n}개 삭제함', ja: '{n} 件削除しました',
    'zh-CN': '已删除 {n} 项', 'zh-TW': '已刪除 {n} 項',
    es: 'Se eliminaron {n}',
  },
  'A source has no input': {
    ko: '소스에는 입력이 없습니다', ja: 'ソースには入力がありません',
    'zh-CN': '源没有输入', 'zh-TW': '來源沒有輸入',
    es: 'Una fuente no tiene entrada',
  },
  'A CPU op ends a branch': {
    ko: 'CPU 연산은 분기의 끝입니다', ja: 'CPU 演算は分岐の終端です',
    'zh-CN': 'CPU 运算是分支的终点', 'zh-TW': 'CPU 運算是分支的終點',
    es: 'Una operación de CPU cierra una rama',
  },
  'A CPU op takes results from models': {
    ko: 'CPU 연산은 모델의 결과를 받습니다', ja: 'CPU 演算はモデルの結果を受け取ります',
    'zh-CN': 'CPU 运算接收模型的结果', 'zh-TW': 'CPU 運算接收模型的結果',
    es: 'Una operación de CPU recibe resultados de modelos',
  },
  'This model does not take a full frame': {
    ko: '이 모델은 전체 프레임을 받지 않습니다', ja: 'このモデルはフレーム全体を受け取りません',
    'zh-CN': '该模型不接受整帧', 'zh-TW': '該模型不接受整幀',
    es: 'Este modelo no recibe un fotograma completo',
  },
  'This model needs a full frame; boxes can only feed a model that takes crops': {
    ko: '이 모델은 전체 프레임이 필요합니다. 박스는 crop을 받는 모델에만 연결할 수 있습니다', ja: 'このモデルはフレーム全体が必要です。ボックスはクロップを受け取るモデルにしか渡せません',
    'zh-CN': '该模型需要整帧；框只能传给接受裁剪的模型', 'zh-TW': '該模型需要整幀；框只能傳給接受裁切的模型',
    es: 'Este modelo necesita un fotograma completo; las cajas solo pueden ir a un modelo que reciba recortes',
  },
  'This model takes crops, and an image is a full frame': {
    ko: '이 모델은 crop을 받는데, 이미지는 전체 프레임입니다', ja: 'このモデルはクロップを受け取りますが、画像はフレーム全体です',
    'zh-CN': '该模型接受裁剪，而图片是整帧', 'zh-TW': '該模型接受裁切，而圖片是整幀',
    es: 'Este modelo recibe recortes y una imagen es un fotograma completo',
  },
  'Only boxes (as crops) or an image can feed another model': {
    ko: '다른 모델에는 박스 (crop으로) 또는 이미지만 넘길 수 있습니다', ja: '他のモデルに渡せるのはボックス (クロップとして) か画像だけです',
    'zh-CN': '只有框（作为裁剪）或图片可以传给另一个模型', 'zh-TW': '只有框（作為裁切）或圖片可以傳給另一個模型',
    es: 'Solo las cajas (como recortes) o una imagen pueden alimentar otro modelo',
  },
  'ROI': {
    ko: 'ROI', ja: 'ROI',
    'zh-CN': 'ROI', 'zh-TW': 'ROI',
    es: 'ROI',
  },
  'result': {
    ko: '결과', ja: '結果',
    'zh-CN': '结果', 'zh-TW': '結果',
    es: 'resultado',
  },
  'port': {
    ko: '포트', ja: 'ポート',
    'zh-CN': '端口', 'zh-TW': '連接埠',
    es: 'puerto',
  },
  'error': {
    ko: '오류', ja: 'エラー',
    'zh-CN': '错误', 'zh-TW': '錯誤',
    es: 'error',
  },
  'not installed': {
    ko: '설치 안 됨', ja: '未インストール',
    'zh-CN': '未安装', 'zh-TW': '未安裝',
    es: 'no instalado',
  },
  'shared': {
    ko: '공유', ja: '共有',
    'zh-CN': '共用', 'zh-TW': '共用',
    es: 'compartido',
  },
  'Unknown model': {
    ko: '알 수 없는 모델', ja: '不明なモデル',
    'zh-CN': '未知模型', 'zh-TW': '未知模型',
    es: 'Modelo desconocido',
  },
  '{n} model files cannot be used': {
    ko: '사용할 수 없는 모델 파일 {n}개', ja: '使用できないモデルファイル: {n} 件',
    'zh-CN': '有 {n} 个模型文件无法使用', 'zh-TW': '有 {n} 個模型檔案無法使用',
    es: '{n} archivos de modelo no se pueden usar',
  },
  'Choose a card above to start.': {
    ko: '위의 카드를 골라 시작하세요.', ja: '上のカードを選んで始めてください。',
    'zh-CN': '选择上方的卡片开始。', 'zh-TW': '選擇上方的卡片開始。',
    es: 'Elija una tarjeta de arriba para empezar.',
  },
  'The uploaded images add up to {mb} MB; one run takes at most {max} MB. Use smaller images or a sample.': {
    ko: '업로드한 이미지가 모두 {mb} MB입니다. 한 번 실행에는 최대 {max} MB까지 올릴 수 있습니다. 더 작은 이미지나 샘플을 쓰세요.', ja: 'アップロードした画像の合計は {mb} MB です。1 回の実行で送れるのは最大 {max} MB です。小さい画像かサンプルを使ってください。',
    'zh-CN': '上传的图片共 {mb} MB；一次运行最多 {max} MB。请使用较小的图片或示例。', 'zh-TW': '上傳的圖片共 {mb} MB；一次執行最多 {max} MB。請使用較小的圖片或範例。',
    es: 'Las imágenes subidas suman {mb} MB; una ejecución admite como máximo {max} MB. Use imágenes más pequeñas o una de muestra.',
  },
  'The download status stopped answering. Check Model Zoo, then refresh the palette.': {
    ko: '다운로드 상태가 응답하지 않습니다. Model Zoo를 확인한 뒤 팔레트를 새로 고치세요.', ja: 'ダウンロード状態が応答しなくなりました。Model Zoo を確認してからパレットを更新してください。',
    'zh-CN': '下载状态不再响应。请检查 Model Zoo，然后刷新组件面板。', 'zh-TW': '下載狀態不再回應。請檢查 Model Zoo，然後重新整理元件面板。',
    es: 'El estado de la descarga dejó de responder. Revise Model Zoo y actualice la paleta.',
  },
  /* ── Graph Composer, Phase 2: logic blocks, zone editor, events, Live ── */
  'A logic block takes results, not frames': {
    ko: 'Logic 블록은 프레임이 아니라 결과를 받습니다', ja: 'ロジックブロックはフレームではなく結果を受け取ります',
    'zh-CN': '逻辑块接收的是结果，而不是帧', 'zh-TW': '邏輯區塊接收的是結果，而不是影格',
    es: 'Un bloque lógico recibe resultados, no fotogramas',
  },
  'This logic block does not take this kind of result': {
    ko: '이 Logic 블록은 이런 종류의 결과를 받지 않습니다', ja: 'このロジックブロックはこの種類の結果を受け取りません',
    'zh-CN': '该逻辑块不接受这种结果', 'zh-TW': '該邏輯區塊不接受這種結果',
    es: 'Este bloque lógico no recibe este tipo de resultado',
  },
  'This logic block takes no more inputs': {
    ko: '이 Logic 블록은 입력을 더 받지 않습니다', ja: 'このロジックブロックはこれ以上入力を受け取りません',
    'zh-CN': '该逻辑块不再接受更多输入', 'zh-TW': '該邏輯區塊不再接受更多輸入',
    es: 'Este bloque lógico no admite más entradas',
  },
  'Only a block that hands on boxes can feed a model, as crops': {
    ko: '박스를 넘기는 블록만 모델에 crop으로 연결할 수 있습니다', ja: 'ボックスを渡すブロックだけがモデルにクロップとして渡せます',
    'zh-CN': '只有输出框的块才能以裁剪的形式传给模型', 'zh-TW': '只有輸出框的區塊才能以裁切的形式傳給模型',
    es: 'Solo un bloque que entrega cajas puede alimentar un modelo, como recortes',
  },
  'Logic': {
    ko: 'Logic', ja: 'ロジック',
    'zh-CN': '逻辑', 'zh-TW': '邏輯',
    es: 'Lógica',
  },
  'Events: {n}': {
    ko: '이벤트: {n}', ja: 'イベント: {n}',
    'zh-CN': '事件：{n}', 'zh-TW': '事件：{n}',
    es: 'Eventos: {n}',
  },
  'Templates': {
    ko: 'Template', ja: 'テンプレート',
    'zh-CN': '模板', 'zh-TW': '範本',
    es: 'Plantillas',
  },
  'Open the template {name}': {
    ko: '{name} Template 열기', ja: 'テンプレート {name} を開く',
    'zh-CN': '打开模板 {name}', 'zh-TW': '開啟範本 {name}',
    es: 'Abrir la plantilla {name}',
  },
  'any result': {
    ko: '모든 결과', ja: '任意の結果',
    'zh-CN': '任意结果', 'zh-TW': '任意結果',
    es: 'cualquier resultado',
  },
  'This dx_app build has no logic blocks yet.': {
    ko: '이 dx_app 빌드에는 아직 Logic 블록이 없습니다.', ja: 'この dx_app ビルドにはまだロジックブロックがありません。',
    'zh-CN': '此 dx_app 构建尚无逻辑块。', 'zh-TW': '此 dx_app 建置尚無邏輯區塊。',
    es: 'Esta compilación de dx_app aún no tiene bloques lógicos.',
  },
  'Filter': {
    ko: '필터', ja: 'フィルター',
    'zh-CN': '过滤', 'zh-TW': '過濾',
    es: 'Filtro',
  },
  'Zone': {
    ko: '구역', ja: 'ゾーン',
    'zh-CN': '区域', 'zh-TW': '區域',
    es: 'Zona',
  },
  'Line crossing': {
    ko: '선 통과', ja: 'ライン通過',
    'zh-CN': '越线', 'zh-TW': '越線',
    es: 'Cruce de línea',
  },
  'Dwell': {
    ko: '체류 시간', ja: '滞留時間',
    'zh-CN': '停留时间', 'zh-TW': '停留時間',
    es: 'Permanencia',
  },
  'Condition → Event': {
    ko: '조건 → 이벤트', ja: '条件 → イベント',
    'zh-CN': '条件 → 事件', 'zh-TW': '條件 → 事件',
    es: 'Condición → Evento',
  },
  'Gallery match': {
    ko: 'Gallery 대조', ja: 'ギャラリー照合',
    'zh-CN': '图库比对', 'zh-TW': '圖庫比對',
    es: 'Coincidencia con galería',
  },
  'User logic': {
    ko: '사용자 Logic', ja: 'ユーザーロジック',
    'zh-CN': '用户逻辑', 'zh-TW': '使用者邏輯',
    es: 'Lógica de usuario',
  },
  'Logic block': {
    ko: 'Logic 블록', ja: 'ロジックブロック',
    'zh-CN': '逻辑块', 'zh-TW': '邏輯區塊',
    es: 'Bloque lógico',
  },
  'Results to a logic block': {
    ko: 'Logic 블록으로 결과 전달', ja: 'ロジックブロックへ結果を渡す',
    'zh-CN': '把结果传给逻辑块', 'zh-TW': '把結果傳給邏輯區塊',
    es: 'Resultados a un bloque lógico',
  },
  'Takes {inputs} · hands on {output}': {
    ko: '입력 {inputs} · 출력 {output}', ja: '入力 {inputs} · 出力 {output}',
    'zh-CN': '输入 {inputs} · 输出 {output}', 'zh-TW': '輸入 {inputs} · 輸出 {output}',
    es: 'Recibe {inputs} · entrega {output}',
  },
  'Fires: {events}': {
    ko: '발생 이벤트: {events}', ja: '発生するイベント: {events}',
    'zh-CN': '触发事件：{events}', 'zh-TW': '觸發事件：{events}',
    es: 'Dispara: {events}',
  },
  'Track objects on {nodes}': {
    ko: '{nodes}에서 객체 추적 켜기', ja: '{nodes} でオブジェクト追跡をオンにする',
    'zh-CN': '在 {nodes} 上开启目标跟踪', 'zh-TW': '在 {nodes} 上開啟目標追蹤',
    es: 'Seguir objetos en {nodes}',
  },
  'Studio runs this block as a pass-through. An exported project gets a function stub named {name} where you write the logic.': {
    ko: 'Studio에서는 이 블록이 입력을 그대로 넘깁니다. 내보낸 프로젝트에는 처리 코드를 직접 작성할 {name} 함수 stub이 생깁니다.', ja: 'Studio ではこのブロックは入力をそのまま渡します。エクスポートしたプロジェクトには、ロジックを書く関数スタブ {name} が入ります。',
    'zh-CN': 'Studio 中该块原样传递输入。导出的项目会包含名为 {name} 的函数桩，供你编写逻辑。', 'zh-TW': 'Studio 中該區塊原樣傳遞輸入。匯出的專案會包含名為 {name} 的函式樁，供你撰寫邏輯。',
    es: 'Studio deja pasar los datos por este bloque. Un proyecto exportado incluye un esbozo de función llamado {name} donde escribir la lógica.',
  },
  'This dx_app build does not list this block; its params are edited as text.': {
    ko: '이 dx_app 빌드는 이 블록을 알려 주지 않아 파라미터를 텍스트로 편집합니다.', ja: 'この dx_app ビルドはこのブロックを一覧にないため、パラメーターはテキストで編集します。',
    'zh-CN': '此 dx_app 构建未列出该块，其参数以文本形式编辑。', 'zh-TW': '此 dx_app 建置未列出該區塊，其參數以文字形式編輯。',
    es: 'Esta compilación de dx_app no lista este bloque; sus parámetros se editan como texto.',
  },
  'Default ({value})': {
    ko: '기본값 ({value})', ja: 'デフォルト ({value})',
    'zh-CN': '默认值 ({value})', 'zh-TW': '預設值 ({value})',
    es: 'Por defecto ({value})',
  },
  'Default': {
    ko: '기본값', ja: 'デフォルト',
    'zh-CN': '默认值', 'zh-TW': '預設值',
    es: 'Por defecto',
  },
  '{min} to {max}': {
    ko: '{min} ~ {max}', ja: '{min} ～ {max}',
    'zh-CN': '{min} 到 {max}', 'zh-TW': '{min} 到 {max}',
    es: 'de {min} a {max}',
  },
  'at least {min}': {
    ko: '{min} 이상', ja: '{min} 以上',
    'zh-CN': '至少 {min}', 'zh-TW': '至少 {min}',
    es: 'al menos {min}',
  },
  'Comma separated. Empty: all.': {
    ko: '쉼표로 구분합니다. 비우면 전체입니다.', ja: 'カンマ区切り。空欄ならすべて。',
    'zh-CN': '以逗号分隔。留空表示全部。', 'zh-TW': '以逗號分隔。留空表示全部。',
    es: 'Separados por comas. Vacío: todos.',
  },
  'Edit {param} on the frame': {
    ko: '프레임 위에서 {param} 편집', ja: 'フレーム上で {param} を編集',
    'zh-CN': '在帧上编辑 {param}', 'zh-TW': '在影格上編輯 {param}',
    es: 'Editar {param} sobre el fotograma',
  },
  'Edit on the frame…': {
    ko: '프레임 위에서 편집…', ja: 'フレーム上で編集…',
    'zh-CN': '在帧上编辑…', 'zh-TW': '在影格上編輯…',
    es: 'Editar sobre el fotograma…',
  },
  'Events: {events}': {
    ko: '이벤트: {events}', ja: 'イベント: {events}',
    'zh-CN': '事件：{events}', 'zh-TW': '事件：{events}',
    es: 'Eventos: {events}',
  },
  'Zone tools': {
    ko: '구역 도구', ja: 'ゾーンツール',
    'zh-CN': '区域工具', 'zh-TW': '區域工具',
    es: 'Herramientas de zona',
  },
  'Points': {
    ko: '점', ja: '点',
    'zh-CN': '点', 'zh-TW': '點',
    es: 'Puntos',
  },
  'Point {n} {axis}': {
    ko: '점 {n} {axis}', ja: '点 {n} の {axis}',
    'zh-CN': '点 {n} 的 {axis}', 'zh-TW': '點 {n} 的 {axis}',
    es: 'Punto {n} {axis}',
  },
  'Point {n} of {total}: x {x}, y {y}': {
    ko: '점 {n} / {total}: x {x}, y {y}', ja: '点 {n} / {total}: x {x}、y {y}',
    'zh-CN': '第 {n} 个点（共 {total} 个）：x {x}，y {y}', 'zh-TW': '第 {n} 個點（共 {total} 個）：x {x}，y {y}',
    es: 'Punto {n} de {total}: x {x}, y {y}',
  },
  'Add zone': {
    ko: '구역 추가', ja: 'ゾーンを追加',
    'zh-CN': '添加区域', 'zh-TW': '新增區域',
    es: 'Añadir zona',
  },
  'Flip direction': {
    ko: '방향 뒤집기', ja: '向きを反転',
    'zh-CN': '翻转方向', 'zh-TW': '翻轉方向',
    es: 'Invertir dirección',
  },
  'Delete point': {
    ko: '점 삭제', ja: '点を削除',
    'zh-CN': '删除点', 'zh-TW': '刪除點',
    es: 'Eliminar punto',
  },
  'Direction flipped': {
    ko: '방향을 뒤집었습니다', ja: '向きを反転しました',
    'zh-CN': '已翻转方向', 'zh-TW': '已翻轉方向',
    es: 'Dirección invertida',
  },
  'Drawing cancelled': {
    ko: '그리기를 취소했습니다', ja: '描画を取り消しました',
    'zh-CN': '已取消绘制', 'zh-TW': '已取消繪製',
    es: 'Dibujo cancelado',
  },
  'Click to add points; Enter, a double click or a click on the first point finishes; Escape cancels.': {
    ko: '클릭해서 점을 추가합니다. Enter, 더블 클릭 또는 첫 점을 클릭하면 끝나고, Escape로 취소합니다.', ja: 'クリックで点を追加します。Enter、ダブルクリック、または最初の点のクリックで完了し、Escape で取り消します。',
    'zh-CN': '单击添加点；按 Enter、双击或单击第一个点结束；按 Escape 取消。', 'zh-TW': '按一下新增點；按 Enter、按兩下或按第一個點結束；按 Escape 取消。',
    es: 'Haga clic para añadir puntos; Intro, un doble clic o un clic en el primer punto termina; Escape cancela.',
  },
  'A zone crosses itself; dx_app may read its inside differently.': {
    ko: '구역의 변이 서로 교차합니다. dx_app이 안쪽을 다르게 판단할 수 있습니다.', ja: 'ゾーンの辺が交差しています。dx_app が内側を違うように判断する場合があります。',
    'zh-CN': '区域的边相互交叉；dx_app 判断的内部可能与预期不同。', 'zh-TW': '區域的邊相互交叉；dx_app 判斷的內部可能與預期不同。',
    es: 'Una zona se cruza consigo misma; dx_app puede interpretar su interior de otra forma.',
  },
  'Done': {
    ko: '완료', ja: '完了',
    'zh-CN': '完成', 'zh-TW': '完成',
    es: 'Hecho',
  },
  'Events': {
    ko: '이벤트', ja: 'イベント',
    'zh-CN': '事件', 'zh-TW': '事件',
    es: 'Eventos',
  },
  'Event': {
    ko: '이벤트', ja: 'イベント',
    'zh-CN': '事件', 'zh-TW': '事件',
    es: 'Evento',
  },
  'Track id': {
    ko: 'track ID', ja: 'トラック ID',
    'zh-CN': '跟踪 ID', 'zh-TW': '追蹤 ID',
    es: 'ID de seguimiento',
  },
  'From (s)': {
    ko: '시작 (초)', ja: '開始 (秒)',
    'zh-CN': '起始（秒）', 'zh-TW': '起始（秒）',
    es: 'Desde (s)',
  },
  'To (s)': {
    ko: '끝 (초)', ja: '終了 (秒)',
    'zh-CN': '结束（秒）', 'zh-TW': '結束（秒）',
    es: 'Hasta (s)',
  },
  'Time (s)': {
    ko: '시간 (초)', ja: '時間 (秒)',
    'zh-CN': '时间（秒）', 'zh-TW': '時間（秒）',
    es: 'Tiempo (s)',
  },
  'Frame': {
    ko: '프레임', ja: 'フレーム',
    'zh-CN': '帧', 'zh-TW': '影格',
    es: 'Fotograma',
  },
  'Show': {
    ko: '보기', ja: '表示',
    'zh-CN': '显示', 'zh-TW': '顯示',
    es: 'Mostrar',
  },
  '{shown} of {total} events': {
    ko: '이벤트 {total}개 중 {shown}개', ja: 'イベント {total} 件中 {shown} 件',
    'zh-CN': '共 {total} 个事件，显示 {shown} 个', 'zh-TW': '共 {total} 個事件，顯示 {shown} 個',
    es: '{shown} de {total} eventos',
  },
  'Only the end of the log was read: the total and the counts are partial.': {
    ko: '로그의 마지막 부분만 읽었으므로 합계와 횟수는 일부입니다.', ja: 'ログの最後の部分だけを読み込みました。合計と件数は一部です。',
    'zh-CN': '只读取了日志的最后部分：总数和计数不完整。', 'zh-TW': '只讀取了日誌的最後部分：總數和計數不完整。',
    es: 'Solo se leyó el final del registro: el total y los recuentos son parciales.',
  },
  'the list shows the latest; the file has all of them': {
    ko: '목록에는 최근 것만 보이고, 파일에는 전부 있습니다', ja: '一覧には最新のものだけ表示され、ファイルにはすべて含まれます',
    'zh-CN': '列表只显示最新的，文件中包含全部', 'zh-TW': '清單只顯示最新的，檔案中包含全部',
    es: 'la lista muestra los más recientes; el archivo los tiene todos',
  },
  'Show event {n} in the video': {
    ko: '비디오에서 이벤트 {n} 보기', ja: '動画でイベント {n} を表示',
    'zh-CN': '在视频中显示事件 {n}', 'zh-TW': '在影片中顯示事件 {n}',
    es: 'Mostrar el evento {n} en el vídeo',
  },
  'Select node {node}': {
    ko: '{node} 노드 선택', ja: 'ノード {node} を選択',
    'zh-CN': '选择节点 {node}', 'zh-TW': '選擇節點 {node}',
    es: 'Seleccionar el nodo {node}',
  },
  'No events yet.': {
    ko: '아직 이벤트가 없습니다.', ja: 'まだイベントはありません。',
    'zh-CN': '尚无事件。', 'zh-TW': '尚無事件。',
    es: 'Aún no hay eventos.',
  },
  'No event matches the filters.': {
    ko: '필터에 맞는 이벤트가 없습니다.', ja: 'フィルターに一致するイベントはありません。',
    'zh-CN': '没有符合筛选条件的事件。', 'zh-TW': '沒有符合篩選條件的事件。',
    es: 'Ningún evento coincide con los filtros.',
  },
  'Download events (JSONL)': {
    ko: '이벤트 다운로드 (JSONL)', ja: 'イベントをダウンロード (JSONL)',
    'zh-CN': '下载事件（JSONL）', 'zh-TW': '下載事件（JSONL）',
    es: 'Descargar eventos (JSONL)',
  },
  'Run the graph': {
    ko: '그래프 실행', ja: 'グラフを実行',
    'zh-CN': '运行图', 'zh-TW': '執行圖',
    es: 'Ejecutar el grafo',
  },
  'Live': {
    ko: 'Live', ja: 'ライブ',
    'zh-CN': '实时', 'zh-TW': '即時',
    es: 'En vivo',
  },
  'Start Live': {
    ko: 'Live 시작', ja: 'ライブを開始',
    'zh-CN': '开始实时运行', 'zh-TW': '開始即時執行',
    es: 'Iniciar en vivo',
  },
  'Starting Live…': {
    ko: 'Live를 시작하는 중…', ja: 'ライブを開始しています…',
    'zh-CN': '正在开始实时运行…', 'zh-TW': '正在開始即時執行…',
    es: 'Iniciando en vivo…',
  },
  'Stopping…': {
    ko: '멈추는 중…', ja: '停止しています…',
    'zh-CN': '正在停止…', 'zh-TW': '正在停止…',
    es: 'Deteniendo…',
  },
  'Live stopped.': {
    ko: 'Live를 멈췄습니다.', ja: 'ライブを停止しました。',
    'zh-CN': '实时运行已停止。', 'zh-TW': '即時執行已停止。',
    es: 'En vivo detenido.',
  },
  'Live stopped: the page stopped asking for it.': {
    ko: 'Live를 멈췄습니다: 페이지가 더 이상 상태를 묻지 않았습니다.', ja: 'ライブを停止しました: ページから状態の問い合わせがなくなりました。',
    'zh-CN': '实时运行已停止：页面不再查询其状态。', 'zh-TW': '即時執行已停止：頁面不再查詢其狀態。',
    es: 'En vivo detenido: la página dejó de consultarlo.',
  },
  'Live ended (exit code {code}).': {
    ko: 'Live가 끝났습니다 (exit code {code}).', ja: 'ライブが終了しました (終了コード {code})。',
    'zh-CN': '实时运行已结束（退出码 {code}）。', 'zh-TW': '即時執行已結束（結束代碼 {code}）。',
    es: 'En vivo terminó (código de salida {code}).',
  },
  'Live failed to start.': {
    ko: 'Live를 시작하지 못했습니다.', ja: 'ライブを開始できませんでした。',
    'zh-CN': '实时运行未能启动。', 'zh-TW': '即時執行未能啟動。',
    es: 'No se pudo iniciar en vivo.',
  },
  'Live view of the graph': {
    ko: '그래프의 Live 화면', ja: 'グラフのライブ表示',
    'zh-CN': '图的实时画面', 'zh-TW': '圖的即時畫面',
    es: 'Vista en vivo del grafo',
  },
  'Live input for {source}': {
    ko: '{source}의 Live 입력', ja: '{source} のライブ入力',
    'zh-CN': '{source} 的实时输入', 'zh-TW': '{source} 的即時輸入',
    es: 'Entrada en vivo para {source}',
  },
  'Camera {n}': {
    ko: '카메라 {n}', ja: 'カメラ {n}',
    'zh-CN': '摄像头 {n}', 'zh-TW': '攝影機 {n}',
    es: 'Cámara {n}',
  },
  'RTSP stream…': {
    ko: 'RTSP 스트림…', ja: 'RTSP ストリーム…',
    'zh-CN': 'RTSP 流…', 'zh-TW': 'RTSP 串流…',
    es: 'Stream RTSP…',
  },
  'RTSP address for {source}': {
    ko: '{source}의 RTSP 주소', ja: '{source} の RTSP アドレス',
    'zh-CN': '{source} 的 RTSP 地址', 'zh-TW': '{source} 的 RTSP 位址',
    es: 'Dirección RTSP para {source}',
  },
  '{video} (looping)': {
    ko: '{video} (반복 재생)', ja: '{video} (ループ再生)',
    'zh-CN': '{video}（循环播放）', 'zh-TW': '{video}（循環播放）',
    es: '{video} (en bucle)',
  },
  'A video loops until you stop. One Live runs at a time; leaving this page stops it.': {
    ko: '비디오는 멈출 때까지 반복 재생됩니다. Live는 한 번에 하나만 실행되고, 이 페이지를 떠나면 멈춥니다.', ja: '動画は停止するまでループ再生されます。ライブは一度に 1 つだけで、このページを離れると停止します。',
    'zh-CN': '视频会循环播放直到你停止。一次只能运行一个实时任务；离开此页面会将其停止。', 'zh-TW': '影片會循環播放直到你停止。一次只能執行一個即時工作；離開此頁面會將其停止。',
    es: 'Un vídeo se repite hasta que lo detenga. Solo se ejecuta un en vivo a la vez; salir de esta página lo detiene.',
  },
  'Live needs these on this computer: {what}': {
    ko: 'Live에 필요한 항목이 이 컴퓨터에 없습니다: {what}', ja: 'ライブにはこのコンピューターに次が必要です: {what}',
    'zh-CN': '实时运行需要在此电脑上安装：{what}', 'zh-TW': '即時執行需要在此電腦上安裝：{what}',
    es: 'En vivo necesita esto en este equipo: {what}',
  },
  'This dx_app build cannot loop a video yet. Use a camera or an RTSP stream.': {
    ko: '이 dx_app 빌드는 아직 비디오를 반복 재생할 수 없습니다. 카메라나 RTSP 스트림을 쓰세요.', ja: 'この dx_app ビルドはまだ動画をループ再生できません。カメラか RTSP ストリームを使ってください。',
    'zh-CN': '此 dx_app 构建尚不能循环播放视频。请使用摄像头或 RTSP 流。', 'zh-TW': '此 dx_app 建置尚不能循環播放影片。請使用攝影機或 RTSP 串流。',
    es: 'Esta compilación de dx_app aún no puede repetir un vídeo. Use una cámara o un stream RTSP.',
  },
  'A graph Live is already running.': {
    ko: '그래프 Live가 이미 실행 중입니다.', ja: 'グラフのライブはすでに実行中です。',
    'zh-CN': '已有图的实时运行在进行。', 'zh-TW': '已有圖的即時執行在進行。',
    es: 'Ya hay un grafo en vivo en ejecución.',
  },
  'A graph run is running. Wait for it or stop it first.': {
    ko: '그래프 실행이 진행 중입니다. 끝날 때까지 기다리거나 먼저 멈추세요.', ja: 'グラフの実行中です。終わるのを待つか、先に停止してください。',
    'zh-CN': '图正在运行。请等待其结束或先停止它。', 'zh-TW': '圖正在執行。請等待其結束或先停止它。',
    es: 'Hay una ejecución del grafo en curso. Espere o deténgala primero.',
  },
  'The Run page has a Live run. Stop it there first.': {
    ko: 'Run 페이지에서 Live 실행이 진행 중입니다. 먼저 그곳에서 멈추세요.', ja: 'Run ページでライブ実行中です。先にそちらで停止してください。',
    'zh-CN': 'Run 页面有实时运行在进行。请先在那里停止。', 'zh-TW': 'Run 頁面有即時執行在進行。請先在那裡停止。',
    es: 'La página Run tiene una ejecución en vivo. Deténgala allí primero.',
  },
  'This input cannot stream: {why}': {
    ko: '이 입력은 Live로 읽을 수 없습니다: {why}', ja: 'この入力はストリーミングできません: {why}',
    'zh-CN': '此输入无法串流：{why}', 'zh-TW': '此輸入無法串流：{why}',
    es: 'Esta entrada no puede transmitirse: {why}',
  },
  'The graph is running Live. Stop Live first.': {
    ko: '그래프가 Live로 실행 중입니다. 먼저 Live를 멈추세요.', ja: 'グラフはライブで実行中です。先にライブを停止してください。',
    'zh-CN': '图正在实时运行。请先停止实时运行。', 'zh-TW': '圖正在即時執行。請先停止即時執行。',
    es: 'El grafo se está ejecutando en vivo. Detenga primero el en vivo.',
  },
  'graph_live_busy': {
    ko: 'Graph Composer에서 Live가 실행 중입니다. 먼저 멈추세요', ja: 'Graph Composer でライブ実行中です。先に停止してください',
    'zh-CN': 'Graph Composer 正在实时运行，请先停止', 'zh-TW': 'Graph Composer 正在即時執行，請先停止',
    es: 'El Graph Composer tiene un en vivo en ejecución; deténgalo primero',
  },
  /* Graph Composer results view (graph-results.js) and Live's "Draw" picker */
  'Layers': {
    ko: '레이어', ja: 'レイヤー',
    'zh-CN': '图层', 'zh-TW': '圖層',
    es: 'Capas',
  },
  'Event panel': {
    ko: '이벤트 패널', ja: 'イベントパネル',
    'zh-CN': '事件面板', 'zh-TW': '事件面板',
    es: 'Panel de eventos',
  },
  'Enlarge {source}': {
    ko: '{source} 크게 보기', ja: '{source} を拡大',
    'zh-CN': '放大 {source}', 'zh-TW': '放大 {source}',
    es: 'Ampliar {source}',
  },
  'Layers for this frame': {
    ko: '이 프레임의 레이어', ja: 'このフレームのレイヤー',
    'zh-CN': '此帧的图层', 'zh-TW': '此影格的圖層',
    es: 'Capas de este fotograma',
  },
  'Running the graph on this frame…': {
    ko: '이 프레임으로 그래프를 실행하는 중…', ja: 'このフレームでグラフを実行中…',
    'zh-CN': '正在用此帧运行图…', 'zh-TW': '正在用此影格執行圖…',
    es: 'Ejecutando el grafo en este fotograma…',
  },
  'Frame at {t} s': {
    ko: '{t}초 지점의 프레임', ja: '{t} 秒のフレーム',
    'zh-CN': '{t} 秒处的帧', 'zh-TW': '{t} 秒處的影格',
    es: 'Fotograma en {t} s',
  },
  'Back to the video': {
    ko: '비디오로 돌아가기', ja: '動画に戻る',
    'zh-CN': '返回视频', 'zh-TW': '返回影片',
    es: 'Volver al vídeo',
  },
  'That run is gone (newer runs replaced it). Run the graph again.': {
    ko: '그 실행 결과가 없습니다 (더 최근 실행으로 교체됨). 그래프를 다시 실행하세요.', ja: 'その実行結果はありません (新しい実行に置き換えられました)。グラフをもう一度実行してください。',
    'zh-CN': '该次运行的结果已不存在（已被更新的运行替换）。请重新运行图。', 'zh-TW': '該次執行的結果已不存在（已被較新的執行取代）。請重新執行圖。',
    es: 'Esa ejecución ya no existe (la reemplazaron otras más recientes). Ejecute el grafo de nuevo.',
  },
  'This dx_app build cannot write layers. Update dx_app to see them.': {
    ko: '이 dx_app 빌드는 레이어를 쓸 수 없습니다. 레이어를 보려면 dx_app을 업데이트하세요.', ja: 'この dx_app のビルドはレイヤーを書き出せません。表示するには dx_app を更新してください。',
    'zh-CN': '此 dx_app 版本无法输出图层。请更新 dx_app 后查看。', 'zh-TW': '此 dx_app 版本無法輸出圖層。請更新 dx_app 後查看。',
    es: 'Esta versión de dx_app no puede escribir capas. Actualice dx_app para verlas.',
  },
  'This frame could not be read: {why}': {
    ko: '이 프레임을 읽을 수 없습니다: {why}', ja: 'このフレームを読み取れませんでした: {why}',
    'zh-CN': '无法读取此帧：{why}', 'zh-TW': '無法讀取此影格：{why}',
    es: 'No se pudo leer este fotograma: {why}',
  },
  'Draw': {
    ko: '그리기', ja: '描画',
    'zh-CN': '绘制', 'zh-TW': '繪製',
    es: 'Dibujar',
  },
  'Only the checked nodes draw on the picture; every node still runs and raises its events.': {
    ko: '체크한 노드만 화면에 그립니다. 모든 노드는 그대로 실행되고 이벤트도 발생합니다.', ja: 'チェックしたノードだけが画面に描画されます。すべてのノードは実行され、イベントも発生します。',
    'zh-CN': '只有勾选的节点会绘制到画面上；所有节点仍会运行并产生事件。', 'zh-TW': '只有勾選的節點會繪製到畫面上；所有節點仍會執行並產生事件。',
    es: 'Solo los nodos marcados dibujan en la imagen; todos los nodos siguen ejecutándose y generando sus eventos.',
  },
  'Check at least one node to draw.': {
    ko: '그릴 노드를 하나 이상 체크하세요.', ja: '描画するノードを 1 つ以上チェックしてください。',
    'zh-CN': '请至少勾选一个要绘制的节点。', 'zh-TW': '請至少勾選一個要繪製的節點。',
    es: 'Marque al menos un nodo para dibujar.',
  },
  'The nodes to draw do not match the graph: {why}': {
    ko: '그릴 노드가 그래프와 맞지 않습니다: {why}', ja: '描画するノードがグラフと一致しません: {why}',
    'zh-CN': '要绘制的节点与图不符：{why}', 'zh-TW': '要繪製的節點與圖不符：{why}',
    es: 'Los nodos a dibujar no coinciden con el grafo: {why}',
  },
  'This dx_app build draws every node. Update dx_app to pick the nodes to draw.': {
    ko: '이 dx_app 빌드는 모든 노드를 그립니다. 그릴 노드를 고르려면 dx_app을 업데이트하세요.', ja: 'この dx_app のビルドはすべてのノードを描画します。描画するノードを選ぶには dx_app を更新してください。',
    'zh-CN': '此 dx_app 版本会绘制所有节点。请更新 dx_app 以选择要绘制的节点。', 'zh-TW': '此 dx_app 版本會繪製所有節點。請更新 dx_app 以選擇要繪製的節點。',
    es: 'Esta versión de dx_app dibuja todos los nodos. Actualice dx_app para elegir qué nodos dibujar.',
  },
  'Last values: {values}': {
    ko: '마지막 값: {values}', ja: '最後の値: {values}',
    'zh-CN': '最近的值：{values}', 'zh-TW': '最近的值：{values}',
    es: 'Últimos valores: {values}',
  },
  'more than {min}': {
    ko: '{min} 초과', ja: '{min} より大きい',
    'zh-CN': '大于 {min}', 'zh-TW': '大於 {min}',
    es: 'más de {min}',
  },
  'at most {max}': {
    ko: '{max} 이하', ja: '{max} 以下',
    'zh-CN': '最多 {max}', 'zh-TW': '最多 {max}',
    es: 'como máximo {max}',
  },
  '{n} points': {
    ko: '점 {n}개', ja: '点 {n} 個',
    'zh-CN': '{n} 个点', 'zh-TW': '{n} 個點',
    es: '{n} puntos',
  },
  'Not drawn yet': {
    ko: '아직 그리지 않았습니다', ja: 'まだ描かれていません',
    'zh-CN': '尚未绘制', 'zh-TW': '尚未繪製',
    es: 'Aún sin dibujar',
  },
  'per crop': {
    ko: 'crop마다', ja: 'クロップごと',
    'zh-CN': '每个裁剪', 'zh-TW': '每個裁切',
    es: 'por recorte',
  },
  'what it takes': {
    ko: '받은 것과 같은 종류', ja: '受け取ったものと同じ種類',
    'zh-CN': '与输入相同的类型', 'zh-TW': '與輸入相同的類型',
    es: 'lo mismo que recibe',
  },
  'This block needs track ids; the detector feeding it does not track.': {
    ko: '이 블록에는 track ID가 필요한데, 입력을 주는 detector가 추적하지 않습니다.', ja: 'このブロックにはトラック ID が必要ですが、入力元の検出器が追跡していません。',
    'zh-CN': '该块需要跟踪 ID，但为它提供输入的检测器没有开启跟踪。', 'zh-TW': '該區塊需要追蹤 ID，但為它提供輸入的偵測器沒有開啟追蹤。',
    es: 'Este bloque necesita ID de seguimiento; el detector que lo alimenta no hace seguimiento.',
  },
  'Redraw zone': {
    ko: '구역 다시 그리기', ja: 'ゾーンを描き直す',
    'zh-CN': '重新绘制区域', 'zh-TW': '重新繪製區域',
    es: 'Volver a dibujar la zona',
  },
  'Zone {node} added': {
    ko: '구역 {node}를 추가했습니다', ja: 'ゾーン {node} を追加しました',
    'zh-CN': '已添加区域 {node}', 'zh-TW': '已新增區域 {node}',
    es: 'Zona {node} añadida',
  },
  'Zone drawing. [ and ] pick a point, arrow keys move it, Insert adds a point, Delete removes it, PageUp and PageDown pick another shape, N adds a zone, F flips a line, Ctrl+Z undoes.': {
    ko: '구역 그리기. [ 와 ]로 점을 고르고, 화살표 키로 옮기며, Insert로 점을 추가하고 Delete로 지웁니다. PageUp/PageDown으로 다른 도형을 고르고, N은 구역 추가, F는 선 방향 뒤집기, Ctrl+Z는 되돌리기입니다.', ja: 'ゾーン描画。[ と ] で点を選び、矢印キーで移動、Insert で点を追加、Delete で削除します。PageUp/PageDown で別の図形を選び、N でゾーン追加、F でラインを反転、Ctrl+Z で元に戻します。',
    'zh-CN': '区域绘制。用 [ 和 ] 选点，方向键移动，Insert 添加点，Delete 删除点，PageUp/PageDown 选择其他图形，N 添加区域，F 翻转线，Ctrl+Z 撤销。', 'zh-TW': '區域繪製。用 [ 和 ] 選點，方向鍵移動，Insert 新增點，Delete 刪除點，PageUp/PageDown 選擇其他圖形，N 新增區域，F 翻轉線，Ctrl+Z 復原。',
    es: 'Dibujo de zonas. [ y ] eligen un punto, las flechas lo mueven, Insert añade un punto, Supr lo elimina, RePág y AvPág eligen otra forma, N añade una zona, F invierte una línea, Ctrl+Z deshace.',
  },
  'Shapes on this frame': {
    ko: '이 프레임의 도형', ja: 'このフレームの図形',
    'zh-CN': '此帧上的图形', 'zh-TW': '此影格上的圖形',
    es: 'Formas en este fotograma',
  },
  'Draw on the frame': {
    ko: '프레임 위에 그리기', ja: 'フレーム上に描く',
    'zh-CN': '在帧上绘制', 'zh-TW': '在影格上繪製',
    es: 'Dibujar sobre el fotograma',
  },
  'A camera or RTSP source has no still frame here; shapes are drawn on an empty 16:9 frame.': {
    ko: '카메라나 RTSP 소스는 여기서 정지 프레임을 보여 줄 수 없어, 빈 16:9 프레임 위에 도형을 그립니다.', ja: 'カメラや RTSP のソースはここで静止フレームを表示できないため、空の 16:9 フレームに図形を描きます。',
    'zh-CN': '摄像头或 RTSP 源在此无法显示静止帧，图形将画在空白的 16:9 帧上。', 'zh-TW': '攝影機或 RTSP 來源在此無法顯示靜止影格，圖形將畫在空白的 16:9 影格上。',
    es: 'Una cámara o una fuente RTSP no tiene aquí un fotograma fijo; las formas se dibujan sobre un fotograma vacío de 16:9.',
  },
  'The input frame could not be read; shapes are drawn on an empty 16:9 frame.': {
    ko: '입력 프레임을 읽지 못해 빈 16:9 프레임 위에 도형을 그립니다.', ja: '入力フレームを読み込めなかったため、空の 16:9 フレームに図形を描きます。',
    'zh-CN': '无法读取输入帧，图形将画在空白的 16:9 帧上。', 'zh-TW': '無法讀取輸入影格，圖形將畫在空白的 16:9 影格上。',
    es: 'No se pudo leer el fotograma de entrada; las formas se dibujan sobre un fotograma vacío de 16:9.',
  },
  /* ── Graph Composer: building a gallery for the gallery op from an image folder (POST /api/graph/gallery/build) ── */
  'Build gallery': {
    ko: 'Gallery 만들기', ja: 'ギャラリーを作成',
    'zh-CN': '构建图库', 'zh-TW': '建立圖庫',
    es: 'Crear galería',
  },
  'Build a gallery from an image folder': {
    ko: '이미지 폴더로 Gallery 만들기', ja: '画像フォルダーからギャラリーを作成',
    'zh-CN': '从图片文件夹构建图库', 'zh-TW': '從圖片資料夾建立圖庫',
    es: 'Crear una galería a partir de una carpeta de imágenes',
  },
  'Image folder': {
    ko: '이미지 폴더', ja: '画像フォルダー',
    'zh-CN': '图片文件夹', 'zh-TW': '圖片資料夾',
    es: 'Carpeta de imágenes',
  },
  'A folder under the dx_app, sample or outputs folders. One subfolder per person names its images after the subfolder; images directly in the folder are named after their files.': {
    ko: 'dx_app, sample, outputs 폴더 아래의 폴더입니다. 사람마다 하위 폴더를 하나씩 두면 그 이미지는 하위 폴더 이름을 갖고, 폴더에 바로 있는 이미지는 파일 이름을 갖습니다.', ja: 'dx_app・sample・outputs フォルダーの下のフォルダーです。人ごとにサブフォルダーを 1 つ置くと、その画像にはサブフォルダー名が付き、フォルダー直下の画像にはファイル名が付きます。',
    'zh-CN': 'dx_app、sample 或 outputs 文件夹下的文件夹。每人一个子文件夹时，其中的图片以子文件夹命名；直接放在该文件夹中的图片以文件名命名。', 'zh-TW': 'dx_app、sample 或 outputs 資料夾下的資料夾。每人一個子資料夾時，其中的圖片以子資料夾命名；直接放在該資料夾中的圖片以檔名命名。',
    es: 'Una carpeta dentro de las carpetas dx_app, sample u outputs. Con una subcarpeta por persona, sus imágenes llevan el nombre de la subcarpeta; las imágenes que están directamente en la carpeta llevan el nombre de su archivo.',
  },
  'Embedding model': {
    ko: 'Embedding 모델', ja: '埋め込みモデル',
    'zh-CN': '嵌入模型', 'zh-TW': '嵌入模型',
    es: 'Modelo de embeddings',
  },
  'Gallery name (optional)': {
    ko: 'Gallery 이름 (선택)', ja: 'ギャラリー名 (任意)',
    'zh-CN': '图库名称（可选）', 'zh-TW': '圖庫名稱（選填）',
    es: 'Nombre de la galería (opcional)',
  },
  'Building the gallery…': {
    ko: 'Gallery를 만드는 중…', ja: 'ギャラリーを作成中…',
    'zh-CN': '正在构建图库…', 'zh-TW': '正在建立圖庫…',
    es: 'Creando la galería…',
  },
  'Gallery built: {people} people, {images} images': {
    ko: 'Gallery를 만들었습니다: {people}명, 이미지 {images}장', ja: 'ギャラリーを作成しました: {people} 人、画像 {images} 枚',
    'zh-CN': '图库已构建：{people} 人，{images} 张图片', 'zh-TW': '圖庫已建立：{people} 人，{images} 張圖片',
    es: 'Galería creada: {people} personas, {images} imágenes',
  },
  'The gallery build failed.': {
    ko: 'Gallery를 만들지 못했습니다.', ja: 'ギャラリーを作成できませんでした。',
    'zh-CN': '图库构建失败。', 'zh-TW': '圖庫建立失敗。',
    es: 'No se pudo crear la galería.',
  },
  // error keys of the NPU job registry (npu_jobs.py) and the gallery builder (graph_gallery.py); the server message follows
  'gallery_busy': {
    ko: 'Gallery를 이미 만들고 있습니다', ja: 'ギャラリーをすでに作成中です',
    'zh-CN': '正在构建图库', 'zh-TW': '正在建立圖庫',
    es: 'Ya se está creando una galería',
  },
  'gallery_exists': {
    ko: '같은 이름의 Gallery가 이미 있습니다. 다른 이름을 입력하세요', ja: '同じ名前のギャラリーがすでにあります。別の名前を入力してください',
    'zh-CN': '已有同名图库，请输入其他名称', 'zh-TW': '已有同名圖庫，請輸入其他名稱',
    es: 'Ya existe una galería con ese nombre; escriba otro',
  },
  'gallery_outside_roots': {
    ko: 'Gallery 파일이 dx_app, sample, assets, outputs 폴더 밖에 있습니다', ja: 'ギャラリーファイルが dx_app・sample・assets・outputs フォルダーの外にあります',
    'zh-CN': '图库文件不在 dx_app、sample、assets、outputs 文件夹内', 'zh-TW': '圖庫檔案不在 dx_app、sample、assets、outputs 資料夾內',
    es: 'El archivo de la galería está fuera de las carpetas dx_app, sample, assets y outputs',
  },
  'graph_run_busy': {
    ko: '그래프 실행이 진행 중입니다. 끝날 때까지 기다리세요', ja: 'グラフの実行中です。終わるまでお待ちください',
    'zh-CN': '图正在运行，请等待其结束', 'zh-TW': '圖正在執行，請等待其結束',
    es: 'Hay una ejecución del grafo en curso; espere a que termine',
  },
  'live_busy': {
    ko: 'Run 페이지에서 Live 실행이 진행 중입니다. 먼저 그곳에서 멈추세요', ja: 'Run ページでライブ実行中です。先にそちらで停止してください',
    'zh-CN': 'Run 页面有实时运行在进行，请先在那里停止', 'zh-TW': 'Run 頁面有即時執行在進行，請先在那裡停止',
    es: 'La página Run tiene una ejecución en vivo; deténgala allí primero',
  },
  'invalid_folder': {
    ko: '폴더가 없거나 dx_app, sample, outputs 폴더 밖에 있습니다', ja: 'フォルダーが存在しないか、dx_app・sample・outputs フォルダーの外にあります',
    'zh-CN': '文件夹不存在，或不在 dx_app、sample、outputs 文件夹内', 'zh-TW': '資料夾不存在，或不在 dx_app、sample、outputs 資料夾內',
    es: 'La carpeta no existe o está fuera de las carpetas dx_app, sample y outputs',
  },
  'invalid_model': {
    ko: '모델 이름이 올바르지 않습니다', ja: 'モデル名が正しくありません',
    'zh-CN': '模型名称无效', 'zh-TW': '模型名稱無效',
    es: 'El nombre del modelo no es válido',
  },
  'invalid_name': {
    ko: 'Gallery 이름은 영문자, 숫자, _, ., - 로 64자 이내여야 합니다', ja: 'ギャラリー名は英数字と _ . - で 64 文字以内にしてください',
    'zh-CN': '图库名称只能使用字母、数字、_、.、-，最多 64 个字符', 'zh-TW': '圖庫名稱只能使用字母、數字、_、.、-，最多 64 個字元',
    es: 'El nombre de la galería admite letras, dígitos, _, . y -, hasta 64 caracteres',
  },
  'gallery_no_images': {
    ko: '폴더에 이미지가 없습니다', ja: 'フォルダーに画像がありません',
    'zh-CN': '文件夹中没有图片', 'zh-TW': '資料夾中沒有圖片',
    es: 'La carpeta no contiene imágenes',
  },
  'gallery_too_many_images': {
    ko: '폴더의 이미지가 너무 많습니다', ja: 'フォルダーの画像が多すぎます',
    'zh-CN': '文件夹中的图片太多', 'zh-TW': '資料夾中的圖片太多',
    es: 'La carpeta tiene demasiadas imágenes',
  },
  'model_missing': {
    ko: '모델이 설치되어 있지 않습니다. 먼저 Model Zoo에서 다운로드하세요', ja: 'モデルがインストールされていません。先に Model Zoo でダウンロードしてください',
    'zh-CN': '模型未安装，请先在 Model Zoo 中下载', 'zh-TW': '模型未安裝，請先在 Model Zoo 中下載',
    es: 'El modelo no está instalado; descárguelo primero en Model Zoo',
  },
  'gallery_script_missing': {
    ko: '이 dx_app에는 Gallery 생성 script가 없습니다', ja: 'この dx_app にはギャラリー作成スクリプトがありません',
    'zh-CN': '此 dx_app 中没有图库构建脚本', 'zh-TW': '此 dx_app 中沒有圖庫建立指令碼',
    es: 'Este dx_app no incluye el script para crear galerías',
  },
  'runtime_python_missing': {
    ko: 'DX-RT runtime Python (venv-dx-runtime)을 찾지 못했습니다', ja: 'DX-RT ランタイムの Python (venv-dx-runtime) が見つかりません',
    'zh-CN': '未找到 DX-RT 运行时 Python (venv-dx-runtime)', 'zh-TW': '找不到 DX-RT 執行環境的 Python (venv-dx-runtime)',
    es: 'No se encontró el Python del runtime de DX-RT (venv-dx-runtime)',
  },
  'gallery_build_failed': {
    ko: 'Gallery를 만들지 못했습니다', ja: 'ギャラリーを作成できませんでした',
    'zh-CN': '图库构建失败', 'zh-TW': '圖庫建立失敗',
    es: 'No se pudo crear la galería',
  },
  'gallery_timeout': {
    ko: 'Gallery 생성이 시간 제한을 넘어 중단되었습니다', ja: 'ギャラリーの作成が制限時間を超えたため停止しました',
    'zh-CN': '图库构建超时，已停止', 'zh-TW': '圖庫建立逾時，已停止',
    es: 'La creación de la galería superó el tiempo límite y se detuvo',
  },
  'gallery_stopped': {
    ko: 'Gallery 생성을 중단했습니다', ja: 'ギャラリーの作成を停止しました',
    'zh-CN': '图库构建已停止', 'zh-TW': '圖庫建立已停止',
    es: 'Se detuvo la creación de la galería',
  },
  'gallery_folder_too_large': {
    ko: '폴더에 파일과 폴더가 너무 많습니다. Gallery 이미지가 있는 폴더를 고르세요', ja: 'フォルダー内のファイルとフォルダーが多すぎます。ギャラリーの画像があるフォルダーを選んでください',
    'zh-CN': '文件夹中的文件和文件夹太多，请选择存放图库图片的文件夹', 'zh-TW': '資料夾中的檔案和資料夾太多，請選擇存放圖庫圖片的資料夾',
    es: 'La carpeta contiene demasiados archivos y carpetas; elija la carpeta con las imágenes de la galería',
  },
  // error keys of the NPU job registry (npu_jobs.py), the graph frame (graph_frame.py) and the Live streams (server.py)
  'npu_hold_lost': {
    ko: '준비하는 동안 다른 작업이 NPU를 사용하기 시작했습니다. 다시 시작하세요', ja: '準備中に別のジョブが NPU を使い始めました。もう一度開始してください',
    'zh-CN': '准备期间另一个任务占用了 NPU，请重新开始', 'zh-TW': '準備期間另一個工作佔用了 NPU，請重新開始',
    es: 'Otro trabajo tomó la NPU mientras este se preparaba; vuelva a iniciarlo',
  },
  'frame_too_large': {
    ko: '파일이 너무 커서 프레임을 표시할 수 없습니다', ja: 'ファイルが大きすぎるためフレームを表示できません',
    'zh-CN': '文件太大，无法显示帧', 'zh-TW': '檔案太大，無法顯示影格',
    es: 'El archivo es demasiado grande para mostrar el fotograma',
  },
  'too_many_viewers': {
    ko: '이 stream을 보는 탭이 너무 많습니다. 다른 탭을 닫으세요', ja: 'このストリームを表示しているタブが多すぎます。ほかのタブを閉じてください',
    'zh-CN': '查看此视频流的标签页过多，请关闭其他标签页', 'zh-TW': '檢視此串流的分頁過多，請關閉其他分頁',
    es: 'Demasiadas pestañas muestran esta transmisión; cierre otra',
  },
  'invalid_slot': {
    ko: '잘못된 Live 슬롯입니다', ja: '無効なライブスロットです',
    'zh-CN': '无效的实时运行插槽', 'zh-TW': '無效的即時執行插槽',
    es: 'Ranura de en vivo no válida',
  },
  // error keys of the graph run, frame and Live routes (graph_run.py, graph_frame.py, graph_live.py, graph_ops.py)
  'invalid_stream': {
    ko: 'stream은 그래프의 소스 중 하나여야 합니다', ja: 'ストリームはグラフのソースのいずれかである必要があります',
    'zh-CN': '视频流必须是图中的某个输入源', 'zh-TW': '串流必須是圖中的某個輸入來源',
    es: 'La transmisión debe ser una de las fuentes del grafo',
  },
  'no_source': {
    ko: '그래프에 소스가 없습니다', ja: 'グラフにソースがありません',
    'zh-CN': '图中没有输入源', 'zh-TW': '圖中沒有輸入來源',
    es: 'El grafo no tiene ninguna fuente',
  },
  'invalid_source_id': {
    ko: '소스 id는 영문자, 숫자, _, ., - 로 64자 이내여야 합니다', ja: 'ソース ID は英数字と _ . - で 64 文字以内にしてください',
    'zh-CN': '输入源 id 只能使用字母、数字、_、.、-，最多 64 个字符', 'zh-TW': '輸入來源 id 只能使用字母、數字、_、.、-，最多 64 個字元',
    es: 'El id de una fuente admite letras, dígitos, _, . y -, hasta 64 caracteres',
  },
  'invalid_live_input': {
    ko: '이 입력은 Live로 실행할 수 없습니다', ja: 'この入力はライブで実行できません',
    'zh-CN': '此输入无法实时运行', 'zh-TW': '此輸入無法即時執行',
    es: 'Esta entrada no se puede ejecutar en vivo',
  },
  'loop_unsupported': {
    ko: '이 dx_app 빌드는 비디오를 반복 재생할 수 없습니다. 카메라나 RTSP 스트림을 쓰세요', ja: 'この dx_app ビルドは動画をループ再生できません。カメラか RTSP ストリームを使ってください',
    'zh-CN': '此 dx_app 版本无法循环播放视频，请使用摄像头或 RTSP 流', 'zh-TW': '此 dx_app 版本無法循環播放影片，請使用攝影機或 RTSP 串流',
    es: 'Esta compilación de dx_app no puede repetir un vídeo; use una cámara o un stream RTSP',
  },
  'graph_live_failed': {
    ko: '그래프 Live를 시작하지 못했습니다', ja: 'グラフのライブを開始できませんでした',
    'zh-CN': '无法启动图的实时运行', 'zh-TW': '無法啟動圖的即時執行',
    es: 'No se pudo iniciar el grafo en vivo',
  },
  'frame_unreadable': {
    ko: '입력 프레임을 읽지 못했습니다', ja: '入力フレームを読み込めませんでした',
    'zh-CN': '无法读取输入帧', 'zh-TW': '無法讀取輸入影格',
    es: 'No se pudo leer el fotograma de entrada',
  },
  'list_ops_unsupported': {
    en: 'This dx_app build does not list its logic blocks (no --list-ops).',
    ko: '이 dx_app 빌드는 Logic 블록 목록을 제공하지 않습니다 (--list-ops 없음).', ja: 'この dx_app ビルドはロジックブロックの一覧を出せません (--list-ops なし)。',
    'zh-CN': '此 dx_app 版本无法列出逻辑块（没有 --list-ops）。', 'zh-TW': '此 dx_app 版本無法列出邏輯區塊（沒有 --list-ops）。',
    es: 'Esta compilación de dx_app no lista sus bloques lógicos (sin --list-ops).',
  },
  /* ─── Graph Composer Phase 3: export a C++ project ─── */
  'Export C++ project': {
    ko: 'C++ 프로젝트 내보내기', ja: 'C++ プロジェクトをエクスポート',
    'zh-CN': '导出 C++ 项目', 'zh-TW': '匯出 C++ 專案',
    es: 'Exportar proyecto C++',
  },
  'Project folder name': {
    ko: '프로젝트 폴더 이름', ja: 'プロジェクトフォルダー名',
    'zh-CN': '项目文件夹名称', 'zh-TW': '專案資料夾名稱',
    es: 'Nombre de la carpeta del proyecto',
  },
  'Letters, digits, _ and -, starting with a letter (at most 48).': {
    ko: '영문자, 숫자, _, - 사용, 영문자로 시작 (최대 48자).', ja: '英字・数字・_・- で、英字で始めます (48 文字まで)。',
    'zh-CN': '字母、数字、_ 和 -，以字母开头（最多 48 个字符）。', 'zh-TW': '字母、數字、_ 和 -，以字母開頭（最多 48 個字元）。',
    es: 'Letras, dígitos, _ y -, empezando por una letra (48 como máximo).',
  },
  'Include the model files ({size})': {
    ko: '모델 파일 포함 ({size})', ja: 'モデルファイルを含める ({size})',
    'zh-CN': '包含模型文件（{size}）', 'zh-TW': '包含模型檔案（{size}）',
    es: 'Incluir los archivos de modelo ({size})',
  },
  'Without them, setup.sh downloads the models from the DEEPX Model Zoo.': {
    ko: '포함하지 않으면 setup.sh가 DEEPX Model Zoo에서 모델을 내려받습니다.', ja: '含めない場合は、setup.sh が DEEPX Model Zoo からモデルをダウンロードします。',
    'zh-CN': '不包含时，setup.sh 会从 DEEPX Model Zoo 下载模型。', 'zh-TW': '不包含時，setup.sh 會從 DEEPX Model Zoo 下載模型。',
    es: 'Sin ellos, setup.sh descarga los modelos del DEEPX Model Zoo.',
  },
  'User logic stubs to fill in': {
    ko: '채워 넣을 사용자 Logic stub', ja: '中身を書くユーザーロジックのスタブ',
    'zh-CN': '待填写的用户逻辑桩', 'zh-TW': '待填寫的使用者邏輯樁',
    es: 'Esqueletos de lógica de usuario por completar',
  },
  'for node {nodes} (input: {kind})': {
    ko: '노드 {nodes}용 (입력: {kind})', ja: 'ノード {nodes} 用 (入力: {kind})',
    'zh-CN': '用于节点 {nodes}（输入：{kind}）', 'zh-TW': '用於節點 {nodes}（輸入：{kind}）',
    es: 'para el nodo {nodes} (entrada: {kind})',
  },
  'The project holds the graph, the engine with only these models, a main.cpp, setup.sh, run.sh and a README. It builds and runs anywhere the DEEPX runtime is installed.': {
    ko: '프로젝트에는 그래프, 이 모델들만 담은 엔진, main.cpp, setup.sh, run.sh, README가 들어 있습니다. DEEPX runtime이 설치된 곳이면 어디서든 빌드하고 실행합니다.',
    ja: 'プロジェクトにはグラフ、これらのモデルだけを含むエンジン、main.cpp、setup.sh、run.sh、README が入ります。DEEPX runtime がインストールされていればどこでもビルドして実行できます。',
    'zh-CN': '项目包含图、仅含这些模型的引擎、main.cpp、setup.sh、run.sh 和 README。只要安装了 DEEPX runtime，就能在任何地方构建并运行。',
    'zh-TW': '專案包含圖、僅含這些模型的引擎、main.cpp、setup.sh、run.sh 和 README。只要安裝了 DEEPX runtime，就能在任何地方建置並執行。',
    es: 'El proyecto contiene el grafo, el motor con solo estos modelos, un main.cpp, setup.sh, run.sh y un README. Se compila y ejecuta en cualquier equipo con el runtime de DEEPX.',
  },
  'Exporting…': {
    ko: '내보내는 중…', ja: 'エクスポート中…',
    'zh-CN': '正在导出…', 'zh-TW': '正在匯出…',
    es: 'Exportando…',
  },
  'Exported to {folder}': {
    ko: '{folder}에 내보냈습니다', ja: '{folder} にエクスポートしました',
    'zh-CN': '已导出到 {folder}', 'zh-TW': '已匯出到 {folder}',
    es: 'Exportado en {folder}',
  },
  'Download .zip ({size})': {
    ko: '.zip 내려받기 ({size})', ja: '.zip をダウンロード ({size})',
    'zh-CN': '下载 .zip（{size}）', 'zh-TW': '下載 .zip（{size}）',
    es: 'Descargar .zip ({size})',
  },
  'Build and run it:': {
    ko: '빌드하고 실행하기:', ja: 'ビルドして実行:',
    'zh-CN': '构建并运行：', 'zh-TW': '建置並執行：',
    es: 'Compílelo y ejecútelo:',
  },
  'This dx_app build cannot export projects. Update dx_app to use it.': {
    ko: '이 dx_app 빌드는 프로젝트를 내보낼 수 없습니다. 사용하려면 dx_app을 업데이트하세요.', ja: 'この dx_app ビルドはプロジェクトをエクスポートできません。使うには dx_app を更新してください。',
    'zh-CN': '此 dx_app 版本无法导出项目。请更新 dx_app 后使用。', 'zh-TW': '此 dx_app 版本無法匯出專案。請更新 dx_app 後使用。',
    es: 'Esta compilación de dx_app no puede exportar proyectos. Actualice dx_app para usarlo.',
  },
  'Not enough disk space: the export needs {need} and {free} is free.': {
    ko: '디스크 공간이 부족합니다: 내보내기에 {need}가 필요한데 {free}만 남아 있습니다.', ja: 'ディスクの空きが足りません: エクスポートには {need} 必要ですが、空きは {free} です。',
    'zh-CN': '磁盘空间不足：导出需要 {need}，但只剩 {free}。', 'zh-TW': '磁碟空間不足：匯出需要 {need}，但只剩 {free}。',
    es: 'No hay espacio en disco suficiente: la exportación necesita {need} y quedan {free} libres.',
  },
  'The export failed.': {
    ko: '내보내기에 실패했습니다.', ja: 'エクスポートに失敗しました。',
    'zh-CN': '导出失败。', 'zh-TW': '匯出失敗。',
    es: 'La exportación falló.',
  },
  'Reading what the export will hold…': {
    ko: '내보낼 내용을 확인하는 중…', ja: 'エクスポートの内容を確認しています…',
    'zh-CN': '正在读取导出内容…', 'zh-TW': '正在讀取匯出內容…',
    es: 'Leyendo lo que contendrá la exportación…',
  },
  'No User logic block: the project runs the graph as it is.': {
    ko: '사용자 Logic 블록이 없습니다: 프로젝트는 그래프를 그대로 실행합니다.', ja: 'ユーザーロジックブロックはありません: プロジェクトはグラフをそのまま実行します。',
    'zh-CN': '没有用户逻辑块：项目按原样运行图。', 'zh-TW': '沒有使用者邏輯區塊：專案按原樣執行圖。',
    es: 'Sin bloque de lógica de usuario: el proyecto ejecuta el grafo tal cual.',
  },
  'Export needs a graph without problems and a dx_app that can export projects.': {
    ko: '내보내려면 문제가 없는 그래프와 프로젝트를 내보낼 수 있는 dx_app이 필요합니다.', ja: 'エクスポートには、問題のないグラフと、プロジェクトをエクスポートできる dx_app が必要です。',
    'zh-CN': '导出需要一个没有问题的图，以及能导出项目的 dx_app。', 'zh-TW': '匯出需要一個沒有問題的圖，以及能匯出專案的 dx_app。',
    es: 'Para exportar hace falta un grafo sin problemas y un dx_app que pueda exportar proyectos.',
  },
  'Close': {
    ko: '닫기', ja: '閉じる',
    'zh-CN': '关闭', 'zh-TW': '關閉',
    es: 'Cerrar',
  },
  'Inputs': {
    ko: '입력', ja: '入力',
    'zh-CN': '输入', 'zh-TW': '輸入',
    es: 'Entradas',
  },
  'for source {source}': {
    ko: '소스 {source}용', ja: 'ソース {source} 用',
    'zh-CN': '用于来源 {source}', 'zh-TW': '用於來源 {source}',
    es: 'para la fuente {source}',
  },
  'no input: give one with --input': {
    ko: '입력 없음: --input 으로 지정하세요', ja: '入力なし: --input で指定してください',
    'zh-CN': '无输入：请用 --input 指定', 'zh-TW': '無輸入：請用 --input 指定',
    es: 'sin entrada: indíquela con --input',
  },
  'An uploaded image is not exported: a source uses the sample picked for it, else its own input.': {
    ko: '업로드한 이미지는 내보내지 않습니다: 소스는 선택한 샘플을, 없으면 자신의 입력을 사용합니다.',
    ja: 'アップロードした画像はエクスポートしません: ソースは選んだサンプルを、なければ自身の入力を使います。',
    'zh-CN': '上传的图片不会导出：来源使用为其选择的样例，否则使用其自身的输入。',
    'zh-TW': '上傳的圖片不會匯出：來源使用為其選擇的範例，否則使用其自身的輸入。',
    es: 'Una imagen subida no se exporta: una fuente usa la muestra elegida para ella o, si no, su propia entrada.',
  },
  'Every model must be installed to include the files.': {
    ko: '모델 파일을 포함하려면 모든 모델이 설치되어 있어야 합니다.', ja: 'ファイルを含めるには、すべてのモデルがインストールされている必要があります。',
    'zh-CN': '要包含文件，所有模型都必须已安装。', 'zh-TW': '要包含檔案，所有模型都必須已安裝。',
    es: 'Para incluir los archivos, todos los modelos deben estar instalados.',
  },
  'export_busy': {
    en: 'Another export is running; wait for it.',
    ko: '다른 내보내기가 진행 중입니다. 끝날 때까지 기다리세요.', ja: '別のエクスポートが実行中です。終わるまでお待ちください。',
    'zh-CN': '另一个导出正在进行，请等待其完成。', 'zh-TW': '另一個匯出正在進行，請等待其完成。',
    es: 'Hay otra exportación en curso; espere a que termine.',
  },
  'export_name_invalid': {
    en: 'The folder name must be 1 to 48 letters, digits, _ or -, starting with a letter.',
    ko: '폴더 이름은 영문자, 숫자, _, - 로 1~48자이고 영문자로 시작해야 합니다.', ja: 'フォルダー名は英字・数字・_・- の 1〜48 文字で、英字で始める必要があります。',
    'zh-CN': '文件夹名称须为 1 到 48 个字母、数字、_ 或 -，并以字母开头。', 'zh-TW': '資料夾名稱須為 1 到 48 個字母、數字、_ 或 -，並以字母開頭。',
    es: 'El nombre de la carpeta debe tener de 1 a 48 letras, dígitos, _ o -, y empezar por una letra.',
  },
  'export_failed': {
    en: 'The export failed.',
    ko: '내보내기에 실패했습니다.', ja: 'エクスポートに失敗しました。',
    'zh-CN': '导出失败。', 'zh-TW': '匯出失敗。',
    es: 'La exportación falló.',
  },
  'model_file_missing': {
    en: 'A model file is not installed here. Export without the model files, or download the model first.',
    ko: '모델 파일이 이 컴퓨터에 설치되어 있지 않습니다. 모델 파일 없이 내보내거나 먼저 모델을 내려받으세요.', ja: 'モデルファイルがこのコンピューターにインストールされていません。モデルファイルなしでエクスポートするか、先にモデルをダウンロードしてください。',
    'zh-CN': '此计算机上未安装模型文件。请不含模型文件导出，或先下载模型。', 'zh-TW': '此電腦上未安裝模型檔案。請不含模型檔案匯出，或先下載模型。',
    es: 'Un archivo de modelo no está instalado aquí. Exporte sin los archivos de modelo o descargue antes el modelo.',
  },
  'model_unknown': {
    en: 'The graph names a model this dx_app does not know.',
    ko: '그래프에 이 dx_app이 모르는 모델이 있습니다.', ja: 'グラフにこの dx_app が知らないモデルがあります。',
    'zh-CN': '图中有此 dx_app 不认识的模型。', 'zh-TW': '圖中有此 dx_app 不認識的模型。',
    es: 'El grafo nombra un modelo que este dx_app no conoce.',
  },
  'model_not_ready': {
    en: 'A model of the graph cannot run in a graph yet.',
    ko: '그래프의 모델 중 아직 그래프에서 실행할 수 없는 모델이 있습니다.', ja: 'グラフのモデルに、まだグラフで実行できないものがあります。',
    'zh-CN': '图中有模型尚不能在图中运行。', 'zh-TW': '圖中有模型尚不能在圖中執行。',
    es: 'Un modelo del grafo aún no puede ejecutarse en un grafo.',
  },
  'user_name_invalid': {
    en: 'A User logic block\'s name must be a C++ name: letters, digits and _, not starting with a digit, not a C++ keyword.',
    ko: '사용자 Logic 블록의 이름은 C++ 이름이어야 합니다: 영문자, 숫자, _ 로 쓰고, 숫자로 시작하지 않으며, C++ keyword가 아니어야 합니다.', ja: 'ユーザーロジックブロックの名前は C++ の名前にしてください: 英字・数字・_ で、数字で始まらず、C++ のキーワードでないこと。',
    'zh-CN': '用户逻辑块的名称必须是 C++ 名称：字母、数字和 _，不以数字开头，且不是 C++ 关键字。', 'zh-TW': '使用者邏輯區塊的名稱必須是 C++ 名稱：字母、數字和 _，不以數字開頭，且不是 C++ 關鍵字。',
    es: 'El nombre de un bloque de lógica de usuario debe ser un nombre de C++: letras, dígitos y _, sin empezar por un dígito y sin ser una palabra clave de C++.',
  },
  'user_kind_invalid': {
    en: 'A User logic block\'s input and output must name one kind of data.',
    ko: '사용자 Logic 블록의 입력과 출력은 같은 데이터 종류여야 합니다.', ja: 'ユーザーロジックブロックの入力と出力は同じ種類のデータにしてください。',
    'zh-CN': '用户逻辑块的输入和输出必须是同一种数据。', 'zh-TW': '使用者邏輯區塊的輸入和輸出必須是同一種資料。',
    es: 'La entrada y la salida de un bloque de lógica de usuario deben ser del mismo tipo de datos.',
  },
  'user_kind_conflict': {
    en: 'Two User logic blocks share a name but take different kinds of data.',
    ko: '두 사용자 Logic 블록이 같은 이름을 쓰지만 서로 다른 데이터 종류를 받습니다.', ja: '2 つのユーザーロジックブロックが同じ名前なのに、異なる種類のデータを受け取ります。',
    'zh-CN': '两个用户逻辑块同名，但接收的数据类型不同。', 'zh-TW': '兩個使用者邏輯區塊同名，但接收的資料類型不同。',
    es: 'Dos bloques de lógica de usuario comparten nombre pero reciben tipos de datos distintos.',
  },
  'input_missing': {
    en: 'An input file of the graph does not exist.',
    ko: '그래프의 입력 파일이 없습니다.', ja: 'グラフの入力ファイルがありません。',
    'zh-CN': '图的输入文件不存在。', 'zh-TW': '圖的輸入檔案不存在。',
    es: 'Un archivo de entrada del grafo no existe.',
  },
  'gallery_missing': {
    en: 'A gallery file of the graph does not exist.',
    ko: '그래프의 Gallery 파일이 없습니다.', ja: 'グラフのギャラリーファイルがありません。',
    'zh-CN': '图的图库文件不存在。', 'zh-TW': '圖的圖庫檔案不存在。',
    es: 'Un archivo de galería del grafo no existe.',
  },
  'graph_unreadable': {
    en: 'The graph could not be read.',
    ko: '그래프를 읽을 수 없습니다.', ja: 'グラフを読み込めませんでした。',
    'zh-CN': '无法读取该图。', 'zh-TW': '無法讀取該圖。',
    es: 'No se pudo leer el grafo.',
  },
  'invalid_input': {
    en: 'An input is not an image or a video under the dx_app, sample, assets or outputs folders.',
    ko: '입력이 dx_app, sample, assets, outputs 폴더 안의 이미지나 비디오가 아닙니다.', ja: '入力が dx_app・sample・assets・outputs フォルダー内の画像や動画ではありません。',
    'zh-CN': '输入不是 dx_app、sample、assets 或 outputs 文件夹中的图片或视频。', 'zh-TW': '輸入不是 dx_app、sample、assets 或 outputs 資料夾中的圖片或影片。',
    es: 'Una entrada no es una imagen ni un vídeo de las carpetas dx_app, sample, assets u outputs.',
  },
  'path_leak': {
    en: 'The exported project would name a path of this computer\'s DEEPX SDK; the export was stopped.',
    ko: '내보낸 프로젝트에 이 컴퓨터의 DEEPX SDK 경로가 들어가게 되어 내보내기를 멈췄습니다.', ja: 'エクスポートしたプロジェクトにこのコンピューターの DEEPX SDK のパスが入るため、エクスポートを止めました。',
    'zh-CN': '导出的项目会包含此计算机上 DEEPX SDK 的路径，导出已停止。', 'zh-TW': '匯出的專案會包含此電腦上 DEEPX SDK 的路徑，匯出已停止。',
    es: 'El proyecto exportado nombraría una ruta del DEEPX SDK de este equipo; la exportación se detuvo.',
  },
  'unknown_job': {
    en: 'This run is no longer known to the server; it ended or the server restarted.',
    ko: '서버가 이 실행을 더 이상 알지 못합니다. 끝났거나 서버가 다시 시작되었습니다.', ja: 'サーバーはこの実行をもう把握していません。終了したか、サーバーが再起動しました。',
    'zh-CN': '服务器已不再记录此次运行：它已结束，或服务器已重启。', 'zh-TW': '伺服器已不再記錄此次執行：它已結束，或伺服器已重新啟動。',
    es: 'El servidor ya no conoce esta ejecución; terminó o el servidor se reinició.',
  },
  /* Graph Composer templates (graph-palette.js TEMPLATE_TEXT): a scenario name and what it decides. */
  'Restricted-zone intrusion': {
    ko: '출입 금지 구역 침입', ja: '立入禁止ゾーンへの侵入',
    'zh-CN': '禁区闯入', 'zh-TW': '禁區闖入',
    es: 'Intrusión en zona restringida',
  },
  'An event when a person enters the zone': {
    ko: '사람이 구역에 들어오면 이벤트', ja: '人がゾーンに入るとイベント',
    'zh-CN': '有人进入区域时触发事件', 'zh-TW': '有人進入區域時觸發事件',
    es: 'Un evento cuando una persona entra en la zona',
  },
  'Line counting': {
    ko: '선 통과 계수', ja: 'ライン通過カウント',
    'zh-CN': '越线计数', 'zh-TW': '越線計數',
    es: 'Conteo por línea',
  },
  'People crossing a line, counted per direction': {
    ko: '선을 지나는 사람을 방향별로 계수', ja: 'ラインを通過した人を方向別にカウント',
    'zh-CN': '按方向统计越线的人', 'zh-TW': '依方向統計越線的人',
    es: 'Personas que cruzan una línea, contadas por sentido',
  },
  'PPE check': {
    ko: '보호구 확인', ja: '保護具チェック',
    'zh-CN': '防护装备检查', 'zh-TW': '防護裝備檢查',
    es: 'Comprobación de EPI',
  },
  'An event for a person in the zone without a hat': {
    ko: '구역 안에 모자를 쓰지 않은 사람이 있으면 이벤트', ja: 'ゾーン内に帽子をかぶっていない人がいるとイベント',
    'zh-CN': '区域内有人未戴帽子时触发事件', 'zh-TW': '區域內有人未戴帽子時觸發事件',
    es: 'Un evento cuando hay una persona sin sombrero en la zona',
  },
  'Loitering': {
    ko: '배회 감지', ja: 'うろつき検知',
    'zh-CN': '徘徊检测', 'zh-TW': '徘徊偵測',
    es: 'Merodeo',
  },
  'An event when a person stays in the zone over 5 s': {
    ko: '사람이 구역에 5초 넘게 머물면 이벤트', ja: '人がゾーンに 5 秒を超えてとどまるとイベント',
    'zh-CN': '有人在区域内停留超过 5 秒时触发事件', 'zh-TW': '有人在區域內停留超過 5 秒時觸發事件',
    es: 'Un evento cuando una persona permanece más de 5 s en la zona',
  },
  'People count per zone': {
    ko: '구역별 인원 계수', ja: 'ゾーンごとの人数カウント',
    'zh-CN': '分区人数统计', 'zh-TW': '分區人數統計',
    es: 'Conteo de personas por zona',
  },
  'People counted in two zones': {
    ko: '두 구역의 인원을 계수', ja: '2 つのゾーンの人数をカウント',
    'zh-CN': '统计两个区域中的人数', 'zh-TW': '統計兩個區域中的人數',
    es: 'Personas contadas en dos zonas',
  },
  'Known person': {
    ko: '등록된 인물 확인', ja: '登録済み人物の確認',
    'zh-CN': '已登记人员识别', 'zh-TW': '已登記人員辨識',
    es: 'Persona conocida',
  },
  'Each person named after the closest Gallery entry, or unknown': {
    ko: '사람마다 가장 가까운 Gallery 항목의 이름, 없으면 unknown', ja: '各人に最も近いギャラリー項目の名前、なければ unknown',
    'zh-CN': '为每个人标注最接近的图库条目名称，没有则为 unknown', 'zh-TW': '為每個人標註最接近的圖庫項目名稱，沒有則為 unknown',
    es: 'Cada persona recibe el nombre de la entrada de galería más cercana, o unknown',
  },
  'Driver attention': {
    ko: '운전자 주의 상태', ja: 'ドライバーの注意状態',
    'zh-CN': '驾驶员注意力', 'zh-TW': '駕駛注意力',
    es: 'Atención del conductor',
  },
  'Events when the driver turns the head away or down': {
    ko: '운전자가 고개를 돌리거나 숙이면 이벤트', ja: 'ドライバーが顔をそらしたり下を向いたりするとイベント',
    'zh-CN': '驾驶员转头或低头时触发事件', 'zh-TW': '駕駛轉頭或低頭時觸發事件',
    es: 'Eventos cuando el conductor gira o baja la cabeza',
  },
  'Multi-camera people count': {
    ko: '여러 카메라 인원 계수', ja: '複数カメラの人数カウント',
    'zh-CN': '多摄像头人数统计', 'zh-TW': '多攝影機人數統計',
    es: 'Conteo de personas con varias cámaras',
  },
  'People counted per camera; an event when one is crowded': {
    ko: '카메라마다 인원을 계수하고, 붐비면 이벤트', ja: 'カメラごとに人数をカウントし、混雑するとイベント',
    'zh-CN': '按摄像头统计人数，拥挤时触发事件', 'zh-TW': '依攝影機統計人數，擁擠時觸發事件',
    es: 'Personas contadas por cámara; un evento cuando una escena se llena de gente',
  },
  /* Graph Composer engine examples and the volume alert template (graph-palette.js TEMPLATE_TEXT). */
  'Logistics volume alert': {
    ko: '물류 부피 경보', ja: '物流の体積アラート',
    'zh-CN': '物流体积警报', 'zh-TW': '物流體積警報',
    es: 'Alerta de volumen logístico',
  },
  'An event when the estimated volume of packages passes a limit': {
    ko: '화물의 추정 부피가 기준을 넘으면 이벤트', ja: '荷物の推定体積が上限を超えるとイベント',
    'zh-CN': '包裹估算体积超过上限时触发事件', 'zh-TW': '包裹估算體積超過上限時觸發事件',
    es: 'Un evento cuando el volumen estimado de los paquetes supera un límite',
  },
  'Detection, segmentation and pose': {
    ko: '검출·분할·자세', ja: '検出・セグメンテーション・姿勢',
    'zh-CN': '检测、分割与姿态', 'zh-TW': '偵測、分割與姿態',
    es: 'Detección, segmentación y pose',
  },
  'Three models on one frame, drawn together': {
    ko: '한 프레임에 모델 세 개를 실행해 함께 그림', ja: '1 フレームに 3 つのモデルを実行して重ねて描画',
    'zh-CN': '在同一帧上运行三个模型并一起绘制', 'zh-TW': '在同一影格上執行三個模型並一起繪製',
    es: 'Tres modelos sobre un fotograma, dibujados juntos',
  },
  'Detection, segmentation and depth': {
    ko: '검출·분할·깊이', ja: '検出・セグメンテーション・深度',
    'zh-CN': '检测、分割与深度', 'zh-TW': '偵測、分割與深度',
    es: 'Detección, segmentación y profundidad',
  },
  'Three models on one frame, with depth instead of pose': {
    ko: '자세 대신 깊이를 쓰는 모델 세 개를 한 프레임에 실행', ja: '姿勢の代わりに深度を使う 3 つのモデルを 1 フレームで実行',
    'zh-CN': '在同一帧上运行三个模型，用深度代替姿态', 'zh-TW': '在同一影格上執行三個模型，以深度取代姿態',
    es: 'Tres modelos sobre un fotograma, con profundidad en lugar de pose',
  },
  'Person re-identification': {
    ko: '인물 재식별', ja: '人物の再識別',
    'zh-CN': '行人重识别', 'zh-TW': '行人重新辨識',
    es: 'Reidentificación de personas',
  },
  'Each tracked person cropped for a ReID embedding': {
    ko: '추적한 사람마다 잘라 ReID embedding 계산', ja: '追跡した人物ごとに切り出して ReID 埋め込みを計算',
    'zh-CN': '裁剪每个被跟踪的人并计算 ReID 嵌入', 'zh-TW': '裁切每個被追蹤的人並計算 ReID 嵌入',
    es: 'Cada persona seguida se recorta para un embedding ReID',
  },
  'Person attributes': {
    ko: '인물 속성', ja: '人物の属性',
    'zh-CN': '行人属性', 'zh-TW': '行人屬性',
    es: 'Atributos de personas',
  },
  'Each person cropped for attribute recognition': {
    ko: '사람마다 잘라 속성 인식', ja: '人物ごとに切り出して属性を認識',
    'zh-CN': '裁剪每个人并识别属性', 'zh-TW': '裁切每個人並辨識屬性',
    es: 'Cada persona se recorta para reconocer sus atributos',
  },
  'Rotated objects classified': {
    ko: '회전된 물체 분류', ja: '回転した物体の分類',
    'zh-CN': '旋转目标分类', 'zh-TW': '旋轉目標分類',
    es: 'Objetos girados clasificados',
  },
  'Oriented boxes straightened, then classified': {
    ko: '회전 박스를 바로 세운 뒤 분류', ja: '回転ボックスをまっすぐにしてから分類',
    'zh-CN': '把旋转框摆正后再分类', 'zh-TW': '把旋轉框擺正後再分類',
    es: 'Las cajas orientadas se enderezan y luego se clasifican',
  },
  'Denoise, then detect': {
    ko: '잡음 제거 후 검출', ja: 'ノイズ除去してから検出',
    'zh-CN': '先去噪再检测', 'zh-TW': '先去噪再偵測',
    es: 'Eliminar ruido y detectar',
  },
  'Detection on the denoised image': {
    ko: '잡음을 없앤 이미지에서 검출', ja: 'ノイズを除去した画像で検出',
    'zh-CN': '在去噪后的图像上检测', 'zh-TW': '在去噪後的影像上偵測',
    es: 'Detección sobre la imagen sin ruido',
  },
  'Super-resolution, detect, classify': {
    ko: '초해상도 후 검출과 분류', ja: '超解像のあと検出と分類',
    'zh-CN': '超分辨率后检测与分类', 'zh-TW': '超解析度後偵測與分類',
    es: 'Superresolución, detectar y clasificar',
  },
  'Detection and classification on a 2x image; too large for DX-M1': {
    ko: '2배 이미지에서 검출하고 분류. DX-M1에는 너무 큼', ja: '2 倍の画像で検出と分類。DX-M1 には大きすぎる',
    'zh-CN': '在 2 倍图像上检测和分类；对 DX-M1 来说太大', 'zh-TW': '在 2 倍影像上偵測和分類；對 DX-M1 來說太大',
    es: 'Detección y clasificación sobre una imagen 2x; demasiado grande para DX-M1',
  },
  'Two cameras, one ReID': {
    ko: '카메라 두 대, ReID 하나', ja: '2 台のカメラ、1 つの ReID',
    'zh-CN': '两路摄像头，一个 ReID', 'zh-TW': '兩路攝影機，一個 ReID',
    es: 'Dos cámaras, un ReID',
  },
  'Two sources share one tracked detector and one ReID model': {
    ko: '두 소스가 추적 detector 하나와 ReID 모델 하나를 함께 사용', ja: '2 つのソースが追跡付き検出器 1 つと ReID モデル 1 つを共有',
    'zh-CN': '两个源共用一个带跟踪的检测器和一个 ReID 模型', 'zh-TW': '兩個來源共用一個附追蹤的偵測器和一個 ReID 模型',
    es: 'Dos fuentes comparten un detector con seguimiento y un modelo ReID',
  },
  'Super-resolution, detect, pose': {
    ko: '초해상도 후 검출과 자세', ja: '超解像のあと検出と姿勢',
    'zh-CN': '超分辨率后检测与姿态', 'zh-TW': '超解析度後偵測與姿態',
    es: 'Superresolución, detectar y pose',
  },
  'Top-down pose on a 2x image; too large for DX-M1': {
    ko: '2배 이미지에서 사람마다 자세 추정. DX-M1에는 너무 큼', ja: '2 倍の画像で人物ごとに姿勢推定。DX-M1 には大きすぎる',
    'zh-CN': '在 2 倍图像上逐人估计姿态；对 DX-M1 来说太大', 'zh-TW': '在 2 倍影像上逐人估計姿態；對 DX-M1 來說太大',
    es: 'Pose por persona sobre una imagen 2x; demasiado grande para DX-M1',
  },
  'Low-light detection, pose and ReID': {
    ko: '저조도 검출·자세·ReID', ja: '低照度での検出・姿勢・ReID',
    'zh-CN': '低光照检测、姿态与 ReID', 'zh-TW': '低光照偵測、姿態與 ReID',
    es: 'Detección, pose y ReID con poca luz',
  },
  'Low-light enhancement, then a pose and an embedding per person': {
    ko: '저조도 보정 후 사람마다 자세와 embedding', ja: '低照度補正のあと人物ごとに姿勢と埋め込み',
    'zh-CN': '低光照增强后，逐人估计姿态并计算嵌入', 'zh-TW': '低光照增強後，逐人估計姿態並計算嵌入',
    es: 'Mejora de poca luz y después una pose y un embedding por persona',
  },
  'Hand landmarks': {
    ko: '손 landmark', ja: '手のランドマーク',
    'zh-CN': '手部关键点', 'zh-TW': '手部關鍵點',
    es: 'Puntos de la mano',
  },
  'Palm detection, then 21 landmarks per hand': {
    ko: '손바닥 검출 후 손마다 landmark 21개', ja: '手のひらを検出して手ごとに 21 点のランドマーク',
    'zh-CN': '先检测手掌，再为每只手求 21 个关键点', 'zh-TW': '先偵測手掌，再為每隻手求 21 個關鍵點',
    es: 'Detección de palmas y luego 21 puntos por mano',
  },
  'Driver head pose': {
    ko: '운전자 머리 자세', ja: 'ドライバーの頭部姿勢',
    'zh-CN': '驾驶员头部姿态', 'zh-TW': '駕駛頭部姿態',
    es: 'Pose de la cabeza del conductor',
  },
  'Face detection, then pitch, yaw and roll': {
    ko: '얼굴 검출 후 pitch, yaw, roll', ja: '顔を検出して pitch・yaw・roll',
    'zh-CN': '检测人脸后求 pitch、yaw、roll', 'zh-TW': '偵測人臉後求 pitch、yaw、roll',
    es: 'Detección de caras y luego pitch, yaw y roll',
  },
  'Package volume': {
    ko: '화물 부피', ja: '荷物の体積',
    'zh-CN': '包裹体积', 'zh-TW': '包裹體積',
    es: 'Volumen de paquetes',
  },
  'Detection, masks and depth give a volume estimate per package': {
    ko: '검출, mask, 깊이로 화물마다 부피 추정', ja: '検出・マスク・深度から荷物ごとの体積を推定',
    'zh-CN': '由检测、掩码和深度估算每件包裹的体积', 'zh-TW': '由偵測、遮罩和深度估算每件包裹的體積',
    es: 'Detección, máscaras y profundidad dan un volumen estimado por paquete',
  },
};

/* ─── Graph Composer logic blocks: Studio's translations of dx_app's --list-ops texts ───
   dx_app writes an op's summary and its params' help in English only. Per op: the summary, and per param a
   label and the help, in six languages. `en` is dx_app's own text: graph-inspector.js uses an entry only while
   it matches what the dx_app build gives, so a reworded or unknown op shows dx_app's text instead. */
window._DX_GRAPH_OPS_I18N = {
  filter: {
    summary: { en: "keeps the boxes of the listed classes with at least a score and an area", ko: "나열한 클래스의 박스 중 점수와 면적이 기준 이상인 박스만 남깁니다", ja: "指定したクラスのうち、スコアと面積が基準以上のボックスだけを残します", "zh-CN": "只保留所列类别中分数和面积达到下限的框", "zh-TW": "只保留所列類別中分數和面積達到下限的框", es: "conserva las cajas de las clases indicadas con al menos una puntuación y un área" },
    params: {
      classes: {
        label: { en: "Classes", ko: "클래스", ja: "クラス", "zh-CN": "类别", "zh-TW": "類別", es: "Clases" },
        help: { en: "class names to keep, as the detector names them; leave it out to keep every class", ko: "남길 클래스 이름 (detector가 쓰는 이름 그대로). 비워 두면 모든 클래스를 남깁니다", ja: "残すクラス名 (検出器が使う名前のまま)。空にするとすべてのクラスを残します", "zh-CN": "要保留的类别名称（与检测器使用的名称一致）；留空则保留所有类别", "zh-TW": "要保留的類別名稱（與偵測器使用的名稱一致）；留空則保留所有類別", es: "nombres de las clases que se conservan, tal como los nombra el detector; vacío conserva todas" }
      },
      min_score: {
        label: { en: "Minimum score", ko: "최소 점수", ja: "最小スコア", "zh-CN": "最低分数", "zh-TW": "最低分數", es: "Puntuación mínima" },
        help: { en: "the smallest confidence kept (0.5, not 50)", ko: "남길 최소 신뢰도 (50이 아니라 0.5)", ja: "残す最小の信頼度 (50 ではなく 0.5)", "zh-CN": "保留的最低置信度（写 0.5，而不是 50）", "zh-TW": "保留的最低置信度（寫 0.5，而不是 50）", es: "la confianza mínima que se conserva (0.5, no 50)" }
      },
      min_area: {
        label: { en: "Minimum area", ko: "최소 면적", ja: "最小面積", "zh-CN": "最小面积", "zh-TW": "最小面積", es: "Área mínima" },
        help: { en: "the smallest box area kept, in source-frame pixels", ko: "남길 최소 박스 면적 (원본 프레임의 픽셀 단위)", ja: "残す最小のボックス面積 (元フレームのピクセル単位)", "zh-CN": "保留的最小框面积，单位为原始帧的像素", "zh-TW": "保留的最小框面積，單位為原始影格的像素", es: "el área mínima de caja que se conserva, en píxeles del fotograma de origen" }
      }
    }
  },
  zone: {
    summary: { en: "keeps the boxes whose anchor point is inside (or outside) a polygon; with track ids, an event when a box enters or leaves", ko: "기준점이 다각형 안 (또는 밖)에 있는 박스를 남깁니다. track ID가 있으면 박스가 들어오거나 나갈 때 이벤트를 냅니다", ja: "基準点が多角形の内側 (または外側) にあるボックスを残します。トラック ID があれば、ボックスが入る・出るときにイベントを出します", "zh-CN": "保留基准点位于多边形内（或外）的框；有跟踪 ID 时，框进入或离开都会触发事件", "zh-TW": "保留基準點位於多邊形內（或外）的框；有追蹤 ID 時，框進入或離開都會觸發事件", es: "conserva las cajas cuyo punto de anclaje está dentro (o fuera) de un polígono; con ID de seguimiento, un evento cuando una caja entra o sale" },
    params: {
      polygon: {
        label: { en: "Polygon", ko: "다각형", ja: "多角形", "zh-CN": "多边形", "zh-TW": "多邊形", es: "Polígono" },
        help: { en: "x0, y0, x1, y1, ...: at least 3 points, each a fraction 0..1 of the frame's width and height", ko: "x0, y0, x1, y1, ...: 점 3개 이상, 각 좌표는 프레임 너비·높이에 대한 0..1 비율", ja: "x0, y0, x1, y1, ...: 3 点以上。各座標はフレームの幅・高さに対する 0..1 の割合", "zh-CN": "x0, y0, x1, y1, ...：至少 3 个点，每个坐标是相对帧宽度和高度的 0..1 比例", "zh-TW": "x0, y0, x1, y1, ...：至少 3 個點，每個座標是相對影格寬度和高度的 0..1 比例", es: "x0, y0, x1, y1, ...: al menos 3 puntos, cada uno una fracción 0..1 del ancho y el alto del fotograma" }
      },
      mode: {
        label: { en: "Mode", ko: "방식", ja: "モード", "zh-CN": "模式", "zh-TW": "模式", es: "Modo" },
        help: { en: "which boxes pass: those whose anchor is inside the polygon, or outside it", ko: "통과시킬 박스: 기준점이 다각형 안 (inside)에 있는 박스 또는 밖 (outside)에 있는 박스", ja: "通すボックス: 基準点が多角形の内側 (inside) にあるもの、または外側 (outside) にあるもの", "zh-CN": "放行哪些框：基准点在多边形内（inside）的，或在多边形外（outside）的", "zh-TW": "放行哪些框：基準點在多邊形內（inside）的，或在多邊形外（outside）的", es: "qué cajas pasan: las que tienen el punto de anclaje dentro del polígono (inside) o fuera (outside)" }
      },
      anchor: {
        label: { en: "Anchor point", ko: "기준점", ja: "基準点", "zh-CN": "基准点", "zh-TW": "基準點", es: "Punto de anclaje" },
        help: { en: "the point of a box that is tested: its bottom centre (where a person stands) or its centre", ko: "검사할 박스의 점: 아래쪽 가운데 (사람이 서 있는 곳) 또는 중심", ja: "判定に使うボックスの点: 下辺の中央 (人が立っている位置) または中心", "zh-CN": "用于判断的框上的点：底边中点（人站立的位置）或中心", "zh-TW": "用於判斷的框上的點：底邊中點（人站立的位置）或中心", es: "el punto de la caja que se comprueba: el centro de su borde inferior (donde está una persona) o su centro" }
      }
    }
  },
  line: {
    summary: { en: "counts tracked boxes crossing a line, in each direction, with an event per crossing", ko: "선을 지나간 tracked 박스를 방향별로 세고, 지나갈 때마다 이벤트를 냅니다", ja: "ラインを横切った追跡中のボックスを方向ごとに数え、横切るたびにイベントを出します", "zh-CN": "按方向统计穿过线的已跟踪框，每次穿越触发一个事件", "zh-TW": "依方向統計穿過線的已追蹤框，每次穿越觸發一個事件", es: "cuenta las cajas con seguimiento que cruzan una línea, en cada sentido, con un evento por cruce" },
    params: {
      line: {
        label: { en: "Line", ko: "선", ja: "ライン", "zh-CN": "线", "zh-TW": "線", es: "Línea" },
        help: { en: "x0, y0, x1, y1: the line from A to B, each a fraction 0..1 of the frame's width and height; \"in\" is a crossing from the left of A->B to its right", ko: "x0, y0, x1, y1: A에서 B로 가는 선, 각 좌표는 프레임 너비·높이에 대한 0..1 비율. \"in\"은 A->B의 왼쪽에서 오른쪽으로 지나가는 것입니다", ja: "x0, y0, x1, y1: A から B へのライン。各座標はフレームの幅・高さに対する 0..1 の割合。\"in\" は A->B の左側から右側への通過です", "zh-CN": "x0, y0, x1, y1：从 A 到 B 的线，每个坐标是相对帧宽度和高度的 0..1 比例；\"in\" 表示从 A->B 的左侧穿到右侧", "zh-TW": "x0, y0, x1, y1：從 A 到 B 的線，每個座標是相對影格寬度和高度的 0..1 比例；\"in\" 表示從 A->B 的左側穿到右側", es: "x0, y0, x1, y1: la línea de A a B, cada valor una fracción 0..1 del ancho y el alto del fotograma; \"in\" es un cruce de la izquierda de A->B a su derecha" }
      },
      anchor: {
        label: { en: "Anchor point", ko: "기준점", ja: "基準点", "zh-CN": "基准点", "zh-TW": "基準點", es: "Punto de anclaje" },
        help: { en: "the point of a box that is tested: its bottom centre (where a person stands) or its centre", ko: "검사할 박스의 점: 아래쪽 가운데 (사람이 서 있는 곳) 또는 중심", ja: "判定に使うボックスの点: 下辺の中央 (人が立っている位置) または中心", "zh-CN": "用于判断的框上的点：底边中点（人站立的位置）或中心", "zh-TW": "用於判斷的框上的點：底邊中點（人站立的位置）或中心", es: "el punto de la caja que se comprueba: el centro de su borde inferior (donde está una persona) o su centro" }
      },
      direction: {
        label: { en: "Direction", ko: "방향", ja: "方向", "zh-CN": "方向", "zh-TW": "方向", es: "Sentido" },
        help: { en: "which crossings raise a \"cross\" event; the counts always keep both", ko: "\"cross\" 이벤트를 낼 통과 방향. 개수는 항상 양방향 모두 셉니다", ja: "\"cross\" イベントを出す通過の向き。件数は常に両方向とも数えます", "zh-CN": "哪些穿越会触发 \"cross\" 事件；计数始终包含两个方向", "zh-TW": "哪些穿越會觸發 \"cross\" 事件；計數始終包含兩個方向", es: "qué cruces lanzan un evento \"cross\"; los recuentos siempre guardan ambos sentidos" }
      }
    }
  },
  count: {
    summary: { en: "counts the boxes of each input (one record per input), in total and per listed class", ko: "입력마다 박스를 셉니다 (입력마다 record 하나). 전체 개수와 나열한 클래스별 개수", ja: "入力ごとにボックスを数えます (入力ごとに 1 レコード)。合計と、指定したクラスごとの件数", "zh-CN": "统计每个输入的框（每个输入一条记录），包括总数和所列各类别的数量", "zh-TW": "統計每個輸入的框（每個輸入一筆記錄），包括總數和所列各類別的數量", es: "cuenta las cajas de cada entrada (un registro por entrada), en total y por cada clase indicada" },
    params: {
      classes: {
        label: { en: "Classes", ko: "클래스", ja: "クラス", "zh-CN": "类别", "zh-TW": "類別", es: "Clases" },
        help: { en: "count only these classes, one number each besides \"total\"; leave it out to count every box", ko: "이 클래스들만 셉니다 (\"total\" 외에 클래스마다 숫자 하나). 비워 두면 모든 박스를 셉니다", ja: "これらのクラスだけを数えます (\"total\" のほかにクラスごとに 1 つの数値)。空にするとすべてのボックスを数えます", "zh-CN": "只统计这些类别，除 \"total\" 外每个类别一个数；留空则统计所有框", "zh-TW": "只統計這些類別，除 \"total\" 外每個類別一個數；留空則統計所有框", es: "cuenta solo estas clases, un número por clase además de \"total\"; vacío cuenta todas las cajas" }
      }
    }
  },
  dwell: {
    summary: { en: "measures how long each tracked box has stayed, with an event when it passes a threshold", ko: "tracked 박스마다 머문 시간을 재고, 기준 시간을 넘으면 이벤트를 냅니다", ja: "追跡中のボックスごとに滞在時間を測り、基準時間を超えるとイベントを出します", "zh-CN": "测量每个已跟踪框停留的时间，超过阈值时触发事件", "zh-TW": "測量每個已追蹤框停留的時間，超過閾值時觸發事件", es: "mide cuánto tiempo lleva cada caja con seguimiento, con un evento cuando supera un umbral" },
    params: {
      threshold_s: {
        label: { en: "Threshold (s)", ko: "기준 시간 (초)", ja: "基準時間 (秒)", "zh-CN": "阈值（秒）", "zh-TW": "閾值（秒）", es: "Umbral (s)" },
        help: { en: "seconds a box must stay before its \"dwell\" event", ko: "\"dwell\" 이벤트를 내기 전에 박스가 머물러야 하는 시간 (초)", ja: "\"dwell\" イベントを出すまでにボックスが滞在する必要がある秒数", "zh-CN": "框停留多少秒后才触发 \"dwell\" 事件", "zh-TW": "框停留多少秒後才觸發 \"dwell\" 事件", es: "segundos que una caja debe permanecer antes de su evento \"dwell\"" }
      },
      grace_s: {
        label: { en: "Grace time (s)", ko: "유예 시간 (초)", ja: "猶予時間 (秒)", "zh-CN": "宽限时间（秒）", "zh-TW": "寬限時間（秒）", es: "Margen (s)" },
        help: { en: "seconds a box may be missing (an occlusion) and still be the same stay", ko: "박스가 가려져 보이지 않아도 같은 체류로 보는 시간 (초)", ja: "ボックスが見えなくなっても (遮蔽) 同じ滞在とみなす秒数", "zh-CN": "框消失（被遮挡）多少秒内仍算同一次停留", "zh-TW": "框消失（被遮擋）多少秒內仍算同一次停留", es: "segundos que una caja puede faltar (una oclusión) y seguir contando como la misma permanencia" }
      }
    }
  },
  condition: {
    summary: { en: "raises an event when a value passes a threshold: a box or crop count, a records number, or the crops with or without a label", ko: "값이 임계값을 넘으면 이벤트를 냅니다: 박스나 crop의 개수, records의 숫자, 또는 label이 있거나 없는 crop", ja: "値がしきい値を超えるとイベントを出します: ボックスやクロップの数、レコードの数値、またはラベルあり・なしのクロップ", "zh-CN": "当某个值越过阈值时触发事件：框或裁剪的数量、记录中的数值，或带有或不带某标签的裁剪", "zh-TW": "當某個值越過閾值時觸發事件：框或裁切的數量、記錄中的數值，或帶有或不帶某標籤的裁切", es: "lanza un evento cuando un valor supera un umbral: un recuento de cajas o recortes, un número de los registros, o los recortes con o sin una etiqueta" },
    params: {
      value: {
        label: { en: "Value", ko: "값", ja: "値", "zh-CN": "值", "zh-TW": "值", es: "Valor" },
        help: { en: "\"count\" (boxes or crops), a number the input writes (records), or \"with:<label>\" / \"without:<label>\" (crops with scores)", ko: "\"count\" (박스나 crop), 입력이 쓰는 숫자 (records), 또는 \"with:<label>\" / \"without:<label>\" (score가 있는 crop)", ja: "\"count\" (ボックスまたはクロップ)、入力が書く数値 (レコード)、または \"with:<label>\" / \"without:<label>\" (スコア付きクロップ)", "zh-CN": "\"count\"（框或裁剪）、输入写出的数值（记录），或 \"with:<label>\" / \"without:<label>\"（带分数的裁剪）", "zh-TW": "\"count\"（框或裁切）、輸入寫出的數值（記錄），或 \"with:<label>\" / \"without:<label>\"（帶分數的裁切）", es: "\"count\" (cajas o recortes), un número que escribe la entrada (registros), o \"with:<label>\" / \"without:<label>\" (recortes con puntuaciones)" }
      },
      comparator: {
        label: { en: "Comparison", ko: "비교", ja: "比較", "zh-CN": "比较", "zh-TW": "比較", es: "Comparación" },
        help: { en: "how the value is compared with \"threshold\"", ko: "값을 \"threshold\"와 비교하는 방법", ja: "値を \"threshold\" と比較する方法", "zh-CN": "值与 \"threshold\" 的比较方式", "zh-TW": "值與 \"threshold\" 的比較方式", es: "cómo se compara el valor con \"threshold\"" }
      },
      threshold: {
        label: { en: "Threshold", ko: "임계값", ja: "しきい値", "zh-CN": "阈值", "zh-TW": "閾值", es: "Umbral" },
        help: { en: "the number the value is compared with", ko: "값과 비교할 숫자", ja: "値と比較する数値", "zh-CN": "与该值比较的数", "zh-TW": "與該值比較的數", es: "el número con el que se compara el valor" }
      },
      reduce: {
        label: { en: "Combine", ko: "합치는 방법", ja: "まとめ方", "zh-CN": "合并方式", "zh-TW": "合併方式", es: "Combinación" },
        help: { en: "how several records' values become one: their largest, smallest or sum", ko: "여러 record의 값을 하나로 합치는 방법: 최댓값, 최솟값 또는 합", ja: "複数のレコードの値を 1 つにまとめる方法: 最大値、最小値、または合計", "zh-CN": "多条记录的值如何合成一个：取最大值、最小值或总和", "zh-TW": "多筆記錄的值如何合成一個：取最大值、最小值或總和", es: "cómo los valores de varios registros se vuelven uno: el mayor, el menor o la suma" }
      },
      cooldown_s: {
        label: { en: "Repeat interval (s)", ko: "반복 간격 (초)", ja: "繰り返し間隔 (秒)", "zh-CN": "重复间隔（秒）", "zh-TW": "重複間隔（秒）", es: "Intervalo de repetición (s)" },
        help: { en: "0: one event when the condition becomes true; more: an event at most this often while it holds", ko: "0: 조건이 참이 될 때 이벤트 한 번. 0보다 크면: 조건이 유지되는 동안 이 간격마다 최대 한 번", ja: "0: 条件が真になったときに 1 回。それより大きい値: 条件が続く間、この間隔ごとに最大 1 回", "zh-CN": "0：条件变为真时触发一次；大于 0：条件持续期间最多每隔这么久触发一次", "zh-TW": "0：條件變為真時觸發一次；大於 0：條件持續期間最多每隔這麼久觸發一次", es: "0: un evento cuando la condición se cumple; más: como mucho un evento cada tanto mientras se mantiene" }
      },
      event: {
        label: { en: "Event name", ko: "이벤트 이름", ja: "イベント名", "zh-CN": "事件名称", "zh-TW": "事件名稱", es: "Nombre del evento" },
        help: { en: "the event name (letters, digits, _ . : -); leave it out for the node id", ko: "이벤트 이름 (영문자, 숫자, _ . : -). 비워 두면 노드 ID를 씁니다", ja: "イベント名 (英字、数字、_ . : -)。空にするとノード ID を使います", "zh-CN": "事件名称（字母、数字、_ . : -）；留空则使用节点 ID", "zh-TW": "事件名稱（字母、數字、_ . : -）；留空則使用節點 ID", es: "el nombre del evento (letras, dígitos, _ . : -); vacío usa el id del nodo" }
      }
    }
  },
  gallery: {
    summary: { en: "names each embedding after its nearest gallery entry, or \"unknown\" under a threshold, with an event when a track's name changes", ko: "각 embedding에 가장 가까운 Gallery 항목의 이름을 붙이고, 임계값 아래면 \"unknown\"으로 합니다. track의 이름이 바뀌면 이벤트를 냅니다", ja: "各埋め込みに最も近いギャラリー項目の名前を付け、しきい値未満なら \"unknown\" にします。トラックの名前が変わるとイベントを出します", "zh-CN": "为每个嵌入向量取最接近的图库条目的名称，低于阈值则为 \"unknown\"；跟踪对象的名称改变时触发事件", "zh-TW": "為每個嵌入向量取最接近的圖庫項目的名稱，低於閾值則為 \"unknown\"；追蹤對象的名稱改變時觸發事件", es: "da a cada embedding el nombre de la entrada de la galería más cercana, o \"unknown\" bajo un umbral, con un evento cuando cambia el nombre de un seguimiento" },
    params: {
      gallery: {
        label: { en: "Gallery file", ko: "Gallery 파일", ja: "ギャラリーファイル", "zh-CN": "图库文件", "zh-TW": "圖庫檔案", es: "Archivo de galería" },
        help: { en: "a DXGAL1 .bin built from an image folder: python3 scripts/build_gallery_database.py --variant <model> --images <folder> --out <file>.bin", ko: "이미지 폴더로 만든 DXGAL1 .bin 파일: python3 scripts/build_gallery_database.py --variant <model> --images <folder> --out <file>.bin", ja: "画像フォルダーから作った DXGAL1 .bin: python3 scripts/build_gallery_database.py --variant <model> --images <folder> --out <file>.bin", "zh-CN": "由图片文件夹生成的 DXGAL1 .bin：python3 scripts/build_gallery_database.py --variant <model> --images <folder> --out <file>.bin", "zh-TW": "由圖片資料夾產生的 DXGAL1 .bin：python3 scripts/build_gallery_database.py --variant <model> --images <folder> --out <file>.bin", es: "un .bin DXGAL1 creado a partir de una carpeta de imágenes: python3 scripts/build_gallery_database.py --variant <model> --images <folder> --out <file>.bin" }
      },
      threshold: {
        label: { en: "Threshold", ko: "임계값", ja: "しきい値", "zh-CN": "阈值", "zh-TW": "閾值", es: "Umbral" },
        help: { en: "the smallest cosine similarity that names a match", ko: "일치로 볼 최소 코사인 유사도", ja: "一致とみなす最小のコサイン類似度", "zh-CN": "判定为匹配的最低余弦相似度", "zh-TW": "判定為相符的最低餘弦相似度", es: "la similitud de coseno mínima que da nombre a una coincidencia" }
      },
      events: {
        label: { en: "Events", ko: "이벤트", ja: "イベント", "zh-CN": "事件", "zh-TW": "事件", es: "Eventos" },
        help: { en: "\"match\" events only, \"unknown\" events too, or none", ko: "\"match\" 이벤트만, \"unknown\" 이벤트도, 또는 이벤트 없음", ja: "\"match\" イベントのみ、\"unknown\" イベントも、またはなし", "zh-CN": "仅 \"match\" 事件、也包括 \"unknown\" 事件，或不触发", "zh-TW": "僅 \"match\" 事件、也包括 \"unknown\" 事件，或不觸發", es: "solo eventos \"match\", también eventos \"unknown\", o ninguno" }
      }
    }
  },
  user: {
    summary: { en: "your own logic: in a run it passes its input through; an exported project gets a function stub to fill in", ko: "직접 작성하는 Logic: 실행할 때는 입력을 그대로 넘기고, export한 프로젝트에는 채워 넣을 함수 stub이 생깁니다", ja: "独自のロジック: 実行時は入力をそのまま渡し、エクスポートしたプロジェクトには中身を書く関数スタブが入ります", "zh-CN": "你自己的逻辑：运行时原样传递输入；导出的项目中会生成一个待填写的函数桩", "zh-TW": "你自己的邏輯：執行時原樣傳遞輸入；匯出的專案中會產生一個待填寫的函式樁", es: "su propia lógica: al ejecutar deja pasar su entrada; un proyecto exportado recibe un esqueleto de función para completar" },
    params: {
      name: {
        label: { en: "Function name", ko: "함수 이름", ja: "関数名", "zh-CN": "函数名", "zh-TW": "函式名稱", es: "Nombre de la función" },
        help: { en: "the stub function's name in an exported project: letters, digits and _, not starting with a digit", ko: "export한 프로젝트의 stub 함수 이름: 영문자, 숫자, _ 사용, 숫자로 시작하지 않음", ja: "エクスポートしたプロジェクトでのスタブ関数名: 英字・数字・_ で、数字で始まらないこと", "zh-CN": "导出项目中桩函数的名称：字母、数字和 _，不能以数字开头", "zh-TW": "匯出專案中樁函式的名稱：字母、數字和 _，不能以數字開頭", es: "el nombre de la función esqueleto en un proyecto exportado: letras, dígitos y _, sin empezar por un dígito" }
      },
      input: {
        label: { en: "Input", ko: "입력", ja: "入力", "zh-CN": "输入", "zh-TW": "輸入", es: "Entrada" },
        help: { en: "the kind of data the function receives", ko: "함수가 받는 데이터 종류", ja: "関数が受け取るデータの種類", "zh-CN": "函数接收的数据类型", "zh-TW": "函式接收的資料類型", es: "el tipo de datos que recibe la función" }
      },
      output: {
        label: { en: "Output", ko: "출력", ja: "出力", "zh-CN": "输出", "zh-TW": "輸出", es: "Salida" },
        help: { en: "the kind it returns; in a run the input passes through, so it equals \"input\"", ko: "함수가 돌려주는 종류. 실행할 때는 입력을 그대로 넘기므로 \"input\"과 같아야 합니다", ja: "関数が返す種類。実行時は入力をそのまま渡すので、\"input\" と同じにします", "zh-CN": "函数返回的类型；运行时输入原样传递，因此与 \"input\" 相同", "zh-TW": "函式回傳的類型；執行時輸入原樣傳遞，因此與 \"input\" 相同", es: "el tipo que devuelve; al ejecutar la entrada pasa tal cual, así que es igual a \"input\"" }
      }
    }
  }
};

/* ─── CSS Selectors for DOM translation ─── */
window._DX_I18N_SELECTORS = [
  '.nav-label',
  'h1 .accent',
  'h2', 'h3',
  'label',
  '.setup-card-title',
  '.setup-card-desc',
  '.gauge-label',
  'th',
  '.btn',
  '.plan-preset',
  '.plan-rb',
  '.dev-tab',
  '.run-tab',
  '.comp-radio',
  '.comp-check',
  '.comp-tip',
  '.txt-dim',
  '.hf-k',
  '.hw-float-title',
  '.lv-label',
  '.stat .label',
  '.comp-status-badge',
  'option',
  '.plan-warn-badge',
].join(',');

/**
 * Translate select option elements (app-specific).
 */
function _i18nOptions() {
  var dict = window._DX_I18N_DICT || {};
  var lang = (window.DXI18n && window.DXI18n.lang) || 'en';
  document.querySelectorAll('select option').forEach(function(opt) {
    var txt = opt.textContent.trim();
    var orig = opt.getAttribute('data-i18n-orig') || txt;
    if (lang === 'en') {
      if (opt.getAttribute('data-i18n-orig')) opt.textContent = orig;
    } else {
      var entry = dict[orig] || dict[txt];
      if (entry && typeof entry === 'object' && entry[lang]) {
        opt.setAttribute('data-i18n-orig', orig);
        opt.textContent = entry[lang];
      } else if (typeof entry === 'string' && lang === 'ko') {
        opt.setAttribute('data-i18n-orig', orig);
        opt.textContent = entry;
      }
    }
  });
}

/* ─── Placeholders ─── */
window._DX_I18N_PLACEHOLDERS = {
  'Search models...': {
    ko: '모델 검색...', ja: 'モデルを検索...',
    es: 'Buscar modelos...',
    'zh-CN': '搜索模型...', 'zh-TW': '搜尋模型...'
  },
  'Username (email)': {
    ko: '사용자 이름 (이메일)', ja: 'ユーザー名 (メール)',
    es: 'Nombre de usuario (correo)',
    'zh-CN': '用户名 (邮箱)', 'zh-TW': '使用者名稱 (電子郵件)'
  },
  'Password': {
    ko: '비밀번호', ja: 'パスワード',
    es: 'Contraseña',
    'zh-CN': '密码', 'zh-TW': '密碼'
  },
  'Enter password...': {
    ko: '비밀번호를 입력하세요...', ja: 'パスワードを入力...',
    'zh-CN': '输入密码...', 'zh-TW': '輸入密碼...',
    es: 'Introduzca contraseña...',
  },
  'Enter value and press Enter': {
    ko: '값을 입력하고 Enter를 누르세요', ja: '値を入力して Enter を押してください',
    es: 'Ingrese un valor y presione Enter',
    'zh-CN': '输入值并按回车', 'zh-TW': '輸入值並按 Enter'
  },
  '/path/to/model.onnx': {
    ko: '/path/to/model.onnx', ja: '/path/to/model.onnx',
    es: '/ruta/modelo.onnx',
    'zh-CN': '/path/to/model.onnx', 'zh-TW': '/path/to/model.onnx'
  },
  'input.1': {
    ko: 'input.1', ja: 'input.1',
    es: 'input.1',
    'zh-CN': 'input.1', 'zh-TW': 'input.1'
  },
  '1,3,224,224': {
    ko: '1,3,224,224', ja: '1,3,224,224',
    es: '1,3,224,224',
    'zh-CN': '1,3,224,224', 'zh-TW': '1,3,224,224'
  },
  '/path/to/calibration_images': {
    ko: '/path/to/calibration_images', ja: '/path/to/calibration_images',
    es: '/path/to/calibration_images',
    'zh-CN': '/path/to/calibration_images', 'zh-TW': '/path/to/calibration_images'
  },
  'Or type a path directly…': {
    ko: '또는 직접 경로를 입력...', ja: 'または直接パスを入力…',
    es: 'O escriba una ruta directamente…',
    'zh-CN': '或直接输入路径…', 'zh-TW': '或直接輸入路徑…'
  },
  'Enter model name': {
    ko: '모델 이름 입력', ja: 'モデル名を入力',
    'zh-CN': '输入模型名称', 'zh-TW': '輸入模型名稱',
    es: 'Introduzca nombre del modelo',
  },
  'e.g. yolov8n_custom': {
    ko: '예: yolov8n_custom', ja: '例: yolov8n_custom',
    es: 'ej. yolov8n_custom',
    'zh-CN': '例: yolov8n_custom', 'zh-TW': '例: yolov8n_custom'
  },
  'e.g. 3d_reconstruction': {
    ko: '예: 3d_reconstruction', ja: '例: 3d_reconstruction',
    es: 'ej. 3d_reconstruction',
    'zh-CN': '例: 3d_reconstruction', 'zh-TW': '例: 3d_reconstruction'
  },
  'chore: update': {
    ko: 'chore: update', ja: 'chore: update',
    es: 'chore: update',
    'zh-CN': 'chore: update', 'zh-TW': 'chore: update'
  },
  'or type model name manually': {
    ko: '또는 모델 이름 수동 입력', ja: 'またはモデル名を手動入力',
    es: 'o escriba el nombre del modelo',
    'zh-CN': '或手动输入模型名称', 'zh-TW': '或手動輸入模型名稱'
  },
  'Search model name…': {
    ko: '모델 이름 검색...', ja: 'モデル名を検索…',
    es: 'Buscar nombre de modelo…',
    'zh-CN': '搜索模型名称…', 'zh-TW': '搜尋模型名稱…'
  },
  'Type a path or click to browse  (Tab = autocomplete)': {
    ko: '경로를 입력하거나 클릭하여 탐색 (Tab = 자동완성)', ja: 'パスを入力またはクリックして参照 (Tab = 自動補完)',
    es: 'Escriba una ruta o haga clic para explorar (Tab = autocompletar)',
    'zh-CN': '输入路径或点击浏览 (Tab = 自动补全)', 'zh-TW': '輸入路徑或點擊瀏覽 (Tab = 自動補全)'
  },
  'or category/model_name (e.g. object_detection/yolov8n)': {
    ko: '또는 category/model_name (예: object_detection/yolov8n)', ja: 'または category/model_name (例: object_detection/yolov8n)',
    es: 'o categoría/nombre_modelo (ej. object_detection/yolov8n)',
    'zh-CN': '或 category/model_name (例: object_detection/yolov8n)', 'zh-TW': '或 category/model_name (例: object_detection/yolov8n)'
  },
  'Type and press Enter': {
    ko: '입력하고 Enter를 누르세요', ja: '入力してEnterを押してください',
    es: 'Escriba y presione Enter',
    'zh-CN': '输入并按Enter', 'zh-TW': '輸入並按Enter'
  },
  'Type input to send to the process (press Enter)': {
    ko: '프로세스에 보낼 입력 (Enter 키)', ja: 'プロセスに送信する入力を入力 (Enter キー)',
    'zh-CN': '输入要发送到进程的内容 (按 Enter)', 'zh-TW': '輸入要傳送至程序的內容 (按 Enter)',
    es: 'Escriba la entrada para enviar al proceso (presione Enter)',
  },
  'Search documentation...': {
    ko: '문서 검색...', ja: 'ドキュメントを検索...',
    es: 'Buscar documentación...',
    'zh-CN': '搜索文档...', 'zh-TW': '搜尋文件...'
  },

  /* Charts / Results */
  'Class': {
    ko: '클래스', ja: 'クラス',
    'zh-CN': '类别', 'zh-TW': '類別',
    es: 'Clase',
  },
  'Detections': {
    ko: '감지 수', ja: '検出数',
    'zh-CN': '检测数', 'zh-TW': '偵測數',
    es: 'Detecciones',
  },
  'Avg Conf': {
    ko: '평균 신뢰도', ja: '平均信頼度',
    'zh-CN': '平均置信度', 'zh-TW': '平均信賴度',
    es: 'Conf. prom.',
  },
  'Handedness': {
    ko: '왼손/오른손', ja: '利き手',
    'zh-CN': '惯用手', 'zh-TW': '慣用手',
    es: 'Lateralidad',
  },
  'Count': {
    ko: '개수', ja: '件数',
    'zh-CN': '数量', 'zh-TW': '數量',
    es: 'Conteo',
  },
  'Avg Pixel %': {
    ko: '평균 픽셀 %', ja: '平均ピクセル%',
    'zh-CN': '平均像素%', 'zh-TW': '平均像素%',
    es: '% píxel prom.',
  },
  'Mean Depth': {
    ko: '평균 깊이', ja: '平均深度',
    'zh-CN': '平均深度', 'zh-TW': '平均深度',
    es: 'Profundidad media',
  },
  'Min Depth': {
    ko: '최소 깊이', ja: '最小深度',
    'zh-CN': '最小深度', 'zh-TW': '最小深度',
    es: 'Profundidad mín.',
  },
  'Max Depth': {
    ko: '최대 깊이', ja: '最大深度',
    'zh-CN': '最大深度', 'zh-TW': '最大深度',
    es: 'Profundidad máx.',
  },
  'Frames': {
    ko: '프레임', ja: 'フレーム',
    'zh-CN': '帧数', 'zh-TW': '幀數',
    es: 'Cuadros',
  },
  'Total Persons': {
    ko: '총 인원', ja: '合計人数',
    'zh-CN': '总人数', 'zh-TW': '總人數',
    es: 'Total de personas',
  },
  'Total Faces': {
    ko: '총 얼굴', ja: '顔の総数',
    'zh-CN': '人脸总数', 'zh-TW': '人臉總數',
    es: 'Total de rostros',
  },
  'Avg/Frame': {
    ko: '평균/프레임', ja: '平均/フレーム',
    'zh-CN': '平均/帧', 'zh-TW': '平均/幀',
    es: 'Prom./Cuadro',
  },
  'Avg Yaw': {
    ko: '평균 Yaw', ja: '平均Yaw',
    'zh-CN': '平均Yaw', 'zh-TW': '平均Yaw',
    es: 'Yaw prom.',
  },
  'Avg Pitch': {
    ko: '평균 Pitch', ja: '平均Pitch',
    'zh-CN': '平均Pitch', 'zh-TW': '平均Pitch',
    es: 'Pitch prom.',
  },
  'Avg Roll': {
    ko: '평균 Roll', ja: '平均Roll',
    'zh-CN': '平均Roll', 'zh-TW': '平均Roll',
    es: 'Roll prom.',
  },
  'No detections recorded.': {
    ko: '기록된 감지가 없습니다.', ja: '検出記録がありません。',
    'zh-CN': '没有检测记录。', 'zh-TW': '沒有偵測記錄。',
    es: 'No se registraron detecciones.',
  },
  'No results recorded.': {
    ko: '기록된 결과가 없습니다.', ja: '結果の記録がありません。',
    'zh-CN': '没有结果记录。', 'zh-TW': '沒有結果記錄。',
    es: 'No se registraron resultados.',
  },
  'No segmentation data.': {
    ko: '분할 데이터가 없습니다.', ja: 'セグメンテーションデータがありません。',
    'zh-CN': '没有分割数据。', 'zh-TW': '沒有分割資料。',
    es: 'Sin datos de segmentación.',
  },
  'Waiting for data…': {
    ko: '데이터 대기 중…', ja: 'データ待機中…',
    'zh-CN': '等待数据…', 'zh-TW': '等待資料…',
    es: 'Esperando datos…',
  },
  'No run data yet': {
    ko: '아직 실행 데이터가 없습니다', ja: '実行データはまだありません',
    'zh-CN': '尚无运行数据', 'zh-TW': '尚無執行資料',
    es: 'Aún no hay datos de ejecución',
  },

  /* Benchmark */
  'DX-APP Benchmark Report': {
    ko: 'DX-APP 벤치마크 리포트', ja: 'DX-APP ベンチマークレポート',
    'zh-CN': 'DX-APP 基准测试报告', 'zh-TW': 'DX-APP 基準測試報告',
    es: 'Informe de benchmark DX-APP',
  },
  'Generated: ': {
    ko: '생성일: ', ja: '生成日: ',
    'zh-CN': '生成日期: ', 'zh-TW': '產生日期: ',
    es: 'Generado: ',
  },
  'Input: ': {
    ko: '입력: ', ja: '入力: ',
    'zh-CN': '输入: ', 'zh-TW': '輸入: ',
    es: 'Entrada: ',
  },
  'Language: ': {
    ko: '언어: ', ja: '言語: ',
    'zh-CN': '语言: ', 'zh-TW': '語言: ',
    es: 'Idioma: ',
  },
  'Loop: ': {
    ko: '루프: ', ja: 'ループ: ',
    'zh-CN': '循环: ', 'zh-TW': '迴圈: ',
    es: 'Bucle: ',
  },

  /* Compiler */
  'Compilation stopped': {
    ko: '컴파일 중단됨', ja: 'コンパイル停止',
    'zh-CN': '编译已停止', 'zh-TW': '編譯已停止',
    es: 'Compilación detenida',
  },

  'Average': {
    ko: '평균', ja: '平均',
    'zh-CN': '平均值', 'zh-TW': '平均值',
    es: 'Promedio',
  },
  'Avg FPS': {
    ko: '평균 FPS', ja: '平均 FPS',
    'zh-CN': '平均 FPS', 'zh-TW': '平均 FPS',
    es: 'FPS prom.',
  },
  'DX-APP Benchmark Report — Generated automatically by DX-APP GUI': {
    ko: 'DX-APP 벤치마크 리포트 — DX-APP GUI에서 자동 생성됨', ja: 'DX-APP ベンチマークレポート — DX-APP GUIにより自動生成',
    'zh-CN': 'DX-APP 基准测试报告 — 由 DX-APP GUI 自动生成', 'zh-TW': 'DX-APP 基準測試報告 — 由 DX-APP GUI 自動產生',
    es: 'DX-APP Benchmark Report — Generado automáticamente por DX-APP GUI',
  },
  'ERROR': {
    ko: '오류', ja: 'エラー',
    'zh-CN': '错误', 'zh-TW': '錯誤',
    es: 'ERROR',
  },
  'Elapsed': {
    ko: '경과', ja: '経過',
    'zh-CN': '已用时间', 'zh-TW': '已用時間',
    es: 'Transcurrido',
  },
  'FPS Bar': {
    ko: 'FPS 바', ja: 'FPS バー',
    'zh-CN': 'FPS 条形图', 'zh-TW': 'FPS 長條圖',
    es: 'Barra de FPS',
  },
  'Failed': {
    ko: '실패', ja: '失敗',
    'zh-CN': '失败', 'zh-TW': '失敗',
    es: 'Fallido',
  },
  'Errors': {
    ko: '오류', ja: 'エラー',
    'zh-CN': '错误', 'zh-TW': '錯誤',
    es: 'Errores',
  },
  'Failed / Error': {
    ko: '실패 / 오류', ja: '失敗 / エラー',
    'zh-CN': '失败 / 错误', 'zh-TW': '失敗 / 錯誤',
    es: 'Fallido / Error',
  },
  'Last 5 lines of output': {
    ko: '마지막 5줄 출력', ja: '出力の最後の5行',
    'zh-CN': '最后 5 行输出', 'zh-TW': '最後 5 行輸出',
    es: 'Últimas 5 líneas de salida',
  },
  'Max': {
    ko: '최대', ja: '最大',
    'zh-CN': '最大值', 'zh-TW': '最大值',
    es: 'Máx',
  },
  'Median': {
    ko: '중앙값', ja: '中央値',
    'zh-CN': '中位数', 'zh-TW': '中位數',
    es: 'Mediana',
  },
  'Min': {
    ko: '최소', ja: '最小',
    'zh-CN': '最小值', 'zh-TW': '最小值',
    es: 'Mín',
  },
  'Passed': {
    ko: '성공', ja: '成功',
    'zh-CN': '通过', 'zh-TW': '通過',
    es: 'Aprobado',
  },
  'Report Generated': {
    ko: '보고서 생성됨', ja: 'レポート生成完了',
    'zh-CN': '报告已生成', 'zh-TW': '報告已產生',
    es: 'Informe generado',
  },
  'Benchmark Detail — ': {
    ko: '벤치마크 상세 —', ja: 'ベンチマーク詳細 —',
    'zh-CN': '基准测试详情 —', 'zh-TW': '基準測試詳情 —',
    es: 'Detalle de benchmark —',
  },
  'elapsed: ': {
    ko: '경과: ', ja: '経過: ',
    'zh-CN': '已用时间: ', 'zh-TW': '已用時間: ',
    es: 'transcurrido: ',
  },
  'Run Error:': {
    ko: '실행 오류:', ja: '実行エラー:',
    'zh-CN': '运行错误:', 'zh-TW': '執行錯誤:',
    es: 'Error de ejecución:',
  },
  'Latency Analysis': {
    ko: '지연시간 분석', ja: 'レイテンシ分析',
    'zh-CN': '延迟分析', 'zh-TW': '延遲分析',
    es: 'Análisis de latencia',
  },
  'Runtime Errors': {
    ko: '런타임 오류', ja: 'ランタイムエラー',
    'zh-CN': '运行时错误', 'zh-TW': '執行階段錯誤',
    es: 'Errores de ejecución',
  },
  'Accuracy Failures': {
    ko: '정확도 실패', ja: '精度失敗',
    'zh-CN': '准确性失败', 'zh-TW': '準確度失敗',
    es: 'Fallos de precisión',
  },
  'Power Efficiency (FPS / Watt)': {
    ko: '전력 효율 (FPS / Watt)', ja: '電力効率 (FPS / Watt)',
    'zh-CN': '能效比 (FPS / Watt)', 'zh-TW': '能效比 (FPS / Watt)',
    es: 'Eficiencia energética (FPS / Watt)',
  },
  'Performance Ranking': {
    ko: '성능 순위', ja: 'パフォーマンスランキング',
    'zh-CN': '性能排名', 'zh-TW': '效能排名',
    es: 'Clasificación de rendimiento',
  },
  'Category Summary': {
    ko: '카테고리 요약', ja: 'カテゴリ概要',
    'zh-CN': '类别摘要', 'zh-TW': '類別摘要',
    es: 'Resumen de categoría',
  },
  'FPS vs Latency': {
    ko: 'FPS 대 지연시간', ja: 'FPS vs レイテンシ',
    'zh-CN': 'FPS 与延迟', 'zh-TW': 'FPS 與延遲',
    es: 'FPS vs Latencia',
  },
  'Hardware Resources (Post-Run)': {
    ko: '하드웨어 리소스 (실행 후)', ja: 'ハードウェアリソース (実行後)',
    'zh-CN': '硬件资源 (运行后)', 'zh-TW': '硬體資源 (執行後)',
    es: 'Recursos de hardware (post-ejecución)',
  },
  'Environment': {
    ko: '환경', ja: '環境',
    'zh-CN': '环境', 'zh-TW': '環境',
    es: 'Entorno',
  },
  'Result Gallery': {
    ko: '결과 갤러리', ja: '結果ギャラリー',
    'zh-CN': '结果画廊', 'zh-TW': '結果圖庫',
    es: 'Galería de resultados',
  },

  'All Tasks': {
    ko: '전체 태스크', ja: '全タスク',
    'zh-CN': '所有任务', 'zh-TW': '所有任務',
    es: 'Todas las tareas',
  },
  'No matches': {
    ko: '일치 항목 없음', ja: '一致なし',
    'zh-CN': '无匹配项', 'zh-TW': '無匹配項',
    es: 'Sin coincidencias',
  },
  'No result': {
    ko: '결과 없음', ja: '結果なし',
    'zh-CN': '无结果', 'zh-TW': '無結果',
    es: 'Sin resultado',
  },
  'No visual result': {
    ko: '시각적 결과 없음', ja: '視覚的な結果なし',
    'zh-CN': '无可视化结果', 'zh-TW': '無可視化結果',
    es: 'Sin resultado visual',
  },
  'Select a model and click Run All': {
    ko: '모델을 선택하고 전체 실행을 클릭하세요', ja: 'モデルを選択して 全て実行 をクリックしてください',
    'zh-CN': '选择模型并点击 全部运行', 'zh-TW': '選擇模型並點擊 全部執行',
    es: 'Seleccione un modelo y haga clic en Ejecutar todo',
  },
  'Task Filter': {
    ko: '태스크 필터', ja: 'Taskフィルター',
    'zh-CN': '任务筛选', 'zh-TW': '任務篩選',
    es: 'Filtro de tarea',
  },
  '— Select Model —': {
    ko: '— 모델 선택 —', ja: '— モデル選択 —',
    'zh-CN': '— 选择模型 —', 'zh-TW': '— 選擇模型 —',
    es: '— Seleccionar modelo —',
  },

  ' step(s)': {
    ko: ' 단계', ja: ' ステップ',
    'zh-CN': ' 步', 'zh-TW': ' 步',
    es: ' paso(s)',
  },
  '" will be auto-selected': {
    ko: '"이 자동 선택됩니다', ja: '" が自動選択されます',
    es: '" se seleccionará automáticamente',
    'zh-CN': '" 将被自动选择', 'zh-TW': '" 將被自動選擇'
  },
  '". Continue?': {
    ko: '"로 저장됩니다. 계속하시겠습니까?', ja: '"で保存されます。続行しますか？',
    es: '". ¿Continuar?',
    'zh-CN': '"保存。是否继续？', 'zh-TW': '"儲存。是否繼續？'
  },
  'DXNN model file not found — check if the compiled file still exists': {
    ko: 'DXNN 모델 파일을 찾을 수 없습니다. 컴파일된 파일이 존재하는지 확인해주세요', ja: 'DXNN モデルファイルが見つかりません — コンパイル済みファイルが存在するか確認してください',
    'zh-CN': '未找到 DXNN 模型文件 — 请检查编译后的文件是否仍然存在', 'zh-TW': '找不到 DXNN 模型檔案 — 請檢查編譯後的檔案是否仍然存在',
    es: 'Archivo de modelo DXNN no encontrado — verifique si el archivo compilado aún existe',
  },
  'DXNN model not found': {
    ko: 'DXNN 모델을 찾을 수 없습니다', ja: 'DXNN モデルが見つかりません',
    'zh-CN': '未找到 DXNN 模型', 'zh-TW': '找不到 DXNN 模型',
    es: 'Modelo DXNN no encontrado',
  },
  'Failed to load models for side-by-side view': {
    ko: '나란히 보기 모델 로드 실패', ja: 'サイドバイサイド表示用のモデル読み込みに失敗しました',
    'zh-CN': '加载并排视图模型失败', 'zh-TW': '載入並排檢視模型失敗',
    es: 'Error al cargar modelos para vista lado a lado',
  },
  'INPUTS': {
    ko: '입력', ja: '入力',
    'zh-CN': '输入', 'zh-TW': '輸入',
    es: 'ENTRADAS',
  },
  'Model file could not be linked': {
    ko: '모델 파일을 연결할 수 없습니다', ja: 'モデルファイルをリンクできませんでした',
    'zh-CN': '无法链接模型文件', 'zh-TW': '無法連結模型檔案',
    es: 'No se pudo vincular el archivo de modelo',
  },
  'Model file not found': {
    ko: '모델 파일을 찾을 수 없습니다', ja: 'モデルファイルが見つかりません',
    'zh-CN': '未找到模型文件', 'zh-TW': '找不到模型檔案',
    es: 'Archivo de modelo no encontrado',
  },
  'No recognized fields': {
    ko: '인식된 필드 없음', ja: '認識されたフィールドなし',
    'zh-CN': '无可识别字段', 'zh-TW': '無可識別欄位',
    es: 'Sin campos reconocidos',
  },
  'No samples': {
    ko: '샘플 없음', ja: 'サンプルなし',
    'zh-CN': '无样本', 'zh-TW': '無樣本',
    es: 'Sin muestras',
  },
  'Nodes': {
    ko: '노드', ja: 'ノード',
    'zh-CN': '节点', 'zh-TW': '節點',
    es: 'Nodos',
  },
  'ONNX model not found': {
    ko: 'ONNX 모델을 찾을 수 없습니다', ja: 'ONNX モデルが見つかりません',
    'zh-CN': '未找到 ONNX 模型', 'zh-TW': '找不到 ONNX 模型',
    es: 'Modelo ONNX no encontrado',
  },
  'OUTPUTS': {
    ko: '출력', ja: '出力',
    'zh-CN': '输出', 'zh-TW': '輸出',
    es: 'SALIDAS',
  },
  'Opset': {
    ko: 'Opset', ja: 'Opset',
    'zh-CN': 'Opset', 'zh-TW': 'Opset',
    es: 'Opset',
  },
  'Output': {
    ko: '출력', ja: '出力',
    'zh-CN': '输出', 'zh-TW': '輸出',
    es: 'Salida',
  },
  'Run already in progress': {
    ko: '실행이 이미 진행 중입니다', ja: '実行はすでに進行中です',
    'zh-CN': '运行已在进行中', 'zh-TW': '執行已在進行中',
    es: 'La ejecución ya está en curso',
  },
  'Size: ': {
    ko: '크기: ', ja: 'サイズ: ',
    'zh-CN': '大小: ', 'zh-TW': '大小: ',
    es: 'Tamaño: ',
  },
  'The model name contains special characters and will be saved as "': {
    ko: '모델 이름에 특수 문자가 포함되어 "', ja: 'モデル名に特殊文字が含まれているため "',
    es: 'El nombre del modelo contiene caracteres especiales y se guardará como "',
    'zh-CN': '模型名称包含特殊字符，将保存为 "', 'zh-TW': '模型名稱包含特殊字元，將儲存為 "'
  },

  'Authenticated': {
    ko: '인증됨', ja: '認証済み',
    'zh-CN': '已认证', 'zh-TW': '已認證',
    es: 'Autenticado',
  },
  'Committing…': {
    ko: '커밋 중…', ja: 'コミット中…',
    'zh-CN': '正在提交…', 'zh-TW': '正在提交…',
    es: 'Confirmando…',
  },
  'Creating skeleton for: ': {
    ko: '스켈레톤 생성 중: ', ja: 'スケルトン作成中: ',
    'zh-CN': '正在创建骨架: ', 'zh-TW': '正在建立骨架: ',
    es: 'Creando esqueleto para: ',
  },
  'Creating...': {
    ko: '생성 중...', ja: '作成中...',
    'zh-CN': '正在创建...', 'zh-TW': '正在建立...',
    es: 'Creando...',
  },
  'Delete ': {
    ko: '삭제 ', ja: '削除 ',
    'zh-CN': '删除 ', 'zh-TW': '刪除 ',
    es: 'Eliminar ',
  },
  'Deleted': {
    ko: '삭제됨', ja: '削除済み',
    'zh-CN': '已删除', 'zh-TW': '已刪除',
    es: 'Eliminado',
  },
  'Extract failed': {
    ko: '추출 실패', ja: '抽出失敗',
    'zh-CN': '提取失败', 'zh-TW': '擷取失敗',
    es: 'Error al extraer',
  },
  'Extracting package for: ': {
    ko: '패키지 추출 중: ', ja: 'パッケージ抽出中: ',
    'zh-CN': '正在提取包: ', 'zh-TW': '正在擷取套件: ',
    es: 'Extrayendo paquete para: ',
  },
  'Model added': {
    ko: '모델 추가됨', ja: 'モデル追加済み',
    'zh-CN': '模型已添加', 'zh-TW': '模型已新增',
    es: 'Modelo agregado',
  },
  'Name required': {
    ko: '이름 필수', ja: '名前は必須です',
    'zh-CN': '名称为必填项', 'zh-TW': '名稱為必填項',
    es: 'Se requiere nombre',
  },
  'Package extracted to outputs/': {
    ko: '패키지가 outputs/에 추출됨', ja: 'パッケージを outputs/ に抽出しました',
    'zh-CN': '包已提取到 outputs/', 'zh-TW': '套件已擷取到 outputs/',
    es: 'Paquete extraído a outputs/',
  },
  'Select or enter a model path': {
    ko: '모델 경로를 선택하거나 입력하세요', ja: 'モデルパスを選択または入力してください',
    'zh-CN': '选择或输入模型路径', 'zh-TW': '選擇或輸入模型路徑',
    es: 'Seleccione o introduzca una ruta de modelo',
  },
  'Skeleton created: ': {
    ko: '스켈레톤 생성됨: ', ja: 'スケルトン作成完了: ',
    'zh-CN': '骨架已创建: ', 'zh-TW': '骨架已建立: ',
    es: 'Esqueleto creado: ',
  },
  'Task name required': {
    ko: '태스크 이름 필수', ja: 'タスク名は必須です',
    'zh-CN': '任务名称为必填项', 'zh-TW': '任務名稱為必填項',
    es: 'Se requiere nombre de tarea',
  },
  'Use letters, digits, underscores only (must start with a letter)': {
    ko: '영문, 숫자, 밑줄만 사용 (문자로 시작)', ja: '英字・数字・アンダースコアのみ使用可（英字で開始）',
    'zh-CN': '仅可使用字母、数字、下划线（必须以字母开头）', 'zh-TW': '僅可使用字母、數字、底線（必須以字母開頭）',
    es: 'Use solo letras, dígitos y guiones bajos (debe comenzar con una letra)',
  },
  'Wrong password': {
    ko: '비밀번호 오류', ja: 'パスワードが間違っています',
    'zh-CN': '密码错误', 'zh-TW': '密碼錯誤',
    es: 'Contraseña incorrecta',
  },

  '(Anonymous if empty)': {
    ko: '(미입력 시 Anonymous)', ja: '(空欄の場合は Anonymous)',
    'zh-CN': '(留空则为 Anonymous)', 'zh-TW': '(留空則為 Anonymous)',
    es: '(Anónimo si está vacío)',
  },
  '(comma separated, max 5)': {
    ko: '(쉼표로 구분, 최대 5개)', ja: '(カンマ区切り、最大5個)',
    'zh-CN': '(逗号分隔，最多 5 个)', 'zh-TW': '(逗號分隔，最多 5 個)',
    es: '(separados por coma, máx. 5)',
  },
  'Community Discussion': {
    ko: '커뮤니티 토론', ja: 'コミュニティディスカッション',
    'zh-CN': '社区讨论', 'zh-TW': '社群討論',
    es: 'Discusión comunitaria',
  },
  'Content': {
    ko: '내용', ja: '内容',
    'zh-CN': '内容', 'zh-TW': '內容',
    es: 'Contenido',
  },
  'DX-M1, YOLOv8, optimization…': {
    ko: 'DX-M1, YOLOv8, 추론 최적화…', ja: 'DX-M1, YOLOv8, 最適化…',
    'zh-CN': 'DX-M1, YOLOv8, 优化…', 'zh-TW': 'DX-M1, YOLOv8, 最佳化…',
    es: 'DX-M1, YOLOv8, optimización…',
  },
  'Enter a comment…': {
    ko: '댓글을 입력하세요…', ja: 'コメントを入力…',
    'zh-CN': '输入评论…', 'zh-TW': '輸入留言…',
    es: 'Introduzca un comentario…',
  },
  'Enter a title': {
    ko: '제목을 입력하세요', ja: 'タイトルを入力',
    'zh-CN': '输入标题', 'zh-TW': '輸入標題',
    es: 'Introduzca un título',
  },
  'Enter content…': {
    ko: '내용을 입력하세요…', ja: '内容を入力…',
    'zh-CN': '输入内容…', 'zh-TW': '輸入內容…',
    es: 'Introduzca contenido…',
  },
  'Nickname': {
    ko: '닉네임', ja: 'ニックネーム',
    'zh-CN': '昵称', 'zh-TW': '暱稱',
    es: 'Apodo',
  },
  'Nickname (optional)': {
    ko: '닉네임 (선택)', ja: 'ニックネーム（任意）',
    'zh-CN': '昵称（可选）', 'zh-TW': '暱稱（選填）',
    es: 'Apodo (opcional)',
  },
  'No posts yet': {
    ko: '게시물이 없습니다', ja: 'まだ投稿がありません',
    'zh-CN': '暂无帖子', 'zh-TW': '尚無貼文',
    es: 'Aún no hay publicaciones',
  },
  'Post Comment': {
    ko: '댓글 등록', ja: 'コメント投稿',
    'zh-CN': '发表评论', 'zh-TW': '發表留言',
    es: 'Publicar comentario',
  },
  'Tags': {
    ko: '태그', ja: 'タグ',
    'zh-CN': '标签', 'zh-TW': '標籤',
    es: 'Etiquetas',
  },
  'Title': {
    ko: '제목', ja: 'タイトル',
    'zh-CN': '标题', 'zh-TW': '標題',
    es: 'Título',
  },
  'Write the first post!': {
    ko: '첫 번째 글을 작성해 보세요!', ja: '最初の投稿を書きましょう！',
    'zh-CN': '来写第一篇帖子吧！', 'zh-TW': '來撰寫第一篇貼文吧！',
    es: '¡Escriba la primera publicación!',
  },
  'Failed to load. Please check the server.': {
    ko: '불러오기 실패. 서버를 확인하세요.', ja: '読み込みに失敗しました。サーバーを確認してください。',
    'zh-CN': '加载失败，请检查服务器。', 'zh-TW': '載入失敗，請檢查伺服器。',
    es: 'Error al cargar. Por favor verifique el servidor.',
  },
  'Submit': {
    ko: '등록', ja: '送信',
    'zh-CN': '提交', 'zh-TW': '提交',
    es: 'Enviar',
  },
  'Recommend': {
    ko: '추천', ja: 'おすすめ',
    'zh-CN': '推荐', 'zh-TW': '推薦',
    es: 'Recomendar',
  },
  'Comments': {
    ko: '댓글', ja: 'コメント',
    'zh-CN': '评论', 'zh-TW': '留言',
    es: 'Comentarios',
  },

  ' (unavailable)': {
    ko: ' (사용 불가)', ja: ' (利用不可)',
    'zh-CN': ' (不可用)', 'zh-TW': ' (不可用)',
    es: ' (no disponible)',
  },
  ' running inference…': {
    ko: ' 추론 실행 중…', ja: ' 推論実行中…',
    'zh-CN': ' 正在运行推理…', 'zh-TW': ' 正在執行推論…',
    es: ' ejecutando inferencia…',
  },
  '(no model selected)': {
    ko: '(모델 미선택)', ja: '(モデル未選択)',
    'zh-CN': '(未选择模型)', 'zh-TW': '(未選擇模型)',
    es: '(ningún modelo seleccionado)',
  },
  '). Check Full Output for details.': {
    ko: '). 전체 출력을 확인하세요.', ja: ')。詳細は全出力を確認してください。',
    'zh-CN': ')。请查看完整输出了解详情。', 'zh-TW': ')。請查看完整輸出了解詳情。',
    es: '). Consulte la Salida Completa para más detalles.',
  },
  'C++ binary has not been built.': {
    ko: 'C++ 바이너리가 빌드되지 않았습니다.', ja: 'C++ バイナリがビルドされていません。',
    'zh-CN': 'C++ 二进制文件尚未构建。', 'zh-TW': 'C++ 二進位檔案尚未建置。',
    es: 'El binario C++ aún no ha sido compilado.',
  },
  'Denoising: automatically removes noise from the input image.': {
    ko: 'Denoising: 입력 이미지에서 노이즈를 자동으로 제거합니다.', ja: 'Denoising: 入力画像からノイズを自動的に除去します。',
    'zh-CN': 'Denoising：自动去除输入图像中的噪声。', 'zh-TW': 'Denoising：自動去除輸入影像中的雜訊。',
    es: 'Reducción de ruido: elimina automáticamente el ruido de la imagen de entrada.',
  },
  'Depth estimation: predicts depth for every pixel without a separate threshold.': {
    ko: 'Depth estimation: 별도의 임계값 없이 모든 픽셀의 깊이를 예측합니다.', ja: 'Depth estimation: 個別のしきい値なしで全ピクセルの深度を予測します。',
    'zh-CN': 'Depth estimation：无需单独阈值即可预测每个像素的深度。', 'zh-TW': 'Depth estimation：無需單獨閾值即可預測每個像素的深度。',
    es: 'Estimación de profundidad: predice la profundidad de cada píxel sin un umbral separado.',
  },
  'Download .tar.gz': {
    ko: '.tar.gz 다운로드', ja: '.tar.gz ダウンロード',
    'zh-CN': '下载 .tar.gz', 'zh-TW': '下載 .tar.gz',
    es: 'Descargar .tar.gz',
  },
  'Embedding: converts the image into a fixed-size feature vector.': {
    ko: 'Embedding: 이미지를 고정 크기의 특징 벡터로 변환합니다.', ja: 'Embedding: 画像を固定サイズの特徴ベクトルに変換します。',
    'zh-CN': 'Embedding：将图像转换为固定大小的特征向量。', 'zh-TW': 'Embedding：將影像轉換為固定大小的特徵向量。',
    es: 'Embedding: convierte la imagen en un vector de características de tamaño fijo.',
  },
  'Embedding: select a face pair folder (2+ images). The first image becomes the reference; later images are compared via cosine similarity.': {
    ko: 'Embedding: 얼굴 쌍 폴더(이미지 2장 이상)를 선택하세요. 첫 이미지가 기준이 되고, 이후 이미지는 코사인 유사도로 비교됩니다.', ja: 'Embedding: 顔ペアフォルダ（画像2枚以上）を選択してください。最初の画像が参照となり、以降の画像はコサイン類似度で比較されます。',
    'zh-CN': 'Embedding：选择人脸配对文件夹（2 张以上图像）。第一张为参考图，后续图像通过余弦相似度比较。', 'zh-TW': 'Embedding：選擇人臉配對資料夾（2 張以上影像）。第一張為參考圖，後續影像透過餘弦相似度比較。',
    es: 'Embedding: seleccione una carpeta de pares faciales (2+ imágenes). La primera es referencia; las siguientes se comparan por similitud coseno.',
  },
  'ReID: select a person pair folder (2+ images). The first image becomes the reference; later images are compared via cosine similarity.': {
    ko: 'ReID: 사람 쌍 폴더(이미지 2장 이상)를 선택하세요. 첫 이미지가 기준이 되고, 이후 이미지는 코사인 유사도로 비교됩니다.', ja: 'ReID: 人物ペアフォルダ（画像2枚以上）を選択してください。最初の画像が参照となり、以降の画像はコサイン類似度で比較されます。',
    'zh-CN': 'ReID：选择行人配对文件夹（2 张以上图像）。第一张为参考图，后续图像通过余弦相似度比较。', 'zh-TW': 'ReID：選擇行人配對資料夾（2 張以上影像）。第一張為參考圖，後續影像透過餘弦相似度比較。',
    es: 'ReID: seleccione una carpeta de pares de personas (2+ imágenes). La primera es referencia; las siguientes se comparan por similitud coseno.',
  },
  'Enhancement: automatically improves brightness and contrast.': {
    ko: 'Enhancement: 밝기와 대비를 자동으로 개선합니다.', ja: 'Enhancement: 明るさとコントラストを自動的に改善します。',
    'zh-CN': 'Enhancement：自动提升亮度和对比度。', 'zh-TW': 'Enhancement：自動提升亮度和對比度。',
    es: 'Mejora: mejora automáticamente el brillo y el contraste.',
  },
  'Loading…': {
    ko: '로딩 중…', ja: '読み込み中…',
    'zh-CN': '加载中…', 'zh-TW': '載入中…',
    es: 'Cargando…',
  },
  'Model file (.dxnn) does not exist. Please compile and try again.': {
    ko: '모델 파일 (.dxnn)이 존재하지 않습니다. 컴파일 후 다시 시도하세요.', ja: 'モデルファイル (.dxnn) が存在しません。コンパイルしてから再試行してください。',
    'zh-CN': '模型文件 (.dxnn) 不存在。请编译后重试。', 'zh-TW': '模型檔案 (.dxnn) 不存在。請編譯後重試。',
    es: 'El archivo de modelo (.dxnn) no existe. Por favor compile e intente de nuevo.',
  },
  'Model file not configured.': {
    ko: '모델 파일이 설정되지 않았습니다.', ja: 'モデルファイルが設定されていません。',
    'zh-CN': '模型文件未配置。', 'zh-TW': '模型檔案未設定。',
    es: 'Archivo de modelo no configurado.',
  },
  'No cameras found': {
    ko: '카메라를 찾을 수 없습니다', ja: 'カメラが見つかりません',
    'zh-CN': '未找到摄像头', 'zh-TW': '找不到攝影機',
    es: 'No se encontraron cámaras',
  },
  'No images': {
    ko: '이미지 없음', ja: '画像なし',
    'zh-CN': '无图像', 'zh-TW': '無影像',
    es: 'Sin imágenes',
  },
  'No result data.': {
    ko: '결과 데이터 없음.', ja: '結果データなし。',
    'zh-CN': '无结果数据。', 'zh-TW': '無結果資料。',
    es: 'Sin datos de resultado.',
  },
  'Package ready for download': {
    ko: '패키지 다운로드 준비 완료', ja: 'パッケージのダウンロード準備完了',
    'zh-CN': '包已准备好下载', 'zh-TW': '套件已準備好下載',
    es: 'Paquete listo para descargar',
  },
  'Passed to the model\'s config.json as the corresponding parameters': {
    ko: '모델의 config.json에 해당 파라미터로 전달됩니다', ja: 'モデルの config.json に対応するパラメータとして渡されます',
    'zh-CN': '作为对应参数传递给模型的 config.json', 'zh-TW': '作為對應參數傳遞給模型的 config.json',
    es: 'Se pasan al config.json del modelo como los parámetros correspondientes',
  },
  'Please configure model file in Developer mode.': {
    ko: 'Developer 모드에서 모델 파일을 설정하세요.', ja: 'Developer モードでモデルファイルを設定してください。',
    'zh-CN': '请在 Developer 模式下配置模型文件。', 'zh-TW': '請在 Developer 模式下設定模型檔案。',
    es: 'Por favor configure el archivo de modelo en modo Desarrollador.',
  },
  'Profiler: ': {
    ko: '프로파일러: ', ja: 'プロファイラー: ',
    'zh-CN': '性能分析器: ', 'zh-TW': '效能分析器: ',
    es: 'Perfilador: ',
  },
  'Python app not found.': {
    ko: 'Python 앱을 찾을 수 없습니다.', ja: 'Python アプリが見つかりません。',
    'zh-CN': '未找到 Python 应用。', 'zh-TW': '找不到 Python 應用程式。',
    es: 'Aplicación Python no encontrada.',
  },
  'Run <code>make</code> build first or switch to Python.': {
    ko: '먼저 <code>make</code> 빌드를 실행하거나 Python으로 전환하세요.', ja: 'まず <code>make</code> ビルドを実行するか、Python に切り替えてください。',
    'zh-CN': '请先运行 <code>make</code> 构建，或切换到 Python。', 'zh-TW': '請先執行 <code>make</code> 建置，或切換到 Python。',
    es: 'Ejecute <code>make</code> primero o cambie a Python.',
  },
  'Super-resolution: automatically upscales the input image.': {
    ko: 'Super-resolution: 입력 이미지를 자동으로 업스케일합니다.', ja: 'Super-resolution: 入力画像を自動的にアップスケールします。',
    'zh-CN': 'Super-resolution：自动放大输入图像。', 'zh-TW': 'Super-resolution：自動放大輸入影像。',
    es: 'Súper resolución: escala automáticamente la imagen de entrada.',
  },
  'Switch to C++ or add a Python app.': {
    ko: 'C++로 전환하거나 Python 앱을 추가하세요.', ja: 'C++ に切り替えるか、Python アプリを追加してください。',
    'zh-CN': '请切换到 C++ 或添加 Python 应用。', 'zh-TW': '請切換到 C++ 或新增 Python 應用程式。',
    es: 'Cambie a C++ o agregue una aplicación Python.',
  },
  'Unknown': {
    ko: '알 수 없음', ja: '不明',
    'zh-CN': '未知', 'zh-TW': '未知',
    es: 'Desconocido',
  },
  '— Select Category —': {
    ko: '— 카테고리 선택 —', ja: '— カテゴリ選択 —',
    'zh-CN': '— 选择类别 —', 'zh-TW': '— 選擇類別 —',
    es: '— Seleccionar categoría —',
  },
  'No result video was generated': {
    ko: '결과 비디오가 생성되지 않았습니다', ja: '結果ビデオが生成されませんでした',
    'zh-CN': '未生成结果视频', 'zh-TW': '未產生結果影片',
    es: 'No se generó video de resultado',
  },
  'Waiting…': {
    ko: '대기 중…', ja: '待機中…',
    'zh-CN': '等待中…', 'zh-TW': '等待中…',
    es: 'Esperando…',
  },
  'Press Start to begin inference': {
    ko: '시작 버튼을 눌러 추론을 시작하세요', ja: '開始ボタンを押して推論を開始してください',
    'zh-CN': '按“开始”按钮以开始推理', 'zh-TW': '按「開始」按鈕以開始推論',
    es: 'Presione Iniciar para comenzar la inferencia',
  },
  'Inference exited abnormally (exit code: ': {
    ko: '추론이 비정상적으로 종료되었습니다 (종료 코드: ', ja: '推論が異常終了しました（終了コード: ',
    'zh-CN': '推理异常退出（退出代码: ', 'zh-TW': '推論異常結束（結束代碼: ',
    es: 'La inferencia terminó de forma anormal (código de salida: ',
  },
  'Extraction complete! Output: ': {
    ko: '추출 완료! 출력:', ja: '抽出完了！出力:',
    'zh-CN': '提取完成！输出:', 'zh-TW': '擷取完成！輸出:',
    es: '¡Extracción completa! Salida:',
  },
  'Enhancement Result: outputs the image with improved brightness and contrast.': {
    ko: 'Enhancement 결과: 밝기와 대비가 개선된 이미지를 출력합니다.', ja: 'Enhancement 結果: 明るさとコントラストが改善された画像を出力します。',
    'zh-CN': 'Enhancement 结果：输出亮度和对比度增强后的图像。', 'zh-TW': 'Enhancement 結果：輸出亮度和對比度增強後的影像。',
    es: 'Resultado de mejora: genera la imagen con brillo y contraste mejorados.',
  },
  'Depth Result: visualizes depth using JET colormap (red=near, blue=far).': {
    ko: 'Depth 결과: JET 컬러맵으로 깊이를 시각화합니다 (빨강=가까움, 파랑=멀리).', ja: 'Depth 結果: JET カラーマップで深度を可視化します（赤=近い、青=遠い）。',
    'zh-CN': 'Depth 结果：使用 JET 色图可视化深度（红色=近，蓝色=远）。', 'zh-TW': 'Depth 結果：使用 JET 色圖視覺化深度（紅色=近，藍色=遠）。',
    es: 'Resultado de profundidad: visualiza la profundidad usando el mapa de colores JET (rojo=cerca, azul=lejos).',
  },
  'Semantic Segmentation: alpha-blends per-pixel class labels using Cityscapes colormap onto the original.': {
    ko: 'Semantic Segmentation: Cityscapes 컬러맵을 사용하여 픽셀별 클래스 레이블을 원본에 알파 블렌딩합니다.', ja: 'Semantic Segmentation: Cityscapes カラーマップを使用してピクセルごとのクラスラベルを元画像にアルファブレンドします。',
    'zh-CN': 'Semantic Segmentation：使用 Cityscapes 色图将逐像素类别标签与原图进行 Alpha 混合。', 'zh-TW': 'Semantic Segmentation：使用 Cityscapes 色圖將逐像素類別標籤與原圖進行 Alpha 混合。',
    es: 'Segmentación semántica: mezcla alfa de etiquetas de clase por píxel usando el mapa de colores Cityscapes sobre la imagen original.',
  },
  'Instance Segmentation: draws per-instance color masks + bounding boxes + class labels.': {
    ko: 'Instance Segmentation: 인스턴스별 컬러 마스크 + 바운딩 박스 + 클래스 레이블을 표시합니다.', ja: 'Instance Segmentation: インスタンスごとのカラーマスク＋バウンディングボックス＋クラスラベルを描画します。',
    'zh-CN': 'Instance Segmentation：绘制逐实例颜色掩码 + 边界框 + 类别标签。', 'zh-TW': 'Instance Segmentation：繪製逐實例顏色遮罩 + 邊界框 + 類別標籤。',
    es: 'Segmentación de instancias: dibuja máscaras de color por instancia + cuadros delimitadores + etiquetas de clase.',
  },
  'Pose Estimation: draws skeleton (joint connections) and keypoints. Low-confidence keypoints may be omitted.': {
    ko: 'Pose Estimation: 스켈레톤(관절 연결)과 키포인트를 표시합니다. 신뢰도가 낮은 키포인트는 생략될 수 있습니다.', ja: 'Pose Estimation: スケルトン（関節接続）とキーポイントを描画します。信頼度の低いキーポイントは省略される場合があります。',
    'zh-CN': 'Pose Estimation：绘制骨架（关节连接）和关键点。低置信度关键点可能会被省略。', 'zh-TW': 'Pose Estimation：繪製骨架（關節連接）和關鍵點。低信賴度關鍵點可能會被省略。',
    es: 'Estimación de pose: dibuja el esqueleto (conexiones articulares) y puntos clave. Los puntos clave de baja confianza pueden omitirse.',
  },
  'Classification Result: overlays Top-K predicted classes and probabilities as text on the image.': {
    ko: 'Classification 결과: Top-K 예측 클래스와 확률을 이미지 위에 텍스트로 표시합니다.', ja: 'Classification 結果: Top-K 予測クラスと確率をテキストとして画像上にオーバーレイします。',
    'zh-CN': 'Classification 结果：将 Top-K 预测类别和概率以文本形式叠加在图像上。', 'zh-TW': 'Classification 結果：將 Top-K 預測類別和機率以文字形式疊加在影像上。',
    es: 'Resultado de clasificación: superpone las clases predichas Top-K y sus probabilidades como texto en la imagen.',
  },
  'Attribute Result: overlays predicted person/face attributes and confidence scores on the image.': {
    ko: 'Attribute 결과: 예측된 사람/얼굴 속성과 신뢰도 점수를 이미지 위에 텍스트로 표시합니다.', ja: 'Attribute 結果: 予測された人物/顔属性と信頼度スコアを画像上にテキストでオーバーレイします。',
    'zh-CN': 'Attribute 结果：将预测的人物/面部属性和置信度分数以文本形式叠加在图像上。', 'zh-TW': 'Attribute 結果：將預測的人物/臉部屬性和信賴度分數以文字形式疊加在影像上。',
    es: 'Resultado de atributos: superpone los atributos de persona/rostro predichos y sus puntuaciones de confianza como texto en la imagen.',
  },
  'Task Summary (': {
    ko: '태스크 요약 (', ja: 'タスク概要 (',
    'zh-CN': '任务摘要 (', 'zh-TW': '任務摘要 (',
    es: 'Resumen de tareas (',
  },
  'Embedding Result: side-by-side reference vs current image with cosine similarity (SAME / DIFFERENT).': {
    ko: 'Embedding 결과: 기준/현재 이미지를 나란히 표시하고 코사인 유사도(SAME / DIFFERENT)를 보여줍니다.', ja: 'Embedding 結果: 参照画像と現在画像を並べて表示し、コサイン類似度（SAME / DIFFERENT）を示します。',
    'zh-CN': 'Embedding 结果：并排显示参考图与当前图，并展示余弦相似度（SAME / DIFFERENT）。', 'zh-TW': 'Embedding 結果：並排顯示參考圖與目前圖，並展示餘弦相似度（SAME / DIFFERENT）。',
    es: 'Resultado de embedding: muestra referencia y actual lado a lado con similitud coseno (SAME / DIFFERENT).',
  },
  'ReID Result: side-by-side reference vs current image with cosine similarity (SAME / DIFFERENT).': {
    ko: 'ReID 결과: 기준/현재 이미지를 나란히 표시하고 코사인 유사도(SAME / DIFFERENT)를 보여줍니다.', ja: 'ReID 結果: 参照画像と現在画像を並べて表示し、コサイン類似度（SAME / DIFFERENT）を示します。',
    'zh-CN': 'ReID 结果：并排显示参考图与当前图，并展示余弦相似度（SAME / DIFFERENT）。', 'zh-TW': 'ReID 結果：並排顯示參考圖與目前圖，並展示餘弦相似度（SAME / DIFFERENT）。',
    es: 'Resultado ReID: muestra referencia y actual lado a lado con similitud coseno (SAME / DIFFERENT).',
  },
  'Denoising Result: outputs the denoised image. DnCNN may process in grayscale (Y channel).': {
    ko: 'Denoising 결과: 노이즈가 제거된 이미지를 출력합니다. DnCNN은 그레이스케일(Y 채널)로 처리할 수 있습니다.', ja: 'Denoising 結果: ノイズ除去された画像を出力します。DnCNN はグレースケール（Yチャネル）で処理する場合があります。',
    'zh-CN': 'Denoising 结果：输出去噪后的图像。DnCNN 可能以灰度（Y 通道）处理。', 'zh-TW': 'Denoising 結果：輸出去噪後的影像。DnCNN 可能以灰階（Y 通道）處理。',
    es: 'Resultado de eliminación de ruido: genera la imagen sin ruido. DnCNN puede procesar en escala de grises (canal Y).',
  },
  'Super Resolution Result: outputs the upscaled image. ESPCN processes the Y channel and restores color.': {
    ko: 'Super Resolution 결과: 업스케일된 이미지를 출력합니다. ESPCN은 Y 채널을 처리하고 색상을 복원합니다.', ja: 'Super Resolution 結果: アップスケールされた画像を出力します。ESPCN は Y チャネルを処理し、色を復元します。',
    'zh-CN': 'Super Resolution 结果：输出放大后的图像。ESPCN 处理 Y 通道并恢复色彩。', 'zh-TW': 'Super Resolution 結果：輸出放大後的影像。ESPCN 處理 Y 通道並恢復色彩。',
    es: 'Resultado de super resolución: genera la imagen escalada. ESPCN procesa el canal Y y restaura el color.',
  },
  'Face Alignment: draws 3D facial landmark points.': {
    ko: 'Face Alignment: 3D 얼굴 랜드마크 포인트를 표시합니다.', ja: 'Face Alignment: 3D 顔ランドマークポイントを描画します。',
    'zh-CN': 'Face Alignment：绘制 3D 面部特征点。', 'zh-TW': 'Face Alignment：繪製 3D 臉部特徵點。',
    es: 'Alineación facial: dibuja puntos de referencia faciales 3D.',
  },
  'Hand Landmark: draws 21 hand landmark points and connections.': {
    ko: 'Hand Landmark: 21개의 손 랜드마크 포인트와 연결을 표시합니다.', ja: 'Hand Landmark: 21個の手のランドマークポイントと接続を描画します。',
    'zh-CN': 'Hand Landmark：绘制 21 个手部特征点及其连接。', 'zh-TW': 'Hand Landmark：繪製 21 個手部特徵點及其連接。',
    es: 'Puntos de referencia de mano: dibuja 21 puntos de referencia y conexiones de la mano.',
  },

  ' models': {
    ko: ' 모델', ja: ' モデル',
    'zh-CN': ' 个模型', 'zh-TW': ' 個模型',
    es: ' modelos',
  },
  'Alpha-blends per-pixel class labels using the Cityscapes colormap.': {
    ko: 'Cityscapes 컬러맵을 사용하여 픽셀별 클래스 레이블을 알파 블렌딩합니다.', ja: 'Cityscapes カラーマップを使用してピクセルごとのクラスラベルをアルファブレンドします。',
    'zh-CN': '使用 Cityscapes 色图对逐像素类别标签进行 Alpha 混合。', 'zh-TW': '使用 Cityscapes 色圖對逐像素類別標籤進行 Alpha 混合。',
    es: 'Mezcla alfa por píxel las etiquetas de clase usando el mapa de colores Cityscapes.',
  },
  'ArcFace face recognition embedding. Additive angular margin.': {
    ko: 'ArcFace 얼굴 인식 임베딩. Additive angular margin 방식.', ja: 'ArcFace 顔認識エンベディング。加法角度マージン方式。',
    'zh-CN': 'ArcFace 人脸识别嵌入。加性角度间隔方法。', 'zh-TW': 'ArcFace 人臉辨識嵌入。加性角度間距方法。',
    es: 'Incrustación de reconocimiento facial ArcFace. Margen angular aditivo.',
  },
  'BiSeNetV1 real-time semantic segmentation. Spatial + Context path.': {
    ko: 'BiSeNetV1 실시간 의미론적 분할. Spatial + Context 경로.', ja: 'BiSeNetV1 リアルタイムセマンティックセグメンテーション。Spatial + Context パス。',
    'zh-CN': 'BiSeNetV1 实时语义分割。Spatial + Context 路径。', 'zh-TW': 'BiSeNetV1 即時語意分割。Spatial + Context 路徑。',
    es: 'Segmentación semántica en tiempo real BiSeNetV1. Rutas Spatial + Context.',
  },
  'BiSeNetV2 real-time semantic segmentation. Detail + Semantic branch.': {
    ko: 'BiSeNetV2 실시간 의미론적 분할. Detail + Semantic 브랜치.', ja: 'BiSeNetV2 リアルタイムセマンティックセグメンテーション。Detail + Semantic ブランチ。',
    'zh-CN': 'BiSeNetV2 实时语义分割。Detail + Semantic 分支。', 'zh-TW': 'BiSeNetV2 即時語意分割。Detail + Semantic 分支。',
    es: 'Segmentación semántica en tiempo real BiSeNetV2. Ramas Detail + Semantic.',
  },
  'CLIP image encoder. Vision-Language contrastive learning.': {
    ko: 'CLIP 이미지 인코더. Vision-Language 대조 학습.', ja: 'CLIP 画像エンコーダー。Vision-Language 対照学習。',
    'zh-CN': 'CLIP 图像编码器。Vision-Language 对比学习。', 'zh-TW': 'CLIP 影像編碼器。Vision-Language 對比學習。',
    es: 'Codificador de imagen CLIP. Aprendizaje contrastivo visión-lenguaje.',
  },
  'CLIP text encoder. Vision-Language contrastive learning.': {
    ko: 'CLIP 텍스트 인코더. Vision-Language 대조 학습.', ja: 'CLIP テキストエンコーダー。Vision-Language 対照学習。',
    'zh-CN': 'CLIP 文本编码器。Vision-Language 对比学习。', 'zh-TW': 'CLIP 文字編碼器。Vision-Language 對比學習。',
    es: 'Codificador de texto CLIP. Aprendizaje contrastivo visión-lenguaje.',
  },
  'CenterNet center-point based detection. Heatmap + offset prediction.': {
    ko: 'CenterNet 중심점 기반 검출. Heatmap + offset 예측.', ja: 'CenterNet センターポイントベース検出。Heatmap + offset 予測。',
    'zh-CN': 'CenterNet 基于中心点的检测。Heatmap + offset 预测。', 'zh-TW': 'CenterNet 基於中心點的偵測。Heatmap + offset 預測。',
    es: 'Detección basada en puntos centrales CenterNet. Mapa de calor + predicción de desplazamiento.',
  },
  'CenterPose center-point based pose estimation. Heatmap + keypoint offset.': {
    ko: 'CenterPose 중심점 기반 자세 추정. Heatmap + keypoint offset.', ja: 'CenterPose センターポイントベース姿勢推定。Heatmap + keypoint offset。',
    'zh-CN': 'CenterPose 基于中心点的姿态估计。Heatmap + keypoint offset。', 'zh-TW': 'CenterPose 基於中心點的姿態估計。Heatmap + keypoint offset。',
    es: 'Estimación de pose basada en puntos centrales CenterPose. Mapa de calor + desplazamiento de puntos clave.',
  },
  'Classes': {
    ko: '클래스', ja: 'クラス',
    'zh-CN': '类别', 'zh-TW': '類別',
    es: 'Clases',
  },
  'Converts the depth map to JET colormap and alpha-blends it with the original.': {
    ko: '깊이 맵을 JET 컬러맵으로 변환하고 원본과 알파 블렌딩합니다.', ja: '深度マップを JET カラーマップに変換し、元画像とアルファブレンドします。',
    'zh-CN': '将深度图转换为 JET 色图，并与原图进行 Alpha 混合。', 'zh-TW': '將深度圖轉換為 JET 色圖，並與原圖進行 Alpha 混合。',
    es: 'Convierte el mapa de profundidad a mapa de colores JET y lo mezcla alfa con el original.',
  },
  'DAMO-YOLO high-efficiency object detection. AlignedOTA label assignment.': {
    ko: 'DAMO-YOLO 고효율 객체 검출. AlignedOTA 레이블 할당.', ja: 'DAMO-YOLO 高効率物体検出。AlignedOTA ラベル割り当て。',
    'zh-CN': 'DAMO-YOLO 高效目标检测。AlignedOTA 标签分配。', 'zh-TW': 'DAMO-YOLO 高效物件偵測。AlignedOTA 標籤分配。',
    es: 'Detección de objetos de alta eficiencia DAMO-YOLO. Asignación de etiquetas AlignedOTA.',
  },
  'DeepLabV3 semantic segmentation. Atrous convolution, ASPP.': {
    ko: 'DeepLabV3 의미론적 분할. Atrous 컨볼루션, ASPP.', ja: 'DeepLabV3 セマンティックセグメンテーション。Atrous 畳み込み、ASPP。',
    'zh-CN': 'DeepLabV3 语义分割。空洞卷积、ASPP。', 'zh-TW': 'DeepLabV3 語意分割。空洞卷積、ASPP。',
    es: 'Segmentación semántica DeepLabV3. Convolución atrous, ASPP.',
  },
  'Displays PPU pipeline results.': {
    ko: 'PPU 파이프라인 결과를 표시합니다.', ja: 'PPU パイプラインの結果を表示します。',
    'zh-CN': '显示 PPU 管线结果。', 'zh-TW': '顯示 PPU 管線結果。',
    es: 'Muestra los resultados del pipeline PPU.',
  },
  'Displays embedding vector info (dimension, value preview, L2 norm) as text.': {
    ko: '임베딩 벡터 정보(차원, 값 미리보기, L2 노름)를 텍스트로 표시합니다.', ja: 'エンベディングベクトル情報（次元、値プレビュー、L2ノルム）をテキストで表示します。',
    'zh-CN': '以文本形式显示嵌入向量信息（维度、值预览、L2 范数）。', 'zh-TW': '以文字形式顯示嵌入向量資訊（維度、值預覽、L2 範數）。',
    es: 'Muestra información del vector de embedding (dimensión, vista previa de valores, norma L2) como texto.',
  },
  'DnCNN image denoising. Residual learning based.': {
    ko: 'DnCNN 이미지 노이즈 제거. 잔차 학습 기반.', ja: 'DnCNN 画像ノイズ除去。残差学習ベース。',
    'zh-CN': 'DnCNN 图像去噪。基于残差学习。', 'zh-TW': 'DnCNN 影像去噪。基於殘差學習。',
    es: 'Eliminación de ruido de imagen DnCNN. Basado en aprendizaje residual.',
  },
  'Draws 21 hand landmark points and connections.': {
    ko: '21개의 손 랜드마크 포인트와 연결을 표시합니다.', ja: '21個の手のランドマークポイントと接続を描画します。',
    'zh-CN': '绘制 21 个手部特征点及其连接。', 'zh-TW': '繪製 21 個手部特徵點及其連接。',
    es: 'Dibuja 21 puntos de referencia de la mano y conexiones.',
  },
  'Draws bounding boxes and per-instance color masks.': {
    ko: '바운딩 박스와 인스턴스별 컬러 마스크를 표시합니다.', ja: 'バウンディングボックスとインスタンスごとのカラーマスクを描画します。',
    'zh-CN': '绘制边界框和逐实例颜色掩码。', 'zh-TW': '繪製邊界框和逐實例顏色遮罩。',
    es: 'Dibuja cajas delimitadoras y máscaras de color por instancia.',
  },
  'Draws bounding boxes around detected hands.': {
    ko: '검출된 손 주위에 바운딩 박스를 표시합니다.', ja: '検出された手の周囲にバウンディングボックスを描画します。',
    'zh-CN': '在检测到的手部周围绘制边界框。', 'zh-TW': '在偵測到的手部周圍繪製邊界框。',
    es: 'Dibuja cajas delimitadoras alrededor de las manos detectadas.',
  },
  'Draws bounding boxes with class labels and confidence scores.': {
    ko: '클래스 레이블과 신뢰도 점수가 포함된 바운딩 박스를 표시합니다.', ja: 'クラスラベルと信頼度スコア付きのバウンディングボックスを描画します。',
    'zh-CN': '绘制带有类别标签和置信度分数的边界框。', 'zh-TW': '繪製帶有類別標籤和信賴度分數的邊界框。',
    es: 'Dibuja cajas delimitadoras con etiquetas de clase y puntuaciones de confianza.',
  },
  'Draws detected keypoints (interest points) on the image.': {
    ko: '검출된 키포인트(관심 지점)를 이미지 위에 표시합니다.', ja: '検出されたキーポイント（興味点）を画像上に描画します。',
    'zh-CN': '在图像上绘制检测到的关键点（兴趣点）。', 'zh-TW': '在影像上繪製偵測到的關鍵點（興趣點）。',
    es: 'Dibuja los puntos clave detectados (puntos de interés) en la imagen.',
  },
  'Draws face alignment landmark points.': {
    ko: '얼굴 정렬 랜드마크 포인트를 표시합니다.', ja: '顔アラインメントランドマークポイントを描画します。',
    'zh-CN': '绘制面部对齐特征点。', 'zh-TW': '繪製臉部對齊特徵點。',
    es: 'Dibuja puntos de referencia de alineación facial.',
  },
  'Draws face bounding boxes and landmark points.': {
    ko: '얼굴 바운딩 박스와 랜드마크 포인트를 표시합니다.', ja: '顔のバウンディングボックスとランドマークポイントを描画します。',
    'zh-CN': '绘制面部边界框和特征点。', 'zh-TW': '繪製臉部邊界框和特徵點。',
    es: 'Dibuja cajas delimitadoras faciales y puntos de referencia.',
  },
  'Draws oriented (rotated) bounding boxes.': {
    ko: '방향이 지정된(회전된) 바운딩 박스를 표시합니다.', ja: '回転バウンディングボックスを描画します。',
    'zh-CN': '绘制旋转边界框。', 'zh-TW': '繪製旋轉邊界框。',
    es: 'Dibuja cajas delimitadoras orientadas (rotadas).',
  },
  'Draws skeleton (joint connections) and keypoints.': {
    ko: '스켈레톤(관절 연결)과 키포인트를 표시합니다.', ja: 'スケルトン（関節接続）とキーポイントを描画します。',
    'zh-CN': '绘制骨架（关节连接）和关键点。', 'zh-TW': '繪製骨架（關節連接）和關鍵點。',
    es: 'Dibuja esqueleto (conexiones articulares) y puntos clave.',
  },
  'Draws the projected 3D bounding box and 6-DoF pose of the object.': {
    ko: '객체의 투영된 3D 바운딩 박스와 6-DoF 포즈를 표시합니다.', ja: 'オブジェクトの投影された 3D バウンディングボックスと 6-DoF 姿勢を描画します。',
    'zh-CN': '绘制物体的投影 3D 边界框和 6-DoF 姿态。', 'zh-TW': '繪製物體的投影 3D 邊界框和 6-DoF 姿態。',
    es: 'Dibuja la caja delimitadora 3D proyectada y la pose 6-DoF del objeto.',
  },
  'ESPCN super-resolution. Sub-pixel convolution layer.': {
    ko: 'ESPCN 초해상도. Sub-pixel 컨볼루션 레이어.', ja: 'ESPCN 超解像。Sub-pixel 畳み込み層。',
    'zh-CN': 'ESPCN 超分辨率。Sub-pixel 卷积层。', 'zh-TW': 'ESPCN 超解析度。Sub-pixel 卷積層。',
    es: 'Super-resolución ESPCN. Capa de convolución sub-píxel.',
  },
  'EfficientDet object detection with BiFPN.': {
    ko: 'EfficientDet 객체 검출 (BiFPN 사용).', ja: 'EfficientDet 物体検出（BiFPN 使用）。',
    'zh-CN': 'EfficientDet 目标检测（使用 BiFPN）。', 'zh-TW': 'EfficientDet 物件偵測（使用 BiFPN）。',
    es: 'Detección de objetos EfficientDet con BiFPN.',
  },
  'EfficientNet image classification. Outputs Top-K probabilities.': {
    ko: 'EfficientNet 이미지 분류. Top-K 확률 출력.', ja: 'EfficientNet 画像分類。Top-K 確率を出力。',
    'zh-CN': 'EfficientNet 图像分类。输出 Top-K 概率。', 'zh-TW': 'EfficientNet 影像分類。輸出 Top-K 機率。',
    es: 'EfficientNet clasificación de imágenes. Genera Top-K probabilidades.',
  },
  'Failed to read file': {
    ko: '파일을 읽지 못했습니다', ja: 'ファイルの読み込みに失敗しました',
    'zh-CN': '读取文件失败', 'zh-TW': '讀取檔案失敗',
    es: 'Error al leer el archivo',
  },
  'FastDepth monocular depth estimation. Depthwise separable convolution.': {
    ko: 'FastDepth 단안 깊이 추정. Depthwise separable 컨볼루션.', ja: 'FastDepth 単眼深度推定。Depthwise separable 畳み込み。',
    'zh-CN': 'FastDepth 单目深度估计。Depthwise separable 卷积。', 'zh-TW': 'FastDepth 單目深度估計。Depthwise separable 卷積。',
    es: 'Estimación de profundidad monocular FastDepth. Convolución separable en profundidad.',
  },
  'Image ready — press Run': {
    ko: '이미지 준비됨 — 실행을 누르세요', ja: '画像の準備ができました — 実行を押してください',
    'zh-CN': '图像已就绪 — 请按运行', 'zh-TW': '影像已就緒 — 請按執行',
    es: 'Imagen lista — pulse Ejecutar',
  },
  'Image too large (max 8MB)': {
    ko: '이미지가 너무 큽니다 (최대 8MB)', ja: '画像が大きすぎます（最大 8MB）',
    'zh-CN': '图像过大（最大 8MB）', 'zh-TW': '影像過大（最大 8MB）',
    es: 'Imagen demasiado grande (máx. 8 MB)',
  },
  'Input Size': {
    ko: '입력 크기', ja: '入力サイズ',
    'zh-CN': '输入大小', 'zh-TW': '輸入大小',
    es: 'Tamaño de entrada',
  },
  'Model File': {
    ko: '모델 파일', ja: 'モデルファイル',
    'zh-CN': '模型文件', 'zh-TW': '模型檔案',
    es: 'Archivo de modelo',
  },
  'NMS Thresh': {
    ko: 'NMS 임계값', ja: 'NMS しきい値',
    'zh-CN': 'NMS 阈值', 'zh-TW': 'NMS 閾值',
    es: 'Umbral NMS',
  },
  'NPU Core': {
    ko: 'NPU 코어', ja: 'NPU コア',
    'zh-CN': 'NPU 核心', 'zh-TW': 'NPU 核心',
    es: 'Núcleo NPU',
  },
  'NanoDet lightweight object detector. Uses GFL head.': {
    ko: 'NanoDet 경량 객체 검출기. GFL head 사용.', ja: 'NanoDet 軽量物体検出器。GFL ヘッド使用。',
    'zh-CN': 'NanoDet 轻量级目标检测器。使用 GFL head。', 'zh-TW': 'NanoDet 輕量級物件偵測器。使用 GFL head。',
    es: 'Detector de objetos ligero NanoDet. Usa cabezal GFL.',
  },
  'Obj Thresh': {
    ko: '객체 임계값', ja: 'オブジェクトしきい値',
    'zh-CN': '目标阈值', 'zh-TW': '目標閾值',
    es: 'Umbral de obj.',
  },
  'Outputs the denoised result image directly.': {
    ko: '노이즈 제거된 결과 이미지를 직접 출력합니다.', ja: 'ノイズ除去された結果画像を直接出力します。',
    'zh-CN': '直接输出去噪后的结果图像。', 'zh-TW': '直接輸出去噪後的結果影像。',
    es: 'Genera directamente la imagen resultante sin ruido.',
  },
  'Outputs the enhanced image directly.': {
    ko: '향상된 이미지를 직접 출력합니다.', ja: '強化された画像を直接出力します。',
    'zh-CN': '直接输出增强后的图像。', 'zh-TW': '直接輸出增強後的影像。',
    es: 'Genera la imagen mejorada directamente.',
  },
  'Outputs the super-resolved result image.': {
    ko: '초해상도 처리된 결과 이미지를 출력합니다.', ja: '超解像処理された結果画像を出力します。',
    'zh-CN': '输出超分辨率处理后的结果图像。', 'zh-TW': '輸出超解析度處理後的結果影像。',
    es: 'Genera la imagen de súper resolución resultante.',
  },
  'Overlays drivable area, lane lines, and vehicle detections on the driving scene.': {
    ko: '주행 가능 영역, 차선, 차량 검출 결과를 주행 장면 위에 오버레이합니다.', ja: '走行可能領域、車線、車両検出結果を走行シーン上にオーバーレイします。',
    'zh-CN': '在行驶场景上叠加可行驶区域、车道线和车辆检测结果。', 'zh-TW': '在行駛場景上疊加可行駛區域、車道線和車輛偵測結果。',
    es: 'Superpone el área transitable, las líneas de carril y las detecciones de vehículos en la escena de conducción.',
  },
  'Overlays Top-K class predictions as text on the image.': {
    ko: 'Top-K 클래스 예측을 이미지 위에 텍스트로 오버레이합니다.', ja: 'Top-K クラス予測をテキストとして画像上にオーバーレイします。',
    'zh-CN': '将 Top-K 类别预测以文本形式叠加在图像上。', 'zh-TW': '將 Top-K 類別預測以文字形式疊加在影像上。',
    es: 'Superpone predicciones Top-K de clase como texto en la imagen.',
  },
  'Please select or upload an image': {
    ko: '이미지를 선택하거나 업로드하세요', ja: '画像を選択またはアップロードしてください',
    'zh-CN': '请选择或上传图像', 'zh-TW': '請選擇或上傳影像',
    es: 'Por favor seleccione o cargue una imagen',
  },
  'Post-processor: ': {
    ko: '후처리기: ', ja: 'ポストプロセッサー: ',
    'zh-CN': '后处理器: ', 'zh-TW': '後處理器: ',
    es: 'Post-procesador: ',
  },
  'Renders 3D bounding boxes on the LiDAR bird\'s-eye-view.': {
    ko: 'LiDAR 조감도에 3D 바운딩 박스를 렌더링합니다.', ja: 'LiDAR の俯瞰図に 3D バウンディングボックスをレンダリングします。',
    'zh-CN': '在 LiDAR 鸟瞰图上渲染 3D 边界框。', 'zh-TW': '在 LiDAR 鳥瞰圖上繪製 3D 邊界框。',
    es: 'Renderiza cajas delimitadoras 3D en la vista aérea del LiDAR.',
  },
  'RetinaFace face detection. FPN + multi-task learning (landmark).': {
    ko: 'RetinaFace 얼굴 검출. FPN + 멀티태스크 학습 (landmark).', ja: 'RetinaFace 顔検出。FPN + マルチタスク学習（landmark）。',
    'zh-CN': 'RetinaFace 人脸检测。FPN + 多任务学习（landmark）。', 'zh-TW': 'RetinaFace 人臉偵測。FPN + 多任務學習（landmark）。',
    es: 'RetinaFace detección de rostros. FPN + aprendizaje multitarea (puntos de referencia).',
  },
  'Rotated bounding box (OBB) detection. Oriented region prediction.': {
    ko: '회전 바운딩 박스 (OBB) 검출. 방향 영역 예측.', ja: '回転バウンディングボックス（OBB）検出。方向領域予測。',
    'zh-CN': '旋转边界框 (OBB) 检测。定向区域预测。', 'zh-TW': '旋轉邊界框 (OBB) 偵測。定向區域預測。',
    es: 'Detección de cuadros delimitadores rotados (OBB). Predicción de región orientada.',
  },
  'SCRFD high-efficiency face detection. Multi-task learning.': {
    ko: 'SCRFD 고효율 얼굴 검출. 멀티태스크 학습.', ja: 'SCRFD 高効率顔検出。マルチタスク学習。',
    'zh-CN': 'SCRFD 高效人脸检测。多任务学习。', 'zh-TW': 'SCRFD 高效人臉偵測。多任務學習。',
    es: 'Detección facial de alta eficiencia SCRFD. Aprendizaje multi-tarea.',
  },
  'Score Thresh': {
    ko: '점수 임계값', ja: 'スコアしきい値',
    'zh-CN': '分数阈值', 'zh-TW': '分數閾值',
    es: 'Umbral de puntuación',
  },
  'SegFormer Transformer-based semantic segmentation. Mix-FFN.': {
    ko: 'SegFormer Transformer 기반 의미론적 분할. Mix-FFN.', ja: 'SegFormer Transformer ベースのセマンティックセグメンテーション。Mix-FFN。',
    'zh-CN': 'SegFormer 基于 Transformer 的语义分割。Mix-FFN。', 'zh-TW': 'SegFormer 基於 Transformer 的語意分割。Mix-FFN。',
    es: 'Segmentación semántica basada en Transformer SegFormer. Mix-FFN.',
  },
  'Single Shot Detector. Multi-scale feature map based detection.': {
    ko: 'Single Shot Detector. 멀티스케일 특징 맵 기반 검출.', ja: 'Single Shot Detector。マルチスケール特徴マップベースの検出。',
    'zh-CN': 'Single Shot Detector。基于多尺度特征图的检测。', 'zh-TW': 'Single Shot Detector。基於多尺度特徵圖的偵測。',
    es: 'Single Shot Detector. Detección basada en mapas de características multiescala.',
  },
  'Ultra-Light-Fast face detection. Lightweight mobile network.': {
    ko: 'Ultra-Light-Fast 얼굴 검출. 경량 모바일 네트워크.', ja: 'Ultra-Light-Fast 顔検出。軽量モバイルネットワーク。',
    'zh-CN': 'Ultra-Light-Fast 人脸检测。轻量级移动网络。', 'zh-TW': 'Ultra-Light-Fast 人臉偵測。輕量級行動網路。',
    es: 'Detección facial Ultra-Light-Fast. Red móvil ligera.',
  },
  'YOLACT real-time instance segmentation. Prototype mask + linear combination.': {
    ko: 'YOLACT 실시간 인스턴스 분할. Prototype mask + 선형 결합.', ja: 'YOLACT リアルタイムインスタンスセグメンテーション。Prototype mask + 線形結合。',
    'zh-CN': 'YOLACT 实时实例分割。Prototype mask + 线性组合。', 'zh-TW': 'YOLACT 即時實例分割。Prototype mask + 線性組合。',
    es: 'Segmentación de instancias en tiempo real YOLACT. Máscara prototipo + combinación lineal.',
  },
  'YOLOX anchor-free object detection. Decoupled head with NMS post-processing.': {
    ko: 'YOLOX 앵커 프리 객체 검출. Decoupled head, NMS 후처리.', ja: 'YOLOX アンカーフリー物体検出。Decoupled head、NMS 後処理。',
    'zh-CN': 'YOLOX 无锚框目标检测。Decoupled head，NMS 后处理。', 'zh-TW': 'YOLOX 無錨框物件偵測。Decoupled head，NMS 後處理。',
    es: 'Detección de objetos sin anclas YOLOX. Cabezal desacoplado con postprocesado NMS.',
  },
  'YOLOv10-based object detection. NMS-free design.': {
    ko: 'YOLOv10 기반 객체 검출. NMS-free 설계.', ja: 'YOLOv10 ベースの物体検出。NMS フリー設計。',
    'zh-CN': 'YOLOv10 目标检测。NMS-free 设计。', 'zh-TW': 'YOLOv10 物件偵測。NMS-free 設計。',
    es: 'Detección de objetos basada en YOLOv10. Diseño sin NMS.',
  },
  'YOLOv11-based object detection. C3k2 blocks with NMS post-processing.': {
    ko: 'YOLOv11 기반 객체 검출. C3k2 블록, NMS 후처리.', ja: 'YOLOv11 ベースの物体検出。C3k2 ブロック、NMS 後処理。',
    'zh-CN': 'YOLOv11 目标检测。C3k2 模块，NMS 后处理。', 'zh-TW': 'YOLOv11 物件偵測。C3k2 區塊，NMS 後處理。',
    es: 'Detección de objetos basada en YOLOv11. Bloques C3k2 con postprocesado NMS.',
  },
  'YOLOv12-based object detection. Attention-based with NMS post-processing.': {
    ko: 'YOLOv12 기반 객체 검출. Attention 기반, NMS 후처리.', ja: 'YOLOv12 ベースの物体検出。Attention ベース、NMS 後処理。',
    'zh-CN': 'YOLOv12 目标检测。基于 Attention，NMS 后处理。', 'zh-TW': 'YOLOv12 物件偵測。基於 Attention，NMS 後處理。',
    es: 'Detección de objetos basada en YOLOv12. Basada en atención con postprocesado NMS.',
  },
  'YOLOv26-based object detection. Latest YOLO architecture with NMS post-processing.': {
    ko: 'YOLOv26 기반 객체 검출. 최신 YOLO 아키텍처, NMS 후처리.', ja: 'YOLOv26 ベースの物体検出。最新 YOLO アーキテクチャ、NMS 後処理。',
    'zh-CN': 'YOLOv26 目标检测。最新 YOLO 架构，NMS 后处理。', 'zh-TW': 'YOLOv26 物件偵測。最新 YOLO 架構，NMS 後處理。',
    es: 'Detección de objetos basada en YOLOv26. La arquitectura YOLO más reciente con postprocesado NMS.',
  },
  'YOLOv5 PPU pipeline. Integrated pre/post-processing.': {
    ko: 'YOLOv5 PPU 파이프라인. 전/후처리 통합.', ja: 'YOLOv5 PPU パイプライン。前処理/後処理統合。',
    'zh-CN': 'YOLOv5 PPU 管线。集成前/后处理。', 'zh-TW': 'YOLOv5 PPU 管線。整合前/後處理。',
    es: 'Pipeline PPU YOLOv5. Pre/post-procesamiento integrado.',
  },
  'YOLOv5-Face face detection with simultaneous landmark prediction.': {
    ko: 'YOLOv5-Face 얼굴 검출 (동시 landmark 예측).', ja: 'YOLOv5-Face 顔検出（同時 landmark 予測）。',
    'zh-CN': 'YOLOv5-Face 人脸检测（同时预测 landmark）。', 'zh-TW': 'YOLOv5-Face 人臉偵測（同時預測 landmark）。',
    es: 'Detección de rostros YOLOv5-Face con predicción simultánea de puntos de referencia.',
  },
  'YOLOv5-Pose estimation. Keypoint regression.': {
    ko: 'YOLOv5-Pose 자세 추정. Keypoint 회귀.', ja: 'YOLOv5-Pose 姿勢推定。Keypoint 回帰。',
    'zh-CN': 'YOLOv5-Pose 姿态估计。Keypoint 回归。', 'zh-TW': 'YOLOv5-Pose 姿態估計。Keypoint 回歸。',
    es: 'Estimación de pose YOLOv5. Regresión de puntos clave.',
  },
  'YOLOv5-Seg instance segmentation. Detection + Proto mask.': {
    ko: 'YOLOv5-Seg 인스턴스 분할. Detection + Proto mask.', ja: 'YOLOv5-Seg インスタンスセグメンテーション。Detection + Proto mask。',
    'zh-CN': 'YOLOv5-Seg 实例分割。Detection + Proto mask。', 'zh-TW': 'YOLOv5-Seg 實例分割。Detection + Proto mask。',
    es: 'Segmentación de instancias YOLOv5-Seg. Detección + máscara Proto.',
  },
  'YOLOv5-based object detection. Anchor-based with NMS post-processing.': {
    ko: 'YOLOv5 기반 객체 검출. 앵커 기반, NMS 후처리.', ja: 'YOLOv5 ベースの物体検出。アンカーベース、NMS 後処理。',
    'zh-CN': 'YOLOv5 目标检测。基于锚框，NMS 后处理。', 'zh-TW': 'YOLOv5 物件偵測。基於錨框，NMS 後處理。',
    es: 'Detección de objetos basada en YOLOv5. Basada en anclas con postprocesado NMS.',
  },
  'YOLOv7 PPU pipeline. Integrated pre/post-processing.': {
    ko: 'YOLOv7 PPU 파이프라인. 전/후처리 통합.', ja: 'YOLOv7 PPU パイプライン。前処理/後処理統合。',
    'zh-CN': 'YOLOv7 PPU 管线。集成前/后处理。', 'zh-TW': 'YOLOv7 PPU 管線。整合前/後處理。',
    es: 'Pipeline PPU YOLOv7. Pre/post-procesamiento integrado.',
  },
  'YOLOv7-Face face detection with simultaneous landmark prediction.': {
    ko: 'YOLOv7-Face 얼굴 검출 (동시 landmark 예측).', ja: 'YOLOv7-Face 顔検出（同時 landmark 予測）。',
    'zh-CN': 'YOLOv7-Face 人脸检测（同时预测 landmark）。', 'zh-TW': 'YOLOv7-Face 人臉偵測（同時預測 landmark）。',
    es: 'Detección de rostros YOLOv7-Face con predicción simultánea de puntos de referencia.',
  },
  'YOLOv7-based object detection. E-ELAN architecture with NMS post-processing.': {
    ko: 'YOLOv7 기반 객체 검출. E-ELAN 아키텍처, NMS 후처리.', ja: 'YOLOv7 ベースの物体検出。E-ELAN アーキテクチャ、NMS 後処理。',
    'zh-CN': 'YOLOv7 目标检测。E-ELAN 架构，NMS 后处理。', 'zh-TW': 'YOLOv7 物件偵測。E-ELAN 架構，NMS 後處理。',
    es: 'Detección de objetos basada en YOLOv7. Arquitectura E-ELAN con postprocesado NMS.',
  },
  'YOLOv8-Pose estimation. Anchor-free keypoint head.': {
    ko: 'YOLOv8-Pose 자세 추정. 앵커 프리 keypoint head.', ja: 'YOLOv8-Pose 姿勢推定。アンカーフリー keypoint head。',
    'zh-CN': 'YOLOv8-Pose 姿态估计。无锚框 keypoint head。', 'zh-TW': 'YOLOv8-Pose 姿態估計。無錨框 keypoint head。',
    es: 'Estimación de pose YOLOv8. Cabezal de puntos clave sin anclas.',
  },
  'YOLOv8-Seg instance segmentation. Anchor-free + Mask head.': {
    ko: 'YOLOv8-Seg 인스턴스 분할. 앵커 프리 + Mask head.', ja: 'YOLOv8-Seg インスタンスセグメンテーション。アンカーフリー + Mask head。',
    'zh-CN': 'YOLOv8-Seg 实例分割。无锚框 + Mask head。', 'zh-TW': 'YOLOv8-Seg 實例分割。無錨框 + Mask head。',
    es: 'Segmentación de instancias YOLOv8-Seg. Sin anclas + cabezal de máscara.',
  },
  'YOLOv8-based object detection. Anchor-free with NMS post-processing.': {
    ko: 'YOLOv8 기반 객체 검출. 앵커 프리, NMS 후처리.', ja: 'YOLOv8 ベースの物体検出。アンカーフリー、NMS 後処理。',
    'zh-CN': 'YOLOv8 目标检测。无锚框，NMS 后处理。', 'zh-TW': 'YOLOv8 物件偵測。無錨框，NMS 後處理。',
    es: 'Detección de objetos basada en YOLOv8. Sin anclas con postprocesado NMS.',
  },
  'YOLOv9-based object detection. PGI/GELAN architecture with NMS post-processing.': {
    ko: 'YOLOv9 기반 객체 검출. PGI/GELAN 아키텍처, NMS 후처리.', ja: 'YOLOv9 ベースの物体検出。PGI/GELAN アーキテクチャ、NMS 後処理。',
    'zh-CN': 'YOLOv9 目标检测。PGI/GELAN 架构，NMS 后处理。', 'zh-TW': 'YOLOv9 物件偵測。PGI/GELAN 架構，NMS 後處理。',
    es: 'Detección de objetos basada en YOLOv9. Arquitectura PGI/GELAN con postprocesado NMS.',
  },
  'Zero-DCE low-light image enhancement. Zero-reference learning.': {
    ko: 'Zero-DCE 저조도 이미지 향상. Zero-reference 학습.', ja: 'Zero-DCE 低照度画像強化。ゼロリファレンス学習。',
    'zh-CN': 'Zero-DCE 低光照图像增强。零参考学习。', 'zh-TW': 'Zero-DCE 低光照影像增強。零參考學習。',
    es: 'Mejora de imágenes con poca luz Zero-DCE. Aprendizaje sin referencia.',
  },
  'Postprocessors': {
    ko: '후처리기', ja: 'ポストプロセッサー',
    'zh-CN': '后处理器', 'zh-TW': '後處理器',
    es: 'Post-procesadores',
  },
  'Visualization': {
    ko: '시각화', ja: '可視化',
    'zh-CN': '可视化', 'zh-TW': '視覺化',
    es: 'Visualización',
  },
  'Full Config (config.json)': {
    ko: '전체 설정 (config.json)', ja: '全設定 (config.json)',
    'zh-CN': '完整配置 (config.json)', 'zh-TW': '完整設定 (config.json)',
    es: 'Configuración completa (config.json)',
  },
  'Basic Info': {
    ko: '기본 정보', ja: '基本情報',
    'zh-CN': '基本信息', 'zh-TW': '基本資訊',
    es: 'Información básica',
  },
  'Preprocessing': {
    ko: '전처리', ja: '前処理',
    'zh-CN': '预处理', 'zh-TW': '預處理',
    es: 'Pre-procesamiento',
  },

  'Add Q-Lite to cart': {
    ko: 'Q-Lite 장바구니에 추가', ja: 'Q-Lite をカートに追加',
    'zh-CN': '将 Q-Lite 加入购物车', 'zh-TW': '將 Q-Lite 加入購物車',
    es: 'Agregar Q-Lite al carrito',
  },
  'Add Q-Pro to cart': {
    ko: 'Q-Pro 장바구니에 추가', ja: 'Q-Pro をカートに追加',
    'zh-CN': '将 Q-Pro 加入购物车', 'zh-TW': '將 Q-Pro 加入購物車',
    es: 'Agregar Q-Pro al carrito',
  },
  'Cancelling download…': {
    ko: '다운로드 취소 중…', ja: 'ダウンロードをキャンセル中…',
    'zh-CN': '正在取消下载…', 'zh-TW': '正在取消下載…',
    es: 'Cancelando descarga…',
  },
  'Clear Cart': {
    ko: '장바구니 비우기', ja: 'カートを空にする',
    'zh-CN': '清空购物车', 'zh-TW': '清空購物車',
    es: 'Vaciar carrito',
  },
  'Download All': {
    ko: '전체 다운로드', ja: '全てダウンロード',
    'zh-CN': '全部下载', 'zh-TW': '全部下載',
    es: 'Descargar todo',
  },
  'Download complete —': {
    ko: '다운로드 완료 —', ja: 'ダウンロード完了 —',
    'zh-CN': '下载完成 —', 'zh-TW': '下載完成 —',
    es: 'Descarga completa —',
  },
  'Download failed': {
    ko: '다운로드 실패', ja: 'ダウンロード失敗',
    'zh-CN': '下载失败', 'zh-TW': '下載失敗',
    es: 'Error en la descarga',
  },
  'Downloaded': {
    ko: '다운로드됨', ja: 'ダウンロード済み',
    'zh-CN': '已下载', 'zh-TW': '已下載',
    es: 'Descargado',
  },
  'Failed to load ModelZoo': {
    ko: 'ModelZoo 로드 실패', ja: 'ModelZoo の読み込みに失敗しました',
    'zh-CN': 'ModelZoo 加载失败', 'zh-TW': 'ModelZoo 載入失敗',
    es: 'Error al cargar ModelZoo',
  },
  'Hide': {
    ko: '숨기기', ja: '非表示',
    'zh-CN': '隐藏', 'zh-TW': '隱藏',
    es: 'Ocultar',
  },
  'Loading ModelZoo page…': {
    ko: 'ModelZoo 페이지 로딩 중…', ja: 'ModelZoo ページを読み込み中…',
    'zh-CN': '正在加载 ModelZoo 页面…', 'zh-TW': '正在載入 ModelZoo 頁面…',
    es: 'Cargando página de ModelZoo…',
  },
  'ModelZoo refreshed': {
    ko: 'ModelZoo 새로고침됨', ja: 'ModelZoo 更新完了',
    'zh-CN': 'ModelZoo 已刷新', 'zh-TW': 'ModelZoo 已重新整理',
    es: 'ModelZoo actualizado',
  },
  'No files selected for download': {
    ko: '다운로드할 파일이 선택되지 않았습니다', ja: 'ダウンロードするファイルが選択されていません',
    'zh-CN': '未选择要下载的文件', 'zh-TW': '未選擇要下載的檔案',
    es: 'No se seleccionaron archivos para descarga',
  },
  'No models found': {
    ko: '모델을 찾을 수 없습니다', ja: 'モデルが見つかりません',
    'zh-CN': '未找到模型', 'zh-TW': '找不到模型',
    es: 'No se encontraron modelos',
  },
  'Remove': {
    ko: '제거', ja: '削除',
    'zh-CN': '移除', 'zh-TW': '移除',
    es: 'Eliminar',
  },
  'Starting…': {
    ko: '시작 중…', ja: '開始中…',
    'zh-CN': '正在启动…', 'zh-TW': '正在啟動…',
    es: 'Iniciando…',
  },
  'View Cart': {
    ko: '장바구니 보기', ja: 'カートを表示',
    'zh-CN': '查看购物车', 'zh-TW': '檢視購物車',
    es: 'Ver carrito',
  },
  'errors': {
    ko: '오류', ja: 'エラー',
    'zh-CN': '个错误', 'zh-TW': '個錯誤',
    es: 'errores',
  },
  'files': {
    ko: '파일', ja: 'ファイル',
    'zh-CN': '个文件', 'zh-TW': '個檔案',
    es: 'archivos',
  },
  'model(s)': {
    ko: '모델', ja: 'モデル',
    'zh-CN': '个模型', 'zh-TW': '個模型',
    es: 'modelo(s)',
  },
  'All done!': {
    ko: '모두 완료!', ja: '全て完了！',
    'zh-CN': '全部完成！', 'zh-TW': '全部完成！',
    es: '¡Todo listo!',
  },

  'Archives': {
    ko: '아카이브', ja: 'アーカイブ',
    'zh-CN': '归档文件', 'zh-TW': '封存檔案',
    es: 'Archivos comprimidos',
  },
  'Deleted ': {
    ko: '삭제됨 ', ja: '削除済み ',
    'zh-CN': '已删除 ', 'zh-TW': '已刪除 ',
    es: 'Eliminado ',
  },
  'Images': {
    ko: '이미지', ja: '画像',
    'zh-CN': '图像', 'zh-TW': '影像',
    es: 'Imágenes',
  },
  'No source image for comparison': {
    ko: '비교할 원본 이미지가 없습니다', ja: '比較用のソース画像がありません',
    'zh-CN': '无可比较的源图像', 'zh-TW': '無可比較的來源影像',
    es: 'Sin imagen fuente para comparación',
  },
  'Other': {
    ko: '기타', ja: 'その他',
    'zh-CN': '其他', 'zh-TW': '其他',
    es: 'Otro',
  },
  'Videos': {
    ko: '비디오', ja: '動画',
    'zh-CN': '视频', 'zh-TW': '影片',
    es: 'Videos',
  },

  'Cascade: crops detected regions from stage-1 (Detection) and passes them to stage-2.': {
    ko: 'Cascade: stage-1 (Detection)에서 검출된 영역을 크롭하여 stage-2로 전달합니다.', ja: 'Cascade: stage-1（Detection）で検出された領域をクロップし、stage-2 に渡します。',
    'zh-CN': 'Cascade：从 stage-1（Detection）裁剪检测到的区域并传递给 stage-2。', 'zh-TW': 'Cascade：從 stage-1（Detection）裁剪偵測到的區域並傳遞給 stage-2。',
    es: 'Cascada: recorta regiones detectadas de la etapa-1 (Detección) y las pasa a la etapa-2.',
  },
  'Chain: each step\'s output image is fed as input to the next step.': {
    ko: 'Chain: 각 단계의 출력 이미지가 다음 단계의 입력으로 전달됩니다.', ja: 'Chain: 各ステップの出力画像が次のステップの入力として渡されます。',
    es: 'Chain: la imagen de salida de cada paso se usa como entrada del siguiente.',
    'zh-CN': 'Chain：每个步骤的输出图像作为下一步骤的输入。', 'zh-TW': 'Chain：每個步驟的輸出影像作為下一步驟的輸入。'
  },
  'Ready': {
    ko: '준비됨', ja: '準備完了',
    'zh-CN': '就绪', 'zh-TW': '就緒',
    es: 'Listo',
  },
  'Running stage-2 inference on {n} detected region(s)': {
    ko: '검출된 영역 {n}개에 stage-2 추론 실행 중', ja: '検出された {n} 件の領域で stage-2 推論を実行中',
    'zh-CN': '正在对 {n} 个检测区域运行 stage-2 推理', 'zh-TW': '正在對 {n} 個偵測區域執行 stage-2 推論',
    es: 'Ejecutando inferencia de etapa-2 en {n} región(es) detectada(s)',
  },
  'Done': {
    ko: '완료', ja: '完了',
    'zh-CN': '完成', 'zh-TW': '完成',
    es: 'Hecho',
  },
  'Running…': {
    ko: '실행 중…', ja: '実行中…',
    'zh-CN': '运行中…', 'zh-TW': '執行中…',
    es: 'Ejecutando…',
  },

  'CPU compute — operations running on the CPU': {
    ko: 'CPU 연산 — CPU에서 실행되는 연산', ja: 'CPU 演算 — CPU上で実行される演算',
    'zh-CN': 'CPU 计算 — 在 CPU 上运行的操作', 'zh-TW': 'CPU 運算 — 在 CPU 上執行的操作',
    es: 'Cómputo CPU — operaciones que se ejecutan en la CPU',
  },
  'Capture — frame capture from input source': {
    ko: 'Capture — 입력 소스에서 프레임 캡처', ja: 'Capture — 入力ソースからのフレームキャプチャ',
    'zh-CN': 'Capture — 从输入源捕获帧', 'zh-TW': 'Capture — 從輸入來源擷取影格',
    es: 'Captura — captura de fotogramas desde la fuente de entrada',
  },
  'Input I/O — reading image/video from disk or camera': {
    ko: 'Input I/O — 디스크 또는 카메라에서 이미지/비디오 읽기', ja: 'Input I/O — ディスクまたはカメラからの画像/動画読み取り',
    'zh-CN': 'Input I/O — 从磁盘或摄像头读取图像/视频', 'zh-TW': 'Input I/O — 從磁碟或攝影機讀取影像/影片',
    es: 'E/S de entrada — lectura de imagen/video desde disco o cámara',
  },
  'NPU compute — neural network inference on the NPU chip': {
    ko: 'NPU 연산 — NPU 칩에서의 신경망 추론', ja: 'NPU 演算 — NPU チップ上でのニューラルネットワーク推論',
    'zh-CN': 'NPU 计算 — NPU 芯片上的神经网络推理', 'zh-TW': 'NPU 運算 — NPU 晶片上的神經網路推論',
    es: 'Cómputo NPU — inferencia de red neuronal en el chip NPU',
  },
  'Output I/O — writing result image/video to disk': {
    ko: 'Output I/O — 결과 이미지/비디오를 디스크에 기록', ja: 'Output I/O — 結果画像/動画のディスクへの書き込み',
    'zh-CN': 'Output I/O — 将结果图像/视频写入磁盘', 'zh-TW': 'Output I/O — 將結果影像/影片寫入磁碟',
    es: 'E/S de salida — escritura de imagen/video de resultado en disco',
  },
  'PCIe transfer — data transfer between CPU and NPU': {
    ko: 'PCIe 전송 — CPU와 NPU 간 데이터 전송', ja: 'PCIe 転送 — CPU と NPU 間のデータ転送',
    'zh-CN': 'PCIe 传输 — CPU 与 NPU 之间的数据传输', 'zh-TW': 'PCIe 傳輸 — CPU 與 NPU 之間的資料傳輸',
    es: 'Transferencia PCIe — transferencia de datos entre CPU y NPU',
  },
  'Postprocessing — NMS, bounding boxes, visualization': {
    ko: 'Postprocessing — NMS, 바운딩 박스, 시각화', ja: 'Postprocessing — NMS、バウンディングボックス、可視化',
    'zh-CN': 'Postprocessing — NMS、边界框、可视化', 'zh-TW': 'Postprocessing — NMS、邊界框、視覺化',
    es: 'Postprocesamiento — NMS, cajas delimitadoras, visualización',
  },
  'Preprocessing — resize, normalize, color conversion': {
    ko: 'Preprocessing — 리사이즈, 정규화, 색상 변환', ja: 'Preprocessing — リサイズ、正規化、色変換',
    'zh-CN': 'Preprocessing — 缩放、归一化、颜色转换', 'zh-TW': 'Preprocessing — 縮放、正規化、色彩轉換',
    es: 'Preprocesamiento — redimensionar, normalizar, conversión de color',
  },
  'Processing Stages': {
    ko: '처리 단계', ja: '処理ステージ',
    'zh-CN': '处理阶段', 'zh-TW': '處理階段',
    es: 'Etapas de procesamiento',
  },
  'Service — DX Runtime service overhead': {
    ko: 'Service — DX Runtime 서비스 오버헤드', ja: 'Service — DX Runtime サービスオーバーヘッド',
    'zh-CN': 'Service — DX Runtime 服务开销', 'zh-TW': 'Service — DX Runtime 服務開銷',
    es: 'Servicio — Sobrecarga del servicio DX Runtime',
  },
  'Total Duration': {
    ko: '총 소요시간', ja: '合計時間',
    'zh-CN': '总时长', 'zh-TW': '總時長',
    es: 'Duración total',
  },
  'Total Events': {
    ko: '총 이벤트', ja: '合計イベント',
    'zh-CN': '总事件数', 'zh-TW': '總事件數',
    es: 'Total de eventos',
  },

  /* ==== Lab Portal ==== */
  /* Lab flows that do real work */
  'New': {
    ko: '생성', ja: '新規',
    'zh-CN': '新建', 'zh-TW': '新增',
    es: 'Nuevo',
  },
  'Overwrite': {
    ko: '덮어쓰기', ja: '上書き',
    'zh-CN': '覆盖', 'zh-TW': '覆寫',
    es: 'Sobrescribir',
  },
  'Add {name} to {category}': {
    ko: '{category}에 {name} 추가', ja: '{category}に {name} を追加',
    'zh-CN': '将 {name} 添加到{category}', 'zh-TW': '將 {name} 新增到{category}',
    es: 'Agregar {name} a {category}',
  },
  'Create the {name} task skeleton': {
    ko: '{name} task skeleton 생성', ja: '{name} タスクのスケルトンを作成',
    'zh-CN': '创建 {name} 任务骨架', 'zh-TW': '建立 {name} 任務骨架',
    es: 'Crear el esqueleto de la tarea {name}',
  },
  'Created': {
    ko: '생성됨', ja: '作成済み',
    'zh-CN': '已创建', 'zh-TW': '已建立',
    es: 'Creado',
  },
  'Copied from': {
    ko: '복사한 예제', ja: 'コピー元',
    'zh-CN': '复制自', 'zh-TW': '複製自',
    es: 'Copiado de',
  },
  'Run the Python copy with your model:': {
    ko: '내 모델로 Python 사본을 실행하세요:', ja: '自分のモデルで Python コピーを実行します:',
    'zh-CN': '用你的模型运行 Python 副本:', 'zh-TW': '用你的模型執行 Python 副本:',
    es: 'Ejecute la copia de Python con su modelo:',
  },
  'Build the C++ copy with dx_app build.sh.': {
    ko: 'C++ 사본은 dx_app build.sh로 빌드하세요.', ja: 'C++ コピーは dx_app の build.sh でビルドします。',
    'zh-CN': 'C++ 副本请用 dx_app 的 build.sh 构建。', 'zh-TW': 'C++ 副本請用 dx_app 的 build.sh 建置。',
    es: 'Compile la copia de C++ con build.sh de dx_app.',
  },
  'Script output': {
    ko: '스크립트 출력', ja: 'スクリプト出力',
    'zh-CN': '脚本输出', 'zh-TW': '腳本輸出',
    es: 'Salida del script',
  },
  'No example to copy for this language': {
    ko: '이 언어로 복사할 예제가 없습니다', ja: 'この言語でコピーできる例がありません',
    'zh-CN': '此语言没有可复制的示例', 'zh-TW': '此語言沒有可複製的範例',
    es: 'No hay ningún ejemplo que copiar para este lenguaje',
  },
  'Add Model copies an existing example and renames it. Run the copy with your own .dxnn.': {
    ko: 'Add Model은 기존 예제를 복사해 이름을 바꿉니다. 복사본은 내 .dxnn으로 실행하세요.', ja: 'Add Model は既存の例をコピーして名前を変えます。コピーは自分の .dxnn で実行してください。',
    'zh-CN': 'Add Model 会复制现有示例并重命名。请用你自己的 .dxnn 运行副本。', 'zh-TW': 'Add Model 會複製現有範例並重新命名。請用你自己的 .dxnn 執行副本。',
    es: 'Add Model copia un ejemplo existente y le cambia el nombre. Ejecute la copia con su propio .dxnn.',
  },
  'Your model (.dxnn, optional)': {
    ko: '내 모델 (.dxnn, 선택)', ja: '自分のモデル (.dxnn、任意)',
    'zh-CN': '你的模型 (.dxnn，可选)', 'zh-TW': '你的模型 (.dxnn，選填)',
    es: 'Su modelo (.dxnn, opcional)',
  },
  'Read the model': {
    ko: '모델 읽기', ja: 'モデルを読み込む',
    'zh-CN': '读取模型', 'zh-TW': '讀取模型',
    es: 'Leer el modelo',
  },
  'One inference': {
    ko: '추론 1회', ja: '推論 1 回',
    'zh-CN': '推理 1 次', 'zh-TW': '推論 1 次',
    es: 'Una inferencia',
  },
  'Completed': {
    ko: '완료', ja: '完了',
    'zh-CN': '已完成', 'zh-TW': '已完成',
    es: 'Completado',
  },
  'Throughput': {
    ko: '처리량', ja: 'スループット',
    'zh-CN': '吞吐量', 'zh-TW': '吞吐量',
    es: 'Throughput',
  },
  'Checks a compiled model on this board: reads the file, runs one inference, then measures throughput.': {
    ko: '이 보드에서 컴파일된 모델을 점검합니다. 파일을 읽고, 추론을 한 번 실행한 뒤 처리량을 잽니다.', ja: 'このボードでコンパイル済みモデルを確認します。ファイルを読み込み、推論を 1 回実行してからスループットを測定します。',
    'zh-CN': '在这块板上检查已编译的模型：读取文件，运行一次推理，再测量吞吐量。', 'zh-TW': '在這塊板子上檢查已編譯的模型：讀取檔案，執行一次推論，再測量吞吐量。',
    es: 'Comprueba un modelo compilado en esta placa: lee el archivo, ejecuta una inferencia y mide el rendimiento.',
  },
  'Compiled model': {
    ko: '컴파일된 모델', ja: 'コンパイル済みモデル',
    'zh-CN': '已编译模型', 'zh-TW': '已編譯模型',
    es: 'Modelo compilado',
  },
  'Other path…': {
    ko: '다른 경로…', ja: '別のパス…',
    'zh-CN': '其他路径…', 'zh-TW': '其他路徑…',
    es: 'Otra ruta…',
  },
  'Pipeline started': {
    ko: '파이프라인 시작됨', ja: 'パイプライン開始済み',
    'zh-CN': '管道已启动', 'zh-TW': '管線已啟動',
    es: 'Pipeline iniciado',
  },
  'Applied': {
    ko: '적용됨', ja: '適用済み',
    'zh-CN': '已应用', 'zh-TW': '已套用',
    es: 'Aplicado',
  },
  'Rolled back': {
    ko: '롤백됨', ja: 'ロールバック済み',
    'zh-CN': '已回滚', 'zh-TW': '已復原',
    es: 'Revertido',
  },
  'Lab changes': {
    ko: 'Lab 변경 내역', ja: 'Lab の変更',
    'zh-CN': 'Lab 变更', 'zh-TW': 'Lab 變更',
    es: 'Cambios de Lab',
  },
  'Type to confirm': {
    ko: '확인하려면 입력', ja: '確認のため入力',
    'zh-CN': '输入以确认', 'zh-TW': '輸入以確認',
    es: 'Escriba para confirmar',
  },
  'This change overwrote existing files. Restore them by hand.': {
    ko: '이 변경은 기존 파일을 덮어썼습니다. 직접 복구하세요.', ja: 'この変更は既存のファイルを上書きしました。手動で復元してください。',
    'zh-CN': '此变更覆盖了现有文件，请手动恢复。', 'zh-TW': '此變更覆寫了現有檔案，請手動還原。',
    es: 'Este cambio sobrescribió archivos existentes. Restáurelos manualmente.',
  },
  'Commit with git': {
    ko: 'git 으로 커밋', ja: 'git でコミット',
    'zh-CN': '用 git 提交', 'zh-TW': '用 git 提交',
    es: 'Confirmar con git',
  },
  'Files this change wrote': {
    ko: '이 변경이 만든 파일', ja: 'この変更が書いたファイル',
    'zh-CN': '此变更写入的文件', 'zh-TW': '此變更寫入的檔案',
    es: 'Archivos que escribió este cambio',
  },
  'Studio does not run git for you. Run these in a terminal to commit only these files:': {
    ko: 'Studio 는 git 을 대신 실행하지 않습니다. 이 파일만 커밋하려면 터미널에서 아래를 실행하세요:',
    ja: 'Studio は git を代わりに実行しません。これらのファイルだけをコミットするには、ターミナルで次を実行してください:',
    'zh-CN': 'Studio 不会替你运行 git。要只提交这些文件，请在终端中运行：',
    'zh-TW': 'Studio 不會替你執行 git。若只要提交這些檔案，請在終端機中執行：',
    es: 'Studio no ejecuta git por usted. Para confirmar solo estos archivos, ejecute esto en una terminal:',
  },
  'Git plan failed': {
    ko: 'git 명령을 만들지 못했습니다', ja: 'git コマンドを作成できませんでした',
    'zh-CN': '无法生成 git 命令', 'zh-TW': '無法產生 git 指令',
    es: 'No se pudieron preparar los comandos de git',
  },
  'No Lab changes yet': {
    ko: '아직 Lab 변경 내역이 없습니다', ja: 'Lab の変更はまだありません',
    'zh-CN': '还没有 Lab 变更', 'zh-TW': '還沒有 Lab 變更',
    es: 'Aún no hay cambios de Lab',
  },
  'Lab portal ready': {
    ko: 'Lab 포털 준비됨', ja: 'Labポータル準備完了',
    'zh-CN': 'Lab门户已就绪', 'zh-TW': 'Lab入口已就緒',
    es: 'Portal de laboratorio listo',
  },
  'Lab portal unavailable': {
    ko: 'Lab 포털을 사용할 수 없습니다', ja: 'Labポータルを利用できません',
    'zh-CN': 'Lab门户不可用', 'zh-TW': 'Lab入口無法使用',
    es: 'Portal de laboratorio no disponible',
  },
  'Lab session unavailable': {
    ko: 'Lab 세션을 사용할 수 없습니다', ja: 'Labセッションを利用できません',
    'zh-CN': 'Lab会话不可用', 'zh-TW': 'Lab工作階段無法使用',
    es: 'Sesión de laboratorio no disponible',
  },
  'The following already exist:\n': {
    ko: '다음이 이미 존재합니다:\n', ja: '以下は既に存在します:\n',
    es: 'Los siguientes elementos ya existen:\n',
    'zh-CN': '以下项目已存在:\n', 'zh-TW': '以下項目已存在:\n'
  },
  'Overwrite?': {
    ko: '덮어쓰시겠습니까?', ja: '上書きしますか?',
    'zh-CN': '要覆盖吗？', 'zh-TW': '要覆寫嗎?',
    es: '¿Sobrescribir?',
  },
  'Cancelled': {
    ko: '취소됨', ja: 'キャンセルされました',
    'zh-CN': '已取消', 'zh-TW': '已取消',
    es: 'Cancelado',
  },
  'Add Model Wizard': {
    ko: '모델 추가 마법사', ja: 'モデル追加ウィザード',
    'zh-CN': '添加模型向导', 'zh-TW': '新增模型精靈',
    es: 'Asistente para agregar modelo',
  },
  'Dry Run': {
    ko: '드라이 런', ja: 'ドライラン',
    'zh-CN': '试运行', 'zh-TW': '試執行',
    es: 'Ejecución de prueba',
  },
  'Change preview': {
    ko: '변경 미리보기', ja: '変更プレビュー',
    'zh-CN': '变更预览', 'zh-TW': '變更預覽',
    es: 'Vista previa de los cambios',
  },
  'Apply changes': {
    ko: '변경 적용', ja: '変更を適用',
    'zh-CN': '应用更改', 'zh-TW': '套用變更',
    es: 'Aplicar cambios',
  },
  'Apply completed': {
    ko: '적용 완료', ja: '適用完了',
    'zh-CN': '应用完成', 'zh-TW': '套用完成',
    es: 'Aplicación completada',
  },
  'This flow is planned for the next phase.': {
    ko: '이 흐름은 다음 단계에서 구현됩니다.', ja: 'このフローは次のフェーズで実装予定です。',
    'zh-CN': '此流程计划在下一阶段实现。', 'zh-TW': '此流程預計在下一階段實作。',
    es: 'Este flujo está planificado para la siguiente fase.',
  },
  'Source Path': {
    ko: '소스 경로', ja: 'ソースパス',
    'zh-CN': '源路径', 'zh-TW': '來源路徑',
    es: 'Ruta de origen',
  },
  'Session expired — please restart the wizard.': {
    ko: '세션이 만료되었습니다. 마법사를 다시 시작하세요.', ja: 'セッションが期限切れです。ウィザードを再開してください。',
    'zh-CN': '会话已过期，请重新启动向导。', 'zh-TW': '工作階段已過期，請重新啟動精靈。',
    es: 'Sesión expirada — por favor reinicie el asistente.',
  },
  'Blockers': {
    ko: '차단 요소', ja: 'ブロッカー',
    'zh-CN': '阻止项', 'zh-TW': '阻止項',
    es: 'Bloqueadores',
  },
  'Warnings': {
    ko: '경고', ja: '警告',
    'zh-CN': '警告', 'zh-TW': '警告',
    es: 'Advertencias',
  },
  'Dry run failed': {
    ko: '드라이 런 실패', ja: 'ドライラン失敗',
    'zh-CN': '试运行失败', 'zh-TW': '試執行失敗',
    es: 'Error en la ejecución de prueba',
  },
  'Dry run error': {
    ko: '드라이 런 오류', ja: 'ドライランエラー',
    'zh-CN': '试运行错误', 'zh-TW': '試執行錯誤',
    es: 'Error de ejecución de prueba',
  },
  'Apply failed': {
    ko: '적용 실패', ja: '適用失敗',
    'zh-CN': '应用失败', 'zh-TW': '套用失敗',
    es: 'Error al aplicar',
  },
  'Apply error': {
    ko: '적용 오류', ja: '適用エラー',
    'zh-CN': '应用错误', 'zh-TW': '套用錯誤',
    es: 'Error de aplicación',
  },
  'Create Task Wizard': {
    ko: '태스크 생성 마법사', ja: 'タスク作成ウィザード',
    'zh-CN': '创建任务向导', 'zh-TW': '建立任務精靈',
    es: 'Asistente para crear tarea',
  },
  'Scaffold Type': {
    ko: '스캐폴드 유형', ja: 'スキャフォールドタイプ',
    'zh-CN': '脚手架类型', 'zh-TW': '鷹架類型',
    es: 'Tipo de estructura',
  },
  'Full scaffold': {
    ko: '전체 스캐폴드', ja: 'フルスキャフォールド',
    'zh-CN': '完整脚手架', 'zh-TW': '完整鷹架',
    es: 'Estructura completa',
  },
  'Postprocessor only': {
    ko: '후처리기만', ja: 'ポストプロセッサーのみ',
    'zh-CN': '仅后处理器', 'zh-TW': '僅後處理器',
    es: 'Solo post-procesador',
  },
  'Generated Files': {
    ko: '생성된 파일', ja: '生成されたファイル',
    'zh-CN': '生成的文件', 'zh-TW': '產生的檔案',
    es: 'Archivos generados',
  },
  'Preview unavailable': {
    ko: '미리보기 없음', ja: 'プレビューなし',
    'zh-CN': '预览不可用', 'zh-TW': '預覽不可用',
    es: 'Vista previa no disponible',
  },
  'Task dry run failed': {
    ko: '태스크 드라이 런 실패', ja: 'タスクドライラン失敗',
    'zh-CN': '任务试运行失败', 'zh-TW': '任務試執行失敗',
    es: 'Error en la ejecución de prueba de tarea',
  },
  'Task dry run error': {
    ko: '태스크 드라이 런 오류', ja: 'タスクドライランエラー',
    'zh-CN': '任务试运行错误', 'zh-TW': '任務試執行錯誤',
    es: 'Error de ejecución de prueba de tarea',
  },
  'Task apply failed': {
    ko: '태스크 적용 실패', ja: 'タスク適用失敗',
    'zh-CN': '任务应用失败', 'zh-TW': '任務套用失敗',
    es: 'Error al aplicar la tarea',
  },
  'Task apply error': {
    ko: '태스크 적용 오류', ja: 'タスク適用エラー',
    'zh-CN': '任务应用错误', 'zh-TW': '任務套用錯誤',
    es: 'Error de aplicación de tarea',
  },

  /* ==== Lab Portal — Experiment Pipeline ==== */
  'Experiment Pipeline': {
    ko: '실험 파이프라인', ja: '実験パイプライン',
    'zh-CN': '实验流水线', 'zh-TW': '實驗流程',
    es: 'Pipeline experimental',
  },
  'Start pipeline': {
    ko: '파이프라인 시작', ja: 'パイプライン開始',
    'zh-CN': '启动流水线', 'zh-TW': '啟動流程',
    es: 'Iniciar pipeline',
  },
  'Cancel run': {
    ko: '실행 중단', ja: '実行キャンセル',
    'zh-CN': '取消运行', 'zh-TW': '取消執行',
    es: 'Cancelar ejecución',
  },
  'Refresh run': {
    ko: '실행 새로고침', ja: '実行更新',
    'zh-CN': '刷新运行', 'zh-TW': '重新整理執行',
    es: 'Actualizar ejecución',
  },
  'Run Status': {
    ko: '실행 상태', ja: '実行ステータス',
    'zh-CN': '运行状态', 'zh-TW': '執行狀態',
    es: 'Estado de ejecución',
  },
  'Current Step': {
    ko: '현재 단계', ja: '現在のステップ',
    'zh-CN': '当前步骤', 'zh-TW': '目前步驟',
    es: 'Paso actual',
  },
  'Pipeline Logs': {
    ko: '파이프라인 로그', ja: 'パイプラインログ',
    'zh-CN': '流水线日志', 'zh-TW': '流程日誌',
    es: 'Registros de pipeline',
  },
  'Pipeline start failed': {
    ko: '파이프라인 시작 실패', ja: 'パイプライン開始失敗',
    'zh-CN': '流水线启动失败', 'zh-TW': '流程啟動失敗',
    es: 'Error al iniciar el pipeline',
  },
  'Pipeline start error': {
    ko: '파이프라인 시작 오류', ja: 'パイプライン開始エラー',
    'zh-CN': '流水线启动错误', 'zh-TW': '流程啟動錯誤',
    es: 'Error de inicio del pipeline',
  },
  'Pipeline refresh failed': {
    ko: '파이프라인 새로고침 실패', ja: 'パイプライン更新失敗',
    'zh-CN': '流水线刷新失败', 'zh-TW': '流程重新整理失敗',
    es: 'Error al actualizar el pipeline',
  },
  'Pipeline cancel failed': {
    ko: '파이프라인 취소 실패', ja: 'パイプラインキャンセル失敗',
    'zh-CN': '流水线取消失败', 'zh-TW': '流程取消失敗',
    es: 'Error al cancelar el pipeline',
  },
  'Pipeline cancel error': {
    ko: '파이프라인 취소 오류', ja: 'パイプラインキャンセルエラー',
    'zh-CN': '流水线取消错误', 'zh-TW': '流程取消錯誤',
    es: 'Error de cancelación del pipeline',
  },

  /* ==== Legacy inline T() migration ==== */
  'comment count suffix': {
    en: '\u200c', ko: '개', ja: '件',
    es: '\u200c',
    'zh-CN': '条', 'zh-TW': '則'
  },

  /* ==== Placeholder i18n (missing entries) ==== */
  'rtsp://… or IP:Port': {
    ko: 'rtsp://… 또는 IP:포트', ja: 'rtsp://… または IP:ポート',
    es: 'rtsp://… o IP:Puerto',
    'zh-CN': 'rtsp://… 或 IP:端口', 'zh-TW': 'rtsp://… 或 IP:連接埠'
  },
  'IP:Port': {
    ko: 'IP:포트', ja: 'IP:ポート',
    es: 'IP:Puerto',
    'zh-CN': 'IP:端口', 'zh-TW': 'IP:連接埠'
  },
  '/path/to/config.json': {
    ko: '/path/to/config.json', ja: '/path/to/config.json',
    es: '/ruta/config.json',
    'zh-CN': '/path/to/config.json', 'zh-TW': '/path/to/config.json'
  },
  'jpeg,jpg,png': {
    ko: 'jpeg,jpg,png', ja: 'jpeg,jpg,png',
    es: 'jpeg,jpg,png',
    'zh-CN': 'jpeg,jpg,png', 'zh-TW': 'jpeg,jpg,png'
  },
  'compiler_output/my_model': {
    ko: 'compiler_output/my_model', ja: 'compiler_output/my_model',
    es: 'compiler_output/my_model',
    'zh-CN': 'compiler_output/my_model', 'zh-TW': 'compiler_output/my_model'
  },
  '[{"bbox":"Mul_441","cls_conf":"Sigmoid_442"}]': {
    ko: '[{"bbox":"Mul_441","cls_conf":"Sigmoid_442"}]', ja: '[{"bbox":"Mul_441","cls_conf":"Sigmoid_442"}]',
    es: '[{"bbox":"Mul_441","cls_conf":"Sigmoid_442"}]',
    'zh-CN': '[{"bbox":"Mul_441","cls_conf":"Sigmoid_442"}]', 'zh-TW': '[{"bbox":"Mul_441","cls_conf":"Sigmoid_442"}]'
  },
  'Show/hide password': {ko:'비밀번호 표시/숨기기',ja:'パスワード表示/非表示',es:'Mostrar/ocultar contraseña','zh-CN':'显示/隐藏密码','zh-TW':'顯示/隱藏密碼'},
  'Close': {ko:'닫기',ja:'閉じる',es:'Cerrar','zh-CN':'关闭','zh-TW':'關閉'},
  'Enable profiling to capture detailed execution timeline': {ko:'상세 실행 타임라인 캡처를 위한 프로파일링 활성화',ja:'詳細な実行タイムラインをキャプチャするプロファイリングを有効化',es:'Habilitar perfilado para capturar la línea de tiempo detallada de ejecución','zh-CN':'启用分析以捕获详细的执行时间线','zh-TW':'啟用分析以擷取詳細的執行時間線'},
  'Refresh': {ko:'새로고침',ja:'更新',es:'Actualizar','zh-CN':'刷新','zh-TW':'重新整理'},
  'Export Benchmark Report': {ko:'벤치마크 보고서 내보내기',ja:'ベンチマークレポートをエクスポート',es:'Exportar informe de rendimiento','zh-CN':'导出基准测试报告','zh-TW':'匯出基準測試報告'},
  'Browse files': {ko:'파일 찾아보기',ja:'ファイルを参照',es:'Explorar archivos','zh-CN':'浏览文件','zh-TW':'瀏覽檔案'},
  'Browse server': {ko:'서버 찾아보기',ja:'サーバーを参照',es:'Explorar servidor','zh-CN':'浏览服务器','zh-TW':'瀏覽伺服器'},
  'Browse folder': {ko:'폴더 찾아보기',ja:'フォルダを参照',es:'Explorar carpeta','zh-CN':'浏览文件夹','zh-TW':'瀏覽資料夾'},
  'Show/hide': {ko:'표시/숨기기',ja:'表示/非表示',es:'Mostrar/ocultar','zh-CN':'显示/隐藏','zh-TW':'顯示/隱藏'},
  'Grid view': {ko:'그리드 보기',ja:'グリッド表示',es:'Vista de cuadrícula','zh-CN':'网格视图','zh-TW':'網格檢視'},
  'Table view': {ko:'테이블 보기',ja:'テーブル表示',es:'Vista de tabla','zh-CN':'表格视图','zh-TW':'表格檢視'},
  'Open in new tab': {ko:'새 탭에서 열기',ja:'新しいタブで開く',es:'Abrir en nueva pestaña','zh-CN':'在新标签页中打开','zh-TW':'在新分頁中開啟'},
  'View pipeline reference table': {ko:'파이프라인 레퍼런스 테이블 보기',ja:'パイプライン参照テーブルを表示',es:'Ver tabla de referencia del pipeline','zh-CN':'查看流水线参考表','zh-TW':'檢視管線參考表'},
  'File browser': {ko:'파일 탐색기',ja:'ファイルブラウザ',es:'Explorador de archivos','zh-CN':'文件浏览器','zh-TW':'檔案瀏覽器'},
  'Check that dx_engine is running. Real inference is not available in Mock mode.': {
    ko: 'dx_engine이 실행 중인지 확인해주세요. (Mock 모드에서는 실제 추론이 불가능합니다)',
    ja: 'dx_engineが実行中か確認してください。(Mockモードでは実際の推論はできません)',
    'zh-CN': '请确认dx_engine正在运行。(Mock模式下无法进行实际推理)',
    'zh-TW': '請確認dx_engine正在執行。(Mock模式下無法進行實際推論)',
    es: 'Verifique que dx_engine esté en ejecución. La inferencia real no está disponible en modo Mock.',
  },
  'Check the model file or executable path.': {
    ko: '모델 파일 또는 실행파일 경로를 확인해주세요.',
    ja: 'モデルファイルまたは実行ファイルのパスを確認してください。',
    'zh-CN': '请检查模型文件或可执行文件路径。',
    'zh-TW': '請檢查模型檔案或執行檔路徑。',
    es: 'Verifique la ruta del archivo de modelo o del ejecutable.',
  },
  'Inference timed out. Try again with a smaller input.': {
    ko: '추론 시간이 초과되었습니다. 더 작은 입력으로 시도해주세요.',
    ja: '推論がタイムアウトしました。より小さい入力で再試行してください。',
    'zh-CN': '推理超时。请使用较小的输入重试。',
    'zh-TW': '推論逾時。請使用較小的輸入重試。',
    es: 'La inferencia ha excedido el tiempo. Intente de nuevo con una entrada más pequeña.',
  },
};

/* ─── inline helper for JS runtime strings (ko, en, ja, zh-CN, zh-TW, es) ───
   The name stays _T5 although es is a sixth argument. */
function _T5(ko, en, ja, zhCN, zhTW, es) {
    var lang = (window.DXI18n && window.DXI18n.lang) || 'en';
    if (lang === 'ko') return ko || en;
    if (lang === 'ja') return ja || en;
    if (lang === 'zh-CN') return zhCN || en;
    if (lang === 'zh-TW') return zhTW || en;
    if (lang === 'es') return es || en;
    return en;
}

/* ─── App-specific callbacks for shared i18n core ─── */
// _i18nOptions() and topbar-title are handled by refreshActivePageLanguage() in utils.js
window._DX_I18N_CALLBACKS = [];
