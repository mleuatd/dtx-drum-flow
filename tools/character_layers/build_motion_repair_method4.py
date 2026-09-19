#!/usr/bin/env python3
import json, hashlib, re
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parents[2]
PROTO=ROOT/"character-assets/prototypes/luna_say_maybe_16m"
WORK=ROOT/"character-assets/edit-workspaces/motion-repair-20260920/method4"
WORK.mkdir(parents=True,exist_ok=True)
prev=ROOT/"character-assets/edit-workspaces/motion-repair-20260920/method3/METHOD3_PROMOTION_RESULT.json"
neutral=Image.open(ROOT/"character-assets/layers/character/base/neutral.png").convert("RGBA")
N=np.asarray(neutral); H,W=N.shape[:2]
contacts=json.loads((PROTO/"INSTRUMENT_CONTACT_POINTS.json").read_text())
ledger=json.loads((ROOT/"character-assets/edit-workspaces/character-brushup-20260919/BRUSHUP_LEDGER.json").read_text())
fails=json.loads(prev.read_text()).get("failedCandidates",[])

LAND={"shoulder_L":(635,342),"shoulder_R":(875,370),"hip_RF":(875,655),"knee_RF":(682,748),"ankle_RF":(650,902)}
# Head core derived from neutral landmarks head_top=(720,30), chin=(615,300);
# do not lock the neutral right wrist/stick zone x~975..1025.
HEAD_CORE=(500,0,840,315)
TORSO_CORE=(650,320,900,600)
STOOL=(765,690,845,1086)
LEFTLEG=(260,610,600,1086)

def cp(part):
    a=(contacts.get("parts",{}).get(part) or {}).get("approximate")
    return None if not a else (int(a["x"]),int(a["y"]))
def parse(k):
    p,l=k.split(":",1); ps=p.split("+"); ls=l.replace("*","R").split("/")
    if len(ls)<len(ps): ls += [ls[-1]]*(len(ps)-len(ls))
    return list(zip(ps,ls))
def safe(s): return re.sub(r"[^a-z0-9_.-]+","_",s.lower())
def guard(diff,r):
    x1,y1,x2,y2=r; return int(np.count_nonzero(diff[y1:y2,x1:x2]))
def bbox(mask):
    ys,xs=np.nonzero(mask)
    return None if not xs.size else {"x":int(xs.min()),"y":int(ys.min()),"width":int(xs.max()-xs.min()+1),"height":int(ys.max()-ys.min()+1)}
def circ(x,y,r):
    yy,xx=np.ogrid[:H,:W]; return (xx-x)**2+(yy-y)**2<=r*r

