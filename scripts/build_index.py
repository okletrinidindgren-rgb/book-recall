#!/usr/bin/env python3
"""Build a lightweight chapter index from book_data.json.

Extracts per-chapter:
  - first_line / last_line (orientation)
  - character mentions (Chinese name patterns)
  - location mentions
  - chapter_brief (first 150 chars)

Zero AI token cost — pure local NLP.
"""

import json
import re
import sys
import os
from collections import Counter

def is_valid_name(name: str) -> bool:
    """Filter out common non-name Chinese phrases."""
    noise = set("点点头,了点头,摇摇头,了摇头,起眉头,着眉头,抬起头,回过头,了口气,着眼睛,"
                "二人,一声,三个人,四个人,两个人,五个人,六个人,七个人,八个人,九个人,十个人,"
                "的人,整个人,这些人,任何人,那些人,有些人,几个人,某个人,每个人,"
                "骗人,杀人,死人,活人,救人,伤人,打人,惹人,吓人,好人,坏人,"
                "不是,可是,但是,如果,因为,所以,而且,或者,虽然,就是,这个,那个,"
                "什么,怎么,为什么,他们,我们,你们,自己,这样,那样,所有,没有,"
                "已经,现在,应该,只是,还是,这种,那种,一个,一样,只能,不能,不会,"
                "一直,毕竟,于是,然后,随即,忽然,居然,竟然,不过,只要,否则,"
                "至于,不仅,也许,或许,大家,众人,所有人,每个人,"
                "不远处,这座城,我们所,备战区".split(","))
    
    action_suffixes = ("说", "道", "想", "站", "坐", "走", "跑", "来", "去", "过", "着", "了", "呢", "吗", "吧")
    
    if name in noise:
        return False
    if len(name) >= 2 and name.endswith(action_suffixes):
        return False
    if all(c in "一二三四五六七八九十百千万个两几多少" for c in name):
        return False
    return True


def extract_chinese_names(text: str) -> list[str]:
    """Extract likely Chinese character names (2-3 char patterns after common verbs/particles)."""
    # Common surname characters (top 100)
    surnames = set("赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳酆鲍史唐费廉岑薛雷贺倪汤滕殷罗毕郝邬安常乐于时傅皮卞齐康伍余元卜顾孟平黄和穆萧尹姚邵湛汪祁毛禹狄米贝明臧计伏成戴宋茅庞熊纪舒屈项祝董梁杜阮蓝闵席季麻强贾路娄危江童颜郭梅盛林刁锺徐邱骆高夏蔡田樊胡凌霍虞万支柯昝管卢莫经房裘缪干解应宗丁宣邓")
    
    # Find 2-3 character names
    name_pattern = re.compile(r'([\u4e00-\u9fff]{2,3})')
    candidates = Counter()
    
    # Names often appear after these context markers
    context_markers = [
        r'(?:叫|叫做|名叫|是|给|让|被|向|跟|对|问|说|道|喊|喝|骂|笑|看|望|瞪|指|拍|拉|推|抱)',
    ]
    
    for marker in context_markers:
        for m in re.finditer(marker + r'([\u4e00-\u9fff]{2,3})', text):
            name = m.group(1)
            if name[0] in surnames or len(name) == 2:
                candidates[name] += 1
    
    # Also catch "XXX说" pattern
    for m in re.finditer(r'([\u4e00-\u9fff]{2,3})(?:说|道|问|答|笑|喊|叫|想|看|听)', text):
        name = m.group(1)
        if name[0] in surnames:
            candidates[name] += 1
    
    # Filter: must appear 2+ times, exclude common non-name phrases
    stop_words = set("不是,可是,但是,如果,因为,所以,而且,或者,虽然,就是,这个,那个,什么,怎么,为什么,他们,我们,你们,自己,这样,那样,所有,没有,已经,现在,应该,只是,还是,这种,那种,一个,一样,只能,不能,不会,一直,毕竟,于是,然后,随即,忽然,居然,竟然,不过,只要,否则,毕竟,至于,不仅,也许,或许,大家,众人,所有人,每个人,点点头,了点头,摇摇头,了摇头,起眉头,着眉头,抬起头,回过头,二人,一声,三个人,四个人,两个人,五个人,六个人,七个人,八个人,九个人,十个人,的人,整个人,这些人,任何人,那些人,有些人,几个人,某个人,每个人,骗人,杀人,死人,活人,救人,伤人,打人,惹人,吓人,好人,坏人".split(","))
    
    names = []
    for name, count in candidates.most_common(50):
        if count >= 2 and name not in stop_words and len(name) <= 3:
            names.append(name)
    
    return names[:20]  # Top 20 per chapter


