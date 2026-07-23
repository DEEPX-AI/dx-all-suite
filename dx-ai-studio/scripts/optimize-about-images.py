#!/usr/bin/env python3
"""deepx-assets → launcher/static/img/about/ image optimization.
Usage: python3 scripts/optimize-about-images.py
"""
import shutil
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'deepx-assets' / 'images'
DST = ROOT / 'launcher' / 'static' / 'img' / 'about'

EXCLUDE_PATTERNS = [
    'banners/썸네일-',
    'our-story/Hero-사인파-',
    'products/DX-H1-Quattro-PCIe카드-실물사진-썸네일',
    'related/DX-H1-Quattro',
    'solutions/partner-',
    'solutions/솔루션-스마트시티-AAEON-',
    'systems/AAEON-DX-AIPlayer-',
]

def should_exclude(rel_path: str) -> bool:
    for pat in EXCLUDE_PATTERNS:
        if pat in rel_path:
            return True
    return False

def resize_copy(src: Path, dst: Path, max_width: int):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.suffix.lower() == '.svg':
        shutil.copy2(src, dst)
        return
    try:
        img = Image.open(src)
        w, h = img.size
        if w > max_width:
            ratio = max_width / w
            new_size = (max_width, int(h * ratio))
            img = img.resize(new_size, Image.LANCZOS)
        if dst.suffix.lower() in ('.jpg', '.jpeg'):
            img.save(dst, 'JPEG', quality=85, optimize=True)
        else:
            img.save(dst, optimize=True)
        print(f'  ✅ {dst.name} ({img.size[0]}×{img.size[1]})')
    except Exception as e:
        print(f'  ❌ {src.name}: {e}')
        shutil.copy2(src, dst)

COPY_MAP = [
    ('our-story/DEEPX-DX-M1-칩다이-Xray-아트렌더링.jpg', 'dx-m1-die.jpg', 600),
    ('our-story/DEEPX-DX-M2-칩다이-아트렌더링.jpg', 'dx-m2-die.jpg', 600),
    ('our-story/DEEPX-Intelligented-by-DEEPX-핵심마케팅-포스터.png', 'marketing/intelligented.png', 800),
]

DIR_MAP = [
    ('awards', 'awards', 400),
    ('partners', 'partners', 9999),  # SVG originals kept
    ('news', 'news', 600),
    ('use-cases', 'use-cases', 600),
    ('architecture', 'architecture', 800),
]

PRODUCTS_SELECT = [
    'DEEPX-AI칩-DX-M1-M1M-M2-라인업-홍보사진.png',
    'DX-M1-칩-실물사진.jpg',
    'DX-M1-칩-블록다이어그램.jpg',
    'DX-H1-Quattro-PCIe카드-실물사진-고해상도.jpg',
    'DX-H1-Quattro-블록다이어그램.jpg',
    'DX-H1-VNPU-PCIe카드-실물사진.png',
    'DX-H1-VNPU-블록다이어그램.jpg',
    'DX-M1-M2HAT-RaspberryPi5-평가키트-실물사진.png',
]

SYSTEMS_SELECT = [
    'Lenovo-ThinkSystem-SR650-V3-2U랙서버-실물사진.png',
    'HPE-ProLiant-DL380-Gen11-2U랙서버-실물사진.png',
    'Supermicro-SYS-221H-2U랙서버-실물사진.png',
    'EmbeddedArtists-COM캐리어보드-DX-M1SOM-평가키트-실물사진.png',
    'Radxa-ROCK5B플러스-파란메탈케이스-실물사진.png',
    'LattePanda-3-Delta-DEEPX-DX-M1-M2장착-실물사진.png',
    'Grinn-AstraOne-에지AI-SBC-실물사진.png',
    'Portwell-WEBS-45J1-팬리스산업용PC-실물사진.png',
]

SOLUTIONS_SELECT = [
    'solution-edge-computing-smart-city-cover.png',
    'solution-smart-mobility-cover.jpg',
    '솔루션-스마트팩토리-커버이미지.jpg',
    '솔루션-스마트팩토리-공장내부-Getty스톡이미지.jpg',
    '솔루션-성공사례-Success-Stories-메인커버.png',
]

PARTNER_PNGS = [
    'our-story/파트너로고-AAEON.png',
    'our-story/파트너로고-AIC.png',
    'our-story/파트너로고-AWS-Amazon.png',
    'our-story/파트너로고-Baidu-PaddlePaddle.png',
    'our-story/파트너로고-Hyundai-현대.png',
    'our-story/파트너로고-LG-U플러스.png',
    'our-story/파트너로고-NetworkOptix.png',
    'our-story/파트너로고-POSCO-DX.png',
    'our-story/파트너로고-WindRiver.png',
]

def main():
    DST.mkdir(parents=True, exist_ok=True)
    total = 0

    print('── Individual files ──')
    for src_rel, dst_rel, max_w in COPY_MAP:
        src = SRC / src_rel
        dst = DST / dst_rel
        if src.exists():
            resize_copy(src, dst, max_w)
            total += 1

    for src_dir, dst_dir, max_w in DIR_MAP:
        src_path = SRC / src_dir
        if not src_path.exists():
            continue
        print(f'\n── {src_dir} → {dst_dir} ──')
        for f in sorted(src_path.iterdir()):
            if f.is_file() and not should_exclude(f'{src_dir}/{f.name}'):
                dst = DST / dst_dir / f.name
                resize_copy(f, dst, max_w)
                total += 1

    print('\n── products (selected) ──')
    for name in PRODUCTS_SELECT:
        src = SRC / 'products' / name
        if src.exists():
            resize_copy(src, DST / 'products' / name, 600)
            total += 1

    print('\n── systems (selected) ──')
    for name in SYSTEMS_SELECT:
        src = SRC / 'systems' / name
        if src.exists():
            resize_copy(src, DST / 'systems' / name, 400)
            total += 1

    print('\n── solutions (selected) ──')
    for name in SOLUTIONS_SELECT:
        src = SRC / 'solutions' / name
        if src.exists():
            resize_copy(src, DST / 'solutions' / name, 800)
            total += 1

    print('\n── Partner PNG logos ──')
    for rel in PARTNER_PNGS:
        src = SRC / rel
        if src.exists():
            dst_name = src.name.replace('파트너로고-', '').lower()
            resize_copy(src, DST / 'partners' / dst_name, 200)
            total += 1

    print(f'\n✅ Total: {total} images optimized')
    import subprocess
    result = subprocess.run(['du', '-sh', str(DST)], capture_output=True, text=True)
    print(f'📦 Size: {result.stdout.strip().split()[0]}')

if __name__ == '__main__':
    main()
