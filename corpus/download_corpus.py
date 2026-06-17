"""
Download the OpenSubtitles es-ja corpus from OPUS.

Source: https://opus.nlpl.eu/opusapi
File:   https://object.pouta.csc.fi/OPUS-OpenSubtitles/v2016/tmx/es-ja.tmx.gz

Run from the corpus/ directory:
    python download_corpus.py
"""

import gzip
import shutil
import urllib.request
from pathlib import Path

TMX_GZ_URL = "https://object.pouta.csc.fi/OPUS-OpenSubtitles/v2016/tmx/es-ja.tmx.gz"
DATA_DIR = Path(__file__).parent / "data"
GZ_PATH = DATA_DIR / "es-ja.tmx.gz"
TMX_PATH = DATA_DIR / "es-ja.tmx"


def _progress(count, block_size, total):
    if total > 0:
        pct = min(count * block_size / total * 100, 100)
        print(f"\r  {pct:.1f}%", end="", flush=True)


def download():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if TMX_PATH.exists():
        print(f"Already exists: {TMX_PATH}")
        return

    print(f"Downloading {TMX_GZ_URL} ...")
    urllib.request.urlretrieve(TMX_GZ_URL, GZ_PATH, reporthook=_progress)
    print()

    print(f"Decompressing → {TMX_PATH} ...")
    with gzip.open(GZ_PATH, "rb") as f_in, open(TMX_PATH, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

    GZ_PATH.unlink()
    print(f"Done. TMX saved to {TMX_PATH}")


if __name__ == "__main__":
    download()
