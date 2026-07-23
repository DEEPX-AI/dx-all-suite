
let _outFiles=[];
let _outView='grid';   // 'grid' | 'table'
let _outFilter='all';  // 'all' | 'image' | 'video' | 'archive' | 'other'

const _TYPE_ICON={image:'🖼️',video:'🎬',archive:'📦',other:'📄'};
const _TYPE_LABEL={all:T('All'),image:T('Images'),video:T('Videos'),archive:T('Archives'),other:T('Other')};

async function loadOutputs(){
  const data=await api('/api/outputs');
  _outFiles=Array.isArray(data)?data:[];
  _renderFilterChips();
  _renderOutputs();
}
function refreshOutputsIfVisible(){
  const page=$('page-outputs');
  if(page&&page.classList.contains('active'))loadOutputs();
}

function setOutView(v){_outView=v;_renderOutputs();
  document.querySelectorAll('.out-view-btn').forEach(b=>b.classList.toggle('active',b.dataset.view===v));}
function setOutFilter(f){_outFilter=f;_renderOutputs();
  document.querySelectorAll('.out-filter-chip').forEach(c=>c.classList.toggle('active',c.dataset.filter===f));}

function _filtered(){return _outFilter==='all'?_outFiles:_outFiles.filter(f=>f.type===_outFilter);}

function _renderFilterChips(){
  const counts={all:_outFiles.length,image:0,video:0,archive:0,other:0};
  _outFiles.forEach(f=>counts[f.type]=(counts[f.type]||0)+1);
  const el=$('out-filters');
  if(!el)return;
  el.innerHTML=Object.keys(_TYPE_LABEL).map(k=>
    '<button class="out-filter-chip'+(k===_outFilter?' active':'')+'" data-filter="'+k+'" onclick="setOutFilter(\''+k+'\')">'+
    (_TYPE_ICON[k]||'📋')+' '+_TYPE_LABEL[k]+' <span class="chip-count">'+counts[k]+'</span></button>'
  ).join('');
}

function _renderOutputs(){
  const files=_filtered();
  const empty=$('out-empty');
  if(empty)empty.style.display=files.length?'none':'block';

  // Table view – also toggle parent card visibility
  const tbl=$('out-table');
  const tableCard=tbl&&tbl.closest('.card');
  if(tableCard)tableCard.style.display=_outView==='table'?'':'none';
  if(tbl)tbl.style.display=_outView==='table'?'':'none';
  if(_outView==='table'&&tbl){
    tbl.querySelector('tbody').innerHTML=files.map(f=>{
      const icon=_TYPE_ICON[f.type]||'📄';
      const preview=f.type==='image'?'<button class="btn btn-sm btn-ghost" onclick="openLightbox(\''+esc(f.name)+'\')">👁️</button>':'';
      return '<tr><td>'+icon+' '+esc(f.name)+'</td>'
        +'<td class="txt-dim txt-sm">'+fmtBytes(f.size||0)+'</td>'
        +'<td class="txt-dim txt-sm">'+fmtTime(f.mtime)+'</td>'
        +'<td>'+preview
        +(f.type==='image'&&f.src_image?'<button class="btn btn-sm btn-ghost" onclick="openCompare(\''+esc(f.name)+'\')">⚖️</button>':'')
        +'<a class="btn btn-sm btn-ghost" href="'+f.url+'" download="'+f.name+'">⬇</a>'
        +'<button class="btn btn-sm btn-ghost txt-err" onclick="deleteOutput(\''+esc(f.name)+'\')">🗑️</button></td></tr>';
    }).join('')||'<tr><td colspan="4" class="txt-dim">No files</td></tr>';
  }

  const grid=$('out-gallery');
  if(grid)grid.style.display=_outView==='grid'?'':'none';
  if(_outView==='grid'&&grid){
    grid.innerHTML=files.map(f=>{
      const icon=_TYPE_ICON[f.type]||'📄';
      const thumb=f.type==='image'
        ?'<img class="gal-thumb" src="'+f.url+'" alt="'+esc(f.name)+'" loading="lazy" onclick="openLightbox(\''+esc(f.name)+'\')">'
        :f.type==='video'
        ?'<video class="gal-thumb" src="'+f.url+'" muted preload="metadata" onclick="openLightbox(\''+esc(f.name)+'\')"></video>'
        :'<div class="gal-thumb gal-thumb-icon">'+icon+'</div>';
      const compareBtn=f.type==='image'&&f.src_image
        ?'<button class="btn btn-xs btn-ghost" onclick="event.stopPropagation();openCompare(\''+esc(f.name)+'\')">⚖️ Compare</button>':'';
      return '<div class="gal-card" data-type="'+f.type+'">'
        +thumb
        +'<div class="gal-info">'
        +'<span class="gal-name txt-sm" title="'+esc(f.name)+'">'+esc(f.name)+'</span>'
        +'<span class="gal-meta txt-dim txt-xs">'+fmtBytes(f.size||0)+' · '+fmtTime(f.mtime)+'</span>'
        +'<div class="gal-actions">'
        +compareBtn
        +'<a class="btn btn-xs btn-ghost" href="'+f.url+'" download="'+f.name+'" onclick="event.stopPropagation()">⬇</a>'
        +'<button class="btn btn-xs btn-ghost txt-err" onclick="event.stopPropagation();deleteOutput(\''+esc(f.name)+'\')">🗑️</button>'
        +'</div></div></div>';
    }).join('')||'<p class="txt-dim txt-sm">No files matching filter.</p>';
  }
}

