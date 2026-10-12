/* Translate English errors from the server right before they are shown.
 *
 * Why in the front end — callers such as config_wizard.js append the server string
 * as is (`alert(T('...') + data.error)`). There are many server call sites, and
 * touching the error paths is risky; one pass just before display leaves the server alone.
 *
 * Why not a plain dictionary — most messages are f-strings with values **inside** the sentence:
 *     Invalid opt_level: 'abc' — must be one of [0, 1]
 * Whole-sentence lookups would not match, and translating only the prefix gives half a
 * translation. So the entries are patterns with capture groups, and values ($1, $2) are copied over.
 *
 * Scope — input validation only: messages a user sees right after a wrong input.
 * Messages normal use never shows, such as 'Job not found', stay English.
 *
 * An unregistered message comes back **unchanged**. Blanking it or replacing it with
 * "unknown error" would be worse — the user would lose the text to search for.
 *
 * Contract: tests/test_server_error_i18n.py
 */
(function () {
  'use strict';

  // Order matters: **more specific patterns first** —
  // 'Invalid input_shapes for X' comes before 'Invalid input_shapes:'.
  var _SERVER_ERROR_PATTERNS = [
    // DX Stream runtime contract
    {
      re: /^Runtime contract failed: (\S+)$/,
      ko: '런타임 점검을 통과하지 못했습니다 ($1)',
      ja: 'ランタイムのチェックに通りませんでした ($1)',
      es: 'El runtime no superó la comprobación ($1)',
      'zh-CN': '运行时检查未通过 ($1)',
      'zh-TW': '執行階段檢查未通過 ($1)',
    },
    {
      re: /^Studio runtime profile is not active and validated\.$/,
      ko: 'Studio 런타임 profile이 활성화 · 검증되지 않았습니다.',
      ja: 'Studio のランタイムプロファイルが有効化・検証されていません。',
      es: 'El perfil de runtime de Studio no está activo ni validado.',
      'zh-CN': 'Studio 运行时配置未激活或未验证。',
      'zh-TW': 'Studio 執行階段設定未啟用或未驗證。',
    },
    {
      re: /^Run the DX-Runtime Dependencies step in (?:DX Stream )?Setup, then try again\.$/,
      ko: 'Setup에서 DX-Runtime 종속성 설치 단계를 실행한 뒤 다시 시도하세요.',
      ja: 'Setup で DX-Runtime 依存関係のステップを実行してから、もう一度お試しください。',
      es: 'Ejecute el paso DX-Runtime Dependencies en Setup y vuelva a intentarlo.',
      'zh-CN': '请在 Setup 中运行 DX-Runtime 依赖项步骤，然后重试。',
      'zh-TW': '請在 Setup 中執行 DX-Runtime 相依套件步驟，然後再試一次。',
    },
    {
      re: /^Invalid input_shapes for (.+?): (.+?) — dimensions must be positive integers$/,
      ko: 'input_shapes의 $1 차원 $2을(를) 쓸 수 없습니다 — 차원은 양의 정수여야 합니다',
      ja: 'input_shapes の $1 の次元 $2 は使用できません — 次元は正の整数である必要があります',
      es: 'La dimensión $2 de $1 en input_shapes no es válida: las dimensiones deben ser enteros positivos',
      'zh-CN': 'input_shapes 中 $1 的维度 $2 无效 — 维度必须为正整数',
      'zh-TW': 'input_shapes 中 $1 的維度 $2 無效 — 維度必須為正整數',
    },
    {
      re: /^Invalid input_shapes for (.+?): expected a list of dimensions$/,
      ko: 'input_shapes의 $1은(는) 차원 목록이어야 합니다',
      ja: 'input_shapes の $1 は次元のリストである必要があります',
      es: '$1 en input_shapes debe ser una lista de dimensiones',
      'zh-CN': 'input_shapes 中的 $1 必须是维度列表',
      'zh-TW': 'input_shapes 中的 $1 必須是維度列表',
    },
    {
      re: /^Invalid input_shapes: expected an object$/,
      ko: 'input_shapes는 객체여야 합니다',
      ja: 'input_shapes はオブジェクトである必要があります',
      es: 'input_shapes debe ser un objeto',
      'zh-CN': 'input_shapes 必须是对象',
      'zh-TW': 'input_shapes 必須是物件',
    },
    {
      re: /^Invalid opt_level: empty — must be one of (.+)$/,
      ko: 'opt_level이 비어 있습니다 — $1 중 하나여야 합니다',
      ja: 'opt_level が空です — $1 のいずれかである必要があります',
      es: 'opt_level está vacío: debe ser uno de $1',
      'zh-CN': 'opt_level 为空 — 必须是 $1 之一',
      'zh-TW': 'opt_level 為空 — 必須是 $1 之一',
    },
    {
      re: /^Invalid opt_level: (.+?) — must be one of (.+)$/,
      ko: 'opt_level 값 $1을(를) 쓸 수 없습니다 — $2 중 하나여야 합니다',
      ja: 'opt_level の値 $1 は使用できません — $2 のいずれかである必要があります',
      es: 'El valor $1 de opt_level no es válido: debe ser uno de $2',
      'zh-CN': 'opt_level 的值 $1 无效 — 必须是 $2 之一',
      'zh-TW': 'opt_level 的值 $1 無效 — 必須是 $2 之一',
    },
    {
      re: /^Invalid calibration_num: (.+?) — must be a positive number of samples$/,
      ko: 'calibration_num 값 $1을(를) 쓸 수 없습니다 — 표본 수는 양수여야 합니다',
      ja: 'calibration_num の値 $1 は使用できません — サンプル数は正の数である必要があります',
      es: 'El valor $1 de calibration_num no es válido: el número de muestras debe ser positivo',
      'zh-CN': 'calibration_num 的值 $1 无效 — 样本数必须为正数',
      'zh-TW': 'calibration_num 的值 $1 無效 — 樣本數必須為正數',
    },
    {
      re: /^Invalid calibration_num: (.+?) — expected a number$/,
      ko: 'calibration_num 값 $1을(를) 쓸 수 없습니다 — 숫자여야 합니다',
      ja: 'calibration_num の値 $1 は使用できません — 数値である必要があります',
      es: 'El valor $1 de calibration_num no es válido: debe ser un número',
      'zh-CN': 'calibration_num 的值 $1 无效 — 必须是数字',
      'zh-TW': 'calibration_num 的值 $1 無效 — 必須是數字',
    },
    {
      re: /^Invalid calibration_num$/,
      ko: 'calibration_num 값을 쓸 수 없습니다',
      ja: 'calibration_num の値が無効です',
      es: 'El valor de calibration_num no es válido',
      'zh-CN': 'calibration_num 的值无效',
      'zh-TW': 'calibration_num 的值無效',
    },
    {
      re: /^Invalid calibration_method: (.+?) — must be one of (.+)$/,
      ko: 'calibration_method 값 $1을(를) 쓸 수 없습니다 — $2 중 하나여야 합니다',
      ja: 'calibration_method の値 $1 は使用できません — $2 のいずれかである必要があります',
      es: 'El valor $1 de calibration_method no es válido: debe ser uno de $2',
      'zh-CN': 'calibration_method 的值 $1 无效 — 必须是 $2 之一',
      'zh-TW': 'calibration_method 的值 $1 無效 — 必須是 $2 之一',
    },
    {
      re: /^recalibration_method must be one of (.+)$/,
      ko: 'recalibration_method는 $1 중 하나여야 합니다',
      ja: 'recalibration_method は $1 のいずれかである必要があります',
      es: 'recalibration_method debe ser uno de $1',
      'zh-CN': 'recalibration_method 必须是 $1 之一',
      'zh-TW': 'recalibration_method 必須是 $1 之一',
    },
    {
      re: /^Invalid file_extensions: expected a list, got a string\. Use (.+?), not (.+?)\.$/,
      ko: 'file_extensions는 목록이어야 합니다 — $2 대신 $1 처럼 적으세요',
      ja: 'file_extensions はリストである必要があります — $2 ではなく $1 のように書いてください',
      es: 'file_extensions debe ser una lista: use $1, no $2',
      'zh-CN': 'file_extensions 必须是列表 — 请用 $1，而不是 $2',
      'zh-TW': 'file_extensions 必須是列表 — 請用 $1，而不是 $2',
    },
    {
      re: /^Invalid file_extensions: expected a list, got (.+)$/,
      ko: 'file_extensions는 목록이어야 합니다 (받은 것: $1)',
      ja: 'file_extensions はリストである必要があります（受け取った型: $1）',
      es: 'file_extensions debe ser una lista (se recibió $1)',
      'zh-CN': 'file_extensions 必须是列表（收到 $1）',
      'zh-TW': 'file_extensions 必須是列表（收到 $1）',
    },
    {
      re: /^Invalid file_extensions: (.+?) — extensions must be non-empty strings$/,
      ko: 'file_extensions의 $1을(를) 쓸 수 없습니다 — 확장자는 비어 있지 않은 문자열이어야 합니다',
      ja: 'file_extensions の $1 は使用できません — 拡張子は空でない文字列である必要があります',
      es: '$1 no es válido en file_extensions: las extensiones deben ser cadenas no vacías',
      'zh-CN': 'file_extensions 中的 $1 无效 — 扩展名必须是非空字符串',
      'zh-TW': 'file_extensions 中的 $1 無效 — 副檔名必須是非空字串',
    },
    {
      re: /^Invalid preprocessings: expected an array of operations, got (.+)$/,
      ko: 'preprocessings는 연산 배열이어야 합니다 (받은 것: $1)',
      ja: 'preprocessings は処理の配列である必要があります（受け取った型: $1）',
      es: 'preprocessings debe ser una matriz de operaciones (se recibió $1)',
      'zh-CN': 'preprocessings 必须是操作数组（收到 $1）',
      'zh-TW': 'preprocessings 必須是操作陣列（收到 $1）',
    },
    {
      re: /^Invalid (.+?)\.std: contains 0 — normalization divides by std$/,
      ko: '$1.std에 0이 있습니다 — 정규화는 std로 나눕니다',
      ja: '$1.std に 0 が含まれています — 正規化は std で除算します',
      es: '$1.std contiene 0: la normalización divide por std',
      'zh-CN': '$1.std 中包含 0 — 归一化需要除以 std',
      'zh-TW': '$1.std 中包含 0 — 正規化需要除以 std',
    },
    {
      re: /^Invalid (.+?): mean has (.+?) channel\(s\) but std has (.+?) — they must describe the same channels$/,
      ko: '$1의 mean은 $2 채널인데 std는 $3 입니다 — 같은 채널을 가리켜야 합니다',
      ja: '$1 の mean は $2 チャンネルですが std は $3 です — 同じチャンネルを表す必要があります',
      es: 'En $1, mean tiene $2 canal(es) pero std tiene $3: deben describir los mismos canales',
      'zh-CN': '$1 的 mean 有 $2 个通道，但 std 有 $3 个 — 必须描述相同的通道',
      'zh-TW': '$1 的 mean 有 $2 個通道，但 std 有 $3 個 — 必須描述相同的通道',
    },
    {
      re: /^Invalid (.+?): expected a non-empty list of per-channel numbers, got (.+)$/,
      ko: '$1은(는) 채널별 숫자의 비어 있지 않은 목록이어야 합니다 (받은 것: $2)',
      ja: '$1 はチャンネルごとの数値の空でないリストである必要があります（受け取った値: $2）',
      es: '$1 debe ser una lista no vacía de números por canal (se recibió $2)',
      'zh-CN': '$1 必须是非空的逐通道数字列表（收到 $2）',
      'zh-TW': '$1 必須是非空的逐通道數字列表（收到 $2）',
    },
    {
      re: /^Invalid (.+?): (.+?) — channel values must be numbers$/,
      ko: '$1의 $2을(를) 쓸 수 없습니다 — 채널 값은 숫자여야 합니다',
      ja: '$1 の $2 は使用できません — チャンネル値は数値である必要があります',
      es: '$2 no es válido en $1: los valores de canal deben ser números',
      'zh-CN': '$1 中的 $2 无效 — 通道值必须是数字',
      'zh-TW': '$1 中的 $2 無效 — 通道值必須是數字',
    },
    {
      re: /^Invalid (.+?): expected exactly one transform per entry, got (.+?) \((.+?)\)\. Split them into separate entries\.$/,
      ko: '$1 에는 항목마다 transform이 하나여야 하는데 $2 개입니다 ($3). 항목을 나누세요',
      ja: '$1 は項目ごとに transform が 1 つである必要がありますが $2 個あります（$3）。項目を分けてください',
      es: '$1 debe tener exactamente una transformación por entrada, pero tiene $2 ($3). Sepárelas en entradas distintas',
      'zh-CN': '$1 每个条目只能有一个 transform，但有 $2 个（$3）。请拆分为独立条目',
      'zh-TW': '$1 每個項目只能有一個 transform，但有 $2 個（$3）。請拆分為獨立項目',
    },
    {
      re: /^Invalid (.+?): expected an object like (.+?), got (.+)$/,
      ko: '$1은(는) $2 같은 객체여야 합니다 (받은 것: $3)',
      ja: '$1 は $2 のようなオブジェクトである必要があります（受け取った型: $3）',
      es: '$1 debe ser un objeto como $2 (se recibió $3)',
      'zh-CN': '$1 必须是类似 $2 的对象（收到 $3）',
      'zh-TW': '$1 必須是類似 $2 的物件（收到 $3）',
    },
    {
      re: /^Invalid (.+?): expected an object of parameters, got (.+)$/,
      ko: '$1은(는) 파라미터 객체여야 합니다 (받은 것: $2)',
      ja: '$1 はパラメータのオブジェクトである必要があります（受け取った型: $2）',
      es: '$1 debe ser un objeto de parámetros (se recibió $2)',
      'zh-CN': '$1 必须是参数对象（收到 $2）',
      'zh-TW': '$1 必須是參數物件（收到 $2）',
    },
    {
      re: /^Invalid (.+?): expected a list of node names, got a string\. A single node must still be a list — use (.+?), not (.+?)\.$/,
      ko: '$1은(는) 노드 이름 목록이어야 합니다. 노드가 하나여도 목록입니다 — $3 대신 $2 처럼 적으세요',
      ja: '$1 はノード名のリストである必要があります。ノードが 1 つでもリストです — $3 ではなく $2 のように書いてください',
      es: '$1 debe ser una lista de nombres de nodo. Incluso un solo nodo va en lista: use $2, no $3',
      'zh-CN': '$1 必须是节点名称列表。即使只有一个节点也要用列表 — 请用 $2，而不是 $3',
      'zh-TW': '$1 必須是節點名稱列表。即使只有一個節點也要用列表 — 請用 $2，而不是 $3',
    },
    {
      re: /^Invalid (.+?): expected a list of node names, got (.+)$/,
      ko: '$1은(는) 노드 이름 목록이어야 합니다 (받은 것: $2)',
      ja: '$1 はノード名のリストである必要があります（受け取った型: $2）',
      es: '$1 debe ser una lista de nombres de nodo (se recibió $2)',
      'zh-CN': '$1 必须是节点名称列表（收到 $2）',
      'zh-TW': '$1 必須是節點名稱列表（收到 $2）',
    },
    {
      re: /^Invalid (.+?): (.+?) — node names must be non-empty strings$/,
      ko: '$1의 $2을(를) 쓸 수 없습니다 — 노드 이름은 비어 있지 않은 문자열이어야 합니다',
      ja: '$1 の $2 は使用できません — ノード名は空でない文字列である必要があります',
      es: '$2 no es válido en $1: los nombres de nodo deben ser cadenas no vacías',
      'zh-CN': '$1 中的 $2 无效 — 节点名称必须是非空字符串',
      'zh-TW': '$1 中的 $2 無效 — 節點名稱必須是非空字串',
    },
    {
      re: /^Invalid (.+?): expected a path string, got (.+)$/,
      ko: '$1은(는) 경로 문자열이어야 합니다 (받은 것: $2)',
      ja: '$1 はパス文字列である必要があります（受け取った型: $2）',
      es: '$1 debe ser una cadena de ruta (se recibió $2)',
      'zh-CN': '$1 必须是路径字符串（收到 $2）',
      'zh-TW': '$1 必須是路徑字串（收到 $2）',
    },
    {
      re: /^Invalid (.+?): (.+?) — must be a positive number$/,
      ko: '$1의 $2을(를) 쓸 수 없습니다 — 양수여야 합니다',
      ja: '$1 の $2 は使用できません — 正の数である必要があります',
      es: '$2 no es válido en $1: debe ser un número positivo',
      'zh-CN': '$1 中的 $2 无效 — 必须是正数',
      'zh-TW': '$1 中的 $2 無效 — 必須是正數',
    },
    {
      re: /^Invalid (.+?): not valid JSON — (.+)$/,
      ko: '$1이(가) 올바른 JSON이 아닙니다 — $2',
      ja: '$1 が有効な JSON ではありません — $2',
      es: '$1 no es JSON válido: $2',
      'zh-CN': '$1 不是有效的 JSON — $2',
      'zh-TW': '$1 不是有效的 JSON — $2',
    },
    {
      re: /^Invalid JSON body$/,
      ko: '요청 본문이 올바른 JSON이 아닙니다',
      ja: 'リクエスト本文が有効な JSON ではありません',
      es: 'El cuerpo de la solicitud no es JSON válido',
      'zh-CN': '请求正文不是有效的 JSON',
      'zh-TW': '請求內容不是有效的 JSON',
    },
    {
      re: /^Invalid JSON$/,
      ko: '올바른 JSON이 아닙니다',
      ja: '有効な JSON ではありません',
      es: 'JSON no válido',
      'zh-CN': '无效的 JSON',
      'zh-TW': '無效的 JSON',
    },
    {
      re: /^Invalid directory path$/,
      ko: '디렉터리 경로가 올바르지 않습니다',
      ja: 'ディレクトリのパスが正しくありません',
      es: 'La ruta del directorio no es válida',
      'zh-CN': '目录路径无效',
      'zh-TW': '目錄路徑無效',
    },
    {
      re: /^Unsupported upload file type\. Allowed: (.+)$/,
      ko: '지원하지 않는 업로드 파일 형식입니다. 허용: $1',
      ja: 'サポートされていないアップロード形式です。許可: $1',
      es: 'Tipo de archivo no admitido. Permitidos: $1',
      'zh-CN': '不支持的上传文件类型。允许：$1',
      'zh-TW': '不支援的上傳檔案類型。允許：$1',
    },
    {
      re: /^Access denied: dir must be under (.+)$/,
      ko: '접근이 거부되었습니다 — dir은 $1 아래여야 합니다',
      ja: 'アクセスが拒否されました — dir は $1 の下にある必要があります',
      es: 'Acceso denegado: dir debe estar bajo $1',
      'zh-CN': '拒绝访问 — dir 必须位于 $1 之下',
      'zh-TW': '拒絕存取 — dir 必須位於 $1 之下',
    },
    {
      re: /^model_path, config_path, and output_dir are required$/,
      ko: 'model_path, config_path, output_dir이 모두 필요합니다',
      ja: 'model_path、config_path、output_dir がすべて必要です',
      es: 'Se requieren model_path, config_path y output_dir',
      'zh-CN': '必须提供 model_path、config_path 和 output_dir',
      'zh-TW': '必須提供 model_path、config_path 和 output_dir',
    },
    {
      re: /^(.+?) parameter required$/,
      ko: '$1 파라미터가 필요합니다',
      ja: '$1 パラメータが必要です',
      es: 'Se requiere el parámetro $1',
      'zh-CN': '需要 $1 参数',
      'zh-TW': '需要 $1 參數',
    },
    // Compile path policy (dx_compiler/core/path_policy.py)
    {
      re: /^(.+?) is outside the allowed folders$/,
      ko: '$1이(가) 허용된 폴더 밖에 있습니다 (suite 폴더 · studio var · 홈 · /media · /mnt)',
      ja: '$1 は許可されたフォルダーの外にあります (suite フォルダー · studio var · ホーム · /media · /mnt)',
      es: '$1 está fuera de las carpetas permitidas (carpeta de la suite · var del studio · inicio · /media · /mnt)',
      'zh-CN': '$1 不在允许的文件夹内 (suite 文件夹 · studio var · 主目录 · /media · /mnt)',
      'zh-TW': '$1 不在允許的資料夾內 (suite 資料夾 · studio var · 主目錄 · /media · /mnt)',
    },
    {
      re: /^(.+?) does not exist$/,
      ko: '$1이(가) 없습니다',
      ja: '$1 が存在しません',
      es: '$1 no existe',
      'zh-CN': '$1 不存在',
      'zh-TW': '$1 不存在',
    },
    {
      re: /^(.+?) is not a file$/,
      ko: '$1은(는) 파일이 아닙니다',
      ja: '$1 はファイルではありません',
      es: '$1 no es un archivo',
      'zh-CN': '$1 不是文件',
      'zh-TW': '$1 不是檔案',
    },
    {
      re: /^(.+?) is not a folder$/,
      ko: '$1은(는) 폴더가 아닙니다',
      ja: '$1 はフォルダーではありません',
      es: '$1 no es una carpeta',
      'zh-CN': '$1 不是文件夹',
      'zh-TW': '$1 不是資料夾',
    },
    {
      re: /^(.+?) is not a valid path$/,
      ko: '$1은(는) 올바른 경로가 아닙니다',
      ja: '$1 は有効なパスではありません',
      es: '$1 no es una ruta válida',
      'zh-CN': '$1 不是有效路径',
      'zh-TW': '$1 不是有效路徑',
    },
    {
      re: /^(.+?) cannot be a compiler job folder$/,
      ko: '$1은(는) 컴파일 작업 폴더로 지정할 수 없습니다',
      ja: '$1 にコンパイルジョブのフォルダーは指定できません',
      es: '$1 no puede ser una carpeta de trabajo del compilador',
      'zh-CN': '$1 不能是编译任务文件夹',
      'zh-TW': '$1 不能是編譯工作資料夾',
    },
    // Remote access refused (shared/dx_server.py)
    {
      re: /^Host not allowed$/,
      ko: '허용되지 않은 접속 주소(Host)입니다',
      ja: '許可されていない接続先 (Host) です',
      es: 'Host no permitido',
      'zh-CN': '不允许的访问地址 (Host)',
      'zh-TW': '不允許的存取位址 (Host)',
    },
    {
      re: /^Cross-origin request refused$/,
      ko: '다른 사이트에서 보낸 요청이라 거부했습니다',
      ja: '別のサイトからの要求のため拒否しました',
      es: 'Solicitud de otro origen rechazada',
      'zh-CN': '已拒绝来自其他站点的请求',
      'zh-TW': '已拒絕來自其他網站的請求',
    },
    {
      re: /^(.+?) is required$/,
      ko: '$1이(가) 필요합니다',
      ja: '$1 が必要です',
      es: 'Se requiere $1',
      'zh-CN': '需要 $1',
      'zh-TW': '需要 $1',
    },
    {
      re: /^temperature must be between (.+?) and (.+)$/,
      ko: 'temperature는 $1과(와) $2 사이여야 합니다',
      ja: 'temperature は $1 から $2 の間である必要があります',
      es: 'temperature debe estar entre $1 y $2',
      'zh-CN': 'temperature 必须在 $1 和 $2 之间',
      'zh-TW': 'temperature 必須在 $1 和 $2 之間',
    },
    // DX-COM refuses to compile below 8 GB free disk (checked inside dxcom, not by the studio)
    {
      re: /^Requires available disk size higher than (\d+) but you have (\d+(?:\.\d)?)\d*G$/,
      ko: 'DX-COM은 디스크 여유 공간이 $1 GB보다 많아야 합니다 (현재 $2 GB). 공간을 비운 뒤 다시 시도하세요.',
      ja: 'DX-COM にはディスクの空き容量が $1 GB より多く必要です (現在 $2 GB)。空き容量を増やしてから、もう一度お試しください。',
      es: 'DX-COM necesita más de $1 GB libres en disco (ahora hay $2 GB). Libere espacio y vuelva a intentarlo.',
      'zh-CN': 'DX-COM 需要超过 $1 GB 的可用磁盘空间 (当前 $2 GB)。请释放空间后重试。',
      'zh-TW': 'DX-COM 需要超過 $1 GB 的可用磁碟空間 (目前 $2 GB)。請釋出空間後再試一次。',
    },
    {
      re: /^temperature must be a number$/,
      ko: 'temperature는 숫자여야 합니다',
      ja: 'temperature は数値である必要があります',
      es: 'temperature debe ser un número',
      'zh-CN': 'temperature 必须是数字',
      'zh-TW': 'temperature 必須是數字',
    },
  ];

  function _lang() {
    try {
      if (typeof DXI18n !== 'undefined' && DXI18n.lang) return DXI18n.lang;
      return localStorage.getItem('dx-lang') || 'en';
    } catch (e) {
      return 'en';
    }
  }

  /**
   * Translate an English error string from the server into the current language.
   * With no matching pattern, the original comes back **unchanged**.
   */
  function translateServerError(msg) {
    if (typeof msg !== 'string' || !msg) return msg;
    var lang = _lang();
    if (lang === 'en') return msg;
    var text = msg.trim();
    for (var i = 0; i < _SERVER_ERROR_PATTERNS.length; i++) {
      var entry = _SERVER_ERROR_PATTERNS[i];
      var m = text.match(entry.re);
      if (!m) continue;
      var tpl = entry[lang];
      if (!tpl) return msg;          // no entry for this language: original
      return tpl.replace(/\$(\d)/g, function (_, d) {
        var v = m[Number(d)];
        return v === undefined ? '' : v;
      });
    }
    return msg;                       // unregistered message: unchanged
  }

  window.translateServerError = translateServerError;
  window._SERVER_ERROR_PATTERNS = _SERVER_ERROR_PATTERNS;
})();
