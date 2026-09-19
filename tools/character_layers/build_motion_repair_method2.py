#!/usr/bin/env python3
import json, hashlib, math, re
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parents[2]
PROTO=ROOT/"character-assets/prototypes/luna_say_maybe_16m"
WORK=ROOT/"character-assets/edit-workspaces/motion-repair-20260920/method2"
WORK.mkdir(parents=True,exist_ok=True)
previous=ROOT/"character-assets/edit-workspaces/motion-repair-20260920/auto/AUTO_REPAIR_PROMOTION_RESULT.json"
neutral=Image.open(ROOT/"character-assets/layers/character/base/neutral.png").convert("RGBA")
N=np.asarray(neutral); H,W=N.shape[:2]
contacts=json.loads((PROTO/"INSTRUMENT_CONTACT_POINTS.json").read_text())
ledger=json.loads((ROOT/"character-assets/edit-workspaces/character-brushup-20260919/BRUSHUP_LEDGER.json").read_text())
fails=json.loads(previous.read_text()).get("failedCandidates",[])

LAND={
 "shoulder_L":(635,342),"shoulder_R":(875,370),
 "hip_LF":(650,620),"hip_RF":(875,655),
 "knee_LF":(535,690),"knee_RF":(682,748),
 "ankle_LF":(430,885),"ankle_RF":(650,902)
}
HEAD=(500,0,930,315)
TORSO=(500,260,1030,590)
STOOL=(765,690,845,1086)
LEFTLEG=(260,610,600,1086)

def contact(part):
    a=(contacts.get("parts",{}).get(part) or {}).get("approximate")
    return None if not a else (int(a["x"]),int(a["y"]))

def parse(k):
    p,l=k.split(":",1); parts=p.split("+"); limbs=l.replace("*","R").split("/")
    if len(limbs)<len(parts): limbs += [limbs[-1]]*(len(parts)-len(limbs))
    return list(zip(parts,limbs))

def safe(s): return re.sub(r"[^a-z0-9_.-]+","_",s.lower())

def bbox(mask):
    ys,xs=np.nonzero(mask)
    return None if not xs.size else {"x":int(xs.min()),"y":int(ys.min()),"width":int(xs.max()-xs.min()+1),"height":int(ys.max()-ys.min()+1)}

def guard(diff,r):
    x1,y1,x2,y2=r; return int(np.count_nonzero(diff[y1:y2,x1:x2]))

def circle(cx,cy,r):
    yy,xx=np.ogrid[:H,:W]; return (xx-cx)**2+(yy-cy)**2<=r*r

