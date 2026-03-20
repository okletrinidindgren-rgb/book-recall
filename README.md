[English](README.md) | [中文](README_CN.md)

# 📖 book-recall

A spoiler-free AI reading companion for [OpenClaw](https://github.com/openclaw/openclaw). Parse books into chapters, build lightweight local indexes, and recall plot on demand — never spoiling what's ahead.

## How It Works

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Parse   │────▶│  Index   │────▶│  Recall  │
│ EPUB/PDF │     │  (local) │     │ (1 call) │
│   TXT    │     │  0 cost  │     │ on demand│
└──────────┘     └──────────┘     └──────────┘
```

1. **Parse** — Split your book into chapters (`book_data.json`)
2. **Index** — Extract characters, locations, chapter briefs locally — zero AI cost, runs in seconds
3. **Recall** — When you ask "what happened before chapter N?", the AI reads the compressed index + last few chapters and generates a full recall in **one single call**

## Quick Start

```bash
# 1. Parse a book
python3 scripts/parse_book.py mybook.txt --output ./books/mybook/ --title "My Book"

# 2. Build index (local, no AI needed)
python3 scripts/build_index.py ./books/mybook/book_data.json

# 3. Ask: "I'm on chapter 50, what happened so far?"
```

## Features

- 📚 **EPUB / PDF / TXT** — three formats supported out of the box
- 🔍 **Local character & location extraction** — NLP heuristics, no AI tokens burned
- 🚫 **Strict anti-spoiler** — never references anything beyond your reading position
- 💰 **One AI call per recall** — compressed index keeps token usage minimal
- 🌍 **Multi-language** — summaries follow the original text's language
- 📊 **~18% compression** — a 1000-chapter book's index fits in ~200KB

## Anti-Spoiler Rules

- Content beyond your stated chapter position is **never** loaded or referenced
- Asking "will X happen?" gets: *"I can't answer that without spoiling. Keep reading! 📖"*
- When in doubt, the system errs on the side of caution

## Dependencies

- Python 3.10+
- EPUB: `pip3 install ebooklib beautifulsoup4 lxml`
- PDF: `pdftotext` (from `poppler-utils` / `brew install poppler`)

## License

MIT
