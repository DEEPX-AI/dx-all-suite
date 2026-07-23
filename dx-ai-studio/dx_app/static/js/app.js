
async function loadModels(){
  const data=await api('/api/models');
  S.models=Array.isArray(data)?data:[];
}

window.addEventListener('message', function(e) {
  if (!e.data || !e.data.type) return;
  if (e.data.type === 'dx-lang-change') {
    if (window._dxTutorial) window._dxTutorial.refreshLang();
  }
});

window.addEventListener('DOMContentLoaded',init);

