#!/usr/bin/env python3
import json, os, struct, zlib, hashlib, math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/"character-assets/prototypes/luna_say_maybe_16m"
BACKLOG=BASE/"MOTION_DEFECT_BACKLOG.json"
AMAP=BASE/"ACTION_KEY_ASSET_MAP.json"
CONTACT=BASE/"INSTRUMENT_CONTACT_POINTS.json"
OUT=BASE/"REPAIR_MEASUREMENTS_AUTO.json"

def read_png(path):
    b=Path(path).read_bytes()
    assert b[:8]==b"\x89PNG\r\n\x1a\n", path
    p=8; width=height=ct=bd=interlace=None; chunks=[]
    while p<len(b):
        n=struct.unpack(">I",b[p:p+4])[0]; typ=b[p+4:p+8]; data=b[p+8:p+8+n]; p+=12+n
        if typ==b"IHDR":
            width,height,bd,ct,comp,flt,interlace=struct.unpack(">IIBBBBB",data)
        elif typ==b"IDAT": chunks.append(data)
        elif typ==b"IEND": break
    if bd!=8 or interlace!=0: raise ValueError(f"Unsupported PNG {path}: bitDepth={bd}, interlace={interlace}")
    channels={0:1,2:3,4:2,6:4}[ct]
    raw=zlib.decompress(b"".join(chunks))
    stride=width*channels
    rows=[]; i=0; prev=bytearray(stride)
    def paeth(a,b,c):
        p=a+b-c; pa=abs(p-a); pb=abs(p-b); pc=abs(p-c)
        return a if pa<=pb and pa<=pc else (b if pb<=pc else c)
    for y in range(height):
        f=raw[i]; i+=1
        cur=bytearray(raw[i:i+stride]); i+=stride
        for x in range(stride):
            a=cur[x-channels] if x>=channels else 0
            bb=prev[x]
            c=prev[x-channels] if x>=channels else 0
            if f==1: cur[x]=(cur[x]+a)&255
            elif f==2: cur[x]=(cur[x]+bb)&255
            elif f==3: cur[x]=(cur[x]+((a+bb)//2))&255
            elif f==4: cur[x]=(cur[x]+paeth(a,bb,c))&255
            elif f!=0: raise ValueError(f"Bad filter {f}")
        rows.append(cur); prev=cur
    rgba=[]
    for row in rows:
        out=bytearray(width*4)
        for x in range(width):
            s=x*channels; d=x*4
            if ct==6: r,g,bv,a=row[s:s+4]
            elif ct==2: r,g,bv=row[s:s+3]; a=255
            elif ct==4: g,a=row[s:s+2]; r=bv=g
            else: g=row[s]; r=bv=g; a=255
            out[d:d+4]=bytes((r,g,bv,a))
        rgba.append(out)
    return {"width":width,"height":height,"rows":rgba,"sha256":hashlib.sha256(b).hexdigest()}

def mask_metrics(img, alpha_threshold=0):
    xs=[]; ys=[]; count=0; sx=sy=0.0
    for y,row in enumerate(img["rows"]):
        for x in range(img["width"]):
            if row[x*4+3]>alpha_threshold:
                count+=1; xs.append(x); ys.append(y); sx+=x; sy+=y
    bbox=None if not xs else {"x":min(xs),"y":min(ys),"width":max(xs)-min(xs)+1,"height":max(ys)-min(ys)+1}
    centroid=None if count==0 else {"x":round(sx/count,3),"y":round(sy/count,3)}
    return {"opaquePixelCount":count,"opaqueBBox":bbox,"opaqueCentroid":centroid}

def diff_metrics(a,b):
    assert a["width"]==b["width"] and a["height"]==b["height"]
    xs=[]; ys=[]; count=0; sx=sy=0.0
    alpha_mismatch=0
    for y in range(a["height"]):
        ra=a["rows"][y]; rb=b["rows"][y]
        for x in range(a["width"]):
            i=x*4
            if ra[i:i+4]!=rb[i:i+4]:
                count+=1; xs.append(x); ys.append(y); sx+=x; sy+=y
                if ra[i+3]!=rb[i+3]: alpha_mismatch+=1
    bbox=None if not xs else {"x":min(xs),"y":min(ys),"width":max(xs)-min(xs)+1,"height":max(ys)-min(ys)+1}
    centroid=None if count==0 else {"x":round(sx/count,3),"y":round(sy/count,3)}
    return {"changedPixels":count,"changedRatio":round(count/(a["width"]*a["height"]),8),"diffBBox":bbox,"diffCentroid":centroid,"alphaMismatchPixels":alpha_mismatch}

def bbox_iou(a,b):
    if not a or not b:return None
    ax2=a["x"]+a["width"]; ay2=a["y"]+a["height"]; bx2=b["x"]+b["width"]; by2=b["y"]+b["height"]
    ix=max(0,min(ax2,bx2)-max(a["x"],b["x"])); iy=max(0,min(ay2,by2)-max(a["y"],b["y"]))
    inter=ix*iy; union=a["width"]*a["height"]+b["width"]*b["height"]-inter
    return round(inter/union,8) if union else 1.0

def centroid_shift(a,b):
    if not a or not b:return None
    return round(math.hypot(a["x"]-b["x"],a["y"]-b["y"]),3)

backlog=json.loads(BACKLOG.read_text())
amap=json.loads(AMAP.read_text())
contacts=json.loads(CONTACT.read_text())
entries={e["actionKey"]:e for e in amap.get("entries",[])}
neutral_path="character-assets/layers/character/base/neutral.png"
neutral=read_png(ROOT/neutral_path); neutral_m=mask_metrics(neutral)
cache={neutral_path:(neutral,neutral_m)}
def load(rel):
    if rel not in cache:
        img=read_png(ROOT/rel); cache[rel]=(img,mask_metrics(img))
    return cache[rel]

out={"schemaVersion":1,"generatedFrom":"GitHub Actions exact PNG bytes","canvas":{"width":neutral["width"],"height":neutral["height"]},"neutral":{"path":neutral_path,"sha256":neutral["sha256"],**neutral_m},"actions":{}}
for d in backlog.get("defects",[]):
    key=d["actionKey"]; e=entries.get(key,{})
    hp=e.get("hitAsset") or next((p for p in d.get("relatedAsset",[]) if "hit" in p.lower()),None)
    rp=e.get("reboundAsset") or next((p for p in d.get("relatedAsset",[]) if "rebound" in p.lower()),None)
    rec={"issueId":d["issueId"],"actionKey":key,"hitPath":hp,"reboundPath":rp}
    try:
        hi,hm=load(hp); ri,rm=load(rp)
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
            if q: pts.append({"instrument":p,"x":q["x"],"y":q["y"],"source":"INSTRUMENT_CONTACT_POINTS.json"})
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
