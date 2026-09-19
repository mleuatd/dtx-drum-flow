#!/usr/bin/env python3
import json, hashlib, math
from pathlib import Path
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"character-assets/prototypes/luna_say_maybe_16m"
BACKLOG=BASE/"MOTION_DEFECT_BACKLOG.json"
AMAP=BASE/"ACTION_KEY_ASSET_MAP.json"
CONTACT=BASE/"INSTRUMENT_CONTACT_POINTS.json"
OUT=BASE/"REPAIR_MEASUREMENTS_AUTO.json"

def load_png(rel):
    path=ROOT/rel
    raw=path.read_bytes()
    im=Image.open(path).convert("RGBA")
    a=np.asarray(im,dtype=np.uint8)
    return {"arr":a,"width":im.width,"height":im.height,"sha256":hashlib.sha256(raw).hexdigest()}

def bbox_from_mask(mask):
    ys,xs=np.nonzero(mask)
    if xs.size==0:return None
    x0,x1=int(xs.min()),int(xs.max()); y0,y1=int(ys.min()),int(ys.max())
    return {"x":x0,"y":y0,"width":x1-x0+1,"height":y1-y0+1}

def centroid_from_mask(mask):
    ys,xs=np.nonzero(mask)
    if xs.size==0:return None
    return {"x":round(float(xs.mean()),3),"y":round(float(ys.mean()),3)}

def mask_metrics(img):
    mask=img["arr"][:,:,3]>0
    return {"opaquePixelCount":int(mask.sum()),"opaqueBBox":bbox_from_mask(mask),"opaqueCentroid":centroid_from_mask(mask)}

def diff_metrics(a,b):
    aa=a["arr"]; bb=b["arr"]
    diff=np.any(aa!=bb,axis=2)
    count=int(diff.sum())
    alpha=int(np.count_nonzero(aa[:,:,3]!=bb[:,:,3]))
    return {"changedPixels":count,"changedRatio":round(count/(a["width"]*a["height"]),8),"diffBBox":bbox_from_mask(diff),"diffCentroid":centroid_from_mask(diff),"alphaMismatchPixels":alpha}

def bbox_iou(a,b):
    if not a or not b:return None
    ax2=a["x"]+a["width"]; ay2=a["y"]+a["height"]; bx2=b["x"]+b["width"]; by2=b["y"]+b["height"]
    ix=max(0,min(ax2,bx2)-max(a["x"],b["x"])); iy=max(0,min(ay2,by2)-max(a["y"],b["y"]))
    inter=ix*iy; union=a["width"]*a["height"]+b["width"]*b["height"]-inter
    return round(inter/union,8) if union else 1.0

def centroid_shift(a,b):
    if not a or not b:return None
    return round(math.hypot(a["x"]-b["x"],a["y"]-b["y"]),3)

def nearest_changed_to_point(diff_mask, x, y):
    ys,xs=np.nonzero(diff_mask)
    if xs.size==0:return None
    d2=(xs-x)**2+(ys-y)**2
    return round(float(np.sqrt(d2.min())),3)

backlog=json.loads(BACKLOG.read_text())
amap=json.loads(AMAP.read_text())
contacts=json.loads(CONTACT.read_text())
entries={e["actionKey"]:e for e in amap.get("entries",[])}
neutral_path="character-assets/layers/character/base/neutral.png"
neutral=load_png(neutral_path); neutral_m=mask_metrics(neutral)
cache={neutral_path:(neutral,neutral_m)}

def load(rel):
    if rel not in cache:
        img=load_png(rel); cache[rel]=(img,mask_metrics(img))
    return cache[rel]

out={"schemaVersion":2,"generatedFrom":"GitHub Actions exact PNG bytes","method":"Pillow RGBA decode + NumPy exact pixel/alpha comparisons","canvas":{"width":neutral["width"],"height":neutral["height"]},"neutral":{"path":neutral_path,"sha256":neutral["sha256"],**neutral_m},"actions":{}}
for d in backlog.get("defects",[]):
    key=d["actionKey"]; e=entries.get(key,{})
    hp=e.get("hitAsset") or next((p for p in d.get("relatedAsset",[]) if "hit" in p.lower()),None)
    rp=e.get("reboundAsset") or next((p for p in d.get("relatedAsset",[]) if "rebound" in p.lower()),None)
    rec={"issueId":d["issueId"],"actionKey":key,"hitPath":hp,"reboundPath":rp}
    try:
        hi,hm=load(hp); ri,rm=load(rp)
        n2h=np.any(neutral["arr"]!=hi["arr"],axis=2)
        n2r=np.any(neutral["arr"]!=ri["arr"],axis=2)
        h2r=np.any(hi["arr"]!=ri["arr"],axis=2)
        rec.update({
          "hit":{"sha256":hi["sha256"],**hm},
          "rebound":{"sha256":ri["sha256"],**rm},
          "neutralToHit":diff_metrics(neutral,hi),
          "neutralToRebound":diff_metrics(neutral,ri),
          "hitToRebound":diff_metrics(hi,ri),
          "shape":{"hitNeutralBboxIoU":bbox_iou(hm["opaqueBBox"],neutral_m["opaqueBBox"]),"reboundNeutralBboxIoU":bbox_iou(rm["opaqueBBox"],neutral_m["opaqueBBox"]),"hitReboundBboxIoU":bbox_iou(hm["opaqueBBox"],rm["opaqueBBox"]),"hitNeutralCentroidShiftPx":centroid_shift(hm["opaqueCentroid"],neutral_m["opaqueCentroid"]),"reboundNeutralCentroidShiftPx":centroid_shift(rm["opaqueCentroid"],neutral_m["opaqueCentroid"]),"hitReboundCentroidShiftPx":centroid_shift(hm["opaqueCentroid"],rm["opaqueCentroid"])}
        })
        parts=key.split(":")[0].split("+")
        pts=[]
        for p in parts:
            q=contacts.get("parts",{}).get(p,{}).get("approximate")
            if q:
                pts.append({"instrument":p,"x":q["x"],"y":q["y"],"source":"INSTRUMENT_CONTACT_POINTS.json","nearestChangedPixelNeutralToHitPx":nearest_changed_to_point(n2h,q["x"],q["y"]),"nearestChangedPixelNeutralToReboundPx":nearest_changed_to_point(n2r,q["x"],q["y"]),"nearestChangedPixelHitToReboundPx":nearest_changed_to_point(h2r,q["x"],q["y"])})
        rec["contactCenters"]=pts
        for phase,dm in [("hit",rec["neutralToHit"]),("rebound",rec["neutralToRebound"])]:
            c=dm.get("diffCentroid")
            rec.setdefault("contactCenterToDiffCentroidPx",{})[phase]=[
              {"instrument":p["instrument"],"distancePx":round(math.hypot(c["x"]-p["x"],c["y"]-p["y"]),3) if c else None}
              for p in pts
            ]
    except Exception as ex:
        rec["measurementError"]=repr(ex)
    out["actions"][key]=rec
OUT.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
print(f"wrote {OUT} actions={len(out['actions'])}")
