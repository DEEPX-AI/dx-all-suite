window.LabComposer = (function () {
  'use strict';

  var currentWorkflow = null;
  var currentTab = 'quick-start';
  var models = [];
  var composerCapabilities = null;
  var modelLoadError = false;
  var customizationHistory = [];
  var customizationHistoryIndex = -1;
  var pendingPluginScaffold = null;
  var savedRecipe = null;
  var compatibleAssets = [];
  var compatibleAssetKey = '';
  var graphEditor = null;
  var graphValidation = { blocked: false, blockers: [] };
  var graphSyncTimer = 0;
  var MAX_CUSTOMIZATION_HISTORY = 20;
  var PLUGIN_DRAG_MIME = 'application/x-dx-app-composer-plugin';
  var MODEL_DRAG_MIME = 'application/x-dx-app-composer-model';
  var ASSET_DRAG_MIME = 'application/x-dx-app-composer-asset';
  var modelSearchQuery = '';
  var expandedModelCategories = {};
  var DEFERRED_COMPOSER_ROUTES = [
    '/api/lab/composer/recipe/export',
    '/api/lab/composer/recipe/import'
  ];

  var ComposerState = {
    selectedNodeId: 'input',
    selectedTemplateModelFile: '',
    dragKind: '',
    get workflow() {
      return currentWorkflow && currentWorkflow.workflow;
    }
  };

  var ComposerApi = {
    update: function (updates) {
      return applyCustomization(updates);
    }
  };

  var ComposerRenderer = {
    palette: renderBuilderPalette,
    canvas: renderBuilderCanvas,
    inspector: renderBuilderInspector
  };

  function text(key) {
    return typeof T === 'function' ? T(key) : key;
  }

  function composerLabels() {
    if (typeof T !== 'function') {
      return {
        quickStart: 'Quick Start',
        templates: 'Templates',
        customize: 'Customize',
        undo: 'Undo',
        redo: 'Redo',
        startHint: 'Pick a runnable model to build and run a workflow.',
        saveOutput: 'Save Output',
        selectInputAsset: 'Select input asset',
        deviceId: 'Device ID',
        invalidDeviceId: 'Device ID must be a non-negative integer',
        pluginPalette: 'Plugin palette',
        dragPlugin: 'Drag a custom plugin to Preprocess or Postprocess',
        customPlugin: 'Custom plugin',
        saveRecipe: 'Save Recipe',
        exportRecipe: 'Export Recipe',
        importRecipe: 'Import Recipe',
        runPackage: 'Run Package',
        developerPackage: 'Developer Package',
        reusableRecipe: 'Reusable Recipe',
        exportPreflight: 'Export Preflight',
        recipeSaved: 'Recipe saved',
        recipeImportFailed: 'Recipe import failed',
        recipeExportFailed: 'Recipe export failed',
        chooseRecipe: 'Choose a recipe JSON file',
        copyOutVerified: 'Copy-out verified',
        plugins: 'Plugins',
        validation: 'Validation',
        addCustomPreprocess: 'Add custom preprocess',
        addCustomPostprocess: 'Add custom postprocess',
        applyPluginScaffold: 'Apply Plugin Scaffold',
        runWorkflow: 'Run Workflow',
        exportPackage: 'Export Package',
        validationBlocked: 'Workflow validation blocked',
        builder: 'Builder',
        runnableModels: 'Runnable Models',
        compatibleAssets: 'Compatible Assets',
        canvas: 'Canvas',
        inspector: 'Inspector',
        dropModelHere: 'Drop model here',
        dropAssetHere: 'Drop asset here',
        builtInFactoryComponent: 'Built-in Factory Component',
        pluginFactoryIntegration: 'Plugin execution requires Factory integration',
        preprocessResolvedByFactory: 'Preprocessing is resolved by the selected model Factory.',
        postprocessSettings: 'Postprocess settings',
        noPostprocessSettings: 'No postprocess settings are available for this model.',
        postprocessImplementation: 'Postprocess implementation',
        standardPostprocess: 'Standard postprocess',
        cppPostprocess: 'C++ postprocess',
        fixedCoreChain: 'The core chain is fixed so the selected DX App Factory and SyncRunner remain executable.',
        fitView: 'Fit view',
        zoomIn: 'Zoom in',
        zoomOut: 'Zoom out',
        validateGraph: 'Validate graph',
        graphReady: 'Graph ready',
        graphBlocked: 'Graph blocked',
        missingConnection: 'Missing required connection',
        connectionNotAllowed: 'Connection is not allowed',
        coreStagesFixed: 'Core stages are fixed',
        pluginScaffold: 'Plugin scaffold',
        genericAssetsHint: 'No category-specific asset found — showing generic sample assets.'
      };
    }
    return {
      quickStart: T('Quick Start'),
      templates: T('Templates'),
      customize: T('Customize'),
      undo: T('Undo'),
      redo: T('Redo'),
      startHint: T('Pick a runnable model to build and run a workflow.'),
      saveOutput: T('Save Output'),
      selectInputAsset: T('Select input asset'),
      deviceId: T('Device ID'),
      invalidDeviceId: T('Device ID must be a non-negative integer'),
      pluginPalette: T('Plugin palette'),
      dragPlugin: T('Drag a custom plugin to Preprocess or Postprocess'),
      customPlugin: T('Custom plugin'),
      saveRecipe: T('Save Recipe'),
      exportRecipe: T('Export Recipe'),
      importRecipe: T('Import Recipe'),
      runPackage: T('Run Package'),
      developerPackage: T('Developer Package'),
      reusableRecipe: T('Reusable Recipe'),
      exportPreflight: T('Export Preflight'),
      recipeSaved: T('Recipe saved'),
      recipeImportFailed: T('Recipe import failed'),
      recipeExportFailed: T('Recipe export failed'),
      chooseRecipe: T('Choose a recipe JSON file'),
      copyOutVerified: T('Copy-out verified'),
      plugins: T('Plugins'),
      validation: T('Validation'),
      addCustomPreprocess: T('Add custom preprocess'),
      addCustomPostprocess: T('Add custom postprocess'),
      applyPluginScaffold: T('Apply Plugin Scaffold'),
      runWorkflow: T('Run Workflow'),
      exportPackage: T('Export Package'),
      validationBlocked: T('Workflow validation blocked'),
      builder: T('Builder'),
      runnableModels: T('Runnable Models'),
      compatibleAssets: T('Compatible Assets'),
      canvas: T('Canvas'),
      inspector: T('Inspector'),
      dropModelHere: T('Drop model here'),
      dropAssetHere: T('Drop asset here'),
      builtInFactoryComponent: T('Built-in Factory Component'),
      pluginFactoryIntegration: T('Plugin execution requires Factory integration'),
      preprocessResolvedByFactory: T('Preprocessing is resolved by the selected model Factory.'),
      postprocessSettings: T('Postprocess settings'),
      noPostprocessSettings: T('No postprocess settings are available for this model.'),
      postprocessImplementation: T('Postprocess implementation'),
      standardPostprocess: T('Standard postprocess'),
      cppPostprocess: T('C++ postprocess'),
      fixedCoreChain: T('The core chain is fixed so the selected DX App Factory and SyncRunner remain executable.'),
      fitView: T('Fit view'),
      zoomIn: T('Zoom in'),
      zoomOut: T('Zoom out'),
      validateGraph: T('Validate graph'),
      graphReady: T('Graph ready'),
      graphBlocked: T('Graph blocked'),
      missingConnection: T('Missing required connection'),
      connectionNotAllowed: T('Connection is not allowed'),
      coreStagesFixed: T('Core stages are fixed'),
      pluginScaffold: T('Plugin scaffold'),
      genericAssetsHint: T('No category-specific asset found — showing generic sample assets.')
    };
  }

  function isBlocked(validation) {
    return !validation || validation.status !== "ready";
  }

  function make(tag, className, value) {
    var element = document.createElement(tag);
    if (className) element.className = className;
    if (value !== undefined && value !== null) element.textContent = value;
    return element;
  }

  function clear(element) {
    if (element) element.textContent = '';
  }

  function root() {
    return document.getElementById('lab-flow-root');
  }

  function isRunnable(model) {
    return !!(model && model.model_exists && (model.cpp_sync || model.py_sync));
  }

  function selectionFor(model) {
    return {
      name: model.name,
      category: model.category,
      model_file: model.model_file
    };
  }

  function labelFor(model) {
    return model.name + ' · ' + model.category;
  }

  function modelForFile(modelFile) {
    return models.find(function (model) {
      return isRunnable(model) && model.model_file === modelFile;
    }) || null;
  }

  function selectedPaletteModel() {
    var workflow = ComposerState.workflow || {};
    var currentModel = workflow.model || {};
    return modelForFile(currentModel.model_file) || modelForFile(ComposerState.selectedTemplateModelFile);
  }

  function applyModelSelection(model) {
    if (!isRunnable(model)) return Promise.resolve();
    ComposerState.selectedTemplateModelFile = model.model_file;
    if (!currentWorkflow) {
      if (currentTab === 'templates') {
        render();
        return Promise.resolve();
      }
      return createQuickStart(model);
    }
    return ComposerApi.update({ model_selection: { model_file: model.model_file } });
  }

  function applyAssetSelection(path) {
    if (!currentWorkflow || typeof path !== 'string' || !path) return Promise.resolve();
    return ComposerApi.update({ input_selection: { path: path } });
  }

  async function request(path, payload) {
    if (window.LabPortal && typeof window.LabPortal.request === 'function') {
      return window.LabPortal.request(path, payload);
    }
    return postJ(path, payload);
  }

  function hasConfig(model) {
    return !!(model && model.config && typeof model.config === 'object'
      && Object.keys(model.config).length);
  }

  function dedupeRunnableModels(list) {
    // One .dxnn can be reached by both an SDK example-dir name and a registry alias
    // (e.g. 'yolov5' + 'yolov5s' → yolov5-s_640x640.dxnn). The palette must offer that
    // runnable binary once; keep the entry that carries a real config (server still
    // re-resolves the runner and identity at Run/Export time). Models with no
    // model_file are preserved individually.
    var byFile = {};
    var order = [];
    list.forEach(function (model) {
      var mf = model && model.model_file ? model.model_file : '';
      if (!mf) { order.push({ model: model }); return; }
      if (!Object.prototype.hasOwnProperty.call(byFile, mf)) {
        byFile[mf] = model;
        order.push({ file: mf });
      } else if (!hasConfig(byFile[mf]) && hasConfig(model)) {
        byFile[mf] = model;
      }
    });
    var out = [];
    var seen = {};
    order.forEach(function (item) {
      if (item.file) {
        if (!seen[item.file]) { seen[item.file] = true; out.push(byFile[item.file]); }
      } else {
        out.push(item.model);
      }
    });
    return out;
  }

  async function loadModels() {
    if (models.length) return models;
    modelLoadError = false;
    try {
      var response = await fetch('/api/models');
      if (!response.ok) throw new Error('models_http_' + response.status);
      var data = await response.json();
      models = Array.isArray(data) ? dedupeRunnableModels(data.filter(isRunnable)) : [];
    } catch (err) {
      models = [];
      modelLoadError = true;
    }
    return models;
  }

  function loadCapabilities() {
    if (window.LabPortal && typeof window.LabPortal.capabilities === 'function') {
      composerCapabilities = window.LabPortal.capabilities();
    }
    return composerCapabilities && composerCapabilities.composer ? composerCapabilities.composer : null;
  }

  function setStatus(message, kind) {
    var status = document.getElementById('lab-status');
    if (!status) return;
    status.textContent = message;
    status.className = 'lab-status lab-status-' + (kind || 'info');
  }

  function appendOption(select, value, label) {
    var option = make('option', '', label);
    option.value = value;
    select.appendChild(option);
  }

  function selectedModel(select) {
    var index = Number(select.value);
    return Number.isInteger(index) && index >= 0 ? models[index] : null;
  }

  function appendModelSelect(parent, id) {
    var field = make('div', 'fg');
    var label = make('label', '', text('Model'));
    label.setAttribute('for', id);
    var select = make('select', 'input');
    select.id = id;
    appendOption(select, '', text('Select Model'));
    models.forEach(function (model, index) {
      appendOption(select, String(index), labelFor(model));
    });
    field.appendChild(label);
    field.appendChild(select);
    parent.appendChild(field);
    return select;
  }

  function assetKeyFor(workflow) {
    var input = workflow && workflow.input ? workflow.input : {};
    var model = workflow && workflow.model ? workflow.model : {};
    return [input.kind || '', model.category || ''].join(':');
  }

  async function loadCompatibleAssets(workflow) {
    var input = workflow && workflow.input ? workflow.input : {};
    var kind = input.kind;
    var key = assetKeyFor(workflow);
    if (key === compatibleAssetKey) return compatibleAssets;
    compatibleAssetKey = key;
    compatibleAssets = [];
    if (kind !== 'image' && kind !== 'video') return compatibleAssets;
    var category = encodeURIComponent((workflow.model || {}).category || '');
    var url = kind === 'video'
      ? '/api/videos?category=' + category
      : '/api/images?category=' + category;
    try {
      var response = await fetch(url);
      var data = response.ok ? await response.json() : [];
      if (compatibleAssetKey === key) {
        compatibleAssets = Array.isArray(data) ? data.filter(function (asset) {
          return typeof asset === 'string' && asset;
        }) : [];
      }
    } catch (err) {
      if (compatibleAssetKey === key) compatibleAssets = [];
    }
    return compatibleAssets;
  }

  function customizationSnapshot(workflow) {
    var execution = workflow && workflow.execution ? workflow.execution : {};
    var plugins = workflow && Array.isArray(workflow.plugins) ? workflow.plugins : [];
    var model = workflow && workflow.model ? workflow.model : {};
    var input = workflow && workflow.input ? workflow.input : {};
    return {
      model_file: typeof model.model_file === 'string' ? model.model_file : '',
      input_path: typeof input.path === 'string' ? input.path : '',
      execution: {
        device_id: execution.device_id === undefined ? null : execution.device_id,
        save_output: execution.save_output !== false,
        config_overrides: execution.config_overrides && typeof execution.config_overrides === 'object'
          && !Array.isArray(execution.config_overrides)
          ? JSON.parse(JSON.stringify(execution.config_overrides)) : {},
        postprocess_implementation: typeof execution.postprocess_implementation === 'string'
          ? execution.postprocess_implementation : 'standard'
      },
      graph_layout: workflow && workflow.graph_layout ? JSON.parse(JSON.stringify(workflow.graph_layout)) : null,
      plugins: plugins.filter(function (plugin) {
        return plugin && typeof plugin.id === 'string';
      }).map(function (plugin) {
        return { id: plugin.id, enabled: plugin.enabled === true };
      })
    };
  }

  function recordCustomizationState() {
    if (!currentWorkflow || !currentWorkflow.workflow) return;
    var snapshot = customizationSnapshot(currentWorkflow.workflow);
    var current = customizationHistory[customizationHistoryIndex];
    if (current && JSON.stringify(current) === JSON.stringify(snapshot)) return;
    customizationHistory = customizationHistory.slice(0, customizationHistoryIndex + 1);
    customizationHistory.push(snapshot);
    if (customizationHistory.length > MAX_CUSTOMIZATION_HISTORY) customizationHistory.shift();
    customizationHistoryIndex = customizationHistory.length - 1;
  }

  function resetCustomizationHistory() {
    customizationHistory = [];
    customizationHistoryIndex = -1;
    recordCustomizationState();
  }

  function historyPatch(snapshot) {
    var workflow = currentWorkflow && currentWorkflow.workflow ? currentWorkflow.workflow : {};
    var enabledById = {};
    (snapshot.plugins || []).forEach(function (plugin) {
      enabledById[plugin.id] = plugin.enabled;
    });
    var updates = {
      execution: {
        device_id: snapshot.execution.device_id,
        save_output: snapshot.execution.save_output,
        config_overrides: snapshot.execution.config_overrides || {},
        postprocess_implementation: snapshot.execution.postprocess_implementation || 'standard'
      },
      plugins: (workflow.plugins || []).filter(function (plugin) {
        return plugin && typeof plugin.id === 'string';
      }).map(function (plugin) {
        return { id: plugin.id, enabled: enabledById[plugin.id] === true };
      })
    };
    if (snapshot.model_file) {
      updates.model_selection = { model_file: snapshot.model_file };
    }
    if (snapshot.input_path) {
      updates.input_selection = { path: snapshot.input_path };
    }
    if (snapshot.graph_layout) updates.graph_layout = snapshot.graph_layout;
    return updates;
  }

  function setWorkflow(response, historyAction) {
    if (!response || !response.workflow || !response.manifest_id) {
      renderError(response && response.error ? response.error : text('Workflow validation blocked'));
      return;
    }
    currentWorkflow = {
      manifest_id: response.manifest_id,
      workflow: response.workflow,
      validation: response.validation || response.workflow.validation || {},
      status: response.status,
      processorCapabilities: response.processor_capabilities || {}
    };
    savedRecipe = null;
    graphValidation = { blocked: false, blockers: [] };
    if (historyAction === 'record') recordCustomizationState();
    else if (historyAction !== 'preserve') resetCustomizationHistory();
    render();
    loadCompatibleAssets(currentWorkflow.workflow).then(function () {
      if (currentWorkflow && compatibleAssetKey === assetKeyFor(currentWorkflow.workflow)) render();
    });
    var blocked = isBlocked(currentWorkflow.validation);
    setStatus(
      blocked ? composerLabels().validationBlocked : text('Workflow ready'),
      blocked ? 'err' : 'ok'
    );
  }

  function renderError(message) {
    var result = document.getElementById('lab-composer-result');
    if (!result) return;
    clear(result);
    result.appendChild(make('p', 'lab-composer-error', message));
    setStatus(message, 'err');
  }

  function renderValidation(parent, validation) {
    if (!validation) return;
    var blocked = isBlocked(validation);
    parent.appendChild(make(
      'p',
      blocked ? 'lab-composer-validation lab-composer-validation-blocked' : 'lab-composer-validation lab-composer-validation-ready',
      blocked ? composerLabels().validationBlocked : text('Workflow ready')
    ));
    var blockers = Array.isArray(validation.blockers) ? validation.blockers : [];
    if (blockers.length) {
      var list = make('ul', 'lab-composer-blockers');
      blockers.forEach(function (blocker) {
        list.appendChild(make('li', '', blocker.node_id + ': ' + blocker.code));
      });
      parent.appendChild(list);
    }
    var warnings = Array.isArray(validation.warnings) ? validation.warnings : [];
    if (warnings.length) {
      var warningList = make('ul', 'lab-composer-warnings');
      warnings.forEach(function (warning) {
        warningList.appendChild(make('li', '', warning.node_id ? warning.node_id + ': ' + warning.code : String(warning)));
      });
      parent.appendChild(warningList);
    }
  }

  function renderWorkflowSummary(parent) {
    if (!currentWorkflow || !currentWorkflow.workflow) return;
    var workflow = currentWorkflow.workflow;
    var model = workflow.model || {};
    var input = workflow.input || {};
    var summary = make('section', 'lab-composer-summary');
    summary.appendChild(make('h3', '', text('Workflow Preview')));
    var details = make('dl', 'lab-composer-summary-details');
    var modelIdentity = [model.name, model.category].filter(Boolean).join(' · ');
    var inputIdentity = [input.kind, input.path].filter(Boolean).join(' · ');
    [
      [text('Model'), modelIdentity || text('Unavailable')],
      [text('Input'), inputIdentity || text('Unavailable')]
    ].forEach(function (item) {
      details.appendChild(make('dt', '', item[0]));
      details.appendChild(make('dd', '', item[1]));
    });
    summary.appendChild(details);
    parent.appendChild(summary);
  }

  function nodeBlockers(node) {
    var validation = currentWorkflow && currentWorkflow.validation ? currentWorkflow.validation : {};
    var blockers = Array.isArray(validation.blockers) ? validation.blockers : [];
    return blockers.filter(function (blocker) {
      return blocker && blocker.node_id === node.id;
    });
  }

  function nodeParameterSummary(node) {
    var params = node && node.params && typeof node.params === 'object' ? node.params : {};
    var entries = Object.keys(params).map(function (key) {
      return key + ': ' + String(params[key]);
    });
    return entries.length ? entries.join(', ') : text('Built-in defaults');
  }

  function processorCapabilities() {
    var capabilities = currentWorkflow && currentWorkflow.processorCapabilities;
    if (!capabilities || typeof capabilities !== 'object') {
      return { preprocess: { factory_owned: true }, postprocess: {} };
    }
    return capabilities;
  }

  function postprocessExecution(workflow) {
    var execution = workflow && workflow.execution && typeof workflow.execution === 'object'
      ? workflow.execution : {};
    var overrides = execution.config_overrides;
    return {
      config_overrides: overrides && typeof overrides === 'object' && !Array.isArray(overrides)
        ? JSON.parse(JSON.stringify(overrides)) : {},
      postprocess_implementation: typeof execution.postprocess_implementation === 'string'
        ? execution.postprocess_implementation : 'standard'
    };
  }

  function appendPostprocessTunableControl(parent, key, fallbackValue, workflow) {
    var field = make('div', 'lab-composer-node-control');
    var id = 'lab-composer-postprocess-' + key;
    var label = make('label', '', key);
    label.setAttribute('for', id);
    var input = document.createElement('input');
    var state = postprocessExecution(workflow);
    var value = Object.prototype.hasOwnProperty.call(state.config_overrides, key)
      ? state.config_overrides[key] : fallbackValue;
    input.className = 'input';
    input.id = id;
    input.type = 'number';
    input.step = 'any';
    input.value = value === undefined || value === null ? '' : String(value);
    input.addEventListener('change', function () {
      var nextValue = Number(input.value);
      if (!Number.isFinite(nextValue)) {
        renderError(composerLabels().validationBlocked);
        return;
      }
      var next = postprocessExecution(currentWorkflow && currentWorkflow.workflow);
      next.config_overrides[key] = nextValue;
      ComposerApi.update({ execution: { config_overrides: next.config_overrides } });
    });
    field.appendChild(label);
    field.appendChild(input);
    parent.appendChild(field);
  }

  function appendPostprocessImplementationControl(parent, options, workflow) {
    if (!Array.isArray(options) || options.length < 2) return;
    var field = make('div', 'lab-composer-node-control');
    var label = make('label', '', composerLabels().postprocessImplementation);
    label.setAttribute('for', 'lab-composer-postprocess-implementation');
    var select = make('select', 'input');
    select.id = 'lab-composer-postprocess-implementation';
    options.forEach(function (option) {
      if (option === 'standard') appendOption(select, option, composerLabels().standardPostprocess);
      if (option === 'cpp_postprocess') appendOption(select, option, composerLabels().cppPostprocess);
    });
    var state = postprocessExecution(workflow);
    select.value = options.indexOf(state.postprocess_implementation) !== -1
      ? state.postprocess_implementation : 'standard';
    select.addEventListener('change', function () {
      if (options.indexOf(select.value) === -1) return;
      ComposerApi.update({ execution: { postprocess_implementation: select.value } });
    });
    field.appendChild(label);
    field.appendChild(select);
    parent.appendChild(field);
  }

  function appendBuiltInProcessorControls(parent, stage) {
    var workflow = currentWorkflow && currentWorkflow.workflow ? currentWorkflow.workflow : {};
    if (stage === 'preprocess') {
      parent.appendChild(make(
        'p', 'lab-composer-factory-note', composerLabels().preprocessResolvedByFactory
      ));
      return;
    }

    var capabilities = processorCapabilities().postprocess || {};
    var keys = Array.isArray(capabilities.tunable_keys) ? capabilities.tunable_keys : [];
    var defaults = capabilities.tunable_defaults && typeof capabilities.tunable_defaults === 'object'
      ? capabilities.tunable_defaults : {};
    var options = Array.isArray(capabilities.implementation_options)
      ? capabilities.implementation_options : ['standard'];
    parent.appendChild(make('h4', '', composerLabels().postprocessSettings));
    if (!keys.length) {
      parent.appendChild(make('p', 'lab-composer-factory-note', composerLabels().noPostprocessSettings));
    } else {
      keys.forEach(function (key) {
        if (typeof key === 'string' && Object.prototype.hasOwnProperty.call(defaults, key)) {
          appendPostprocessTunableControl(parent, key, defaults[key], workflow);
        }
      });
    }
    appendPostprocessImplementationControl(parent, options, workflow);
  }

  function appendPluginControls(card, stage) {
    var workflow = currentWorkflow && currentWorkflow.workflow ? currentWorkflow.workflow : {};
    var plugins = Array.isArray(workflow.plugins) ? workflow.plugins : [];
    plugins.filter(function (plugin) {
      return plugin && plugin.stage === stage && typeof plugin.id === 'string';
    }).forEach(function (plugin) {
      var toggle = make('label', 'lab-composer-plugin-toggle');
      var checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.checked = plugin.enabled === true;
      checkbox.addEventListener('change', function () {
        applyCustomization({ plugins: [{ id: plugin.id, enabled: checkbox.checked }] });
      });
      toggle.appendChild(checkbox);
      toggle.appendChild(make('span', '', plugin.id));
      card.appendChild(toggle);
    });

    var control = make('div', 'lab-composer-plugin-control');
    var language = make('select', 'input');
    appendOption(language, 'python', 'Python');
    appendOption(language, 'cpp', 'C++');
    var label = stage === 'preprocess'
      ? composerLabels().addCustomPreprocess
      : composerLabels().addCustomPostprocess;
    var button = appendActionButton(control, 'btn-blue', label, function () {
      planPluginScaffold(stage, language.value);
    });
    button.classList.add('lab-composer-plugin-button');
    card.appendChild(control);
  }

  function appendModelCustomization(card, workflow) {
    var field = make('div', 'lab-composer-node-control');
    var label = make('label', '', text('Model'));
    label.setAttribute('for', 'lab-composer-workflow-model');
    var select = make('select', 'input');
    select.id = 'lab-composer-workflow-model';
    appendOption(select, '', text('Select Model'));
    models.forEach(function (model, index) {
      appendOption(select, String(index), labelFor(model));
      if (workflow.model && workflow.model.model_file === model.model_file) select.value = String(index);
    });
    select.addEventListener('change', function () {
      var selected = selectedModel(select);
      if (!selected) return;
      applyCustomization({ model_selection: { model_file: selected.model_file } });
    });
    field.appendChild(label);
    field.appendChild(select);
    card.appendChild(field);
  }

  function appendAssetCustomization(card, workflow) {
    var input = workflow.input || {};
    if (input.kind !== 'image' && input.kind !== 'video') return;
    var field = make('div', 'lab-composer-node-control');
    var label = make('label', '', composerLabels().selectInputAsset);
    label.setAttribute('for', 'lab-composer-input-asset');
    var select = make('select', 'input');
    select.id = 'lab-composer-input-asset';
    var assets = compatibleAssetKey === assetKeyFor(workflow) ? compatibleAssets.slice() : [];
    if (input.path && assets.indexOf(input.path) === -1) assets.unshift(input.path);
    appendOption(select, '', composerLabels().selectInputAsset);
    assets.forEach(function (asset) {
      appendOption(select, asset, asset);
    });
    select.value = input.path || '';
    select.disabled = !assets.length;
    select.addEventListener('change', function () {
      if (!select.value) return;
      applyCustomization({ input_selection: { path: select.value } });
    });
    field.appendChild(label);
    field.appendChild(select);
    card.appendChild(field);
  }

  function appendExecutionControls(card, workflow) {
    var execution = workflow.execution || {};
    var field = make('div', 'lab-composer-node-control');
    var label = make('label', '', composerLabels().deviceId);
    label.setAttribute('for', 'lab-composer-device-id');
    var device = document.createElement('input');
    device.className = 'input';
    device.id = 'lab-composer-device-id';
    device.type = 'number';
    device.min = '0';
    device.step = '1';
    device.value = execution.device_id === null || execution.device_id === undefined ? '' : String(execution.device_id);
    device.addEventListener('change', function () {
      var deviceId = device.value === '' ? null : Number(device.value);
      if (deviceId !== null && (!Number.isInteger(deviceId) || deviceId < 0)) {
        renderError(composerLabels().invalidDeviceId);
        return;
      }
      applyCustomization({ execution: { device_id: deviceId } });
    });
    field.appendChild(label);
    field.appendChild(device);
    card.appendChild(field);
  }

  function appendPluginDropTarget(card, stage) {
    card.classList.add('lab-composer-plugin-drop-target');
    card.setAttribute('data-plugin-drop-stage', stage);
    card.appendChild(make('p', 'lab-composer-drop-hint', composerLabels().dragPlugin));
    card.addEventListener('dragover', function (event) {
      if (!event.dataTransfer || !Array.prototype.includes.call(event.dataTransfer.types, PLUGIN_DRAG_MIME)) return;
      event.preventDefault();
      card.classList.add('lab-composer-plugin-drop-active');
      event.dataTransfer.dropEffect = 'copy';
    });
    card.addEventListener('dragleave', function () {
      card.classList.remove('lab-composer-plugin-drop-active');
    });
    card.addEventListener('drop', function (event) {
      event.preventDefault();
      card.classList.remove('lab-composer-plugin-drop-active');
      var language = event.dataTransfer ? event.dataTransfer.getData(PLUGIN_DRAG_MIME) : '';
      if (language !== 'python' && language !== 'cpp') return;
      planPluginScaffold(stage, language);
    });
  }

  function renderPluginPalette(graph) {
    var palette = make('section', 'lab-composer-plugin-palette');
    palette.appendChild(make('h4', '', composerLabels().pluginPalette));
    palette.appendChild(make('p', 'txt-dim txt-sm', composerLabels().dragPlugin));
    ['python', 'cpp'].forEach(function (language) {
      var chip = make('button', 'lab-composer-plugin-chip', language === 'python' ? 'Python' : 'C++');
      chip.type = 'button';
      chip.draggable = true;
      chip.setAttribute('aria-label', language + ' ' + composerLabels().customPlugin);
      chip.addEventListener('dragstart', function (event) {
        if (!event.dataTransfer) return;
        event.dataTransfer.effectAllowed = 'copy';
        event.dataTransfer.setData(PLUGIN_DRAG_MIME, language);
      });
      palette.appendChild(chip);
    });
    graph.appendChild(palette);
  }

  function appendChoice(parent, label, className, selected, clickHandler, dragMime, dragValue) {
    var button = make('button', className + (selected ? ' selected' : ''), label);
    button.type = 'button';
    button.setAttribute('aria-pressed', String(selected));
    button.addEventListener('click', clickHandler);
    if (dragMime && typeof dragValue === 'string') {
      button.draggable = true;
      button.addEventListener('dragstart', function (event) {
        if (!event.dataTransfer) return;
        ComposerState.dragKind = dragMime;
        event.dataTransfer.effectAllowed = 'copy';
        event.dataTransfer.setData(dragMime, dragValue);
      });
    }
    parent.appendChild(button);
    return button;
  }

  function availableAssets() {
    var workflow = ComposerState.workflow || {};
    var input = workflow.input || {};
    var assets = compatibleAssetKey === assetKeyFor(workflow) ? compatibleAssets.slice() : [];
    if (input.path && assets.indexOf(input.path) === -1) assets.unshift(input.path);
    return assets;
  }

  function modelGroupKey(model) {
    return (model && model.category) || '';
  }

  function modelGroupLabel(model) {
    return (model && (model.category_label || model.category)) || text('Uncategorized');
  }

  function modelMatchesQuery(model, query) {
    if (!query) return true;
    var haystack = (labelFor(model) + ' ' + modelGroupKey(model) + ' ' + modelGroupLabel(model)).toLowerCase();
    return haystack.indexOf(query) !== -1;
  }

  function renderModelGroups(list) {
    clear(list);
    var query = modelSearchQuery.trim().toLowerCase();
    var selected = selectedPaletteModel();
    var groups = {};
    var order = [];
    models.forEach(function (model) {
      if (!modelMatchesQuery(model, query)) return;
      var key = modelGroupKey(model);
      if (!Object.prototype.hasOwnProperty.call(groups, key)) {
        groups[key] = [];
        order.push(key);
      }
      groups[key].push(model);
    });
    if (!order.length) {
      list.appendChild(make('p', 'lab-composer-empty', text('No models match your search.')));
      return;
    }
    order.sort(function (a, b) {
      return modelGroupLabel(groups[a][0]).localeCompare(modelGroupLabel(groups[b][0]));
    });
    order.forEach(function (key) {
      var groupModels = groups[key];
      // Default OPEN: a category stays expanded until the user explicitly collapses it
      // (expandedModelCategories[key] is undefined on first paint / for untouched groups).
      var stored = expandedModelCategories[key];
      var expanded = !!query || (stored === undefined ? true : stored);
      var group = make('div', 'lab-composer-model-group');
      group.setAttribute('data-collapsed', String(!expanded));
      var head = make('button', 'lab-composer-model-group-head',
        modelGroupLabel(groupModels[0]) + ' (' + groupModels.length + ')');
      head.type = 'button';
      head.setAttribute('aria-expanded', String(expanded));
      head.addEventListener('click', function () {
        var currentlyExpanded = group.getAttribute('data-collapsed') !== 'true';
        expandedModelCategories[key] = !currentlyExpanded;
        group.setAttribute('data-collapsed', String(currentlyExpanded));
        head.setAttribute('aria-expanded', String(!currentlyExpanded));
      });
      group.appendChild(head);
      groupModels.forEach(function (model) {
        appendChoice(
          group,
          labelFor(model),
          'lab-composer-palette-item lab-composer-model-choice',
          !!selected && selected.model_file === model.model_file,
          function () { applyModelSelection(model); },
          MODEL_DRAG_MIME,
          model.model_file
        );
      });
      list.appendChild(group);
    });
  }

  function appendModelChoices(parent) {
    if (!models.length) {
      parent.appendChild(make('p', 'lab-composer-empty', modelLoadError
        ? text('Unable to load runnable models. Check the Lab connection and try again.')
        : text('No runnable models are installed. Download a DXNN model before creating a workflow.')));
      return;
    }
    var section = make('div', 'lab-composer-model-palette');
    var search = document.createElement('input');
    search.type = 'search';
    search.className = 'lab-composer-model-search';
    search.placeholder = text('Search models...');
    search.setAttribute('aria-label', text('Search models...'));
    search.value = modelSearchQuery;
    var list = make('div', 'lab-composer-model-list');
    search.addEventListener('input', function (event) {
      modelSearchQuery = event.target.value;
      renderModelGroups(list);
    });
    section.appendChild(search);
    section.appendChild(list);
    parent.appendChild(section);
    renderModelGroups(list);
  }

  function assetBasename(path) {
    var value = String(path || '');
    var slash = value.lastIndexOf('/');
    return slash >= 0 ? value.slice(slash + 1) : value;
  }

  function isImageAssetPath(path) {
    return /\.(jpe?g|png|bmp|webp|gif)$/i.test(String(path || ''));
  }

  function appendAssetThumbnail(button, path) {
    // Image inputs get a visual preview so users pick by sight, not filename. dx_app
    // serves sample inputs at /file/<path>; the path comes from the trusted server asset
    // list. Lazy-loaded; a non-image (video/pair dir) or missing file hides the img and
    // falls back to the filename caption. DOM-safe: element APIs only, no HTML strings.
    if (!isImageAssetPath(path)) return;
    var img = document.createElement('img');
    img.className = 'lab-composer-asset-thumb';
    img.loading = 'lazy';
    img.decoding = 'async';
    img.alt = '';
    // Server downscales to a small preview (82x54px display) instead of shipping the
    // full-res original; falls back to hiding the img on any error. Path is from the
    // trusted server asset list; encode it so subdirs/spaces survive the query string.
    img.src = '/api/asset-thumb?w=160&f=' + encodeURIComponent(path);
    img.addEventListener('error', function () { img.style.display = 'none'; });
    button.insertBefore(img, button.firstChild);
  }

  function appendAssetChoices(parent) {
    var workflow = ComposerState.workflow || {};
    var input = workflow.input || {};
    var assets = availableAssets();
    if (!currentWorkflow) {
      parent.appendChild(make('p', 'txt-dim txt-sm', text('Choose a model to create a workflow first.')));
      return;
    }
    if (!assets.length) {
      parent.appendChild(make('p', 'lab-composer-empty', composerLabels().selectInputAsset));
      return;
    }
    // input_generic is a sibling key set by the workflow resolver (lab_portal.py) when no
    // model-demo or category default asset was available/installed, so it fell back to the
    // generic asset gallery. Surface that here rather than implying these are model-specific.
    if (workflow.input_generic === true) {
      parent.appendChild(make('p', 'lab-composer-generic-hint txt-dim txt-sm', composerLabels().genericAssetsHint));
    }
    var grid = make('div', 'lab-composer-asset-grid');
    assets.forEach(function (asset) {
      var choice = appendChoice(
        grid,
        assetBasename(asset),
        'lab-composer-palette-item lab-composer-asset-choice',
        input.path === asset,
        function () { applyAssetSelection(asset); },
        ASSET_DRAG_MIME,
        asset
      );
      appendAssetThumbnail(choice, asset);
    });
    parent.appendChild(grid);
  }

  function appendSelectionDropTarget(card, kind) {
    var dragMime = kind === 'model' ? MODEL_DRAG_MIME : ASSET_DRAG_MIME;
    var hint = kind === 'model' ? composerLabels().dropModelHere : composerLabels().dropAssetHere;
    card.classList.add('lab-composer-selection-drop-target');
    card.setAttribute('data-drop-kind', kind);
    card.appendChild(make('p', 'lab-composer-drop-hint', hint));
    card.addEventListener('dragover', function (event) {
      if (!event.dataTransfer || !Array.prototype.includes.call(event.dataTransfer.types, dragMime)) return;
      event.preventDefault();
      card.classList.add('lab-composer-drop-active');
      event.dataTransfer.dropEffect = 'copy';
    });
    card.addEventListener('dragleave', function () {
      card.classList.remove('lab-composer-drop-active');
    });
    card.addEventListener('drop', function (event) {
      event.preventDefault();
      card.classList.remove('lab-composer-drop-active');
      var value = event.dataTransfer ? event.dataTransfer.getData(dragMime) : '';
      if (kind === 'model') {
        var model = modelForFile(value);
        if (model) applyModelSelection(model);
        return;
      }
      if (availableAssets().indexOf(value) !== -1) applyAssetSelection(value);
    });
  }

  function nodeLabel(kind) {
    return {
      input: 'Input',
      builtin_preprocess: 'Preprocess',
      inference: 'Inference',
      builtin_postprocess: 'Postprocess',
      builtin_visualizer: 'Visualize'
    }[kind] || kind;
  }

  function nodeIdForKind(kind) {
    return {
      input: 'input',
      builtin_preprocess: 'preprocess',
      inference: 'inference',
      builtin_postprocess: 'postprocess',
      builtin_visualizer: 'visualize'
    }[kind] || kind;
  }

  function builderNodes() {
    var workflow = ComposerState.workflow || {};
    var nodes = Array.isArray(workflow.nodes) ? workflow.nodes : [];
    var kinds = [
      'input',
      'builtin_preprocess',
      'inference',
      'builtin_postprocess',
      'builtin_visualizer'
    ];
    return kinds.map(function (kind) {
      return nodes.find(function (node) { return node && node.id === nodeIdForKind(kind); }) || {
        id: nodeIdForKind(kind), kind: kind,
        enabled: true,
        params: {}
      };
    });
  }

  function builderNodeSummary(node) {
    var workflow = ComposerState.workflow || {};
    var model = workflow.model || {};
    var input = workflow.input || {};
    if (node.kind === 'input') return input.path || text('Unavailable');
    if (node.kind === 'inference') return model.name ? labelFor(model) : text('Unavailable');
    if (node.kind === 'builtin_preprocess' || node.kind === 'builtin_postprocess') {
      return composerLabels().builtInFactoryComponent;
    }
    if (node.kind === 'builtin_visualizer') return text('Built-in defaults');
    return nodeParameterSummary(node);
  }

  function selectBuilderNode(nodeId) {
    ComposerState.selectedNodeId = nodeId;
    var inspector = document.getElementById('lab-composer-inspector');
    if (!inspector || !inspector.parentNode) return;
    var parent = inspector.parentNode;
    inspector.remove();
    renderBuilderInspector(parent);
  }

  // Each templates entry carries { category, input_kind }. A template with a category
  // must match the selected model's category. Templates with no category (the
  // input_kind 'video'/'camera' capture flows, e.g. RTSP/webcam starting points) apply
  // across every model category, so they stay visible no matter which model is selected.
  function templateVisibleForCategory(entry, modelCategory) {
    if (!modelCategory) return true;
    if (!entry || !entry.category) return true;
    return entry.category === modelCategory;
  }

  function filterTemplateIds(templates, modelCategory) {
    return Object.keys(templates || {}).filter(function (templateId) {
      return templateVisibleForCategory(templates[templateId], modelCategory);
    });
  }

  function renderBuilderPalette(parent) {
    var palette = make('aside', 'lab-composer-palette');
    palette.appendChild(make('h3', '', composerLabels().builder));
    renderTabs(palette);
    if (currentTab === 'templates') {
      palette.appendChild(make('h4', '', composerLabels().runnableModels));
      appendModelChoices(palette);
      palette.appendChild(make('h4', '', composerLabels().templates));
      var composer = loadCapabilities();
      var templates = composer && composer.templates ? composer.templates : {};
      var paletteModel = selectedPaletteModel();
      var visibleTemplateIds = filterTemplateIds(templates, paletteModel && paletteModel.category);
      visibleTemplateIds.forEach(function (templateId) {
        appendChoice(
          palette,
          templateId.replace(/_/g, ' '),
          'lab-composer-palette-item lab-composer-template-choice',
          false,
          function () { createTemplate(templateId, selectedPaletteModel()); }
        );
      });
      if (!visibleTemplateIds.length) {
        palette.appendChild(make('p', 'txt-dim txt-sm', text('Templates are unavailable until the Lab session is ready.')));
      }
    } else {
      palette.appendChild(make('h4', '', composerLabels().runnableModels));
      appendModelChoices(palette);
    }
    palette.appendChild(make('h4', '', composerLabels().compatibleAssets));
    appendAssetChoices(palette);
    renderPluginPalette(palette);
    parent.appendChild(palette);
  }

  function selectedBuilderNode() {
    var nodes = builderNodes();
    return nodes.find(function (node) { return node.id === ComposerState.selectedNodeId; }) || nodes[0];
  }

  function graphEditorLabels() {
    var labels = composerLabels();
    return {
      undo: labels.undo,
      redo: labels.redo,
      fitView: labels.fitView,
      zoomIn: labels.zoomIn,
      zoomOut: labels.zoomOut,
      validate: labels.validateGraph,
      graphReady: labels.graphReady,
      graphBlocked: labels.graphBlocked,
      input: text('Input'),
      preprocess: text('Preprocess'),
      inference: text('Inference'),
      postprocess: text('Postprocess'),
      visualize: text('Visualize'),
      builtIn: labels.builtInFactoryComponent,
      unavailable: text('Unavailable'),
      canvas: labels.canvas,
      minimap: text('Minimap')
    };
  }

  function updateGraphActionState() {
    var blocked = !currentWorkflow || isBlocked(currentWorkflow.validation) || graphValidation.blocked;
    [
      document.getElementById('lab-composer-run'),
      document.getElementById('lab-composer-export')
    ].forEach(function (button) {
      if (button) button.disabled = blocked;
    });
  }

  function scheduleGraphLayoutSync(layout) {
    if (!currentWorkflow || graphValidation.blocked) return;
    if (graphSyncTimer) window.clearTimeout(graphSyncTimer);
    graphSyncTimer = window.setTimeout(function () {
      graphSyncTimer = 0;
      if (currentWorkflow && !graphValidation.blocked) {
        ComposerApi.update({ graph_layout: layout });
      }
    }, 250);
  }

  function handleGraphDrop(drop) {
    if (!drop) return;
    if (drop.mime === MODEL_DRAG_MIME && drop.targetId === 'inference') {
      var model = modelForFile(drop.value);
      if (model) applyModelSelection(model);
      return;
    }
    if (drop.mime === ASSET_DRAG_MIME && drop.targetId === 'input') {
      if (availableAssets().indexOf(drop.value) !== -1) applyAssetSelection(drop.value);
      return;
    }
    if (drop.mime === PLUGIN_DRAG_MIME && (drop.targetId === 'preprocess' || drop.targetId === 'postprocess')) {
      if (drop.value === 'python' || drop.value === 'cpp') planPluginScaffold(drop.targetId, drop.value);
    }
  }

  function renderBuilderCanvas(parent) {
    var canvas = make('section', 'lab-composer-canvas');
    canvas.appendChild(make('h3', '', composerLabels().canvas));
    canvas.appendChild(make('p', 'txt-dim txt-sm', composerLabels().fixedCoreChain));
    if (!currentWorkflow) {
      // Actionable empty state: the fixed chain renders greyed "Unavailable" nodes before
      // a model is chosen, which reads as broken. Tell the user the one action that starts it.
      canvas.appendChild(make('p', 'lab-composer-start-hint', composerLabels().startHint));
    }
    var host = make('div', 'lab-composer-graph-host');
    canvas.appendChild(host);
    if (!window.LabComposerGraph || typeof window.LabComposerGraph.create !== 'function') {
      host.appendChild(make('p', 'lab-composer-error', text('Workflow validation blocked')));
      parent.appendChild(canvas);
      return;
    }
    if (graphEditor) graphEditor.destroy();
    var workflow = ComposerState.workflow || {};
    graphEditor = window.LabComposerGraph.create(host, workflow.graph_layout, {
      labels: graphEditorLabels(),
      onSelect: selectBuilderNode,
      onDrop: handleGraphDrop,
      onValidationChange: function (validation) {
        graphValidation = validation;
        updateGraphActionState();
      },
      onLayoutChange: function (layout, validation) {
        graphValidation = validation;
        updateGraphActionState();
        scheduleGraphLayoutSync(layout);
      }
    });
    graphEditor.setWorkflow(workflow);
    graphValidation = graphEditor.validate();
    parent.appendChild(canvas);
  }

  function appendInspectorAssetPicker(parent) {
    // Compact per-node picker. The full browseable/draggable Compatible Assets list
    // lives once in the Builder palette; the Inspector only needs to show and change
    // THIS node's selected asset (no duplicate long list). Reuses the trusted,
    // server-validated applyAssetSelection mutation.
    if (!currentWorkflow) {
      parent.appendChild(make('p', 'txt-dim txt-sm', text('Choose a model to create a workflow first.')));
      return;
    }
    var assets = availableAssets();
    if (!assets.length) {
      parent.appendChild(make('p', 'lab-composer-empty', composerLabels().selectInputAsset));
      return;
    }
    var workflow = ComposerState.workflow || {};
    var current = (workflow.input || {}).path || '';
    var field = make('div', 'fg');
    var select = make('select', 'input');
    select.id = 'lab-composer-inspector-asset';
    assets.forEach(function (asset) { appendOption(select, asset, asset); });
    if (assets.indexOf(current) !== -1) select.value = current;
    select.addEventListener('change', function () {
      if (availableAssets().indexOf(select.value) !== -1) applyAssetSelection(select.value);
    });
    field.appendChild(select);
    parent.appendChild(field);
  }

  function appendInspectorModelPicker(parent) {
    // Compact per-node model picker; the full draggable Runnable Models list stays in
    // the palette. Reuses the trusted applyModelSelection mutation (server re-resolves).
    if (!models.length) {
      parent.appendChild(make('p', 'lab-composer-empty', modelLoadError
        ? text('Unable to load runnable models. Check the Lab connection and try again.')
        : text('No runnable models are installed. Download a DXNN model before creating a workflow.')));
      return;
    }
    var current = selectedPaletteModel();
    var currentIndex = -1;
    var field = make('div', 'fg');
    var select = make('select', 'input');
    select.id = 'lab-composer-inspector-model';
    models.forEach(function (model, index) {
      appendOption(select, String(index), labelFor(model));
      if (current && current.model_file === model.model_file) currentIndex = index;
    });
    if (currentIndex !== -1) select.value = String(currentIndex);
    select.addEventListener('change', function () {
      var model = models[Number(select.value)];
      if (model) applyModelSelection(model);
    });
    field.appendChild(select);
    parent.appendChild(field);
  }

  function renderBuilderInspector(parent) {
    var inspector = make('aside', 'lab-composer-inspector');
    inspector.id = 'lab-composer-inspector';
    var node = selectedBuilderNode();
    inspector.appendChild(make('h3', '', composerLabels().inspector));
    inspector.appendChild(make('h4', '', text(nodeLabel(node.kind))));
    inspector.appendChild(make('p', 'txt-dim txt-sm', builderNodeSummary(node)));
    if (node.kind === 'input') {
      inspector.appendChild(make('h4', '', composerLabels().compatibleAssets));
      appendInspectorAssetPicker(inspector);
    } else if (node.kind === 'inference') {
      inspector.appendChild(make('h4', '', composerLabels().runnableModels));
      appendInspectorModelPicker(inspector);
    } else if (node.kind === 'builtin_preprocess' || node.kind === 'builtin_postprocess') {
      var stage = node.kind === 'builtin_preprocess' ? 'preprocess' : 'postprocess';
      inspector.appendChild(make('p', 'lab-composer-factory-note', composerLabels().builtInFactoryComponent));
      inspector.appendChild(make('p', 'lab-composer-factory-note', composerLabels().pluginFactoryIntegration));
      appendBuiltInProcessorControls(inspector, stage);
      if (currentWorkflow) appendPluginControls(inspector, stage);
    } else if (node.kind === 'builtin_visualizer' && currentWorkflow) {
      var workflow = currentWorkflow.workflow || {};
      var saveOutput = make('label', 'lab-composer-plugin-toggle');
      var checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.checked = workflow.execution && workflow.execution.save_output !== false;
      checkbox.addEventListener('change', function () {
        ComposerApi.update({ execution: { save_output: checkbox.checked } });
      });
      saveOutput.appendChild(checkbox);
      saveOutput.appendChild(make('span', '', composerLabels().saveOutput));
      inspector.appendChild(saveOutput);
      appendExecutionControls(inspector, workflow);
    }
    parent.appendChild(inspector);
  }

  function renderHistoryControls(graph) {
    var controls = make('div', 'lab-composer-history');
    var undo = appendActionButton(controls, 'btn-blue', composerLabels().undo, undoCustomization);
    undo.disabled = customizationHistoryIndex <= 0;
    var redo = appendActionButton(controls, 'btn-blue', composerLabels().redo, redoCustomization);
    redo.disabled = customizationHistoryIndex < 0 || customizationHistoryIndex >= customizationHistory.length - 1;
    graph.appendChild(controls);
  }

  function renderPluginScaffoldPreview(graph) {
    if (!pendingPluginScaffold) return;
    var preview = make('section', 'lab-composer-plugin-preview');
    preview.appendChild(make('h4', '', text('Plugin scaffold preview')));
    (pendingPluginScaffold.operations || []).forEach(function (operation) {
      preview.appendChild(make('p', 'txt-sm', operation.path || text('Unavailable')));
    });
    preview.appendChild(appendActionButton(
      preview,
      'btn-acc',
      composerLabels().applyPluginScaffold,
      applyPluginScaffold
    ));
    graph.appendChild(preview);
  }

  function renderGraph(parent) {
    var graph = make('section', 'lab-composer-graph');
    graph.id = 'lab-composer-graph';
    renderHistoryControls(graph);
    var builder = make('div', 'lab-composer-builder');
    ComposerRenderer.palette(builder);
    ComposerRenderer.canvas(builder);
    ComposerRenderer.inspector(builder);
    graph.appendChild(builder);
    renderPluginScaffoldPreview(graph);
    parent.appendChild(graph);
  }

  function renderResult(parent) {
    var result = make('section', 'lab-composer-result');
    result.id = 'lab-composer-result';
    result.appendChild(make('h3', '', text('Workflow Result')));
    if (!currentWorkflow) {
      result.appendChild(make('p', 'txt-dim', text('Run a ready workflow to view visual output.')));
    }
    parent.appendChild(result);
  }

  function appendActionButton(parent, className, label, handler) {
    var button = make('button', 'btn ' + className, label);
    button.type = 'button';
    button.addEventListener('click', handler);
    parent.appendChild(button);
    return button;
  }

  function renderActions(parent) {
    var actions = make('div', 'lab-composer-actions');
    var validation = currentWorkflow && currentWorkflow.validation ? currentWorkflow.validation : {};
    var blocked = !currentWorkflow || isBlocked(validation) || graphValidation.blocked;
    var runButton = appendActionButton(actions, 'btn-acc', composerLabels().runWorkflow, runWorkflow);
    runButton.id = 'lab-composer-run';
    runButton.disabled = blocked;
    var exportButton = appendActionButton(actions, 'btn-blue', composerLabels().exportPackage, function () {
      exportPackage('run');
    });
    exportButton.id = 'lab-composer-export';
    exportButton.disabled = blocked;
    parent.appendChild(actions);
  }

  function renderRecipeControls(parent) {
    var validation = currentWorkflow && currentWorkflow.validation ? currentWorkflow.validation : {};
    if (!currentWorkflow || isBlocked(validation) || graphValidation.blocked) return;
    var section = make('section', 'lab-composer-recipe-controls');
    section.appendChild(make('h3', '', composerLabels().saveRecipe));
    var actions = make('div', 'lab-composer-recipe-actions');
    appendActionButton(actions, 'btn-blue', composerLabels().saveRecipe, saveRecipe);
    appendActionButton(actions, 'btn-blue', composerLabels().exportRecipe, exportRecipe);
    var importLabel = make('label', 'btn btn-blue', composerLabels().importRecipe);
    importLabel.setAttribute('for', 'lab-composer-recipe-file');
    var importFile = document.createElement('input');
    importFile.id = 'lab-composer-recipe-file';
    importFile.type = 'file';
    importFile.accept = '.json,application/json';
    importFile.className = 'lab-composer-recipe-file';
    importFile.addEventListener('change', function () {
      var file = importFile.files && importFile.files[0];
      if (!file) return;
      var reader = new FileReader();
      reader.onload = function () {
        var recipe;
        try {
          recipe = JSON.parse(String(reader.result || ''));
        } catch (err) {
          renderError(composerLabels().recipeImportFailed);
          return;
        }
        if (typeof recipe !== 'object' || recipe === null || Array.isArray(recipe)) {
          renderError(composerLabels().recipeImportFailed);
          return;
        }
        importRecipe(recipe);
      };
      reader.onerror = function () {
        renderError(composerLabels().recipeImportFailed);
      };
      reader.readAsText(file);
      importFile.value = '';
    });
    actions.appendChild(importLabel);
    actions.appendChild(importFile);
    section.appendChild(actions);
    if (savedRecipe) section.appendChild(make('p', 'txt-dim txt-sm', composerLabels().recipeSaved));
    parent.appendChild(section);
  }

  function renderExportPanel(parent) {
    var validation = currentWorkflow && currentWorkflow.validation ? currentWorkflow.validation : {};
    if (!currentWorkflow || isBlocked(validation) || graphValidation.blocked) return;
    var workflow = currentWorkflow.workflow || {};
    var model = workflow.model || {};
    var input = workflow.input || {};
    var plugins = Array.isArray(workflow.plugins) ? workflow.plugins : [];
    var section = make('section', 'lab-composer-export-panel');
    section.appendChild(make('h3', '', composerLabels().exportPreflight));
    var summary = make('dl', 'lab-composer-export-summary');
    [
      [text('Model'), [model.name, model.category].filter(Boolean).join(' · ') || text('Unavailable')],
      [text('Input'), [input.kind, input.path].filter(Boolean).join(' · ') || text('Unavailable')],
      [composerLabels().plugins, plugins.length ? plugins.map(function (plugin) { return plugin.id; }).join(', ') : text('Built-in defaults')],
      [composerLabels().validation, validation.status]
    ].forEach(function (item) {
      summary.appendChild(make('dt', '', item[0]));
      summary.appendChild(make('dd', '', item[1]));
    });
    section.appendChild(summary);
    var actions = make('div', 'lab-composer-export-actions');
    [
      ['run', composerLabels().runPackage],
      ['developer', composerLabels().developerPackage],
      ['recipe', composerLabels().reusableRecipe]
    ].forEach(function (choice) {
      appendActionButton(actions, 'btn-blue', choice[1], function () {
        exportPackage(choice[0]);
      });
    });
    section.appendChild(actions);
    parent.appendChild(section);
  }

  async function createQuickStart(model) {
    if (!model) {
      renderError(text('Select Model'));
      return;
    }
    setStatus(text('Creating workflow'), 'info');
    var result = await request('/api/lab/composer/quick_start', { selection: selectionFor(model) });
    setWorkflow(result);
  }

  async function createTemplate(templateId, model) {
    setStatus(text('Creating workflow'), 'info');
    var payload = { template_id: templateId };
    if (model) payload.selection = selectionFor(model);
    var result = await request('/api/lab/composer/template', payload);
    if (result && result.error_code === 'template_model_mismatch') {
      renderError(result.error || text('Template is not compatible with the selected model.'));
      return;
    }
    setWorkflow(result);
  }

  async function applyCustomization(updates, historyIndex) {
    if (!currentWorkflow) return;
    setStatus(text('Updating workflow'), 'info');
    var result = await request("/api/lab/composer/customize", {
      manifest_id: currentWorkflow.manifest_id,
      updates: updates
    });
    if (!result || result.error) {
      renderError((result && result.error) || text('Workflow validation blocked'));
      return;
    }
    if (typeof historyIndex === 'number') customizationHistoryIndex = historyIndex;
    setWorkflow(result, typeof historyIndex === 'number' ? 'preserve' : 'record');
  }

  async function undoCustomization() {
    if (customizationHistoryIndex <= 0) return;
    var targetIndex = customizationHistoryIndex - 1;
    await applyCustomization(historyPatch(customizationHistory[targetIndex]), targetIndex);
  }

  async function redoCustomization() {
    if (customizationHistoryIndex < 0 || customizationHistoryIndex >= customizationHistory.length - 1) return;
    var targetIndex = customizationHistoryIndex + 1;
    await applyCustomization(historyPatch(customizationHistory[targetIndex]), targetIndex);
  }

  async function planPluginScaffold(stage, language) {
    if (!currentWorkflow) return;
    setStatus(text('Creating Plugin Scaffold'), 'info');
    var result = await request('/api/lab/composer/plugin/dry_run', {
      workflow_manifest_id: currentWorkflow.manifest_id,
      plugin_name: 'custom_' + stage,
      stage: stage,
      language: language
    });
    if (!result || result.error) {
      renderError((result && result.error) || text('Plugin scaffold planning failed'));
      return;
    }
    pendingPluginScaffold = result;
    render();
  }

  async function applyPluginScaffold() {
    if (!pendingPluginScaffold) return;
    var confirmations = {};
    var required = Array.isArray(pendingPluginScaffold.confirmations)
      ? pendingPluginScaffold.confirmations : [];
    for (var index = 0; index < required.length; index += 1) {
      var confirmation = required[index];
      if (typeof window.confirm === 'function' && !window.confirm(confirmation.label)) return;
      confirmations[confirmation.key] = confirmation.expected;
    }
    setStatus(text('Applying Plugin Scaffold'), 'info');
    var result = await request('/api/lab/composer/plugin/apply', {
      plugin_manifest_id: pendingPluginScaffold.id,
      confirmations: confirmations
    });
    if (!result || result.error) {
      renderError((result && result.error) || text('Plugin scaffold apply failed'));
      return;
    }
    pendingPluginScaffold = null;
    setWorkflow(result, 'record');
  }

  function renderQuickStart(parent) {
    var panel = make('section', 'lab-composer-panel');
    panel.appendChild(make('h3', '', composerLabels().quickStart));
    panel.appendChild(make('p', 'txt-dim txt-sm', text('Select a runnable model and let Lab choose a compatible input.')));
    var select = appendModelSelect(panel, 'lab-composer-model');
    if (modelLoadError) {
      panel.appendChild(make('p', 'lab-composer-empty', text('Unable to load runnable models. Check the Lab connection and try again.')));
    } else if (!models.length) {
      panel.appendChild(make('p', 'lab-composer-empty', text('No runnable models are installed. Download a DXNN model before creating a workflow.')));
    }
    select.addEventListener('change', function () {
      createQuickStart(selectedModel(select));
    });
    parent.appendChild(panel);
  }

  function renderTemplates(parent) {
    var panel = make('section', 'lab-composer-panel');
    panel.appendChild(make('h3', '', composerLabels().templates));
    panel.appendChild(make('p', 'txt-dim txt-sm', text('Start with a supported task and a compatible runnable model.')));
    var modelSelect = appendModelSelect(panel, 'lab-composer-template-model');
    var templateGrid = make('div', 'lab-composer-template-grid');
    var composer = loadCapabilities();
    var templates = composer && composer.templates ? composer.templates : {};
    Object.keys(templates).forEach(function (templateId) {
      var button = make('button', 'lab-composer-template', templateId.replace(/_/g, ' '));
      button.type = 'button';
      button.addEventListener('click', function () {
        createTemplate(templateId, selectedModel(modelSelect));
      });
      templateGrid.appendChild(button);
    });
    if (!templateGrid.childNodes.length) {
      templateGrid.appendChild(make('p', 'txt-dim', text('Templates are unavailable until the Lab session is ready.')));
    }
    panel.appendChild(templateGrid);
    parent.appendChild(panel);
  }

  function renderTabs(parent) {
    var tabs = make('div', 'lab-composer-tabs');
    [
      { id: 'quick-start', label: composerLabels().quickStart },
      { id: 'templates', label: composerLabels().templates }
    ].forEach(function (tab) {
      var button = make('button', 'lab-composer-tab' + (currentTab === tab.id ? ' active' : ''), tab.label);
      button.type = 'button';
      button.setAttribute('aria-selected', String(currentTab === tab.id));
      button.addEventListener('click', function () {
        currentTab = tab.id;
        render();
      });
      tabs.appendChild(button);
    });
    parent.appendChild(tabs);
  }

  function render() {
    var container = root();
    if (!container) return;
    if (graphEditor) {
      graphEditor.destroy();
      graphEditor = null;
    }
    clear(container);
    var shell = make('section', 'lab-composer');
    shell.appendChild(make('h2', 'lab-composer-title', text('DX App Composer')));
    renderGraph(shell);
    renderWorkflowSummary(shell);
    if (currentWorkflow) renderValidation(shell, currentWorkflow.validation);
    renderActions(shell);
    // Result sits directly under Run/Export so the run→result feedback loop needs no
    // scroll past the recipe and export-preflight panels.
    renderResult(shell);
    renderRecipeControls(shell);
    renderExportPanel(shell);
    container.appendChild(shell);
  }

  function refreshComposerLanguage() {
    // Composer builds its DOM with T() at render time (no data-i18n attributes), so a
    // language switch cannot be applied by DXI18n.applyLang — re-render to re-translate.
    // But only when the composer is actually on screen: LabComposer.open() already
    // re-renders with the current language every time the composer flow is (re-)selected,
    // so re-rendering a hidden composer just wastes a full teardown+rebuild plus a re-fetch
    // of every asset thumbnail. offsetParent === null ⇒ hidden (display:none ancestor).
    var el = root();
    if (el && el.offsetParent !== null) render();
  }

  function safeOutputUrl(value) {
    return typeof value === 'string' && value.indexOf('/outputs/') === 0 ? value : '';
  }

  function renderRunResult(data) {
    var result = document.getElementById('lab-composer-result');
    if (!result) return;
    clear(result);
    result.appendChild(make('h3', '', text('Workflow Result')));
    if (!data || data.error) {
      result.appendChild(make('p', 'lab-composer-error', (data && data.error) || text('Workflow run failed')));
      return;
    }
    var image = data.result_image;
    var imageUrl = safeOutputUrl(data.result_image_url);
    var videoUrl = safeOutputUrl(data.result_video_url);
    if (typeof image === 'string' && image) {
      var imageElement = document.createElement('img');
      imageElement.className = 'res-img';
      imageElement.alt = text('Workflow Result');
      imageElement.src = 'data:image/jpeg;base64,' + image;
      result.appendChild(imageElement);
    } else if (imageUrl) {
      var outputImage = document.createElement('img');
      outputImage.className = 'res-img';
      outputImage.alt = text('Workflow Result');
      outputImage.src = imageUrl;
      result.appendChild(outputImage);
    } else if (videoUrl) {
      var video = document.createElement('video');
      video.className = 'res-img';
      video.controls = true;
      video.src = videoUrl;
      result.appendChild(video);
    } else {
      result.appendChild(make('p', 'txt-dim', text('Workflow completed without a visual output.')));
    }
    ['exit_code', 'fps', 'latency_ms'].forEach(function (key) {
      if (data[key] !== undefined && data[key] !== null) {
        result.appendChild(make('p', 'txt-sm', key + ': ' + String(data[key])));
      }
    });
  }

  async function runWorkflow() {
    if (!currentWorkflow || graphValidation.blocked) {
      renderError(composerLabels().graphBlocked);
      return;
    }
    setStatus(text('Running workflow'), 'info');
    var result = await runComposerWithProgress(currentWorkflow.manifest_id);
    renderRunResult(result);
    setStatus(result && result.error ? result.error : text('Workflow completed'), result && result.error ? 'err' : 'ok');
  }

  function _composerSleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

  function _composerGetJSON(url) {
    if (typeof api === 'function') return api(url);
    return fetch(url).then(function (r) { return r.json(); });
  }

  // Non-blocking composer run: /api/lab/composer/run_async → poll shared /api/run_poll into a
  // progress bar → /api/run_result. Same result shape as the sync run; falls back to the
  // blocking /api/lab/composer/run if the async path is unavailable.
  async function runComposerWithProgress(manifestId) {
    var start = null;
    try { start = await request("/api/lab/composer/run_async", { manifest_id: manifestId }); }
    catch (e) { start = null; }
    if (!start || start.error || !start.job_id) {
      return await request("/api/lab/composer/run", { manifest_id: manifestId });
    }
    var id = start.job_id;
    renderComposerProgress();
    for (;;) {
      await _composerSleep(600);
      var poll = null;
      try { poll = await _composerGetJSON('/api/run_poll?id=' + encodeURIComponent(id)); }
      catch (e) { poll = null; }
      if (!poll) continue;
      if (poll.error) break;
      updateComposerProgress(poll);
      if (!poll.running) break;
    }
    for (var i = 0; i < 12; i++) {
      var r = null;
      try { r = await _composerGetJSON('/api/run_result?id=' + encodeURIComponent(id)); }
      catch (e) { r = null; }
      if (r && r.error === 'unknown_job') return { error: 'run_result_unavailable' };
      if (r && !r.running) return r;
      await _composerSleep(300);
    }
    return { error: 'run_result_timeout' };
  }

  function renderComposerProgress() {
    var el = document.getElementById('lab-composer-result');
    if (!el) return;
    clear(el);
    var wrap = make('div', 'run-prog');
    var track = make('div', 'comp-progress');
    var bar = make('div', 'comp-progress-bar indeterminate');
    bar.id = 'composer-prog-bar';
    track.appendChild(bar);
    var lbl = make('p', 'txt-dim', text('Running inference…'));
    lbl.id = 'composer-prog-label';
    wrap.appendChild(track);
    wrap.appendChild(lbl);
    el.appendChild(wrap);
  }

  function updateComposerProgress(poll) {
    var bar = document.getElementById('composer-prog-bar');
    var lbl = document.getElementById('composer-prog-label');
    if (!bar || !lbl) return;
    var elp = poll.elapsed != null ? (' · ' + poll.elapsed + 's') : '';
    if (poll.pct != null) {
      bar.classList.remove('indeterminate');
      bar.style.width = poll.pct + '%';
      var fr = poll.frames ? (' · ' + poll.frames + (poll.total ? ('/' + poll.total) : '') + ' ' + T('frames')) : '';
      lbl.textContent = poll.pct + '%' + fr + elp;
    } else {
      bar.classList.add('indeterminate');
      var f2 = poll.frames ? (poll.frames + ' ' + T('frames') + ' · ') : '';
      lbl.textContent = f2 + T('Running inference…') + elp;
    }
  }

  function downloadRecipe(recipe) {
    var blob = new Blob([JSON.stringify(recipe, null, 2) + '\n'], { type: 'application/json' });
    var url = URL.createObjectURL(blob);
    var link = document.createElement('a');
    link.href = url;
    link.download = 'workflow.recipe.json';
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 0);
  }

  async function saveRecipe() {
    if (!currentWorkflow) return;
    setStatus(composerLabels().saveRecipe, 'info');
    var result = await request('/api/lab/composer/recipe/export', {
      manifest_id: currentWorkflow.manifest_id
    });
    if (!result || result.error || !result.recipe || typeof result.recipe !== 'object') {
      renderError((result && result.error) || composerLabels().recipeExportFailed);
      return;
    }
    savedRecipe = result.recipe;
    render();
    setStatus(composerLabels().recipeSaved, 'ok');
  }

  async function exportRecipe() {
    if (!currentWorkflow) return;
    setStatus(composerLabels().exportRecipe, 'info');
    var result = await request('/api/lab/composer/recipe/export', {
      manifest_id: currentWorkflow.manifest_id
    });
    if (!result || result.error || !result.recipe || typeof result.recipe !== 'object') {
      renderError((result && result.error) || composerLabels().recipeExportFailed);
      return;
    }
    savedRecipe = result.recipe;
    downloadRecipe(savedRecipe);
    render();
    setStatus(composerLabels().recipeSaved, 'ok');
  }

  async function importRecipe(recipe) {
    setStatus(composerLabels().importRecipe, 'info');
    var result = await request('/api/lab/composer/recipe/import', { recipe: recipe });
    if (!result || result.error) {
      renderError((result && result.error) || composerLabels().recipeImportFailed);
      return;
    }
    setWorkflow(result);
  }

  async function exportPackage(packageType) {
    if (!currentWorkflow || graphValidation.blocked) {
      renderError(composerLabels().graphBlocked);
      return;
    }
    setStatus(composerLabels().exportPreflight, 'info');
    var result = await request('/api/lab/composer/export', {
      manifest_id: currentWorkflow.manifest_id,
      package_type: packageType
    });
    var output = document.getElementById('lab-composer-result');
    if (!output) return;
    var archiveUrl = result && result.download ? safeOutputUrl(result.download.url) : '';
    if (
      !result || result.error || !result.download || !archiveUrl ||
      typeof result.download.name !== 'string' || !result.download.name
    ) {
      renderError((result && result.error) || text('Package export failed'));
      return;
    }
    clear(output);
    output.appendChild(make('h3', '', text('Export Package')));
    var link = make('a', 'btn btn-acc', result.download.name);
    link.href = archiveUrl;
    link.download = result.download.name;
    output.appendChild(link);
    if (result.copy_out_verified) {
      output.appendChild(make('p', 'txt-dim txt-sm', composerLabels().copyOutVerified));
    }
    setStatus(text('Package export completed'), 'ok');
  }

  async function open() {
    await loadModels();
    loadCapabilities();
    render();
  }

  // Re-translate the Composer when the studio language changes (it renders with T()
  // at build time, so DXI18n.applyLang alone cannot swap its strings live).
  if (window.DXI18n && typeof window.DXI18n.onLangChange === 'function') {
    window.DXI18n.onLangChange(refreshComposerLanguage);
  } else {
    window._DX_I18N_CALLBACKS = window._DX_I18N_CALLBACKS || [];
    window._DX_I18N_CALLBACKS.push(refreshComposerLanguage);
  }

  return { open: open };
})();
