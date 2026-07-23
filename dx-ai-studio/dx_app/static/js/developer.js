// Lab mode — no password gate, uses X-Lab-Token header via postJ (utils.js)

async function labEnsureSession(){
  if(S.labToken)return S.labToken;
  var res=await api('/api/lab/session');
  if(res&&res.ok&&res.token){
    S.labToken=res.token;
    return S.labToken;
  }
  toast(T('Lab session unavailable'),'err');
  return '';
}
async function initLabPage(){
  await labEnsureSession();
  if (window.LabPortal && LabPortal.init) await LabPortal.init();
  _devInitSelects();
}
async function openDev(){
  nav('lab');
}
function _devInitSelects(){
  api('/api/task_types').then(function(tasks){
    if(!Array.isArray(tasks))return;
    $('da-task').innerHTML=tasks.map(function(t){return'<option value="'+t+'">'+t+'</option>'}).join('');
    _devUpdatePP($('da-task').value);
  });
  // Populate category filters for delete/extract
  var cats=[...new Set(S.models.map(function(m){return m.category}))].sort();
  var catOpts='<option value="">All Categories</option>'+cats.map(function(c){return'<option value="'+c+'">'+c+'</option>'}).join('');
  if($('dd-cat'))$('dd-cat').innerHTML=catOpts;
  if($('de-cat'))$('de-cat').innerHTML=catOpts;
  filterDelModels();
  filterExtModels();
}
function filterDelModels(){
  var cat=$('dd-cat')?$('dd-cat').value:'';
  var q=$('dd-search')?$('dd-search').value.toLowerCase():'';
  var list=S.models.filter(function(m){
    if(cat&&m.category!==cat)return false;
    if(q&&m.name.toLowerCase().indexOf(q)<0&&m.category.toLowerCase().indexOf(q)<0)return false;
    return true;
  });
  var opts='<option value="">— Select ('+list.length+') —</option>'+list.map(function(m){return'<option value="'+esc(m.name)+'">'+esc(m.name)+' ('+m.category+')</option>'}).join('');
  if($('dd-model-sel'))$('dd-model-sel').innerHTML=opts;
}
function filterExtModels(){
  var cat=$('de-cat')?$('de-cat').value:'';
  var q=$('de-search')?$('de-search').value.toLowerCase():'';
  var list=S.models.filter(function(m){
    if(cat&&m.category!==cat)return false;
    if(q&&m.name.toLowerCase().indexOf(q)<0&&m.category.toLowerCase().indexOf(q)<0)return false;
    return true;
  });
  var opts='<option value="">— Select ('+list.length+') —</option>'+list.map(function(m){
    var p=m.category+'/'+m.name;
    return'<option value="'+p+'">'+esc(m.name)+' ('+m.category+')</option>';
  }).join('');
  if($('de-model-sel'))$('de-model-sel').innerHTML=opts;
}
function _devUpdatePP(task){
  api('/api/postprocessors').then(function(pps){
    var list=(pps&&pps[task])||[];
    $('da-pp').innerHTML=list.length?list.map(function(p){return'<option>'+p+'</option>'}).join(''):'<option value="">N/A</option>';
  });
}

function devTab(el,t){
  document.querySelectorAll('.dev-tab').forEach(b=>b.classList.remove('active'));
  el.classList.add('active');
  document.querySelectorAll('.dev-panel').forEach(p=>p.classList.remove('active'));
  const pane=$(t);if(pane)pane.classList.add('active');
}

async function devAddModel(){
  const data={model_name:$('da-name').value,task_type:$('da-task').value,
    lang:$('da-lang').value,category:$('da-task').value,
    postprocessor:$('da-pp').value,
    sync_only:$('da-sync').checked};
  if(!data.model_name){toast(T('Name required'),'warn');return}
  var res=await postJ('/api/dev/add_model',data);
  if(res.error&&res.existing&&res.existing.length){
    var msg=T('The following already exist:\n')+res.existing.join('\n')+'\n\n'+T('Overwrite?');
    if(confirm(msg)){
      data.confirm_overwrite=true;
      res=await postJ('/api/dev/add_model',data);
    }else{toast(T('Cancelled'),'warn');return}
  }
  $('da-out').classList.remove('hidden');
  if(res.ok){toast(T('Model added'),'ok');$('da-out').textContent=res.output||'Done';await loadModels();renderModelsPage()}
  else{toast(res.error||T('Failed'),'err');$('da-out').textContent=res.error||'Failed'}
}

