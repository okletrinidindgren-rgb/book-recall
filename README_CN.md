# book-recall 📖🧠

无剧透的 AI 阅读伴侣。帮你回忆之前的剧情，绝不泄露后面的内容。

## 痛点

读长篇小说读到一半，忘了前面某个角色是谁、三章前发生了什么。想问 AI，又怕被剧透。

## 解决方案

**book-recall** 把你的电子书按章节切分，随着你的阅读进度逐章生成详细摘要，随时帮你回顾到当前位置的全部剧情——**绝对零剧透**。

## 功能特性

- 📚 **导入书籍** — 支持 EPUB、PDF、TXT 格式
- 📝 **章节摘要** — 详细、无剧透、跟随原文语言
- 👤 **角色追踪** — 自动记录人物关系，标注首次出场章节
- 📅 **事件时间线** — 关键事件按章节排列
- 🚫 **防剧透机制** — 严格保证不泄露未读章节的任何信息
- 🔖 **阅读进度** — 记住你读到哪里了

## 快速上手

### 1. 解析书籍

```bash
python3 scripts/parse_book.py 我的小说.epub --output ./我的小说/
```

### 2. 生成摘要（到第 N 章）

```bash
# 获取某一章的 AI 提示词
python3 scripts/summarize_chapters.py ./我的小说/book_data.json --prompt-for 1

# 保存 AI 返回的摘要
python3 scripts/summarize_chapters.py ./我的小说/book_data.json \
  --save-summary 1 \
  --summary-json '{"summary":"...","key_events":["..."],"new_characters":[{"name":"...","description":"..."}]}'
```

### 3. 回忆剧情

```bash
python3 scripts/summarize_chapters.py ./我的小说/book_data.json --recall 5
```

输出包含：
- 🧑‍🤝‍🧑 你遇到过的所有角色
- 📋 关键事件时间线
- 📖 逐章剧情摘要

### 4. 查看状态

```bash
python3 scripts/summarize_chapters.py ./我的小说/book_data.json
```

## 依赖

- Python 3.10+
- EPUB 支持：`pip3 install ebooklib beautifulsoup4 lxml`
- PDF 支持：`pdftotext`（`brew install poppler` 或 `apt install poppler-utils`）

## 为 AI Agent 设计

这是一个 [OpenClaw](https://github.com/openclaw/openclaw) skill。安装后，你只需要把电子书发给 AI，说"我读到第几章了"，它就会帮你回忆之前的剧情。

## 许可证

MIT
