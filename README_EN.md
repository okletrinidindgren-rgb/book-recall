[中文](README.md) | [English](README_EN.md)

<div align="center">

# 📖 book-recall

**Spoiler-Free AI Reading Companion**

*Parse books · Local index · On-demand recall · One AI call*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](https://python.org)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-purple.svg)](https://github.com/openclaw/openclaw)

</div>

---

## 💡 Why?

Reading a long novel and forgot what happened 3 days ago? Feeding the entire book to AI burns tokens. Asking without context gets hallucinations.

**book-recall's approach:**

```
        Zero AI cost                   Zero AI cost                   Zero AI cost                  Only 1 call
  ┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐
  │    📄 Parse     │  ──────▶ │    🔍 Index     │  ──────▶ │    📝 Prompt    │  ──────▶ │    🤖 Recall    │
  │   EPUB/PDF/TXT  │          │ Chars·Locs·Brief│          │Timeline+Recent  │          │  Full recap     │
  └─────────────────┘          └─────────────────┘          └─────────────────┘          └─────────────────┘
```

> A 100-chapter book: traditional approach = 100 AI calls + 500K tokens. We need **1 call + 8K tokens**.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🌍 **Chinese + English** | Auto language detection with NLP heuristics for both languages |
| 📚 **Three formats** | EPUB / PDF / TXT with smart chapter splitting |
| 🔍 **Local character extraction** | Chinese: surname + context + nicknames. English: dialogue attribution + possessives + title prefixes |
| 📍 **Location extraction** | Chinese location suffixes + English preposition context |
| 🚫 **Strict anti-spoiler** | Never references content beyond your reading position |
| 💰 **Minimal cost** | Indexing is 100% local, recall needs only 1 AI call |
| 📊 **High compression** | Index is ~19% of original, ~200KB for a 1000-chapter book |

---

## 🚀 Quick Start

### Install Dependencies

```bash
# EPUB parsing
pip3 install ebooklib beautifulsoup4 lxml

# PDF parsing (pick one)
brew install poppler            # macOS
sudo apt install poppler-utils  # Linux
```

### Three Steps

```bash
# 1️⃣ Parse book → chapter JSON
python3 scripts/parse_book.py mybook.epub --output ./books/mybook/ --title "My Book"

# 2️⃣ Build index (local, zero AI cost)
python3 scripts/build_index.py ./books/mybook/book_data.json

# 3️⃣ I'm on chapter 30, what happened so far?
python3 scripts/recall.py ./books/mybook/book_data.json --chapter 30
```

---

## 📊 Token Cost Comparison

| Approach | 100 chapters | 500 chapters | 1000 chapters |
|----------|-------------|-------------|--------------|
| ❌ Full text to AI | ~500K tokens | ~2.5M tokens | ~5M tokens |
| ❌ Pre-summarize all | 100 AI calls | 500 AI calls | 1000 AI calls |
| ✅ **book-recall** | **~8K tokens, 1 call** | **~17K tokens, 1 call** | **~27K tokens, 1 call** |

---

## 📖 Documentation

For complete workflow, script parameters, and advanced usage, see [SKILL.md](SKILL.md).

---

## 📄 License

[MIT](LICENSE)

---

<div align="center">

**Never forget the plot. Never get spoiled.** 📚✨

</div>
