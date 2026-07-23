
function renderModelsPage(){
  var cats=[...new Set(S.models.map(function(m){return m.category}))].sort();
  var html='<button class="chip active" data-cat="" onclick="chipFilter(this)">'+T('All')+'</button>';
  cats.forEach(function(c){html+='<button class="chip" data-cat="'+c+'" onclick="chipFilter(this)">'+c.replace(/_/g,' ')+'</button>'});
  $('cat-chips').innerHTML=html;
  filterModels();
}

function chipFilter(el){
  document.querySelectorAll('#cat-chips .chip').forEach(c=>c.classList.remove('active'));
  el.classList.add('active');
  filterModels();
}

function filterModels(){
  const search=($('m-search').value||'').toLowerCase();
  const chip=document.querySelector('#cat-chips .chip.active');
  const cat=chip?chip.dataset.cat:'';
  let list=S.models.filter(m=>{
    if(m.name.startsWith('_'))return false;
    if(search&&!m.name.toLowerCase().includes(search)&&!m.category.includes(search))return false;
    if(cat&&m.category!==cat)return false;
    return true;
  });
  const tb=$('m-table').querySelector('tbody');
  tb.innerHTML=list.map(function(m){
    var meta=[];
    if(m.npu_core)meta.push('<span class="badge b-blue">'+m.npu_core+'</span>');
    if(m.dataset)meta.push('<span class="badge b-warn">'+m.dataset+'</span>');
    if(m.input_resolution)meta.push('<span class="badge b-cat">'+m.input_resolution+'</span>');
    var modes=[];
    if(m.cpp_sync||m.py_sync)modes.push('<span class="badge b-ok">'+T('Sync')+'</span>');
    if(m.cpp_async||m.py_async)modes.push('<span class="badge b-blue">'+T('Async')+'</span>');
    var fileInfo=m.model_file?(m.model_exists?'\u2705':'\u274c')+'<span class="txt-dim"> '+m.model_file.split('/').pop()+'</span>':'\u2014';
    return '<tr>'
      +'<td>'+esc(m.name)+'</td>'
      +'<td><span class="badge b-cat">'+m.category.replace(/_/g,' ')+'</span></td>'
      +'<td>'+(m.cpp?'<span class="badge b-ok">\u2713</span>':'<span class="badge b-no">\u2014</span>')+'</td>'
      +'<td>'+(m.python?'<span class="badge b-ok">\u2713</span>':'<span class="badge b-no">\u2014</span>')+'</td>'
      +'<td>'+modes.join(' ')+'</td>'
      +'<td>'+(meta.join(' ')||'\u2014')+'</td>'
      +'<td style="font-size:11px;">'+fileInfo+'</td>'
      +'<td class="m-actions"><button class="m-action-btn" onclick="event.stopPropagation();showDetail(\''+esc(m.name)+'\')" title="Details">🔍 Detail</button>'
      +(_onnxGraphArg(m.model_file)&&m.model_exists?'<button class="m-action-btn" onclick="event.stopPropagation();openModelGraph(\''+esc(m.model_file)+'\')" title="View Graph">📊 Graph</button>':'')
      +'<button class="m-action-btn m-action-run" onclick="event.stopPropagation();quickRun(\''+esc(m.name)+'\',\''+esc(m.category)+'\',\''+esc(m.model_file||'')+'\')">▶ Run</button></td>'
      +'</tr>';
  }).join('');
  $('m-count').textContent=list.length+' / '+S.models.length+T(' models');
}

// ── Model graph (DX-TRON removed this release → dx-compiler's graph viewer) ──
// dx-compiler parses ONNX only; .dxnn graphs are not supported, so the Graph button is
// shown only when the model has an ONNX path. (dx_app inference models are .dxnn, so it
// stays hidden for them until they carry an ONNX or dx-compiler gains .dxnn support.)
function _onnxGraphArg(modelFile){
  if(!modelFile) return '';
  var mm=String(modelFile).match(/(\S+\.onnx)\b/i);
  return mm?mm[1]:'';
}
function openModelGraph(modelFile){
  var onnx=_onnxGraphArg(modelFile);
  if(!onnx){toast(T('Graph view is available for ONNX models only'),'warn');return;}
  // Deep-link into the dx-compiler graph viewer. Absolute path from the launcher origin;
  // the launcher proxies /compiler/ to dx-compiler, whose viewer reads ?viewer_path and
  // renders the graph. (Path must be absolute and under an allowed root.)
  window.open('/compiler/?viewer_path='+encodeURIComponent(onnx),'_blank','noopener');
}

