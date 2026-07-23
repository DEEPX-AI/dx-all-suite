

function _updateMockBanner(){
  var el=$('mock-banner');
  if(!el)return;
  if(S.isMock){
    el.textContent='⚠ '+statusLabel('Mock Mode');
    el.style.display='inline';
  }else{
    el.textContent='';
    el.style.display='none';
  }
}

async function refreshDash(){
  const [hw,si]=await Promise.all([api('/api/hw_status'),api('/api/system_info')]);
  S.lastHW=hw;
  S.lastSystemInfo=si;
  S.cpuCores=si.cpu_cores||4;
  S.thresholds=si.thresholds||{};
  S.isMock=!!hw.mock;
  _updateMockBanner();
  renderStatusBar(hw);
  renderNPUTopo(hw);
  renderSysInfo(si);
  requestAnimationFrame(drawCharts);
}

function _finiteMetric(value){
  if(value==null||value==='')return null;
  var num=Number(value);
  return Number.isFinite(num)?num:null;
}

function _normalizeDramPct(value){
  var num=_finiteMetric(value);
  if(num==null||num<0)return null;
  return +num.toFixed(1);
}

function _formatDramPct(value){
  return value==null?T('N/A'):value.toFixed(1)+'%';
}

function _seriesValue(value){
  return _finiteMetric(value);
}

function renderStatusBar(hw){
  var npus=hw.npus||[];
  var h='';
  // NPU별 온도 카드
  npus.forEach(function(n, idx){
    // F-15: cores==0 means every temperature channel returned the invalid sentinel
    // (e.g. -32768). Do NOT render that as "0.0°C" with an OK/green badge — a dead
    // sensor is not a healthy 0°C. Show a no-data state instead.
    var hasTemp=(n.cores||0)>0 && (n.temperatures||[]).length>0;
    var st=hasTemp?getStatus('npu_temp',n.temp_avg||0):'none';
    var valStr=hasTemp?(n.temp_avg||0).toFixed(1)+'°C':statusLabel('No data available');
    h+='<div class="status-card '+statusClass(st)+'" data-help-id="status-npu-'+idx+'">'
      +'<span class="sc-badge">'+statusEmoji(st)+'</span>'
      +'<span class="sc-label">NPU '+n.id+'</span>'
      +'<span class="sc-value">'+valStr+'</span>'
      +(n.mock?'<span class="sc-mock">('+statusLabel('Mock')+')</span>':'')
      +'</div>';
  });
  // DRAM worst-case
  if(npus.length){
    var dramValues=npus.map(function(n){return _normalizeDramPct(n.dram_pct)}).filter(function(v){return v!=null});
    var worstDram=dramValues.length?Math.max.apply(null,dramValues):null;
    var dSt=worstDram==null?'none':getStatus('npu_dram',worstDram);
    h+='<div class="status-card '+statusClass(dSt)+'" data-help-id="status-dram"><span class="sc-badge">'+statusEmoji(dSt)+'</span><span class="sc-label">'+statusLabel('DRAM')+'</span><span class="sc-value">'+_formatDramPct(worstDram)+'</span></div>';
    // Util worst-case (임계치 없음)
    var worstUtil=Math.max.apply(null,npus.map(function(n){var u=n.utilization||[];return u.length?u.reduce(function(a,b){return a+b},0)/u.length:0}));
    h+='<div class="status-card" data-help-id="status-util"><span class="sc-label">'+statusLabel('Util')+'</span><span class="sc-value">'+worstUtil.toFixed(1)+'%</span></div>';
    // Volt worst-case (임계치 없음)
    var worstVolt=Math.max.apply(null,npus.map(function(n){return n.voltage_avg||0}));
    h+='<div class="status-card" data-help-id="status-voltage"><span class="sc-label">'+statusLabel('Voltage')+'</span><span class="sc-value">'+worstVolt.toFixed(0)+' mV</span></div>';
    // Clock worst-case (임계치 없음) — Math.min: 최저 클럭 NPU가 병목이므로 min 사용
    var worstClock=Math.min.apply(null,npus.map(function(n){return n.clock_avg||0}));
    h+='<div class="status-card" data-help-id="status-clock"><span class="sc-label">'+statusLabel('Clock')+'</span><span class="sc-value">'+worstClock.toFixed(0)+' MHz</span></div>';
  }
  var cpuSt=getStatus('cpu_load',hw.cpu_load||0);
  h+='<div class="status-card '+statusClass(cpuSt)+'" data-help-id="status-cpu"><span class="sc-badge">'+statusEmoji(cpuSt)+'</span><span class="sc-label">CPU</span><span class="sc-value">'+(hw.cpu_load||0).toFixed(2)+'</span></div>';
  var memSt=getStatus('memory',hw.mem_pct||0);
  h+='<div class="status-card '+statusClass(memSt)+'" data-help-id="status-memory"><span class="sc-badge">'+statusEmoji(memSt)+'</span><span class="sc-label">'+statusLabel('Memory')+'</span><span class="sc-value">'+(hw.mem_pct||0).toFixed(1)+'%</span></div>';
  $('status-bar').innerHTML=h;
}


