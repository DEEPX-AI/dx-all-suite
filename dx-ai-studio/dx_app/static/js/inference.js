
var _runMediaCache={};
var _runMediaPending={};
var _runMediaCacheTTL=60000; // 60s TTL
var _lastRunImageCategory=null;
var _lastSelectedRunImageEl=null;
var _runInFlight=false;
var PENDING_AUTO_SELECT=null;

// config.json key → Run UI slider (extend bindings for new tunables; values come from API config)
var RUN_PARAM_BINDINGS=[
  {configKey:'score_threshold',altKeys:['confidence_threshold','conf_threshold'],el:'r-conf',sections:['r-conf-row','r-params-detect','r-params-classify']},
  {configKey:'nms_threshold',altKeys:['iou_threshold'],el:'r-nms',sections:['r-params-detect']},
  {configKey:'obj_threshold',el:'r-obj',sections:['r-params-detect'],optionalRow:'r-obj-row'},
  {configKey:'top_k',el:'r-topk',sections:['r-params-classify']},
  {configKey:'alpha',el:'r-alpha',sections:['r-params-seg'],optional:true}
];

function _cfgPick(cfg,binding){
  if(!cfg||typeof cfg!=='object')return null;
  if(cfg[binding.configKey]!=null)return cfg[binding.configKey];
  var alts=binding.altKeys||[];
  for(var i=0;i<alts.length;i++){if(cfg[alts[i]]!=null)return cfg[alts[i]];}
  return null;
}

function _sliderDefault(elId){
  var el=$(elId);if(!el)return null;
  return el.getAttribute('data-default')||el.defaultValue||el.value;
}

function _setRunSlider(elId,val){
  var el=$(elId);if(!el||val==null||val==='')return;
  var num=Number(val);
  if(!isFinite(num))return;
  if(el.id==='r-topk'){
    var topk=Math.max(1,Math.round(num));
    if(topk>Number(el.max))el.max=String(topk);
    el.value=String(topk);
    if(el.nextElementSibling)el.nextElementSibling.textContent=String(topk);
    return;
  }
  el.value=String(num);
  if(el.nextElementSibling)el.nextElementSibling.textContent=String(num);
}

function _isRunSectionVisible(sectionId){
  var sec=$(sectionId);
  if(!sec)return false;
  if(sec.classList.contains('hidden'))return false;
  if(sec.style&&sec.style.display==='none')return false;
  return true;
}

function _isRunControlActive(binding){
  var el=$(binding.el);if(!el)return false;
  if(binding.optionalRow){
    var row=$(binding.optionalRow);
    if(row&&row.classList.contains('hidden'))return false;
  }
  var sections=binding.sections||[];
  if(!sections.length)return true;
  for(var i=0;i<sections.length;i++){
    if(_isRunSectionVisible(sections[i]))return true;
  }
  return false;
}

function resetRunParamsToDefaults(){
  RUN_PARAM_BINDINGS.forEach(function(b){
    _setRunSlider(b.el,_sliderDefault(b.el));
    if(b.optionalRow){var row=$(b.optionalRow);if(row)row.classList.add('hidden');}
  });
}

function applyRunParamsFromModel(m){
  var cfg=(m&&m.config)||{};
  RUN_PARAM_BINDINGS.forEach(function(b){
    var val=_cfgPick(cfg,b);
    if(val!=null){
      _setRunSlider(b.el,val);
      if(b.optionalRow){var row=$(b.optionalRow);if(row)row.classList.remove('hidden');}
    }else if(b.optionalRow){
      var hideRow=$(b.optionalRow);
      if(hideRow)hideRow.classList.add('hidden');
      _setRunSlider(b.el,_sliderDefault(b.el));
    }
  });
}

function collectRunConfigOverrides(){
  var out={};
  RUN_PARAM_BINDINGS.forEach(function(b){
    if(!_isRunControlActive(b))return;
    var el=$(b.el);if(!el)return;
    var raw=el.value;
    if(raw===''||raw==null)return;
    var num=Number(raw);
    if(!isFinite(num))return;
    if(b.configKey==='top_k')out[b.configKey]=Math.max(1,Math.round(num));
    else out[b.configKey]=num;
  });
  return out;
}

function _invalidateRunMediaCache(cat){
  if(cat){delete _runMediaCache[cat];delete _runMediaPending[cat];}
  else{_runMediaCache={};_runMediaPending={};}
}

function setTextIfChanged(el,text){
  if(el&&el.textContent!==text)el.textContent=text;
}

function translatedError(res){
  var raw=(res&&res.error)||'';
  if(res&&res.error_key){
    var translated=T(res.error_key);
    if(translated&&translated!==res.error_key){
      return raw&&raw!==translated?translated+' — '+raw:translated;
    }
  }
  return raw;
}

function quickRun(name,cat,modelFile){
  PENDING_AUTO_SELECT={name:name,category:cat,modelFile:modelFile||'',source:'models'};
  nav('run');
}

function _applyPendingAutoSelect(){
  if(!PENDING_AUTO_SELECT)return;
  var ps=PENDING_AUTO_SELECT;PENDING_AUTO_SELECT=null;
  setTimeout(function(){
    var catSel=$('r-cat');
    if(!catSel)return;
    for(var i=0;i<catSel.options.length;i++){if(catSel.options[i].value===ps.category){catSel.selectedIndex=i;break;}}
    onRCat();
    var modSel=$('r-model');
    if(!modSel)return;
    for(var j=0;j<modSel.options.length;j++){if(modSel.options[j].value===ps.name){modSel.selectedIndex=j;break;}}
    if(modSel.value)onRModel();
    if(ps.source==='deploy'){
      toast(T('Deployed model ')+ps.name+T(' selected. Press Run to start inference.'),'ok');
    }
  },150);
}

function initRunPage(){
  _invalidateRunMediaCache();
  $('r-export-out').classList.add('hidden');
  var cats=[...new Set(S.models.map(function(m){return m.category}))].sort();
  $('r-cat').innerHTML='<option value="">'+T('— Select Category —')+'</option>'+cats.map(function(c){return '<option value="'+esc(c)+'">'+esc(c)+'</option>'}).join('');
  _applyPendingAutoSelect();
}

function onRCat(){
  var cat=$('r-cat').value;$('r-model').innerHTML='<option value="">\u2014</option>';
  if(!cat){resetRunParamsToDefaults();updateRunInputMode('');return;}
  var mods=S.models.filter(function(m){return m.category===cat});
  $('r-model').innerHTML='<option value="">\u2014</option>'+mods.map(function(m){return '<option value="'+esc(m.name)+'">'+esc(m.name)+'</option>'}).join('');
  resetRunParamsToDefaults();
  loadRunImages(cat);
  updateRunParams(cat);
  updateRunInputMode(cat);
}

function updateRunInputMode(cat){
  // Mirror of dx_app _IMAGE_ONLY_TASKS (common/runner/sync_runner.py): single-model
  // examples for these tasks reject video/camera/rtsp — they need a detector crop
  // pipeline (embedding/reid/attribute), are single-frame (hand_*), or use non-video
  // input (DOPE static pose, SFA3D LiDAR .bin). Video is disabled for them here.
  var imageOnly=['embedding','reid','attribute_recognition',
                 'hand_landmark','hand_detection','object_pose_estimation','3d_object_detection'];
  var vidRadio=$('r-input-vid');
  var imgRadio=$('r-input-img');
  var restrict=imageOnly.indexOf(cat)!==-1;
  if(restrict&&imgRadio)imgRadio.checked=true;
  if(vidRadio){
    vidRadio.disabled=restrict;
    var lbl=vidRadio.closest('label');
    if(lbl)lbl.style.opacity=restrict?'0.45':'';
  }
  toggleRInput();
}

