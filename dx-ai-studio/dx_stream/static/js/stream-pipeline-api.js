/**
 * DX Stream Pipeline — API & 연결 검증 모듈
 * 서버 API 호출, 파이프라인 제어, 연결 규칙 검증, 팔레트 하이라이트
 */

DXStream.pipelineInit = async function () {
    var resp = await DXStream.api('/api/pipeline/elements');
    if (resp.error) return;
    // 새 API 형식: {categories: {...}, connection_rules: {...}, ...}
    var cats = resp.categories || resp;  // backward compat
    DXStream._pipeState.elements = cats;
    DXStream._connectionRules = resp.connection_rules || {};
    DXStream._elementOverrides = resp.element_overrides || {};
    DXStream._semanticWarnings = resp.semantic_warnings || [];
    DXStream._autoConverterRules = resp.auto_converter_rules || [];
    var flat = [];
    if (!Array.isArray(cats)) {
        Object.keys(cats).forEach(function (cat) {
            cats[cat].forEach(function (el) { flat.push(el); });
        });
    } else {
        flat = cats;
    }
    DXStream._pipeState.elementFlat = flat;
    // 모델/비디오/라이브러리 목록 로드 (속성 드롭다운용)
    DXStream._pipeAssets = null;
    DXStream.api('/api/pipeline/assets').then(function (a) {
        if (!a.error) DXStream._pipeAssets = a;
    });
    _renderPalette(cats);
    _initCanvas();
    _bindPaletteDrag();
    _hidePropertyPanel();
    // localStorage 자동복원
    try {
        var draft = localStorage.getItem('dx-pipeline-draft');
        if (draft) {
            var d = JSON.parse(draft);
            if (d.nodes && d.nodes.length > 0) {
                DXStream._pipeState.nodes = d.nodes;
                DXStream._pipeState.edges = d.edges || [];
                DXStream._pipeState._nextId = d._nextId || 1;
            }
        }
    } catch(_) {}
    _updateElementCount();
    _updatePipelineButtons();
    _pushHistory(); // 초기 상태 기록
};

/* ── 언어 변경 시 캔버스/팔레트만 갱신 (이벤트 리스너 중복 방지) ── */
DXStream._pipelineRefreshLang = function () {
    if (DXStream._pipeState.elements) {
        _renderPalette(DXStream._pipeState.elements);
    }
    _refreshCanvas();
    _updateElementCount();
};

DXStream.pipelineZoomIn = function () {
    DXStream._pipeState.zoom = Math.min(DXStream._pipeState.zoom + 0.1, 3.0);
    _refreshCanvas();
};

DXStream.pipelineZoomOut = function () {
    DXStream._pipeState.zoom = Math.max(DXStream._pipeState.zoom - 0.1, 0.3);
    _refreshCanvas();
};

DXStream.pipelineFitView = function () {
    var st = DXStream._pipeState;
    if (st.nodes.length === 0) {
        st.zoom = 1; st.offsetX = 0; st.offsetY = 0;
        _refreshCanvas(); return;
    }
    var canvas = DXStream.$('pipeline-canvas');
    if (!canvas) return;
    var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    st.nodes.forEach(function (n) {
        if (n.x < minX) minX = n.x;
        if (n.y < minY) minY = n.y;
        if (n.x + _NODE_W > maxX) maxX = n.x + _NODE_W;
        if (n.y + _NODE_H > maxY) maxY = n.y + _NODE_H;
    });
    var pad = 60;
    var bw = maxX - minX + pad * 2;
    var bh = maxY - minY + pad * 2;
    st.zoom = Math.max(0.3, Math.min(2.0, Math.min(canvas.width / bw, canvas.height / bh)));
    st.offsetX = (canvas.width - bw * st.zoom) / 2 - minX * st.zoom + pad * st.zoom;
    st.offsetY = (canvas.height - bh * st.zoom) / 2 - minY * st.zoom + pad * st.zoom;
    _refreshCanvas();
};

DXStream.pipelineReset = function () {
    DXStream.confirmModal(
        T('Reset Pipeline'),
        T('Reset pipeline? All nodes and connections will be removed.')
    ).then(function (ok) {
        if (!ok) return;
        var st = DXStream._pipeState;
        st.zoom = 1.0;
        st.offsetX = 0;
        st.offsetY = 0;
        st.nodes = [];
        st.edges = [];
        st.selectedNode = null;
        st.selectedNodes = [];
        st.selectedEdge = null;
        _hidePropertyPanel();
        _pushHistory();
        _updateElementCount();
        _refreshCanvas();
    });
};

