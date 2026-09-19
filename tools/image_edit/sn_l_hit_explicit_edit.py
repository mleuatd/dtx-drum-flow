#!/usr/bin/env python3
import argparse, base64, hashlib, json, math, os, sys
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
    pts=c["exactJointPositions"]
    shoulder=tuple(map(float,pts["shoulder_l"]))
    elbow=tuple(map(float,pts["elbow_l"]))
    wrist=tuple(map(float,pts["wrist_l"]))
    target=tuple(map(float,c["exactContactPoints"][0]["target"]))

    # GPT Image mask: transparent pixels are the editable guidance region.
    mask=Image.new("RGBA",src.size,(255,255,255,255))
    draw=ImageDraw.Draw(mask,"RGBA")
    def line(a,b,width):
        draw.line([a,b],fill=(0,0,0,0),width=width)
    def circle(p,r):
        x,y=p
        draw.ellipse((x-r,y-r,x+r,y+r),fill=(0,0,0,0))
    line(shoulder,elbow,116)
    line(elbow,wrist,110)
    line(wrist,target,78)
    for p,r in [(shoulder,54),(elbow,62),(wrist,64),(target,44)]:
        circle(p,r)
    mask.save(mask_path)

    prompt = f"""Edit the FIRST input image directly. It is the mandatory parent and must remain the same character and same composition.
Action: SN:L hit. Change ONLY the left arm, left hand, and left drumstick inside the transparent mask.
Exact geometry in the 1448x1086 canvas:
left shoulder {shoulder}; left elbow {elbow}; left wrist {wrist}; stick tip/contact {target}.
The stick tip must touch the snare at exactly {target}. Keep the shoulder fixed at {shoulder}.
Preserve head, face, long hair, torso, right arm, both legs, stool, camera, crop, scale, clothing, and all non-masked content.
Do not add drums, cymbals, pedals, labels, panels, captions, background objects, color, shading, gradients, or a new scene.
Style: the same rough monochrome hand-drawn fine-line sketch as the parent. Do not switch to a thick digital brush. Use repeated fine uneven strokes where darker line density is needed.
The result is a character-layer edit, not a presentation sheet. Do not redraw the whole body."""
    Path(prompt_path).write_text(prompt,encoding="utf-8")
    meta={
        "source":src_path,
        "sourceSha256":EXPECTED_NEUTRAL_SHA256,
        "mask":mask_path,
        "constraints":constraints_path,
        "shoulder":shoulder,
        "elbow":elbow,
        "wrist":wrist,
        "contact":target,
        "canvas":list(EXPECTED_SIZE)
    }
    print(json.dumps(meta,ensure_ascii=False,indent=2))

def finalize(src_path, mask_path, api_path, out_path):
    src=Image.open(src_path).convert("RGBA")
    mask=Image.open(mask_path).convert("RGBA")
    api=Image.open(api_path).convert("RGBA")
    if src.size != EXPECTED_SIZE or mask.size != EXPECTED_SIZE:
        raise SystemExit("source/mask size mismatch")
    if api.size != EXPECTED_SIZE:
        raise SystemExit(f"API output size mismatch: {api.size}; refusing resize")
    sp=src.load(); mp=mask.load(); ap=api.load()
    out=src.copy(); op=out.load()
    for y in range(src.height):
        for x in range(src.width):
            if mp[x,y][3] >= 128:
                continue
            r,g,b,a=ap[x,y]
            # gpt-image-2 does not provide transparent output; deterministically remove white paper
            lum=(r+g+b)/3.0
            if lum >= 248:
                aa=0
            elif lum >= 220:
                aa=max(0,min(255,int((248-lum)/28.0*255)))
            else:
                aa=255
            op[x,y]=(r,g,b,aa)
    Path(out_path).parent.mkdir(parents=True,exist_ok=True)
    out.save(out_path)

def qa(src_path, mask_path, candidate_path, constraints_path, qa_path):
    src=Image.open(src_path).convert("RGBA")
    mask=Image.open(mask_path).convert("RGBA")
    cand=Image.open(candidate_path).convert("RGBA")
    c=load_constraints(constraints_path)
    target=tuple(map(int,c["exactContactPoints"][0]["target"]))
    if cand.size != EXPECTED_SIZE:
        raise SystemExit("candidate size mismatch")
    sp=src.load(); mp=mask.load(); cp=cand.load()
    outside_changed=0; inside_changed=0; alpha_zero=0
    for y in range(src.height):
        for x in range(src.width):
            if cp[x,y][3] == 0: alpha_zero += 1
            changed = cp[x,y] != sp[x,y]
            if not changed: continue
            if mp[x,y][3] >= 128: outside_changed += 1
            else: inside_changed += 1
    tx,ty=target
    contact_dark=0
    for y in range(max(0,ty-18),min(cand.height,ty+19)):
        for x in range(max(0,tx-18),min(cand.width,tx+19)):
            r,g,b,a=cp[x,y]
            if a>64 and (r+g+b)/3 < 180:
                contact_dark += 1
    result={
        "schemaVersion":1,
        "actionKey":"SN:L","phase":"hit",
        "sourceSha256":sha256_file(src_path),
        "candidateSha256":sha256_file(candidate_path),
        "canvas":list(cand.size),
        "outsideMaskChangedPixels":outside_changed,
        "insideMaskChangedPixels":inside_changed,
        "transparentPixels":alpha_zero,
        "contactPoint":list(target),
        "darkPixelsWithin18pxOfContact":contact_dark,
        "checks":{
            "sourceExact":sha256_file(src_path)==EXPECTED_NEUTRAL_SHA256,
            "canvasExact":cand.size==EXPECTED_SIZE,
            "outsideMaskExact":outside_changed==0,
            "localEditNonEmpty":inside_changed>100,
            "alphaPresent":alpha_zero>1000,
            "contactEvidence":contact_dark>=3
        }
    }
    result["pass"]=all(result["checks"].values())
    Path(qa_path).parent.mkdir(parents=True,exist_ok=True)
    Path(qa_path).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if not result["pass"]:
        raise SystemExit(2)

def main():
    p=argparse.ArgumentParser()
    sub=p.add_subparsers(dest="cmd",required=True)
    a=sub.add_parser("prepare")
    a.add_argument("--source",required=True); a.add_argument("--constraints",required=True)
    a.add_argument("--mask",required=True); a.add_argument("--prompt",required=True)
    b=sub.add_parser("finalize")
    b.add_argument("--source",required=True); b.add_argument("--mask",required=True)
    b.add_argument("--api-output",required=True); b.add_argument("--output",required=True)
    q=sub.add_parser("qa")
    q.add_argument("--source",required=True); q.add_argument("--mask",required=True)
    q.add_argument("--candidate",required=True); q.add_argument("--constraints",required=True); q.add_argument("--qa",required=True)
    args=p.parse_args()
    if args.cmd=="prepare": build_mask(args.source,args.constraints,args.mask,args.prompt)
    elif args.cmd=="finalize": finalize(args.source,args.mask,args.api_output,args.output)
    else: qa(args.source,args.mask,args.candidate,args.constraints,args.qa)
if __name__=="__main__":
    main()