function _runMediaThumb(path){
  if(/\.(jpe?g|png|bmp)$/i.test(path))return path;
  var pairCovers={
    'sample/img/face_pair':'sample/img/face_pair/1_reference.jpg',
    'sample/img/person_pair':'sample/img/person_pair/1_reference.jpg'
  };
  return pairCovers[path]||path;
}

function updateRunParams(cat){
  // Categories that need detection params (confidence + NMS)
  var detectCats=['object_detection','face_detection','pose_estimation','obb_detection','instance_segmentation','ppu','hand_landmark','face_alignment'];
  // Categories that need classification params
  var classifyCats=['classification','attribute_recognition'];
  // Categories that need segmentation params
  var segCats=['semantic_segmentation'];
  // Categories that need no params (restoration-type)
  var noneDescMap={
    depth_estimation:T('Depth estimation: predicts depth for every pixel without a separate threshold.'),
    image_denoising:T('Denoising: automatically removes noise from the input image.'),
    super_resolution:T('Super-resolution: automatically upscales the input image.'),
    image_enhancement:T('Enhancement: automatically improves brightness and contrast.'),
    embedding:T('Embedding: select a face pair folder (2+ images). The first image becomes the reference; later images are compared via cosine similarity.'),
    reid:T('ReID: select a person pair folder (2+ images). The first image becomes the reference; later images are compared via cosine similarity.')
  };
  $('r-params-detect').classList.add('hidden');
  $('r-params-classify').classList.add('hidden');
  $('r-params-seg').classList.add('hidden');
  $('r-params-none').classList.add('hidden');
  // Show confidence slider for detect + classify
  var confRow=$('r-conf').closest('.grid2');
  if(detectCats.indexOf(cat)!==-1){
    $('r-params-detect').classList.remove('hidden');
    if(confRow)confRow.style.display='';
    $('r-params-note').textContent=T('Passed to the model\'s config.json as score_threshold / nms_threshold');
  }else if(classifyCats.indexOf(cat)!==-1){
    $('r-params-classify').classList.remove('hidden');
    if(confRow)confRow.style.display='';
    $('r-params-note').textContent=T('Top-K: shows the top-K class predictions');
  }else if(segCats.indexOf(cat)!==-1){
    $('r-params-seg').classList.remove('hidden');
    if(confRow)confRow.style.display='none';
    $('r-params-note').textContent=T('Semantic segmentation: predicts per-pixel class labels');
  }else if(noneDescMap[cat]){
    $('r-params-none').classList.remove('hidden');
    $('r-params-desc').textContent=noneDescMap[cat];
    if(confRow)confRow.style.display='none';
    $('r-params-note').textContent='';
  }else{
    $('r-params-detect').classList.remove('hidden');
    if(confRow)confRow.style.display='';
    $('r-params-note').textContent=T('Passed to the model\'s config.json as the corresponding parameters');
  }
}

function onRModel(){
  const m=S.models.find(x=>x.name===$('r-model').value);if(!m)return;
  const lang=$('r-lang');lang.innerHTML='';
  if(m.cpp)lang.innerHTML+='<option value="cpp">C++</option>';
  if(m.python)lang.innerHTML+='<option value="python">Python</option>';
  const mode=$('r-mode');mode.innerHTML='';
  if(m.cpp_sync||m.py_sync)mode.innerHTML+='<option value="sync">Sync</option>';
  if(m.cpp_async||m.py_async)mode.innerHTML+='<option value="async">Async</option>';
  applyRunParamsFromModel(m);
  loadRunImages(m.category);
  updateRunParams(m.category);
  updateRunInputMode(m.category);
}

function loadRunImages(cat){
  cat=cat||'__all__';
  if(_lastRunImageCategory===cat&&_runMediaCache[cat]&&(Date.now()-_runMediaCache[cat]._ts)<_runMediaCacheTTL){
    _renderRunMedia(cat,_runMediaCache[cat]);
    return;
  }
  if(_runMediaPending[cat])return;
  var grid=$('img-grid');
  if(grid)grid.innerHTML='<p class="txt-dim">'+T('Loading…')+'</p>';
  _lastRunImageCategory=cat;
  var imgUrl=(cat&&cat!=='__all__')?('/api/images?category='+encodeURIComponent(cat)):'/api/images';
  _runMediaPending[cat]=Promise.all([api(imgUrl),api('/api/videos')]).then(function(results){
    _runMediaCache[cat]={
      images:Array.isArray(results[0])?results[0]:[],
      videos:Array.isArray(results[1])?results[1]:[],
      _ts:Date.now()
    };
    _renderRunMedia(cat,_runMediaCache[cat]);
  }).finally(function(){
    delete _runMediaPending[cat];
  });
}

function _renderRunMedia(cat,media){
  var grid=$('img-grid');
  var list=media&&Array.isArray(media.images)?media.images:[];
  var defImg=CAT_IMG[cat];
  if(defImg&&(!S.selectedImage||list.indexOf(S.selectedImage)===-1)){
    S.selectedImage=defImg;
  }
  if(grid){
    grid.innerHTML=list.map(function(p){
      var fn=p.split('/').pop();
      var sel=S.selectedImage===p?' selected':'';
      var isImg=/\.(jpe?g|png|bmp)$/i.test(p);
      var isDir=!isImg&&!/\.[a-z0-9]+$/i.test(p);
      if(!isImg&&!isDir){
        // Non-image input (e.g. LiDAR .bin point cloud) — no raster thumbnail exists,
        // show a labeled placeholder tile instead of a broken <img>.
        var ext=(fn.split('.').pop()||'').toUpperCase();
        return '<div class="img-item img-item--data'+sel+'" onclick="pickImg(this,\''+p+'\')" title="'+fn+'">'
          +'<div class="img-data-ph"><span class="img-data-ext">'+esc(ext)+'</span><span class="img-data-name">'+esc(fn)+'</span></div></div>';
      }
      var thumb=_runMediaThumb(p);
      var badge=isDir?'<span class="img-dir-badge">📁</span>':'';
      return '<div class="img-item'+sel+'" onclick="pickImg(this,\''+p+'\')" title="'+fn+'">'
        +badge+'<img src="/file/'+thumb+'" alt="'+fn+'" loading="lazy"/></div>';
    }).join('')||'<p class="txt-dim">'+T('No images')+'</p>';
    _lastSelectedRunImageEl=grid.querySelector('.img-item.selected');
  }
  var vids=media&&Array.isArray(media.videos)?media.videos:[];
  var vidOpts=vids.map(function(v){return '<option value="'+v+'">'+v.split('/').pop()+'</option>'}).join('')||'<option value="">'+T('No videos')+'</option>';
  var rVideo=$('r-video'),cVideo=$('c-video');
  if(rVideo)rVideo.innerHTML=vidOpts;
  if(cVideo)cVideo.innerHTML=vidOpts;
}

function pickImg(el,path){
  if(_lastSelectedRunImageEl&&_lastSelectedRunImageEl!==el)_lastSelectedRunImageEl.classList.remove('selected');
  el.classList.add('selected');S.selectedImage=path;
  _lastSelectedRunImageEl=el;
  // Picking a sample clears any pending upload so the two inputs never conflict.
  S.uploadedImage=null;var un=$('r-upload-name');if(un)un.textContent='';
}

