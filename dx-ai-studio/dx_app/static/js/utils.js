// State, utilities, navigation, helpers


const S={
  models:[],images:[],videos:[],cats:[],
  selImg:'',chartMode:'temp',
  rtData:[],rtView:'rt',accRange:'5m',abCols:2,pipeSteps:[],
  devToken:null,benchAbort:false,benchRes:{},
  sseSource:null,cpuCores:4
};
const CAT_IMG={object_detection:'sample/img/sample_street.jpg',face_detection:'sample/img/sample_face.jpg',
 pose_estimation:'sample/img/sample_people.jpg',obb_detection:'sample/img/sample_parking.jpg',classification:'sample/img/sample_dog.jpg',
 instance_segmentation:'sample/img/sample_street.jpg',semantic_segmentation:'sample/img/sample_horse.jpg',
 depth_estimation:'sample/img/sample_kitchen.jpg',image_denoising:'sample/img/sample_dark_room.jpg',super_resolution:'sample/img/sample_dark_room.jpg',
 image_enhancement:'sample/img/sample_dark_room.jpg',embedding:'sample/img/face_pair',reid:'sample/img/person_pair',ppu:'sample/img/sample_face.jpg',
 face_alignment:'sample/img/sample_face.jpg',hand_landmark:'sample/img/sample_people.jpg',
 attribute_recognition:'sample/img/sample_person_a1.jpg',
 hand_detection:'sample/img/sample_hand.jpg',keypoint_detection:'sample/img/sample_street.jpg',
 object_pose_estimation:'sample/dope/000000.png',panoptic_driving_perception:'sample/img/sample_parking.jpg',
 '3d_object_detection':'sample/kitti/velodyne/000049.bin',
 object_detection_x_semantic_segmentation:'sample/img/sample_parking.jpg'};
// CSS token-aware color constants (resolved at runtime)
const _cs=getComputedStyle(document.documentElement);
const _cv=k=>_cs.getPropertyValue(k).trim();
const WF_COLORS=[_cv('--info'),_cv('--app-accent'),_cv('--warning'),_cv('--error'),_cv('--npu')];
const WF_STEPS=['Read','Preprocess','Inference','Postprocess','Display'];

const $=id=>document.getElementById(id);
const esc=s=>{const d=document.createElement('div');d.textContent=s;return d.innerHTML};
function api(url,opts){return fetch(url,opts).then(r=>r.json()).catch(e=>({error:e.message}))}
function findModel(name){return S.models.find(function(m){return m.name===name})}
function postJ(url,body){return api(url,{method:'POST',headers:{'Content-Type':'application/json','X-Lab-Token':S.labToken||S.devToken||''},body:JSON.stringify(body)})}

const _toastIcons={ok:'✅',err:'❌',info:'ℹ️',warn:'⚠️'};
const _toastHistory=[];
const _TOAST_HIST_MAX=100;
let _toastUnread=0;

function toast(msg,type='info',opts){
  if(!opts)opts={};
  const tc=type==='ok'?'ok':type==='err'?'err':type==='warn'?'warn':'info';
  const icon=_toastIcons[tc]||'ℹ️';
  _toastHistory.unshift({msg,type:tc,time:Date.now(),icon,actionLabel:opts.action?opts.action.label:null,actionUrl:opts.action&&opts.action.url?opts.action.url:null});
  if(_toastHistory.length>_TOAST_HIST_MAX)_toastHistory.pop();
  _toastUnread++;
  _updateNotifBadge();
  const t=document.createElement('div');
  t.className='toast toast-'+tc;
  t.innerHTML='<span class="toast-icon">'+icon+'</span><span class="toast-msg">'+esc(msg)+'</span>';
  if(opts.action){
    const ab=document.createElement('button');ab.className='toast-action';ab.textContent=opts.action.label;
    ab.onclick=function(){opts.action.fn();t.classList.remove('show');setTimeout(()=>t.remove(),400);};
    t.appendChild(ab);
  }
  if(!opts.persist){
    const cb=document.createElement('button');cb.className='toast-close';cb.innerHTML='✕';
    cb.onclick=function(){t.classList.remove('show');setTimeout(()=>t.remove(),400);};
    t.appendChild(cb);
  }
  $('toast-wrap').appendChild(t);
  requestAnimationFrame(()=>t.classList.add('show'));
  if(!opts.persist){
    const dur=opts.duration||3500;
    setTimeout(()=>{t.classList.remove('show');setTimeout(()=>t.remove(),400)},dur);
  }
}

