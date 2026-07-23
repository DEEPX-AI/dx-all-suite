/**
 * DX Stream — 파이프라인 빌더 (bootstrap)
 * 모듈 로드 순서: state → api → serialization → renderer → bootstrap
 * contextmenu + touch 이벤트를 pipelineInit 에 바인딩한다.
 */

/* contextmenu + touch 바인딩 */
var _origPipelineInit = DXStream.pipelineInit;
DXStream.pipelineInit = async function () {
    if (_origPipelineInit) await _origPipelineInit();
    var canvas = DXStream.$('pipeline-canvas');
    if (canvas && !canvas.dataset.pipeContextBound) {
        canvas.dataset.pipeContextBound = '1';
        canvas.addEventListener('contextmenu', _showContextMenu);
        _initTouchEvents(canvas);
    }
};
