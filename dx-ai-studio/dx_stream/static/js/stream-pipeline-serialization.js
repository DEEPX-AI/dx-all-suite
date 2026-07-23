/**
 * DX Stream Pipeline — 직렬화 & 히스토리 모듈
 * gst-launch 미리보기, 프리셋 로드, 히스토리(undo/redo), 노드 조작(복사/붙여넣기/삭제)
 */

function _updateCommandPreview() {
    var el = DXStream.$('pipeline-command-output');
    if (!el) return;
    var st = DXStream._pipeState;
    if (st.nodes.length === 0) {
        _setCommandPreviewText(el, 'gst-launch-1.0 ...', true);
        return;
    }

    // 토폴로지 정렬 (BFS) → gst-launch 문자열 생성
    var inDeg = {};
    st.nodes.forEach(function (n) { inDeg[n.id] = 0; });
    st.edges.forEach(function (e) { inDeg[e.to] = (inDeg[e.to] || 0) + 1; });

    var queue = [];
    st.nodes.forEach(function (n) { if (inDeg[n.id] === 0) queue.push(n.id); });

    var ordered = [];
    while (queue.length > 0) {
        var cur = queue.shift();
        ordered.push(cur);
        st.edges.forEach(function (e) {
            if (e.from === cur) {
                inDeg[e.to]--;
                if (inDeg[e.to] === 0) queue.push(e.to);
            }
        });
    }
    // 정렬 안 된 노드도 추가 (고립 노드)
    st.nodes.forEach(function (n) {
        if (ordered.indexOf(n.id) === -1) ordered.push(n.id);
    });

    var nodeMap = {};
    st.nodes.forEach(function (n) { nodeMap[n.id] = n; });

    // 엣지 연결 set
    var edgeSet = {};
    st.edges.forEach(function (e) { edgeSet[e.from + '->' + e.to] = true; });

    var parts = [];
    for (var i = 0; i < ordered.length; i++) {
        var n = nodeMap[ordered[i]];
        if (!n) continue;
        var seg = n.type.toLowerCase();
        // 속성 추가
        if (n.properties) {
            var propParts = [];
            Object.keys(n.properties).forEach(function (k) {
                var v = n.properties[k];
                if (v !== '' && v != null) {
                    var sv = String(v);
                    if (sv.indexOf(' ') !== -1) sv = '"' + sv + '"';
                    propParts.push(k + '=' + sv);
                }
            });
            if (propParts.length > 0) seg += ' ' + propParts.join(' ');
        }
        parts.push(seg);
        // 다음 노드와 연결?
        if (i < ordered.length - 1) {
            var nextId = ordered[i + 1];
            if (edgeSet[n.id + '->' + nextId]) {
                parts.push('!');
            } else {
                parts.push(' ');
            }
        }
    }
    var cmd = 'gst-launch-1.0 ' + parts.join(' ').replace(/ {2,}/g, '  ');
    _setCommandPreviewText(el, cmd, false);
}

DXStream.loadPreset = async function (demoId) {
    var demos = await DXStream.api('/api/demos');
    if (demos.error || !Array.isArray(demos)) {
        DXStream.toast(T('Failed to load presets'), 'error');
        return;
    }
    var demo = demos.find(function (d) { return d.id === demoId; });
    if (!demo) {
        DXStream.toast(T('Preset not found'), 'error');
        return;
    }

    var st = DXStream._pipeState;
    st.nodes = [];
    st.edges = [];
    st.selectedNode = null;
    st.selectedNodes = [];
    st._nextId = 1;
    var topology = _demoToNodes(demo);
    var startX = 60, startY = 100, gapX = 200;

    if (!topology.linear && topology.nodes) {
        // 분기 토폴로지: 노드와 엣지를 직접 배치
        var posMap = {};
        topology.nodes.forEach(function (tn, i) {
            var node = {
                id: tn.id || ('n' + st._nextId++),
                type: tn.type,
                name: tn.type,
                category: tn.category || 'utility',
                x: tn.x != null ? tn.x : startX + (i % 6) * gapX,
                y: tn.y != null ? tn.y : startY + Math.floor(i / 6) * 140,
                properties: tn.props || {},
            };
            posMap[tn.id] = node.id;
            st.nodes.push(node);
        });
        topology.edges.forEach(function (e) {
            var srcId = posMap[e[0]] || e[0];
            var dstId = posMap[e[1]] || e[1];
            st.edges.push({
                id: 'e' + st._nextId++,
                from: srcId,
                to: dstId,
            });
        });
    } else {
        // 선형 토폴로지: steps 배열 사용
        var steps = topology.steps || topology;
        steps.forEach(function (step, i) {
            var node = {
                id: 'n' + st._nextId++,
                type: step.type,
                name: step.type,
                category: step.category || 'utility',
                x: startX + i * gapX,
                y: startY,
                properties: step.props || {},
            };
            st.nodes.push(node);
            if (i > 0) {
                st.edges.push({
                    id: 'e' + st._nextId++,
                    from: st.nodes[i - 1].id,
                    to: node.id,
                });
            }
        });
    }

    _updateElementCount();
    DXStream.pipelineFitView();
    DXStream.toast(T('Preset loaded: ') + (demo.name_ko || demo.name_en), 'success');
};

