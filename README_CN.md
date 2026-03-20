[English](README.md) | [中文](README_CN.md)

# 📖 book-recall

为 [OpenClaw](https://github.com/openclaw/openclaw) 打造的无剧透 AI 阅读伴侣。将书籍解析为章节，在本地构建轻量索引，按需回忆剧情 —— 绝不剧透。

## 工作原理

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│   解析   │────▶│   索引   │────▶│ 回忆提示 │────▶│   AI    │
│ EPUB/PDF │     │ (本地)   │     │  (本地)  │     │ (1次调用)│
│   TXT    │     │  零成本  │     │  零成本  │     │  按需    │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
```

1. **解析** — 将书籍拆分为章节（`book_data.json`）
2. **索引** — 本地提取人物、地点、章节摘要 —— 零 AI 成本
3. **回忆提示** — 生成结构化提示词，包含压缩时间线 + 近几章全文
4. **AI 回忆** — 将提示词发送给 AI，生成完整的无剧透回顾

## 特性

- 📚 支持 **EPUB / PDF / TXT**
- 🌍 **中英文双语** — 自动语言检测，两种语言均有 NLP 提取
- 🔍 **智能人名提取** — 中文姓氏模式 + 英文对话归因、所有格、称谓前缀
- 📍 **地点提取** — 中文地名后缀 + 英文介词上下文
- 🚫 **严格防剧透** — 绝不引用阅读位置之后的内容
- 💰 **每次回忆仅 1 次 AI 调用** — 压缩索引将 token 用量降到最低（100章约 8K）
- 📊 **约 19% 压缩率** — 1000 章的书，索引只有约 200KB

## 快速开始

```bash
# 1. 解析书籍
python3 scripts/parse_book.py mybook.epub --output ./books/mybook/ --title "我的书"

# 2. 构建索引（本地运行，无需 AI）
python3 scripts/build_index.py ./books/mybook/book_data.json

# 3. 生成第 50 章的回忆提示
python3 scripts/recall.py ./books/mybook/book_data.json --chapter 50

# 4. 或获取快速上下文摘要（无需 AI）
python3 scripts/recall.py ./books/mybook/book_data.json --chapter 50 --format context
```

## 依赖

- Python 3.10+
- EPUB: `pip3 install ebooklib beautifulsoup4 lxml`
- PDF: `pdftotext`（来自 `poppler-utils` / `brew install poppler`）

## 许可证

MIT
