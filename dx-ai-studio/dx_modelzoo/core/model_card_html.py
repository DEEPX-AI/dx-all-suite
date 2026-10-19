"""Model card → one self-contained HTML page: inline CSS and JS, no request except the links a reader clicks.

Dark by default; the Theme button switches to light and remembers it (localStorage, guarded); print is light.
Contract: tests/dx_modelzoo/test_model_card_html.py, tests/dx_modelzoo/test_model_card_layout_browser.py
"""
from __future__ import annotations

import html as _html
import re

from dx_modelzoo.core.model_card import commands, fmt_delta, fmt_fps, fmt_input, fmt_num
from dx_modelzoo.core.model_card_labels import CATALOG_NUMBERS, boards_footer, boards_note, generated_note, lede, measured_note, t
from dx_modelzoo.core.model_card_md import HEADER

_DARK = ("--page:#000;--panel:#161617;--ink:#f5f5f7;--ink2:#d2d2d7;--muted:#a1a1a6;--line:#2c2c2e;"
         "--accent:#2997ff;--accent-ink:#2997ff;--soft:#0a2540;--code-bg:#0b0b0c;--good:#3fb950;--bad:#ff6b5e;"
         "color-scheme:dark")
_LIGHT = ("--page:#f5f5f7;--panel:#fff;--ink:#1d1d1f;--ink2:#424245;--muted:#6e6e73;--line:#e3e3e8;"
          "--accent:#0071e3;--accent-ink:#0066cc;--soft:#eef5fd;--code-bg:#1d1d1f;--good:#1a7f37;--bad:#c9372c;"
          "color-scheme:light")
