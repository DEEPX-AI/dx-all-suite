// (Planner TCO engine moved to dx_planner/ standalone server)

async function init(){
  await loadModels();
  nav('models');
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
