#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,math
from pathlib import Path

HAND_LIMBS={"L","R"}
FOOT_LIMBS={"LF","RF"}
SUPPORTED_LIMBS=HAND_LIMBS|FOOT_LIMBS

def load_json(path): return json.loads(Path(path).read_text(encoding="utf-8"))
def sha256_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for c in iter(lambda:f.read(1024*1024),b""): h.update(c)
    return h.hexdigest()
def dist(a,b): return math.hypot(b[0]-a[0],b[1]-a[1])
def clamp(v,lo,hi): return max(lo,min(hi,v))

def parse_action_key(action_key):
    if ":" not in action_key:
        raise ValueError("actionKey must contain ':'")
    parts_raw,limbs_raw=action_key.split(":",1)
    parts=[x for x in parts_raw.split("+") if x]
    limbs=[x for x in limbs_raw.split("/") if x]
    if not parts or len(parts)!=len(limbs):
        raise ValueError("actionKey part/limb cardinality mismatch: %s" % action_key)
    bad=[x for x in limbs if x not in SUPPORTED_LIMBS]
    if bad:
        raise ValueError("unsupported limb(s): %s" % ",".join(bad))
    return [{"part":part,"limb":limb} for part,limb in zip(parts,limbs)]

def limb_joint_names(limb):
    if limb in HAND_LIMBS:
        s=limb.lower()
        return ["shoulder_"+s,"elbow_"+s,"wrist_"+s]
    if limb in FOOT_LIMBS:
        s="l" if limb=="LF" else "r"
        return ["hip_"+s,"knee_"+s,"ankle_"+s]
    raise ValueError("unsupported limb: %s" % limb)

def two_bone_ik(root,target,l1,l2,bend=1):
    rx,ry=map(float,root); tx,ty=map(float,target); dx,dy=tx-rx,ty-ry
    d=max(1e-9,math.hypot(dx,dy)); reach=min(d,l1+l2-1e-6); minr=abs(l1-l2)+1e-6
    reach=max(reach,minr); ux,uy=dx/d,dy/d
    a=(l1*l1-l2*l2+reach*reach)/(2*reach)
    h=math.sqrt(max(0,l1*l1-a*a)); px,py=rx+a*ux,ry+a*uy
    elbow=[px-bend*uy*h,py+bend*ux*h]
    end=[rx+ux*reach,ry+uy*reach]
    return {"joint":[round(elbow[0],3),round(elbow[1],3)],"end":[round(end[0],3),round(end[1],3)],
            "requestedTarget":[tx,ty],"requestedDistance":round(d,3),"reachDistance":round(reach,3),
            "reachable": d <= l1+l2+1e-6 and d >= abs(l1-l2)-1e-6}
def write_json(path,obj):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
