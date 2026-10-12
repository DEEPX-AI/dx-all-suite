"""Build shared/static/dx-icons.svg, the source of the studio icon set.

24px grid, two layers: a faint fill (g.f) and a 2px line (g.l), coloured with currentColor.
S[name] = (fill elements, line elements). Icons that read from lines alone leave the fill empty.

    python -m scripts.build_icon_sprite

Contract: tests/shared/test_icon_system.py · tests/shared/test_task_icons.py
"""
import math
F = 'fill: currentColor; fill-opacity: var(--ico-fill, .24); opacity: var(--ico-fill-o, 1); stroke: none'
L = 'fill: none; stroke: currentColor; stroke-width: var(--ico-stroke, 2); stroke-linecap: round; stroke-linejoin: round'
def R(x, y, w, h, rx): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/>'
def P(d): return f'<path d="{d}"/>'
def C(cx, cy, r): return f'<circle cx="{cx}" cy="{cy}" r="{r}"/>'

def gear():
    pts = []
    teeth, ro, ri = 8, 9.2, 7.0
    for i in range(teeth * 4):
        a = (i / (teeth * 4)) * 2 * math.pi - math.pi / 2
        r = ro if (i % 4) in (1, 2) else ri
        pts.append((12 + r * math.cos(a), 12 + r * math.sin(a)))
    return 'M' + 'L'.join(f'{x:.2f} {y:.2f}' for x, y in pts) + 'z'

G = gear()
S = {}
# ── The 8 modules (same glyphs as the launcher home) ──
S['app'] = ([R(3, 4, 18, 13, 2.5)], [R(3, 4, 18, 13, 2.5), P('M10.5 8.2v4.6l4-2.3z'), P('M8 20.5h8')])
S['stream'] = ([R(7.5, 3.5, 13, 10, 2)], [R(7.5, 3.5, 13, 10, 2), P('M3.5 8v8.5a2 2 0 0 0 2 2H16'), P('M12.5 6.6l3.2 1.9-3.2 1.9z')])
S['zoo'] = ([R(13.5, 3.5, 7, 7, 2)], [R(3.5, 3.5, 7, 7, 2), R(13.5, 3.5, 7, 7, 2), R(3.5, 13.5, 7, 7, 2), R(13.5, 13.5, 7, 7, 2)])
S['compiler'] = ([R(6, 6, 12, 12, 2.5)], [R(6, 6, 12, 12, 2.5), P('M9.5 2.5V6M14.5 2.5V6M9.5 18v3.5M14.5 18v3.5M2.5 9.5H6M2.5 14.5H6M18 9.5h3.5M18 14.5h3.5'), P('M12 9v5M9.8 11.8 12 14l2.2-2.2')])
S['bench'] = ([P('M4 16a8 8 0 0 1 16 0z')], [P('M4 16a8 8 0 0 1 16 0'), P('M12 16l4.2-4.6'), C(12, 16, 1.4), P('M3 19.5h18')])
S['edge'] = ([C(12, 12, 9)], [C(12, 12, 9), P('M15.6 8.4l-2.3 4.9-4.9 2.3 2.3-4.9z')])
S['monitor'] = ([R(3, 4, 18, 16, 3)], [R(3, 4, 18, 16, 3), P('M6 12.5h3l1.8-4 2.6 8 1.8-4H18')])
S['agent'] = ([R(3, 5.5, 18, 14, 3)], [R(3, 5.5, 18, 14, 3), P('M7 10.5l2.5 2L7 14.5'), P('M12 15h4'), P('M18.5 1.8v2.8M17.1 3.2h2.8')])
# ── Books ──
S['library'] = ([R(5.2, 5, 6.6, 14.5, 1)], [P('M6.5 5v14M10.5 5v14'), P('M14 5.6l3.4 13'), P('M4.5 19.5h15')])
OPEN_BOOK = 'M12 7.2c-2-1.5-5-1.6-7.5-.6v11.2c2.5-1 5.5-.9 7.5.6 2-1.5 5-1.6 7.5-.6V6.6c-2.5-1-5.5-.9-7.5.6z'
S['book'] = ([P(OPEN_BOOK)], [P(OPEN_BOOK + 'M12 7.2v11.2')])
# ── Pages · tools (names used by the rail and tabs) ──
HOUSE = 'M4 10.8 12 4l8 6.8v8.7a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 4 19.5z'
S['home'] = ([P(HOUSE)], [P(HOUSE), P('M10 21v-5.5h4V21')])
S['setup'] = ([C(15, 7, 2.2), C(9, 12, 2.2), C(16, 17, 2.2)],
              [P('M4 7h8.8M17.2 7H20M4 12h2.8M11.2 12H20M4 17h9.8M18.2 17H20'), C(15, 7, 2.2), C(9, 12, 2.2), C(16, 17, 2.2)])
