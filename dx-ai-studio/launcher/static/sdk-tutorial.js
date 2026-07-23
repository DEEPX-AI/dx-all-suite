(function() {
  'use strict';

  function _sdkDebugLog() { if (window.DX_DEBUG_SDK === true) console.log.apply(console, arguments); }

  function _findFirstMdFile(data) {
    // Find the first non-PDF file in the data for document viewer tutorial step
    if (!data || !data.drawers) return null;
    for (var d = 0; d < data.drawers.length; d++) {
      var drawer = data.drawers[d];
      for (var s = 0; s < drawer.sections.length; s++) {
        for (var f = 0; f < drawer.sections[s].files.length; f++) {
          var file = drawer.sections[s].files[f];
          if (file.type !== 'pdf') return { file: file, color: drawer.color };
        }
      }
    }
    return null;
  }

  function _expandFirstSidebarGroup() {
    var groups = document.querySelectorAll('.sdk-sidebar-group:not(.flat)');
    for (var i = 0; i < groups.length; i++) {
      var g = groups[i];
      g.classList.add('expanded');
      var sec = g.querySelector('.sdk-sidebar-section:not(.search-hidden)');
      if (sec) {
        sec.click();
        return true;
      }
    }
    var flatHead = document.querySelector('.sdk-sidebar-group.flat .sdk-sidebar-group-head');
    if (flatHead) {
      flatHead.click();
      return true;
    }
    return false;
  }

  function _prepListNav() {
    if (window._sdkLib) window._sdkLib.switchView('list');
    _expandFirstSidebarGroup();
  }

  function _prepListWithFileCards() {
    _prepListNav();
  }

  function _openFirstDocViewer() {
    if (!window._sdkLib) return;
    var data = window._sdkLib.getLibData();
    var found = _findFirstMdFile(data);
    if (found) window._sdkLib.openBookViewer(found.file, found.color);
  }

  function _closeDocViewer() {
    // The Document Viewer section (immediately before Architecture) leaves the full-screen
    // #sdkBookViewer (position:fixed; z-index:200) open, covering the topbar. Without closing it
    // the architecture button sits hidden behind the viewer, so the spotlight lands on the viewer
    // overlay instead of the button. _sdkLib does not expose closeBookViewer(), so close it here.
    var viewer = document.getElementById('sdkBookViewer');
    if (viewer && viewer.classList.contains('open')) {
      viewer.classList.remove('open');
      var body = document.getElementById('sdkViewerBody');
      if (body) body.innerHTML = '';
    }
  }

  var secWelcome = {
    id: 'welcome',
    icon: '🏠',
    title: {
      ko: '환영합니다', en: 'Welcome', ja: 'ようこそ', 'zh-CN': '欢迎', 'zh-TW': '歡迎', es: 'Bienvenida'},
    steps: [
      {
        target: '.sdk-topbar',
        position: 'bottom',
        title: {
          en: 'Welcome to SDK Library',
          ko: 'SDK Library에 오신 것을 환영합니다',
          ja: 'SDKライブラリへようこそ',
          'zh-CN': '欢迎使用 SDK Library',
          'zh-TW': '歡迎使用 SDK Library',
          es: 'Bienvenido a SDK Library'
        },
        content: {
          en: 'The <strong>SDK Library</strong> is your central hub for browsing, searching, and reading all SDK documentation. Let\'s take a quick tour of the main features.',
          ko: '<strong>SDK Library</strong>는 모든 SDK 문서를 탐색, 검색, 열람할 수 있는 중앙 허브입니다. 주요 기능을 간단히 둘러보겠습니다.',
          ja: '<strong>SDKライブラリ</strong>は、すべてのSDKドキュメントを閲覧・検索・読むための中央ハブです。主な機能を簡単にご紹介します。',
          'zh-CN': '<strong>SDK Library</strong>是您浏览、搜索和阅读所有 SDK 文档的中心枢纽。让我们快速浏览一下主要功能。',
          'zh-TW': '<strong>SDK Library</strong>是您瀏覽、搜尋和閱讀所有 SDK 文件的中心樞紐。讓我們快速瀏覽一下主要功能。',
          es: '<strong>SDK Library</strong> es su centro para explorar, buscar y leer toda la documentación del SDK. Hagamos un recorrido rápido por las funciones principales.'
        }
      },
      {
        target: '#sdkDocCount',
        position: 'bottom',
        title: {
          ko: '문서 수', en: 'Document Count', ja: 'ドキュメント数', 'zh-CN': '文档数量', 'zh-TW': '文件數量', es: 'Recuento de documentos'},
        content: {
          ko: '이 <strong>배지</strong>는 라이브러리에서 사용할 수 있는 총 문서 수를 보여줍니다. 문서가 추가되거나 필터링되면 자동으로 업데이트됩니다.', en: 'This <strong>badge</strong> shows the total number of documents available in the library. It updates automatically as documents are added or filtered.', ja: 'この<strong>バッジ</strong>は、ライブラリで利用可能なドキュメントの総数を表示します。ドキュメントが追加またはフィルタリングされると自動的に更新されます。', 'zh-CN': '此<strong>徽章</strong>显示库中可用的文档总数。当文档被添加或筛选时会自动更新。', 'zh-TW': '此<strong>徽章</strong>顯示庫中可用的文件總數。當文件被新增或篩選時會自動更新。', es: 'Esta <strong>insignia</strong> muestra el número total de documentos disponibles en la biblioteca. Se actualiza automáticamente al añadir o filtrar documentos.'}
      },
      {
        target: '#sdkLibSearch',
        position: 'bottom',
        title: {
          ko: '문서 검색', en: 'Search Documents', ja: 'ドキュメント検索', 'zh-CN': '搜索文档', 'zh-TW': '搜尋文件', es: 'Buscar documentos'},
        content: {
          ko: '<strong>검색 바</strong>를 사용하여 제목이나 파일 경로로 문서를 빠르게 필터링하세요. 입력하는 동안 실시간으로 결과가 업데이트됩니다.', en: 'Use the <strong>search bar</strong> to quickly filter documents by title or file path. Results update in real-time as you type.', ja: '<strong>検索バー</strong>を使って、タイトルやファイルパスでドキュメントをすばやくフィルタリングできます。入力中にリアルタイムで結果が更新されます。', 'zh-CN': '使用<strong>搜索栏</strong>按标题或文件路径快速筛选文档。输入时结果会实时更新。', 'zh-TW': '使用<strong>搜尋欄</strong>按標題或檔案路徑快速篩選文件。輸入時結果會即時更新。', es: 'Use la <strong>barra de búsqueda</strong> para filtrar documentos por título o ruta. Los resultados se actualizan en tiempo real mientras escribe.'}
      },
      {
        target: '#dxToolbar',
        position: 'left',
        title: {
          ko: '툴바', en: 'Toolbar', ja: 'ツールバー', 'zh-CN': '工具栏', 'zh-TW': '工具列', es: 'Barra de herramientas'},
        content: {
          ko: '<strong>툴바</strong>에서 언어 선택, 설정 및 이 튜토리얼에 빠르게 접근할 수 있습니다. 여기서 환경을 커스터마이즈하세요.', en: 'The <strong>toolbar</strong> gives you quick access to language selection, settings, and this tutorial. Customize your experience here.', ja: '<strong>ツールバー</strong>から、言語選択、設定、このチュートリアルにすばやくアクセスできます。ここでお好みにカスタマイズしてください。', 'zh-CN': '<strong>工具栏</strong>让您快速访问语言选择、设置和本教程。在这里自定义您的体验。', 'zh-TW': '<strong>工具列</strong>讓您快速存取語言選擇、設定和本教學。在這裡自訂您的體驗。', es: 'La <strong>barra de herramientas</strong> ofrece acceso rápido al idioma, la configuración y este tutorial. Personalice su experiencia aquí.'}
      }
    ]
  };

  var secViewModes = {
    id: 'view-modes',
    icon: '🔄',
    title: {
      ko: '뷰 모드', en: 'View Modes', ja: 'ビューモード', 'zh-CN': '视图模式', 'zh-TW': '檢視模式', es: 'Modos de vista'},
    steps: [
      {
        target: '.sdk-topbar-toggle',
        position: 'bottom',
        title: {
          ko: '뷰 모드 전환', en: 'View Mode Toggle', ja: 'ビューモード切替', 'zh-CN': '视图模式切换', 'zh-TW': '檢視模式切換', es: 'Alternar modo de vista'},
        content: {
          ko: '이 <strong>토글</strong>을 사용하여 List 뷰와 Cabinet 뷰 사이를 전환하세요. 각 뷰는 문서를 탐색하는 다른 방법을 제공합니다.', en: 'Use this <strong>toggle</strong> to switch between List view and Cabinet view. Each view provides a different way to browse your documents.', ja: 'この<strong>トグル</strong>を使って、リストビューとキャビネットビューを切り替えます。各ビューはドキュメントを閲覧する異なる方法を提供します。', 'zh-CN': '使用此<strong>切换按钮</strong>在列表视图和文件柜视图之间切换。每种视图提供不同的文档浏览方式。', 'zh-TW': '使用此<strong>切換按鈕</strong>在列表檢視和文件櫃檢視之間切換。每種檢視提供不同的文件瀏覽方式。', es: 'Use este <strong>interruptor</strong> para alternar entre la vista de lista y la de archivador. Cada vista ofrece una forma distinta de explorar sus documentos.'}
      },
      {
        target: '[data-mode="list"]',
        position: 'bottom',
        title: {
          ko: 'List 뷰', en: 'List View', ja: 'リストビュー', 'zh-CN': '列表视图', 'zh-TW': '列表檢視', es: 'Vista de lista'},
        content: {
          ko: '<strong>List 뷰</strong>는 사이드바-콘텐츠 레이아웃으로 문서를 표시합니다. 왼쪽에 카테고리가 나열되고, 오른쪽에 파일 카드가 나타납니다.', en: '<strong>List view</strong> displays documents in a sidebar-content layout. Categories are listed on the left, and file cards appear on the right.', ja: '<strong>リストビュー</strong>は、サイドバー・コンテンツレイアウトでドキュメントを表示します。左側にカテゴリが一覧表示され、右側にファイルカードが表示されます。', 'zh-CN': '<strong>列表视图</strong>以侧边栏-内容布局显示文档。左侧列出分类，右侧显示文件卡片。', 'zh-TW': '<strong>列表檢視</strong>以側邊欄-內容佈局顯示文件。左側列出分類，右側顯示檔案卡片。', es: 'La <strong>vista de lista</strong> muestra documentos en un diseño de barra lateral y contenido. Las categorías aparecen a la izquierda y las tarjetas de archivo a la derecha.'},
        beforeStep: function() {
          if (window._sdkLib) window._sdkLib.switchView('list');
        }
      },
      {
        target: '[data-mode="cabinet"]',
        position: 'bottom',
        title: {
          ko: 'Cabinet 뷰', en: 'Cabinet View', ja: 'キャビネットビュー', 'zh-CN': '文件柜视图', 'zh-TW': '文件櫃檢視', es: 'Vista de archivador'},
        content: {
          ko: '<strong>Cabinet 뷰</strong>는 문서를 카테고리별 컬러 코딩된 서랍으로 정리합니다. 서랍을 클릭하면 확장하여 내용을 탐색할 수 있습니다.', en: '<strong>Cabinet view</strong> organizes documents into color-coded drawers by category. Click a drawer to expand and browse its contents.', ja: '<strong>キャビネットビュー</strong>は、ドキュメントをカテゴリ別の色分けされた引き出しに整理します。引き出しをクリックして展開し、内容を閲覧できます。', 'zh-CN': '<strong>文件柜视图</strong>将文档按分类整理到带颜色标记的抽屉中。点击抽屉可展开浏览其内容。', 'zh-TW': '<strong>文件櫃檢視</strong>將文件按分類整理到帶顏色標記的抽屜中。點擊抽屜可展開瀏覽其內容。', es: 'La <strong>vista de archivador</strong> organiza los documentos en cajones codificados por color según la categoría. Haga clic en un cajón para expandirlo y explorar su contenido.'},
        beforeStep: function() {
          if (window._sdkLib) window._sdkLib.switchView('cabinet');
        }
      },
      {
        target: '[data-mode="list"]',
        position: 'bottom',
        title: {
          ko: '기본 뷰', en: 'Default View', ja: 'デフォルトビュー', 'zh-CN': '默认视图', 'zh-TW': '預設檢視', es: 'Vista predeterminada'},
        content: {
          ko: '<strong>기본 뷰</strong>는 List 모드입니다. 위의 토글 버튼을 사용하여 언제든지 뷰를 전환할 수 있습니다.', en: 'The <strong>default view</strong> is List mode. You can switch between views at any time using the toggle buttons above.', ja: '<strong>デフォルトビュー</strong>はリストモードです。上のトグルボタンを使って、いつでもビューを切り替えることができます。', 'zh-CN': '<strong>默认视图</strong>是列表模式。您可以随时使用上方的切换按钮在视图之间切换。', 'zh-TW': '<strong>預設檢視</strong>是列表模式。您可以隨時使用上方的切換按鈕在檢視之間切換。', es: 'La <strong>vista predeterminada</strong> es el modo lista. Puede cambiar de vista en cualquier momento con los botones superiores.'},
        beforeStep: function() {
          if (window._sdkLib) window._sdkLib.switchView('list');
        }
      }
    ]
  };

  var secListNav = {
    id: 'list-navigation',
    icon: '📋',
    title: {
      ko: '리스트 탐색', en: 'List Navigation', ja: 'リストナビゲーション', 'zh-CN': '列表导航', 'zh-TW': '列表導航', es: 'Navegación en lista'},
    prerequisite: 'view-modes',
    prerequisiteMessage: {
      ko: '먼저 뷰 모드를 완료하세요', en: 'Complete View Modes first', ja: '先にビューモードを完了してください', 'zh-CN': '请先完成视图模式', 'zh-TW': '請先完成檢視模式', es: 'Complete primero los modos de vista'},
    beforeStart: function() {
      if (window._sdkLib) window._sdkLib.switchView('list');
    },
    steps: [
      {
        target: '.sdk-list-sidebar',
        position: 'right',
        title: {
          ko: '사이드바 카테고리', en: 'Sidebar Categories', ja: 'サイドバーカテゴリ', 'zh-CN': '侧边栏分类', 'zh-TW': '側邊欄分類', es: 'Categorías de la barra lateral'},
        content: {
          ko: '<strong>사이드바</strong>에 모든 문서 카테고리가 나열됩니다. 카테고리를 클릭하면 콘텐츠 영역의 해당 문서로 바로 이동합니다.', en: 'The <strong>sidebar</strong> lists all document categories. Click a category to jump directly to its documents in the content area.', ja: '<strong>サイドバー</strong>にすべてのドキュメントカテゴリが一覧表示されます。カテゴリをクリックすると、コンテンツエリアの該当ドキュメントに直接移動します。', 'zh-CN': '<strong>侧边栏</strong>列出所有文档分类。点击分类可直接跳转到内容区域中的对应文档。', 'zh-TW': '<strong>側邊欄</strong>列出所有文件分類。點擊分類可直接跳轉到內容區域中的對應文件。', es: 'La <strong>barra lateral</strong> enumera todas las categorías de documentos. Haga clic en una categoría para ir directamente a sus documentos en el área de contenido.'}
      },
      {
        target: '.sdk-sidebar-group-head',
        position: 'right',
        title: {
          ko: '그룹 펼치기/접기', en: 'Expand/Collapse Groups', ja: 'グループの展開/折りたたみ', 'zh-CN': '展开/折叠分组', 'zh-TW': '展開/摺疊分組', es: 'Expandir/contraer grupos'},
        content: {
          ko: '<strong>그룹 헤더</strong>를 클릭하면 카테고리 그룹을 펼치거나 접을 수 있습니다. 필요한 문서에 집중하는 데 도움이 됩니다.', en: 'Click the <strong>group header</strong> to expand or collapse a category group. This helps you focus on the documents you need.', ja: '<strong>グループヘッダー</strong>をクリックして、カテゴリグループを展開または折りたたみます。必要なドキュメントに集中するのに役立ちます。', 'zh-CN': '点击<strong>分组标题</strong>可展开或折叠分类组。这有助于您专注于所需的文档。', 'zh-TW': '點擊<strong>分組標題</strong>可展開或摺疊分類組。這有助於您專注於所需的文件。', es: 'Haga clic en el <strong>encabezado del grupo</strong> para expandir o contraer un grupo de categorías. Así puede centrarse en los documentos que necesita.'},
        beforeStep: function() {
          var head = document.querySelector('.sdk-sidebar-group:not(.flat) .sdk-sidebar-group-head');
          if (head) {
            var group = head.closest('.sdk-sidebar-group');
            if (group && !group.classList.contains('expanded')) group.classList.add('expanded');
          }
        }
      },
      {
        target: '.sdk-sidebar-section',
        position: 'right',
        title: {
          ko: '섹션 선택', en: 'Select Section', ja: 'セクション選択', 'zh-CN': '选择章节', 'zh-TW': '選擇章節', es: 'Seleccionar sección'},
        content: {
          ko: '<strong>섹션</strong>을 클릭하면 해당 섹션이 강조 표시되고 콘텐츠 영역이 해당 문서로 스크롤됩니다.', en: 'Click a <strong>section</strong> to highlight it and scroll the content area to show the corresponding documents.', ja: '<strong>セクション</strong>をクリックすると、ハイライト表示され、コンテンツエリアが対応するドキュメントにスクロールします。', 'zh-CN': '点击<strong>章节</strong>可高亮显示并滚动内容区域到对应的文档。', 'zh-TW': '點擊<strong>章節</strong>可高亮顯示並滾動內容區域到對應的文件。', es: 'Haga clic en una <strong>sección</strong> para resaltarla y desplazar el área de contenido hasta los documentos correspondientes.'},
        beforeStep: function() { _expandFirstSidebarGroup(); }
      },
      {
        target: '#sdkListContent .file-card',
        position: 'top',
        title: {
          ko: '파일 카드', en: 'File Cards', ja: 'ファイルカード', 'zh-CN': '文件卡片', 'zh-TW': '檔案卡片', es: 'Tarjetas de archivo'},
        content: {
          ko: '각 <strong>파일 카드</strong>는 하나의 문서를 나타냅니다. 제목, 파일 유형, 경로가 표시됩니다. 카드를 클릭하면 문서 뷰어가 열립니다.', en: 'Each <strong>file card</strong> represents a document. It shows the title, file type, and path. Click a card to open the document viewer.', ja: '各<strong>ファイルカード</strong>は1つのドキュメントを表します。タイトル、ファイルタイプ、パスが表示されます。カードをクリックするとドキュメントビューアが開きます。', 'zh-CN': '每个<strong>文件卡片</strong>代表一个文档，显示标题、文件类型和路径。点击卡片可打开文档查看器。', 'zh-TW': '每個<strong>檔案卡片</strong>代表一個文件，顯示標題、檔案類型和路徑。點擊卡片可開啟文件檢視器。', es: 'Cada <strong>tarjeta de archivo</strong> representa un documento con título, tipo y ruta. Haga clic en una tarjeta para abrir el visor.'},
        beforeStep: function() { _prepListWithFileCards(); }
      },
      {
        target: '#sdkListContent',
        position: 'top',
        title: {
          ko: '콘텐츠 영역', en: 'Content Area', ja: 'コンテンツエリア', 'zh-CN': '内容区域', 'zh-TW': '內容區域', es: 'Área de contenido'},
        content: {
          ko: '<strong>콘텐츠 영역</strong>에 선택한 카테고리의 모든 파일 카드가 표시됩니다. 스크롤하여 사용 가능한 문서를 탐색하세요.', en: 'The <strong>content area</strong> displays all file cards for the selected category. Scroll through to browse available documents.', ja: '<strong>コンテンツエリア</strong>には、選択したカテゴリのすべてのファイルカードが表示されます。スクロールして利用可能なドキュメントを閲覧してください。', 'zh-CN': '<strong>内容区域</strong>显示所选分类的所有文件卡片。滚动浏览可用的文档。', 'zh-TW': '<strong>內容區域</strong>顯示所選分類的所有檔案卡片。滾動瀏覽可用的文件。', es: 'El <strong>área de contenido</strong> muestra todas las tarjetas de archivo de la categoría seleccionada. Desplácese para explorar los documentos disponibles.'}
      }
    ]
  };

  var secCabinetDrawers = {
    id: 'cabinet-drawers',
    icon: '🗄️',
    title: {
      ko: '캐비넷 서랍', en: 'Cabinet Drawers', ja: 'キャビネット引き出し', 'zh-CN': '文件柜抽屉', 'zh-TW': '文件櫃抽屜', es: 'Cajones del archivador'},
    prerequisite: 'view-modes',
    prerequisiteMessage: {
      ko: '먼저 뷰 모드를 완료하세요', en: 'Complete View Modes first', ja: '先にビューモードを完了してください', 'zh-CN': '请先完成视图模式', 'zh-TW': '請先完成檢視模式', es: 'Complete primero los modos de vista'},
    beforeStart: function() {
      if (window._sdkLib) window._sdkLib.switchView('cabinet');
    },
    steps: [
      {
        target: '.cabinet-drawers',
        position: 'top',
        title: {
          ko: '카테고리 서랍', en: 'Category Drawers', ja: 'カテゴリ引き出し', 'zh-CN': '分类抽屉', 'zh-TW': '分類抽屜', es: 'Cajones por categoría'},
        content: {
          ko: '캐비넷에는 <strong>5개의 카테고리 서랍</strong>이 있으며, 각각 색상으로 구분되어 쉽게 식별할 수 있습니다. 아무 서랍이나 클릭하면 확장하여 문서를 볼 수 있습니다.', en: 'The cabinet contains <strong>5 category drawers</strong>, each color-coded for easy identification. Click any drawer to expand and view its documents.', ja: 'キャビネットには<strong>5つのカテゴリ引き出し</strong>があり、それぞれ色分けされて簡単に識別できます。引き出しをクリックして展開し、ドキュメントを表示できます。', 'zh-CN': '文件柜包含<strong>5个分类抽屉</strong>，每个都用颜色标记以便于识别。点击任何抽屉可展开查看其文档。', 'zh-TW': '文件櫃包含<strong>5個分類抽屜</strong>，每個都用顏色標記以便於識別。點擊任何抽屜可展開查看其文件。', es: 'El archivador contiene <strong>5 cajones por categoría</strong>, cada uno con un color distinto. Haga clic en cualquier cajón para expandirlo y ver sus documentos.'}
      },
      {
        target: '.drawer-face',
        position: 'bottom',
        title: {
          ko: '서랍 열기', en: 'Open a Drawer', ja: '引き出しを開く', 'zh-CN': '打开抽屉', 'zh-TW': '開啟抽屜', es: 'Abrir un cajón'},
        content: {
          ko: '<strong>서랍 면</strong>을 클릭하면 서랍이 확장되어 내부 문서가 표시됩니다. 부드러운 애니메이션으로 서랍이 열립니다.', en: 'Click a <strong>drawer face</strong> to expand it and reveal the documents inside. The drawer slides open with a smooth animation.', ja: '<strong>引き出しの表面</strong>をクリックすると展開され、中のドキュメントが表示されます。スムーズなアニメーションで引き出しが開きます。', 'zh-CN': '点击<strong>抽屉面板</strong>可展开显示内部文档。抽屉会以平滑的动画打开。', 'zh-TW': '點擊<strong>抽屜面板</strong>可展開顯示內部文件。抽屜會以平滑的動畫開啟。', es: 'Haga clic en la <strong>cara del cajón</strong> para expandirlo y ver los documentos dentro. El cajón se abre con una animación suave.'},
        beforeStep: function() {
          var face = document.querySelector('.drawer-face');
          if (face) face.click();
        }
      },
      {
        target: '.drawer-body',
        position: 'top',
        title: {
          ko: '서랍 내용', en: 'Drawer Contents', ja: '引き出しの内容', 'zh-CN': '抽屉内容', 'zh-TW': '抽屜內容', es: 'Contenido del cajón'},
        content: {
          ko: '서랍 안에는 주제별로 정리된 <strong>섹션과 파일 카드</strong>가 있습니다. 각 카드는 문서 제목, 유형, 경로를 보여줍니다.', en: 'Inside a drawer you\'ll find <strong>sections and file cards</strong> organized by topic. Each card shows the document title, type, and path.', ja: '引き出しの中には、トピック別に整理された<strong>セクションとファイルカード</strong>があります。各カードにはドキュメントのタイトル、タイプ、パスが表示されます。', 'zh-CN': '抽屉内有按主题整理的<strong>章节和文件卡片</strong>。每张卡片显示文档标题、类型和路径。', 'zh-TW': '抽屜內有按主題整理的<strong>章節和檔案卡片</strong>。每張卡片顯示文件標題、類型和路徑。', es: 'Dentro de un cajón encontrará <strong>secciones y tarjetas</strong> organizadas por tema. Cada tarjeta muestra título, tipo y ruta del documento.'}
      },
      {
        target: '.drawer-face',
        position: 'bottom',
        title: {
          ko: '서랍 닫기 및 전환', en: 'Close & Switch Drawers', ja: '引き出しの閉じる・切替', 'zh-CN': '关闭和切换抽屉', 'zh-TW': '關閉和切換抽屜', es: 'Cerrar y cambiar cajones'},
        content: {
          ko: '열린 서랍의 면을 클릭하면 <strong>닫히고</strong>, 다른 서랍을 클릭하면 <strong>전환</strong>됩니다. 한 번에 하나의 서랍만 열 수 있습니다.', en: 'Click an open drawer\'s face to <strong>close</strong> it, or click another drawer to <strong>switch</strong>. Only one drawer can be open at a time.', ja: '開いている引き出しの表面をクリックして<strong>閉じる</strong>か、別の引き出しをクリックして<strong>切り替え</strong>ます。一度に開ける引き出しは1つだけです。', 'zh-CN': '点击已打开抽屉的面板可<strong>关闭</strong>它，或点击另一个抽屉进行<strong>切换</strong>。一次只能打开一个抽屉。', 'zh-TW': '點擊已開啟抽屜的面板可<strong>關閉</strong>它，或點擊另一個抽屜進行<strong>切換</strong>。一次只能開啟一個抽屜。', es: 'Haga clic en la cara de un cajón abierto para <strong>cerrarlo</strong>, o en otro cajón para <strong>cambiar</strong>. Solo puede haber un cajón abierto a la vez.'}
      },
      {
        target: '.cabinet-drawers',
        position: 'top',
        title: {
          ko: '색상 카테고리', en: 'Color Categories', ja: 'カラーカテゴリ', 'zh-CN': '颜色分类', 'zh-TW': '顏色分類', es: 'Categorías por color'},
        content: {
          ko: '각 서랍에는 <strong>고유한 색상</strong>이 있습니다: <strong>금색</strong>은 브로셔, <strong>빨간색</strong>은 all-suite, <strong>녹색</strong>은 Compiler, <strong>파란색</strong>은 Model Zoo, <strong>호박색</strong>은 Runtime입니다.', en: 'Each drawer has a <strong>unique color</strong>: <strong>gold</strong> for brochures, <strong>red</strong> for all-suite, <strong>green</strong> for compiler, <strong>blue</strong> for modelzoo, and <strong>amber</strong> for runtime.', ja: '各引き出しには<strong>固有の色</strong>があります。<strong>金色</strong>はブローシャー、<strong>赤</strong>はall-suite、<strong>緑</strong>はコンパイラ、<strong>青</strong>はModel Zoo、<strong>琥珀色</strong>はランタイムです。', 'zh-CN': '每个抽屉都有<strong>独特的颜色</strong>：<strong>金色</strong>代表宣传册、<strong>红色</strong>代表all-suite、<strong>绿色</strong>代表编译器、<strong>蓝色</strong>代表模型库、<strong>琥珀色</strong>代表运行时。', 'zh-TW': '每個抽屜都有<strong>獨特的顏色</strong>：<strong>金色</strong>代表宣傳冊、<strong>紅色</strong>代表all-suite、<strong>綠色</strong>代表編譯器、<strong>藍色</strong>代表模型庫、<strong>琥珀色</strong>代表執行環境。', es: 'Each drawer has a <strong>unique color</strong>: <strong>gold</strong> for brochures, <strong>red</strong> for all-suite, <strong>green</strong> for compiler, <strong>blue</strong> for modelzoo, and <strong>amber</strong> for runtime.'}
      }
    ]
  };

  var secSearch = {
    id: 'search',
    icon: '🔍',
    title: {
      ko: '검색', en: 'Search', ja: '検索', 'zh-CN': '搜索', 'zh-TW': '搜尋', es: 'Buscar'},
    steps: [
      {
        target: '#sdkLibSearch',
        position: 'bottom',
        title: {
          ko: '실시간 검색', en: 'Real-time Search', ja: 'リアルタイム検索', 'zh-CN': '实时搜索', 'zh-TW': '即時搜尋', es: 'Búsqueda en tiempo real'},
        content: {
          ko: '<strong>검색 바</strong>에 입력하면 실시간으로 문서가 필터링됩니다. 문서 <strong>제목</strong>과 <strong>파일 경로</strong>에 대해 매칭됩니다.', en: 'Type in the <strong>search bar</strong> to filter documents in real-time. It matches against document <strong>titles</strong> and <strong>file paths</strong>.', ja: '<strong>検索バー</strong>に入力すると、リアルタイムでドキュメントがフィルタリングされます。ドキュメントの<strong>タイトル</strong>と<strong>ファイルパス</strong>に対してマッチングされます。', 'zh-CN': '在<strong>搜索栏</strong>中输入可实时筛选文档。它会匹配文档的<strong>标题</strong>和<strong>文件路径</strong>。', 'zh-TW': '在<strong>搜尋欄</strong>中輸入可即時篩選文件。它會匹配文件的<strong>標題</strong>和<strong>檔案路徑</strong>。', es: 'Escriba en la <strong>barra de búsqueda</strong> para filtrar documentos en tiempo real. Coincide con <strong>títulos</strong> y <strong>rutas</strong> de archivo.'}
      },
      {
        target: '.sdk-body',
        position: 'top',
        title: {
          ko: '필터링된 결과', en: 'Filtered Results', ja: 'フィルタリング結果', 'zh-CN': '筛选结果', 'zh-TW': '篩選結果', es: 'Resultados filtrados'},
        content: {
          ko: '검색 시 <strong>일치하는 문서</strong>만 표시되고 나머지는 숨겨집니다. 문서 수 배지가 필터링된 총 수를 반영하여 업데이트됩니다.', en: 'When searching, only <strong>matched documents</strong> are shown and the rest are hidden. The document count badge updates to reflect the filtered total.', ja: '検索中は<strong>一致するドキュメント</strong>のみが表示され、残りは非表示になります。ドキュメント数バッジがフィルタリングされた合計を反映して更新されます。', 'zh-CN': '搜索时，只显示<strong>匹配的文档</strong>，其余文档被隐藏。文档数量徽章会更新以反映筛选后的总数。', 'zh-TW': '搜尋時，只顯示<strong>匹配的文件</strong>，其餘文件被隱藏。文件數量徽章會更新以反映篩選後的總數。', es: 'Al buscar, solo se muestran los <strong>documentos coincidentes</strong> y el resto se oculta. La insignia de recuento refleja el total filtrado.'}
      },
      {
        target: '#sdkLibSearch',
        position: 'bottom',
        title: {
          ko: '검색 초기화', en: 'Clear Search', ja: '検索クリア', 'zh-CN': '清除搜索', 'zh-TW': '清除搜尋', es: 'Limpiar búsqueda'},
        content: {
          ko: '검색 바를 <strong>지우면</strong> 필터가 초기화되어 모든 문서가 다시 표시됩니다. Escape를 눌러 검색을 지울 수도 있습니다.', en: '<strong>Clear</strong> the search bar to reset the filter and show all documents again. You can also press Escape to clear the search.', ja: '検索バーを<strong>クリア</strong>すると、フィルターがリセットされてすべてのドキュメントが再表示されます。Escapeキーを押して検索をクリアすることもできます。', 'zh-CN': '<strong>清除</strong>搜索栏可重置筛选并重新显示所有文档。您也可以按Escape键清除搜索。', 'zh-TW': '<strong>清除</strong>搜尋欄可重置篩選並重新顯示所有文件。您也可以按Escape鍵清除搜尋。', es: '<strong>Limpie</strong> la barra de búsqueda para restablecer el filtro y mostrar todos los documentos. También puede pulsar Escape para limpiar la búsqueda.'}
      }
    ]
  };

  var secDocViewer = {
    id: 'document-viewer',
    icon: '📖',
    title: {
      ko: '문서 뷰어', en: 'Document Viewer', ja: 'ドキュメントビューア', 'zh-CN': '文档查看器', 'zh-TW': '文件檢視器', es: 'Visor de documentos'},
    beforeStart: function() {
      _prepListWithFileCards();
    },
    steps: [
      {
        target: '#sdkListContent .file-card',
        position: 'top',
        title: {
          ko: '문서 열기', en: 'Open a Document', ja: 'ドキュメントを開く', 'zh-CN': '打开文档', 'zh-TW': '開啟文件', es: 'Abrir un documento'},
        content: {
          ko: '아무 <strong>파일 카드</strong>를 클릭하면 내장 뷰어에서 문서가 열립니다. 마크다운과 텍스트 파일은 전체 서식이 적용되어 렌더링됩니다.', en: 'Click any <strong>file card</strong> to open the document in the built-in viewer. Markdown and text files are rendered with full formatting.', ja: '任意の<strong>ファイルカード</strong>をクリックすると、内蔵ビューアでドキュメントが開きます。マークダウンとテキストファイルは完全なフォーマットでレンダリングされます。', 'zh-CN': '点击任意<strong>文件卡片</strong>可在内置查看器中打开文档。Markdown和文本文件会以完整格式渲染。', 'zh-TW': '點擊任意<strong>檔案卡片</strong>可在內建檢視器中開啟文件。Markdown和文字檔案會以完整格式渲染。', es: 'Haga clic en cualquier <strong>tarjeta</strong> para abrir el documento en el visor integrado. Markdown y texto se renderizan con formato completo.'},
        beforeStep: function() { _prepListWithFileCards(); }
      },
      {
        target: '.sdk-viewer-header',
        position: 'bottom',
        title: {
          ko: '뷰어 헤더', en: 'Viewer Header', ja: 'ビューアヘッダー', 'zh-CN': '查看器标题栏', 'zh-TW': '檢視器標題列', es: 'Encabezado del visor'},
        content: {
          ko: '<strong>헤더</strong>에 문서 제목, 파일 경로, 닫기 버튼이 표시됩니다. 현재 문서를 한눈에 확인할 수 있습니다.', en: 'The <strong>header</strong> shows the document title, file path, and a close button. You can identify the current document at a glance.', ja: '<strong>ヘッダー</strong>には、ドキュメントのタイトル、ファイルパス、閉じるボタンが表示されます。現在のドキュメントを一目で確認できます。', 'zh-CN': '<strong>标题栏</strong>显示文档标题、文件路径和关闭按钮。您可以一目了然地识别当前文档。', 'zh-TW': '<strong>標題列</strong>顯示文件標題、檔案路徑和關閉按鈕。您可以一目了然地識別當前文件。', es: 'El <strong>encabezado</strong> muestra el título, la ruta del archivo y un botón de cierre. Puede identificar el documento actual de un vistazo.'},
        beforeStep: function() { _openFirstDocViewer(); }
      },
      {
        target: '#sdkViewerBody',
        position: 'left',
        title: {
          ko: '문서 내용', en: 'Document Content', ja: 'ドキュメント内容', 'zh-CN': '文档内容', 'zh-TW': '文件內容', es: 'Contenido del documento'},
        content: {
          ko: '<strong>콘텐츠 영역</strong>에 구문 강조, 테이블, 이미지가 포함된 렌더링된 마크다운이 표시됩니다. 스크롤하여 전체 문서를 읽으세요.', en: 'The <strong>content area</strong> displays the rendered Markdown with syntax highlighting, tables, and images. Scroll to read the full document.', ja: '<strong>コンテンツエリア</strong>には、シンタックスハイライト、テーブル、画像を含むレンダリングされたマークダウンが表示されます。スクロールしてドキュメント全体を閲覧してください。', 'zh-CN': '<strong>内容区域</strong>显示带有语法高亮、表格和图片的渲染Markdown。滚动阅读完整文档。', 'zh-TW': '<strong>內容區域</strong>顯示帶有語法高亮、表格和圖片的渲染Markdown。滾動閱讀完整文件。', es: 'El <strong>área de contenido</strong> muestra el Markdown renderizado con resaltado de sintaxis, tablas e imágenes. Desplácese para leer el documento completo.'}
      },
      {
        target: '#sdkViewerSearch',
        position: 'bottom',
        title: {
          ko: '문서 내 검색', en: 'Document Search', ja: 'ドキュメント内検索', 'zh-CN': '文档内搜索', 'zh-TW': '文件內搜尋', es: 'Búsqueda en documento'},
        content: {
          ko: '<strong>Ctrl+F</strong>를 눌러 문서 내 검색을 열 수 있습니다. 현재 보고 있는 문서 내에서 특정 텍스트를 빠르게 찾으세요.', en: 'Press <strong>Ctrl+F</strong> to open the in-document search. Find specific text within the currently viewed document quickly.', ja: '<strong>Ctrl+F</strong>を押してドキュメント内検索を開きます。現在表示中のドキュメント内で特定のテキストをすばやく見つけられます。', 'zh-CN': '按<strong>Ctrl+F</strong>可打开文档内搜索。快速查找当前查看文档中的特定文本。', 'zh-TW': '按<strong>Ctrl+F</strong>可開啟文件內搜尋。快速查找當前檢視文件中的特定文字。', es: 'Pulse <strong>Ctrl+F</strong> para abrir la búsqueda dentro del documento y localizar texto específico rápidamente.'}
      },
      {
        target: '.sdk-viewer-close',
        position: 'left',
        title: {
          ko: '뷰어 닫기', en: 'Close Viewer', ja: 'ビューアを閉じる', 'zh-CN': '关闭查看器', 'zh-TW': '關閉檢視器', es: 'Cerrar visor'},
        content: {
          ko: '<strong>닫기 버튼</strong>을 클릭하거나 <strong>ESC</strong>를 눌러 문서 뷰어를 닫고 라이브러리 뷰로 돌아갑니다.', en: 'Click the <strong>close button</strong> or press <strong>ESC</strong> to close the document viewer and return to the library view.', ja: '<strong>閉じるボタン</strong>をクリックするか、<strong>ESC</strong>キーを押してドキュメントビューアを閉じ、ライブラリビューに戻ります。', 'zh-CN': '点击<strong>关闭按钮</strong>或按<strong>ESC</strong>关闭文档查看器并返回库视图。', 'zh-TW': '點擊<strong>關閉按鈕</strong>或按<strong>ESC</strong>關閉文件檢視器並返回庫檢視。', es: 'Haga clic en el <strong>botón cerrar</strong> o pulse <strong>ESC</strong> para cerrar el visor y volver a la vista de biblioteca.'}
      }
    ]
  };

  var secArchitecture = {
    id: 'architecture',
    icon: '🏗️',
    title: {
      ko: '아키텍처', en: 'Architecture', ja: 'アーキテクチャ', 'zh-CN': '架构', 'zh-TW': '架構', es: 'Arquitectura'},
    beforeStart: function() { _closeDocViewer(); },
    steps: [
      {
        target: '#sdkArchBtn',
        position: 'bottom',
        beforeStep: function() { _closeDocViewer(); },
        title: {
          ko: '아키텍처 버튼', en: 'Architecture Button', ja: 'アーキテクチャボタン', 'zh-CN': '架构按钮', 'zh-TW': '架構按鈕', es: 'Botón de arquitectura'},
        content: {
          ko: '<strong>아키텍처 버튼</strong>을 클릭하면 SDK 아키텍처의 전체 화면 다이어그램이 열립니다. 시스템의 전반적인 개요를 제공합니다.', en: 'Click the <strong>architecture button</strong> to open a full-screen diagram of the SDK architecture. It provides a high-level overview of the system.', ja: '<strong>アーキテクチャボタン</strong>をクリックすると、SDKアーキテクチャのフルスクリーン図が開きます。システムの全体的な概要を提供します。', 'zh-CN': '点击<strong>架构按钮</strong>可打开SDK架构的全屏示意图，提供系统的高层概览。', 'zh-TW': '點擊<strong>架構按鈕</strong>可開啟SDK架構的全螢幕示意圖，提供系統的高層概覽。', es: 'Haga clic en el <strong>botón de arquitectura</strong> para abrir un diagrama a pantalla completa del SDK. Ofrece una visión general del sistema.'}
      },
      {
        target: '#sdkArchOverlay',
        position: 'top',
        title: {
          ko: '아키텍처 다이어그램', en: 'Architecture Diagram', ja: 'アーキテクチャ図', 'zh-CN': '架构图', 'zh-TW': '架構圖', es: 'Diagrama de arquitectura'},
        content: {
          ko: '이 <strong>전체 화면 오버레이</strong>에 SDK 아키텍처 다이어그램이 표시됩니다. 오버레이의 아무 곳이나 클릭하면 닫히고 라이브러리로 돌아갑니다.', en: 'This <strong>full-screen overlay</strong> displays the SDK architecture diagram. Click anywhere on the overlay to close it and return to the library.', ja: 'この<strong>フルスクリーンオーバーレイ</strong>にSDKアーキテクチャ図が表示されます。オーバーレイの任意の場所をクリックすると閉じてライブラリに戻ります。', 'zh-CN': '此<strong>全屏覆盖层</strong>显示SDK架构图。点击覆盖层的任意位置可关闭并返回库。', 'zh-TW': '此<strong>全螢幕覆蓋層</strong>顯示SDK架構圖。點擊覆蓋層的任意位置可關閉並返回庫。', es: 'Esta <strong>superposición a pantalla completa</strong> muestra el diagrama de arquitectura del SDK. Haga clic en cualquier parte para cerrarla y volver a la biblioteca.'},
        beforeStep: function() {
          var archBtn = document.getElementById('sdkArchBtn');
          if (archBtn) archBtn.click();
        }
      }
    ]
  };

  var secToolbar = {
    id: 'toolbar',
    icon: '⚙️',
    title: {
      ko: '툴바', en: 'Toolbar', ja: 'ツールバー', 'zh-CN': '工具栏', 'zh-TW': '工具列', es: 'Barra de herramientas'},
    steps: [
      {
        target: '#langToggle',
        position: 'left',
        title: {
          ko: '언어 선택', en: 'Language Selector', ja: '言語選択', 'zh-CN': '语言选择', 'zh-TW': '語言選擇', es: 'Selector de idioma'},
        content: {
          ko: '<strong>언어 드롭다운</strong>을 사용하여 5개 지원 언어(English, 한국어, 日本語, 简体中文, 繁體中文) 간에 전환하세요.', en: 'Use the <strong>language dropdown</strong> to switch between 5 supported languages: English, 한국어, 日本語, 简体中文, and 繁體中文.', ja: '<strong>言語ドロップダウン</strong>を使って、5つの対応言語（English、한국어、日本語、简体中文、繁體中文）を切り替えられます。', 'zh-CN': '使用<strong>语言下拉菜单</strong>在5种支持的语言之间切换：English、한국어、日本語、简体中文和繁體中文。', 'zh-TW': '使用<strong>語言下拉選單</strong>在5種支援的語言之間切換：English、한국어、日本語、简体中文和繁體中文。', es: 'Use el <strong>menú desplegable de idioma</strong> para cambiar entre 5 idiomas: English, 한국어, 日本語, 简体中文 y 繁體中文.'}
      },
      {
        target: '#dxToolbarTutorial',
        position: 'left',
        title: {
          ko: '튜토리얼 버튼', en: 'Tutorial Button', ja: 'チュートリアルボタン', 'zh-CN': '教程按钮', 'zh-TW': '教學按鈕', es: 'Botón del tutorial'},
        content: {
          ko: '언제든지 <strong>🎓 튜토리얼 버튼</strong>을 클릭하면 이 목차가 다시 열리고 원하는 튜토리얼 섹션을 다시 볼 수 있습니다.', en: 'Click the <strong>🎓 tutorial button</strong> at any time to reopen this Table of Contents and revisit any tutorial section.', ja: 'いつでも<strong>🎓チュートリアルボタン</strong>をクリックすると、この目次が再表示され、任意のチュートリアルセクションを再訪できます。', 'zh-CN': '随时点击<strong>🎓教程按钮</strong>可重新打开此目录并重新查看任何教程章节。', 'zh-TW': '隨時點擊<strong>🎓教學按鈕</strong>可重新開啟此目錄並重新查看任何教學章節。', es: 'Haga clic en el <strong>botón 🎓 del tutorial</strong> en cualquier momento para reabrir este índice y revisar cualquier sección.'}
      }
    ]
  };

  var sections = [
    secWelcome,
    secViewModes,
    secListNav,
    secCabinetDrawers,
    secSearch,
    secDocViewer,
    secArchitecture,
    secToolbar
  ];

  var _initDone = false;
  var _engine = null;

  function connectToolbar() {
    if (!_engine) return;
    if (typeof DXToolbar !== 'undefined' && typeof DXToolbar.connectTutorial === 'function') {
      DXToolbar.connectTutorial(_engine, { owner: 'sdk_library' });
    }
  }

  function beforeLeave() {
    if (!_engine) return;
    if (typeof _engine.suspend === 'function') _engine.suspend();
    else {
      if (typeof _engine.hideTOC === 'function') _engine.hideTOC();
      if (typeof _engine.stop === 'function') _engine.stop();
    }
  }

  window.SDKTutorial = {
    connectToolbar: connectToolbar,
    beforeLeave: beforeLeave
  };

  _sdkDebugLog('[SDK Tutorial] script loaded, registering sdk-library-ready listener');
  window.addEventListener('sdk-library-ready', function initSdkTutorial() {
    _sdkDebugLog('[SDK Tutorial] sdk-library-ready event received, _initDone=', _initDone);
    if (_initDone) {
      connectToolbar();
      return;
    }
    _initDone = true;
    if (typeof DXTutorial === 'undefined') {
      console.error('[SDK Tutorial] DXTutorial is undefined — tutorial-init.js not loaded?');
      return;
    }
    _sdkDebugLog('[SDK Tutorial] calling DXTutorial.create with', sections.length, 'sections');
    DXTutorial.create({
      appId: 'sdk_library',
      keepPreviousEngine: true,
      sections: sections,
      helpLinks: [
        { title: { ko: 'SDK 개요', en: 'SDK Overview', ja: 'SDK概要', 'zh-CN': 'SDK概述', 'zh-TW': 'SDK概述', es: 'Resumen del SDK'},
          summary: { en: 'Introduction to the SDK Library and document navigation', ko: 'SDK Library 소개 및 문서 탐색 방법', ja: 'SDKライブラリの紹介とドキュメントナビゲーション', 'zh-CN': 'SDK Library 介绍和文档导航方法', 'zh-TW': 'SDK Library 介紹和文件導覽方法', es: 'Introducción a SDK Library y navegación de documentos' } },
        { title: { ko: '아키텍처 참조', en: 'Architecture Reference', ja: 'アーキテクチャ参照', 'zh-CN': '架构参考', 'zh-TW': '架構參考', es: 'Referencia de arquitectura'},
          summary: { ko: 'SDK 아키텍처 다이어그램과 모듈 관계 보기', en: 'View SDK architecture diagrams and module relationships', ja: 'SDKアーキテクチャ図とモジュール関係を表示', 'zh-CN': '查看SDK架构图和模块关系', 'zh-TW': '查看SDK架構圖和模組關係', es: 'Ver diagramas de arquitectura del SDK y relaciones entre módulos'} }
      ],
      getLang: function() { return (typeof DXI18n !== 'undefined') ? DXI18n.lang : 'en'; },
      setupButtons: function(engine) {
        _engine = engine;
connectToolbar();
      },
      onComplete: function(sectionId) {
        _sdkDebugLog('[SDK Tutorial] section complete:', sectionId);
      }
    });
  });

})();
