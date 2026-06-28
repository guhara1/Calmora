#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
히어로 원본 이미지를 webp로 압축(목표 용량 이하)해 assets/img/hero-spa.webp 생성.

사용:
    python3 tools/make_hero_webp.py <원본경로> [목표KB=50] [최대가로px=1280]

예:
    python3 tools/make_hero_webp.py assets/img/hero-spa-src.png 50 1280
"""
import sys, os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "img", "hero-spa.webp")

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    src = sys.argv[1]
    target_kb = float(sys.argv[2]) if len(sys.argv) > 2 else 50.0
    max_w = int(sys.argv[3]) if len(sys.argv) > 3 else 1280
    target = int(target_kb * 1024)

    im = Image.open(src).convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)

    # 품질을 낮춰가며 목표 용량 이하를 찾고, 안 되면 가로폭도 축소
    best = None
    for width in (max_w, 1152, 1024, 960, 896, 800):
        w_im = im if width == im.width else im.resize(
            (width, round(im.height * width / im.width)), Image.LANCZOS)
        for q in range(82, 24, -3):
            w_im.save(OUT, "WEBP", quality=q, method=6)
            size = os.path.getsize(OUT)
            if best is None or size < best[0]:
                best = (size, width, q)
            if size <= target:
                print(f"OK  {size/1024:.1f}KB  {width}px  q={q}  -> {OUT}")
                return
    # 목표 미달이어도 가장 작은 결과 저장(마지막 저장본). best 재생성
    size, width, q = best
    w_im = im if width == im.width else im.resize(
        (width, round(im.height * width / im.width)), Image.LANCZOS)
    w_im.save(OUT, "WEBP", quality=q, method=6)
    print(f"WARN 목표({target_kb}KB) 미달, 최소본 저장: {os.path.getsize(OUT)/1024:.1f}KB {width}px q={q}")

if __name__ == "__main__":
    main()