async function devDelModel(){
  const name=$('dd-name').value;if(!name){toast(T('Enter model name'),'warn');return}
  if(!confirm(T('Delete ')+name+'?'))return;
  const confirmText='delete:'+name;
  const res=await postJ('/api/dev/delete_model',{model_name:name,lang:$('dd-lang').value,confirm:confirmText});
  $('dd-out').classList.remove('hidden');
  if(res.ok){toast(T('Deleted'),'ok');$('dd-out').textContent=JSON.stringify(res.deleted)||'Done';await loadModels();renderModelsPage()}
  else{toast(res.error||T('Failed'),'err');$('dd-out').textContent=res.error||'Failed'}
}

async function devGitCommit(){
  const msg=$('dg-msg').value||'Update models';
  $('dg-out').textContent=T('Committing…');$('dg-out').classList.remove('hidden');
  const res=await postJ('/api/dev/git_commit',{message:msg,push:$('dg-push').checked,confirm_push:$('dg-push').checked?'push':''});
  $('dg-out').textContent=res.output||res.error||'Done';
}

async function devExtract(){
  var path=($('de-model-sel')&&$('de-model-sel').value)||$('de-path').value;
  var lang=$('de-lang').value;
  if(!path){toast(T('Select or enter a model path'),'warn');return}
  var btn=document.querySelector('#dev-ext .btn-acc');
  if(btn){btn.disabled=true;btn.textContent='\u23f3 '+T('Extracting...')}
  $('de-out').textContent=T('Extracting package for: ')+path+'\n...';$('de-out').classList.remove('hidden');
  const res=await postJ('/api/dev/extract',{model_path:path,lang:lang});
  if(btn){btn.disabled=false;btn.textContent='\ud83d\udce6 '+T('Extract Package')}
  if(res.ok){
    var txt='\u2705 Success! Output directory: '+res.output_dir+'\n\n';
    (res.results||[]).forEach(function(r){
      txt+='['+(r.lang||'?')+'] '+(r.ok?'\u2705 OK':'\u274c FAIL')+'\n';
      if(r.output)txt+=r.output+'\n';
    });
    $('de-out').textContent=txt;
    toast(T('Package extracted to outputs/'),'ok');
  }else{
    $('de-out').textContent='\u274c Error: '+(res.error||'Unknown error');
    toast(res.error||T('Extract failed'),'err');
  }
}

async function devNewTask(){
  var name=$('ds-name').value.trim();
  if(!name){toast(T('Task name required'),'warn');return}
  if(!/^[a-zA-Z][a-zA-Z0-9_]*$/.test(name)){toast(T('Use letters, digits, underscores only (must start with a letter)'),'warn');return}
  var lang=$('ds-lang').value;
  var btn=document.querySelector('#dev-skel .btn-acc');
  if(btn){btn.disabled=true;btn.textContent='⏳ '+T('Creating...')}
  $('ds-out').textContent=T('Creating skeleton for: ')+name+'\n...';$('ds-out').classList.remove('hidden');
  var data={task_name:name,lang:lang};
  var res=await postJ('/api/dev/new_task',data);
  if(res.error&&res.existing&&res.existing.length){
    var msg=T('The following already exist:\n')+res.existing.join('\n')+'\n\n'+T('Overwrite?');
    if(confirm(msg)){
      data.confirm_overwrite=true;
      res=await postJ('/api/dev/new_task',data);
    }else{if(btn){btn.disabled=false;btn.textContent='🦴 '+T('Create Skeleton')}toast(T('Cancelled'),'warn');return}
  }
  if(btn){btn.disabled=false;btn.textContent='🦴 '+T('Create Skeleton')}
  if(res.ok){
    var txt='✅ Task skeleton created: '+res.task_name+' ('+res.task_upper+')\n\n';
    txt+='Generated '+res.count+' files:\n';
    (res.files||[]).forEach(function(f){txt+='  📄 '+f+'\n'});
    txt+='\n💡 Search TODO in generated files for implementation points.';
    $('ds-out').textContent=txt;
    toast(T('Skeleton created: ')+res.task_name,'ok');
  }else{
    $('ds-out').textContent='❌ Error: '+(res.error||'Unknown error');
    toast(res.error||T('Failed'),'err');
  }
}

if (typeof registerLangRefresher === 'function') {
  registerLangRefresher(function refreshDeveloperLanguage() {
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
  });
}
