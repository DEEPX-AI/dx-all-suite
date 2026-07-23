/**
 * DX Stream Pipeline — 렌더러 & 인터랙션 모듈
 * 팔레트, 캔버스 초기화, 히트테스트, 마우스/터치 이벤트, 노드/엣지 드로잉, 속성 패널, 미니맵
 */

function _renderPalette(grouped) {
    var palette = DXStream.$('palette-list');
    if (!palette) return;

    var categories = Array.isArray(grouped)
        ? grouped.reduce(function (acc, el) {
            (acc[el.category] = acc[el.category] || []).push(el);
            return acc;
        }, {})
        : grouped;

    palette.innerHTML = Object.entries(categories).map(function (entry) {
        var cat = entry[0], items = entry[1];
        var color = _catColor(cat);
        var icon = _catIcon(cat);
        return '<div class="palette-group" style="--cat-color:' + color + '">' +
            '<div class="palette-group-title">' +
                '<span class="palette-cat-icon">' + icon + '</span>' +
                '<span>' + _catLabel(cat) + '</span>' +
                '<span class="palette-cat-count">' + items.length + '</span>' +
            '</div>' +
            items.map(function (el) {
                return '<div class="palette-item" draggable="true" data-element="' + el.name + '" data-category="' + cat + '"' +
                     ' title="' + T(el.description_en, el.description_ko) + '"' +
                     ' style="--cat-color:' + color + '">' +
                    '<span class="palette-item-bar"></span>' +
                    '<span class="palette-item-name">' + el.name + '</span>' +
                '</div>';
            }).join('') +
          '</div>';
    }).join('');
}

function _bindPaletteDrag() {
    var palette = DXStream.$('palette-list');
    var container = document.querySelector('.canvas-container');
    var canvas = DXStream.$('pipeline-canvas');
    if (!palette || !container || !canvas) return;

    // 중복 등록 방지
    if (container.dataset.pipeDragBound) return;
    container.dataset.pipeDragBound = '1';

    var dragEnterCount = 0;

    palette.addEventListener('dragstart', function (e) {
        var item = e.target.closest('.palette-item');
        if (!item) return;
        e.dataTransfer.setData('text/plain', item.dataset.element);
        e.dataTransfer.effectAllowed = 'copy';
        item.classList.add('dragging');
    });
    palette.addEventListener('dragend', function (e) {
        var item = e.target.closest('.palette-item');
        if (item) item.classList.remove('dragging');
        // safety: clear drag-over on any drag end (cancel or outside drop)
        dragEnterCount = 0;
        container.classList.remove('drag-over');
    });

    // drop on canvas — use enter/leave counter to handle child element events
    container.addEventListener('dragenter', function (e) {
        e.preventDefault();
        dragEnterCount++;
        container.classList.add('drag-over');
    });
    container.addEventListener('dragover', function (e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'copy';
    });
    container.addEventListener('dragleave', function (e) {
        dragEnterCount--;
        if (dragEnterCount <= 0) {
            dragEnterCount = 0;
            container.classList.remove('drag-over');
        }
    });
    container.addEventListener('drop', function (e) {
        e.preventDefault();
        dragEnterCount = 0;
        container.classList.remove('drag-over');
        var elName = e.dataTransfer.getData('text/plain');
        if (!elName) return;
        var rect = canvas.getBoundingClientRect();
        var st = DXStream._pipeState;
        var x = (e.clientX - rect.left - st.offsetX) / st.zoom;
        var y = (e.clientY - rect.top - st.offsetY) / st.zoom;
        _addNode(elName, x, y);
    });
}

function _addNode(elementName, x, y) {
    var st = DXStream._pipeState;
    var elDef = st.elementFlat.find(function (e) { return e.name === elementName; });
    if (!elDef) return;

    var props = {};
    if (elDef.properties && Array.isArray(elDef.properties)) {
        elDef.properties.forEach(function (p) {
            props[p.name] = p.default !== undefined ? p.default : '';
        });
    }

    var node = {
        id: 'n' + st._nextId++,
        type: elDef.name,
        name: elDef.name,
        category: elDef.category,
        x: Math.round(x - _NODE_W / 2),
        y: Math.round(y - _NODE_H / 2),
        properties: props,
    };
    st.nodes.push(node);
    _pushHistory();
    _updateElementCount();
    _refreshCanvas();
}

function _updateElementCount() {
    var el = DXStream.$('pipeline-element-count');
    if (!el) return;
    var n = DXStream._pipeState.nodes.length;
    var ko = el.querySelector('.ko');
    var en = el.querySelector('.en');
    if (ko) ko.textContent = '\uc5d8\ub9ac\uba3c\ud2b8: ' + n;
    if (en) en.textContent = 'Elements: ' + n;
}

function _initCanvas() {
    var canvas = DXStream.$('pipeline-canvas');
    if (!canvas) return;

    function resize() {
        var parent = canvas.parentElement;
        if (!parent) return;
        canvas.width = parent.clientWidth;
        canvas.height = parent.clientHeight;
        _scheduleCanvasRefresh();
    }
    var resizeTimer = null;
    function scheduleResize() {
        if (resizeTimer) clearTimeout(resizeTimer);
        resizeTimer = setTimeout(resize, 100);
    }
    resize();

    // 중복 등록 방지: 이미 바인딩되었으면 리사이즈만 수행
    if (canvas.dataset.pipeEvtBound) return;
    canvas.dataset.pipeEvtBound = '1';

    window.addEventListener('resize', scheduleResize);

    canvas.addEventListener('mousedown', _canvasMouseDown);
    canvas.addEventListener('mousemove', _canvasMouseMove);
    canvas.addEventListener('mouseup', _canvasMouseUp);
    canvas.addEventListener('dblclick', _canvasDblClick);
    canvas.addEventListener('wheel', _canvasWheel, { passive: false });
    canvas.addEventListener('contextmenu', function (e) { e.preventDefault(); });

    var existing = document.getElementById('pipeline-tooltip');
    if (!existing) {
        var tip = document.createElement('div');
        tip.id = 'pipeline-tooltip';
        tip.className = 'pipeline-tooltip';
        canvas.parentElement.style.position = 'relative';
        canvas.parentElement.appendChild(tip);
    }
}

