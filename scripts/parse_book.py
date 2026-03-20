#!/usr/bin/env python3
"""
book-recall: Parse EPUB/PDF/TXT into chapter-segmented JSON.

Usage:
    python3 parse_book.py <file_path> [--output <output_dir>]

Output: A JSON file with chapter-level text, saved to <output_dir>/book_data.json
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def parse_epub(file_path: str) -> list[dict]:
    """Parse EPUB into chapters using ebooklib + BeautifulSoup."""
    try:
        import ebooklib
        from ebooklib import epub
        from bs4 import BeautifulSoup
    except ImportError:
        print("Error: Install deps first: pip3 install ebooklib beautifulsoup4 lxml", file=sys.stderr)
        sys.exit(1)

    book = epub.read_epub(file_path)
    chapters = []
    chapter_num = 0

    # Get spine order (reading order)
    spine_ids = [item_id for item_id, _ in book.spine]
    items_by_id = {item.get_id(): item for item in book.get_items()}

    for item_id in spine_ids:
        item = items_by_id.get(item_id)
        if item is None:
            continue
        if item.get_type() != ebooklib.ITEM_DOCUMENT:
            continue

        content = item.get_content().decode("utf-8", errors="replace")
        soup = BeautifulSoup(content, "lxml")
        text = soup.get_text(separator="\n").strip()

        if len(text) < 100:
            # Skip very short items (cover, copyright, etc.)
            continue

        chapter_num += 1

        # Try to extract chapter title from headings
        title = None
        for tag in ["h1", "h2", "h3"]:
            heading = soup.find(tag)
            if heading:
                title = heading.get_text().strip()
                break

        if not title:
            title = f"Chapter {chapter_num}"

        chapters.append({
            "number": chapter_num,
            "title": title,
            "text": text,
            "word_count": len(text.split()),
        })

    return chapters


def parse_pdf(file_path: str) -> list[dict]:
    """Parse PDF into chapters using pdftotext + heuristic splitting."""
    import subprocess

    result = subprocess.run(
        ["pdftotext", "-layout", file_path, "-"],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode != 0:
        print(f"Error: pdftotext failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    full_text = result.stdout
    return split_into_chapters(full_text)


def parse_txt(file_path: str) -> list[dict]:
    """Parse plain text file into chapters."""
    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
        full_text = f.read()
    return split_into_chapters(full_text)


def split_into_chapters(text: str) -> list[dict]:
    """
    Heuristic chapter splitting for PDF/TXT.
    Looks for patterns like "Chapter 1", "第一章", "CHAPTER ONE", etc.
    """
    # Common chapter heading patterns (English + Chinese + numbered)
    patterns = [
        r"(?m)^[\s]*(?:CHAPTER|Chapter|chapter)[\s]+[\dIVXLCivxlc]+[.\s:].*$",
        r"(?m)^[\s]*(?:PART|Part|part)[\s]+[\dIVXLCivxlc]+[.\s:].*$",
        r"(?m)^[\s]*第[\s]*[一二三四五六七八九十百千\d]+[\s]*[章节卷部回].*$",
        r"(?m)^[\s]*\d+[.\s]+[A-Z\u4e00-\u9fff].*$",
    ]

    # Find all chapter boundaries
    boundaries = []
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            boundaries.append((match.start(), match.group().strip()))

    # Sort by position
    boundaries.sort(key=lambda x: x[0])

    # Deduplicate nearby boundaries (within 50 chars)
    deduped = []
    for pos, title in boundaries:
        if not deduped or pos - deduped[-1][0] > 50:
            deduped.append((pos, title))
    boundaries = deduped

    if len(boundaries) < 2:
        # Can't find chapter markers, split by fixed size (~3000 words)
        words = text.split()
        chunk_size = 3000
        chapters = []
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i : i + chunk_size])
            chapters.append({
                "number": len(chapters) + 1,
                "title": f"Section {len(chapters) + 1}",
                "text": chunk,
                "word_count": min(chunk_size, len(words) - i),
            })
        return chapters

    # Split text at boundaries
    chapters = []
    for i, (pos, title) in enumerate(boundaries):
        end = boundaries[i + 1][0] if i + 1 < len(boundaries) else len(text)
        chapter_text = text[pos:end].strip()
        if len(chapter_text) < 50:
            continue
        chapters.append({
            "number": i + 1,
            "title": title,
            "text": chapter_text,
            "word_count": len(chapter_text.split()),
        })

    return chapters


def main():
    parser = argparse.ArgumentParser(description="Parse book into chapter-segmented JSON")
    parser.add_argument("file", help="Path to EPUB, PDF, or TXT file")
    parser.add_argument("--output", "-o", help="Output directory (default: same dir as input)")
    args = parser.parse_args()

    file_path = os.path.expanduser(args.file)
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    ext = Path(file_path).suffix.lower()
    book_name = Path(file_path).stem

    print(f"Parsing: {file_path} ({ext})")

    if ext == ".epub":
        chapters = parse_epub(file_path)
    elif ext == ".pdf":
        chapters = parse_pdf(file_path)
    elif ext == ".txt":
        chapters = parse_txt(file_path)
    else:
        print(f"Error: Unsupported format '{ext}'. Use .epub, .pdf, or .txt", file=sys.stderr)
        sys.exit(1)

    if not chapters:
        print("Error: No chapters found.", file=sys.stderr)
        sys.exit(1)

    # Build output
    output_dir = args.output or os.path.dirname(file_path) or "."
    os.makedirs(output_dir, exist_ok=True)

    book_data = {
        "title": book_name,
        "source_file": os.path.basename(file_path),
        "total_chapters": len(chapters),
        "total_words": sum(ch["word_count"] for ch in chapters),
        "chapters": [],
        "characters": {},      # To be filled by AI summarization
        "current_chapter": 0,  # Reading progress
    }

    for ch in chapters:
        book_data["chapters"].append({
            "number": ch["number"],
            "title": ch["title"],
            "word_count": ch["word_count"],
            "text": ch["text"],
            "summary": None,          # To be filled by AI
            "key_events": [],          # To be filled by AI
            "new_characters": [],      # To be filled by AI
        })

    output_file = os.path.join(output_dir, "book_data.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(book_data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Parsed {len(chapters)} chapters, {book_data['total_words']} words total")
    print(f"📁 Saved to: {output_file}")

    # Print chapter list
    print(f"\n{'#':<4} {'Title':<50} {'Words':>8}")
    print("-" * 64)
    for ch in chapters:
        title_display = ch["title"][:48]
        print(f"{ch['number']:<4} {title_display:<50} {ch['word_count']:>8}")


if __name__ == "__main__":
    main()
