
async function loadModels(){
  const [data,labels]=await Promise.all([api('/api/models'),api('/api/category_labels').catch(function(){return {};})]);
  S.models=Array.isArray(data)?data:[];
  S.catLabels=(labels&&typeof labels==='object'&&!Array.isArray(labels))?labels:{};
}

// Full ModelZoo catalog (354 = 352 homepage + 2 PPU) for the Models page only.
// Kept separate from S.models (runnable-only, used by Run/Bench/Compare pickers).
async function loadCatalog(){
  const data=await api('/api/catalog');
  S.catalog=Array.isArray(data)?data:[];
}

window.addEventListener('message', function(e) {
  if (!e.data || !e.data.type) return;
  if (e.data.type === 'dx-lang-change') {
    if (window._dxTutorial) window._dxTutorial.refreshLang();
  }
});

window.addEventListener('DOMContentLoaded',initDxApp);

