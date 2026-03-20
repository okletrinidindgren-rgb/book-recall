# book-recall 📖🧠

A spoiler-free AI reading companion. Never forget what happened in earlier chapters — without getting anything spoiled.

## The Problem

You're halfway through a long novel and can't remember who that character is, or what happened three chapters ago. You want to ask an AI, but you're afraid of spoilers.

## The Solution

**book-recall** parses your book into chapters, generates detailed summaries as you read, and gives you a full recap up to your current position — with **zero spoilers** from chapters you haven't read yet.

## Features

- 📚 **Import books** — EPUB, PDF, TXT support
- 📝 **Chapter summaries** — detailed, spoiler-free, in the book's original language
- 👤 **Character tracking** — automatically tracks who's who and when they appear
- 📅 **Event timeline** — key events tagged by chapter
- 🚫 **Anti-spoiler** — strict rules ensure nothing from future chapters leaks
- 🔖 **Progress tracking** — knows where you left off

## Quick Start

### 1. Parse a book

```bash
python3 scripts/parse_book.py my_book.epub --output ./my_book/
```

### 2. Generate summaries (up to chapter N)

```bash
# Get the AI prompt for a chapter
python3 scripts/summarize_chapters.py ./my_book/book_data.json --prompt-for 1

# Save the AI's response
python3 scripts/summarize_chapters.py ./my_book/book_data.json \
  --save-summary 1 \
  --summary-json '{"summary":"...","key_events":["..."],"new_characters":[{"name":"...","description":"..."}]}'
```

### 3. Recall everything up to your position

```bash
python3 scripts/summarize_chapters.py ./my_book/book_data.json --recall 5
```

Output includes:
- Characters you've met
- Key events timeline
- Chapter-by-chapter summaries

### 4. Check status

```bash
python3 scripts/summarize_chapters.py ./my_book/book_data.json
```

## Dependencies

- Python 3.10+
- EPUB: `pip3 install ebooklib beautifulsoup4 lxml`
- PDF: `pdftotext` (from `poppler-utils` / `brew install poppler`)

## Designed for AI Agents

This is an [OpenClaw](https://github.com/openclaw/openclaw) skill. Install it and your AI agent will automatically use it when you send a book file and ask for reading help.

## License

MIT
