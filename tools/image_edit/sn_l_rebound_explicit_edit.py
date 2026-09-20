#!/usr/bin/env python3
import argparse, hashlib, json, math
from pathlib import Path
from PIL import Image, ImageDraw

EXPECTED_NEUTRAL_SHA256 = "886e3490bb926b496d95eb1f8fb2e1ecc69859fdba35d1b13858fe8f31dd39e9"
EXPECTED_SIZE = (1448, 1086)

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def load_constraints(path):
    with open(path,"r",encoding="utf-8") as f:
        return json.load(f)

def build_mask(src_path, constraints_path, mask_path, prompt_path):
    if sha256_file(src_path) != EXPECTED_NEUTRAL_SHA256:
        raise SystemExit("neutral SHA256 mismatch")
    src=Image.open(src_path).convert("RGBA")
    if src.size != EXPECTED_SIZE:
        raise SystemExit(f"neutral size mismatch: {src.size}")
    c=load_constraints(constraints_path)
    j=c["joints"]
    shoulder=tuple(map(float,j["shoulder_l"]))
    elbow=tuple(map(float,j["elbow_l"]))
    wrist=tuple(map(float,j["wrist_l"]))
    tip=tuple(map(float,c["stickTip"]))
    contact=tuple(map(float,c["contactPoint"]))
    min_sep=float(c.get("tolerancesPx",{}).get("reboundSeparation",16))

    mask=Image.new("RGBA",src.size,(255,255,255,255))
    draw=ImageDraw.Draw(mask,"RGBA")
    def line(a,b,width): draw.line([a,b],fill=(0,0,0,0),width=width)
    def circle(p,r):
        x,y=p
        draw.ellipse((x-r,y-r,x+r,y+r),fill=(0,0,0,0))

    # One continuous editable corridor: shoulder -> elbow -> wrist -> rebound stick tip.
    line(shoulder,elbow,120)
    line(elbow,wrist,112)
    line(wrist,tip,76)
    for p,r in [(shoulder,56),(elbow,64),(wrist,66),(tip,42)]:
        circle(p,r)
    mask.save(mask_path)

    prompt=f"""Edit the FIRST input image directly. It is the mandatory parent and must remain the same character and same composition.
Action: SN:L rebound. Change ONLY the left arm, left hand, and left drumstick inside the transparent mask.
Exact target geometry in the 1448x1086 canvas:
left shoulder {shoulder}; left elbow {elbow}; left wrist {wrist}; rebound stick tip {tip}.
The snare contact point is {contact}. This is REBOUND, not hit: the stick tip must remain visibly away from the snare contact, at least {min_sep:.0f} px, while the hand grips one continuous stick.
Create exactly one coherent left upper arm, one forearm, one hand, and one continuous drumstick. No duplicate hand, no detached hand/blob, no broken stick, no floating fragment, no alpha gap, no rectangular patch.
Keep the shoulder attached naturally to the existing jacket/sleeve at {shoulder}. Preserve the jacket outline around the shoulder without cutting a hole or creating a pasted rectangle.
Preserve head, face, long hair, torso, right arm, pelvis, both legs, boots, stool, camera, crop, scale, clothing outside the mask, and all non-masked pixels exactly.
Do not add drums, cymbals, pedals, labels, panels, captions, background objects, color, shading, gradients, or a new scene.
Style: exactly the same rough monochrome hand-drawn fine-line sketch as the parent. Use repeated fine uneven strokes where darker line density is needed; do not switch to a thick digital brush.
The result is a transparent character-layer edit, not a presentation sheet. Do not redraw the whole body."""
    Path(prompt_path).write_text(prompt,encoding="utf-8")
    print(json.dumps({
        "source":src_path,"sourceSha256":EXPECTED_NEUTRAL_SHA256,
        "constraints":constraints_path,"mask":mask_path,
        "shoulder":shoulder,"elbow":elbow,"wrist":wrist,
        "stickTip":tip,"contact":contact,"minimumSeparationPx":min_sep,
        "canvas":list(EXPECTED_SIZE)
    },ensure_ascii=False,indent=2))

