"""Chip die image analysis for hotspot coordinate distribution."""
from PIL import Image
import json

for name in ['dx-m1-die.jpg', 'dx-m2-die.jpg']:
    img = Image.open(f'launcher/static/img/about/{name}')
    print(f'{name}: {img.size}')

# SVG viewBox is 0 0 600 620
# Grid-distributed hotspot layout

m1_hotspots = {
    'vision':     {'x': 15, 'y': 20, 'width': 180, 'height': 170},
    'company':    {'x': 210, 'y': 20, 'width': 180, 'height': 170},
    'investment': {'x': 405, 'y': 20, 'width': 180, 'height': 170},
    'awards':     {'x': 15, 'y': 210, 'width': 180, 'height': 170},
    'milestones': {'x': 210, 'y': 210, 'width': 180, 'height': 170},
    'values':     {'x': 405, 'y': 210, 'width': 180, 'height': 170},
    'news':       {'x': 15, 'y': 400, 'width': 280, 'height': 200},
    'media':      {'x': 310, 'y': 400, 'width': 275, 'height': 200},
}

m2_hotspots = {
    'chips':     {'x': 15, 'y': 20, 'width': 180, 'height': 170},
    'modules':   {'x': 210, 'y': 20, 'width': 180, 'height': 170},
    'iq8':       {'x': 405, 'y': 20, 'width': 180, 'height': 170},
    'sdk':       {'x': 15, 'y': 210, 'width': 180, 'height': 170},
    'solutions': {'x': 210, 'y': 210, 'width': 180, 'height': 170},
    'partners':  {'x': 405, 'y': 210, 'width': 180, 'height': 170},
    'buy':       {'x': 150, 'y': 400, 'width': 300, 'height': 200},
}

print("\nM1 hotspots (8 regions, 600x620 viewBox):")
for k, h in m1_hotspots.items():
    print(f"  {k}: x={h['x']} y={h['y']} w={h['width']} h={h['height']}")

print("\nM2 hotspots (7 regions, 600x620 viewBox):")
for k, h in m2_hotspots.items():
    print(f"  {k}: x={h['x']} y={h['y']} w={h['width']} h={h['height']}")
