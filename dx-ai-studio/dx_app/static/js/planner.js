// (Planner TCO engine moved to dx_planner/ standalone server)

// reference.js also declares a global `init`. In the same global scope the later file
// wins, so the names are kept apart and the two boot paths do not overwrite each other.
// (contract: tests/shared/test_static_script_scope.py)
async function initDxApp(){
  await loadModels();
  // loadModels() waits for the catalog. If the user (or the tutorial, or a deep link)
  // moved to another screen meanwhile, do not send them back: the screen in view would
  // flip as boot finishes. Navigate only while the initial screen is still showing.
  var _active = document.querySelector('.page.active');
  if (!_active || _active.id === 'page-models') nav('models');
  // If A/B opened first (deep link, quick tab switch), its columns were drawn before the models arrived and have no options; redraw them.
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