CUBE = 'M12 3l8 4.5v9L12 21l-8-4.5v-9z'
S['models'] = ([P(CUBE)], [P(CUBE), P('M4 7.5l8 4.5 8-4.5M12 12v9')])
S['run'] = ([C(12, 12, 9)], [C(12, 12, 9), P('M10 8.5v7l5.5-3.5z')])
S['demo'] = ([R(3, 9, 18, 11, 2)], [R(3, 9, 18, 11, 2), P('M3.5 9 5 4.5h15.5L19 9'), P('M9.5 4.5 8 9M15 4.5 13.5 9')])
S['compare'] = ([R(3, 4, 8, 16, 2)], [R(3, 4, 8, 16, 2), R(13, 4, 8, 16, 2), P('M15.5 9h3M15.5 12h3M5.5 9h3')])
TRAY = 'M5 15h14v3.5a1.5 1.5 0 0 1-1.5 1.5h-11A1.5 1.5 0 0 1 5 18.5z'
S['download'] = ([P(TRAY)], [P('M12 4v10M8 10l4 4 4-4'), P('M5 15v3.5a1.5 1.5 0 0 0 1.5 1.5h11a1.5 1.5 0 0 0 1.5-1.5V15')])
S['upload'] = ([P(TRAY)], [P('M12 14V4M8 8l4-4 4 4'), P('M5 15v3.5a1.5 1.5 0 0 0 1.5 1.5h11a1.5 1.5 0 0 0 1.5-1.5V15')])
FLASK = 'M9.5 3.5v5.2L4.6 17.6A2 2 0 0 0 6.3 20.5h11.4a2 2 0 0 0 1.7-2.9L14.5 8.7V3.5'
S['lab'] = ([P('M7.3 13.5h9.4l2.7 4.1a2 2 0 0 1-1.7 2.9H6.3a2 2 0 0 1-1.7-2.9z')], [P(FLASK), P('M8.5 3.5h7'), P('M7.3 13.5h9.4')])
FOLDER = 'M3 7.5A1.5 1.5 0 0 1 4.5 6h4.8l2 2h8.2A1.5 1.5 0 0 1 21 9.5v8a1.5 1.5 0 0 1-1.5 1.5h-15A1.5 1.5 0 0 1 3 17.5z'
S['folder'] = ([P(FOLDER)], [P(FOLDER)])
S['dev'] = ([R(3, 4, 18, 16, 3)], [R(3, 4, 18, 16, 3), P('M9 9.5 6.5 12 9 14.5M15 9.5l2.5 2.5-2.5 2.5M13 8.5l-2 7')])
S['chev'] = ([], [P('M9 6l6 6-6 6')])
S['chevd'] = ([], [P('M6 9l6 6 6-6')])
S['dots'] = ([], [C(6, 12, .9), C(12, 12, .9), C(18, 12, .9)])
S['dashboard'] = ([R(3, 3, 8, 10, 2)], [R(3, 3, 8, 10, 2), R(13, 3, 8, 6, 2), R(13, 11, 8, 10, 2), R(3, 15, 8, 6, 2)])
PIECE = 'M5 5h5a2 2 0 1 1 4 0h5v5a2 2 0 1 1 0 4v5h-5a2 2 0 1 0-4 0H5v-5a2 2 0 1 0 0-4z'
S['puzzle'] = ([P(PIECE)], [P(PIECE)])
SPANNER = 'M15.5 3.5a5 5 0 0 0-4.7 6.6l-6.5 6.5a2 2 0 0 0 2.8 2.8l6.5-6.5a5 5 0 0 0 6.6-4.7L17.4 10.9l-3-.5-.5-3 2.8-2.8a5 5 0 0 0-1.2-.1z'
S['wrench'] = ([P(SPANNER)], [P(SPANNER)])
# ── General UI marks ──
MERIDIAN = 'M12 3c2.5 2.6 3.5 5.6 3.5 9s-1 6.4-3.5 9c-2.5-2.6-3.5-5.6-3.5-9s1-6.4 3.5-9z'
S['globe'] = ([C(12, 12, 9)], [C(12, 12, 9), P('M3 12h18'), P(MERIDIAN)])
S['theme'] = ([P('M12 3a9 9 0 0 1 0 18z')], [C(12, 12, 9), P('M12 3v18')])
CAP = 'M12 5 2.5 9.5 12 14l9.5-4.5z'
S['graduation'] = ([P(CAP)], [P(CAP), P('M6.5 11.8V16c0 1.4 2.5 3 5.5 3s5.5-1.6 5.5-3v-4.2'), P('M21.5 9.5V15')])
S['gear'] = ([P(G)], [P(G), C(12, 12, 3)])
S['check'] = ([], [P('M5 12.5l4.5 4.5L19 7.5')])
TRI = 'M10.3 4.2a2 2 0 0 1 3.4 0l7.6 13.1a2 2 0 0 1-1.7 3H4.4a2 2 0 0 1-1.7-3z'
S['alert'] = ([P(TRI)], [P(TRI), P('M12 9.5v4.5'), P('M12 17.2v.1')])
S['x'] = ([], [P('M6 6l12 12M18 6 6 18')])
S['info'] = ([C(12, 12, 9)], [C(12, 12, 9), P('M12 11v5.5'), P('M12 7.8v.1')])
S['spinner'] = ([], [P('M12 3a9 9 0 1 0 9 9')])
S['lock'] = ([R(5, 10.5, 14, 10, 2)], [R(5, 10.5, 14, 10, 2), P('M8 10.5V7.5a4 4 0 0 1 8 0v3'), P('M12 14.5v2')])
BIN = 'M6 7h12l-1 12.2A1.8 1.8 0 0 1 15.2 21H8.8A1.8 1.8 0 0 1 7 19.2z'
S['trash'] = ([P(BIN)], [P(BIN), P('M4 7h16'), P('M9.5 7V4.5h5V7'), P('M10 11v6M14 11v6')])
BUBBLE = 'M4 5.5A1.5 1.5 0 0 1 5.5 4h13A1.5 1.5 0 0 1 20 5.5v9a1.5 1.5 0 0 1-1.5 1.5H10l-4.5 4v-4A1.5 1.5 0 0 1 4 14.5z'
S['chat'] = ([P(BUBBLE)], [P(BUBBLE), P('M8 9h8M8 12h5')])
S['send'] = ([], [P('M4 12 20 4l-4 16-4-7z'), P('M12 13l8-9')])
S['play'] = ([P('M8 5.5v13l10-6.5z')], [P('M8 5.5v13l10-6.5z')])
S['stop'] = ([R(6, 6, 12, 12, 2)], [R(6, 6, 12, 12, 2)])
S['refresh'] = ([], [P('M20 12a8 8 0 1 1-2.3-5.7'), P('M20 4v4.5h-4.5')])
S['search'] = ([], [C(10.5, 10.5, 6.5), P('M15.5 15.5 20 20')])
S['image'] = ([R(3, 4.5, 18, 15, 2.5)], [R(3, 4.5, 18, 15, 2.5), P('M3.5 16l5-5 4 4 2.5-2.5 5.5 5.5'), C(15.5, 9, 1.6)])
S['video'] = ([R(3, 6, 13, 12, 2.5)], [R(3, 6, 13, 12, 2.5), P('M16 10.5l5-3v9l-5-3z')])
CAM = 'M4 8.5A1.5 1.5 0 0 1 5.5 7h2.3l1.4-2.2h5.6L16.2 7h2.3A1.5 1.5 0 0 1 20 8.5v9a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 4 17.5z'
S['camera'] = ([P(CAM)], [P(CAM), C(12, 13, 3.5)])
PAGE = 'M13.5 3H7a1.5 1.5 0 0 0-1.5 1.5v15A1.5 1.5 0 0 0 7 21h10a1.5 1.5 0 0 0 1.5-1.5V8z'
S['file'] = ([P(PAGE)], [P(PAGE), P('M13.5 3v5h5'), P('M9 13h6M9 16.5h6')])
S['clipboard'] = ([R(5, 5, 14, 16, 2)], [R(5, 5, 14, 16, 2), R(9, 3, 6, 4, 1), P('M9 11h6M9 15h4')])
S['copy'] = ([R(8, 8, 12, 12, 2)], [R(8, 8, 12, 12, 2), P('M16 8V5.5A1.5 1.5 0 0 0 14.5 4h-9A1.5 1.5 0 0 0 4 5.5v9A1.5 1.5 0 0 0 5.5 16H8')])
EYE = 'M2.5 12s3.5-6.5 9.5-6.5 9.5 6.5 9.5 6.5-3.5 6.5-9.5 6.5S2.5 12 2.5 12z'
S['eye'] = ([P(EYE)], [P(EYE), C(12, 12, 3)])
S['external'] = ([], [P('M14 4h6v6'), P('M20 4l-9 9'), P('M18 14v4.5a1.5 1.5 0 0 1-1.5 1.5h-11A1.5 1.5 0 0 1 4 18.5v-11A1.5 1.5 0 0 1 5.5 6H10')])