function _screenToWorld(e, canvas) {
    var rect = canvas.getBoundingClientRect();
    var st = DXStream._pipeState;
    return {
        x: (e.clientX - rect.left - st.offsetX) / st.zoom,
        y: (e.clientY - rect.top - st.offsetY) / st.zoom,
    };
}

function _hitNode(wx, wy) {
    var st = DXStream._pipeState;
    for (var i = st.nodes.length - 1; i >= 0; i--) {
        var n = st.nodes[i];
        if (wx >= n.x && wx <= n.x + _NODE_W && wy >= n.y && wy <= n.y + _NODE_H) return n;
    }
    return null;
}

function _hitOutputPort(wx, wy) {
    var st = DXStream._pipeState;
    for (var i = st.nodes.length - 1; i >= 0; i--) {
        var n = st.nodes[i];
        var px = n.x + _NODE_W, py = n.y + _NODE_H / 2;
        if (Math.abs(wx - px) < _PORT_HIT && Math.abs(wy - py) < _PORT_HIT) return n;
    }
    return null;
}

function _hitInputPort(wx, wy) {
    var st = DXStream._pipeState;
    for (var i = st.nodes.length - 1; i >= 0; i--) {
        var n = st.nodes[i];
        var px = n.x, py = n.y + _NODE_H / 2;
        if (Math.abs(wx - px) < _PORT_HIT && Math.abs(wy - py) < _PORT_HIT) return n;
    }
    return null;
}

function _getPipelineNodeMap(st) {
    var nodeMap = {};
    st.nodes.forEach(function (n) { nodeMap[n.id] = n; });
    return nodeMap;
}

function _edgeBoundsContains(wx, wy, x1, y1, x2, y2, threshold) {
    var cpPad = Math.min(Math.abs(x2 - x1) * 0.5, 80);
    var pad = Math.max(threshold, cpPad);
    return wx >= Math.min(x1, x2) - pad
        && wx <= Math.max(x1, x2) + pad
        && wy >= Math.min(y1, y2) - threshold
        && wy <= Math.max(y1, y2) + threshold;
}

function _hitEdge(wx, wy) {
    var st = DXStream._pipeState;
    var nodeMap = _getPipelineNodeMap(st);
    var threshold = 8;
    for (var i = st.edges.length - 1; i >= 0; i--) {
        var ed = st.edges[i];
        var fn = nodeMap[ed.from];
        var tn = nodeMap[ed.to];
        if (!fn || !tn) continue;
        var x1 = fn.x + _NODE_W, y1 = fn.y + _NODE_H / 2;
        var x2 = tn.x, y2 = tn.y + _NODE_H / 2;
        if (!_edgeBoundsContains(wx, wy, x1, y1, x2, y2, threshold)) continue;
        if (_distToBezierSq(wx, wy, x1, y1, x2, y2) < threshold * threshold) return ed;
    }
    return null;
}

function _distToBezierSq(px, py, x1, y1, x2, y2) {
    var cpOff = Math.min(Math.abs(x2 - x1) * 0.5, 80);
    var minD2 = Infinity;
    for (var t = 0; t <= 1; t += 0.05) {
        var mt = 1 - t;
        var cx1 = x1 + cpOff, cy1 = y1, cx2 = x2 - cpOff, cy2 = y2;
        var bx = mt*mt*mt*x1 + 3*mt*mt*t*cx1 + 3*mt*t*t*cx2 + t*t*t*x2;
        var by = mt*mt*mt*y1 + 3*mt*mt*t*cy1 + 3*mt*t*t*cy2 + t*t*t*y2;
        var d2 = (px-bx)*(px-bx) + (py-by)*(py-by);
        if (d2 < minD2) minD2 = d2;
    }
    return minD2;
}

function _canvasMouseDown(e) {
    var canvas = e.target;
    var w = _screenToWorld(e, canvas);
    var st = DXStream._pipeState;

    if (e.button === 1 || e.button === 2) {
        st._pan = { startX: e.clientX, startY: e.clientY, origOX: st.offsetX, origOY: st.offsetY };
        canvas.style.cursor = 'grabbing';
        return;
    }

    var portNode = _hitOutputPort(w.x, w.y);
    if (portNode) {
        if (!_canStartEdge(portNode.id)) {
            DXStream.toast(T('Cannot start edge from this node'), 'error');
            return;
        }
        st._edge = { fromId: portNode.id, mx: w.x, my: w.y };
        st._connectable = _getConnectable(portNode.id);
        _highlightPalette(portNode.id);
        return;
    }

    var hit = _hitNode(w.x, w.y);
    if (hit) {
        st.selectedEdge = null;
        if (e.shiftKey) {
            // Shift+클릭: 멀티 선택 토글
            var idx = st.selectedNodes.indexOf(hit.id);
            if (idx >= 0) { st.selectedNodes.splice(idx, 1); }
            else { st.selectedNodes.push(hit.id); }
        } else if (!st.selectedNodes.includes(hit.id)) {
            st.selectedNodes = [hit.id];
        }
        st.selectedNode = st.selectedNodes[0] || null;
        DXStream._showPropertyPanel(hit);
        // 멀티 노드 드래그
        if (st.selectedNodes.length > 1 && st.selectedNodes.includes(hit.id)) {
            var origPositions = st.selectedNodes.map(function (nid) {
                var nd = st.nodes.find(function (n) { return n.id === nid; });
                return { id: nid, x: nd.x, y: nd.y };
            });
            st._drag = { multi: true, startX: w.x, startY: w.y, origPositions: origPositions };
        } else {
            st._drag = { nodeId: hit.id, startX: w.x, startY: w.y, origX: hit.x, origY: hit.y };
        }
        _refreshCanvas();
        return;
    }

    var hitEd = _hitEdge(w.x, w.y);
    if (hitEd) {
        st.selectedEdge = hitEd.id;
        st.selectedNode = null;
        st.selectedNodes = [];
        _hidePropertyPanel();
        _refreshCanvas();
        return;
    }

    st.selectedNode = null;
    st.selectedNodes = [];
    st.selectedEdge = null;
    _hidePropertyPanel();
    _refreshCanvas();
    st._pan = { startX: e.clientX, startY: e.clientY, origOX: st.offsetX, origOY: st.offsetY };
    canvas.style.cursor = 'grabbing';
}

