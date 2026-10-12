/* ── Home prompt router ───────────────────────────────────────
 *
 * The hero input answers before it thinks. An agent run takes minutes, and a
 * spinner on a front door is the wrong first impression — so this never starts
 * one. It reads the sentence with keyword matching over material the studio
 * already serves (the model catalogue, the twelve stream demos) and hands back
 * routes it can reach right now.
 *
 * Pure: `resolve(text, catalog, demos)` in, `{parsed, routes}` out. No DOM, no
 * fetch — the caller owns the data and the rendering. That is what lets it be
 * tested in a blank page with no server.
 *
 * When nothing matches, `routes` is empty. That is not a failure: it is the
 * agent's cue. Offering "build it from scratch" beside a preset we just found
 * reads as if the studio does not trust its own answer.
 */
(function () {
  'use strict';

  /* Task vocabulary. The words on the left are what people type; the ids on the
     right are what the demos and the catalogue already call these tasks.
     The studio speaks six languages, so the words do too — otherwise a Korean or
     Japanese sentence would match nothing and always go to the agent.
     The longest word that appears wins — "face detection" is a face, not the
     "detection" of the first row. */
  var TASKS = [
    { id: 'object_detection', words: ['object detection', 'detection', 'detect', 'cctv', 'people', 'person', 'yolo',
      '객체 탐지', '물체 탐지', '사람 탐지', '탐지', '검출', '사람', '物体検出', '検出', '人物', '目标检测', '物件偵測',
      '检测', '偵測', '行人', 'detección de objetos', 'detección', 'detectar', 'personas'] },
    { id: 'pose_estimation',  words: ['pose estimation', 'pose', 'keypoint', 'skeleton', 'push-up', 'pushup',
      '자세 추정', '포즈', '자세', '팔굽혀펴기', '姿勢推定', '姿勢', 'ポーズ', '腕立て', '姿态估计', '姿態估計', '姿态', '姿態',
      '俯卧撑', '伏地挺身', 'estimación de pose', 'postura', 'flexiones'] },
    { id: 'segmentation',     words: ['segmentation', 'segment', 'mask', 'masking',
      '세그멘테이션', '분할', 'セグメンテーション', '分割', 'segmentación', 'segmentar'] },
    { id: 'face_detection',   words: ['face detection', 'face',
      '얼굴 탐지', '얼굴', '顔検出', '顔', '人脸检测', '人臉偵測', '人脸', '人臉', 'detección de rostros', 'rostro'] },
    { id: 'classification',   words: ['classification', 'classify', 'label',
      '분류', '分類', '分类', 'clasificación', 'clasificar'] }
  ];

  /* Verbs that name a destination on their own. */
  var VERBS = [
    { id: 'compile', module: 'compiler', words: ['compile', 'quantize', 'dxnn', 'onnx', 'dxcom',
      '컴파일', '양자화', 'コンパイル', '量子化', '编译', '編譯', '量化', 'compilar', 'cuantizar'] },
    { id: 'benchmark', module: 'benchmark', words: ['benchmark', 'fps compare', 'q-lite vs', 'q-pro vs',
      '벤치마크', 'ベンチマーク', '基准测试', '基準測試', 'comparativa de rendimiento'] },
    { id: 'monitor', module: 'monitor', words: ['temperature', 'npu usage', 'utilisation', 'utilization', 'telemetry',
      '온도', '사용률', '温度', '使用率', '溫度', 'temperatura'] }
  ];

  var SOURCES = [
    { id: 'webcam', words: ['webcam', 'camera', 'usb cam', '웹캠', '카메라', 'カメラ', 'ウェブカメラ', '摄像头', '攝影機',
      '相机', '相機', 'cámara'] },
    { id: 'video',  words: ['video file', 'video', 'mp4', 'file', '영상', '동영상', '비디오', '動画', 'ビデオ', '视频', '影片',
      'vídeo'] },
    { id: 'rtsp',   words: ['rtsp', 'ip camera', 'cctv', 'ip 카메라', 'ip カメラ', '网络摄像机', '網路攝影機', 'cámara ip'] }
  ];

  function _norm(text) {
    return String(text || '').toLowerCase();
  }

  /* The entry whose longest word appears in the sentence (ties: the earlier row). */
  function _firstMatch(table, hay) {
    var best = null, bestLen = 0;
    for (var i = 0; i < table.length; i++) {
      var entry = table[i];
      for (var j = 0; j < entry.words.length; j++) {
        var w = entry.words[j];
        if (w.length > bestLen && hay.indexOf(w) !== -1) { best = entry; bestLen = w.length; }
      }
    }
    return best;
  }

  /* The Model Zoo catalogue calls the task "category"; older lists call it "task". */
  function _taskOf(entry) {
    return (entry && (entry.task || entry.category)) || null;
  }

  /* "segmentation" covers the zoo's semantic_ and instance_segmentation. */
  function _sameTask(have, want) {
    return !!have && (have === want || have.slice(-(want.length + 1)) === '_' + want);
  }

  /* "4-channel", "4 ch", "4ch", "2-ch" — all the ways people write a count. */
  function _channels(hay) {
    var m = hay.match(/(\d+)\s*[- ]?\s*(?:channel|ch\b|cameras?|streams?|채널|대|チャンネル|ch|路|通道|canal(?:es)?|cámaras)/);
    return m ? parseInt(m[1], 10) : null;
  }

  function _fps(hay) {
    var m = hay.match(/(\d+)\s*fps/);
    return m ? parseInt(m[1], 10) : null;
  }

  /* A model the user named outright beats anything inferred from a task word. */
  function _model(hay, catalog) {
    var best = null;
    for (var i = 0; i < (catalog || []).length; i++) {
      var entry = catalog[i];
      var names = [entry.name, entry.id];
      for (var j = 0; j < names.length; j++) {
        var name = _norm(names[j]);
        if (!name || name.length < 4) continue;
        if (hay.indexOf(name) !== -1 && (!best || name.length > best._len)) {
          best = { name: entry.name || entry.id, task: _taskOf(entry), _len: name.length };
        }
      }
    }
    return best;
  }

  function _demoFor(task, demos) {
    for (var i = 0; i < (demos || []).length; i++) {
      if (demos[i].category === task) return demos[i];
    }
    return null;
  }

  function _countModels(task, catalog) {
    var n = 0;
    for (var i = 0; i < (catalog || []).length; i++) {
      if (_sameTask(_taskOf(catalog[i]), task)) n++;
    }
    return n;
  }

  function resolve(text, catalog, demos) {
    var hay = _norm(text);
    var parsed = {
      task: null, channels: null, fps: null, source: null, model: null, verb: null
    };
    var routes = [];

    if (!hay.trim()) return { parsed: parsed, routes: routes };

    var task = _firstMatch(TASKS, hay);
    var verb = _firstMatch(VERBS, hay);
    var source = _firstMatch(SOURCES, hay);
    var model = _model(hay, catalog);

    parsed.channels = _channels(hay);
    parsed.fps = _fps(hay);
    if (source) parsed.source = source.id;
    if (verb) parsed.verb = verb.id;
    if (model) parsed.model = model.name;
    parsed.task = (task && task.id) || (model && model.task) || null;

    /* A named verb is the most specific thing in the sentence. */
    if (verb) {
      routes.push({
        kind: 'verb',
        module: verb.module,
        model: model ? model.name : null,
        title: verb.id,
        why: model ? model.name : null
      });
    }

    /* A task with a matching demo is something we can start right now. */
    if (parsed.task) {
      var demo = _demoFor(parsed.task, demos);
      if (demo) {
        routes.push({
          kind: 'run',
          module: 'stream',
          demo: demo.id,
          model: model ? model.name : null,
          title: demo.name_en || demo.category,
          task: parsed.task,
          channels: parsed.channels || null,
          why: parsed.channels ? parsed.channels + '-channel' : null
        });
      }

      /* Channels or a frame-rate target is a sizing question, and EdgeGuide is
         the only place that answers it from measured numbers. */
      if (parsed.channels || parsed.fps) {
        routes.push({
          kind: 'fit',
          module: 'planner',
          title: 'DX-M1',
          why: [
            parsed.channels ? parsed.channels + ' ch' : null,
            parsed.fps ? parsed.fps + ' FPS' : null
          ].filter(Boolean).join(' · ')
        });
      }

      var count = _countModels(parsed.task, catalog);
      if (count) {
        routes.push({
          kind: 'models',
          module: 'zoo',
          task: parsed.task,
          count: count,
          model: model ? model.name : null,
          title: parsed.task
        });
      }
    } else if (model) {
      /* A model named with no task still has one destination worth offering. */
      routes.push({
        kind: 'models', module: 'zoo', model: model.name, count: 1, title: model.name
      });
    }

    return { parsed: parsed, routes: routes };
  }

  window.DXHomeRouter = { resolve: resolve, TASKS: TASKS, VERBS: VERBS };
})();
