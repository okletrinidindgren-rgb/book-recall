#!/usr/bin/env python3
"""Build a lightweight chapter index from book_data.json.

Extracts per-chapter:
  - first_line / last_line (orientation)
  - character mentions (Chinese + English)
  - location mentions (Chinese + English)
  - chapter_brief (first 150 chars)
  - detected language

Zero AI token cost — pure local NLP.
"""

import json
import re
import sys
import os
from collections import Counter


# ── Language detection ──────────────────────────────────────────────

def detect_language(text: str) -> str:
    """Detect dominant language: 'zh', 'en', or 'mixed'."""
    sample = text[:3000]
    cjk = sum(1 for c in sample if '\u4e00' <= c <= '\u9fff')
    latin = sum(1 for c in sample if c.isascii() and c.isalpha())
    total = cjk + latin or 1
    if cjk / total > 0.3:
        return "zh"
    if latin / total > 0.7:
        return "en"
    return "mixed"


# ── Chinese name extraction ────────────────────────────────────────

def is_valid_chinese_name(name: str) -> bool:
    """Filter out common non-name Chinese phrases using generic language rules."""
    function_words = set(
        "不是,可是,但是,如果,因为,所以,而且,或者,虽然,就是,这个,那个,"
        "什么,怎么,为什么,他们,我们,你们,自己,这样,那样,所有,没有,"
        "已经,现在,应该,只是,还是,这种,那种,一个,一样,只能,不能,不会,"
        "一直,毕竟,于是,然后,随即,忽然,居然,竟然,不过,只要,否则,"
        "至于,不仅,也许,或许,大家,众人".split(",")
    )
    if name in function_words:
        return False

    action_suffixes = ("说", "道", "想", "站", "坐", "走", "跑", "来", "去",
                       "过", "着", "了", "呢", "吗", "吧", "的", "地", "得")
    if len(name) >= 2 and name.endswith(action_suffixes):
        return False

    body_action_patterns = re.compile(
        r'^(?:点点|摇摇|了点|了摇|起眉|着眉|抬起|回过|低下|扭过|了口|着眼|皱眉)'
    )
    if body_action_patterns.match(name):
        return False

    people_pattern = re.compile(r'^[\u4e00-\u9fff]*(?:个|些|有|所有|每|任何|整|几|两|这|那)人$')
    if people_pattern.match(name):
        return False

    if len(name) == 2 and name.endswith("人") and name[0] in "骗杀死活救伤打惹吓好坏找帮害怕烦选领跟":
        return False

    if all(c in "一二三四五六七八九十百千万个两几多少" for c in name):
        return False

    if name[0] in "我你他她它们":
        return False

    short_noise = re.compile(
        r'^(?:一[声下次些番把]|的人|其[他她]人|所有人|每个人|这[些个种]|那[些个种]|有[些人])$'
    )
    if short_noise.match(name):
        return False

    return True


def extract_chinese_names(text: str) -> list[str]:
    """Extract likely Chinese character names (2-3 char patterns after common verbs/particles)."""
    surnames = set("赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳酆鲍史唐费廉岑薛雷贺倪汤滕殷罗毕郝邬安常乐于时傅皮卞齐康伍余元卜顾孟平黄和穆萧尹姚邵湛汪祁毛禹狄米贝明臧计伏成戴宋茅庞熊纪舒屈项祝董梁杜阮蓝闵席季麻强贾路娄危江童颜郭梅盛林刁锺徐邱骆高夏蔡田樊胡凌霍虞万支柯昝管卢莫经房裘缪干解应宗丁宣邓")

    candidates = Counter()
    context_markers = [
        r'(?:叫|叫做|名叫|是|给|让|被|向|跟|对|问|说|道|喊|喝|骂|笑|看|望|瞪|指|拍|拉|推|抱)',
    ]
    for marker in context_markers:
        for m in re.finditer(marker + r'([\u4e00-\u9fff]{2,3})', text):
            name = m.group(1)
            if name[0] in surnames or len(name) == 2:
                candidates[name] += 1

    for m in re.finditer(r'([\u4e00-\u9fff]{2,3})(?:说|道|问|答|笑|喊|叫|想|看|听)', text):
        name = m.group(1)
        if name[0] in surnames:
            candidates[name] += 1

    names = []
    for name, count in candidates.most_common(50):
        if count >= 2 and len(name) <= 3 and is_valid_chinese_name(name):
            names.append(name)
    return names[:20]