var _MAX_UPLOAD_BYTES=8*1024*1024;  // mirrors backend MAX_IMAGE_BASE64_BYTES budget
function onRunUpload(input){
  var f=input.files&&input.files[0];if(!f)return;
  if(f.size>_MAX_UPLOAD_BYTES){toast(T('Image too large (max 8MB)'),'err');input.value='';return;}
  var rd=new FileReader();
  rd.onload=function(){
    S.uploadedImage=rd.result;                 // data:image/...;base64,....
    S.selectedImage=null;                      // upload wins over sample selection
    if(_lastSelectedRunImageEl){_lastSelectedRunImageEl.classList.remove('selected');_lastSelectedRunImageEl=null;}
    var un=$('r-upload-name');if(un)un.textContent=f.name;
    toast(T('Image ready — press Run'),'ok');
  };
  rd.onerror=function(){toast(T('Failed to read file'),'err');};
  rd.readAsDataURL(f);
}

function toggleRInput(){
  var val=document.querySelector('input[name="r-itype"]:checked').value;
  $('img-picker').classList.toggle('hidden',val!=='image');
  $('video-picker').classList.toggle('hidden',val!=='video');
    if(val==='video'){
    var model=$('r-model').value;
    var m=model?findModel(model):null;
    var langEl=$('r-lang');
    if(m&&m.python&&langEl&&langEl.querySelector('option[value="python"]')){
      // Python path supports --save on video; stock C++ --save can crash (VideoWriter w/h=0).
      if(langEl.value==='cpp')langEl.value='python';
    }
  }
}

function loadCameras(){
  api('/api/cameras').then(function(cams){
    if(!Array.isArray(cams)||!cams.length){
      var nocam='<option value="" disabled>'+T('No cameras found')+'</option>';
      ['c-camera','b-cam-sel','ab-camera'].forEach(function(id){var el=$(id);if(el)el.innerHTML=nocam});
      return;
    }
    var opts=cams.map(function(c){
      var lbl=c.device+(c.available?' ('+c.width+'×'+c.height+')':T(' (unavailable)'));
      return '<option value="'+c.index+'"'+(c.available?'':' disabled')+'>'+lbl+'</option>';
    }).join('');
    ['c-camera','b-cam-sel','ab-camera'].forEach(function(id){var el=$(id);if(el)el.innerHTML=opts});
  });
}

function initRTSPStreams(selId){
  var el=$(selId);if(!el||el.options.length>1)return;
  var opts='';
  for(var i=1;i<=16;i++)opts+='<option value="stream'+i+'">Stream '+i+'</option>';
  el.innerHTML=opts;
  ['c-rtsp-stream','b-rtsp-stream','ab-rtsp-stream'].forEach(function(id){
    var s=$(id);if(s&&s.options.length<=1)s.innerHTML=opts;
  });
}

function buildRTSPUrl(ipId,streamId){
  var ip=$(ipId)?$(ipId).value:'';
  var stream=$(streamId)?$(streamId).value:'stream1';
  return 'rtsp://'+ip+'/'+stream;
}

async function doRun(){
  if(_runInFlight){toast(T('Run already in progress'),'warn');return}
  const model=$('r-model').value;if(!model){toast(T('Select a model'),'warn');return}
  const m=findModel(model);if(!m){toast(T('Model not found'),'err');return}
  if(!m.model_file){toast(T('⚠ Model file not configured for ')+model,'err');$('r-result').innerHTML='<p style="color:var(--error)">\u274c '+T('Model file not configured.')+'<br><span class="txt-dim">'+T('Please configure model file in Developer mode.')+'</span></p>';return}
  if(m.model_exists===false){toast(T('⚠ Model file missing: ')+m.model_file,'err');$('r-result').innerHTML='<p style="color:var(--error)">\u274c '+T('Model file not found')+'<br><code style="font-size:11px;color:var(--text-3)">'+esc(m.model_file)+'</code><br><span class="txt-dim">'+T('Model file (.dxnn) does not exist. Please compile and try again.')+'</span></p>';return}
  const lang=$('r-lang').value;
  if(lang==='cpp'&&!m.cpp){toast(T('⚠ C++ binary not built for ')+model,'err');$('r-result').innerHTML='<p style="color:var(--error)">\u274c '+T('C++ binary has not been built.')+'<br><span class="txt-dim">'+T('Run <code>make</code> build first or switch to Python.')+'</span></p>';return}
  if(lang==='python'&&!m.python){toast(T('⚠ Python app not found for ')+model,'err');$('r-result').innerHTML='<p style="color:var(--error)">\u274c '+T('Python app not found.')+'<br><span class="txt-dim">'+T('Switch to C++ or add a Python app.')+'</span></p>';return}
  const isImg=$('r-input-img').checked;
  const inputType=isImg?'image':'video';
  if(isImg&&!S.selectedImage&&!S.uploadedImage){toast(T('Please select or upload an image'),'warn');return}
  if(inputType==='video'&&!$('r-video').value){toast(T('Please select a video'),'warn');return}
  const runBtn=$('r-run-btn');
  _runInFlight=true;
  if(runBtn)runBtn.disabled=true;
  try{
  S.running=true;$('r-result').innerHTML='<div class="spin"></div><p class="txt-dim mt8">'+T('Running inference…')+'</p>';
  const body={model_name:model,category:m.category,model_file:m.model_file,
    lang:$('r-lang').value,variant:$('r-mode').value,input_type:inputType,
    device_id:parseInt($('r-dev').value)||0,
    config_overrides:collectRunConfigOverrides()};
  if(isImg&&S.uploadedImage)body.image_base64=S.uploadedImage;
  else if(isImg&&S.selectedImage)body.image_path=S.selectedImage;
  else if(inputType==='video')body.video_path=$('r-video').value;
  const res=await postJ('/api/run',body);
  if(res.error){
    var errMsg=translatedError(res);
    var rawErr=res.error||'';
    var hint='';
    if(rawErr.indexOf('dx_engine')!==-1||rawErr.indexOf('engine')!==-1)hint='<br><span class="txt-dim">'+T('Check that dx_engine is running. Real inference is not available in Mock mode.')+'</span>';
    else if(rawErr.indexOf('not found')!==-1||rawErr.indexOf('No such')!==-1)hint='<br><span class="txt-dim">'+T('Check the model file or executable path.')+'</span>';
    else if(rawErr.indexOf('timeout')!==-1||rawErr.indexOf('Timeout')!==-1)hint='<br><span class="txt-dim">'+T('Inference timed out. Try again with a smaller input.')+'</span>';
    $('r-result').innerHTML='<p style="color:var(--error)">'+T('❌ Error: ')+esc(errMsg)+hint+'</p>';
    toast(errMsg,'err');return;
  }
  renderRunResult(res);
  if(typeof refreshOutputsIfVisible === 'function')refreshOutputsIfVisible();
  }finally{
    S.running=false;
    _runInFlight=false;
    if(runBtn)runBtn.disabled=false;
  }
}

