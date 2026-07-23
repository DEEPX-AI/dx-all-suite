// DX Charts — 공유 차트 헬퍼 라이브러리
// dx_app/static/js/charts.js + dx_monitor/static/js/charts.js 통합

function _dxChartCssColor(token,fallback){
  if(typeof _cv==='function'){
    var value=_cv(token);
    if(value)return value;
  }
  return fallback;
}

function _dxChartWaterfallColors(){
  return[
    _dxChartCssColor('--info','#60a5fa'),
    _dxChartCssColor('--app-accent','#22d3ee'),
    _dxChartCssColor('--warning','#f59e0b'),
    _dxChartCssColor('--error','#ef4444'),
    _dxChartCssColor('--npu','#a78bfa')
  ];
}

function _chartFiniteValues(datasets){
  var values=[];
  datasets.forEach(function(ds){
    (ds.data||[]).forEach(function(v){
      if(typeof v==='number'&&Number.isFinite(v))values.push(v);
    });
  });
  return values;
}

function _prepareChartCanvas(canvas,resetInline){
  const ctx=canvas.getContext('2d');
  if(resetInline&&!canvas._dxChartSize){canvas.style.width='';canvas.style.height='';}
  const parent=canvas.parentElement;
  let W=parent.clientWidth||parent.offsetWidth||0;
  let H=parent.clientHeight||parent.offsetHeight||0;
  if(W<10||H<10){
    const pRect=parent.getBoundingClientRect();
    W=W||pRect.width;
    H=H||pRect.height;
  }
  if(W<10)W=300;
  if(H<10)H=200;
  const pixelW=W*2,pixelH=H*2;
  if(canvas.width!==pixelW||canvas.height!==pixelH){
    canvas.width=pixelW;canvas.height=pixelH;
    canvas.style.width=W+'px';canvas.style.height=H+'px';
    canvas._dxChartSize={W:W,H:H};
  }
  ctx.setTransform(1,0,0,1,0,0);
  ctx.scale(2,2);
  return{ctx:ctx,W:W,H:H};
}

