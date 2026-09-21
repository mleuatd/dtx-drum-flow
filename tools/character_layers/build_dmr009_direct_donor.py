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
    # Primary-action-first: the completed HH:R hit is the parent and is left untouched.
    cand=hh.copy()

    # Add only the lower RF bass-drum action. Never touch primary right-arm HH action.
    bd_diff=np.any(bd!=neutral,axis=2)
    lower=np.zeros(bd_diff.shape,bool)
    lower[760:1030,500:780]=True
    bd_mask=binary_dilation(bd_diff & lower,iterations=2)
    cand[bd_mask]=bd[bd_mask]

    comp=alpha_comp(drum,cand)

    OUT.mkdir(parents=True,exist_ok=True)
    cp=OUT/"DMR009_direct_HH_parent_plus_BD_RF.png"
    fp=OUT/"DMR009_direct_HH_parent_plus_BD_RF_fixed_drum.png"
    save(cand,cp); save(comp,fp)

    result={
      "schemaVersion":1,
      "issueId":"DMR-009",
      "phase":"hit",
      "primaryAction":"Right Hand -> HH -> HIT",
      "secondaryAction":"Right Foot -> BD -> HIT",
      "method":"DIRECT_COMPLETED_HH_PARENT_PLUS_BD_RF_LOWER_ONLY",
      "primaryParent":{
        "path":"character-assets/layers/character/hh/hit_r.png",
        "sha256":sha(HH),
        "pixelsModifiedBySecondaryOverlay":int(np.count_nonzero(bd_mask))
      },
      "secondaryDonor":{
        "path":"character-assets/layers/character/bd/hit_rf.png",
        "sha256":sha(BD),
        "roi":[500,760,780,1030]
      },
      "candidate":{"path":str(cp.relative_to(ROOT)),"sha256":sha(cp),"changedBBoxFromHH":bbox(np.any(cand!=hh,axis=2))},
      "fixedDrumComposite":{"path":str(fp.relative_to(ROOT)),"sha256":sha(fp)},
      "formalPromotion":False,
      "visualQaStatus":"PENDING_AI_VISUAL_QA",
      "hardRequirement":"If the character's own right hand does not clearly strike HH at impact, FAIL regardless of all other checks."
    }
    (OUT/"DMR009_direct_donor_qa.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))

if __name__=="__main__":
    main()
