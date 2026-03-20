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
# Recommended: summary mode (index-based AI prompt, no raw text)
python3 scripts/recall.py <dir>/book_data.json --chapter <N> --format summary

# Full AI prompt with recent chapter text (high token cost)
python3 scripts/recall.py <dir>/book_data.json --chapter <N> --format prompt [--recent 3]

# Quick context summary (no AI needed, just prints index data)
python3 scripts/recall.py <dir>/book_data.json --chapter <N> --format context
```

**Three formats:**

| Format | Default | AI Call | Includes Raw Text | Token Cost |
|--------|---------|--------|-------------------|------------|
| `summary` | ✅ Yes | 1 call | No (briefs only) | **Low** (~3-8K) |
| `prompt` | | 1 call | Yes (last K chapters) | **High** (~8-27K) |
| `context` | | None | No | **Zero** |

- **`summary`** (recommended): Builds an AI prompt from index data only — character roster, locations, chapter briefs. Best balance of quality and cost.
- **`prompt`**: Includes full text of recent chapters for maximum detail. Use for deep recall or when summary isn't detailed enough.
- **`context`**: Prints raw index data as plain text. No AI needed. Good for quick reference.

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

| Book size | Format | Index | Recent text | Total prompt |
|-----------|--------|-------|-------------|-------------|
| 100 chapters | summary | ~3K | 0 | **~3K** |
| 100 chapters | prompt | ~3K | ~5K | ~8K |
| 500 chapters | summary | ~8K | 0 | **~8K** |
| 500 chapters | prompt | ~12K | ~5K | ~17K |
| 1000 chapters | summary | ~15K | 0 | **~15K** |
| 1000 chapters | prompt | ~22K | ~5K | ~27K |

**Recommendation:** Use `summary` by default. Switch to `prompt` only when the reader needs granular detail about recent chapters.
