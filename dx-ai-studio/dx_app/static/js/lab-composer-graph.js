window.LabComposerGraph = (function () {
  'use strict';

  var CORE_NODE_IDS = ['input', 'preprocess', 'inference', 'postprocess', 'visualize'];
  var CORE_EDGES = [
    ['input', 'preprocess'],
    ['preprocess', 'inference'],
    ['inference', 'postprocess'],
    ['postprocess', 'visualize']
  ];
  var NODE_WIDTH = 176;
  var NODE_HEIGHT = 96;
  var PORT_RADIUS = 8;
  var GRID_SIZE = 20;
  var MIN_ZOOM = 0.3;
  var MAX_ZOOM = 3;

  function defaultLayout() {
    var x = [80, 310, 540, 770, 1000];
    return {
      version: 1,
      nodes: CORE_NODE_IDS.map(function (id, index) {
        return { id: id, x: x[index], y: 220 };
      }),
      edges: CORE_EDGES.map(function (edge) {
        return { id: edge[0] + '-' + edge[1], from: edge[0], to: edge[1] };
      }),
      viewport: { zoom: 1, offset_x: 0, offset_y: 0 }
    };
  }

  function clone(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function finite(value, minimum, maximum) {
    return typeof value === 'number' && isFinite(value) && value >= minimum && value <= maximum;
  }

  function legalEdge(source, target) {
    return CORE_EDGES.some(function (edge) {
      return edge[0] === source && edge[1] === target;
    });
  }

  function canonicalLayout(layout) {
    var fallback = defaultLayout();
    if (!layout || !Array.isArray(layout.nodes) || !Array.isArray(layout.edges) || !layout.viewport) {
      return fallback;
    }
    var byId = {};
    layout.nodes.forEach(function (node) {
      if (node && CORE_NODE_IDS.indexOf(node.id) !== -1 && finite(node.x, -5000, 5000) && finite(node.y, -5000, 5000)) {
        byId[node.id] = { id: node.id, x: node.x, y: node.y };
      }
    });
    if (CORE_NODE_IDS.some(function (id) { return !byId[id]; })) return fallback;
    var edges = layout.edges.filter(function (edge) {
      return edge && legalEdge(edge.from, edge.to) && edge.id === edge.from + '-' + edge.to;
    });
    var unique = {};
    edges = edges.filter(function (edge) {
      if (unique[edge.id]) return false;
      unique[edge.id] = true;
      return true;
    }).map(function (edge) {
      return { id: edge.id, from: edge.from, to: edge.to };
    });
    var viewport = layout.viewport;
    return {
      version: 1,
      nodes: CORE_NODE_IDS.map(function (id) { return byId[id]; }),
      edges: edges,
      viewport: {
        zoom: finite(viewport.zoom, MIN_ZOOM, MAX_ZOOM) ? viewport.zoom : 1,
        offset_x: finite(viewport.offset_x, -10000, 10000) ? viewport.offset_x : 0,
        offset_y: finite(viewport.offset_y, -10000, 10000) ? viewport.offset_y : 0
      }
    };
  }

  function ComposerGraphState(layout) {
    var normalized = canonicalLayout(layout);
    this.nodes = {};
    normalized.nodes.forEach(function (node) {
      this.nodes[node.id] = { id: node.id, x: node.x, y: node.y };
    }, this);
    this.edges = normalized.edges;
    this.selectedNodeId = 'input';
    this.selectedEdgeId = '';
    this.viewport = normalized.viewport;
    this.history = [];
    this.historyIndex = -1;
    this.drag = null;
    this.pan = null;
    this.connecting = null;
    this.workflow = null;
    this.pushHistory();
  }

  ComposerGraphState.prototype.snapshot = function () {
    return {
      nodes: CORE_NODE_IDS.map(function (id) {
        var node = this.nodes[id];
        return { id: id, x: node.x, y: node.y };
      }, this),
      edges: this.edges.map(function (edge) {
        return { id: edge.id, from: edge.from, to: edge.to };
      }),
      viewport: {
        zoom: this.viewport.zoom,
        offset_x: this.viewport.offset_x,
        offset_y: this.viewport.offset_y
      }
    };
  };

  ComposerGraphState.prototype.pushHistory = function () {
    var snapshot = this.snapshot();
    var current = this.history[this.historyIndex];
    if (current && JSON.stringify(current) === JSON.stringify(snapshot)) return;
    this.history = this.history.slice(0, this.historyIndex + 1);
    this.history.push(snapshot);
    if (this.history.length > 40) this.history.shift();
    this.historyIndex = this.history.length - 1;
  };

  ComposerGraphState.prototype.restore = function (snapshot) {
    var normalized = canonicalLayout(snapshot);
    normalized.nodes.forEach(function (node) {
      this.nodes[node.id] = { id: node.id, x: node.x, y: node.y };
    }, this);
    this.edges = normalized.edges;
    this.viewport = normalized.viewport;
    this.selectedEdgeId = '';
  };

  function validateLegalEdges(state) {
    var seen = {};
    var actual = {};
    state.edges.forEach(function (edge) {
      var key = edge.from + '>' + edge.to;
      if (seen[key] || !legalEdge(edge.from, edge.to) || edge.id !== edge.from + '-' + edge.to) {
        actual.invalid = true;
      }
      seen[key] = true;
      actual[key] = true;
    });
    var blockers = [];
    if (actual.invalid) blockers.push({ code: 'connection_not_allowed' });
    CORE_EDGES.forEach(function (edge) {
      if (!actual[edge[0] + '>' + edge[1]]) {
        blockers.push({ code: 'missing_connection', from: edge[0], to: edge[1] });
      }
    });
    return { blocked: blockers.length > 0, blockers: blockers };
  }

  function make(tag, className, value) {
    var element = document.createElement(tag);
    if (className) element.className = className;
    if (value !== undefined) element.textContent = value;
    return element;
  }

  function actionButton(label, handler) {
    var button = make('button', 'btn btn-ghost btn-sm', label);
    button.type = 'button';
    button.addEventListener('click', handler);
    return button;
  }

  function create(host, graphLayout, callbacks) {
    callbacks = callbacks || {};
    var state = new ComposerGraphState(graphLayout);
    var labels = callbacks.labels || {};
    var text = function (key, fallback) { return labels[key] || fallback; };
    var root = make('div', 'lab-composer-graph-editor');
    var toolbar = make('div', 'lab-composer-graph-toolbar');
    var canvas = document.createElement('canvas');
    var minimap = document.createElement('canvas');
    var status = make('span', 'lab-composer-graph-status');
    var ctx = canvas.getContext('2d');
    var miniContext = minimap.getContext('2d');
    var resizeObserver = null;
    var fallbackResizeListener = false;
    var destroyed = false;
    var canvasSize = { width: 1, height: 1, pixelRatio: 1 };
    var previewPoint = null;

    canvas.className = 'lab-composer-graph-surface';
    canvas.tabIndex = 0;
    canvas.setAttribute('role', 'application');
    canvas.setAttribute('aria-label', text('canvas', 'Pipeline canvas'));
    minimap.className = 'lab-composer-graph-minimap';
    minimap.width = 150;
    minimap.height = 92;
    minimap.setAttribute('aria-label', text('minimap', 'Pipeline minimap'));

    toolbar.appendChild(actionButton('↶ ' + text('undo', 'Undo'), function () { undo(); }));
    toolbar.appendChild(actionButton('↷ ' + text('redo', 'Redo'), function () { redo(); }));
    toolbar.appendChild(actionButton('− ' + text('zoomOut', 'Zoom out'), function () { zoomBy(0.85); }));
    toolbar.appendChild(actionButton('+ ' + text('zoomIn', 'Zoom in'), function () { zoomBy(1.15); }));
    toolbar.appendChild(actionButton('⊙ ' + text('fitView', 'Fit view'), function () { fitView(); }));
    toolbar.appendChild(actionButton('✓ ' + text('validate', 'Validate graph'), function () { emitValidation(); }));
    toolbar.appendChild(status);
    root.appendChild(toolbar);
    root.appendChild(canvas);
    root.appendChild(minimap);
    host.appendChild(root);

    function screenPoint(event) {
      var bounds = canvas.getBoundingClientRect();
      return { x: event.clientX - bounds.left, y: event.clientY - bounds.top };
    }

    function toWorld(point) {
      return {
        x: (point.x - state.viewport.offset_x) / state.viewport.zoom,
        y: (point.y - state.viewport.offset_y) / state.viewport.zoom
      };
    }

    function toScreen(point) {
      return {
        x: point.x * state.viewport.zoom + state.viewport.offset_x,
        y: point.y * state.viewport.zoom + state.viewport.offset_y
      };
    }

    function nodeAt(point) {
      var selected = null;
      CORE_NODE_IDS.forEach(function (id) {
        var node = state.nodes[id];
        if (point.x >= node.x && point.x <= node.x + NODE_WIDTH && point.y >= node.y && point.y <= node.y + NODE_HEIGHT) {
          selected = node;
        }
      });
      return selected;
    }

    function portAt(point) {
      var match = null;
      CORE_NODE_IDS.forEach(function (id) {
        var node = state.nodes[id];
        [
          { type: 'in', x: node.x, y: node.y + NODE_HEIGHT / 2 },
          { type: 'out', x: node.x + NODE_WIDTH, y: node.y + NODE_HEIGHT / 2 }
        ].forEach(function (port) {
          var dx = point.x - port.x;
          var dy = point.y - port.y;
          if (dx * dx + dy * dy <= (PORT_RADIUS + 5) * (PORT_RADIUS + 5)) {
            match = { id: id, type: port.type, x: port.x, y: port.y };
          }
        });
      });
      return match;
    }

    function edgeAt(point) {
      var selected = null;
      state.edges.forEach(function (edge) {
        var from = outputPort(edge.from);
        var to = inputPort(edge.to);
        var distance = distanceToSegment(point, from, to);
        if (distance <= 12 / state.viewport.zoom) selected = edge;
      });
      return selected;
    }

    function distanceToSegment(point, from, to) {
      var dx = to.x - from.x;
      var dy = to.y - from.y;
      var length = dx * dx + dy * dy;
      if (!length) return Math.sqrt(Math.pow(point.x - from.x, 2) + Math.pow(point.y - from.y, 2));
      var projection = ((point.x - from.x) * dx + (point.y - from.y) * dy) / length;
      projection = Math.max(0, Math.min(1, projection));
      var x = from.x + projection * dx;
      var y = from.y + projection * dy;
      return Math.sqrt(Math.pow(point.x - x, 2) + Math.pow(point.y - y, 2));
    }

    function inputPort(id) {
      var node = state.nodes[id];
      return { x: node.x, y: node.y + NODE_HEIGHT / 2 };
    }

    function outputPort(id) {
      var node = state.nodes[id];
      return { x: node.x + NODE_WIDTH, y: node.y + NODE_HEIGHT / 2 };
    }

    function nodeName(id) {
      return {
        input: text('input', 'Input'),
        preprocess: text('preprocess', 'Preprocess'),
        inference: text('inference', 'Inference'),
        postprocess: text('postprocess', 'Postprocess'),
        visualize: text('visualize', 'Visualize')
      }[id] || id;
    }

    function nodeDetail(id) {
      var workflow = state.workflow || {};
      if (id === 'input') return (workflow.input || {}).path || text('unavailable', 'Input not selected');
      if (id === 'inference') return (workflow.model || {}).name || text('unavailable', 'Model not selected');
      return text('builtIn', 'Built-in Factory component');
    }

    function resize() {
      if (destroyed) return;
      var rect = root.getBoundingClientRect();
      var width = Math.max(320, Math.floor(rect.width));
      var height = Math.max(360, Math.floor(rect.height - toolbar.getBoundingClientRect().height - 8));
      var pixelRatio = window.devicePixelRatio || 1;
      canvas.style.width = width + 'px';
      canvas.style.height = height + 'px';
      canvas.width = Math.floor(width * pixelRatio);
      canvas.height = Math.floor(height * pixelRatio);
      canvasSize = { width: width, height: height, pixelRatio: pixelRatio };
      render();
    }

    function beginFrame(context) {
      context.setTransform(canvasSize.pixelRatio, 0, 0, canvasSize.pixelRatio, 0, 0);
      context.clearRect(0, 0, canvasSize.width, canvasSize.height);
    }

    function drawGrid() {
      ctx.save();
      ctx.strokeStyle = 'rgba(148, 163, 184, 0.14)';
      ctx.lineWidth = 1;
      var spacing = GRID_SIZE * state.viewport.zoom;
      if (spacing >= 10) {
        var startX = state.viewport.offset_x % spacing;
        var startY = state.viewport.offset_y % spacing;
        for (var x = startX; x <= canvasSize.width; x += spacing) {
          ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvasSize.height); ctx.stroke();
        }
        for (var y = startY; y <= canvasSize.height; y += spacing) {
          ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvasSize.width, y); ctx.stroke();
        }
      }
      ctx.restore();
    }

    function drawBezier(from, to, color, width, dashed) {
      var source = toScreen(from);
      var target = toScreen(to);
      var curve = Math.max(40, Math.abs(target.x - source.x) * 0.45);
      ctx.save();
      ctx.strokeStyle = color;
      ctx.lineWidth = width;
      if (dashed) ctx.setLineDash([7, 5]);
      ctx.beginPath();
      ctx.moveTo(source.x, source.y);
      ctx.bezierCurveTo(source.x + curve, source.y, target.x - curve, target.y, target.x, target.y);
      ctx.stroke();
      ctx.restore();
      drawArrow(target, source, color);
    }

    function drawArrow(target, source, color) {
      var angle = Math.atan2(target.y - source.y, target.x - source.x);
      ctx.save();
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.moveTo(target.x, target.y);
      ctx.lineTo(target.x - 9 * Math.cos(angle - Math.PI / 6), target.y - 9 * Math.sin(angle - Math.PI / 6));
      ctx.lineTo(target.x - 9 * Math.cos(angle + Math.PI / 6), target.y - 9 * Math.sin(angle + Math.PI / 6));
      ctx.closePath();
      ctx.fill();
      ctx.restore();
    }

    function drawEdges() {
      var validation = validateLegalEdges(state);
      CORE_EDGES.forEach(function (pair) {
        var id = pair[0] + '-' + pair[1];
        var edge = state.edges.find(function (candidate) { return candidate.id === id; });
        var selected = state.selectedEdgeId === id;
        var color = edge ? (selected ? '#93c5fd' : '#5b8def') : '#e8796a';
        drawBezier(outputPort(pair[0]), inputPort(pair[1]), color, selected ? 4 : 2.5, !edge);
      });
      if (state.connecting && previewPoint) {
        drawBezier(outputPort(state.connecting.from), toWorld(previewPoint), '#fbbf24', 2, true);
      }
      if (validation.blocked) {
        root.classList.add('lab-composer-graph-blocked');
      } else {
        root.classList.remove('lab-composer-graph-blocked');
      }
    }

    function drawPorts(node) {
      var selected = state.selectedNodeId === node.id;
      [
        { port: inputPort(node.id), label: 'in' },
        { port: outputPort(node.id), label: 'out' }
      ].forEach(function (item) {
        var point = toScreen(item.port);
        ctx.save();
        ctx.fillStyle = selected ? '#a5f3fc' : '#6ea8fe';
        ctx.strokeStyle = '#0f172a';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(point.x, point.y, PORT_RADIUS, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
        ctx.restore();
      });
    }

    function drawNodes() {
      CORE_NODE_IDS.forEach(function (id) {
        var node = state.nodes[id];
        var point = toScreen(node);
        var width = NODE_WIDTH * state.viewport.zoom;
        var height = NODE_HEIGHT * state.viewport.zoom;
        var selected = state.selectedNodeId === id;
        ctx.save();
        ctx.fillStyle = selected ? '#1e3a5f' : '#172033';
        ctx.strokeStyle = selected ? '#7dd3fc' : '#4b638b';
        ctx.lineWidth = selected ? 3 : 1.5;
        roundRect(ctx, point.x, point.y, width, height, 10);
        ctx.fill(); ctx.stroke();
        ctx.fillStyle = '#e2e8f0';
        ctx.font = '600 ' + Math.max(12, 16 * state.viewport.zoom) + 'px sans-serif';
        ctx.fillText(nodeName(id), point.x + 16 * state.viewport.zoom, point.y + 30 * state.viewport.zoom);
        ctx.fillStyle = '#94a3b8';
        ctx.font = Math.max(10, 12 * state.viewport.zoom) + 'px sans-serif';
        var detail = nodeDetail(id);
        ctx.fillText(clipText(detail, Math.max(12, 20 * state.viewport.zoom)), point.x + 16 * state.viewport.zoom, point.y + 57 * state.viewport.zoom);
        ctx.restore();
        drawPorts(node);
      });
    }

    function clipText(value, maxLength) {
      value = String(value || '');
      return value.length > maxLength ? value.slice(0, Math.max(1, maxLength - 1)) + '…' : value;
    }

    function roundRect(context, x, y, width, height, radius) {
      var bounded = Math.min(radius, width / 2, height / 2);
      context.beginPath();
      context.moveTo(x + bounded, y);
      context.arcTo(x + width, y, x + width, y + height, bounded);
      context.arcTo(x + width, y + height, x, y + height, bounded);
      context.arcTo(x, y + height, x, y, bounded);
      context.arcTo(x, y, x + width, y, bounded);
      context.closePath();
    }

    function drawMinimap() {
      var width = minimap.width;
      var height = minimap.height;
      miniContext.clearRect(0, 0, width, height);
      miniContext.fillStyle = '#0b1220';
      miniContext.fillRect(0, 0, width, height);
      var nodes = CORE_NODE_IDS.map(function (id) { return state.nodes[id]; });
      var minX = Math.min.apply(null, nodes.map(function (node) { return node.x; })) - 50;
      var maxX = Math.max.apply(null, nodes.map(function (node) { return node.x + NODE_WIDTH; })) + 50;
      var minY = Math.min.apply(null, nodes.map(function (node) { return node.y; })) - 50;
      var maxY = Math.max.apply(null, nodes.map(function (node) { return node.y + NODE_HEIGHT; })) + 50;
      var scale = Math.min(width / Math.max(1, maxX - minX), height / Math.max(1, maxY - minY));
      CORE_EDGES.forEach(function (edge) {
        var from = outputPort(edge[0]);
        var to = inputPort(edge[1]);
        miniContext.strokeStyle = '#4f7fd8';
        miniContext.beginPath();
        miniContext.moveTo((from.x - minX) * scale, (from.y - minY) * scale);
        miniContext.lineTo((to.x - minX) * scale, (to.y - minY) * scale);
        miniContext.stroke();
      });
      nodes.forEach(function (node) {
        miniContext.fillStyle = node.id === state.selectedNodeId ? '#7dd3fc' : '#5475a5';
        miniContext.fillRect((node.x - minX) * scale, (node.y - minY) * scale, NODE_WIDTH * scale, NODE_HEIGHT * scale);
      });
      var viewportX = ((-state.viewport.offset_x / state.viewport.zoom) - minX) * scale;
      var viewportY = ((-state.viewport.offset_y / state.viewport.zoom) - minY) * scale;
      var viewportWidth = (canvasSize.width / state.viewport.zoom) * scale;
      var viewportHeight = (canvasSize.height / state.viewport.zoom) * scale;
      miniContext.strokeStyle = '#f8fafc';
      miniContext.lineWidth = 1;
      miniContext.strokeRect(viewportX, viewportY, viewportWidth, viewportHeight);
    }

    function render() {
      if (destroyed) return;
      beginFrame(ctx);
      ctx.fillStyle = '#0b1120';
      ctx.fillRect(0, 0, canvasSize.width, canvasSize.height);
      drawGrid();
      drawEdges();
      drawNodes();
      drawMinimap();
      updateStatus();
    }

    function updateStatus() {
      var validation = validateLegalEdges(state);
      status.className = 'lab-composer-graph-status ' + (validation.blocked ? 'blocked' : 'ready');
      status.textContent = validation.blocked ? text('graphBlocked', 'Graph blocked') : text('graphReady', 'Graph ready');
    }

    function emitValidation() {
      var validation = validateLegalEdges(state);
      updateStatus();
      if (callbacks.onValidationChange) callbacks.onValidationChange(validation);
      return validation;
    }

    function emitLayoutChange() {
      var validation = emitValidation();
      if (!validation.blocked && callbacks.onLayoutChange) callbacks.onLayoutChange(getLayout(), validation);
    }

    function selectNode(id) {
      state.selectedNodeId = id;
      state.selectedEdgeId = '';
      render();
      if (callbacks.onSelect) callbacks.onSelect(id);
    }

    function commitChange() {
      state.pushHistory();
      emitLayoutChange();
      render();
    }

    function onPointerDown(event) {
      if (destroyed || event.button !== 0) return;
      canvas.focus();
      var screen = screenPoint(event);
      var world = toWorld(screen);
      var port = portAt(world);
      if (port && port.type === 'out') {
        state.connecting = { from: port.id };
        previewPoint = screen;
      } else {
        var node = nodeAt(world);
        if (node) {
          state.drag = {
            id: node.id,
            offset_x: world.x - node.x,
            offset_y: world.y - node.y,
            moved: false
          };
          selectNode(node.id);
        } else {
          var edge = edgeAt(world);
          if (edge) {
            state.selectedEdgeId = edge.id;
            state.selectedNodeId = '';
            render();
          } else {
            state.pan = {
              x: screen.x,
              y: screen.y,
              offset_x: state.viewport.offset_x,
              offset_y: state.viewport.offset_y,
              moved: false
            };
          }
        }
      }
      canvas.setPointerCapture(event.pointerId);
      event.preventDefault();
    }

    function onPointerMove(event) {
      if (destroyed) return;
      var screen = screenPoint(event);
      var world = toWorld(screen);
      if (state.drag) {
        var node = state.nodes[state.drag.id];
        var nextX = Math.round((world.x - state.drag.offset_x) / GRID_SIZE) * GRID_SIZE;
        var nextY = Math.round((world.y - state.drag.offset_y) / GRID_SIZE) * GRID_SIZE;
        if (node.x !== nextX || node.y !== nextY) state.drag.moved = true;
        node.x = nextX;
        node.y = nextY;
        render();
      } else if (state.pan) {
        var nextOffsetX = state.pan.offset_x + screen.x - state.pan.x;
        var nextOffsetY = state.pan.offset_y + screen.y - state.pan.y;
        if (state.viewport.offset_x !== nextOffsetX || state.viewport.offset_y !== nextOffsetY) state.pan.moved = true;
        state.viewport.offset_x = nextOffsetX;
        state.viewport.offset_y = nextOffsetY;
        render();
      } else if (state.connecting) {
        previewPoint = screen;
        render();
      }
    }

    function onPointerUp(event) {
      if (destroyed) return;
      var screen = screenPoint(event);
      var changed = Boolean(
        (state.drag && state.drag.moved) ||
        (state.pan && state.pan.moved)
      );
      if (state.connecting) {
        var target = portAt(toWorld(screen));
        if (target && target.type === 'in' && legalEdge(state.connecting.from, target.id)) {
          var edgeId = state.connecting.from + '-' + target.id;
          if (!state.edges.some(function (edge) { return edge.id === edgeId; })) {
            state.edges.push({ id: edgeId, from: state.connecting.from, to: target.id });
            changed = true;
          }
        } else {
          root.classList.add('lab-composer-graph-invalid-link');
          window.setTimeout(function () { root.classList.remove('lab-composer-graph-invalid-link'); }, 420);
        }
      }
      state.drag = null;
      state.pan = null;
      state.connecting = null;
      previewPoint = null;
      if (canvas.hasPointerCapture(event.pointerId)) canvas.releasePointerCapture(event.pointerId);
      if (changed) commitChange();
      else render();
    }

    function onWheel(event) {
      event.preventDefault();
      var point = screenPoint(event);
      zoomAt(point, event.deltaY < 0 ? 1.1 : 0.9);
    }

    function zoomAt(point, factor) {
      var before = toWorld(point);
      state.viewport.zoom = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, state.viewport.zoom * factor));
      state.viewport.offset_x = point.x - before.x * state.viewport.zoom;
      state.viewport.offset_y = point.y - before.y * state.viewport.zoom;
      commitChange();
    }

    function zoomBy(factor) {
      zoomAt({ x: canvasSize.width / 2, y: canvasSize.height / 2 }, factor);
    }

    function fitView() {
      var nodes = CORE_NODE_IDS.map(function (id) { return state.nodes[id]; });
      var minX = Math.min.apply(null, nodes.map(function (node) { return node.x; }));
      var maxX = Math.max.apply(null, nodes.map(function (node) { return node.x + NODE_WIDTH; }));
      var minY = Math.min.apply(null, nodes.map(function (node) { return node.y; }));
      var maxY = Math.max.apply(null, nodes.map(function (node) { return node.y + NODE_HEIGHT; }));
      var padding = 70;
      var zoom = Math.min(
        (canvasSize.width - padding * 2) / Math.max(1, maxX - minX),
        (canvasSize.height - padding * 2) / Math.max(1, maxY - minY),
        MAX_ZOOM
      );
      state.viewport.zoom = Math.max(MIN_ZOOM, zoom);
      state.viewport.offset_x = (canvasSize.width - (maxX - minX) * state.viewport.zoom) / 2 - minX * state.viewport.zoom;
      state.viewport.offset_y = (canvasSize.height - (maxY - minY) * state.viewport.zoom) / 2 - minY * state.viewport.zoom;
      commitChange();
    }

    function undo() {
      if (state.historyIndex <= 0) return;
      state.historyIndex -= 1;
      state.restore(state.history[state.historyIndex]);
      emitLayoutChange();
      render();
    }

    function redo() {
      if (state.historyIndex >= state.history.length - 1) return;
      state.historyIndex += 1;
      state.restore(state.history[state.historyIndex]);
      emitLayoutChange();
      render();
    }

    function onKeyDown(event) {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'z') {
        event.preventDefault();
        if (event.shiftKey) redo(); else undo();
        return;
      }
      if ((event.key === 'Delete' || event.key === 'Backspace') && state.selectedEdgeId) {
        state.edges = state.edges.filter(function (edge) { return edge.id !== state.selectedEdgeId; });
        state.selectedEdgeId = '';
        commitChange();
      }
    }

    function onDragOver(event) {
      var typeList = event.dataTransfer ? event.dataTransfer.types : [];
      if (!typeList || !typeList.length) return;
      event.preventDefault();
      canvas.classList.add('drop-active');
    }

    function onDragLeave() {
      canvas.classList.remove('drop-active');
    }

    function onDrop(event) {
      event.preventDefault();
      canvas.classList.remove('drop-active');
      if (!event.dataTransfer || !callbacks.onDrop) return;
      var node = nodeAt(toWorld(screenPoint(event)));
      if (!node) return;
      var types = event.dataTransfer.types || [];
      var mime = '';
      for (var index = 0; index < types.length; index += 1) {
        if (types[index] === 'application/x-dx-app-composer-model' || types[index] === 'application/x-dx-app-composer-asset' || types[index] === 'application/x-dx-app-composer-plugin') {
          mime = types[index];
          break;
        }
      }
      if (!mime) return;
      var allowed = (
        (mime === 'application/x-dx-app-composer-model' && node.id === 'inference') ||
        (mime === 'application/x-dx-app-composer-asset' && node.id === 'input') ||
        (mime === 'application/x-dx-app-composer-plugin' && (node.id === 'preprocess' || node.id === 'postprocess'))
      );
      if (allowed) callbacks.onDrop({ targetId: node.id, mime: mime, value: event.dataTransfer.getData(mime) });
      else {
        root.classList.add('lab-composer-graph-invalid-link');
        window.setTimeout(function () { root.classList.remove('lab-composer-graph-invalid-link'); }, 420);
      }
    }

    function getLayout() {
      return {
        version: 1,
        nodes: CORE_NODE_IDS.map(function (id) {
          var node = state.nodes[id];
          return { id: id, x: node.x, y: node.y };
        }),
        edges: CORE_EDGES.map(function (pair) {
          var id = pair[0] + '-' + pair[1];
          return state.edges.find(function (edge) { return edge.id === id; });
        }).filter(Boolean).map(function (edge) {
          return { id: edge.id, from: edge.from, to: edge.to };
        }),
        viewport: {
          zoom: state.viewport.zoom,
          offset_x: state.viewport.offset_x,
          offset_y: state.viewport.offset_y
        }
      };
    }

    function setWorkflow(workflow) {
      state.workflow = workflow || null;
      render();
    }

    function destroy() {
      if (destroyed) return;
      destroyed = true;
      canvas.removeEventListener('pointerdown', onPointerDown);
      canvas.removeEventListener('pointermove', onPointerMove);
      canvas.removeEventListener('pointerup', onPointerUp);
      canvas.removeEventListener('wheel', onWheel);
      canvas.removeEventListener('keydown', onKeyDown);
      canvas.removeEventListener('dragover', onDragOver);
      canvas.removeEventListener('dragleave', onDragLeave);
      canvas.removeEventListener('drop', onDrop);
      if (resizeObserver) resizeObserver.disconnect();
      if (fallbackResizeListener) window.removeEventListener('resize', resize);
      root.remove();
    }

    canvas.addEventListener('pointerdown', onPointerDown);
    canvas.addEventListener('pointermove', onPointerMove);
    canvas.addEventListener('pointerup', onPointerUp);
    canvas.addEventListener('wheel', onWheel, { passive: false });
    canvas.addEventListener('keydown', onKeyDown);
    canvas.addEventListener('dragover', onDragOver);
    canvas.addEventListener('dragleave', onDragLeave);
    canvas.addEventListener('drop', onDrop);
    if (typeof ResizeObserver === 'function') {
      resizeObserver = new ResizeObserver(resize);
      resizeObserver.observe(root);
    } else {
      window.addEventListener('resize', resize);
      fallbackResizeListener = true;
    }
    resize();
    emitValidation();

    return {
      getLayout: getLayout,
      setWorkflow: setWorkflow,
      validate: emitValidation,
      destroy: destroy,
      fitView: fitView,
      undo: undo,
      redo: redo
    };
  }

  return {
    create: create,
    ComposerGraphState: ComposerGraphState,
    validateLegalEdges: validateLegalEdges
  };
})();
