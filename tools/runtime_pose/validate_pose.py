#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,math
from common import load_json,parse_action_key,limb_joint_names
def point(d,*keys):
    for k in keys:
        if isinstance(d,dict) and k in d:return d[k]
    return None
def d(a,b): return math.hypot(a[0]-b[0],a[1]-b[1])

def _legacy_effectors(pkg):
    if pkg.get("effectors") is not None:
        return pkg["effectors"]
    target=pkg.get("contactPoint")
    limb=pkg.get("limb")
    part=pkg.get("instrument")
    if limb in ("L","R"):
        p=pkg.get("stickTip") or point(pkg.get("joints",{}),"stick_tip")
        return [{"part":part,"limb":limb,"kind":"stick","target":target,"point":p}]
    if limb in ("LF","RF"):
        p=(pkg.get("legReach") or {}).get("footTarget")
        return [{"part":part,"limb":limb,"kind":"pedal","target":target or pkg.get("pedalTarget"),"point":p}]
    if target and pkg.get("stickTip"):
        return [{"part":part,"limb":limb,"kind":"stick","target":target,"point":pkg.get("stickTip")}]
    return []

def _validate_one_effector(e,phase,tol,rebound_min):
    target=e.get("target"); p=e.get("point")
    base={"part":e.get("part"),"limb":e.get("limb"),"kind":e.get("kind")}
    if not target:
        if phase=="hit":
            return {**base,"pass":False,"mode":"missing_authoritative_contact"}
        return {**base,"pass":True,"mode":"contact_not_numerically_available"}
    if not p:
        return {**base,"pass":False,"mode":phase or "unknown","reason":"missing_effector_point"}
    err=d(target,p)
    if phase=="hit":
        return {**base,"pass":err<=tol,"mode":"hit_exact_contact","errorPx":round(err,3),"tolerancePx":tol}
    if phase=="rebound":
        return {**base,"pass":err>=rebound_min,"mode":"rebound_separation","separationPx":round(err,3),"minimumSeparationPx":rebound_min}
    return {**base,"pass":True,"mode":"neutral_no_contact_required","distanceFromContactPx":round(err,3)}

def validate_contacts(pkg,tol=8.0,rebound_min=16.0):
    checks=[_validate_one_effector(e,pkg.get("phase"),tol,rebound_min) for e in _legacy_effectors(pkg)]
    if not checks:
        return {"pass":False,"mode":"no_effectors","checks":[]}
    return {"pass":all(x.get("pass",False) for x in checks),"mode":"multi_effector" if len(checks)>1 else checks[0].get("mode"),"checks":checks}

def validate_contact(pkg,tol=8.0,rebound_min=16.0):
    result=validate_contacts(pkg,tol,rebound_min)
    if len(result["checks"])==1:
        one=dict(result["checks"][0]); one["pass"]=result["pass"]; return one
    return result

def validate_registration(pkg,neutral,stool_tol=12,hip_tol=18):
    s=pkg.get("stoolAnchor"); ns=neutral.get("stoolAnchor"); h=pkg.get("hipAnchor"); nh=neutral.get("hipAnchor")
    se=d(s,ns) if s and ns else 1e9; he=d(h,nh) if h and nh else 1e9
    return {"pass":se<=stool_tol and he<=hip_tol,"stoolShiftPx":round(se,3),"hipShiftPx":round(he,3),"stoolTolerancePx":stool_tol,"hipTolerancePx":hip_tol}

def active_joint_names(pkg):
    limbs=pkg.get("limbs")
    if not limbs:
        if pkg.get("limb"): limbs=[pkg["limb"]]
        elif pkg.get("actionKey"):
            try: limbs=[x["limb"] for x in parse_action_key(pkg["actionKey"])]
            except Exception: limbs=[]
        else: limbs=[]
    out=set()
    for limb in limbs:
        try: out.update(limb_joint_names(limb))
        except ValueError: pass
    return out

def validate_transition(a,b,max_joint=120,max_stool=12,max_hip=18):
    ja=a.get("joints",{}); jb=b.get("joints",{}); shared=set(ja)&set(jb)
    shifts={k:round(d(ja[k],jb[k]),3) for k in shared if isinstance(ja[k],list) and len(ja[k])==2}
    ms=max(shifts.values(),default=0)
    active_names=active_joint_names(b) or active_joint_names(a)
    active={k:v for k,v in shifts.items() if k in active_names}
    inactive={k:v for k,v in shifts.items() if k not in active_names}
    core={k:v for k,v in shifts.items() if k.startswith(("head_","chin","neck","hip_"))}
    s=d(a["stoolAnchor"],b["stoolAnchor"]); h=d(a["hipAnchor"],b["hipAnchor"])
    return {
        "pass":ms<=max_joint and s<=max_stool and h<=max_hip,
        "maxJointShiftPx":round(ms,3),
        "activeLimbMaxJointShiftPx":round(max(active.values(),default=0),3),
        "inactiveLimbMaxJointShiftPx":round(max(inactive.values(),default=0),3),
        "coreMaxJointShiftPx":round(max(core.values(),default=0),3),
        "stoolShiftPx":round(s,3),"hipShiftPx":round(h,3),"jointShifts":shifts
    }
if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--package",required=True); p.add_argument("--neutral"); p.add_argument("--previous"); a=p.parse_args()
    pkg=load_json(a.package); out={"contact":validate_contacts(pkg)}
    if a.neutral: out["registration"]=validate_registration(pkg,load_json(a.neutral))
    if a.previous: out["transition"]=validate_transition(load_json(a.previous),pkg)
    out["pass"]=all(v.get("pass",False) for v in out.values() if isinstance(v,dict)); print(json.dumps(out,ensure_ascii=False,indent=2))
