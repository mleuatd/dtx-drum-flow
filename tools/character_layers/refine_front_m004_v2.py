#!/usr/bin/env python3
import json, hashlib
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
AUTO=ROOT/"character-assets/edit-workspaces/motion-repair-20260920/auto"
OUT=ROOT/"character-assets/edit-workspaces/motion-repair-20260920/front-m004-v2"
OUT.mkdir(parents=True,exist_ok=True)
neutral=Image.open(ROOT/"character-assets/layers/character/base/neutral.png").convert("RGBA")
drum=Image.open(ROOT/"character-assets/layers/drum/drum_base.png").convert("RGBA")
W,H=neutral.size

phases={
 "hit":{
   "parent":AUTO/"rc_sn_r_l_hit_refresh_candidate.png",
   "source":ROOT/"character-assets/layers/character/combo/rc_sn_hit_refresh.png",
 },
 "rebound":{
   "parent":AUTO/"rc_sn_r_l_rebound_refresh_candidate.png",
   "source":ROOT/"character-assets/layers/character/combo/rc_sn_rebound_refresh.png",
 }
}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def countdiff(a,b):
    return int(np.count_nonzero(np.any(np.asarray(a)!=np.asarray(b),axis=2)))
def mask_count(m): return int(np.count_nonzero(np.asarray(m)>0))

rows=[]
for phase,p in phases.items():
    parent=Image.open(p["parent"]).convert("RGBA")
    source=Image.open(p["source"]).convert("RGBA")
    assert parent.size==source.size==neutral.size==(1448,1086)

    out=parent.copy()
    allowed=Image.new("L",(W,H),0)

    # Visual QA diagnosis from v1 full-resolution artifact:
    # horizontal static-hair splice is localized to the lower central hair.
    # Restore ONLY this static hair band from approved neutral.
    hair=Image.new("L",(W,H),0); hd=ImageDraw.Draw(hair)
    hd.rounded_rectangle((675,505,895,575),radius=24,fill=255)
    # Do not touch outer arm corridors at the sides.
    out.paste(neutral,(0,0),hair)
    allowed=Image.fromarray(np.maximum(np.asarray(allowed),np.asarray(hair)).astype(np.uint8),"L")

    # v1 also retains the neutral right-hand/stick pose beside the hair while
    # the active RC arm is already raised. Replace only that observed residue
    # zone with the corresponding formal active-frame pixels, including alpha.
    residue=Image.new("L",(W,H),0); rd=ImageDraw.Draw(residue)
    rd.ellipse((928,365,1045,485),fill=255)
    rd.polygon([(965,360),(1028,355),(1055,405),(1035,470),(960,470),(930,420)],fill=255)
    out.paste(source,(0,0),residue)
    allowed=Image.fromarray(np.maximum(np.asarray(allowed),np.asarray(residue)).astype(np.uint8),"L")

    op=OUT/f"rc_sn_{phase}_candidate_v2.png"
    out.save(op)
    comp=Image.alpha_composite(drum,out)
    comp.save(OUT/f"rc_sn_{phase}_candidate_v2_fixed_drum.png")

    A=np.asarray(parent); Q=np.asarray(out); M=np.asarray(allowed)>0
    diff=np.any(A!=Q,axis=2)
    outside=int(np.count_nonzero(diff & ~M))
    # Mandatory static lower-body/stool lock against the v1 parent.
    lower=int(np.count_nonzero(np.any(A[620:,:,:]!=Q[620:,:,:],axis=2)))
    # Contact neighborhoods must stay exactly as in the already machine-pass v1.
    yy,xx=np.ogrid[:H,:W]
    contact_rc=(xx-1215)**2+(yy-145)**2<=95**2
    contact_sn=(xx-420)**2+(yy-535)**2<=95**2
    contact_changed=int(np.count_nonzero(diff & (contact_rc|contact_sn)))
    checks={
      "changedVisible":int(diff.sum())>=100,
      "outsideRepairMaskZero":outside==0,
      "lowerBodyAndStoolExactToV1":lower==0,
      "instrumentContactNeighborhoodsExactToV1":contact_changed==0
    }
    rec={
      "phase":phase,
      "parent":str(p["parent"].relative_to(ROOT)),
      "parentSha256":sha(p["parent"]),
      "formalSource":str(p["source"].relative_to(ROOT)),
      "candidate":str(op.relative_to(ROOT)),
      "candidateSha256":sha(op),
      "changedPixelsVsV1":int(diff.sum()),
      "repairMaskPixels":mask_count(allowed),
      "outsideRepairMaskChangedPixels":outside,
      "lowerChangedPixels":lower,
      "contactNeighborhoodChangedPixels":contact_changed,
      "checks":checks,
      "machinePass":all(checks.values())
    }
    (OUT/f"rc_sn_{phase}_candidate_v2_qa.json").write_text(json.dumps(rec,indent=2)+"\n")
    rows.append(rec)

# Compact transition sheet, full-size pair remains separate.
frames=[neutral,Image.open(OUT/"rc_sn_hit_candidate_v2.png").convert("RGBA"),Image.open(OUT/"rc_sn_rebound_candidate_v2.png").convert("RGBA"),neutral]
thumbs=[]
for f in frames:
    c=Image.alpha_composite(drum,f).convert("RGB"); c.thumbnail((480,360)); thumbs.append(c)
strip=Image.new("RGB",(1920,360),"white")
for i,t in enumerate(thumbs): strip.paste(t,(i*480,0))
strip.save(OUT/"rc_sn_v2_transition.jpg",quality=95)
summary={"schemaVersion":2,"issueId":"MOTION-004","actionKey":"RC+SN:R/L","parent":"v1 machine-pass candidate","method":"restore neutral static hair band + replace observed neutral right-hand residue from formal active frame","phases":rows,"pairMachinePass":all(x["machinePass"] for x in rows)}
(OUT/"M004_V2_SUMMARY.json").write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps({"pairMachinePass":summary["pairMachinePass"],"phases":[(x["phase"],x["candidateSha256"]) for x in rows]}))
if not summary["pairMachinePass"]: raise SystemExit(2)
