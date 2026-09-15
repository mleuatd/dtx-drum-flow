from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import urllib.request
from pathlib import Path

INSTANCES = [
    "https://pipedapi.kavin.rocks",
    "https://pipedapi.leptons.xyz",
    "https://pipedapi.nosebs.ru",
    "https://pipedapi-libre.kavin.rocks",
    "https://pipedapi.adminforge.de",
    "https://api.piped.yt",
    "https://api.piped.private.coffee",
    "https://pipedapi.darkness.services",
    "https://pipedapi.owo.si",
    "https://pipedapi.ducks.party",
]


def video_id_from_url(url: str) -> str:
    m = re.search(r"(?:youtu\.be/|[?&]v=)([A-Za-z0-9_-]{11})", url)
    if not m:
        raise ValueError(f"Could not parse YouTube video id from {url}")
    return m.group(1)


def ranked_streams(data: dict) -> list[dict]:
    streams = [s for s in data.get("videoStreams", []) if s.get("url")]
    def score(s: dict):
        h = int(s.get("height") or 0)
        fps = int(s.get("fps") or 0)
        mime = str(s.get("mimeType") or "").lower()
        codec = str(s.get("codec") or "").lower()
        # Prefer <=1080p, MP4/H.264 and higher FPS for frame extraction.
        return (
            1 if 240 <= h <= 1080 else 0,
            min(h, 1080),
            1 if "mp4" in mime else 0,
            1 if "avc" in codec or "h264" in codec else 0,
            fps,
            int(s.get("bitrate") or 0),
        )
    return sorted(streams, key=score, reverse=True)


def copy_url(url: str, out: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as src, out.open("wb") as dst:
        shutil.copyfileobj(src, dst, length=1024 * 1024)


def fetch(url: str, out: Path) -> dict:
    vid = video_id_from_url(url)
    errors = []
    for base in INSTANCES:
        try:
            req = urllib.request.Request(
                f"{base}/streams/{vid}",
                headers={"User-Agent": "Mozilla/5.0"},
            )
            with urllib.request.urlopen(req, timeout=25) as r:
                data = json.load(r)
            for stream in ranked_streams(data)[:6]:
                try:
                    copy_url(stream["url"], out)
                    if out.exists() and out.stat().st_size > 100_000:
                        return {
                            "instance": base,
                            "video_id": vid,
                            "title": data.get("title"),
                            "duration": data.get("duration"),
                            "height": stream.get("height"),
                            "fps": stream.get("fps"),
                            "mimeType": stream.get("mimeType"),
                            "videoOnly": stream.get("videoOnly"),
                            "bytes": out.stat().st_size,
                        }
                except Exception as e:
                    errors.append(f"{base} stream: {type(e).__name__}: {e}")
        except Exception as e:
            errors.append(f"{base}: {type(e).__name__}: {e}")
    raise RuntimeError("All Piped instances failed:\n" + "\n".join(errors))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("output", type=Path)
    ap.add_argument("--metadata", type=Path)
    args = ap.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    meta = fetch(args.url, args.output)
    if args.metadata:
        args.metadata.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False))


if __name__ == "__main__":
    main()