def finalize(src_path, mask_path, api_path, out_path):
    src=Image.open(src_path).convert("RGBA")
    mask=Image.open(mask_path).convert("RGBA")
    api=Image.open(api_path).convert("RGBA")
    if src.size != EXPECTED_SIZE or mask.size != EXPECTED_SIZE or api.size != EXPECTED_SIZE:
        raise SystemExit(f"size mismatch: src={src.size} mask={mask.size} api={api.size}")
    sp=src.load(); mp=mask.load(); ap=api.load()
    out=src.copy(); op=out.load()
    for y in range(src.height):
        for x in range(src.width):
            if mp[x,y][3] >= 128:
                continue
            r,g,b,a=ap[x,y]
            lum=(r+g+b)/3.0
            if lum >= 248: aa=0
            elif lum >= 220: aa=max(0,min(255,int((248-lum)/28.0*255)))
            else: aa=255
            op[x,y]=(r,g,b,aa)
    Path(out_path).parent.mkdir(parents=True,exist_ok=True)
    out.save(out_path)

def qa(src_path, mask_path, candidate_path, constraints_path, qa_path):
    src=Image.open(src_path).convert("RGBA")
    mask=Image.open(mask_path).convert("RGBA")
    cand=Image.open(candidate_path).convert("RGBA")
    c=load_constraints(constraints_path)
    tip=tuple(map(int,c["stickTip"]))
    contact=tuple(map(int,c["contactPoint"]))
    min_sep=float(c.get("tolerancesPx",{}).get("reboundSeparation",16))
    if cand.size != EXPECTED_SIZE:
        raise SystemExit("candidate size mismatch")
    sp=src.load(); mp=mask.load(); cp=cand.load()
    outside_changed=inside_changed=alpha_zero=0
    for y in range(src.height):
        for x in range(src.width):
            if cp[x,y][3] == 0: alpha_zero += 1
            changed=cp[x,y] != sp[x,y]
            if not changed: continue
            if mp[x,y][3] >= 128: outside_changed += 1
            else: inside_changed += 1

    def dark_pixels(center,radius=18):
        cx,cy=center; n=0
        for y in range(max(0,cy-radius),min(cand.height,cy+radius+1)):
            for x in range(max(0,cx-radius),min(cand.width,cx+radius+1)):
                r,g,b,a=cp[x,y]
                if a>64 and (r+g+b)/3<180: n+=1
        return n

    tip_dark=dark_pixels(tip,18)
    contact_dark=dark_pixels(contact,12)
    sep=math.hypot(tip[0]-contact[0],tip[1]-contact[1])
    result={
      "schemaVersion":1,"issueId":"MOTION-001","actionKey":"SN:L","phase":"rebound",
      "sourceSha256":sha256_file(src_path),"candidateSha256":sha256_file(candidate_path),
      "canvas":list(cand.size),"outsideMaskChangedPixels":outside_changed,
      "insideMaskChangedPixels":inside_changed,"transparentPixels":alpha_zero,
      "stickTip":list(tip),"contactPoint":list(contact),
      "reboundSeparationPx":round(sep,3),"minimumSeparationPx":min_sep,
      "darkPixelsWithin18pxOfStickTip":tip_dark,
      "darkPixelsWithin12pxOfContact":contact_dark,
      "checks":{
        "sourceExact":sha256_file(src_path)==EXPECTED_NEUTRAL_SHA256,
        "canvasExact":cand.size==EXPECTED_SIZE,
        "outsideMaskExact":outside_changed==0,
        "localEditNonEmpty":inside_changed>100,
        "alphaPresent":alpha_zero>1000,
        "stickTipEvidence":tip_dark>=3,
        "reboundSeparatedFromContact":sep>=min_sep
      }
    }
    result["pass"]=all(result["checks"].values())
    Path(qa_path).parent.mkdir(parents=True,exist_ok=True)
    Path(qa_path).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if not result["pass"]: raise SystemExit(2)

def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest="cmd",required=True)
    a=sub.add_parser("prepare"); a.add_argument("--source",required=True); a.add_argument("--constraints",required=True); a.add_argument("--mask",required=True); a.add_argument("--prompt",required=True)
    b=sub.add_parser("finalize"); b.add_argument("--source",required=True); b.add_argument("--mask",required=True); b.add_argument("--api-output",required=True); b.add_argument("--output",required=True)
    q=sub.add_parser("qa"); q.add_argument("--source",required=True); q.add_argument("--mask",required=True); q.add_argument("--candidate",required=True); q.add_argument("--constraints",required=True); q.add_argument("--qa",required=True)
    args=p.parse_args()
    if args.cmd=="prepare": build_mask(args.source,args.constraints,args.mask,args.prompt)
    elif args.cmd=="finalize": finalize(args.source,args.mask,args.api_output,args.output)
    else: qa(args.source,args.mask,args.candidate,args.constraints,args.qa)
if __name__=="__main__": main()
