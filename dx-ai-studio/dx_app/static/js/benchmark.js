
var _benchRunning=false; // true while doBench is executing

function _benchErrorMessage(res){
  var raw=(res&&res.error)||'';
  if(res&&res.error_key){
    var translated=T(res.error_key);
    if(translated&&translated!==res.error_key){
      return raw&&raw!==translated?translated+' — '+raw:translated;
    }
  }
  return raw;
}

function initBenchPage(){
  // Preserve state: if benchmark is running or results exist, only refresh model list
  var hasResults=S.benchRes&&Object.keys(S.benchRes).length>0;
  var skipRebuild=_benchRunning; // don't wipe results during a running benchmark
  var cats=[...new Set(S.models.map(function(m){return m.category}))].sort();
  $('b-cat').innerHTML='<option value="">'+T('All Categories')+'</option>'+cats.map(function(c){return '<option>'+c+'</option>'}).join('');
  api('/api/images').then(function(imgs){
    var list=Array.isArray(imgs)?imgs:[];
    $('b-img-sel').innerHTML='<option value="">'+T('Default (built-in)')+'</option>'+list.map(function(f){return '<option value="'+esc(f)+'">'+esc(f.split('/').pop())+'</option>'}).join('');
  });
  api('/api/videos').then(function(vids){
    var list=Array.isArray(vids)?vids:[];
    $('b-vid-sel').innerHTML='<option value="">'+T('Default (built-in)')+'</option>'+list.map(function(f){return '<option value="'+esc(f)+'">'+esc(f.split('/').pop())+'</option>'}).join('');
  });
  if(!skipRebuild)filterBenchModels();
  // Auto-select model from Compiler → Deploy & Benchmark
  if(typeof PENDING_BENCH_SELECT!=='undefined'&&PENDING_BENCH_SELECT){
    var target=PENDING_BENCH_SELECT;PENDING_BENCH_SELECT=null;
    setTimeout(function(){
      var found=false;
      document.querySelectorAll('.b-chk').forEach(function(chk){
        if(chk.value===target){chk.checked=true;found=true;}
      });
      if(found){
        toast('📊 "'+target+'" '+T('auto-selected')+' — '+T('choose comparison models and start benchmark'),'ok');
      }else{
        toast('⚠️ "'+target+'" '+T('not found in model list'),'warn');
      }
    },200);
  }
}

function toggleBenchInput(){
  var t=$('b-input-type').value;
  $('b-input-image').style.display=t==='image'?'':'none';
  $('b-input-video').style.display=t==='video'?'':'none';
  $('b-input-camera').style.display=t==='camera'?'':'none';
  $('b-input-rtsp').style.display=t==='rtsp'?'':'none';
  // Change Loop label to Frame Count for camera/rtsp
  var lbl=$('b-loop-label');
  if(lbl)lbl.textContent=(t==='camera'||t==='rtsp')?T('Frame Count'):T('Loop Count');
  if(t==='camera')loadCameras();
  if(t==='rtsp')initRTSPStreams('b-rtsp-stream');
}

function filterBenchModels(){
  const cat=$('b-cat').value, lang=$('b-lang').value;
  let list=S.models.filter(m=>{
    if(cat&&m.category!==cat)return false;
    if(lang==='cpp'&&!m.cpp)return false;
    if(lang==='python'&&!m.python)return false;
    return true;
  });
  $('bench-sel').querySelector('tbody').innerHTML=list.map(function(m){
    return '<tr><td><input type="checkbox" class="b-chk" value="'+esc(m.name)+'" data-cat="'+m.category+'"/></td>'
      +'<td>'+esc(m.name)+'</td><td><span class="badge b-cat">'+m.category+'</span></td>'
      +'<td>'+(m.cpp?'\u2713':'')+' '+(m.python?'\u2713':'')+'</td></tr>';
  }).join('');
}

function bSelAll(){document.querySelectorAll('.b-chk').forEach(c=>c.checked=true)}
function bDesel(){document.querySelectorAll('.b-chk').forEach(c=>c.checked=false)}