DXStream.pipelineValidate = async function () {
    var st = DXStream._pipeState;
    var issues = [];
    var warnNodeIds = [];

    // 1. client-side: source 존재 확인
    var hasSource = st.nodes.some(function (n) { return n.category === 'source'; });
    if (!hasSource && st.nodes.length > 0) {
        issues.push(T('Pipeline has no source'));
    }

    // 2. client-side: 고립 노드
    st.nodes.forEach(function (n) {
        var connected = st.edges.some(function (ed) { return ed.from === n.id || ed.to === n.id; });
        if (!connected && st.nodes.length > 1) {
            issues.push(T('Isolated node found') + ': ' + n.name);
            warnNodeIds.push(n.id);
        }
    });

    // 3. client-side: ELEMENT_OVERRIDES 검증 (min_outputs, min_inputs)
    var overrides = DXStream._elementOverrides || {};
    st.nodes.forEach(function (n) {
        var ov = overrides[n.type];
        if (!ov) return;
        if (ov.min_outputs) {
            var outCount = st.edges.filter(function (ed) { return ed.from === n.id; }).length;
            if (outCount < ov.min_outputs) {
                issues.push(n.name + ': ' + T(ov.warn_msg_en));
                warnNodeIds.push(n.id);
            }
        }
        if (ov.min_inputs) {
            var inCount = st.edges.filter(function (ed) { return ed.to === n.id; }).length;
            if (inCount < ov.min_inputs) {
                issues.push(n.name + ': ' + T(ov.warn_msg_en));
                warnNodeIds.push(n.id);
            }
        }
    });

    // 4. client-side: DxDeTile without DxTile 경고
    var hasDeTile = st.nodes.some(function (n) { return n.type === 'DxDeTile'; });
    var hasTile = st.nodes.some(function (n) { return n.type === 'DxTile'; });
    if (hasDeTile && !hasTile) {
        st.nodes.forEach(function (n) {
            if (n.type === 'DxDeTile') {
                issues.push(n.name + ': ' + T('Use with DxTile'));
                warnNodeIds.push(n.id);
            }
        });
    }

    // client-side 결과 표시
    if (issues.length > 0) {
        DXStream.toast(T('Pipeline has issues: ') + issues.length, 'warn');
        issues.forEach(function (msg) { DXStream.toast(msg, 'warn'); });
    }

    // warn 노드 시각적 강조 (3초 후 해제)
    if (warnNodeIds.length > 0) {
        st._validateWarnNodes = warnNodeIds;
        _refreshCanvas();
        setTimeout(function () {
            st._validateWarnNodes = [];
            _refreshCanvas();
        }, 3000);
    }

    // 4. server-side GStreamer 검증 (기존 로직 유지)
    var resp = await DXStream.postJ('/api/pipeline/validate', {
        nodes: st.nodes,
        edges: st.edges,
    });
    if (resp.error) {
        DXStream.toast(resp.error, 'error');
        return;
    }
    if (issues.length === 0) {
        DXStream.toast(T('Pipeline is valid'), 'ok');
    }
};

// Show the MJPEG <img> stream in the pipeline preview (creating the element if needed) and
// hide the WebRTC <video>. Reused by the normal MJPEG path and the WebRTC→MJPEG fallback.
DXStream._wirePipelineMjpeg = function () {
    var videoSection = DXStream.$('pipeline-video-section');
    if (videoSection) videoSection.style.display = '';
    var pipeVideo = DXStream.$('pipeline-webrtc-video');
    if (pipeVideo) pipeVideo.style.display = 'none';
    var mjpegImg = DXStream.$('pipeline-mjpeg-stream');
    if (!mjpegImg) {
        mjpegImg = document.createElement('img');
        mjpegImg.id = 'pipeline-mjpeg-stream';
        mjpegImg.style.cssText = 'width:100%;height:auto;border-radius:8px;background:#000;';
        var container = pipeVideo ? pipeVideo.parentNode : videoSection;
        if (container) container.appendChild(mjpegImg);
    }
    mjpegImg.style.display = '';
    mjpegImg.src = '/api/stream/mjpeg?' + Date.now();
    if (videoSection) videoSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
};

