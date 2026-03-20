#!/usr/bin/env python3
"""Generate a recall prompt from book_index.json + book_data.json.

Given a reading position (chapter N), produces a structured prompt that includes:
  - Compressed timeline from index (chapters 1..N)
  - Full text of last K chapters for detail
  - Character roster + locations
  - Anti-spoiler instructions

The output is a prompt string ready to send to an AI model.

Usage:
    python3 recall.py <book_data.json> --chapter <N> [--recent 3] [--format prompt|context]
"""

import argparse
import json
import os
import sys


def load_json(path: str) -> dict:
    with open(os.path.expanduser(path), "r", encoding="utf-8") as f:
        return json.load(f)


def build_recall_prompt(
    book_data: dict,
    book_index: dict,
    current_chapter: int,
    recent_count: int = 3,
) -> str:
    """Build a recall prompt for the AI model."""

    title = book_index.get("title", book_data.get("title", "Untitled"))
    lang = book_index.get("language", "zh")
    total = book_index.get("total_chapters", len(book_data.get("chapters", [])))

    # ── Character roster (up to current chapter) ──
    # Collect characters from index chapters up to N
    char_freq = {}
    for ch_idx in book_index.get("chapters", []):
        if ch_idx["number"] > current_chapter:
            break
        for name in ch_idx.get("characters", []):
            char_freq[name] = char_freq.get(name, 0) + 1

    top_characters = sorted(char_freq.items(), key=lambda x: -x[1])[:30]

    # ── Location roster ──
    loc_freq = {}
    for ch_idx in book_index.get("chapters", []):
        if ch_idx["number"] > current_chapter:
            break
        for loc in ch_idx.get("locations", []):
            loc_freq[loc] = loc_freq.get(loc, 0) + 1

    top_locations = sorted(loc_freq.items(), key=lambda x: -x[1])[:15]

    # ── Compressed timeline (from index) ──
    timeline_lines = []
    for ch_idx in book_index.get("chapters", []):
        if ch_idx["number"] > current_chapter:
            break
        chars_str = ", ".join(ch_idx.get("characters", [])[:5])
        timeline_lines.append(
            f"Ch.{ch_idx['number']} [{ch_idx['title']}] "
            f"({ch_idx.get('word_count', '?')} words) — "
            f"{ch_idx.get('brief', '')[:120]}... "
            f"[Characters: {chars_str}]"
        )

    # ── Full text of recent chapters ──
    recent_start = max(1, current_chapter - recent_count + 1)
    recent_texts = []
    for ch in book_data.get("chapters", []):
        if ch["number"] < recent_start or ch["number"] > current_chapter:
            continue
        recent_texts.append(
            f"### Chapter {ch['number']}: {ch['title']}\n\n{ch['text']}"
        )

    # ── Build prompt ──
    lang_instruction = {
        "zh": "请用中文回复。",
        "en": "Reply in English.",
        "mixed": "Reply in the same language as the book's primary text.",
    }.get(lang, "Reply in the same language as the book.")

    prompt = f"""You are a spoiler-free reading companion for "{title}".
The reader is currently at **Chapter {current_chapter}** of {total}.

**CRITICAL ANTI-SPOILER RULES:**
1. NEVER reference content from chapters after Chapter {current_chapter}.
2. NEVER hint at future plot developments, even vaguely.
3. If the reader asks "will X happen?" → reply "I can't answer that without spoiling. Keep reading! 📖"

{lang_instruction}

---

## Character Roster (by frequency, chapters 1–{current_chapter})

{chr(10).join(f"- **{name}** (appeared in {count} chapters)" for name, count in top_characters)}

## Key Locations

{chr(10).join(f"- **{loc}** ({count} mentions)" for loc, count in top_locations)}

## Compressed Timeline (Chapters 1–{current_chapter})

{chr(10).join(timeline_lines)}

## Recent Chapters (Full Text)

{chr(10).join(recent_texts)}

---

**Task:** Based on the above, provide a comprehensive recall for the reader:
1. **Character guide** — who are the main characters, their roles and relationships
2. **Plot summary** — major arcs and story progression from Ch.1 to Ch.{current_chapter}
3. **Recent chapters detail** — detailed summary of what just happened
4. **Key mysteries/questions** — unresolved threads the reader should be tracking
5. **Emotional beats** — important revelations, twists, tension points

Keep the recall engaging and well-organized. Use headings and bullet points.
"""
    return prompt


