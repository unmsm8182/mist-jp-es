"""
Corpus exploration script for OpenSubtitles es-ja TMX corpus.
Analyzes a sample of the file without loading it fully into memory.
"""

import xml.etree.ElementTree as ET
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

# ── Configuration ────────────────────────────────────────────────────────────

TMX_PATH = Path("data/es-ja.tmx")
IDS_PATH = Path("data/es-ja.txt/OpenSubtitles.es-ja.ids")
SAMPLE_SIZE = 1000


# ── Helpers ──────────────────────────────────────────────────────────────────

def detect_script(text: str) -> str:
    """Detect dominant Unicode script in a string."""
    scripts = Counter()
    for ch in text:
        cat = unicodedata.category(ch)
        name = unicodedata.name(ch, "")
        if "HIRAGANA" in name or "KATAKANA" in name or "CJK" in name:
            scripts["ja"] += 1
        elif cat.startswith("L"):
            scripts["latin"] += 1
    return scripts.most_common(1)[0][0] if scripts else "unknown"


def text_issues(text: str) -> list[str]:
    """Identify common quality issues in a segment."""
    issues = []
    if not text or not text.strip():
        issues.append("empty")
    if len(text.strip()) == 1:
        issues.append("single_char")
    if re.search(r"<[^>]+>", text):
        issues.append("html_tags")
    if re.search(r"\{[^}]+\}", text):
        issues.append("curly_braces")
    if re.search(r"\d{2}:\d{2}:\d{2}", text):
        issues.append("timecode")
    if len(text) > 500:
        issues.append("very_long")
    return issues


# ── TMX Exploration ──────────────────────────────────────────────────────────

def explore_tmx(path: Path, sample_size: int) -> dict:
    languages = set()
    tu_attributes: list[dict] = []
    tuv_attributes: list[dict] = []
    header_info = {}
    segments = []  # {"es": ..., "ja": ...}
    tu_count = 0
    has_prop_elements = False
    has_note_elements = False

    for event, elem in ET.iterparse(str(path), events=["start", "end"]):
        if event == "start" and elem.tag == "header":
            header_info = dict(elem.attrib)

        if event == "end" and elem.tag == "tu":
            tu_count += 1
            if elem.attrib:
                tu_attributes.append(dict(elem.attrib))

            pair = {}
            for tuv in elem.findall("tuv"):
                lang = tuv.get("{http://www.w3.org/XML/1998/namespace}lang") or tuv.get("xml:lang", "?")
                languages.add(lang)
                if not tuv_attributes and tuv.attrib:
                    tuv_attributes.append(dict(tuv.attrib))
                seg = tuv.find("seg")
                text = (seg.text or "").strip() if seg is not None else ""
                pair[lang] = text

            if elem.find("prop") is not None:
                has_prop_elements = True
            if elem.find("note") is not None:
                has_note_elements = True

            segments.append(pair)
            elem.clear()

            if tu_count >= sample_size:
                break

    return {
        "header": header_info,
        "languages": sorted(languages),
        "tu_attributes_sample": tu_attributes[:3],
        "tuv_attributes_sample": tuv_attributes[:3],
        "has_prop_elements": has_prop_elements,
        "has_note_elements": has_note_elements,
        "segments": segments,
        "sampled_tu_count": tu_count,
    }


def analyze_quality(segments: list[dict]) -> dict:
    es_issues = Counter()
    ja_issues = Counter()
    empty_pairs = 0
    incomplete_pairs = 0
    len_es = []
    len_ja = []
    script_mismatches_ja = 0

    for pair in segments:
        es = pair.get("es", "")
        ja = pair.get("ja", "")

        if not es and not ja:
            empty_pairs += 1
            continue
        if not es or not ja:
            incomplete_pairs += 1
            continue

        len_es.append(len(es))
        len_ja.append(len(ja))

        for issue in text_issues(es):
            es_issues[issue] += 1
        for issue in text_issues(ja):
            ja_issues[issue] += 1

        if detect_script(ja) == "latin":
            script_mismatches_ja += 1

    n = len(segments)
    return {
        "total_sampled": n,
        "empty_pairs": empty_pairs,
        "incomplete_pairs": incomplete_pairs,
        "es_issues": dict(es_issues),
        "ja_issues": dict(ja_issues),
        "avg_len_es": round(sum(len_es) / len(len_es), 1) if len_es else 0,
        "avg_len_ja": round(sum(len_ja) / len(len_ja), 1) if len_ja else 0,
        "max_len_es": max(len_es) if len_es else 0,
        "max_len_ja": max(len_ja) if len_ja else 0,
        "ja_non_japanese_script": script_mismatches_ja,
    }


def sample_ids(path: Path, n: int = 5) -> list[str]:
    lines = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= n:
                break
            lines.append(line.rstrip("\n"))
    return lines


# ── Report ───────────────────────────────────────────────────────────────────