function _resetPipelineAfterFallbackFailure(error) {
    DXStream._pipeRunning = false;
    _updatePipelineButtons();
    DXStream.toast(T('MJPEG fallback failed: ') + error, 'error');
}

DXStream.pipelineRun = async function () {
    if (DXStream._pipeRunning) return;
    DXStream._pipeRunning = true;
    _updatePipelineButtons();

    const st = DXStream._pipeState;
    const webrtcPayloadTypes = await DXStream.webrtc.preferredPayloadTypes();
    const _runBody = {
        nodes: st.nodes,
        edges: st.edges,
        webrtcPayloadTypes: webrtcPayloadTypes,
    };
    // Same Local/Remote choice as the demo page: remote (SSH tunnel/NAT) → HW H264 over HTTP
    // (fMP4 + MSE), or MJPEG if the browser lacks MSE. Local keeps WebRTC.
    if (DXStream._playbackMode === 'remote') {
        if (DXStream._mseSupported && DXStream._mseSupported()) _runBody.output = 'fmp4';
        else _runBody.forceMjpeg = true;
    }
    const resp = await DXStream.postJ('/api/pipeline/run', _runBody);
    if (resp.error) {
        DXStream._pipeRunning = false;
        _updatePipelineButtons();
        DXStream.toast(resp.error, 'error');
        return;
    }
    DXStream.toast(T('Pipeline started'), 'success');

    // 파이프라인 상태 배지 즉시 갱신
    var badge = DXStream.$('pipeline-status');
    if (badge) { badge.textContent = '▶ ' + T('Running'); badge.className = 'status-pill pill-running'; }

    // MJPEG/WebRTC/fMP4 자동 연결 (output_mode에 따라)
    if (resp.output_mode === 'mjpeg' || resp.output_mode === 'webrtc' || resp.output_mode === 'fmp4') {
        var videoSection = DXStream.$('pipeline-video-section');
        if (videoSection) {
            videoSection.style.display = '';
        }

        if (resp.output_mode === 'mjpeg') {
            DXStream._wirePipelineMjpeg();
        } else if (resp.output_mode === 'fmp4') {
            // Remote (tunnel/NAT): HW H264 over HTTP via MSE — reuses the demo page's player.
            var pipeVideo = DXStream.$('pipeline-webrtc-video');
            var pmjpeg = DXStream.$('pipeline-mjpeg-stream');
            if (pmjpeg) pmjpeg.style.display = 'none';
            if (pipeVideo && DXStream._fmp4PlayInto) DXStream._fmp4PlayInto(pipeVideo);
            if (videoSection) videoSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            var pipeVideo = DXStream.$('pipeline-webrtc-video');
            if (pipeVideo) {
                // Local WebRTC, but auto-fall back to MJPEG if it can't connect within the
                // deadline (air-gapped/tunnel → ICE stalls forever, video stays black). Re-run
                // the pipeline forcing MJPEG, then wire the <img> stream.
                DXStream.webrtc.connect(pipeVideo, false, function (reason) {
                    DXStream.toast(T('WebRTC could not connect — switching to MJPEG'), 'info');
                    DXStream.postJ('/api/pipeline/run',
                        Object.assign({}, _runBody, { forceMjpeg: true })
                    ).then(function (r2) {
                        if (r2 && !r2.error && r2.output_mode === 'mjpeg') {
                            DXStream._wirePipelineMjpeg();
                        } else {
                            _resetPipelineAfterFallbackFailure(
                                (r2 && r2.error) || 'Forced MJPEG did not start'
                            );
                        }
                    }).catch(function (error) {
                        _resetPipelineAfterFallbackFailure(error && error.message ? error.message : error);
                    });
                });
            }
        }
    } else if (resp.output_mode === 'native') {
        DXStream.toast(T('Native display mode (fpsdisplaysink)'), 'info');
    }
};