function _demoToNodes(demo) {
    var a = DXStream._pipeAssets;
    // 멀티소스 데모 (Demo 8: 4 sources → compositor)
    if (demo.id === 8 || demo.pipeline_type === 'multi_source') {
        return _demoMultiNodes(demo);
    }
    // 2차 분기 데모 (Demo 10: tee → 2 branches → DxGather)
    if (demo.id === 10 || demo.pipeline_type === 'secondary') {
        return _demoSecondaryNodes(demo);
    }

    // config-type 데모: config-file-path 기반 프로퍼티
    if (demo.pipeline_type === 'config' && demo.config_dir) {
        var cfgBase = demo.config_dir;
        var nodes = [
            { type: 'urisourcebin', category: 'source', props: { uri: demo.default_video || '' } },
            { type: 'decodebin', category: 'utility', props: {} },
            { type: 'DxPreprocess', category: 'preprocess', props: { 'config-file-path': cfgBase + '/preprocess_config.json' } },
            { type: 'DxInfer', category: 'inference', props: { 'config-file-path': cfgBase + '/inference_config.json' } },
            { type: 'DxPostprocess', category: 'postprocess', props: { 'config-file-path': cfgBase + '/postprocess_config.json' } },
            { type: 'DxOsd', category: 'visualization', props: {} },
        ];
        return { linear: true, steps: nodes };
    }

    // tracking-config 데모 (demo 7): config-file-path + DxTracker
    if (demo.pipeline_type === 'tracking' && demo.config_dir) {
        var cfgBase2 = demo.config_dir;
        var nodes2 = [
            { type: 'urisourcebin', category: 'source', props: { uri: demo.default_video || '' } },
            { type: 'decodebin', category: 'utility', props: {} },
            { type: 'DxPreprocess', category: 'preprocess', props: { 'config-file-path': cfgBase2 + '/preprocess_config.json' } },
            { type: 'DxInfer', category: 'inference', props: { 'config-file-path': cfgBase2 + '/inference_config.json' } },
            { type: 'DxPostprocess', category: 'postprocess', props: { 'config-file-path': cfgBase2 + '/postprocess_config.json' } },
            { type: 'DxTracker', category: 'tracking', props: { 'config-file-path': 'tracker_config.json' } },
            { type: 'DxOsd', category: 'visualization', props: {} },
        ];
        return { linear: true, steps: nodes2 };
    }

    // 기본 선형 파이프라인 패턴 (standard 타입)
    var ppProps = {};
    if (demo.postproc_lib) ppProps['library-file-path'] = demo.postproc_lib;
    if (demo.postproc_func) ppProps['function-name'] = demo.postproc_func;
    var inferProps = {};
    if (demo.model) {
        inferProps['model-path'] = (a && a.models_dir) ? a.models_dir + '/' + demo.model : demo.model;
    }
    if (demo.preprocess_id != null) {
        inferProps['preprocess-id'] = demo.preprocess_id;
        inferProps['inference-id'] = 1;
    }
    var preprocProps = {};
    if (demo.preprocess_id != null) preprocProps['preprocess-id'] = demo.preprocess_id;
    if (demo.resize) {
        preprocProps['resize-width'] = demo.resize[0];
        preprocProps['resize-height'] = demo.resize[1];
    }
    var nodes = [
        { type: 'urisourcebin', category: 'source', props: { uri: demo.default_video || '' } },
        { type: 'decodebin', category: 'utility', props: {} },
        { type: 'DxPreprocess', category: 'preprocess', props: preprocProps },
        { type: 'DxInfer', category: 'inference', props: inferProps },
        { type: 'DxPostprocess', category: 'postprocess', props: ppProps },
        { type: 'DxOsd', category: 'visualization', props: {} },
    ];
    if (demo.pipeline_type === 'tracking') {
        nodes.splice(5, 0, { type: 'DxTracker', category: 'tracking', props: {} });
    }
    return { linear: true, steps: nodes };
}

