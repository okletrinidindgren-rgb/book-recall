---
name: book-recall
description: >
  Reading companion that helps recall previous plot without spoilers.
  Import an EPUB/PDF/TXT book, parse it by chapters, build a local
  index (zero AI cost), then recall plot on demand using compressed
  context + minimal AI calls.
  Use when: (1) user sends a book file and wants reading support,
  (2) user says "I'm on chapter N, what happened before?",
  (3) user asks about characters or plot points from earlier chapters,
  (4) user mentions "book recall", "reading companion", "recap",
  "what happened so far", "帮我回忆", "读到第几章了".
---

# book-recall

Spoiler-free reading companion. Parse → Index → Recall.

## Architecture

| Step | AI Cost | Script |
|------|---------|--------|
| Parse book → chapters | 0 | `scripts/parse_book.py` |
| Build index (characters, locations, briefs) | 0 | `scripts/build_index.py` |
| Generate recall prompt | 0 | `scripts/recall.py` |
| Recall (send prompt to AI) | **1 call** | Agent sends prompt |

**Language support:** Auto-detects Chinese / English / mixed. Character and location extraction works for both.

## Workflow

### 1. Parse

```bash
python3 scripts/parse_book.py <file> --output <dir> [--title "Title"]
```

- Supports `.epub`, `.pdf`, `.txt`
- Output: `<dir>/book_data.json`
- EPUB deps: `pip3 install ebooklib beautifulsoup4 lxml`
- PDF deps: `pdftotext` (poppler)
- If filename is garbled, script warns. **Always ask user for correct title.**

### 2. Index (zero cost)

```bash
python3 scripts/build_index.py <dir>/book_data.json
```

- Output: `<dir>/book_index.json` (~19% of original)
- Extracts per chapter: brief, first/last line, characters, locations
- Detects language automatically
- Chinese: surname-based + context patterns + nickname extraction
- English: dialogue attribution + possessives + title prefixes (Mr./Dr./etc.)

### 3. Recall

```bash
# Full AI prompt (send output to model)
python3 scripts/recall.py <dir>/book_data.json --chapter <N> [--recent 3]

# Quick context summary (no AI needed)
python3 scripts/recall.py <dir>/book_data.json --chapter <N> --format context
```

**Prompt mode** (`--format prompt`, default): Builds a structured prompt with:
- Compressed timeline from index (all chapters 1..N)
- Full text of last K chapters (default 3) for detail
- Character roster + locations up to chapter N
- Anti-spoiler instructions
- Task instructions for the AI

**Context mode** (`--format context`): Prints index-only summary, no AI call needed.

The agent should run `recall.py`, capture the output, and send it as a prompt to generate the recall.

### 4. Optional: Pre-summarize chapters

```bash
python3 scripts/summarize_chapters.py <dir>/book_data.json --prompt-for <N>
```

This is **optional**. Use only when the user wants persistent per-chapter summaries stored in `book_data.json`. Not needed for the standard recall flow.

## Anti-Spoiler Rules (Critical)

1. **NEVER** load or reference content beyond the user's stated chapter position
2. **NEVER** hint at future developments
3. "Will X happen?" → "Can't answer without spoiling. Keep reading! 📖"
4. When uncertain, err on the side of caution

## File Structure

```
books/<name>/
├── book_data.json       # Full chapter text (large)
└── book_index.json      # Lightweight index (~19%)
```

## Recall Token Budget

| Book size | Index | Recent 3ch | Total prompt |
|-----------|-------|------------|-------------|
| 100 chapters | ~3K tokens | ~5K tokens | ~8K |
| 500 chapters | ~12K tokens | ~5K tokens | ~17K |
| 1000 chapters | ~22K tokens | ~5K tokens | ~27K |

For 500+ chapters, consider `--recent 2` to stay under 20K tokens.