DXStream.pipelineStop = async function () {
    DXStream.webrtc.disconnect();
    if (DXStream._fmp4Stop) DXStream._fmp4Stop();  // tear down MSE stream if remote/fMP4 was active
    var resp = await DXStream.postJ('/api/pipeline/stop', {});
    DXStream._pipeRunning = false;
    _updatePipelineButtons();
    if (resp.error) {
        DXStream.toast(resp.error, 'error');
        return;
    }
    DXStream.toast(T('Pipeline stopped'), 'info');

    // 비디오 섹션 숨김 및 정리
    var videoSection = DXStream.$('pipeline-video-section');
    if (videoSection) {
        videoSection.style.display = 'none';
    }
    var pipeVideo = DXStream.$('pipeline-webrtc-video');
    if (pipeVideo) { pipeVideo.srcObject = null; pipeVideo.style.display = ''; }
    var mjpegImg = DXStream.$('pipeline-mjpeg-stream');
    if (mjpegImg) { mjpegImg.src = ''; mjpegImg.style.display = 'none'; }
    var statsOverlay = DXStream.$('webrtc-stats-overlay');
    if (statsOverlay) statsOverlay.textContent = '';

    // 파이프라인 상태 배지 즉시 갱신
    var badge = DXStream.$('pipeline-status');
    if (badge) { badge.textContent = T('Idle'); badge.className = 'status-pill pill-idle'; }
};

function _updatePipelineButtons() {
    var runBtn = DXStream.$('btn-pipeline-run');
    var stopBtn = DXStream.$('btn-pipeline-stop');
    if (runBtn) runBtn.disabled = DXStream._pipeRunning;
    if (stopBtn) stopBtn.disabled = !DXStream._pipeRunning;
}

/* ── HTML onclick에서 호출하는 함수 alias/구현 ── */
DXStream.runPipeline = function () { DXStream.pipelineRun(); };
DXStream.stopPipeline = function () { DXStream.pipelineStop(); };

