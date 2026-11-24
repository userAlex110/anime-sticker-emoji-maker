#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检查一批贴纸是否真的带透明通道，输出需要去底的文件清单。

用法：
    python3 check_alpha.py --dir ./成品
    python3 check_alpha.py --dir ./成品 --json ./alpha_report.json

判定：
- OK           : RGBA/LA，且存在全透明像素（min alpha < 10）
- NO_ALPHA     : 没有 alpha 通道（常见于生图工具偶发返回 RGB 白底）
- OPAQUE       : 有 alpha 但完全不透明（等于没抠图）

对 NO_ALPHA / OPAQUE 的文件，逐个跑：
    mediakit-cli image remove-image-background --image-url "<绝对路径或URL>" --scene general
抠图结果要复查白边是否保留（见 references/qc-checklist.md）。
"""
import argparse
import glob
import json
import os

from PIL import Image


def inspect(path):
    im = Image.open(path)
    info = dict(file=os.path.basename(path), mode=im.mode, size=list(im.size))
    if im.mode not in ("RGBA", "LA") and "transparency" not in im.info:
        info["status"] = "NO_ALPHA"
        return info
    rgba = im.convert("RGBA")
    a = rgba.getchannel("A")
    lo, _ = a.getextrema()
    hist = a.histogram()
    ratio = hist[0] / (rgba.width * rgba.height)
    info["transparent_ratio"] = round(ratio, 3)
    info["status"] = "OK" if lo < 10 else "OPAQUE"
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--json", default="")
    a = ap.parse_args()

    files = sorted(glob.glob(os.path.join(a.dir, "*.png")))
    if not files:
        raise SystemExit("没有找到 PNG")
    rows = [inspect(f) for f in files]
    for r in rows:
        flag = "OK  " if r["status"] == "OK" else "!!  "
        extra = f"透明占比 {r.get('transparent_ratio', 0):.1%}" if "transparent_ratio" in r else "无 alpha 通道"
        print(f"{flag}{r['file']:34s} {r['mode']:5s} {r['size'][0]}x{r['size'][1]}  {extra}")

    bad = [r["file"] for r in rows if r["status"] != "OK"]
    print(f"\n共 {len(rows)} 张，需去底 {len(bad)} 张")
    for f in bad:
        print("  -", f)

    if a.json:
        with open(a.json, "w", encoding="utf-8") as fp:
            json.dump(rows, fp, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
