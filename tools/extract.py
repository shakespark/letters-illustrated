#!/usr/bin/env python3
"""从本机的 epub 解压目录（source/epub/index.html）提取文本到 source/text/NN.txt。
00 = Preface、Introduction、Editorial Note；01–05 = 五个十年（1960s … 2000s）。
每行一段，行首 [段号]（每个文件内连续编号）。`# ✉ k` 是这个十年里的第 k 封信（或备忘录、专栏），后面是日期和称呼。
段落标记：没有标记 = 作者 2007 年写的串场文字；{D} 日期行；{L} 信的正文（含称呼、落款）；{Q} 缩进的引文；
{H} 信里附的专栏标题；{N} 信里的编号条目；{I} 这里原书是一张图（信头、诗、表），文字搜不到，内容见 source/notes/images.md。
这一版电子书是扫描识别的，错字照原样保留（读者在 Kindle 里看到、搜到的就是这些字）。"""
import html, os, re
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
s = open(os.path.join(ROOT, "source/epub/index.html"), encoding="utf-8").read()
s = s[s.index("<body"):]
KIND = {"cl-1p-v": "", "cl-1p-v1": "", "cl-pf-v": "", "cl-pr-v": "{D} ", "cl-pi-v": "{L} ", "cl-pi-v1": "{L} ", "cl-pi-v2": "{L} ", "cl-pi-v3": "{L} ",
        "cl-bq-v": "{Q} ", "cl-h1-c-v": "{H} ", "cl-pc-v": "{H} ", "cl-l-1-v": "{N} ", "cl-f-l-v": "{L} "}
FILES = {"PREFACE": 0, "The 1960s": 1, "The 1970s": 2, "The 1980s": 3, "The 1990s": 4, "The 2000s": 5}
DATE = re.compile(r"^(January|February|March|April|May|June|July|August|September|October|November|December)\b.{0,12}\b(19|20)\d\d\b")
out, cur, page, newpage = {}, None, 0, False
for pg, tag, cls, txt in re.findall(r'<div id="page(\d+)"[^>]*>|<(h\d|p) class="([^"]+)"[^>]*>(.*?)</\2>', s, flags=re.S):
    if pg: page, newpage = int(pg), True; continue
    imgs = re.findall(r'<img src="([^"]+)"', txt)
    t = re.sub(r"\s+", " ", html.unescape(re.sub("<[^>]+>", "", txt))).strip()
    if tag in ("h1", "h2"):
        if t in FILES: cur = FILES[t]; out[cur] = []
        elif t.startswith("Index"): cur = None
        if cur == 0: out[0].append(("#", t.title()))
        continue
    if cur is None: continue
    if cls == "cl-pf-v" and t.startswith("EDITORIAL NOTE"): out[cur].append(("#", "Editorial Note"))
    kind = KIND.get(cls, "")
    for i in imgs: out[cur].append(("{I} ", f"〔图：{i}〕"))
    if not t: continue
    if kind == "{L} " and DATE.match(t) and len(t.split()) <= 4: kind = "{D} "
    # 扫描版在换页处把一段切成了两段：同一种段落、前半段没有以句末标点收尾，就接回去
    if newpage and out[cur] and out[cur][-1][0] == kind and kind in ("", "{L} ") and not re.search(r"[.?!:;\"'”)…\]]$|\.{3}$", out[cur][-1][1]) and not t.startswith("Dear "):
        out[cur][-1] = (kind, out[cur][-1][1] + " " + t)
    else: out[cur].append((kind, t))
    newpage = False
os.makedirs(os.path.join(ROOT, "source/text"), exist_ok=True)
for k, items in sorted(out.items()):
    lines, n, letters, prev_letter = [], 0, 0, False
    for i, (kind, t) in enumerate(items):
        if kind == "#": lines.append(f"# {t}\n"); continue
        in_letter = kind != ""
        # 一封信从日期行开始；没有日期行的，从串场文字之后的第一段信文开始
        if k and in_letter and (kind == "{D} " or not prev_letter) and not (prev_letter and items[i - 1][0] == "{D} "):
            if not (kind != "{D} " and prev_letter):
                letters += 1
                nxt = [x[1] for x in items[i:i + 4] if x[0] in ("{L} ", "{N} ")]
                sal = next((x for x in nxt if re.match(r"(Dear |TO:|FROM:|MEMORANDUM)", x)), "")
                date = t if kind == "{D} " else ""
                lines.append(f"# ✉ {letters} · {date or '（没有日期行）'} · {sal[:60]}\n")
        prev_letter = in_letter
        n += 1; lines.append(f"[{n}] {kind}{t}\n")
    open(os.path.join(ROOT, f"source/text/{k:02d}.txt"), "w", encoding="utf-8").write("".join(lines))
    words = sum(len(x.split()) - 1 for x in lines if x[0] == "[")
    print(f"{k:02d}  {letters:3d} 封  {n:4d} 段  {words:6d} 词")