out={"schemaVersion":4,"method":"RD-specific right-side release using neutral head landmarks","headCore":HEAD_CORE,"targets":[]}
for f in fails:
    tid,key,phase=f["id"],f["actionKey"],f["phase"]
    t=next((z for z in ledger.get("targets",[]) if z.get("id")==tid),None)
    if not t or t.get("terminalId")!="CHAT-MOTION-REPAIR" or t.get("claimState")!="CLAIMED":
        out["targets"].append({"id":tid,"actionKey":key,"phase":phase,"pass":False,"skip":"claim_changed"}); continue
    srcp=ROOT/t["formalGitHubPath"]; src=Image.open(srcp).convert("RGBA"); S=np.asarray(src)
    comps=parse(key); has_bd=any(p=="BD" and l=="RF" for p,l in comps)
    geom=Image.new("L",(W,H),0); d=ImageDraw.Draw(geom)
    for part,limb in comps:
        target=cp(part)
        if limb in ("L","R") and target:
            sh=LAND["shoulder_"+limb]
            width=175 if phase=="hit" else 205
            d.line([sh,target],fill=255,width=width)
            rr=105 if phase=="hit" else 135
            d.ellipse([target[0]-rr,target[1]-rr,target[0]+rr,target[1]+rr],fill=255)
        elif limb=="RF":
            hip,knee,ank=LAND["hip_RF"],LAND["knee_RF"],LAND["ankle_RF"]; target=target or ank
            d.line([hip,knee,ank,target],fill=255,width=185 if phase=="hit" else 205,joint="curve")
            for p,r in [(hip,70),(knee,78),(ank,88),(target,95 if phase=="hit" else 115)]:
                d.ellipse([p[0]-r,p[1]-r,p[0]+r,p[1]+r],fill=255)
    G=np.asarray(geom)>0
    G[HEAD_CORE[1]:HEAD_CORE[3],HEAD_CORE[0]:HEAD_CORE[2]]=False
    G[TORSO_CORE[1]:TORSO_CORE[3],TORSO_CORE[0]:TORSO_CORE[2]]=False
    G[STOOL[1]:STOOL[3],STOOL[0]:STOOL[2]]=False
    if has_bd: G[LEFTLEG[1]:LEFTLEG[3],LEFTLEG[0]:LEFTLEG[2]]=False
    else: G[620:,:]=False

    diff=np.any(S!=N,axis=2); alpha=S[:,:,3]!=N[:,:,3]
    sink=(S[:,:,:3].min(axis=2)<225)&(S[:,:,3]>0); nink=(N[:,:,:3].min(axis=2)<225)&(N[:,:,3]>0)
    interest=diff&(alpha|sink|nink)
    D=np.asarray(Image.fromarray((interest.astype(np.uint8)*255),"L").filter(ImageFilter.MaxFilter(11)))>0
    M=G&D
    cand=neutral.copy(); cand.paste(src,(0,0),Image.fromarray((M.astype(np.uint8)*255),"L"))
    Q=np.asarray(cand); nd=np.any(Q!=N,axis=2); exact=np.all(Q==S,axis=2)
    changed=int(nd.sum()); ratio=changed/(W*H)
    preservation=[]
    for part,limb in comps:
        target=cp(part)
        if not target: continue
        radius=48 if phase=="hit" else 65
        reg=circ(target[0],target[1],radius)&interest
        denom=int(reg.sum()); kept=int(np.count_nonzero(reg&exact)); pr=1 if denom==0 else kept/denom
        threshold=.60 if phase=="hit" else .40
        preservation.append({"part":part,"limb":limb,"radiusPx":radius,"sourceRelevantPixels":denom,"preservedPixels":kept,"preserveRatio":round(pr,4),"threshold":threshold,"pass":pr>=threshold})
    checks={"changedVisible":changed>=250,"ratioWithinLimit":ratio<=(.10 if len(comps)==1 else .16),
      "outsideMaskZero":int(np.count_nonzero(nd&~M))==0,"headCoreLocked":guard(nd,HEAD_CORE)==0,
      "torsoCoreLocked":guard(nd,TORSO_CORE)==0,"stoolLocked":guard(nd,STOOL)==0,
      "leftLegLocked":True if not has_bd else guard(nd,LEFTLEG)==0,
      "localContactSourcePreservation":all(x["pass"] for x in preservation)}
    passed=all(checks.values()); stem=safe(tid); cpath=WORK/(stem+"_candidate.png"); cand.save(cpath)
    Image.alpha_composite(Image.open(ROOT/"character-assets/layers/drum/drum_base.png").convert("RGBA"),cand).save(WORK/(stem+"_fixed_drum.png"))
    rec={"id":tid,"actionKey":key,"phase":phase,"source":t["formalGitHubPath"],"sourceSha256":hashlib.sha256(srcp.read_bytes()).hexdigest(),
      "candidate":str(cpath.relative_to(ROOT)),"candidateSha256":hashlib.sha256(cpath.read_bytes()).hexdigest(),
      "changedPixelsVsNeutral":changed,"changedRatioVsNeutral":round(ratio,8),"changedBBoxVsNeutral":bbox(nd),
      "headCoreGuardChangedPixels":guard(nd,HEAD_CORE),"torsoCoreGuardChangedPixels":guard(nd,TORSO_CORE),
      "stoolGuardChangedPixels":guard(nd,STOOL),"leftLegGuardChangedPixels":guard(nd,LEFTLEG) if has_bd else None,
      "sourceLocalPreservation":preservation,"checks":checks,"pass":passed}
    (WORK/(stem+"_qa.json")).write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n"); out["targets"].append(rec)
out["passCount"]=sum(bool(x.get("pass")) for x in out["targets"]); out["failCount"]=len(out["targets"])-out["passCount"]
(WORK/"METHOD4_CANDIDATE_SUMMARY.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"targets":len(out["targets"]),"pass":out["passCount"],"fail":out["failCount"]}))
