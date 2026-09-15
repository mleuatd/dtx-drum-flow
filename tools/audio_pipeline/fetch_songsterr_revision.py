from __future__ import annotations

import argparse, html, json, re, urllib.request
from pathlib import Path

CDNS = [
    "https://dqsljvtekg760.cloudfront.net",
    "https://d3d3l6a6rcgkaf.cloudfront.net",
]

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36"

def get(url: str):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
        "Referer": "https://www.songsterr.com/",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read(), r.headers.get_content_type()

def parse_state(page: bytes):
    text = page.decode("utf-8", "replace")
    patterns = [
        r'<script[^>]+id=["\']state["\'][^>]*>(.*?)</script>',
        r'<script[^>]*id=["\']state["\'][^>]*>(.*?)</script>',
    ]
    for p in patterns:
        m = re.search(p, text, flags=re.I|re.S)
        if m:
            raw = html.unescape(m.group(1).strip())
            return json.loads(raw)
    raise RuntimeError("Songsterr state payload not found")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("-o","--output",type=Path,required=True)
    args=ap.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)

    page,_=get(args.url)
    state=parse_state(page)
    current=state["meta"]["current"]
    meta={
        "sourceUrl":args.url,
        "songId":current.get("songId"),
        "revisionId":current.get("revisionId"),
        "image":current.get("image"),
        "title":current.get("title"),
        "artist":current.get("artist"),
        "tracks":current.get("tracks",[]),
    }
    (args.output/"state_meta.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")

    errors=[]
    downloaded=[]
    for track in meta["tracks"]:
        part=track.get("partId")
        if not isinstance(part,int):
            continue
        payload=None
        used=None
        for base in CDNS:
            u=f"{base}/{meta['songId']}/{meta['revisionId']}/{meta['image']}/{part}.json"
            try:
                raw,_=get(u)
                payload=json.loads(raw)
                used=u
                break
            except Exception as e:
                errors.append({"partId":part,"url":u,"error":repr(e)})
        if payload is None:
            continue
        name=str(track.get("name") or track.get("instrument") or f"part_{part}")
        low=name.lower()
        is_drum=("drum" in low) or track.get("instrumentId") in (128,129)
        fn=args.output/("drums_revision.json" if is_drum and not (args.output/"drums_revision.json").exists() else f"part_{part}.json")
        fn.write_text(json.dumps({"trackMeta":track,"revision":payload,"source":used},ensure_ascii=False,indent=2),encoding="utf-8")
        downloaded.append({"partId":part,"name":name,"isDrum":is_drum,"file":fn.name,"source":used})

    summary={"meta":meta,"downloaded":downloaded,"errors":errors}
    (args.output/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False))

if __name__=="__main__":
    main()
