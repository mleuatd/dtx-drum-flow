#!/usr/bin/env python3
import json, hashlib, re
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT=Path(__file__).resolve().parents[2]
PROTO=ROOT/"character-assets/prototypes/luna_say_maybe_16m"
BACKLOG=PROTO/"MOTION_DEFECT_BACKLOG.json"
WORK=ROOT/"character-assets/edit-workspaces/motion-repair-20260920/method4"
WORK.mkdir(parents=True,exist_ok=True)
prev=ROOT/"character-assets/edit-workspaces/motion-repair-20260920/method3/METHOD3_PROMOTION_RESULT.json"
neutral=Image.open(ROOT/"character-assets/layers/character/base/neutral.png").convert("RGBA")
N=np.asarray(neutral); H,W=N.shape[:2]
contacts=json.loads((PROTO/"INSTRUMENT_CONTACT_POINTS.json").read_text())
ledger=json.loads((ROOT/"character-assets/edit-workspaces/character-brushup-20260919/BRUSHUP_LEDGER.json").read_text())
fails=json.loads(prev.read_text()).get("failedCandidates",[])
backlog=json.loads(BACKLOG.read_text())
forced_hold_targets=[]
rd_sn_defect=next((d for d in backlog.get("defects",[]) if d.get("actionKey")=="RD+SN:R/L"),None)
if rd_sn_defect and (rd_sn_defect.get("claim") or {}).get("state")=="CLAIMED" and (rd_sn_defect.get("claim") or {}).get("owner") in ("CHATGPT-FRONT","CHAT-PASS2-BACK"):
    forced_hold_targets += [{"id":"rd_sn_r_l_hit","actionKey":"RD+SN:R/L","phase":"hit","_holdRepairClaim":True},{"id":"rd_sn_r_l_rebound","actionKey":"RD+SN:R/L","phase":"rebound","_holdRepairClaim":True}]
rd_r_defect=next((d for d in backlog.get("defects",[]) if d.get("actionKey")=="RD:R"),None)
if rd_r_defect and (rd_r_defect.get("claim") or {}).get("state")=="CLAIMED" and (rd_r_defect.get("claim") or {}).get("owner") in ("CHATGPT-FRONT","CHAT-PASS2-BACK"):
    forced_hold_targets += [{"id":"rd_r_hit","actionKey":"RD:R","phase":"hit","_holdRepairClaim":True},{"id":"rd_r_rebound","actionKey":"RD:R","phase":"rebound","_holdRepairClaim":True}]
m015_defect=next((d for d in backlog.get("defects",[]) if d.get("actionKey")=="BD+HH+SN:RF/R/L"),None)
if m015_defect and (m015_defect.get("claim") or {}).get("state")=="CLAIMED" and (m015_defect.get("claim") or {}).get("owner")=="CHAT-PASS2-BACK":
    forced_hold_targets += [
      {"id":"bd_hh_sn_rf_r_l_hit_refresh","actionKey":"BD+HH+SN:RF/R/L","phase":"hit","_holdRepairClaim":True},
      {"id":"bd_hh_sn_rf_r_l_rebound_refresh","actionKey":"BD+HH+SN:RF/R/L","phase":"rebound","_holdRepairClaim":True}
    ]
