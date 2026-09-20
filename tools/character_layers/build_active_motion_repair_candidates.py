#!/usr/bin/env python3
import json, hashlib, math, re, os
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
legacy_targets=[t for t in ledger.get("targets",[]) if ((t.get("terminalId")=="CHAT-MOTION-REPAIR" and t.get("claimState")=="CLAIMED") or (t.get("terminalId")=="CHAT-PASS2-BACK" and t.get("claimState")=="PASS2_CLAIMED"))]
claim_owner=os.environ.get("CLAIM_OWNER","").strip()
queue_keys={x.strip() for x in os.environ.get("ACTION_KEYS","").split(",") if x.strip()}
hold_claimed_keys={d.get("actionKey") for d in backlog.get("defects",[]) if (d.get("claim") or {}).get("state")=="CLAIMED" and (not claim_owner or (d.get("claim") or {}).get("owner")==claim_owner) and (not queue_keys or d.get("actionKey") in queue_keys)}
targets=[]
seen=set()
for t in ledger.get("targets",[]):
    if t in legacy_targets or t.get("actionKey") in hold_claimed_keys:
        if t.get("id") not in seen:
            targets.append(t); seen.add(t.get("id"))

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
    formal_source_sha=hashlib.sha256(src_path.read_bytes()).hexdigest()

    # MOTION-012: deterministic standalone HT reconstruction.
    # Use one stable approved arm shape for both phases; remove the neutral
    # resting stick first, then draw exactly one HT stick per phase.
    if key=="HT:R":
        hh_rel="character-assets/layers/character/hh/hit_r.png"
        hh=Image.open(ROOT/hh_rel).convert("RGBA")
        rebuilt=neutral.copy()

        # Remove only the exposed neutral resting-stick pixels before the grip.
        # Do not cut a wide transparent channel through the hand/sleeve: that
        # produced the white triangular fragments seen in the rebound artifact.
        erase=Image.new("L",(W,H),0); ed=ImageDraw.Draw(erase)
        old_tip=(405,390); erase_end=(488,458)
        ed.line([old_tip,erase_end],fill=255,width=28)
        ed.ellipse([old_tip[0]-13,old_tip[1]-13,old_tip[0]+13,old_tip[1]+13],fill=255)
        E=np.asarray(erase)>0
        arr=np.array(rebuilt)
        arr[E,3]=0
        rebuilt=Image.fromarray(arr,"RGBA")

        # Stable forearm/hand from the approved HH hit authority. The anatomical
        # mask follows the sleeve/hand shape, so opaque white pixels are safe and
        # no rectangular source boundary can enter the candidate.
        arm=Image.new("L",(W,H),0); ad=ImageDraw.Draw(arm)
        pts=[(650,390),(595,405),(545,430),(500,452)]
        grip=(500,452)
        ad.line(pts,fill=255,width=92,joint="curve")
        for p,r in [(pts[1],46),(pts[2],48),(grip,52)]:
            ad.ellipse([p[0]-r,p[1]-r,p[0]+r,p[1]+r],fill=255)
        A=np.asarray(arm)>0
        A[HEAD[1]:HEAD[3],HEAD[0]:HEAD[2]]=False
        A[PELVIS[1]:PELVIS[3],PELVIS[0]:PELVIS[2]]=False
        A[STOOL[1]:STOOL[3],STOOL[0]:STOOL[2]]=False
        A[620:,:]=False

        # The approved HH arm authority also contains its own HH stick. Exclude
        # that stick corridor from the transplant, otherwise the HT candidate
        # visibly carries two sticks. Preserve only a compact grip disk so the
        # newly drawn HT stick remains connected to the hand.
        old_hh=Image.new("L",(W,H),0); ohd=ImageDraw.Draw(old_hh)
        ohd.line([(405,390),(500,470)],fill=255,width=34)
        O=np.asarray(old_hh)>0
        yy,xx=np.ogrid[:H,:W]
        grip_keep=(xx-grip[0])**2+(yy-grip[1])**2<=24**2
        A &= (~O | grip_keep)

        rebuilt.paste(hh,(0,0),Image.fromarray((A.astype(np.uint8)*255),"L"))

        # One and only one HT stick. Rebound differs by release angle only,
        # avoiding the previously broken alternate-arm source.
        ht=pt_for("HT") or (575,360)
        tip=ht if phase=="hit" else (ht[0]+14,ht[1]-36)
        rd=ImageDraw.Draw(rebuilt)
        rd.line([grip,tip],fill=(20,20,20,255),width=5)
        rd.line([(grip[0]+3,grip[1]-1),(tip[0]+3,tip[1]-1)],fill=(65,65,65,255),width=2)

        src=rebuilt
        S=np.asarray(src)

    # MOTION-014: the formal BD+SN pair contains known rectangular splice/
    # stick-dropout corruption. Rebuild the candidate source deterministically
    # from two already-approved live authorities instead of reusing that corrupt
    # combo drawing: SN:L for the left arm/stick and BD:RF for the right foot.
    if key=="BD+SN:RF/L":
        sn_rel=("character-assets/layers/character/sn/hit_l.png"
                if phase=="hit" else
                "character-assets/layers/character/sn/rebound_l.png")
        bd_rel=("character-assets/layers/character/bd/hit_rf.png"
                if phase=="hit" else
                "character-assets/layers/character/bd/rebound_rf.png")
        sn=Image.open(ROOT/sn_rel).convert("RGBA")
        bd=Image.open(ROOT/bd_rel).convert("RGBA")
        combo=neutral.copy()

        # Tight left-arm/snare corridor.
        sn_mask=Image.new("L",(W,H),0); sd=ImageDraw.Draw(sn_mask)
        sh=LANDMARKS["shoulder_L"]; end=pt_for("SN")
        width=150 if phase=="hit" else 175
        sd.line([sh,end],fill=255,width=width)
        sr=62; er=115 if phase=="hit" else 145
        sd.ellipse([sh[0]-sr,sh[1]-sr,sh[0]+sr,sh[1]+sr],fill=255)
        sd.ellipse([end[0]-er,end[1]-er,end[0]+er,end[1]+er],fill=255)
        sm=np.asarray(sn_mask)>0
        sm[HEAD[1]:HEAD[3],HEAD[0]:HEAD[2]]=False
        sm[PELVIS[1]:PELVIS[3],PELVIS[0]:PELVIS[2]]=False
        sm[STOOL[1]:STOOL[3],STOOL[0]:STOOL[2]]=False
        combo.paste(sn,(0,0),Image.fromarray((sm.astype(np.uint8)*255),"L"))

        # Tight right-foot/bass-drum corridor.
        foot_mask=Image.new("L",(W,H),0); fd=ImageDraw.Draw(foot_mask)
        hip=LANDMARKS["hip_RF"]; knee=LANDMARKS["knee_RF"]; ankle=LANDMARKS["ankle_RF"]; bend=pt_for("BD") or ankle
        fd.line([hip,knee,ankle,bend],fill=255,width=135,joint="curve")
        for p,r in [(knee,65),(ankle,75),(bend,90)]:
            fd.ellipse([p[0]-r,p[1]-r,p[0]+r,p[1]+r],fill=255)
        fm=np.asarray(foot_mask)>0
        fm[STOOL[1]:STOOL[3],STOOL[0]:STOOL[2]]=False
        combo.paste(bd,(0,0),Image.fromarray((fm.astype(np.uint8)*255),"L"))

        src=combo
        S=np.asarray(src)

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
            # When an authoritative instrument contact exists, keep the arm
            # corridor tight around shoulder -> contact. Extending the mask toward
            # the whole-frame diff centroid was pulling unrelated hair/torso splice
            # artifacts into combo candidates (notably BD+HT and BD+SN).
            if target:
                width=150 if phase=="hit" else 175
                shoulder_r=62
                er=115 if phase=="hit" else 145
            else:
                width=210 if phase=="hit" else 245
                shoulder_r=95
                er=145 if phase=="hit" else 195
            gd.line([sh,end],fill=255,width=width)
            gd.ellipse([sh[0]-shoulder_r,sh[1]-shoulder_r,sh[0]+shoulder_r,sh[1]+shoulder_r],fill=255)
            gd.ellipse([end[0]-er,end[1]-er,end[0]+er,end[1]+er],fill=255)
            if diffcent and not target:
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
    # HT:R is drawn on the screen-left side in this fixed camera. Keep the
    # screen-right hair/torso absolutely locked through the upper-body band;
    # otherwise source splice artifacts beginning at the head-lock boundary
    # can leak into BD+HT candidates.
    if any(part=="HT" and limb=="R" for part,limb in components) and key!="HT:R":
        G[300:620,700:]=False
    # Static locks. Foot-active combos need a narrow RF pedal corridor through
    # the pelvis/lower-body guard; do not unlock the whole pelvis or stool.
    G[HEAD[1]:HEAD[3],HEAD[0]:HEAD[2]]=False
    G[PELVIS[1]:PELVIS[3],PELVIS[0]:PELVIS[2]]=False
    G[STOOL[1]:STOOL[3],STOOL[0]:STOOL[2]]=False
    if has_foot:
        for part,limb in components:
            if limb not in ("LF","RF"):
                continue
            hip=LANDMARKS["hip_"+limb]; knee=LANDMARKS["knee_"+limb]; ankle=LANDMARKS["ankle_"+limb]
            end=pt_for(part) or ankle
            foot=Image.new("L",(W,H),0); fd=ImageDraw.Draw(foot)
            fd.line([hip,knee,ankle,end],fill=255,width=135,joint="curve")
            for p,r in [(knee,65),(ankle,75),(end,90)]:
                fd.ellipse([p[0]-r,p[1]-r,p[0]+r,p[1]+r],fill=255)
            F=np.asarray(foot)>0
            G |= F
        # Stool remains immutable even where the foot corridor approaches it.
        G[STOOL[1]:STOOL[3],STOOL[0]:STOOL[2]]=False
    else:
        G[620:,:]=False

    diff=np.any(S!=N,axis=2)
    alpha_mismatch=S[:,:,3]!=N[:,:,3]
    src_ink=(S[:,:,:3].min(axis=2)<225)&(S[:,:,3]>0)
    neu_ink=(N[:,:,:3].min(axis=2)<225)&(N[:,:,3]>0)
    interest=diff & (alpha_mismatch | src_ink | neu_ink)
    dil=Image.fromarray((interest.astype(np.uint8)*255),"L").filter(ImageFilter.MaxFilter(15))
    D=np.asarray(dil)>0
    M=G & D

    if key=="HT:R":
        # The final candidate is initialized from neutral below, so explicitly
        # carry the neutral resting-stick erase ROI through the final paste.
        erase_final=Image.new("L",(W,H),0); ef=ImageDraw.Draw(erase_final)
        old_tip=(405,390); erase_end=(488,458)
        ef.line([old_tip,erase_end],fill=255,width=28)
        ef.ellipse([old_tip[0]-13,old_tip[1]-13,old_tip[0]+13,old_tip[1]+13],fill=255)
        M |= (np.asarray(erase_final)>0)

    # Small deterministic stick bridges. These are line-only ROIs; never use
    # rectangular image transplants. HT:R deliberately has no synthetic bridge:
    # the prior bridge crossed the real stick in hit and floated above the arm
    # in rebound, causing the visual-integrity failure.
    stick_bridge = None
    stick_lines = None
    if key=="BD+HT:RF/R" and phase=="rebound":
        bridge=Image.new("L",(W,H),0)
        bd=ImageDraw.Draw(bridge)
        line1=((489,263),(514,307)); line2=((494,260),(519,307))
        bd.line(line1,fill=255,width=15)
        bd.line(line2,fill=255,width=15)
        stick_bridge=np.asarray(bridge)>0
        stick_lines=(line1,line2)
        M |= stick_bridge

    mask=Image.fromarray((M.astype(np.uint8)*255),"L")
    cand=neutral.copy(); cand.paste(src,(0,0),mask)
    if stick_bridge is not None and stick_lines is not None:
        cd=ImageDraw.Draw(cand)
        # Two imperfect parallel strokes preserve the rough pencil-like stick.
        cd.line(stick_lines[0],fill=(20,20,20,255),width=3)
        cd.line(stick_lines[1],fill=(55,55,55,255),width=2)
    Q=np.asarray(cand)
    ndiff=np.any(Q!=N,axis=2)
    changed=int(ndiff.sum()); ratio=changed/(W*H)
    if stick_bridge is not None:
        x1,y1,x2,y2=HEAD
        head_region=ndiff[y1:y2,x1:x2]
        head_exception=stick_bridge[y1:y2,x1:x2]
        headc=int(np.count_nonzero(head_region & ~head_exception))
    else:
        headc=guard_count(ndiff,HEAD)
    pelvisc=guard_count(ndiff,PELVIS); stoolc=guard_count(ndiff,STOOL)
    # Foot-active actions intentionally change the RF limb through part of the
    # coarse pelvis rectangle. Judge only pelvis pixels outside the permitted
    # semantic mask, rather than failing intentional RF motion.
    if has_foot:
        x1,y1,x2,y2=PELVIS
        pelvis_region=ndiff[y1:y2,x1:x2]
        pelvis_allowed=M[y1:y2,x1:x2]
        pelvisc=int(np.count_nonzero(pelvis_region & ~pelvis_allowed))
    lower=int(np.count_nonzero(ndiff[620:,:])) if not has_foot else None
    outside=int(np.count_nonzero(ndiff & ~M))

    preserves=[]
    for part,limb in components:
        p=pt_for(part)
        if not p: continue
        r=125 if phase=="hit" else 180
        region=circle_mask(p[0],p[1],r)
        # Preservation is only meaningful inside the candidate's permitted
        # semantic repair mask. Contacts outside M are deliberately neutral-
        # locked and must not make a valid bounded repair fail.
        relevant=region & interest & M
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
      "sourceSha256":formal_source_sha,
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