function openLightbox(name){
  const f=_outFiles.find(x=>x.name===name);if(!f)return;
  const dlg=$('gallery-lightbox');if(!dlg)return;
  const body=$('lb-body');
  if(f.type==='image'){
    body.innerHTML='<img src="'+f.url+'" class="lb-img" alt="'+esc(f.name)+'">';
  }else if(f.type==='video'){
    body.innerHTML='<video src="'+f.url+'" class="lb-img" controls autoplay muted></video>';
  }else{
    body.innerHTML='<div class="lb-placeholder">'+(_TYPE_ICON[f.type]||'📄')+'<br>'+esc(f.name)+'</div>';
  }
  $('lb-title').textContent=f.name;
  $('lb-download').href=f.url;$('lb-download').download=f.name;
  const cmpBtn=$('lb-compare');
  if(cmpBtn)cmpBtn.style.display=(f.type==='image'&&f.src_image)?'':'none';
  if(cmpBtn)cmpBtn.onclick=()=>{dlg.close();openCompare(name);};
  dlg.showModal();
}
function closeLightbox(){const d=$('gallery-lightbox');if(d)d.close();}

function openCompare(name){
  const f=_outFiles.find(x=>x.name===name);
  if(!f||!f.src_image)return toast(T('No source image for comparison'),'warn');
  const dlg=$('compare-dialog');if(!dlg)return;
  $('cmp-after').src=f.url;
  $('cmp-before').src='/'+f.src_image;
  $('cmp-slider').value=50;
  _updateCompareSlider(50);
  $('cmp-title').textContent='Before / After — '+f.name;
  dlg.showModal();
}
function closeCompare(){const d=$('compare-dialog');if(d)d.close();}
function _updateCompareSlider(v){
  const pct=v||$('cmp-slider').value;
  const wrap=$('cmp-wrap');if(!wrap)return;
  wrap.style.setProperty('--split',pct+'%');
}

async function deleteOutput(name){
  if(!confirm(T('Delete ')+name+'?'))return;
  const r=await postJ('/api/outputs/delete',{name});
  if(r.error)return toast(r.error,'err');
  toast(T('Deleted ')+name,'ok');
  loadOutputs();
}

if (typeof registerLangRefresher === 'function') {
  registerLangRefresher(function refreshOutputsLanguage() {
    if (document.querySelector('#page-outputs.active') && typeof loadOutputs === 'function') loadOutputs();
  });
}