var _sseFallbackTimer=null;

function _isMonitorVisible(){
  return typeof document==='undefined'||!document.hidden;
}

function _hwStatusSignature(hw){
  var npus=(hw.npus||[]).map(function(n){
    var util=n.utilization||[];
    var dram=_normalizeDramPct(n.dram_pct);
    return[
      n.id,
      +(n.temp_avg||0).toFixed(1),
      dram==null?'na':dram.toFixed(1),
      +(util.length?util.reduce(function(a,b){return a+b},0)/util.length:0).toFixed(1),
      +(n.voltage_avg||0).toFixed(0),
      +(n.clock_avg||0).toFixed(0),
      !!n.mock
    ].join(':');
  }).join('|');
  var lang=(typeof getLocale==='function')?getLocale():'';
  return [lang,+(hw.cpu_load||0).toFixed(2),+(hw.mem_pct||0).toFixed(1),npus].join('||');
}

function _applyHWData(d){
  var npus=d.npus||[];
  S.isMock=!!d.mock;
  S.lastHW=d;
  _updateMockBanner();
  // 상태 바 업데이트
  var statusSig=_hwStatusSignature(d);
  if (statusSig !== S._lastStatusSig){
    S._lastStatusSig=statusSig;
    renderStatusBar(d);
  }
  // NPU 토폴로지 (5초마다)
  var now=Date.now();
  if(!_applyHWData._lastTopo||now-_applyHWData._lastTopo>5000){
    _applyHWData._lastTopo=now;
    renderNPUTopo(d);
  }
  // 새 데이터 구조로 push
  var entry={t:now,npus:[],system:{}};
  npus.forEach(function(n){
    var u=n.utilization||[];
    entry.npus.push({
      temp:+(n.temp_avg||0).toFixed(1),
      volt:+(n.voltage_avg||0).toFixed(0),
      clock:+(n.clock_avg||0).toFixed(0),
      dram:_normalizeDramPct(n.dram_pct),
      util:u.length?+(u.reduce(function(a,b){return a+b},0)/u.length).toFixed(1):0,
      temps:(n.temperatures||[]).map(function(t){return+t.toFixed(1)})
    });
  });
  entry.system={
    cpu:+(d.cpu_load||0).toFixed(2),
    mem:+(d.mem_pct||0),
    cpu_cores:d.cpu_cores_pct||[]
  };
  S.rtData.push(entry);
  if(S.rtData.length>RT_MAX)S.rtData.shift();
  requestAnimationFrame(drawCharts);
}