function _canvasMouseMove(e) {
    var canvas = DXStream.$('pipeline-canvas');
    if (!canvas) return;
    var st = DXStream._pipeState;

    if (st._pan) {
        st.offsetX = st._pan.origOX + (e.clientX - st._pan.startX);
        st.offsetY = st._pan.origOY + (e.clientY - st._pan.startY);
        _scheduleCanvasRefresh();
        return;
    }

    if (st._drag) {
        var w = _screenToWorld(e, canvas);
        if (st._drag.multi) {
            // 멀티 노드 드래그
            var dx = w.x - st._drag.startX;
            var dy = w.y - st._drag.startY;
            st._drag.origPositions.forEach(function (op) {
                var nd = st.nodes.find(function (n) { return n.id === op.id; });
                if (nd) { nd.x = op.x + dx; nd.y = op.y + dy; }
            });
        } else {
            var node = st.nodes.find(function (n) { return n.id === st._drag.nodeId; });
            if (node) {
                node.x = st._drag.origX + (w.x - st._drag.startX);
                node.y = st._drag.origY + (w.y - st._drag.startY);
            }
        }
        _scheduleCanvasRefresh();
        return;
    }

    if (st._edge) {
        var w2 = _screenToWorld(e, canvas);
        st._edge.mx = w2.x;
        st._edge.my = w2.y;

        var tip = document.getElementById('pipeline-tooltip');
        if (tip && st._connectable) {
            var hovered = _hitNode(w2.x, w2.y);
            if (hovered) {
                var blocked = st._connectable.block.find(function (b) { return b.id === hovered.id; });
                var warned = st._connectable.warn.find(function (wr) { return wr.id === hovered.id; });
                if (blocked) {
                    tip.textContent = blocked.reason;
                    tip.style.left = (e.offsetX + 12) + 'px';
                    tip.style.top = (e.offsetY - 30) + 'px';
                    tip.classList.add('visible');
                } else if (warned) {
                    tip.textContent = warned.reason;
                    tip.style.left = (e.offsetX + 12) + 'px';
                    tip.style.top = (e.offsetY - 30) + 'px';
                    tip.classList.add('visible');
                } else {
                    tip.classList.remove('visible');
                }
            } else {
                tip.classList.remove('visible');
            }
        }

        _scheduleCanvasRefresh();
        return;
    }

    var w3 = _screenToWorld(e, canvas);

    var tip = document.getElementById('pipeline-tooltip');
    if (tip && !st._edge) {
        var hoveredEdge = null;
        var nodeMap = _getPipelineNodeMap(st);
        st.edges.forEach(function (ed) {
            if (ed.status !== 'warn') return;
            var fn = nodeMap[ed.from];
            var tn = nodeMap[ed.to];
            if (!fn || !tn) return;
            var x1 = fn.x + _NODE_W, y1 = fn.y + _NODE_H / 2;
            var x2 = tn.x, y2 = tn.y + _NODE_H / 2;
            var mx = (x1 + x2) / 2, my = (y1 + y2) / 2;
            var distSq = (w3.x - mx) * (w3.x - mx) + (w3.y - my) * (w3.y - my);
            if (distSq < 400) hoveredEdge = ed;
        });
        if (hoveredEdge && hoveredEdge.warnMsg) {
            tip.textContent = hoveredEdge.warnMsg;
            tip.style.left = (e.offsetX + 12) + 'px';
            tip.style.top = (e.offsetY - 30) + 'px';
            tip.classList.add('visible');
        } else {
            tip.classList.remove('visible');
        }
    }

    if (_hitOutputPort(w3.x, w3.y) || _hitInputPort(w3.x, w3.y)) {
        canvas.style.cursor = 'crosshair';
    } else if (_hitNode(w3.x, w3.y)) {
        canvas.style.cursor = 'grab';
    } else if (_hitEdge(w3.x, w3.y)) {
        canvas.style.cursor = 'pointer';
    } else {
        canvas.style.cursor = 'default';
    }
}

