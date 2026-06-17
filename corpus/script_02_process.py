"""
Full streaming processor for OpenSubtitles es-ja TMX corpus.

Pipeline:
  TMX (iterparse) ──┐
                    ├──► extract ──► clean ──► enrich (stub) ──► write JSONL
  IDS (readline)  ──┘

Output: data/processed/corpus_es_ja.jsonl  (one JSON object per line)
"""

import json
import re
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Iterator, Optional

# ── Configuration ─────────────────────────────────────────────────────────────

TMX_PATH = Path("data/es-ja.tmx")
IDS_PATH = Path("data/es-ja.txt/OpenSubtitles.es-ja.ids")
OUTPUT_DIR = Path("data/processed")
OUTPUT_PATH = OUTPUT_DIR / "corpus_es_ja.jsonl"

# Quality filter thresholds (set to None to disable a filter)
MIN_SEGMENT_LEN = 2          # chars; segments shorter than this are dropped
MAX_SEGMENT_LEN = 1000       # chars; segments longer than this are dropped
MAX_LEN_RATIO = 15.0         # max(len_es, len_ja) / min(...); drops extreme mismatches
PROGRESS_EVERY = 100_000     # print progress every N records


# ── Data model ────────────────────────────────────────────────────────────────

@dataclass
class TranslationUnit:
    document_id: str
    sequence_id: int
    japanese_text: str
    spanish_text: str
    sentiment: Optional[str] = field(default=None)
    intent: Optional[str] = field(default=None)

    def to_dict(self) -> dict:
        return asdict(self)


# ── IDS parser ────────────────────────────────────────────────────────────────

def iter_ids(path: Path) -> Iterator[str]:
    """
    Yield document_id strings from the IDS file, one per alignment line.

    IDS format (tab-separated):
      es_path  ja_path  es_seg_ids  ja_seg_ids

    We use the ES subtitle path as the canonical document identifier,
    stripping the leading "es/" prefix and ".xml.gz" suffix to produce
    a compact ID like "1920/10323/5829947".
    """
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.split("\t", 1)
            es_path = parts[0].strip() if parts else ""
            doc_id = es_path.removeprefix("es/").removesuffix(".xml.gz")
            yield doc_id


# ── TMX parser ────────────────────────────────────────────────────────────────

def iter_tmx(path: Path) -> Iterator[tuple[str, str]]:
    """
    Yield (spanish_text, japanese_text) pairs by streaming the TMX file.
    Uses iterparse to avoid loading the full XML into memory.
    """
    for _event, elem in ET.iterparse(str(path), events=["end"]):
        if elem.tag != "tu":
            continue

        es_text = ""
        ja_text = ""
        for tuv in elem.findall("tuv"):
            lang = (
                tuv.get("{http://www.w3.org/XML/1998/namespace}lang")
                or tuv.get("xml:lang", "")
            )
            seg = tuv.find("seg")
            text = (seg.text or "") if seg is not None else ""
            if lang == "es":
                es_text = text
            elif lang == "ja":
                ja_text = text

        elem.clear()
        yield es_text, ja_text


# ── Text cleaning ─────────────────────────────────────────────────────────────

_MULTI_SPACE = re.compile(r"[ \t]+")
_MULTI_NEWLINE = re.compile(r"\n{2,}")


def clean_segment(text: str) -> str:
    """Normalize whitespace; preserve all original characters and punctuation."""
    text = _MULTI_SPACE.sub(" ", text)
    text = _MULTI_NEWLINE.sub("\n", text)
    return text.strip()


# ── Quality filters ───────────────────────────────────────────────────────────

_HTML_TAG = re.compile(r"<[^>]+>")
_TIMECODE = re.compile(r"\d{1,2}:\d{2}:\d{2}")


