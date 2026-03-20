[English](README.md) | [中文](README_CN.md)

# 📖 book-recall

A spoiler-free AI reading companion for OpenClaw. Parse books into chapters, build lightweight local indexes, and recall plot on demand — without spoiling what's ahead.

## Architecture: Local-First, AI-Lite

| Step | AI Cost | What it does |
|------|---------|-------------|
| **Parse** | 0 | Split EPUB/PDF/TXT into chapters → `book_data.json` |
| **Index** | 0 | Extract characters, locations, briefs → `book_index.json` |
| **Recall** | **1 call** | Read compressed index + recent chapters, generate recall |

**Old approach:** Pre-summarize every chapter = 100 AI calls for 100 chapters.
**New approach:** Local index + on-demand recall = 1 AI call regardless of chapter count.

## Quick Start

```bash
# 1. Parse a book
python3 scripts/parse_book.py mybook.txt --output ./books/mybook/ --title "My Book"

# 2. Build index (zero AI cost, takes seconds)
python3 scripts/build_index.py ./books/mybook/book_data.json

# 3. Ask the AI: "I'm on chapter 50, what happened so far?"
#    → AI reads index + last few chapters, generates recall in one shot
```

## Features

- 📚 Supports **EPUB**, **PDF**, and **TXT** formats
- 🔍 Local NLP extraction: character names, locations, chapter briefs
- 🚫 **Strict anti-spoiler**: never references content beyond your reading position
- 💰 **Minimal AI cost**: one call per recall, not one per chapter
- 🌍 **Multi-language**: summaries follow the original text's language
- 📊 Compression: ~19% of original file size for the index

## How Recall Works

When you say "I'm on chapter 100":

1. Load the lightweight index (~200KB for a 1000-chapter book)
2. Gather chapter titles, character appearances, briefs up to your position
3. Load full text of only the last 3-5 chapters
4. Send ONE prompt to AI → get character roster, plot arcs, detailed recent summary

## Dependencies

- Python 3.10+
- EPUB support: `pip3 install ebooklib beautifulsoup4 lxml`
- PDF support: `pdftotext` (from `poppler-utils`)

## License

MIT