_CSS = """
:root{%DARK%;--radius:18px;--font:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,
"Noto Sans CJK KR","Noto Sans CJK JP","Noto Sans CJK SC",sans-serif;--mono:"JetBrains Mono","SF Mono",ui-monospace,Menlo,Consolas,monospace}
:root[data-theme=light]{%LIGHT%}
@media print{:root,:root[data-theme=light]{%LIGHT%}.theme,.copy{display:none}.aside{position:static}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--page);color:var(--ink);font:15px/1.55 var(--font);-webkit-font-smoothing:antialiased}
a{color:var(--accent-ink);text-decoration:none}a:hover{text-decoration:underline}
.page{max-width:1160px;margin:0 auto;padding:clamp(20px,4vw,48px) clamp(16px,3vw,32px) 56px}
.top{display:flex;justify-content:space-between;align-items:center;gap:12px}
.crumb{font-size:13px;color:var(--muted);display:flex;flex-wrap:wrap;gap:6px 8px;align-items:center;min-width:0}
.crumb code{font:12.5px var(--mono);color:var(--ink2)}.nb{white-space:nowrap}
.theme{border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:999px;padding:5px 12px;
font:12.5px var(--font);cursor:pointer;white-space:nowrap}
.hero{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,1fr);gap:clamp(20px,3vw,40px);align-items:center;margin-top:14px}
h1{font-size:clamp(30px,4.2vw,46px);line-height:1.08;letter-spacing:-.025em;margin:0 0 12px;text-wrap:balance;overflow-wrap:anywhere}
.hero>*{min-width:0}
.lede{font-size:17px;color:var(--ink2);margin:0 0 18px;max-width:46ch;text-wrap:pretty}
.notice{font-size:13.5px;color:var(--bad);margin:0 0 14px}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 20px;padding:0;list-style:none}
.chips li{border:1px solid var(--line);background:var(--panel);border-radius:999px;padding:3px 11px;font-size:12.5px;white-space:nowrap}
.chips .q{background:var(--soft);border-color:transparent;color:var(--accent-ink);font-weight:600}
.actions{display:flex;flex-wrap:wrap;gap:10px}
.btn{display:inline-flex;align-items:center;border-radius:999px;padding:9px 18px;font-size:14px;font-weight:600;white-space:nowrap}
.btn.primary{background:var(--accent);color:#fff}.btn.ghost{border:1px solid var(--line);background:var(--panel);color:var(--ink)}
.btn:hover{text-decoration:none;filter:brightness(1.06)}
figure{margin:0}.shot{background:var(--panel);border-radius:var(--radius);padding:10px}
.shot img{display:block;width:100%;height:auto;border-radius:12px}
figcaption{font-size:12.5px;color:var(--muted);padding:8px 4px 2px;overflow-wrap:anywhere}
.kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:clamp(24px,3vw,36px) 0}
.kpi{background:var(--panel);border-radius:14px;padding:14px 16px;min-width:0}
.kpi b{display:block;font-size:clamp(22px,2.6vw,30px);letter-spacing:-.02em;font-variant-numeric:tabular-nums;white-space:nowrap}
.kpi span{display:block;font-size:12.5px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.kpi.na b{color:var(--muted);font-weight:500}
.cols{display:grid;grid-template-columns:minmax(0,1fr) 340px;gap:20px;align-items:start}.cols>*{min-width:0}
.panel{background:var(--panel);border-radius:var(--radius);padding:clamp(18px,2.4vw,26px);margin-bottom:20px;min-width:0}
.aside p{overflow-wrap:anywhere}
h2{font-size:21px;letter-spacing:-.015em;margin:0 0 4px}.sub{color:var(--muted);font-size:13.5px;margin:0 0 16px}
h3{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin:22px 0 8px;font-weight:600}
.cmd{margin:0 0 12px;background:var(--code-bg);border-radius:12px;overflow:hidden}
.cmd .bar{display:flex;justify-content:space-between;align-items:center;padding:7px 10px 7px 16px;
border-bottom:1px solid rgba(255,255,255,.08);font-size:12px;color:#a1a1a6;letter-spacing:.03em}
.cmd pre{margin:0;color:#f5f5f7;padding:12px 16px 14px;font:13px/1.6 var(--mono);overflow-x:auto;white-space:pre}
.cmd .c{color:#8e8e93}
.copy{border:0;border-radius:7px;background:rgba(255,255,255,.1);color:#f5f5f7;font:12px var(--font);padding:4px 10px;cursor:pointer}
.copy:hover{background:rgba(255,255,255,.2)}
.scroll{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:14px}
th{font-size:12px;font-weight:600;color:var(--muted);text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);white-space:nowrap;vertical-align:bottom}
td{padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}tr:last-child td{border-bottom:0}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
td.n small{display:block;font-size:12px}td.n small.neg{color:var(--bad)}td.n small.pos{color:var(--good)}
td.n small.zero{color:var(--muted)}
td.k{white-space:nowrap;font-weight:500}
.note{font-size:12.5px;color:var(--muted);margin:10px 0 0}.warn{font-size:13px;color:var(--bad);margin:10px 0 0}
.empty{color:var(--ink2);font-size:14px;margin:0 0 10px}
dl.facts{margin:0;display:grid;grid-template-columns:auto minmax(0,1fr);gap:10px 16px}
dl.facts dt{color:var(--muted);font-size:13px;white-space:nowrap}dl.facts dd{margin:0;font-size:14px;text-align:right;overflow-wrap:anywhere}
ul.dl{list-style:none;margin:0;padding:0}
ul.dl li{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:10px 0;border-bottom:1px solid var(--line)}
ul.dl li:last-child{border-bottom:0}ul.dl .t{min-width:0}ul.dl .t b{display:block;font-size:14px;white-space:nowrap}
ul.dl .t span{font-size:12px;color:var(--muted)}ul.dl .l{display:flex;gap:6px;flex-shrink:0}
ul.dl .l a{border:1px solid var(--line);border-radius:999px;padding:4px 11px;font-size:12.5px;font-weight:600;white-space:nowrap}
.files{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:2px 24px}
.files li{padding:10px 0;border-bottom:1px solid var(--line);min-width:0}
.files code,.files a{display:block;font:13px var(--mono)}.files a{font-family:var(--font);font-weight:600}
.files li>span{display:block;font-size:12.5px;color:var(--muted)}
.foot{color:var(--muted);font-size:12.5px;border-top:1px solid var(--line);margin-top:8px;padding-top:16px;line-height:1.6}
.aside{position:sticky;top:20px}
@media (max-width:1000px){.cols{grid-template-columns:1fr}.aside{position:static}.kpis{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:760px){.hero{grid-template-columns:1fr}.lede{max-width:none}}
""".replace("%DARK%", _DARK).replace("%LIGHT%", _LIGHT)
_BOOT = "try{if(localStorage.getItem('dx-card-theme')==='light')document.documentElement.dataset.theme='light'}catch(e){}"
_JS = """document.querySelector('.theme').addEventListener('click',function(){var r=document.documentElement;
var light=r.dataset.theme!=='light';if(light){r.dataset.theme='light'}else{delete r.dataset.theme}
try{localStorage.setItem('dx-card-theme',light?'light':'dark')}catch(e){}});
document.querySelectorAll('.copy').forEach(function(b){b.addEventListener('click',function(){
var text=b.closest('.cmd').querySelector('pre').innerText.split('\\n').filter(function(l){return l.charAt(0)!=='#'}).join('\\n').trim();
var done=function(){var o=b.textContent;b.textContent=b.dataset.copied;setTimeout(function(){b.textContent=o},1200)};
if(navigator.clipboard){navigator.clipboard.writeText(text).then(done,function(){})}})});"""


