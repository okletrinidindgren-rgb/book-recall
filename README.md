[English](README.md) | [中文](README_CN.md)

# 📖 book-recall

A spoiler-free AI reading companion for [OpenClaw](https://github.com/openclaw/openclaw). Parse books into chapters, build lightweight local indexes, and recall plot on demand — never spoiling what's ahead.

## How It Works

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Parse   │────▶│  Index   │────▶│  Recall  │────▶│    AI    │
│ EPUB/PDF │     │  (local) │     │  Prompt  │     │ (1 call) │
│   TXT    │     │  0 cost  │     │  0 cost  │     │ on demand│
└──────────┘     └──────────┘     └──────────┘     └──────────┘
```

1. **Parse** — Split your book into chapters (`book_data.json`)
2. **Index** — Extract characters, locations, chapter briefs locally — zero AI cost
3. **Recall Prompt** — Generate a structured prompt with compressed timeline + recent chapters
4. **AI Recall** — Send the prompt to AI for a comprehensive, spoiler-free recap

## Features

- 📚 **EPUB / PDF / TXT** support
- 🌍 **Chinese + English** — auto language detection, NLP extraction for both
- 🔍 **Smart character extraction** — Chinese surname patterns + English dialogue attribution, possessives, title prefixes
- 📍 **Location extraction** — Chinese location suffixes + English preposition context
- 🚫 **Strict anti-spoiler** — never references anything beyond your reading position
- 💰 **One AI call per recall** — compressed index keeps token usage minimal (~8K for 100 chapters)
- 📊 **~19% compression** — a 1000-chapter book's index fits in ~200KB

## Quick Start

```bash
# 1. Parse a book
python3 scripts/parse_book.py mybook.epub --output ./books/mybook/ --title "My Book"

# 2. Build index (local, no AI needed)
python3 scripts/build_index.py ./books/mybook/book_data.json

# 3. Generate recall prompt for chapter 50
python3 scripts/recall.py ./books/mybook/book_data.json --chapter 50

# 4. Or get a quick context summary (no AI)
python3 scripts/recall.py ./books/mybook/book_data.json --chapter 50 --format context
```

## Dependencies

- Python 3.10+
- EPUB: `pip3 install ebooklib beautifulsoup4 lxml`
- PDF: `pdftotext` (from `poppler-utils` / `brew install poppler`)

## License

MIT
