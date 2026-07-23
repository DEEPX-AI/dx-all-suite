/**
 * DX Agent Dev — assistant markdown → HTML (GFM-lite + Mermaid + spec mode)
 * Used by console.js; exported as window.DXMarkdownRender for tests.
 */
(function (global) {
  'use strict';

  var MERMAID_START = /^(flowchart|graph|sequenceDiagram|classDiagram|stateDiagram-v2|stateDiagram|erDiagram|gantt|pie|gitGraph|journey|C4Context|mindmap|timeline|sankey-beta|block-beta)/i;

  function escapeHtml(text) {
    if (typeof document !== 'undefined' && document.createElement) {
      var div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    }
    return String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  /** Close dangling ```; insert early before prose/tables when possible. */
  function repairCodeFences(text) {
    if (!text) return '';
    var count = (text.match(/```/g) || []).length;
    if (count % 2 === 0) return text;

    var lastOpen = text.lastIndexOf('```');
    var afterOpen = text.slice(lastOpen + 3);
    var breakPatterns = [
      /\n(\|[^\n]+\|)/,
      /\n#{1,3} /,
      /\n---[ \t]*\r?\n/,
      /\n\n-\s+\*\*/,
      /\n-\s+\*\*/,
      /\n\n\*\*[^*]+\*\*/,
      /\n\*\*[^*]+\*\*/,
    ];
    var breakAt = -1;
    breakPatterns.forEach(function (pat) {
      var m = afterOpen.match(pat);
      if (m && m.index != null && (breakAt < 0 || m.index < breakAt)) breakAt = m.index;
    });
    if (breakAt >= 0) {
      var insert = lastOpen + 3 + breakAt;
      return text.slice(0, insert) + '\n```' + text.slice(insert);
    }
    return text + '\n```';
  }

  /** Wrap bare `mermaid` + flowchart blocks when agents omit fences. */
  function normalizeBareMermaid(text) {
    if (!text || /```\s*mermaid/i.test(text)) return text;
    var out = text.replace(
      /(?:^|\n)mermaid[ \t]*\r?\n([\s\S]*?)(?=\r?\n\r?\n|\r?\n---[ \t]*\r?\n|\r?\n#{1,3} |\r?\n\|[^\n]+\||$)/g,
      function (full, body) {
        var trimmed = (body || '').trim();
        if (!trimmed || !MERMAID_START.test(trimmed)) return full;
        return '\n\n```mermaid\n' + trimmed + '\n```\n';
      }
    );
    return out;
  }

  function isSpecContent(text) {
    if (!text) return false;
    if (text.length > 1800) return true;
    if ((text.match(/^## /gm) || []).length >= 2) return true;
    if ((text.match(/^### /gm) || []).length >= 4) return true;
    if ((text.match(/\|[^\n]+\|/g) || []).length >= 4) return true;
    if (/```mermaid|^mermaid[ \t]*\r?\n/m.test(text)) return true;
    return false;
  }

  function preserveBlock(preserved, block) {
    var token = '\x00PH' + preserved.length + '\x00';
    preserved.push(block);
    return token;
  }

  function renderCodeBlock(lang, code, preserved, mermaidErrorLabel) {
    var trimmed = (code || '').trim();
    var langLower = (lang || '').toLowerCase();
    if (langLower === 'mermaid') {
      if (!trimmed || /^Syntax error/i.test(trimmed)) {
        return preserveBlock(preserved, '<pre class="mermaid-error">' + escapeHtml(mermaidErrorLabel || 'Diagram could not be rendered.') + '</pre>');
      }
      return preserveBlock(preserved, '<pre class="mermaid-source"><code>' + trimmed + '</code></pre>');
    }
    var firstLine = trimmed.split('\n')[0] || '';
    if (/^\d+:\d+:/.test(firstLine)) {
      var rest = trimmed.slice(firstLine.length).replace(/^\r?\n/, '');
      return preserveBlock(
        preserved,
        '<pre class="code-citation"><div class="citation-meta">' + escapeHtml(firstLine) + '</div><code>' + rest + '</code></pre>'
      );
    }
    return preserveBlock(preserved, '<pre class="code-block"><code>' + trimmed + '</code></pre>');
  }

  function parsePipeTable(block) {
    var rows = block.trim().split(/\r?\n/).filter(function (r) { return r.trim(); });
    if (rows.length < 1) return null;
    var pipeRows = rows.filter(function (r) { return /^\|.+\|$/.test(r.trim()); });
    if (pipeRows.length < 2) return null;

    var hasSep = pipeRows.length > 1 && /^\|[\s\-:|]+\|$/.test(pipeRows[1].trim());
    var html = '<div class="md-table-wrap"><table class="md-table">';
    pipeRows.forEach(function (row, i) {
      if (hasSep && i === 1) return;
      var cells = row.split('|').filter(function (_c, ci, arr) { return ci > 0 && ci < arr.length - 1; });
      var isHead = hasSep ? i === 0 : i === 0 && pipeRows.length > 1;
      var tag = isHead ? 'th' : 'td';
      html += '<tr>' + cells.map(function (c) { return '<' + tag + '>' + c.trim() + '</' + tag + '>'; }).join('') + '</tr>';
    });
    html += '</table></div>';
    return html;
  }

  function parseTabTable(block) {
    var rows = block.trim().split(/\r?\n/).filter(function (r) { return r.indexOf('\t') >= 0; });
    if (rows.length < 2) return null;
    var html = '<div class="md-table-wrap"><table class="md-table">';
    rows.forEach(function (row, i) {
      var cells = row.split('\t').map(function (c) { return c.trim(); });
      var tag = i === 0 ? 'th' : 'td';
      html += '<tr>' + cells.map(function (c) { return '<' + tag + '>' + c + '</' + tag + '>'; }).join('') + '</tr>';
    });
    html += '</table></div>';
    return html;
  }

  function renderMarkdown(body, opts) {
    opts = opts || {};
    if (!body) return '';

    var preserved = [];
    var html = escapeHtml(body);

    html = html.replace(/```(\w*)[ \t]*\r?\n([\s\S]*?)```/g, function (_, lang, code) {
      return renderCodeBlock(lang, code, preserved, opts.mermaidErrorLabel);
    });

    html = html.replace(/`([^`\n]+)`/g, '<code class="md-inline-code">$1</code>');
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, function (_, label, url) {
      var safeUrl = escapeHtml(url).replace(/"/g, '&quot;');
      return '<a class="md-link" href="' + safeUrl + '" target="_blank" rel="noopener noreferrer">' + label + '</a>';
    });

    html = html.replace(/^#### (.+)$/gm, '<h5 class="md-h5">$1</h5>');
    html = html.replace(/^### (.+)$/gm, '<h4 class="md-h4">$1</h4>');
    html = html.replace(/^## (.+)$/gm, '<h3 class="md-h3">$1</h3>');
    html = html.replace(/^# (.+)$/gm, '<h2 class="md-h2">$1</h2>');
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>');

    html = html.replace(/^([-*_]){3,}[ \t]*$/gm, function () {
      return preserveBlock(preserved, '<hr class="md-hr">');
    });

    html = html.replace(/((?:\|[^\n]+\|\r?\n?)+)/g, function (block) {
      var table = parsePipeTable(block);
      return table ? preserveBlock(preserved, table) : block;
    });

    html = html.replace(/((?:[^\n<]*\t[^\n<]+\r?\n?){2,})/g, function (block) {
      if (block.indexOf('|') >= 0 && block.indexOf('\t') < 0) return block;
      var table = parseTabTable(block);
      return table ? preserveBlock(preserved, table) : block;
    });

    html = html.replace(/(?:^|\n)((?:[-*] [^\n]+\r?\n?)+)/g, function (block) {
      var items = block.trim().split(/\r?\n/);
      return '<ul class="md-list">' + items.map(function (item) {
        return '<li>' + item.replace(/^[-*] /, '') + '</li>';
      }).join('') + '</ul>';
    });

    html = html.replace(/(?:^|\n)((?:\d+\. [^\n]+\r?\n?)+)/g, function (block) {
      var items = block.trim().split(/\r?\n/);
      return '<ol class="md-list md-list-ol">' + items.map(function (item) {
        return '<li>' + item.replace(/^\d+\. /, '') + '</li>';
      }).join('') + '</ol>';
    });

    html = html.replace(/\r?\n/g, '<br>');
    preserved.forEach(function (block, i) {
      html = html.split('\x00PH' + i + '\x00').join(block);
    });
    return html;
  }

  global.DXMarkdownRender = {
    repairCodeFences: repairCodeFences,
    normalizeBareMermaid: normalizeBareMermaid,
    isSpecContent: isSpecContent,
    render: renderMarkdown,
    escapeHtml: escapeHtml,
  };
})(typeof window !== 'undefined' ? window : globalThis);