function _demoMultiNodes(demo) {
    // Demo 8: 4×(source→decode→preprocess→infer→postprocess→osd→scale) → compositor
    var cfgDir = demo.config_dir || 'YoloV5S_PPU';
    var streamNodes = [];
    var streamEdges = [];
    var compNode = { id: 'comp', type: 'compositor', category: 'utility', props: {} };

    for (var i = 0; i < 4; i++) {
        var prefix = 's' + i + '_';
        var nodes = [
            { id: prefix + 'src', type: 'urisourcebin', category: 'source', props: { uri: '' }, x: 60, y: 60 + i * 120 },
            { id: prefix + 'dec', type: 'decodebin', category: 'utility', props: {}, x: 220, y: 60 + i * 120 },
            { id: prefix + 'pre', type: 'DxPreprocess', category: 'preprocess', props: { 'config-file-path': cfgDir + '/preprocess_config.json' }, x: 380, y: 60 + i * 120 },
            { id: prefix + 'inf', type: 'DxInfer', category: 'inference', props: { 'config-file-path': cfgDir + '/inference_config.json' }, x: 540, y: 60 + i * 120 },
            { id: prefix + 'pp', type: 'DxPostprocess', category: 'postprocess', props: { 'config-file-path': cfgDir + '/postprocess_config.json' }, x: 700, y: 60 + i * 120 },
            { id: prefix + 'osd', type: 'DxOsd', category: 'visualization', props: {}, x: 860, y: 60 + i * 120 },
            { id: prefix + 'sc', type: 'DxScale', category: 'utility', props: { width: 640, height: 360 }, x: 1020, y: 60 + i * 120 },
        ];
        streamNodes = streamNodes.concat(nodes);
        streamEdges.push([prefix + 'src', prefix + 'dec']);
        streamEdges.push([prefix + 'dec', prefix + 'pre']);
        streamEdges.push([prefix + 'pre', prefix + 'inf']);
        streamEdges.push([prefix + 'inf', prefix + 'pp']);
        streamEdges.push([prefix + 'pp', prefix + 'osd']);
        streamEdges.push([prefix + 'osd', prefix + 'sc']);
        streamEdges.push([prefix + 'sc', 'comp']);
    }

    compNode.x = 1180;
    compNode.y = 240;
    streamNodes.push(compNode);

    return {
        linear: false,
        nodes: streamNodes,
        edges: streamEdges,
    };
}

