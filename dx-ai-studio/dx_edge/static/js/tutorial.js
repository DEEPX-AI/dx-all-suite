(function () {
  'use strict';

  /* Read-only tour: steps point at controls and may switch tabs, but never press
     Deploy, Delete, Upload & compile or anything else that writes to AWS. */

  function _visible(sel) {
    var el = document.querySelector(sel);
    if (!el) return false;
    var r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  }

  // Aim the step at the first visible candidate; the last one is always on screen.
  function _pick(step, candidates) {
    for (var i = 0; i < candidates.length; i++) {
      if (_visible(candidates[i])) { step.target = candidates[i]; return; }
    }
    step.target = candidates[candidates.length - 1];
  }

  // Same as clicking the tab: shows its panel only, no AWS call.
  function _tab(kind) {
    var tab = document.getElementById('edgeTab-' + kind);
    if (tab && tab.getAttribute('aria-selected') !== 'true') tab.click();
  }

  var sections = [

    { id: 'overview', icon: 'cloud',
      title: { ko: 'DX Cloud 개요', en: 'DX Cloud Overview', ja: 'DX Cloud の概要', 'zh-CN': 'DX Cloud 概览', 'zh-TW': 'DX Cloud 概覽', es: 'Resumen de DX Cloud' },
      description: { ko: '화면 구성과 상단 상태 chip', en: 'Page layout and the status chips at the top', ja: '画面構成と上部のステータスチップ', 'zh-CN': '页面布局和顶部的状态标签', 'zh-TW': '頁面佈局和頂部的狀態標籤', es: 'Diseño de la página y chips de estado superiores' },
      steps: [
        { target: '.dx-shell-header-left', position: 'bottom',
          title: { ko: 'DX Cloud', en: 'DX Cloud', ja: 'DX Cloud', 'zh-CN': 'DX Cloud', 'zh-TW': 'DX Cloud', es: 'DX Cloud' },
          content: { ko: '<strong>DX Cloud</strong>는 AWS Marketplace의 DEEPX solution을 내 AWS 계정에서 사용하게 해 줍니다: CloudFormation 스택 배포, 클라우드에서 .onnx → .dxnn 컴파일, Greengrass device에 dx-runtime 배포.', en: '<strong>DX Cloud</strong> runs the DEEPX solutions from AWS Marketplace in your own AWS account: deploy CloudFormation stacks, compile .onnx to .dxnn in the cloud, and roll dx-runtime out to Greengrass devices.', ja: '<strong>DX Cloud</strong> は AWS Marketplace の DEEPX ソリューションを自分の AWS アカウントで使えるようにします。CloudFormation スタックのデプロイ、クラウドでの .onnx → .dxnn コンパイル、Greengrass デバイスへの dx-runtime 配布です。', 'zh-CN': '<strong>DX Cloud</strong> 让您在自己的 AWS 账户中使用 AWS Marketplace 上的 DEEPX 解决方案：部署 CloudFormation 堆栈、在云端将 .onnx 编译为 .dxnn，并向 Greengrass 设备分发 dx-runtime。', 'zh-TW': '<strong>DX Cloud</strong> 讓您在自己的 AWS 帳戶中使用 AWS Marketplace 上的 DEEPX 解決方案：部署 CloudFormation 堆疊、在雲端將 .onnx 編譯為 .dxnn，並向 Greengrass 裝置分發 dx-runtime。', es: '<strong>DX Cloud</strong> ejecuta las soluciones DEEPX de AWS Marketplace en su propia cuenta de AWS: despliega pilas de CloudFormation, compila .onnx a .dxnn en la nube y distribuye dx-runtime a dispositivos Greengrass.' } },
        { target: '#edgeStatus', position: 'bottom',
          title: { ko: '상태 chip', en: 'Status Chips', ja: 'ステータスチップ', 'zh-CN': '状态标签', 'zh-TW': '狀態標籤', es: 'Chips de estado' },
          content: { ko: '현재 탭의 <strong>Profile, Region, Account, 구독, 스택 수</strong>를 한눈에 보여줍니다. 연결 확인이 성공하면 값이 채워집니다.', en: 'Shows the current tab\'s <strong>profile, region, account, subscription and stack count</strong> at a glance. The values fill in once the connection check succeeds.', ja: '現在のタブの<strong>プロファイル、リージョン、アカウント、サブスクリプション、スタック数</strong>を一目で表示します。接続確認が成功すると値が入ります。', 'zh-CN': '一目了然地显示当前标签页的<strong>配置文件、区域、账户、订阅和堆栈数量</strong>。连接检查成功后会填入数值。', 'zh-TW': '一目了然地顯示目前分頁的<strong>設定檔、區域、帳戶、訂閱和堆疊數量</strong>。連線檢查成功後會填入數值。', es: 'Muestra de un vistazo el <strong>perfil, la región, la cuenta, la suscripción y el número de pilas</strong> de la pestaña actual. Los valores aparecen cuando la comprobación de conexión tiene éxito.' } },
        { target: '#dxToolbar', position: 'left',
          title: { ko: '페이지 툴바', en: 'Page Toolbar', ja: 'ページのツールバー', 'zh-CN': '页面工具栏', 'zh-TW': '頁面工具列', es: 'Barra de la página' },
          content: { ko: '언어 · 테마 · 튜토리얼 버튼입니다. 튜토리얼 버튼으로 언제든 이 목차를 다시 열 수 있습니다.', en: 'Language, theme and tutorial buttons. The tutorial button reopens this table of contents at any time.', ja: '言語・テーマ・チュートリアルのボタンです。チュートリアルボタンでいつでもこの目次を開き直せます。', 'zh-CN': '语言、主题和教程按钮。随时可以用教程按钮重新打开此目录。', 'zh-TW': '語言、主題和教學按鈕。隨時可以用教學按鈕重新開啟此目錄。', es: 'Botones de idioma, tema y tutorial. El botón de tutorial vuelve a abrir este índice en cualquier momento.' } },
      ]
    },

    { id: 'marketplace', icon: 'external',
      title: { ko: 'AWS Marketplace의 DEEPX', en: 'DEEPX on AWS Marketplace', ja: 'AWS Marketplace の DEEPX', 'zh-CN': 'AWS Marketplace 上的 DEEPX', 'zh-TW': 'AWS Marketplace 上的 DEEPX', es: 'DEEPX en AWS Marketplace' },
      description: { ko: '두 solution 카드와 AWS Console 가이드', en: 'The two solution cards and the AWS Console guide', ja: '2 つのソリューションカードと AWS Console ガイド', 'zh-CN': '两张解决方案卡片和 AWS Console 指南', 'zh-TW': '兩張解決方案卡片和 AWS Console 指南', es: 'Las dos tarjetas de solución y la guía de AWS Console' },
      steps: [
        { target: '.edge-market .edge-grid', position: 'bottom',
          title: { ko: 'Solution 카드', en: 'Solution Cards', ja: 'ソリューションカード', 'zh-CN': '解决方案卡片', 'zh-TW': '解決方案卡片', es: 'Tarjetas de solución' },
          content: { ko: '<strong>DEEPX Compiler Solution</strong>은 EC2에서 dxcom을 실행하고, <strong>DEEPX Greengrass Solution</strong>은 Thing Group의 모든 device에 NPU driver · dx_rt · dx_stream을 배포합니다. <strong>Marketplace 페이지 열기</strong>에서 구독합니다.', en: '<strong>DEEPX Compiler Solution</strong> runs dxcom on EC2; <strong>DEEPX Greengrass Solution</strong> deploys the NPU driver, dx_rt and dx_stream to every device in a Thing Group. Subscribe from <strong>Open Marketplace listing</strong>.', ja: '<strong>DEEPX Compiler Solution</strong> は EC2 で dxcom を実行し、<strong>DEEPX Greengrass Solution</strong> は Thing Group のすべてのデバイスに NPU ドライバー・dx_rt・dx_stream を配布します。<strong>Marketplace ページを開く</strong>から購読します。', 'zh-CN': '<strong>DEEPX Compiler Solution</strong> 在 EC2 上运行 dxcom；<strong>DEEPX Greengrass Solution</strong> 向 Thing Group 中的所有设备部署 NPU 驱动、dx_rt 和 dx_stream。通过<strong>打开 Marketplace 页面</strong>进行订阅。', 'zh-TW': '<strong>DEEPX Compiler Solution</strong> 在 EC2 上執行 dxcom；<strong>DEEPX Greengrass Solution</strong> 向 Thing Group 中的所有裝置部署 NPU 驅動程式、dx_rt 和 dx_stream。透過<strong>開啟 Marketplace 頁面</strong>進行訂閱。', es: '<strong>DEEPX Compiler Solution</strong> ejecuta dxcom en EC2; <strong>DEEPX Greengrass Solution</strong> despliega el controlador del NPU, dx_rt y dx_stream en todos los dispositivos de un Thing Group. Suscríbase desde <strong>Abrir la ficha de Marketplace</strong>.' } },
        { target: '.edge-market a[href="guide#compiler"]', position: 'bottom',
          title: { ko: 'AWS Console 가이드', en: 'AWS Console Guide', ja: 'AWS Console ガイド', 'zh-CN': 'AWS Console 指南', 'zh-TW': 'AWS Console 指南', es: 'Guía de AWS Console' },
          content: { ko: 'Studio 없이 <strong>AWS Console</strong>에서 같은 작업(구독, 스택 배포, 컴파일)을 하는 방법을 단계별로 보여줍니다.', en: 'Walks through doing the same work (subscribe, deploy a stack, compile) in the <strong>AWS Console</strong> without Studio, step by step.', ja: 'Studio を使わずに <strong>AWS Console</strong> で同じ作業（購読、スタックのデプロイ、コンパイル）を行う手順をステップごとに示します。', 'zh-CN': '逐步说明如何在不使用 Studio 的情况下，在 <strong>AWS Console</strong> 中完成同样的工作（订阅、部署堆栈、编译）。', 'zh-TW': '逐步說明如何在不使用 Studio 的情況下，在 <strong>AWS Console</strong> 中完成同樣的工作（訂閱、部署堆疊、編譯）。', es: 'Explica paso a paso cómo hacer el mismo trabajo (suscribirse, desplegar una pila, compilar) en la <strong>AWS Console</strong> sin Studio.' } },
      ]
    },

    { id: 'connection', icon: 'setup',
      title: { ko: '1. AWS 연결', en: '1. AWS Connection', ja: '1. AWS 接続', 'zh-CN': '1. AWS 连接', 'zh-TW': '1. AWS 連線', es: '1. Conexión con AWS' },
      description: { ko: 'Profile, Region, 연결 확인, AWS CLI 설정 가이드', en: 'Profile, region, connection check and the AWS CLI setup guide', ja: 'プロファイル、リージョン、接続確認、AWS CLI 設定ガイド', 'zh-CN': '配置文件、区域、连接检查和 AWS CLI 设置指南', 'zh-TW': '設定檔、區域、連線檢查和 AWS CLI 設定指南', es: 'Perfil, región, comprobación de conexión y guía de configuración de AWS CLI' },
      steps: [
        { target: '#edgeProfile', position: 'bottom',
          title: { ko: 'AWS profile', en: 'AWS Profile', ja: 'AWS プロファイル', 'zh-CN': 'AWS 配置文件', 'zh-TW': 'AWS 設定檔', es: 'Perfil de AWS' },
          content: { ko: 'Studio를 실행하는 PC의 AWS CLI 설정(~/.aws)에서 profile을 고릅니다. Studio는 access key를 묻거나 저장하지 않습니다.', en: 'Pick a profile from the AWS CLI configuration (~/.aws) on the machine running Studio. Studio never asks for or stores access keys.', ja: 'Studio を実行している PC の AWS CLI 設定（~/.aws）からプロファイルを選びます。Studio がアクセスキーを求めたり保存したりすることはありません。', 'zh-CN': '从运行 Studio 的电脑上的 AWS CLI 配置（~/.aws）中选择配置文件。Studio 从不询问或保存访问密钥。', 'zh-TW': '從執行 Studio 的電腦上的 AWS CLI 設定（~/.aws）中選擇設定檔。Studio 從不詢問或儲存存取金鑰。', es: 'Elija un perfil de la configuración de AWS CLI (~/.aws) del equipo que ejecuta Studio. Studio nunca pide ni guarda claves de acceso.' } },
        { target: '#edgeRegion', position: 'bottom',
          title: { ko: '리전', en: 'Region', ja: 'リージョン', 'zh-CN': '区域', 'zh-TW': '區域', es: 'Región' },
          content: { ko: '계정에서 사용할 수 있는 리전 목록입니다. 스택과 컴파일 작업은 리전마다 따로 있으므로, 스택을 만든 리전을 고르세요.', en: 'The regions enabled for the account. Stacks and compile jobs live per region, so pick the region where your stack is.', ja: 'アカウントで有効なリージョンの一覧です。スタックとコンパイルジョブはリージョンごとに分かれるので、スタックを作成したリージョンを選んでください。', 'zh-CN': '该账户已启用的区域列表。堆栈和编译任务按区域区分，请选择堆栈所在的区域。', 'zh-TW': '該帳戶已啟用的區域清單。堆疊和編譯工作依區域區分，請選擇堆疊所在的區域。', es: 'Las regiones habilitadas para la cuenta. Las pilas y los trabajos de compilación son por región, así que elija la región donde está su pila.' } },
        { target: '#edgeCheck', position: 'bottom',
          title: { ko: '연결 확인', en: 'Check Connection', ja: '接続確認', 'zh-CN': '检查连接', 'zh-TW': '檢查連線', es: 'Comprobar conexión' },
          content: { ko: '<strong>연결 확인</strong>은 읽기 전용 호출로 계정을 확인하고 아래 단계를 엽니다. 새로 만든 named profile도 재시작 없이 목록에 나타납니다.', en: '<strong>Check connection</strong> confirms the account with a read-only call and unlocks the steps below. Newly created named profiles also appear in the list without a restart.', ja: '<strong>接続を確認</strong>は読み取り専用の呼び出しでアカウントを確認し、下の手順を開きます。新しく作った名前付きプロファイルも再起動なしで一覧に表示されます。', 'zh-CN': '<strong>检查连接</strong>通过只读调用确认账户，并解锁下面的步骤。新建的命名配置文件也无需重启即可出现在列表中。', 'zh-TW': '<strong>檢查連線</strong>透過唯讀呼叫確認帳戶，並解鎖下方的步驟。新建立的具名設定檔也無需重新啟動即可出現在清單中。', es: '<strong>Comprobar conexión</strong> confirma la cuenta con una llamada de solo lectura y desbloquea los pasos siguientes. Los perfiles con nombre recién creados también aparecen en la lista sin reiniciar.' } },
        { target: '#edgeGuide > summary', position: 'top',
          title: { ko: 'AWS CLI 설정 가이드', en: 'AWS CLI Setup Guide', ja: 'AWS CLI 設定ガイド', 'zh-CN': 'AWS CLI 设置指南', 'zh-TW': 'AWS CLI 設定指南', es: 'Guía de configuración de AWS CLI' },
          content: { ko: '펼치면 AWS CLI v2 설치, <code>aws configure</code> 또는 <code>aws sso login</code>, 확인 명령, 필요한 권한을 복사 가능한 명령과 함께 보여줍니다.', en: 'Expand it for installing AWS CLI v2, <code>aws configure</code> or <code>aws sso login</code>, a verify command and the required permissions, each with copyable commands.', ja: '展開すると AWS CLI v2 のインストール、<code>aws configure</code> または <code>aws sso login</code>、確認コマンド、必要な権限をコピーできるコマンド付きで表示します。', 'zh-CN': '展开后可看到安装 AWS CLI v2、<code>aws configure</code> 或 <code>aws sso login</code>、验证命令以及所需权限，每条命令都可复制。', 'zh-TW': '展開後可看到安裝 AWS CLI v2、<code>aws configure</code> 或 <code>aws sso login</code>、驗證指令以及所需權限，每條指令都可複製。', es: 'Despliéguela para ver cómo instalar AWS CLI v2, <code>aws configure</code> o <code>aws sso login</code>, un comando de verificación y los permisos necesarios, todos con comandos para copiar.' } },
      ]
    },

    { id: 'solutions', icon: 'cloud',
      title: { ko: 'Solution 탭과 구독', en: 'Solution Tabs & Subscription', ja: 'ソリューションタブと購読', 'zh-CN': '解决方案标签页与订阅', 'zh-TW': '解決方案分頁與訂閱', es: 'Pestañas de solución y suscripción' },
      description: { ko: '제품별 탭과 Marketplace 구독 상태', en: 'One tab per product and the Marketplace subscription state', ja: '製品ごとのタブと Marketplace の購読状態', 'zh-CN': '每个产品一个标签页，以及 Marketplace 订阅状态', 'zh-TW': '每個產品一個分頁，以及 Marketplace 訂閱狀態', es: 'Una pestaña por producto y el estado de la suscripción de Marketplace' },
      beforeStart: function () { _tab('compiler'); },
      steps: [
        { target: '.edge-tabs', position: 'bottom',
          title: { ko: 'Solution 탭', en: 'Solution Tabs', ja: 'ソリューションタブ', 'zh-CN': '解决方案标签页', 'zh-TW': '解決方案分頁', es: 'Pestañas de solución' },
          content: { ko: 'Marketplace 제품마다 탭이 하나씩 있습니다. 2–4단계는 탭마다 반복되고, <strong>DEEPX Greengrass Solution</strong> 탭에서는 4-1 Cloud Compile과 4-2 Devices를 따로 쓸 수 있습니다.', en: 'One tab per Marketplace product. Steps 2–4 repeat in each tab; in the <strong>DEEPX Greengrass Solution</strong> tab, 4-1 Cloud Compile and 4-2 Devices can be used separately.', ja: 'Marketplace 製品ごとにタブが 1 つあります。手順 2–4 はタブごとに繰り返され、<strong>DEEPX Greengrass Solution</strong> タブでは 4-1 クラウドコンパイルと 4-2 デバイスを別々に使えます。', 'zh-CN': '每个 Marketplace 产品对应一个标签页。步骤 2–4 在每个标签页中重复；在 <strong>DEEPX Greengrass Solution</strong> 标签页中，4-1 云端编译和 4-2 设备可以分别使用。', 'zh-TW': '每個 Marketplace 產品對應一個分頁。步驟 2–4 在每個分頁中重複；在 <strong>DEEPX Greengrass Solution</strong> 分頁中，4-1 雲端編譯和 4-2 裝置可以分別使用。', es: 'Una pestaña por producto de Marketplace. Los pasos 2–4 se repiten en cada pestaña; en la pestaña <strong>DEEPX Greengrass Solution</strong>, 4-1 Compilación en la nube y 4-2 Dispositivos se usan por separado.' } },
        { target: '[aria-labelledby="edgeSubsTitle-compiler"]', position: 'bottom',
          beforeStep: function () { _tab('compiler'); _pick(this, ['#edgeSubs-compiler', '[aria-labelledby="edgeSubsTitle-compiler"]']); },
          title: { ko: '2. Marketplace 구독', en: '2. Marketplace Subscription', ja: '2. Marketplace の購読', 'zh-CN': '2. Marketplace 订阅', 'zh-TW': '2. Marketplace 訂閱', es: '2. Suscripción de Marketplace' },
          content: { ko: '이 AWS 계정이 제품을 구독했는지 보여줍니다. 구독은 계정 관리자가 Marketplace 페이지에서 계정당 한 번 수락합니다.', en: 'Shows whether this AWS account is subscribed to the product. An account admin accepts the subscription once per account on the Marketplace page.', ja: 'この AWS アカウントが製品を購読しているかを示します。購読はアカウント管理者が Marketplace ページでアカウントごとに 1 回承認します。', 'zh-CN': '显示此 AWS 账户是否已订阅该产品。订阅由账户管理员在 Marketplace 页面上为每个账户接受一次。', 'zh-TW': '顯示此 AWS 帳戶是否已訂閱該產品。訂閱由帳戶管理員在 Marketplace 頁面上為每個帳戶接受一次。', es: 'Indica si esta cuenta de AWS está suscrita al producto. Un administrador de la cuenta acepta la suscripción una vez por cuenta en la página de Marketplace.' } },
      ]
    },

    { id: 'stacks', icon: 'models',
      title: { ko: '3. 스택', en: '3. Stacks', ja: '3. スタック', 'zh-CN': '3. 堆栈', 'zh-TW': '3. 堆疊', es: '3. Pilas' },
      description: { ko: 'CloudFormation 스택 목록, 배포, 이름 확인 후 삭제', en: 'CloudFormation stack list, deploy, and delete with name confirmation', ja: 'CloudFormation スタックの一覧、デプロイ、名前確認付きの削除', 'zh-CN': 'CloudFormation 堆栈列表、部署，以及需确认名称的删除', 'zh-TW': 'CloudFormation 堆疊清單、部署，以及需確認名稱的刪除', es: 'Lista de pilas de CloudFormation, despliegue y eliminación con confirmación del nombre' },
      beforeStart: function () { _tab('compiler'); },
      steps: [
        { target: '[aria-labelledby="edgeSetupTitle-compiler"]', position: 'bottom',
          beforeStep: function () { _pick(this, ['#edgeStackList-compiler', '[aria-labelledby="edgeSetupTitle-compiler"]']); },
          title: { ko: '스택 목록', en: 'Stack List', ja: 'スタック一覧', 'zh-CN': '堆栈列表', 'zh-TW': '堆疊清單', es: 'Lista de pilas' },
          content: { ko: '이 리전에서 구독한 template으로 만든 CloudFormation 스택과 상태입니다. 목록은 읽기만 하며, <strong>스택 배포</strong>를 누르기 전에는 아무것도 만들지 않습니다.', en: 'CloudFormation stacks made from the subscribed template in this region, with their status. The list only reads; nothing is created until you press <strong>Deploy stack</strong>.', ja: 'このリージョンで購読したテンプレートから作られた CloudFormation スタックとその状態です。一覧は読み取るだけで、<strong>スタックをデプロイ</strong>を押すまで何も作成しません。', 'zh-CN': '此区域中由已订阅模板创建的 CloudFormation 堆栈及其状态。列表只做读取，按下<strong>部署 Stack</strong>之前不会创建任何资源。', 'zh-TW': '此區域中由已訂閱範本建立的 CloudFormation 堆疊及其狀態。清單只做讀取，按下<strong>部署 Stack</strong>之前不會建立任何資源。', es: 'Pilas de CloudFormation creadas con la plantilla suscrita en esta región, con su estado. La lista solo lee; no se crea nada hasta que pulse <strong>Desplegar pila</strong>.' } },
        { target: '#edgeDeployForm-compiler', position: 'top',
          title: { ko: '스택 배포', en: 'Deploy a Stack', ja: 'スタックのデプロイ', 'zh-CN': '部署堆栈', 'zh-TW': '部署堆疊', es: 'Desplegar una pila' },
          content: { ko: '새 스택 이름을 넣고 <strong>스택 배포</strong>를 누르면 CloudFormation 스택(EC2, S3 bucket 등)이 만들어지고, 진행 상태와 event가 아래에 표시됩니다. 튜토리얼은 이 버튼을 누르지 않습니다.', en: 'Enter a new stack name and press <strong>Deploy stack</strong> to create the CloudFormation stack (EC2, an S3 bucket and more); progress and events appear below. The tutorial never presses this button.', ja: '新しいスタック名を入れて<strong>スタックをデプロイ</strong>を押すと CloudFormation スタック（EC2、S3 バケットなど）が作成され、進み具合とイベントが下に表示されます。チュートリアルはこのボタンを押しません。', 'zh-CN': '输入新的堆栈名称并按<strong>部署 Stack</strong>，即可创建 CloudFormation 堆栈（EC2、S3 存储桶等），进度和事件显示在下方。教程不会按下此按钮。', 'zh-TW': '輸入新的堆疊名稱並按<strong>部署 Stack</strong>，即可建立 CloudFormation 堆疊（EC2、S3 儲存貯體等），進度和事件顯示在下方。教學不會按下此按鈕。', es: 'Escriba un nombre de pila nuevo y pulse <strong>Desplegar pila</strong> para crear la pila de CloudFormation (EC2, un bucket de S3 y más); el progreso y los eventos aparecen debajo. El tutorial nunca pulsa este botón.' } },
        { target: '[aria-labelledby="edgeSetupTitle-compiler"]', position: 'bottom',
          beforeStep: function () { _pick(this, ['#edgeStackList-compiler .btn-danger', '#edgeStackList-compiler', '[aria-labelledby="edgeSetupTitle-compiler"]']); },
          title: { ko: '스택 삭제', en: 'Delete a Stack', ja: 'スタックの削除', 'zh-CN': '删除堆栈', 'zh-TW': '刪除堆疊', es: 'Eliminar una pila' },
          content: { ko: '각 스택의 <strong>삭제</strong>는 확인 창을 엽니다. 스택 이름을 정확히 입력해야 삭제 버튼이 켜집니다. S3 model bucket은 남습니다(DeletionPolicy: Retain).', en: 'Each stack\'s <strong>Delete</strong> opens a confirm dialog; Delete turns on only after you type the exact stack name. The S3 model bucket is kept (DeletionPolicy: Retain).', ja: '各スタックの<strong>削除</strong>は確認ダイアログを開きます。スタック名を正確に入力するまで削除ボタンは有効になりません。S3 モデルバケットは残ります（DeletionPolicy: Retain）。', 'zh-CN': '每个堆栈的<strong>删除</strong>会打开确认对话框；只有准确输入堆栈名称后删除按钮才会启用。S3 模型存储桶会保留（DeletionPolicy: Retain）。', 'zh-TW': '每個堆疊的<strong>刪除</strong>會開啟確認對話框；只有準確輸入堆疊名稱後刪除按鈕才會啟用。S3 模型儲存貯體會保留（DeletionPolicy: Retain）。', es: '<strong>Eliminar</strong> en cada pila abre un diálogo de confirmación; el botón solo se activa tras escribir el nombre exacto de la pila. El bucket de modelos de S3 se conserva (DeletionPolicy: Retain).' } },
      ]
    },

    { id: 'compile', icon: 'compiler',
      title: { ko: '4. Cloud Compile', en: '4. Cloud Compile', ja: '4. クラウドコンパイル', 'zh-CN': '4. 云端编译', 'zh-TW': '4. 雲端編譯', es: '4. Compilación en la nube' },
      description: { ko: '스택 선택, 파일 놓기, 업로드 및 컴파일, 작업 상태', en: 'Stack picker, drop zones, upload & compile, job status', ja: 'スタック選択、ドロップ領域、アップロードとコンパイル、ジョブ状態', 'zh-CN': '堆栈选择、拖放区、上传并编译、任务状态', 'zh-TW': '堆疊選擇、拖放區、上傳並編譯、工作狀態', es: 'Selector de pila, zonas de arrastre, subir y compilar, estado del trabajo' },
      beforeStart: function () { _tab('compiler'); },
      steps: [
        { target: '#edgeStack-compiler', position: 'bottom',
          title: { ko: '컴파일 스택', en: 'Compile Stack', ja: 'コンパイル用スタック', 'zh-CN': '编译堆栈', 'zh-TW': '編譯堆疊', es: 'Pila de compilación' },
          content: { ko: '컴파일을 실행할 스택을 고릅니다. 새로 배포한 스택이 보이지 않으면 옆의 새로고침을 누르세요.', en: 'Pick the stack that runs the compile. If a newly deployed stack is missing, press the refresh button next to it.', ja: 'コンパイルを実行するスタックを選びます。新しくデプロイしたスタックが見えない場合は、横の更新ボタンを押してください。', 'zh-CN': '选择执行编译的堆栈。如果看不到新部署的堆栈，请按旁边的刷新按钮。', 'zh-TW': '選擇執行編譯的堆疊。如果看不到新部署的堆疊，請按旁邊的重新整理按鈕。', es: 'Elija la pila que ejecuta la compilación. Si no aparece una pila recién desplegada, pulse el botón de actualizar que está al lado.' } },
        { target: '#edgeOnnxDrop-compiler', position: 'bottom',
          title: { ko: 'ONNX 모델', en: 'ONNX Model', ja: 'ONNX モデル', 'zh-CN': 'ONNX 模型', 'zh-TW': 'ONNX 模型', es: 'Modelo ONNX' },
          content: { ko: '.onnx 파일을 여기에 끌어 놓거나 클릭해서 고릅니다.', en: 'Drop an .onnx file here, or click to choose one.', ja: '.onnx ファイルをここにドロップするか、クリックして選びます。', 'zh-CN': '将 .onnx 文件拖放到此处，或点击选择。', 'zh-TW': '將 .onnx 檔案拖放到此處，或點擊選擇。', es: 'Suelte aquí un archivo .onnx o haga clic para elegirlo.' } },
        { target: '#edgeJsonDrop-compiler', position: 'bottom',
          title: { ko: '컴파일 설정 (.json)', en: 'Compile Config (.json)', ja: 'コンパイル設定（.json）', 'zh-CN': '编译配置（.json）', 'zh-TW': '編譯設定（.json）', es: 'Configuración de compilación (.json)' },
          content: { ko: '같은 model의 dxcom 설정 .json을 놓습니다. 입력 shape, 전처리, calibration 설정이 여기에 들어 있습니다.', en: 'Drop the dxcom config .json for the same model; it carries the input shape, preprocessing and calibration settings.', ja: '同じモデルの dxcom 設定 .json をドロップします。入力 shape、前処理、キャリブレーションの設定が含まれます。', 'zh-CN': '拖放同一模型的 dxcom 配置 .json，其中包含输入 shape、预处理和校准设置。', 'zh-TW': '拖放同一模型的 dxcom 設定 .json，其中包含輸入 shape、前處理和校準設定。', es: 'Suelte el .json de configuración de dxcom del mismo modelo; contiene la forma de entrada, el preprocesamiento y la calibración.' } },
        { target: '#edgeStart-compiler', position: 'top',
          title: { ko: '업로드 후 컴파일', en: 'Upload and Compile', ja: 'アップロードしてコンパイル', 'zh-CN': '上传并编译', 'zh-TW': '上傳並編譯', es: 'Subir y compilar' },
          content: { ko: '두 파일을 스택의 S3 model bucket에 올리면 스택이 그 옆에 .dxnn을 컴파일합니다. 튜토리얼은 이 버튼을 누르지 않습니다.', en: 'Uploads both files to the stack\'s S3 model bucket; the stack then compiles a .dxnn next to them. The tutorial never presses this button.', ja: '2 つのファイルをスタックの S3 モデルバケットにアップロードすると、スタックがその隣に .dxnn をコンパイルします。チュートリアルはこのボタンを押しません。', 'zh-CN': '将两个文件上传到堆栈的 S3 模型存储桶，堆栈随后在旁边编译出 .dxnn。教程不会按下此按钮。', 'zh-TW': '將兩個檔案上傳到堆疊的 S3 模型儲存貯體，堆疊隨後在旁邊編譯出 .dxnn。教學不會按下此按鈕。', es: 'Sube ambos archivos al bucket de modelos de S3 de la pila; después la pila compila un .dxnn junto a ellos. El tutorial nunca pulsa este botón.' } },
        { target: '#cloudCompile-compiler', position: 'top',
          // Prefer the compile log panel when present, then the job box; both stay hidden until a job runs.
          beforeStep: function () { _pick(this, ['#edgePanel-compiler [id^="edgeLog"]', '#edgeJob-compiler', '#cloudCompile-compiler']); },
          title: { ko: '작업 상태와 링크', en: 'Job Status & Links', ja: 'ジョブ状態とリンク', 'zh-CN': '任务状态与链接', 'zh-TW': '工作狀態與連結', es: 'Estado del trabajo y enlaces' },
          content: { ko: '작업이 시작되면 여기에 상태, S3 경로, <strong>컴파일 로그</strong>가 나타납니다. 끝나면 <strong>.dxnn 다운로드</strong>, <strong>Studio 모델 폴더에 저장</strong>, AWS Console 링크를 쓸 수 있습니다.', en: 'Once a job starts, its state, S3 path and <strong>Compile log</strong> appear here. When it finishes, use <strong>Download .dxnn</strong>, <strong>Save to Studio models</strong> or the AWS Console links.', ja: 'ジョブが始まると、状態、S3 パス、<strong>コンパイルログ</strong>がここに表示されます。完了したら <strong>.dxnn をダウンロード</strong>、<strong>Studio のモデルに保存</strong>、AWS Console のリンクを使えます。', 'zh-CN': '任务开始后，其状态、S3 路径和<strong>编译日志</strong>会显示在这里。完成后可使用<strong>下载 .dxnn</strong>、<strong>保存到 Studio 模型目录</strong>或 AWS Console 链接。', 'zh-TW': '工作開始後，其狀態、S3 路徑和<strong>編譯日誌</strong>會顯示在這裡。完成後可使用<strong>下載 .dxnn</strong>、<strong>儲存到 Studio 模型目錄</strong>或 AWS Console 連結。', es: 'Cuando empieza un trabajo, aquí aparecen su estado, la ruta de S3 y el <strong>Registro de compilación</strong>. Al terminar, use <strong>Descargar .dxnn</strong>, <strong>Guardar en los modelos de Studio</strong> o los enlaces de AWS Console.' } },
        { target: '#cloudCompile-compiler .edge-jobs', position: 'top',
          title: { ko: '컴파일 작업', en: 'Compile Jobs', ja: 'コンパイルジョブ', 'zh-CN': '编译任务', 'zh-TW': '編譯工作', es: 'Trabajos de compilación' },
          content: { ko: '스택 bucket의 모든 model 폴더를 보여줍니다. 다른 세션이나 S3 console에서 올린 것도 포함되며, 끝난 작업은 여기서 .dxnn을 받을 수 있습니다.', en: 'Lists every model folder in the stack bucket, including uploads from other sessions and the S3 console; finished jobs offer their .dxnn here.', ja: 'スタックのバケットにあるすべてのモデルフォルダーを表示します。他のセッションや S3 コンソールからのアップロードも含まれ、完了したジョブはここから .dxnn を取得できます。', 'zh-CN': '列出堆栈存储桶中的所有模型文件夹，包括从其他会话和 S3 控制台上传的内容；已完成的任务可在这里获取 .dxnn。', 'zh-TW': '列出堆疊儲存貯體中的所有模型資料夾，包括從其他工作階段和 S3 主控台上傳的內容；已完成的工作可在這裡取得 .dxnn。', es: 'Muestra todas las carpetas de modelos del bucket de la pila, incluidas las subidas desde otras sesiones y la consola de S3; los trabajos terminados ofrecen aquí su .dxnn.' } },
      ]
    },

    { id: 'devices', icon: 'dev',
      title: { ko: '4-2. Devices (dx-runtime)', en: '4-2. Devices (dx-runtime)', ja: '4-2. デバイス（dx-runtime）', 'zh-CN': '4-2. 设备（dx-runtime）', 'zh-TW': '4-2. 裝置（dx-runtime）', es: '4-2. Dispositivos (dx-runtime)' },
      description: { ko: 'Greengrass 탭의 device 표와 device 등록 script', en: 'The device table and the register-device script on the Greengrass tab', ja: 'Greengrass タブのデバイス表とデバイス登録スクリプト', 'zh-CN': 'Greengrass 标签页中的设备表和设备注册脚本', 'zh-TW': 'Greengrass 分頁中的裝置表和裝置註冊腳本', es: 'La tabla de dispositivos y el script de registro en la pestaña Greengrass' },
      beforeStart: function () { _tab('greengrass'); },
      steps: [
        { target: '#edgeTab-greengrass', position: 'bottom',
          beforeStep: function () { _tab('greengrass'); },
          title: { ko: 'DEEPX Greengrass Solution 탭', en: 'DEEPX Greengrass Solution Tab', ja: 'DEEPX Greengrass Solution タブ', 'zh-CN': 'DEEPX Greengrass Solution 标签页', 'zh-TW': 'DEEPX Greengrass Solution 分頁', es: 'Pestaña DEEPX Greengrass Solution' },
          content: { ko: '이 탭은 Greengrass 스택의 2–3단계와 함께, 따로 쓸 수 있는 4-1 Cloud Compile과 4-2 Devices를 보여줍니다.', en: 'This tab shows steps 2–3 for Greengrass stacks plus two independent steps: 4-1 Cloud Compile and 4-2 Devices.', ja: 'このタブには Greengrass スタックの手順 2–3 と、別々に使える手順 4-1 クラウドコンパイルと 4-2 デバイスがあります。', 'zh-CN': '此标签页显示 Greengrass 堆栈的步骤 2–3，以及可分别使用的步骤 4-1 云端编译和 4-2 设备。', 'zh-TW': '此分頁顯示 Greengrass 堆疊的步驟 2–3，以及可分別使用的步驟 4-1 雲端編譯和 4-2 裝置。', es: 'Esta pestaña muestra los pasos 2–3 de las pilas de Greengrass y dos pasos independientes: 4-1 Compilación en la nube y 4-2 Dispositivos.' } },
        { target: '#cloudCompile-greengrass .edge-jobs', position: 'top',
          beforeStep: function () { _tab('greengrass'); },
          title: { ko: 'Greengrass 컴파일 작업', en: 'Greengrass Compile Jobs', ja: 'Greengrass のコンパイルジョブ', 'zh-CN': 'Greengrass 编译任务', 'zh-TW': 'Greengrass 編譯工作', es: 'Trabajos de compilación de Greengrass' },
          content: { ko: 'Greengrass 스택에도 같은 컴파일 단계가 있습니다. 이 표는 그 스택 bucket의 컴파일 작업을 보여주고, 각 행에서 .dxnn 다운로드, Studio 저장, 로그 보기를 할 수 있습니다.', en: 'Greengrass stacks have the same compile step. This table lists the compile jobs in that stack\'s bucket; each row can download the .dxnn, save it to Studio or show its log.', ja: 'Greengrass スタックにも同じコンパイル手順があります。この表はそのスタックのバケットにあるコンパイルジョブを表示し、各行から .dxnn のダウンロード、Studio への保存、ログ表示ができます。', 'zh-CN': 'Greengrass 堆栈也有相同的编译步骤。此表列出该堆栈存储桶中的编译任务，每一行都可以下载 .dxnn、保存到 Studio 或查看日志。', 'zh-TW': 'Greengrass 堆疊也有相同的編譯步驟。此表列出該堆疊儲存貯體中的編譯工作，每一列都可以下載 .dxnn、儲存到 Studio 或檢視日誌。', es: 'Las pilas de Greengrass tienen el mismo paso de compilación. Esta tabla muestra los trabajos de compilación del bucket de esa pila; cada fila permite descargar el .dxnn, guardarlo en Studio o ver su registro.' } },
        { target: '#edgeDevices .edge-table-wrap', position: 'top',
          beforeStep: function () { _tab('greengrass'); _pick(this, ['#edgeDevices .edge-table-wrap', '#edgeDevices']); },
          title: { ko: 'Core device 표', en: 'Core Device Table', ja: 'コアデバイス表', 'zh-CN': '核心设备表', 'zh-TW': '核心裝置表', es: 'Tabla de dispositivos principales' },
          content: { ko: '4단계에서 고른 Greengrass 스택의 Thing Group, deployment 상태와 각 core device의 상태, 마지막 업데이트, 설치된 component를 보여줍니다.', en: 'For the Greengrass stack picked in step 4: its Thing Group and deployment state, and each core device\'s status, last update and installed components.', ja: '手順 4 で選んだ Greengrass スタックの Thing Group とデプロイ状態、各コアデバイスの状態、最終更新、インストール済みコンポーネントを表示します。', 'zh-CN': '显示在步骤 4 中选择的 Greengrass 堆栈的 Thing Group 和部署状态，以及每个核心设备的状态、最近更新和已安装的组件。', 'zh-TW': '顯示在步驟 4 中選擇的 Greengrass 堆疊的 Thing Group 和部署狀態，以及每個核心裝置的狀態、最近更新和已安裝的元件。', es: 'Para la pila de Greengrass elegida en el paso 4: su Thing Group y el estado del despliegue, y el estado, la última actualización y los componentes instalados de cada dispositivo principal.' } },
        { target: '#edgeRegForm', position: 'top',
          beforeStep: function () { _tab('greengrass'); },
          title: { ko: 'Device 등록', en: 'Register a Device', ja: 'デバイスの登録', 'zh-CN': '注册设备', 'zh-TW': '註冊裝置', es: 'Registrar un dispositivo' },
          content: { ko: 'Thing 이름을 넣고 <strong>스크립트 생성</strong>을 누르면 device에서 실행할 설치 script가 나옵니다. Script에는 자격 증명이 없으며, device는 자체 AWS 자격 증명과 Java 11 이상이 필요합니다. 등록된 device는 Thing Group에 들어가 dx-runtime component를 받습니다.', en: 'Enter a Thing name and press <strong>Generate script</strong> to get the install script to run on the device. The script holds no credentials; the device needs its own AWS credentials and Java 11 or later. A registered device joins the Thing Group and receives the dx-runtime components.', ja: 'Thing 名を入れて<strong>スクリプトを生成</strong>を押すと、デバイスで実行するインストールスクリプトが出ます。スクリプトに認証情報は含まれず、デバイスには自身の AWS 認証情報と Java 11 以降が必要です。登録したデバイスは Thing Group に入り、dx-runtime コンポーネントを受け取ります。', 'zh-CN': '输入 Thing 名称并按<strong>生成脚本</strong>，即可得到在设备上运行的安装脚本。脚本不含任何凭证；设备需要自己的 AWS 凭证和 Java 11 或更高版本。注册后的设备会加入 Thing Group 并接收 dx-runtime 组件。', 'zh-TW': '輸入 Thing 名稱並按<strong>產生指令碼</strong>，即可得到在裝置上執行的安裝腳本。腳本不含任何憑證；裝置需要自己的 AWS 憑證和 Java 11 或更新版本。註冊後的裝置會加入 Thing Group 並接收 dx-runtime 元件。', es: 'Escriba un nombre de Thing y pulse <strong>Generar script</strong> para obtener el script de instalación que se ejecuta en el dispositivo. El script no contiene credenciales; el dispositivo necesita sus propias credenciales de AWS y Java 11 o posterior. Un dispositivo registrado entra en el Thing Group y recibe los componentes de dx-runtime.' } },
      ]
    },

  ];

  window.DXTutorial.create({
    appId: 'cloud',
    sections: sections,
    toolbarSelector: '#dxToolbar',
    skipButtons: true,
    getLang: function () {
      if (typeof DXI18n !== 'undefined' && DXI18n.lang) return DXI18n.lang;
      return localStorage.getItem('dx-lang') || 'en';
    },
    onNav: function () {},
    onComplete: function (sectionId) {
      var engine = window._dxTutorial;
      var sec = engine.sections.find(function (s) { return s.id === sectionId; });
      if (sec) console.info('[DXTutorial]', '"' + engine._t(sec.title) + '" ' + engine._tl('tutorial complete!'));
    }
  });

})();