function _updateNotifBadge(){
  const b=$('notif-badge');
  if(!b)return;
  if(_toastUnread>0){b.textContent=_toastUnread>99?'99+':_toastUnread;b.style.display='inline-block';}
  else{b.style.display='none';}
}

function toggleNotifDrawer(){
  const d=$('notif-drawer');
  if(!d)return;
  const open=d.classList.toggle('open');
  if(open){
    _toastUnread=0;_updateNotifBadge();
    _renderNotifHistory();
  }
}

function _isNotifDrawerOpen(){
  const d=$('notif-drawer');
  return !!(d&&d.classList.contains('open'));
}

function _renderNotifHistory(){
  const c=$('notif-list');
  if(!c)return;
  if(!_toastHistory.length){c.innerHTML='<p class="txt-dim" style="padding:16px;text-align:center">'+T('No notifications yet')+'</p>';return;}
  c.innerHTML=_toastHistory.map(function(h){
    const ts=fmtClock(h.time);
    var actionHtml=h.actionUrl?'<br><a class="btn btn-xs btn-acc" href="'+esc(h.actionUrl)+'" download style="margin-top:4px;display:inline-block;font-size:10px;padding:3px 10px;background:var(--accent);color:#fff;border-radius:6px;text-decoration:none;font-weight:600">⬇️ '+esc(h.actionLabel||T('Download'))+'</a>':'';
    return '<div class="notif-item notif-'+h.type+'"><span class="notif-icon">'+h.icon+'</span><span class="notif-msg">'+esc(h.msg)+actionHtml+'</span><span class="notif-time">'+ts+'</span></div>';
  }).join('');
}

function clearNotifHistory(){
  _toastHistory.length=0;_toastUnread=0;_updateNotifBadge();
  const c=$('notif-list');if(c)c.innerHTML='<p class="txt-dim" style="padding:16px;text-align:center">'+T('Cleared')+'</p>';
}
function openModal(id){
  var d=$(id);
  d.showModal();
  // Close when clicking on the backdrop (outside .modal content)
  if(!d._bdClose){
    d._bdClose=true;
    d.addEventListener('click',function(e){
      if(e.target===d)d.close();
    });
  }
}
function closeModal(id){$(id).close()}
function fmtBytes(b){if(b<1024)return b+'B';if(b<1048576)return(b/1024).toFixed(1)+'KB';return(b/1048576).toFixed(1)+'MB'}
const LOCALE_BY_LANG={
  en:'en-US',
  ko:'ko-KR',
  ja:'ja-JP',
  'zh-CN':'zh-CN',
  'zh-TW':'zh-TW',
  es:'es-ES'
};
function getLang(){return (window.DXI18n&&DXI18n.lang)||localStorage.getItem('dx-lang')||'en'}
function getLocale(){return LOCALE_BY_LANG[getLang()]||'en-US'}
function fmtDate(ts){const d=new Date(ts*1000);return d.toLocaleDateString(getLocale())}
function fmtTime(ts){const d=new Date(ts*1000);return d.toLocaleString(getLocale(),{hour12:false})}
function fmtClock(epochMs){const d=new Date(epochMs);return d.toLocaleTimeString(getLocale(),{hour12:false,hour:'2-digit',minute:'2-digit',second:'2-digit'})}
function tempColor(t){return t<40?_cv('--success'):t<55?_cv('--warning'):_cv('--error')}