function drawLineChart(canvas,datasets,opts){
  if(!opts)opts={};
  var prepared=_prepareChartCanvas(canvas,true);
  var ctx=prepared.ctx;
  var W=prepared.W;
  var H=prepared.H;
  var pad={t:20,r:16,b:38,l:52};
  var cw=W-pad.l-pad.r, ch=H-pad.t-pad.b;
  ctx.fillStyle=_dxChartCssColor('--bg-2','#0f172a');ctx.fillRect(0,0,W,H);
  var finiteValues=_chartFiniteValues(datasets);
  var hasData=datasets.length>0&&datasets.some(function(d){return _chartFiniteValues([d]).length>=2});
  var mn=0,mx=1,rng=1;
  if(hasData){
    var allV=finiteValues;
    mn=opts.min!=null?opts.min:Math.min.apply(null,allV);
    mx=opts.max!=null?opts.max:Math.max.apply(null,allV);
    if(mn===mx){mn-=1;mx+=1}
    rng=mx-mn;
  }
  ctx.strokeStyle='rgba(148,163,184,.12)';ctx.lineWidth=0.5;
  for(var i=0;i<=4;i++){
    var y=pad.t+ch*(i/4);
    ctx.beginPath();ctx.moveTo(pad.l,y);ctx.lineTo(pad.l+cw,y);ctx.stroke();
    ctx.fillStyle=_dxChartCssColor('--text-3','#94a3b8');ctx.font='10px sans-serif';ctx.textAlign='right';
    ctx.fillText(hasData?(mx-rng*(i/4)).toFixed(1):'--',pad.l-6,y+3);
  }
  if(!hasData){
    ctx.fillStyle='rgba(139,148,158,0.35)';ctx.font='11px sans-serif';ctx.textAlign='center';
    var emptyText=opts.emptyText||(typeof T==='function'?T('Waiting for data…'):'');
    ctx.fillText(emptyText,W/2,H/2);
    if(opts.label){ctx.fillStyle=_dxChartCssColor('--text-3','#94a3b8');ctx.textAlign='left';ctx.fillText(opts.label,pad.l,H-4);}
    return;
  }
  datasets.forEach(function(ds){
    if(_chartFiniteValues([ds]).length<2)return;
    ctx.strokeStyle=ds.color||_dxChartCssColor('--app-accent','#22d3ee');ctx.lineWidth=1.5;ctx.beginPath();
    var started=false;
    ds.data.forEach(function(v,i){
      if(v==null||!Number.isFinite(v)){started=false;return;}
      var x=pad.l+(i/(ds.data.length-1))*cw;
      var y2=pad.t+ch*(1-(v-mn)/rng);
      if(!started){ctx.moveTo(x,y2);started=true;}else{ctx.lineTo(x,y2);}
    });
    ctx.stroke();
    ctx.strokeStyle=ds.color||_dxChartCssColor('--app-accent','#22d3ee');ctx.globalAlpha=0.15;ctx.lineWidth=4;ctx.stroke();ctx.globalAlpha=1;ctx.lineWidth=1.5;
  });
  if(opts.thresholds&&hasData){
    opts.thresholds.forEach(function(th){
      if(th.value==null||th.value<mn||th.value>mx)return;
      var y=pad.t+ch*(1-(th.value-mn)/rng);
      ctx.save();
      ctx.strokeStyle=th.color||'rgba(248,81,73,.6)';
      ctx.lineWidth=1;
      ctx.setLineDash([6,4]);
      ctx.beginPath();ctx.moveTo(pad.l,y);ctx.lineTo(pad.l+cw,y);ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle=th.color||'rgba(248,81,73,.8)';
      ctx.font='9px sans-serif';ctx.textAlign='right';
      ctx.fillText(th.label||th.value.toString(),pad.l+cw,y-3);
      ctx.restore();
    });
  }
  if(opts.label){ctx.fillStyle=_dxChartCssColor('--text-2','#cbd5e1');ctx.font='bold 10px sans-serif';ctx.textAlign='left';ctx.fillText(opts.label,pad.l,pad.t-6)}
  if(opts.timeLabels&&opts.timeLabels.length){
    ctx.fillStyle=_dxChartCssColor('--text-3','#94a3b8');ctx.font='9px sans-serif';ctx.textAlign='center';
    var len=datasets[0]?datasets[0].data.length:opts.timeLabels.length;
    var lastDrawnX=-999;
    opts.timeLabels.forEach(function(lbl,i){
      if(!lbl)return;
      var x=pad.l+(i/(Math.max(len-1,1)))*cw;
      if(x-lastDrawnX<60)return;
      ctx.fillText(lbl,x,H-pad.b+14);
      lastDrawnX=x;
    });
  }
}

function drawBarChart(canvas,items,opts){
  if(!opts)opts={};
  var prepared=_prepareChartCanvas(canvas,false);
  var ctx=prepared.ctx;
  var W=prepared.W;
  var H=prepared.H;
  var pad={t:16,r:16,b:60,l:48};
  var cw=W-pad.l-pad.r, ch=H-pad.t-pad.b;
  ctx.fillStyle=_dxChartCssColor('--bg-2','#0f172a');ctx.fillRect(0,0,W,H);
  if(!items.length){
    ctx.fillStyle='rgba(139,148,158,0.35)';ctx.font='11px sans-serif';ctx.textAlign='center';
    var emptyText=opts.emptyText||(typeof T==='function'?T('No run data yet'):'');
    ctx.fillText(emptyText,W/2,H/2);
    return;
  }
  var mx=Math.max.apply(null,items.map(function(i){return i.val}))*1.1||1;
  ctx.fillStyle=_dxChartCssColor('--bg-2','#0f172a');ctx.fillRect(0,0,W,H);
  var bw=Math.min(30,cw/items.length-4);
  items.forEach(function(it,i){
    var x=pad.l+(i+0.5)*(cw/items.length)-bw/2;
    var bh=(it.val/mx)*ch;
    var y=pad.t+ch-bh;
    var grad=ctx.createLinearGradient(x,y,x,y+bh);
    grad.addColorStop(0,it.color||_dxChartCssColor('--app-accent','#22d3ee'));grad.addColorStop(1,_dxChartCssColor('--accent-dim','#0e7490'));
    ctx.fillStyle=grad;ctx.beginPath();
    ctx.roundRect(x,y,bw,bh,3);ctx.fill();
    ctx.fillStyle=_dxChartCssColor('--text-1','#f8fafc');ctx.font='bold 10px sans-serif';ctx.textAlign='center';
    ctx.fillText(it.val.toFixed(1),x+bw/2,y-4);
    ctx.fillStyle=_dxChartCssColor('--text-3','#94a3b8');ctx.font='9px sans-serif';
    var lbl=it.label.length>16?it.label.slice(0,15)+'\u2026':it.label;
    ctx.save();ctx.translate(x+bw/2,pad.t+ch+4);ctx.rotate(-0.6);ctx.textAlign='left';
    ctx.fillText(lbl,0,0);ctx.restore();
  });
}

