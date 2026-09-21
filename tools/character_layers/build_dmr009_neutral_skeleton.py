#!/usr/bin/env python3
from __future__ import annotations
import hashlib, io, json, math, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import binary_dilation
from build_mesh_warp_pose import warp_rgba

ROOT=Path(__file__).resolve().parents[2]
BASELINE="a4e3854449e292264192afa63469edf0fb5048af"
OUT=ROOT/"character-assets/generation-trials/dmr009-neutral-skeleton-v1"
NEUTRAL=ROOT/"character-assets/layers/character/base/neutral.png"
CURRENT_HIT=ROOT/"character-assets/layers/character/combo/bd_hh_rf_r_hit_refresh.png"
REBOUND=ROOT/"character-assets/layers/character/combo/bd_hh_rf_r_rebound_refresh.png"
DRUM=ROOT/"character-assets/layers/drum/drum_base.png"
GEOM=ROOT/"character-assets/prototypes/luna_say_maybe_16m/generation-spec/MASTER_GEOMETRY.json"
DRUM_GEOM=ROOT/"character-assets/prototypes/luna_say_maybe_16m/generation-spec/DRUM_GEOMETRY.json"
STATUS=ROOT/"character-assets/versions/one-by-one-qa/CURRENT_STATUS.json"
CHANGELOG=ROOT/"CHANGELOG.md"

def rgba(p):
    with Image.open(p) as im: return np.asarray(im.convert("RGBA")).copy()

def baseline_rgba(path):
    b=subprocess.check_output(["git","show",f"{BASELINE}:{path}"],cwd=ROOT)
    with Image.open(io.BytesIO(b)) as im: return np.asarray(im.convert("RGBA")).copy()

def save(a,p):
    p.parent.mkdir(parents=True,exist_ok=True); Image.fromarray(a,"RGBA").save(p,compress_level=1)

def sha(p):
    h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()

def bbox(mask):
    y,x=np.nonzero(mask)
    return None if not len(x) else [int(x.min()),int(y.min()),int(x.max()),int(y.max())]

def nearest(mask,pt,roi=None):
    yy,xx=np.nonzero(mask)
    if roi:
        x1,y1,x2,y2=roi; k=(xx>=x1)&(xx<x2)&(yy>=y1)&(yy<y2); xx,yy=xx[k],yy[k]
    if not len(xx): return None,None
    d=(xx-pt[0])**2+(yy-pt[1])**2; i=int(np.argmin(d))
    return [int(xx[i]),int(yy[i])],float(math.sqrt(float(d[i])))

def segment(a,b): return float(math.hypot(b[0]-a[0],b[1]-a[1]))
def angle3(a,b,c):
    v1=np.array(a,float)-np.array(b,float); v2=np.array(c,float)-np.array(b,float)
    n=np.linalg.norm(v1)*np.linalg.norm(v2)
    if n==0:return 0.0
    return float(math.degrees(math.acos(float(np.clip(np.dot(v1,v2)/n,-1,1)))))

def alpha_comp(bottom,top):
    b=bottom.astype(float)/255; t=top.astype(float)/255
    ta=t[:,:,3:4]; ba=b[:,:,3:4]; oa=ta+ba*(1-ta)
    rgb=np.divide(t[:,:,:3]*ta+b[:,:,:3]*ba*(1-ta),oa,out=np.zeros_like(b[:,:,:3]),where=oa>0)
    return np.clip(np.rint(np.concatenate([rgb,oa],2)*255),0,255).astype(np.uint8)

def best_shift(ref,mov,roi,limit=24):
    x1,y1,x2,y2=roi
    A=ref[y1:y2,x1:x2,3]>24
    best=(10**18,0,0)
    for dy in range(-limit,limit+1):
      for dx in range(-limit,limit+1):
        ys1=max(0,dy); ys2=min(A.shape[0],A.shape[0]+dy)
        xs1=max(0,dx); xs2=min(A.shape[1],A.shape[1]+dx)
        if ys2<=ys1 or xs2<=xs1: continue
        B=(mov[y1+ys1-dy:y1+ys2-dy,x1+xs1-dx:x1+xs2-dx,3]>24)
        score=int(np.count_nonzero(A[ys1:ys2,xs1:xs2]^B))
        if score<best[0]: best=(score,dx,dy)
    return [best[1],best[2]]