# ── Shared chrome ──
RAYS = 'M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M5.3 18.7l1.4-1.4M17.3 6.7l1.4-1.4'
S['sun'] = ([C(12, 12, 4.2)], [C(12, 12, 4.2), P(RAYS)])
MOON = 'M20 14.2A8.2 8.2 0 1 1 9.8 4a6.6 6.6 0 0 0 10.2 10.2z'
S['moon'] = ([P(MOON)], [P(MOON)])
S['circle'] = ([], [C(12, 12, 7.5)])
S['menu'] = ([], [P('M4 7h16M4 12h16M4 17h16')])
BULB = 'M10 4.5a2 2 0 0 1 4 0v8.3a4.5 4.5 0 1 1-4 0z'
S['thermometer'] = ([C(12, 16.8, 2.4)], [P(BULB), P('M12 9v7')])
BOLT = 'M13 2.5 5 13.5h6l-1 8 8-11h-6z'
S['bolt'] = ([P(BOLT)], [P(BOLT)])
S['cpu'] = ([R(7, 7, 10, 10, 2)], [R(4.5, 4.5, 15, 15, 3), R(9, 9, 6, 6, 1), P('M9 2v2.5M15 2v2.5M9 19.5V22M15 19.5V22M2 9h2.5M2 15h2.5M19.5 9H22M19.5 15H22')])
S['memory'] = ([R(3, 7, 18, 9, 2)], [R(3, 7, 18, 9, 2), P('M7 10.5v2M10.5 10.5v2M14 10.5v2M17.5 10.5v2'), P('M6 16v2.5M10 16v2.5M14 16v2.5M18 16v2.5')])
S['disk'] = ([C(12, 12, 9)], [C(12, 12, 9), C(12, 12, 2.5), P('M15.5 6.5a7 7 0 0 1 2.2 2.8')])
S['clock'] = ([C(12, 12, 9)], [C(12, 12, 9), P('M12 7v5l3.2 2')])