function drawGauge(canvas,pct,color){
  var ctx=canvas.getContext('2d');
  var w=canvas.width,h=canvas.height;
  ctx.clearRect(0,0,w,h);
  var cx=w/2,cy=h/2+10,r=45;
  var start=0.75*Math.PI,end=2.25*Math.PI;
  ctx.beginPath();ctx.arc(cx,cy,r,start,end);ctx.strokeStyle=_dxChartCssColor('--bg-3','#1e293b');ctx.lineWidth=10;ctx.lineCap='round';ctx.stroke();
  var angle=start+(end-start)*Math.min(pct/100,1);
  ctx.beginPath();ctx.arc(cx,cy,r,start,angle);ctx.strokeStyle=color||_dxChartCssColor('--app-accent','#22d3ee');ctx.lineWidth=10;ctx.lineCap='round';ctx.stroke();
  ctx.beginPath();ctx.arc(cx,cy,r,start,angle);ctx.strokeStyle=color||_dxChartCssColor('--app-accent','#22d3ee');ctx.globalAlpha=0.2;ctx.lineWidth=16;ctx.stroke();ctx.globalAlpha=1;
}

function renderWaterfall(perf){
  if(!perf||!perf.pipeline||!perf.pipeline.length)return'';
  var total=perf.total_pipeline_ms||perf.pipeline.reduce(function(s,p){return s+p.latency_ms},0);
  var wfColors=_dxChartWaterfallColors();
  var h='<div class="wf-bar">';
  perf.pipeline.forEach(function(p,i){
    var pct=total>0?(p.latency_ms/total*100):20;
    var bg=wfColors[i%wfColors.length];
    var bot=p.step===perf.bottleneck?' wf-bottleneck':'';
    h+='<div class="wf-seg'+bot+'" style="width:'+Math.max(pct,5)+'%;background:'+bg+'" title="'+p.step+': '+p.latency_ms+'ms">'+p.latency_ms.toFixed(1)+'</div>';
  });
  h+='</div><div class="wf-legend">';
  perf.pipeline.forEach(function(p,i){
    var bg=wfColors[i%wfColors.length];
    var bot=p.step===perf.bottleneck;
    var pct=total>0?(p.latency_ms/total*100).toFixed(0):'--';
    h+='<span><span class="wf-dot'+(bot?' wf-bottleneck':'')+'" style="background:'+bg+'"></span>'+p.step+' '+p.latency_ms.toFixed(1)+'ms ('+pct+'%)'+(bot?' <span class="wf-bot-tag">▲ bottleneck</span>':'')+'</span>';
  });
  h+='</div>';return h;
}

function renderPerfCards(res){
  var p=res.perf||{};var h='<div class="perf-grid">';
  if(p.overall_fps)h+='<div class="perf-item"><div class="pv">'+p.overall_fps+'</div><div class="pl">Overall FPS</div></div>';
  if(p.inference_latency)h+='<div class="perf-item"><div class="pv">'+p.inference_latency+'</div><div class="pl">Inference ms</div></div>';
  if(p.total_frames)h+='<div class="perf-item"><div class="pv">'+p.total_frames+'</div><div class="pl">Frames</div></div>';
  if(p.total_time)h+='<div class="perf-item"><div class="pv">'+p.total_time+'s</div><div class="pl">Total Time</div></div>';
  var exitColor=res.exit_code===0?'var(--success)':'var(--error)';
  var exitIcon=res.exit_code===0?'\u2705':'\u274c';
  h+='<div class="perf-item"><div class="pv" style="color:'+exitColor+'">'+exitIcon+'</div><div class="pl">Exit '+res.exit_code+'</div></div>';
  h+='</div>';
  h+=renderWaterfall(p);
  return h;
}

