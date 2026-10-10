#!/usr/bin/env python3
"""章节页结构检查：python3 tools/lint.py chapters/01a.html …
每个十年拆成几页（01a、01b…），每页的段落范围读 assets/chapters.js 里的 p: [起, 止]。
查：小节标题和顺序、信件地图（开头几个词是否照抄、顺序、够不够）、错字表（屏幕上的字是否真在那一段里）、
「Odyssey 里讲过这一段」的链接、词条（.en 重复、.loc 是否在原文对应段落里、顺序、密度、trap 占比）、引用块数量、图片、
页面里的 <style>/<script>/写死的颜色、直引号、原书材料的路径。通用的几项在 ~/tutorials-deploy/scripts/lint_common.py。"""
import os, re, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.expanduser("~/tutorials-deploy/scripts"))
from lint_common import norm, check_entries, check_quotes, check_images, check_markup, counts

PAGES = {m.group(1): (int(m.group(2)), int(m.group(3))) for m in re.finditer(
    r'id: "(\d\d[a-z]?)", ch: \d+, part: "[^"]*", p: \[(\d+), (\d+)\]', open(os.path.join(ROOT, "assets/chapters.js"), encoding="utf-8").read())}
ody = os.path.expanduser("~/a_personal_odyssey/assets/chapters.js")
ODYSSEY = set(re.findall(r'\{ id: "(\d\d[a-c]?)"', open(ody, encoding="utf-8").read())) if os.path.exists(ody) else None
SECS = ["这一页在做什么", "收信人和提到的人", "信件地图", "背景：作者默认你知道的事", "Odyssey 里讲过这一段", "这一版的错字", "词与短语", "值得停下来的句子", "检查一下理解"]

def load(src):
    """读 source/text/NN.txt：{段号: 归一化后的文字}（去掉 {D} {L} 这类标记），以及每封信（# ✉）第一段的段号。"""
    paras, letters, pending = {}, [], False
    for line in (open(src, encoding="utf-8").read().splitlines() if os.path.exists(src) else []):
        m = re.match(r"\[(\d+)\] (?:\{[A-Z]\} )?(.*)$", line)
        if line.startswith("# ✉"): pending = True
        elif m:
            paras[int(m.group(1))] = norm(m.group(2))
            if pending: letters.append(int(m.group(1))); pending = False
    return paras, letters