# ── Tasks (icon = "task-<key>" in dx_modelzoo/core/config.py CATEGORIES) ──
CORNERS = 'M3 8V4.5A1.5 1.5 0 0 1 4.5 3H8M16 3h3.5A1.5 1.5 0 0 1 21 4.5V8M21 16v3.5a1.5 1.5 0 0 1-1.5 1.5H16M8 21H4.5A1.5 1.5 0 0 1 3 19.5V16'
S['task-object_detection'] = ([R(7.5, 7.5, 9, 9, 1.5)], [P(CORNERS), R(7.5, 7.5, 9, 9, 1.5)])
TAG = 'M3.5 11.6V5a1.5 1.5 0 0 1 1.5-1.5h6.6l8.6 8.6a1.5 1.5 0 0 1 0 2.1l-6.2 6.2a1.5 1.5 0 0 1-2.1 0z'
S['task-classification'] = ([P(TAG)], [P(TAG), C(8.5, 8.5, 1.5)])
S['task-ppu'] = ([R(6, 6, 12, 12, 2.5)], [R(6, 6, 12, 12, 2.5), P('M9.5 2.5V6M14.5 2.5V6M9.5 18v3.5M14.5 18v3.5M2.5 9.5H6M2.5 14.5H6M18 9.5h3.5M18 14.5h3.5'), P('M9.5 10h5M10.5 12.5h3M11.5 15h1')])
S['task-instance_segmentation'] = ([P('M4 14a5.5 5.5 0 0 1 11 0v3.5A2.5 2.5 0 0 1 12.5 20h-6A2.5 2.5 0 0 1 4 17.5z')],
    [P('M4 14a5.5 5.5 0 0 1 11 0v3.5A2.5 2.5 0 0 1 12.5 20h-6A2.5 2.5 0 0 1 4 17.5z'), C(15.5, 8.5, 5)])