def extract_nicknames_and_descriptors(text: str) -> list[str]:
    """Extract descriptive character references like 花臂男, 白大褂, 山羊头."""
    patterns = [
        r'([\u4e00-\u9fff]{1,2}(?:男|女|人|头|哥|姐|弟|妹|叔|伯|爷|婆))',
        r'((?:老|小|大)[\u4e00-\u9fff]{1,2})',
    ]
    found = Counter()
    for p in patterns:
        for m in re.finditer(p, text):
            found[m.group(1)] += 1
    
    stop = set("众人,男人,女人,所有人,每个人,一个人,其他人,其余人,死人,别人,旁人,下面,上面,里面,外面,那人,这人,本人,个人,几人,二人,三人,四人,五人,六人,七人,八人,九人,十人,老人,敌人,大人,小人,友人,两人".split(","))
    return [w for w, c in found.most_common(20) if c >= 2 and w not in stop]


def extract_locations(text: str) -> list[str]:
    """Extract location mentions."""
    # Common location suffixes
    loc_pattern = re.compile(r'([\u4e00-\u9fff]{2,5}(?:市|省|区|县|镇|村|街道|大道|路|大楼|楼|手术室|教室|房间|医院|寺|塔|山|河|湖|海|岛|洞|谷|城市|城|国|酒店|餐馆|学校|广场|公园|大厅|宫殿|庙|桥|车站|机场|工厂))')
    found = Counter()
    for m in loc_pattern.finditer(text):
        loc = m.group(1)
        # Filter noise: must start with a plausible place-name char, not a verb/pronoun
        if loc[0] in "我你他她它们的在是有被让给向从把将":
            continue
        found[loc] += 1
    return [loc for loc, _ in found.most_common(10)]


def build_index(book_data: dict) -> dict:
    """Build lightweight index for all chapters."""
    chapters = book_data.get("chapters", [])
    index = {
        "title": book_data.get("title", "Untitled"),
        "total_chapters": len(chapters),
        "chapters": [],
        "global_characters": Counter(),
        "global_locations": Counter(),
    }
    
    all_chars = Counter()
    all_locs = Counter()
    
    for ch in chapters:
        text = ch.get("text", "")
        lines = [l.strip() for l in text.split("\n") if l.strip() and not re.match(r'^第\d+章', l)]
        
        first_line = lines[0] if lines else ""
        last_line = lines[-1] if lines else ""
        brief = text[:200].replace("\n", " ")
        
        names = extract_chinese_names(text)
        nicknames = extract_nicknames_and_descriptors(text)
        locations = extract_locations(text)
        
        # Merge names and nicknames, filter noise
        all_people = [n for n in dict.fromkeys(names + nicknames) if is_valid_name(n)]
        
        for n in all_people:
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
            "characters": all_people[:10],
            "locations": locations[:5],
        })
    
    # Global character frequency (top 50)
    index["global_characters"] = [{"name": n, "appearances": c} for n, c in all_chars.most_common(100) if is_valid_name(n)][:50]
    index["global_locations"] = [{"name": n, "appearances": c} for n, c in all_locs.most_common(60) if is_valid_name(n)][:30]
    
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
    
    out_path = args.output or os.path.join(os.path.dirname(path), "book_index.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Index saved: {out_path}")
    print(f"   Top characters: {', '.join(c['name'] for c in index['global_characters'][:10])}")
    print(f"   Top locations: {', '.join(l['name'] for l in index['global_locations'][:5])}")
    
    # Size comparison
    orig_size = os.path.getsize(path)
    idx_size = os.path.getsize(out_path)
    print(f"   Compression: {orig_size/1024:.0f}KB → {idx_size/1024:.0f}KB ({idx_size/orig_size*100:.1f}%)")


if __name__ == "__main__":
    main()