function _startHWPoll(){
  if(_sseFallbackTimer)return;
  _sseFallbackTimer=setInterval(async function(){
    if (!_isMonitorVisible()) return;
    try{var d=await api('/api/hw_status');if(d&&!d.error)_applyHWData(d);}catch(e){}
  },3000);
}

function _setSseStatus(status){
  var el=$('sse-status');
  if(!el)return;
  if(status==='degraded'){
    el.textContent='⚠ Polling';
    el.className='sse-status degraded';
    el.style.display='';
  }else{
    el.textContent='';
    el.className='sse-status';
    el.style.display='none';
  }
}

function startSSE(){
  if(S.sseSource)S.sseSource.close();
  var connected=false;
  try{
    S.sseSource=new EventSource('/api/hw_stream');
    var sseTimeout=setTimeout(function(){if(!connected){S.sseSource.close();_startHWPoll();setTimeout(startSSE,5000);}},6000);
    S.sseSource.onmessage=function(e){
      try{
        if(!connected){connected=true;clearTimeout(sseTimeout);_setSseStatus('live');if(_sseFallbackTimer){clearInterval(_sseFallbackTimer);_sseFallbackTimer=null;}}
        _applyHWData(JSON.parse(e.data));
      }catch(ex){console.error('[DX Monitor SSE]',ex);}
    };
    S.sseSource.onerror=function(){S.sseSource.close();clearTimeout(sseTimeout);_setSseStatus('degraded');_startHWPoll();setTimeout(startSSE,5000)};
  }catch(e){_startHWPoll();setTimeout(startSSE,5000);}
}


var RT_PTS={'rt':40,'5m':200,'15m':600,'30m':1200,'1h':2400,'all':RT_MAX};

function _sliceData(range){
  var max=RT_PTS[range]||40;
  return S.rtData.length<=max?S.rtData:S.rtData.slice(-max);
}

function _timeLabels(data){
  if(!data.length)return[];
  var labels=new Array(data.length).fill('');
  var step=Math.max(1,Math.floor(data.length/6));
  for(var i=0;i<data.length;i+=step){
    labels[i]=formatTime(data[i].t);
  }
  if(data.length>1){labels[data.length-1]=formatTime(data[data.length-1].t);}
  return labels;
}

function _thresholdsFor(key){
  var thKey=CHART_THRESHOLD_MAP[key];
  if(!thKey)return[];
  var th=S.thresholds[thKey];
  if(!th||!th.warn)return[];
  return[
    {value:th.warn,color:'rgba(210,153,34,.6)',label:th.warn+''+(th.unit||'')+' ⚠️'},
    {value:th.crit,color:'rgba(248,81,73,.6)',label:th.crit+''+(th.unit||'')+' 🔴'}
  ];
}

var CHART_CFG={
  temp:{labelKey:'temp',color:_cv('--error'),npuKey:'temp'},
  volt:{labelKey:'volt',color:_cv('--warning'),npuKey:'volt'},
  clock:{labelKey:'clock',color:_cv('--info'),npuKey:'clock'},
  dram:{labelKey:'dram',color:'#e879f9',npuKey:'dram'},
  util:{labelKey:'util',color:_cv('--info'),npuKey:'util'},
  ctemp:{labelKey:'ctemp',color:_cv('--warning'),npuKey:'temps',multi:true},
  cpu:{labelKey:'cpu',color:_cv('--npu'),sysKey:'cpu'},
  mem:{labelKey:'mem',color:_cv('--app-accent'),sysKey:'mem'},
  cpucores:{labelKey:'cpucores',color:_cv('--emerald'),sysKey:'cpu_cores',multi:true}
};

var CORE_COLORS=[_cv('--error'),_cv('--warning'),_cv('--info'),_cv('--success')];

