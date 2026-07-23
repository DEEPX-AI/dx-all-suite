
// A/B Model Compare  (2×2 grid, up to 8 slots, video support, original+result)
function filterABModels(i){
  var catSel=$('ab-cat-'+i);var searchEl=$('ab-search-'+i);var modelSel=$('ab-model-'+i);
  if(!modelSel)return;
  var cat=catSel?catSel.value:'';
  var q=(searchEl?searchEl.value:'').toLowerCase();
  var cur=modelSel.value;
  var filtered=S.models.filter(function(m){
    if(cat&&m.category!==cat)return false;
    if(q&&m.name.toLowerCase().indexOf(q)===-1)return false;
    return true;
  });
  modelSel.innerHTML='<option value="">'+T('— Select Model —')+'</option>'+filtered.map(function(m){return '<option value="'+m.name+'"'+(m.name===cur?' selected':'')+'>'+m.name+'</option>'}).join('');
  var acList=$('ab-ac-'+i);
  if(acList&&q.length>0){
    acList.innerHTML=filtered.slice(0,15).map(function(m){
      return '<div class="ac-item" data-name="'+m.name+'" onclick="pickABModel('+i+',\''+m.name+'\')">'+
        esc(m.name)+'<span class="ac-cat">'+m.category.replace(/_/g,' ')+'</span></div>';
    }).join('')||'<div class="ac-item txt-dim">'+T('No matches')+'</div>';
    acList.classList.add('open');
  }else if(acList){acList.classList.remove('open');}
}

function pickABModel(i,name){
  var sel=$('ab-model-'+i);if(sel)sel.value=name;
  var search=$('ab-search-'+i);if(search)search.value=name;
  var ac=$('ab-ac-'+i);if(ac)ac.classList.remove('open');
}

var _abDocClickHandler=null;
var _abInFlight=false;
function setABCols(n){
  S.abCols=n;
  $('ab-compare-card').classList.add('hidden');
  document.querySelectorAll('#ab-cols .btn').forEach(b=>b.classList.remove('active'));
  var activeBtn=document.querySelector('#ab-cols .btn[onclick="setABCols('+n+')"]');
  if(activeBtn)activeBtn.classList.add('active');
  const grid=$('ab-panels');
  // Always use 2-column grid layout
  grid.style.gridTemplateColumns='repeat(2,1fr)';
  grid.innerHTML='';
  const slots=['A','B','C','D','E','F','G','H'];
  const cats=[...new Set(S.models.map(function(m){return m.category}))].sort();
  const catOpts='<option value="">'+T('All Tasks')+'</option>'+cats.map(function(c){return '<option>'+c+'</option>'}).join('');
  const opts=S.models.map(function(m){return '<option value="'+m.name+'">'+m.name+'</option>'}).join('');
  for(var i=0;i<n;i++){
    grid.innerHTML+='<div class="ab-panel" id="abp-'+i+'">'
      +'<div class="ab-panel-hdr"><span class="ab-slot-badge">'+T('Slot ')+slots[i]+'</span></div>'
      +'<div class="ab-panel-body">'
      +'<div class="fg"><label>'+T('Task Filter')+'</label><select class="input" id="ab-cat-'+i+'" onchange="filterABModels('+i+')">'+catOpts+'</select></div>'
      +'<div class="fg"><label>'+T('Search')+'</label><div class="ac-wrap"><input type="text" class="input" id="ab-search-'+i+'" placeholder="Type model name..." oninput="filterABModels('+i+')" onfocus="filterABModels('+i+')" autocomplete="off"><div class="ac-list" id="ab-ac-'+i+'"></div></div></div>'
      +'<div class="fg"><label>Model</label><select class="input" id="ab-model-'+i+'"><option value="">'+T('— Select Model —')+'</option>'+opts+'</select></div>'
      +'<div class="fg"><label>Language</label><select class="input" id="ab-lang-'+i+'"><option value="cpp">C++ (Compiled)</option><option value="python">Python</option></select></div>'
      +'<div class="ab-res-area"><div id="ab-res-'+i+'" class="txt-dim txt-sm">'+T('Select a model and click ▶ Run All')+'</div></div>'
      +'</div></div>';
  }
  if(_abDocClickHandler){document.removeEventListener('click',_abDocClickHandler)}
  _abDocClickHandler=function(e){
    for(var j=0;j<n;j++){var ac=$('ab-ac-'+j);if(ac&&!ac.contains(e.target)&&e.target.id!=='ab-search-'+j)ac.classList.remove('open');}
  };
  document.addEventListener('click',_abDocClickHandler);
}