function _canvasMouseUp(e) {
    var canvas = DXStream.$('pipeline-canvas');
    if (!canvas) return;
    var st = DXStream._pipeState;

    if (st._pan) {
        st._pan = null;
        canvas.style.cursor = 'default';
        return;
    }

    if (st._drag) {
        if (st._drag.multi) {
            // 멀티 노드 드래그: 모든 선택 노드 그리드 스냅
            st._drag.origPositions.forEach(function (op) {
                var nd = st.nodes.find(function (n) { return n.id === op.id; });
                if (nd) {
                    nd.x = Math.round(nd.x / 20) * 20;
                    nd.y = Math.round(nd.y / 20) * 20;
                }
            });
            _pushHistory();
        } else {
            // 단일 노드 드래그: 그리드 스냅
            var node = st.nodes.find(function (n) { return n.id === st._drag.nodeId; });
            if (node) {
                node.x = Math.round(node.x / 20) * 20;
                node.y = Math.round(node.y / 20) * 20;
                _pushHistory();
            }
        }
        st._drag = null;
        _refreshCanvas();
        return;
    }

    if (st._edge) {
        var w = _screenToWorld(e, canvas);
        var target = _hitInputPort(w.x, w.y);
        if (target && target.id !== st._edge.fromId) {
            var dup = st.edges.some(function (ed) {
                return ed.from === st._edge.fromId && ed.to === target.id;
            });
            if (dup) {
                DXStream.toast(T('Duplicate connection'), 'error');
            } else if (_hasCycle(st._edge.fromId, target.id, st.edges)) {
                DXStream.toast(T('Cannot connect: would create a cycle'), 'error');
            } else {
                var v = _validateConnection(st._edge.fromId, target.id);
                if (v.result === 'block') {
                    DXStream.toast(T('Connection blocked: ') + v.reason, 'error');
                } else if (v.result === 'auto_convert') {
                    var _fromId = st._edge.fromId;
                    var _toId = target.id;
                    var _insert = v.insert;
                    var _reason = v.reason;
                    st._edge = null;
                    st._connectable = null;
                    _clearPaletteHighlight();
                    _refreshCanvas();
                    DXStream.confirmModal(
                        T('Insert Converter'),
                        T('Insert converter between nodes?')
                    ).then(function (ok) {
                        if (ok) {
                            _autoInsertConverter(_fromId, _toId, _insert);
                        } else {
                            _createEdge(_fromId, _toId, 'warn', _reason);
                            _pushHistory();
                        }
                        _refreshCanvas();
                    });
                    return;
                } else if (v.result === 'warn') {
                    _createEdge(st._edge.fromId, target.id, 'warn', v.reason);
                    DXStream.toast(T('Warning: ') + v.reason, 'warn');
                    _pushHistory();
                } else {
                    _createEdge(st._edge.fromId, target.id);
                    _pushHistory();
                }
            }
        }
        st._edge = null;
        st._connectable = null;
        _clearPaletteHighlight();
        var tip = document.getElementById('pipeline-tooltip');
        if (tip) tip.classList.remove('visible');
        _refreshCanvas();
        return;
    }
}

function _canvasDblClick(e) {
    var canvas = e.target;
    var w = _screenToWorld(e, canvas);
    var st = DXStream._pipeState;

    var node = _hitNode(w.x, w.y);
    if (node) {
        DXStream.confirmModal(
            T('Delete Node'),
            T('Delete node "' + node.name + '"?', '"' + node.name + '" 노드를 삭제하시겠습니까?')
        ).then(function (ok) {
            if (!ok) return;
            st.nodes = st.nodes.filter(function (n) { return n.id !== node.id; });
            st.edges = st.edges.filter(function (ed) { return ed.from !== node.id && ed.to !== node.id; });
            st.selectedNodes = st.selectedNodes.filter(function (id) { return id !== node.id; });
            if (st.selectedNode === node.id) {
                st.selectedNode = st.selectedNodes[0] || null;
            }
            if (!st.selectedNode) _hidePropertyPanel();
            _pushHistory();
            _updateElementCount();
            _refreshCanvas();
        });
        return;
    }

    var edgeHit = _hitEdge(w.x, w.y);
    if (edgeHit) {
        st.edges = st.edges.filter(function (ed) { return ed.id !== edgeHit.id; });
        st.selectedEdge = null;
        _pushHistory();
        _refreshCanvas();
        DXStream.toast(T('Edge deleted'), 'info');
        return;
    }
}

function _canvasWheel(e) {
    e.preventDefault();
    var st = DXStream._pipeState;
    var delta = e.deltaY > 0 ? -0.08 : 0.08;
    st.zoom = Math.max(0.3, Math.min(3.0, st.zoom + delta));
    _scheduleCanvasRefresh();
}