def _e(value):
    return _html.escape(str(value), quote=True)


def _cmd(text, label, labels):
    body = "\n".join(f"<span class=c>{_e(line)}</span>" if line.startswith("#") else _e(line)
                     for line in text.splitlines())
    return (f'<div class=cmd><div class=bar><span>{_e(label)}</span><button class=copy type=button '
            f'data-copied="{_e(t(labels, "Copied"))}">{_e(t(labels, "Copy"))}</button></div><pre>{body}</pre></div>')


def _wbr(name):
    """Break a long name only after "_" or "/": each chunk stays whole (nowrap), <wbr> marks the break points."""
    chunks = [c for c in re.split(r"(?<=[_/])", str(name)) if c]
    return "<wbr>".join(f"<span class=nb>{_e(c)}</span>" for c in chunks)


def render_html(card, *, labels=None, lang="en", image_src=None, readme_href="README.md", other_href=None,
                marker=False, performance=True):
    """marker: the exporter's "do not edit" comment (model_card_md.HEADER) right after the doctype; Studio's Save as
    HTML leaves it out, its file is not regenerated.
    performance: FPS, FPS/W and board measurements. Studio's Save as HTML shows them; the dx_app example card leaves
    them out (Studio Benchmark data, not a property of the example) and keeps accuracy."""
    L = labels or {}
    cmds = commands(card)
    acc = card["accuracy"]
    tiers = card["downloads"]["tiers"]
    onnx = card["downloads"]["onnx"]

    actions = []
    if tiers:
        actions.append(f'<a class="btn primary" href="{_e(tiers[0]["dxnn"])}">'
                       f'{_e(t(L, "Download {tier} DXNN", tier=tiers[0]["label"]))}</a>')
    if onnx:
        actions.append(f'<a class="btn ghost" href="{_e(onnx)}">ONNX</a>')
    if readme_href:
        actions.append(f'<a class="btn ghost" href="{_e(readme_href)}">README</a>')
    chips = "".join(f"<li>{_e(c)}</li>" for c in (card["task_label"], fmt_input(card["input"]),
                                                 card["dataset"], card["license"]) if c)
    chips += "".join(f"<li class=q>{_e(x['label'])}</li>" for x in tiers)
    notice = "" if card["published"] else f"<p class=notice>{_e(t(L, 'Not published in DX Model Zoo.'))}</p>"
    shot = ""
    if image_src and card["has_image"]:
        caption = t(L, "Output of the {tier} model on DX-M1 · input {sample}",
                    tier=tiers[0]["label"] if tiers else "Q-Lite", sample=card["sample"] or "—")
        shot = (f'<figure class=shot><img src="{_e(image_src)}" alt="{_e(card["name"])}" loading=lazy>'
                f"<figcaption>{_e(caption)}</figcaption></figure>")

    first = next((r for r in acc["rows"] if r["tier"] == "qlite"), None) or \
        next((r for r in acc["rows"] if r["tier"] != "raw"), None)
    first_value = first["cells"][0]["value"] if first and first["cells"] else None
    kpis = [
        (fmt_num(first_value) if first_value is not None else None,
         t(L, "{metric} · {tier}", metric=acc["metrics"][0], tier=first["label"] if first else "Q-Lite")),
        (fmt_fps(card["fps"]) if card["fps"] is not None else None, "FPS · DX-M1"),
        (fmt_num(card["fps_per_watt"], 1) if card["fps_per_watt"] is not None else None, "FPS/W · DX-M1"),
        (f"{fmt_num(card['params'])} M" if card["params"] is not None else None, t(L, "Parameters")),
    ] if performance else [
        (fmt_num(first_value) if first_value is not None else None,
         t(L, "{metric} · {tier}", metric=acc["metrics"][0], tier=first["label"] if first else "Q-Lite")),
        (fmt_input(card["input"]) or None, t(L, "Input")),
        (f"{fmt_num(card['params'])} M" if card["params"] is not None else None, t(L, "Parameters")),
        (f"{fmt_num(card['ops'])} GOPs" if card["ops"] is not None else None, t(L, "Operations")),
    ]
    kpi_html = "".join(f'<div class="kpi{"" if v else " na"}"><b>{_e(v) if v else "—"}</b><span>{_e(k)}</span></div>'
                       for v, k in kpis)

    head = "".join(f"<th class=n>{_e(m)}</th>" for m in acc["metrics"])
    body = ""
    for row in acc["rows"]:
        cells = ""
        for c in row["cells"]:
            delta = ""
            if c["delta"] is not None:
                tone = "zero" if fmt_delta(c["delta"]).startswith("±") else "neg" if c["delta"] < 0 else "pos"
                delta = f'<small class="{tone}">{_e(fmt_delta(c["delta"]))}</small>'
            cells += f"<td class=n>{_e(fmt_num(c['value']))}{delta}</td>"
        body += f"<tr><td class=k>{_e(row['label'])}</td>{cells}</tr>"
    accuracy = (f"<div class=scroll><table><thead><tr><th>{_e(t(L, 'Quantization'))}</th>{head}</tr></thead>"
                f"<tbody>{body}</tbody></table></div>") if acc["rows"] else "<p class=empty>—</p>"
    if card["dataset"] and any(c["delta"] is not None for r in acc["rows"] for c in r["cells"]):
        accuracy += f"<p class=note>{_e(t(L, '{dataset} · difference vs Raw below each value.', dataset=card['dataset']))}</p>"
    for w in acc["warnings"]:
        warning = t(L, "{tier} is {drop} points below Raw on {metric}.",
                    tier=w["tier"], drop=f"{w['drop']:.2f}", metric=w["metric"])
        accuracy += f"<p class=warn>{_e(warning)}</p>"
    if card["fps"] is not None:
        measured = measured_note(card, L)
        throughput = f"<p class=sub>{_e(measured)}</p>"
    else:
        throughput = (f"<p class=empty>{_e(t(L, 'Throughput for this model is not published yet. Measure it on your board:'))}</p>"
                      + _cmd(cmds["measure"], t(L, "Measure"), L))
    if not card["published"]:
        throughput = f"<p class=note style=\"margin:0 0 12px\">{_e(t(L, CATALOG_NUMBERS))}</p>" + throughput
    boards = ""
    if performance and card["boards"]["rows"]:
        rows = "".join(f"<tr><td class=k>{_e(r['board'])}</td><td class=n>{_e(fmt_num(r['throughput_fps'], 1))}</td>"
                       f"<td class=n>{_e(fmt_num(r['single_fps'], 1))}</td><td class=n>{_e(fmt_num(r['latency_ms'], 1))}</td></tr>"
                       for r in card["boards"]["rows"])
        boards = (f"<h3>{_e(t(L, 'Measured on host boards'))}</h3><div class=scroll><table><thead><tr>"
                  f"<th>{_e(t(L, 'Board'))}</th><th class=n>{_e(t(L, 'Throughput FPS'))}</th>"
                  f"<th class=n>{_e(t(L, 'Single-stream FPS'))}</th><th class=n>{_e(t(L, 'Latency ms'))}</th></tr></thead>"
                  f"<tbody>{rows}</tbody></table></div><p class=note>{_e(boards_note(card, L))}</p>")

    facts = [("Task", card["task_label"]), ("Dataset", card["dataset"]),
             ("Metric", " · ".join(acc["metrics"])), ("Input", fmt_input(card["input"])),
             ("Parameters", f"{fmt_num(card['params'])} M" if card["params"] is not None else None),
             ("Operations", f"{fmt_num(card['ops'])} GOPs" if card["ops"] is not None else None),
             ("Family", card["family"])]
    fact_html = "".join(f"<dt>{_e(t(L, k))}</dt><dd>{_e(v)}</dd>" for k, v in facts if v)
    dls = ""
    if onnx:
        dls += (f"<li><div class=t><b>ONNX</b><span>{_e(t(L, 'original model'))}</span></div>"
                f'<div class=l><a href="{_e(onnx)}">ONNX</a></div></li>')
    for x in tiers:
        json_link = f'<a href="{_e(x["json"])}">JSON</a>' if x["json"] else ""
        dls += (f"<li><div class=t><b>{_e(x['label'])}</b><span>DX-COM {_e(x['compiler'] or '—')}</span></div>"
                f'<div class=l><a href="{_e(x["dxnn"])}">DXNN</a>{json_link}</div></li>')
    manifest = card["downloads"].get("manifest")
    if manifest:
        dls += (f"<li><div class=t><b>{_e(t(L, 'DXNN (dx_app manifest)'))}</b>"
                f"<span>DX-COM {_e(manifest['compiler'] or '—')}</span></div>"
                f'<div class=l><a href="{_e(manifest["dxnn"])}">DXNN</a></div></li>')
    dls = f"<ul class=dl>{dls}</ul>" if dls else "<p class=empty>—</p>"
    files = "".join(f"<li><code>{_wbr(f['name'])}</code><span>{_e(t(L, f['role']))}</span></li>"
                    for f in card["files"]["python"])
    if other_href and card["has_cpp"]:
        files += (f'<li><a href="{_e(other_href)}">{_e(t(L, "C++ version of this example"))} →</a>'
                  f"<span>{_wbr(card['paths']['cpp'] + '/')}</span></li>")
    files = f"<ul class=files>{files}</ul>" if files else "<p class=empty>—</p>"
    license_text = (f"<p class=sub style=\"margin:0 0 8px\">{_e(card['license_text'])}</p>"
                    if card["license_text"] and card["license_text"] != card["license"] else "")
    footer = "\n".join(_e(x) for x in (generated_note(card, L), boards_footer(card, L) if performance else None) if x)
    source = (f'<a href="{_e(card["source"])}">{_e(card["source"].replace("https://github.com/", ""))}</a>'
              if card["source"] else "—")
    owner = f" · © {_e(card['copyright'])}" if card["copyright"] else ""

    if performance:
        perf_section = (f"<section class=panel><h2>{_e(t(L, 'Performance'))}</h2>{throughput}"
                        f"<h3>{_e(t(L, 'Accuracy'))}</h3>{accuracy}{boards}</section>")
    else:
        catalog = (f"<p class=note style=\"margin:0 0 12px\">{_e(t(L, CATALOG_NUMBERS))}</p>"
                   if not card["published"] else "")
        perf_section = f"<section class=panel><h2>{_e(t(L, 'Accuracy'))}</h2>{catalog}{accuracy}</section>"
    return f"""<!doctype html>
{HEADER if marker else ""}<html lang="{_e(lang)}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_e(card['name'])} · {_e(t(L, 'DX-APP example'))}</title>
<script>{_BOOT}</script><style>{_CSS}</style></head>
<body><div class=page>
<div class=top><div class=crumb><span>{_e(t(L, 'DX-APP example'))}</span><span>·</span><span>{_e(card['task_label'])}</span>
<span>·</span><code>{_wbr(card['variant'])}</code></div><button class=theme type=button>{_e(t(L, 'Theme'))}</button></div>
<section class=hero><div><h1>{_e(card['name']).replace('_', '_<wbr>')}</h1><p class=lede>{_e(lede(card, L))}</p>{notice}
<ul class=chips>{chips}</ul><div class=actions>{''.join(actions)}</div></div>{shot}</section>
<div class=kpis>{kpi_html}</div>
<div class=cols><main>
<section class=panel><h2>{_e(t(L, 'Quick start'))}</h2>
<p class=sub>{_e(t(L, 'Run from the dx_app root after ./install.sh and ./build.sh.'))}</p>
{_cmd(cmds['get'], t(L, 'Get the model'), L)}{_cmd(cmds['python'], 'Python', L)}{_cmd(cmds['cpp'], 'C++', L)}</section>
{perf_section}
<section class=panel><h2>{_e(t(L, 'Files in this example'))}</h2>{files}</section>
</main><aside class=aside>
<section class=panel><h2>{_e(t(L, 'Model'))}</h2><dl class=facts>{fact_html}</dl></section>
<section class=panel><h2>{_e(t(L, 'Downloads'))}</h2>{dls}</section>
<section class=panel><h2>{_e(t(L, 'Source & License'))}</h2><p style="margin:0 0 6px">{source}</p>
<p class=sub style="margin:0 0 8px">{_e(card['license'] or '—')}{owner} — {_e(t(L, 'Check the upstream license before commercial use.'))}</p>
{license_text}
<p class=sub style="margin:0">{_e(t(L, 'Compile it yourself: DX-COM in dx-compiler, or DX AI Studio → Compiler.'))}</p></section>
</aside></div>
<p class=foot>{footer}
{_e(t(L, 'Open this model in DX AI Studio → Model Zoo for live inference and the model graph.'))}</p>
</div><script>{_JS}</script></body></html>
"""
