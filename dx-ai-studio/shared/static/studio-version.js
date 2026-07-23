/**
 * DX AI Studio release identity (single source of truth).
 * Bump semver here for beta/RC/stable releases.
 */
(function (global) {
  'use strict';

  var VERSION = {
    channel: 'beta',
    label: 'Beta version',
    semver: '0.1.0',
  };

  function badgeText() {
    return 'BETA · v' + VERSION.semver;
  }

  function displayText() {
    return VERSION.label + ' · v' + VERSION.semver;
  }

  function titleSuffix() {
    return ' (Beta v' + VERSION.semver + ')';
  }

  function applyStudioVersion(root) {
    root = root || document;
    var baseTitle = (document.title || 'DEEPX AI Studio')
      .replace(/\s*\(Beta v[^)]*\)\s*$/, '')
      .trim();
    document.title = baseTitle + titleSuffix();

    var badge = root.getElementById('studioBetaBadge');
    if (badge) badge.textContent = badgeText();

    var hub = root.getElementById('studioVersionHub');
    if (hub) hub.textContent = displayText();

    var footer = root.getElementById('studioVersionFooter');
    if (footer) footer.textContent = displayText();
  }

  global.DXStudioVersion = {
    VERSION: VERSION,
    badgeText: badgeText,
    displayText: displayText,
    titleSuffix: titleSuffix,
    apply: applyStudioVersion,
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      applyStudioVersion();
    });
  } else {
    applyStudioVersion();
  }
})(typeof window !== 'undefined' ? window : globalThis);
