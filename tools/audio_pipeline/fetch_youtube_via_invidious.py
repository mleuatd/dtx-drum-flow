from __future__ import annotations

import argparse
import json
import re
import shutil
import urllib.parse
import urllib.request
from pathlib import Path

INSTANCES = [
    "https://inv.nadeko.net",
    "https://invidious.nerdvpn.de",
    "https://yt.chocolatemoo53.com",
    "https://invidious.tiekoetter.com",
]


def video_id_from_url(url: str) -> str:
    m = re.search(r"(?:youtu\.be/|[?&]v=)([A-Za-z0-9_-]{11})", url)
    if not m:
        raise ValueError(f"Could not parse YouTube video id from {url}")
    return m.group(1)


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def copy_url(url: str, out: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=90) as src, out.open("wb") as dst:
        shutil.copyfileobj(src, dst, length=1024 * 1024)


def quality_height(stream: dict) -> int:
    q = str(stream.get("qualityLabel") or stream.get("quality") or "")
    m = re.search(r"(\d{3,4})p", q)
    if m:
        return int(m.group(1))
    res = str(stream.get("resolution") or "")
    m = re.search(r"x(\d+)", res)
    return int(m.group(1)) if m else 0


def fetch(url: str, out: Path) -> dict:
    vid = video_id_from_url(url)
    errors = []
    for base in INSTANCES:
        try:
            api = f"{base}/api/v1/videos/{vid}?local=true"
            data = get_json(api)
            streams = [s for s in data.get("formatStreams", []) if s.get("itag")]
            streams.sort(key=quality_height, reverse=True)

            # Prefer instance-proxied latest_version URLs. These keep the GitHub
            # runner away from googlevideo.com and avoid YouTube bot checks.
            for stream in streams[:8]:
                itag = str(stream.get("itag"))
                local_url = (
                    f"{base}/latest_version?"
                    + urllib.parse.urlencode({"id": vid, "itag": itag, "local": "true"})
                )
                try:
                    copy_url(local_url, out)
                    if out.exists() and out.stat().st_size > 100_000:
                        return {
                            "instance": base,
                            "video_id": vid,
                            "title": data.get("title"),
                            "duration": data.get("lengthSeconds"),
                            "itag": itag,
                            "quality": stream.get("qualityLabel") or stream.get("quality"),
                            "resolution": stream.get("resolution"),
                            "bytes": out.stat().st_size,
                            "proxied": True,
                        }
                except Exception as e:
                    errors.append(f"{base} itag {itag}: {type(e).__name__}: {e}")

            # Some instances return an already proxied/relative stream URL.
            for stream in streams[:8]:
                raw = stream.get("url")
                if not raw:
                    continue
                target = urllib.parse.urljoin(base, raw)
                try:
                    copy_url(target, out)
                    if out.exists() and out.stat().st_size > 100_000:
                        return {
                            "instance": base,
                            "video_id": vid,
                            "title": data.get("title"),
                            "duration": data.get("lengthSeconds"),
                            "itag": stream.get("itag"),
                            "quality": stream.get("qualityLabel") or stream.get("quality"),
                            "resolution": stream.get("resolution"),
                            "bytes": out.stat().st_size,
                            "proxied": target.startswith(base),
                        }
                except Exception as e:
                    errors.append(f"{base} raw stream: {type(e).__name__}: {e}")
        except Exception as e:
            errors.append(f"{base}: {type(e).__name__}: {e}")
    raise RuntimeError("All Invidious instances failed:\n" + "\n".join(errors))


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
