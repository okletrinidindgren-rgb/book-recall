[中文](README.md) | [English](README_EN.md)

<div align="center">

# 📖 book-recall

**无剧透 AI 阅读伴侣**

*解析书籍 · 本地索引 · 按需回忆 · 一次 AI 调用*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](https://python.org)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-purple.svg)](https://github.com/openclaw/openclaw)

</div>

---

## 💡 为什么需要它？

读网文/长篇小说时，隔几天再看就忘了前面的剧情。直接问 AI "帮我回忆"？要么把整本书喂进去（烧 token），要么 AI 乱编（没读过你的书）。

**book-recall 的方案：**

```
         零 AI 成本                    零 AI 成本                    零 AI 成本                   仅 1 次调用
  ┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐
  │    📄 解析      │  ──────▶ │    🔍 索引      │  ──────▶ │    📝 提示词    │  ──────▶ │    🤖 回忆      │
  │   EPUB/PDF/TXT  │          │  人物·地点·摘要  │          │ 压缩时间线+近章 │          │  完整剧情回顾   │
  └─────────────────┘          └─────────────────┘          └─────────────────┘          └─────────────────┘
```

> 100 章的书，传统方案要 100 次 AI 调用 + 50 万 token。我们只要 **1 次调用 + 8K token**。

---

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🌍 **中英文双语** | 自动语言检测，中文姓氏模式 + 英文对话归因等多种 NLP 启发式 |
| 📚 **三格式支持** | EPUB / PDF / TXT，智能章节分割 |
| 🔍 **本地人物提取** | 中文：姓氏 + 上下文 + 昵称。英文：对话归因 + 所有格 + 称谓前缀 |
| 📍 **地点提取** | 中文地名后缀 + 英文介词上下文 |
| 🚫 **严格防剧透** | 绝不引用阅读位置之后的任何内容 |
| 💰 **极低成本** | 索引全程本地零成本，回忆仅 1 次 AI 调用 |
| 📊 **高压缩率** | 索引仅原文 ~19%，1000 章的书索引只有 ~200KB |

---

## 🚀 快速开始

### 安装依赖

```bash
# EPUB 解析
pip3 install ebooklib beautifulsoup4 lxml

# PDF 解析（二选一）
brew install poppler        # macOS
sudo apt install poppler-utils  # Linux
```

### 三步使用

```bash
# 1️⃣ 解析书籍 → 章节 JSON
python3 scripts/parse_book.py 三体.epub --output ./books/santi/ --title "三体"

# 2️⃣ 构建索引（本地运行，零 AI 成本）
python3 scripts/build_index.py ./books/santi/book_data.json

# 3️⃣ 我读到第 30 章了，帮我回忆！
python3 scripts/recall.py ./books/santi/book_data.json --chapter 30
```

---

## 📊 Token 成本对比

| 方案 | 100 章 | 500 章 | 1000 章 |
|------|--------|--------|---------|
| ❌ 全文喂给 AI | ~500K tokens | ~2.5M tokens | ~5M tokens |
| ❌ 逐章预摘要 | 100 次调用 | 500 次调用 | 1000 次调用 |
| ✅ **book-recall** | **~8K tokens, 1 次调用** | **~17K tokens, 1 次调用** | **~27K tokens, 1 次调用** |

---

## 🛡️ 防剧透规则

这是阅读伴侣的生命线：

- ❌ 绝不加载或引用阅读位置之后的章节
- ❌ 绝不暗示未来剧情发展
- ✅ 问 "后面会怎样？" → *"不能说，会剧透的。继续读吧！📖"*

---

## 📁 文件结构

```
books/三体/
├── book_data.json       # 全文章节数据（较大）
└── book_index.json      # 轻量索引（~19%）
```

---

## 📖 详细文档

关于完整的工作流、脚本参数和高级用法，请参阅 [SKILL.md](SKILL.md)。

---

## 📄 许可证

[MIT](LICENSE)

---

<div align="center">

**读书不忘事，回忆不剧透。** 📚✨

</div>
