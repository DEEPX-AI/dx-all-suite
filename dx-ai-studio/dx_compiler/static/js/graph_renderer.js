/**
 * GraphRenderer — dagre-based DAG layout + SVG renderer for ONNX model graphs.
 * Requires dagre.js loaded globally via script tag.
 */
(function () {
    'use strict';

    const SVG_NS = 'http://www.w3.org/2000/svg';

    // Stored interaction handler refs for clean removal on clearGraph
    let _interactionClickHandler = null;
    let _interactionDblClickHandler = null;
    let _interactionSvgClickHandler = null;
    let _interactionMouseEnterHandler = null;
    let _interactionMouseLeaveHandler = null;
    let _interactionGraphContent = null;
    let _interactionSvgElement = null;

    // Stored zoom/pan cleanup function for removal on re-init
    let _zoomPanCleanup = null;

    const LAYOUT = {
        nodeWidth: 160,
        nodeHeight: 50,
        hGap: 40,
        vGap: 60,
        padding: 60,
        computeNodeWidth: 200,
        maxLabelLength: 20,
    };

    const CATEGORY_CONFIG = {
        compute:       { color: '#4f46e5', bg: '#eef2ff', shape: 'roundrect', label: 'Compute' },
        memory:        { color: '#64748b', bg: '#f1f5f9', shape: 'parallelogram', label: 'Memory' },
        activation:    { color: '#059669', bg: '#ecfdf5', shape: 'stadium', label: 'Activation' },
        normalization: { color: '#0d9488', bg: '#f0fdfa', shape: 'doublerect', label: 'Normalization' },
        pooling:       { color: '#7c3aed', bg: '#f5f3ff', shape: 'trapezoid', label: 'Pooling' },
        elementwise:   { color: '#d97706', bg: '#fffbeb', shape: 'circle', label: 'Elementwise' },
        quantize:      { color: '#ca8a04', bg: '#fefce8', shape: 'octagon', label: 'Quantize' },
        other:         { color: '#6b7280', bg: '#f9fafb', shape: 'rect', label: 'Other' },
    };

    const EDGE_STYLE = {
        stroke: '#cbd5e1',
        strokeHighlight: '#3b82f6',
        strokeWidth: 1.5,
    };

    const BOX_PADDING = 40;
    const LABEL_SPACE = 25;
    const IO_NODE_W = 140;
    const IO_NODE_H = 28;
    const ARROW_LEN = 8;

    function getNodeWidth(node) {
        if (!node) return LAYOUT.nodeWidth;
        const cat = node.category || 'other';
        if (cat === 'compute') return LAYOUT.computeNodeWidth;
        if (cat === 'elementwise') return 120;
        return LAYOUT.nodeWidth;
    }

    function dagreLayout(nodes, edges) {
        const g = new dagre.graphlib.Graph();
        g.setGraph({
            rankdir: 'TB',
            ranksep: LAYOUT.vGap,
            nodesep: LAYOUT.hGap,
            edgesep: 20,
            marginx: LAYOUT.padding,
            marginy: LAYOUT.padding,
        });
        g.setDefaultEdgeLabel(function () { return {}; });

        const nodeIds = new Set();
        for (let i = 0; i < nodes.length; i++) {
            const n = nodes[i];
            const w = getNodeWidth(n);
            g.setNode(n.id, { width: w, height: LAYOUT.nodeHeight });
            nodeIds.add(n.id);
        }

        for (let ei = 0; ei < edges.length; ei++) {
            const e = edges[ei];
            if (e.from_node && e.to_node && nodeIds.has(e.from_node) && nodeIds.has(e.to_node)) {
                if (!g.hasEdge(e.from_node, e.to_node)) {
                    g.setEdge(e.from_node, e.to_node);
                }
            }
        }

        dagre.layout(g);

        const positions = new Map();
        g.nodes().forEach(function (id) {
            const dn = g.node(id);
            positions.set(id, {
                x: dn.x - dn.width / 2,
                y: dn.y - dn.height / 2,
                w: dn.width,
                h: dn.height,
            });
        });

        const edgePaths = new Map();
        g.edges().forEach(function (e) {
            const de = g.edge(e);
            if (de && de.points) {
                edgePaths.set(e.v + '\u2192' + e.w, de.points);
            }
        });

        return { positions: positions, edgePaths: edgePaths };
    }

    function edgePointsToPath(points, arrowOffset) {
        if (!points || points.length < 2) return '';
        var last = points[points.length - 1];
        var prev = points[points.length - 2];
        var dx = last.x - prev.x;
        var dy = last.y - prev.y;
        var len = Math.sqrt(dx * dx + dy * dy);
        var off = arrowOffset || 0;
        var endX = len > 0 ? last.x - (dx / len) * off : last.x;
        var endY = len > 0 ? last.y - (dy / len) * off : last.y;

        if (points.length === 2) {
            return 'M' + points[0].x + ',' + points[0].y +
                   'L' + endX + ',' + endY;
        }
        if (points.length === 3) {
            return 'M' + points[0].x + ',' + points[0].y +
                   'Q' + points[1].x + ',' + points[1].y +
                   ',' + endX + ',' + endY;
        }
        var d = 'M' + points[0].x + ',' + points[0].y;
        for (var i = 1; i < points.length - 2; i++) {
            var midX = (points[i].x + points[i + 1].x) / 2;
            var midY = (points[i].y + points[i + 1].y) / 2;
            d += 'Q' + points[i].x + ',' + points[i].y + ',' + midX + ',' + midY;
        }
        var p = points[points.length - 2];
        d += 'Q' + p.x + ',' + p.y + ',' + endX + ',' + endY;
        return d;
    }


    /** Create an SVG element in the SVG namespace. */
    function svgEl(tag, attrs) {
        const el = document.createElementNS(SVG_NS, tag);
        if (attrs) {
            for (const [k, v] of Object.entries(attrs)) {
                el.setAttribute(k, v);
            }
        }
        return el;
    }

    /** Truncate text to fit. */
    function truncate(text, maxLen) {
        if (!text) return '';
        if (text.length <= maxLen) return text;
        return text.slice(0, maxLen - 1) + '…';
    }

    /** Get shape info string from edges for a node's first output. */
    function getShapeInfo(nodeId, edges) {
        for (const e of edges) {
            if (e.from_node === nodeId && e.shape) {
                return '[' + e.shape.map(d => d === -1 ? '?' : d).join('×') + ']';
            }
        }
        return '';
    }


    function renderRoundRect(g, x, y, w, h, cfg) {
        const rect = svgEl('rect', {
            x: x, y: y, width: w, height: h,
            rx: 8, ry: 8,
            fill: cfg.bg, stroke: cfg.color, 'stroke-width': 1.5,
        });
        g.appendChild(rect);
        return rect;
    }

    function renderParallelogram(g, x, y, w, h, cfg) {
        const offset = 10;
        const points = [
            `${x + offset},${y}`,
            `${x + w},${y}`,
            `${x + w - offset},${y + h}`,
            `${x},${y + h}`,
        ].join(' ');
        const poly = svgEl('polygon', {
            points: points,
            fill: cfg.bg, stroke: cfg.color, 'stroke-width': 1.5,
        });
        g.appendChild(poly);
        return poly;
    }

    function renderStadium(g, x, y, w, h, cfg) {
        const rect = svgEl('rect', {
            x: x, y: y, width: w, height: h,
            rx: h / 2, ry: h / 2,
            fill: cfg.bg, stroke: cfg.color, 'stroke-width': 1.5,
        });
        g.appendChild(rect);
        return rect;
    }

    function renderDoubleRect(g, x, y, w, h, cfg) {
        const gap = 3;
        const outer = svgEl('rect', {
            x: x, y: y, width: w, height: h,
            rx: 4, ry: 4,
            fill: cfg.bg, stroke: cfg.color, 'stroke-width': 1.5,
        });
        g.appendChild(outer);
        const inner = svgEl('rect', {
            x: x + gap, y: y + gap, width: w - 2 * gap, height: h - 2 * gap,
            rx: 2, ry: 2,
            fill: 'none', stroke: cfg.color, 'stroke-width': 1,
        });
        g.appendChild(inner);
        return outer;
    }

    function renderTrapezoid(g, x, y, w, h, cfg) {
        const inset = 10;
        const points = [
            `${x + inset},${y}`,
            `${x + w - inset},${y}`,
            `${x + w},${y + h}`,
            `${x},${y + h}`,
        ].join(' ');
        const poly = svgEl('polygon', {
            points: points,
            fill: cfg.bg, stroke: cfg.color, 'stroke-width': 1.5,
        });
        g.appendChild(poly);
        return poly;
    }

    function renderCircleShape(g, x, y, w, h, cfg) {
        const cx = x + w / 2;
        const cy = y + h / 2;
        const rx = w / 2;
        const ry = h / 2;
        const ellipse = svgEl('ellipse', {
            cx: cx, cy: cy, rx: rx, ry: ry,
            fill: cfg.bg, stroke: cfg.color, 'stroke-width': 1.5,
        });
        g.appendChild(ellipse);
        return ellipse;
    }

    function renderOctagon(g, x, y, w, h, cfg) {
        const inset = Math.min(w, h) * 0.25;
        const points = [
            `${x + inset},${y}`,
            `${x + w - inset},${y}`,
            `${x + w},${y + inset}`,
            `${x + w},${y + h - inset}`,
            `${x + w - inset},${y + h}`,
            `${x + inset},${y + h}`,
            `${x},${y + h - inset}`,
            `${x},${y + inset}`,
        ].join(' ');
        const poly = svgEl('polygon', {
            points: points,
            fill: cfg.bg, stroke: cfg.color, 'stroke-width': 1.5,
        });
        g.appendChild(poly);
        return poly;
    }

    function renderRect(g, x, y, w, h, cfg) {
        const rect = svgEl('rect', {
            x: x, y: y, width: w, height: h,
            rx: 4, ry: 4,
            fill: cfg.bg, stroke: cfg.color, 'stroke-width': 1.5,
        });
        g.appendChild(rect);
        return rect;
    }

    const SHAPE_RENDERERS = {
        roundrect: renderRoundRect,
        parallelogram: renderParallelogram,
        stadium: renderStadium,
        doublerect: renderDoubleRect,
        trapezoid: renderTrapezoid,
        circle: renderCircleShape,
        octagon: renderOctagon,
        rect: renderRect,
    };

    /**
     * Render a single node group.
     * @param {Object} node - Node data: { id, op_type, category, inputs, outputs, device, ... }
     * @param {{x: number, y: number, w: number, h: number}} pos - Layout position
     * @param {Array} edges - All graph edges (used for shape info display)
     * @param {Element} graphContent - The SVG graph-content container
     * @returns {SVGGElement} The node <g> element
     */
    function renderNode(node, pos, edges, graphContent) {
        const cat = node.category || 'other';
        const cfg = CATEGORY_CONFIG[cat] || CATEGORY_CONFIG.other;
        const shapeType = cfg.shape;

        // Sanitize position values — prevent NaN from corrupting data attributes
        var rx = isNaN(pos.x) ? 0 : pos.x;
        var ry = isNaN(pos.y) ? 0 : pos.y;
        var rw = isNaN(pos.w) ? LAYOUT.nodeWidth : pos.w;
        var rh = isNaN(pos.h) ? LAYOUT.nodeHeight : pos.h;

        const g = svgEl('g', {
            class: 'node-group',
            'data-node-id': node.id,
            'data-category': cat,
            'data-x': rx,
            'data-y': ry,
            'data-w': rw,
            'data-h': rh,
        });

        // Render shape
        const renderer = SHAPE_RENDERERS[shapeType] || SHAPE_RENDERERS.rect;
        renderer(g, rx, ry, rw, rh, cfg);

        // Device overlay
        if (node.device) {
            applyDeviceOverlay(g, node.device, pos, cfg);
        }

        // Op type label
        const label = truncate(node.op_type, LAYOUT.maxLabelLength);

        const text = svgEl('text', {
            x: rx + rw / 2,
            y: ry + rh / 2,
            'text-anchor': 'middle',
            'dominant-baseline': 'central',
            fill: cfg.color,
            'font-size': cat === 'compute' ? '13' : '12',
            'font-weight': cat === 'compute' ? '600' : '500',
            'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            'pointer-events': 'none',
        });
        text.textContent = label;
        g.appendChild(text);

        graphContent.appendChild(g);
        return g;
    }

    /** Apply device-specific visual overlay to a node group. */
    function applyDeviceOverlay(g, device, pos, cfg) {
        // Device overlays are only for non-partitioned models.
        // In partitioned models, the partition box already indicates device.
    }


    /**
     * Render a single edge as a cubic bezier path with an optional tensor label.
     * @returns {SVGPathElement}
     */
    /** Create an I/O tensor node box (stadium shape) with label text. */
    function _renderIONodeBox(cx, y, tensorName, shape, ioType, container) {
        var isInput = ioType === 'input';
        var ioG = svgEl('g', {
            class: 'node-group graph-io-node',
            'data-tensor': tensorName || '',
            'data-io-type': ioType,
        });
        var shapeStr = '';
        if (shape && shape.length > 0) {
            shapeStr = '[' + shape.map(function(d) { return d === -1 ? '?' : d; }).join('\u00d7') + ']';
        }
        var label = truncate(tensorName || ioType, 18);
        if (shapeStr) label += '  ' + shapeStr;
        var textW = Math.max(IO_NODE_W, label.length * 7 + 24);
        ioG.appendChild(svgEl('rect', {
            x: cx - textW / 2, y: y, width: textW, height: IO_NODE_H,
            rx: IO_NODE_H / 2, ry: IO_NODE_H / 2,
            fill: isInput ? '#e0f2fe' : '#fef3c7',
            stroke: isInput ? '#38bdf8' : '#f59e0b',
            'stroke-width': 1.5,
        }));
        var txt = svgEl('text', {
            x: cx, y: y + IO_NODE_H / 2,
            'text-anchor': 'middle', 'dominant-baseline': 'central',
            fill: isInput ? '#0369a1' : '#92400e',
            'font-size': '11', 'font-weight': '600', 'pointer-events': 'none',
            'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        });
        txt.textContent = label;
        ioG.appendChild(txt);
        container.appendChild(ioG);
    }

    /** Render a tensor shape label at the midpoint of an edge. */
    function _renderEdgeLabel(edge, midX, midY, container) {
        if (!edge.shape || edge.shape.length === 0) return;
        var labelText = '[' + edge.shape.map(function(d) { return d === -1 ? '?' : d; }).join('\u00d7') + ']';

        var labelGroup = svgEl('g', {
            class: 'edge-label-group',
            'data-tensor-name': edge.from_output || edge.to_input || '',
            'data-tensor-shape': JSON.stringify(edge.shape),
            'data-tensor-dtype': edge.dtype || '',
            'data-from-node': edge.from_node || '',
            'data-to-node': edge.to_node || '',
        });

        var labelHit = svgEl('rect', {
            x: midX - 40, y: midY - 10, width: 80, height: 20,
            fill: 'transparent', class: 'edge-label-hit', cursor: 'pointer',
        });
        labelGroup.appendChild(labelHit);

        var labelBg = svgEl('rect', {
            x: midX - 2, y: midY - 7, width: 4, height: 14,
            rx: 3, ry: 3, fill: '#fff', opacity: '0.85',
            class: 'edge-label-bg', 'pointer-events': 'none',
        });
        labelGroup.appendChild(labelBg);

        var label = svgEl('text', {
            x: midX, y: midY,
            'text-anchor': 'middle', 'dominant-baseline': 'central',
            fill: '#64748b', 'font-size': '9', 'font-weight': '500',
            'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            'pointer-events': 'none', class: 'edge-label',
        });
        label.textContent = labelText;
        labelGroup.appendChild(label);
        container.appendChild(labelGroup);

        requestAnimationFrame(function() {
            try {
                var bbox = label.getBBox();
                labelBg.setAttribute('x', bbox.x - 3);
                labelBg.setAttribute('y', bbox.y - 1);
                labelBg.setAttribute('width', bbox.width + 6);
                labelBg.setAttribute('height', bbox.height + 2);
                labelHit.setAttribute('x', bbox.x - 8);
                labelHit.setAttribute('y', bbox.y - 4);
                labelHit.setAttribute('width', bbox.width + 16);
                labelHit.setAttribute('height', bbox.height + 8);
            } catch (_) { /* ignore if not in DOM */ }
        });
    }

    /**
     * Render a single edge between two nodes with optional shape label and hit area.
     * Handles I/O nodes (graph inputs/outputs) and grouped multi-input edges.
     * @param {Object} edge - Edge data: { from_node, to_node, from_output, to_input, shape, dtype }
     * @param {Map} positions - Map of nodeId → {x, y, w, h}
     * @param {Element} graphContent - The SVG graph-content container
     * @param {Array} edgePaths - Array to collect rendered SVG path elements
     * @param {Object} [tensorInfo] - Tensor metadata: tensorName → {shape, dtype}
     */
    function renderEdge(edge, positions, graphContent, edgePaths, tensorInfo) {
        if (tensorInfo && !edge.shape) {
            var tKey = edge.from_output || edge.to_input;
            var tInfo = tKey ? tensorInfo[tKey] : null;
            if (tInfo) {
                if (tInfo.shape) edge.shape = tInfo.shape;
                if (tInfo.dtype) edge.dtype = tInfo.dtype;
            }
        }

        var toPos = positions.get(edge.to_node);
        var d, labelX, labelY;

        if (edge._isGraphOutput || (!edge.to_node && edge.from_node)) {
            var fromPos = positions.get(edge.from_node);
            if (!fromPos) return null;
            var x1 = fromPos.x + fromPos.w / 2;
            var y1 = fromPos.y + fromPos.h;
            var ioY = y1 + LAYOUT.vGap * 0.4;
            _renderIONodeBox(x1, ioY, edge.from_output, edge.shape, 'output', graphContent);
            var cy_ctrl = (y1 + ioY) / 2;
            d = 'M ' + x1 + ' ' + y1 + ' C ' + x1 + ' ' + cy_ctrl + ', ' + x1 + ' ' + cy_ctrl + ', ' + x1 + ' ' + ioY;
            labelX = x1;
            labelY = cy_ctrl;
        } else if (!toPos) {
            return null;
        } else if (!edge.from_node || !positions.has(edge.from_node)) {
            var x1b = toPos.x + toPos.w / 2;
            var ioYb = toPos.y - LAYOUT.vGap * 0.4 - IO_NODE_H;
            _renderIONodeBox(x1b, ioYb, edge.from_output, edge.shape, 'input', graphContent);
            var y2Short = toPos.y - ARROW_LEN;
            var ioBottom = ioYb + IO_NODE_H;
            var cyb = (ioBottom + y2Short) / 2;
            d = 'M ' + x1b + ' ' + ioBottom + ' C ' + x1b + ' ' + cyb + ', ' + x1b + ' ' + cyb + ', ' + x1b + ' ' + y2Short;
            labelX = x1b;
            labelY = cyb;
        } else {
            var key = edge.from_node + '\u2192' + edge.to_node;
            var points = edgePaths ? edgePaths.get(key) : null;
            if (points) {
                d = edgePointsToPath(points, ARROW_LEN);
                var midIdx = Math.floor(points.length / 2);
                labelX = points[midIdx].x;
                labelY = points[midIdx].y;
            } else {
                var fromPos2 = positions.get(edge.from_node);
                if (!fromPos2) return null;
                var x1c = fromPos2.x + fromPos2.w / 2;
                var y1c = fromPos2.y + fromPos2.h;
                var x2c = toPos.x + toPos.w / 2;
                var y2c = toPos.y - ARROW_LEN;
                var cyc = (y1c + y2c) / 2;
                d = 'M ' + x1c + ' ' + y1c + ' C ' + x1c + ' ' + cyc + ', ' + x2c + ' ' + cyc + ', ' + x2c + ' ' + y2c;
                labelX = (x1c + x2c) / 2;
                labelY = (y1c + toPos.y) / 2;
            }
        }

        var hitArea = svgEl('path', {
            d: d, fill: 'none', stroke: 'transparent', 'stroke-width': 12, class: 'edge-hitarea',
        });
        if (edge.from_node) hitArea.setAttribute('data-from', edge.from_node);
        if (edge.to_node) hitArea.setAttribute('data-to', edge.to_node);
        if (edge.from_output) hitArea.setAttribute('data-tensor', edge.from_output);
        graphContent.appendChild(hitArea);

        var path = svgEl('path', {
            d: d, fill: 'none', stroke: EDGE_STYLE.stroke,
            'stroke-width': EDGE_STYLE.strokeWidth, 'marker-end': 'url(#arrowhead)',
            class: 'edge-path', 'pointer-events': 'none',
        });
        if (edge.from_node) path.setAttribute('data-from', edge.from_node);
        if (edge.to_node) path.setAttribute('data-to', edge.to_node);
        if (edge.from_output) path.setAttribute('data-tensor', edge.from_output);
        graphContent.appendChild(path);

        _renderEdgeLabel(edge, labelX, labelY, graphContent);

        return path;
    }



    /**
     * Unified interaction handler for both flat and partitioned graphs.
     * @param {SVGElement} svgElement
     * @param {SVGGElement} graphContent - #graph-content group
     * @param {Map} nodeMap - nodeId → node data
     * @param {Array} edges
     * @param {boolean} [isPartitioned=false] - Enable subgraph toggle & IO node handling
     */
    function setupInteractions(svgElement, graphContent, nodeMap, edges, isPartitioned) {
        _interactionGraphContent = graphContent;
        _interactionSvgElement = svgElement;

        _interactionClickHandler = function (e) {
            const nodeGroup = e.target.closest('.node-group');
            const edgeLabelGroup = e.target.closest('.edge-label-group');
            const subgraphBg = e.target.closest('.subgraph-bg');
            const edgeHit = e.target.closest('.edge-hitarea');

            // Partitioned-only: subgraph toggle button / collapsed box
            if (isPartitioned) {
                var subgraphToggle = e.target.closest('.subgraph-toggle');
                if (subgraphToggle) {
                    var sgId = subgraphToggle.getAttribute('data-subgraph-id');
                    if (sgId) {
                        svgElement.dispatchEvent(new CustomEvent('subgraph-toggled', {
                            bubbles: true, detail: { subgraphId: sgId },
                        }));
                        svgElement.dispatchEvent(new CustomEvent('subgraph-selected', {
                            bubbles: true, detail: { subgraphId: sgId, device: '' },
                        }));
                    }
                    return;
                }
                if (subgraphBg && subgraphBg.getAttribute('data-collapsed') === 'true') {
                    var sgId2 = subgraphBg.getAttribute('data-subgraph-id');
                    if (sgId2) {
                        svgElement.dispatchEvent(new CustomEvent('subgraph-toggled', {
                            bubbles: true, detail: { subgraphId: sgId2 },
                        }));
                        svgElement.dispatchEvent(new CustomEvent('subgraph-selected', {
                            bubbles: true, detail: { subgraphId: sgId2, device: '' },
                        }));
                    }
                    return;
                }
            }

            // Clear highlights when interacting with a specific object
            if (nodeGroup || edgeLabelGroup || subgraphBg || edgeHit) {
                clearAllEdgeHighlights(svgElement);
            }

            // Partitioned-only: IO node (graph input/output)
            var ioNode = isPartitioned && nodeGroup && nodeGroup.classList.contains('graph-io-node') ? nodeGroup : null;
            if (ioNode) {
                const prev = graphContent.querySelector('.node-group.selected');
                if (prev && prev !== ioNode) prev.classList.remove('selected');
                ioNode.classList.toggle('selected');

                var tensorName = ioNode.getAttribute('data-tensor');
                if (tensorName && ioNode.classList.contains('selected')) {
                    highlightEdgesByTensor(svgElement, tensorName, true, null);
                }
                svgElement.dispatchEvent(new CustomEvent('edge-selected', {
                    bubbles: true, detail: { tensorName: tensorName },
                }));

            } else if (nodeGroup) {
                // -- Node click --
                const prev = graphContent.querySelector('.node-group.selected');
                if (prev && prev !== nodeGroup) prev.classList.remove('selected');

                nodeGroup.classList.toggle('selected');

                const nodeId = nodeGroup.getAttribute('data-node-id');
                const node = nodeMap.get(nodeId);
                const isSelected = nodeGroup.classList.contains('selected');

                if (isSelected) {
                    highlightConnectedEdges(graphContent, nodeId, true);
                }


                svgElement.dispatchEvent(new CustomEvent('node-selected', {
                    bubbles: true, detail: { node: node, selected: isSelected },
                }));

            } else if (edgeLabelGroup) {
                // -- Edge label click → show tensor detail --
                const prev = graphContent.querySelector('.node-group.selected');
                if (prev) prev.classList.remove('selected');

                const tensorName = edgeLabelGroup.getAttribute('data-tensor-name');
                if (tensorName) {
                    svgElement.dispatchEvent(new CustomEvent('edge-selected', {
                        bubbles: true, detail: { tensorName: tensorName },
                    }));
                }

            } else if (subgraphBg) {
                // -- Subgraph background click → show detail --
                const prev = graphContent.querySelector('.node-group.selected');
                if (prev) prev.classList.remove('selected');

                const subgraphId = subgraphBg.getAttribute('data-subgraph-id');
                if (subgraphId) {
                    let device = '';
                    for (const [, node] of nodeMap) {
                        if (node.subgraph_id === subgraphId) {
                            device = node.subgraph_device || '';
                            break;
                        }
                    }
                    svgElement.dispatchEvent(new CustomEvent('subgraph-selected', {
                        bubbles: true, detail: { subgraphId: subgraphId, device: device },
                    }));
                }

            } else if (edgeHit) {
                // -- Edge path click (via hit area) → show tensor detail --
                const prev = graphContent.querySelector('.node-group.selected');
                if (prev) prev.classList.remove('selected');

                const tensorName = edgeHit.getAttribute('data-tensor');
                if (tensorName) {
                    if (isPartitioned) {
                        var clickedTensor = tensorName.split(',')[0];
                        highlightEdgesByTensor(svgElement, clickedTensor, true, null);
                        svgElement.dispatchEvent(new CustomEvent('edge-selected', {
                            bubbles: true, detail: { tensorName: clickedTensor },
                        }));
                    } else {
                        var visiblePath = edgeHit.nextElementSibling;
                        if (visiblePath && visiblePath.classList.contains('edge-path')) {
                            visiblePath.classList.add('tensor-highlighted');
                            visiblePath.setAttribute('marker-end', 'url(#arrowhead-highlight)');
                        }
                        svgElement.dispatchEvent(new CustomEvent('edge-selected', {
                            bubbles: true, detail: { tensorName: tensorName },
                        }));
                    }
                }

            } else {
                // -- Click on empty area → deselect everything --
                const prev = graphContent.querySelector('.node-group.selected');
                if (prev) prev.classList.remove('selected');

                clearAllEdgeHighlights(svgElement);
                svgElement.dispatchEvent(new CustomEvent('node-selected', {
                    bubbles: true, detail: { node: null, selected: false },
                }));
            }
        };
        graphContent.addEventListener('click', _interactionClickHandler);

        // Double-click background → clear all highlights
        _interactionDblClickHandler = function (e) {
            if (e.target.closest('.node-group') || e.target.closest('.edge-label-group')
                || e.target.closest('.edge-hitarea')) return;
            if (isPartitioned) {
                if (e.target.closest('.subgraph-toggle')) return;
                var collapsedBg = e.target.closest('.subgraph-bg');
                if (collapsedBg && collapsedBg.getAttribute('data-collapsed') === 'true') return;
            }
            var prev = graphContent.querySelector('.node-group.selected');
            if (prev) prev.classList.remove('selected');
            clearAllEdgeHighlights(svgElement);
            svgElement.dispatchEvent(new CustomEvent('node-selected', {
                bubbles: true, detail: { node: null, selected: false },
            }));
        };
        graphContent.addEventListener('dblclick', _interactionDblClickHandler);

        // SVG background click (outside graphContent)
        _interactionSvgClickHandler = function (e) {
            if (e.target === svgElement) {
                var prev = graphContent.querySelector('.node-group.selected');
                if (prev) prev.classList.remove('selected');
                clearAllEdgeHighlights(svgElement);
                svgElement.dispatchEvent(new CustomEvent('node-selected', {
                    bubbles: true, detail: { node: null, selected: false },
                }));
            }
        };
        svgElement.addEventListener('click', _interactionSvgClickHandler);

        _interactionMouseEnterHandler = function (e) {
            const nodeGroup = e.target.closest('.node-group');
            if (!nodeGroup) return;
            nodeGroup.classList.add('hovered');
        };
        graphContent.addEventListener('mouseenter', _interactionMouseEnterHandler, true);

        _interactionMouseLeaveHandler = function (e) {
            const nodeGroup = e.target.closest('.node-group');
            if (!nodeGroup) return;
            nodeGroup.classList.remove('hovered');
        };
        graphContent.addEventListener('mouseleave', _interactionMouseLeaveHandler, true);
    }

    /**
     * Highlight or unhighlight edges connected to a specific node.
     * @param {Element} graphContent - The graph content container element
     * @param {string} nodeId - ID of the node whose edges to highlight
     * @param {boolean} highlight - True to highlight, false to remove highlights
     */
    function highlightConnectedEdges(graphContent, nodeId, highlight) {
        const edgePaths = graphContent.querySelectorAll('.edge-path');
        for (const path of edgePaths) {
            const from = path.getAttribute('data-from');
            const to = path.getAttribute('data-to');
            if (from === nodeId || to === nodeId) {
                if (highlight) {
                    path.classList.add('tensor-highlighted');
                    path.setAttribute('marker-end', 'url(#arrowhead-highlight)');
                    path.parentNode.appendChild(path);
                } else {
                    path.classList.remove('tensor-highlighted');
                    path.setAttribute('marker-end', 'url(#arrowhead)');
                }
            }
        }
    }

    /**
     * Highlight or unhighlight edges carrying a given tensor.
     * @param {SVGSVGElement} svgElement - The SVG element containing the graph
     * @param {string} tensorName - Name of the tensor to match on edges
     * @param {boolean} highlight - True to highlight, false to remove highlights
     * @param {string} [contextNodeId] - If provided, only highlight edges
     *   connected to this node (prevents fan-out from lighting up the whole graph)
     */
    function highlightEdgesByTensor(svgElement, tensorName, highlight, contextNodeId) {
        const graphContent = svgElement.querySelector('#graph-content');
        if (!graphContent) return;
        const edgePaths = graphContent.querySelectorAll('.edge-path');
        for (const path of edgePaths) {
            const edgeTensor = path.getAttribute('data-tensor');
            const isCross = path.classList.contains('cross-edge');
            var shouldHighlight = false;

            if (isCross) {
                // Fan paths: exact tensor match
                // Trunk paths: comma-separated list, highlight if tensor is included
                if (edgeTensor === tensorName) {
                    shouldHighlight = true;
                } else if (edgeTensor && edgeTensor.indexOf(',') !== -1) {
                    var tensors = edgeTensor.split(',');
                    if (tensors.indexOf(tensorName) !== -1) shouldHighlight = true;
                }
            } else {
                if (edgeTensor === tensorName) {
                    if (contextNodeId) {
                        var from = path.getAttribute('data-from');
                        var to = path.getAttribute('data-to');
                        if (from !== contextNodeId && to !== contextNodeId) continue;
                    }
                    shouldHighlight = true;
                }
            }

            if (shouldHighlight) {
                if (highlight) {
                    path.classList.add('tensor-highlighted');
                    if (path.getAttribute('marker-end')) {
                        path.setAttribute('marker-end', 'url(#arrowhead-highlight)');
                    }
                    path.parentNode.appendChild(path);
                } else {
                    path.classList.remove('tensor-highlighted');
                    if (path.getAttribute('marker-end')) {
                        path.setAttribute('marker-end', 'url(#arrowhead)');
                    }
                }
            }
        }
    }

    /**
     * Remove all edge highlights from the graph.
     * @param {SVGSVGElement} svgElement - The SVG element containing the graph
     */
    function clearAllEdgeHighlights(svgElement) {
        const graphContent = svgElement.querySelector('#graph-content');
        if (!graphContent) return;
        const edgePaths = graphContent.querySelectorAll('.edge-path');
        for (const path of edgePaths) {
            path.classList.remove('highlighted', 'tensor-highlighted');
            // Only reset marker-end on paths that have arrows (fan-out and in-graph edges)
            if (path.getAttribute('marker-end')) {
                path.setAttribute('marker-end', 'url(#arrowhead)');
            }
        }
    }


    /**
     * Set up zoom and pan controls on the SVG via mouse wheel and drag.
     * @param {SVGSVGElement} svgElement - The SVG element to attach zoom/pan to
     * @returns {{getTransform: Function, setTransform: Function, resetTransform: Function}} Zoom/pan controls
     */
    function setupZoomPan(svgElement) {
        // Clean up previous zoom/pan listeners to prevent stacking
        if (_zoomPanCleanup) {
            _zoomPanCleanup();
            _zoomPanCleanup = null;
        }

        const graphContent = svgElement.querySelector('#graph-content');
        if (!graphContent) return null;

        const transform = { x: 0, y: 0, scale: 1 };
        let isPanning = false;
        let panStart = { x: 0, y: 0 };
        let panStartTransform = { x: 0, y: 0 };

        // Clamp pan so the viewport stays within graph bounds + margin
        function clampTransform() {
            try {
                var bbox = graphContent.getBBox();
                if (!bbox || bbox.width === 0) return;
            } catch (_) { return; }
            var svgRect = svgElement.getBoundingClientRect();
            var svgW = svgRect.width || svgElement.clientWidth || 800;
            var svgH = svgRect.height || svgElement.clientHeight || 600;
            var s = transform.scale;
            // Allow half-viewport margin beyond graph edges
            var marginX = svgW * 0.5;
            var marginY = svgH * 0.5;
            var minX = -(bbox.x + bbox.width) * s - marginX + svgW;
            var maxX = -bbox.x * s + marginX;
            var minY = -(bbox.y + bbox.height) * s - marginY + svgH;
            var maxY = -bbox.y * s + marginY;
            if (minX > maxX) { var midX = (minX + maxX) / 2; minX = midX; maxX = midX; }
            if (minY > maxY) { var midY = (minY + maxY) / 2; minY = midY; maxY = midY; }
            transform.x = Math.max(minX, Math.min(maxX, transform.x));
            transform.y = Math.max(minY, Math.min(maxY, transform.y));
        }

        function applyTransform() {
            if (isNaN(transform.x) || isNaN(transform.y) || isNaN(transform.scale)) {
                transform.x = 0; transform.y = 0; transform.scale = 1;
            }
            clampTransform();
            graphContent.setAttribute(
                'transform',
                `translate(${transform.x},${transform.y}) scale(${transform.scale})`
            );
            svgElement.dispatchEvent(new CustomEvent('zoom-changed', {
                detail: { scale: transform.scale },
            }));
        }

        function onWheel(e) {
            e.preventDefault();
            if (e.ctrlKey || e.metaKey) {
                var factor = e.deltaY < 0 ? 1.15 : 0.85;
                var rect = svgElement.getBoundingClientRect();
                var cx = e.clientX - rect.left;
                var cy = e.clientY - rect.top;
                var newScale = transform.scale * factor;
                transform.x = cx - (cx - transform.x) * (newScale / transform.scale);
                transform.y = cy - (cy - transform.y) * (newScale / transform.scale);
                transform.scale = newScale;
                applyTransform();
                svgElement.dispatchEvent(new Event('zoom-changed'));
            } else {
                var scrollSpeed = 1.5;
                transform.x -= e.deltaX * scrollSpeed;
                transform.y -= e.deltaY * scrollSpeed;
                applyTransform();
            }
        }

        // Middle-click autoscroll
        let isAutoScrolling = false;
        let autoScrollOrigin = { x: 0, y: 0 };
        let autoScrollCursor = { x: 0, y: 0 };
        let autoScrollRAF = null;

        function autoScrollLoop() {
            if (!isAutoScrolling) return;
            var rawDy = autoScrollCursor.y - autoScrollOrigin.y;
            var dy = -Math.sign(rawDy) * Math.pow(Math.abs(rawDy), 1.4) * 0.015;
            if (Math.abs(rawDy) > 3) {
                transform.y += dy;
                applyTransform();
            }
            autoScrollRAF = requestAnimationFrame(autoScrollLoop);
        }

        function onSvgMousedownMiddle(e) {
            if (e.button === 1) {
                e.preventDefault();
                if (isAutoScrolling) {
                    isAutoScrolling = false;
                    svgElement.style.cursor = '';
                    if (autoScrollRAF) {
                        cancelAnimationFrame(autoScrollRAF);
                        autoScrollRAF = null;
                    }
                } else {
                    isAutoScrolling = true;
                    autoScrollOrigin.x = e.clientX;
                    autoScrollOrigin.y = e.clientY;
                    autoScrollCursor.x = e.clientX;
                    autoScrollCursor.y = e.clientY;
                    svgElement.style.cursor = 'ns-resize';
                    autoScrollRAF = requestAnimationFrame(autoScrollLoop);
                }
            }
        }

        function onWindowMousemoveAutoscroll(e) {
            if (!isAutoScrolling) return;
            autoScrollCursor.x = e.clientX;
            autoScrollCursor.y = e.clientY;
        }

        function onWindowMousedownAutoStop(e) {
            if (e.button === 0 && isAutoScrolling) {
                isAutoScrolling = false;
                svgElement.style.cursor = '';
                if (autoScrollRAF) {
                    cancelAnimationFrame(autoScrollRAF);
                    autoScrollRAF = null;
                }
            }
        }

        function onAuxclick(e) {
            if (e.button === 1) e.preventDefault();
        }

        // Pan with mouse drag
        function onSvgMousedownPan(e) {
            if (e.button !== 0) return;
            e.preventDefault();
            if (e.target.closest('.node-group')) return;
            isPanning = true;
            panStart.x = e.clientX;
            panStart.y = e.clientY;
            panStartTransform.x = transform.x;
            panStartTransform.y = transform.y;
            svgElement.style.cursor = 'grabbing';
        }

        function onWindowMousemovePan(e) {
            if (!isPanning) return;
            const dx = e.clientX - panStart.x;
            const dy = e.clientY - panStart.y;
            transform.x = panStartTransform.x + dx;
            transform.y = panStartTransform.y + dy;
            applyTransform();
        }

        function onWindowMouseup() {
            if (isPanning) {
                isPanning = false;
                svgElement.style.cursor = '';
            }
        }

        svgElement.addEventListener('wheel', onWheel, { passive: false });
        svgElement.addEventListener('mousedown', onSvgMousedownMiddle);
        window.addEventListener('mousemove', onWindowMousemoveAutoscroll);
        window.addEventListener('mousedown', onWindowMousedownAutoStop);
        svgElement.addEventListener('auxclick', onAuxclick);
        svgElement.addEventListener('mousedown', onSvgMousedownPan);
        window.addEventListener('mousemove', onWindowMousemovePan);
        window.addEventListener('mouseup', onWindowMouseup);

        _zoomPanCleanup = function () {
            svgElement.removeEventListener('wheel', onWheel);
            svgElement.removeEventListener('mousedown', onSvgMousedownMiddle);
            window.removeEventListener('mousemove', onWindowMousemoveAutoscroll);
            window.removeEventListener('mousedown', onWindowMousedownAutoStop);
            svgElement.removeEventListener('auxclick', onAuxclick);
            svgElement.removeEventListener('mousedown', onSvgMousedownPan);
            window.removeEventListener('mousemove', onWindowMousemovePan);
            window.removeEventListener('mouseup', onWindowMouseup);
            if (autoScrollRAF) {
                cancelAnimationFrame(autoScrollRAF);
                autoScrollRAF = null;
            }
        };

        function fitToView() {
            const bbox = graphContent.getBBox();
            if (bbox.width === 0 || bbox.height === 0) return;

            const svgRect = svgElement.getBoundingClientRect();
            const svgW = svgRect.width || svgElement.clientWidth || 800;
            const svgH = svgRect.height || svgElement.clientHeight || 600;

            const pad = 40;
            const scaleX = (svgW - pad * 2) / bbox.width;
            const scaleY = (svgH - pad * 2) / bbox.height;
            const newScale = Math.min(scaleX, scaleY, 3.0);

            transform.scale = newScale;
            transform.x = (svgW - bbox.width * newScale) / 2 - bbox.x * newScale;
            transform.y = (svgH - bbox.height * newScale) / 2 - bbox.y * newScale;

            applyTransform();
        }

        /** Focus on a specific node position, centering it without changing zoom level. */
        function focusNode(nodeX, nodeY, nodeW, nodeH) {
            // Reject NaN inputs to prevent permanent transform corruption
            if (isNaN(nodeX) || isNaN(nodeY) || isNaN(nodeW) || isNaN(nodeH)) {
                console.warn('[PAN] focusNode rejected NaN input:', {nodeX, nodeY, nodeW, nodeH});
                return;
            }
            const svgRect = svgElement.getBoundingClientRect();
            const svgW = svgRect.width || svgElement.clientWidth || 800;
            const svgH = svgRect.height || svgElement.clientHeight || 600;

            const refWidth = LAYOUT.nodeWidth;

            // Keep current scale, but ensure minimum readable size
            var newScale = transform.scale;
            var minReadable = 120 / (nodeW || refWidth);
            if (newScale < minReadable) newScale = minReadable;

            // Center the node in the viewport
            const cx = nodeX + (nodeW || refWidth) / 2;
            const cy = nodeY + (nodeH || LAYOUT.nodeHeight) / 2;
            transform.scale = newScale;
            transform.x = svgW * 0.35 - cx * newScale;
            transform.y = svgH * 0.25 - cy * newScale;

            applyTransform();
        }

        return {
            getTransform: function () { return { ...transform }; },
            setTransform: function (x, y, scale) {
                transform.x = x;
                transform.y = y;
                transform.scale = Math.min(20.0, Math.max(0.05, scale));
                applyTransform();
            },
            fitToView: fitToView,
            focusNode: focusNode,
        };
    }



    /** Group nodes/edges by subgraph; identify cross-edges and graph I/O edges. */
    function _groupBySubgraph(nodes, edges, subgraphsList, graphData) {
        var nodeSgMap = new Map();
        var subgraphNodes = new Map();
        var subgraphEdges = new Map();
        var crossEdges = [];

        for (var si = 0; si < subgraphsList.length; si++) {
            subgraphNodes.set(subgraphsList[si].id, []);
            subgraphEdges.set(subgraphsList[si].id, []);
        }

        for (var ni = 0; ni < nodes.length; ni++) {
            var sgId = nodes[ni].subgraph_id;
            if (sgId) {
                nodeSgMap.set(nodes[ni].id, sgId);
                if (!subgraphNodes.has(sgId)) {
                    subgraphNodes.set(sgId, []);
                    subgraphEdges.set(sgId, []);
                }
                subgraphNodes.get(sgId).push(nodes[ni]);
            }
        }

        for (var ei = 0; ei < edges.length; ei++) {
            var e = edges[ei];
            var fromSg = e.from_node ? nodeSgMap.get(e.from_node) : null;
            var toSg = e.to_node ? nodeSgMap.get(e.to_node) : null;

            if (fromSg && toSg && fromSg === toSg) {
                subgraphEdges.get(fromSg).push(e);
            } else if (fromSg && toSg && fromSg !== toSg) {
                crossEdges.push(e);
            } else if (!fromSg && toSg) {
                subgraphEdges.get(toSg).push(e);
            }
        }

        // Build output-to-node map: tensor name → producing node id
        var outputToNode = new Map();
        for (var ni2 = 0; ni2 < nodes.length; ni2++) {
            var outs = nodes[ni2].outputs || [];
            for (var oi2 = 0; oi2 < outs.length; oi2++) {
                outputToNode.set(outs[oi2], nodes[ni2].id);
            }
        }

        // Add graph output edges (search by node outputs, not edges)
        var graphOutputs = graphData.outputs || [];
        for (var oi = 0; oi < graphOutputs.length; oi++) {
            var out = graphOutputs[oi];
            var producer = outputToNode.get(out.name);
            // Fallback: if producer not found, connect to last node of last subgraph
            if (!producer && subgraphsList.length > 0) {
                var _lastSgId = subgraphsList[subgraphsList.length - 1].id;
                var _lastSgNodes = subgraphNodes.get(_lastSgId) || [];
                if (_lastSgNodes.length > 0) {
                    producer = _lastSgNodes[_lastSgNodes.length - 1].id;
                }
            }
            if (producer) {
                var producerSg = nodeSgMap.get(producer);
                if (producerSg && subgraphEdges.has(producerSg)) {
                    subgraphEdges.get(producerSg).push({
                        from_node: producer,
                        from_output: out.name,
                        to_node: null,
                        shape: out.shape,
                        dtype: out.dtype,
                        _isGraphOutput: true
                    });
                }
            }
        }

        // Separate graph input edges from subgraphEdges → render outside boxes
        var graphInputEdges = [];
        for (var ei2 = 0; ei2 < edges.length; ei2++) {
            var e2 = edges[ei2];
            if (!e2.from_node && e2.to_node) {
                var ts = nodeSgMap.get(e2.to_node);
                if (ts) graphInputEdges.push(e2);
            }
        }
        // Remove graph input edges from subgraphEdges (they'll be rendered externally)
        for (var _ref of subgraphEdges) {
            var _sgId = _ref[0], _sgEdges = _ref[1];
            subgraphEdges.set(_sgId, _sgEdges.filter(function(e) {
                return e.from_node !== null && e.from_node !== undefined;
            }));
        }

        return { nodeSgMap: nodeSgMap, subgraphNodes: subgraphNodes, subgraphEdges: subgraphEdges, crossEdges: crossEdges, graphInputEdges: graphInputEdges };
    }

    /** Run dagre layout on each subgraph independently; add dummy boundary nodes for cross-edges. */
    function _layoutSubgraphs(subgraphNodes, subgraphEdges, crossEdges, nodeSgMap, collapsedSubgraphs) {
        var internalPositions = new Map();
        var internalBBoxes = new Map();
        var internalEdgePaths = new Map();

        for (var _ref of subgraphNodes) {
            var sgId = _ref[0], subNodes = _ref[1];
            if (subNodes.length === 0) {
                internalBBoxes.set(sgId, { width: 200, height: 100 });
                internalPositions.set(sgId, new Map());
                internalEdgePaths.set(sgId, new Map());
                continue;
            }

            if (collapsedSubgraphs && collapsedSubgraphs.has(sgId)) {
                internalBBoxes.set(sgId, { width: 240, height: 30 });
                internalPositions.set(sgId, new Map());
                internalEdgePaths.set(sgId, new Map());
                continue;
            }

            var subEdges = subgraphEdges.get(sgId) || [];

            // Dummy boundary nodes for cross-partition edges
            var dummyPrefix = '__xbnd_' + sgId + '_';
            var dummyNodes = [];
            var augEdges = subEdges.slice();
            for (var ci = 0; ci < crossEdges.length; ci++) {
                var ce = crossEdges[ci];
                var cFromSg = ce.from_node ? nodeSgMap.get(ce.from_node) : null;
                var cToSg = ce.to_node ? nodeSgMap.get(ce.to_node) : null;
                if (cFromSg === sgId && cToSg !== sgId) {
                    var dId = dummyPrefix + 'out_' + ci;
                    dummyNodes.push({ id: dId, op_type: '', category: 'other' });
                    augEdges.push({ from_node: ce.from_node, to_node: dId });
                } else if (cToSg === sgId && cFromSg !== sgId) {
                    var dId2 = dummyPrefix + 'in_' + ci;
                    dummyNodes.push({ id: dId2, op_type: '', category: 'other' });
                    augEdges.push({ from_node: dId2, to_node: ce.to_node });
                }
            }

            var allLayoutNodes = subNodes.concat(dummyNodes);
            var innerResult = dagreLayout(allLayoutNodes, augEdges);
            var positions = innerResult.positions;
            var sgEdgePaths = innerResult.edgePaths;

            // Remove dummy nodes from positions
            for (var di = 0; di < dummyNodes.length; di++) {
                positions.delete(dummyNodes[di].id);
            }

            // Normalize positions to start from (0, 0)
            var minX = Infinity, minY = Infinity;
            for (var _ref2 of positions) {
                var pos = _ref2[1];
                if (pos.x < minX) minX = pos.x;
                if (pos.y < minY) minY = pos.y;
            }
            for (var _ref3 of positions) {
                var pos2 = _ref3[1];
                pos2.x -= minX;
                pos2.y -= minY;
            }
            if (minX !== Infinity) {
                for (var _ref4 of sgEdgePaths) {
                    var pts = _ref4[1];
                    for (var pi = 0; pi < pts.length; pi++) {
                        pts[pi] = { x: pts[pi].x - minX, y: pts[pi].y - minY };
                    }
                }
            }

            var maxX = 0, maxY = 0;
            for (var _ref5 of positions) {
                var pos3 = _ref5[1];
                if (pos3.x + pos3.w > maxX) maxX = pos3.x + pos3.w;
                if (pos3.y + pos3.h > maxY) maxY = pos3.y + pos3.h;
            }

            internalBBoxes.set(sgId, { width: maxX, height: maxY });
            internalPositions.set(sgId, positions);
            internalEdgePaths.set(sgId, sgEdgePaths);
        }

        return { internalPositions: internalPositions, internalBBoxes: internalBBoxes, internalEdgePaths: internalEdgePaths };
    }

    /** Create partition-level dagre DAG for subgraph box placement. */
    function _layoutPartitionDAG(subgraphsList, internalBBoxes, crossEdges, nodeSgMap, collapsedSubgraphs) {
        var boxSizes = new Map();
        for (var si = 0; si < subgraphsList.length; si++) {
            var sg = subgraphsList[si];
            var bbox = internalBBoxes.get(sg.id) || { width: 200, height: 100 };
            if (collapsedSubgraphs && collapsedSubgraphs.has(sg.id)) {
                boxSizes.set(sg.id, { w: 280, h: 56 });
            } else {
                boxSizes.set(sg.id, { w: bbox.width + BOX_PADDING * 2, h: bbox.height + BOX_PADDING * 2 + LABEL_SPACE });
            }
        }

        var pg = new dagre.graphlib.Graph();
        pg.setGraph({ rankdir: 'TB', ranksep: 80, nodesep: 60, marginx: 60, marginy: 60 });
        pg.setDefaultEdgeLabel(function () { return {}; });
        for (var si2 = 0; si2 < subgraphsList.length; si2++) {
            var bs = boxSizes.get(subgraphsList[si2].id);
            pg.setNode(subgraphsList[si2].id, { width: bs.w, height: bs.h });
        }
        var partEdgeSet = new Set();
        for (var ci = 0; ci < crossEdges.length; ci++) {
            var ce = crossEdges[ci];
            var fromSg = nodeSgMap.get(ce.from_node);
            var toSg = nodeSgMap.get(ce.to_node);
            if (fromSg && toSg && fromSg !== toSg) {
                var k = fromSg + '\u2192' + toSg;
                if (!partEdgeSet.has(k)) {
                    partEdgeSet.add(k);
                    pg.setEdge(fromSg, toSg);
                }
            }
        }
        dagre.layout(pg);

        var partitionPositions = new Map();
        pg.nodes().forEach(function (id) {
            var dn = pg.node(id);
            partitionPositions.set(id, {
                x: dn.x - dn.width / 2,
                y: dn.y - dn.height / 2,
                w: dn.width,
                h: dn.height,
            });
        });

        var partitionEdgePaths = new Map();
        pg.edges().forEach(function (e) {
            var de = pg.edge(e);
            if (de && de.points) {
                partitionEdgePaths.set(e.v + '\u2192' + e.w, de.points);
            }
        });

        return { partitionPositions: partitionPositions, partitionEdgePaths: partitionEdgePaths };
    }

    /** Offset subgraph-local positions to global coordinates. */
    function _offsetInternalPositions(internalPositions, internalEdgePaths, partitionPositions, collapsedSubgraphs) {
        var allPositions = new Map();
        var allEdgePaths = new Map();
        for (var _ref of internalPositions) {
            var sgId = _ref[0], positions = _ref[1];
            if (collapsedSubgraphs && collapsedSubgraphs.has(sgId)) continue;
            var boxPos = partitionPositions.get(sgId);
            if (!boxPos) continue;
            var offsetX = boxPos.x + BOX_PADDING;
            var offsetY = boxPos.y + BOX_PADDING + LABEL_SPACE;

            for (var _ref2 of positions) {
                var nodeId = _ref2[0], pos = _ref2[1];
                pos.x += offsetX;
                pos.y += offsetY;
                allPositions.set(nodeId, pos);
            }

            var sgEdgePaths = internalEdgePaths.get(sgId);
            if (sgEdgePaths) {
                var offsetPaths = new Map();
                for (var _ref3 of sgEdgePaths) {
                    var key = _ref3[0], pts = _ref3[1];
                    offsetPaths.set(key, pts.map(function (p) {
                        return { x: p.x + offsetX, y: p.y + offsetY };
                    }));
                }
                allEdgePaths.set(sgId, offsetPaths);
            }
        }
        return { allPositions: allPositions, allEdgePaths: allEdgePaths };
    }

    /** Render subgraph background rects with labels and toggle buttons. */
    function _renderPartitionBackgrounds(subgraphsList, partitionPositions, collapsedSubgraphs, bgLayer) {
        for (var si = 0; si < subgraphsList.length; si++) {
            var sg = subgraphsList[si];
            var boxPos = partitionPositions.get(sg.id);
            if (!boxPos) continue;

            var device = (sg.device || '').toLowerCase();
            var isNpu = device.indexOf('npu') !== -1;
            var isCollapsed = collapsedSubgraphs && collapsedSubgraphs.has(sg.id);

            var rect = svgEl('rect', {
                x: boxPos.x, y: boxPos.y,
                width: boxPos.w, height: boxPos.h,
                rx: 16, ry: 16,
                fill: isNpu ? '#eef2ff' : '#fef3c7',
                stroke: isNpu ? (isCollapsed ? '#818cf8' : '#c7d2fe') : (isCollapsed ? '#fbbf24' : '#fde68a'),
                'stroke-width': isCollapsed ? 2 : 1.5,
                class: 'subgraph-bg',
                cursor: 'pointer',
            });
            rect.setAttribute('data-subgraph-id', sg.id);
            if (isCollapsed) rect.setAttribute('data-collapsed', 'true');
            bgLayer.appendChild(rect);

            if (isCollapsed) {
                var nodeCount = sg.node_count || 0;
                var label = svgEl('text', {
                    x: boxPos.x + boxPos.w / 2,
                    y: boxPos.y + boxPos.h / 2 + 1,
                    'text-anchor': 'middle',
                    'dominant-baseline': 'central',
                    'font-size': '13px',
                    'font-weight': '600',
                    fill: '#475569',
                    class: 'subgraph-label',
                    'pointer-events': 'none',
                });
                label.textContent = '\u25B6 ' + sg.id + (sg.device ? ' (' + sg.device + ')' : '') + ' \u2014 ' + nodeCount + ' nodes';
                label.setAttribute('data-subgraph-id', sg.id);
                bgLayer.appendChild(label);
            } else {
                var toggle = svgEl('text', {
                    x: boxPos.x + 12,
                    y: boxPos.y + 18,
                    'font-size': '13px',
                    'font-weight': '600',
                    fill: '#64748b',
                    class: 'subgraph-label subgraph-toggle',
                    cursor: 'pointer',
                });
                toggle.textContent = '\u25BC ' + sg.id + (sg.device ? ' (' + sg.device + ')' : '');
                toggle.setAttribute('data-subgraph-id', sg.id);
                bgLayer.appendChild(toggle);
            }
        }
    }

    /** Render bundled cross-partition edges: fan-in → trunk → fan-out. */
    function _renderCrossPartitionEdges(crossEdges, nodeSgMap, partitionPositions, partitionEdgePaths, allPositions, collapsedSubgraphs, edgeLayer) {
        var renderedEdges = [];

        // Group cross-edges by (fromSg → toSg) pair
        var pairEdges = new Map();
        for (var ci = 0; ci < crossEdges.length; ci++) {
            var ce = crossEdges[ci];
            var cFromSg = nodeSgMap.get(ce.from_node);
            var cToSg = nodeSgMap.get(ce.to_node);
            if (!cFromSg || !cToSg) continue;
            var pk = cFromSg + '\u2192' + cToSg;
            if (!pairEdges.has(pk)) pairEdges.set(pk, []);
            pairEdges.get(pk).push(ce);
        }

        // Count pairs per source/target subgraph for spreading collection/entry points
        var srcPairCount = new Map(), srcPairIdx = new Map();
        var tgtPairCount = new Map(), tgtPairIdx = new Map();
        for (var _ref of pairEdges) {
            var pk2 = _ref[0];
            var sp = pk2.split('\u2192');
            var si = srcPairCount.get(sp[0]) || 0;
            srcPairIdx.set(pk2, si);
            srcPairCount.set(sp[0], si + 1);
            var ti = tgtPairCount.get(sp[1]) || 0;
            tgtPairIdx.set(pk2, ti);
            tgtPairCount.set(sp[1], ti + 1);
        }

        for (var _ref2 of pairEdges) {
            var pairKey = _ref2[0], pEdges = _ref2[1];
            var parts = pairKey.split('\u2192');
            var fromSgId = parts[0], toSgId = parts[1];
            var fromBox = partitionPositions.get(fromSgId);
            var toBox = partitionPositions.get(toSgId);
            if (!fromBox || !toBox) continue;

            var partPoints = partitionEdgePaths.get(pairKey);
            var groupId = pairKey;

            var tensorNames = [];
            for (var ei = 0; ei < pEdges.length; ei++) {
                if (pEdges[ei].from_output) tensorNames.push(pEdges[ei].from_output);
            }

            // Collection point at source subgraph bottom edge
            var srcN = srcPairCount.get(fromSgId) || 1;
            var srcI = srcPairIdx.get(pairKey) || 0;
            var srcSpread = Math.min(fromBox.w * 0.4, 400) / Math.max(srcN - 1, 1);
            var collectX = fromBox.x + fromBox.w / 2 + (srcI - (srcN - 1) / 2) * srcSpread;
            var collectY = fromBox.y + fromBox.h;

            // Entry point at target subgraph top edge
            var tgtN = tgtPairCount.get(toSgId) || 1;
            var tgtI = tgtPairIdx.get(pairKey) || 0;
            var tgtSpread = Math.min(toBox.w * 0.4, 400) / Math.max(tgtN - 1, 1);
            var entryX = toBox.x + toBox.w / 2 + (tgtI - (tgtN - 1) / 2) * tgtSpread;
            var entryY = toBox.y;

            // --- A) Dashed fan-in: each source node → collection point ---
            var BRACE_H = 30;
            for (var ei2 = 0; ei2 < pEdges.length; ei2++) {
                var srcEdge = pEdges[ei2];
                var srcPos = allPositions.get(srcEdge.from_node);
                if (!srcPos) continue;

                var srcCX = srcPos.x + srcPos.w / 2;
                var srcBottom = srcPos.y + srcPos.h;

                var fanPoints = [
                    { x: srcCX, y: srcBottom },
                    { x: srcCX, y: collectY - BRACE_H },
                    { x: collectX, y: collectY - BRACE_H },
                    { x: collectX, y: collectY - BRACE_H * 0.3 },
                    { x: collectX, y: collectY }
                ];
                var fanD = edgePointsToPath(fanPoints, 0);

                var fanHit = svgEl('path', {
                    d: fanD, fill: 'none', stroke: 'transparent', 'stroke-width': 12,
                    class: 'edge-hitarea',
                });
                fanHit.setAttribute('data-from', srcEdge.from_node);
                fanHit.setAttribute('data-to', srcEdge.to_node);
                if (srcEdge.from_output) fanHit.setAttribute('data-tensor', srcEdge.from_output);
                fanHit.setAttribute('data-cross-group', groupId);
                edgeLayer.appendChild(fanHit);

                var fanPath = svgEl('path', {
                    d: fanD, fill: 'none',
                    stroke: EDGE_STYLE.stroke, 'stroke-width': EDGE_STYLE.strokeWidth,
                    'stroke-dasharray': '6,4',
                    class: 'edge-path cross-edge cross-fan', 'pointer-events': 'none',
                });
                fanPath.setAttribute('data-from', srcEdge.from_node);
                fanPath.setAttribute('data-to', srcEdge.to_node);
                if (srcEdge.from_output) fanPath.setAttribute('data-tensor', srcEdge.from_output);
                fanPath.setAttribute('data-cross-group', groupId);
                edgeLayer.appendChild(fanPath);
                renderedEdges.push(fanPath);
            }

            // --- B) Solid trunk: collection point → entry point ---
            var trunkPoints = [];
            trunkPoints.push({ x: collectX, y: collectY });

            if (partPoints && partPoints.length > 2) {
                for (var pi = 1; pi < partPoints.length - 1; pi++) {
                    trunkPoints.push({ x: partPoints[pi].x, y: partPoints[pi].y });
                }
            } else {
                var trunkMidY = (collectY + entryY) / 2;
                trunkPoints.push({ x: (collectX + entryX) / 2, y: trunkMidY });
            }
            if (trunkPoints[trunkPoints.length - 1].x !== entryX) {
                trunkPoints.push({ x: entryX, y: entryY - 15 });
            }
            trunkPoints.push({ x: entryX, y: entryY });

            var trunkD = edgePointsToPath(trunkPoints, (collapsedSubgraphs && collapsedSubgraphs.has(toSgId)) ? ARROW_LEN : 0);

            var trunkHit = svgEl('path', {
                d: trunkD, fill: 'none', stroke: 'transparent', 'stroke-width': 14,
                class: 'edge-hitarea',
            });
            trunkHit.setAttribute('data-cross-group', groupId);
            trunkHit.setAttribute('data-tensor', tensorNames.join(','));
            edgeLayer.appendChild(trunkHit);

            var trunkAttrs = {
                d: trunkD, fill: 'none',
                stroke: EDGE_STYLE.stroke, 'stroke-width': EDGE_STYLE.strokeWidth + 0.5,
                class: 'edge-path cross-edge cross-trunk', 'pointer-events': 'none',
            };
            if (collapsedSubgraphs && collapsedSubgraphs.has(toSgId)) {
                trunkAttrs['marker-end'] = 'url(#arrowhead)';
            }
            var trunkPath = svgEl('path', trunkAttrs);
            trunkPath.setAttribute('data-cross-group', groupId);
            trunkPath.setAttribute('data-tensor', tensorNames.join(','));
            edgeLayer.appendChild(trunkPath);
            renderedEdges.push(trunkPath);

            // --- C) Dashed fan-out: entry point → each target node ---
            for (var ei3 = 0; ei3 < pEdges.length; ei3++) {
                var tgtEdge = pEdges[ei3];
                var tgtPos = allPositions.get(tgtEdge.to_node);
                if (!tgtPos) continue;

                var tgtCX = tgtPos.x + tgtPos.w / 2;
                var tgtTop = tgtPos.y;

                var fanOutPoints = [
                    { x: entryX, y: entryY },
                    { x: entryX, y: entryY + BRACE_H * 0.3 },
                    { x: tgtCX, y: entryY + BRACE_H },
                    { x: tgtCX, y: entryY + BRACE_H },
                    { x: tgtCX, y: tgtTop }
                ];
                var fanOutD = edgePointsToPath(fanOutPoints, ARROW_LEN);

                var fanOutHit = svgEl('path', {
                    d: fanOutD, fill: 'none', stroke: 'transparent', 'stroke-width': 12,
                    class: 'edge-hitarea',
                });
                fanOutHit.setAttribute('data-from', tgtEdge.from_node);
                fanOutHit.setAttribute('data-to', tgtEdge.to_node);
                if (tgtEdge.from_output) fanOutHit.setAttribute('data-tensor', tgtEdge.from_output);
                fanOutHit.setAttribute('data-cross-group', groupId);
                edgeLayer.appendChild(fanOutHit);

                var fanOutPath = svgEl('path', {
                    d: fanOutD, fill: 'none',
                    stroke: EDGE_STYLE.stroke, 'stroke-width': EDGE_STYLE.strokeWidth,
                    'stroke-dasharray': '6,4',
                    'marker-end': 'url(#arrowhead)',
                    class: 'edge-path cross-edge cross-fan', 'pointer-events': 'none',
                });
                fanOutPath.setAttribute('data-from', tgtEdge.from_node);
                fanOutPath.setAttribute('data-to', tgtEdge.to_node);
                if (tgtEdge.from_output) fanOutPath.setAttribute('data-tensor', tgtEdge.from_output);
                fanOutPath.setAttribute('data-cross-group', groupId);
                edgeLayer.appendChild(fanOutPath);
                renderedEdges.push(fanOutPath);
            }
        }

        return renderedEdges;
    }

    /** Render graph input tensor node boxes and their connecting edges. */
    function _renderGraphInputNodes(graphInputEdges, nodeSgMap, partitionPositions, allPositions, collapsedSubgraphs, edgeLayer, nodeLayer) {
        var renderedEdges = [];

        for (var gi = 0; gi < graphInputEdges.length; gi++) {
            var gEdge = graphInputEdges[gi];
            var tgtSgId = nodeSgMap.get(gEdge.to_node);
            var tgtBox = tgtSgId ? partitionPositions.get(tgtSgId) : null;
            if (!tgtBox) continue;

            var tgtPos = allPositions.get(gEdge.to_node);
            var tgtIsCollapsed = collapsedSubgraphs && collapsedSubgraphs.has(tgtSgId);
            var tgtCX = tgtPos ? (tgtPos.x + tgtPos.w / 2) : (tgtBox.x + tgtBox.w / 2);
            var ioX = tgtCX - IO_NODE_W / 2;
            var ioY = tgtBox.y - 50 - IO_NODE_H;

            var ioG = svgEl('g', {
                class: 'node-group graph-io-node',
                'data-tensor': gEdge.from_output || '',
                'data-io-type': 'input',
            });
            var ioRect = svgEl('rect', {
                x: ioX, y: ioY, width: IO_NODE_W, height: IO_NODE_H,
                rx: IO_NODE_H / 2, ry: IO_NODE_H / 2,
                fill: '#e0f2fe', stroke: '#38bdf8', 'stroke-width': 1.5,
            });
            ioG.appendChild(ioRect);
            var ioText = svgEl('text', {
                x: tgtCX, y: ioY + IO_NODE_H / 2,
                'text-anchor': 'middle', 'dominant-baseline': 'central',
                fill: '#0369a1', 'font-size': '11', 'font-weight': '600',
                'pointer-events': 'none',
                'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            });
            ioText.textContent = truncate(gEdge.from_output || 'input', 18);
            ioG.appendChild(ioText);
            if (gEdge.shape && gEdge.shape.length > 0) {
                var shapeStr = '[' + gEdge.shape.join('\u00d7') + ']';
                var ioShape = svgEl('text', {
                    x: tgtCX, y: ioY + IO_NODE_H + 12,
                    'text-anchor': 'middle', 'dominant-baseline': 'central',
                    fill: '#64748b', 'font-size': '9', 'pointer-events': 'none',
                });
                ioShape.textContent = shapeStr;
                ioG.appendChild(ioShape);
            }
            nodeLayer.appendChild(ioG);

            var inputEndY = tgtIsCollapsed ? tgtBox.y : tgtPos.y;
            var inputPts = [
                { x: tgtCX, y: ioY + IO_NODE_H },
                { x: tgtCX, y: tgtBox.y - 15 },
                { x: tgtCX, y: inputEndY }
            ];
            var inputD = edgePointsToPath(inputPts, ARROW_LEN);

            var inputHit = svgEl('path', {
                d: inputD, fill: 'none', stroke: 'transparent', 'stroke-width': 12,
                class: 'edge-hitarea',
            });
            if (gEdge.to_node) inputHit.setAttribute('data-to', gEdge.to_node);
            if (gEdge.from_output) inputHit.setAttribute('data-tensor', gEdge.from_output);
            edgeLayer.appendChild(inputHit);

            var inputPath = svgEl('path', {
                d: inputD, fill: 'none',
                stroke: EDGE_STYLE.stroke, 'stroke-width': EDGE_STYLE.strokeWidth,
                'stroke-dasharray': '6,4',
                'marker-end': 'url(#arrowhead)',
                class: 'edge-path cross-edge', 'pointer-events': 'none',
            });
            if (gEdge.to_node) inputPath.setAttribute('data-to', gEdge.to_node);
            if (gEdge.from_output) inputPath.setAttribute('data-tensor', gEdge.from_output);
            edgeLayer.appendChild(inputPath);
            renderedEdges.push(inputPath);
        }

        return renderedEdges;
    }

    /** Render graph output tensor node boxes and their connecting edges. */
    function _renderGraphOutputNodes(subgraphEdges, partitionPositions, allPositions, collapsedSubgraphs, edgeLayer, nodeLayer) {
        var renderedEdges = [];

        for (var _ref of subgraphEdges) {
            var sgId = _ref[0], sgEdges = _ref[1];
            var outEdges = sgEdges.filter(function(e) { return e._isGraphOutput; });
            if (outEdges.length === 0) continue;
            subgraphEdges.set(sgId, sgEdges.filter(function(e) { return !e._isGraphOutput; }));
            var sgBox = partitionPositions.get(sgId);
            if (!sgBox) continue;

            for (var oei = 0; oei < outEdges.length; oei++) {
                var oEdge = outEdges[oei];
                var srcPos = allPositions.get(oEdge.from_node);
                var srcIsCollapsed = collapsedSubgraphs && collapsedSubgraphs.has(sgId);

                var srcCX = srcPos ? (srcPos.x + srcPos.w / 2) : (sgBox.x + sgBox.w / 2);
                var boxBottom = sgBox.y + sgBox.h;
                var oioX = srcCX - IO_NODE_W / 2;
                var oioY = boxBottom + 50;

                var oioG = svgEl('g', {
                    class: 'node-group graph-io-node',
                    'data-tensor': oEdge.from_output || '',
                    'data-io-type': 'output',
                });
                var oioRect = svgEl('rect', {
                    x: oioX, y: oioY, width: IO_NODE_W, height: IO_NODE_H,
                    rx: IO_NODE_H / 2, ry: IO_NODE_H / 2,
                    fill: '#fef3c7', stroke: '#f59e0b', 'stroke-width': 1.5,
                });
                oioG.appendChild(oioRect);
                var oioText = svgEl('text', {
                    x: srcCX, y: oioY + IO_NODE_H / 2,
                    'text-anchor': 'middle', 'dominant-baseline': 'central',
                    fill: '#92400e', 'font-size': '11', 'font-weight': '600',
                    'pointer-events': 'none',
                    'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                });
                oioText.textContent = truncate(oEdge.from_output || 'output', 18);
                oioG.appendChild(oioText);
                if (oEdge.shape && oEdge.shape.length > 0) {
                    var oShapeStr = '[' + oEdge.shape.join('\u00d7') + ']';
                    var oioShape = svgEl('text', {
                        x: srcCX, y: oioY + IO_NODE_H + 12,
                        'text-anchor': 'middle', 'dominant-baseline': 'central',
                        fill: '#64748b', 'font-size': '9', 'pointer-events': 'none',
                    });
                    oioShape.textContent = oShapeStr;
                    oioG.appendChild(oioShape);
                }
                nodeLayer.appendChild(oioG);

                var outStartY = (srcIsCollapsed || !srcPos) ? boxBottom : (srcPos.y + srcPos.h);
                var outPts = [
                    { x: srcCX, y: outStartY },
                    { x: srcCX, y: boxBottom + 15 },
                    { x: srcCX, y: oioY }
                ];
                var outD = edgePointsToPath(outPts, ARROW_LEN);

                var outHit = svgEl('path', {
                    d: outD, fill: 'none', stroke: 'transparent', 'stroke-width': 12,
                    class: 'edge-hitarea',
                });
                if (oEdge.from_node) outHit.setAttribute('data-from', oEdge.from_node);
                if (oEdge.from_output) outHit.setAttribute('data-tensor', oEdge.from_output);
                edgeLayer.appendChild(outHit);

                var outPath = svgEl('path', {
                    d: outD, fill: 'none',
                    stroke: EDGE_STYLE.stroke, 'stroke-width': EDGE_STYLE.strokeWidth,
                    'stroke-dasharray': '6,4',
                    'marker-end': 'url(#arrowhead)',
                    class: 'edge-path cross-edge', 'pointer-events': 'none',
                });
                if (oEdge.from_node) outPath.setAttribute('data-from', oEdge.from_node);
                if (oEdge.from_output) outPath.setAttribute('data-tensor', oEdge.from_output);
                edgeLayer.appendChild(outPath);
                renderedEdges.push(outPath);
            }
        }

        return renderedEdges;
    }

    /**
     * Render a partitioned model with 2-level hierarchical layout.
     * Level 1: dagre per subgraph for internal node layout.
     * Level 2: dagre for subgraph box arrangement (vertical stacking).
     * Cross-edges: smooth Q-bezier curves using partition-level routing.
     */
    function renderPartitionedGraph(svgElement, graphData, collapsedSubgraphs) {
        var graphContent = svgElement.querySelector('#graph-content');
        if (!graphContent) return null;

        while (graphContent.firstChild) {
            graphContent.removeChild(graphContent.firstChild);
        }

        var nodes = graphData.nodes || [];
        var edges = graphData.edges || [];
        var subgraphsList = graphData.subgraphs || [];

        if (nodes.length === 0) {
            return { nodePositions: new Map(), nodeCount: 0, edgeCount: 0 };
        }

        var nodeMap = new Map();
        for (var ni = 0; ni < nodes.length; ni++) nodeMap.set(nodes[ni].id, nodes[ni]);

        // A) Group nodes/edges by subgraph
        var grouped = _groupBySubgraph(nodes, edges, subgraphsList, graphData);

        // B) Layout each subgraph independently
        var layoutResult = _layoutSubgraphs(grouped.subgraphNodes, grouped.subgraphEdges, grouped.crossEdges, grouped.nodeSgMap, collapsedSubgraphs);

        // C) Build partition-level DAG
        var partResult = _layoutPartitionDAG(subgraphsList, layoutResult.internalBBoxes, grouped.crossEdges, grouped.nodeSgMap, collapsedSubgraphs);

        // D) Offset internal positions to global coordinates
        var offsetResult = _offsetInternalPositions(layoutResult.internalPositions, layoutResult.internalEdgePaths, partResult.partitionPositions, collapsedSubgraphs);

        // E) Create SVG layers
        var bgLayer = svgEl('g', { class: 'layer-bg' });
        var edgeLayer = svgEl('g', { class: 'layer-edges' });
        var nodeLayer = svgEl('g', { class: 'layer-nodes' });
        graphContent.appendChild(bgLayer);
        graphContent.appendChild(edgeLayer);
        graphContent.appendChild(nodeLayer);

        // E.1) Partition backgrounds
        _renderPartitionBackgrounds(subgraphsList, partResult.partitionPositions, collapsedSubgraphs, bgLayer);

        // E.2) Cross-partition edges
        var renderedEdges = _renderCrossPartitionEdges(grouped.crossEdges, grouped.nodeSgMap, partResult.partitionPositions, partResult.partitionEdgePaths, offsetResult.allPositions, collapsedSubgraphs, edgeLayer);

        // E.2b) Graph input nodes
        var inputEdges = _renderGraphInputNodes(grouped.graphInputEdges, grouped.nodeSgMap, partResult.partitionPositions, offsetResult.allPositions, collapsedSubgraphs, edgeLayer, nodeLayer);
        for (var ii = 0; ii < inputEdges.length; ii++) renderedEdges.push(inputEdges[ii]);

        // E.2c) Graph output nodes
        var outputEdges = _renderGraphOutputNodes(grouped.subgraphEdges, partResult.partitionPositions, offsetResult.allPositions, collapsedSubgraphs, edgeLayer, nodeLayer);
        for (var oi = 0; oi < outputEdges.length; oi++) renderedEdges.push(outputEdges[oi]);

        // E.3) Internal edges within each subgraph
        for (var _ref of grouped.subgraphEdges) {
            var sgId = _ref[0];
            if (collapsedSubgraphs && collapsedSubgraphs.has(sgId)) continue;
            var subEdges = grouped.subgraphEdges.get(sgId) || [];
            var sgEdgePaths = offsetResult.allEdgePaths.get(sgId);
            for (var ei = 0; ei < subEdges.length; ei++) {
                var path = renderEdge(subEdges[ei], offsetResult.allPositions, edgeLayer, sgEdgePaths, graphData.tensor_info);
                if (path) renderedEdges.push(path);
            }
        }

        // E.4) Internal nodes
        for (var _ref2 of grouped.subgraphNodes) {
            var sgId2 = _ref2[0], subNodes = _ref2[1];
            if (collapsedSubgraphs && collapsedSubgraphs.has(sgId2)) continue;
            for (var ni2 = 0; ni2 < subNodes.length; ni2++) {
                var pos = offsetResult.allPositions.get(subNodes[ni2].id);
                if (pos) renderNode(subNodes[ni2], pos, edges, nodeLayer);
            }
        }

        svgElement.removeAttribute('viewBox');
        setupInteractions(svgElement, graphContent, nodeMap, edges, true);

        return {
            nodePositions: offsetResult.allPositions,
            nodeCount: nodes.length,
            edgeCount: renderedEdges.length,
            nodeMap: nodeMap,
            collapsedSubgraphs: collapsedSubgraphs || new Set(),
        };
    }


    /**
     * Render the full graph into the SVG element.
     * @param {SVGSVGElement} svgElement - The <svg> element
     * @param {object} graphData - Parsed graph: { nodes, edges, inputs, outputs, ... }
     * @param {object} [options] - Options: { collapsedSubgraphs: Set }
     * @returns {{ nodePositions: Map, nodeCount: number, edgeCount: number }}
     */
    function renderGraph(svgElement, graphData, options) {
        // If partitioned model, use hierarchical layout
        const subgraphs = graphData.subgraphs || [];
        if (subgraphs.length > 0) {
            var collapsedSet = (options && options.collapsedSubgraphs) || null;
            if (!collapsedSet) {
                // Default: all subgraphs collapsed
                collapsedSet = new Set(subgraphs.map(function(s) { return s.id; }));
            }
            return renderPartitionedGraph(svgElement, graphData, collapsedSet);
        }

        const graphContent = svgElement.querySelector('#graph-content');
        if (!graphContent) return null;

        // Clear existing content
        while (graphContent.firstChild) {
            graphContent.removeChild(graphContent.firstChild);
        }

        const nodes = graphData.nodes || [];
        const edges = graphData.edges || [];

        if (nodes.length === 0) {
            return { nodePositions: new Map(), nodeCount: 0, edgeCount: 0 };
        }

        // Build node map
        const nodeMap = new Map();
        for (const n of nodes) nodeMap.set(n.id, n);

        // Layout pipeline (dagre)
        const layoutResult = dagreLayout(nodes, edges);
        const positions = layoutResult.positions;
        const edgePaths = layoutResult.edgePaths;

        // Render subgraph background rects (behind edges and nodes)
        const subgraphGroups = new Map();
        for (const n of nodes) {
            if (n.subgraph_id) {
                if (!subgraphGroups.has(n.subgraph_id)) {
                    subgraphGroups.set(n.subgraph_id, { device: n.subgraph_device || '', nodeIds: [] });
                }
                subgraphGroups.get(n.subgraph_id).nodeIds.push(n.id);
            }
        }
        for (const [subgraphId, group] of subgraphGroups) {
            let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
            let maxW = 0, maxH = 0;
            for (const nid of group.nodeIds) {
                const pos = positions.get(nid);
                if (!pos) continue;
                if (pos.x < minX) minX = pos.x;
                if (pos.y < minY) minY = pos.y;
                if (pos.x > maxX) { maxX = pos.x; maxW = pos.w; }
                if (pos.y > maxY) { maxY = pos.y; maxH = pos.h; }
            }
            if (minX === Infinity) continue;

            const isNpu = (group.device || '').toLowerCase().indexOf('npu') !== -1;
            const fillColor = isNpu ? '#eef2ff' : '#fef3c7';
            const strokeColor = isNpu ? '#c7d2fe' : '#fde68a';

            const rect = svgEl('rect', {
                x: minX - 20,
                y: minY - 30,
                width: (maxX + maxW) - minX + 40,
                height: (maxY + maxH) - minY + 50,
                rx: 12, ry: 12,
                fill: fillColor,
                stroke: strokeColor,
                'stroke-width': 1,
                opacity: 0.6,
                class: 'subgraph-bg',
            });
            rect.setAttribute('data-subgraph-id', subgraphId);
            graphContent.appendChild(rect);

            const label = svgEl('text', {
                x: minX - 12,
                y: minY - 14,
                'font-size': '13px',
                'font-weight': '600',
                fill: '#64748b',
                class: 'subgraph-label',
            });
            label.textContent = subgraphId;
            label.setAttribute('data-subgraph-id', subgraphId);
            graphContent.appendChild(label);
        }

        // Add graph output edges (search node outputs, not edges)
        var graphOutputs = graphData.outputs || [];
        for (var oi = 0; oi < graphOutputs.length; oi++) {
            var out = graphOutputs[oi];
            var producer = null;
            for (var ni2 = 0; ni2 < nodes.length; ni2++) {
                var nOuts = nodes[ni2].outputs || [];
                if (nOuts.indexOf(out.name) !== -1) {
                    producer = nodes[ni2].id;
                    break;
                }
            }
            if (producer) {
                edges.push({
                    from_node: producer,
                    from_output: out.name,
                    to_node: null,
                    shape: out.shape,
                    dtype: out.dtype,
                    _isGraphOutput: true
                });
            }
        }

        // Render edges first (behind nodes)
        const renderedEdges = [];
        for (const edge of edges) {
            const path = renderEdge(edge, positions, graphContent, edgePaths, graphData.tensor_info);
            if (path) renderedEdges.push(path);
        }

        // Render nodes
        for (const node of nodes) {
            const pos = positions.get(node.id);
            if (pos) {
                renderNode(node, pos, edges, graphContent);
            }
        }

        // Do NOT set viewBox — let zoom/pan handle all coordinate transforms.
        // Remove any prior viewBox so the SVG uses its CSS pixel dimensions.
        svgElement.removeAttribute('viewBox');

        // Setup interactions
        setupInteractions(svgElement, graphContent, nodeMap, edges, false);

        return {
            nodePositions: positions,
            nodeCount: nodes.length,
            edgeCount: renderedEdges.length,
            nodeMap: nodeMap,
        };
    }

    /**
     * Remove all rendered elements from the graph SVG and
     * abort previous interaction listeners.
     * @param {SVGSVGElement} svgElement
     */
    function clearGraph(svgElement) {
        // Remove previous zoom/pan listeners
        if (_zoomPanCleanup) {
            _zoomPanCleanup();
            _zoomPanCleanup = null;
        }
        // Remove previous interaction listeners to prevent double-fire
        if (_interactionGraphContent) {
            if (_interactionClickHandler)
                _interactionGraphContent.removeEventListener('click', _interactionClickHandler);
            if (_interactionDblClickHandler)
                _interactionGraphContent.removeEventListener('dblclick', _interactionDblClickHandler);
            if (_interactionMouseEnterHandler)
                _interactionGraphContent.removeEventListener('mouseenter', _interactionMouseEnterHandler, true);
            if (_interactionMouseLeaveHandler)
                _interactionGraphContent.removeEventListener('mouseleave', _interactionMouseLeaveHandler, true);
            _interactionClickHandler = null;
            _interactionDblClickHandler = null;
            _interactionMouseEnterHandler = null;
            _interactionMouseLeaveHandler = null;
            _interactionGraphContent = null;
        }
        if (_interactionSvgElement) {
            if (_interactionSvgClickHandler)
                _interactionSvgElement.removeEventListener('click', _interactionSvgClickHandler);
            _interactionSvgClickHandler = null;
            _interactionSvgElement = null;
        }
        const graphContent = svgElement.querySelector('#graph-content');
        if (!graphContent) return;
        while (graphContent.firstChild) {
            graphContent.removeChild(graphContent.firstChild);
        }
    }

    window.GraphRenderer = {
        renderGraph: renderGraph,
        clearGraph: clearGraph,
        setupZoomPan: setupZoomPan,
        highlightEdgesByTensor: highlightEdgesByTensor,
        highlightConnectedEdges: highlightConnectedEdges,
        clearAllEdgeHighlights: clearAllEdgeHighlights,
    };

})();
if (typeof registerCompilerLangRefresher === 'function') {
  registerCompilerLangRefresher(function() {
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
  });
}