# Active PASS2 HOLD claim overrides a stale failedCandidates entry with the
# same id; otherwise the stale entry lacks _holdRepairClaim and is skipped.
forced_by_id={x.get("id"):x for x in forced_hold_targets}
fails=[forced_by_id.get(x.get("id"),x) for x in fails]
seen={x.get("id") for x in fails}
fails += [x for x in forced_hold_targets if x.get("id") not in seen]

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
    hold_repair_claim=bool(f.get("_holdRepairClaim"))
    legacy_claim=bool(t and t.get("terminalId")=="CHAT-MOTION-REPAIR" and t.get("claimState")=="CLAIMED")
    if not t or not (legacy_claim or hold_repair_claim):
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
    # HOLD repair refinement for RD+SN rebound: keep the already-good left SN
    # motion, but restrict the right RD source patch to the upper hand/stick
    # corridor. This intentionally excludes the lower duplicate/disconnected
    # right-hand fragment seen in the formal rebound while leaving locked body
    # regions on the neutral baseline.
    if tid in ("rd_sn_r_l_hit","rd_sn_r_l_rebound","rd_r_hit","rd_r_rebound","bd_hh_sn_rf_r_l_hit_refresh","bd_hh_sn_rf_r_l_rebound_refresh"):
        # PASS2 pair repair: build one coherent RD right-side corridor for BOTH
        # phases instead of trying to promote a rebound-only fix. Keep the
        # already-good left SN motion and reject the lower/rear duplicate RD
        # limb by limiting source transplant to the upper shoulder-hand-stick
        # corridor. Body core/head/stool remain neutral-locked above.
        local=np.zeros((H,W),dtype=bool)
        if "rd_sn" in tid:
            local[300:620,340:700]=True   # left SN hand/stick/forearm
        if "bd_hh_sn" in tid:
            # MOTION-015 visual-fail refinement. Keep the current formal pair
            # as the source authority but admit only compact, phase-specific
            # hand/stick corridors plus the already-proven RF pedal corridor.
            # HH contact is far left at x=190,y=390; include the complete
            # right-hand-to-HH stick path so rebound contact evidence is not
            # clipped by the previous x>=760 local box.
            local[300:600,300:700]=True   # L: hand/grip/SN stick corridor
            local[280:535,140:1110]=True  # R: hand/grip/HH stick to HH contact
            local[590:1010,600:910]=True  # RF: BD leg/pedal corridor
        if phase=="hit":
            local[245:525,830:1135]=True # hit: one upper right RD corridor
        else:
            local[205:442,850:1115]=True # rebound: one upper right RD corridor
        M &= local
    # MOTION-015 method5: topology-aware fragment rejection.  Method4's
    # rectangular local corridor passed pixel QA but leaked disconnected white
    # source patches into the composite.  For this pair, keep only changed-ink
    # components that are spatially supported by source ink; this removes
    # opaque/white splice islands while retaining hand/stick/RF strokes.
    if "bd_hh_sn" in tid:
        src_ink=(S[:,:,:3].min(axis=2)<225)&(S[:,:,3]>0)
        support=np.asarray(Image.fromarray((src_ink.astype(np.uint8)*255),"L").filter(ImageFilter.MaxFilter(9)))>0
        M &= support
        # Method6: reject tiny disconnected changed-ink islands. Keep only
        # source-supported components that are large enough to be real linework
        # or that touch an active instrument contact neighborhood. This is
        # intentionally applied after the method5 support mask so RF/HH/SN
        # contact corridors remain protected while floating fragments are
        # removed without widening any transplant rectangle.
        raw=(M & interest).astype(np.uint8)
        seen=np.zeros((H,W),dtype=bool); keep=np.zeros((H,W),dtype=bool)
        active_contacts=[cp(p) for p,l in comps if cp(p)]
        for yy in range(H):
            for xx in range(W):
                if not raw[yy,xx] or seen[yy,xx]: continue
                stack=[(xx,yy)]; seen[yy,xx]=True; pts=[]
                while stack:
                    px,py=stack.pop(); pts.append((px,py))
                    for nx,ny in ((px-1,py),(px+1,py),(px,py-1),(px,py+1)):
                        if 0<=nx<W and 0<=ny<H and raw[ny,nx] and not seen[ny,nx]:
                            seen[ny,nx]=True; stack.append((nx,ny))
                touches_contact=any(any((px-cx)**2+(py-cy)**2<=80**2 for px,py in pts) for cx,cy in active_contacts)
                if len(pts)>=18 or touches_contact:
                    for px,py in pts: keep[py,px]=True
        keep=np.asarray(Image.fromarray((keep.astype(np.uint8)*255),"L").filter(ImageFilter.MaxFilter(5)))>0
        M &= keep
        # Method7: explicit left-hand/stick continuity reconstruction.
        # Topology filtering alone retained a confused grip and rebound
        # zig-zag fragment. Restrict L/SN to one narrow connected corridor.
        if any(p=="SN" and l=="L" for p,l in comps):
            sn=cp("SN") or (500,520)
            sh=LAND["shoulder_L"]
            corridor=Image.new("L",(W,H),0); cd=ImageDraw.Draw(corridor)
            grip=(505,455) if phase=="hit" else (475,430)
            cd.line([sh,grip,sn],fill=255,width=76 if phase=="hit" else 56,joint="curve")
            cd.ellipse([grip[0]-(54 if phase=="hit" else 42),grip[1]-(54 if phase=="hit" else 42),grip[0]+(54 if phase=="hit" else 42),grip[1]+(54 if phase=="hit" else 42)],fill=255)
            C=np.asarray(corridor)>0
            left_zone=np.zeros((H,W),dtype=bool); left_zone[300:600,280:720]=True
            # Preserve the actual SN contact disk after continuity cleanup;
            # visual cleanup applies to the approach corridor, not the contact itself.
            contact_keep=np.zeros((H,W),dtype=bool)
            if phase=="hit":
                yy,xx=np.ogrid[:H,:W]
                contact_keep=((xx-sn[0])**2+(yy-sn[1])**2 <= 54**2) & src_ink
            M=(M & ~left_zone) | ((M & C & left_zone) | contact_keep)
            # Method10: direct bounded cleanup after full-resolution Method9 review.
            # These tiny regions were confirmed by full-resolution review and
            # are outside the intended connected hand→stick/contact path.
            if phase=="rebound":
                reject=np.zeros((H,W),dtype=bool)
                # Full-resolution Method9 review: remaining artifacts are a
                # diagonal/triangular island immediately above the left tom
                # and two short floating strokes below the skirt/left thigh.
                reject[330:455,430:555]=True
                reject[700:815,610:735]=True
                M &= ~reject
                # Re-open only a narrow connected SN stick/contact route.
                route=Image.new("L",(W,H),0); rd=ImageDraw.Draw(route)
                rd.line([(505,455),(470,430),sn],fill=255,width=34,joint="curve")
                R=np.asarray(route)>0
                M |= (R & src_ink & left_zone)
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