async function doBench(){
  const checks=[...document.querySelectorAll('.b-chk:checked')];
  if(!checks.length){toast(T('Select models to benchmark'),'warn');return}
  _benchRunning=true;
  const lang=$('b-lang').value||'cpp';
  const mode=$('b-mode').value||'sync';
  const inputType=$('b-input-type').value||'image';
  const loopCount=parseInt($('b-loop').value)||100;
  const imgPath=$('b-img-sel').value||'';
  const vidPath=$('b-vid-sel').value||'';
  const results=[];
  const tb=$('bench-res').querySelector('tbody');
  tb.innerHTML='';
  S.benchRes={};
  const rc=$('b-result-card');if(rc)rc.classList.remove('hidden');
  const runBtn=$('b-run-btn');if(runBtn){runBtn.disabled=true;runBtn.textContent='\u23f3 '+T('Running...')}
  for(const chk of checks){
    const name=chk.value,cat=chk.dataset.cat;
    const m=findModel(name);if(!m)continue;
    var rid='br-'+name.replace(/[^a-zA-Z0-9]/g,'_');
    var tr=document.createElement('tr');
    tr.id=rid;
    tr.innerHTML='<td>'+esc(name)+'</td><td colspan="6"><div class="spinner" style="width:16px;height:16px;display:inline-block"></div> '+T('Running...')+'</td>';
    tb.appendChild(tr);
    var body={model_name:name,category:cat,model_file:m.model_file,lang:lang,variant:mode,input_type:inputType,device_id:0,loop:loopCount};
    if(inputType==='image'&&imgPath)body.image_path=imgPath;
    if(inputType==='video'&&vidPath)body.video_path=vidPath;
    if(inputType==='camera'){body.camera_id=parseInt($('b-cam-sel').value)||0}
    if(inputType==='rtsp'){body.rtsp_url=buildRTSPUrl('b-rtsp-ip','b-rtsp-stream')}
    const res=await postJ('/api/run',body);
    S.benchRes[name]={...res,name:name,cat:cat,lang:lang,_inputType:inputType,_imgPath:imgPath,_vidPath:vidPath};
    results.push({name:name,cat:cat,fps:res.fps,latency:res.latency,exit_code:res.exit_code});
    var row=$(rid);
    if(row){
      var isErr=!!res.error;
      var isPassed=!isErr&&res.exit_code===0;
      var errMsg=_benchErrorMessage(res);
      var statusBadge=isPassed?'<span class="badge b-ok">'+T('PASS')+'</span>'
        :isErr?'<span class="badge b-red" title="'+esc(errMsg)+'">'+T('ERROR')+'</span>'
        :'<span class="badge b-red">'+T('FAIL')+'</span>';
      var ename=name.replace(/\\/g,'\\\\').replace(/'/g,"\\'");
      row.className='b-row-clickable';
      row.onclick=function(n){return function(){showBenchDetail(n)}}(name);
      row.innerHTML='<td><strong>'+esc(name)+'</strong></td>'
        +'<td><span class="badge b-cat">'+cat+'</span></td><td>'+statusBadge+'</td>'
        +'<td class="txt-acc">'+(res.fps||'\u2014')+'</td>'
        +'<td>'+(res.latency?res.latency+'ms':'\u2014')+'</td>'
        +'<td><button class="bench-detail-btn" onclick="event.stopPropagation();showBenchDetail(\''+ename+'\')">🔍 Detail</button></td>';
    }
  }
  if(runBtn){runBtn.disabled=false;runBtn.textContent='\u23f1\ufe0f '+T('Start Benchmark')}
  _benchRunning=false;
  const items=results.filter(function(r){return r.fps}).map(function(r){return{label:r.name.length>15?r.name.slice(0,14)+'\u2026':r.name,val:parseFloat(r.fps),color:_cv('--app-accent')}});
  if(items.length)drawBarChart($('bench-chart'),items);
  toast(T('Benchmark complete')+' ('+results.length+' '+T('models')+')','ok');
}

function showBenchDetail(name){
  var r=S.benchRes[name];if(!r){toast(T('No data — run benchmark first'),'warn');return}
  var h='';
  if(r.error){
    var errMsg=_benchErrorMessage(r);
    h+='<div style="background:rgba(248,81,73,.12);border:1px solid rgba(248,81,73,.4);border-radius:6px;padding:10px 14px;margin-bottom:12px;color:#F85149">'
      +'<strong>'+T('⚠️ Run Error:')+'</strong> '+esc(errMsg)+'</div>';
  }
  h+='<div class="flex gap8 mb12">';
  h+='<span class="badge b-cat">'+(r.cat||r.category||'')+'</span>';
  h+='<span class="badge" style="background:var(--bg-3);color:var(--text-1)">'+(r.lang||'cpp')+'</span>';
  if(r.elapsed_s)h+='<span class="txt-dim txt-sm">'+T('elapsed: ')+r.elapsed_s+'s</span>';
  h+='</div>';
  var hasOrig=(r._inputType==='image'&&r._imgPath)||(r._inputType==='video'&&r._vidPath);
  var hasResult=!!r.result_image||!!r.result_video_url;
  if(hasOrig||hasResult){
    h+='<div style="display:grid;grid-template-columns:'+(hasOrig&&hasResult?'1fr 1fr':'1fr')+';gap:12px;margin-bottom:12px">';
    if(hasOrig){
      h+='<div><div style="font-size:11px;font-weight:600;color:var(--text-3);text-transform:uppercase;margin-bottom:4px">'+T('Original')+'</div>';
      if(r._inputType==='video'&&r._vidPath)h+='<video src="/file/'+esc(r._vidPath)+'" controls style="max-width:100%;border-radius:6px"></video>';
      else if(r._imgPath)h+='<img src="/file/'+esc(r._imgPath)+'" class="res-img" onclick="previewImg(this.src)" style="max-height:300px;max-width:100%"/>';
      h+='</div>';
    }
    if(hasResult){
      h+='<div><div style="font-size:11px;font-weight:600;color:var(--text-3);text-transform:uppercase;margin-bottom:4px">'+T('Result')+'</div>';
      if(r.result_video_url)h+='<video src="'+r.result_video_url+'" controls style="max-width:100%;border-radius:6px"></video>';
      else if(r.result_image)h+='<img src="data:image/jpeg;base64,'+r.result_image+'" class="res-img" onclick="previewImg(this.src)" style="max-height:300px;max-width:100%"/>';
      h+='</div>';
    }
    h+='</div>';
  } else if(r.result_image){
    h+='<div class="mb12"><img src="data:image/jpeg;base64,'+r.result_image+'" class="res-img" onclick="previewImg(this.src)" style="max-height:300px"/></div>';
  }
  h+='<div class="perf-grid">';
  if(r.fps)h+='<div class="pcard"><div class="pv txt-acc">'+r.fps+'</div><div class="pk">FPS</div></div>';
  if(r.latency)h+='<div class="pcard"><div class="pv">'+r.latency+'ms</div><div class="pk">Latency</div></div>';

  if(r.elapsed_s)h+='<div class="pcard"><div class="pv">'+r.elapsed_s+'s</div><div class="pk">Total</div></div>';
  var ec=r.exit_code===0;
  h+='<div class="pcard"><div class="pv" style="color:'+(ec?'var(--success)':'var(--error)')+'">'+(ec?'\u2705':'\u274c')+'</div><div class="pk">Exit '+r.exit_code+'</div></div>';
  h+='</div>';
  if(r.perf&&r.perf.pipeline&&r.perf.pipeline.length)h+='<div class="mt12">'+renderWaterfall(r.perf)+'</div>';
  var hw=r.hw_after;
  if(hw){
    h+='<h2 class="mt12">'+T('HW State After Run')+'</h2><div class="perf-grid">';
    if(hw.cpu_percent!=null)h+='<div class="pcard"><div class="pv">'+hw.cpu_percent+'%</div><div class="pk">CPU</div></div>';
    if(hw.mem_percent!=null)h+='<div class="pcard"><div class="pv">'+hw.mem_percent+'%</div><div class="pk">RAM</div></div>';
    if(hw.npus&&hw.npus[0]){var n=hw.npus[0];
      if(n.temp_C!=null)h+='<div class="pcard"><div class="pv">'+n.temp_C+'\u00b0C</div><div class="pk">Temp</div></div>';
      if(n.freq_MHz!=null)h+='<div class="pcard"><div class="pv">'+n.freq_MHz+'MHz</div><div class="pk">Clock</div></div>';
      if(n.power_est_mW!=null)h+='<div class="pcard"><div class="pv">'+n.power_est_mW+'mW</div><div class="pk">Power</div></div>';}
    h+='</div>';
  }
  if(r.output)h+='<details class="mt12"><summary class="clickable txt-dim">'+T('📋 Full Output')+' ('+esc(r.output).length+' chars)</summary><div class="code mt8 txt-sm" style="max-height:300px;overflow:auto">'+esc(r.output)+'</div></details>';
  $('md-title').innerHTML=T('🔋 Benchmark Detail — ')+esc(name);
  $('md-body').innerHTML=h;
  openModal('modal-detail');
}

function benchExportReport(){
  if(!S.benchRes||!Object.keys(S.benchRes).length){toast(T('No benchmark results to export'),'warn');return;}
  var models=Object.keys(S.benchRes);
  var ts=new Date().toLocaleString(getLocale(),{hour12:false});
  var lang=models.length?S.benchRes[models[0]].lang||'cpp':'cpp';
  var inputType=models.length?S.benchRes[models[0]]._inputType||'image':'image';
  var loopCount=$('b-loop')?$('b-loop').value:'100';

  var passed=0, failed=0, errors=0, totalFps=0, fpsCount=0;
  var rows=[];
  models.forEach(function(name){
    var r=S.benchRes[name];
    var status=r.error?'ERROR':(r.exit_code===0?'PASS':'FAIL');
    if(status==='PASS')passed++;
    else if(status==='ERROR')errors++;
    else failed++;
    var fps=parseFloat(r.fps)||0;
    if(fps){totalFps+=fps;fpsCount++;}
    rows.push({
      name:name, category:r.cat||r.category||'', status:status,
      fps:r.fps||'-', latency:r.latency?r.latency+'ms':'-',
      elapsed:r.elapsed_s?r.elapsed_s+'s':'-',
      exit_code:r.exit_code!=null?r.exit_code:'-'
    });
  });
  var avgFps=fpsCount?(totalFps/fpsCount).toFixed(1):'-';

  var ranked=rows.slice().sort(function(a,b){return (parseFloat(b.fps)||0)-(parseFloat(a.fps)||0);});

  var h='<!DOCTYPE html><html><head><meta charset="utf-8"><title>'+T('DX-APP Benchmark Report')+'</title>';
  h+='<style>';
  h+='*{margin:0;padding:0;box-sizing:border-box}';
  h+='body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#0b0f19;color:#cbd5e1;padding:40px}';
  h+='.rpt{max-width:1000px;margin:0 auto}';
  h+='.rpt h1{font-size:28px;margin-bottom:8px;color:#58A6FF}';
  h+='.rpt h2{font-size:18px;margin:24px 0 12px;color:#f0f6fc;border-bottom:1px solid #1e293b;padding-bottom:6px}';
  h+='.rpt-meta{font-size:12px;color:#94a3b8;margin-bottom:24px}';
  h+='.rpt-summary{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin-bottom:24px}';
  h+='.rpt-card{background:#111827;border:1px solid #1e293b;border-radius:8px;padding:16px;text-align:center}';
  h+='.rpt-card .val{font-size:28px;font-weight:700} .rpt-card .lbl{font-size:11px;color:#94a3b8;margin-top:4px;text-transform:uppercase}';
  h+='.rpt-card .val.green{color:#3FB950} .rpt-card .val.red{color:#F85149} .rpt-card .val.amber{color:#D29922} .rpt-card .val.blue{color:#58A6FF} .rpt-card .val.acc{color:#638CFF}';
  h+='table{width:100%;border-collapse:collapse;font-size:13px}';
  h+='th{text-align:left;padding:8px 12px;background:#111827;color:#94a3b8;font-size:11px;text-transform:uppercase;border-bottom:2px solid #1e293b}';
  h+='td{padding:8px 12px;border-bottom:1px solid #21262d}';
  h+='tr:hover{background:#111827}';
  h+='.badge{display:inline-block;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600}';
  h+='.b-pass{background:rgba(63,185,80,.15);color:#3FB950} .b-fail{background:rgba(248,81,73,.15);color:#F85149} .b-err{background:rgba(210,153,34,.15);color:#D29922}';
  h+='.rank{font-weight:700;color:#638CFF}';
  h+='.bar-container{height:20px;background:#21262d;border-radius:4px;overflow:hidden;min-width:60px}';
  h+='.bar-fill{height:100%;background:linear-gradient(90deg,#638CFF,#58A6FF);border-radius:4px;transition:width .3s}';
  h+='.footer{margin-top:32px;padding-top:16px;border-top:1px solid #1e293b;font-size:11px;color:#484f58;text-align:center}';
  h+='@media print{body{background:#fff;color:#1f2937} .rpt-card{border-color:#e5e7eb;background:#f9fafb} th{background:#f3f4f6;color:#6b7280} td{border-color:#e5e7eb} tr:hover{background:transparent}}';
  h+='</style></head><body><div class="rpt">';

  h+='<h1>'+T('📊 DX-APP Benchmark Report')+'</h1>';
  h+='<div class="rpt-meta">'+T('Generated: ')+esc(ts)+' | '+T('Language: ')+esc(lang)+' | '+T('Input: ')+esc(inputType)+' | '+T('Loop: ')+esc(loopCount)+'</div>';

  h+='<div class="rpt-summary">';
  h+='<div class="rpt-card"><div class="val blue">'+models.length+'</div><div class="lbl">'+T('Total Models')+'</div></div>';
  h+='<div class="rpt-card"><div class="val green">'+passed+'</div><div class="lbl">'+T('Passed')+'</div></div>';
  h+='<div class="rpt-card"><div class="val red">'+failed+'</div><div class="lbl">'+T('Failed')+'</div></div>';
  h+='<div class="rpt-card"><div class="val amber">'+errors+'</div><div class="lbl">'+T('Errors')+'</div></div>';
  h+='<div class="rpt-card"><div class="val acc">'+avgFps+'</div><div class="lbl">'+T('Avg FPS')+'</div></div>';
  h+='</div>';

  h+='<h2>'+T('🏆 Performance Ranking')+'</h2>';
  h+='<table><thead><tr><th>#</th><th>'+T('Model')+'</th><th>'+T('Category')+'</th><th>'+T('Status')+'</th><th>FPS</th><th>'+T('Latency')+'</th><th>'+T('Elapsed')+'</th><th>'+T('FPS Bar')+'</th></tr></thead><tbody>';
  var maxFps=ranked.length?Math.max.apply(null,ranked.map(function(r){return parseFloat(r.fps)||0})):1;
  ranked.forEach(function(r,i){
    var statusBadge=r.status==='PASS'?'<span class="badge b-pass">PASS</span>'
      :r.status==='ERROR'?'<span class="badge b-err">ERROR</span>'
      :'<span class="badge b-fail">FAIL</span>';
    var fpsVal=parseFloat(r.fps)||0;
    var barPct=maxFps>0?Math.round(fpsVal/maxFps*100):0;
    h+='<tr><td class="rank">'+(i+1)+'</td><td><strong>'+esc(r.name)+'</strong></td>';
    h+='<td>'+esc(r.category)+'</td><td>'+statusBadge+'</td>';
    h+='<td style="color:#638CFF;font-weight:600">'+esc(r.fps)+'</td>';
    h+='<td>'+esc(r.latency)+'</td><td>'+esc(r.elapsed)+'</td>';
    h+='<td><div class="bar-container"><div class="bar-fill" style="width:'+barPct+'%"></div></div></td></tr>';
  });
  h+='</tbody></table>';

  var cats={};
  rows.forEach(function(r){
    if(!cats[r.category])cats[r.category]={count:0,fps:0,fpsN:0,passed:0,failed:0,errors:0};
    cats[r.category].count++;
    var fp=parseFloat(r.fps)||0;
    if(fp){cats[r.category].fps+=fp;cats[r.category].fpsN++;}
    if(r.status==='PASS')cats[r.category].passed++;
    else if(r.status==='ERROR')cats[r.category].errors++;
    else cats[r.category].failed++;
  });
  h+='<h2>'+T('📂 Category Summary')+'</h2>';
  h+='<table><thead><tr><th>'+T('Category')+'</th><th>'+T('Models')+'</th><th>'+T('Passed')+'</th><th>'+T('Failed')+'</th><th>'+T('Errors')+'</th><th>'+T('Avg FPS')+'</th></tr></thead><tbody>';
  Object.keys(cats).sort().forEach(function(c){
    var d=cats[c];
    h+='<tr><td><strong>'+esc(c)+'</strong></td><td>'+d.count+'</td>';
    h+='<td style="color:#3FB950">'+d.passed+'</td><td style="color:#F85149">'+d.failed+'</td><td style="color:#D29922">'+d.errors+'</td>';
    h+='<td style="color:#638CFF">'+(d.fpsN?(d.fps/d.fpsN).toFixed(1):'-')+'</td></tr>';
  });
  h+='</tbody></table>';

  var latVals=[], fpsVals=[];
  models.forEach(function(name){
    var r=S.benchRes[name];
    var lat=parseFloat(r.latency)||0, fp=parseFloat(r.fps)||0;
    if(lat)latVals.push({name:name,val:lat});
    if(fp)fpsVals.push({name:name,val:fp});
  });
  if(latVals.length>1){
    latVals.sort(function(a,b){return a.val-b.val});
    var latMin=latVals[0], latMax=latVals[latVals.length-1];
    var latSum=latVals.reduce(function(s,v){return s+v.val},0);
    var latAvg=(latSum/latVals.length).toFixed(2);
    var latMed=latVals.length%2===0
      ?((latVals[latVals.length/2-1].val+latVals[latVals.length/2].val)/2).toFixed(2)
      :latVals[Math.floor(latVals.length/2)].val.toFixed(2);
    var latP95=latVals[Math.min(Math.floor(latVals.length*0.95),latVals.length-1)];
    h+='<h2>'+T('⚡ Latency Analysis')+'</h2>';
    h+='<div class="rpt-summary">';
    h+='<div class="rpt-card"><div class="val green">'+latMin.val+'ms</div><div class="lbl">'+T('Min')+' ('+esc(latMin.name)+')</div></div>';
    h+='<div class="rpt-card"><div class="val red">'+latMax.val+'ms</div><div class="lbl">'+T('Max')+' ('+esc(latMax.name)+')</div></div>';
    h+='<div class="rpt-card"><div class="val blue">'+latAvg+'ms</div><div class="lbl">'+T('Average')+'</div></div>';
    h+='<div class="rpt-card"><div class="val acc">'+latMed+'ms</div><div class="lbl">'+T('Median')+'</div></div>';
    h+='<div class="rpt-card"><div class="val" style="color:#D29922">'+latP95.val+'ms</div><div class="lbl">P95</div></div>';
    h+='</div>';
  }

  if(fpsVals.length>1&&latVals.length>1){
    var svgW=800,svgH=320,pad=50;
    var allFps=models.map(function(n){return parseFloat(S.benchRes[n].fps)||0}).filter(function(v){return v>0});
    var allLat=models.map(function(n){return parseFloat(S.benchRes[n].latency)||0}).filter(function(v){return v>0});
    if(allFps.length>1&&allLat.length>1){
      var fpsMin2=Math.min.apply(null,allFps)*0.9, fpsMax2=Math.max.apply(null,allFps)*1.1;
      var latMin2=Math.min.apply(null,allLat)*0.9, latMax2=Math.max.apply(null,allLat)*1.1;
      h+='<h2>'+T('📈 FPS vs Latency')+'</h2>';
      h+='<div style="overflow-x:auto"><svg width="'+svgW+'" height="'+svgH+'" style="background:#111827;border-radius:8px;border:1px solid #1e293b">';
      h+='<line x1="'+pad+'" y1="'+(svgH-pad)+'" x2="'+(svgW-20)+'" y2="'+(svgH-pad)+'" stroke="#1e293b" stroke-width="1"/>';
      h+='<line x1="'+pad+'" y1="20" x2="'+pad+'" y2="'+(svgH-pad)+'" stroke="#1e293b" stroke-width="1"/>';
      h+='<text x="'+(svgW/2)+'" y="'+(svgH-8)+'" text-anchor="middle" fill="#94a3b8" font-size="11">FPS →</text>';
      h+='<text x="14" y="'+(svgH/2)+'" text-anchor="middle" fill="#94a3b8" font-size="11" transform="rotate(-90,14,'+(svgH/2)+')">Latency (ms) →</text>';
      for(var gi=0;gi<=4;gi++){
        var gy=svgH-pad-(gi/4)*(svgH-pad-20);
        var gx=pad+(gi/4)*(svgW-pad-20);
        h+='<line x1="'+pad+'" y1="'+gy+'" x2="'+(svgW-20)+'" y2="'+gy+'" stroke="#21262d" stroke-width="0.5"/>';
        h+='<text x="'+(pad-4)+'" y="'+(gy+4)+'" text-anchor="end" fill="#484f58" font-size="9">'+(latMin2+(latMax2-latMin2)*gi/4).toFixed(0)+'</text>';
        h+='<text x="'+gx+'" y="'+(svgH-pad+14)+'" text-anchor="middle" fill="#484f58" font-size="9">'+(fpsMin2+(fpsMax2-fpsMin2)*gi/4).toFixed(0)+'</text>';
      }
      var colors=['#638CFF','#58A6FF','#fb923c','#bc8cff','#ff7b72','#79c0ff','#56d364','#e3b341','#ffa657','#d2a8ff'];
      models.forEach(function(name,mi){
        var r=S.benchRes[name];
        var fp=parseFloat(r.fps)||0, lt=parseFloat(r.latency)||0;
        if(!fp||!lt)return;
        var cx=pad+(fp-fpsMin2)/(fpsMax2-fpsMin2)*(svgW-pad-20);
        var cy=svgH-pad-(lt-latMin2)/(latMax2-latMin2)*(svgH-pad-20);
        var col=colors[mi%colors.length];
        h+='<circle cx="'+cx.toFixed(1)+'" cy="'+cy.toFixed(1)+'" r="6" fill="'+col+'" opacity="0.85" stroke="#0b0f19" stroke-width="1.5"/>';
        h+='<text x="'+(cx+9).toFixed(1)+'" y="'+(cy+4).toFixed(1)+'" fill="'+col+'" font-size="10" font-weight="600">'+esc(name.length>18?name.slice(0,17)+'…':name)+'</text>';
      });
      h+='</svg></div>';
    }
  }

  var hwData=[];
  models.forEach(function(name){
    var r=S.benchRes[name];
    if(!r.hw_after)return;
    var hw=r.hw_after;
    var item={name:name, cpu:hw.cpu_percent, mem:hw.mem_percent};
    if(hw.npus&&hw.npus[0]){
      item.temp=hw.npus[0].temp_C;
      item.freq=hw.npus[0].freq_MHz;
      item.power=hw.npus[0].power_est_mW;
    }
    hwData.push(item);
  });
  if(hwData.length){
    h+='<h2>'+T('🔧 Hardware Resources (Post-Run)')+'</h2>';
    h+='<table><thead><tr><th>Model</th><th>CPU %</th><th>RAM %</th>';
    var hasNpu=hwData.some(function(d){return d.temp!=null||d.freq!=null||d.power!=null});
    if(hasNpu)h+='<th>NPU Temp</th><th>NPU Clock</th><th>Power</th>';
    h+='</tr></thead><tbody>';
    var cpuSum=0,cpuN=0,memSum=0,memN=0,tempSum=0,tempN=0,powerSum=0,powerN=0;
    hwData.forEach(function(d){
      h+='<tr><td>'+esc(d.name)+'</td>';
      h+='<td>'+(d.cpu!=null?d.cpu+'%':'-')+'</td>';
      h+='<td>'+(d.mem!=null?d.mem+'%':'-')+'</td>';
      if(hasNpu){
        h+='<td>'+(d.temp!=null?d.temp+'°C':'-')+'</td>';
        h+='<td>'+(d.freq!=null?d.freq+'MHz':'-')+'</td>';
        h+='<td>'+(d.power!=null?d.power+'mW':'-')+'</td>';
      }
      h+='</tr>';
      if(d.cpu!=null){cpuSum+=d.cpu;cpuN++;}
      if(d.mem!=null){memSum+=d.mem;memN++;}
      if(d.temp!=null){tempSum+=d.temp;tempN++;}
      if(d.power!=null){powerSum+=d.power;powerN++;}
    });
    h+='<tr style="font-weight:700;border-top:2px solid #1e293b"><td>'+T('Average')+'</td>';
    h+='<td style="color:#58A6FF">'+(cpuN?(cpuSum/cpuN).toFixed(1)+'%':'-')+'</td>';
    h+='<td style="color:#58A6FF">'+(memN?(memSum/memN).toFixed(1)+'%':'-')+'</td>';
    if(hasNpu){
      h+='<td style="color:#fb923c">'+(tempN?(tempSum/tempN).toFixed(1)+'°C':'-')+'</td>';
      h+='<td>-</td>';
      h+='<td style="color:#D29922">'+(powerN?(powerSum/powerN).toFixed(1)+'mW':'-')+'</td>';
    }
    h+='</tr></tbody></table>';

    // Power Efficiency (FPS/Watt) if power data exists
    if(powerN>0){
      h+='<h2>'+T('🏅 Power Efficiency (FPS / Watt)')+'</h2>';
      var effRows=[];
      models.forEach(function(name){
        var r=S.benchRes[name];
        var fp=parseFloat(r.fps)||0;
        var hw2=r.hw_after;
        if(!fp||!hw2||!hw2.npus||!hw2.npus[0]||hw2.npus[0].power_est_mW==null)return;
        var watts=hw2.npus[0].power_est_mW/1000;
        if(watts>0)effRows.push({name:name,fps:fp,power:hw2.npus[0].power_est_mW,eff:(fp/watts).toFixed(2)});
      });
      if(effRows.length){
        effRows.sort(function(a,b){return parseFloat(b.eff)-parseFloat(a.eff)});
        h+='<table><thead><tr><th>#</th><th>Model</th><th>FPS</th><th>Power (mW)</th><th>FPS/W</th></tr></thead><tbody>';
        effRows.forEach(function(e,i){
          h+='<tr><td class="rank">'+(i+1)+'</td><td><strong>'+esc(e.name)+'</strong></td>';
          h+='<td>'+e.fps+'</td><td>'+e.power+'mW</td>';
          h+='<td style="color:#638CFF;font-weight:700">'+e.eff+'</td></tr>';
        });
        h+='</tbody></table>';
      }
    }
  }

  var imgModels=models.filter(function(n){return S.benchRes[n].result_image});
  if(imgModels.length){
    h+='<h2>'+T('🖼️ Result Gallery')+'</h2>';
    h+='<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px">';
    imgModels.forEach(function(name){
      var r=S.benchRes[name];
      h+='<div style="background:#111827;border:1px solid #1e293b;border-radius:8px;overflow:hidden">';
      h+='<img src="data:image/jpeg;base64,'+r.result_image+'" style="width:100%;height:160px;object-fit:cover"/>';
      h+='<div style="padding:8px 10px">';
      h+='<div style="font-weight:600;font-size:12px;margin-bottom:4px">'+esc(name)+'</div>';
      h+='<div style="font-size:11px;color:#94a3b8">'+esc(r.cat||'')+' · '+(r.fps||'-')+' FPS</div>';
      h+='</div></div>';
    });
    h+='</div>';
  }

  var errModels=models.filter(function(n){var r=S.benchRes[n];return !!r.error});
  if(errModels.length){
    h+='<h2>'+T('❌ Runtime Errors')+'</h2>';
    errModels.forEach(function(name){
      var r=S.benchRes[name];
      h+='<div style="background:rgba(248,81,73,.06);border:1px solid rgba(248,81,73,.25);border-radius:8px;padding:12px 16px;margin-bottom:8px">';
      h+='<div style="font-weight:700;margin-bottom:4px">'+esc(name)+'</div>';
      if(r.error)h+='<div style="color:#F85149;font-size:12px;margin-bottom:4px">'+esc(_benchErrorMessage(r))+'</div>';
      if(r.exit_code!=null)h+='<div style="font-size:11px;color:#94a3b8">Exit code: '+r.exit_code+'</div>';
      if(r.output){
        var lastLines=r.output.trim().split('\n').slice(-5).join('\n');
        h+='<details style="margin-top:6px"><summary style="cursor:pointer;font-size:11px;color:#94a3b8">'+T('Last 5 lines of output')+'</summary>';
        h+='<pre style="font-size:10px;color:#cbd5e1;background:#0b0f19;padding:8px;border-radius:4px;margin-top:4px;overflow-x:auto;white-space:pre-wrap">'+esc(lastLines)+'</pre></details>';
      }
      h+='</div>';
    });
  }
  var failModels=models.filter(function(n){var r=S.benchRes[n];return !r.error&&r.exit_code!=null&&r.exit_code!==0});
  if(failModels.length){
    h+='<h2>'+T('⚠️ Accuracy Failures')+'</h2>';
    failModels.forEach(function(name){
      var r=S.benchRes[name];
      h+='<div style="background:rgba(248,81,73,.06);border:1px solid rgba(248,81,73,.25);border-radius:8px;padding:12px 16px;margin-bottom:8px">';
      h+='<div style="font-weight:700;margin-bottom:4px">'+esc(name)+'</div>';
      if(r.exit_code!=null)h+='<div style="font-size:11px;color:#94a3b8">Exit code: '+r.exit_code+'</div>';
      if(r.output){
        var lastLines=r.output.trim().split('\n').slice(-5).join('\n');
        h+='<details style="margin-top:6px"><summary style="cursor:pointer;font-size:11px;color:#94a3b8">'+T('Last 5 lines of output')+'</summary>';
        h+='<pre style="font-size:10px;color:#cbd5e1;background:#0b0f19;padding:8px;border-radius:4px;margin-top:4px;overflow-x:auto;white-space:pre-wrap">'+esc(lastLines)+'</pre></details>';
      }
      h+='</div>';
    });
  }

  h+='<h2>'+T('🖥️ Environment')+'</h2>';
  h+='<table><tbody>';
  h+='<tr><td>'+T('Language')+'</td><td>'+esc(lang)+'</td></tr>';
  h+='<tr><td>'+T('Input Type')+'</td><td>'+esc(inputType)+'</td></tr>';
  h+='<tr><td>'+T('Loop Count')+'</td><td>'+esc(loopCount)+'</td></tr>';
  h+='<tr><td>'+T('Report Generated')+'</td><td>'+esc(ts)+'</td></tr>';
  h+='</tbody></table>';

  h+='<div class="footer">'+T('DX-APP Benchmark Report — Generated automatically by DX-APP GUI')+'</div>';
  h+='</div></body></html>';

  var blob=new Blob([h],{type:'text/html;charset=utf-8'});
  var a=document.createElement('a');
  a.href=URL.createObjectURL(blob);
  a.download='benchmark_report_'+new Date().toISOString().slice(0,10)+'.html';
  a.click();
  toast('📄 '+T('Benchmark report downloaded'),'ok');
}

if (typeof registerLangRefresher === 'function') {
  registerLangRefresher(function refreshBenchmarkPageLanguage() {
    if (document.querySelector('#page-bench.active') && typeof refreshBenchLanguage === 'function') refreshBenchLanguage();
  });
}