FRAME = R(3, 4, 18, 16, 2.5)
S['task-semantic_segmentation'] = ([P('M3 14.5c3.5-.5 5.5-5 9-5s5.5 3 9 2.5v6a2.5 2.5 0 0 1-2.5 2.5h-13A2.5 2.5 0 0 1 3 17.5z')],
    [FRAME, P('M3 14.5c3.5-.5 5.5-5 9-5s5.5 3 9 2.5'), P('M12 9.5V20')])
S['task-face_detection'] = ([C(12, 12, 5)], [P(CORNERS), C(12, 12, 5), P('M10 13.6c1.2.9 2.8.9 4 0'), P('M10.2 10.6v.1M13.8 10.6v.1')])
S['task-pose_estimation'] = ([C(12, 4.8, 2)], [C(12, 4.8, 2), P('M5.5 10l6.5-1.5 6.5 1.5'), P('M12 8.5v5.5'), P('M8 21l4-7 4 7')])
S['task-image_denoising'] = ([P('M12 4h6.5A2.5 2.5 0 0 1 21 6.5v11a2.5 2.5 0 0 1-2.5 2.5H12z')],
    [FRAME, P('M12 4v16'), P('M6.5 8v.1M9 11v.1M6 13.5v.1M8.5 16.5v.1')])
OBB = 'M3.5 11.5 13.5 4l7 9.5-10 7.5z'
S['task-obb_detection'] = ([P(OBB)], [P(OBB), C(3.5, 11.5, .6), C(13.5, 4, .6), C(20.5, 13.5, .6), C(10.5, 21, .6)])
S['task-reid'] = ([C(7.5, 8, 2.8), P('M2.5 19a5 5 0 0 1 10 0z')],
    [C(7.5, 8, 2.8), P('M2.5 19a5 5 0 0 1 10 0'), C(16.5, 8, 2.8), P('M11.5 19a5 5 0 0 1 10 0')])
S['task-embedding'] = ([C(8.5, 14.5, 1.8), C(13, 8.5, 1.8), C(18, 12, 1.8)],
    [P('M3.5 3.5v17h17'), C(8.5, 14.5, 1.8), C(13, 8.5, 1.8), C(18, 12, 1.8), P('M9.6 13.1l2.3-3.1M14.5 9.6l2 1.4')])
S['task-attribute_recognition'] = ([P('M15 10.5h4l2 2.5-2 2.5h-4z')],
    [C(8.5, 7.5, 3), P('M3 19.5a5.5 5.5 0 0 1 11 0'), P('M15 10.5h4l2 2.5-2 2.5h-4z')])
S['task-super_resolution'] = ([R(11, 3, 10, 10, 2)], [R(3, 15, 6, 6, 1.5), R(11, 3, 10, 10, 2), P('M7 13l4.5-4.5'), P('M8 8.5h3.5V12')])
S['task-face_alignment'] = ([C(12, 12, 8.5)], [C(12, 12, 8.5), C(9, 10, .5), C(15, 10, .5), C(12, 13, .5), C(9.5, 16, .5), C(14.5, 16, .5)])
LAYER = 'M12 3.5 21 8l-9 4.5L3 8z'
S['task-depth_estimation'] = ([P(LAYER)], [P(LAYER), P('M3 12.5l9 4.5 9-4.5'), P('M3 17l9 4.5 9-4.5')])
S['task-image_enhancement'] = ([R(3, 7, 14, 14, 2.5)], [R(3, 7, 14, 14, 2.5), P('M3.5 18l4-4 3 3 2-2 4 4'), P('M19.5 2v5M17 4.5h5')])
HAND = ('M7 12.5V7a1.5 1.5 0 0 1 3 0v4.5V5a1.5 1.5 0 0 1 3 0v6.5V6a1.5 1.5 0 0 1 3 0v6.5V9a1.5 1.5 0 0 1 3 0v5.5'
        'a7 7 0 0 1-7 7h-.5a7 7 0 0 1-5.8-3.1l-2.3-3.4a1.5 1.5 0 0 1 2.4-1.8L7 14.5z')