function initABImages(){
  Promise.all([api('/api/images'),api('/api/videos')]).then(function(r){
    var imgs=Array.isArray(r[0])?r[0]:[];
    var vids=Array.isArray(r[1])?r[1]:[];
    $('ab-img').innerHTML=
      (imgs.length?'<optgroup label="Images">'+imgs.map(function(p){return '<option value="'+p+'" data-type="image">'+p.split('/').pop()+'</option>'}).join('')+'</optgroup>':'')
      +(vids.length?'<optgroup label="Videos">'+vids.map(function(p){return '<option value="'+p+'" data-type="video">'+p.split('/').pop()+'</option>'}).join('')+'</optgroup>':'');
  });
}

function _getABInputType(){
  var mode=$('ab-itype')?$('ab-itype').value:'file';
  if(mode==='camera')return 'camera';
  if(mode==='rtsp')return 'rtsp';
  var sel=$('ab-img');if(!sel||!sel.selectedOptions.length)return 'image';
  return sel.selectedOptions[0].getAttribute('data-type')||'image';
}

function toggleABInput(){
  var t=$('ab-itype').value;
  var fp=$('ab-file-pick');if(fp)fp.classList.toggle('hidden',t!=='file');
  var cp=$('ab-cam-pick');if(cp)cp.classList.toggle('hidden',t!=='camera');
  var rp=$('ab-rtsp-pick');if(rp)rp.classList.toggle('hidden',t!=='rtsp');
  var frm=$('ab-frames-pick');if(frm)frm.classList.toggle('hidden',t==='file');
  if(t==='camera')loadCameras();
  if(t==='rtsp')initRTSPStreams('ab-rtsp-stream');
}