function _refreshCanvas() {
    var canvas = DXStream.$('pipeline-canvas');
    if (!canvas) return;
    var ctx = canvas.getContext('2d');
    var w = canvas.width, h = canvas.height;
    var st = DXStream._pipeState;
    var nodeMap = _getPipelineNodeMap(st);

    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = _themeColor('bg0') || '#0f0f1a';
    ctx.fillRect(0, 0, w, h);

    var step = 20 * st.zoom;
    ctx.strokeStyle = 'rgba(255,255,255,0.06)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (var x = ((st.offsetX % step) + step) % step; x < w; x += step) {
        ctx.moveTo(x, 0); ctx.lineTo(x, h);
    }
    for (var y = ((st.offsetY % step) + step) % step; y < h; y += step) {
        ctx.moveTo(0, y); ctx.lineTo(w, y);
    }
    ctx.stroke();

    if (st.nodes.length === 0) {
        ctx.fillStyle = 'rgba(255,255,255,0.2)';
        ctx.font = '14px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(T('Drag elements from the palette'), w / 2, h / 2);
        return;
    }

    ctx.save();
    ctx.translate(st.offsetX, st.offsetY);
    ctx.scale(st.zoom, st.zoom);

    st.edges.forEach(function (ed) {
        var fromNode = nodeMap[ed.from];
        var toNode = nodeMap[ed.to];
        if (!fromNode || !toNode) return;
        _drawEdge(ctx,
            fromNode.x + _NODE_W, fromNode.y + _NODE_H / 2,
            toNode.x, toNode.y + _NODE_H / 2,
            false, ed.id === st.selectedEdge,
            _catColor(fromNode.category), _catColor(toNode.category),
            ed.status === 'warn');
    });

    if (st._edge) {
        var fromNode = nodeMap[st._edge.fromId];
        if (fromNode) {
            _drawEdge(ctx,
                fromNode.x + _NODE_W, fromNode.y + _NODE_H / 2,
                st._edge.mx, st._edge.my, true);
        }
    }

    st.nodes.forEach(function (n) {
        var connStatus = undefined;
        if (st._edge && st._connectable) {
            if (n.id === st._edge.fromId) connStatus = undefined;
            else if (st._connectable.allow.indexOf(n.id) !== -1) connStatus = 'allow';
            else if (st._connectable.warn.some(function (w) { return w.id === n.id; })) connStatus = 'warn';
            else if (st._connectable.block.some(function (b) { return b.id === n.id; })) connStatus = 'block';
        }
        if (!connStatus && st._validateWarnNodes && st._validateWarnNodes.indexOf(n.id) !== -1) {
            connStatus = 'warn';
        }
        _drawNode(ctx, n, st.selectedNodes.includes(n.id), connStatus);
    });

    ctx.restore();

    _drawMinimap(st, w, h);
}