def extract_chinese_nicknames(text: str) -> list[str]:
    """Extract descriptive character references like 花臂男, 白大褂, 山羊头."""
    patterns = [
        r'([\u4e00-\u9fff]{1,2}(?:男|女|人|头|哥|姐|弟|妹|叔|伯|爷|婆))',
        r'((?:老|小|大)[\u4e00-\u9fff]{1,2})',
    ]
    found = Counter()
    for p in patterns:
        for m in re.finditer(p, text):
            found[m.group(1)] += 1

    stop = set("众人,男人,女人,别人,旁人,老人,敌人,大人,小人,本人,个人".split(","))
    quant_people = re.compile(r'^[一二三四五六七八九十百千两几多数]人$')
    return [w for w, c in found.most_common(20)
            if c >= 2 and w not in stop and not quant_people.match(w)]


def extract_chinese_locations(text: str) -> list[str]:
    """Extract Chinese location mentions."""
    loc_pattern = re.compile(
        r'([\u4e00-\u9fff]{2,5}(?:市|省|区|县|镇|村|街道|大道|路|大楼|楼|手术室|教室|房间|医院|寺|塔|山|河|湖|海|岛|洞|谷|城市|城|国|酒店|餐馆|学校|广场|公园|大厅|宫殿|庙|桥|车站|机场|工厂))'
    )
    found = Counter()
    for m in loc_pattern.finditer(text):
        loc = m.group(1)
        if loc[0] in "我你他她它们的在是有被让给向从把将":
            continue
        found[loc] += 1
    return [loc for loc, _ in found.most_common(10)]


# ── English name extraction ────────────────────────────────────────

# Common English words that look like names but aren't
EN_STOP_WORDS = set("""
    The This That These Those What When Where Which Who How Did Does
    Was Were Been Being Have Has Had Will Would Could Should Must May
    Might Shall Can But And For Not You All Any Her His Its Let Our
    She They Too Why Are One Two Three Four Five New Old Big Little
    Good Great Just More Most Much Such Very Also Even Still Back
    Down Here Into Long Made Many More Most Only Over Same Some Than
    Them Then Well With From About After Again Before Between Each
    Under Until Above Below During Without Around Within Upon Both
    Every Other Same First Last Next Another Each Never Before After
    Then Quite Rather Really Already Almost Away Behind Beyond Else
    Right Left True False Inside Outside North South East West Beyond
    Maybe Sometimes Always Often Suddenly Finally Perhaps
""".split())


def extract_english_names(text: str) -> list[str]:
    """Extract likely English character names using heuristic patterns."""
    candidates = Counter()

    # Pattern 1: Dialogue attribution — "said X", "X said", "asked X", etc.
    dialogue_verbs = r'(?:said|asked|replied|answered|whispered|shouted|cried|muttered|exclaimed|called|yelled|told|thought|wondered|declared|demanded|insisted|suggested|screamed|murmured|sighed|laughed|smiled|nodded|shrugged|added|continued|explained|interrupted|agreed|protested|warned|promised|admitted|confessed|announced|argued|begged|commanded|complained|gasped|groaned|hissed|moaned|pleaded|snapped|sobbed|stammered|urged)'
    # "Name said" / "Name asked"
    for m in re.finditer(r'\b([A-Z][a-z]{1,15})\s+' + dialogue_verbs + r'\b', text):
        w = m.group(1)
        if w not in EN_STOP_WORDS:
            candidates[w] += 1
    # "said Name" / "asked Name"
    for m in re.finditer(dialogue_verbs + r'\s+([A-Z][a-z]{1,15})\b', text):
        w = m.group(1)
        if w not in EN_STOP_WORDS:
            candidates[w] += 1

    # Pattern 2: Possessive — "Name's"
    for m in re.finditer(r"\b([A-Z][a-z]{1,15})'s\b", text):
        w = m.group(1)
        if w not in EN_STOP_WORDS:
            candidates[w] += 1

    # Pattern 3: Name at sentence start followed by a verb
    for m in re.finditer(r'(?:^|\. )([A-Z][a-z]{1,15})\s+(?:was|is|had|has|went|looked|felt|saw|took|got|came|ran|stood|sat|walked|turned|knew|heard|began|found|gave|left|thought|seemed|tried|wanted|put|told|made|let|kept|set|started|opened|held|moved|brought|watched|followed|reached|spoke)\b', text):
        w = m.group(1)
        if w not in EN_STOP_WORDS:
            candidates[w] += 1

    # Pattern 4: "Mr./Mrs./Miss/Dr./Professor Name"
    for m in re.finditer(r'(?:Mr|Mrs|Ms|Miss|Dr|Professor|Lord|Lady|Sir|King|Queen|Prince|Princess|Captain|Colonel|General|Father|Mother|Uncle|Aunt)\.?\s+([A-Z][a-z]{1,15})', text):
        candidates[m.group(1)] += 1

    # Filter: must appear 3+ times
    names = [n for n, c in candidates.most_common(30) if c >= 3]
    return names[:20]