function _demoSecondaryNodes(demo) {
    // Demo 10: source→decode→preprocess→infer→postprocess→tracker→tee
    //          tee→branch1(preprocess→infer→postprocess)→gather
    //          tee→branch2(preprocess→infer→postprocess)→gather
    //          gather→osd
    var cfgDir = demo.config_dir || 'YoloV5S_PPU';
    var a = DXStream._pipeAssets;
    return {
        linear: false,
        nodes: [
            { id: 'src', type: 'urisourcebin', category: 'source', props: { uri: demo.default_video || '' }, x: 60, y: 200 },
            { id: 'dec', type: 'decodebin', category: 'utility', props: {}, x: 220, y: 200 },
            { id: 'pre0', type: 'DxPreprocess', category: 'preprocess', props: { 'config-file-path': cfgDir + '/preprocess_config.json' }, x: 380, y: 200 },
            { id: 'inf0', type: 'DxInfer', category: 'inference', props: { 'config-file-path': cfgDir + '/inference_config.json' }, x: 540, y: 200 },
            { id: 'pp0', type: 'DxPostprocess', category: 'postprocess', props: { 'config-file-path': cfgDir + '/postprocess_config.json' }, x: 700, y: 200 },
            { id: 'trk', type: 'DxTracker', category: 'tracking', props: { 'config-file-path': 'tracker_config.json' }, x: 860, y: 200 },
            { id: 'tee1', type: 'tee', category: 'utility', props: {}, x: 1020, y: 200 },
            { id: 'pre1', type: 'DxPreprocess', category: 'preprocess', props: { 'preprocess-id': 2, 'resize-width': 224, 'resize-height': 224, 'secondary-mode': true, 'interval': 5 }, x: 1180, y: 100 },
            { id: 'inf1', type: 'DxInfer', category: 'inference', props: { 'preprocess-id': 2, 'inference-id': 2, 'secondary-mode': true, 'model-path': (a && a.models_dir ? a.models_dir + '/' : '') + 'EfficientNet_Lite0.dxnn' }, x: 1340, y: 100 },
            { id: 'pp1', type: 'DxPostprocess', category: 'postprocess', props: { 'inference-id': 2, 'secondary-mode': true }, x: 1500, y: 100 },
            { id: 'pre2', type: 'DxPreprocess', category: 'preprocess', props: { 'preprocess-id': 3, 'resize-width': 640, 'resize-height': 640, 'secondary-mode': true, 'target-class-id': 0, 'interval': 5 }, x: 1180, y: 300 },
            { id: 'inf2', type: 'DxInfer', category: 'inference', props: { 'preprocess-id': 3, 'inference-id': 3, 'secondary-mode': true, 'model-path': (a && a.models_dir ? a.models_dir + '/' : '') + 'SCRFD500M.dxnn' }, x: 1340, y: 300 },
            { id: 'pp2', type: 'DxPostprocess', category: 'postprocess', props: { 'inference-id': 3, 'secondary-mode': true }, x: 1500, y: 300 },
            { id: 'gath', type: 'DxGather', category: 'utility', props: {}, x: 1660, y: 200 },
            { id: 'osd', type: 'DxOsd', category: 'visualization', props: {}, x: 1820, y: 200 },
        ],
        edges: [
            ['src', 'dec'], ['dec', 'pre0'], ['pre0', 'inf0'], ['inf0', 'pp0'],
            ['pp0', 'trk'], ['trk', 'tee1'],
            ['tee1', 'pre1'], ['pre1', 'inf1'], ['inf1', 'pp1'], ['pp1', 'gath'],
            ['tee1', 'pre2'], ['pre2', 'inf2'], ['inf2', 'pp2'], ['pp2', 'gath'],
            ['gath', 'osd'],
        ],
    };
}

function _pushHistory() {
    var st = DXStream._pipeState;
    var snap = JSON.stringify({ nodes: st.nodes, edges: st.edges, _nextId: st._nextId });
    // 현재 위치 이후 미래 히스토리 삭제
    st._history = st._history.slice(0, st._historyIdx + 1);
    st._history.push(snap);
    if (st._history.length > 50) st._history.shift(); // 메모리 제한
    st._historyIdx = st._history.length - 1;
    _scheduleDraftSave(snap);
    _scheduleCommandPreview();
}

function _restoreHistory() {
    var st = DXStream._pipeState;
    if (st._historyIdx < 0 || st._historyIdx >= st._history.length) return;
    var snap = JSON.parse(st._history[st._historyIdx]);
    st.nodes = snap.nodes;
    st.edges = snap.edges;
    st._nextId = snap._nextId || st._nextId;
    st.selectedNode = null;
    st.selectedNodes = [];
    _hidePropertyPanel();
    _updateElementCount();
    _refreshCanvas();
    _scheduleCommandPreview();
}

DXStream._undo = function () {
    var st = DXStream._pipeState;
    if (st._historyIdx <= 0) return;
    st._historyIdx--;
    _restoreHistory();
    DXStream.toast(T('Undo'), 'info');
};

DXStream._redo = function () {
    var st = DXStream._pipeState;
    if (st._historyIdx >= st._history.length - 1) return;
    st._historyIdx++;
    _restoreHistory();
    DXStream.toast(T('Redo'), 'info');
};