function _drawNode(ctx, node, selected, connStatus) {
    // outer save — connStatus에 따른 전체 노드 globalAlpha 제어
    ctx.save();
    if (connStatus === 'block') {
        ctx.globalAlpha = 0.3;
    }

    var x = node.x, y = node.y;
    var color = _catColor(node.category);
    var icon = _catIcon(node.category);

    var r = parseInt(color.slice(1,3),16), g = parseInt(color.slice(3,5),16), b = parseInt(color.slice(5,7),16);

    ctx.save();
    if (connStatus === 'allow') {
        ctx.shadowColor = _cv('--success');
        ctx.shadowBlur = 16;
    } else if (connStatus === 'warn') {
        ctx.shadowColor = _cv('--warning');
        ctx.shadowBlur = 12;
    } else if (connStatus === 'block') {
        ctx.shadowColor = 'transparent';
        ctx.shadowBlur = 0;
    } else {
        ctx.shadowColor = 'rgba(' + r + ',' + g + ',' + b + ',0.25)';
        ctx.shadowBlur = selected ? 16 : 10;
    }
    ctx.shadowOffsetX = 0;
    ctx.shadowOffsetY = connStatus ? 0 : 4;

    var bodyGrad = ctx.createLinearGradient(x, y, x + _NODE_W, y + _NODE_H);
    bodyGrad.addColorStop(0, 'rgba(' + r + ',' + g + ',' + b + ',' + (selected ? 0.20 : 0.10) + ')');
    bodyGrad.addColorStop(1, 'rgba(' + r + ',' + g + ',' + b + ',' + (selected ? 0.08 : 0.03) + ')');
    _roundRect(ctx, x, y, _NODE_W, _NODE_H, 10);
    ctx.fillStyle = bodyGrad;
    ctx.fill();
    ctx.restore();

    ctx.strokeStyle = selected ? '#fff' : 'rgba(' + r + ',' + g + ',' + b + ',0.6)';
    ctx.lineWidth = selected ? 2 : 1;
    _roundRect(ctx, x, y, _NODE_W, _NODE_H, 10);
    ctx.stroke();

    ctx.save();
    ctx.shadowColor = 'rgba(' + r + ',' + g + ',' + b + ',0.5)';
    ctx.shadowBlur = 6;
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(x + 10, y);
    ctx.lineTo(x + 5, y);
    ctx.arcTo(x, y, x, y + 10, 10);
    ctx.lineTo(x, y + _NODE_H - 10);
    ctx.arcTo(x, y + _NODE_H, x + 10, y + _NODE_H, 10);
    ctx.lineTo(x + 5, y + _NODE_H);
    ctx.lineTo(x + 5, y);
    ctx.closePath();
    ctx.fill();
    ctx.restore();

    ctx.fillStyle = color;
    ctx.font = '13px sans-serif';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';
    ctx.fillText(icon, x + 10, y + _NODE_H / 2);

    ctx.fillStyle = '#E2E8F0';
    ctx.font = 'bold 11px sans-serif';
    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';
    ctx.fillText(_truncate(node.name, 16), x + 26, y + _NODE_H / 2 - 8);

    ctx.fillStyle = 'rgba(' + r + ',' + g + ',' + b + ',0.7)';
    ctx.font = '9px sans-serif';
    ctx.fillText(_catLabel(node.category), x + 26, y + _NODE_H / 2 + 8);

    // input port (left) — block 상태에서는 숨김
    if (connStatus !== 'block') {
        ctx.beginPath();
        ctx.arc(x, y + _NODE_H / 2, _PORT_R + 1, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(' + r + ',' + g + ',' + b + ',0.15)';
        ctx.fill();
        ctx.beginPath();
        ctx.arc(x, y + _NODE_H / 2, _PORT_R, 0, Math.PI * 2);
        ctx.fillStyle = '#0e1525';
        ctx.fill();
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;
        ctx.stroke();
    }

    ctx.beginPath();
    ctx.arc(x + _NODE_W, y + _NODE_H / 2, _PORT_R + 1, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(' + r + ',' + g + ',' + b + ',0.15)';
    ctx.fill();
    ctx.beginPath();
    ctx.arc(x + _NODE_W, y + _NODE_H / 2, _PORT_R, 0, Math.PI * 2);
    ctx.fillStyle = '#0e1525';
    ctx.fill();
    ctx.strokeStyle = color;
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // 차단 표시 (block 상태)
    if (connStatus === 'block') {
        ctx.globalAlpha = 1;
        ctx.font = '18px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('🚫', x + _NODE_W / 2, y + _NODE_H / 2);
    }

    // 외부 restore — globalAlpha 복원
    ctx.restore();
}

function _drawEdge(ctx, x1, y1, x2, y2, dashed, selected, fromColor, toColor, warnEdge) {
    var cpOff = Math.min(Math.abs(x2 - x1) * 0.5, 80);
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.bezierCurveTo(x1 + cpOff, y1, x2 - cpOff, y2, x2, y2);

    if (selected) {
        ctx.strokeStyle = '#F85149';
    } else if (warnEdge) {
        ctx.strokeStyle = _cv('--warning');
    } else if (dashed) {
        ctx.strokeStyle = 'rgba(255,255,255,0.3)';
    } else if (fromColor && toColor) {
        var grad = ctx.createLinearGradient(x1, y1, x2, y2);
        grad.addColorStop(0, fromColor);
        grad.addColorStop(1, toColor);
        ctx.strokeStyle = grad;
    } else {
        ctx.strokeStyle = 'rgba(255,255,255,0.5)';
    }
    ctx.lineWidth = selected ? 3 : 2;
    if (dashed) ctx.setLineDash([6, 4]);
    else if (warnEdge) ctx.setLineDash([8, 4]);
    else ctx.setLineDash([]);
    ctx.stroke();
    ctx.setLineDash([]);

    if (!dashed) {
        var angle = Math.atan2(y2 - y1, x2 - x1);
        ctx.save();
        ctx.translate(x2, y2);
        ctx.rotate(angle);
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.lineTo(-8, -4);
        ctx.lineTo(-8, 4);
        ctx.closePath();
        ctx.fillStyle = warnEdge ? _cv('--warning') : (toColor || 'rgba(255,255,255,0.5)');
        ctx.fill();
        ctx.restore();
    }

    if (warnEdge) {
        var mx = (x1 + x2) / 2;
        var my = (y1 + y2) / 2;
        ctx.font = '14px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('⚠️', mx, my - 10);
    }
}
function _roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.arcTo(x + w, y, x + w, y + r, r);
    ctx.lineTo(x + w, y + h - r);
    ctx.arcTo(x + w, y + h, x + w - r, y + h, r);
    ctx.lineTo(x + r, y + h);
    ctx.arcTo(x, y + h, x, y + h - r, r);
    ctx.lineTo(x, y + r);
    ctx.arcTo(x, y, x + r, y, r);
    ctx.closePath();
}

function _truncate(s, max) {
    return s.length > max ? s.slice(0, max - 1) + '\u2026' : s;
}

function _hidePropertyPanel() {
    var panel = DXStream.$('property-panel');
    var content = DXStream.$('prop-content');
    if (content) content.innerHTML = '';
    var empty = panel ? panel.querySelector('.prop-empty') : null;
    if (empty) empty.style.display = '';
}

/* 속성 드롭다운 옵션 생성 — 모델/비디오/라이브러리/설정 */
function _getDropdownOptions(propName, nodeType) {
    var a = DXStream._pipeAssets;
    if (!a) return null;

    if (propName === 'model-path') {
        return (a.models || []).map(function (m) {
            return { value: a.models_dir + '/' + m, label: m };
        });
    }
    if (propName === 'library-file-path') {
        return (a.libraries || []).map(function (lib) {
            return { value: a.libs_dir + '/' + lib, label: lib.replace('libpostprocess_', '').replace('.so', '') };
        });
    }
    if (propName === 'function-name') {
        return [
            { value: 'PostProcess', label: 'PostProcess' },
        ];
    }
    if (propName === 'config-file-path') {
        var items = [];
        (a.configs || []).forEach(function (dir) {
            ['preprocess_config.json', 'inference_config.json', 'postprocess_config.json'].forEach(function (f) {
                items.push({ value: a.configs_dir + '/' + dir + '/' + f, label: dir + '/' + f });
            });
        });
        // 트래커 설정도 추가
        items.push({ value: a.configs_dir + '/tracker_config.json', label: 'tracker_config.json' });
        return items;
    }
    if (propName === 'uri' && (nodeType === 'urisourcebin' || nodeType === 'filesrc')) {
        return (a.videos || []).map(function (v) {
            return { value: 'file://' + a.videos_dir + '/' + v, label: v };
        });
    }
    return null;
}

DXStream._showPropertyPanel = function (node) {
    var panel = DXStream.$('property-panel');
    var content = DXStream.$('prop-content');
    if (!panel || !content) return;
    var empty = panel.querySelector('.prop-empty');
    if (empty) empty.style.display = 'none';

    var header = panel.querySelector('.prop-header');
    if (header) header.textContent = node.name || T('Properties');

    // 요소 정의에서 속성 메타데이터 가져오기
    var elDef = DXStream._pipeState.elementFlat.find(function (e) { return e.name === node.type; });
    var propMeta = {};
    if (elDef && elDef.properties && Array.isArray(elDef.properties)) {
        elDef.properties.forEach(function (p) { propMeta[p.name] = p; });
    }

    if (node.properties && typeof node.properties === 'object') {
        content.innerHTML = Object.entries(node.properties).map(function (entry) {
            var safeId = node.id.replace(/'/g, "\\'");
            var safeKey = entry[0].replace(/'/g, "\\'");
            var meta = propMeta[entry[0]] || {};
            var inputType = 'text';
            var placeholder = '';
            var extraAttr = '';
            if (meta.type === 'int' || meta.type === 'uint' || meta.type === 'float' || meta.type === 'double') {
                inputType = 'number';
                if (meta.min != null) extraAttr += ' min="' + meta.min + '"';
                if (meta.max != null) extraAttr += ' max="' + meta.max + '"';
                if (meta.type === 'float' || meta.type === 'double') extraAttr += ' step="0.01"';
            }
            if (meta.type === 'bool' || meta.type === 'boolean') {
                inputType = 'checkbox';
            }
            if (meta.description_en || meta.description_ko) {
                placeholder = T(meta.description_en || '', meta.description_ko || '');
            }
            var typeHint = meta.type ? '<span class=\"prop-type-hint\">' + meta.type + '</span>' : '';

            // 드롭다운 대상: model-path, library-file-path, function-name, config-file-path, uri
            var dropdown = _getDropdownOptions(entry[0], node.type);
            if (dropdown) {
                var curVal = entry[1] != null ? String(entry[1]) : '';
                var opts = '<option value="">' + (placeholder || T('Select...')) + '</option>';
                dropdown.forEach(function (opt) {
                    var sel = (opt.value === curVal) ? ' selected' : '';
                    opts += '<option value="' + opt.value.replace(/"/g, '&quot;') + '"' + sel + '>' + opt.label + '</option>';
                });
                // 목록에 없는 값이면 커스텀 항목 추가
                if (curVal && !dropdown.some(function (o) { return o.value === curVal; })) {
                    opts += '<option value="' + curVal.replace(/"/g, '&quot;') + '" selected>' + curVal.split('/').pop() + ' (custom)</option>';
                }
                return '<div class=\"prop-row\">' +
                    '<label class=\"prop-label\">' + entry[0] + typeHint + '</label>' +
                    '<select class=\"prop-select\" data-prop=\"' + entry[0] + '\"' +
                    ' onchange=\"DXStream._updateNodeProp(\'' + safeId + '\',\'' + safeKey + '\',this.value)\">' +
                    opts + '</select></div>';
            }

            if (inputType === 'checkbox') {
                var checked = (entry[1] === true || entry[1] === 'true' || entry[1] === '1') ? ' checked' : '';
                return '<div class=\"prop-row\">' +
                    '<label class=\"prop-label\">' + entry[0] + typeHint + '</label>' +
                    '<input class=\"prop-input\" type=\"checkbox\"' + checked + ' data-prop=\"' + entry[0] + '\"' +
                    ' onchange=\"DXStream._updateNodeProp(\'' + safeId + '\',\'' + safeKey + '\',this.checked)\">' +
                    '</div>';
            }
            return '<div class=\"prop-row\">' +
                '<label class=\"prop-label\">' + entry[0] + typeHint + '</label>' +
                '<input class=\"prop-input\" type=\"' + inputType + '\" value=\"' + (entry[1] != null ? String(entry[1]).replace(/"/g, '&quot;') : '') + '\" data-prop=\"' + entry[0] + '\"' +
                ' placeholder=\"' + placeholder.replace(/"/g, '&quot;') + '\"' + extraAttr +
                ' onchange=\"DXStream._updateNodeProp(\'' + safeId + '\',\'' + safeKey + '\',this.value)\">' +
                '</div>';
        }).join('');
    }
};

DXStream._updateNodeProp = function (nodeId, key, value) {
    var node = DXStream._pipeState.nodes.find(function (n) { return n.id === nodeId; });
    if (node && node.properties) {
        node.properties[key] = value;
        _pushHistory();
    }
};

function _ensureMinimapCanvasSize(mmCanvas, container) {
    var nextW = container.clientWidth || 160;
    var nextH = container.clientHeight || 120;
    if (mmCanvas.width !== nextW) mmCanvas.width = nextW;
    if (mmCanvas.height !== nextH) mmCanvas.height = nextH;
}

function _drawMinimap(st, canvasW, canvasH) {
    var container = DXStream.$('canvas-minimap');
    if (!container || st.nodes.length === 0) {
        if (container) container.style.display = 'none';
        return;
    }
    container.style.display = '';

    var mmCanvas = container.querySelector('canvas');
    if (!mmCanvas) {
        mmCanvas = document.createElement('canvas');
        container.appendChild(mmCanvas);
    }
    _ensureMinimapCanvasSize(mmCanvas, container);
    var mmCtx = mmCanvas.getContext('2d');
    var mw = mmCanvas.width, mh = mmCanvas.height;
    var nodeMap = _getPipelineNodeMap(st);

    var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    st.nodes.forEach(function (n) {
        if (n.x < minX) minX = n.x;
        if (n.y < minY) minY = n.y;
        if (n.x + _NODE_W > maxX) maxX = n.x + _NODE_W;
        if (n.y + _NODE_H > maxY) maxY = n.y + _NODE_H;
    });
    var pad = 40;
    var bw = maxX - minX + pad * 2;
    var bh = maxY - minY + pad * 2;
    var scale = Math.min(mw / bw, mh / bh);

    mmCtx.clearRect(0, 0, mw, mh);
    mmCtx.fillStyle = 'rgba(0,0,0,0.5)';
    mmCtx.fillRect(0, 0, mw, mh);

    mmCtx.strokeStyle = 'rgba(255,255,255,0.25)';
    mmCtx.lineWidth = 1;
    st.edges.forEach(function (ed) {
        var fn = nodeMap[ed.from];
        var tn = nodeMap[ed.to];
        if (!fn || !tn) return;
        mmCtx.beginPath();
        mmCtx.moveTo((fn.x + _NODE_W - minX + pad) * scale, (fn.y + _NODE_H / 2 - minY + pad) * scale);
        mmCtx.lineTo((tn.x - minX + pad) * scale, (tn.y + _NODE_H / 2 - minY + pad) * scale);
        mmCtx.stroke();
    });

    st.nodes.forEach(function (n) {
        var nx = (n.x - minX + pad) * scale;
        var ny = (n.y - minY + pad) * scale;
        var nw = _NODE_W * scale;
        var nh = _NODE_H * scale;
        mmCtx.fillStyle = _catColor(n.category);
        mmCtx.globalAlpha = 0.7;
        mmCtx.fillRect(nx, ny, nw, nh);
        mmCtx.globalAlpha = 1.0;
    });

    var vpLeft = (-st.offsetX / st.zoom - minX + pad) * scale;
    var vpTop = (-st.offsetY / st.zoom - minY + pad) * scale;
    var vpW = (canvasW / st.zoom) * scale;
    var vpH = (canvasH / st.zoom) * scale;
    mmCtx.strokeStyle = 'rgba(16, 185, 129, 0.8)';
    mmCtx.lineWidth = 1.5;
    mmCtx.strokeRect(vpLeft, vpTop, vpW, vpH);
}

function _showContextMenu(e) {
    e.preventDefault();
    _hideContextMenu();

    var canvas = DXStream.$('pipeline-canvas');
    if (!canvas) return;
    var st = DXStream._pipeState;
    var w = _screenToWorld(e, canvas);
    var hitNode = _hitNode(w.x, w.y);

    var menu = document.createElement('div');
    menu.className = 'ctx-menu';
    menu.id = 'pipe-ctx-menu';

    function _item(label, shortcut, fn) {
        var el = document.createElement('div');
        el.className = 'ctx-menu-item';
        el.textContent = label;
        if (shortcut) {
            var sp = document.createElement('span');
            sp.className = 'shortcut';
            sp.textContent = shortcut;
            el.appendChild(sp);
        }
        el.addEventListener('click', function () { _hideContextMenu(); fn(); });
        menu.appendChild(el);
    }
    function _sep() {
        var el = document.createElement('div');
        el.className = 'ctx-menu-sep';
        menu.appendChild(el);
    }

    if (hitNode) {
        if (!st.selectedNodes.includes(hitNode.id)) {
            st.selectedNodes = [hitNode.id];
            st.selectedNode = hitNode.id;
        }
        _item(T('Delete'), 'Del', function () { DXStream._deleteSelectedNode(); });
        _item(T('Copy'), 'Ctrl+C', function () { DXStream._copyNodes(); });
        _sep();
        _item(T('Properties'), '', function () { DXStream._showPropertyPanel(hitNode); });
    } else {
        _item(T('Paste'), 'Ctrl+V', function () { DXStream._pasteNodes(); });
        _item(T('Select All'), 'Ctrl+A', function () {
            st.selectedNodes = st.nodes.map(function (n) { return n.id; });
            st.selectedNode = st.selectedNodes[0] || null;
            _refreshCanvas();
        });
        _sep();
        _item(T('Undo'), 'Ctrl+Z', function () { DXStream._undo(); });
        _item(T('Redo'), 'Ctrl+Shift+Z', function () { DXStream._redo(); });
        _sep();
        _item(T('Fit View'), '', function () { DXStream.pipelineFitView(); });
        _item(T('Clear All'), '', function () { DXStream.pipelineClear(); });
    }

    menu.style.left = e.clientX + 'px';
    menu.style.top = e.clientY + 'px';
    document.body.appendChild(menu);

    var rect = menu.getBoundingClientRect();
    if (rect.right > window.innerWidth) menu.style.left = (e.clientX - rect.width) + 'px';
    if (rect.bottom > window.innerHeight) menu.style.top = (e.clientY - rect.height) + 'px';

    setTimeout(function () {
        document.addEventListener('click', _hideContextMenu, { once: true });
    }, 0);
}

function _hideContextMenu() {
    var old = document.getElementById('pipe-ctx-menu');
    if (old) old.remove();
}

function _touchToMouse(type, e) {
    if (e.touches.length > 1) return;
    var touch = e.touches[0] || e.changedTouches[0];
    var mouseEvent = new MouseEvent(type, {
        clientX: touch.clientX,
        clientY: touch.clientY,
        button: 0,
        bubbles: true,
    });
    e.target.dispatchEvent(mouseEvent);
    e.preventDefault();
}

function _initTouchEvents(canvas) {
    canvas.addEventListener('touchstart', function (e) { _touchToMouse('mousedown', e); }, { passive: false });
    canvas.addEventListener('touchmove', function (e) { _touchToMouse('mousemove', e); }, { passive: false });
    canvas.addEventListener('touchend', function (e) { _touchToMouse('mouseup', e); }, { passive: false });

    var _longPress = null;
    canvas.addEventListener('touchstart', function (e) {
        _longPress = setTimeout(function () {
            var touch = e.touches[0];
            var fakeEvent = { preventDefault: function () {}, clientX: touch.clientX, clientY: touch.clientY, target: canvas };
            _showContextMenu(fakeEvent);
        }, 600);
    });
    canvas.addEventListener('touchend', function () { clearTimeout(_longPress); });
    canvas.addEventListener('touchmove', function () { clearTimeout(_longPress); });
}
if (typeof registerStreamLangRefresher === 'function') {
  registerStreamLangRefresher(function() {
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
    if (typeof DXStream !== 'undefined' && DXStream.S && DXStream.S.currentPage && typeof DXStream.nav === 'function') {
      DXStream.nav(DXStream.S.currentPage);
    }
  });
}