def print_report(tmx_data: dict, quality: dict, ids_sample: list[str]):
    sep = "─" * 70

    print(f"\n{'═' * 70}")
    print("  CORPUS EXPLORATION REPORT — OpenSubtitles es-ja TMX")
    print(f"{'═' * 70}\n")

    print("FILE")
    print(sep)
    print(f"  TMX path : {TMX_PATH}")
    print(f"  IDS path : {IDS_PATH}")
    print(f"  Sample   : {tmx_data['sampled_tu_count']} translation units\n")

    print("TMX HEADER")
    print(sep)
    for k, v in tmx_data["header"].items():
        print(f"  {k:<25} {v}")
    print()

    print("LANGUAGES DETECTED")
    print(sep)
    print(f"  {tmx_data['languages']}\n")

    print("TU ELEMENT STRUCTURE")
    print(sep)
    print("  <tu>")
    print("    <tuv xml:lang='es'><seg>Spanish text</seg></tuv>")
    print("    <tuv xml:lang='ja'><seg>Japanese text</seg></tuv>")
    print("  </tu>")
    if tmx_data["tu_attributes_sample"]:
        print(f"  TU attributes found : {tmx_data['tu_attributes_sample'][:2]}")
    else:
        print("  TU attributes       : none (doc IDs not embedded in TMX)")
    print(f"  <prop> elements     : {tmx_data['has_prop_elements']}")
    print(f"  <note> elements     : {tmx_data['has_note_elements']}\n")

    print("IDS FILE STRUCTURE (tab-separated)")
    print(sep)
    print("  Columns: es_subtitle_path | ja_subtitle_path | es_seg_ids | ja_seg_ids")
    print("  Sample rows:")
    for row in ids_sample:
        print(f"    {row}")
    print()

    print("SEGMENT EXAMPLES")
    print(sep)
    for i, pair in enumerate(tmx_data["segments"][2:7], start=3):
        es = pair.get("es", "")
        ja = pair.get("ja", "")
        print(f"  [{i}] ES: {es[:80]}")
        print(f"       JA: {ja[:80]}")
    print()

    print("QUALITY ANALYSIS (sample)")
    print(sep)
    q = quality
    print(f"  Total sampled        : {q['total_sampled']}")
    print(f"  Empty pairs          : {q['empty_pairs']}")
    print(f"  Incomplete pairs     : {q['incomplete_pairs']}")
    print(f"  Avg length ES (chars): {q['avg_len_es']}")
    print(f"  Avg length JA (chars): {q['avg_len_ja']}")
    print(f"  Max length ES        : {q['max_len_es']}")
    print(f"  Max length JA        : {q['max_len_ja']}")
    print(f"  JA segments w/ no Japanese script: {q['ja_non_japanese_script']}")
    if q["es_issues"]:
        print(f"  ES quality issues    : {q['es_issues']}")
    if q["ja_issues"]:
        print(f"  JA quality issues    : {q['ja_issues']}")
    print()

    print("TARGET JSON STRUCTURE")
    print(sep)
    sample = tmx_data["segments"][4]
    ids_fields = ids_sample[4].split("\t") if len(ids_sample) > 4 else ["?", "?"]
    doc_id = ids_fields[0].replace("es/", "").replace(".xml.gz", "") if len(ids_fields) >= 2 else "unknown"
    print(
        f"""  {{
    "document_id": "{doc_id}",
    "sequence_id": 4,
    "japanese_text": "{sample.get('ja', '')[:60]}",
    "spanish_text": "{sample.get('es', '')[:60]}",
    "sentiment": null,
    "intent": null
  }}"""
    )
    print()

    print("QUALITY FILTER RECOMMENDATIONS")
    print(sep)
    recommendations = [
        "1. Drop pairs where either segment is empty or whitespace-only.",
        "2. Drop pairs where either segment is a single character (likely noise).",
        "3. Drop pairs with raw HTML tags — subtitle formatting artifacts.",
        "4. Drop pairs with timecodes (HH:MM:SS pattern).",
        "5. Consider length-ratio filter: len(ja)/len(es) > 10 or < 0.1 may be misalignments.",
        "6. Consider min-length threshold (e.g. ≥ 2 chars per segment).",
        "7. Optionally deduplicate exact (es, ja) pairs — subtitles repeat across movies.",
        "8. Flag segments where JA contains only Latin script (possible alignment error).",
        "9. TMX has no document boundary markers — use the IDS file to reconstruct them.",
        "10. Sentences merged from multiple subtitle lines (IDS col 3/4 has multiple IDs)"
        " are normal and acceptable for translation tasks.",
    ]
    for r in recommendations:
        print(f"  {r}")
    print()


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Sampling {SAMPLE_SIZE} TUs from {TMX_PATH} ...")
    tmx_data = explore_tmx(TMX_PATH, SAMPLE_SIZE)
    quality = analyze_quality(tmx_data["segments"])
    ids_sample = sample_ids(IDS_PATH, n=8)
    print_report(tmx_data, quality, ids_sample)
