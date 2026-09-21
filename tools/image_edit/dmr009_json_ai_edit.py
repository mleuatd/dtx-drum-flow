#!/usr/bin/env python3
import argparse, hashlib, json, math
from pathlib import Path
from PIL import Image, ImageDraw

EXPECTED_NEUTRAL_SHA256="886e3490bb926b496d95eb1f8fb2e1ecc69859fdba35d1b13858fe8f31dd39e9"
EXPECTED_SIZE=(1448,1086)

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def draw_polyline_mask(draw,points,width):
    draw.line([tuple(map(float,p)) for p in points],fill=(0,0,0,0),width=int(width),joint="curve")
    r=max(10,int(width)//2)
    for x,y in points:
        draw.ellipse((x-r,y-r,x+r,y+r),fill=(0,0,0,0))

def prepare(source,constraints,mask_out,prompt_out):
    if sha256_file(source)!=EXPECTED_NEUTRAL_SHA256:
        raise SystemExit("neutral SHA256 mismatch")
    src=Image.open(source).convert("RGBA")
    if src.size!=EXPECTED_SIZE: raise SystemExit(f"source size mismatch {src.size}")
    c=load_json(constraints)
    mask=Image.new("RGBA",src.size,(255,255,255,255))
    draw=ImageDraw.Draw(mask,"RGBA")
    for reg in c["editableRegions"]:
        draw_polyline_mask(draw,reg["polyline"],reg["widthPx"])
    mask.save(mask_out)

    g=c["geometryHardConstraints"]
    arm=g["solvedActiveLimbTargets"]["rightArmVisualChain"]
    leg=g["solvedActiveLimbTargets"]["rightFootVisualChain"]
    prompt=f"""Edit the FIRST input image directly. It is the mandatory parent. Keep the same character, camera, body scale, stool, head, hair, torso, clothing identity, and all non-masked pixels.

Task: DMR-009 hit = BD+HH:RF/R. Change ONLY the transparent masked regions for the active right arm/hand/stick and active right leg/foot.

JSON geometry constraints are HARD anchors, not a request to draw stiff straight geometry:
- HH right-arm visual chain: shoulder {arm['shoulder']}, elbow near {arm['elbow']}, wrist near {arm['wrist']}, grip near {arm['grip']}, HH contact {arm['hhContact']}.
- BD right-foot visual chain: hip {leg['hip']}, knee near {leg['knee']}, ankle near {leg['ankle']}, pedal contact near {leg['pedalContact']}.
- Head, torso, hip center, stool, camera and scale must stay unchanged.

Within those anchors, make the pose LOOK NATURAL to a human viewer. Use normal anatomical curvature, believable joint bends, natural hand/grip connection, natural foot/ankle continuity, and plausible clothing folds. Avoid puppet-like or mechanically straight limbs.

Style is HARD: preserve the parent's rough monochrome hand-drawn fine-line sketch. Use multiple fine uneven/retraced strokes where needed. Do NOT create smooth vector-clean lines, black blob grips, doubled sticks, broken sticks, extra limbs, floating hands/feet, or redraw the whole body.

Do not add drums, cymbals, labels, panels, captions, backgrounds, color, shading or a new scene. The fixed drum is external and must not be drawn into this character layer.
"""
    Path(prompt_out).write_text(prompt,encoding="utf-8")
    print(json.dumps({"source":source,"constraints":constraints,"mask":mask_out,"prompt":prompt_out},ensure_ascii=False))

def finalize(source,mask_path,api_output,out):
    src=Image.open(source).convert("RGBA")
    mask=Image.open(mask_path).convert("RGBA")
    api=Image.open(api_output).convert("RGBA")
    if src.size!=EXPECTED_SIZE or api.size!=EXPECTED_SIZE or mask.size!=EXPECTED_SIZE:
        raise SystemExit("size mismatch; refusing resize")
    outim=src.copy()
    sp=src.load(); mp=mask.load(); ap=api.load(); op=outim.load()
    for y in range(src.height):
        for x in range(src.width):
            if mp[x,y][3]>=128: continue
            r,g,b,a=ap[x,y]
            lum=(r+g+b)/3.0
            if lum>=248: aa=0
            elif lum>=220: aa=max(0,min(255,int((248-lum)/28.0*255)))
            else: aa=255
            op[x,y]=(r,g,b,aa)
    Path(out).parent.mkdir(parents=True,exist_ok=True)
    outim.save(out,compress_level=1)

def _static_changed(src,cand,box):
    x1,y1,x2,y2=box
    n=0
    sp=src.load(); cp=cand.load()
    for y in range(y1,y2):
        for x in range(x1,x2):
            if sp[x,y]!=cp[x,y]: n+=1
    return n

def qa(source,mask_path,candidate,constraints,qa_out):
    src=Image.open(source).convert("RGBA"); mask=Image.open(mask_path).convert("RGBA"); cand=Image.open(candidate).convert("RGBA")
    c=load_json(constraints)
    sp=src.load(); mp=mask.load(); cp=cand.load()
    outside=inside=alpha_zero=0
    for y in range(src.height):
        for x in range(src.width):
            if cp[x,y][3]==0: alpha_zero+=1
            if cp[x,y]==sp[x,y]: continue
            if mp[x,y][3]>=128: outside+=1
            else: inside+=1
    hh=tuple(c["geometryHardConstraints"]["fixedContactPoints"][0]["target"])
    pedal=tuple(c["geometryHardConstraints"]["fixedContactPoints"][1]["target"])
    def dark_near(pt,r=20):
        tx,ty=map(int,pt); n=0
        for y in range(max(0,ty-r),min(cand.height,ty+r+1)):
            for x in range(max(0,tx-r),min(cand.width,tx+r+1)):
                rr,gg,bb,aa=cp[x,y]
                if aa>64 and (rr+gg+bb)/3<180:n+=1
        return n
    static={
      "head":_static_changed(src,cand,(500,0,900,330)),
      "torso":_static_changed(src,cand,(650,330,900,620)),
      "hip":_static_changed(src,cand,(650,575,820,650)),
      "stool":_static_changed(src,cand,(730,675,880,790))
    }
    result={
      "schemaVersion":1,"issueId":"DMR-009","phase":"hit","actionKey":"BD+HH:RF/R",
      "sourceSha256":sha256_file(source),"candidateSha256":sha256_file(candidate),
      "outsideMaskChangedPixels":outside,"insideMaskChangedPixels":inside,
      "staticChangedPixels":static,"hhTarget":list(hh),"bdPedalTarget":list(pedal),
      "hhDarkPixelsWithin20px":dark_near(hh),"pedalDarkPixelsWithin20px":dark_near(pedal),
      "checks":{
        "sourceExact":sha256_file(source)==EXPECTED_NEUTRAL_SHA256,
        "canvasExact":cand.size==EXPECTED_SIZE,
        "outsideMaskExact":outside==0,
        "editNonEmpty":inside>500,
        "alphaPresent":alpha_zero>1000,
        "staticHeadExact":static["head"]==0,
        "staticTorsoExact":static["torso"]==0,
        "staticHipExact":static["hip"]==0,
        "staticStoolExact":static["stool"]==0,
        "hhContactEvidence":dark_near(hh)>=3,
        "bdPedalEvidence":dark_near(pedal)>=3
      },
      "visualNaturalnessRequired":True,
      "formalOverwriteAllowed":False
    }
    result["machinePass"]=all(result["checks"].values())
    Path(qa_out).parent.mkdir(parents=True,exist_ok=True)
    Path(qa_out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if not result["machinePass"]: raise SystemExit(2)

def main():
    p=argparse.ArgumentParser(); s=p.add_subparsers(dest="cmd",required=True)
    a=s.add_parser("prepare")
    for k in ["source","constraints","mask","prompt"]: a.add_argument("--"+k,required=True)
    b=s.add_parser("finalize")
    for k in ["source","mask","api-output","output"]: b.add_argument("--"+k,required=True)
    q=s.add_parser("qa")
    for k in ["source","mask","candidate","constraints","qa"]: q.add_argument("--"+k,required=True)
    args=p.parse_args()
    if args.cmd=="prepare": prepare(args.source,args.constraints,args.mask,args.prompt)
    elif args.cmd=="finalize": finalize(args.source,args.mask,args.api_output,args.output)
    else: qa(args.source,args.mask,args.candidate,args.constraints,args.qa)

if __name__=="__main__": main()
