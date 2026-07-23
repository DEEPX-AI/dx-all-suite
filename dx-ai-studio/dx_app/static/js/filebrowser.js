
var FB={target:null,mode:'file',filter:null,curPath:null,selected:null};
function fileBrowse(targetId,mode,filter){
  FB.target=targetId;FB.mode=mode||'file';FB.filter=filter||null;FB.selected=null;
  var inp=$(targetId);
  var startPath=inp&&inp.value.trim()?inp.value.trim():null;
  if(startPath&&mode==='file'){
    var parts=startPath.split('/');parts.pop();
    startPath=parts.join('/')||null;
  }
  $('fb-title').textContent=mode==='dir'?T('📂 Select Folder'):T('📄 Select File');
  fbLoadDir(startPath||'~');
  openModal('modal-fb');
}
function fbLoadDir(path){
  api('/api/fs/list?path='+encodeURIComponent(path)).then(function(r){
    if(r.error){toast(r.error,'err');return;}
    FB.curPath=r.path;
    FB.selected=FB.mode==='dir'?r.path:null;
    // Input is user-managed — fbLoadDir does not overwrite it
    // Except: sync in dir mode, when input is empty, or when navigated via breadcrumb
    var cur=$('fb-cur-path').value.trim();
    if(FB.mode==='dir'||!cur||cur==='/'){
      $('fb-cur-path').value=r.path+(r.path.endsWith('/')?'':'/');
    }
    var parts=r.path.split('/').filter(Boolean);
    var bc=$('fb-breadcrumb');
    var bhtml='<span onclick="fbLoadDir(\'/\')">🏠 /</span>';
    var acc='';
    parts.forEach(function(p){
      acc+='/'+p;
      var cp=acc;
      bhtml+='&nbsp;›&nbsp;<span onclick="fbLoadDir(\''+(cp.replace(/'/g,'\\"'))+'\')">'+p+'</span>';
    });
    bc.innerHTML=bhtml;
    var list=$('fb-list');list.innerHTML='';
    if(r.parent){
      var el=document.createElement('div');
      el.className='fb-item fb-dir';
      el.textContent='📁 ..';
      var pp=r.parent;
      el.onclick=function(){fbLoadDir(pp);};
      list.appendChild(el);
    }
    (r.entries||[]).forEach(function(e){
      if(FB.mode==='dir'&&e.type==='file')return;
      var dim=FB.filter&&e.type==='file'&&e.ext!==FB.filter;
      var el=document.createElement('div');
      el.className='fb-item '+(e.type==='dir'?'fb-dir':'fb-file')+(dim?' fb-dim':'');
      var sz='';
      if(e.size!=null){sz=e.size>1048576?(e.size/1048576).toFixed(1)+'MB':e.size>1024?(e.size/1024).toFixed(0)+'KB':e.size+'B';}
      el.innerHTML=(e.type==='dir'?'📁 ':'📄 ')+'<span style="flex:1">'+e.name+'</span>'+(sz?'<span style="font-size:10px;color:var(--text-3)">'+sz+'</span>':'');
      el.style.display='flex';
      var ep=e.path,isDir=e.type==='dir';
      el.onclick=function(){
        if(isDir){
          FB.selected=ep;$('fb-cur-path').value=ep+'/';
          fbLoadDir(ep);
        }else{
          list.querySelectorAll('.fb-file').forEach(function(x){x.classList.remove('fb-selected');});
          el.classList.add('fb-selected');
          FB.selected=ep;$('fb-cur-path').value=ep;
        }
      };
      list.appendChild(el);
    });
  }).catch(function(){toast(T('File browser error'),'err');});
}
var _fbAcTimer=null,_fbAcItems=[],_fbAcParent='';
function fbPathInput(val){
  clearTimeout(_fbAcTimer);
  var ac=$('fb-ac-list');
  if(!val){ac.style.display='none';_fbAcItems=[];return;}
  _fbAcTimer=setTimeout(function(){_fbFetch(val);},80);
}
function _fbFetch(val){
  var slash=val.lastIndexOf('/');
  _fbAcParent=slash>=0?val.substring(0,slash+1):'/';
  var parent=slash>=0?(val.substring(0,slash)||'/'):'/'
  var prefix=val.substring(slash+1).toLowerCase();
  api('/api/fs/list?path='+encodeURIComponent(parent)).then(function(r){
    if(r.error){$('fb-ac-list').style.display='none';_fbAcItems=[];return;}
    _fbAcItems=(r.entries||[]).filter(function(e){
      return e.name.toLowerCase().startsWith(prefix)&&(FB.mode!=='dir'||e.type==='dir');
    });
    _fbRenderAc();
  }).catch(function(){$('fb-ac-list').style.display='none';_fbAcItems=[];});
}
function _fbRenderAc(){
  var ac=$('fb-ac-list');
  if(!_fbAcItems.length){ac.style.display='none';return;}
  ac.innerHTML=_fbAcItems.map(function(e,i){
    return '<div class="fb-ac-item" data-i="'+i+'" onmousedown="event.preventDefault();fbAcApply('+i+',true)">'
      +(e.type==='dir'?'📁 ':'📄 ')+esc(e.name)+(e.type==='dir'?'/':'')+'</div>';
  }).join('');
  ac.style.display='';
}
function fbAcApply(i,navigate){
  var e=_fbAcItems[i];if(!e)return;
  var inp=$('fb-cur-path');
  var slash=inp.value.lastIndexOf('/');
  var newPath=(slash>=0?inp.value.substring(0,slash+1):'/')+e.name+(e.type==='dir'?'/':'');
  inp.value=newPath;
  FB.selected=e.path+(e.type==='dir'?'':'');
  $('fb-ac-list').style.display='none';
  _fbAcItems=[];
  if(navigate||e.type!=='dir'){
    // Refresh list (user can keep typing)
    fbLoadDir(e.type==='dir'?e.path:(e.path.substring(0,e.path.lastIndexOf('/'))||'/'));
  }
  setTimeout(function(){inp.focus();inp.setSelectionRange(inp.value.length,inp.value.length);},10);
}
function fbPathKeydown(ev){
  var ac=$('fb-ac-list');
  var items=ac.querySelectorAll('.fb-ac-item');
  var active=ac.querySelector('.fb-ac-active');
  if(ev.key==='ArrowDown'){
    ev.preventDefault();
    if(!items.length)return;
    if(active)active.classList.remove('fb-ac-active');
    var next=active?active.nextElementSibling:items[0];
    if(!next)next=items[0];
    next.classList.add('fb-ac-active');
    return;
  }
  if(ev.key==='ArrowUp'){
    ev.preventDefault();
    if(!items.length)return;
    if(active)active.classList.remove('fb-ac-active');
    var prev=active?active.previousElementSibling:items[items.length-1];
    if(!prev)prev=items[items.length-1];
    prev.classList.add('fb-ac-active');
    return;
  }
  if(ev.key==='Tab'){
    ev.preventDefault();
    // If no dropdown items, fetch AC immediately
    if(!_fbAcItems.length){
      var val=$('fb-cur-path').value;
      if(!val)return;
      var slash=val.lastIndexOf('/');
      var parent=slash>=0?(val.substring(0,slash)||'/'):'/';
      var prefix=val.substring(slash+1).toLowerCase();
      api('/api/fs/list?path='+encodeURIComponent(parent)).then(function(r){
        if(r.error)return;
        _fbAcItems=(r.entries||[]).filter(function(e){
          return e.name.toLowerCase().startsWith(prefix)&&(FB.mode!=='dir'||e.type==='dir');
        });
        _fbTabComplete();
      });
      return;
    }
    _fbTabComplete();
    return;
  }
  if(ev.key==='Enter'){
    ev.preventDefault();
    if(active){
      var idx=parseInt(active.getAttribute('data-i'));
      fbAcApply(idx,true);
    }else{
      var v=$('fb-cur-path').value.trim();
      $('fb-ac-list').style.display='none';
      if(v){
        var isDir=v.endsWith('/');
        FB.selected=v.replace(/\/$/,'');
        fbLoadDir(isDir?v:v.substring(0,v.lastIndexOf('/')+1)||'/');
      }
    }
    return;
  }
  if(ev.key==='Escape'){$('fb-ac-list').style.display='none';return;}
}
function _fbTabComplete(){
  if(!_fbAcItems.length)return;
  if(_fbAcItems.length===1){fbAcApply(0,true);return;}
  var names=_fbAcItems.map(function(e){return e.name;});
  var common=names[0];
  for(var k=1;k<names.length;k++){
    var a=common,b=names[k],c='';
    for(var j=0;j<Math.min(a.length,b.length);j++){if(a[j]===b[j])c+=a[j];else break;}
    common=c;
  }
  var inp=$('fb-cur-path');
  var slash=inp.value.lastIndexOf('/');
  inp.value=(slash>=0?inp.value.substring(0,slash+1):'/')+common;
  // If common prefix exactly matches a directory name, append /
  var exactDir=null;
  for(var m=0;m<_fbAcItems.length;m++){
    if(_fbAcItems[m].name===common&&_fbAcItems[m].type==='dir'){exactDir=m;break;}
  }
  if(exactDir!==null){
    fbAcApply(exactDir,true);
    return;
  }
  _fbRenderAc();
  setTimeout(function(){inp.focus();inp.setSelectionRange(inp.value.length,inp.value.length);},10);
}
function fbConfirm(){
  var typed=$('fb-cur-path').value.trim();
  if(typed&&!FB.selected)FB.selected=typed;
  if(!FB.selected)FB.selected=typed;
  if(!FB.selected){toast(T('No item selected'),'warn');return;}
  if(FB.target==='_json_browse'){
    fbClose();
    var pi=$('comp-json-path');if(pi)pi.value=FB.selected||'';
    compLoadJsonFromServer(FB.selected);return;
  }
  var inp=$(FB.target);if(inp)inp.value=FB.selected;
  fbClose();
  if(FB.target==='comp-onnx-path')compInspectOnnx();
}
function compLoadJsonFromServer(path){
  fetch('/api/fs/read?path='+encodeURIComponent(path))
    .then(function(r){return r.json()})
    .then(function(r){
      if(r.content){
        try{var data=JSON.parse(r.content);compApplyJson(data);toast(T('JSON config applied: ')+path.split('/').pop(),'ok');}
        catch(e){toast(T('JSON parse error: ')+e.message,'err')}
      }else{toast(T('Failed to read file: ')+(r.error||path),'err')}
    })
    .catch(function(e){toast(T('Error: ')+e.message,'err')});
}
function fbClose(){closeModal('modal-fb');}

// ── Nav cleanup: stop polling when leaving compiler page ──
var _origNav=typeof nav==='function'?nav:null;

if (typeof registerLangRefresher === 'function') {
  registerLangRefresher(function refreshFileBrowserLanguage() {
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
  });
}