const PAGES=['setup','models','run','bench','compare','modelzoo','lab','outputs','reference'];
const PAGE_TITLES={setup:'⚙️ Setup & Install',models:'Models',run:'Run Inference',bench:'Benchmark',compare:'A/B Compare',modelzoo:'📥 ModelZoo',lab:'🧪 Lab',outputs:'Outputs',reference:'📖 Reference'};
function _applyLangToActivePage(){
  if(!window.DXI18n)return;
  const active=document.querySelector('.page.active');
  DXI18n.applyLang(active||document);
}
function nav(page){
  // Auto-stop continuous inference when leaving Run page
  if(CONT.running)contStop();
  PAGES.forEach(p=>{
    const el=$('page-'+p);if(el)el.classList.toggle('active',p===page);
  });
  document.querySelectorAll('.nav-item').forEach(n=>n.classList.toggle('active',n.dataset.page===page));
  $('topbar-title').textContent=T(PAGE_TITLES[page]||page);
  if(page==='outputs')loadOutputs();
  if(page==='models')renderModelsPage();
  if(page==='run'){initRunPage();loadRunImages()}
  if(page==='bench')initBenchPage();
  if(page==='compare'){setABCols(S.abCols);initABImages()}
  if(page==='modelzoo')initModelZoo();
  if(page==='lab')initLabPage();
  if(page==='setup')setupInit();
  // Re-apply i18n after page content renders
  if(window.DXI18n)setTimeout(function(){_applyLangToActivePage();},50);
}
// openDev is defined in developer.js (with auth logic)


function toggleSidebar(){
  const sb=document.querySelector('.sidebar');
  const ml=document.querySelector('.main');
  sb.classList.toggle('collapsed');
  ml.style.marginLeft=sb.classList.contains('collapsed')?'60px':'220px';
}




function updateSlider(id,val){$(id).textContent=val}

function refreshActivePageLanguage(){
  _applyLangToActivePage();
  const active=document.querySelector('.page.active');
  const page=active&&active.id?active.id.replace(/^page-/,''):'';
  const titleEl=$('topbar-title');
  if(titleEl&&page)titleEl.textContent=T(PAGE_TITLES[page]||page);
  if(typeof _i18nOptions==='function')_i18nOptions();
  if(_isNotifDrawerOpen())_renderNotifHistory();
  if(page==='models'&&typeof renderModelsPage==='function')renderModelsPage();
  else if(page==='run')refreshRunLanguage();
  else if(page==='bench')refreshBenchLanguage();
  else if(page==='compare')refreshCompareLanguage();
  else if(page==='lab'&&typeof initLabPage==='function')initLabPage();
}

// Safe language-only refresh helpers (no API calls, no state reset)
function refreshRunLanguage(){
  var catSel=$('r-cat');
  var cat=catSel?catSel.value:'';
  if(catSel&&catSel.options.length&&catSel.options[0].value==='')
    catSel.options[0].textContent=T('— Select Category —');
  if(cat)updateRunParams(cat);
}

function refreshBenchLanguage(){
  var catSel=$('b-cat');
  if(catSel&&catSel.options.length&&catSel.options[0].value==='')
    catSel.options[0].textContent=T('All Categories');
  var imgSel=$('b-img-sel');
  if(imgSel&&imgSel.options.length&&imgSel.options[0].value==='')
    imgSel.options[0].textContent=T('Default (built-in)');
  var vidSel=$('b-vid-sel');
  if(vidSel&&vidSel.options.length&&vidSel.options[0].value==='')
    vidSel.options[0].textContent=T('Default (built-in)');
  var lbl=$('b-loop-label');
  if(lbl){
    var t=$('b-input-type')?$('b-input-type').value:'image';
    lbl.textContent=(t==='camera'||t==='rtsp')?T('Frame Count'):T('Loop Count');
  }
  // Update run button text if benchmark is running
  var runBtn=$('b-run-btn');
  if(runBtn&&typeof _benchRunning!=='undefined'&&_benchRunning)runBtn.textContent=T('⏳ Running…');
}

function refreshCompareLanguage(){
  // Re-translate placeholder labels in existing panels without rebuilding
  for(var i=0;i<S.abCols;i++){
    var catSel=$('ab-cat-'+i);
    if(catSel&&catSel.options.length&&catSel.options[0].value==='')
      catSel.options[0].textContent=T('All Tasks');
    var modSel=$('ab-model-'+i);
    if(modSel&&modSel.options.length&&modSel.options[0].value==='')
      modSel.options[0].textContent=T('— Select Model —');
  }
}

// Language changes handled by lang-refresh.js (refreshDxAppModuleLanguage)

