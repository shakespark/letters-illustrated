#!/usr/bin/env python3
"""复用 Odyssey 伴读已经取好的维基照片（省得再去维基排队）：
    python3 tools/reuse_img.py list                       # 列出可复用的照片和出处
    python3 tools/reuse_img.py 05-b-friedman.jpg 01 a-friedman   # 复制成 assets/img/01-a-friedman.jpg，并把出处那一行抄进 CREDITS.md
复制后照样要用 Read 看一眼图，再写 alt 和图注。"""
import os, re, shutil, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SRC = os.path.expanduser("~/a_personal_odyssey/assets/img")
credits = {m.group(1): m.group(2) for m in re.finditer(r"^- `([^`]+)` — (.*)$", open(os.path.join(SRC, "CREDITS.md"), encoding="utf-8").read(), flags=re.M)}
if len(sys.argv) == 2 and sys.argv[1] == "list":
    for k, v in sorted(credits.items()): print(k, "—", v.split(" — https://")[0])
    sys.exit(0)
if len(sys.argv) != 4 or not re.fullmatch(r"\d\d", sys.argv[2]) or not re.fullmatch(r"[a-z0-9-]+", sys.argv[3]): sys.exit(__doc__)
src, name = sys.argv[1], f"{sys.argv[2]}-{sys.argv[3]}.jpg"
if src not in credits: sys.exit(f"Odyssey 的 CREDITS.md 里没有 {src}")
dst = os.path.join(ROOT, "assets/img", name)
if os.path.exists(dst): sys.exit(f"已经有 {name} 了")
shutil.copyfile(os.path.join(SRC, src), dst)
with open(os.path.join(ROOT, "assets/img/CREDITS.md"), "a", encoding="utf-8") as f: f.write(f"- `{name}` — {credits[src]}\n")
parts = credits[src].split(" — ")
print(f"已复制为 assets/img/{name}\n出处：{parts[1]}，{parts[2]}，维基共享资源")