function _extractSeries(data,cfg,npuIdx){
  if(cfg.sysKey){
    if(cfg.multi){
      var nSeries=Math.max.apply(null,data.map(function(d){return(d.system[cfg.sysKey]||[]).length}))||1;
      return Array.from({length:nSeries},function(_,i){return{
        data:data.map(function(d){return _seriesValue((d.system[cfg.sysKey]||[])[i])}),
        color:'hsl('+(i*360/Math.max(nSeries,1))+',70%,60%)'
      };});
    }
    return[{data:data.map(function(d){return _seriesValue(d.system[cfg.sysKey])}),color:cfg.color}];
  }
  if(cfg.multi){
    var nSeries2=Math.max.apply(null,data.map(function(d){var n=d.npus[npuIdx];return n?(n[cfg.npuKey]||[]).length:0}))||1;
    return Array.from({length:nSeries2},function(_,i){return{
      data:data.map(function(d){var n=d.npus[npuIdx];return n?_seriesValue((n[cfg.npuKey]||[])[i]):null}),
      color:CORE_COLORS[i%CORE_COLORS.length]
    };});
  }
  return[{data:data.map(function(d){var n=d.npus[npuIdx];return n?_seriesValue(n[cfg.npuKey]):null}),color:cfg.color}];
}

function _latestNpuVal(cfg,npuIdx){
  if(!S.rtData.length)return 0;
  var last=S.rtData[S.rtData.length-1];
  var n=last.npus[npuIdx];
  if(!n)return 0;
  if(cfg.multi){
    var arr=(n[cfg.npuKey]||[]).map(_seriesValue).filter(function(v){return v!=null});
    return arr.length?Math.max.apply(null,arr):null;
  }
  return _seriesValue(n[cfg.npuKey]);
}

function _latestSysVal(cfg){
  if(!S.rtData.length)return 0;
  var last=S.rtData[S.rtData.length-1];
  if(cfg.multi){
    var arr=(last.system[cfg.sysKey]||[]).map(_seriesValue).filter(function(v){return v!=null});
    return arr.length?Math.max.apply(null,arr):null;
  }
  return _seriesValue(last.system[cfg.sysKey]);
}

function drawCharts(){
  var mode=S.chartMode;
  var data=_sliceData(S.rtView);
  var tl=_timeLabels(data);
  var area=$('chart-area');
  if(!area)return;
  var npuCount=S.rtData.length?(S.rtData[S.rtData.length-1].npus||[]).length:0;

  if(mode==='all'){
    _drawAllMode(area,data,tl,npuCount);
  }else{
    _drawSingleMode(area,data,tl,npuCount,mode);
  }
}