def passes_quality_filter(es: str, ja: str) -> bool:
    """Return True if the pair is worth keeping."""
    if not es or not ja:
        return False

    len_es, len_ja = len(es), len(ja)

    if MIN_SEGMENT_LEN is not None:
        if len_es < MIN_SEGMENT_LEN or len_ja < MIN_SEGMENT_LEN:
            return False

    if MAX_SEGMENT_LEN is not None:
        if len_es > MAX_SEGMENT_LEN or len_ja > MAX_SEGMENT_LEN:
            return False

    if MAX_LEN_RATIO is not None:
        ratio = max(len_es, len_ja) / min(len_es, len_ja)
        if ratio > MAX_LEN_RATIO:
            return False

    if _HTML_TAG.search(es) or _HTML_TAG.search(ja):
        return False

    if _TIMECODE.search(es) or _TIMECODE.search(ja):
        return False

    return True


# ── Enrichment stubs ──────────────────────────────────────────────────────────
# These functions are intentionally empty placeholders.
# Plug in your models here in a future pipeline stage without touching
# the extract/clean/write layers above.

def enrich_sentiment(unit: TranslationUnit) -> TranslationUnit:
    """Future: populate unit.sentiment using a multilingual sentiment model."""
    # Example:
    #   unit.sentiment = sentiment_model.predict(unit.japanese_text)
    return unit


def enrich_intent(unit: TranslationUnit) -> TranslationUnit:
    """Future: populate unit.intent using an intent classification model."""
    # Example:
    #   unit.intent = intent_model.predict(unit.spanish_text)
    return unit


# ── Pipeline ──────────────────────────────────────────────────────────────────

def run_pipeline(
    tmx_path: Path,
    ids_path: Path,
    output_path: Path,
    apply_quality_filter: bool = True,
) -> dict:
    """
    Stream-process the TMX corpus and write a JSONL file.
    Returns a summary dict with counts.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    total_read = 0
    total_kept = 0
    total_dropped = 0
    start = time.time()

    ids_iter = iter_ids(ids_path)
    tmx_iter = iter_tmx(tmx_path)

    with open(output_path, "w", encoding="utf-8") as out_f:
        sequence_id = 0

        for (es_raw, ja_raw), doc_id in zip(tmx_iter, ids_iter):
            total_read += 1

            es = clean_segment(es_raw)
            ja = clean_segment(ja_raw)

            if apply_quality_filter and not passes_quality_filter(es, ja):
                total_dropped += 1
                continue

            unit = TranslationUnit(
                document_id=doc_id,
                sequence_id=sequence_id,
                japanese_text=ja,
                spanish_text=es,
            )

            # Enrichment hooks (currently no-ops)
            unit = enrich_sentiment(unit)
            unit = enrich_intent(unit)

            out_f.write(json.dumps(unit.to_dict(), ensure_ascii=False) + "\n")
            total_kept += 1
            sequence_id += 1

            if total_read % PROGRESS_EVERY == 0:
                elapsed = time.time() - start
                rate = total_read / elapsed
                print(
                    f"  [{total_read:>9,}] kept={total_kept:,}  dropped={total_dropped:,}"
                    f"  rate={rate:,.0f} rec/s"
                )

    elapsed = time.time() - start
    return {
        "total_read": total_read,
        "total_kept": total_kept,
        "total_dropped": total_dropped,
        "drop_rate_pct": round(100 * total_dropped / total_read, 2) if total_read else 0,
        "elapsed_seconds": round(elapsed, 1),
        "output_path": str(output_path),
    }


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Processing {TMX_PATH}  →  {OUTPUT_PATH}")
    print("Quality filter: ON\n")

    summary = run_pipeline(TMX_PATH, IDS_PATH, OUTPUT_PATH, apply_quality_filter=True)

    print("\n── Summary " + "─" * 60)
    for k, v in summary.items():
        print(f"  {k:<25} {v}")

    # Print a few sample records
    print("\n── Sample output (first 3 records) " + "─" * 35)
    with open(OUTPUT_PATH, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if i >= 3:
                break
            rec = json.loads(line)
            print(json.dumps(rec, ensure_ascii=False, indent=2))
