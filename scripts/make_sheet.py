#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把一批透明底贴纸拼成一张整版预览（白卡片网格），用于交付前的整体检查。

用法：
    python3 make_sheet.py --src ./成品 --out ./00_整版预览.png
    python3 make_sheet.py --src ./成品 --out ./预览.png --cols 5 --cell 400

说明：
- 只做排版预览，不改原图；贴纸仍以单张透明 PNG 交付。
- 按文件名排序，建议命名成 `<角色>_<序号>_<动作>.png`，同角色自然排在一起。
"""
import argparse
import glob
import math
import os

from PIL import Image, ImageDraw

BG = (247, 246, 243)
CARD = (255, 255, 255)
LINE = (232, 230, 224)


def build(src, out, cols=4, cell=420, gap=14, margin=36, pad=22, radius=16):
    files = sorted(
        f for f in glob.glob(os.path.join(src, "*.png"))
        if not os.path.basename(f).startswith("00_") and "整版" not in os.path.basename(f)
    )
    if not files:
        raise SystemExit("没有找到 PNG（已排除 00_ 开头的预览图）")
    rows = math.ceil(len(files) / cols)
    W = margin * 2 + cols * cell + (cols - 1) * gap
    H = margin * 2 + rows * cell + (rows - 1) * gap
    sheet = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(sheet)

    for i, f in enumerate(files):
        im = Image.open(f).convert("RGBA")
        im.thumbnail((cell - pad, cell - pad), Image.LANCZOS)
        r, c = divmod(i, cols)
        x0 = margin + c * (cell + gap)
        y0 = margin + r * (cell + gap)
        d.rounded_rectangle([x0, y0, x0 + cell, y0 + cell], radius=radius, fill=CARD, outline=LINE, width=2)
        sheet.paste(im, (x0 + (cell - im.width) // 2, y0 + (cell - im.height) // 2), im)

    sheet.save(out)
    print(f"{out} {sheet.width}x{sheet.height} {len(files)}张")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--cell", type=int, default=420)
    a = ap.parse_args()
    build(a.src, a.out, a.cols, a.cell)


if __name__ == "__main__":
    main()
