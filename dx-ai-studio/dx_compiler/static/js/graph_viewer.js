/**
 * GraphViewer — shared utilities and node detail rendering for graph viewers.
 * Used by both the main app viewer and standalone model summary HTML.
 * Requires graph_renderer.js loaded before this script.
 */
(function () {
    'use strict';

    var CATEGORY_COLORS = {
        compute: '#4f46e5', memory: '#64748b', activation: '#059669',
        normalization: '#0d9488', pooling: '#7c3aed', elementwise: '#d97706',
        quantize: '#ca8a04', other: '#6b7280',
    };

    function escapeHtml(str) {
        var div = document.createElement('div');
        div.appendChild(document.createTextNode(String(str)));
        return div.innerHTML;
    }

    function _findNodeCpuReason(graphData, nodeId) {
        var subgraphs = graphData.subgraphs || [];
        for (var si = 0; si < subgraphs.length; si++) {
            var sg = subgraphs[si];
            if (!sg.cpu_reasons) continue;
            var nr = sg.cpu_reasons.node_reasons || {};
            if (nr[nodeId]) {
                var r = nr[nodeId];
                return r.detail || r.category || '';
            }
        }
        return '';
    }

    function formatValue(v) {
        if (v === null || v === undefined) return 'N/A';
        if (Array.isArray(v)) {
            if (v.length <= 8) return '[' + v.join(', ') + ']';
            return '[' + v.slice(0, 6).join(', ') + ', \u2026 (' + v.length + ' items)]';
        }
        if (typeof v === 'object') {
            try { return JSON.stringify(v, null, 1); } catch (_) { return String(v); }
        }
        if (typeof v === 'number') {
            return Number.isInteger(v) ? String(v) : v.toFixed(4).replace(/0+$/, '0');
        }
        return String(v);
    }

    function formatShape(shape) {
        if (!shape || !Array.isArray(shape)) return '';
        return '[' + shape.map(function(d) { return d === -1 ? '?' : d; }).join(', ') + ']';
    }

    function formatBytes(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
        return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
    }

    /**
     * Find tensor metadata (shape, dtype) from graph inputs, outputs, and params.
     * @param {string} tensorName - Name of the tensor to look up
     * @param {Object} graphData - Full graph data object
     * @returns {{shape: Array, dtype: string}|null} Tensor info or null if not found
     */
    function lookupTensorInfo(tensorName, graphData) {
        if (!graphData) return null;
        var ti = graphData.tensor_info;
        if (ti && ti[tensorName]) return ti[tensorName];
        var edges = graphData.edges || [];
        for (var i = 0; i < edges.length; i++) {
            if ((edges[i].from_output === tensorName || edges[i].to_input === tensorName) && edges[i].shape) {
                return { name: tensorName, shape: edges[i].shape, dtype: edges[i].dtype || null };
            }
        }
        var ios = (graphData.inputs || []).concat(graphData.outputs || []);
        for (var j = 0; j < ios.length; j++) {
            if (ios[j].name === tensorName) return ios[j];
        }
        var params = graphData.params || [];
        for (var p = 0; p < params.length; p++) {
            if (params[p].name === tensorName) return params[p];
        }
        return null;
    }

    /**
     * Render a single tensor info item as HTML.
     * @param {string} name - Tensor name
     * @param {object} graphData - Full graph data for lookup
     * @param {string} kind - 'tensor' | 'param' | 'output'
     * @param {boolean} isGraphInput - Whether this is a graph-level input
     * @param {object} [options] - { clickable: true }
     */
    function renderTensorItem(name, graphData, kind, isGraphInput, options) {
        var info = lookupTensorInfo(name, graphData);
        var cls = kind === 'param' ? 'info-tensor info-tensor-param' : 'info-tensor info-tensor-activation';
        var clickable = options && options.clickable !== false;
        var clickAttr = '';
        if (clickable && graphData) {
            cls += ' clickable';
            clickAttr = ' data-click-action="show-tensor-detail" data-click-target="' + escapeHtml(name) + '"';
        }

        var html = '<div class="' + cls + '"' + clickAttr + '>';
        html += '<div class="info-tensor-row1">';
        if (kind === 'param') html += '<span class="tensor-kind-badge param-badge">P</span>';
        else if (isGraphInput) html += '<span class="tensor-kind-badge input-badge">IN</span>';
        else html += '<span class="tensor-kind-badge tensor-badge">T</span>';
        html += '<span class="tensor-name">' + escapeHtml(name) + '</span>';
        if (clickAttr) html += '<span style="color:#94a3b8;font-size:10px;flex-shrink:0">\u2139</span>';
        html += '</div>';

        if (info && ((info.shape && info.shape.length > 0) || info.dtype)) {
            html += '<div class="info-tensor-row2">';
            if (info.shape && info.shape.length > 0) html += '<span class="tensor-shape">' + formatShape(info.shape) + '</span>';
            if (info.dtype) html += '<span class="tensor-dtype">' + escapeHtml(info.dtype) + '</span>';
            if (kind === 'param' && info.size_bytes) html += '<span class="tensor-size">' + formatBytes(info.size_bytes) + '</span>';
            html += '</div>';
        }
        html += '</div>';
        return html;
    }

    /**
     * Generate complete node detail HTML.
     * @param {object} node - Node data { id, op_type, category, device, inputs, outputs, attrs }
     * @param {object} graphData - Full graph data for tensor lookup
     * @param {object} [options] - { clickable: true, includeTitle: true }
     * @returns {string} HTML string
     */
    function renderNodeDetailHTML(node, graphData, options) {
        var opts = options || {};
        var catColor = CATEGORY_COLORS[node.category] || CATEGORY_COLORS.other;

        var paramSet = {};
        var graphInputSet = {};
        if (graphData) {
            var params = graphData.params || [];
            for (var pi = 0; pi < params.length; pi++) paramSet[params[pi].name] = true;
            var gInputs = graphData.inputs || [];
            for (var gi = 0; gi < gInputs.length; gi++) graphInputSet[gInputs[gi].name] = true;
        }

        var html = '';

        // Title
        if (opts.includeTitle !== false) {
            html += '<div class="info-row" style="margin-bottom:4px">';
            html += '<span class="info-value" style="font-size:14px;font-weight:700;word-break:break-all;color:#1e293b">' + escapeHtml(node.id || node.op_type) + '</span>';
            html += '</div>';
        }

        // Operation + Category
        html += '<div class="info-row"><span class="info-label">Operation</span>';
        html += '<span class="info-value"><span class="op-badge" style="background:' + catColor + '">' + escapeHtml(node.op_type) + '</span></span></div>';
        html += '<div class="info-row"><span class="info-label">Category</span>';
        html += '<span class="info-value">' + escapeHtml(node.category || 'other') + '</span></div>';
        if (node.device) {
            html += '<div class="info-row"><span class="info-label">Device</span>';
            html += '<span class="info-value">' + escapeHtml(node.device) + '</span></div>';

            // CPU reason display
            if (node.device.toLowerCase().indexOf('cpu') !== -1 && graphData) {
                var cpuReason = _findNodeCpuReason(graphData, node.id);
                if (cpuReason) {
                    html += '<div class="info-row"><span class="info-label">CPU Reason</span>';
                    html += '<span class="info-value" style="color:#92400e;font-style:italic">' + escapeHtml(cpuReason) + '</span></div>';
                }
            }
        }

        // Inputs (separated into tensor vs param)
        var inputs = node.inputs || [];
        if (inputs.length > 0) {
            var tensorInputs = [], paramInputs = [];
            for (var i = 0; i < inputs.length; i++) {
                if (!inputs[i]) continue;
                if (paramSet[inputs[i]]) paramInputs.push(inputs[i]);
                else tensorInputs.push(inputs[i]);
            }
            if (tensorInputs.length > 0) {
                html += '<div class="info-section-title">Tensor Inputs</div>';
                for (var ti2 = 0; ti2 < tensorInputs.length; ti2++)
                    html += renderTensorItem(tensorInputs[ti2], graphData, 'tensor', graphInputSet[tensorInputs[ti2]], opts);
            }
            if (paramInputs.length > 0) {
                html += '<div class="info-section-title">Param Inputs</div>';
                for (var pi2 = 0; pi2 < paramInputs.length; pi2++)
                    html += renderTensorItem(paramInputs[pi2], graphData, 'param', false, opts);
            }
        }

        // Outputs
        var outputs = node.outputs || [];
        if (outputs.length > 0) {
            html += '<div class="info-section-title">Outputs</div>';
            for (var j = 0; j < outputs.length; j++)
                html += renderTensorItem(outputs[j], graphData, 'output', false, opts);
        }

        // Attributes
        var attrs = node.attrs || {};
        var attrKeys = Object.keys(attrs);
        if (attrKeys.length > 0) {
            html += '<div class="info-section-title">Attributes</div>';
            for (var k = 0; k < attrKeys.length; k++) {
                html += '<div class="info-row"><span class="info-label">' + escapeHtml(attrKeys[k]) + '</span>';
                html += '<span class="info-value">' + escapeHtml(formatValue(attrs[attrKeys[k]])) + '</span></div>';
            }
        }

        return html;
    }

    /**
     * Generate complete subgraph detail HTML.
     * Shows input/output tensors and per-node CPU reasons.
     * @param {string} subgraphId - e.g. "cpu_0"
     * @param {object} graphData - Full graph data
     * @param {object} [options] - { clickable: true }
     * @returns {string} HTML string
     */
    function renderSubgraphDetailHTML(subgraphId, graphData, options) {
        var opts = options || {};
        if (!graphData) return '';

        var sg = null;
        var subgraphs = graphData.subgraphs || [];
        for (var i = 0; i < subgraphs.length; i++) {
            if (subgraphs[i].id === subgraphId) { sg = subgraphs[i]; break; }
        }
        if (!sg) return '';

        var isCpu = (sg.device || '').toLowerCase().indexOf('cpu') !== -1;
        var deviceColor = isCpu ? '#92400e' : '#4338ca';

        var html = '';

        // Title
        html += '<div class="info-row" style="margin-bottom:4px">';
        html += '<span class="info-value" style="font-size:14px;font-weight:700;color:#1e293b">' + escapeHtml(sg.id) + '</span>';
        html += '</div>';

        // Device
        html += '<div class="info-row"><span class="info-label">Device</span>';
        html += '<span class="info-value" style="color:' + deviceColor + ';font-weight:600">' + escapeHtml(sg.device || 'N/A') + '</span></div>';

        // Node count
        html += '<div class="info-row"><span class="info-label">Nodes</span>';
        html += '<span class="info-value">' + (sg.node_count || 0) + '</span></div>';

        // Collect subgraph nodes
        var nodes = graphData.nodes || [];
        var sgNodeIds = {};
        for (var ni = 0; ni < nodes.length; ni++) {
            if (nodes[ni].subgraph_id === subgraphId) sgNodeIds[nodes[ni].id] = true;
        }

        // Determine input/output tensors from edges
        var edges = graphData.edges || [];
        var inputTensors = {};
        var outputTensors = {};
        for (var ei = 0; ei < edges.length; ei++) {
            var edge = edges[ei];
            var fromIn = edge.from_node && sgNodeIds[edge.from_node];
            var toIn = edge.to_node && sgNodeIds[edge.to_node];
            if (!fromIn && toIn) {
                var tName = edge.from_output || edge.to_input;
                if (tName) inputTensors[tName] = true;
            }
            if (fromIn && !toIn) {
                var oName = edge.from_output || '';
                if (oName) outputTensors[oName] = true;
            }
        }
        // Check root graph outputs produced by nodes in this subgraph
        var graphOutputs = graphData.outputs || [];
        if (graphOutputs.length > 0) {
            // Tensor names produced by this subgraph's nodes
            var sgProducedTensors = {};
            for (var ni2 = 0; ni2 < nodes.length; ni2++) {
                if (nodes[ni2].subgraph_id === subgraphId) {
                    var nOuts = nodes[ni2].outputs || [];
                    for (var oi2 = 0; oi2 < nOuts.length; oi2++) {
                        sgProducedTensors[nOuts[oi2]] = true;
                    }
                }
            }
            // All tensor names produced by any node (to detect unresolved names)
            var allProduced = {};
            for (var ni3 = 0; ni3 < nodes.length; ni3++) {
                var nOuts3 = nodes[ni3].outputs || [];
                for (var oi3 = 0; oi3 < nOuts3.length; oi3++) {
                    allProduced[nOuts3[oi3]] = true;
                }
            }
            var isLastSg = subgraphs.length > 0 && subgraphs[subgraphs.length - 1].id === subgraphId;
            for (var gi = 0; gi < graphOutputs.length; gi++) {
                var goName2 = graphOutputs[gi].name;
                if (!goName2) continue;
                // Direct match: graph output name equals a tensor produced here
                if (sgProducedTensors[goName2]) {
                    outputTensors[goName2] = true;
                } else if (isLastSg && !allProduced[goName2]) {
                    // Fallback: unresolved graph output → assign to last subgraph
                    outputTensors[goName2] = true;
                }
            }
        }

        // Input tensors
        var inKeys = Object.keys(inputTensors);
        if (inKeys.length > 0) {
            html += '<div class="info-section-title">Input Tensors</div>';
            for (var ik = 0; ik < inKeys.length; ik++) {
                html += renderTensorItem(inKeys[ik], graphData, 'tensor', true, opts);
            }
        }

        // Output tensors
        var outKeys = Object.keys(outputTensors);
        if (outKeys.length > 0) {
            html += '<div class="info-section-title">Output Tensors</div>';
            for (var ok2 = 0; ok2 < outKeys.length; ok2++) {
                html += renderTensorItem(outKeys[ok2], graphData, 'output', false, opts);
            }
        }

        // CPU reasons (detailed per-node list)
        if (isCpu && sg.cpu_reasons) {
            html += '<div class="info-section-title">CPU Assignment Reasons</div>';

            // Group-level reason
            var gr = sg.cpu_reasons.group_reason;
            if (gr) {
                var grLabel = '';
                if (gr.category === 'user_excluded') grLabel = 'User option에 의해 CPU 할당';
                else if (gr.category === 'offload_disabled') grLabel = 'Offloading 비활성화 — 첫 번째 NPU 그래프만 NPU 유지';
                else if (gr.category === 'lightweight_merge') grLabel = 'Matrix 연산 없음 — device overhead 경감을 위해 CPU merge';
                else grLabel = gr.detail || gr.category;
                html += '<div style="font-size:12px;color:#92400e;padding:4px 0;font-style:italic">' + escapeHtml(grLabel) + '</div>';
            }

            // Node-level reasons (detailed)
            var nodeReasons = sg.cpu_reasons.node_reasons || {};
            var nrKeys = Object.keys(nodeReasons);
            if (nrKeys.length > 0) {
                // Group by category for display
                var byCategory = {};
                for (var nri = 0; nri < nrKeys.length; nri++) {
                    var nid = nrKeys[nri];
                    var reason = nodeReasons[nid];
                    var cat = reason.category || 'unknown';
                    if (!byCategory[cat]) byCategory[cat] = [];
                    byCategory[cat].push({ id: nid, detail: reason.detail || '' });
                }

                var catLabels = {
                    hw_constraint: 'Unsupported Operation',
                    unsupported_op: 'Unsupported Operation',
                    user_excluded: 'User Excluded',
                    infection: 'MemoryOp Infection',
                };

                // Classifier categories show per-node detail; others show reason only
                var classifierCats = { hw_constraint: true, unsupported_op: true };
                var catKeys = Object.keys(byCategory);
                for (var ci = 0; ci < catKeys.length; ci++) {
                    var catKey = catKeys[ci];
                    var items = byCategory[catKey];
                    var catLabel = catLabels[catKey] || catKey;
                    var isClassifier = !!classifierCats[catKey];

                    html += '<div class="cpu-reason-category" data-reason-category="' + escapeHtml(catKey) + '" '
                        + 'style="margin-top:6px;cursor:pointer;user-select:none">';
                    html += '<div style="font-size:11px;font-weight:600;color:#78350f;padding:2px 4px;background:#fef3c7;border-radius:4px;display:inline-block">';
                    html += escapeHtml(catLabel) + ' (' + items.length + ')';
                    html += '</div>';

                    if (isClassifier) {
                        for (var ii = 0; ii < items.length; ii++) {
                            html += '<div class="cpu-reason-node" data-node-id="' + escapeHtml(items[ii].id) + '" '
                                + 'style="font-size:11px;color:#475569;padding:2px 0 2px 8px;cursor:pointer">';
                            html += '<span style="color:#1e293b;font-weight:500">' + escapeHtml(items[ii].id) + '</span>';
                            if (items[ii].detail) {
                                html += ' — <span style="color:#92400e">' + escapeHtml(items[ii].detail) + '</span>';
                            }
                            html += '</div>';
                        }
                    } else {
                        var reason = items[0].detail || catLabel;
                        html += '<div style="font-size:11px;color:#92400e;padding:2px 0 2px 8px;font-style:italic">'
                            + escapeHtml(reason) + '</div>';
                    }
                    html += '</div>';
                }
            }
        }

        return html;
    }


    function truncateId(id) {
        if (!id) return '';
        if (id.length <= 28) return id;
        return '\u2026' + id.slice(-26);
    }

    function findNodeById(nodeId, graphData) {
        var nodes = graphData.nodes || [];
        for (var i = 0; i < nodes.length; i++) {
            if (nodes[i].id === nodeId) return nodes[i];
        }
        return null;
    }


    /**
     * Generate HTML for the tensor detail popup panel.
     * @param {string} tensorName - Name of the tensor to render details for
     * @param {Object} graphData - Full graph data for producer/consumer lookup
     * @param {Object} [opts] - Options for rendering
     * @returns {string} HTML string
     */
    function renderTensorDetailHTML(tensorName, graphData, opts) {
        opts = opts || {};
        var info = lookupTensorInfo(tensorName, graphData);

        // Find producing node and consuming nodes
        var producerNode = null;
        var consumerNodes = [];
        var edges = graphData.edges || [];
        for (var i = 0; i < edges.length; i++) {
            if (edges[i].from_output === tensorName && edges[i].from_node) {
                producerNode = edges[i].from_node;
            }
            if (edges[i].to_input === tensorName && edges[i].to_node) {
                consumerNodes.push(edges[i].to_node);
            }
        }

        // Check if it's a param
        var paramData = null;
        var params = graphData.params || [];
        for (var p = 0; p < params.length; p++) {
            if (params[p].name === tensorName) { paramData = params[p]; break; }
        }

        // Check if it's a graph input or output
        var isGraphInput = false, isGraphOutput = false;
        var gInputs = graphData.inputs || [];
        for (var gi = 0; gi < gInputs.length; gi++) {
            if (gInputs[gi].name === tensorName) { isGraphInput = true; break; }
        }
        var gOutputs = graphData.outputs || [];
        for (var go = 0; go < gOutputs.length; go++) {
            if (gOutputs[go].name === tensorName) { isGraphOutput = true; break; }
        }

        var html = '';

        // Back button — return to previous detail view
        html += '<div data-back-action="true" style="display:inline-flex;align-items:center;gap:4px;cursor:pointer;padding:4px 10px;margin-bottom:8px;border-radius:4px;background:#f1f5f9;color:#475569;font-size:12px;font-weight:500;transition:background .15s"'
             +  ' onmouseover="this.style.background=\'#e2e8f0\'" onmouseout="this.style.background=\'#f1f5f9\'">'
             +  '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5"/><polyline points="12 19 5 12 12 5"/></svg>'
             +  'Back</div>';

        // Type badge
        var kindLabel = paramData ? 'Parameter' : (isGraphInput ? 'Graph Input' : (isGraphOutput ? 'Graph Output' : 'Tensor'));
        var kindColor = paramData ? '#d97706' : (isGraphInput ? '#059669' : '#3b82f6');
        html += '<div class="info-row"><span class="info-label">Type</span>';
        html += '<span class="info-value"><span class="op-badge" style="background:' + kindColor + '">' + escapeHtml(kindLabel) + '</span></span></div>';

        // Name
        html += '<div class="info-row"><span class="info-label">Name</span>';
        html += '<span class="info-value" style="font-size:11px;word-break:break-all">' + escapeHtml(tensorName) + '</span></div>';

        // Shape
        if (info && info.shape && info.shape.length > 0) {
            html += '<div class="info-row"><span class="info-label">Shape</span>';
            html += '<span class="info-value" style="color:#4f46e5;font-weight:600">' + formatShape(info.shape) + '</span></div>';
            var numEl = 1;
            for (var s = 0; s < info.shape.length; s++) { if (info.shape[s] > 0) numEl *= info.shape[s]; }
            html += '<div class="info-row"><span class="info-label">Elements</span>';
            html += '<span class="info-value">' + numEl.toLocaleString() + '</span></div>';
        }

        // Dtype
        if (info && info.dtype) {
            html += '<div class="info-row"><span class="info-label">Dtype</span>';
            html += '<span class="info-value">' + escapeHtml(info.dtype) + '</span></div>';
        }

        // Size (for params)
        if (paramData && paramData.size_bytes) {
            html += '<div class="info-row"><span class="info-label">Size</span>';
            html += '<span class="info-value">' + formatBytes(paramData.size_bytes) + '</span></div>';
        }

        // Producer node
        if (producerNode) {
            var prodNode = findNodeById(producerNode, graphData);
            html += '<div class="info-section-title">Producer</div>';
            html += '<div class="info-tensor' + (opts.clickable ? ' clickable' : '') + '" data-click-action="navigate-node" data-click-target="' + escapeHtml(producerNode) + '">';
            if (prodNode) {
                var pc = CATEGORY_COLORS[prodNode.category] || CATEGORY_COLORS.other;
                html += '<span class="tensor-kind-badge" style="background:' + pc + '">N</span>';
                html += '<span class="tensor-name">' + escapeHtml(prodNode.op_type) + '</span>';
                html += '<span style="color:#94a3b8;font-size:10px">' + escapeHtml(truncateId(producerNode)) + '</span>';
            } else {
                html += '<span class="tensor-name">' + escapeHtml(producerNode) + '</span>';
            }
            html += '</div>';
        }

        // Consumer nodes
        if (consumerNodes.length > 0) {
            html += '<div class="info-section-title">Consumers (' + consumerNodes.length + ')</div>';
            for (var ci = 0; ci < consumerNodes.length; ci++) {
                var consNode = findNodeById(consumerNodes[ci], graphData);
                html += '<div class="info-tensor' + (opts.clickable ? ' clickable' : '') + '" data-click-action="navigate-node" data-click-target="' + escapeHtml(consumerNodes[ci]) + '">';
                if (consNode) {
                    var cc = CATEGORY_COLORS[consNode.category] || CATEGORY_COLORS.other;
                    html += '<span class="tensor-kind-badge" style="background:' + cc + '">N</span>';
                    html += '<span class="tensor-name">' + escapeHtml(consNode.op_type) + '</span>';
                    html += '<span style="color:#94a3b8;font-size:10px">' + escapeHtml(truncateId(consumerNodes[ci])) + '</span>';
                } else {
                    html += '<span class="tensor-name">' + escapeHtml(consumerNodes[ci]) + '</span>';
                }
                html += '</div>';
            }
        }

        return html;
    }

    /**
     * Add highlight (selected) class to SVG nodes by ID array.
     * @param {SVGSVGElement} svgEl - The SVG element containing the graph
     * @param {Array<string>} nodeIds - Array of node IDs to highlight
     */
    function highlightCpuReasonNodes(svgEl, nodeIds) {
        if (!svgEl) return;
        var gc = svgEl.querySelector('#graph-content');
        if (!gc) return;
        GraphRenderer.clearAllEdgeHighlights(svgEl);
        var prevSel = gc.querySelectorAll('.node-group.selected');
        for (var i = 0; i < prevSel.length; i++) prevSel[i].classList.remove('selected');
        for (var j = 0; j < nodeIds.length; j++) {
            var ng = gc.querySelector('.node-group[data-node-id="' + nodeIds[j] + '"]');
            if (ng) ng.classList.add('selected');
        }
    }

    /**
     * Zoom and pan the SVG to center on a specific node, highlighting it.
     * @param {SVGSVGElement} svgEl - The SVG element containing the graph
     * @param {Object} zoomPan - Zoom/pan control object with focusNode method
     * @param {string} nodeId - ID of the node to zoom to
     */
    function highlightAndZoomToNode(svgEl, zoomPan, nodeId) {
        if (!svgEl) return;
        var gc = svgEl.querySelector('#graph-content');
        if (!gc) return;
        GraphRenderer.clearAllEdgeHighlights(svgEl);
        var prevSel = gc.querySelectorAll('.node-group.selected');
        for (var i = 0; i < prevSel.length; i++) prevSel[i].classList.remove('selected');
        var ng = gc.querySelector('.node-group[data-node-id="' + nodeId + '"]');
        if (ng) {
            ng.classList.add('selected');
            var px = parseFloat(ng.getAttribute('data-x'));
            var py = parseFloat(ng.getAttribute('data-y'));
            var pw = parseFloat(ng.getAttribute('data-w'));
            var ph = parseFloat(ng.getAttribute('data-h'));
            if (!isNaN(px) && !isNaN(py) && !isNaN(pw) && !isNaN(ph)
                && zoomPan && zoomPan.focusNode) {
                zoomPan.focusNode(px, py, pw, ph);
            }
        }
    }


    /**
     * Show the detail section with given HTML content.
     * @param {string} sectionId - ID of the section wrapper element
     * @param {string} contentId - ID of the content container element
     * @param {string} html - innerHTML to set
     */
    function showDetailSection(sectionId, contentId, html) {
        var section = document.getElementById(sectionId);
        var content = document.getElementById(contentId);
        if (!section || !content) return;
        content.innerHTML = html;
        section.style.display = '';
    }

    /**
     * Hide the detail section and clear its content.
     * @param {string} sectionId - ID of the section wrapper element
     * @param {string} contentId - ID of the content container element
     */
    function hideDetailSection(sectionId, contentId) {
        var section = document.getElementById(sectionId);
        if (section) section.style.display = 'none';
        var content = document.getElementById(contentId);
        if (content) content.innerHTML = '';
    }

    /**
     * Show tensor detail in the detail panel with edge highlighting and back button.
     * @param {Object} opts
     * @param {HTMLElement} opts.svgEl - The SVG element containing the graph
     * @param {string} opts.tensorName - Name of the tensor to show
     * @param {Object} opts.graphData - The graph data object
     * @param {string|null} opts.contextNodeId - Currently selected node ID (for edge direction)
     * @param {string} opts.sectionId - ID of the detail section wrapper
     * @param {string} opts.contentId - ID of the detail content container
     * @param {Function} opts.onBack - Callback when back button is clicked
     */
    function showTensorDetail(opts) {
        var svgEl = opts.svgEl;
        var tensorName = opts.tensorName;
        var graphData = opts.graphData;
        var contextNodeId = opts.contextNodeId;
        var sectionId = opts.sectionId;
        var contentId = opts.contentId;
        var onBack = opts.onBack;

        if (!graphData) return;

        // Highlight tensor edges in graph
        if (svgEl) {
            var prevSelected = svgEl.querySelector('#graph-content .node-group.selected');
            if (prevSelected) prevSelected.classList.remove('selected');
            GraphRenderer.clearAllEdgeHighlights(svgEl);
            GraphRenderer.highlightEdgesByTensor(svgEl, tensorName, true, contextNodeId);
        }

        var html = renderTensorDetailHTML(tensorName, graphData, { clickable: true });
        showDetailSection(sectionId, contentId, html);

        // Back button handler
        var content = document.getElementById(contentId);
        if (content) {
            var backBtn = content.querySelector('[data-back-action]');
            if (backBtn) {
                backBtn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    if (svgEl) GraphRenderer.clearAllEdgeHighlights(svgEl);
                    if (onBack) onBack();
                });
            }
        }
    }

    /**
     * Find the best node to zoom to when clicking a tensor.
     * If we have a context node, zoom to the OTHER end of the tensor.
     * Otherwise, zoom to the producer node.
     */
    function _findTensorEndpointNode(tensorName, graphData, contextNodeId) {
        var edges = graphData.edges || [];
        var producerNode = null;
        var consumerNodes = [];
        for (var i = 0; i < edges.length; i++) {
            if (edges[i].from_output === tensorName && edges[i].from_node) {
                producerNode = edges[i].from_node;
            }
            if (edges[i].to_input === tensorName && edges[i].to_node) {
                consumerNodes.push(edges[i].to_node);
            }
        }
        if (contextNodeId) {
            // Zoom to the other end: if context is producer, go to first consumer; vice versa
            if (contextNodeId === producerNode && consumerNodes.length > 0) {
                return consumerNodes[0];
            }
            if (consumerNodes.indexOf(contextNodeId) !== -1 && producerNode) {
                return producerNode;
            }
        }
        // Default: zoom to producer (or first consumer)
        return producerNode || (consumerNodes.length > 0 ? consumerNodes[0] : null);
    }

    /**
     * Navigate to a node: select it visually, highlight connected edges, focus camera.
     * @param {Object} opts
     * @param {HTMLElement} opts.svgEl - The SVG element
     * @param {Object} opts.zoomPan - The zoomPan control object
     * @param {string} opts.nodeId - Target node ID
     * @param {Object} opts.graphData - The graph data
     * @param {Function} [opts.onNodeSelected] - Callback with node data when node is found
     */
    function navigateToNode(opts) {
        var svgEl = opts.svgEl;
        var zoomPan = opts.zoomPan;
        var nodeId = opts.nodeId;
        var graphData = opts.graphData;
        var onNodeSelected = opts.onNodeSelected;

        if (!svgEl) return;
        var graphContent = svgEl.querySelector('#graph-content');
        if (!graphContent) return;

        // Clear previous selection
        var prev = graphContent.querySelector('.node-group.selected');
        if (prev) prev.classList.remove('selected');

        var target = graphContent.querySelector('.node-group[data-node-id="' + CSS.escape(nodeId) + '"]');
        if (!target) return;

        target.classList.add('selected');
        GraphRenderer.clearAllEdgeHighlights(svgEl);

        // Focus camera
        if (zoomPan && typeof zoomPan.focusNode === 'function') {
            var px = parseFloat(target.getAttribute('data-x'));
            var py = parseFloat(target.getAttribute('data-y'));
            var pw = parseFloat(target.getAttribute('data-w'));
            var ph = parseFloat(target.getAttribute('data-h'));
            if (!isNaN(px) && !isNaN(py) && !isNaN(pw) && !isNaN(ph)) {
                zoomPan.focusNode(px, py, pw, ph);
            }
        }

        // Notify consumer of selection
        if (graphData && onNodeSelected) {
            var node = findNodeById(nodeId, graphData);
            if (node) onNodeSelected(node);
        }
    }

    /**
     * Set up click delegation on the sidebar detail panel.
     * Handles CPU reason clicks, tensor clicks, and navigate-node actions.
     * @param {HTMLElement} containerEl - The content container (e.g. #node-info-content)
     * @param {Object} callbacks
     * @param {Function} callbacks.highlightAndZoom - function(nodeId) to zoom to a single node
     * @param {Function} callbacks.highlightCpuReasons - function(nodeIds) to highlight multiple nodes
     * @param {Function} callbacks.navigateNode - function(nodeId) to navigate to a node
     * @param {Function} callbacks.showTensorDetail - function(tensorName) to show tensor detail
     */
    function setupSidebarClickDelegation(containerEl, callbacks) {
        if (!containerEl) return;
        containerEl.addEventListener('click', function(e) {
            // CPU reason node click → highlight + zoom to individual node
            var nodeEl = e.target.closest('.cpu-reason-node');
            if (nodeEl) {
                var nid = nodeEl.getAttribute('data-node-id');
                if (nid && callbacks.highlightAndZoom) callbacks.highlightAndZoom(nid);
                e.stopPropagation();
                return;
            }

            // CPU reason category click → highlight all nodes in category
            var catEl = e.target.closest('.cpu-reason-category');
            if (catEl) {
                var nodeEls = catEl.querySelectorAll('.cpu-reason-node');
                var ids = [];
                for (var ni = 0; ni < nodeEls.length; ni++) {
                    var id = nodeEls[ni].getAttribute('data-node-id');
                    if (id) ids.push(id);
                }
                if (ids.length > 0 && callbacks.highlightCpuReasons) callbacks.highlightCpuReasons(ids);
                e.stopPropagation();
                return;
            }

            var tensorEl = e.target.closest('.info-tensor.clickable');
            if (!tensorEl) return;
            var action = tensorEl.getAttribute('data-click-action');
            var target = tensorEl.getAttribute('data-click-target');
            if (!action || !target) return;
            e.stopPropagation();
            if (action === 'navigate-node' && callbacks.navigateNode) callbacks.navigateNode(target);
            else if (action === 'show-tensor-detail' && callbacks.showTensorDetail) callbacks.showTensorDetail(target);
        });
    }

    window.GraphViewer = {
        CATEGORY_COLORS: CATEGORY_COLORS,
        escapeHtml: escapeHtml,
        formatValue: formatValue,
        formatShape: formatShape,
        formatBytes: formatBytes,
        lookupTensorInfo: lookupTensorInfo,
        truncateId: truncateId,
        findNodeById: findNodeById,
        findTensorEndpointNode: _findTensorEndpointNode,
        renderTensorItem: renderTensorItem,
        renderNodeDetailHTML: renderNodeDetailHTML,
        renderSubgraphDetailHTML: renderSubgraphDetailHTML,
        renderTensorDetailHTML: renderTensorDetailHTML,
        highlightCpuReasonNodes: highlightCpuReasonNodes,
        highlightAndZoomToNode: highlightAndZoomToNode,
        showDetailSection: showDetailSection,
        hideDetailSection: hideDetailSection,
        showTensorDetail: showTensorDetail,
        navigateToNode: navigateToNode,
        setupSidebarClickDelegation: setupSidebarClickDelegation,
    };

})();
