"""
Download the OpenSubtitles es-ja corpus via the OPUS API.

API docs: https://opus.nlpl.eu/opusapi
Corpus:   OpenSubtitles v2016, language pair es-ja, TMX format

Run from the corpus/ directory (inside the venv):
    python download_corpus.py
"""

import gzip
import shutil
from pathlib import Path

import requests

OPUS_API = "https://opus.nlpl.eu/opusapi"
CORPUS   = "OpenSubtitles"
VERSION  = "v2016"
SRC      = "es"
TGT      = "ja"

DATA_DIR = Path(__file__).parent / "data"
GZ_PATH  = DATA_DIR / "es-ja.tmx.gz"
TMX_PATH = DATA_DIR / "es-ja.tmx"


def get_download_url() -> str:
    params = {
        "corpus": CORPUS,
        "version": VERSION,
        "source": SRC,
        "target": TGT,
        "preprocessing": "tmx",
    }
    print(f"Querying OPUS API: {OPUS_API}")
    resp = requests.get(OPUS_API, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    corpora = data.get("corpora", [])
    if not corpora:
        raise RuntimeError(f"No results from OPUS API: {data}")
    url = corpora[0].get("url") or corpora[0].get("download")
    if not url:
        raise RuntimeError(f"No download URL in OPUS API response: {corpora[0]}")
    return url


def download():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if TMX_PATH.exists():
        print(f"Already exists: {TMX_PATH}")
        return

    url = get_download_url()
    print(f"Downloading: {url}")
    with requests.get(url, stream=True, timeout=300) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        downloaded = 0
        with open(GZ_PATH, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded / total * 100
                    print(f"\r  {pct:.1f}%  ({downloaded // 1_000_000} MB)", end="", flush=True)
    print()

    print(f"Decompressing → {TMX_PATH} ...")
    with gzip.open(GZ_PATH, "rb") as f_in, open(TMX_PATH, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

    GZ_PATH.unlink()
    print(f"Done. TMX saved to {TMX_PATH}")


if __name__ == "__main__":
    download()