DXStream._deleteSelectedNode = function () {
    var st = DXStream._pipeState;
    if (st.selectedNodes.length === 0 && !st.selectedNode) return;

    var targets = st.selectedNodes.length > 0 ? st.selectedNodes.slice() : [st.selectedNode];
    var label = targets.length > 1
        ? T('Delete ' + targets.length + ' nodes?', targets.length + '개 노드를 삭제하시겠습니까?')
        : T('Delete selected node?');

    DXStream.confirmModal(T('Delete Node'), label).then(function (ok) {
        if (!ok) return;
        var ids = {};
        targets.forEach(function (id) { ids[id] = true; });
        st.nodes = st.nodes.filter(function (n) { return !ids[n.id]; });
        st.edges = st.edges.filter(function (ed) { return !ids[ed.from] && !ids[ed.to]; });
        st.selectedNode = null;
        st.selectedNodes = [];
        _hidePropertyPanel();
        _pushHistory();
        _updateElementCount();
        _refreshCanvas();
    });
};

DXStream._deselectNode = function () {
    DXStream._pipeState.selectedNode = null;
    DXStream._pipeState.selectedNodes = [];
    DXStream._pipeState.selectedEdge = null;
    _hidePropertyPanel();
    _refreshCanvas();
};

DXStream._deselectAll = function () {
    DXStream._pipeState.selectedNode = null;
    DXStream._pipeState.selectedNodes = [];
    DXStream._pipeState.selectedEdge = null;
    _hidePropertyPanel();
    _refreshCanvas();
};

DXStream._deleteSelectedEdge = function () {
    var st = DXStream._pipeState;
    if (!st.selectedEdge) return;
    st.edges = st.edges.filter(function (ed) { return ed.id !== st.selectedEdge; });
    st.selectedEdge = null;
    _pushHistory();
    _refreshCanvas();
    DXStream.toast(T('Edge deleted'), 'info');
};

DXStream._copyNodes = function () {
    var st = DXStream._pipeState;
    if (st.selectedNodes.length === 0) {
        DXStream.toast(T('No nodes selected'), 'info');
        return;
    }
    var selSet = {};
    st.selectedNodes.forEach(function (id) { selSet[id] = true; });

    st._clipboard = st.selectedNodes.map(function (nid) {
        var n = st.nodes.find(function (nd) { return nd.id === nid; });
        return n ? JSON.parse(JSON.stringify(n)) : null;
    }).filter(Boolean);

    // 선택 노드 간의 내부 엣지도 복사
    st._clipboardEdges = st.edges.filter(function (ed) {
        return selSet[ed.from] && selSet[ed.to];
    }).map(function (ed) { return JSON.parse(JSON.stringify(ed)); });

    DXStream.toast(T('Copied ' + st._clipboard.length + ' nodes', st._clipboard.length + '개 노드 복사됨'), 'success');
};

DXStream._pasteNodes = function () {
    var st = DXStream._pipeState;
    if (!st._clipboard || st._clipboard.length === 0) {
        DXStream.toast(T('Nothing to paste'), 'info');
        return;
    }
    var offset = 40;
    var idMap = {};
    st.selectedNodes = [];

    st._clipboard.forEach(function (orig) {
        var newId = 'n' + st._nextId++;
        idMap[orig.id] = newId;
        var newNode = JSON.parse(JSON.stringify(orig));
        newNode.id = newId;
        newNode.x += offset;
        newNode.y += offset;
        st.nodes.push(newNode);
        st.selectedNodes.push(newId);
    });

    // 내부 엣지 재연결
    if (st._clipboardEdges) {
        st._clipboardEdges.forEach(function (orig) {
            var newFrom = idMap[orig.from];
            var newTo = idMap[orig.to];
            if (newFrom && newTo) {
                st.edges.push({
                    id: 'e' + st._nextId++,
                    from: newFrom,
                    to: newTo,
                });
            }
        });
    }

    st.selectedNode = st.selectedNodes[0] || null;
    _pushHistory();
    _updateElementCount();
    _refreshCanvas();
    DXStream.toast(T('Pasted ' + st._clipboard.length + ' nodes', st._clipboard.length + '개 노드 붙여넣기'), 'success');
};
