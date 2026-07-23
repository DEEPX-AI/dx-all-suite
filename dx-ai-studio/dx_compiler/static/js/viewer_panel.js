// viewer_panel.js — Manages the embedded model viewer panel with phase tabs
(function() {
    'use strict';

    var graphCache = {};
    var activePhase = null;
    var zoomPanState = null;  // single zoom/pan state (like standalone viewer)
    var collapsedStates = {};  // per-phase subgraph collapse state
    var zoomStates = {};       // per-phase zoom/pan transform { x, y, scale }
    var lastMeta = null;       // last renderGraph() return value (nodePositions, nodeMap, etc.)
    var selectedNode = null;
    var currentQxnnJobId = null;
    var currentDiagnosisReportUrl = null;
    var currentQxnnPath = null;
    var currentQxnnSuggestedOutputDir = null;

    var _hasGraphAssets = (typeof GraphViewer !== 'undefined') && (typeof GraphRenderer !== 'undefined');
    var truncateId = _hasGraphAssets ? GraphViewer.truncateId : function(s) { return s; };
    var findNodeById = _hasGraphAssets ? GraphViewer.findNodeById : function() { return null; };
    var CATEGORY_COLORS = _hasGraphAssets ? GraphViewer.CATEGORY_COLORS : {};

    function _normalizeCollapsed(v) {
        if (!v) return new Set();
        if (v instanceof Set) return v;
        if (Array.isArray(v)) return new Set(v);
        try { return new Set(Array.from(v)); } catch (e) { return new Set(); }
    }

    var searchTimer = null;
    var searchDropdownIndex = -1;
    var lastSearchCount = null;

    function _getSvgEl() { return document.getElementById('viewer-svg'); }
    function _getZoomPan() { return zoomPanState; }

    function tr(key) {
        return typeof T === 'function' ? T(key) : key;
    }

    function phaseLabel(phase) {
        var labels = {
            input: 'Input',
            prepared: 'Prepared',
            surgery: 'Surgery',
            partition: 'Partition',
            dxnn: 'DXNN',
        };
        return tr(labels[phase] || phase || '');
    }

    function renderWaitingEmpty(phase) {
        var empty = document.getElementById('viewer-empty');
        if (!empty) return;
        empty.style.display = '';
        empty.innerHTML =
            '<span class="viewer-empty-icon">⏳</span>' +
            '<span>' + tr('Waiting for {phase} model...').replace('{phase}', phaseLabel(phase)) + '</span>';
    }

    function renderDefaultEmpty() {
        var empty = document.getElementById('viewer-empty');
        if (!empty) return;
        empty.style.display = '';
        empty.innerHTML =
            '<span class="viewer-empty-icon">⬡</span>' +
            '<span>' + tr('Load a model to visualize') + '</span>';
    }

    // Deep-link handoff notice (e.g. from dx_modelzoo when the model's ONNX artifact
    // isn't downloaded locally, so there's nothing to hand this viewer to load). Kept
    // separate from renderDefaultEmpty() so a language switch (refreshLanguage) can
    // re-render it in the new language instead of reverting to the generic message.
    var deepLinkNotice = null;

    var DEEP_LINK_NOTICE_TEXT = {
        onnx_missing: 'This model\'s ONNX file isn\'t downloaded yet. Download or compile it in DX Model Zoo, then reopen this graph.',
    };

    function renderDeepLinkNotice(noticeCode) {
        var empty = document.getElementById('viewer-empty');
        if (!empty) return;
        var text = DEEP_LINK_NOTICE_TEXT[noticeCode];
        if (!text) return renderDefaultEmpty();
        empty.style.display = '';
        empty.innerHTML =
            '<span class="viewer-empty-icon">⬇️</span>' +
            '<span>' + tr(text) + '</span>';
    }

    function showNodeInfo(nodeData) {
        selectedNode = nodeData;
        var graphData = activePhase ? graphCache[activePhase] : null;
        var html = GraphViewer.renderNodeDetailHTML(nodeData, graphData, { clickable: true });
        GraphViewer.showDetailSection('node-info', 'node-info-content', html);
    }

    function hideNodeInfo() {
        selectedNode = null;
        if (typeof GraphViewer !== 'undefined' && GraphViewer.hideDetailSection) {
            GraphViewer.hideDetailSection('node-info', 'node-info-content');
            return;
        }
        var section = document.getElementById('node-info');
        var content = document.getElementById('node-info-content');
        if (content) content.innerHTML = '';
        if (section) section.style.display = 'none';
    }

    function showSubgraphInfo(subgraphId) {
        selectedNode = null;
        var graphData = activePhase ? graphCache[activePhase] : null;
        if (!graphData) return;
        var html = GraphViewer.renderSubgraphDetailHTML(subgraphId, graphData, { clickable: true });
        GraphViewer.showDetailSection('node-info', 'node-info-content', html);
    }

    function highlightCpuReasonNodes(nodeIds) {
        GraphViewer.highlightCpuReasonNodes(_getSvgEl(), nodeIds);
    }

    function highlightAndZoomToNode(nodeId) {
        GraphViewer.highlightAndZoomToNode(_getSvgEl(), _getZoomPan(), nodeId);
    }

    function _ensureNodeVisible(nodeId, graphData) {
        var svg = _getSvgEl();
        if (!svg || !graphData) return;
        if (lastMeta && lastMeta.nodePositions && !lastMeta.nodePositions.get(nodeId)) {
            var node = findNodeById(nodeId, graphData);
            if (node && node.subgraph_id) {
                var collapsed = collapsedStates[activePhase];
                if (collapsed && collapsed.has(node.subgraph_id)) {
                    collapsed.delete(node.subgraph_id);
                    var savedTransform = zoomPanState ? zoomPanState.getTransform() : null;
                    GraphRenderer.clearGraph(svg);
                    var meta = GraphRenderer.renderGraph(svg, graphData, {
                        collapsedSubgraphs: collapsed,
                    });
                    if (meta) {
                        collapsedStates[activePhase] = _normalizeCollapsed(meta.collapsedSubgraphs);
                    }
                    lastMeta = meta;
                    zoomPanState = GraphRenderer.setupZoomPan(svg);
                    updateStatusBar(activePhase, meta);
                    if (savedTransform && zoomPanState) {
                        zoomPanState.setTransform(savedTransform.x, savedTransform.y, savedTransform.scale);
                    }
                }
            }
        }
    }

    function showTensorDetailPopup(tensorName) {
        var graphData = activePhase ? graphCache[activePhase] : null;
        if (!graphData) return;
        var currentNodeId = selectedNode ? selectedNode.id : null;
        var previousNode = selectedNode;
        selectedNode = null;

        // Find the zoom target (the node at the other end of the tensor)
        var zoomTargetId = null;
        try {
            if (GraphViewer.findTensorEndpointNode) {
                zoomTargetId = GraphViewer.findTensorEndpointNode(tensorName, graphData, currentNodeId);
                if (zoomTargetId) {
                    _ensureNodeVisible(zoomTargetId, graphData);
                }
            }
        } catch (e) { console.warn('[TensorZoom] findEndpoint error:', e); }

        // Show tensor detail (highlight + detail panel)
        GraphViewer.showTensorDetail({
            svgEl: _getSvgEl(),
            tensorName: tensorName,
            graphData: graphData,
            contextNodeId: currentNodeId,
            sectionId: 'node-info',
            contentId: 'node-info-content',
            onBack: function() {
                if (previousNode) showNodeInfo(previousNode);
                else hideNodeInfo();
            },
        });

        // Zoom to the target node — inline logic with setTransform for reliability
        if (zoomTargetId && zoomPanState) {
            var _tid = zoomTargetId;
            setTimeout(function() {
                try {
                    var svg = _getSvgEl();
                    var zp = zoomPanState;
                    if (!svg || !zp || !zp.setTransform) {
                        console.warn('[TensorZoom] no svg/zoomPan:', !!svg, !!zp);
                        return;
                    }
                    var gc = svg.querySelector('#graph-content');
                    if (!gc) { console.warn('[TensorZoom] no #graph-content'); return; }
                    var ng = gc.querySelector('.node-group[data-node-id="' + _tid + '"]');
                    if (!ng) { console.warn('[TensorZoom] node not found:', _tid); return; }
                    var px = parseFloat(ng.getAttribute('data-x'));
                    var py = parseFloat(ng.getAttribute('data-y'));
                    var pw = parseFloat(ng.getAttribute('data-w')) || 160;
                    var ph = parseFloat(ng.getAttribute('data-h')) || 50;
                    if (isNaN(px) || isNaN(py)) {
                        console.warn('[TensorZoom] NaN coords:', px, py);
                        return;
                    }
                    var svgRect = svg.getBoundingClientRect();
                    var svgW = svgRect.width || 800;
                    var svgH = svgRect.height || 600;
                    var t = zp.getTransform();
                    var scale = Math.max(t.scale, 120 / pw);
                    var cx = px + pw / 2;
                    var cy = py + ph / 2;
                    var tx = svgW * 0.35 - cx * scale;
                    var ty = svgH * 0.25 - cy * scale;
                    console.log('[TensorZoom] zooming to', _tid, 'tx='+tx.toFixed(0), 'ty='+ty.toFixed(0), 'scale='+scale.toFixed(2));
                    zp.setTransform(tx, ty, scale);
                } catch (e) { console.warn('[TensorZoom] error:', e); }
            }, 50);
        } else if (zoomTargetId) {
            console.warn('[TensorZoom] no zoomPanState');
        } else {
            console.warn('[TensorZoom] no zoomTargetId for tensor:', tensorName);
        }
    }

    function navigateToNode(nodeId) {
        var svg = _getSvgEl();
        var graphData = activePhase ? graphCache[activePhase] : null;
        if (!svg || !graphData) return;

        // If node is inside a collapsed subgraph, expand it first
        _ensureNodeVisible(nodeId, graphData);

        GraphViewer.navigateToNode({
            svgEl: svg,
            zoomPan: _getZoomPan(),
            nodeId: nodeId,
            graphData: graphData,
            onNodeSelected: function(node) {
                var evt = new CustomEvent('node-selected', {
                    bubbles: true,
                    detail: { node: node, selected: true },
                });
                svg.dispatchEvent(evt);
            },
        });
    }

    function init() {
        document.querySelectorAll('.viewer-tab').forEach(function(tab) {
            tab.addEventListener('click', function() {
                if (this.classList.contains('disabled')) return;
                switchTab(this.dataset.phase);
            });
        });

        var zoomIn = document.getElementById('zoom-in');
        var zoomOut = document.getElementById('zoom-out');
        var zoomFit = document.getElementById('zoom-fit');
        if (zoomIn) zoomIn.addEventListener('click', function() { zoom(1.2); });
        if (zoomOut) zoomOut.addEventListener('click', function() { zoom(0.8); });
        if (zoomFit) zoomFit.addEventListener('click', function() { fitGraph(); });

        var collapseAllBtn = document.getElementById('collapse-all');
        var expandAllBtn = document.getElementById('expand-all');
        if (collapseAllBtn) collapseAllBtn.addEventListener('click', function() { collapseAll(); });
        if (expandAllBtn) expandAllBtn.addEventListener('click', function() { expandAll(); });

        // Node/edge/subgraph interaction events from GraphRenderer
        var svg = document.getElementById('viewer-svg');
        if (svg) {
            svg.addEventListener('node-selected', function(e) {
                var detail = e.detail;
                GraphRenderer.clearAllEdgeHighlights(svg);
                if (detail && detail.selected && detail.node) {
                    if (nodeSelectionMode && nodeSelectionType) {
                        toggleNodeSelection(detail.node);
                    } else {
                        showNodeInfo(detail.node);
                    }
                } else {
                    if (!nodeSelectionMode) hideNodeInfo();
                }
            });
            svg.addEventListener('edge-selected', function(e) {
                var detail = e.detail;
                if (detail && detail.tensorName) {
                    showTensorDetailPopup(detail.tensorName);
                }
            });
            svg.addEventListener('zoom-changed', function() {
                updateZoomDisplay();
            });
            svg.addEventListener('subgraph-selected', function(e) {
                var detail = e.detail;
                if (!detail || !detail.subgraphId) return;
                showSubgraphInfo(detail.subgraphId);
            });
            svg.addEventListener('subgraph-toggled', function(e) {
                var detail = e.detail;
                if (!detail || !detail.subgraphId || !activePhase) return;

                if (!collapsedStates[activePhase]) {
                    collapsedStates[activePhase] = new Set();
                }
                // Toggle
                if (collapsedStates[activePhase].has(detail.subgraphId)) {
                    collapsedStates[activePhase].delete(detail.subgraphId);
                } else {
                    collapsedStates[activePhase].add(detail.subgraphId);
                }
                // Save current transform
                var savedTransform = zoomPanState
                    ? zoomPanState.getTransform() : null;

                // Re-render with updated collapsed state
                GraphRenderer.clearGraph(svg);
                var meta = GraphRenderer.renderGraph(svg, graphCache[activePhase], {
                    collapsedSubgraphs: collapsedStates[activePhase],
                });
                if (meta) {
                    collapsedStates[activePhase] = _normalizeCollapsed(meta.collapsedSubgraphs);
                }
                lastMeta = meta;
                zoomPanState = GraphRenderer.setupZoomPan(svg);
                updateStatusBar(activePhase, meta);
                hideNodeInfo();

                // Restore transform
                if (savedTransform && zoomPanState) {
                    zoomPanState.setTransform(
                        savedTransform.x, savedTransform.y, savedTransform.scale);
                }
            });
        }

        // Sidebar click delegation (shared)
        var infoContent = document.getElementById('node-info-content');
        if (typeof GraphViewer !== 'undefined') {
            GraphViewer.setupSidebarClickDelegation(infoContent, {
                highlightAndZoom: highlightAndZoomToNode,
                highlightCpuReasons: highlightCpuReasonNodes,
                navigateNode: navigateToNode,
                showTensorDetail: showTensorDetailPopup,
            });
        }

        // Search, explorer, keyboard shortcuts
        setupSearch();
        setupExplorer();
        setupKeyboardShortcuts();

        // Deep-link: /compiler/?viewer_path=<absolute .onnx path>  → auto-parse + render
        // the model's graph on the "input" tab. Lets other Studio modules (dx_app, modelzoo)
        // hand off an ONNX model and land the user straight on its graph, replacing DX-TRON.
        // ?viewer_notice=<code> is used instead when the caller has no artifact to hand off
        // (e.g. modelzoo's ONNX isn't downloaded locally) so the empty state explains why,
        // rather than showing the generic "Load a model to visualize" message.
        try {
            var _params = new URLSearchParams(window.location.search);
            var _dl = _params.get('viewer_path');
            if (_dl) {
                loadModel('input', _dl);
            } else {
                var _notice = _params.get('viewer_notice');
                if (_notice) {
                    deepLinkNotice = _notice;
                    renderDeepLinkNotice(_notice);
                }
            }
        } catch (e) { /* no-op: deep-link is best-effort */ }
    }

    function switchTab(phase) {
        if (activePhase === phase) return;
        if (zoomPanState && activePhase) {
            zoomStates[activePhase] = zoomPanState.getTransform();
        }
        activePhase = phase;

        document.querySelectorAll('.viewer-tab').forEach(function(t) {
            t.classList.toggle('active', t.dataset.phase === phase);
        });

        renderPhase(phase);
    }

    function renderPhase(phase) {
        hideNodeInfo();
        clearSearch();
        updateQxnnViewVisibility(phase);
        var svg = document.getElementById('viewer-svg');
        var empty = document.getElementById('viewer-empty');

        // Enable/disable collapse/expand buttons depending on phase
        updateCollapseExpandButtons(phase);

        if (phase === 'qxnn') {
            if (svg && window.GraphRenderer) GraphRenderer.clearGraph(svg);
            if (empty) empty.style.display = 'none';
            updateStatusBar(phase, null);
            populateExplorer(null);
            return;
        }

        if (graphCache[phase]) {
            if (empty) empty.style.display = 'none';
            if (window.GraphRenderer) {
                GraphRenderer.clearGraph(svg);
                var renderOpts = {};
                if (collapsedStates[phase]) {
                    renderOpts.collapsedSubgraphs = collapsedStates[phase];
                }
                var meta = GraphRenderer.renderGraph(svg, graphCache[phase], renderOpts);
                if (meta) {
                    collapsedStates[phase] = _normalizeCollapsed(meta.collapsedSubgraphs);
                }
                lastMeta = meta;
                zoomPanState = GraphRenderer.setupZoomPan(svg);
                if (zoomPanState) {
                    var saved = zoomStates[phase];
                    if (saved) {
                        zoomPanState.setTransform(saved.x, saved.y, saved.scale);
                    } else {
                        requestAnimationFrame(function() {
                            zoomPanState.fitToView();
                        });
                    }
                }
                updateStatusBar(phase, meta);
                populateExplorer(graphCache[phase]);
            }
        } else {
            if (svg && window.GraphRenderer) GraphRenderer.clearGraph(svg);
            renderWaitingEmpty(phase);
            updateStatusBar(phase, null);
            populateExplorer(null);
        }
    }

    function updateStatusBar(phase, meta) {
        var gd = graphCache[phase];
        var sn = document.getElementById('status-nodes');
        var se = document.getElementById('status-edges');
        if (sn) sn.textContent = tr('Nodes') + ': ' + (gd ? (gd.nodes || []).length : 0);
        if (se) se.textContent = tr('Edges') + ': ' + (gd ? (gd.edges || []).length : 0);
    }

    function updateZoomDisplay() {
        var sz = document.getElementById('status-zoom');
        if (!sz || !zoomPanState) return;
        var t = zoomPanState.getTransform();
        sz.textContent = tr('Zoom') + ': ' + Math.round(t.scale * 100) + '%';
    }

    function zoom(factor) {
        if (!zoomPanState) return;
        var t = zoomPanState.getTransform();
        zoomPanState.setTransform(t.x, t.y, t.scale * factor);
        updateZoomDisplay();
    }

    function fitGraph() {
        if (!zoomPanState) return;
        zoomPanState.fitToView();
        updateZoomDisplay();
    }

    function collapseAll() {
        if (!activePhase) return;
        var graphData = graphCache[activePhase];
        if (!graphData) return;
        var subgraphs = graphData.subgraphs || [];
        if (!collapsedStates[activePhase]) collapsedStates[activePhase] = new Set();
        // Add all subgraph ids
        subgraphs.forEach(function(s) { if (s && s.id) collapsedStates[activePhase].add(s.id); });

        var svg = _getSvgEl();
        var savedTransform = zoomPanState ? zoomPanState.getTransform() : null;
        GraphRenderer.clearGraph(svg);
        var meta = GraphRenderer.renderGraph(svg, graphData, { collapsedSubgraphs: collapsedStates[activePhase] });
        if (meta) collapsedStates[activePhase] = _normalizeCollapsed(meta.collapsedSubgraphs);
        lastMeta = meta;
        zoomPanState = GraphRenderer.setupZoomPan(svg);
        updateStatusBar(activePhase, meta);
        hideNodeInfo();
        // After collapse, fit the graph to view so focus remains correct
        // (prefer fitting over restoring the previous transform when layout changed)
        if (zoomPanState && typeof zoomPanState.fitToView === 'function') {
            requestAnimationFrame(function() {
                try { zoomPanState.fitToView(); } catch(e) { /* ignore */ }
                updateZoomDisplay();
            });
        }
    }

    function expandAll() {
        if (!activePhase) return;
        var graphData = graphCache[activePhase];
        if (!graphData) return;
        // Clear collapsed set
        collapsedStates[activePhase] = new Set();

        var svg = _getSvgEl();
        var savedTransform = zoomPanState ? zoomPanState.getTransform() : null;
        GraphRenderer.clearGraph(svg);
        var meta = GraphRenderer.renderGraph(svg, graphData, { collapsedSubgraphs: collapsedStates[activePhase] });
        if (meta) collapsedStates[activePhase] = _normalizeCollapsed(meta.collapsedSubgraphs);
        lastMeta = meta;
        zoomPanState = GraphRenderer.setupZoomPan(svg);
        updateStatusBar(activePhase, meta);
        hideNodeInfo();
        // After expand, fit the graph to view so focus remains correct
        if (zoomPanState && typeof zoomPanState.fitToView === 'function') {
            requestAnimationFrame(function() {
                try { zoomPanState.fitToView(); } catch(e) { /* ignore */ }
                updateZoomDisplay();
            });
        }
    }

    function loadModel(phase, modelPath) {
        fetch('/viewer/parse', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: modelPath })
        })
        .then(function(r) { return r.json(); })
        .then(function(graphData) {
            if (graphData.error) {
                console.error('Viewer parse error:', graphData.error);
                return;
            }
            graphCache[phase] = graphData;
            var tab = document.querySelector('.viewer-tab[data-phase="' + phase + '"]');
            if (tab) tab.classList.remove('disabled');
            // Only auto-switch for the input model; intermediate phases just enable the tab
            if (phase === 'input') switchTab(phase);
        })
        .catch(function(err) {
            console.error('Failed to load model for phase ' + phase + ':', err);
        });
    }

    var PHASE_MAP = {
        'SURGERY': 'surgery',
        'PARTITION': 'partition',
        'DXNN': 'dxnn',
        'prepared': 'prepared',
    };

    // Update collapse/expand button enabled state
    function updateCollapseExpandButtons(phase) {
        var collapseAllBtn = document.getElementById('collapse-all');
        var expandAllBtn = document.getElementById('expand-all');
        var enabled = false;
        if (phase && (phase === 'partition' || phase === 'dxnn')) {
            // Only enable when the phase has a loaded graph
            enabled = !!graphCache[phase];
        }
        [collapseAllBtn, expandAllBtn].forEach(function(btn) {
            if (!btn) return;
            btn.disabled = !enabled;
            btn.setAttribute('aria-disabled', !enabled ? 'true' : 'false');
            if (!enabled) btn.classList.add('muted'); else btn.classList.remove('muted');
        });
    }

    function handleModelReady(data) {
        var tabPhase = PHASE_MAP[data.phase];
        if (!tabPhase) return;

        if (data.graph) {
            // In-memory graph data from GUI callback (no file saved)
            graphCache[tabPhase] = data.graph;
            var tab = document.querySelector('.viewer-tab[data-phase="' + tabPhase + '"]');
            if (tab) tab.classList.remove('disabled');
            if (tabPhase === 'prepared') switchTab('prepared');
        } else if (data.path) {
            loadModel(tabPhase, data.path);
        }
    }

    function handleQxnnAvailable(jobId, data) {
        currentQxnnJobId = jobId;
        var hasDiagnosisReport = !!(data && data.diagnosis_report_available);
        var diagnosisRequested = !!(data && data.quant_diagnosis_requested);
        currentDiagnosisReportUrl = hasDiagnosisReport
            ? ((data && data.diagnosis_report_url) || ('/compile/' + encodeURIComponent(jobId) + '/quant-diagnosis/report'))
            : null;
        currentQxnnPath = (data && data.qxnn_path) || null;
        currentQxnnSuggestedOutputDir = (data && data.suggested_output_dir) || null;
        var tab = document.querySelector('.viewer-tab[data-phase="qxnn"]');
        if (tab && (hasDiagnosisReport || diagnosisRequested)) tab.classList.remove('disabled');
        if (activePhase === 'qxnn') updateQxnnViewVisibility('qxnn');
    }

    function renderResumeActionBar() {
        var view = document.getElementById('quant-diagnosis-view');
        if (!view) return;
        var bar = document.getElementById('diag-resume-actionbar');
        if (!currentQxnnPath) {
            if (bar) bar.style.display = 'none';
            return;
        }
        if (!bar) {
            bar = document.createElement('div');
            bar.id = 'diag-resume-actionbar';
            bar.className = 'diagnosis-actionbar';
            bar.innerHTML =
                '<span class="da-label">' + tr('Quantization Diagnosis') + '</span>' +
                '<span class="da-qxnn" id="diag-resume-qxnn"></span>' +
                '<span class="da-spacer"></span>' +
                '<button type="button" class="diag-send-btn" id="diag-send-btn" ' +
                'title="' + tr('Prefill the Resume panel with this QXNN path') + '">' +
                tr('Resume from this QXNN') + ' &rarr;</button>';
            view.insertBefore(bar, view.firstChild);
            bar.querySelector('#diag-send-btn').addEventListener('click', sendQxnnToResumePanel);
        }
        bar.style.display = '';
        var nameEl = bar.querySelector('#diag-resume-qxnn');
        if (nameEl) {
            var parts = String(currentQxnnPath).split('/');
            nameEl.textContent = parts[parts.length - 1] || currentQxnnPath;
            nameEl.title = currentQxnnPath;
        }
    }

    function sendQxnnToResumePanel() {
        var pathEl = document.getElementById('qxnn_path');
        var outEl = document.getElementById('resume_output_dir');
        if (!pathEl || !outEl) return;
        pathEl.value = currentQxnnPath || '';
        if (currentQxnnSuggestedOutputDir) outEl.value = currentQxnnSuggestedOutputDir;
        pathEl.classList.add('prefilled');
        outEl.classList.add('prefilled');
        if (window.setResumeCardOpen) window.setResumeCardOpen(true);
        var card = document.getElementById('resume-card');
        if (card) {
            card.classList.remove('flash');
            void card.offsetWidth;
            card.classList.add('flash');
            card.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }

    function resetQxnnState() {
        currentQxnnJobId = null;
        currentDiagnosisReportUrl = null;
        currentQxnnPath = null;
        currentQxnnSuggestedOutputDir = null;
        var panel = document.getElementById('viewer-panel');
        if (panel) panel.classList.remove('diagnosis-mode');
        var view = document.getElementById('quant-diagnosis-view');
        if (view) view.style.display = 'none';
        var actionbar = document.getElementById('diag-resume-actionbar');
        if (actionbar) actionbar.style.display = 'none';
        var frame = document.getElementById('quant-diagnosis-frame');
        if (frame) {
            frame.style.display = 'none';
            frame.removeAttribute('src');
        }
        var unavailable = document.getElementById('quant-diagnosis-unavailable');
        if (unavailable) unavailable.style.display = 'none';
    }

    function updateQxnnViewVisibility(phase) {
        var view = document.getElementById('quant-diagnosis-view');
        var panel = document.getElementById('viewer-panel');
        var active = phase === 'qxnn';
        if (panel) panel.classList.toggle('diagnosis-mode', active);
        if (!view) return;
        view.style.display = active ? 'flex' : 'none';
        if (active) { renderResumeActionBar(); renderQxnnReport(); }
    }

    function renderQxnnReport() {
        var frame = document.getElementById('quant-diagnosis-frame');
        var unavailable = document.getElementById('quant-diagnosis-unavailable');
        var hasReport = !!currentDiagnosisReportUrl;
        if (frame) {
            if (hasReport) {
                if (frame.getAttribute('src') !== currentDiagnosisReportUrl) {
                    frame.src = currentDiagnosisReportUrl;
                }
                frame.style.display = '';
            } else {
                frame.style.display = 'none';
                frame.removeAttribute('src');
            }
        }
        if (unavailable) {
            unavailable.style.display = hasReport ? 'none' : 'flex';
            if (!hasReport) {
                unavailable.textContent = currentQxnnJobId
                    ? tr('Diagnosis unavailable: no diagnosis_report.html was generated. The compile may have succeeded — a diagnosis failure does not fail the compile.')
                    : tr('Quantization diagnosis report unavailable.');
            }
        }
    }

    function resetViewer() {
        // Ensure buttons are disabled when viewer is reset
        updateCollapseExpandButtons(null);
        exitNodeSelectionMode();
        resetQxnnState();
        clearSearch();
        graphCache = {};
        collapsedStates = {};
        zoomStates = {};
        activePhase = null;
        deepLinkNotice = null;
        document.querySelectorAll('.viewer-tab').forEach(function(t) {
            t.classList.remove('active');
            if (t.dataset.phase !== 'input') t.classList.add('disabled');
        });
        var inputTab = document.querySelector('.viewer-tab[data-phase="input"]');
        if (inputTab) inputTab.classList.add('active');
        var svg = document.getElementById('viewer-svg');
        var empty = document.getElementById('viewer-empty');
        if (svg && window.GraphRenderer) GraphRenderer.clearGraph(svg);
        renderDefaultEmpty();
        hideNodeInfo();
        populateExplorer(null);
    }

    var nodeSelectionMode = false;
    var nodeSelectionType = null;
    var selectedInputNodes = [];
    var selectedOutputNodes = [];
    var currentJobId = null;
    var excludedNodesSet = new Set();
    var NODE_SELECTION_UNSUPPORTED_KEY = 'node_selection_unsupported_subprocess';
    var NODE_SELECTION_UNSUPPORTED_MESSAGE = 'Node selection is unavailable in subprocess compile mode. Compilation will continue without range selection.';

    function _warningMessage(data, key, fallback) {
        var warnings = data && Array.isArray(data.warnings) ? data.warnings : [];
        for (var i = 0; i < warnings.length; i++) {
            if (warnings[i] && warnings[i].key === key) {
                return warnings[i].message || fallback;
            }
        }
        return fallback;
    }

    function applyCompilerCapabilities(data) {
        if (!data || !data.capabilities) return;
        var nodeSelection = document.getElementById('node-selection');
        if (!nodeSelection) return;
        var unsupported = data.capabilities.node_selection === false;
        var message = _warningMessage(data, NODE_SELECTION_UNSUPPORTED_KEY, NODE_SELECTION_UNSUPPORTED_MESSAGE);
        var label = document.querySelector('label[for="node-selection"]');
        var tip = nodeSelection.parentElement ? nodeSelection.parentElement.querySelector('.help-tip') : null;
        var warn = document.getElementById('auto-detect-warning-wiz') || document.getElementById('auto-detect-warning');
        if (unsupported) {
            nodeSelection.checked = false;
            nodeSelection.disabled = true;
            nodeSelection.title = tr(message);
            if (label) label.title = tr(message);
            if (tip) {
                tip.setAttribute('data-tip', tr(message));
                tip.setAttribute('title', tr(message));
            }
            if (warn) {
                warn.style.display = '';
                warn.textContent = tr(message);
            }
            if (nodeSelectionMode) exitNodeSelectionMode();
        } else {
            nodeSelection.disabled = false;
            nodeSelection.title = '';
            if (label) label.title = '';
        }
    }

    function enterNodeSelectionMode(data, jobId) {
        if (nodeSelectionMode) return;
        nodeSelectionMode = true;
        currentJobId = jobId;
        selectedInputNodes = [];
        selectedOutputNodes = [];
        excludedNodesSet = new Set();
        nodeSelectionType = 'input';
        hideNodeInfo();
        var svg = document.getElementById('viewer-svg');
        if (svg) svg.style.cursor = 'crosshair';
        showNodeSelectionUI();
    }

    function exitNodeSelectionMode() {
        nodeSelectionMode = false;
        nodeSelectionType = null;
        currentJobId = null;
        selectedInputNodes = [];
        selectedOutputNodes = [];
        excludedNodesSet = new Set();
        hideNodeSelectionUI();
    }

    function showNodeSelectionUI() {
        // Toolbar overlay on top of viewer canvas
        var canvasWrap = document.getElementById('viewer-canvas-wrap');
        if (canvasWrap) {
            var toolbar = document.createElement('div');
            toolbar.id = 'ns-toolbar';
            toolbar.innerHTML =
                '<button id="ns-input-btn" class="ns-toolbar-btn ns-toolbar-input active">' +
                '● ' + tr('Set Input Nodes') + '</button>' +
                '<button id="ns-output-btn" class="ns-toolbar-btn ns-toolbar-output">' +
                '● ' + tr('Set Output Nodes') + '</button>';
            canvasWrap.appendChild(toolbar);

            document.getElementById('ns-input-btn').addEventListener('click', function() {
                setNodeSelectionType('input');
            });
            document.getElementById('ns-output-btn').addEventListener('click', function() {
                setNodeSelectionType('output');
            });
        }

        // Right sidebar: hide original content, show selection panel
        var sidebar = document.getElementById('node-info');
        if (sidebar) {
            sidebar.style.display = '';
            // Hide original children instead of destroying them
            Array.from(sidebar.children).forEach(function(child) {
                child.style.display = 'none';
            });
            var panel = document.createElement('div');
            panel.id = 'node-selection-panel';
            panel.innerHTML =
                '<h3>' + tr('Compile Range') + '</h3>' +
                '<div style="padding: 0 16px 16px;">' +
                '  <div id="ns-input-list">' +
                '    <div class="ns-list-header ns-list-header-input">' + tr('Input Nodes') + '</div>' +
                '    <div id="ns-input-items"><div class="ns-empty">' + tr('None selected') + '</div></div>' +
                '  </div>' +
                '  <div id="ns-output-list" style="margin-top:12px;">' +
                '    <div class="ns-list-header ns-list-header-output">' + tr('Output Nodes') + '</div>' +
                '    <div id="ns-output-items"><div class="ns-empty">' + tr('None selected') + '</div></div>' +
                '  </div>' +
                '  <button id="ns-calc-btn" class="ns-action-btn ns-calc-btn">' +
                '    ' + tr('Calculate Range') + '</button>' +
                '  <div id="ns-range-info" class="ns-range-info"></div>' +
                '  <button id="ns-resume-btn" class="ns-action-btn ns-resume-btn">' +
                '    ' + tr('▶ Resume Compilation') + '</button>' +
                '</div>';
            sidebar.appendChild(panel);

            document.getElementById('ns-calc-btn').addEventListener('click', calculateExcludeRange);
            document.getElementById('ns-resume-btn').addEventListener('click', resumeCompilation);
        }
    }

    function hideNodeSelectionUI() {
        var toolbar = document.getElementById('ns-toolbar');
        if (toolbar) toolbar.remove();
        var panel = document.getElementById('node-selection-panel');
        if (panel) panel.remove();
        // Restore original sidebar children that were hidden
        var sidebar = document.getElementById('node-info');
        if (sidebar) {
            Array.from(sidebar.children).forEach(function(child) {
                child.style.display = '';
            });
            sidebar.style.display = 'none';
        }
        var svg = document.getElementById('viewer-svg');
        if (svg) {
            svg.querySelectorAll('.node-group').forEach(function(g) {
                g.classList.remove('ns-input-selected', 'ns-output-selected',
                                   'ns-included', 'ns-excluded', 'selected');
            });
            svg.style.cursor = '';
        }
    }

    function setNodeSelectionType(type) {
        nodeSelectionType = type;
        var inputBtn = document.getElementById('ns-input-btn');
        var outputBtn = document.getElementById('ns-output-btn');
        if (!inputBtn || !outputBtn) return;
        inputBtn.classList.toggle('active', type === 'input');
        outputBtn.classList.toggle('active', type === 'output');
        var svg = document.getElementById('viewer-svg');
        if (svg) svg.style.cursor = 'crosshair';
    }

    function toggleNodeSelection(node) {
        var name = node.id;
        if (!name) return;

        var targetList, otherList;
        if (nodeSelectionType === 'input') {
            targetList = selectedInputNodes;
            otherList = selectedOutputNodes;
        } else {
            targetList = selectedOutputNodes;
            otherList = selectedInputNodes;
        }

        var idx = targetList.indexOf(name);
        if (idx >= 0) {
            targetList.splice(idx, 1);
        } else {
            var otherIdx = otherList.indexOf(name);
            if (otherIdx >= 0) otherList.splice(otherIdx, 1);
            targetList.push(name);
        }

        updateNodeSelectionVisuals();
        renderNodeSelectionLists();
    }

    function updateNodeSelectionVisuals() {
        var svg = document.getElementById('viewer-svg');
        if (!svg) return;

        svg.querySelectorAll('.node-group').forEach(function(g) {
            g.classList.remove('ns-input-selected', 'ns-output-selected',
                               'ns-included', 'ns-excluded');
        });

        selectedInputNodes.forEach(function(name) {
            var g = svg.querySelector('.node-group[data-node-id="' + name + '"]');
            if (g) {
                g.classList.add('ns-input-selected');
                g.classList.add('ns-included');
            }
        });

        selectedOutputNodes.forEach(function(name) {
            var g = svg.querySelector('.node-group[data-node-id="' + name + '"]');
            if (g) {
                g.classList.add('ns-output-selected');
                g.classList.add('ns-included');
            }
        });

        if (excludedNodesSet.size > 0) {
            svg.querySelectorAll('.node-group').forEach(function(g) {
                var nodeName = g.getAttribute('data-node-id');
                if (nodeName && !g.classList.contains('ns-input-selected') &&
                    !g.classList.contains('ns-output-selected')) {
                    if (excludedNodesSet.has(nodeName)) {
                        g.classList.add('ns-excluded');
                    } else {
                        g.classList.add('ns-included');
                    }
                }
            });
        }
    }

    function renderNodeSelectionLists() {
        var inputItems = document.getElementById('ns-input-items');
        var outputItems = document.getElementById('ns-output-items');
        if (!inputItems || !outputItems) return;

        inputItems.innerHTML = selectedInputNodes.length === 0
            ? '<div class="ns-empty">' + tr('None selected') + '</div>'
            : selectedInputNodes.map(function(n) {
                return '<div class="ns-item ns-item-input">' +
                    '<span>' + n + '</span>' +
                    '<button onclick="ViewerPanel._removeNode(\'input\',\'' +
                    n.replace(/'/g, "\\'") + '\')">&times;</button></div>';
              }).join('');

        outputItems.innerHTML = selectedOutputNodes.length === 0
            ? '<div class="ns-empty">' + tr('None selected') + '</div>'
            : selectedOutputNodes.map(function(n) {
                return '<div class="ns-item ns-item-output">' +
                    '<span>' + n + '</span>' +
                    '<button onclick="ViewerPanel._removeNode(\'output\',\'' +
                    n.replace(/'/g, "\\'") + '\')">&times;</button></div>';
              }).join('');
    }

    function removeNode(type, name) {
        var list = type === 'input' ? selectedInputNodes : selectedOutputNodes;
        var idx = list.indexOf(name);
        if (idx >= 0) list.splice(idx, 1);
        updateNodeSelectionVisuals();
        renderNodeSelectionLists();
    }

    function calculateExcludeRange() {
        if (!currentJobId) return;
        var btn = document.getElementById('ns-calc-btn');
        if (btn) { btn.textContent = tr('Calculating...'); btn.disabled = true; }

        fetch('/compile/' + currentJobId + '/calculate-exclude', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                input_nodes: selectedInputNodes,
                output_nodes: selectedOutputNodes,
            })
        })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.error) {
                var info = document.getElementById('ns-range-info');
                if (info) info.textContent = 'Error: ' + data.error;
                return;
            }
            excludedNodesSet = new Set(data.excluded_nodes);
            updateNodeSelectionVisuals();
            var info = document.getElementById('ns-range-info');
            if (info) {
                info.textContent = data.included_count + '/' + data.total_count + ' ' + tr('nodes included') +
                    ', ' + data.excluded_nodes.length + ' ' + tr('excluded');
            }
        })
        .catch(function(err) {
            console.error('Calculate exclude failed:', err);
        })
        .finally(function() {
            if (btn) { btn.textContent = tr('Calculate Range'); btn.disabled = false; }
        });
    }

    function resumeCompilation() {
        if (!currentJobId) return;
        var btn = document.getElementById('ns-resume-btn');
        if (btn) { btn.textContent = tr('Resuming...'); btn.disabled = true; }

        fetch('/compile/' + currentJobId + '/resume', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                input_nodes: selectedInputNodes,
                output_nodes: selectedOutputNodes,
            })
        })
        .then(function(r) { return r.json(); })
        .then(function() {
            exitNodeSelectionMode();
        })
        .catch(function(err) {
            console.error('Resume failed:', err);
            if (btn) { btn.textContent = tr('▶ Resume Compilation'); btn.disabled = false; }
        });
    }


    function setupSearch() {
        var input = document.getElementById('search-input');
        var dropdown = document.getElementById('search-dropdown');
        if (!input) return;

        // Allow wheel scroll inside dropdown without triggering graph pan/zoom
        if (dropdown) {
            dropdown.addEventListener('wheel', function(e) { e.stopPropagation(); }, { passive: true });
        }

        input.addEventListener('input', function() {
            if (searchTimer) clearTimeout(searchTimer);
            searchTimer = setTimeout(function() {
                performSearch(input.value);
            }, 150);
        });

        input.addEventListener('keydown', function(e) {
            if (!dropdown) return;
            var items = dropdown.querySelectorAll('.search-dropdown-item');
            if (items.length === 0) return;

            if (e.key === 'ArrowDown') {
                e.preventDefault();
                searchDropdownIndex = Math.min(searchDropdownIndex + 1, items.length - 1);
                updateDropdownActive(items);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                searchDropdownIndex = Math.max(searchDropdownIndex - 1, 0);
                updateDropdownActive(items);
            } else if (e.key === 'Enter') {
                e.preventDefault();
                if (searchDropdownIndex >= 0 && searchDropdownIndex < items.length) {
                    var selItem = items[searchDropdownIndex];
                    var tensorName = selItem.getAttribute('data-tensor-name');
                    var nodeId = selItem.getAttribute('data-node-id');
                    clearSearch();
                    if (tensorName) {
                        highlightTensorFromSearch(tensorName);
                    } else if (nodeId) {
                        navigateToNode(nodeId);
                    }
                }
            }
        });

        input.addEventListener('focus', function() {
            if (input.value.trim()) performSearch(input.value);
        });

        document.addEventListener('click', function(e) {
            if (!e.target.closest('.search-wrapper')) {
                hideSearchDropdown();
            }
        });
    }

    function updateDropdownActive(items) {
        for (var i = 0; i < items.length; i++) {
            items[i].classList.toggle('active', i === searchDropdownIndex);
        }
        if (searchDropdownIndex >= 0 && items[searchDropdownIndex]) {
            items[searchDropdownIndex].scrollIntoView({ block: 'nearest' });
        }
    }

    function performSearch(query) {
        var svg = document.getElementById('viewer-svg');
        if (!svg) return;
        var graphContent = svg.querySelector('#graph-content');

        // Clear previous visual highlights
        if (graphContent) {
            var nodeGroups = graphContent.querySelectorAll('.node-group');
            for (var i = 0; i < nodeGroups.length; i++) {
                nodeGroups[i].classList.remove('search-match');
            }
        }
        GraphRenderer.clearAllEdgeHighlights(svg);

        var q = query.trim().toLowerCase();
        if (!q) {
            updateStatusSearchCount(null);
            hideSearchDropdown();
            return;
        }

        var graphData = activePhase ? graphCache[activePhase] : null;
        var nodes = graphData ? (graphData.nodes || []) : [];

        // ── Node matches (data-driven, works even when subgraphs collapsed) ──
        var matches = [];
        for (var n = 0; n < nodes.length; n++) {
            var node = nodes[n];
            var opLower = (node.op_type || '').toLowerCase();
            var idLower = (node.id || '').toLowerCase();
            var score = 0;

            if (opLower === q)                    { score = 100; }
            else if (idLower === q)               { score = 98; }
            else if (opLower.indexOf(q) === 0)    { score = 80; }
            else if (idLower.indexOf(q) === 0)    { score = 78; }
            else if (opLower.indexOf(q) !== -1)   { score = 60; }
            else if (idLower.indexOf(q) !== -1)   { score = 58; }

            if (score > 0) {
                matches.push({ type: 'node', node: node, score: score });
                // Highlight in SVG if visible
                if (graphContent) {
                    var ng = graphContent.querySelector('.node-group[data-node-id="' + node.id + '"]');
                    if (ng) ng.classList.add('search-match');
                }
            }
        }

        var tensorMatches = [];
        if (graphData) {
            var tensorInfo = graphData.tensor_info || {};
            for (var tname in tensorInfo) {
                var tLower = tname.toLowerCase();
                var tScore = 0;
                if (tLower === q)                   { tScore = 99; }
                else if (tLower.indexOf(q) === 0)   { tScore = 79; }
                else if (tLower.indexOf(q) !== -1)  { tScore = 59; }
                if (tScore > 0) {
                    tensorMatches.push({ type: 'tensor', tensorName: tname, info: tensorInfo[tname], score: tScore });
                }
            }
        }

        // Merge and sort by score
        var combined = matches.concat(tensorMatches);
        combined.sort(function (a, b) {
            if (b.score !== a.score) return b.score - a.score;
            var aName = a.type === 'tensor' ? a.tensorName : (a.node.id || '');
            var bName = b.type === 'tensor' ? b.tensorName : (b.node.id || '');
            return aName.localeCompare(bName);
        });

        updateStatusSearchCount(combined.length);
        showSearchDropdown(combined.slice(0, 50));
    }

    function showSearchDropdown(matches) {
        var dropdown = document.getElementById('search-dropdown');
        if (!dropdown) return;
        dropdown.innerHTML = '';
        searchDropdownIndex = -1;

        if (matches.length === 0) { hideSearchDropdown(); return; }

        for (var i = 0; i < matches.length; i++) {
            var m = matches[i];
            var item = document.createElement('div');
            item.className = 'search-dropdown-item';

            if (m.type === 'tensor') {
                item.setAttribute('data-tensor-name', m.tensorName);

                var tBadge = document.createElement('span');
                tBadge.className = 'sdi-badge';
                tBadge.style.background = '#e05265';
                tBadge.textContent = 'tensor';

                var tName = document.createElement('span');
                tName.className = 'sdi-name';
                tName.textContent = m.tensorName.length > 36 ? '…' + m.tensorName.slice(-34) : m.tensorName;

                item.appendChild(tBadge);
                item.appendChild(tName);

                (function(tensorName) {
                    item.addEventListener('click', function() {
                        clearSearch();
                        highlightTensorFromSearch(tensorName);
                    });
                })(m.tensorName);
            } else {
                item.setAttribute('data-node-id', m.node.id);

                var cat = m.node.category || 'other';
                var color = CATEGORY_COLORS[cat] || CATEGORY_COLORS.other;

                var badge = document.createElement('span');
                badge.className = 'sdi-badge';
                badge.style.background = color;
                badge.textContent = (m.node.op_type || 'Unknown').substring(0, 12);

                var nameSpan = document.createElement('span');
                nameSpan.className = 'sdi-name';
                var nid = m.node.id;
                nameSpan.textContent = nid.length > 36 ? '…' + nid.slice(-34) : nid;

                item.appendChild(badge);
                item.appendChild(nameSpan);

                (function(nodeId) {
                    item.addEventListener('click', function() {
                        clearSearch();
                        navigateToNode(nodeId);
                    });
                })(m.node.id);
            }

            dropdown.appendChild(item);
        }

        dropdown.classList.add('visible');
    }

    function hideSearchDropdown() {
        var dropdown = document.getElementById('search-dropdown');
        if (dropdown) {
            dropdown.classList.remove('visible');
            dropdown.innerHTML = '';
            searchDropdownIndex = -1;
        }
    }

    function clearSearch() {
        var input = document.getElementById('search-input');
        if (input) input.value = '';
        performSearch('');
        hideSearchDropdown();
    }

    function highlightTensorFromSearch(tensorName) {
        var svg = _getSvgEl();
        var graphData = activePhase ? graphCache[activePhase] : null;
        if (!svg || !graphData) return;

        // Zoom to an endpoint node of this tensor
        var zoomTargetId = null;
        try {
            if (GraphViewer.findTensorEndpointNode) {
                zoomTargetId = GraphViewer.findTensorEndpointNode(tensorName, graphData, null);
            }
        } catch (e) { /* ignore */ }

        // Expand collapsed subgraph FIRST (may re-render the graph)
        if (zoomTargetId) {
            _ensureNodeVisible(zoomTargetId, graphData);
        }

        // Apply highlight AFTER any re-render
        GraphRenderer.clearAllEdgeHighlights(svg);
        GraphRenderer.highlightEdgesByTensor(svg, tensorName, true, null);

        if (zoomTargetId && zoomPanState) {
            var _tid = zoomTargetId;
            setTimeout(function() {
                try {
                    var gc = svg.querySelector('#graph-content');
                    if (!gc) return;
                    var ng = gc.querySelector('.node-group[data-node-id="' + _tid + '"]');
                    if (!ng) return;
                    var px = parseFloat(ng.getAttribute('data-x'));
                    var py = parseFloat(ng.getAttribute('data-y'));
                    var pw = parseFloat(ng.getAttribute('data-w')) || 160;
                    var ph = parseFloat(ng.getAttribute('data-h')) || 50;
                    if (isNaN(px) || isNaN(py)) return;
                    var svgRect = svg.getBoundingClientRect();
                    var svgW = svgRect.width || 800;
                    var svgH = svgRect.height || 600;
                    var t = zoomPanState.getTransform();
                    var scale = Math.max(t.scale, 120 / pw);
                    var cx = px + pw / 2;
                    var cy = py + ph / 2;
                    var tx = svgW * 0.35 - cx * scale;
                    var ty = svgH * 0.25 - cy * scale;
                    zoomPanState.setTransform(tx, ty, scale);
                } catch (e) { /* ignore */ }
            }, 50);
        }
    }

    function updateStatusSearchCount(count) {
        lastSearchCount = count;
        var sn = document.getElementById('status-nodes');
        if (!sn) return;
        var gd = activePhase ? graphCache[activePhase] : null;
        var totalNodes = gd ? (gd.nodes || []).length : 0;
        if (count !== null && count !== undefined) {
            sn.textContent = tr('Nodes') + ': ' + totalNodes + ' (' + count + ' ' + tr('matched') + ')';
        } else {
            sn.textContent = tr('Nodes') + ': ' + totalNodes;
        }
    }


    function setupExplorer() {
        var toggleBtn = document.getElementById('explorer-toggle');
        var closeBtn = document.getElementById('explorer-close');
        var panel = document.getElementById('explorer-panel');
        if (!toggleBtn || !panel) return;

        toggleBtn.addEventListener('click', function() {
            panel.classList.add('open');
            toggleBtn.style.display = 'none';
        });
        if (closeBtn) {
            closeBtn.addEventListener('click', function() {
                panel.classList.remove('open');
                toggleBtn.style.display = '';
            });
        }
    }

    function populateExplorer(graphData) {
        var content = document.getElementById('explorer-content');
        if (!content) return;
        content.innerHTML = '';

        if (!graphData) {
            content.innerHTML = '<div class="explorer-placeholder">' + tr('Load a model to explore nodes') + '</div>';
            return;
        }

        var nodes = graphData.nodes || [];
        if (nodes.length === 0) {
            content.innerHTML = '<div class="explorer-placeholder">' + tr('No nodes in graph') + '</div>';
            return;
        }

        // Build category → opType → nodes tree
        var tree = {};
        for (var i = 0; i < nodes.length; i++) {
            var n = nodes[i];
            var cat = n.category || 'other';
            if (!tree[cat]) tree[cat] = {};
            var op = n.op_type || 'Unknown';
            if (!tree[cat][op]) tree[cat][op] = [];
            tree[cat][op].push(n);
        }

        var CAT_CONFIG = {
            compute:       { color: '#4f46e5', label: 'Compute' },
            memory:        { color: '#64748b', label: 'Memory' },
            activation:    { color: '#059669', label: 'Activation' },
            normalization: { color: '#0d9488', label: 'Normalization' },
            pooling:       { color: '#7c3aed', label: 'Pooling' },
            elementwise:   { color: '#d97706', label: 'Elementwise' },
            quantize:      { color: '#ca8a04', label: 'Quantize' },
            other:         { color: '#6b7280', label: 'Other' },
        };

        var catOrder = ['compute', 'memory', 'activation', 'normalization', 'pooling', 'elementwise', 'quantize', 'other'];
        var sortedCats = catOrder.filter(function(c) { return tree[c]; });
        for (var c in tree) {
            if (sortedCats.indexOf(c) === -1) sortedCats.push(c);
        }

        for (var ci = 0; ci < sortedCats.length; ci++) {
            var catKey = sortedCats[ci];
            var opTypes = tree[catKey];
            var cfg = CAT_CONFIG[catKey] || CAT_CONFIG.other;

            var catTotal = 0;
            for (var opCount in opTypes) catTotal += opTypes[opCount].length;

            var catDiv = document.createElement('div');
            catDiv.className = 'explorer-category';

            var catHeader = document.createElement('div');
            catHeader.className = 'explorer-category-header';
            catHeader.innerHTML =
                '<span class="cat-chevron">▶</span>' +
                '<span class="cat-dot" style="background:' + cfg.color + '"></span>' +
                '<span class="cat-label">' + tr(cfg.label) + '</span>' +
                '<span class="cat-count">' + catTotal + '</span>';

            var catBody = document.createElement('div');
            catBody.className = 'explorer-category-body';

            (function(header, body) {
                header.addEventListener('click', function() {
                    header.classList.toggle('expanded');
                    body.classList.toggle('expanded');
                });
            })(catHeader, catBody);

            var opKeys = Object.keys(opTypes).sort();

            for (var oi = 0; oi < opKeys.length; oi++) {
                var opKey = opKeys[oi];
                var opNodes = opTypes[opKey];

                var opDiv = document.createElement('div');
                opDiv.className = 'explorer-optype';

                var opHeader = document.createElement('div');
                opHeader.className = 'explorer-optype-header';
                opHeader.innerHTML =
                    '<span class="op-chevron">▶</span>' +
                    '<span class="op-label">' + opKey + '</span>' +
                    '<span class="op-count">' + opNodes.length + '</span>';

                var opBody = document.createElement('div');
                opBody.className = 'explorer-optype-body';

                (function(header, body) {
                    header.addEventListener('click', function() {
                        header.classList.toggle('expanded');
                        body.classList.toggle('expanded');
                    });
                })(opHeader, opBody);

                for (var ni = 0; ni < opNodes.length; ni++) {
                    var nodeItem = document.createElement('div');
                    nodeItem.className = 'explorer-node-item';
                    nodeItem.setAttribute('data-node-id', opNodes[ni].id);
                    var displayName = opNodes[ni].id;
                    if (displayName.length > 35) {
                        displayName = '…' + displayName.slice(-34);
                    }
                    nodeItem.textContent = displayName;
                    nodeItem.title = opNodes[ni].id;

                    (function(nodeId) {
                        nodeItem.addEventListener('click', function() {
                            var prev = content.querySelector('.explorer-node-item.active');
                            if (prev) prev.classList.remove('active');
                            this.classList.add('active');
                            navigateToNode(nodeId);
                        });
                    })(opNodes[ni].id);

                    opBody.appendChild(nodeItem);
                }

                opDiv.appendChild(opHeader);
                opDiv.appendChild(opBody);
                catBody.appendChild(opDiv);
            }

            catDiv.appendChild(catHeader);
            catDiv.appendChild(catBody);
            content.appendChild(catDiv);
        }
    }


    function setupKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            // Ctrl+F or Cmd+F → focus search
            if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
                var input = document.getElementById('search-input');
                if (input) {
                    e.preventDefault();
                    input.focus();
                    input.select();
                }
            }
            // Escape → clear search or hide node info
            if (e.key === 'Escape') {
                var input = document.getElementById('search-input');
                if (input && document.activeElement === input) {
                    clearSearch();
                    input.blur();
                } else {
                    hideNodeInfo();
                }
            }
            // Home or 0 → fit graph
            if (e.key === 'Home' || (e.key === '0' && !e.ctrlKey && !e.metaKey &&
                document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA')) {
                fitGraph();
            }
        });
    }

    window.ViewerPanel = {
        init: init,
        loadModel: loadModel,
        switchTab: switchTab,
        resetViewer: resetViewer,
        handleModelReady: handleModelReady,
        handleQxnnAvailable: handleQxnnAvailable,
        applyCompilerCapabilities: applyCompilerCapabilities,
        getActivePhase: function () { return activePhase; },
        zoom: zoom,
        enterNodeSelectionMode: enterNodeSelectionMode,
        exitNodeSelectionMode: exitNodeSelectionMode,
        _removeNode: removeNode,
        _refreshLanguage: refreshLanguage,
    };

    function refreshLanguage() {
        if (activePhase) {
            updateStatusBar(activePhase, lastMeta);
            updateZoomDisplay();
            if (!graphCache[activePhase]) {
                renderWaitingEmpty(activePhase);
            }
            populateExplorer(graphCache[activePhase] || null);
        } else if (deepLinkNotice) {
            renderDeepLinkNotice(deepLinkNotice);
            updateStatusBar(null, null);
            populateExplorer(null);
        } else {
            renderDefaultEmpty();
            updateStatusBar(null, null);
            populateExplorer(null);
        }
        if (lastSearchCount !== null) {
            updateStatusSearchCount(lastSearchCount);
        }
        if (nodeSelectionMode) {
            hideNodeSelectionUI();
            showNodeSelectionUI();
            setNodeSelectionType(nodeSelectionType);
            renderNodeSelectionLists();
            updateNodeSelectionVisuals();
        }
    }

    if (window.DXI18n && typeof DXI18n.onLangChange === 'function') {
        DXI18n.onLangChange(refreshLanguage);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
