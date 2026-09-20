#!/usr/bin/env python3
import json, hashlib, math, re
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parents[2]
PROTO=ROOT/"character-assets/prototypes/luna_say_maybe_16m"
WORK=ROOT/"character-assets/edit-workspaces/motion-repair-20260920/auto"
WORK.mkdir(parents=True,exist_ok=True)

neutral=Image.open(ROOT/"character-assets/layers/character/base/neutral.png").convert("RGBA")
N=np.asarray(neutral)
H,W=N.shape[:2]
contacts=json.loads((PROTO/"INSTRUMENT_CONTACT_POINTS.json").read_text())
amap=json.loads((PROTO/"ACTION_KEY_ASSET_MAP.json").read_text())
backlog=json.loads((PROTO/"MOTION_DEFECT_BACKLOG.json").read_text())
measure=json.loads((PROTO/"REPAIR_MEASUREMENTS_AUTO.json").read_text())
ledger_path=ROOT/"character-assets/edit-workspaces/character-brushup-20260919/BRUSHUP_LEDGER.json"
ledger=json.loads(ledger_path.read_text())

entries={e["actionKey"]:e for e in amap.get("entries",[])}
targets=[t for t in ledger.get("targets",[]) if ((t.get("terminalId")=="CHAT-MOTION-REPAIR" and t.get("claimState")=="CLAIMED") or (t.get("terminalId")=="CHAT-PASS2-BACK" and t.get("claimState")=="PASS2_CLAIMED"))]

LANDMARKS={
 "shoulder_L":(635,342),"shoulder_R":(875,370),
 "hip_LF":(650,620),"hip_RF":(875,655),
 "knee_LF":(535,690),"knee_RF":(682,748),
 "ankle_LF":(430,885),"ankle_RF":(650,902),
}
HEAD=(500,0,930,315)
PELVIS=(560,570,980,820)
STOOL=(765,690,845,1086)

def parse_action(k):
    left,right=k.split(":",1)
    ps=left.split("+")
    ls=right.replace("*","R").split("/")
    if len(ls)<len(ps):
        ls += [ls[-1]]*(len(ps)-len(ls))
    return list(zip(ps,ls))

def pt_for(part):
    a=(contacts.get("parts",{}).get(part) or {}).get("approximate")
    return None if not a else (int(a["x"]),int(a["y"]))

def bbox(mask):
    ys,xs=np.nonzero(mask)
    if xs.size==0:return None
    return {"x":int(xs.min()),"y":int(ys.min()),"width":int(xs.max()-xs.min()+1),"height":int(ys.max()-ys.min()+1)}

def circle_mask(cx,cy,r):
    yy,xx=np.ogrid[:H,:W]
    return (xx-cx)**2+(yy-cy)**2<=r*r

def guard_count(diff, rect):
    x1,y1,x2,y2=rect
    return int(np.count_nonzero(diff[y1:y2,x1:x2]))

def safe_name(s):
    return re.sub(r"[^A-Za-z0-9_.-]+","_",s).strip("_").lower()