function renderPipelineTable(perf){
  if(!perf||!perf.pipeline||!perf.pipeline.length)return'';
  var h='<table class="perf-table"><thead><tr><th>Pipeline Step</th><th>Avg Latency</th><th>Throughput</th></tr></thead><tbody>';
  perf.pipeline.forEach(function(p){
    var bot=p.step===perf.bottleneck;
    h+='<tr'+(bot?' class="pt-bot"':'')+'>';
    h+='<td>'+p.step+'</td>';
    h+='<td>'+p.latency_ms.toFixed(2)+' ms</td>';
    h+='<td>'+p.throughput_fps.toFixed(1)+' FPS</td>';
    h+='</tr>';
  });
  h+='</tbody></table>';
  return h;
}

function renderSparkline(values,w,h){
  if(!values||values.length<2)return'';
  var min=Math.min.apply(null,values),max=Math.max.apply(null,values);
  var range=max-min||0.001;
  var pad=4;
  var pts=values.map(function(v,i){
    var x=pad+i*((w-2*pad)/(values.length-1));
    var y=(h-pad)-((v-min)/range*(h-2*pad));
    return x.toFixed(1)+','+y.toFixed(1);
  }).join(' ');
  var last=values[values.length-1];
  var lx=w-pad;
  var ly=(h-pad)-((last-min)/range*(h-2*pad));
  return '<svg viewBox="0 0 '+w+' '+h+'" width="100%" height="'+h+'" preserveAspectRatio="none" style="display:block"><polyline points="'+pts+'" fill="none" stroke="var(--accent)" stroke-width="1.5" stroke-linejoin="round"/><circle cx="'+lx.toFixed(1)+'" cy="'+ly.toFixed(1)+'" r="2.5" fill="var(--accent)"/></svg>';
}