def extract_english_locations(text: str) -> list[str]:
    """Extract English location mentions using preposition context."""
    found = Counter()

    # "in/at/to/from/near/toward + Capitalized Word(s)"
    for m in re.finditer(r'\b(?:in|at|to|from|near|toward|towards|outside|inside|across|through|around|beyond)\s+(?:the\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b', text):
        loc = m.group(1)
        if loc not in EN_STOP_WORDS and len(loc) > 2:
            found[loc] += 1

    # Common location suffixes
    for m in re.finditer(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\s+(?:Street|Road|Avenue|Lane|Square|Park|Bridge|Tower|Castle|Palace|Church|Temple|River|Lake|Mountain|Island|Forest|Station|Airport|Hotel|Inn|Hall|House|Manor|Court|Garden|Academy|School|University|Hospital|Kingdom|Empire|City|Town|Village))\b', text):
        found[m.group(1)] += 1

    return [loc for loc, c in found.most_common(10) if c >= 2]


# ── Unified extraction ─────────────────────────────────────────────

def extract_characters(text: str, lang: str) -> list[str]:
    """Extract character names based on detected language."""
    if lang == "zh":
        names = extract_chinese_names(text)
        nicknames = extract_chinese_nicknames(text)
        return [n for n in dict.fromkeys(names + nicknames) if is_valid_chinese_name(n)][:15]
    elif lang == "en":
        return extract_english_names(text)
    else:  # mixed
        zh = extract_chinese_names(text)
        en = extract_english_names(text)
        return list(dict.fromkeys(zh + en))[:20]


def extract_locations(text: str, lang: str) -> list[str]:
    """Extract locations based on detected language."""
    if lang == "zh":
        return extract_chinese_locations(text)
    elif lang == "en":
        return extract_english_locations(text)
    else:
        return list(dict.fromkeys(extract_chinese_locations(text) + extract_english_locations(text)))[:10]


# ── Index builder ──────────────────────────────────────────────────

def build_index(book_data: dict) -> dict:
    """Build lightweight index for all chapters."""
    chapters = book_data.get("chapters", [])

    # Detect language from first few chapters
    sample_text = " ".join(ch.get("text", "")[:1000] for ch in chapters[:5])
    lang = detect_language(sample_text)

    index = {
        "title": book_data.get("title", "Untitled"),
        "language": lang,
        "total_chapters": len(chapters),
        "chapters": [],
        "global_characters": [],
        "global_locations": [],
    }

    all_chars = Counter()
    all_locs = Counter()

    for ch in chapters:
        text = ch.get("text", "")
        lines = [l.strip() for l in text.split("\n") if l.strip()]

        first_line = lines[0] if lines else ""
        last_line = lines[-1] if lines else ""
        brief = text[:200].replace("\n", " ")

        chars = extract_characters(text, lang)
        locations = extract_locations(text, lang)

        for n in chars:
            all_chars[n] += 1
        for l in locations:
            all_locs[l] += 1

        index["chapters"].append({
            "number": ch["number"],
            "title": ch["title"],
            "word_count": ch.get("word_count", 0),
            "char_count": len(text),
            "brief": brief,
            "first_line": first_line[:100],
            "last_line": last_line[:100],
            "characters": chars[:10],
            "locations": locations[:5],
        })

    index["global_characters"] = [
        {"name": n, "appearances": c}
        for n, c in all_chars.most_common(50)
    ]
    index["global_locations"] = [
        {"name": n, "appearances": c}
        for n, c in all_locs.most_common(30)
    ]

    return index


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Build lightweight chapter index (zero AI cost)")
    parser.add_argument("book_data", help="Path to book_data.json")
    parser.add_argument("--output", "-o", help="Output path (default: same dir/book_index.json)")
    args = parser.parse_args()

    path = os.path.expanduser(args.book_data)
    with open(path, "r", encoding="utf-8") as f:
        book_data = json.load(f)

    print(f"📚 Building index for: {book_data.get('title', 'Untitled')}")
    print(f"   Chapters: {len(book_data.get('chapters', []))}")

    index = build_index(book_data)

    print(f"   Language: {index['language']}")

    out_path = args.output or os.path.join(os.path.dirname(path), "book_index.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"✅ Index saved: {out_path}")
    print(f"   Top characters: {', '.join(c['name'] for c in index['global_characters'][:10])}")
    print(f"   Top locations: {', '.join(l['name'] for l in index['global_locations'][:5])}")

    orig_size = os.path.getsize(path)
    idx_size = os.path.getsize(out_path)
    print(f"   Compression: {orig_size/1024:.0f}KB → {idx_size/1024:.0f}KB ({idx_size/orig_size*100:.1f}%)")


if __name__ == "__main__":
    main()
