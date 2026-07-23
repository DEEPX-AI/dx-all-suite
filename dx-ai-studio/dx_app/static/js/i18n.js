/* ============================================================
   i18n.js — DX-APP i18n Data Module
   Exports dictionaries & callbacks for shared/i18n.js core.
   ============================================================ */
'use strict';

/* ─── Translation Dictionary (English → Korean) ─── */
window._DX_I18N_DICT = {
  /* ==== Sidebar ==== */
  'Setup': {
    ko: '설정', ja: 'セットアップ',
    'zh-CN': '设置', 'zh-TW': '設定',
    es: 'Configuración',
  },
  'Dashboard': {
    ko: '대시보드', ja: 'ダッシュボード',
    'zh-CN': '仪表板', 'zh-TW': '儀表板',
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
    'zh-CN': 'A/B 比较', 'zh-TW': 'A/B 比較',
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
    ko: '설정 & 설치', ja: 'セットアップ & インストール',
    'zh-CN': '设置 & 安装', 'zh-TW': '設定 & 安裝',
    es: 'Configuración e instalación',
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
    'zh-CN': 'DX-APP 依赖项', 'zh-TW': 'DX-APP 相依性',
    es: 'Dependencias de DX-APP',
  },
  'DX-APP Build': {
    ko: 'DX-APP 빌드', ja: 'DX-APP ビルド',
    'zh-CN': 'DX-APP 构建', 'zh-TW': 'DX-APP 建置',
    es: 'Compilación DX-APP',
  },
  'Sample Assets Setup': {
    ko: '샘플 에셋 설정', ja: 'サンプルアセットセットアップ',
    'zh-CN': '示例资源设置', 'zh-TW': '範例資源設定',
    es: 'Configuración de activos de muestra',
  },
  'DX-Runtime Dependencies': {
    ko: 'DX-Runtime 종속성', ja: 'DX-Runtime 依存関係',
    'zh-CN': 'DX-Runtime 依赖项', 'zh-TW': 'DX-Runtime 相依性',
    es: 'Dependencias de DX-Runtime',
  },
  'NPU Linux Driver': {
    ko: 'NPU 리눅스 드라이버', ja: 'NPU Linux ドライバ',
    'zh-CN': 'NPU Linux 驱动', 'zh-TW': 'NPU Linux 驅動程式',
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
    ko: '상태 새로고침', ja: 'ステータス更新',
    'zh-CN': '刷新状态', 'zh-TW': '重新整理狀態',
    es: 'Actualizar estado',
  },
  'Send': {
    ko: '보내기', ja: '送信',
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
    'zh-CN': '选择要运行的项目 — 日志将显示在此处。', 'zh-TW': '選擇要執行的項目 — 日誌將顯示在此處。',
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
    ko: 'NPU가 감지되지 않음', ja: 'NPUが検出されません',
    'zh-CN': '未检测到NPU', 'zh-TW': '未偵測到NPU',
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
    es: 'Voltio',
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
    'zh-CN': '主机名', 'zh-TW': '主機名',
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
    es: 'Meta',
  },
  'File': {
    ko: '파일', ja: 'ファイル',
    'zh-CN': '文件', 'zh-TW': '檔案',
    es: 'Archivo',
  },
  /* ==== Run Inference ==== */
  'Single': {
    ko: '단일', ja: 'シングル',
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
    es: 'Vídeo',
  },
  'Sample Image': {
    ko: '샘플 이미지', ja: 'サンプル画像',
    'zh-CN': '示例图像', 'zh-TW': '範例影像',
    es: 'Imagen de muestra',
  },
  'Video File': {
    ko: '동영상 파일', ja: '動画ファイル',
    'zh-CN': '视频文件', 'zh-TW': '影片檔案',
    es: 'Archivo de vídeo',
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
    es: 'Sincronizar',
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
    'zh-CN': '此任务不需要额外参数。', 'zh-TW': '此任務不需要額外參數。',
    es: 'No se requieren parámetros adicionales para esta tarea.',
  },
  'Continuous Config': {
    ko: '연속 구성', ja: '連続設定',
    'zh-CN': '连续配置', 'zh-TW': '連續設定',
    es: 'Configuración continua',
  },
  'Model Slots': {
    ko: '모델 슬롯', ja: 'モデルスロット',
    'zh-CN': '模型槽位', 'zh-TW': '模型插槽',
    es: 'Ranuras de modelo',
  },
  'Start Continuous': {
    ko: '연속 시작', ja: '連続開始',
    'zh-CN': '启动连续', 'zh-TW': '啟動連續',
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
  'Run All': {
    ko: '전체 실행', ja: 'すべて実行',
    'zh-CN': '全部运行', 'zh-TW': '全部執行',
    es: 'Ejecutar todo',
  },
  'Performance Comparison': {
    ko: '성능 비교', ja: 'パフォーマンス比較',
    'zh-CN': '性能比较', 'zh-TW': '效能比較',
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
    es: 'Vídeo de entrada',
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
  'Chain: each step\'s output image is fed as input to the next step.': '체인: 각 단계의 출력 이미지가 다음 단계의 입력으로 전달됩니다.',

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
    ko: '수정일', ja: '更新日',
    'zh-CN': '修改日期', 'zh-TW': '修改日期',
    es: 'Modificado',
  },
  'No output files yet.': {
    ko: '아직 출력 파일이 없습니다.', ja: 'まだ出力ファイルがありません。',
    'zh-CN': '暂无输出文件。', 'zh-TW': '尚無輸出檔案。',
    es: 'Sin archivos de salida aún.',
  },

  /* ==== Planner ==== */
  'Configuration': {
    ko: '구성', ja: '設定',
    'zh-CN': '配置', 'zh-TW': '設定',
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
    es: 'Negocio (12h)',
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
    es: 'Tienda no tripulada',
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
    es: 'Ley GDPR/de privacidad: la nube no es adecuada: transferencia de vídeo transfronteriza restringida',
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
    ko: '모델 추가', ja: 'モデル追加',
    'zh-CN': '添加模型', 'zh-TW': '新增模型',
    es: 'Agregar modelo',
  },
  'Delete Model': {
    ko: '모델 삭제', ja: 'モデル削除',
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
    'zh-CN': '提取包', 'zh-TW': '提取套件',
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
    ko: '후처리기', ja: 'ポストプロセッサー',
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
    'zh-CN': '提取包', 'zh-TW': '提取套件',
    es: 'Extraer paquete',
  },
  'Select Model': {
    ko: '모델 선택', ja: 'モデル選択',
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
    ko: '파일 선택', ja: 'ファイル選択',
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
    ko: '전처리기', ja: 'プリプロセッサ',
    'zh-CN': '预处理器', 'zh-TW': '前處理器',
    es: 'Pre-procesador',
  },
  'Visualizer': {
    ko: '시각화기', ja: 'ビジュアライザ',
    'zh-CN': '可视化器', 'zh-TW': '視覺化器',
    es: 'Visualizador',
  },
  'Recommended Pipelines by Category': {
    ko: '카테고리별 권장 파이프라인', ja: 'カテゴリ別おすすめパイプライン',
    'zh-CN': '按类别推荐的流水线', 'zh-TW': '按類別推薦的管線',
    es: 'Pipelines recomendados por categoría',
  },
  'Deploy?': {
    ko: '배포?', ja: 'デプロイしますか?',
    'zh-CN': '部署？', 'zh-TW': '部署？',
    es: '¿Desplegar?',
  },
  'Reconfigure': {
    ko: '재구성', ja: '再設定',
    'zh-CN': '重新配置', 'zh-TW': '重新設定',
    es: 'Reconfigurar',
  },
  'Confirm Deploy': {
    ko: '배포 확인', ja: 'デプロイ確認',
    'zh-CN': '确认部署', 'zh-TW': '確認部署',
    es: 'Confirmar despliegue',
  },
  'Select Sample Image': {
    ko: '샘플 이미지 선택', ja: 'サンプル画像を選択',
    'zh-CN': '选择示例图像', 'zh-TW': '選擇範例影像',
    es: 'Seleccionar imagen de muestra',
  },

  /* ==== Buttons with emoji ==== */
  '▶ Run Inference': {
    ko: '▶ 추론 실행', ja: '▶ 推論実行',
    'zh-CN': '▶ 运行推理', 'zh-TW': '▶ 執行推論',
    es: '▶ Ejecutar inferencia',
  },
  '⏹ Stop': {
    ko: '⏹ 중지', ja: '⏹ 停止',
    'zh-CN': '⏹ 停止', 'zh-TW': '⏹ 停止',
    es: '⏹ Detener',
  },
  '🎯 ROI': {
    ko: '🎯 ROI', ja: '🎯 ROI',
    'zh-CN': '🎯 ROI', 'zh-TW': '🎯 ROI',
    es: '🎯 ROI',
  },
  '☑ Select All': {
    ko: '☑ 전체 선택', ja: '☑ すべて選択',
    'zh-CN': '☑ 全选', 'zh-TW': '☑ 全選',
    es: '☑ Seleccionar todo',
  },
  '☐ Deselect': {
    ko: '☐ 선택 해제', ja: '☐ 選択解除',
    'zh-CN': '☐ 取消选择', 'zh-TW': '☐ 取消選擇',
    es: '☐ Deseleccionar',
  },
  '▶ Run All': {
    ko: '▶ 전체 실행', ja: '▶ すべて実行',
    'zh-CN': '▶ 全部运行', 'zh-TW': '▶ 全部執行',
    es: '▶ Ejecutar todo',
  },
  '➕ Add Step': {
    ko: '➕ 단계 추가', ja: '➕ ステップ追加',
    'zh-CN': '➕ 添加步骤', 'zh-TW': '➕ 新增步驟',
    es: '➕ Agregar paso',
  },
  '▶ Start Compile': {
    ko: '▶ 컴파일 시작', ja: '▶ コンパイル開始',
    'zh-CN': '▶ 启动编译', 'zh-TW': '▶ 啟動編譯',
    es: '▶ Iniciar compilación',
  },
  '📋 Export JSON': {
    ko: '📋 JSON 내보내기', ja: '📋 JSON エクスポート',
    'zh-CN': '📋 导出 JSON', 'zh-TW': '📋 匯出 JSON',
    es: '📋 Exportar JSON',
  },
  '📋 Execution Log': {
    ko: '📋 실행 로그', ja: '📋 実行ログ',
    'zh-CN': '📋 执行日志', 'zh-TW': '📋 執行日誌',
    es: '📋 Registro de ejecución',
  },
  '🔄 Refresh Status': {
    ko: '🔄 상태 새로고침', ja: '🔄 ステータス更新',
    'zh-CN': '🔄 刷新状态', 'zh-TW': '🔄 重新整理狀態',
    es: '🔄 Actualizar estado',
  },
  '⌨️ Manual Input': {
    ko: '⌨️ 수동 입력', ja: '⌨️ 手動入力',
    'zh-CN': '⌨️ 手动输入', 'zh-TW': '⌨️ 手動輸入',
    es: '⌨️ Entrada manual',
  },
  '📥 Export Report': {
    ko: '📥 보고서 내보내기', ja: '📥 レポートエクスポート',
    'zh-CN': '📥 导出报告', 'zh-TW': '📥 匯出報告',
    es: '📥 Exportar informe',
  },
  '📂 Local File': {
    ko: '📂 로컬 파일', ja: '📂 ローカルファイル',
    'zh-CN': '📂 本地文件', 'zh-TW': '📂 本機檔案',
    es: '📂 Archivo local',
  },
  '🗂 Browse Server': {
    ko: '🗂 서버 찾아보기', ja: '🗂 サーバーを参照',
    'zh-CN': '🗂 浏览服务器', 'zh-TW': '🗂 瀏覽伺服器',
    es: '🗂 Explorar servidor',
  },
  '🔍 Inspect': {
    ko: '🔍 검사', ja: '🔍 検査',
    'zh-CN': '🔍 检查', 'zh-TW': '🔍 檢查',
    es: '🔍 Inspeccionar',
  },
  '📷 Single': {
    ko: '📷 단일', ja: '📷 シングル',
    'zh-CN': '📷 单次', 'zh-TW': '📷 單次',
    es: '📷 Individual',
  },
  '🔄 Continuous': {
    ko: '🔄 연속', ja: '🔄 連続',
    'zh-CN': '🔄 连续', 'zh-TW': '🔄 連續',
    es: '🔄 Continuo',
  },
  '▶ Start Continuous': {
    ko: '▶ 연속 시작', ja: '▶ 連続開始',
    'zh-CN': '▶ 启动连续', 'zh-TW': '▶ 啟動連續',
    es: '▶ Iniciar continuo',
  },
  '＋ Add Model': {
    ko: '＋ 모델 추가', ja: '＋ モデル追加',
    'zh-CN': '＋ 添加模型', 'zh-TW': '＋ 新增模型',
    es: '＋ Agregar modelo',
  },
  '🔓 Authenticate': {
    ko: '🔓 인증', ja: '🔓 認証',
    'zh-CN': '🔓 认证', 'zh-TW': '🔓 驗證',
    es: '🔓 Autenticar',
  },
  '➕ Add Model': {
    ko: '➕ 모델 추가', ja: '➕ モデル追加',
    'zh-CN': '➕ 添加模型', 'zh-TW': '➕ 新增模型',
    es: '➕ Agregar modelo',
  },
  '🗑️ Delete Model': {
    ko: '🗑️ 모델 삭제', ja: '🗑️ モデル削除',
    'zh-CN': '🗑️ 删除模型', 'zh-TW': '🗑️ 刪除模型',
    es: '🗑️ Eliminar modelo',
  },
  '🦴 Create Skeleton': {
    ko: '🦴 스켈레톤 생성', ja: '🦴 スケルトン作成',
    'zh-CN': '🦴 创建骨架', 'zh-TW': '🦴 建立骨架',
    es: '🦴 Crear esqueleto',
  },
  '📝 Commit': {
    ko: '📝 커밋', ja: '📝 コミット',
    'zh-CN': '📝 提交', 'zh-TW': '📝 提交',
    es: '📝 Confirmar',
  },
  '📦 Extract Package': {
    ko: '📦 패키지 추출', ja: '📦 パッケージ抽出',
    'zh-CN': '📦 提取包', 'zh-TW': '📦 提取套件',
    es: '📦 Extraer paquete',
  },
  '✕ Clear': {
    ko: '✕ 지우기', ja: '✕ クリア',
    'zh-CN': '✕ 清除', 'zh-TW': '✕ 清除',
    es: '✕ Limpiar',
  },
  '✓ Apply ROI': {
    ko: '✓ ROI 적용', ja: '✓ ROIを適用',
    'zh-CN': '✓ 应用 ROI', 'zh-TW': '✓ 套用 ROI',
    es: '✓ Aplicar ROI',
  },
  '✅ Select': {
    ko: '✅ 선택', ja: '✅ 選択',
    'zh-CN': '✅ 选择', 'zh-TW': '✅ 選擇',
    es: '✅ Seleccionar',
  },
  '📦 Deploy?': {
    ko: '📦 배포?', ja: '📦 デプロイしますか?',
    'zh-CN': '📦 部署？', 'zh-TW': '📦 部署？',
    es: '📦 ¿Desplegar?',
  },
  '↩ Reconfigure': {
    ko: '↩ 재구성', ja: '↩ 再設定',
    'zh-CN': '↩ 重新配置', 'zh-TW': '↩ 重新設定',
    es: '↩ Reconfigurar',
  },
  '✅ Confirm Deploy': {
    ko: '✅ 배포 확인', ja: '✅ デプロイ確認',
    'zh-CN': '✅ 确认部署', 'zh-TW': '✅ 確認部署',
    es: '✅ Confirmar despliegue',
  },
  '+ Add Task': {
    ko: '+ 작업 추가', ja: '+ タスク追加',
    'zh-CN': '+ 添加任务', 'zh-TW': '+ 新增任務',
    es: '+ Agregar tarea',
  },

  /* ==== Setup titles with emoji ==== */
  '🏗️ DX-APP Dependencies': {
    ko: '🏗️ DX-APP 종속성', ja: '🏗️ DX-APP 依存関係',
    'zh-CN': '🏗️ DX-APP 依赖项', 'zh-TW': '🏗️ DX-APP 相依性',
    es: '🏗️ Dependencias de DX-APP',
  },
  '🔨 DX-APP Build': {
    ko: '🔨 DX-APP 빌드', ja: '🔨 DX-APP ビルド',
    'zh-CN': '🔨 DX-APP 构建', 'zh-TW': '🔨 DX-APP 建置',
    es: '🔨 Compilación DX-APP',
  },
  '📦 Sample Assets Setup': {
    ko: '📦 샘플 에셋 설정', ja: '📦 サンプルアセットセットアップ',
    'zh-CN': '📦 示例资源设置', 'zh-TW': '📦 範例資源設定',
    es: '📦 Configuración de activos de muestra',
  },
  '🔧 DX-Runtime Dependencies': {
    ko: '🔧 DX-Runtime 종속성', ja: '🔧 DX-Runtime 依存関係',
    'zh-CN': '🔧 DX-Runtime 依赖项', 'zh-TW': '🔧 DX-Runtime 相依性',
    es: '🔧 Dependencias de DX-Runtime',
  },
  '🔌 NPU Linux Driver': {
    ko: '🔌 NPU 리눅스 드라이버', ja: '🔌 NPU Linux ドライバ',
    'zh-CN': '🔌 NPU Linux 驱动', 'zh-TW': '🔌 NPU Linux 驅動程式',
    es: '🔌 Controlador Linux NPU',
  },
  '🛠️ DX-COM Compiler': {
    ko: '🛠️ DX-COM 컴파일러', ja: '🛠️ DX-COM コンパイラ',
    'zh-CN': '🛠️ DX-COM 编译器', 'zh-TW': '🛠️ DX-COM 編譯器',
    es: '🛠️ Compilador DX-COM',
  },
  '🔐 DEEPX Developers Portal Account': {
    ko: '🔐 DEEPX 개발자 포털 계정', ja: '🔐 DEEPX 開発者ポータルアカウント',
    'zh-CN': '🔐 DEEPX 开发者门户账户', 'zh-TW': '🔐 DEEPX 開發者入口網站帳戶',
    es: '🔐 Cuenta del portal de desarrolladores DEEPX',
  },

  /* ==== Compiler sections with emoji ==== */
  '⚡ Presets': {
    ko: '⚡ 프리셋', ja: '⚡ プリセット',
    'zh-CN': '⚡ 预设', 'zh-TW': '⚡ 預設',
    es: '⚡ Preajustes',
  },
  '📄 ONNX Model': {
    ko: '📄 ONNX 모델', ja: '📄 ONNX モデル',
    'zh-CN': '📄 ONNX 模型', 'zh-TW': '📄 ONNX 模型',
    es: '📄 Modelo ONNX',
  },
  '📋 Load JSON Config': {
    ko: '📋 JSON 구성 로드', ja: '📋 JSON 設定を読み込む',
    'zh-CN': '📋 加载 JSON 配置', 'zh-TW': '📋 載入 JSON 設定',
    es: '📋 Cargar configuración JSON',
  },
  '⚙️ Compile Settings': {
    ko: '⚙️ 컴파일 설정', ja: '⚙️ コンパイル設定',
    'zh-CN': '⚙️ 编译设置', 'zh-TW': '⚙️ 編譯設定',
    es: '⚙️ Configuración de compilación',
  },
  '�� Calibration Dataset': {
    ko: '📁 보정 데이터셋', ja: '📁 キャリブレーションデータセット',
    'zh-CN': '📁 校准数据集', 'zh-TW': '📁 校準資料集',
    es: '�� Conjunto de datos de calibración',
  },
  '🎨 Preprocessing Pipeline': {
    ko: '🎨 전처리 파이프라인', ja: '🎨 前処理パイプライン',
    'zh-CN': '🎨 预处理流水线', 'zh-TW': '🎨 前處理管線',
    es: '🎨 Pipeline de pre-procesamiento',
  },
  '🎯 PPU Settings (Object Detection only)': {
    ko: '🎯 PPU 설정 (객체 검출 전용)', ja: '🎯 PPU 設定 (物体検出専用)',
    'zh-CN': '🎯 PPU 设置 (仅目标检测)', 'zh-TW': '🎯 PPU 設定 (僅物件偵測)',
    es: '🎯 Configuración de PPU (solo detección de objetos)',
  },
  '📂 Output Settings': {
    ko: '📂 출력 설정', ja: '📂 出力設定',
    'zh-CN': '📂 输出设置', 'zh-TW': '📂 輸出設定',
    es: '📂 Configuración de salida',
  },
  '📋 Compile Log': {
    ko: '📋 컴파일 로그', ja: '📋 コンパイルログ',
    'zh-CN': '📋 编译日志', 'zh-TW': '📋 編譯日誌',
    es: '📋 Registro de compilación',
  },
  '📊 Compile Result': {
    ko: '📊 컴파일 결과', ja: '📊 コンパイル結果',
    'zh-CN': '📊 编译结果', 'zh-TW': '📊 編譯結果',
    es: '📊 Resultado de compilación',
  },
  '🔬 Model Visualization': {
    ko: '🔬 모델 시각화', ja: '🔬 モデル可視化',
    'zh-CN': '🔬 模型可视化', 'zh-TW': '🔬 模型視覺化',
    es: '🔬 Visualización del modelo',
  },
  '📜 Compile History': {
    ko: '📜 컴파일 이력', ja: '📜 コンパイル履歴',
    'zh-CN': '📜 编译历史', 'zh-TW': '📜 編譯歷史',
    es: '📜 Historial de compilación',
  },

  /* ==== Dashboard sections with emoji ==== */
  '📦 Export Model Package': {
    ko: '📦 모델 패키지 내보내기', ja: '📦 モデルパッケージのエクスポート',
    'zh-CN': '📦 导出模型包', 'zh-TW': '📦 匯出模型套件',
    es: '📦 Exportar paquete de modelo',
  },
  '🔄 Continuous Config': {
    ko: '🔄 연속 구성', ja: '🔄 連続設定',
    'zh-CN': '🔄 连续配置', 'zh-TW': '🔄 連續設定',
    es: '🔄 Configuración continua',
  },
  '📺 Live Display': {
    ko: '📺 라이브 디스플레이', ja: '📺 ライブ表示',
    'zh-CN': '📺 实时显示', 'zh-TW': '📺 即時顯示',
    es: '📺 Pantalla en vivo',
  },

  /* ==== Topbar page titles (with emoji) ==== */
  '⚙️ Setup & Install': {
    ko: '⚙️ 설정 & 설치', ja: '⚙️ セットアップ & インストール',
    'zh-CN': '⚙️ 设置 & 安装', 'zh-TW': '⚙️ 設定 & 安裝',
    es: '⚙️ Configuración e instalación',
  },

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
  'Unavailable': {
    ko: '사용 불가', ja: '利用不可',
    'zh-CN': '不可用', 'zh-TW': '不可用',
    es: 'No disponible',
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
    'zh-CN': '启动基准测试', 'zh-TW': '啟動基準測試',
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
    ko: '루프 카운트', ja: 'ループ回数',
    'zh-CN': '循环次数', 'zh-TW': '循環次數',
    es: 'Conteo de bucles',
  },
  'Results': {
    ko: '결과', ja: '結果',
    'zh-CN': '结果', 'zh-TW': '結果',
    es: 'Resultados',
  },
  'click row for detail': {
    ko: '행을 클릭하면 상세 보기', ja: '行をクリックして詳細を表示',
    'zh-CN': '点击行查看详情', 'zh-TW': '點擊行查看詳情',
    es: 'haga clic en la fila para detalles',
  },
  'FPS Comparison': {
    ko: 'FPS 비교', ja: 'FPS 比較',
    'zh-CN': 'FPS 比较', 'zh-TW': 'FPS 比較',
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
    ko: '리포트 내보내기', ja: 'レポートエクスポート',
    'zh-CN': '导出报告', 'zh-TW': '匯出報告',
    es: 'Exportar informe',
  },
  '⏱️ Start Benchmark': {
    ko: '⏱️ 벤치마크 시작', ja: '⏱️ ベンチマーク開始',
    'zh-CN': '⏱️ 启动基准测试', 'zh-TW': '⏱️ 啟動基準測試',
    es: '⏱️ Iniciar benchmark',
  },
  '📄 Export Report': {
    ko: '📄 리포트 내보내기', ja: '📄 レポートエクスポート',
    'zh-CN': '📄 导出报告', 'zh-TW': '📄 匯出報告',
    es: '📄 Exportar informe',
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
  '☑ All': {
    ko: '☑ 전체', ja: '☑ すべて',
    'zh-CN': '☑ 全部', 'zh-TW': '☑ 全部',
    es: '☑ Todo',
  },
  '☐ None': {
    ko: '☐ 해제', ja: '☐ なし',
    'zh-CN': '☐ 无', 'zh-TW': '☐ 無',
    es: '☐ Ninguno',
  },
  '📋 Models': {
    ko: '📋 모델', ja: '📋 モデル',
    'zh-CN': '📋 模型', 'zh-TW': '📋 模型',
    es: '📋 Modelos',
  },
  '⚙️ Settings': {
    ko: '⚙️ 설정', ja: '⚙️ 設定',
    'zh-CN': '⚙️ 设置', 'zh-TW': '⚙️ 設定',
    es: '⚙️ Configuración',
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
  '🧪 Test Run': {
    ko: '🧪 테스트 실행', ja: '🧪 テスト実行',
    'zh-CN': '🧪 测试运行', 'zh-TW': '🧪 測試執行',
    es: '🧪 Ejecución de prueba',
  },
  '🚀 Deploy & Run Now': {
    ko: '🚀 배포 & 즉시 실행', ja: '🚀 デプロイ & 今すぐ実行',
    'zh-CN': '🚀 部署 & 立即运行', 'zh-TW': '🚀 部署 & 立即執行',
    es: '🚀 Desplegar y ejecutar ahora',
  },
  '📊 Deploy & Benchmark': {
    ko: '📊 배포 & 벤치마크', ja: '📊 デプロイ & ベンチマーク',
    'zh-CN': '📊 Deploy & 基准测试', 'zh-TW': '📊 部署 & 基準測試',
    es: '📊 Desplegar y benchmark',
  },
  '📥 Download': {
    ko: '📥 다운로드', ja: '📥 ダウンロード',
    'zh-CN': '📥 下载', 'zh-TW': '📥 下載',
    es: '📥 Descargar',
  },
  '🔬 View DXNN Graph': {
    ko: '🔬 DXNN 그래프 보기', ja: '🔬 DXNNグラフを表示',
    'zh-CN': '🔬 查看 DXNN 图', 'zh-TW': '🔬 檢視 DXNN 圖',
    es: '🔬 Ver gráfico DXNN',
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
  '🧪 Test Result': {
    ko: '🧪 테스트 결과', ja: '🧪 テスト結果',
    'zh-CN': '🧪 测试结果', 'zh-TW': '🧪 測試結果',
    es: '🧪 Resultado de prueba',
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
  '📦 Export': {
    ko: '📦 내보내기', ja: '📦 エクスポート',
    'zh-CN': '📦 导出', 'zh-TW': '📦 匯出',
    es: '📦 Exportar',
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
  '❌ Error': {
    ko: '❌ 오류', ja: '❌ エラー',
    'zh-CN': '❌ 错误', 'zh-TW': '❌ 錯誤',
    es: '❌ Error',
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
  '▶ Run Pipeline': {
    ko: '▶ 파이프라인 실행', ja: '▶ パイプライン実行',
    'zh-CN': '▶ Run 流水线', 'zh-TW': '▶ Run 管線',
    es: '▶ Ejecutar pipeline',
  },

  /* ==== Compare ==== */
  'Select an image or video': {
    ko: '이미지 또는 비디오를 선택하세요', ja: '画像または動画を選択してください',
    'zh-CN': '请选择图像或视频', 'zh-TW': '請選擇影像或影片',
    es: 'Seleccione una imagen o vídeo',
  },
  'Select at least one model': {
    ko: '최소 하나의 모델을 선택하세요', ja: '少なくとも1つのモデルを選択してください',
    'zh-CN': '请至少选择一个模型', 'zh-TW': '請至少選擇一個模型',
    es: 'Seleccione al menos un modelo',
  },

  /* ==== File Browser ==== */
  '📂 Select Folder': {
    ko: '📂 폴더 선택', ja: '📂 フォルダ選択',
    'zh-CN': '📂 选择文件夹', 'zh-TW': '📂 選擇資料夾',
    es: '📂 Seleccionar carpeta',
  },
  '📄 Select File': {
    ko: '📄 파일 선택', ja: '📄 ファイル選択',
    'zh-CN': '📄 选择文件', 'zh-TW': '📄 選擇檔案',
    es: '📄 Seleccionar archivo',
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

  /* ==== Forum (reverse) ==== */
  'Please enter comment content': {
    ko: '댓글 내용을 입력하세요', ja: 'コメント内容を入力してください',
    'zh-CN': '请输入评论内容', 'zh-TW': '請輸入留言內容',
    es: 'Por favor introduzca contenido del comentario',
  },
  'Comment posted 🎉': {
    ko: '댓글이 등록되었습니다 🎉', ja: 'コメントが投稿されました 🎉',
    'zh-CN': '评论已发布 🎉', 'zh-TW': '留言已發布 🎉',
    es: '¡Comentario publicado 🎉',
  },
  'Please enter a title': {
    ko: '제목을 입력하세요', ja: 'タイトルを入力してください',
    'zh-CN': '请输入标题', 'zh-TW': '請輸入標題',
    es: 'Por favor introduzca un título',
  },
  'Please enter content': {
    ko: '내용을 입력하세요', ja: '内容を入力してください',
    'zh-CN': '请输入内容', 'zh-TW': '請輸入內容',
    es: 'Por favor introduzca contenido',
  },
  'Post published 🎉': {
    ko: '게시물이 등록되었습니다 🎉', ja: '投稿が公開されました 🎉',
    'zh-CN': '帖子已发布 🎉', 'zh-TW': '文章已發布 🎉',
    es: '¡Publicación publicada 🎉',
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
  '⚠ Model file not configured for ': {
    ko: '⚠ 모델 파일이 설정되지 않음: ', ja: '⚠ モデルファイル未設定: ',
    'zh-CN': '⚠ 模型文件未配置: ', 'zh-TW': '⚠ 模型檔案未設定: ',
    es: '⚠ Archivo de modelo no configurado para ',
  },
  '⚠ Model file missing: ': {
    ko: '⚠ 모델 파일 누락: ', ja: '⚠ モデルファイル欠落: ',
    'zh-CN': '⚠ 模型文件缺失: ', 'zh-TW': '⚠ 模型檔案遺失: ',
    es: '⚠ Archivo de modelo faltante: ',
  },
  '⚠ C++ binary not built for ': {
    ko: '⚠ C++ 바이너리가 빌드되지 않음: ', ja: '⚠ C++ バイナリ未ビルド: ',
    'zh-CN': '⚠ C++ 二进制文件未构建: ', 'zh-TW': '⚠ C++ 二進位檔未建置: ',
    es: '⚠ Binario C++ no compilado para ',
  },
  '⚠ Python app not found for ': {
    ko: '⚠ Python 앱을 찾을 수 없음: ', ja: '⚠ Python アプリが見つかりません: ',
    'zh-CN': '⚠ 未找到 Python 应用: ', 'zh-TW': '⚠ 未找到 Python 應用: ',
    es: '⚠ Aplicación Python no encontrada para ',
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

  /* ==== Forum (extra) ==== */
  'just now': {
    ko: '방금 전', ja: 'たった今',
    'zh-CN': '刚刚', 'zh-TW': '剛剛',
    es: 'ahora mismo',
  },
  ' min ago': {
    ko: '분 전', ja: ' 分前',
    'zh-CN': ' 分钟前', 'zh-TW': ' 分鐘前',
    es: ' hace min',
  },
  ' hours ago': {
    ko: '시간 전', ja: ' 時間前',
    'zh-CN': ' 小时前', 'zh-TW': ' 小時前',
    es: ' hace horas',
  },
  ' days ago': {
    ko: '일 전', ja: ' 日前',
    'zh-CN': ' 天前', 'zh-TW': ' 天前',
    es: ' hace días',
  },
  'Ask DeepX': {
    ko: 'DeepX에게 질문', ja: 'DeepX に質問',
    'zh-CN': '向 DeepX 提问', 'zh-TW': '向 DeepX 提問',
    es: 'Preguntar a DeepX',
  },
  'Community': {
    ko: '커뮤니티', ja: 'コミュニティ',
    'zh-CN': '社区', 'zh-TW': '社群',
    es: 'Comunidad',
  },

  /* ==== Community page buttons ==== */
  'All': {
    ko: '전체', ja: 'すべて',
    'zh-CN': '全部', 'zh-TW': '全部',
    es: 'Todo',
  },
  '🏢 Ask DeepX': {
    ko: '🏢 DeepX에게 질문', ja: '🏢 DeepX に質問',
    'zh-CN': '🏢 向 DeepX 提问', 'zh-TW': '🏢 向 DeepX 提問',
    es: '🏢 Preguntar a DeepX',
  },
  '💬 Community': {
    ko: '💬 커뮤니티', ja: '💬 コミュニティ',
    'zh-CN': '💬 社区', 'zh-TW': '💬 社群',
    es: '💬 Comunidad',
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
  '✏️ New Post': {
    ko: '✏️ 새 글 작성', ja: '✏️ 新規投稿',
    'zh-CN': '✏️ 新帖子', 'zh-TW': '✏️ 新貼文',
    es: '✏️ Nueva publicación',
  },

  /* ==== Model source option ==== */
  '🔒 Internal (Air-gapped)': {
    ko: '🔒 Internal (폐쇄망)', ja: '🔒 Internal (エアギャップ)',
    'zh-CN': '🔒 Internal (离线)', 'zh-TW': '🔒 Internal (離線)',
    es: '🔒 Interno (Air-gapped)',
  },

  /* ==== Page descriptions ==== */
  'Ask questions to the DeepX team or share experiences with other users. 🌐': {
    ko: 'DeepX 팀에게 질문하거나, 사용자들과 경험을 나눠보세요. 🌐', ja: 'DeepX チームへの質問や他のユーザーとの経験共有ができます。🌐',
    'zh-CN': '向 DeepX 团队提问或与其他用户分享经验。🌐', 'zh-TW': '向 DeepX 團隊提問或與其他使用者分享經驗。🌐',
    es: 'Haga preguntas al equipo de DeepX o comparta experiencias con otros usuarios. 🌐',
  },
  'Detailed guides, parameters, workflows, and tips for each DX-APP feature — all in one place.': {
    ko: 'DX-APP 기능별 상세 가이드 · 파라미터 · 워크플로우 · 팁을 한 곳에서 확인하세요.', ja: 'DX-APP 機能ごとの詳細ガイド・パラメータ・ワークフロー・ヒントをまとめて確認できます。',
    'zh-CN': 'DX-APP 各功能的详细指南、参数、工作流程和技巧 — 一站式查阅。', 'zh-TW': 'DX-APP 各功能的詳細指南、參數、工作流程和技巧 — 一站式查閱。',
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
  'ModelZoo': { ko: 'ModelZoo', ja: 'ModelZoo', 'zh-CN': 'ModelZoo', 'zh-TW': 'ModelZoo',es:'ModelZoo'},
  'Install dependencies and build each component from this page. Run top-to-bottom, left-to-right.': {
    ko: '이 페이지에서 종속성을 설치하고 각 구성 요소를 빌드하세요. 위에서 아래로, 왼쪽에서 오른쪽으로 실행합니다.',
    ja: 'このページから依存関係をインストールし、各コンポーネントをビルドしてください。上から下、左から右の順に実行します。',
    'zh-CN': '从此页面安装依赖项并构建各组件。按从上到下、从左到右的顺序执行。',
    'zh-TW': '從此頁面安裝相依套件並建置各元件。按從上到下、從左到右的順序執行。',
    es: 'Instale dependencias y compile cada componente desde esta página. Ejecute de arriba a abajo, de izquierda a derecha.',
  },
  'Install system packages required for C++ build (cmake, gcc, ninja, OpenCV, …) →': {
    ko: 'C++ 빌드에 필요한 시스템 패키지 설치 (cmake, gcc, ninja, OpenCV, …) →',
    ja: 'C++ ビルドに必要なシステムパッケージをインストール (cmake, gcc, ninja, OpenCV, …) →',
    'zh-CN': '安装 C++ 构建所需的系统包 (cmake, gcc, ninja, OpenCV, …) →',
    'zh-TW': '安裝 C++ 建置所需的系統套件 (cmake, gcc, ninja, OpenCV, …) →',
    es: 'Instale los paquetes del sistema requeridos para la compilación C++ (cmake, gcc, ninja, OpenCV, …) →',
  },
  'Compile C++ demo binaries (cmake) →': {
    ko: 'C++ 데모 바이너리 컴파일 (cmake) →',
    ja: 'C++ デモバイナリをコンパイル (cmake) →',
    'zh-CN': '编译 C++ 演示二进制文件 (cmake) →',
    'zh-TW': '編譯 C++ 展示二進位檔 (cmake) →',
    es: 'Compile binarios de demo C++ (cmake) →',
  },
  'Download sample models & videos for Run / Benchmark demos →': {
    ko: 'Run / Benchmark 데모용 샘플 모델 및 비디오 다운로드 →',
    ja: 'Run / Benchmark デモ用のサンプルモデルと動画をダウンロード →',
    'zh-CN': '下载 Run / Benchmark 演示用的示例模型和视频 →',
    'zh-TW': '下載 Run / Benchmark 展示用的範例模型和影片 →',
    es: 'Descargue modelos y videos de ejemplo para demos de Ejecución / Benchmark →',
  },
  'Install packages required for NPU runtime (cmake, ONNX Runtime, …) →': {
    ko: 'NPU 런타임에 필요한 패키지 설치 (cmake, ONNX Runtime, …) →',
    ja: 'NPU ランタイムに必要なパッケージをインストール (cmake, ONNX Runtime, …) →',
    'zh-CN': '安装 NPU 运行时所需的软件包 (cmake, ONNX Runtime, …) →',
    'zh-TW': '安裝 NPU 執行環境所需的套件 (cmake, ONNX Runtime, …) →',
    es: 'Instale los paquetes requeridos para el runtime NPU (cmake, ONNX Runtime, …) →',
  },
  'Install DEEPX NPU kernel driver (requires sudo) →': {
    ko: 'DEEPX NPU 커널 드라이버 설치 (sudo 필요) →',
    ja: 'DEEPX NPU カーネルドライバをインストール (sudo 必要) →',
    'zh-CN': '安装 DEEPX NPU 内核驱动 (需要 sudo) →',
    'zh-TW': '安裝 DEEPX NPU 核心驅動 (需要 sudo) →',
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
  'Run Diagnostics': { ko: '진단 실행', ja: '診断を実行', 'zh-CN': '运行诊断', 'zh-TW': '執行診斷',es:'Ejecutar diagnóstico'},
  'Comprehensive system health check: PCIe link, kernel modules, DKMS, services, CLI tools, Python venv, disk, memory, model integrity.': {
    ko: '시스템 종합 진단: PCIe 링크, 커널 모듈, DKMS, 서비스, CLI 도구, Python 가상환경, 디스크, 메모리, 모델 무결성.',
    ja: 'システム総合ヘルスチェック：PCIe リンク、カーネルモジュール、DKMS、サービス、CLI ツール、Python 仮想環境、ディスク、メモリ、モデル整合性。',
    'zh-CN': '系统综合健康检查：PCIe 链路、内核模块、DKMS、服务、CLI 工具、Python 虚拟环境、磁盘、内存、模型完整性。',
    'zh-TW': '系統綜合健康檢查：PCIe 連結、核心模組、DKMS、服務、CLI 工具、Python 虛擬環境、磁碟、記憶體、模型完整性。',
    es: 'Verificación integral del estado del sistema: enlace PCIe, módulos del kernel, DKMS, servicios, herramientas CLI, Python venv, disco, memoria, integridad del modelo.',
  },
  'Actions': { ko: '작업', ja: 'アクション', 'zh-CN': '操作', 'zh-TW': '操作',es:'Acciones'},
  'Passed to the model\'s config.json as score_threshold / nms_threshold': {
    ko: '모델의 config.json에 score_threshold / nms_threshold로 전달됩니다',
    ja: 'モデルの config.json に score_threshold / nms_threshold として渡されます',
    es: 'Se pasa al config.json del modelo como score_threshold / nms_threshold',
    'zh-CN': '作为 score_threshold / nms_threshold 传递给模型的 config.json',
    'zh-TW': '作為 score_threshold / nms_threshold 傳遞給模型的 config.json'
  },
  'Profiler': { ko: '프로파일러', ja: 'プロファイラー', 'zh-CN': '性能分析器', 'zh-TW': '分析器',es:'Perfilador'},
  'Profiler Timeline': { ko: '프로파일러 타임라인', ja: 'プロファイラー タイムライン', 'zh-CN': '性能分析器时间轴', 'zh-TW': '分析器時間軸',es:'Línea de tiempo del perfilador'},
  'Reset Zoom': { ko: '줌 초기화', ja: 'ズームをリセット', 'zh-CN': '重置缩放', 'zh-TW': '重設縮放',es:'Restablecer zoom'},
  'Extract the selected model\'s source code, config, and model file as a package. Available for download on the Outputs page.': {
    ko: '선택한 모델의 소스 코드, 설정, 모델 파일을 패키지로 추출합니다. Outputs 페이지에서 다운로드할 수 있습니다.',
    ja: '選択したモデルのソースコード、設定、モデルファイルをパッケージとして抽出します。Outputs ページでダウンロードできます。',
    'zh-CN': '将所选模型的源代码、配置和模型文件打包提取。可在 Outputs 页面下载。',
    'zh-TW': '將所選模型的原始碼、設定和模型檔案打包匯出。可在 Outputs 頁面下載。',
    es: 'Extraiga el código fuente, configuración y archivo de modelo del modelo seleccionado como paquete. Disponible para descarga en la página de Salidas.',
  },
  'Camera Device': { ko: '카메라 장치', ja: 'カメラデバイス', 'zh-CN': '摄像头设备', 'zh-TW': '攝影機裝置',es:'Dispositivo de cámara'},
  'RTSP Server': { ko: 'RTSP 서버', ja: 'RTSP サーバー', 'zh-CN': 'RTSP 服务器', 'zh-TW': 'RTSP 伺服器',es:'Servidor RTSP'},
  'Stream': { ko: '스트림', ja: 'ストリーム', 'zh-CN': '串流', 'zh-TW': '串流',es:'Flujo'},
  'Settings': { ko: '설정', ja: '設定', 'zh-CN': '设置', 'zh-TW': '設定',es:'Configuración'},
  'None': { ko: '해제', ja: 'なし', 'zh-CN': '无', 'zh-TW': '無',es:'Ninguno'},
  'Latency(ms)': { ko: '지연시간(ms)', ja: 'レイテンシ(ms)', 'zh-CN': '延迟(ms)', 'zh-TW': '延遲(ms)',es:'Latencia (ms)'},
  'Slots:': { ko: '슬롯:', ja: 'スロット:', 'zh-CN': '插槽:', 'zh-TW': '插槽:',es:'Ranuras:'},
  'Shared Input (Image / Video)': { ko: '공유 입력 (이미지 / 동영상)', ja: '共有入力 (画像 / 動画)', 'zh-CN': '共享输入 (图片 / 视频)', 'zh-TW': '共用輸入 (影像 / 影片)',es:'Entrada compartida (Imagen / Vídeo)'},
  'Camera': { ko: '카메라', ja: 'カメラ', 'zh-CN': '摄像头', 'zh-TW': '攝影機',es:'Cámara'},
  'Browse the DEEPX ModelZoo — select models and download Q-Lite / Q-Pro DXNN files directly.': {
    ko: 'DEEPX 모델 저장소를 탐색하세요 — 모델을 선택하고 Q-Lite / Q-Pro DXNN 파일을 직접 다운로드합니다.',
    ja: 'DEEPX ModelZoo を閲覧 — モデルを選択し、Q-Lite / Q-Pro DXNN ファイルを直接ダウンロードできます。',
    'zh-CN': '浏览 DEEPX 模型库 — 选择模型并直接下载 Q-Lite / Q-Pro DXNN 文件。',
    'zh-TW': '瀏覽 DEEPX 模型庫 — 選擇模型並直接下載 Q-Lite / Q-Pro DXNN 檔案。',
    es: 'Explore el DEEPX ModelZoo — seleccione modelos y descargue archivos DXNN Q-Lite / Q-Pro directamente.',
  },
  'ModelZoo Homepage': { ko: 'ModelZoo 홈페이지', ja: 'ModelZoo ホームページ', 'zh-CN': 'ModelZoo 主页', 'zh-TW': 'ModelZoo 首頁',es:'Página principal de ModelZoo'},
  'Source': { ko: '소스', ja: 'ソース', 'zh-CN': '来源', 'zh-TW': '來源',es:'Fuente'},
  'New Only': { ko: '새 항목만', ja: '新規のみ', 'zh-CN': '仅新增', 'zh-TW': '僅新增',es:'Solo nuevos'},
  'Q-Lite All': { ko: 'Q-Lite 전체', ja: 'Q-Lite 全て', 'zh-CN': 'Q-Lite 全部', 'zh-TW': 'Q-Lite 全部',es:'Todo Q-Lite'},
  'Q-Pro All': { ko: 'Q-Pro 전체', ja: 'Q-Pro 全て', 'zh-CN': 'Q-Pro 全部', 'zh-TW': 'Q-Pro 全部',es:'Todo Q-Pro'},
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
  'Before': { ko: '이전', ja: '変換前', 'zh-CN': '转换前', 'zh-TW': '轉換前',es:'Antes'},
  'After': { ko: '이후', ja: '変換後', 'zh-CN': '转换后', 'zh-TW': '轉換後',es:'Después'},
  'Detail': { ko: '상세', ja: '詳細', 'zh-CN': '详情', 'zh-TW': '詳情',es:'Detalle'},
  'Drag on the image to select a Region of Interest (ROI).✅ Only the selected area will be auto-cropped for inference. Click Apply then Run Inference to infer the ROI only.': {
    ko: '이미지 위에서 드래그하여 관심 영역(ROI)을 선택하세요.✅ 선택한 영역만 추론을 위해 자동 잘림됩니다. Apply를 클릭한 후 Run Inference를 실행하면 ROI만 추론합니다.',
    ja: '画像上でドラッグして関心領域 (ROI) を選択してください。✅ 選択した領域のみが推論用に自動クロップされます。Apply をクリックして Run Inference を実行すると ROI のみを推論します。',
    'zh-CN': '在图片上拖拽选择感兴趣区域 (ROI)。✅ 仅所选区域会被自动裁剪用于推理。点击 Apply 后执行 Run Inference 即可仅对 ROI 进行推理。',
    'zh-TW': '在影像上拖曳選擇感興趣區域 (ROI)。✅ 僅所選區域會被自動裁切用於推論。點擊 Apply 後執行 Run Inference 即可僅對 ROI 進行推論。',
    es: 'Arrastre sobre la imagen para seleccionar una Región de Interés (ROI).✅ Solo el área seleccionada se recortará automáticamente para inferencia. Haga clic en Aplicar y luego en Ejecutar inferencia para inferir solo el ROI.',
  },
  'This will permanently delete model source files from disk.': {
    ko: '디스크에서 모델 소스 파일이 영구적으로 삭제됩니다.',
    ja: 'ディスクからモデルソースファイルが永久に削除されます。',
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
    ja: '生成するファイル：Factory インターフェース、Postprocessor、Visualizer、Sync/Async Runner (C++)、Postprocessor/Visualizer (Python)',
    'zh-CN': '将生成的文件：Factory 接口、Postprocessor、Visualizer、Sync/Async Runner (C++)、Postprocessor/Visualizer (Python)',
    'zh-TW': '將產生的檔案：Factory 介面、Postprocessor、Visualizer、Sync/Async Runner (C++)、Postprocessor/Visualizer (Python)',
    es: 'Archivos a generar: interfaz Factory, Postprocessor, Visualizer, Runner Sync/Async (C++), Postprocessor/Visualizer (Python)',
  },
  'Packages are saved to outputs/ directory. Use the Outputs page to download.': {
    ko: '패키지는 outputs/ 디렉토리에 저장됩니다. Outputs 페이지에서 다운로드하세요.',
    ja: 'パッケージは outputs/ ディレクトリに保存されます。Outputs ページからダウンロードしてください。',
    'zh-CN': '包已保存至 outputs/ 目录。请在 Outputs 页面下载。',
    'zh-TW': '套件已儲存至 outputs/ 目錄。請在 Outputs 頁面下載。',
    es: 'Los paquetes se guardan en el directorio outputs/. Use la página de Salidas para descargar.',
  },
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
    es: '/path/to/model.onnx',
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
  '🔍 Search…': {
    ko: '🔍 검색…', ja: '🔍 検索…',
    'zh-CN': '🔍 搜索…', 'zh-TW': '🔍 搜尋…',
    es: '🔍 Buscar…',
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
    ko: '손잡이', ja: '利き手',
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
    'zh-CN': '人脸总数', 'zh-TW': '總面部',
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
  '📊 DX-APP Benchmark Report': {
    ko: '📊 DX-APP 벤치마크 리포트', ja: '📊 DX-APP ベンチマークレポート',
    'zh-CN': '📊 DX-APP 基准测试报告', 'zh-TW': '📊 DX-APP 基準測試報告',
    es: '📊 Informe de benchmark DX-APP',
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
  '⏳ Compiling…': {
    ko: '⏳ 컴파일 중…', ja: '⏳ コンパイル中…',
    'zh-CN': '⏳ 编译中…', 'zh-TW': '⏳ 編譯中…',
    es: '⏳ Compilando…',
  },
  '✅ Compilation succeeded': {
    ko: '✅ 컴파일 성공', ja: '✅ コンパイル成功',
    'zh-CN': '✅ 编译成功', 'zh-TW': '✅ 編譯成功',
    es: '✅ Compilación exitosa',
  },
  '❌ Compilation failed': {
    ko: '❌ 컴파일 실패', ja: '❌ コンパイル失敗',
    'zh-CN': '❌ 编译失败', 'zh-TW': '❌ 編譯失敗',
    es: '❌ Compilación fallida',
  },
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
  '📋 Full Output': {
    ko: '📋 전체 출력', ja: '📋 全出力',
    'zh-CN': '📋 完整输出', 'zh-TW': '📋 完整輸出',
    es: '📋 Salida completa',
  },
  '🔋 Benchmark Detail — ': {
    ko: '🔋 벤치마크 상세 — ', ja: '🔋 ベンチマーク詳細 — ',
    'zh-CN': '🔋 基准测试详情 — ', 'zh-TW': '🔋 基準測試詳情 — ',
    es: '🔋 Detalle de benchmark — ',
  },
  'elapsed: ': {
    ko: '경과: ', ja: '経過: ',
    'zh-CN': '已用时间: ', 'zh-TW': '已用時間: ',
    es: 'transcurrido: ',
  },
  '⚠️ Run Error:': {
    ko: '⚠️ 실행 오류:', ja: '⚠️ 実行エラー:',
    'zh-CN': '⚠️ 运行错误:', 'zh-TW': '⚠️ 執行錯誤:',
    es: '⚠️ Error de ejecución:',
  },
  '⚡ Latency Analysis': {
    ko: '⚡ 지연시간 분석', ja: '⚡ レイテンシ分析',
    'zh-CN': '⚡ 延迟分析', 'zh-TW': '⚡ 延遲分析',
    es: '⚡ Análisis de latencia',
  },
  '❌ Error Details': {
    ko: '❌ 오류 상세', ja: '❌ エラー詳細',
    'zh-CN': '❌ 错误详情', 'zh-TW': '❌ 錯誤詳情',
    es: '❌ Detalles del error',
  },
  '❌ Runtime Errors': {
    ko: '❌ 런타임 오류', ja: '❌ ランタイムエラー',
    'zh-CN': '❌ 运行时错误', 'zh-TW': '❌ 執行階段錯誤',
    es: '❌ Errores de ejecución',
  },
  '⚠️ Accuracy Failures': {
    ko: '⚠️ 정확도 실패', ja: '⚠️ 精度失敗',
    'zh-CN': '⚠️ 准确性失败', 'zh-TW': '⚠️ 準確度失敗',
    es: '⚠️ Fallos de precisión',
  },
  '🏅 Power Efficiency (FPS / Watt)': {
    ko: '🏅 전력 효율 (FPS / Watt)', ja: '🏅 電力効率 (FPS / Watt)',
    'zh-CN': '🏅 能效比 (FPS / Watt)', 'zh-TW': '🏅 能效比 (FPS / Watt)',
    es: '🏅 Eficiencia energética (FPS / Watt)',
  },
  '🏆 Performance Ranking': {
    ko: '🏆 성능 순위', ja: '🏆 パフォーマンスランキング',
    'zh-CN': '🏆 性能排名', 'zh-TW': '🏆 效能排名',
    es: '🏆 Clasificación de rendimiento',
  },
  '📂 Category Summary': {
    ko: '📂 카테고리 요약', ja: '📂 カテゴリ概要',
    'zh-CN': '📂 类别摘要', 'zh-TW': '📂 類別摘要',
    es: '📂 Resumen de categoría',
  },
  '📈 FPS vs Latency': {
    ko: '📈 FPS 대 지연시간', ja: '📈 FPS vs レイテンシ',
    'zh-CN': '📈 FPS 与延迟', 'zh-TW': '📈 FPS 與延遲',
    es: '📈 FPS vs Latencia',
  },
  '🔧 Hardware Resources (Post-Run)': {
    ko: '🔧 하드웨어 리소스 (실행 후)', ja: '🔧 ハードウェアリソース (実行後)',
    'zh-CN': '🔧 硬件资源 (运行后)', 'zh-TW': '🔧 硬體資源 (執行後)',
    es: '🔧 Recursos de hardware (post-ejecución)',
  },
  '🖥️ Environment': {
    ko: '🖥️ 환경', ja: '🖥️ 環境',
    'zh-CN': '🖥️ 环境', 'zh-TW': '🖥️ 環境',
    es: '🖥️ Entorno',
  },
  '🖼️ Result Gallery': {
    ko: '🖼️ 결과 갤러리', ja: '🖼️ 結果ギャラリー',
    'zh-CN': '🖼️ 结果画廊', 'zh-TW': '🖼️ 結果圖庫',
    es: '🖼️ Galería de resultados',
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
  'Select a model and click ▶ Run All': {
    ko: '모델을 선택하고 ▶ 전체 실행을 클릭하세요', ja: 'モデルを選択して ▶ 全て実行 をクリックしてください',
    'zh-CN': '选择模型并点击 ▶ 全部运行', 'zh-TW': '選擇模型並點擊 ▶ 全部執行',
    es: 'Seleccione un modelo y haga clic en ▶ Ejecutar todo',
  },
  'Task Filter': {
    ko: '태스크 필터', ja: 'タスクフィルター',
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
    ko: '" 이 자동 선택됩니다', ja: '" が自動選択されます',
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
  'Running inference…': {
    ko: '추론 실행 중…', ja: '推論実行中…',
    'zh-CN': '正在运行推理…', 'zh-TW': '正在執行推論…',
    es: 'Ejecutando inferencia…',
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
  '⚠️ Status check failed': {
    ko: '⚠️ 상태 확인 실패', ja: '⚠️ ステータス確認失敗',
    'zh-CN': '⚠️ 状态检查失败', 'zh-TW': '⚠️ 狀態檢查失敗',
    es: '⚠️ Verificación de estado fallida',
  },
  '📊 Navigating to Benchmark — "': {
    ko: '📊 벤치마크로 이동 — "', ja: '📊 ベンチマークに移動 — "',
    es: '📊 Navegando a Benchmark — "',
    'zh-CN': '📊 正在导航到基准测试 — "', 'zh-TW': '📊 前往基準測試 — "'
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
  '⏳ Loading…': {
    ko: '⏳ 불러오는 중…', ja: '⏳ 読み込み中…',
    'zh-CN': '⏳ 加载中…', 'zh-TW': '⏳ 載入中…',
    es: '⏳ Cargando…',
  },
  '⚠️ Failed to load. Please check the server.': {
    ko: '⚠️ 불러오기 실패. 서버를 확인하세요.', ja: '⚠️ 読み込みに失敗しました。サーバーを確認してください。',
    'zh-CN': '⚠️ 加载失败，请检查服务器。', 'zh-TW': '⚠️ 載入失敗，請檢查伺服器。',
    es: '⚠️ Error al cargar. Por favor verifique el servidor.',
  },
  '✅ Submit': {
    ko: '✅ 등록', ja: '✅ 送信',
    'zh-CN': '✅ 提交', 'zh-TW': '✅ 提交',
    es: '✅ Enviar',
  },
  '👍 Recommend': {
    ko: '👍 추천', ja: '👍 おすすめ',
    'zh-CN': '👍 推荐', 'zh-TW': '👍 推薦',
    es: '👍 Recomendar',
  },
  '💬 Comments': {
    ko: '💬 댓글', ja: '💬 コメント',
    'zh-CN': '💬 评论', 'zh-TW': '💬 留言',
    es: '💬 Comentarios',
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
  '❌ Error: ': {
    ko: '❌ 오류: ', ja: '❌ エラー: ',
    'zh-CN': '❌ 错误: ', 'zh-TW': '❌ 錯誤: ',
    es: '❌ Error: ',
  },
  'ℹ️ No result video was generated': {
    ko: 'ℹ️ 결과 비디오가 생성되지 않았습니다', ja: 'ℹ️ 結果ビデオが生成されませんでした',
    'zh-CN': 'ℹ️ 未生成结果视频', 'zh-TW': 'ℹ️ 未產生結果影片',
    es: 'ℹ️ No se generó vídeo de resultado',
  },
  '⏳ Processing...': {
    ko: '⏳ 처리 중...', ja: '⏳ 処理中...',
    'zh-CN': '⏳ 处理中...', 'zh-TW': '⏳ 處理中...',
    es: '⏳ Procesando...',
  },
  '⏳ Waiting…': {
    ko: '⏳ 대기 중…', ja: '⏳ 待機中…',
    'zh-CN': '⏳ 等待中…', 'zh-TW': '⏳ 等待中…',
    es: '⏳ Esperando…',
  },
  '⏹ Stopped': {
    ko: '⏹ 중지됨', ja: '⏹ 停止',
    'zh-CN': '⏹ 已停止', 'zh-TW': '⏹ 已停止',
    es: '⏹ Detenido',
  },
  '▶ Press Start to begin inference': {
    ko: '▶ 시작 버튼을 눌러 추론을 시작하세요', ja: '▶ 開始ボタンを押して推論を開始してください',
    'zh-CN': '▶ 按“开始”按钮以开始推理', 'zh-TW': '▶ 按「開始」按鈕以開始推論',
    es: '▶ Presione Iniciar para comenzar la inferencia',
  },
  '⚠️ Inference exited abnormally (exit code: ': {
    ko: '⚠️ 추론이 비정상적으로 종료되었습니다 (종료 코드: ', ja: '⚠️ 推論が異常終了しました（終了コード: ',
    'zh-CN': '⚠️ 推理异常退出（退出代码: ', 'zh-TW': '⚠️ 推論異常結束（結束代碼: ',
    es: '⚠️ La inferencia terminó de forma anormal (código de salida: ',
  },
  '✅ Extraction complete! Output: ': {
    ko: '✅ 추출 완료! 출력: ', ja: '✅ 抽出完了！出力: ',
    'zh-CN': '✅ 提取完成！输出: ', 'zh-TW': '✅ 擷取完成！輸出: ',
    es: '✅ ¡Extracción completa! Salida: ',
  },
  '✅ ROI selected': {
    ko: '✅ ROI 선택됨', ja: '✅ ROI 選択済み',
    'zh-CN': '✅ ROI 已选择', 'zh-TW': '✅ ROI 已選擇',
    es: '✅ ROI seleccionado',
  },
  '✨ Enhancement Result: outputs the image with improved brightness and contrast.': {
    ko: '✨ Enhancement 결과: 밝기와 대비가 개선된 이미지를 출력합니다.', ja: '✨ Enhancement 結果: 明るさとコントラストが改善された画像を出力します。',
    'zh-CN': '✨ Enhancement 结果：输出亮度和对比度增强后的图像。', 'zh-TW': '✨ Enhancement 結果：輸出亮度和對比度增強後的影像。',
    es: '✨ Resultado de mejora: genera la imagen con brillo y contraste mejorados.',
  },
  '🌈 Depth Result: visualizes depth using JET colormap (red=near, blue=far).': {
    ko: '🌈 Depth 결과: JET 컬러맵으로 깊이를 시각화합니다 (빨강=가까움, 파랑=멀리).', ja: '🌈 Depth 結果: JET カラーマップで深度を可視化します（赤=近い、青=遠い）。',
    'zh-CN': '🌈 Depth 结果：使用 JET 色图可视化深度（红色=近，蓝色=远）。', 'zh-TW': '🌈 Depth 結果：使用 JET 色圖視覺化深度（紅色=近，藍色=遠）。',
    es: '🌈 Resultado de profundidad: visualiza la profundidad usando el mapa de colores JET (rojo=cerca, azul=lejos).',
  },
  '🎨 Semantic Segmentation: alpha-blends per-pixel class labels using Cityscapes colormap onto the original.': {
    ko: '🎨 Semantic Segmentation: Cityscapes 컬러맵을 사용하여 픽셀별 클래스 레이블을 원본에 알파 블렌딩합니다.', ja: '🎨 Semantic Segmentation: Cityscapes カラーマップを使用してピクセルごとのクラスラベルを元画像にアルファブレンドします。',
    'zh-CN': '🎨 Semantic Segmentation：使用 Cityscapes 色图将逐像素类别标签与原图进行 Alpha 混合。', 'zh-TW': '🎨 Semantic Segmentation：使用 Cityscapes 色圖將逐像素類別標籤與原圖進行 Alpha 混合。',
    es: '🎨 Segmentación semántica: mezcla alfa de etiquetas de clase por píxel usando el mapa de colores Cityscapes sobre la imagen original.',
  },
  '🎭 Instance Segmentation: draws per-instance color masks + bounding boxes + class labels.': {
    ko: '🎭 Instance Segmentation: 인스턴스별 컬러 마스크 + 바운딩 박스 + 클래스 레이블을 표시합니다.', ja: '🎭 Instance Segmentation: インスタンスごとのカラーマスク＋バウンディングボックス＋クラスラベルを描画します。',
    'zh-CN': '🎭 Instance Segmentation：绘制逐实例颜色掩码 + 边界框 + 类别标签。', 'zh-TW': '🎭 Instance Segmentation：繪製逐實例顏色遮罩 + 邊界框 + 類別標籤。',
    es: '🎭 Segmentación de instancias: dibuja máscaras de color por instancia + cuadros delimitadores + etiquetas de clase.',
  },
  '🎯 ROI applied — only the selected region was inferred.': {
    ko: '🎯 ROI 적용됨 — 선택한 영역만 추론되었습니다.', ja: '🎯 ROI 適用済み — 選択された領域のみ推論されました。',
    'zh-CN': '🎯 ROI 已应用 — 仅对选定区域进行了推理。', 'zh-TW': '🎯 ROI 已套用 — 僅對選定區域進行了推論。',
    es: '🎯 ROI aplicado — solo se infirió la región seleccionada.',
  },
  '💃 Pose Estimation: draws skeleton (joint connections) and keypoints. Low-confidence keypoints may be omitted.': {
    ko: '💃 Pose Estimation: 스켈레톤(관절 연결)과 키포인트를 표시합니다. 신뢰도가 낮은 키포인트는 생략될 수 있습니다.', ja: '💃 Pose Estimation: スケルトン（関節接続）とキーポイントを描画します。信頼度の低いキーポイントは省略される場合があります。',
    'zh-CN': '💃 Pose Estimation：绘制骨架（关节连接）和关键点。低置信度关键点可能会被省略。', 'zh-TW': '💃 Pose Estimation：繪製骨架（關節連接）和關鍵點。低信賴度關鍵點可能會被省略。',
    es: '💃 Estimación de pose: dibuja el esqueleto (conexiones articulares) y puntos clave. Los puntos clave de baja confianza pueden omitirse.',
  },
  '📊 Classification Result: overlays Top-K predicted classes and probabilities as text on the image.': {
    ko: '📊 Classification 결과: Top-K 예측 클래스와 확률을 이미지 위에 텍스트로 표시합니다.', ja: '📊 Classification 結果: Top-K 予測クラスと確率をテキストとして画像上にオーバーレイします。',
    'zh-CN': '📊 Classification 结果：将 Top-K 预测类别和概率以文本形式叠加在图像上。', 'zh-TW': '📊 Classification 結果：將 Top-K 預測類別和機率以文字形式疊加在影像上。',
    es: '📊 Resultado de clasificación: superpone las clases predichas Top-K y sus probabilidades como texto en la imagen.',
  },
  '🏷️ Attribute Result: overlays predicted person/face attributes and confidence scores on the image.': {
    ko: '🏷️ Attribute 결과: 예측된 사람/얼굴 속성과 신뢰도 점수를 이미지 위에 텍스트로 표시합니다.', ja: '🏷️ Attribute 結果: 予測された人物/顔属性と信頼度スコアを画像上にテキストでオーバーレイします。',
    'zh-CN': '🏷️ Attribute 结果：将预测的人物/面部属性和置信度分数以文本形式叠加在图像上。', 'zh-TW': '🏷️ Attribute 結果：將預測的人物/臉部屬性和信賴度分數以文字形式疊加在影像上。',
    es: '🏷️ Resultado de atributos: superpone los atributos de persona/rostro predichos y sus puntuaciones de confianza como texto en la imagen.',
  },
  '📊 Task Summary (': {
    ko: '📊 태스크 요약 (', ja: '📊 タスク概要 (',
    'zh-CN': '📊 任务摘要 (', 'zh-TW': '📊 任務摘要 (',
    es: '📊 Resumen de tareas (',
  },
  '📐 Embedding Result: displays vector dimension, first-8 values, and L2 norm as text. Embeddings are feature vectors, not visual detections.': {
    ko: '📐 Embedding 결과: 벡터 차원, 첫 8개 값, L2 노름을 텍스트로 표시합니다. Embedding은 특징 벡터이며 시각적 검출이 아닙니다.', ja: '📐 Embedding 結果: ベクトル次元、最初の8値、L2ノルムをテキストで表示します。Embedding は特徴ベクトルであり、視覚的な検出ではありません。',
    'zh-CN': '📐 Embedding 结果：以文本形式显示向量维度、前 8 个值和 L2 范数。Embedding 是特征向量，不是视觉检测。', 'zh-TW': '📐 Embedding 結果：以文字形式顯示向量維度、前 8 個值和 L2 範數。Embedding 是特徵向量，不是視覺偵測。',
    es: '📐 Resultado de incrustación: muestra la dimensión del vector, los primeros 8 valores y la norma L2 como texto. Las incrustaciones son vectores de características, no detecciones visuales.',
  },
  '📐 Embedding Result: side-by-side reference vs current image with cosine similarity (SAME / DIFFERENT).': {
    ko: '📐 Embedding 결과: 기준/현재 이미지를 나란히 표시하고 코사인 유사도(SAME / DIFFERENT)를 보여줍니다.', ja: '📐 Embedding 結果: 参照画像と現在画像を並べて表示し、コサイン類似度（SAME / DIFFERENT）を示します。',
    'zh-CN': '📐 Embedding 结果：并排显示参考图与当前图，并展示余弦相似度（SAME / DIFFERENT）。', 'zh-TW': '📐 Embedding 結果：並排顯示參考圖與目前圖，並展示餘弦相似度（SAME / DIFFERENT）。',
    es: '📐 Resultado de embedding: muestra referencia y actual lado a lado con similitud coseno (SAME / DIFFERENT).',
  },
  '🧍 ReID Result: side-by-side reference vs current image with cosine similarity (SAME / DIFFERENT).': {
    ko: '🧍 ReID 결과: 기준/현재 이미지를 나란히 표시하고 코사인 유사도(SAME / DIFFERENT)를 보여줍니다.', ja: '🧍 ReID 結果: 参照画像と現在画像を並べて表示し、コサイン類似度（SAME / DIFFERENT）を示します。',
    'zh-CN': '🧍 ReID 结果：并排显示参考图与当前图，并展示余弦相似度（SAME / DIFFERENT）。', 'zh-TW': '🧍 ReID 結果：並排顯示參考圖與目前圖，並展示餘弦相似度（SAME / DIFFERENT）。',
    es: '🧍 Resultado ReID: muestra referencia y actual lado a lado con similitud coseno (SAME / DIFFERENT).',
  },
  '🔇 Denoising Result: outputs the denoised image. DnCNN may process in grayscale (Y channel).': {
    ko: '🔇 Denoising 결과: 노이즈가 제거된 이미지를 출력합니다. DnCNN은 그레이스케일(Y 채널)로 처리할 수 있습니다.', ja: '🔇 Denoising 結果: ノイズ除去された画像を出力します。DnCNN はグレースケール（Yチャネル）で処理する場合があります。',
    'zh-CN': '🔇 Denoising 结果：输出去噪后的图像。DnCNN 可能以灰度（Y 通道）处理。', 'zh-TW': '🔇 Denoising 結果：輸出去噪後的影像。DnCNN 可能以灰階（Y 通道）處理。',
    es: '🔇 Resultado de eliminación de ruido: genera la imagen sin ruido. DnCNN puede procesar en escala de grises (canal Y).',
  },
  '🔍 Super Resolution Result: outputs the upscaled image. ESPCN processes the Y channel and restores color.': {
    ko: '🔍 Super Resolution 결과: 업스케일된 이미지를 출력합니다. ESPCN은 Y 채널을 처리하고 색상을 복원합니다.', ja: '🔍 Super Resolution 結果: アップスケールされた画像を出力します。ESPCN は Y チャネルを処理し、色を復元します。',
    'zh-CN': '🔍 Super Resolution 结果：输出放大后的图像。ESPCN 处理 Y 通道并恢复色彩。', 'zh-TW': '🔍 Super Resolution 結果：輸出放大後的影像。ESPCN 處理 Y 通道並恢復色彩。',
    es: '🔍 Resultado de super resolución: genera la imagen escalada. ESPCN procesa el canal Y y restaura el color.',
  },
  '🖼️ Cropped Input': {
    ko: '🖼️ 크롭된 입력', ja: '🖼️ クロップされた入力',
    'zh-CN': '🖼️ 裁剪后的输入', 'zh-TW': '🖼️ 裁剪後的輸入',
    es: '🖼️ Entrada recortada',
  },
  '😊 Face Alignment: draws 3D facial landmark points.': {
    ko: '😊 Face Alignment: 3D 얼굴 랜드마크 포인트를 표시합니다.', ja: '😊 Face Alignment: 3D 顔ランドマークポイントを描画します。',
    'zh-CN': '😊 Face Alignment：绘制 3D 面部特征点。', 'zh-TW': '😊 Face Alignment：繪製 3D 臉部特徵點。',
    es: '😊 Alineación facial: dibuja puntos de referencia faciales 3D.',
  },
  '🤚 Hand Landmark: draws 21 hand landmark points and connections.': {
    ko: '🤚 Hand Landmark: 21개의 손 랜드마크 포인트와 연결을 표시합니다.', ja: '🤚 Hand Landmark: 21個の手のランドマークポイントと接続を描画します。',
    'zh-CN': '🤚 Hand Landmark：绘制 21 个手部特征点及其连接。', 'zh-TW': '🤚 Hand Landmark：繪製 21 個手部特徵點及其連接。',
    es: '🤚 Puntos de referencia de mano: dibuja 21 puntos de referencia y conexiones de la mano.',
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
    es: 'YOLACT tiempo real instance segmentación. Prototype mask + linear combination.',
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
  '⚙️ Postprocessors': {
    ko: '⚙️ 후처리기', ja: '⚙️ ポストプロセッサー',
    'zh-CN': '⚙️ 后处理器', 'zh-TW': '⚙️ 後處理器',
    es: '⚙️ Post-procesadores',
  },
  '👁️ Visualization': {
    ko: '👁️ 시각화', ja: '👁️ 可視化',
    'zh-CN': '👁️ 可视化', 'zh-TW': '👁️ 視覺化',
    es: '👁️ Visualización',
  },
  '📄 Full Config (config.json)': {
    ko: '📄 전체 설정 (config.json)', ja: '📄 全設定 (config.json)',
    'zh-CN': '📄 完整配置 (config.json)', 'zh-TW': '📄 完整設定 (config.json)',
    es: '📄 Configuración completa (config.json)',
  },
  '📋 Basic Info': {
    ko: '📋 기본 정보', ja: '📋 基本情報',
    'zh-CN': '📋 基本信息', 'zh-TW': '📋 基本資訊',
    es: '📋 Información básica',
  },
  '🔧 Preprocessing': {
    ko: '🔧 전처리', ja: '🔧 前処理',
    'zh-CN': '🔧 预处理', 'zh-TW': '🔧 預處理',
    es: '🔧 Pre-procesamiento',
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
  '✅ All done!': {
    ko: '✅ 모두 완료!', ja: '✅ 全て完了！',
    'zh-CN': '✅ 全部完成！', 'zh-TW': '✅ 全部完成！',
    es: '✅ ¡Todo listo!',
  },

  'Archives': {
    ko: '아카이브', ja: 'アーカイブ',
    'zh-CN': '归档文件', 'zh-TW': '封存檔案',
    es: 'Archivos',
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
    es: 'Vídeos',
  },

  ' detected region(s)': {
    ko: '개 검출 영역', ja: ' 件の検出領域',
    'zh-CN': ' 个检测区域', 'zh-TW': ' 個偵測區域',
    es: ' región(es) detectada(s)',
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
  'Running stage-2 inference on ': {
    ko: ' 에서 stage-2 추론 실행 중', ja: ' で stage-2 推論実行中',
    'zh-CN': '正在对 ', 'zh-TW': '正在對 ',
    es: 'Ejecutando inferencia de etapa-2 en ',
  },
  '⏳ Queued': {
    ko: '⏳ 대기 중', ja: '⏳ キュー待ち',
    'zh-CN': '⏳ 排队中', 'zh-TW': '⏳ 排隊中',
    es: '⏳ En cola',
  },
  '✅ Done': {
    ko: '✅ 완료', ja: '✅ 完了',
    'zh-CN': '✅ 完成', 'zh-TW': '✅ 完成',
    es: '✅ Hecho',
  },
  '❌ Failed': {
    ko: '❌ 실패', ja: '❌ 失敗',
    'zh-CN': '❌ 失败', 'zh-TW': '❌ 失敗',
    es: '❌ Fallido',
  },
  '⏳ Running...': {
    ko: '⏳ 실행 중...', ja: '⏳ 実行中...',
    'zh-CN': '⏳ 运行中...', 'zh-TW': '⏳ 執行中...',
    es: '⏳ Ejecutando...',
  },
  '⏳ Running…': {
    ko: '⏳ 실행 중…', ja: '⏳ 実行中…',
    'zh-CN': '⏳ 运行中…', 'zh-TW': '⏳ 執行中…',
    es: '⏳ Ejecutando…',
  },

  'CPU compute — operations running on the CPU': {
    ko: 'CPU 연산 — CPU에서 실행되는 연산', ja: 'CPU 演算 — CPU上で実行される演算',
    'zh-CN': 'CPU 计算 — 在 CPU 上运行的操作', 'zh-TW': 'CPU 運算 — 在 CPU 上執行的操作',
    es: 'CPU compute — operaciones ejecutándose en el CPU',
  },
  'Capture — frame capture from input source': {
    ko: 'Capture — 입력 소스에서 프레임 캡처', ja: 'Capture — 入力ソースからのフレームキャプチャ',
    'zh-CN': 'Capture — 从输入源捕获帧', 'zh-TW': 'Capture — 從輸入來源擷取影格',
    es: 'Captura — captura de fotogramas desde la fuente de entrada',
  },
  'Input I/O — reading image/video from disk or camera': {
    ko: 'Input I/O — 디스크 또는 카메라에서 이미지/비디오 읽기', ja: 'Input I/O — ディスクまたはカメラからの画像/動画読み取り',
    'zh-CN': 'Input I/O — 从磁盘或摄像头读取图像/视频', 'zh-TW': 'Input I/O — 從磁碟或攝影機讀取影像/影片',
    es: 'E/S de entrada — lectura de imagen/vídeo desde disco o cámara',
  },
  'NPU compute — neural network inference on the NPU chip': {
    ko: 'NPU 연산 — NPU 칩에서의 신경망 추론', ja: 'NPU 演算 — NPU チップ上でのニューラルネットワーク推論',
    'zh-CN': 'NPU 计算 — NPU 芯片上的神经网络推理', 'zh-TW': 'NPU 運算 — NPU 晶片上的神經網路推論',
    es: 'Cómputo NPU — inferencia de red neuronal en el chip NPU',
  },
  'Output I/O — writing result image/video to disk': {
    ko: 'Output I/O — 결과 이미지/비디오를 디스크에 기록', ja: 'Output I/O — 結果画像/動画のディスクへの書き込み',
    'zh-CN': 'Output I/O — 将结果图像/视频写入磁盘', 'zh-TW': 'Output I/O — 將結果影像/影片寫入磁碟',
    es: 'E/S de salida — escritura de imagen/vídeo de resultado en disco',
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
  '🔴 Top bottlenecks (longest operations):': {
    ko: '🔴 상위 병목 (가장 오래 걸린 연산):', ja: '🔴 トップボトルネック（最も時間がかかった処理）:',
    'zh-CN': '🔴 主要瓶颈（耗时最长的操作）：', 'zh-TW': '🔴 主要瓶頸（耗時最長的操作）：',
    es: '🔴 Principales cuellos de botella (operaciones más largas):',
  },

  /* ==== Lab Portal ==== */
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
    es: 'Cambiar vista previa',
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
    ko: '실행 취소', ja: '実行キャンセル',
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
  'IP:Port': {
    ko: 'IP:포트', ja: 'IP:ポート',
    es: 'IP:Puerto',
    'zh-CN': 'IP:端口', 'zh-TW': 'IP:連接埠'
  },
  '/path/to/config.json': {
    ko: '/path/to/config.json', ja: '/path/to/config.json',
    es: '/path/to/config.json',
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

/* ─── 5-language inline helper for JS runtime strings ─── */
function _T5(ko, en, ja, zhCN, zhTW) {
    var lang = (window.DXI18n && window.DXI18n.lang) || 'en';
    if (lang === 'ko') return ko || en;
    if (lang === 'ja') return ja || en;
    if (lang === 'zh-CN') return zhCN || en;
    if (lang === 'zh-TW') return zhTW || en;
    return en;
}

/* ─── App-specific callbacks for shared i18n core ─── */
// _i18nOptions() and topbar-title are handled by refreshActivePageLanguage() in utils.js
window._DX_I18N_CALLBACKS = [];
