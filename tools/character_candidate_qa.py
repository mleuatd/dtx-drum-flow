from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

W,H=1448,1086

def sha256(p:Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()

def alpha_bbox(im):
    if im.mode!="RGBA":
        return None
    return im.getchannel("A").getbbox()

def centroid(im):
    a=im.getchannel("A")
    bbox=a.getbbox()
    if not bbox:
        return None
    px=a.load(); sx=sy=sw=0
    for y in range(bbox[1],bbox[3]):
        for x in range(bbox[0],bbox[2]):
            w=px[x,y]
            if w:
                sx+=x*w; sy+=y*w; sw+=w
    return None if not sw else [sx/sw,sy/sw]

def diff_metrics(a,b):
    if a.size!=b.size:
        return {"comparable":False}
    da=ImageChops.difference(a.convert("RGBA"),b.convert("RGBA"))
    stat=ImageStat.Stat(da)
    changed=sum(1 for px in da.getdata() if px!=(0,0,0,0))
    total=a.width*a.height
    return {
        "comparable":True,
        "changedPixelRatio":changed/total,
        "meanChannelDiff":stat.mean,
        "bboxA":alpha_bbox(a.convert("RGBA")),
        "bboxB":alpha_bbox(b.convert("RGBA")),
        "centroidA":centroid(a.convert("RGBA")),
        "centroidB":centroid(b.convert("RGBA"))
    }

ap=argparse.ArgumentParser()
ap.add_argument("candidate")
ap.add_argument("--neutral")
ap.add_argument("--expected-name")
ap.add_argument("--out",default="candidate-qa.json")
ap.add_argument("--mode",choices=["lightweight","full"],default="lightweight")
args=ap.parse_args()

p=Path(args.candidate)
res={
    "file":str(p),
    "status":"PASS",
    "gateClass":"PASS",
    "errors":[],
    "warnings":[],
    "signals":[],
    "recommendedActions":[],
    "sha256":sha256(p)
}

try:
    im=Image.open(p)
except Exception as e:
    res["status"]="FAIL"
    res["gateClass"]="HARD_FAIL"
    res["errors"].append("not readable image: "+str(e))
else:
    res.update({
        "format":im.format,
        "mode":im.mode,
        "size":list(im.size),
        "alphaBBox":alpha_bbox(im.convert("RGBA"))
    })
    if im.format!="PNG":
        res["errors"].append("format is not PNG")
    if im.size!=(W,H):
        res["errors"].append(f"dimensions {im.size} != {(W,H)}")
    if im.mode!="RGBA":
        res["warnings"].append("source mode is not RGBA")

    rgba=im.convert("RGBA")
    a=rgba.getchannel("A")
    ext=a.getextrema()
    if ext[0]==255:
        res["errors"].append("no transparent pixels")
    if ext[1]==0:
        res["errors"].append("empty alpha image")

    bbox=a.getbbox()
    if bbox:
        bw,bh=bbox[2]-bbox[0],bbox[3]-bbox[1]
        if bw>W*.96 and bh>H*.96:
            res["warnings"].append("alpha bbox nearly fills whole canvas; inspect opaque background/extreme crop")
        if bw<W*.08 or bh<H*.08:
            res["warnings"].append("very small visible bbox; possible empty/cropped candidate")

    if args.expected_name and p.name!=args.expected_name:
        res["warnings"].append("filename differs from expected: "+args.expected_name)

    if args.neutral:
        n=Image.open(args.neutral).convert("RGBA")
        res["neutralDiff"]=diff_metrics(n,rgba)
        ratio=res["neutralDiff"].get("changedPixelRatio",0)
        if ratio>0.55:
            msg="large whole-frame diff vs neutral; possible redraw/camera/background change"
            if args.mode=="full":
                res["warnings"].append(msg)
            else:
                res["signals"].append("NONBLOCKING_"+msg.replace(" ","_").upper())
            res["signals"].append("WHOLE_FRAME_DIFF_RISK")
            res["recommendedActions"].append(
                "Run visual identity/camera/stool continuity review before rejecting; do not reject from diff ratio alone."
            )
        ca=res["neutralDiff"].get("centroidA")
        cb=res["neutralDiff"].get("centroidB")
        if ca and cb:
            shift=((ca[0]-cb[0])**2+(ca[1]-cb[1])**2)**0.5
            res["neutralDiff"]["centroidShiftPx"]=shift
            if shift>45:
                msg="large alpha centroid shift; inspect body/stool/camera translation"
                if args.mode=="full":
                    res["warnings"].append(msg)
                else:
                    res["signals"].append("NONBLOCKING_"+msg.replace(" ","_").upper())
                res["signals"].append("CENTROID_SHIFT_RISK")
                res["recommendedActions"].append(
                    "Inspect core body/stool registration; if core is stable, repair only the moved limb/contact region."
                )

if res["errors"]:
    res["status"]="FAIL"
    res["gateClass"]="HARD_FAIL"
    res["recommendedActions"].append(
        "Fix binary/layer validity before any visual retry; do not generate a new pose just to fix file-format errors."
    )
elif res["warnings"]:
    res["status"]="WARN"
    res["gateClass"]="VISUAL_REVIEW_REQUIRED"
    res["recommendedActions"].append(
        "Warnings are not automatic rejection. Use visual continuity/contact QA and retry-controller only if a real visual defect is confirmed."
    )
else:
    res["status"]="PASS"
    res["gateClass"]="PASS"

res["qaMode"]=args.mode
res["phasePolicy"]="PRE_RUNTIME_LIGHTWEIGHT" if args.mode=="lightweight" else "FULL_DIAGNOSTIC"
if args.mode=="lightweight" and not res["errors"]:
    res["status"]="PASS"
    res["gateClass"]="PASS_LIGHTWEIGHT"
    if res["signals"]:
        res["recommendedActions"].append("Carry non-blocking visual signals forward to POST_RUNTIME screenshot QA; do not retry before implementation.")

res["retryPolicy"]={
    "sameFailureSameStrategyMaxAttempts":1,
    "onConfirmedVisualFailure":"classify failure ID, then run tools/character-retry-controller.mjs",
    "metadataOnlyOrMetricOnlySignal":"do not auto-reject"
}

Path(args.out).write_text(json.dumps(res,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(res,ensure_ascii=False,indent=2))