function renderRunResult(r){
  var h='';
  var isVideo=!$('r-input-img').checked;
  var cat=$('r-cat').value;
  var VIS_HINTS={
    classification:T('📊 Classification Result: overlays Top-K predicted classes and probabilities as text on the image.'),
    attribute_recognition:T('🏷️ Attribute Result: overlays predicted person/face attributes and confidence scores on the image.'),
    depth_estimation:T('🌈 Depth Result: visualizes depth using JET colormap (red=near, blue=far).'),
    embedding:T('📐 Embedding Result: side-by-side reference vs current image with cosine similarity (SAME / DIFFERENT).'),
    reid:T('🧍 ReID Result: side-by-side reference vs current image with cosine similarity (SAME / DIFFERENT).'),
    image_denoising:T('🔇 Denoising Result: outputs the denoised image. DnCNN may process in grayscale (Y channel).'),
    super_resolution:T('🔍 Super Resolution Result: outputs the upscaled image. ESPCN processes the Y channel and restores color.'),
    image_enhancement:T('✨ Enhancement Result: outputs the image with improved brightness and contrast.'),
    semantic_segmentation:T('🎨 Semantic Segmentation: alpha-blends per-pixel class labels using Cityscapes colormap onto the original.'),
    instance_segmentation:T('🎭 Instance Segmentation: draws per-instance color masks + bounding boxes + class labels.'),
    pose_estimation:T('💃 Pose Estimation: draws skeleton (joint connections) and keypoints. Low-confidence keypoints may be omitted.'),
    hand_landmark:T('🤚 Hand Landmark: draws 21 hand landmark points and connections.'),
    face_alignment:T('😊 Face Alignment: draws 3D facial landmark points.')
  };
  if(VIS_HINTS[cat]){
    h+='<div style="background:var(--accent-dim);border:1px solid rgba(99,140,255,.2);border-radius:8px;padding:8px 12px;margin-bottom:10px;font-size:11px;color:var(--accent)">'+VIS_HINTS[cat]+'</div>';
  }
  if(r.result_video_url){h+='<div class="mb8"><video src="'+r.result_video_url+'" controls class="res-img" style="max-width:100%"></video></div>'}
  var pairCats=['embedding','reid'];
  // CMP slider applies when input is an image and result_image is present (not pair-compare layouts)
  // "Before" image is either a picked sample (served via /file/) or an uploaded
  // data URL — support both so the compare slider also works for uploads.
  var beforeSrc=S.uploadedImage?S.uploadedImage:(S.selectedImage?'/file/'+S.selectedImage:null);
  if(r.result_image&&!isVideo&&beforeSrc&&pairCats.indexOf(cat)===-1){
    var cmpId='cmp-'+Date.now();
    h+='<div class="cmp-wrap mb8" id="'+cmpId+'">';
    h+='<img class="cmp-before" src="'+beforeSrc+'" crossorigin="anonymous"/>';
    h+='<span class="cmp-lbl cmp-lbl-orig">'+T('Original')+'</span>';
    h+='<div class="cmp-after-clip"><img src="data:image/jpeg;base64,'+r.result_image+'" alt="result"/><span class="cmp-lbl cmp-lbl-result">'+T('Result')+'</span></div>';
    h+='<div class="cmp-handle"></div>';
    h+='</div>';
    var _cid=cmpId;setTimeout(function(){initCmpSlider(_cid)},60);
  }else if(r.result_image&&!isVideo){
    h+='<div class="mb8"><img src="data:image/jpeg;base64,'+r.result_image+'" class="res-img" onclick="previewImg(this.src)"/></div>';
  }
  h+='<div class="perf-grid">';
  if(r.fps)h+='<div class="pcard"><div class="pv txt-acc">'+r.fps+'</div><div class="pk">FPS</div></div>';
  if(r.latency)h+='<div class="pcard"><div class="pv">'+r.latency+'ms</div><div class="pk">Latency</div></div>';
  if(r.fps_per_watt)h+='<div class="pcard"><div class="pv" style="color:var(--success)">'+r.fps_per_watt+'</div><div class="pk">FPS/W</div></div>';
  if(r.elapsed_s)h+='<div class="pcard"><div class="pv">'+r.elapsed_s+'s</div><div class="pk">Elapsed</div></div>';
  var exitColor=r.exit_code===0?'var(--success)':'var(--error)';
  var exitIcon=r.exit_code===0?'\u2705':'\u274c';
  h+='<div class="pcard"><div class="pv" style="color:'+exitColor+'">'+exitIcon+'</div><div class="pk">Exit '+r.exit_code+'</div></div>';
  h+='</div>';
  if(r.perf&&r.perf.pipeline&&r.perf.pipeline.length){
    h+='<div class="mt8">'+renderWaterfall(r.perf)+'</div>';
  }
  // Task-tag specific summary (single run)
  if(r.task_tag&&r.task_summary){
    h+='<div class="mt8"><div style="font-size:11px;color:var(--text-3);margin-bottom:4px">'+T('📊 Task Summary (')+r.task_tag+')</div>';
    h+=renderTaskSummary(r.task_tag,r.task_summary)+'</div>';
  }else if(r.det_summary&&Object.keys(r.det_summary).length){
    h+='<div class="mt8">'+renderDetSummary(r.det_summary)+'</div>';
  }
  if(r.exit_code!==0){
    h+='<div style="background:rgba(248,81,73,.08);border:1px solid rgba(248,81,73,.2);border-radius:8px;padding:8px 12px;margin-top:10px;font-size:11px;color:var(--error)">'+T('⚠️ Inference exited abnormally (exit code: ')+r.exit_code+T('). Check Full Output for details.')+'</div>';
  }
  if(r.output){h+='<details class="mt8"><summary class="clickable txt-dim">'+T('📋 Full Output')+'</summary><div class="code mt8">'+esc(r.output)+'</div></details>'}
  $('r-result').innerHTML=h;
}

function previewImg(src){
  $('img-preview').src=src;
  openModal('modal-imgpreview');
}

function initCmpSlider(id){
  var wrap=$(id);if(!wrap)return;
  var clip=wrap.querySelector('.cmp-after-clip');
  var handle=wrap.querySelector('.cmp-handle');
  if(!clip||!handle)return;
  // Fix container to source image aspect ratio (prevents resolution mismatch)
  var beforeImg=wrap.querySelector('.cmp-before');
  function normalizeCmpSize(){
    var nw=beforeImg.naturalWidth,nh=beforeImg.naturalHeight;
    if(!nw||!nh)return;
    wrap.style.aspectRatio=nw+'/'+nh;
    wrap.classList.add('cmp-ready');
  }
  if(beforeImg&&beforeImg.complete&&beforeImg.naturalWidth)normalizeCmpSize();
  else if(beforeImg)beforeImg.addEventListener('load',normalizeCmpSize);
  var dragging=false;
  function setPct(pct){
    pct=Math.max(2,Math.min(98,pct));
    clip.style.clipPath='inset(0 '+(100-pct)+'% 0 0)';
    handle.style.left=pct+'%';
  }
  function setPos(clientX){
    var rect=wrap.getBoundingClientRect();
    setPct((clientX-rect.left)/rect.width*100);
  }
  function onDocMouseMove(e){setPos(e.clientX)}
  function onDocMouseUp(){stopDrag();document.removeEventListener('mousemove',onDocMouseMove);document.removeEventListener('mouseup',onDocMouseUp)}
  function onDocTouchMove(e){e.preventDefault();setPos(e.touches[0].clientX)}
  function onDocTouchEnd(){stopDrag();document.removeEventListener('touchmove',onDocTouchMove);document.removeEventListener('touchend',onDocTouchEnd)}
  function startDrag(){dragging=true;wrap.classList.add('cmp-dragging')}
  function stopDrag(){dragging=false;wrap.classList.remove('cmp-dragging')}
  wrap.addEventListener('mousedown',function(e){startDrag();e.preventDefault();setPos(e.clientX);document.addEventListener('mousemove',onDocMouseMove);document.addEventListener('mouseup',onDocMouseUp)});
  wrap.addEventListener('touchstart',function(e){startDrag();setPos(e.touches[0].clientX);document.addEventListener('touchmove',onDocTouchMove,{passive:false});document.addEventListener('touchend',onDocTouchEnd)},{passive:true});
  // A안: 결과 100% → 0.8초 후 50%로 sweep
  setTimeout(function(){setPct(50)},500);
}