bad = 0
for path in sys.argv[1:]:
    t = open(path, encoding="utf-8").read(); errs = []
    pid = re.search(r"(\d\d[a-z]?)\.html$", path).group(1); nn = pid[:2]; N = int(nn)
    paras, letters = load(os.path.join(ROOT, f"source/text/{nn}.txt"))
    if N and pid not in PAGES: errs.append(f"chapters.js 里没有 {pid} 这一页")
    P0, P1 = PAGES.get(pid, (1, max(paras, default=0)))
    paras = {k: v for k, v in paras.items() if P0 <= k <= P1}
    letters = [p for p in letters if P0 <= p <= P1]
    if f'<body data-page="{pid}">' not in t: errs.append(f'<body> 应写成 <body data-page="{pid}">')

    if N:
        pos = [t.find(f"<h2>{s}</h2>") for s in SECS]
        for s, k in zip(SECS, pos):
            if k < 0: errs.append(f"缺少小节：{s}")
        if -1 not in pos and pos != sorted(pos): errs.append("小节顺序不对，应为：" + " → ".join(SECS))
        for s in re.findall(r"<h2>(.*?)</h2>", t):
            if s not in SECS: errs.append(f"多出来的小节标题：{s}（标题一个字都不能改）")

        # 信件地图：<ol class="map"><li data-p="段号"><b>开头几个词</b><span class="meta">日期 · 写给谁</span>留意什么</li>
        items = [(int(p), norm(re.sub(r"<[^>]+>", "", b)).strip("… ").strip()) for p, b in re.findall(r'<li(?: class="in")? data-p="(\d+)"><b>(.*?)</b>', t, flags=re.S)]
        ps = [p for p, _ in items]
        if ps != sorted(set(ps)): errs.append(f"信件地图的段号应递增、不重复，实际是 {ps}")
        if len(items) < max(3, int(len(letters) * 0.8)): errs.append(f"信件地图只有 {len(items)} 条，这一页有 {len(letters)} 封信（至少列出八成）")
        for p, b in items:
            if p not in paras: errs.append(f"信件地图：第 {p} 段不在这一页的范围（{P0}–{P1}）里")
            elif not paras[p].startswith(b): errs.append(f"信件地图：{b!r} 不是第 {p} 段的开头")
            if not 3 <= len(b.split()) <= 7: errs.append(f"信件地图：开头应照抄 4–6 个词：{b!r}")
        if t.count('<span class="meta">') < len(items): errs.append("信件地图：每条都要有 <span class=\"meta\">日期 · 写给谁</span>")

        # 错字表：<table class="terms typos"> … <tr data-p="段号"><td>屏幕上的字</td><td>应为</td><td class="zh">说明</td></tr>
        typos = re.findall(r'<tr data-p="(\d+)"><td>(.*?)</td><td>(.*?)</td>', t, flags=re.S)
        if '<table class="terms typos">' not in t or len(typos) < 3: errs.append(f"错字表至少 3 行（<table class=\"terms typos\">，每行 <tr data-p>），现在 {len(typos)} 行")
        for p, wrong, right in typos:
            w = norm(re.sub(r"<[^>]+>", "", wrong))
            if w not in paras.get(int(p), ""): errs.append(f"错字表：第 {p} 段里找不到 {w!r}（第一格要照抄屏幕上的字）")
            if w == norm(re.sub(r"<[^>]+>", "", right)): errs.append(f"错字表：{w!r} 两格一样")

        # Odyssey 的链接
        sec = t[t.find("<h2>Odyssey 里讲过这一段</h2>"):t.find("<h2>这一版的错字</h2>")]
        links = re.findall(r'href="([^"]*odyssey[^"]*)"', t)
        for u in links:
            m = re.fullmatch(r"/odyssey/chapters/(\d\d[a-c]?)\.html", u)
            if not m: errs.append(f"Odyssey 的链接应写成 /odyssey/chapters/<页 id>.html：{u}")
            elif ODYSSEY is not None and m.group(1) not in ODYSSEY: errs.append(f"Odyssey 伴读没有这一页：{u}")
        if sec.count("<div><b>") < 1: errs.append("「Odyssey 里讲过这一段」至少一张卡片")

    c0 = counts(t)
    errs += check_entries(t, paras, per_k=14 if N else None, max_n=110, trap_ratio=0.4 if N else None, scope="这一页")
    if N and c0["词条"] and c0["trap"] > c0["词条"] * 0.62: errs.append(f"trap {c0['trap']}/{c0['词条']}，标得太宽（四成到六成为宜）")
    errs += check_quotes(t, 2)
    errs += check_images(t, path, min_photos=1 if N else 0, min_svgs=1 if N else 0)
    c = counts(t)
    if N and c["照片"] + c["SVG"] < 4: errs.append(f"图不够：照片 {c['照片']}，SVG {c['SVG']}（至少共 4 张）")
    if c["照片"] > 6: errs.append(f"照片 {c['照片']} 张，超过 6 张")
    if N and not 5 <= c["检查题"] <= 6: errs.append(f"理解检查应有 5–6 题，现在 {c['检查题']} 题")
    errs += check_markup(t)
    g = re.search(r'<div class="gist">(.*?)</div>', t, flags=re.S)
    if g and len(re.findall(r"[一-鿿]", g.group(1))) > 170: errs.append(f"「这一页在做什么」{len(re.findall(r'[一-鿿]', g.group(1)))} 个汉字，超过 150")
    print(("✗" if errs else "✓"), path, " ".join(f"{k} {v}" for k, v in c.items()), f"地图 {len(re.findall(r'<li(?: class=.in.)? data-p=', t))} 错字 {len(re.findall(r'<tr data-p=', t))}")
    for e in errs: print("    " + e)
    bad += bool(errs)
sys.exit(1 if bad else 0)