async function showDetail(name){
  var info=await api('/api/model_info?name='+encodeURIComponent(name));
  $('md-title').textContent='🔍 '+name;
  var cfg=info.config||{};
  var PP_DESC={
    yolov5:T('YOLOv5-based object detection. Anchor-based with NMS post-processing.'),
    yolov7:T('YOLOv7-based object detection. E-ELAN architecture with NMS post-processing.'),
    yolov8:T('YOLOv8-based object detection. Anchor-free with NMS post-processing.'),
    yolov9:T('YOLOv9-based object detection. PGI/GELAN architecture with NMS post-processing.'),
    yolov10:T('YOLOv10-based object detection. NMS-free design.'),
    yolov11:T('YOLOv11-based object detection. C3k2 blocks with NMS post-processing.'),
    yolov12:T('YOLOv12-based object detection. Attention-based with NMS post-processing.'),
    yolov26:T('YOLOv26-based object detection. Latest YOLO architecture with NMS post-processing.'),
    yolox:T('YOLOX anchor-free object detection. Decoupled head with NMS post-processing.'),
    ssd:T('Single Shot Detector. Multi-scale feature map based detection.'),
    nanodet:T('NanoDet lightweight object detector. Uses GFL head.'),
    damoyolo:T('DAMO-YOLO high-efficiency object detection. AlignedOTA label assignment.'),
    centernet:T('CenterNet center-point based detection. Heatmap + offset prediction.'),
    efficientdet:T('EfficientDet object detection with BiFPN.'),
    efficientnet:T('EfficientNet image classification. Outputs Top-K probabilities.'),
    bisenetv1:T('BiSeNetV1 real-time semantic segmentation. Spatial + Context path.'),
    bisenetv2:T('BiSeNetV2 real-time semantic segmentation. Detail + Semantic branch.'),
    deeplabv3:T('DeepLabV3 semantic segmentation. Atrous convolution, ASPP.'),
    segformer:T('SegFormer Transformer-based semantic segmentation. Mix-FFN.'),
    yolov5seg:T('YOLOv5-Seg instance segmentation. Detection + Proto mask.'),
    yolov8seg:T('YOLOv8-Seg instance segmentation. Anchor-free + Mask head.'),
    yolact:T('YOLACT real-time instance segmentation. Prototype mask + linear combination.'),
    yolov5pose:T('YOLOv5-Pose estimation. Keypoint regression.'),
    yolov8pose:T('YOLOv8-Pose estimation. Anchor-free keypoint head.'),
    centerpose:T('CenterPose center-point based pose estimation. Heatmap + keypoint offset.'),
    scrfd:T('SCRFD high-efficiency face detection. Multi-task learning.'),
    retinaface:T('RetinaFace face detection. FPN + multi-task learning (landmark).'),
    ulfg:T('Ultra-Light-Fast face detection. Lightweight mobile network.'),
    yolov5face:T('YOLOv5-Face face detection with simultaneous landmark prediction.'),
    yolov7face:T('YOLOv7-Face face detection with simultaneous landmark prediction.'),
    obb:T('Rotated bounding box (OBB) detection. Oriented region prediction.'),
    fastdepth:T('FastDepth monocular depth estimation. Depthwise separable convolution.'),
    dncnn:T('DnCNN image denoising. Residual learning based.'),
    espcn:T('ESPCN super-resolution. Sub-pixel convolution layer.'),
    zero_dce:T('Zero-DCE low-light image enhancement. Zero-reference learning.'),
    arcface:T('ArcFace face recognition embedding. Additive angular margin.'),
    clip_image:T('CLIP image encoder. Vision-Language contrastive learning.'),
    clip_text:T('CLIP text encoder. Vision-Language contrastive learning.'),
    yolov5_ppu:T('YOLOv5 PPU pipeline. Integrated pre/post-processing.'),
    yolov7_ppu:T('YOLOv7 PPU pipeline. Integrated pre/post-processing.')
  };
  var VIS_DESC={
    object_detection:T('Draws bounding boxes with class labels and confidence scores.'),
    face_detection:T('Draws face bounding boxes and landmark points.'),
    pose_estimation:T('Draws skeleton (joint connections) and keypoints.'),
    obb_detection:T('Draws oriented (rotated) bounding boxes.'),
    classification:T('Overlays Top-K class predictions as text on the image.'),
    instance_segmentation:T('Draws bounding boxes and per-instance color masks.'),
    semantic_segmentation:T('Alpha-blends per-pixel class labels using the Cityscapes colormap.'),
    depth_estimation:T('Converts the depth map to JET colormap and alpha-blends it with the original.'),
    image_denoising:T('Outputs the denoised result image directly.'),
    super_resolution:T('Outputs the super-resolved result image.'),
    image_enhancement:T('Outputs the enhanced image directly.'),
    embedding:T('Displays embedding vector info (dimension, value preview, L2 norm) as text.'),
    ppu:T('Displays PPU pipeline results.'),
    face_alignment:T('Draws face alignment landmark points.'),
    hand_landmark:T('Draws 21 hand landmark points and connections.'),
    hand_detection:T('Draws bounding boxes around detected hands.'),
    keypoint_detection:T('Draws detected keypoints (interest points) on the image.'),
    object_pose_estimation:T('Draws the projected 3D bounding box and 6-DoF pose of the object.'),
    panoptic_driving_perception:T('Overlays drivable area, lane lines, and vehicle detections on the driving scene.'),
    '3d_object_detection':T('Renders 3D bounding boxes on the LiDAR bird\'s-eye-view.')
  };
  var h='';
  h+='<div class="detail-info-card"><h3>'+T('📋 Basic Info')+'</h3><table class="detail-tbl">';
  h+='<tr><td>'+T('Category')+'</td><td><span class="badge b-cat">'+(info.category||'').replace(/_/g,' ')+'</span></td></tr>';
  h+='<tr><td>'+T('Model File')+'</td><td>'+(info.model_exists?'✅':'❌')+' <span class="txt-sm" style="color:var(--text-1)">'+(info.model_file||'N/A')+'</span>'
    +(_onnxGraphArg(info.model_file)&&info.model_exists?' <button class="btn btn-ghost btn-sm" style="margin-left:8px;height:22px;font-size:11px" onclick="closeModal(\'modal-detail\');openModelGraph(\''+esc(info.model_file)+'\')">📊 View Graph</button>':'')
    +'</td></tr>';
  if(cfg.npu_core||cfg.NPU_CORE)h+='<tr><td>'+T('NPU Core')+'</td><td><span class="badge b-blue">'+(cfg.npu_core||cfg.NPU_CORE)+'</span></td></tr>';
  if(cfg.dataset||cfg.DATASET)h+='<tr><td>'+T('Dataset')+'</td><td><span class="badge b-warn">'+(cfg.dataset||cfg.DATASET)+'</span></td></tr>';
  if(cfg.input_size||cfg.INPUT_SIZE)h+='<tr><td>'+T('Input Size')+'</td><td>'+(cfg.input_size||cfg.INPUT_SIZE)+'</td></tr>';
  if(cfg.num_classes||cfg.NUM_CLASSES)h+='<tr><td>'+T('Classes')+'</td><td>'+(cfg.num_classes||cfg.NUM_CLASSES)+'</td></tr>';
  if(cfg.top_k)h+='<tr><td>Top-K</td><td>'+cfg.top_k+'</td></tr>';
  if(cfg.score_threshold!=null)h+='<tr><td>'+T('Score Thresh')+'</td><td>'+cfg.score_threshold+'</td></tr>';
  if(cfg.nms_threshold!=null)h+='<tr><td>'+T('NMS Thresh')+'</td><td>'+cfg.nms_threshold+'</td></tr>';
  if(cfg.obj_threshold!=null)h+='<tr><td>'+T('Obj Thresh')+'</td><td>'+cfg.obj_threshold+'</td></tr>';
  h+='</table></div>';
  var cat=info.category||'';
  if(VIS_DESC[cat]){
    h+='<div class="detail-info-card"><h3>'+T('👁️ Visualization')+'</h3>';
    h+='<p style="font-size:12px;line-height:1.5;color:var(--text-1);margin:0">'+VIS_DESC[cat]+'</p></div>';
  }
  var pps=info.postprocessors||{};
  if(Object.keys(pps).length){
    h+='<div class="detail-info-card"><h3>'+T('⚙️ Postprocessors')+'</h3>';
    h+='<div class="grid2" style="gap:10px">';
    Object.keys(pps).forEach(function(lang){
      var pp=pps[lang];
      var ppName=(pp.name||'').replace(/_postprocessor$/,'');
      var desc=PP_DESC[ppName]||T('Post-processor: ')+ppName;
      h+='<div class="pp-card">';
      h+='<div class="pp-header"><span class="badge '+(lang==='cpp'?'b-blue':'b-ok')+'">'+(lang==='cpp'?'C++':'Python')+'</span>';
      h+='<strong style="font-size:12px;color:var(--text-1)">'+ppName+'</strong></div>';
      h+='<p class="pp-desc">'+desc+'</p>';
      if(pp.file){h+='<button class="btn btn-sm btn-ghost" onclick="viewCode(\''+pp.file+'\')" style="font-size:11px">📄 View Source</button>'}
      h+='</div>';
    });
    h+='</div></div>';
  }
  if(cfg.preprocess||cfg.PREPROCESS||cfg.mean||cfg.std||cfg.resize||cfg.pad||cfg.normalize!=null){
    h+='<div class="detail-info-card"><h3>'+T('🔧 Preprocessing')+'</h3><table class="detail-tbl">';
    if(cfg.mean)h+='<tr><td>Mean</td><td style="font-family:var(--mono);font-size:11px">'+JSON.stringify(cfg.mean)+'</td></tr>';
    if(cfg.std)h+='<tr><td>Std</td><td style="font-family:var(--mono);font-size:11px">'+JSON.stringify(cfg.std)+'</td></tr>';
    if(cfg.preprocess||cfg.PREPROCESS)h+='<tr><td>Pipeline</td><td style="font-family:var(--mono);font-size:11px">'+esc(JSON.stringify(cfg.preprocess||cfg.PREPROCESS))+'</td></tr>';
    if(cfg.resize)h+='<tr><td>Resize</td><td>'+JSON.stringify(cfg.resize)+'</td></tr>';
    if(cfg.pad)h+='<tr><td>Padding</td><td>'+JSON.stringify(cfg.pad)+'</td></tr>';
    if(cfg.normalize!=null)h+='<tr><td>Normalize</td><td>'+cfg.normalize+'</td></tr>';
    h+='</table></div>';
  }
  if(cfg&&Object.keys(cfg).length){
    h+='<details class="detail-info-card" style="cursor:pointer"><summary style="font-size:13px;font-weight:600;color:var(--accent)">'+T('📄 Full Config (config.json)')+'</summary>';
    h+='<div class="code mt8" style="max-height:200px;font-size:11px">'+esc(JSON.stringify(cfg,null,2))+'</div></details>';
  }
  var fls=info.files||{};
  Object.keys(fls).forEach(function(lang){
    var files=fls[lang];
    h+='<details class="detail-info-card"><summary style="font-size:13px;font-weight:600;color:var(--accent)">'+(lang==='cpp'?'C++':'Python')+' Files ('+files.length+')</summary>';
    h+='<ul class="flist mt8">';
    files.forEach(function(f){
      if(f.endsWith('.hpp')||f.endsWith('.py')||f.endsWith('.cpp')){
        h+='<li><span class="flink" onclick="viewCode(\''+f+'\')">'+f+'</span></li>';
      }else{
        h+='<li><span class="txt-dim">'+f+'</span></li>';
      }
    });
    h+='</ul></details>';
  });
  $('md-body').innerHTML=h;
  openModal('modal-detail');
}

async function viewCode(path){
  var res=await api('/api/file_content?path='+encodeURIComponent(path));
  if(res.content){
    $('md-title').textContent='\ud83d\udcc4 '+path.split('/').pop();
    $('md-body').innerHTML='<p class="txt-sm txt-dim mb8">'+path+'</p><div class="code">'+esc(res.content)+'</div>';
  }else{toast(T('File not found'),'err')}
}

if (typeof registerLangRefresher === 'function') {
  registerLangRefresher(function refreshModelsLanguage() {
    if (document.querySelector('#page-models.active') && typeof renderModelsPage === 'function') renderModelsPage();
  });
}
