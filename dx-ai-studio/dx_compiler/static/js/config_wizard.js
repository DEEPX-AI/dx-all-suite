/* Config Builder Wizard */
(function() {
    let currentStep = 1;
    const totalSteps = 4;

    const CV2_INTERP = ['NEAREST', 'LINEAR', 'CUBIC', 'AREA', 'LANCZOS4'];
    const PIL_INTERP = ['NEAREST', 'BILINEAR', 'BICUBIC', 'LANCZOS', 'BOX', 'HAMMING'];
    const COLOR_FORMS = ['RGB2BGR', 'BGR2RGB', 'RGB2GRAY', 'BGR2GRAY', 'RGB2YCrCb', 'BGR2YCrCb', 'RGB2YUV', 'BGR2YUV', 'RGB2HSV', 'BGR2HSV', 'RGB2LAB', 'BGR2LAB'];
    const DTYPES = ['float32', 'float16', 'int8', 'uint8', 'int16', 'int32', 'int64'];

    function sel(options, defaultVal) { return {_options: options, _default: defaultVal}; }

    const RESIZE_MODES = {
        'default':     {params: {width: 224, height: 224, interpolation: sel(CV2_INTERP, 'LINEAR')}, desc: 'Standard resize to exact dimensions'},
        'mlcommons':   {params: {width: 224, height: 224, scale: 87.5, interpolation: sel(CV2_INTERP, 'NEAREST')}, desc: 'MLCommons benchmark style (short-side align)'},
        'scale':       {params: {scale: 0.875, interpolation: sel(CV2_INTERP, 'NEAREST')}, desc: 'Scale factor resize (no target size)'},
        'torchvision': {params: {size: 256, interpolation: sel(PIL_INTERP, 'BILINEAR')}, desc: 'PyTorch-style short-side resize'},
        'pad':         {params: {size: 640, pad_location: sel(['BACK', 'EDGE'], 'BACK'), pad_value: 0, interpolation: sel(CV2_INTERP, 'LINEAR')}, desc: 'Resize + pad to square'},
        'pycls':       {params: {size: 256, interpolation: sel(CV2_INTERP, 'LINEAR')}, desc: 'pycls-style short-side resize'},
    };

    const TRANSFORM_DEFAULTS = {
        resize: '_resize_modes',
        normalize: {mean: [0.485, 0.456, 0.406], std: [0.229, 0.224, 0.225]},
        transpose: {axis: [2, 0, 1]},
        expandDim: {axis: 0},
        centercrop: {width: 224, height: 224},
        centercrop2: {width: 224, height: 224},
        convertColor: {form: sel(COLOR_FORMS, 'RGB2BGR')},
        div: {x: 255.0},
        mul: {x: 1.0},
        subtract: {x: 0.0},
        add: {x: 0.0},
        squeeze: {axis: 0},
        pil_2_cv: null,
        dtype: {t: sel(DTYPES, 'float32')},
        slice: {channel: 3},
    };

    window.openWizard = function() {
        document.getElementById('config-wizard').style.display = 'flex';
    };
    window.closeWizard = function() {
        document.getElementById('config-wizard').style.display = 'none';
    };
    window.addInputRow = addInputRow;

    function wizGoTo(step) {
        const loaderMode = document.querySelector('input[name="loader_mode"]:checked');
        const isDummy = loaderMode && loaderMode.value === 'dummy';

        // Skip step 3 for dummy mode
        if (step === 3 && isDummy) {
            step = currentStep < 3 ? 4 : 2;
        }

        if (step < 1 || step > totalSteps) return;
        currentStep = step;

        // Update step visibility
        document.querySelectorAll('.wizard-step').forEach(s => s.classList.remove('active'));
        const target = document.querySelector('.wizard-step[data-step="' + step + '"]');
        if (target) target.classList.add('active');

        // Update dots
        document.querySelectorAll('.step-dot').forEach(d => {
            const ds = parseInt(d.dataset.step);
            d.classList.toggle('active', ds === step);
            d.classList.toggle('completed', ds < step);
        });

        // Update nav buttons
        document.getElementById('wiz-prev').style.display = step > 1 ? '' : 'none';
        const nextBtn = document.getElementById('wiz-next');
        if (step === totalSteps) {
            nextBtn.textContent = T('✅ Use This Config');
            updateJsonPreview();
        } else {
            nextBtn.textContent = T('Next →');
        }
    }

    // Message constants (centralized for i18n later)
    const MESSAGES = {
        EMPTY_PATH: 'Auto-detect did not run: ONNX file path is empty. Please provide a model path or add input shapes manually.',
        NOT_FOUND: 'Auto-detect did not run: ONNX file not found. Please verify the model path or add input shapes manually.',
        DYNAMIC_INPUTS: 'Note: Automatic input detection did not fill shapes because one or more inputs are dynamic. Please enter input shapes manually.',
        DETECTING: 'Detecting...'
    };

    function autoDetect() {
        const modelInput = document.getElementById('model_path');
        const path = modelInput ? modelInput.value : '';
        const wizWarn = document.getElementById('auto-detect-warning-wiz');
        if (wizWarn) { wizWarn.style.display = 'none'; wizWarn.textContent = ''; }
        if (!path) {
            if (wizWarn) { wizWarn.style.display = ''; wizWarn.textContent = T(MESSAGES.EMPTY_PATH); }
            return;
        }
        const btn = document.getElementById('btn-auto-detect');
        btn.disabled = true;
        btn.textContent = T('Detecting...');

        fetch('/model/inspect?path=' + encodeURIComponent(path))
            .then(r => r.json())
            .then(data => {
                btn.disabled = false;
                btn.textContent = T('🔍 Auto Detect from Model');
                if (data.error) {
                    if (wizWarn) { wizWarn.style.display = ''; wizWarn.textContent = T('Auto-detect skipped:') + ' ' + data.error; }
                    return;
                }
                // Clear existing rows
                document.getElementById('input-shapes-list').innerHTML = '';
                // Add detected inputs
                // Support two possible shapes formats for backward compatibility:
                // 1) { name: {shape: [...], dynamic: bool} }
                // 2) { name: [..] }
                let allStatic = true;
                for (const [name, payload] of Object.entries(data.inputs)) {
                    if (Array.isArray(payload)) {
                        addInputRow(name, payload);
                    } else if (payload && typeof payload === 'object') {
                        const shape = payload.shape || [];
                        const dynamic = !!payload.dynamic;
                        if (dynamic) allStatic = false;
                        addInputRow(name, shape);
                    } else {
                        // unknown format — skip
                        continue;
                    }
                }
                // Show banner when auto-detected (all inputs static) or server indicates auto_detected
                const banner = document.getElementById('auto-detect-banner');
                const serverFlag = data.auto_detected === true;
                if (banner) {
                    if (serverFlag || allStatic) {
                        banner.style.display = '';
                        if (wizWarn) { wizWarn.style.display = 'none'; wizWarn.textContent = ''; }
                    } else {
                        banner.style.display = 'none';
                        if (wizWarn) { wizWarn.style.display = ''; wizWarn.textContent = T(MESSAGES.DYNAMIC_INPUTS); }
                    }
                }
            })
            .catch(err => {
                btn.disabled = false;
                btn.textContent = T('🔍 Auto Detect from Model');
                if (wizWarn) { wizWarn.style.display = ''; wizWarn.textContent = T('Auto-detect failed:') + ' ' + (err.message || String(err)); }
            });
    }

    function addInputRow(name, shape) {
        name = name || '';
        shape = shape || [1, 3, 224, 224];
        const list = document.getElementById('input-shapes-list');
        const row = document.createElement('div');
        row.className = 'input-shape-row';

        const nameInput = document.createElement('input');
        nameInput.type = 'text';
        nameInput.className = 'shape-name';
        nameInput.value = name;
        nameInput.placeholder = 'input_name';

        const dimsInput = document.createElement('input');
        dimsInput.type = 'text';
        dimsInput.className = 'shape-dims';
        dimsInput.value = shape.join(', ');
        dimsInput.placeholder = '1, 3, 224, 224';

        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'btn-remove';
        removeBtn.textContent = '✕';
        removeBtn.addEventListener('click', function() { row.remove(); });

        row.appendChild(nameInput);
        row.appendChild(dimsInput);
        row.appendChild(removeBtn);
        list.appendChild(row);
    }

    function createParamField(key, val) {
        const lbl = document.createElement('label');
        lbl.textContent = key + ' ';
        if (val && val._options) {
            const select = document.createElement('select');
            select.className = 'prep-input';
            select.dataset.param = key;
            for (const o of val._options) {
                const opt = document.createElement('option');
                opt.value = o;
                opt.textContent = o;
                if (o === val._default) opt.selected = true;
                select.appendChild(opt);
            }
            lbl.appendChild(select);
        } else {
            const inp = document.createElement('input');
            inp.type = 'text';
            inp.className = 'prep-input';
            inp.dataset.param = key;
            inp.value = Array.isArray(val) ? val.join(', ') : val;
            lbl.appendChild(inp);
        }
        return lbl;
    }

    function renderResizeParams(container, mode) {
        const info = RESIZE_MODES[mode];
        if (!info) return;
        container.innerHTML = '';
        for (const [key, val] of Object.entries(info.params)) {
            container.appendChild(createParamField(key, val));
        }
    }

    function addPrepItem(name) {
        if (!name) return;
        const pipeline = document.getElementById('prep-pipeline');
        const item = document.createElement('div');
        item.className = 'prep-item';
        item.dataset.transform = name;

        // Header with remove button
        const header = document.createElement('div');
        header.className = 'prep-item-header';
        const title = document.createElement('strong');
        title.textContent = name;
        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'btn-remove';
        removeBtn.textContent = '✕';
        removeBtn.addEventListener('click', function() { item.remove(); });
        header.appendChild(title);
        header.appendChild(removeBtn);
        item.appendChild(header);

        if (name === 'resize') {
            // Mode selector
            const modeRow = document.createElement('div');
            modeRow.className = 'resize-mode-row';
            const modeLabel = document.createElement('label');
            modeLabel.textContent = 'mode ';
            const modeSelect = document.createElement('select');
            modeSelect.className = 'resize-mode-select';
            for (const m of Object.keys(RESIZE_MODES)) {
                const opt = document.createElement('option');
                opt.value = m;
                opt.textContent = m;
                if (m === 'default') opt.selected = true;
                modeSelect.appendChild(opt);
            }
            modeLabel.appendChild(modeSelect);
            modeRow.appendChild(modeLabel);

            const modeDesc = document.createElement('span');
            modeDesc.className = 'resize-mode-desc';
            modeDesc.textContent = RESIZE_MODES['default'].desc;
            modeRow.appendChild(modeDesc);
            item.appendChild(modeRow);

            // Mode-specific params
            const paramsDiv = document.createElement('div');
            paramsDiv.className = 'prep-params';
            renderResizeParams(paramsDiv, 'default');
            item.appendChild(paramsDiv);

            modeSelect.addEventListener('change', function() {
                renderResizeParams(paramsDiv, this.value);
                modeDesc.textContent = RESIZE_MODES[this.value].desc;
            });
        } else {
            const defaults = TRANSFORM_DEFAULTS[name];
            if (defaults === null) {
                const noParams = document.createElement('span');
                noParams.className = 'prep-no-params';
                noParams.textContent = T('No parameters');
                item.appendChild(noParams);
            } else {
                const paramsDiv = document.createElement('div');
                paramsDiv.className = 'prep-params';
                for (const [key, val] of Object.entries(defaults)) {
                    paramsDiv.appendChild(createParamField(key, val));
                }
                item.appendChild(paramsDiv);
            }
        }

        pipeline.appendChild(item);
        document.getElementById('prep-select').value = '';
    }

    function buildConfigJson() {
        const config = {};

        // Input shapes
        const inputShapes = {};
        document.querySelectorAll('.input-shape-row').forEach(row => {
            const name = row.querySelector('.shape-name').value.trim();
            const dims = row.querySelector('.shape-dims').value.trim()
                .split(',').map(d => parseInt(d.trim())).filter(d => !isNaN(d));
            if (name && dims.length) inputShapes[name] = dims;
        });
        config.input_shapes = inputShapes;

        // Loader mode
        const loaderMode = document.querySelector('input[name="loader_mode"]:checked');
        config.loader_mode = loaderMode ? loaderMode.value : 'dummy';

        // Default loader fields
        if (config.loader_mode === 'default') {
            const dp = document.getElementById('wiz-dataset-path').value.trim();
            if (dp) config.dataset_path = dp;

            const fe = document.getElementById('wiz-file-extensions').value.trim();
            if (fe) config.file_extensions = fe.split(',').map(s => s.trim()).filter(s => s);

            const cn = document.getElementById('wiz-calib-num').value;
            if (cn) config.calibration_num = parseInt(cn);

            const cm = document.getElementById('wiz-calib-method').value;
            if (cm) config.calibration_method = cm;

            // Preprocessings
            const preps = [];
            document.querySelectorAll('.prep-item').forEach(item => {
                const tName = item.dataset.transform;
                if (tName === 'resize') {
                    const modeSelect = item.querySelector('.resize-mode-select');
                    const mode = modeSelect ? modeSelect.value : 'default';
                    const params = {mode: mode};
                    item.querySelectorAll('.prep-input').forEach(inp => {
                        const key = inp.dataset.param;
                        const raw = inp.value.trim();
                        if (raw.includes(',')) {
                            params[key] = raw.split(',').map(v => parseFloat(v.trim()));
                        } else {
                            const num = parseFloat(raw);
                            params[key] = isNaN(num) ? raw : num;
                        }
                    });
                    preps.push({resize: params});
                    return;
                }
                const defaults = TRANSFORM_DEFAULTS[tName];
                if (defaults === null) {
                    preps.push({[tName]: null});
                    return;
                }
                const params = {};
                item.querySelectorAll('.prep-input').forEach(inp => {
                    const key = inp.dataset.param;
                    const raw = inp.value.trim();
                    if (raw.includes(',')) {
                        params[key] = raw.split(',').map(v => parseFloat(v.trim()));
                    } else {
                        const num = parseFloat(raw);
                        params[key] = isNaN(num) ? raw : num;
                    }
                });
                preps.push({[tName]: params});
            });
            if (preps.length) config.preprocessings = preps;
        }

        return config;
    }

    function updateJsonPreview() {
        const config = buildConfigJson();
        // Build the final config structure (like the server does)
        const preview = {inputs: config.input_shapes || {}};
        if (config.loader_mode === 'default') {
            const dl = {};
            if (config.dataset_path) dl.dataset_path = config.dataset_path;
            if (config.file_extensions) dl.file_extensions = config.file_extensions;
            if (config.preprocessings) dl.preprocessings = config.preprocessings;
            preview.default_loader = dl;
        }
        if (config.calibration_num) preview.calibration_num = config.calibration_num;
        if (config.calibration_method) preview.calibration_method = config.calibration_method;
        document.getElementById('wiz-json-preview').textContent = JSON.stringify(preview, null, 2);
    }

    function generateConfig() {
        const config = buildConfigJson();
        const nextBtn = document.getElementById('wiz-next');
        nextBtn.disabled = true;
        nextBtn.textContent = T('Generating...');

        fetch('/config/generate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(config),
        })
        .then(r => r.json())
        .then(data => {
            nextBtn.disabled = false;
            nextBtn.textContent = T('✅ Use This Config');
            if (data.error) {
                alert(T('Config generation failed: ') + data.error);
                return;
            }
            // Set config_path and close wizard
            const configInput = document.getElementById('config_path');
            if (configInput) configInput.value = data.path;
            closeWizard();
        })
        .catch(err => {
            nextBtn.disabled = false;
            nextBtn.textContent = T('✅ Use This Config');
            alert(T('Config generation failed: ') + err.message);
        });
    }

    function updateModeCards() {
        document.querySelectorAll('.mode-card').forEach(card => {
            const radio = card.querySelector('input[type="radio"]');
            card.classList.toggle('selected', radio && radio.checked);
        });
    }

    document.addEventListener('DOMContentLoaded', function() {
        const prevBtn = document.getElementById('wiz-prev');
        const nextBtn = document.getElementById('wiz-next');
        const addInputBtn = document.getElementById('btn-add-input');
        const autoDetectBtn = document.getElementById('btn-auto-detect');
        const addPrepBtn = document.getElementById('btn-add-prep');

        if (prevBtn) prevBtn.addEventListener('click', function() { wizGoTo(currentStep - 1); });
        if (nextBtn) nextBtn.addEventListener('click', function() {
            if (currentStep === totalSteps) {
                generateConfig();
            } else {
                wizGoTo(currentStep + 1);
            }
        });
        if (addInputBtn) addInputBtn.addEventListener('click', function() { addInputRow('', null); });
        if (autoDetectBtn) autoDetectBtn.addEventListener('click', autoDetect);
        if (addPrepBtn) addPrepBtn.addEventListener('click', function() {
            const sel = document.getElementById('prep-select');
            addPrepItem(sel.value);
        });

        // Loader mode radio change
        document.querySelectorAll('input[name="loader_mode"]').forEach(radio => {
            radio.addEventListener('change', updateModeCards);
        });
    });

    window.applyWizardPatches = function(patches) {
        if (!Array.isArray(patches)) return;
        patches.forEach(function(p) {
            if (!p || p.target !== 'wizard') return;
            if (p.field === 'open' || p.value === true) {
                openWizard();
                const toggle = document.getElementById('config_build_toggle');
                if (toggle && !toggle.checked) {
                    toggle.checked = true;
                    toggle.dispatchEvent(new Event('change'));
                }
            }
            if (p.field === 'input_shapes' && p.value && typeof p.value === 'object') {
                openWizard();
                const list = document.getElementById('input-shapes-list');
                if (list) list.innerHTML = '';
                Object.entries(p.value).forEach(function(entry) {
                    addInputRow(entry[0], entry[1]);
                });
                wizGoTo(1);
            }
            if ((p.field === 'dataset_path' || p.field === 'calibration_dataset') && typeof p.value === 'string') {
                openWizard();
                const dp = document.getElementById('wiz-dataset-path');
                if (dp) dp.value = p.value;
                const defRadio = document.querySelector('input[name="loader_mode"][value="default"]');
                if (defRadio) {
                    defRadio.checked = true;
                    updateModeCards();
                }
                wizGoTo(2);
            }
            if (p.field === 'calibration_num') {
                const cn = document.getElementById('wiz-calib-num');
                if (cn) cn.value = p.value;
            }
            if (p.field === 'calibration_method') {
                const cm = document.getElementById('wiz-calib-method');
                if (cm) cm.value = p.value;
            }
        });
        updateJsonPreview();
    };
})();
if (typeof registerCompilerLangRefresher === 'function') {
  registerCompilerLangRefresher(function() {
    if (typeof DXI18n !== 'undefined' && DXI18n.applyLang) DXI18n.applyLang(document);
  });
}