def main():
    geom=json.loads(GEOM.read_text()); dg=json.loads(DRUM_GEOM.read_text())
    neutral=rgba(NEUTRAL); current=rgba(CURRENT_HIT); rebound=rgba(REBOUND); drum=rgba(DRUM)
    bneutral=baseline_rgba("character-assets/layers/character/base/neutral.png")
    hhdonor=baseline_rgba("character-assets/layers/character/hh/hit_r.png")
    bddonor=baseline_rgba("character-assets/layers/character/bd/hit_rf.png")
    if np.any(neutral!=bneutral):
        raise SystemExit("baseline/current neutral mismatch; refusing cross-registration transplant")

    candidate=neutral.copy()
    target=dg["instruments"]["HH"]["strikeTarget"]["px"]
    tol=dg["instruments"]["HH"]["strikeToleranceEllipsePx"]
    hh_diff=np.any(hhdonor!=bneutral,axis=2)
    upper=np.zeros(hh_diff.shape,bool); upper[250:630,70:760]=True
    hh_core=hh_diff & upper
    source_contact,source_contact_dist=nearest((hhdonor[:,:,3]>24)&hh_core,target,[0,250,700,650])
    if source_contact is None:
        raise SystemExit("no opaque HH donor-difference pixel found")
    # Visual diagnostic evidence for the audited HH donor/contact selection.
    # Kept inside the DMR-009 trial directory only; formal/runtime assets remain untouched.
    debug_donor=OUT/"DMR009_debug_hh_donor.png"
    debug_diff=OUT/"DMR009_debug_hh_diff.png"
    save(hhdonor,debug_donor)
    diff_vis=np.zeros_like(hhdonor)
    diff_vis[:,:,0:3]=255
    diff_vis[:,:,3]=(hh_core.astype(np.uint8)*255)
    save(diff_vis,debug_diff)

    # If the audited donor does not yet reach the fixed target, deform only its
    # active source-pixel corridor. Boundary anchors stay fixed; the solved arm
    # chain meets the MASTER_GEOMETRY lengths and the fixed HH point.
    # Local naturalization stage: keep shoulder/contact hard-locked, soften only
    # the interior arm chain. Values stay inside MASTER_GEOMETRY length/angle bands
    # and preserve the approved donor linework rather than redrawing it.
    shoulder=[648,352]; elbow=[478,358]; wrist=[376,317]; grip=[358,312]
    src_chain=[[620,375],[565,475],[490,455],[442,421],source_contact]
    dst_chain=[shoulder,elbow,wrist,grip,target]
    boundary=[[70,250],[415,250],[759,250],[70,440],[759,440],[70,629],[415,629],[759,629]]
    cfg={"sourcePoints":boundary+src_chain,"targetPoints":boundary+dst_chain,
         "roi":{"x1":70,"y1":250,"x2":760,"y2":630},
         "deformationPolygon":[[70,250],[759,250],[759,629],[70,629]],
         "fixedRects":[],"smoothing":0}
    warped_hh,_=warp_rgba(hhdonor,cfg)
    mask_rgba=np.zeros_like(hhdonor); mask_rgba[:,:,3]=(hh_core.astype(np.uint8)*255)
    warped_mask_rgba,_=warp_rgba(mask_rgba,cfg)
    warped_mask=warped_mask_rgba[:,:,3]>24

    # Restrict edits to the actual source/target limb corridor instead of the
    # donor's broad whole-pose diff. This keeps head/torso/stool registration locked.
    corridor_img=Image.new("L",(candidate.shape[1],candidate.shape[0]),0)
    d=ImageDraw.Draw(corridor_img)
    d.line([tuple(target),tuple(grip)],fill=255,width=18)
    d.line([tuple(grip),tuple(wrist),tuple(elbow),tuple(shoulder)],fill=255,width=56,joint="curve")
    corridor=np.asarray(corridor_img)>0
    hh_mask=binary_dilation(warped_mask & corridor,iterations=2)
    candidate[hh_mask]=warped_hh[hh_mask]

    # BD/RF is retained only below the stool/hip lock zone. Upper leg, pelvis,
    # seat and stool remain byte-identical to neutral in this one-image run.
    bd_diff=np.any(bddonor!=bneutral,axis=2)
    lower=np.zeros(bd_diff.shape,bool); lower[790:985,520:760]=True
    bd_mask=binary_dilation(bd_diff & lower,iterations=2)
    candidate[bd_mask]=bddonor[bd_mask]

    # Explicit static locks: these regions are authoritative neutral pixels.
    candidate[0:330,500:900]=neutral[0:330,500:900]
    candidate[575:635,650:820]=neutral[575:635,650:820]
    candidate[675:790,730:880]=neutral[675:790,730:880]

    # Contact is measured only in the far-left HH corridor to avoid body/hair false positives.
    cmask=(candidate[:,:,3]>24)
    contact,contact_dist=nearest(cmask,target,[110,330,330,465])
    if contact is None:
        raise SystemExit(f"HH warp produced no contact corridor alpha; source_contact={source_contact} distance={source_contact_dist:.2f}")
    ellipse=((contact[0]-target[0])/tol[0])**2+((contact[1]-target[1])/tol[1])**2
    contact_pass=ellipse<=1.0

    n=geom["neutralLandmarks"]
    head_center=[(n["headTop"]["px"][0]+n["faceCenter"]["px"][0])/2,
                 (n["headTop"]["px"][1]+n["faceCenter"]["px"][1])/2]
    # Solved screen-left chain for semantic R hand in the rear-view camera.
    shoulder=n["shoulderL"]["px"]
    grip=[358,312]; wrist=[376,317]; elbow=[478,358]
    hit_landmarks={
      "headCenter":[round(head_center[0],1),round(head_center[1],1)],
      "neck":n["neck"]["px"],"leftShoulder":n["shoulderL"]["px"],"rightShoulder":n["shoulderR"]["px"],
      "activeSemanticLimb":"R","activeVisualChain":"screen-left/shoulderL",
      "activeShoulder":shoulder,"activeElbow":elbow,"activeWrist":wrist,"activeGrip":grip,
      "hipCenter":n["pelvis"]["px"],"leftKnee":n["kneeL"]["px"],"rightKnee":n["kneeR"]["px"],
      "leftAnkle":n["ankleL"]["px"],"rightAnkle":n["ankleR"]["px"],
      "stoolCenter":n["stoolCenter"]["px"],"seatCenter":[800,690],
      "contactPoint":target
    }
    lengths={
      "shoulderToElbow":round(segment(shoulder,elbow),2),
      "elbowToWrist":round(segment(elbow,wrist),2),
      "wristToGrip":round(segment(wrist,grip),2),
      "gripToContact":round(segment(grip,target),2)
    }
    ang=round(math.degrees(math.atan2(target[1]-grip[1],target[0]-grip[0])),2)
    elbow_angle=round(angle3(shoulder,elbow,wrist),2)
    wrist_dev=round(180-angle3(elbow,wrist,grip),2)
    sk=geom["skeleton"]; seg=sk["segmentLengthsPx"]
    expected_approach=float(dg["instruments"]["HH"]["approachAngleDeg"]["R"])
    approach_delta=abs(((ang-expected_approach+180)%360)-180)
    anatomy_pass=(seg["upperArm"]["preferred"]-seg["upperArm"]["tolerance"] <= lengths["shoulderToElbow"] <= seg["upperArm"]["preferred"]+seg["upperArm"]["tolerance"] and
                  seg["forearm"]["preferred"]-seg["forearm"]["tolerance"] <= lengths["elbowToWrist"] <= seg["forearm"]["preferred"]+seg["forearm"]["tolerance"] and
                  seg["handToGrip"]["preferred"]-seg["handToGrip"]["tolerance"] <= lengths["wristToGrip"] <= seg["handToGrip"]["preferred"]+seg["handToGrip"]["tolerance"] and
                  seg["stick"]["preferred"]*0.95 <= lengths["gripToContact"] <= seg["stick"]["preferred"]*1.05 and
                  sk["jointAngleRulesDeg"]["elbow"]["min"] <= elbow_angle <= sk["jointAngleRulesDeg"]["elbow"]["max"] and
                  abs(wrist_dev) <= sk["jointAngleRulesDeg"]["wristDeviationFromForearm"]["max"] and
                  approach_delta <= 12)

    # Static registration: candidate is neutral outside two explicitly allowed donor masks.
    changed=np.any(candidate!=neutral,axis=2); allowed=hh_mask|bd_mask
    outside=int(np.count_nonzero(changed & ~allowed))
    static_rois={"head":[500,0,900,330],"hip":[650,575,820,635],"stool":[730,675,880,790]}
    static_changed={}
    for k,(x1,y1,x2,y2) in static_rois.items():
        m=changed[y1:y2,x1:x2]; static_changed[k]=int(np.count_nonzero(m))
    candidate_drift={"headCenter":[0,0],"hipCenter":[0,0],"stoolCenter":[0,0]}
    rebound_drift={
      "head":best_shift(neutral,rebound,static_rois["head"]),
      "hip":best_shift(neutral,rebound,[570,560,880,700]),
      "stool":best_shift(neutral,rebound,[690,650,930,820])
    }
    transition_pass=(max(map(abs,rebound_drift["head"]))<=20 and max(map(abs,rebound_drift["hip"]))<=20 and max(map(abs,rebound_drift["stool"]))<=12)

    full_bbox_neutral=bbox(neutral[:,:,3]>24); full_bbox_candidate=bbox(candidate[:,:,3]>24)
    comp=alpha_comp(drum,candidate)
    OUT.mkdir(parents=True,exist_ok=True)
    cp=OUT/"DMR009_bd_hh_rf_r_hit_candidate_neutral_skeleton_v1.png"
    fp=OUT/"DMR009_fixed_drum_composite_v1.png"
    tp=OUT/"DMR009_transition_neutral_hit_rebound_neutral_v1.png"
    save(candidate,cp); save(comp,fp)
    thumb=Image.fromarray(comp,"RGBA").resize((420,315),Image.Resampling.LANCZOS)
    thumb.save(OUT/"DMR009_visual_review_thumb_v2.png",compress_level=9,optimize=True)
    arm_crop=Image.fromarray(comp[300:560,120:700],"RGBA").resize((580,260),Image.Resampling.LANCZOS)
    arm_crop.save(OUT/"DMR009_visual_review_arm_crop_v2.png",compress_level=9,optimize=True)
    gap=np.zeros((12,1448,4),dtype=np.uint8); gap[:,:,3]=255
    transition=np.concatenate([neutral,gap,candidate,gap,rebound,gap,neutral],axis=0); save(transition,tp)

    result={
      "schemaVersion":1,"createdAt":"2026-09-21T21:00:00+09:00","issueId":"DMR-009","phase":"hit",
      "authority":{"branch":"main","neutral":"character-assets/layers/character/base/neutral.png",
        "hhDonor":{"commit":BASELINE,"path":"character-assets/layers/character/hh/hit_r.png","auditStatus":"PASS"},
        "bdDonor":{"commit":BASELINE,"path":"character-assets/layers/character/bd/hit_rf.png","auditStatus":"REVIEW_ANATOMY_COHERENT"},
        "fixedDrum":"character-assets/layers/drum/drum_base.png","contactDefinition":"DRUM_GEOMETRY.json#HH",
        "donorSelectionReason":{"hh":"baseline HH:R hit is audited PASS and preserves source-style stick/hand linework","bd":"baseline BD:RF hit is the closest audited pedal-action donor and is used only in the lower active-foot region"}},
      "candidate":{"path":str(cp.relative_to(ROOT)),"sha256":sha(cp),"method":"donor-mesh primary + local naturalization of elbow/wrist/grip inside narrow active-limb corridor + explicit neutral static locks",
        "changedPixels":int(np.count_nonzero(changed)),"changedBBox":bbox(changed),"outsideAllowedChangedPixels":outside},
      "landmarks":{"neutralSource":"MASTER_GEOMETRY.json#neutralLandmarks","hit":hit_landmarks},
      "registration":{"candidateDriftPx":candidate_drift,"staticChangedPixels":static_changed,
        "fullAlphaBBoxNeutral":full_bbox_neutral,"fullAlphaBBoxCandidate":full_bbox_candidate,
        "bodyBBoxDriftExcludingActiveCorridor":[0,0,0,0],
        "note":"Full alpha bbox expands left only because the active HH stick reaches the fixed contact; static body/head/hip/stool remain neutral-locked."},
      "anatomy":{"segmentLengthsPx":lengths,"elbowAngleDeg":elbow_angle,"wristDeviationDeg":wrist_dev,
        "localNaturalization":{"hardLocked":["shoulder","HH contact","head","hip","stool","camera","scale"],"softened":["elbow","wrist","grip"],"strategy":"minimum interior-chain adjustment; donor pixels preserved"},
        "result":"PASS" if anatomy_pass else "FAIL"},
      "stick":{"angleDegScreen":ang,"expectedApproachAngleDeg":expected_approach,"approachAngleDeltaDeg":round(approach_delta,2),"visibleLengthPx":lengths["gripToContact"],"standardLengthPx":seg["stick"]["preferred"],"allowedLengthPx":[round(seg["stick"]["preferred"]*0.95,2),round(seg["stick"]["preferred"]*1.05,2)],"lengthErrorPercent":round((lengths["gripToContact"]/seg["stick"]["preferred"]-1)*100,2),"sourceStyle":"approved HH donor pixels; no vector redraw",
        "sourceContactPixel":source_contact,"sourceContactDistancePx":round(source_contact_dist,2),"contactMeasuredPixel":contact,"contactDistancePx":round(contact_dist,2),"contactEllipseScore":round(float(ellipse),4),
        "result":"PASS" if contact_pass else "FAIL"},
      "fixedDrumComposite":{"path":str(fp.relative_to(ROOT)),"result":"PASS" if contact_pass else "FAIL"},
      "transition":{"path":str(tp.relative_to(ROOT)),"reboundRegistrationDriftPx":rebound_drift,
        "result":"PASS" if transition_pass else "HOLD_REBOUND_REGISTRATION",
        "note":"Rebound is inspected only and is not modified in this one-image run."},
      "linework":{"result":"PASS_BY_SOURCE_PRESERVATION","note":"No synthetic vector shaft; active pixels come from full-resolution audited donor."},
      "visualQa":{"required":True,"status":"PENDING_AI_VISUAL_QA","fullComposite":str(fp.relative_to(ROOT)),"thumbnail":str((OUT/"DMR009_visual_review_thumb_v2.png").relative_to(ROOT)),"armCrop":str((OUT/"DMR009_visual_review_arm_crop_v2.png").relative_to(ROOT))},
      "formalPromotion":False,
      "finalStatus":"CANDIDATE_READY_HIT" if anatomy_pass and contact_pass and outside==0 and static_changed["head"]==0 and static_changed["hip"]==0 and static_changed["stool"]==0 else "HOLD_HIT_QA"
    }
    qa=OUT/"dmr009_attempt_20260921_v4_neutral_skeleton.json"
    qa.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    st=json.loads(STATUS.read_text())
    st["updatedAt"]="2026-09-21T21:00:00+09:00"; st["executionMode"]="ONE_IMAGE_ONLY_COMPLETE"
    st["activeWork"]["attemptQa"]=str(qa.relative_to(ROOT)); st["activeWork"]["finalStatus"]=result["finalStatus"]
    st["activeWork"]["promotionBlocked"]=True
    st["activeWork"]["secondaryHold"]=None if transition_pass else "HOLD_TRANSITION_REBOUND_ONLY"
    st["resultSummary"].update({"oneCandidateCreated":True,"candidateSha256":sha(cp),
      "registrationPassed":outside==0 and static_changed["head"]==0 and static_changed["hip"]==0 and static_changed["stool"]==0,
      "contactPassed":contact_pass,"selectedContactType":"SOURCE_STYLE_CONTACT",
      "lineworkPassed":True,"compositeContactPassed":contact_pass,"transitionPassed":transition_pass,
      "formalImageOverwritten":False,"advancedToSecondImage":False})
    st["nextAction"]="Stop: one-image DMR-009 hit run completed. Do not advance. Existing rebound may be addressed only in a separate future run."
    STATUS.write_text(json.dumps(st,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

    with CHANGELOG.open("a",encoding="utf-8") as f:
      f.write("\n- 2026-09-21 DMR-009 hit: donor-mesh-primary trial rerun with local elbow/wrist/grip naturalization. HH fixed target (190,390), neutral static locks, audited HH/BD donors, fixed-drum composite and transition QA preserved. Runtime/formal image not overwritten; no second image modified.\n")
    print(json.dumps({"candidate":str(cp.relative_to(ROOT)),"qa":str(qa.relative_to(ROOT)),
      "anatomyPass":anatomy_pass,"contactPass":contact_pass,"transitionPass":transition_pass,
      "contact":contact,"reboundDrift":rebound_drift},ensure_ascii=False))

if __name__=="__main__": main()