async function doStop(){
  await postJ('/api/stop',{});
  S.running=false;toast(T('Stopped'),'info');
}

async function doExportFromRun(){
  var model=$('r-model').value;if(!model){toast(T('Please select a model first'),'warn');return}
  var m=findModel(model);if(!m){toast(T('Model not found'),'err');return}
  var lang=$('r-export-lang').value;
  var path=m.category+'/'+model;
  var btn=$('r-export-btn');btn.disabled=true;btn.textContent='⏳ '+T('Extracting...');
  $('r-export-out').classList.remove('hidden');$('r-export-out').textContent=T('Extracting package: ')+path+'\n...';
  var res=await postJ('/api/extract',{model_path:path,lang:lang});
  btn.disabled=false;btn.textContent='📦 '+T('Export');
  if(res.ok){
    var txt=T('✅ Extraction complete! Output: ')+res.output_dir+'\n\n';
    (res.results||[]).forEach(function(r){
      txt+='['+r.lang+'] '+(r.ok?'✅ OK':'❌ FAIL')+'\n';
      if(r.output)txt+=r.output+'\n';
    });
    if(res.download_url){
      txt+='\n📦 Download: '+res.download_url+'\n';
    }
    $('r-export-out').innerHTML=esc(txt)+(res.download_url?'<br><a class="btn btn-sm btn-acc" href="'+res.download_url+'" download style="margin-top:8px;display:inline-block">⬇️ '+T('Download .tar.gz')+'</a>':'');
    toast(T('Package ready for download'),'ok',{duration:5000,action:res.download_url?{label:T('Download'),url:res.download_url,fn:function(){window.open(res.download_url)}}:null});
  }else{
    $('r-export-out').textContent=T('❌ Error: ')+(res.error||T('Unknown'));
    toast(res.error||T('Extraction failed'),'err');
  }
}

var CONT={slots:[{cat:'',model:''}],running:false,timerInt:null,startTime:0};

function toggleRunTab(tab){
  $('run-single-tab').classList.toggle('hidden',tab!=='single');
  $('run-cont-tab').classList.toggle('hidden',tab!=='continuous');
  document.querySelectorAll('.run-tab').forEach(function(b){b.classList.toggle('active',b.dataset.rtab===tab)});
  if(tab==='continuous')initContTab();
}

function initContTab(){
  api('/api/videos').then(function(vids){
    var list=Array.isArray(vids)?vids:[];
    $('c-video').innerHTML=list.map(function(v){return '<option value="'+v+'">'+v.split('/').pop()+'</option>'}).join('')||'<option value="">'+T('No videos')+'</option>';
  });
  contRenderSlots();
}

function contRenderSlots(){
  var h='';
  CONT.slots.forEach(function(sl,i){
    var cats=[...new Set(S.models.map(function(m){return m.category}))].sort();
    var catOpts='<option value="">\u2014 Category \u2014</option>'+cats.map(function(c){
      return '<option'+(c===sl.cat?' selected':'')+'>'+c+'</option>';
    }).join('');
    var modOpts='<option value="">\u2014 Model \u2014</option>';
    if(sl.cat){
      var mods=S.models.filter(function(m){return m.category===sl.cat});
      modOpts+=mods.map(function(m){return '<option'+(m.name===sl.model?' selected':'')+'>'+m.name+'</option>'}).join('');
    }
    h+='<div class="cont-slot-cfg" data-cidx="'+i+'">';
    h+='<span style="color:var(--text-3);font-size:11px;font-weight:700;min-width:16px">'+(i+1)+'</span>';
    h+='<select onchange="contOnCat('+i+',this.value)">'+catOpts+'</select>';
    h+='<select onchange="contOnModel('+i+',this.value)">'+modOpts+'</select>';
    if(CONT.slots.length>1)h+='<button class="cont-x" onclick="contRemoveSlot('+i+')">\u00d7</button>';
    h+='</div>';
  });
  $('c-slots').innerHTML=h;
  $('c-slot-count').textContent='('+CONT.slots.length+'/8)';
  $('c-add-btn').disabled=CONT.slots.length>=8;
  contRenderGrid();
}

function contOnCat(idx,val){
  CONT.slots[idx].cat=val;CONT.slots[idx].model='';
  contRenderSlots();
}
function contOnModel(idx,val){CONT.slots[idx].model=val}

function toggleContInput(){
  var t=$('c-input-type').value;
  $('c-video-pick').classList.toggle('hidden',t!=='video');
  $('c-camera-pick').classList.toggle('hidden',t!=='camera');
  $('c-rtsp-pick').classList.toggle('hidden',t!=='rtsp');
  if(t==='camera')loadCameras();
  if(t==='rtsp')initRTSPStreams('c-rtsp-stream');
}

function contAddSlot(){
  if(CONT.slots.length>=8){toast(T('You can add up to 8 models'),'warn');return}
  CONT.slots.push({cat:'',model:''});
  contRenderSlots();
}
function contRemoveSlot(idx){
  if(CONT.slots.length<=1)return;
  CONT.slots.splice(idx,1);
  contRenderSlots();
}

function contRenderGrid(){
  var n=CONT.slots.length;
  var grid=$('c-grid');
  grid.className='cont-grid '+(n<=1?'g1':'g2');
  var h='';
  for(var i=0;i<n;i++){
    var mName=CONT.slots[i].model||T('(no model selected)');
    h+='<div class="cont-slot" id="c-slot-'+i+'">';
    h+='<div class="cont-overlay">';
    h+='<span class="cont-badge cb-model">'+esc(mName)+'</span>';
    h+='<span class="cont-badge cb-fps" id="c-fps-'+i+'"></span>';
    h+='<span class="cont-badge cb-status" id="c-status-'+i+'"></span>';
    h+='</div>';
    h+='<div class="cont-ph" id="c-ph-'+i+'">'+(CONT.running?T('⏳ Waiting…'):T('▶ Press Start to begin inference'))+'</div>';
    h+='</div>';
  }
  grid.innerHTML=h;
}

