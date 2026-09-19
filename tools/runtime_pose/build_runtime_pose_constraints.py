#!/usr/bin/env python3
from __future__ import annotations
import argparse,copy,json,math
from pathlib import Path
from common import load_json,write_json,dist
from solve_arm_reach import solve as solve_arm
from solve_leg_reach import solve as solve_leg

def midpoint(a,b): return [round((a[0]+b[0])/2,3),round((a[1]+b[1])/2,3)]
def main():
    p=argparse.ArgumentParser(); p.add_argument("--action-key",required=True); p.add_argument("--phase",choices=["neutral","hit","rebound"],required=True)
    p.add_argument("--contacts",required=True); p.add_argument("--anchors",required=True); p.add_argument("--retarget",required=True); p.add_argument("--appearance",required=True)
    p.add_argument("--drum-sha",required=True); p.add_argument("--output",required=True); a=p.parse_args()
    contacts=load_json(a.contacts); anchors=load_json(a.anchors); ret=load_json(a.retarget); appearance=load_json(a.appearance)
    part,limb=a.action_key.split(":",1); state=copy.deepcopy(anchors["states"][a.phase]); joints=state["joints"]
    cp=(contacts["parts"].get(part) or {}).get("approximate"); target=[cp["x"],cp["y"]] if cp else None
    neutral=anchors["states"]["neutral"]; stool=neutral["props"]["stool_center"]; hip=midpoint(neutral["joints"]["hip_l"],neutral["joints"]["hip_r"])
    out={"schemaVersion":1,"authority":"tool","actionKey":a.action_key,"phase":a.phase,"instrument":part,"limb":limb,
         "targetHeadCount":ret["targetHeadCount"],"camera":"three-quarter-back / over-shoulder; face slightly screen-left; gaze right; drum rightward",
         "stoolAnchor":stool,"hipAnchor":hip,"characterScaleLocked":True,"canvas":contacts["canvas"],"contactPoint":target,
         "fixedDrumSha256":a.drum_sha,"sourceFrameSha256":anchors["sourceFrames"][a.phase]["sha256"],"joints":joints,
         "appearanceProfileId":appearance["profileId"],"retargetProfileId":ret["profileId"],
         "forbiddenMovementZones":["camera","stool","pelvis beyond tolerance","wrong limb","wrong instrument","fixed drum pixels in character layer"],
         "tolerancesPx":{"stickTip":8,"stool":12,"hip":18,"transitionJoint":120},"confidence":state.get("confidence",0)}
    if a.phase=="neutral":
        out["stickTip"]=neutral["props"].get("stick_tip_l" if limb=="L" else "stick_tip_r")
    elif target and limb in ("L","R"):
        side=limb.lower(); shoulder=joints["shoulder_"+side]; wrist=joints["wrist_"+side]; elbow=joints["elbow_"+side]
        upper=dist(shoulder,elbow); fore=dist(elbow,wrist); existing_tip=state["props"].get("stick_tip_"+side)
        stick=dist(wrist,existing_tip) if existing_tip else 150
        bend=1 if side=="l" else -1; solved=solve_arm(shoulder,target,upper,fore,stick,0,bend)
        joints["elbow_"+side]=solved["elbow"]; joints["wrist_"+side]=solved["wrist"]; out["stickTip"]=solved["stickTip"]; out["reach"]=solved
    elif target and limb in ("LF","RF"):
        side="l" if limb=="LF" else "r"; hipj=joints["hip_"+side]; knee=joints["knee_"+side]; ankle=joints["ankle_"+side]
        solved=solve_leg(hipj,target,dist(hipj,knee),dist(knee,ankle),35,1 if side=="l" else -1)
        joints["knee_"+side]=solved["knee"]; joints["ankle_"+side]=solved["ankle"]; out["pedalTarget"]=target; out["legReach"]=solved
    # hard-lock torso registration to neutral-derived anchors; action joints remain local-motion observations/solutions.
    out["stoolAnchor"]=stool; out["hipAnchor"]=hip
    write_json(a.output,out); print(json.dumps(out,ensure_ascii=False))
if __name__=="__main__": main()
