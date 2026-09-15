from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path

import cv2
import mido
import numpy as np

DEFAULT_PARTS = ["LC","HH","SN","HT","BD","LT","FT","RC"]
GM = {"LC":49,"HH":42,"SN":38,"HT":48,"BD":36,"LT":45,"FT":41,"RC":49,"RD":51,"LP":44,"LB":35}


@dataclass
class VideoNote:
    time: float
    part: str
    frame: int
    confidence: float


def infer_geometry(frame: np.ndarray, lane_count: int = 8):
    """Infer a DTX-style chart rectangle from long grid lines."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 120)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 80, minLineLength=250, maxLineGap=12)
    if lines is None:
        raise RuntimeError("Could not infer chart geometry; pass --left/--right/--judge-y")
    horizontal, vertical = [], []
    for raw in lines[:, 0]:
        x1, y1, x2, y2 = map(int, raw)
        if abs(y2-y1) <= 3:
            horizontal.append((min(x1,x2), max(x1,x2), (y1+y2)//2))
        if abs(x2-x1) <= 3:
            vertical.append(((x1+x2)//2, min(y1,y2), max(y1,y2)))
    if not horizontal or not vertical:
        raise RuntimeError("Insufficient grid lines")
    left = int(np.percentile([x for x,_,_ in vertical], 5))
    right = int(np.percentile([x for x,_,_ in vertical], 95))
    # Judgment line is usually the brightest/lowest long horizontal line.
    candidates=[h for h in horizontal if h[1]-h[0] > (right-left)*0.7]
    if not candidates:
        raise RuntimeError("Could not find judgment line")
    judge_y=max(y for _,_,y in candidates)
    lane_w=(right-left)/lane_count
    centers=[left+(i+0.5)*lane_w for i in range(lane_count)]
    return left,right,judge_y,centers


def detect_notes(video: Path, parts: list[str], left=None, right=None, judge_y=None,
                 strip_height=20, saturation=70, value=110, min_pixels=20):
    cap=cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open {video}")
    fps=float(cap.get(cv2.CAP_PROP_FPS) or 30.0)
    ok, first=cap.read()
    if not ok:
        raise RuntimeError("Empty video")
    h,w=first.shape[:2]
    if left is None or right is None or judge_y is None:
        il,ir,iy,centers=infer_geometry(first,len(parts))
        left=il if left is None else left
        right=ir if right is None else right
        judge_y=iy if judge_y is None else judge_y
    lane_w=(right-left)/len(parts)
    centers=[left+(i+0.5)*lane_w for i in range(len(parts))]

    cap.set(cv2.CAP_PROP_POS_FRAMES,0)
    prev=[False]*len(parts)
    last=[-999999]*len(parts)
    out=[]
    frame_idx=0
    half=max(3,strip_height//2)
    while True:
        ok, frame=cap.read()
        if not ok:
            break
        hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        ya=max(0,int(judge_y-half)); yb=min(h,int(judge_y+half+1))
        for i,x in enumerate(centers):
            xa=max(0,int(x-lane_w*0.39)); xb=min(w,int(x+lane_w*0.39))
            patch=hsv[ya:yb,xa:xb]
            mask=(patch[:,:,1]>saturation)&(patch[:,:,2]>value)
            count=int(mask.sum())
            occ=count>=min_pixels
            # Rising edge means a colored note entered the judgment strip.
            if occ and not prev[i] and frame_idx-last[i] > 2:
                confidence=min(1.0,count/max(min_pixels*4,1))
                out.append(VideoNote(frame_idx/fps,parts[i],frame_idx,confidence))
                last[i]=frame_idx
            prev[i]=occ
        frame_idx += 1
    cap.release()
    return out, {"fps":fps,"left":left,"right":right,"judgeY":judge_y,"laneCenters":centers}


def write_midi(notes: list[VideoNote], out: Path, bpm: float):
    mid=mido.MidiFile(ticks_per_beat=480)
    tr=mido.MidiTrack(); mid.tracks.append(tr)
    tempo=mido.bpm2tempo(bpm)
    tr.append(mido.MetaMessage("set_tempo",tempo=tempo,time=0))
    last=0
    for n in sorted(notes,key=lambda x:x.time):
        tick=round(mido.second2tick(n.time,mid.ticks_per_beat,tempo))
        dt=max(0,tick-last)
        note=GM.get(n.part,37)
        tr.append(mido.Message("note_on",channel=9,note=note,velocity=100,time=dt))
        tr.append(mido.Message("note_off",channel=9,note=note,velocity=0,time=4))
        last=tick+4
    mid.save(out)


def write_dtx(notes: list[VideoNote], out: Path, bpm: float):
    """Write a simple high-resolution DTX skeleton using 192 subdivisions per measure."""
    channel={"HH":"11","SN":"12","BD":"13","HT":"14","LT":"15","RC":"16","FT":"17","LC":"1A","RD":"19","LP":"1B","LB":"1C"}
    sec_per_measure=240.0/bpm
    by={}
    for n in notes:
        ch=channel.get(n.part)
        if not ch: continue
        measure=max(0,int(n.time/sec_per_measure))
        pos=(n.time-measure*sec_per_measure)/sec_per_measure
        slot=min(191,max(0,round(pos*192)))
        by.setdefault((measure,ch),{})[slot]="01"
    lines=["#TITLE:Video reconstructed chart",f"#BPM:{bpm:.6f}","#WAV01:internal","#VOLUME01:100"]
    for (m,ch),slots in sorted(by.items()):
        data=["00"]*192
        for k,v in slots.items(): data[k]=v
        lines.append(f"#{m:03d}{ch}:{''.join(data)}")
    out.write_text("\n".join(lines)+"\n",encoding="shift_jis",errors="replace")


def main():
    ap=argparse.ArgumentParser(description="Reconstruct a DTX-style chart from a scrolling chart video.")
    ap.add_argument("video",type=Path)
    ap.add_argument("-o","--output",type=Path,required=True)
    ap.add_argument("--parts",default=",".join(DEFAULT_PARTS))
    ap.add_argument("--bpm",type=float,default=140.0)
    ap.add_argument("--left",type=float)
    ap.add_argument("--right",type=float)
    ap.add_argument("--judge-y",type=float)
    args=ap.parse_args()
    parts=[x.strip() for x in args.parts.split(",") if x.strip()]
    args.output.mkdir(parents=True,exist_ok=True)
    notes,geom=detect_notes(args.video,parts,args.left,args.right,args.judge_y)
    payload={"bpm":args.bpm,"sourceVideo":args.video.name,"geometry":geom,
             "notes":[asdict(n) for n in notes]}
    (args.output/"video_notes.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    write_midi(notes,args.output/"video_chart.mid",args.bpm)
    write_dtx(notes,args.output/"video_chart.dtx",args.bpm)
    print(json.dumps({"notes":len(notes),**geom},ensure_ascii=False))


if __name__=="__main__":
    main()
