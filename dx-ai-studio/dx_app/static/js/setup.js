
var SETUP={running:false,pollTimer:null,activeStep:null,_stdinManual:false,completedSteps:{}};
var SETUP_SUDO_STEPS={'dx-app-deps':true,'dx-app-build':true,'dx-rt-deps':true,'dx-rt-build':true,'dx-driver':true};

// Live-log renderers (formerly in compiler.js; the Setup page reuses them for step logs).
function compColorLog(text){
  return text.split('\n').map(function(line){
    if(line.match(/\[INFO\]|info/i))return '<span class="cl-info">'+esc(line)+'</span>';
    if(line.match(/\[WARN|warning/i))return '<span class="cl-warn">'+esc(line)+'</span>';
    if(line.match(/\[ERROR|error|fail/i))return '<span class="cl-err">'+esc(line)+'</span>';
    if(line.match(/success|complete|done/i))return '<span class="cl-done">'+esc(line)+'</span>';
    return esc(line);
  }).join('\n');
}
function compRenderLogAppend(logEl,text,state){
  if(!logEl)return;
  state=state||SETUP;
  var next=String(text||'');
  var prev=state._renderedLogText||'';
  if(next===prev)return;
  if(prev&&next.indexOf(prev)===0){
    logEl.insertAdjacentHTML('beforeend',compColorLog(next.slice(prev.length)));
  }else{
    logEl.innerHTML=compColorLog(next);
  }
  state._renderedLogText=next;
  logEl.scrollTop=logEl.scrollHeight;
}
function setupInit(){setupCheckAll();setupLoadVersions();}
/* ── Shared step list and icons ──
   This only reports status (no hand-painted badges or emoji); next step, bar and collapsing are done by DXSteps. */
function _setupIco(n){return (typeof window.DXIcon==='function')?window.DXIcon(n):'';}
function _setupStepState(id,state,facts){
  var root=document.getElementById('setup-steps');
  if(root&&window.DXSteps&&id)window.DXSteps.set(root,id,state,facts?{facts:facts}:undefined);
}
/* Backend detail ("cmake · gcc · ninja") as short facts on one line. */
function _setupFacts(detail){
  if(!detail)return[];
  return String(detail).split(/\s+·\s+/).filter(Boolean).slice(0,4).map(_setupFactText);
}
/* The server sends facts (detail) in English only; known shapes are shown in the chosen language
   (e.g. "18 model(s), 24 video(s)", "Loaded"). Unknown words, names and versions stay as they are. Matched top-down. */
var _SETUP_FACTS=[
  [/^(\d+) model\(s\), (\d+) video\(s\)$/,{ko:'모델 $1개, 영상 $2개',ja:'モデル $1 件、動画 $2 件','zh-CN':'$1 个模型，$2 个视频','zh-TW':'$1 個模型，$2 部影片',es:'$1 modelos, $2 videos'}],
  [/^(\d+) model\(s\) — all OK$/,{ko:'모델 $1개 — 모두 정상',ja:'モデル $1 件 — すべて正常','zh-CN':'$1 个模型 — 全部正常','zh-TW':'$1 個模型 — 全部正常',es:'$1 modelos — todos correctos'}],
  [/^(\d+) model\(s\), (\d+) corrupted \(0 bytes\): (.+)$/,{ko:'모델 $1개, 손상 $2개 (0 바이트): $3',ja:'モデル $1 件、破損 $2 件 (0 バイト): $3','zh-CN':'$1 个模型，$2 个损坏 (0 字节): $3','zh-TW':'$1 個模型，$2 個損毀 (0 位元組): $3',es:'$1 modelos, $2 dañados (0 bytes): $3'}],
  [/^([\d.]+) GB free \/ (\d+) GB total$/,{ko:'$1 GB 남음 / 전체 $2 GB',ja:'空き $1 GB / 合計 $2 GB','zh-CN':'可用 $1 GB / 共 $2 GB','zh-TW':'可用 $1 GB / 共 $2 GB',es:'$1 GB libres / $2 GB en total'}],
  [/^(\d+) MB available \/ (\d+) MB total$/,{ko:'$1 MB 사용 가능 / 전체 $2 MB',ja:'利用可能 $1 MB / 合計 $2 MB','zh-CN':'可用 $1 MB / 共 $2 MB','zh-TW':'可用 $1 MB / 共 $2 MB',es:'$1 MB disponibles / $2 MB en total'}],
  [/^Found: (.+) \| Missing: (.+)$/,{ko:'있음: $1 | 없음: $2',ja:'あり: $1 | なし: $2','zh-CN':'已找到: $1 | 缺少: $2','zh-TW':'已找到: $1 | 缺少: $2',es:'Encontrado: $1 | Falta: $2'}],
  [/^Found: (.+)$/,{ko:'있음: $1',ja:'あり: $1','zh-CN':'已找到: $1','zh-TW':'已找到: $1',es:'Encontrado: $1'}],
  [/^missing: (.+)$/,{ko:'없음: $1',ja:'なし: $1','zh-CN':'缺少: $1','zh-TW':'缺少: $1',es:'falta: $1'}],
  // DX-APP Build (setup_steps._app_build_status) and Sample Assets (shared/asset_setup.sample_assets_status)
  [/^demo C\+\+ (\d+)\/(\d+)$/,{ko:'데모 C++ $1/$2',ja:'デモ C++ $1/$2','zh-CN':'演示 C++ $1/$2','zh-TW':'示範 C++ $1/$2',es:'C++ de demo $1/$2'}],
  [/^all C\+\+ (\d+)\/(\d+)$/,{ko:'전체 C++ $1/$2',ja:'C++ 全体 $1/$2','zh-CN':'全部 C++ $1/$2','zh-TW':'全部 C++ $1/$2',es:'C++ en total $1/$2'}],
  [/^demo models (\d+)\/(\d+) \((\d+) unverified\)$/,{ko:'데모 모델 $1/$2 (검증 안 됨 $3)',ja:'デモモデル $1/$2 (未検証 $3)','zh-CN':'演示模型 $1/$2（未验证 $3）','zh-TW':'示範模型 $1/$2（未驗證 $3）',es:'modelos de demo $1/$2 ($3 sin verificar)'}],
  [/^demo models (\d+)\/(\d+)$/,{ko:'데모 모델 $1/$2',ja:'デモモデル $1/$2','zh-CN':'演示模型 $1/$2','zh-TW':'示範模型 $1/$2',es:'modelos de demo $1/$2'}],
  [/^models (\d+)\/(\d+) \((\d+) unverified\)$/,{ko:'모델 $1/$2 (검증 안 됨 $3)',ja:'モデル $1/$2 (未検証 $3)','zh-CN':'模型 $1/$2（未验证 $3）','zh-TW':'模型 $1/$2（未驗證 $3）',es:'modelos $1/$2 ($3 sin verificar)'}],
  [/^models (\d+)\/(\d+)$/,{ko:'모델 $1/$2',ja:'モデル $1/$2','zh-CN':'模型 $1/$2','zh-TW':'模型 $1/$2',es:'modelos $1/$2'}],
  [/^videos (\d+)\/(\d+) \((\d+) unverified\)$/,{ko:'영상 $1/$2 (검증 안 됨 $3)',ja:'動画 $1/$2 (未検証 $3)','zh-CN':'视频 $1/$2（未验证 $3）','zh-TW':'影片 $1/$2（未驗證 $3）',es:'videos $1/$2 ($3 sin verificar)'}],
  [/^videos (\d+)\/(\d+)$/,{ko:'영상 $1/$2',ja:'動画 $1/$2','zh-CN':'视频 $1/$2','zh-TW':'影片 $1/$2',es:'videos $1/$2'}],
  [/^Unverified sample assets: (.+)$/,{ko:'샘플 자산을 확인할 수 없음: $1',ja:'サンプルを確認できません: $1','zh-CN':'无法确认示例资源: $1','zh-TW':'無法確認範例資源: $1',es:'No se pudieron comprobar los recursos de ejemplo: $1'}],
  [/^probe failed: (.+)$/,{ko:'확인 실패: $1',ja:'確認に失敗: $1','zh-CN':'检测失败: $1','zh-TW':'檢測失敗: $1',es:'falló la comprobación: $1'}],
  [/^No DeepX device found on PCIe bus$/,{ko:'PCIe 버스에서 DeepX 장치를 찾지 못했습니다',ja:'PCIe バスに DeepX デバイスがありません','zh-CN':'PCIe 总线上未找到 DeepX 设备','zh-TW':'PCIe 匯流排上未找到 DeepX 裝置',es:'No se encontró ningún dispositivo DeepX en el bus PCIe'}],
  [/^(?:No )?\/dev\/dxrt\* or \/dev\/deepx\* (?:not )?found$/,{ko:'/dev/dxrt* · /dev/deepx* 없음',ja:'/dev/dxrt* · /dev/deepx* なし','zh-CN':'未找到 /dev/dxrt* · /dev/deepx*','zh-TW':'未找到 /dev/dxrt* · /dev/deepx*',es:'No se encontró /dev/dxrt* ni /dev/deepx*'}],
  [/^No DKMS entry for dxrt\/deepx$/,{ko:'dxrt/deepx의 DKMS 항목 없음',ja:'dxrt/deepx の DKMS エントリなし','zh-CN':'没有 dxrt/deepx 的 DKMS 条目','zh-TW':'沒有 dxrt/deepx 的 DKMS 項目',es:'No hay entrada DKMS para dxrt/deepx'}],
  [/^Loaded$/,{ko:'로드됨',ja:'ロード済み','zh-CN':'已加载','zh-TW':'已載入',es:'Cargado'}],
  [/^Not loaded$/,{ko:'로드 안 됨',ja:'未ロード','zh-CN':'未加载','zh-TW':'未載入',es:'No cargado'}],
  [/^active$/,{ko:'실행 중',ja:'稼働中','zh-CN':'运行中','zh-TW':'執行中',es:'activo'}],
  [/^Not installed$/,{ko:'설치 안 됨',ja:'未インストール','zh-CN':'未安装','zh-TW':'未安裝',es:'No instalado'}],
  [/^Install required$/,{ko:'설치 필요',ja:'インストールが必要','zh-CN':'需要安装','zh-TW':'需要安裝',es:'Requiere instalación'}],
  [/^(\S+) not installed$/,{ko:'$1 미설치',ja:'$1 未インストール','zh-CN':'未安装 $1','zh-TW':'未安裝 $1',es:'$1 no instalado'}],
  [/^(\S+) not available$/,{ko:'$1 사용 불가',ja:'$1 は利用できません','zh-CN':'$1 不可用','zh-TW':'$1 無法使用',es:'$1 no disponible'}],
  [/^(\S+) failed$/,{ko:'$1 실패',ja:'$1 に失敗','zh-CN':'$1 失败','zh-TW':'$1 失敗',es:'$1 falló'}],
  [/^(\S+) not found$/,{ko:'$1 없음',ja:'$1 なし','zh-CN':'未找到 $1','zh-TW':'未找到 $1',es:'$1 no encontrado'}],
  [/^(\S+) found$/,{ko:'$1 있음',ja:'$1 あり','zh-CN':'已找到 $1','zh-TW':'已找到 $1',es:'$1 encontrado'}]
];
function _setupFactText(text){
  text=String(text==null?'':text);
  var lang=(window.DXI18n&&window.DXI18n.lang)||'en';
  if(lang==='en')return text;
  for(var i=0;i<_SETUP_FACTS.length;i++){
    var m=text.match(_SETUP_FACTS[i][0]);
    if(!m)continue;
    var tpl=_SETUP_FACTS[i][1][lang];
    return tpl?tpl.replace(/\$(\d)/g,function(_,n){return m[+n]||'';}):text;
  }
  return text;
}
/* Status next to the run log, in the same shape as the step list's status (icon + words). */
function _setupRunStatus(el,state,text){
  var icon={running:'spinner',done:'check',failed:'x',todo:'stop'}[state]||'info';
  el.className='dx-step-state is-'+state;
  el.innerHTML=_setupIco(icon)+'<span>'+esc(text)+'</span>';
}
async function setupCheckAll(){
  try{
    var r=await api('/api/setup/status');
    ['dx-app-deps','dx-rt-deps','dx-rt-build','dx-driver','dx-app-build','dx-app-setup'].forEach(function(id){
      var s=r[id];if(!s)return;
      var locallyDone=SETUP.completedSteps&&SETUP.completedSteps[id];
      var det=$('setup-detail-'+id);
      /* Facts (s.detail) show as chips in the row; the line below holds only other words (just completed). */
      if(det)det.textContent=(locallyDone&&!s.ok)?_T5('방금 완료됨','Completed just now','完了したばかり','刚刚完成','剛剛完成','Completado ahora mismo'):'';
      /* Badge, next step and bar are painted by the shared step list (shared/static/dx-steps.js). One row holds short facts only. */
      _setupStepState(id,(s.ok||locallyDone)?'done':'todo',_setupFacts(s.detail));
      /* Present files without a Studio record are installed but unverified: offer Verify
         (the same step checks each file's size against the server and keeps a matching one). */
      if(id==='dx-app-setup'){
        var vb=$('setup-verify-dx-app-setup');
        if(vb)vb.style.display=(s.ok&&s.verified===false)?'':'none';
      }
    });
    _setupLiveDisplay(r['live-display']);
  }catch(e){console.error('setupCheckAll error:',e);}
}
/* Optional Live display capture (Xvfb): reported, never installed by a step (setup_steps.live_display_status). */
function _setupLiveDisplay(s){
  var box=$('setup-live-display'), st=$('setup-live-display-state');
  if(!box||!st||!s)return;
  box.setAttribute('data-ok',s.ok?'true':'false');
  _setupRunStatus(st,s.ok?'done':'todo',_setupFactText(s.ok?'Xvfb found':'Xvfb not installed'));
}
function setupMarkStepDone(stepId){
  if(!stepId)return;
  SETUP.completedSteps[stepId]=true;
  _setupStepState(stepId,'done');
  var det=$('setup-detail-'+stepId);
  if(det)det.textContent=_T5('방금 완료됨','Completed just now','完了したばかり','刚刚完成','剛剛完成','Completado ahora mismo');
}
async function setupRun(stepId){
  var params={};
  if(SETUP_SUDO_STEPS[stepId]){
    var authFailed=false;
    while(true){
      var pw=await setupPromptSudoPassword(authFailed);
      if(pw===null){toast(_T5('취소됨','Cancelled','キャンセル','已取消','已取消','Cancelado'),'warn');return;}
      params.password=pw;
      var res=await _setupDoRun(stepId,params);
      if(res&&res.sudo_auth){authFailed=true;continue;}  // wrong password → re-prompt
      return;
    }
  }
  _setupDoRun(stepId,params);
}
function setupPromptSudoPassword(authFailed){
  return new Promise(function(resolve){
    var old=document.getElementById('setup-sudo-modal');if(old)old.remove();
    var overlay=document.createElement('div');
    overlay.id='setup-sudo-modal';
    overlay.style.cssText='position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.55);display:flex;align-items:center;justify-content:center;padding:20px';
    var box=document.createElement('div');
    box.style.cssText='width:min(420px,100%);background:var(--surface-panel,var(--control-bg));border:1px solid var(--border-subtle);border-radius:12px;padding:18px;box-shadow:0 20px 60px rgba(0,0,0,.35)';
    box.innerHTML='<h3 style="margin:0 0 8px">'+_setupIco('lock')+' '+_T5('sudo 인증','sudo Authentication','sudo認証','sudo 认证','sudo 認證','Autenticación sudo')+'</h3>'
      +(authFailed?('<p class="txt-sm" style="margin:0 0 8px;color:var(--danger,#e5484d)">'+_T5('비밀번호가 올바르지 않습니다. 다시 입력하세요.','Incorrect password. Please try again.','パスワードが正しくありません。もう一度入力してください。','密码不正确，请重新输入。','密碼不正確，請重新輸入。','Contraseña incorrecta. Inténtelo de nuevo.')+'</p>'):'')
      +'<p class="txt-sm txt-dim" style="margin:0 0 12px">'+_T5('이 설치 단계는 관리자 권한이 필요합니다. 비밀번호는 이 실행 요청에만 사용됩니다.','This setup step requires administrator privileges. The password is used only for this run.','この設定ステップには管理者権限が必要です。パスワードはこの実行にのみ使用されます。','此安装步骤需要管理员权限。密码仅用于本次运行。','此安裝步驟需要管理員權限。密碼僅用於本次執行。','Este paso de configuración requiere privilegios de administrador. La contraseña se usa solo para esta ejecución.')+'</p>'
      +'<input id="setup-sudo-password" type="password" style="width:100%;box-sizing:border-box;padding:9px 11px;border-radius:8px;border:1px solid var(--border-subtle);background:var(--surface-page);color:var(--text-primary)" placeholder="sudo password">'
      +'<div style="display:flex;justify-content:flex-end;gap:8px;margin-top:14px">'
      +'<button class="btn btn-ghost btn-sm" id="setup-sudo-cancel">'+_T5('취소','Cancel','キャンセル','取消','取消','Cancelar')+'</button>'
      +'<button class="btn btn-primary btn-sm" id="setup-sudo-ok">'+_T5('계속','Continue','続行','继续','繼續','Continuar')+'</button>'
      +'</div>';
    overlay.appendChild(box);document.body.appendChild(overlay);
    var input=document.getElementById('setup-sudo-password');
    var done=function(value){overlay.remove();resolve(value);};
    document.getElementById('setup-sudo-cancel').onclick=function(){done(null);};
    document.getElementById('setup-sudo-ok').onclick=function(){done(input.value);};
    input.onkeydown=function(e){if(e.key==='Enter')done(input.value);if(e.key==='Escape')done(null);};
    setTimeout(function(){input.focus();},0);
  });
}
async function _setupDoRun(stepId,params){
  if(SETUP.running){toast(_T6('다른 작업이 이미 실행 중입니다','Another task is already running','別のタスクが実行中です','另一个任务正在运行','另一個任務正在執行','Otra tarea ya está en ejecución'),'err');return{busy:true};}
  SETUP.running=true;SETUP.activeStep=stepId;
  var stopBtn=$('setup-stop-btn');if(stopBtn)stopBtn.style.display='';
  SETUP._renderedLogText='';
  var logEl=$('setup-log');if(logEl)logEl.textContent=_T5('준비 중…\n','Preparing…\n','準備中…\n','准备中…\n','準備中…\n','Preparando…\n');
  var rs=$('setup-run-status');
  if(rs){rs.style.display='';_setupRunStatus(rs,'running',_T5('실행 중…','Running…','実行中…','运行中…','執行中…','En ejecución…'));}
  _setupStepState(stepId,'running');
  var body=Object.assign({step:stepId},params);
  var r=await postJ('/api/setup/run',body);
  if(r&&r.sudo_auth){
    // wrong/expired sudo password — reset and let the caller re-prompt
    SETUP.running=false;
    if(stopBtn)stopBtn.style.display='none';
    if(rs)rs.style.display='none';
    if(logEl)logEl.textContent='';
    setupCheckAll();
    return{sudo_auth:true};
  }
  if(!r.ok&&!r.started){
    SETUP.running=false;
    if(stopBtn)stopBtn.style.display='none';
    toast(_T6('실행 실패: ','Run failed: ','実行失敗: ','运行失败: ','執行失敗: ','Error al ejecutar: ')+(r.error||''),'err');
    if(rs)_setupRunStatus(rs,'failed',_T5('실패','Failed','失敗','失败','失敗','Falló'));
    _setupStepState(stepId,'failed');
    return{error:r.error||'failed'};
  }
  if(SETUP.pollTimer)clearInterval(SETUP.pollTimer);
  SETUP.pollTimer=setInterval(setupPollLog,700);  // snappier live progress
  return{started:true};
}
function setupPollLog(){
  if(!SETUP.running)return;
  api('/api/setup/log').then(function(r){
    if(r.log){
      var logEl=$('setup-log');
      if(logEl)compRenderLogAppend(logEl,r.log,SETUP);
      setupDetectPrompt(r.log);
    }
    if(r.done){
      clearInterval(SETUP.pollTimer);SETUP.pollTimer=null;
      SETUP.running=false;setupHideStdin();
      var stopBtn=$('setup-stop-btn');if(stopBtn)stopBtn.style.display='none';
      var rs=$('setup-run-status');
      var completedStep=SETUP.activeStep;
      if(r.exit_code===0){
        toast((SETUP.activeStep||'task')+_T6(' 완료!',' complete!',' 完了!',' 完成!',' 完成!',' ¡completo!'),'ok');
        if(rs)_setupRunStatus(rs,'done',_T5('완료','Done','完了','完成','完成','Completado'));
        setupMarkStepDone(completedStep);
        SETUP._lastExitCode=0;
      }else if(r.exit_code===130){
        if(rs)_setupRunStatus(rs,'todo',_T5('중단됨','Stopped','中断','已中断','已中斷','Detenido'));
        SETUP._lastExitCode=130;
      }else{
        toast(_T6('실패 (종료 ','Failed (exit ','失敗 (終了 ','失败 (退出 ','失敗 (結束 ','Error (salida ')+r.exit_code+')','err');
        if(rs)_setupRunStatus(rs,'failed',_T5('실패','Failed','失敗','失败','失敗','Falló')+' (exit '+r.exit_code+')');
        _setupStepState(completedStep,'failed');
        SETUP._lastExitCode=r.exit_code;
      }
      if(r.exit_code===0)setupCheckAll().then(function(){setupMarkStepDone(completedStep);});
      else setupCheckAll();
    }
  }).catch(function(e){console.error('setup poll error:',e);});
}
function setupToggleStdin(){
  var row=$('setup-stdin-row');
  if(!row)return;
  var visible=row.style.display!=='none';
  if(visible){
    row.style.display='none';
    _setupStdinBtnUpdate(false);
  }else{
    row.style.display='';
    SETUP._stdinManual=true;
    var inp=$('setup-stdin-input');if(inp){inp.type='text';inp.focus();}
    _setupStdinBtnUpdate(true);
  }
}
function _setupStdinBtnUpdate(on){
  var btn=$('setup-stdin-toggle-btn');
  if(!btn)return;
  if(on){btn.style.background='var(--accent)';btn.style.color='var(--text-primary)';}
  else{btn.style.background='';btn.style.color='';}
}
function setupDetectPrompt(log){
  var lines=log.trimEnd().split('\n');var last=lines[lines.length-1]||'';
  var lt=last.trim();
  // A trailing prompt line typically ends with ':' (password/value), '>' (interactive
  // selectors like the ModelZoo downloader's "Categories >"), or '?' (yes/no questions).
  var isPrompt=/password for|[Pp]assword\s*:|[Uu]sername.*:|Python version\s*:|\[Y\/n\]|\[y\/N\]/.test(last)
               ||(lt.length>0&&(lt.endsWith(':')||lt.endsWith('>')||lt.endsWith('?'))&&last.length<120);
  var row=$('setup-stdin-row');
  if(isPrompt&&row){
    row.style.display='';
    var pr=$('setup-stdin-prompt');if(pr)pr.textContent=last.trim().substring(0,80);
    var inp=$('setup-stdin-input');
    if(inp)inp.type=/[Pp]assword|password for/.test(last)?'password':'text';
    if(inp&&document.activeElement!==inp)inp.focus();
    _setupStdinBtnUpdate(true);
  }else if(row&&row.style.display!=='none'&&!SETUP._stdinManual){
    // auto-hide only if not manually opened
    row.style.display='none';
    _setupStdinBtnUpdate(false);
  }
}
function setupSendInput(){
  var inp=$('setup-stdin-input');if(!inp)return;
  var val=inp.value;inp.value='';
  // Keep row open for further input
  var pr=$('setup-stdin-prompt');if(pr)pr.textContent=_T5('프로세스에 보낼 입력을 입력하세요 (Enter 키)','Type input to send to the process (press Enter)','プロセスに送信する入力を入力 (Enter キー)','输入要发送到进程的内容 (按 Enter)','輸入要傳送至程序的內容 (按 Enter)','Escriba la entrada para enviar al proceso (pulse Enter)');
  if(inp)inp.type='text';
  postJ('/api/setup/input',{text:val}).then(function(r){
    if(!r.ok)toast(_T5('입력 전송 실패: ','Failed to send input: ','入力送信失敗: ','输入发送失败: ','輸入傳送失敗: ','No se pudo enviar la entrada: ')+(r.error||''),'err');
  });
}
function setupHideStdin(){
  var row=$('setup-stdin-row');if(row)row.style.display='none';
  _setupStdinBtnUpdate(false);
  SETUP._stdinManual=false;
}

/* Diagnostics result, redrawn on a language switch (SETUP._diag). True if it passed. */
function _setupRenderDiag(r){
  var sum=$('diag-summary');
  sum.style.display='';
  var allOk=r.all_ok;
  sum.innerHTML='<div class="diag-summary-bar '+(allOk?'diag-pass':'diag-fail')+'">'+_setupIco(allOk?'check':'alert')+' <strong>'+r.passed+'/'+r.total+'</strong> '+_T5('검사 통과','checks passed','検査合格','检查通过','檢查通過','comprobaciones superadas')+'</div>';
  $('diag-results').innerHTML=(r.checks||[]).map(function(c){
    var cls=c.ok?'diag-card-ok':'diag-card-fail';
    var icon=_setupIco(c.ok?'check':'x');
    var lang=(window.DXI18n&&window.DXI18n.lang)||localStorage.getItem('dx-lang')||'en';
    var langKey=lang.replace('-','');
    var label=typeof c.label==='object'?(c.label[langKey]||c.label.en):c.label;
    var html='<div class="diag-card '+cls+'">';
    html+='<div class="diag-card-title">'+icon+' '+esc(label)+'</div>';
    html+='<div class="diag-card-detail">'+esc(_setupFactText(c.detail||''))+'</div>';
    if(!c.ok&&c.fix){
      var fixText=typeof c.fix==='object'?(c.fix[langKey]||c.fix.en):c.fix;
      html+='<div class="diag-card-fix">'+_setupIco('info')+' '+esc(fixText)+'</div>';
    }
    html+='</div>';
    return html;
  }).join('');
  return allOk;
}

async function runDiagnostics(){
  var btn=$('diag-run-btn');btn.disabled=true;btn.innerHTML=_setupIco('spinner')+' '+_T5('실행 중...','Running...','実行中...','运行中...','執行中...','En ejecución...');
  $('diag-results').innerHTML='<p class="txt-dim">'+_T5('진단 실행 중…','Running diagnostics…','診断実行中…','诊断运行中…','診斷執行中…','Ejecutando diagnóstico…')+'</p>';
  try{
    var r=await api('/api/setup/diagnostics');
    btn.disabled=false;btn.innerHTML=_setupIco('play')+' '+_T5('진단 실행','Run Diagnostics','診断実行','运行诊断','執行診斷','Ejecutar diagnóstico');
    if(r.error){toast(r.error,'err');return;}
    SETUP._diag=r;
    var allOk=_setupRenderDiag(r);
    if(!allOk)toast(_T5('일부 검사 실패 — 진단 확인','Some checks failed — see diagnostics','一部の検査が失敗 — 診断を確認','部分检查失败 — 查看诊断','部分檢查失敗 — 查看診斷','Algunas comprobaciones fallaron — revise el diagnóstico'),'warn');
    else toast(_T5('모든 진단 통과!','All diagnostics passed!','すべての診断に合格!','所有诊断通过!','所有診斷通過!','¡Todos los diagnósticos superados!'),'ok');
  }catch(e){
    btn.disabled=false;btn.innerHTML=_setupIco('play')+' '+_T5('진단 실행','Run Diagnostics','診断実行','运行诊断','執行診斷','Ejecutar diagnóstico');
    toast(_T5('진단 오류: ','Diagnostics error: ','診断エラー: ','诊断错误: ','診斷錯誤: ','Error de diagnóstico: ')+e.message,'err');
  }
}

/* ── Shared sequencing core (Run All + Demo Quick Start both run through this) ──
 * Runs `steps` in order into the SAME #setup-log / sudo-prompt / poll machinery
 * used by a single setupRun() call (_setupDoRun + setupPollLog). One sudo prompt
 * upfront covers every sudo-requiring step in the list; a wrong password re-prompts
 * and retries the step it failed on (same UX as the original Run All).
 * opts:
 *   progressEl      — optional element updated with "n/len" while running
 *   extraParamsFor  — optional fn(stepId)->object merged into that step's run params
 *                      (Demo Quick Start uses this to pass {demo_only:true} for
 *                      'dx-app-setup' only — every other step is unchanged)
 * Returns one of: {completed:true} | {cancelled:true} | {error} | {failed:true,stepId,stoppedAt}
 */
async function _setupRunSequence(steps, opts) {
  opts=opts||{};
  var progressEl=opts.progressEl;
  var extraParamsFor=opts.extraParamsFor||function(){return{};};
  var sudoPassword=null;
  if(steps.some(function(id){return SETUP_SUDO_STEPS[id];})){
    sudoPassword=await setupPromptSudoPassword();
    if(sudoPassword===null){toast(_T6('취소됨','Cancelled','キャンセル','已取消','已取消','Cancelado'),'warn');return{cancelled:true};}
  }
  var i;
  for(i=0;i<steps.length;i++){
    if(progressEl){
      progressEl.style.display='';
      progressEl.textContent=_T6('실행 중…','Running…','実行中…','运行中…','執行中…','Ejecutando…')+' '+(i+1)+'/'+steps.length;
    }
    SETUP._lastExitCode=null;
    var needsSudo=!!SETUP_SUDO_STEPS[steps[i]];
    var params=Object.assign({},extraParamsFor(steps[i]));
    if(needsSudo)params.password=sudoPassword;
    var startRes,cancelled=false;
    while(true){
      startRes=await _setupDoRun(steps[i],params);
      if(startRes&&startRes.sudo_auth){  // wrong sudo password → re-prompt + retry this step
        var npw=await setupPromptSudoPassword(true);
        if(npw===null){cancelled=true;break;}
        sudoPassword=npw;
        params.password=sudoPassword;
        continue;
      }
      break;
    }
    if(cancelled){toast(_T6('취소됨','Cancelled','キャンセル','已取消','已取消','Cancelado'),'warn');return{cancelled:true,stoppedAt:i};}
    if(startRes&&startRes.error)return{error:startRes.error,stoppedAt:i};  // _setupDoRun already toasted
    while(SETUP.running){await new Promise(function(r){setTimeout(r,1500)});}
    await setupCheckAll();
    if(SETUP._lastExitCode===0)setupMarkStepDone(steps[i]);
    if(SETUP._lastExitCode!==0)return{failed:true,stepId:steps[i],stoppedAt:i};
  }
  return{completed:true};
}

/* ── Run All ── */
async function setupRunAll() {
  var btn=$('setup-run-all');
  var prog=$('setup-run-all-progress');
  if(SETUP.running){toast(_T6('다른 작업이 이미 실행 중입니다','Another task is already running','別のタスクが実行中です','另一个任务正在运行','另一個任務正在執行','Otra tarea ya está en ejecución'),'err');return;}
  var ALL=['dx-app-deps','dx-rt-deps','dx-rt-build','dx-driver','dx-app-build','dx-app-setup','inference-venv'];
  // Idempotency: skip steps already satisfied so re-running Run All on a machine that ALREADY
  // has a working runtime/driver/build (e.g. an existing dx-all-suite user who just added AI
  // Studio) does NOT rebuild dx_rt, reinstall the NPU driver, or overwrite /usr/local/lib — it
  // only fills genuine gaps. (Demo Quick Start already filters this way via the backend.)
  var STEPS=ALL;
  try{
    var st=await api('/api/setup/status');
    STEPS=ALL.filter(function(id){return !(((st&&st[id])||{}).ok);});
  }catch(e){/* status probe failed → run the full list rather than silently skip */}
  if(!STEPS.length){
    toast(_T6('이미 모두 설치되어 있습니다 — 실행할 항목 없음','Everything is already installed — nothing to run','すべてインストール済み — 実行する項目なし','已全部安装 — 无需执行','已全部安裝 — 無需執行','Todo ya está instalado — nada que ejecutar'),'ok');
    return;
  }
  btn.disabled=true;
  var res=await _setupRunSequence(STEPS,{progressEl:prog});
  btn.disabled=false;
  prog.style.display='none';
  if(res&&res.completed)toast(_T6('전체 실행 완료!','Run All complete!','全実行完了!','全部执行完成!','全部執行完成!','¡Ejecución completa!'),'ok');
  else if(res&&res.failed)toast(_T6('전체 실행 중단','Run All stopped','全実行中断','全部执行中断','全部執行中斷','Ejecución detenida')+' — '+res.stepId,'err');
  // cancelled / start-error cases already toasted inside _setupRunSequence / _setupDoRun
}

/* ── Demo Quick Start ── (top-of-page highlighted block; Task 10 of the Run Demo GUI feature)
 * Fetches the minimal step list still needed for a demo from the backend
 * (GET /api/setup/quick-start-plan → quick_start_plan(), the single source of
 * truth — see dx_app/core/setup_steps.py), then reuses the exact same sudo
 * prompt + sequencing + #setup-log as Run All via _setupRunSequence. Only
 * 'dx-app-build' and 'dx-app-setup' get demo_only:true so the backend (setup_steps.step_argv)
 * builds --minimal and downloads only the run_demo models plus the sample videos.
 */
/* Demo form of the build and asset steps (setup_steps.step_argv): build.sh --minimal and the run_demo models only. */
function _setupDemoParams(id){return (id==='dx-app-setup'||id==='dx-app-build')?{demo_only:true}:{};}
async function setupDemoQuickStart() {
  if(SETUP.running){toast(_T6('다른 작업이 이미 실행 중입니다','Another task is already running','別のタスクが実行中です','另一个任务正在运行','另一個任務正在執行','Otra tarea ya está en ejecución'),'err');return;}
  var btn=$('setup-quickstart-btn');
  var prog=$('setup-quickstart-progress');
  if(btn)btn.disabled=true;
  try{
    var r=await api('/api/setup/quick-start-plan');
    var plan=r.plan||[];
    if(plan.length===0){
      if(prog)prog.style.display='none';
      _setupQuickstartRevealTryDemo();
      return;
    }
    var res=await _setupRunSequence(plan,{
      progressEl:prog,
      extraParamsFor:_setupDemoParams
    });
    if(res&&res.completed){
      toast(_T6('데모 준비 완료!','Demo ready!','デモの準備ができました!','演示已就绪！','示範已就緒！','¡Demo lista!'),'ok');
      _setupQuickstartRevealTryDemo();
    }else if(res&&res.failed){
      toast(_T6('데모 설정 실패','Demo setup failed','デモ設定に失敗','演示设置失败','示範設定失敗','Error al configurar la demo')+' — '+res.stepId,'err');
    }
    // cancelled / start-error cases already toasted inside _setupRunSequence / _setupDoRun
  }catch(e){
    toast(_T6('데모 설정 오류: ','Demo setup error: ','デモ設定エラー: ','演示设置错误: ','示範設定錯誤: ','Error de configuración de demo: ')+e.message,'err');
  }finally{
    if(btn)btn.disabled=false;
    if(prog)prog.style.display='none';
  }
}
function _setupQuickstartRevealTryDemo(){
  var b=$('setup-try-demo');
  if(b)b.style.display='';
}

/* ── Stop ── */
async function setupStop() {
  try{
    var r=await fetch('/api/setup/stop',{method:'POST'}).then(function(x){return x.json()});
    if(r.ok)toast(_T6('중단됨','Stopped','中断済','已中断','已中斷','Detenido'),'warn');
    else toast(_T6('중단 실패','Stop failed','中断失敗','中断失败','中斷失敗','Error al detener'),'err');
  }catch(e){toast(_T6('중단 오류: ','Stop error: ','中断エラー: ','中断错误: ','中斷錯誤: ','Error al detener: ')+e.message,'err');}
}

/* ── Version Info Display ── */
async function setupLoadVersions() {
  try{
    var st=await fetch('/api/setup/status').then(function(x){return x.json()});
    if(st.versions){
      var vc=$('setup-version-card');if(vc)vc.style.display='';
      var vg=$('setup-version-grid');if(!vg)return;
      var labels={dx_app:'DX-APP',dx_runtime:'DX-Runtime',npu_driver:'NPU Driver',compiler:'DX-COM',kernel:'Kernel',python:'Python'};
      vg.innerHTML='';
      Object.keys(st.versions).forEach(function(k){
        vg.innerHTML+='<div style="padding:6px 10px;background:var(--control-bg);border-radius:var(--radius);font-size:12px">'
          +'<div class="txt-dim" style="font-size:10px">'+(labels[k]||k)+'</div>'
          +'<div style="font-family:var(--mono)">'+esc(st.versions[k])+'</div></div>';
      });
    }
  }catch(e){}
}

if (typeof registerLangRefresher === 'function') {
  registerLangRefresher(function refreshSetupLanguage() {
    if (document.querySelector('#page-setup.active') && typeof setupInit === 'function') setupInit();
    if (SETUP._diag && document.getElementById('diag-results')) _setupRenderDiag(SETUP._diag);
  });
}
