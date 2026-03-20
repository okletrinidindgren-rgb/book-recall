[English](README.md) | [中文](README_CN.md)

# 📖 book-recall

无剧透的 AI 阅读伴侣（OpenClaw 技能）。解析书籍章节，构建本地轻量索引，按需回忆剧情——绝不剧透后续内容。

## 架构：本地优先，AI 最小化

| 步骤 | AI 开销 | 功能 |
|------|---------|------|
| **解析** | 0 | 将 EPUB/PDF/TXT 拆分为章节 → `book_data.json` |
| **建索引** | 0 | 提取人物、地点、章节摘要 → `book_index.json` |
| **回忆** | **1次调用** | 读取压缩索引 + 最近几章原文，一次生成回忆 |

**旧方案：** 每章预生成摘要 = 100章需要100次 AI 调用。
**新方案：** 本地索引 + 按需回忆 = 不管多少章都只需1次 AI 调用。

## 快速开始

```bash
# 1. 解析书籍
python3 scripts/parse_book.py mybook.txt --output ./books/mybook/ --title "书名"

# 2. 建索引（零 AI 开销，秒级完成）
python3 scripts/build_index.py ./books/mybook/book_data.json

# 3. 问 AI："我读到第50章了，前面讲了什么？"
#    → AI 读索引 + 最近几章，一次性生成回忆
```

## 特性

- 📚 支持 **EPUB**、**PDF**、**TXT** 格式
- 🔍 本地 NLP 提取：人物名、地点、章节概要
- 🚫 **严格防剧透**：绝不引用超出阅读进度的内容
- 💰 **极低 AI 开销**：每次回忆只需一次调用
- 🌍 **多语言**：摘要跟随原文语言
- 📊 索引压缩率：原文件大小的 ~19%

## 依赖

- Python 3.10+
- EPUB：`pip3 install ebooklib beautifulsoup4 lxml`
- PDF：`pdftotext`（来自 `poppler-utils`）

## 协议

MIT