out={"schemaVersion":2,"method":"cause-specific second pass: active RF leg corridor or narrow ride-contact corridor","targets":[]}
for f in fails:
    tid=f["id"]; key=f["actionKey"]; phase=f["phase"]
    t=next((z for z in ledger.get("targets",[]) if z.get("id")==tid),None)
    if not t or t.get("terminalId")!="CHAT-MOTION-REPAIR" or t.get("claimState")!="CLAIMED":
        out["targets"].append({"id":tid,"actionKey":key,"phase":phase,"pass":False,"skip":"claim_changed"}); continue
    srcp=ROOT/t["formalGitHubPath"]; src=Image.open(srcp).convert("RGBA"); S=np.asarray(src)
    comps=parse(key); has_bd=any(p=="BD" and l=="RF" for p,l in comps)

    geom=Image.new("L",(W,H),0); d=ImageDraw.Draw(geom)
    for part,limb in comps:
        trg=contact(part)
        if limb in ("L","R"):
            sh=LAND["shoulder_"+limb]
            if trg:
                # Narrower arm corridor but preserve playing-surface contact patch.
                d.line([sh,trg],fill=255,width=190 if phase=="hit" else 220)
                rr=105 if phase=="hit" else 135
                d.ellipse([trg[0]-rr,trg[1]-rr,trg[0]+rr,trg[1]+rr],fill=255)
                d.ellipse([sh[0]-85,sh[1]-85,sh[0]+85,sh[1]+85],fill=255)
        elif limb=="RF":
            hip,knee,ank=LAND["hip_RF"],LAND["knee_RF"],LAND["ankle_RF"]; trg=trg or ankle
            # Explicit active-leg corridor. No blanket pelvis lock for an active RF.
            d.line([hip,knee,ank,trg],fill=255,width=185 if phase=="hit" else 205,joint="curve")
            for p,r in [(hip,72),(knee,78),(ank,88),(trg,95 if phase=="hit" else 115)]:
                d.ellipse([p[0]-r,p[1]-r,p[0]+r,p[1]+r],fill=255)

    G=np.asarray(geom)>0
    # Absolute static locks.
    G[HEAD[1]:HEAD[3],HEAD[0]:HEAD[2]]=False
    # Torso above hip must remain neutral; keep a small RF hip exception below y=590.
    G[TORSO[1]:TORSO[3],TORSO[0]:TORSO[2]]=False
    G[STOOL[1]:STOOL[3],STOOL[0]:STOOL[2]]=False
    if has_bd:
        G[LEFTLEG[1]:LEFTLEG[3],LEFTLEG[0]:LEFTLEG[2]]=False
    else:
        G[620:,:]=False

    diff=np.any(S!=N,axis=2)
    alpha=S[:,:,3]!=N[:,:,3]
    sink=(S[:,:,:3].min(axis=2)<225)&(S[:,:,3]>0)
    nink=(N[:,:,:3].min(axis=2)<225)&(N[:,:,3]>0)
    interest=diff & (alpha|sink|nink)
    D=np.asarray(Image.fromarray((interest.astype(np.uint8)*255),"L").filter(ImageFilter.MaxFilter(13)))>0
    M=G&D
    cand=neutral.copy(); cand.paste(src,(0,0),Image.fromarray((M.astype(np.uint8)*255),"L"))
    Q=np.asarray(cand); nd=np.any(Q!=N,axis=2)
    changed=int(nd.sum()); ratio=changed/(W*H); outside=int(np.count_nonzero(nd&~M))
    checks={
      "changedVisible":changed>=250,
      "ratioWithinLimit":ratio <= (0.12 if len(comps)==1 else 0.16),
      "outsideMaskZero":outside==0,
      "headLocked":guard(nd,HEAD)==0,
      "torsoLocked":guard(nd,TORSO)==0,
      "stoolLocked":guard(nd,STOOL)==0,
      "leftLegLocked":True if not has_bd else guard(nd,LEFTLEG)==0
    }
    preservation=[]
    exact=np.all(Q==S,axis=2)
    for part,limb in comps:
        trg=contact(part)
        if not trg: continue
        radius=55 if phase=="hit" else 75
        reg=circle(trg[0],trg[1],radius)&interest
        denom=int(reg.sum()); kept=int(np.count_nonzero(reg&exact))
        pr=1.0 if denom==0 else kept/denom
        # BD source often includes whole-body fill in larger radii; evaluate only local cue.
        threshold=0.55 if phase=="hit" else 0.40
        preservation.append({"part":part,"limb":limb,"radiusPx":radius,"sourceRelevantPixels":denom,"preservedPixels":kept,"preserveRatio":round(pr,4),"threshold":threshold,"pass":pr>=threshold})
    checks["localContactSourcePreservation"]=all(x["pass"] for x in preservation)
    passed=all(checks.values())

    stem=safe(tid)
    cp=WORK/(stem+"_candidate.png"); cand.save(cp)
    Image.alpha_composite(Image.open(ROOT/"character-assets/layers/drum/drum_base.png").convert("RGBA"),cand).save(WORK/(stem+"_fixed_drum.png"))
    rec={"id":tid,"actionKey":key,"phase":phase,"source":t["formalGitHubPath"],"sourceSha256":hashlib.sha256(srcp.read_bytes()).hexdigest(),
      "candidate":str(cp.relative_to(ROOT)),"candidateSha256":hashlib.sha256(cp.read_bytes()).hexdigest(),
      "hasActiveBDRightFoot":has_bd,"changedPixelsVsNeutral":changed,"changedRatioVsNeutral":round(ratio,8),"changedBBoxVsNeutral":bbox(nd),
      "outsideMaskChangedPixels":outside,"headGuardChangedPixels":guard(nd,HEAD),"torsoGuardChangedPixels":guard(nd,TORSO),
      "stoolGuardChangedPixels":guard(nd,STOOL),"leftLegGuardChangedPixels":guard(nd,LEFTLEG) if has_bd else None,
      "sourceLocalPreservation":preservation,"checks":checks,"pass":passed}
    (WORK/(stem+"_qa.json")).write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n")
    out["targets"].append(rec)
out["passCount"]=sum(bool(x.get("pass")) for x in out["targets"]); out["failCount"]=len(out["targets"])-out["passCount"]
(WORK/"METHOD2_CANDIDATE_SUMMARY.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"targets":len(out["targets"]),"pass":out["passCount"],"fail":out["failCount"]}))
