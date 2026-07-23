
var pipeStepId=0;
function addPipeStep(){
  pipeStepId++;
  var el=document.createElement('div');el.className='pipe-step';el.id='ps-'+pipeStepId;
  var opts=S.models.map(function(m){return '<option data-cat="'+m.category+'">'+m.name+'</option>'}).join('');
  var sid=pipeStepId;
  el.innerHTML='<div class="flex-row gap8 mb8">'
    +'<select class="input" id="ps-model-'+sid+'"><option value="">\u2014 Model \u2014</option>'+opts+'</select>'
    +'<select class="input" id="ps-lang-'+sid+'"><option value="cpp">C++</option><option value="python">Python</option></select>'
    +'<button class="btn btn-sm btn-red" onclick="removePipeStep('+sid+')">\u2715</button>'
    +'</div><div class="flex-row gap8"><span class="badge b-cat">Step '+sid+'</span><span class="txt-dim txt-sm" id="ps-status-'+sid+'">'+T('Ready')+'</span></div>';
  $('pipe-steps').appendChild(el);
}

function removePipeStep(id){const el=$('ps-'+id);if(el)el.remove()}

function initPipeImages(){
  api('/api/images').then(function(imgs){
    var list=Array.isArray(imgs)?imgs:[];
    var el=$('pipe-img');if(el)el.innerHTML=list.map(function(p){return '<option value="'+p+'">'+p.split('/').pop()+'</option>'}).join('');
  });
  api('/api/videos').then(function(vids){
    var list=Array.isArray(vids)?vids:[];
    var el=$('pipe-vid');if(el)el.innerHTML=list.map(function(p){return '<option value="'+p+'">'+p.split('/').pop()+'</option>'}).join('');
  });
  var modeEl=$('pipe-mode');
  if(modeEl)modeEl.addEventListener('change',function(){
    var m=this.value;
    var desc=$('pipe-mode-desc');
    if(desc)desc.textContent=m==='cascade'
      ?T('Cascade: crops detected regions from stage-1 (Detection) and passes them to stage-2.')
      :T('Chain: each step\'s output image is fed as input to the next step.');
  });
}

function togglePipeInput(){
  var isImg=document.querySelector('input[name="pipe-input-type"][value="image"]').checked;
  $('pipe-img-wrap').style.display=isImg?'':'none';
  $('pipe-vid-wrap').style.display=isImg?'none':'';
}

async function doPipeRun(){
  var isImg=document.querySelector('input[name="pipe-input-type"][value="image"]').checked;
  var inputType=isImg?'image':'video';
  var inputPath=isImg?$('pipe-img').value:$('pipe-vid').value;
  var mode=$('pipe-mode').value;
  if(!inputPath){toast(T('Select input'),'warn');return}
  const steps=[];
  document.querySelectorAll('.pipe-step').forEach(function(el){
    var id=el.id.replace('ps-','');
    var sel=$('ps-model-'+id);if(!sel||!sel.value)return;
    var m=findModel(sel.value);if(!m)return;
    steps.push({model_name:m.name,category:m.category,model_file:m.model_file,lang:$('ps-lang-'+id).value,variant:'sync'});
    $('ps-status-'+id).textContent=T('⏳ Queued');
  });
  if(!steps.length){toast(T('Add pipeline steps'),'warn');return}
  var runBtn=$('pipe-run-btn');runBtn.disabled=true;runBtn.textContent=T('⏳ Running...');
  const res=await postJ('/api/run_pipeline',{input_path:inputPath,steps:steps,input_type:inputType,mode:mode});
  runBtn.disabled=false;runBtn.textContent=T('▶ Run Pipeline');
  const results=Array.isArray(res)?res:[];
  $('pipe-results').innerHTML='';
  results.forEach(function(r,i){
    if(!r){return}
    var stepName=steps[i]?steps[i].model_name:(r.step_model||'Step '+(i+1));
    var h='<div class="card mb8"><h3>Step '+(i+1)+': '+esc(stepName)+'</h3>';
    // Cascade mode: show crop results
    if(r.cascade_crops){
      h+='<p class="txt-dim txt-sm mb8">'+T('Running stage-2 inference on ')+r.crop_count+T(' detected region(s)')+'</p>';
      h+='<div style="display:flex;gap:10px;flex-wrap:wrap">';
      (r.cascade_crops||[]).forEach(function(cr,ci){
        h+='<div style="flex:0 0 220px;background:var(--bg-3);border-radius:8px;padding:8px;text-align:center">';
        h+='<div class="txt-sm" style="font-weight:600;margin-bottom:4px">'+esc(cr.crop_class||'#'+ci)+' <span class="txt-dim">('+((cr.crop_conf||0)*100).toFixed(1)+'%)</span></div>';
        if(cr.result_image)h+='<img src="data:image/jpeg;base64,'+cr.result_image+'" class="res-img" style="max-height:200px" onclick="previewImg(this.src)"/>';
        if(cr.fps)h+='<div class="txt-sm txt-acc mt4">'+cr.fps+' FPS</div>';
        if(cr.exit_code!==0)h+='<div class="txt-sm" style="color:var(--error)">Error</div>';
        h+='</div>';
      });
      h+='</div>';
    }else{
      // Chain mode & step results
      if(r.result_image)h+='<img src="data:image/jpeg;base64,'+r.result_image+'" class="res-img mb8" onclick="previewImg(this.src)"/>';
      if(r.result_video_url)h+='<div class="mt8"><video src="'+r.result_video_url+'" controls style="max-width:100%;border-radius:8px"></video></div>';
      h+='<div class="perf-grid">';
      if(r.fps)h+='<div class="pcard"><div class="pv txt-acc">'+r.fps+'</div><div class="pk">FPS</div></div>';
      if(r.latency)h+='<div class="pcard"><div class="pv">'+r.latency+'ms</div><div class="pk">Latency</div></div>';
      h+='</div>';
      if(r.exit_code!==0)h+='<p style="color:var(--error)">Error (code '+r.exit_code+')</p>';
    }
    if(r.cascade_note)h+='<p class="txt-dim txt-sm">ℹ '+esc(r.cascade_note)+'</p>';
    h+='</div>';
    $('pipe-results').innerHTML+=h;
    var allSteps=document.querySelectorAll('.pipe-step');
    if(allSteps[i]){
      var sid=allSteps[i].id.replace('ps-','');
      var ok=r.cascade_crops?(r.crop_count>0):(r.exit_code===0);
      $('ps-status-'+sid).textContent=ok?T('✅ Done'):T('❌ Failed');
    }
  });
}

if (typeof registerLangRefresher === 'function') {
  registerLangRefresher(function refreshPipelineLanguage() {
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document.querySelector('#page-run') || document);
  });
}