S['task-hand_landmark'] = ([P(HAND)], [P(HAND), C(8.5, 9.5, .5), C(11.5, 8, .5), C(14.5, 8.5, .5), C(17.5, 11.5, .5)])
def T(d, t):
    return f'<path d="{d}" transform="{t}" vector-effect="non-scaling-stroke"/>'
S['task-hand_detection'] = ([T(HAND, 'translate(4.2 4) scale(.66)')], [P(CORNERS), T(HAND, 'translate(4.2 4) scale(.66)')])
PIN = 'M12 21.5s-6.5-5.7-6.5-11.2a6.5 6.5 0 0 1 13 0c0 5.5-6.5 11.2-6.5 11.2z'
S['task-keypoint_detection'] = ([P(PIN)], [P(PIN), C(12, 10.3, 2.3)])
BOX = 'M14 5.5l5 2.8v5.6l-5 2.8-5-2.8V8.3z'
S['task-object_pose_estimation'] = ([P(BOX)], [P(BOX), P('M9 8.3l5 2.8 5-2.8M14 11.1v5.6'), P('M4 20.5V9M4 20.5h11.5M4 20.5l-1.5 1.5')])
S['task-panoptic_driving_perception'] = ([P('M8.5 3.5h7L20.5 20.5h-17z')],
    [P('M8.5 3.5 3.5 20.5M15.5 3.5l5 17'), P('M12 5v2M12 10.5v2.5M12 16.5v4')])
S['task-3d_object_detection'] = ([R(3, 9, 12, 12, 1.5)],
    [R(3, 9, 12, 12, 1.5), P('M9 3h10.5A1.5 1.5 0 0 1 21 4.5V15'), P('M3.4 9.4 9 3.4M14.6 9.4 20.6 3.4M14.6 20.6l5.9-5.9'), P('M9 3v2.5M9 8v1')])
# ── dx_app per-model task keys: renamed legacy keys reuse the same drawing under their own id, new tasks get
#    new drawings. Same table as dx_modelzoo/core/config.py CATEGORIES and LEGACY_TO_TASK in shared/tasks.py. ──
S['task-image_classification'] = S['task-classification']
S['task-oriented_object_detection'] = S['task-obb_detection']
S['task-face_landmark'] = S['task-face_alignment']
S['task-face_recognition'] = S['task-embedding']
S['task-person_attribute'] = S['task-attribute_recognition']
S['task-low_light_enhancement'] = S['task-image_enhancement']
S['task-person_reid'] = S['task-reid']
SPARK = 'M18.5 2.5v4M16.5 4.5h4'
S['task-anomaly_detection'] = ([FRAME], [FRAME, P('M6 14.5h3l2-5.5 2.5 8 1.5-3.5H18')])
S['task-zero_shot_image_classification'] = ([P(TAG)], [P(TAG), C(8.5, 8.5, 1.5), P(SPARK)])
S['task-zero_shot_instance_segmentation'] = ([P('M4 14a5.5 5.5 0 0 1 11 0v3.5A2.5 2.5 0 0 1 12.5 20h-6A2.5 2.5 0 0 1 4 17.5z')],
    [P('M4 14a5.5 5.5 0 0 1 11 0v3.5A2.5 2.5 0 0 1 12.5 20h-6A2.5 2.5 0 0 1 4 17.5z'), C(15.5, 10.5, 4), P('M5.5 2.5v4M3.5 4.5h4')])
