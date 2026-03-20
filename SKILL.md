---
name: book-recall
description: >
  Reading companion that helps recall previous plot without spoilers.
  Import an EPUB/PDF/TXT book, parse it by chapters, generate detailed
  per-chapter summaries with character tracking, and recall everything
  up to your current reading position — never spoiling what's ahead.
  Use when: (1) user sends a book file and wants reading support,
  (2) user says "I'm on chapter N, what happened before?",
  (3) user asks about characters or plot points from earlier chapters,
  (4) user mentions "book recall", "reading companion", "recap",
  "what happened so far", "帮我回忆", "读到第几章了".
---

# book-recall

A spoiler-free reading companion. Parse books into chapters, generate detailed summaries, track characters, and recall previous plot on demand.

## Workflow

### 1. Import a Book

When the user provides a book file (EPUB, PDF, or TXT):

```bash
python3 scripts/parse_book.py <file_path> --output <output_dir> [--title "Book Title"]
```

- Default output dir: `~/.openclaw/workspace/books/<book_name>/`
- Produces `book_data.json` with chapter-segmented text
- Print the chapter list so the user can confirm parsing quality

**Dependencies** (install if missing):
- EPUB: `pip3 install ebooklib beautifulsoup4 lxml`
- PDF: `pdftotext` (from `poppler-utils` / `brew install poppler`)

### 2. Generate Chapter Summaries

Summarize chapters **sequentially** up to the user's current reading position. Never summarize ahead.

**For each unsummarized chapter:**

1. Get the prompt:
   ```bash
   python3 scripts/summarize_chapters.py <book_data.json> --prompt-for <N>
   ```
2. The prompt includes the chapter text + all previous summaries for context. Send this to the AI model.
3. The AI returns a JSON with `summary`, `key_events`, `new_characters`.
4. Save the result:
   ```bash
   python3 scripts/summarize_chapters.py <book_data.json> --save-summary <N> --summary-json '<json_string>'
   ```

**Important:** Process chapters one at a time, in order. Each summary builds on previous ones.

**Batch shortcut** — to see all pending prompts up to chapter N:
```bash
python3 scripts/summarize_chapters.py <book_data.json> --up-to <N>
```

### 3. Recall (The Core Feature)

When the user says "I'm on chapter N" or "帮我回忆前面的剧情":

```bash
python3 scripts/summarize_chapters.py <book_data.json> --recall <N>
```

This outputs:
- **Character roster** — all characters met so far with descriptions
- **Key events timeline** — chronological bullet points tagged by chapter
- **Chapter-by-chapter summaries** — detailed recap

Present this to the user in a readable format. **Never include anything from chapters after N.**

### 4. Check Status

```bash
python3 scripts/summarize_chapters.py <book_data.json>
```

Shows: book title, total chapters, words, current position, summarization progress, character count.

## Anti-Spoiler Rules (CRITICAL)

1. **NEVER** reference content from chapters beyond the user's stated position.
2. **NEVER** hint at future plot developments, even vaguely.
3. If the user asks "will X happen?" — respond: "I can't answer that without spoiling. Keep reading! 📖"
4. Summaries are generated **only** for chapters ≤ current position.
5. When uncertain whether something is a spoiler, err on the side of caution.

## Summary Quality Guidelines

Each chapter summary should include:
- **Plot progression** — what happened, in order
- **Character actions & motivations** — what each character did and why
- **Emotional beats** — mood, tension, revelations
- **Important dialogue** — key quotes or conversations (paraphrased)
- **Setting changes** — new locations or time jumps

Summaries follow the **original text's language** (English book → English summary, 中文书 → 中文摘要).

## File Structure

```
~/.openclaw/workspace/books/<book_name>/
├── book_data.json       # Parsed chapters + summaries + characters
└── <original_file>      # Copy of the source book (optional)
```

## Limitations

- Large books (50+ chapters) may take time to summarize — do it incrementally as the user reads.
- PDF parsing quality depends on the PDF structure; scanned PDFs need OCR.
- Chapter detection uses heuristics; user may need to confirm chapter boundaries.
- DRM-protected files are not supported.
