// (Planner TCO engine moved to dx_planner/ standalone server)

// reference.js 도 전역에 `init` 을 선언한다. 같은 전역 스코프라 나중 파일이
// 이기므로, 이름을 나눠 두 부팅 경로가 서로를 덮지 않게 한다.
// (계약: tests/shared/test_static_script_scope.py)
async function initDxApp(){
  await loadModels();
  // loadModels() 는 카탈로그를 기다린다. 그 사이에 사용자가 (또는 튜토리얼이,
  // 딥링크가) 다른 화면으로 갔다면 여기서 되돌리면 안 된다 — 부팅이 끝나는
  // 순간 보고 있던 화면이 뒤바뀐다. 아직 초기 화면 그대로일 때만 넘긴다.
  var _active = document.querySelector('.page.active');
  if (!_active || _active.id === 'page-models') nav('models');
  // A/B 를 먼저 열었다면 (딥링크 · 빠른 탭 이동) 그 칸은 모델이 오기 전에 그려져 선택지가 비었다 — 다시 그린다.
  else if (_active.id === 'page-compare' && typeof setABCols === 'function') setABCols(S.abCols);
  initRunPage();
  initBenchPage();
  initABImages();
  initPipeImages();
  // Pre-load chat models in background so picker is ready when chat opens
  if(typeof _loadChatModels === 'function') setTimeout(_loadChatModels, 500);
  var ipd=$('modal-imgpreview');
  ipd.addEventListener('click',function(){ipd.close()});
  ipd.addEventListener('cancel',function(e){e.preventDefault();ipd.close()});
  $('m-search').addEventListener('input',function(){filterModels()});
}