async function doABRun(){
  if(_abInFlight){toast(T('Run already in progress'),'warn');return}
  const abMode=$('ab-itype')?$('ab-itype').value:'file';
  const inputType=_getABInputType();
  const inputPath=(abMode==='file')?$('ab-img').value:'';
  if(abMode==='file'&&!inputPath){toast(T('Select an image or video'),'warn');return}
  const reqs=[];
  const slotMap=[];
  for(let i=0;i<S.abCols;i++){
    const mn=$('ab-model-'+i).value;if(!mn)continue;
    const m=findModel(mn);if(!m)continue;
    const body={model_name:mn,category:m.category,model_file:m.model_file,lang:$('ab-lang-'+i).value,variant:'sync',input_type:inputType,device_id:0};
    if(inputType==='image')body.image_path=inputPath;
    else if(inputType==='video')body.video_path=inputPath;
    if(inputType==='camera'){body.camera_id=parseInt($('ab-camera').value)||0;body.loop=parseInt($('ab-frames').value)||30}
    if(inputType==='rtsp'){body.rtsp_url=buildRTSPUrl('ab-rtsp-ip','ab-rtsp-stream');body.loop=parseInt($('ab-frames').value)||30}
    reqs.push(body);
    slotMap.push(i);
    $('ab-res-'+i).innerHTML='<div class="spinner" style="width:16px;height:16px"></div>';
  }
  if(!reqs.length){toast(T('Select at least one model'),'warn');return}
  _abInFlight=true;
  const btn=$('ab-run-btn');
  if(btn)btn.disabled=true;
  try{
  const res=await postJ('/api/run_multi',{requests:reqs});
  const results=Array.isArray(res)?res:[];
  // Build original preview (use /file/ route for server-side paths)
  var isLive=(inputType==='camera'||inputType==='rtsp');
  var origHtml='';
  if(isLive){
    origHtml='<div class="txt-dim txt-sm" style="padding:8px">📹 Live source ('+(inputType==='camera'?'/dev/video'+($('ab-camera').value||'0'):'RTSP')+')</div>';
  }else if(inputType==='image'){
    origHtml='<img src="/file/'+inputPath+'" class="res-img mb8" onclick="previewImg(this.src)" style="max-width:100%;border:1px solid var(--bg-2);border-radius:6px"/>';
  }else{
    origHtml='<video src="/file/'+inputPath+'" controls style="max-width:100%;border-radius:6px" class="mb8"></video>';
  }
  results.forEach(function(r,ri){
    var si=slotMap[ri];
    if(!r){$('ab-res-'+si).innerHTML='<p class="txt-dim">'+T('No result')+'</p>';return}
    var h='<div class="ab-result-pair">';
    h+='<div class="ab-orig"><div class="ab-label">'+T('Original')+'</div>'+origHtml+'</div>';
    h+='<div class="ab-output"><div class="ab-label">'+T('Result')+'</div>';
    if(inputType==='video'&&r.result_video_url){
      h+='<video src="'+r.result_video_url+'" controls class="res-img mb8" style="max-width:100%;border-radius:6px"></video>';
    }else if(r.result_image){
      h+='<img src="data:image/jpeg;base64,'+r.result_image+'" class="res-img mb8" onclick="previewImg(this.src)"/>';
    }else{
      h+='<p class="txt-dim txt-sm">'+T('No visual result')+'</p>';
    }
    h+='</div></div>';
    h+='<div class="perf-grid">';
    if(r.fps)h+='<div class="pcard"><div class="pv txt-acc">'+r.fps+'</div><div class="pk">FPS</div></div>';
    if(r.latency)h+='<div class="pcard"><div class="pv">'+r.latency+'ms</div><div class="pk">Latency</div></div>';
    h+='</div>';
    if(r.perf&&r.perf.pipeline&&r.perf.pipeline.length){h+='<div class="mt8">'+renderWaterfall(r.perf)+'</div>';}
    if(r.exit_code!==0)h+='<p class="txt-sm" style="color:var(--error)">Exit code: '+r.exit_code+'</p>';
    if(r.output)h+='<details class="mt8"><summary class="clickable txt-dim txt-sm">\ud83d\udccb Full Output</summary><div class="code mt4" style="max-height:200px;overflow:auto;font-size:10px">'+esc(r.output)+'</div></details>';
    $('ab-res-'+si).innerHTML=h;
  });
  $('ab-compare-card').classList.remove('hidden');
  var ct='<table class="tbl mt8"><thead><tr><th>'+T('Slot')+'</th><th>'+T('Model')+'</th><th>FPS</th><th>Latency</th></tr></thead><tbody>';
  results.forEach(function(r,ri){
    var si=slotMap[ri];
    var mn=$('ab-model-'+si)?$('ab-model-'+si).value:'';
    var slots='ABCDEFGH';
    ct+='<tr><td>'+slots[si]+'</td><td>'+esc(mn)+'</td>'
      +'<td class="txt-acc">'+(r&&r.fps?r.fps:'\u2014')+'</td>'
      +'<td>'+(r&&r.latency?r.latency+'ms':'\u2014')+'</td></tr>';
  });
  ct+='</tbody></table>';
  $('ab-cmp-table').innerHTML=ct;
  }finally{
    _abInFlight=false;
    if(btn)btn.disabled=false;
  }
}

if (typeof registerLangRefresher === 'function') {
  registerLangRefresher(function refreshComparePageLanguage() {
    if (document.querySelector('#page-compare.active') && typeof refreshCompareLanguage === 'function') refreshCompareLanguage();
  });
}