S['task-image_matting'] = ([C(12, 9.5, 3.2), P('M6 20.5a6 6 0 0 1 12 0z')],
    [R(3, 3, 18, 18, 2.5), C(12, 9.5, 3.2), P('M6 20.5a6 6 0 0 1 12 0'), P('M3 8h2M3 13h2M19 8h2M19 13h2')])
S['task-image_retrieval'] = ([R(3, 3, 12, 12, 2)], [R(3, 3, 12, 12, 2), C(15.5, 15.5, 4), P('M18.5 18.5l3 3')])
S['task-visual_place_recognition'] = ([P(PIN)], [P(PIN), P('M9.5 10.5l2 2 3.5-4'), P('M4 21.5h16')])
S['task-face_attribute'] = ([C(10, 12.5, 6.5)],
    [C(10, 12.5, 6.5), P('M8.3 11.2v.1M11.7 11.2v.1'), P('M8 14.8c1.2.9 2.8.9 4 0'), P('M16.5 3h3.5l1.5 1.8-1.5 1.8h-3.5z')])

# ── Industry and award marks (launcher About, SDK Library) ──
CAR = 'M5 16.5V12l1.8-4.6A2 2 0 0 1 8.6 6h6.8a2 2 0 0 1 1.8 1.4L19 12v4.5'
S['car'] = ([P('M4 12h16v4.5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1z')], [P(CAR), P('M3.5 12h17'), P('M4 12v5.5M20 12v5.5'), C(8, 15, .6), C(16, 15, .6), P('M6.5 17.5v2M17.5 17.5v2')])
S['factory'] = ([P('M3 20V10l5 3V10l5 3V7l8 4v9z')], [P('M3 20V10l5 3V10l5 3V7l8 4v9z'), P('M2 20h20'), P('M16.5 5V3.5M7 16h2M12 16h2M17 16h2')])
S['robot'] = ([R(5, 8, 14, 11, 3)], [R(5, 8, 14, 11, 3), P('M12 8V4.5'), C(12, 3.5, 1), C(9.5, 13, .9), C(14.5, 13, .9), P('M10 16.2h4'), P('M3 12v3M21 12v3')])
S['city'] = ([R(9, 3, 7, 18, 1)], [P('M3 21h18'), R(9, 3, 7, 18, 1), P('M4 21V10h5M16 21v-8h4v8'), P('M11.5 7h2M11.5 10.5h2M11.5 14h2M6 13.5h1M6 17h1M17.5 16h1')])
S['drone'] = ([R(9, 9, 6, 6, 1.5)], [R(9, 9, 6, 6, 1.5), P('M9 9 7 7M15 9l2-2M9 15l-2 2M15 15l2 2'), C(5.5, 5.5, 2.5), C(18.5, 5.5, 2.5), C(5.5, 18.5, 2.5), C(18.5, 18.5, 2.5)])
BAG = 'M5 8h14l-1.2 11.4a1.8 1.8 0 0 1-1.8 1.6H8a1.8 1.8 0 0 1-1.8-1.6z'
S['bag'] = ([P(BAG)], [P(BAG), P('M9 10V6.5a3 3 0 0 1 6 0V10')])
S['medical'] = ([R(3, 5, 18, 15, 3)], [R(3, 5, 18, 15, 3), P('M9 5V3.5h6V5'), P('M12 9.5v6M9 12.5h6')])
SHIELD = 'M12 3 19.5 6v5.5c0 4.6-3.2 8.3-7.5 9.5-4.3-1.2-7.5-4.9-7.5-9.5V6z'
S['shield'] = ([P(SHIELD)], [P(SHIELD), P('M8.8 12.2l2.2 2.2 4.2-4.4')])
CUP = 'M7 4h10v5a5 5 0 0 1-10 0z'
S['award'] = ([P(CUP)], [P(CUP), P('M7 6H4.5v1.5A3 3 0 0 0 7.3 10.5M17 6h2.5v1.5a3 3 0 0 1-2.8 3'), P('M12 14v3.5M8.5 20.5h7M9.5 20.5l.8-3h3.4l.8 3')])
STAR = 'M12 3.5l2.6 5.4 5.9.8-4.3 4.1 1 5.9L12 17l-5.2 2.7 1-5.9-4.3-4.1 5.9-.8z'
S['star'] = ([P(STAR)], [P(STAR)])
S['news'] = ([R(3, 5, 14, 15, 2)], [P('M17 8h2.5A1.5 1.5 0 0 1 21 9.5v8.5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6.5A1.5 1.5 0 0 1 4.5 5H15.5A1.5 1.5 0 0 1 17 6.5V18a2 2 0 0 0 2 2'), P('M6.5 9h7M6.5 12.5h7M6.5 16h4.5')])
S['users'] = ([C(9, 8, 3.2)], [C(9, 8, 3.2), P('M3 19.5a6 6 0 0 1 12 0'), P('M15.5 5.2a3.2 3.2 0 0 1 0 5.6'), P('M17.5 13.8a6 6 0 0 1 3.5 5.7')])
S['briefcase'] = ([R(3, 7, 18, 13, 2.5)], [R(3, 7, 18, 13, 2.5), P('M8.5 7V5.5A1.5 1.5 0 0 1 10 4h4a1.5 1.5 0 0 1 1.5 1.5V7'), P('M3 12.5h18'), P('M12 11.5v2.5')])
S['user'] = ([C(12, 8, 3.8)], [C(12, 8, 3.8), P('M4.5 20.5a7.5 7.5 0 0 1 15 0')])