function _drawSingleMode(area,data,tl,npuCount,mode){
  var cfg=CHART_CFG[mode];
  if(!cfg){area.innerHTML='';S._chartLayoutKey='';return;}
  var unitLabel=metricLabel(cfg.labelKey);
  var isNpu=NPU_CHART_KEYS.indexOf(mode)>=0;
  var isSys=SYS_CHART_KEYS.indexOf(mode)>=0;
  var th=_thresholdsFor(mode);
  var thKey=CHART_THRESHOLD_MAP[mode]||'';
  var rows=[];

  if(isNpu){
    for(var i=0;i<npuCount;i++){
      var val=_latestNpuVal(cfg,i);
      var st=val==null?'none':(thKey?getStatus(thKey,val):'none');
      rows.push({id:'npu-'+i,label:'NPU '+i,val:val,status:st,
        datasets:_extractSeries(data,cfg,i),mock:S.isMock,unit:unitLabel});
    }
  }else if(isSys){
    var val2=_latestSysVal(cfg);
    var st2=val2==null?'none':(thKey?getStatus(thKey,val2):'none');
    rows.push({id:'sys',label:T('System'),val:val2,status:st2,
      datasets:_extractSeries(data,cfg,0),mock:false,unit:unitLabel});
  }

  var layoutKey='single:'+mode+':'+npuCount+':'+S.isMock;
  if(S._chartLayoutKey!==layoutKey){
    S._chartLayoutKey=layoutKey;
    var h='';
    rows.forEach(function(r,idx){
      var canvasId='chart-single-'+idx;
      h+='<div class="chart-row" data-help-id="chart-row-'+esc(r.id)+'">'
        +'<div class="chart-row-label '+statusClass(r.status)+'" data-help-id="chart-label-'+esc(r.id)+'">'
        +'<div class="cr-id">'+esc(r.label)+'</div>'
        +'<div class="cr-val">'+(r.val==null?T('N/A'):r.val.toFixed(1))+'</div>'
        +'<div class="cr-badge">'+statusEmoji(r.status)+'</div>'
        +(r.mock?'<div class="cr-mock">('+statusLabel('Mock')+')</div>':'')
        +'</div>'
        +'<div class="chart-row-canvas"><div class="chart-box" data-help-id="chart-box-single-'+idx+'"><canvas id="'+canvasId+'"></canvas></div></div>'
        +'</div>';
    });
    area.innerHTML=h;
  }else{
    rows.forEach(function(r,idx){
      var labelEl=area.querySelector('[data-help-id="chart-label-'+esc(r.id)+'"]');
      if(labelEl){
        labelEl.className='chart-row-label '+statusClass(r.status);
        var valEl=labelEl.querySelector('.cr-val');
        if(valEl)valEl.textContent=r.val==null?T('N/A'):r.val.toFixed(1);
        var badgeEl=labelEl.querySelector('.cr-badge');
        if(badgeEl)badgeEl.textContent=statusEmoji(r.status);
      }
    });
  }
  rows.forEach(function(r,idx){
    var el=$('chart-single-'+idx);
    if(el)drawLineChart(el,r.datasets,{label:r.unit,timeLabels:tl,thresholds:th,emptyText:T('Waiting for data...')});
  });
}

function _drawAllMode(area,data,tl,npuCount){
  var npuKeys=['temp','volt','clock','dram','util','ctemp'];
  var sysKeys=['cpu','mem','cpucores'];

  var layoutKey='all:'+npuCount+':'+S.isMock;
  if(S._chartLayoutKey!==layoutKey){
    S._chartLayoutKey=layoutKey;
    var h='';

    for(var ni=0;ni<npuCount;ni++){
      h+='<div class="chart-row-label" data-help-id="chart-label-npu-'+ni+'" style="justify-content:flex-start;flex-direction:row;gap:8px;min-width:auto;max-width:none">'
        +'<span class="cr-id" style="font-size:14px">NPU '+ni+(S.isMock?' ('+statusLabel('Mock')+')':'')+'</span></div>';
      h+='<div class="chart-all-grid" data-help-id="chart-grid-npu-'+ni+'">';
      npuKeys.forEach(function(key){
        var canvasId='all-npu'+ni+'-'+key;
        h+='<div class="chart-box" data-help-id="chart-box-'+canvasId+'"><canvas id="'+canvasId+'"></canvas></div>';
      });
      h+='</div>';
    }

    h+='<div class="chart-row-label" data-help-id="chart-label-system" style="justify-content:flex-start;flex-direction:row;gap:8px;min-width:auto;max-width:none;margin-top:12px">'
      +'<span class="cr-id" style="font-size:14px">'+T('System')+'</span></div>';
    h+='<div class="chart-all-grid" data-help-id="chart-grid-system">';
    sysKeys.forEach(function(key){
      var canvasId='all-sys-'+key;
      h+='<div class="chart-box" data-help-id="chart-box-'+canvasId+'"><canvas id="'+canvasId+'"></canvas></div>';
    });
    h+='</div>';

    area.innerHTML=h;
  }

  for(var ni2=0;ni2<npuCount;ni2++){
    npuKeys.forEach(function(key){
      var cfg=CHART_CFG[key];
      var el=$('all-npu'+ni2+'-'+key);
      if(el)drawLineChart(el,_extractSeries(data,cfg,ni2),{label:'NPU '+ni2+' '+metricLabel(cfg.labelKey),timeLabels:tl,thresholds:_thresholdsFor(key),emptyText:T('Waiting for data...')});
    });
  }
  sysKeys.forEach(function(key){
    var cfg=CHART_CFG[key];
    var el=$('all-sys-'+key);
    if(el)drawLineChart(el,_extractSeries(data,cfg,0),{label:metricLabel(cfg.labelKey),timeLabels:tl,thresholds:_thresholdsFor(key),emptyText:T('Waiting for data...')});
  });
}


