#!/usr/bin/env python3
"""
book-recall: Generate chapter summaries with character tracking.

Usage:
    python3 summarize_chapters.py <book_data.json> [--up-to <chapter_num>] [--force]

Reads book_data.json, generates summaries for chapters that don't have one yet.
Uses the AI agent (prints prompts to stdout for the agent to process).
"""

import argparse
import json
import os
import sys


def load_book(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_book(path: str, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_chapter_text(book: dict, chapter_num: int) -> str | None:
    for ch in book["chapters"]:
        if ch["number"] == chapter_num:
            return ch["text"]
    return None


def get_chapter(book: dict, chapter_num: int) -> dict | None:
    for ch in book["chapters"]:
        if ch["number"] == chapter_num:
            return ch
    return None


def build_summary_prompt(book: dict, chapter_num: int) -> str:
    """Build a prompt for AI to summarize a single chapter (no spoilers)."""
    chapter = get_chapter(book, chapter_num)
    if not chapter:
        return ""

    # Gather previous summaries for context
    prev_context = ""
    for ch in book["chapters"]:
        if ch["number"] >= chapter_num:
            break
        if ch.get("summary"):
            prev_context += f"\n### {ch['title']}\n{ch['summary']}\n"

    # Character roster so far
    char_info = ""
    if book.get("characters"):
        char_info = "\n**Known characters so far:**\n"
        for name, desc in book["characters"].items():
            char_info += f"- **{name}**: {desc}\n"

    prompt = f"""You are a reading companion assistant. Summarize the following chapter of "{book['title']}".

**CRITICAL RULES:**
1. Write the summary in the SAME LANGUAGE as the original text.
2. NEVER include information from chapters after Chapter {chapter_num}.
3. Be detailed — include key plot points, character actions, emotional beats, and important dialogue.
4. At the end, list any NEW characters introduced in this chapter.
5. List KEY EVENTS as bullet points.

{f"**Story so far (Chapters 1-{chapter_num - 1}):**{prev_context}" if prev_context else "This is the first chapter."}
{char_info}

**Chapter {chapter_num}: {chapter['title']}**

<chapter_text>
{chapter['text']}
</chapter_text>

**Respond in this exact JSON format:**
```json
{{
  "summary": "Detailed chapter summary (3-5 paragraphs)...",
  "key_events": ["event 1", "event 2", ...],
  "new_characters": [
    {{"name": "Character Name", "description": "Brief description and role"}}
  ]
}}
```"""
    return prompt


def build_recall_prompt(book: dict, up_to_chapter: int) -> str:
    """Build a recap of everything up to chapter N (no spoilers)."""
    summaries = []
    for ch in book["chapters"]:
        if ch["number"] > up_to_chapter:
            break
        if ch.get("summary"):
            summaries.append(f"### Chapter {ch['number']}: {ch['title']}\n{ch['summary']}")

    if not summaries:
        return f"No summaries available yet for chapters 1-{up_to_chapter}. Run summarization first."

    char_info = ""
    if book.get("characters"):
        char_info = "\n## Characters You've Met\n"
        for name, desc in book["characters"].items():
            char_info += f"- **{name}**: {desc}\n"

    # Collect all key events
    events_section = ""
    all_events = []
    for ch in book["chapters"]:
        if ch["number"] > up_to_chapter:
            break
        for evt in ch.get("key_events", []):
            all_events.append(f"- [Ch.{ch['number']}] {evt}")
    if all_events:
        events_section = "\n## Key Events Timeline\n" + "\n".join(all_events)

    recap = f"""# 📖 {book['title']} — Recap up to Chapter {up_to_chapter}

{char_info}
{events_section}

## Chapter Summaries

{"".join(f"{s}\n\n" for s in summaries)}

---
*You are currently at Chapter {up_to_chapter} of {book['total_chapters']}. ({round(up_to_chapter / book['total_chapters'] * 100)}% complete)*
"""
    return recap


def main():
    parser = argparse.ArgumentParser(description="Generate chapter summaries / recall")
    parser.add_argument("book_json", help="Path to book_data.json")
    parser.add_argument("--up-to", type=int, help="Generate summaries up to this chapter")
    parser.add_argument("--recall", type=int, help="Print a recap up to this chapter (no AI needed)")
    parser.add_argument("--prompt-for", type=int, help="Print the AI prompt for a specific chapter")
    parser.add_argument("--save-summary", type=int, help="Chapter number to save summary for")
    parser.add_argument("--summary-json", help="JSON string with summary data to save")
    args = parser.parse_args()

    book_path = os.path.expanduser(args.book_json)
    book = load_book(book_path)

    if args.recall:
        print(build_recall_prompt(book, args.recall))
        return

    if args.prompt_for:
        prompt = build_summary_prompt(book, args.prompt_for)
        if prompt:
            print(prompt)
        else:
            print(f"Chapter {args.prompt_for} not found.", file=sys.stderr)
            sys.exit(1)
        return

    if args.save_summary and args.summary_json:
        chapter = get_chapter(book, args.save_summary)
        if not chapter:
            print(f"Chapter {args.save_summary} not found.", file=sys.stderr)
            sys.exit(1)

        try:
            data = json.loads(args.summary_json)
        except json.JSONDecodeError:
            print("Error: Invalid JSON for summary data.", file=sys.stderr)
            sys.exit(1)

        chapter["summary"] = data.get("summary", "")
        chapter["key_events"] = data.get("key_events", [])
        chapter["new_characters"] = data.get("new_characters", [])

        # Update character roster
        for char in data.get("new_characters", []):
            name = char.get("name", "")
            desc = char.get("description", "")
            if name:
                book["characters"][name] = desc

        book["current_chapter"] = args.save_summary
        save_book(book_path, book)
        print(f"✅ Saved summary for Chapter {args.save_summary}")
        return

    if args.up_to:
        # Print prompts for all unsummarized chapters up to N
        for ch in book["chapters"]:
            if ch["number"] > args.up_to:
                break
            if ch.get("summary"):
                print(f"⏭️  Chapter {ch['number']} already summarized, skipping.")
                continue
            print(f"\n{'='*60}")
            print(f"SUMMARIZE CHAPTER {ch['number']}: {ch['title']}")
            print(f"{'='*60}\n")
            prompt = build_summary_prompt(book, ch["number"])
            print(prompt)
            print(f"\n{'='*60}\n")
        return

    # Default: show status
    print(f"📖 {book['title']}")
    print(f"   Chapters: {book['total_chapters']}")
    print(f"   Words: {book['total_words']}")
    print(f"   Current: Chapter {book.get('current_chapter', 0)}")
    print()
    summarized = sum(1 for ch in book["chapters"] if ch.get("summary"))
    print(f"   Summarized: {summarized}/{book['total_chapters']}")
    if book.get("characters"):
        print(f"   Characters tracked: {len(book['characters'])}")


if __name__ == "__main__":
    main()