summary={"schemaVersion":1,"method":"neutral-locked semantic corridor + changed-ink/alpha transplant","targets":[]}
for t in targets:
    key=t["actionKey"]; phase=t["phase"]; rel=t["formalGitHubPath"]
    src_path=ROOT/rel
    if not src_path.exists():
        summary["targets"].append({"id":t["id"],"actionKey":key,"phase":phase,"pass":False,"reasons":["source_missing"],"source":rel}); continue
    src=Image.open(src_path).convert("RGBA"); S=np.asarray(src)
    if S.shape!=N.shape:
        summary["targets"].append({"id":t["id"],"actionKey":key,"phase":phase,"pass":False,"reasons":["canvas_mismatch"],"source":rel}); continue
    components=parse_action(key)
    geom=Image.new("L",(W,H),0); gd=ImageDraw.Draw(geom)
    has_foot=False
    measure_action=measure.get("actions",{}).get(key,{})
    diffcent=(measure_action.get("neutralToHit" if phase=="hit" else "neutralToRebound") or {}).get("diffCentroid")
    for part,limb in components:
        target=pt_for(part)
        if limb in ("L","R"):
            sh=LANDMARKS["shoulder_"+limb]
            end=target if target else ((int(diffcent["x"]),int(diffcent["y"])) if diffcent else sh)
            width=210 if phase=="hit" else 245
            gd.line([sh,end],fill=255,width=width)
            gd.ellipse([sh[0]-95,sh[1]-95,sh[0]+95,sh[1]+95],fill=255)
            er=145 if phase=="hit" else 195
            gd.ellipse([end[0]-er,end[1]-er,end[0]+er,end[1]+er],fill=255)
            if diffcent:
                dc=(int(diffcent["x"]),int(diffcent["y"]))
                gd.line([sh,dc],fill=255,width=190)
                gd.ellipse([dc[0]-135,dc[1]-135,dc[0]+135,dc[1]+135],fill=255)
        elif limb in ("LF","RF"):
            has_foot=True
            hip=LANDMARKS["hip_"+limb]; knee=LANDMARKS["knee_"+limb]; ankle=LANDMARKS["ankle_"+limb]
            end=target if target else ankle
            gd.line([hip,knee,ankle,end],fill=255,width=205,joint="curve")
            for p,r in [(hip,80),(knee,85),(ankle,95),(end,115)]:
                gd.ellipse([p[0]-r,p[1]-r,p[0]+r,p[1]+r],fill=255)

    G=np.asarray(geom)>0
    # Static locks.
    G[HEAD[1]:HEAD[3],HEAD[0]:HEAD[2]]=False
    G[PELVIS[1]:PELVIS[3],PELVIS[0]:PELVIS[2]]=False
    G[STOOL[1]:STOOL[3],STOOL[0]:STOOL[2]]=False
    if not has_foot:
        G[620:,:]=False

    diff=np.any(S!=N,axis=2)
    alpha_mismatch=S[:,:,3]!=N[:,:,3]
    src_ink=(S[:,:,:3].min(axis=2)<225)&(S[:,:,3]>0)
    neu_ink=(N[:,:,:3].min(axis=2)<225)&(N[:,:,3]>0)
    interest=diff & (alpha_mismatch | src_ink | neu_ink)
    dil=Image.fromarray((interest.astype(np.uint8)*255),"L").filter(ImageFilter.MaxFilter(15))
    D=np.asarray(dil)>0
    M=G & D

    mask=Image.fromarray((M.astype(np.uint8)*255),"L")
    cand=neutral.copy(); cand.paste(src,(0,0),mask)
    Q=np.asarray(cand)
    ndiff=np.any(Q!=N,axis=2)
    changed=int(ndiff.sum()); ratio=changed/(W*H)
    headc=guard_count(ndiff,HEAD); pelvisc=guard_count(ndiff,PELVIS); stoolc=guard_count(ndiff,STOOL)
    lower=int(np.count_nonzero(ndiff[620:,:])) if not has_foot else None
    outside=int(np.count_nonzero(ndiff & ~M))

    preserves=[]
    for part,limb in components:
        p=pt_for(part)
        if not p: continue
        r=125 if phase=="hit" else 180
        region=circle_mask(p[0],p[1],r)
        relevant=region & interest
        denom=int(relevant.sum())
        if denom:
            exact=np.all(Q==S,axis=2)
            preserved=int(np.count_nonzero(relevant & exact))
            preserves.append({"part":part,"limb":limb,"radiusPx":r,"sourceRelevantPixels":denom,"preservedPixels":preserved,"preserveRatio":round(preserved/denom,4)})
    if phase=="hit":
        preserve_pass=all(x["preserveRatio"]>=0.65 for x in preserves) if preserves else True
    else:
        preserve_pass=all(x["preserveRatio"]>=0.45 for x in preserves) if preserves else True

    max_ratio=0.10 if len(components)==1 else 0.14
    checks={
      "changedVisible": changed>=250,
      "changedRatioWithinLimit": ratio<=max_ratio,
      "outsideSemanticMaskZero": outside==0,
      "headLocked": headc==0,
      "pelvisLocked": pelvisc==0,
      "stoolLocked": stoolc==0,
      "inactiveLowerLocked": True if has_foot else lower==0,
      "localSourcePreservation": preserve_pass,
    }
    passed=all(checks.values())
    stem=safe_name(t["id"])
    cp=WORK/(stem+"_candidate.png"); qp=WORK/(stem+"_qa.json")
    cand.save(cp)
    comp=Image.alpha_composite(Image.open(ROOT/"character-assets/layers/drum/drum_base.png").convert("RGBA"),cand)
    comp.save(WORK/(stem+"_fixed_drum.png"))
    rec={
      "id":t["id"],"actionKey":key,"phase":phase,"source":rel,
      "sourceSha256":hashlib.sha256(src_path.read_bytes()).hexdigest(),
      "candidate":str(cp.relative_to(ROOT)),
      "candidateSha256":hashlib.sha256(cp.read_bytes()).hexdigest(),
      "components":[{"part":p,"limb":l,"contact":pt_for(p)} for p,l in components],
      "maskPixelCount":int(M.sum()),"changedPixelsVsNeutral":changed,"changedRatioVsNeutral":round(ratio,8),
      "changedBBoxVsNeutral":bbox(ndiff),"headGuardChangedPixels":headc,"pelvisGuardChangedPixels":pelvisc,
      "stoolGuardChangedPixels":stoolc,"inactiveLowerChangedPixels":lower,"outsideMaskChangedPixels":outside,
      "sourceLocalPreservation":preserves,"checks":checks,"pass":passed
    }
    qp.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n")
    summary["targets"].append(rec)

summary["passCount"]=sum(1 for x in summary["targets"] if x.get("pass"))
summary["failCount"]=sum(1 for x in summary["targets"] if not x.get("pass"))
(WORK/"AUTO_REPAIR_CANDIDATE_SUMMARY.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"targets":len(summary["targets"]),"pass":summary["passCount"],"fail":summary["failCount"]}))