function setTimeRange(r){
  S.rtView=r;
  ['rt','5m','15m','30m','1h','all'].forEach(function(k){
    var b=$('tr-'+k);if(!b)return;
    b.classList.toggle('active',k===r);
  });
  requestAnimationFrame(drawCharts);
}

function setChartMode(m){
  S.chartMode=m;
  var allModes=['temp','volt','clock','dram','util','ctemp','cpu','mem','cpucores','all'];
  allModes.forEach(function(k){
    var b=$('cm-'+k);if(!b)return;
    b.classList.toggle('active',k===m);
  });
  requestAnimationFrame(drawCharts);
}


function _fmtBytes(b){
  if(!b||b<=0)return'0 B';
  var u=['B','KB','MB','GB','TB'];var i=Math.floor(Math.log(b)/Math.log(1024));
  return(b/Math.pow(1024,i)).toFixed(i>0?1:0)+' '+u[i];
}
function _renderDdrStatus(n){
  var s=n.ddr_status;if(!s||!s.length)return'';
  var badges=s.map(function(v,i){
    return'<span style="font-size:11px;padding:1px 5px;border-radius:4px;background:rgba(255,255,255,.07);color:'+tempColor(v)+'">CH'+i+' '+v+'</span>';
  }).join('');
  return'<div class="npu-metric" style="align-items:flex-start"><span class="mk">'+T('🌡️ DDR Channel Temp')+'</span><span class="mv" style="display:flex;gap:4px;flex-wrap:wrap">'+badges+'</span></div>';
}
function _renderDdrErrors(n){
  var sbe=n.ddr_sbe_cnt||[],dbe=n.ddr_dbe_cnt||[];
  var hasSbe=sbe.some(function(v){return v>0}),hasDbe=dbe.some(function(v){return v>0});
  if(!hasSbe&&!hasDbe)return'';
  var h='<div class="npu-metric" style="align-items:flex-start"><span class="mk" style="color:var(--error)">⚠️ '+T('DDR Errors')+'</span><span class="mv" style="display:flex;gap:4px;flex-wrap:wrap">';
  if(hasSbe)h+=sbe.map(function(v,i){return v>0?'<span style="font-size:11px;padding:1px 5px;border-radius:4px;background:rgba(210,153,34,.12);color:var(--warning)">CH'+i+' SBE:'+v+'</span>':'';}).join('');
  if(hasDbe)h+=dbe.map(function(v,i){return v>0?'<span style="font-size:11px;padding:1px 5px;border-radius:4px;background:rgba(248,81,73,.12);color:var(--error)">CH'+i+' DBE:'+v+'</span>':'';}).join('');
  return h+'</span></div>';
}
function renderNPUTopo(hw){
  const npus=hw.npus||[];
  if($('npu-status-label'))$('npu-status-label').textContent=hw.mock?T('Mock Data'):npus.length+T(' NPU(s)');
  if($('npu-topo'))$('npu-topo').innerHTML=npus.map(function(n, idx){
    var tc=tempColor(n.temp_avg||0);
    var coreRows='';
    if((n.temperatures||[]).length>1){
      var badges=(n.temperatures||[]).map(function(t,i){
        return '<span style="font-size:11px;padding:1px 5px;border-radius:4px;background:rgba(255,255,255,.07);color:'+tempColor(t)+'">C'+i+' '+t.toFixed(0)+'°</span>';
      }).join('');
      coreRows='<div class="npu-metric" style="align-items:flex-start"><span class="mk">'+T('🌡️ Cores')+'</span><span class="mv" style="display:flex;gap:4px;flex-wrap:wrap">'+badges+'</span></div>';
    }
    var npuId=esc(n.id==null?'':String(n.id));
    var firmware=esc(String(n.firmware_version||''));
    var chip=esc(String((n.device_variant||'')+(n.device_type?' '+n.device_type:'')));
    var board=esc(String(n.board_type||''));
    var memoryLabel=(n.memory_type||'')+(n.memory_freq_mhz?' @ '+n.memory_freq_mhz+' MHz':'')+(n.memory_size_bytes?' ('+_fmtBytes(n.memory_size_bytes)+')':'');
    var memory=esc(String(memoryLabel));
    var dramPct=_normalizeDramPct(n.dram_pct);
    var dramWidth=dramPct==null?0:Math.min(dramPct,100);
    return '<div class="npu-card mb8" data-help-id="npu-card-'+idx+'">'
      +'<div class="npu-id"><span class="dot" style="background:'+tc+'"></span>NPU '+npuId+' '+(n.mock?'('+T('Mock')+')':'')+'</div>'
      +'<div class="npu-metric"><span class="mk">'+T('🌡️ Avg Temp')+'</span><span class="mv" style="color:'+tc+'">'+(n.temp_avg||0).toFixed(1)+'°C</span></div>'
      +coreRows
      +'<div class="npu-metric"><span class="mk">'+T('⚡ Voltage')+'</span><span class="mv">'+(n.voltage_avg||0).toFixed(0)+' mV</span></div>'
      +'<div class="npu-metric"><span class="mk">'+T('🔄 Clock')+'</span><span class="mv">'+(n.clock_avg||0).toFixed(0)+' MHz</span></div>'
      +(n.dram_total_mb>0?'<div class="npu-metric" style="flex-direction:column;align-items:flex-start;gap:4px"><span class="mk">'+T('💾 DRAM')+'</span><div style="width:100%;background:rgba(255,255,255,.08);border-radius:4px;height:6px;margin:2px 0"><div style="width:'+dramWidth.toFixed(1)+'%;background:#e879f9;border-radius:4px;height:6px"></div></div><span class="mv" style="color:#e879f9">'+(n.dram_used_mb||0)+' / '+(n.dram_total_mb||0)+' MB ('+_formatDramPct(dramPct)+')</span></div>':'')
      +((n.utilization||[]).length?'<div class="npu-metric" style="align-items:flex-start"><span class="mk">⚙️ '+T('Util')+'</span><span class="mv" style="display:flex;gap:4px;flex-wrap:wrap">'+(n.utilization||[]).map(function(u,i){return'<span style="font-size:11px;padding:1px 5px;border-radius:4px;background:rgba(255,255,255,.07);color:var(--info)">C'+i+' '+u+'%</span>';}).join('')+'</span></div>':'')
      +'<div class="npu-metric"><span class="mk">'+T('🧪 Cores')+'</span><span class="mv">'+(n.cores||1)+'</span></div>'
      +(n.firmware_version?'<div class="npu-metric"><span class="mk">'+T('🔧 Firmware')+'</span><span class="mv" style="color:var(--info)">'+firmware+'</span></div>':'')
      +(n.device_variant||n.device_type?'<div class="npu-metric"><span class="mk">'+T('🧩 Chip')+'</span><span class="mv" style="color:var(--npu-light)">'+chip+'</span></div>':'')
      +(n.board_type?'<div class="npu-metric"><span class="mk">'+T('📋 Board')+'</span><span class="mv">'+board+'</span></div>':'')
      +(n.memory_type?'<div class="npu-metric"><span class="mk">'+T('💿 DDR Type')+'</span><span class="mv">'+memory+'</span></div>':'')
      +_renderDdrStatus(n)
      +_renderDdrErrors(n)
      +'</div>';
  }).join('')||'<p class="txt-dim">'+T('No NPU detected')+'</p>';
}