function renderDetSummary(ds){
  if(!ds)return'';
  function _e(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
  var entries=Object.entries(ds).sort(function(a,b){return b[1].count-a[1].count});
  if(!entries.length){
    var noDetText=typeof T==='function'?T('No detections recorded.'):'No detections recorded.';
    return'<p style="color:var(--text-3);font-size:12px">'+noDetText+'</p>';
  }
  var clsLabel=typeof T==='function'?T('Class'):'Class';
  var detLabel=typeof T==='function'?T('Detections'):'Detections';
  var confLabel=typeof T==='function'?T('Avg Conf'):'Avg Conf';
  var h='<table class="perf-table"><thead><tr><th>'+clsLabel+'</th><th style="text-align:right">'+detLabel+'</th><th style="text-align:right">'+confLabel+'</th></tr></thead><tbody>';
  entries.forEach(function(e){
    var ca=(e[1].conf_avg||0)*100;
    h+='<tr><td>'+_e(e[0])+'</td><td>'+e[1].count+'</td><td>'+ca.toFixed(1)+'%</td></tr>';
  });
  return h+'</tbody></table>';
}

function renderTaskSummary(tag,summary){
  if(!tag||!summary)return'';
  function _e(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
  function _t(en,ko){return typeof T==='function'?T(en,ko):en;}
  var h='';
  if(tag==='DET'||tag==='ISEG'||tag==='OBB'||tag==='CLS'||tag==='HAND'){
    var entries=Object.entries(summary).sort(function(a,b){return(b[1].count||0)-(a[1].count||0)});
    if(!entries.length)return'<p style="color:var(--text-3);font-size:12px">'+_t('No results recorded.','기록된 결과가 없습니다.')+'</p>';
    var lbl=tag==='HAND'?_t('Handedness','손잡이'):_t('Class','클래스');
    h='<table class="perf-table"><thead><tr><th>'+lbl+'</th><th style="text-align:right">'+_t('Count','개수')+'</th><th style="text-align:right">'+_t('Avg Conf','평균 신뢰도')+'</th></tr></thead><tbody>';
    entries.forEach(function(e){
      var ca=(e[1].conf_avg||0)*100;
      h+='<tr><td>'+_e(e[0])+'</td><td style="text-align:right">'+(e[1].count||0)+'</td><td style="text-align:right">'+ca.toFixed(1)+'%</td></tr>';
    });
    h+='</tbody></table>';
  }
  else if(tag==='SEG'){
    var entries=Object.entries(summary).sort(function(a,b){return(b[1].avg_pct||0)-(a[1].avg_pct||0)});
    if(!entries.length)return'<p style="color:var(--text-3);font-size:12px">'+_t('No segmentation data.','분할 데이터가 없습니다.')+'</p>';
    h='<table class="perf-table"><thead><tr><th>'+_t('Class','클래스')+'</th><th style="text-align:right">'+_t('Avg Pixel %','평균 픽셀 %')+'</th></tr></thead><tbody>';
    entries.forEach(function(e){
      h+='<tr><td>'+_e(e[0])+'</td><td style="text-align:right">'+(e[1].avg_pct||0).toFixed(2)+'%</td></tr>';
    });
    h+='</tbody></table>';
  }
  else if(tag==='DEPTH'){
    h='<div class="perf-grid">';
    h+='<div class="pcard"><div class="pv txt-acc">'+(summary.mean||0).toFixed(2)+'</div><div class="pk">'+_t('Mean Depth','평균 깊이')+'</div></div>';
    h+='<div class="pcard"><div class="pv">'+(summary.min||0).toFixed(2)+'</div><div class="pk">'+_t('Min Depth','최소 깊이')+'</div></div>';
    h+='<div class="pcard"><div class="pv">'+(summary.max||0).toFixed(2)+'</div><div class="pk">'+_t('Max Depth','최대 깊이')+'</div></div>';
    if(summary.frames)h+='<div class="pcard"><div class="pv">'+summary.frames+'</div><div class="pk">'+_t('Frames','프레임')+'</div></div>';
    h+='</div>';
  }
  else if(tag==='POSE'||tag==='FACE'){
    var _totLabel=tag==='POSE'?_t('Total Persons','총 인원'):_t('Total Faces','총 얼굴');
    h='<div class="perf-grid">';
    h+='<div class="pcard"><div class="pv txt-acc">'+(summary.total_detections||0)+'</div><div class="pk">'+_totLabel+'</div></div>';
    h+='<div class="pcard"><div class="pv">'+(summary.avg_per_frame||0).toFixed(1)+'</div><div class="pk">'+_t('Avg/Frame','평균/프레임')+'</div></div>';
    if(summary.frames)h+='<div class="pcard"><div class="pv">'+summary.frames+'</div><div class="pk">'+_t('Frames','프레임')+'</div></div>';
    h+='</div>';
  }
  else if(tag==='ALIGN'){
    h='<div class="perf-grid">';
    h+='<div class="pcard"><div class="pv txt-acc">'+(summary.avg_yaw||0).toFixed(1)+'°</div><div class="pk">'+_t('Avg Yaw','평균 Yaw')+'</div></div>';
    h+='<div class="pcard"><div class="pv">'+(summary.avg_pitch||0).toFixed(1)+'°</div><div class="pk">'+_t('Avg Pitch','평균 Pitch')+'</div></div>';
    h+='<div class="pcard"><div class="pv">'+(summary.avg_roll||0).toFixed(1)+'°</div><div class="pk">'+_t('Avg Roll','평균 Roll')+'</div></div>';
    if(summary.frames)h+='<div class="pcard"><div class="pv">'+summary.frames+'</div><div class="pk">'+_t('Frames','프레임')+'</div></div>';
    h+='</div>';
  }
  return h;
}

if(typeof window!=='undefined'){
  window.drawLineChart=drawLineChart;
  window.drawBarChart=drawBarChart;
  window.drawGauge=drawGauge;
  window.renderWaterfall=renderWaterfall;
  window.renderPerfCards=renderPerfCards;
  window.renderPipelineTable=renderPipelineTable;
  window.renderSparkline=renderSparkline;
  window.renderDetSummary=renderDetSummary;
  window.renderTaskSummary=renderTaskSummary;
  window._prepareChartCanvas=_prepareChartCanvas;
}
