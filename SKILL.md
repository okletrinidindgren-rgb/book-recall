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

A spoiler-free reading companion. Parse books, build lightweight indexes locally, and recall plot on demand with minimal AI cost.

## Architecture: Local-First, AI-Lite

| Step | AI Cost | Description |
|------|---------|-------------|
| 1. Parse book | 0 | Split into chapters → `book_data.json` |
| 2. Build index | 0 | Extract characters, locations, brief per chapter → `book_index.json` |
| 3. Recall | **1 call** | Read index + recent chapters, generate recall in one shot |

**Key principle:** Scripts do the heavy lifting locally. AI is only invoked when the user asks for a recall.

## Workflow

### 1. Import a Book

```bash
python3 scripts/parse_book.py <file_path> --output <output_dir> [--title "Book Title"]
```

- Default output: `~/.openclaw/workspace/books/<book_name>/`
- Produces `book_data.json` with chapter-segmented text
- If filename is garbled, script warns and sets "Untitled". **Always ask user for correct title.**
- **Never guess or fabricate a book title or author.**

**Dependencies** (install if missing):
- EPUB: `pip3 install ebooklib beautifulsoup4 lxml`
- PDF: `pdftotext` (from `poppler-utils` / `brew install poppler`)

### 2. Build Index (Zero AI Cost)

```bash
python3 scripts/build_index.py <book_data.json>
```

Produces `book_index.json` (~19% of original size) containing per-chapter:
- `brief` — first 200 chars
- `first_line` / `last_line` — orientation markers
- `characters` — extracted character names
- `locations` — extracted place names

Plus global stats: top characters by frequency, top locations.

**Run this once after parsing.** Takes seconds even for 1000+ chapter books.

### 3. Recall (The Core Feature) — On Demand

When the user says "I'm on chapter N" or "帮我回忆":

**Strategy: Compressed context, single AI call.**

1. Load `book_index.json` (lightweight, ~200KB for 1000ch book)
2. From the index, gather for chapters 1 to N:
   - Chapter titles + briefs (compressed timeline)
   - Characters mentioned per chapter
   - Global character frequency up to chapter N
3. Load **full text** of the last 3-5 chapters only (for detail)
4. Send ONE prompt to AI with all the above, asking for:
   - Character roster with descriptions
   - Key plot arcs / game arcs
   - Detailed summary of recent chapters
   - Brief timeline of earlier chapters
5. Present the recall to the user

**Token budget:** ~5-10K input tokens for index + recent chapters, vs 200K+ for all chapters.

### 4. What If User Asks About a Specific Earlier Chapter?

Load that chapter's full text from `book_data.json` + surrounding index context.
Send ONE prompt. No pre-computation needed.

## Anti-Spoiler Rules (CRITICAL)

1. **NEVER** reference content from chapters beyond the user's stated position.
2. **NEVER** hint at future plot developments, even vaguely.
3. If asked "will X happen?" → "I can't answer that without spoiling. Keep reading! 📖"
4. Only load/read chapters ≤ current position.
5. When uncertain, err on the side of caution.

## Summary Quality Guidelines

When generating recall, include:
- **Plot progression** — what happened, key games/arcs
- **Character roster** — who appeared, roles, relationships
- **Emotional beats** — tension, revelations, twists
- **Key dialogue** — important conversations (paraphrased)
- **Setting** — locations, world-building details

Summaries follow the **original text's language**.

## File Structure

```
~/.openclaw/workspace/books/<book_name>/
├── book_data.json       # Full chapter text (large)
├── book_index.json      # Lightweight index (small, ~19% of original)
```

## Cost Comparison

| Approach | Chapters | AI Calls | Tokens |
|----------|----------|----------|--------|
| ❌ Old: pre-summarize all | 100 | 100 | ~500K |
| ✅ New: index + on-demand | 100 | 1 | ~8K |

## Limitations

- Index character extraction uses heuristics — may miss some names or include noise
- PDF parsing depends on structure; scanned PDFs need OCR
- Chapter detection uses regex heuristics; user may need to confirm boundaries
- Very long recall ranges (500+ chapters) may need chunked prompts