function renderSysInfo(si){
  const rows=[['OS',si.os],[T('Hostname'),si.hostname],[T('CPU'),si.cpu_model],[T('CPU Cores'),si.cpu_cores],
    [T('Memory'),si.mem_total_gb+'GB'],['Python',si.python],['OpenCV',si.opencv],
    ['DX-RT',si.dx_rt_version],['DX-APP',si.dx_app_version],[T('NPU Count'),si.npu_count],
    [T('NPU PCI'),(si.npu_pci||[]).join(', ')],[T('DX Engine'),si.dx_engine_available?'✅ '+T('Available'):'❌ '+T('Unavailable')],
    [T('SDK Version'),si.sdk_version||T('N/A')],[T('Driver Version'),si.driver_version||T('N/A')],
    [T('PCIe Driver'),si.pcie_driver_version||T('N/A')],[T('Uptime'),si.uptime||T('N/A')]];
  $('sysinfo-table').querySelector('tbody').innerHTML=rows.map(function(row, idx){return '<tr data-help-id="sysinfo-row-'+idx+'"><td style="color:var(--text-3);width:120px">'+esc(row[0])+'</td><td>'+esc(row[1]||T('N/A'))+'</td></tr>'}).join('');
  S.cpuCores=si.cpu_cores||4;
}


