/**
 * DX Stream — pipeline builder (bootstrap)
 * Module load order: state → api → serialization → renderer → bootstrap
 * Binds the contextmenu and touch events in pipelineInit.
 */

/* contextmenu + touch bindings */
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