async function contStart(){
  var valid=CONT.slots.every(function(sl){return sl.cat&&sl.model});
  if(!valid){toast(T('Please select Category and Model for all slots'),'warn');return}
  var cInputType=$('c-input-type')?$('c-input-type').value:'video';
  if(cInputType==='video'&&!$('c-video').value){toast(T('Please select a video'),'warn');return}
  for(var i=0;i<CONT.slots.length;i++){
    var m=findModel(CONT.slots[i].model);
    if(!m){toast(T('Model not found: ')+CONT.slots[i].model,'err');return}
    if(!m.model_file){toast(T('Model file not configured: ')+CONT.slots[i].model,'err');return}
    if(m.model_exists===false){toast(T('Model file not found: ')+CONT.slots[i].model,'err');return}
  }
  CONT.running=true;
  $('c-start-btn').classList.add('hidden');
  $('c-stop-btn').classList.remove('hidden');
  document.querySelectorAll('#run-cont-tab select, #c-add-btn').forEach(function(el){el.disabled=true});
  document.querySelectorAll('.cont-x').forEach(function(el){el.disabled=true});
  CONT.startTime=Date.now();
  $('c-timer').classList.add('active');
  CONT.timerInt=setInterval(function(){
    var s=Math.floor((Date.now()-CONT.startTime)/1000);
    var m=Math.floor(s/60);s=s%60;
    $('c-timer-txt').textContent=(m<10?'0':'')+m+':'+(s<10?'0':'')+s;
  },1000);
  // ── Camera / RTSP → Live mode (Xvfb + MJPEG) ──
  if(cInputType==='camera'||cInputType==='rtsp'){
    return contStartLive(cInputType);
  }

  contRenderGrid();
  // Run inferences sequentially
  var allResults=[];
  for(var i=0;i<CONT.slots.length;i++){
    if(!CONT.running)break;
    var sl=CONT.slots[i];
    var m=findModel(sl.model);
    var slot=$('c-slot-'+i);
    if(slot){slot.className='cont-slot processing'}
    var statusEl=$('c-status-'+i);
    if(statusEl)statusEl.textContent=T('⏳ Processing...');
    var phEl=$('c-ph-'+i);
    if(phEl)phEl.innerHTML='<div class="spin"></div><p class="txt-dim mt8">'+esc(sl.model)+T(' running inference…')+'</p>';
    var body={
      model_name:sl.model,category:sl.cat,model_file:m.model_file,
      lang:$('c-lang').value,variant:$('c-mode').value,
      input_type:cInputType,device_id:parseInt($('c-dev').value)||0
    };
    if(cInputType==='video')body.video_path=$('c-video').value;
    if(cInputType==='camera'){body.camera_id=parseInt($('c-camera').value)||0;body.loop=parseInt($('c-cam-frames').value)||300}
    if(cInputType==='rtsp'){body.rtsp_url=buildRTSPUrl('c-rtsp-ip','c-rtsp-stream')}
    var res=await postJ('/api/run',body);
    allResults.push(res);
    if(!CONT.running)break;
    contShowResult(i,res,sl.model);
  }
  contFinish(allResults);
}

function contShowResult(idx,res,modelName){
  var slot=$('c-slot-'+idx);
  var fpsEl=$('c-fps-'+idx);
  var statusEl=$('c-status-'+idx);
  if(!slot)return;
  if(res.error){
    slot.className='cont-slot error';
    setTextIfChanged(statusEl,T('❌ Error'));
    var phEl=$('c-ph-'+idx);
    if(phEl)phEl.innerHTML='<p style="color:var(--error);font-size:12px;padding:12px">❌ '+esc(translatedError(res))+'</p>';
    return;
  }
  slot.className='cont-slot done';
  setTextIfChanged(statusEl,T('✅ Done'));
  if(res.fps)setTextIfChanged(fpsEl,res.fps+' FPS');
  var content='';
  if(res.result_video_url){
    content='<video src="'+res.result_video_url+'" autoplay loop muted playsinline style="width:100%;display:block;border-radius:var(--radius)"></video>';
  }else if(res.result_image){
    content='<img src="data:image/jpeg;base64,'+res.result_image+'" style="width:100%;display:block;border-radius:var(--radius)"/>';
  }else{
    content='<div class="cont-ph">'+T('ℹ️ No result video was generated')+'</div>';
  }
  // Keep overlay, replace content
  var overlay=slot.querySelector('.cont-overlay');
  slot.innerHTML=content;
  if(overlay)slot.insertBefore(overlay,slot.firstChild);
  var ov=slot.querySelector('.cont-overlay');
  if(!ov){
    ov=document.createElement('div');ov.className='cont-overlay';
    ov.innerHTML='<span class="cont-badge cb-model">'+esc(modelName)+'</span><span class="cont-badge cb-fps" id="c-fps-'+idx+'">'+(res.fps?res.fps+' FPS':'')+'</span><span class="cont-badge cb-status" id="c-status-'+idx+'">'+T('✅ Done')+'</span>';
    slot.insertBefore(ov,slot.firstChild);
  }
}

function contFinish(results){
  CONT.running=false;
  clearInterval(CONT.timerInt);
  $('c-timer').classList.remove('active');
  $('c-start-btn').classList.remove('hidden');
  $('c-stop-btn').classList.add('hidden');
  document.querySelectorAll('#run-cont-tab select, #c-add-btn').forEach(function(el){el.disabled=false});
  document.querySelectorAll('.cont-x').forEach(function(el){el.disabled=false});
  $('c-add-btn').disabled=CONT.slots.length>=8;
  if(typeof refreshOutputsIfVisible === 'function')refreshOutputsIfVisible();
  if(results&&results.length>0){
    var h='<div class="perf-grid">';
    results.forEach(function(r,i){
      if(!r)return;
      var col=r.error?'var(--error)':'var(--accent)';
      var icon=r.error?'❌':'✅';
      h+='<div class="pcard"><div class="pv" style="color:'+col+'">'+icon+'</div><div class="pk">'+(CONT.slots[i]?CONT.slots[i].model:'Slot '+i)+'</div></div>';
      if(r.fps)h+='<div class="pcard"><div class="pv txt-acc">'+r.fps+'</div><div class="pk">FPS</div></div>';
      if(r.latency)h+='<div class="pcard"><div class="pv">'+r.latency+'ms</div><div class="pk">Latency</div></div>';
      if(r.elapsed_s)h+='<div class="pcard"><div class="pv">'+r.elapsed_s+'s</div><div class="pk">Elapsed</div></div>';
    });
    h+='</div>';
    // Task-tag specific summaries for sequential runs
    results.forEach(function(r,i){
      if(!r||r.error)return;
      if(r.task_tag&&r.task_summary){
        h+='<div class="mt8"><div style="font-size:11px;color:var(--text-3);margin-bottom:4px">📊 '+(CONT.slots[i]?CONT.slots[i].model:'Slot '+i)+' ('+r.task_tag+')</div>';
        h+=renderTaskSummary(r.task_tag,r.task_summary)+'</div>';
      }else if(r.det_summary&&Object.keys(r.det_summary).length){
        h+='<div class="mt8"><div style="font-size:11px;color:var(--text-3);margin-bottom:4px">'+(CONT.slots[i]?CONT.slots[i].model:'Slot '+i)+'</div>';
        h+=renderDetSummary(r.det_summary)+'</div>';
      }
    });
    $('c-summary').innerHTML=h;
    $('c-summary').style.display='';
  }
  toast(T('Continuous inference complete'),'ok');
}

async function contStop(){
  var cInputType=$('c-input-type')?$('c-input-type').value:'video';
  if(cInputType==='camera'||cInputType==='rtsp'){
    contStopLive();
    return;
  }
  CONT.running=false;
  await postJ('/api/stop',{});
  clearInterval(CONT.timerInt);
  $('c-timer').classList.remove('active');
  $('c-start-btn').classList.remove('hidden');
  $('c-stop-btn').classList.add('hidden');
  document.querySelectorAll('#run-cont-tab select, #c-add-btn').forEach(function(el){el.disabled=false});
  document.querySelectorAll('.cont-x').forEach(function(el){el.disabled=false});
  $('c-add-btn').disabled=CONT.slots.length>=8;
  document.querySelectorAll('#c-grid video').forEach(function(v){v.pause()});
  CONT.slots.forEach(function(sl,i){
    var statusEl=$('c-status-'+i);
    if(statusEl&&(statusEl.textContent==='⏳ Processing...'||statusEl.textContent==='⏳ 처리 중...'))statusEl.textContent=T('⏹ Stopped');
    var slot=$('c-slot-'+i);
    if(slot&&slot.classList.contains('processing')){slot.className='cont-slot'}
  });
  toast(T('Continuous inference stopped'),'info');
}