S['plus'] = ([], [P('M12 5v14M5 12h14')])
S['minus'] = ([], [P('M5 12h14')])

out = ['<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0" style="position:absolute" aria-hidden="true">',
       '<!-- DX AI Studio icon set. 24 grid, two layers: a faint fill (g.f) + a 2px line (g.l).',
       '     CSS outside cannot reach inside the <use> shadow tree, so shapes change only through inherited variables:',
       '     ico-fill (fill opacity, .24), ico-fill-o (whole fill, 1), ico-stroke (line width, 2). Colour is currentColor.',
       '     (XML comments cannot contain a double dash, so the variable names lose their leading dashes.)',
       '     The eight module icons match the launcher home glyphs. Contract: tests/shared/test_icon_system.py -->',
       '<defs>']
for name, (fills, lines) in S.items():
    body = ''
    if fills:
        body += f'<g class="f" style="{F}">' + ''.join(fills) + '</g>'
    body += f'<g class="l" style="{L}">' + ''.join(lines) + '</g>'
    out.append(f'<symbol id="{name}" viewBox="0 0 24 24">{body}</symbol>')
out += ['</defs>', '</svg>']
open(__import__('pathlib').Path(__file__).resolve().parents[1] / 'shared/static/dx-icons.svg', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print(len(S), 'symbols')

# ── Tab icons (favicons): the module glyph on a dark tile ──
# Tab strips can be light or dark; a dark tile with accent lines reads on both.
# Module name -> glyph. The launcher stands for the whole studio, so it gets the letters DX.
FAV_DIR = __import__('pathlib').Path(__file__).resolve().parents[1] / 'shared/static/favicons'
FAV = {'dx_app': 'app', 'dx_stream': 'stream', 'dx_modelzoo': 'zoo', 'dx_compiler': 'compiler',
       'dx_benchmark': 'bench', 'dx_planner': 'edge', 'dx_monitor': 'monitor', 'dx_agent_dev': 'agent'}
FAV_BG, FAV_FG = '#0b1220', '#2997ff'
FAV_DIR.mkdir(parents=True, exist_ok=True)
def _fav(body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
            f'<rect width="32" height="32" rx="7" fill="{FAV_BG}"/>{body}</svg>\n')
for mod, name in FAV.items():
    fills, lines = S[name]
    g = (f'<g transform="translate(2.5 2.5) scale(1.125)">'
         f'<g fill="{FAV_FG}" fill-opacity=".28" stroke="none">' + ''.join(fills) + '</g>'
         f'<g fill="none" stroke="{FAV_FG}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' + ''.join(lines) + '</g></g>')
    (FAV_DIR / f'{mod}.svg').write_text(_fav(g), encoding='utf-8')
(FAV_DIR / 'launcher.svg').write_text(_fav(
    f'<text x="16" y="21.5" text-anchor="middle" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="14" font-weight="800" fill="{FAV_FG}">DX</text>'), encoding='utf-8')
print(len(FAV) + 1, 'favicons')
