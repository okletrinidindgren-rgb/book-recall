[English](README.md) | [中文](README_CN.md)

# 📖 book-recall

无剧透的 AI 阅读伴侣，基于 [OpenClaw](https://github.com/openclaw/openclaw)。解析书籍章节、构建本地轻量索引、按需回忆剧情——绝不剧透后续内容。

## 工作原理

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│   解析   │────▶│  建索引  │────▶│  回忆    │
│ EPUB/PDF │     │  (本地)  │     │ (1次调用)│
│   TXT    │     │  零开销  │     │  按需    │
└──────────┘     └──────────┘     └──────────┘
```

1. **解析** — 将书拆分为章节（`book_data.json`）
2. **建索引** — 本地提取人物、地点、章节概要——零 AI 开销，秒级完成
3. **回忆** — 当你问"第 N 章之前讲了什么？"，AI 读取压缩索引 + 最近几章原文，**一次调用**生成完整回忆

## 快速开始

```bash
# 1. 解析书籍
python3 scripts/parse_book.py mybook.txt --output ./books/mybook/ --title "书名"

# 2. 建索引（本地运行，无需 AI）
python3 scripts/build_index.py ./books/mybook/book_data.json

# 3. 问："我读到第50章了，前面讲了什么？"
```

## 特性

- 📚 **EPUB / PDF / TXT** — 开箱支持三种格式
- 🔍 **本地人物与地点提取** — NLP 启发式规则，不消耗 AI token
- 🚫 **严格防剧透** — 绝不引用超出阅读进度的任何内容
- 💰 **每次回忆仅一次 AI 调用** — 压缩索引将 token 用量降到最低
- 🌍 **多语言** — 摘要跟随原文语言
- 📊 **~18% 压缩率** — 千章小说的索引仅 ~200KB

## 防剧透规则

- 超出你声明的章节位置的内容**绝不**会被加载或引用
- 问"X 会不会发生？" → *"回答这个就剧透了，继续读吧！📖"*
- 有疑虑时，系统宁可多防一层

## 依赖

- Python 3.10+
- EPUB：`pip3 install ebooklib beautifulsoup4 lxml`
- PDF：`pdftotext`（来自 `poppler-utils` / `brew install poppler`）

## 协议

MIT