DXStream.exportPipeline = function () {
    var st = DXStream._pipeState;
    var data = JSON.stringify({ nodes: st.nodes, edges: st.edges }, null, 2);
    var blob = new Blob([data], { type: 'application/json' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'pipeline.json';
    a.click();
    URL.revokeObjectURL(a.href);
    DXStream.toast(T('Pipeline exported'), 'success');
};

DXStream.savePipelineToServer = async function () {
    var name = await DXStream.inputModal(
        T('💾 파이프라인 저장'),
        { placeholder: T('파이프라인 이름') }
    );
    if (!name) return;
    var st = DXStream._pipeState;
    var resp = await DXStream.postJ('/api/pipeline/save', {
        name: name, nodes: st.nodes, edges: st.edges
    });
    if (resp.error) { DXStream.toast(resp.error, 'error'); return; }
    DXStream.toast(T('Saved: ') + name, 'success');
};

DXStream.loadPipelineFromServer = async function () {
    var list = await DXStream.api('/api/pipeline/list');
    if (!list || list.length === 0) {
        DXStream.toast(T('No saved pipelines'), 'info');
        return;
    }
    var name = await DXStream.inputModal(
        T('📂 파이프라인 로드'),
        { description: list.join(', '),
          placeholder: T('파이프라인 이름 입력') }
    );
    if (!name) return;
    var data = await DXStream.api('/api/pipeline/load/' + name);
    if (data.error) { DXStream.toast(data.error, 'error'); return; }
    DXStream._pipeState.nodes = data.nodes || [];
    DXStream._pipeState.edges = data.edges || [];
    // _nextId 재계산 (node/edge ID 충돌 방지)
    var maxId = 0;
    DXStream._pipeState.nodes.forEach(function (n) {
        var num = parseInt((n.id || '').replace('n', '')) || 0;
        if (num > maxId) maxId = num;
    });
    DXStream._pipeState.edges.forEach(function (e) {
        var num = parseInt((e.id || '').replace('e', '')) || 0;
        if (num > maxId) maxId = num;
    });
    DXStream._pipeState._nextId = maxId + 1;
    DXStream._pipeState.selectedNode = null;
    DXStream._pipeState.selectedNodes = [];
    _pushHistory();
    _refreshCanvas();
    DXStream.toast(T('Loaded: ') + name, 'success');
};

DXStream.deletePipelineFromServer = async function () {
    var list = await DXStream.api('/api/pipeline/list');
    if (!list || list.length === 0) {
        DXStream.toast(T('No saved pipelines'), 'info');
        return;
    }
    var name = await DXStream.inputModal(
        T('🗑️ 파이프라인 삭제'),
        { description: list.join(', '),
          placeholder: T('삭제할 파이프라인 이름') }
    );
    if (!name) return;
    var resp = await DXStream.postJ('/api/pipeline/delete/' + name, {});
    if (resp.error) { DXStream.toast(resp.error, 'error'); return; }
    DXStream.toast(T('Deleted: ') + name, 'success');
};

DXStream.importPipeline = function () {
    var input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = function (e) {
        var file = e.target.files[0];
        if (!file) return;
        var reader = new FileReader();
        reader.onload = function (ev) {
            try {
                var data = JSON.parse(ev.target.result);
                var doImport = function () {
                    DXStream._pipeState.nodes = data.nodes || [];
                    DXStream._pipeState.edges = data.edges || [];
                    DXStream._pipeState.selectedNode = null;
                    DXStream._pipeState.selectedNodes = [];
                    DXStream._pipeState.selectedEdge = null;
                    DXStream._pipeState._nextId = Math.max.apply(null,
                        (data.nodes || []).map(function (n) { return parseInt(n.id.replace('n','')) || 0; }).concat([0])) + 1;
                    _pushHistory();
                    _updateElementCount();
                    _refreshCanvas();
                    DXStream.toast(T('Pipeline imported'), 'success');
                };
                if (DXStream._pipeState.nodes.length > 0) {
                    DXStream.confirmModal(
                        T('Import Pipeline'),
                        T('Current pipeline will be replaced. Continue?')
                    ).then(function (ok) { if (ok) doImport(); });
                } else {
                    doImport();
                }
            } catch (err) {
                DXStream.toast(T('Error: ') + err.message, 'error');
            }
        };
        reader.readAsText(file);
    };
    input.click();
};

function _hasCycle(fromId, toId, edges) {
    // toId → fromId에 도달 가능하면 순환
    var visited = {};
    var queue = [toId];
    while (queue.length > 0) {
        var cur = queue.shift();
        if (cur === fromId) return true;
        if (visited[cur]) continue;
        visited[cur] = true;
        edges.forEach(function (ed) {
            if (ed.from === cur) queue.push(ed.to);
        });
    }
    return false;
}

function _canStartEdge(nodeId) {
    var node = DXStream._pipeState.nodes.find(function (n) { return n.id === nodeId; });
    if (!node) return false;
    var override = (DXStream._elementOverrides || {})[node.type];
    if (override && override.has_output === false) return false;
    var rule = (DXStream._connectionRules || {})[node.category];
    if (rule && rule.has_output === false) return false;
    return true;
}

function _validateConnection(fromId, toId) {
    var st = DXStream._pipeState;
    var fromNode = st.nodes.find(function (n) { return n.id === fromId; });
    var toNode = st.nodes.find(function (n) { return n.id === toId; });
    if (!fromNode || !toNode) return { result: 'block', reason: 'Node not found' };
    var rules = DXStream._connectionRules || {};
    var overrides = DXStream._elementOverrides || {};
    var fromRule = rules[fromNode.category] || {};
    var toRule = rules[toNode.category] || {};
    var fromOv = overrides[fromNode.type] || {};
    var toOv = overrides[toNode.type] || {};

    // Step 1: 구조 검증
    var hasOut = fromOv.has_output !== undefined ? fromOv.has_output : (fromRule.has_output !== false);
    if (!hasOut) return { result: 'block', reason: T('Output has no outgoing connections') };
    var hasIn = toOv.has_input !== undefined ? toOv.has_input : (toRule.has_input !== false);
    if (!hasIn) return { result: 'block', reason: T('Source cannot receive input') };

    // Step 2: 카테고리 호환성
    var allowed = fromRule.allowed_next;
    if (allowed !== null && allowed !== undefined) {
        if (allowed.indexOf(toNode.category) === -1 && toNode.category !== 'utility') {
            // 차단 전 의미론적 경고 확인 (inference→inference 등)
            var sWarnings = DXStream._semanticWarnings || [];
            for (var si = 0; si < sWarnings.length; si++) {
                var sw = sWarnings[si];
                if (sw.pattern === 'inference_to_inference' &&
                    fromNode.category === 'inference' && toNode.category === 'inference') {
                    return { result: 'warn', reason: T(sw.msg_en) };
                }
            }
            return { result: 'block', reason: T('Category connection not allowed') };
        }
    }

    // Step 3: 자동 컨버터 (의미론적보다 먼저)
    var acRules = DXStream._autoConverterRules || [];
    for (var i = 0; i < acRules.length; i++) {
        var acr = acRules[i];
        if (acr.from_categories.indexOf(fromNode.category) !== -1 &&
            acr.to_elements.indexOf(toNode.type) !== -1) {
            return { result: 'auto_convert', insert: acr.insert, reason: T(acr.msg_en) };
        }
    }

    // Step 4: 의미론적 경고
    var sWarnings = DXStream._semanticWarnings || [];
    for (var j = 0; j < sWarnings.length; j++) {
        var sw = sWarnings[j];
        if (sw.pattern === 'inference_to_inference' &&
            fromNode.category === 'inference' && toNode.category === 'inference') {
            return { result: 'warn', reason: T(sw.msg_en) };
        }
    }

    var rec = toOv.recommended_prev_elements;
    if (rec && rec.indexOf(fromNode.type) === -1) {
        return { result: 'warn', reason: T('Warning: ') + T('Recommended: connect from ') + rec.join(', ') };
    }

    return { result: 'allow' };
}

function _getConnectable(fromId) {
    var st = DXStream._pipeState;
    var result = { allow: [], warn: [], block: [] };
    st.nodes.forEach(function (n) {
        if (n.id === fromId) return;
        var dup = st.edges.some(function (ed) { return ed.from === fromId && ed.to === n.id; });
        if (dup) { result.block.push({ id: n.id, reason: T('Duplicate connection') }); return; }
        if (_hasCycle(fromId, n.id, st.edges)) { result.block.push({ id: n.id, reason: T('Cannot connect: would create a cycle') }); return; }
        var v = _validateConnection(fromId, n.id);
        if (v.result === 'allow' || v.result === 'auto_convert') result.allow.push(n.id);
        else if (v.result === 'warn') result.warn.push({ id: n.id, reason: v.reason });
        else result.block.push({ id: n.id, reason: v.reason });
    });
    return result;
}

function _createEdge(fromId, toId, status, warnMsg) {
    var st = DXStream._pipeState;
    var edge = { id: 'e' + st._nextId++, from: fromId, to: toId };
    if (status) edge.status = status;
    if (warnMsg) edge.warnMsg = warnMsg;
    st.edges.push(edge);
}

function _autoInsertConverter(fromId, toId, converterType) {
    var st = DXStream._pipeState;
    var fromNode = st.nodes.find(function (n) { return n.id === fromId; });
    var toNode = st.nodes.find(function (n) { return n.id === toId; });
    if (!fromNode || !toNode) return;
    var cx = (fromNode.x + toNode.x) / 2;
    var cy = fromNode.y;
    if (Math.abs(toNode.x - fromNode.x) < _NODE_W + 20) {
        cx = fromNode.x + _NODE_W + 20;
    }
    var converterId = 'n' + st._nextId++;
    var converterEl = st.elementFlat.find(function (e) { return e.name === converterType; });
    st.nodes.push({
        id: converterId, type: converterType, name: converterType,
        category: converterEl ? converterEl.category : 'utility',
        x: Math.round(cx / 20) * 20, y: Math.round(cy / 20) * 20, properties: {}
    });
    st.edges.push({ id: 'e' + st._nextId++, from: fromId, to: converterId });
    st.edges.push({ id: 'e' + st._nextId++, from: converterId, to: toId });
    _pushHistory();
    _updateElementCount();
    _refreshCanvas();
    DXStream.toast(T('Converter inserted: ') + converterType, 'info');
}

function _highlightPalette(fromId) {
    var st = DXStream._pipeState;
    var fromNode = st.nodes.find(function (n) { return n.id === fromId; });
    if (!fromNode) return;
    var rules = DXStream._connectionRules || {};
    var fromRule = rules[fromNode.category] || {};
    var allowed = fromRule.allowed_next;
    _clearPaletteHighlight();
    if (allowed === null || allowed === undefined) {
        // utility: 모든 카테고리 연결 가능
        document.querySelectorAll('.palette-item').forEach(function (el) {
            el.classList.add('connectable');
        });
        return;
    }
    document.querySelectorAll('.palette-item').forEach(function (el) {
        var cat = el.getAttribute('data-category');
        if (cat && (allowed.indexOf(cat) !== -1 || cat === 'utility')) {
            el.classList.add('connectable');
        }
    });
}

function _clearPaletteHighlight() {
    document.querySelectorAll('.palette-item.connectable').forEach(function (el) {
        el.classList.remove('connectable');
    });
}
if (typeof registerStreamLangRefresher === 'function') {
  registerStreamLangRefresher(function() {
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
    if (typeof DXStream !== 'undefined' && DXStream.S && DXStream.S.currentPage && typeof DXStream.nav === 'function') {
      DXStream.nav(DXStream.S.currentPage);
    }
  });
}