var _eventLastTs=0;
function _eventBadge(level){
  var cls='b-ok';
  if(level==='WARNING')cls='b-warn';
  else if(level==='ERROR'||level==='CRITICAL')cls='b-red';
  else if(level==='DEBUG')cls='b-no';
  return'<span class="badge '+cls+'" style="font-size:10px;min-width:44px;text-align:center">'+esc(level)+'</span>';
}

function renderEvents(){
  var events=S.lastEvents||[];
  var el=$('event-log');
  if(!el)return;
  if(!events.length){
    el.innerHTML='<p class="txt-dim txt-sm">'+T('No events recorded')+'</p>';
    if($('event-count'))$('event-count').textContent=eventCountLabel(0);
    return;
  }
  el.innerHTML='';
  events.forEach(function(ev, idx){
    var row=document.createElement('div');
    row.className='event-row';
    row.setAttribute('data-help-id','event-row-'+idx);
    row.innerHTML='<span class="event-ts">'+formatTime((ev.timestamp||0)*1000)+'</span>'+_eventBadge(ev.level||'INFO')+'<span class="event-msg">'+esc(ev.message||'')+'</span>';
    el.appendChild(row);
  });
  S.lastEventCount=events.length;
  if($('event-count'))$('event-count').textContent=eventCountLabel(events.length);
  el.scrollTop=el.scrollHeight;
}

function pollEvents(){
  if (!_isMonitorVisible()) return;
  api('/api/events?since='+_eventLastTs).then(function(data){
    if(!data||data.error||!Array.isArray(data))return;
    if(!data.length)return;
    data.forEach(function(ev){
      var ts=ev.timestamp||0;
      if(ts>_eventLastTs)_eventLastTs=ts;
    });
    S.lastEvents=S.lastEvents.concat(data);
    if(S.lastEvents.length>200)S.lastEvents=S.lastEvents.slice(-200);
    renderEvents();
  });
}

function refreshLanguage(){
  S._lastStatusSig='';
  S._chartLayoutKey='';
  if(S.lastHW){renderStatusBar(S.lastHW);renderNPUTopo(S.lastHW);}
  if(S.lastSystemInfo){renderSysInfo(S.lastSystemInfo);}
  requestAnimationFrame(drawCharts);
  renderEvents();
}

if(typeof DXI18n!=='undefined')DXI18n.onLangChange(refreshLanguage);
setInterval(pollEvents,3000);