def build_summary_prompt(
    book_index: dict,
    current_chapter: int,
) -> str:
    """Build a mid-weight AI prompt using only index data (no full chapter text).

    Includes: character roster, location roster, compressed timeline with briefs.
    Much cheaper than 'prompt' mode (no raw chapter text), but richer than 'context'.
    """
    title = book_index.get("title", "Untitled")
    lang = book_index.get("language", "zh")
    total = book_index.get("total_chapters", 0)

    # ── Characters ──
    char_freq = {}
    for ch_idx in book_index.get("chapters", []):
        if ch_idx["number"] > current_chapter:
            break
        for name in ch_idx.get("characters", []):
            char_freq[name] = char_freq.get(name, 0) + 1
    top_characters = sorted(char_freq.items(), key=lambda x: -x[1])[:25]

    # ── Locations ──
    loc_freq = {}
    for ch_idx in book_index.get("chapters", []):
        if ch_idx["number"] > current_chapter:
            break
        for loc in ch_idx.get("locations", []):
            loc_freq[loc] = loc_freq.get(loc, 0) + 1
    top_locations = sorted(loc_freq.items(), key=lambda x: -x[1])[:10]

    # ── Timeline (brief only, no full text) ──
    timeline_lines = []
    for ch_idx in book_index.get("chapters", []):
        if ch_idx["number"] > current_chapter:
            break
        chars_str = ", ".join(ch_idx.get("characters", [])[:4])
        brief = ch_idx.get("brief", "")[:150]
        timeline_lines.append(
            f"Ch.{ch_idx['number']} [{ch_idx['title']}] — {brief}... [{chars_str}]"
        )

    lang_instruction = {
        "zh": "请用中文回复。",
        "en": "Reply in English.",
        "mixed": "Reply in the same language as the book's primary text.",
    }.get(lang, "Reply in the same language as the book.")

    prompt = f"""You are a spoiler-free reading companion for "{title}".
The reader is at **Chapter {current_chapter}** of {total}.

**ANTI-SPOILER:** NEVER reference anything after Chapter {current_chapter}.

{lang_instruction}

## Characters (chapters 1–{current_chapter})

{chr(10).join(f"- **{name}** ({count} chapters)" for name, count in top_characters)}

## Locations

{chr(10).join(f"- **{loc}** ({count}x)" for loc, count in top_locations) if top_locations else "- (none extracted)"}

## Chapter Timeline

{chr(10).join(timeline_lines)}

---

**Task:** Provide a comprehensive, engaging recall:
1. **Character guide** — main characters, roles, relationships
2. **Plot summary** — major arcs from Ch.1 to Ch.{current_chapter}
3. **Recent events** — what happened in the last few chapters
4. **Unresolved mysteries** — threads the reader should track
5. **Key moments** — important revelations, twists, emotional beats

Use headings and bullet points. Be vivid but concise.
"""
    return prompt


def build_context_only(
    book_index: dict,
    current_chapter: int,
) -> str:
    """Build a lightweight context summary (no AI needed, just prints index data)."""
    title = book_index.get("title", "Untitled")
    lines = [f"📖 {title} — Reading at Chapter {current_chapter}\n"]

    lines.append("## Characters seen so far:")
    char_freq = {}
    for ch_idx in book_index.get("chapters", []):
        if ch_idx["number"] > current_chapter:
            break
        for name in ch_idx.get("characters", []):
            char_freq[name] = char_freq.get(name, 0) + 1
    for name, count in sorted(char_freq.items(), key=lambda x: -x[1])[:20]:
        lines.append(f"  - {name} ({count} chapters)")

    lines.append("\n## Chapter briefs:")
    for ch_idx in book_index.get("chapters", []):
        if ch_idx["number"] > current_chapter:
            break
        lines.append(f"  Ch.{ch_idx['number']} [{ch_idx['title']}]: {ch_idx.get('brief', '')[:80]}...")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate recall prompt for AI")
    parser.add_argument("book_data", help="Path to book_data.json")
    parser.add_argument("--chapter", "-c", type=int, required=True, help="Current reading position")
    parser.add_argument("--recent", "-r", type=int, default=3, help="Number of recent chapters to include in full (default: 3)")
    parser.add_argument("--format", "-f", choices=["prompt", "summary", "context"], default="summary",
                        help="Output format: 'prompt' (full AI prompt with recent chapter text), "
                             "'summary' (AI prompt from index only, no raw text — recommended), "
                             "or 'context' (index-only plain text, no AI needed)")
    parser.add_argument("--index", "-i", help="Path to book_index.json (default: same dir as book_data)")
    args = parser.parse_args()

    data_path = os.path.expanduser(args.book_data)
    book_data = load_json(data_path)

    index_path = args.index or os.path.join(os.path.dirname(data_path), "book_index.json")
    if not os.path.exists(index_path):
        print(f"Error: Index not found at {index_path}. Run build_index.py first.", file=sys.stderr)
        sys.exit(1)
    book_index = load_json(index_path)

    total = book_index.get("total_chapters", len(book_data.get("chapters", [])))
    if args.chapter < 1 or args.chapter > total:
        print(f"Error: Chapter {args.chapter} out of range (1–{total}).", file=sys.stderr)
        sys.exit(1)

    if args.format == "context":
        print(build_context_only(book_index, args.chapter))
    elif args.format == "summary":
        print(build_summary_prompt(book_index, args.chapter))
    else:
        print(build_recall_prompt(book_data, book_index, args.chapter, args.recent))


if __name__ == "__main__":
    main()