// Live Inference (Camera/RTSP → per-slot Xvfb → MJPEG)
var LIVE={slots:[]};

function _makeLiveSlotEl(slotIdx,modelName){
  var el=document.createElement('div');
  el.className='live-slot';
  el.id='c-ls-'+slotIdx;
  el.innerHTML=
    '<div class="live-slot-header">'+
    '<span style="color:var(--text-3)">'+T('Slot ')+(slotIdx+1)+'</span>'+
    '<span class="cont-badge cb-model" style="margin-left:6px">'+esc(modelName)+'</span>'+
    '<span class="cont-badge cb-fps" id="c-ls-fps-badge-'+slotIdx+'" style="margin-left:4px"></span>'+
    '</div>'+
    '<div class="live-slot-vid">'+
    '<img id="c-ls-img-'+slotIdx+'" style="width:100%;display:block" alt="Live '+(slotIdx+1)+'"/>'+
    '</div>'+
    '<div class="live-slot-stats">'+
    '<span class="stat-pill">Frames\u00a0<b id="c-ls-frames-'+slotIdx+'">0</b></span>'+
    '<span class="stat-pill">FPS\u00a0<b id="c-ls-fps-'+slotIdx+'">—</b></span>'+
    '<span class="stat-pill">Avg\u00a0<b id="c-ls-avg-'+slotIdx+'">0</b></span>'+
    '<span class="stat-pill">Elapsed\u00a0<b id="c-ls-ela-'+slotIdx+'">0s</b></span>'+
    '</div>'+
    '<div id="c-ls-pred-'+slotIdx+'" class="live-slot-pred" style="display:none"></div>'+
    '<div id="c-ls-chart-'+slotIdx+'" class="live-slot-chart sparkline-wrap" style="display:none"></div>';
  return el;
}

async function contStartLive(cInputType){
  var grid=$('c-live-slots');
  grid.innerHTML='';
  var n=CONT.slots.length;
  grid.className='live-slots-grid g'+n;
  LIVE.slots=[];
  LIVE.startTime=Date.now()/1000;
  $('c-grid').classList.add('hidden');
  $('c-live-view').classList.remove('hidden');
  $('c-summary').style.display='none';
  $('c-summary').innerHTML='';
  for(var i=0;i<n;i++){
    var sl=CONT.slots[i];
    var m=findModel(sl.model);
    if(!m){toast(T('Slot ')+(i+1)+T(': Model not found'),'err');continue;}
    var el=_makeLiveSlotEl(i,sl.model);
    grid.appendChild(el);
    var body={
      model_name:sl.model,category:sl.cat,model_file:m.model_file,
      lang:$('c-lang').value,variant:$('c-mode').value,
      input_type:cInputType,device_id:parseInt($('c-dev').value)||0,
      slot_idx:i,
      n_total_slots:n
    };
    if(cInputType==='camera')body.camera_id=parseInt($('c-camera').value)||0;
    if(cInputType==='rtsp')body.rtsp_url=buildRTSPUrl('c-rtsp-ip','c-rtsp-stream');
    var res=await postJ('/api/run_live',body);
    if(res.error){toast(T('Slot ')+(i+1)+': '+translatedError(res),'err');continue;}
    var lslot={slotIdx:i,jobId:res.job_id,pollInt:null,lastFrames:0,lastPollTime:0,confHistory:[],result:null,done:false,finishing:false};
    LIVE.slots.push(lslot);
    document.getElementById('c-ls-img-'+i).src='/api/live_frame?slot='+i+'&t='+Date.now();
    // Start polling (IIFE closure over lslot)
    (function(ls){
      ls.pollInt=setInterval(async function(){
        if(!ls.jobId)return;
        try{
          var poll=await api('/api/live_poll?id='+ls.jobId);
          if(!poll||poll.error)return;
          _updateSlotStats(ls,poll);
          if(!poll.running){clearInterval(ls.pollInt);contFinishLiveSlot(ls);}
        }catch(e){}
      },1000);
    })(lslot);
  }
  if(LIVE.slots.length===0){contResetUI();return;}
}

function _updateSlotStats(lslot,poll){
  var i=lslot.slotIdx;
  var now=Date.now()/1000;
  var wfps='—';
  if(lslot.lastPollTime>0){
    var dt=now-lslot.lastPollTime;
    var df=poll.frames-lslot.lastFrames;
    if(dt>0&&df>=0)wfps=(df/dt).toFixed(1);
  }
  lslot.lastFrames=poll.frames;
  lslot.lastPollTime=now;
  // Confidence sparkline for classification
  if(poll.last_pred&&poll.last_pred.length){
    var cm=poll.last_pred[0].match(/([\.\d]+)\s*%?\s*$/);
    if(cm){
      lslot.confHistory.push(parseFloat(cm[1]));
      if(lslot.confHistory.length>60)lslot.confHistory.shift();
      var chartEl=document.getElementById('c-ls-chart-'+i);
      if(chartEl&&lslot.confHistory.length>=2){
        chartEl.style.display='';
        _updateLiveSparkline(chartEl,lslot.confHistory,400,42);
      }
    }
  }
  function _u(id,val){var el=document.getElementById(id);if(el)el.textContent=val;}
  _u('c-ls-frames-'+i,poll.frames);
  _u('c-ls-fps-'+i,wfps);
  _u('c-ls-avg-'+i,poll.fps_est);
  _u('c-ls-ela-'+i,poll.elapsed+'s');
  _u('c-ls-fps-badge-'+i,wfps+' FPS');
  if(poll.last_pred&&poll.last_pred.length){
    var pred=document.getElementById('c-ls-pred-'+i);
    if(pred){pred.style.display='';pred.textContent=poll.last_pred.join('\n');}
  }
}

function _buildLiveSparklineGeometry(values,w,h){
  var min=Math.min.apply(null,values),max=Math.max.apply(null,values);
  var range=max-min||0.001;
  var pad=4;
  var pts=values.map(function(v,i){
    var x=pad+i*((w-2*pad)/(values.length-1));
    var y=(h-pad)-((v-min)/range*(h-2*pad));
    return x.toFixed(1)+','+y.toFixed(1);
  }).join(' ');
  var last=values[values.length-1];
  return{
    pts:pts,
    lx:w-pad,
    ly:(h-pad)-((last-min)/range*(h-2*pad))
  };
}

function _updateLiveSparkline(chartEl,values,w,h){
  var label=chartEl.querySelector('.sparkline-label');
  if(!label){
    label=document.createElement('div');
    label.className='sparkline-label';
    chartEl.appendChild(label);
  }
  label.textContent='Conf (top-1, '+values.length+' polls)';

  var svg=chartEl.querySelector('svg');
  var polyline=svg?svg.querySelector('polyline'):null;
  var circle=svg?svg.querySelector('circle'):null;
  if(!svg){
    svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
    svg.setAttribute('viewBox','0 0 '+w+' '+h);
    svg.setAttribute('width','100%');
    svg.setAttribute('height',h);
    svg.setAttribute('preserveAspectRatio','none');
    svg.style.display='block';
    polyline=document.createElementNS('http://www.w3.org/2000/svg','polyline');
    polyline.setAttribute('fill','none');
    polyline.setAttribute('stroke','var(--accent)');
    polyline.setAttribute('stroke-width','1.5');
    polyline.setAttribute('stroke-linejoin','round');
    circle=document.createElementNS('http://www.w3.org/2000/svg','circle');
    circle.setAttribute('r','2.5');
    circle.setAttribute('fill','var(--accent)');
    svg.appendChild(polyline);
    svg.appendChild(circle);
    chartEl.appendChild(svg);
  }
  var geom=_buildLiveSparklineGeometry(values,w,h);
  polyline.setAttribute('points',geom.pts);
  circle.setAttribute('cx',geom.lx.toFixed(1));
  circle.setAttribute('cy',geom.ly.toFixed(1));
}

