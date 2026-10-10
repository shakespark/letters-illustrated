// A Man of Letters · 英文伴读：共享脚本。注入顶栏、章头、五个十年的时间条、章末导航、页脚；接管词条的"记下"和筛选。
// localStorage 键一律带 ml- 前缀（全站各教程同一个域名）：ml-done-<页 id>、ml-star-<页 id>-<词条>、ml-theme。
(() => {
  const BOOK = window.ML_BOOK || [], PAGES = window.ML_PAGES || [], READY = new Set(window.ML_READY || []);
  const SITE = "A Man of Letters · 英文伴读";
  const ROOT = document.currentScript.src.replace(/assets\/ml\.js.*$/, "");
  const LS = {
    get(k) { try { return localStorage.getItem(k); } catch { return null; } },
    set(k, v) { try { v == null ? localStorage.removeItem(k) : localStorage.setItem(k, v); } catch {} },
    keys(prefix) { try { return Object.keys(localStorage).filter((k) => k.startsWith(prefix)); } catch { return []; } },
  };
  const h = (tag, attrs = {}, ...kids) => {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) k === "class" ? (el.className = v) : k.startsWith("on") ? (el[k] = v) : el.setAttribute(k, v);
    el.append(...kids.filter((x) => x != null));
    return el;
  };
  const href = (id) => `${ROOT}chapters/${id}.html`;
  const book = (ch) => BOOK.find((b) => b.n === ch) || {};
  const label = (p) => (p.ch === 0 ? "开读之前" : `${book(p.ch).zh}（${p.part}）`);
  const minutes = (words) => Math.max(2, Math.round(words / 130)); // 读外语原文，按每分钟 130 词估
  const isDone = (id) => LS.get(`ml-done-${id}`) === "1";
  const badges = (p) => [
    p.y ? h("span", { class: "badge" }, p.y) : null,
    p.letters ? h("span", { class: "badge" }, `${p.letters} 封信`) : null,
    h("span", { class: "badge" }, `约 ${p.words} 词 · 读约 ${minutes(p.words)} 分钟`),
  ];

  const saved = LS.get("ml-theme");
  if (saved) document.documentElement.dataset.theme = saved;
  function themeBtn() {
    return h("button", { class: "btn", "aria-label": "切换深色/浅色", onclick() {
      const dark = document.documentElement.dataset.theme ? document.documentElement.dataset.theme === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
      const next = dark ? "light" : "dark";
      document.documentElement.dataset.theme = next; LS.set("ml-theme", next);
    } }, "深/浅");
  }

  // 时间条：这一页所在的十年里有几页，标出当前是哪一页；两头是前后的十年。窄屏横向滚动。
  function strip(p) {
    const cells = [];
    for (const b of BOOK.filter((x) => x.n > 0)) {
      const pages = PAGES.filter((x) => x.ch === b.n);
      if (b.n !== p.ch) {
        const ready = pages[0] && READY.has(pages[0].id);
        cells.push(h(ready ? "a" : "span", Object.assign({ class: "cell", title: [b.en, b.place].filter(Boolean).join(" · ") }, ready ? { href: href(pages[0].id) } : {}),
          h("b", {}, b.zh.replace(" 年代", "s")), h("span", { class: "zh" }, `${pages.length} 页`), h("span", { class: "y" }, b.y)));
        continue;
      }
      for (const x of pages) {
        const ready = READY.has(x.id) && x.id !== p.id;
        cells.push(h(ready ? "a" : "span", Object.assign({ class: "cell" + (x.id === p.id ? " here" : ""), title: x.t }, ready ? { href: href(x.id) } : {}),
          h("b", {}, x.part), h("span", { class: "zh" }, b.zh), h("span", { class: "y" }, x.y)));
      }
    }
    const el = h("div", { class: "lifeline", role: "navigation", "aria-label": "全书五个十年，和这个十年里的各页" }, ...cells);
    requestAnimationFrame(() => { const here = el.querySelector(".here"); if (here) el.scrollLeft = here.offsetLeft - el.clientWidth / 2 + here.clientWidth / 2; });
    return el;
  }

  function mountChrome() {
    const id = document.body.dataset.page || null;
    const i = PAGES.findIndex((x) => x.id === id), p = PAGES[i];
    document.body.prepend(h("div", { class: "topbar" }, h("div", { class: "topbar-inner" },
      h("a", { class: "home", href: `${ROOT}index.html` }, SITE),
      h("span", { class: "crumb" }, p ? `${label(p)}${p.ch ? " · " + p.t : ""}` : ""),
      themeBtn())));
    document.body.append(h("footer", { class: "site-footer" },
      h("a", { href: "https://beian.miit.gov.cn/", target: "_blank", rel: "noopener" }, "京ICP备18057656号-1")));
    if (!p) return;
    const b = book(p.ch), main = document.querySelector("main");
    document.title = `${label(p)}${p.ch ? " · " + p.t : ""} · ${SITE}`;
    main.prepend(h("div", { class: "chapter-head" },
      h("div", { class: "kicker" }, p.ch === 0 ? "PREFACE · INTRODUCTION" : `${b.en.toUpperCase()} · ${p.y}`),
      h("h1", {}, p.ch === 0 ? p.t : `${label(p)}　${p.t}`),
      h("div", { class: "badges" }, ...badges(p))),
      ...(p.ch ? [strip(p)] : []));
    const prev = PAGES[i - 1], next = PAGES[i + 1];
    const done = h("button", { class: "btn" });
    const paint = () => { done.textContent = isDone(id) ? "✓ 已读完这一页对应的部分" : "标记：这一部分读完了"; done.setAttribute("aria-pressed", isDone(id)); };
    done.onclick = () => { LS.set(`ml-done-${id}`, isDone(id) ? null : "1"); paint(); };
    paint();
    main.append(h("div", { class: "chapter-end" }, done, h("div", { class: "nav" },
      prev ? h("a", { class: "btn", href: href(prev.id) }, `← ${label(prev)}`) : null,
      h("a", { class: "btn", href: `${ROOT}index.html` }, "目录"),
      next && READY.has(next.id) ? h("a", { class: "btn primary", href: href(next.id) }, `${label(next)} →`) : null)));
  }

  // 词条：<div class="entry [trap]"><div class="en">…</div><div class="loc" data-p="段号">原句里的 4–7 个词</div><div class="zh">…</div><div class="note">…</div></div>
  function wireEntries() {
    const entries = [...document.querySelectorAll(".entry")];
    if (!entries.length) return;
    const id = document.body.dataset.page;
    const count = h("span", { class: "count" });
    const mk = (text, cls) => h("button", { class: "btn", "aria-pressed": String(!cls), onclick(e) {
      document.body.classList.remove("only-traps", "only-starred");
      if (cls) document.body.classList.add(cls);
      bar.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b === e.currentTarget)));
    } }, text);
    const bar = h("div", { class: "toolbar" }, mk("全部", ""), mk("只看「每个字都认识」", "only-traps"), mk("只看我记下的", "only-starred"), count);
    const anchor = document.querySelector(".sec") || entries[0];
    anchor.before(bar, h("p", { class: "empty-note" }, "还没有记下任何词条。回到「全部」，点词条右边的「记下」。"));
    const refresh = () => {
      const k = entries.filter((e) => e.classList.contains("starred")).length;
      document.body.classList.toggle("none-starred", k === 0);
      count.textContent = `共 ${entries.length} 条 · 已记下 ${k}`;
    };
    for (const e of entries) {
      const en = e.querySelector(".en"), text = en.textContent.trim();
      const key = `ml-star-${id}-${text}`;
      if (e.classList.contains("trap")) en.append(h("span", { class: "tag" }, "每个字都认识"));
      const btn = h("button", { class: "btn star" });
      const paint = () => { btn.textContent = e.classList.contains("starred") ? "已记下" : "记下"; };
      if (LS.get(key)) e.classList.add("starred");
      btn.onclick = () => {
        const on = e.classList.toggle("starred");
        LS.set(key, on ? JSON.stringify({ zh: e.querySelector(".zh")?.textContent.trim() || "" }) : null);
        paint(); refresh();
      };
      paint(); en.after(btn);
    }
    refresh();
  }

  // 首页：目录（按十年分组）、进度、我的词本
  function mountHome() {
    const toc = document.getElementById("toc");
    if (!toc) return;
    for (const b of BOOK) {
      const pages = PAGES.filter((p) => p.ch === b.n);
      if (b.n) toc.append(h("li", { class: "chap" }, h("span", { class: "en" }, b.en), h("span", { class: "meta" }, [b.age, b.place].filter(Boolean).join(" · "))));
      for (const p of pages) {
        const ready = READY.has(p.id);
        toc.append(h("li", {}, h("a", Object.assign({ class: (isDone(p.id) ? "done " : "") + (ready ? "" : "todo") }, ready ? { href: href(p.id) } : {}),
          h("span", { class: "n" }, isDone(p.id) ? "✓" : p.ch === 0 ? "序" : p.part),
          h("span", { class: "t" }, ready ? p.t : `${p.y}`),
          h("span", { class: "b" }, ...(ready ? badges(p) : [h("span", { class: "badge" }, "待写")])),
          ready && p.d ? h("span", { class: "d" }, p.d) : null)));
      }
    }
    const doneN = PAGES.filter((p) => isDone(p.id)).length;
    const pr = document.getElementById("progress");
    if (pr) pr.append(h("div", { class: "progress" }, Object.assign(h("i"), { style: `width:${(100 * doneN) / PAGES.length}%` })), h("p", { class: "lede" }, `已读完 ${doneN} / ${PAGES.length} 页`));
    const wb = document.getElementById("wordbook");
    if (wb) {
      const keys = LS.keys("ml-star-").sort();
      if (!keys.length) wb.append(h("p", { class: "lede" }, "还是空的。在章节页里点词条右边的「记下」，它们会汇总到这里。"));
      for (const k of keys) {
        const m = k.match(/^ml-star-(\d\d[a-z]?)-(.*)$/); if (!m) continue;
        const p = PAGES.find((x) => x.id === m[1]); if (!p) continue;
        let zh = ""; try { zh = JSON.parse(LS.get(k)).zh; } catch {}
        wb.append(h("div", {}, h("b", {}, m[2]), h("span", {}, zh), h("a", { href: href(p.id) }, label(p))));
      }
    }
  }

  document.addEventListener("DOMContentLoaded", () => { mountChrome(); wireEntries(); mountHome(); });
  // 跨设备同步：模块在首页仓库里（/_home/sync.js），所有教程站共用。只在线上加载；本地预览要联调时设 localStorage["sync-dev"] = "1"
  try { if (location.hostname === "t.miaowuao.cn" || localStorage.getItem("sync-dev")) document.head.append(Object.assign(document.createElement("script"), { src: "/_home/sync.js" })); } catch (e) {}
  window.ML = { h, LS, ROOT, href, label, isDone };
})();
