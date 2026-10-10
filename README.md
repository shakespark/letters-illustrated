# A Man of Letters · 英文伴读

陪读者在 Kindle 上读英文原版 *A Man of Letters*（Thomas Sowell, 2007）。这是一本书信集：1960–2006 年的两百六十多封信，按十年分成五部分。
每页对应几年的信：这几年在做什么、收信人和提到的人、信件地图、作者默认读者知道的背景、和回忆录 *A Personal Odyssey* 的对照、
这一版电子书的错字、按出现顺序排的词与短语、几道理解检查题。本站没有译文，不替代原书。

线上地址：https://t.miaowuao.cn/letters/ 　姊妹站：[A Personal Odyssey · 英文伴读](https://t.miaowuao.cn/odyssey/)（`~/a_personal_odyssey`）

## 目录结构

- `index.html`：首页（怎么用、目录、阅读进度、我的词本）
- `chapters/<id>.html`：`00` 开读之前；正文按十年编号（`01` = 1960s … `05` = 2000s），每个十年按年份拆成 `01a` `01b`… 共 19 页
- `assets/`：共享样式 `style.css`、脚本 `ml.js`、目录数据 `chapters.js`、图片 `img/`（出处见 `img/CREDITS.md`）
- `tools/`：`extract.py` 提取原书文本、`fetch_img.py` 取图、`reuse_img.py` 复用 Odyssey 伴读已有的照片、`lint.py` 结构检查、
  `overlap.py` 与原书的重合检查、`check.mjs` 浏览器检查（后三个的通用部分在 `~/tutorials-deploy/scripts/`）
- `AUTHORING.md`：章节页编写规范（公共部分见 `~/tutorials-deploy/AUTHORING-COMMON.md`）
- `source/`：原书材料，只在本机，不入库、不部署

localStorage 键的前缀是 `ml-`（`ml-done-<页 id>`、`ml-star-<页 id>-<词条>`、`ml-theme`）。

## 这本书特有的做法

- **Kindle 版是扫描识别的。** `source/text/` 里的错字照原样保留，词条的定位片段照屏幕上的字抄，读者才搜得到；每页有一张「这一版的错字」。
  原书做成图片的脚注和信头整理在 `source/notes/images.md`。
- **和 Odyssey 伴读互相链接。** 每页的「Odyssey 里讲过这一段」链到 `/odyssey/chapters/<页 id>.html`，`lint.py` 会对照那边的目录检查页 id。
- **星号隐去的收信人不猜；只有名没有姓的私人朋友不查、不配照片。**

## 版权

原书版权归作者和出版方。本站不翻译、不转述原书，每页直接引用不超过两处、每处不超过 25 个英文单词。
照片来自维基共享资源，授权为公有领域或 CC BY / CC BY-SA，逐张登记在 `assets/img/CREDITS.md`；示意图是本站自己画的。

## 改完之后

```sh
python3 tools/lint.py chapters/*.html
python3 tools/overlap.py chapters/*.html index.html
node tools/check.mjs
```
推送到 `main` 即自动部署（见 `.github/workflows/deploy.yml`，部署方式见 `~/tutorials-deploy`）。