async function contStopLive(){
  LIVE.slots.forEach(function(ls){clearInterval(ls.pollInt);});
  await postJ('/api/live_stop',{});
  toast(T('Stopping inference…'),'info');
  setTimeout(function(){
    LIVE.slots.forEach(function(ls){if(!ls.done)contFinishLiveSlot(ls);});
  },2500);
}

async function contFinishLiveSlot(lslot){
  if(lslot.done||lslot.finishing)return;
  lslot.finishing=true;  // re-entry guard (sync, before any await)
  clearInterval(lslot.pollInt);
  var imgEl=document.getElementById('c-ls-img-'+lslot.slotIdx);
  if(imgEl)imgEl.src='';
  try{lslot.result=await api('/api/live_result?id='+lslot.jobId);}catch(e){}
  // Fallback: if result is null/undefined (e.g. api error), synthesize from poll data
  if(!lslot.result||lslot.result.error){
    var elapsed=lslot.lastPollTime>0?Math.round(lslot.lastPollTime-(LIVE.startTime||lslot.lastPollTime)):0;
    lslot.result={
      job_id:lslot.jobId,
      model:(CONT.slots[lslot.slotIdx]||{}).model||'',
      category:(CONT.slots[lslot.slotIdx]||{}).cat||'',
      frames:lslot.lastFrames||0,
      fps_est:lslot.lastFrames>0&&elapsed>0?Math.round(lslot.lastFrames/elapsed*10)/10:0,
      elapsed:elapsed,
      perf:{},det_summary:{},
      _synthetic:true,
      _orig_error:lslot.result?lslot.result.error:null
    };
  }
  lslot.done=true;  // mark done AFTER result is collected
  if(LIVE.slots.every(function(s){return s.done;})){
    contShowSummary();
    contResetUI();
    toast(T('Live inference complete'),'ok');
  }
}

function contShowSummary(){
  var DET_CATS=['object_detection','face_detection','pose_estimation','obb_detection'];
  var CLF_CATS=['classification'];
  var h='';
  var first=true;
  LIVE.slots.forEach(function(lslot,idx){
    var sl=CONT.slots[lslot.slotIdx]||CONT.slots[idx]||{};
    var result=lslot.result;
    var cat=sl.cat||'';
    h+='<div class="live-slot-summary'+(first?'':' live-slot-summary')+'">';
    first=false;
    h+='<div class="ls-title">'+T('Slot ')+(lslot.slotIdx+1)+': '+esc(sl.model||'')+'</div>';
    if(result&&!result.error){
      if(CLF_CATS.indexOf(cat)>=0&&lslot.confHistory.length>=4){
        h+='<div class="sparkline-wrap mb8"><div class="sparkline-label">'+T('Confidence Trend')+' ('+lslot.confHistory.length+' 폴링)</div>';
        h+=renderSparkline(lslot.confHistory,400,52)+'</div>';
      }
      // Tag-based summary (new): use task_tag/task_summary if available
      if(result.task_tag&&result.task_summary){
        h+='<div class="mt8">'+renderTaskSummary(result.task_tag,result.task_summary)+'</div>';
      }else if(DET_CATS.indexOf(cat)>=0&&result.det_summary){
        // Fallback: legacy det_summary
        h+='<div class="mt8">'+renderDetSummary(result.det_summary)+'</div>';
      }
      h+='<div class="perf-grid mt8">';
      // FPS: prefer real fps from perf, fallback to estimate
      var _showFps=result.fps||'';
      if(!_showFps&&lslot.lastFrames>0){
        var _el=parseFloat(result.elapsed_seconds||result.elapsed||0);
        if(_el>0)_showFps=(lslot.lastFrames/_el).toFixed(1)+' (est)';
      }
      if(_showFps)h+='<div class="pcard"><div class="pv txt-acc">'+_showFps+'</div><div class="pk">FPS</div></div>';
      if(result.latency)h+='<div class="pcard"><div class="pv">'+result.latency+' ms</div><div class="pk">Latency</div></div>';
      var _frames=result.total_frames||result.frames||lslot.lastFrames||0;
      if(_frames)h+='<div class="pcard"><div class="pv">'+_frames+'</div><div class="pk">Frames</div></div>';
      var _time=result.total_time||result.elapsed_seconds||result.elapsed||'';
      if(_time)h+='<div class="pcard"><div class="pv">'+_time+' s</div><div class="pk">'+(result.total_time?'Time':'Elapsed')+'</div></div>';
      h+='</div>';
      if(result.perf&&result.perf.pipeline&&result.perf.pipeline.length&&!result.perf.pipeline_async_only){
        h+='<div class="mt8">'+renderPipelineTable(result.perf)+'</div>';
        h+='<div class="mt8">'+renderWaterfall(result.perf)+'</div>';
      }
      if(result.perf&&result.perf.pipeline_async_only){
        h+='<div class="pcard mt8"><div class="pv txt-acc">'+(result.perf.inference_fps||result.fps||'—')+'</div><div class="pk">Inference FPS (async)</div></div>';
      }
      if(result.perf&&result.perf.inflight_avg){
        h+='<div class="perf-grid mt8">';
        h+='<div class="pcard"><div class="pv">'+result.perf.inflight_avg+'</div><div class="pk">Inflight Avg</div></div>';
        if(result.perf.inflight_max)h+='<div class="pcard"><div class="pv">'+result.perf.inflight_max+'</div><div class="pk">Inflight Max</div></div>';
        h+='</div>';
      }
    }else if(result&&result.error){
      h+='<p style="color:var(--error);font-size:12px">❌ '+esc(result.error)+'</p>';
    }else{
      h+='<p style="color:var(--text-3);font-size:12px">'+T('No result data.')+'</p>';
    }
    h+='</div>';
  });
  if(h){$('c-summary').innerHTML=h;$('c-summary').style.display='';}
}

function contResetUI(){
  CONT.running=false;
  clearInterval(CONT.timerInt);
  $('c-timer').classList.remove('active');
  $('c-start-btn').classList.remove('hidden');
  $('c-stop-btn').classList.add('hidden');
  document.querySelectorAll('#run-cont-tab select, #c-add-btn').forEach(function(el){el.disabled=false;});
  document.querySelectorAll('.cont-x').forEach(function(el){el.disabled=false;});
  $('c-add-btn').disabled=CONT.slots.length>=8;
  $('c-grid').classList.remove('hidden');
  $('c-live-view').classList.add('hidden');
  LIVE.slots=[];
}

if (typeof registerLangRefresher === 'function') {
  registerLangRefresher(function refreshInferenceLanguage() {
    if (!document.querySelector('#page-run.active')) return;
    if (typeof refreshRunLanguage === 'function') refreshRunLanguage();
    var catSel = typeof $ === 'function' ? $('r-cat') : null;
    if (catSel && catSel.value && typeof updateRunParams === 'function') updateRunParams(catSel.value);
  });
}
