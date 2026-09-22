#!/usr/bin/env python3
from pathlib import Path
import json, hashlib
import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"character-assets/generation-trials/dmr009-direct-donor-v1"
NEUTRAL=ROOT/"character-assets/layers/character/base/neutral.png"
HH=ROOT/"character-assets/layers/character/hh/hit_r.png"
BD=ROOT/"character-assets/layers/character/bd/hit_rf.png"
REBOUND=ROOT/"character-assets/layers/character/combo/bd_hh_rf_r_rebound_refresh.png"
DRUM=ROOT/"character-assets/layers/drum/drum_base.png"

def rgba(p):
    with Image.open(p) as im:
        return np.asarray(im.convert("RGBA")).copy()

def save(a,p):
    p.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(a,"RGBA").save(p,compress_level=1)

def sha(p):
    h=hashlib.sha256(); h.update(p.read_bytes()); return h.hexdigest()

def alpha_comp(bottom,top):
    b=bottom.astype(float)/255.0; t=top.astype(float)/255.0
    ta=t[:,:,3:4]; ba=b[:,:,3:4]
    oa=ta+ba*(1-ta)
    rgb=np.divide(t[:,:,:3]*ta+b[:,:,:3]*ba*(1-ta),oa,
                  out=np.zeros_like(b[:,:,:3]),where=oa>0)
    out=np.clip(np.rint(np.concatenate([rgb,oa],2)*255),0,255).astype(np.uint8)
    no_top=top[:,:,3]==0
    out[no_top]=bottom[no_top]
    return out

def bbox(mask):
    y,x=np.nonzero(mask)
    return None if not len(x) else [int(x.min()),int(y.min()),int(x.max()),int(y.max())]

def main():
    neutral=rgba(NEUTRAL); hh=rgba(HH); bd=rgba(BD); drum=rgba(DRUM)
    rebound=rgba(REBOUND)

    # Primary-action-first: completed HH:R hit is the parent and is preserved.
    cand=hh.copy()

    # Add only RF bass-drum motion pixels in the lower active-foot region.
    # Ownership comes from donor-vs-neutral motion pixels, never an opaque rectangle.
    bd_diff=np.any(bd!=neutral,axis=2)
    lower=np.zeros(bd_diff.shape,bool)
    lower[760:1030,500:780]=True
    seed=bd_diff & lower
    bd_mask=binary_dilation(seed,iterations=2)
    cand[bd_mask]=bd[bd_mask]

    changed=np.any(cand!=hh,axis=2)
    outside_lower=np.count_nonzero(changed & ~binary_dilation(lower,iterations=2))
    upper_changed=np.count_nonzero(changed[:758,:])
    right_hh_zone_changed=np.count_nonzero(changed[240:620,120:850])

    comp=alpha_comp(drum,cand)
    neutral_comp=alpha_comp(drum,neutral)
    rebound_comp=alpha_comp(drum,rebound)

    OUT.mkdir(parents=True,exist_ok=True)
    cp=OUT/"DMR009_direct_HH_parent_plus_BD_RF.png"
    fp=OUT/"DMR009_direct_HH_parent_plus_BD_RF_fixed_drum.png"
    tp=OUT/"DMR009_retry20_transition_fixed_drum.png"
    crop=OUT/"DMR009_retry20_hh_arm_contact_crop.png"
    save(cand,cp); save(comp,fp)
    save(np.concatenate([neutral_comp,comp,rebound_comp,neutral_comp],axis=1),tp)
    save(comp[240:620,120:850],crop)

    result={
      "schemaVersion":2,
      "issueId":"DMR-009",
      "phase":"hit",
      "primaryAction":"Right Hand -> HH -> HIT",
      "secondaryAction":"Right Foot -> BD -> HIT",
      "method":"DIRECT_COMPLETED_HH_PARENT_PLUS_BD_RF_LOWER_ONLY",
      "primaryParent":{
        "path":"character-assets/layers/character/hh/hit_r.png",
        "sha256":sha(HH),
        "auditStatus":"PASS_FROM_EXISTING_REPOSITORY_RECORD"
      },
      "secondaryDonor":{
        "path":"character-assets/layers/character/bd/hit_rf.png",
        "sha256":sha(BD),
        "roi":[500,760,780,1030],
        "ownership":"BD_VS_NEUTRAL_MOTION_PIXELS_DILATED_2PX"
      },
      "candidate":{
        "path":str(cp.relative_to(ROOT)),
        "sha256":sha(cp),
        "changedPixelsFromHH":int(np.count_nonzero(changed)),
        "changedBBoxFromHH":bbox(changed)
      },
      "numericQa":{
        "upperBodyChangedPixelsYlt758":int(upper_changed),
        "hhArmContactZoneChangedPixels":int(right_hh_zone_changed),
        "outsideAllowedLowerCorridorChangedPixels":int(outside_lower),
        "upperBodyHhActionByteIdentical":bool(upper_changed==0),
        "hhArmContactZoneByteIdentical":bool(right_hh_zone_changed==0),
        "lowerCorridorOnly":bool(outside_lower==0),
        "result":"PASS" if upper_changed==0 and right_hh_zone_changed==0 and outside_lower==0 else "FAIL"
      },
      "fixedDrumComposite":{
        "path":str(fp.relative_to(ROOT)),
        "sha256":sha(fp)
      },
      "transitionEvidence":{
        "path":str(tp.relative_to(ROOT)),
        "sequence":["neutral","retry20_hit","existing_rebound_READ_ONLY","neutral"],
        "pairedReboundPath":str(REBOUND.relative_to(ROOT)),
        "pairedReboundSha256":sha(REBOUND),
        "pairedReboundModified":False
      },
      "visualReviewEvidence":{
        "hhArmContactCrop":str(crop.relative_to(ROOT)),
        "visualQaStatus":"PENDING_AI_VISUAL_QA"
      },
      "formalPromotion":False,
      "hardRequirement":"If the character's own right hand does not clearly strike HH at impact, FAIL regardless of all other checks."
    }
    (OUT/"DMR009_direct_donor_qa.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))

if __name__=="__main__":
    main()
